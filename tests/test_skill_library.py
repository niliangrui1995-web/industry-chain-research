from __future__ import annotations

import importlib.util
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
    "financial-evidence-audit",
    "ht-local-market-data",
    "income-investment",
    "research-industry-chain",
    "research-listed-company",
    "user-investment-discipline",
}
REMOVED_ROUTES = {
    "industry-research-router",
    "browser-grok-gemini-research",
    "semiconductor-ai-chain-investment-researcher",
    "user-investment-framework",
}
class SkillLibraryTests(unittest.TestCase):
    def test_repository_uses_standard_skill_root(self) -> None:
        self.assertFalse((ROOT / "skills").exists())
        actual = {path.name for path in SKILL_ROOT.iterdir() if path.is_dir()}
        self.assertEqual(len(actual), 11)
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

        discipline_lines = (
            SKILL_ROOT / "user-investment-discipline" / "SKILL.md"
        ).read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(discipline_lines), 100)
        self.assertLessEqual(len((ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines()), 60)

    def test_active_files_do_not_reference_removed_routes(self) -> None:
        paths = list(SKILL_ROOT.glob("*/SKILL.md")) + [
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "docs" / "earnings_movement" / "A_SHARE_EARNINGS_MOVEMENT_PROMPT.md",
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for removed in REMOVED_ROUTES:
                with self.subTest(path=path, removed=removed):
                    self.assertNotIn(removed, text)

    def test_hithink_finance_is_registered_as_an_account_level_data_companion(self) -> None:
        for path in [
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "SKILL_PACK_MANIFEST.md",
        ]:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn("hithink-finance", text)
                self.assertIn("账户级", text)
                self.assertIn("厂商", text)

    def test_domain_routes_are_mutually_bounded(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        company = (SKILL_ROOT / "research-listed-company" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        industry = (SKILL_ROOT / "research-industry-chain" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        income = (SKILL_ROOT / "income-investment" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        discipline = (
            SKILL_ROOT / "user-investment-discipline" / "SKILL.md"
        ).read_text(encoding="utf-8")

        for needle in ["上市公司深研", "护城河", "point-in-time", "strongest bear case"]:
            self.assertIn(needle, company)
        for needle in ["需求超过合格供给", "第二供应商", "不自动授予瓶颈等级"]:
            self.assertIn(needle, industry)
        for needle in ["REIT", "不得对所有行业机械使用 EPS payout", "portfolio_action=N/A"]:
            self.assertIn(needle, income)
        for needle in ["MA30", "加杠杆", "每一次都一样！！！"]:
            self.assertIn(needle, discipline)

        self.assertIn("Do not use for pure industry-chain", company)
        self.assertIn("Do not use for ordinary company", discipline)
        self.assertIn("Do not use for quote-only dividend-yield", income)

        for route in [
            "research-listed-company",
            "research-industry-chain",
            "earnings-call-investment-analyst",
            "income-investment",
            "a-share-company-tracking",
            "a-share-leverage-capitulation-analyst",
            "user-investment-discipline",
            "ai-chain-research-orchestrator",
        ]:
            with self.subTest(route=route):
                self.assertIn(route, agents)

    def test_listed_company_research_requires_pre_event_expectation_check(self) -> None:
        company = (SKILL_ROOT / "research-listed-company" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        expectation = (
            SKILL_ROOT
            / "research-listed-company"
            / "references"
            / "expectation-valuation.md"
        ).read_text(encoding="utf-8")
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

        for needle in ["point-in-time", "financial-evidence-audit", "provisional"]:
            self.assertIn(needle, company)

        for needle in [
            "expectation_as_of",
            "每家机构只保留事件前最后一份目标年度预测",
            "当前滚动 F10",
            "最新单季度扣非归母净利润",
            "comparison_basis=annualized_quarterly_deducted_vs_fy_attributable_consensus",
            "annualized_core_gap_status=above|straddles|below|insufficient",
            "formal_surprise_status=N/A",
            "company_value_type=actual_quarter|preannouncement_quarter_range|derived_quarter",
            "正式报告发布后以正式值替换预告值",
            "Q4扣非=全年扣非-前三季度扣非",
            "PE(TTM，用户口径)",
            "valuation_basis=latest_single_quarter_deducted_attributable_net_profit_x4",
        ]:
            with self.subTest(document="expectation", needle=needle):
                self.assertIn(needle, expectation)

        for needle in [
            "expectation_as_of",
            "expectation_age_days",
            "当前滚动 F10",
            "最新单季度扣非归母×4",
            "company_metric=deducted_attributable_net_profit",
            "derived_metric=annualized_single_quarter_deducted_attributable_net_profit",
            "formal_surprise_status=N/A",
            "derivation_formula",
            "不得事后自设容忍带",
            "PE(TTM，用户口径)",
        ]:
            with self.subTest(document="earnings_checklist", needle=needle):
                self.assertIn(needle, earnings_checklist)

        for needle in [
            "expectation_as_of",
            "company_metric",
            "derived_metric",
            "comparison_basis",
            "annualization_factor",
            "annualized_core_gap_status",
            "formal_surprise_status",
            "market_cap_as_of",
            "valuation_basis",
        ]:
            with self.subTest(document="evidence_schema", needle=needle):
                self.assertIn(needle, evidence_schema)

        self.assertIn("market=A-share", earnings_checklist)
        self.assertIn("非 A 股", earnings_checklist)
        self.assertIn("generic valuation", earnings_checklist)
        self.assertIn("expectation_surprise", earnings_checklist)
        self.assertIn("subject_kind=reported_actual|company_guidance", earnings_checklist)
        self.assertIn("非 A 股", expectation)
        self.assertIn("expectation_surprise", expectation)
        self.assertIn("expectation_surprise", evidence_schema)

        child_template = (
            ROOT / "docs" / "earnings_parent" / "CHILD_PROMPT_TEMPLATE.md"
        ).read_text(encoding="utf-8")
        for needle in [
            "calculation_audit_status",
            "audit_release_status",
            "audit_artifact",
            "audit_blockers",
            "unresolved_numeric_conflicts",
        ]:
            self.assertIn(needle, child_template)
            self.assertIn(needle, evidence_schema)
        self.assertNotIn("financial_audit_status", child_template)

    def test_active_automation_prompts_use_standard_paths(self) -> None:
        prompt_paths = [
            ROOT / "docs" / "earnings_movement" / "A_SHARE_EARNINGS_MOVEMENT_PROMPT.md",
            ROOT / "docs" / "company_tracking" / "A_SHARE_COMPANY_TRACKING_PROMPT.md",
            ROOT / "docs" / "company_tracking" / "A_SHARE_COMPANY_TRACKING_AUTOMATION.md",
            ROOT / "docs" / "earnings_parent" / "PARENT_POLICY.md",
            ROOT / "docs" / "earnings_parent" / "MOTHER_PROMPT_ENTRYPOINT.md",
            ROOT / "docs" / "earnings_parent" / "CHILD_PROMPT_TEMPLATE.md",
        ]
        for path in prompt_paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertNotIn("产业链投研\\skills\\", text)
                self.assertNotIn("skills/industry-research-router", text)

    def test_automation_outputs_require_chinese(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        earnings_movement = (
            ROOT / "docs" / "earnings_movement" / "A_SHARE_EARNINGS_MOVEMENT_PROMPT.md"
        ).read_text(encoding="utf-8")
        company_tracking = (
            ROOT / "docs" / "company_tracking" / "A_SHARE_COMPANY_TRACKING_PROMPT.md"
        ).read_text(encoding="utf-8")
        deprecated_tracking = (
            ROOT / "docs" / "company_tracking" / "A_SHARE_COMPANY_TRACKING_AUTOMATION.md"
        ).read_text(encoding="utf-8")
        parent_policy = (
            ROOT / "docs" / "earnings_parent" / "PARENT_POLICY.md"
        ).read_text(encoding="utf-8")
        mother_entrypoint = (
            ROOT / "docs" / "earnings_parent" / "MOTHER_PROMPT_ENTRYPOINT.md"
        ).read_text(encoding="utf-8")
        child_template = (
            ROOT / "docs" / "earnings_parent" / "CHILD_PROMPT_TEMPLATE.md"
        ).read_text(encoding="utf-8")

        for text in [
            agents,
            earnings_movement,
            company_tracking,
            deprecated_tracking,
            parent_policy,
            mother_entrypoint,
        ]:
            self.assertIn("用户可见", text)
            self.assertIn("中文", text)
        self.assertIn("已废弃入口", deprecated_tracking)
        self.assertIn("A_SHARE_COMPANY_TRACKING_PROMPT.md", deprecated_tracking)
        self.assertNotIn("@chrome", deprecated_tracking)
        self.assertNotIn("Multi-agent requirement", deprecated_tracking)
        self.assertIn("OUTPUT LANGUAGE HARD GATE", child_template)
        self.assertIn("must be written in Chinese", child_template)
        self.assertIn("FINANCIAL EVIDENCE AUDIT HARD GATE", mother_entrypoint)
        self.assertIn("financial-evidence-audit", mother_entrypoint)

    def test_earnings_movement_uses_the_earnings_domain_route(self) -> None:
        prompt = (
            ROOT / "docs" / "earnings_movement" / "A_SHARE_EARNINGS_MOVEMENT_PROMPT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("earnings-call-investment-analyst", prompt)
        self.assertIn("financial-evidence-audit", prompt)
        self.assertIn("a-share-disclosure-trading-data", prompt)
        self.assertIn("不再并行加载 `research-listed-company`", prompt)

    def test_upstream_method_license_is_preserved(self) -> None:
        notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 xbtlin", notice)
        self.assertIn("MIT License", notice)
        self.assertIn("09ebc400a8815636e02f5b7d1d811a53164a0b92", notice)
        self.assertIn("fadewalk/serenity-stock-choke", notice)
        self.assertIn("b64c5fd7823e8ab75c8421d4e5077270430a5124", notice)
        self.assertIn("Copyright (c) 2025-2026 fadewalk", notice)
        self.assertIn("research-industry-chain", notice)


class EarningsPackSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        script = (
            SKILL_ROOT
            / "earnings-call-investment-analyst"
            / "scripts"
            / "earnings_pack_builder.py"
        )
        spec = importlib.util.spec_from_file_location("earnings_pack_builder", script)
        assert spec is not None and spec.loader is not None
        cls.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.builder)

    def test_unverified_shared_platform_is_not_an_official_source(self) -> None:
        sources, gaps = self.builder.build_sources(
            source_inventory=None,
            webcast_assets={
                "input_url": "https://event.on24.com/unverified-event",
                "assets": [
                    {
                        "category": "document",
                        "url": "https://q4cdn.com/unverified.pdf",
                    }
                ],
            },
            transcript_manifest=None,
            transcript_path=None,
            manual_sources=[],
            company_domains={"issuer.example"},
        )

        self.assertEqual([source["source_type"] for source in sources], ["unknown", "unknown"])
        official_ids = [
            source_id
            for source_type in ["company_original", "regulatory_filing", "official_event_platform"]
            for source_id in self.builder.source_ids_by_type(sources, source_type)
        ]
        self.assertEqual(official_ids, [])
        self.assertEqual(self.builder.company_original_status(sources, gaps), "unavailable")

    def test_verified_manual_platform_role_survives_webcast_deduplication(self) -> None:
        event_url = "https://event.on24.com/issuer-q2-event"
        notes = "Verified company IR link: https://issuer.example/ir/q2"
        sources, _ = self.builder.build_sources(
            source_inventory=None,
            webcast_assets={"input_url": event_url},
            transcript_manifest=None,
            transcript_path=None,
            manual_sources=[
                {"url": event_url, "type": "official_event_platform", "notes": notes}
            ],
            company_domains={"issuer.example"},
        )

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["source_type"], "official_event_platform")
        self.assertEqual(sources[0]["hosting_type"], "official_platform_hosted")
        self.assertEqual(sources[0]["notes"], notes)
        self.assertEqual(
            self.builder.source_ids_by_type(sources, "official_event_platform"),
            [sources[0]["id"]],
        )

    def test_company_and_regulatory_domains_keep_their_source_roles(self) -> None:
        self.assertEqual(
            self.builder.classify_source("https://ir.issuer.example/q2", company_domains={"issuer.example"}),
            "company_original",
        )
        self.assertEqual(
            self.builder.classify_source("https://www.sec.gov/Archives/issuer-q2"),
            "regulatory_filing",
        )


if __name__ == "__main__":
    unittest.main()
