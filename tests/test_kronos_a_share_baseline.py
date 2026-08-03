from __future__ import annotations

import importlib.util
import json
import math
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".agents" / "skills" / "kronos-market-forecasting" / "scripts" / "kronos_a_share_baseline.py"
SCRIPTS_DIR = MODULE_PATH.parent
CORPORATE_ACTION_COLUMNS = (
    "ticker",
    "announcement_date",
    "ex_date",
    "cash_div",
    "bonus_ratio",
    "rights_ratio",
    "rights_price",
)


def load_module():
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("kronos_a_share_baseline", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class KronosAshareBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def setUp(self) -> None:
        self.segments = {
            "train": ["2022-01-03", "2022-12-30"],
            "validation": ["2023-01-02", "2023-12-29"],
            "development_test": ["2024-01-02", "2024-12-31"],
            "locked_retrospective": ["2025-01-02", "2025-12-31"],
        }

    def _write_corporate_actions(
        self,
        training: Path,
        rows: list[dict[str, object]] | None = None,
        *,
        name: str = "corporate_actions.csv",
    ) -> Path:
        path = training / "data" / "normalized" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows or [], columns=CORPORATE_ACTION_COLUMNS).to_csv(path, index=False)
        return path

    def _normalized_fixture(
        self, training: Path
    ) -> tuple[Path, Path, Path, float, pd.Timestamp]:
        dates = pd.bdate_range("2023-01-02", periods=120)
        rows = []
        for ticker, daily_log_return in (("sh600000", 0.002), ("sh000906", 0.0005)):
            for index, date in enumerate(dates):
                close = 100.0 * math.exp(daily_log_return * index)
                rows.append(
                    {
                        "trade_date": date.strftime("%Y-%m-%d"),
                        "ticker": ticker,
                        "open": close,
                        "high": close * 1.01,
                        "low": close * 0.99,
                        "close": close,
                        "volume": 1000.0,
                        "amount": close * 1000.0,
                    }
                )
        source = training / "data" / "normalized" / "bars.csv"
        source.parent.mkdir(parents=True)
        pd.DataFrame(rows).to_csv(source, index=False)
        origin, target = dates[90], dates[100]
        label = (0.002 * 10) - (0.0005 * 10)
        sample = training / "data" / "datasets" / "sample_index.csv"
        sample.parent.mkdir(parents=True)
        pd.DataFrame(
            [
                {
                    "sample_id": 0,
                    "ticker": "sh600000",
                    "origin_date": int(origin.strftime("%Y%m%d")),
                    "target_date": int(target.strftime("%Y%m%d")),
                    "split": "validation",
                    "label_excess_10d": label,
                }
            ]
        ).to_csv(sample, index=False)
        actions = self._write_corporate_actions(training)
        return source, sample, actions, label, origin

    def _realized_label(
        self,
        source: Path,
        sample: Path,
        actions: Path,
    ) -> float:
        market = pd.read_csv(source)
        market["trade_date"] = pd.to_datetime(market["trade_date"])
        sample_row = pd.read_csv(sample).iloc[0]
        origin = pd.to_datetime(str(int(sample_row["origin_date"])), format="%Y%m%d")
        target = pd.to_datetime(str(int(sample_row["target_date"])), format="%Y%m%d")
        stock = market[market["ticker"] == "sh600000"].sort_values(
            "trade_date"
        ).reset_index(drop=True)
        benchmark = market[market["ticker"] == "sh000906"].sort_values(
            "trade_date"
        ).reset_index(drop=True)
        stock_positions = {
            value: index for index, value in enumerate(stock["trade_date"])
        }
        stock_for_label = stock.copy()
        stock_for_label["date"] = stock_for_label["trade_date"].dt.strftime(
            "%Y%m%d"
        ).astype(np.int64)
        stock_return = self.module.realized_total_log_return(
            stock_for_label,
            origin_index=stock_positions[origin],
            target_index=stock_positions[target],
            corporate_actions=self.module.load_corporate_actions(actions),
            ticker="sh600000",
        )
        benchmark_close = benchmark.set_index("trade_date")["close"]
        return stock_return - math.log(
            float(benchmark_close.loc[target]) / float(benchmark_close.loc[origin])
        )

    def _companion_fixture(self, training: Path):
        dates = pd.bdate_range("2023-01-02", "2023-09-15")
        rows = []
        for ticker, daily_log_return in (("sh600000", 0.001), ("sh000906", 0.0002)):
            for index, date in enumerate(dates):
                close = 20.0 * math.exp(daily_log_return * index)
                rows.append(
                    {
                        "trade_date": date.strftime("%Y-%m-%d"),
                        "ticker": ticker,
                        "open": close,
                        "high": close * 1.01,
                        "low": close * 0.99,
                        "close": close,
                        "volume": 1000.0,
                        "amount": close * 1000.0,
                        "price_basis": "trade_price_raw",
                    }
                )
        source_frame = pd.DataFrame(rows)
        source = training / "data" / "raw" / "execution.csv"
        source.parent.mkdir(parents=True)
        source_frame.to_csv(source, index=False)
        date_positions = {date: index for index, date in enumerate(dates)}
        target_dates = [pd.Timestamp("2023-08-25"), pd.Timestamp("2023-08-28")]
        sample_rows = []
        for sample_id, target in enumerate(target_dates):
            origin = dates[date_positions[target] - 10]
            sample_rows.append(
                {
                    "sample_id": sample_id,
                    "ticker": "sh600000",
                    "origin_date": int(origin.strftime("%Y%m%d")),
                    "target_date": int(target.strftime("%Y%m%d")),
                    "split": "validation",
                    "label_excess_10d": (0.001 - 0.0002) * 10,
                }
            )
        sample = training / "data" / "datasets" / "companion_sample_index.csv"
        sample.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(sample_rows).to_csv(sample, index=False)
        provider = training / "data" / "qlib" / "companion_provider"
        actions = self._write_corporate_actions(
            training, name="companion_corporate_actions.csv"
        )
        self.module.build_project_qlib_provider(
            source_path=source,
            sample_index_path=sample,
            corporate_actions_path=actions,
            provider_uri=provider,
            training_root=training,
            segments=self.segments,
        )

        stock = source_frame[source_frame["ticker"] == "sh600000"].copy()
        stock["trade_date"] = pd.to_datetime(stock["trade_date"])
        stock = stock.set_index("trade_date")
        suspension_rows = []
        limit_rows = []
        expected_entries = []
        for sample_id, sample_row in enumerate(sample_rows):
            origin = pd.to_datetime(str(sample_row["origin_date"]), format="%Y%m%d")
            target = pd.to_datetime(str(sample_row["target_date"]), format="%Y%m%d")
            entry = dates[date_positions[origin] + 1]
            expected_entries.append(entry)
            for phase, date in (("entry", entry), ("exit", target)):
                suspension_rows.append(
                    {
                        "ticker": "600000.SH",
                        "trade_date": date.strftime("%Y-%m-%d"),
                        "is_suspended": sample_id == 0 and phase == "entry",
                    }
                )
                price = float(stock.loc[date, "open" if phase == "entry" else "close"])
                if sample_id == 0 and phase == "entry":
                    up_limit, down_limit = price, price * 0.8
                elif sample_id == 0 and phase == "exit":
                    up_limit, down_limit = price * 1.2, price
                else:
                    up_limit, down_limit = np.nan, np.nan
                limit_rows.append(
                    {
                        "ticker": "600000.SH",
                        "trade_date": date.strftime("%Y-%m-%d"),
                        "up_limit": up_limit,
                        "down_limit": down_limit,
                    }
                )
        suspensions = training / "data" / "normalized" / "suspensions.csv"
        limits = training / "data" / "normalized" / "price_limits.csv"
        suspensions.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(suspension_rows).to_csv(suspensions, index=False)
        pd.DataFrame(limit_rows).to_csv(limits, index=False)
        artifacts = {}
        artifact_dir = training / "runs" / "fixture" / "predictions"
        artifact_dir.mkdir(parents=True)
        for offset, name in enumerate(self.module.EXTERNAL_SCORE_COLUMNS):
            path = artifact_dir / f"{name}.csv"
            pd.DataFrame(
                {"sample_id": [0, 1], "raw_score": [0.1 + offset, 0.2 + offset]}
            ).to_csv(path, index=False)
            artifacts[name] = {"path": str(path), "sha256": self.module.sha256_file(path)}
        binding = {
            "base_model_sha256": "a" * 64,
            "tokenizer_sha256": "b" * 64,
            "data_sha256": "c" * 64,
            "config_sha256": "d" * 64,
        }
        return {
            "source": source,
            "sample": sample,
            "provider": provider,
            "suspensions": suspensions,
            "limits": limits,
            "artifacts": artifacts,
            "binding": binding,
            "expected_entries": expected_entries,
        }

    def test_task_uses_precomputed_excess_log_label(self) -> None:
        task = self.module.build_task_config(
            provider_uri=Path("qlib"), segments=self.segments
        )
        self.assertEqual(task["label"], "$label_excess_10d")
        self.assertNotIn("Ref(", task["label"])
        self.assertEqual(task["label_contract"], self.module.LABEL_CONTRACT)
        self.assertEqual(task["label_unit"], "natural_log_return")
        self.assertNotIn("100", task["label_contract"])
        self.assertEqual(task["market"], "csi800")

    def test_task_binds_all_lightgbm_random_seeds(self) -> None:
        task = self.module.build_task_config(
            provider_uri=Path("qlib"), segments=self.segments, seed=117
        )
        model = task["model"]
        self.assertEqual(
            {
                model["seed"],
                model["feature_fraction_seed"],
                model["bagging_seed"],
                model["data_random_seed"],
            },
            {117},
        )

    def test_label_and_momentum_are_unscaled_natural_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, expected_label, _ = self._normalized_fixture(training)
            self.assertAlmostEqual(expected_label, 0.015)
            report = self.module.build_project_qlib_provider(
                source_path=source,
                sample_index_path=sample,
                corporate_actions_path=actions,
                provider_uri=training / "data" / "qlib" / "provider",
                training_root=training,
                segments=self.segments,
            )
            baseline_inputs = pd.read_csv(
                Path(report["provider_uri"]) / "baseline_inputs.csv"
            )
            self.assertAlmostEqual(baseline_inputs.loc[0, "label_excess_10d"], 0.015)
            self.assertAlmostEqual(baseline_inputs.loc[0, "momentum_score"], 0.04)
            self.assertEqual(report["label_unit"], "natural_log_return")

    def test_causal_model_prices_remove_mechanical_action_jump_without_future_use(self) -> None:
        dates = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
        market = pd.DataFrame(
            {
                "trade_date": dates,
                "ticker": ["sh600000"] * 3,
                "open": [10.0, 5.0, 5.0],
                "high": [10.0, 5.0, 5.0],
                "low": [10.0, 5.0, 5.0],
                "close": [10.0, 5.0, 5.0],
                "vwap": [10.0, 5.0, 5.0],
                "volume": [100.0] * 3,
                "amount": [1000.0, 500.0, 500.0],
            }
        )
        actions = pd.DataFrame(
            [
                {
                    "ticker": "sh600000",
                    "announcement_date": pd.Timestamp("2024-01-02"),
                    "ex_date": pd.Timestamp("2024-01-03"),
                    "cash_div": 0.0,
                    "bonus_ratio": 1.0,
                    "rights_ratio": 0.0,
                    "rights_price": 0.0,
                },
                {
                    "ticker": "sh600000",
                    "announcement_date": pd.Timestamp("2024-01-05"),
                    "ex_date": pd.Timestamp("2024-01-08"),
                    "cash_div": 1.0,
                    "bonus_ratio": 0.0,
                    "rights_ratio": 0.0,
                    "rights_price": 0.0,
                },
            ]
        )
        adjusted, applied = self.module._causal_model_price_market(market, actions)
        self.assertEqual(applied, 1)
        np.testing.assert_allclose(adjusted["close"], [10.0, 10.0, 10.0])
        self.assertEqual(float(adjusted.loc[0, "close"]), 10.0)

    def test_overlapping_segments_and_cross_split_label_are_rejected(self) -> None:
        overlapping = dict(self.segments)
        overlapping["development_test"] = ["2023-12-29", "2024-12-31"]
        with self.assertRaisesRegex(self.module.BaselineError, "split 重叠"):
            self.module.validate_segments(overlapping)
        sample = pd.DataFrame(
            [
                {
                    "sample_id": 0,
                    "ticker": "sh600000",
                    "origin_date": 20231225,
                    "target_date": 20240108,
                    "split": "validation",
                    "label_excess_10d": 1.0,
                }
            ]
        )
        with self.assertRaisesRegex(self.module.BaselineError, "label_crosses_split"):
            self.module.validate_sample_index_contract(sample, self.segments)

    def test_project_provider_materializes_exact_label_and_naive_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, expected_label, origin = self._normalized_fixture(training)
            provider = training / "data" / "qlib" / "provider"
            report = self.module.build_project_qlib_provider(
                source_path=source,
                sample_index_path=sample,
                corporate_actions_path=actions,
                provider_uri=provider,
                training_root=training,
                segments=self.segments,
            )
            self.assertEqual(report["schema_version"], self.module.PROVIDER_SCHEMA)
            self.assertFalse(report["downloaded_public_qlib_package"])
            self.assertEqual(report["label_expression"], "$label_excess_10d")
            baseline_inputs = pd.read_csv(provider / "baseline_inputs.csv")
            self.assertEqual(baseline_inputs["sample_id"].tolist(), [0])
            self.assertAlmostEqual(baseline_inputs.loc[0, "label_excess_10d"], expected_label)
            self.assertAlmostEqual(baseline_inputs.loc[0, "momentum_score"], 0.04)
            self.assertAlmostEqual(
                baseline_inputs.loc[0, "reversal_score"],
                -baseline_inputs.loc[0, "momentum_score"],
            )
            calendar = pd.read_csv(provider / "calendars" / "day.txt", header=None)[0]
            origin_position = int(np.flatnonzero(calendar == origin.strftime("%Y-%m-%d"))[0])
            label_bin = np.fromfile(
                provider / "features" / "sh600000" / "label_excess_10d.day.bin",
                dtype="<f4",
            )
            self.assertEqual(int(label_bin[0]), origin_position)
            self.assertAlmostEqual(float(label_bin[1]), expected_label, places=6)
            inspected = self.module.inspect_project_qlib_provider(provider, training)
            self.assertEqual(inspected["sample_count"], 1)

    def test_label_mismatch_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, _, _ = self._normalized_fixture(training)
            frame = pd.read_csv(sample)
            frame.loc[0, "label_excess_10d"] += 0.01
            frame.to_csv(sample, index=False)
            with self.assertRaisesRegex(self.module.BaselineError, "label_mismatch"):
                self.module.build_project_qlib_provider(
                    source_path=source,
                    sample_index_path=sample,
                    corporate_actions_path=actions,
                    provider_uri=training / "data" / "qlib" / "provider",
                    training_root=training,
                    segments=self.segments,
                )

    def test_dividend_window_uses_bound_dataset_total_return_and_detects_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, raw_label, origin = self._normalized_fixture(training)
            sample_frame = pd.read_csv(sample)
            target = pd.to_datetime(
                str(int(sample_frame.loc[0, "target_date"])), format="%Y%m%d"
            )
            event_dates = pd.bdate_range(origin, target)
            self._write_corporate_actions(
                training,
                [
                    {
                        "ticker": "600000.SH",
                        "announcement_date": event_dates[1].strftime("%Y-%m-%d"),
                        "ex_date": event_dates[5].strftime("%Y-%m-%d"),
                        "cash_div": 2.0,
                        "bonus_ratio": 0.0,
                        "rights_ratio": 0.0,
                        "rights_price": 0.0,
                    }
                ],
            )
            expected = self._realized_label(source, sample, actions)
            self.assertNotAlmostEqual(expected, raw_label)
            sample_frame.loc[0, "label_excess_10d"] = expected
            sample_frame.to_csv(sample, index=False)
            provider = training / "data" / "qlib" / "dividend-provider"
            report = self.module.build_project_qlib_provider(
                source_path=source,
                sample_index_path=sample,
                corporate_actions_path=actions,
                provider_uri=provider,
                training_root=training,
                segments=self.segments,
            )
            baseline_inputs = pd.read_csv(provider / "baseline_inputs.csv")
            self.assertAlmostEqual(
                baseline_inputs.loc[0, "label_excess_10d"], expected
            )
            self.assertEqual(
                report["corporate_actions_sha256"], self.module.sha256_file(actions)
            )
            actions.write_text(actions.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.BaselineError, "corporate_actions SHA256 漂移"
            ):
                self.module.inspect_project_qlib_provider(provider, training)

    def test_post_target_corporate_action_does_not_leak_into_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, raw_label, _ = self._normalized_fixture(training)
            target = pd.to_datetime(
                str(int(pd.read_csv(sample).loc[0, "target_date"])), format="%Y%m%d"
            )
            self._write_corporate_actions(
                training,
                [
                    {
                        "ticker": "sh600000",
                        "announcement_date": (target + pd.offsets.BDay(1)).strftime(
                            "%Y-%m-%d"
                        ),
                        "ex_date": (target + pd.offsets.BDay(2)).strftime("%Y-%m-%d"),
                        "cash_div": 10.0,
                        "bonus_ratio": 0.0,
                        "rights_ratio": 0.0,
                        "rights_price": 0.0,
                    }
                ],
            )
            self.assertAlmostEqual(
                self._realized_label(source, sample, actions), raw_label
            )
            provider = training / "data" / "qlib" / "post-target-provider"
            self.module.build_project_qlib_provider(
                source_path=source,
                sample_index_path=sample,
                corporate_actions_path=actions,
                provider_uri=provider,
                training_root=training,
                segments=self.segments,
            )

    def test_sample_id_must_preserve_full_source_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, _, _ = self._normalized_fixture(training)
            frame = pd.read_csv(sample)
            frame.loc[0, "sample_id"] = 1
            frame.to_csv(sample, index=False)
            with self.assertRaisesRegex(
                self.module.BaselineError, "sample_id 必须从0连续递增"
            ):
                self.module.build_project_qlib_provider(
                    source_path=source,
                    sample_index_path=sample,
                    corporate_actions_path=actions,
                    provider_uri=training / "data" / "qlib" / "provider",
                    training_root=training,
                    segments=self.segments,
                )

    def test_eleven_trading_day_purge_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, _, _ = self._normalized_fixture(training)
            dates = pd.bdate_range("2023-01-02", periods=120)
            frame = pd.read_csv(sample)
            frame.loc[0, "origin_date"] = int(dates[109].strftime("%Y%m%d"))
            frame.loc[0, "target_date"] = int(dates[119].strftime("%Y%m%d"))
            frame.to_csv(sample, index=False)
            with self.assertRaisesRegex(self.module.BaselineError, "purge_violation"):
                self.module.build_project_qlib_provider(
                    source_path=source,
                    sample_index_path=sample,
                    corporate_actions_path=actions,
                    provider_uri=training / "data" / "qlib" / "provider",
                    training_root=training,
                    segments=self.segments,
                )

    def test_every_provider_read_and_write_path_is_guarded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            training.mkdir()
            source, sample, actions, _, _ = self._normalized_fixture(training)
            with self.assertRaisesRegex(self.module.BaselineError, "path_outside_training_root"):
                self.module.build_project_qlib_provider(
                    source_path=source,
                    sample_index_path=sample,
                    corporate_actions_path=actions,
                    provider_uri=root / "outside-provider",
                    training_root=training,
                    segments=self.segments,
                )
            outside_source = root / "outside.csv"
            outside_source.write_bytes(source.read_bytes())
            with self.assertRaisesRegex(self.module.BaselineError, "path_outside_training_root"):
                self.module.build_project_qlib_provider(
                    source_path=outside_source,
                    sample_index_path=sample,
                    corporate_actions_path=actions,
                    provider_uri=training / "data" / "qlib" / "provider",
                    training_root=training,
                    segments=self.segments,
                )

    def test_alpha158_output_retains_sample_id_for_companion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            source, sample, actions, _, origin = self._normalized_fixture(training)
            provider = training / "data" / "qlib" / "provider"
            self.module.build_project_qlib_provider(
                source_path=source,
                sample_index_path=sample,
                corporate_actions_path=actions,
                provider_uri=provider,
                training_root=training,
                segments=self.segments,
            )

            class FakeAlpha158:
                def __init__(self, **_: object) -> None:
                    pass

            class FakeDatasetH:
                def __init__(self, **_: object) -> None:
                    pass

            class FakeLGBModel:
                def __init__(self, **kwargs: object) -> None:
                    self.seed = int(kwargs["seed"])

                def fit(self, _: object) -> None:
                    pass

                def predict(self, _: object, *, segment: str) -> pd.Series:
                    self_segment = segment
                    if self_segment != "valid":
                        raise AssertionError(f"unexpected segment: {self_segment}")
                    index = pd.MultiIndex.from_tuples(
                        [(origin, "SH600000")], names=["datetime", "instrument"]
                    )
                    return pd.Series([self.seed / 100.0], index=index, name="score")

            qlib = types.ModuleType("qlib")
            qlib_init = mock.Mock()
            qlib.init = qlib_init
            config = types.ModuleType("qlib.config")
            config.REG_CN = "cn"
            handler = types.ModuleType("qlib.contrib.data.handler")
            handler.Alpha158 = FakeAlpha158
            gbdt = types.ModuleType("qlib.contrib.model.gbdt")
            gbdt.LGBModel = FakeLGBModel
            dataset = types.ModuleType("qlib.data.dataset")
            dataset.DatasetH = FakeDatasetH
            fake_modules = {
                "qlib": qlib,
                "qlib.config": config,
                "qlib.contrib.data.handler": handler,
                "qlib.contrib.model.gbdt": gbdt,
                "qlib.data.dataset": dataset,
            }
            output = training / "runs" / "fixture" / "alpha158.csv"
            with mock.patch.dict(sys.modules, fake_modules):
                report = self.module.run_alpha158_lightgbm(
                    provider_uri=provider,
                    training_root=training,
                    output_path=output,
                    segments=self.segments,
                    seeds=(100, 101),
                )
            prediction = pd.read_csv(output)
            self.assertEqual(prediction["sample_id"].tolist(), [0])
            self.assertEqual(report["row_count"], 1)
            self.assertEqual(report["seed_count"], 2)
            self.assertEqual(report["seeds"], [100, 101])
            self.assertEqual(report["aggregate_method"], "arithmetic_mean_prediction")
            self.assertAlmostEqual(prediction.loc[0, "raw_score"], 1.005)
            qlib_init.assert_called_once()
            init_kwargs = qlib_init.call_args.kwargs
            experiment_uri = init_kwargs["exp_manager"]["kwargs"]["uri"]
            expected_experiment_root = (
                training / "registry" / "qlib-mlruns"
            ).resolve()
            self.assertEqual(experiment_uri, "file:" + str(expected_experiment_root))
            self.assertEqual(report["experiment_manager_uri"], experiment_uri)
            self.assertTrue(expected_experiment_root.is_dir())

    def test_lightgbm_seed_contract_rejects_duplicates_and_more_than_twenty(self) -> None:
        with self.assertRaisesRegex(self.module.BaselineError, "seeds"):
            self.module.run_alpha158_lightgbm(
                provider_uri=Path("missing"),
                training_root=Path("missing"),
                output_path=Path("missing"),
                segments=self.segments,
                seeds=(100, 100),
            )
        with self.assertRaisesRegex(self.module.BaselineError, "seeds"):
            self.module.run_alpha158_lightgbm(
                provider_uri=Path("missing"),
                training_root=Path("missing"),
                output_path=Path("missing"),
                segments=self.segments,
                seeds=tuple(range(21)),
            )

    def test_structured_comparison_requires_all_six_baselines(self) -> None:
        dates = ["2023-02-01", "2023-02-02"]
        tickers = ["sh600000", "sz000001"]
        rows = []
        sample_id = 0
        for date_index, date in enumerate(dates):
            for ticker_index, ticker in enumerate(tickers):
                momentum = float((ticker_index * 2 - 1) * (date_index + 1))
                rows.append(
                    {
                        "sample_id": sample_id,
                        "ticker": ticker,
                        "trade_date": date,
                        "split": "validation",
                        "label_excess_10d": momentum * 0.5,
                        "last_value_score": 0.0,
                        "momentum_score": momentum,
                        "reversal_score": -momentum,
                    }
                )
                sample_id += 1
        inputs = pd.DataFrame(rows)
        keys = inputs[["sample_id", "ticker", "trade_date"]]
        external = {
            "zero_shot_kronos": keys.assign(raw_score=[-0.4, 0.4, -0.8, 0.8]),
            "head_only": keys.assign(raw_score=[-0.5, 0.5, -1.0, 1.0]),
            "alpha158_lightgbm": keys.assign(raw_score=[-0.6, 0.6, -1.2, 1.2]),
        }
        report = self.module.build_baseline_comparison(
            baseline_inputs=inputs,
            external_scores=external,
            evaluate_split="validation",
        )
        self.assertEqual(set(report["baselines"]), set(self.module.REQUIRED_BASELINES))
        self.assertEqual(report["sample_count"], 4)
        self.assertIsNone(report["baselines"]["last_value"]["mean_daily_rank_ic"])
        self.assertEqual(
            report["baselines"]["last_value"]["rank_ic_status"],
            "zero_information",
        )
        self.assertAlmostEqual(report["baselines"]["momentum"]["mean_daily_rank_ic"], 1.0)
        self.module.validate_baseline_comparison(report)
        missing = dict(external)
        missing.pop("head_only")
        with self.assertRaisesRegex(self.module.BaselineError, "必须恰好包含"):
            self.module.build_baseline_comparison(
                baseline_inputs=inputs,
                external_scores=missing,
                evaluate_split="validation",
            )

    def test_evaluation_companion_execution_flags_tax_and_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            training.mkdir()
            fixture = self._companion_fixture(training)
            output = training / "runs" / "fixture" / "predictions" / "companion.csv"
            metadata = self.module.build_evaluation_companion(
                training_root=training,
                sample_index_path=fixture["sample"],
                raw_market_source_path=fixture["source"],
                provider_uri=fixture["provider"],
                suspensions_path=fixture["suspensions"],
                price_limits_path=fixture["limits"],
                external_score_artifacts=fixture["artifacts"],
                binding=fixture["binding"],
                output_path=output,
            )
            frame = pd.read_csv(output)
            self.assertEqual(frame["sample_id"].tolist(), [0, 1])
            self.assertEqual(
                frame["entry_date"].tolist(),
                [date.strftime("%Y-%m-%d") for date in fixture["expected_entries"]],
            )
            self.assertEqual(frame["exit_date"].tolist(), ["2023-08-25", "2023-08-28"])
            self.assertFalse(bool(frame.loc[0, "entry_tradable"]))
            self.assertTrue(bool(frame.loc[0, "entry_limit_blocked"]))
            self.assertTrue(bool(frame.loc[0, "exit_limit_blocked"]))
            self.assertTrue(bool(frame.loc[1, "entry_tradable"]))
            self.assertFalse(bool(frame.loc[1, "entry_limit_blocked"]))
            self.assertFalse(bool(frame.loc[1, "exit_limit_blocked"]))
            self.assertEqual(frame["stamp_duty_rate"].tolist(), [0.001, 0.0005])
            self.assertTrue((frame["holding_period_sessions"] == 10).all())
            np.testing.assert_allclose(
                frame["drift_score"], frame["momentum_score"] / 20.0 * 10.0
            )
            self.assertEqual(
                set(metadata["source_artifacts"]),
                {"execution", *self.module.COMPANION_SCORE_COLUMNS},
            )
            alpha_path = Path(fixture["artifacts"]["alpha158_score"]["path"])
            alpha_path.write_text(alpha_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(self.module.BaselineError, "SHA256 漂移"):
                self.module.inspect_evaluation_companion(
                    output, training, binding=fixture["binding"]
                )


if __name__ == "__main__":
    unittest.main()
