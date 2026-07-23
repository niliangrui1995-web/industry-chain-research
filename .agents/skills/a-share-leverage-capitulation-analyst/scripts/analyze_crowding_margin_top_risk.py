#!/usr/bin/env python3
"""Research A-share crowding, stock-level margin flows, and future drawdown risk.

The study is deliberately vendor-bounded:

* stock-level price and financing observations come from the frozen DFCF detail DB;
* market-total financing comes from the physically separate DFCF aggregate table;
* the Shenzhen Composite trend comes from the user's read-only local TDX daily file.

All features on date T use only observations available through T.  Because complete
margin data are available only after the close, model outputs are after-close risk
estimates whose first executable session is T+1.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import os
import re
import sqlite3
import struct
import warnings
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

STUDY_NAME = "crowding_margin_top_risk_2016_present"
INDEX_CODE = "399106"
MODEL_START_DATE = pd.Timestamp("2019-01-01")
MOMENTUM_OBSERVATIONS = 120
MIN_MOMENTUM_OBSERVATIONS = 120
MOMENTUM_DENSITY_SPAN = 150
IPO_MOMENTUM_EXCLUSION_OBSERVATIONS = 20
RAW_RETURN_BREAK_THRESHOLD_PCT = 22.0
CANDIDATE_QUANTILE = 0.90
PERSISTENCE_DAYS = 20
PERSISTENCE_MIN_HITS = 12
MIN_CROWD_SIZE = 30
MIN_CROWD_RETURN_COVERAGE = 0.80
MIN_MARGIN_FLOW_COVERAGE = 0.80
FLOW_DENOMINATOR_FLOOR_YUAN = 1_000_000
CAUSAL_RANK_WINDOW = 756
CAUSAL_RANK_MIN_OBSERVATIONS = 252
MODEL_EMBARGO_DAYS = 40
PRIMARY_DRAWDOWN_HORIZON = 20
PRIMARY_DRAWDOWN_THRESHOLD = -8.0
EVENT_DECLUSTER_DAYS = 40


@dataclass(frozen=True)
class StudyConfig:
    db_path: Path
    aggregate_margin_csv: Path
    aggregate_audit_json: Path
    index_day_path: Path
    ht_root: Path
    market_snapshot_manifest: Path
    gbbq_path: Path
    gbbq_reader_path: Path
    individual_audit_json: Path
    output_dir: Path
    start_date: str = "2016-01-01"
    end_date: str | None = None
    candidate_quantile: float = CANDIDATE_QUANTILE
    persistence_min_hits: int = PERSISTENCE_MIN_HITS
    min_crowd_size: int = MIN_CROWD_SIZE


def sha256_file(path: Path, chunk_size: int = 4 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def jsonable(value: object) -> object:
    if value is pd.NaT or value is pd.NA:
        return None
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        if pd.isna(value):
            return None
        return pd.Timestamp(value).strftime("%Y-%m-%d")
    if isinstance(value, (np.integer, np.floating)):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def validate_output_dir(path: Path) -> Path:
    resolved = path.resolve()
    if any(part.lower() == "verified_2016_present" for part in resolved.parts):
        raise ValueError(
            "Output under verified_2016_present is forbidden because the "
            "exchange-audited artifact tree is frozen"
        )
    return resolved


def atomic_write_text(path: Path, text_value: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(text_value, encoding=encoding)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        frame.to_csv(temporary, index=False, encoding="utf-8-sig")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_tdx_day(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"TDX index file not found: {path}")
    raw = path.read_bytes()
    if not raw or len(raw) % 32:
        raise ValueError(f"Invalid TDX day file size: {path}")
    rows = []
    for offset in range(0, len(raw), 32):
        date_i, open_i, high_i, low_i, close_i, amount, volume, _ = struct.unpack_from(
            "<IIIIIfII", raw, offset
        )
        rows.append(
            (
                pd.to_datetime(str(date_i), format="%Y%m%d"),
                open_i / 100.0,
                high_i / 100.0,
                low_i / 100.0,
                close_i / 100.0,
                float(amount),
                int(volume),
            )
        )
    frame = pd.DataFrame(
        rows,
        columns=["date", "index_open", "index_high", "index_low", "index_close", "index_amount", "index_volume"],
    )
    frame = frame.drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)
    frame["index_return_pct"] = frame["index_close"].pct_change() * 100.0
    return frame


SH_SZ_STOCK_PATTERN = re.compile(
    r"(?:sh(?:600|601|603|605|688|689)|sz(?:000|001|002|003|300|301|302))\d{3}\.day$"
)


def discover_sh_sz_day_files(ht_root: Path) -> list[Path]:
    files: list[Path] = []
    for market in ("sh", "sz"):
        folder = ht_root / "vipdoc" / market / "lday"
        if folder.exists():
            files.extend(
                path
                for path in folder.glob("*.day")
                if SH_SZ_STOCK_PATTERN.fullmatch(path.name.lower())
            )
    if not files:
        raise FileNotFoundError(f"No SH/SZ A-share day files under {ht_root}")
    return sorted(files)


def canonical_tdx_stock_code(path: Path) -> str:
    stem = path.stem.lower()
    if not re.fullmatch(r"(?:sh|sz)\d{6}", stem):
        raise ValueError(f"Not a canonical SH/SZ TDX stock file: {path}")
    return f"{stem[2:]}.{stem[:2].upper()}"


def load_causal_corporate_actions(
    gbbq_path: Path,
    gbbq_reader_path: Path,
    end_date: pd.Timestamp,
) -> tuple[dict[tuple[str, int], tuple[float, float, float]], dict[str, object]]:
    """Read TDX category-1 rights events without applying future events backward.

    Values are interpreted using the TDX convention: cash dividend, bonus shares,
    and rights shares are stated per 10 shares; the rights price is per share.
    Multiple same-day records are combined into cash, rights consideration, and
    share-count additions so only information dated on or before each return is used.
    """

    if not gbbq_path.exists():
        raise FileNotFoundError(f"TDX gbbq file not found: {gbbq_path}")
    if not gbbq_reader_path.exists():
        raise FileNotFoundError(f"pytdx gbbq reader not found: {gbbq_reader_path}")
    spec = importlib.util.spec_from_file_location(
        "_local_pytdx_gbbq_reader", gbbq_reader_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load gbbq reader: {gbbq_reader_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw = module.GbbqReader().get_df(str(gbbq_path))
    required = {
        "market",
        "code",
        "datetime",
        "category",
        "hongli_panqianliutong",
        "peigujia_qianzongguben",
        "songgu_qianzongguben",
        "peigu_houzongguben",
    }
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"TDX gbbq reader missing fields: {sorted(missing)}")

    end_date_i = int(end_date.strftime("%Y%m%d"))
    selected = raw[
        raw["category"].eq(1)
        & raw["market"].isin([0, 1])
        & raw["datetime"].le(end_date_i)
    ].copy()
    actions: dict[tuple[str, int], tuple[float, float, float]] = {}
    future_events_excluded = int(
        np.count_nonzero(
            raw["category"].eq(1)
            & raw["market"].isin([0, 1])
            & raw["datetime"].gt(end_date_i)
        )
    )
    for row in selected.itertuples(index=False):
        suffix = "SZ" if int(row.market) == 0 else "SH"
        key = (f"{str(row.code).zfill(6)}.{suffix}", int(row.datetime))
        cash = float(row.hongli_panqianliutong) / 10.0
        rights = float(row.peigu_houzongguben) / 10.0
        share_addition = (
            float(row.songgu_qianzongguben) / 10.0 + rights
        )
        rights_consideration = (
            float(row.peigujia_qianzongguben) * rights
        )
        prior = actions.get(key, (0.0, 0.0, 0.0))
        actions[key] = (
            prior[0] + cash,
            prior[1] + rights_consideration,
            prior[2] + share_addition,
        )

    audit = {
        "source": str(gbbq_path),
        "reader_source": str(gbbq_reader_path),
        "sample_status": "tdx_vendor_corporate_actions_causal_approximation",
        "category_1_sh_sz_rows_through_end": len(selected),
        "unique_action_security_dates": len(actions),
        "future_category_1_rows_excluded": future_events_excluded,
        "gbbq_sha256": sha256_file(gbbq_path),
        "reader_sha256": sha256_file(gbbq_reader_path),
        "formula": (
            "reference=(previous_close-cash_per_share+rights_consideration_per_share)"
            "/(1+bonus_and_rights_shares_per_share); return=close/reference-1"
        ),
        "boundary": (
            "TDX field order is reader-source verified, while per-10-share units "
            "follow TDX convention and local implementation. This is a causal "
            "approximation; differential distributions or special events may differ."
        ),
    }
    return actions, audit


def load_tdx_market_rows(
    ht_root: Path,
    warmup_start: pd.Timestamp,
    end_date: pd.Timestamp,
    corporate_actions: dict[tuple[str, int], tuple[float, float, float]],
) -> tuple[
    dict[int, list[tuple[str, float, float, bool, float, float]]],
    dict[str, object],
    dict[str, tuple[int, str]],
]:
    """Load causal daily returns for the full local SH/SZ history.

    TDX files are unadjusted. Category-1 events dated T adjust only T's reference
    price, never prior history. The first 20 observations are excluded from momentum,
    and unexplained absolute returns above 22% clear the causal momentum history.
    """

    files = discover_sh_sz_day_files(ht_root)
    rows_by_date: dict[
        int, list[tuple[str, float, float, bool, float, float]]
    ] = defaultdict(list)
    manifest_digest = hashlib.sha256()
    relevant_file_hashes: dict[str, tuple[int, str]] = {}
    total_records = 0
    retained_records = 0
    abnormal_breaks = 0
    corporate_action_returns = 0
    invalid_corporate_actions = 0
    first_record_exclusions = 0
    invalid_files: list[str] = []
    warmup_date_i = int(warmup_start.strftime("%Y%m%d"))
    end_date_i = int(end_date.strftime("%Y%m%d"))

    for path in files:
        raw = path.read_bytes()
        if not raw or len(raw) % 32:
            invalid_files.append(str(path))
            continue

        code = canonical_tdx_stock_code(path)
        previous_close: float | None = None
        observation_number = 0
        relevant_prefix_bytes = 0
        for offset in range(0, len(raw), 32):
            date_i, _, _, _, close_i, amount, _, _ = struct.unpack_from(
                "<IIIIIfII", raw, offset
            )
            close = close_i / 100.0
            total_records += 1
            observation_number += 1
            if date_i <= end_date_i:
                relevant_prefix_bytes = offset + 32
            return_pct = math.nan
            momentum_return_pct = math.nan
            reset_momentum = False
            if previous_close is None:
                first_record_exclusions += 1
            elif previous_close > 0.0 and close > 0.0:
                reference_close = previous_close
                action = corporate_actions.get((code, date_i))
                if action is not None:
                    cash, rights_consideration, share_addition = action
                    denominator = 1.0 + share_addition
                    if denominator > 0.0:
                        reference_close = (
                            previous_close - cash + rights_consideration
                        ) / denominator
                    if not np.isfinite(reference_close) or reference_close <= 0.0:
                        reference_close = math.nan
                        invalid_corporate_actions += 1
                    else:
                        corporate_action_returns += 1
                raw_return = (
                    (close / reference_close - 1.0) * 100.0
                    if np.isfinite(reference_close) and reference_close > 0.0
                    else math.nan
                )
                if abs(raw_return) <= RAW_RETURN_BREAK_THRESHOLD_PCT:
                    return_pct = float(raw_return)
                    if observation_number > IPO_MOMENTUM_EXCLUSION_OBSERVATIONS:
                        momentum_return_pct = float(raw_return)
                else:
                    abnormal_breaks += 1
                    reset_momentum = True
            else:
                reset_momentum = True
            if close > 0.0:
                previous_close = close
            if date_i < warmup_date_i or date_i > end_date_i:
                continue
            rows_by_date[date_i].append(
                (
                    code,
                    return_pct,
                    momentum_return_pct,
                    reset_momentum,
                    close,
                    float(amount),
                )
            )
            retained_records += 1
        relevant_digest = hashlib.sha256(
            raw[:relevant_prefix_bytes]
        ).hexdigest()
        relevant_file_hashes[str(path)] = (
            relevant_prefix_bytes,
            relevant_digest,
        )
        manifest_digest.update(
            str(path.relative_to(ht_root)).encode("utf-8")
        )
        manifest_digest.update(bytes.fromhex(relevant_digest))

    audit = {
        "source": "D:/HT TDX raw SH/SZ .day files",
        "source_status": "market_data_vendor",
        "stock_files": len(files),
        "invalid_files": invalid_files,
        "total_file_records": total_records,
        "retained_records": retained_records,
        "date_count": len(rows_by_date),
        "date_start": (
            pd.to_datetime(str(min(rows_by_date)), format="%Y%m%d")
            if rows_by_date
            else None
        ),
        "date_end": (
            pd.to_datetime(str(max(rows_by_date)), format="%Y%m%d")
            if rows_by_date
            else None
        ),
        "first_record_exclusions": first_record_exclusions,
        "causal_corporate_action_returns": corporate_action_returns,
        "invalid_corporate_action_reference_prices": invalid_corporate_actions,
        "raw_return_breaks_over_22pct": abnormal_breaks,
        "corporate_action_treatment": (
            "Category-1 events adjust only their own dated reference price. Raw or "
            "adjusted return abs>22% is excluded and resets momentum; first 20 local "
            "observations never enter momentum. Differential distributions and "
            "unrecorded smaller events remain a vendor-data limitation."
        ),
        "survivorship_boundary": (
            "Historical files ending before the current date are included when "
            "present, but the local folder cannot prove complete retention of every "
            "delisted security."
        ),
        "relevant_prefix_manifest_sha256": manifest_digest.hexdigest(),
        "relevant_prefix_definition": (
            f"All complete 32-byte records with trade date <= {end_date:%Y-%m-%d}; "
            "later live-session records are outside the research snapshot."
        ),
    }
    return dict(rows_by_date), audit, relevant_file_hashes


def verify_tdx_relevant_prefixes(
    relevant_file_hashes: dict[str, tuple[int, str]],
    end_date: pd.Timestamp,
) -> None:
    end_date_i = int(end_date.strftime("%Y%m%d"))
    changed = []
    for path_text, (expected_bytes, expected_hash) in relevant_file_hashes.items():
        path = Path(path_text)
        if not path.exists():
            changed.append(path_text)
            continue
        raw = path.read_bytes()
        if not raw or len(raw) % 32:
            changed.append(path_text)
            continue
        relevant_bytes = 0
        for offset in range(0, len(raw), 32):
            date_i = struct.unpack_from("<I", raw, offset)[0]
            if date_i <= end_date_i:
                relevant_bytes = offset + 32
            else:
                break
        actual_hash = hashlib.sha256(raw[:relevant_bytes]).hexdigest()
        if relevant_bytes != expected_bytes or actual_hash != expected_hash:
            changed.append(path_text)
    if changed:
        raise RuntimeError(
            "Local TDX stock history through the research end date changed "
            f"during the study: {changed[:10]}"
        )


def load_aggregate_margin(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Aggregate margin CSV not found: {path}")
    frame = pd.read_csv(path, encoding="utf-8")
    required = {"date", "total_margin_y", "total_change_pct", "sample_status"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Aggregate margin CSV missing fields: {sorted(missing)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    if frame["date"].duplicated().any():
        raise ValueError("Aggregate margin CSV contains duplicate dates")
    for column in ("total_margin_y", "total_change_pct"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame["total_margin_y"].isna().any() or frame["total_margin_y"].le(0.0).any():
        raise ValueError("Aggregate margin CSV has invalid total balances")
    if set(frame["sample_status"].dropna().unique()) != {
        "dfcf_vendor_only_unverified_by_exchange"
    }:
        raise ValueError("Aggregate margin CSV has unexpected sample_status")
    frame = frame.sort_values("date").reset_index(drop=True)
    return frame


def validate_input_audits(
    config: StudyConfig,
    aggregate: pd.DataFrame,
    index_frame: pd.DataFrame,
) -> dict[str, object]:
    with config.individual_audit_json.open("r", encoding="utf-8") as handle:
        individual = json.load(handle)
    with config.aggregate_audit_json.open("r", encoding="utf-8") as handle:
        aggregate_audit = json.load(handle)

    if (
        individual.get("sample_status")
        != "dfcf_vendor_individual_detail_unverified_by_exchange"
    ):
        raise RuntimeError("Unexpected individual-margin sample_status")
    if individual.get("dfcf_only") is not True or int(
        individual.get("exchange_requests", -1)
    ) != 0:
        raise RuntimeError("Individual-margin audit is not DFCF-only")
    if individual.get("vendor_pagination_complete") is not True:
        raise RuntimeError("Individual-margin vendor pagination is incomplete")
    if individual.get("failed_dates") or individual.get("row_mismatch_dates"):
        raise RuntimeError("Individual-margin audit contains failed or mismatched dates")
    if int(individual.get("null_financing_balance_rows", -1)) != 0:
        raise RuntimeError("Individual-margin audit contains null balances")
    if int(individual.get("negative_financing_balance_rows", -1)) != 0:
        raise RuntimeError("Individual-margin audit contains negative balances")
    if not set(individual.get("missing_calendar_dates", [])).issubset(
        set(individual.get("vendor_no_data_dates", []))
    ):
        raise RuntimeError("Unexplained individual-margin calendar gaps")
    if (
        aggregate_audit.get("sample_status")
        != "dfcf_vendor_only_unverified_by_exchange"
    ):
        raise RuntimeError("Unexpected aggregate-margin sample_status")
    if aggregate_audit.get("dfcf_only") is not True or int(
        aggregate_audit.get("exchange_requests", -1)
    ) != 0:
        raise RuntimeError("Aggregate-margin audit is not DFCF-only")
    if aggregate_audit.get("sh_latest") != aggregate_audit.get("sz_latest"):
        raise RuntimeError("Aggregate SH/SZ latest dates do not match")

    database_hash = sha256_file(config.db_path)
    aggregate_hash = sha256_file(config.aggregate_margin_csv)
    if database_hash != individual.get("database_sha256"):
        raise RuntimeError("Individual-margin SQLite SHA256 does not match its audit")
    if aggregate_hash != aggregate_audit.get("dfcf_margin_balances_sha256"):
        raise RuntimeError("Aggregate-margin CSV SHA256 does not match its audit")
    wal_path = Path(f"{config.db_path}-wal")
    if wal_path.exists() and wal_path.stat().st_size != 0:
        raise RuntimeError("Individual-margin SQLite has a non-empty WAL snapshot")

    connection = sqlite3.connect(f"file:{config.db_path}?mode=ro", uri=True)
    try:
        quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
        database_stats = connection.execute(
            """
            SELECT
                COUNT(*),
                COUNT(DISTINCT trade_date),
                MIN(trade_date),
                MAX(trade_date)
            FROM margin_daily
            """
        ).fetchone()
        duplicate = connection.execute(
            """
            SELECT 1
            FROM margin_daily
            GROUP BY trade_date, secu_code, vendor_market
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        ).fetchone()
    finally:
        connection.close()
    if quick_check != "ok":
        raise RuntimeError(f"Individual-margin SQLite quick_check failed: {quick_check}")
    if duplicate is not None:
        raise RuntimeError("Individual-margin SQLite contains duplicate primary keys")
    if int(database_stats[0]) != int(individual.get("database_rows", -1)):
        raise RuntimeError("Individual-margin SQLite row count does not match its audit")
    if int(database_stats[1]) != int(individual.get("database_dates", -1)):
        raise RuntimeError("Individual-margin SQLite date count does not match its audit")
    if str(database_stats[2]) != str(individual.get("database_start")):
        raise RuntimeError("Individual-margin SQLite start date does not match its audit")
    if str(database_stats[3]) != str(individual.get("database_end")):
        raise RuntimeError("Individual-margin SQLite end date does not match its audit")

    aggregate_dates = set(aggregate["date"])
    index_dates = set(index_frame["date"])
    missing_index_dates = sorted(aggregate_dates.difference(index_dates))
    if missing_index_dates:
        raise RuntimeError(
            f"Index calendar misses aggregate dates: {missing_index_dates[:10]}"
        )
    aggregate_latest = aggregate["date"].max().strftime("%Y-%m-%d")
    if aggregate_latest != aggregate_audit.get("latest_common_date"):
        raise RuntimeError("Aggregate CSV latest date does not match aggregate audit")

    return {
        "individual_audit": individual,
        "aggregate_audit": aggregate_audit,
        "database_quick_check": quick_check,
        "database_rows": int(database_stats[0]),
        "database_dates": int(database_stats[1]),
        "database_start": str(database_stats[2]),
        "database_end": str(database_stats[3]),
        "database_duplicate_primary_keys": 0,
        "aggregate_rows": len(aggregate),
        "aggregate_start": aggregate["date"].min(),
        "aggregate_end": aggregate["date"].max(),
        "index_calendar_missing_aggregate_dates": 0,
        "input_hashes": {
            "individual_margin_sqlite": database_hash,
            "individual_margin_audit_json": sha256_file(
                config.individual_audit_json
            ),
            "aggregate_margin_csv": aggregate_hash,
            "aggregate_margin_audit_json": sha256_file(
                config.aggregate_audit_json
            ),
            "index_day_file_before": sha256_file(config.index_day_path),
            "market_snapshot_manifest": sha256_file(
                config.market_snapshot_manifest
            ),
            "analysis_script": sha256_file(Path(__file__).resolve()),
        },
    }


def mark_long_break_eves(dates: pd.Series) -> pd.Series:
    ordered = pd.to_datetime(dates)
    return (ordered.shift(-1) - ordered).dt.days.ge(5).fillna(False)


def causal_percentile(
    series: pd.Series,
    window: int = CAUSAL_RANK_WINDOW,
    min_periods: int = CAUSAL_RANK_MIN_OBSERVATIONS,
) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")

    def last_percentile(values: np.ndarray) -> float:
        current = values[-1]
        if not np.isfinite(current):
            return np.nan
        clean = values[np.isfinite(values)]
        if len(clean) < min_periods:
            return np.nan
        lower = np.count_nonzero(clean < current)
        equal = np.count_nonzero(clean == current)
        return float((lower + 0.5 * equal) / len(clean))

    return numeric.rolling(window=window, min_periods=min_periods).apply(
        last_percentile, raw=True
    )


def rolling_z_score(
    series: pd.Series,
    window: int = CAUSAL_RANK_WINDOW,
    min_periods: int = CAUSAL_RANK_MIN_OBSERVATIONS,
) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    mean = numeric.rolling(window, min_periods=min_periods).mean()
    std = numeric.rolling(window, min_periods=min_periods).std(ddof=0)
    return (numeric - mean) / std.replace(0.0, np.nan)


def forward_max_drawdown_pct(
    values: pd.Series,
    horizon: int,
    valid_observation: pd.Series | None = None,
) -> pd.Series:
    """Worst future close return relative to T close, not path peak-to-trough MDD."""

    array = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    valid = (
        pd.Series(valid_observation, index=values.index)
        .fillna(False)
        .to_numpy(dtype=bool)
        if valid_observation is not None
        else np.isfinite(array)
    )
    output = np.full(len(array), np.nan, dtype=float)
    for index in range(len(array)):
        if (
            not np.isfinite(array[index])
            or not valid[index]
            or index + horizon >= len(array)
        ):
            continue
        future = array[index + 1 : index + horizon + 1]
        future_valid = valid[index + 1 : index + horizon + 1]
        if len(future) != horizon or not future_valid.all() or not np.isfinite(future).all():
            continue
        output[index] = (future.min() / array[index] - 1.0) * 100.0
    return pd.Series(output, index=values.index)


def detect_peak_events(
    values: pd.Series,
    horizon: int = PRIMARY_DRAWDOWN_HORIZON,
    drawdown_threshold_pct: float = PRIMARY_DRAWDOWN_THRESHOLD,
    trailing_high_window: int = 60,
    decluster_days: int = EVENT_DECLUSTER_DAYS,
    valid_observation: pd.Series | None = None,
) -> list[int]:
    numeric = pd.to_numeric(values, errors="coerce")
    trailing_high = numeric.rolling(trailing_high_window, min_periods=40).max()
    future_drawdown = forward_max_drawdown_pct(
        numeric, horizon, valid_observation=valid_observation
    )
    candidates = np.flatnonzero(
        (
            numeric.ge(trailing_high * 0.999)
            & future_drawdown.le(drawdown_threshold_pct)
        ).fillna(False).to_numpy()
    ).tolist()
    if not candidates:
        return []

    clusters: list[list[int]] = [[candidates[0]]]
    for position in candidates[1:]:
        if position - clusters[-1][-1] <= decluster_days:
            clusters[-1].append(position)
        else:
            clusters.append([position])

    events = []
    array = numeric.to_numpy(dtype=float)
    for cluster in clusters:
        finite = [position for position in cluster if np.isfinite(array[position])]
        if finite:
            events.append(max(finite, key=lambda position: array[position]))
    return events


def label_event_within_horizon(
    length: int,
    event_positions: Sequence[int],
    horizon: int,
    confirmation_horizon: int = 0,
    valid_observation: pd.Series | None = None,
) -> pd.Series:
    """Label whether a fully observable event occurs in T+1 through T+horizon."""

    labels = np.zeros(length, dtype=float)
    for event_position in event_positions:
        start = max(0, event_position - horizon)
        labels[start:event_position] = 1.0
    censor_length = horizon + confirmation_horizon
    if censor_length > 0:
        labels[max(0, length - censor_length) :] = np.nan
    if valid_observation is not None:
        valid = (
            pd.Series(valid_observation)
            .fillna(False)
            .to_numpy(dtype=bool)
        )
        if len(valid) != length:
            raise ValueError("valid_observation length does not match labels")
        for position in range(max(0, length - censor_length)):
            if not valid[position : position + censor_length + 1].all():
                labels[position] = np.nan
    return pd.Series(labels, dtype="Int64")


def classify_trend_regime(
    close: pd.Series,
    ma20: pd.Series,
    ma50: pd.Series,
    ma250: pd.Series,
) -> pd.Series:
    complete = pd.concat([close, ma20, ma50, ma250], axis=1).notna().all(axis=1)
    uptrend = (
        close.gt(ma250)
        & ma20.gt(ma50)
        & ma50.gt(ma250)
        & complete
    )
    downtrend = (
        close.lt(ma250)
        & ma20.lt(ma50)
        & ma50.lt(ma250)
        & complete
    )
    output = pd.Series(pd.NA, index=close.index, dtype="string")
    output.loc[complete] = "transition"
    output.loc[uptrend] = "uptrend"
    output.loc[downtrend] = "downtrend"
    return output


def mean_pairwise_residual_correlation(
    members: Sequence[str],
    return_history: dict[str, deque[tuple[int, float]]],
    market_median_by_position: dict[int, float],
    current_position: int,
    lookback: int = 20,
) -> tuple[float, int]:
    expected_positions = list(range(current_position - lookback + 1, current_position + 1))
    rows = []
    for code in members:
        history = return_history.get(code)
        if history is None or len(history) < lookback:
            continue
        tail = list(history)[-lookback:]
        if [position for position, _ in tail] != expected_positions:
            continue
        market_values = [market_median_by_position.get(position) for position in expected_positions]
        if any(value is None or not np.isfinite(value) for value in market_values):
            continue
        residual = np.asarray([value for _, value in tail], dtype=float) - np.asarray(
            market_values, dtype=float
        )
        std = residual.std(ddof=0)
        if not np.isfinite(std) or std <= 1e-12:
            continue
        rows.append((residual - residual.mean()) / std)

    count = len(rows)
    if count < 2:
        return (math.nan, count)
    matrix = np.vstack(rows)
    time_count = matrix.shape[1]
    summed = matrix.sum(axis=0)
    numerator = float(np.square(summed).sum() - count * time_count)
    denominator = float(count * (count - 1) * time_count)
    return (float(np.clip(numerator / denominator, -1.0, 1.0)), count)


def _safe_ratio(numerator: float, denominator: float, scale: float = 100.0) -> float:
    if not np.isfinite(denominator) or denominator <= 0:
        return math.nan
    return float(numerator / denominator * scale)


def margin_flow_validity(
    frame: pd.DataFrame,
    coverage_threshold: float = MIN_MARGIN_FLOW_COVERAGE,
) -> pd.Series:
    eligible = frame["crowd_financing_eligible_t_minus_1_count"]
    required = np.maximum(20, eligible * coverage_threshold)
    return (
        eligible.ge(30)
        & frame["crowd_margin_continuity_coverage"].ge(coverage_threshold)
        & frame["crowd_flow_comparable_count"].ge(required)
    )


def build_daily_micro_panel(
    config: StudyConfig,
    aggregate_calendar: pd.DataFrame,
    index_calendar: pd.DataFrame,
    price_rows_by_date: dict[
        int, list[tuple[str, float, float, bool, float, float]]
    ],
) -> tuple[pd.DataFrame, dict[str, object]]:
    aggregate_dates = set(
        aggregate_calendar["date"].dt.strftime("%Y-%m-%d").tolist()
    )
    calendar = (
        index_calendar[["date"]]
        .drop_duplicates()
        .sort_values("date")
        .reset_index(drop=True)
    )
    calendar["date_str"] = calendar["date"].dt.strftime("%Y-%m-%d")
    calendar["date_i"] = calendar["date"].dt.strftime("%Y%m%d").astype(int)
    calendar_position = dict(
        zip(calendar["date_str"], calendar.index, strict=True)
    )

    connection = sqlite3.connect(f"file:{config.db_path}?mode=ro", uri=True)
    query = """
        SELECT
            trade_date,
            secu_code,
            financing_balance_yuan,
            financing_buy_yuan,
            financing_repay_yuan,
            financing_net_buy_yuan,
            close_price,
            change_pct
        FROM a_share_stock_margin_daily
        WHERE trade_date >= ?
          AND (? IS NULL OR trade_date <= ?)
          AND vendor_market IN ('融资融券_沪证', '融资融券_深证')
        ORDER BY trade_date, secu_code
    """
    cursor = connection.execute(
        query, (config.start_date, config.end_date, config.end_date)
    )
    grouped_iter = iter(itertools.groupby(cursor, key=lambda row: row[0]))
    current_group = next(grouped_iter, None)

    return_history: dict[str, deque[tuple[int, float]]] = defaultdict(
        lambda: deque(maxlen=MOMENTUM_OBSERVATIONS)
    )
    top_hit_positions: dict[str, deque[int]] = defaultdict(deque)
    previous_balance: dict[str, tuple[int, float]] = {}
    last_price_position: dict[str, int] = {}
    market_median_by_position: dict[int, float] = {}
    previous_crowd: set[str] = set()
    rows_out: list[dict[str, object]] = []
    processed_margin_rows = 0
    continuous_rows = 0
    balance_net_mismatch_rows = 0
    balance_net_abs_residual_yuan = 0.0
    tdx_dfcf_close_comparable = 0
    tdx_dfcf_close_exact = 0

    for calendar_row in calendar.itertuples(index=False):
        trade_date = calendar_row.date_str
        date_i = int(calendar_row.date_i)
        position = int(calendar_position[trade_date])
        price_rows = price_rows_by_date.get(date_i, [])
        if not price_rows:
            continue

        price_codes = [row[0] for row in price_rows]
        price_returns = np.asarray([row[1] for row in price_rows], dtype=float)
        momentum_returns = np.asarray([row[2] for row in price_rows], dtype=float)
        reset_flags = np.asarray([row[3] for row in price_rows], dtype=bool)
        price_closes = np.asarray([row[4] for row in price_rows], dtype=float)
        price_amounts = np.asarray([row[5] for row in price_rows], dtype=float)
        price_code_to_offset = {
            code: offset for offset, code in enumerate(price_codes)
        }

        momentum_by_code: dict[str, float] = {}
        for code, momentum_return, reset in zip(
            price_codes, momentum_returns, reset_flags, strict=True
        ):
            history = return_history[code]
            if reset:
                history.clear()
            if np.isfinite(momentum_return) and momentum_return > -100.0:
                history.append((position, float(momentum_return)))
            if (
                np.isfinite(momentum_return)
                and len(history) >= MIN_MOMENTUM_OBSERVATIONS
                and list(history)[-MIN_MOMENTUM_OBSERVATIONS][0]
                >= position - MOMENTUM_DENSITY_SPAN
            ):
                values = (
                    np.asarray(
                        [value for _, value in list(history)[-MOMENTUM_OBSERVATIONS:]],
                        dtype=float,
                    )
                    / 100.0
                )
                momentum_by_code[code] = float(np.log1p(values).sum())

        finite_price_returns = price_returns[np.isfinite(price_returns)]
        market_median = (
            float(np.median(finite_price_returns))
            if len(finite_price_returns)
            else math.nan
        )
        market_median_by_position[position] = market_median
        market_down_share = (
            float(
                np.count_nonzero(finite_price_returns < 0.0)
                / len(finite_price_returns)
                * 100.0
            )
            if len(finite_price_returns)
            else math.nan
        )

        next_crowd: set[str] = set()
        candidate_count = 0
        momentum_threshold = math.nan
        if momentum_by_code:
            momentum_values = np.fromiter(momentum_by_code.values(), dtype=float)
            momentum_threshold = float(
                np.quantile(momentum_values, config.candidate_quantile)
            )
            candidates = [
                code
                for code, momentum in momentum_by_code.items()
                if momentum >= momentum_threshold
            ]
            candidate_count = len(candidates)
            for code in candidates:
                hits = top_hit_positions[code]
                hits.append(position)
                while hits and hits[0] < position - PERSISTENCE_DAYS + 1:
                    hits.popleft()
                if len(hits) >= config.persistence_min_hits:
                    next_crowd.add(code)
            if len(next_crowd) < config.min_crowd_size:
                next_crowd = set()

        analysis_crowd = previous_crowd
        crowd_return_values = []
        crowd_turnover_yuan = 0.0
        for code in analysis_crowd:
            offset = price_code_to_offset.get(code)
            if offset is not None and np.isfinite(price_returns[offset]):
                crowd_return_values.append(float(price_returns[offset]))
                if np.isfinite(price_amounts[offset]):
                    crowd_turnover_yuan += float(price_amounts[offset])
            elif last_price_position.get(code) == position - 1:
                # A member selected yesterday but missing today is treated as a
                # one-day suspension with unchanged marked price.
                crowd_return_values.append(0.0)
        crowd_return_array = np.asarray(crowd_return_values, dtype=float)
        crowd_return_coverage = (
            len(crowd_return_array) / len(analysis_crowd)
            if analysis_crowd
            else math.nan
        )
        crowd_strategy_return_pct = (
            float(crowd_return_array.mean())
            if analysis_crowd
            and crowd_return_coverage >= MIN_CROWD_RETURN_COVERAGE
            and len(crowd_return_array)
            else math.nan
        )
        crowd_return_pct = crowd_strategy_return_pct
        rest_return_values = [
            price_returns[offset]
            for offset, code in enumerate(price_codes)
            if code not in analysis_crowd and np.isfinite(price_returns[offset])
        ]
        rest_return_pct = (
            float(np.mean(rest_return_values))
            if rest_return_values
            else math.nan
        )
        crowd_sync = (
            _safe_ratio(
                abs(float(crowd_return_array.mean())),
                float(np.mean(np.abs(crowd_return_array))),
                scale=1.0,
            )
            if len(crowd_return_array)
            else math.nan
        )
        crowd_momentum_values = [
            momentum_by_code[code]
            for code in analysis_crowd
            if code in momentum_by_code
        ]
        all_momentum_values = list(momentum_by_code.values())
        crowd_momentum_spread = (
            float(
                np.median(crowd_momentum_values)
                - np.median(all_momentum_values)
            )
            if crowd_momentum_values and all_momentum_values
            else math.nan
        )
        crowd_correlation, correlation_members = (
            mean_pairwise_residual_correlation(
                sorted(analysis_crowd),
                return_history,
                market_median_by_position,
                position,
            )
        )
        for code in price_codes:
            last_price_position[code] = position

        while current_group is not None and current_group[0] < trade_date:
            list(current_group[1])
            current_group = next(grouped_iter, None)
        if current_group is not None and current_group[0] == trade_date:
            margin_rows = list(current_group[1])
            current_group = next(grouped_iter, None)
        else:
            margin_rows = []
        processed_margin_rows += len(margin_rows)

        margin_codes = [str(row[1]) for row in margin_rows]
        balances = np.asarray([float(row[2]) for row in margin_rows], dtype=float)
        buys = np.asarray(
            [float(row[3]) if row[3] is not None else np.nan for row in margin_rows],
            dtype=float,
        )
        repays = np.asarray(
            [float(row[4]) if row[4] is not None else np.nan for row in margin_rows],
            dtype=float,
        )
        net_buys = np.asarray(
            [float(row[5]) if row[5] is not None else np.nan for row in margin_rows],
            dtype=float,
        )
        margin_closes = np.asarray(
            [float(row[6]) if row[6] is not None else np.nan for row in margin_rows],
            dtype=float,
        )
        margin_code_to_offset = {
            code: offset for offset, code in enumerate(margin_codes)
        }
        crowd_margin_mask = np.asarray(
            [code in analysis_crowd for code in margin_codes], dtype=bool
        )
        rest_margin_mask = ~crowd_margin_mask
        crowd_margin_present_count = int(np.count_nonzero(crowd_margin_mask))
        crowd_margin_coverage = (
            crowd_margin_present_count / len(analysis_crowd)
            if analysis_crowd
            else math.nan
        )
        crowd_financing_eligible_t_minus_1_count = sum(
            1
            for code in analysis_crowd
            if code in previous_balance
            and previous_balance[code][0] == position - 1
        )
        crowd_financing_eligibility_share = (
            crowd_financing_eligible_t_minus_1_count / len(analysis_crowd)
            if analysis_crowd
            else math.nan
        )

        previous_values = np.full(len(margin_codes), np.nan, dtype=float)
        balance_deltas = np.full(len(margin_codes), np.nan, dtype=float)
        adjustment_residuals = np.full(len(margin_codes), np.nan, dtype=float)
        valid_change = np.zeros(len(margin_codes), dtype=bool)
        for offset, (code, balance) in enumerate(
            zip(margin_codes, balances, strict=True)
        ):
            previous = previous_balance.get(code)
            if previous is not None and previous[0] == position - 1 and previous[1] > 0.0:
                previous_values[offset] = previous[1]
                balance_deltas[offset] = balance - previous[1]
                valid_change[offset] = True
                continuous_rows += 1
                if np.isfinite(net_buys[offset]):
                    residual = balance_deltas[offset] - net_buys[offset]
                    adjustment_residuals[offset] = residual
                    balance_net_abs_residual_yuan += abs(residual)
                    tolerance = max(1.0, abs(balance_deltas[offset]) * 1e-9)
                    if abs(residual) > tolerance:
                        balance_net_mismatch_rows += 1
            previous_balance[code] = (position, balance)

            price_offset = price_code_to_offset.get(code)
            if (
                price_offset is not None
                and np.isfinite(margin_closes[offset])
                and np.isfinite(price_closes[price_offset])
            ):
                tdx_dfcf_close_comparable += 1
                if abs(margin_closes[offset] - price_closes[price_offset]) < 0.005:
                    tdx_dfcf_close_exact += 1

        crowd_valid = crowd_margin_mask & valid_change
        rest_valid = rest_margin_mask & valid_change
        crowd_margin_continuity_coverage = (
            np.count_nonzero(crowd_valid)
            / crowd_financing_eligible_t_minus_1_count
            if crowd_financing_eligible_t_minus_1_count
            else math.nan
        )
        crowd_previous_sum = float(np.nansum(previous_values[crowd_valid]))
        rest_previous_sum = float(np.nansum(previous_values[rest_valid]))
        crowd_balance_delta_sum = float(
            np.nansum(balance_deltas[crowd_valid])
        )
        rest_balance_delta_sum = float(np.nansum(balance_deltas[rest_valid]))
        crowd_balance_flow_pct = _safe_ratio(
            crowd_balance_delta_sum, crowd_previous_sum
        )
        rest_balance_flow_pct = _safe_ratio(
            rest_balance_delta_sum, rest_previous_sum
        )
        balance_flow_spread_pct = (
            crowd_balance_flow_pct - rest_balance_flow_pct
            if np.isfinite(crowd_balance_flow_pct)
            and np.isfinite(rest_balance_flow_pct)
            else math.nan
        )
        crowd_transaction_net_yuan = float(np.nansum(net_buys[crowd_valid]))
        rest_transaction_net_yuan = float(np.nansum(net_buys[rest_valid]))
        crowd_transaction_net_pct = _safe_ratio(
            crowd_transaction_net_yuan, crowd_previous_sum
        )
        rest_transaction_net_pct = _safe_ratio(
            rest_transaction_net_yuan, rest_previous_sum
        )
        transaction_spread_pct = (
            crowd_transaction_net_pct - rest_transaction_net_pct
            if np.isfinite(crowd_transaction_net_pct)
            and np.isfinite(rest_transaction_net_pct)
            else math.nan
        )
        crowd_adjustment_pct = _safe_ratio(
            float(np.nansum(adjustment_residuals[crowd_valid])),
            crowd_previous_sum,
        )
        all_previous_sum = float(np.nansum(previous_values[valid_change]))
        all_adjustment_abs_pct = _safe_ratio(
            float(np.nansum(np.abs(adjustment_residuals[valid_change]))),
            all_previous_sum,
        )
        accounting_adjustment_day = (
            bool(all_adjustment_abs_pct > 0.10)
            if np.isfinite(all_adjustment_abs_pct)
            else False
        )
        crowd_outflow_breadth = (
            float(
                np.count_nonzero(balance_deltas[crowd_valid] < 0.0)
                / np.count_nonzero(crowd_valid)
                * 100.0
            )
            if np.count_nonzero(crowd_valid)
            else math.nan
        )
        crowd_transaction_outflow_breadth = (
            float(
                np.count_nonzero(net_buys[crowd_valid] < 0.0)
                / np.count_nonzero(crowd_valid)
                * 100.0
            )
            if np.count_nonzero(crowd_valid)
            else math.nan
        )
        rest_outflow_breadth = (
            float(
                np.count_nonzero(balance_deltas[rest_valid] < 0.0)
                / np.count_nonzero(rest_valid)
                * 100.0
            )
            if np.count_nonzero(rest_valid)
            else math.nan
        )

        denominator_valid = valid_change & (
            previous_values >= FLOW_DENOMINATOR_FLOOR_YUAN
        )
        delta_rates = np.full(len(margin_codes), np.nan, dtype=float)
        delta_rates[denominator_valid] = (
            balance_deltas[denominator_valid]
            / previous_values[denominator_valid]
            * 100.0
        )
        cross_section_rates = delta_rates[
            denominator_valid & np.isfinite(delta_rates)
        ]
        extreme_cutoff = (
            float(np.quantile(cross_section_rates, 0.10))
            if len(cross_section_rates) >= 100
            else math.nan
        )
        crowd_rate_values = delta_rates[
            crowd_margin_mask & denominator_valid & np.isfinite(delta_rates)
        ]
        crowd_extreme_outflow_share = (
            float(
                np.count_nonzero(crowd_rate_values <= extreme_cutoff)
                / len(crowd_rate_values)
                * 100.0
            )
            if len(crowd_rate_values) and np.isfinite(extreme_cutoff)
            else math.nan
        )

        continuous_current_balances = balances[valid_change]
        crowd_continuous_balance = float(np.nansum(balances[crowd_valid]))
        continuous_balance_sum = float(
            np.nansum(continuous_current_balances)
        )
        crowd_margin_share = _safe_ratio(
            crowd_continuous_balance, continuous_balance_sum
        )
        positive_balances = continuous_current_balances[
            np.isfinite(continuous_current_balances)
            & (continuous_current_balances > 0.0)
        ]
        margin_hhi = (
            float(
                np.square(
                    positive_balances / positive_balances.sum()
                ).sum()
            )
            if len(positive_balances)
            else math.nan
        )
        normalized_hhi = (
            float(
                (margin_hhi - 1.0 / len(positive_balances))
                / (1.0 - 1.0 / len(positive_balances))
            )
            if len(positive_balances) > 1 and np.isfinite(margin_hhi)
            else math.nan
        )
        effective_margin_names = (
            1.0 / margin_hhi
            if np.isfinite(margin_hhi) and margin_hhi > 0.0
            else math.nan
        )
        sorted_balances = np.sort(positive_balances)
        top10_margin_share = (
            _safe_ratio(
                float(sorted_balances[-10:].sum()),
                float(sorted_balances.sum()),
            )
            if len(sorted_balances)
            else math.nan
        )

        crowd_buy = float(np.nansum(buys[crowd_valid]))
        crowd_repay = float(np.nansum(repays[crowd_valid]))
        crowd_activity = crowd_buy + crowd_repay
        crowd_buy_repay_pressure = _safe_ratio(
            crowd_buy - crowd_repay, crowd_activity
        )
        crowd_buy_rate = _safe_ratio(crowd_buy, crowd_previous_sum)
        crowd_repay_rate = _safe_ratio(crowd_repay, crowd_previous_sum)
        crowd_buy_to_turnover = _safe_ratio(
            crowd_buy, crowd_turnover_yuan
        )
        crowd_transaction_net_to_turnover = _safe_ratio(
            crowd_transaction_net_yuan, crowd_turnover_yuan
        )

        crowd_code_balance = sorted(
            (
                (margin_codes[offset], balances[offset])
                for offset in np.flatnonzero(crowd_margin_mask)
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        top_margin_codes = [code for code, _ in crowd_code_balance[:10]]

        if trade_date in aggregate_dates:
            rows_out.append(
                {
                    "date": trade_date,
                    "market_price_count": len(price_codes),
                    "financing_stock_count": len(margin_codes),
                    "momentum_eligible_count": len(momentum_by_code),
                    "candidate_count": candidate_count,
                    "crowd_count": len(analysis_crowd),
                    "next_day_crowd_count": len(next_crowd),
                    "crowd_return_coverage": crowd_return_coverage,
                    "crowd_margin_coverage": crowd_margin_coverage,
                    "crowd_financing_eligible_t_minus_1_count": (
                        crowd_financing_eligible_t_minus_1_count
                    ),
                    "crowd_financing_eligibility_share_pct": (
                        crowd_financing_eligibility_share * 100.0
                        if np.isfinite(crowd_financing_eligibility_share)
                        else math.nan
                    ),
                    "crowd_margin_continuity_coverage": (
                        crowd_margin_continuity_coverage
                    ),
                    "momentum_threshold_log": momentum_threshold,
                    "crowd_momentum_spread_log": crowd_momentum_spread,
                    "crowd_return_pct": crowd_return_pct,
                    "rest_return_pct": rest_return_pct,
                    "crowd_return_spread_pct": (
                        crowd_return_pct - rest_return_pct
                        if np.isfinite(crowd_return_pct)
                        and np.isfinite(rest_return_pct)
                        else math.nan
                    ),
                    "crowd_strategy_return_pct": crowd_strategy_return_pct,
                    "crowd_sync": crowd_sync,
                    "crowd_corr20": crowd_correlation,
                    "crowd_corr20_members": correlation_members,
                    "market_return_median_pct": market_median,
                    "market_down_share_pct": market_down_share,
                    "crowd_margin_share_pct": crowd_margin_share,
                    "margin_balance_hhi": margin_hhi,
                    "margin_balance_hhi_normalized": normalized_hhi,
                    "effective_margin_names": effective_margin_names,
                    "top10_margin_share_pct": top10_margin_share,
                    "crowd_margin_flow_pct": crowd_balance_flow_pct,
                    "rest_margin_flow_pct": rest_balance_flow_pct,
                    "crowd_vs_rest_flow_spread_pct": balance_flow_spread_pct,
                    "crowd_transaction_net_pct": crowd_transaction_net_pct,
                    "rest_transaction_net_pct": rest_transaction_net_pct,
                    "crowd_vs_rest_transaction_spread_pct": transaction_spread_pct,
                    "crowd_adjustment_residual_pct": crowd_adjustment_pct,
                    "all_adjustment_abs_pct_of_previous_balance": all_adjustment_abs_pct,
                    "accounting_adjustment_day": accounting_adjustment_day,
                    "crowd_outflow_breadth_pct": crowd_outflow_breadth,
                    "crowd_transaction_outflow_breadth_pct": crowd_transaction_outflow_breadth,
                    "rest_outflow_breadth_pct": rest_outflow_breadth,
                    "crowd_extreme_outflow_share_pct": crowd_extreme_outflow_share,
                    "crowd_extreme_outflow_cutoff_pct": extreme_cutoff,
                    "crowd_buy_rate_pct": crowd_buy_rate,
                    "crowd_repay_rate_pct": crowd_repay_rate,
                    "crowd_buy_repay_pressure_pct": crowd_buy_repay_pressure,
                    "crowd_buy_to_turnover_pct": crowd_buy_to_turnover,
                    "crowd_transaction_net_to_turnover_pct": crowd_transaction_net_to_turnover,
                    "crowd_flow_comparable_count": int(
                        np.count_nonzero(crowd_valid)
                    ),
                    "rest_flow_comparable_count": int(
                        np.count_nonzero(rest_valid)
                    ),
                    "crowd_member_codes": ";".join(
                        sorted(analysis_crowd)
                    ),
                    "crowd_top_margin_codes": ";".join(top_margin_codes),
                }
            )
        previous_crowd = next_crowd

    connection.close()
    panel = pd.DataFrame(rows_out)
    if panel.empty:
        raise ValueError("No stock-level daily panel was built")
    panel["date"] = pd.to_datetime(panel["date"], errors="raise")
    panel = panel.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    audit = {
        "processed_margin_rows_sh_sz": processed_margin_rows,
        "panel_dates": len(panel),
        "panel_start": panel["date"].min(),
        "panel_end": panel["date"].max(),
        "continuous_stock_rows": continuous_rows,
        "balance_net_mismatch_rows": balance_net_mismatch_rows,
        "balance_net_mismatch_ratio": (
            balance_net_mismatch_rows / continuous_rows
            if continuous_rows
            else None
        ),
        "balance_net_absolute_residual_yuan": balance_net_abs_residual_yuan,
        "tdx_dfcf_close_comparable_rows": tdx_dfcf_close_comparable,
        "tdx_dfcf_close_exact_rows": tdx_dfcf_close_exact,
        "tdx_dfcf_close_exact_ratio": (
            tdx_dfcf_close_exact / tdx_dfcf_close_comparable
            if tdx_dfcf_close_comparable
            else None
        ),
        "crowd_definition": {
            "price_universe": "all locally retained SH/SZ A-share TDX day files",
            "momentum_observations": MOMENTUM_OBSERVATIONS,
            "minimum_momentum_observations": MIN_MOMENTUM_OBSERVATIONS,
            "ipo_momentum_exclusion_observations": IPO_MOMENTUM_EXCLUSION_OBSERVATIONS,
            "raw_return_break_threshold_pct": RAW_RETURN_BREAK_THRESHOLD_PCT,
            "candidate_quantile": config.candidate_quantile,
            "persistence_days": PERSISTENCE_DAYS,
            "persistence_min_hits": config.persistence_min_hits,
            "minimum_crowd_size": config.min_crowd_size,
            "membership_lag_for_returns_and_margin": 1,
            "suspension_return": (
                "0% only for a T-1 member whose last local price record is T-1; "
                "otherwise the member is missing and the coverage gate applies"
            ),
        },
    }
    return panel, audit


def add_derived_features(
    panel: pd.DataFrame,
    aggregate_margin: pd.DataFrame,
    index_frame: pd.DataFrame,
) -> pd.DataFrame:
    frame = panel.merge(
        aggregate_margin[
            ["date", "total_margin_y", "total_change_pct", "sample_status"]
        ],
        on="date",
        how="left",
        validate="one_to_one",
    ).merge(index_frame, on="date", how="left", validate="one_to_one")
    frame = frame.sort_values("date").reset_index(drop=True)
    frame["long_break_eve"] = mark_long_break_eves(frame["date"])
    frame["crowd_strategy_return_valid"] = (
        frame["crowd_count"].ge(MIN_CROWD_SIZE)
        & frame["crowd_return_coverage"].ge(MIN_CROWD_RETURN_COVERAGE)
        & pd.to_numeric(
            frame["crowd_strategy_return_pct"], errors="coerce"
        ).notna()
    )
    frame["individual_flow_valid"] = margin_flow_validity(
        frame, MIN_MARGIN_FLOW_COVERAGE
    )
    financing_count_change = frame["financing_stock_count"].diff()
    financing_count_change_pct = frame["financing_stock_count"].pct_change()
    frame["financing_universe_change_count"] = financing_count_change
    frame["financing_universe_change_pct"] = financing_count_change_pct * 100.0
    frame["universe_reset"] = (
        financing_count_change.abs().gt(50)
        | financing_count_change_pct.abs().gt(0.02)
    ).fillna(False)
    frame["universe_reset_last_5d"] = (
        frame["universe_reset"].astype(int).rolling(5, min_periods=1).max().astype(bool)
    )

    residual = pd.to_numeric(
        frame["all_adjustment_abs_pct_of_previous_balance"], errors="coerce"
    )
    residual_prior_q99 = (
        residual.shift(1)
        .rolling(CAUSAL_RANK_WINDOW, min_periods=CAUSAL_RANK_MIN_OBSERVATIONS)
        .quantile(0.99)
    )
    frame["adjustment_abs_pct_prior_q99"] = residual_prior_q99
    frame["accounting_adjustment_day"] = (
        residual.gt(0.10)
        | (residual_prior_q99.notna() & residual.gt(residual_prior_q99))
    ).fillna(False)

    balance_flow_columns = [
        "crowd_margin_flow_pct",
        "rest_margin_flow_pct",
        "crowd_vs_rest_flow_spread_pct",
        "crowd_outflow_breadth_pct",
        "rest_outflow_breadth_pct",
        "crowd_extreme_outflow_share_pct",
    ]
    transaction_flow_columns = [
        "crowd_transaction_net_pct",
        "rest_transaction_net_pct",
        "crowd_vs_rest_transaction_spread_pct",
        "crowd_transaction_outflow_breadth_pct",
        "crowd_buy_rate_pct",
        "crowd_repay_rate_pct",
        "crowd_buy_repay_pressure_pct",
        "crowd_buy_to_turnover_pct",
        "crowd_transaction_net_to_turnover_pct",
    ]
    aggregate_flow_columns = [
        "total_change_pct",
    ]
    for column in (
        balance_flow_columns
        + transaction_flow_columns
        + aggregate_flow_columns
    ):
        frame[f"{column}_raw"] = frame[column]
    frame.loc[
        frame["long_break_eve"],
        balance_flow_columns + transaction_flow_columns + aggregate_flow_columns,
    ] = np.nan
    frame.loc[
        ~frame["individual_flow_valid"],
        balance_flow_columns + transaction_flow_columns,
    ] = np.nan
    frame.loc[
        ~frame["individual_flow_valid"],
        [
            "crowd_margin_share_pct",
            "crowd_adjustment_residual_pct",
        ],
    ] = np.nan
    frame.loc[
        frame["accounting_adjustment_day"],
        transaction_flow_columns,
    ] = np.nan

    strategy_returns = pd.to_numeric(
        frame["crowd_strategy_return_pct"], errors="coerce"
    ).where(frame["crowd_strategy_return_valid"])
    frame["crowd_strategy_return_pct"] = strategy_returns
    frame["crowd_strategy_index"] = (
        1.0 + strategy_returns / 100.0
    ).cumprod(skipna=True) * 100.0

    for window in (5, 20, 60):
        frame[f"crowd_strategy_return_{window}d_pct"] = (
            (1.0 + strategy_returns / 100.0)
            .rolling(window, min_periods=window)
            .apply(np.prod, raw=True)
            .sub(1.0)
            .mul(100.0)
        )
    crowd_valid_60 = (
        frame["crowd_strategy_return_valid"]
        .astype(int)
        .rolling(60, min_periods=60)
        .sum()
        .eq(60)
    )
    frame["crowd_index_distance_60d_high_pct"] = (
        frame["crowd_strategy_index"]
        / frame["crowd_strategy_index"].rolling(60, min_periods=60).max()
        - 1.0
    ).mul(100.0).where(crowd_valid_60)

    frame["crowd_margin_flow_5d_pct"] = frame["crowd_margin_flow_pct"].rolling(
        5, min_periods=5
    ).sum()
    frame["crowd_margin_flow_20d_pct"] = frame["crowd_margin_flow_pct"].rolling(
        20, min_periods=20
    ).sum()
    frame["crowd_outflow_breadth_5d_pct"] = frame[
        "crowd_outflow_breadth_pct"
    ].rolling(5, min_periods=5).mean()
    frame["crowd_extreme_outflow_share_5d_pct"] = frame[
        "crowd_extreme_outflow_share_pct"
    ].rolling(5, min_periods=5).mean()
    frame["crowd_flow_spread_5d_pct"] = frame[
        "crowd_vs_rest_flow_spread_pct"
    ].rolling(5, min_periods=5).mean()
    frame["crowd_transaction_net_5d_pct"] = frame[
        "crowd_transaction_net_pct"
    ].rolling(5, min_periods=5).sum()
    frame["crowd_transaction_outflow_breadth_5d_pct"] = frame[
        "crowd_transaction_outflow_breadth_pct"
    ].rolling(5, min_periods=5).mean()
    frame["crowd_transaction_spread_5d_pct"] = frame[
        "crowd_vs_rest_transaction_spread_pct"
    ].rolling(5, min_periods=5).mean()
    frame["crowd_margin_share_change_5d_pct"] = frame[
        "crowd_margin_share_pct"
    ].diff(5).where(~frame["universe_reset_last_5d"])
    frame["margin_hhi_normalized_change_5d"] = frame[
        "margin_balance_hhi_normalized"
    ].diff(5).where(~frame["universe_reset_last_5d"])
    frame["total_margin_change_5d_pct"] = frame["total_change_pct"].rolling(
        5, min_periods=5
    ).sum()
    frame["total_margin_change_20d_pct"] = frame["total_change_pct"].rolling(
        20, min_periods=20
    ).sum()

    frame["crowd_price_flow_divergence_z"] = rolling_z_score(
        frame["crowd_strategy_return_5d_pct"]
    ) - rolling_z_score(frame["crowd_margin_flow_5d_pct"])

    for window in (20, 50, 250):
        moving_average = frame["index_close"].rolling(
            window, min_periods=window
        ).mean()
        frame[f"index_ma{window}"] = moving_average
        frame[f"index_ma{window}_gap_pct"] = (
            frame["index_close"] / moving_average - 1.0
        ) * 100.0
    frame["index_return_20d_pct"] = frame["index_close"].pct_change(20) * 100.0
    frame["trend_regime"] = classify_trend_regime(
        frame["index_close"],
        frame["index_ma20"],
        frame["index_ma50"],
        frame["index_ma250"],
    )
    for regime in ("uptrend", "downtrend", "transition"):
        frame[f"trend_{regime}"] = (
            frame["trend_regime"].eq(regime).astype(float)
        )
        frame.loc[frame["trend_regime"].isna(), f"trend_{regime}"] = np.nan

    percentile_inputs = {
        "crowd_momentum_spread_pctile": "crowd_momentum_spread_log",
        "crowd_corr20_pctile": "crowd_corr20",
        "crowd_return_20d_pctile": "crowd_strategy_return_20d_pct",
        "crowd_flow_5d_pctile": "crowd_margin_flow_5d_pct",
        "crowd_outflow_breadth_5d_pctile": "crowd_outflow_breadth_5d_pct",
        "crowd_extreme_outflow_5d_pctile": "crowd_extreme_outflow_share_5d_pct",
        "crowd_flow_spread_5d_pctile": "crowd_flow_spread_5d_pct",
        "crowd_transaction_net_5d_pctile": "crowd_transaction_net_5d_pct",
        "crowd_transaction_outflow_5d_pctile": (
            "crowd_transaction_outflow_breadth_5d_pct"
        ),
        "crowd_transaction_spread_5d_pctile": "crowd_transaction_spread_5d_pct",
        "crowd_margin_share_change_5d_pctile": "crowd_margin_share_change_5d_pct",
        "margin_hhi_change_5d_pctile": "margin_hhi_normalized_change_5d",
        "price_flow_divergence_pctile": "crowd_price_flow_divergence_z",
        "total_margin_change_5d_pctile": "total_margin_change_5d_pct",
        "total_margin_change_20d_pctile": "total_margin_change_20d_pct",
    }
    for output_column, input_column in percentile_inputs.items():
        frame[output_column] = causal_percentile(frame[input_column])

    frame["crowding_intensity_score"] = frame[
        [
            "crowd_momentum_spread_pctile",
            "crowd_corr20_pctile",
            "crowd_return_20d_pctile",
        ]
    ].mean(axis=1, skipna=False)
    frame["micro_margin_risk_score"] = pd.concat(
        [
            1.0 - frame["crowd_flow_5d_pctile"],
            frame["crowd_outflow_breadth_5d_pctile"],
            frame["crowd_extreme_outflow_5d_pctile"],
            1.0 - frame["crowd_flow_spread_5d_pctile"],
            1.0 - frame["crowd_transaction_net_5d_pctile"],
            frame["crowd_transaction_outflow_5d_pctile"],
            1.0 - frame["crowd_transaction_spread_5d_pctile"],
            1.0 - frame["crowd_margin_share_change_5d_pctile"],
            frame["margin_hhi_change_5d_pctile"],
            frame["price_flow_divergence_pctile"],
        ],
        axis=1,
    ).mean(axis=1, skipna=False)
    frame["aggregate_margin_risk_score"] = pd.concat(
        [
            1.0 - frame["total_margin_change_5d_pctile"],
            1.0 - frame["total_margin_change_20d_pctile"],
        ],
        axis=1,
    ).mean(axis=1, skipna=False)
    frame["crowd_outflow_breadth_x_downtrend"] = (
        frame["crowd_outflow_breadth_5d_pct"] * frame["trend_downtrend"]
    )
    frame["crowd_outflow_breadth_x_uptrend"] = (
        frame["crowd_outflow_breadth_5d_pct"] * frame["trend_uptrend"]
    )
    frame["divergence_x_crowding"] = (
        frame["crowd_price_flow_divergence_z"]
        * frame["crowding_intensity_score"]
    )

    for horizon in (5, 10, 20, 40):
        frame[f"crowd_future_mdd_{horizon}d_pct"] = forward_max_drawdown_pct(
            frame["crowd_strategy_index"],
            horizon,
            valid_observation=frame["crowd_strategy_return_valid"],
        )
        frame[f"market_future_mdd_{horizon}d_pct"] = forward_max_drawdown_pct(
            frame["index_close"], horizon
        )
    frame["target_crowd_drawdown_20d"] = (
        frame["crowd_future_mdd_20d_pct"].le(PRIMARY_DRAWDOWN_THRESHOLD)
    ).astype("Int64")
    frame.loc[
        frame["crowd_future_mdd_20d_pct"].isna(), "target_crowd_drawdown_20d"
    ] = pd.NA
    frame["target_market_drawdown_20d"] = (
        frame["market_future_mdd_20d_pct"].le(PRIMARY_DRAWDOWN_THRESHOLD)
    ).astype("Int64")
    frame.loc[
        frame["market_future_mdd_20d_pct"].isna(), "target_market_drawdown_20d"
    ] = pd.NA

    crowd_events = detect_peak_events(
        frame["crowd_strategy_index"],
        valid_observation=frame["crowd_strategy_return_valid"],
    )
    market_events = detect_peak_events(frame["index_close"])
    crowd_peak_candidates = detect_peak_events(
        frame["crowd_strategy_index"],
        decluster_days=0,
        valid_observation=frame["crowd_strategy_return_valid"],
    )
    market_peak_candidates = detect_peak_events(
        frame["index_close"],
        decluster_days=0,
    )
    for horizon in (5, 10, 20):
        frame[f"target_crowd_top_within_{horizon}d"] = label_event_within_horizon(
            len(frame),
            crowd_peak_candidates,
            horizon,
            confirmation_horizon=PRIMARY_DRAWDOWN_HORIZON,
            valid_observation=frame["crowd_strategy_return_valid"],
        )
        frame[f"target_market_top_within_{horizon}d"] = label_event_within_horizon(
            len(frame),
            market_peak_candidates,
            horizon,
            confirmation_horizon=PRIMARY_DRAWDOWN_HORIZON,
            valid_observation=frame["index_close"].notna(),
        )
    frame.attrs["crowd_event_positions"] = crowd_events
    frame.attrs["market_event_positions"] = market_events
    frame.attrs["crowd_peak_candidate_positions"] = crowd_peak_candidates
    frame.attrs["market_peak_candidate_positions"] = market_peak_candidates
    return frame


PRICE_FEATURES = [
    "crowd_momentum_spread_log",
    "crowd_corr20",
    "crowd_sync",
    "crowd_strategy_return_5d_pct",
    "crowd_strategy_return_20d_pct",
    "crowd_index_distance_60d_high_pct",
    "market_down_share_pct",
    "market_return_median_pct",
    "index_return_20d_pct",
    "index_ma20_gap_pct",
    "index_ma50_gap_pct",
    "index_ma250_gap_pct",
]
AGGREGATE_FEATURES = [
    "total_change_pct",
    "total_margin_change_5d_pct",
    "total_margin_change_20d_pct",
]
MICRO_FEATURES = [
    "crowd_margin_share_pct",
    "crowd_margin_share_change_5d_pct",
    "crowd_margin_flow_pct",
    "crowd_margin_flow_5d_pct",
    "crowd_outflow_breadth_pct",
    "crowd_outflow_breadth_5d_pct",
    "crowd_extreme_outflow_share_5d_pct",
    "crowd_vs_rest_flow_spread_pct",
    "crowd_flow_spread_5d_pct",
    "crowd_buy_repay_pressure_pct",
    "crowd_transaction_net_pct",
    "crowd_transaction_net_5d_pct",
    "crowd_transaction_outflow_breadth_5d_pct",
    "crowd_vs_rest_transaction_spread_pct",
    "crowd_transaction_spread_5d_pct",
    "margin_balance_hhi_normalized",
    "margin_hhi_normalized_change_5d",
    "crowd_buy_to_turnover_pct",
    "crowd_transaction_net_to_turnover_pct",
    "crowd_adjustment_residual_pct",
    "crowd_price_flow_divergence_z",
]
REGIME_INTERACTIONS = [
    "trend_uptrend",
    "trend_downtrend",
    "trend_transition",
    "crowd_outflow_breadth_x_downtrend",
    "crowd_outflow_breadth_x_uptrend",
    "divergence_x_crowding",
]
MODEL_FEATURES = {
    "price_only": PRICE_FEATURES,
    "price_plus_aggregate": PRICE_FEATURES + AGGREGATE_FEATURES,
    "price_plus_aggregate_plus_individual": PRICE_FEATURES
    + AGGREGATE_FEATURES
    + MICRO_FEATURES,
    "individual_plus_regime": PRICE_FEATURES
    + AGGREGATE_FEATURES
    + MICRO_FEATURES
    + REGIME_INTERACTIONS,
}
MODEL_TARGETS = [
    "target_crowd_drawdown_20d",
    "target_market_drawdown_20d",
    "target_crowd_top_within_10d",
    "target_market_top_within_10d",
]


def make_logistic_pipeline(features: Sequence[str]) -> Pipeline:
    transformer = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(strategy="median", keep_empty_features=True),
                        ),
                        ("scaler", StandardScaler()),
                    ]
                ),
                list(features),
            )
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return Pipeline(
        [
            ("preprocess", transformer),
            (
                "model",
                LogisticRegression(
                    C=0.5,
                    solver="liblinear",
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    )


def binary_metrics(
    labels: np.ndarray,
    probabilities: np.ndarray,
    flags: np.ndarray,
) -> dict[str, float | int | None]:
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    flags = np.asarray(flags, dtype=int)
    if len(np.unique(labels)) < 2:
        roc_auc = None
        average_precision = None
    else:
        roc_auc = float(roc_auc_score(labels, probabilities))
        average_precision = float(average_precision_score(labels, probabilities))
    return {
        "n": int(len(labels)),
        "positives": int(labels.sum()),
        "prevalence": float(labels.mean()) if len(labels) else None,
        "roc_auc": roc_auc,
        "average_precision": average_precision,
        "brier": float(brier_score_loss(labels, probabilities)) if len(labels) else None,
        "flag_rate": float(flags.mean()) if len(flags) else None,
        "flag_precision": float(precision_score(labels, flags, zero_division=0)),
        "flag_recall": float(recall_score(labels, flags, zero_division=0)),
        "flag_event_rate": float(labels[flags == 1].mean()) if np.any(flags == 1) else None,
        "risk_lift": (
            float(labels[flags == 1].mean() / labels.mean())
            if np.any(flags == 1) and labels.mean() > 0
            else None
        ),
    }


def walk_forward_models(
    frame: pd.DataFrame,
    targets: Sequence[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    working = frame.copy()
    working["_position"] = np.arange(len(working))
    predictions: list[dict[str, object]] = []
    metrics: list[dict[str, object]] = []
    coefficients: list[dict[str, object]] = []

    for target in targets:
        target_valid = working[target].notna()
        for model_name, features in MODEL_FEATURES.items():
            for year in sorted(
                working.loc[
                    target_valid & working["date"].ge(MODEL_START_DATE), "date"
                ].dt.year.unique()
            ):
                test_mask = (
                    target_valid
                    & working["date"].dt.year.eq(year)
                    & working["date"].ge(MODEL_START_DATE)
                    & ~working["long_break_eve"]
                )
                test_positions = working.loc[test_mask, "_position"]
                if test_positions.empty:
                    continue
                cutoff_position = int(test_positions.min()) - MODEL_EMBARGO_DAYS
                train_mask = (
                    target_valid
                    & working["_position"].lt(cutoff_position)
                    & ~working["long_break_eve"]
                )
                train = working.loc[train_mask]
                test = working.loc[test_mask]
                if len(train) < 500 or train[target].nunique() < 2:
                    continue

                pipeline = make_logistic_pipeline(features)
                pipeline.fit(train[list(features)], train[target].astype(int))
                train_probabilities = pipeline.predict_proba(train[list(features)])[:, 1]
                threshold = float(np.quantile(train_probabilities, 0.90))
                test_probabilities = pipeline.predict_proba(test[list(features)])[:, 1]
                test_flags = (test_probabilities >= threshold).astype(int)

                for (_, row), probability, flag in zip(
                    test.iterrows(),
                    test_probabilities,
                    test_flags,
                    strict=True,
                ):
                    predictions.append(
                        {
                            "date": row["date"],
                            "target": target,
                            "model": model_name,
                            "test_year": int(year),
                            "probability": float(probability),
                            "training_probability_q90": threshold,
                            "risk_flag": int(flag),
                            "label": int(row[target]),
                        }
                    )

                fold_metrics = binary_metrics(
                    test[target].astype(int).to_numpy(),
                    test_probabilities,
                    test_flags,
                )
                metrics.append(
                    {
                        "scope": "year",
                        "target": target,
                        "model": model_name,
                        "year": int(year),
                        "train_end": train["date"].max(),
                        "test_start": test["date"].min(),
                        "test_end": test["date"].max(),
                        **fold_metrics,
                    }
                )

                model = pipeline.named_steps["model"]
                for feature, coefficient in zip(
                    features, model.coef_[0], strict=True
                ):
                    coefficients.append(
                        {
                            "target": target,
                            "model": model_name,
                            "year": int(year),
                            "feature": feature,
                            "standardized_coefficient": float(coefficient),
                        }
                    )

    prediction_frame = pd.DataFrame(predictions)
    metric_frame = pd.DataFrame(metrics)
    coefficient_frame = pd.DataFrame(coefficients)
    if prediction_frame.empty:
        raise ValueError("No walk-forward predictions were produced")

    pooled_metrics = []
    for (target, model_name), group in prediction_frame.groupby(
        ["target", "model"], sort=True
    ):
        values = binary_metrics(
            group["label"].to_numpy(),
            group["probability"].to_numpy(),
            group["risk_flag"].to_numpy(),
        )
        pooled_metrics.append(
            {
                "scope": "pooled_oos",
                "target": target,
                "model": model_name,
                "year": "all",
                "train_end": pd.NaT,
                "test_start": group["date"].min(),
                "test_end": group["date"].max(),
                **values,
            }
        )
    metric_frame = pd.concat(
        [metric_frame, pd.DataFrame(pooled_metrics)],
        ignore_index=True,
    )
    return prediction_frame, metric_frame, coefficient_frame


def build_calibration_table(predictions: pd.DataFrame) -> pd.DataFrame:
    edges = np.linspace(0.0, 1.0, 11)
    rows: list[dict[str, object]] = []
    for (target, model), group in predictions.groupby(
        ["target", "model"], sort=True
    ):
        bins = pd.cut(
            group["probability"],
            bins=edges,
            include_lowest=True,
            right=True,
        )
        for interval, sample in group.groupby(bins, observed=True):
            if sample.empty:
                continue
            rows.append(
                {
                    "target": target,
                    "model": model,
                    "probability_bin": str(interval),
                    "bin_left": float(interval.left),
                    "bin_right": float(interval.right),
                    "n": len(sample),
                    "mean_predicted_probability": float(
                        sample["probability"].mean()
                    ),
                    "observed_event_rate": float(sample["label"].mean()),
                    "calibration_gap": float(
                        sample["probability"].mean() - sample["label"].mean()
                    ),
                }
            )
    return pd.DataFrame(rows)


def build_current_risk_snapshot(
    frame: pd.DataFrame,
    targets: Sequence[str],
) -> pd.DataFrame:
    working = frame.copy()
    working["_position"] = np.arange(len(working))
    current_position = int(working["_position"].max())
    current = working.iloc[-1]
    cutoff_position = current_position - MODEL_EMBARGO_DAYS
    rows: list[dict[str, object]] = []
    for target in targets:
        for model_name, features in MODEL_FEATURES.items():
            train = working[
                working[target].notna()
                & working["_position"].lt(cutoff_position)
                & ~working["long_break_eve"]
            ]
            if len(train) < 500 or train[target].nunique() < 2:
                continue
            pipeline = make_logistic_pipeline(features)
            pipeline.fit(train[list(features)], train[target].astype(int))
            train_probability = pipeline.predict_proba(
                train[list(features)]
            )[:, 1]
            threshold = float(np.quantile(train_probability, 0.90))
            probability = float(
                pipeline.predict_proba(
                    working.loc[[current.name], list(features)]
                )[0, 1]
            )
            rows.append(
                {
                    "as_of_date": current["date"],
                    "signal_available": "after T close when DFCF T margin is published",
                    "first_executable_session": "T+1",
                    "target": target,
                    "model": model_name,
                    "probability": probability,
                    "training_probability_q90": threshold,
                    "risk_flag": int(probability >= threshold),
                    "training_rows": len(train),
                    "training_events": int(train[target].astype(int).sum()),
                    "training_end_date": train["date"].max(),
                    "training_end_position": int(train["_position"].max()),
                    "snapshot_position": current_position,
                    "embargo_days": MODEL_EMBARGO_DAYS,
                    "crowding_intensity_score": current.get(
                        "crowding_intensity_score"
                    ),
                    "micro_margin_risk_score": current.get(
                        "micro_margin_risk_score"
                    ),
                    "aggregate_margin_risk_score": current.get(
                        "aggregate_margin_risk_score"
                    ),
                    "trend_regime": current.get("trend_regime"),
                    "individual_flow_valid": current.get(
                        "individual_flow_valid"
                    ),
                    "crowd_margin_coverage": current.get(
                        "crowd_margin_coverage"
                    ),
                    "crowd_margin_continuity_coverage": current.get(
                        "crowd_margin_continuity_coverage"
                    ),
                    "crowd_financing_eligibility_share_pct": current.get(
                        "crowd_financing_eligibility_share_pct"
                    ),
                    "current_feature_missing_count": int(
                        working.loc[current.name, list(features)].isna().sum()
                    ),
                    "current_feature_count": len(features),
                }
            )
    return pd.DataFrame(rows)


def block_bootstrap_model_delta(
    predictions: pd.DataFrame,
    target: str,
    model_a: str,
    model_b: str,
    block_size: int = 20,
    repetitions: int = 500,
    seed: int = 42,
) -> dict[str, object]:
    left = predictions[
        (predictions["target"] == target) & (predictions["model"] == model_a)
    ][["date", "label", "probability"]].rename(columns={"probability": "probability_a"})
    right = predictions[
        (predictions["target"] == target) & (predictions["model"] == model_b)
    ][["date", "label", "probability"]].rename(columns={"probability": "probability_b"})
    merged = left.merge(right, on=["date", "label"], how="inner").sort_values("date")
    if len(merged) < 100 or merged["label"].nunique() < 2:
        return {
            "target": target,
            "model_a": model_a,
            "model_b": model_b,
            "n": len(merged),
            "available": False,
        }

    labels = merged["label"].to_numpy(dtype=int)
    prob_a = merged["probability_a"].to_numpy(dtype=float)
    prob_b = merged["probability_b"].to_numpy(dtype=float)
    point_ap_delta = float(
        average_precision_score(labels, prob_b)
        - average_precision_score(labels, prob_a)
    )
    point_brier_improvement = float(
        brier_score_loss(labels, prob_a) - brier_score_loss(labels, prob_b)
    )

    rng = np.random.default_rng(seed)
    starts = np.arange(0, len(merged), block_size)
    ap_deltas = []
    brier_improvements = []
    for _ in range(repetitions):
        selected = rng.choice(starts, size=len(starts), replace=True)
        indices = np.concatenate(
            [np.arange(start, min(start + block_size, len(merged))) for start in selected]
        )[: len(merged)]
        sample_labels = labels[indices]
        if len(np.unique(sample_labels)) < 2:
            continue
        sample_a = prob_a[indices]
        sample_b = prob_b[indices]
        ap_deltas.append(
            average_precision_score(sample_labels, sample_b)
            - average_precision_score(sample_labels, sample_a)
        )
        brier_improvements.append(
            brier_score_loss(sample_labels, sample_a)
            - brier_score_loss(sample_labels, sample_b)
        )

    return {
        "target": target,
        "model_a": model_a,
        "model_b": model_b,
        "n": len(merged),
        "available": bool(ap_deltas),
        "average_precision_delta": point_ap_delta,
        "average_precision_delta_ci95": (
            [float(value) for value in np.quantile(ap_deltas, [0.025, 0.975])]
            if ap_deltas
            else None
        ),
        "brier_improvement": point_brier_improvement,
        "brier_improvement_ci95": (
            [
                float(value)
                for value in np.quantile(brier_improvements, [0.025, 0.975])
            ]
            if brier_improvements
            else None
        ),
        "bootstrap_repetitions_used": len(ap_deltas),
        "block_size": block_size,
    }


def build_risk_group_analysis(frame: pd.DataFrame) -> pd.DataFrame:
    target = "target_crowd_drawdown_20d"
    valid = frame[
        frame["date"].ge(MODEL_START_DATE)
        & frame[target].notna()
        & ~frame["long_break_eve"]
        & frame["crowding_intensity_score"].notna()
        & frame["micro_margin_risk_score"].notna()
        & frame["aggregate_margin_risk_score"].notna()
    ].copy()
    if valid.empty:
        return pd.DataFrame()

    conditions = {
        "all_valid_days": pd.Series(True, index=valid.index),
        "crowding_top20pct": valid["crowding_intensity_score"].ge(0.80),
        "micro_risk_top20pct": valid["micro_margin_risk_score"].ge(0.80),
        "aggregate_risk_top20pct": valid["aggregate_margin_risk_score"].ge(0.80),
        "crowding_and_micro_top20pct": valid["crowding_intensity_score"].ge(0.80)
        & valid["micro_margin_risk_score"].ge(0.80),
        "crowding_and_aggregate_top20pct": valid["crowding_intensity_score"].ge(0.80)
        & valid["aggregate_margin_risk_score"].ge(0.80),
        "crowding_micro_and_downtrend": valid["crowding_intensity_score"].ge(0.80)
        & valid["micro_margin_risk_score"].ge(0.80)
        & valid["trend_downtrend"].eq(1.0),
        "crowding_micro_and_uptrend": valid["crowding_intensity_score"].ge(0.80)
        & valid["micro_margin_risk_score"].ge(0.80)
        & valid["trend_uptrend"].eq(1.0),
    }
    base_rate = float(valid[target].astype(int).mean())
    rows = []
    for name, mask in conditions.items():
        sample = valid.loc[mask]
        event_rate = (
            float(sample[target].astype(int).mean()) if len(sample) else math.nan
        )
        rows.append(
            {
                "group": name,
                "n": len(sample),
                "events": int(sample[target].astype(int).sum()) if len(sample) else 0,
                "event_rate": event_rate,
                "base_event_rate": base_rate,
                "risk_ratio": event_rate / base_rate if base_rate and np.isfinite(event_rate) else math.nan,
                "median_future_mdd_20d_pct": (
                    float(sample["crowd_future_mdd_20d_pct"].median())
                    if len(sample)
                    else math.nan
                ),
            }
        )

    valid["micro_risk_decile"] = pd.cut(
        valid["micro_margin_risk_score"],
        bins=np.linspace(0.0, 1.0, 11),
        labels=range(1, 11),
        include_lowest=True,
    )
    for decile, sample in valid.groupby("micro_risk_decile", observed=True):
        rows.append(
            {
                "group": f"micro_risk_decile_{int(decile)}",
                "n": len(sample),
                "events": int(sample[target].astype(int).sum()),
                "event_rate": float(sample[target].astype(int).mean()),
                "base_event_rate": base_rate,
                "risk_ratio": float(sample[target].astype(int).mean()) / base_rate,
                "median_future_mdd_20d_pct": float(
                    sample["crowd_future_mdd_20d_pct"].median()
                ),
            }
        )
    return pd.DataFrame(rows)


def build_event_table(
    frame: pd.DataFrame,
    predictions: pd.DataFrame,
    event_kind: str,
    event_positions: Sequence[int],
) -> pd.DataFrame:
    top_target = (
        "target_crowd_top_within_10d"
        if event_kind == "crowd"
        else "target_market_top_within_10d"
    )
    drawdown_target = (
        "target_crowd_drawdown_20d"
        if event_kind == "crowd"
        else "target_market_drawdown_20d"
    )
    top_predictions = predictions[
        (predictions["target"] == top_target)
        & (predictions["model"] == "individual_plus_regime")
    ].set_index("date")
    drawdown_predictions = predictions[
        (predictions["target"] == drawdown_target)
        & (predictions["model"] == "individual_plus_regime")
    ].set_index("date")
    rows = []
    for position in event_positions:
        if position < 0 or position >= len(frame):
            continue
        event_row = frame.iloc[position]
        if event_row["date"] < MODEL_START_DATE:
            continue
        prior = frame.iloc[max(0, position - 10) : position]
        prior_predictions = top_predictions.reindex(prior["date"]).dropna(
            subset=["probability"]
        )
        flagged = prior_predictions[prior_predictions["risk_flag"].eq(1)]
        first_flag_date = flagged.index.min() if not flagged.empty else pd.NaT
        lead_days = (
            position - int(frame.index[frame["date"].eq(first_flag_date)][0])
            if pd.notna(first_flag_date)
            else math.nan
        )
        risk_values = {}
        for lag in (20, 10, 5, 0):
            lag_position = position - lag
            if lag_position < 0:
                continue
            lag_date = frame.iloc[lag_position]["date"]
            top_probability = (
                top_predictions.loc[lag_date, "probability"]
                if lag_date in top_predictions.index
                else math.nan
            )
            drawdown_probability = (
                drawdown_predictions.loc[lag_date, "probability"]
                if lag_date in drawdown_predictions.index
                else math.nan
            )
            if isinstance(top_probability, pd.Series):
                top_probability = top_probability.iloc[-1]
            if isinstance(drawdown_probability, pd.Series):
                drawdown_probability = drawdown_probability.iloc[-1]
            risk_values[f"top_probability_T_minus_{lag}"] = top_probability
            risk_values[
                f"drawdown_probability_T_minus_{lag}"
            ] = drawdown_probability
            risk_values[f"micro_risk_T_minus_{lag}"] = frame.iloc[lag_position][
                "micro_margin_risk_score"
            ]
            risk_values[f"aggregate_risk_T_minus_{lag}"] = frame.iloc[lag_position][
                "aggregate_margin_risk_score"
            ]
        rows.append(
            {
                "event_kind": event_kind,
                "event_date": event_row["date"],
                "top_prediction_target": top_target,
                "drawdown_prediction_target": drawdown_target,
                "first_model_flag_date_prior10": first_flag_date,
                "model_flag_lead_trading_days": lead_days,
                "crowd_future_mdd_20d_pct": event_row["crowd_future_mdd_20d_pct"],
                "market_future_mdd_20d_pct": event_row["market_future_mdd_20d_pct"],
                "crowding_intensity_score": event_row["crowding_intensity_score"],
                "micro_margin_risk_score": event_row["micro_margin_risk_score"],
                "aggregate_margin_risk_score": event_row["aggregate_margin_risk_score"],
                **risk_values,
            }
        )
    return pd.DataFrame(rows)


def build_event_membership_table(
    frame: pd.DataFrame,
    crowd_event_positions: Sequence[int],
    market_event_positions: Sequence[int],
    event_window: int = 20,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for event_kind, positions in (
        ("crowd", crowd_event_positions),
        ("market", market_event_positions),
    ):
        for event_position in positions:
            event_date = frame.iloc[event_position]["date"]
            for position in range(
                max(0, event_position - event_window),
                min(len(frame), event_position + event_window + 1),
            ):
                row = frame.iloc[position]
                rows.append(
                    {
                        "event_kind": event_kind,
                        "event_date": event_date,
                        "date": row["date"],
                        "relative_trading_day": position - event_position,
                        "crowd_count": row["crowd_count"],
                        "crowd_member_codes": row["crowd_member_codes"],
                        "crowd_top_margin_codes": row["crowd_top_margin_codes"],
                        "crowd_margin_coverage": row["crowd_margin_coverage"],
                        "crowd_margin_continuity_coverage": row[
                            "crowd_margin_continuity_coverage"
                        ],
                        "crowd_financing_eligibility_share_pct": row[
                            "crowd_financing_eligibility_share_pct"
                        ],
                        "crowd_strategy_return_pct": row[
                            "crowd_strategy_return_pct"
                        ],
                        "crowd_margin_flow_pct": row["crowd_margin_flow_pct"],
                        "crowd_transaction_net_pct": row[
                            "crowd_transaction_net_pct"
                        ],
                        "crowd_outflow_breadth_pct": row[
                            "crowd_outflow_breadth_pct"
                        ],
                    }
                )
    return pd.DataFrame(rows)


def summarize_parameter_panel(
    frame: pd.DataFrame,
    candidate_quantile: float,
    persistence_min_hits: int,
) -> dict[str, object]:
    valid = frame[
        frame["date"].ge(MODEL_START_DATE)
        & frame["target_crowd_drawdown_20d"].notna()
        & ~frame["long_break_eve"]
    ]
    score_valid = valid[
        valid["crowding_intensity_score"].notna()
        & valid["micro_margin_risk_score"].notna()
    ]
    high_risk = score_valid[
        score_valid["crowding_intensity_score"].ge(0.80)
        & score_valid["micro_margin_risk_score"].ge(0.80)
    ]
    base_rate = (
        float(score_valid["target_crowd_drawdown_20d"].astype(int).mean())
        if len(score_valid)
        else math.nan
    )
    high_rate = (
        float(high_risk["target_crowd_drawdown_20d"].astype(int).mean())
        if len(high_risk)
        else math.nan
    )
    return {
        "candidate_quantile": candidate_quantile,
        "persistence_min_hits": persistence_min_hits,
        "valid_days": len(valid),
        "score_valid_days": len(score_valid),
        "median_crowd_count": (
            float(valid["crowd_count"].median()) if len(valid) else math.nan
        ),
        "crowd_peak_events": len(frame.attrs.get("crowd_event_positions", [])),
        "market_peak_events": len(frame.attrs.get("market_event_positions", [])),
        "base_drawdown_event_rate": base_rate,
        "high_crowding_micro_risk_days": len(high_risk),
        "high_crowding_micro_drawdown_event_rate": high_rate,
        "high_crowding_micro_risk_ratio": (
            high_rate / base_rate
            if np.isfinite(high_rate) and np.isfinite(base_rate) and base_rate > 0
            else math.nan
        ),
        "median_future_crowd_mdd_20d_pct": (
            float(valid["crowd_future_mdd_20d_pct"].median())
            if len(valid)
            else math.nan
        ),
    }


def build_coverage_sensitivity(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for coverage in (0.70, 0.80, 0.90):
        valid = margin_flow_validity(frame, coverage)
        analysis = frame[
            frame["date"].ge(MODEL_START_DATE)
            & frame["target_crowd_drawdown_20d"].notna()
            & ~frame["long_break_eve"]
            & valid
        ]
        rows.append(
            {
                "sensitivity_type": "margin_member_coverage",
                "coverage_threshold": coverage,
                "valid_days": len(analysis),
                "valid_day_share": (
                    float(
                        valid[
                            frame["date"].ge(MODEL_START_DATE)
                            & frame["target_crowd_drawdown_20d"].notna()
                            & ~frame["long_break_eve"]
                        ].mean()
                    )
                    if len(frame)
                    else math.nan
                ),
                "drawdown_event_rate": (
                    float(
                        analysis["target_crowd_drawdown_20d"].astype(int).mean()
                    )
                    if len(analysis)
                    else math.nan
                ),
                "median_financing_eligibility_share_pct": (
                    float(
                        analysis[
                            "crowd_financing_eligibility_share_pct"
                        ].median()
                    )
                    if len(analysis)
                    else math.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def pooled_metric_lookup(
    metric_frame: pd.DataFrame,
    target: str,
    model: str,
) -> dict[str, object]:
    row = metric_frame[
        (metric_frame["scope"] == "pooled_oos")
        & (metric_frame["target"] == target)
        & (metric_frame["model"] == model)
    ]
    return row.iloc[0].to_dict() if not row.empty else {}


def write_report(
    output_path: Path,
    metadata: dict[str, object],
    metrics: pd.DataFrame,
    risk_groups: pd.DataFrame,
    event_table: pd.DataFrame,
    bootstrap_results: list[dict[str, object]],
    current_snapshot: pd.DataFrame,
    parameter_sensitivity: pd.DataFrame,
) -> None:
    def format_number(value: object, specification: str) -> str:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return "N/A"
        return format(numeric, specification) if np.isfinite(numeric) else "N/A"

    target = "target_crowd_drawdown_20d"
    price = pooled_metric_lookup(metrics, target, "price_only")
    aggregate = pooled_metric_lookup(metrics, target, "price_plus_aggregate")
    individual = pooled_metric_lookup(
        metrics, target, "price_plus_aggregate_plus_individual"
    )
    regime = pooled_metric_lookup(metrics, target, "individual_plus_regime")
    top_timing = pooled_metric_lookup(
        metrics, "target_crowd_top_within_10d", "individual_plus_regime"
    )
    group_lookup = (
        risk_groups.set_index("group").to_dict("index") if not risk_groups.empty else {}
    )
    lines = [
        "# A股抱团、个股融资与顶部风险研究",
        "",
        f"- 生成时间：{metadata['generated_at']}",
        f"- 个股融资与价格样本：{metadata['panel_start']} 至 {metadata['panel_end']}",
        f"- 样本外预测：2019-01-01 起，按自然年扩展窗口，测试前隔离 {MODEL_EMBARGO_DAYS} 个交易日",
        "- 信号时点：T日收盘后；第一可执行时点为T+1，任何T日收盘收益均不作为可执行收益",
        "- 结论性质：厂商数据上的历史条件统计，不证明融资流出由强平造成，也不构成投资建议",
        "",
        "## 模型定义",
        "",
        "- 动态抱团：过去120个有效观测的相对强势前10%，且过去20日中至少12次进入强势组；T日组合只影响T+1收益。",
        "- 主要结果变量：以T日收盘为基准，未来20个交易日最低收盘跌幅是否达到8%（不是路径峰谷最大回撤）；顶部时点模型预测T+1至T+10是否出现事后确认的顶部。",
        "- 对照模型依次加入：价格拥挤、两市总融资、逐股融资、市场环境交互。",
        "",
        "## 样本外结果",
        "",
        "| 模型 | ROC-AUC | PR-AUC | Brier | 风险标记命中率 | 风险提升倍数 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, values in [
        ("仅价格拥挤", price),
        ("价格＋总融资", aggregate),
        ("价格＋总融资＋个股融资", individual),
        ("个股融资＋市场环境", regime),
    ]:
        lines.append(
            "| {name} | {roc} | {ap} | {brier} | {precision} | {lift} |".format(
                name=name,
                roc=format_number(values.get("roc_auc"), ".3f"),
                ap=format_number(values.get("average_precision"), ".3f"),
                brier=format_number(values.get("brier"), ".3f"),
                precision=format_number(values.get("flag_precision"), ".1%"),
                lift=format_number(values.get("risk_lift"), ".2f"),
            )
        )

    lines.extend(["", "## 条件风险", ""])
    for group_name, label in [
        ("all_valid_days", "全部有效日"),
        ("crowding_top20pct", "拥挤度最高20%的日期"),
        ("crowding_and_micro_top20pct", "高拥挤＋个股融资风险最高20%"),
        ("crowding_and_aggregate_top20pct", "高拥挤＋总融资风险最高20%"),
        ("crowding_micro_and_downtrend", "高拥挤＋个股融资风险＋下降趋势"),
        ("crowding_micro_and_uptrend", "高拥挤＋个股融资风险＋上升趋势"),
    ]:
        values = group_lookup.get(group_name)
        if values:
            lines.append(
                f"- {label}：N={values['n']}，未来20日回撤≥8%的比例"
                f" {values['event_rate']:.1%}，相对基准 {values['risk_ratio']:.2f} 倍。"
            )

    lines.extend(["", "## 顶部时点与当前风险", ""])
    if top_timing:
        lines.append(
            "- 抱团顶部T+1至T+10样本外模型："
            f"ROC-AUC={format_number(top_timing.get('roc_auc'), '.3f')}，"
            f"PR-AUC={format_number(top_timing.get('average_precision'), '.3f')}，"
            f"Brier={format_number(top_timing.get('brier'), '.3f')}。"
        )
    if current_snapshot.empty:
        lines.append("- 当前快照不可用。")
    else:
        latest = current_snapshot[
            current_snapshot["model"].eq("individual_plus_regime")
        ].sort_values("target")
        for _, row in latest.iterrows():
            lines.append(
                f"- {row['as_of_date']:%Y-%m-%d} {row['target']}："
                f"历史风险概率/评分 {row['probability']:.1%}，"
                f"训练期90%阈值 {row['training_probability_q90']:.1%}，"
                f"风险标记={int(row['risk_flag'])}，趋势={row['trend_regime']}。"
            )

    lines.extend(["", "## 参数稳健性", ""])
    if parameter_sensitivity.empty:
        lines.append("- 参数敏感性结果不可用。")
    else:
        for _, row in parameter_sensitivity.iterrows():
            lines.append(
                f"- 强势分位{row['candidate_quantile']:.0%}/"
                f"20日命中{int(row['persistence_min_hits'])}次："
                f"抱团数中位数{row['median_crowd_count']:.0f}，"
                f"高拥挤＋高微观融资风险样本N={int(row['high_crowding_micro_risk_days'])}，"
                f"20日最低收盘跌幅事件率{row['high_crowding_micro_drawdown_event_rate']:.1%}，"
                f"相对基准{row['high_crowding_micro_risk_ratio']:.2f}倍。"
            )

    lines.extend(["", "## 个股数据增量检验", ""])
    for result in bootstrap_results:
        if not result.get("available"):
            continue
        ap_ci = result.get("average_precision_delta_ci95")
        brier_ci = result.get("brier_improvement_ci95")
        lines.append(
            "- {target}：加入个股融资后PR-AUC变化 {ap:+.4f}"
            "（20日块自助法95%区间 {ap_low:+.4f} 至 {ap_high:+.4f}）；"
            "Brier改善 {brier:+.4f}（区间 {b_low:+.4f} 至 {b_high:+.4f}）。".format(
                target=result["target"],
                ap=result["average_precision_delta"],
                ap_low=ap_ci[0],
                ap_high=ap_ci[1],
                brier=result["brier_improvement"],
                b_low=brier_ci[0],
                b_high=brier_ci[1],
            )
        )

    lines.extend(["", "## 历史顶部事件", ""])
    if event_table.empty:
        lines.append("- 样本外区间未识别到满足固定阈值的去重顶部事件。")
    else:
        for _, row in event_table.sort_values(["event_kind", "event_date"]).iterrows():
            lead = (
                f"{int(row['model_flag_lead_trading_days'])}个交易日"
                if pd.notna(row["model_flag_lead_trading_days"])
                else "未提前触发"
            )
            lines.append(
                f"- {row['event_kind']} {row['event_date']:%Y-%m-%d}："
                f"未来20日抱团最大回撤 {row['crowd_future_mdd_20d_pct']:.2f}%，"
                f"市场最大回撤 {row['market_future_mdd_20d_pct']:.2f}%，"
                f"模型提前量 {lead}。"
            )

    lines.extend(
        [
            "",
            "## 证据边界",
            "",
            "- 东方财富逐股明细与市场汇总不能精确核平；逐股库只用于横截面和组内变化，总融资因子只读取独立汇总表。",
            "- 股票进入或退出明细库不会被当成普通融资流入/流出；个股变化仅在连续交易日同时存在时计算。",
            "- 动态抱团先在本地保存的全部沪深A股价格文件中识别，再与个股融资库相交计算融资指标；历史退市文件是否完整保留无法由本地目录自行证明。",
            "- 逐股融资因子只描述T−1时已具融资记录的抱团子集；80%门槛是该子集在T日仍具连续记录的完整率，不是要求80%的全部抱团股都具备融资资格。融资资格子集占全部抱团的比例必须另列。",
            "- TDX未复权价格按当日已发生的gbbq权益事件做因果近似；特殊除权和差异化分红仍可能存在小误差。",
            "- 顶部事件和未来最大回撤是事后标签；所有模型特征、标准化、阈值和训练样本严格止于预测日。",
            "- 日度标签高度重叠，模型优劣必须结合20日块自助区间和去重事件，而不能只看单一胜率。",
        ]
    )
    atomic_write_text(output_path, "\n".join(lines) + "\n")


def run_study(config: StudyConfig) -> dict[str, object]:
    output_dir = validate_output_dir(config.output_dir)
    config = replace(config, output_dir=output_dir)
    for path in (
        config.db_path,
        config.aggregate_margin_csv,
        config.aggregate_audit_json,
        config.index_day_path,
        config.ht_root,
        config.market_snapshot_manifest,
        config.gbbq_path,
        config.gbbq_reader_path,
        config.individual_audit_json,
    ):
        if not path.exists():
            raise FileNotFoundError(path)

    full_aggregate = load_aggregate_margin(config.aggregate_margin_csv)
    full_index_frame = read_tdx_day(config.index_day_path)
    input_audit = validate_input_audits(
        config, full_aggregate, full_index_frame
    )
    aggregate = full_aggregate
    if config.end_date:
        aggregate = aggregate[aggregate["date"].le(pd.Timestamp(config.end_date))]
    aggregate = aggregate[aggregate["date"].ge(pd.Timestamp(config.start_date))]
    if aggregate.empty:
        raise ValueError("Aggregate margin data are empty for the requested dates")
    individual_audit = input_audit["individual_audit"]
    warmup_start = aggregate["date"].min() - pd.Timedelta(days=550)
    index_frame = full_index_frame[
        full_index_frame["date"].between(warmup_start, aggregate["date"].max())
    ]
    print("Loading causal TDX corporate actions...", flush=True)
    corporate_actions, corporate_action_audit = load_causal_corporate_actions(
        config.gbbq_path,
        config.gbbq_reader_path,
        aggregate["date"].max(),
    )
    print("Loading full local SH/SZ price history...", flush=True)
    price_rows_by_date, price_audit, price_relevant_hashes = load_tdx_market_rows(
        config.ht_root,
        warmup_start,
        aggregate["date"].max(),
        corporate_actions,
    )
    print("Building primary dynamic-crowd and financing panel...", flush=True)
    micro_panel, micro_audit = build_daily_micro_panel(
        config,
        aggregate,
        index_frame,
        price_rows_by_date,
    )
    factor_panel = add_derived_features(micro_panel, aggregate, index_frame)
    crowd_events = list(factor_panel.attrs.get("crowd_event_positions", []))
    market_events = list(factor_panel.attrs.get("market_event_positions", []))

    print("Running annual expanding-window out-of-sample models...", flush=True)
    predictions, metrics, coefficients = walk_forward_models(
        factor_panel, MODEL_TARGETS
    )
    calibration = build_calibration_table(predictions)
    current_snapshot = build_current_risk_snapshot(
        factor_panel, MODEL_TARGETS
    )
    risk_groups = build_risk_group_analysis(factor_panel)
    crowd_event_table = build_event_table(
        factor_panel, predictions, "crowd", crowd_events
    )
    market_event_table = build_event_table(
        factor_panel, predictions, "market", market_events
    )
    event_table = pd.concat(
        [crowd_event_table, market_event_table], ignore_index=True
    )
    event_membership = build_event_membership_table(
        factor_panel, crowd_events, market_events
    )

    bootstrap_results = [
        block_bootstrap_model_delta(
            predictions,
            target,
            "price_plus_aggregate",
            "price_plus_aggregate_plus_individual",
        )
        for target in MODEL_TARGETS
    ]
    bootstrap_results.extend(
        [
            block_bootstrap_model_delta(
                predictions,
                target,
                "price_plus_aggregate_plus_individual",
                "individual_plus_regime",
            )
            for target in MODEL_TARGETS
        ]
    )

    print("Running pre-registered crowd-definition sensitivity panels...", flush=True)
    parameter_rows = [
        summarize_parameter_panel(
            factor_panel,
            config.candidate_quantile,
            config.persistence_min_hits,
        )
    ]
    for candidate_quantile, persistence_min_hits in (
        (0.85, 10),
        (0.95, 14),
    ):
        sensitivity_config = replace(
            config,
            candidate_quantile=candidate_quantile,
            persistence_min_hits=persistence_min_hits,
        )
        sensitivity_micro, _ = build_daily_micro_panel(
            sensitivity_config,
            aggregate,
            index_frame,
            price_rows_by_date,
        )
        sensitivity_panel = add_derived_features(
            sensitivity_micro, aggregate, index_frame
        )
        parameter_rows.append(
            summarize_parameter_panel(
                sensitivity_panel,
                candidate_quantile,
                persistence_min_hits,
            )
        )
        del sensitivity_micro, sensitivity_panel
    parameter_sensitivity = pd.DataFrame(parameter_rows).sort_values(
        ["candidate_quantile", "persistence_min_hits"]
    )
    coverage_sensitivity = build_coverage_sensitivity(factor_panel)

    verify_tdx_relevant_prefixes(
        price_relevant_hashes, aggregate["date"].max()
    )
    input_audit["input_hashes"]["index_day_file_after"] = sha256_file(
        config.index_day_path
    )
    input_audit["input_hashes"]["gbbq_file_after"] = sha256_file(
        config.gbbq_path
    )
    input_audit["input_hashes"]["gbbq_reader_after"] = sha256_file(
        config.gbbq_reader_path
    )
    if (
        input_audit["input_hashes"]["index_day_file_before"]
        != input_audit["input_hashes"]["index_day_file_after"]
    ):
        raise RuntimeError("TDX index file changed while the study was running")
    if (
        corporate_action_audit["gbbq_sha256"]
        != input_audit["input_hashes"]["gbbq_file_after"]
    ):
        raise RuntimeError("TDX gbbq file changed while the study was running")
    if (
        corporate_action_audit["reader_sha256"]
        != input_audit["input_hashes"]["gbbq_reader_after"]
    ):
        raise RuntimeError("TDX gbbq reader changed while the study was running")
    end_hashes = {
        "individual_margin_sqlite": sha256_file(config.db_path),
        "individual_margin_audit_json": sha256_file(
            config.individual_audit_json
        ),
        "aggregate_margin_csv": sha256_file(config.aggregate_margin_csv),
        "aggregate_margin_audit_json": sha256_file(
            config.aggregate_audit_json
        ),
        "analysis_script": sha256_file(Path(__file__).resolve()),
        "market_snapshot_manifest": sha256_file(
            config.market_snapshot_manifest
        ),
    }
    for name, end_hash in end_hashes.items():
        if input_audit["input_hashes"][name] != end_hash:
            raise RuntimeError(f"Input changed while the study was running: {name}")
        input_audit["input_hashes"][f"{name}_after"] = end_hash
    wal_path = Path(f"{config.db_path}-wal")
    if wal_path.exists() and wal_path.stat().st_size != 0:
        raise RuntimeError("Individual-margin SQLite WAL changed during the study")

    metadata = {
        "study_name": STUDY_NAME,
        "generated_at": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(),
        "config": asdict(config),
        "panel_start": factor_panel["date"].min(),
        "panel_end": factor_panel["date"].max(),
        "panel_dates": len(factor_panel),
        "model_start": MODEL_START_DATE,
        "individual_source_status": individual_audit.get("sample_status"),
        "individual_database_rows": individual_audit.get("database_rows"),
        "individual_database_dates": individual_audit.get("database_dates"),
        "individual_vendor_no_data_dates": individual_audit.get(
            "vendor_no_data_dates", []
        ),
        "individual_calendar_coverage_complete": individual_audit.get(
            "calendar_coverage_complete"
        ),
        "aggregate_reconciliation_exact": individual_audit.get(
            "aggregate_reconciliation", {}
        ).get("exact_reconciliation_passed"),
        "input_audit_summary": {
            key: value
            for key, value in input_audit.items()
            if key not in {"individual_audit", "aggregate_audit"}
        },
        "price_audit": price_audit,
        "corporate_action_audit": corporate_action_audit,
        "micro_panel_audit": micro_audit,
        "crowd_event_dates": [
            factor_panel.iloc[position]["date"] for position in crowd_events
        ],
        "market_event_dates": [
            factor_panel.iloc[position]["date"] for position in market_events
        ],
        "targets": {
            "primary": (
                "future 20-trading-day worst close return from T close for the "
                "one-day-lagged dynamic crowd portfolio <= -8%; this is not "
                "path peak-to-trough maximum drawdown"
            ),
            "secondary": (
                "future 20-trading-day worst close return from T close for "
                "Shenzhen Composite <= -8%"
            ),
            "timing": (
                "whether a retrospectively confirmed crowd/market peak occurs "
                "strictly within T+1 through T+10"
            ),
        },
        "signal_availability": (
            "Features dated T are complete only after DFCF publishes T margin data; "
            "first executable session is T+1."
        ),
        "input_hashes": input_audit["input_hashes"],
        "bootstrap_model_deltas": bootstrap_results,
        "parameter_sensitivity": parameter_sensitivity.to_dict("records"),
        "coverage_sensitivity": coverage_sensitivity.to_dict("records"),
    }

    config.output_dir.mkdir(parents=True, exist_ok=True)
    completion_manifest_path = config.output_dir / "_RUN_COMPLETE.json"
    if completion_manifest_path.exists():
        completion_manifest_path.unlink()
    label_columns = [
        "date",
        "crowd_strategy_return_valid",
        "crowd_future_mdd_5d_pct",
        "crowd_future_mdd_10d_pct",
        "crowd_future_mdd_20d_pct",
        "crowd_future_mdd_40d_pct",
        "market_future_mdd_5d_pct",
        "market_future_mdd_10d_pct",
        "market_future_mdd_20d_pct",
        "market_future_mdd_40d_pct",
        "target_crowd_drawdown_20d",
        "target_market_drawdown_20d",
        "target_crowd_top_within_5d",
        "target_crowd_top_within_10d",
        "target_crowd_top_within_20d",
        "target_market_top_within_5d",
        "target_market_top_within_10d",
        "target_market_top_within_20d",
    ]
    atomic_write_csv(
        factor_panel, config.output_dir / "daily_factor_panel.csv"
    )
    atomic_write_csv(
        factor_panel[label_columns],
        config.output_dir / "top_event_labels.csv",
    )
    atomic_write_csv(
        predictions, config.output_dir / "oos_model_predictions.csv"
    )
    atomic_write_csv(
        metrics, config.output_dir / "model_performance.csv"
    )
    atomic_write_csv(
        coefficients, config.output_dir / "model_coefficients.csv"
    )
    atomic_write_csv(
        calibration, config.output_dir / "probability_calibration.csv"
    )
    atomic_write_csv(
        current_snapshot, config.output_dir / "current_risk_snapshot.csv"
    )
    atomic_write_csv(
        risk_groups, config.output_dir / "risk_group_analysis.csv"
    )
    atomic_write_csv(
        event_table, config.output_dir / "top_event_study.csv"
    )
    atomic_write_csv(
        event_membership,
        config.output_dir / "crowd_membership_event_days.csv",
    )
    atomic_write_csv(
        parameter_sensitivity,
        config.output_dir / "parameter_sensitivity.csv",
    )
    atomic_write_csv(
        coverage_sensitivity,
        config.output_dir / "coverage_sensitivity.csv",
    )
    atomic_write_text(
        config.output_dir / "input_audit.json",
        json.dumps(jsonable(input_audit), ensure_ascii=False, indent=2),
    )
    atomic_write_text(
        config.output_dir / "current_risk_snapshot.json",
        json.dumps(
            jsonable(current_snapshot.to_dict("records")),
            ensure_ascii=False,
            indent=2,
        ),
    )
    report_path = config.output_dir / "RESEARCH_REPORT.md"
    write_report(
        report_path,
        metadata,
        metrics,
        risk_groups,
        event_table,
        bootstrap_results,
        current_snapshot,
        parameter_sensitivity,
    )
    results = {
        "metadata": metadata,
        "pooled_oos_metrics": metrics[metrics["scope"].eq("pooled_oos")].to_dict(
            "records"
        ),
        "risk_groups": risk_groups.to_dict("records"),
        "top_events": event_table.to_dict("records"),
        "current_risk_snapshot": current_snapshot.to_dict("records"),
        "parameter_sensitivity": parameter_sensitivity.to_dict("records"),
        "coverage_sensitivity": coverage_sensitivity.to_dict("records"),
        "bootstrap_model_deltas": bootstrap_results,
        "output_files": {
            "daily_factor_panel": "daily_factor_panel.csv",
            "top_event_labels": "top_event_labels.csv",
            "oos_predictions": "oos_model_predictions.csv",
            "model_performance": "model_performance.csv",
            "model_coefficients": "model_coefficients.csv",
            "probability_calibration": "probability_calibration.csv",
            "current_risk_snapshot_csv": "current_risk_snapshot.csv",
            "current_risk_snapshot_json": "current_risk_snapshot.json",
            "risk_group_analysis": "risk_group_analysis.csv",
            "top_event_study": "top_event_study.csv",
            "crowd_membership_event_days": "crowd_membership_event_days.csv",
            "parameter_sensitivity": "parameter_sensitivity.csv",
            "coverage_sensitivity": "coverage_sensitivity.csv",
            "input_audit": "input_audit.json",
            "research_report": "RESEARCH_REPORT.md",
        },
    }
    atomic_write_text(
        config.output_dir / "research_results.json",
        json.dumps(jsonable(results), ensure_ascii=False, indent=2),
    )
    published_files = sorted(
        path
        for path in config.output_dir.iterdir()
        if path.is_file() and path.name != completion_manifest_path.name
    )
    completion_manifest = {
        "study_name": STUDY_NAME,
        "status": "complete",
        "generated_at": metadata["generated_at"],
        "files": {
            path.name: {
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in published_files
        },
    }
    atomic_write_text(
        completion_manifest_path,
        json.dumps(jsonable(completion_manifest), ensure_ascii=False, indent=2),
    )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze dynamic A-share crowding and stock-level margin-flow top risk"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(r"D:\vcp_hunter\产业链投研"),
    )
    parser.add_argument("--start-date", default="2016-01-01")
    parser.add_argument("--end-date")
    parser.add_argument("--candidate-quantile", type=float, default=CANDIDATE_QUANTILE)
    parser.add_argument(
        "--persistence-min-hits", type=int, default=PERSISTENCE_MIN_HITS
    )
    parser.add_argument("--min-crowd-size", type=int, default=MIN_CROWD_SIZE)
    parser.add_argument("--output-dir", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.project_root.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else root / "artifacts" / "leverage_capitulation" / STUDY_NAME
    )
    market_snapshot = (
        root
        / "artifacts"
        / "leverage_capitulation"
        / "crowding_margin_top_risk_input_snapshot_20260722"
    )
    config = StudyConfig(
        db_path=root
        / "artifacts"
        / "leverage_capitulation"
        / "individual_margin_2016_present"
        / "eastmoney_individual_margin.sqlite",
        aggregate_margin_csv=root
        / "artifacts"
        / "leverage_capitulation"
        / "dfcf_daily"
        / "dfcf_margin_balances.csv",
        aggregate_audit_json=root
        / "artifacts"
        / "leverage_capitulation"
        / "dfcf_daily"
        / "dfcf_margin_audit.json",
        index_day_path=market_snapshot
        / "vipdoc"
        / "sz"
        / "lday"
        / "sz399106.day",
        ht_root=market_snapshot,
        market_snapshot_manifest=market_snapshot / "snapshot_manifest.csv",
        gbbq_path=market_snapshot / "T0002" / "hq_cache" / "gbbq",
        gbbq_reader_path=Path(
            r"D:\vcp_hunter\紫金研选\.venv\Lib\site-packages"
            r"\pytdx\reader\gbbq_reader.py"
        ),
        individual_audit_json=root
        / "artifacts"
        / "leverage_capitulation"
        / "individual_margin_2016_present"
        / "individual_margin_audit.json",
        output_dir=output_dir,
        start_date=args.start_date,
        end_date=args.end_date,
        candidate_quantile=args.candidate_quantile,
        persistence_min_hits=args.persistence_min_hits,
        min_crowd_size=args.min_crowd_size,
    )
    results = run_study(config)
    pooled = results["pooled_oos_metrics"]
    print(f"Study completed: {output_dir}")
    print(f"Pooled model rows: {len(pooled)}")
    print(f"Report: {output_dir / 'RESEARCH_REPORT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
