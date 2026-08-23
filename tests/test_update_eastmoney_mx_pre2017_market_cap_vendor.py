from __future__ import annotations

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
    / "update_eastmoney_mx_pre2017_market_cap_vendor.py"
)


def load_module():
    assert SCRIPT_PATH.exists(), "缺少东方财富妙想前 2017 市值更新入口"
    spec = importlib.util.spec_from_file_location(
        "update_eastmoney_mx_pre2017_market_cap_vendor", SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def mx_payload(
    days: list[str], values: list[str], raw_values: list[str] | None = None
) -> bytes:
    raw_values = raw_values or [
        str(Decimal(value.removesuffix("万亿")) * Decimal("1000000000000"))
        for value in values
    ]
    return json.dumps(
        {
            "status": 0,
            "message": "ok",
            "data": {
                "data": {
                    "searchDataResultDTO": {
                        "questionId": "test-question-id",
                        "dataTableDTOList": [
                            {
                                "entityName": "沪深A股(板块)",
                                "entityTagDTO": {
                                    "entityId": "001004",
                                    "fullName": "沪深A股",
                                    "className": "市场类(沪深京)",
                                },
                                "field": {
                                    "returnCode": "326608",
                                    "returnSourceCode": "ZSZ",
                                    "returnName": "总市值(合计)",
                                    "returnSourceName": "总市值(合计)_板块",
                                    "dateGranularity": "DAY",
                                    "unit": "1",
                                },
                                "table": {"headName": days, "326608": values},
                                "rawTable": {
                                    "headName": [value[:10] for value in days],
                                    "326608": raw_values,
                                },
                            }
                        ]
                    }
                }
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self.content = payload

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.calls: list[dict[str, object]] = []

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, str],
        timeout: int,
    ) -> FakeResponse:
        self.calls.append(
            {"url": url, "headers": dict(headers), "json": dict(json), "timeout": timeout}
        )
        return FakeResponse(self.payload)


def write_dfcf_dates(root: Path, days: list[str]) -> None:
    (root / "AGENTS.md").write_text("# fixture\n", encoding="utf-8")
    daily = root / "artifacts/leverage_capitulation/dfcf_daily"
    daily.mkdir(parents=True)
    daily.joinpath("dfcf_margin_balances.csv").write_text(
        "date\n" + "".join(f"{day}\n" for day in days), encoding="utf-8"
    )


def test_parse_mx_payload_normalizes_reverse_daily_series_to_dfcf_dates() -> None:
    module = load_module()

    records = module.parse_mx_payload(
        mx_payload(
            ["2016-12-30(日)", "2016-12-29(日)"],
            ["52.45万亿", "52.33万亿"],
            ["52448780844158.03", "52325812966030.89"],
        ),
        expected_dates=[date(2016, 12, 29), date(2016, 12, 30)],
    )

    assert [record.trade_date for record in records] == [
        date(2016, 12, 29),
        date(2016, 12, 30),
    ]
    assert records[0].raw_total_market_cap == Decimal("52325812966030.89")
    assert records[0].market_cap_yi == Decimal("523258.1296603089")
    assert records[1].raw_total_market_cap == Decimal("52448780844158.03")
    assert records[1].market_cap_yi == Decimal("524487.8084415803")


def test_parse_mx_payload_refuses_missing_dfcf_date() -> None:
    module = load_module()

    with pytest.raises(ValueError, match="DFCF"):
        module.parse_mx_payload(
            mx_payload(["2016-12-30(日)"], ["52.45万亿"]),
            expected_dates=[date(2016, 12, 29), date(2016, 12, 30)],
        )


def test_update_writes_raw_csv_and_date_contract_without_full_dfcf_hash(
    tmp_path: Path,
) -> None:
    module = load_module()
    write_dfcf_dates(tmp_path, ["2016-12-29", "2016-12-30", "2017-01-03"])
    session = FakeSession(
        mx_payload(
            ["2016-12-30(日)", "2016-12-29(日)"],
            ["52.45万亿", "52.33万亿"],
            ["52448780844158.03", "52325812966030.89"],
        )
    )
    requested = module.load_dfcf_pre2017_common_dates(
        tmp_path, date(2016, 12, 29), date(2016, 12, 30)
    )

    result = module.update_vendor_market_cap(
        tmp_path,
        requested,
        module.UpdateOptions(session=session, api_key="test-key", timeout_seconds=1),
    )

    output = tmp_path / module.OUTPUT_DIRECTORY
    csv_path = output / module.TABLE_FILENAME
    raw_path = output / "raw/mx-response.json"
    manifest = json.loads((output / module.MANIFEST_FILENAME).read_text(encoding="utf-8"))
    audit = json.loads((output / module.AUDIT_FILENAME).read_text(encoding="utf-8"))
    assert result["output_records"] == 2
    assert result["missing_dfcf_common_dates"] == []
    assert session.calls[0]["url"] == module.SOURCE_URL
    assert session.calls[0]["json"] == {
        "toolQuery": "2016年12月29日至2016年12月30日沪深A股每日总市值"
    }
    assert session.calls[0]["headers"]["apikey"] == "test-key"
    assert raw_path.exists()
    assert manifest["csv_sha256"] == module.sha256_file(csv_path)
    assert manifest["raw_response"]["sha256"] == module.sha256_file(raw_path)
    assert manifest["raw_response"]["question_id"] == "test-question-id"
    assert manifest["source_profile"] == {
        "entity_id": "001004",
        "entity_name": "沪深A股",
        "entity_class": "市场类(沪深京)",
        "return_code": "326608",
        "return_name": "总市值(合计)",
        "return_source_code": "ZSZ",
        "return_source_name": "总市值(合计)_板块",
        "date_granularity": "DAY",
        "raw_unit": "yuan",
    }
    assert manifest["dfcf_pre2017_date_contract"]["count"] == 2
    assert "dfcf_input" not in manifest
    assert audit["date_linkage_status"] == "pass"
    assert audit["raw_response_sha256"] == manifest["raw_response"]["sha256"]
    rows = csv_path.read_text(encoding="utf-8").splitlines()
    assert rows[1].startswith("2016-12-29,523258.1296603089,")
    assert rows[2].startswith("2016-12-30,524487.8084415803,")


def test_cli_refuses_implicit_rebuild_of_frozen_pre2017_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    monkeypatch.setattr(sys, "argv", ["update_eastmoney_mx_pre2017_market_cap_vendor.py"])

    with pytest.raises(SystemExit) as raised:
        module.main()

    assert raised.value.code == 2
