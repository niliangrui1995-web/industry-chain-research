#!/usr/bin/env python3
"""Shared, fail-closed runtime helpers for Kronos A-share training jobs."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, MutableMapping


DEFAULT_TRAINING_ROOT = Path(
    r"D:\vcp_hunter\产业链投研\_training\kronos_ashare"
)

LAYOUT_RELATIVE_PATHS: dict[str, Path] = {
    "runtime": Path("runtime"),
    "uv_cache": Path("runtime") / "uv-cache",
    "uv_python": Path("runtime") / "uv-python",
    "pip_cache": Path("runtime") / "pip-cache",
    "venvs": Path("runtime") / "venvs",
    "huggingface": Path("runtime") / "huggingface",
    "torch": Path("runtime") / "torch",
    "tmp": Path("runtime") / "tmp",
    "data": Path("data"),
    "runs": Path("runs"),
    "registry": Path("registry"),
}

IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}


class KronosAshareRuntimeError(RuntimeError):
    """Raised when the local A-share training runtime contract is invalid."""


@dataclass(frozen=True)
class TrainingLayout:
    root: Path
    runtime: Path
    uv_cache: Path
    uv_python: Path
    pip_cache: Path
    venvs: Path
    huggingface: Path
    torch: Path
    tmp: Path
    data: Path
    runs: Path
    registry: Path

    def to_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


def _resolved(path: str | os.PathLike[str], *, strict: bool = False) -> Path:
    try:
        return Path(path).expanduser().resolve(strict=strict)
    except (OSError, RuntimeError) as exc:
        raise KronosAshareRuntimeError(f"无法解析路径：{path}: {exc}") from exc


def is_within(candidate: str | os.PathLike[str], root: str | os.PathLike[str]) -> bool:
    """Return whether the resolved candidate is equal to or below root."""

    candidate_path = _resolved(candidate)
    root_path = _resolved(root)
    try:
        common = os.path.commonpath(
            [os.path.normcase(str(candidate_path)), os.path.normcase(str(root_path))]
        )
    except ValueError:
        return False
    return common == os.path.normcase(str(root_path))


def resolve_under(
    root: str | os.PathLike[str],
    candidate: str | os.PathLike[str],
    *,
    must_exist: bool = False,
    allow_root: bool = False,
) -> Path:
    """Resolve a child path and reject traversal, drive changes, and symlink escape."""

    root_path = _resolved(root)
    raw_candidate = Path(candidate)
    joined = raw_candidate if raw_candidate.is_absolute() else root_path / raw_candidate
    candidate_path = _resolved(joined, strict=must_exist)
    if not is_within(candidate_path, root_path):
        raise KronosAshareRuntimeError(
            f"path_outside_training_root: candidate={candidate_path}, root={root_path}"
        )
    if candidate_path == root_path and not allow_root:
        raise KronosAshareRuntimeError(
            "path_outside_training_root: 调用方必须指定训练根下的具体子路径"
        )
    return candidate_path


def resolve_training_root(
    root: str | os.PathLike[str] | None = None,
) -> Path:
    selected = DEFAULT_TRAINING_ROOT if root is None else Path(root)
    if not selected.is_absolute():
        raise KronosAshareRuntimeError("path_outside_training_root: 训练根必须是绝对路径")
    resolved = _resolved(selected)
    fixed_declared = Path(os.path.abspath(DEFAULT_TRAINING_ROOT))
    fixed_resolved = _resolved(DEFAULT_TRAINING_ROOT)
    if os.path.normcase(str(fixed_declared)) != os.path.normcase(str(fixed_resolved)):
        raise KronosAshareRuntimeError(
            "path_outside_training_root: 固定训练根的祖先目录不得是 symlink/junction"
        )
    if os.path.normcase(str(resolved)) != os.path.normcase(str(fixed_resolved)):
        raise KronosAshareRuntimeError(
            f"path_outside_training_root: root={resolved}, expected={fixed_resolved}"
        )
    return resolved


def get_training_layout(
    root: str | os.PathLike[str] | None = None,
    *,
    create: bool = False,
) -> TrainingLayout:
    root_path = resolve_training_root(root)
    values: dict[str, Path] = {"root": root_path}
    for name, relative in LAYOUT_RELATIVE_PATHS.items():
        values[name] = resolve_under(root_path, relative)
    layout = TrainingLayout(**values)
    if create:
        for path in layout.to_dict().values():
            Path(path).mkdir(parents=True, exist_ok=True)
    return layout


def validate_identifier(value: str, label: str = "identifier") -> str:
    """Validate path-safe, reproducible dataset and run identifiers."""

    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise KronosAshareRuntimeError(
            f"{label} 仅允许 1..64 位小写字母、数字、下划线和连字符，且首位必须是字母或数字"
        )
    if value.casefold() in WINDOWS_RESERVED_NAMES:
        raise KronosAshareRuntimeError(f"{label} 使用了 Windows 保留名称：{value}")
    return value


def dataset_directory(
    dataset_id: str,
    layout: TrainingLayout | None = None,
    *,
    create: bool = False,
) -> Path:
    selected = get_training_layout() if layout is None else layout
    resolve_training_root(selected.root)
    path = resolve_under(selected.data, validate_identifier(dataset_id, "dataset_id"))
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def run_directory(
    run_id: str,
    layout: TrainingLayout | None = None,
    *,
    create: bool = False,
) -> Path:
    selected = get_training_layout() if layout is None else layout
    resolve_training_root(selected.root)
    path = resolve_under(selected.runs, validate_identifier(run_id, "run_id"))
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def environment_mapping(layout: TrainingLayout | None = None) -> dict[str, str]:
    """Return the process environment contract without mutating os.environ."""

    selected = get_training_layout() if layout is None else layout
    resolve_training_root(selected.root)
    return {
        "KRONOS_A_SHARE_ROOT": str(selected.root),
        "KRONOS_A_SHARE_TRAINING_ROOT": str(selected.root),
        "KRONOS_VENV_ROOT": str(selected.venvs),
        "UV_CACHE_DIR": str(selected.uv_cache),
        "UV_PYTHON_INSTALL_DIR": str(selected.uv_python),
        "PIP_CACHE_DIR": str(selected.pip_cache),
        "HF_HOME": str(selected.huggingface),
        "TORCH_HOME": str(selected.torch),
        "QLIB_PROVIDER_URI": str(selected.data / "qlib"),
        "QLIB_DATA_PATH": str(selected.data / "qlib"),
        "TEMP": str(selected.tmp),
        "TMP": str(selected.tmp),
        "TMPDIR": str(selected.tmp),
    }


def subprocess_environment(
    layout: TrainingLayout | None = None,
    base: Mapping[str, str] | None = None,
) -> dict[str, str]:
    result = dict(os.environ if base is None else base)
    result.update(environment_mapping(layout))
    return result


def apply_environment_mapping(
    layout: TrainingLayout | None = None,
    environ: MutableMapping[str, str] | None = None,
) -> dict[str, str | None]:
    """Apply the contract to an explicit environment and return previous values."""

    target = os.environ if environ is None else environ
    mapping = environment_mapping(layout)
    previous = {key: target.get(key) for key in mapping}
    target.update(mapping)
    if target is os.environ:
        # ``tempfile`` caches its first resolved directory.  pandas/pyarrow can
        # import it before the CLI has built its workflow context, so changing
        # TEMP/TMP alone is insufficient and silently leaves later third-party
        # writes on C:.  Bind the module cache as part of the process contract.
        temporary_root = Path(mapping["TEMP"]).resolve(strict=False)
        temporary_root.mkdir(parents=True, exist_ok=True)
        tempfile.tempdir = str(temporary_root)
    return previous


def sha256_file(path: str | os.PathLike[str], chunk_size: int = 1024 * 1024) -> str:
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")
    file_path = _resolved(path, strict=True)
    if not file_path.is_file():
        raise KronosAshareRuntimeError(f"SHA256 目标不是普通文件：{file_path}")
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(
    path: str | os.PathLike[str],
    payload: Any,
    *,
    allowed_root: str | os.PathLike[str] | None = None,
) -> Path:
    """Durably replace a UTF-8 JSON file using a same-directory temporary file."""

    destination = _resolved(path)
    if allowed_root is not None:
        destination = resolve_under(allowed_root, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        if os.name != "nt":
            directory_fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return destination


def _nearest_existing_parent(path: Path) -> Path:
    current = path
    while not current.exists():
        if current.parent == current:
            raise KronosAshareRuntimeError(f"找不到可用于磁盘检查的父目录：{path}")
        current = current.parent
    return current


def memory_info() -> dict[str, int | str]:
    """Return total and available physical memory without requiring psutil."""

    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("memory_load", ctypes.c_ulong),
                ("total_physical", ctypes.c_ulonglong),
                ("available_physical", ctypes.c_ulonglong),
                ("total_page_file", ctypes.c_ulonglong),
                ("available_page_file", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong),
                ("available_virtual", ctypes.c_ulonglong),
                ("available_extended_virtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(MemoryStatus)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise KronosAshareRuntimeError("Windows GlobalMemoryStatusEx 调用失败")
        return {
            "source": "GlobalMemoryStatusEx",
            "total_bytes": int(status.total_physical),
            "available_bytes": int(status.available_physical),
        }

    page_size = os.sysconf("SC_PAGE_SIZE")
    total_pages = os.sysconf("SC_PHYS_PAGES")
    available_pages = os.sysconf("SC_AVPHYS_PAGES")
    return {
        "source": "sysconf",
        "total_bytes": int(page_size * total_pages),
        "available_bytes": int(page_size * available_pages),
    }


def cuda_info() -> dict[str, Any]:
    try:
        import torch
    except (ImportError, OSError) as exc:
        return {"available": False, "reason": f"torch_unavailable:{type(exc).__name__}"}

    report: dict[str, Any] = {
        "available": bool(torch.cuda.is_available()),
        "torch_version": torch.__version__,
        "cuda_build": torch.version.cuda,
        "devices": [],
    }
    if not report["available"]:
        return report
    for index in range(torch.cuda.device_count()):
        properties = torch.cuda.get_device_properties(index)
        report["devices"].append(
            {
                "index": index,
                "name": properties.name,
                "capability": list(torch.cuda.get_device_capability(index)),
                "total_memory_bytes": int(properties.total_memory),
            }
        )
    return report


def preflight_training(
    root: str | os.PathLike[str] | None = None,
    *,
    min_disk_free_gib: float = 20.0,
    min_ram_available_gib: float = 4.0,
    require_cuda: bool = True,
    min_cuda_vram_gib: float = 4.0,
) -> dict[str, Any]:
    """Check local resources without creating directories or changing environment."""

    thresholds = {
        "min_disk_free_gib": min_disk_free_gib,
        "min_ram_available_gib": min_ram_available_gib,
        "min_cuda_vram_gib": min_cuda_vram_gib,
    }
    if any(not isinstance(value, (int, float)) or value < 0 for value in thresholds.values()):
        raise ValueError("资源阈值必须是非负数")

    training_root = resolve_training_root(root)
    probe_path = _nearest_existing_parent(training_root)
    disk = shutil.disk_usage(probe_path)
    memory = memory_info()
    cuda = cuda_info()
    gib = 1024**3
    blockers: list[str] = []
    warnings: list[str] = []

    if disk.free < min_disk_free_gib * gib:
        blockers.append(
            f"disk_free_below_threshold:{disk.free / gib:.2f}<{min_disk_free_gib:.2f}GiB"
        )
    if int(memory["available_bytes"]) < min_ram_available_gib * gib:
        blockers.append(
            "ram_available_below_threshold:"
            f"{int(memory['available_bytes']) / gib:.2f}<{min_ram_available_gib:.2f}GiB"
        )

    devices = cuda.get("devices", [])
    if require_cuda and not cuda.get("available"):
        blockers.append("cuda_required_but_unavailable")
    elif cuda.get("available"):
        largest_vram = max(
            (int(device["total_memory_bytes"]) for device in devices), default=0
        )
        if largest_vram < min_cuda_vram_gib * gib:
            blockers.append(
                "cuda_vram_below_threshold:"
                f"{largest_vram / gib:.2f}<{min_cuda_vram_gib:.2f}GiB"
            )
    else:
        warnings.append("CUDA 不可用；仅允许调用方明确选择 CPU 诊断。")

    return {
        "status": "blocked" if blockers else "ok",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "training_root": str(training_root),
        "root_exists": training_root.exists(),
        "thresholds": {**thresholds, "require_cuda": require_cuda},
        "disk": {
            "probe_path": str(probe_path),
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
        },
        "memory": memory,
        "cuda": cuda,
        "blockers": blockers,
        "warnings": warnings,
    }


__all__ = [
    "DEFAULT_TRAINING_ROOT",
    "KronosAshareRuntimeError",
    "TrainingLayout",
    "apply_environment_mapping",
    "atomic_write_json",
    "cuda_info",
    "dataset_directory",
    "environment_mapping",
    "get_training_layout",
    "is_within",
    "memory_info",
    "preflight_training",
    "resolve_training_root",
    "resolve_under",
    "run_directory",
    "sha256_file",
    "subprocess_environment",
    "validate_identifier",
]
