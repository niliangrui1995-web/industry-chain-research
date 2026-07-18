from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests


DAY_STRUCT = struct.Struct("<IIIIIfII")
INDEX_FILES = {
    "shanghai": "sh000001",
    "sz_comp": "sz399106",
    "chinext": "sz399006",
    "chinext_comp": "sz399102",
}
CNI_DAILY_URL = "https://hq.cnindex.com.cn/market/market/getIndexDailyDataWithDataFormat"
SZSE_MARGIN_URL = "https://www.szse.cn/api/report/ShowReport/data"
HORIZONS = (1, 2, 5, 10, 20, 40)
TRADING_DAYS_PER_YEAR = 244
TERMINAL_SIGNAL_GAP = 10


@dataclass(frozen=True)
class BacktestConfig:
    window_years: int = 3
    rank_threshold: int = 15
    breadth_threshold: float = 80.0
    min_window_observations: int = 600
    min_breadth_count: int = 1000
    min_breadth_coverage: float = 0.70
    start_date: str = "2019-01-01"
    validation_date: str = "2024-01-01"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_day_file(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"TDX day file not found: {path}")
    raw = path.read_bytes()
    if len(raw) % DAY_STRUCT.size:
        raise ValueError(f"Invalid TDX day file size: {path}")

    records: list[tuple[int, float, float]] = []
    for offset in range(0, len(raw), DAY_STRUCT.size):
        date_value, open_value, _, _, close_value, _, _, _ = DAY_STRUCT.unpack_from(raw, offset)
        if date_value and open_value and close_value:
            records.append((date_value, open_value / 100.0, close_value / 100.0))

    frame = pd.DataFrame(records, columns=["date", "open", "close"])
    if frame.empty:
        raise ValueError(f"No valid daily records in {path}")
    frame["date"] = pd.to_datetime(frame["date"].astype(str), format="%Y%m%d", errors="raise")
    frame = frame.drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)
    frame["return_pct"] = frame["close"].pct_change() * 100.0
    return frame


def read_cni_index(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    response = requests.get(
        CNI_DAILY_URL,
        params={
            "indexCode": code,
            "startDate": start_date,
            "endDate": end_date,
            "frequency": "day",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 200:
        raise ValueError(f"CNIndex returned an error for {code}: {payload.get('message')}")
    rows = payload.get("data", {}).get("data", [])
    if not rows:
        raise ValueError(f"CNIndex returned no rows for {code}")
    frame = pd.DataFrame(
        rows,
        columns=[
            "date",
            "_1",
            "high",
            "open",
            "low",
            "close",
            "_2",
            "return_pct",
            "amount",
            "volume",
            "_3",
        ],
    )
    frame = frame[["date", "open", "close", "return_pct"]].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    for column in ("open", "close"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame["return_pct"] = pd.to_numeric(
        frame["return_pct"].astype(str).str.replace("%", "", regex=False), errors="raise"
    )
    return frame.drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)


def load_indexes(
    ht_root: Path,
    *,
    source: str = "cnindex",
    start_date: str = "2014-01-01",
    end_date: str = "2099-12-31",
) -> pd.DataFrame:
    frames: dict[str, pd.DataFrame] = {}
    for label, code in INDEX_FILES.items():
        if source == "cnindex" and label != "shanghai":
            frame = read_cni_index(code[2:], start_date, end_date)
        else:
            market = code[:2]
            path = ht_root / "vipdoc" / market / "lday" / f"{code}.day"
            frame = read_day_file(path)
        frame = frame.rename(
            columns={
                "open": f"{label}_open",
                "close": f"{label}_close",
                "return_pct": f"{label}_return_pct",
            }
        )
        frames[label] = frame

    merged = frames["sz_comp"].merge(
        frames["chinext"], on="date", how="inner", validate="one_to_one"
    )
    merged = merged.merge(frames["chinext_comp"], on="date", how="inner", validate="one_to_one")
    merged = merged.merge(frames["shanghai"], on="date", how="left", validate="one_to_one")
    return merged.sort_values("date").reset_index(drop=True)


def load_margin_history(
    path: Path,
    szse_repair_csv: Path | None = None,
    *,
    trust_audited_snapshot: bool = False,
) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Margin history CSV not found: {path}")
    frame = pd.read_csv(path)
    required = {"date", "sh_margin_y", "sz_margin_y", "total_margin_y"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Margin CSV missing columns: {sorted(missing)}")

    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    for column in ("sh_margin_y", "sz_margin_y", "total_margin_y"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame = frame.drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)

    if "daily_margin_change_pct" in frame.columns:
        supplied = pd.to_numeric(frame["daily_margin_change_pct"], errors="coerce")
        raw_change_pct = frame["total_margin_y"].diff() / frame["total_margin_y"].shift(1) * 100.0
        comparable = supplied.notna() & raw_change_pct.notna()
        max_error = (supplied[comparable] - raw_change_pct[comparable]).abs().max()
        if pd.notna(max_error) and max_error > 1e-8:
            raise ValueError(f"Margin percentage column disagrees with raw balances; max error={max_error}")

    repair_rows_applied = 0
    if szse_repair_csv is not None:
        if not szse_repair_csv.exists():
            raise FileNotFoundError(f"SZSE margin repair CSV not found: {szse_repair_csv}")
        repairs = pd.read_csv(szse_repair_csv)
        required_repairs = {"date", "sz_margin_y", "source", "fetched_at_utc"}
        missing_repairs = required_repairs - set(repairs.columns)
        if missing_repairs:
            raise ValueError(f"SZSE repair CSV missing columns: {sorted(missing_repairs)}")
        repairs = repairs.copy()
        repairs["date"] = pd.to_datetime(repairs["date"], errors="raise")
        repairs["sz_margin_y"] = pd.to_numeric(repairs["sz_margin_y"], errors="raise")
        if not repairs["source"].eq(SZSE_MARGIN_URL).all():
            raise ValueError("SZSE repair CSV contains an unapproved source URL")
        if repairs["date"].duplicated().any():
            raise ValueError("SZSE repair CSV contains duplicate dates")
        unknown_dates = repairs.loc[~repairs["date"].isin(frame["date"]), "date"]
        if not unknown_dates.empty:
            raise ValueError(f"SZSE repair CSV contains dates absent from margin history: {len(unknown_dates)}")
        repair_map = repairs.set_index("date")["sz_margin_y"]
        repair_mask = frame["date"].isin(repair_map.index)
        frame.loc[repair_mask, "sz_margin_y"] = frame.loc[repair_mask, "date"].map(repair_map)
        frame.loc[repair_mask, "total_margin_y"] = (
            frame.loc[repair_mask, "sh_margin_y"] + frame.loc[repair_mask, "sz_margin_y"]
        )
        repair_rows_applied = int(repair_mask.sum())

    previous_balance = frame["total_margin_y"].shift(1)
    frame["margin_change_amount"] = frame["total_margin_y"].diff()
    frame["margin_change_pct"] = frame["margin_change_amount"] / previous_balance * 100.0
    frame["margin_outflow_pct"] = -frame["margin_change_pct"]
    if trust_audited_snapshot:
        frame["sh_margin_y_stale"] = False
        frame["sz_margin_y_stale"] = False
        frame["margin_data_valid"] = True
    else:
        stale_columns: list[str] = []
        for component in ("sh_margin_y", "sz_margin_y"):
            repeated = frame[component].eq(frame[component].shift(1))
            stale_column = f"{component}_stale"
            frame[stale_column] = repeated | repeated.shift(1, fill_value=False)
            stale_columns.append(stale_column)
        frame["margin_data_valid"] = ~frame[stale_columns].any(axis=1)
    frame.attrs["repair_rows_applied"] = repair_rows_applied
    return frame


def is_a_share_day_file(path: Path) -> bool:
    name = path.stem.lower()
    patterns = (
        r"sh(?:600|601|603|605|688|689)\d{3}",
        r"sz(?:000|001|002|003|300|301)\d{3}",
        r"bj(?:43|83|87|88|92)\d{4}",
    )
    return any(re.fullmatch(pattern, name) for pattern in patterns)


def discover_a_share_files(ht_root: Path) -> list[Path]:
    files: list[Path] = []
    for market in ("sh", "sz", "bj"):
        folder = ht_root / "vipdoc" / market / "lday"
        if folder.exists():
            files.extend(path for path in folder.glob("*.day") if is_a_share_day_file(path))
    if not files:
        raise FileNotFoundError(f"No A-share .day files found under {ht_root / 'vipdoc'}")
    return sorted(files)


def build_market_breadth(
    paths: Iterable[Path], start_date: pd.Timestamp, end_date: pd.Timestamp
) -> pd.DataFrame:
    start_value = int(start_date.strftime("%Y%m%d"))
    end_value = int(end_date.strftime("%Y%m%d"))
    totals: dict[int, list[int]] = {}
    for path in paths:
        raw = path.read_bytes()
        if len(raw) % DAY_STRUCT.size:
            continue
        previous_close: int | None = None
        for offset in range(0, len(raw), DAY_STRUCT.size):
            date_value, _, _, _, close_value, _, _, _ = DAY_STRUCT.unpack_from(raw, offset)
            if not date_value or not close_value:
                previous_close = close_value or previous_close
                continue
            if previous_close:
                if start_value <= date_value <= end_value:
                    counts = totals.setdefault(date_value, [0, 0, 0, 0])
                    counts[0] += 1
                    if close_value < previous_close:
                        counts[1] += 1
                    elif close_value > previous_close:
                        counts[2] += 1
                    else:
                        counts[3] += 1
            previous_close = close_value

    rows = [
        (date, values[0], values[1], values[2], values[3])
        for date, values in sorted(totals.items())
    ]
    frame = pd.DataFrame(rows, columns=["date", "breadth_total", "down_count", "up_count", "flat_count"])
    if frame.empty:
        raise ValueError("No market-breadth observations were built")
    frame["date"] = pd.to_datetime(frame["date"].astype(str), format="%Y%m%d", errors="raise")
    frame["down_pct"] = frame["down_count"] / frame["breadth_total"] * 100.0
    reference_count = frame["breadth_total"].rolling(20, min_periods=1).median()
    frame["breadth_coverage"] = frame["breadth_total"] / reference_count.replace(0.0, np.nan)
    return frame


def mark_long_break_eves(frame: pd.DataFrame) -> pd.Series:
    dates = pd.to_datetime(frame["date"])
    gap_to_next = dates.shift(-1) - dates
    return gap_to_next.dt.days.ge(5).fillna(False)


def rolling_extreme_rank(
    dates: pd.Series,
    values: pd.Series,
    years: int,
    *,
    descending: bool,
    eligible: pd.Series | None = None,
    min_observations: int = 600,
) -> pd.Series:
    parsed_dates = pd.to_datetime(dates).reset_index(drop=True)
    numeric = pd.to_numeric(values, errors="coerce").reset_index(drop=True)
    allowed = (
        pd.Series(True, index=numeric.index)
        if eligible is None
        else eligible.fillna(False).astype(bool).reset_index(drop=True)
    )
    ranks = pd.Series(np.nan, index=numeric.index, dtype=float)

    for position, (date, value) in enumerate(zip(parsed_dates, numeric)):
        if pd.isna(value) or not allowed.iloc[position]:
            continue
        start = date - pd.DateOffset(years=years)
        mask = (
            (parsed_dates.iloc[: position + 1] >= start)
            & allowed.iloc[: position + 1]
            & numeric.iloc[: position + 1].notna()
        )
        window = numeric.iloc[: position + 1][mask]
        if len(window) < min_observations or window.index.empty:
            continue
        if parsed_dates.iloc[0] > start:
            continue
        ranks.iloc[position] = 1 + int((window > value).sum() if descending else (window < value).sum())
    return ranks


def add_factor_columns(frame: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
    result = frame.sort_values("date").reset_index(drop=True).copy()
    result["long_break_eve"] = mark_long_break_eves(result)
    breadth_valid = (
        result["breadth_total"].ge(config.min_breadth_count)
        & result["breadth_coverage"].ge(config.min_breadth_coverage)
    )
    result["breadth_valid"] = breadth_valid.fillna(False)
    margin_eligible = ~result["long_break_eve"] & result["margin_data_valid"].fillna(False)

    for label in ("sz_comp", "chinext", "chinext_comp"):
        result[f"{label}_rank"] = rolling_extreme_rank(
            result["date"],
            result[f"{label}_return_pct"],
            config.window_years,
            descending=False,
            min_observations=config.min_window_observations,
        )
    result["margin_outflow_rank"] = rolling_extreme_rank(
        result["date"],
        result["margin_outflow_pct"],
        config.window_years,
        descending=True,
        eligible=margin_eligible,
        min_observations=config.min_window_observations,
    )
    return result


def signal_masks(frame: pd.DataFrame, config: BacktestConfig) -> dict[str, pd.Series]:
    valid = (
        frame["date"].ge(pd.Timestamp(config.start_date))
        & frame["breadth_valid"]
        & frame["margin_data_valid"]
        & ~frame["long_break_eve"]
    )
    margin = frame["margin_outflow_rank"].le(config.rank_threshold)
    breadth = frame["down_pct"].ge(config.breadth_threshold)
    sz = frame["sz_comp_rank"].le(config.rank_threshold)
    chinext = frame["chinext_rank"].le(config.rank_threshold)
    chinext_comp = frame["chinext_comp_rank"].le(config.rank_threshold)
    return {
        "sz_index_only": valid & sz,
        "sz_plus_margin": valid & sz & margin,
        "sz_triple": valid & sz & margin & breadth,
        "chinext_triple": valid & chinext & margin & breadth,
        "chinext_comp_triple": valid & chinext_comp & margin & breadth,
        "dual_triple": valid & sz & chinext & margin & breadth,
    }


def add_forward_returns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for label in ("shanghai", "sz_comp", "chinext", "chinext_comp"):
        close = result[f"{label}_close"]
        next_open = result[f"{label}_open"].shift(-1)
        for horizon in HORIZONS:
            exit_close = close.shift(-horizon)
            result[f"{label}_cc_t{horizon}"] = (exit_close / close - 1.0) * 100.0
            result[f"{label}_next_open_t{horizon}"] = (exit_close / next_open - 1.0) * 100.0
    return result


def wilson_interval(wins: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (math.nan, math.nan)
    proportion = wins / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    margin = z * math.sqrt(
        proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total)
    ) / denominator
    return ((centre - margin) * 100.0, (centre + margin) * 100.0)


def summarize_values(values: pd.Series, benchmark: pd.Series) -> dict[str, float | int | None]:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    base = pd.to_numeric(benchmark, errors="coerce").dropna()
    if clean.empty:
        return {"n": 0, "win_rate": None, "mean": None, "median": None, "min": None, "max": None}
    wins = int(clean.gt(0).sum())
    low, high = wilson_interval(wins, len(clean))
    std = float(clean.std(ddof=1)) if len(clean) > 1 else math.nan
    t_stat = float(clean.mean() / (std / math.sqrt(len(clean)))) if len(clean) > 1 and std > 0 else math.nan
    return {
        "n": int(len(clean)),
        "win_rate": round(wins / len(clean) * 100.0, 4),
        "win_rate_ci_low": round(low, 4),
        "win_rate_ci_high": round(high, 4),
        "mean": round(float(clean.mean()), 4),
        "median": round(float(clean.median()), 4),
        "min": round(float(clean.min()), 4),
        "max": round(float(clean.max()), 4),
        "t_stat": None if math.isnan(t_stat) else round(t_stat, 4),
        "benchmark_win_rate": None if base.empty else round(float(base.gt(0).mean() * 100.0), 4),
        "benchmark_mean": None if base.empty else round(float(base.mean()), 4),
    }


def summarize_mask(
    frame: pd.DataFrame,
    mask: pd.Series,
    config: BacktestConfig,
) -> dict[str, object]:
    output: dict[str, object] = {"signal_count": int(mask.sum())}
    eligible = (
        frame["date"].ge(pd.Timestamp(config.start_date))
        & frame["breadth_valid"]
        & frame["margin_data_valid"]
        & ~frame["long_break_eve"]
    )
    for label in ("shanghai", "sz_comp", "chinext", "chinext_comp"):
        label_output: dict[str, object] = {}
        for entry in ("cc", "next_open"):
            horizon_output: dict[str, object] = {}
            for horizon in HORIZONS:
                column = f"{label}_{entry}_t{horizon}"
                horizon_output[f"t{horizon}"] = summarize_values(
                    frame.loc[mask, column], frame.loc[eligible, column]
                )
            label_output[entry] = horizon_output
        output[label] = label_output
    return output


def sample_periods(frame: pd.DataFrame, mask: pd.Series, config: BacktestConfig) -> dict[str, pd.Series]:
    split = pd.Timestamp(config.validation_date)
    terminal = terminal_signal_mask(mask, TERMINAL_SIGNAL_GAP)
    return {
        "all_signals": mask,
        "terminal_10d": terminal,
        "pre_validation": mask & frame["date"].lt(split),
        "post_validation": mask & frame["date"].ge(split),
        "terminal_10d_pre_validation": terminal & frame["date"].lt(split),
        "terminal_10d_post_validation": terminal & frame["date"].ge(split),
    }


def terminal_signal_mask(mask: pd.Series, max_gap: int = TERMINAL_SIGNAL_GAP) -> pd.Series:
    if max_gap < 0:
        raise ValueError("Terminal signal gap must be non-negative")
    values = mask.fillna(False).astype(bool).to_numpy()
    positions = np.flatnonzero(values)
    terminal = pd.Series(False, index=mask.index, dtype=bool)
    if not len(positions):
        return terminal
    keep = np.ones(len(positions), dtype=bool)
    if len(positions) > 1:
        keep[:-1] = np.diff(positions) > max_gap
    terminal.iloc[positions[keep]] = True
    return terminal


def signal_table(frame: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    columns = [
        "date",
        "sz_comp_close",
        "chinext_close",
        "chinext_comp_close",
        "sz_comp_return_pct",
        "chinext_return_pct",
        "chinext_comp_return_pct",
        "margin_change_amount",
        "margin_outflow_pct",
        "sz_comp_rank",
        "chinext_rank",
        "chinext_comp_rank",
        "margin_outflow_rank",
        "margin_data_valid",
        "breadth_total",
        "breadth_coverage",
        "down_pct",
    ]
    for label in ("shanghai", "sz_comp", "chinext", "chinext_comp"):
        for horizon in HORIZONS:
            columns.extend([f"{label}_cc_t{horizon}", f"{label}_next_open_t{horizon}"])
    return frame.loc[mask, columns].copy()


def sensitivity_analysis(base: pd.DataFrame, config: BacktestConfig) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for years in (2, 3, 5):
        configured = BacktestConfig(
            window_years=years,
            rank_threshold=config.rank_threshold,
            breadth_threshold=config.breadth_threshold,
            min_window_observations=max(400, int(TRADING_DAYS_PER_YEAR * years * 0.80)),
            min_breadth_count=config.min_breadth_count,
            min_breadth_coverage=config.min_breadth_coverage,
            start_date=config.start_date,
            validation_date=config.validation_date,
        )
        factored = add_factor_columns(base, configured)
        for rank in (10, 15, 20, 25):
            for breadth in (75.0, 80.0, 85.0, 90.0):
                trial = BacktestConfig(
                    **{
                        **configured.__dict__,
                        "rank_threshold": rank,
                        "breadth_threshold": breadth,
                    }
                )
                masks = signal_masks(factored, trial)
                comparisons = (
                    ("sz_triple", "399106", "sz_comp"),
                    ("chinext_triple", "399006", "chinext"),
                    ("chinext_comp_triple", "399102", "chinext_comp"),
                )
                for signal_name, index_code, return_label in comparisons:
                    mask = terminal_signal_mask(masks[signal_name], TERMINAL_SIGNAL_GAP)
                    values = factored.loc[mask, f"{return_label}_cc_t2"].dropna()
                    results.append(
                        {
                            "signal": signal_name,
                            "index_code": index_code,
                            "window_years": years,
                            "rank_threshold": rank,
                            "breadth_threshold": breadth,
                            "sample_policy": "terminal_10d",
                            "n": int(len(values)),
                            "t2_from_t_close_win_rate": (
                                None if values.empty else round(float(values.gt(0).mean() * 100.0), 4)
                            ),
                            "t2_from_t_close_mean": (
                                None if values.empty else round(float(values.mean()), 4)
                            ),
                        }
                    )
    return results


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


def write_outputs(
    output_dir: Path,
    frame: pd.DataFrame,
    masks: dict[str, pd.Series],
    summaries: dict[str, object],
    sensitivity: list[dict[str, object]],
    metadata: dict[str, object],
    config: BacktestConfig,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": metadata,
        "config": config.__dict__,
        "summaries": summaries,
        "sensitivity": sensitivity,
    }
    (output_dir / "backtest_results.json").write_text(
        json.dumps(to_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for name, mask in masks.items():
        signal_table(frame, mask).to_csv(output_dir / f"signals_{name}.csv", index=False, encoding="utf-8-sig")
        terminal = terminal_signal_mask(mask, TERMINAL_SIGNAL_GAP)
        signal_table(frame, terminal).to_csv(
            output_dir / f"signals_{name}_terminal_10d.csv",
            index=False,
            encoding="utf-8-sig",
        )
    pd.DataFrame(sensitivity).to_csv(output_dir / "sensitivity.csv", index=False, encoding="utf-8-sig")
    panel_columns = [
        "date",
        "sz_comp_close",
        "chinext_close",
        "chinext_comp_close",
        "sz_comp_return_pct",
        "chinext_return_pct",
        "chinext_comp_return_pct",
        "margin_change_amount",
        "margin_outflow_pct",
        "sz_comp_rank",
        "chinext_rank",
        "chinext_comp_rank",
        "margin_outflow_rank",
        "margin_data_valid",
        "breadth_total",
        "breadth_coverage",
        "down_pct",
        "breadth_valid",
        "long_break_eve",
    ]
    frame[panel_columns].to_csv(output_dir / "factor_panel.csv", index=False, encoding="utf-8-sig")


def run_backtest(
    margin_csv: Path,
    ht_root: Path,
    config: BacktestConfig,
    *,
    index_source: str = "cnindex",
    szse_repair_csv: Path | None = None,
    margin_audit_json: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.Series], dict[str, object], list[dict[str, object]], dict[str, object]]:
    if margin_audit_json is None:
        raise ValueError("A verified margin audit JSON is required for backtesting")
    index_start = (pd.Timestamp(config.start_date) - pd.DateOffset(years=max(5, config.window_years))).strftime("%Y-%m-%d")
    indexes = add_forward_returns(
        load_indexes(
            ht_root,
            source=index_source,
            start_date=index_start,
            end_date=pd.Timestamp.today().strftime("%Y-%m-%d"),
        )
    )
    audit_metadata: dict[str, object] | None = None
    if margin_audit_json is not None:
        if szse_repair_csv is not None:
            raise ValueError("Do not combine an audited snapshot with a repair overlay")
        if not margin_audit_json.exists():
            raise FileNotFoundError(f"Margin audit JSON not found: {margin_audit_json}")
        audit_metadata = json.loads(margin_audit_json.read_text(encoding="utf-8"))
        if audit_metadata.get("verified_snapshot_complete") is not True:
            raise ValueError("Margin audit report did not pass the verified snapshot gate")
        expected_hash = audit_metadata.get("verified_margin_balances_sha256")
        if expected_hash != sha256_file(margin_csv):
            raise ValueError("Margin CSV hash does not match the verified audit report")
    margin = load_margin_history(
        margin_csv,
        szse_repair_csv,
        trust_audited_snapshot=audit_metadata is not None,
    )
    if audit_metadata is not None:
        if int(audit_metadata.get("verified_rows", -1)) != len(margin):
            raise ValueError("Margin row count does not match the verified audit report")
        if audit_metadata.get("verified_start") != margin["date"].min().strftime("%Y-%m-%d"):
            raise ValueError("Margin start date does not match the verified audit report")
        if audit_metadata.get("verified_end") != margin["date"].max().strftime("%Y-%m-%d"):
            raise ValueError("Margin end date does not match the verified audit report")
    repair_rows_applied = int(margin.attrs.get("repair_rows_applied", 0))
    start = max(pd.Timestamp(config.start_date) - pd.DateOffset(years=max(5, config.window_years)), indexes["date"].min())
    end = min(indexes["date"].max(), margin["date"].max())
    breadth_files = discover_a_share_files(ht_root)
    breadth = build_market_breadth(breadth_files, start, end)

    base = indexes.merge(margin, on="date", how="inner", validate="one_to_one")
    base = base.merge(breadth, on="date", how="left", validate="one_to_one")
    base = base.sort_values("date").reset_index(drop=True)
    factored = add_factor_columns(base, config)
    masks = signal_masks(factored, config)

    summaries: dict[str, object] = {}
    for name, mask in masks.items():
        summaries[name] = {
            period: summarize_mask(factored, period_mask, config)
            for period, period_mask in sample_periods(factored, mask, config).items()
        }
    sensitivity = sensitivity_analysis(base, config)
    metadata = {
        "warmup_data_start": factored["date"].min(),
        "evaluation_start": pd.Timestamp(config.start_date),
        "data_end": factored["date"].max(),
        "margin_csv": str(margin_csv.resolve()),
        "margin_csv_sha256": sha256_file(margin_csv),
        "szse_repair_csv": None if szse_repair_csv is None else str(szse_repair_csv.resolve()),
        "szse_repair_csv_sha256": None if szse_repair_csv is None else sha256_file(szse_repair_csv),
        "szse_repair_rows_applied": repair_rows_applied,
        "margin_audit_json": None if margin_audit_json is None else str(margin_audit_json.resolve()),
        "margin_audit_json_sha256": None if margin_audit_json is None else sha256_file(margin_audit_json),
        "margin_source_status": (
            "eastmoney_snapshot_validated_with_exchange_checks"
            if audit_metadata is not None
            else (
                "local_snapshot_with_official_szse_repairs"
                if szse_repair_csv is not None
                else "partially_verified_local_snapshot_with_detected_stale_intervals"
            )
        ),
        "invalid_margin_rows": int((~factored["margin_data_valid"]).sum()),
        "ht_root": str(ht_root.resolve()),
        "factor_index_source": index_source,
        "factor_index_codes": {
            "sz_comp": "399106",
            "chinext": "399006",
            "chinext_comp": "399102",
        },
        "factor_index_endpoint": CNI_DAILY_URL if index_source == "cnindex" else str(ht_root.resolve()),
        "breadth_source": "current local TDX A-share files; traded-stock denominator",
        "breadth_survivorship_risk": True,
        "breadth_files": len(breadth_files),
        "latest_breadth_count": int(breadth.iloc[-1]["breadth_total"]),
        "reported_return_basis": "signal-day close to T+N close; retrospective and not executable",
        "signal_availability": (
            "margin balance is available only after the signal-day close; "
            "T-close returns contain signal-availability look-ahead"
        ),
        "implementation_reference": (
            "next-open returns remain in raw outputs only as an executable comparison"
        ),
        "signal_sample_policy": (
            "raw signal files retain every qualifying date; forward-outcome headline uses the final signal "
            "in each chained cluster whose adjacent signal positions differ by at most 10 trading days"
        ),
        "terminal_signal_gap_trading_days": TERMINAL_SIGNAL_GAP,
        "terminal_selection_lookahead": (
            "the final signal in a 10-day cluster is identifiable only after observing subsequent signal dates; "
            "terminal_10d is retrospective episode analysis, not a T-close executable strategy"
        ),
        "dependence_warning": (
            "consecutive signals and forward-return windows can overlap; observations are not independent"
        ),
        "causal_boundary": "margin balance decline is a deleveraging proxy, not proof of forced liquidation",
    }
    return factored, masks, summaries, sensitivity, metadata


def build_parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parents[4]
    parser = argparse.ArgumentParser(description="Auditable A-share leverage-deleveraging factor backtest")
    parser.add_argument("--margin-csv", type=Path, required=True)
    parser.add_argument("--szse-repair-csv", type=Path)
    parser.add_argument("--margin-audit-json", type=Path, required=True)
    parser.add_argument("--ht-root", type=Path, default=Path(r"D:\HT"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--index-source", choices=["cnindex", "tdx"], default="cnindex")
    parser.add_argument("--window-years", type=int, default=3)
    parser.add_argument("--rank-threshold", type=int, default=15)
    parser.add_argument("--breadth-threshold", type=float, default=80.0)
    parser.add_argument("--min-window-observations", type=int, default=600)
    parser.add_argument("--min-breadth-count", type=int, default=1000)
    parser.add_argument("--min-breadth-coverage", type=float, default=0.70)
    parser.add_argument("--start-date", default="2019-01-01")
    parser.add_argument("--validation-date", default="2024-01-01")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = BacktestConfig(
        window_years=args.window_years,
        rank_threshold=args.rank_threshold,
        breadth_threshold=args.breadth_threshold,
        min_window_observations=args.min_window_observations,
        min_breadth_count=args.min_breadth_count,
        min_breadth_coverage=args.min_breadth_coverage,
        start_date=args.start_date,
        validation_date=args.validation_date,
    )
    frame, masks, summaries, sensitivity, metadata = run_backtest(
        args.margin_csv,
        args.ht_root,
        config,
        index_source=args.index_source,
        szse_repair_csv=args.szse_repair_csv,
        margin_audit_json=args.margin_audit_json,
    )
    if args.output_dir:
        write_outputs(args.output_dir, frame, masks, summaries, sensitivity, metadata, config)
    concise = {
        "metadata": metadata,
        "config": config.__dict__,
        "signal_counts": {name: int(mask.sum()) for name, mask in masks.items()},
        "triple_comparison": {
            name: summaries[name]
            for name in ("sz_triple", "chinext_triple", "chinext_comp_triple")
        },
    }
    print(json.dumps(to_jsonable(concise), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
