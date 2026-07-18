from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from array import array
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / ".agents"
    / "skills"
    / "a-share-leverage-capitulation-analyst"
    / "scripts"
    / "analyze_market_median_returns.py"
)
SPEC = importlib.util.spec_from_file_location("analyze_market_median_returns", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MarketMedianReturnAnalysisTests(unittest.TestCase):
    def test_daily_median_uses_all_comparable_returns(self) -> None:
        summary = MODULE.summarize_returns(array("d", [-10.0, -2.0, 2.0, 10.0]))

        self.assertEqual(summary["comparable_count"], 4)
        self.assertEqual(summary["down_count"], 2)
        self.assertAlmostEqual(summary["market_return_median_pct"], 0.0)
        self.assertAlmostEqual(summary["decliners_median_return_pct"], -6.0)

    def test_vendor_average_price_index_uses_close_to_close_return(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sh880003.day"
            path.write_bytes(
                b"".join(
                    [
                        MODULE.DAY_STRUCT.pack(20260102, 1000, 1000, 1000, 1000, 0.0, 0, 0),
                        MODULE.DAY_STRUCT.pack(20260105, 900, 900, 900, 900, 0.0, 0, 0),
                    ]
                )
            )

            frame = MODULE.read_vendor_close_index(
                path,
                "tdx_average_price_index_close",
                "tdx_average_price_index_return_pct",
            )

            self.assertAlmostEqual(frame.iloc[-1]["tdx_average_price_index_close"], 9.0)
            self.assertAlmostEqual(frame.iloc[-1]["tdx_average_price_index_return_pct"], -10.0)

    def test_average_price_source_must_match_the_controlled_audit_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            snapshot = folder / "sh880003_complete.day"
            snapshot.write_bytes(b"controlled-880003-snapshot")
            audit_path = folder / "intraday_drawdown_analysis_audit.json"
            audit_path.write_text(
                json.dumps(
                    {
                        "sources": {
                            "880003": {
                                "path": str(snapshot),
                                "sha256": MODULE.sha256_file(snapshot),
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            resolved, audit = MODULE.load_audited_average_price_source(audit_path, None)

            self.assertEqual(resolved, snapshot)
            self.assertEqual(audit["expected_sha256"], audit["actual_sha256"])

            relocated = folder / "relocated.day"
            relocated.write_bytes(b"different-snapshot")
            with self.assertRaisesRegex(ValueError, "hash does not match"):
                MODULE.load_audited_average_price_source(audit_path, relocated)

    def test_trimmed_median_is_an_audit_field_not_the_primary_value(self) -> None:
        summary = MODULE.summarize_returns(array("d", [-40.0, -4.0, -3.0, -2.0, 5.0]))

        self.assertAlmostEqual(summary["market_return_median_pct"], -3.0)
        self.assertAlmostEqual(summary["trimmed_market_return_median_pct"], -2.5)
        self.assertEqual(summary["abs_return_gt_22_count"], 1)

    def test_causal_rank_is_unchanged_when_future_rows_are_appended(self) -> None:
        dates = pd.Series(pd.bdate_range("2020-01-01", periods=800))
        values = pd.Series(np.sin(np.arange(800)) * 5.0)
        base = MODULE.causal_rolling_rank(
            dates,
            values,
            years=2,
            min_observations=400,
        )
        extended = MODULE.causal_rolling_rank(
            pd.concat([dates, pd.Series([pd.Timestamp("2030-01-02")])], ignore_index=True),
            pd.concat([values, pd.Series([-99.0])], ignore_index=True),
            years=2,
            min_observations=400,
        )

        pd.testing.assert_frame_equal(base, extended.iloc[:-1].reset_index(drop=True))

    def test_full_window_allows_a_known_long_holiday_after_window_start(self) -> None:
        dates = pd.Series(
            pd.DatetimeIndex([pd.Timestamp("2017-09-29")]).append(
                pd.bdate_range("2017-10-09", "2020-09-30")
            )
        )
        values = pd.Series(np.arange(len(dates), dtype=float))

        ranked = MODULE.causal_rolling_rank(
            dates,
            values,
            years=3,
            min_observations=600,
        )

        self.assertFalse(pd.isna(ranked.iloc[-1]["market_return_median_rank_3y"]))

    def test_rank_one_means_the_worst_median_in_the_past_window(self) -> None:
        dates = pd.Series(pd.bdate_range("2020-01-01", periods=600))
        values = pd.Series(np.zeros(600))
        values.iloc[-1] = -10.0

        ranked = MODULE.causal_rolling_rank(
            dates,
            values,
            years=2,
            min_observations=400,
        )

        self.assertEqual(ranked.iloc[-1]["market_return_median_rank_3y"], 1)
        self.assertGreaterEqual(
            ranked.iloc[-1]["market_return_median_rank_window_observations"], 400
        )

    def test_signal_availability_is_the_next_trading_date(self) -> None:
        calendar = pd.DatetimeIndex(pd.to_datetime(["2026-07-16", "2026-07-17", "2026-07-20"]))

        self.assertEqual(
            MODULE.next_trading_date(calendar, pd.Timestamp("2026-07-16")),
            pd.Timestamp("2026-07-17"),
        )
        self.assertTrue(pd.isna(MODULE.next_trading_date(calendar, pd.Timestamp("2026-07-20"))))

    def test_estimated_signal_is_loaded_separately_from_formal_statistics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            payload = {
                "formal_statistics_inclusion": False,
                "scenarios": [
                    {
                        "date": "2026-07-17",
                        "sample_status": "estimated_not_in_formal_statistics",
                        "sz_comp_return_pct": -5.2,
                        "margin_outflow_pct": 2.7,
                        "sz_comp_rank": 3,
                        "margin_outflow_rank": 1,
                        "breadth_total": 5521,
                        "down_pct": 90.67,
                        "breadth_valid": True,
                        "long_break_eve": False,
                    }
                ],
            }
            (folder / "estimated_signal_scenarios.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )

            scenarios, audit = MODULE.load_estimated_original_signal_scenarios(folder)

            self.assertEqual(len(scenarios), 1)
            self.assertEqual(scenarios.iloc[0]["date"], pd.Timestamp("2026-07-17"))
            self.assertEqual(audit["estimated_original_signal_count"], 1)

    def test_average_price_index_replacement_changes_only_the_index_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            dates = pd.to_datetime(["2019-01-02", "2019-01-03", "2019-01-04"])
            pd.DataFrame(
                {
                    "date": dates,
                    "sz_comp_return_pct": [-5.0, -3.0, -4.0],
                    "sz_comp_rank": [1.0, 20.0, 1.0],
                    "margin_outflow_pct": [1.0, 1.0, 1.0],
                    "margin_outflow_rank": [1.0, 1.0, 1.0],
                    "breadth_total": [3000, 3000, 3000],
                    "down_pct": [90.0, 90.0, 90.0],
                    "breadth_valid": [True, True, True],
                    "margin_data_valid": [True, True, True],
                    "long_break_eve": [False, False, False],
                }
            ).to_csv(folder / "factor_panel.csv", index=False)
            daily = pd.DataFrame(
                {
                    "date": dates,
                    "market_return_median_pct": [-4.0, -3.0, -2.0],
                    "market_return_median_rank_3y": [1, 2, 3],
                    "tdx_average_price_index_close": [10.0, 9.0, 8.0],
                    "tdx_average_price_index_return_pct": [-5.0, -4.0, -3.0],
                    "tdx_average_price_index_return_rank_3y": [1, 1, 20],
                }
            )
            original_signals = pd.DataFrame({"date": dates[[0, 2]]})

            replacement, comparison, audit = (
                MODULE.build_average_price_replacement_comparison(
                    folder,
                    daily,
                    original_signals,
                )
            )

            self.assertEqual(replacement["date"].dt.strftime("%Y-%m-%d").tolist(), [
                "2019-01-02",
                "2019-01-03",
            ])
            self.assertEqual(comparison["membership"].tolist(), [
                "both",
                "880003_only",
                "399106_only",
            ])
            self.assertEqual(audit["common_formal_signal_count"], 1)
            self.assertEqual(audit["original_399106_only_count"], 1)
            self.assertEqual(audit["replacement_880003_only_count"], 1)


if __name__ == "__main__":
    unittest.main()
