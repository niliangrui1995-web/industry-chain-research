"""按 AI 成员集合选择尾部追加或 AI-only 历史重算的单命令日更入口。

成功时标准输出恰好一行 JSON。成员集合按排序后的证券代码指纹比较，故工作簿
行重排不会触发重算；旧发布包没有该指纹时，保守地执行一次 AI-only 重算。
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

import append_tdx_trading_concentration_tail as appender
import backfill_ai_chain_turnover_share as backfill
import build_tdx_trading_concentration as builder


def _artifact_paths(directory: Path) -> dict[str, Path]:
    return {
        "payload": directory / builder.PAYLOAD_FILENAME,
        "manifest": directory / builder.MANIFEST_FILENAME,
        "csv": directory / builder.CSV_FILENAME,
    }


def _read_bundle_snapshot(directory: Path) -> dict[str, bytes]:
    paths = _artifact_paths(directory)
    try:
        return {name: path.read_bytes() for name, path in paths.items()}
    except OSError as exc:
        raise ValueError(f"无法读取发布包快照: {directory}") from exc


def _restore_bundle_snapshot(directory: Path, snapshot: dict[str, bytes]) -> None:
    paths = _artifact_paths(directory)
    for name in ("payload", "csv", "manifest"):
        builder.atomic_write_bytes(snapshot[name], paths[name])


def _replace_bundle_from_staging(
    staging_directory: Path, output_directory: Path, output_snapshot: dict[str, bytes]
) -> None:
    staging_paths = _artifact_paths(staging_directory)
    output_paths = _artifact_paths(output_directory)
    builder.verify_artifact_bundle(
        staging_paths["payload"], staging_paths["manifest"], staging_paths["csv"]
    )
    try:
        for name in ("payload", "csv", "manifest"):
            builder.atomic_write_bytes(staging_paths[name].read_bytes(), output_paths[name])
        builder.verify_artifact_bundle(
            output_paths["payload"], output_paths["manifest"], output_paths["csv"]
        )
    except Exception:
        _restore_bundle_snapshot(output_directory, output_snapshot)
        raise


def _result_paths_for_output(result: dict[str, object], output_directory: Path) -> dict[str, object]:
    return {
        **result,
        "payload": str(output_directory / builder.PAYLOAD_FILENAME),
        "manifest": str(output_directory / builder.MANIFEST_FILENAME),
        "csv": str(output_directory / builder.CSV_FILENAME),
    }


def _validate_publish_directory(publish_directory: Path | None) -> None:
    if publish_directory is not None and publish_directory.resolve() != builder.PUBLISH_DIRECTORY.resolve():
        raise ValueError(f"publish-dir 必须是已授权静态数据目录: {builder.PUBLISH_DIRECTORY}")


def run_daily_refresh(
    *,
    project_root: Path,
    tdx_root: Path,
    output_directory: Path,
    publish_directory: Path | None,
) -> dict[str, object]:
    """更新 C5 与 AI 子序列；成员变化时仅重算 AI 的既有日历。"""

    _validate_publish_directory(publish_directory)
    (
        payload,
        manifest,
        _baseline_records,
        _baseline_csv_bytes,
        payload_series,
        manifest_series,
    ) = backfill.read_baseline(output_directory)
    del payload, manifest
    universe = builder.load_ai_chain_universe(project_root)
    membership = backfill.ai_chain_membership_status(
        payload_series, manifest_series, universe
    )
    output_snapshot = _read_bundle_snapshot(output_directory)

    with tempfile.TemporaryDirectory(
        prefix=".tmp_tdx_trading_concentration_refresh-", dir=output_directory.parent
    ) as temporary:
        staging_directory = Path(temporary)
        for name, path in _artifact_paths(output_directory).items():
            shutil.copy2(path, _artifact_paths(staging_directory)[name])

        if membership["status"] == "matched":
            append_result = appender.run_append(
                project_root=project_root,
                tdx_root=tdx_root,
                output_directory=staging_directory,
                publish_directory=None,
            )
            if append_result["status"] == "no_changes":
                return {
                    "status": "no_changes",
                    "ai_chain_action": "append",
                    "ai_chain_membership": membership,
                    "rebuild": None,
                    "append": _result_paths_for_output(append_result, output_directory),
                    "published": False,
                }
            rebuild_result = None
            status = append_result["status"]
            ai_chain_action = "append"
        else:
            rebuild_result = backfill.run_backfill(
                project_root=project_root,
                tdx_root=tdx_root,
                output_directory=staging_directory,
                publish_directory=None,
                rebuild_on_universe_change=True,
            )
            append_result = appender.run_append(
                project_root=project_root,
                tdx_root=tdx_root,
                output_directory=staging_directory,
                publish_directory=None,
            )
            status = "updated" if append_result["status"] == "updated" else "ai_chain_rebuilt"
            ai_chain_action = "rebuild_then_append"

        try:
            _replace_bundle_from_staging(staging_directory, output_directory, output_snapshot)
            if publish_directory is not None:
                output_paths = _artifact_paths(output_directory)
                builder.publish_bundle_atomically(
                    output_paths["payload"], output_paths["manifest"], publish_directory
                )
        except Exception:
            _restore_bundle_snapshot(output_directory, output_snapshot)
            raise
    return {
        "status": status,
        "ai_chain_action": ai_chain_action,
        "ai_chain_membership": membership,
        "rebuild": (
            _result_paths_for_output(rebuild_result, output_directory)
            if rebuild_result is not None
            else None
        ),
        "append": _result_paths_for_output(append_result, output_directory),
        "published": publish_directory is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="日更 C5 与 AI 产业链成交拥挤度")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--tdx-root", default=r"D:\HT")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--publish-dir", default=None)
    args = parser.parse_args()

    try:
        project_root = builder.resolve_project_root(args.project_root)
        tdx_root = Path(args.tdx_root).resolve()
        output_directory = (
            Path(args.output_dir).resolve()
            if args.output_dir
            else (project_root / builder.DEFAULT_OUTPUT_DIRECTORY).resolve()
        )
        result = run_daily_refresh(
            project_root=project_root,
            tdx_root=tdx_root,
            output_directory=output_directory,
            publish_directory=Path(args.publish_dir).resolve() if args.publish_dir else None,
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                ensure_ascii=False,
            )
        )
        raise SystemExit(1) from exc
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
