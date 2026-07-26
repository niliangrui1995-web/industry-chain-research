from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents" / "skills" / "research-industry-chain" / "scripts" / "validate_bottleneck_evidence.py"


class BottleneckEvidenceValidatorTests(unittest.TestCase):
    def run_row(self, row: dict[str, str]) -> tuple[int, dict]:
        fields = [
            "check_id", "node", "severity", "claim_window", "claim_as_of", "max_age_days",
            "demand_evidence_kind", "supply_evidence_kind", "demand_evidence",
            "demand_evidence_date", "demand_source_type", "demand_source_locator",
            "supply_evidence", "supply_evidence_date", "supply_source_type",
            "supply_source_locator", "supply_gap_evidence", "gap_evidence_date",
            "gap_source_type", "gap_source_locator", "direct_gap_consequence",
            "constraint_mechanism", "time_horizon", "evidence_grade", "source",
            "source_date", "counterevidence",
            "substitution_path", "second_source_status", "relief_window",
            "positive_validation", "key_reversal",
        ]
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", newline="", delete=False)
        with handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerow(row)
        path = Path(handle.name)
        self.addCleanup(path.unlink, missing_ok=True)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--csv",
                str(path),
                "--as-of",
                "2026-07-27",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        return proc.returncode, json.loads(proc.stdout)

    def complete_row(self) -> dict[str, str]:
        return {
            "check_id": "check-qualified-component-20260727",
            "node": "qualified component",
            "severity": "soft_bottleneck",
            "claim_window": "current",
            "claim_as_of": "2026-07-27",
            "demand_evidence_kind": "demand_step",
            "supply_evidence_kind": "qualified_supply_limit",
            "demand_evidence": "dated customer ramp",
            "demand_evidence_date": "2026-07-20",
            "demand_source_type": "official_counterparty",
            "demand_source_locator": "https://example.com/customer-ramp",
            "supply_evidence": "qualified capacity disclosure",
            "supply_evidence_date": "2026-07-18",
            "supply_source_type": "company_original",
            "supply_source_locator": "https://example.com/supplier-capacity",
            "supply_gap_evidence": "allocation and delivery delay",
            "gap_evidence_date": "2026-07-25",
            "gap_source_type": "official_counterparty",
            "gap_source_locator": "https://example.com/allocation-notice",
            "direct_gap_consequence": "allocation and delayed customer delivery",
            "constraint_mechanism": "qualification and yield",
            "time_horizon": "next 2 quarters",
            "evidence_grade": "B",
            "source": "official disclosure",
            "source_date": "2026-07-25",
            "counterevidence": "second source trial",
            "substitution_path": "second-source qualification",
            "second_source_status": "qualifying",
            "relief_window": "two quarters if qualification succeeds",
            "positive_validation": "allocation persists after capacity ramp",
            "key_reversal": "qualified second source reaches volume",
        }

    def test_complete_packet_only_becomes_reviewable(self) -> None:
        code, payload = self.run_row(self.complete_row())
        self.assertEqual(code, 0)
        node = payload["nodes"][0]
        self.assertEqual(node["review_status"], "eligible_for_bottleneck_review")
        self.assertEqual(node["freshness_status"], "fresh")
        self.assertEqual(node["max_age_days"], 180)
        self.assertNotIn("hard_bottleneck", json.dumps(payload))

    def test_missing_supply_gap_fails(self) -> None:
        row = self.complete_row()
        row["supply_gap_evidence"] = ""
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        self.assertIn("supply_gap_evidence", payload["nodes"][0]["missing_fields"])

    def test_c_grade_is_watch_only(self) -> None:
        row = self.complete_row()
        row["severity"] = "watch"
        row["evidence_grade"] = "C"
        code, payload = self.run_row(row)
        self.assertEqual(code, 0)
        self.assertEqual(payload["nodes"][0]["review_status"], "watch_only")

    def test_missing_counterevidence_record_fails(self) -> None:
        row = self.complete_row()
        row["counterevidence"] = ""
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        self.assertIn("counterevidence", payload["nodes"][0]["missing_fields"])

    def test_bare_na_does_not_satisfy_counterevidence_gate(self) -> None:
        row = self.complete_row()
        row["counterevidence"] = "N/A"
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        self.assertIn("counterevidence", payload["nodes"][0]["missing_fields"])

    def test_placeholder_states_cannot_fake_a_complete_packet(self) -> None:
        for placeholder in ["blocked", "pending", "TODO", "TBD", "-", "evidence_absent"]:
            with self.subTest(placeholder=placeholder):
                row = self.complete_row()
                for field in row:
                    if field != "evidence_grade":
                        row[field] = placeholder
                code, payload = self.run_row(row)
                self.assertEqual(code, 1)
                self.assertEqual(payload["nodes"][0]["review_status"], "incomplete")
                self.assertIn("supply_gap_evidence", payload["nodes"][0]["missing_fields"])

    def test_soft_packet_cannot_be_relabelled_hard(self) -> None:
        soft_row = self.complete_row()
        code, payload = self.run_row(soft_row)
        self.assertEqual(code, 0)
        self.assertEqual(
            payload["nodes"][0]["review_status"], "eligible_for_bottleneck_review"
        )

        hard_row = self.complete_row()
        hard_row["severity"] = "hard_bottleneck"
        code, payload = self.run_row(hard_row)
        self.assertEqual(code, 1)
        node = payload["nodes"][0]
        self.assertEqual(node["review_status"], "ineligible_for_claimed_severity")
        self.assertIn("A-grade", "\n".join(node["consistency_issues"]))

    def test_hard_bottleneck_requires_current_closed_loop_and_no_certified_alternative(self) -> None:
        row = self.complete_row()
        row.update(
            {
                "severity": "hard_bottleneck",
                "evidence_grade": "A",
                "claim_window": "future",
                "demand_evidence_kind": "qualitative_signal",
                "supply_evidence_kind": "qualitative_constraint",
                "second_source_status": "qualified",
            }
        )
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        issues = "\n".join(payload["nodes"][0]["consistency_issues"])
        self.assertIn("current claim_window", issues)
        self.assertIn("quantified demand or a demand step", issues)
        self.assertIn("qualified/usable supply, yield, delivery, or certified-supplier limit", issues)
        self.assertIn("certified alternative", issues)

        valid_hard = self.complete_row()
        valid_hard.update({"severity": "hard_bottleneck", "evidence_grade": "A"})
        code, payload = self.run_row(valid_hard)
        self.assertEqual(code, 0)
        self.assertEqual(
            payload["nodes"][0]["review_status"], "eligible_for_bottleneck_review"
        )
        self.assertEqual(payload["nodes"][0]["freshness_status"], "fresh")

    def test_stale_2021_evidence_cannot_support_current_hard_or_soft(self) -> None:
        for severity, grade in (("hard_bottleneck", "A"), ("soft_bottleneck", "B")):
            with self.subTest(severity=severity):
                row = self.complete_row()
                row.update({"severity": severity, "evidence_grade": grade})
                for field in (
                    "demand_evidence_date",
                    "supply_evidence_date",
                    "gap_evidence_date",
                    "source_date",
                ):
                    row[field] = "2021-01-01"
                code, payload = self.run_row(row)
                self.assertEqual(code, 1)
                node = payload["nodes"][0]
                self.assertEqual(node["freshness_status"], "stale")
                self.assertEqual(node["review_status"], "ineligible_for_claimed_severity")
                self.assertIn("within 180 days", "\n".join(node["consistency_issues"]))

    def test_stale_evidence_remains_usable_only_as_watch_or_historical(self) -> None:
        row = self.complete_row()
        for field in (
            "demand_evidence_date",
            "supply_evidence_date",
            "gap_evidence_date",
            "source_date",
        ):
            row[field] = "2021-01-01"

        watch = dict(row, severity="watch", evidence_grade="C")
        code, payload = self.run_row(watch)
        self.assertEqual(code, 0)
        self.assertEqual(payload["nodes"][0]["review_status"], "watch_only")
        self.assertEqual(payload["nodes"][0]["freshness_status"], "stale")

        historical = dict(row, claim_window="historical")
        code, payload = self.run_row(historical)
        self.assertEqual(code, 0)
        self.assertEqual(
            payload["nodes"][0]["review_status"], "eligible_for_bottleneck_review"
        )
        self.assertEqual(payload["nodes"][0]["freshness_status"], "stale")

    def test_invalid_iso_date_and_excessive_override_are_ineligible(self) -> None:
        row = self.complete_row()
        row["demand_evidence_date"] = "2026-02-30"
        row["max_age_days"] = "366"
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        node = payload["nodes"][0]
        self.assertEqual(node["freshness_status"], "invalid")
        issues = "\n".join(node["consistency_issues"])
        self.assertIn("invalid ISO date/timestamp for demand_evidence_date", issues)
        self.assertIn("between 1 and 365", issues)

    def test_fresh_anonymous_self_graded_a_cannot_support_hard_bottleneck(self) -> None:
        row = self.complete_row()
        row.update({"severity": "hard_bottleneck", "evidence_grade": "A"})
        for leg in ("demand", "supply", "gap"):
            row[f"{leg}_source_type"] = "anonymous"
            row[f"{leg}_source_locator"] = "https://example.com/anonymous-post"
        row["source"] = "anonymous social post"
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        node = payload["nodes"][0]
        self.assertEqual(node["review_status"], "ineligible_for_claimed_severity")
        issues = "\n".join(node["consistency_issues"])
        self.assertIn("requires regulatory/official", issues)
        self.assertIn("watch-only", issues)

    def test_credible_third_party_is_soft_only_not_hard(self) -> None:
        row = self.complete_row()
        for leg in ("demand", "supply", "gap"):
            row[f"{leg}_source_type"] = "credible_third_party"
        code, payload = self.run_row(row)
        self.assertEqual(code, 0)
        self.assertEqual(
            payload["nodes"][0]["review_status"], "eligible_for_bottleneck_review"
        )

        row.update({"severity": "hard_bottleneck", "evidence_grade": "A"})
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        self.assertIn(
            "requires regulatory/official",
            "\n".join(payload["nodes"][0]["consistency_issues"]),
        )

    def test_custom_max_age_days_is_enforced(self) -> None:
        row = self.complete_row()
        row["max_age_days"] = "5"
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        node = payload["nodes"][0]
        self.assertEqual(node["max_age_days"], 5)
        self.assertEqual(node["freshness_status"], "stale")

    def test_future_claim_packet_cannot_cross_explicit_as_of(self) -> None:
        row = self.complete_row()
        row["claim_as_of"] = "2099-01-02"
        for field in (
            "demand_evidence_date",
            "supply_evidence_date",
            "gap_evidence_date",
            "source_date",
        ):
            row[field] = "2099-01-01"
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        node = payload["nodes"][0]
        self.assertEqual(node["freshness_status"], "invalid")
        self.assertIn("cannot be after as_of", "\n".join(node["consistency_issues"]))

    def test_invalid_severity_is_ineligible(self) -> None:
        row = self.complete_row()
        row["severity"] = "critical_bottleneck"
        code, payload = self.run_row(row)
        self.assertEqual(code, 1)
        self.assertEqual(
            payload["nodes"][0]["review_status"], "ineligible_for_claimed_severity"
        )
        self.assertIn("invalid severity", payload["nodes"][0]["consistency_issues"][0])

    def test_empty_packet_is_schema_error(self) -> None:
        fields = [
            "check_id", "node", "severity", "claim_window", "claim_as_of", "max_age_days",
            "demand_evidence_kind", "supply_evidence_kind", "demand_evidence",
            "demand_evidence_date", "demand_source_type", "demand_source_locator",
            "supply_evidence", "supply_evidence_date", "supply_source_type",
            "supply_source_locator", "supply_gap_evidence", "gap_evidence_date",
            "gap_source_type", "gap_source_locator", "direct_gap_consequence",
            "constraint_mechanism", "time_horizon", "evidence_grade", "source",
            "source_date", "counterevidence",
            "substitution_path", "second_source_status", "relief_window",
            "positive_validation", "key_reversal",
        ]
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", encoding="utf-8", newline="", delete=False
        )
        with handle:
            csv.DictWriter(handle, fieldnames=fields).writeheader()
        path = Path(handle.name)
        self.addCleanup(path.unlink, missing_ok=True)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--csv",
                str(path),
                "--as-of",
                "2026-07-27",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("at least one evidence row", proc.stdout)


if __name__ == "__main__":
    unittest.main()
