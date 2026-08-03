"""Two-stage training and crash-safe checkpoints for Kronos A-share adapters."""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import shutil
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch
from torch import nn

try:
    from kronos_a_share_model import (
        KRONOS_LORA_TARGETS,
        KronosScoringHead,
        LoRAContractError,
        LoRALinear,
        ScorerLoss,
        cross_sectional_scorer_loss,
        future_token_cross_entropy,
        inject_kronos_lora,
        iter_lora_modules,
        load_lora_state_dict,
        lora_state_dict,
        set_lora_trainable,
    )
except ImportError:  # pragma: no cover - package-style import fallback
    from .kronos_a_share_model import (
        KRONOS_LORA_TARGETS,
        KronosScoringHead,
        LoRAContractError,
        LoRALinear,
        ScorerLoss,
        cross_sectional_scorer_loss,
        future_token_cross_entropy,
        inject_kronos_lora,
        iter_lora_modules,
        load_lora_state_dict,
        lora_state_dict,
        set_lora_trainable,
    )


CHECKPOINT_PROTOCOL = "kronos-a-share-checkpoint-v1"
REQUIRED_HASH_NAMES = (
    "base_model_sha256",
    "tokenizer_sha256",
    "config_sha256",
    "dataset_sha256",
)
CHECKPOINT_NAME_PATTERN = re.compile(r"^(adapter|scorer)-step-(\d{8})$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class TrainingContractError(RuntimeError):
    """Training inputs or state violate the fixed two-stage contract."""


class CheckpointIntegrityError(RuntimeError):
    """A checkpoint is incomplete, corrupt, or bound to another experiment."""


class CheckpointBindingError(CheckpointIntegrityError):
    """The checkpoint belongs to another model, tokenizer, config, or dataset."""


class CheckpointBusyError(RuntimeError):
    """Another process currently owns the checkpoint store."""


@dataclass(frozen=True)
class CheckpointBinding:
    base_model_sha256: str
    tokenizer_sha256: str
    config_sha256: str
    dataset_sha256: str

    def __post_init__(self) -> None:
        for name in REQUIRED_HASH_NAMES:
            value = getattr(self, name)
            if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value.lower()) is None:
                raise ValueError(f"{name} 必须是64位 SHA256")
            object.__setattr__(self, name, value.lower())

    def as_dict(self) -> dict[str, str]:
        return {name: getattr(self, name) for name in REQUIRED_HASH_NAMES}

    @classmethod
    def from_mapping(cls, value: Mapping[str, str]) -> "CheckpointBinding":
        missing = set(REQUIRED_HASH_NAMES) - set(value)
        extra = set(value) - set(REQUIRED_HASH_NAMES)
        if missing or extra:
            raise ValueError(
                f"checkpoint binding 字段不匹配：missing={sorted(missing)}, extra={sorted(extra)}"
            )
        return cls(**{name: value[name] for name in REQUIRED_HASH_NAMES})


@dataclass(frozen=True)
class AdapterBatch:
    s1_ids: torch.Tensor
    s2_ids: torch.Tensor
    s1_targets: torch.Tensor
    s2_targets: torch.Tensor
    future_mask: torch.Tensor
    stamp: torch.Tensor | None = None
    padding_mask: torch.Tensor | None = None


@dataclass(frozen=True)
class ScorerBatch:
    s1_ids: torch.Tensor
    s2_ids: torch.Tensor
    targets: torch.Tensor
    dates: Sequence[Any] | torch.Tensor
    stamp: torch.Tensor | None = None
    padding_mask: torch.Tensor | None = None
    history_length: int | torch.Tensor | None = None


@dataclass(frozen=True)
class LoadedCheckpoint:
    path: Path
    stage: str
    step: int
    metric: float | None
    manifest: dict[str, Any]
    extra_state: dict[str, Any]


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_lora_state_sha256(state: Mapping[str, torch.Tensor]) -> str:
    """Hash LoRA tensors independently of ``torch.save`` container metadata."""

    if not isinstance(state, Mapping) or not state:
        raise CheckpointIntegrityError("checkpoint LoRA state 为空或类型无效")
    digest = hashlib.sha256()
    for name in sorted(state):
        tensor = state[name]
        if not isinstance(name, str) or not isinstance(tensor, torch.Tensor):
            raise CheckpointIntegrityError("checkpoint LoRA state 键或张量类型无效")
        value = tensor.detach().cpu().contiguous()
        name_bytes = name.encode("utf-8")
        dtype_bytes = str(value.dtype).encode("ascii")
        shape_bytes = json.dumps(list(value.shape), separators=(",", ":")).encode(
            "ascii"
        )
        raw = value.view(torch.uint8).numpy().tobytes(order="C")
        for payload in (name_bytes, dtype_bytes, shape_bytes, raw):
            digest.update(len(payload).to_bytes(8, byteorder="big", signed=False))
            digest.update(payload)
    return digest.hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _binding_digest(binding: CheckpointBinding) -> str:
    return _sha256_bytes(_canonical_json(binding.as_dict()))


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_exclusive(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.parent / f".{path.name}.pending-{uuid.uuid4().hex}"
    _write_exclusive(pending, payload)
    os.replace(pending, path)
    _fsync_directory(path.parent)


class CheckpointFileLock:
    """Non-blocking OS lock; a process crash releases the kernel lock."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle: Any | None = None

    def __enter__(self) -> "CheckpointFileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        self.handle.seek(0, os.SEEK_END)
        if self.handle.tell() == 0:
            self.handle.write(b"\0")
            self.handle.flush()
            os.fsync(self.handle.fileno())
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close()
            self.handle = None
            raise CheckpointBusyError(f"checkpoint 已被其他训练进程锁定：{self.path}") from exc
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        assert self.handle is not None
        try:
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
            self.handle = None


def set_deterministic_seed(seed: int, *, deterministic_algorithms: bool = False) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic_algorithms:
        torch.use_deterministic_algorithms(True)


def capture_rng_state() -> dict[str, Any]:
    numpy_state = np.random.get_state()
    state: dict[str, Any] = {
        "python": random.getstate(),
        "numpy": {
            "bit_generator": numpy_state[0],
            "keys": numpy_state[1].astype(np.uint32).tolist(),
            "position": int(numpy_state[2]),
            "has_gauss": int(numpy_state[3]),
            "cached_gaussian": float(numpy_state[4]),
        },
        "torch_cpu": torch.get_rng_state().cpu(),
        "torch_cuda": [],
    }
    if torch.cuda.is_available():
        state["torch_cuda"] = [item.cpu() for item in torch.cuda.get_rng_state_all()]
    return state


def _recursive_tuple(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_recursive_tuple(item) for item in value)
    return value


def restore_rng_state(state: Mapping[str, Any]) -> None:
    required = {"python", "numpy", "torch_cpu", "torch_cuda"}
    if set(state) != required:
        raise CheckpointIntegrityError("RNG state 字段不完整")
    random.setstate(_recursive_tuple(state["python"]))
    numpy_state = state["numpy"]
    np.random.set_state(
        (
            numpy_state["bit_generator"],
            np.asarray(numpy_state["keys"], dtype=np.uint32),
            int(numpy_state["position"]),
            int(numpy_state["has_gauss"]),
            float(numpy_state["cached_gaussian"]),
        )
    )
    torch.set_rng_state(state["torch_cpu"].cpu())
    cuda_states = state["torch_cuda"]
    if cuda_states:
        if not torch.cuda.is_available():
            raise CheckpointIntegrityError("checkpoint 含 CUDA RNG，但当前 CUDA 不可用")
        if len(cuda_states) != torch.cuda.device_count():
            raise CheckpointIntegrityError("CUDA RNG 设备数量与当前环境不一致")
        torch.cuda.set_rng_state_all([item.cpu() for item in cuda_states])


def prepare_adapter_stage(
    model: nn.Module,
    *,
    rank: int = 8,
    alpha: float = 16.0,
    dropout: float = 0.05,
) -> None:
    inject_kronos_lora(model, rank=rank, alpha=alpha, dropout=dropout, strict=True)
    set_lora_trainable(model, True)
    model.train()


def adapter_forward_loss(
    model: nn.Module,
    batch: AdapterBatch,
) -> tuple[torch.Tensor, dict[str, float]]:
    s1_logits, s2_logits = model(
        batch.s1_ids,
        batch.s2_ids,
        stamp=batch.stamp,
        padding_mask=batch.padding_mask,
        use_teacher_forcing=True,
        s1_targets=batch.s1_targets,
    )
    total, ce_s1, ce_s2 = future_token_cross_entropy(
        s1_logits,
        s2_logits,
        batch.s1_targets,
        batch.s2_targets,
        batch.future_mask,
    )
    metrics = {
        "loss": float(total.detach().cpu()),
        "ce_s1": float(ce_s1.detach().cpu()),
        "ce_s2": float(ce_s2.detach().cpu()),
    }
    return total, metrics


def adapter_train_step(
    model: nn.Module,
    batch: AdapterBatch,
    optimizer: torch.optim.Optimizer,
    *,
    max_grad_norm: float | None = None,
) -> dict[str, float]:
    set_lora_trainable(model, True)
    model.train()
    optimizer.zero_grad(set_to_none=True)
    loss, metrics = adapter_forward_loss(model, batch)
    loss.backward()
    if max_grad_norm is not None:
        if max_grad_norm <= 0:
            raise ValueError("max_grad_norm 必须大于 0")
        norm = nn.utils.clip_grad_norm_(
            [parameter for parameter in model.parameters() if parameter.requires_grad],
            max_grad_norm,
        )
        metrics["grad_norm"] = float(norm.detach().cpu())
    optimizer.step()
    return metrics


def prepare_scorer_stage(model: nn.Module, scoring_head: KronosScoringHead) -> None:
    set_lora_trainable(model, False)
    for parameter in scoring_head.parameters():
        parameter.requires_grad_(True)
    model.eval()
    scoring_head.train()


def scorer_forward_loss(
    model: nn.Module,
    scoring_head: KronosScoringHead,
    batch: ScorerBatch,
    *,
    smooth_l1_weight: float = 1.0,
    ranknet_weight: float = 1.0,
) -> tuple[ScorerLoss, torch.Tensor]:
    with torch.no_grad():
        _, context = model.decode_s1(
            batch.s1_ids,
            batch.s2_ids,
            stamp=batch.stamp,
            padding_mask=batch.padding_mask,
        )
    scores = scoring_head(context, history_length=batch.history_length)
    losses = cross_sectional_scorer_loss(
        scores,
        batch.targets,
        batch.dates,
        smooth_l1_weight=smooth_l1_weight,
        ranknet_weight=ranknet_weight,
    )
    return losses, scores


def scorer_train_step(
    model: nn.Module,
    scoring_head: KronosScoringHead,
    batch: ScorerBatch,
    optimizer: torch.optim.Optimizer,
    *,
    smooth_l1_weight: float = 1.0,
    ranknet_weight: float = 1.0,
    max_grad_norm: float | None = None,
) -> dict[str, float | int]:
    prepare_scorer_stage(model, scoring_head)
    optimizer.zero_grad(set_to_none=True)
    losses, _ = scorer_forward_loss(
        model,
        scoring_head,
        batch,
        smooth_l1_weight=smooth_l1_weight,
        ranknet_weight=ranknet_weight,
    )
    losses.total.backward()
    metrics: dict[str, float | int] = {
        "loss": float(losses.total.detach().cpu()),
        "smooth_l1": float(losses.smooth_l1.detach().cpu()),
        "ranknet": float(losses.ranknet.detach().cpu()),
        "pair_count": losses.pair_count,
    }
    if max_grad_norm is not None:
        if max_grad_norm <= 0:
            raise ValueError("max_grad_norm 必须大于 0")
        norm = nn.utils.clip_grad_norm_(scoring_head.parameters(), max_grad_norm)
        metrics["grad_norm"] = float(norm.detach().cpu())
    optimizer.step()
    return metrics


def _lora_configuration(model: nn.Module) -> dict[str, float | int]:
    modules = list(iter_lora_modules(model))
    configurations = {
        (module.rank, module.alpha, module.dropout_p) for _, module in modules
    }
    if len(configurations) != 1:
        raise LoRAContractError("26个 LoRA 目标的超参数不一致")
    rank, alpha, dropout = configurations.pop()
    return {"rank": rank, "alpha": alpha, "dropout": dropout}


class CheckpointStore:
    """Hash-bound, single-writer checkpoint storage with crash recovery."""

    def __init__(
        self,
        root: Path | str,
        binding: CheckpointBinding | Mapping[str, str],
    ) -> None:
        self.root = Path(root).resolve()
        self.binding = (
            binding
            if isinstance(binding, CheckpointBinding)
            else CheckpointBinding.from_mapping(binding)
        )
        self.lock_path = self.root / ".checkpoint.lock"

    def save(
        self,
        *,
        stage: str,
        step: int,
        model: nn.Module,
        optimizer: torch.optim.Optimizer | None = None,
        scoring_head: KronosScoringHead | None = None,
        metric: float | None = None,
        is_best: bool = False,
        extra_state: Mapping[str, Any] | None = None,
    ) -> Path:
        if stage not in {"adapter", "scorer"}:
            raise ValueError("stage 必须是 adapter 或 scorer")
        if not 0 <= step <= 99_999_999:
            raise ValueError("step 必须位于 0..99999999")
        if stage == "scorer" and scoring_head is None:
            raise ValueError("scorer checkpoint 必须提供 scoring_head")
        if stage == "adapter" and scoring_head is not None:
            raise ValueError("adapter checkpoint 不得混入 scoring_head")
        if metric is not None and not math.isfinite(metric):
            raise ValueError("metric 必须为有限数")

        model_trainable = {
            name for name, parameter in model.named_parameters() if parameter.requires_grad
        }
        expected_lora_trainable = {
            f"{target}.{suffix}"
            for target in KRONOS_LORA_TARGETS
            for suffix in ("lora_A", "lora_B")
        }
        if stage == "adapter" and model_trainable != expected_lora_trainable:
            raise TrainingContractError("adapter checkpoint 只允许26组 LoRA A/B 可训练")
        if stage == "scorer" and model_trainable:
            raise TrainingContractError("scorer checkpoint 要求 Kronos/LoRA 全部冻结")

        self.root.mkdir(parents=True, exist_ok=True)
        name = f"{stage}-step-{step:08d}"
        destination = self.root / name
        pending = self.root / f".{name}.pending-{uuid.uuid4().hex}"
        with CheckpointFileLock(self.lock_path):
            self._recover_unlocked()
            if destination.exists():
                raise FileExistsError(f"checkpoint 已存在：{destination}")
            pending.mkdir()
            state = {
                "protocol": CHECKPOINT_PROTOCOL,
                "stage": stage,
                "step": step,
                "lora_state": lora_state_dict(model),
                "scoring_head_state": (
                    scoring_head.state_dict() if scoring_head is not None else None
                ),
                "optimizer_state": (
                    optimizer.state_dict() if optimizer is not None else None
                ),
                "rng_state": capture_rng_state(),
                "extra_state": dict(extra_state or {}),
            }
            state_path = pending / "state.pt"
            with state_path.open("xb") as handle:
                torch.save(state, handle)
                handle.flush()
                os.fsync(handle.fileno())
            state_size = state_path.stat().st_size
            state_sha256 = _sha256_file(state_path)
            manifest = {
                "protocol": CHECKPOINT_PROTOCOL,
                "checkpoint_name": name,
                "stage": stage,
                "step": step,
                "metric": metric,
                "is_best": bool(is_best),
                "created_at_ns": time.time_ns(),
                "binding": self.binding.as_dict(),
                "binding_sha256": _binding_digest(self.binding),
                "lora": _lora_configuration(model),
                "files": {
                    "state.pt": {"size": state_size, "sha256": state_sha256}
                },
            }
            manifest_payload = _canonical_json(manifest)
            _write_exclusive(pending / "manifest.json", manifest_payload)
            committed = {
                "protocol": CHECKPOINT_PROTOCOL,
                "checkpoint_name": name,
                "manifest_sha256": _sha256_bytes(manifest_payload),
            }
            _write_exclusive(pending / "COMMITTED", _canonical_json(committed))
            _fsync_directory(pending)
            os.replace(pending, destination)
            _fsync_directory(self.root)
            self._write_pointer_unlocked("latest", manifest)
            if is_best:
                self._write_pointer_unlocked("best", manifest)
            return destination

    def load(
        self,
        reference: str,
        *,
        model: nn.Module,
        optimizer: torch.optim.Optimizer | None = None,
        scoring_head: KronosScoringHead | None = None,
        restore_rng: bool = True,
        map_location: str | torch.device = "cpu",
    ) -> LoadedCheckpoint:
        self.root.mkdir(parents=True, exist_ok=True)
        with CheckpointFileLock(self.lock_path):
            self._recover_unlocked()
            checkpoint_path = self._resolve_reference_unlocked(reference)
            manifest = self._validate_checkpoint_unlocked(checkpoint_path)
            state_path = checkpoint_path / "state.pt"
            try:
                state = torch.load(
                    state_path, map_location=map_location, weights_only=True
                )
            except TypeError:  # pragma: no cover - PyTorch <2.6 compatibility
                state = torch.load(state_path, map_location=map_location)
            if not isinstance(state, dict) or state.get("protocol") != CHECKPOINT_PROTOCOL:
                raise CheckpointIntegrityError("state.pt 协议不匹配")
            if state.get("stage") != manifest["stage"] or state.get("step") != manifest["step"]:
                raise CheckpointIntegrityError("state.pt 与 manifest 的阶段或步数不匹配")
            lora_config = manifest["lora"]
            try:
                first_target = model.get_submodule(KRONOS_LORA_TARGETS[0])
            except AttributeError as exc:
                raise LoRAContractError("待加载模型不是兼容的 Kronos-base") from exc
            if isinstance(first_target, nn.Linear):
                inject_kronos_lora(
                    model,
                    rank=int(lora_config["rank"]),
                    alpha=float(lora_config["alpha"]),
                    dropout=float(lora_config["dropout"]),
                    strict=True,
                )
            elif isinstance(first_target, LoRALinear):
                inject_kronos_lora(
                    model,
                    rank=int(lora_config["rank"]),
                    alpha=float(lora_config["alpha"]),
                    dropout=float(lora_config["dropout"]),
                    strict=True,
                )
            else:
                raise LoRAContractError("LoRA 首目标类型不兼容")
            load_lora_state_dict(model, state["lora_state"], strict=True)

            stage = manifest["stage"]
            saved_head_state = state.get("scoring_head_state")
            if stage == "scorer":
                if scoring_head is None:
                    raise TrainingContractError("加载 scorer checkpoint 必须提供 scoring_head")
                if saved_head_state is None:
                    raise CheckpointIntegrityError("scorer checkpoint 缺少评分头")
                scoring_head.load_state_dict(saved_head_state, strict=True)
            elif scoring_head is not None and saved_head_state is not None:
                scoring_head.load_state_dict(saved_head_state, strict=True)

            # Restore the stage's trainable-parameter contract as well as values.
            set_lora_trainable(model, stage == "adapter")

            saved_optimizer = state.get("optimizer_state")
            if optimizer is not None:
                if saved_optimizer is None:
                    raise TrainingContractError("checkpoint 未保存 optimizer state")
                optimizer.load_state_dict(saved_optimizer)
                expected_parameters = (
                    [parameter for parameter in model.parameters() if parameter.requires_grad]
                    if stage == "adapter"
                    else list(scoring_head.parameters()) if scoring_head is not None else []
                )
                optimizer_parameters = [
                    parameter
                    for group in optimizer.param_groups
                    for parameter in group["params"]
                ]
                if {id(parameter) for parameter in optimizer_parameters} != {
                    id(parameter) for parameter in expected_parameters
                }:
                    raise TrainingContractError(
                        "optimizer 参数组与当前训练阶段不匹配；请在 LoRA 注入后创建 optimizer"
                    )
            if restore_rng:
                restore_rng_state(state["rng_state"])
            return LoadedCheckpoint(
                path=checkpoint_path,
                stage=stage,
                step=int(manifest["step"]),
                metric=manifest["metric"],
                manifest=manifest,
                extra_state=dict(state.get("extra_state") or {}),
            )

    def inspect(self, reference: str = "latest") -> dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        with CheckpointFileLock(self.lock_path):
            self._recover_unlocked()
            return self._validate_checkpoint_unlocked(
                self._resolve_reference_unlocked(reference)
            )

    def recover(self) -> dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        with CheckpointFileLock(self.lock_path):
            return self._recover_unlocked()

    def _recover_unlocked(self) -> dict[str, Any]:
        removed: list[str] = []
        corrupt: list[str] = []
        for candidate in self.root.iterdir():
            if candidate.name.startswith(".") and ".pending-" in candidate.name:
                if candidate.is_dir():
                    shutil.rmtree(candidate)
                else:
                    candidate.unlink()
                removed.append(candidate.name)

        valid: list[dict[str, Any]] = []
        if self.root.exists():
            for candidate in self.root.iterdir():
                match = CHECKPOINT_NAME_PATTERN.fullmatch(candidate.name)
                if not match or not candidate.is_dir():
                    continue
                if not (candidate / "COMMITTED").is_file():
                    shutil.rmtree(candidate)
                    removed.append(candidate.name)
                    continue
                try:
                    valid.append(self._validate_checkpoint_unlocked(candidate))
                except CheckpointBindingError:
                    # A caller with the wrong experiment binding must never rewrite
                    # another run's latest/best pointers.
                    raise
                except CheckpointIntegrityError:
                    corrupt.append(candidate.name)

        valid.sort(key=lambda item: (int(item["created_at_ns"]), int(item["step"])))
        if valid:
            self._write_pointer_unlocked("latest", valid[-1])
        else:
            (self.root / "latest.json").unlink(missing_ok=True)
        best = [manifest for manifest in valid if manifest.get("is_best") is True]
        if best:
            self._write_pointer_unlocked("best", best[-1])
        else:
            (self.root / "best.json").unlink(missing_ok=True)
        return {
            "valid": [item["checkpoint_name"] for item in valid],
            "removed_incomplete": removed,
            "preserved_corrupt": corrupt,
        }

    def _write_pointer_unlocked(self, kind: str, manifest: Mapping[str, Any]) -> None:
        pointer = {
            "protocol": CHECKPOINT_PROTOCOL,
            "checkpoint_name": manifest["checkpoint_name"],
            "manifest_sha256": _sha256_file(
                self.root / manifest["checkpoint_name"] / "manifest.json"
            ),
            "binding_sha256": _binding_digest(self.binding),
        }
        _atomic_write(self.root / f"{kind}.json", _canonical_json(pointer))

    def _resolve_reference_unlocked(self, reference: str) -> Path:
        pointer: dict[str, Any] | None = None
        if reference in {"latest", "best"}:
            pointer_path = self.root / f"{reference}.json"
            if not pointer_path.is_file():
                raise FileNotFoundError(f"checkpoint 指针不存在：{pointer_path}")
            try:
                pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise CheckpointIntegrityError(f"checkpoint 指针不可解析：{pointer_path}") from exc
            if pointer.get("protocol") != CHECKPOINT_PROTOCOL:
                raise CheckpointIntegrityError("checkpoint 指针协议不匹配")
            if pointer.get("binding_sha256") != _binding_digest(self.binding):
                raise CheckpointIntegrityError("checkpoint 指针哈希绑定不匹配")
            reference = pointer.get("checkpoint_name", "")
        if CHECKPOINT_NAME_PATTERN.fullmatch(reference) is None:
            raise ValueError(f"非法 checkpoint 引用：{reference!r}")
        checkpoint_path = self.root / reference
        if pointer is not None:
            manifest_path = checkpoint_path / "manifest.json"
            if not manifest_path.is_file() or _sha256_file(manifest_path) != pointer.get(
                "manifest_sha256"
            ):
                raise CheckpointIntegrityError("checkpoint 指针的 manifest 哈希不匹配")
        return checkpoint_path

    def _validate_checkpoint_unlocked(self, checkpoint_path: Path) -> dict[str, Any]:
        if not checkpoint_path.is_dir():
            raise CheckpointIntegrityError(f"checkpoint 目录不存在：{checkpoint_path}")
        manifest_path = checkpoint_path / "manifest.json"
        committed_path = checkpoint_path / "COMMITTED"
        state_path = checkpoint_path / "state.pt"
        try:
            manifest_payload = manifest_path.read_bytes()
            manifest = json.loads(manifest_payload.decode("utf-8"))
            committed = json.loads(committed_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CheckpointIntegrityError(f"checkpoint metadata 不完整：{checkpoint_path}") from exc
        if (
            manifest.get("protocol") != CHECKPOINT_PROTOCOL
            or committed.get("protocol") != CHECKPOINT_PROTOCOL
            or manifest.get("checkpoint_name") != checkpoint_path.name
            or committed.get("checkpoint_name") != checkpoint_path.name
        ):
            raise CheckpointIntegrityError(f"checkpoint 身份不匹配：{checkpoint_path}")
        if committed.get("manifest_sha256") != _sha256_bytes(manifest_payload):
            raise CheckpointIntegrityError(f"manifest 哈希校验失败：{checkpoint_path}")
        if manifest.get("binding") != self.binding.as_dict() or manifest.get(
            "binding_sha256"
        ) != _binding_digest(self.binding):
            raise CheckpointBindingError("checkpoint 的模型/Tokenizer/配置/数据哈希不匹配")
        state_metadata = manifest.get("files", {}).get("state.pt", {})
        if not state_path.is_file():
            raise CheckpointIntegrityError(f"checkpoint 缺少 state.pt：{checkpoint_path}")
        if (
            state_path.stat().st_size != state_metadata.get("size")
            or _sha256_file(state_path) != state_metadata.get("sha256")
        ):
            raise CheckpointIntegrityError(f"state.pt 哈希校验失败：{checkpoint_path}")
        if CHECKPOINT_NAME_PATTERN.fullmatch(checkpoint_path.name) is None:
            raise CheckpointIntegrityError("checkpoint 名称非法")
        return manifest
