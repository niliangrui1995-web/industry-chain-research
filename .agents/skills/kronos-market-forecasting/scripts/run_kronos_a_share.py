#!/usr/bin/env python3
"""Unified, fail-closed CLI for the project-local Kronos A-share workflow."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import sys
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlsplit

import numpy as np
import pandas as pd
import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CONFIG = SCRIPT_DIR.parent / "configs" / "a_share_daily_v1.yaml"
CLI_SCHEMA_VERSION = "kronos-a-share-cli-v1"
CONFIG_SCHEMA_VERSION = "kronos-a-share-v1"
GATE_SCHEMA_VERSION = "kronos-a-share-gate-v2"
GATE_RECEIPT_SCHEMA_VERSION = "kronos-a-share-gate-receipt-v2"
GATE_HEAD_SCHEMA_VERSION = "kronos-a-share-gate-head-v1"
HORIZON = 10
LOOKBACK = 90
PURGE_DAYS = 11
SMOKE_NAMESPACE_SUFFIX = "-smoke-v5"
SMOKE_MAX_STEPS = 400
SMOKE_CHECKPOINT_INTERVAL = 50
FULL_MAX_STEPS = 10_000
FULL_CHECKPOINT_INTERVAL = 1_000
ADAPTER_EARLY_STOPPING_PATIENCE = 3
FORMAL_MIN_CROSS_SECTION = 100
FORMAL_MIN_COVERAGE_RATIO = 0.95
FORMAL_SCORER_SEEDS = tuple(range(100, 120))
FORMAL_ADAPTER_DIAGNOSTIC_LRS = (1e-5, 3e-5, 1e-4)
FORMAL_ADAPTER_DIAGNOSTIC_SEEDS = (100, 101, 102)
ADAPTER_DIAGNOSTIC_CE_CEILING = 2.637683
ADAPTER_DIAGNOSTIC_TIE_TOLERANCE = 1e-4
ADAPTER_DIAGNOSTIC_MATRIX_SCHEMA = "kronos-a-share-adapter-diagnostic-matrix-v1"
ADAPTER_DIAGNOSTIC_RECEIPT_SCHEMA = "kronos-a-share-adapter-diagnostic-receipt-v1"
PUBLIC_PIT_TABLES = (
    "security_master",
    "st_status",
    "suspensions",
    "price_limits",
    "index_membership",
    "corporate_actions",
    "trading_calendar",
    "coverage",
)
PUBLIC_PIT_SUFFIXES = {".csv", ".parquet", ".pq"}
PIT_PROVENANCE_SCHEMA = "kronos-a-share-pit-provenance-v1"
TRADING_CALENDAR_ARTIFACT_ROLE = "trading_calendar"
TRADING_CALENDAR_ARTIFACT_SCHEMA = "kronos-a-share-trading-calendar-v1"
TRADING_CALENDAR_OFFICIAL_DOMAINS = (
    "sse.com.cn",
    "szse.cn",
    "bse.cn",
    "csindex.com.cn",
)

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from kronos_a_share_data import (  # noqa: E402
    AShareDataError,
    SHANGHAI_TZ,
    assess_sample_trade_state,
    create_immutable_snapshot,
    create_inference_snapshot,
    load_snapshot_manifest,
    prepare_data_gate,
    validate_pit_bundle,
    verify_immutable_snapshot,
    verify_inference_snapshot,
)
from kronos_a_share_dataset import (  # noqa: E402
    DatasetBuildError,
    FEATURE_COLUMNS,
    SPLIT_CODES,
    WINDOW_SCHEMA,
    WindowSpec,
    build_sample_index,
    causal_adjusted_normalized_window,
    causal_adjusted_price_window,
    load_token_cache,
    load_corporate_actions,
    normalize_ticker,
    read_day_file,
    time_stamps,
    tokenize_sample_index,
)
from kronos_a_share_evaluation import (  # noqa: E402
    GateThresholds,
    daily_rank_ic,
    evaluate_gate,
    monthly_block_bootstrap_difference,
    quarterly_rank_ic_summary,
    top_quantile_return_after_cost,
)
from kronos_a_share_forward import (  # noqa: E402
    ForwardRegistryError,
    inspect_forward_registry,
    record_forward_batch,
)
from kronos_a_share_public_data import (  # noqa: E402
    PublicDataError,
    publish_normalized_pit_bundle,
)
from kronos_a_share_runtime import (  # noqa: E402
    KronosAshareRuntimeError,
    TrainingLayout,
    apply_environment_mapping,
    atomic_write_json,
    get_training_layout,
    preflight_training,
    resolve_under,
    run_directory,
    sha256_file,
    validate_identifier,
)


class CliContractError(RuntimeError):
    """The command or local artifacts violate the fixed workflow contract."""


class CliBlocked(CliContractError):
    """A safety or release gate blocked an otherwise understood command."""


CONFIG_KEYS: dict[str, Any] = {
    "schema_version": None,
    "runtime": {
        "project_root": None,
        "training_root": None,
        "kronos_runtime_root": None,
        "python_version": None,
        "device": None,
        "min_free_disk_gb": None,
        "min_free_ram_gb": None,
        "max_gpu_memory_gb": None,
        "num_workers": None,
    },
    "data": {
        "source_root": None,
        "snapshot_id": None,
        "dataset_id": None,
        "as_of": None,
        "lookback": None,
        "horizon": None,
        "purge_days": None,
        "minimum_listing_days": None,
        "universe": None,
        "price_adjustment": None,
        "public_pit": {
            "version_root": None,
            "security_master": None,
            "st_status": None,
            "suspensions": None,
            "price_limits": None,
            "index_membership": None,
            "corporate_actions": None,
            "trading_calendar": None,
            "coverage": None,
        },
        "splits": {
            "train": None,
            "validation": None,
            "development_test": None,
            "locked_retrospective": None,
        },
    },
    "model": {
        "source_revision": None,
        "model_revision": None,
        "tokenizer_revision": None,
        "model_sha256": None,
        "tokenizer_sha256": None,
        "lora": {
            "rank": None,
            "alpha": None,
            "dropout": None,
            "targets": None,
            "expected_modules": None,
            "expected_parameters": None,
        },
        "scorer": {"hidden_size": None, "expected_parameters": None},
    },
    "training": {
        "seed": None,
        "precision": None,
        "adapter": {
            "batch_size": None,
            "gradient_accumulation": None,
            "learning_rate": None,
            "weight_decay": None,
            "warmup_steps": None,
            "max_steps": None,
            "smoke_steps": None,
            "checkpoint_interval": None,
            "validation_interval": None,
            "early_stopping_patience": None,
            "gradient_clip": None,
            "validation_contract": None,
        },
        "scorer": {
            "learning_rate": None,
            "weight_decay": None,
            "max_epochs": None,
            "early_stopping_patience": None,
            "smooth_l1_weight": None,
            "ranknet_weight": None,
        },
    },
    "evaluation": {
        "adapter_ce_improvement_min": None,
        "validation_rank_ic_min": None,
        "baseline_rank_ic_lift_min": None,
        "positive_quarter_fraction_min": None,
        "bootstrap_iterations": None,
        "base_round_trip_cost_bps": None,
        "stress_round_trip_cost_bps": None,
        "forward_observation_min_days": None,
        "forward_observation_recommended_days": None,
    },
    "output": {"run_id": None, "overwrite": None},
}


@dataclass(frozen=True)
class WorkflowContext:
    config_path: Path
    config: dict[str, Any]
    config_sha256: str
    training_config_sha256: str
    layout: TrainingLayout
    dataset_id: str
    run_id: str
    dataset_dir: Path
    token_dir: Path
    run_dir: Path
    checkpoint_dir: Path
    metrics_dir: Path
    predictions_dir: Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    return _sha256_bytes(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )


def _data_config_sha256(config: Mapping[str, Any]) -> str:
    return _canonical_json_sha256(
        {
            "schema_version": "kronos-a-share-data-config-v1",
            "data": config["data"],
            "model_identity": {
                "model_sha256": config["model"]["model_sha256"],
                "tokenizer_sha256": config["model"]["tokenizer_sha256"],
            },
        }
    )


def _validated_adapter_stop_after(
    *, engineering_smoke: bool, requested: int | None, max_allowed_steps: int
) -> int:
    stop_after = int(requested or max_allowed_steps)
    if engineering_smoke and stop_after % SMOKE_CHECKPOINT_INTERVAL != 0:
        raise CliContractError(
            "engineering smoke --stop-after 必须落在50步验证/检查点边界"
        )
    if (
        not engineering_smoke
        and stop_after != max_allowed_steps
        and stop_after % FULL_CHECKPOINT_INTERVAL != 0
    ):
        raise CliContractError(
            "formal adapter --stop-after 仅允许落在 1000 步验证/恢复边界或完整 10000 步"
        )
    if stop_after < 1 or stop_after > max_allowed_steps:
        raise CliContractError(f"stop-after 必须位于 1..{max_allowed_steps}")
    return stop_after


def _validated_formal_scorer_epochs(
    *, engineering_smoke: bool, requested: int | None, configured: int
) -> int:
    if not engineering_smoke and requested is not None and int(requested) != configured:
        raise CliContractError("formal scorer 不允许用 --max-epochs 缩短固定训练合同")
    return min(int(requested or configured), configured) if engineering_smoke else configured


def _is_explicit_adapter_diagnostic(args: argparse.Namespace) -> bool:
    return bool(
        getattr(args, "engineering_smoke", False)
        and getattr(args, "learning_rate", None) is not None
        and getattr(args, "seed", None) is not None
    )


def _strict_keys(value: Any, schema: Any, path: str = "config") -> None:
    if schema is None:
        return
    if not isinstance(value, dict):
        raise CliContractError(f"{path} 必须是对象")
    missing = sorted(set(schema) - set(value))
    unknown = sorted(set(value) - set(schema))
    if missing or unknown:
        raise CliContractError(
            f"{path} 字段不匹配：missing={missing}, unknown={unknown}"
        )
    for key, child_schema in schema.items():
        _strict_keys(value[key], child_schema, f"{path}.{key}")


def _validate_splits(splits: Mapping[str, Any]) -> None:
    fixed = {
        "train": ["2018-01-02", "2022-12-30"],
        "validation": ["2023-01-03", "2024-06-28"],
        "development_test": ["2024-07-01", "2025-06-30"],
        "locked_retrospective": ["2025-07-01", "2026-07-31"],
    }
    ordered: list[tuple[pd.Timestamp, pd.Timestamp, str]] = []
    for name in (
        "train",
        "validation",
        "development_test",
        "locked_retrospective",
    ):
        interval = splits[name]
        if not isinstance(interval, list) or len(interval) != 2:
            raise CliContractError(f"data.splits.{name} 必须是 [start, end]")
        start, end = (pd.Timestamp(item) for item in interval)
        if start > end:
            raise CliContractError(f"data.splits.{name} 起止日期反向")
        if [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")] != fixed[name]:
            raise CliContractError(f"data.splits.{name} 必须使用固定时间切分")
        ordered.append((start, end, name))
    for (_, left_end, left_name), (right_start, _, right_name) in zip(
        ordered, ordered[1:]
    ):
        if left_end >= right_start:
            raise CliContractError(f"split 重叠：{left_name}/{right_name}")


def _config_absolute_path(value: Any, *, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise CliContractError(f"{field} 必须是非空绝对路径或 null")
    raw = Path(value).expanduser()
    if not raw.is_absolute():
        raise CliContractError(f"{field} 必须是绝对路径")
    return raw.resolve(strict=False)


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def _path_is_within(candidate: Path, root: Path) -> bool:
    try:
        return os.path.commonpath(
            [os.path.normcase(str(candidate)), os.path.normcase(str(root))]
        ) == os.path.normcase(str(root))
    except ValueError:
        return False


def _validate_public_pit_config(
    public_pit: Mapping[str, Any],
    *,
    training_root: Path,
) -> None:
    root_value = public_pit["version_root"]
    configured_tables = {
        name: value
        for name in PUBLIC_PIT_TABLES
        if (value := public_pit[name]) is not None
    }
    if root_value is None:
        if configured_tables:
            raise CliContractError(
                "data.public_pit.version_root 必须与单表路径同时配置"
            )
        return

    version_root = _config_absolute_path(
        root_value, field="data.public_pit.version_root"
    )
    data_root = (training_root / "data").resolve(strict=False)
    if _same_path(version_root, data_root) or not _path_is_within(
        version_root, data_root
    ):
        raise CliContractError(
            "data.public_pit.version_root 必须位于固定训练根 data 子目录内"
        )
    for table_name, value in configured_tables.items():
        path = _config_absolute_path(
            value, field=f"data.public_pit.{table_name}"
        )
        if not _same_path(path.parent, version_root):
            raise CliContractError(
                f"data.public_pit.{table_name} 必须直接位于同一 version_root"
            )
        if path.stem != table_name or path.suffix.lower() not in PUBLIC_PIT_SUFFIXES:
            raise CliContractError(
                f"data.public_pit.{table_name} 必须命名为 "
                f"{table_name}.csv/.parquet/.pq"
            )


def _validate_config(payload: dict[str, Any]) -> None:
    _strict_keys(payload, CONFIG_KEYS)
    if payload["schema_version"] != CONFIG_SCHEMA_VERSION:
        raise CliContractError(f"schema_version 必须为 {CONFIG_SCHEMA_VERSION}")
    runtime = payload["runtime"]
    if Path(runtime["project_root"]).resolve() != PROJECT_ROOT.resolve():
        raise CliContractError("path_outside_training_root: runtime.project_root 与固定项目根不一致")
    expected_training = (PROJECT_ROOT / "_training" / "kronos_ashare").resolve()
    if Path(runtime["training_root"]).resolve() != expected_training:
        raise CliContractError("path_outside_training_root: runtime.training_root 必须是项目内固定 D 盘训练根")
    expected_runtime = (PROJECT_ROOT / "_downloads" / "Kronos").resolve()
    if Path(runtime["kronos_runtime_root"]).resolve() != expected_runtime:
        raise CliContractError("path_outside_training_root: runtime.kronos_runtime_root 必须是项目内固定只读模型根")
    data = payload["data"]
    _validate_public_pit_config(
        data["public_pit"], training_root=expected_training
    )
    if (data["lookback"], data["horizon"], data["purge_days"]) != (
        LOOKBACK,
        HORIZON,
        PURGE_DAYS,
    ):
        raise CliContractError("固定窗口必须为 lookback=90,horizon=10,purge_days=11")
    if data["universe"] != "csi300+csi500":
        raise CliContractError("正式股票池必须为 csi300+csi500")
    if data["price_adjustment"] != "causal_backward_total_return":
        raise CliContractError("模型价格必须使用 causal_backward_total_return")
    if int(data["minimum_listing_days"]) != 120:
        raise CliContractError("minimum_listing_days 固定为 120")
    _validate_splits(data["splits"])
    validate_identifier(str(data["dataset_id"]), "dataset_id")
    validate_identifier(str(payload["output"]["run_id"]), "run_id")
    model = payload["model"]
    import run_kronos_forecast as base_cli

    fixed_identity = {
        "source_revision": base_cli.SOURCE_REVISION,
        "model_revision": base_cli.MODEL_REVISION,
        "tokenizer_revision": base_cli.TOKENIZER_REVISION,
        "model_sha256": base_cli.MODEL_SHA256,
        "tokenizer_sha256": base_cli.TOKENIZER_SHA256,
    }
    identity_drift = {
        key: {"expected": expected, "actual": model.get(key)}
        for key, expected in fixed_identity.items()
        if model.get(key) != expected
    }
    if identity_drift:
        raise CliContractError(f"Kronos 固定模型身份配置漂移：{identity_drift}")
    if (
        model["lora"]["rank"],
        model["lora"]["alpha"],
        model["lora"]["dropout"],
        model["lora"]["targets"],
        model["lora"]["expected_modules"],
        model["lora"]["expected_parameters"],
    ) != (8, 16, 0.05, "q_proj+v_proj", 26, 346_112):
        raise CliContractError("LoRA 合同必须为 r=8,alpha=16,dropout=0.05,26/346112")
    if (
        model["scorer"]["hidden_size"],
        model["scorer"]["expected_parameters"],
    ) != (832, 2_497):
        raise CliContractError("评分头合同必须为 hidden_size=832,parameters=2497")
    training = payload["training"]
    if training["precision"] != "fp32" or runtime["num_workers"] != 0:
        raise CliContractError("本机合同固定为 FP32、num_workers=0")
    if int(training["seed"]) != 100:
        raise CliContractError("正式训练 seed 必须固定为100")
    adapter = training["adapter"]
    if int(adapter["checkpoint_interval"]) != int(adapter["validation_interval"]):
        raise CliContractError("checkpoint_interval 必须与 validation_interval 严格对齐")
    if (
        int(adapter["batch_size"]),
        int(adapter["gradient_accumulation"]),
        int(adapter["max_steps"]),
        int(adapter["smoke_steps"]),
        int(adapter["checkpoint_interval"]),
        int(adapter["validation_interval"]),
        int(adapter["early_stopping_patience"]),
    ) != (16, 2, 10_000, SMOKE_MAX_STEPS, FULL_CHECKPOINT_INTERVAL, FULL_CHECKPOINT_INTERVAL, ADAPTER_EARLY_STOPPING_PATIENCE):
        raise CliContractError("Adapter 本机训练合同不得弱化或改写")
    if adapter["validation_contract"] != "causal-dependency-cross-attention-v1":
        raise CliContractError("Adapter validation_contract 必须锁定因果 s2 验证语义")
    scorer = training["scorer"]
    if int(scorer["max_epochs"]) != 100 or int(scorer["early_stopping_patience"]) != 10:
        raise CliContractError("Scorer 固定 max_epochs=100, early_stopping_patience=10")
    evaluation = payload["evaluation"]
    floors = {
        "adapter_ce_improvement_min": 0.01,
        "validation_rank_ic_min": 0.03,
        "baseline_rank_ic_lift_min": 0.005,
        "positive_quarter_fraction_min": 0.5,
    }
    for key, floor in floors.items():
        value = float(evaluation[key])
        if not math.isfinite(value) or value < floor:
            raise CliContractError(f"evaluation.{key} 不得低于固定准出下限 {floor}")
    if float(evaluation["positive_quarter_fraction_min"]) > 1:
        raise CliContractError("positive_quarter_fraction_min 不得大于 1")
    if int(evaluation["bootstrap_iterations"]) < 2_000:
        raise CliContractError("bootstrap_iterations 不得低于 2000")
    base_cost = Decimal(str(evaluation["base_round_trip_cost_bps"]))
    stress_cost = Decimal(str(evaluation["stress_round_trip_cost_bps"]))
    if base_cost < Decimal("35") or stress_cost < Decimal("70") or stress_cost < base_cost:
        raise CliContractError("交易成本门不得弱于 35/70 bp")
    if int(evaluation["forward_observation_min_days"]) < 60 or int(
        evaluation["forward_observation_recommended_days"]
    ) < 120:
        raise CliContractError("前瞻观察期不得短于 60/120 个交易日")
    if payload["output"]["overwrite"] is not False:
        raise CliContractError("output.overwrite 必须为 false")


def load_config(path: Path) -> tuple[dict[str, Any], str]:
    config_path = path.expanduser().resolve(strict=True)
    raw = config_path.read_bytes()
    try:
        payload = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise CliContractError(f"配置无法按 UTF-8 YAML 解析：{config_path}") from exc
    if not isinstance(payload, dict):
        raise CliContractError("配置顶层必须是对象")
    _validate_config(payload)
    return payload, _sha256_bytes(raw)


def _resolve_training_profile(
    config: Mapping[str, Any],
    *,
    base_config_sha256: str,
    profile: str | None,
    learning_rate_override: float | None = None,
    seed_override: int | None = None,
) -> tuple[dict[str, Any], str, str]:
    """Resolve immutable training values and return config/hash/run suffix."""

    if profile not in {None, "engineering_smoke", "full"}:
        raise CliContractError("training profile 仅允许 engineering_smoke/full")
    if profile != "engineering_smoke" and (
        learning_rate_override is not None or seed_override is not None
    ):
        raise CliContractError(
            "--learning-rate/--seed 仅允许与 --engineering-smoke 同时使用"
        )
    resolved = copy.deepcopy(dict(config))
    adapter = resolved["training"]["adapter"]
    if profile == "engineering_smoke":
        adapter["smoke_steps"] = SMOKE_MAX_STEPS
        adapter["checkpoint_interval"] = SMOKE_CHECKPOINT_INTERVAL
        adapter["validation_interval"] = SMOKE_CHECKPOINT_INTERVAL
        adapter["early_stopping_patience"] = ADAPTER_EARLY_STOPPING_PATIENCE
        if learning_rate_override is not None:
            value = float(learning_rate_override)
            if not math.isfinite(value) or value <= 0:
                raise CliContractError("--learning-rate 必须为有限正数")
            adapter["learning_rate"] = value
        if seed_override is not None:
            if isinstance(seed_override, bool) or int(seed_override) < 0:
                raise CliContractError("--seed 必须为非负整数")
            resolved["training"]["seed"] = int(seed_override)
    if int(adapter["checkpoint_interval"]) != int(adapter["validation_interval"]):
        raise CliContractError("checkpoint_interval 必须与 validation_interval 严格对齐")
    changed = resolved != config
    resolved_hash = (
        _canonical_json_sha256(
            {
                "schema_version": "kronos-a-share-resolved-training-v1",
                "base_config_sha256": base_config_sha256,
                "profile": profile,
                "config": resolved,
            }
        )
        if changed
        else base_config_sha256
    )
    explicit_override = learning_rate_override is not None or seed_override is not None
    suffix = f"-trial-{resolved_hash[:10]}" if explicit_override else ""
    return resolved, resolved_hash, suffix


def build_context(
    config_path: Path,
    *,
    create: bool,
    variant: str | None = None,
    training_profile: str | None = None,
    learning_rate_override: float | None = None,
    seed_override: int | None = None,
) -> WorkflowContext:
    base_config, config_hash = load_config(config_path)
    config, training_config_hash, run_suffix = _resolve_training_profile(
        base_config,
        base_config_sha256=config_hash,
        profile=training_profile,
        learning_rate_override=learning_rate_override,
        seed_override=seed_override,
    )
    layout = get_training_layout(config["runtime"]["training_root"], create=create)
    # Environment routing is a process-safety contract, independent of whether
    # this command creates artifacts. In particular, `check --load-model` must
    # never fall back to the user's C-drive TEMP or an unrelated HF cache.
    apply_environment_mapping(layout)
    if variant not in {None, "smoke"}:
        raise CliContractError("variant 仅允许 smoke 或省略")
    suffix = SMOKE_NAMESPACE_SUFFIX if variant == "smoke" else ""
    dataset_id = validate_identifier(
        f"{config['data']['dataset_id']}{suffix}", "dataset_id"
    )
    run_id = validate_identifier(
        f"{config['output']['run_id']}{suffix}{run_suffix}", "run_id"
    )
    dataset_dir = resolve_under(layout.data, Path("datasets") / dataset_id)
    token_dir = resolve_under(layout.data, Path("tokens") / dataset_id)
    run_dir = run_directory(run_id, layout, create=create)
    checkpoint_dir = resolve_under(run_dir, "checkpoints")
    metrics_dir = resolve_under(run_dir, "metrics")
    predictions_dir = resolve_under(run_dir, "predictions")
    if create:
        for path in (dataset_dir, checkpoint_dir, metrics_dir, predictions_dir):
            path.mkdir(parents=True, exist_ok=True)
    return WorkflowContext(
        config_path=config_path.resolve(),
        config=config,
        config_sha256=config_hash,
        training_config_sha256=training_config_hash,
        layout=layout,
        dataset_id=dataset_id,
        run_id=run_id,
        dataset_dir=dataset_dir,
        token_dir=token_dir,
        run_dir=run_dir,
        checkpoint_dir=checkpoint_dir,
        metrics_dir=metrics_dir,
        predictions_dir=predictions_dir,
    )


def _json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CliContractError(f"JSON 工件不可解析：{path}") from exc
    if not isinstance(payload, dict):
        raise CliContractError(f"JSON 工件顶层不是对象：{path}")
    return payload


def _snapshot_directory(context: WorkflowContext) -> Path:
    return resolve_under(
        context.layout.data,
        Path("raw") / context.config["data"]["snapshot_id"],
    )


def _snapshot_manifest_path(context: WorkflowContext) -> Path:
    return _snapshot_directory(context) / "source_manifest.json"


def _data_report_path(context: WorkflowContext) -> Path:
    return context.dataset_dir / "data_quality_report.json"


def _pit_root(context: WorkflowContext, override: Path | None = None) -> Path:
    public_pit = context.config["data"]["public_pit"]
    configured_root = (
        _config_absolute_path(
            public_pit["version_root"], field="data.public_pit.version_root"
        )
        if public_pit["version_root"] is not None
        else None
    )
    if override is not None:
        selected = override.expanduser().resolve(strict=False)
        if configured_root is not None and not _same_path(selected, configured_root):
            raise CliContractError(
                "--pit-root 与 data.public_pit.version_root 不一致"
            )
    elif configured_root is not None:
        selected = configured_root
    else:
        selected = resolve_under(context.layout.data, Path("normalized") / "pit")
    if not _path_is_within(selected, context.layout.data) or _same_path(
        selected, context.layout.data
    ):
        raise CliContractError("PIT version_root 必须位于训练 data 子目录内")
    for table_name in PUBLIC_PIT_TABLES:
        configured_path = public_pit[table_name]
        if configured_path is None:
            continue
        path = _config_absolute_path(
            configured_path, field=f"data.public_pit.{table_name}"
        )
        if not _same_path(path.parent, selected):
            raise CliContractError(
                f"data.public_pit.{table_name} 与 PIT version_root 不一致"
            )
        if not path.is_file():
            raise CliContractError(
                f"已配置的 PIT 文件不存在：{table_name}={path}"
            )
    return selected


def _membership_path(context: WorkflowContext, pit_root: Path) -> Path | None:
    value = context.config["data"]["public_pit"].get("index_membership")
    if value:
        return Path(value).expanduser().resolve()
    for suffix in (".parquet", ".pq", ".csv"):
        candidate = pit_root / f"index_membership{suffix}"
        if candidate.is_file():
            return candidate.resolve()
    return None


def _pit_table_path(pit_root: Path, name: str) -> Path | None:
    for suffix in (".parquet", ".pq", ".csv"):
        candidate = pit_root / f"{name}{suffix}"
        if candidate.is_file():
            return candidate.resolve()
    return None


def _pit_inventory(pit_root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    if not pit_root.is_dir():
        return files
    root = pit_root.resolve()
    for path in sorted(
        (value for value in pit_root.rglob("*") if value.is_file()),
        key=lambda value: value.relative_to(pit_root).as_posix().casefold(),
    ):
        resolved = path.resolve()
        if not _path_is_within(resolved, root):
            raise CliContractError(f"path_outside_training_root: PIT evidence={resolved}")
        files.append(
            {
                "name": path.relative_to(pit_root).as_posix(),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def _expected_prepare_contract(
    context: WorkflowContext,
    *,
    pit_root: Path,
    data_status: str,
    max_samples_per_split: int | None,
) -> dict[str, Any]:
    snapshot_manifest = _snapshot_manifest_path(context)
    data_report = _data_report_path(context)
    return {
        "schema_version": "kronos-a-share-prepare-contract-v1",
        "dataset_id": context.dataset_id,
        "config_sha256": _data_config_sha256(context.config),
        "snapshot_id": context.config["data"]["snapshot_id"],
        "snapshot_manifest_sha256": sha256_file(snapshot_manifest),
        "pit_root": str(pit_root.resolve()),
        "pit_inventory": _pit_inventory(pit_root),
        "data_status": data_status,
        "data_quality_report_sha256": sha256_file(data_report),
        "max_samples_per_split": max_samples_per_split,
        "window": {
            "lookback": LOOKBACK,
            "horizon": HORIZON,
            "purge_days": PURGE_DAYS,
        },
    }


def _has_verified_survivorship_audit(sample_manifest: Mapping[str, Any]) -> bool:
    audit = sample_manifest.get("survivorship_bias_audit")
    if not isinstance(audit, Mapping):
        return False
    required_zero_counts = (
        "missing_historical_day_file_count",
        "missing_suspension_state_member_dates",
        "unexplained_missing_quote_member_dates",
    )
    try:
        return (
            audit.get("schema_version")
            == "kronos-a-share-survivorship-audit-v1"
            and audit.get("verified") is True
            and int(audit.get("checked_member_dates", 0)) >= 1
            and all(int(audit.get(key, -1)) == 0 for key in required_zero_counts)
        )
    except (TypeError, ValueError):
        return False


def _validate_prepared_index(
    context: WorkflowContext,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    contract_path = context.dataset_dir / "prepare_contract.json"
    sample_manifest_path = context.dataset_dir / "sample_manifest.json"
    sample_index_path = context.dataset_dir / "sample_index.csv"
    if not all(path.is_file() for path in (contract_path, sample_manifest_path, sample_index_path)):
        raise CliBlocked("prepare 工件不完整；请使用新的 dataset_id 重建")
    contract = _json_file(contract_path)
    for key, value in expected.items():
        if contract.get(key) != value:
            raise CliBlocked(f"prepare 合同漂移：{key}；拒绝复用旧样本")
    sample_manifest = _json_file(sample_manifest_path)
    if (
        expected.get("data_status") == "production_ready"
        and sample_manifest.get("sample_trade_state_checked") is not True
    ):
        raise CliBlocked("production 样本未逐证券消费 PIT 交易状态审计")
    if expected.get("data_status") == "production_ready":
        if sample_manifest.get("schema_version") != WINDOW_SCHEMA:
            raise CliBlocked(
                "production 样本索引不是当前 PIT 分层样本合同；请使用新的 dataset_id 重建"
            )
        try:
            index_columns = set(pd.read_csv(sample_index_path, nrows=0).columns)
        except (OSError, ValueError, pd.errors.ParserError) as exc:
            raise CliBlocked("production sample_index.csv 无法读取") from exc
        if "active_member_count" not in index_columns:
            raise CliBlocked(
                "production 样本索引缺少 active_member_count；请使用新的 dataset_id 重建"
            )
        if not _has_verified_survivorship_audit(sample_manifest):
            raise CliBlocked(
                "production 样本未通过历史成分行情覆盖/幸存者偏差审计"
            )
    if sample_manifest.get("sample_index_sha256") != sha256_file(sample_index_path):
        raise CliBlocked("sample_index.csv 哈希与 manifest 不一致")
    if contract.get("sample_manifest_sha256") != sha256_file(sample_manifest_path):
        raise CliBlocked("sample_manifest.json 哈希漂移")
    return sample_manifest


def _verify_token_cache(context: WorkflowContext) -> dict[str, Any]:
    manifest_path = context.token_dir / "manifest.json"
    if not manifest_path.is_file():
        raise CliBlocked("token cache 缺少 manifest.json")
    manifest = _json_file(manifest_path)
    if manifest.get("tokenizer_sha256") != context.config["model"]["tokenizer_sha256"]:
        raise CliBlocked("token cache Tokenizer 哈希漂移")
    report_path = context.dataset_dir / "data_quality_report.json"
    if report_path.is_file() and _json_file(report_path).get("status") == "production_ready":
        adjustment = manifest.get("adjustment")
        required_adjustment = {
            "mode": "causal_backward_total_return",
            "materialized": True,
            "trade_price_raw": True,
            "model_price_adjusted": True,
            "cutoff_field": "origin_date",
            "future_action_use_count": 0,
        }
        if not isinstance(adjustment, dict) or any(
            adjustment.get(key) != value for key, value in required_adjustment.items()
        ):
            raise CliBlocked("production token cache 未通过因果复权合同")
    sample_index = context.dataset_dir / "sample_index.csv"
    if not sample_index.is_file() or manifest.get("sample_index_sha256") != sha256_file(
        sample_index
    ):
        raise CliBlocked("token cache 与 sample_index 哈希不一致")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise CliBlocked("token cache manifest.files 不完整")
    if (
        report_path.is_file()
        and _json_file(report_path).get("status") == "production_ready"
        and "active_member_count.npy" not in files
    ):
        raise CliBlocked("production token cache 缺少 active_member_count.npy")
    for name, metadata in files.items():
        path = resolve_under(context.token_dir, name)
        if (
            not path.is_file()
            or path.stat().st_size != metadata.get("bytes")
            or sha256_file(path) != metadata.get("sha256")
        ):
            raise CliBlocked(f"token cache 文件哈希失败：{name}")
    return manifest


def _load_data_status(context: WorkflowContext) -> dict[str, Any]:
    path = _data_report_path(context)
    if not path.is_file():
        return {
            "status": "blocked",
            "blocking_issues": ["missing_data_quality_report"],
            "provisional_issues": [],
        }
    report = _json_file(path)
    if report.get("status") not in {
        "production_ready",
        "local_provisional",
        "blocked",
    }:
        raise CliContractError("data_quality_report.status 非法")
    return report


def _assert_data_allowed(data_status: str, *, engineering_smoke: bool) -> None:
    if data_status == "blocked":
        raise CliBlocked("数据门为 blocked，禁止训练或评分")
    if data_status != "production_ready" and not engineering_smoke:
        raise CliBlocked("正式训练只接受 production_ready；请先补齐 PIT 数据")


def _dataset_hash(context: WorkflowContext) -> str:
    contract_path = context.dataset_dir / "prepare_contract.json"
    report_path = context.dataset_dir / "data_quality_report.json"
    if not contract_path.is_file() or not report_path.is_file():
        raise CliBlocked("缺少 prepare/data quality 绑定工件")
    contract = _json_file(contract_path)
    report = _json_file(report_path)
    pit_root = Path(str(contract.get("pit_root", ""))).resolve()
    if report.get("status") == "production_ready":
        resolve_under(context.layout.root, pit_root, allow_root=False)
    expected = _expected_prepare_contract(
        context,
        pit_root=pit_root,
        data_status=str(report.get("status")),
        max_samples_per_split=contract.get("max_samples_per_split"),
    )
    _validate_prepared_index(context, expected)
    _verify_token_cache(context)
    paths = {
        "token_manifest": context.token_dir / "manifest.json",
        "prepare_contract": context.dataset_dir / "prepare_contract.json",
        "sample_manifest": context.dataset_dir / "sample_manifest.json",
        "data_quality_report": context.dataset_dir / "data_quality_report.json",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise CliBlocked(f"数据绑定工件缺失：{missing}")
    payload = {
        "schema_version": "kronos-a-share-data-binding-v1",
        "dataset_id": context.dataset_id,
        "files": {name: sha256_file(path) for name, path in paths.items()},
    }
    return _sha256_bytes(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    )


def _binding(context: WorkflowContext):
    from kronos_a_share_training import CheckpointBinding

    return CheckpointBinding(
        base_model_sha256=context.config["model"]["model_sha256"],
        tokenizer_sha256=context.config["model"]["tokenizer_sha256"],
        config_sha256=context.training_config_sha256,
        dataset_sha256=_dataset_hash(context),
    )


def _envelope(
    command: str,
    *,
    status: str,
    message: str,
    **payload: Any,
) -> dict[str, Any]:
    return {
        "schema_version": CLI_SCHEMA_VERSION,
        "command": command,
        "status": status,
        "message": message,
        "generated_at": _utc_now(),
        **payload,
    }


def _load_kronos_components(context: WorkflowContext, requested_device: str):
    import run_kronos_forecast as base_cli

    runtime_root = Path(context.config["runtime"]["kronos_runtime_root"]).resolve()
    runtime_report = base_cli.validate_runtime(runtime_root)
    for field in (
        "source_revision",
        "model_revision",
        "tokenizer_revision",
        "model_sha256",
        "tokenizer_sha256",
    ):
        if runtime_report.get(field) != context.config["model"].get(field):
            raise CliBlocked(
                f"实际 Kronos runtime 与配置身份不一致：{field}"
            )
    device, warnings, cuda_report = base_cli.resolve_device(requested_device)
    paths = base_cli.runtime_paths(runtime_root)
    os.environ["HF_HUB_OFFLINE"] = "1"
    if str(paths["source"]) not in sys.path:
        sys.path.insert(0, str(paths["source"]))
    from model import Kronos, KronosTokenizer

    tokenizer = KronosTokenizer.from_pretrained(paths["tokenizer"])
    model = Kronos.from_pretrained(paths["model"])
    tokenizer.to(device).eval()
    model.to(device).eval()
    return SimpleNamespace(
        model=model,
        tokenizer=tokenizer,
        device=device,
        runtime_report=runtime_report,
        warnings=warnings,
        cuda=cuda_report,
    )


def command_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    context = build_context(
        args.config, create=True, variant=getattr(args, "_variant", None)
    )
    inference_as_of = getattr(args, "inference_as_of", None)
    inference_pit_root = getattr(args, "inference_pit_root", None)
    if inference_as_of is not None:
        if inference_pit_root is None:
            raise CliContractError(
                "--inference-as-of 必须同时提供 --inference-pit-root"
            )
        manifest = create_inference_snapshot(
            context.config["data"]["source_root"],
            inference_pit_root,
            context.layout.root,
            as_of=inference_as_of,
            dry_run=bool(args.dry_run),
            project_root=PROJECT_ROOT,
        )
        reused = bool(manifest.pop("reused", False))
        return _envelope(
            "snapshot",
            status="ok" if not manifest.get("dry_run") else "unverified",
            message=(
                "当日 inference 不可变快照已复用。"
                if reused
                else "当日 inference 行情与7表PIT快照校验完成。"
            ),
            snapshot=manifest,
            reused=reused,
            inference_mode=True,
            evidence_class="market_data_vendor+public_pit",
        )
    if inference_pit_root is not None:
        raise CliContractError(
            "--inference-pit-root 仅能与 --inference-as-of 同时使用"
        )
    manifest_path = _snapshot_manifest_path(context)
    if manifest_path.exists() and args.reuse:
        manifest = verify_immutable_snapshot(
            manifest_path,
            training_root=context.layout.root,
            project_root=PROJECT_ROOT,
        )
        reused = True
    else:
        manifest = create_immutable_snapshot(
            context.config["data"]["source_root"],
            context.layout.data,
            snapshot_id=context.config["data"]["snapshot_id"],
            dry_run=args.dry_run,
            project_root=PROJECT_ROOT,
        )
        reused = False
    return _envelope(
        "snapshot",
        status="ok" if not manifest.get("dry_run") else "unverified",
        message="TDX 不可变快照已复用。" if reused else "TDX 快照校验完成。",
        snapshot=manifest,
        reused=reused,
        evidence_class="market_data_vendor",
    )


def _prepare_index(
    context: WorkflowContext,
    *,
    pit_root: Path,
    max_samples_per_split: int | None,
    force: bool,
) -> dict[str, Any]:
    manifest_path = context.dataset_dir / "sample_manifest.json"
    pit_validation = validate_pit_bundle(pit_root)
    if manifest_path.is_file():
        if force:
            raise CliBlocked("样本索引是哈希绑定工件；请使用新的 dataset_id 重建")
        existing = _json_file(manifest_path)
        if (
            pit_validation.production_ready
            and existing.get("schema_version") != WINDOW_SCHEMA
        ):
            raise CliBlocked(
                "旧样本不是当前 PIT 分层样本合同；请使用新的 dataset_id 重建"
            )
        if (
            pit_validation.production_ready
            and not _has_verified_survivorship_audit(existing)
        ):
            raise CliBlocked(
                "旧样本缺少幸存者偏差审计；请使用新的 dataset_id 重建"
            )
        return existing
    trade_state_checker = None
    if pit_validation.production_ready:
        def trade_state_checker(
            ticker: str,
            signal_date: pd.Timestamp,
            raw_close: float,
            previous_raw_close: float,
        ) -> Mapping[str, Any]:
            external_ticker = f"{ticker[2:]}.{ticker[:2].upper()}"
            return assess_sample_trade_state(
                pit_validation,
                external_ticker,
                signal_date,
                trade_price_raw=raw_close,
                previous_close_raw=previous_raw_close,
                minimum_listing_days=int(
                    context.config["data"]["minimum_listing_days"]
                ),
            )

    try:
        return build_sample_index(
            _snapshot_directory(context),
            context.dataset_dir,
            context.layout.root,
            splits=context.config["data"]["splits"],
            membership_path=_membership_path(context, pit_root),
            suspensions_path=_pit_table_path(pit_root, "suspensions"),
            corporate_actions_path=_pit_table_path(pit_root, "corporate_actions"),
            benchmark_ticker="sh000906",
            spec=WindowSpec(lookback=LOOKBACK, horizon=HORIZON, purge_days=PURGE_DAYS),
            max_samples_per_split=max_samples_per_split,
            seed=int(context.config["training"]["seed"]),
            trade_state_checker=trade_state_checker,
            require_complete_membership_coverage=pit_validation.production_ready,
        )
    except DatasetBuildError as exc:
        if pit_validation.production_ready:
            raise CliBlocked(f"幸存者偏差准出阻断：{exc}") from exc
        raise


def _prepare_tokens(
    context: WorkflowContext,
    *,
    device: str,
    force: bool,
    pit_root: Path,
) -> dict[str, Any]:
    if context.token_dir.exists():
        if not force:
            return _verify_token_cache(context)
        raise CliContractError("token cache 是不可变工件；请使用新的 dataset_id，不能 --force 覆盖")
    components = _load_kronos_components(context, device)
    return tokenize_sample_index(
        context.dataset_dir / "sample_index.csv",
        context.token_dir,
        context.layout.root,
        tokenizer=components.tokenizer,
        tokenizer_sha256=context.config["model"]["tokenizer_sha256"],
        corporate_actions_path=_pit_table_path(pit_root, "corporate_actions"),
        device=components.device,
        batch_size=64,
        spec=WindowSpec(lookback=LOOKBACK, horizon=HORIZON, purge_days=PURGE_DAYS),
    )


def command_prepare(args: argparse.Namespace) -> dict[str, Any]:
    context = build_context(
        args.config, create=True, variant=getattr(args, "_variant", None)
    )
    snapshot_manifest = _snapshot_manifest_path(context)
    if not snapshot_manifest.is_file():
        raise CliBlocked("缺少实际不可变快照；请先运行 snapshot（非 --dry-run）")
    # `prepare` is also a public entry point, so it must independently re-hash
    # every immutable snapshot file instead of trusting manifest existence.
    verify_immutable_snapshot(
        snapshot_manifest,
        training_root=context.layout.root,
        project_root=PROJECT_ROOT,
    )
    pit_root = _pit_root(context, args.pit_root)
    normalization_manifest = getattr(args, "pit_normalization_manifest", None)
    normalization_report = None
    if normalization_manifest is not None:
        try:
            normalization_report = publish_normalized_pit_bundle(
                normalization_manifest,
                pit_root,
                context.layout.root,
            )
        except PublicDataError as exc:
            raise CliBlocked(f"PIT 原始响应归一化发布失败：{exc}") from exc
    contract_path = context.dataset_dir / "prepare_contract.json"
    report_path = _data_report_path(context)
    sample_preexisting = (context.dataset_dir / "sample_manifest.json").is_file()
    if sample_preexisting and not contract_path.is_file():
        raise CliBlocked("发现无 prepare_contract 的旧样本；请使用新的 dataset_id 重建")
    if contract_path.is_file() and report_path.is_file():
        report = _json_file(report_path)
        if report.get("status") == "blocked":
            raise CliBlocked("已有 data_quality_report 为 blocked")
        expected = _expected_prepare_contract(
            context,
            pit_root=pit_root,
            data_status=report["status"],
            max_samples_per_split=args.max_samples_per_split,
        )
        _validate_prepared_index(context, expected)
    else:
        report = prepare_data_gate(
            snapshot_manifest,
            pit_root,
            output_path=report_path,
            training_root=context.layout.root,
            project_root=PROJECT_ROOT,
        )
        if report["status"] == "blocked":
            raise CliBlocked("快照或 PIT 合同无效，prepare 已停止")
    sample_manifest = _prepare_index(
        context,
        pit_root=pit_root,
        max_samples_per_split=args.max_samples_per_split,
        force=args.force,
    )
    token_manifest = None
    if args.tokenize:
        token_existed = context.token_dir.is_dir()
        token_manifest = _prepare_tokens(
            context,
            device=args.device,
            force=args.force,
            pit_root=pit_root,
        )
        if not token_existed:
            adjustment = token_manifest.get("adjustment", {})
            adjustment_artifact = (
                context.token_dir / "manifest.json"
                if adjustment.get("materialized") is True
                else None
            )
            report = prepare_data_gate(
                snapshot_manifest,
                pit_root,
                output_path=report_path,
                training_root=context.layout.root,
                project_root=PROJECT_ROOT,
                model_adjustment_manifest=adjustment_artifact,
            )
            if report["status"] == "blocked":
                raise CliBlocked("因果复权 token manifest 未通过数据门")
    expected = _expected_prepare_contract(
        context,
        pit_root=pit_root,
        data_status=report["status"],
        max_samples_per_split=args.max_samples_per_split,
    )
    expected.update(
        {
            "sample_manifest_sha256": sha256_file(
                context.dataset_dir / "sample_manifest.json"
            ),
            "sample_index_sha256": sha256_file(
                context.dataset_dir / "sample_index.csv"
            ),
            "token_manifest_sha256": (
                sha256_file(context.token_dir / "manifest.json")
                if context.token_dir.is_dir()
                else None
            ),
        }
    )
    if contract_path.is_file():
        existing = _json_file(contract_path)
        if existing != expected:
            if token_manifest is None or token_existed:
                raise CliBlocked("prepare 合同漂移；拒绝复用或覆盖旧数据集")
            atomic_write_json(contract_path, expected, allowed_root=context.layout.root)
    else:
        atomic_write_json(contract_path, expected, allowed_root=context.layout.root)
    return _envelope(
        "prepare",
        status="ok" if report["status"] == "production_ready" else "unverified",
        message=(
            "A股 PIT 数据集已达到 production_ready。"
            if report["status"] == "production_ready"
            else "工程数据集已生成，但 PIT 数据门仍为 local_provisional。"
        ),
        data_status=report["status"],
        data_quality_report=str(_data_report_path(context)),
        sample_manifest=sample_manifest,
        token_manifest=token_manifest,
        pit_normalization=normalization_report,
        evidence_class="market_data_vendor",
    )


def command_check(args: argparse.Namespace) -> dict[str, Any]:
    context = build_context(
        args.config, create=False, variant=getattr(args, "_variant", None)
    )
    runtime = context.config["runtime"]
    report = preflight_training(
        context.layout.root,
        min_disk_free_gib=float(runtime["min_free_disk_gb"]),
        min_ram_available_gib=float(runtime["min_free_ram_gb"]),
        require_cuda=args.device != "cpu",
        min_cuda_vram_gib=3.0,
    )
    import run_kronos_forecast as base_cli

    runtime_report = base_cli.validate_runtime(
        Path(runtime["kronos_runtime_root"]).resolve()
    )
    model_load = "not_requested"
    device_report: dict[str, Any] | None = None
    if args.load_model:
        components = _load_kronos_components(context, args.device)
        model_load = "ok"
        device_report = {
            "device": components.device,
            "cuda": components.cuda,
            "warnings": components.warnings,
        }
    data_report = _load_data_status(context)
    status = "ok" if report["status"] == "ok" else "blocked"
    return _envelope(
        "check",
        status=status,
        message="Kronos A股运行环境检查完成。",
        preflight=report,
        runtime=runtime_report,
        model_load=model_load,
        device=device_report,
        data_status=data_report["status"],
        evidence_class="model_output_runtime_check",
    )


def _load_cache(context: WorkflowContext) -> dict[str, Any]:
    if not context.token_dir.is_dir():
        raise CliBlocked("缺少 token cache；请先运行 prepare --tokenize")
    return load_token_cache(context.token_dir)


def _adapter_batch(arrays: Mapping[str, Any], indices: np.ndarray, device: str):
    import torch
    from kronos_a_share_model import build_future_mask
    from kronos_a_share_training import AdapterBatch

    s1_full = torch.as_tensor(np.asarray(arrays["s1"][indices]), device=device).long()
    s2_full = torch.as_tensor(np.asarray(arrays["s2"][indices]), device=device).long()
    stamp = torch.as_tensor(np.asarray(arrays["stamp"][indices, :-1]), device=device).long()
    sequence_length = s1_full.shape[1] - 1
    mask = build_future_mask(
        sequence_length,
        history_length=LOOKBACK - 1,
        future_length=HORIZON,
        batch_size=len(indices),
        device=device,
    )
    return AdapterBatch(
        s1_ids=s1_full[:, :-1],
        s2_ids=s2_full[:, :-1],
        s1_targets=s1_full[:, 1:],
        s2_targets=s2_full[:, 1:],
        future_mask=mask,
        stamp=stamp,
    )


def _deterministic_batch(
    members: np.ndarray,
    *,
    microstep: int,
    batch_size: int,
    seed: int,
) -> np.ndarray:
    if len(members) == 0:
        raise CliContractError("训练 split 没有样本")
    start = microstep * batch_size
    result: list[int] = []
    while len(result) < batch_size:
        epoch, offset = divmod(start, len(members))
        order = np.random.default_rng(seed + epoch).permutation(members)
        take = min(batch_size - len(result), len(members) - offset)
        result.extend(int(value) for value in order[offset : offset + take])
        start += take
    return np.asarray(result, dtype=np.int64)


def _validation_adapter_ce(
    model: Any,
    arrays: Mapping[str, Any],
    members: np.ndarray,
    *,
    batch_size: int,
    device: str,
) -> float:
    import torch
    from kronos_a_share_training import adapter_forward_loss

    total = 0.0
    count = 0
    with _causal_validation_mode(model), torch.no_grad():
        for start in range(0, len(members), batch_size):
            indices = members[start : start + batch_size]
            loss, _ = adapter_forward_loss(model, _adapter_batch(arrays, indices, device))
            total += float(loss.detach().cpu()) * len(indices)
            count += len(indices)
    if count == 0:
        raise CliContractError("validation split 没有样本")
    return total / count


@contextmanager
def _causal_validation_mode(model: Any):
    """Evaluate deterministically while preserving Kronos s2 causal attention.

    Upstream Kronos binds dependency cross-attention causality to that module's
    ``training`` flag.  Calling ``model.eval()`` alone therefore leaks later s1
    targets into earlier s2 logits.  Set only the parent flag directly so LoRA
    dropout children remain in evaluation mode.
    """

    module_states = [(module, bool(module.training)) for module in model.modules()]
    model.eval()
    dependency_layer = getattr(model, "dep_layer", None)
    cross_attention = getattr(dependency_layer, "cross_attn", None)
    if cross_attention is None:
        for module, training in module_states:
            module.training = training
        raise CliContractError("Kronos dep_layer.cross_attn 不存在，无法保证验证因果性")
    cross_attention.training = True
    try:
        yield
    finally:
        for module, training in module_states:
            module.training = training


def _resume_reference(store: Any, requested: str, stage: str) -> str | None:
    if requested == "none":
        return None
    if requested == "auto":
        try:
            return _stage_reference(store, stage=stage, kind="latest")
        except FileNotFoundError:
            return None
    reference = requested
    try:
        manifest = store.inspect(reference)
    except FileNotFoundError:
        if requested == "auto":
            return None
        raise
    if manifest["stage"] != stage:
        if requested == "auto":
            return None
        raise CliContractError(f"checkpoint {reference} 不是 {stage} 阶段")
    return reference


def _stage_manifests(store: Any, stage: str) -> list[dict[str, Any]]:
    recovery = store.recover()
    manifests = []
    for name in recovery["valid"]:
        manifest = store.inspect(name)
        if manifest["stage"] == stage:
            manifests.append(manifest)
    manifests.sort(key=lambda value: (int(value["created_at_ns"]), int(value["step"])))
    return manifests


def _stage_reference(store: Any, *, stage: str, kind: str) -> str:
    if kind not in {"latest", "best"}:
        manifest = store.inspect(kind)
        if manifest["stage"] != stage:
            raise CliContractError(f"checkpoint {kind} 不是 {stage} 阶段")
        return manifest["checkpoint_name"]
    manifests = _stage_manifests(store, stage)
    if kind == "best":
        manifests = [
            item
            for item in manifests
            if item.get("is_best") is True
            and item.get("metric") is not None
            and math.isfinite(float(item["metric"]))
        ]
    if not manifests:
        raise FileNotFoundError(f"不存在 {stage} {kind} checkpoint")
    return manifests[-1]["checkpoint_name"]


def _checkpoint_state(store: Any, reference: str) -> dict[str, Any]:
    import torch

    manifest = store.inspect(reference)
    state_path = store.root / manifest["checkpoint_name"] / "state.pt"
    try:
        state = torch.load(state_path, map_location="cpu", weights_only=True)
    except TypeError:  # pragma: no cover - PyTorch <2.6
        state = torch.load(state_path, map_location="cpu")
    if not isinstance(state, dict):
        raise CliContractError("checkpoint state.pt 内容无效")
    return state


def _checkpoint_extra_state(store: Any, reference: str) -> dict[str, Any]:
    state = _checkpoint_state(store, reference)
    if not isinstance(state.get("extra_state"), dict):
        raise CliContractError("checkpoint extra_state 不完整")
    return dict(state["extra_state"])


def _checkpoint_lora_state_sha256(store: Any, reference: str) -> str:
    from kronos_a_share_training import canonical_lora_state_sha256

    state = _checkpoint_state(store, reference)
    lora_state = state.get("lora_state")
    if not isinstance(lora_state, Mapping):
        raise CliContractError("checkpoint lora_state 不完整")
    return canonical_lora_state_sha256(lora_state)


def _scorer_checkpoint_hashes(
    store: Any, scorer_manifest: Mapping[str, Any]
) -> tuple[str, str, str]:
    """Return adapter reference/hash and scorer-state hash without conflating them."""

    if scorer_manifest.get("stage") != "scorer":
        raise CliContractError("评估 checkpoint 必须属于 scorer 阶段")
    scorer_reference = str(scorer_manifest.get("checkpoint_name", ""))
    extra_state = _checkpoint_extra_state(store, scorer_reference)
    if extra_state.get("engineering_smoke") is not False:
        raise CliContractError("engineering_smoke scorer checkpoint 不得进入 formal gate")
    adapter_reference = str(extra_state.get("adapter_checkpoint", ""))
    if not adapter_reference:
        raise CliContractError("scorer checkpoint 未绑定 adapter_checkpoint")
    adapter_manifest = store.inspect(adapter_reference)
    if adapter_manifest.get("stage") != "adapter":
        raise CliContractError("scorer checkpoint 绑定的不是 adapter checkpoint")
    adapter_hash = str(
        adapter_manifest.get("files", {}).get("state.pt", {}).get("sha256", "")
    )
    scorer_hash = str(
        scorer_manifest.get("files", {}).get("state.pt", {}).get("sha256", "")
    )
    for field, value in (
        ("adapter_hash", adapter_hash),
        ("scorer_checkpoint_hash", scorer_hash),
    ):
        if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
            raise CliContractError(f"{field} 不是有效 SHA256")
    declared = extra_state.get("adapter_hash")
    if declared is not None and declared != adapter_hash:
        raise CliContractError("scorer checkpoint 声明的 adapter_hash 与 adapter 工件不一致")
    scorer_lora_hash = _checkpoint_lora_state_sha256(store, scorer_reference)
    adapter_lora_hash = _checkpoint_lora_state_sha256(store, adapter_reference)
    if scorer_lora_hash != adapter_lora_hash:
        raise CliContractError(
            "scorer checkpoint 内 LoRA 张量与声明绑定的 adapter checkpoint 不一致"
        )
    return adapter_reference, adapter_hash, scorer_hash


def _scorer_stability_evidence(
    context: WorkflowContext,
    *,
    checkpoint_reference: str,
    scorer_checkpoint_hash: str,
) -> dict[str, Any]:
    path = context.metrics_dir / "scorer_summary.json"
    if not path.is_file():
        raise CliContractError("formal gate 缺少 scorer_summary.json")
    summary = _json_file(path)
    evidence = summary.get("scorer_seed_stability")
    if (
        summary.get("status") != "ok"
        or summary.get("evaluated_checkpoint") != checkpoint_reference
        or summary.get("scorer_checkpoint_hash") != scorer_checkpoint_hash
        or not isinstance(evidence, Mapping)
        or evidence.get("seeds") != list(FORMAL_SCORER_SEEDS)
        or evidence.get("production_seed") != 100
        or evidence.get("selection_policy")
        != "seed100_checkpoint_fixed_no_seed_selection"
        or evidence.get("schema_version")
        != "kronos-a-share-scorer-seed-stability-v2"
        or evidence.get("binding") != _gate_binding(_binding(context))
        or evidence.get("evaluated_checkpoint") != checkpoint_reference
        or evidence.get("scorer_checkpoint_hash") != scorer_checkpoint_hash
        or evidence.get("training_max_epochs")
        != int(context.config["training"]["scorer"]["max_epochs"])
        or evidence.get("early_stopping_patience")
        != int(context.config["training"]["scorer"]["early_stopping_patience"])
        or not isinstance(evidence.get("per_seed"), list)
        or len(evidence["per_seed"]) != len(FORMAL_SCORER_SEEDS)
        or summary.get("scorer_seed_stability_sha256")
        != _canonical_json_sha256(evidence)
    ):
        raise CliContractError("formal gate scorer 20-seed stability 证据不完整")
    observed_seeds = [int(item.get("seed", -1)) for item in evidence["per_seed"]]
    values = np.asarray(
        [item.get("best_validation_rank_ic") for item in evidence["per_seed"]],
        dtype=np.float64,
    )
    published = [
        int(item["seed"])
        for item in evidence["per_seed"]
        if item.get("published_checkpoint") is True
    ]
    arrays = _load_cache(context)["arrays"]
    expected_ids = _members_for_split(arrays, "validation")
    expected_sample_hash = _sha256_bytes(expected_ids.tobytes())
    observed_artifacts: list[dict[str, Any]] = []
    prediction_columns = ["sample_id", "raw_score"]
    for item in evidence["per_seed"]:
        if not isinstance(item, Mapping):
            raise CliContractError("formal gate scorer per-seed 证据格式无效")
        try:
            path = resolve_under(
                context.layout.root,
                Path(str(item.get("prediction_path", ""))).resolve(strict=True),
            )
        except (OSError, RuntimeError, ValueError) as exc:
            raise CliContractError("formal gate scorer per-seed prediction 路径无效") from exc
        frame = pd.read_csv(path)
        if list(frame.columns) != prediction_columns:
            raise CliContractError("formal gate scorer per-seed prediction 列合同无效")
        ids = pd.to_numeric(frame["sample_id"], errors="raise").to_numpy(dtype=np.int64)
        scores = pd.to_numeric(frame["raw_score"], errors="coerce").to_numpy(dtype=float)
        if (
            not np.array_equal(ids, expected_ids)
            or not np.isfinite(scores).all()
            or item.get("row_count") != len(expected_ids)
            or item.get("sample_id_sha256") != expected_sample_hash
            or item.get("prediction_sha256") != sha256_file(path)
        ):
            raise CliContractError("formal gate scorer per-seed prediction/hash 未绑定 validation 全样本")
        reconstructed = pd.DataFrame(
            {
                "sample_id": ids,
                "trade_date": pd.to_datetime(
                    np.asarray(arrays["trade_date"])[ids].astype(str),
                    format="%Y%m%d",
                ).strftime("%Y-%m-%d"),
                "instrument_id": np.asarray(arrays["instrument_id"])[ids],
                "active_member_count": np.asarray(arrays["active_member_count"])[ids],
                "raw_score": scores,
                "label_excess_10d": np.asarray(arrays["label"])[ids],
            }
        )
        live_rank_ic = _mean_rank_ic(reconstructed, formal_cross_section=True)
        if not math.isclose(
            live_rank_ic,
            float(item.get("best_validation_rank_ic", math.nan)),
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise CliContractError("formal gate scorer per-seed RankIC 与预测工件不一致")
        observed_artifacts.append(
            {
                "seed": int(item["seed"]),
                "prediction_sha256": item["prediction_sha256"],
                "sample_id_sha256": item["sample_id_sha256"],
                "row_count": item["row_count"],
                "best_validation_rank_ic": item["best_validation_rank_ic"],
                "best_epoch": item["best_epoch"],
                "completed_epoch": item["completed_epoch"],
                "published_checkpoint": item["published_checkpoint"],
            }
        )
    if (
        observed_seeds != list(FORMAL_SCORER_SEEDS)
        or not np.isfinite(values).all()
        or published != [100]
        or not math.isclose(
            float(evidence.get("rank_ic_mean", math.nan)),
            float(values.mean()),
            rel_tol=0,
            abs_tol=1e-12,
        )
        or not math.isclose(
            float(evidence.get("rank_ic_std", math.nan)),
            float(values.std(ddof=1)),
            rel_tol=0,
            abs_tol=1e-12,
        )
        or evidence.get("validation_sample_id_sha256") != expected_sample_hash
        or evidence.get("seed_artifacts_sha256")
        != _canonical_json_sha256({"artifacts": observed_artifacts})
    ):
        raise CliContractError("formal gate scorer 种子聚合或不择优合同无效")
    return dict(evidence)


def _global_training_lock_path(context: WorkflowContext) -> Path:
    """One machine-local lock shared by full, smoke and baseline training."""

    return resolve_under(
        context.layout.root,
        context.layout.registry / ".model-training.lock",
    )


def _adapter_context(args: argparse.Namespace, *, create: bool) -> WorkflowContext:
    engineering_smoke = bool(getattr(args, "engineering_smoke", False))
    variant = getattr(args, "_variant", None)
    if engineering_smoke:
        variant = "smoke"
    return build_context(
        args.config,
        create=create,
        variant=variant,
        training_profile="engineering_smoke" if engineering_smoke else "full",
        learning_rate_override=getattr(args, "learning_rate", None),
        seed_override=getattr(args, "seed", None),
    )


def _write_resolved_training_config(
    context: WorkflowContext, *, engineering_smoke: bool
) -> Path:
    path = context.metrics_dir / "resolved_training_config.json"
    payload = {
        "schema_version": "kronos-a-share-resolved-training-v1",
        "run_id": context.run_id,
        "dataset_id": context.dataset_id,
        "profile": "engineering_smoke" if engineering_smoke else "full",
        "base_config_sha256": context.config_sha256,
        "resolved_config_sha256": context.training_config_sha256,
        "seed": int(context.config["training"]["seed"]),
        "adapter": dict(context.config["training"]["adapter"]),
    }
    if path.is_file():
        if _json_file(path) != payload:
            raise CliBlocked("resolved training config 漂移，拒绝混合恢复")
    else:
        atomic_write_json(path, payload, allowed_root=context.layout.root)
    return path


def command_train_adapter(args: argparse.Namespace) -> dict[str, Any]:
    from kronos_a_share_training import CheckpointFileLock

    lock_context = _adapter_context(args, create=True)
    # Acquire before importing/loading Torch or Kronos components so a second
    # full/smoke/evaluation process cannot consume GPU memory while waiting.
    with CheckpointFileLock(_global_training_lock_path(lock_context)):
        return _command_train_adapter_impl(args)


def _command_train_adapter_impl(args: argparse.Namespace) -> dict[str, Any]:
    import torch
    from kronos_a_share_model import validate_kronos_base_adapter_parameter_count
    from kronos_a_share_training import (
        CheckpointFileLock,
        CheckpointStore,
        adapter_forward_loss,
        prepare_adapter_stage,
        select_validated_adapter,
        set_deterministic_seed,
    )

    context = _adapter_context(args, create=True)
    data_report = _load_data_status(context)
    engineering_smoke = bool(args.engineering_smoke)
    _assert_data_allowed(data_report["status"], engineering_smoke=engineering_smoke)
    if not engineering_smoke:
        diagnostic_evidence = _materialize_adapter_diagnostic_from_registry(context)
        if diagnostic_evidence is None:
            raise CliBlocked(
                "formal adapter 必须先完成固定5-run smoke诊断、选中LR复核并更新正式配置"
            )
    resolved_config_path = _write_resolved_training_config(
        context, engineering_smoke=engineering_smoke
    )
    cache = _load_cache(context)
    arrays = cache["arrays"]
    train_members = np.flatnonzero(np.asarray(arrays["split"]) == SPLIT_CODES["train"])
    valid_members = np.flatnonzero(
        np.asarray(arrays["split"]) == SPLIT_CODES["validation"]
    )
    seed = int(context.config["training"]["seed"])
    set_deterministic_seed(seed)
    components = _load_kronos_components(context, args.device)
    model = components.model
    lora = context.config["model"]["lora"]
    prepare_adapter_stage(
        model,
        rank=int(lora["rank"]),
        alpha=float(lora["alpha"]),
        dropout=float(lora["dropout"]),
    )
    validate_kronos_base_adapter_parameter_count(model)
    settings = context.config["training"]["adapter"]
    optimizer = torch.optim.AdamW(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=float(settings["learning_rate"]),
        weight_decay=float(settings["weight_decay"]),
    )
    warmup = max(1, int(settings["warmup_steps"]))
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda step: min(1.0, (step + 1) / warmup)
    )
    binding = _binding(context)
    store = CheckpointStore(context.checkpoint_dir, binding)
    max_allowed_steps = int(
        settings["smoke_steps"] if engineering_smoke else settings["max_steps"]
    )
    stop_after = _validated_adapter_stop_after(
        engineering_smoke=engineering_smoke,
        requested=args.stop_after,
        max_allowed_steps=max_allowed_steps,
    )
    if (
        not engineering_smoke
        and stop_after != max_allowed_steps
        and stop_after % FULL_CHECKPOINT_INTERVAL != 0
    ):
        raise CliContractError(
            "formal adapter --stop-after 仅允许落在1000步验证/恢复边界或完整10000步"
        )
    if stop_after < 1 or stop_after > max_allowed_steps:
        raise CliContractError(f"stop-after 必须位于 1..{max_allowed_steps}")
    resume = _resume_reference(store, args.resume, "adapter")
    start_step = 0
    best_validation = math.inf
    zero_shot_validation = math.nan
    validation_history: list[dict[str, Any]] = []
    stale_validations = 0
    if resume is not None:
        loaded = store.load(
            resume,
            model=model,
            optimizer=optimizer,
            restore_rng=True,
            map_location=components.device,
        )
        start_step = loaded.step
        best_validation = float(loaded.extra_state.get("best_validation_ce", math.inf))
        zero_shot_validation = float(
            loaded.extra_state.get("zero_shot_validation_ce", math.nan)
        )
        history = loaded.extra_state.get("validation_history", [])
        if not isinstance(history, list):
            raise CliContractError("adapter checkpoint validation_history 无效")
        validation_history = [dict(item) for item in history]
        stale_validations = int(loaded.extra_state.get("stale_validations", 0))
        scheduler_state = loaded.extra_state.get("scheduler_state")
        if scheduler_state:
            scheduler.load_state_dict(scheduler_state)
    if start_step >= stop_after:
        existing_summary = context.metrics_dir / "adapter_summary.json"
        summary = _json_file(existing_summary) if existing_summary.is_file() else {
            "schema_version": "kronos-a-share-adapter-train-v1",
            "status": "unverified" if engineering_smoke else "ok",
            "run_id": context.run_id,
            "completed_step": start_step,
            "checkpoint": str(store.root / store.inspect(resume)["checkpoint_name"]),
        }
        if (
            not engineering_smoke
            and summary.get("formal_training_complete") is True
            and summary.get("zero_shot_fallback") is False
            and summary.get("checkpoint_name")
            and summary.get("adapter_hash")
        ):
            try:
                diagnostic_evidence = _adapter_diagnostic_matrix_evidence(
                    context,
                    production_reference=str(summary["checkpoint_name"]),
                    production_hash=str(summary["adapter_hash"]),
                )
            except CliContractError:
                summary["status"] = "unverified"
                summary.pop("adapter_diagnostic_matrix_evidence", None)
            else:
                summary["status"] = "ok"
                summary["adapter_diagnostic_matrix_evidence"] = diagnostic_evidence
            atomic_write_json(
                existing_summary,
                summary,
                allowed_root=context.layout.root,
            )
        return _envelope(
            "train-adapter",
            status=summary.get("status", "unverified"),
            message="LoRA checkpoint 已达到 stop-after，本次未重复训练。",
            training=summary,
            evidence_class="model_output",
            output_type="N/A",
        )
    if not math.isfinite(zero_shot_validation):
        zero_shot_validation = _validation_adapter_ce(
            model,
            arrays,
            valid_members,
            batch_size=int(settings["batch_size"]),
            device=components.device,
        )
    batch_size = int(settings["batch_size"])
    accumulation = int(settings["gradient_accumulation"])
    checkpoint_interval = int(settings["checkpoint_interval"])
    validation_interval = int(settings["validation_interval"])
    if checkpoint_interval != validation_interval:
        raise CliContractError("checkpoint_interval 必须与 validation_interval 严格对齐")
    patience = int(settings["early_stopping_patience"])
    minimum_improvement = float(
        context.config["evaluation"]["adapter_ce_improvement_min"]
    )
    last_metrics: dict[str, float] = {}
    saved_path: Path | None = None
    completed_step = start_step
    early_stopped = False
    if components.device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()
    with CheckpointFileLock(context.checkpoint_dir / ".training.lock"):
        for step in range(start_step + 1, stop_after + 1):
            optimizer.zero_grad(set_to_none=True)
            aggregate = {"loss": 0.0, "ce_s1": 0.0, "ce_s2": 0.0}
            for accumulation_index in range(accumulation):
                microstep = (step - 1) * accumulation + accumulation_index
                indices = _deterministic_batch(
                    train_members,
                    microstep=microstep,
                    batch_size=batch_size,
                    seed=seed,
                )
                loss, metrics = adapter_forward_loss(
                    model, _adapter_batch(arrays, indices, components.device)
                )
                if not bool(torch.isfinite(loss)):
                    raise CliBlocked("adapter loss 出现 NaN/Inf，已停止训练")
                (loss / accumulation).backward()
                for key in aggregate:
                    aggregate[key] += float(metrics[key]) / accumulation
            norm = torch.nn.utils.clip_grad_norm_(
                [parameter for parameter in model.parameters() if parameter.requires_grad],
                float(settings["gradient_clip"]),
            )
            optimizer.step()
            scheduler.step()
            aggregate["grad_norm"] = float(norm.detach().cpu())
            aggregate["learning_rate"] = float(optimizer.param_groups[0]["lr"])
            last_metrics = aggregate
            validation_ce: float | None = None
            is_best = False
            if step % validation_interval == 0 or step == stop_after:
                validation_ce = _validation_adapter_ce(
                    model,
                    arrays,
                    valid_members,
                    batch_size=batch_size,
                    device=components.device,
                )
                validation_history.append(
                    {
                        "step": step,
                        "validation_ce": validation_ce,
                        "train_loss": float(aggregate["loss"]),
                        "ce_s1": float(aggregate["ce_s1"]),
                        "ce_s2": float(aggregate["ce_s2"]),
                        "learning_rate": float(aggregate["learning_rate"]),
                    }
                )
                selection = select_validated_adapter(
                    validation_history,
                    zero_shot_validation_ce=zero_shot_validation,
                    minimum_improvement=minimum_improvement,
                )
                best_validation = selection.best_validation_ce
                stale_validations = selection.stale_validations
                is_best = bool(
                    not selection.zero_shot_fallback
                    and selection.best_step == step
                )
            if step % checkpoint_interval == 0 or step == stop_after:
                if validation_ce is None:
                    raise CliContractError("拒绝保存缺少因果 CE 的 adapter checkpoint")
                selection = select_validated_adapter(
                    validation_history,
                    zero_shot_validation_ce=zero_shot_validation,
                    minimum_improvement=minimum_improvement,
                )
                best_entry = next(
                    (
                        item
                        for item in validation_history
                        if int(item["step"]) == selection.best_step
                    ),
                    None,
                )
                train_validation_gap = (
                    float(selection.best_validation_ce - float(best_entry["train_loss"]))
                    if best_entry is not None
                    else None
                )
                saved_path = store.save(
                    stage="adapter",
                    step=step,
                    model=model,
                    optimizer=optimizer,
                    metric=validation_ce,
                    is_best=is_best,
                    extra_state={
                        "run_id": context.run_id,
                        "zero_shot_validation_ce": zero_shot_validation,
                        "best_validation_ce": best_validation,
                        "best_step": selection.best_step,
                        "selection_reason": selection.selection_reason,
                        "zero_shot_fallback": selection.zero_shot_fallback,
                        "validation_history": validation_history,
                        "stale_validations": stale_validations,
                        "train_validation_gap": train_validation_gap,
                        "validation_contract": settings["validation_contract"],
                        "peak_gpu_memory_bytes": (
                            int(torch.cuda.max_memory_allocated())
                            if components.device.startswith("cuda")
                            else 0
                        ),
                        "gpu_memory_limit_bytes": 3 * 1024**3,
                        "scheduler_state": scheduler.state_dict(),
                        "engineering_smoke": engineering_smoke,
                        "resolved_config_sha256": context.training_config_sha256,
                        "checkpoint_interval": checkpoint_interval,
                        "validation_interval": validation_interval,
                        "early_stopping_patience": patience,
                        "max_allowed_steps": max_allowed_steps,
                    },
                )
            completed_step = step
            if validation_ce is not None and stale_validations >= patience:
                early_stopped = True
                break
    selection = select_validated_adapter(
        validation_history,
        zero_shot_validation_ce=zero_shot_validation,
        minimum_improvement=minimum_improvement,
    )
    best_validation = selection.best_validation_ce
    diagnostic_best_entry = min(
        validation_history, key=lambda item: float(item["validation_ce"])
    )
    diagnostic_best_validation = float(diagnostic_best_entry["validation_ce"])
    diagnostic_improvement = (
        zero_shot_validation - diagnostic_best_validation
    ) / zero_shot_validation
    best_entry = next(
        (
            item
            for item in validation_history
            if int(item["step"]) == selection.best_step
        ),
        None,
    )
    train_validation_gap = (
        float(best_validation - float(best_entry["train_loss"]))
        if best_entry is not None
        else None
    )
    best_adapter_reference: str | None = None
    best_adapter_hash: str | None = None
    if not selection.zero_shot_fallback:
        best_adapter_reference = _stage_reference(store, stage="adapter", kind="best")
        best_adapter_manifest = store.inspect(best_adapter_reference)
        if (
            not math.isfinite(float(best_adapter_manifest.get("metric", math.nan)))
            or int(best_adapter_manifest["step"]) != selection.best_step
        ):
            raise CliContractError("best adapter 未绑定最优现场因果 CE")
        best_adapter_hash = best_adapter_manifest["files"]["state.pt"]["sha256"]
    diagnostic_checkpoint_reference = best_adapter_reference
    diagnostic_checkpoint_hash = best_adapter_hash
    if engineering_smoke and validation_history:
        diagnostic_checkpoint_reference = (
            f"adapter-step-{int(diagnostic_best_entry['step']):08d}"
        )
        diagnostic_manifest = store.inspect(diagnostic_checkpoint_reference)
        diagnostic_checkpoint_hash = diagnostic_manifest["files"]["state.pt"][
            "sha256"
        ]
    peak_bytes = (
        int(torch.cuda.max_memory_allocated())
        if components.device.startswith("cuda")
        else 0
    )
    improvement = selection.improvement
    gpu_memory_limit_bytes = int(
        float(context.config["runtime"]["max_gpu_memory_gb"]) * 1024**3
    )
    peak_within_limit = peak_bytes <= gpu_memory_limit_bytes
    formal_training_complete = bool(
        not engineering_smoke
        and (completed_step == max_allowed_steps or early_stopped)
        and completed_step % FULL_CHECKPOINT_INTERVAL == 0
    )
    summary = {
        "schema_version": "kronos-a-share-adapter-train-v1",
        "status": (
            "blocked"
            if selection.zero_shot_fallback or not peak_within_limit
            else "unverified"
        ),
        "data_status": data_report["status"],
        "run_id": context.run_id,
        "binding": _gate_binding(binding),
        "start_step": start_step,
        "completed_step": completed_step,
        "early_stopped": early_stopped,
        "max_allowed_steps": max_allowed_steps,
        "formal_training_complete": formal_training_complete,
        "zero_shot_validation_ce": zero_shot_validation,
        "best_validation_ce": best_validation,
        "best_step": selection.best_step,
        "adapter_ce_improvement": improvement,
        "diagnostic_best_validation_ce": diagnostic_best_validation,
        "diagnostic_best_step": int(diagnostic_best_entry["step"]),
        "diagnostic_ce_improvement": diagnostic_improvement,
        "selection_reason": selection.selection_reason,
        "zero_shot_fallback": selection.zero_shot_fallback,
        "validation_history": validation_history,
        "train_validation_gap": train_validation_gap,
        "last_train_metrics": last_metrics,
        "peak_gpu_memory_bytes": peak_bytes,
        "gpu_memory_limit_bytes": gpu_memory_limit_bytes,
        "checkpoint": (
            str(context.checkpoint_dir / best_adapter_reference)
            if best_adapter_reference is not None
            else None
        ),
        "checkpoint_name": best_adapter_reference,
        "adapter_hash": best_adapter_hash,
        "diagnostic_checkpoint_name": diagnostic_checkpoint_reference,
        "diagnostic_checkpoint_hash": diagnostic_checkpoint_hash,
        "resolved_training_config": str(resolved_config_path),
        "resolved_config_sha256": context.training_config_sha256,
        "generated_at": _utc_now(),
    }
    atomic_write_json(
        context.metrics_dir / "adapter_summary.json",
        summary,
        allowed_root=context.layout.root,
    )
    if _is_explicit_adapter_diagnostic(args):
        _register_adapter_diagnostic_trial(context, summary)
    if (
        not engineering_smoke
        and formal_training_complete
        and not selection.zero_shot_fallback
        and peak_within_limit
        and best_adapter_reference is not None
        and best_adapter_hash is not None
    ):
        try:
            diagnostic_evidence = _adapter_diagnostic_matrix_evidence(
                context,
                production_reference=best_adapter_reference,
                production_hash=best_adapter_hash,
            )
        except CliContractError:
            pass
        else:
            summary["status"] = "ok"
            summary["adapter_diagnostic_matrix_evidence"] = diagnostic_evidence
            atomic_write_json(
                context.metrics_dir / "adapter_summary.json",
                summary,
                allowed_root=context.layout.root,
            )
    if not peak_within_limit:
        raise CliBlocked("峰值显存超过配置的3 GiB准入上限")
    return _envelope(
        "train-adapter",
        status=summary["status"],
        message=(
            "LoRA 工程冒烟完成；工件未经准出。"
            if args.engineering_smoke
            else "LoRA 训练阶段完成。"
        ),
        training=summary,
        evidence_class="model_output",
        output_type="N/A",
    )


def _last_context_states(
    model: Any,
    arrays: Mapping[str, Any],
    indices: np.ndarray,
    *,
    device: str,
    chunk_size: int,
):
    import torch

    states: list[torch.Tensor] = []
    model.eval()
    with torch.no_grad():
        for start in range(0, len(indices), chunk_size):
            selected = indices[start : start + chunk_size]
            s1 = torch.as_tensor(
                np.asarray(arrays["s1"][selected, :LOOKBACK]), device=device
            ).long()
            s2 = torch.as_tensor(
                np.asarray(arrays["s2"][selected, :LOOKBACK]), device=device
            ).long()
            stamp = torch.as_tensor(
                np.asarray(arrays["stamp"][selected, :LOOKBACK]), device=device
            ).long()
            _, context = model.decode_s1(s1, s2, stamp=stamp)
            states.append(context[:, LOOKBACK - 1].detach())
    return torch.cat(states, dim=0)


def _scorer_loss_for_date(
    model: Any,
    head: Any,
    arrays: Mapping[str, Any],
    indices: np.ndarray,
    *,
    device: str,
    chunk_size: int,
    smooth_l1_weight: float,
    ranknet_weight: float,
):
    import torch
    from kronos_a_share_model import cross_sectional_scorer_loss

    states = _last_context_states(
        model, arrays, indices, device=device, chunk_size=chunk_size
    )
    scores = head(states.unsqueeze(1), history_length=1)
    targets = torch.as_tensor(
        np.asarray(arrays["label"][indices]), device=device, dtype=scores.dtype
    )
    dates = np.asarray(arrays["trade_date"][indices]).tolist()
    return cross_sectional_scorer_loss(
        scores,
        targets,
        dates,
        smooth_l1_weight=smooth_l1_weight,
        ranknet_weight=ranknet_weight,
    ), scores


def _date_index_groups(
    arrays: Mapping[str, Any],
    members: np.ndarray,
    *,
    formal_cross_section: bool = False,
) -> list[np.ndarray]:
    dates = np.asarray(arrays["trade_date"][members])
    groups = [members[dates == value] for value in np.unique(dates)]
    groups = [group for group in groups if len(group) >= 2]
    if not formal_cross_section:
        return groups
    if "active_member_count" not in arrays:
        raise CliContractError("formal scorer 缺少 active_member_count token 合同")
    for group in groups:
        active_values = np.unique(
            np.asarray(arrays["active_member_count"][group], dtype=np.int64)
        )
        eligible_count = int(
            np.unique(np.asarray(arrays["instrument_id"][group])).size
        )
        if len(active_values) != 1 or int(active_values[0]) < 1:
            raise CliContractError("formal scorer 同日 active_member_count 不唯一")
        coverage = eligible_count / int(active_values[0])
        if (
            eligible_count < FORMAL_MIN_CROSS_SECTION
            or coverage < FORMAL_MIN_COVERAGE_RATIO
        ):
            trade_date = int(np.asarray(arrays["trade_date"])[int(group[0])])
            raise CliContractError(
                "formal scorer 横截面覆盖不足："
                f"trade_date={trade_date}, eligible_count={eligible_count}, "
                f"active_member_count={int(active_values[0])}, coverage={coverage:.6f}"
            )
    return groups


def _score_members(
    model: Any,
    head: Any,
    arrays: Mapping[str, Any],
    members: np.ndarray,
    *,
    device: str,
    chunk_size: int,
    formal_cross_section: bool = False,
) -> pd.DataFrame:
    import torch

    rows: list[pd.DataFrame] = []
    active_member_counts = (
        arrays["active_member_count"]
        if "active_member_count" in arrays
        else np.zeros(len(np.asarray(arrays["trade_date"])), dtype=np.int32)
    )
    head.eval()
    with torch.no_grad():
        for group in _date_index_groups(
            arrays, members, formal_cross_section=formal_cross_section
        ):
            states = _last_context_states(
                model, arrays, group, device=device, chunk_size=chunk_size
            )
            scores = head(states.unsqueeze(1), history_length=1).detach().cpu().numpy()
            rows.append(
                pd.DataFrame(
                    {
                        "sample_id": group,
                        "trade_date": pd.to_datetime(
                            np.asarray(arrays["trade_date"][group]).astype(str),
                            format="%Y%m%d",
                        ).strftime("%Y-%m-%d"),
                        "instrument_id": np.asarray(arrays["instrument_id"][group]),
                        "active_member_count": np.asarray(
                            active_member_counts[group]
                        ),
                        "raw_score": scores,
                        "label_excess_10d": np.asarray(arrays["label"][group]),
                    }
                )
            )
    head.train()
    if not rows:
        raise CliContractError("评分 split 缺少至少两个证券的同日横截面")
    return pd.concat(rows, ignore_index=True)


def _mean_rank_ic(frame: pd.DataFrame, *, formal_cross_section: bool = False) -> float:
    daily = daily_rank_ic(
        frame,
        min_instruments=(FORMAL_MIN_CROSS_SECTION if formal_cross_section else 2),
        active_member_count_column=(
            "active_member_count" if formal_cross_section else None
        ),
        min_coverage_ratio=(
            FORMAL_MIN_COVERAGE_RATIO if formal_cross_section else None
        ),
        require_eligible_cross_section=formal_cross_section,
    )
    values = pd.to_numeric(daily["rank_ic"], errors="coerce")
    finite = values[np.isfinite(values)]
    if finite.empty:
        raise CliContractError("验证集 RankIC 全部不可计算")
    return float(finite.mean())


def _train_ephemeral_scorer_seed(
    model: Any,
    arrays: Mapping[str, Any],
    train_members: np.ndarray,
    valid_members: np.ndarray,
    *,
    seed: int,
    settings: Mapping[str, Any],
    max_epochs: int,
    device: str,
    chunk_size: int,
) -> dict[str, Any]:
    """Train one non-published scorer seed for stability evidence only."""

    import torch
    from kronos_a_share_model import KronosScoringHead
    from kronos_a_share_training import prepare_scorer_stage, set_deterministic_seed

    set_deterministic_seed(seed)
    head = KronosScoringHead(d_model=832).to(device)
    prepare_scorer_stage(model, head)
    optimizer = torch.optim.AdamW(
        head.parameters(),
        lr=float(settings["learning_rate"]),
        weight_decay=float(settings["weight_decay"]),
    )
    train_groups = _date_index_groups(
        arrays, train_members, formal_cross_section=True
    )
    if not train_groups:
        raise CliContractError("scorer stability 没有可比较的正式横截面")
    best_rank_ic = -math.inf
    best_epoch = 0
    best_predictions: pd.DataFrame | None = None
    stale = 0
    completed_epoch = 0
    for epoch in range(1, max_epochs + 1):
        order = np.random.default_rng(seed + epoch).permutation(len(train_groups))
        for group_index in order:
            group = train_groups[int(group_index)]
            head.train()
            optimizer.zero_grad(set_to_none=True)
            scorer_loss, _ = _scorer_loss_for_date(
                model,
                head,
                arrays,
                group,
                device=device,
                chunk_size=chunk_size,
                smooth_l1_weight=float(settings["smooth_l1_weight"]),
                ranknet_weight=float(settings["ranknet_weight"]),
            )
            if not bool(torch.isfinite(scorer_loss.total)):
                raise CliBlocked(f"scorer seed={seed} loss 出现 NaN/Inf")
            scorer_loss.total.backward()
            torch.nn.utils.clip_grad_norm_(head.parameters(), 3.0)
            optimizer.step()
        validation = _score_members(
            model,
            head,
            arrays,
            valid_members,
            device=device,
            chunk_size=chunk_size,
            formal_cross_section=True,
        )
        rank_ic = _mean_rank_ic(validation, formal_cross_section=True)
        completed_epoch = epoch
        if rank_ic > best_rank_ic:
            best_rank_ic = rank_ic
            best_epoch = epoch
            best_predictions = validation[["sample_id", "raw_score"]].copy()
            stale = 0
        else:
            stale += 1
        if stale >= int(settings["early_stopping_patience"]):
            break
    if best_predictions is None:
        raise CliContractError(f"scorer seed={seed} 未产生可审计 validation prediction")
    return {
        "seed": seed,
        "best_validation_rank_ic": float(best_rank_ic),
        "best_epoch": best_epoch,
        "completed_epoch": completed_epoch,
        "_best_predictions": best_predictions,
    }


def _scorer_seed_stability(
    context: WorkflowContext,
    model: Any,
    arrays: Mapping[str, Any],
    train_members: np.ndarray,
    valid_members: np.ndarray,
    *,
    primary_validation_frame: pd.DataFrame,
    binding: Any,
    adapter_checkpoint: str,
    adapter_hash: str,
    evaluated_checkpoint: str,
    scorer_checkpoint_hash: str,
    settings: Mapping[str, Any],
    max_epochs: int,
    device: str,
    chunk_size: int,
) -> dict[str, Any]:
    from kronos_a_share_training import CheckpointStore

    evidence_root = resolve_under(
        context.layout.root,
        context.predictions_dir / "scorer-seed-stability" / scorer_checkpoint_hash,
    )
    evidence_root.mkdir(parents=True, exist_ok=True)
    expected_ids = _members_for_split(arrays, "validation")
    sample_hash = _sha256_bytes(expected_ids.tobytes())

    def persist(seed: int, frame: pd.DataFrame, details: Mapping[str, Any]) -> dict[str, Any]:
        ordered = frame[["sample_id", "raw_score"]].copy()
        ordered["sample_id"] = pd.to_numeric(ordered["sample_id"], errors="raise").astype(
            np.int64
        )
        ordered["raw_score"] = pd.to_numeric(ordered["raw_score"], errors="coerce")
        ordered = ordered.sort_values("sample_id").reset_index(drop=True)
        ids = ordered["sample_id"].to_numpy(dtype=np.int64)
        if not np.array_equal(ids, expected_ids) or not np.isfinite(
            ordered["raw_score"].to_numpy(dtype=float)
        ).all():
            raise CliContractError(f"scorer seed={seed} validation prediction 未全量绑定")
        path = evidence_root / f"seed-{seed}.csv"
        prediction_hash = _atomic_csv(path, ordered, context.layout.root)
        return {
            "seed": seed,
            **dict(details),
            "prediction_path": str(path.resolve()),
            "prediction_sha256": prediction_hash,
            "sample_id_sha256": sample_hash,
            "row_count": int(len(ordered)),
        }

    primary_rank_ic = _mean_rank_ic(
        primary_validation_frame, formal_cross_section=True
    )
    primary_manifest = CheckpointStore(context.checkpoint_dir, binding).inspect(
        evaluated_checkpoint
    )
    primary_extra = _checkpoint_extra_state(
        CheckpointStore(context.checkpoint_dir, binding), evaluated_checkpoint
    )
    per_seed = [
        persist(
            100,
            primary_validation_frame,
            {
                "best_validation_rank_ic": float(primary_rank_ic),
                "best_epoch": int(primary_extra.get("best_epoch", primary_manifest["step"])),
                "completed_epoch": int(primary_extra.get("scorer_epoch", primary_manifest["step"])),
                "published_checkpoint": True,
            },
        )
    ]
    for seed in FORMAL_SCORER_SEEDS[1:]:
        result = _train_ephemeral_scorer_seed(
            model,
            arrays,
            train_members,
            valid_members,
            seed=seed,
            settings=settings,
            max_epochs=max_epochs,
            device=device,
            chunk_size=chunk_size,
        )
        predictions = result.pop("_best_predictions")
        result["published_checkpoint"] = False
        per_seed.append(persist(seed, predictions, result))
    values = np.asarray(
        [item["best_validation_rank_ic"] for item in per_seed], dtype=np.float64
    )
    if len(per_seed) != 20 or not np.isfinite(values).all():
        raise CliContractError("scorer 20-seed stability 证据不完整")
    artifact_commitments = [
        {
            key: item[key]
            for key in (
                "seed",
                "prediction_sha256",
                "sample_id_sha256",
                "row_count",
                "best_validation_rank_ic",
                "best_epoch",
                "completed_epoch",
                "published_checkpoint",
            )
        }
        for item in per_seed
    ]
    return {
        "schema_version": "kronos-a-share-scorer-seed-stability-v2",
        "binding": _gate_binding(binding),
        "adapter_checkpoint": adapter_checkpoint,
        "adapter_hash": adapter_hash,
        "evaluated_checkpoint": evaluated_checkpoint,
        "scorer_checkpoint_hash": scorer_checkpoint_hash,
        "seeds": list(FORMAL_SCORER_SEEDS),
        "production_seed": 100,
        "selection_policy": "seed100_checkpoint_fixed_no_seed_selection",
        "aggregate_method": "mean_and_sample_std_over_20_fixed_seeds",
        "training_max_epochs": int(settings["max_epochs"]),
        "early_stopping_patience": int(settings["early_stopping_patience"]),
        "validation_sample_id_sha256": sample_hash,
        "seed_artifacts_sha256": _canonical_json_sha256(
            {"artifacts": artifact_commitments}
        ),
        "rank_ic_mean": float(values.mean()),
        "rank_ic_std": float(values.std(ddof=1)),
        "per_seed": per_seed,
    }


def _atomic_csv(path: Path, frame: pd.DataFrame, root: Path) -> str:
    destination = resolve_under(root, path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = frame.to_csv(index=False, lineterminator="\n").encode("utf-8")
    pending = destination.with_name(f".{destination.name}.pending-{os.getpid()}")
    with pending.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, destination)
    return _sha256_bytes(payload)


def _members_for_split(arrays: Mapping[str, Any], split: str) -> np.ndarray:
    if split not in SPLIT_CODES:
        raise CliContractError(f"split 无效：{split}")
    members = np.flatnonzero(
        np.asarray(arrays["split"]) == SPLIT_CODES[split]
    ).astype(np.int64)
    if len(members) == 0:
        raise CliContractError(f"{split} split 没有样本")
    return members


def _validation_members(arrays: Mapping[str, Any]) -> np.ndarray:
    return _members_for_split(arrays, "validation")


def _score_artifact_record(
    context: WorkflowContext,
    *,
    path: Path,
    name: str,
    binding: Any,
    expected_ids: np.ndarray,
) -> dict[str, str]:
    artifact = resolve_under(context.layout.root, path)
    metadata_path = artifact.with_suffix(artifact.suffix + ".metadata.json")
    if not artifact.is_file() or not metadata_path.is_file():
        raise CliContractError(f"{name} 基线工件或 metadata 缺失")
    metadata = _json_file(metadata_path)
    expected = {
        "schema_version": "kronos-a-share-score-artifact-v1",
        "name": name,
        "binding": _gate_binding(binding),
        "output_sha256": sha256_file(artifact),
        "sample_id_sha256": _sha256_bytes(expected_ids.tobytes()),
        "row_count": int(len(expected_ids)),
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise CliContractError(f"{name} 基线 provenance 不匹配：{key}")
    frame = pd.read_csv(artifact)
    if set(frame.columns) != {"sample_id", "raw_score"}:
        raise CliContractError(f"{name} 基线列合同无效")
    ids = pd.to_numeric(frame["sample_id"], errors="raise").to_numpy(dtype=np.int64)
    scores = pd.to_numeric(frame["raw_score"], errors="coerce").to_numpy(dtype=float)
    if not np.array_equal(ids, expected_ids) or not np.isfinite(scores).all():
        raise CliContractError(f"{name} 基线 sample_id/score 合同无效")
    return {"path": str(artifact), "sha256": expected["output_sha256"]}


def _write_score_artifact(
    context: WorkflowContext,
    *,
    path: Path,
    name: str,
    binding: Any,
    frame: pd.DataFrame,
    details: Mapping[str, Any],
) -> dict[str, str]:
    ordered = frame[["sample_id", "raw_score"]].copy()
    ordered["sample_id"] = pd.to_numeric(
        ordered["sample_id"], errors="raise"
    ).astype(np.int64)
    ordered["raw_score"] = pd.to_numeric(
        ordered["raw_score"], errors="coerce"
    )
    ordered = ordered.sort_values("sample_id").reset_index(drop=True)
    if ordered["sample_id"].duplicated().any() or not np.isfinite(
        ordered["raw_score"].to_numpy(dtype=float)
    ).all():
        raise CliContractError(f"{name} 基线包含重复 sample_id 或 NaN/Inf")
    output_hash = _atomic_csv(path, ordered, context.layout.root)
    ids = ordered["sample_id"].to_numpy(dtype=np.int64)
    metadata = {
        "schema_version": "kronos-a-share-score-artifact-v1",
        "name": name,
        "binding": _gate_binding(binding),
        "output_path": str(path.resolve()),
        "output_sha256": output_hash,
        "sample_id_sha256": _sha256_bytes(ids.tobytes()),
        "row_count": int(len(ordered)),
        "details": dict(details),
        "generated_at": _utc_now(),
    }
    atomic_write_json(
        path.with_suffix(path.suffix + ".metadata.json"),
        metadata,
        allowed_root=context.layout.root,
    )
    return {"path": str(path.resolve()), "sha256": output_hash}


def _normalized_histories(
    context: WorkflowContext,
    sample_ids: np.ndarray,
) -> np.ndarray:
    index = pd.read_csv(context.dataset_dir / "sample_index.csv")
    if "sample_id" not in index or index["sample_id"].duplicated().any():
        raise CliContractError("sample_index.sample_id 合同无效")
    index = index.set_index("sample_id", drop=False)
    missing = sorted(set(int(value) for value in sample_ids) - set(index.index))
    if missing:
        raise CliContractError(f"sample_index 缺少 validation sample_id：{missing[:10]}")
    actions_path = _pit_table_path(_pit_root(context), "corporate_actions")
    if actions_path is None:
        raise CliContractError("正式 zero-shot 基线缺少 corporate_actions")
    actions = load_corporate_actions(actions_path)
    frames: dict[str, pd.DataFrame] = {}
    values: list[np.ndarray] = []
    spec = WindowSpec(lookback=LOOKBACK, horizon=HORIZON, purge_days=PURGE_DAYS)
    for sample_id in sample_ids:
        row = index.loc[int(sample_id)]
        path = str(row["day_file"])
        if path not in frames:
            frames[path] = read_day_file(
                resolve_under(context.layout.root, Path(path).resolve(strict=True))
            )
        normalized, _ = causal_adjusted_normalized_window(
            frames[path],
            int(row["start_index"]),
            spec,
            corporate_actions=actions,
            ticker=str(row["ticker"]),
            origin_date=int(row["origin_date"]),
        )
        values.append(normalized[:LOOKBACK])
    return np.stack(values).astype(np.float32, copy=False)


def _ensure_zero_shot_scores(
    context: WorkflowContext,
    *,
    binding: Any,
    arrays: Mapping[str, Any],
    device: str,
    chunk_size: int,
    evaluate_split: str = "validation",
    output_path: Path | None = None,
    reuse_existing: bool = True,
) -> dict[str, str]:
    import torch
    from kronos_a_share_training import set_deterministic_seed

    members = _members_for_split(arrays, evaluate_split)
    output = output_path or context.predictions_dir / (
        "zero_shot_scores.csv"
        if evaluate_split == "validation"
        else f"{evaluate_split}_zero_shot_scores.csv"
    )
    output = resolve_under(context.layout.root, output)
    if reuse_existing and output.is_file():
        return _score_artifact_record(
            context,
            path=output,
            name="zero_shot_score",
            binding=binding,
            expected_ids=members,
        )
    components = _load_kronos_components(context, device)
    runtime_root = Path(context.config["runtime"]["kronos_runtime_root"])
    paths = __import__("run_kronos_forecast").runtime_paths(runtime_root)
    if str(paths["source"]) not in sys.path:
        sys.path.insert(0, str(paths["source"]))
    from model import KronosPredictor

    predictor = KronosPredictor(
        components.model,
        components.tokenizer,
        device=components.device,
        max_context=512,
    )
    set_deterministic_seed(int(context.config["training"]["seed"]) + 10_001)
    all_histories = _normalized_histories(context, members)
    scores: list[np.ndarray] = []
    for start in range(0, len(members), chunk_size):
        selected = members[start : start + chunk_size]
        histories = all_histories[start : start + len(selected)]
        x_stamp = np.asarray(arrays["stamp"][selected, :LOOKBACK], dtype=np.float32)
        y_stamp = np.asarray(
            arrays["stamp"][selected, LOOKBACK : LOOKBACK + HORIZON],
            dtype=np.float32,
        )
        with torch.inference_mode():
            prediction = predictor.generate(
                histories,
                x_stamp,
                y_stamp,
                HORIZON,
                1.0,
                0,
                0.9,
                1,
                False,
            )
        prediction = np.asarray(prediction, dtype=np.float32)
        if prediction.shape != (len(selected), HORIZON, len(FEATURE_COLUMNS)):
            raise CliContractError(f"zero-shot prediction 形状无效：{prediction.shape}")
        scores.append(prediction[:, -1, 3] - histories[:, -1, 3])
    frame = pd.DataFrame(
        {"sample_id": members, "raw_score": np.concatenate(scores)}
    )
    return _write_score_artifact(
        context,
        path=output,
        name="zero_shot_score",
        binding=binding,
        frame=frame,
        details={
            "contract": "base_kronos_terminal_normalized_close_minus_last_close",
            "temperature": 1.0,
            "top_k": 0,
            "top_p": 0.9,
            "sample_count": 1,
            "evaluate_split": evaluate_split,
        },
    )


def _ensure_head_only_scores(
    context: WorkflowContext,
    *,
    binding: Any,
    arrays: Mapping[str, Any],
    device: str,
    chunk_size: int,
    evaluate_split: str = "validation",
    output_path: Path | None = None,
    reuse_existing: bool = True,
) -> dict[str, str]:
    import torch
    from kronos_a_share_model import KronosScoringHead
    from kronos_a_share_training import set_deterministic_seed

    valid_members = _validation_members(arrays)
    target_members = _members_for_split(arrays, evaluate_split)
    output = output_path or context.predictions_dir / (
        "head_only_scores.csv"
        if evaluate_split == "validation"
        else f"{evaluate_split}_head_only_scores.csv"
    )
    output = resolve_under(context.layout.root, output)
    if reuse_existing and output.is_file():
        return _score_artifact_record(
            context,
            path=output,
            name="head_only_score",
            binding=binding,
            expected_ids=target_members,
        )
    train_members = np.flatnonzero(
        np.asarray(arrays["split"]) == SPLIT_CODES["train"]
    ).astype(np.int64)
    components = _load_kronos_components(context, device)
    model = components.model
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    model.eval()
    seed = int(context.config["training"]["seed"]) + 20_001
    set_deterministic_seed(seed)
    head = KronosScoringHead(832).to(components.device)
    settings = context.config["training"]["scorer"]
    optimizer = torch.optim.AdamW(
        head.parameters(),
        lr=float(settings["learning_rate"]),
        weight_decay=float(settings["weight_decay"]),
    )
    groups = _date_index_groups(
        arrays, train_members, formal_cross_section=True
    )
    if not groups:
        raise CliContractError("head-only 训练集没有同日横截面")
    best_rank_ic = -math.inf
    best_state: dict[str, Any] | None = None
    stale = 0
    completed_epoch = 0
    for epoch in range(1, int(settings["max_epochs"]) + 1):
        order = np.random.default_rng(seed + epoch).permutation(len(groups))
        for group_index in order:
            group = groups[int(group_index)]
            head.train()
            optimizer.zero_grad(set_to_none=True)
            losses, _ = _scorer_loss_for_date(
                model,
                head,
                arrays,
                group,
                device=components.device,
                chunk_size=chunk_size,
                smooth_l1_weight=float(settings["smooth_l1_weight"]),
                ranknet_weight=float(settings["ranknet_weight"]),
            )
            if not bool(torch.isfinite(losses.total)):
                raise CliContractError("head-only loss 出现 NaN/Inf")
            losses.total.backward()
            torch.nn.utils.clip_grad_norm_(head.parameters(), 3.0)
            optimizer.step()
        validation = _score_members(
            model,
            head,
            arrays,
            valid_members,
            device=components.device,
            chunk_size=chunk_size,
            formal_cross_section=True,
        )
        rank_ic = _mean_rank_ic(validation, formal_cross_section=True)
        completed_epoch = epoch
        if rank_ic > best_rank_ic:
            best_rank_ic = rank_ic
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in head.state_dict().items()
            }
            stale = 0
        else:
            stale += 1
        if stale >= int(settings["early_stopping_patience"]):
            break
    if best_state is None:
        raise CliContractError("head-only 未产生有效 checkpoint")
    head.load_state_dict(best_state, strict=True)
    target_scores = _score_members(
        model,
        head,
        arrays,
        target_members,
        device=components.device,
        chunk_size=chunk_size,
        formal_cross_section=True,
    ).sort_values("sample_id")
    return _write_score_artifact(
        context,
        path=output,
        name="head_only_score",
        binding=binding,
        frame=target_scores[["sample_id", "raw_score"]],
        details={
            "contract": "frozen_zero_shot_kronos_layernorm_linear_head",
            "best_validation_rank_ic": best_rank_ic,
            "completed_epoch": completed_epoch,
            "seed": seed,
            "evaluate_split": evaluate_split,
        },
    )


def _require_formal_provider_membership(
    provider_manifest: Mapping[str, Any],
    index_membership_path: Path,
) -> None:
    if (
        provider_manifest.get("pit_membership_verified") is not True
        or provider_manifest.get("instrument_membership_contract")
        != "pit_csi300_union_csi500_effective_intervals"
        or Path(str(provider_manifest.get("index_membership_path"))).resolve()
        != index_membership_path.resolve()
        or provider_manifest.get("index_membership_sha256")
        != sha256_file(index_membership_path)
    ):
        raise CliContractError(
            "正式评估拒绝缺少当前 PIT index_membership 绑定的 Qlib provider"
        )


def _ensure_evaluation_companion(
    context: WorkflowContext,
    *,
    binding: Any,
    output_path: Path,
    device: str,
    chunk_size: int,
    evaluate_split: str = "validation",
    force_recompute_baselines: bool = False,
) -> Path:
    """Build every mandatory baseline and execution artifact inside the full pipeline."""

    from kronos_a_share_baseline import (
        build_baseline_comparison,
        build_evaluation_companion,
        build_project_qlib_provider,
        inspect_alpha158_lightgbm_evidence,
        inspect_evaluation_companion,
        inspect_project_qlib_provider,
        run_alpha158_lightgbm,
    )
    from kronos_a_share_training import CheckpointFileLock

    output = resolve_under(context.layout.root, output_path)
    lock = context.predictions_dir / ".evaluation-baselines.lock"
    with CheckpointFileLock(lock):
        if output.is_file() and not force_recompute_baselines:
            inspect_evaluation_companion(
                output,
                context.layout.root,
                binding=binding,
                evaluate_split=evaluate_split,
            )
            return output
        arrays = _load_cache(context)["arrays"]
        members = _members_for_split(arrays, evaluate_split)
        pit_root = _pit_root(context)
        corporate_actions_path = _pit_table_path(pit_root, "corporate_actions")
        suspensions_path = _pit_table_path(pit_root, "suspensions")
        price_limits_path = _pit_table_path(pit_root, "price_limits")
        index_membership_path = _pit_table_path(pit_root, "index_membership")
        if (
            corporate_actions_path is None
            or suspensions_path is None
            or price_limits_path is None
            or index_membership_path is None
        ):
            raise CliContractError(
                "自动评估 companion 缺少 corporate_actions/suspensions/price_limits/index_membership"
            )
        artifact_root = (
            output.parent / "formal-recomputed-sources"
            if force_recompute_baselines
            else context.predictions_dir
        )
        artifact_root = resolve_under(context.layout.root, artifact_root)
        artifact_root.mkdir(parents=True, exist_ok=True)
        provider = (
            artifact_root / "qlib-provider"
            if force_recompute_baselines
            else resolve_under(
                context.layout.data,
                Path("qlib") / context.dataset_id,
            )
        )
        if provider.is_dir():
            provider_manifest = inspect_project_qlib_provider(
                provider, context.layout.root
            )
        else:
            provider.parent.mkdir(parents=True, exist_ok=True)
            provider_manifest = build_project_qlib_provider(
                source_path=_snapshot_directory(context),
                sample_index_path=context.dataset_dir / "sample_index.csv",
                corporate_actions_path=corporate_actions_path,
                index_membership_path=index_membership_path,
                provider_uri=provider,
                training_root=context.layout.root,
                segments=context.config["data"]["splits"],
            )
        _require_formal_provider_membership(
            provider_manifest,
            index_membership_path,
        )
        zero_shot = _ensure_zero_shot_scores(
            context,
            binding=binding,
            arrays=arrays,
            device=device,
            chunk_size=chunk_size,
            evaluate_split=evaluate_split,
            output_path=(
                artifact_root / "zero_shot_scores.csv"
                if force_recompute_baselines
                else None
            ),
            reuse_existing=not force_recompute_baselines,
        )
        head_only = _ensure_head_only_scores(
            context,
            binding=binding,
            arrays=arrays,
            device=device,
            chunk_size=chunk_size,
            evaluate_split=evaluate_split,
            output_path=(
                artifact_root / "head_only_scores.csv"
                if force_recompute_baselines
                else None
            ),
            reuse_existing=not force_recompute_baselines,
        )
        alpha_standard = (
            artifact_root / "alpha158_scores.csv"
            if force_recompute_baselines
            else context.predictions_dir
            / (
                "alpha158_scores.csv"
                if evaluate_split == "validation"
                else f"{evaluate_split}_alpha158_scores.csv"
            )
        )
        alpha_raw = (
            artifact_root / "alpha158_lightgbm_raw.csv"
            if force_recompute_baselines
            else context.predictions_dir
            / (
                "alpha158_lightgbm_raw.csv"
                if evaluate_split == "validation"
                else f"{evaluate_split}_alpha158_lightgbm_raw.csv"
            )
        )
        if alpha_standard.is_file() and not force_recompute_baselines:
            inspect_alpha158_lightgbm_evidence(
                alpha_raw,
                context.layout.root,
                provider_manifest_sha256=provider_manifest["manifest_sha256"],
                evaluate_split=evaluate_split,
                seeds=FORMAL_SCORER_SEEDS,
                expected_ids=members,
            )
            alpha158 = _score_artifact_record(
                context,
                path=alpha_standard,
                name="alpha158_score",
                binding=binding,
                expected_ids=members,
            )
        else:
            if alpha_raw.is_file() and not force_recompute_baselines:
                alpha_metadata = _json_file(
                    alpha_raw.with_suffix(alpha_raw.suffix + ".metadata.json")
                )
                expected_alpha = {
                    "schema_version": "kronos-a-share-alpha158-lightgbm-v4",
                    "provider_manifest_sha256": provider_manifest["manifest_sha256"],
                    "output_sha256": sha256_file(alpha_raw),
                    "evaluate_split": evaluate_split,
                    "seeds": list(FORMAL_SCORER_SEEDS),
                    "seed_count": len(FORMAL_SCORER_SEEDS),
                    "aggregate_method": "arithmetic_mean_prediction",
                }
                for key, value in expected_alpha.items():
                    if alpha_metadata.get(key) != value:
                        raise CliContractError(f"Alpha158 工件 provenance 不匹配：{key}")
            else:
                run_alpha158_lightgbm(
                    provider_uri=provider,
                    training_root=context.layout.root,
                    output_path=alpha_raw,
                    segments=context.config["data"]["splits"],
                    evaluate_split=evaluate_split,
                    seeds=FORMAL_SCORER_SEEDS,
                )
            inspect_alpha158_lightgbm_evidence(
                alpha_raw,
                context.layout.root,
                provider_manifest_sha256=provider_manifest["manifest_sha256"],
                evaluate_split=evaluate_split,
                seeds=FORMAL_SCORER_SEEDS,
                expected_ids=members,
            )
            alpha_frame = pd.read_csv(alpha_raw)
            alpha158 = _write_score_artifact(
                context,
                path=alpha_standard,
                name="alpha158_score",
                binding=binding,
                frame=alpha_frame[["sample_id", "raw_score"]],
                details={
                    "contract": "project_qlib_alpha158_lightgbm",
                    "provider_manifest_sha256": provider_manifest[
                        "manifest_sha256"
                    ],
                    "raw_artifact_sha256": sha256_file(alpha_raw),
                    "evaluate_split": evaluate_split,
                },
            )
        sample_keys = pd.read_csv(context.dataset_dir / "sample_index.csv")[
            ["sample_id", "ticker", "origin_date"]
        ].rename(columns={"origin_date": "trade_date"})

        def comparison_scores(record: Mapping[str, str]) -> pd.DataFrame:
            score_frame = pd.read_csv(Path(record["path"]))
            return sample_keys.merge(
                score_frame,
                on="sample_id",
                how="inner",
                validate="one_to_one",
            )

        build_baseline_comparison(
            baseline_inputs=provider / "baseline_inputs.csv",
            external_scores={
                "zero_shot_kronos": comparison_scores(zero_shot),
                "head_only": comparison_scores(head_only),
                "alpha158_lightgbm": comparison_scores(alpha158),
            },
            evaluate_split=evaluate_split,
            training_root=context.layout.root,
            output_path=artifact_root / "baseline_comparison.json",
            min_instruments=FORMAL_MIN_CROSS_SECTION,
            active_member_count_column="active_member_count",
            min_coverage_ratio=FORMAL_MIN_COVERAGE_RATIO,
            require_eligible_cross_section=True,
        )
        build_evaluation_companion(
            training_root=context.layout.root,
            sample_index_path=context.dataset_dir / "sample_index.csv",
            raw_market_source_path=_snapshot_directory(context),
            provider_uri=provider,
            suspensions_path=suspensions_path,
            price_limits_path=price_limits_path,
            external_score_artifacts={
                "zero_shot_score": zero_shot,
                "head_only_score": head_only,
                "alpha158_score": alpha158,
            },
            binding=binding,
            output_path=output,
            evaluate_split=evaluate_split,
        )
        inspect_evaluation_companion(
            output,
            context.layout.root,
            binding=binding,
            evaluate_split=evaluate_split,
        )
    return output


def _stable_execution_audit(
    companion_metadata: Mapping[str, Any],
    *,
    training_root: Path,
) -> dict[str, Any]:
    sources = companion_metadata.get("source_artifacts")
    if not isinstance(sources, Mapping) or not isinstance(sources.get("execution"), Mapping):
        raise CliContractError("evaluation companion 缺少 execution 审计来源")
    record = sources["execution"]
    if set(record) != {"path", "sha256"}:
        raise CliContractError("evaluation companion execution 来源记录无效")
    path = resolve_under(
        training_root,
        Path(str(record["path"])).resolve(strict=True),
    )
    if sha256_file(path) != record["sha256"]:
        raise CliContractError("evaluation companion execution 审计哈希漂移")
    audit = _json_file(path)
    stable = {key: value for key, value in audit.items() if key != "generated_at"}
    inner_sources = stable.get("source_artifacts")
    if not isinstance(inner_sources, Mapping):
        raise CliContractError("evaluation companion execution 内层来源无效")
    stable["source_artifacts"] = {
        name: source.get("sha256")
        for name, source in inner_sources.items()
        if name != "provider_manifest" and isinstance(source, Mapping)
    }
    return stable


def _assert_rebuilt_companion_matches(
    context: WorkflowContext,
    *,
    canonical_path: Path,
    rebuilt_path: Path,
    binding: Any,
    evaluate_split: str,
) -> None:
    from kronos_a_share_baseline import inspect_evaluation_companion

    canonical = resolve_under(context.layout.root, canonical_path.resolve(strict=True))
    rebuilt = resolve_under(context.layout.root, rebuilt_path.resolve(strict=True))
    canonical_metadata = inspect_evaluation_companion(
        canonical,
        context.layout.root,
        binding=binding,
        evaluate_split=evaluate_split,
    )
    rebuilt_metadata = inspect_evaluation_companion(
        rebuilt,
        context.layout.root,
        binding=binding,
        evaluate_split=evaluate_split,
    )
    if sha256_file(canonical) != sha256_file(rebuilt):
        raise CliContractError(
            "formal validation companion 与绑定源现场重建结果不一致"
        )
    stable_metadata_fields = (
        "schema_version",
        "row_count",
        "evaluate_split",
        "sample_id_sha256",
        "binding",
        "diagnostic_dataset_sha256",
        "holding_period_sessions",
        "execution_contract",
        "drift_contract",
    )
    for field in stable_metadata_fields:
        if canonical_metadata.get(field) != rebuilt_metadata.get(field):
            raise CliContractError(
                f"formal validation companion metadata 与现场重建不一致：{field}"
            )
    canonical_sources = canonical_metadata.get("source_artifacts")
    rebuilt_sources = rebuilt_metadata.get("source_artifacts")
    if not isinstance(canonical_sources, Mapping) or not isinstance(
        rebuilt_sources, Mapping
    ):
        raise CliContractError("formal validation companion source_artifacts 无效")
    for name in BASELINE_SCORE_COLUMNS:
        canonical_record = canonical_sources.get(name)
        rebuilt_record = rebuilt_sources.get(name)
        if (
            not isinstance(canonical_record, Mapping)
            or not isinstance(rebuilt_record, Mapping)
            or canonical_record.get("sha256") != rebuilt_record.get("sha256")
        ):
            raise CliContractError(
                f"formal validation companion 基线来源与现场重建不一致：{name}"
            )
    if _stable_execution_audit(
        canonical_metadata, training_root=context.layout.root
    ) != _stable_execution_audit(rebuilt_metadata, training_root=context.layout.root):
        raise CliContractError(
            "formal validation execution 审计与绑定源现场重建不一致"
        )


@contextmanager
def _formal_rebuilt_companion(
    context: WorkflowContext,
    *,
    binding: Any,
    canonical_path: Path,
    device: str,
    chunk_size: int,
):
    temp_root = resolve_under(
        context.layout.root,
        Path(getattr(context.layout, "tmp", context.predictions_dir / ".tmp"))
        / "formal-evaluation"
        / f"{context.run_id}-{os.getpid()}-{uuid.uuid4().hex}",
    )
    temp_root.mkdir(parents=True, exist_ok=False)
    rebuilt_path = temp_root / "validation_baselines.csv"
    try:
        rebuilt = _ensure_evaluation_companion(
            context,
            binding=binding,
            output_path=rebuilt_path,
            device=device,
            chunk_size=chunk_size,
            evaluate_split="validation",
            force_recompute_baselines=True,
        )
        _assert_rebuilt_companion_matches(
            context,
            canonical_path=canonical_path,
            rebuilt_path=rebuilt,
            binding=binding,
            evaluate_split="validation",
        )
        yield rebuilt
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def command_train_scorer(args: argparse.Namespace) -> dict[str, Any]:
    from kronos_a_share_training import CheckpointFileLock

    if bool(getattr(args, "engineering_smoke", False)):
        raise CliBlocked(
            "engineering smoke 只验证 adapter 工程链路，不训练 scorer 或输出 RankIC"
        )
    lock_context = build_context(
        args.config, create=True, variant=getattr(args, "_variant", None)
    )
    with CheckpointFileLock(_global_training_lock_path(lock_context)):
        return _command_train_scorer_impl(args)


def _command_train_scorer_impl(args: argparse.Namespace) -> dict[str, Any]:
    import torch
    from kronos_a_share_model import KronosScoringHead
    from kronos_a_share_training import (
        CheckpointFileLock,
        CheckpointStore,
        prepare_scorer_stage,
        set_deterministic_seed,
    )

    context = build_context(
        args.config, create=True, variant=getattr(args, "_variant", None)
    )
    data_report = _load_data_status(context)
    _assert_data_allowed(data_report["status"], engineering_smoke=args.engineering_smoke)
    cache = _load_cache(context)
    arrays = cache["arrays"]
    train_members = np.flatnonzero(np.asarray(arrays["split"]) == SPLIT_CODES["train"])
    valid_members = np.flatnonzero(
        np.asarray(arrays["split"]) == SPLIT_CODES["validation"]
    )
    seed = int(context.config["training"]["seed"])
    if seed != 100:
        raise CliContractError("正式 scorer checkpoint 必须固定使用 seed100")
    set_deterministic_seed(seed)
    components = _load_kronos_components(context, args.device)
    model = components.model
    head = KronosScoringHead(
        d_model=int(context.config["model"]["scorer"]["hidden_size"])
    ).to(components.device)
    if sum(parameter.numel() for parameter in head.parameters()) != 2_497:
        raise CliContractError("评分头参数数量不是 2497")
    settings = context.config["training"]["scorer"]
    optimizer = torch.optim.AdamW(
        head.parameters(),
        lr=float(settings["learning_rate"]),
        weight_decay=float(settings["weight_decay"]),
    )
    binding = _binding(context)
    store = CheckpointStore(context.checkpoint_dir, binding)
    adapter_reference = _stage_reference(
        store,
        stage="adapter",
        kind=args.adapter,
    )
    resume = _resume_reference(store, args.resume, "scorer")
    if resume is not None:
        resume_extra = _checkpoint_extra_state(store, resume)
        if resume_extra.get("adapter_checkpoint") != adapter_reference:
            if args.resume == "auto":
                resume = None
            else:
                raise CliContractError(
                    "scorer checkpoint 绑定的 adapter 与 --adapter 不一致"
                )
    start_epoch = 0
    checkpoint_step_base = max(
        (int(item["step"]) for item in _stage_manifests(store, "scorer")),
        default=0,
    )
    best_rank_ic = -math.inf
    best_epoch = 0
    stale_epochs = 0
    adapter_checkpoint: str
    if resume is not None:
        loaded = store.load(
            resume,
            model=model,
            optimizer=optimizer,
            scoring_head=head,
            restore_rng=True,
            map_location=components.device,
        )
        start_epoch = int(loaded.extra_state.get("scorer_epoch", loaded.step))
        checkpoint_step_base = loaded.step - start_epoch
        best_rank_ic = float(loaded.extra_state.get("best_validation_rank_ic", -math.inf))
        best_epoch = int(loaded.extra_state.get("best_epoch", 0))
        stale_epochs = int(loaded.extra_state.get("stale_epochs", 0))
        adapter_checkpoint = str(loaded.extra_state.get("adapter_checkpoint", ""))
    else:
        adapter_manifest = store.inspect(adapter_reference)
        if adapter_manifest["stage"] != "adapter":
            raise CliContractError("--adapter 必须引用 adapter checkpoint")
        store.load(
            adapter_reference,
            model=model,
            restore_rng=False,
            map_location=components.device,
        )
        adapter_checkpoint = adapter_manifest["checkpoint_name"]
        prepare_scorer_stage(model, head)
    bound_adapter_manifest = store.inspect(adapter_checkpoint)
    if bound_adapter_manifest.get("stage") != "adapter":
        raise CliContractError("scorer 绑定的 adapter checkpoint 阶段无效")
    adapter_state_hash = str(
        bound_adapter_manifest["files"]["state.pt"]["sha256"]
    )
    configured_max_epochs = int(settings["max_epochs"])
    if args.max_epochs is not None and int(args.max_epochs) != configured_max_epochs:
        raise CliContractError(
            "formal scorer --max-epochs 不得偏离固定配置；20-seed 必须使用同一完整训练合同"
        )
    max_epochs = _validated_formal_scorer_epochs(
        engineering_smoke=bool(args.engineering_smoke),
        requested=args.max_epochs,
        configured=configured_max_epochs,
    )
    if max_epochs < 1 or max_epochs > int(settings["max_epochs"]):
        raise CliContractError("max-epochs 必须位于 1..配置上限")
    if start_epoch >= max_epochs:
        existing_summary = context.metrics_dir / "scorer_summary.json"
        summary = _json_file(existing_summary) if existing_summary.is_file() else {
            "schema_version": "kronos-a-share-scorer-train-v1",
            "status": "unverified" if args.engineering_smoke else "ok",
            "run_id": context.run_id,
            "completed_epoch": start_epoch,
        }
        best_reference = _stage_reference(store, stage="scorer", kind="best")
        best_manifest = store.inspect(best_reference)
        observed_adapter, _, scorer_hash = _scorer_checkpoint_hashes(store, best_manifest)
        if observed_adapter != adapter_checkpoint:
            raise CliBlocked("scorer 复用证据绑定到不同 adapter checkpoint")
        _scorer_stability_evidence(
            context,
            checkpoint_reference=best_reference,
            scorer_checkpoint_hash=scorer_hash,
        )
        stability = summary.get("scorer_seed_stability")
        if (
            isinstance(stability, Mapping)
            and stability.get("seeds") == list(FORMAL_SCORER_SEEDS)
            and isinstance(stability.get("per_seed"), list)
            and len(stability["per_seed"]) == len(FORMAL_SCORER_SEEDS)
        ):
            return _envelope(
                "train-scorer",
                status=summary.get("status", "unverified"),
                message="scorer checkpoint 与20种子审计已完成，本次未重复训练。",
                training=summary,
                evidence_class="model_output",
                output_type="N/A",
            )
    train_groups = _date_index_groups(
        arrays, train_members, formal_cross_section=True
    )
    if not train_groups:
        raise CliContractError("训练集没有可比较的同日横截面")
    patience = int(settings["early_stopping_patience"])
    chunk_size = int(args.chunk_size)
    saved_path: Path | None = None
    last_train_loss = math.nan
    with CheckpointFileLock(context.checkpoint_dir / ".training.lock"):
        for epoch in range(start_epoch + 1, max_epochs + 1):
            order = np.random.default_rng(seed + epoch).permutation(len(train_groups))
            losses: list[float] = []
            for group_index in order:
                group = train_groups[int(group_index)]
                head.train()
                optimizer.zero_grad(set_to_none=True)
                scorer_loss, _ = _scorer_loss_for_date(
                    model,
                    head,
                    arrays,
                    group,
                    device=components.device,
                    chunk_size=chunk_size,
                    smooth_l1_weight=float(settings["smooth_l1_weight"]),
                    ranknet_weight=float(settings["ranknet_weight"]),
                )
                scorer_loss.total.backward()
                torch.nn.utils.clip_grad_norm_(head.parameters(), 3.0)
                optimizer.step()
                losses.append(float(scorer_loss.total.detach().cpu()))
            last_train_loss = float(np.mean(losses))
            validation_frame = _score_members(
                model,
                head,
                arrays,
                valid_members,
                device=components.device,
                chunk_size=chunk_size,
                formal_cross_section=True,
            )
            validation_rank_ic = _mean_rank_ic(
                validation_frame, formal_cross_section=True
            )
            is_best = validation_rank_ic > best_rank_ic
            if is_best:
                best_rank_ic = validation_rank_ic
                best_epoch = epoch
                stale_epochs = 0
            else:
                stale_epochs += 1
            prepare_scorer_stage(model, head)
            saved_path = store.save(
                stage="scorer",
                step=checkpoint_step_base + epoch,
                model=model,
                optimizer=optimizer,
                scoring_head=head,
                metric=validation_rank_ic,
                is_best=is_best,
                extra_state={
                    "run_id": context.run_id,
                    "adapter_checkpoint": adapter_checkpoint,
                    "adapter_hash": adapter_state_hash,
                    "scorer_epoch": epoch,
                    "best_validation_rank_ic": best_rank_ic,
                    "best_epoch": best_epoch,
                    "stale_epochs": stale_epochs,
                    "engineering_smoke": bool(args.engineering_smoke),
                    "training_max_epochs": configured_max_epochs,
                    "early_stopping_patience": patience,
                },
            )
            if stale_epochs >= patience:
                break
    best_reference = _stage_reference(store, stage="scorer", kind="best")
    best_manifest = store.inspect(best_reference)
    store.load(
        best_reference,
        model=model,
        scoring_head=head,
        restore_rng=False,
        map_location=components.device,
    )
    validation_frame = _score_members(
        model,
        head,
        arrays,
        valid_members,
        device=components.device,
        chunk_size=chunk_size,
        formal_cross_section=True,
    )
    scorer_state_hash = best_manifest["files"]["state.pt"]["sha256"]
    scorer_seed_stability = _scorer_seed_stability(
        context,
        model,
        arrays,
        train_members,
        valid_members,
        primary_validation_frame=validation_frame,
        binding=binding,
        adapter_checkpoint=adapter_checkpoint,
        adapter_hash=adapter_state_hash,
        evaluated_checkpoint=best_manifest["checkpoint_name"],
        scorer_checkpoint_hash=scorer_state_hash,
        settings=settings,
        max_epochs=max_epochs,
        device=components.device,
        chunk_size=chunk_size,
    )
    scorer_seed_stability_sha256 = _canonical_json_sha256(
        scorer_seed_stability
    )
    prediction_path = context.predictions_dir / "validation_predictions.csv"
    prediction_hash = _atomic_csv(
        prediction_path, validation_frame, context.layout.root
    )
    prediction_metadata_path = prediction_path.with_suffix(
        prediction_path.suffix + ".metadata.json"
    )
    prediction_metadata = {
        "schema_version": "kronos-a-share-controlled-predictions-v2",
        "prediction_contract": "live-checkpoint-recompute-required-v1",
        "run_id": context.run_id,
        "dataset_id": context.dataset_id,
        "evaluate_split": "validation",
        "binding": _gate_binding(binding),
        "evaluated_checkpoint": best_manifest["checkpoint_name"],
        "adapter_hash": adapter_state_hash,
        "scorer_checkpoint_hash": scorer_state_hash,
        "scorer_seed_stability_sha256": scorer_seed_stability_sha256,
        "prediction_sha256": prediction_hash,
        "row_count": int(len(validation_frame)),
        "sample_id_sha256": _sha256_bytes(
            validation_frame["sample_id"].to_numpy(dtype=np.int64).tobytes()
        ),
        "generated_at": _utc_now(),
    }
    atomic_write_json(
        prediction_metadata_path,
        prediction_metadata,
        allowed_root=context.layout.root,
    )
    summary = {
        "schema_version": "kronos-a-share-scorer-train-v1",
        "status": "unverified" if args.engineering_smoke else "ok",
        "data_status": data_report["status"],
        "run_id": context.run_id,
        "completed_epoch": int(best_manifest["step"]),
        "best_validation_rank_ic": best_rank_ic,
        "scorer_seed_stability": scorer_seed_stability,
        "scorer_seed_stability_sha256": scorer_seed_stability_sha256,
        "last_train_loss": last_train_loss,
        "adapter_checkpoint": adapter_checkpoint,
        "evaluated_checkpoint": best_manifest["checkpoint_name"],
        "adapter_hash": adapter_state_hash,
        "scorer_checkpoint_hash": scorer_state_hash,
        "predictions": str(prediction_path),
        "predictions_metadata": str(prediction_metadata_path),
        "generated_at": _utc_now(),
    }
    atomic_write_json(
        context.metrics_dir / "scorer_summary.json",
        summary,
        allowed_root=context.layout.root,
    )
    return _envelope(
        "train-scorer",
        status=summary["status"],
        message=(
            "评分头工程训练完成；仍需独立基线、成本与 bootstrap 准出。"
            if args.engineering_smoke
            else "横截面评分头训练完成。"
        ),
        training=summary,
        evidence_class="model_output",
        output_type="N/A",
    )


def _gate_binding(binding: Any) -> dict[str, str]:
    values = binding.as_dict()
    return {
        "base_model_sha256": values["base_model_sha256"],
        "tokenizer_sha256": values["tokenizer_sha256"],
        "data_sha256": values["dataset_sha256"],
        "config_sha256": values["config_sha256"],
    }


_GATE_HEAD_CORE_FIELDS = (
    "schema_version",
    "sequence",
    "gate_sha256",
    "gate_receipt_sha256",
    "previous_event_sha256",
    "created_at",
)


def _gate_head_event_sha256(event: Mapping[str, Any]) -> str:
    try:
        core = {field: event[field] for field in _GATE_HEAD_CORE_FIELDS}
    except KeyError as exc:
        raise CliBlocked("gate lineage event 缺少字段") from exc
    return _canonical_json_sha256(core)


def _read_gate_lineage(
    context: WorkflowContext,
    *,
    require_active_head: bool,
) -> list[dict[str, Any]]:
    lineage_dir = context.checkpoint_dir / "gate-lineage"
    head_path = context.checkpoint_dir / "gate-head.json"
    if not lineage_dir.is_dir():
        if require_active_head and head_path.exists():
            raise CliBlocked("active gate head 缺少不可变 lineage")
        return []
    files = sorted(lineage_dir.glob("*.json"))
    if not files:
        raise CliBlocked("gate-lineage 目录为空")
    events: list[dict[str, Any]] = []
    previous_hash: str | None = None
    expected_fields = {*_GATE_HEAD_CORE_FIELDS, "event_sha256"}
    for expected_sequence, path in enumerate(files, start=1):
        event = _json_file(path)
        if set(event) != expected_fields:
            raise CliBlocked("gate lineage event 字段不匹配")
        sequence = event.get("sequence")
        if (
            isinstance(sequence, bool)
            or not isinstance(sequence, int)
            or sequence != expected_sequence
        ):
            raise CliBlocked("gate lineage sequence 不连续")
        if event.get("schema_version") != GATE_HEAD_SCHEMA_VERSION:
            raise CliBlocked("gate lineage schema_version 不匹配")
        if event.get("previous_event_sha256") != previous_hash:
            raise CliBlocked("gate lineage previous hash 断链")
        event_hash = _gate_head_event_sha256(event)
        if event.get("event_sha256") != event_hash:
            raise CliBlocked("gate lineage event hash 不匹配")
        expected_name = f"{expected_sequence:08d}-{event_hash}.json"
        if path.name != expected_name:
            raise CliBlocked("gate lineage 文件名与 event hash 不匹配")
        gate_hash = event.get("gate_sha256")
        receipt_hash = event.get("gate_receipt_sha256")
        if not isinstance(gate_hash, str) or len(gate_hash) != 64:
            raise CliBlocked("gate lineage gate_sha256 无效")
        if not isinstance(receipt_hash, str) or len(receipt_hash) != 64:
            raise CliBlocked("gate lineage receipt sha256 无效")
        receipt_path = context.checkpoint_dir / "gate-receipts" / f"{gate_hash}.json"
        if not receipt_path.is_file() or sha256_file(receipt_path) != receipt_hash:
            raise CliBlocked("gate lineage 对应 release receipt 缺失或漂移")
        receipt = _json_file(receipt_path)
        if (
            receipt.get("schema_version") != GATE_RECEIPT_SCHEMA_VERSION
            or receipt.get("gate_sha256") != gate_hash
            or receipt.get("gate_sequence") != expected_sequence
        ):
            raise CliBlocked("gate lineage 与 release receipt 语义不匹配")
        events.append(event)
        previous_hash = event_hash
    if require_active_head:
        if not head_path.is_file():
            raise CliBlocked("缺少 active gate head")
        head = _json_file(head_path)
        if head != events[-1]:
            raise CliBlocked("active gate head 不是最新不可变 lineage event")
    return events


def _write_gate_unlocked(
    context: WorkflowContext,
    *,
    binding: Any,
    gate_status: str,
    adapter_hash: str | None,
    scorer_checkpoint_hash: str | None,
    evaluated_checkpoint: str | None,
    reasons: Sequence[str],
    verification_status: str,
    research_scoring_allowed: bool = False,
    forward_observation: Mapping[str, Any] | None = None,
    metrics: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    lineage = _read_gate_lineage(context, require_active_head=False)
    gate_sequence = len(lineage) + 1
    previous_event_sha256 = lineage[-1]["event_sha256"] if lineage else None
    if gate_status not in {"passed", "blocked"}:
        raise CliContractError("gate_status 必须为 passed 或 blocked")
    if gate_status == "passed" or research_scoring_allowed:
        for field, value in (
            ("adapter_hash", adapter_hash),
            ("scorer_checkpoint_hash", scorer_checkpoint_hash),
        ):
            if not isinstance(value, str) or len(value) != 64:
                raise CliContractError(f"可评分 gate 必须绑定64位 {field}")
        if not evaluated_checkpoint:
            raise CliContractError("可评分 gate 必须绑定 evaluated_checkpoint")
    if gate_status == "passed" and research_scoring_allowed:
        raise CliContractError("passed gate 不应再标记 research_scoring_allowed")
    gate = {
        "schema_version": GATE_SCHEMA_VERSION,
        "gate_sequence": gate_sequence,
        "gate_status": gate_status,
        "run_id": context.run_id,
        "binding": _gate_binding(binding),
        "adapter_hash": adapter_hash,
        "scorer_checkpoint_hash": scorer_checkpoint_hash,
        "evaluated_checkpoint": evaluated_checkpoint,
        "generated_at": _utc_now(),
        "verification_status": verification_status,
        "evidence_class": "model_output",
        "output_type": "model_output" if gate_status == "passed" else "N/A",
        "research_scoring_allowed": bool(research_scoring_allowed),
        "forward_observation": dict(forward_observation or {}),
        "reasons": list(reasons),
        "metrics": dict(metrics or {}),
    }
    atomic_write_json(
        context.checkpoint_dir / "gate.json",
        gate,
        allowed_root=context.layout.root,
    )
    gate_path = context.checkpoint_dir / "gate.json"
    gate_hash = sha256_file(gate_path)
    receipt = {
        "schema_version": GATE_RECEIPT_SCHEMA_VERSION,
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
        "gate_sequence": gate_sequence,
    }
    receipt_path = (
        context.checkpoint_dir / "gate-receipts" / f"{gate_hash}.json"
    )
    if receipt_path.is_file():
        if _json_file(receipt_path) != receipt:
            raise CliContractError("不可变 gate receipt 内容冲突")
    else:
        atomic_write_json(
            receipt_path,
            receipt,
            allowed_root=context.layout.root,
        )
    event = {
        "schema_version": GATE_HEAD_SCHEMA_VERSION,
        "sequence": gate_sequence,
        "gate_sha256": gate_hash,
        "gate_receipt_sha256": sha256_file(receipt_path),
        "previous_event_sha256": previous_event_sha256,
        "created_at": _utc_now(),
    }
    event["event_sha256"] = _gate_head_event_sha256(event)
    event_path = (
        context.checkpoint_dir
        / "gate-lineage"
        / f"{gate_sequence:08d}-{event['event_sha256']}.json"
    )
    if event_path.is_file():
        if _json_file(event_path) != event:
            raise CliContractError("不可变 gate lineage event 内容冲突")
    else:
        atomic_write_json(
            event_path,
            event,
            allowed_root=context.layout.root,
        )
    atomic_write_json(
        context.checkpoint_dir / "gate-head.json",
        event,
        allowed_root=context.layout.root,
    )
    return gate


def _write_gate(
    context: WorkflowContext,
    *,
    binding: Any,
    gate_status: str,
    adapter_hash: str | None,
    scorer_checkpoint_hash: str | None,
    evaluated_checkpoint: str | None,
    reasons: Sequence[str],
    verification_status: str,
    research_scoring_allowed: bool = False,
    forward_observation: Mapping[str, Any] | None = None,
    metrics: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    from kronos_a_share_training import CheckpointFileLock

    with CheckpointFileLock(context.checkpoint_dir / ".gate-write.lock"):
        return _write_gate_unlocked(
            context,
            binding=binding,
            gate_status=gate_status,
            adapter_hash=adapter_hash,
            scorer_checkpoint_hash=scorer_checkpoint_hash,
            evaluated_checkpoint=evaluated_checkpoint,
            reasons=reasons,
            verification_status=verification_status,
            research_scoring_allowed=research_scoring_allowed,
            forward_observation=forward_observation,
            metrics=metrics,
        )


BASELINE_SCORE_COLUMNS = (
    "zero_shot_score",
    "head_only_score",
    "last_value_score",
    "drift_score",
    "momentum_score",
    "reversal_score",
    "alpha158_score",
)


def _recompute_scorer_predictions(
    context: WorkflowContext,
    *,
    store: Any,
    checkpoint_reference: str,
    split: str,
    device: str,
    chunk_size: int,
) -> pd.DataFrame:
    """Recreate scores from the committed scorer instead of trusting CSVs."""

    from kronos_a_share_model import KronosScoringHead
    from kronos_a_share_training import prepare_scorer_stage, set_deterministic_seed

    if split not in SPLIT_CODES:
        raise CliContractError(f"评估 split 无效：{split}")
    if chunk_size < 1:
        raise CliContractError("chunk-size 必须为正整数")
    arrays = _load_cache(context)["arrays"]
    members = np.flatnonzero(
        np.asarray(arrays["split"]) == SPLIT_CODES[split]
    ).astype(np.int64)
    if not len(members):
        raise CliContractError(f"{split} split 没有可评估样本")
    set_deterministic_seed(int(context.config["training"]["seed"]) + 30_001)
    components = _load_kronos_components(context, device)
    head = KronosScoringHead(
        d_model=int(context.config["model"]["scorer"]["hidden_size"])
    ).to(components.device)
    loaded = store.load(
        checkpoint_reference,
        model=components.model,
        scoring_head=head,
        restore_rng=False,
        map_location=components.device,
    )
    if loaded.stage != "scorer":
        raise CliContractError("重算预测必须使用 scorer checkpoint")
    prepare_scorer_stage(components.model, head)
    components.model.eval()
    head.eval()
    return _score_members(
        components.model,
        head,
        arrays,
        members,
        device=components.device,
        chunk_size=chunk_size,
        formal_cross_section=True,
    )


def _controlled_prediction_path(context: WorkflowContext, split: str) -> Path:
    return context.predictions_dir / f"{split}_predictions.csv"


def _materialize_non_gate_predictions(
    context: WorkflowContext,
    *,
    binding: Any,
    checkpoint: Mapping[str, Any],
    adapter_hash: str,
    scorer_checkpoint_hash: str,
    split: str,
    frame: pd.DataFrame,
) -> Path:
    if split == "validation":
        return _controlled_prediction_path(context, split)
    path = _controlled_prediction_path(context, split)
    metadata_path = path.with_suffix(path.suffix + ".metadata.json")
    if path.is_file() or metadata_path.is_file():
        if not path.is_file() or not metadata_path.is_file():
            raise CliContractError(f"{split} controlled predictions 工件不完整")
        return path
    prediction_hash = _atomic_csv(path, frame, context.layout.root)
    metadata = {
        "schema_version": "kronos-a-share-controlled-predictions-v2",
        "prediction_contract": "live-checkpoint-recompute-required-v1",
        "run_id": context.run_id,
        "dataset_id": context.dataset_id,
        "evaluate_split": split,
        "binding": _gate_binding(binding),
        "evaluated_checkpoint": checkpoint["checkpoint_name"],
        "adapter_hash": adapter_hash,
        "scorer_checkpoint_hash": scorer_checkpoint_hash,
        "prediction_sha256": prediction_hash,
        "row_count": int(len(frame)),
        "sample_id_sha256": _sha256_bytes(
            frame["sample_id"].to_numpy(dtype=np.int64).tobytes()
        ),
        "generated_at": _utc_now(),
    }
    atomic_write_json(metadata_path, metadata, allowed_root=context.layout.root)
    return path


def _controlled_evaluation_frame(
    context: WorkflowContext,
    *,
    binding: Any,
    checkpoint: Mapping[str, Any],
    adapter_hash: str,
    scorer_checkpoint_hash: str,
    companion_path: Path,
    live_predictions: pd.DataFrame,
    evaluate_split: str = "validation",
) -> pd.DataFrame:
    prediction_path = _controlled_prediction_path(context, evaluate_split)
    metadata_path = prediction_path.with_suffix(prediction_path.suffix + ".metadata.json")
    if not prediction_path.is_file() or not metadata_path.is_file():
        raise CliContractError("缺少 train-scorer 受控生成的 validation predictions")
    metadata = _json_file(metadata_path)
    expected = {
        "schema_version": "kronos-a-share-controlled-predictions-v2",
        "prediction_contract": "live-checkpoint-recompute-required-v1",
        "run_id": context.run_id,
        "dataset_id": context.dataset_id,
        "evaluate_split": evaluate_split,
        "binding": _gate_binding(binding),
        "evaluated_checkpoint": checkpoint["checkpoint_name"],
        "adapter_hash": adapter_hash,
        "scorer_checkpoint_hash": scorer_checkpoint_hash,
        "prediction_sha256": sha256_file(prediction_path),
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise CliContractError(f"受控 predictions provenance 不匹配：{key}")
    controlled = pd.read_csv(prediction_path)
    required_controlled = {
        "sample_id",
        "trade_date",
        "instrument_id",
        "active_member_count",
        "raw_score",
        "label_excess_10d",
    }
    missing = sorted(required_controlled - set(controlled.columns))
    if missing or controlled["sample_id"].duplicated().any():
        raise CliContractError(f"受控 predictions 主键或字段无效：missing={missing}")
    if len(controlled) != metadata.get("row_count"):
        raise CliContractError("受控 predictions 行数漂移")
    ids = pd.to_numeric(controlled["sample_id"], errors="raise").to_numpy(dtype=np.int64)
    if _sha256_bytes(ids.tobytes()) != metadata.get("sample_id_sha256"):
        raise CliContractError("受控 predictions sample_id 哈希漂移")
    cache = _load_cache(context)
    arrays = cache["arrays"]
    if len(ids) == 0 or ids.min() < 0 or ids.max() >= len(arrays["label"]):
        raise CliContractError("受控 predictions sample_id 越界")
    expected_split = np.asarray(arrays["split"][ids])
    if not np.all(expected_split == SPLIT_CODES[evaluate_split]):
        raise CliContractError(f"受控 predictions 混入非 {evaluate_split} 样本")
    if not np.allclose(
        pd.to_numeric(controlled["label_excess_10d"], errors="raise"),
        np.asarray(arrays["label"][ids]),
        rtol=0,
        atol=1e-6,
    ):
        raise CliContractError("受控 predictions label 与 token cache 不一致")
    controlled_dates = pd.to_datetime(
        controlled["trade_date"], errors="raise"
    ).dt.strftime("%Y%m%d").astype(np.int32)
    if not np.array_equal(controlled_dates, np.asarray(arrays["trade_date"][ids])):
        raise CliContractError("受控 predictions trade_date 与 token cache 不一致")
    if not np.array_equal(
        pd.to_numeric(controlled["instrument_id"], errors="raise").to_numpy(
            dtype=np.int32
        ),
        np.asarray(arrays["instrument_id"][ids]),
    ):
        raise CliContractError("受控 predictions instrument_id 与 token cache 不一致")
    if not np.array_equal(
        pd.to_numeric(controlled["active_member_count"], errors="raise").to_numpy(
            dtype=np.int32
        ),
        np.asarray(arrays["active_member_count"][ids]),
    ):
        raise CliContractError("受控 predictions active_member_count 与 token cache 不一致")
    live = live_predictions.copy()
    if set(live.columns) != required_controlled or len(live) != len(controlled):
        raise CliContractError("实时 checkpoint 重算 predictions 列/行合同不匹配")
    live_ids = pd.to_numeric(live["sample_id"], errors="raise").to_numpy(dtype=np.int64)
    if not np.array_equal(live_ids, ids):
        raise CliContractError("受控 predictions 与 checkpoint 重算 sample_id 不一致")
    for column in ("trade_date", "instrument_id", "active_member_count"):
        left = controlled[column].astype(str).to_numpy()
        right = live[column].astype(str).to_numpy()
        if not np.array_equal(left, right):
            raise CliContractError(f"受控 predictions 与 checkpoint 重算 {column} 不一致")
    if not np.allclose(
        pd.to_numeric(controlled["label_excess_10d"], errors="raise"),
        pd.to_numeric(live["label_excess_10d"], errors="raise"),
        rtol=0,
        atol=1e-6,
    ):
        raise CliContractError("受控 predictions 与 checkpoint 重算 label 不一致")
    if not np.allclose(
        pd.to_numeric(controlled["raw_score"], errors="raise"),
        pd.to_numeric(live["raw_score"], errors="raise"),
        rtol=1e-7,
        atol=1e-7,
    ):
        raise CliContractError("受控 predictions raw_score 与 checkpoint 实时重算不一致")
    controlled = live

    companion = resolve_under(context.layout.root, companion_path.resolve(strict=True))
    companion_metadata_path = companion.with_suffix(companion.suffix + ".metadata.json")
    if not companion_metadata_path.is_file():
        raise CliContractError("基线/成交 companion 缺少 metadata.json")
    companion_metadata = _json_file(companion_metadata_path)
    if companion_metadata.get("schema_version") != "kronos-a-share-baseline-bundle-v3":
        raise CliContractError("基线 companion schema_version 不匹配")
    if companion_metadata.get("input_sha256") != sha256_file(companion):
        raise CliContractError("基线 companion 输入哈希不匹配")
    if companion_metadata.get("binding") != _gate_binding(binding):
        raise CliContractError("基线 companion 数据/配置 binding 不匹配")
    if companion_metadata.get("evaluate_split") != evaluate_split:
        raise CliContractError(
            "基线 companion evaluate_split 不匹配："
            f"expected={evaluate_split}, actual={companion_metadata.get('evaluate_split')}"
        )
    if companion_metadata.get("sample_id_sha256") != metadata.get("sample_id_sha256"):
        raise CliContractError("基线 companion sample_id 哈希不匹配")
    source_artifacts = companion_metadata.get("source_artifacts")
    required_sources = {"execution", *BASELINE_SCORE_COLUMNS}
    if not isinstance(source_artifacts, dict) or not required_sources.issubset(
        source_artifacts
    ):
        raise CliContractError("基线 companion 缺少逐基线来源工件记录")
    for source_name in sorted(required_sources):
        record = source_artifacts[source_name]
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise CliContractError(f"基线来源记录格式无效：{source_name}")
        source_path = resolve_under(
            context.layout.root,
            Path(str(record["path"])).resolve(strict=True),
        )
        if sha256_file(source_path) != record["sha256"]:
            raise CliContractError(f"基线来源工件哈希不匹配：{source_name}")
    supplemental = pd.read_csv(companion)
    required_supplemental = {
        "sample_id",
        "entry_date",
        "exit_date",
        "entry_price_raw",
        "exit_price_raw",
        "entry_tradable",
        "exit_tradable",
        "entry_limit_blocked",
        "exit_limit_blocked",
        "stamp_duty_rate",
        "corporate_action_factor",
        "corporate_action_event_count",
        "holding_period_sessions",
        "active_member_count",
        *BASELINE_SCORE_COLUMNS,
    }
    missing = sorted(required_supplemental - set(supplemental.columns))
    forbidden = (
        required_controlled - {"sample_id", "active_member_count"}
    ) & set(supplemental.columns)
    if missing or forbidden or supplemental["sample_id"].duplicated().any():
        raise CliContractError(
            f"基线 companion 字段无效：missing={missing}, forbidden={sorted(forbidden)}"
        )
    supplemental_ids = pd.to_numeric(
        supplemental["sample_id"], errors="raise"
    ).to_numpy(dtype=np.int64)
    if not np.array_equal(supplemental_ids, ids):
        raise CliContractError("基线 companion 必须与受控 predictions 同序、全量一一对应")
    if not np.array_equal(
        pd.to_numeric(supplemental["active_member_count"], errors="raise").to_numpy(
            dtype=np.int32
        ),
        pd.to_numeric(controlled["active_member_count"], errors="raise").to_numpy(
            dtype=np.int32
        ),
    ):
        raise CliContractError("companion active_member_count 与受控 predictions 不一致")
    supplemental = supplemental.drop(columns=["active_member_count"])
    return controlled.merge(supplemental, on="sample_id", how="inner", validate="one_to_one")


def _evaluation_metrics(
    context: WorkflowContext,
    frame: pd.DataFrame,
    *,
    expected_adapter_reference: str,
    expected_adapter_hash: str,
    adapter_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    required = {
        "trade_date",
        "active_member_count",
        "raw_score",
        "label_excess_10d",
        "entry_price_raw",
        "exit_price_raw",
        *BASELINE_SCORE_COLUMNS,
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise CliContractError(f"正式评估输入缺少字段：{missing}")
    rank_ic_kwargs = {
        "min_instruments": FORMAL_MIN_CROSS_SECTION,
        "active_member_count_column": "active_member_count",
        "min_coverage_ratio": FORMAL_MIN_COVERAGE_RATIO,
        "require_eligible_cross_section": True,
    }
    model_daily = daily_rank_ic(frame, **rank_ic_kwargs)
    validation_rank_ic = _mean_rank_ic(frame, formal_cross_section=True)
    baseline_daily: dict[str, pd.DataFrame] = {}
    baseline_means: dict[str, float] = {}
    for column in BASELINE_SCORE_COLUMNS:
        daily = daily_rank_ic(frame, score_column=column, **rank_ic_kwargs)
        values = pd.to_numeric(daily["rank_ic"], errors="coerce")
        finite = values[np.isfinite(values)]
        if finite.empty:
            if column != "last_value_score":
                raise CliContractError(f"基线 {column} 没有可计算的日 RankIC")
            # A literal last-value forecast has zero return for every security,
            # so cross-sectional Spearman is mathematically undefined. Treat it
            # as the explicit zero-information benchmark, not as missing data.
            daily = daily.copy()
            daily["rank_ic"] = 0.0
            finite = daily["rank_ic"]
        baseline_daily[column] = daily
        baseline_means[column] = float(finite.mean())
    strongest_name = max(baseline_means, key=baseline_means.get)
    strongest_rank_ic = baseline_means[strongest_name]
    bootstrap = monthly_block_bootstrap_difference(
        model_daily,
        baseline_daily[strongest_name],
        iterations=int(context.config["evaluation"]["bootstrap_iterations"]),
        seed=int(context.config["training"]["seed"]),
    )
    quarterly = quarterly_rank_ic_summary(model_daily)
    base_cost = top_quantile_return_after_cost(
        frame,
        cost_bps=Decimal(str(context.config["evaluation"]["base_round_trip_cost_bps"])),
    )
    stress_cost = top_quantile_return_after_cost(
        frame,
        cost_bps=Decimal(str(context.config["evaluation"]["stress_round_trip_cost_bps"])),
    )
    if adapter_evidence is None:
        adapter_evidence = _adapter_checkpoint_release_metrics(
            context,
            reference=expected_adapter_reference,
            expected_hash=expected_adapter_hash,
        )
    return {
        "adapter_ce_improvement": adapter_evidence["adapter_ce_improvement"],
        "validation_rank_ic": validation_rank_ic,
        "zero_shot_rank_ic": baseline_means["zero_shot_score"],
        "head_only_rank_ic": baseline_means["head_only_score"],
        "positive_quarter_fraction": float(quarterly["positive_fraction"]),
        "bootstrap_ci95_lower": float(bootstrap["ci95_lower"]),
        "base_after_cost_return": float(base_cost["mean_return_after_cost"]),
        "stress_after_cost_return": float(stress_cost["mean_return_after_cost"]),
        "strongest_baseline": strongest_name,
        "strongest_baseline_rank_ic": strongest_rank_ic,
        "strongest_baseline_lift": validation_rank_ic - strongest_rank_ic,
        "baseline_rank_ic": baseline_means,
        "quarterly": quarterly,
        "bootstrap": bootstrap,
        "base_cost": base_cost,
        "stress_cost": stress_cost,
        "adapter_checkpoint_evidence": adapter_evidence,
    }


def _adapter_diagnostic_matrix_evidence(
    context: WorkflowContext,
    *,
    production_reference: str,
    production_hash: str,
) -> dict[str, Any]:
    """Verify the fixed LR x seed adapter diagnostic and its immutable receipt."""

    release_bound = bool(production_reference or production_hash)
    if bool(production_reference) != bool(production_hash):
        raise CliContractError("adapter diagnostic release binding 必须同时提供 checkpoint 与哈希")
    if release_bound and (
        not str(production_reference).startswith("adapter-step-")
        or len(str(production_hash)) != 64
    ):
        raise CliContractError("adapter diagnostic release binding 的正式 checkpoint 无效")
    matrix_path = context.metrics_dir / "adapter_diagnostic_matrix.json"
    receipt_path = context.metrics_dir / "adapter_diagnostic_matrix.receipt.json"
    if not matrix_path.is_file() or not receipt_path.is_file():
        raise CliContractError("adapter formal release 缺少 LR×seed 诊断矩阵或收据")
    matrix = _json_file(matrix_path)
    receipt = _json_file(receipt_path)
    matrix_fields = {
        "schema_version",
        "binding",
        "diagnostic_dataset_sha256",
        "learning_rates",
        "seeds",
        "selection_policy",
        "minimum_mean_ce_improvement",
        "maximum_single_run_ce_regression",
        "selected_learning_rate",
        "production_seed",
        "runs",
        "payload_sha256",
    }
    receipt_fields = {
        "schema_version",
        "matrix_sha256",
        "matrix_payload_sha256",
        "binding",
        "diagnostic_dataset_sha256",
        "selected_learning_rate",
        "production_seed",
        "payload_sha256",
    }
    if set(matrix) != matrix_fields or set(receipt) != receipt_fields:
        raise CliContractError("adapter LR×seed 诊断矩阵或收据字段不符合固定合同")
    matrix_unsigned = {key: value for key, value in matrix.items() if key != "payload_sha256"}
    receipt_unsigned = {
        key: value for key, value in receipt.items() if key != "payload_sha256"
    }
    matrix_payload_sha256 = _canonical_json_sha256(matrix_unsigned)
    if matrix.get("payload_sha256") != matrix_payload_sha256:
        raise CliContractError("adapter LR×seed 诊断矩阵 payload 哈希漂移")
    if receipt.get("payload_sha256") != _canonical_json_sha256(receipt_unsigned):
        raise CliContractError("adapter LR×seed 诊断收据 payload 哈希漂移")
    current_binding = _gate_binding(_binding(context))
    smoke_dataset_id = validate_identifier(
        f"{context.config['data']['dataset_id']}{SMOKE_NAMESPACE_SUFFIX}",
        "dataset_id",
    )
    smoke_context = SimpleNamespace(
        config=context.config,
        layout=context.layout,
        dataset_id=smoke_dataset_id,
        dataset_dir=resolve_under(
            context.layout.data, Path("datasets") / smoke_dataset_id
        ),
        token_dir=resolve_under(
            context.layout.data, Path("tokens") / smoke_dataset_id
        ),
    )
    live_diagnostic_dataset_sha256 = _dataset_hash(smoke_context)
    production_lr = float(context.config["training"]["adapter"]["learning_rate"])
    production_seed = int(context.config["training"]["seed"])
    expected_lrs = list(FORMAL_ADAPTER_DIAGNOSTIC_LRS)
    expected_seeds = list(FORMAL_ADAPTER_DIAGNOSTIC_SEEDS)
    matrix_sha256 = sha256_file(matrix_path)
    if (
        matrix.get("schema_version") != ADAPTER_DIAGNOSTIC_MATRIX_SCHEMA
        or matrix.get("binding") != current_binding
        or not isinstance(matrix.get("diagnostic_dataset_sha256"), str)
        or len(matrix.get("diagnostic_dataset_sha256", "")) != 64
        or matrix.get("diagnostic_dataset_sha256")
        != live_diagnostic_dataset_sha256
        or matrix.get("learning_rates") != expected_lrs
        or matrix.get("seeds") != expected_seeds
        or matrix.get("selection_policy")
        != "seed100_min_best_ce_with_1e-4_lower_lr_tiebreak"
        or not math.isclose(
            float(matrix.get("minimum_mean_ce_improvement", math.nan)),
            0.01,
            rel_tol=0,
            abs_tol=1e-12,
        )
        or not math.isclose(
            float(matrix.get("maximum_single_run_ce_regression", math.nan)),
            0.01,
            rel_tol=0,
            abs_tol=1e-12,
        )
        or not math.isclose(
            float(matrix.get("selected_learning_rate", math.nan)),
            production_lr,
            rel_tol=0,
            abs_tol=1e-15,
        )
        or int(matrix.get("production_seed", -1)) != production_seed
        or receipt.get("schema_version") != ADAPTER_DIAGNOSTIC_RECEIPT_SCHEMA
        or receipt.get("matrix_sha256") != matrix_sha256
        or receipt.get("matrix_payload_sha256") != matrix_payload_sha256
        or receipt.get("binding") != current_binding
        or receipt.get("diagnostic_dataset_sha256")
        != matrix.get("diagnostic_dataset_sha256")
        or not math.isclose(
            float(receipt.get("selected_learning_rate", math.nan)),
            production_lr,
            rel_tol=0,
            abs_tol=1e-15,
        )
        or int(receipt.get("production_seed", -1)) != production_seed
    ):
        raise CliContractError("adapter LR×seed 诊断矩阵未绑定当前生产 adapter")

    run_fields = {
        "learning_rate",
        "seed",
        "resolved_config_path",
        "resolved_config_file_sha256",
        "resolved_config_sha256",
        "checkpoint_path",
        "checkpoint_manifest_sha256",
        "checkpoint_state_sha256",
        "summary_path",
        "summary_sha256",
        "sample_manifest_path",
        "sample_manifest_sha256",
        "total_sample_count",
        "zero_shot_validation_ce",
        "best_validation_ce",
        "adapter_ce_improvement",
        "completed_step",
        "early_stopped",
    }
    runs = matrix.get("runs")
    if not isinstance(runs, list) or len(runs) != 5:
        raise CliContractError("adapter LR×seed 诊断矩阵必须包含唯一 5 次运行")
    seen: set[tuple[float, int]] = set()
    improvements: dict[float, list[float]] = {lr: [] for lr in expected_lrs}
    artifact_commitments: list[dict[str, Any]] = []
    binding_values = _binding(context).as_dict()
    for run in runs:
        if not isinstance(run, Mapping) or set(run) != run_fields:
            raise CliContractError("adapter LR×seed 单次运行字段不符合固定合同")
        lr = float(run.get("learning_rate", math.nan))
        seed = int(run.get("seed", -1))
        key = (lr, seed)
        if lr not in expected_lrs or seed not in expected_seeds or key in seen:
            raise CliContractError("adapter LR×seed 诊断矩阵组合缺失、重复或越界")
        seen.add(key)
        config_path = resolve_under(
            context.layout.root, str(run["resolved_config_path"]), must_exist=True
        )
        checkpoint_path = resolve_under(
            context.layout.root, str(run["checkpoint_path"]), must_exist=True
        )
        if not config_path.is_file() or not checkpoint_path.is_dir():
            raise CliContractError("adapter LR×seed 运行工件类型无效")
        resolved = _json_file(config_path)
        resolved_hash = str(run["resolved_config_sha256"])
        if (
            sha256_file(config_path) != run["resolved_config_file_sha256"]
            or resolved.get("schema_version")
            != "kronos-a-share-resolved-training-v1"
            or resolved.get("profile") != "engineering_smoke"
            or resolved.get("resolved_config_sha256") != resolved_hash
            or int(resolved.get("seed", -1)) != seed
            or not math.isclose(
                float(resolved.get("adapter", {}).get("learning_rate", math.nan)),
                lr,
                rel_tol=0,
                abs_tol=1e-15,
            )
        ):
            raise CliContractError("adapter LR×seed resolved config 证据不一致")
        manifest_path = checkpoint_path / "manifest.json"
        committed_path = checkpoint_path / "COMMITTED"
        state_path = checkpoint_path / "state.pt"
        summary_path = resolve_under(
            context.layout.root, str(run["summary_path"]), must_exist=True
        )
        sample_manifest_path = resolve_under(
            context.layout.root, str(run["sample_manifest_path"]), must_exist=True
        )
        if not all(path.is_file() for path in (manifest_path, committed_path, state_path)):
            raise CliContractError("adapter LR×seed checkpoint 工件不完整")
        if not summary_path.is_file() or sha256_file(summary_path) != run["summary_sha256"]:
            raise CliContractError("adapter LR×seed summary 哈希不一致")
        trial_summary = _json_file(summary_path)
        sample_manifest = _json_file(sample_manifest_path)
        manifest = _json_file(manifest_path)
        committed = _json_file(committed_path)
        manifest_sha256 = sha256_file(manifest_path)
        state_sha256 = sha256_file(state_path)
        trial_binding = manifest.get("binding", {})
        if (
            manifest_sha256 != run["checkpoint_manifest_sha256"]
            or state_sha256 != run["checkpoint_state_sha256"]
            or committed.get("manifest_sha256") != manifest_sha256
            or committed.get("checkpoint_name") != checkpoint_path.name
            or manifest.get("checkpoint_name") != checkpoint_path.name
            or manifest.get("stage") != "adapter"
            or manifest.get("files", {}).get("state.pt", {}).get("sha256")
            != state_sha256
            or trial_binding.get("base_model_sha256")
            != binding_values["base_model_sha256"]
            or trial_binding.get("tokenizer_sha256")
            != binding_values["tokenizer_sha256"]
            or trial_binding.get("dataset_sha256")
            != matrix.get("diagnostic_dataset_sha256")
            or trial_binding.get("config_sha256") != resolved_hash
        ):
            raise CliContractError("adapter LR×seed checkpoint 哈希或绑定不一致")
        zero = float(run.get("zero_shot_validation_ce", math.nan))
        best = float(run.get("best_validation_ce", math.nan))
        improvement = float(run.get("adapter_ce_improvement", math.nan))
        completed_step = int(run.get("completed_step", -1))
        early_stopped = run.get("early_stopped")
        trial_history = trial_summary.get("validation_history")
        if not isinstance(trial_history, list) or not trial_history:
            raise CliContractError("adapter LR×seed summary 缺少 validation_history")
        history_rows = sorted(
            trial_history, key=lambda value: int(value.get("step", -1))
        )
        history_best = min(
            history_rows, key=lambda value: float(value.get("validation_ce", math.inf))
        )
        if (
            not all(math.isfinite(value) and value > 0 for value in (zero, best))
            or not math.isfinite(improvement)
            or not math.isclose(improvement, (zero - best) / zero, rel_tol=0, abs_tol=1e-12)
            or not isinstance(early_stopped, bool)
            or completed_step < SMOKE_CHECKPOINT_INTERVAL
            or completed_step > SMOKE_MAX_STEPS
            or completed_step % SMOKE_CHECKPOINT_INTERVAL != 0
            or int(trial_summary.get("completed_step", -1)) != completed_step
            or trial_summary.get("data_status") != "production_ready"
            or sample_manifest_path
            != smoke_context.dataset_dir / "sample_manifest.json"
            or not sample_manifest_path.is_file()
            or sha256_file(sample_manifest_path) != run["sample_manifest_sha256"]
            or int(sample_manifest.get("sample_count", -1))
            != int(run.get("total_sample_count", -2))
            or int(run.get("total_sample_count", -1)) < 512
            or not _has_verified_survivorship_audit(sample_manifest)
            or (completed_step < SMOKE_MAX_STEPS and early_stopped is not True)
            or trial_summary.get("diagnostic_checkpoint_name")
            != checkpoint_path.name
            or trial_summary.get("diagnostic_checkpoint_hash") != state_sha256
            or any(
                not isinstance(item, Mapping)
                or int(item.get("step", -1)) % SMOKE_CHECKPOINT_INTERVAL != 0
                or int(item.get("step", -1)) > SMOKE_MAX_STEPS
                or not math.isfinite(float(item.get("validation_ce", math.nan)))
                for item in history_rows
            )
            or int(trial_summary.get("diagnostic_best_step", -1))
            != int(history_best.get("step", -2))
            or not math.isclose(
                float(history_best.get("validation_ce", math.nan)),
                best,
                rel_tol=0,
                abs_tol=1e-12,
            )
            or not math.isclose(
                float(trial_summary.get("zero_shot_validation_ce", math.nan)),
                zero,
                rel_tol=0,
                abs_tol=1e-12,
            )
            or not math.isclose(
                float(trial_summary.get("diagnostic_best_validation_ce", math.nan)),
                best,
                rel_tol=0,
                abs_tol=1e-12,
            )
        ):
            raise CliContractError("adapter LR×seed 运行未满足完整训练或 CE 稳定性合同")
        improvements[lr].append(improvement)
        artifact_commitments.append(
            {
                "learning_rate": lr,
                "seed": seed,
                "resolved_config_file_sha256": run["resolved_config_file_sha256"],
                "checkpoint_manifest_sha256": manifest_sha256,
                "checkpoint_state_sha256": state_sha256,
                "summary_sha256": run["summary_sha256"],
                "sample_manifest_sha256": run["sample_manifest_sha256"],
            }
        )
    sweep = {(lr, 100) for lr in expected_lrs}
    if not sweep.issubset(seen):
        raise CliContractError("adapter LR sweep 缺少固定 seed=100 的三条运行")
    run_by_key = {(float(item["learning_rate"]), int(item["seed"])): item for item in runs}
    eligible: list[tuple[float, float]] = []
    for lr in expected_lrs:
        item = run_by_key[(lr, 100)]
        summary = _json_file(
            resolve_under(context.layout.root, str(item["summary_path"]), must_exist=True)
        )
        history = summary.get("validation_history")
        best_step = int(summary.get("diagnostic_best_step", -1))
        if not isinstance(history, list):
            continue
        ordered = sorted(history, key=lambda value: int(value.get("step", -1)))
        indices = [
            index
            for index, value in enumerate(ordered)
            if int(value.get("step", -1)) == best_step
        ]
        if len(indices) != 1 or indices[0] == 0 or indices[0] == len(ordered) - 1:
            continue
        index = indices[0]
        best_ce = float(item["best_validation_ce"])
        zero = float(item["zero_shot_validation_ce"])
        if (
            best_ce <= ADAPTER_DIAGNOSTIC_CE_CEILING
            and math.isclose(
                best_ce,
                min(float(value["validation_ce"]) for value in ordered),
                rel_tol=0,
                abs_tol=1e-12,
            )
            and float(ordered[index - 1]["validation_ce"]) <= zero
            and float(ordered[index + 1]["validation_ce"]) <= zero
        ):
            eligible.append((lr, best_ce))
    if not eligible:
        raise CliContractError("adapter LR sweep 没有满足 CE 上限和相邻点稳定性的候选")
    minimum_ce = min(value for _, value in eligible)
    selected_lr = min(
        lr for lr, value in eligible if value <= minimum_ce + ADAPTER_DIAGNOSTIC_TIE_TOLERANCE
    )
    expected_seen = sweep | {(selected_lr, 101), (selected_lr, 102)}
    if seen != expected_seen:
        raise CliContractError("adapter LR×seed 唯一 5 次运行不符合 sweep 后复核合同")
    selected_improvements = improvements[selected_lr]
    if (
        len(selected_improvements) != 3
        or any(value <= 0 for value in selected_improvements)
        or float(np.mean(selected_improvements)) < 0.01
        or any(value < -0.01 for value in selected_improvements)
    ):
        raise CliContractError("adapter selected LR 三 seed 稳定性未通过")
    if not math.isclose(selected_lr, production_lr, rel_tol=0, abs_tol=1e-15):
        raise CliContractError("adapter 生产学习率不是固定规则选出的 LR×seed 最优值")
    return {
        "schema_version": ADAPTER_DIAGNOSTIC_RECEIPT_SCHEMA,
        "matrix_sha256": matrix_sha256,
        "matrix_payload_sha256": matrix_payload_sha256,
        "receipt_sha256": sha256_file(receipt_path),
        "binding": current_binding,
        "selected_learning_rate": selected_lr,
        "production_seed": production_seed,
        "run_count": len(runs),
        "run_artifact_root_sha256": _canonical_json_sha256(
            {"artifacts": sorted(artifact_commitments, key=lambda item: (item["learning_rate"], item["seed"]))}
        ),
        "release_bound": release_bound,
        "production_checkpoint_name": production_reference if release_bound else None,
        "production_adapter_hash": production_hash if release_bound else None,
    }


def _adapter_diagnostic_trial_path(
    context: WorkflowContext, *, learning_rate: float, seed: int
) -> Path:
    family_config = copy.deepcopy(
        load_config(context.config_path)[0]
        if getattr(context, "config_path", None) is not None
        else context.config
    )
    family_config["training"]["seed"] = None
    family_config["training"]["adapter"]["learning_rate"] = None
    family_sha256 = _canonical_json_sha256(
        {
            "schema_version": "kronos-a-share-adapter-diagnostic-family-v1",
            "config": family_config,
        }
    )
    return resolve_under(
        context.layout.registry,
        Path("adapter-diagnostic-v1")
        / family_sha256
        / f"lr-{learning_rate:.0e}-seed-{seed}.json",
    )


def _write_append_only_json(
    path: Path, payload: Mapping[str, Any], *, allowed_root: Path
) -> None:
    path = resolve_under(allowed_root, path)
    if path.is_file():
        if _json_file(path) != dict(payload):
            raise CliBlocked("append-only ledger 已有冲突条目，拒绝覆盖")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(
            dict(payload), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        if _json_file(path) != dict(payload):
            raise CliBlocked("append-only ledger 并发登记冲突，拒绝覆盖")


def _register_adapter_diagnostic_trial(
    context: WorkflowContext, summary: Mapping[str, Any]
) -> dict[str, Any] | None:
    """Atomically register a smoke trial and emit the fixed five-run receipt."""

    lr = float(context.config["training"]["adapter"]["learning_rate"])
    seed = int(context.config["training"]["seed"])
    if lr not in FORMAL_ADAPTER_DIAGNOSTIC_LRS or seed not in FORMAL_ADAPTER_DIAGNOSTIC_SEEDS:
        return None
    checkpoint_name = str(summary.get("diagnostic_checkpoint_name", ""))
    checkpoint_path = context.checkpoint_dir / checkpoint_name
    resolved_path = context.metrics_dir / "resolved_training_config.json"
    summary_path = context.metrics_dir / "adapter_summary.json"
    manifest_path = checkpoint_path / "manifest.json"
    state_path = checkpoint_path / "state.pt"
    sample_manifest_path = context.dataset_dir / "sample_manifest.json"
    if not all(
        path.is_file()
        for path in (
            resolved_path,
            summary_path,
            manifest_path,
            state_path,
            sample_manifest_path,
        )
    ):
        raise CliContractError("adapter diagnostic trial 工件不完整，无法登记")
    sample_manifest = _json_file(sample_manifest_path)
    if (
        summary.get("data_status") != "production_ready"
        or int(sample_manifest.get("sample_count", -1)) < 512
        or not _has_verified_survivorship_audit(sample_manifest)
    ):
        raise CliBlocked(
            "adapter diagnostic 仅允许 production_ready 且分层样本总数不少于512的数据集"
        )
    entry = {
        "learning_rate": lr,
        "seed": seed,
        "resolved_config_path": str(resolved_path.relative_to(context.layout.root)),
        "resolved_config_file_sha256": sha256_file(resolved_path),
        "resolved_config_sha256": context.training_config_sha256,
        "checkpoint_path": str(checkpoint_path.relative_to(context.layout.root)),
        "checkpoint_manifest_sha256": sha256_file(manifest_path),
        "checkpoint_state_sha256": sha256_file(state_path),
        "summary_path": str(summary_path.relative_to(context.layout.root)),
        "summary_sha256": sha256_file(summary_path),
        "sample_manifest_path": str(
            sample_manifest_path.relative_to(context.layout.root)
        ),
        "sample_manifest_sha256": sha256_file(sample_manifest_path),
        "total_sample_count": int(sample_manifest["sample_count"]),
        "zero_shot_validation_ce": float(summary["zero_shot_validation_ce"]),
        "best_validation_ce": float(summary["diagnostic_best_validation_ce"]),
        "adapter_ce_improvement": float(summary["diagnostic_ce_improvement"]),
        "completed_step": int(summary["completed_step"]),
        "early_stopped": bool(summary["early_stopped"]),
    }
    trial_path = _adapter_diagnostic_trial_path(
        context, learning_rate=lr, seed=seed
    )
    _write_append_only_json(
        trial_path, entry, allowed_root=context.layout.root
    )

    def read_trial(candidate_lr: float, candidate_seed: int) -> dict[str, Any] | None:
        path = _adapter_diagnostic_trial_path(
            context, learning_rate=candidate_lr, seed=candidate_seed
        )
        return _json_file(path) if path.is_file() else None

    sweep = [read_trial(candidate_lr, 100) for candidate_lr in FORMAL_ADAPTER_DIAGNOSTIC_LRS]
    if any(item is None for item in sweep):
        return None
    eligible: list[tuple[float, float]] = []
    for item in sweep:
        assert item is not None
        trial_summary = _json_file(
            resolve_under(context.layout.root, str(item["summary_path"]), must_exist=True)
        )
        history = sorted(
            trial_summary.get("validation_history", []),
            key=lambda value: int(value.get("step", -1)),
        )
        best_step = int(trial_summary.get("diagnostic_best_step", -1))
        indices = [
            index
            for index, value in enumerate(history)
            if int(value.get("step", -1)) == best_step
        ]
        if len(indices) != 1 or indices[0] == 0 or indices[0] == len(history) - 1:
            continue
        index = indices[0]
        zero = float(item["zero_shot_validation_ce"])
        best = float(item["best_validation_ce"])
        if (
            best <= ADAPTER_DIAGNOSTIC_CE_CEILING
            and float(history[index - 1]["validation_ce"]) <= zero
            and float(history[index + 1]["validation_ce"]) <= zero
        ):
            eligible.append((float(item["learning_rate"]), best))
    if not eligible:
        return None
    minimum_ce = min(value for _, value in eligible)
    selected_lr = min(
        candidate_lr
        for candidate_lr, value in eligible
        if value <= minimum_ce + ADAPTER_DIAGNOSTIC_TIE_TOLERANCE
    )
    selected_extra = [read_trial(selected_lr, value) for value in (101, 102)]
    if any(item is None for item in selected_extra):
        return None
    runs = [item for item in sweep if item is not None] + [
        item for item in selected_extra if item is not None
    ]
    base_config, _ = load_config(context.config_path)
    if not math.isclose(
        float(base_config["training"]["adapter"]["learning_rate"]),
        selected_lr,
        rel_tol=0,
        abs_tol=1e-15,
    ):
        selection_path = trial_path.parent / "selected_learning_rate.json"
        atomic_write_json(
            selection_path,
            {
                "schema_version": "kronos-a-share-adapter-diagnostic-selection-v1",
                "selected_learning_rate": selected_lr,
                "selection_policy": "seed100_min_best_ce_with_1e-4_lower_lr_tiebreak",
            },
            allowed_root=context.layout.root,
        )
        return None
    production_context = build_context(
        context.config_path,
        create=True,
        training_profile="full",
    )
    diagnostic_dataset_hashes = {
        _json_file(
            resolve_under(context.layout.root, str(item["checkpoint_path"]), must_exist=True)
            / "manifest.json"
        ).get("binding", {}).get("dataset_sha256")
        for item in runs
    }
    if len(diagnostic_dataset_hashes) != 1:
        raise CliBlocked("adapter diagnostic 五次运行的数据集绑定不一致")
    diagnostic_dataset_sha256 = str(next(iter(diagnostic_dataset_hashes)))
    matrix = {
        "schema_version": ADAPTER_DIAGNOSTIC_MATRIX_SCHEMA,
        "binding": _gate_binding(_binding(production_context)),
        "diagnostic_dataset_sha256": diagnostic_dataset_sha256,
        "learning_rates": list(FORMAL_ADAPTER_DIAGNOSTIC_LRS),
        "seeds": list(FORMAL_ADAPTER_DIAGNOSTIC_SEEDS),
        "selection_policy": "seed100_min_best_ce_with_1e-4_lower_lr_tiebreak",
        "minimum_mean_ce_improvement": 0.01,
        "maximum_single_run_ce_regression": 0.01,
        "selected_learning_rate": selected_lr,
        "production_seed": 100,
        "runs": runs,
    }
    matrix["payload_sha256"] = _canonical_json_sha256(matrix)
    matrix_path = production_context.metrics_dir / "adapter_diagnostic_matrix.json"
    atomic_write_json(matrix_path, matrix, allowed_root=context.layout.root)
    receipt = {
        "schema_version": ADAPTER_DIAGNOSTIC_RECEIPT_SCHEMA,
        "matrix_sha256": sha256_file(matrix_path),
        "matrix_payload_sha256": matrix["payload_sha256"],
        "binding": matrix["binding"],
        "diagnostic_dataset_sha256": diagnostic_dataset_sha256,
        "selected_learning_rate": selected_lr,
        "production_seed": 100,
    }
    receipt["payload_sha256"] = _canonical_json_sha256(receipt)
    atomic_write_json(
        production_context.metrics_dir / "adapter_diagnostic_matrix.receipt.json",
        receipt,
        allowed_root=context.layout.root,
    )
    return _adapter_diagnostic_matrix_evidence(
        production_context,
        production_reference="",
        production_hash="",
    )


def _materialize_adapter_diagnostic_from_registry(
    context: WorkflowContext,
) -> dict[str, Any] | None:
    """Materialize the five already-finished smoke trials for the current full config."""

    def read_trial(lr: float, seed: int) -> dict[str, Any] | None:
        path = _adapter_diagnostic_trial_path(
            context, learning_rate=lr, seed=seed
        )
        return _json_file(path) if path.is_file() else None

    sweep = [read_trial(lr, 100) for lr in FORMAL_ADAPTER_DIAGNOSTIC_LRS]
    if any(item is None for item in sweep):
        return None
    eligible: list[tuple[float, float]] = []
    for item in sweep:
        assert item is not None
        summary = _json_file(
            resolve_under(context.layout.root, str(item["summary_path"]), must_exist=True)
        )
        history = sorted(
            summary.get("validation_history", []),
            key=lambda value: int(value.get("step", -1)),
        )
        best_step = int(summary.get("diagnostic_best_step", -1))
        indices = [
            index
            for index, value in enumerate(history)
            if int(value.get("step", -1)) == best_step
        ]
        if len(indices) != 1 or indices[0] == 0 or indices[0] == len(history) - 1:
            continue
        index = indices[0]
        zero = float(item["zero_shot_validation_ce"])
        best = float(item["best_validation_ce"])
        if (
            best <= ADAPTER_DIAGNOSTIC_CE_CEILING
            and float(history[index - 1]["validation_ce"]) <= zero
            and float(history[index + 1]["validation_ce"]) <= zero
        ):
            eligible.append((float(item["learning_rate"]), best))
    if not eligible:
        return None
    minimum_ce = min(value for _, value in eligible)
    selected_lr = min(
        lr
        for lr, value in eligible
        if value <= minimum_ce + ADAPTER_DIAGNOSTIC_TIE_TOLERANCE
    )
    if not math.isclose(
        float(context.config["training"]["adapter"]["learning_rate"]),
        selected_lr,
        rel_tol=0,
        abs_tol=1e-15,
    ):
        return None
    extras = [read_trial(selected_lr, seed) for seed in (101, 102)]
    if any(item is None for item in extras):
        return None
    runs = [item for item in sweep if item is not None] + [
        item for item in extras if item is not None
    ]
    diagnostic_dataset_hashes = {
        _json_file(
            resolve_under(context.layout.root, str(item["checkpoint_path"]), must_exist=True)
            / "manifest.json"
        ).get("binding", {}).get("dataset_sha256")
        for item in runs
    }
    if len(diagnostic_dataset_hashes) != 1:
        raise CliBlocked("adapter diagnostic 五次运行的数据集绑定不一致")
    diagnostic_dataset_sha256 = str(next(iter(diagnostic_dataset_hashes)))
    matrix = {
        "schema_version": ADAPTER_DIAGNOSTIC_MATRIX_SCHEMA,
        "binding": _gate_binding(_binding(context)),
        "diagnostic_dataset_sha256": diagnostic_dataset_sha256,
        "learning_rates": list(FORMAL_ADAPTER_DIAGNOSTIC_LRS),
        "seeds": list(FORMAL_ADAPTER_DIAGNOSTIC_SEEDS),
        "selection_policy": "seed100_min_best_ce_with_1e-4_lower_lr_tiebreak",
        "minimum_mean_ce_improvement": 0.01,
        "maximum_single_run_ce_regression": 0.01,
        "selected_learning_rate": selected_lr,
        "production_seed": 100,
        "runs": runs,
    }
    matrix["payload_sha256"] = _canonical_json_sha256(matrix)
    matrix_path = context.metrics_dir / "adapter_diagnostic_matrix.json"
    atomic_write_json(matrix_path, matrix, allowed_root=context.layout.root)
    receipt = {
        "schema_version": ADAPTER_DIAGNOSTIC_RECEIPT_SCHEMA,
        "matrix_sha256": sha256_file(matrix_path),
        "matrix_payload_sha256": matrix["payload_sha256"],
        "binding": matrix["binding"],
        "diagnostic_dataset_sha256": diagnostic_dataset_sha256,
        "selected_learning_rate": selected_lr,
        "production_seed": 100,
    }
    receipt["payload_sha256"] = _canonical_json_sha256(receipt)
    atomic_write_json(
        context.metrics_dir / "adapter_diagnostic_matrix.receipt.json",
        receipt,
        allowed_root=context.layout.root,
    )
    return _adapter_diagnostic_matrix_evidence(
        context,
        production_reference="",
        production_hash="",
    )


def _adapter_checkpoint_release_metrics(
    context: WorkflowContext,
    *,
    reference: str,
    expected_hash: str,
) -> dict[str, Any]:
    """Read release-critical CE/GPU evidence from the committed checkpoint."""

    from kronos_a_share_training import CheckpointStore

    store = CheckpointStore(context.checkpoint_dir, _binding(context))
    manifest = store.inspect(reference)
    if (
        manifest.get("stage") != "adapter"
        or manifest.get("checkpoint_name") != reference
        or manifest.get("files", {}).get("state.pt", {}).get("sha256")
        != expected_hash
    ):
        raise CliContractError("adapter checkpoint 身份/哈希不匹配")
    extra = _checkpoint_extra_state(store, reference)
    summary_path = context.metrics_dir / "adapter_summary.json"
    if not summary_path.is_file():
        raise CliContractError("adapter checkpoint 缺少正式训练完成 summary")
    summary = _json_file(summary_path)
    diagnostic_evidence = _adapter_diagnostic_matrix_evidence(
        context,
        production_reference=reference,
        production_hash=expected_hash,
    )
    zero = float(extra.get("zero_shot_validation_ce", math.nan))
    best = float(extra.get("best_validation_ce", math.nan))
    metric = float(manifest.get("metric", math.nan))
    history = extra.get("validation_history")
    history_entry = (
        next(
            (
                item
                for item in history
                if isinstance(item, Mapping)
                and int(item.get("step", -1)) == int(manifest.get("step", -2))
            ),
            None,
        )
        if isinstance(history, list)
        else None
    )
    if (
        extra.get("validation_contract")
        != context.config["training"]["adapter"]["validation_contract"]
        or extra.get("engineering_smoke") is not False
        or not all(math.isfinite(value) and value > 0 for value in (zero, best, metric))
        or not math.isclose(best, metric, rel_tol=0, abs_tol=1e-12)
        or extra.get("zero_shot_fallback") is not False
        or int(extra.get("best_step", -1)) != int(manifest.get("step", -2))
        or extra.get("selection_reason")
        != "minimum_causal_validation_ce_meets_release_threshold"
        or not isinstance(history_entry, Mapping)
        or not math.isclose(
            float(history_entry.get("validation_ce", math.nan)),
            metric,
            rel_tol=0,
            abs_tol=1e-12,
        )
        or extra.get("resolved_config_sha256") != context.training_config_sha256
        or int(extra.get("checkpoint_interval", -1)) != FULL_CHECKPOINT_INTERVAL
        or int(extra.get("validation_interval", -1)) != FULL_CHECKPOINT_INTERVAL
        or int(extra.get("early_stopping_patience", -1))
        != ADAPTER_EARLY_STOPPING_PATIENCE
        or int(extra.get("max_allowed_steps", -1)) != FULL_MAX_STEPS
        or int(manifest.get("step", -1)) % FULL_CHECKPOINT_INTERVAL != 0
        or any(
            not isinstance(item, Mapping)
            or int(item.get("step", -1)) % FULL_CHECKPOINT_INTERVAL != 0
            for item in history
        )
        or summary.get("status") != "ok"
        or summary.get("formal_training_complete") is not True
        or int(summary.get("max_allowed_steps", -1)) != FULL_MAX_STEPS
        or summary.get("checkpoint_name") != reference
        or summary.get("adapter_hash") != expected_hash
        or summary.get("adapter_diagnostic_matrix_evidence") != diagnostic_evidence
        or int(summary.get("best_step", -1)) != int(manifest.get("step", -2))
        or (
            int(summary.get("completed_step", -1)) != FULL_MAX_STEPS
            and summary.get("early_stopped") is not True
        )
        or int(summary.get("completed_step", -1)) % FULL_CHECKPOINT_INTERVAL != 0
    ):
        raise CliContractError("adapter checkpoint CE 因果验证证据不完整")
    peak = extra.get("peak_gpu_memory_bytes")
    limit = extra.get("gpu_memory_limit_bytes")
    if (
        isinstance(peak, bool)
        or isinstance(limit, bool)
        or not isinstance(peak, int)
        or not isinstance(limit, int)
        or peak < 0
        or limit != 3 * 1024**3
        or peak > limit
    ):
        raise CliContractError("adapter checkpoint 显存证据未通过3 GiB硬门")
    return {
        "checkpoint_name": reference,
        "adapter_hash": expected_hash,
        "validation_contract": extra["validation_contract"],
        "zero_shot_validation_ce": zero,
        "best_validation_ce": best,
        "adapter_ce_improvement": (zero - best) / zero,
        "peak_gpu_memory_bytes": peak,
        "gpu_memory_limit_bytes": limit,
        "adapter_diagnostic_matrix_evidence": diagnostic_evidence,
    }


def _live_adapter_checkpoint_release_metrics(
    context: WorkflowContext,
    *,
    store: Any,
    reference: str,
    expected_hash: str,
    device: str,
    chunk_size: int,
) -> dict[str, Any]:
    """Recompute release CE on the bound validation cache; declarations are audit only."""

    if chunk_size < 1:
        raise CliContractError("chunk-size 必须为正整数")
    declared = _adapter_checkpoint_release_metrics(
        context,
        reference=reference,
        expected_hash=expected_hash,
    )
    arrays = _load_cache(context)["arrays"]
    valid_members = _members_for_split(arrays, "validation")
    components = _load_kronos_components(context, device)
    try:
        live_zero = _validation_adapter_ce(
            components.model,
            arrays,
            valid_members,
            batch_size=chunk_size,
            device=components.device,
        )
        loaded = store.load(
            reference,
            model=components.model,
            restore_rng=False,
            map_location=components.device,
        )
        if loaded.stage != "adapter":
            raise CliContractError("现场 CE 重算必须加载 adapter checkpoint")
        live_adapted = _validation_adapter_ce(
            components.model,
            arrays,
            valid_members,
            batch_size=chunk_size,
            device=components.device,
        )
    finally:
        import gc
        import torch

        del components
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    if not all(
        math.isfinite(value) and value > 0 for value in (live_zero, live_adapted)
    ):
        raise CliContractError("现场重算 adapter CE 包含 NaN/Inf 或非正数")
    declaration_matches_live = math.isclose(
        declared["zero_shot_validation_ce"],
        live_zero,
        rel_tol=1e-5,
        abs_tol=1e-6,
    ) and math.isclose(
        declared["best_validation_ce"],
        live_adapted,
        rel_tol=1e-5,
        abs_tol=1e-6,
    )
    return {
        **declared,
        "declared_zero_shot_validation_ce": declared["zero_shot_validation_ce"],
        "declared_best_validation_ce": declared["best_validation_ce"],
        "live_zero_shot_validation_ce": live_zero,
        "live_adapter_validation_ce": live_adapted,
        "adapter_ce_improvement": (live_zero - live_adapted) / live_zero,
        "declaration_matches_live": declaration_matches_live,
        "release_metric_source": "live_validation_cache_recompute",
    }


def _evaluation_commitment_path(
    context: WorkflowContext,
    *,
    binding: Any,
    adapter_hash: str,
    scorer_hash: str,
    split: str,
) -> Path:
    identity = {
        "schema_version": "kronos-a-share-evaluation-identity-v1",
        "binding": _gate_binding(binding),
        "adapter_hash": adapter_hash,
        "scorer_checkpoint_hash": scorer_hash,
        "split": split,
    }
    return resolve_under(
        context.layout.registry,
        Path("evaluation-commitments")
        / split
        / f"{_canonical_json_sha256(identity)}.json",
    )


def _write_evaluation_commitment(
    path: Path,
    *,
    context: WorkflowContext,
    binding: Any,
    adapter_hash: str,
    scorer_hash: str,
    split: str,
    report_path: Path,
) -> dict[str, Any]:
    payload = {
        "schema_version": "kronos-a-share-evaluation-commitment-v1",
        "binding": _gate_binding(binding),
        "adapter_hash": adapter_hash,
        "scorer_checkpoint_hash": scorer_hash,
        "split": split,
        "audit_only": split == "locked_retrospective",
        "report_path": str(report_path.relative_to(context.layout.root)),
        "report_sha256": sha256_file(report_path),
    }
    payload["payload_sha256"] = _canonical_json_sha256(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise CliBlocked(f"{split} 冻结绑定已存在成功 evaluation commitment，拒绝重复执行") from exc
    return payload


def _command_evaluate_impl(args: argparse.Namespace) -> dict[str, Any]:
    from kronos_a_share_training import CheckpointFileLock, CheckpointStore

    context = build_context(
        args.config, create=True, variant=getattr(args, "_variant", None)
    )
    binding = _binding(context)
    store = CheckpointStore(context.checkpoint_dir, binding)
    reasons: list[str] = []
    evaluated_checkpoint: str | None = None
    adapter_reference: str | None = None
    adapter_hash: str | None = None
    scorer_checkpoint_hash: str | None = None
    scorer_stability_evidence: dict[str, Any] | None = None
    checkpoint: dict[str, Any] | None = None
    try:
        checkpoint_reference = _stage_reference(
            store, stage="scorer", kind=args.checkpoint
        )
        checkpoint = store.inspect(checkpoint_reference)
        evaluated_checkpoint = checkpoint["checkpoint_name"]
        adapter_reference, adapter_hash, scorer_checkpoint_hash = _scorer_checkpoint_hashes(
            store, checkpoint
        )
        if args.split in {"development_test", "locked_retrospective"}:
            preliminary_commitment = _evaluation_commitment_path(
                context,
                binding=binding,
                adapter_hash=adapter_hash,
                scorer_hash=scorer_checkpoint_hash,
                split=args.split,
            )
            if preliminary_commitment.is_file():
                raise CliBlocked(
                    f"{args.split} 冻结绑定已存在成功 commitment，拒绝重复执行"
                )
        scorer_stability_evidence = _scorer_stability_evidence(
            context,
            checkpoint_reference=evaluated_checkpoint,
            scorer_checkpoint_hash=scorer_checkpoint_hash,
        )
    except CliBlocked:
        raise
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        reasons.append(f"checkpoint_unavailable:{exc}")
    evaluation_commitment_path: Path | None = None
    if (
        args.split in {"development_test", "locked_retrospective"}
        and adapter_hash is not None
        and scorer_checkpoint_hash is not None
    ):
        evaluation_commitment_path = _evaluation_commitment_path(
            context,
            binding=binding,
            adapter_hash=adapter_hash,
            scorer_hash=scorer_checkpoint_hash,
            split=args.split,
        )
        if evaluation_commitment_path.is_file():
            raise CliBlocked(f"{args.split} 冻结绑定已存在成功 commitment，拒绝重复执行")
    data_report = _load_data_status(context)
    if data_report["status"] != "production_ready":
        reasons.append(f"data_status={data_report['status']}，未达到 production_ready")
    canonical_validation_input = context.predictions_dir / "validation_baselines.csv"
    if args.split == "validation":
        input_path = canonical_validation_input
        if (
            args.input is not None
            and args.input.resolve() != canonical_validation_input.resolve()
        ):
            reasons.append(
                "formal_validation_rejects_noncanonical_input:"
                f"{args.input.resolve()}"
            )
    else:
        input_path = (
            args.input.resolve()
            if args.input is not None
            else context.predictions_dir / f"{args.split}_baselines.csv"
        )
    metrics: dict[str, Any] = {}
    if (
        not input_path.is_file()
        and checkpoint is not None
        and data_report["status"] == "production_ready"
    ):
        try:
            with CheckpointFileLock(_global_training_lock_path(context)):
                input_path = _ensure_evaluation_companion(
                    context,
                    binding=binding,
                    output_path=input_path,
                    device=getattr(args, "device", "auto"),
                    chunk_size=int(getattr(args, "chunk_size", 16)),
                    evaluate_split=args.split,
                )
        except (OSError, RuntimeError, TypeError, ValueError, KeyError) as exc:
            reasons.append(f"baseline_build_incomplete:{exc}")
    if not input_path.is_file():
        reasons.append(f"missing_evaluation_input:{input_path}")
    elif checkpoint is not None:
        try:
            with CheckpointFileLock(_global_training_lock_path(context)):
                live_predictions = _recompute_scorer_predictions(
                    context,
                    store=store,
                    checkpoint_reference=checkpoint["checkpoint_name"],
                    split=args.split,
                    device=getattr(args, "device", "auto"),
                    chunk_size=int(getattr(args, "chunk_size", 16)),
                )
                _materialize_non_gate_predictions(
                    context,
                    binding=binding,
                    checkpoint=checkpoint,
                    adapter_hash=adapter_hash,
                    scorer_checkpoint_hash=scorer_checkpoint_hash,
                    split=args.split,
                    frame=live_predictions,
                )
                adapter_evidence: Mapping[str, Any] | None = None
                if (
                    args.split == "validation"
                    and data_report["status"] == "production_ready"
                ):
                    with _formal_rebuilt_companion(
                        context,
                        binding=binding,
                        canonical_path=input_path,
                        device=getattr(args, "device", "auto"),
                        chunk_size=int(getattr(args, "chunk_size", 16)),
                    ) as rebuilt_input:
                        controlled = _controlled_evaluation_frame(
                            context,
                            binding=binding,
                            checkpoint=checkpoint,
                            adapter_hash=adapter_hash,
                            scorer_checkpoint_hash=scorer_checkpoint_hash,
                            companion_path=rebuilt_input,
                            live_predictions=live_predictions,
                            evaluate_split="validation",
                        )
                    adapter_evidence = _live_adapter_checkpoint_release_metrics(
                        context,
                        store=store,
                        reference=adapter_reference,
                        expected_hash=adapter_hash,
                        device=getattr(args, "device", "auto"),
                        chunk_size=int(getattr(args, "chunk_size", 16)),
                    )
                else:
                    controlled = _controlled_evaluation_frame(
                        context,
                        binding=binding,
                        checkpoint=checkpoint,
                        adapter_hash=adapter_hash,
                        scorer_checkpoint_hash=scorer_checkpoint_hash,
                        companion_path=input_path,
                        live_predictions=live_predictions,
                        evaluate_split=args.split,
                    )
            metrics = _evaluation_metrics(
                context,
                controlled,
                expected_adapter_reference=adapter_reference,
                expected_adapter_hash=adapter_hash,
                adapter_evidence=adapter_evidence,
            )
            metrics["scorer_seed_stability"] = scorer_stability_evidence
            if (
                args.split == "validation"
                and adapter_evidence is not None
                and adapter_evidence.get("declaration_matches_live") is not True
            ):
                reasons.append("adapter_checkpoint_declared_ce_mismatch")
        except (OSError, RuntimeError, TypeError, ValueError, KeyError) as exc:
            reasons.append(f"evaluation_incomplete:{exc}")
    if args.split != "validation":
        audit_only = args.split == "locked_retrospective"
        report = {
            "schema_version": "kronos-a-share-evaluation-v1",
            "input": str(input_path),
            "split": args.split,
            "data_status": data_report["status"],
            "formal_gate_eligible": False,
            "audit_only": audit_only,
            "configuration_selection_allowed": False,
            "gate": None,
            "metrics": metrics,
            "reasons": reasons,
            "generated_at": _utc_now(),
        }
        report_path = context.metrics_dir / f"evaluation_report_{args.split}.json"
        commitment = None
        if (
            not reasons
            and evaluation_commitment_path is not None
            and adapter_hash is not None
            and scorer_checkpoint_hash is not None
        ):
            report_path = evaluation_commitment_path.with_name(
                f"{evaluation_commitment_path.stem}.report.json"
            )
            if not getattr(args, "_evaluation_identity_lock_held", False):
                raise CliContractError(
                    "development/locked evaluation 必须在 identity 锁内执行"
                )
            if evaluation_commitment_path.is_file() or report_path.is_file():
                raise CliBlocked(
                    f"{args.split} 冻结绑定已存在成功/进行中的 commitment"
                )
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_bytes = (
                json.dumps(
                    report,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
            with report_path.open("xb") as handle:
                handle.write(report_bytes)
                handle.flush()
                os.fsync(handle.fileno())
            commitment = _write_evaluation_commitment(
                evaluation_commitment_path,
                context=context,
                binding=binding,
                adapter_hash=adapter_hash,
                scorer_hash=scorer_checkpoint_hash,
                split=args.split,
                report_path=report_path,
            )
        else:
            atomic_write_json(
                report_path,
                report,
                allowed_root=context.layout.root,
            )
        return _envelope(
            "evaluate",
            status="ok" if not reasons else "unverified",
            message=(
                f"{args.split} 受控评估完成；该分段不签发正式 gate。"
                if not reasons
                else f"{args.split} 受控评估未完整，输出固定为 N/A。"
            ),
            report=report,
            evaluation_commitment=commitment,
            evidence_class="model_output",
            output_type="model_output" if not reasons else "N/A",
        )
    gate_result: dict[str, Any] | None = None
    if not reasons:
        evaluation = context.config["evaluation"]
        thresholds = GateThresholds(
            adapter_ce_improvement_min=float(evaluation["adapter_ce_improvement_min"]),
            validation_rank_ic_min=float(evaluation["validation_rank_ic_min"]),
            baseline_rank_ic_lift_min=float(evaluation["baseline_rank_ic_lift_min"]),
            positive_quarter_fraction_min=float(
                evaluation["positive_quarter_fraction_min"]
            ),
            base_round_trip_cost_bps=Decimal(
                str(evaluation["base_round_trip_cost_bps"])
            ),
            stress_round_trip_cost_bps=Decimal(
                str(evaluation["stress_round_trip_cost_bps"])
            ),
        )
        gate_result = evaluate_gate(
            data_status=data_report["status"],
            thresholds=thresholds,
            **{
                key: metrics[key]
                for key in (
                    "adapter_ce_improvement",
                    "validation_rank_ic",
                    "zero_shot_rank_ic",
                    "head_only_rank_ic",
                    "positive_quarter_fraction",
                    "bootstrap_ci95_lower",
                    "base_after_cost_return",
                    "stress_after_cost_return",
                )
            },
        )
        if metrics["strongest_baseline_lift"] < thresholds.baseline_rank_ic_lift_min:
            gate_result["gate_status"] = "blocked"
            gate_result["publishable"] = False
            gate_result["output_type"] = "N/A"
            gate_result["reasons"].append(
                "相对全部候选中的最强基线 RankIC 提升不足 0.005"
            )
        reasons.extend(gate_result["reasons"])
    evaluation = context.config["evaluation"]
    forward_observation = inspect_forward_registry(
        context.layout.registry
        / "forward-observations"
        / (scorer_checkpoint_hash or ("0" * 64)),
        context.layout.root,
        minimum_days=int(evaluation["forward_observation_min_days"]),
        recommended_days=int(evaluation["forward_observation_recommended_days"]),
        expected_adapter_hash=adapter_hash,
        expected_scorer_checkpoint_hash=scorer_checkpoint_hash,
        expected_gate_binding=_gate_binding(binding),
    )
    retrospective_passed = (
        not reasons
        and gate_result is not None
        and gate_result["gate_status"] == "passed"
    )
    research_scoring_allowed = False
    if retrospective_passed and not forward_observation["minimum_met"]:
        reasons.append(
            "forward_observation_days="
            f"{forward_observation['observation_days']}<"
            f"{forward_observation['minimum_days']}"
        )
        research_scoring_allowed = True
    passed = retrospective_passed and forward_observation["minimum_met"]
    gate = _write_gate(
        context,
        binding=binding,
        gate_status="passed" if passed else "blocked",
        adapter_hash=adapter_hash,
        scorer_checkpoint_hash=scorer_checkpoint_hash,
        evaluated_checkpoint=evaluated_checkpoint,
        reasons=reasons,
        verification_status="verified" if passed else "unverified",
        research_scoring_allowed=research_scoring_allowed,
        forward_observation=forward_observation,
        metrics=metrics,
    )
    report = {
        "schema_version": "kronos-a-share-evaluation-v1",
        "input": str(input_path),
        "split": args.split,
        "data_status": data_report["status"],
        "gate": gate,
        "generated_at": _utc_now(),
    }
    atomic_write_json(
        context.metrics_dir / "evaluation_report.json",
        report,
        allowed_root=context.layout.root,
    )
    return _envelope(
        "evaluate",
        status="ok" if passed else "unverified",
        message=(
            "模型工件通过准出；结论仍仅是 model_output。"
            if passed
            else "评估已完成但未通过准出，输出固定为 N/A。"
        ),
        gate=gate,
        evidence_class="model_output",
        output_type=gate["output_type"],
    )


def command_evaluate(args: argparse.Namespace) -> dict[str, Any]:
    if args.split not in {"development_test", "locked_retrospective"}:
        return _command_evaluate_impl(args)

    from kronos_a_share_training import CheckpointFileLock, CheckpointStore

    context = build_context(
        args.config, create=True, variant=getattr(args, "_variant", None)
    )
    binding = _binding(context)
    try:
        store = CheckpointStore(context.checkpoint_dir, binding)
        reference = _stage_reference(store, stage="scorer", kind=args.checkpoint)
        checkpoint = store.inspect(reference)
        _, adapter_hash, scorer_hash = _scorer_checkpoint_hashes(store, checkpoint)
    except (FileNotFoundError, RuntimeError, ValueError):
        return _command_evaluate_impl(args)
    commitment_path = _evaluation_commitment_path(
        context,
        binding=binding,
        adapter_hash=adapter_hash,
        scorer_hash=scorer_hash,
        split=args.split,
    )
    report_path = commitment_path.with_name(f"{commitment_path.stem}.report.json")
    lock_path = commitment_path.with_name(f"{commitment_path.stem}.lock")
    with CheckpointFileLock(lock_path):
        if commitment_path.is_file() or report_path.is_file():
            raise CliBlocked(
                f"{args.split} 冻结绑定已存在成功/进行中的 commitment"
            )
        setattr(args, "_evaluation_identity_lock_held", True)
        try:
            return _command_evaluate_impl(args)
        finally:
            delattr(args, "_evaluation_identity_lock_held")


def _blocked_score_record(
    context: WorkflowContext,
    *,
    as_of: str,
    ticker: str,
    adapter_hash: str | None,
    flags: Sequence[str],
) -> dict[str, Any]:
    return {
        "as_of": as_of,
        "ticker": ticker,
        "horizon": HORIZON,
        "raw_score": None,
        "percentile": None,
        "forecast_path": [],
        "path_dispersion": None,
        "dataset_id": context.dataset_id,
        "run_id": context.run_id,
        "adapter_hash": adapter_hash,
        "gate_status": "blocked",
        "constraint_flags": list(flags),
        "evidence_class": "model_output",
        "output_type": "N/A",
    }


def _validate_score_cross_section(*, eligible_count: int, active_count: int) -> float:
    if active_count < 1 or eligible_count < 0 or eligible_count > active_count:
        raise CliBlocked("score-as-of 正式横截面计数无效")
    coverage_ratio = eligible_count / active_count
    if (
        eligible_count < FORMAL_MIN_CROSS_SECTION
        or coverage_ratio < FORMAL_MIN_COVERAGE_RATIO
    ):
        raise CliBlocked(
            "score-as-of 正式横截面覆盖不足："
            f"eligible_count={eligible_count}, active_member_count={active_count}, "
            f"coverage_ratio={coverage_ratio:.6f}"
        )
    return coverage_ratio


def _public_forward_commitment(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": record.get("status"),
        "payload_sha256": record.get("payload_sha256"),
        "internal_blind_store": True,
    }


def _expected_gate_receipt(
    context: WorkflowContext,
    gate_path: Path,
    gate: Mapping[str, Any],
) -> tuple[Path, dict[str, Any]]:
    gate_hash = sha256_file(gate_path)
    receipt_path = (
        context.checkpoint_dir / "gate-receipts" / f"{gate_hash}.json"
    )
    return receipt_path, {
        "schema_version": GATE_RECEIPT_SCHEMA_VERSION,
        "gate_sha256": gate_hash,
        "gate_bytes": gate_path.stat().st_size,
        "gate_schema_version": gate.get("schema_version"),
        "gate_status": gate.get("gate_status"),
        "run_id": gate.get("run_id"),
        "binding": gate.get("binding"),
        "adapter_hash": gate.get("adapter_hash"),
        "scorer_checkpoint_hash": gate.get("scorer_checkpoint_hash"),
        "evaluated_checkpoint": gate.get("evaluated_checkpoint"),
        "gate_generated_at": gate.get("generated_at"),
        "gate_sequence": gate.get("gate_sequence"),
    }


def _verify_gate_receipt(
    context: WorkflowContext,
    gate_path: Path,
    gate: Mapping[str, Any],
) -> dict[str, Any]:
    receipt_path, expected = _expected_gate_receipt(context, gate_path, gate)
    if not receipt_path.is_file():
        raise CliBlocked("gate.json 缺少匹配的不可变 release receipt")
    receipt = _json_file(receipt_path)
    if receipt != expected:
        raise CliBlocked("gate release receipt 与 gate.json 哈希或绑定不一致")
    return receipt


def _validate_scoring_gate_semantics(
    context: WorkflowContext,
    gate: Mapping[str, Any],
) -> None:
    gate_status = gate.get("gate_status")
    research = gate.get("research_scoring_allowed") is True
    if gate_status not in {"passed", "blocked"}:
        raise CliBlocked("gate_status 非法")
    if gate_status == "passed" and research:
        raise CliBlocked("passed gate 不得标记 research_scoring_allowed")
    if gate_status != "passed" and not research:
        return

    if _load_data_status(context).get("status") != "production_ready":
        raise CliBlocked("可评分 gate 的数据状态不再是 production_ready")
    for field in ("adapter_hash", "scorer_checkpoint_hash"):
        value = gate.get(field)
        if not isinstance(value, str) or len(value) != 64:
            raise CliBlocked(f"可评分 gate 缺少64位 {field}")
    if not gate.get("evaluated_checkpoint"):
        raise CliBlocked("可评分 gate 缺少 evaluated_checkpoint")

    metrics = gate.get("metrics")
    required_metrics = {
        "adapter_ce_improvement",
        "validation_rank_ic",
        "zero_shot_rank_ic",
        "head_only_rank_ic",
        "positive_quarter_fraction",
        "bootstrap_ci95_lower",
        "base_after_cost_return",
        "stress_after_cost_return",
        "strongest_baseline_rank_ic",
        "strongest_baseline_lift",
    }
    if not isinstance(metrics, Mapping) or not required_metrics.issubset(metrics):
        raise CliBlocked("可评分 gate 缺少完整历史准出 metrics")
    cached_adapter_evidence = metrics.get("adapter_checkpoint_evidence")
    if not isinstance(cached_adapter_evidence, Mapping):
        raise CliBlocked("可评分 gate 缺少 adapter 完整训练证据")
    try:
        live_adapter_evidence = _adapter_checkpoint_release_metrics(
            context,
            reference=str(cached_adapter_evidence.get("checkpoint_name", "")),
            expected_hash=str(gate["adapter_hash"]),
        )
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as exc:
        raise CliBlocked("adapter 完整训练证据无法现场重验") from exc
    if _canonical_json_sha256(cached_adapter_evidence) != _canonical_json_sha256(
        live_adapter_evidence
    ):
        raise CliBlocked("gate adapter 证据与现场完整训练证据不一致")
    cached_stability = metrics.get("scorer_seed_stability")
    if not isinstance(cached_stability, Mapping):
        raise CliBlocked("可评分 gate 缺少 scorer 20-seed stability")
    try:
        live_stability = _scorer_stability_evidence(
            context,
            checkpoint_reference=str(gate["evaluated_checkpoint"]),
            scorer_checkpoint_hash=str(gate["scorer_checkpoint_hash"]),
        )
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as exc:
        raise CliBlocked("scorer 20-seed stability 无法现场重验") from exc
    if _canonical_json_sha256(cached_stability) != _canonical_json_sha256(
        live_stability
    ):
        raise CliBlocked("gate scorer 20-seed stability 与现场证据不一致")
    evaluation = context.config["evaluation"]
    thresholds = GateThresholds(
        adapter_ce_improvement_min=float(evaluation["adapter_ce_improvement_min"]),
        validation_rank_ic_min=float(evaluation["validation_rank_ic_min"]),
        baseline_rank_ic_lift_min=float(evaluation["baseline_rank_ic_lift_min"]),
        positive_quarter_fraction_min=float(
            evaluation["positive_quarter_fraction_min"]
        ),
        base_round_trip_cost_bps=Decimal(
            str(evaluation["base_round_trip_cost_bps"])
        ),
        stress_round_trip_cost_bps=Decimal(
            str(evaluation["stress_round_trip_cost_bps"])
        ),
    )
    try:
        numeric_metrics = {name: float(metrics[name]) for name in required_metrics}
        if not all(math.isfinite(value) for value in numeric_metrics.values()):
            raise ValueError("gate metrics 包含 NaN/Inf")
        recomputed = evaluate_gate(
            data_status="production_ready",
            thresholds=thresholds,
            **{
                name: numeric_metrics[name]
                for name in required_metrics
                if name
                not in {"strongest_baseline_rank_ic", "strongest_baseline_lift"}
            },
        )
    except (ArithmeticError, TypeError, ValueError, KeyError) as exc:
        raise CliBlocked("gate metrics 无法重算") from exc
    if recomputed.get("gate_status") != "passed":
        raise CliBlocked("gate metrics 重算未通过历史准出")

    if numeric_metrics["strongest_baseline_lift"] < float(
        evaluation["baseline_rank_ic_lift_min"]
    ):
        raise CliBlocked("gate 未通过相对全部候选最强基线的 RankIC 提升门")

    baseline_rank_ic = metrics.get("baseline_rank_ic")
    if not isinstance(baseline_rank_ic, Mapping) or not baseline_rank_ic:
        raise CliBlocked("gate 缺少可现场重算的 baseline_rank_ic 全集合")
    try:
        baseline_values = {
            str(name): float(value) for name, value in baseline_rank_ic.items()
        }
    except (TypeError, ValueError) as exc:
        raise CliBlocked("gate baseline_rank_ic 全集合不可解析") from exc
    if not all(math.isfinite(value) for value in baseline_values.values()):
        raise CliBlocked("gate baseline_rank_ic 全集合包含 NaN/Inf")
    live_strongest_name = max(baseline_values, key=baseline_values.get)
    live_strongest_rank_ic = baseline_values[live_strongest_name]
    live_strongest_lift = (
        numeric_metrics["validation_rank_ic"] - live_strongest_rank_ic
    )
    if (
        metrics.get("strongest_baseline") != live_strongest_name
        or not math.isclose(
            numeric_metrics["strongest_baseline_rank_ic"],
            live_strongest_rank_ic,
            rel_tol=0,
            abs_tol=1e-12,
        )
        or not math.isclose(
            numeric_metrics["strongest_baseline_lift"],
            live_strongest_lift,
            rel_tol=0,
            abs_tol=1e-12,
        )
    ):
        raise CliBlocked("gate strongest baseline 或 lift 与全基线集合现场重算不一致")

    forward = gate.get("forward_observation")
    if not isinstance(forward, Mapping):
        raise CliBlocked("可评分 gate 缺少 forward_observation")
    try:
        minimum_days = int(evaluation["forward_observation_min_days"])
        recommended_days = int(evaluation["forward_observation_recommended_days"])
        observed_minimum = int(forward.get("minimum_days", -1))
        observed_recommended = int(forward.get("recommended_days", -1))
        observation_days = int(forward.get("observation_days", -1))
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise CliBlocked("gate 前瞻观察计数无法解析") from exc
    if observed_minimum != minimum_days or observed_recommended != recommended_days:
        raise CliBlocked("gate 前瞻观察阈值与配置不一致")
    minimum_met = forward.get("minimum_met") is True
    cached_commitments = forward.get("batch_commitments")
    cached_root = forward.get("registry_root_sha256")
    if not isinstance(cached_commitments, list) or not isinstance(cached_root, str):
        raise CliBlocked("gate 前瞻观察缺少不可变 registry commitment")
    try:
        live_forward = inspect_forward_registry(
            context.layout.registry
            / "forward-observations"
            / str(gate["scorer_checkpoint_hash"]),
            context.layout.root,
            minimum_days=minimum_days,
            recommended_days=recommended_days,
            expected_adapter_hash=str(gate["adapter_hash"]),
            expected_scorer_checkpoint_hash=str(gate["scorer_checkpoint_hash"]),
            expected_gate_binding=gate["binding"],
        )
    except (ArithmeticError, ForwardRegistryError, OSError, TypeError, ValueError) as exc:
        raise CliBlocked("当前前瞻账本无法重新验证") from exc
    live_commitments = live_forward.get("batch_commitments")
    if not isinstance(live_commitments, list):
        raise CliBlocked("当前前瞻账本缺少 batch commitments")
    if live_commitments[: len(cached_commitments)] != cached_commitments:
        raise CliBlocked("当前前瞻账本删除、重排或改写了 gate 已绑定批次")
    try:
        live_observation_days = int(live_forward.get("observation_days", -1))
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise CliBlocked("当前前瞻账本观察日无法解析") from exc
    if live_observation_days < observation_days:
        raise CliBlocked("当前前瞻账本观察日少于 gate 已绑定计数")
    reasons = gate.get("reasons")
    if not isinstance(reasons, list):
        raise CliBlocked("gate reasons 必须是列表")
    if gate_status == "passed":
        if (
            gate.get("verification_status") != "verified"
            or gate.get("output_type") != "model_output"
            or reasons
            or not minimum_met
            or observation_days < minimum_days
            or live_forward.get("minimum_met") is not True
            or live_forward.get("registry_root_sha256") != cached_root
            or live_commitments != cached_commitments
        ):
            raise CliBlocked("passed gate 未满足前瞻、验证或输出合同")
    else:
        expected_reason = f"forward_observation_days={observation_days}<{minimum_days}"
        if (
            gate.get("verification_status") != "unverified"
            or gate.get("output_type") != "N/A"
            or minimum_met
            or observation_days >= minimum_days
            or reasons != [expected_reason]
        ):
            raise CliBlocked("前瞻研究 gate 含历史失败或语义漂移")


def _validate_gate(context: WorkflowContext, binding: Any) -> dict[str, Any]:
    path = context.checkpoint_dir / "gate.json"
    if not path.is_file():
        raise CliBlocked("缺少 gate.json；score-as-of 只能输出 N/A")
    gate = _json_file(path)
    required = {
        "schema_version",
        "gate_sequence",
        "gate_status",
        "run_id",
        "binding",
        "adapter_hash",
        "scorer_checkpoint_hash",
        "evaluated_checkpoint",
        "generated_at",
        "research_scoring_allowed",
        "verification_status",
        "output_type",
        "forward_observation",
        "reasons",
        "metrics",
    }
    missing = sorted(required - set(gate))
    if missing:
        raise CliBlocked(f"gate.json 缺少字段：{missing}")
    if gate["schema_version"] != GATE_SCHEMA_VERSION:
        raise CliBlocked("gate.json schema_version 不匹配")
    if isinstance(gate["gate_sequence"], bool) or not isinstance(
        gate["gate_sequence"], int
    ) or gate["gate_sequence"] < 1:
        raise CliBlocked("gate_sequence 无效")
    if gate["run_id"] != context.run_id or gate["binding"] != _gate_binding(binding):
        raise CliBlocked("gate.json 与当前 run/config/data 哈希不匹配")
    try:
        generated_at = datetime.fromisoformat(
            str(gate["generated_at"]).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise CliBlocked("gate.generated_at 无法解析") from exc
    if generated_at.tzinfo is None:
        raise CliBlocked("gate.generated_at 必须包含时区")
    receipt = _verify_gate_receipt(context, path, gate)
    lineage = _read_gate_lineage(context, require_active_head=True)
    active = lineage[-1]
    if (
        active["sequence"] != gate["gate_sequence"]
        or active["gate_sha256"] != sha256_file(path)
        or active["gate_receipt_sha256"]
        != sha256_file(
            context.checkpoint_dir
            / "gate-receipts"
            / f"{receipt['gate_sha256']}.json"
        )
    ):
        raise CliBlocked("gate.json 不是 active gate lineage 当前授权")
    _validate_scoring_gate_semantics(context, gate)
    return gate


def _standard_ticker(value: str) -> str:
    normalized = normalize_ticker(value)
    return f"{normalized[2:]}.{normalized[:2].upper()}"


def _local_naive(value: pd.Timestamp) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    return timestamp.tz_localize(None) if timestamp.tzinfo is not None else timestamp


def _daily_score_as_of(value: Any) -> pd.Timestamp:
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise CliContractError("score as_of 不是有效日期") from exc
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(SHANGHAI_TZ)
    else:
        timestamp = timestamp.tz_convert(SHANGHAI_TZ)
    if timestamp != timestamp.normalize():
        raise CliContractError("日频 score as_of 只接受交易日期零点，不接受盘中时点")
    return timestamp


def _inference_snapshot_inputs(
    context: WorkflowContext,
    requested: Path | None,
    as_of: pd.Timestamp,
) -> tuple[dict[str, Any], Path, Path]:
    if requested is None:
        raise CliBlocked(
            "缺少 --inference-snapshot；score-as-of 禁止读取训练快照或活动 D:\\HT"
        )
    try:
        selected = resolve_under(
            context.layout.root,
            requested,
            must_exist=True,
        )
        manifest_path = (
            selected / "inference_manifest.json" if selected.is_dir() else selected
        )
        manifest = verify_inference_snapshot(
            manifest_path,
            training_root=context.layout.root,
            project_root=PROJECT_ROOT,
            expected_as_of=as_of,
        )
        manifest["_manifest_file_sha256"] = sha256_file(manifest_path)
        manifest["_manifest_path"] = str(manifest_path.resolve())
    except (AShareDataError, KronosAshareRuntimeError, OSError, ValueError) as exc:
        raise CliBlocked(f"当日 inference snapshot 无效：{exc}") from exc
    snapshot_root = manifest_path.resolve().parent
    market_root = resolve_under(snapshot_root, "market", must_exist=True)
    pit_root = resolve_under(snapshot_root, "pit", must_exist=True)
    return manifest, market_root, pit_root


def _active_universe(pit_root: Path, as_of: pd.Timestamp) -> list[str]:
    membership = _pit_table_path(pit_root, "index_membership")
    if membership is None or not membership.is_file():
        raise CliBlocked("production score 缺少点时 CSI300/CSI500 成分表")
    frame = (
        pd.read_parquet(membership)
        if membership.suffix.lower() in {".parquet", ".pq"}
        else pd.read_csv(membership)
    )
    required = {"ticker", "index_code", "effective_from", "effective_to"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise CliBlocked(f"index_membership 缺少字段：{missing}")
    work = frame.copy()
    work["ticker"] = work["ticker"].map(normalize_ticker)
    work["effective_from"] = pd.to_datetime(work["effective_from"], errors="coerce")
    work["effective_to"] = pd.to_datetime(work["effective_to"], errors="coerce")
    if work["effective_from"].isna().any():
        raise CliBlocked("index_membership.effective_from 存在无效日期")
    accepted = {"CSI300", "CSI500", "000300", "000905", "000300.SH", "000905.SH"}
    work = work[work["index_code"].astype(str).str.upper().isin(accepted)]
    local_date = _local_naive(as_of).normalize()
    active = work[
        (work["effective_from"] <= local_date)
        & (work["effective_to"].isna() | (work["effective_to"] >= local_date))
    ]
    universe = sorted(active["ticker"].unique().tolist())
    if not universe:
        raise CliBlocked("as_of 时点 CSI800 股票池为空")
    return universe


def _history_as_of(
    market_root: Path,
    normalized_ticker: str,
    as_of: pd.Timestamp,
    corporate_actions: pd.DataFrame,
    required_open_dates: pd.DatetimeIndex,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    market = normalized_ticker[:2]
    path = market_root / "tdx_day" / market / f"{normalized_ticker}.day"
    if not path.is_file():
        raise CliContractError(f"快照缺少 {normalized_ticker}.day")
    source_frame = read_day_file(path)
    parsed = pd.to_datetime(source_frame["date"].astype(str), format="%Y%m%d")
    source_frame = source_frame.loc[
        parsed <= _local_naive(as_of).normalize()
    ].tail(LOOKBACK + 1).reset_index(drop=True)
    if len(source_frame) < LOOKBACK:
        raise CliContractError(f"{normalized_ticker} 不足90根历史 K 线")
    start_index = len(source_frame) - LOOKBACK
    frame = source_frame.iloc[start_index:].reset_index(drop=True)
    last_date = pd.to_datetime(str(int(frame.iloc[-1]["date"])), format="%Y%m%d")
    if last_date != _local_naive(as_of).normalize():
        raise CliContractError(f"{normalized_ticker} 在 as_of 无可成交日线（停牌或数据缺口）")
    observed_dates = pd.DatetimeIndex(
        pd.to_datetime(frame["date"].astype(str), format="%Y%m%d")
    ).normalize()
    if len(required_open_dates) != LOOKBACK or not observed_dates.equals(
        required_open_dates
    ):
        raise CliContractError(
            f"{normalized_ticker} official_open_sessions_mismatch:停牌或中间缺日不得拼接为连续90日输入"
        )
    window = WindowSpec(lookback=LOOKBACK, horizon=0, purge_days=PURGE_DAYS)
    adjusted_raw, _ = causal_adjusted_price_window(
        source_frame,
        start_index,
        window,
        corporate_actions=corporate_actions,
        ticker=normalized_ticker,
        origin_date=int(frame.iloc[-1]["date"]),
    )
    normalized, _ = causal_adjusted_normalized_window(
        source_frame,
        start_index,
        window,
        corporate_actions=corporate_actions,
        ticker=normalized_ticker,
        origin_date=int(frame.iloc[-1]["date"]),
    )
    adjusted_frame = pd.DataFrame(adjusted_raw, columns=FEATURE_COLUMNS)
    return frame, adjusted_frame, normalized


def _official_open_sessions_as_of(
    trading_calendar_path: Path, as_of: pd.Timestamp
) -> pd.DatetimeIndex:
    frame = (
        pd.read_parquet(trading_calendar_path)
        if trading_calendar_path.suffix.lower() in {".parquet", ".pq"}
        else pd.read_csv(trading_calendar_path)
    )
    if not {"trade_date", "is_open"}.issubset(frame.columns):
        raise CliBlocked("inference PIT trading_calendar 缺少 trade_date/is_open")
    open_mask = frame["is_open"].map(
        lambda value: value is True
        or value == 1
        or str(value).strip().lower() in {"true", "1", "yes", "y"}
    )
    dates = pd.DatetimeIndex(
        pd.to_datetime(frame.loc[open_mask, "trade_date"], errors="coerce")
    ).normalize()
    dates = dates[~dates.isna()]
    dates = dates[
        dates <= _local_naive(as_of).normalize()
    ].drop_duplicates().sort_values()
    if len(dates) < LOOKBACK or dates[-1] != _local_naive(as_of).normalize():
        raise CliBlocked("inference PIT trading_calendar 不足最近90个官方开放日或 as_of 非开放日")
    return dates[-LOOKBACK:]


def _forecast_path_samples(
    predictor: Any,
    *,
    adjusted_history: pd.DataFrame,
    history_timestamps: pd.Series,
    future_timestamps: pd.DatetimeIndex,
    sample_count: int,
    temperature: float,
    top_k: int,
    top_p: float,
) -> tuple[pd.DataFrame, float]:
    """Generate explicit paths so dispersion is measured before averaging."""

    if sample_count < 1:
        raise CliContractError("sample_count 必须至少为1")
    values = adjusted_history[list(FEATURE_COLUMNS)].to_numpy(dtype=np.float32)
    if values.shape != (LOOKBACK, len(FEATURE_COLUMNS)) or not np.isfinite(values).all():
        raise CliContractError("因果复权历史输入形状或数值无效")
    mean = values.mean(axis=0)
    std = values.std(axis=0)
    normalized = np.clip((values - mean) / (std + 1e-5), -5.0, 5.0)

    history_index = pd.DatetimeIndex(pd.to_datetime(history_timestamps, errors="coerce"))
    if history_index.isna().any() or len(history_index) != LOOKBACK:
        raise CliContractError("历史 timestamps 必须包含90个有效时点")
    future_index = pd.DatetimeIndex(future_timestamps)
    x_stamp = np.column_stack(
        [
            history_index.minute,
            history_index.hour,
            history_index.weekday,
            history_index.day,
            history_index.month,
        ]
    ).astype(np.float32)
    y_stamp = np.column_stack(
        [
            future_index.minute,
            future_index.hour,
            future_index.weekday,
            future_index.day,
            future_index.month,
        ]
    ).astype(np.float32)
    samples: list[np.ndarray] = []
    for _ in range(sample_count):
        generated = predictor.generate(
            normalized[np.newaxis, :],
            x_stamp[np.newaxis, :],
            y_stamp[np.newaxis, :],
            HORIZON,
            temperature,
            top_k,
            top_p,
            1,
            False,
        )
        decoded = np.asarray(generated, dtype=np.float32)
        if decoded.shape != (1, HORIZON, len(FEATURE_COLUMNS)):
            raise CliContractError(f"Kronos 预测张量形状无效：{decoded.shape}")
        samples.append(decoded[0] * (std + 1e-5) + mean)
    paths = np.stack(samples)
    if not np.isfinite(paths).all():
        raise CliContractError("Kronos forecast_path 包含 NaN/Inf")
    open_values = paths[:, :, 0]
    high_values = paths[:, :, 1]
    low_values = paths[:, :, 2]
    close_values = paths[:, :, 3]
    if bool(
        (open_values <= 0).any()
        or (high_values <= 0).any()
        or (low_values <= 0).any()
        or (close_values <= 0).any()
    ):
        raise CliContractError("Kronos forecast_path OHLC 必须为正数")
    if bool(
        (high_values < np.maximum(open_values, close_values)).any()
        or (low_values > np.minimum(open_values, close_values)).any()
        or (high_values < low_values).any()
    ):
        raise CliContractError("Kronos forecast_path OHLC 关系无效")
    if bool((paths[:, :, 4] < 0).any() or (paths[:, :, 5] < 0).any()):
        raise CliContractError("Kronos forecast_path volume/amount 不得为负")
    averaged = paths.mean(axis=0)
    last_close = float(values[-1, 3])
    if last_close <= 0 or bool((paths[:, -1, 3] <= 0).any()):
        raise CliContractError("Kronos close 路径包含非正价格，无法计算离散度")
    terminal_log_returns = np.log(paths[:, -1, 3] / last_close)
    dispersion = float(np.std(terminal_log_returns, ddof=0))
    forecast = pd.DataFrame(averaged, columns=FEATURE_COLUMNS)
    forecast.insert(0, "timestamp", future_index.astype(str))
    return forecast, dispersion


def _future_dates(
    path: Path | None,
    as_of: pd.Timestamp,
    *,
    inference_manifest: Mapping[str, Any] | None = None,
    snapshot_root: Path | None = None,
) -> pd.DatetimeIndex:
    if path is None:
        raise CliBlocked("passed gate 的 forecast_path 必须提供 --future-timestamps")
    selected = path.resolve(strict=True)
    if (inference_manifest is None) != (snapshot_root is None):
        raise CliContractError("future timestamps provenance 参数必须成对提供")
    if inference_manifest is not None and snapshot_root is not None:
        try:
            selected = resolve_under(snapshot_root, selected, must_exist=True)
            relative = selected.relative_to(snapshot_root.resolve()).as_posix()
        except (KronosAshareRuntimeError, OSError, ValueError) as exc:
            raise CliBlocked("future timestamps 必须来自当日 inference snapshot") from exc
        matches = [
            item
            for item in inference_manifest.get("pit_files", [])
            if isinstance(item, Mapping)
            and item.get("relative_path") == relative
            and item.get("role") == "raw_response"
        ]
        if len(matches) != 1 or sha256_file(selected) != matches[0].get("sha256"):
            raise CliBlocked(
                "future timestamps 未绑定到当日 inference snapshot 的官方原始响应"
            )
        pit_relative = relative.removeprefix("pit/")
        provenance_matches: list[Mapping[str, Any]] = []
        for item in inference_manifest.get("pit_files", []):
            if not isinstance(item, Mapping) or item.get("role") != "provenance_manifest":
                continue
            provenance_path = resolve_under(
                snapshot_root,
                snapshot_root / str(item.get("relative_path", "")),
                must_exist=True,
            )
            if sha256_file(provenance_path) != item.get("sha256"):
                raise CliBlocked("future timestamps provenance manifest 哈希漂移")
            provenance = _json_file(provenance_path)
            if provenance.get("schema_version") != PIT_PROVENANCE_SCHEMA:
                raise CliBlocked("future timestamps provenance schema 无效")
            for source in provenance.get("sources", []):
                if isinstance(source, Mapping) and source.get("path") == pit_relative:
                    provenance_matches.append(source)
        if len(provenance_matches) != 1:
            raise CliBlocked(
                "future timestamps 必须唯一绑定专用 trading_calendar provenance"
            )
        calendar_source = provenance_matches[0]
        calendar_url = str(calendar_source.get("url", ""))
        parsed_url = urlsplit(calendar_url)
        official_host = (parsed_url.hostname or "").lower().rstrip(".")
        if (
            calendar_source.get("source_class") != "official_primary"
            or calendar_source.get("role") != "authoritative"
            or calendar_source.get("artifact_role")
            != TRADING_CALENDAR_ARTIFACT_ROLE
            or calendar_source.get("artifact_schema_version")
            != TRADING_CALENDAR_ARTIFACT_SCHEMA
            or calendar_source.get("sha256") != matches[0].get("sha256")
            or parsed_url.scheme.lower() != "https"
            or not any(
                official_host == domain or official_host.endswith(f".{domain}")
                for domain in TRADING_CALENDAR_OFFICIAL_DOMAINS
            )
        ):
            raise CliBlocked(
                "future timestamps 必须绑定允许官方域名及固定 schema 的 "
                "trading_calendar 工件"
            )
    frame = pd.read_csv(selected)
    if list(frame.columns) != ["timestamps"]:
        raise CliContractError("future timestamps CSV 必须精确符合 trading_calendar schema")
    values = pd.DatetimeIndex(pd.to_datetime(frame["timestamps"], errors="coerce"))
    if values.isna().any() or len(values) < HORIZON:
        raise CliContractError("future timestamps 必须包含至少10个有效交易日期")
    if values.tz is not None:
        values = values.tz_convert(as_of.tzinfo).tz_localize(None) if as_of.tzinfo else values.tz_localize(None)
    local_as_of = _local_naive(as_of)
    if not values.equals(values.normalize()):
        raise CliContractError("future timestamps 必须是日频交易日期，不接受时分秒")
    if (
        values.has_duplicates
        or not values.is_monotonic_increasing
    ):
        raise CliContractError("future timestamps 必须严格递增且不重复")
    future = values[values > local_as_of.normalize()]
    if len(future) < HORIZON:
        raise CliContractError("future timestamps 在 as_of 后不足10个交易日期")
    future = future[:HORIZON]
    if bool((future.weekday >= 5).any()):
        raise CliContractError("future timestamps 含周末，不能作为权威交易日历")
    return future


def _command_score_as_of_impl(args: argparse.Namespace) -> dict[str, Any]:
    import torch
    from kronos_a_share_model import KronosScoringHead
    from kronos_a_share_training import CheckpointStore

    context = build_context(
        args.config, create=True, variant=getattr(args, "_variant", None)
    )
    as_of = _daily_score_as_of(args.as_of or context.config["data"]["as_of"])
    as_of_text = as_of.isoformat()
    requested = [_standard_ticker(value) for value in args.symbols]
    try:
        binding = _binding(context)
        gate = _validate_gate(context, binding)
        gate_path = context.checkpoint_dir / "gate.json"
        gate_sha256 = sha256_file(gate_path)
        gate_receipt = _verify_gate_receipt(context, gate_path, gate)
        gate_receipt_path = (
            context.checkpoint_dir
            / "gate-receipts"
            / f"{gate_sha256}.json"
        )
        release_receipt_binding = {
            "schema_version": "kronos-a-share-gate-receipt-binding-v2",
            "gate_sha256": gate_sha256,
            "gate_receipt_sha256": sha256_file(gate_receipt_path),
            "gate_receipt_schema_version": gate_receipt["schema_version"],
            "gate_receipt_path": gate_receipt_path.relative_to(
                context.layout.root
            ).as_posix(),
            "gate_sequence": gate["gate_sequence"],
        }
        verify_immutable_snapshot(
            _snapshot_manifest_path(context),
            training_root=context.layout.root,
            project_root=PROJECT_ROOT,
        )
        inference_manifest, inference_market_root, inference_pit_root = (
            _inference_snapshot_inputs(
                context,
                getattr(args, "inference_snapshot", None),
                as_of,
            )
        )
    except (CliBlocked, AShareDataError) as exc:
        records = [
            _blocked_score_record(
                context,
                as_of=as_of_text,
                ticker=ticker,
                adapter_hash=None,
                flags=[str(exc)],
            )
            for ticker in requested
        ]
        return _envelope(
            "score-as-of",
            status="unverified",
            message="模型未通过绑定准出，个股结果固定为 N/A。",
            records=records,
            evidence_class="model_output",
            output_type="N/A",
        )
    adapter_hash = gate.get("adapter_hash")
    research_scoring = (
        gate.get("gate_status") == "blocked"
        and gate.get("research_scoring_allowed") is True
    )
    if gate.get("gate_status") != "passed" and not research_scoring:
        records = [
            _blocked_score_record(
                context,
                as_of=as_of_text,
                ticker=ticker,
                adapter_hash=adapter_hash,
                flags=list(gate.get("reasons") or ["model_gate_blocked"]),
            )
            for ticker in requested
        ]
        return _envelope(
            "score-as-of",
            status="unverified",
            message="准出门为 blocked，个股结果固定为 N/A。",
            records=records,
            evidence_class="model_output",
            output_type="N/A",
        )
    future = _future_dates(
        args.future_timestamps,
        as_of,
        inference_manifest=inference_manifest,
        snapshot_root=inference_market_root.parent,
    )
    store = CheckpointStore(context.checkpoint_dir, binding)
    manifest = store.inspect(gate["evaluated_checkpoint"])
    if manifest["files"]["state.pt"]["sha256"] != gate.get(
        "scorer_checkpoint_hash"
    ):
        raise CliBlocked("gate scorer_checkpoint_hash 与 evaluated checkpoint 不一致")
    if manifest["stage"] != "scorer":
        raise CliBlocked("score-as-of 需要通过准出的 scorer checkpoint")
    _, observed_adapter_hash, _ = _scorer_checkpoint_hashes(store, manifest)
    if observed_adapter_hash != adapter_hash:
        raise CliBlocked("gate adapter_hash 与 scorer 绑定的 adapter 不一致")
    components = _load_kronos_components(context, args.device)
    head = KronosScoringHead(832).to(components.device)
    store.load(
        gate["evaluated_checkpoint"],
        model=components.model,
        scoring_head=head,
        restore_rng=False,
        map_location=components.device,
    )
    universe = _active_universe(inference_pit_root, as_of)
    corporate_actions_path = _pit_table_path(
        inference_pit_root, "corporate_actions"
    )
    if corporate_actions_path is None:
        raise CliBlocked("production score 缺少点时公司行动表")
    corporate_actions = load_corporate_actions(corporate_actions_path)
    trading_calendar_path = _pit_table_path(
        inference_pit_root, "trading_calendar"
    )
    if trading_calendar_path is None:
        raise CliBlocked("production score 缺少 inference PIT trading_calendar")
    required_open_dates = _official_open_sessions_as_of(
        trading_calendar_path, as_of
    )
    histories: dict[str, pd.DataFrame] = {}
    adjusted_histories: dict[str, pd.DataFrame] = {}
    normalized_values: list[np.ndarray] = []
    stamps: list[np.ndarray] = []
    eligible: list[str] = []
    failures: dict[str, str] = {}
    for ticker in universe:
        try:
            history, adjusted_history, normalized = _history_as_of(
                inference_market_root,
                ticker,
                as_of,
                corporate_actions,
                required_open_dates,
            )
        except (OSError, ValueError, CliContractError) as exc:
            failures[ticker] = str(exc)
            continue
        histories[ticker] = history
        adjusted_histories[ticker] = adjusted_history
        normalized_values.append(normalized)
        stamps.append(time_stamps(history["date"].to_numpy(dtype=np.int64)))
        eligible.append(ticker)
    active_count = len(universe)
    eligible_count = len(eligible)
    _validate_score_cross_section(
        eligible_count=eligible_count, active_count=active_count
    )
    if len(eligible) < 2:
        raise CliBlocked("点时股票池可评分证券不足2只")
    scores: list[np.ndarray] = []
    chunk_size = int(args.chunk_size)
    head.eval()
    with torch.inference_mode():
        for start in range(0, len(eligible), chunk_size):
            values = torch.from_numpy(
                np.stack(normalized_values[start : start + chunk_size])
            ).to(components.device)
            s1, s2 = components.tokenizer.encode(values, half=True)
            stamp = torch.from_numpy(np.stack(stamps[start : start + chunk_size])).to(
                components.device
            ).long()
            _, context_states = components.model.decode_s1(s1, s2, stamp=stamp)
            batch_scores = head(
                context_states[:, LOOKBACK - 1 : LOOKBACK], history_length=1
            )
            scores.append(batch_scores.detach().cpu().numpy())
    raw_scores = np.concatenate(scores)
    ranking = pd.Series(raw_scores).rank(method="average", pct=True).to_numpy()
    score_map = dict(zip(eligible, raw_scores, strict=True))
    percentile_map = dict(zip(eligible, ranking, strict=True))
    runtime_root = Path(context.config["runtime"]["kronos_runtime_root"])
    paths = __import__("run_kronos_forecast").runtime_paths(runtime_root)
    if str(paths["source"]) not in sys.path:
        sys.path.insert(0, str(paths["source"]))
    from model import KronosPredictor

    predictor = KronosPredictor(
        components.model,
        components.tokenizer,
        device=components.device,
        max_context=512,
    )
    records: list[dict[str, Any]] = []
    for display_ticker in requested:
        ticker = normalize_ticker(display_ticker)
        if ticker not in score_map:
            records.append(
                _blocked_score_record(
                    context,
                    as_of=as_of_text,
                    ticker=display_ticker,
                    adapter_hash=adapter_hash,
                    flags=[failures.get(ticker, "not_in_point_in_time_csi800")],
                )
            )
            continue
        history = histories[ticker]
        history_timestamps = pd.Series(
            pd.to_datetime(history["date"].astype(str), format="%Y%m%d")
        )
        with torch.inference_mode():
            forecast, path_dispersion = _forecast_path_samples(
                predictor,
                adjusted_history=adjusted_histories[ticker],
                history_timestamps=history_timestamps,
                future_timestamps=future,
                sample_count=int(args.sample_count),
                temperature=float(args.temperature),
                top_k=int(args.top_k),
                top_p=float(args.top_p),
            )
        records.append(
            {
                "as_of": as_of_text,
                "ticker": display_ticker,
                "horizon": HORIZON,
                "raw_score": float(score_map[ticker]),
                "percentile": float(percentile_map[ticker]),
                "forecast_path": forecast.to_dict(orient="records"),
                "path_dispersion": path_dispersion,
                "dataset_id": context.dataset_id,
                "run_id": context.run_id,
                "adapter_hash": adapter_hash,
                "inference_snapshot_id": inference_manifest["snapshot_id"],
                "inference_input_sha256": inference_manifest["input_sha256"],
                "gate_status": gate["gate_status"],
                "constraint_flags": (
                    ["sample_count_one_dispersion_is_zero_by_definition"]
                    if args.sample_count == 1
                    else []
                )
                + (["forward_observation_research_only"] if research_scoring else []),
                "evidence_class": "model_output",
                "output_type": "model_output",
            }
        )
    internal_output_type = (
        "model_output"
        if all(item["output_type"] == "model_output" for item in records)
        else "N/A"
    )
    forward_registry = None
    forward_commitment = None
    if internal_output_type == "model_output" and research_scoring:
        forward_registry = record_forward_batch(
            training_root=context.layout.root,
            registry_root=context.layout.registry / "forward-observations",
            as_of=as_of,
            records=records,
            universe_scores=[
                {
                    "ticker": _standard_ticker(ticker),
                    "raw_score": float(score_map[ticker]),
                    "percentile": float(percentile_map[ticker]),
                }
                for ticker in eligible
            ],
            gate=gate,
            inference_input_binding=inference_manifest["input_binding"],
            inference_input_sha256=inference_manifest["input_sha256"],
            inference_snapshot_id=inference_manifest["snapshot_id"],
            inference_manifest_path=Path(inference_manifest["_manifest_path"]),
            inference_manifest_sha256=inference_manifest[
                "_manifest_file_sha256"
            ],
            future_calendar_path=args.future_timestamps,
            release_receipt_binding=release_receipt_binding,
            authoritative_future_trading_dates=[
                timestamp.date().isoformat() for timestamp in future
            ],
            minimum_days=int(
                context.config["evaluation"]["forward_observation_min_days"]
            ),
            recommended_days=int(
                context.config["evaluation"][
                    "forward_observation_recommended_days"
                ]
            ),
        )
        forward_commitment = _public_forward_commitment(forward_registry)
    if research_scoring and internal_output_type == "model_output":
        records = [
            _blocked_score_record(
                context,
                as_of=as_of_text,
                ticker=ticker,
                adapter_hash=adapter_hash,
                flags=list(gate.get("reasons") or ["forward_observation_pending"]),
            )
            for ticker in requested
        ]
        output_type = "N/A"
    else:
        output_type = internal_output_type
    return _envelope(
        "score-as-of",
        status="ok" if output_type == "model_output" else "unverified",
        message=(
            "前瞻研究预测已写入不可变账本；未满观察期，对外结果固定为 N/A。"
            if research_scoring and forward_registry is not None
            else "点时横截面评分完成；结果仅为 model_output。"
        ),
        records=records,
        eligible_universe_count=len(eligible),
        excluded_universe_count=len(failures),
        inference_snapshot_id=inference_manifest["snapshot_id"],
        inference_input_sha256=inference_manifest["input_sha256"],
        forward_registry=forward_commitment,
        evidence_class="model_output",
        output_type=output_type,
    )


def command_score_as_of(args: argparse.Namespace) -> dict[str, Any]:
    """Keep the per-ticker N/A contract for every operational scoring failure."""

    try:
        return _command_score_as_of_impl(args)
    except (
        AShareDataError,
        CliBlocked,
        CliContractError,
        DatasetBuildError,
        ForwardRegistryError,
        KronosAshareRuntimeError,
        KeyError,
        OSError,
        OverflowError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        context = build_context(
            args.config,
            create=True,
            variant=getattr(args, "_variant", None),
        )
        raw_as_of = args.as_of or context.config["data"]["as_of"]
        try:
            as_of_text = _daily_score_as_of(raw_as_of).isoformat()
        except CliContractError:
            as_of_text = str(raw_as_of)
        records: list[dict[str, Any]] = []
        for value in args.symbols:
            try:
                ticker = _standard_ticker(value)
            except (CliContractError, ValueError):
                ticker = str(value)
            records.append(
                _blocked_score_record(
                    context,
                    as_of=as_of_text,
                    ticker=ticker,
                    adapter_hash=None,
                    flags=[f"score_fail_closed:{exc}"],
                )
            )
        return _envelope(
            "score-as-of",
            status="unverified",
            message="评分过程未满足完整合同，逐证券结果固定为 N/A。",
            records=records,
            evidence_class="model_output",
            output_type="N/A",
        )


def _read_only_checkpoint_store(
    checkpoint_root: Path,
    reference: str,
    context: WorkflowContext,
):
    from kronos_a_share_training import CheckpointBinding, CheckpointStore

    checkpoint_root = resolve_under(
        context.layout.root,
        checkpoint_root,
        must_exist=True,
    )
    resolved_reference = reference
    if reference in {"latest", "best"}:
        pointer = _json_file(
            resolve_under(checkpoint_root, f"{reference}.json", must_exist=True)
        )
        resolved_reference = str(pointer.get("checkpoint_name", ""))
    manifest_path = resolve_under(
        checkpoint_root,
        Path(resolved_reference) / "manifest.json",
        must_exist=True,
    )
    manifest = _json_file(manifest_path)
    binding = CheckpointBinding.from_mapping(manifest.get("binding", {}))
    if binding.base_model_sha256 != context.config["model"]["model_sha256"]:
        raise CliBlocked("只读诊断 checkpoint 的 Base 哈希与当前固定模型不一致")
    if binding.tokenizer_sha256 != context.config["model"]["tokenizer_sha256"]:
        raise CliBlocked("只读诊断 checkpoint 的 Tokenizer 哈希与当前固定模型不一致")
    return CheckpointStore(checkpoint_root, binding)


def _read_only_adapter_replay_diagnostic(
    context: WorkflowContext,
    *,
    store: Any,
    checkpoint_references: Sequence[str],
    token_dir: Path,
    repeats: int,
    batch_size: int,
    device: str,
) -> dict[str, Any]:
    from kronos_a_share_model import validate_kronos_base_adapter_parameter_count
    from kronos_a_share_training import (
        prepare_adapter_stage,
        select_validated_adapter,
        set_deterministic_seed,
    )

    if repeats < 2 or repeats > 10:
        raise CliContractError("diagnostic-repeats 必须位于 2..10")
    if batch_size < 1:
        raise CliContractError("diagnostic-batch-size 必须为正整数")
    token_dir = resolve_under(
        context.layout.root,
        token_dir,
        must_exist=True,
    )
    cache = load_token_cache(
        token_dir,
        mmap_mode=None,
        diagnostic_legacy_read_only=True,
    )
    if cache.get("diagnostic_legacy_read_only") is not True:
        raise CliContractError(
            "只读重放仅用于缺少 active_member_count 的 legacy smoke token cache"
        )
    manifest = cache["manifest"]
    adjustment = manifest.get("adjustment")
    if not isinstance(adjustment, Mapping) or adjustment.get("materialized") is not False:
        raise CliContractError("legacy 诊断 token 状态与已知 local_provisional 合同不符")
    for path_field, hash_field in (
        ("sample_index_path", "sample_index_sha256"),
        ("sample_manifest_path", "sample_manifest_sha256"),
    ):
        source_path = resolve_under(
            context.layout.root,
            manifest.get(path_field, ""),
            must_exist=True,
        )
        if sha256_file(source_path) != manifest.get(hash_field):
            raise CliBlocked(f"legacy 诊断 {path_field} 哈希漂移")

    arrays = cache["arrays"]
    valid_members = np.flatnonzero(
        np.asarray(arrays["split"]) == SPLIT_CODES["validation"]
    )
    if len(valid_members) < 1:
        raise CliContractError("legacy 诊断 validation split 没有样本")
    if not checkpoint_references:
        raise CliContractError("只读 CE 重放至少需要一个 adapter checkpoint")
    checkpoint_manifests: list[tuple[str, dict[str, Any]]] = []
    observed_steps: set[int] = set()
    for reference in checkpoint_references:
        checkpoint_manifest = store.inspect_read_only(reference)
        step = int(checkpoint_manifest.get("step", -1))
        if checkpoint_manifest.get("stage") != "adapter" or step < 1:
            raise CliContractError("只读 CE 重放只接受 adapter checkpoint")
        if step in observed_steps:
            raise CliContractError("只读 CE 重放 checkpoint step 不得重复")
        observed_steps.add(step)
        checkpoint_manifests.append((reference, checkpoint_manifest))

    results: list[dict[str, Any]] = []
    replay_targets: list[tuple[str, dict[str, Any] | None]] = [
        ("step0_zero_shot", None),
        *checkpoint_manifests,
    ]
    for label, checkpoint_manifest in replay_targets:
        values: list[float] = []
        for repeat_index in range(repeats):
            set_deterministic_seed(int(context.config["training"]["seed"]))
            components = _load_kronos_components(context, device)
            model = components.model
            if checkpoint_manifest is None:
                lora = checkpoint_manifests[0][1]["lora"]
                prepare_adapter_stage(
                    model,
                    rank=int(lora["rank"]),
                    alpha=float(lora["alpha"]),
                    dropout=float(lora["dropout"]),
                )
            else:
                store.load(
                    label,
                    model=model,
                    restore_rng=False,
                    map_location=components.device,
                    read_only=True,
                )
            validate_kronos_base_adapter_parameter_count(model)
            values.append(
                _validation_adapter_ce(
                    model,
                    arrays,
                    valid_members,
                    batch_size=batch_size,
                    device=components.device,
                )
            )
            del model, components
        spread = max(values) - min(values)
        results.append(
            {
                "reference": label,
                "step": (
                    0
                    if checkpoint_manifest is None
                    else int(checkpoint_manifest["step"])
                ),
                "causal_validation_ce": values,
                "mean_causal_validation_ce": float(np.mean(values)),
                "ce_spread": spread,
                "deterministic_within_1e_5": spread <= 1e-5,
            }
        )

    selection = select_validated_adapter(
        [
            {
                "step": item["step"],
                "validation_ce": item["mean_causal_validation_ce"],
            }
            for item in results[1:]
        ],
        zero_shot_validation_ce=results[0]["mean_causal_validation_ce"],
        minimum_improvement=float(
            context.config["evaluation"]["adapter_ce_improvement_min"]
        ),
    )
    deterministic = all(item["deterministic_within_1e_5"] for item in results)
    return {
        "schema_version": "kronos-a-share-read-only-adapter-replay-v1",
        "diagnostic_only": True,
        "data_status": "local_provisional",
        "token_cache": str(token_dir),
        "token_cache_schema_version": manifest.get("schema_version"),
        "checkpoint_references": [item[0] for item in checkpoint_manifests],
        "repeats": repeats,
        "sample_count": int(len(valid_members)),
        "results": results,
        "live_validation_history": [
            {
                "step": item["step"],
                "validation_ce": item["mean_causal_validation_ce"],
            }
            for item in results[1:]
        ],
        "deterministic_replay_passed": deterministic,
        "selector": {
            "best_step": selection.best_step,
            "best_validation_ce": selection.best_validation_ce,
            "improvement": selection.improvement,
            "zero_shot_fallback": selection.zero_shot_fallback,
            "selection_reason": selection.selection_reason,
        },
        "formal_gate_eligible": False,
        "output_type": "N/A",
    }


def command_inspect_checkpoint(args: argparse.Namespace) -> dict[str, Any]:
    from kronos_a_share_training import CheckpointStore

    requested_variant = getattr(args, "_variant", None)
    if requested_variant is None and getattr(args, "mode", "full") == "smoke":
        requested_variant = "smoke"
    context = build_context(
        args.config,
        create=False,
        variant=requested_variant,
        training_profile=(
            "engineering_smoke"
            if getattr(args, "mode", "full") == "smoke"
            else "full"
        ),
    )
    diagnostic_root = getattr(args, "read_only_checkpoint_dir", None)
    if diagnostic_root is not None:
        if args.recover:
            raise CliContractError("只读 checkpoint 诊断不得执行 --recover")
        store = _read_only_checkpoint_store(
            diagnostic_root,
            args.checkpoint,
            context,
        )
        recovery = None
        manifest = store.inspect_read_only(args.checkpoint)
    else:
        store = CheckpointStore(context.checkpoint_dir, _binding(context))
        recovery = store.recover() if args.recover else None
        manifest = store.inspect(args.checkpoint)
    diagnostic = None
    diagnostic_artifact = None
    diagnostic_token_dir = getattr(args, "diagnostic_token_dir", None)
    if diagnostic_token_dir is not None:
        if diagnostic_root is None:
            raise CliContractError(
                "--diagnostic-token-dir 必须配合 --read-only-checkpoint-dir"
            )
        diagnostic = _read_only_adapter_replay_diagnostic(
            context,
            store=store,
            checkpoint_references=(
                args.diagnostic_checkpoints
                if args.diagnostic_checkpoints is not None
                else [args.checkpoint]
            ),
            token_dir=diagnostic_token_dir,
            repeats=int(args.diagnostic_repeats),
            batch_size=int(args.diagnostic_batch_size),
            device=args.device,
        )
    diagnostic_output = getattr(args, "diagnostic_output", None)
    if diagnostic_output is not None:
        if diagnostic is None or diagnostic_root is None:
            raise CliContractError(
                "--diagnostic-output 只允许持久化只读 adapter CE 重放"
            )
        output_path = resolve_under(context.layout.root, diagnostic_output)
        if output_path.exists():
            raise CliContractError("diagnostic-output 已存在，拒绝覆盖审计工件")
        artifact_payload = {
            "schema_version": "kronos-a-share-read-only-diagnostic-artifact-v1",
            "generated_at": _utc_now(),
            "checkpoint_root": str(
                resolve_under(context.layout.root, diagnostic_root, must_exist=True)
            ),
            "checkpoint_manifest": manifest,
            "diagnostic": diagnostic,
        }
        atomic_write_json(
            output_path,
            artifact_payload,
            allowed_root=context.layout.root,
        )
        diagnostic_artifact = {
            "path": str(output_path),
            "bytes": output_path.stat().st_size,
            "sha256": sha256_file(output_path),
        }
    gate_path = context.checkpoint_dir / "gate.json"
    gate: dict[str, Any] | None = None
    gate_integrity = "missing"
    gate_error: str | None = None
    if diagnostic_root is None and gate_path.is_file():
        try:
            gate = _validate_gate(context, _binding(context))
            gate_integrity = "verified"
        except CliBlocked as exc:
            gate_integrity = "blocked"
            gate_error = str(exc)
    return _envelope(
        "inspect-checkpoint",
        status="unverified" if gate_integrity == "blocked" else "ok",
        message=(
            "checkpoint 通过，但 gate 完整性验证失败。"
            if gate_integrity == "blocked"
            else "checkpoint 完整性与哈希绑定检查通过。"
        ),
        checkpoint=manifest,
        checkpoint_integrity="verified",
        gate=gate,
        gate_integrity=gate_integrity,
        gate_error=gate_error,
        recovery=recovery,
        read_only=diagnostic_root is not None,
        diagnostic=diagnostic,
        diagnostic_artifact=diagnostic_artifact,
        evidence_class="model_output_checkpoint",
        output_type="N/A" if diagnostic is not None else "model_output",
    )


def command_pipeline(args: argparse.Namespace) -> dict[str, Any]:
    smoke = args.mode == "smoke"
    variant = "smoke" if smoke else None
    context = build_context(args.config, create=True, variant=variant)
    steps: list[dict[str, Any]] = []
    steps.append(
        command_check(
            SimpleNamespace(
                config=args.config,
                device=args.device,
                load_model=True,
                _variant=variant,
            )
        )
    )
    if steps[-1]["status"] == "blocked":
        raise CliBlocked("资源 preflight 未通过，pipeline 未启动")
    steps.append(
        command_snapshot(
            SimpleNamespace(
                config=args.config,
                dry_run=False,
                reuse=True,
                _variant=variant,
            )
        )
    )
    steps.append(
        command_prepare(
            SimpleNamespace(
                config=args.config,
                pit_root=args.pit_root,
                max_samples_per_split=(args.smoke_samples_per_split if smoke else None),
                force=False,
                tokenize=True,
                device=args.device,
                _variant=variant,
            )
        )
    )
    prepared_status = steps[-1]["data_status"]
    if not smoke and prepared_status != "production_ready":
        raise CliBlocked("full pipeline 只接受 production_ready，未启动训练")
    adapter_settings = context.config["training"]["adapter"]
    adapter_step = command_train_adapter(
        SimpleNamespace(
            config=args.config,
            engineering_smoke=smoke,
            device=args.device,
            resume="auto",
            stop_after=(
                SMOKE_MAX_STEPS
                if smoke
                else int(adapter_settings["max_steps"])
            ),
            learning_rate=None,
            seed=None,
            _variant=variant,
        )
    )
    steps.append(adapter_step)
    if smoke:
        steps.append(
            command_inspect_checkpoint(
                SimpleNamespace(
                    config=args.config,
                    checkpoint="latest",
                    recover=True,
                    mode="smoke",
                    _variant=variant,
                )
            )
        )
        return _envelope(
            "pipeline",
            status="unverified",
            message=(
                "smoke 仅完成显存、NaN、因果 CE、checkpoint "
                "与恢复验证；未训练 scorer，未产生质量 RankIC。"
            ),
            mode="smoke",
            data_status=prepared_status,
            gate_status="blocked",
            steps=steps,
            evidence_class="model_output",
            output_type="N/A",
        )
    if adapter_step["training"].get("zero_shot_fallback") is True:
        return _envelope(
            "pipeline",
            status="blocked",
            message="Adapter 未达到 zero-shot CE 改善门槛，已停止 scorer 与正式评估。",
            mode="full",
            data_status=prepared_status,
            gate_status="blocked",
            steps=steps,
            evidence_class="model_output",
            output_type="N/A",
        )
    steps.append(
        command_train_scorer(
            SimpleNamespace(
                config=args.config,
                engineering_smoke=False,
                device=args.device,
                adapter="best",
                resume="auto",
                max_epochs=None,
                chunk_size=args.chunk_size,
                _variant=variant,
            )
        )
    )
    evaluation = command_evaluate(
        SimpleNamespace(
            config=args.config,
            checkpoint="best",
            split="validation",
            input=args.evaluation_input,
            chunk_size=args.chunk_size,
            device=args.device,
            _variant=variant,
        )
    )
    steps.append(evaluation)
    passed = evaluation["gate"]["gate_status"] == "passed"
    return _envelope(
        "pipeline",
        status="ok" if passed else "unverified",
        message=(
            "完整流水线通过准出；结果仍仅是 model_output。"
            if passed
            else (
                "smoke 工程链路完成；gate 保持 blocked/unverified。"
                if smoke
                else "full 流水线完成但未通过模型准出。"
            )
        ),
        mode=args.mode,
        data_status=prepared_status,
        gate_status=evaluation["gate"]["gate_status"],
        steps=steps,
        evidence_class="model_output",
        output_type="model_output" if passed else "N/A",
    )


def _add_config(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Kronos-base A股 PIT、LoRA、评分头与样本外准出统一入口"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="创建或审计不可变 TDX 快照")
    _add_config(snapshot)
    snapshot.add_argument("--dry-run", action="store_true")
    snapshot.add_argument("--reuse", action="store_true")
    snapshot.add_argument("--inference-as-of")
    snapshot.add_argument("--inference-pit-root", type=Path)

    prepare = commands.add_parser("prepare", help="构建 PIT 数据门、样本索引与 token cache")
    _add_config(prepare)
    prepare.add_argument("--pit-root", type=Path)
    prepare.add_argument("--pit-normalization-manifest", type=Path)
    prepare.add_argument("--tokenize", action="store_true")
    prepare.add_argument("--max-samples-per-split", type=int)
    prepare.add_argument("--force", action="store_true")
    prepare.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")

    check = commands.add_parser("check", help="检查路径、资源、哈希和本地模型")
    _add_config(check)
    check.add_argument("--load-model", action="store_true")
    check.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")

    adapter = commands.add_parser("train-adapter", help="训练 future-only CE LoRA")
    _add_config(adapter)
    adapter.add_argument("--resume", default="auto")
    adapter.add_argument("--stop-after", type=int)
    adapter.add_argument("--engineering-smoke", action="store_true")
    adapter.add_argument("--learning-rate", type=float)
    adapter.add_argument("--seed", type=int)
    adapter.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")

    scorer = commands.add_parser("train-scorer", help="训练同日横截面评分头")
    _add_config(scorer)
    scorer.add_argument("--adapter", default="best")
    scorer.add_argument("--resume", default="auto")
    scorer.add_argument("--max-epochs", type=int)
    scorer.add_argument("--chunk-size", type=int, default=16)
    scorer.add_argument("--engineering-smoke", action="store_true")
    scorer.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")

    evaluate = commands.add_parser("evaluate", help="滚动样本外评估并原子写 gate.json")
    _add_config(evaluate)
    evaluate.add_argument("--checkpoint", default="best")
    evaluate.add_argument(
        "--split",
        choices=["validation", "development_test", "locked_retrospective"],
        default="validation",
    )
    evaluate.add_argument("--input", type=Path)
    evaluate.add_argument("--chunk-size", type=int, default=16)
    evaluate.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")

    score = commands.add_parser("score-as-of", help="对准出模型做点时横截面评分")
    _add_config(score)
    score.add_argument("--symbols", nargs="+", required=True)
    score.add_argument("--as-of", required=True)
    score.add_argument("--inference-snapshot", type=Path)
    score.add_argument("--future-timestamps", type=Path)
    score.add_argument("--chunk-size", type=int, default=16)
    score.add_argument("--temperature", type=float, default=1.0)
    score.add_argument("--top-k", type=int, default=0)
    score.add_argument("--top-p", type=float, default=0.9)
    score.add_argument("--sample-count", type=int, default=1)
    score.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")

    inspect = commands.add_parser("inspect-checkpoint", help="检查 checkpoint 与 gate 哈希")
    _add_config(inspect)
    inspect.add_argument("--checkpoint", default="latest")
    inspect.add_argument("--recover", action="store_true")
    inspect.add_argument("--mode", choices=["full", "smoke"], default="full")
    inspect.add_argument("--read-only-checkpoint-dir", type=Path)
    inspect.add_argument("--diagnostic-token-dir", type=Path)
    inspect.add_argument("--diagnostic-checkpoints", nargs="+")
    inspect.add_argument("--diagnostic-output", type=Path)
    inspect.add_argument("--diagnostic-repeats", type=int, default=3)
    inspect.add_argument("--diagnostic-batch-size", type=int, default=16)
    inspect.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")

    pipeline = commands.add_parser("pipeline", help="运行 smoke 或 full 受控流水线")
    _add_config(pipeline)
    pipeline.add_argument("--mode", choices=["smoke", "full"], required=True)
    pipeline.add_argument("--pit-root", type=Path)
    pipeline.add_argument("--evaluation-input", type=Path)
    pipeline.add_argument("--smoke-samples-per-split", type=int, default=64)
    pipeline.add_argument("--chunk-size", type=int, default=16)
    pipeline.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    return parser


COMMANDS = {
    "snapshot": command_snapshot,
    "prepare": command_prepare,
    "check": command_check,
    "train-adapter": command_train_adapter,
    "train-scorer": command_train_scorer,
    "evaluate": command_evaluate,
    "score-as-of": command_score_as_of,
    "inspect-checkpoint": command_inspect_checkpoint,
    "pipeline": command_pipeline,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if getattr(args, "chunk_size", 1) < 1:
            raise CliContractError("chunk-size 必须为正整数")
        if getattr(args, "sample_count", 1) < 1:
            raise CliContractError("sample-count 必须为正整数")
        if not 0 < getattr(args, "top_p", 0.9) <= 1:
            raise CliContractError("top-p 必须位于 (0,1]")
        if getattr(args, "temperature", 1.0) <= 0:
            raise CliContractError("temperature 必须大于0")
        payload = COMMANDS[args.command](args)
        print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
        if args.command == "pipeline" and args.mode == "full" and payload["status"] != "ok":
            return 2
        return 0
    except CliBlocked as exc:
        payload = _envelope(
            args.command,
            status="blocked",
            message=str(exc),
            evidence_class="model_output",
            output_type="N/A",
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as exc:
        payload = _envelope(
            args.command,
            status="error",
            message=f"Kronos A股执行失败：{exc}",
            evidence_class="model_output",
            output_type="N/A",
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
