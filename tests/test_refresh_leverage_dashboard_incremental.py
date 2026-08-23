from __future__ import annotations

import csv
from datetime import date
import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "refresh_leverage_dashboard_incremental.py"
SPEC = importlib.util.spec_from_file_location("refresh_leverage_dashboard_incremental", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_csv(path: Path, dates: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date"])
        writer.writeheader()
        writer.writerows({"date": value} for value in dates)


def write_tdx(path: Path, dates: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = b"".join(
        MODULE.TDX_DAY_STRUCT.pack(
            int(value.replace("-", "")), 0, 0, 0, 0, 0.0, 0, 0
        )
        for value in dates
    )
    path.write_bytes(payload)


def write_fixture(
    root: Path,
    *,
    dfcf_dates: list[str],
    post_dates: list[str],
    tdx_dates: list[str],
) -> Path:
    root.mkdir(parents=True)
    (root / "AGENTS.md").write_text("fixture\n", encoding="utf-8")
    write_csv(
        root / MODULE.DFCF_DIRECTORY / "dfcf_margin_balances.csv", dfcf_dates
    )
    post_directory = root / MODULE.POST2017_DIRECTORY
    write_csv(post_directory / "eastmoney_post2017_market_cap_vendor.csv", post_dates)
    (post_directory / "eastmoney_post2017_market_cap_vendor_manifest.json").write_text(
        "{}\n", encoding="utf-8"
    )
    tdx = root / "tdx" / "sh000001.day"
    write_tdx(tdx, tdx_dates)
    return tdx


def test_plan_ignores_historical_internal_gaps_and_only_requests_new_tail(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "research"
    tdx = write_fixture(
        project_root,
        dfcf_dates=["2017-01-03", "2017-01-05"],
        post_dates=["2017-01-03", "2017-01-05"],
        tdx_dates=["2017-01-03", "2017-01-04", "2017-01-05", "2017-01-06"],
    )

    plan = MODULE.build_refresh_plan(
        project_root, tdx_path=tdx, as_of=date(2017, 1, 6)
    )

    assert [window.to_dict() for window in plan.dfcf_windows] == [
        {"start": "2017-01-06", "end": "2017-01-06"}
    ]
    assert plan.market_cap_windows == ()
    assert plan.to_dict()["historical_data_policy"] == "reuse_without_full_validation"


def test_plan_requests_only_new_market_cap_tail(tmp_path: Path) -> None:
    project_root = tmp_path / "research"
    tdx = write_fixture(
        project_root,
        dfcf_dates=["2017-01-03", "2017-01-04", "2017-01-05"],
        post_dates=["2017-01-03", "2017-01-04"],
        tdx_dates=["2017-01-03", "2017-01-04", "2017-01-05"],
    )

    plan = MODULE.build_refresh_plan(
        project_root, tdx_path=tdx, as_of=date(2017, 1, 5)
    )

    assert plan.dfcf_windows == ()
    assert [window.to_dict() for window in plan.market_cap_windows] == [
        {"start": "2017-01-05", "end": "2017-01-05"}
    ]


def test_plan_reports_no_changes_when_no_new_tail_data_exists(tmp_path: Path) -> None:
    project_root = tmp_path / "research"
    tdx = write_fixture(
        project_root,
        dfcf_dates=["2017-01-03", "2017-01-04"],
        post_dates=["2017-01-03", "2017-01-04"],
        tdx_dates=["2017-01-03", "2017-01-04"],
    )

    plan = MODULE.build_refresh_plan(
        project_root, tdx_path=tdx, as_of=date(2017, 1, 4)
    )

    assert plan.to_dict()["status"] == "no_changes"
    assert plan.has_work is False


def test_plan_blocks_missing_post2017_baseline(tmp_path: Path) -> None:
    project_root = tmp_path / "research"
    tdx = write_fixture(
        project_root,
        dfcf_dates=["2017-01-03"],
        post_dates=["2017-01-03"],
        tdx_dates=["2017-01-03"],
    )
    (project_root / MODULE.POST2017_DIRECTORY / "eastmoney_post2017_market_cap_vendor_manifest.json").unlink()

    with pytest.raises(MODULE.RefreshBlocked, match="基线缺失"):
        MODULE.build_refresh_plan(
            project_root, tdx_path=tdx, as_of=date(2017, 1, 3)
        )


def test_execute_uses_only_planned_tail_intervals_and_never_full_bootstrap(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_root = tmp_path / "research"
    fund_root = tmp_path / "fund"
    plans = iter(
        [
            MODULE.RefreshPlan(
                dfcf_windows=(MODULE.DateWindow(date(2026, 8, 4), date(2026, 8, 4)),),
                market_cap_windows=(),
            ),
            MODULE.RefreshPlan(
                dfcf_windows=(),
                market_cap_windows=(
                    MODULE.DateWindow(date(2026, 8, 4), date(2026, 8, 4)),
                ),
            ),
            MODULE.RefreshPlan(dfcf_windows=(), market_cap_windows=()),
        ]
    )
    commands: list[list[str]] = []

    monkeypatch.setattr(MODULE, "build_refresh_plan", lambda *_args, **_kwargs: next(plans))
    monkeypatch.setattr(
        MODULE,
        "_run",
        lambda command, _root: commands.append(command)
        or {"command": command, "stdout": ""},
    )

    result = MODULE.execute_refresh(project_root, fund_root)

    assert result["status"] == "updated"
    assert len(commands) == 3
    assert commands[0][-4:] == [
        "--backfill-start",
        "2026-08-04",
        "--end-date",
        "2026-08-04",
    ]
    market_command = commands[1]
    assert market_command[market_command.index("--start-date") + 1] == "2026-08-04"
    assert market_command[market_command.index("--end-date") + 1] == "2026-08-04"
    assert "--incremental" in market_command
    assert "--bootstrap-full" not in market_command
    assert commands[2][1].endswith("append_leverage_dashboard_tail.py")
    assert commands[2][-2:] == ["--end-date", "2026-08-04"]
