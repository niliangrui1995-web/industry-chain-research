from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
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
    / "leverage_capitulation_backtest.py"
)
SPEC = importlib.util.spec_from_file_location("leverage_capitulation_backtest", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class LeverageCapitulationBacktestTests(unittest.TestCase):
    def test_uses_three_indexes_named_by_the_skill(self) -> None:
        self.assertEqual(MODULE.INDEX_FILES["sz_comp"], "sz399106")
        self.assertEqual(MODULE.INDEX_FILES["chinext"], "sz399006")
        self.assertEqual(MODULE.INDEX_FILES["chinext_comp"], "sz399102")

    def test_margin_factor_is_percentage_and_official_repair_recomputes_total(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            margin_path = folder / "margin.csv"
            repair_path = folder / "repair.csv"
            pd.DataFrame(
                {
                    "date": ["2025-01-02", "2025-01-03", "2025-01-06"],
                    "sh_margin_y": [100.0, 90.0, 80.0],
                    "sz_margin_y": [100.0, 100.0, 100.0],
                    "total_margin_y": [200.0, 190.0, 180.0],
                    "daily_margin_change_pct": [np.nan, -5.0, -5.263157894736842],
                }
            ).to_csv(margin_path, index=False)
            pd.DataFrame(
                {
                    "date": ["2025-01-03"],
                    "sz_margin_y": [95.0],
                    "source": [MODULE.SZSE_MARGIN_URL],
                    "fetched_at_utc": ["2025-01-07T00:00:00+00:00"],
                }
            ).to_csv(repair_path, index=False)

            frame = MODULE.load_margin_history(margin_path, repair_path)

            self.assertEqual(frame.attrs["repair_rows_applied"], 1)
            self.assertAlmostEqual(frame.loc[1, "total_margin_y"], 185.0)
            self.assertAlmostEqual(frame.loc[1, "margin_outflow_pct"], 7.5)

    def test_audited_snapshot_does_not_reject_legitimate_rounded_repeats(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            margin_path = Path(temp_dir) / "official.csv"
            pd.DataFrame(
                {
                    "date": ["2016-01-04", "2016-01-05"],
                    "sh_margin_y": [100.0, 101.0],
                    "sz_margin_y": [50.0, 50.0],
                    "total_margin_y": [150.0, 151.0],
                }
            ).to_csv(margin_path, index=False)
            frame = MODULE.load_margin_history(margin_path, trust_audited_snapshot=True)
            self.assertTrue(frame["margin_data_valid"].all())

    def test_backtest_requires_verified_margin_audit(self) -> None:
        with self.assertRaisesRegex(ValueError, "verified margin audit JSON is required"):
            MODULE.run_backtest(
                Path("missing-margin.csv"),
                Path("missing-ht-root"),
                MODULE.BacktestConfig(),
            )

    def test_rolling_rank_has_no_future_dependency_and_requires_full_window(self) -> None:
        dates = pd.Series(pd.bdate_range("2020-01-01", periods=800))
        values = pd.Series(np.arange(800, dtype=float))
        base = MODULE.rolling_extreme_rank(
            dates,
            values,
            2,
            descending=True,
            min_observations=400,
        )
        extended = MODULE.rolling_extreme_rank(
            pd.concat([dates, pd.Series([pd.Timestamp("2030-01-01")])], ignore_index=True),
            pd.concat([values, pd.Series([1_000_000.0])], ignore_index=True),
            2,
            descending=True,
            min_observations=400,
        )
        pd.testing.assert_series_equal(base, extended.iloc[:-1].reset_index(drop=True))
        self.assertTrue(base.iloc[:399].isna().all())

    def test_rolling_rank_does_not_reject_a_complete_window_after_a_long_holiday(self) -> None:
        dates = pd.Series(
            pd.DatetimeIndex([pd.Timestamp("2017-09-29")]).append(
                pd.bdate_range("2017-10-09", "2020-09-30")
            )
        )
        values = pd.Series(np.arange(len(dates), dtype=float))

        ranks = MODULE.rolling_extreme_rank(
            dates,
            values,
            3,
            descending=False,
            min_observations=600,
        )

        self.assertFalse(pd.isna(ranks.iloc[-1]))

    def test_sample_periods_keep_raw_signals_and_add_terminal_10d_sample(self) -> None:
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2023-12-29", "2024-01-02", "2024-01-03", "2024-01-04"]
                )
            }
        )
        mask = pd.Series([True, True, True, False])

        periods = MODULE.sample_periods(frame, mask, MODULE.BacktestConfig())

        self.assertEqual(periods["all_signals"].tolist(), [True, True, True, False])
        self.assertEqual(periods["terminal_10d"].tolist(), [False, False, True, False])
        self.assertEqual(periods["pre_validation"].tolist(), [True, False, False, False])
        self.assertEqual(periods["post_validation"].tolist(), [False, True, True, False])
        self.assertEqual(periods["terminal_10d_pre_validation"].tolist(), [False, False, False, False])
        self.assertEqual(periods["terminal_10d_post_validation"].tolist(), [False, False, True, False])
        self.assertNotIn("all_declustered", periods)

    def test_terminal_signal_mask_chains_gaps_at_or_below_10_trading_days(self) -> None:
        mask = pd.Series(False, index=range(32))
        mask.iloc[[0, 10, 20, 31]] = True

        terminal = MODULE.terminal_signal_mask(mask, max_gap=10)

        self.assertEqual(np.flatnonzero(terminal).tolist(), [20, 31])

    def test_long_holiday_eve_is_excluded_without_future_market_values(self) -> None:
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2025-09-29", "2025-09-30", "2025-10-09", "2025-10-10"]
                )
            }
        )
        marked = MODULE.mark_long_break_eves(frame)
        self.assertEqual(marked.tolist(), [False, True, False, False])

    def test_signal_statistics_start_on_2019_01_01(self) -> None:
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2018-12-28", "2019-01-02"]),
                "breadth_valid": [True, True],
                "margin_data_valid": [True, True],
                "long_break_eve": [False, False],
                "margin_outflow_rank": [1.0, 1.0],
                "down_pct": [90.0, 90.0],
                "sz_comp_rank": [1.0, 1.0],
                "chinext_rank": [1.0, 1.0],
                "chinext_comp_rank": [1.0, 1.0],
            }
        )
        masks = MODULE.signal_masks(frame, MODULE.BacktestConfig())
        self.assertEqual(masks["dual_triple"].tolist(), [False, True])

    def test_three_index_triple_signals_are_calculated_separately(self) -> None:
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"]),
                "breadth_valid": [True, True, True],
                "margin_data_valid": [True, True, True],
                "long_break_eve": [False, False, False],
                "margin_outflow_rank": [1.0, 1.0, 1.0],
                "down_pct": [90.0, 90.0, 90.0],
                "sz_comp_rank": [1.0, 99.0, 99.0],
                "chinext_rank": [99.0, 1.0, 99.0],
                "chinext_comp_rank": [99.0, 99.0, 1.0],
            }
        )
        masks = MODULE.signal_masks(frame, MODULE.BacktestConfig())
        self.assertEqual(masks["sz_triple"].tolist(), [True, False, False])
        self.assertEqual(masks["chinext_triple"].tolist(), [False, True, False])
        self.assertEqual(masks["chinext_comp_triple"].tolist(), [False, False, True])

    def test_primary_return_basis_starts_at_signal_day_close(self) -> None:
        frame = pd.DataFrame(
            {
                f"{label}_{field}": values
                for label in ("shanghai", "sz_comp", "chinext", "chinext_comp")
                for field, values in (("open", [100.0, 110.0, 121.0]), ("close", [100.0, 120.0, 132.0]))
            }
        )
        result = MODULE.add_forward_returns(frame)
        self.assertAlmostEqual(result.loc[0, "sz_comp_cc_t1"], 20.0)
        self.assertAlmostEqual(result.loc[0, "sz_comp_cc_t2"], 32.0)
        self.assertAlmostEqual(result.loc[0, "sz_comp_next_open_t1"], (120.0 / 110.0 - 1.0) * 100.0)

        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('factored.loc[mask, f"{return_label}_cc_t2"]', text)
        self.assertNotIn('factored.loc[mask, f"{return_label}_next_open_t2"]', text)

    def test_script_contains_no_hardcoded_synthetic_event(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn('"2026-07-17", -600', text)
        self.assertNotIn("92.86", text)


if __name__ == "__main__":
    unittest.main()
