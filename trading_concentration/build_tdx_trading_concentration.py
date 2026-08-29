"""构建“通达信全A等权 AMOUNT 口径 C5”交易集中度日度发布包。

原始输入只读自用户的 ``D:\\HT\\vipdoc`` 日线目录；本任务目录只落盘
加工后的 CSV、JSON 和 manifest，不复制任何原始 .day 文件。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import numpy as np


DAY_DTYPE = np.dtype(
    [
        ("date", "<u4"),
        ("open", "<u4"),
        ("high", "<u4"),
        ("low", "<u4"),
        ("close", "<u4"),
        ("amount", "<f4"),
        ("volume", "<u4"),
        ("reserved", "<u4"),
    ]
)
DAY_RECORD_BYTES = DAY_DTYPE.itemsize

START_DATE = 20130101
BEIJING_UNIVERSE_SWITCH_DATE = 20220802
TASK_DIRECTORY = Path("trading_concentration")
DEFAULT_OUTPUT_DIRECTORY = TASK_DIRECTORY / "data"
PUBLISH_DIRECTORY = Path(r"D:\vcp_hunter\基金持仓\public\data")
PAYLOAD_FILENAME = "trading-concentration-dashboard.json"
MANIFEST_FILENAME = "trading-concentration-dashboard.manifest.json"
CSV_FILENAME = "trading-concentration-daily.csv"

MARKET_DIRECTORIES = {
    "sh": Path("vipdoc/sh/lday"),
    "sz": Path("vipdoc/sz/lday"),
    "bj": Path("vipdoc/bj/lday"),
}
CANDIDATE_PREFIXES = {
    "sh": ("600", "601", "603", "605", "688", "689"),
    "sz": ("000", "001", "002", "003", "300", "301"),
    "bj": ("43", "83", "87", "88", "92"),
}
DENOMINATOR_PATHS = {
    "sh880008": Path("vipdoc/sh/lday/sh880008.day"),
}
CHINEXT_INDEX_PATH = Path("vipdoc/sz/lday/sz399006.day")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    market: str
    code: str
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class DenominatorRow:
    date: int
    amount_yuan: float
    source: str


def beijing_now() -> str:
    return datetime.now(timezone(timedelta(hours=8), name="Asia/Shanghai")).isoformat(
        timespec="seconds"
    )


def compact_date_to_iso(value: int) -> str:
    raw = f"{int(value):08d}"
    try:
        return datetime.strptime(raw, "%Y%m%d").date().isoformat()
    except ValueError as exc:
        raise ValueError(f"无效 .day 日期: {value}") from exc


def parse_compact_date(value: str) -> int:
    if re.fullmatch(r"\d{8}", value) is None:
        raise ValueError("日期必须是 YYYYMMDD")
    compact_date_to_iso(int(value))
    return int(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def atomic_write_bytes(payload: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def code_from_day_path(path: Path, market: str) -> str | None:
    stem = path.stem.lower()
    if not stem.startswith(market):
        return None
    code = stem[len(market) :]
    return code if len(code) == 6 and code.isdigit() else None


def snapshot_file(path: Path, market: str, code: str) -> FileSnapshot:
    stat = path.stat()
    return FileSnapshot(
        path=path,
        market=market,
        code=code,
        size=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
    )


def discover_candidate_files(tdx_root: Path) -> list[FileSnapshot]:
    snapshots: list[FileSnapshot] = []
    for market, prefixes in CANDIDATE_PREFIXES.items():
        directory = tdx_root / MARKET_DIRECTORIES[market]
        if not directory.is_dir():
            raise FileNotFoundError(f"缺少 {market} 日线目录: {directory}")
        for path in sorted(directory.glob(f"{market}*.day")):
            code = code_from_day_path(path, market)
            if code is None or not code.startswith(prefixes):
                continue
            snapshots.append(snapshot_file(path, market, code))
    if not snapshots:
        raise ValueError("未找到任何普通 A 股候选 .day 文件")
    return snapshots


def denominator_snapshots(tdx_root: Path) -> dict[str, FileSnapshot]:
    result: dict[str, FileSnapshot] = {}
    for name, relative_path in DENOMINATOR_PATHS.items():
        path = tdx_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"缺少分母日线: {path}")
        market = "sh" if name.startswith("sh") else "sz"
        code = name[2:]
        result[name] = snapshot_file(path, market, code)
    return result


def comparison_index_snapshot(tdx_root: Path) -> FileSnapshot:
    path = tdx_root / CHINEXT_INDEX_PATH
    if not path.is_file():
        raise FileNotFoundError(f"缺少创业板指日线: {path}")
    return snapshot_file(path, "sz", "399006")


def assert_snapshots_unchanged(snapshots: Iterable[FileSnapshot]) -> None:
    changed: list[str] = []
    for snapshot in snapshots:
        try:
            stat = snapshot.path.stat()
        except OSError:
            changed.append(str(snapshot.path))
            continue
        if stat.st_size != snapshot.size or stat.st_mtime_ns != snapshot.mtime_ns:
            changed.append(str(snapshot.path))
    if changed:
        preview = "；".join(changed[:5])
        suffix = " 等" if len(changed) > 5 else ""
        raise RuntimeError(f"计算期间本地日线发生变化，拒绝混合快照输出: {preview}{suffix}")


def read_day_array(path: Path, *, label: str) -> np.ndarray:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise OSError(f"无法读取 {label}: {path}") from exc
    if size == 0:
        raise ValueError(f"{label} 是空文件: {path}")
    if size % DAY_RECORD_BYTES != 0:
        raise ValueError(f"{label} 长度不是 {DAY_RECORD_BYTES} 字节记录的整数倍: {path}")
    return np.fromfile(path, dtype=DAY_DTYPE)


def amount_by_date(records: np.ndarray, *, label: str) -> dict[int, float]:
    result: dict[int, float] = {}
    for raw_date, raw_amount in zip(records["date"], records["amount"], strict=True):
        date = int(raw_date)
        compact_date_to_iso(date)
        if date in result:
            raise ValueError(f"{label} 出现重复交易日: {compact_date_to_iso(date)}")
        amount = float(raw_amount)
        if not math.isfinite(amount):
            raise ValueError(f"{label} 出现非有限成交额: {compact_date_to_iso(date)}")
        result[date] = amount
    return result


def close_by_date(records: np.ndarray, *, label: str) -> dict[int, float]:
    """读取指数收盘价；无效点留给调用方按日期呈现为缺口。"""

    result: dict[int, float] = {}
    seen_dates: set[int] = set()
    for raw_date, raw_close in zip(records["date"], records["close"], strict=True):
        date = int(raw_date)
        compact_date_to_iso(date)
        if date in seen_dates:
            raise ValueError(f"{label} 出现重复交易日: {compact_date_to_iso(date)}")
        seen_dates.add(date)
        close = float(raw_close) / 100
        if not math.isfinite(close):
            raise ValueError(f"{label} 出现非有限收盘价: {compact_date_to_iso(date)}")
        if close > 0:
            result[date] = close
    if not result:
        raise ValueError(f"{label} 没有有效收盘价")
    return result


def build_denominator_rows(
    denominator_data: dict[str, dict[int, float]], start_date: int
) -> tuple[list[DenominatorRow], list[dict[str, str]]]:
    full = denominator_data["sh880008"]
    rows: list[DenominatorRow] = []
    omitted: list[dict[str, str]] = []

    for date in sorted(date for date in full if date >= start_date):
        amount = full[date]
        if amount <= 0:
            omitted.append(
                {
                    "date": compact_date_to_iso(date),
                    "reason": "sh880008_not_positive",
                }
            )
            continue
        rows.append(DenominatorRow(date=date, amount_yuan=amount, source="sh880008"))

    rows.sort(key=lambda row: row.date)
    if not rows:
        raise ValueError("分母日历为空")
    if any(left.date >= right.date for left, right in zip(rows, rows[1:])):
        raise ValueError("分母日历日期不严格递增")
    return rows, omitted


def scan_active_amount_matrix(
    candidates: list[FileSnapshot], calendar_dates: np.ndarray
) -> tuple[np.ndarray, list[dict[str, str]]]:
    """把每只候选股票映射到分母日历；矩阵仅在内存中存在。"""

    matrix = np.zeros((calendar_dates.size, len(candidates)), dtype=np.float32)
    skipped: list[dict[str, str]] = []
    calendar_start = int(calendar_dates[0])
    calendar_end = int(calendar_dates[-1])

    for column, snapshot in enumerate(candidates):
        try:
            if snapshot.size == 0:
                raise ValueError("empty_day_file")
            if snapshot.size % DAY_RECORD_BYTES != 0:
                raise ValueError("invalid_day_record_length")
            records = np.fromfile(snapshot.path, dtype=DAY_DTYPE)
        except (OSError, ValueError) as exc:
            skipped.append({"path": str(snapshot.path), "reason": str(exc)})
            continue

        valid = (
            (records["date"] >= calendar_start)
            & (records["date"] <= calendar_end)
            & (records["close"] > 0)
            & (records["amount"] > 0)
            & np.isfinite(records["amount"])
            & (records["volume"] > 0)
        )
        if snapshot.market == "bj":
            valid &= records["date"] >= BEIJING_UNIVERSE_SWITCH_DATE
        if not bool(valid.any()):
            continue

        record_dates = records["date"][valid]
        positions = np.searchsorted(calendar_dates, record_dates)
        matches = positions < calendar_dates.size
        matched_indexes = np.nonzero(matches)[0]
        if matched_indexes.size:
            matches[matched_indexes] &= (
                calendar_dates[positions[matched_indexes]] == record_dates[matched_indexes]
            )
        if not bool(matches.any()):
            continue
        matrix[positions[matches], column] = records["amount"][valid][matches]

    return matrix, skipped


def rounded_yi(amount_yuan: float) -> float:
    # 保留 8 位小数，既满足网页展示精度，也保证极小合成样本可由输出字段反算 C5。
    return round(amount_yuan / 100_000_000, 8)


def build_records(
    denominator_rows: list[DenominatorRow],
    amount_matrix: np.ndarray,
    chinext_close_by_date: dict[int, float],
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    if amount_matrix.shape[0] != len(denominator_rows):
        raise ValueError("分子矩阵和分母日历行数不一致")
    records: list[dict[str, object]] = []
    omitted: list[dict[str, str]] = []

    for row_index, denominator in enumerate(denominator_rows):
        active_amounts = amount_matrix[row_index]
        active_amounts = active_amounts[active_amounts > 0]
        active_stock_count = int(active_amounts.size)
        if active_stock_count == 0:
            omitted.append(
                {"date": compact_date_to_iso(denominator.date), "reason": "no_active_candidate_stock"}
            )
            continue
        top5_stock_count = (active_stock_count + 19) // 20
        top_amount_yuan = float(
            np.partition(active_amounts, active_stock_count - top5_stock_count)[
                active_stock_count - top5_stock_count :
            ].sum(dtype=np.float64)
        )
        c5_pct = 100 * top_amount_yuan / denominator.amount_yuan
        if not math.isfinite(c5_pct) or c5_pct < 0:
            raise ValueError(f"{compact_date_to_iso(denominator.date)} 计算出无效 C5")
        chinext_close = chinext_close_by_date.get(denominator.date)
        records.append(
            {
                "date": compact_date_to_iso(denominator.date),
                "chinext_close": round(chinext_close, 2) if chinext_close is not None else None,
                "c5_pct": round(c5_pct, 6),
                "top5_amount_yi": rounded_yi(top_amount_yuan),
                "market_amount_yi": rounded_yi(denominator.amount_yuan),
                "active_stock_count": active_stock_count,
                "top5_stock_count": top5_stock_count,
                "denominator_source": denominator.source,
                "numerator_scope": (
                    "sh_sz_bj_active_a"
                    if denominator.date >= BEIJING_UNIVERSE_SWITCH_DATE
                    else "sh_sz_active_a"
                ),
            }
        )
    return records, omitted


def records_to_csv_bytes(records: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=[
            "date",
            "chinext_close",
            "c5_pct",
            "top5_amount_yi",
            "market_amount_yi",
            "active_stock_count",
            "top5_stock_count",
            "denominator_source",
            "numerator_scope",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue().encode("utf-8")


def candidate_counts(candidates: Iterable[FileSnapshot]) -> dict[str, int]:
    result = {market: 0 for market in CANDIDATE_PREFIXES}
    for candidate in candidates:
        result[candidate.market] += 1
    return result


def build_payload(records: list[dict[str, object]], generated_at: str) -> dict[str, object]:
    return {
        "schema_version": "1",
        "generated_at_beijing": generated_at,
        "records": records,
        "provenance": {
            "evidence_level": "market_data_vendor",
            "source": "通达信本地盘后 .day 日线",
            "metric_name": "通达信全A等权 AMOUNT 口径 C5",
            "definition": "C5 = 当日成交活跃普通 A 股中，成交额前 5% 个股成交额之和 / sh880008.day.amount × 100%。",
            "active_stock_rule": "close > 0 且 amount > 0 且 volume > 0；K = ceil(0.05 × N)。",
            "comparison_index": {
                "code": "399006",
                "name": "创业板指",
                "field": "chinext_close",
                "value": "收盘价",
            },
            "raw_data_copied": False,
            "scope_warning": "该曲线以通达信全A等权品种的 AMOUNT 字段为分母，并以通达信厂商日线中的交易活跃 A 股为分子代理；不等同于官方逐日全市场成分清单。未设置覆盖率门槛，也不插值。",
        },
    }


def build_manifest(
    *,
    records: list[dict[str, object]],
    generated_at: str,
    tdx_root: Path,
    candidates: list[FileSnapshot],
    denominator_files: dict[str, FileSnapshot],
    comparison_index_file: FileSnapshot,
    comparison_index_close_by_date: dict[int, float],
    skipped_candidate_files: list[dict[str, str]],
    omitted_dates: list[dict[str, str]],
) -> dict[str, object]:
    candidate_file_count = candidate_counts(candidates)
    denominator_inputs = {
        name: {
            "path": str(snapshot.path),
            "bytes": snapshot.size,
            "sha256": sha256_file(snapshot.path),
            "last_write_time_utc": datetime.fromtimestamp(
                snapshot.mtime_ns / 1_000_000_000, tz=timezone.utc
            ).isoformat(timespec="seconds"),
        }
        for name, snapshot in denominator_files.items()
    }
    comparison_index_dates = sorted(comparison_index_close_by_date)
    comparison_index_input = {
        "code": "399006",
        "name": "创业板指",
        "field": "chinext_close",
        "value": "收盘价",
        "price_scale": "close / 100",
        "source": "通达信本地盘后 .day 日线",
        "path": str(comparison_index_file.path),
        "bytes": comparison_index_file.size,
        "sha256": sha256_file(comparison_index_file.path),
        "last_write_time_utc": datetime.fromtimestamp(
            comparison_index_file.mtime_ns / 1_000_000_000, tz=timezone.utc
        ).isoformat(timespec="seconds"),
        "data_range": {
            "start": compact_date_to_iso(comparison_index_dates[0]),
            "end": compact_date_to_iso(comparison_index_dates[-1]),
        },
        "missing_output_records": sum(
            record.get("chinext_close") is None for record in records
        ),
    }
    return {
        "schema_version": "1",
        "generated_at_beijing": generated_at,
        "payload_sha256": None,
        "csv_sha256": None,
        "payload_records": len(records),
        "data_range": {
            "start": records[0]["date"] if records else None,
            "end": records[-1]["date"] if records else None,
        },
        "evidence_level": "market_data_vendor",
        "source": "通达信本地盘后 .day 日线",
        "raw_data_copied": False,
        "source_paths": {
            "tdx_root": str(tdx_root),
            "sh_l_day": str(tdx_root / MARKET_DIRECTORIES["sh"]),
            "sz_l_day": str(tdx_root / MARKET_DIRECTORIES["sz"]),
            "bj_l_day": str(tdx_root / MARKET_DIRECTORIES["bj"]),
        },
        "denominator_inputs": denominator_inputs,
        "comparison_index_input": comparison_index_input,
        "denominator_segments": [
            {
                "start": compact_date_to_iso(START_DATE),
                "end": records[-1]["date"] if records else None,
                "source": "sh880008",
                "formula": "sh880008.day.amount",
            },
        ],
        "numerator_segments": [
            {
                "start": compact_date_to_iso(START_DATE),
                "end": "2022-08-01",
                "scope": "sh_sz_active_a",
            },
            {
                "start": "2022-08-02",
                "end": records[-1]["date"] if records else None,
                "scope": "sh_sz_bj_active_a",
            },
        ],
        "candidate_prefix_rules": {
            market: list(prefixes) for market, prefixes in CANDIDATE_PREFIXES.items()
        },
        "candidate_file_count": candidate_file_count,
        "candidate_file_count_total": len(candidates),
        "candidate_total_bytes": sum(candidate.size for candidate in candidates),
        "skipped_candidate_files": skipped_candidate_files,
        "omitted_dates": omitted_dates,
        "scope_warning": "分母全期间使用 sh880008.day.amount；分子于 2022-08-02 起纳入北交所候选股。sh880008 的历史成分与纳入规则未作为本包的官方逐日成分清单使用。该包不设 coverage_ratio 门槛，也不插值。",
    }


def _strict_iso_date(value: object, label: str) -> str:
    if not isinstance(value, str) or DATE_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{label} 不是 YYYY-MM-DD")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"{label} 不是有效日期") from exc
    return value


def verify_artifact_bundle(payload_path: Path, manifest_path: Path, csv_path: Path) -> dict[str, object]:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(manifest, dict):
        raise ValueError("发布包 JSON 根节点必须为对象")
    if payload.get("schema_version") != "1" or manifest.get("schema_version") != "1":
        raise ValueError("发布包 schema_version 不受支持")
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("payload provenance 必须为对象")
    comparison_index = provenance.get("comparison_index")
    if not isinstance(comparison_index, dict):
        raise ValueError("payload 缺少创业板指说明")
    if (
        comparison_index.get("code") != "399006"
        or comparison_index.get("field") != "chinext_close"
        or comparison_index.get("value") != "收盘价"
    ):
        raise ValueError("payload 创业板指字段说明不一致")
    if manifest.get("payload_sha256") != sha256_file(payload_path):
        raise ValueError("payload SHA-256 自检失败")
    if manifest.get("csv_sha256") != sha256_file(csv_path):
        raise ValueError("CSV SHA-256 自检失败")
    records = payload.get("records")
    if not isinstance(records, list) or manifest.get("payload_records") != len(records):
        raise ValueError("payload_records 自检失败")
    previous_date: str | None = None
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"records[{index}] 不是对象")
        date = _strict_iso_date(record.get("date"), f"records[{index}].date")
        if previous_date is not None and date <= previous_date:
            raise ValueError("records 日期必须严格递增")
        previous_date = date
        active_count = record.get("active_stock_count")
        top_count = record.get("top5_stock_count")
        if not isinstance(active_count, int) or active_count <= 0:
            raise ValueError("active_stock_count 必须是正整数")
        if top_count != (active_count + 19) // 20:
            raise ValueError("top5_stock_count 必须为 ceil(5% × active_stock_count)")
        values = (record.get("c5_pct"), record.get("top5_amount_yi"), record.get("market_amount_yi"))
        if not all(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0 for value in values):
            raise ValueError("C5 和成交额字段必须是非负有限数")
        if float(record["market_amount_yi"]) <= 0:
            raise ValueError("market_amount_yi 必须为正")
        if "chinext_close" not in record:
            raise ValueError("chinext_close 字段缺失")
        chinext_close = record["chinext_close"]
        if chinext_close is not None and (
            not isinstance(chinext_close, (int, float))
            or not math.isfinite(chinext_close)
            or float(chinext_close) <= 0
        ):
            raise ValueError("chinext_close 必须为 null 或正有限数")
        recomputed = 100 * float(record["top5_amount_yi"]) / float(record["market_amount_yi"])
        if abs(recomputed - float(record["c5_pct"])) > 0.0002:
            raise ValueError("C5 与成交额字段不一致")
        if record.get("denominator_source") != "sh880008":
            raise ValueError("分母来源不一致")
        expected_scope = "sh_sz_active_a" if date < "2022-08-02" else "sh_sz_bj_active_a"
        if record.get("numerator_scope") != expected_scope:
            raise ValueError("分子分段不一致")
    expected_range = {
        "start": records[0]["date"] if records else None,
        "end": records[-1]["date"] if records else None,
    }
    if manifest.get("data_range") != expected_range:
        raise ValueError("manifest data_range 不一致")
    if manifest.get("raw_data_copied") is not False:
        raise ValueError("manifest 必须明确 raw_data_copied=false")
    comparison_index = manifest.get("comparison_index_input")
    if not isinstance(comparison_index, dict):
        raise ValueError("manifest 缺少创业板指输入说明")
    if comparison_index.get("code") != "399006" or comparison_index.get("field") != "chinext_close":
        raise ValueError("manifest 创业板指字段说明不一致")
    if comparison_index.get("source") != "通达信本地盘后 .day 日线":
        raise ValueError("manifest 创业板指来源说明不一致")
    missing_chinext = sum(record.get("chinext_close") is None for record in records)
    if comparison_index.get("missing_output_records") != missing_chinext:
        raise ValueError("manifest 创业板指缺口统计不一致")
    return manifest


def write_bundle(
    output_directory: Path,
    payload: dict[str, object],
    manifest: dict[str, object],
    records: list[dict[str, object]],
) -> tuple[Path, Path, Path]:
    payload_path = output_directory / PAYLOAD_FILENAME
    manifest_path = output_directory / MANIFEST_FILENAME
    csv_path = output_directory / CSV_FILENAME
    atomic_write_bytes(json_bytes(payload), payload_path)
    atomic_write_bytes(records_to_csv_bytes(records), csv_path)
    completed_manifest = dict(manifest)
    completed_manifest["payload_sha256"] = sha256_file(payload_path)
    completed_manifest["csv_sha256"] = sha256_file(csv_path)
    atomic_write_bytes(json_bytes(completed_manifest), manifest_path)
    verify_artifact_bundle(payload_path, manifest_path, csv_path)
    return payload_path, manifest_path, csv_path


def read_published_snapshot(payload_target: Path, manifest_target: Path) -> tuple[bytes, bytes] | None:
    payload_exists = payload_target.exists()
    manifest_exists = manifest_target.exists()
    if payload_exists != manifest_exists:
        raise ValueError("发布目录已有不完整 JSON 对，拒绝覆盖")
    if not payload_exists:
        return None
    return payload_target.read_bytes(), manifest_target.read_bytes()


def restore_published_snapshot(
    snapshot: tuple[bytes, bytes] | None, payload_target: Path, manifest_target: Path
) -> None:
    if snapshot is None:
        for target in (payload_target, manifest_target):
            if target.exists():
                target.unlink()
        return
    atomic_write_bytes(snapshot[0], payload_target)
    atomic_write_bytes(snapshot[1], manifest_target)


def publish_bundle_atomically(payload_path: Path, manifest_path: Path, publish_directory: Path) -> None:
    if publish_directory.resolve() != PUBLISH_DIRECTORY.resolve():
        raise ValueError(f"publish-dir 必须是已授权静态数据目录: {PUBLISH_DIRECTORY}")
    artifact_csv = payload_path.parent / CSV_FILENAME
    verify_artifact_bundle(payload_path, manifest_path, artifact_csv)
    payload_target = publish_directory / payload_path.name
    manifest_target = publish_directory / manifest_path.name
    snapshot = read_published_snapshot(payload_target, manifest_target)
    try:
        # manifest 是提交标记：旧 manifest 会拒绝读取新 payload，直到新 manifest 到位。
        atomic_write_bytes(payload_path.read_bytes(), payload_target)
        atomic_write_bytes(manifest_path.read_bytes(), manifest_target)
        if sha256_file(payload_target) != sha256_file(payload_path):
            raise ValueError("发布后 payload SHA-256 不一致")
        if sha256_file(manifest_target) != sha256_file(manifest_path):
            raise ValueError("发布后 manifest SHA-256 不一致")
    except Exception:
        restore_published_snapshot(snapshot, payload_target, manifest_target)
        raise


def resolve_project_root(value: str | None) -> Path:
    root = Path(value).resolve() if value else Path(__file__).resolve().parents[1]
    if not (root / "AGENTS.md").is_file():
        raise FileNotFoundError(f"无法确认产业链投研项目根目录: {root}")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="构建通达信全A等权 AMOUNT 口径 C5 交易集中度发布包")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--tdx-root", default=r"D:\HT")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--publish-dir", default=None)
    parser.add_argument("--start-date", default=str(START_DATE), help="YYYYMMDD，默认 20130101")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    tdx_root = Path(args.tdx_root).resolve()
    start_date = parse_compact_date(args.start_date)
    output_directory = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else (project_root / DEFAULT_OUTPUT_DIRECTORY).resolve()
    )

    candidates = discover_candidate_files(tdx_root)
    denominator_files = denominator_snapshots(tdx_root)
    comparison_index_file = comparison_index_snapshot(tdx_root)
    denominator_data = {
        name: amount_by_date(read_day_array(snapshot.path, label=name), label=name)
        for name, snapshot in denominator_files.items()
    }
    chinext_close_by_date = close_by_date(
        read_day_array(comparison_index_file.path, label="sz399006"), label="sz399006"
    )
    denominator_rows, denominator_omitted = build_denominator_rows(denominator_data, start_date)
    calendar_dates = np.asarray([row.date for row in denominator_rows], dtype=np.uint32)
    amount_matrix, skipped_candidate_files = scan_active_amount_matrix(candidates, calendar_dates)
    records, numerator_omitted = build_records(
        denominator_rows, amount_matrix, chinext_close_by_date
    )
    del amount_matrix

    # 拒绝用 TDX 刷新中的混合快照生成产物；不复制任何原始文件。
    assert_snapshots_unchanged(
        [*candidates, *denominator_files.values(), comparison_index_file]
    )
    generated_at = beijing_now()
    payload = build_payload(records, generated_at)
    manifest = build_manifest(
        records=records,
        generated_at=generated_at,
        tdx_root=tdx_root,
        candidates=candidates,
        denominator_files=denominator_files,
        comparison_index_file=comparison_index_file,
        comparison_index_close_by_date=chinext_close_by_date,
        skipped_candidate_files=skipped_candidate_files,
        omitted_dates=[*denominator_omitted, *numerator_omitted],
    )
    payload_path, manifest_path, csv_path = write_bundle(output_directory, payload, manifest, records)
    if args.publish_dir:
        publish_bundle_atomically(payload_path, manifest_path, Path(args.publish_dir).resolve())
    verified_manifest = verify_artifact_bundle(payload_path, manifest_path, csv_path)
    print(
        json.dumps(
            {
                "payload": str(payload_path),
                "manifest": str(manifest_path),
                "csv": str(csv_path),
                "records": verified_manifest["payload_records"],
                "data_range": verified_manifest["data_range"],
                "published": bool(args.publish_dir),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
