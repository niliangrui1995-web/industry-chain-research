#!/usr/bin/env python3
"""Validate and run the project-local Kronos-base checkpoint offline."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
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


def validate_arguments(args: argparse.Namespace) -> None:
    if args.load_model and not args.check:
        raise KronosRuntimeError("--load-model 只能与 --check 联用")
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
        load_predictor(args.runtime_root, device)
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
    predictor = load_predictor(args.runtime_root, device)
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
    metadata_payload = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_output_pair(output_path, metadata_path, output_payload, metadata_payload, args.force)

    print("Kronos 预测完成；结果仅标记为 model_output。")
    print(f"预测 CSV：{output_path}")
    print(f"元数据：{metadata_path}")
    if warnings:
        print("警告：")
        for warning in warnings:
            print(f"- {warning}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="离线校验并运行项目本地 Kronos-base")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="校验本地环境、revision 与权重哈希")
    action.add_argument("--input", type=Path, help="历史 K 线 CSV")
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--load-model", action="store_true", help="与 --check 联用，完整加载权重")
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
