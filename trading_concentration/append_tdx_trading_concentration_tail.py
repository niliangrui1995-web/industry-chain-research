"""仅追加通达信 C5 交易集中度的新分母日期。

该入口只读取已发布加工包和严格晚于 ``append_checkpoint`` 的 .day 尾部记录。
它不会重新扫描、计算或回填既有个股历史；首次建库或人工历史修订仍使用
``build_tdx_trading_concentration.py``。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

import build_tdx_trading_concentration as builder


DATE_PREFIX = struct.Struct("<I")


@dataclass(frozen=True)
class TailRead:
    records: np.ndarray
    tail_bytes: int
    latest_date: int | None


def iso_to_compact(value: object, *, label: str) -> int:
    if not isinstance(value, str):
        raise ValueError(f"{label} 必须是 YYYY-MM-DD")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{label} 必须是有效 YYYY-MM-DD") from exc
    return int(parsed.strftime("%Y%m%d"))


def file_record_count(path: Path, *, label: str) -> int:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise OSError(f"无法读取 {label}: {path}") from exc
    if size == 0:
        raise ValueError(f"{label} 是空文件: {path}")
    if size % builder.DAY_RECORD_BYTES != 0:
        raise ValueError(
            f"{label} 长度不是 {builder.DAY_RECORD_BYTES} 字节记录的整数倍: {path}"
        )
    return size // builder.DAY_RECORD_BYTES


def read_tail_day_records(path: Path, *, after_date: int, label: str) -> TailRead:
    """二分定位并仅载入严格晚于 ``after_date`` 的定长 .day 尾部。"""

    record_count = file_record_count(path, label=label)
    with path.open("rb") as handle:
        def date_at(index: int) -> int:
            handle.seek(index * builder.DAY_RECORD_BYTES)
            raw = handle.read(DATE_PREFIX.size)
            if len(raw) != DATE_PREFIX.size:
                raise ValueError(f"{label} 读取记录日期失败: index={index}")
            date = int(DATE_PREFIX.unpack(raw)[0])
            builder.compact_date_to_iso(date)
            return date

        latest_date = date_at(record_count - 1)
        if latest_date <= after_date:
            return TailRead(
                records=np.empty(0, dtype=builder.DAY_DTYPE), tail_bytes=0, latest_date=latest_date
            )

        low = 0
        high = record_count
        while low < high:
            middle = (low + high) // 2
            if date_at(middle) <= after_date:
                low = middle + 1
            else:
                high = middle

        if low == record_count:
            raise ValueError(f"{label} 二分尾部定位异常")
        if low > 0 and date_at(low - 1) > after_date:
            raise ValueError(f"{label} 日期未按升序排列，拒绝尾部追加")
        if date_at(low) <= after_date:
            raise ValueError(f"{label} 日期未按升序排列，拒绝尾部追加")

        handle.seek(low * builder.DAY_RECORD_BYTES)
        tail_blob = handle.read()

    records = np.frombuffer(tail_blob, dtype=builder.DAY_DTYPE).copy()
    previous_date = after_date
    for raw_date in records["date"]:
        date = int(raw_date)
        builder.compact_date_to_iso(date)
        if date <= previous_date:
            raise ValueError(f"{label} 尾部日期未严格递增或重复: {date}")
        previous_date = date
    return TailRead(records=records, tail_bytes=len(tail_blob), latest_date=latest_date)


def tail_close_by_date(records: np.ndarray, *, label: str) -> dict[int, float]:
    """尾部创业板指缺失保留为空，不因尾段全部无效而中断追加。"""

    result: dict[int, float] = {}
    for raw_date, raw_close in zip(records["date"], records["close"], strict=True):
        date = int(raw_date)
        builder.compact_date_to_iso(date)
        close = float(raw_close) / 100
        if not math.isfinite(close):
            raise ValueError(f"{label} 出现非有限收盘价: {builder.compact_date_to_iso(date)}")
        if close > 0:
            result[date] = close
    return result


def build_tail_denominator_rows(
    denominator_amount_by_date: dict[int, float], *, after_date: int
) -> tuple[list[builder.DenominatorRow], list[dict[str, str]]]:
    rows: list[builder.DenominatorRow] = []
    omitted: list[dict[str, str]] = []
    for date in sorted(denominator_amount_by_date):
        if date <= after_date:
            raise ValueError("尾部分母包含已处理日期")
        amount = denominator_amount_by_date[date]
        if amount <= 0:
            omitted.append(
                {"date": builder.compact_date_to_iso(date), "reason": "sh880008_not_positive"}
            )
            continue
        rows.append(
            builder.DenominatorRow(date=date, amount_yuan=amount, source="sh880008")
        )
    return rows, omitted


def scan_tail_active_amount_matrix(
    candidates: list[builder.FileSnapshot], *, calendar_dates: np.ndarray, after_date: int
) -> tuple[np.ndarray, list[dict[str, str]], dict[str, int]]:
    """只读取每只候选 .day 二分定位后的尾部，绝不读取历史矩阵。"""

    matrix = np.zeros((calendar_dates.size, len(candidates)), dtype=np.float32)
    skipped: list[dict[str, str]] = []
    stats = {
        "candidate_files_examined": 0,
        "candidate_files_with_tail_records": 0,
        "candidate_tail_records_scanned": 0,
        "candidate_tail_bytes_scanned": 0,
    }

    for column, snapshot in enumerate(candidates):
        stats["candidate_files_examined"] += 1
        try:
            tail = read_tail_day_records(
                snapshot.path,
                after_date=after_date,
                label=f"{snapshot.market}{snapshot.code}",
            )
        except (OSError, ValueError) as exc:
            skipped.append({"path": str(snapshot.path), "reason": str(exc)})
            continue

        stats["candidate_tail_bytes_scanned"] += tail.tail_bytes
        stats["candidate_tail_records_scanned"] += int(tail.records.size)
        if tail.records.size == 0:
            continue
        stats["candidate_files_with_tail_records"] += 1

        valid = (
            (tail.records["close"] > 0)
            & (tail.records["amount"] > 0)
            & np.isfinite(tail.records["amount"])
            & (tail.records["volume"] > 0)
        )
        if snapshot.market == "bj":
            valid &= tail.records["date"] >= builder.BEIJING_UNIVERSE_SWITCH_DATE
        if not bool(valid.any()):
            continue

        record_dates = tail.records["date"][valid]
        positions = np.searchsorted(calendar_dates, record_dates)
        matches = positions < calendar_dates.size
        matched_indexes = np.nonzero(matches)[0]
        if matched_indexes.size:
            matches[matched_indexes] &= (
                calendar_dates[positions[matched_indexes]] == record_dates[matched_indexes]
            )
        if bool(matches.any()):
            matrix[positions[matches], column] = tail.records["amount"][valid][matches]

    return matrix, skipped, stats


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} 根节点必须是对象")
    return value


def _validate_omitted_dates(value: object, *, watermark: int) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("manifest omitted_dates 必须是数组")
    result: list[dict[str, str]] = []
    seen_dates: set[str] = set()
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise ValueError(f"omitted_dates[{index}] 必须是对象")
        date = entry.get("date")
        reason = entry.get("reason")
        compact_date = iso_to_compact(date, label=f"omitted_dates[{index}].date")
        if compact_date > watermark:
            raise ValueError("omitted_dates 超出已处理水位")
        if not isinstance(reason, str) or not reason:
            raise ValueError(f"omitted_dates[{index}].reason 无效")
        if date in seen_dates:
            raise ValueError("omitted_dates 日期不能重复")
        seen_dates.add(date)
        result.append({"date": date, "reason": reason})
    return result


def read_baseline_bundle(output_directory: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], int, list[dict[str, str]]]:
    payload_path = output_directory / builder.PAYLOAD_FILENAME
    manifest_path = output_directory / builder.MANIFEST_FILENAME
    csv_path = output_directory / builder.CSV_FILENAME
    builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)
    payload = _read_json(payload_path, label="既有 payload")
    manifest = _read_json(manifest_path, label="既有 manifest")
    records = payload.get("records")
    if not isinstance(records, list) or not records or not all(isinstance(row, dict) for row in records):
        raise ValueError("既有 payload records 无效")
    if builder.records_to_csv_bytes(records) != csv_path.read_bytes():
        raise ValueError("既有 CSV 与 payload records 不一致，拒绝在损坏基线上追加")

    record_end = iso_to_compact(records[-1].get("date"), label="既有 records 末日")
    segments = manifest.get("denominator_segments")
    expected_end = records[-1]["date"]
    if (
        not isinstance(segments, list)
        or len(segments) != 1
        or not isinstance(segments[0], dict)
        or segments[0].get("source") != "sh880008"
        or segments[0].get("formula") != "sh880008.day.amount"
        or segments[0].get("end") != expected_end
    ):
        raise ValueError("既有 manifest 不是统一 sh880008 分母包")

    checkpoint = manifest.get("append_checkpoint")
    if checkpoint is None:
        watermark = record_end
    else:
        if not isinstance(checkpoint, dict) or checkpoint.get("mode") != "append_only":
            raise ValueError("append_checkpoint 无效")
        watermark = iso_to_compact(
            checkpoint.get("last_denominator_date"), label="append_checkpoint.last_denominator_date"
        )
        if watermark < record_end:
            raise ValueError("append_checkpoint 不能早于已发布 records 末日")
    omitted_dates = _validate_omitted_dates(manifest.get("omitted_dates"), watermark=watermark)
    return payload, manifest, records, watermark, omitted_dates


def _snapshot_stat(snapshot: builder.FileSnapshot, tail: TailRead) -> dict[str, object]:
    return {
        "path": str(snapshot.path),
        "source_file_bytes": snapshot.size,
        "source_file_last_write_time_utc": datetime.fromtimestamp(
            snapshot.mtime_ns / 1_000_000_000, tz=timezone.utc
        ).isoformat(timespec="seconds"),
        "tail_record_count": int(tail.records.size),
        "tail_bytes_scanned": tail.tail_bytes,
        "tail_sha256": hashlib.sha256(tail.records.tobytes()).hexdigest(),
    }


def build_append_manifest(
    *,
    baseline: dict[str, Any],
    records: list[dict[str, Any]],
    candidates: list[builder.FileSnapshot],
    denominator_file: builder.FileSnapshot,
    denominator_tail: TailRead,
    comparison_index_file: builder.FileSnapshot,
    comparison_index_tail: TailRead,
    previous_watermark: int,
    processed_through: int,
    skipped_tail_candidates: list[dict[str, str]],
    omitted_dates: list[dict[str, str]],
    candidate_tail_stats: dict[str, int],
) -> dict[str, Any]:
    manifest = json.loads(json.dumps(baseline, ensure_ascii=False))
    record_end = records[-1]["date"]
    existing_skipped = manifest.get("skipped_candidate_files")
    if not isinstance(existing_skipped, list):
        raise ValueError("既有 skipped_candidate_files 必须是数组")
    combined_skipped = [*existing_skipped]
    known_skips = {
        (entry.get("path"), entry.get("reason"))
        for entry in combined_skipped
        if isinstance(entry, dict)
    }
    for entry in skipped_tail_candidates:
        identity = (entry["path"], entry["reason"])
        if identity not in known_skips:
            combined_skipped.append(entry)
            known_skips.add(identity)

    manifest["generated_at_beijing"] = builder.beijing_now()
    manifest["payload_sha256"] = None
    manifest["csv_sha256"] = None
    manifest["payload_records"] = len(records)
    manifest["data_range"] = {"start": records[0]["date"], "end": record_end}
    manifest["denominator_segments"] = [
        {
            "start": builder.compact_date_to_iso(builder.START_DATE),
            "end": record_end,
            "source": "sh880008",
            "formula": "sh880008.day.amount",
        }
    ]
    manifest["numerator_segments"] = [
        {"start": builder.compact_date_to_iso(builder.START_DATE), "end": "2022-08-01", "scope": "sh_sz_active_a"},
        {"start": "2022-08-02", "end": record_end, "scope": "sh_sz_bj_active_a"},
    ]
    manifest["candidate_file_count"] = builder.candidate_counts(candidates)
    manifest["candidate_file_count_total"] = len(candidates)
    manifest["candidate_total_bytes"] = sum(candidate.size for candidate in candidates)
    manifest["skipped_candidate_files"] = combined_skipped
    manifest["omitted_dates"] = omitted_dates

    comparison_index_input = manifest.get("comparison_index_input")
    if not isinstance(comparison_index_input, dict):
        raise ValueError("既有 manifest 缺少 comparison_index_input")
    comparison_index_input["missing_output_records"] = sum(
        record.get("chinext_close") is None for record in records
    )

    manifest["append_checkpoint"] = {
        "mode": "append_only",
        "last_denominator_date": builder.compact_date_to_iso(processed_through),
        "last_append": {
            "previous_last_denominator_date": builder.compact_date_to_iso(previous_watermark),
            "processed_source_date_start": builder.compact_date_to_iso(
                int(denominator_tail.records["date"][0])
            ),
            "processed_source_date_end": builder.compact_date_to_iso(processed_through),
            "records_added": len(records) - int(baseline["payload_records"]),
            "omitted_dates_added": len(omitted_dates) - len(baseline["omitted_dates"]),
            "denominator_tail_input": _snapshot_stat(denominator_file, denominator_tail),
            "comparison_index_tail_input": _snapshot_stat(
                comparison_index_file, comparison_index_tail
            ),
            **candidate_tail_stats,
        },
    }
    return manifest


def run_append(
    *,
    project_root: Path,
    tdx_root: Path,
    output_directory: Path,
    publish_directory: Path | None,
) -> dict[str, object]:
    del project_root  # 已由 CLI 校验；输出目录可在测试中独立指定。
    payload, baseline_manifest, previous_records, watermark, existing_omitted = read_baseline_bundle(
        output_directory
    )
    denominator_files = builder.denominator_snapshots(tdx_root)
    denominator_file = denominator_files["sh880008"]
    denominator_tail = read_tail_day_records(
        denominator_file.path, after_date=watermark, label="sh880008"
    )
    local_latest_date = (
        builder.compact_date_to_iso(denominator_tail.latest_date)
        if denominator_tail.latest_date is not None
        else None
    )
    if denominator_tail.records.size == 0:
        return {
            "status": "no_changes",
            "watermark_date": builder.compact_date_to_iso(watermark),
            "local_latest_date": local_latest_date,
            "records_added": 0,
            "published": False,
        }

    comparison_index_file = builder.comparison_index_snapshot(tdx_root)
    comparison_index_tail = read_tail_day_records(
        comparison_index_file.path, after_date=watermark, label="sz399006"
    )
    denominator_amounts = builder.amount_by_date(denominator_tail.records, label="sh880008")
    denominator_rows, denominator_omitted = build_tail_denominator_rows(
        denominator_amounts, after_date=watermark
    )
    calendar_dates = np.asarray([row.date for row in denominator_rows], dtype=np.uint32)
    candidates = builder.discover_candidate_files(tdx_root)
    if calendar_dates.size:
        amount_matrix, skipped_tail_candidates, candidate_tail_stats = scan_tail_active_amount_matrix(
            candidates, calendar_dates=calendar_dates, after_date=watermark
        )
        tail_records, numerator_omitted = builder.build_records(
            denominator_rows,
            amount_matrix,
            tail_close_by_date(comparison_index_tail.records, label="sz399006"),
        )
        del amount_matrix
    else:
        skipped_tail_candidates = []
        candidate_tail_stats = {
            "candidate_files_examined": 0,
            "candidate_files_with_tail_records": 0,
            "candidate_tail_records_scanned": 0,
            "candidate_tail_bytes_scanned": 0,
        }
        tail_records = []
        numerator_omitted = []

    processed_through = max(denominator_amounts)
    records = [*previous_records, *tail_records]
    omitted_dates = [*existing_omitted, *denominator_omitted, *numerator_omitted]
    _validate_omitted_dates(omitted_dates, watermark=processed_through)
    payload["generated_at_beijing"] = builder.beijing_now()
    payload["records"] = records
    manifest = build_append_manifest(
        baseline=baseline_manifest,
        records=records,
        candidates=candidates,
        denominator_file=denominator_file,
        denominator_tail=denominator_tail,
        comparison_index_file=comparison_index_file,
        comparison_index_tail=comparison_index_tail,
        previous_watermark=watermark,
        processed_through=processed_through,
        skipped_tail_candidates=skipped_tail_candidates,
        omitted_dates=omitted_dates,
        candidate_tail_stats=candidate_tail_stats,
    )

    builder.assert_snapshots_unchanged(
        [*candidates, *denominator_files.values(), comparison_index_file]
    )
    payload_path, manifest_path, csv_path = builder.write_bundle(
        output_directory, payload, manifest, records
    )
    if publish_directory is not None:
        builder.publish_bundle_atomically(payload_path, manifest_path, publish_directory)
    verified_manifest = builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)
    return {
        "status": "updated",
        "watermark_date": builder.compact_date_to_iso(watermark),
        "local_latest_date": local_latest_date,
        "processed_source_date_range": {
            "start": builder.compact_date_to_iso(int(denominator_tail.records["date"][0])),
            "end": builder.compact_date_to_iso(processed_through),
        },
        "records_added": len(tail_records),
        "omitted_dates_added": len(omitted_dates) - len(existing_omitted),
        "records": verified_manifest["payload_records"],
        "data_range": verified_manifest["data_range"],
        "payload": str(payload_path),
        "manifest": str(manifest_path),
        "csv": str(csv_path),
        "published": publish_directory is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="仅追加通达信 C5 交易集中度的新交易日")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--tdx-root", default=r"D:\\HT")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--publish-dir", default=None)
    args = parser.parse_args()

    project_root = builder.resolve_project_root(args.project_root)
    tdx_root = Path(args.tdx_root).resolve()
    output_directory = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else (project_root / builder.DEFAULT_OUTPUT_DIRECTORY).resolve()
    )
    result = run_append(
        project_root=project_root,
        tdx_root=tdx_root,
        output_directory=output_directory,
        publish_directory=Path(args.publish_dir).resolve() if args.publish_dir else None,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
