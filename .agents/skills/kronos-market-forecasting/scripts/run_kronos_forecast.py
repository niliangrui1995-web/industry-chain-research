#!/usr/bin/env python3
"""Validate and run the project-local Kronos-base checkpoint offline."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_RUNTIME_ROOT = REPO_ROOT / "_downloads" / "Kronos"
SOURCE_REVISION = "67b630e67f6a18c9e9be918d9b4337c960db1e9a"
MODEL_REVISION = "2b554741eca47781b64468546e77fef3e85130e6"
TOKENIZER_REVISION = "0e0117387f39004a9016484a186a908917e22426"
MODEL_CONFIG_SHA256 = "77ebc3038b647709b92be002f801d72e1a385f4c8c2c5aa1cc6cf21fcfe44eb2"
TOKENIZER_CONFIG_SHA256 = "2366e7ccfec76cbc19cf3c4c1b9c5d901be336ca1e83f2d2292c9bff381b77a2"
MODEL_SHA256 = "abff193acab6db1a0368e9773e75799d11403b6d054ee6d5f0a11aeabc5f4b83"
TOKENIZER_SHA256 = "59d85f6af76a2c3b8240ea06cb21db4213b4eeca053f246b23e29cf832fc6bee"
PRICE_COLUMNS = ["open", "high", "low", "close"]
OPTIONAL_COLUMNS = ["volume", "amount"]
MAX_CONTEXT = 512
ADAPTER_GATE_SCHEMA_VERSION = "kronos-a-share-gate-v2"
ADAPTER_GATE_RECEIPT_SCHEMA_VERSION = "kronos-a-share-gate-receipt-v2"
ADAPTER_GATE_HEAD_SCHEMA_VERSION = "kronos-a-share-gate-head-v1"


class KronosRuntimeError(RuntimeError):
    """Raised when the local runtime or input contract is invalid."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_sha256(payload: dict[str, Any]) -> str:
    return sha256_bytes(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )


def validate_file_hash(path: Path, expected: str, label: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise KronosRuntimeError(f"{label} SHA256 不匹配：expected={expected}, actual={actual}")
    return actual


def validate_source_checkout(source: Path, expected_revision: str) -> str:
    revision_proc = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if revision_proc.returncode != 0:
        raise KronosRuntimeError(f"无法读取 Kronos 源码 revision：{revision_proc.stderr.strip()}")
    revision = revision_proc.stdout.strip()
    if revision != expected_revision:
        raise KronosRuntimeError(
            f"Kronos 源码 revision 漂移：expected={expected_revision}, actual={revision}"
        )

    status_proc = subprocess.run(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if status_proc.returncode != 0:
        raise KronosRuntimeError(f"无法核验 Kronos 源码工作树：{status_proc.stderr.strip()}")
    if status_proc.stdout.strip():
        raise KronosRuntimeError("Kronos 源码工作树存在修改或未跟踪文件；拒绝报告固定 revision")
    return revision


def runtime_paths(runtime_root: Path) -> dict[str, Path]:
    return {
        "source": runtime_root / "source",
        "model": runtime_root / "Kronos-base",
        "tokenizer": runtime_root / "Kronos-Tokenizer-base",
    }


def validate_runtime(runtime_root: Path) -> dict[str, Any]:
    paths = runtime_paths(runtime_root)
    required = [
        paths["source"] / "model" / "__init__.py",
        paths["source"] / "model" / "kronos.py",
        paths["source"] / "model" / "module.py",
        paths["source"] / "LICENSE",
        paths["model"] / "config.json",
        paths["model"] / "model.safetensors",
        paths["tokenizer"] / "config.json",
        paths["tokenizer"] / "model.safetensors",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise KronosRuntimeError("missing_local_runtime: " + ", ".join(missing))

    for config_path in (paths["model"] / "config.json", paths["tokenizer"] / "config.json"):
        try:
            json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise KronosRuntimeError(f"配置文件无效：{config_path}: {exc}") from exc

    source_revision = validate_source_checkout(paths["source"], SOURCE_REVISION)
    model_config_hash = validate_file_hash(
        paths["model"] / "config.json", MODEL_CONFIG_SHA256, "Kronos-base config"
    )
    tokenizer_config_hash = validate_file_hash(
        paths["tokenizer"] / "config.json",
        TOKENIZER_CONFIG_SHA256,
        "Kronos-Tokenizer-base config",
    )
    model_hash = validate_file_hash(
        paths["model"] / "model.safetensors", MODEL_SHA256, "Kronos-base 权重"
    )
    tokenizer_hash = validate_file_hash(
        paths["tokenizer"] / "model.safetensors",
        TOKENIZER_SHA256,
        "Kronos-Tokenizer-base 权重",
    )

    return {
        "runtime_root": str(runtime_root.resolve()),
        "source_revision": source_revision,
        "model_revision": MODEL_REVISION,
        "tokenizer_revision": TOKENIZER_REVISION,
        "model_config_sha256": model_config_hash,
        "tokenizer_config_sha256": tokenizer_config_hash,
        "model_sha256": model_hash,
        "tokenizer_sha256": tokenizer_hash,
    }


def resolve_device(requested: str) -> tuple[str, list[str], dict[str, Any]]:
    import torch

    warnings: list[str] = []
    cuda_available = torch.cuda.is_available()
    cuda_report: dict[str, Any] = {
        "torch": torch.__version__,
        "cuda_build": torch.version.cuda,
        "cuda_available": cuda_available,
        "arch_list": torch.cuda.get_arch_list() if cuda_available else [],
    }
    cuda_supported = False
    if cuda_available:
        capability = torch.cuda.get_device_capability(0)
        target_arch = f"sm_{capability[0]}{capability[1]}"
        cuda_report.update(
            {
                "gpu": torch.cuda.get_device_name(0),
                "capability": list(capability),
                "target_arch": target_arch,
            }
        )
        cuda_supported = target_arch in cuda_report["arch_list"]

    if requested == "cpu":
        return "cpu", warnings, cuda_report
    if requested == "cuda":
        if not cuda_available:
            raise KronosRuntimeError("请求 CUDA，但 torch.cuda.is_available() 为 False")
        if not cuda_supported:
            raise KronosRuntimeError(
                f"当前 PyTorch wheel 不包含 {cuda_report.get('target_arch')}；请使用 CPU 或兼容 wheel"
            )
        return "cuda:0", warnings, cuda_report
    if cuda_available and cuda_supported:
        return "cuda:0", warnings, cuda_report
    if cuda_available and not cuda_supported:
        warnings.append("检测到 CUDA，但当前 wheel 不含本机 GPU 架构；已明确回退 CPU。")
    else:
        warnings.append("未检测到可用 CUDA；已使用 CPU。")
    return "cpu", warnings, cuda_report


def set_seed(seed: int) -> None:
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_history(
    input_path: Path,
    timestamp_column: str,
    lookback: int,
) -> tuple[pd.DataFrame, pd.Series, list[str], dict[str, Any]]:
    if not input_path.is_file():
        raise KronosRuntimeError(f"输入 CSV 不存在：{input_path}")
    payload = input_path.read_bytes()
    frame = pd.read_csv(io.BytesIO(payload))
    required = [timestamp_column, *PRICE_COLUMNS]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise KronosRuntimeError(f"输入 CSV 缺少字段：{missing}")

    timestamps = pd.to_datetime(frame[timestamp_column], errors="coerce")
    if timestamps.isna().any():
        raise KronosRuntimeError("timestamps 存在无法解析的值")
    if not is_datetime64_any_dtype(timestamps.dtype):
        raise KronosRuntimeError("timestamps 必须使用一致时区；不要混合不同时区偏移")
    if timestamps.duplicated().any():
        raise KronosRuntimeError("timestamps 存在重复值")
    if not timestamps.is_monotonic_increasing:
        raise KronosRuntimeError("timestamps 必须严格递增")

    present_features = [*PRICE_COLUMNS, *[column for column in OPTIONAL_COLUMNS if column in frame.columns]]
    for column in present_features:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    values = frame[present_features].to_numpy(dtype=np.float64)
    if not np.isfinite(values).all():
        raise KronosRuntimeError("OHLCV/amount 存在非数值、NaN 或 Inf")
    if (frame[PRICE_COLUMNS] <= 0).any().any():
        raise KronosRuntimeError("open/high/low/close 必须为正数")
    for column in OPTIONAL_COLUMNS:
        if column in frame.columns and (frame[column] < 0).any():
            raise KronosRuntimeError(f"{column} 不得为负数")

    invalid_ohlc = (
        (frame["high"] < frame[["open", "close"]].max(axis=1))
        | (frame["low"] > frame[["open", "close"]].min(axis=1))
        | (frame["high"] < frame["low"])
    )
    if invalid_ohlc.any():
        bad_rows = frame.index[invalid_ohlc].tolist()[:10]
        raise KronosRuntimeError(f"输入存在不合法 OHLC，前 10 个行号：{bad_rows}")

    warnings: list[str] = []
    if len(frame) < 2:
        raise KronosRuntimeError("至少需要 2 根历史 K 线")
    if len(frame) < lookback:
        warnings.append(f"历史仅有 {len(frame)} 根，少于请求的 lookback={lookback}；已使用全部历史。")
    history_rows = min(len(frame), lookback)
    history = frame.iloc[-history_rows:][present_features].reset_index(drop=True)
    history_timestamps = timestamps.iloc[-history_rows:].reset_index(drop=True)
    if history_rows < 64:
        warnings.append(f"有效上下文只有 {history_rows} 根；预测稳定性可能较低。")

    details = {
        "input_rows": len(frame),
        "history_rows": history_rows,
        "provided_features": present_features,
        "data_as_of": history_timestamps.iloc[-1].isoformat(),
        "input_sha256": sha256_bytes(payload),
    }
    return history, history_timestamps, warnings, details


def load_future_timestamps(
    future_path: Path | None,
    frequency: str | None,
    timestamp_column: str,
    last_history_timestamp: pd.Timestamp,
    pred_len: int,
) -> tuple[pd.Series, str, str | None, list[str]]:
    warnings: list[str] = []
    future_hash: str | None = None
    if future_path is not None:
        if not future_path.is_file():
            raise KronosRuntimeError(f"未来时间戳 CSV 不存在：{future_path}")
        payload = future_path.read_bytes()
        future_hash = sha256_bytes(payload)
        frame = pd.read_csv(io.BytesIO(payload))
        if timestamp_column not in frame.columns:
            raise KronosRuntimeError(f"未来时间戳 CSV 缺少字段：{timestamp_column}")
        future = pd.to_datetime(frame[timestamp_column], errors="coerce")
        source = f"file:{future_path.resolve()}"
    elif frequency is not None:
        try:
            future = pd.Series(
                pd.date_range(start=last_history_timestamp, periods=pred_len + 1, freq=frequency)[1:],
                name=timestamp_column,
            )
        except (TypeError, ValueError) as exc:
            raise KronosRuntimeError(f"无法按 freq={frequency!r} 生成未来时间戳：{exc}") from exc
        source = f"generated_freq:{frequency}"
        warnings.append("未来时点由 --freq 生成，未核验交易所节假日、午休、夜盘或停牌日历。")
    else:
        raise KronosRuntimeError("必须提供 --future-timestamps 或 --freq")

    if future.isna().any():
        raise KronosRuntimeError("未来时间戳存在无法解析的值")
    if not is_datetime64_any_dtype(future.dtype):
        raise KronosRuntimeError("未来时间戳必须使用一致时区；不要混合不同时区偏移")
    if len(future) != pred_len:
        raise KronosRuntimeError(f"未来时间戳行数必须等于 pred_len={pred_len}，实际为 {len(future)}")
    if future.duplicated().any() or not future.is_monotonic_increasing:
        raise KronosRuntimeError("未来时间戳必须严格递增且无重复")
    history_is_aware = last_history_timestamp.tzinfo is not None
    future_is_aware = future.iloc[0].tzinfo is not None
    if history_is_aware != future_is_aware:
        raise KronosRuntimeError("历史与未来时间戳必须同时带时区或同时不带时区")
    if history_is_aware:
        history_timezone = last_history_timestamp.tz
        future_timezone = future.dt.tz
        if str(history_timezone) != str(future_timezone):
            future = future.dt.tz_convert(history_timezone)
            warnings.append(
                f"未来时间戳已从 {future_timezone} 转换为历史时区 {history_timezone} 后再生成时间特征。"
            )
    if future.iloc[0] <= last_history_timestamp:
        raise KronosRuntimeError("第一条未来时间戳必须晚于历史末端")
    return future.reset_index(drop=True), source, future_hash, warnings


def load_predictor(runtime_root: Path, device: str):
    paths = runtime_paths(runtime_root)
    os.environ["HF_HUB_OFFLINE"] = "1"
    sys.path.insert(0, str(paths["source"]))
    from model import Kronos, KronosPredictor, KronosTokenizer

    tokenizer = KronosTokenizer.from_pretrained(paths["tokenizer"])
    model = Kronos.from_pretrained(paths["model"])
    tokenizer.eval()
    model.eval()
    return KronosPredictor(model, tokenizer, device=device, max_context=MAX_CONTEXT)


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise KronosRuntimeError(f"{label}不可解析：{path}") from exc
    if not isinstance(value, dict):
        raise KronosRuntimeError(f"{label}必须是 JSON object：{path}")
    return value


def _select_adapter_checkpoint(
    adapter_dir: Path,
) -> tuple[Path, str, Path, Path, dict[str, Any] | None, str | None]:
    """Resolve a checkpoint store/root without trusting its pointers or gate."""

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from kronos_a_share_training import CHECKPOINT_NAME_PATTERN

    requested = adapter_dir.resolve()
    if not requested.is_dir():
        raise KronosRuntimeError(f"adapter-dir 不存在或不是目录：{requested}")

    direct_checkpoint = all(
        (requested / name).is_file()
        for name in ("manifest.json", "state.pt", "COMMITTED")
    )
    if direct_checkpoint:
        root = requested.parent
        reference = requested.name
        if CHECKPOINT_NAME_PATTERN.fullmatch(reference) is None:
            raise KronosRuntimeError(f"adapter checkpoint 目录名非法：{reference}")
    else:
        root = requested
        reference = ""

    gate_path = root / "gate.json"
    gate_payload: dict[str, Any] | None = None
    gate_parse_error: str | None = None
    if gate_path.is_file():
        try:
            gate_payload = _read_json_object(gate_path, "adapter gate.json")
        except KronosRuntimeError as exc:
            gate_parse_error = str(exc)

    if not reference:
        evaluated = gate_payload.get("evaluated_checkpoint") if gate_payload else None
        if (
            isinstance(evaluated, str)
            and CHECKPOINT_NAME_PATTERN.fullmatch(evaluated) is not None
            and (root / evaluated).is_dir()
        ):
            reference = evaluated
        else:
            for pointer_name in ("best", "latest"):
                pointer_path = root / f"{pointer_name}.json"
                if not pointer_path.is_file():
                    continue
                pointer = _read_json_object(pointer_path, f"checkpoint {pointer_name} pointer")
                candidate = pointer.get("checkpoint_name")
                if not isinstance(candidate, str) or CHECKPOINT_NAME_PATTERN.fullmatch(candidate) is None:
                    raise KronosRuntimeError(f"checkpoint {pointer_name} pointer 引用非法")
                reference = pointer_name
                break
        if not reference:
            raise KronosRuntimeError(
                f"adapter store 缺少可用的 evaluated/best/latest checkpoint：{root}"
            )

    checkpoint_name = reference
    if reference in {"best", "latest"}:
        pointer = _read_json_object(root / f"{reference}.json", f"checkpoint {reference} pointer")
        checkpoint_name = pointer.get("checkpoint_name", "")
    checkpoint_path = root / checkpoint_name
    return root, reference, checkpoint_path, gate_path, gate_payload, gate_parse_error


def _adapter_gate_lineage_reasons(
    gate_path: Path,
    gate_payload: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    checkpoint_dir = gate_path.parent
    lineage_dir = checkpoint_dir / "gate-lineage"
    head_path = checkpoint_dir / "gate-head.json"
    if not lineage_dir.is_dir() or not head_path.is_file():
        return ["passed gate 缺少 active gate lineage/head"]
    files = sorted(lineage_dir.glob("*.json"))
    if not files:
        return ["passed gate 的 immutable lineage 为空"]
    previous_hash: str | None = None
    latest: dict[str, Any] | None = None
    core_fields = (
        "schema_version",
        "sequence",
        "gate_sha256",
        "gate_receipt_sha256",
        "previous_event_sha256",
        "created_at",
    )
    expected_fields = {*core_fields, "event_sha256"}
    for expected_sequence, path in enumerate(files, start=1):
        try:
            event = _read_json_object(path, "adapter gate lineage")
        except KronosRuntimeError as exc:
            reasons.append(str(exc))
            break
        if set(event) != expected_fields:
            reasons.append("adapter gate lineage 字段不匹配")
            break
        core = {field: event[field] for field in core_fields}
        try:
            event_hash = canonical_json_sha256(core)
        except (TypeError, ValueError) as exc:
            reasons.append(f"adapter gate lineage 无法哈希：{exc}")
            break
        if (
            event.get("schema_version") != ADAPTER_GATE_HEAD_SCHEMA_VERSION
            or isinstance(event.get("sequence"), bool)
            or not isinstance(event.get("sequence"), int)
            or event.get("sequence") != expected_sequence
            or event.get("previous_event_sha256") != previous_hash
            or event.get("event_sha256") != event_hash
            or path.name != f"{expected_sequence:08d}-{event_hash}.json"
        ):
            reasons.append("adapter gate lineage 序号、链或哈希不匹配")
            break
        gate_hash = event.get("gate_sha256")
        receipt_hash = event.get("gate_receipt_sha256")
        if not isinstance(gate_hash, str) or len(gate_hash) != 64:
            reasons.append("adapter gate lineage gate SHA256 无效")
            break
        receipt_path = checkpoint_dir / "gate-receipts" / f"{gate_hash}.json"
        if (
            not receipt_path.is_file()
            or not isinstance(receipt_hash, str)
            or sha256_file(receipt_path) != receipt_hash
        ):
            reasons.append("adapter gate lineage receipt 缺失或漂移")
            break
        try:
            receipt = _read_json_object(receipt_path, "adapter gate lineage receipt")
        except KronosRuntimeError as exc:
            reasons.append(str(exc))
            break
        if (
            receipt.get("schema_version") != ADAPTER_GATE_RECEIPT_SCHEMA_VERSION
            or receipt.get("gate_sha256") != gate_hash
            or receipt.get("gate_sequence") != expected_sequence
        ):
            reasons.append("adapter gate lineage 与 receipt 语义不一致")
            break
        previous_hash = event_hash
        latest = event
    if reasons or latest is None:
        return reasons or ["adapter gate lineage 无有效事件"]
    try:
        active_head = _read_json_object(head_path, "adapter active gate head")
    except KronosRuntimeError as exc:
        return [str(exc)]
    if active_head != latest:
        reasons.append("adapter active gate head 不是最新 lineage event")
    if (
        latest.get("gate_sha256") != sha256_file(gate_path)
        or latest.get("sequence") != gate_payload.get("gate_sequence")
    ):
        reasons.append("adapter gate.json 不是 active lineage 当前授权")
    return reasons


def _validate_adapter_gate(
    *,
    gate_path: Path,
    gate_payload: dict[str, Any] | None,
    gate_parse_error: str | None,
    manifest: dict[str, Any],
    extra_state: dict[str, Any],
    observed_adapter_hash: str,
) -> dict[str, Any]:
    """Fail closed unless gate.json is bound to the exact loaded checkpoint."""

    state_hash = manifest.get("files", {}).get("state.pt", {}).get("sha256")
    if gate_parse_error is not None:
        return {
            "gate_status": "blocked",
            "release_output_type": "N/A",
            "gate_path": str(gate_path),
            "gate_sha256": sha256_file(gate_path) if gate_path.is_file() else None,
            "gate_reasons": [gate_parse_error],
        }
    if gate_payload is None:
        return {
            "gate_status": "unverified",
            "release_output_type": "N/A",
            "gate_path": str(gate_path),
            "gate_sha256": None,
            "gate_reasons": ["adapter store 缺少 gate.json，仅允许研究性 model_output"],
        }

    reasons: list[str] = []
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
        "verification_status",
        "output_type",
        "research_scoring_allowed",
        "forward_observation",
        "reasons",
        "metrics",
    }
    missing = sorted(required - set(gate_payload))
    if missing:
        reasons.append(f"gate.json 缺少字段：{missing}")
    if gate_payload.get("schema_version") != ADAPTER_GATE_SCHEMA_VERSION:
        reasons.append("gate.json schema_version 不匹配")
    gate_sequence = gate_payload.get("gate_sequence")
    if isinstance(gate_sequence, bool) or not isinstance(gate_sequence, int) or gate_sequence < 1:
        reasons.append("gate.json gate_sequence 无效")
    if gate_payload.get("gate_status") != "passed":
        reasons.append(f"gate_status={gate_payload.get('gate_status')!r}，未正式准出")
    elif manifest.get("stage") != "scorer":
        reasons.append("正式准出 gate 必须指向 scorer checkpoint")
    if gate_payload.get("evaluated_checkpoint") != manifest.get("checkpoint_name"):
        reasons.append("gate.json evaluated_checkpoint 与已加载 checkpoint 不一致")
    if gate_payload.get("adapter_hash") != observed_adapter_hash:
        reasons.append("gate.json adapter_hash 与实际 LoRA adapter checkpoint 不一致")
    if manifest.get("stage") == "scorer":
        if gate_payload.get("scorer_checkpoint_hash") != state_hash:
            reasons.append(
                "gate.json scorer_checkpoint_hash 与 scorer state.pt SHA256 不一致"
            )
    elif gate_payload.get("scorer_checkpoint_hash") not in (None, state_hash):
        reasons.append("adapter 阶段 gate 的 scorer_checkpoint_hash 无效")

    manifest_binding = manifest.get("binding")
    gate_binding = gate_payload.get("binding")
    expected_gate_binding = None
    if isinstance(manifest_binding, dict):
        expected_gate_binding = {
            "base_model_sha256": manifest_binding.get("base_model_sha256"),
            "tokenizer_sha256": manifest_binding.get("tokenizer_sha256"),
            "data_sha256": manifest_binding.get("dataset_sha256"),
            "config_sha256": manifest_binding.get("config_sha256"),
        }
    if gate_binding != expected_gate_binding:
        reasons.append("gate.json binding 与 checkpoint manifest 不一致")

    checkpoint_run_id = extra_state.get("run_id")
    if not isinstance(checkpoint_run_id, str) or not checkpoint_run_id:
        reasons.append("checkpoint extra_state 缺少 run_id，无法绑定准出评估")
    elif gate_payload.get("run_id") != checkpoint_run_id:
        reasons.append("gate.json run_id 与 checkpoint extra_state 不一致")

    generated_at = gate_payload.get("generated_at")
    if not isinstance(generated_at, str):
        reasons.append("gate.json generated_at 无效")
    else:
        try:
            parsed_generated_at = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
            if parsed_generated_at.tzinfo is None:
                reasons.append("gate.json generated_at 必须包含时区")
        except ValueError:
            reasons.append("gate.json generated_at 无法解析")

    declared_reasons = gate_payload.get("reasons")
    if isinstance(declared_reasons, list) and gate_payload.get("gate_status") != "passed":
        reasons.extend(str(item) for item in declared_reasons)
    if gate_payload.get("gate_status") == "passed":
        if gate_payload.get("verification_status") != "verified":
            reasons.append("passed gate verification_status 必须为 verified")
        if gate_payload.get("output_type") != "model_output":
            reasons.append("passed gate output_type 必须为 model_output")
        if gate_payload.get("research_scoring_allowed") is not False:
            reasons.append("passed gate 不得是 research_scoring_allowed")
        if declared_reasons != []:
            reasons.append("passed gate reasons 必须为空")
        forward = gate_payload.get("forward_observation")
        if not isinstance(forward, dict):
            reasons.append("passed gate 缺少 forward_observation")
        else:
            try:
                observation_days = int(forward.get("observation_days", -1))
                minimum_days = int(forward.get("minimum_days", -1))
                recommended_days = int(forward.get("recommended_days", -1))
            except (TypeError, ValueError):
                reasons.append("passed gate forward_observation 数值无效")
            else:
                if (
                    minimum_days < 60
                    or recommended_days < 120
                    or observation_days < minimum_days
                    or forward.get("minimum_met") is not True
                ):
                    reasons.append("passed gate 未满足60/120日前瞻观察合同")
                cached_commitments = forward.get("batch_commitments")
                cached_root = forward.get("registry_root_sha256")
                if not isinstance(cached_commitments, list) or not isinstance(
                    cached_root, str
                ):
                    reasons.append("passed gate 缺少 forward registry commitment")
                elif gate_path.parent.name != "checkpoints" or gate_path.parent.parent.parent.name != "runs":
                    reasons.append("adapter gate 路径无法定位受控 training root")
                else:
                    training_root = gate_path.parent.parents[2]
                    try:
                        scripts_dir = Path(__file__).resolve().parent
                        if str(scripts_dir) not in sys.path:
                            sys.path.insert(0, str(scripts_dir))
                        from kronos_a_share_forward import inspect_forward_registry

                        live_forward = inspect_forward_registry(
                            training_root
                            / "registry"
                            / "forward-observations"
                            / str(gate_payload.get("scorer_checkpoint_hash")),
                            training_root,
                            minimum_days=minimum_days,
                            recommended_days=recommended_days,
                            expected_adapter_hash=str(gate_payload.get("adapter_hash")),
                            expected_scorer_checkpoint_hash=str(
                                gate_payload.get("scorer_checkpoint_hash")
                            ),
                            expected_gate_binding=gate_payload.get("binding"),
                        )
                    except (OSError, RuntimeError, TypeError, ValueError) as exc:
                        reasons.append(f"passed gate 当前 forward registry 无法验证：{exc}")
                    else:
                        if (
                            live_forward.get("minimum_met") is not True
                            or live_forward.get("batch_commitments")
                            != cached_commitments
                            or live_forward.get("registry_root_sha256") != cached_root
                        ):
                            reasons.append("passed gate 与当前 forward registry 不一致")
        metrics = gate_payload.get("metrics")
        metric_names = {
            "adapter_ce_improvement",
            "validation_rank_ic",
            "zero_shot_rank_ic",
            "head_only_rank_ic",
            "positive_quarter_fraction",
            "bootstrap_ci95_lower",
            "base_after_cost_return",
            "stress_after_cost_return",
        }
        if not isinstance(metrics, dict) or not metric_names.issubset(metrics):
            reasons.append("passed gate 缺少完整历史准出 metrics")
        else:
            try:
                values = {name: float(metrics[name]) for name in metric_names}
            except (TypeError, ValueError, KeyError):
                reasons.append("passed gate metrics 数值无效")
            else:
                if not all(math.isfinite(value) for value in values.values()):
                    reasons.append("passed gate metrics 包含 NaN/Inf")
                if values["adapter_ce_improvement"] < 0.01:
                    reasons.append("passed gate adapter CE 未达1%")
                if values["validation_rank_ic"] < 0.03:
                    reasons.append("passed gate RankIC 未达0.03")
                if (
                    values["validation_rank_ic"] - values["zero_shot_rank_ic"]
                    < 0.005
                    or values["validation_rank_ic"] - values["head_only_rank_ic"]
                    < 0.005
                ):
                    reasons.append("passed gate 未领先 zero-shot/head-only 0.005")
                if values["positive_quarter_fraction"] <= 0.5:
                    reasons.append("passed gate 正RankIC季度未过半")
                if values["bootstrap_ci95_lower"] <= 0:
                    reasons.append("passed gate bootstrap 95%下界未大于0")
                if values["base_after_cost_return"] <= 0:
                    reasons.append("passed gate 35bp成本后收益未为正")
                if values["stress_after_cost_return"] < 0:
                    reasons.append("passed gate 70bp压力成本后收益为负")

        gate_hash = sha256_file(gate_path)
        receipt_path = gate_path.parent / "gate-receipts" / f"{gate_hash}.json"
        expected_receipt = {
            "schema_version": ADAPTER_GATE_RECEIPT_SCHEMA_VERSION,
            "gate_sha256": gate_hash,
            "gate_bytes": gate_path.stat().st_size,
            "gate_schema_version": gate_payload.get("schema_version"),
            "gate_status": gate_payload.get("gate_status"),
            "run_id": gate_payload.get("run_id"),
            "binding": gate_payload.get("binding"),
            "adapter_hash": gate_payload.get("adapter_hash"),
            "scorer_checkpoint_hash": gate_payload.get("scorer_checkpoint_hash"),
            "evaluated_checkpoint": gate_payload.get("evaluated_checkpoint"),
            "gate_generated_at": gate_payload.get("generated_at"),
            "gate_sequence": gate_payload.get("gate_sequence"),
        }
        if not receipt_path.is_file():
            reasons.append("passed gate 缺少匹配的不可变 release receipt")
        else:
            try:
                observed_receipt = _read_json_object(
                    receipt_path, "adapter gate receipt"
                )
            except KronosRuntimeError as exc:
                reasons.append(str(exc))
            else:
                if observed_receipt != expected_receipt:
                    reasons.append("adapter gate receipt 与 gate.json 哈希或绑定不一致")
        reasons.extend(_adapter_gate_lineage_reasons(gate_path, gate_payload))
    passed = not reasons
    return {
        "gate_status": "passed" if passed else "blocked",
        "release_output_type": "model_output" if passed else "N/A",
        "gate_path": str(gate_path),
        "gate_sha256": sha256_file(gate_path),
        "gate_reasons": reasons,
        "run_id": gate_payload.get("run_id"),
        "generated_at": generated_at,
    }


def load_adapter_into_model(model: Any, adapter_dir: Path) -> dict[str, Any]:
    """Load a hash-bound LoRA checkpoint and independently validate its gate."""

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from kronos_a_share_model import KronosScoringHead, set_lora_trainable
    from kronos_a_share_training import CheckpointBinding, CheckpointStore

    (
        root,
        reference,
        checkpoint_path,
        gate_path,
        gate_payload,
        gate_parse_error,
    ) = _select_adapter_checkpoint(adapter_dir)
    manifest_preview = _read_json_object(checkpoint_path / "manifest.json", "checkpoint manifest")
    try:
        binding = CheckpointBinding.from_mapping(manifest_preview.get("binding", {}))
    except (TypeError, ValueError) as exc:
        raise KronosRuntimeError(f"checkpoint binding 无效：{exc}") from exc
    if binding.base_model_sha256 != MODEL_SHA256:
        raise KronosRuntimeError(
            "checkpoint 绑定的 Kronos-base 与当前固定权重不一致"
        )
    if binding.tokenizer_sha256 != TOKENIZER_SHA256:
        raise KronosRuntimeError(
            "checkpoint 绑定的 Tokenizer 与当前固定权重不一致"
        )

    stage = manifest_preview.get("stage")
    scoring_head = KronosScoringHead() if stage == "scorer" else None
    store = CheckpointStore(root, binding)
    try:
        loaded = store.load(
            reference,
            model=model,
            scoring_head=scoring_head,
            restore_rng=False,
            map_location="cpu",
        )
    except (RuntimeError, OSError, TypeError, ValueError) as exc:
        raise KronosRuntimeError(f"adapter checkpoint 校验或加载失败：{exc}") from exc
    set_lora_trainable(model, False)
    model.eval()

    state_metadata = loaded.manifest["files"]["state.pt"]
    if loaded.stage == "scorer":
        adapter_reference = loaded.extra_state.get("adapter_checkpoint")
        if not isinstance(adapter_reference, str) or not adapter_reference:
            raise KronosRuntimeError("scorer checkpoint 缺少 adapter_checkpoint 绑定")
        try:
            adapter_manifest = store.inspect(adapter_reference)
        except (RuntimeError, OSError, TypeError, ValueError) as exc:
            raise KronosRuntimeError(f"scorer 绑定的 adapter checkpoint 无效：{exc}") from exc
        if adapter_manifest.get("stage") != "adapter":
            raise KronosRuntimeError("scorer 绑定的 checkpoint 不是 adapter 阶段")
        observed_adapter_hash = adapter_manifest["files"]["state.pt"]["sha256"]
        declared_adapter_hash = loaded.extra_state.get("adapter_hash")
        if declared_adapter_hash is not None and declared_adapter_hash != observed_adapter_hash:
            raise KronosRuntimeError("scorer extra_state.adapter_hash 与 adapter 工件不一致")
    else:
        observed_adapter_hash = state_metadata["sha256"]

    gate_report = _validate_adapter_gate(
        gate_path=gate_path,
        gate_payload=gate_payload,
        gate_parse_error=gate_parse_error,
        manifest=loaded.manifest,
        extra_state=loaded.extra_state,
        observed_adapter_hash=observed_adapter_hash,
    )
    return {
        "checkpoint_path": str(loaded.path),
        "checkpoint_name": loaded.manifest["checkpoint_name"],
        "stage": loaded.stage,
        "step": loaded.step,
        "adapter_hash": observed_adapter_hash,
        "checkpoint_hash": state_metadata["sha256"],
        "binding": loaded.manifest["binding"],
        **gate_report,
    }


def load_predictor_with_adapter(
    runtime_root: Path,
    device: str,
    adapter_dir: Path,
    *,
    allow_unreleased: bool = False,
):
    paths = runtime_paths(runtime_root)
    os.environ["HF_HUB_OFFLINE"] = "1"
    sys.path.insert(0, str(paths["source"]))
    from model import Kronos, KronosPredictor, KronosTokenizer

    tokenizer = KronosTokenizer.from_pretrained(paths["tokenizer"])
    model = Kronos.from_pretrained(paths["model"])
    adapter_report = load_adapter_into_model(model, adapter_dir)
    tokenizer.eval()
    model.eval()
    if adapter_report["gate_status"] != "passed" and not allow_unreleased:
        return None, adapter_report
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=MAX_CONTEXT)
    return predictor, adapter_report


def validate_arguments(args: argparse.Namespace) -> None:
    if args.load_model and not args.check:
        raise KronosRuntimeError("--load-model 只能与 --check 联用")
    if args.check and args.adapter_dir is not None and not args.load_model:
        raise KronosRuntimeError("--check 使用 --adapter-dir 时必须同时传入 --load-model")
    allow_research_output = bool(getattr(args, "allow_research_output", False))
    if allow_research_output and args.adapter_dir is None:
        raise KronosRuntimeError("--allow-research-output 只能与 --adapter-dir 联用")
    if allow_research_output and args.check:
        raise KronosRuntimeError("--allow-research-output 只适用于显式预测，不适用于 --check")
    if not 2 <= args.lookback <= MAX_CONTEXT:
        raise KronosRuntimeError(f"lookback 必须位于 2..{MAX_CONTEXT}")
    if args.pred_len is not None and not 1 <= args.pred_len <= MAX_CONTEXT:
        raise KronosRuntimeError(f"pred_len 必须位于 1..{MAX_CONTEXT}")
    if args.temperature <= 0:
        raise KronosRuntimeError("temperature 必须大于 0")
    if args.top_k < 0:
        raise KronosRuntimeError("top_k 不得为负数")
    if not 0 < args.top_p <= 1:
        raise KronosRuntimeError("top_p 必须位于 (0, 1]")
    if not 1 <= args.sample_count <= 100:
        raise KronosRuntimeError("sample_count 必须位于 1..100")


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def validate_output_paths(
    input_path: Path,
    future_path: Path | None,
    output_path: Path,
    metadata_path: Path,
    runtime_root: Path,
) -> None:
    if output_path.suffix.lower() != ".csv":
        raise KronosRuntimeError("output 必须使用 .csv 扩展名")
    protected = {input_path}
    if future_path is not None:
        protected.add(future_path)
    for candidate in (output_path, metadata_path):
        if candidate in protected:
            raise KronosRuntimeError("输出或 metadata 不得覆盖历史/未来时间戳输入")
        if is_within(candidate, runtime_root):
            raise KronosRuntimeError("输出不得写入 Kronos 源码、配置或权重运行目录")


def write_payload(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


class OutputPathLock:
    """Cross-process lock whose OS lock is released automatically after a crash."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle: Any | None = None

    def __enter__(self) -> "OutputPathLock":
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
            raise KronosRuntimeError(f"同一路径已有 Kronos 写出任务：{self.path}") from exc
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


def output_transaction_paths(
    output_path: Path,
    metadata_path: Path,
) -> dict[str, Path]:
    identity = os.path.normcase(
        f"{output_path.resolve()}\0{metadata_path.resolve()}"
    ).encode("utf-8")
    key = sha256_bytes(identity)
    tag = key[:16]
    prefix = f".{output_path.name}.kronos-{tag}"
    return {
        "lock": output_path.parent / ".kronos-locks" / f"{key}.lock",
        "pending_output": output_path.parent / f"{prefix}.output.pending",
        "pending_metadata": output_path.parent / f"{prefix}.metadata.pending",
        "backup_output": output_path.parent / f"{prefix}.output.bak",
        "backup_metadata": output_path.parent / f"{prefix}.metadata.bak",
        "commit_pending": output_path.parent / f"{prefix}.commit.pending",
        "commit": output_path.parent / f"{prefix}.commit",
    }


def points_to_same_file(path: Path, reference: Path) -> bool:
    try:
        return path.exists() and reference.exists() and os.path.samefile(path, reference)
    except OSError:
        return False


def unlink_if_owned(path: Path, reference: Path) -> None:
    if points_to_same_file(path, reference):
        path.unlink()


def restore_backup(backup: Path, destination: Path) -> None:
    if not backup.exists():
        return
    if destination.exists():
        if points_to_same_file(destination, backup):
            backup.unlink()
            return
        raise KronosRuntimeError(
            f"检测到中断事务，但恢复目标已被其他文件占用：{destination}；"
            f"原文件保留在 {backup}"
        )
    try:
        os.link(backup, destination)
    except FileExistsError as exc:
        raise KronosRuntimeError(
            f"检测到中断事务，但恢复目标在恢复期间被占用：{destination}；"
            f"原文件保留在 {backup}"
        ) from exc
    fsync_directory(destination.parent)
    backup.unlink()


def fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def read_commit_marker(commit: Path, expected_key: str) -> dict[str, Any]:
    try:
        marker = json.loads(commit.read_text(encoding="ascii"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise KronosRuntimeError(
            f"recovery_required: 事务标记不可解析，已保留现场：{commit}"
        ) from exc
    required = {
        "protocol": "kronos-output-pair-v1",
        "transaction_key": expected_key,
    }
    if any(marker.get(key) != value for key, value in required.items()):
        raise KronosRuntimeError(
            f"recovery_required: 事务标记身份不匹配，已保留现场：{commit}"
        )
    for key in ("output_sha256", "metadata_sha256", "output_size", "metadata_size"):
        if key not in marker:
            raise KronosRuntimeError(
                f"recovery_required: 事务标记缺少 {key}，已保留现场：{commit}"
            )
    return marker


def validate_committed_pair(
    output_path: Path,
    metadata_path: Path,
    marker: dict[str, Any],
) -> None:
    checks = [
        (output_path, marker["output_size"], marker["output_sha256"], "预测 CSV"),
        (metadata_path, marker["metadata_size"], marker["metadata_sha256"], "metadata"),
    ]
    for path, expected_size, expected_hash, label in checks:
        if not path.is_file():
            raise KronosRuntimeError(
                f"recovery_required: 已提交事务缺少{label}，已保留现场：{path}"
            )
        if path.stat().st_size != expected_size or sha256_file(path) != expected_hash:
            raise KronosRuntimeError(
                f"recovery_required: 已提交事务的{label}与事务标记不一致，已保留现场：{path}"
            )


def recover_output_transaction(
    output_path: Path,
    metadata_path: Path,
    paths: dict[str, Path],
) -> None:
    pending_output = paths["pending_output"]
    pending_metadata = paths["pending_metadata"]
    commit = paths["commit"]

    if commit.exists():
        marker = read_commit_marker(commit, paths["lock"].stem)
        validate_committed_pair(output_path, metadata_path, marker)
        for key in (
            "backup_output",
            "backup_metadata",
            "pending_output",
            "pending_metadata",
            "commit_pending",
        ):
            paths[key].unlink(missing_ok=True)
        fsync_directory(output_path.parent)
        commit.unlink(missing_ok=True)
        fsync_directory(output_path.parent)
        return

    unlink_if_owned(output_path, pending_output)
    unlink_if_owned(metadata_path, pending_metadata)
    restore_backup(paths["backup_output"], output_path)
    restore_backup(paths["backup_metadata"], metadata_path)
    pending_output.unlink(missing_ok=True)
    pending_metadata.unlink(missing_ok=True)
    paths["commit_pending"].unlink(missing_ok=True)
    commit.unlink(missing_ok=True)
    fsync_directory(output_path.parent)


def prepare_output_pair(
    output_path: Path,
    metadata_path: Path,
    force: bool,
) -> None:
    paths = output_transaction_paths(output_path, metadata_path)
    with OutputPathLock(paths["lock"]):
        recover_output_transaction(output_path, metadata_path, paths)
        if not force and (output_path.exists() or metadata_path.exists()):
            raise KronosRuntimeError("输出已存在；确认需要覆盖时显式传入 --force")


def backup_existing(path: Path, backup: Path) -> None:
    if not path.exists():
        return
    os.link(path, backup)
    if not points_to_same_file(path, backup):
        raise KronosRuntimeError(f"备份输出时路径发生并发变化：{path}")
    fsync_directory(path.parent)
    path.unlink()


def write_output_pair(
    output_path: Path,
    metadata_path: Path,
    output_payload: bytes,
    metadata_payload: bytes,
    force: bool,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    paths = output_transaction_paths(output_path, metadata_path)

    with OutputPathLock(paths["lock"]):
        recover_output_transaction(output_path, metadata_path, paths)
        if not force and (output_path.exists() or metadata_path.exists()):
            raise KronosRuntimeError("推理期间输出路径已被占用；未覆盖任何文件")

        write_payload(paths["pending_output"], output_payload)
        write_payload(paths["pending_metadata"], metadata_payload)
        fsync_directory(output_path.parent)
        try:
            if force:
                backup_existing(output_path, paths["backup_output"])
                backup_existing(metadata_path, paths["backup_metadata"])
            os.link(paths["pending_output"], output_path)
            os.link(paths["pending_metadata"], metadata_path)
            fsync_directory(output_path.parent)
            commit_payload = json.dumps(
                {
                    "protocol": "kronos-output-pair-v1",
                    "transaction_key": paths["lock"].stem,
                    "output_sha256": sha256_bytes(output_payload),
                    "output_size": len(output_payload),
                    "metadata_sha256": sha256_bytes(metadata_payload),
                    "metadata_size": len(metadata_payload),
                    "had_output": paths["backup_output"].exists(),
                    "had_metadata": paths["backup_metadata"].exists(),
                },
                sort_keys=True,
            ).encode("ascii")
            write_payload(paths["commit_pending"], commit_payload)
            os.replace(paths["commit_pending"], paths["commit"])
            fsync_directory(output_path.parent)
            paths["backup_output"].unlink(missing_ok=True)
            paths["backup_metadata"].unlink(missing_ok=True)
            paths["pending_output"].unlink(missing_ok=True)
            paths["pending_metadata"].unlink(missing_ok=True)
            fsync_directory(output_path.parent)
            paths["commit"].unlink()
            fsync_directory(output_path.parent)
        except (OSError, KronosRuntimeError) as exc:
            try:
                recover_output_transaction(output_path, metadata_path, paths)
            except KronosRuntimeError as recovery_exc:
                raise KronosRuntimeError(
                    f"写出失败且自动恢复未完成：{recovery_exc}"
                ) from exc
            if isinstance(exc, FileExistsError):
                raise KronosRuntimeError("推理期间输出路径已被占用；未覆盖其他文件") from exc
            raise


def run_check(args: argparse.Namespace) -> int:
    runtime_report = validate_runtime(args.runtime_root)
    device, warnings, cuda_report = resolve_device(args.device)
    report: dict[str, Any] = {
        "status": "ok",
        "evidence_class": "model_output_runtime_check",
        **runtime_report,
        "python": sys.version,
        "device": device,
        "cuda": cuda_report,
        "warnings": warnings,
    }
    if args.load_model:
        if args.adapter_dir is None:
            load_predictor(args.runtime_root, device)
        else:
            _, adapter_report = load_predictor_with_adapter(
                args.runtime_root, device, args.adapter_dir
            )
            report["adapter"] = adapter_report
            if adapter_report["gate_status"] != "passed":
                warnings.append(
                    f"adapter gate_status={adapter_report['gate_status']}；"
                    "本地加载成功不代表正式准出，准出输出为 N/A。"
                )
        report["model_load"] = "ok"
    print("Kronos 本地安装检查通过。")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def run_forecast(args: argparse.Namespace) -> int:
    if args.pred_len is None or args.output is None:
        raise KronosRuntimeError("预测时必须提供 --pred-len 与 --output")
    validate_arguments(args)
    runtime_report = validate_runtime(args.runtime_root)
    input_path = args.input.resolve()
    future_path = args.future_timestamps.resolve() if args.future_timestamps else None
    output_path = args.output.resolve()
    metadata_path = output_path.with_suffix(output_path.suffix + ".metadata.json")
    validate_output_paths(
        input_path,
        future_path,
        output_path,
        metadata_path,
        args.runtime_root.resolve(),
    )
    output_prepared = args.adapter_dir is None
    if output_prepared:
        prepare_output_pair(output_path, metadata_path, args.force)
    history, x_timestamp, warnings, input_details = load_history(
        input_path, args.timestamp_column, args.lookback
    )
    y_timestamp, timestamp_source, future_hash, timestamp_warnings = load_future_timestamps(
        future_path,
        args.freq,
        args.timestamp_column,
        x_timestamp.iloc[-1],
        args.pred_len,
    )
    warnings.extend(timestamp_warnings)
    device, device_warnings, cuda_report = resolve_device(args.device)
    warnings.extend(device_warnings)

    set_seed(args.seed)
    adapter_report: dict[str, Any] | None = None
    research_only = False
    if args.adapter_dir is None:
        predictor = load_predictor(args.runtime_root, device)
    else:
        allow_research_output = bool(
            getattr(args, "allow_research_output", False)
        )
        predictor, adapter_report = load_predictor_with_adapter(
            args.runtime_root,
            device,
            args.adapter_dir,
            allow_unreleased=allow_research_output,
        )
        if adapter_report["gate_status"] == "passed":
            warnings.append(
                "adapter 已通过绑定的 gate.json 校验；准出仅适用于模型工件，不构成交易建议。"
            )
        else:
            research_only = True
            if not allow_research_output:
                payload = {
                    "status": "unverified",
                    "output_type": "N/A",
                    "evidence_class": "model_output",
                    "research_only": False,
                    "output_written": False,
                    "output_path": str(output_path),
                    "message": (
                        "adapter 未通过正式准出；默认禁止生成数值预测。"
                        "如确需研究输出，显式传入 --allow-research-output，"
                        "并使用 .research-only.csv 文件名。"
                    ),
                    "adapter": adapter_report,
                }
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 2
            if not output_path.name.lower().endswith(".research-only.csv"):
                raise KronosRuntimeError(
                    "未准出 adapter 的研究输出文件名必须以 .research-only.csv 结尾"
                )
            warnings.append(
                f"adapter gate_status={adapter_report['gate_status']}；"
                "本次路径为显式 research-only model_output，正式准出固定为 N/A。"
            )
    if predictor is None:
        raise KronosRuntimeError("adapter predictor 未通过准出且未启用研究输出")

    if not output_prepared:
        prepare_output_pair(output_path, metadata_path, args.force)
    import torch

    with torch.inference_mode():
        predicted = predictor.predict(
            df=history,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=args.pred_len,
            T=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            sample_count=args.sample_count,
            verbose=not args.quiet,
        )

    predicted_values = predicted[[*PRICE_COLUMNS, *OPTIONAL_COLUMNS]].to_numpy(dtype=np.float64)
    if not np.isfinite(predicted_values).all():
        raise KronosRuntimeError("模型输出包含 NaN 或 Inf；未写出文件")
    invalid_output = (
        (predicted["high"] < predicted[["open", "close"]].max(axis=1))
        | (predicted["low"] > predicted[["open", "close"]].min(axis=1))
        | (predicted["high"] < predicted["low"])
    )
    invalid_count = int(invalid_output.sum())
    nonpositive_price_count = int((predicted[PRICE_COLUMNS] <= 0).any(axis=1).sum())
    negative_activity_count = int((predicted[OPTIONAL_COLUMNS] < 0).any(axis=1).sum())
    if invalid_count:
        warnings.append(f"原始模型输出中有 {invalid_count} 根 K 线不满足标准 OHLC 结构；未自动修正。")
    if nonpositive_price_count:
        warnings.append(f"原始模型输出中有 {nonpositive_price_count} 根 K 线包含非正价格；未自动修正。")
    if negative_activity_count:
        warnings.append(
            f"原始模型输出中有 {negative_activity_count} 根 K 线包含负 volume/amount；未自动修正。"
        )

    output_frame = predicted.reset_index()
    output_frame = output_frame.rename(columns={output_frame.columns[0]: args.timestamp_column})
    output_payload = output_frame.to_csv(index=False, lineterminator="\n").encode("utf-8")

    metadata: dict[str, Any] = {
        "status": "ok",
        "evidence_class": "model_output",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **runtime_report,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "output_sha256": sha256_bytes(output_payload),
        **input_details,
        "timestamp_source": timestamp_source,
        "future_timestamps_sha256": future_hash,
        "pred_len": args.pred_len,
        "parameters": {
            "lookback": args.lookback,
            "temperature": args.temperature,
            "top_k": args.top_k,
            "top_p": args.top_p,
            "sample_count": args.sample_count,
            "seed": args.seed,
        },
        "device": device,
        "cuda": cuda_report,
        "invalid_output_ohlc_count": invalid_count,
        "nonpositive_output_price_count": nonpositive_price_count,
        "negative_output_volume_or_amount_count": negative_activity_count,
        "warnings": warnings,
        "disclaimer": "Kronos 条件生成结果，仅为 model_output，不是未来事实、上涨概率或独立交易信号。",
    }
    if adapter_report is not None:
        metadata["adapter"] = adapter_report
        metadata.update(
            {
                "status": "unverified" if research_only else "ok",
                "output_type": "N/A" if research_only else "model_output",
                "release_mode": (
                    "research-only" if research_only else "released-adapter"
                ),
                "research_only": research_only,
                "publishable": not research_only,
            }
        )
    metadata_payload = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_output_pair(output_path, metadata_path, output_payload, metadata_payload, args.force)

    if research_only:
        print("Kronos research-only 预测完成；正式准出固定为 N/A。")
    else:
        print("Kronos 预测完成；结果仅标记为 model_output。")
    print(f"预测 CSV：{output_path}")
    print(f"元数据：{metadata_path}")
    if warnings:
        print("警告：")
        for warning in warnings:
            print(f"- {warning}")
    return 2 if research_only else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="离线校验并运行项目本地 Kronos-base")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="校验本地环境、revision 与权重哈希")
    action.add_argument("--input", type=Path, help="历史 K 线 CSV")
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--load-model", action="store_true", help="与 --check 联用，完整加载权重")
    parser.add_argument(
        "--adapter-dir",
        type=Path,
        help="A股 LoRA checkpoint store 根目录或具体 checkpoint 目录",
    )
    parser.add_argument(
        "--allow-research-output",
        action="store_true",
        help=(
            "显式允许未准出 adapter 生成 research-only 数值路径；"
            "输出名必须以 .research-only.csv 结尾，顶层仍为 N/A"
        ),
    )
    parser.add_argument("--output", type=Path, help="预测 CSV 输出路径")
    future_time = parser.add_mutually_exclusive_group()
    future_time.add_argument("--future-timestamps", type=Path, help="未来时间戳 CSV")
    future_time.add_argument("--freq", help="pandas 频率，例如 5min 或 B")
    parser.add_argument("--timestamp-column", default="timestamps")
    parser.add_argument("--lookback", type=int, default=400)
    parser.add_argument("--pred-len", type=int)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--sample-count", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--force", action="store_true", help="显式允许覆盖已有输出与 metadata")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        validate_arguments(args)
        if args.check:
            return run_check(args)
        return run_forecast(args)
    except (RuntimeError, OSError, TypeError, ValueError) as exc:
        print(f"Kronos 执行失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
