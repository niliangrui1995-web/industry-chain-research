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
