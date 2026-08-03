from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "update_a_share_total_market_cap.py"
SPEC = importlib.util.spec_from_file_location("update_a_share_total_market_cap", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_frame_filters_dates_and_preserves_vendor_boundary() -> None:
    frame = MODULE.build_frame(
        [
            {"date": "2011-08-02", "marketCap": 100.0},
            {"date": "2011-08-03", "marketCap": 101.5},
            {"date": "2011-08-04", "marketCap": 102.5},
        ],
        start_date="2011-08-03",
        end_date="2011-08-03",
    )

    assert frame["source_date_raw"].dt.strftime("%Y-%m-%d").tolist() == ["2011-08-03"]
    assert frame["a_share_total_market_cap_yi"].tolist() == [101.5]
    assert frame["date_mapping_status"].tolist() == ["unverified"]
    assert frame["reporting_eligible"].tolist() == [False]


def test_build_frame_rejects_non_positive_market_cap() -> None:
    with pytest.raises(ValueError, match="无效值"):
        MODULE.build_frame(
            [{"date": "2011-08-03", "marketCap": 0}],
            start_date="2011-08-03",
            end_date="2011-08-03",
        )


def test_build_frame_flags_duplicate_and_weekend_dates_without_dropping_rows() -> None:
    frame = MODULE.build_frame(
        [
            {"date": "2011-08-06", "marketCap": 100.0},
            {"date": "2011-08-06", "marketCap": 101.0},
        ],
        start_date="2011-08-06",
        end_date="2011-08-06",
    )

    assert len(frame) == 2
    assert frame["duplicate_count_for_date"].eq(2).all()
    assert frame["is_weekend"].all()
    assert frame["quality_status"].eq("duplicate_and_weekend_date_unverified").all()
