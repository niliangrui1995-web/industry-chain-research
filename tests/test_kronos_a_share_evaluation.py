from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd
from decimal import Decimal


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "kronos-market-forecasting"
    / "scripts"
    / "kronos_a_share_evaluation.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("kronos_a_share_evaluation", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class KronosAshareEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_daily_rank_ic_never_mixes_dates(self) -> None:
        frame = pd.DataFrame(
            {
                "trade_date": ["2026-01-01"] * 3 + ["2026-01-02"] * 3,
                "raw_score": [1, 2, 3, 1, 2, 3],
                "label_excess_10d": [1, 2, 3, 3, 2, 1],
            }
        )
        result = self.module.daily_rank_ic(frame)
        self.assertEqual(result["rank_ic"].round(6).tolist(), [1.0, -1.0])

    def test_formal_daily_rank_ic_requires_size_and_membership_coverage(self) -> None:
        frame = pd.DataFrame(
            {
                "trade_date": ["2026-01-05"] * 100,
                "raw_score": range(100),
                "label_excess_10d": range(100),
                "active_member_count": [105] * 100,
            }
        )
        result = self.module.daily_rank_ic(
            frame,
            min_instruments=100,
            active_member_count_column="active_member_count",
            min_coverage_ratio=0.95,
            require_eligible_cross_section=True,
        )
        self.assertEqual(result["eligible_cross_section"].tolist(), [True])
        self.assertAlmostEqual(result.loc[0, "coverage_ratio"], 100 / 105)

        frame["active_member_count"] = 106
        with self.assertRaisesRegex(
            self.module.EvaluationError, "横截面不满足准出门"
        ):
            self.module.daily_rank_ic(
                frame,
                min_instruments=100,
                active_member_count_column="active_member_count",
                min_coverage_ratio=0.95,
                require_eligible_cross_section=True,
            )

    def test_daily_rank_ic_rejects_inconsistent_active_member_count(self) -> None:
        frame = pd.DataFrame(
            {
                "trade_date": ["2026-01-05"] * 3,
                "raw_score": [1.0, 2.0, 3.0],
                "label_excess_10d": [1.0, 2.0, 3.0],
                "active_member_count": [3, 4, 3],
            }
        )
        with self.assertRaisesRegex(self.module.EvaluationError, "同日唯一正整数"):
            self.module.daily_rank_ic(
                frame,
                active_member_count_column="active_member_count",
            )

    def test_bootstrap_is_deterministic(self) -> None:
        dates = pd.date_range("2025-01-01", periods=90, freq="D")
        model = pd.DataFrame({"trade_date": dates, "rank_ic": [0.1] * len(dates)})
        baseline = pd.DataFrame({"trade_date": dates, "rank_ic": [0.0] * len(dates)})
        first = self.module.monthly_block_bootstrap_difference(model, baseline, iterations=200)
        second = self.module.monthly_block_bootstrap_difference(model, baseline, iterations=200)
        self.assertEqual(first, second)
        self.assertGreater(first["ci95_lower"], 0)

    def test_gate_fails_closed_on_provisional_data(self) -> None:
        result = self.module.evaluate_gate(
            data_status="local_provisional",
            adapter_ce_improvement=0.02,
            validation_rank_ic=0.05,
            zero_shot_rank_ic=0.01,
            head_only_rank_ic=0.02,
            positive_quarter_fraction=0.75,
            bootstrap_ci95_lower=0.01,
            base_after_cost_return=0.01,
            stress_after_cost_return=0.001,
        )
        self.assertEqual(result["gate_status"], "blocked")
        self.assertEqual(result["output_type"], "N/A")

    def test_gate_passes_only_above_every_threshold(self) -> None:
        result = self.module.evaluate_gate(
            data_status="production_ready",
            adapter_ce_improvement=0.02,
            validation_rank_ic=0.05,
            zero_shot_rank_ic=0.01,
            head_only_rank_ic=0.02,
            positive_quarter_fraction=0.75,
            bootstrap_ci95_lower=0.01,
            base_after_cost_return=0.01,
            stress_after_cost_return=0.001,
        )
        self.assertEqual(result["gate_status"], "passed")
        self.assertEqual(result["output_type"], "model_output")

    def test_quarter_summary_uses_three_month_rolling_windows(self) -> None:
        daily = pd.DataFrame(
            {
                "trade_date": [
                    "2024-01-15",
                    "2024-02-15",
                    "2024-03-15",
                    "2024-04-15",
                ],
                "rank_ic": [0.1, 0.1, 0.1, -0.5],
            }
        )
        result = self.module.quarterly_rank_ic_summary(daily)
        self.assertEqual(result["quarter_count"], 2)
        self.assertEqual(result["positive_quarter_count"], 1)
        self.assertEqual(
            result["window_contract"],
            "three_consecutive_calendar_months_monthly_step",
        )

    def test_executable_cost_contract_parses_false_strings_strictly(self) -> None:
        frame = pd.DataFrame(
            {
                "trade_date": ["2024-01-02"] * 4,
                "raw_score": [4.0, 3.0, 2.0, 1.0],
                "entry_date": ["2024-01-03"] * 4,
                "exit_date": ["2024-01-17"] * 4,
                "entry_price_raw": [10.0] * 4,
                "exit_price_raw": [20.0, 11.0, 10.0, 9.0],
                "entry_tradable": ["False", "True", "True", "True"],
                "exit_tradable": ["True"] * 4,
                "entry_limit_blocked": ["False"] * 4,
                "exit_limit_blocked": ["False"] * 4,
                "stamp_duty_rate": [0.0005] * 4,
                "corporate_action_factor": [1.0] * 4,
                "corporate_action_event_count": [0] * 4,
                "holding_period_sessions": [10] * 4,
            }
        )
        result = self.module.top_quantile_return_after_cost(
            frame, cost_bps=Decimal("35")
        )
        self.assertEqual(result["selected_trade_count"], 1)
        self.assertAlmostEqual(result["mean_return_after_cost"], 0.09595, places=8)

    def test_executable_cost_contract_blocks_invalid_exit_and_stamp_duty(self) -> None:
        frame = pd.DataFrame(
            {
                "trade_date": ["2023-08-25", "2023-08-28"],
                "raw_score": [1.0, 1.0],
                "entry_date": ["2023-08-28", "2023-08-29"],
                "exit_date": ["2023-09-11", "2023-09-12"],
                "entry_price_raw": [10.0, 10.0],
                "exit_price_raw": [10.1, 10.1],
                "entry_tradable": [True, True],
                "exit_tradable": [True, False],
                "entry_limit_blocked": [False, False],
                "exit_limit_blocked": [False, False],
                "stamp_duty_rate": [0.0005, 0.0005],
                "corporate_action_factor": [1.0, 1.0],
                "corporate_action_event_count": [0, 0],
                "holding_period_sessions": [10, 10],
            }
        )
        with self.assertRaisesRegex(self.module.EvaluationError, "无法按合同退出"):
            self.module.top_quantile_return_after_cost(
                frame, cost_bps=Decimal("35")
            )
        frame.loc[1, "exit_tradable"] = True
        frame.loc[0, "stamp_duty_rate"] = 0.001
        with self.assertRaisesRegex(self.module.EvaluationError, "印花税"):
            self.module.top_quantile_return_after_cost(
                frame, cost_bps=Decimal("35")
            )

    def test_execution_return_uses_action_factor_and_exit_value_stamp_tax(self) -> None:
        frame = pd.DataFrame(
            {
                "trade_date": ["2024-01-02"],
                "raw_score": [1.0],
                "entry_date": ["2024-01-03"],
                "exit_date": ["2024-01-17"],
                "entry_price_raw": [10.0],
                "exit_price_raw": [5.5],
                "entry_tradable": [True],
                "exit_tradable": [True],
                "entry_limit_blocked": [False],
                "exit_limit_blocked": [False],
                "stamp_duty_rate": [0.0005],
                "corporate_action_factor": [0.5],
                "corporate_action_event_count": [1],
                "holding_period_sessions": [10],
            }
        )
        result = self.module.top_quantile_return_after_cost(
            frame, cost_bps=Decimal("0")
        )
        self.assertAlmostEqual(
            result["mean_return_after_cost"],
            1.1 * (1.0 - 0.0005) - 1.0,
            places=10,
        )

    def test_score_record_is_na_when_blocked(self) -> None:
        record = self.module.build_score_record(
            as_of="2026-08-03T15:00:00+08:00",
            ticker="002415.SZ",
            raw_score=1.2,
            percentile=0.9,
            forecast_path=[],
            path_dispersion=0.1,
            dataset_id="dataset-1",
            run_id="run-1",
            adapter_hash="a" * 64,
            gate_status="blocked",
            constraint_flags=["public_pit_incomplete"],
        )
        self.assertEqual(record["evidence_class"], "model_output")
        self.assertEqual(record["output_type"], "N/A")


if __name__ == "__main__":
    unittest.main()
