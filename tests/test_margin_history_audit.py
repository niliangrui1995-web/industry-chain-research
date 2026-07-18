from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / ".agents"
    / "skills"
    / "a-share-leverage-capitulation-analyst"
    / "scripts"
    / "audit_margin_history.py"
)
SPEC = importlib.util.spec_from_file_location("audit_margin_history", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MarginHistoryAuditTests(unittest.TestCase):
    def test_legacy_root_history_is_deleted_and_not_a_script_fallback(self) -> None:
        self.assertFalse((ROOT / "ashare_daily_margin_history.csv").exists())
        for script_name in (
            "audit_margin_history.py",
            "leverage_capitulation_backtest.py",
            "fetch_szse_margin_repairs.py",
        ):
            text = (SCRIPT.parent / script_name).read_text(encoding="utf-8")
            self.assertNotIn("ashare_daily_margin_history.csv", text)

    def test_eastmoney_market_uses_six_pages_and_normalizes_yuan(self) -> None:
        calls: list[dict[str, str]] = []

        def fake_request(url: str, *, params: dict[str, str], headers: dict[str, str]) -> object:
            self.assertEqual(url, MODULE.EASTMONEY_URL)
            self.assertEqual(headers, MODULE.EASTMONEY_HEADERS)
            calls.append(params)
            page = int(params["pageNumber"])
            return {
                "success": True,
                "result": {
                    "count": 6,
                    "pages": 6,
                    "data": [
                        {
                            "DIM_DATE": f"2016-01-{page + 3:02d} 00:00:00",
                            "RZYE": page * 100_000_000,
                        }
                    ],
                },
            }

        with patch.object(MODULE, "request_json", side_effect=fake_request):
            frame, metadata = MODULE.fetch_eastmoney_market(
                "SZ", "2016-01-01", "2016-01-31"
            )

        self.assertEqual(metadata, {"requests": 6, "rows": 6})
        self.assertEqual(len(calls), 6)
        self.assertTrue(all(call["pageSize"] == "500" for call in calls))
        self.assertTrue(all('(SCDM="001")' in call["filter"] for call in calls))
        self.assertEqual(frame["sz_margin_y"].tolist(), [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    def test_official_szse_comparison_uses_published_precision(self) -> None:
        dates = pd.to_datetime(["2016-01-04", "2016-01-05"])
        eastmoney = pd.DataFrame(
            {"date": dates, "sz_margin_y": [100.005, 101.0]}
        )
        official = pd.DataFrame(
            {"date": dates, "sz_margin_y": [100.0, 101.02]}
        )

        result = MODULE.compare_official_szse_cache(eastmoney, official)

        self.assertEqual(result["official_szse_checks"], 2)
        self.assertEqual(result["official_szse_mismatches_at_0_01_yi_precision"], 1)
        self.assertAlmostEqual(result["official_szse_max_abs_error_y"], 0.02)


if __name__ == "__main__":
    unittest.main()
