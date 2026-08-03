from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

import pandas as pd
import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    ROOT
    / ".agents"
    / "skills"
    / "kronos-market-forecasting"
    / "scripts"
)
RUNNER_PATH = SCRIPTS / "run_kronos_forecast.py"
sys.path.insert(0, str(SCRIPTS))

from kronos_a_share_model import KronosScoringHead, inject_kronos_lora  # noqa: E402
from kronos_a_share_training import (  # noqa: E402
    CheckpointBinding,
    CheckpointStore,
    prepare_scorer_stage,
)


def load_runner_module():
    spec = importlib.util.spec_from_file_location(
        "kronos_forecast_adapter_runner", RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ToyAttention(nn.Module):
    def __init__(self, width: int) -> None:
        super().__init__()
        self.q_proj = nn.Linear(width, width)
        self.k_proj = nn.Linear(width, width)
        self.v_proj = nn.Linear(width, width)


class ToyBlock(nn.Module):
    def __init__(self, width: int) -> None:
        super().__init__()
        self.self_attn = ToyAttention(width)


class ToyDependencyLayer(nn.Module):
    def __init__(self, width: int) -> None:
        super().__init__()
        self.cross_attn = ToyAttention(width)


class ToyKronos(nn.Module):
    def __init__(self, width: int = 4) -> None:
        super().__init__()
        self.transformer = nn.ModuleList([ToyBlock(width) for _ in range(12)])
        self.dep_layer = ToyDependencyLayer(width)


class KronosForecastAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner_module()

    def setUp(self) -> None:
        self.forward_commitments = [{"fixture": "bound-forward-registry"}]
        self.forward_root = "9" * 64
        self.forward_inspector = mock.patch(
            "kronos_a_share_forward.inspect_forward_registry",
            return_value={
                "observation_days": 60,
                "minimum_days": 60,
                "recommended_days": 120,
                "minimum_met": True,
                "batch_commitments": self.forward_commitments,
                "registry_root_sha256": self.forward_root,
            },
        )
        self.forward_inspector.start()

    def tearDown(self) -> None:
        self.forward_inspector.stop()

    def _create_checkpoint(
        self,
        root: Path,
        *,
        base_hash: str | None = None,
        with_gate: bool = True,
    ) -> Path:
        binding = CheckpointBinding(
            base_hash or self.runner.MODEL_SHA256,
            self.runner.TOKENIZER_SHA256,
            "c" * 64,
            "d" * 64,
        )
        model = ToyKronos()
        inject_kronos_lora(model, rank=2, alpha=4, dropout=0)
        store = CheckpointStore(root, binding)
        adapter_checkpoint = store.save(
            stage="adapter",
            step=100,
            model=model,
            is_best=True,
            extra_state={"run_id": "run-test"},
        )
        if not with_gate:
            return adapter_checkpoint
        adapter_manifest = json.loads(
            (adapter_checkpoint / "manifest.json").read_text(encoding="utf-8")
        )
        head = KronosScoringHead()
        prepare_scorer_stage(model, head)
        checkpoint = store.save(
            stage="scorer",
            step=1,
            model=model,
            scoring_head=head,
            is_best=True,
            extra_state={
                "run_id": "run-test",
                "adapter_checkpoint": adapter_checkpoint.name,
                "adapter_hash": adapter_manifest["files"]["state.pt"]["sha256"],
            },
        )
        manifest = json.loads(
            (checkpoint / "manifest.json").read_text(encoding="utf-8")
        )
        gate = self._passed_gate(
            binding=binding,
            adapter_hash=adapter_manifest["files"]["state.pt"]["sha256"],
            scorer_hash=manifest["files"]["state.pt"]["sha256"],
            checkpoint_name=checkpoint.name,
        )
        self._write_gate_with_receipt(root, gate)
        return checkpoint

    def _passed_gate(
        self,
        *,
        binding: CheckpointBinding,
        adapter_hash: str,
        scorer_hash: str,
        checkpoint_name: str,
    ) -> dict[str, object]:
        return {
            "schema_version": "kronos-a-share-gate-v2",
            "gate_sequence": 1,
            "gate_status": "passed",
            "run_id": "run-test",
            "binding": {
                "base_model_sha256": binding.base_model_sha256,
                "tokenizer_sha256": binding.tokenizer_sha256,
                "data_sha256": binding.dataset_sha256,
                "config_sha256": binding.config_sha256,
            },
            "adapter_hash": adapter_hash,
            "scorer_checkpoint_hash": scorer_hash,
            "evaluated_checkpoint": checkpoint_name,
            "generated_at": "2026-08-03T00:00:00+00:00",
            "verification_status": "verified",
            "output_type": "model_output",
            "research_scoring_allowed": False,
            "reasons": [],
            "forward_observation": {
                "observation_days": 60,
                "minimum_days": 60,
                "recommended_days": 120,
                "minimum_met": True,
                "batch_commitments": self.forward_commitments,
                "registry_root_sha256": self.forward_root,
            },
            "metrics": {
                "adapter_ce_improvement": 0.02,
                "validation_rank_ic": 0.08,
                "zero_shot_rank_ic": 0.01,
                "head_only_rank_ic": 0.02,
                "positive_quarter_fraction": 1.0,
                "bootstrap_ci95_lower": 0.01,
                "base_after_cost_return": 0.01,
                "stress_after_cost_return": 0.001,
            },
        }

    def _write_gate_with_receipt(
        self, root: Path, gate: dict[str, object]
    ) -> None:
        gate_path = root / "gate.json"
        gate_path.write_text(json.dumps(gate, ensure_ascii=False), encoding="utf-8")
        gate_hash = self.runner.sha256_file(gate_path)
        receipt = {
            "schema_version": "kronos-a-share-gate-receipt-v2",
            "gate_sha256": gate_hash,
            "gate_bytes": gate_path.stat().st_size,
            "gate_schema_version": gate["schema_version"],
            "gate_status": gate["gate_status"],
            "run_id": gate["run_id"],
            "binding": gate["binding"],
            "adapter_hash": gate["adapter_hash"],
            "scorer_checkpoint_hash": gate["scorer_checkpoint_hash"],
            "evaluated_checkpoint": gate["evaluated_checkpoint"],
            "gate_generated_at": gate["generated_at"],
            "gate_sequence": gate["gate_sequence"],
        }
        receipt_path = root / "gate-receipts" / f"{gate_hash}.json"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False), encoding="utf-8"
        )
        event = {
            "schema_version": "kronos-a-share-gate-head-v1",
            "sequence": gate["gate_sequence"],
            "gate_sha256": gate_hash,
            "gate_receipt_sha256": self.runner.sha256_file(receipt_path),
            "previous_event_sha256": None,
            "created_at": "2026-08-03T00:00:01+00:00",
        }
        event["event_sha256"] = self.runner.canonical_json_sha256(event)
        lineage = root / "gate-lineage"
        lineage.mkdir(parents=True, exist_ok=True)
        (lineage / f"00000001-{event['event_sha256']}.json").write_text(
            json.dumps(event, ensure_ascii=False), encoding="utf-8"
        )
        (root / "gate-head.json").write_text(
            json.dumps(event, ensure_ascii=False), encoding="utf-8"
        )

    def test_base_parser_and_check_branch_remain_adapter_free(self) -> None:
        args = self.runner.build_parser().parse_args(["--check", "--load-model"])
        self.assertIsNone(args.adapter_dir)
        runtime_report = {
            "runtime_root": "runtime",
            "source_revision": "source",
            "model_revision": "model",
            "tokenizer_revision": "tokenizer",
        }
        with (
            mock.patch.object(self.runner, "validate_runtime", return_value=runtime_report),
            mock.patch.object(
                self.runner,
                "resolve_device",
                return_value=("cpu", [], {"cuda_available": False}),
            ),
            mock.patch.object(self.runner, "load_predictor") as base_loader,
            mock.patch.object(self.runner, "load_predictor_with_adapter") as adapter_loader,
            redirect_stdout(StringIO()) as output,
        ):
            self.assertEqual(self.runner.run_check(args), 0)

        base_loader.assert_called_once()
        adapter_loader.assert_not_called()
        self.assertNotIn('"adapter"', output.getvalue())

    def test_valid_gate_is_bound_to_exact_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training" / "runs" / "run-test" / "checkpoints"
            checkpoint = self._create_checkpoint(root)
            report = self.runner.load_adapter_into_model(ToyKronos(), root)

        self.assertEqual(report["checkpoint_name"], checkpoint.name)
        self.assertEqual(report["gate_status"], "passed")
        self.assertEqual(report["release_output_type"], "model_output")
        self.assertEqual(report["adapter_hash"], report["adapter_hash"].lower())

    def test_scorer_gate_keeps_adapter_and_scorer_hashes_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training" / "runs" / "run-test" / "checkpoints"
            binding = CheckpointBinding(
                self.runner.MODEL_SHA256,
                self.runner.TOKENIZER_SHA256,
                "c" * 64,
                "d" * 64,
            )
            model = ToyKronos()
            inject_kronos_lora(model, rank=2, alpha=4, dropout=0)
            store = CheckpointStore(root, binding)
            adapter_path = store.save(
                stage="adapter",
                step=100,
                model=model,
                is_best=True,
                extra_state={"run_id": "run-test"},
            )
            adapter_manifest = json.loads(
                (adapter_path / "manifest.json").read_text(encoding="utf-8")
            )
            head = KronosScoringHead()
            prepare_scorer_stage(model, head)
            scorer_path = store.save(
                stage="scorer",
                step=1,
                model=model,
                scoring_head=head,
                is_best=True,
                extra_state={
                    "run_id": "run-test",
                    "adapter_checkpoint": adapter_path.name,
                    "adapter_hash": adapter_manifest["files"]["state.pt"]["sha256"],
                },
            )
            scorer_manifest = json.loads(
                (scorer_path / "manifest.json").read_text(encoding="utf-8")
            )
            gate = self._passed_gate(
                binding=binding,
                adapter_hash=adapter_manifest["files"]["state.pt"]["sha256"],
                scorer_hash=scorer_manifest["files"]["state.pt"]["sha256"],
                checkpoint_name=scorer_path.name,
            )
            self._write_gate_with_receipt(root, gate)
            report = self.runner.load_adapter_into_model(ToyKronos(), root)

        self.assertEqual(report["gate_status"], "passed")
        self.assertEqual(report["adapter_hash"], gate["adapter_hash"])
        self.assertEqual(report["checkpoint_hash"], gate["scorer_checkpoint_hash"])
        self.assertNotEqual(report["adapter_hash"], report["checkpoint_hash"])

    def test_specific_checkpoint_is_supported_but_gate_mismatch_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training" / "runs" / "run-test" / "checkpoints"
            checkpoint = self._create_checkpoint(root)
            gate_path = root / "gate.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["adapter_hash"] = "f" * 64
            gate_path.write_text(json.dumps(gate), encoding="utf-8")

            report = self.runner.load_adapter_into_model(ToyKronos(), checkpoint)

        self.assertEqual(report["gate_status"], "blocked")
        self.assertEqual(report["release_output_type"], "N/A")
        self.assertTrue(any("adapter_hash" in reason for reason in report["gate_reasons"]))

    def test_passed_gate_without_release_receipt_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training" / "runs" / "run-test" / "checkpoints"
            self._create_checkpoint(root)
            for receipt in (root / "gate-receipts").glob("*.json"):
                receipt.unlink()
            report = self.runner.load_adapter_into_model(ToyKronos(), root)

        self.assertEqual(report["gate_status"], "blocked")
        self.assertEqual(report["release_output_type"], "N/A")
        self.assertTrue(
            any("release receipt" in reason for reason in report["gate_reasons"])
        )

    def test_missing_gate_is_unverified_research_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training" / "runs" / "run-test" / "checkpoints"
            self._create_checkpoint(root, with_gate=False)
            report = self.runner.load_adapter_into_model(ToyKronos(), root)

        self.assertEqual(report["gate_status"], "unverified")
        self.assertEqual(report["release_output_type"], "N/A")

    def test_checkpoint_bound_to_other_base_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training" / "runs" / "run-test" / "checkpoints"
            self._create_checkpoint(root, base_hash="a" * 64, with_gate=False)
            with self.assertRaisesRegex(
                self.runner.KronosRuntimeError, "Kronos-base"
            ):
                self.runner.load_adapter_into_model(ToyKronos(), root)

    def test_tampered_state_is_rejected_before_adapter_use(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training" / "runs" / "run-test" / "checkpoints"
            checkpoint = self._create_checkpoint(root)
            with (checkpoint / "state.pt").open("ab") as handle:
                handle.write(b"tamper")

            with self.assertRaisesRegex(
                self.runner.KronosRuntimeError, "state.pt"
            ):
                self.runner.load_adapter_into_model(ToyKronos(), root)

    def test_adapter_check_requires_full_model_load(self) -> None:
        args = self.runner.build_parser().parse_args(
            ["--check", "--adapter-dir", "checkpoint"]
        )
        with self.assertRaisesRegex(self.runner.KronosRuntimeError, "--load-model"):
            self.runner.validate_arguments(args)

    def test_blocked_adapter_forecast_is_fail_closed_before_prediction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_path = root / "forecast.csv"
            args = self.runner.build_parser().parse_args(
                [
                    "--input",
                    str(root / "history.csv"),
                    "--freq",
                    "B",
                    "--pred-len",
                    "2",
                    "--output",
                    str(output_path),
                    "--adapter-dir",
                    str(root / "checkpoints"),
                    "--device",
                    "cpu",
                ]
            )
            predictor = mock.Mock()
            adapter_report = {
                "gate_status": "blocked",
                "release_output_type": "N/A",
                "gate_reasons": ["forward_observation_days=0<60"],
            }
            history = pd.DataFrame(
                {
                    "open": [1.0, 1.1],
                    "high": [1.1, 1.2],
                    "low": [0.9, 1.0],
                    "close": [1.0, 1.1],
                    "volume": [100.0, 110.0],
                    "amount": [100.0, 121.0],
                }
            )
            timestamps = pd.Series(pd.to_datetime(["2026-07-30", "2026-07-31"]))
            future = pd.Series(pd.to_datetime(["2026-08-03", "2026-08-04"]))
            with (
                mock.patch.object(
                    self.runner,
                    "validate_runtime",
                    return_value={"runtime_root": "runtime"},
                ),
                mock.patch.object(
                    self.runner,
                    "load_history",
                    return_value=(history, timestamps, [], {"data_cutoff": "2026-07-31"}),
                ),
                mock.patch.object(
                    self.runner,
                    "load_future_timestamps",
                    return_value=(future, "freq:B", None, []),
                ),
                mock.patch.object(
                    self.runner,
                    "resolve_device",
                    return_value=("cpu", [], {"cuda_available": False}),
                ),
                mock.patch.object(
                    self.runner,
                    "load_predictor_with_adapter",
                    return_value=(None, adapter_report),
                ) as adapter_loader,
                mock.patch.object(self.runner, "prepare_output_pair") as prepare_output,
                redirect_stdout(StringIO()) as stdout,
            ):
                result = self.runner.run_forecast(args)

            self.assertEqual(result, 2)
            adapter_loader.assert_called_once_with(
                args.runtime_root,
                "cpu",
                args.adapter_dir,
                allow_unreleased=False,
            )
            predictor.predict.assert_not_called()
            prepare_output.assert_not_called()
            self.assertFalse(output_path.exists())
            self.assertFalse(
                output_path.with_suffix(output_path.suffix + ".metadata.json").exists()
            )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "unverified")
            self.assertEqual(payload["output_type"], "N/A")
            self.assertFalse(payload["output_written"])
            self.assertFalse(payload["research_only"])

    def test_explicit_research_output_is_named_and_remains_top_level_na(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_path = root / "forecast.research-only.csv"
            args = self.runner.build_parser().parse_args(
                [
                    "--input",
                    str(root / "history.csv"),
                    "--freq",
                    "B",
                    "--pred-len",
                    "2",
                    "--output",
                    str(output_path),
                    "--adapter-dir",
                    str(root / "checkpoints"),
                    "--allow-research-output",
                    "--device",
                    "cpu",
                ]
            )
            predicted = pd.DataFrame(
                {
                    "open": [1.1, 1.2],
                    "high": [1.2, 1.3],
                    "low": [1.0, 1.1],
                    "close": [1.15, 1.25],
                    "volume": [120.0, 130.0],
                    "amount": [138.0, 162.5],
                },
                index=pd.to_datetime(["2026-08-03", "2026-08-04"]),
            )
            predictor = mock.Mock()
            predictor.predict.return_value = predicted
            adapter_report = {
                "gate_status": "unverified",
                "release_output_type": "N/A",
                "gate_reasons": ["adapter store 缺少 gate.json"],
            }
            history = predicted.copy()
            timestamps = pd.Series(pd.to_datetime(["2026-07-30", "2026-07-31"]))
            future = pd.Series(pd.to_datetime(["2026-08-03", "2026-08-04"]))
            with (
                mock.patch.object(
                    self.runner,
                    "validate_runtime",
                    return_value={"runtime_root": "runtime"},
                ),
                mock.patch.object(
                    self.runner,
                    "load_history",
                    return_value=(history, timestamps, [], {"data_cutoff": "2026-07-31"}),
                ),
                mock.patch.object(
                    self.runner,
                    "load_future_timestamps",
                    return_value=(future, "freq:B", None, []),
                ),
                mock.patch.object(
                    self.runner,
                    "resolve_device",
                    return_value=("cpu", [], {"cuda_available": False}),
                ),
                mock.patch.object(
                    self.runner,
                    "load_predictor_with_adapter",
                    return_value=(predictor, adapter_report),
                ) as adapter_loader,
                redirect_stdout(StringIO()) as stdout,
            ):
                result = self.runner.run_forecast(args)

            self.assertEqual(result, 2)
            adapter_loader.assert_called_once_with(
                args.runtime_root,
                "cpu",
                args.adapter_dir,
                allow_unreleased=True,
            )
            predictor.predict.assert_called_once()
            self.assertTrue(output_path.is_file())
            metadata_path = output_path.with_suffix(
                output_path.suffix + ".metadata.json"
            )
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["status"], "unverified")
            self.assertEqual(metadata["output_type"], "N/A")
            self.assertEqual(metadata["release_mode"], "research-only")
            self.assertTrue(metadata["research_only"])
            self.assertFalse(metadata["publishable"])
            self.assertIn("research-only", output_path.name)
            self.assertIn("research-only", stdout.getvalue())
            self.assertIn("N/A", stdout.getvalue())

    def test_research_output_rejects_formal_looking_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self.runner.build_parser().parse_args(
                [
                    "--input",
                    str(root / "history.csv"),
                    "--freq",
                    "B",
                    "--pred-len",
                    "2",
                    "--output",
                    str(root / "forecast.csv"),
                    "--adapter-dir",
                    str(root / "checkpoints"),
                    "--allow-research-output",
                    "--device",
                    "cpu",
                ]
            )
            predictor = mock.Mock()
            adapter_report = {
                "gate_status": "blocked",
                "release_output_type": "N/A",
                "gate_reasons": ["model gate blocked"],
            }
            timestamps = pd.Series(pd.to_datetime(["2026-07-30", "2026-07-31"]))
            future = pd.Series(pd.to_datetime(["2026-08-03", "2026-08-04"]))
            with (
                mock.patch.object(self.runner, "validate_runtime", return_value={}),
                mock.patch.object(
                    self.runner,
                    "load_history",
                    return_value=(pd.DataFrame(), timestamps, [], {}),
                ),
                mock.patch.object(
                    self.runner,
                    "load_future_timestamps",
                    return_value=(future, "freq:B", None, []),
                ),
                mock.patch.object(
                    self.runner,
                    "resolve_device",
                    return_value=("cpu", [], {"cuda_available": False}),
                ),
                mock.patch.object(
                    self.runner,
                    "load_predictor_with_adapter",
                    return_value=(predictor, adapter_report),
                ),
                mock.patch.object(self.runner, "prepare_output_pair") as prepare_output,
            ):
                with self.assertRaisesRegex(
                    self.runner.KronosRuntimeError, "research-only.csv"
                ):
                    self.runner.run_forecast(args)

            predictor.predict.assert_not_called()
            prepare_output.assert_not_called()


if __name__ == "__main__":
    unittest.main()
