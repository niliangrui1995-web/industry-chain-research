from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
import json
from pathlib import Path
import struct
import subprocess
import sys
from typing import Iterable


PROTOCOL_VERSION = "2026-08-28.1"
PROJECT_ROOT_DEFAULT = Path(r"D:\vcp_hunter\产业链投研")
FUND_ROOT_DEFAULT = Path(r"D:\vcp_hunter\基金持仓")
DFCF_DIRECTORY = Path("artifacts/leverage_capitulation/dfcf_daily")
POST2017_DIRECTORY = Path(
    "artifacts/leverage_capitulation/eastmoney_post2017_market_cap_vendor"
)
POST2017_START = date(2017, 1, 3)
TDX_DAY_STRUCT = struct.Struct("<IIIIIfII")

DFCF_SCRIPT = Path(
    ".agents/skills/a-share-leverage-capitulation-analyst/scripts/update_dfcf_margin_daily.py"
)
POST2017_SCRIPT = Path("scripts/update_eastmoney_shsz_market_cap_vendor.py")
BUNDLE_SCRIPT = Path("scripts/append_leverage_dashboard_tail.py")


class RefreshBlocked(RuntimeError):
    """缺少可复用基线或新增尾部数据无法按固定路径更新。"""


@dataclass(frozen=True)
class DateWindow:
    start: date
    end: date

    def to_dict(self) -> dict[str, str]:
        return {"start": self.start.isoformat(), "end": self.end.isoformat()}


@dataclass(frozen=True)
class RefreshPlan:
    dfcf_windows: tuple[DateWindow, ...]
    market_cap_windows: tuple[DateWindow, ...]

    @property
    def has_work(self) -> bool:
        return bool(self.dfcf_windows or self.market_cap_windows)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ready" if self.has_work else "no_changes",
            "protocol_version": PROTOCOL_VERSION,
            "historical_data_policy": "reuse_without_full_validation",
            "dfcf_tail_gap_windows": [
                window.to_dict() for window in self.dfcf_windows
            ],
            "post2017_market_cap_tail_gap_windows": [
                window.to_dict() for window in self.market_cap_windows
            ],
        }


def _parse_date(value: object, label: str) -> date:
    if not isinstance(value, str):
        raise RefreshBlocked(f"{label} 缺少 YYYY-MM-DD 日期")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RefreshBlocked(f"{label} 不是 YYYY-MM-DD 日期") from exc


def _read_last_csv_date(path: Path, label: str) -> date:
    """只读取既有表的最后一个日期；不扫描或修复中间历史缺口。"""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            latest: date | None = None
            for row in reader:
                value = row.get("date")
                if value:
                    latest = _parse_date(value, f"{label}.date")
    except OSError as exc:
        raise RefreshBlocked(f"{label} 无法读取: {path}") from exc
    if latest is None:
        raise RefreshBlocked(f"{label} 为空")
    return latest


def _read_csv_dates_after(
    path: Path, label: str, after: date, cutoff: date
) -> list[date]:
    """仅读取最后基线日期之后的新增记录，历史记录不参与校验。"""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            values = [
                current
                for row in reader
                if (value := row.get("date"))
                and after < (current := _parse_date(value, f"{label}.date")) <= cutoff
            ]
    except OSError as exc:
        raise RefreshBlocked(f"{label} 无法读取: {path}") from exc
    return sorted(set(values))


def _read_tdx_dates_after(path: Path, after: date, cutoff: date) -> list[date]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RefreshBlocked(f"TDX 日历哨兵无法读取: {path}") from exc
    if not payload or len(payload) % TDX_DAY_STRUCT.size:
        raise RefreshBlocked("TDX 日历哨兵格式无效")
    values: list[date] = []
    for offset in range(0, len(payload), TDX_DAY_STRUCT.size):
        raw_day = TDX_DAY_STRUCT.unpack_from(payload, offset)[0]
        try:
            current = datetime.strptime(str(raw_day), "%Y%m%d").date()
        except ValueError as exc:
            raise RefreshBlocked("TDX 日历哨兵包含无效日期") from exc
        if after < current <= cutoff:
            values.append(current)
    return sorted(set(values))


def _as_tail_window(values: Iterable[date]) -> tuple[DateWindow, ...]:
    dates = sorted(set(values))
    if not dates:
        return ()
    return (DateWindow(start=dates[0], end=dates[-1]),)


def build_refresh_plan(
    project_root: Path,
    *,
    tdx_path: Path | None = None,
    as_of: date | None = None,
) -> RefreshPlan:
    if not (project_root / "AGENTS.md").is_file():
        raise RefreshBlocked(f"无法确认项目根目录: {project_root}")

    cutoff = as_of or date.today()
    dfcf_table = project_root / DFCF_DIRECTORY / "dfcf_margin_balances.csv"
    dfcf_latest = _read_last_csv_date(dfcf_table, "DFCF 合并表")
    sentinel = tdx_path or Path(r"D:\HT\vipdoc\sh\lday\sh000001.day")
    dfcf_windows = _as_tail_window(
        _read_tdx_dates_after(sentinel, after=dfcf_latest, cutoff=cutoff)
    )

    post2017_directory = project_root / POST2017_DIRECTORY
    post2017_table = post2017_directory / "eastmoney_post2017_market_cap_vendor.csv"
    post2017_manifest = (
        post2017_directory / "eastmoney_post2017_market_cap_vendor_manifest.json"
    )
    if not post2017_table.exists() or not post2017_manifest.exists():
        raise RefreshBlocked("后2017市值基线缺失；日常任务禁止自动全量初始化")
    post2017_latest = _read_last_csv_date(post2017_table, "后2017市值表")
    market_cap_windows = _as_tail_window(
        _read_csv_dates_after(
            dfcf_table,
            "DFCF 合并表",
            after=max(post2017_latest, POST2017_START - date.resolution),
            cutoff=cutoff,
        )
    )
    return RefreshPlan(
        dfcf_windows=dfcf_windows,
        market_cap_windows=market_cap_windows,
    )


def _run(command: list[str], project_root: Path) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).strip()
        raise RefreshBlocked(f"增量入口失败: {detail[-1000:]}")
    return {"command": command, "stdout": completed.stdout.strip()}


def execute_refresh(project_root: Path, fund_root: Path) -> dict[str, object]:
    initial = build_refresh_plan(project_root)
    executions: list[dict[str, object]] = []
    requested_dfcf_windows = [window.to_dict() for window in initial.dfcf_windows]
    for window in initial.dfcf_windows:
        executions.append(
            _run(
                [
                    sys.executable,
                    str(project_root / DFCF_SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--backfill-start",
                    window.start.isoformat(),
                    "--end-date",
                    window.end.isoformat(),
                ],
                project_root,
            )
        )

    after_dfcf = build_refresh_plan(project_root)
    if after_dfcf.dfcf_windows:
        return {
            "status": "pending_dfcf_source",
            "protocol_version": PROTOCOL_VERSION,
            "historical_data_policy": "reuse_without_full_validation",
            "remaining_dfcf_tail_gap_windows": [
                window.to_dict() for window in after_dfcf.dfcf_windows
            ],
            "executions": executions,
        }

    requested_market_cap_windows = [
        window.to_dict() for window in after_dfcf.market_cap_windows
    ]
    for window in after_dfcf.market_cap_windows:
        executions.append(
            _run(
                [
                    sys.executable,
                    str(project_root / POST2017_SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--start-date",
                    window.start.isoformat(),
                    "--end-date",
                    window.end.isoformat(),
                    "--incremental",
                ],
                project_root,
            )
        )

    after_market_cap = build_refresh_plan(project_root)
    if after_market_cap.market_cap_windows:
        return {
            "status": "pending_market_cap_source",
            "protocol_version": PROTOCOL_VERSION,
            "historical_data_policy": "reuse_without_full_validation",
            "remaining_post2017_market_cap_tail_gap_windows": [
                window.to_dict() for window in after_market_cap.market_cap_windows
            ],
            "executions": executions,
        }

    if executions:
        completed_windows = [
            *initial.dfcf_windows,
            *after_dfcf.market_cap_windows,
        ]
        tail_end = max(window.end for window in completed_windows)
        executions.append(
            _run(
                [
                    sys.executable,
                    str(project_root / BUNDLE_SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--publish-dir",
                    str(fund_root / "public/data"),
                    "--end-date",
                    tail_end.isoformat(),
                ],
                project_root,
            )
        )
    return {
        "status": "updated" if executions else "no_changes",
        "protocol_version": PROTOCOL_VERSION,
        "historical_data_policy": "reuse_without_full_validation",
        "updated_dfcf_tail_gap_windows": requested_dfcf_windows,
        "updated_post2017_market_cap_tail_gap_windows": requested_market_cap_windows,
        "executions": executions,
    }


def _resolve_root(value: str | None, default: Path, marker: str) -> Path:
    root = Path(value).expanduser().resolve() if value else default
    if not (root / marker).exists():
        raise RefreshBlocked(f"无法确认目录: {root}")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="仅补尾部新增缺口的两融网页数据")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--fund-root", default=None)
    parser.add_argument("--execute", action="store_true", help="执行新增尾部缺口计划")
    args = parser.parse_args()
    try:
        project_root = _resolve_root(args.project_root, PROJECT_ROOT_DEFAULT, "AGENTS.md")
        fund_root = _resolve_root(args.fund_root, FUND_ROOT_DEFAULT, "package.json")
        result = (
            execute_refresh(project_root, fund_root)
            if args.execute
            else build_refresh_plan(project_root).to_dict()
        )
    except RefreshBlocked as exc:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "protocol_version": PROTOCOL_VERSION,
                    "reason": str(exc),
                },
                ensure_ascii=False,
            )
        )
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
