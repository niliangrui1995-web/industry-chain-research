import hashlib
from datetime import date, timedelta
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
        "TX_NUM": "1",
    }


def valid_sse_payload(trade_date="2011-08-03"):
    return exact_pre2017_sse_payload(trade_date)


def exact_pre2017_sse_payload(trade_date="2011-08-03", *, total="110.75"):
    return sse_payload(
        [
            {
                **sse_row("1", "100.25", trade_date),
                "TX_NUM": "100",
            },
            {
                **sse_row("2", "10.50", trade_date),
                "TX_NUM": "10",
            },
            {
                **sse_row("12", total, trade_date),
                "TX_NUM": "110",
            },
        ]
    )


def sse_mapping_evidence_bytes():
    return """
        if ($stockday.length > 0) {
            var stockDay = {
                parms: {
                    searchDate: init ? '' : day,
                    sqlId: 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C',
                    stockType: '90'
                },
                fnCallBack: function(data) {
                    var item = data.result;
                    var header = [
                        ["", "<div class='th_div_center'>单日情况</div>"],
                        ["", "<div class='th_div_center'>股票</div>"],
                        ["", "<div class='th_div_center'>主板A</div>"],
                        ["", "<div class='th_div_center'>主板B</div>"],
                        ["", "<div class='th_div_center'>科创板</div>"],
                        ["", "<div class='th_div_center'>股票回购</div>"]
                    ];
                    for (var i = 0; i < item.length; i++) {
                        var result = item[i];
                        if (result.PRODUCT_TYPE == "40") { arrA = createArr(result); }
                        else if (result.PRODUCT_TYPE == "1") { arrB = createArr(result); }
                        else if (result.PRODUCT_TYPE == "2") { arrC = createArr(result); }
                        else if (result.PRODUCT_TYPE == "43") { arrF = createArr(result); }
                        else if (result.PRODUCT_TYPE == "48") { arrG = createArr(result); }
                    }
                    var list = [
                        ['市价总值(亿元)', arrA[5], arrB[5], arrC[5], arrG[5], arrF[5]]
                    ];
                }
            };
        }
        if ($fundday_new.length > 0) {
            var fundDay = {parms: {sqlId: 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C', fundType: '47'}};
        }
    """.encode("utf-8")


def szse_five_category_workbook_bytes(*, stock_total="11400000000", b_cap="900000000"):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["证券类别", "数量(只)", "成交金额(元)", "总市值(元)", "流通市值(元)"])
    sheet.append(["股票", 5, 0, stock_total, 0])
    sheet.append(["主板A股", 1, 0, "10000000000", 0])
    sheet.append(["主板B股", 1, 0, b_cap, 0])
    sheet.append(["中小板", 1, 0, "200000000", 0])
    sheet.append(["创业板", 1, 0, "300000000", 0])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def szse_workbook_bytes(*, historical=True):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["证券类别", "数量(只)", "成交金额(元)", "总市值(元)", "流通市值(元)"])
    suffix = "" if historical else "A股"
    sheet.append(["股票", 5, 0, "11400000000", 0])
    sheet.append([f"主板A股", 1, 0, "10000000000", 0])
    sheet.append(["主板B股", 1, 0, "900000000", 0])
    sheet.append([f"中小板{suffix}", 1, 0, "200000000", 0])
    sheet.append([f"创业板{suffix}", 1, 0, "300000000", 0])
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


def test_parse_legacy_sse_requires_1_2_12_and_validates_a_plus_b_identity():
    module = load_module()

    assert module.parse_legacy_sse_payload(
        exact_pre2017_sse_payload(), date(2011, 8, 3)
    ) == Decimal("100.25")

    with pytest.raises(ValueError, match="PRODUCT_TYPE=12"):
        module.parse_legacy_sse_payload(
            exact_pre2017_sse_payload(total="110.76"), date(2011, 8, 3)
        )


def test_parse_legacy_sse_requires_tx_num_for_all_three_product_types():
    module = load_module()
    payload = json.loads(exact_pre2017_sse_payload().decode("utf-8"))
    for row in payload["result"]:
        row.pop("TX_NUM")

    with pytest.raises(ValueError, match="TX_NUM"):
        module.parse_legacy_sse_payload(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"), date(2011, 8, 3)
        )


def test_parse_legacy_sse_rejects_fractional_tx_num():
    module = load_module()
    payload = json.loads(exact_pre2017_sse_payload().decode("utf-8"))
    payload["result"][0]["TX_NUM"] = "100.5"
    payload["result"][2]["TX_NUM"] = "110.5"

    with pytest.raises(ValueError, match="TX_NUM"):
        module.parse_legacy_sse_payload(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"), date(2011, 8, 3)
        )


def test_parse_legacy_sse_rejects_non_midnight_cal_date_suffix():
    module = load_module()
    payload = json.loads(exact_pre2017_sse_payload().decode("utf-8"))
    payload["result"][0]["CAL_DATE"] = "2011-08-03 12:00:00"

    with pytest.raises(ValueError, match="CAL_DATE"):
        module.parse_legacy_sse_payload(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"), date(2011, 8, 3)
        )


def test_parse_legacy_sse_accepts_official_zero_time_fraction_suffix():
    module = load_module()

    assert module.parse_legacy_sse_payload(
        exact_pre2017_sse_payload("2011-08-03 00:00:00.0"), date(2011, 8, 3)
    ) == Decimal("100.25")


def test_sse_mapping_evidence_requires_official_header_and_direct_1_2_assignments():
    module = load_module()

    parsed = module.parse_sse_mapping_evidence(sse_mapping_evidence_bytes())

    assert parsed["product_type_mapping"] == {
        "1": "主板A",
        "2": "主板B",
        "40": "股票",
        "43": "股票回购",
        "48": "科创板",
    }
    with pytest.raises(ValueError, match="主板A"):
        module.parse_sse_mapping_evidence(
            sse_mapping_evidence_bytes().replace(
                "主板A".encode("utf-8"), "未知板块".encode("utf-8")
            )
        )


def test_sse_mapping_evidence_binds_stockday_block_not_other_same_sql_block():
    module = load_module()
    payload = sse_mapping_evidence_bytes()
    stock_branch = b'if (result.PRODUCT_TYPE == "40") { arrA = createArr(result); }'
    assert stock_branch in payload
    forged = payload.replace(stock_branch, b'if (result.PRODUCT_TYPE == "41") { arrA = createArr(result); }')

    with pytest.raises(ValueError, match="branch mapping"):
        module.parse_sse_mapping_evidence(forged)


def test_sse_mapping_evidence_rejects_branches_spliced_from_another_function_block():
    module = load_module()
    payload = sse_mapping_evidence_bytes()
    stock_branches = b'''\
                        if (result.PRODUCT_TYPE == "40") { arrA = createArr(result); }
                        else if (result.PRODUCT_TYPE == "1") { arrB = createArr(result); }
                        else if (result.PRODUCT_TYPE == "2") { arrC = createArr(result); }
                        else if (result.PRODUCT_TYPE == "43") { arrF = createArr(result); }
                        else if (result.PRODUCT_TYPE == "48") { arrG = createArr(result); }
'''
    assert stock_branches in payload
    spliced = payload.replace(stock_branches, b"", 1) + b'''\
        function unrelated() {
            for (var i = 0; i < item.length; i++) {
                var result = item[i];
                if (result.PRODUCT_TYPE == "40") { arrA = createArr(result); }
                else if (result.PRODUCT_TYPE == "1") { arrB = createArr(result); }
                else if (result.PRODUCT_TYPE == "2") { arrC = createArr(result); }
                else if (result.PRODUCT_TYPE == "43") { arrF = createArr(result); }
                else if (result.PRODUCT_TYPE == "48") { arrG = createArr(result); }
            }
        }
'''

    with pytest.raises(ValueError, match="branch mapping"):
        module.parse_sse_mapping_evidence(spliced)


def test_sse_mapping_evidence_requires_daily_sql_id_as_the_sqlid_parameter_value():
    module = load_module()
    payload = sse_mapping_evidence_bytes().replace(
        b"sqlId: 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C',\n                    stockType",
        b"sqlId: 'OTHER',\n                    note: 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C',\n                    stockType",
    )

    with pytest.raises(ValueError, match="daily SQL id"):
        module.parse_sse_mapping_evidence(payload)


def test_sse_mapping_evidence_rejects_duplicate_stockday_parameter_property():
    module = load_module()
    payload = sse_mapping_evidence_bytes().replace(
        b"stockType: '90'\n",
        b"stockType: '90',\n                    stockType: '90'\n",
    )

    with pytest.raises(ValueError, match="duplicate stockDay parms property stockType"):
        module.parse_sse_mapping_evidence(payload)


def test_sse_mapping_evidence_ignores_commented_parms_and_reads_direct_stockday_parms():
    module = load_module()
    payload = sse_mapping_evidence_bytes().replace(
        b"var stockDay = {\n                parms: {",
        b"var stockDay = {\n                // parms: {searchDate: day, sqlId: 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C', stockType: '90'}\n                parms: {",
    ).replace(
        b"sqlId: 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C',\n                    stockType",
        b"sqlId: 'OTHER',\n                    stockType",
    )

    with pytest.raises(ValueError, match="daily SQL id"):
        module.parse_sse_mapping_evidence(payload)


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


def test_parse_old_szse_workbook_requires_five_categories_and_stock_equals_a_plus_b():
    module = load_module()

    assert module.parse_old_szse_workbook(
        szse_five_category_workbook_bytes(), date(2011, 8, 3)
    ) == Decimal("105")

    with pytest.raises(ValueError, match="股票.*A.*B"):
        module.parse_old_szse_workbook(
            szse_five_category_workbook_bytes(stock_total="11400000001"),
            date(2011, 8, 3),
        )


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


@pytest.mark.parametrize(
    "manifest, audit",
    [
        ({"reporting_eligible": True}, {"ratio_reporting_eligible": False}),
        ({"reporting_eligible": False}, {"ratio_reporting_eligible": True}),
    ],
)
def test_rebuild_from_existing_never_overwrites_existing_eligible_output(
    tmp_path, manifest, audit
):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    write_old_szse_raw(tmp_path, trade_date, szse_workbook_bytes())
    output = tmp_path / module.OUTPUT_DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "official_pre2017_market_cap.csv"
    manifest_path = output / "official_pre2017_market_cap_manifest.json"
    audit_path = output / module.OFFICIAL_AUDIT_FILENAME
    csv_path.write_bytes(b"existing eligible csv\n")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (csv_path, manifest_path, audit_path)
    }

    with pytest.raises(ValueError, match="eligible"):
        module.build_official_pre2017_market_cap(
            tmp_path,
            [trade_date],
            options(module, FakeSession()),
            rebuild_from_existing=True,
        )

    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (csv_path, manifest_path, audit_path)
    } == before


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


def test_validated_new_szse_checkpoint_accepts_only_the_2015_06_11_gap(tmp_path):
    module = load_module()
    trade_date = date(2011, 8, 3)
    output = tmp_path / module.OUTPUT_DIRECTORY
    payload = szse_workbook_bytes()
    relative_path = module._szse_output_relative_path(trade_date)
    raw_path = output / relative_path
    raw_path.parent.mkdir(parents=True)
    raw_path.write_bytes(payload)
    manifest = {
        "szse_raw_entries": [
            {
                "date": trade_date.isoformat(),
                "market": "SZSE",
                "source_url": module.SZSE_SHOW_REPORT_URL,
                "request_parameters": module._szse_parameters(trade_date),
                "relative_path": relative_path.as_posix(),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "retrieved_at_utc": "2026-08-14T00:00:00+00:00",
                "schema_version": module.SZSE_SCHEMA_VERSION,
                "storage": "official_pre2017_output",
            }
        ]
    }

    assert module._validated_new_szse(output, manifest, trade_date) is None
    with pytest.raises(ValueError, match="2015-06-11"):
        module._new_szse_entry(trade_date, module._szse_parameters(trade_date), payload)


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
    session = FakeSession(
        [
            FakeResponse(sse_mapping_evidence_bytes()),
            FakeResponse(sse_payload_bytes),
        ]
    )

    result = module.build_official_pre2017_market_cap(
        tmp_path, [trade_date], options(module, session), rebuild_from_existing=False
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    raw_path = output / "raw/sse/2011-08-03.json"
    manifest_path = output / "official_pre2017_market_cap_manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    frame = pd.read_csv(output / "official_pre2017_market_cap.csv", dtype=str)
    assert result["network_requests"] == 2
    assert [call["url"] for call in session.calls] == [
        module.SSE_MAPPING_EVIDENCE_URL,
        module.SSE_QUERY_URL,
    ]
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
    assert manifest["reporting_eligible"] is False
    assert manifest["dfcf_input"]["sha256"] == hashlib.sha256(
        (
            tmp_path
            / "artifacts/leverage_capitulation/dfcf_daily/dfcf_margin_balances.csv"
        ).read_bytes()
    ).hexdigest()


def test_normal_run_persists_hashable_sse_mapping_and_blocks_partial_range_from_eligibility(
    tmp_path,
):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    write_old_szse_raw(tmp_path, trade_date, szse_workbook_bytes())
    session = FakeSession(
        [
            FakeResponse(sse_mapping_evidence_bytes()),
            FakeResponse(exact_pre2017_sse_payload()),
        ]
    )

    result = module.build_official_pre2017_market_cap(
        tmp_path, [trade_date], options(module, session), rebuild_from_existing=False
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    manifest = json.loads(
        (output / "official_pre2017_market_cap_manifest.json").read_text("utf-8")
    )
    audit = json.loads(
        (output / "official_pre2017_market_cap_audit.json").read_text("utf-8")
    )
    mapping = manifest["sse_mapping_evidence"]
    mapping_path = output / mapping["relative_path"]
    assert result["network_requests"] == 2
    assert [call["url"] for call in session.calls] == [
        module.SSE_MAPPING_EVIDENCE_URL,
        module.SSE_QUERY_URL,
    ]
    assert mapping_path.read_bytes() == sse_mapping_evidence_bytes()
    assert mapping["sha256"] == hashlib.sha256(mapping_path.read_bytes()).hexdigest()
    assert mapping["parsed"]["product_type_mapping"]["1"] == "主板A"
    assert manifest["reporting_eligible"] is False
    assert audit["official_raw_chain_status"] == "blocked"
    assert audit["scope_mapping_status"] == "pass"
    assert audit["financial_evidence_audit"] == {
        "applicable": False,
        "status": "N/A",
        "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
    }


def test_manifest_marks_reporting_eligible_only_for_exact_full_1316_date_contract(
    tmp_path, monkeypatch
):
    module = load_module()
    start = date(2011, 8, 3)
    end = date(2016, 12, 30)
    full_dates = [start] + [start + timedelta(days=index) for index in range(1, 1315)] + [end]
    assert len(full_dates) == 1316 and full_dates == sorted(full_dates)
    write_dfcf_dates(tmp_path, [start.isoformat()])
    legacy_root = tmp_path / "legacy"
    legacy_manifest_path = legacy_root / "raw_response_manifest.json"
    legacy_manifest_path.parent.mkdir(parents=True)
    legacy_manifest_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(
        module,
        "load_dfcf_pre2017_common_dates",
        lambda _root, _start, _end: full_dates,
    )
    mapping_payload = sse_mapping_evidence_bytes()
    mapping = module.SseMappingEvidence(
        payload=mapping_payload,
        entry=module._sse_mapping_entry(
            mapping_payload, module.parse_sse_mapping_evidence(mapping_payload)
        ),
        parsed=module.parse_sse_mapping_evidence(mapping_payload),
    )
    szse = module.LegacySzsePayload(
        payload=b"fixture",
        entry={"sha256": "b" * 64},
        market_cap_yi=Decimal("105"),
    )
    records = [
        {
            "date": item.isoformat(),
            "sh_a_market_cap_yi": Decimal("100"),
            "sz_a_market_cap_yi": Decimal("105"),
            "market_cap_yi": Decimal("205"),
        }
        for item in full_dates
    ]
    sse_entries = [{"date": item.isoformat()} for item in full_dates]
    szse_by_date = {item: szse for item in full_dates}

    complete = module._build_manifest(
        project_root=tmp_path,
        legacy_raw_root=legacy_root,
        legacy_manifest_path=legacy_manifest_path,
        requested=full_dates,
        records=records,
        sse_entries=sse_entries,
        szse_by_date=szse_by_date,
        szse_unavailable=[],
        missing_details=[],
        mapping_evidence=mapping,
        mode="normal",
        csv_sha256="a" * 64,
        finalized=True,
    )
    partial = module._build_manifest(
        project_root=tmp_path,
        legacy_raw_root=legacy_root,
        legacy_manifest_path=legacy_manifest_path,
        requested=full_dates[:-1],
        records=records[:-1],
        sse_entries=sse_entries[:-1],
        szse_by_date={item: szse for item in full_dates[:-1]},
        szse_unavailable=[],
        missing_details=[],
        mapping_evidence=mapping,
        mode="normal",
        csv_sha256="a" * 64,
        finalized=True,
    )
    non_gap_new_szse = module.LegacySzsePayload(
        payload=b"fixture",
        entry={"sha256": "c" * 64},
        market_cap_yi=Decimal("105"),
        storage="official_pre2017_output",
    )
    non_gap_new_szse_by_date = dict(szse_by_date)
    non_gap_new_szse_by_date[full_dates[0]] = non_gap_new_szse
    non_gap_new_szse_manifest = module._build_manifest(
        project_root=tmp_path,
        legacy_raw_root=legacy_root,
        legacy_manifest_path=legacy_manifest_path,
        requested=full_dates,
        records=records,
        sse_entries=sse_entries,
        szse_by_date=non_gap_new_szse_by_date,
        szse_unavailable=[],
        missing_details=[],
        mapping_evidence=mapping,
        mode="normal",
        csv_sha256="a" * 64,
        finalized=True,
    )

    assert complete["reporting_eligible"] is True
    assert complete["raw_chain_audit"]["date_linkage_status"] == "pass"
    assert partial["reporting_eligible"] is False
    assert partial["raw_chain_audit"]["official_raw_chain_status"] == "blocked"
    assert non_gap_new_szse_manifest["reporting_eligible"] is False
    assert non_gap_new_szse_manifest["new_szse_gap_dates"] == ["2011-08-03"]


def test_only_2015_06_11_missing_szse_file_can_be_fetched_into_new_raw_chain(tmp_path):
    module = load_module()
    trade_date = date(2015, 6, 11)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    legacy_root = tmp_path / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
    legacy_root.mkdir(parents=True)
    legacy_manifest = legacy_root / "raw_response_manifest.json"
    legacy_manifest.write_text("[]", encoding="utf-8")
    old_hash = hashlib.sha256(legacy_manifest.read_bytes()).hexdigest()
    session = FakeSession(
        [
            FakeResponse(sse_mapping_evidence_bytes()),
            FakeResponse(szse_workbook_bytes()),
            FakeResponse(exact_pre2017_sse_payload("2015-06-11")),
        ]
    )

    result = module.build_official_pre2017_market_cap(
        tmp_path, [trade_date], options(module, session), rebuild_from_existing=False
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    manifest = json.loads(
        (output / "official_pre2017_market_cap_manifest.json").read_text("utf-8")
    )
    gap_entries = [
        entry
        for entry in manifest["szse_raw_entries"]
        if entry["date"] == "2015-06-11"
    ]
    assert result["network_requests"] == 3
    assert [call["url"] for call in session.calls] == [
        module.SSE_MAPPING_EVIDENCE_URL,
        module.SZSE_SHOW_REPORT_URL,
        module.SSE_QUERY_URL,
    ]
    assert hashlib.sha256(legacy_manifest.read_bytes()).hexdigest() == old_hash
    assert len(gap_entries) == 1
    assert gap_entries[0]["storage"] == "official_pre2017_output"
    assert (output / gap_entries[0]["relative_path"]).is_file()


def test_invalid_sse_response_is_not_persisted_as_success(tmp_path):
    module = load_module()
    trade_date = date(2011, 8, 3)
    write_dfcf_dates(tmp_path, [trade_date.isoformat()])
    write_old_szse_raw(tmp_path, trade_date, szse_workbook_bytes())
    session = FakeSession(
        [
            FakeResponse(sse_mapping_evidence_bytes()),
            FakeResponse(sse_payload([sse_row("1", "0")])),
        ]
    )

    result = module.build_official_pre2017_market_cap(
        tmp_path, [trade_date], options(module, session), rebuild_from_existing=False
    )

    output = tmp_path / "artifacts/leverage_capitulation/official_pre2017_market_cap"
    manifest = json.loads(
        (output / "official_pre2017_market_cap_manifest.json").read_text("utf-8")
    )
    assert result["network_requests"] == 2
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
            FakeResponse(sse_mapping_evidence_bytes()),
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
    assert result["network_requests"] == 3
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
