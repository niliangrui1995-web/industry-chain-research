from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class EarningsParentGuardrailTests(unittest.TestCase):
    def test_model_policy_defaults_to_gpt_5_6_sol_ultra(self) -> None:
        module = load_module(
            "earnings_parent_guardrail_model",
            ROOT / "scripts" / "earnings_parent_guardrail.py",
        )

        self.assertEqual(
            module._model_policy_for_event(None),
            ("gpt-5.6-sol", "ultra"),
        )
        self.assertEqual(
            module._model_policy_for_child(None),
            ("gpt-5.6-sol", "ultra"),
        )

    def test_scan_children_flags_scheduler_next_run_mismatch(self) -> None:
        module = load_module("earnings_parent_guardrail", ROOT / "scripts" / "earnings_parent_guardrail.py")
        planned = dt.datetime(2026, 6, 25, 7, 30, tzinfo=module.BEIJING_TZ)
        scheduler_next = planned + dt.timedelta(hours=2)
        prompt = "\n".join(
            [
                "TASK_KEY: MU|2026-06-24|May/2026",
                "Company: Micron",
                "Ticker: MU",
                "Report date: 2026-06-24",
                "Fiscal period: May/2026",
                "Planned child start Beijing: 2026-06-25 07:30",
                "Schedule basis: official_call_plus_3h",
                "",
                "CHILD TASK SKILL HARD GATE:",
                "Project-local skill resolution is successful",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            automations = Path(tmp)
            child_dir = automations / "mu-micron-2026-06-24"
            child_dir.mkdir()
            toml = "\n".join(
                [
                    'id = "mu-micron-2026-06-24"',
                    'status = "ACTIVE"',
                    'rrule = "DTSTART:20260625T073000\\nRRULE:FREQ=WEEKLY;BYDAY=TH;BYHOUR=7;BYMINUTE=30;COUNT=1"',
                    f"prompt = {json.dumps(prompt, ensure_ascii=False)}",
                    "",
                ]
            )
            (child_dir / "automation.toml").write_text(toml, encoding="utf-8")
            scheduler_rows = {
                "mu-micron-2026-06-24": {
                    "status": "ACTIVE",
                    "next_run_at": int(scheduler_next.timestamp() * 1000),
                    "last_run_at": None,
                }
            }

            children, problems = module._scan_children(automations, scheduler_rows)

            self.assertEqual(problems, [])
            self.assertEqual(len(children), 1)
            self.assertFalse(children[0].scheduler_next_run_matches_planned)
            self.assertEqual(children[0].scheduler_next_run_delta_seconds, 7200)


if __name__ == "__main__":
    unittest.main()
