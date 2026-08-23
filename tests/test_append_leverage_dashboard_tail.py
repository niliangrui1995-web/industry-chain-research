from __future__ import annotations

import csv
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "append_leverage_dashboard_tail.py"
SPEC = importlib.util.spec_from_file_location("append_leverage_dashboard_tail", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tdx(path: Path, dates_and_closes: list[tuple[str, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"".join(
            MODULE.DAY_STRUCT.pack(
                int(day.replace("-", "")), 0, 0, close, close, 0.0, 0, 0
            )
            for day, close in dates_and_closes
        )
    )


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def baseline_record() -> dict[str, object]:
    return {
        "date": "2026-08-20",
        "denominator_market_cap_yi": 1000.0,
        "index_000001_close": 3000.0,
        "index_399006_close": 2000.0,
        "index_399106_close": 1800.0,
        "market_cap_review_status": "eastmoney_vendor_unverified",
        "market_cap_source": "eastmoney_post2017_vendor_unverified",
        "ratio_pct": 2.0,
        "sh_margin_yi": 10.0,
        "sz_margin_yi": 10.0,
        "total_margin_yi": 20.0,
    }


def write_fixture(tmp_path: Path, *, include_new_market_cap: bool = True) -> tuple[Path, Path]:
    project_root = tmp_path / "research"
    publish_dir = tmp_path / "fund" / "public" / "data"
    project_root.mkdir(parents=True)
    (project_root / "AGENTS.md").write_text("fixture\n", encoding="utf-8")
    publish_dir.mkdir(parents=True)

    payload = {
        "schema_version": "1",
        "generated_at_beijing": "2026-08-23T09:00:00+08:00",
        "provenance": {
            "ratio_available": True,
            "ratio_unavailable_reason": None,
            "ratio_scope_warning": "fixture",
            "ratio_data_range": {"start": "2026-08-20", "end": "2026-08-20"},
            "source_switch_date": "2017-01-03",
        },
        "records": [baseline_record()],
    }
    manifest = {
        "schema_version": "1",
        "payload_sha256": "base-payload-sha",
        "payload_records": 1,
        "data_range": {"start": "2026-08-20", "end": "2026-08-20"},
        "market_cap": {
            "ratio_available": True,
            "ratio_data_range": {"start": "2026-08-20", "end": "2026-08-20"},
            "ratio_missing_records": 0,
            "source_segments": [
                {"start": "2011-08-03", "end": "2016-12-30"},
                {"start": "2017-01-03", "end": "2026-08-20"},
            ],
        },
    }
    (publish_dir / MODULE.PAYLOAD_FILENAME).write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    (publish_dir / MODULE.MANIFEST_FILENAME).write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )

    write_csv(
        project_root / MODULE.DFCF_DIRECTORY / "dfcf_margin_balances.csv",
        ["date", "sh_margin_y", "sz_margin_y", "total_margin_y"],
        [
            {"date": "2026-08-20", "sh_margin_y": "10", "sz_margin_y": "10", "total_margin_y": "20"},
            {"date": "2026-08-21", "sh_margin_y": "11", "sz_margin_y": "12", "total_margin_y": "23"},
        ],
    )
    market_rows = [
        {"date": "2026-08-20", "market_cap_yi": "1000"},
    ]
    if include_new_market_cap:
        market_rows.append({"date": "2026-08-21", "market_cap_yi": "1100"})
    write_csv(
        project_root
        / MODULE.POST2017_DIRECTORY
        / "eastmoney_post2017_market_cap_vendor.csv",
        ["date", "market_cap_yi"],
        market_rows,
    )
    index_paths: dict[str, Path] = {}
    for code, close in {"000001": 301000, "399106": 181000, "399006": 201000}.items():
        path = tmp_path / "tdx" / f"{code}.day"
        write_tdx(path, [("2026-08-20", close - 100), ("2026-08-21", close)])
        index_paths[code] = path
    MODULE.INDEX_PATHS = index_paths
    return project_root, publish_dir


def test_append_only_adds_new_tail_and_preserves_existing_records(tmp_path: Path) -> None:
    project_root, publish_dir = write_fixture(tmp_path)
    before_payload = json.loads(
        (publish_dir / MODULE.PAYLOAD_FILENAME).read_text(encoding="utf-8")
    )

    result = MODULE.append_tail(project_root, publish_dir, cutoff=date(2026, 8, 21))

    payload_path = publish_dir / MODULE.PAYLOAD_FILENAME
    manifest_path = publish_dir / MODULE.MANIFEST_FILENAME
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert result["status"] == "updated"
    assert result["appended_dates"] == ["2026-08-21"]
    assert payload["records"][0] == before_payload["records"][0]
    assert [record["date"] for record in payload["records"]] == [
        "2026-08-20",
        "2026-08-21",
    ]
    assert payload["records"][-1]["ratio_pct"] == 2.09090909
    assert manifest["payload_records"] == 2
    assert manifest["data_range"]["end"] == "2026-08-21"
    assert manifest["market_cap"]["source_segments"][1]["end"] == "2026-08-21"
    assert manifest["incremental_tail"] == {
        "base_payload_sha256": "base-payload-sha",
        "base_last_date": "2026-08-20",
        "appended_dates": ["2026-08-21"],
    }
    assert manifest["payload_sha256"] == sha256(payload_path.read_bytes())
    artifact_payload = (
        project_root / MODULE.DASHBOARD_DIRECTORY / MODULE.PAYLOAD_FILENAME
    )
    assert artifact_payload.read_bytes() == payload_path.read_bytes()


def test_append_does_not_write_when_no_new_tail_exists(tmp_path: Path) -> None:
    project_root, publish_dir = write_fixture(tmp_path)
    payload_path = publish_dir / MODULE.PAYLOAD_FILENAME
    manifest_path = publish_dir / MODULE.MANIFEST_FILENAME
    before = (payload_path.read_bytes(), manifest_path.read_bytes())

    result = MODULE.append_tail(project_root, publish_dir, cutoff=date(2026, 8, 20))

    assert result["status"] == "no_changes"
    assert (payload_path.read_bytes(), manifest_path.read_bytes()) == before
    assert not (project_root / MODULE.DASHBOARD_DIRECTORY / MODULE.PAYLOAD_FILENAME).exists()


def test_append_refuses_incomplete_new_records_without_writing(tmp_path: Path) -> None:
    project_root, publish_dir = write_fixture(tmp_path, include_new_market_cap=False)
    payload_path = publish_dir / MODULE.PAYLOAD_FILENAME
    manifest_path = publish_dir / MODULE.MANIFEST_FILENAME
    before = (payload_path.read_bytes(), manifest_path.read_bytes())

    with pytest.raises(MODULE.TailAppendBlocked, match="缺少同日市值"):
        MODULE.append_tail(project_root, publish_dir, cutoff=date(2026, 8, 21))

    assert (payload_path.read_bytes(), manifest_path.read_bytes()) == before
    assert not (project_root / MODULE.DASHBOARD_DIRECTORY / MODULE.PAYLOAD_FILENAME).exists()
