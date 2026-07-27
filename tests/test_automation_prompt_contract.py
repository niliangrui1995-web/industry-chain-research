from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_VERSION = "2026-07-27.1"


def load_metadata_module():
    path = ROOT / "scripts" / "automation_run_metadata.py"
    spec = importlib.util.spec_from_file_location("automation_run_metadata", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AutomationPromptContractTests(unittest.TestCase):
    def test_contract_document_and_runtime_helper_share_one_version(self) -> None:
        module = load_metadata_module()
        contract = (
            ROOT / "docs" / "automation" / "AUTOMATION_RUN_CONTRACT.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(module.PROMPT_CONTRACT_VERSION, CONTRACT_VERSION)
        self.assertIn(f"prompt_contract_version={CONTRACT_VERSION}", contract)
        for field in [
            "skill_revision",
            "prompt_contract_version",
            "skill_content_sha256",
            "skill_tree_status",
            "skills",
        ]:
            self.assertIn(field, contract)

    def test_automation_entrypoints_persist_version_metadata(self) -> None:
        prompt_paths = [
            ROOT / "docs" / "company_tracking" / "A_SHARE_COMPANY_TRACKING_PROMPT.md",
            ROOT / "docs" / "earnings_movement" / "A_SHARE_EARNINGS_MOVEMENT_PROMPT.md",
            ROOT / "docs" / "earnings_parent" / "PARENT_POLICY.md",
            ROOT / "docs" / "earnings_parent" / "MOTHER_PROMPT_ENTRYPOINT.md",
            ROOT / "docs" / "earnings_parent" / "CHILD_PROMPT_TEMPLATE.md",
            ROOT / "artifacts" / "weekly_chain_tracking" / "README.md",
        ]
        for path in prompt_paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("AUTOMATION_RUN_CONTRACT.md", text)
                self.assertIn("automation_run_metadata.py", text)
                self.assertIn("skill_revision", text)
                self.assertIn("prompt_contract_version", text)

    def test_weekly_templates_have_durable_metadata_fields(self) -> None:
        for family in ["ai_chain", "ai_pcb", "optical_module"]:
            path = (
                ROOT
                / "artifacts"
                / "weekly_chain_tracking"
                / family
                / "BASELINE_TEMPLATE.md"
            )
            with self.subTest(family=family):
                text = path.read_text(encoding="utf-8")
                self.assertIn("## 运行元数据", text)
                self.assertIn("skill_revision", text)
                self.assertIn(
                    f"`prompt_contract_version`：`{CONTRACT_VERSION}`",
                    text,
                )

    def test_company_tracking_prompt_enforces_pre_and_post_write_e2e_gates(self) -> None:
        prompt = (
            ROOT / "docs" / "company_tracking" / "A_SHARE_COMPANY_TRACKING_PROMPT.md"
        ).read_text(encoding="utf-8")
        readme = (
            ROOT / "artifacts" / "company_tracking" / "README.md"
        ).read_text(encoding="utf-8")

        for text in [prompt, readme]:
            self.assertIn("validate_company_tracking_run.py snapshot", text)
            self.assertIn("validate_company_tracking_run.py validate", text)
            self.assertIn(".run_validation_snapshot.tmp", text)
            self.assertIn("blocked/postwrite_validation_failed", text)


if __name__ == "__main__":
    unittest.main()
