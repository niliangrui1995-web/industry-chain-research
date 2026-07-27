from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


PROMPT_CONTRACT_VERSION = "2026-07-27.1"
BEIJING = ZoneInfo("Asia/Shanghai")


class MetadataError(RuntimeError):
    pass


def _run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown git error"
        raise MetadataError(f"git command failed: {detail}")
    return completed.stdout.strip()


def _skill_files(
    repo_root: Path, skill_root: Path, skill_names: list[str]
) -> list[Path]:
    names = sorted(set(skill_names)) or sorted(
        path.name for path in skill_root.iterdir() if path.is_dir()
    )
    relative_directories: list[str] = []
    for name in names:
        skill_dir = skill_root / name
        entrypoint = skill_dir / "SKILL.md"
        if not entrypoint.is_file():
            raise MetadataError(f"missing skill entrypoint: {entrypoint}")
        relative_directories.append(skill_dir.relative_to(repo_root).as_posix())

    listed = _run_git(
        repo_root,
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        *relative_directories,
    )
    files = [repo_root / line for line in listed.splitlines() if line]
    entrypoints = {skill_root / name / "SKILL.md" for name in names}
    if not entrypoints.issubset(set(files)):
        missing = sorted(str(path) for path in entrypoints - set(files))
        raise MetadataError(
            "skill entrypoint is ignored or outside revision tracking: "
            + ", ".join(missing)
        )
    return sorted((path for path in files if path.is_file()), key=lambda path: path.as_posix())


def _content_digest(repo_root: Path, files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(repo_root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def collect_metadata(repo_root: Path, skill_names: list[str]) -> dict[str, object]:
    repo_root = repo_root.resolve()
    skill_root = repo_root / ".agents" / "skills"
    if not skill_root.is_dir():
        raise MetadataError(f"missing project skill root: {skill_root}")

    files = _skill_files(repo_root, skill_root, skill_names)
    content_digest = _content_digest(repo_root, files)
    git_sha = _run_git(repo_root, "rev-parse", "--verify", "HEAD")
    dirty_output = _run_git(repo_root, "status", "--porcelain", "--", ".agents/skills")
    skill_tree_status = "dirty" if dirty_output else "clean"
    skill_revision = f"git:{git_sha}"
    if skill_tree_status == "dirty":
        skill_revision += f"+dirty:{content_digest[:12]}"

    selected_skills = sorted(set(skill_names)) or sorted(
        path.name for path in skill_root.iterdir() if path.is_dir()
    )
    return {
        "status": "ok",
        "prompt_contract_version": PROMPT_CONTRACT_VERSION,
        "skill_revision": skill_revision,
        "skill_content_sha256": content_digest,
        "skill_tree_status": skill_tree_status,
        "skills": selected_skills,
        "captured_at_beijing": datetime.now(BEIJING).isoformat(timespec="seconds"),
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve reproducible metadata for a project-skill automation run."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Git repository containing .agents/skills.",
    )
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Project skill name used by the run; repeat for multiple skills.",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        payload = collect_metadata(args.repo_root, args.skill)
        exit_code = 0
    except (MetadataError, OSError) as exc:
        payload = {
            "status": "blocked",
            "failure_reason": "precheck_failed",
            "prompt_contract_version": PROMPT_CONTRACT_VERSION,
            "skill_revision": "N/A",
            "error": str(exc),
        }
        exit_code = 2

    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
