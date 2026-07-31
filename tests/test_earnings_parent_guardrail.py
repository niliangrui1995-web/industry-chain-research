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


def child_prompt(*, status_marker: str = "CURRENT_TEMPLATE_SENTINEL") -> str:
    return "\n".join(
        [
            "TASK_KEY: MU|2026-06-24|May/2026",
            "Company: Micron",
            "Ticker: MU",
            "Report date: 2026-06-24",
            "Fiscal period: May/2026",
            "Sector: Memory",
            "Market: US",
            "Planned child start Beijing: 2026-06-25 07:30",
            "Schedule basis: official_call_plus_3h",
            "Official call Beijing time: 2026-06-25 04:30",
            "Calendar source: Company IR",
            "Event status: confirmed",
            "Source confidence: official_confirmed",
            "Official source URL: https://example.com/ir",
            "Calendar caveat: Official call time confirmed.",
            "",
            "## Prompt Body",
            "OUTPUT LANGUAGE HARD GATE:",
            "AUTOMATION RUN VERSION HARD GATE (prompt_contract_version=2026-07-27.1):",
            "CHILD TASK SKILL HARD GATE:",
            "Project-local skill resolution is successful",
            "FINANCIAL EVIDENCE AUDIT HARD GATE:",
            status_marker,
        ]
    )


def planned_event(module):
    return module.PlannedEvent(
        company="Micron",
        ticker="MU",
        sector="Memory",
        market="US",
        report_date="2026-06-24",
        fiscal_period="May/2026",
        time_label="after market close",
        event_status="confirmed",
        event_source="Company IR",
        source_type="official_ir_event",
        priority="high",
        planned_child_start_beijing="2026-06-25 07:30",
        schedule_basis="official_call_plus_3h",
        official_call_beijing="2026-06-25 04:30",
        original_call_time_text="2026-06-24 16:30 ET",
        original_timezone="America/New_York",
        call_time_source_url="https://example.com/ir",
        call_time_source_type="official_ir_event",
        calendar_source="Company IR",
        source_confidence="official_confirmed",
        official_source_url="https://example.com/ir",
        calendar_caveat="Official call time confirmed.",
        task_key="MU|2026-06-24|May/2026",
    )


class EarningsParentGuardrailTests(unittest.TestCase):
    def test_model_policy_defaults_to_gpt_5_6_sol_xhigh(self) -> None:
        module = load_module(
            "earnings_parent_guardrail_model",
            ROOT / "scripts" / "earnings_parent_guardrail.py",
        )

        self.assertEqual(
            module._model_policy_for_event(None),
            ("gpt-5.6-terra", "xhigh"),
        )
        self.assertEqual(
            module._model_policy_for_child(None),
            ("gpt-5.6-terra", "xhigh"),
        )

    def test_one_shot_rrule_uses_beijing_local_wall_clock(self) -> None:
        module = load_module("earnings_parent_guardrail_rrule", ROOT / "scripts" / "earnings_parent_guardrail.py")
        planned = dt.datetime(2026, 6, 24, 20, 0, tzinfo=module.BEIJING_TZ)
        expected = "RRULE:FREQ=WEEKLY;BYDAY=WE;BYHOUR=20;BYMINUTE=0;COUNT=1"

        self.assertEqual(module._make_one_shot_rrule(planned), expected)
        self.assertEqual(module._make_one_shot_rrule(planned.astimezone(dt.timezone.utc)), expected)
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            module._make_one_shot_rrule(dt.datetime(2026, 6, 24, 20, 0))

    def test_rrule_contract_accepts_legacy_dtstart_but_rejects_utc_fields(self) -> None:
        module = load_module(
            "earnings_parent_guardrail_rrule_contract",
            ROOT / "scripts" / "earnings_parent_guardrail.py",
        )
        planned = dt.datetime(2026, 6, 24, 20, 0, tzinfo=module.BEIJING_TZ)
        local_rrule = (
            "DTSTART:20260624T200000\n"
            "RRULE:FREQ=WEEKLY;BYDAY=WE;BYHOUR=20;BYMINUTE=0;COUNT=1"
        )
        utc_rrule = "RRULE:FREQ=WEEKLY;BYDAY=WE;BYHOUR=12;BYMINUTE=0;COUNT=1"

        self.assertTrue(module._rrule_matches_planned_local_wall_clock(local_rrule, planned))
        self.assertFalse(module._rrule_matches_planned_local_wall_clock(utc_rrule, planned))

    def test_scan_children_flags_scheduler_next_run_mismatch(self) -> None:
        module = load_module("earnings_parent_guardrail", ROOT / "scripts" / "earnings_parent_guardrail.py")
        planned = dt.datetime(2026, 6, 25, 7, 30, tzinfo=module.BEIJING_TZ)
        scheduler_next = planned + dt.timedelta(hours=2)
        prompt = child_prompt()
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

    def test_scheduler_readback_is_final_execution_time_truth(self) -> None:
        module = load_module(
            "earnings_parent_guardrail_scheduler_truth",
            ROOT / "scripts" / "earnings_parent_guardrail.py",
        )
        planned = dt.datetime(2026, 6, 25, 7, 30, tzinfo=module.BEIJING_TZ)
        prompt = child_prompt()
        with tempfile.TemporaryDirectory() as tmp:
            automations = Path(tmp)
            child_dir = automations / "mu-micron-2026-06-24"
            child_dir.mkdir()
            data = {
                "id": "mu-micron-2026-06-24",
                "status": "ACTIVE",
                "rrule": "RRULE:FREQ=WEEKLY;BYDAY=TH;BYHOUR=7;BYMINUTE=30;COUNT=1",
                "prompt": prompt,
            }
            (child_dir / "automation.toml").write_text(module._dump_toml(data), encoding="utf-8")
            scheduler_rows = {
                "mu-micron-2026-06-24": {
                    "status": "ACTIVE",
                    "next_run_at": int(planned.timestamp() * 1000),
                    "last_run_at": None,
                }
            }

            children, problems = module._scan_children(automations, scheduler_rows)

            self.assertEqual(problems, [])
            self.assertTrue(children[0].rrule_ok)
            self.assertTrue(children[0].scheduler_next_run_matches_planned)
            self.assertEqual(children[0].scheduler_next_run_beijing, "2026-06-25 07:30")

    def test_paused_child_is_rerendered_from_current_template_before_resume(self) -> None:
        module = load_module(
            "earnings_parent_guardrail_resume",
            ROOT / "scripts" / "earnings_parent_guardrail.py",
        )
        event = planned_event(module)
        planned = module._parse_beijing_time(event.planned_child_start_beijing)
        assert planned is not None
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automations = root / "automations"
            child_dir = automations / "mu-micron-2026-06-24"
            child_dir.mkdir(parents=True)
            template_path = root / module.CHILD_TEMPLATE_RELATIVE_PATH
            template_path.parent.mkdir(parents=True)
            template_path.write_text(
                "# Current template\n\n"
                "## Prompt Body\n\n"
                "OUTPUT LANGUAGE HARD GATE:\n"
                "AUTOMATION RUN VERSION HARD GATE (prompt_contract_version=2026-07-27.1):\n"
                "CHILD TASK SKILL HARD GATE:\n"
                "FINANCIAL EVIDENCE AUDIT HARD GATE:\n"
                "CURRENT_TEMPLATE_SENTINEL\n",
                encoding="utf-8",
            )
            data = {
                "version": 1,
                "id": "mu-micron-2026-06-24",
                "kind": "cron",
                "name": "old name",
                "prompt": child_prompt(status_marker="OLD_TEMPLATE_SENTINEL"),
                "status": "PAUSED",
                "rrule": module._make_one_shot_rrule(planned),
                "model": "gpt-5.6-terra",
                "reasoning_effort": "xhigh",
                "execution_environment": "local",
                "cwds": [str(root)],
            }
            automation_path = child_dir / "automation.toml"
            automation_path.write_text(module._dump_toml(data), encoding="utf-8")
            scheduler_rows = {
                data["id"]: {
                    "status": "PAUSED",
                    "next_run_at": int(planned.timestamp() * 1000),
                    "last_run_at": None,
                }
            }
            children, problems = module._scan_children(automations, scheduler_rows)
            self.assertEqual(problems, [])
            actions, blockers = module._build_action_plan(
                [event],
                children,
                dt.datetime(2026, 6, 25, 6, 0, tzinfo=module.BEIJING_TZ),
            )

            self.assertEqual(blockers, [])
            self.assertEqual(len(actions["update"]), 1)
            self.assertIn(
                "prompt_template_sync_before_resume",
                actions["update"][0]["update_reasons"],
            )

            result = module._apply_actions(
                actions,
                [event],
                children,
                automations,
                root,
                123456789,
                "test",
            )
            updated = module._read_toml(automation_path)

            self.assertTrue(result["applied"])
            self.assertEqual(updated["status"], "ACTIVE")
            self.assertIn("OUTPUT LANGUAGE HARD GATE", updated["prompt"])
            self.assertIn("prompt_contract_version=2026-07-27.1", updated["prompt"])
            self.assertIn("CURRENT_TEMPLATE_SENTINEL", updated["prompt"])
            self.assertNotIn("OLD_TEMPLATE_SENTINEL", updated["prompt"])

    def test_missing_current_template_never_falls_back_to_old_child_prompt(self) -> None:
        module = load_module(
            "earnings_parent_guardrail_template_gate",
            ROOT / "scripts" / "earnings_parent_guardrail.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(module._template_body(Path(tmp), []))


if __name__ == "__main__":
    unittest.main()
