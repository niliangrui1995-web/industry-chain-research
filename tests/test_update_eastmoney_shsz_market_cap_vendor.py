import csv
import importlib.util
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "update_eastmoney_shsz_market_cap_vendor.py"
)
SPEC = importlib.util.spec_from_file_location(
    "update_eastmoney_shsz_market_cap_vendor", SCRIPT_PATH
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, payload: bytes, status_code: int = 200) -> None:
        self.content = payload
        self.status_code = status_code


class FakeSession:
    def __init__(self, pages: dict[int, FakeResponse]) -> None:
        self.pages = pages
        self.calls: list[dict[str, object]] = []

    def get(self, url: str, *, params: dict[str, object], headers: dict[str, str], timeout: int) -> FakeResponse:
        del headers, timeout
        self.calls.append({"url": url, "params": dict(params)})
        return self.pages[int(params["pageNumber"])]


def vendor_payload(
    rows: list[dict[str, object]],
    *,
    page_number: int = 1,
    pages: int = 1,
    count: int | None = None,
    success: bool = True,
) -> bytes:
    return json.dumps(
        {
            "success": success,
            "result": {
                "data": rows,
                "count": len(rows) if count is None else count,
                "pages": pages,
                "pageNum": page_number,
                "pageSize": 500,
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")


def row(day: str, cap: str = "11513579024.5431", market: str = "000300") -> dict[str, object]:
    return {
        "TRADE_DATE": f"{day} 00:00:00",
        "TRADE_MARKET_CODE": market,
        "TOTAL_MARKET_CAP": cap,
    }


def write_dfcf_dates(root: Path, days: list[str]) -> None:
    (root / "AGENTS.md").write_text("# fixture\n", encoding="utf-8")
    daily = root / "artifacts/leverage_capitulation/dfcf_daily"
    daily.mkdir(parents=True)
    daily.joinpath("dfcf_margin_balances.csv").write_text(
        "date\n" + "".join(f"{day}\n" for day in days), encoding="utf-8"
    )


def test_decimal_to_yi_preserves_exact_decimal_conversion() -> None:
    assert MODULE.decimal_to_yi("11513579024.5431") == Decimal("1151357.90245431")


def test_parse_page_rejects_unsuccessful_response() -> None:
    with pytest.raises(ValueError, match="success"):
        MODULE.parse_page_payload(
            vendor_payload([row("2017-01-03")], success=False),
            expected_page_number=1,
            requested_start=date(2017, 1, 3),
            requested_end=date(2017, 1, 3),
        )


def test_parse_page_rejects_unknown_market_code() -> None:
    with pytest.raises(ValueError, match="TRADE_MARKET_CODE"):
        MODULE.parse_page_payload(
            vendor_payload([row("2017-01-03", market="000301")]),
            expected_page_number=1,
            requested_start=date(2017, 1, 3),
            requested_end=date(2017, 1, 3),
        )


def test_parse_page_rejects_nonpositive_market_cap() -> None:
    with pytest.raises(ValueError, match="TOTAL_MARKET_CAP"):
        MODULE.parse_page_payload(
            vendor_payload([row("2017-01-03", cap="0")]),
            expected_page_number=1,
            requested_start=date(2017, 1, 3),
            requested_end=date(2017, 1, 3),
        )


def test_validate_vendor_records_rejects_duplicate_and_nonascending_dates() -> None:
    first = MODULE.VendorRecord(
        trade_date=date(2017, 1, 3),
        source_trade_date="2017-01-03 00:00:00",
        raw_total_market_cap=Decimal("10000"),
        market_cap_yi=Decimal("1"),
    )
    duplicate = MODULE.VendorRecord(
        trade_date=date(2017, 1, 3),
        source_trade_date="2017-01-03 00:00:00",
        raw_total_market_cap=Decimal("10001"),
        market_cap_yi=Decimal("1.0001"),
    )
    with pytest.raises(ValueError, match="唯一且升序"):
        MODULE.validate_vendor_records([first, duplicate])
    descending = MODULE.VendorRecord(
        trade_date=date(2017, 1, 2),
        source_trade_date="2017-01-02 00:00:00",
        raw_total_market_cap=Decimal("9999"),
        market_cap_yi=Decimal("0.9999"),
    )
    with pytest.raises(ValueError, match="唯一且升序"):
        MODULE.validate_vendor_records([first, descending])


def test_update_writes_only_exact_dfcf_dates_with_raw_hash_manifest(tmp_path: Path) -> None:
    write_dfcf_dates(tmp_path, ["2016-12-30", "2017-01-03", "2017-01-05"])
    session = FakeSession(
        {
            1: FakeResponse(
                vendor_payload(
                    [row("2017-01-03")], page_number=1, pages=2, count=3
                )
            ),
            2: FakeResponse(
                vendor_payload(
                    [row("2017-01-04"), row("2017-01-05")],
                    page_number=2,
                    pages=2,
                    count=3,
                )
            ),
        }
    )
    requested = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 3), date(2017, 1, 5)
    )

    result = MODULE.update_vendor_market_cap(
        tmp_path,
        requested,
        MODULE.UpdateOptions(
            session=session,
            page_size=500,
            timeout_seconds=1,
            max_retries=0,
            sleep_seconds=0,
        ),
    )

    output_dir = tmp_path / MODULE.OUTPUT_DIRECTORY
    table = output_dir / MODULE.TABLE_FILENAME
    manifest_path = output_dir / MODULE.MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert result["network_requests"] == 2
    assert [call["params"]["pageNumber"] for call in session.calls] == [1, 2]
    assert session.calls[0]["params"]["filter"] == (
        '(TRADE_MARKET_CODE="000300")(TRADE_DATE>=\'2017-01-03\')'
        '(TRADE_DATE<=\'2017-01-05\')'
    )
    assert table.read_text(encoding="utf-8").splitlines()[1:] == [
        "2017-01-03,1151357.90245431,东方财富Choice厂商数据,000300,2017-01-03 00:00:00,11513579024.5431,raw_divided_by_10000,pass",
        "2017-01-05,1151357.90245431,东方财富Choice厂商数据,000300,2017-01-05 00:00:00,11513579024.5431,raw_divided_by_10000,pass",
    ]
    assert manifest["csv_sha256"] == MODULE.sha256_file(table)
    assert manifest["reporting_eligible"] is False
    assert manifest["ratio_review_status"] == "eastmoney_vendor_unverified"
    assert manifest["missing_dfcf_common_dates"] == []
    assert manifest["returned_non_dfcf_dates"] == ["2017-01-04"]
    assert len(manifest["pages"]) == 2
    for page in manifest["pages"]:
        raw_path = output_dir / str(page["relative_path"])
        assert raw_path.exists()
        assert page["sha256"] == MODULE.sha256_file(raw_path)


def test_update_records_missing_dfcf_dates_without_filling_them(tmp_path: Path) -> None:
    write_dfcf_dates(tmp_path, ["2017-01-03", "2017-01-04"])
    session = FakeSession(
        {
            1: FakeResponse(
                vendor_payload([row("2017-01-03")], page_number=1, pages=1, count=1)
            )
        }
    )
    requested = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 3), date(2017, 1, 4)
    )

    MODULE.update_vendor_market_cap(
        tmp_path,
        requested,
        MODULE.UpdateOptions(
            session=session,
            page_size=500,
            timeout_seconds=1,
            max_retries=0,
            sleep_seconds=0,
        ),
    )

    output_dir = tmp_path / MODULE.OUTPUT_DIRECTORY
    manifest = json.loads(
        (output_dir / MODULE.MANIFEST_FILENAME).read_text(encoding="utf-8")
    )
    rows = (output_dir / MODULE.TABLE_FILENAME).read_text(encoding="utf-8").splitlines()
    assert len(rows) == 2
    assert manifest["missing_dfcf_common_dates"] == ["2017-01-04"]


def test_incremental_update_preserves_baseline_and_replaces_refreshed_date(tmp_path: Path) -> None:
    write_dfcf_dates(tmp_path, ["2017-01-03", "2017-01-04", "2017-01-05"])
    options = {
        "page_size": 500,
        "timeout_seconds": 1,
        "max_retries": 0,
        "sleep_seconds": 0,
    }
    baseline_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 3), date(2017, 1, 4)
    )
    MODULE.update_vendor_market_cap(
        tmp_path,
        baseline_dates,
        MODULE.UpdateOptions(
            session=FakeSession(
                {
                    1: FakeResponse(
                        vendor_payload(
                            [
                                row("2017-01-03", cap="10000"),
                                row("2017-01-04", cap="20000"),
                            ]
                        )
                    )
                }
            ),
            **options,
        ),
    )

    refreshed_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 4), date(2017, 1, 5)
    )
    result = MODULE.update_vendor_market_cap(
        tmp_path,
        refreshed_dates,
        MODULE.UpdateOptions(
            session=FakeSession(
                {
                    1: FakeResponse(
                        vendor_payload(
                            [
                                row("2017-01-04", cap="22000"),
                                row("2017-01-05", cap="30000"),
                            ]
                        )
                    )
                }
            ),
            **options,
        ),
        incremental=True,
    )

    output_dir = tmp_path / MODULE.OUTPUT_DIRECTORY
    rows = list(csv.DictReader((output_dir / MODULE.TABLE_FILENAME).open(encoding="utf-8")))
    manifest = json.loads((output_dir / MODULE.MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert result["incremental"] is True
    assert [row["date"] for row in rows] == ["2017-01-03", "2017-01-04", "2017-01-05"]
    assert [row["raw_total_market_cap"] for row in rows] == ["10000", "22000", "30000"]
    assert manifest["manifest_version"] == 2
    assert len(manifest["batches"]) == 2
    assert manifest["batches"][0]["raw_directory"] == "raw"
    assert manifest["batches"][1]["requested_start"] == "2017-01-04"
    assert manifest["revision_summary"]["revised_dates"] == ["2017-01-04"]


def test_incremental_update_removes_stale_row_when_refreshed_vendor_response_omits_dfcf_day(
    tmp_path: Path,
) -> None:
    write_dfcf_dates(tmp_path, ["2017-01-03", "2017-01-04", "2017-01-05"])
    options = {
        "page_size": 500,
        "timeout_seconds": 1,
        "max_retries": 0,
        "sleep_seconds": 0,
    }
    baseline_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 3), date(2017, 1, 5)
    )
    MODULE.update_vendor_market_cap(
        tmp_path,
        baseline_dates,
        MODULE.UpdateOptions(
            session=FakeSession(
                {
                    1: FakeResponse(
                        vendor_payload(
                            [
                                row("2017-01-03", cap="10000"),
                                row("2017-01-04", cap="20000"),
                                row("2017-01-05", cap="30000"),
                            ]
                        )
                    )
                }
            ),
            **options,
        ),
    )

    refreshed_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 4), date(2017, 1, 5)
    )
    MODULE.update_vendor_market_cap(
        tmp_path,
        refreshed_dates,
        MODULE.UpdateOptions(
            session=FakeSession(
                {1: FakeResponse(vendor_payload([row("2017-01-05", cap="31000")]))}
            ),
            **options,
        ),
        incremental=True,
    )

    output_dir = tmp_path / MODULE.OUTPUT_DIRECTORY
    rows = list(csv.DictReader((output_dir / MODULE.TABLE_FILENAME).open(encoding="utf-8")))
    manifest = json.loads((output_dir / MODULE.MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert [row["date"] for row in rows] == ["2017-01-03", "2017-01-05"]
    assert manifest["missing_dfcf_common_dates"] == ["2017-01-04"]
    assert manifest["active_missing_dfcf_common_dates"] == ["2017-01-04"]
    assert manifest["revision_summary"]["withdrawn_dfcf_dates"] == ["2017-01-04"]


def test_incremental_update_refuses_to_merge_when_existing_manifest_csv_hash_is_invalid(
    tmp_path: Path,
) -> None:
    write_dfcf_dates(tmp_path, ["2017-01-03", "2017-01-04"])
    options = {
        "page_size": 500,
        "timeout_seconds": 1,
        "max_retries": 0,
        "sleep_seconds": 0,
    }
    baseline_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 3), date(2017, 1, 3)
    )
    MODULE.update_vendor_market_cap(
        tmp_path,
        baseline_dates,
        MODULE.UpdateOptions(
            session=FakeSession(
                {1: FakeResponse(vendor_payload([row("2017-01-03", cap="10000")]))}
            ),
            **options,
        ),
    )
    output_dir = tmp_path / MODULE.OUTPUT_DIRECTORY
    table_path = output_dir / MODULE.TABLE_FILENAME
    manifest_path = output_dir / MODULE.MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["csv_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    before_table = table_path.read_bytes()
    before_manifest = manifest_path.read_bytes()

    refreshed_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 4), date(2017, 1, 4)
    )
    with pytest.raises(ValueError, match="CSV SHA-256"):
        MODULE.update_vendor_market_cap(
            tmp_path,
            refreshed_dates,
            MODULE.UpdateOptions(
                session=FakeSession(
                    {1: FakeResponse(vendor_payload([row("2017-01-04", cap="20000")]))}
                ),
                **options,
            ),
            incremental=True,
        )

    assert table_path.read_bytes() == before_table
    assert manifest_path.read_bytes() == before_manifest
    assert not (output_dir / "raw/batches").exists()


def test_incremental_update_refuses_to_merge_when_existing_manifest_output_records_is_invalid(
    tmp_path: Path,
) -> None:
    write_dfcf_dates(tmp_path, ["2017-01-03", "2017-01-04"])
    options = {
        "page_size": 500,
        "timeout_seconds": 1,
        "max_retries": 0,
        "sleep_seconds": 0,
    }
    baseline_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 3), date(2017, 1, 3)
    )
    MODULE.update_vendor_market_cap(
        tmp_path,
        baseline_dates,
        MODULE.UpdateOptions(
            session=FakeSession(
                {1: FakeResponse(vendor_payload([row("2017-01-03", cap="10000")]))}
            ),
            **options,
        ),
    )
    output_dir = tmp_path / MODULE.OUTPUT_DIRECTORY
    table_path = output_dir / MODULE.TABLE_FILENAME
    manifest_path = output_dir / MODULE.MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["output_records"] = 2
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    before_table = table_path.read_bytes()
    before_manifest = manifest_path.read_bytes()

    refreshed_dates = MODULE.load_dfcf_post2017_common_dates(
        tmp_path, date(2017, 1, 4), date(2017, 1, 4)
    )
    with pytest.raises(ValueError, match="output_records"):
        MODULE.update_vendor_market_cap(
            tmp_path,
            refreshed_dates,
            MODULE.UpdateOptions(
                session=FakeSession(
                    {1: FakeResponse(vendor_payload([row("2017-01-04", cap="20000")]))}
                ),
                **options,
            ),
            incremental=True,
        )

    assert table_path.read_bytes() == before_table
    assert manifest_path.read_bytes() == before_manifest
    assert not (output_dir / "raw/batches").exists()


def test_load_dfcf_dates_refuses_to_touch_pre2017_range(tmp_path: Path) -> None:
    write_dfcf_dates(tmp_path, ["2016-12-30", "2017-01-03"])
    with pytest.raises(ValueError, match="2017-01-03"):
        MODULE.load_dfcf_post2017_common_dates(
            tmp_path, date(2016, 12, 30), date(2017, 1, 3)
        )


def test_cli_dry_run_makes_zero_http_requests_and_writes_no_vendor_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    write_dfcf_dates(tmp_path, ["2017-01-03", "2017-01-04"])
    calls = 0

    def forbidden_session() -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("dry-run must not create an HTTP session")

    monkeypatch.setattr(MODULE.requests, "Session", forbidden_session)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "update_eastmoney_shsz_market_cap_vendor.py",
            "--project-root",
            str(tmp_path),
            "--start-date",
            "2017-01-03",
            "--end-date",
            "2017-01-04",
            "--bootstrap-full",
            "--dry-run",
        ],
    )

    MODULE.main()

    result = json.loads(capsys.readouterr().out)
    assert calls == 0
    assert result["dry_run"] is True
    assert result["incremental"] is False
    assert result["requested_dates"] == 2
    assert not (tmp_path / MODULE.OUTPUT_DIRECTORY).exists()


def test_cli_mode_defaults_to_incremental_for_complete_existing_state(tmp_path: Path) -> None:
    output = tmp_path / MODULE.OUTPUT_DIRECTORY
    output.mkdir(parents=True)
    (output / MODULE.TABLE_FILENAME).write_text("date\n2017-01-03\n", encoding="utf-8")
    (output / MODULE.MANIFEST_FILENAME).write_text("{}\n", encoding="utf-8")

    assert MODULE.resolve_cli_incremental_mode(
        output, bootstrap_full=False, incremental_requested=False
    ) is True


def test_cli_mode_rejects_implicit_full_bootstrap_and_incomplete_state(tmp_path: Path) -> None:
    output = tmp_path / MODULE.OUTPUT_DIRECTORY

    with pytest.raises(ValueError, match="显式传入 --bootstrap-full"):
        MODULE.resolve_cli_incremental_mode(
            output, bootstrap_full=False, incremental_requested=False
        )

    output.mkdir(parents=True)
    (output / MODULE.TABLE_FILENAME).write_text("date\n2017-01-03\n", encoding="utf-8")
    with pytest.raises(ValueError, match="必须同时存在"):
        MODULE.resolve_cli_incremental_mode(
            output, bootstrap_full=False, incremental_requested=True
        )
