from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path

import pandas as pd


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_margin_market_cap_chinext_chart.py"
SPEC = importlib.util.spec_from_file_location("build_margin_market_cap_chinext_chart", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_panel_only_uses_exact_unique_non_weekend_dates() -> None:
    margin = pd.DataFrame(
        {
            "date": pd.to_datetime(["2014-01-02", "2014-01-03"]),
            "total_margin_y": ["100", "120"],
            "sample_status": [MODULE.DFCF_STATUS, MODULE.DFCF_STATUS],
        }
    )
    market_cap = pd.DataFrame(
        {
            "source_date_raw": pd.to_datetime(["2014-01-02", "2014-01-03", "2014-01-03"]),
            "a_share_total_market_cap_yi": ["10000", "11000", "11100"],
            "duplicate_count_for_date": [1, 2, 2],
            "is_weekend": [False, False, False],
            "date_mapping_status": ["unverified", "unverified", "unverified"],
            "reporting_eligible": [False, False, False],
        }
    )
    chinext = pd.DataFrame(
        {
            "date": pd.to_datetime(["2014-01-02", "2014-01-03"]),
            "chinext_close": [Decimal("1000"), Decimal("1100")],
        }
    )

    panel, diagnostics = MODULE.build_panel(
        margin, market_cap, chinext, start_date="2014-01-01"
    )

    assert panel["date"].dt.strftime("%Y-%m-%d").tolist() == ["2014-01-02"]
    assert panel["sh_sz_margin_to_all_a_market_cap_pct"].tolist() == ["1.00000000"]
    assert panel["chinext_normalized"].tolist() == ["100.00000000"]
    assert diagnostics["market_cap_duplicate_dates_excluded"] == 1
    assert diagnostics["common_rows"] == 1


def test_parse_day_bytes_uses_fifth_field_as_close() -> None:
    payload = MODULE.DAY_STRUCT.pack(20140102, 130230, 133310, 129934, 133300, 0.0, 0, 0)

    frame = MODULE.parse_day_bytes(payload)

    assert frame.iloc[0]["chinext_close"] == Decimal("1333")
