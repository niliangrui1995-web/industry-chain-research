from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".agents"
    / "skills"
    / "a-share-leverage-capitulation-analyst"
    / "scripts"
    / "update_dfcf_margin_daily.py"
)
SPEC = importlib.util.spec_from_file_location("update_dfcf_margin_daily", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def market_frame(column: str, values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-07-17", "2026-07-20"]),
            column: values,
            "source": [MODULE.DFCF_URL, MODULE.DFCF_URL],
            "fetched_at_utc": ["2026-07-21T00:00:00+00:00"] * 2,
        }
    )


def test_build_merged_table_uses_common_dates_and_calculates_changes() -> None:
    sh = market_frame("sh_margin_y", [100.0, 95.0])
    sz = market_frame("sz_margin_y", [80.0, 76.0])

    table = MODULE.build_merged_table(sh, sz)

    assert table["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-07-17", "2026-07-20"]
    assert table["total_margin_y"].tolist() == [180.0, 171.0]
    assert table.iloc[-1]["total_change_y"] == -9.0
    assert table.iloc[-1]["total_change_pct"] == pytest.approx(-5.0)
    assert table["sample_status"].eq(MODULE.SAMPLE_STATUS).all()


def test_merge_market_snapshot_keeps_unchanged_rows_and_applies_corrections() -> None:
    existing = market_frame("sh_margin_y", [100.0, 95.0])
    incoming = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-07-20", "2026-07-21"]),
            "sh_margin_y": [94.5, 93.0],
            "source": [MODULE.DFCF_URL, MODULE.DFCF_URL],
            "fetched_at_utc": ["2026-07-22T00:00:00+00:00"] * 2,
        }
    )

    merged, changed = MODULE.merge_market_snapshot(existing, incoming, "sh_margin_y")

    assert changed == 2
    assert merged["date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2026-07-17",
        "2026-07-20",
        "2026-07-21",
    ]
    assert merged["sh_margin_y"].tolist() == [100.0, 94.5, 93.0]


def test_daily_updater_contains_no_exchange_endpoint() -> None:
    source = SCRIPT_PATH.read_text(encoding="utf-8").lower()
    assert "query.sse.com.cn" not in source
    assert "www.szse.cn" not in source


@pytest.mark.parametrize("missing_market", ["SH", "SZ"])
def test_missing_previous_session_never_becomes_multiday_change(missing_market: str) -> None:
    dates = pd.to_datetime(["2026-07-17", "2026-07-20", "2026-07-21", "2026-07-22"])
    sh = pd.DataFrame({"date": dates, "sh_margin_y": [100.0, 99.0, 98.0, 97.0]})
    sz = pd.DataFrame({"date": dates, "sz_margin_y": [80.0, 79.0, 78.0, 77.0]})
    if missing_market == "SH":
        sh = sh.drop(index=1)
    else:
        sz = sz.drop(index=1)

    table = MODULE.build_merged_table(sh, sz).set_index("date")

    assert pd.Timestamp("2026-07-20") not in table.index
    assert table.loc["2026-07-21", "total_margin_y"] == 176.0
    for prefix in (missing_market.lower(), "total"):
        assert pd.isna(table.loc["2026-07-21", f"{prefix}_change_y"])
        assert pd.isna(table.loc["2026-07-21", f"{prefix}_change_pct"])
    complete_market = "sz" if missing_market == "SH" else "sh"
    assert table.loc["2026-07-21", f"{complete_market}_change_y"] == -1.0
    assert table.loc["2026-07-21", "change_status"] == "previous_session_incomplete"
    assert table.loc["2026-07-22", "total_change_y"] == -2.0
    assert table.loc["2026-07-22", "change_status"] == "complete"


def test_holiday_gap_remains_a_valid_previous_session() -> None:
    dates = pd.to_datetime(["2026-09-30", "2026-10-08"])
    sh = pd.DataFrame({"date": dates, "sh_margin_y": [100.0, 99.0]})
    sz = pd.DataFrame({"date": dates, "sz_margin_y": [80.0, 79.0]})
    table = MODULE.build_merged_table(sh, sz)
    assert table.iloc[-1]["total_change_y"] == -2.0
    assert table.iloc[-1]["change_status"] == "complete"


def test_existing_local_calendar_catches_session_missing_on_both_markets() -> None:
    dates = pd.to_datetime(["2026-07-17", "2026-07-21", "2026-07-22"])
    calendar = pd.to_datetime(["2026-07-17", "2026-07-20", "2026-07-21", "2026-07-22"])
    sh = pd.DataFrame({"date": dates, "sh_margin_y": [100.0, 98.0, 97.0]})
    sz = pd.DataFrame({"date": dates, "sz_margin_y": [80.0, 78.0, 77.0]})

    table = MODULE.build_merged_table(sh, sz, trading_calendar=calendar).set_index("date")

    assert pd.Timestamp("2026-07-20") not in table.index
    for prefix in ("sh", "sz", "total"):
        assert pd.isna(table.loc["2026-07-21", f"{prefix}_change_pct"])
    assert table.loc["2026-07-21", "change_status"] == "previous_session_incomplete"
    assert table.loc["2026-07-22", "total_change_y"] == -2.0


def test_local_calendar_missing_and_invalid_data_are_explicit(tmp_path: Path) -> None:
    missing = tmp_path / "sh000001.day"
    dates, metadata = MODULE.load_trading_calendar(missing)
    assert dates is None
    assert metadata["status"] == "unavailable"
    missing.write_bytes(b"invalid")
    with pytest.raises(ValueError, match="calendar"):
        MODULE.load_trading_calendar(missing)
