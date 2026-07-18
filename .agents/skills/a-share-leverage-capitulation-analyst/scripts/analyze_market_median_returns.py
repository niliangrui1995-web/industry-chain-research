from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from array import array
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DAY_STRUCT = struct.Struct("<IIIIIfII")
A_SHARE_PATTERNS = (
    re.compile(r"sh(?:600|601|603|605|688|689)\d{3}"),
    re.compile(r"sz(?:000|001|002|003|300|301)\d{3}"),
    re.compile(r"bj(?:43|83|87|88|92)\d{4}"),
)
ORIGINAL_SIGNAL_NAME = "sz_triple"
ORIGINAL_INDEX_CODE = "399106"
TDX_AVERAGE_PRICE_INDEX_CODE = "880003"
OUTPUT_YEARS = 10
RANK_WINDOW_YEARS = 3
MIN_RANK_OBSERVATIONS = 600


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_audited_average_price_source(
    source_audit_path: Path,
    override_path: Path | None,
) -> tuple[Path, dict[str, object]]:
    if not source_audit_path.is_file():
        raise FileNotFoundError(
            f"Controlled 880003 source audit is unavailable: {source_audit_path}"
        )
    payload = json.loads(source_audit_path.read_text(encoding="utf-8"))
    source = payload.get("sources", {}).get(TDX_AVERAGE_PRICE_INDEX_CODE)
    if not isinstance(source, dict):
        raise ValueError("Controlled source audit does not contain 880003 metadata")
    expected_hash = str(source.get("sha256", ""))
    if len(expected_hash) != 64:
        raise ValueError("Controlled source audit does not contain a valid 880003 SHA-256")

    source_path = override_path or Path(str(source.get("path", "")))
    if not source_path.is_file():
        raise FileNotFoundError(f"Controlled 880003 snapshot is unavailable: {source_path}")
    actual_hash = sha256_file(source_path)
    if actual_hash != expected_hash:
        raise ValueError("Controlled 880003 snapshot hash does not match its source audit")
    return source_path, {
        "source_audit_path": str(source_audit_path.resolve()),
        "source_audit_sha256": sha256_file(source_audit_path),
        "expected_sha256": expected_hash,
        "actual_sha256": actual_hash,
    }


def is_a_share_day_file(path: Path) -> bool:
    return any(pattern.fullmatch(path.stem.lower()) for pattern in A_SHARE_PATTERNS)


def discover_a_share_files(ht_root: Path) -> list[Path]:
    files: list[Path] = []
    for market in ("sh", "sz", "bj"):
        folder = ht_root / "vipdoc" / market / "lday"
        if folder.exists():
            files.extend(path for path in folder.glob("*.day") if is_a_share_day_file(path))
    if not files:
        raise FileNotFoundError(f"No A-share .day files found under {ht_root / 'vipdoc'}")
    return sorted(files)


def read_trading_calendar(ht_root: Path) -> pd.DatetimeIndex:
    path = ht_root / "vipdoc" / "sz" / "lday" / "sz399106.day"
    if not path.exists():
        raise FileNotFoundError(f"Trading-calendar index file not found: {path}")
    raw = path.read_bytes()
    if not raw or len(raw) % DAY_STRUCT.size:
        raise ValueError(f"Invalid trading-calendar index file: {path}")
    dates: list[int] = []
    previous = 0
    for offset in range(0, len(raw), DAY_STRUCT.size):
        date_value, _, _, _, close_value, _, _, _ = DAY_STRUCT.unpack_from(raw, offset)
        if not 19900101 <= date_value <= 20991231 or close_value <= 0:
            raise ValueError(f"Invalid calendar record in {path} at byte offset {offset}")
        if date_value <= previous:
            raise ValueError(f"Non-increasing calendar record in {path} at byte offset {offset}")
        dates.append(date_value)
        previous = date_value
    return pd.DatetimeIndex(pd.to_datetime(pd.Series(dates).astype(str), format="%Y%m%d"))


def read_vendor_close_index(path: Path, close_column: str, return_column: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Vendor index file not found: {path}")
    raw = path.read_bytes()
    if not raw or len(raw) % DAY_STRUCT.size:
        raise ValueError(f"Invalid vendor index file: {path}")
    rows: list[tuple[int, float]] = []
    previous_date = 0
    for offset in range(0, len(raw), DAY_STRUCT.size):
        date_value, _, _, _, close_value, _, _, _ = DAY_STRUCT.unpack_from(raw, offset)
        if not 19900101 <= date_value <= 20991231 or close_value <= 0:
            raise ValueError(f"Invalid vendor index record in {path} at byte offset {offset}")
        if date_value <= previous_date:
            raise ValueError(f"Non-increasing vendor index record in {path} at byte offset {offset}")
        rows.append((date_value, close_value / 100.0))
        previous_date = date_value
    frame = pd.DataFrame(rows, columns=["date", close_column])
    frame["date"] = pd.to_datetime(frame["date"].astype(str), format="%Y%m%d", errors="raise")
    frame[return_column] = frame[close_column].pct_change() * 100.0
    return frame


def collect_daily_returns(
    paths: Iterable[Path],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> tuple[dict[int, array], dict[str, object]]:
    start_value = int(start_date.strftime("%Y%m%d"))
    end_value = int(end_date.strftime("%Y%m%d"))
    returns_by_date: dict[int, array] = {}
    invalid_size_files: list[str] = []
    invalid_order_files: list[str] = []
    invalid_date_rows = 0
    invalid_close_rows = 0
    file_first_dates: Counter[int] = Counter()
    file_last_dates: Counter[int] = Counter()
    file_count = 0

    for path in paths:
        file_count += 1
        raw = path.read_bytes()
        if not raw or len(raw) % DAY_STRUCT.size:
            invalid_size_files.append(str(path))
            continue
        previous_date = 0
        previous_valid_close: int | None = None
        first_date = 0
        last_date = 0
        ordered = True
        for offset in range(0, len(raw), DAY_STRUCT.size):
            date_value, _, _, _, close_value, _, _, _ = DAY_STRUCT.unpack_from(raw, offset)
            if not 19900101 <= date_value <= 20991231:
                invalid_date_rows += 1
                ordered = False
                continue
            if date_value <= previous_date:
                ordered = False
            if not first_date:
                first_date = date_value
            last_date = date_value
            previous_date = date_value
            if close_value <= 0:
                invalid_close_rows += 1
                continue
            if previous_valid_close is not None and start_value <= date_value <= end_value:
                daily = returns_by_date.setdefault(date_value, array("d"))
                daily.append((close_value / previous_valid_close - 1.0) * 100.0)
            previous_valid_close = close_value
        if not ordered:
            invalid_order_files.append(str(path))
        if first_date:
            file_first_dates[first_date] += 1
            file_last_dates[last_date] += 1

    report = {
        "a_share_files": file_count,
        "invalid_size_files": len(invalid_size_files),
        "invalid_order_files": len(invalid_order_files),
        "invalid_date_rows": invalid_date_rows,
        "invalid_close_rows": invalid_close_rows,
        "earliest_file_date": str(min(file_first_dates)) if file_first_dates else None,
        "latest_file_date": str(max(file_last_dates)) if file_last_dates else None,
        "files_with_latest_date": (
            int(file_last_dates[max(file_last_dates)]) if file_last_dates else 0
        ),
        "files_ending_before_latest_date": (
            file_count - int(file_last_dates[max(file_last_dates)]) if file_last_dates else file_count
        ),
        "invalid_size_examples": invalid_size_files[:10],
        "invalid_order_examples": invalid_order_files[:10],
    }
    return returns_by_date, report


def summarize_returns(values: array) -> dict[str, float | int | None]:
    numeric = np.frombuffer(values, dtype=np.float64)
    if numeric.size == 0:
        raise ValueError("Cannot summarize an empty daily return array")
    down = numeric[numeric < 0.0]
    trimmed = numeric[np.abs(numeric) <= 22.0]
    return {
        "comparable_count": int(numeric.size),
        "down_count": int((numeric < 0.0).sum()),
        "up_count": int((numeric > 0.0).sum()),
        "flat_count": int((numeric == 0.0).sum()),
        "down_pct": float((numeric < 0.0).mean() * 100.0),
        "market_return_median_pct": float(np.median(numeric)),
        "decliners_median_return_pct": None if down.size == 0 else float(np.median(down)),
        "market_return_mean_pct": float(numeric.mean()),
        "return_q25_pct": float(np.quantile(numeric, 0.25)),
        "return_q75_pct": float(np.quantile(numeric, 0.75)),
        "return_min_pct": float(numeric.min()),
        "return_max_pct": float(numeric.max()),
        "abs_return_gt_22_count": int((np.abs(numeric) > 22.0).sum()),
        "trimmed_comparable_count": int(trimmed.size),
        "trimmed_market_return_median_pct": (
            None if trimmed.size == 0 else float(np.median(trimmed))
        ),
    }


def build_daily_statistics(
    calendar: pd.DatetimeIndex,
    returns_by_date: dict[int, array],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    selected_calendar = calendar[(calendar >= start_date) & (calendar <= end_date)]
    rows: list[dict[str, object]] = []
    missing_dates: list[str] = []
    for date in selected_calendar:
        date_value = int(date.strftime("%Y%m%d"))
        values = returns_by_date.get(date_value)
        if values is None or len(values) == 0:
            missing_dates.append(date.strftime("%Y-%m-%d"))
            continue
        rows.append({"date": date, **summarize_returns(values)})
    if missing_dates:
        raise ValueError(
            f"Missing stock-return distributions for {len(missing_dates)} trading dates: "
            f"{missing_dates[:10]}"
        )
    frame = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    reference_count = frame["comparable_count"].rolling(20, min_periods=1).median()
    frame["coverage_ratio_to_trailing_20d_median"] = (
        frame["comparable_count"] / reference_count.replace(0.0, np.nan)
    )
    frame["market_data_valid"] = (
        frame["comparable_count"].ge(1000)
        & frame["coverage_ratio_to_trailing_20d_median"].ge(0.70)
    )
    return frame


def causal_rolling_rank(
    dates: pd.Series,
    values: pd.Series,
    *,
    years: int = 3,
    min_observations: int = 600,
    eligible: pd.Series | None = None,
) -> pd.DataFrame:
    parsed_dates = pd.to_datetime(dates).reset_index(drop=True)
    numeric = pd.to_numeric(values, errors="coerce").reset_index(drop=True)
    allowed = (
        pd.Series(True, index=numeric.index)
        if eligible is None
        else eligible.fillna(False).astype(bool).reset_index(drop=True)
    )
    ranks = pd.Series(np.nan, index=numeric.index, dtype=float)
    observations = pd.Series(pd.NA, index=numeric.index, dtype="Int64")
    percentiles = pd.Series(np.nan, index=numeric.index, dtype=float)
    window_starts = pd.Series(pd.NaT, index=numeric.index, dtype="datetime64[ns]")

    for position, (date, value) in enumerate(zip(parsed_dates, numeric)):
        if pd.isna(value) or not allowed.iloc[position]:
            continue
        start = date - pd.DateOffset(years=years)
        past_dates = parsed_dates.iloc[: position + 1]
        mask = (
            past_dates.ge(start)
            & allowed.iloc[: position + 1]
            & numeric.iloc[: position + 1].notna()
        )
        window = numeric.iloc[: position + 1][mask]
        if len(window) < min_observations or window.index.empty:
            continue
        if parsed_dates.iloc[0] > start:
            continue
        rank = 1 + int((window < value).sum())
        ranks.iloc[position] = rank
        observations.iloc[position] = len(window)
        percentiles.iloc[position] = rank / len(window) * 100.0
        window_starts.iloc[position] = start

    return pd.DataFrame(
        {
            "market_return_median_rank_3y": ranks.astype("Int64"),
            "market_return_median_rank_window_observations": observations,
            "market_return_median_rank_percentile_3y": percentiles,
            "market_return_median_rank_window_start": window_starts,
        }
    )


def parse_bool_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    normalized = series.astype(str).str.strip().str.lower()
    valid = normalized.isin({"true", "false"})
    if not valid.all():
        bad = sorted(normalized.loc[~valid].unique().tolist())
        raise ValueError(f"Invalid boolean values: {bad[:10]}")
    return normalized.eq("true")


def load_original_signal_dates(backtest_dir: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    results_path = backtest_dir / "backtest_results.json"
    panel_path = backtest_dir / "factor_panel.csv"
    signals_path = backtest_dir / f"signals_{ORIGINAL_SIGNAL_NAME}.csv"
    for path in (results_path, panel_path, signals_path):
        if not path.exists():
            raise FileNotFoundError(f"Required backtest artifact not found: {path}")

    results = json.loads(results_path.read_text(encoding="utf-8"))
    config = results.get("config", {})
    expected_config = {
        "window_years": 3,
        "rank_threshold": 15,
        "breadth_threshold": 80.0,
        "start_date": "2019-01-01",
    }
    for key, expected in expected_config.items():
        if config.get(key) != expected:
            raise ValueError(
                f"Backtest config {key}={config.get(key)!r} does not match original factor {expected!r}"
            )

    metadata = results.get("metadata", {})
    factor_codes = metadata.get("factor_index_codes", {})
    if factor_codes.get("sz_comp") != ORIGINAL_INDEX_CODE:
        raise ValueError("Original factor does not use Shenzhen Composite 399106")

    margin_csv = Path(str(metadata.get("margin_csv", "")))
    margin_audit_path = Path(str(metadata.get("margin_audit_json", "")))
    if not margin_csv.exists() or not margin_audit_path.exists():
        raise FileNotFoundError("Verified margin artifacts referenced by the backtest are unavailable")
    margin_audit = json.loads(margin_audit_path.read_text(encoding="utf-8"))
    if margin_audit.get("verified_snapshot_complete") is not True:
        raise ValueError("Margin audit did not pass the verified snapshot gate")
    margin_hash = sha256_file(margin_csv)
    if margin_hash != margin_audit.get("verified_margin_balances_sha256"):
        raise ValueError("Verified margin CSV hash does not match its audit report")
    if margin_hash != metadata.get("margin_csv_sha256"):
        raise ValueError("Verified margin CSV hash does not match the backtest metadata")

    panel = pd.read_csv(panel_path, parse_dates=["date"])
    required = {
        "date",
        "sz_comp_return_pct",
        "margin_outflow_pct",
        "sz_comp_rank",
        "margin_outflow_rank",
        "breadth_total",
        "down_pct",
        "breadth_valid",
        "margin_data_valid",
        "long_break_eve",
    }
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"Factor panel missing columns: {sorted(missing)}")
    breadth_valid = parse_bool_series(panel["breadth_valid"])
    margin_valid = parse_bool_series(panel["margin_data_valid"])
    long_break_eve = parse_bool_series(panel["long_break_eve"])
    mask = (
        panel["date"].ge(pd.Timestamp(expected_config["start_date"]))
        & breadth_valid
        & margin_valid
        & ~long_break_eve
        & panel["sz_comp_rank"].le(expected_config["rank_threshold"])
        & panel["margin_outflow_rank"].le(expected_config["rank_threshold"])
        & panel["down_pct"].ge(expected_config["breadth_threshold"])
    )
    selected_columns = [
        "date",
        "sz_comp_return_pct",
        "margin_outflow_pct",
        "sz_comp_rank",
        "margin_outflow_rank",
        "breadth_total",
        "down_pct",
    ]
    selected = panel.loc[mask, selected_columns].copy().sort_values("date").reset_index(drop=True)

    exported = pd.read_csv(signals_path, parse_dates=["date"])
    selected_dates = selected["date"].dt.strftime("%Y-%m-%d").tolist()
    exported_dates = exported["date"].dt.strftime("%Y-%m-%d").tolist()
    if selected_dates != exported_dates:
        raise ValueError("Recomputed original-factor signal dates disagree with signals_sz_triple.csv")
    expected_count = int(
        results.get("summaries", {})
        .get(ORIGINAL_SIGNAL_NAME, {})
        .get("all_signals", {})
        .get("signal_count", -1)
    )
    if len(selected) != expected_count:
        raise ValueError(
            f"Recomputed original-factor signal count {len(selected)} disagrees with summary {expected_count}"
        )

    audit = {
        "backtest_results": str(results_path.resolve()),
        "backtest_results_sha256": sha256_file(results_path),
        "factor_panel": str(panel_path.resolve()),
        "factor_panel_sha256": sha256_file(panel_path),
        "signals_csv": str(signals_path.resolve()),
        "signals_csv_sha256": sha256_file(signals_path),
        "verified_margin_csv": str(margin_csv.resolve()),
        "verified_margin_csv_sha256": margin_hash,
        "margin_audit_json": str(margin_audit_path.resolve()),
        "margin_audit_json_sha256": sha256_file(margin_audit_path),
        "verified_margin_start": margin_audit.get("verified_start"),
        "verified_margin_end": margin_audit.get("verified_end"),
        "formal_signal_count": len(selected),
    }
    return selected, audit


def next_trading_date(calendar: pd.DatetimeIndex, date: pd.Timestamp) -> pd.Timestamp | pd.NaT:
    position = int(calendar.searchsorted(date, side="right"))
    return pd.NaT if position >= len(calendar) else calendar[position]


def build_signal_rank_table(
    signals: pd.DataFrame,
    daily: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    *,
    sample_status: str = "formal_verified",
    information_timing: str = "T日压力；T+1交易日开市前信号可用",
) -> pd.DataFrame:
    lookup_columns = [
        "date",
        "comparable_count",
        "market_return_median_pct",
        "decliners_median_return_pct",
        "return_q25_pct",
        "return_q75_pct",
        "market_return_median_rank_3y",
        "market_return_median_rank_window_observations",
        "market_return_median_rank_percentile_3y",
        "tdx_average_price_index_close",
        "tdx_average_price_index_return_pct",
        "tdx_average_price_index_return_rank_3y",
        "tdx_average_price_index_return_rank_window_observations",
        "tdx_average_price_index_return_rank_percentile_3y",
        "market_data_valid",
    ]
    event_lookup = daily[lookup_columns].rename(
        columns={
            "date": "factor_observation_date",
            "comparable_count": "factor_date_comparable_count",
            "market_return_median_pct": "factor_date_market_return_median_pct",
            "decliners_median_return_pct": "factor_date_decliners_median_return_pct",
            "return_q25_pct": "factor_date_return_q25_pct",
            "return_q75_pct": "factor_date_return_q75_pct",
            "market_return_median_rank_3y": "factor_date_market_return_median_rank_3y",
            "market_return_median_rank_window_observations": (
                "factor_date_rank_window_observations"
            ),
            "market_return_median_rank_percentile_3y": (
                "factor_date_market_return_median_rank_percentile_3y"
            ),
            "tdx_average_price_index_close": "factor_date_tdx_average_price_index_close",
            "tdx_average_price_index_return_pct": (
                "factor_date_tdx_average_price_index_return_pct"
            ),
            "tdx_average_price_index_return_rank_3y": (
                "factor_date_tdx_average_price_index_return_rank_3y"
            ),
            "tdx_average_price_index_return_rank_window_observations": (
                "factor_date_tdx_average_price_index_rank_window_observations"
            ),
            "tdx_average_price_index_return_rank_percentile_3y": (
                "factor_date_tdx_average_price_index_return_rank_percentile_3y"
            ),
            "market_data_valid": "factor_date_market_data_valid",
        }
    )
    output = signals.rename(columns={"date": "factor_observation_date"}).merge(
        event_lookup,
        on="factor_observation_date",
        how="left",
        validate="one_to_one",
    )
    if output["factor_date_market_return_median_pct"].isna().any():
        raise ValueError("One or more formal signal dates are missing market-median statistics")

    output["signal_available_date"] = output["factor_observation_date"].map(
        lambda value: next_trading_date(calendar, pd.Timestamp(value))
    )
    available_lookup = daily[lookup_columns].rename(
        columns={
            "date": "signal_available_date",
            "comparable_count": "available_date_comparable_count",
            "market_return_median_pct": "available_date_market_return_median_pct",
            "decliners_median_return_pct": "available_date_decliners_median_return_pct",
            "return_q25_pct": "available_date_return_q25_pct",
            "return_q75_pct": "available_date_return_q75_pct",
            "market_return_median_rank_3y": "available_date_market_return_median_rank_3y",
            "market_return_median_rank_window_observations": (
                "available_date_rank_window_observations"
            ),
            "market_return_median_rank_percentile_3y": (
                "available_date_market_return_median_rank_percentile_3y"
            ),
            "tdx_average_price_index_close": "available_date_tdx_average_price_index_close",
            "tdx_average_price_index_return_pct": (
                "available_date_tdx_average_price_index_return_pct"
            ),
            "tdx_average_price_index_return_rank_3y": (
                "available_date_tdx_average_price_index_return_rank_3y"
            ),
            "tdx_average_price_index_return_rank_window_observations": (
                "available_date_tdx_average_price_index_rank_window_observations"
            ),
            "tdx_average_price_index_return_rank_percentile_3y": (
                "available_date_tdx_average_price_index_return_rank_percentile_3y"
            ),
            "market_data_valid": "available_date_market_data_valid",
        }
    )
    output = output.merge(
        available_lookup,
        on="signal_available_date",
        how="left",
        validate="many_to_one",
    )
    output.insert(0, "sample_status", sample_status)
    output.insert(1, "signal_definition", "399106跌幅排名Top15+融资流出比例排名Top15+收跌占比>=80%")
    output.insert(2, "information_timing", information_timing)
    return output


def load_estimated_original_signal_scenarios(
    backtest_dir: Path,
) -> tuple[pd.DataFrame, dict[str, object]]:
    scenario_path = backtest_dir / "estimated_signal_scenarios.json"
    if not scenario_path.exists():
        return pd.DataFrame(), {
            "estimated_scenario_source": None,
            "estimated_scenario_source_sha256": None,
            "estimated_original_signal_count": 0,
        }
    payload = json.loads(scenario_path.read_text(encoding="utf-8"))
    if payload.get("formal_statistics_inclusion") is not False:
        raise ValueError("Estimated scenario file must explicitly exclude scenarios from formal statistics")
    required = {
        "date",
        "sample_status",
        "sz_comp_return_pct",
        "margin_outflow_pct",
        "sz_comp_rank",
        "margin_outflow_rank",
        "breadth_total",
        "down_pct",
        "breadth_valid",
        "long_break_eve",
    }
    selected: list[dict[str, object]] = []
    for scenario in payload.get("scenarios", []):
        missing = required - set(scenario)
        if missing:
            raise ValueError(f"Estimated scenario missing columns: {sorted(missing)}")
        if scenario["sample_status"] != "estimated_not_in_formal_statistics":
            raise ValueError("Estimated scenario has an invalid sample status")
        original_signal_pass = (
            float(scenario["sz_comp_rank"]) <= 15
            and float(scenario["margin_outflow_rank"]) <= 15
            and float(scenario["down_pct"]) >= 80.0
            and bool(scenario["breadth_valid"])
            and not bool(scenario["long_break_eve"])
        )
        if original_signal_pass:
            selected.append(
                {
                    "date": pd.Timestamp(scenario["date"]),
                    "sz_comp_return_pct": float(scenario["sz_comp_return_pct"]),
                    "margin_outflow_pct": float(scenario["margin_outflow_pct"]),
                    "sz_comp_rank": float(scenario["sz_comp_rank"]),
                    "margin_outflow_rank": float(scenario["margin_outflow_rank"]),
                    "breadth_total": int(scenario["breadth_total"]),
                    "down_pct": float(scenario["down_pct"]),
                }
            )
    frame = pd.DataFrame(selected)
    if not frame.empty:
        frame = frame.sort_values("date").reset_index(drop=True)
    audit = {
        "estimated_scenario_source": str(scenario_path.resolve()),
        "estimated_scenario_source_sha256": sha256_file(scenario_path),
        "estimated_original_signal_count": len(frame),
    }
    return frame, audit


def build_average_price_replacement_comparison(
    backtest_dir: Path,
    daily: pd.DataFrame,
    original_signals: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    panel_path = backtest_dir / "factor_panel.csv"
    if not panel_path.exists():
        raise FileNotFoundError(f"Factor panel not found: {panel_path}")
    panel = pd.read_csv(panel_path, parse_dates=["date"])
    required = {
        "date",
        "sz_comp_return_pct",
        "sz_comp_rank",
        "margin_outflow_pct",
        "margin_outflow_rank",
        "breadth_total",
        "down_pct",
        "breadth_valid",
        "margin_data_valid",
        "long_break_eve",
    }
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"Factor panel missing columns for index replacement: {sorted(missing)}")
    daily_columns = [
        "date",
        "market_return_median_pct",
        "market_return_median_rank_3y",
        "tdx_average_price_index_close",
        "tdx_average_price_index_return_pct",
        "tdx_average_price_index_return_rank_3y",
    ]
    merged = panel.merge(
        daily[daily_columns],
        on="date",
        how="left",
        validate="one_to_one",
    )
    breadth_valid = parse_bool_series(merged["breadth_valid"])
    margin_valid = parse_bool_series(merged["margin_data_valid"])
    long_break_eve = parse_bool_series(merged["long_break_eve"])
    common = (
        merged["date"].ge(pd.Timestamp("2019-01-01"))
        & breadth_valid
        & margin_valid
        & ~long_break_eve
        & merged["margin_outflow_rank"].notna()
        & merged["margin_outflow_rank"].le(15)
        & merged["down_pct"].ge(80.0)
    )
    original_mask = common & merged["sz_comp_rank"].notna() & merged["sz_comp_rank"].le(15)
    replacement_mask = (
        common
        & merged["tdx_average_price_index_return_rank_3y"].notna()
        & merged["tdx_average_price_index_return_rank_3y"].le(15)
    )
    expected_original_dates = original_signals["date"].dt.strftime("%Y-%m-%d").tolist()
    recomputed_original_dates = (
        merged.loc[original_mask, "date"].dt.strftime("%Y-%m-%d").tolist()
    )
    if recomputed_original_dates != expected_original_dates:
        raise ValueError(
            "Index-replacement comparison could not reproduce the verified 399106 signal dates"
        )

    merged["signal_399106"] = original_mask
    merged["signal_880003"] = replacement_mask
    union_mask = original_mask | replacement_mask
    comparison = merged.loc[
        union_mask,
        [
            "date",
            "signal_399106",
            "signal_880003",
            "sz_comp_return_pct",
            "sz_comp_rank",
            "tdx_average_price_index_close",
            "tdx_average_price_index_return_pct",
            "tdx_average_price_index_return_rank_3y",
            "margin_outflow_pct",
            "margin_outflow_rank",
            "breadth_total",
            "down_pct",
            "market_return_median_pct",
            "market_return_median_rank_3y",
        ],
    ].copy()
    comparison.insert(0, "sample_status", "formal_verified")
    comparison.insert(
        2,
        "membership",
        np.select(
            [
                comparison["signal_399106"] & comparison["signal_880003"],
                comparison["signal_399106"],
            ],
            ["both", "399106_only"],
            default="880003_only",
        ),
    )
    comparison = comparison.sort_values("date").reset_index(drop=True)
    replacement_signals = comparison.loc[comparison["signal_880003"]].copy()
    audit = {
        "factor_panel": str(panel_path.resolve()),
        "factor_panel_sha256": sha256_file(panel_path),
        "original_399106_formal_signal_count": int(original_mask.sum()),
        "replacement_880003_formal_signal_count": int(replacement_mask.sum()),
        "common_formal_signal_count": int((original_mask & replacement_mask).sum()),
        "original_399106_only_count": int((original_mask & ~replacement_mask).sum()),
        "replacement_880003_only_count": int((replacement_mask & ~original_mask).sum()),
        "formal_union_count": int(union_mask.sum()),
    }
    return replacement_signals, comparison, audit


def build_estimated_replacement_comparison(
    estimated_signals: pd.DataFrame,
    daily: pd.DataFrame,
) -> pd.DataFrame:
    if estimated_signals.empty:
        return pd.DataFrame()
    daily_columns = [
        "date",
        "market_return_median_pct",
        "market_return_median_rank_3y",
        "tdx_average_price_index_close",
        "tdx_average_price_index_return_pct",
        "tdx_average_price_index_return_rank_3y",
    ]
    scenario = estimated_signals.merge(
        daily[daily_columns],
        on="date",
        how="left",
        validate="one_to_one",
    )
    if scenario["tdx_average_price_index_return_rank_3y"].isna().any():
        raise ValueError("Estimated scenario is missing the 880003 causal rank")
    scenario["signal_399106"] = True
    scenario["signal_880003"] = scenario["tdx_average_price_index_return_rank_3y"].le(15)
    scenario.insert(0, "sample_status", "estimated_not_in_formal_statistics")
    scenario.insert(
        2,
        "membership",
        np.where(scenario["signal_880003"], "both", "399106_only"),
    )
    columns = [
        "sample_status",
        "date",
        "membership",
        "signal_399106",
        "signal_880003",
        "sz_comp_return_pct",
        "sz_comp_rank",
        "tdx_average_price_index_close",
        "tdx_average_price_index_return_pct",
        "tdx_average_price_index_return_rank_3y",
        "margin_outflow_pct",
        "margin_outflow_rank",
        "breadth_total",
        "down_pct",
        "market_return_median_pct",
        "market_return_median_rank_3y",
    ]
    return scenario[columns].sort_values("date").reset_index(drop=True)


def to_jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def build_parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parents[4]
    default_backtest = (
        project_root
        / "artifacts"
        / "leverage_capitulation"
        / "verified_2016_present"
        / "backtest_2019_present"
    )
    default_output = (
        project_root
        / "artifacts"
        / "leverage_capitulation"
        / "verified_2016_present"
        / "market_median_10y"
    )
    default_source_audit = (
        project_root
        / "artifacts"
        / "leverage_capitulation"
        / "verified_2016_present"
        / "intraday_index_drawdown_3y"
        / "intraday_drawdown_analysis_audit.json"
    )
    parser = argparse.ArgumentParser(
        description="Calculate causal daily A-share median returns and original-signal trailing ranks"
    )
    parser.add_argument("--ht-root", type=Path, default=Path(r"D:\HT"))
    parser.add_argument("--backtest-dir", type=Path, default=default_backtest)
    parser.add_argument("--output-dir", type=Path, default=default_output)
    parser.add_argument(
        "--average-price-index-path",
        type=Path,
        help="Optional relocated 880003 snapshot; its hash must match the controlled source audit",
    )
    parser.add_argument(
        "--intraday-source-audit",
        type=Path,
        default=default_source_audit,
        help="Audit JSON that locks the complete 880003 snapshot SHA-256",
    )
    parser.add_argument("--end-date", help="Optional inclusive end date; defaults to latest local 399106 date")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    calendar = read_trading_calendar(args.ht_root)
    latest_local_date = pd.Timestamp(calendar.max())
    requested_end = latest_local_date if args.end_date is None else pd.Timestamp(args.end_date)
    end_date = min(requested_end, latest_local_date)
    output_boundary = end_date - pd.DateOffset(years=OUTPUT_YEARS)
    output_start_date = pd.Timestamp(calendar[calendar >= output_boundary].min())
    warmup_boundary = output_start_date - pd.DateOffset(years=RANK_WINDOW_YEARS)
    warmup_start_date = pd.Timestamp(calendar[calendar >= warmup_boundary].min())

    paths = discover_a_share_files(args.ht_root)
    returns_by_date, file_audit = collect_daily_returns(paths, warmup_start_date, end_date)
    daily = build_daily_statistics(calendar, returns_by_date, warmup_start_date, end_date)
    average_price_index_path, average_price_source_audit = load_audited_average_price_source(
        args.intraday_source_audit,
        args.average_price_index_path,
    )
    average_price_index = read_vendor_close_index(
        average_price_index_path,
        "tdx_average_price_index_close",
        "tdx_average_price_index_return_pct",
    )
    daily = daily.merge(
        average_price_index,
        on="date",
        how="left",
        validate="one_to_one",
    )
    rank_columns = causal_rolling_rank(
        daily["date"],
        daily["market_return_median_pct"],
        years=RANK_WINDOW_YEARS,
        min_observations=MIN_RANK_OBSERVATIONS,
        eligible=daily["market_data_valid"],
    )
    average_price_rank_columns = causal_rolling_rank(
        daily["date"],
        daily["tdx_average_price_index_return_pct"],
        years=RANK_WINDOW_YEARS,
        min_observations=MIN_RANK_OBSERVATIONS,
        eligible=daily["market_data_valid"],
    ).rename(
        columns={
            "market_return_median_rank_3y": "tdx_average_price_index_return_rank_3y",
            "market_return_median_rank_window_observations": (
                "tdx_average_price_index_return_rank_window_observations"
            ),
            "market_return_median_rank_percentile_3y": (
                "tdx_average_price_index_return_rank_percentile_3y"
            ),
            "market_return_median_rank_window_start": (
                "tdx_average_price_index_return_rank_window_start"
            ),
        }
    )
    daily = pd.concat([daily, rank_columns, average_price_rank_columns], axis=1)
    output_daily = daily.loc[daily["date"].between(output_start_date, end_date)].copy()
    if output_daily["market_return_median_rank_3y"].isna().any():
        missing = output_daily.loc[
            output_daily["market_return_median_rank_3y"].isna(), "date"
        ].dt.strftime("%Y-%m-%d").tolist()
        raise ValueError(f"Causal three-year rank is unavailable for output dates: {missing[:10]}")
    missing_average_price = output_daily[
        [
            "tdx_average_price_index_return_pct",
            "tdx_average_price_index_return_rank_3y",
        ]
    ].isna().any(axis=1)
    if missing_average_price.any():
        missing = output_daily.loc[missing_average_price, "date"].dt.strftime("%Y-%m-%d").tolist()
        raise ValueError(
            f"TDX average-price index return or causal rank is unavailable for output dates: {missing[:10]}"
        )

    signals, signal_audit = load_original_signal_dates(args.backtest_dir)
    signal_table = build_signal_rank_table(signals, daily, calendar)
    estimated_signals, estimated_signal_audit = load_estimated_original_signal_scenarios(
        args.backtest_dir
    )
    if estimated_signals.empty:
        estimated_signal_table = signal_table.iloc[0:0].copy()
    else:
        estimated_signal_table = build_signal_rank_table(
            estimated_signals,
            daily,
            calendar,
            sample_status="estimated_not_in_formal_statistics",
            information_timing=(
                "T日压力；下一交易日开市前信号可用；下一交易日本地日线尚未落盘"
            ),
        )
    combined_signal_table = (
        pd.concat([signal_table, estimated_signal_table], ignore_index=True)
        .sort_values("factor_observation_date")
        .reset_index(drop=True)
    )
    replacement_signals, replacement_comparison, replacement_audit = (
        build_average_price_replacement_comparison(
            args.backtest_dir,
            daily,
            signals,
        )
    )
    estimated_replacement_comparison = build_estimated_replacement_comparison(
        estimated_signals,
        daily,
    )
    replacement_comparison_with_scenarios = (
        pd.concat(
            [replacement_comparison, estimated_replacement_comparison],
            ignore_index=True,
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    daily_path = args.output_dir / "market_median_daily_10y.csv"
    signal_path = args.output_dir / "original_399106_signal_market_median_rank_3y.csv"
    estimated_signal_path = (
        args.output_dir / "estimated_original_399106_signal_market_median_rank_3y.csv"
    )
    combined_signal_path = (
        args.output_dir / "original_399106_signal_market_median_rank_3y_with_scenarios.csv"
    )
    replacement_signal_path = args.output_dir / "signals_tdx_average_price_880003_triple.csv"
    replacement_comparison_path = (
        args.output_dir / "signal_date_comparison_399106_vs_880003.csv"
    )
    replacement_comparison_scenario_path = (
        args.output_dir / "signal_date_comparison_399106_vs_880003_with_scenarios.csv"
    )
    audit_path = args.output_dir / "market_median_analysis_audit.json"
    output_daily.to_csv(daily_path, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
    signal_table.to_csv(signal_path, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
    estimated_signal_table.to_csv(
        estimated_signal_path, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d"
    )
    combined_signal_table.to_csv(
        combined_signal_path, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d"
    )
    replacement_signals.to_csv(
        replacement_signal_path, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d"
    )
    replacement_comparison.to_csv(
        replacement_comparison_path,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )
    replacement_comparison_with_scenarios.to_csv(
        replacement_comparison_scenario_path,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )

    latest_row = output_daily.iloc[-1]
    estimated_scenario_dates = (
        estimated_signal_table["factor_observation_date"].dt.strftime("%Y-%m-%d").tolist()
    )
    audit = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "data_classification": "market_data_vendor",
        "ht_root": str(args.ht_root.resolve()),
        "calendar_source": str(
            (args.ht_root / "vipdoc" / "sz" / "lday" / "sz399106.day").resolve()
        ),
        "latest_local_trading_date": latest_local_date.strftime("%Y-%m-%d"),
        "output_start": output_start_date.strftime("%Y-%m-%d"),
        "output_end": end_date.strftime("%Y-%m-%d"),
        "output_trading_days": len(output_daily),
        "warmup_start": warmup_start_date.strftime("%Y-%m-%d"),
        "market_return_definition": (
            "For every A-share with a valid close on T and a previous valid local record, "
            "close(T)/previous_valid_close-1; daily market value is the cross-sectional median."
        ),
        "suspension_handling": (
            "No T record means exclusion on T; the first post-suspension return uses the previous valid record."
        ),
        "ipo_handling": "First local record is excluded because no previous valid close exists.",
        "rank_definition": (
            "1 + count of strictly lower daily market medians within [T-3 calendar years, T]; "
            "rank 1 is the worst median decline."
        ),
        "tdx_average_price_index": {
            "code": TDX_AVERAGE_PRICE_INDEX_CODE,
            "source_status": "market_data_vendor",
            "path": str(average_price_index_path.resolve()),
            "sha256": sha256_file(average_price_index_path),
            "controlled_source_audit": average_price_source_audit,
            "start": average_price_index["date"].min().strftime("%Y-%m-%d"),
            "end": average_price_index["date"].max().strftime("%Y-%m-%d"),
            "return_definition": "close(T)/close(T-1 trading record)-1",
            "rank_definition": (
                "1 + count of strictly lower 880003 daily returns within [T-3 calendar years, T]; "
                "rank 1 is the worst decline."
            ),
        },
        "rank_uses_current_and_past_only": True,
        "rank_window_years": RANK_WINDOW_YEARS,
        "minimum_rank_observations": MIN_RANK_OBSERVATIONS,
        "signal_information_timing": (
            "Factor observation date T is descriptive. Because T margin balances are published "
            "before T+1 open, the signal is marked available on the next trading date."
        ),
        "estimated_scenarios_in_formal_signal_table": False,
        "estimated_scenario_count": len(estimated_scenario_dates),
        "estimated_scenario_dates": estimated_scenario_dates,
        "estimated_scenarios_in_combined_display_table": len(estimated_scenario_dates),
        "survivorship_risk": (
            "Historical files ending before the latest date are included when present, but the local vendor "
            "folder cannot prove complete retention of every delisted security."
        ),
        "corporate_action_risk": (
            "Raw local close records can contain adjustment discontinuities; the primary median keeps all valid "
            "returns and the abs-return<=22% median is supplied as a robustness audit."
        ),
        "file_audit": file_audit,
        "signal_audit": signal_audit,
        "estimated_signal_audit": estimated_signal_audit,
        "displayed_signal_count": len(combined_signal_table),
        "average_price_index_replacement_audit": {
            **replacement_audit,
            "estimated_scenario_rows": len(estimated_replacement_comparison),
            "displayed_union_rows": len(replacement_comparison_with_scenarios),
        },
        "latest_day": {
            "date": latest_row["date"].strftime("%Y-%m-%d"),
            "comparable_count": int(latest_row["comparable_count"]),
            "market_return_median_pct": float(latest_row["market_return_median_pct"]),
            "decliners_median_return_pct": float(latest_row["decliners_median_return_pct"]),
            "market_return_median_rank_3y": int(latest_row["market_return_median_rank_3y"]),
            "market_return_median_rank_window_observations": int(
                latest_row["market_return_median_rank_window_observations"]
            ),
            "tdx_average_price_index_close": float(
                latest_row["tdx_average_price_index_close"]
            ),
            "tdx_average_price_index_return_pct": float(
                latest_row["tdx_average_price_index_return_pct"]
            ),
            "tdx_average_price_index_return_rank_3y": int(
                latest_row["tdx_average_price_index_return_rank_3y"]
            ),
            "tdx_average_price_index_return_rank_window_observations": int(
                latest_row["tdx_average_price_index_return_rank_window_observations"]
            ),
        },
        "daily_csv": str(daily_path.resolve()),
        "daily_csv_sha256": sha256_file(daily_path),
        "signal_csv": str(signal_path.resolve()),
        "signal_csv_sha256": sha256_file(signal_path),
        "estimated_signal_csv": str(estimated_signal_path.resolve()),
        "estimated_signal_csv_sha256": sha256_file(estimated_signal_path),
        "combined_signal_csv": str(combined_signal_path.resolve()),
        "combined_signal_csv_sha256": sha256_file(combined_signal_path),
        "replacement_880003_signal_csv": str(replacement_signal_path.resolve()),
        "replacement_880003_signal_csv_sha256": sha256_file(replacement_signal_path),
        "replacement_comparison_csv": str(replacement_comparison_path.resolve()),
        "replacement_comparison_csv_sha256": sha256_file(replacement_comparison_path),
        "replacement_comparison_with_scenarios_csv": str(
            replacement_comparison_scenario_path.resolve()
        ),
        "replacement_comparison_with_scenarios_csv_sha256": sha256_file(
            replacement_comparison_scenario_path
        ),
    }
    audit_path.write_text(
        json.dumps(to_jsonable(audit), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(to_jsonable(audit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
