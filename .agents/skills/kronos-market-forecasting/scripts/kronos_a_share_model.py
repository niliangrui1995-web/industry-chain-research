"""Small, auditable model components for the Kronos A-share adapters.

This module deliberately does not import or modify the protected upstream Kronos
checkout.  Callers pass an already-loaded Kronos model (or a compatible test
double) and this module wraps the exact attention projections used by
Kronos-base.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import torch
from torch import nn
from torch.nn import functional as F


KRONOS_BASE_LAYER_COUNT = 12
DEFAULT_LORA_RANK = 8
DEFAULT_LORA_ALPHA = 16.0
DEFAULT_LORA_DROPOUT = 0.05
DEFAULT_D_MODEL = 832

KRONOS_LORA_TARGETS: tuple[str, ...] = tuple(
    name
    for layer_index in range(KRONOS_BASE_LAYER_COUNT)
    for name in (
        f"transformer.{layer_index}.self_attn.q_proj",
        f"transformer.{layer_index}.self_attn.v_proj",
    )
) + (
    "dep_layer.cross_attn.q_proj",
    "dep_layer.cross_attn.v_proj",
)


class LoRAContractError(RuntimeError):
    """The supplied model or adapter state does not match the fixed contract."""


class LoRALinear(nn.Module):
    """A dependency-free LoRA wrapper around a frozen ``nn.Linear`` layer."""

    def __init__(
        self,
        base: nn.Linear,
        *,
        rank: int = DEFAULT_LORA_RANK,
        alpha: float = DEFAULT_LORA_ALPHA,
        dropout: float = DEFAULT_LORA_DROPOUT,
    ) -> None:
        super().__init__()
        if not isinstance(base, nn.Linear):
            raise TypeError("base 必须是 torch.nn.Linear")
        if rank <= 0:
            raise ValueError("rank 必须大于 0")
        if alpha <= 0:
            raise ValueError("alpha 必须大于 0")
        if not 0.0 <= dropout < 1.0:
            raise ValueError("dropout 必须位于 [0, 1)")

        self.base = base
        self.rank = int(rank)
        self.alpha = float(alpha)
        self.scaling = self.alpha / self.rank
        self.dropout_p = float(dropout)
        self.lora_dropout = nn.Dropout(self.dropout_p)

        for parameter in self.base.parameters():
            parameter.requires_grad_(False)

        factory = {"device": base.weight.device, "dtype": base.weight.dtype}
        self.lora_A = nn.Parameter(torch.empty(self.rank, base.in_features, **factory))
        self.lora_B = nn.Parameter(torch.empty(base.out_features, self.rank, **factory))
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        nn.init.zeros_(self.lora_B)

    @property
    def in_features(self) -> int:
        return self.base.in_features

    @property
    def out_features(self) -> int:
        return self.base.out_features

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        base_output = self.base(inputs)
        low_rank = F.linear(F.linear(self.lora_dropout(inputs), self.lora_A), self.lora_B)
        return base_output + low_rank * self.scaling


@dataclass(frozen=True)
class LoRAInjectionReport:
    target_names: tuple[str, ...]
    target_count: int
    trainable_parameters: int
    total_parameters: int


def _projection_names(model: nn.Module) -> set[str]:
    return {
        name
        for name, module in model.named_modules()
        if name.endswith((".q_proj", ".v_proj"))
        and isinstance(module, (nn.Linear, LoRALinear))
    }


def _parent_and_attribute(model: nn.Module, qualified_name: str) -> tuple[nn.Module, str]:
    parent_name, separator, attribute = qualified_name.rpartition(".")
    if not separator:
        return model, qualified_name
    try:
        parent = model.get_submodule(parent_name)
    except AttributeError as exc:
        raise LoRAContractError(f"缺少 LoRA 目标父模块：{parent_name}") from exc
    return parent, attribute


def inject_kronos_lora(
    model: nn.Module,
    *,
    rank: int = DEFAULT_LORA_RANK,
    alpha: float = DEFAULT_LORA_ALPHA,
    dropout: float = DEFAULT_LORA_DROPOUT,
    strict: bool = True,
) -> LoRAInjectionReport:
    """Freeze ``model`` and wrap the exact 26 Kronos-base q/v projections.

    In strict mode an extra or missing q/v projection is considered architecture
    drift.  Re-entry is accepted only when every target is already wrapped with
    exactly the requested LoRA hyperparameters.
    """

    discovered = _projection_names(model)
    expected = set(KRONOS_LORA_TARGETS)
    missing = sorted(expected - discovered)
    extra = sorted(discovered - expected)
    if missing or (strict and extra):
        raise LoRAContractError(
            "Kronos LoRA 目标不匹配："
            f"missing={missing or []}, extra={extra or []}, expected_count=26"
        )

    for parameter in model.parameters():
        parameter.requires_grad_(False)

    for target_name in KRONOS_LORA_TARGETS:
        parent, attribute = _parent_and_attribute(model, target_name)
        current = getattr(parent, attribute, None)
        if isinstance(current, LoRALinear):
            if (
                current.rank != rank
                or current.alpha != float(alpha)
                or current.dropout_p != float(dropout)
            ):
                raise LoRAContractError(
                    f"已注入的 LoRA 参数不一致：{target_name}"
                )
            current.lora_A.requires_grad_(True)
            current.lora_B.requires_grad_(True)
            continue
        if not isinstance(current, nn.Linear):
            raise LoRAContractError(
                f"LoRA 目标必须是 nn.Linear：{target_name}={type(current).__name__}"
            )
        setattr(
            parent,
            attribute,
            LoRALinear(current, rank=rank, alpha=alpha, dropout=dropout),
        )

    trainable_names = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    expected_trainable = {
        f"{target}.{suffix}"
        for target in KRONOS_LORA_TARGETS
        for suffix in ("lora_A", "lora_B")
    }
    if trainable_names != expected_trainable:
        raise LoRAContractError(
            "冻结合同失败：除 LoRA A/B 外仍有可训练参数，"
            f"unexpected={sorted(trainable_names - expected_trainable)}"
        )

    return LoRAInjectionReport(
        target_names=KRONOS_LORA_TARGETS,
        target_count=len(KRONOS_LORA_TARGETS),
        trainable_parameters=sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        ),
        total_parameters=sum(parameter.numel() for parameter in model.parameters()),
    )


def iter_lora_modules(model: nn.Module) -> Iterable[tuple[str, LoRALinear]]:
    for target_name in KRONOS_LORA_TARGETS:
        try:
            module = model.get_submodule(target_name)
        except AttributeError as exc:
            raise LoRAContractError(f"缺少已注入 LoRA 目标：{target_name}") from exc
        if not isinstance(module, LoRALinear):
            raise LoRAContractError(f"目标尚未注入 LoRA：{target_name}")
        yield target_name, module


def set_lora_trainable(model: nn.Module, trainable: bool) -> None:
    """Freeze the full model, then optionally enable only LoRA A/B tensors."""

    for parameter in model.parameters():
        parameter.requires_grad_(False)
    for _, module in iter_lora_modules(model):
        module.lora_A.requires_grad_(trainable)
        module.lora_B.requires_grad_(trainable)


def lora_state_dict(model: nn.Module) -> dict[str, torch.Tensor]:
    state: dict[str, torch.Tensor] = {}
    for target_name, module in iter_lora_modules(model):
        state[f"{target_name}.lora_A"] = module.lora_A.detach().cpu().clone()
        state[f"{target_name}.lora_B"] = module.lora_B.detach().cpu().clone()
    return state


def load_lora_state_dict(
    model: nn.Module,
    state: Mapping[str, torch.Tensor],
    *,
    strict: bool = True,
) -> None:
    expected_keys = {
        f"{target_name}.{suffix}"
        for target_name in KRONOS_LORA_TARGETS
        for suffix in ("lora_A", "lora_B")
    }
    supplied_keys = set(state)
    if strict and supplied_keys != expected_keys:
        raise LoRAContractError(
            "LoRA state_dict 键不匹配："
            f"missing={sorted(expected_keys - supplied_keys)}, "
            f"extra={sorted(supplied_keys - expected_keys)}"
        )

    with torch.no_grad():
        for target_name, module in iter_lora_modules(model):
            for suffix in ("lora_A", "lora_B"):
                key = f"{target_name}.{suffix}"
                if key not in state:
                    if strict:
                        raise LoRAContractError(f"LoRA state_dict 缺少：{key}")
                    continue
                destination = getattr(module, suffix)
                source = state[key]
                if not isinstance(source, torch.Tensor) or source.shape != destination.shape:
                    raise LoRAContractError(
                        f"LoRA 张量形状不匹配：{key}, "
                        f"expected={tuple(destination.shape)}, "
                        f"actual={getattr(source, 'shape', None)}"
                    )
                destination.copy_(source.to(device=destination.device, dtype=destination.dtype))


def build_future_mask(
    sequence_length: int,
    history_length: int,
    future_length: int,
    *,
    batch_size: int | None = None,
    device: torch.device | str | None = None,
) -> torch.Tensor:
    """Create a target-position mask for future bars in an aligned token sequence."""

    if sequence_length <= 0:
        raise ValueError("sequence_length 必须大于 0")
    if history_length < 0 or future_length <= 0:
        raise ValueError("history_length 不得为负且 future_length 必须大于 0")
    if history_length + future_length > sequence_length:
        raise ValueError("历史与未来窗口超出序列长度")
    mask = torch.zeros(sequence_length, dtype=torch.bool, device=device)
    mask[history_length : history_length + future_length] = True
    if batch_size is not None:
        if batch_size <= 0:
            raise ValueError("batch_size 必须大于 0")
        mask = mask.unsqueeze(0).expand(batch_size, -1).clone()
    return mask


def future_token_cross_entropy(
    s1_logits: torch.Tensor,
    s2_logits: torch.Tensor,
    s1_targets: torch.Tensor,
    s2_targets: torch.Tensor,
    future_mask: torch.Tensor,
    *,
    ignore_index: int = -100,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Compute CE only at explicitly marked future target positions."""

    if s1_logits.ndim != 3 or s2_logits.ndim != 3:
        raise ValueError("logits 必须是 [batch, sequence, vocabulary]")
    if s1_logits.shape[:2] != s2_logits.shape[:2]:
        raise ValueError("s1/s2 logits 的 batch 与 sequence 必须一致")
    if s1_targets.shape != s1_logits.shape[:2] or s2_targets.shape != s2_logits.shape[:2]:
        raise ValueError("targets 必须与 logits 的前两维一致")
    if future_mask.ndim == 1:
        if future_mask.shape[0] != s1_logits.shape[1]:
            raise ValueError("一维 future_mask 长度不匹配")
        future_mask = future_mask.unsqueeze(0).expand(s1_logits.shape[0], -1)
    if future_mask.shape != s1_logits.shape[:2]:
        raise ValueError("future_mask 必须是 [sequence] 或 [batch, sequence]")
    mask = future_mask.to(device=s1_logits.device, dtype=torch.bool)
    mask_s1 = mask & (s1_targets.to(s1_logits.device) != ignore_index)
    mask_s2 = mask & (s2_targets.to(s2_logits.device) != ignore_index)
    if not bool(mask_s1.any()) or not bool(mask_s2.any()):
        raise ValueError("future_mask 没有可用于两个 token 层级的目标")

    s1_target_device = s1_targets.to(s1_logits.device)
    s2_target_device = s2_targets.to(s2_logits.device)
    ce_s1 = F.cross_entropy(s1_logits[mask_s1], s1_target_device[mask_s1])
    ce_s2 = F.cross_entropy(s2_logits[mask_s2], s2_target_device[mask_s2])
    return (ce_s1 + ce_s2) / 2.0, ce_s1, ce_s2


class KronosScoringHead(nn.Module):
    """The fixed LayerNorm(d_model) -> Linear(d_model, 1) cross-sectional head."""

    def __init__(self, d_model: int = DEFAULT_D_MODEL) -> None:
        super().__init__()
        if d_model <= 0:
            raise ValueError("d_model 必须大于 0")
        self.d_model = int(d_model)
        self.norm = nn.LayerNorm(self.d_model)
        self.projection = nn.Linear(self.d_model, 1)

    def forward(
        self,
        context: torch.Tensor,
        history_length: int | torch.Tensor | None = None,
    ) -> torch.Tensor:
        if context.ndim != 3 or context.shape[-1] != self.d_model:
            raise ValueError(
                f"context 必须是 [batch, sequence, {self.d_model}]"
            )
        batch_size, sequence_length, _ = context.shape
        if history_length is None:
            last_state = context[:, -1]
        elif isinstance(history_length, int):
            if not 1 <= history_length <= sequence_length:
                raise ValueError("history_length 超出 context")
            last_state = context[:, history_length - 1]
        else:
            lengths = history_length.to(device=context.device, dtype=torch.long).reshape(-1)
            if lengths.numel() != batch_size:
                raise ValueError("逐样本 history_length 数量与 batch 不一致")
            if bool(((lengths < 1) | (lengths > sequence_length)).any()):
                raise ValueError("逐样本 history_length 超出 context")
            last_state = context[
                torch.arange(batch_size, device=context.device), lengths - 1
            ]
        return self.projection(self.norm(last_state)).squeeze(-1)


def score_historical_tokens(
    model: nn.Module,
    scoring_head: KronosScoringHead,
    s1_ids: torch.Tensor,
    s2_ids: torch.Tensor,
    *,
    stamp: torch.Tensor | None = None,
    padding_mask: torch.Tensor | None = None,
    history_length: int | torch.Tensor | None = None,
) -> torch.Tensor:
    """Score a historical prefix from ``decode_s1`` without consuming future bars."""

    _, context = model.decode_s1(
        s1_ids,
        s2_ids,
        stamp=stamp,
        padding_mask=padding_mask,
    )
    return scoring_head(context, history_length=history_length)


def _date_groups(dates: Sequence[Any] | torch.Tensor, count: int) -> list[list[int]]:
    if isinstance(dates, torch.Tensor):
        values = dates.detach().cpu().reshape(-1).tolist()
    else:
        values = list(dates)
    if len(values) != count:
        raise ValueError("dates 数量与 scores 不一致")
    groups: dict[Any, list[int]] = {}
    for index, value in enumerate(values):
        groups.setdefault(value, []).append(index)
    return list(groups.values())


def grouped_ranknet_loss(
    scores: torch.Tensor,
    targets: torch.Tensor,
    dates: Sequence[Any] | torch.Tensor,
) -> tuple[torch.Tensor, int]:
    """RankNet over comparable pairs from the same date only."""

    scores = scores.reshape(-1)
    targets = targets.to(device=scores.device, dtype=scores.dtype).reshape(-1)
    if scores.shape != targets.shape:
        raise ValueError("scores 与 targets 形状不一致")
    losses: list[torch.Tensor] = []
    pair_count = 0
    for indices in _date_groups(dates, scores.numel()):
        if len(indices) < 2:
            continue
        index_tensor = torch.tensor(indices, device=scores.device, dtype=torch.long)
        group_scores = scores[index_tensor]
        group_targets = targets[index_tensor]
        score_diff = group_scores[:, None] - group_scores[None, :]
        target_diff = group_targets[:, None] - group_targets[None, :]
        comparable = torch.triu(target_diff != 0, diagonal=1)
        if not bool(comparable.any()):
            continue
        signs = torch.sign(target_diff[comparable])
        losses.append(F.softplus(-signs * score_diff[comparable]))
        pair_count += int(comparable.sum().item())
    if not losses:
        return scores.sum() * 0.0, 0
    return torch.cat(losses).mean(), pair_count


@dataclass(frozen=True)
class ScorerLoss:
    total: torch.Tensor
    smooth_l1: torch.Tensor
    ranknet: torch.Tensor
    pair_count: int


def cross_sectional_scorer_loss(
    scores: torch.Tensor,
    targets: torch.Tensor,
    dates: Sequence[Any] | torch.Tensor,
    *,
    smooth_l1_weight: float = 1.0,
    ranknet_weight: float = 1.0,
    smooth_l1_beta: float = 1.0,
) -> ScorerLoss:
    if smooth_l1_weight < 0 or ranknet_weight < 0:
        raise ValueError("loss 权重不得为负")
    if smooth_l1_weight == 0 and ranknet_weight == 0:
        raise ValueError("至少一个 loss 权重必须大于 0")
    flattened_scores = scores.reshape(-1)
    flattened_targets = targets.to(
        device=flattened_scores.device, dtype=flattened_scores.dtype
    ).reshape(-1)
    if flattened_scores.shape != flattened_targets.shape:
        raise ValueError("scores 与 targets 形状不一致")
    if not bool(torch.isfinite(flattened_scores).all()) or not bool(
        torch.isfinite(flattened_targets).all()
    ):
        raise ValueError("scores/targets 含 NaN 或 Inf")
    smooth_l1 = F.smooth_l1_loss(
        flattened_scores, flattened_targets, beta=smooth_l1_beta
    )
    ranknet, pair_count = grouped_ranknet_loss(
        flattened_scores, flattened_targets, dates
    )
    total = smooth_l1_weight * smooth_l1 + ranknet_weight * ranknet
    return ScorerLoss(total, smooth_l1, ranknet, pair_count)


def count_trainable_parameters(module: nn.Module) -> int:
    return sum(parameter.numel() for parameter in module.parameters() if parameter.requires_grad)


def validate_kronos_base_adapter_parameter_count(model: nn.Module) -> int:
    """Assert the production r=8, d_model=832 adapter has 346,112 parameters."""

    trainable = count_trainable_parameters(model)
    expected = 346_112
    if trainable != expected:
        raise LoRAContractError(
            f"Kronos-base LoRA 可训练参数不匹配：expected={expected}, actual={trainable}"
        )
    return trainable
