from __future__ import annotations

import copy
import json
import math
import random
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
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
sys.path.insert(0, str(SCRIPTS))

from kronos_a_share_model import (  # noqa: E402
    KRONOS_LORA_TARGETS,
    KronosScoringHead,
    LoRAContractError,
    build_future_mask,
    cross_sectional_scorer_loss,
    future_token_cross_entropy,
    grouped_ranknet_loss,
    inject_kronos_lora,
    load_lora_state_dict,
    lora_state_dict,
)
from kronos_a_share_training import (  # noqa: E402
    CheckpointBinding,
    CheckpointBusyError,
    CheckpointFileLock,
    CheckpointIntegrityError,
    CheckpointStore,
    ScorerBatch,
    capture_rng_state,
    prepare_scorer_stage,
    restore_rng_state,
    scorer_forward_loss,
    select_validated_adapter,
    set_deterministic_seed,
)


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
    def __init__(self, width: int = 4, vocab_s1: int = 7, vocab_s2: int = 5) -> None:
        super().__init__()
        self.width = width
        self.transformer = nn.ModuleList([ToyBlock(width) for _ in range(12)])
        self.dep_layer = ToyDependencyLayer(width)
        self.embedding_s1 = nn.Embedding(vocab_s1, width)
        self.embedding_s2 = nn.Embedding(vocab_s2, width)
        self.head_s1 = nn.Linear(width, vocab_s1)
        self.head_s2 = nn.Linear(width, vocab_s2)

    def _context(self, s1_ids: torch.Tensor, s2_ids: torch.Tensor) -> torch.Tensor:
        context = self.embedding_s1(s1_ids) + self.embedding_s2(s2_ids)
        for block in self.transformer:
            context = context + 0.01 * (
                block.self_attn.q_proj(context) + block.self_attn.v_proj(context)
            )
        context = context + 0.01 * (
            self.dep_layer.cross_attn.q_proj(context)
            + self.dep_layer.cross_attn.v_proj(context)
        )
        return context

    def forward(
        self,
        s1_ids: torch.Tensor,
        s2_ids: torch.Tensor,
        stamp: torch.Tensor | None = None,
        padding_mask: torch.Tensor | None = None,
        use_teacher_forcing: bool = False,
        s1_targets: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        context = self._context(s1_ids, s2_ids)
        return self.head_s1(context), self.head_s2(context)

    def decode_s1(
        self,
        s1_ids: torch.Tensor,
        s2_ids: torch.Tensor,
        stamp: torch.Tensor | None = None,
        padding_mask: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        context = self._context(s1_ids, s2_ids)
        return self.head_s1(context), context


def binding(character: str = "a") -> CheckpointBinding:
    values = [chr(ord(character) + offset) * 64 for offset in range(4)]
    return CheckpointBinding(*values)


class KronosLoRATests(unittest.TestCase):
    def test_strict_injection_wraps_exactly_26_targets_and_freezes_base(self) -> None:
        model = ToyKronos(width=4)
        report = inject_kronos_lora(model, rank=4, alpha=8, dropout=0)

        self.assertEqual(report.target_names, KRONOS_LORA_TARGETS)
        self.assertEqual(report.target_count, 26)
        self.assertEqual(report.trainable_parameters, 26 * (4 * 4 + 4 * 4))
        trainable = {
            name for name, parameter in model.named_parameters() if parameter.requires_grad
        }
        self.assertEqual(len(trainable), 52)
        self.assertTrue(all(name.endswith(("lora_A", "lora_B")) for name in trainable))

    def test_strict_injection_rejects_architecture_drift(self) -> None:
        missing = ToyKronos()
        missing.transformer[3].self_attn.q_proj = nn.Identity()
        with self.assertRaisesRegex(LoRAContractError, "missing"):
            inject_kronos_lora(missing)

        extra = ToyKronos()
        extra.other = ToyAttention(4)
        with self.assertRaisesRegex(LoRAContractError, "extra"):
            inject_kronos_lora(extra)

    def test_lora_state_roundtrip_preserves_outputs_without_base_weights(self) -> None:
        torch.manual_seed(7)
        source = ToyKronos()
        destination = copy.deepcopy(source)
        inject_kronos_lora(source, rank=2, alpha=4, dropout=0)
        inject_kronos_lora(destination, rank=2, alpha=4, dropout=0)
        randomized = {
            key: torch.randn_like(tensor)
            for key, tensor in lora_state_dict(source).items()
        }
        load_lora_state_dict(source, randomized)
        saved = lora_state_dict(source)
        self.assertEqual(len(saved), 52)
        self.assertFalse(any("base" in key for key in saved))
        load_lora_state_dict(destination, saved)

        s1 = torch.randint(0, 7, (2, 5))
        s2 = torch.randint(0, 5, (2, 5))
        source.eval()
        destination.eval()
        actual = source(s1, s2)
        expected = destination(s1, s2)
        torch.testing.assert_close(actual[0], expected[0])
        torch.testing.assert_close(actual[1], expected[1])


class LossAndScorerTests(unittest.TestCase):
    def test_future_ce_has_zero_gradient_on_history_positions(self) -> None:
        torch.manual_seed(1)
        s1_logits = torch.randn(2, 6, 7, requires_grad=True)
        s2_logits = torch.randn(2, 6, 5, requires_grad=True)
        s1_targets = torch.randint(0, 7, (2, 6))
        s2_targets = torch.randint(0, 5, (2, 6))
        mask = build_future_mask(6, history_length=4, future_length=2)

        loss, _, _ = future_token_cross_entropy(
            s1_logits, s2_logits, s1_targets, s2_targets, mask
        )
        loss.backward()

        self.assertEqual(int(torch.count_nonzero(s1_logits.grad[:, :4])), 0)
        self.assertEqual(int(torch.count_nonzero(s2_logits.grad[:, :4])), 0)
        self.assertGreater(int(torch.count_nonzero(s1_logits.grad[:, 4:])), 0)
        self.assertGreater(int(torch.count_nonzero(s2_logits.grad[:, 4:])), 0)

    def test_ranknet_never_builds_cross_date_pairs(self) -> None:
        scores = torch.tensor([0.0, 1.0, -100.0, -99.0], requires_grad=True)
        targets = torch.tensor([0.0, 1.0, 100.0, 101.0])
        loss, pair_count = grouped_ranknet_loss(
            scores, targets, ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02"]
        )

        self.assertEqual(pair_count, 2)
        self.assertAlmostEqual(float(loss.detach()), math.log1p(math.exp(-1)), places=6)
        combined = cross_sectional_scorer_loss(
            scores,
            targets,
            ["a", "a", "b", "b"],
            smooth_l1_weight=0,
            ranknet_weight=1,
        )
        self.assertEqual(combined.pair_count, 2)

    def test_fixed_scoring_head_has_2497_parameters_and_ignores_future_suffix(self) -> None:
        head = KronosScoringHead()
        self.assertEqual(sum(parameter.numel() for parameter in head.parameters()), 2_497)
        prefix = torch.randn(2, 3, 832)
        context_a = torch.cat([prefix, torch.randn(2, 2, 832)], dim=1)
        context_b = torch.cat([prefix, torch.randn(2, 2, 832) * 100], dim=1)

        score_a = head(context_a, history_length=3)
        score_b = head(context_b, history_length=3)
        torch.testing.assert_close(score_a, score_b)

    def test_scorer_stage_freezes_every_model_parameter(self) -> None:
        model = ToyKronos()
        inject_kronos_lora(model, rank=2, alpha=4, dropout=0)
        head = KronosScoringHead(d_model=4)
        prepare_scorer_stage(model, head)
        batch = ScorerBatch(
            s1_ids=torch.randint(0, 7, (4, 3)),
            s2_ids=torch.randint(0, 5, (4, 3)),
            targets=torch.tensor([-1.0, 1.0, -0.5, 0.5]),
            dates=["a", "a", "b", "b"],
            history_length=3,
        )
        losses, _ = scorer_forward_loss(model, head, batch)
        losses.total.backward()

        self.assertTrue(all(parameter.grad is None for parameter in model.parameters()))
        self.assertTrue(any(parameter.grad is not None for parameter in head.parameters()))


class CheckpointTests(unittest.TestCase):
    def _injected_model(self) -> ToyKronos:
        model = ToyKronos()
        inject_kronos_lora(model, rank=2, alpha=4, dropout=0)
        return model

    def test_checkpoint_roundtrip_hash_binding_and_rng_restore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "checkpoints"
            model = self._injected_model()
            optimizer = torch.optim.Adam(
                [parameter for parameter in model.parameters() if parameter.requires_grad],
                lr=1e-3,
            )
            store = CheckpointStore(root, binding("a"))
            set_deterministic_seed(123)
            saved_lora = lora_state_dict(model)
            path = store.save(
                stage="adapter",
                step=100,
                model=model,
                optimizer=optimizer,
                metric=1.25,
                is_best=True,
                extra_state={"epoch": 3},
            )
            expected_random = (
                random.random(),
                float(np.random.random()),
                torch.rand(3),
            )

            random.seed(999)
            np.random.seed(999)
            torch.manual_seed(999)
            with torch.no_grad():
                for module in model.modules():
                    if hasattr(module, "lora_A"):
                        module.lora_A.zero_()
                        module.lora_B.zero_()
            loaded = store.load(
                "latest", model=model, optimizer=optimizer, restore_rng=True
            )

            self.assertEqual(loaded.path, path)
            self.assertEqual(loaded.step, 100)
            self.assertEqual(loaded.extra_state, {"epoch": 3})
            self.assertTrue((path / "COMMITTED").is_file())
            self.assertTrue((root / "latest.json").is_file())
            self.assertTrue((root / "best.json").is_file())
            for key, value in saved_lora.items():
                torch.testing.assert_close(lora_state_dict(model)[key], value)
            actual_random = (
                random.random(),
                float(np.random.random()),
                torch.rand(3),
            )
            self.assertEqual(actual_random[0], expected_random[0])
            self.assertEqual(actual_random[1], expected_random[1])
            torch.testing.assert_close(actual_random[2], expected_random[2])

            manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["binding"], binding("a").as_dict())

    def test_checkpoint_rejects_another_model_or_dataset_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "checkpoints"
            model = self._injected_model()
            CheckpointStore(root, binding("a")).save(
                stage="adapter", step=1, model=model
            )
            pointer_before = (root / "latest.json").read_bytes()
            with self.assertRaisesRegex(CheckpointIntegrityError, "哈希不匹配"):
                CheckpointStore(root, binding("b")).inspect(
                    "adapter-step-00000001"
                )
            self.assertEqual((root / "latest.json").read_bytes(), pointer_before)

    def test_recovery_removes_only_incomplete_checkpoint_transactions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "checkpoints"
            root.mkdir()
            model = self._injected_model()
            store = CheckpointStore(root, binding("a"))
            good = store.save(stage="adapter", step=1, model=model)
            (root / ".adapter-step-00000002.pending-dead").mkdir()
            incomplete = root / "adapter-step-00000003"
            incomplete.mkdir()
            (incomplete / "state.pt").write_bytes(b"partial")
            (root / "latest.json").unlink()

            report = store.recover()

            self.assertTrue(good.is_dir())
            self.assertFalse((root / ".adapter-step-00000002.pending-dead").exists())
            self.assertFalse(incomplete.exists())
            self.assertTrue((root / "latest.json").is_file())
            self.assertEqual(report["valid"], ["adapter-step-00000001"])

    def test_read_only_checkpoint_load_never_recovers_or_rewrites(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "checkpoints"
            source_model = self._injected_model()
            store = CheckpointStore(root, binding("a"))
            store.save(stage="adapter", step=1, model=source_model)
            pointer_before = (root / "latest.json").read_bytes()
            pending = root / ".adapter-step-00000002.pending-diagnostic"
            pending.mkdir()

            target_model = self._injected_model()
            manifest = store.inspect_read_only("adapter-step-00000001")
            loaded = store.load(
                "adapter-step-00000001",
                model=target_model,
                restore_rng=False,
                read_only=True,
            )

            self.assertEqual(manifest["step"], 1)
            self.assertEqual(loaded.step, 1)
            self.assertTrue(pending.is_dir())
            self.assertEqual((root / "latest.json").read_bytes(), pointer_before)

    def test_scorer_checkpoint_roundtrip_restores_head_and_keeps_lora_frozen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            model = self._injected_model()
            head = KronosScoringHead(d_model=4)
            prepare_scorer_stage(model, head)
            saved_head = copy.deepcopy(head.state_dict())
            store = CheckpointStore(Path(tmp) / "checkpoints", binding("a"))
            store.save(stage="scorer", step=2, model=model, scoring_head=head)
            with torch.no_grad():
                for parameter in head.parameters():
                    parameter.zero_()
            store.load("latest", model=model, scoring_head=head, restore_rng=False)

            for key, value in saved_head.items():
                torch.testing.assert_close(head.state_dict()[key], value)
            self.assertTrue(all(not parameter.requires_grad for parameter in model.parameters()))

    def test_os_lock_rejects_a_second_writer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "checkpoint.lock"
            with CheckpointFileLock(lock_path):
                with self.assertRaises(CheckpointBusyError):
                    with CheckpointFileLock(lock_path):
                        self.fail("第二个 writer 不应获得 OS lock")


class AdapterSelectionTests(unittest.TestCase):
    def test_selects_step200_from_live_causal_history_not_last_checkpoint(self) -> None:
        selection = select_validated_adapter(
            [
                {"step": 100, "validation_ce": 2.660604},
                {"step": 200, "validation_ce": 2.634986},
                {"step": 1000, "validation_ce": 4.442699},
            ],
            zero_shot_validation_ce=2.6643258333,
            minimum_improvement=0.01,
        )
        self.assertEqual(selection.best_step, 200)
        self.assertFalse(selection.zero_shot_fallback)
        self.assertGreaterEqual(selection.improvement, 0.01)
        self.assertEqual(selection.stale_validations, 1)

    def test_falls_back_to_zero_shot_when_best_gain_is_below_one_percent(self) -> None:
        selection = select_validated_adapter(
            [{"step": 50, "validation_ce": 0.995}],
            zero_shot_validation_ce=1.0,
            minimum_improvement=0.01,
        )
        self.assertTrue(selection.zero_shot_fallback)
        self.assertEqual(
            selection.selection_reason,
            "best_adapter_below_minimum_ce_improvement",
        )

    def test_equal_validation_ce_keeps_earlier_checkpoint(self) -> None:
        selection = select_validated_adapter(
            [
                {"step": 50, "validation_ce": 0.98},
                {"step": 100, "validation_ce": 0.98},
            ],
            zero_shot_validation_ce=1.0,
        )
        self.assertEqual(selection.best_step, 50)
        self.assertEqual(selection.stale_validations, 1)


class RngStateTests(unittest.TestCase):
    def test_capture_and_restore_is_deterministic_for_python_numpy_and_torch(self) -> None:
        set_deterministic_seed(77)
        state = capture_rng_state()
        expected = (random.random(), np.random.random(), torch.rand(2))
        _ = (random.random(), np.random.random(), torch.rand(2))
        restore_rng_state(state)
        actual = (random.random(), np.random.random(), torch.rand(2))

        self.assertEqual(actual[0], expected[0])
        self.assertEqual(actual[1], expected[1])
        torch.testing.assert_close(actual[2], expected[2])


if __name__ == "__main__":
    unittest.main()
