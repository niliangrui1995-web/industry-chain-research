import hashlib
from datetime import date
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import sys

from decimal import Decimal

from openpyxl import Workbook
import pandas as pd
import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "build_official_pre2017_market_cap.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("official_pre2017_market_cap", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sse_payload(rows):
    return json.dumps({"result": rows}, ensure_ascii=False).encode("utf-8")


def sse_row(product_type, amount, trade_date="2011-08-03"):
    return {
        "CAL_DATE": trade_date,
        "PRODUCT_TYPE": product_type,
        "MKT_VALUE_FULL": amount,
    }


def valid_sse_payload(trade_date="2011-08-03"):
    return sse_payload(
        [
            sse_row("1", "100.25", trade_date),
            sse_row("2", "10.50", trade_date),
            sse_row("48", "20.00", trade_date),
            sse_row("40", "130.75", trade_date),
            sse_row("43", "1.00", trade_date),
        ]
    )


def szse_workbook_bytes(*, historical=True):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["证券类别", "数量(只)", "成交金额(元)", "总市值(元)", "流通市值(元)"])
    suffix = "" if historical else "A股"
    sheet.append([f"主板A股", 1, 0, "10000000000", 0])
    sheet.append([f"中小板{suffix}", 1, 0, "200000000", 0])
    sheet.append([f"创业板{suffix}", 1, 0, "300000000", 0])
    sheet.append(["主板B股", 1, 0, "999999999", 0])
    sheet.append(["基金", 1, 0, "999999999", 0])
    sheet.append(["债券", 1, 0, "999999999", 0])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.content = payload
        self.status_code = status_code


class FakeSession:
    def __init__(self, responses=()):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, *, params, headers, timeout):
        self.calls.append(
            {
                "url": url,
                "params": dict(params),
                "headers": dict(headers),
                "timeout": timeout,
            }
        )
        if not self.responses:
            raise AssertionError("unexpected network request")
        return self.responses.pop(0)


def write_dfcf_dates(root: Path, dates):
    path = root / "artifacts/leverage_capitulation/dfcf_daily/dfcf_margin_balances.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "date,total_margin_y\n"
        + "".join(f"{item},1\n" for item in dates),
        encoding="utf-8",
    )
    return path


def write_old_szse_raw(root: Path, trade_date: date, payload: bytes):
    output = root / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
    raw_path = output / "raw" / f"{trade_date.isoformat()}_szse.xlsx"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(payload)
    entry = {
        "date": trade_date.isoformat(),
        "market": "SZSE",
        "source_url": "https://www.szse.cn/api/report/ShowReport",
        "request_parameters": {
            "SHOWTYPE": "xlsx",
            "CATALOGID": "1803_sczm",
            "TABKEY": "tab1",
            "txtQueryDate": trade_date.isoformat(),
        },
        "relative_path": f"raw/{trade_date.isoformat()}_szse.xlsx",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "retrieved_at_utc": "2026-08-14T00:00:00+00:00",
        "schema_version": "show_report_xlsx",
    }
    manifest_path = output / "raw_response_manifest.json"
    entries = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else []
    )
    entries = [
        item
        for item in entries
        if not (item["date"] == entry["date"] and item["market"] == entry["market"])
    ]
    entries.append(entry)
    manifest_path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    return entry


def options(module, session):
    return module.RequestOptions(
        session=session,
        sleep_seconds=0,
        timeout_seconds=7,
        max_retries=0,
    )


def test_parse_legacy_sse_uses_product_type_one_only_and_exact_requested_date():
    module = load_module()

    parsed = module.parse_legacy_sse_payload(valid_sse_payload(), date(2011, 8, 3))

    assert parsed == Decimal("100.25")


@pytest.mark.parametrize(
    "payload, message",
    [
        (sse_payload([]), "empty"),
        (sse_payload([sse_row("1", "100", "2011-08-04")]), "date"),
        (
            sse_payload([sse_row("1", "100"), sse_row("1", "101")]),
            "duplicate",
        ),
        (sse_payload([sse_row("99", "100")]), "unknown"),
        (sse_payload([sse_row("1", "NaN")]), "positive"),
        (sse_payload([sse_row("1", "0")]), "positive"),
    ],
)
def test_parse_legacy_sse_fails_closed_for_invalid_response(payload, message):
    module = load_module()

    with pytest.raises(ValueError, match=message):
        module.parse_legacy_sse_payload(payload, date(2011, 8, 3))


@pytest.mark.parametrize("historical", [True, False])
def test_parse_old_szse_workbook_accepts_historical_and_modern_a_labels(historical):
    module = load_module()

    parsed = module.parse_old_szse_workbook(
        szse_workbook_bytes(historical=historical), date(2011, 8, 3)
    )

    assert parsed == Decimal("105")


def test_fetch_sse_uses_only_legacy_search_date_parameters():
    module = load_module()
    session = FakeSession([FakeResponse(valid_sse_payload())])

    payload, params, attempts = module.fetch_legacy_sse(
        date(2011, 8, 3), options(module, session)
    )

    assert payload == valid_sse_payload()
    assert attempts == 1
    assert session.calls == [
        {
            "url": module.SSE_QUERY_URL,
            "params": {
                "sqlId": "COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C",
                "stockType": "90",
                "searchDate": "2011-08-03",
            },
            "headers": module.SSE_HEADERS,
            "timeout": 7,
        }
    ]
    assert params == session.calls[0]["params"]
    assert "TRADE_DATE" not in params


def test_fetch_sse_rejects_post2017_before_http():
    module = load_module()
    session = FakeSession()

    with pytest.raises(ValueError, match="2011-08-03..2016-12-30"):
        module.fetch_legacy_sse(date(2017, 1, 3), options(module, session))

    assert session.calls == []


def test_low_level_sse_request_rejects_nonlegacy_or_trade_date_parameters_before_http():
    module = load_module()
    session = FakeSession()
    invalid_params = {
        "sqlId": "COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C",
        "stockType": "90",
        "TRADE_DATE": "2017-01-03",
    }

    with pytest.raises(ValueError, match="legacy searchDate"):
        module._request_with_retry(options(module, session), params=invalid_params)

    assert session.calls == []


def test_load_dfcf_common_dates_rejects_post2017_requested_range(tmp_path):
    module = load_module()
    write_dfcf_dates(
        tmp_path,
        ["2011-08-03", "2011-08-04", "2017-01-03", "2017-01-04"],
    )

    with pytest.raises(ValueError, match="2016-12-30"):
        module.load_dfcf_pre2017_common_dates(
            tmp_path, date(2011, 8, 3), date(2017, 1, 4)
        )


def test_cli_rejects_post2017_before_http_or_any_output_write(tmp_path, monkeypatch):
    module = load_module()
    (tmp_path / "AGENTS.md").write_text("# test\n", encoding="utf-8")
    dfcf_path = write_dfcf_dates(tmp_path, ["2016-12-30", "2017-01-03"])
    before = hashlib.sha256(dfcf_path.read_bytes()).hexdigest()
    calls = 0

    def forbidden_session():
        nonlocal calls
        calls += 1
        raise AssertionError("post-2017 range must be rejected before HTTP")

    monkeypatch.setattr(module.requests, "Session", forbidden_session)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT_PATH),
            "--project-root",
            str(tmp_path),
            "--start-date",
            "2017-01-03",
            "--end-date",
            "2017-01-03",
            "--dry-run",
        ],
    )

    with pytest.raises(SystemExit) as raised:
        module.main()

    assert raised.value.code == 2
    assert calls == 0
    assert hashlib.sha256(dfcf_path.read_bytes()).hexdigest() == before
    assert not (tmp_path / module.OUTPUT_DIRECTORY).exists()


def test_cli_default_end_date_stops_at_2016_12_30_without_http_or_writes(
    tmp_path, monkeypatch, capsys
):
    module = load_module()
    (tmp_path / "AGENTS.md").write_text("# test\n", encoding="utf-8")
    dfcf_path = write_dfcf_dates(tmp_path, ["2016-12-30", "2017-01-03"])
    before = hashlib.sha256(dfcf_path.read_bytes()).hexdigest()
    calls = 0

    def forbidden_session():
        nonlocal calls
        calls += 1
        raise AssertionError("dry-run must not create an HTTP session")

    monkeypatch.setattr(module.requests, "Session", forbidden_session)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT_PATH),
            "--project-root",
            str(tmp_path),
            "--dry-run",
        ],
    )

    assert module.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert calls == 0
    assert result["requested_dates"] == 1
    assert result["start_date"] == "2016-12-30"
    assert result["end_date"] == "2016-12-30"
    assert hashlib.sha256(dfcf_path.read_bytes()).hexdigest() == before
    assert not (tmp_path / module.OUTPUT_DIRECTORY).exists()


def test_public_builder_rejects_date_that_is_not_a_dfcf_common_date(tmp_path):
    module = load_module()
    write_dfcf_dates(tmp_path, ["2011-08-03"])

    with pytest.raises(ValueError, match="DFCF common date"):
        module.build_official_pre2017_market_cap(
            tmp_path,
            [date(2011, 8, 4)],
            options(module, FakeSession()),
            rebuild_from_existing=True,
        )


def test_rebuild_from_existing_reuses_verified_szse_without_http_or_sse_raw_write(tmp_path):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    write_old_szse_raw(tmp_path, trade_date, szse_workbook_bytes())
    session = FakeSession()

    result = module.build_official_pre2017_market_cap(
        tmp_path,
        [trade_date],
        options(module, session),
        rebuild_from_existing=True,
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    manifest = json.loads(
        (output / "official_pre2017_market_cap_manifest.json").read_text("utf-8")
    )
    assert session.calls == []
    assert result["network_requests"] == 0
    assert result["reusable_szse_dates"] == 1
    assert manifest["mode"] == "rebuild_from_existing"
    assert manifest["final_output_ready"] is False
    assert manifest["reusable_szse_dates"] == ["2011-08-03"]
    assert manifest["completed_dates"] == []
    assert manifest["missing_dates"] == ["2011-08-03"]
    assert manifest["reporting_eligible"] is False
    assert not (output / "raw" / "sse").exists()
    assert pd.read_csv(output / "official_pre2017_market_cap.csv").empty


def test_rebuild_from_existing_accepts_explicit_read_only_legacy_raw_root(tmp_path):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    external_legacy_root = tmp_path / "external_legacy_read_only"
    write_old_szse_raw(external_legacy_root, trade_date, szse_workbook_bytes())

    result = module.build_official_pre2017_market_cap(
        tmp_path,
        [trade_date],
        options(module, FakeSession()),
        rebuild_from_existing=True,
        legacy_raw_root=external_legacy_root
        / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily",
    )

    assert result["reusable_szse_dates"] == 1
    manifest = json.loads(
        (
            tmp_path
            / "artifacts/leverage_capitulation/official_pre2017_market_cap/"
            "official_pre2017_market_cap_manifest.json"
        ).read_text("utf-8")
    )
    assert manifest["legacy_raw_root"] == str(
        (
            external_legacy_root
            / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
        ).resolve()
    )


@pytest.mark.parametrize("corruption", ["date", "relative_path", "sha256"])
def test_rebuild_from_existing_rejects_corrupt_old_szse_manifest_without_network(
    tmp_path, corruption
):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    entry = write_old_szse_raw(tmp_path, trade_date, szse_workbook_bytes())
    manifest_path = (
        tmp_path
        / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily/raw_response_manifest.json"
    )
    if corruption == "date":
        entry["date"] = "2011-08-04"
    elif corruption == "relative_path":
        entry["relative_path"] = "../outside.xlsx"
    else:
        entry["sha256"] = "f" * 64
    manifest_path.write_text(json.dumps([entry]), encoding="utf-8")
    session = FakeSession()

    result = module.build_official_pre2017_market_cap(
        tmp_path,
        [trade_date],
        options(module, session),
        rebuild_from_existing=True,
    )

    assert session.calls == []
    assert result["network_requests"] == 0
    assert result["reusable_szse_dates"] == 0
    manifest = json.loads(
        (
            tmp_path
            / "artifacts/leverage_capitulation/official_pre2017_market_cap/"
            "official_pre2017_market_cap_manifest.json"
        ).read_text("utf-8")
    )
    assert manifest["missing_dates"] == ["2011-08-03"]
    assert manifest["szse_unavailable_dates"][0]["date"] == "2011-08-03"


def test_normal_run_reuses_old_szse_fetches_sse_and_journals_new_raw(tmp_path):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    szse_payload = szse_workbook_bytes()
    szse_entry = write_old_szse_raw(tmp_path, trade_date, szse_payload)
    sse_payload_bytes = valid_sse_payload()
    session = FakeSession([FakeResponse(sse_payload_bytes)])

    result = module.build_official_pre2017_market_cap(
        tmp_path, [trade_date], options(module, session), rebuild_from_existing=False
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    raw_path = output / "raw/sse/2011-08-03.json"
    manifest_path = output / "official_pre2017_market_cap_manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    frame = pd.read_csv(output / "official_pre2017_market_cap.csv", dtype=str)
    assert result["network_requests"] == 1
    assert [call["url"] for call in session.calls] == [module.SSE_QUERY_URL]
    assert raw_path.read_bytes() == sse_payload_bytes
    assert manifest["sse_raw_entries"] == [
        {
            "date": "2011-08-03",
            "source_url": module.SSE_QUERY_URL,
            "request_parameters": {
                "sqlId": "COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C",
                "stockType": "90",
                "searchDate": "2011-08-03",
            },
            "relative_path": "raw/sse/2011-08-03.json",
            "sha256": hashlib.sha256(sse_payload_bytes).hexdigest(),
            "bytes": len(sse_payload_bytes),
            "schema_version": "legacy_product_type",
        }
    ]
    assert frame.to_dict("records") == [
        {
            "date": "2011-08-03",
            "sh_a_market_cap_yi": "100.25",
            "sz_a_market_cap_yi": "105",
            "market_cap_yi": "205.25",
            "source_segment": "official_exchange_pre_2017",
            "status": "pass",
            "sse_raw_sha256": hashlib.sha256(sse_payload_bytes).hexdigest(),
            "szse_raw_sha256": szse_entry["sha256"],
        }
    ]
    assert manifest["completed_dates"] == ["2011-08-03"]
    assert manifest["missing_dates"] == []
    assert manifest["reporting_eligible"] is True
    assert manifest["dfcf_input"]["sha256"] == hashlib.sha256(
        (
            tmp_path
            / "artifacts/leverage_capitulation/dfcf_daily/dfcf_margin_balances.csv"
        ).read_bytes()
    ).hexdigest()


def test_invalid_sse_response_is_not_persisted_as_success(tmp_path):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    write_old_szse_raw(tmp_path, trade_date, szse_workbook_bytes())
    session = FakeSession([FakeResponse(sse_payload([sse_row("1", "0")]))])

    result = module.build_official_pre2017_market_cap(
        tmp_path, [trade_date], options(module, session), rebuild_from_existing=False
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    manifest = json.loads(
        (output / "official_pre2017_market_cap_manifest.json").read_text("utf-8")
    )
    assert result["network_requests"] == 1
    assert not (output / "raw/sse/2011-08-03.json").exists()
    assert manifest["sse_raw_entries"] == []
    assert manifest["missing_dates"] == ["2011-08-03"]
    assert manifest["reporting_eligible"] is False


def test_sse_raw_entry_is_journaled_before_a_later_date_fails(tmp_path):
    module = load_module()
    dates = [date(2011, 8, 3), date(2011, 8, 4)]
    write_dfcf_dates(tmp_path, [item.isoformat() for item in dates])
    for item in dates:
        write_old_szse_raw(tmp_path, item, szse_workbook_bytes())
    session = FakeSession(
        [
            FakeResponse(valid_sse_payload("2011-08-03")),
            FakeResponse(sse_payload([sse_row("1", "0", "2011-08-04")])),
        ]
    )

    result = module.build_official_pre2017_market_cap(
        tmp_path, dates, options(module, session), rebuild_from_existing=False
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    manifest = json.loads(
        (output / "official_pre2017_market_cap_manifest.json").read_text("utf-8")
    )
    assert result["network_requests"] == 2
    assert [entry["date"] for entry in manifest["sse_raw_entries"]] == ["2011-08-03"]
    assert (output / "raw/sse/2011-08-03.json").exists()
    assert not (output / "raw/sse/2011-08-04.json").exists()
    assert manifest["completed_dates"] == ["2011-08-03"]
    assert manifest["missing_dates"] == ["2011-08-04"]


def test_rebuild_does_not_construct_http_session_or_change_legacy_inputs(
    tmp_path, monkeypatch, capsys
):
    module = load_module()
    (tmp_path / "AGENTS.md").write_text("# test\n", encoding="utf-8")
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    legacy_root = tmp_path / "legacy"
    write_old_szse_raw(legacy_root, trade_date, szse_workbook_bytes())
    actual_legacy_root = (
        legacy_root
        / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
    )
    manifest_path = actual_legacy_root / "raw_response_manifest.json"
    raw_path = actual_legacy_root / "raw/2011-08-03_szse.xlsx"
    before = (hashlib.sha256(manifest_path.read_bytes()).hexdigest(), hashlib.sha256(raw_path.read_bytes()).hexdigest())

    def forbidden_session():
        raise AssertionError("rebuild-from-existing must not construct HTTP session")

    monkeypatch.setattr(module.requests, "Session", forbidden_session)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT_PATH),
            "--project-root",
            str(tmp_path),
            "--legacy-raw-root",
            str(actual_legacy_root),
            "--start-date",
            "2011-08-03",
            "--end-date",
            "2011-08-03",
            "--rebuild-from-existing",
        ],
    )

    assert module.main() == 0
    assert json.loads(capsys.readouterr().out)["network_requests"] == 0
    after = (hashlib.sha256(manifest_path.read_bytes()).hexdigest(), hashlib.sha256(raw_path.read_bytes()).hexdigest())
    assert after == before


def test_cli_dry_run_has_zero_http_and_zero_target_writes(tmp_path, monkeypatch, capsys):
    module = load_module()
    (tmp_path / "AGENTS.md").write_text("# test\n", encoding="utf-8")
    write_dfcf_dates(tmp_path, ["2011-08-03"])
    calls = 0

    def forbidden_session():
        nonlocal calls
        calls += 1
        raise AssertionError("dry-run must not create a session")

    monkeypatch.setattr(module.requests, "Session", forbidden_session)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT_PATH),
            "--project-root",
            str(tmp_path),
            "--start-date",
            "2011-08-03",
            "--end-date",
            "2011-08-03",
            "--dry-run",
        ],
    )

    assert module.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert calls == 0
    assert result["dry_run"] is True
    assert result["requested_dates"] == 1
    assert not (
        tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    ).exists()
