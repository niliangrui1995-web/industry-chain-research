from __future__ import annotations

import json
import hashlib
import shutil
import struct
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import numpy as np
import pytest


MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / ".agents"
    / "skills"
    / "kronos-market-forecasting"
    / "scripts"
)
sys.path.insert(0, str(MODULE_DIR))

import kronos_a_share_data as data  # noqa: E402


def _day_record(
    trade_date: int,
    open_i: int = 1000,
    high_i: int = 1100,
    low_i: int = 900,
    close_i: int = 1050,
    amount: float = 1000.0,
    volume: int = 100,
) -> bytes:
    return struct.pack(
        "<IIIIIfII",
        trade_date,
        open_i,
        high_i,
        low_i,
        close_i,
        amount,
        volume,
        0,
    )


def _write_day(path: Path, records: list[bytes] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"".join(
            records
            or [
                _day_record(20260730),
                _day_record(20260731, open_i=1050, high_i=1120, low_i=1000, close_i=1100),
            ]
        )
    )
    return path


def _make_tdx_source(root: Path) -> Path:
    for market in ("sh", "sz", "bj"):
        (root / "vipdoc" / market / "lday").mkdir(parents=True, exist_ok=True)
    _write_day(root / "vipdoc" / "sh" / "lday" / "sh600000.day")
    _write_day(root / "vipdoc" / "sz" / "lday" / "sz000001.day")
    _write_day(root / "vipdoc" / "bj" / "lday" / "bj920001.day")
    _write_day(root / "vipdoc" / "sh" / "lday" / "sh000300.day")
    _write_day(root / "vipdoc" / "sh" / "lday" / "sh000905.day")
    _write_day(root / "vipdoc" / "sh" / "lday" / "sh000906.day")
    _write_day(root / "vipdoc" / "sh" / "lday" / "sh000001.day")
    _write_day(root / "vipdoc" / "bj" / "lday" / "bj899050.day")
    cache = root / "T0002" / "hq_cache"
    cache.mkdir(parents=True)
    (cache / "gbbq").write_bytes(b"gbbq-fixture")
    (cache / "base.dbf").write_bytes(b"dbf-fixture")
    return root


def _training_paths(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "project"
    project.mkdir()
    return project, project / "_training" / "kronos_ashare"


def _write_csv(root: Path, table_name: str, rows: list[dict[str, object]]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(root / f"{table_name}.csv", index=False, encoding="utf-8")


def _make_valid_pit_bundle(root: Path) -> Path:
    calendar_dates = pd.bdate_range("2018-01-01", "2026-07-31")
    covered_dates = calendar_dates[calendar_dates >= pd.Timestamp("2018-01-02")]
    previous_date_by_date = {
        current: calendar_dates[index - 1]
        for index, current in enumerate(calendar_dates)
        if index > 0
    }
    _write_csv(
        root,
        "security_master",
        [
            {
                "ticker": "600000.SH",
                "exchange": "SH",
                "board": "main",
                "security_type": "A_STOCK",
                "list_date": "1999-11-10",
                "delist_date": "",
            }
        ],
    )
    _write_csv(
        root,
        "st_status",
        [
            {
                "ticker": "600000.SH",
                "effective_from": "2018-01-02",
                "effective_to": "",
                "is_st": 0,
            }
        ],
    )
    _write_csv(
        root,
        "suspensions",
        [
            {
                "ticker": "600000.SH",
                "trade_date": current.date().isoformat(),
                "is_suspended": int(current == pd.Timestamp("2020-01-02")),
            }
            for current in covered_dates
        ],
    )
    _write_csv(
        root,
        "price_limits",
        [
            {
                "ticker": "600000.SH",
                "trade_date": current.date().isoformat(),
                "up_limit": 11.0,
                "down_limit": 9.0,
                "rule_version": "main_normal_10pct",
                "no_limit_reason": "",
                "previous_trade_date": previous_date_by_date[current].date().isoformat(),
                "previous_close_raw": 10.0,
            }
            for current in covered_dates
        ],
    )
    _write_csv(
        root,
        "index_membership",
        [
            {
                "index_code": index_code,
                "ticker": "600000.SH",
                "effective_from": "2018-01-02",
                "effective_to": "",
            }
            for index_code in ("000300.SH", "000905.SH")
        ],
    )
    _write_csv(
        root,
        "corporate_actions",
        [
            {
                "ticker": "600000.SH",
                "announcement_date": "2020-05-01",
                "ex_date": "2020-06-01",
                "cash_div": 0.1,
                "bonus_ratio": 0.0,
                "rights_ratio": 0.0,
                "rights_price": 0.0,
            }
        ],
    )
    _write_csv(
        root,
        "trading_calendar",
        [
            {
                "trade_date": current.date().isoformat(),
                "is_open": 1,
                "benchmark_ticker": "000906.SH",
            }
            for current in calendar_dates
        ],
    )
    _write_csv(
        root,
        "coverage",
        [
            {
                "dataset": dataset,
                "coverage_start": "2018-01-02",
                "coverage_end": "2026-07-31",
                "is_complete": 1,
            }
            for dataset in (
                "security_master",
                "st_status",
                "suspensions",
                "price_limits",
                "index_membership",
                "corporate_actions",
                "trading_calendar",
            )
        ],
    )
    return root


def _add_verified_coverage_bindings(
    root: Path,
    *,
    coverage_start: str = "2018-01-01",
    coverage_end: str = "2026-07-31",
) -> Path:
    raw_root = root / "raw_responses"
    manifest_root = root / "provenance"
    raw_root.mkdir(parents=True, exist_ok=True)
    manifest_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for dataset in data.PIT_PROVENANCE_DATASETS:
        table_path = root / f"{dataset}.csv"
        frame = data.validate_pit_table(dataset, table_path)
        raw_path = raw_root / f"{dataset}.bin"
        raw_path.write_bytes(f"raw-response:{dataset}\n".encode("utf-8"))
        manifest_path = manifest_root / f"{dataset}.json"
        manifest = {
            "schema_version": data.PIT_PROVENANCE_SCHEMA,
            "dataset": dataset,
            "coverage_start": coverage_start,
            "coverage_end": coverage_end,
            "sources": [
                {
                    "source_id": f"official-{dataset}",
                    "source_class": "official_primary",
                    "url": f"https://example.invalid/{dataset}.csv",
                    "retrieved_at": "2026-08-03T00:00:00+00:00",
                    "valid_from": coverage_start,
                    "valid_to": coverage_end,
                    "path": raw_path.relative_to(root).as_posix(),
                    "bytes": raw_path.stat().st_size,
                    "sha256": _sha256(raw_path),
                }
            ],
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
        )
        rows.append(
            {
                "dataset": dataset,
                "coverage_start": coverage_start,
                "coverage_end": coverage_end,
                "is_complete": 1,
                "binding_schema": data.PIT_COVERAGE_BINDING_SCHEMA,
                "file_sha256": _sha256(table_path),
                "schema_sha256": data.pit_table_schema_sha256(dataset, frame),
                "row_count": len(frame),
                "file_bytes": table_path.stat().st_size,
                "source_manifest": manifest_path.relative_to(root).as_posix(),
                "source_manifest_sha256": _sha256(manifest_path),
            }
        )
    _write_csv(root, "coverage", rows)
    return root


def _valid_manifest(*, dry_run: bool = False) -> dict[str, object]:
    return {
        "snapshot_id": "fixture",
        "source_consistent": True,
        "dry_run": dry_run,
        "kind_counts": {"tdx_day": 3, "gbbq": 1, "base_dbf": 1},
    }


def _valid_adjustment_manifest() -> dict[str, object]:
    return {
        "schema_version": data.MODEL_ADJUSTMENT_SCHEMA,
        "adjustment": {
            "mode": "causal_backward_total_return",
            "materialized": True,
            "trade_price_raw": True,
            "model_price_adjusted": True,
            "cutoff_field": "origin_date",
            "future_action_use_count": 0,
            "future_action_audit_verified": True,
        },
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_verified_adjustment_artifact(
    training_root: Path,
    pit_root: Path,
) -> tuple[Path, Path]:
    snapshot_dir = training_root / "data" / "raw" / "fixture"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_manifest = snapshot_dir / "source_manifest.json"
    snapshot_manifest.write_text(
        json.dumps(_valid_manifest(), ensure_ascii=False), encoding="utf-8"
    )

    dataset_dir = training_root / "data" / "datasets" / "fixture"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    sample_index = dataset_dir / "sample_index.csv"
    sample_index.write_text("sample_id\n0\n", encoding="utf-8")
    sample_manifest = dataset_dir / "sample_manifest.json"
    sample_manifest.write_text(
        json.dumps({"sample_index_sha256": _sha256(sample_index)}),
        encoding="utf-8",
    )

    token_dir = training_root / "data" / "tokens" / "fixture"
    token_dir.mkdir(parents=True, exist_ok=True)
    arrays = {
        "s1.npy": np.zeros((1, 100), dtype=np.uint16),
        "s2.npy": np.zeros((1, 100), dtype=np.uint16),
        "stamp.npy": np.zeros((1, 100, 5), dtype=np.uint8),
        "label.npy": np.zeros((1,), dtype=np.float32),
        "trade_date.npy": np.zeros((1,), dtype=np.int32),
        "instrument_id.npy": np.zeros((1,), dtype=np.int32),
        "active_member_count.npy": np.ones((1,), dtype=np.int32),
        "split.npy": np.zeros((1,), dtype=np.uint8),
    }
    files = {}
    for filename, array in arrays.items():
        path = token_dir / filename
        np.save(path, array)
        files[filename] = {"bytes": path.stat().st_size, "sha256": _sha256(path)}
    token_manifest = token_dir / "manifest.json"
    payload = {
        **_valid_adjustment_manifest(),
        "sample_count": 1,
        "files": files,
        "snapshot_manifest_sha256": _sha256(snapshot_manifest),
        "sample_index_path": str(sample_index),
        "sample_index_sha256": _sha256(sample_index),
        "sample_manifest_path": str(sample_manifest),
        "sample_manifest_sha256": _sha256(sample_manifest),
        "membership_sha256": _sha256(pit_root / "index_membership.csv"),
        "corporate_actions_sha256": _sha256(pit_root / "corporate_actions.csv"),
    }
    token_manifest.write_text(json.dumps(payload), encoding="utf-8")
    return snapshot_manifest, token_manifest


def _make_inference_fixture(
    tmp_path: Path,
    *,
    as_of: datetime,
) -> tuple[Path, Path, Path, data.PitBundleValidation]:
    project = tmp_path / "inference-project"
    training_root = project / "_training" / "kronos_ashare"
    pit_root = training_root / "data" / "inference-sources" / "current"
    source = tmp_path / "inference-tdx"
    tickers = ("600000.SH", "000001.SZ")
    dates = pd.date_range(
        end=as_of.date(), periods=data.INFERENCE_MARKET_RECORDS, freq="D"
    )
    records = [
        _day_record(
            int(stamp.strftime("%Y%m%d")),
            open_i=1000 + index,
            high_i=1100 + index,
            low_i=900 + index,
            close_i=1050 + index,
        )
        for index, stamp in enumerate(dates)
    ]
    _write_day(source / "vipdoc" / "sh" / "lday" / "sh600000.day", records)
    _write_day(source / "vipdoc" / "sz" / "lday" / "sz000001.day", records)

    raw_root = pit_root / "raw_responses"
    provenance_root = pit_root / "provenance"
    raw_root.mkdir(parents=True)
    provenance_root.mkdir(parents=True)
    coverage_rows: list[dict[str, object]] = []
    frames: dict[str, pd.DataFrame] = {}
    for table_name in (*data.MANDATORY_PIT_TABLES, data.TRADING_CALENDAR_TABLE):
        table_path = pit_root / f"{table_name}.csv"
        table_path.parent.mkdir(parents=True, exist_ok=True)
        table_path.write_text(f"fixture\n{table_name}\n", encoding="utf-8")
    for dataset in data.PIT_PROVENANCE_DATASETS:
        raw_path = raw_root / f"{dataset}.bin"
        raw_path.write_bytes(f"raw:{dataset}".encode("utf-8"))
        manifest_path = provenance_root / f"{dataset}.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": data.PIT_PROVENANCE_SCHEMA,
                    "dataset": dataset,
                    "coverage_start": as_of.date().isoformat(),
                    "coverage_end": as_of.date().isoformat(),
                    "sources": [
                        {
                            "source_id": dataset,
                            "source_class": "official_primary",
                            "url": f"https://example.invalid/{dataset}",
                            "retrieved_at": as_of.isoformat(),
                            "valid_from": as_of.date().isoformat(),
                            "valid_to": as_of.date().isoformat(),
                            "path": raw_path.relative_to(pit_root).as_posix(),
                            "sha256": _sha256(raw_path),
                            "bytes": raw_path.stat().st_size,
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        coverage_rows.append(
            {
                "dataset": dataset,
                "coverage_start": pd.Timestamp(as_of.date()),
                "coverage_end": pd.Timestamp(as_of.date()),
                "is_complete": True,
                "binding_schema": data.PIT_COVERAGE_BINDING_SCHEMA,
                "file_sha256": "a" * 64,
                "schema_sha256": "b" * 64,
                "row_count": 1,
                "file_bytes": 1,
                "source_manifest": manifest_path.relative_to(pit_root).as_posix(),
                "source_manifest_sha256": _sha256(manifest_path),
            }
        )
    frames["coverage"] = pd.DataFrame(coverage_rows)
    frames["index_membership"] = pd.DataFrame(
        [
            {
                "index_code": index_code,
                "ticker": ticker,
                "effective_from": pd.Timestamp(as_of.date()),
                "effective_to": pd.NaT,
            }
            for index_code, ticker in zip(data.REQUIRED_INDEX_CODES, tickers, strict=True)
        ]
    )
    frames["suspensions"] = pd.DataFrame(
        [
            {
                "ticker": ticker,
                "trade_date": pd.Timestamp(as_of.date()),
                "is_suspended": False,
            }
            for ticker in tickers
        ]
    )
    capabilities = {name: True for name in data.REQUIRED_CAPABILITIES}
    validation = data.PitBundleValidation(
        frames=frames,
        table_reports={},
        missing_tables=[],
        errors=[],
        warnings=[],
        capabilities=capabilities,
    )
    return project, training_root, source, validation


def test_guard_training_root_accepts_only_project_download_tree(tmp_path: Path) -> None:
    project, training_root = _training_paths(tmp_path)
    assert data.guard_training_root(training_root, project_root=project) == training_root.resolve()
    assert data.guard_training_root(training_root / "raw", project_root=project) == (
        training_root / "raw"
    ).resolve()
    with pytest.raises(data.UnsafePathError):
        data.guard_training_root(project, project_root=project)
    with pytest.raises(data.UnsafePathError):
        data.guard_training_root(tmp_path / "elsewhere", project_root=project)


def test_read_tdx_day_parses_fixed_binary_contract(tmp_path: Path) -> None:
    path = _write_day(tmp_path / "sh600000.day")
    frame = data.read_tdx_day(path)
    metadata = data.inspect_tdx_day(path)

    assert list(frame.columns) == [
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "amount",
        "volume",
        "reserved",
    ]
    assert frame.loc[0, "open"] == 10.0
    assert frame.loc[1, "close"] == 11.0
    assert metadata["records"] == 2
    assert metadata["first_date"] == "2026-07-30"
    assert metadata["last_date"] == "2026-07-31"
    assert len(metadata["sha256"]) == 64


@pytest.mark.parametrize(
    "raw, message",
    [
        (b"bad", "整数倍"),
        (_day_record(20260731, high_i=1000, close_i=1050), "OHLC"),
        (_day_record(20260731) + _day_record(20260731), "严格递增"),
        (_day_record(20260230), "日期非法"),
        (_day_record(20260731, amount=-1.0), "成交额非法"),
    ],
)
def test_read_tdx_day_rejects_corrupt_records(tmp_path: Path, raw: bytes, message: str) -> None:
    path = tmp_path / "bad.day"
    path.write_bytes(raw)
    with pytest.raises(data.TdxDayFormatError, match=message):
        data.read_tdx_day(path)


def test_snapshot_dry_run_validates_without_writing(tmp_path: Path) -> None:
    source = _make_tdx_source(tmp_path / "HT")
    project, training_root = _training_paths(tmp_path)
    manifest = data.create_immutable_snapshot(
        source,
        training_root,
        snapshot_id="dry-fixture",
        dry_run=True,
        project_root=project,
    )

    assert manifest["dry_run"] is True
    assert manifest["source_consistent"] is True
    assert manifest["kind_counts"] == {"tdx_day": 6, "gbbq": 1, "base_dbf": 1}
    assert not training_root.exists()
    relative_sources = {row["source_relative"] for row in manifest["files"]}
    assert "vipdoc/sh/lday/sh000300.day" in relative_sources
    assert "vipdoc/sh/lday/sh000905.day" in relative_sources
    assert "vipdoc/sh/lday/sh000906.day" in relative_sources
    assert "vipdoc/sh/lday/sh000001.day" not in relative_sources
    assert "vipdoc/bj/lday/bj899050.day" not in relative_sources


def test_snapshot_copy_is_atomic_hashed_and_non_overwriting(tmp_path: Path) -> None:
    source = _make_tdx_source(tmp_path / "HT")
    project, training_root = _training_paths(tmp_path)
    manifest = data.create_immutable_snapshot(
        source,
        training_root,
        snapshot_id="copy-fixture",
        dry_run=False,
        project_root=project,
    )
    final_path = training_root / "raw" / "copy-fixture"

    assert final_path.is_dir()
    assert (final_path / "tdx_day" / "sh" / "sh600000.day").is_file()
    assert (final_path / "hq_cache" / "gbbq").read_bytes() == b"gbbq-fixture"
    persisted = json.loads((final_path / "source_manifest.json").read_text(encoding="utf-8"))
    assert persisted["source_consistent"] is True
    assert all(
        row["destination_sha256"] == row["sha256"]
        for row in manifest["files"]
    )
    verified = data.verify_immutable_snapshot(
        final_path / "source_manifest.json",
        training_root=training_root,
        project_root=project,
    )
    assert verified["snapshot_id"] == "copy-fixture"
    with pytest.raises(FileExistsError):
        data.create_immutable_snapshot(
            source,
            training_root,
            snapshot_id="copy-fixture",
            dry_run=False,
            project_root=project,
        )


def test_snapshot_reuse_rejects_tampered_payload(tmp_path: Path) -> None:
    source = _make_tdx_source(tmp_path / "HT")
    project, training_root = _training_paths(tmp_path)
    data.create_immutable_snapshot(
        source,
        training_root,
        snapshot_id="tamper-fixture",
        dry_run=False,
        project_root=project,
    )
    snapshot = training_root / "raw" / "tamper-fixture"
    with (snapshot / "tdx_day" / "sh" / "sh600000.day").open("ab") as handle:
        handle.write(b"tamper")
    with pytest.raises(data.AShareDataError, match="大小漂移"):
        data.verify_immutable_snapshot(
            snapshot / "source_manifest.json",
            training_root=training_root,
            project_root=project,
        )


def test_daily_inference_snapshot_binds_market_and_all_seven_pit_tables(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture = datetime(2026, 8, 3, 16, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    now = capture.replace(hour=0)
    monkeypatch.setattr(data, "_now_shanghai", lambda: capture)
    project, training_root, source, validation = _make_inference_fixture(
        tmp_path,
        as_of=now,
    )
    pit_root = training_root / "data" / "inference-sources" / "current"
    monkeypatch.setattr(data, "validate_pit_bundle", lambda *args, **kwargs: validation)

    created = data.create_inference_snapshot(
        source,
        pit_root,
        training_root,
        as_of=now.isoformat(),
        project_root=project,
    )
    manifest_path = (
        training_root
        / "data"
        / "inference"
        / "snapshots"
        / created["snapshot_id"]
        / "inference_manifest.json"
    )
    verified = data.verify_inference_snapshot(
        manifest_path,
        training_root=training_root,
        project_root=project,
        expected_as_of=now.isoformat(),
    )

    assert verified["input_sha256"] == created["input_sha256"]
    assert verified["active_universe_count"] == 2
    assert {
        item["dataset"]
        for item in verified["pit_files"]
        if item["role"] == "pit_table"
    } == set(data.MANDATORY_PIT_TABLES)
    assert [
        item["dataset"]
        for item in verified["pit_files"]
        if item["role"] == "trading_calendar"
    ] == [data.TRADING_CALENDAR_TABLE]
    assert any(
        item["dataset"] == data.TRADING_CALENDAR_TABLE
        and item["role"] == "provenance_manifest"
        for item in verified["pit_files"]
    )
    assert any(
        item["dataset"] == data.TRADING_CALENDAR_TABLE
        and item["role"] == "raw_response"
        for item in verified["pit_files"]
    )
    assert all(
        str(item["relative_path"]).startswith("market/")
        for item in verified["market_files"]
    )


def test_daily_inference_snapshot_tamper_and_same_day_reselection_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture = datetime(2026, 8, 3, 16, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    now = capture.replace(hour=0)
    monkeypatch.setattr(data, "_now_shanghai", lambda: capture)
    project, training_root, source, validation = _make_inference_fixture(
        tmp_path,
        as_of=now,
    )
    pit_root = training_root / "data" / "inference-sources" / "current"
    monkeypatch.setattr(data, "validate_pit_bundle", lambda *args, **kwargs: validation)
    created = data.create_inference_snapshot(
        source,
        pit_root,
        training_root,
        as_of=now.isoformat(),
        project_root=project,
    )
    snapshot_root = (
        training_root / "data" / "inference" / "snapshots" / created["snapshot_id"]
    )
    market_path = snapshot_root / created["market_files"][0]["relative_path"]
    market_path.write_bytes(market_path.read_bytes() + b"tamper")
    with pytest.raises(data.AShareDataError, match="哈希漂移"):
        data.verify_inference_snapshot(
            snapshot_root / "inference_manifest.json",
            training_root=training_root,
            project_root=project,
        )

    # A corrupted prior daily snapshot also blocks a replacement; callers cannot
    # cherry-pick a second same-day input after seeing a prediction.
    with pytest.raises(data.AShareDataError):
        data.create_inference_snapshot(
            source,
            pit_root,
            training_root,
            as_of=now.isoformat(),
            project_root=project,
        )


def test_daily_inference_snapshot_requires_current_complete_pit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture = datetime(2026, 8, 3, 16, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    now = capture.replace(hour=0)
    monkeypatch.setattr(data, "_now_shanghai", lambda: capture)
    project, training_root, source, _ = _make_inference_fixture(tmp_path, as_of=now)
    pit_root = training_root / "data" / "inference-sources" / "current"
    blocked = data.PitBundleValidation(
        frames={},
        table_reports={},
        missing_tables=["coverage"],
        errors=[],
        warnings=["coverage 不完整"],
        capabilities={name: False for name in data.REQUIRED_CAPABILITIES},
    )
    monkeypatch.setattr(data, "validate_pit_bundle", lambda *args, **kwargs: blocked)
    with pytest.raises(data.PitContractError, match="production_ready"):
        data.create_inference_snapshot(
            source,
            pit_root,
            training_root,
            as_of=now.isoformat(),
            project_root=project,
        )
    assert not (training_root / "data" / "inference" / "snapshots").exists()


def test_daily_inference_snapshot_rejects_intraday_cutoff_and_preclose_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timezone_shanghai = ZoneInfo("Asia/Shanghai")
    session = datetime(2026, 8, 3, 0, 0, tzinfo=timezone_shanghai)
    project, training_root, source, validation = _make_inference_fixture(
        tmp_path,
        as_of=session,
    )
    pit_root = training_root / "data" / "inference-sources" / "current"
    monkeypatch.setattr(data, "validate_pit_bundle", lambda *args, **kwargs: validation)
    monkeypatch.setattr(
        data,
        "_now_shanghai",
        lambda: datetime(2026, 8, 3, 16, 0, tzinfo=timezone_shanghai),
    )
    with pytest.raises(data.AShareDataError, match="盘中时点不支持"):
        data.create_inference_snapshot(
            source,
            pit_root,
            training_root,
            as_of="2026-08-03T09:30:00+08:00",
            project_root=project,
        )

    monkeypatch.setattr(
        data,
        "_now_shanghai",
        lambda: datetime(2026, 8, 3, 14, 59, tzinfo=timezone_shanghai),
    )
    with pytest.raises(data.AShareDataError, match="15:00收盘后"):
        data.create_inference_snapshot(
            source,
            pit_root,
            training_root,
            as_of=session.isoformat(),
            project_root=project,
        )


def test_snapshot_aborts_and_cleans_staging_if_source_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _make_tdx_source(tmp_path / "HT")
    project, training_root = _training_paths(tmp_path)
    original_copy = shutil.copy2
    changed = False

    def mutating_copy(source_path: str | Path, destination_path: str | Path, *args: object, **kwargs: object):
        nonlocal changed
        result = original_copy(source_path, destination_path, *args, **kwargs)
        path = Path(source_path)
        if path.name == "sh600000.day" and not changed:
            path.write_bytes(path.read_bytes() + b"x")
            changed = True
        return result

    monkeypatch.setattr(data.shutil, "copy2", mutating_copy)
    with pytest.raises(data.SnapshotSourceChangedError):
        data.create_immutable_snapshot(
            source,
            training_root,
            snapshot_id="changed-fixture",
            dry_run=False,
            project_root=project,
        )

    assert not (training_root / "raw" / "changed-fixture").exists()
    assert not list((training_root / "raw").glob(".changed-fixture.pending-*"))


def test_single_member_cannot_fake_complete_csi300_or_csi500_history(tmp_path: Path) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    validation = data.validate_pit_bundle(pit_root)
    report = data.build_data_quality_report(
        _valid_manifest(), validation, _valid_adjustment_manifest()
    )

    assert validation.errors == []
    assert validation.missing_tables == []
    assert validation.production_ready is False
    assert validation.capabilities["csi300_history"] is False
    assert validation.capabilities["csi500_history"] is False
    assert validation.capabilities["security_master_history"] is False
    assert validation.capabilities["st_history"] is False
    assert validation.table_reports["security_master"]["coverage_binding"]["reason"] == (
        "missing_cryptographic_binding"
    )
    assert report["status"] == "local_provisional"
    assert "model_adjustment_manifest_unverified" in report["provisional_issues"]


def test_coverage_binding_verifies_real_table_schema_and_raw_provenance(
    tmp_path: Path,
) -> None:
    pit_root = _add_verified_coverage_bindings(
        _make_valid_pit_bundle(tmp_path / "pit")
    )
    validation = data.validate_pit_bundle(pit_root)

    assert validation.errors == []
    for dataset in data.PIT_PROVENANCE_DATASETS:
        binding = validation.table_reports[dataset]["coverage_binding"]
        assert binding["verified"] is True
        assert binding["file_sha256"] == _sha256(pit_root / f"{dataset}.csv")
        assert binding["schema_sha256"] == data.pit_table_schema_sha256(
            dataset, validation.frames[dataset]
        )
        assert binding["provenance"]["source_count"] == 1
    assert validation.capabilities["security_master_history"] is True
    assert validation.capabilities["corporate_action_history"] is True
    assert validation.production_ready is False  # one row still cannot impersonate CSI300/500


def test_coverage_binding_rejects_derived_file_or_raw_response_tamper(
    tmp_path: Path,
) -> None:
    pit_root = _add_verified_coverage_bindings(
        _make_valid_pit_bundle(tmp_path / "pit")
    )
    with (pit_root / "security_master.csv").open("a", encoding="utf-8") as handle:
        handle.write("\n")
    derived_tamper = data.validate_pit_bundle(pit_root)
    assert any(
        "security_master.coverage_binding" in error and "file_sha256" in error
        for error in derived_tamper.errors
    )

    pit_root = _add_verified_coverage_bindings(
        _make_valid_pit_bundle(tmp_path / "pit-raw")
    )
    (pit_root / "raw_responses" / "st_status.bin").write_bytes(b"tampered")
    raw_tamper = data.validate_pit_bundle(pit_root)
    assert any(
        "st_status.coverage_binding" in error and "原始响应 SHA256" in error
        for error in raw_tamper.errors
    )


def test_coverage_binding_rejects_schema_or_provenance_period_drift(
    tmp_path: Path,
) -> None:
    pit_root = _add_verified_coverage_bindings(
        _make_valid_pit_bundle(tmp_path / "pit-schema")
    )
    coverage = pd.read_csv(pit_root / "coverage.csv")
    coverage.loc[coverage["dataset"] == "price_limits", "schema_sha256"] = "0" * 64
    coverage.to_csv(pit_root / "coverage.csv", index=False)
    schema_drift = data.validate_pit_bundle(pit_root)
    assert any(
        "price_limits.coverage_binding" in error and "schema_sha256" in error
        for error in schema_drift.errors
    )

    pit_root = _add_verified_coverage_bindings(
        _make_valid_pit_bundle(tmp_path / "pit-period")
    )
    manifest_path = pit_root / "provenance" / "corporate_actions.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["coverage_start"] = "2020-01-01"
    manifest["sources"][0]["valid_from"] = "2020-01-01"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    coverage = pd.read_csv(pit_root / "coverage.csv")
    coverage.loc[
        coverage["dataset"] == "corporate_actions", "source_manifest_sha256"
    ] = _sha256(manifest_path)
    coverage.to_csv(pit_root / "coverage.csv", index=False)
    period_drift = data.validate_pit_bundle(pit_root)
    assert any(
        "corporate_actions.coverage_binding" in error and "有效期覆盖不足" in error
        for error in period_drift.errors
    )


def test_sample_trade_state_fails_closed_on_missing_status_or_raw_price(
    tmp_path: Path,
) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    suspensions = pd.read_csv(pit_root / "suspensions.csv")
    suspensions["is_suspended"] = 0
    suspensions.to_csv(pit_root / "suspensions.csv", index=False)
    _add_verified_coverage_bindings(pit_root)
    validation = data.validate_pit_bundle(pit_root)

    confirmed = data.assess_sample_trade_state(
        validation,
        "600000.SH",
        "2020-01-02",
        trade_price_raw="11.00",
        previous_close_raw="10.00",
    )
    assert confirmed["state_confirmed"] is True
    assert confirmed["eligible_for_formal_sample"] is True
    assert confirmed["listing_days"] >= 120
    assert confirmed["is_st"] is False
    assert confirmed["is_suspended"] is False
    assert confirmed["is_at_up_limit"] is True

    missing_price = data.assess_sample_trade_state(
        validation,
        "600000.SH",
        "2020-01-02",
        trade_price_raw=None,
        previous_close_raw="10.00",
    )
    assert missing_price["state_confirmed"] is False
    assert missing_price["eligible_for_formal_sample"] is False
    assert "unconfirmed_raw_price_for_limit_state" in missing_price["constraint_flags"]

    missing_previous_close = data.assess_sample_trade_state(
        validation,
        "600000.SH",
        "2020-01-02",
        trade_price_raw="11.00",
        previous_close_raw=None,
    )
    assert missing_previous_close["state_confirmed"] is False
    assert missing_previous_close["eligible_for_formal_sample"] is False
    assert "unconfirmed_previous_close_raw" in missing_previous_close["constraint_flags"]

    missing_daily_state = data.assess_sample_trade_state(
        validation,
        "600000.SH",
        "2026-08-03",
        trade_price_raw="10.00",
        previous_close_raw="10.00",
    )
    assert missing_daily_state["state_confirmed"] is False
    assert "unconfirmed_suspension_state" in missing_daily_state["constraint_flags"]
    assert "unconfirmed_price_limit_state" in missing_daily_state["constraint_flags"]


def test_calendar_primary_key_exposes_an_entire_missing_member_day(
    tmp_path: Path,
) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    missing_date = "2020-01-03"
    for table_name in ("suspensions", "price_limits"):
        frame = pd.read_csv(pit_root / f"{table_name}.csv")
        frame = frame[frame["trade_date"].astype(str) != missing_date]
        frame.to_csv(pit_root / f"{table_name}.csv", index=False)
    _add_verified_coverage_bindings(pit_root)

    validation = data.validate_pit_bundle(
        pit_root,
        coverage_start=date(2020, 1, 2),
        coverage_end=date(2020, 1, 6),
    )
    audit = validation.table_reports["sample_trade_state_audit"]

    assert audit["trade_date_count"] == 3
    assert audit["checked_member_dates"] == 3
    assert audit["missing_suspension_member_dates"] == 1
    assert audit["missing_price_limit_member_dates"] == 1
    assert any("missing_suspension_member_dates:1" in error for error in validation.errors)
    assert any("missing_price_limit_member_dates:1" in error for error in validation.errors)
    assert validation.production_ready is False
    assert validation.table_reports["trading_calendar"]["primary_key"] == [
        "trade_date"
    ]
    assert validation.table_reports["trading_calendar"]["sha256"] == _sha256(
        pit_root / "trading_calendar.csv"
    )


def test_price_limit_recalculation_mismatch_blocks_gate_and_sample(
    tmp_path: Path,
) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    limits = pd.read_csv(pit_root / "price_limits.csv")
    target = limits["trade_date"].astype(str).eq("2020-01-02")
    limits.loc[target, "previous_close_raw"] = 10.05
    limits.loc[target, "up_limit"] = 11.05  # ROUND_HALF_UP 应为 11.06
    limits.loc[target, "down_limit"] = 9.05
    limits.to_csv(pit_root / "price_limits.csv", index=False)
    suspensions = pd.read_csv(pit_root / "suspensions.csv")
    suspensions["is_suspended"] = 0
    suspensions.to_csv(pit_root / "suspensions.csv", index=False)
    _add_verified_coverage_bindings(pit_root)

    validation = data.validate_pit_bundle(
        pit_root,
        coverage_start=date(2020, 1, 2),
        coverage_end=date(2020, 1, 2),
    )
    audit = validation.table_reports["sample_trade_state_audit"]
    sample = data.assess_sample_trade_state(
        validation,
        "600000.SH",
        "2020-01-02",
        trade_price_raw="11.05",
        previous_close_raw="10.05",
    )
    gate = data.build_data_quality_report(
        _valid_manifest(),
        validation,
        _valid_adjustment_manifest(),
        model_adjustment_verified=True,
    )

    assert audit["price_limit_recalculation_checked"] == 1
    assert audit["price_limit_recalculation_mismatches"] == 1
    assert any("price_limit_recalculation_mismatches:1" in error for error in validation.errors)
    assert sample["state_confirmed"] is False
    assert sample["eligible_for_formal_sample"] is False
    assert gate["status"] == "blocked"
    assert "price_limit_recalculation_mismatch" in sample["constraint_flags"]
    assert sample["recalculated_price_limits"]["up_limit"] == "11.06"


def test_complete_pit_without_materialized_adjusted_prices_is_provisional(tmp_path: Path) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    validation = data.validate_pit_bundle(pit_root)
    report = data.build_data_quality_report(_valid_manifest(), validation)

    assert report["status"] == "local_provisional"
    assert "model_price_adjusted_not_materialized" in report["provisional_issues"]


def test_future_action_zero_count_without_verified_audit_is_blocked(tmp_path: Path) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    validation = data.validate_pit_bundle(pit_root)
    adjustment = _valid_adjustment_manifest()
    adjustment["adjustment"]["future_action_audit_verified"] = False

    report = data.build_data_quality_report(
        _valid_manifest(),
        validation,
        adjustment,
        model_adjustment_verified=True,
    )

    assert report["status"] == "blocked"
    assert any(
        issue == "invalid_model_adjustment_manifest:future_action_audit_verified=False"
        for issue in report["blocking_issues"]
    )


def test_v1_normalization_is_cryptographically_valid_but_formally_capped(
    tmp_path: Path,
) -> None:
    pit_root = _add_verified_coverage_bindings(_make_valid_pit_bundle(tmp_path / "pit"))
    coverage = pd.read_csv(pit_root / "coverage.csv")
    for dataset in data.PIT_PROVENANCE_DATASETS:
        manifest_path = pit_root / "provenance" / f"{dataset}.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["normalization"] = {
            "schema_version": data.PIT_NORMALIZATION_SCHEMA_V1
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
        )
        coverage.loc[
            coverage["dataset"] == dataset, "source_manifest_sha256"
        ] = _sha256(manifest_path)
    coverage.to_csv(pit_root / "coverage.csv", index=False)

    validation = data.validate_pit_bundle(pit_root)
    contract = validation.table_reports["normalization_release_contract"]
    assert contract["verified"] is False
    assert contract["reason"] == "normalization_v1_local_provisional_only"
    assert validation.capabilities["normalization_release_contract"] is False
    assert validation.production_ready is False


def test_unversioned_pit_bundle_cannot_enter_formal_release(tmp_path: Path) -> None:
    pit_root = _add_verified_coverage_bindings(_make_valid_pit_bundle(tmp_path / "pit"))

    validation = data.validate_pit_bundle(pit_root)

    contract = validation.table_reports["normalization_release_contract"]
    assert contract["verified"] is False
    assert contract["reason"] == "normalization_provenance_absent"
    assert contract["publication"]["present"] is False
    assert validation.capabilities["normalization_release_contract"] is False
    assert validation.production_ready is False


def test_v2_publication_requires_exact_previous_open_session(tmp_path: Path) -> None:
    root = tmp_path / "pit"
    root.mkdir()
    calendar = pd.DataFrame(
        {
            "trade_date": pd.to_datetime(["2017-12-29", "2018-01-02"]),
            "is_open": [True, True],
        }
    )
    extractor_config = {"encoding": "utf-8", "delimiter": ","}
    extractor_config_sha256 = hashlib.sha256(
        json.dumps(
            extractor_config,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    def source(source_id: str) -> dict[str, object]:
        return {
            "source_id": source_id,
            "source_class": "official_primary",
            "snapshot_manifest": str(tmp_path / "snapshot.json"),
            "format": "csv",
            "extractor_id": "csv-table-v1",
            "extractor_version": "1",
            "extractor_config": extractor_config,
            "extractor_config_sha256": extractor_config_sha256,
            "extracted_sha256": "1" * 64,
            "extracted_row_count": 1,
            "row_audit_status": "passed",
            "row_audit": {
                "schema_version": data.PIT_ROW_AUDIT_SCHEMA,
                "path": str(tmp_path / f"{source_id}-row-audit.csv"),
                "sha256": "4" * 64,
                "bytes": 1,
                "row_count": 1,
                "source_sha256": "5" * 64,
                "extracted_sha256": "1" * 64,
                "audit_status": "passed",
                "audited_at": "2026-08-03T00:00:00+00:00",
                "auditor": "unit-test-reviewer",
            },
            "mapping": {"ticker": "ticker"},
        }

    normalization = {
        "schema_version": data.PIT_NORMALIZATION_SCHEMA_V2,
        "model_coverage_start": "2018-01-02",
        "model_coverage_end": "2026-07-31",
        "evidence_lookback_start": "2017-12-29",
        "source_priority": [
            "official_primary",
            "public_secondary",
            "tdx_mechanical",
        ],
        "datasets": {},
    }
    for dataset, contract in data.V2_COVERAGE_KEY_CONTRACTS.items():
        normalization["datasets"][dataset] = {
            "coverage_key_contract": contract,
            "sources": [source(f"{dataset}-source")],
            "expected_keys": (
                source(f"{dataset}-keys") if contract == "source_bound" else None
            ),
        }
        if dataset in {"index_membership", "corporate_actions"}:
            normalization["datasets"][dataset]["completeness_receipt"] = {
                "path": str(tmp_path / f"{dataset}-receipt.json"),
                "sha256": "6" * 64,
                "bytes": 1,
            }
    normalization_path = tmp_path / "reviewed.json"
    normalization_path.write_text(json.dumps(normalization), encoding="utf-8")
    normalization_hash = _sha256(normalization_path)
    tables = {
        dataset: {
            "rows": 1,
            "sha256": "2" * 64,
            "schema_sha256": "3" * 64,
            "is_complete": True,
            "coverage_key_contract": contract,
        }
        for dataset, contract in data.V2_COVERAGE_KEY_CONTRACTS.items()
    }
    live_tables = {
        dataset: {
            "rows": 1,
            "sha256": "2" * 64,
            "schema_sha256": "3" * 64,
            "coverage_binding": {"verified": True},
        }
        for dataset in data.PIT_PROVENANCE_DATASETS
    }
    for dataset in ("index_membership", "corporate_actions"):
        live_tables[dataset]["coverage_binding"] = {
            "verified": True,
            "provenance": {
                "normalization": {
                    "completeness_receipt": {
                        "verified": True,
                        "sha256": "6" * 64,
                    }
                }
            },
        }
    payload = {
        "schema_version": data.PIT_PUBLICATION_SCHEMA_V2,
        "status": "local_provisional",
        "formal_release_allowed": True,
        "normalization_schema_version": data.PIT_NORMALIZATION_SCHEMA_V2,
        "normalization_manifest": str(normalization_path.resolve()),
        "normalization_manifest_sha256": normalization_hash,
        "source_priority": [
            "official_primary",
            "public_secondary",
            "tdx_mechanical",
        ],
        "generated_at": "2026-08-03T00:00:00+00:00",
        "tables": tables,
        "artifact_inventory": [],
        "pit_validation": {"production_ready": False},
        "model_coverage_start": "2018-01-02",
        "model_coverage_end": "2026-07-31",
        "evidence_lookback_start": "2018-01-01",
    }
    publication = root / "publication_manifest.json"
    publication.write_text(json.dumps(payload), encoding="utf-8")
    (root / "publication_manifest.sha256").write_text(
        f"{_sha256(publication)}  publication_manifest.json\n", encoding="ascii"
    )
    with pytest.raises(data.PitContractError, match="前一开放交易日"):
        data._validate_publication_manifest(
            root,
            coverage_start=data.PIT_START,
            coverage_end=data.PIT_END,
            calendar=calendar,
            table_reports=live_tables,
        )

    payload["evidence_lookback_start"] = "2017-12-29"
    publication.write_text(json.dumps(payload), encoding="utf-8")
    (root / "publication_manifest.sha256").write_text(
        f"{_sha256(publication)}  publication_manifest.json\n", encoding="ascii"
    )
    report = data._validate_publication_manifest(
        root,
        coverage_start=data.PIT_START,
        coverage_end=data.PIT_END,
        calendar=calendar,
        table_reports=live_tables,
    )
    assert report["formal_release_allowed"] is True
    assert report["evidence_lookback_start"] == "2017-12-29"
    normalization_path.write_text("{}", encoding="utf-8")
    with pytest.raises(data.PitContractError, match="SHA256 漂移"):
        data._validate_publication_manifest(
            root,
            coverage_start=data.PIT_START,
            coverage_end=data.PIT_END,
            calendar=calendar,
            table_reports=live_tables,
        )


def test_missing_st_suspension_and_csi500_remains_provisional(tmp_path: Path) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    (pit_root / "st_status.csv").unlink()
    (pit_root / "suspensions.csv").unlink()
    membership = pd.read_csv(pit_root / "index_membership.csv")
    membership[membership["index_code"] == "000300.SH"].to_csv(
        pit_root / "index_membership.csv", index=False
    )

    validation = data.validate_pit_bundle(pit_root)
    report = data.build_data_quality_report(_valid_manifest(), validation)

    assert validation.capabilities["st_history"] is False
    assert validation.capabilities["suspension_history"] is False
    assert validation.capabilities["csi500_history"] is False
    assert report["status"] == "local_provisional"
    assert "missing_pit_table:st_status" in report["provisional_issues"]
    assert "missing_capability:csi500_history" in report["provisional_issues"]


def test_malformed_pit_table_blocks_data_gate(tmp_path: Path) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    _write_csv(
        pit_root,
        "price_limits",
        [
            {
                "ticker": "600000.SH",
                "trade_date": "2020-01-02",
                "up_limit": 9.0,
                "down_limit": 11.0,
            }
        ],
    )
    validation = data.validate_pit_bundle(pit_root)
    report = data.build_data_quality_report(_valid_manifest(), validation)

    assert validation.errors
    assert report["status"] == "blocked"
    assert any(issue.startswith("pit_contract_error:") for issue in report["blocking_issues"])


def test_price_limit_rules_are_versioned_and_round_half_up() -> None:
    normal = data.calculate_price_limits(
        "10.05", date(2026, 8, 3), exchange="SH", board="main"
    )
    assert normal.up_limit == Decimal("11.06")
    assert normal.down_limit == Decimal("9.05")
    assert normal.ratio == Decimal("0.10")

    st_before = data.calculate_price_limits(
        10, date(2026, 7, 3), exchange="SZ", board="main", is_st=True
    )
    st_after = data.calculate_price_limits(
        10, date(2026, 7, 6), exchange="SZ", board="main", is_st=True
    )
    assert st_before.ratio == Decimal("0.05")
    assert st_before.rule_version == "main_st_pre_20260706_5pct"
    assert st_after.ratio == Decimal("0.10")
    assert st_after.rule_version == "main_st_from_20260706_10pct"

    chinext_before = data.calculate_price_limits(
        10, date(2020, 8, 21), exchange="SZ", board="chinext"
    )
    chinext_after = data.calculate_price_limits(
        10, date(2020, 8, 24), exchange="SZ", board="chinext"
    )
    assert chinext_before.ratio == Decimal("0.10")
    assert chinext_after.ratio == Decimal("0.20")
    assert data.calculate_price_limits(
        10, date(2026, 8, 3), exchange="BJ", board="bse"
    ).ratio == Decimal("0.30")


def test_ipo_and_explicit_exceptions_return_no_limit() -> None:
    ipo = data.calculate_price_limits(
        10,
        date(2026, 8, 3),
        exchange="SH",
        board="main",
        listing_date=date(2026, 7, 30),
        trading_day_number=3,
    )
    relisted = data.calculate_price_limits(
        10,
        date(2026, 8, 3),
        exchange="SH",
        board="main",
        no_limit_reason="relisting_first_day",
    )
    assert ipo.up_limit is None and ipo.no_limit_reason == "ipo_initial_trading_days"
    assert relisted.down_limit is None and relisted.no_limit_reason == "relisting_first_day"
    with pytest.raises(ValueError, match="不匹配"):
        data.calculate_price_limits(10, date(2026, 8, 3), exchange="SZ", board="star")


def test_split_assignments_apply_fixed_90_10_and_purge_11() -> None:
    calendar = pd.bdate_range("2017-06-01", "2026-08-31")
    assignments = data.build_split_assignments(calendar)
    contract = data.split_contract()

    assert contract["lookback"] == 90
    assert contract["horizon"] == 10
    assert contract["purge_sessions"] == 11
    assert [item["name"] for item in contract["splits"]] == [
        "train",
        "validation",
        "development_test",
        "locked_retrospective",
    ]
    positions = {timestamp: index for index, timestamp in enumerate(calendar)}
    for split in data.FIXED_SPLITS:
        segment = calendar[(calendar.date >= split.start) & (calendar.date <= split.end)]
        selected = assignments[assignments["split"] == split.name]
        assert not selected.empty
        assert selected["window_start_date"].min().date() >= split.start
        assert selected["signal_date"].max() == segment[-12]
        assert selected["label_end_date"].max().date() <= split.end
        assert positions[selected["signal_date"].min()] >= 90


def test_prepare_data_gate_can_write_guarded_report(tmp_path: Path) -> None:
    pit_root = _make_valid_pit_bundle(tmp_path / "pit")
    project, training_root = _training_paths(tmp_path)
    snapshot_manifest, token_manifest = _write_verified_adjustment_artifact(
        training_root,
        pit_root,
    )
    output = training_root / "reports" / "quality.json"
    report = data.prepare_data_gate(
        snapshot_manifest,
        pit_root,
        output_path=output,
        training_root=training_root,
        project_root=project,
        model_adjustment_manifest=token_manifest,
    )

    assert report["status"] == "local_provisional"
    assert report["model_adjustment"]["materialized"] is True
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "local_provisional"
    with pytest.raises(data.UnsafePathError):
        data.write_data_quality_report(
            tmp_path / "outside.json",
            report,
            training_root=training_root,
            project_root=project,
        )
