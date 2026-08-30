"""一次性回填 AI 产业链成交额占比，不重算既有 C5 历史。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import build_tdx_trading_concentration as builder


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} 根节点必须是对象")
    return value


def read_baseline(
    output_directory: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], bytes, dict[str, Any] | None]:
    payload_path = output_directory / builder.PAYLOAD_FILENAME
    manifest_path = output_directory / builder.MANIFEST_FILENAME
    csv_path = output_directory / builder.CSV_FILENAME
    builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)
    payload = _read_json(payload_path, label="既有 payload")
    manifest = _read_json(manifest_path, label="既有 manifest")
    payload_series = payload.get("ai_chain_series")
    manifest_series = manifest.get("ai_chain_series")
    if (payload_series is None) != (manifest_series is None):
        raise ValueError("AI 产业链子序列必须同时存在于 payload 与 manifest")
    if payload_series is not None and not isinstance(payload_series, dict):
        raise ValueError("既有 AI 产业链子序列无效")
    records = payload.get("records")
    if not isinstance(records, list) or not records or not all(isinstance(record, dict) for record in records):
        raise ValueError("既有 C5 records 无效")
    csv_bytes = csv_path.read_bytes()
    if builder.records_to_csv_bytes(records) != csv_bytes:
        raise ValueError("既有 CSV 与 C5 records 不一致，拒绝回填")
    return payload, manifest, records, csv_bytes, payload_series


def denominator_rows_for_existing_records(
    records: list[dict[str, Any]], denominator_amount_by_date: dict[int, float]
) -> list[builder.DenominatorRow]:
    rows: list[builder.DenominatorRow] = []
    for record in records:
        date = record.get("date")
        if not isinstance(date, str) or date < builder.compact_date_to_iso(builder.AI_CHAIN_START_DATE):
            continue
        compact_date = builder.parse_compact_date(date.replace("-", ""))
        amount_yuan = denominator_amount_by_date.get(compact_date)
        if amount_yuan is None or amount_yuan <= 0:
            raise ValueError(f"AI 回填日期缺少正分母: {date}")
        market_amount_yi = record.get("market_amount_yi")
        if not isinstance(market_amount_yi, (int, float)) or abs(
            float(market_amount_yi) - builder.rounded_yi(amount_yuan)
        ) > 0.00000001:
            raise ValueError(f"既有 C5 与当前 sh880008 分母不一致: {date}")
        rows.append(builder.DenominatorRow(compact_date, amount_yuan, "sh880008"))
    if not rows:
        raise ValueError("既有 C5 包没有 2025-01-01 及之后的可回填交易日")
    return rows


def run_backfill(
    *,
    project_root: Path,
    tdx_root: Path,
    output_directory: Path,
    publish_directory: Path | None,
) -> dict[str, object]:
    payload, baseline_manifest, baseline_records, baseline_csv_bytes, existing_series = read_baseline(
        output_directory
    )
    candidates = builder.discover_candidate_files(tdx_root)
    universe = builder.load_ai_chain_universe(project_root)
    ai_candidates = builder.ai_chain_candidate_snapshots(universe, candidates)
    denominator_files: dict[str, builder.FileSnapshot] = {}
    if existing_series is None:
        denominator_files = builder.denominator_snapshots(tdx_root)
        denominator_file = denominator_files["sh880008"]
        denominator_amount_by_date = builder.amount_by_date(
            builder.read_day_array(denominator_file.path, label="sh880008"), label="sh880008"
        )
        denominator_rows = denominator_rows_for_existing_records(
            baseline_records, denominator_amount_by_date
        )
        calendar_dates = np.asarray([row.date for row in denominator_rows], dtype=np.uint32)
        ai_amount_matrix, skipped_ai_candidates = builder.scan_active_amount_matrix(
            ai_candidates, calendar_dates
        )
        if skipped_ai_candidates:
            raise ValueError(f"AI 产业链候选日线不可读，拒绝回填: {skipped_ai_candidates[0]}")
        series_records = builder.build_ai_chain_series_records(
            denominator_rows,
            ai_amount_matrix,
            c5_output_dates={row.date for row in denominator_rows},
        )
        if len(series_records) != len(denominator_rows):
            raise ValueError("AI 产业链回填交易日数量不完整")
        status = "backfilled"
    else:
        existing_universe = existing_series.get("universe")
        series_records = existing_series.get("records")
        expected_codes_sha256 = builder.ai_chain_codes_sha256(universe.resolved_codes)
        if (
            not isinstance(existing_universe, dict)
            or existing_universe.get("code_count") != len(universe.resolved_codes)
            or existing_universe.get("codes_sha256") != expected_codes_sha256
            or not isinstance(series_records, list)
            or not all(isinstance(record, dict) for record in series_records)
        ):
            raise ValueError(
                "AI 产业链股票池实际成分已变化；需显式重新回填，拒绝只刷新工作簿元数据"
            )
        status = "universe_metadata_refreshed"
    ai_chain_series = builder.build_ai_chain_series(series_records, universe)
    manifest = json.loads(json.dumps(baseline_manifest, ensure_ascii=False))
    manifest["generated_at_beijing"] = builder.beijing_now()
    manifest["payload_sha256"] = None
    manifest["csv_sha256"] = None
    manifest["ai_chain_series"] = builder.build_ai_chain_manifest(
        series_records, universe, ai_candidates
    )
    payload["generated_at_beijing"] = manifest["generated_at_beijing"]
    payload["ai_chain_series"] = ai_chain_series

    builder.assert_ai_chain_universe_unchanged(universe)
    builder.assert_snapshots_unchanged([*ai_candidates, *denominator_files.values()])
    payload_path, manifest_path, csv_path = builder.write_bundle(
        output_directory, payload, manifest, baseline_records
    )
    if csv_path.read_bytes() != baseline_csv_bytes:
        raise RuntimeError("AI 回填意外改写了既有 C5 CSV")
    reloaded_payload = _read_json(payload_path, label="回填后 payload")
    if reloaded_payload.get("records") != baseline_records:
        raise RuntimeError("AI 回填意外改写了既有 C5 records")
    if publish_directory is not None:
        builder.publish_bundle_atomically(payload_path, manifest_path, publish_directory)
    verified_manifest = builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)
    ai_manifest = verified_manifest["ai_chain_series"]
    return {
        "status": status,
        "c5_records_preserved": True,
        "csv_bytes_preserved": True,
        "ai_chain_records_preserved": existing_series is not None,
        "ai_chain_records": ai_manifest["records"],
        "ai_chain_data_range": ai_manifest["data_range"],
        "ai_chain_missing_output_records": ai_manifest["missing_output_records"],
        "payload": str(payload_path),
        "manifest": str(manifest_path),
        "csv": str(csv_path),
        "published": publish_directory is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="回填 AI 产业链成交额占比或刷新同成分工作簿元数据")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--tdx-root", default=r"D:\HT")
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
    result = run_backfill(
        project_root=project_root,
        tdx_root=tdx_root,
        output_directory=output_directory,
        publish_directory=Path(args.publish_dir).resolve() if args.publish_dir else None,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
