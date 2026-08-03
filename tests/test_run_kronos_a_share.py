from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "kronos-market-forecasting" / "scripts"
CLI_PATH = SCRIPTS / "run_kronos_a_share.py"
CONFIG_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "kronos-market-forecasting"
    / "configs"
    / "a_share_daily_v1.yaml"
)
sys.path.insert(0, str(SCRIPTS))


def load_cli():
    spec = importlib.util.spec_from_file_location("run_kronos_a_share", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 {CLI_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeBinding:
    def as_dict(self):
        return {
            "base_model_sha256": "a" * 64,
            "tokenizer_sha256": "b" * 64,
            "config_sha256": "c" * 64,
            "dataset_sha256": "d" * 64,
        }


class UnifiedCliContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli = load_cli()

    def _write_minimal_companion(
        self,
        root: Path,
        name: str,
        *,
        evaluate_split: str = "validation",
        entry_price: float = 10.0,
    ) -> Path:
        import kronos_a_share_baseline as baseline

        root.mkdir(parents=True, exist_ok=True)
        source = root / "bound-score-source.csv"
        source.write_text("sample_id,raw_score\n0,0.1\n", encoding="utf-8")
        source_record = {"path": str(source), "sha256": self.cli.sha256_file(source)}
        execution = root / f"{name}.execution.json"
        execution.write_text(
            json.dumps(
                {
                    "schema_version": baseline.EXECUTION_AUDIT_SCHEMA,
                    "generated_at": "2026-08-03T00:00:00+00:00",
                    "sample_id_sha256": hashlib.sha256(
                        np.asarray([0], dtype=np.int64).tobytes()
                    ).hexdigest(),
                    "row_count": 1,
                    "source_artifacts": {},
                }
            ),
            encoding="utf-8",
        )
        output = root / f"{name}.csv"
        row = {
            "sample_id": 0,
            "entry_date": "2023-01-04",
            "exit_date": "2023-01-17",
            "entry_price_raw": entry_price,
            "exit_price_raw": 10.1,
            "entry_tradable": True,
            "exit_tradable": True,
            "entry_limit_blocked": False,
            "exit_limit_blocked": False,
            "stamp_duty_rate": 0.001,
            "corporate_action_factor": 1.0,
            "corporate_action_event_count": 0,
            "holding_period_sessions": 10,
        }
        for column in baseline.COMPANION_SCORE_COLUMNS:
            row[column] = 0.1
        pd.DataFrame([row]).to_csv(output, index=False, lineterminator="\n")
        sources = {
            column: dict(source_record) for column in baseline.COMPANION_SCORE_COLUMNS
        }
        sources["execution"] = {
            "path": str(execution),
            "sha256": self.cli.sha256_file(execution),
        }
        metadata = {
            "schema_version": baseline.EVALUATION_COMPANION_SCHEMA,
            "input_sha256": self.cli.sha256_file(output),
            "row_count": 1,
            "evaluate_split": evaluate_split,
            "sample_id_sha256": hashlib.sha256(
                np.asarray([0], dtype=np.int64).tobytes()
            ).hexdigest(),
            "binding": self.cli._gate_binding(FakeBinding()),
            "holding_period_sessions": 10,
            "execution_contract": "fixture",
            "drift_contract": "fixture",
            "source_artifacts": sources,
        }
        output.with_suffix(output.suffix + ".metadata.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )
        return output

    def test_parser_exposes_exact_nine_commands(self) -> None:
        parser = self.cli.build_parser()
        subparser_action = next(
            action
            for action in parser._actions
            if action.__class__.__name__ == "_SubParsersAction"
        )
        self.assertEqual(
            set(subparser_action.choices),
            {
                "snapshot",
                "prepare",
                "check",
                "train-adapter",
                "train-scorer",
                "evaluate",
                "score-as-of",
                "inspect-checkpoint",
                "pipeline",
            },
        )

    def test_causal_validation_mode_blocks_future_s2_leakage(self) -> None:
        upstream_path = ROOT / "_downloads" / "Kronos" / "source" / "model" / "module.py"
        spec = importlib.util.spec_from_file_location("kronos_upstream_module_test", upstream_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        upstream = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(upstream)

        class ProbeModel(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.dep_layer = upstream.DependencyAwareLayer(8, n_heads=2)
                self.probe_dropout = torch.nn.Dropout(0.5)

        torch.manual_seed(7)
        model = ProbeModel()
        model.train()
        hidden = torch.randn(1, 6, 8)
        changed = hidden.clone()
        changed[:, 3:, :] += 10.0
        sibling = torch.randn(1, 6, 8)

        model.eval()
        leaked = model.dep_layer(hidden, sibling)
        leaked_changed = model.dep_layer(changed, sibling)
        self.assertGreater(
            float((leaked[:, :3] - leaked_changed[:, :3]).abs().max()),
            1e-5,
        )

        model.train()
        with self.cli._causal_validation_mode(model):
            self.assertFalse(model.training)
            self.assertTrue(model.dep_layer.cross_attn.training)
            self.assertFalse(model.dep_layer.cross_attn.q_proj.training)
            self.assertFalse(model.probe_dropout.training)
            causal = model.dep_layer(hidden, sibling)
            causal_changed = model.dep_layer(changed, sibling)
        self.assertTrue(torch.allclose(causal[:, :3], causal_changed[:, :3], atol=1e-6))
        self.assertTrue(model.training)
        self.assertTrue(model.probe_dropout.training)

    def test_parser_routes_daily_inference_without_adding_a_tenth_command(self) -> None:
        snapshot = self.cli.build_parser().parse_args(
            [
                "snapshot",
                "--inference-as-of",
                "2026-08-03T00:00:00+08:00",
                "--inference-pit-root",
                str(ROOT / "_training" / "kronos_ashare" / "data" / "pit-current"),
            ]
        )
        score = self.cli.build_parser().parse_args(
            [
                "score-as-of",
                "--symbols",
                "300620.SZ",
                "--as-of",
                "2026-08-03T00:00:00+08:00",
                "--inference-snapshot",
                str(ROOT / "_training" / "kronos_ashare" / "data" / "inference"),
            ]
        )
        self.assertEqual(snapshot.command, "snapshot")
        self.assertIsNotNone(snapshot.inference_pit_root)
        self.assertEqual(score.command, "score-as-of")
        self.assertIsNotNone(score.inference_snapshot)
        parsed = self.cli.build_parser().parse_args(["pipeline", "--mode", "smoke"])
        self.assertEqual(parsed.mode, "smoke")
        inspect = self.cli.build_parser().parse_args(
            ["inspect-checkpoint", "--mode", "smoke", "--recover"]
        )
        self.assertEqual(inspect.mode, "smoke")
        self.assertTrue(inspect.recover)

    def test_prepare_routes_optional_raw_pit_normalization_without_tenth_command(self) -> None:
        manifest = ROOT / "_training" / "kronos_ashare" / "data" / "raw" / "normalize.json"
        parsed = self.cli.build_parser().parse_args(
            ["prepare", "--pit-normalization-manifest", str(manifest)]
        )
        self.assertEqual(parsed.command, "prepare")
        self.assertEqual(parsed.pit_normalization_manifest, manifest)

    def test_config_is_strict_and_rejects_unknown_fields(self) -> None:
        payload, digest = self.cli.load_config(CONFIG_PATH)
        self.assertEqual(payload["schema_version"], "kronos-a-share-v1")
        self.assertEqual(len(digest), 64)
        self.assertEqual(
            set(payload["data"]["public_pit"]),
            {
                "version_root",
                "security_master",
                "st_status",
                "suspensions",
                "price_limits",
                "index_membership",
                "corporate_actions",
                "trading_calendar",
                "coverage",
            },
        )
        self.assertEqual(
            payload["training"]["adapter"]["validation_contract"],
            "causal-dependency-cross-attention-v1",
        )
        drifted = copy.deepcopy(payload)
        drifted["training"]["adapter"]["silent_new_option"] = True
        with self.assertRaisesRegex(self.cli.CliContractError, "unknown"):
            self.cli._validate_config(drifted)
        legacy = copy.deepcopy(payload)
        legacy["data"]["public_pit"].pop("security_master")
        legacy["data"]["public_pit"]["securities"] = None
        with self.assertRaisesRegex(self.cli.CliContractError, "unknown=.*securities"):
            self.cli._validate_config(legacy)
        legacy = copy.deepcopy(payload)
        legacy["data"]["public_pit"].pop("st_status")
        legacy["data"]["public_pit"]["trade_status"] = None
        with self.assertRaisesRegex(self.cli.CliContractError, "unknown=.*trade_status"):
            self.cli._validate_config(legacy)

        identity_drift = copy.deepcopy(payload)
        identity_drift["model"]["model_sha256"] = "0" * 64
        with self.assertRaisesRegex(self.cli.CliContractError, "固定模型身份"):
            self.cli._validate_config(identity_drift)

    def test_public_pit_paths_are_canonical_and_share_one_version_root(self) -> None:
        payload, _ = self.cli.load_config(CONFIG_PATH)
        pit_root = (
            ROOT
            / "_training"
            / "kronos_ashare"
            / "data"
            / "normalized"
            / "pit"
            / "pit-v1"
        ).resolve()
        configured = copy.deepcopy(payload)
        configured["data"]["public_pit"]["version_root"] = str(pit_root)
        for table_name in self.cli.PUBLIC_PIT_TABLES:
            configured["data"]["public_pit"][table_name] = str(
                pit_root / f"{table_name}.csv"
            )
        self.cli._validate_config(configured)

        missing_root = copy.deepcopy(payload)
        missing_root["data"]["public_pit"]["security_master"] = str(
            pit_root / "security_master.csv"
        )
        with self.assertRaisesRegex(self.cli.CliContractError, "version_root"):
            self.cli._validate_config(missing_root)

        split_root = copy.deepcopy(configured)
        split_root["data"]["public_pit"]["suspensions"] = str(
            pit_root.parent / "other" / "suspensions.csv"
        )
        with self.assertRaisesRegex(self.cli.CliContractError, "同一 version_root"):
            self.cli._validate_config(split_root)

        wrong_name = copy.deepcopy(configured)
        wrong_name["data"]["public_pit"]["coverage"] = str(
            pit_root / "coverage-v2.csv"
        )
        with self.assertRaisesRegex(self.cli.CliContractError, "coverage.csv"):
            self.cli._validate_config(wrong_name)

    def test_pit_root_override_cannot_escape_training_data_or_drift_from_config(self) -> None:
        context = self.cli.build_context(CONFIG_PATH, create=False)
        expected = (context.layout.data / "normalized" / "pit").resolve()
        self.assertEqual(self.cli._pit_root(context), expected)
        with self.assertRaisesRegex(self.cli.CliContractError, "data 子目录"):
            self.cli._pit_root(context, ROOT)

        configured = copy.deepcopy(context.config)
        version_root = (expected / "pit-v1").resolve()
        configured["data"]["public_pit"]["version_root"] = str(version_root)
        configured_context = SimpleNamespace(
            config=configured,
            layout=context.layout,
        )
        self.assertEqual(self.cli._pit_root(configured_context), version_root)
        with self.assertRaisesRegex(self.cli.CliContractError, "不一致"):
            self.cli._pit_root(configured_context, expected / "pit-v2")

    def test_config_cannot_weaken_release_thresholds_or_fixed_splits(self) -> None:
        payload, _ = self.cli.load_config(CONFIG_PATH)
        weakened = copy.deepcopy(payload)
        weakened["evaluation"]["validation_rank_ic_min"] = -1
        with self.assertRaisesRegex(self.cli.CliContractError, "准出下限"):
            self.cli._validate_config(weakened)
        weakened = copy.deepcopy(payload)
        weakened["evaluation"]["stress_round_trip_cost_bps"] = "0"
        with self.assertRaisesRegex(self.cli.CliContractError, "35/70"):
            self.cli._validate_config(weakened)
        drifted_split = copy.deepcopy(payload)
        drifted_split["data"]["splits"]["validation"][0] = "2023-02-01"
        with self.assertRaisesRegex(self.cli.CliContractError, "固定时间切分"):
            self.cli._validate_config(drifted_split)

    def test_component_load_rejects_actual_runtime_identity_drift(self) -> None:
        config, _ = self.cli.load_config(CONFIG_PATH)
        context = SimpleNamespace(config=config)
        report = {
            "source_revision": config["model"]["source_revision"],
            "model_revision": config["model"]["model_revision"],
            "tokenizer_revision": config["model"]["tokenizer_revision"],
            "model_sha256": "0" * 64,
            "tokenizer_sha256": config["model"]["tokenizer_sha256"],
        }
        import run_kronos_forecast as base_cli

        with mock.patch.object(base_cli, "validate_runtime", return_value=report):
            with self.assertRaisesRegex(self.cli.CliBlocked, "model_sha256"):
                self.cli._load_kronos_components(context, "cpu")

    def test_full_training_rejects_provisional_but_smoke_accepts_it(self) -> None:
        with self.assertRaises(self.cli.CliBlocked):
            self.cli._assert_data_allowed(
                "local_provisional", engineering_smoke=False
            )
        self.cli._assert_data_allowed(
            "local_provisional", engineering_smoke=True
        )
        with self.assertRaises(self.cli.CliBlocked):
            self.cli._assert_data_allowed("blocked", engineering_smoke=True)

    def test_adapter_batch_shifts_tokens_and_masks_only_future_ten(self) -> None:
        arrays = {
            "s1": np.tile(np.arange(100, dtype=np.uint16), (3, 1)),
            "s2": np.tile(np.arange(100, dtype=np.uint16), (3, 1)),
            "stamp": np.zeros((3, 100, 5), dtype=np.uint8),
        }
        batch = self.cli._adapter_batch(
            arrays, np.asarray([0, 2], dtype=np.int64), "cpu"
        )
        self.assertEqual(tuple(batch.s1_ids.shape), (2, 99))
        self.assertEqual(tuple(batch.s1_targets.shape), (2, 99))
        self.assertTrue(torch.equal(batch.s1_ids[:, 1:], batch.s1_targets[:, :-1]))
        self.assertEqual(int(batch.future_mask.sum()), 20)
        self.assertFalse(bool(batch.future_mask[:, :89].any()))
        self.assertTrue(bool(batch.future_mask[:, 89:].all()))

    def test_deterministic_batches_are_resume_stable(self) -> None:
        members = np.asarray([2, 4, 6, 8, 10])
        first = self.cli._deterministic_batch(
            members, microstep=7, batch_size=4, seed=100
        )
        resumed = self.cli._deterministic_batch(
            members, microstep=7, batch_size=4, seed=100
        )
        np.testing.assert_array_equal(first, resumed)
        self.assertTrue(set(first).issubset(set(members)))

    def test_smoke_uses_separate_dataset_and_run_namespaces(self) -> None:
        full = self.cli.build_context(CONFIG_PATH, create=False)
        smoke = self.cli.build_context(CONFIG_PATH, create=False, variant="smoke")
        self.assertNotEqual(full.dataset_id, smoke.dataset_id)
        self.assertNotEqual(full.run_id, smoke.run_id)
        self.assertTrue(smoke.dataset_id.endswith("-smoke-v4"))
        self.assertTrue(smoke.run_id.endswith("-smoke-v4"))
        self.assertNotEqual(full.token_dir, smoke.token_dir)
        self.assertNotEqual(full.checkpoint_dir, smoke.checkpoint_dir)

    def test_full_and_smoke_training_share_one_preload_global_lock(self) -> None:
        full = self.cli.build_context(CONFIG_PATH, create=False)
        smoke = self.cli.build_context(CONFIG_PATH, create=False, variant="smoke")
        full_lock = self.cli._global_training_lock_path(full)
        smoke_lock = self.cli._global_training_lock_path(smoke)
        self.assertEqual(full_lock, smoke_lock)
        self.assertEqual(full_lock, full.layout.registry / ".model-training.lock")

        from kronos_a_share_training import CheckpointBusyError, CheckpointFileLock

        with CheckpointFileLock(full_lock):
            with self.assertRaises(CheckpointBusyError):
                self.cli.command_train_adapter(
                    SimpleNamespace(config=CONFIG_PATH, _variant="smoke")
                )

    def test_read_only_context_still_routes_all_process_caches_to_training_root(self) -> None:
        with mock.patch.object(self.cli, "apply_environment_mapping") as apply_mapping:
            context = self.cli.build_context(CONFIG_PATH, create=False)
        apply_mapping.assert_called_once_with(context.layout)

    def test_real_cli_context_repairs_cached_c_drive_tempfile(self) -> None:
        script = (
            "import json,os,sys,tempfile; from pathlib import Path; "
            f"sys.path.insert(0, {str(SCRIPTS)!r}); "
            "before=tempfile.gettempdir(); import run_kronos_a_share as cli; "
            f"cli.build_context(Path({str(CONFIG_PATH)!r}), create=False); "
            "print(json.dumps({'before':before,'env':os.environ['TEMP'],"
            "'after':tempfile.gettempdir()}))"
        )
        environment = os.environ.copy()
        c_temp = Path.home() / "AppData" / "Local" / "Temp"
        for name in ("TEMP", "TMP", "TMPDIR"):
            environment[name] = str(c_temp)
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", script],
            cwd=ROOT,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        expected = str(
            (
                ROOT
                / "_training"
                / "kronos_ashare"
                / "runtime"
                / "tmp"
            ).resolve()
        )
        self.assertTrue(payload["before"].lower().startswith("c:"))
        self.assertEqual(payload["env"], expected)
        self.assertEqual(payload["after"], expected)

    def test_prepare_rehashes_snapshot_before_consuming_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            data_root = root / "data"
            snapshot = data_root / "raw" / "snapshot-v1"
            snapshot.mkdir(parents=True)
            (snapshot / "source_manifest.json").write_text(
                "{}", encoding="utf-8"
            )
            context = SimpleNamespace(
                layout=SimpleNamespace(root=root, data=data_root),
                config={"data": {"snapshot_id": "snapshot-v1"}},
            )
            with (
                mock.patch.object(self.cli, "build_context", return_value=context),
                mock.patch.object(
                    self.cli,
                    "verify_immutable_snapshot",
                    side_effect=self.cli.CliBlocked("snapshot_hash_drift"),
                ) as verify_snapshot,
                mock.patch.object(self.cli, "_pit_root") as pit_root,
            ):
                with self.assertRaisesRegex(
                    self.cli.CliBlocked, "snapshot_hash_drift"
                ):
                    self.cli.command_prepare(
                        SimpleNamespace(
                            config=CONFIG_PATH,
                            pit_root=None,
                            max_samples_per_split=None,
                            force=False,
                            tokenize=False,
                            device="cpu",
                        )
                    )
            verify_snapshot.assert_called_once_with(
                snapshot / "source_manifest.json",
                training_root=root,
                project_root=ROOT,
            )
            pit_root.assert_not_called()

    def test_prepare_fails_closed_when_raw_pit_publication_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training_root = Path(tmp) / "training"
            snapshot_dir = training_root / "data" / "raw" / "snapshot-v1"
            snapshot_dir.mkdir(parents=True)
            snapshot_manifest = snapshot_dir / "source_manifest.json"
            snapshot_manifest.write_text("{}", encoding="utf-8")
            pit_root = training_root / "data" / "normalized" / "pit-v1"
            context = SimpleNamespace(
                layout=SimpleNamespace(root=training_root, data=training_root / "data"),
                config={"data": {"snapshot_id": "snapshot-v1"}},
                dataset_dir=training_root / "data" / "datasets" / "dataset-v1",
            )
            args = SimpleNamespace(
                config=CONFIG_PATH,
                pit_root=pit_root,
                pit_normalization_manifest=training_root / "normalize.json",
                max_samples_per_split=None,
                force=False,
                tokenize=False,
                device="cpu",
            )
            with (
                mock.patch.object(self.cli, "build_context", return_value=context),
                mock.patch.object(self.cli, "verify_immutable_snapshot"),
                mock.patch.object(self.cli, "_pit_root", return_value=pit_root),
                mock.patch.object(
                    self.cli,
                    "publish_normalized_pit_bundle",
                    side_effect=self.cli.PublicDataError("same_priority_conflict"),
                ) as publish,
            ):
                with self.assertRaisesRegex(self.cli.CliBlocked, "归一化发布失败"):
                    self.cli.command_prepare(args)
            publish.assert_called_once_with(
                args.pit_normalization_manifest,
                pit_root,
                training_root,
            )

    def test_production_rejects_legacy_sample_without_survivorship_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dataset_dir = Path(temporary).resolve() / "dataset"
            dataset_dir.mkdir()
            sample_index = dataset_dir / "sample_index.csv"
            sample_index.write_text(
                "sample_id,ticker\n0,sh600000\n", encoding="utf-8"
            )
            sample_manifest = dataset_dir / "sample_manifest.json"
            sample_manifest.write_text(
                json.dumps(
                    {
                        "sample_trade_state_checked": True,
                        "sample_index_sha256": self.cli.sha256_file(sample_index),
                    }
                ),
                encoding="utf-8",
            )
            contract = dataset_dir / "prepare_contract.json"
            contract.write_text(
                json.dumps(
                    {
                        "data_status": "production_ready",
                        "sample_manifest_sha256": self.cli.sha256_file(sample_manifest),
                    }
                ),
                encoding="utf-8",
            )
            context = SimpleNamespace(dataset_dir=dataset_dir)
            with self.assertRaisesRegex(
                self.cli.CliBlocked,
                "\u5e78\u5b58\u8005\u504f\u5dee\u5ba1\u8ba1",
            ):
                self.cli._validate_prepared_index(
                    context,
                    {"data_status": "production_ready"},
                )

    def test_production_accepts_bound_zero_gap_survivorship_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dataset_dir = Path(temporary).resolve() / "dataset"
            dataset_dir.mkdir()
            sample_index = dataset_dir / "sample_index.csv"
            sample_index.write_text(
                "sample_id,ticker\n0,sh600000\n", encoding="utf-8"
            )
            sample_manifest = dataset_dir / "sample_manifest.json"
            sample_manifest.write_text(
                json.dumps(
                    {
                        "sample_trade_state_checked": True,
                        "sample_index_sha256": self.cli.sha256_file(sample_index),
                        "survivorship_bias_audit": {
                            "schema_version": "kronos-a-share-survivorship-audit-v1",
                            "verified": True,
                            "checked_member_dates": 100,
                            "missing_historical_day_file_count": 0,
                            "missing_suspension_state_member_dates": 0,
                            "unexplained_missing_quote_member_dates": 0,
                        },
                    }
                ),
                encoding="utf-8",
            )
            contract = dataset_dir / "prepare_contract.json"
            contract.write_text(
                json.dumps(
                    {
                        "data_status": "production_ready",
                        "sample_manifest_sha256": self.cli.sha256_file(sample_manifest),
                    }
                ),
                encoding="utf-8",
            )
            context = SimpleNamespace(dataset_dir=dataset_dir)
            result = self.cli._validate_prepared_index(
                context,
                {"data_status": "production_ready"},
            )
            self.assertTrue(result["survivorship_bias_audit"]["verified"])

    def test_stage_reference_never_confuses_adapter_and_scorer_best(self) -> None:
        manifests = {
            "adapter-step-00000010": {
                "stage": "adapter",
                "checkpoint_name": "adapter-step-00000010",
                "step": 10,
                "created_at_ns": 1,
                "is_best": True,
            },
            "scorer-step-00000002": {
                "stage": "scorer",
                "checkpoint_name": "scorer-step-00000002",
                "step": 2,
                "created_at_ns": 2,
                "is_best": True,
            },
        }

        class Store:
            def recover(self):
                return {"valid": list(manifests)}

            def inspect(self, name):
                return manifests[name]

        self.assertEqual(
            self.cli._stage_reference(Store(), stage="adapter", kind="best"),
            "adapter-step-00000010",
        )
        self.assertEqual(
            self.cli._stage_reference(Store(), stage="scorer", kind="best"),
            "scorer-step-00000002",
        )

    def test_future_dates_normalize_timezone_without_changing_local_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "future.csv"
            dates = pd.date_range("2026-08-03", periods=10, freq="B", tz="Asia/Shanghai")
            pd.DataFrame({"timestamps": dates.astype(str)}).to_csv(path, index=False)
            actual = self.cli._future_dates(
                path, pd.Timestamp("2026-07-31T15:00:00+08:00")
            )
            self.assertIsNone(actual.tz)
            self.assertEqual(len(actual), 10)
            self.assertEqual(actual[0], pd.Timestamp("2026-08-03"))

    def test_future_dates_reject_intraday_points(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "future.csv"
            dates = pd.date_range("2026-08-03T15:01:00", periods=10, freq="min")
            pd.DataFrame({"timestamps": dates.astype(str)}).to_csv(path, index=False)
            with self.assertRaisesRegex(self.cli.CliContractError, "日频交易日期"):
                self.cli._future_dates(
                    path, pd.Timestamp("2026-07-31T00:00:00+08:00")
                )

    def test_future_dates_are_hash_bound_to_inference_raw_response(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            snapshot_root = Path(temporary) / "inference"
            path = snapshot_root / "pit" / "raw" / "official-calendar.csv"
            path.parent.mkdir(parents=True)
            dates = pd.bdate_range("2026-08-03", periods=12)
            pd.DataFrame({"timestamps": dates.astype(str)}).to_csv(path, index=False)
            provenance_path = snapshot_root / "pit" / "provenance" / "calendar.json"
            provenance_path.parent.mkdir(parents=True)
            provenance_path.write_text(
                json.dumps(
                    {
                        "schema_version": "kronos-a-share-pit-provenance-v1",
                        "sources": [
                            {
                                "path": path.relative_to(snapshot_root / "pit").as_posix(),
                                "source_class": "official_primary",
                                "role": "authoritative",
                                "artifact_role": "trading_calendar",
                                "artifact_schema_version": "kronos-a-share-trading-calendar-v1",
                                "url": "https://www.sse.com.cn/official-calendar.csv",
                                "sha256": self.cli.sha256_file(path),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            manifest = {
                "pit_files": [
                    {
                        "relative_path": path.relative_to(snapshot_root).as_posix(),
                        "role": "raw_response",
                        "sha256": self.cli.sha256_file(path),
                    },
                    {
                        "relative_path": provenance_path.relative_to(
                            snapshot_root
                        ).as_posix(),
                        "role": "provenance_manifest",
                        "sha256": self.cli.sha256_file(provenance_path),
                    },
                ]
            }
            actual = self.cli._future_dates(
                path,
                pd.Timestamp("2026-07-31T00:00:00+08:00"),
                inference_manifest=manifest,
                snapshot_root=snapshot_root,
            )
            self.assertEqual(len(actual), 10)
            outside = Path(temporary) / "outside.csv"
            outside.write_bytes(path.read_bytes())
            with self.assertRaisesRegex(self.cli.CliBlocked, "inference snapshot"):
                self.cli._future_dates(
                    outside,
                    pd.Timestamp("2026-07-31T00:00:00+08:00"),
                    inference_manifest=manifest,
                    snapshot_root=snapshot_root,
                )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["sources"][0]["source_class"] = "public_secondary"
            provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
            manifest["pit_files"][1]["sha256"] = self.cli.sha256_file(
                provenance_path
            )
            with self.assertRaisesRegex(self.cli.CliBlocked, "固定 schema"):
                self.cli._future_dates(
                    path,
                    pd.Timestamp("2026-07-31T00:00:00+08:00"),
                    inference_manifest=manifest,
                    snapshot_root=snapshot_root,
                )

            provenance["sources"][0]["source_class"] = "official_primary"
            provenance["sources"][0]["artifact_role"] = "arbitrary_timestamps"
            provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
            manifest["pit_files"][1]["sha256"] = self.cli.sha256_file(
                provenance_path
            )
            with self.assertRaisesRegex(self.cli.CliBlocked, "trading_calendar"):
                self.cli._future_dates(
                    path,
                    pd.Timestamp("2026-07-31T00:00:00+08:00"),
                    inference_manifest=manifest,
                    snapshot_root=snapshot_root,
                )

            provenance["sources"][0]["artifact_role"] = "trading_calendar"
            provenance["sources"][0]["url"] = "https://example.com/calendar.csv"
            provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
            manifest["pit_files"][1]["sha256"] = self.cli.sha256_file(
                provenance_path
            )
            with self.assertRaisesRegex(self.cli.CliBlocked, "允许官方域名"):
                self.cli._future_dates(
                    path,
                    pd.Timestamp("2026-07-31T00:00:00+08:00"),
                    inference_manifest=manifest,
                    snapshot_root=snapshot_root,
                )

    def test_forecast_paths_use_explicit_samples_and_report_dispersion(self) -> None:
        history_dates = pd.Series(pd.bdate_range("2026-03-30", periods=90))
        future_dates = pd.bdate_range(history_dates.iloc[-1] + pd.Timedelta(days=1), periods=10)
        base = np.linspace(10.0, 12.0, 90, dtype=np.float32)
        adjusted = pd.DataFrame(
            {
                "open": base,
                "high": base + 0.2,
                "low": base - 0.2,
                "close": base + 0.1,
                "volume": np.linspace(1000, 2000, 90, dtype=np.float32),
                "amount": np.linspace(10000, 24000, 90, dtype=np.float32),
            }
        )

        class FakePredictor:
            def __init__(self):
                self.calls = 0

            def generate(self, x, x_stamp, y_stamp, pred_len, *_args):
                self.calls += 1
                self.last_x = np.asarray(x)
                self.last_x_stamp = np.asarray(x_stamp)
                self.last_y_stamp = np.asarray(y_stamp)
                result = np.zeros((1, pred_len, 6), dtype=np.float32)
                result[:, :, 1] = 2.0
                result[:, :, 2] = -2.0
                result[:, :, 3] = float(self.calls) * 0.1
                return result

        predictor = FakePredictor()
        forecast, dispersion = self.cli._forecast_path_samples(
            predictor,
            adjusted_history=adjusted,
            history_timestamps=history_dates,
            future_timestamps=future_dates,
            sample_count=3,
            temperature=1.0,
            top_k=0,
            top_p=0.9,
        )
        self.assertEqual(predictor.calls, 3)
        self.assertEqual(predictor.last_x.shape, (1, 90, 6))
        self.assertEqual(predictor.last_x_stamp.shape, (1, 90, 5))
        self.assertEqual(predictor.last_y_stamp.shape, (1, 10, 5))
        self.assertEqual(len(forecast), 10)
        self.assertGreater(dispersion, 0)

    def test_forecast_paths_reject_nonfinite_and_invalid_ohlcva(self) -> None:
        history_dates = pd.Series(pd.bdate_range("2026-03-30", periods=90))
        future_dates = pd.bdate_range(
            history_dates.iloc[-1] + pd.Timedelta(days=1), periods=10
        )
        base = np.linspace(10.0, 12.0, 90, dtype=np.float32)
        adjusted = pd.DataFrame(
            {
                "open": base,
                "high": base + 0.2,
                "low": base - 0.2,
                "close": base + 0.1,
                "volume": np.linspace(1000, 2000, 90, dtype=np.float32),
                "amount": np.linspace(10000, 24000, 90, dtype=np.float32),
            }
        )

        class InvalidPredictor:
            def __init__(self, mutation):
                self.mutation = mutation

            def generate(self, _x, _x_stamp, _y_stamp, pred_len, *_args):
                result = np.zeros((1, pred_len, 6), dtype=np.float32)
                result[:, :, 1] = 2.0
                result[:, :, 2] = -2.0
                self.mutation(result)
                return result

        cases = (
            (lambda result: result.__setitem__((0, 0, 0), np.nan), "NaN/Inf"),
            (lambda result: result.__setitem__((0, 0, 1), -10.0), "OHLC"),
            (lambda result: result.__setitem__((0, 0, 4), -10.0), "volume/amount"),
        )
        for mutation, expected in cases:
            with self.subTest(expected=expected), self.assertRaisesRegex(
                self.cli.CliContractError, expected
            ):
                self.cli._forecast_path_samples(
                    InvalidPredictor(mutation),
                    adjusted_history=adjusted,
                    history_timestamps=history_dates,
                    future_timestamps=future_dates,
                    sample_count=1,
                    temperature=1.0,
                    top_k=0,
                    top_p=0.9,
                )

    def test_controlled_evaluation_rejects_missing_generated_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            context = SimpleNamespace(
                predictions_dir=root / "predictions",
                run_id="run-v1",
                dataset_id="dataset-v1",
            )
            context.predictions_dir.mkdir()
            with self.assertRaisesRegex(
                self.cli.CliContractError, "受控生成"
            ):
                self.cli._controlled_evaluation_frame(
                    context,
                    binding=FakeBinding(),
                    checkpoint={
                        "checkpoint_name": "scorer-step-00000001",
                        "files": {"state.pt": {"sha256": "e" * 64}},
                    },
                    adapter_hash="a" * 64,
                    scorer_checkpoint_hash="e" * 64,
                    companion_path=root / "external.csv",
                    live_predictions=pd.DataFrame(),
                )

    def test_controlled_evaluation_rejects_rehashed_forged_scores(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            predictions = root / "predictions"
            predictions.mkdir()
            path = predictions / "validation_predictions.csv"
            forged = pd.DataFrame(
                {
                    "sample_id": [0],
                    "trade_date": ["2023-01-03"],
                    "instrument_id": [7],
                    "raw_score": [99.0],
                    "label_excess_10d": [0.1],
                }
            )
            forged.to_csv(path, index=False)
            metadata = {
                "schema_version": "kronos-a-share-controlled-predictions-v2",
                "prediction_contract": "live-checkpoint-recompute-required-v1",
                "run_id": "run-v1",
                "dataset_id": "dataset-v1",
                "evaluate_split": "validation",
                "binding": self.cli._gate_binding(FakeBinding()),
                "evaluated_checkpoint": "scorer-step-00000001",
                "adapter_hash": "a" * 64,
                "scorer_checkpoint_hash": "e" * 64,
                "prediction_sha256": self.cli.sha256_file(path),
                "row_count": 1,
                "sample_id_sha256": hashlib.sha256(
                    np.asarray([0], dtype=np.int64).tobytes()
                ).hexdigest(),
            }
            path.with_suffix(path.suffix + ".metadata.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            context = SimpleNamespace(
                predictions_dir=predictions,
                run_id="run-v1",
                dataset_id="dataset-v1",
                layout=SimpleNamespace(root=root),
            )
            live = forged.copy()
            live["raw_score"] = 0.25
            arrays = {
                "split": np.asarray([self.cli.SPLIT_CODES["validation"]]),
                "label": np.asarray([0.1], dtype=np.float32),
                "trade_date": np.asarray([20230103], dtype=np.int32),
                "instrument_id": np.asarray([7], dtype=np.int32),
            }
            with (
                mock.patch.object(self.cli, "_load_cache", return_value={"arrays": arrays}),
                self.assertRaisesRegex(self.cli.CliContractError, "raw_score"),
            ):
                self.cli._controlled_evaluation_frame(
                    context,
                    binding=FakeBinding(),
                    checkpoint={"checkpoint_name": "scorer-step-00000001"},
                    adapter_hash="a" * 64,
                    scorer_checkpoint_hash="e" * 64,
                    companion_path=root / "unused.csv",
                    live_predictions=live,
                )

    def test_formal_rebuild_rejects_rehashed_forged_companion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            canonical = self._write_minimal_companion(root, "canonical")
            rebuilt = self._write_minimal_companion(root, "rebuilt")
            forged = pd.read_csv(canonical)
            forged.loc[0, "entry_price_raw"] = 1.0
            forged.to_csv(canonical, index=False, lineterminator="\n")
            metadata_path = canonical.with_suffix(canonical.suffix + ".metadata.json")
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["input_sha256"] = self.cli.sha256_file(canonical)
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            context = SimpleNamespace(layout=SimpleNamespace(root=root))
            with self.assertRaisesRegex(
                self.cli.CliContractError, "现场重建结果不一致"
            ):
                self.cli._assert_rebuilt_companion_matches(
                    context,
                    canonical_path=canonical,
                    rebuilt_path=rebuilt,
                    binding=FakeBinding(),
                    evaluate_split="validation",
                )

    def test_formal_rebuild_rejects_rehashed_baseline_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            canonical = self._write_minimal_companion(root, "canonical")
            rebuilt = self._write_minimal_companion(root, "rebuilt")
            forged_source = root / "forged-zero-shot.csv"
            forged_source.write_text(
                "sample_id,raw_score\n0,0.9\n", encoding="utf-8"
            )
            metadata_path = canonical.with_suffix(canonical.suffix + ".metadata.json")
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["source_artifacts"]["zero_shot_score"] = {
                "path": str(forged_source),
                "sha256": self.cli.sha256_file(forged_source),
            }
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            context = SimpleNamespace(layout=SimpleNamespace(root=root))
            with self.assertRaisesRegex(
                self.cli.CliContractError, "基线来源与现场重建不一致"
            ):
                self.cli._assert_rebuilt_companion_matches(
                    context,
                    canonical_path=canonical,
                    rebuilt_path=rebuilt,
                    binding=FakeBinding(),
                    evaluate_split="validation",
                )

    def test_force_recompute_companion_uses_fresh_baseline_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            predictions = root / "predictions"
            data_root = root / "data"
            dataset_dir = root / "dataset"
            snapshot = root / "snapshot"
            pit = root / "pit"
            for path in (predictions, data_root, dataset_dir, snapshot, pit):
                path.mkdir(parents=True)
            for name in ("corporate_actions", "suspensions", "price_limits"):
                (pit / f"{name}.csv").write_text("fixture\n", encoding="utf-8")
            for name in (
                "zero_shot_scores.csv",
                "head_only_scores.csv",
                "alpha158_scores.csv",
                "alpha158_lightgbm_raw.csv",
            ):
                (predictions / name).write_text("forged\n", encoding="utf-8")
            output = root / "formal" / "validation_baselines.csv"
            context = SimpleNamespace(
                layout=SimpleNamespace(root=root, data=data_root),
                predictions_dir=predictions,
                dataset_dir=dataset_dir,
                dataset_id="dataset-v1",
                config={"data": {"splits": {}}},
            )

            def run_alpha(*_args, **kwargs):
                kwargs["output_path"].parent.mkdir(parents=True, exist_ok=True)
                pd.DataFrame({"sample_id": [0], "raw_score": [0.1]}).to_csv(
                    kwargs["output_path"], index=False
                )

            def build_companion(*_args, **kwargs):
                kwargs["output_path"].parent.mkdir(parents=True, exist_ok=True)
                kwargs["output_path"].write_text("sample_id\n0\n", encoding="utf-8")

            import kronos_a_share_baseline as baseline

            with (
                mock.patch.object(
                    self.cli,
                    "_load_cache",
                    return_value={
                        "arrays": {
                            "split": np.asarray(
                                [self.cli.SPLIT_CODES["validation"]]
                            )
                        }
                    },
                ),
                mock.patch.object(self.cli, "_pit_root", return_value=pit),
                mock.patch.object(
                    self.cli,
                    "_pit_table_path",
                    side_effect=lambda _root, name: pit / f"{name}.csv",
                ),
                mock.patch.object(
                    self.cli, "_snapshot_directory", return_value=snapshot
                ),
                mock.patch.object(
                    self.cli,
                    "_ensure_zero_shot_scores",
                    return_value={"path": "zero", "sha256": "a" * 64},
                ) as zero,
                mock.patch.object(
                    self.cli,
                    "_ensure_head_only_scores",
                    return_value={"path": "head", "sha256": "b" * 64},
                ) as head,
                mock.patch.object(
                    baseline,
                    "build_project_qlib_provider",
                    return_value={"manifest_sha256": "c" * 64},
                ) as provider,
                mock.patch.object(
                    baseline, "run_alpha158_lightgbm", side_effect=run_alpha
                ) as alpha,
                mock.patch.object(
                    baseline, "build_evaluation_companion", side_effect=build_companion
                ),
                mock.patch.object(baseline, "inspect_evaluation_companion"),
            ):
                actual = self.cli._ensure_evaluation_companion(
                    context,
                    binding=FakeBinding(),
                    output_path=output,
                    device="cpu",
                    chunk_size=1,
                    evaluate_split="validation",
                    force_recompute_baselines=True,
                )
            self.assertEqual(actual, output)
            self.assertFalse(zero.call_args.kwargs["reuse_existing"])
            self.assertFalse(head.call_args.kwargs["reuse_existing"])
            self.assertNotEqual(
                zero.call_args.kwargs["output_path"],
                predictions / "zero_shot_scores.csv",
            )
            self.assertIn("formal-recomputed-sources", str(provider.call_args.kwargs["provider_uri"]))
            self.assertIn("formal-recomputed-sources", str(alpha.call_args.kwargs["output_path"]))

    def test_cross_split_companion_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            companion = self._write_minimal_companion(
                root, "development", evaluate_split="development_test"
            )
            import kronos_a_share_baseline as baseline

            with self.assertRaisesRegex(baseline.BaselineError, "evaluate_split"):
                baseline.inspect_evaluation_companion(
                    companion,
                    root,
                    binding=FakeBinding(),
                    evaluate_split="locked_retrospective",
                )

    def test_adapter_release_metrics_come_from_committed_checkpoint(self) -> None:
        config, _ = self.cli.load_config(CONFIG_PATH)
        context = SimpleNamespace(
            checkpoint_dir=Path("D:/fixture/checkpoints"),
            config=config,
        )

        class FakeStore:
            def __init__(self, *_args, **_kwargs):
                pass

            def inspect(self, reference):
                return {
                    "stage": "adapter",
                    "checkpoint_name": reference,
                    "metric": 0.9,
                    "files": {"state.pt": {"sha256": "a" * 64}},
                }

        extra = {
            "zero_shot_validation_ce": 1.0,
            "best_validation_ce": 0.9,
            "validation_contract": "causal-dependency-cross-attention-v1",
            "engineering_smoke": False,
            "peak_gpu_memory_bytes": 1024,
            "gpu_memory_limit_bytes": 3 * 1024**3,
        }
        import kronos_a_share_training

        with (
            mock.patch.object(self.cli, "_binding", return_value=FakeBinding()),
            mock.patch.object(kronos_a_share_training, "CheckpointStore", FakeStore),
            mock.patch.object(self.cli, "_checkpoint_extra_state", return_value=extra),
        ):
            evidence = self.cli._adapter_checkpoint_release_metrics(
                context,
                reference="adapter-step-00000001",
                expected_hash="a" * 64,
            )
        self.assertAlmostEqual(evidence["adapter_ce_improvement"], 0.1)

    def test_live_adapter_ce_overrides_forged_declared_metrics(self) -> None:
        config, _ = self.cli.load_config(CONFIG_PATH)
        context = SimpleNamespace(config=config)

        class FakeStore:
            def load(self, *_args, **_kwargs):
                return SimpleNamespace(stage="adapter")

        components = SimpleNamespace(model=object(), device="cpu")
        arrays = {"split": np.asarray([self.cli.SPLIT_CODES["validation"]])}
        declared = {
            "zero_shot_validation_ce": 1.0,
            "best_validation_ce": 0.1,
            "adapter_ce_improvement": 0.9,
            "peak_gpu_memory_bytes": 1,
            "gpu_memory_limit_bytes": 3 * 1024**3,
        }
        with (
            mock.patch.object(
                self.cli,
                "_adapter_checkpoint_release_metrics",
                return_value=declared,
            ),
            mock.patch.object(self.cli, "_load_cache", return_value={"arrays": arrays}),
            mock.patch.object(
                self.cli, "_load_kronos_components", return_value=components
            ),
            mock.patch.object(
                self.cli,
                "_validation_adapter_ce",
                side_effect=[1.0, 1.1],
            ),
        ):
            evidence = self.cli._live_adapter_checkpoint_release_metrics(
                context,
                store=FakeStore(),
                reference="adapter-step-00000001",
                expected_hash="a" * 64,
                device="cpu",
                chunk_size=1,
            )
        self.assertAlmostEqual(evidence["adapter_ce_improvement"], -0.1)
        self.assertFalse(evidence["declaration_matches_live"])
        self.assertEqual(evidence["release_metric_source"], "live_validation_cache_recompute")

    def test_scorer_lora_must_match_declared_adapter_lora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            adapter_name = "adapter-step-00000001"
            scorer_name = "scorer-step-00000002"
            (root / adapter_name).mkdir()
            (root / scorer_name).mkdir()
            torch.save(
                {"lora_state": {"target.lora_A": torch.tensor([[1.0]])}, "extra_state": {}},
                root / adapter_name / "state.pt",
            )
            torch.save(
                {
                    "lora_state": {"target.lora_A": torch.tensor([[2.0]])},
                    "extra_state": {
                        "adapter_checkpoint": adapter_name,
                        "adapter_hash": "a" * 64,
                        "engineering_smoke": False,
                    },
                },
                root / scorer_name / "state.pt",
            )

            class FakeStore:
                def __init__(self):
                    self.root = root

                def inspect(self, reference):
                    if reference == adapter_name:
                        return {
                            "stage": "adapter",
                            "checkpoint_name": adapter_name,
                            "files": {"state.pt": {"sha256": "a" * 64}},
                        }
                    return {
                        "stage": "scorer",
                        "checkpoint_name": scorer_name,
                        "files": {"state.pt": {"sha256": "e" * 64}},
                    }

            with self.assertRaisesRegex(self.cli.CliContractError, "LoRA 张量"):
                self.cli._scorer_checkpoint_hashes(
                    FakeStore(), FakeStore().inspect(scorer_name)
                )
            torch.save(
                {
                    "lora_state": {"target.lora_A": torch.tensor([[1.0]])},
                    "extra_state": {
                        "adapter_checkpoint": adapter_name,
                        "adapter_hash": "a" * 64,
                        "engineering_smoke": True,
                    },
                },
                root / scorer_name / "state.pt",
            )
            with self.assertRaisesRegex(self.cli.CliContractError, "engineering_smoke"):
                self.cli._scorer_checkpoint_hashes(
                    FakeStore(), FakeStore().inspect(scorer_name)
                )

    def test_gate_has_adapter_forecast_binding_contract_and_is_atomic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            checkpoint_dir = root / "runs" / "r" / "checkpoints"
            checkpoint_dir.mkdir(parents=True)
            context = SimpleNamespace(
                run_id="run-v1",
                checkpoint_dir=checkpoint_dir,
                layout=SimpleNamespace(root=root),
            )
            gate = self.cli._write_gate(
                context,
                binding=FakeBinding(),
                gate_status="blocked",
                adapter_hash="e" * 64,
                scorer_checkpoint_hash="f" * 64,
                evaluated_checkpoint="scorer-step-00000001",
                reasons=["local_provisional"],
                verification_status="unverified",
            )
            persisted = json.loads(
                (checkpoint_dir / "gate.json").read_text(encoding="utf-8")
            )
            self.assertEqual(persisted, gate)
            self.assertEqual(gate["schema_version"], "kronos-a-share-gate-v2")
            self.assertEqual(gate["gate_sequence"], 1)
            self.assertTrue((checkpoint_dir / "gate-head.json").is_file())
            self.assertEqual(len(list((checkpoint_dir / "gate-lineage").glob("*.json"))), 1)
            self.assertEqual(
                gate["binding"],
                {
                    "base_model_sha256": "a" * 64,
                    "tokenizer_sha256": "b" * 64,
                    "data_sha256": "d" * 64,
                    "config_sha256": "c" * 64,
                },
            )
            self.assertEqual(gate["output_type"], "N/A")
            self.assertEqual(
                list(checkpoint_dir.glob(".gate.json.*.tmp")), []
            )
            gate_hash = hashlib.sha256(
                (checkpoint_dir / "gate.json").read_bytes()
            ).hexdigest()
            receipt_path = checkpoint_dir / "gate-receipts" / f"{gate_hash}.json"
            self.assertTrue(receipt_path.is_file())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["gate_sha256"], gate_hash)
            self.assertEqual(receipt["evaluated_checkpoint"], gate["evaluated_checkpoint"])

    def test_single_file_gate_edit_cannot_promote_blocked_model(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            checkpoint_dir = root / "runs" / "r" / "checkpoints"
            checkpoint_dir.mkdir(parents=True)
            config, _ = self.cli.load_config(CONFIG_PATH)
            context = SimpleNamespace(
                run_id="run-v1",
                checkpoint_dir=checkpoint_dir,
                layout=SimpleNamespace(root=root),
                config=config,
            )
            self.cli._write_gate(
                context,
                binding=FakeBinding(),
                gate_status="blocked",
                adapter_hash="a" * 64,
                scorer_checkpoint_hash="e" * 64,
                evaluated_checkpoint="scorer-step-00000001",
                reasons=["adapter_ce_improvement_below_threshold"],
                verification_status="unverified",
            )
            gate_path = checkpoint_dir / "gate.json"
            tampered = json.loads(gate_path.read_text(encoding="utf-8"))
            tampered.update(
                {
                    "gate_status": "passed",
                    "verification_status": "verified",
                    "output_type": "model_output",
                    "reasons": [],
                    "metrics": {
                        "adapter_ce_improvement": 1.0,
                        "validation_rank_ic": 1.0,
                        "zero_shot_rank_ic": 0.0,
                        "head_only_rank_ic": 0.0,
                        "positive_quarter_fraction": 1.0,
                        "bootstrap_ci95_lower": 1.0,
                        "base_after_cost_return": 1.0,
                        "stress_after_cost_return": 1.0,
                    },
                    "forward_observation": {
                        "observation_days": 60,
                        "minimum_days": 60,
                        "recommended_days": 120,
                        "minimum_met": True,
                    },
                }
            )
            gate_path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaisesRegex(self.cli.CliBlocked, "release receipt"):
                self.cli._validate_gate(context, FakeBinding())

    def test_old_passed_gate_cannot_roll_back_newer_active_blocked_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            checkpoint_dir = root / "runs" / "r" / "checkpoints"
            checkpoint_dir.mkdir(parents=True)
            config, _ = self.cli.load_config(CONFIG_PATH)
            context = SimpleNamespace(
                run_id="run-v1",
                checkpoint_dir=checkpoint_dir,
                layout=SimpleNamespace(root=root),
                config=config,
            )
            self.cli._write_gate(
                context,
                binding=FakeBinding(),
                gate_status="passed",
                adapter_hash="a" * 64,
                scorer_checkpoint_hash="e" * 64,
                evaluated_checkpoint="scorer-step-00000001",
                reasons=[],
                verification_status="verified",
            )
            gate_path = checkpoint_dir / "gate.json"
            old_passed = gate_path.read_bytes()
            self.cli._write_gate(
                context,
                binding=FakeBinding(),
                gate_status="blocked",
                adapter_hash="a" * 64,
                scorer_checkpoint_hash="e" * 64,
                evaluated_checkpoint="scorer-step-00000001",
                reasons=["revoked"],
                verification_status="unverified",
            )
            gate_path.write_bytes(old_passed)
            with self.assertRaisesRegex(self.cli.CliBlocked, "active gate lineage"):
                self.cli._validate_gate(context, FakeBinding())

    def test_passed_gate_requires_live_bound_forward_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            checkpoint_dir = root / "runs" / "r" / "checkpoints"
            registry = root / "registry"
            checkpoint_dir.mkdir(parents=True)
            registry.mkdir()
            config, _ = self.cli.load_config(CONFIG_PATH)
            context = SimpleNamespace(
                run_id="run-v1",
                checkpoint_dir=checkpoint_dir,
                layout=SimpleNamespace(root=root, registry=registry),
                config=config,
            )
            metrics = {
                "adapter_ce_improvement": 0.02,
                "validation_rank_ic": 0.08,
                "zero_shot_rank_ic": 0.01,
                "head_only_rank_ic": 0.02,
                "positive_quarter_fraction": 1.0,
                "bootstrap_ci95_lower": 0.01,
                "base_after_cost_return": 0.01,
                "stress_after_cost_return": 0.001,
            }
            self.cli._write_gate(
                context,
                binding=FakeBinding(),
                gate_status="passed",
                adapter_hash="a" * 64,
                scorer_checkpoint_hash="e" * 64,
                evaluated_checkpoint="scorer-step-00000001",
                reasons=[],
                verification_status="verified",
                forward_observation={
                    "observation_days": 60,
                    "minimum_days": 60,
                    "recommended_days": 120,
                    "minimum_met": True,
                    "batch_commitments": [{"date": "2026-08-03"}],
                    "registry_root_sha256": "f" * 64,
                },
                metrics=metrics,
            )
            with mock.patch.object(
                self.cli,
                "_load_data_status",
                return_value={"status": "production_ready"},
            ):
                with self.assertRaisesRegex(
                    self.cli.CliBlocked, "删除、重排或改写"
                ):
                    self.cli._validate_gate(context, FakeBinding())

    def test_evaluate_never_promotes_local_provisional_even_with_good_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            checkpoint_dir = root / "runs" / "r" / "checkpoints"
            metrics_dir = root / "runs" / "r" / "metrics"
            predictions_dir = root / "runs" / "r" / "predictions"
            for path in (checkpoint_dir, metrics_dir, predictions_dir):
                path.mkdir(parents=True)
            evaluation_input = predictions_dir / "fixture.csv"
            pd.DataFrame({"fixture": [1]}).to_csv(evaluation_input, index=False)
            config, _ = self.cli.load_config(CONFIG_PATH)
            context = SimpleNamespace(
                run_id="run-v1",
                checkpoint_dir=checkpoint_dir,
                metrics_dir=metrics_dir,
                predictions_dir=predictions_dir,
                layout=SimpleNamespace(root=root, registry=root / "registry"),
                config=config,
            )

            class FakeStore:
                def __init__(self, *_args, **_kwargs):
                    pass

                def inspect(self, _reference):
                    return {
                        "stage": "scorer",
                        "checkpoint_name": "scorer-step-00000001",
                        "created_at_ns": 1,
                        "step": 1,
                        "is_best": True,
                        "files": {"state.pt": {"sha256": "e" * 64}},
                    }

                def recover(self):
                    return {"valid": ["scorer-step-00000001"]}

            perfect = {
                "adapter_ce_improvement": 0.02,
                "validation_rank_ic": 0.08,
                "zero_shot_rank_ic": 0.01,
                "head_only_rank_ic": 0.02,
                "positive_quarter_fraction": 1.0,
                "bootstrap_ci95_lower": 0.01,
                "base_after_cost_return": 0.01,
                "stress_after_cost_return": 0.001,
            }
            import kronos_a_share_training

            with (
                mock.patch.object(self.cli, "build_context", return_value=context),
                mock.patch.object(self.cli, "_binding", return_value=FakeBinding()),
                mock.patch.object(
                    self.cli,
                    "_scorer_checkpoint_hashes",
                    return_value=("adapter-step-00000001", "a" * 64, "e" * 64),
                ),
                mock.patch.object(
                    self.cli,
                    "_load_data_status",
                    return_value={"status": "local_provisional"},
                ),
                mock.patch.object(
                    self.cli,
                    "_controlled_evaluation_frame",
                    return_value=pd.DataFrame({"fixture": [1]}),
                ),
                mock.patch.object(
                    self.cli,
                    "_recompute_scorer_predictions",
                    return_value=pd.DataFrame({"fixture": [1]}),
                ),
                mock.patch.object(self.cli, "_evaluation_metrics", return_value=perfect),
                mock.patch.object(
                    kronos_a_share_training, "CheckpointStore", FakeStore
                ),
            ):
                result = self.cli.command_evaluate(
                    SimpleNamespace(
                        config=CONFIG_PATH,
                        checkpoint="best",
                        split="validation",
                        input=evaluation_input,
                    )
                )
            self.assertEqual(result["gate"]["gate_status"], "blocked")
            self.assertEqual(result["gate"]["verification_status"], "unverified")
            self.assertEqual(result["output_type"], "N/A")
            self.assertTrue(
                any(
                    reason.startswith("formal_validation_rejects_noncanonical_input:")
                    for reason in result["gate"]["reasons"]
                )
            )

    def test_last_value_is_an_explicit_zero_information_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            metrics_dir = root / "metrics"
            metrics_dir.mkdir()
            config, _ = self.cli.load_config(CONFIG_PATH)
            adapter_reference = "adapter-step-00000001"
            adapter_hash = "a" * 64
            (metrics_dir / "adapter_summary.json").write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "binding": self.cli._gate_binding(FakeBinding()),
                        "checkpoint_name": adapter_reference,
                        "adapter_hash": adapter_hash,
                        "adapter_ce_improvement": 0.02,
                        "peak_gpu_memory_bytes": 1,
                        "gpu_memory_limit_bytes": 2,
                    }
                ),
                encoding="utf-8",
            )
            rows = []
            for date in ("2023-01-31", "2023-02-28"):
                for position in range(3):
                    row = {
                        "trade_date": date,
                        "raw_score": float(position),
                        "label_excess_10d": float(position),
                        "entry_price_raw": 10.0,
                        "exit_price_raw": 10.1,
                    }
                    for column in self.cli.BASELINE_SCORE_COLUMNS:
                        row[column] = (
                            0.0
                            if column == "last_value_score"
                            else float(position)
                        )
                    rows.append(row)
            context = SimpleNamespace(config=config, metrics_dir=metrics_dir)
            with (
                mock.patch.object(self.cli, "_binding", return_value=FakeBinding()),
                mock.patch.object(
                    self.cli,
                    "monthly_block_bootstrap_difference",
                    return_value={"ci95_lower": 0.01},
                ),
                mock.patch.object(
                    self.cli,
                    "top_quantile_return_after_cost",
                    return_value={"mean_return_after_cost": 0.01},
                ),
                mock.patch.object(
                    self.cli,
                    "_adapter_checkpoint_release_metrics",
                    return_value={"adapter_ce_improvement": 0.02},
                ),
            ):
                metrics = self.cli._evaluation_metrics(
                    context,
                    pd.DataFrame(rows),
                    expected_adapter_reference=adapter_reference,
                    expected_adapter_hash=adapter_hash,
                )
            self.assertEqual(metrics["baseline_rank_ic"]["last_value_score"], 0.0)

    def test_evaluate_builds_missing_companion_and_blocks_until_forward_minimum(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            checkpoint_dir = root / "runs" / "r" / "checkpoints"
            metrics_dir = root / "runs" / "r" / "metrics"
            predictions_dir = root / "runs" / "r" / "predictions"
            registry_dir = root / "registry"
            for path in (checkpoint_dir, metrics_dir, predictions_dir, registry_dir):
                path.mkdir(parents=True)
            config, _ = self.cli.load_config(CONFIG_PATH)
            context = SimpleNamespace(
                run_id="run-v1",
                checkpoint_dir=checkpoint_dir,
                metrics_dir=metrics_dir,
                predictions_dir=predictions_dir,
                layout=SimpleNamespace(root=root, registry=registry_dir),
                config=config,
            )

            class FakeStore:
                def __init__(self, *_args, **_kwargs):
                    pass

                def inspect(self, _reference):
                    return {
                        "stage": "scorer",
                        "checkpoint_name": "scorer-step-00000001",
                        "created_at_ns": 1,
                        "step": 1,
                        "is_best": True,
                        "files": {"state.pt": {"sha256": "e" * 64}},
                    }

                def recover(self):
                    return {"valid": ["scorer-step-00000001"]}

            perfect = {
                "adapter_ce_improvement": 0.02,
                "validation_rank_ic": 0.08,
                "zero_shot_rank_ic": 0.01,
                "head_only_rank_ic": 0.02,
                "positive_quarter_fraction": 1.0,
                "bootstrap_ci95_lower": 0.01,
                "base_after_cost_return": 0.01,
                "stress_after_cost_return": 0.001,
            }
            companion = predictions_dir / "validation_baselines.csv"

            def build_companion(*_args, **_kwargs):
                companion.write_text("sample_id\n0\n", encoding="utf-8")
                return companion

            import kronos_a_share_training

            forward = {
                "observation_days": 0,
                "matured_observation_days": 0,
                "pending_observation_days": 0,
                "minimum_days": 60,
                "recommended_days": 120,
                "minimum_met": False,
                "recommended_met": False,
                "batch_commitments": [],
                "registry_root_sha256": "0" * 64,
            }
            with (
                mock.patch.object(self.cli, "build_context", return_value=context),
                mock.patch.object(self.cli, "_binding", return_value=FakeBinding()),
                mock.patch.object(
                    self.cli,
                    "_scorer_checkpoint_hashes",
                    return_value=("adapter-step-00000001", "a" * 64, "e" * 64),
                ),
                mock.patch.object(
                    self.cli,
                    "_load_data_status",
                    return_value={"status": "production_ready"},
                ),
                mock.patch.object(
                    self.cli,
                    "_ensure_evaluation_companion",
                    side_effect=build_companion,
                ) as ensure_companion,
                mock.patch.object(
                    self.cli,
                    "_controlled_evaluation_frame",
                    return_value=pd.DataFrame({"fixture": [1]}),
                ),
                mock.patch.object(
                    self.cli,
                    "_recompute_scorer_predictions",
                    return_value=pd.DataFrame({"fixture": [1]}),
                ),
                mock.patch.object(
                    self.cli, "_assert_rebuilt_companion_matches"
                ),
                mock.patch.object(
                    self.cli,
                    "_live_adapter_checkpoint_release_metrics",
                    return_value={
                        "adapter_ce_improvement": 0.02,
                        "declaration_matches_live": True,
                    },
                ),
                mock.patch.object(self.cli, "_evaluation_metrics", return_value=perfect),
                mock.patch.object(
                    self.cli, "inspect_forward_registry", return_value=forward
                ),
                mock.patch.object(
                    kronos_a_share_training, "CheckpointStore", FakeStore
                ),
            ):
                result = self.cli.command_evaluate(
                    SimpleNamespace(
                        config=CONFIG_PATH,
                        checkpoint="best",
                        split="validation",
                        input=None,
                        device="cpu",
                        chunk_size=16,
                    )
                )
            self.assertEqual(ensure_companion.call_count, 2)
            self.assertTrue(
                ensure_companion.call_args_list[1].kwargs["force_recompute_baselines"]
            )
            self.assertEqual(result["gate"]["gate_status"], "blocked")
            self.assertTrue(result["gate"]["research_scoring_allowed"])
            self.assertIn(
                "forward_observation_days=0<60", result["gate"]["reasons"]
            )
            self.assertEqual(result["output_type"], "N/A")
            with mock.patch.object(
                self.cli,
                "_load_data_status",
                return_value={"status": "production_ready"},
            ):
                validated = self.cli._validate_gate(context, FakeBinding())
            self.assertTrue(validated["research_scoring_allowed"])

    def test_nonvalidation_splits_never_write_or_change_gate(self) -> None:
        import kronos_a_share_training

        for split in ("development_test", "locked_retrospective"):
            with self.subTest(split=split), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                checkpoint_dir = root / "runs" / "r" / "checkpoints"
                metrics_dir = root / "runs" / "r" / "metrics"
                predictions_dir = root / "runs" / "r" / "predictions"
                registry_dir = root / "registry"
                for path in (checkpoint_dir, metrics_dir, predictions_dir, registry_dir):
                    path.mkdir(parents=True)
                gate_path = checkpoint_dir / "gate.json"
                head_path = checkpoint_dir / "gate-head.json"
                gate_path.write_bytes(b"gate-sentinel")
                head_path.write_bytes(b"head-sentinel")
                evaluation_input = predictions_dir / f"{split}_baselines.csv"
                evaluation_input.write_text("sample_id\n0\n", encoding="utf-8")
                config, _ = self.cli.load_config(CONFIG_PATH)
                context = SimpleNamespace(
                    run_id="run-v1",
                    dataset_id="dataset-v1",
                    checkpoint_dir=checkpoint_dir,
                    metrics_dir=metrics_dir,
                    predictions_dir=predictions_dir,
                    layout=SimpleNamespace(root=root, registry=registry_dir),
                    config=config,
                )

                class FakeStore:
                    def __init__(self, *_args, **_kwargs):
                        pass

                    def inspect(self, _reference):
                        return {
                            "stage": "scorer",
                            "checkpoint_name": "scorer-step-00000001",
                            "created_at_ns": 1,
                            "step": 1,
                            "is_best": True,
                            "files": {"state.pt": {"sha256": "e" * 64}},
                        }

                    def recover(self):
                        return {"valid": ["scorer-step-00000001"]}

                with (
                    mock.patch.object(self.cli, "build_context", return_value=context),
                    mock.patch.object(self.cli, "_binding", return_value=FakeBinding()),
                    mock.patch.object(
                        self.cli,
                        "_scorer_checkpoint_hashes",
                        return_value=("adapter-step-00000001", "a" * 64, "e" * 64),
                    ),
                    mock.patch.object(
                        self.cli,
                        "_load_data_status",
                        return_value={"status": "production_ready"},
                    ),
                    mock.patch.object(
                        self.cli,
                        "_recompute_scorer_predictions",
                        return_value=pd.DataFrame({"fixture": [1]}),
                    ),
                    mock.patch.object(self.cli, "_materialize_non_gate_predictions"),
                    mock.patch.object(
                        self.cli,
                        "_controlled_evaluation_frame",
                        return_value=pd.DataFrame({"fixture": [1]}),
                    ) as controlled,
                    mock.patch.object(
                        self.cli,
                        "_evaluation_metrics",
                        return_value={"adapter_ce_improvement": 0.02},
                    ),
                    mock.patch.object(self.cli, "_write_gate") as write_gate,
                    mock.patch.object(
                        kronos_a_share_training, "CheckpointStore", FakeStore
                    ),
                ):
                    result = self.cli.command_evaluate(
                        SimpleNamespace(
                            config=CONFIG_PATH,
                            checkpoint="best",
                            split=split,
                            input=evaluation_input,
                            device="cpu",
                            chunk_size=2,
                        )
                    )
                write_gate.assert_not_called()
                self.assertEqual(gate_path.read_bytes(), b"gate-sentinel")
                self.assertEqual(head_path.read_bytes(), b"head-sentinel")
                self.assertEqual(result["report"]["split"], split)
                self.assertFalse(result["report"]["formal_gate_eligible"])
                self.assertEqual(controlled.call_args.kwargs["evaluate_split"], split)

    def test_nonvalidation_prediction_metadata_binds_split(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            predictions = root / "predictions"
            predictions.mkdir()
            context = SimpleNamespace(
                predictions_dir=predictions,
                run_id="run-v1",
                dataset_id="dataset-v1",
                layout=SimpleNamespace(root=root),
            )
            frame = pd.DataFrame(
                {
                    "sample_id": [7],
                    "trade_date": ["2024-07-01"],
                    "instrument_id": [1],
                    "raw_score": [0.2],
                    "label_excess_10d": [0.1],
                }
            )
            for split in ("development_test", "locked_retrospective"):
                path = self.cli._materialize_non_gate_predictions(
                    context,
                    binding=FakeBinding(),
                    checkpoint={"checkpoint_name": "scorer-step-00000001"},
                    adapter_hash="a" * 64,
                    scorer_checkpoint_hash="e" * 64,
                    split=split,
                    frame=frame,
                )
                metadata = json.loads(
                    path.with_suffix(path.suffix + ".metadata.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(metadata["evaluate_split"], split)

    def test_score_as_of_returns_stable_na_contract_when_gate_is_missing(self) -> None:
        context = SimpleNamespace(dataset_id="dataset-v1", run_id="run-v1")
        with (
            mock.patch.object(self.cli, "build_context", return_value=context),
            mock.patch.object(self.cli, "_binding", return_value=FakeBinding()),
            mock.patch.object(
                self.cli,
                "_validate_gate",
                side_effect=self.cli.CliBlocked("missing gate"),
            ),
        ):
            result = self.cli.command_score_as_of(
                SimpleNamespace(
                    config=CONFIG_PATH,
                    as_of="2026-07-31",
                    symbols=["300620.SZ", "600330.SH"],
                    future_timestamps=None,
                    device="cpu",
                    chunk_size=2,
                    temperature=1.0,
                    top_k=0,
                    top_p=0.9,
                    sample_count=1,
                )
            )
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(result["output_type"], "N/A")
        self.assertEqual(len(result["records"]), 2)
        required = {
            "as_of",
            "ticker",
            "horizon",
            "raw_score",
            "percentile",
            "forecast_path",
            "path_dispersion",
            "dataset_id",
            "run_id",
            "adapter_hash",
            "gate_status",
            "constraint_flags",
            "output_type",
        }
        for record in result["records"]:
            self.assertTrue(required.issubset(record))
            self.assertEqual(record["gate_status"], "blocked")
            self.assertEqual(record["output_type"], "N/A")
            self.assertIsNone(record["raw_score"])

    def test_score_as_of_fails_closed_without_daily_inference_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            checkpoint_dir = root / "checkpoints"
            checkpoint_dir.mkdir()
            context = SimpleNamespace(
                dataset_id="dataset-v1",
                run_id="run-v1",
                checkpoint_dir=checkpoint_dir,
                layout=SimpleNamespace(root=root),
            )
            gate = {
                "gate_sequence": 1,
                "gate_status": "passed",
                "adapter_hash": "a" * 64,
                "scorer_checkpoint_hash": "c" * 64,
                "evaluated_checkpoint": "scorer-step-1",
                "binding": {"data_sha256": "b" * 64},
            }
            with (
                mock.patch.object(self.cli, "build_context", return_value=context),
                mock.patch.object(self.cli, "_binding", return_value=FakeBinding()),
                mock.patch.object(self.cli, "_validate_gate", return_value=gate),
                mock.patch.object(
                    self.cli,
                    "_verify_gate_receipt",
                    return_value={"schema_version": "kronos-a-share-gate-receipt-v2"},
                ),
                mock.patch.object(self.cli, "sha256_file", return_value="d" * 64),
                mock.patch.object(self.cli, "verify_immutable_snapshot"),
                mock.patch.object(
                    self.cli,
                    "_snapshot_manifest_path",
                    return_value=root / "training-snapshot.json",
                ),
            ):
                result = self.cli.command_score_as_of(
                    SimpleNamespace(
                        config=CONFIG_PATH,
                        as_of="2026-08-03T00:00:00+08:00",
                        symbols=["300620.SZ"],
                        future_timestamps=None,
                        inference_snapshot=None,
                        device="cpu",
                        chunk_size=2,
                        temperature=1.0,
                        top_k=0,
                        top_p=0.9,
                        sample_count=1,
                    )
                )
            self.assertEqual(result["status"], "unverified")
            self.assertEqual(result["output_type"], "N/A")
            self.assertIn(
                "缺少 --inference-snapshot",
                result["records"][0]["constraint_flags"][0],
            )

    def test_score_as_of_operational_error_preserves_per_ticker_na_contract(self) -> None:
        context = SimpleNamespace(dataset_id="dataset-v1", run_id="run-v1")
        args = SimpleNamespace(
            config=CONFIG_PATH,
            as_of="2026-08-03T00:00:00+08:00",
            symbols=["300620.SZ", "603259.SH"],
        )
        with (
            mock.patch.object(
                self.cli,
                "_command_score_as_of_impl",
                side_effect=OverflowError("invalid forward counter"),
            ),
            mock.patch.object(self.cli, "build_context", return_value=context),
        ):
            result = self.cli.command_score_as_of(args)
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(result["output_type"], "N/A")
        self.assertEqual([row["ticker"] for row in result["records"]], [
            "300620.SZ",
            "603259.SH",
        ])
        self.assertTrue(
            all(row["output_type"] == "N/A" for row in result["records"])
        )


if __name__ == "__main__":
    unittest.main()
