import importlib.util
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_leverage_dashboard_bundle.py"
SPEC = importlib.util.spec_from_file_location("build_leverage_dashboard_bundle", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_csv(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")


def write_matching_dfcf_audit(daily: Path, exchange_requests: int = 0) -> None:
    audit = {
        "dfcf_only": True,
        "exchange_requests": exchange_requests,
        "sample_status": MODULE.DFCF_STATUS,
        "dfcf_sse_margin_sha256": MODULE.sha256_file(daily / "dfcf_sse_margin.csv"),
        "dfcf_szse_margin_sha256": MODULE.sha256_file(daily / "dfcf_szse_margin.csv"),
        "dfcf_margin_balances_sha256": MODULE.sha256_file(daily / "dfcf_margin_balances.csv"),
    }
    (daily / "dfcf_margin_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False), encoding="utf-8"
    )


def write_valid_dfcf_fixture(root: Path, days: list[str], exchange_requests: int = 0) -> None:
    (root / "AGENTS.md").write_text("# fixture\n", encoding="utf-8")
    daily = root / "artifacts/leverage_capitulation/dfcf_daily"
    daily.mkdir(parents=True)
    sh_rows = [f"{day},{100 + index}\n" for index, day in enumerate(days)]
    sz_rows = [f"{day},{80 + index}\n" for index, day in enumerate(days)]
    total_rows = [
        f"{day},{100 + index},{80 + index},{180 + 2 * index},{MODULE.DFCF_STATUS}\n"
        for index, day in enumerate(days)
    ]
    write_csv(daily / "dfcf_sse_margin.csv", "date,sh_margin_y\n" + "".join(sh_rows))
    write_csv(daily / "dfcf_szse_margin.csv", "date,sz_margin_y\n" + "".join(sz_rows))
    write_csv(
        daily / "dfcf_margin_balances.csv",
        "date,sh_margin_y,sz_margin_y,total_margin_y,sample_status\n" + "".join(total_rows),
    )
    write_matching_dfcf_audit(daily, exchange_requests)


def vendor_raw_row(day: str, raw_total_market_cap: str = "120000000") -> dict[str, object]:
    return {
        "TRADE_DATE": f"{day} 00:00:00",
        "TRADE_MARKET_CODE": MODULE.EASTMONEY_MARKET_CODE,
        "TOTAL_MARKET_CAP": raw_total_market_cap,
    }


def raw_page_payload(rows: list[dict[str, object]]) -> bytes:
    return json.dumps(
        {
            "success": True,
            "result": {
                "data": rows,
                "count": len(rows),
                "pages": 1,
                "pageNum": 1,
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")


def _csv_row_from_raw(row: dict[str, object]) -> str:
    raw_total = Decimal(str(row["TOTAL_MARKET_CAP"]))
    return ",".join(
        [
            str(row["TRADE_DATE"])[:10],
            format(raw_total / Decimal("10000"), "f"),
            MODULE.EASTMONEY_SOURCE,
            str(row["TRADE_MARKET_CODE"]),
            str(row["TRADE_DATE"]),
            format(raw_total, "f"),
            "raw_divided_by_10000",
            "pass",
        ]
    )


def write_vendor_fixture(root: Path, raw_rows: list[dict[str, object]] | None = None) -> Path:
    rows = raw_rows or [vendor_raw_row("2017-01-03")]
    vendor_dir = root / MODULE.VENDOR_OUTPUT_DIRECTORY
    raw_path = vendor_dir / "raw/page-0001.json"
    raw_path.parent.mkdir(parents=True)
    raw_path.write_bytes(raw_page_payload(rows))
    table_path = vendor_dir / MODULE.VENDOR_TABLE_FILENAME
    write_csv(
        table_path,
        "date,market_cap_yi,source,source_market_code,source_trade_date,raw_total_market_cap,unit_conversion,status\n"
        + "\n".join(_csv_row_from_raw(row) for row in rows)
        + "\n",
    )
    manifest = {
        "source": MODULE.EASTMONEY_SOURCE,
        "source_url": MODULE.EASTMONEY_URL,
        "report_name": MODULE.EASTMONEY_REPORT_NAME,
        "source_market_code": MODULE.EASTMONEY_MARKET_CODE,
        "csv_sha256": MODULE.sha256_file(table_path),
        "reporting_eligible": False,
        "ratio_review_status": MODULE.EASTMONEY_REVIEW_STATUS,
        "scope_warning": MODULE.VENDOR_SCOPE_WARNING,
        "requested_start": str(rows[0]["TRADE_DATE"])[:10],
        "requested_end": str(rows[-1]["TRADE_DATE"])[:10],
        "output_records": len(rows),
        "data_range": {
            "start_date": str(rows[0]["TRADE_DATE"])[:10],
            "end_date": str(rows[-1]["TRADE_DATE"])[:10],
        },
        "pages": [
            {
                "page_number": 1,
                "relative_path": "raw/page-0001.json",
                "sha256": MODULE.sha256_file(raw_path),
                "bytes": raw_path.stat().st_size,
                "returned_rows": len(rows),
                "reported_count": len(rows),
                "reported_pages": 1,
                "request": {
                    "parameters": {
                        "reportName": MODULE.EASTMONEY_REPORT_NAME,
                        "columns": "ALL",
                        "filter": (
                            f'(TRADE_MARKET_CODE="{MODULE.EASTMONEY_MARKET_CODE}")'
                            f"(TRADE_DATE>='{str(rows[0]['TRADE_DATE'])[:10]}')"
                            f"(TRADE_DATE<='{str(rows[-1]['TRADE_DATE'])[:10]}')"
                        ),
                        "source": "WEB",
                        "client": "WEB",
                        "pageNumber": 1,
                        "pageSize": 500,
                        "sortColumns": "TRADE_DATE",
                        "sortTypes": "1",
                    },
                    "attempts": 1,
                },
            }
        ],
    }
    write_vendor_manifest(vendor_dir, manifest)
    return vendor_dir


def vendor_manifest_path(vendor_dir: Path) -> Path:
    return vendor_dir / MODULE.VENDOR_MANIFEST_FILENAME


def load_vendor_manifest(vendor_dir: Path) -> dict[str, object]:
    return json.loads(vendor_manifest_path(vendor_dir).read_text(encoding="utf-8"))


def write_vendor_manifest(vendor_dir: Path, manifest: dict[str, object]) -> None:
    vendor_manifest_path(vendor_dir).write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )


def refresh_vendor_csv_hash(vendor_dir: Path, manifest: dict[str, object]) -> None:
    manifest["csv_sha256"] = MODULE.sha256_file(vendor_dir / MODULE.VENDOR_TABLE_FILENAME)
    write_vendor_manifest(vendor_dir, manifest)


def index_frames(days: list[str]) -> dict[str, pd.DataFrame]:
    return {
        "000001": pd.DataFrame({"date": days, "close": [3000 + index for index in range(len(days))]}),
        "399106": pd.DataFrame({"date": days, "close": [10000 + index for index in range(len(days))]}),
        "399006": pd.DataFrame({"date": days, "close": [2000 + index for index in range(len(days))]}),
    }


def build_from_fixture(root: Path, days: list[str]) -> tuple[list[dict[str, object]], dict[str, object], object, object, str | None]:
    margin = MODULE.verify_dfcf_inputs(root)
    vendor, vendor_reason = MODULE.verify_post2017_vendor_inputs(root)
    records, provenance = MODULE.build_dashboard_records(
        margin.frame, vendor, index_frames(days), vendor_reason
    )
    return records, provenance, margin, vendor, vendor_reason


def test_bundle_refuses_dfcf_audit_with_exchange_requests(tmp_path: Path) -> None:
    write_valid_dfcf_fixture(tmp_path, ["2017-01-03"], exchange_requests=1)
    with pytest.raises(ValueError, match="exchange_requests"):
        MODULE.verify_dfcf_inputs(tmp_path)


def test_verify_post2017_vendor_requires_hashes_raw_pages_and_unreviewed_contract(tmp_path: Path) -> None:
    write_vendor_fixture(tmp_path)
    vendor, reason = MODULE.verify_post2017_vendor_inputs(tmp_path)
    assert reason is None
    assert vendor is not None
    assert vendor.frame["date"].tolist() == ["2017-01-03"]
    assert vendor.frame["market_cap_yi"].tolist() == ["12000"]
    assert vendor.manifest["reporting_eligible"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        "csv_hash",
        "page_hash",
        "page_path",
        "review_status",
        "reporting_eligible",
        "csv_market_code",
        "raw_market_code",
        "raw_page_number",
        "request_page_number",
        "nonpass",
        "duplicate",
        "descending",
        "negative",
        "nan",
        "source_date_mismatch",
        "missing_scope_warning",
    ],
)
def test_bad_vendor_inputs_disable_every_ratio_without_fallback(tmp_path: Path, mutation: str) -> None:
    days = ["2016-12-30", "2017-01-03", "2017-01-04"]
    write_valid_dfcf_fixture(tmp_path, days)
    raw_rows = (
        [vendor_raw_row("2017-01-03"), vendor_raw_row("2017-01-04", "121000000")]
        if mutation == "descending"
        else None
    )
    vendor_dir = write_vendor_fixture(tmp_path, raw_rows)
    manifest = load_vendor_manifest(vendor_dir)
    table_path = vendor_dir / MODULE.VENDOR_TABLE_FILENAME

    if mutation == "csv_hash":
        manifest["csv_sha256"] = "0" * 64
    elif mutation == "page_hash":
        manifest["pages"][0]["sha256"] = "0" * 64
    elif mutation == "page_path":
        manifest["pages"][0]["relative_path"] = "raw/other.json"
    elif mutation == "review_status":
        manifest["ratio_review_status"] = "strict_audited"
    elif mutation == "reporting_eligible":
        manifest["reporting_eligible"] = True
    elif mutation == "csv_market_code":
        table_path.write_text(
            table_path.read_text(encoding="utf-8").replace(",000300,", ",000301,"),
            encoding="utf-8",
        )
        refresh_vendor_csv_hash(vendor_dir, manifest)
        manifest = load_vendor_manifest(vendor_dir)
    elif mutation == "raw_market_code":
        raw_path = vendor_dir / "raw/page-0001.json"
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        raw["result"]["data"][0]["TRADE_MARKET_CODE"] = "000301"
        raw_path.write_text(json.dumps(raw), encoding="utf-8")
        manifest["pages"][0]["sha256"] = MODULE.sha256_file(raw_path)
        manifest["pages"][0]["bytes"] = raw_path.stat().st_size
    elif mutation == "raw_page_number":
        raw_path = vendor_dir / "raw/page-0001.json"
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        raw["result"]["pageNum"] = 2
        raw_path.write_text(json.dumps(raw), encoding="utf-8")
        manifest["pages"][0]["sha256"] = MODULE.sha256_file(raw_path)
        manifest["pages"][0]["bytes"] = raw_path.stat().st_size
    elif mutation == "request_page_number":
        manifest["pages"][0]["request"]["parameters"]["pageNumber"] = 2
    elif mutation == "nonpass":
        table_path.write_text(table_path.read_text(encoding="utf-8").replace(",pass\n", ",failed\n"), encoding="utf-8")
        refresh_vendor_csv_hash(vendor_dir, manifest)
        manifest = load_vendor_manifest(vendor_dir)
    elif mutation == "duplicate":
        lines = table_path.read_text(encoding="utf-8").splitlines()
        table_path.write_text("\n".join(lines + [lines[1]]) + "\n", encoding="utf-8")
        refresh_vendor_csv_hash(vendor_dir, manifest)
        manifest = load_vendor_manifest(vendor_dir)
    elif mutation == "descending":
        lines = table_path.read_text(encoding="utf-8").splitlines()
        table_path.write_text("\n".join([lines[0], lines[2], lines[1]]) + "\n", encoding="utf-8")
        refresh_vendor_csv_hash(vendor_dir, manifest)
        manifest = load_vendor_manifest(vendor_dir)
    elif mutation in {"negative", "nan"}:
        replacement = "-1" if mutation == "negative" else "NaN"
        lines = table_path.read_text(encoding="utf-8").splitlines()
        fields = lines[1].split(",")
        fields[1] = replacement
        lines[1] = ",".join(fields)
        table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        refresh_vendor_csv_hash(vendor_dir, manifest)
        manifest = load_vendor_manifest(vendor_dir)
    elif mutation == "source_date_mismatch":
        lines = table_path.read_text(encoding="utf-8").splitlines()
        fields = lines[1].split(",")
        fields[4] = "2017-01-04 00:00:00"
        lines[1] = ",".join(fields)
        table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        refresh_vendor_csv_hash(vendor_dir, manifest)
        manifest = load_vendor_manifest(vendor_dir)
    elif mutation == "missing_scope_warning":
        manifest["scope_warning"] = ""

    write_vendor_manifest(vendor_dir, manifest)
    records, provenance, _, vendor, reason = build_from_fixture(tmp_path, days)
    assert vendor is None
    assert isinstance(reason, str) and re.search(r"[\u4e00-\u9fff]", reason)
    assert provenance["ratio_available"] is False
    assert all(record["ratio_pct"] is None for record in records)
    assert all(record["denominator_market_cap_yi"] is None for record in records)


def test_records_force_pre2017_na_and_exact_post2017_vendor_join_only(tmp_path: Path) -> None:
    days = ["2016-12-30", "2017-01-03", "2017-01-04"]
    write_valid_dfcf_fixture(tmp_path, days)
    write_vendor_fixture(tmp_path, [vendor_raw_row("2017-01-03")])
    records, provenance, _, vendor, reason = build_from_fixture(tmp_path, days)
    assert vendor is not None and reason is None
    assert [record["date"] for record in records] == days
    expected_fields = {
        "date",
        "sh_margin_yi",
        "sz_margin_yi",
        "total_margin_yi",
        "denominator_market_cap_yi",
        "market_cap_source",
        "market_cap_review_status",
        "ratio_pct",
        "index_000001_close",
        "index_399106_close",
        "index_399006_close",
    }
    assert set(records[0]) == expected_fields
    assert not {"sh_a_market_cap_yi", "sz_a_market_cap_yi", "sh_sz_a_market_cap_yi"} & set(records[0])
    assert records[0]["denominator_market_cap_yi"] is None
    assert records[0]["market_cap_source"] == "pre2017_official_pending"
    assert records[0]["market_cap_review_status"] == "unavailable"
    assert records[0]["ratio_pct"] is None
    assert records[1]["denominator_market_cap_yi"] == 12000.0
    assert records[1]["market_cap_source"] == "eastmoney_post2017_vendor_unverified"
    assert records[1]["market_cap_review_status"] == "eastmoney_vendor_unverified"
    assert Decimal(str(records[1]["ratio_pct"])) == Decimal("1.51666667")
    assert records[2]["denominator_market_cap_yi"] is None
    assert records[2]["market_cap_source"] == "eastmoney_post2017_vendor_unverified"
    assert records[2]["market_cap_review_status"] == "unavailable"
    assert records[2]["ratio_pct"] is None
    assert provenance["ratio_available"] is True
    assert provenance["ratio_data_range"] == {"start": "2017-01-03", "end": "2017-01-03"}
    assert provenance["source_switch_date"] == "2017-01-03"


def test_vendor_dates_outside_dfcf_backbone_never_create_output_record(tmp_path: Path) -> None:
    days = ["2016-12-30", "2017-01-03"]
    write_valid_dfcf_fixture(tmp_path, days)
    write_vendor_fixture(tmp_path, [vendor_raw_row("2017-01-05")])
    records, provenance, _, vendor, reason = build_from_fixture(tmp_path, days)
    assert vendor is not None and reason is None
    assert [record["date"] for record in records] == days
    assert all(record["ratio_pct"] is None for record in records)
    assert provenance["ratio_available"] is False


def test_missing_vendor_never_falls_back_to_old_strict_or_full_a_inputs(tmp_path: Path) -> None:
    days = ["2016-12-30", "2017-01-03"]
    write_valid_dfcf_fixture(tmp_path, days)
    old_dir = tmp_path / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
    old_dir.mkdir(parents=True)
    write_csv(
        old_dir / "sh_sz_a_share_market_cap.csv",
        "date,sh_a_market_cap_yi,sz_a_market_cap_yi,sh_sz_a_market_cap_yi,scope_status\n"
        "2017-01-03,1,1,2,pass\n",
    )
    records, provenance, _, vendor, reason = build_from_fixture(tmp_path, days)
    assert vendor is None and isinstance(reason, str)
    assert provenance["ratio_available"] is False
    assert [record["ratio_pct"] for record in records] == [None, None]


def test_payload_manifest_schema_hash_and_atomic_publish_are_consistent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    days = ["2016-12-30", "2017-01-03", "2017-01-04"]
    write_valid_dfcf_fixture(tmp_path, days)
    write_vendor_fixture(tmp_path, [vendor_raw_row("2017-01-03")])
    records, provenance, margin, vendor, vendor_reason = build_from_fixture(tmp_path, days)
    metadata = {
        ticker: {
            "source": "本地TDX厂商日线",
            "path": f"fixture/{ticker}.day",
            "sha256": "a" * 64,
            "first_date": days[0],
            "last_date": days[-1],
        }
        for ticker in MODULE.INDEX_PATHS
    }
    payload = MODULE.build_payload(records, provenance)
    manifest = MODULE.build_manifest(records, provenance, margin, vendor, vendor_reason, metadata)
    artifact_dir = tmp_path / "artifact"
    payload_path, manifest_path = MODULE.write_bundle(artifact_dir, payload, manifest)
    parsed_payload = json.loads(payload_path.read_text(encoding="utf-8"))
    parsed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert {"schema_version", "generated_at_beijing", "records", "provenance"} <= set(parsed_payload)
    assert parsed_payload["provenance"]["ratio_available"] is True
    assert parsed_manifest["payload_sha256"] == MODULE.sha256_file(payload_path)
    assert parsed_manifest["payload_records"] == 3
    assert parsed_manifest["data_range"] == {"start": "2016-12-30", "end": "2017-01-04"}
    assert parsed_manifest["dfcf"]["dfcf_only"] is True
    assert parsed_manifest["dfcf"]["exchange_requests"] == 0
    assert parsed_manifest["market_cap"]["reporting_eligible"] is False
    assert parsed_manifest["market_cap"]["ratio_review_status"] == (
        "mixed_pre2017_pending_eastmoney_vendor_unverified"
    )
    assert parsed_manifest["market_cap"]["ratio_missing_records"] == 2
    assert len(parsed_manifest["market_cap"]["source_segments"]) == 2

    publish_dir = tmp_path / "public/data"
    monkeypatch.setattr(MODULE, "PUBLISH_DIRECTORY", publish_dir)
    MODULE.publish_bundle_atomically(payload_path, manifest_path, publish_dir)
    assert (publish_dir / payload_path.name).read_bytes() == payload_path.read_bytes()
    assert (publish_dir / manifest_path.name).read_bytes() == manifest_path.read_bytes()


def test_publish_rolls_back_payload_if_manifest_commit_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publish_dir = tmp_path / "public/data"
    monkeypatch.setattr(MODULE, "PUBLISH_DIRECTORY", publish_dir)
    old_payload = {"schema_version": "1", "records": [], "provenance": {}}
    old_manifest = {"schema_version": "1", "payload_records": 0}
    old_payload_path, old_manifest_path = MODULE.write_bundle(publish_dir, old_payload, old_manifest)
    original_payload = old_payload_path.read_bytes()
    original_manifest = old_manifest_path.read_bytes()

    new_payload = {"schema_version": "1", "records": [{"date": "2017-01-03"}], "provenance": {}}
    new_manifest = {"schema_version": "1", "payload_records": 1}
    artifact_dir = tmp_path / "artifact"
    payload_path, manifest_path = MODULE.write_bundle(artifact_dir, new_payload, new_manifest)
    real_atomic_write = MODULE._atomic_write_bytes
    failed = False

    def fail_once_on_manifest(payload: bytes, path: Path) -> None:
        nonlocal failed
        if path == publish_dir / manifest_path.name and not failed:
            failed = True
            raise OSError("injected manifest replace failure")
        real_atomic_write(payload, path)

    monkeypatch.setattr(MODULE, "_atomic_write_bytes", fail_once_on_manifest)
    with pytest.raises(OSError, match="injected manifest"):
        MODULE.publish_bundle_atomically(payload_path, manifest_path, publish_dir)

    assert failed is True
    assert old_payload_path.read_bytes() == original_payload
    assert old_manifest_path.read_bytes() == original_manifest
    MODULE._verify_artifact_bundle(old_payload_path, old_manifest_path)


def test_publish_accepts_verified_legacy_row_count_pair_for_first_schema_upgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publish_dir = tmp_path / "public/data"
    publish_dir.mkdir(parents=True)
    monkeypatch.setattr(MODULE, "PUBLISH_DIRECTORY", publish_dir)
    legacy_payload_path = publish_dir / "leverage-dashboard.json"
    legacy_manifest_path = publish_dir / "leverage-dashboard.manifest.json"
    legacy_payload = {"records": [{"date": "2016-12-30"}]}
    legacy_payload_path.write_bytes(MODULE._json_bytes(legacy_payload))
    legacy_manifest_path.write_bytes(
        MODULE._json_bytes(
            {
                "payload_sha256": MODULE.sha256_file(legacy_payload_path),
                "row_count": 1,
            }
        )
    )

    new_payload = {"schema_version": "1", "records": [{"date": "2017-01-03"}], "provenance": {}}
    new_manifest = {"schema_version": "1", "payload_records": 1}
    artifact_dir = tmp_path / "artifact"
    payload_path, manifest_path = MODULE.write_bundle(artifact_dir, new_payload, new_manifest)
    MODULE.publish_bundle_atomically(payload_path, manifest_path, publish_dir)

    published_manifest = json.loads(legacy_manifest_path.read_text(encoding="utf-8"))
    assert published_manifest["payload_records"] == 1
    assert "row_count" not in published_manifest
    MODULE._verify_artifact_bundle(legacy_payload_path, legacy_manifest_path)


def test_main_rejects_removed_output_dir_override_before_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    days = ["2016-12-30", "2017-01-03", "2017-01-04"]
    write_valid_dfcf_fixture(tmp_path, days)
    write_vendor_fixture(tmp_path, [vendor_raw_row("2017-01-03")])
    metadata = {
        ticker: {
            "source": "fixture",
            "path": f"fixture/{ticker}.day",
            "sha256": "a" * 64,
            "first_date": days[0],
            "last_date": days[-1],
        }
        for ticker in MODULE.INDEX_PATHS
    }
    monkeypatch.setattr(MODULE, "_load_indices", lambda: (index_frames(days), metadata))
    forbidden_output_dir = tmp_path / "outside-dashboard-bundle"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_leverage_dashboard_bundle.py",
            "--project-root",
            str(tmp_path),
            "--output-dir",
            str(forbidden_output_dir),
        ],
    )

    with pytest.raises(SystemExit) as raised:
        MODULE.main()

    assert raised.value.code == 2
    assert "unrecognized arguments: --output-dir" in capsys.readouterr().err
    assert not forbidden_output_dir.exists()
    assert not (tmp_path / MODULE.OUTPUT_DIRECTORY).exists()


def test_main_prints_valid_manifest_after_decimal_audit_parse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    days = ["2016-12-30", "2017-01-03", "2017-01-04"]
    write_valid_dfcf_fixture(tmp_path, days)
    write_vendor_fixture(tmp_path, [vendor_raw_row("2017-01-03")])
    metadata = {
        ticker: {
            "source": "fixture",
            "path": f"fixture/{ticker}.day",
            "sha256": "a" * 64,
            "first_date": days[0],
            "last_date": days[-1],
        }
        for ticker in MODULE.INDEX_PATHS
    }
    monkeypatch.setattr(MODULE, "_load_indices", lambda: (index_frames(days), metadata))
    output_dir = tmp_path / MODULE.OUTPUT_DIRECTORY
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_leverage_dashboard_bundle.py",
            "--project-root",
            str(tmp_path),
        ],
    )

    MODULE.main()

    printed = json.loads(capsys.readouterr().out)
    assert printed["schema_version"] == "1"
    assert printed["payload_records"] == 3
    assert printed["payload_sha256"] == MODULE.sha256_file(output_dir / "leverage-dashboard.json")
