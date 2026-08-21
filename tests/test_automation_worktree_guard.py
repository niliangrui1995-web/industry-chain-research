from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "automation_worktree_guard.py"


class AutomationWorktreeGuardTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()

    def _make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        (repo / "tracked.txt").write_text("clean\n", encoding="utf-8")
        self._git(repo, "init")
        self._git(repo, "config", "user.email", "guard-test@example.invalid")
        self._git(repo, "config", "user.name", "Worktree Guard Test")
        self._git(repo, "add", "tracked.txt")
        self._git(repo, "commit", "-m", "test fixture")
        return repo

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python", str(SCRIPT), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def _snapshot(self, repo: Path, snapshot: Path) -> dict[str, object]:
        completed = self._run("snapshot", "--repo-root", str(repo), "--snapshot", str(snapshot))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ok")
        return payload

    def _verify(
        self, repo: Path, snapshot: Path, *allow_paths: str
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        command = ["verify", "--repo-root", str(repo), "--snapshot", str(snapshot)]
        for allow_path in allow_paths:
            command.extend(["--allow-path", allow_path])
        completed = self._run(*command)
        return completed, json.loads(completed.stdout)

    def test_preserves_preexisting_nonwhite_change_when_its_content_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            snapshot = root / "snapshot.json"
            (repo / "tracked.txt").write_text("written by another automation\n", encoding="utf-8")

            self._snapshot(repo, snapshot)
            completed, payload = self._verify(repo, snapshot)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["preserved_preexisting_paths"], ["tracked.txt"])
            self.assertEqual(payload["unexpected_paths"], [])

    def test_blocks_new_nonwhite_path_after_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            snapshot = root / "snapshot.json"

            self._snapshot(repo, snapshot)
            (repo / "foreign-output.md").write_text("new foreign output\n", encoding="utf-8")
            completed, payload = self._verify(repo, snapshot)

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["failure_reason"], "unexpected_worktree_changes")
            self.assertEqual(payload["unexpected_paths"], ["foreign-output.md"])

    def test_blocks_content_change_to_path_already_dirty_at_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            snapshot = root / "snapshot.json"
            target = repo / "tracked.txt"
            target.write_text("first external value\n", encoding="utf-8")

            self._snapshot(repo, snapshot)
            target.write_text("second external value\n", encoding="utf-8")
            completed, payload = self._verify(repo, snapshot)

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["unexpected_paths"], ["tracked.txt"])

    def test_accepts_repeated_allow_paths_without_staging_them(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            snapshot = root / "snapshot.json"

            self._snapshot(repo, snapshot)
            (repo / "owned-one.json").write_text("one\n", encoding="utf-8")
            (repo / "owned-two.json").write_text("two\n", encoding="utf-8")
            completed, payload = self._verify(repo, snapshot, "owned-one.json", "owned-two.json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["unexpected_paths"], [])
            self.assertEqual(
                payload["allowed_changed_paths"],
                ["owned-one.json", "owned-two.json"],
            )
            self.assertEqual(self._git(repo, "diff", "--cached", "--name-only"), "")

    def test_handles_space_and_unicode_filename_in_porcelain_z_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            snapshot = root / "snapshot.json"
            relative_path = "外部 文件 [第二版].txt"
            (repo / relative_path).write_text("external\n", encoding="utf-8")

            self._snapshot(repo, snapshot)
            completed, payload = self._verify(repo, snapshot)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["preserved_preexisting_paths"], [relative_path])

    def test_blocks_deleted_preexisting_dirty_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            snapshot = root / "snapshot.json"
            target = repo / "tracked.txt"
            target.write_text("external change\n", encoding="utf-8")

            self._snapshot(repo, snapshot)
            target.unlink()
            completed, payload = self._verify(repo, snapshot)

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["unexpected_paths"], ["tracked.txt"])

    def test_rejects_windows_rooted_allow_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            snapshot = root / "snapshot.json"

            self._snapshot(repo, snapshot)
            completed, payload = self._verify(repo, snapshot, r"\outside")

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["failure_reason"], "worktree_guard_error")


if __name__ == "__main__":
    unittest.main()
