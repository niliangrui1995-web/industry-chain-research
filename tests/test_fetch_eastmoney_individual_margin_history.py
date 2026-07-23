from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".agents"
    / "skills"
    / "a-share-leverage-capitulation-analyst"
    / "scripts"
    / "fetch_eastmoney_individual_margin_history.py"
)
SPEC = importlib.util.spec_from_file_location(
    "fetch_eastmoney_individual_margin_history",
    SCRIPT_PATH,
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def raw_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "DATE": "2026-07-22 00:00:00",
        "MARKET": "融资融券_深证",
        "SCODE": "000001",
        "SECNAME": "平安银行",
        "RZYE": 4_906_065_922,
        "RQYL": 1_767_500,
        "RZRQYE": 4_925_473_072,
        "RQYE": 19_407_150,
        "RQMCL": 76_900,
        "RZMRE": 63_580_422,
        "RZCHE": 94_684_005,
        "RZJME": -31_103_583,
        "RQCHL": 8_500,
        "SPJ": 10.98,
        "ZDF": 1.2915,
        "TRADE_MARKET_CODE": "069001002001",
        "TRADE_MARKET": "深交所主板",
        "SECUCODE": "000001.SZ",
    }
    row.update(overrides)
    return row


def test_classify_instrument_separates_stocks_and_etfs() -> None:
    assert MODULE.classify_instrument("069001002001", "000001.SZ") == "A_SHARE_STOCK"
    assert MODULE.classify_instrument("069001001006", "688981.SH") == "A_SHARE_STOCK"
    assert MODULE.classify_instrument("069001017", "920001.BJ") == "A_SHARE_STOCK"
    assert MODULE.classify_instrument("069001001", "510050.SH") == "ETF"
    assert MODULE.classify_instrument("069001002", "159915.SZ") == "ETF"


def test_normalize_detail_row_validates_date_and_balance() -> None:
    normalized = MODULE.normalize_detail_row(raw_row(), "2026-07-22")
    assert normalized[0] == "2026-07-22"
    assert normalized[1] == "000001.SZ"
    assert normalized[7] == "A_SHARE_STOCK"
    assert normalized[8] == 4_906_065_922

    with pytest.raises(ValueError, match="date mismatch"):
        MODULE.normalize_detail_row(raw_row(), "2026-07-21")
    with pytest.raises(ValueError, match="invalid financing balance"):
        MODULE.normalize_detail_row(raw_row(RZYE=None), "2026-07-22")


def test_store_date_fetch_replaces_one_date_atomically(tmp_path: Path) -> None:
    database = tmp_path / "margin.sqlite"
    connection = MODULE.open_database(database)
    first = MODULE.DateFetch(
        trade_date="2026-07-22",
        expected_rows=1,
        pages=1,
        rows=[MODULE.normalize_detail_row(raw_row(), "2026-07-22")],
    )
    MODULE.store_date_fetch(connection, first, fetched_at_utc="2026-07-23T00:00:00+00:00")

    corrected = MODULE.DateFetch(
        trade_date="2026-07-22",
        expected_rows=1,
        pages=1,
        rows=[
            MODULE.normalize_detail_row(
                raw_row(RZYE=4_800_000_000),
                "2026-07-22",
            )
        ],
    )
    MODULE.store_date_fetch(
        connection,
        corrected,
        fetched_at_utc="2026-07-23T01:00:00+00:00",
    )

    assert connection.execute("SELECT COUNT(*) FROM margin_daily").fetchone()[0] == 1
    assert (
        connection.execute(
            "SELECT financing_balance_yuan FROM margin_daily"
        ).fetchone()[0]
        == 4_800_000_000
    )
    assert MODULE.completed_dates(connection) == {"2026-07-22"}
    connection.close()


def test_sqlite_view_excludes_etf_rows(tmp_path: Path) -> None:
    connection = MODULE.open_database(tmp_path / "margin.sqlite")
    rows = [
        MODULE.normalize_detail_row(raw_row(), "2026-07-22"),
        MODULE.normalize_detail_row(
            raw_row(
                SCODE="510050",
                SECUCODE="510050.SH",
                SECNAME="50ETF",
                MARKET="融资融券_沪证",
                TRADE_MARKET_CODE="069001001",
                TRADE_MARKET="上海证券交易所",
            ),
            "2026-07-22",
        ),
    ]
    MODULE.store_date_fetch(
        connection,
        MODULE.DateFetch(
            trade_date="2026-07-22",
            expected_rows=2,
            pages=1,
            rows=rows,
        ),
    )

    assert connection.execute("SELECT COUNT(*) FROM margin_daily").fetchone()[0] == 2
    assert (
        connection.execute(
            "SELECT COUNT(*) FROM a_share_stock_margin_daily"
        ).fetchone()[0]
        == 1
    )
    connection.close()


def test_vendor_gap_is_settled_but_not_complete(tmp_path: Path) -> None:
    connection = MODULE.open_database(tmp_path / "margin.sqlite")
    MODULE.store_vendor_gap(
        connection,
        "2020-12-31",
        MODULE.VendorNoDataError("返回数据为空"),
    )

    assert MODULE.completed_dates(connection) == set()
    assert MODULE.settled_dates(connection) == {"2020-12-31"}
    status = connection.execute(
        "SELECT status FROM fetch_status WHERE trade_date = '2020-12-31'"
    ).fetchone()[0]
    assert status == "vendor_no_data"
    connection.close()
