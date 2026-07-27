from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "automation_run_metadata.py"
CONTRACT_VERSION = "2026-07-27.1"


class AutomationRunMetadataTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()

    def _run(self, repo: Path, skill: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python",
                str(SCRIPT),
                "--repo-root",
                str(repo),
                "--skill",
                skill,
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def _make_repo(self, root: Path) -> str:
        skill_dir = root / ".agents" / "skills" / "demo-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: test\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        (root / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
        self._git(root, "init")
        self._git(root, "config", "user.email", "automation-test@example.invalid")
        self._git(root, "config", "user.name", "Automation Test")
        self._git(root, "add", ".gitignore", ".agents/skills/demo-skill/SKILL.md")
        self._git(root, "commit", "-m", "test fixture")
        return self._git(root, "rev-parse", "HEAD")

    def test_clean_skill_tree_records_git_revision_and_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            git_sha = self._make_repo(repo)

            completed = self._run(repo, "demo-skill")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["prompt_contract_version"], CONTRACT_VERSION)
            self.assertEqual(payload["skill_revision"], f"git:{git_sha}")
            self.assertEqual(payload["skill_tree_status"], "clean")
            self.assertEqual(payload["skills"], ["demo-skill"])
            self.assertRegex(payload["skill_content_sha256"], r"^[0-9a-f]{64}$")

    def test_dirty_skill_tree_is_not_reported_as_pinned_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            git_sha = self._make_repo(repo)
            skill = repo / ".agents" / "skills" / "demo-skill" / "SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

            completed = self._run(repo, "demo-skill")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["skill_tree_status"], "dirty")
            self.assertRegex(
                payload["skill_revision"],
                rf"^git:{git_sha}\+dirty:[0-9a-f]{{12}}$",
            )

    def test_missing_skill_fails_closed_with_machine_readable_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self._make_repo(repo)

            completed = self._run(repo, "missing-skill")

            self.assertEqual(completed.returncode, 2)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["failure_reason"], "precheck_failed")
            self.assertEqual(payload["skill_revision"], "N/A")
            self.assertIn("missing skill entrypoint", payload["error"])

    def test_ignored_runtime_cache_does_not_change_skill_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self._make_repo(repo)
            before = json.loads(self._run(repo, "demo-skill").stdout)
            cache = (
                repo
                / ".agents"
                / "skills"
                / "demo-skill"
                / "scripts"
                / "__pycache__"
                / "helper.pyc"
            )
            cache.parent.mkdir(parents=True)
            cache.write_bytes(b"generated runtime cache")

            completed = self._run(repo, "demo-skill")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            after = json.loads(completed.stdout)
            self.assertEqual(after["skill_tree_status"], "clean")
            self.assertEqual(after["skill_revision"], before["skill_revision"])
            self.assertEqual(after["skill_content_sha256"], before["skill_content_sha256"])


if __name__ == "__main__":
    unittest.main()
