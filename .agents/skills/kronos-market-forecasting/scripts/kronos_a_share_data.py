from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import struct
import tempfile
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_TRAINING_ROOT = PROJECT_ROOT / "_training" / "kronos_ashare"
DEFAULT_TDX_ROOT = Path(r"D:\HT")

TDX_DAY_RECORD = struct.Struct("<IIIIIfII")
TDX_DAY_RECORD_SIZE = TDX_DAY_RECORD.size
LOOKBACK = 90
HORIZON = 10
PURGE_SESSIONS = 11
PIT_START = date(2018, 1, 2)
PIT_END = date(2026, 7, 31)


class AShareDataError(RuntimeError):
    """Base error for the A-share data preparation module."""


class UnsafePathError(AShareDataError):
    """Raised when a requested write target is outside the guarded tree."""


class TdxDayFormatError(AShareDataError):
    """Raised when a TDX .day file violates the fixed binary contract."""


class SnapshotSourceChangedError(AShareDataError):
    """Raised when an active source changes while a snapshot is being built."""


class PitContractError(AShareDataError):
    """Raised when an external PIT table violates its declared contract."""


@dataclass(frozen=True)
class DateSplit:
    name: str
    start: date
    end: date


FIXED_SPLITS: tuple[DateSplit, ...] = (
    DateSplit("train", date(2018, 1, 2), date(2022, 12, 30)),
    DateSplit("validation", date(2023, 1, 3), date(2024, 6, 28)),
    DateSplit("development_test", date(2024, 7, 1), date(2025, 6, 30)),
    DateSplit("locked_retrospective", date(2025, 7, 1), date(2026, 7, 31)),
)


@dataclass(frozen=True)
class SnapshotSource:
    source_path: Path
    source_relative: str
    destination_relative: str
    kind: str
    market: str | None = None
    code: str | None = None


@dataclass(frozen=True)
class PitTableSpec:
    required_columns: tuple[str, ...]
    optional_columns: tuple[str, ...] = ()
    required_dates: tuple[str, ...] = ()
    nullable_dates: tuple[str, ...] = ()
    interval: tuple[str, str] | None = None
    interval_keys: tuple[str, ...] = ()


PIT_TABLE_SPECS: dict[str, PitTableSpec] = {
    "security_master": PitTableSpec(
        required_columns=(
            "ticker",
            "exchange",
            "board",
            "security_type",
            "list_date",
            "delist_date",
        ),
        required_dates=("list_date",),
        nullable_dates=("delist_date",),
        interval=("list_date", "delist_date"),
        interval_keys=("ticker",),
    ),
    "st_status": PitTableSpec(
        required_columns=("ticker", "effective_from", "effective_to", "is_st"),
        required_dates=("effective_from",),
        nullable_dates=("effective_to",),
        interval=("effective_from", "effective_to"),
        interval_keys=("ticker",),
    ),
    "suspensions": PitTableSpec(
        required_columns=("ticker", "trade_date", "is_suspended"),
        required_dates=("trade_date",),
    ),
    "price_limits": PitTableSpec(
        required_columns=("ticker", "trade_date", "up_limit", "down_limit"),
        optional_columns=(
            "rule_version",
            "no_limit_reason",
            "previous_trade_date",
            "previous_close_raw",
        ),
        required_dates=("trade_date",),
        nullable_dates=("previous_trade_date",),
    ),
    "index_membership": PitTableSpec(
        required_columns=("index_code", "ticker", "effective_from", "effective_to"),
        required_dates=("effective_from",),
        nullable_dates=("effective_to",),
        interval=("effective_from", "effective_to"),
        interval_keys=("index_code", "ticker"),
    ),
    "corporate_actions": PitTableSpec(
        required_columns=(
            "ticker",
            "announcement_date",
            "ex_date",
            "cash_div",
            "bonus_ratio",
            "rights_ratio",
            "rights_price",
        ),
        required_dates=("announcement_date", "ex_date"),
    ),
    "trading_calendar": PitTableSpec(
        required_columns=("trade_date", "is_open"),
        optional_columns=("benchmark_ticker",),
        required_dates=("trade_date",),
    ),
    "coverage": PitTableSpec(
        required_columns=("dataset", "coverage_start", "coverage_end", "is_complete"),
        optional_columns=(
            "binding_schema",
            "file_sha256",
            "schema_sha256",
            "row_count",
            "file_bytes",
            "source_manifest",
            "source_manifest_sha256",
        ),
        required_dates=("coverage_start", "coverage_end"),
    ),
}

TRADING_CALENDAR_TABLE = "trading_calendar"
MANDATORY_PIT_TABLES = tuple(
    table_name
    for table_name in PIT_TABLE_SPECS
    if table_name not in {TRADING_CALENDAR_TABLE}
)
REQUIRED_INDEX_CODES = ("000300.SH", "000905.SH")
PIT_COVERAGE_BINDING_SCHEMA = "kronos-a-share-pit-coverage-v1"
PIT_PROVENANCE_SCHEMA = "kronos-a-share-pit-provenance-v1"
MINIMUM_LISTING_DAYS = 120
PIT_PROVENANCE_DATASETS = (
    "security_master",
    "st_status",
    "suspensions",
    "price_limits",
    "index_membership",
    "corporate_actions",
    TRADING_CALENDAR_TABLE,
)
COVERAGE_BINDING_COLUMNS = (
    "binding_schema",
    "file_sha256",
    "schema_sha256",
    "row_count",
    "file_bytes",
    "source_manifest",
    "source_manifest_sha256",
)
REQUIRED_CAPABILITIES = (
    "security_master_history",
    "st_history",
    "suspension_history",
    "price_limit_history",
    "corporate_action_history",
    "csi300_history",
    "csi500_history",
    "sample_trade_state_history",
    "trading_calendar_history",
)
MODEL_ADJUSTMENT_SCHEMA = "kronos-a-share-token-cache-v1"
INFERENCE_SNAPSHOT_SCHEMA = "kronos-a-share-inference-snapshot-v1"
INFERENCE_INPUT_BINDING_SCHEMA = "kronos-a-share-inference-input-v1"
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
INFERENCE_MARKET_RECORDS = LOOKBACK + 1

_TICKER_RE = re.compile(r"^\d{6}\.(?:SH|SZ|BJ)$")
_SNAPSHOT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
_TRUE_VALUES = {True, 1, "1", "true", "yes", "y"}
_FALSE_VALUES = {False, 0, "0", "false", "no", "n"}


@dataclass
class PitBundleValidation:
    frames: dict[str, pd.DataFrame]
    table_reports: dict[str, dict[str, Any]]
    missing_tables: list[str]
    errors: list[str]
    warnings: list[str]
    capabilities: dict[str, bool]

    @property
    def production_ready(self) -> bool:
        return (
            not self.errors
            and not self.missing_tables
            and all(self.capabilities.get(name, False) for name in REQUIRED_CAPABILITIES)
        )

    def to_report(self) -> dict[str, Any]:
        return {
            "table_reports": self.table_reports,
            "missing_tables": self.missing_tables,
            "errors": self.errors,
            "warnings": self.warnings,
            "capabilities": self.capabilities,
            "production_ready": self.production_ready,
        }


@dataclass(frozen=True)
class PriceLimitResult:
    up_limit: Decimal | None
    down_limit: Decimal | None
    ratio: Decimal | None
    rule_version: str
    no_limit_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "up_limit": str(self.up_limit) if self.up_limit is not None else None,
            "down_limit": str(self.down_limit) if self.down_limit is not None else None,
            "ratio": str(self.ratio) if self.ratio is not None else None,
            "rule_version": self.rule_version,
            "no_limit_reason": self.no_limit_reason,
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolved(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def guard_training_root(
    path: str | os.PathLike[str],
    *,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
) -> Path:
    """Allow writes only below <project>/_training/kronos_ashare."""

    project = _resolved(project_root)
    allowed_lexical = Path(os.path.abspath(project / "_training" / "kronos_ashare"))
    candidate_lexical = Path(os.path.abspath(Path(path).expanduser()))
    if candidate_lexical != allowed_lexical and allowed_lexical not in candidate_lexical.parents:
        raise UnsafePathError(f"path_outside_training_root: {candidate_lexical}")
    candidate = _resolved(candidate_lexical)
    allowed = _resolved(allowed_lexical)
    if candidate != allowed and allowed not in candidate.parents:
        raise UnsafePathError(f"path_outside_training_root: {candidate}")
    if candidate != project and project not in candidate.parents:
        raise UnsafePathError(f"path_outside_training_root: {candidate}")
    if candidate == Path(candidate.anchor):
        raise UnsafePathError(f"path_outside_training_root: {candidate}")
    return candidate


def guard_output_path(
    path: str | os.PathLike[str],
    *,
    training_root: str | os.PathLike[str] = DEFAULT_TRAINING_ROOT,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
) -> Path:
    root = guard_training_root(training_root, project_root=project_root)
    candidate = _resolved(path)
    if candidate == root or root not in candidate.parents:
        raise UnsafePathError(f"path_outside_training_root: {candidate}")
    return candidate


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _date_from_yyyymmdd(value: int, *, record_number: int, source: str) -> date:
    year, rem = divmod(value, 10000)
    month, day_value = divmod(rem, 100)
    try:
        return date(year, month, day_value)
    except ValueError as exc:
        raise TdxDayFormatError(
            f"{source}: 第 {record_number} 条记录日期非法: {value}"
        ) from exc


def _decode_tdx_day(raw: bytes, *, source: str, collect_rows: bool) -> tuple[dict[str, Any], list[tuple[Any, ...]]]:
    if not raw:
        raise TdxDayFormatError(f"{source}: 文件为空")
    if len(raw) % TDX_DAY_RECORD_SIZE:
        raise TdxDayFormatError(
            f"{source}: 文件长度 {len(raw)} 不是 {TDX_DAY_RECORD_SIZE} 的整数倍"
        )

    previous_date: date | None = None
    rows: list[tuple[Any, ...]] = []
    first_date: date | None = None
    last_date: date | None = None
    for index, record in enumerate(TDX_DAY_RECORD.iter_unpack(raw), start=1):
        raw_date, open_i, high_i, low_i, close_i, amount, volume, reserved = record
        trade_date = _date_from_yyyymmdd(raw_date, record_number=index, source=source)
        if previous_date is not None and trade_date <= previous_date:
            raise TdxDayFormatError(
                f"{source}: 日期未严格递增，第 {index} 条为 {trade_date.isoformat()}"
            )
        prices = (open_i, high_i, low_i, close_i)
        if any(value <= 0 for value in prices):
            raise TdxDayFormatError(f"{source}: 第 {index} 条存在非正价格")
        if high_i < max(open_i, close_i) or low_i > min(open_i, close_i) or high_i < low_i:
            raise TdxDayFormatError(f"{source}: 第 {index} 条 OHLC 结构非法")
        if not math.isfinite(amount) or amount < 0:
            raise TdxDayFormatError(f"{source}: 第 {index} 条成交额非法")
        if volume < 0:
            raise TdxDayFormatError(f"{source}: 第 {index} 条成交量非法")

        if collect_rows:
            rows.append(
                (
                    pd.Timestamp(trade_date),
                    open_i / 100.0,
                    high_i / 100.0,
                    low_i / 100.0,
                    close_i / 100.0,
                    float(amount),
                    int(volume),
                    int(reserved),
                )
            )
        first_date = first_date or trade_date
        last_date = trade_date
        previous_date = trade_date

    return (
        {
            "records": len(raw) // TDX_DAY_RECORD_SIZE,
            "first_date": first_date.isoformat() if first_date else None,
            "last_date": last_date.isoformat() if last_date else None,
            "size": len(raw),
        },
        rows,
    )


def read_tdx_day(path: str | os.PathLike[str]) -> pd.DataFrame:
    """Parse and validate one TDX daily file."""

    source = Path(path)
    raw = source.read_bytes()
    _, rows = _decode_tdx_day(raw, source=str(source), collect_rows=True)
    return pd.DataFrame(
        rows,
        columns=(
            "trade_date",
            "open",
            "high",
            "low",
            "close",
            "amount",
            "volume",
            "reserved",
        ),
    )


def inspect_tdx_day(path: str | os.PathLike[str]) -> dict[str, Any]:
    source = Path(path)
    raw = source.read_bytes()
    metadata, _ = _decode_tdx_day(raw, source=str(source), collect_rows=False)
    metadata["sha256"] = _sha256_bytes(raw)
    return metadata


def _is_a_share_code(market: str, code: str) -> bool:
    if not re.fullmatch(r"\d{6}", code):
        return False
    if market == "sh":
        return code.startswith(("600", "601", "603", "605", "688", "689"))
    if market == "sz":
        return code.startswith(("000", "001", "002", "003", "300", "301"))
    if market == "bj":
        return code.startswith(("4", "8", "92")) and not code.startswith("899")
    return False


_REQUIRED_BENCHMARKS = {
    ("sh", "000300"),  # CSI 300
    ("sh", "000905"),  # CSI 500
    ("sh", "000906"),  # CSI 800
}


def discover_snapshot_sources(source_root: str | os.PathLike[str]) -> list[SnapshotSource]:
    root = _resolved(source_root)
    sources: list[SnapshotSource] = []
    for market in ("sh", "sz", "bj"):
        daily_dir = root / "vipdoc" / market / "lday"
        if not daily_dir.is_dir():
            raise FileNotFoundError(f"缺少 TDX 日线目录: {daily_dir}")
        for path in sorted(daily_dir.glob(f"{market}*.day"), key=lambda item: item.name.lower()):
            code = path.stem[2:]
            if not _is_a_share_code(market, code) and (market, code) not in _REQUIRED_BENCHMARKS:
                continue
            relative = path.relative_to(root).as_posix()
            sources.append(
                SnapshotSource(
                    source_path=path,
                    source_relative=relative,
                    destination_relative=f"tdx_day/{market}/{path.name}",
                    kind="tdx_day",
                    market=market,
                    code=code,
                )
            )

    if not sources:
        raise FileNotFoundError(f"{root}: 未发现符合 A 股代码规则的 .day 文件")

    cache_dir = root / "T0002" / "hq_cache"
    for filename, kind in (("gbbq", "gbbq"), ("base.dbf", "base_dbf")):
        path = cache_dir / filename
        if not path.is_file() or path.stat().st_size <= 0:
            raise FileNotFoundError(f"缺少非空 TDX 原始文件: {path}")
        sources.append(
            SnapshotSource(
                source_path=path,
                source_relative=path.relative_to(root).as_posix(),
                destination_relative=f"hq_cache/{filename}",
                kind=kind,
            )
        )
    return sources


def _snapshot_id(value: str | None) -> str:
    candidate = value or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if not _SNAPSHOT_ID_RE.fullmatch(candidate):
        raise ValueError(f"snapshot_id 非法: {candidate!r}")
    return candidate


def _source_inventory(sources: Sequence[SnapshotSource]) -> tuple[str, ...]:
    return tuple(sorted(item.source_relative for item in sources))


def _cleanup_staging(
    staging: Path | None,
    *,
    training_root: Path,
    project_root: str | os.PathLike[str],
) -> None:
    if staging is None or not staging.exists():
        return
    guarded = guard_output_path(
        staging,
        training_root=training_root,
        project_root=project_root,
    )
    shutil.rmtree(guarded)


def create_immutable_snapshot(
    source_root: str | os.PathLike[str] = DEFAULT_TDX_ROOT,
    training_root: str | os.PathLike[str] = DEFAULT_TRAINING_ROOT,
    *,
    snapshot_id: str | None = None,
    dry_run: bool = True,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
) -> dict[str, Any]:
    """Validate and optionally copy an immutable, narrowly scoped TDX snapshot.

    The function never writes to ``source_root``. Actual copies require
    ``dry_run=False`` and are atomically promoted from a staging directory.
    """

    source = _resolved(source_root)
    target_root = guard_training_root(training_root, project_root=project_root)
    if source == target_root or source in target_root.parents or target_root in source.parents:
        raise UnsafePathError("TDX 源目录与训练目录不得相互包含")

    snapshot_name = _snapshot_id(snapshot_id)
    raw_root = target_root / "raw"
    final_path = guard_output_path(
        raw_root / snapshot_name,
        training_root=target_root,
        project_root=project_root,
    )
    raw_root = final_path.parent
    sources = discover_snapshot_sources(source)
    initial_inventory = _source_inventory(sources)
    if final_path.exists():
        raise FileExistsError(f"不可覆盖已有不可变快照: {final_path}")

    staging: Path | None = None
    entries: list[dict[str, Any]] = []
    initial_hashes: dict[str, str] = {}
    try:
        if not dry_run:
            raw_root.mkdir(parents=True, exist_ok=True)
            staging = Path(tempfile.mkdtemp(prefix=f".{snapshot_name}.pending-", dir=raw_root))

        for item in sources:
            if item.kind == "tdx_day":
                metadata = inspect_tdx_day(item.source_path)
            else:
                size = item.source_path.stat().st_size
                metadata = {"size": size, "sha256": _sha256_file(item.source_path)}
            initial_hashes[item.source_relative] = metadata["sha256"]

            destination_sha256: str | None = None
            if staging is not None:
                destination = staging / Path(item.destination_relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item.source_path, destination)
                destination_sha256 = _sha256_file(destination)
                if destination_sha256 != metadata["sha256"]:
                    raise SnapshotSourceChangedError(
                        f"复制后哈希不一致: {item.source_relative}"
                    )

            entries.append(
                {
                    "kind": item.kind,
                    "market": item.market,
                    "code": item.code,
                    "source_relative": item.source_relative,
                    "destination_relative": item.destination_relative,
                    "size": metadata["size"],
                    "sha256": metadata["sha256"],
                    "destination_sha256": destination_sha256,
                    "records": metadata.get("records"),
                    "first_date": metadata.get("first_date"),
                    "last_date": metadata.get("last_date"),
                }
            )

        final_sources = discover_snapshot_sources(source)
        if _source_inventory(final_sources) != initial_inventory:
            raise SnapshotSourceChangedError("快照期间 TDX 源文件清单发生变化")
        final_by_relative = {item.source_relative: item for item in final_sources}
        for relative, expected_hash in initial_hashes.items():
            current_hash = _sha256_file(final_by_relative[relative].source_path)
            if current_hash != expected_hash:
                raise SnapshotSourceChangedError(f"快照期间源文件发生变化: {relative}")

        kind_counts: dict[str, int] = {}
        for entry in entries:
            kind_counts[entry["kind"]] = kind_counts.get(entry["kind"], 0) + 1
        manifest = {
            "schema_version": 1,
            "snapshot_id": snapshot_name,
            "generated_at": _utc_now(),
            "source_root": str(source),
            "snapshot_path": str(final_path),
            "dry_run": dry_run,
            "source_consistent": True,
            "evidence_class": "market_data_vendor",
            "kind_counts": kind_counts,
            "files": entries,
        }

        if staging is not None:
            manifest_path = staging / "source_manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(staging, final_path)
            staging = None
        return manifest
    except Exception:
        _cleanup_staging(
            staging,
            training_root=target_root,
            project_root=project_root,
        )
        raise


def load_snapshot_manifest(path: str | os.PathLike[str]) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AShareDataError("source_manifest.json 顶层必须是对象")
    return payload


def verify_immutable_snapshot(
    manifest_path: str | os.PathLike[str],
    *,
    training_root: str | os.PathLike[str] = DEFAULT_TRAINING_ROOT,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
) -> dict[str, Any]:
    path = guard_training_root(manifest_path, project_root=project_root)
    guard_training_root(training_root, project_root=project_root)
    if not path.is_file() or path.name != "source_manifest.json":
        raise AShareDataError("snapshot manifest 路径无效")
    manifest = load_snapshot_manifest(path)
    if (
        manifest.get("schema_version") != 1
        or manifest.get("dry_run") is not False
        or manifest.get("source_consistent") is not True
    ):
        raise AShareDataError("snapshot manifest 状态不允许复用")
    snapshot_root = path.parent.resolve()
    if _resolved(str(manifest.get("snapshot_path", ""))) != snapshot_root:
        raise AShareDataError("snapshot_path 与 manifest 所在目录不一致")
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise AShareDataError("snapshot manifest.files 为空")
    expected_files = {"source_manifest.json"}
    for entry in entries:
        relative = entry.get("destination_relative")
        if not isinstance(relative, str) or not relative:
            raise AShareDataError("snapshot destination_relative 无效")
        target = guard_output_path(
            snapshot_root / Path(relative),
            training_root=training_root,
            project_root=project_root,
        )
        expected_files.add(target.relative_to(snapshot_root).as_posix())
        if not target.is_file():
            raise AShareDataError(f"snapshot 文件缺失: {relative}")
        if target.stat().st_size != int(entry.get("size", -1)):
            raise AShareDataError(f"snapshot 文件大小漂移: {relative}")
        expected_hash = entry.get("destination_sha256") or entry.get("sha256")
        if not isinstance(expected_hash, str) or _sha256_file(target) != expected_hash:
            raise AShareDataError(f"snapshot SHA256 漂移: {relative}")
    actual_files = {
        item.relative_to(snapshot_root).as_posix()
        for item in snapshot_root.rglob("*")
        if item.is_file()
    }
    if actual_files != expected_files:
        raise AShareDataError(
            f"snapshot 文件集合漂移: extra={sorted(actual_files - expected_files)}, "
            f"missing={sorted(expected_files - actual_files)}"
        )
    return manifest


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    if suffix in {".parquet", ".pq"}:
        try:
            return pd.read_parquet(path)
        except ImportError as exc:
            raise PitContractError(
                f"读取 {path.name} 需要 pyarrow 或 fastparquet"
            ) from exc
    raise PitContractError(f"仅支持 CSV/Parquet PIT 文件: {path}")


def _coerce_bool(value: Any, *, column: str) -> bool:
    normalized = value.strip().lower() if isinstance(value, str) else value
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise PitContractError(f"{column} 包含非法布尔值: {value!r}")


def _validate_tickers(frame: pd.DataFrame, column: str = "ticker") -> None:
    bad = frame[column].astype(str).map(lambda value: _TICKER_RE.fullmatch(value) is None)
    if bad.any():
        sample = frame.loc[bad, column].astype(str).head(3).tolist()
        raise PitContractError(f"{column} 必须使用 000001.SZ 格式，非法样例: {sample}")


def _validate_intervals(frame: pd.DataFrame, spec: PitTableSpec, *, table_name: str) -> None:
    if spec.interval is None:
        return
    start_column, end_column = spec.interval
    invalid = frame[end_column].notna() & (frame[end_column] < frame[start_column])
    if invalid.any():
        raise PitContractError(f"{table_name}: 存在结束日期早于开始日期的区间")

    keys: str | list[str]
    keys = spec.interval_keys[0] if len(spec.interval_keys) == 1 else list(spec.interval_keys)
    grouped = frame.sort_values([*spec.interval_keys, start_column]).groupby(keys, dropna=False)
    for group_key, group in grouped:
        previous_end: pd.Timestamp | None = None
        for row in group.itertuples(index=False):
            current_start = getattr(row, start_column)
            current_end = getattr(row, end_column)
            if previous_end is not None and current_start <= previous_end:
                raise PitContractError(f"{table_name}: {group_key!r} 存在重叠区间")
            previous_end = pd.Timestamp.max.normalize() if pd.isna(current_end) else current_end


def validate_pit_table(table_name: str, source: pd.DataFrame | str | os.PathLike[str]) -> pd.DataFrame:
    if table_name not in PIT_TABLE_SPECS:
        raise PitContractError(f"未知 PIT 表: {table_name}")
    spec = PIT_TABLE_SPECS[table_name]
    frame = source.copy() if isinstance(source, pd.DataFrame) else _read_table(Path(source))
    frame.columns = [str(column).strip() for column in frame.columns]
    missing = [column for column in spec.required_columns if column not in frame.columns]
    if missing:
        raise PitContractError(f"{table_name}: 缺少字段 {missing}")
    if frame.empty:
        raise PitContractError(f"{table_name}: 表为空")
    selected_columns = [
        *spec.required_columns,
        *(column for column in spec.optional_columns if column in frame.columns),
    ]
    frame = frame.loc[:, list(dict.fromkeys(selected_columns))].copy()

    for column in spec.required_dates:
        parsed = pd.to_datetime(frame[column], errors="coerce").dt.normalize()
        if parsed.isna().any():
            raise PitContractError(f"{table_name}.{column}: 存在空值或非法日期")
        frame[column] = parsed
    for column in spec.nullable_dates:
        if column not in frame.columns:
            continue
        raw = frame[column]
        parsed = pd.to_datetime(raw, errors="coerce").dt.normalize()
        invalid = raw.notna() & raw.astype(str).str.strip().ne("") & parsed.isna()
        if invalid.any():
            raise PitContractError(f"{table_name}.{column}: 存在非法日期")
        frame[column] = parsed

    if "ticker" in frame.columns:
        _validate_tickers(frame)

    if table_name == "security_master":
        allowed_exchange = {"SH", "SZ", "BJ"}
        allowed_board = {"main", "chinext", "star", "bse"}
        if not set(frame["exchange"].astype(str)).issubset(allowed_exchange):
            raise PitContractError("security_master.exchange 仅允许 SH/SZ/BJ")
        if not set(frame["board"].astype(str)).issubset(allowed_board):
            raise PitContractError("security_master.board 仅允许 main/chinext/star/bse")
        suffix = frame["ticker"].astype(str).str[-2:]
        if not suffix.eq(frame["exchange"].astype(str)).all():
            raise PitContractError("security_master 的 ticker 后缀与 exchange 不一致")
    elif table_name in {"st_status", "suspensions", TRADING_CALENDAR_TABLE}:
        bool_column = {
            "st_status": "is_st",
            "suspensions": "is_suspended",
            TRADING_CALENDAR_TABLE: "is_open",
        }[table_name]
        frame[bool_column] = frame[bool_column].map(
            lambda value: _coerce_bool(value, column=f"{table_name}.{bool_column}")
        )
        if table_name == TRADING_CALENDAR_TABLE and "benchmark_ticker" in frame.columns:
            benchmark = frame["benchmark_ticker"].fillna("").astype(str).str.strip()
            invalid = ~benchmark.isin({"", "000300.SH", "000905.SH", "000906.SH"})
            if invalid.any():
                raise PitContractError(
                    "trading_calendar.benchmark_ticker 仅允许 CSI300/500/800"
                )
            frame["benchmark_ticker"] = benchmark
    elif table_name == "price_limits":
        up = pd.to_numeric(frame["up_limit"], errors="coerce")
        down = pd.to_numeric(frame["down_limit"], errors="coerce")
        one_missing = up.isna() ^ down.isna()
        if one_missing.any():
            raise PitContractError("price_limits: up_limit/down_limit 必须同时为空或同时存在")
        limited = up.notna()
        if ((up[limited] <= 0) | (down[limited] <= 0) | (up[limited] < down[limited])).any():
            raise PitContractError("price_limits: 涨跌停价非法")
        frame["up_limit"], frame["down_limit"] = up, down
        if "rule_version" in frame.columns:
            empty_rule = frame["rule_version"].isna() | frame["rule_version"].astype(str).str.strip().eq("")
            if empty_rule.any():
                raise PitContractError("price_limits.rule_version 不得为空")
        if "no_limit_reason" in frame.columns:
            reason = frame["no_limit_reason"].fillna("").astype(str).str.strip()
            if (limited & reason.ne("")).any():
                raise PitContractError("price_limits: 有涨跌停价时 no_limit_reason 必须为空")
            if ((~limited) & reason.eq("")).any():
                raise PitContractError("price_limits: 无涨跌停价时必须说明 no_limit_reason")
            frame["no_limit_reason"] = reason
        previous_fields = {"previous_trade_date", "previous_close_raw"}
        present_previous_fields = previous_fields.intersection(frame.columns)
        if present_previous_fields and present_previous_fields != previous_fields:
            raise PitContractError(
                "price_limits: previous_trade_date/previous_close_raw 必须同时存在"
            )
        if present_previous_fields:
            previous_close = pd.to_numeric(frame["previous_close_raw"], errors="coerce")
            if previous_close.isna().any() or (previous_close <= 0).any():
                raise PitContractError("price_limits.previous_close_raw 必须为正数")
            if (frame["previous_trade_date"] >= frame["trade_date"]).any():
                raise PitContractError(
                    "price_limits.previous_trade_date 必须早于 trade_date"
                )
            frame["previous_close_raw"] = previous_close
    elif table_name == "corporate_actions":
        for column in ("cash_div", "bonus_ratio", "rights_ratio", "rights_price"):
            values = pd.to_numeric(frame[column], errors="coerce")
            if values.isna().any() or (values < 0).any():
                raise PitContractError(f"corporate_actions.{column}: 必须为非负数")
            frame[column] = values
        if (frame["announcement_date"] > frame["ex_date"]).any():
            raise PitContractError("corporate_actions: announcement_date 晚于 ex_date")
    elif table_name == "index_membership":
        invalid_codes = ~frame["index_code"].astype(str).str.fullmatch(r"\d{6}\.SH")
        if invalid_codes.any():
            raise PitContractError("index_membership.index_code 必须使用 000300.SH 格式")
    elif table_name == "coverage":
        frame["is_complete"] = frame["is_complete"].map(
            lambda value: _coerce_bool(value, column="coverage.is_complete")
        )
        allowed = set(PIT_TABLE_SPECS) - {"coverage"}
        if not set(frame["dataset"].astype(str)).issubset(allowed):
            raise PitContractError("coverage.dataset 包含未知数据集")
        if frame["dataset"].duplicated().any():
            raise PitContractError("coverage.dataset 不得重复")
        if (frame["coverage_end"] < frame["coverage_start"]).any():
            raise PitContractError("coverage: coverage_end 早于 coverage_start")
        present_bindings = [column for column in COVERAGE_BINDING_COLUMNS if column in frame.columns]
        if present_bindings and len(present_bindings) != len(COVERAGE_BINDING_COLUMNS):
            missing_bindings = sorted(set(COVERAGE_BINDING_COLUMNS) - set(present_bindings))
            raise PitContractError(f"coverage: provenance 绑定字段不完整 {missing_bindings}")
        if present_bindings:
            complete = frame["is_complete"]
            for column in COVERAGE_BINDING_COLUMNS:
                missing_value = frame[column].isna() | frame[column].astype(str).str.strip().eq("")
                if (complete & missing_value).any():
                    raise PitContractError(f"coverage.{column}: complete 行不得为空")
            bound = frame[complete]
            if not bound.empty:
                if not bound["binding_schema"].astype(str).eq(PIT_COVERAGE_BINDING_SCHEMA).all():
                    raise PitContractError(
                        f"coverage.binding_schema 必须为 {PIT_COVERAGE_BINDING_SCHEMA}"
                    )
                for column in ("file_sha256", "schema_sha256", "source_manifest_sha256"):
                    valid_hash = bound[column].astype(str).str.fullmatch(r"[0-9a-f]{64}")
                    if not valid_hash.all():
                        raise PitContractError(f"coverage.{column}: 必须为小写 SHA256")
                for column in ("row_count", "file_bytes"):
                    numeric = pd.to_numeric(bound[column], errors="coerce")
                    if numeric.isna().any() or (numeric < 1).any() or (numeric % 1 != 0).any():
                        raise PitContractError(f"coverage.{column}: 必须为正整数")
                    frame.loc[complete, column] = numeric.astype("int64")

    duplicate_keys: list[str] = []
    if table_name == "suspensions":
        duplicate_keys = ["ticker", "trade_date"]
    elif table_name == "price_limits":
        duplicate_keys = ["ticker", "trade_date"]
    elif table_name == TRADING_CALENDAR_TABLE:
        duplicate_keys = ["trade_date"]
    elif table_name == "corporate_actions":
        duplicate_keys = ["ticker", "announcement_date", "ex_date"]
    elif table_name == "coverage":
        duplicate_keys = ["dataset"]
    if duplicate_keys and frame.duplicated(duplicate_keys).any():
        raise PitContractError(f"{table_name}: 主键重复 {duplicate_keys}")

    _validate_intervals(frame, spec, table_name=table_name)
    sort_candidates = (
        "ticker",
        "index_code",
        "trade_date",
        "effective_from",
        "list_date",
        "ex_date",
    )
    return frame.sort_values(
        [column for column in sort_candidates if column in frame.columns]
    ).reset_index(drop=True)


def _find_pit_file(root: Path, table_name: str) -> Path | None:
    matches = [path for suffix in (".parquet", ".pq", ".csv") if (path := root / f"{table_name}{suffix}").is_file()]
    if len(matches) > 1:
        raise PitContractError(f"{table_name}: 同时存在多个 CSV/Parquet 文件")
    return matches[0] if matches else None


def _coverage_complete(
    coverage: pd.DataFrame | None,
    dataset: str,
    *,
    start: date,
    end: date,
) -> bool:
    if coverage is None:
        return False
    rows = coverage[coverage["dataset"].astype(str) == dataset]
    if len(rows) != 1:
        return False
    row = rows.iloc[0]
    return bool(row["is_complete"]) and row["coverage_start"].date() <= start and row["coverage_end"].date() >= end


def pit_table_schema_sha256(table_name: str, frame: pd.DataFrame) -> str:
    """Return a stable fingerprint for the consumed PIT table schema."""

    if table_name not in PIT_TABLE_SPECS:
        raise PitContractError(f"未知 PIT 表: {table_name}")
    spec = PIT_TABLE_SPECS[table_name]
    date_columns = set(spec.required_dates) | set(spec.nullable_dates)
    boolean_columns = {"is_st", "is_suspended", "is_complete"}
    numeric_columns = {
        "up_limit",
        "down_limit",
        "previous_close_raw",
        "cash_div",
        "bonus_ratio",
        "rights_ratio",
        "rights_price",
        "row_count",
        "file_bytes",
    }
    columns: list[dict[str, str]] = []
    for column in frame.columns:
        if column in date_columns:
            logical_type = "date"
        elif column in boolean_columns:
            logical_type = "boolean"
        elif column in numeric_columns:
            logical_type = "number"
        else:
            logical_type = "string"
        columns.append({"name": str(column), "logical_type": logical_type})
    descriptor = {
        "schema_version": "kronos-a-share-pit-table-schema-v1",
        "table": table_name,
        "columns": columns,
        "required_columns": list(spec.required_columns),
        "interval": list(spec.interval) if spec.interval else None,
        "interval_keys": list(spec.interval_keys),
    }
    payload = json.dumps(
        descriptor,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_bytes(payload)


def _parse_manifest_date(value: Any, *, field: str) -> date:
    try:
        parsed = date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise PitContractError(f"provenance {field} 不是 YYYY-MM-DD") from exc
    return parsed


def _resolve_pit_artifact(root: Path, reference: Any, *, field: str) -> Path:
    if not isinstance(reference, str) or not reference.strip():
        raise PitContractError(f"provenance {field} 不能为空")
    relative = Path(reference)
    if relative.is_absolute() or ".." in relative.parts:
        raise PitContractError(f"provenance {field} 必须是 PIT 根内相对路径")
    candidate = (root / relative).resolve(strict=True)
    if candidate == root or root not in candidate.parents or not candidate.is_file():
        raise PitContractError(f"provenance {field} 越界或不是文件")
    return candidate


def _date_intervals_cover(
    intervals: Sequence[tuple[date, date]],
    *,
    start: date,
    end: date,
) -> bool:
    if not intervals:
        return False
    cursor = start
    for interval_start, interval_end in sorted(intervals):
        if interval_end < cursor:
            continue
        if interval_start > cursor:
            return False
        cursor = max(cursor, interval_end + timedelta(days=1))
        if cursor > end:
            return True
    return cursor > end


def _verify_source_provenance(
    root: Path,
    *,
    dataset: str,
    table_path: Path,
    manifest_reference: Any,
    expected_manifest_sha256: str,
    start: date,
    end: date,
) -> dict[str, Any]:
    manifest_path = _resolve_pit_artifact(
        root, manifest_reference, field=f"{dataset}.source_manifest"
    )
    if manifest_path in {table_path.resolve(), (root / "coverage.csv").resolve(strict=False)}:
        raise PitContractError(f"{dataset}: source manifest 不得指向派生表")
    actual_manifest_sha256 = _sha256_file(manifest_path)
    if actual_manifest_sha256 != expected_manifest_sha256:
        raise PitContractError(f"{dataset}: source manifest SHA256 不匹配")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PitContractError(f"{dataset}: source manifest 无法解析") from exc
    if not isinstance(manifest, Mapping):
        raise PitContractError(f"{dataset}: source manifest 必须是 JSON object")
    if manifest.get("schema_version") != PIT_PROVENANCE_SCHEMA:
        raise PitContractError(
            f"{dataset}: provenance schema_version 必须为 {PIT_PROVENANCE_SCHEMA}"
        )
    if manifest.get("dataset") != dataset:
        raise PitContractError(f"{dataset}: provenance dataset 绑定不匹配")
    manifest_start = _parse_manifest_date(
        manifest.get("coverage_start"), field=f"{dataset}.coverage_start"
    )
    manifest_end = _parse_manifest_date(
        manifest.get("coverage_end"), field=f"{dataset}.coverage_end"
    )
    if manifest_start > start or manifest_end < end:
        raise PitContractError(f"{dataset}: provenance 有效期覆盖不足")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise PitContractError(f"{dataset}: provenance sources 必须为非空数组")

    intervals: list[tuple[date, date]] = []
    source_reports: list[dict[str, Any]] = []
    for index, source in enumerate(sources):
        label = f"{dataset}.sources[{index}]"
        if not isinstance(source, Mapping):
            raise PitContractError(f"{label} 必须是 object")
        source_id = str(source.get("source_id", "")).strip()
        if not source_id:
            raise PitContractError(f"{label}.source_id 不能为空")
        source_class = source.get("source_class")
        if source_class not in {"official_primary", "public_secondary"}:
            raise PitContractError(f"{label}.source_class 不属于允许证据等级")
        url = str(source.get("url", "")).strip()
        if not re.fullmatch(r"https://[^\s]+", url, flags=re.IGNORECASE):
            raise PitContractError(f"{label}.url 必须为 HTTPS")
        try:
            retrieved_at = datetime.fromisoformat(
                str(source.get("retrieved_at", "")).replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise PitContractError(f"{label}.retrieved_at 不是 ISO-8601") from exc
        if retrieved_at.tzinfo is None:
            raise PitContractError(f"{label}.retrieved_at 必须包含时区")
        valid_from = _parse_manifest_date(
            source.get("valid_from"), field=f"{label}.valid_from"
        )
        valid_to = _parse_manifest_date(
            source.get("valid_to"), field=f"{label}.valid_to"
        )
        if valid_to < valid_from:
            raise PitContractError(f"{label}: valid_to 早于 valid_from")
        raw_path = _resolve_pit_artifact(root, source.get("path"), field=f"{label}.path")
        if raw_path in {table_path.resolve(), manifest_path}:
            raise PitContractError(f"{label}.path 必须指向独立原始响应")
        expected_hash = str(source.get("sha256", ""))
        if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            raise PitContractError(f"{label}.sha256 必须为小写 SHA256")
        if _sha256_file(raw_path) != expected_hash:
            raise PitContractError(f"{label}: 原始响应 SHA256 不匹配")
        if source.get("bytes") is not None and int(source["bytes"]) != raw_path.stat().st_size:
            raise PitContractError(f"{label}: 原始响应字节数不匹配")
        intervals.append((valid_from, valid_to))
        source_reports.append(
            {
                "source_id": source_id,
                "source_class": source_class,
                "url": url,
                "valid_from": valid_from.isoformat(),
                "valid_to": valid_to.isoformat(),
                "path": str(raw_path),
                "sha256": expected_hash,
            }
        )
    if not _date_intervals_cover(intervals, start=start, end=end):
        raise PitContractError(f"{dataset}: 原始响应有效期存在缺口")
    return {
        "verified": True,
        "manifest_path": str(manifest_path),
        "manifest_sha256": actual_manifest_sha256,
        "source_count": len(source_reports),
        "sources": source_reports,
    }


def _verify_coverage_binding(
    root: Path,
    *,
    dataset: str,
    table_path: Path,
    frame: pd.DataFrame,
    coverage: pd.DataFrame | None,
    start: date,
    end: date,
) -> tuple[bool, dict[str, Any]]:
    if coverage is None:
        return False, {"verified": False, "reason": "missing_coverage"}
    rows = coverage[coverage["dataset"].astype(str) == dataset]
    if len(rows) != 1:
        return False, {"verified": False, "reason": "missing_coverage_row"}
    row = rows.iloc[0]
    if not bool(row["is_complete"]):
        return False, {"verified": False, "reason": "coverage_not_complete"}
    if row["coverage_start"].date() > start or row["coverage_end"].date() < end:
        return False, {"verified": False, "reason": "declared_period_insufficient"}
    if not set(COVERAGE_BINDING_COLUMNS).issubset(coverage.columns):
        return False, {"verified": False, "reason": "missing_cryptographic_binding"}

    actual_file_sha256 = _sha256_file(table_path)
    actual_schema_sha256 = pit_table_schema_sha256(dataset, frame)
    checks = {
        "file_sha256": (str(row["file_sha256"]), actual_file_sha256),
        "schema_sha256": (str(row["schema_sha256"]), actual_schema_sha256),
        "row_count": (int(row["row_count"]), len(frame)),
        "file_bytes": (int(row["file_bytes"]), table_path.stat().st_size),
    }
    for field, (declared, actual) in checks.items():
        if declared != actual:
            raise PitContractError(
                f"{dataset}: coverage.{field} 绑定不匹配 declared={declared!r} actual={actual!r}"
            )
    provenance = _verify_source_provenance(
        root,
        dataset=dataset,
        table_path=table_path,
        manifest_reference=row["source_manifest"],
        expected_manifest_sha256=str(row["source_manifest_sha256"]),
        start=start,
        end=end,
    )
    return True, {
        "verified": True,
        "binding_schema": PIT_COVERAGE_BINDING_SCHEMA,
        "file_sha256": actual_file_sha256,
        "schema_sha256": actual_schema_sha256,
        "row_count": len(frame),
        "file_bytes": table_path.stat().st_size,
        "coverage_start": row["coverage_start"].date().isoformat(),
        "coverage_end": row["coverage_end"].date().isoformat(),
        "provenance": provenance,
    }


def _membership_covers(
    frame: pd.DataFrame | None,
    index_code: str,
    *,
    start: date,
    end: date,
    expected_constituents: int,
) -> bool:
    if frame is None:
        return False
    subset = frame[frame["index_code"].astype(str) == index_code]
    if subset.empty:
        return False
    intervals = [
        (
            str(row.ticker),
            max(row.effective_from.date(), start),
            min(row.effective_to.date(), end) if pd.notna(row.effective_to) else end,
        )
        for row in subset.itertuples(index=False)
        if row.effective_from.date() <= end
        and (pd.isna(row.effective_to) or row.effective_to.date() >= start)
    ]
    if not intervals or expected_constituents < 1:
        return False
    boundaries = {start, end}
    for _, interval_start, interval_end in intervals:
        boundaries.add(interval_start)
        if interval_end < end:
            boundaries.add(interval_end + timedelta(days=1))
    for point in sorted(boundaries):
        active = {
            ticker
            for ticker, interval_start, interval_end in intervals
            if interval_start <= point <= interval_end
        }
        if len(active) != expected_constituents:
            return False
    return True


def _membership_matches_security_master(
    membership: pd.DataFrame | None,
    security_master: pd.DataFrame | None,
    index_code: str,
) -> bool:
    if membership is None or security_master is None:
        return False
    master = security_master.set_index("ticker", drop=False)
    for row in membership[membership["index_code"].astype(str) == index_code].itertuples(
        index=False
    ):
        if row.ticker not in master.index:
            return False
        security = master.loc[row.ticker]
        if isinstance(security, pd.DataFrame):
            candidates = security
        else:
            candidates = security.to_frame().T
        effective_to = row.effective_to if pd.notna(row.effective_to) else pd.Timestamp.max
        valid = False
        for item in candidates.itertuples(index=False):
            delist_date = item.delist_date if pd.notna(item.delist_date) else pd.Timestamp.max
            if (
                str(item.security_type) == "A_STOCK"
                and item.list_date <= row.effective_from
                and effective_to <= delist_date
            ):
                valid = True
                break
        if not valid:
            return False
    return True


def _status_intervals_cover_membership(
    status: pd.DataFrame | None,
    membership: pd.DataFrame | None,
    *,
    start: date,
    end: date,
) -> bool:
    if status is None or membership is None:
        return False
    status_by_ticker: dict[str, list[tuple[date, date]]] = {}
    for row in status.itertuples(index=False):
        interval_start = max(row.effective_from.date(), start)
        interval_end = min(row.effective_to.date(), end) if pd.notna(row.effective_to) else end
        if interval_start <= interval_end:
            status_by_ticker.setdefault(str(row.ticker), []).append(
                (interval_start, interval_end)
            )
    required = membership[membership["index_code"].astype(str).isin(REQUIRED_INDEX_CODES)]
    for row in required.itertuples(index=False):
        interval_start = max(row.effective_from.date(), start)
        interval_end = min(row.effective_to.date(), end) if pd.notna(row.effective_to) else end
        if interval_start > interval_end:
            continue
        clipped = [
            (max(left, interval_start), min(right, interval_end))
            for left, right in status_by_ticker.get(str(row.ticker), [])
            if right >= interval_start and left <= interval_end
        ]
        if not _date_intervals_cover(clipped, start=interval_start, end=interval_end):
            return False
    return True


def _active_membership_events(
    membership: pd.DataFrame,
    *,
    start: date,
    end: date,
) -> dict[date, list[tuple[str, int]]]:
    events: dict[date, list[tuple[str, int]]] = {}
    required = membership[membership["index_code"].astype(str).isin(REQUIRED_INDEX_CODES)]
    for row in required.itertuples(index=False):
        interval_start = max(row.effective_from.date(), start)
        interval_end = min(row.effective_to.date(), end) if pd.notna(row.effective_to) else end
        if interval_start > interval_end:
            continue
        ticker = str(row.ticker)
        events.setdefault(interval_start, []).append((ticker, 1))
        if interval_end < end:
            events.setdefault(interval_end + timedelta(days=1), []).append((ticker, -1))
    return events


def _audit_daily_trade_state_coverage(
    frames: Mapping[str, pd.DataFrame],
    *,
    start: date,
    end: date,
) -> dict[str, Any]:
    membership = frames.get("index_membership")
    suspensions = frames.get("suspensions")
    price_limits = frames.get("price_limits")
    st_status = frames.get("st_status")
    security_master = frames.get("security_master")
    trading_calendar = frames.get(TRADING_CALENDAR_TABLE)
    issues: list[str] = []
    if any(
        frame is None
        for frame in (
            membership,
            suspensions,
            price_limits,
            st_status,
            security_master,
            trading_calendar,
        )
    ):
        return {
            "verified": False,
            "issues": ["missing_required_trade_state_or_calendar_table"],
            "trade_date_period_verified": False,
            "calendar_primary_key_verified": False,
            "st_coverage_verified": False,
            "price_rule_schema_verified": False,
            "trade_date_count": 0,
            "checked_member_dates": 0,
            "price_limit_recalculation_checked": 0,
            "price_limit_recalculation_mismatches": 0,
            "missing_previous_close_member_dates": 0,
        }
    assert membership is not None
    assert suspensions is not None
    assert price_limits is not None
    assert st_status is not None
    assert security_master is not None
    assert trading_calendar is not None
    price_rule_schema_verified = {"rule_version", "no_limit_reason"}.issubset(
        price_limits.columns
    )
    if not price_rule_schema_verified:
        issues.append("price_limit_rule_columns_missing")
    previous_close_schema_verified = {
        "previous_trade_date",
        "previous_close_raw",
    }.issubset(price_limits.columns)
    if not previous_close_schema_verified:
        issues.append("price_limit_previous_close_columns_missing")

    calendar_primary_key_verified = not trading_calendar["trade_date"].duplicated().any()
    if not calendar_primary_key_verified:
        issues.append("trading_calendar_primary_key_invalid")
    all_open_dates = sorted(
        row.trade_date.date()
        for row in trading_calendar.itertuples(index=False)
        if bool(row.is_open)
    )
    dates = [value for value in all_open_dates if start <= value <= end]
    trade_date_period_verified = bool(dates) and dates[0] <= start and dates[-1] >= end
    if not trade_date_period_verified:
        issues.append("trading_calendar_dates_do_not_cover_period")
    st_coverage_verified = _status_intervals_cover_membership(
        st_status, membership, start=start, end=end
    )
    if not st_coverage_verified:
        issues.append("st_intervals_do_not_cover_membership")

    suspension_keys = set(
        zip(
            suspensions["ticker"].astype(str),
            suspensions["trade_date"].dt.date,
        )
    )
    limit_keys = set(
        zip(
            price_limits["ticker"].astype(str),
            price_limits["trade_date"].dt.date,
        )
    )
    open_date_set = set(all_open_dates)
    state_dates = {
        value.date()
        for frame in (suspensions, price_limits)
        for value in frame["trade_date"]
        if start <= value.date() <= end
    }
    state_dates_not_in_calendar = len(state_dates - open_date_set)
    if state_dates_not_in_calendar:
        issues.append(
            f"trade_state_dates_not_in_calendar:{state_dates_not_in_calendar}"
        )

    previous_open_date = {
        current: all_open_dates[index - 1]
        for index, current in enumerate(all_open_dates)
        if index > 0
    }
    limit_rows = {
        (str(row.ticker), row.trade_date.date()): row
        for row in price_limits.itertuples(index=False)
    }
    master_by_ticker: dict[str, list[Any]] = {}
    for row in security_master.itertuples(index=False):
        master_by_ticker.setdefault(str(row.ticker), []).append(row)
    st_by_ticker: dict[str, list[Any]] = {}
    for row in st_status.itertuples(index=False):
        st_by_ticker.setdefault(str(row.ticker), []).append(row)

    def active_interval_row(
        rows: Sequence[Any],
        current: date,
        start_field: str,
        end_field: str,
    ) -> Any | None:
        active = []
        current_timestamp = pd.Timestamp(current)
        for row in rows:
            interval_start = getattr(row, start_field)
            interval_end = getattr(row, end_field)
            if interval_start <= current_timestamp and (
                pd.isna(interval_end) or interval_end >= current_timestamp
            ):
                active.append(row)
        return active[0] if len(active) == 1 else None

    def decimal_or_none(value: Any) -> Decimal | None:
        if pd.isna(value):
            return None
        return _decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    events = _active_membership_events(membership, start=start, end=end)
    event_dates = sorted(events)
    event_index = 0
    active_counts: dict[str, int] = {}
    missing_suspension = 0
    missing_limit = 0
    missing_previous_close = 0
    recalculation_checked = 0
    recalculation_mismatches = 0
    mismatch_examples: list[str] = []
    checked_member_dates = 0
    for trade_date in dates:
        while event_index < len(event_dates) and event_dates[event_index] <= trade_date:
            for ticker, delta in events[event_dates[event_index]]:
                next_count = active_counts.get(ticker, 0) + delta
                if next_count <= 0:
                    active_counts.pop(ticker, None)
                else:
                    active_counts[ticker] = next_count
            event_index += 1
        active = tuple(active_counts)
        checked_member_dates += len(active)
        missing_suspension += sum(
            (ticker, trade_date) not in suspension_keys for ticker in active
        )
        missing_limit += sum((ticker, trade_date) not in limit_keys for ticker in active)
        if not price_rule_schema_verified or not previous_close_schema_verified:
            continue
        for ticker in active:
            limit_row = limit_rows.get((ticker, trade_date))
            if limit_row is None:
                continue
            expected_previous_date = previous_open_date.get(trade_date)
            stored_previous_date = getattr(limit_row, "previous_trade_date", pd.NaT)
            stored_previous_close = getattr(limit_row, "previous_close_raw", None)
            if (
                expected_previous_date is None
                or pd.isna(stored_previous_date)
                or stored_previous_close is None
                or pd.isna(stored_previous_close)
            ):
                missing_previous_close += 1
                continue
            if stored_previous_date.date() != expected_previous_date:
                recalculation_mismatches += 1
                if len(mismatch_examples) < 5:
                    mismatch_examples.append(
                        f"{ticker}@{trade_date}:previous_trade_date"
                    )
                continue

            security = active_interval_row(
                master_by_ticker.get(ticker, ()),
                trade_date,
                "list_date",
                "delist_date",
            )
            st_row = active_interval_row(
                st_by_ticker.get(ticker, ()),
                trade_date,
                "effective_from",
                "effective_to",
            )
            if security is None or st_row is None:
                recalculation_mismatches += 1
                if len(mismatch_examples) < 5:
                    mismatch_examples.append(f"{ticker}@{trade_date}:state")
                continue

            reason = str(getattr(limit_row, "no_limit_reason", "") or "").strip() or None
            trading_day_number: int | None = None
            explicit_reason = reason
            if reason == "ipo_initial_trading_days":
                listing_date = security.list_date.date()
                if listing_date not in open_date_set:
                    missing_previous_close += 1
                    continue
                trading_day_number = sum(
                    listing_date <= value <= trade_date for value in all_open_dates
                )
                explicit_reason = None
            try:
                recalculated = calculate_price_limits(
                    stored_previous_close,
                    trade_date,
                    exchange=str(security.exchange),
                    board=str(security.board),
                    is_st=bool(st_row.is_st),
                    listing_date=security.list_date.date(),
                    trading_day_number=trading_day_number,
                    no_limit_reason=explicit_reason,
                )
                actual_up = decimal_or_none(limit_row.up_limit)
                actual_down = decimal_or_none(limit_row.down_limit)
            except (ArithmeticError, TypeError, ValueError):
                recalculation_mismatches += 1
                if len(mismatch_examples) < 5:
                    mismatch_examples.append(f"{ticker}@{trade_date}:calculation")
                continue
            recalculation_checked += 1
            actual_rule = str(getattr(limit_row, "rule_version", "")).strip()
            actual_reason = reason
            if (
                actual_up != recalculated.up_limit
                or actual_down != recalculated.down_limit
                or actual_rule != recalculated.rule_version
                or actual_reason != recalculated.no_limit_reason
            ):
                recalculation_mismatches += 1
                if len(mismatch_examples) < 5:
                    mismatch_examples.append(f"{ticker}@{trade_date}:limit_or_rule")
    if missing_suspension:
        issues.append(f"missing_suspension_member_dates:{missing_suspension}")
    if missing_limit:
        issues.append(f"missing_price_limit_member_dates:{missing_limit}")
    if missing_previous_close:
        issues.append(
            f"missing_previous_close_member_dates:{missing_previous_close}"
        )
    if recalculation_mismatches:
        issues.append(
            f"price_limit_recalculation_mismatches:{recalculation_mismatches}"
        )
    return {
        "verified": not issues,
        "issues": issues,
        "trade_date_period_verified": trade_date_period_verified,
        "calendar_primary_key_verified": calendar_primary_key_verified,
        "st_coverage_verified": st_coverage_verified,
        "price_rule_schema_verified": price_rule_schema_verified,
        "previous_close_schema_verified": previous_close_schema_verified,
        "trade_date_count": len(dates),
        "checked_member_dates": checked_member_dates,
        "missing_suspension_member_dates": missing_suspension,
        "missing_price_limit_member_dates": missing_limit,
        "missing_previous_close_member_dates": missing_previous_close,
        "price_limit_recalculation_checked": recalculation_checked,
        "price_limit_recalculation_mismatches": recalculation_mismatches,
        "price_limit_recalculation_mismatch_examples": mismatch_examples,
        "trade_state_dates_not_in_calendar": state_dates_not_in_calendar,
    }


def _corporate_actions_match_security_master(
    actions: pd.DataFrame | None,
    security_master: pd.DataFrame | None,
) -> bool:
    if actions is None or security_master is None:
        return False
    known = set(security_master["ticker"].astype(str))
    return set(actions["ticker"].astype(str)).issubset(known)


def assess_sample_trade_state(
    validation: PitBundleValidation,
    ticker: str,
    signal_date: date | str | pd.Timestamp,
    *,
    trade_price_raw: Decimal | int | float | str | None,
    previous_close_raw: Decimal | int | float | str | None = None,
    minimum_listing_days: int = MINIMUM_LISTING_DAYS,
) -> dict[str, Any]:
    """Fail closed unless one sample's PIT trading state is fully evidenced."""

    ticker = str(ticker).upper()
    if _TICKER_RE.fullmatch(ticker) is None:
        raise PitContractError("sample ticker 必须使用 000001.SZ 格式")
    try:
        as_of = pd.Timestamp(signal_date).normalize()
    except (TypeError, ValueError) as exc:
        raise PitContractError("sample signal_date 无效") from exc
    if minimum_listing_days != MINIMUM_LISTING_DAYS:
        raise PitContractError(f"minimum_listing_days 固定为 {MINIMUM_LISTING_DAYS}")

    flags: list[str] = []
    if validation.errors:
        flags.append("pit_bundle_contract_error")
    required_tables = (
        "security_master",
        "st_status",
        "suspensions",
        "price_limits",
        "index_membership",
        TRADING_CALENDAR_TABLE,
    )
    for table_name in required_tables:
        binding = validation.table_reports.get(table_name, {}).get("coverage_binding", {})
        if binding.get("verified") is not True:
            flags.append(f"unverified_provenance:{table_name}")

    membership = validation.frames.get("index_membership")
    member = pd.DataFrame()
    if membership is not None:
        member = membership[
            membership["index_code"].astype(str).isin(REQUIRED_INDEX_CODES)
            & membership["ticker"].astype(str).eq(ticker)
            & (membership["effective_from"] <= as_of)
            & (membership["effective_to"].isna() | (membership["effective_to"] >= as_of))
        ]
    if member.empty:
        flags.append("not_in_pit_csi300_or_csi500")

    master = validation.frames.get("security_master")
    security = pd.DataFrame()
    if master is not None:
        security = master[
            master["ticker"].astype(str).eq(ticker)
            & (master["list_date"] <= as_of)
            & (master["delist_date"].isna() | (master["delist_date"] >= as_of))
        ]
    listing_days: int | None = None
    security_row: Any | None = None
    if len(security) != 1:
        flags.append("unconfirmed_listing_state")
    else:
        security_row = security.iloc[0]
        listing_days = int((as_of - security_row["list_date"]).days)
        if listing_days < minimum_listing_days:
            flags.append("listing_age_below_120_days")

    st_frame = validation.frames.get("st_status")
    st_rows = pd.DataFrame()
    if st_frame is not None:
        st_rows = st_frame[
            st_frame["ticker"].astype(str).eq(ticker)
            & (st_frame["effective_from"] <= as_of)
            & (st_frame["effective_to"].isna() | (st_frame["effective_to"] >= as_of))
        ]
    is_st: bool | None = None
    if len(st_rows) != 1:
        flags.append("unconfirmed_st_state")
    else:
        is_st = bool(st_rows.iloc[0]["is_st"])

    suspensions = validation.frames.get("suspensions")
    suspension_rows = pd.DataFrame()
    if suspensions is not None:
        suspension_rows = suspensions[
            suspensions["ticker"].astype(str).eq(ticker)
            & suspensions["trade_date"].eq(as_of)
        ]
    is_suspended: bool | None = None
    if len(suspension_rows) != 1:
        flags.append("unconfirmed_suspension_state")
    else:
        is_suspended = bool(suspension_rows.iloc[0]["is_suspended"])
        if is_suspended:
            flags.append("suspended")

    price_limits = validation.frames.get("price_limits")
    limit_rows = pd.DataFrame()
    if price_limits is not None:
        limit_rows = price_limits[
            price_limits["ticker"].astype(str).eq(ticker)
            & price_limits["trade_date"].eq(as_of)
        ]
    up_limit: Decimal | None = None
    down_limit: Decimal | None = None
    rule_version: str | None = None
    no_limit_reason: str | None = None
    limit_row: Any | None = None
    if len(limit_rows) != 1 or not {"rule_version", "no_limit_reason"}.issubset(limit_rows.columns):
        flags.append("unconfirmed_price_limit_state")
    else:
        limit_row = limit_rows.iloc[0]
        rule_version = str(limit_row["rule_version"])
        no_limit_reason = str(limit_row["no_limit_reason"]).strip() or None
        if pd.notna(limit_row["up_limit"]):
            up_limit = Decimal(str(limit_row["up_limit"])).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            down_limit = Decimal(str(limit_row["down_limit"])).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

    previous_trade_date: date | None = None
    calendar = validation.frames.get(TRADING_CALENDAR_TABLE)
    if calendar is None:
        flags.append("unconfirmed_trading_calendar")
    else:
        earlier_open_dates = sorted(
            row.trade_date.date()
            for row in calendar.itertuples(index=False)
            if bool(row.is_open) and row.trade_date < as_of
        )
        if not earlier_open_dates:
            flags.append("unconfirmed_previous_trade_date")
        else:
            previous_trade_date = earlier_open_dates[-1]

    normalized_previous_close: Decimal | None = None
    if previous_close_raw is None:
        flags.append("unconfirmed_previous_close_raw")
    else:
        try:
            normalized_previous_close = _decimal(previous_close_raw).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (ValueError, ArithmeticError):
            flags.append("invalid_previous_close_raw")
        else:
            if normalized_previous_close <= 0:
                flags.append("invalid_previous_close_raw")

    recalculated_limit: PriceLimitResult | None = None
    if (
        limit_row is not None
        and security_row is not None
        and is_st is not None
        and previous_trade_date is not None
        and normalized_previous_close is not None
        and normalized_previous_close > 0
    ):
        if {"previous_trade_date", "previous_close_raw"}.issubset(limit_rows.columns):
            bound_previous_date = limit_row["previous_trade_date"]
            bound_previous_close = limit_row["previous_close_raw"]
            if (
                pd.isna(bound_previous_date)
                or bound_previous_date.date() != previous_trade_date
                or pd.isna(bound_previous_close)
                or _decimal(bound_previous_close).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                != normalized_previous_close
            ):
                flags.append("previous_close_binding_mismatch")
        else:
            flags.append("unconfirmed_previous_close_binding")

        explicit_reason = no_limit_reason
        trading_day_number: int | None = None
        if no_limit_reason == "ipo_initial_trading_days":
            listing_date = security_row["list_date"].date()
            listing_open_dates = [
                row.trade_date.date()
                for row in calendar.itertuples(index=False)
                if bool(row.is_open)
                and listing_date <= row.trade_date.date() <= as_of.date()
            ]
            if not listing_open_dates or listing_open_dates[0] != listing_date:
                flags.append("unconfirmed_listing_trading_day_number")
            else:
                trading_day_number = len(listing_open_dates)
                explicit_reason = None
        try:
            recalculated_limit = calculate_price_limits(
                normalized_previous_close,
                as_of.date(),
                exchange=str(security_row["exchange"]),
                board=str(security_row["board"]),
                is_st=is_st,
                listing_date=security_row["list_date"].date(),
                trading_day_number=trading_day_number,
                no_limit_reason=explicit_reason,
            )
        except (ArithmeticError, TypeError, ValueError):
            flags.append("invalid_price_limit_recalculation_inputs")
        else:
            if (
                up_limit != recalculated_limit.up_limit
                or down_limit != recalculated_limit.down_limit
                or rule_version != recalculated_limit.rule_version
                or no_limit_reason != recalculated_limit.no_limit_reason
            ):
                flags.append("price_limit_recalculation_mismatch")

    is_at_up_limit: bool | None = None
    is_at_down_limit: bool | None = None
    if trade_price_raw is None:
        flags.append("unconfirmed_raw_price_for_limit_state")
    else:
        try:
            raw_price = _decimal(trade_price_raw).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (ValueError, ArithmeticError):
            flags.append("invalid_raw_price_for_limit_state")
        else:
            if raw_price <= 0:
                flags.append("invalid_raw_price_for_limit_state")
            elif up_limit is None and down_limit is None:
                is_at_up_limit = False
                is_at_down_limit = False
            elif up_limit is not None and down_limit is not None:
                if raw_price > up_limit or raw_price < down_limit:
                    flags.append("raw_price_outside_price_limits")
                is_at_up_limit = raw_price == up_limit
                is_at_down_limit = raw_price == down_limit
            else:
                flags.append("unconfirmed_price_limit_state")

    fail_closed_prefixes = (
        "pit_bundle_",
        "unverified_provenance:",
        "unconfirmed_",
        "invalid_",
        "raw_price_outside_",
        "previous_close_",
        "price_limit_",
        "not_in_",
        "listing_age_",
    )
    confirmed = not any(flag.startswith(fail_closed_prefixes) for flag in flags)
    eligible = confirmed and is_suspended is False
    return {
        "ticker": ticker,
        "signal_date": as_of.date().isoformat(),
        "minimum_listing_days": minimum_listing_days,
        "listing_days": listing_days,
        "is_st": is_st,
        "is_suspended": is_suspended,
        "previous_trade_date": (
            previous_trade_date.isoformat() if previous_trade_date is not None else None
        ),
        "previous_close_raw": (
            str(normalized_previous_close)
            if normalized_previous_close is not None
            else None
        ),
        "up_limit": str(up_limit) if up_limit is not None else None,
        "down_limit": str(down_limit) if down_limit is not None else None,
        "rule_version": rule_version,
        "no_limit_reason": no_limit_reason,
        "recalculated_price_limits": (
            recalculated_limit.to_dict() if recalculated_limit is not None else None
        ),
        "is_at_up_limit": is_at_up_limit,
        "is_at_down_limit": is_at_down_limit,
        "state_confirmed": confirmed,
        "eligible_for_formal_sample": eligible,
        "constraint_flags": list(dict.fromkeys(flags)),
    }


def validate_pit_bundle(
    pit_root: str | os.PathLike[str],
    *,
    coverage_start: date = PIT_START,
    coverage_end: date = PIT_END,
) -> PitBundleValidation:
    root = _resolved(pit_root)
    frames: dict[str, pd.DataFrame] = {}
    reports: dict[str, dict[str, Any]] = {}
    paths: dict[str, Path] = {}
    missing: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []

    for table_name in MANDATORY_PIT_TABLES:
        try:
            path = _find_pit_file(root, table_name)
            if path is None:
                missing.append(table_name)
                continue
            frame = validate_pit_table(table_name, path)
            frames[table_name] = frame
            paths[table_name] = path
            reports[table_name] = {
                "path": str(path),
                "rows": len(frame),
                "sha256": _sha256_file(path),
                "bytes": path.stat().st_size,
                "schema_sha256": pit_table_schema_sha256(table_name, frame),
            }
        except (OSError, ValueError, PitContractError) as exc:
            errors.append(f"{table_name}: {exc}")

    try:
        calendar_path = _find_pit_file(root, TRADING_CALENDAR_TABLE)
        if calendar_path is None:
            missing.append(TRADING_CALENDAR_TABLE)
        else:
            calendar_frame = validate_pit_table(
                TRADING_CALENDAR_TABLE,
                calendar_path,
            )
            frames[TRADING_CALENDAR_TABLE] = calendar_frame
            paths[TRADING_CALENDAR_TABLE] = calendar_path
            reports[TRADING_CALENDAR_TABLE] = {
                "path": str(calendar_path),
                "rows": len(calendar_frame),
                "sha256": _sha256_file(calendar_path),
                "bytes": calendar_path.stat().st_size,
                "schema_sha256": pit_table_schema_sha256(
                    TRADING_CALENDAR_TABLE,
                    calendar_frame,
                ),
                "primary_key": ["trade_date"],
            }
    except (OSError, ValueError, PitContractError) as exc:
        errors.append(f"{TRADING_CALENDAR_TABLE}: {exc}")

    coverage = frames.get("coverage")
    membership = frames.get("index_membership")
    security_master = frames.get("security_master")
    declared_coverage_ok = {
        name: _coverage_complete(coverage, name, start=coverage_start, end=coverage_end)
        for name in PIT_TABLE_SPECS
        if name != "coverage"
    }
    binding_ok: dict[str, bool] = {name: False for name in PIT_PROVENANCE_DATASETS}
    calendar_frame = frames.get(TRADING_CALENDAR_TABLE)
    earlier_calendar_dates = (
        sorted(
            row.trade_date.date()
            for row in calendar_frame.itertuples(index=False)
            if bool(row.is_open) and row.trade_date.date() < coverage_start
        )
        if calendar_frame is not None
        else []
    )
    previous_session_start = (
        earlier_calendar_dates[-1] if earlier_calendar_dates else coverage_start
    )
    for name in PIT_PROVENANCE_DATASETS:
        if name not in frames or name not in paths:
            continue
        try:
            verified, binding_report = _verify_coverage_binding(
                root,
                dataset=name,
                table_path=paths[name],
                frame=frames[name],
                coverage=coverage,
                start=(
                    previous_session_start
                    if name in {"price_limits", TRADING_CALENDAR_TABLE}
                    else coverage_start
                ),
                end=coverage_end,
            )
            if name == TRADING_CALENDAR_TABLE and verified:
                sources = binding_report.get("provenance", {}).get("sources", [])
                authoritative = bool(sources) and all(
                    source.get("source_class") == "official_primary"
                    for source in sources
                )
                binding_report["authoritative_primary"] = authoritative
                verified = verified and authoritative
                binding_report["verified"] = verified
                if not authoritative:
                    binding_report["reason"] = "calendar_requires_official_primary"
            binding_ok[name] = verified
            reports[name]["coverage_binding"] = binding_report
            if not verified:
                warnings.append(
                    f"{name}: coverage 声明缺少可核验文件/Schema/原始响应绑定"
                )
        except (OSError, ValueError, KeyError, TypeError, PitContractError) as exc:
            reports[name]["coverage_binding"] = {
                "verified": False,
                "reason": "invalid_binding",
                "error": str(exc),
            }
            errors.append(f"{name}.coverage_binding: {exc}")

    daily_state_audit = _audit_daily_trade_state_coverage(
        frames,
        start=coverage_start,
        end=coverage_end,
    )
    reports["sample_trade_state_audit"] = daily_state_audit
    semantic_contradictions = (
        "missing_suspension_member_dates:",
        "missing_price_limit_member_dates:",
        "missing_previous_close_member_dates:",
        "price_limit_recalculation_mismatches:",
        "trade_state_dates_not_in_calendar:",
    )
    trade_state_bindings_verified = all(
        binding_ok.get(name, False)
        for name in (
            "security_master",
            "st_status",
            "suspensions",
            "price_limits",
            "index_membership",
            TRADING_CALENDAR_TABLE,
        )
    )
    if trade_state_bindings_verified:
        for issue in daily_state_audit.get("issues", []):
            if str(issue).startswith(semantic_contradictions):
                errors.append(f"sample_trade_state_audit: {issue}")
    st_semantic_ok = bool(daily_state_audit.get("st_coverage_verified"))
    suspension_semantic_ok = (
        bool(daily_state_audit.get("trade_date_period_verified"))
        and int(daily_state_audit.get("missing_suspension_member_dates", 1)) == 0
    )
    price_limit_semantic_ok = (
        bool(daily_state_audit.get("trade_date_period_verified"))
        and bool(daily_state_audit.get("calendar_primary_key_verified"))
        and bool(daily_state_audit.get("price_rule_schema_verified"))
        and bool(daily_state_audit.get("previous_close_schema_verified"))
        and int(daily_state_audit.get("missing_price_limit_member_dates", 1)) == 0
        and int(daily_state_audit.get("missing_previous_close_member_dates", 1)) == 0
        and int(daily_state_audit.get("price_limit_recalculation_mismatches", 1)) == 0
        and int(daily_state_audit.get("price_limit_recalculation_checked", -1))
        == int(daily_state_audit.get("checked_member_dates", 0))
    )
    membership_master_ok = all(
        _membership_matches_security_master(membership, security_master, index_code)
        for index_code in REQUIRED_INDEX_CODES
    )
    corporate_action_master_ok = _corporate_actions_match_security_master(
        frames.get("corporate_actions"), security_master
    )
    capabilities = {
        "trading_calendar_history": (
            TRADING_CALENDAR_TABLE in frames
            and declared_coverage_ok[TRADING_CALENDAR_TABLE]
            and binding_ok[TRADING_CALENDAR_TABLE]
            and bool(daily_state_audit.get("trade_date_period_verified"))
            and bool(daily_state_audit.get("calendar_primary_key_verified"))
        ),
        "security_master_history": (
            "security_master" in frames
            and declared_coverage_ok["security_master"]
            and binding_ok["security_master"]
            and membership_master_ok
        ),
        "st_history": (
            "st_status" in frames
            and declared_coverage_ok["st_status"]
            and binding_ok["st_status"]
            and st_semantic_ok
        ),
        "suspension_history": (
            "suspensions" in frames
            and declared_coverage_ok["suspensions"]
            and binding_ok["suspensions"]
            and suspension_semantic_ok
        ),
        "price_limit_history": (
            "price_limits" in frames
            and declared_coverage_ok["price_limits"]
            and binding_ok["price_limits"]
            and price_limit_semantic_ok
        ),
        "corporate_action_history": (
            "corporate_actions" in frames
            and declared_coverage_ok["corporate_actions"]
            and binding_ok["corporate_actions"]
            and corporate_action_master_ok
        ),
        "csi300_history": (
            "index_membership" in frames
            and declared_coverage_ok["index_membership"]
            and binding_ok["index_membership"]
            and _membership_covers(
                membership,
                "000300.SH",
                start=coverage_start,
                end=coverage_end,
                expected_constituents=300,
            )
            and _membership_matches_security_master(
                membership,
                security_master,
                "000300.SH",
            )
        ),
        "csi500_history": (
            "index_membership" in frames
            and declared_coverage_ok["index_membership"]
            and binding_ok["index_membership"]
            and _membership_covers(
                membership,
                "000905.SH",
                start=coverage_start,
                end=coverage_end,
                expected_constituents=500,
            )
            and _membership_matches_security_master(
                membership,
                security_master,
                "000905.SH",
            )
        ),
    }
    capabilities["sample_trade_state_history"] = all(
        capabilities.get(name, False)
        for name in (
            "security_master_history",
            "st_history",
            "suspension_history",
            "price_limit_history",
            "csi300_history",
            "csi500_history",
            "trading_calendar_history",
        )
    ) and bool(daily_state_audit.get("verified"))
    if "coverage" in missing:
        warnings.append("缺少 coverage 表，无法证明外部 PIT 数据覆盖完整性")
    for capability, available in capabilities.items():
        if not available:
            warnings.append(f"PIT 能力缺失或覆盖不足: {capability}")
    return PitBundleValidation(frames, reports, missing, errors, warnings, capabilities)


def _canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _inference_as_of(value: Any) -> pd.Timestamp:
    try:
        result = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise AShareDataError("inference as_of 不是有效时间") from exc
    if result.tzinfo is None:
        raise AShareDataError("inference as_of 必须包含时区")
    local = result.tz_convert(SHANGHAI_TZ)
    if local != local.normalize():
        raise AShareDataError(
            "日频 inference as_of 只接受带时区的交易日期零点；盘中时点不支持"
        )
    return local


def _now_shanghai() -> datetime:
    """Return the capture clock through one patchable, production-owned seam."""

    return datetime.now(SHANGHAI_TZ)


def _relative_pit_artifact(root: Path, reference: Any, *, field: str) -> Path:
    if not isinstance(reference, str) or not reference.strip():
        raise PitContractError(f"{field} 不能为空")
    relative = Path(reference)
    if relative.is_absolute() or ".." in relative.parts:
        raise PitContractError(f"{field} 必须是 PIT 根内相对路径")
    candidate = (root / relative).resolve(strict=True)
    if root not in candidate.parents or not candidate.is_file():
        raise PitContractError(f"{field} 越界或不是文件")
    return candidate


def _inference_pit_artifacts(
    root: Path,
    frames: Mapping[str, pd.DataFrame],
) -> list[dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}
    for table_name in MANDATORY_PIT_TABLES:
        table_path = _find_pit_file(root, table_name)
        if table_path is None:
            raise PitContractError(f"inference PIT 缺少表：{table_name}")
        relative = table_path.relative_to(root).as_posix()
        artifacts[relative] = {
            "relative_path": relative,
            "role": "pit_table",
            "dataset": table_name,
            "source": table_path,
        }

    calendar_path = _find_pit_file(root, TRADING_CALENDAR_TABLE)
    if calendar_path is None:
        raise PitContractError(f"inference PIT 缺少表：{TRADING_CALENDAR_TABLE}")
    calendar_relative = calendar_path.relative_to(root).as_posix()
    artifacts[calendar_relative] = {
        "relative_path": calendar_relative,
        "role": "trading_calendar",
        "dataset": TRADING_CALENDAR_TABLE,
        "source": calendar_path,
    }

    coverage = frames.get("coverage")
    if coverage is None or not set(COVERAGE_BINDING_COLUMNS).issubset(coverage.columns):
        raise PitContractError("inference PIT coverage 缺少完整 provenance 绑定")
    for row in coverage.itertuples(index=False):
        if not bool(row.is_complete):
            raise PitContractError(f"inference PIT coverage 未完成：{row.dataset}")
        manifest_path = _relative_pit_artifact(
            root,
            row.source_manifest,
            field=f"{row.dataset}.source_manifest",
        )
        manifest_relative = manifest_path.relative_to(root).as_posix()
        artifacts[manifest_relative] = {
            "relative_path": manifest_relative,
            "role": "provenance_manifest",
            "dataset": str(row.dataset),
            "source": manifest_path,
        }
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise PitContractError(
                f"{row.dataset}: provenance manifest 无法解析"
            ) from exc
        sources = manifest.get("sources") if isinstance(manifest, Mapping) else None
        if not isinstance(sources, list) or not sources:
            raise PitContractError(f"{row.dataset}: provenance sources 为空")
        for index, source in enumerate(sources):
            if not isinstance(source, Mapping):
                raise PitContractError(
                    f"{row.dataset}.sources[{index}] 必须是对象"
                )
            raw_path = _relative_pit_artifact(
                root,
                source.get("path"),
                field=f"{row.dataset}.sources[{index}].path",
            )
            raw_relative = raw_path.relative_to(root).as_posix()
            artifacts[raw_relative] = {
                "relative_path": raw_relative,
                "role": "raw_response",
                "dataset": str(row.dataset),
                "source": raw_path,
            }
    return [artifacts[key] for key in sorted(artifacts)]


def _audit_inference_provenance_times(
    root: Path,
    frames: Mapping[str, pd.DataFrame],
    *,
    as_of: pd.Timestamp,
    generated_at: pd.Timestamp,
) -> dict[str, Any]:
    coverage = frames.get("coverage")
    if coverage is None:
        raise PitContractError("inference PIT 缺少 coverage")
    retrieved_values: list[pd.Timestamp] = []
    for row in coverage.itertuples(index=False):
        manifest_path = _relative_pit_artifact(
            root,
            row.source_manifest,
            field=f"{row.dataset}.source_manifest",
        )
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise PitContractError(
                f"{row.dataset}: provenance manifest 无法解析"
            ) from exc
        sources = manifest.get("sources") if isinstance(manifest, Mapping) else None
        if not isinstance(sources, list) or not sources:
            raise PitContractError(f"{row.dataset}: provenance sources 为空")
        for index, source in enumerate(sources):
            try:
                retrieved = pd.Timestamp(source.get("retrieved_at"))
            except (TypeError, ValueError) as exc:
                raise PitContractError(
                    f"{row.dataset}.sources[{index}].retrieved_at 无效"
                ) from exc
            if retrieved.tzinfo is None:
                raise PitContractError(
                    f"{row.dataset}.sources[{index}].retrieved_at 必须包含时区"
                )
            if retrieved > generated_at:
                raise PitContractError(
                    f"{row.dataset}.sources[{index}] 在 snapshot 之后抓取"
                )
            if retrieved.tz_convert(SHANGHAI_TZ).date() > as_of.date():
                raise PitContractError(
                    f"{row.dataset}.sources[{index}] 在 as_of 之后抓取"
                )
            retrieved_values.append(retrieved.tz_convert(timezone.utc))
    if not retrieved_values:
        raise PitContractError("inference PIT provenance 未包含原始响应抓取时间")
    return {
        "provenance_source_count": len(retrieved_values),
        "latest_retrieved_at": max(retrieved_values).isoformat(),
        "retrieval_not_after_snapshot": True,
        "retrieval_not_after_as_of_date": True,
    }


def _inference_universe(
    frames: Mapping[str, pd.DataFrame],
    as_of_date: date,
) -> tuple[list[str], dict[str, bool]]:
    membership = frames.get("index_membership")
    suspensions = frames.get("suspensions")
    if membership is None or suspensions is None:
        raise PitContractError("inference PIT 缺少成分或停牌表")
    local_date = pd.Timestamp(as_of_date)
    members = membership[
        membership["index_code"].astype(str).isin(REQUIRED_INDEX_CODES)
        & (membership["effective_from"] <= local_date)
        & (
            membership["effective_to"].isna()
            | (membership["effective_to"] >= local_date)
        )
    ]
    universe = sorted(members["ticker"].astype(str).unique().tolist())
    if not universe:
        raise PitContractError("inference as_of 的 CSI800 股票池为空")
    day_state = suspensions[suspensions["trade_date"] == local_date]
    if day_state["ticker"].duplicated().any():
        raise PitContractError("inference suspensions 同日 ticker 重复")
    suspended = {
        str(row.ticker): bool(row.is_suspended)
        for row in day_state.itertuples(index=False)
    }
    missing = sorted(set(universe) - set(suspended))
    if missing:
        raise PitContractError(
            f"inference suspensions 未覆盖当日成分：count={len(missing)}"
        )
    return universe, {ticker: suspended[ticker] for ticker in universe}


def _inference_input_binding(
    *,
    as_of: pd.Timestamp,
    universe: Sequence[str],
    market_files: Sequence[Mapping[str, Any]],
    pit_files: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    deterministic_market = [
        {
            "ticker": str(item["ticker"]),
            "relative_path": str(item["relative_path"]),
            "bytes": int(item["bytes"]),
            "sha256": str(item["sha256"]),
            "records": int(item["records"]),
            "first_date": str(item["first_date"]),
            "last_date": str(item["last_date"]),
            "is_suspended": bool(item["is_suspended"]),
        }
        for item in market_files
    ]
    deterministic_pit = [
        {
            "relative_path": str(item["relative_path"]),
            "role": str(item["role"]),
            "dataset": str(item["dataset"]),
            "bytes": int(item["bytes"]),
            "sha256": str(item["sha256"]),
        }
        for item in pit_files
    ]
    return {
        "schema_version": INFERENCE_INPUT_BINDING_SCHEMA,
        "as_of": as_of.isoformat(),
        "universe_count": len(universe),
        "universe_sha256": _canonical_json_sha256({"tickers": list(universe)}),
        "market_files": deterministic_market,
        "pit_files": deterministic_pit,
    }


def _inference_snapshot_root(
    training_root: Path,
    *,
    project_root: Path,
) -> Path:
    return guard_output_path(
        training_root / "data" / "inference" / "snapshots",
        training_root=training_root,
        project_root=project_root,
    )


def create_inference_snapshot(
    source_root: str | os.PathLike[str],
    pit_root: str | os.PathLike[str],
    training_root: str | os.PathLike[str] = DEFAULT_TRAINING_ROOT,
    *,
    as_of: Any,
    dry_run: bool = False,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
) -> dict[str, Any]:
    """Build one immutable daily inference input without changing training data.

    Only this explicit snapshot operation may read the active TDX tree. Scoring
    consumes the copied market/PIT files and their deterministic input binding.
    """

    project = _resolved(project_root)
    target_root = guard_training_root(training_root, project_root=project)
    data_root = (target_root / "data").resolve(strict=False)
    source = _resolved(source_root)
    pit_source = _resolved(pit_root)
    if pit_source == data_root or data_root not in pit_source.parents:
        raise UnsafePathError("inference PIT 源必须位于训练根 data 子目录内")
    snapshot_parent = _inference_snapshot_root(target_root, project_root=project)
    if pit_source == snapshot_parent or snapshot_parent in pit_source.parents:
        raise UnsafePathError("inference PIT 源不得位于不可变快照目录内")
    if source == target_root or source in target_root.parents or target_root in source.parents:
        raise UnsafePathError("活动行情源与训练目录不得相互包含")

    observed_at = _inference_as_of(as_of)
    now = _now_shanghai()
    if observed_at.date() != now.date():
        raise AShareDataError("inference snapshot 只能在对应交易日当日生成")
    if now.timetz().replace(tzinfo=None) < time(15, 0):
        raise AShareDataError("日频 inference snapshot 只能在15:00收盘后生成")
    coverage_date = observed_at.date()
    pit_validation = validate_pit_bundle(
        pit_source,
        coverage_start=coverage_date,
        coverage_end=coverage_date,
    )
    if not pit_validation.production_ready:
        raise PitContractError(
            "当日 inference PIT 未达到 production_ready："
            + ";".join(
                [*pit_validation.errors, *pit_validation.missing_tables, *pit_validation.warnings]
            )
        )
    universe, suspended = _inference_universe(
        pit_validation.frames,
        coverage_date,
    )
    pit_artifacts = _inference_pit_artifacts(pit_source, pit_validation.frames)
    generated_at = datetime.now(timezone.utc)
    provenance_time_audit = _audit_inference_provenance_times(
        pit_source,
        pit_validation.frames,
        as_of=observed_at,
        generated_at=pd.Timestamp(generated_at),
    )

    market_files: list[dict[str, Any]] = []
    for ticker in universe:
        code, exchange = ticker.split(".")
        market = exchange.lower()
        path = source / "vipdoc" / market / "lday" / f"{market}{code}.day"
        if not path.is_file():
            raise FileNotFoundError(f"活动行情缺少当日成分日线：{ticker}")
        source_payload = path.read_bytes()
        source_metadata, _ = _decode_tdx_day(
            source_payload,
            source=str(path),
            collect_rows=False,
        )
        if int(source_metadata["records"]) < INFERENCE_MARKET_RECORDS:
            raise TdxDayFormatError(
                f"{ticker}: inference 历史不足{INFERENCE_MARKET_RECORDS}根"
            )
        snapshot_payload = source_payload[
            -INFERENCE_MARKET_RECORDS * TDX_DAY_RECORD_SIZE :
        ]
        metadata, _ = _decode_tdx_day(
            snapshot_payload,
            source=f"{path}#tail-{INFERENCE_MARKET_RECORDS}",
            collect_rows=False,
        )
        last_date = date.fromisoformat(str(metadata["last_date"]))
        if last_date > coverage_date:
            raise TdxDayFormatError(f"{ticker}: 行情包含 as_of 之后数据")
        if not suspended[ticker] and last_date != coverage_date:
            raise TdxDayFormatError(f"{ticker}: 非停牌证券缺少 as_of 日线")
        market_files.append(
            {
                "ticker": ticker,
                "relative_path": f"market/tdx_day/{market}/{market}{code}.day",
                "bytes": len(snapshot_payload),
                "sha256": _sha256_bytes(snapshot_payload),
                "records": int(metadata["records"]),
                "first_date": str(metadata["first_date"]),
                "last_date": str(metadata["last_date"]),
                "is_suspended": suspended[ticker],
                "source": path,
                "source_bytes": len(source_payload),
                "source_sha256": _sha256_bytes(source_payload),
                "payload": snapshot_payload,
            }
        )
    market_files.sort(key=lambda item: item["ticker"])
    pit_files = [
        {
            "relative_path": f"pit/{item['relative_path']}",
            "pit_relative_path": item["relative_path"],
            "role": item["role"],
            "dataset": item["dataset"],
            "bytes": item["source"].stat().st_size,
            "sha256": _sha256_file(item["source"]),
            "source": item["source"],
        }
        for item in pit_artifacts
    ]
    binding = _inference_input_binding(
        as_of=observed_at,
        universe=universe,
        market_files=market_files,
        pit_files=pit_files,
    )
    input_sha256 = _canonical_json_sha256(binding)
    directory_name = f"{observed_at.strftime('%Y%m%d')}-{input_sha256[:16]}"
    final_path = guard_output_path(
        snapshot_parent / directory_name,
        training_root=target_root,
        project_root=project,
    )
    public_market = [
        {
            key: value
            for key, value in item.items()
            if key not in {"source", "payload"}
        }
        for item in market_files
    ]
    public_pit = [
        {
            key: value
            for key, value in item.items()
            if key not in {"source", "pit_relative_path"}
        }
        for item in pit_files
    ]
    manifest = {
        "schema_version": INFERENCE_SNAPSHOT_SCHEMA,
        "snapshot_id": directory_name,
        "generated_at": generated_at.isoformat(),
        "as_of": observed_at.isoformat(),
        "snapshot_path": str(final_path),
        "dry_run": bool(dry_run),
        "source_consistent": True,
        "pit_production_ready": True,
        "evidence_class": "market_data_vendor+public_pit",
        "active_universe": universe,
        "active_universe_count": len(universe),
        "market_files": public_market,
        "pit_files": public_pit,
        "as_of_audit": {
            "coverage_start": coverage_date.isoformat(),
            "coverage_end": coverage_date.isoformat(),
            "mandatory_pit_tables": list(MANDATORY_PIT_TABLES),
            "mandatory_pit_table_count": len(MANDATORY_PIT_TABLES),
            "all_pit_capabilities_verified": True,
            "all_non_suspended_market_bars_at_as_of": True,
            "future_market_bar_count": 0,
            **provenance_time_audit,
        },
        "input_binding": binding,
        "input_sha256": input_sha256,
    }
    unsigned = dict(manifest)
    manifest["payload_sha256"] = _canonical_json_sha256(unsigned)
    if dry_run:
        return manifest

    snapshot_parent.mkdir(parents=True, exist_ok=True)
    existing_for_date = sorted(snapshot_parent.glob(f"{observed_at.strftime('%Y%m%d')}-*"))
    for existing in existing_for_date:
        existing_manifest = existing / "inference_manifest.json"
        verified = verify_inference_snapshot(
            existing_manifest,
            training_root=target_root,
            project_root=project,
            expected_as_of=observed_at,
        )
        if verified.get("input_sha256") == input_sha256:
            reused = dict(verified)
            reused["reused"] = True
            return reused
    if existing_for_date:
        raise AShareDataError("同一 as_of 已存在不同 inference snapshot，拒绝择时替换")

    staging = Path(tempfile.mkdtemp(prefix=f".{directory_name}.pending-", dir=snapshot_parent))
    published = False
    try:
        for item in market_files:
            destination = staging / item["relative_path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(item["payload"])
            if destination.stat().st_size != item["bytes"] or _sha256_file(destination) != item["sha256"]:
                raise SnapshotSourceChangedError(f"inference 行情复制校验失败：{item['ticker']}")
        for item in pit_files:
            destination = staging / item["relative_path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item["source"], destination)
            if destination.stat().st_size != item["bytes"] or _sha256_file(destination) != item["sha256"]:
                raise SnapshotSourceChangedError(
                    f"inference PIT 复制校验失败：{item['relative_path']}"
                )
        for item in market_files:
            if (
                item["source"].stat().st_size != item["source_bytes"]
                or _sha256_file(item["source"]) != item["source_sha256"]
            ):
                raise SnapshotSourceChangedError("inference snapshot 期间行情源发生变化")
        for item in pit_files:
            if item["source"].stat().st_size != item["bytes"] or _sha256_file(item["source"]) != item["sha256"]:
                raise SnapshotSourceChangedError("inference snapshot 期间源文件发生变化")
        staged_validation = validate_pit_bundle(
            staging / "pit",
            coverage_start=coverage_date,
            coverage_end=coverage_date,
        )
        if not staged_validation.production_ready:
            raise PitContractError("复制后的 inference PIT 未通过当日复验")
        staged_provenance_audit = _audit_inference_provenance_times(
            staging / "pit",
            staged_validation.frames,
            as_of=observed_at,
            generated_at=pd.Timestamp(generated_at),
        )
        if staged_provenance_audit != provenance_time_audit:
            raise PitContractError("复制后的 inference PIT 抓取时间审计漂移")
        (staging / "inference_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(staging, final_path)
        staging = None
        published = True
        verified = verify_inference_snapshot(
            final_path / "inference_manifest.json",
            training_root=target_root,
            project_root=project,
            expected_as_of=observed_at,
        )
        verified["reused"] = False
        return verified
    except Exception:
        if published and final_path.exists():
            _cleanup_staging(
                final_path,
                training_root=target_root,
                project_root=project,
            )
        _cleanup_staging(
            staging,
            training_root=target_root,
            project_root=project,
        )
        raise


def verify_inference_snapshot(
    manifest_path: str | os.PathLike[str],
    *,
    training_root: str | os.PathLike[str] = DEFAULT_TRAINING_ROOT,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
    expected_as_of: Any | None = None,
) -> dict[str, Any]:
    """Rehash and semantically re-audit an immutable daily inference input."""

    project = _resolved(project_root)
    target_root = guard_training_root(training_root, project_root=project)
    path = guard_output_path(
        manifest_path,
        training_root=target_root,
        project_root=project,
    )
    expected_parent = _inference_snapshot_root(target_root, project_root=project)
    if path.name != "inference_manifest.json" or path.parent.parent != expected_parent:
        raise AShareDataError("inference manifest 路径无效")
    if not path.is_file():
        raise AShareDataError("inference manifest 不存在")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AShareDataError("inference manifest 无法解析") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != INFERENCE_SNAPSHOT_SCHEMA:
        raise AShareDataError("inference manifest schema 无效")
    if (
        manifest.get("dry_run") is not False
        or manifest.get("source_consistent") is not True
        or manifest.get("pit_production_ready") is not True
    ):
        raise AShareDataError("inference manifest 状态不允许评分")
    declared_payload = manifest.get("payload_sha256")
    unsigned = dict(manifest)
    unsigned.pop("payload_sha256", None)
    if declared_payload != _canonical_json_sha256(unsigned):
        raise AShareDataError("inference manifest payload SHA256 漂移")
    observed_at = _inference_as_of(manifest.get("as_of"))
    if expected_as_of is not None and observed_at != _inference_as_of(expected_as_of):
        raise AShareDataError("inference snapshot as_of 与评分请求不一致")
    try:
        generated_at = pd.Timestamp(manifest.get("generated_at"))
    except (TypeError, ValueError) as exc:
        raise AShareDataError("inference generated_at 无效") from exc
    if generated_at.tzinfo is None:
        raise AShareDataError("inference generated_at 必须包含时区")
    if generated_at.tz_convert(SHANGHAI_TZ).date() != observed_at.date():
        raise AShareDataError("inference snapshot 不是 as_of 当日生成")
    snapshot_root = path.parent.resolve()
    if _resolved(str(manifest.get("snapshot_path", ""))) != snapshot_root:
        raise AShareDataError("inference snapshot_path 与 manifest 目录不一致")

    universe = manifest.get("active_universe")
    market_files = manifest.get("market_files")
    pit_files = manifest.get("pit_files")
    if (
        not isinstance(universe, list)
        or not universe
        or universe != sorted(set(map(str, universe)))
        or manifest.get("active_universe_count") != len(universe)
        or not isinstance(market_files, list)
        or not isinstance(pit_files, list)
    ):
        raise AShareDataError("inference manifest universe/files 合同无效")
    expected_files = {"inference_manifest.json"}
    for collection, prefix in ((market_files, "market/"), (pit_files, "pit/")):
        for item in collection:
            if not isinstance(item, Mapping):
                raise AShareDataError("inference files 行必须是对象")
            relative_text = str(item.get("relative_path", ""))
            relative = Path(relative_text)
            if (
                not relative_text.startswith(prefix)
                or relative.is_absolute()
                or ".." in relative.parts
            ):
                raise AShareDataError("inference relative_path 越界")
            candidate = (snapshot_root / relative).resolve(strict=True)
            if snapshot_root not in candidate.parents or not candidate.is_file():
                raise AShareDataError("inference 文件缺失或越界")
            expected_files.add(relative.as_posix())
            if (
                candidate.stat().st_size != int(item.get("bytes", -1))
                or _sha256_file(candidate) != item.get("sha256")
            ):
                raise AShareDataError(f"inference 文件哈希漂移：{relative_text}")
    actual_files = {
        item.relative_to(snapshot_root).as_posix()
        for item in snapshot_root.rglob("*")
        if item.is_file()
    }
    if actual_files != expected_files:
        raise AShareDataError("inference snapshot 文件集合漂移")
    bound_tables = {
        str(item.get("dataset"))
        for item in pit_files
        if item.get("role") == "pit_table"
    }
    if bound_tables != set(MANDATORY_PIT_TABLES):
        raise AShareDataError("inference snapshot 未绑定全部7张 PIT 表")
    calendar_tables = [
        item
        for item in pit_files
        if item.get("role") == "trading_calendar"
        and item.get("dataset") == TRADING_CALENDAR_TABLE
    ]
    calendar_provenance = [
        item
        for item in pit_files
        if item.get("role") == "provenance_manifest"
        and item.get("dataset") == TRADING_CALENDAR_TABLE
    ]
    calendar_raw_responses = [
        item
        for item in pit_files
        if item.get("role") == "raw_response"
        and item.get("dataset") == TRADING_CALENDAR_TABLE
    ]
    if (
        len(calendar_tables) != 1
        or len(calendar_provenance) != 1
        or not calendar_raw_responses
    ):
        raise AShareDataError(
            "inference snapshot 未完整绑定 trading_calendar 表、provenance 与原始响应"
        )

    pit_root = snapshot_root / "pit"
    pit_validation = validate_pit_bundle(
        pit_root,
        coverage_start=observed_at.date(),
        coverage_end=observed_at.date(),
    )
    if not pit_validation.production_ready:
        raise PitContractError("inference snapshot PIT 当日语义复验失败")
    provenance_time_audit = _audit_inference_provenance_times(
        pit_root,
        pit_validation.frames,
        as_of=observed_at,
        generated_at=generated_at,
    )
    observed_universe, suspended = _inference_universe(
        pit_validation.frames,
        observed_at.date(),
    )
    if observed_universe != universe:
        raise AShareDataError("inference snapshot 股票池与 PIT as_of 不一致")
    market_by_ticker = {str(item.get("ticker")): item for item in market_files}
    if set(market_by_ticker) != set(universe) or len(market_by_ticker) != len(market_files):
        raise AShareDataError("inference market files 未完整覆盖股票池")
    for ticker in universe:
        item = market_by_ticker[ticker]
        if bool(item.get("is_suspended")) != suspended[ticker]:
            raise AShareDataError(f"{ticker}: inference 停牌绑定漂移")
        market_path = snapshot_root / str(item["relative_path"])
        metadata = inspect_tdx_day(market_path)
        if any(
            metadata.get(key) != item.get(key)
            for key in ("records", "first_date", "last_date")
        ):
            raise AShareDataError(f"{ticker}: inference 日线元数据漂移")
        if int(metadata["records"]) != INFERENCE_MARKET_RECORDS:
            raise AShareDataError(
                f"{ticker}: inference 日线必须包含90根输入及1根复权前序"
            )
        last_date = date.fromisoformat(str(metadata["last_date"]))
        if last_date > observed_at.date():
            raise AShareDataError(f"{ticker}: inference 行情穿越 as_of")
        if not suspended[ticker] and last_date != observed_at.date():
            raise AShareDataError(f"{ticker}: 非停牌证券缺少 as_of 日线")

    binding = _inference_input_binding(
        as_of=observed_at,
        universe=universe,
        market_files=market_files,
        pit_files=pit_files,
    )
    input_sha256 = _canonical_json_sha256(binding)
    if manifest.get("input_binding") != binding or manifest.get("input_sha256") != input_sha256:
        raise AShareDataError("inference input binding/hash 漂移")
    expected_snapshot_id = f"{observed_at.strftime('%Y%m%d')}-{input_sha256[:16]}"
    if manifest.get("snapshot_id") != expected_snapshot_id or snapshot_root.name != expected_snapshot_id:
        raise AShareDataError("inference snapshot_id 与 input hash 不一致")
    audit = manifest.get("as_of_audit")
    if not isinstance(audit, Mapping) or any(
        audit.get(key) != value
        for key, value in {
            "coverage_start": observed_at.date().isoformat(),
            "coverage_end": observed_at.date().isoformat(),
            "mandatory_pit_table_count": len(MANDATORY_PIT_TABLES),
            "all_pit_capabilities_verified": True,
            "all_non_suspended_market_bars_at_as_of": True,
            "future_market_bar_count": 0,
            **provenance_time_audit,
        }.items()
    ):
        raise AShareDataError("inference coverage/as_of 审计声明无效")
    return manifest


def _decimal(value: Decimal | int | float | str) -> Decimal:
    result = value if isinstance(value, Decimal) else Decimal(str(value))
    if not result.is_finite():
        raise ValueError(f"数值不是有限数: {value!r}")
    return result


def _no_limit_for_ipo(
    *,
    board: str,
    listing_date: date | None,
    trading_day_number: int | None,
) -> bool:
    if listing_date is None or trading_day_number is None or trading_day_number <= 0:
        return False
    if board == "main":
        return listing_date >= date(2023, 4, 10) and trading_day_number <= 5
    if board == "chinext":
        return listing_date >= date(2020, 8, 24) and trading_day_number <= 5
    if board == "star":
        return trading_day_number <= 5
    if board == "bse":
        return trading_day_number == 1
    return False


def resolve_price_limit_rule(
    trade_date: date,
    *,
    exchange: str,
    board: str,
    is_st: bool = False,
    listing_date: date | None = None,
    trading_day_number: int | None = None,
    no_limit_reason: str | None = None,
) -> tuple[Decimal | None, str, str | None]:
    exchange = exchange.upper()
    board = board.lower()
    if exchange not in {"SH", "SZ", "BJ"}:
        raise ValueError(f"未知交易所: {exchange}")
    if board not in {"main", "chinext", "star", "bse"}:
        raise ValueError(f"未知板块: {board}")
    board_mismatch = (
        (board == "star" and exchange != "SH")
        or (board == "chinext" and exchange != "SZ")
        or (board == "bse" and exchange != "BJ")
    )
    if board_mismatch:
        raise ValueError(f"交易所与板块不匹配: {exchange}/{board}")
    if board == "main" and exchange not in {"SH", "SZ"}:
        raise ValueError(f"交易所与主板不匹配: {exchange}")

    if no_limit_reason:
        return None, "explicit_no_limit", no_limit_reason
    if _no_limit_for_ipo(
        board=board,
        listing_date=listing_date,
        trading_day_number=trading_day_number,
    ):
        return None, f"{board}_ipo_no_limit", "ipo_initial_trading_days"

    if board == "main":
        if is_st and trade_date < date(2026, 7, 6):
            return Decimal("0.05"), "main_st_pre_20260706_5pct", None
        if is_st:
            return Decimal("0.10"), "main_st_from_20260706_10pct", None
        return Decimal("0.10"), "main_normal_10pct", None
    if board == "chinext":
        if trade_date < date(2020, 8, 24):
            return Decimal("0.10"), "chinext_pre_20200824_10pct", None
        return Decimal("0.20"), "chinext_from_20200824_20pct", None
    if board == "star":
        return Decimal("0.20"), "star_20pct", None
    return Decimal("0.30"), "bse_30pct", None


def calculate_price_limits(
    previous_close: Decimal | int | float | str,
    trade_date: date,
    *,
    exchange: str,
    board: str,
    is_st: bool = False,
    listing_date: date | None = None,
    trading_day_number: int | None = None,
    no_limit_reason: str | None = None,
    tick_size: Decimal | int | float | str = Decimal("0.01"),
) -> PriceLimitResult:
    close = _decimal(previous_close)
    tick = _decimal(tick_size)
    if close <= 0 or tick <= 0:
        raise ValueError("previous_close 和 tick_size 必须为正数")
    ratio, rule_version, resolved_reason = resolve_price_limit_rule(
        trade_date,
        exchange=exchange,
        board=board,
        is_st=is_st,
        listing_date=listing_date,
        trading_day_number=trading_day_number,
        no_limit_reason=no_limit_reason,
    )
    if ratio is None:
        return PriceLimitResult(None, None, None, rule_version, resolved_reason)

    up = (close * (Decimal("1") + ratio)).quantize(tick, rounding=ROUND_HALF_UP)
    down = (close * (Decimal("1") - ratio)).quantize(tick, rounding=ROUND_HALF_UP)
    if up - close < tick:
        up = close + tick
    if close - down < tick:
        down = max(tick, close - tick)
    down = max(tick, down)
    return PriceLimitResult(up, down, ratio, rule_version)


def split_contract() -> dict[str, Any]:
    return {
        "lookback": LOOKBACK,
        "horizon": HORIZON,
        "purge_sessions": PURGE_SESSIONS,
        "splits": [
            {"name": item.name, "start": item.start.isoformat(), "end": item.end.isoformat()}
            for item in FIXED_SPLITS
        ],
    }


def build_split_assignments(trading_calendar: Sequence[Any]) -> pd.DataFrame:
    """Assign eligible signal dates after applying 90/10 and an 11-session purge."""

    calendar = pd.DatetimeIndex(pd.to_datetime(list(trading_calendar), errors="raise")).normalize()
    calendar = calendar.drop_duplicates().sort_values()
    if len(calendar) <= LOOKBACK:
        raise ValueError("交易日历不足以提供 90 个回看交易日")
    positions = {timestamp: index for index, timestamp in enumerate(calendar)}
    rows: list[dict[str, Any]] = []
    for split in FIXED_SPLITS:
        segment = calendar[(calendar.date >= split.start) & (calendar.date <= split.end)]
        if len(segment) <= PURGE_SESSIONS:
            continue
        for signal_date in segment[:-PURGE_SESSIONS]:
            position = positions[signal_date]
            window_start_position = position - LOOKBACK + 1
            if window_start_position < 0:
                continue
            window_start = calendar[window_start_position]
            if window_start.date() < split.start:
                continue
            label_end_position = position + HORIZON
            if label_end_position >= len(calendar):
                continue
            label_end = calendar[label_end_position]
            if label_end.date() > split.end:
                continue
            rows.append(
                {
                    "window_start_date": window_start,
                    "signal_date": signal_date,
                    "label_end_date": label_end,
                    "split": split.name,
                }
            )
    return pd.DataFrame(
        rows,
        columns=("window_start_date", "signal_date", "label_end_date", "split"),
    )


def build_data_quality_report(
    snapshot_manifest: Mapping[str, Any] | None,
    pit_validation: PitBundleValidation | None,
    model_adjustment_manifest: Mapping[str, Any] | None = None,
    *,
    model_adjustment_verified: bool = False,
    model_adjustment_error: str | None = None,
) -> dict[str, Any]:
    blocking: list[str] = []
    provisional: list[str] = []

    if not snapshot_manifest:
        blocking.append("missing_snapshot_manifest")
        snapshot_summary: dict[str, Any] | None = None
    else:
        snapshot_summary = {
            "snapshot_id": snapshot_manifest.get("snapshot_id"),
            "source_consistent": bool(snapshot_manifest.get("source_consistent")),
            "kind_counts": snapshot_manifest.get("kind_counts", {}),
            "dry_run": bool(snapshot_manifest.get("dry_run")),
        }
        if not snapshot_summary["source_consistent"]:
            blocking.append("snapshot_source_changed")
        if int(snapshot_summary["kind_counts"].get("tdx_day", 0)) <= 0:
            blocking.append("missing_tdx_day_files")
        if int(snapshot_summary["kind_counts"].get("gbbq", 0)) != 1:
            blocking.append("missing_gbbq")
        if int(snapshot_summary["kind_counts"].get("base_dbf", 0)) != 1:
            blocking.append("missing_base_dbf")
        if snapshot_summary["dry_run"]:
            provisional.append("snapshot_is_dry_run")

    pit_report = pit_validation.to_report() if pit_validation is not None else None
    if pit_validation is None:
        provisional.extend(f"missing_capability:{name}" for name in REQUIRED_CAPABILITIES)
    else:
        blocking.extend(f"pit_contract_error:{error}" for error in pit_validation.errors)
        provisional.extend(f"missing_pit_table:{name}" for name in pit_validation.missing_tables)
        provisional.extend(
            f"missing_capability:{name}"
            for name in REQUIRED_CAPABILITIES
            if not pit_validation.capabilities.get(name, False)
        )

    adjustment_summary: dict[str, Any] | None = None
    if model_adjustment_error:
        blocking.append(f"invalid_model_adjustment_artifact:{model_adjustment_error}")
    if model_adjustment_manifest is None:
        provisional.append("model_price_adjusted_not_materialized")
    else:
        adjustment = model_adjustment_manifest.get("adjustment")
        if not isinstance(adjustment, Mapping):
            blocking.append("invalid_model_adjustment_manifest:missing_adjustment")
        else:
            adjustment_summary = {
                "schema_version": model_adjustment_manifest.get("schema_version"),
                "mode": adjustment.get("mode"),
                "materialized": bool(adjustment.get("materialized")),
                "trade_price_raw": bool(adjustment.get("trade_price_raw")),
                "model_price_adjusted": bool(adjustment.get("model_price_adjusted")),
                "cutoff_field": adjustment.get("cutoff_field"),
                "future_action_use_count": adjustment.get("future_action_use_count"),
            }
            expected = {
                "schema_version": MODEL_ADJUSTMENT_SCHEMA,
                "mode": "causal_backward_total_return",
                "materialized": True,
                "trade_price_raw": True,
                "model_price_adjusted": True,
                "cutoff_field": "origin_date",
                "future_action_use_count": 0,
            }
            for key, expected_value in expected.items():
                actual = adjustment_summary.get(key)
                if actual != expected_value:
                    blocking.append(
                        f"invalid_model_adjustment_manifest:{key}={actual!r}"
                    )
            if not model_adjustment_verified:
                provisional.append("model_adjustment_manifest_unverified")

    blocking = list(dict.fromkeys(blocking))
    provisional = list(dict.fromkeys(provisional))
    status = "blocked" if blocking else "local_provisional" if provisional else "production_ready"
    return {
        "schema_version": 1,
        "generated_at": _utc_now(),
        "status": status,
        "evidence_class": "market_data_vendor",
        "blocking_issues": blocking,
        "provisional_issues": provisional,
        "snapshot": snapshot_summary,
        "pit": pit_report,
        "model_adjustment": adjustment_summary,
        "split_contract": split_contract(),
    }


def _verify_model_adjustment_artifact(
    manifest_path: str | os.PathLike[str],
    *,
    training_root: str | os.PathLike[str],
    project_root: str | os.PathLike[str],
    snapshot_manifest_path: Path,
    pit_validation: PitBundleValidation,
) -> dict[str, Any]:
    path = guard_training_root(manifest_path, project_root=project_root)
    guard_training_root(training_root, project_root=project_root)
    if not path.is_file() or path.name != "manifest.json":
        raise PitContractError("model adjustment manifest 路径无效")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != MODEL_ADJUSTMENT_SCHEMA:
        raise PitContractError("model adjustment schema_version 无效")
    sample_count = int(manifest.get("sample_count", -1))
    if sample_count < 1:
        raise PitContractError("model adjustment sample_count 无效")
    required_layout = {
        "s1.npy": (np.dtype("uint16"), (sample_count, 100)),
        "s2.npy": (np.dtype("uint16"), (sample_count, 100)),
        "stamp.npy": (np.dtype("uint8"), (sample_count, 100, 5)),
        "label.npy": (np.dtype("float32"), (sample_count,)),
        "trade_date.npy": (np.dtype("int32"), (sample_count,)),
        "instrument_id.npy": (np.dtype("int32"), (sample_count,)),
        "split.npy": (np.dtype("uint8"), (sample_count,)),
    }
    files = manifest.get("files")
    if not isinstance(files, Mapping) or set(files) != set(required_layout):
        raise PitContractError("model adjustment token files 合同不完整")
    for filename, (expected_dtype, expected_shape) in required_layout.items():
        file_path = guard_training_root(path.parent / filename, project_root=project_root)
        if not file_path.is_file():
            raise PitContractError(f"model adjustment 缺少 {filename}")
        contract = files[filename]
        if int(contract.get("bytes", -1)) != file_path.stat().st_size:
            raise PitContractError(f"model adjustment {filename} 字节数不匹配")
        if contract.get("sha256") != _sha256_file(file_path):
            raise PitContractError(f"model adjustment {filename} SHA256 不匹配")
        array = np.load(file_path, mmap_mode="r", allow_pickle=False)
        if array.dtype != expected_dtype or array.shape != expected_shape:
            raise PitContractError(
                f"model adjustment {filename} dtype/shape 不匹配"
            )

    if not snapshot_manifest_path.is_file():
        raise PitContractError("snapshot manifest 未以文件绑定")
    if manifest.get("snapshot_manifest_sha256") != _sha256_file(snapshot_manifest_path):
        raise PitContractError("snapshot manifest SHA256 绑定不匹配")
    for key in ("sample_index_path", "sample_manifest_path"):
        raw = manifest.get(key)
        if not isinstance(raw, str):
            raise PitContractError(f"model adjustment 缺少 {key}")
        artifact_path = guard_training_root(raw, project_root=project_root)
        if not artifact_path.is_file():
            raise PitContractError(f"model adjustment {key} 越界或缺失")
        digest_key = key.replace("_path", "_sha256")
        if manifest.get(digest_key) != _sha256_file(artifact_path):
            raise PitContractError(f"model adjustment {digest_key} 不匹配")

    for field, table_name in (
        ("membership_sha256", "index_membership"),
        ("corporate_actions_sha256", "corporate_actions"),
    ):
        expected = pit_validation.table_reports.get(table_name, {}).get("sha256")
        if not expected or manifest.get(field) != expected:
            raise PitContractError(f"model adjustment {field} 与 PIT 不匹配")
    verified = dict(manifest)
    verified["artifact_verification"] = {
        "verified": True,
        "manifest_path": str(path),
        "manifest_sha256": _sha256_file(path),
        "verified_file_count": len(required_layout),
    }
    return verified


def write_data_quality_report(
    output_path: str | os.PathLike[str],
    report: Mapping[str, Any],
    *,
    training_root: str | os.PathLike[str] = DEFAULT_TRAINING_ROOT,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
) -> Path:
    output = guard_output_path(
        output_path,
        training_root=training_root,
        project_root=project_root,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(dict(report), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return output


def prepare_data_gate(
    snapshot_manifest: Mapping[str, Any] | str | os.PathLike[str],
    pit_root: str | os.PathLike[str],
    *,
    output_path: str | os.PathLike[str] | None = None,
    training_root: str | os.PathLike[str] = DEFAULT_TRAINING_ROOT,
    project_root: str | os.PathLike[str] = PROJECT_ROOT,
    coverage_start: date = PIT_START,
    coverage_end: date = PIT_END,
    model_adjustment_manifest: Mapping[str, Any] | str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    """Validate snapshot + external PIT inputs and optionally persist the gate report."""

    manifest = (
        dict(snapshot_manifest)
        if isinstance(snapshot_manifest, Mapping)
        else load_snapshot_manifest(snapshot_manifest)
    )
    snapshot_manifest_path = (
        Path(snapshot_manifest).resolve()
        if not isinstance(snapshot_manifest, Mapping)
        else Path()
    )
    pit_validation = validate_pit_bundle(
        pit_root,
        coverage_start=coverage_start,
        coverage_end=coverage_end,
    )
    adjustment_verified = False
    adjustment_error = None
    if model_adjustment_manifest is None:
        adjustment_manifest = None
    elif isinstance(model_adjustment_manifest, Mapping):
        adjustment_manifest = dict(model_adjustment_manifest)
    else:
        try:
            adjustment_manifest = _verify_model_adjustment_artifact(
                model_adjustment_manifest,
                training_root=training_root,
                project_root=project_root,
                snapshot_manifest_path=snapshot_manifest_path,
                pit_validation=pit_validation,
            )
            adjustment_verified = True
        except (OSError, ValueError, KeyError, TypeError, PitContractError) as exc:
            adjustment_manifest = None
            adjustment_error = str(exc)
    report = build_data_quality_report(
        manifest,
        pit_validation,
        adjustment_manifest,
        model_adjustment_verified=adjustment_verified,
        model_adjustment_error=adjustment_error,
    )
    if output_path is not None:
        write_data_quality_report(
            output_path,
            report,
            training_root=training_root,
            project_root=project_root,
        )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kronos A 股训练数据合同与快照工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="校验或复制不可变 TDX 快照")
    snapshot.add_argument("--source-root", default=str(DEFAULT_TDX_ROOT))
    snapshot.add_argument("--training-root", default=str(DEFAULT_TRAINING_ROOT))
    snapshot.add_argument("--snapshot-id")
    snapshot.add_argument("--copy", action="store_true", help="实际复制；默认仅 dry-run")

    validate_pit = subparsers.add_parser("validate-pit", help="校验外部 PIT CSV/Parquet")
    validate_pit.add_argument("pit_root")

    limit = subparsers.add_parser("price-limit", help="计算版本化 A 股涨跌停价")
    limit.add_argument("previous_close")
    limit.add_argument("trade_date")
    limit.add_argument("--exchange", required=True)
    limit.add_argument("--board", required=True)
    limit.add_argument("--st", action="store_true")

    subparsers.add_parser("show-splits", help="输出固定训练切分合同")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "snapshot":
        payload = create_immutable_snapshot(
            args.source_root,
            args.training_root,
            snapshot_id=args.snapshot_id,
            dry_run=not args.copy,
        )
    elif args.command == "validate-pit":
        payload = validate_pit_bundle(args.pit_root).to_report()
    elif args.command == "price-limit":
        payload = calculate_price_limits(
            args.previous_close,
            date.fromisoformat(args.trade_date),
            exchange=args.exchange,
            board=args.board,
            is_st=args.st,
        ).to_dict()
    else:
        payload = split_contract()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
