#!/usr/bin/env python3
"""Leakage-controlled, project-local A-share baselines for Kronos evaluation."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import struct
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from kronos_a_share_dataset import (
    DatasetBuildError,
    _event_adjustment_factor,
    load_corporate_actions,
    load_membership,
    realized_total_log_return,
)


BASELINE_SCHEMA = "kronos-a-share-alpha158-lightgbm-v4"
PROVIDER_SCHEMA = "kronos-a-share-qlib-provider-v4"
COMPARISON_SCHEMA = "kronos-a-share-baseline-comparison-v2"
EVALUATION_COMPANION_SCHEMA = "kronos-a-share-baseline-bundle-v3"
EXECUTION_AUDIT_SCHEMA = "kronos-a-share-execution-audit-v2"
LABEL_EXPRESSION = "$label_excess_10d"
LABEL_COLUMN = "label_excess_10d"
LABEL_UNIT = "natural_log_return"
LABEL_CONTRACT = (
    "realized_total_log_return(stock_origin, stock_target, PIT_corporate_actions) - "
    "ln(csi800_close_target / csi800_close_origin)"
)
REQUIRED_SPLITS = (
    "train",
    "validation",
    "development_test",
    "locked_retrospective",
)
NAIVE_BASELINES = ("last_value", "momentum", "reversal")
EXTERNAL_BASELINES = ("zero_shot_kronos", "head_only", "alpha158_lightgbm")
REQUIRED_BASELINES = NAIVE_BASELINES + EXTERNAL_BASELINES
COMPANION_SCORE_COLUMNS = (
    "zero_shot_score",
    "head_only_score",
    "last_value_score",
    "drift_score",
    "momentum_score",
    "reversal_score",
    "alpha158_score",
)
EXTERNAL_SCORE_COLUMNS = ("zero_shot_score", "head_only_score", "alpha158_score")
DAY_RECORD = struct.Struct("<IIIIIfII")
FEATURE_COLUMNS = ("open", "high", "low", "close", "vwap", "volume")
TICKER_PATTERN = re.compile(r"^(?:sh|sz|bj)\d{6}$")
FORMAL_MIN_CROSS_SECTION = 100
FORMAL_MIN_COVERAGE_RATIO = 0.95


class BaselineError(RuntimeError):
    """Raised when a provider, split, label, or comparison contract is invalid."""


def ensure_within(path: Path, root: Path) -> Path:
    candidate = path.resolve()
    boundary = root.resolve()
    try:
        candidate.relative_to(boundary)
    except ValueError as exc:
        raise BaselineError(f"path_outside_training_root: {candidate}") from exc
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f".{path.name}.pending-{os.getpid()}")
    with pending.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, path)


def _as_date(value: Any, *, field: str) -> pd.Timestamp:
    text = str(value).strip()
    if re.fullmatch(r"\d{8}(?:\.0)?", text):
        text = text[:8]
        parsed = pd.to_datetime(text, format="%Y%m%d", errors="coerce")
    else:
        parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise BaselineError(f"{field} 日期无效：{value}")
    return pd.Timestamp(parsed).normalize()


def _normalize_ticker(value: Any) -> str:
    ticker = str(value).strip().lower()
    match = re.fullmatch(r"(\d{6})\.(sh|sz|bj)", ticker)
    if match:
        ticker = f"{match.group(2)}{match.group(1)}"
    if not TICKER_PATTERN.fullmatch(ticker):
        raise BaselineError(f"ticker 格式无效：{value}")
    return ticker


def validate_segments(segments: Mapping[str, list[str]]) -> dict[str, list[str]]:
    missing = sorted(set(REQUIRED_SPLITS) - set(segments))
    extra = sorted(set(segments) - set(REQUIRED_SPLITS))
    if missing or extra:
        raise BaselineError(f"Qlib baseline split 合同不完整：missing={missing}, extra={extra}")
    normalized: dict[str, list[str]] = {}
    previous_end: pd.Timestamp | None = None
    for name in REQUIRED_SPLITS:
        interval = segments[name]
        if not isinstance(interval, (list, tuple)) or len(interval) != 2:
            raise BaselineError(f"split {name} 必须是 [start, end]")
        start = _as_date(interval[0], field=f"split {name} start")
        end = _as_date(interval[1], field=f"split {name} end")
        if start > end:
            raise BaselineError(f"split {name} 起止日期倒置")
        if previous_end is not None and start <= previous_end:
            raise BaselineError(f"split 重叠或顺序错误：{name}")
        normalized[name] = [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
        previous_end = end
    return normalized


def validate_sample_index_contract(
    sample_index: pd.DataFrame,
    segments: Mapping[str, list[str]],
) -> pd.DataFrame:
    """Validate exact labels and prove every origin/target remains in one split."""

    normalized_segments = validate_segments(segments)
    required = {"sample_id", "ticker", "origin_date", "target_date", "split", LABEL_COLUMN}
    missing = sorted(required - set(sample_index.columns))
    if missing:
        raise BaselineError(f"sample_index 缺少字段：{missing}")
    if sample_index.empty:
        raise BaselineError("sample_index 为空")
    frame = sample_index.copy()
    numeric_sample_ids = pd.to_numeric(frame["sample_id"], errors="coerce")
    sample_id_values = numeric_sample_ids.to_numpy(dtype=float)
    if (
        not np.isfinite(sample_id_values).all()
        or not np.equal(sample_id_values, np.floor(sample_id_values)).all()
    ):
        raise BaselineError("sample_index sample_id 必须为整数")
    try:
        sample_ids = numeric_sample_ids.to_numpy(dtype=np.int64)
    except (OverflowError, ValueError) as exc:
        raise BaselineError("sample_index sample_id 超出 int64 范围") from exc
    if not np.array_equal(sample_ids, np.arange(len(frame), dtype=np.int64)):
        raise BaselineError("sample_index sample_id 必须从0连续递增并保持原始全序")
    frame["sample_id"] = sample_ids
    frame["ticker"] = frame["ticker"].map(_normalize_ticker)
    frame["origin_date"] = [
        _as_date(value, field="origin_date") for value in frame["origin_date"]
    ]
    frame["target_date"] = [
        _as_date(value, field="target_date") for value in frame["target_date"]
    ]
    frame[LABEL_COLUMN] = pd.to_numeric(frame[LABEL_COLUMN], errors="coerce")
    if not np.isfinite(frame[LABEL_COLUMN].to_numpy(dtype=float)).all():
        raise BaselineError(f"sample_index {LABEL_COLUMN} 包含 NaN/Inf")
    if frame.duplicated(["ticker", "origin_date"]).any():
        raise BaselineError("sample_index 存在重复 ticker/origin_date")
    for row in frame.itertuples(index=False):
        split = str(row.split)
        if split not in normalized_segments:
            raise BaselineError(f"sample_index split 无效：{split}")
        start, end = map(pd.Timestamp, normalized_segments[split])
        origin = pd.Timestamp(row.origin_date)
        target = pd.Timestamp(row.target_date)
        if not (start <= origin < target <= end):
            raise BaselineError(
                f"label_crosses_split: {row.ticker} {origin.date()}->{target.date()} split={split}"
            )
        if hasattr(row, "window_start_date"):
            window_start = _as_date(row.window_start_date, field="window_start_date")
            if window_start < start or window_start > origin:
                raise BaselineError(f"history_crosses_split: {row.ticker} split={split}")
    return frame


def _read_sample_index(
    sample_index_path: Path,
    training_root: Path,
    segments: Mapping[str, list[str]],
) -> tuple[Path, pd.DataFrame]:
    path = ensure_within(sample_index_path, training_root)
    if not path.is_file():
        raise BaselineError(f"sample_index 不存在：{path}")
    return path, validate_sample_index_contract(pd.read_csv(path), segments)


def _read_tdx_day(path: Path, ticker: str) -> pd.DataFrame:
    payload = path.read_bytes()
    if not payload or len(payload) % DAY_RECORD.size:
        raise BaselineError(f"TDX .day 长度不是32字节整数倍：{path}")
    rows: list[tuple[Any, ...]] = []
    previous = 0
    for offset in range(0, len(payload), DAY_RECORD.size):
        date, open_i, high_i, low_i, close_i, amount, volume, _ = DAY_RECORD.unpack_from(
            payload, offset
        )
        if date <= previous:
            raise BaselineError(f"TDX .day 日期非严格递增：{path}")
        previous = date
        values = [open_i / 100.0, high_i / 100.0, low_i / 100.0, close_i / 100.0]
        if min(values) <= 0 or values[1] < max(values[0], values[3]) or values[2] > min(
            values[0], values[3]
        ):
            raise BaselineError(f"TDX .day OHLC 无效：{path} date={date}")
        rows.append(
            (
                pd.to_datetime(str(date), format="%Y%m%d"),
                ticker,
                *values,
                float(volume),
                float(amount),
            )
        )
    return pd.DataFrame(
        rows,
        columns=["trade_date", "ticker", "open", "high", "low", "close", "volume", "amount"],
    )


def _read_normalized_source(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(path)
    elif suffix in {".parquet", ".pq"}:
        try:
            frame = pd.read_parquet(path)
        except ImportError as exc:
            raise BaselineError("读取 Parquet 需要 pyarrow") from exc
    else:
        raise BaselineError("normalized source 仅支持 .csv/.parquet")
    if "trade_date" not in frame and "date" in frame:
        frame = frame.rename(columns={"date": "trade_date"})
    required = {"trade_date", "ticker", "open", "high", "low", "close"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise BaselineError(f"normalized source 缺少字段：{missing}")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].map(_normalize_ticker)
    frame["trade_date"] = [
        _as_date(value, field="trade_date") for value in frame["trade_date"]
    ]
    for column in ("open", "high", "low", "close"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for column in ("volume", "amount"):
        if column not in frame:
            frame[column] = 0.0
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _load_market_source(
    source_path: Path,
    sample_index: pd.DataFrame,
    training_root: Path,
    benchmark_ticker: str,
) -> tuple[pd.DataFrame, list[Path], str, dict[str, str]]:
    source = ensure_within(source_path, training_root)
    if source.is_file():
        hashes = {str(source): sha256_file(source)}
        frame = _read_normalized_source(source)
        if sha256_file(source) != hashes[str(source)]:
            raise BaselineError("source_hash_drift: 读取 normalized source 期间文件发生变化")
        return frame, [source], "normalized", hashes
    if not source.is_dir():
        raise BaselineError(f"项目内 normalized/raw 快照不存在：{source}")
    if "day_file" not in sample_index:
        raise BaselineError("raw snapshot 模式要求 sample_index.day_file")
    paths_by_ticker: dict[str, Path] = {}
    for row in sample_index[["ticker", "day_file"]].drop_duplicates().itertuples(index=False):
        ticker = _normalize_ticker(row.ticker)
        day_path = ensure_within(Path(str(row.day_file)), training_root)
        ensure_within(day_path, source)
        if not day_path.is_file():
            raise BaselineError(f"sample_index.day_file 不存在：{day_path}")
        previous = paths_by_ticker.setdefault(ticker, day_path)
        if previous != day_path:
            raise BaselineError(f"ticker 对应多个 day_file：{ticker}")
    benchmark_matches = sorted(source.rglob(f"{benchmark_ticker}.day"))
    if len(benchmark_matches) != 1:
        raise BaselineError(f"raw snapshot 必须且只能包含一个 {benchmark_ticker}.day")
    paths_by_ticker[benchmark_ticker] = benchmark_matches[0].resolve()
    source_files = list(paths_by_ticker.values())
    hashes = {str(path.resolve()): sha256_file(path) for path in source_files}
    frames = [_read_tdx_day(path, ticker) for ticker, path in sorted(paths_by_ticker.items())]
    if any(sha256_file(path) != hashes[str(path.resolve())] for path in source_files):
        raise BaselineError("source_hash_drift: 读取 raw snapshot 期间文件发生变化")
    return pd.concat(frames, ignore_index=True), source_files, "tdx_raw_snapshot", hashes


def _validate_market_frame(frame: pd.DataFrame, benchmark_ticker: str) -> pd.DataFrame:
    result = frame.copy()
    required = {"trade_date", "ticker", "open", "high", "low", "close", "volume", "amount"}
    missing = sorted(required - set(result.columns))
    if missing:
        raise BaselineError(f"market source 缺少字段：{missing}")
    if result.duplicated(["ticker", "trade_date"]).any():
        raise BaselineError("market source 存在重复 ticker/trade_date")
    numeric = ["open", "high", "low", "close", "volume", "amount"]
    if not np.isfinite(result[numeric].to_numpy(dtype=float)).all():
        raise BaselineError("market source 包含 NaN/Inf")
    if (result[["open", "high", "low", "close"]] <= 0).any(axis=None):
        raise BaselineError("market source 包含非正价格")
    invalid_ohlc = (
        (result["high"] < result[["open", "close"]].max(axis=1))
        | (result["low"] > result[["open", "close"]].min(axis=1))
        | (result["high"] < result["low"])
    )
    if invalid_ohlc.any() or (result[["volume", "amount"]] < 0).any(axis=None):
        raise BaselineError("market source OHLC/成交量额无效")
    if benchmark_ticker not in set(result["ticker"]):
        raise BaselineError(f"market source 缺少 CSI800 基准 {benchmark_ticker}")
    result["vwap"] = result["close"]
    active = (result["volume"] > 0) & (result["amount"] > 0)
    computed_vwap = result.loc[active, "amount"] / result.loc[active, "volume"]
    sane = computed_vwap > 0
    result.loc[computed_vwap.index[sane], "vwap"] = computed_vwap[sane]
    return result.sort_values(["ticker", "trade_date"]).reset_index(drop=True)


def _causal_model_price_market(
    market: pd.DataFrame,
    corporate_actions: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    """Create a PIT forward-adjusted price level without future action use.

    At an effective ex-date the current and later OHLC/VWAP values are divided
    by the same factor used by the dataset's backward-adjusted window.  The two
    representations differ only by a constant inside any as-of window, while
    this representation can be materialized once for Qlib.
    """

    adjusted = market.copy()
    applied = 0
    price_columns = ("open", "high", "low", "close", "vwap")
    for ticker, positions in adjusted.groupby("ticker", sort=False).groups.items():
        position_array = np.asarray(list(positions), dtype=np.int64)
        stock = adjusted.loc[position_array].sort_values("trade_date").copy()
        stock["date"] = stock["trade_date"].dt.strftime("%Y%m%d").astype(np.int64)
        dates = stock["trade_date"].to_numpy(dtype="datetime64[ns]")
        scale = np.ones(len(stock), dtype=np.float64)
        events = corporate_actions[corporate_actions["ticker"] == ticker].sort_values(
            ["ex_date", "announcement_date"]
        )
        for event in events.itertuples(index=False):
            ex_date = pd.Timestamp(event.ex_date).normalize()
            announcement = pd.Timestamp(event.announcement_date).normalize()
            if ex_date > pd.Timestamp(stock["trade_date"].max()):
                continue
            if announcement > ex_date:
                raise BaselineError(
                    f"corporate_action_non_pit: {ticker} {ex_date.date()} "
                    f"announcement={announcement.date()}"
                )
            factor = _event_adjustment_factor(stock, event, ticker)
            effective = dates >= np.datetime64(ex_date)
            if bool(effective.any()):
                scale[effective] /= factor
                applied += 1
        stock.loc[:, price_columns] = (
            stock.loc[:, price_columns].to_numpy(dtype=np.float64)
            * scale[:, np.newaxis]
        )
        adjusted.loc[stock.index, price_columns] = stock.loc[:, price_columns]
    if not np.isfinite(adjusted[list(price_columns)].to_numpy(dtype=float)).all():
        raise BaselineError("model_price_adjusted 包含 NaN/Inf")
    return adjusted.sort_values(["ticker", "trade_date"]).reset_index(drop=True), applied


def _audit_labels_and_build_naive_scores(
    sample_index: pd.DataFrame,
    raw_market: pd.DataFrame,
    model_market: pd.DataFrame,
    corporate_actions: pd.DataFrame,
    benchmark_ticker: str,
    segments: Mapping[str, list[str]],
    horizon: int,
    momentum_lookback: int,
    lookback: int,
    purge_days: int,
) -> pd.DataFrame:
    grouped = {
        ticker: group.sort_values("trade_date").reset_index(drop=True)
        for ticker, group in raw_market.groupby("ticker", sort=False)
    }
    adjusted_grouped = {
        ticker: group.sort_values("trade_date").reset_index(drop=True)
        for ticker, group in model_market.groupby("ticker", sort=False)
    }
    benchmark = grouped[benchmark_ticker]
    benchmark_positions = {
        date: index for index, date in enumerate(benchmark["trade_date"].tolist())
    }
    benchmark_close = benchmark.set_index("trade_date")["close"]
    label_frames: dict[str, pd.DataFrame] = {}
    actions_by_ticker = {
        ticker: group.reset_index(drop=True)
        for ticker, group in corporate_actions.groupby("ticker", sort=False)
    }
    empty_actions = corporate_actions.iloc[0:0].copy()
    records: list[dict[str, Any]] = []
    for row in sample_index.itertuples(index=False):
        ticker = row.ticker
        stock = grouped.get(ticker)
        adjusted_stock = adjusted_grouped.get(ticker)
        if stock is None or adjusted_stock is None:
            raise BaselineError(f"market source 缺少样本证券：{ticker}")
        stock_positions = {date: index for index, date in enumerate(stock["trade_date"].tolist())}
        origin = pd.Timestamp(row.origin_date)
        target = pd.Timestamp(row.target_date)
        stock_origin = stock_positions.get(origin)
        stock_target = stock_positions.get(target)
        bench_origin = benchmark_positions.get(origin)
        bench_target = benchmark_positions.get(target)
        if None in (stock_origin, stock_target, bench_origin, bench_target):
            raise BaselineError(f"label 日期缺失：{ticker} {origin.date()}->{target.date()}")
        if stock_target - stock_origin != horizon or bench_target - bench_origin != horizon:
            raise BaselineError(f"label_horizon_not_{horizon}_bars: {ticker} {origin.date()}")
        split_start, split_end = map(pd.Timestamp, segments[str(row.split)])
        split_calendar = benchmark[
            (benchmark["trade_date"] >= split_start) & (benchmark["trade_date"] <= split_end)
        ]["trade_date"].tolist()
        if len(split_calendar) <= purge_days or origin > split_calendar[-purge_days - 1]:
            raise BaselineError(f"purge_violation: {ticker} {origin.date()} split={row.split}")
        if stock_origin < lookback - 1 or bench_origin < lookback - 1:
            raise BaselineError(f"lookback 历史不足：{ticker} {origin.date()}")
        if (
            pd.Timestamp(stock.iloc[stock_origin - lookback + 1]["trade_date"]) < split_start
            or pd.Timestamp(benchmark.iloc[bench_origin - lookback + 1]["trade_date"]) < split_start
        ):
            raise BaselineError(f"history_crosses_split: {ticker} split={row.split}")
        if stock_origin < momentum_lookback:
            raise BaselineError(f"momentum 历史不足：{ticker} {origin.date()}")
        benchmark_origin_close = float(benchmark_close.loc[origin])
        benchmark_target_close = float(benchmark_close.loc[target])
        stock_for_label = label_frames.get(ticker)
        if stock_for_label is None:
            stock_for_label = stock.copy()
            stock_for_label["date"] = stock_for_label["trade_date"].dt.strftime(
                "%Y%m%d"
            ).astype(np.int64)
            label_frames[ticker] = stock_for_label
        try:
            stock_return = realized_total_log_return(
                stock_for_label,
                origin_index=int(stock_origin),
                target_index=int(stock_target),
                corporate_actions=actions_by_ticker.get(ticker, empty_actions),
                ticker=ticker,
            )
        except DatasetBuildError as exc:
            raise BaselineError(
                f"corporate_action_label_error: {ticker} {origin.date()}->{target.date()}: {exc}"
            ) from exc
        expected = stock_return - math.log(
            benchmark_target_close / benchmark_origin_close
        )
        if not math.isclose(float(row.label_excess_10d), expected, rel_tol=1e-9, abs_tol=1e-8):
            raise BaselineError(
                f"label_mismatch: {ticker} {origin.date()} sample={row.label_excess_10d} expected={expected}"
            )
        momentum = math.log(
            float(adjusted_stock.iloc[stock_origin]["close"])
            / float(adjusted_stock.iloc[stock_origin - momentum_lookback]["close"])
        )
        record = {
            "sample_id": int(row.sample_id),
            "ticker": ticker,
            "trade_date": origin.strftime("%Y-%m-%d"),
            "target_date": target.strftime("%Y-%m-%d"),
            "split": str(row.split),
            LABEL_COLUMN: float(row.label_excess_10d),
            "last_value_score": 0.0,
            "momentum_score": momentum,
            "reversal_score": -momentum,
        }
        if hasattr(row, "active_member_count"):
            active_member_count = int(row.active_member_count)
            if active_member_count < 1:
                raise BaselineError(
                    f"active_member_count 无效：{ticker} {origin.date()}"
                )
            record["active_member_count"] = active_member_count
        records.append(record)
    result = pd.DataFrame(records).sort_values("sample_id").reset_index(drop=True)
    observed_ids = result["sample_id"].to_numpy(dtype=np.int64)
    expected_ids = sample_index["sample_id"].to_numpy(dtype=np.int64)
    if not np.array_equal(observed_ids, expected_ids):
        raise BaselineError("baseline_inputs sample_id 未保持 sample_index 全序")
    return result


def _write_feature_bin(path: Path, calendar: pd.DatetimeIndex, series: pd.Series) -> None:
    aligned = series.reindex(calendar).astype(float)
    present = np.flatnonzero(aligned.notna().to_numpy())
    if not len(present):
        raise BaselineError(f"Qlib feature 无有效值：{path.name}")
    start, end = int(present[0]), int(present[-1])
    payload = np.concatenate(
        [np.asarray([start], dtype="<f4"), aligned.iloc[start : end + 1].to_numpy(dtype="<f4")]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    payload.tofile(path)


def _pit_instrument_intervals(
    membership: pd.DataFrame,
    sample_index: pd.DataFrame,
    model_market: pd.DataFrame,
) -> dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]]:
    """Build the Qlib universe from PIT CSI300/500 spans, never quote envelopes."""

    intervals: dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]] = {}
    for ticker in sorted(sample_index["ticker"].unique()):
        stock = model_market[model_market["ticker"] == ticker]
        if stock.empty:
            raise BaselineError(f"Qlib provider 缺少证券数据：{ticker}")
        quote_start = pd.Timestamp(stock["trade_date"].min()).normalize()
        quote_end = pd.Timestamp(stock["trade_date"].max()).normalize()
        rows = membership[membership["ticker"] == ticker].sort_values(
            ["effective_from", "effective_to", "index_code"]
        )
        spans: list[tuple[pd.Timestamp, pd.Timestamp]] = []
        for row in rows.itertuples(index=False):
            start = max(pd.Timestamp(row.effective_from).normalize(), quote_start)
            end = min(pd.Timestamp(row.effective_to).normalize(), quote_end)
            if start > end:
                continue
            if spans and start <= spans[-1][1]:
                spans[-1] = (spans[-1][0], max(spans[-1][1], end))
            else:
                spans.append((start, end))
        if not spans:
            raise BaselineError(f"PIT index_membership 未覆盖样本证券：{ticker}")
        origins = pd.to_datetime(
            sample_index.loc[sample_index["ticker"] == ticker, "origin_date"],
            errors="raise",
        ).dt.normalize()
        uncovered = [
            value
            for value in origins
            if not any(start <= value <= end for start, end in spans)
        ]
        if uncovered:
            raise BaselineError(
                f"PIT index_membership 未覆盖样本日期：{ticker} {uncovered[0].date()}"
            )
        intervals[ticker] = spans
    return intervals


def build_project_qlib_provider(
    *,
    source_path: Path,
    sample_index_path: Path,
    corporate_actions_path: Path,
    index_membership_path: Path | None = None,
    provider_uri: Path,
    training_root: Path,
    segments: Mapping[str, list[str]],
    market: str = "csi800",
    benchmark_ticker: str = "sh000906",
    horizon: int = 10,
    momentum_lookback: int = 20,
    lookback: int = 90,
    purge_days: int = 11,
) -> dict[str, Any]:
    """Build a minimal Qlib binary provider from a project snapshot; never downloads data."""

    if market != "csi800" or benchmark_ticker != "sh000906":
        raise BaselineError("kronos-a-share-v1 固定 market=csi800, benchmark=sh000906")
    if horizon != 10 or momentum_lookback != 20 or lookback != 90 or purge_days != 11:
        raise BaselineError(
            "kronos-a-share-v1 固定 lookback=90,horizon=10,purge_days=11,momentum_lookback=20"
        )
    normalized_segments = validate_segments(segments)
    root = training_root.resolve()
    provider = ensure_within(provider_uri, root)
    sample_path, sample_index = _read_sample_index(sample_index_path, root, normalized_segments)
    actions_path = ensure_within(corporate_actions_path, root)
    if not actions_path.is_file():
        raise BaselineError(f"corporate_actions 不存在：{actions_path}")
    actions_hash_before = sha256_file(actions_path)
    try:
        corporate_actions = load_corporate_actions(actions_path)
    except (DatasetBuildError, OSError, ValueError) as exc:
        raise BaselineError(f"corporate_actions 合同无效：{exc}") from exc
    if corporate_actions is None:
        raise BaselineError("corporate_actions_path 必须显式提供")
    if sha256_file(actions_path) != actions_hash_before:
        raise BaselineError("corporate_actions_hash_drift: 读取期间文件发生变化")
    membership_path: Path | None = None
    membership_hash_before: str | None = None
    membership: pd.DataFrame | None = None
    if index_membership_path is not None:
        membership_path = ensure_within(index_membership_path, root)
        if not membership_path.is_file():
            raise BaselineError(f"index_membership 不存在：{membership_path}")
        membership_hash_before = sha256_file(membership_path)
        try:
            membership = load_membership(membership_path)
        except (DatasetBuildError, OSError, ValueError) as exc:
            raise BaselineError(f"index_membership 合同无效：{exc}") from exc
        if membership is None or membership.empty:
            raise BaselineError("index_membership_path 必须包含 CSI300/CSI500 区间")
        if sha256_file(membership_path) != membership_hash_before:
            raise BaselineError("index_membership_hash_drift: 读取期间文件发生变化")
    market_frame, source_files, source_kind, source_hashes_before = _load_market_source(
        source_path, sample_index, root, benchmark_ticker
    )
    market_frame = _validate_market_frame(market_frame, benchmark_ticker)
    model_market, applied_action_count = _causal_model_price_market(
        market_frame, corporate_actions
    )
    baseline_inputs = _audit_labels_and_build_naive_scores(
        sample_index,
        market_frame,
        model_market,
        corporate_actions,
        benchmark_ticker,
        normalized_segments,
        horizon,
        momentum_lookback,
        lookback,
        purge_days,
    )
    if provider.exists():
        raise BaselineError(f"Qlib provider 已存在，拒绝覆盖：{provider}")
    pending = ensure_within(
        provider.with_name(f".{provider.name}.pending-{os.getpid()}"), root
    )
    if pending.exists():
        raise BaselineError(f"Qlib provider pending 已存在：{pending}")
    pending.mkdir(parents=True)
    try:
        benchmark_dates = model_market.loc[
            model_market["ticker"] == benchmark_ticker, "trade_date"
        ].sort_values()
        calendar = pd.DatetimeIndex(benchmark_dates.drop_duplicates())
        atomic_write(
            pending / "calendars" / "day.txt",
            ("\n".join(date.strftime("%Y-%m-%d") for date in calendar) + "\n").encode("utf-8"),
        )
        label_map = baseline_inputs.set_index(["ticker", "trade_date"])[LABEL_COLUMN]
        instrument_lines: list[str] = []
        sample_tickers = sorted(sample_index["ticker"].unique())
        pit_intervals = (
            _pit_instrument_intervals(membership, sample_index, model_market)
            if membership is not None
            else None
        )
        for ticker in sample_tickers:
            stock = model_market[model_market["ticker"] == ticker].set_index("trade_date")
            if stock.empty:
                raise BaselineError(f"Qlib provider 缺少证券数据：{ticker}")
            if pit_intervals is None:
                instrument_lines.append(
                    f"{ticker.upper()}\t{stock.index.min():%Y-%m-%d}\t{stock.index.max():%Y-%m-%d}"
                )
            else:
                instrument_lines.extend(
                    f"{ticker.upper()}\t{start:%Y-%m-%d}\t{end:%Y-%m-%d}"
                    for start, end in pit_intervals[ticker]
                )
            feature_dir = pending / "features" / ticker
            for feature in FEATURE_COLUMNS:
                _write_feature_bin(feature_dir / f"{feature}.day.bin", calendar, stock[feature])
            label_series = pd.Series(index=calendar, dtype=float)
            ticker_labels = label_map.loc[ticker]
            for date_text, value in ticker_labels.items():
                label_series.loc[pd.Timestamp(date_text)] = float(value)
            _write_feature_bin(
                feature_dir / f"{LABEL_COLUMN}.day.bin", calendar, label_series
            )
        atomic_write(
            pending / "instruments" / f"{market}.txt",
            ("\n".join(instrument_lines) + "\n").encode("utf-8"),
        )
        baseline_path = pending / "baseline_inputs.csv"
        atomic_write(
            baseline_path,
            baseline_inputs.to_csv(index=False, lineterminator="\n").encode("utf-8"),
        )
        source_hashes_after = {str(path.resolve()): sha256_file(path) for path in source_files}
        if source_hashes_before != source_hashes_after:
            raise BaselineError("source_hash_drift: provider 构建期间快照发生变化")
        actions_hash_after = sha256_file(actions_path)
        if actions_hash_after != actions_hash_before:
            raise BaselineError("corporate_actions_hash_drift: provider 构建期间文件发生变化")
        if membership_path is not None and (
            sha256_file(membership_path) != membership_hash_before
        ):
            raise BaselineError("index_membership_hash_drift: provider 构建期间文件发生变化")
        provider_files = {
            path.relative_to(pending).as_posix(): {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(pending.rglob("*"))
            if path.is_file()
        }
        manifest = {
            "schema_version": PROVIDER_SCHEMA,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_kind": source_kind,
            "source_path": str(Path(source_path).resolve()),
            "source_files": source_hashes_after,
            "sample_index_path": str(sample_path),
            "sample_index_sha256": sha256_file(sample_path),
            "sample_id_sha256": _sample_id_sha256(
                sample_index["sample_id"].to_numpy(dtype=np.int64)
            ),
            "corporate_actions_path": str(actions_path),
            "corporate_actions_sha256": actions_hash_after,
            "index_membership_path": (
                str(membership_path) if membership_path is not None else None
            ),
            "index_membership_sha256": membership_hash_before,
            "pit_membership_verified": membership is not None,
            "instrument_membership_contract": (
                "pit_csi300_union_csi500_effective_intervals"
                if membership is not None
                else "quote_envelope_provisional_only"
            ),
            "instrument_interval_count": len(instrument_lines),
            "feature_price_basis": "causal_forward_total_return_equivalent",
            "adjusted_price_columns": ["open", "high", "low", "close", "vwap"],
            "unadjusted_feature_columns": ["volume"],
            "applied_corporate_action_count": applied_action_count,
            "future_action_use_count": 0,
            "segments": normalized_segments,
            "market": market,
            "benchmark_ticker": benchmark_ticker,
            "label_expression": LABEL_EXPRESSION,
            "label_contract": LABEL_CONTRACT,
            "label_unit": LABEL_UNIT,
            "horizon": horizon,
            "lookback": lookback,
            "purge_days": purge_days,
            "calendar_count": len(calendar),
            "instrument_count": len(sample_tickers),
            "sample_count": len(sample_index),
            "baseline_inputs": "baseline_inputs.csv",
            "baseline_inputs_sha256": sha256_file(baseline_path),
            "files": provider_files,
            "downloaded_public_qlib_package": False,
        }
        atomic_write(
            pending / "kronos_provider_manifest.json",
            (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        os.replace(pending, provider)
    except Exception:
        if pending.exists():
            shutil.rmtree(pending)
        raise
    return inspect_project_qlib_provider(provider, root)


def inspect_project_qlib_provider(provider_uri: Path, training_root: Path) -> dict[str, Any]:
    provider = ensure_within(provider_uri, training_root)
    manifest_path = provider / "kronos_provider_manifest.json"
    if not manifest_path.is_file():
        raise BaselineError(f"项目内 Qlib provider manifest 不存在：{manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != PROVIDER_SCHEMA:
        raise BaselineError("Qlib provider schema_version 不匹配")
    if (
        manifest.get("label_expression") != LABEL_EXPRESSION
        or manifest.get("label_contract") != LABEL_CONTRACT
        or manifest.get("label_unit") != LABEL_UNIT
    ):
        raise BaselineError("Qlib provider label 合同不匹配")
    validate_segments(manifest.get("segments", {}))
    if manifest.get("downloaded_public_qlib_package") is not False:
        raise BaselineError("Qlib provider 来源合同不合格")
    if (
        manifest.get("feature_price_basis")
        != "causal_forward_total_return_equivalent"
        or manifest.get("adjusted_price_columns")
        != ["open", "high", "low", "close", "vwap"]
        or manifest.get("unadjusted_feature_columns") != ["volume"]
        or manifest.get("future_action_use_count") != 0
        or not isinstance(manifest.get("applied_corporate_action_count"), int)
        or manifest.get("applied_corporate_action_count", -1) < 0
    ):
        raise BaselineError("Qlib provider model_price_adjusted 因果合同不匹配")
    for relative, contract in manifest.get("files", {}).items():
        path = ensure_within(provider / relative, training_root)
        if not path.is_file() or path.stat().st_size != contract.get("bytes"):
            raise BaselineError(f"Qlib provider 文件缺失或大小漂移：{relative}")
        if sha256_file(path) != contract.get("sha256"):
            raise BaselineError(f"Qlib provider SHA256 漂移：{relative}")
    sample_path = ensure_within(Path(manifest["sample_index_path"]), training_root)
    if sha256_file(sample_path) != manifest.get("sample_index_sha256"):
        raise BaselineError("Qlib provider sample_index SHA256 漂移")
    actions_text = manifest.get("corporate_actions_path")
    actions_hash = manifest.get("corporate_actions_sha256")
    if not isinstance(actions_text, str) or not isinstance(actions_hash, str):
        raise BaselineError("Qlib provider 缺少 corporate_actions 哈希绑定")
    actions_path = ensure_within(Path(actions_text), training_root)
    if not actions_path.is_file() or sha256_file(actions_path) != actions_hash:
        raise BaselineError("Qlib provider corporate_actions SHA256 漂移")
    membership_text = manifest.get("index_membership_path")
    membership_hash = manifest.get("index_membership_sha256")
    membership_verified = manifest.get("pit_membership_verified")
    membership_contract = manifest.get("instrument_membership_contract")
    if membership_verified is True:
        if (
            not isinstance(membership_text, str)
            or not isinstance(membership_hash, str)
            or membership_contract != "pit_csi300_union_csi500_effective_intervals"
        ):
            raise BaselineError("Qlib provider PIT membership 合同缺失")
        membership_path = ensure_within(Path(membership_text), training_root)
        if (
            not membership_path.is_file()
            or sha256_file(membership_path) != membership_hash
        ):
            raise BaselineError("Qlib provider index_membership SHA256 漂移")
    elif not (
        membership_verified is False
        and membership_text is None
        and membership_hash is None
        and membership_contract == "quote_envelope_provisional_only"
    ):
        raise BaselineError("Qlib provider membership 准出状态无效")
    interval_count = manifest.get("instrument_interval_count")
    if not isinstance(interval_count, int) or interval_count < 1:
        raise BaselineError("Qlib provider instrument_interval_count 无效")
    for source_text, expected_hash in manifest.get("source_files", {}).items():
        source = ensure_within(Path(source_text), training_root)
        if not source.is_file() or sha256_file(source) != expected_hash:
            raise BaselineError(f"Qlib provider source_hash_drift：{source}")
    baseline_path = ensure_within(provider / manifest["baseline_inputs"], training_root)
    if sha256_file(baseline_path) != manifest.get("baseline_inputs_sha256"):
        raise BaselineError("Qlib provider baseline_inputs SHA256 漂移")
    baseline_inputs = pd.read_csv(baseline_path)
    if "sample_id" not in baseline_inputs:
        raise BaselineError("Qlib provider baseline_inputs 缺少 sample_id")
    baseline_ids = pd.to_numeric(
        baseline_inputs["sample_id"], errors="raise"
    ).to_numpy(dtype=np.int64)
    if _sample_id_sha256(baseline_ids) != manifest.get("sample_id_sha256"):
        raise BaselineError("Qlib provider baseline_inputs sample_id 全序漂移")
    result = dict(manifest)
    result["provider_uri"] = str(provider)
    result["manifest_path"] = str(manifest_path)
    result["manifest_sha256"] = sha256_file(manifest_path)
    return result


def build_task_config(
    *,
    provider_uri: Path,
    segments: Mapping[str, list[str]],
    market: str = "csi800",
    seed: int = 100,
) -> dict[str, Any]:
    normalized_segments = validate_segments(segments)
    if market != "csi800":
        raise BaselineError("kronos-a-share-v1 的 Alpha158 基线固定使用 csi800")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise BaselineError("LightGBM seed 必须为非负整数")
    return {
        "schema_version": BASELINE_SCHEMA,
        "provider_uri": str(provider_uri.resolve()),
        "region": "cn",
        "market": market,
        "label": LABEL_EXPRESSION,
        "label_contract": LABEL_CONTRACT,
        "label_unit": LABEL_UNIT,
        "horizon": 10,
        "purge_days": 11,
        "segments": normalized_segments,
        "model": {
            "class": "LGBModel",
            "loss": "mse",
            "learning_rate": 0.05,
            "num_leaves": 64,
            "max_depth": 8,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "lambda_l1": 1.0,
            "lambda_l2": 1.0,
            "num_threads": 4,
            "seed": seed,
            "feature_fraction_seed": seed,
            "bagging_seed": seed,
            "data_random_seed": seed,
            "deterministic": True,
            "force_col_wise": True,
        },
    }


def _prediction_to_frame(prediction: Any) -> pd.DataFrame:
    if isinstance(prediction, pd.DataFrame):
        if prediction.shape[1] != 1:
            raise BaselineError("Alpha158 prediction 必须只有一个 score 列")
        prediction = prediction.iloc[:, 0]
    frame = prediction.rename("raw_score").reset_index()
    rename = {}
    if "datetime" in frame:
        rename["datetime"] = "trade_date"
    if "instrument" in frame:
        rename["instrument"] = "ticker"
    frame = frame.rename(columns=rename)
    if not {"trade_date", "ticker", "raw_score"}.issubset(frame.columns):
        raise BaselineError("Alpha158 prediction 索引缺少 datetime/instrument")
    frame["trade_date"] = [
        _as_date(value, field="trade_date") for value in frame["trade_date"]
    ]
    frame["ticker"] = frame["ticker"].map(_normalize_ticker)
    if frame.duplicated(["ticker", "trade_date"]).any():
        raise BaselineError("Alpha158 prediction 存在重复键")
    return frame[["ticker", "trade_date", "raw_score"]]


def run_alpha158_lightgbm(
    *,
    provider_uri: Path,
    training_root: Path,
    output_path: Path,
    segments: Mapping[str, list[str]],
    evaluate_split: str = "validation",
    market: str = "csi800",
    seeds: Sequence[int] = (100,),
) -> dict[str, Any]:
    """Train a deterministic multi-seed Alpha158+LightGBM comparison.

    The published score is the arithmetic mean of every requested seed.  Per-seed
    metrics remain in metadata so release evaluation cannot cherry-pick a run.
    """

    normalized_seeds = tuple(seeds)
    if (
        not normalized_seeds
        or len(normalized_seeds) > 20
        or len(set(normalized_seeds)) != len(normalized_seeds)
        or any(
            isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
            for seed in normalized_seeds
        )
    ):
        raise BaselineError("LightGBM seeds 必须为1至20个互异非负整数")

    provider_manifest = inspect_project_qlib_provider(provider_uri, training_root)
    output = ensure_within(output_path, training_root)
    task = build_task_config(
        provider_uri=Path(provider_manifest["provider_uri"]),
        segments=segments,
        market=market,
        seed=normalized_seeds[0],
    )
    if task["segments"] != provider_manifest["segments"]:
        raise BaselineError("运行 split 与 Qlib provider manifest 不一致")
    if evaluate_split not in REQUIRED_SPLITS:
        raise BaselineError(f"未知 evaluate_split：{evaluate_split}")
    try:
        import qlib
        from qlib.config import REG_CN
        from qlib.contrib.data.handler import Alpha158
        from qlib.contrib.model.gbdt import LGBModel
        from qlib.data.dataset import DatasetH
    except ImportError as exc:
        raise BaselineError("缺少 pyqlib/lightgbm 训练依赖") from exc

    # pyqlib defaults MLflow to ``file:<cwd>/mlruns``.  The project cwd is
    # outside the dedicated training root, so leaving the default in place
    # would create an undeclared write target even when the current model path
    # does not explicitly start a recorder.
    experiment_root = ensure_within(
        Path(training_root) / "registry" / "qlib-mlruns", training_root
    )
    experiment_root.mkdir(parents=True, exist_ok=True)
    experiment_uri = "file:" + str(experiment_root)
    qlib.init(
        provider_uri=provider_manifest["provider_uri"],
        region=REG_CN,
        exp_manager={
            "class": "MLflowExpManager",
            "module_path": "qlib.workflow.expm",
            "kwargs": {
                "uri": experiment_uri,
                "default_exp_name": "kronos_a_share",
            },
        },
    )
    train_start, train_end = task["segments"]["train"]
    all_start = min(interval[0] for interval in task["segments"].values())
    all_end = max(interval[1] for interval in task["segments"].values())
    handler = Alpha158(
        instruments=market,
        start_time=all_start,
        end_time=all_end,
        fit_start_time=train_start,
        fit_end_time=train_end,
        label=[LABEL_EXPRESSION],
    )
    qlib_segments = {
        "train": tuple(task["segments"]["train"]),
        "valid": tuple(task["segments"]["validation"]),
        "test": tuple(task["segments"]["development_test"]),
        "locked_retrospective": tuple(task["segments"]["locked_retrospective"]),
    }
    dataset = DatasetH(handler=handler, segments=qlib_segments)
    segment_key = {
        "validation": "valid",
        "development_test": "test",
    }.get(evaluate_split, evaluate_split)
    baseline_inputs = pd.read_csv(Path(provider_manifest["provider_uri"]) / "baseline_inputs.csv")
    baseline_inputs["trade_date"] = [
        _as_date(value, field="trade_date") for value in baseline_inputs["trade_date"]
    ]
    expected = baseline_inputs[baseline_inputs["split"] == evaluate_split].copy()
    expected_ids = expected["sample_id"].to_numpy(dtype=np.int64)
    seed_scores: list[np.ndarray] = []
    seed_metrics: list[dict[str, Any]] = []
    seed_artifacts: list[dict[str, Any]] = []
    seed_root = ensure_within(
        output.parent / f"{output.name}.seed-evidence", training_root
    )
    seed_root.mkdir(parents=True, exist_ok=True)
    for seed in normalized_seeds:
        seed_task = build_task_config(
            provider_uri=Path(provider_manifest["provider_uri"]),
            segments=segments,
            market=market,
            seed=seed,
        )
        kwargs = dict(seed_task["model"])
        kwargs.pop("class")
        model = LGBModel(**kwargs)
        model.fit(dataset)
        prediction_frame = _prediction_to_frame(
            model.predict(dataset, segment=segment_key)
        )
        seed_frame = expected.merge(
            prediction_frame,
            on=["ticker", "trade_date"],
            how="left",
            validate="one_to_one",
        )
        if seed_frame.empty or seed_frame["raw_score"].isna().any():
            raise BaselineError(f"Alpha158 seed={seed} prediction 未完整覆盖审计样本")
        observed_ids = seed_frame["sample_id"].to_numpy(dtype=np.int64)
        if not np.array_equal(observed_ids, expected_ids):
            raise BaselineError(
                f"Alpha158 seed={seed} prediction 未保持 evaluation sample_id 全序"
            )
        scores = seed_frame["raw_score"].to_numpy(dtype=np.float64)
        if not np.isfinite(scores).all():
            raise BaselineError(f"Alpha158 seed={seed} prediction 含 NaN/Inf")
        seed_scores.append(scores)
        rank_ic, rank_ic_days = _mean_daily_rankic(
            seed_frame,
            min_instruments=FORMAL_MIN_CROSS_SECTION,
            active_member_count_column="active_member_count",
            min_coverage_ratio=FORMAL_MIN_COVERAGE_RATIO,
            require_eligible_cross_section=True,
        )
        seed_artifact = seed_frame[["sample_id", "raw_score"]].copy()
        seed_artifact_path = seed_root / f"seed-{seed}.csv"
        seed_payload = seed_artifact.to_csv(index=False, lineterminator="\n").encode(
            "utf-8"
        )
        atomic_write(seed_artifact_path, seed_payload)
        seed_artifacts.append(
            {
                "seed": seed,
                "path": str(seed_artifact_path.resolve()),
                "sha256": hashlib.sha256(seed_payload).hexdigest(),
                "row_count": int(len(seed_artifact)),
                "sample_id_sha256": _sample_id_sha256(observed_ids),
                "mean_daily_rank_ic": rank_ic,
                "rank_ic_day_count": rank_ic_days,
            }
        )
        seed_metrics.append(
            {
                "seed": seed,
                "mean_daily_rank_ic": rank_ic,
                "rank_ic_day_count": rank_ic_days,
                "mse": float(
                    np.mean(
                        np.square(
                            scores
                            - seed_frame[LABEL_COLUMN].to_numpy(dtype=np.float64)
                        )
                    )
                ),
            }
        )
    frame = expected.copy()
    frame["raw_score"] = np.mean(np.stack(seed_scores, axis=0), axis=0)
    frame = frame[
        ["sample_id", "trade_date", "ticker", "split", "raw_score", LABEL_COLUMN]
    ]
    frame["trade_date"] = frame["trade_date"].dt.strftime("%Y-%m-%d")
    output_payload = frame.to_csv(index=False, lineterminator="\n").encode("utf-8")
    atomic_write(output, output_payload)
    finite_rank_ic = np.asarray(
        [
            item["mean_daily_rank_ic"]
            for item in seed_metrics
            if item["mean_daily_rank_ic"] is not None
        ],
        dtype=np.float64,
    )
    report = {
        "schema_version": BASELINE_SCHEMA,
        "status": "ok",
        "evidence_class": "model_output_baseline",
        "provider_uri": provider_manifest["provider_uri"],
        "provider_manifest_sha256": provider_manifest["manifest_sha256"],
        "experiment_manager_uri": experiment_uri,
        "evaluate_split": evaluate_split,
        "row_count": int(len(frame)),
        "sample_id_sha256": _sample_id_sha256(
            frame["sample_id"].to_numpy(dtype=np.int64)
        ),
        "output_path": str(output),
        "output_sha256": hashlib.sha256(output_payload).hexdigest(),
        "label_column": LABEL_COLUMN,
        "label_contract": LABEL_CONTRACT,
        "label_unit": LABEL_UNIT,
        "task": task,
        "seeds": list(normalized_seeds),
        "seed_count": len(normalized_seeds),
        "aggregate_method": "arithmetic_mean_prediction",
        "seed_metrics": seed_metrics,
        "formal_cross_section": {
            "min_instruments": FORMAL_MIN_CROSS_SECTION,
            "active_member_count_column": "active_member_count",
            "min_coverage_ratio": FORMAL_MIN_COVERAGE_RATIO,
            "require_eligible_cross_section": True,
        },
        "seed_artifacts": seed_artifacts,
        "seed_artifacts_sha256": _canonical_json_sha256(
            {"artifacts": seed_artifacts}
        ),
        "mean_daily_rank_ic_mean": (
            float(np.mean(finite_rank_ic)) if finite_rank_ic.size else None
        ),
        "mean_daily_rank_ic_std": (
            float(np.std(finite_rank_ic, ddof=0)) if finite_rank_ic.size else None
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write(
        output.with_suffix(output.suffix + ".metadata.json"),
        (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )
    return report


def inspect_alpha158_lightgbm_evidence(
    output_path: Path,
    training_root: Path,
    *,
    provider_manifest_sha256: str,
    evaluate_split: str,
    seeds: Sequence[int],
    expected_ids: np.ndarray,
) -> dict[str, Any]:
    """Revalidate the aggregate against all per-seed prediction commitments."""

    root = training_root.resolve()
    output = ensure_within(output_path, root)
    metadata_path = output.with_suffix(output.suffix + ".metadata.json")
    if not output.is_file() or not metadata_path.is_file():
        raise BaselineError("Alpha158 aggregate 或 metadata 缺失")
    try:
        report = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BaselineError("Alpha158 metadata 无法解析") from exc
    normalized_seeds = list(seeds)
    expected_ids = np.asarray(expected_ids, dtype=np.int64)
    formal_contract = {
        "min_instruments": FORMAL_MIN_CROSS_SECTION,
        "active_member_count_column": "active_member_count",
        "min_coverage_ratio": FORMAL_MIN_COVERAGE_RATIO,
        "require_eligible_cross_section": True,
    }
    artifacts = report.get("seed_artifacts")
    if (
        report.get("schema_version") != BASELINE_SCHEMA
        or report.get("status") != "ok"
        or report.get("provider_manifest_sha256") != provider_manifest_sha256
        or report.get("evaluate_split") != evaluate_split
        or report.get("seeds") != normalized_seeds
        or report.get("seed_count") != len(normalized_seeds)
        or report.get("aggregate_method") != "arithmetic_mean_prediction"
        or report.get("formal_cross_section") != formal_contract
        or report.get("output_sha256") != sha256_file(output)
        or report.get("row_count") != len(expected_ids)
        or report.get("sample_id_sha256") != _sample_id_sha256(expected_ids)
        or not isinstance(artifacts, list)
        or len(artifacts) != len(normalized_seeds)
        or report.get("seed_artifacts_sha256")
        != _canonical_json_sha256({"artifacts": artifacts})
    ):
        raise BaselineError("Alpha158 20-seed aggregate/provenance 合同无效")

    provider = inspect_project_qlib_provider(
        Path(str(report.get("provider_uri", ""))), root
    )
    if provider.get("manifest_sha256") != provider_manifest_sha256:
        raise BaselineError("Alpha158 provider manifest 已漂移")
    baseline_inputs = pd.read_csv(Path(provider["provider_uri"]) / "baseline_inputs.csv")
    expected = baseline_inputs[baseline_inputs["split"] == evaluate_split].copy()
    observed_expected_ids = pd.to_numeric(
        expected["sample_id"], errors="raise"
    ).to_numpy(dtype=np.int64)
    if not np.array_equal(observed_expected_ids, expected_ids):
        raise BaselineError("Alpha158 evaluation sample_id 与 provider 不一致")

    aggregate = pd.read_csv(output)
    aggregate_ids = pd.to_numeric(
        aggregate["sample_id"], errors="raise"
    ).to_numpy(dtype=np.int64)
    aggregate_scores = pd.to_numeric(
        aggregate["raw_score"], errors="coerce"
    ).to_numpy(dtype=float)
    if not np.array_equal(aggregate_ids, expected_ids) or not np.isfinite(
        aggregate_scores
    ).all():
        raise BaselineError("Alpha158 aggregate sample/score 无效")

    seed_metrics = report.get("seed_metrics")
    if not isinstance(seed_metrics, list) or len(seed_metrics) != len(normalized_seeds):
        raise BaselineError("Alpha158 seed_metrics 不完整")
    score_vectors: list[np.ndarray] = []
    for position, (seed, artifact, metric) in enumerate(
        zip(normalized_seeds, artifacts, seed_metrics, strict=True)
    ):
        if (
            not isinstance(artifact, Mapping)
            or not isinstance(metric, Mapping)
            or artifact.get("seed") != seed
            or metric.get("seed") != seed
        ):
            raise BaselineError(f"Alpha158 seed evidence 顺序/身份无效：{position}")
        path = ensure_within(Path(str(artifact.get("path", ""))), root)
        if not path.is_file() or artifact.get("sha256") != sha256_file(path):
            raise BaselineError(f"Alpha158 seed={seed} prediction hash 漂移")
        frame = pd.read_csv(path)
        if list(frame.columns) != ["sample_id", "raw_score"]:
            raise BaselineError(f"Alpha158 seed={seed} prediction 列合同无效")
        ids = pd.to_numeric(frame["sample_id"], errors="raise").to_numpy(dtype=np.int64)
        scores = pd.to_numeric(frame["raw_score"], errors="coerce").to_numpy(dtype=float)
        if (
            not np.array_equal(ids, expected_ids)
            or not np.isfinite(scores).all()
            or artifact.get("row_count") != len(expected_ids)
            or artifact.get("sample_id_sha256") != _sample_id_sha256(expected_ids)
        ):
            raise BaselineError(f"Alpha158 seed={seed} 未绑定 evaluation 全样本")
        audited = expected.copy()
        audited["raw_score"] = scores
        rank_ic, rank_ic_days = _mean_daily_rankic(
            audited,
            min_instruments=FORMAL_MIN_CROSS_SECTION,
            active_member_count_column="active_member_count",
            min_coverage_ratio=FORMAL_MIN_COVERAGE_RATIO,
            require_eligible_cross_section=True,
        )
        for source in (artifact, metric):
            declared_rank = source.get("mean_daily_rank_ic")
            if rank_ic is None:
                if declared_rank is not None:
                    raise BaselineError(f"Alpha158 seed={seed} RankIC 证据不一致")
            elif not math.isclose(
                float(declared_rank), rank_ic, rel_tol=0, abs_tol=1e-12
            ):
                raise BaselineError(f"Alpha158 seed={seed} RankIC 证据不一致")
            if source.get("rank_ic_day_count") != rank_ic_days:
                raise BaselineError(f"Alpha158 seed={seed} RankIC 日数不一致")
        score_vectors.append(scores)
    if not np.allclose(
        np.mean(np.stack(score_vectors, axis=0), axis=0),
        aggregate_scores,
        rtol=0,
        atol=1e-12,
    ):
        raise BaselineError("Alpha158 aggregate 不是20-seed逐样本算术均值")
    return dict(report)


def _load_score_frame(
    value: Path | pd.DataFrame,
    *,
    training_root: Path | None,
    name: str,
) -> pd.DataFrame:
    if isinstance(value, Path):
        if training_root is None:
            raise BaselineError(f"{name} 使用文件时必须提供 training_root")
        path = ensure_within(value, training_root)
        if not path.is_file():
            raise BaselineError(f"{name} score 文件不存在：{path}")
        frame = pd.read_csv(path)
    elif isinstance(value, pd.DataFrame):
        frame = value.copy()
    else:
        raise BaselineError(f"{name} score 类型无效")
    if "origin_date" in frame and "trade_date" not in frame:
        frame = frame.rename(columns={"origin_date": "trade_date"})
    if "score" in frame and "raw_score" not in frame:
        frame = frame.rename(columns={"score": "raw_score"})
    required = {"sample_id", "ticker", "trade_date", "raw_score"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise BaselineError(f"{name} score 缺少字段：{missing}")
    frame["ticker"] = frame["ticker"].map(_normalize_ticker)
    frame["trade_date"] = [
        _as_date(item, field="trade_date") for item in frame["trade_date"]
    ]
    frame["raw_score"] = pd.to_numeric(frame["raw_score"], errors="coerce")
    sample_ids = pd.to_numeric(frame["sample_id"], errors="coerce")
    if sample_ids.isna().any() or not np.equal(
        sample_ids.to_numpy(dtype=float), np.floor(sample_ids.to_numpy(dtype=float))
    ).all():
        raise BaselineError(f"{name} score sample_id 必须为整数")
    frame["sample_id"] = sample_ids.to_numpy(dtype=np.int64)
    if frame.duplicated(["sample_id"]).any() or frame.duplicated(
        ["ticker", "trade_date"]
    ).any():
        raise BaselineError(f"{name} score 存在重复键")
    return frame[["sample_id", "ticker", "trade_date", "raw_score"]]


def _mean_daily_rankic(
    frame: pd.DataFrame,
    *,
    min_instruments: int = 2,
    active_member_count_column: str | None = None,
    min_coverage_ratio: float | None = None,
    require_eligible_cross_section: bool = False,
) -> tuple[float | None, int]:
    if min_instruments < 2:
        raise BaselineError("min_instruments 必须至少为2")
    if require_eligible_cross_section:
        if not active_member_count_column or active_member_count_column not in frame:
            raise BaselineError("formal RankIC 缺少 active_member_count")
        if min_coverage_ratio is None or not 0 < min_coverage_ratio <= 1:
            raise BaselineError("formal RankIC min_coverage_ratio 必须位于(0,1]")
    values: list[float] = []
    for trade_date, group in frame.groupby("trade_date"):
        if require_eligible_cross_section:
            counts = pd.to_numeric(
                group[active_member_count_column], errors="coerce"
            ).dropna().unique()
            if len(counts) != 1 or counts[0] <= 0 or not float(counts[0]).is_integer():
                raise BaselineError(
                    f"formal RankIC active_member_count 无效或不一致：{trade_date}"
                )
            active_member_count = int(counts[0])
            coverage_ratio = len(group) / active_member_count
            if len(group) < min_instruments or coverage_ratio < float(min_coverage_ratio):
                raise BaselineError(
                    "formal RankIC 横截面未达标："
                    f"{trade_date} eligible_count={len(group)} "
                    f"active_member_count={active_member_count} coverage_ratio={coverage_ratio:.6f}"
                )
        if (
            len(group) < min_instruments
            or group["raw_score"].nunique() < 2
            or group[LABEL_COLUMN].nunique() < 2
        ):
            continue
        value = group["raw_score"].rank().corr(group[LABEL_COLUMN].rank())
        if pd.notna(value):
            values.append(float(value))
    return (float(np.mean(values)), len(values)) if values else (None, 0)


def validate_baseline_comparison(report: Mapping[str, Any]) -> dict[str, Any]:
    if report.get("schema_version") != COMPARISON_SCHEMA or report.get("status") != "ok":
        raise BaselineError("baseline comparison schema/status 无效")
    if (
        report.get("label_column") != LABEL_COLUMN
        or report.get("label_contract") != LABEL_CONTRACT
        or report.get("label_unit") != LABEL_UNIT
    ):
        raise BaselineError("baseline comparison label 合同无效")
    baselines = report.get("baselines")
    if not isinstance(baselines, dict) or set(baselines) != set(REQUIRED_BASELINES):
        raise BaselineError("baseline comparison 缺少必需基线")
    sample_count = report.get("sample_count")
    if not isinstance(sample_count, int) or sample_count < 1:
        raise BaselineError("baseline comparison sample_count 无效")
    cross_section = report.get("cross_section_contract")
    if not isinstance(cross_section, dict):
        raise BaselineError("baseline comparison 缺少 cross_section_contract")
    if not isinstance(cross_section.get("min_instruments"), int) or cross_section[
        "min_instruments"
    ] < 2:
        raise BaselineError("baseline comparison min_instruments 无效")
    if cross_section.get("require_eligible_cross_section"):
        if cross_section.get("active_member_count_column") != "active_member_count":
            raise BaselineError("formal baseline comparison active_member_count 合同无效")
        ratio = cross_section.get("min_coverage_ratio")
        if not isinstance(ratio, (int, float)) or not 0 < float(ratio) <= 1:
            raise BaselineError("formal baseline comparison min_coverage_ratio 无效")
    for name in REQUIRED_BASELINES:
        contract = baselines[name]
        if contract.get("row_count") != sample_count:
            raise BaselineError(f"baseline comparison {name} 覆盖不完整")
        mse = contract.get("mse")
        if not isinstance(mse, (int, float)) or not math.isfinite(mse) or mse < 0:
            raise BaselineError(f"baseline comparison {name} mse 无效")
        rank_ic = contract.get("mean_daily_rank_ic")
        if rank_ic is not None and (
            not isinstance(rank_ic, (int, float)) or not math.isfinite(rank_ic) or abs(rank_ic) > 1
        ):
            raise BaselineError(f"baseline comparison {name} RankIC 无效")
        rank_ic_status = contract.get("rank_ic_status")
        if rank_ic_status not in {"computed", "zero_information", "insufficient_cross_section"}:
            raise BaselineError(f"baseline comparison {name} rank_ic_status 无效")
    last_value = baselines["last_value"]
    if (
        last_value.get("mean_daily_rank_ic") is not None
        or last_value.get("rank_ic_day_count") != 0
        or last_value.get("rank_ic_status") != "zero_information"
    ):
        raise BaselineError("last_value 必须明确标记为 zero_information/RankIC=null")
    return dict(report)


def build_baseline_comparison(
    *,
    baseline_inputs: Path | pd.DataFrame,
    external_scores: Mapping[str, Path | pd.DataFrame],
    evaluate_split: str,
    training_root: Path | None = None,
    output_path: Path | None = None,
    min_instruments: int = 2,
    active_member_count_column: str | None = None,
    min_coverage_ratio: float | None = None,
    require_eligible_cross_section: bool = False,
) -> dict[str, Any]:
    """Create and validate one structured comparison for all mandatory baselines."""

    if set(external_scores) != set(EXTERNAL_BASELINES):
        raise BaselineError(
            f"external_scores 必须恰好包含：{list(EXTERNAL_BASELINES)}"
        )
    if isinstance(baseline_inputs, Path):
        if training_root is None:
            raise BaselineError("baseline_inputs 使用文件时必须提供 training_root")
        input_path = ensure_within(baseline_inputs, training_root)
        inputs = pd.read_csv(input_path)
    elif isinstance(baseline_inputs, pd.DataFrame):
        inputs = baseline_inputs.copy()
    else:
        raise BaselineError("baseline_inputs 类型无效")
    required = {
        "sample_id",
        "ticker",
        "trade_date",
        "split",
        LABEL_COLUMN,
        "last_value_score",
        "momentum_score",
        "reversal_score",
    }
    missing = sorted(required - set(inputs.columns))
    if missing:
        raise BaselineError(f"baseline_inputs 缺少字段：{missing}")
    if require_eligible_cross_section:
        if active_member_count_column != "active_member_count":
            raise BaselineError(
                "formal baseline comparison 必须使用 active_member_count"
            )
        if active_member_count_column not in inputs:
            raise BaselineError("formal baseline comparison 缺少 active_member_count")
    if evaluate_split not in REQUIRED_SPLITS:
        raise BaselineError(f"evaluate_split 无效：{evaluate_split}")
    sample_ids = pd.to_numeric(inputs["sample_id"], errors="coerce")
    if sample_ids.isna().any() or not np.array_equal(
        sample_ids.to_numpy(dtype=np.int64),
        np.arange(len(inputs), dtype=np.int64),
    ):
        raise BaselineError("baseline_inputs sample_id 未保持从0开始的完整全序")
    inputs["sample_id"] = sample_ids.to_numpy(dtype=np.int64)
    inputs = inputs[inputs["split"] == evaluate_split].copy()
    if inputs.empty:
        raise BaselineError(f"baseline_inputs 在 {evaluate_split} 为空")
    inputs["ticker"] = inputs["ticker"].map(_normalize_ticker)
    inputs["trade_date"] = [
        _as_date(item, field="trade_date") for item in inputs["trade_date"]
    ]
    inputs[LABEL_COLUMN] = pd.to_numeric(inputs[LABEL_COLUMN], errors="coerce")
    if inputs.duplicated(["ticker", "trade_date"]).any() or not np.isfinite(
        inputs[LABEL_COLUMN].to_numpy(dtype=float)
    ).all():
        raise BaselineError("baseline_inputs 键或 label 无效")
    contract_columns = ["sample_id", "ticker", "trade_date", LABEL_COLUMN]
    if require_eligible_cross_section:
        contract_columns.append("active_member_count")
    long_frames: list[pd.DataFrame] = []
    score_columns = {
        "last_value": "last_value_score",
        "momentum": "momentum_score",
        "reversal": "reversal_score",
    }
    for name, column in score_columns.items():
        part = inputs[contract_columns + [column]].rename(
            columns={column: "raw_score"}
        )
        part.insert(0, "baseline", name)
        long_frames.append(part)
    keys = inputs[contract_columns]
    for name in EXTERNAL_BASELINES:
        scores = _load_score_frame(external_scores[name], training_root=training_root, name=name)
        part = keys.merge(
            scores,
            on=["sample_id", "ticker", "trade_date"],
            how="left",
            validate="one_to_one",
        )
        if part["raw_score"].isna().any():
            raise BaselineError(f"{name} 未完整覆盖 {evaluate_split} 样本")
        part.insert(0, "baseline", name)
        long_frames.append(part)
    records = pd.concat(long_frames, ignore_index=True)
    if not np.isfinite(records[["raw_score", LABEL_COLUMN]].to_numpy(dtype=float)).all():
        raise BaselineError("baseline comparison 包含 NaN/Inf")
    metrics: dict[str, Any] = {}
    for name, group in records.groupby("baseline", sort=False):
        rank_ic, rank_ic_days = _mean_daily_rankic(
            group,
            min_instruments=min_instruments,
            active_member_count_column=active_member_count_column,
            min_coverage_ratio=min_coverage_ratio,
            require_eligible_cross_section=require_eligible_cross_section,
        )
        score_is_constant = group["raw_score"].nunique(dropna=False) < 2
        metrics[name] = {
            "row_count": int(len(group)),
            "mean_daily_rank_ic": rank_ic,
            "rank_ic_day_count": rank_ic_days,
            "rank_ic_status": (
                "zero_information"
                if score_is_constant
                else "computed" if rank_ic is not None else "insufficient_cross_section"
            ),
            "mse": float(np.mean(np.square(group["raw_score"] - group[LABEL_COLUMN]))),
        }
    report: dict[str, Any] = {
        "schema_version": COMPARISON_SCHEMA,
        "status": "ok",
        "evidence_class": "model_output_baseline",
        "evaluate_split": evaluate_split,
        "sample_count": int(len(inputs)),
        "label_column": LABEL_COLUMN,
        "label_contract": LABEL_CONTRACT,
        "label_unit": LABEL_UNIT,
        "required_baselines": list(REQUIRED_BASELINES),
        "cross_section_contract": {
            "min_instruments": min_instruments,
            "active_member_count_column": active_member_count_column,
            "min_coverage_ratio": min_coverage_ratio,
            "require_eligible_cross_section": require_eligible_cross_section,
        },
        "baselines": metrics,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if output_path is not None:
        if training_root is None:
            raise BaselineError("写 comparison 时必须提供 training_root")
        output = ensure_within(output_path, training_root)
        serializable = records.copy()
        serializable["trade_date"] = serializable["trade_date"].dt.strftime("%Y-%m-%d")
        payload = serializable.to_csv(index=False, lineterminator="\n").encode("utf-8")
        atomic_write(output, payload)
        report["output_path"] = str(output)
        report["output_sha256"] = hashlib.sha256(payload).hexdigest()
        atomic_write(
            output.with_suffix(output.suffix + ".metadata.json"),
            (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
    return validate_baseline_comparison(report)


def _normalize_gate_binding(binding: Any) -> dict[str, str]:
    if hasattr(binding, "as_dict"):
        values = dict(binding.as_dict())
    elif isinstance(binding, Mapping):
        values = dict(binding)
    else:
        raise BaselineError("binding 必须是 mapping 或提供 as_dict()")
    if "data_sha256" not in values and "dataset_sha256" in values:
        values["data_sha256"] = values["dataset_sha256"]
    required = (
        "base_model_sha256",
        "tokenizer_sha256",
        "data_sha256",
        "config_sha256",
    )
    result: dict[str, str] = {}
    for key in required:
        value = str(values.get(key, "")).lower()
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise BaselineError(f"binding.{key} 必须是64位 SHA256")
        result[key] = value
    return result


def _sample_id_sha256(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype=np.int64).tobytes()).hexdigest()


def _strict_bool(value: Any, *, field: str) -> bool:
    mapping = {
        True: True,
        False: False,
        1: True,
        0: False,
        "true": True,
        "false": False,
        "1": True,
        "0": False,
    }
    key = value.strip().lower() if isinstance(value, str) else value
    if key not in mapping:
        raise BaselineError(f"{field} 含非严格布尔值：{value!r}")
    return mapping[key]


def _artifact_record(
    value: Mapping[str, Any],
    *,
    name: str,
    training_root: Path,
) -> tuple[Path, dict[str, str]]:
    if not isinstance(value, Mapping) or set(value) != {"path", "sha256"}:
        raise BaselineError(f"{name} artifact 必须恰好包含 path/sha256")
    path = ensure_within(Path(str(value["path"])), training_root)
    if not path.is_file():
        raise BaselineError(f"{name} artifact 不存在：{path}")
    expected = str(value["sha256"]).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected) or sha256_file(path) != expected:
        raise BaselineError(f"{name} artifact SHA256 漂移")
    return path, {"path": str(path), "sha256": expected}


def _read_pit_execution_tables(
    *,
    suspensions_path: Path,
    price_limits_path: Path,
    training_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, str]]]:
    paths = {
        "suspensions": ensure_within(suspensions_path, training_root),
        "price_limits": ensure_within(price_limits_path, training_root),
    }
    for name, path in paths.items():
        if not path.is_file():
            raise BaselineError(f"PIT {name} 不存在：{path}")
    hashes = {name: sha256_file(path) for name, path in paths.items()}
    suspensions = pd.read_csv(paths["suspensions"])
    price_limits = pd.read_csv(paths["price_limits"])
    missing_suspensions = sorted(
        {"ticker", "trade_date", "is_suspended"} - set(suspensions.columns)
    )
    missing_limits = sorted(
        {"ticker", "trade_date", "up_limit", "down_limit"} - set(price_limits.columns)
    )
    if missing_suspensions or missing_limits:
        raise BaselineError(
            "PIT execution 字段不完整："
            f"suspensions={missing_suspensions}, price_limits={missing_limits}"
        )
    for name, frame in (("suspensions", suspensions), ("price_limits", price_limits)):
        frame["ticker"] = frame["ticker"].map(_normalize_ticker)
        frame["trade_date"] = [
            _as_date(value, field=f"{name}.trade_date") for value in frame["trade_date"]
        ]
        if frame.duplicated(["ticker", "trade_date"]).any():
            raise BaselineError(f"PIT {name} 存在重复 ticker/trade_date")
    suspensions["is_suspended"] = [
        _strict_bool(value, field="suspensions.is_suspended")
        for value in suspensions["is_suspended"]
    ]
    up = pd.to_numeric(price_limits["up_limit"], errors="coerce")
    down = pd.to_numeric(price_limits["down_limit"], errors="coerce")
    if (up.isna() ^ down.isna()).any():
        raise BaselineError("PIT price_limits 的 up_limit/down_limit 必须同时为空或存在")
    limited = up.notna()
    if ((up[limited] <= 0) | (down[limited] <= 0) | (up[limited] < down[limited])).any():
        raise BaselineError("PIT price_limits 价格无效")
    price_limits["up_limit"] = up
    price_limits["down_limit"] = down
    for name, path in paths.items():
        if sha256_file(path) != hashes[name]:
            raise BaselineError(f"source_hash_drift: PIT {name} 读取期间发生变化")
    records = {
        name: {"path": str(path), "sha256": hashes[name]} for name, path in paths.items()
    }
    return suspensions, price_limits, records


def _decimal_price(value: Any, *, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise BaselineError(f"{field} 不是有效价格：{value}") from exc
    if not result.is_finite() or result <= 0:
        raise BaselineError(f"{field} 必须是正数")
    return result


def _execution_frame(
    *,
    samples: pd.DataFrame,
    raw_market_source_path: Path,
    suspensions: pd.DataFrame,
    price_limits: pd.DataFrame,
    corporate_actions: pd.DataFrame,
    training_root: Path,
    benchmark_ticker: str,
) -> tuple[pd.DataFrame, dict[str, str], str]:
    market, source_files, source_kind, source_hashes = _load_market_source(
        raw_market_source_path, samples, training_root, benchmark_ticker
    )
    market = _validate_market_frame(market, benchmark_ticker)
    if source_kind == "normalized":
        if "price_basis" not in market.columns or not market["price_basis"].astype(str).eq(
            "trade_price_raw"
        ).all():
            raise BaselineError(
                "normalized execution source 必须逐行声明 price_basis=trade_price_raw"
            )
    grouped = {
        ticker: group.sort_values("trade_date").reset_index(drop=True)
        for ticker, group in market.groupby("ticker", sort=False)
    }
    benchmark = grouped[benchmark_ticker]
    benchmark_positions = {
        date: index for index, date in enumerate(benchmark["trade_date"].tolist())
    }
    suspension_index = suspensions.set_index(["ticker", "trade_date"])["is_suspended"]
    limit_index = price_limits.set_index(["ticker", "trade_date"])[
        ["up_limit", "down_limit"]
    ]
    actions_by_ticker = {
        ticker: group.sort_values(["ex_date", "announcement_date"])
        for ticker, group in corporate_actions.groupby("ticker", sort=False)
    }
    rows: list[dict[str, Any]] = []
    for row in samples.itertuples(index=False):
        stock = grouped.get(row.ticker)
        if stock is None:
            raise BaselineError(f"raw execution source 缺少证券：{row.ticker}")
        stock_positions = {
            date: index for index, date in enumerate(stock["trade_date"].tolist())
        }
        origin = pd.Timestamp(row.origin_date)
        target = pd.Timestamp(row.target_date)
        origin_position = stock_positions.get(origin)
        benchmark_origin = benchmark_positions.get(origin)
        if origin_position is None or benchmark_origin is None:
            raise BaselineError(f"raw execution source 缺少 signal date：{row.ticker} {origin.date()}")
        if origin_position + 10 >= len(stock) or benchmark_origin + 10 >= len(benchmark):
            raise BaselineError(f"raw execution source 缺少10日成交窗口：{row.ticker}")
        entry_row = stock.iloc[origin_position + 1]
        exit_row = stock.iloc[origin_position + 10]
        expected_entry_date = pd.Timestamp(benchmark.iloc[benchmark_origin + 1]["trade_date"])
        expected_exit_date = pd.Timestamp(benchmark.iloc[benchmark_origin + 10]["trade_date"])
        entry_date = pd.Timestamp(entry_row["trade_date"])
        exit_date = pd.Timestamp(exit_row["trade_date"])
        if entry_date != expected_entry_date:
            raise BaselineError(f"entry_session_gap: {row.ticker} {origin.date()}")
        if exit_date != target or exit_date != expected_exit_date:
            raise BaselineError(f"exit_session_or_target_mismatch: {row.ticker} {origin.date()}")
        entry_key = (row.ticker, entry_date)
        exit_key = (row.ticker, exit_date)
        if entry_key not in suspension_index.index or exit_key not in suspension_index.index:
            raise BaselineError(f"PIT suspensions 未完整覆盖 entry/exit：{row.ticker}")
        if entry_key not in limit_index.index or exit_key not in limit_index.index:
            raise BaselineError(f"PIT price_limits 未完整覆盖 entry/exit：{row.ticker}")
        entry_suspended = bool(suspension_index.loc[entry_key])
        exit_suspended = bool(suspension_index.loc[exit_key])
        entry_limits = limit_index.loc[entry_key]
        exit_limits = limit_index.loc[exit_key]
        entry_price = _decimal_price(entry_row["open"], field="entry_price_raw")
        exit_price = _decimal_price(exit_row["close"], field="exit_price_raw")
        entry_limit_blocked = False
        if pd.notna(entry_limits["up_limit"]):
            entry_limit_blocked = entry_price >= _decimal_price(
                entry_limits["up_limit"], field="entry up_limit"
            )
        exit_limit_blocked = False
        if pd.notna(exit_limits["down_limit"]):
            exit_limit_blocked = exit_price <= _decimal_price(
                exit_limits["down_limit"], field="exit down_limit"
            )
        stock_for_actions = stock.copy()
        stock_for_actions["date"] = stock_for_actions["trade_date"].dt.strftime(
            "%Y%m%d"
        ).astype(np.int64)
        factor_product = 1.0
        action_count = 0
        ticker_actions = actions_by_ticker.get(row.ticker)
        if ticker_actions is not None:
            holding_actions = ticker_actions[
                (ticker_actions["announcement_date"] <= exit_date)
                & (ticker_actions["ex_date"] > entry_date)
                & (ticker_actions["ex_date"] <= exit_date)
            ]
            for event in holding_actions.itertuples(index=False):
                if pd.Timestamp(event.announcement_date) > pd.Timestamp(event.ex_date):
                    raise BaselineError(
                        f"corporate_action_non_pit: {row.ticker} "
                        f"{pd.Timestamp(event.ex_date).date()}"
                    )
                factor_product *= _event_adjustment_factor(
                    stock_for_actions, event, row.ticker
                )
                action_count += 1
        if not math.isfinite(factor_product) or factor_product <= 0:
            raise BaselineError("execution corporate_action_factor 无效")
        rows.append(
            {
                "sample_id": int(row.sample_id),
                "entry_date": entry_date.strftime("%Y-%m-%d"),
                "exit_date": exit_date.strftime("%Y-%m-%d"),
                "entry_price_raw": float(entry_price),
                "exit_price_raw": float(exit_price),
                "entry_tradable": not entry_suspended,
                "exit_tradable": not exit_suspended,
                "entry_limit_blocked": entry_limit_blocked,
                "exit_limit_blocked": exit_limit_blocked,
                "stamp_duty_rate": 0.001 if exit_date < pd.Timestamp("2023-08-28") else 0.0005,
                "corporate_action_factor": factor_product,
                "corporate_action_event_count": action_count,
                "holding_period_sessions": 10,
            }
        )
    for source in source_files:
        if sha256_file(source) != source_hashes[str(source.resolve())]:
            raise BaselineError(f"source_hash_drift: raw market source 发生变化：{source}")
    return pd.DataFrame(rows), source_hashes, source_kind


def _load_external_companion_score(
    *,
    name: str,
    artifact: Mapping[str, Any],
    expected_ids: np.ndarray,
    training_root: Path,
) -> tuple[np.ndarray, dict[str, str]]:
    path, record = _artifact_record(
        artifact, name=name, training_root=training_root
    )
    frame = pd.read_csv(path)
    if "sample_id" not in frame:
        raise BaselineError(f"{name} artifact 缺少 sample_id")
    score_column = name if name in frame else "raw_score" if "raw_score" in frame else None
    if score_column is None:
        raise BaselineError(f"{name} artifact 缺少 {name}/raw_score")
    ids = pd.to_numeric(frame["sample_id"], errors="raise").to_numpy(dtype=np.int64)
    if frame["sample_id"].duplicated().any() or not np.array_equal(ids, expected_ids):
        raise BaselineError(f"{name} 必须与 sample_id 同序、全量一一对应")
    scores = pd.to_numeric(frame[score_column], errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(scores).all():
        raise BaselineError(f"{name} 包含 NaN/Inf")
    if sha256_file(path) != record["sha256"]:
        raise BaselineError(f"{name} artifact SHA256 漂移")
    return scores, record


def inspect_evaluation_companion(
    output_path: Path,
    training_root: Path,
    *,
    binding: Any | None = None,
    evaluate_split: str | None = None,
) -> dict[str, Any]:
    output = ensure_within(output_path, training_root)
    metadata_path = output.with_suffix(output.suffix + ".metadata.json")
    if not output.is_file() or not metadata_path.is_file():
        raise BaselineError("evaluation companion 或 metadata 不存在")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("schema_version") != EVALUATION_COMPANION_SCHEMA:
        raise BaselineError("evaluation companion schema_version 不匹配")
    if metadata.get("input_sha256") != sha256_file(output):
        raise BaselineError("evaluation companion input SHA256 漂移")
    if binding is not None and metadata.get("binding") != _normalize_gate_binding(binding):
        raise BaselineError("evaluation companion binding 不匹配")
    if evaluate_split is not None and metadata.get("evaluate_split") != evaluate_split:
        raise BaselineError(
            "evaluation companion evaluate_split 不匹配："
            f"expected={evaluate_split}, actual={metadata.get('evaluate_split')}"
        )
    frame = pd.read_csv(output)
    required_columns = {
        "sample_id",
        "active_member_count",
        "entry_date",
        "exit_date",
        "entry_price_raw",
        "exit_price_raw",
        "entry_tradable",
        "exit_tradable",
        "entry_limit_blocked",
        "exit_limit_blocked",
        "stamp_duty_rate",
        "corporate_action_factor",
        "corporate_action_event_count",
        "holding_period_sessions",
        *COMPANION_SCORE_COLUMNS,
    }
    if set(frame.columns) != required_columns:
        raise BaselineError("evaluation companion 列合同不匹配")
    ids = pd.to_numeric(frame["sample_id"], errors="raise").to_numpy(dtype=np.int64)
    if frame["sample_id"].duplicated().any() or _sample_id_sha256(ids) != metadata.get(
        "sample_id_sha256"
    ):
        raise BaselineError("evaluation companion sample_id 合同不匹配")
    if len(frame) != metadata.get("row_count"):
        raise BaselineError("evaluation companion row_count 漂移")
    numeric = [
        "active_member_count",
        "entry_price_raw",
        "exit_price_raw",
        "stamp_duty_rate",
        "corporate_action_factor",
        "corporate_action_event_count",
        *COMPANION_SCORE_COLUMNS,
    ]
    if not np.isfinite(frame[numeric].apply(pd.to_numeric, errors="coerce").to_numpy()).all():
        raise BaselineError("evaluation companion 数值包含 NaN/Inf")
    if not (pd.to_numeric(frame["holding_period_sessions"], errors="coerce") == 10).all():
        raise BaselineError("evaluation companion holding_period_sessions 必须为10")
    active_members = pd.to_numeric(
        frame["active_member_count"], errors="coerce"
    ).to_numpy(dtype=float)
    if (
        not np.isfinite(active_members).all()
        or (active_members < 1).any()
        or not np.equal(active_members, np.floor(active_members)).all()
    ):
        raise BaselineError("evaluation companion active_member_count 合同无效")
    factors = pd.to_numeric(frame["corporate_action_factor"], errors="coerce")
    action_counts = pd.to_numeric(frame["corporate_action_event_count"], errors="coerce")
    if (factors <= 0).any() or (action_counts < 0).any() or not np.equal(
        action_counts.to_numpy(dtype=float),
        np.floor(action_counts.to_numpy(dtype=float)),
    ).all():
        raise BaselineError("evaluation companion corporate action 因子合同无效")
    exits = pd.to_datetime(frame["exit_date"], errors="coerce")
    entries = pd.to_datetime(frame["entry_date"], errors="coerce")
    if exits.isna().any() or entries.isna().any() or not (exits > entries).all():
        raise BaselineError("evaluation companion entry/exit 日期无效")
    expected_tax = np.where(exits < pd.Timestamp("2023-08-28"), 0.001, 0.0005)
    if not np.allclose(frame["stamp_duty_rate"], expected_tax, rtol=0, atol=1e-12):
        raise BaselineError("evaluation companion 印花税有效期错误")
    for column in (
        "entry_tradable",
        "exit_tradable",
        "entry_limit_blocked",
        "exit_limit_blocked",
    ):
        for value in frame[column]:
            _strict_bool(value, field=column)
    required_sources = {"execution", *COMPANION_SCORE_COLUMNS}
    source_artifacts = metadata.get("source_artifacts")
    if not isinstance(source_artifacts, dict) or set(source_artifacts) != required_sources:
        raise BaselineError("evaluation companion source_artifacts 合同不完整")
    resolved_sources: dict[str, Path] = {}
    for name in sorted(required_sources):
        path, _ = _artifact_record(
            source_artifacts[name], name=name, training_root=training_root
        )
        resolved_sources[name] = path
    execution_audit = json.loads(resolved_sources["execution"].read_text(encoding="utf-8"))
    if execution_audit.get("schema_version") != EXECUTION_AUDIT_SCHEMA:
        raise BaselineError("execution audit schema_version 不匹配")
    for name, record in execution_audit.get("source_artifacts", {}).items():
        _artifact_record(record, name=f"execution.{name}", training_root=training_root)
    return metadata


def build_evaluation_companion(
    *,
    training_root: Path,
    sample_index_path: Path,
    raw_market_source_path: Path,
    provider_uri: Path,
    suspensions_path: Path,
    price_limits_path: Path,
    external_score_artifacts: Mapping[str, Mapping[str, Any]],
    binding: Any,
    output_path: Path,
    evaluate_split: str = "validation",
    benchmark_ticker: str = "sh000906",
) -> dict[str, Any]:
    """Build the audited execution/baseline companion consumed by ``evaluate``.

    Entry is the first raw open after the signal; exit is the raw close at the
    sample's tenth target session. ``drift_score`` is the 20-session natural-log
    momentum projected linearly to ten sessions: ``momentum_score / 20 * 10``.
    """

    root = training_root.resolve()
    output = ensure_within(output_path, root)
    gate_binding = _normalize_gate_binding(binding)
    if set(external_score_artifacts) != set(EXTERNAL_SCORE_COLUMNS):
        raise BaselineError(
            f"external_score_artifacts 必须恰好包含：{list(EXTERNAL_SCORE_COLUMNS)}"
        )
    provider = inspect_project_qlib_provider(provider_uri, root)
    actions_path = ensure_within(Path(provider["corporate_actions_path"]), root)
    if sha256_file(actions_path) != provider["corporate_actions_sha256"]:
        raise BaselineError("evaluation corporate_actions 与 provider 哈希绑定不一致")
    try:
        corporate_actions = load_corporate_actions(actions_path)
    except (DatasetBuildError, OSError, ValueError) as exc:
        raise BaselineError(f"evaluation corporate_actions 合同无效：{exc}") from exc
    if corporate_actions is None:
        raise BaselineError("evaluation corporate_actions 必须显式提供")
    segments = provider["segments"]
    sample_path, all_samples = _read_sample_index(sample_index_path, root, segments)
    if sha256_file(sample_path) != provider.get("sample_index_sha256"):
        raise BaselineError("evaluation sample_index 与受审计 provider 不一致")
    if "sample_id" not in all_samples:
        raise BaselineError("evaluation sample_index 缺少 sample_id")
    samples = all_samples[all_samples["split"] == evaluate_split].copy()
    if samples.empty:
        raise BaselineError(f"sample_index 在 {evaluate_split} 为空")
    sample_ids = pd.to_numeric(samples["sample_id"], errors="raise").to_numpy(dtype=np.int64)
    if samples["sample_id"].duplicated().any():
        raise BaselineError("evaluation sample_id 重复")
    sample_hash_before = sha256_file(sample_path)
    suspensions, price_limits, pit_records = _read_pit_execution_tables(
        suspensions_path=suspensions_path,
        price_limits_path=price_limits_path,
        training_root=root,
    )
    execution, raw_source_hashes, raw_source_kind = _execution_frame(
        samples=samples,
        raw_market_source_path=raw_market_source_path,
        suspensions=suspensions,
        price_limits=price_limits,
        corporate_actions=corporate_actions,
        training_root=root,
        benchmark_ticker=benchmark_ticker,
    )
    if not np.array_equal(execution["sample_id"].to_numpy(dtype=np.int64), sample_ids):
        raise BaselineError("execution rows 未与 sample_id 同序全覆盖")

    baseline_path = ensure_within(
        Path(provider["provider_uri"]) / provider["baseline_inputs"], root
    )
    baseline_hash = sha256_file(baseline_path)
    baseline_inputs = pd.read_csv(baseline_path)
    baseline_inputs["ticker"] = baseline_inputs["ticker"].map(_normalize_ticker)
    baseline_inputs["trade_date"] = [
        _as_date(value, field="baseline_inputs.trade_date")
        for value in baseline_inputs["trade_date"]
    ]
    if baseline_inputs.duplicated(["ticker", "trade_date"]).any():
        raise BaselineError("provider baseline_inputs 存在重复键")
    if "active_member_count" not in samples or "active_member_count" not in baseline_inputs:
        raise BaselineError("evaluation companion 缺少 active_member_count 来源绑定")
    sample_keys = samples[
        ["sample_id", "ticker", "origin_date", LABEL_COLUMN, "active_member_count"]
    ].rename(
        columns={
            "origin_date": "trade_date",
            LABEL_COLUMN: "sample_label",
            "active_member_count": "sample_active_member_count",
        }
    )
    naive = sample_keys.merge(
        baseline_inputs[
            [
                "sample_id",
                "ticker",
                "trade_date",
                LABEL_COLUMN,
                "active_member_count",
                "last_value_score",
                "momentum_score",
                "reversal_score",
            ]
        ],
        on=["sample_id", "ticker", "trade_date"],
        how="left",
        validate="one_to_one",
    )
    if naive[["last_value_score", "momentum_score", "reversal_score"]].isna().any().any():
        raise BaselineError("provider baseline_inputs 未全量覆盖 evaluation samples")
    if not np.allclose(
        naive["sample_label"], naive[LABEL_COLUMN], rtol=0, atol=1e-8
    ):
        raise BaselineError("provider baseline_inputs label 与 sample_index 不一致")
    sample_active = pd.to_numeric(
        naive["sample_active_member_count"], errors="coerce"
    ).to_numpy(dtype=float)
    provider_active = pd.to_numeric(
        naive["active_member_count"], errors="coerce"
    ).to_numpy(dtype=float)
    if (
        not np.isfinite(sample_active).all()
        or (sample_active < 1).any()
        or not np.equal(sample_active, np.floor(sample_active)).all()
        or not np.array_equal(sample_active, provider_active)
    ):
        raise BaselineError(
            "provider baseline_inputs active_member_count 与 sample_index 不一致"
        )
    if not np.array_equal(naive["sample_id"].to_numpy(dtype=np.int64), sample_ids):
        raise BaselineError("provider baseline_inputs 未与 sample_id 同序")
    result = execution.copy()
    result["active_member_count"] = sample_active.astype(np.int32)
    for column in ("last_value_score", "momentum_score", "reversal_score"):
        result[column] = pd.to_numeric(naive[column], errors="coerce").to_numpy(dtype=float)
    result["drift_score"] = result["momentum_score"] / 20.0 * 10.0

    source_artifacts: dict[str, dict[str, str]] = {}
    for name in EXTERNAL_SCORE_COLUMNS:
        scores, record = _load_external_companion_score(
            name=name,
            artifact=external_score_artifacts[name],
            expected_ids=sample_ids,
            training_root=root,
        )
        result[name] = scores
        source_artifacts[name] = record
    naive_record = {"path": str(baseline_path), "sha256": baseline_hash}
    for name in ("last_value_score", "drift_score", "momentum_score", "reversal_score"):
        source_artifacts[name] = dict(naive_record)
    ordered_columns = [
        "sample_id",
        "active_member_count",
        "entry_date",
        "exit_date",
        "entry_price_raw",
        "exit_price_raw",
        "entry_tradable",
        "exit_tradable",
        "entry_limit_blocked",
        "exit_limit_blocked",
        "stamp_duty_rate",
        "corporate_action_factor",
        "corporate_action_event_count",
        "holding_period_sessions",
        *COMPANION_SCORE_COLUMNS,
    ]
    result = result[ordered_columns]
    if not np.isfinite(result[list(COMPANION_SCORE_COLUMNS)].to_numpy(dtype=float)).all():
        raise BaselineError("evaluation companion score 包含 NaN/Inf")
    if sha256_file(sample_path) != sample_hash_before or sha256_file(baseline_path) != baseline_hash:
        raise BaselineError("source_hash_drift: sample_index/provider baseline_inputs 发生变化")

    execution_artifact_path = ensure_within(
        output.with_suffix(output.suffix + ".execution.json"), root
    )
    inner_sources: dict[str, dict[str, str]] = {
        "sample_index": {"path": str(sample_path), "sha256": sample_hash_before},
        "provider_manifest": {
            "path": provider["manifest_path"],
            "sha256": provider["manifest_sha256"],
        },
        "corporate_actions": {
            "path": str(actions_path),
            "sha256": provider["corporate_actions_sha256"],
        },
        **pit_records,
    }
    for index, (path_text, digest) in enumerate(sorted(raw_source_hashes.items())):
        inner_sources[f"raw_market_{index:04d}"] = {"path": path_text, "sha256": digest}
    execution_audit = {
        "schema_version": EXECUTION_AUDIT_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_id_sha256": _sample_id_sha256(sample_ids),
        "row_count": len(result),
        "raw_source_kind": raw_source_kind,
        "entry_contract": "first_raw_open_after_signal",
        "exit_contract": "tenth_target_session_raw_close",
        "holding_period_sessions": 10,
        "entry_tradability_contract": "not_suspended_and_not_at_or_above_up_limit",
        "exit_tradability_contract": "not_suspended_and_not_at_or_below_down_limit",
        "stamp_duty_schedule": {
            "before_2023-08-28": 0.001,
            "from_2023-08-28": 0.0005,
            "charged_on": "exit",
            "tax_base": "exit_market_value_after_corporate_action_factor",
        },
        "corporate_action_return_contract": (
            "gross_ratio=exit_price_raw/(entry_price_raw*product(event_factor));"
            "entry_date<ex_date<=exit_date;announcement_date<=exit_date"
        ),
        "drift_contract": "20_session_natural_log_momentum_divided_by_20_times_10",
        "source_artifacts": inner_sources,
    }
    atomic_write(
        execution_artifact_path,
        (json.dumps(execution_audit, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )
    source_artifacts["execution"] = {
        "path": str(execution_artifact_path),
        "sha256": sha256_file(execution_artifact_path),
    }
    payload = result.to_csv(index=False, lineterminator="\n").encode("utf-8")
    atomic_write(output, payload)
    metadata = {
        "schema_version": EVALUATION_COMPANION_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(output),
        "input_sha256": hashlib.sha256(payload).hexdigest(),
        "row_count": len(result),
        "evaluate_split": evaluate_split,
        "sample_id_sha256": _sample_id_sha256(sample_ids),
        "binding": gate_binding,
        "holding_period_sessions": 10,
        "execution_contract": "next_session_raw_open_to_tenth_target_session_raw_close",
        "drift_contract": "20_session_natural_log_momentum_divided_by_20_times_10",
        "source_artifacts": source_artifacts,
    }
    metadata_path = output.with_suffix(output.suffix + ".metadata.json")
    atomic_write(
        metadata_path,
        (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )
    return inspect_evaluation_companion(
        output,
        root,
        binding=binding,
        evaluate_split=evaluate_split,
    )
