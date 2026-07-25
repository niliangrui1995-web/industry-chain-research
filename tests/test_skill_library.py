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

    def test_listed_company_research_requires_pre_event_expectation_check(self) -> None:
        framework = (SKILL_ROOT / "user-investment-framework" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        earnings_checklist = (
            SKILL_ROOT
            / "earnings-call-investment-analyst"
            / "references"
            / "analysis-checklist.md"
        ).read_text(encoding="utf-8")
        evidence_schema = (
            SKILL_ROOT
            / "earnings-call-investment-analyst"
            / "references"
            / "evidence-schema.md"
        ).read_text(encoding="utf-8")
        framework_interface = (
            SKILL_ROOT / "user-investment-framework" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")

        for needle in [
            "上市公司盈利预期门禁（条件强制）",
            "point-in-time",
            "不要求机构预测恰好在前一日更新",
            "无历史 point-in-time 快照时",
            "每家机构只保留事件前最后一份目标年度归母净利润预测",
            "最新单季度扣非归母×4",
            "按单季扣非年化口径超预期/区间跨越/低于预期/证据不足",
            "comparison_basis=annualized_quarterly_deducted_vs_fy_attributable_consensus",
            "annualized_core_gap_status=above|straddles|below|insufficient",
            "formal_surprise_status=N/A",
            "company_value_type=actual_quarter|preannouncement_quarter_range|derived_quarter",
            "正式报告发布后以正式值替换预告值",
            "Q4扣非=全年扣非-前三季度扣非",
            "PE(TTM，用户口径)",
            "valuation_basis=latest_single_quarter_deducted_attributable_net_profit_x4",
            "consensus_metric=unresolved",
        ]:
            with self.subTest(document="framework", needle=needle):
                self.assertIn(needle, framework)

        for needle in [
            "expectation_as_of",
            "expectation_age_days",
            "当前滚动 F10",
            "最新单季度扣非归母×4",
            "company_metric=annualized_single_quarter_deducted_attributable_net_profit",
            "comparison_basis=annualized_quarterly_deducted_vs_fy_attributable_consensus",
            "Prior Guidance",
            "formal_surprise_status=N/A",
            "derivation_formula",
            "annualization_factor=4",
            "正式报告发布后以正式值替换预告值",
            "Q4扣非=全年扣非-前三季度扣非",
            "不得事后自设容忍带",
            "不得机械用低值减低值",
            "当前总市值/(最新单季度扣非归母×4)",
            "PE(TTM，用户口径)",
        ]:
            with self.subTest(document="earnings_checklist", needle=needle):
                self.assertIn(needle, earnings_checklist)

        for needle in [
            "expectation_as_of",
            "company_metric",
            "consensus_metric",
            "comparison_basis",
            "quarterly_value_low",
            "annualization_factor",
            "annualized_value_low",
            "annualized_core_gap_status",
            "formal_surprise_status",
            "derivation_formula",
            "market_cap_as_of",
            "pe_ttm_user_low",
            "valuation_basis",
        ]:
            with self.subTest(document="evidence_schema", needle=needle):
                self.assertIn(needle, evidence_schema)

        self.assertIn("latest single-quarter deducted attributable profit", framework_interface)

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
