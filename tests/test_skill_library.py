from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills"
EXPECTED_SKILLS = {
    "a-share-company-tracking",
    "a-share-disclosure-trading-data",
    "a-share-leverage-capitulation-analyst",
    "ai-chain-research-orchestrator",
    "earnings-call-investment-analyst",
    "ht-local-market-data",
    "research-industry-chain",
    "user-investment-framework",
}
REMOVED_ROUTES = {
    "industry-research-router",
    "browser-grok-gemini-research",
    "semiconductor-ai-chain-investment-researcher",
}


class SkillLibraryTests(unittest.TestCase):
    def test_repository_uses_standard_skill_root(self) -> None:
        self.assertFalse((ROOT / "skills").exists())
        actual = {path.name for path in SKILL_ROOT.iterdir() if path.is_dir()}
        self.assertEqual(actual, EXPECTED_SKILLS)

    def test_skill_metadata_and_entrypoints_are_compact(self) -> None:
        for name in sorted(EXPECTED_SKILLS):
            with self.subTest(skill=name):
                skill_file = SKILL_ROOT / name / "SKILL.md"
                metadata_file = SKILL_ROOT / name / "agents" / "openai.yaml"
                text = skill_file.read_text(encoding="utf-8")
                frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
                self.assertIsNotNone(frontmatter)
                assert frontmatter is not None
                name_match = re.search(r"(?m)^name:\s*([^\n]+)$", frontmatter.group(1))
                self.assertIsNotNone(name_match)
                assert name_match is not None
                self.assertEqual(name_match.group(1).strip().strip("\"'"), name)
                self.assertLessEqual(len(text.splitlines()), 180)
                metadata = metadata_file.read_text(encoding="utf-8")
                self.assertIn(f"${name}", metadata)

        master_lines = (SKILL_ROOT / "user-investment-framework" / "SKILL.md").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertLessEqual(len(master_lines), 100)
        self.assertLessEqual(len((ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines()), 60)

    def test_active_skills_do_not_reference_removed_routes(self) -> None:
        for skill_file in SKILL_ROOT.glob("*/SKILL.md"):
            text = skill_file.read_text(encoding="utf-8")
            for removed in REMOVED_ROUTES:
                with self.subTest(skill=skill_file.parent.name, removed=removed):
                    self.assertNotIn(removed, text)

    def test_active_automation_prompts_use_standard_paths(self) -> None:
        prompt_paths = [
            ROOT / "docs" / "earnings_movement" / "A_SHARE_EARNINGS_MOVEMENT_PROMPT.md",
            ROOT / "docs" / "company_tracking" / "A_SHARE_COMPANY_TRACKING_PROMPT.md",
            ROOT / "docs" / "earnings_parent" / "PARENT_POLICY.md",
            ROOT / "docs" / "earnings_parent" / "MOTHER_PROMPT_ENTRYPOINT.md",
            ROOT / "docs" / "earnings_parent" / "CHILD_PROMPT_TEMPLATE.md",
        ]
        for path in prompt_paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertNotIn("产业链投研\\skills\\", text)
                self.assertNotIn("skills/industry-research-router", text)


if __name__ == "__main__":
    unittest.main()
