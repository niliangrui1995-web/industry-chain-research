"""Bounded ZIP extraction helpers for Office documents."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path, PurePosixPath

MAX_ZIP_MEMBERS = 10_000
MAX_ZIP_TOTAL_BYTES = 250 * 1024 * 1024
MAX_ZIP_MEMBER_BYTES = 100 * 1024 * 1024
MAX_ZIP_COMPRESSION_RATIO = 100


class UnsafeZipError(ValueError):
    """Raised when an Office ZIP exceeds local safety limits."""


def safe_extractall(zip_file: zipfile.ZipFile, output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    _validate_members(zip_file.infolist())
    zip_file.extractall(output_path)


def _validate_members(members: list[zipfile.ZipInfo]) -> None:
    if len(members) > MAX_ZIP_MEMBERS:
        raise UnsafeZipError(f"archive has too many entries: {len(members)}")

    total_size = 0
    for member in members:
        _validate_member_path(member.filename)
        if _is_symlink(member):
            raise UnsafeZipError(f"archive entry is a symlink: {member.filename}")
        if member.file_size > MAX_ZIP_MEMBER_BYTES:
            raise UnsafeZipError(f"archive entry is too large: {member.filename}")
        if member.compress_size and member.file_size / member.compress_size > MAX_ZIP_COMPRESSION_RATIO:
            raise UnsafeZipError(f"archive entry has suspicious compression ratio: {member.filename}")
        total_size += member.file_size
        if total_size > MAX_ZIP_TOTAL_BYTES:
            raise UnsafeZipError("archive uncompressed size exceeds limit")


def _validate_member_path(name: str) -> None:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or normalized.startswith("/")
        or os.path.isabs(normalized)
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise UnsafeZipError(f"archive entry has unsafe path: {name}")


def _is_symlink(member: zipfile.ZipInfo) -> bool:
    return ((member.external_attr >> 16) & 0o170000) == 0o120000
