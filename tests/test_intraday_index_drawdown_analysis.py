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
    / "analyze_intraday_index_drawdown_ranks.py"
)
SPEC = importlib.util.spec_from_file_location("analyze_intraday_index_drawdown_ranks", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class IntradayIndexDrawdownAnalysisTests(unittest.TestCase):
    def test_intraday_drawdown_uses_low_over_previous_close(self) -> None:
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-02", "2026-01-05"]),
                "open": [100.0, 96.0],
                "high": [101.0, 99.0],
                "low": [99.0, 90.0],
                "close": [100.0, 95.0],
            }
        )

        ranked = MODULE.add_return_and_rank(frame)

        self.assertAlmostEqual(ranked.iloc[1]["intraday_max_drawdown_pct"], -10.0)
        self.assertAlmostEqual(ranked.iloc[1]["close_return_pct"], -5.0)

    def test_tied_values_use_competition_ranking(self) -> None:
        dates = pd.Series(pd.bdate_range("2020-01-01", periods=800))
        values = pd.Series(np.zeros(800))
        values.iloc[-3:] = [-10.0, -10.0, -9.0]

        ranked = MODULE.causal_rank(dates, values, years=2, min_observations=400)

        self.assertEqual(ranked.iloc[-3]["rank_3y"], 1)
        self.assertEqual(ranked.iloc[-2]["rank_3y"], 1)
        self.assertEqual(ranked.iloc[-1]["rank_3y"], 3)

    def test_future_rows_do_not_change_historical_rank(self) -> None:
        dates = pd.Series(pd.bdate_range("2020-01-01", periods=800))
        values = pd.Series(np.sin(np.arange(800)) * 5.0)
        base = MODULE.causal_rank(dates, values, years=2, min_observations=400)
        extended = MODULE.causal_rank(
            pd.concat([dates, pd.Series([pd.Timestamp("2030-01-02")])], ignore_index=True),
            pd.concat([values, pd.Series([-99.0])], ignore_index=True),
            years=2,
            min_observations=400,
        )

        pd.testing.assert_frame_equal(base, extended.iloc[:-1].reset_index(drop=True))

    def test_tdx_reader_preserves_high_and_low(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sz399106.day"
            path.write_bytes(
                MODULE.DAY_STRUCT.pack(20260105, 1000, 1100, 900, 1050, 0.0, 0, 0)
            )

            frame = MODULE.read_tdx_day(path)

            self.assertAlmostEqual(frame.iloc[0]["high"], 11.0)
            self.assertAlmostEqual(frame.iloc[0]["low"], 9.0)

    def test_inconsistently_ordered_dates_are_rejected(self) -> None:
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-02", "2026-01-06", "2026-01-05"]),
                "open": [10.0, 10.0, 10.0],
                "high": [11.0, 11.0, 11.0],
                "low": [9.0, 9.0, 9.0],
                "close": [10.0, 10.0, 10.0],
            }
        )

        with self.assertRaisesRegex(ValueError, "consistently ordered"):
            MODULE.validate_ohlc(frame, Path("unordered.day"))

    def test_complete_window_survives_a_long_calendar_break(self) -> None:
        dates = pd.Series(
            pd.DatetimeIndex([pd.Timestamp("2017-09-29")]).append(
                pd.bdate_range("2017-10-09", "2020-09-30")
            )
        )
        values = pd.Series(np.arange(len(dates), dtype=float))

        ranked = MODULE.causal_rank(dates, values, years=3, min_observations=600)

        self.assertFalse(pd.isna(ranked.iloc[-1]["rank_3y"]))


if __name__ == "__main__":
    unittest.main()
