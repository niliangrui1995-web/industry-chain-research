from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


SNAPSHOT_SCHEMA_VERSION = 1
BLOCKED_EXIT_CODE = 2


class GuardError(ValueError):
    """不能安全比较工作区基线时抛出。"""


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _print_payload(payload: dict[str, object]) -> None:
    print(_json_bytes(payload).decode("utf-8"), end="")


def _run_git(repo_root: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        error = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GuardError(f"git {' '.join(args)} 失败：{error or f'退出码 {completed.returncode}'}")
    return completed.stdout


def _resolve_repo_root(value: str) -> Path:
    requested = Path(value).expanduser().resolve()
    top_level = _run_git(requested, "rev-parse", "--show-toplevel")
    try:
        return Path(top_level.decode("utf-8", errors="surrogateescape").strip()).resolve()
    except UnicodeDecodeError as exc:
        raise GuardError("git 仓库根目录无法解码") from exc


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _normalise_relative_path(value: str) -> str:
    if not value or "\x00" in value:
        raise GuardError("git 状态包含空路径或 NUL 路径")
    if "\\" in value:
        raise GuardError(f"git 状态包含无法安全处理的反斜杠路径：{value!r}")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if posix.is_absolute() or posix.root or windows.is_absolute() or windows.root or windows.drive:
        raise GuardError(f"git 状态包含绝对路径：{value!r}")
    if any(part in {"", ".", ".."} for part in posix.parts):
        raise GuardError(f"git 状态包含越界路径：{value!r}")
    return posix.as_posix()


def _decode_relative_path(value: bytes) -> str:
    try:
        decoded = value.decode("utf-8", errors="surrogateescape")
    except UnicodeDecodeError as exc:
        raise GuardError("git 状态路径无法解码") from exc
    return _normalise_relative_path(decoded)


def _is_supported_status(status: str) -> bool:
    if status == "??":
        return True
    if len(status) != 2 or status == "  ":
        return False
    if "U" in status or "!" in status or "?" in status:
        return False
    return all(character in {" ", "M", "T", "A", "D", "R", "C"} for character in status)


def _parse_porcelain_v1_z(payload: bytes) -> list[dict[str, object]]:
    if not payload:
        return []
    if not payload.endswith(b"\0"):
        raise GuardError("git status --porcelain=v1 -z 输出缺少结尾 NUL")
    fields = payload.split(b"\0")
    entries: list[dict[str, object]] = []
    index = 0
    while index < len(fields) - 1:
        field = fields[index]
        if len(field) < 4 or field[2:3] != b" ":
            raise GuardError("git status --porcelain=v1 -z 状态无法解析")
        try:
            status = field[:2].decode("ascii")
        except UnicodeDecodeError as exc:
            raise GuardError("git status 状态不是 ASCII") from exc
        if not _is_supported_status(status):
            raise GuardError(f"git status 包含无法安全处理的状态：{status!r}")
        path = _decode_relative_path(field[3:])
        original_path: str | None = None
        if "R" in status or "C" in status:
            if index + 1 >= len(fields) - 1:
                raise GuardError("git status 重命名或复制记录缺少原路径")
            original_path = _decode_relative_path(fields[index + 1])
            index += 1
        entries.append({"path": path, "original_path": original_path, "status": status})
        index += 1
    identities = {(str(entry["path"]), entry["original_path"]) for entry in entries}
    if len(identities) != len(entries):
        raise GuardError("git status 包含重复路径记录")
    return entries


def _fingerprint_path(repo_root: Path, relative_path: str) -> dict[str, str | None]:
    path = repo_root.joinpath(*PurePosixPath(relative_path).parts)
    try:
        before = path.lstat()
    except FileNotFoundError:
        return {"state": "missing", "sha256": None}
    if stat.S_ISLNK(before.st_mode):
        target = os.readlink(path)
        return {
            "state": "symlink",
            "sha256": hashlib.sha256(os.fsencode(target)).hexdigest(),
        }
    if not stat.S_ISREG(before.st_mode):
        raise GuardError(f"无法安全哈希非普通文件：{relative_path!r}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    try:
        after = path.lstat()
    except FileNotFoundError as exc:
        raise GuardError(f"哈希期间文件消失：{relative_path!r}") from exc
    before_state = (before.st_mode, before.st_size, before.st_mtime_ns)
    after_state = (after.st_mode, after.st_size, after.st_mtime_ns)
    if before_state != after_state:
        raise GuardError(f"哈希期间文件发生变化：{relative_path!r}")
    return {"state": "present", "sha256": digest.hexdigest()}


def _status_entries(repo_root: Path) -> list[dict[str, object]]:
    raw_status = _run_git(repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    entries = _parse_porcelain_v1_z(raw_status)
    for entry in entries:
        path = str(entry["path"])
        entry["fingerprint"] = _fingerprint_path(repo_root, path)
        original_path = entry["original_path"]
        entry["original_fingerprint"] = (
            _fingerprint_path(repo_root, str(original_path)) if original_path is not None else None
        )
    return sorted(entries, key=lambda item: (str(item["path"]), str(item["original_path"] or "")))


def _entry_identity(entry: dict[str, object]) -> tuple[str, str | None]:
    original_path = entry.get("original_path")
    return str(entry["path"]), str(original_path) if original_path is not None else None


def _entry_paths(entry: dict[str, object]) -> set[str]:
    paths = {str(entry["path"])}
    original_path = entry.get("original_path")
    if original_path is not None:
        paths.add(str(original_path))
    return paths


def _entry_matches(left: dict[str, object], right: dict[str, object]) -> bool:
    return (
        left.get("status") == right.get("status")
        and left.get("fingerprint") == right.get("fingerprint")
        and left.get("original_fingerprint") == right.get("original_fingerprint")
    )


def _validate_snapshot_entry(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise GuardError("快照 entries 包含非对象")
    path = value.get("path")
    status = value.get("status")
    original_path = value.get("original_path")
    fingerprint = value.get("fingerprint")
    original_fingerprint = value.get("original_fingerprint")
    if not isinstance(path, str) or not isinstance(status, str):
        raise GuardError("快照 entry 缺少 path 或 status")
    normalised_path = _normalise_relative_path(path)
    if not _is_supported_status(status):
        raise GuardError("快照 entry 包含无法安全处理的状态")
    if original_path is not None:
        if not isinstance(original_path, str):
            raise GuardError("快照 entry original_path 类型错误")
        original_path = _normalise_relative_path(original_path)
    if ("R" in status or "C" in status) != (original_path is not None):
        raise GuardError("快照 entry 重命名或复制路径不完整")
    normalised_fingerprint = _validate_fingerprint(fingerprint, "fingerprint")
    if original_path is None:
        if original_fingerprint is not None:
            raise GuardError("快照 entry 不应包含 original_fingerprint")
    else:
        original_fingerprint = _validate_fingerprint(original_fingerprint, "original_fingerprint")
    return {
        "path": normalised_path,
        "original_path": original_path,
        "status": status,
        "fingerprint": normalised_fingerprint,
        "original_fingerprint": original_fingerprint,
    }


def _validate_fingerprint(value: object, name: str) -> dict[str, str | None]:
    if not isinstance(value, dict):
        raise GuardError(f"快照 entry {name} 类型错误")
    state = value.get("state")
    sha256 = value.get("sha256")
    if state not in {"present", "missing", "symlink"}:
        raise GuardError(f"快照 entry {name} state 无法安全处理")
    if state == "missing":
        if sha256 is not None:
            raise GuardError(f"快照 entry {name} missing 状态不应有 SHA-256")
    elif not isinstance(sha256, str) or len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
        raise GuardError(f"快照 entry {name} SHA-256 无法安全处理")
    return {"state": state, "sha256": sha256}


def _snapshot_path(value: str, repo_root: Path) -> Path:
    path = Path(value).expanduser().resolve()
    if _is_relative_to(path, repo_root):
        raise GuardError("snapshot 必须位于仓库外，避免其自身污染工作区")
    return path


def _write_snapshot(snapshot_path: Path, payload: dict[str, object]) -> None:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=snapshot_path.parent, suffix=".tmp") as handle:
        temporary = Path(handle.name)
        handle.write(_json_bytes(payload))
    try:
        os.replace(temporary, snapshot_path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _load_snapshot(snapshot_path: Path, repo_root: Path) -> list[dict[str, object]]:
    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GuardError(f"无法读取工作区快照：{exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
        raise GuardError("工作区快照 schema_version 不匹配")
    if data.get("repo_root") != str(repo_root):
        raise GuardError("工作区快照不属于当前仓库")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise GuardError("工作区快照缺少 entries")
    normalised = [_validate_snapshot_entry(entry) for entry in entries]
    identities = {_entry_identity(entry) for entry in normalised}
    if len(identities) != len(normalised):
        raise GuardError("工作区快照包含重复路径记录")
    return normalised


def snapshot(repo_root: Path, snapshot_path: Path) -> dict[str, object]:
    entries = _status_entries(repo_root)
    payload: dict[str, object] = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "repo_root": str(repo_root),
        "entries": entries,
    }
    _write_snapshot(snapshot_path, payload)
    return {
        "status": "ok",
        "mode": "snapshot",
        "repo_root": str(repo_root),
        "snapshot_path": str(snapshot_path),
        "dirty_paths": sorted({path for entry in entries for path in _entry_paths(entry)}),
    }


def verify(repo_root: Path, snapshot_path: Path, allowed_paths: set[str]) -> dict[str, object]:
    baseline_entries = _load_snapshot(snapshot_path, repo_root)
    current_entries = _status_entries(repo_root)
    baseline = {_entry_identity(entry): entry for entry in baseline_entries}
    current = {_entry_identity(entry): entry for entry in current_entries}
    preserved: set[str] = set()
    allowed_changed: set[str] = set()
    unexpected: set[str] = set()

    for identity in sorted(set(baseline) | set(current)):
        before = baseline.get(identity)
        after = current.get(identity)
        paths = set()
        if before is not None:
            paths.update(_entry_paths(before))
        if after is not None:
            paths.update(_entry_paths(after))
        changed = before is None or after is None or not _entry_matches(before, after)
        if changed:
            if paths.issubset(allowed_paths):
                allowed_changed.update(paths)
            else:
                unexpected.update(path for path in paths if path not in allowed_paths)
        else:
            preserved.update(path for path in paths if path not in allowed_paths)

    status = "blocked" if unexpected else "ok"
    result: dict[str, object] = {
        "status": status,
        "mode": "verify",
        "repo_root": str(repo_root),
        "snapshot_path": str(snapshot_path),
        "allow_paths": sorted(allowed_paths),
        "preserved_preexisting_paths": sorted(preserved),
        "allowed_changed_paths": sorted(allowed_changed),
        "unexpected_paths": sorted(unexpected),
    }
    if unexpected:
        result["failure_reason"] = "unexpected_worktree_changes"
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="比较自动化运行前后的 Git 工作区基线")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("snapshot", "verify"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--repo-root", required=True)
        subparser.add_argument("--snapshot", required=True)
        if command == "verify":
            subparser.add_argument("--allow-path", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repo_root = _resolve_repo_root(args.repo_root)
        snapshot_path = _snapshot_path(args.snapshot, repo_root)
        if args.command == "snapshot":
            result = snapshot(repo_root, snapshot_path)
        else:
            allowed_paths = {_normalise_relative_path(value) for value in args.allow_path}
            result = verify(repo_root, snapshot_path, allowed_paths)
    except GuardError as exc:
        _print_payload(
            {
                "status": "blocked",
                "failure_reason": "worktree_guard_error",
                "error": str(exc),
            }
        )
        return BLOCKED_EXIT_CODE
    _print_payload(result)
    return BLOCKED_EXIT_CODE if result["status"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
