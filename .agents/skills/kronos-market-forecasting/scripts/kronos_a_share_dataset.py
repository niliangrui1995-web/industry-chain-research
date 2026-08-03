#!/usr/bin/env python3
"""Build leakage-controlled A-share sample indices and Kronos token caches."""

from __future__ import annotations

import hashlib
import gc
import json
import math
import os
import re
import shutil
import struct
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

import numpy as np
import pandas as pd


DAY_RECORD = struct.Struct("<IIIIIfII")
WINDOW_SCHEMA = "kronos-a-share-window-index-v1"
TOKEN_SCHEMA = "kronos-a-share-token-cache-v1"
FEATURE_COLUMNS = ["open", "high", "low", "close", "volume", "amount"]
PRICE_COLUMN_COUNT = 4
SPLIT_NAMES = ["train", "validation", "development_test", "locked_retrospective"]
SPLIT_CODES = {name: index for index, name in enumerate(SPLIT_NAMES)}
A_SHARE_PATTERN = re.compile(
    r"^(?:sh(?:600|601|603|605|688|689)\d{3}|sz(?:000|001|002|003|300|301)\d{3}|bj[489]\d{5})$"
)


class DatasetBuildError(RuntimeError):
    """Raised when the prepared dataset could leak or write outside its root."""


@dataclass(frozen=True)
class WindowSpec:
    lookback: int = 90
    horizon: int = 10
    purge_days: int = 11
    clip: float = 5.0

    @property
    def total_bars(self) -> int:
        return self.lookback + self.horizon


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_within(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    boundary = root.resolve()
    try:
        resolved.relative_to(boundary)
    except ValueError as exc:
        raise DatasetBuildError(f"path_outside_training_root: {resolved}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f".{path.name}.pending-{os.getpid()}")
    with pending.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, path)


def read_day_file(path: Path) -> pd.DataFrame:
    payload = path.read_bytes()
    if not payload or len(payload) % DAY_RECORD.size:
        raise DatasetBuildError(f"TDX .day 长度不是32字节整数倍：{path}")
    rows = []
    previous_date = 0
    for offset in range(0, len(payload), DAY_RECORD.size):
        date, open_i, high_i, low_i, close_i, amount, volume, _ = DAY_RECORD.unpack_from(
            payload, offset
        )
        if date <= previous_date:
            raise DatasetBuildError(f"TDX .day 日期非严格递增：{path}")
        previous_date = date
        open_v, high_v, low_v, close_v = (
            open_i / 100.0,
            high_i / 100.0,
            low_i / 100.0,
            close_i / 100.0,
        )
        if min(open_v, high_v, low_v, close_v) <= 0:
            raise DatasetBuildError(f"TDX .day 包含非正价格：{path} date={date}")
        if high_v < max(open_v, close_v) or low_v > min(open_v, close_v) or high_v < low_v:
            raise DatasetBuildError(f"TDX .day OHLC 无效：{path} date={date}")
        if amount < 0 or volume < 0:
            raise DatasetBuildError(f"TDX .day 成交量额为负：{path} date={date}")
        rows.append((date, open_v, high_v, low_v, close_v, float(volume), float(amount)))
    return pd.DataFrame(rows, columns=["date", *FEATURE_COLUMNS])


def normalize_ticker(value: str) -> str:
    text = str(value).strip().lower()
    if re.fullmatch(r"(?:sh|sz|bj)\d{6}", text):
        return text
    match = re.fullmatch(r"(\d{6})\.(sh|sz|bj)", text)
    if match:
        return f"{match.group(2)}{match.group(1)}"
    raise DatasetBuildError(f"ticker 格式无效：{value}")


def discover_day_files(snapshot_root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in snapshot_root.rglob("*.day"):
        ticker = path.stem.lower()
        if not A_SHARE_PATTERN.fullmatch(ticker) and ticker not in {
            "sh000300",
            "sh000905",
            "sh000906",
        }:
            continue
        if ticker in files:
            raise DatasetBuildError(f"快照内 ticker 重复：{ticker}")
        files[ticker] = path.resolve()
    return files


def load_membership(path: Path | None) -> pd.DataFrame | None:
    if path is None:
        return None
    if path.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)
    required = {"ticker", "index_code", "effective_from", "effective_to"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise DatasetBuildError(f"index_membership 缺少字段：{missing}")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].map(normalize_ticker)
    frame["index_code"] = frame["index_code"].astype(str).str.upper().str.replace(r"\.SH$", "", regex=True)
    frame = frame[frame["index_code"].isin({"CSI300", "CSI500", "000300", "000905"})]
    frame["effective_from"] = pd.to_datetime(frame["effective_from"], errors="coerce")
    effective_to_raw = frame["effective_to"].astype("string").str.strip()
    open_ended = effective_to_raw.isna() | effective_to_raw.eq("")
    frame["effective_to"] = pd.to_datetime(effective_to_raw.mask(open_ended), errors="coerce")
    frame.loc[open_ended, "effective_to"] = pd.Timestamp.max.normalize()
    if frame["effective_from"].isna().any() or frame["effective_to"].isna().any():
        raise DatasetBuildError("index_membership 有无效日期")
    if (frame["effective_from"] > frame["effective_to"]).any():
        raise DatasetBuildError("index_membership 有反向有效区间")
    return frame


def load_suspensions(path: Path | None) -> pd.DataFrame | None:
    if path is None:
        return None
    if path.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)
    required = {"ticker", "trade_date", "is_suspended"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise DatasetBuildError(f"suspensions 缺少字段：{missing}")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].map(normalize_ticker)
    frame["trade_date"] = pd.to_datetime(frame["trade_date"], errors="coerce").dt.normalize()
    if frame["trade_date"].isna().any():
        raise DatasetBuildError("suspensions 有无效日期")

    true_values = {"1", "true", "yes", "y"}
    false_values = {"0", "false", "no", "n"}

    def parse_boolean(value: Any) -> bool:
        if isinstance(value, (bool, np.bool_)):
            return bool(value)
        if isinstance(value, (int, np.integer)) and int(value) in {0, 1}:
            return bool(value)
        text = str(value).strip().lower()
        if text in true_values:
            return True
        if text in false_values:
            return False
        raise DatasetBuildError(f"suspensions.is_suspended 非布尔值：{value!r}")

    frame["is_suspended"] = frame["is_suspended"].map(parse_boolean)
    if frame.duplicated(["ticker", "trade_date"]).any():
        raise DatasetBuildError("suspensions 存在重复 ticker/trade_date")
    return frame.sort_values(["ticker", "trade_date"]).reset_index(drop=True)


def _split_periods(splits: Mapping[str, list[str]]) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    periods: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    for name in SPLIT_NAMES:
        raw = splits.get(name)
        if raw is None or len(raw) != 2:
            raise DatasetBuildError(f"split {name} 必须是 [start, end]")
        start, end = (pd.Timestamp(value).normalize() for value in raw)
        if pd.isna(start) or pd.isna(end) or start > end:
            raise DatasetBuildError(f"split {name} 日期区间无效")
        periods.append((start, end))
    return periods


def audit_membership_market_coverage(
    snapshot_root: Path,
    *,
    membership: pd.DataFrame,
    suspensions: pd.DataFrame,
    splits: Mapping[str, list[str]],
    benchmark_ticker: str = "sh000906",
    day_files: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Prove PIT index members have a quote or an explicit suspension each day.

    The audit is deliberately independent of generated training windows.  It
    walks the complete point-in-time CSI300/CSI500 membership across every
    configured split date so a missing historical ``.day`` file cannot be
    hidden by simply producing no samples for that security.
    """

    files = dict(day_files) if day_files is not None else discover_day_files(snapshot_root)
    if benchmark_ticker not in files:
        raise DatasetBuildError(f"快照缺少基准 {benchmark_ticker}.day")
    periods = _split_periods(splits)
    benchmark = read_day_file(files[benchmark_ticker])
    benchmark_dates = pd.to_datetime(
        benchmark["date"].astype(str), format="%Y%m%d", errors="raise"
    ).dt.normalize()
    pit_dates = suspensions["trade_date"].drop_duplicates().sort_values()
    calendar = pd.DatetimeIndex(benchmark_dates).union(pd.DatetimeIndex(pit_dates)).sort_values()
    in_scope = np.zeros(len(calendar), dtype=bool)
    for start, end in periods:
        in_scope |= (calendar >= start) & (calendar <= end)
    calendar = calendar[in_scope]
    if calendar.empty:
        raise DatasetBuildError("survivorship_bias_guard_failed: no_in_scope_trade_dates")
    calendar_values = calendar.to_numpy(dtype="datetime64[ns]")
    calendar_ints = np.asarray(
        [int(value.strftime("%Y%m%d")) for value in calendar], dtype=np.int64
    )

    suspension_groups: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for ticker, group in suspensions.groupby("ticker", sort=False):
        dates = np.asarray(
            [int(value.strftime("%Y%m%d")) for value in group["trade_date"]],
            dtype=np.int64,
        )
        suspension_groups[str(ticker)] = (
            dates,
            group["is_suspended"].to_numpy(dtype=bool),
        )

    active_by_ticker: dict[str, np.ndarray] = {}
    for ticker, group in membership.groupby("ticker", sort=True):
        active = np.zeros(len(calendar), dtype=bool)
        for row in group.itertuples(index=False):
            start = np.datetime64(row.effective_from.to_datetime64())
            end = np.datetime64(row.effective_to.to_datetime64())
            active |= (calendar_values >= start) & (calendar_values <= end)
        if active.any():
            active_by_ticker[str(ticker)] = calendar_ints[active]

    missing_day_files: list[str] = []
    missing_suspension_state_count = 0
    unexplained_missing_quote_count = 0
    explicit_suspension_count = 0
    quote_count = 0
    checked_member_dates = 0
    examples: list[dict[str, Any]] = []
    file_digest = hashlib.sha256()
    for ticker, active_dates in active_by_ticker.items():
        checked_member_dates += len(active_dates)
        path = files.get(ticker)
        if path is None:
            missing_day_files.append(ticker)
            unexplained_missing_quote_count += len(active_dates)
            if len(examples) < 100:
                examples.append(
                    {
                        "ticker": ticker,
                        "trade_date": int(active_dates[0]),
                        "reason": "missing_historical_day_file",
                    }
                )
            continue

        frame = read_day_file(path)
        quote_dates = frame["date"].to_numpy(dtype=np.int64)
        quote_positions = np.searchsorted(quote_dates, active_dates)
        has_quote = quote_positions < len(quote_dates)
        has_quote[has_quote] &= quote_dates[quote_positions[has_quote]] == active_dates[has_quote]
        quote_count += int(has_quote.sum())
        file_digest.update(f"{ticker}:{sha256_file(path)}\n".encode("ascii"))

        state_dates, state_values = suspension_groups.get(
            ticker,
            (np.empty(0, dtype=np.int64), np.empty(0, dtype=bool)),
        )
        state_positions = np.searchsorted(state_dates, active_dates)
        has_state = state_positions < len(state_dates)
        has_state[has_state] &= state_dates[state_positions[has_state]] == active_dates[has_state]
        state_is_suspended = np.zeros(len(active_dates), dtype=bool)
        state_is_suspended[has_state] = state_values[state_positions[has_state]]

        missing_quote = ~has_quote
        explained = missing_quote & has_state & state_is_suspended
        missing_state = missing_quote & ~has_state
        unexplained = missing_quote & ~explained
        explicit_suspension_count += int(explained.sum())
        missing_suspension_state_count += int(missing_state.sum())
        unexplained_missing_quote_count += int(unexplained.sum())
        if unexplained.any() and len(examples) < 100:
            for trade_date, lacks_state in zip(
                active_dates[unexplained], missing_state[unexplained], strict=True
            ):
                examples.append(
                    {
                        "ticker": ticker,
                        "trade_date": int(trade_date),
                        "reason": (
                            "missing_suspension_state"
                            if bool(lacks_state)
                            else "missing_quote_without_explicit_suspension"
                        ),
                    }
                )
                if len(examples) >= 100:
                    break

    verified = bool(active_by_ticker) and not (
        missing_day_files
        or missing_suspension_state_count
        or unexplained_missing_quote_count
    )
    return {
        "schema_version": "kronos-a-share-survivorship-audit-v1",
        "verified": verified,
        "trade_date_count": int(len(calendar)),
        "active_member_ticker_count": int(len(active_by_ticker)),
        "checked_member_dates": int(checked_member_dates),
        "quote_member_dates": int(quote_count),
        "explicit_suspension_member_dates": int(explicit_suspension_count),
        "missing_historical_day_file_count": int(len(missing_day_files)),
        "missing_historical_day_files": missing_day_files,
        "missing_suspension_state_member_dates": int(missing_suspension_state_count),
        "unexplained_missing_quote_member_dates": int(unexplained_missing_quote_count),
        "checked_day_files_sha256": file_digest.hexdigest(),
        "failure_examples": examples,
    }


def load_corporate_actions(path: Path | None) -> pd.DataFrame | None:
    if path is None:
        return None
    if path.suffix.lower() == ".parquet":
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)
    required = {
        "ticker",
        "announcement_date",
        "ex_date",
        "cash_div",
        "bonus_ratio",
        "rights_ratio",
        "rights_price",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise DatasetBuildError(f"corporate_actions 缺少字段：{missing}")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].map(normalize_ticker)
    for column in ("announcement_date", "ex_date"):
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    if frame[["announcement_date", "ex_date"]].isna().any().any():
        raise DatasetBuildError("corporate_actions 有无效日期")
    if (frame["announcement_date"] > frame["ex_date"]).any():
        raise DatasetBuildError("corporate_actions announcement_date 晚于 ex_date")
    for column in ("cash_div", "bonus_ratio", "rights_ratio", "rights_price"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any() or (frame[column] < 0).any():
            raise DatasetBuildError(f"corporate_actions.{column} 必须为非负数")
    return frame.sort_values(["ticker", "ex_date", "announcement_date"]).reset_index(drop=True)


def membership_contains(
    membership: pd.DataFrame | None,
    ticker: str,
    origin: pd.Timestamp,
) -> bool:
    if membership is None:
        return True
    rows = membership[membership["ticker"] == ticker]
    if rows.empty:
        return False
    return bool(((rows["effective_from"] <= origin) & (origin <= rows["effective_to"])).any())


def _split_for_window(
    window_start: pd.Timestamp,
    origin: pd.Timestamp,
    target: pd.Timestamp,
    splits: dict[str, list[str]],
    benchmark_dates: pd.DatetimeIndex,
    purge_days: int,
) -> str | None:
    for name in SPLIT_NAMES:
        if name not in splits or len(splits[name]) != 2:
            raise DatasetBuildError(f"split {name} 必须是 [start, end]")
        start, end = map(pd.Timestamp, splits[name])
        segment = benchmark_dates[(benchmark_dates >= start) & (benchmark_dates <= end)]
        if len(segment) <= purge_days:
            continue
        latest_origin = segment[-purge_days - 1]
        if start <= window_start and origin <= latest_origin and target <= end:
            return name
    return None


def _benchmark_returns(frame: pd.DataFrame, horizon: int) -> dict[tuple[int, int], float]:
    dates = frame["date"].to_numpy(dtype=np.int64)
    close = frame["close"].to_numpy(dtype=np.float64)
    result: dict[tuple[int, int], float] = {}
    for index in range(0, len(frame) - horizon):
        result[(int(dates[index]), int(dates[index + horizon]))] = float(
            math.log(close[index + horizon] / close[index])
        )
    return result


def _event_adjustment_factor(frame: pd.DataFrame, event: Any, ticker: str) -> float:
    ex_date_i = int(event.ex_date.strftime("%Y%m%d"))
    all_dates = frame["date"].to_numpy(dtype=np.int64)
    prior_positions = np.flatnonzero(all_dates < ex_date_i)
    if prior_positions.size == 0:
        raise DatasetBuildError(
            f"corporate action 缺少除权日前收盘价：{ticker} {event.ex_date.date()}"
        )
    previous_close = float(frame.iloc[int(prior_positions[-1])]["close"])
    denominator = 1.0 + float(event.bonus_ratio) + float(event.rights_ratio)
    reference = (
        previous_close
        - float(event.cash_div)
        + float(event.rights_ratio) * float(event.rights_price)
    ) / denominator
    factor = reference / previous_close
    if not math.isfinite(factor) or factor <= 0:
        raise DatasetBuildError(
            f"corporate action 复权因子无效：{ticker} {event.ex_date.date()}"
        )
    return factor


def realized_total_log_return(
    frame: pd.DataFrame,
    *,
    origin_index: int,
    target_index: int,
    corporate_actions: pd.DataFrame | None,
    ticker: str,
) -> float:
    start_close = float(frame.iloc[origin_index]["close"])
    end_close = float(frame.iloc[target_index]["close"])
    if corporate_actions is not None:
        origin = pd.to_datetime(str(int(frame.iloc[origin_index]["date"])), format="%Y%m%d")
        target = pd.to_datetime(str(int(frame.iloc[target_index]["date"])), format="%Y%m%d")
        events = corporate_actions[
            (corporate_actions["ticker"] == normalize_ticker(ticker))
            & (corporate_actions["announcement_date"] <= target)
            & (corporate_actions["ex_date"] > origin)
            & (corporate_actions["ex_date"] <= target)
        ]
        for event in events.itertuples(index=False):
            start_close *= _event_adjustment_factor(frame, event, ticker)
    return float(math.log(end_close / start_close))


def build_sample_index(
    snapshot_root: Path,
    output_directory: Path,
    training_root: Path,
    *,
    splits: dict[str, list[str]],
    membership_path: Path | None = None,
    suspensions_path: Path | None = None,
    corporate_actions_path: Path | None = None,
    benchmark_ticker: str = "sh000906",
    spec: WindowSpec | None = None,
    max_samples_per_split: int | None = None,
    seed: int = 100,
    trade_state_checker: Callable[[str, pd.Timestamp, float], Mapping[str, Any]] | None = None,
    require_complete_membership_coverage: bool = False,
) -> dict[str, Any]:
    """Create a deterministic sample index; it does not tokenize or load Kronos."""

    window = spec or WindowSpec()
    if window.lookback != 90 or window.horizon != 10 or window.purge_days != 11:
        raise DatasetBuildError("kronos-a-share-v1 固定 lookback=90,horizon=10,purge_days=11")
    if max_samples_per_split is not None and max_samples_per_split < 1:
        raise DatasetBuildError("max_samples_per_split 必须为正整数")
    snapshot_root = ensure_within(snapshot_root, training_root)
    output = ensure_within(output_directory, training_root)
    output.mkdir(parents=True, exist_ok=True)
    if membership_path is not None:
        membership_path = ensure_within(membership_path, training_root)
    if suspensions_path is not None:
        suspensions_path = ensure_within(suspensions_path, training_root)
    if corporate_actions_path is not None:
        corporate_actions_path = ensure_within(corporate_actions_path, training_root)
    files = discover_day_files(snapshot_root)
    if benchmark_ticker not in files:
        raise DatasetBuildError(f"快照缺少基准 {benchmark_ticker}.day")
    membership = load_membership(membership_path)
    suspensions = load_suspensions(suspensions_path)
    corporate_actions = load_corporate_actions(corporate_actions_path)
    if membership is not None and suspensions is not None:
        survivorship_audit = audit_membership_market_coverage(
            snapshot_root,
            membership=membership,
            suspensions=suspensions,
            splits=splits,
            benchmark_ticker=benchmark_ticker,
            day_files=files,
        )
    else:
        survivorship_audit = {
            "schema_version": "kronos-a-share-survivorship-audit-v1",
            "verified": False,
            "reason": "index_membership_or_suspensions_unavailable",
        }
    if require_complete_membership_coverage and survivorship_audit.get("verified") is not True:
        raise DatasetBuildError(
            "survivorship_bias_guard_failed: "
            f"missing_historical_day_files="
            f"{survivorship_audit.get('missing_historical_day_file_count', 'N/A')}, "
            f"missing_suspension_state_member_dates="
            f"{survivorship_audit.get('missing_suspension_state_member_dates', 'N/A')}, "
            f"unexplained_missing_quote_member_dates="
            f"{survivorship_audit.get('unexplained_missing_quote_member_dates', 'N/A')}"
        )
    benchmark = read_day_file(files[benchmark_ticker])
    benchmark_returns = _benchmark_returns(benchmark, window.horizon)
    benchmark_dates_i = benchmark["date"].to_numpy(dtype=np.int64)
    benchmark_dates = pd.DatetimeIndex(
        pd.to_datetime(benchmark_dates_i.astype(str), format="%Y%m%d")
    )
    benchmark_positions = {
        int(trade_date): index for index, trade_date in enumerate(benchmark_dates_i)
    }
    rows: list[dict[str, Any]] = []
    selected_split_counts = {name: 0 for name in SPLIT_NAMES}
    selected_ticker_split_counts: dict[tuple[str, str], int] = {}
    skipped = {
        "invalid_or_short": 0,
        "not_member": 0,
        "benchmark_gap": 0,
        "suspension_or_calendar_gap": 0,
        "outside_split": 0,
        "unconfirmed_trade_state": 0,
        "ineligible_trade_state": 0,
    }
    for ticker, path in sorted(files.items()):
        if max_samples_per_split is not None and all(
            selected_split_counts[name] >= max_samples_per_split
            for name in SPLIT_NAMES
        ):
            break
        if not A_SHARE_PATTERN.fullmatch(ticker):
            continue
        try:
            frame = read_day_file(path)
        except DatasetBuildError:
            skipped["invalid_or_short"] += 1
            continue
        if len(frame) < window.total_bars:
            skipped["invalid_or_short"] += 1
            continue
        for start_index in range(0, len(frame) - window.total_bars + 1):
            if max_samples_per_split is not None and all(
                selected_split_counts[name] >= max_samples_per_split
                or selected_ticker_split_counts.get((ticker, name), 0) >= 1
                for name in SPLIT_NAMES
            ):
                break
            origin_index = start_index + window.lookback - 1
            target_index = origin_index + window.horizon
            window_dates_i = frame.iloc[
                start_index : start_index + window.total_bars
            ]["date"].to_numpy(dtype=np.int64)
            origin_date_i = int(frame.iloc[origin_index]["date"])
            target_date_i = int(frame.iloc[target_index]["date"])
            benchmark_origin = benchmark_positions.get(origin_date_i)
            benchmark_start = (
                None if benchmark_origin is None else benchmark_origin - window.lookback + 1
            )
            benchmark_end = (
                None if benchmark_origin is None else benchmark_origin + window.horizon + 1
            )
            if (
                benchmark_start is None
                or benchmark_start < 0
                or benchmark_end is None
                or benchmark_end > len(benchmark_dates_i)
                or not np.array_equal(
                    window_dates_i,
                    benchmark_dates_i[benchmark_start:benchmark_end],
                )
            ):
                skipped["suspension_or_calendar_gap"] += 1
                continue
            window_start = pd.to_datetime(str(int(window_dates_i[0])), format="%Y%m%d")
            origin = pd.to_datetime(str(origin_date_i), format="%Y%m%d")
            target = pd.to_datetime(str(target_date_i), format="%Y%m%d")
            split = _split_for_window(
                window_start,
                origin,
                target,
                splits,
                benchmark_dates,
                window.purge_days,
            )
            if split is None:
                skipped["outside_split"] += 1
                continue
            if (
                max_samples_per_split is not None
                and (
                    selected_split_counts[split] >= max_samples_per_split
                    or selected_ticker_split_counts.get((ticker, split), 0) >= 1
                )
            ):
                continue
            if not membership_contains(membership, ticker, origin):
                skipped["not_member"] += 1
                continue
            if trade_state_checker is not None:
                trade_state = trade_state_checker(
                    ticker,
                    origin,
                    float(frame.iloc[origin_index]["close"]),
                )
                if trade_state.get("state_confirmed") is not True:
                    skipped["unconfirmed_trade_state"] += 1
                    continue
                if trade_state.get("eligible_for_formal_sample") is not True:
                    skipped["ineligible_trade_state"] += 1
                    continue
            benchmark_return = benchmark_returns.get((origin_date_i, target_date_i))
            if benchmark_return is None:
                skipped["benchmark_gap"] += 1
                continue
            stock_return = realized_total_log_return(
                frame,
                origin_index=origin_index,
                target_index=target_index,
                corporate_actions=corporate_actions,
                ticker=ticker,
            )
            label = stock_return - benchmark_return
            rows.append(
                {
                    "ticker": ticker,
                    "day_file": str(path),
                    "start_index": start_index,
                    "origin_date": origin_date_i,
                    "target_date": target_date_i,
                    "split": split,
                    "label_excess_10d": label,
                }
            )
            selected_split_counts[split] += 1
            selected_ticker_split_counts[(ticker, split)] = (
                selected_ticker_split_counts.get((ticker, split), 0) + 1
            )
    index_frame = pd.DataFrame(rows)
    if index_frame.empty:
        raise DatasetBuildError("没有满足窗口、切分和股票池条件的样本")
    if max_samples_per_split is not None:
        if any(
            selected_split_counts[name] > max_samples_per_split
            for name in SPLIT_NAMES
        ):
            raise DatasetBuildError("smoke 有界采样超过 max_samples_per_split")
    index_frame = index_frame.sort_values(["origin_date", "ticker", "start_index"]).reset_index(drop=True)
    index_frame.insert(0, "sample_id", np.arange(len(index_frame), dtype=np.int64))
    index_path = output / "sample_index.csv"
    atomic_write(index_path, index_frame.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    counts = {name: int((index_frame["split"] == name).sum()) for name in SPLIT_NAMES}
    manifest = {
        "schema_version": WINDOW_SCHEMA,
        "status": (
            "production_candidate"
            if (
                membership is not None
                and suspensions is not None
                and corporate_actions is not None
                and trade_state_checker is not None
                and survivorship_audit.get("verified") is True
            )
            else "local_provisional"
        ),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_root": str(snapshot_root.resolve()),
        "snapshot_manifest_sha256": (
            sha256_file(snapshot_root / "source_manifest.json")
            if (snapshot_root / "source_manifest.json").is_file()
            else None
        ),
        "sample_index": str(index_path),
        "sample_index_sha256": sha256_file(index_path),
        "sample_count": int(len(index_frame)),
        "split_counts": counts,
        "membership_path": str(membership_path.resolve()) if membership_path else None,
        "membership_sha256": sha256_file(membership_path) if membership_path else None,
        "suspensions_path": str(suspensions_path.resolve()) if suspensions_path else None,
        "suspensions_sha256": sha256_file(suspensions_path) if suspensions_path else None,
        "corporate_actions_path": (
            str(corporate_actions_path.resolve()) if corporate_actions_path else None
        ),
        "corporate_actions_sha256": (
            sha256_file(corporate_actions_path) if corporate_actions_path else None
        ),
        "benchmark_ticker": benchmark_ticker,
        "sample_trade_state_checked": trade_state_checker is not None,
        "survivorship_bias_audit": survivorship_audit,
        "selection": {
            "mode": "deterministic_bounded_smoke" if max_samples_per_split else "full",
            "max_samples_per_split": max_samples_per_split,
            "max_samples_per_ticker_per_split": 1 if max_samples_per_split else None,
            "seed": seed,
        },
        "window": {"lookback": window.lookback, "horizon": window.horizon, "purge_days": window.purge_days},
        "label_contract": {
            "name": "future_10d_excess_log_return_vs_csi800",
            "scale": "natural_log_return",
            "stock_price_mode": (
                "realized_total_return" if corporate_actions is not None else "raw_local_provisional"
            ),
            "benchmark_price_mode": "csi800_close_to_close",
        },
        "estimated_token_cache_bytes": int(len(index_frame) * (window.total_bars * 9 + 12)),
        "skipped": skipped,
    }
    manifest_path = output / "sample_manifest.json"
    atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return manifest


def causal_adjusted_price_window(
    frame: pd.DataFrame,
    start_index: int,
    spec: WindowSpec,
    *,
    corporate_actions: pd.DataFrame | None,
    ticker: str,
    origin_date: int,
) -> tuple[np.ndarray, int]:
    """Return the raw-scale window after point-in-time causal adjustment.

    Only corporate actions both announced and effective by ``origin_date`` may
    alter the historical price columns.  Keeping this raw-scale representation
    separate lets the scorer and the autoregressive forecast path consume the
    exact same adjusted history before each applies its own normalization.
    """

    values = frame.iloc[start_index : start_index + spec.total_bars][FEATURE_COLUMNS].to_numpy(
        dtype=np.float32,
        copy=True,
    )
    if values.shape != (spec.total_bars, len(FEATURE_COLUMNS)):
        raise DatasetBuildError("样本窗口长度不足")
    applied_event_count = 0
    if corporate_actions is not None:
        origin = pd.to_datetime(str(int(origin_date)), format="%Y%m%d")
        events = corporate_actions[
            (corporate_actions["ticker"] == normalize_ticker(ticker))
            & (corporate_actions["announcement_date"] <= origin)
            & (corporate_actions["ex_date"] <= origin)
        ]
        all_dates = frame["date"].to_numpy(dtype=np.int64)
        window_dates = frame.iloc[
            start_index : start_index + spec.total_bars
        ]["date"].to_numpy(dtype=np.int64)
        for event in events.itertuples(index=False):
            ex_date_i = int(event.ex_date.strftime("%Y%m%d"))
            affected = window_dates < ex_date_i
            if not bool(affected.any()):
                continue
            factor = _event_adjustment_factor(frame, event, ticker)
            values[affected, :PRICE_COLUMN_COUNT] *= np.float32(factor)
            applied_event_count += 1
    return values, applied_event_count


def causal_adjusted_normalized_window(
    frame: pd.DataFrame,
    start_index: int,
    spec: WindowSpec,
    *,
    corporate_actions: pd.DataFrame | None,
    ticker: str,
    origin_date: int,
) -> tuple[np.ndarray, int]:
    values, applied_event_count = causal_adjusted_price_window(
        frame,
        start_index,
        spec,
        corporate_actions=corporate_actions,
        ticker=ticker,
        origin_date=origin_date,
    )
    past = values[: spec.lookback]
    mean = past.mean(axis=0)
    std = past.std(axis=0)
    normalized = (values - mean) / (std + np.float32(1e-5))
    return np.clip(normalized, -spec.clip, spec.clip).astype(np.float32), applied_event_count


def normalized_window(frame: pd.DataFrame, start_index: int, spec: WindowSpec) -> np.ndarray:
    values, _ = causal_adjusted_normalized_window(
        frame,
        start_index,
        spec,
        corporate_actions=None,
        ticker="sh600000",
        origin_date=int(frame.iloc[start_index + spec.lookback - 1]["date"]),
    )
    return values


def time_stamps(dates: np.ndarray) -> np.ndarray:
    parsed = pd.to_datetime(dates.astype(str), format="%Y%m%d")
    return np.column_stack(
        [
            np.zeros(len(parsed), dtype=np.uint8),
            np.full(len(parsed), 15, dtype=np.uint8),
            parsed.weekday.astype(np.uint8),
            parsed.day.astype(np.uint8),
            parsed.month.astype(np.uint8),
        ]
    )


def _flush_token_batch(tokenizer: Any, torch: Any, device: str, batch: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    values = torch.from_numpy(np.stack(batch)).to(device)
    with torch.inference_mode():
        s1, s2 = tokenizer.encode(values, half=True)
    return s1.detach().cpu().numpy().astype(np.uint16), s2.detach().cpu().numpy().astype(np.uint16)


def _close_token_memmaps(arrays: Mapping[str, Any]) -> None:
    """Flush and close numpy memmaps before a Windows directory rename."""

    for array in arrays.values():
        array.flush()
    for array in arrays.values():
        memory_map = getattr(array, "_mmap", None)
        if memory_map is not None and not memory_map.closed:
            memory_map.close()
    gc.collect()


def tokenize_sample_index(
    sample_index_path: Path,
    output_directory: Path,
    training_root: Path,
    *,
    tokenizer: Any,
    tokenizer_sha256: str,
    corporate_actions_path: Path | None = None,
    device: str,
    batch_size: int = 64,
    spec: WindowSpec | None = None,
) -> dict[str, Any]:
    """Pre-tokenize deterministic windows into memory-mapped arrays."""

    import torch

    window = spec or WindowSpec()
    sample_index_path = ensure_within(sample_index_path, training_root)
    output = ensure_within(output_directory, training_root)
    if output.exists():
        raise DatasetBuildError(f"token cache 已存在：{output}")
    if batch_size < 1:
        raise DatasetBuildError("batch_size 必须为正整数")
    index_frame = pd.read_csv(sample_index_path)
    sample_manifest_path = sample_index_path.parent / "sample_manifest.json"
    if not sample_manifest_path.is_file():
        raise DatasetBuildError("缺少 sample_manifest.json，拒绝生成无来源绑定的 token cache")
    sample_manifest = json.loads(sample_manifest_path.read_text(encoding="utf-8"))
    if sample_manifest.get("sample_index_sha256") != sha256_file(sample_index_path):
        raise DatasetBuildError("sample_index 与 sample_manifest SHA256 不匹配")
    if corporate_actions_path is not None:
        corporate_actions_path = ensure_within(corporate_actions_path, training_root)
    expected_actions_path = sample_manifest.get("corporate_actions_path")
    actual_actions_path = str(corporate_actions_path) if corporate_actions_path else None
    if expected_actions_path != actual_actions_path:
        raise DatasetBuildError("corporate_actions 路径与 sample_manifest 不匹配")
    if corporate_actions_path is not None and sample_manifest.get(
        "corporate_actions_sha256"
    ) != sha256_file(corporate_actions_path):
        raise DatasetBuildError("corporate_actions SHA256 与 sample_manifest 不匹配")
    corporate_actions = load_corporate_actions(corporate_actions_path)
    required = {"sample_id", "ticker", "day_file", "start_index", "origin_date", "split", "label_excess_10d"}
    missing = sorted(required - set(index_frame.columns))
    if missing:
        raise DatasetBuildError(f"sample_index 缺少字段：{missing}")
    sample_ids = pd.to_numeric(index_frame["sample_id"], errors="raise").astype(int)
    if sorted(sample_ids.tolist()) != list(range(len(index_frame))):
        raise DatasetBuildError("sample_id 必须从0连续递增")
    pending = output.with_name(f".{output.name}.pending-{os.getpid()}")
    if pending.exists():
        shutil.rmtree(pending)
    pending.mkdir(parents=True)
    count = len(index_frame)
    arrays = {
        "s1.npy": np.lib.format.open_memmap(pending / "s1.npy", mode="w+", dtype=np.uint16, shape=(count, window.total_bars)),
        "s2.npy": np.lib.format.open_memmap(pending / "s2.npy", mode="w+", dtype=np.uint16, shape=(count, window.total_bars)),
        "stamp.npy": np.lib.format.open_memmap(pending / "stamp.npy", mode="w+", dtype=np.uint8, shape=(count, window.total_bars, 5)),
        "label.npy": np.lib.format.open_memmap(pending / "label.npy", mode="w+", dtype=np.float32, shape=(count,)),
        "trade_date.npy": np.lib.format.open_memmap(pending / "trade_date.npy", mode="w+", dtype=np.int32, shape=(count,)),
        "instrument_id.npy": np.lib.format.open_memmap(pending / "instrument_id.npy", mode="w+", dtype=np.int32, shape=(count,)),
        "split.npy": np.lib.format.open_memmap(pending / "split.npy", mode="w+", dtype=np.uint8, shape=(count,)),
    }
    instruments = {ticker: index for index, ticker in enumerate(sorted(index_frame["ticker"].unique()))}
    batch_values: list[np.ndarray] = []
    batch_destinations: list[int] = []
    cache_path: str | None = None
    cache_frame: pd.DataFrame | None = None
    applied_event_count = 0

    def flush() -> None:
        if not batch_values:
            return
        s1, s2 = _flush_token_batch(tokenizer, torch, device, batch_values)
        arrays["s1.npy"][batch_destinations] = s1
        arrays["s2.npy"][batch_destinations] = s2
        batch_values.clear()
        batch_destinations.clear()

    try:
        for row in index_frame.sort_values(["day_file", "start_index"]).itertuples(index=False):
            if row.day_file != cache_path:
                cache_path = row.day_file
                cache_frame = read_day_file(ensure_within(Path(cache_path), training_root))
            assert cache_frame is not None
            start = int(row.start_index)
            destination = int(row.sample_id)
            adjusted, applied = causal_adjusted_normalized_window(
                cache_frame,
                start,
                window,
                corporate_actions=corporate_actions,
                ticker=str(row.ticker),
                origin_date=int(row.origin_date),
            )
            batch_values.append(adjusted)
            applied_event_count += applied
            batch_destinations.append(destination)
            dates = cache_frame.iloc[start : start + window.total_bars]["date"].to_numpy(dtype=np.int64)
            arrays["stamp.npy"][destination] = time_stamps(dates)
            arrays["label.npy"][destination] = np.float32(row.label_excess_10d)
            arrays["trade_date.npy"][destination] = np.int32(row.origin_date)
            arrays["instrument_id.npy"][destination] = np.int32(instruments[row.ticker])
            arrays["split.npy"][destination] = np.uint8(SPLIT_CODES[row.split])
            if len(batch_values) >= batch_size:
                flush()
        flush()
        _close_token_memmaps(arrays)
        files = {}
        for path in sorted(pending.glob("*.npy")):
            files[path.name] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        manifest = {
            "schema_version": TOKEN_SCHEMA,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "sample_count": count,
            "sample_index_sha256": sha256_file(sample_index_path),
            "sample_index_path": str(sample_index_path),
            "sample_manifest_path": str(sample_manifest_path),
            "sample_manifest_sha256": sha256_file(sample_manifest_path),
            "snapshot_manifest_sha256": sample_manifest.get("snapshot_manifest_sha256"),
            "membership_sha256": sample_manifest.get("membership_sha256"),
            "corporate_actions_sha256": sample_manifest.get("corporate_actions_sha256"),
            "tokenizer_sha256": tokenizer_sha256,
            "window": {"lookback": window.lookback, "horizon": window.horizon},
            "dtype": {"s1": "uint16", "s2": "uint16", "stamp": "uint8", "label": "float32"},
            "instruments": instruments,
            "split_codes": SPLIT_CODES,
            "adjustment": {
                "mode": "causal_backward_total_return",
                "materialized": corporate_actions is not None,
                "trade_price_raw": True,
                "model_price_adjusted": corporate_actions is not None,
                "cutoff_field": "origin_date",
                "future_action_use_count": 0,
                "applied_event_count": applied_event_count,
                "corporate_actions_path": (
                    str(corporate_actions_path) if corporate_actions_path else None
                ),
            },
            "files": files,
        }
        atomic_write(pending / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        os.replace(pending, output)
        return manifest
    except BaseException:
        _close_token_memmaps(arrays)
        if pending.exists():
            shutil.rmtree(pending)
        raise


def load_token_cache(directory: Path, *, mmap_mode: str = "r") -> dict[str, Any]:
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != TOKEN_SCHEMA:
        raise DatasetBuildError("token cache schema_version 无效")
    required_layout = {
        "s1.npy": (np.dtype("uint16"), (int(manifest["sample_count"]), 100)),
        "s2.npy": (np.dtype("uint16"), (int(manifest["sample_count"]), 100)),
        "stamp.npy": (np.dtype("uint8"), (int(manifest["sample_count"]), 100, 5)),
        "label.npy": (np.dtype("float32"), (int(manifest["sample_count"]),)),
        "trade_date.npy": (np.dtype("int32"), (int(manifest["sample_count"]),)),
        "instrument_id.npy": (np.dtype("int32"), (int(manifest["sample_count"]),)),
        "split.npy": (np.dtype("uint8"), (int(manifest["sample_count"]),)),
    }
    file_contract = manifest.get("files")
    if not isinstance(file_contract, dict) or set(file_contract) != set(required_layout):
        raise DatasetBuildError("token cache files 合同不完整")
    arrays: dict[str, Any] = {}
    for filename, (expected_dtype, expected_shape) in required_layout.items():
        path = directory / filename
        if not path.is_file():
            raise DatasetBuildError(f"token cache 缺少文件：{filename}")
        contract = file_contract[filename]
        if int(contract.get("bytes", -1)) != path.stat().st_size:
            raise DatasetBuildError(f"token cache {filename} 字节数不匹配")
        if contract.get("sha256") != sha256_file(path):
            raise DatasetBuildError(f"token cache {filename} SHA256 不匹配")
        array = np.load(path, mmap_mode=mmap_mode, allow_pickle=False)
        if array.dtype != expected_dtype or array.shape != expected_shape:
            raise DatasetBuildError(
                f"token cache {filename} dtype/shape 不匹配：{array.dtype}/{array.shape}"
            )
        arrays[path.stem] = array
    expected = int(manifest["sample_count"])
    for name, array in arrays.items():
        if len(array) != expected:
            raise DatasetBuildError(f"token cache {name} 行数与 manifest 不一致")
    return {"manifest": manifest, "arrays": arrays}
