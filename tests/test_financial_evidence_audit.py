from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / ".agents"
    / "skills"
    / "financial-evidence-audit"
    / "scripts"
    / "financial_evidence_audit.py"
)


def instant(as_of: str) -> dict:
    return {"kind": "instant", "as_of": as_of}


def duration(start: str, end: str, frequency: str, label: str) -> dict:
    return {
        "kind": "duration",
        "start": start,
        "end": end,
        "frequency": frequency,
        "label": label,
    }


def estimate(expectation_as_of: str, label: str = "FY2026E") -> dict:
    return {
        "kind": "estimate",
        "expectation_as_of": expectation_as_of,
        "target_start": "2026-01-01",
        "target_end": "2026-12-31",
        "frequency": "year",
        "label": label,
    }


def source(
    source_id: str,
    source_type: str,
    origin_id: str,
    *,
    status: str = "accepted",
    source_date: str = "2026-07-20",
) -> dict:
    result = {
        "id": source_id,
        "source_type": source_type,
        "origin_id": origin_id,
        "locator": f"https://example.com/{source_id}",
        "source_date": source_date,
        "checked_at": "2026-07-27T15:00:00+08:00",
        "status": status,
    }
    if status == "excluded":
        result.update(
            {
                "exclusion_code": "wrong_period",
                "exclusion_reason": "The value is from a different fiscal period.",
            }
        )
    return result


def fact(
    fact_id: str,
    metric: str,
    value: str | None,
    unit: str,
    currency: str | None,
    period: dict,
    basis: str,
    source_refs: list[str],
    *,
    scale: str = "1",
    missing_reason: str | None = None,
    available_at: str | None = None,
) -> dict:
    result = {
        "id": fact_id,
        "metric": metric,
        "value": value,
        "unit": unit,
        "currency": currency,
        "scale": scale,
        "period": period,
        "basis": basis,
        "source_refs": source_refs,
    }
    if period.get("kind") == "duration":
        result["available_at"] = available_at or period["end"]
    elif available_at is not None:
        result["available_at"] = available_at
    if value is None:
        result["missing_reason"] = missing_reason or "source_gap"
    return result


def gate(
    minimum: int = 1,
    counted: str = "official",
    anchor: str = "official",
) -> dict:
    return {
        "min_independent_origins": minimum,
        "counted_tier": counted,
        "required_anchor_tier": anchor,
    }


def value_ref(fact_id: str) -> dict:
    return {"fact_id": fact_id}


def check_ref(check_id: str, output: str) -> dict:
    return {"check_id": check_id, "output": output}


class FinancialEvidenceAuditTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, dict]:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        self.assertTrue(process.stdout, msg=process.stderr)
        try:
            payload = json.loads(process.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic on regression
            self.fail(f"stdout is not JSON: {process.stdout}\nstderr: {process.stderr}\n{exc}")
        return process.returncode, payload

    def write_payload(self, payload: dict, *, allow_nan: bool = True) -> Path:
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        )
        with handle:
            json.dump(payload, handle, ensure_ascii=False, allow_nan=allow_nan)
        path = Path(handle.name)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def audit(self, payload: dict) -> tuple[int, dict]:
        return self.run_cli("audit", "--input", str(self.write_payload(payload)))

    def valid_cross_source_payload(self) -> dict:
        annual = duration("2025-01-01", "2025-12-31", "year", "FY2025")
        return {
            "schema_version": "1.0",
            "audit_id": "cross-source-pass",
            "as_of": "2026-07-27T15:00:00+08:00",
            "sources": [
                source("S_REPORT", "report_under_audit", "report:draft"),
                source("S_OFFICIAL", "official_filing", "issuer:FY2025:annual-report"),
            ],
            "facts": [
                fact(
                    "F_REPORT",
                    "revenue",
                    "100",
                    "currency",
                    "CNY",
                    annual,
                    "reported_consolidated_prc_gaap",
                    ["S_REPORT"],
                ),
                fact(
                    "F_OFFICIAL",
                    "revenue",
                    "100",
                    "currency",
                    "CNY",
                    annual,
                    "reported_consolidated_prc_gaap",
                    ["S_OFFICIAL"],
                ),
            ],
            "checks": [
                {
                    "id": "C_REVENUE",
                    "kind": "cross_source",
                    "materiality": "material",
                    "target": value_ref("F_REPORT"),
                    "references": [value_ref("F_OFFICIAL")],
                    "source_gate": gate(),
                    "tolerance": {"relative_pct": "0", "absolute_base": "0"},
                }
            ],
        }

    def market_cap_payload(self) -> dict:
        price_time = "2026-07-27T15:00:00+08:00"
        return {
            "schema_version": "1.0",
            "audit_id": "market-cap",
            "as_of": price_time,
            "sources": [
                source(
                    "S_PRICE",
                    "market_data_vendor",
                    "vendor:close:20260727",
                    source_date="2026-07-27",
                ),
                source("S_SHARES", "official_filing", "issuer:shares:20260630"),
                source(
                    "S_CAP",
                    "market_data_vendor",
                    "vendor:market-cap:20260727",
                    source_date="2026-07-27",
                ),
            ],
            "facts": [
                fact(
                    "F_PRICE",
                    "close_price",
                    "10.25",
                    "currency_per_share",
                    "CNY",
                    instant(price_time),
                    "unadjusted_close",
                    ["S_PRICE"],
                ),
                fact(
                    "F_SHARES",
                    "total_shares",
                    "100000000",
                    "share",
                    None,
                    instant("2026-06-30T23:59:59+08:00"),
                    "total_shares_outstanding",
                    ["S_SHARES"],
                ),
                fact(
                    "F_CAP",
                    "total_market_cap",
                    "1025000000",
                    "currency",
                    "CNY",
                    instant(price_time),
                    "total_market_cap",
                    ["S_CAP"],
                ),
            ],
            "checks": [
                {
                    "id": "C_MARKET_CAP",
                    "kind": "market_cap",
                    "materiality": "material",
                    "price": value_ref("F_PRICE"),
                    "shares": value_ref("F_SHARES"),
                    "expected": value_ref("F_CAP"),
                    "capitalization_basis": "total",
                    "max_share_age_days": 30,
                    "source_gate": gate(2, "vendor_or_official", "vendor_or_official"),
                    "tolerance": {"relative_pct": "0", "absolute_base": "0"},
                }
            ],
        }

    def derived_pe_payload(self) -> dict:
        event_at = "2026-07-25T18:00:00+08:00"
        quarter = duration("2026-04-01", "2026-06-30", "quarter", "Q2 FY2026")
        payload = {
            "schema_version": "1.0",
            "audit_id": "derived-pe",
            "as_of": "2026-07-27T15:00:00+08:00",
            "sources": [
                source(
                    "S_PRICE",
                    "market_data_vendor",
                    "vendor:price:20260725",
                    source_date="2026-07-25",
                ),
                source("S_SHARES", "official_filing", "issuer:shares:20260630"),
                source(
                    "S_QUARTER",
                    "official_filing",
                    "issuer:q2:2026",
                    source_date="2026-07-25",
                ),
                source("S_CONSENSUS", "market_data_vendor", "vendor:consensus:20260720"),
            ],
            "facts": [
                fact(
                    "F_PRICE",
                    "close_price",
                    "5",
                    "currency_per_share",
                    "CNY",
                    instant("2026-07-25T15:00:00+08:00"),
                    "unadjusted_close",
                    ["S_PRICE"],
                ),
                fact(
                    "F_SHARES",
                    "total_shares",
                    "100",
                    "share",
                    None,
                    instant("2026-06-30T23:59:59+08:00"),
                    "total_shares_outstanding",
                    ["S_SHARES"],
                ),
                fact(
                    "F_Q_LOW",
                    "deducted_attributable_net_profit",
                    "20",
                    "currency",
                    "CNY",
                    quarter,
                    "actual_quarterly_deducted_attributable_net_profit_prc_gaap",
                    ["S_QUARTER"],
                    available_at=event_at,
                ),
                fact(
                    "F_Q_HIGH",
                    "deducted_attributable_net_profit",
                    "25",
                    "currency",
                    "CNY",
                    quarter,
                    "actual_quarterly_deducted_attributable_net_profit_prc_gaap",
                    ["S_QUARTER"],
                    available_at=event_at,
                ),
                fact(
                    "F_CONSENSUS",
                    "fy_attributable_net_profit",
                    "90",
                    "currency",
                    "CNY",
                    estimate("2026-07-20"),
                    "pre_event_fy_attributable_net_profit_consensus_prc_gaap",
                    ["S_CONSENSUS"],
                ),
            ],
            "checks": [
                {
                    "id": "C_MARKET_CAP",
                    "kind": "market_cap",
                    "materiality": "material",
                    "price": value_ref("F_PRICE"),
                    "shares": value_ref("F_SHARES"),
                    "capitalization_basis": "total",
                    "max_share_age_days": 30,
                    "source_gate": gate(2, "vendor_or_official", "vendor_or_official"),
                },
                {
                    "id": "C_EXPECTATION",
                    "kind": "expectation_gap",
                    "materiality": "material",
                    "quarterly_low": value_ref("F_Q_LOW"),
                    "quarterly_high": value_ref("F_Q_HIGH"),
                    "consensus": value_ref("F_CONSENSUS"),
                    "annualization_factor": "4",
                    "event_at": event_at,
                    "comparison_basis": "annualized_quarterly_deducted_vs_fy_attributable_consensus",
                    "company_metric": "deducted_attributable_net_profit",
                    "consensus_metric": "fy_attributable_net_profit",
                    "source_gate": gate(2, "vendor_or_official", "official"),
                },
                {
                    "id": "C_PE",
                    "kind": "valuation",
                    "materiality": "material",
                    "metric": "pe_user_defined",
                    "numerator": check_ref("C_MARKET_CAP", "value"),
                    "denominator_low": check_ref("C_EXPECTATION", "annualized_low"),
                    "denominator_high": check_ref("C_EXPECTATION", "annualized_high"),
                    "valuation_basis": "latest_single_quarter_deducted_attributable_net_profit_x4",
                    "source_gate": gate(3, "vendor_or_official", "official"),
                },
            ],
        }
        return payload

    def surprise_payload(
        self,
        *,
        metric: str = "revenue",
        actual_low: str = "105",
        actual_high: str = "105",
        consensus: str = "100",
        basis: str = "us_gaap_reported",
        expected_percentage: str | None = None,
    ) -> dict:
        event_at = "2026-07-25T16:00:00-04:00"
        quarter = duration("2026-04-01", "2026-06-30", "quarter", "Q2 2026")
        consensus_period = {
            "kind": "estimate",
            "expectation_as_of": "2026-07-20",
            "target_start": "2026-04-01",
            "target_end": "2026-06-30",
            "frequency": "quarter",
            "label": "Q2 2026E",
        }
        unit = (
            "currency_per_share"
            if metric
            in {
                "eps",
                "earnings_per_share",
                "basic_eps",
                "diluted_eps",
                "gaap_eps",
                "adjusted_eps",
                "non_gaap_eps",
            }
            else "currency"
        )
        payload = {
            "schema_version": "1.0",
            "audit_id": f"surprise-{metric}",
            "as_of": "2026-07-27T15:00:00-04:00",
            "sources": [
                source(
                    "S_ACTUAL",
                    "company_ir",
                    "issuer:q2-2026-release",
                    source_date="2026-07-25",
                ),
                source(
                    "S_CONSENSUS",
                    "market_data_vendor",
                    "vendor:q2-2026-consensus",
                    source_date="2026-07-20",
                ),
            ],
            "facts": [
                fact(
                    "F_ACTUAL_LOW",
                    metric,
                    actual_low,
                    unit,
                    "USD",
                    quarter,
                    basis,
                    ["S_ACTUAL"],
                    available_at=event_at,
                ),
                fact(
                    "F_ACTUAL_HIGH",
                    metric,
                    actual_high,
                    unit,
                    "USD",
                    quarter,
                    basis,
                    ["S_ACTUAL"],
                    available_at=event_at,
                ),
                fact(
                    "F_CONSENSUS",
                    metric,
                    consensus,
                    unit,
                    "USD",
                    consensus_period,
                    basis,
                    ["S_CONSENSUS"],
                ),
            ],
            "checks": [
                {
                    "id": "C_SURPRISE",
                    "kind": "expectation_surprise",
                    "materiality": "material",
                    "subject_kind": "reported_actual",
                    "actual_low": value_ref("F_ACTUAL_LOW"),
                    "actual_high": value_ref("F_ACTUAL_HIGH"),
                    "consensus": value_ref("F_CONSENSUS"),
                    "event_at": event_at,
                    "tolerance": {"relative_pct": "0", "absolute_base": "0"},
                    "source_gate": gate(
                        2, "vendor_or_official", "official"
                    ),
                }
            ],
        }
        if expected_percentage is not None:
            payload["sources"].append(
                source(
                    "S_REPORT",
                    "report_under_audit",
                    "report:surprise-claim",
                    source_date="2026-07-27",
                )
            )
            output_basis = f"{basis}_vs_pre_event_consensus"
            for suffix in ("LOW", "HIGH"):
                payload["facts"].append(
                    fact(
                        f"F_EXPECTED_{suffix}",
                        f"{metric}_surprise_pct",
                        expected_percentage,
                        "percent",
                        None,
                        quarter,
                        output_basis,
                        ["S_REPORT"],
                        available_at="2026-07-27",
                    )
                )
            payload["checks"][0].update(
                {
                    "expected_low": value_ref("F_EXPECTED_LOW"),
                    "expected_high": value_ref("F_EXPECTED_HIGH"),
                    "expected_kind": "percentage",
                    "claim_tolerance": {
                        "relative_pct": "0",
                        "absolute_base": "0",
                    },
                }
            )
        return payload

    def guidance_surprise_payload(
        self,
        *,
        metric: str = "revenue",
        guidance_low: str = "110",
        guidance_high: str = "120",
        consensus: str = "105",
        basis: str = "us_gaap_guidance",
    ) -> dict:
        event_at = "2026-07-25T16:00:00-04:00"
        target = {
            "kind": "estimate",
            "expectation_as_of": event_at,
            "target_start": "2026-07-01",
            "target_end": "2026-09-30",
            "frequency": "quarter",
            "label": "Q3 2026 guidance",
        }
        consensus_period = copy.deepcopy(target)
        consensus_period["expectation_as_of"] = "2026-07-20"
        consensus_period["label"] = "Q3 2026E"
        unit = "currency_per_share" if "eps" in metric else "currency"
        return {
            "schema_version": "1.0",
            "audit_id": f"guidance-surprise-{metric}",
            "as_of": "2026-07-27T15:00:00-04:00",
            "sources": [
                source(
                    "S_GUIDANCE",
                    "company_ir",
                    "issuer:q3-2026-guidance",
                    source_date="2026-07-25",
                ),
                source(
                    "S_CONSENSUS",
                    "market_data_vendor",
                    "vendor:q3-2026-consensus",
                    source_date="2026-07-20",
                ),
            ],
            "facts": [
                fact(
                    "F_GUIDANCE_LOW",
                    metric,
                    guidance_low,
                    unit,
                    "USD",
                    target,
                    basis,
                    ["S_GUIDANCE"],
                ),
                fact(
                    "F_GUIDANCE_HIGH",
                    metric,
                    guidance_high,
                    unit,
                    "USD",
                    target,
                    basis,
                    ["S_GUIDANCE"],
                ),
                fact(
                    "F_CONSENSUS",
                    metric,
                    consensus,
                    unit,
                    "USD",
                    consensus_period,
                    basis,
                    ["S_CONSENSUS"],
                ),
            ],
            "checks": [
                {
                    "id": "C_GUIDANCE_SURPRISE",
                    "kind": "expectation_surprise",
                    "materiality": "material",
                    "subject_kind": "company_guidance",
                    "guidance_low": value_ref("F_GUIDANCE_LOW"),
                    "guidance_high": value_ref("F_GUIDANCE_HIGH"),
                    "consensus": value_ref("F_CONSENSUS"),
                    "event_at": event_at,
                    "tolerance": {"relative_pct": "0", "absolute_base": "0"},
                    "source_gate": gate(2, "vendor_or_official", "official"),
                }
            ],
        }

    def test_calc_is_decimal_only_and_reports_rounding(self) -> None:
        code, payload = self.run_cli("calc", "--expr", "0.1 + 0.2")
        self.assertEqual(code, 0)
        self.assertEqual(payload["result"], "0.3")
        self.assertFalse(payload["rounded"])

        code, payload = self.run_cli("calc", "--expr", "1 / 3")
        self.assertEqual(code, 0)
        self.assertTrue(payload["rounded"])
        self.assertEqual(payload["precision"], 50)

    def test_calc_preserves_scientific_and_fifty_digit_values(self) -> None:
        code, payload = self.run_cli("calc", "--expr", "510 * 9.11e9")
        self.assertEqual(code, 0)
        self.assertEqual(payload["result"], "4646100000000")

        long_value = "1.1234567890123456789012345678901234567890123456789"
        code, payload = self.run_cli("calc", "--expr", f"{long_value} + 0")
        self.assertEqual(code, 0)
        self.assertEqual(payload["result"], long_value)

    def test_calc_rejects_calls_division_by_zero_and_overflow(self) -> None:
        for expression in ("sum([1, 2])", "1 / 0", "1e10000 * 1e10000"):
            with self.subTest(expression=expression):
                code, payload = self.run_cli("calc", "--expr", expression)
                self.assertEqual(code, 2)
                self.assertEqual(payload["verdict"], "ERROR")
                self.assertEqual(payload["release_status"], "invalid_input")

    def test_valid_cross_source_audit_is_publishable(self) -> None:
        code, payload = self.audit(self.valid_cross_source_payload())
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["release_status"], "publishable")
        self.assertEqual(payload["summary"]["verified_count"], 1)
        self.assertEqual(len(payload["input_sha256"]), 64)

    def test_audit_fact_scaling_preserves_fifty_digit_decimal(self) -> None:
        payload = self.valid_cross_source_payload()
        long_value = "1.1234567890123456789012345678901234567890123456789"
        payload["facts"][0]["value"] = long_value
        payload["facts"][1]["value"] = long_value
        code, result = self.audit(payload)
        self.assertEqual(code, 0)
        self.assertEqual(
            result["checks"][0]["outputs"]["value"]["value"], long_value
        )

    def test_fact_scaling_rejects_rounded_or_inexact_51_to_200_digit_inputs(self) -> None:
        for digits in (51, 200):
            with self.subTest(digits=digits):
                payload = self.valid_cross_source_payload()
                value = "1" * digits
                payload["facts"][0]["value"] = value
                payload["facts"][1]["value"] = value
                code, result = self.audit(payload)
                self.assertEqual(code, 2)
                self.assertEqual(result["code"], "DECIMAL_PRECISION_LOSS")

    def test_empty_checks_fail_with_zero_verified(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["checks"] = []
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(result["release_status"], "blocked")
        self.assertEqual(result["global_issues"][0]["code"], "NO_VERIFIED_CHECKS")

    def test_lead_only_never_counts_as_an_independent_source(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["sources"].append(source("S_LEAD", "lead_only", "social:post:1"))
        payload["facts"].append(
            copy.deepcopy(payload["facts"][1])
            | {"id": "F_LEAD", "source_refs": ["S_LEAD"]}
        )
        check = payload["checks"][0]
        check["references"].append(value_ref("F_LEAD"))
        check["source_gate"] = gate(2, "any_credible", "official")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(
            result["checks"][0]["source_gate"]["independent_origin_count"], 1
        )

    def test_two_urls_with_one_origin_count_once(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["sources"].append(
            source("S_COPY", "official_filing", "issuer:FY2025:annual-report")
        )
        payload["facts"].append(
            copy.deepcopy(payload["facts"][1])
            | {"id": "F_COPY", "source_refs": ["S_COPY"]}
        )
        check = payload["checks"][0]
        check["references"].append(value_ref("F_COPY"))
        check["source_gate"] = gate(2)
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(
            result["checks"][0]["source_gate"]["independent_origin_count"], 1
        )

    def test_pairwise_source_conflict_cannot_hide_around_target(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["facts"][1]["value"] = "99.1"
        payload["sources"].append(
            source("S_SECOND", "official_filing", "auditor:FY2025:confirmation")
        )
        payload["facts"].append(
            copy.deepcopy(payload["facts"][1])
            | {"id": "F_SECOND", "value": "100.9", "source_refs": ["S_SECOND"]}
        )
        check = payload["checks"][0]
        check["references"].append(value_ref("F_SECOND"))
        check["source_gate"] = gate(2)
        check["tolerance"] = {"relative_pct": "1", "absolute_base": "0"}
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        codes = {issue["code"] for issue in result["checks"][0]["issues"]}
        self.assertIn("MATERIAL_CONFLICT", codes)

    def test_currency_unit_period_and_basis_mismatches_fail_closed(self) -> None:
        mutations = {
            "currency": "USD",
            "unit": "currency_per_share",
            "period": duration("2024-01-01", "2024-12-31", "year", "FY2024"),
            "basis": "adjusted_non_gaap",
        }
        expected_codes = {
            "currency": "CURRENCY_MISMATCH",
            "unit": "UNIT_MISMATCH",
            "period": "PERIOD_MISMATCH",
            "basis": "BASIS_MISMATCH",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                payload = self.valid_cross_source_payload()
                payload["facts"][1][field] = value
                if field == "unit":
                    payload["facts"][1]["currency"] = "CNY"
                code, result = self.audit(payload)
                self.assertEqual(code, 1)
                codes = {issue["code"] for issue in result["checks"][0]["issues"]}
                self.assertIn(expected_codes[field], codes)

    def test_cross_source_and_percentage_change_require_matching_metrics(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["facts"][1]["metric"] = "net_profit"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "METRIC_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.percentage_payload(expected=False)
        payload["facts"][1]["metric"] = "net_profit"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "METRIC_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_market_cap_calculation_and_scale_are_verified(self) -> None:
        payload = self.market_cap_payload()
        payload["facts"][1]["value"] = "10000"
        payload["facts"][1]["scale"] = "10000"
        code, result = self.audit(payload)
        self.assertEqual(code, 0)
        self.assertEqual(
            result["checks"][0]["outputs"]["value"]["value"], "1025000000"
        )

    def test_market_cap_mismatch_and_stale_shares_are_blocked(self) -> None:
        payload = self.market_cap_payload()
        payload["facts"][2]["value"] = "900000000"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(result["release_status"], "blocked")

        payload = self.market_cap_payload()
        payload["checks"][0]["max_share_age_days"] = 1
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        codes = {issue["code"] for issue in result["checks"][0]["issues"]}
        self.assertIn("PERIOD_MISMATCH", codes)

    def test_market_cap_requires_legal_metric_and_basis_contract(self) -> None:
        mutations = (
            (0, "metric", "eps", "METRIC_MISMATCH"),
            (0, "basis", "ttm_eps", "BASIS_MISMATCH"),
            (0, "basis", "adjusted_close", "BASIS_MISMATCH"),
            (1, "metric", "revenue", "METRIC_MISMATCH"),
            (2, "metric", "enterprise_value", "METRIC_MISMATCH"),
        )
        for fact_index, field, value, expected_code in mutations:
            with self.subTest(fact_index=fact_index, field=field):
                payload = self.market_cap_payload()
                payload["facts"][fact_index][field] = value
                code, result = self.audit(payload)
                self.assertEqual(code, 1)
                codes = {issue["code"] for issue in result["checks"][0]["issues"]}
                self.assertIn(expected_code, codes)

    def test_market_cap_price_cannot_piggyback_on_official_shares(self) -> None:
        payload = self.market_cap_payload()
        payload["sources"][0]["source_type"] = "lead_only"
        payload["checks"][0]["source_gate"] = gate(1, "official", "official")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        check = result["checks"][0]
        self.assertEqual(check["source_gate"]["independent_origin_count"], 1)
        self.assertIn(
            "UNTRUSTED_RECORD_SOURCE",
            {issue["code"] for issue in check["issues"]},
        )

    def test_fact_source_date_must_bind_to_information_available_time(self) -> None:
        payload = self.market_cap_payload()
        for item in payload["sources"]:
            item["source_date"] = "2020-01-01"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        stale_refs = {
            ref
            for issue in result["checks"][0]["issues"]
            if issue["code"] == "STALE_RECORD_SOURCE"
            for ref in issue["refs"]
        }
        self.assertEqual(stale_refs, {"S_PRICE", "S_SHARES", "S_CAP"})

        payload = self.market_cap_payload()
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)

        payload = self.derived_pe_payload()
        payload["sources"][3]["source_date"] = "2020-01-01"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "STALE_RECORD_SOURCE",
            {issue["code"] for issue in result["checks"][1]["issues"]},
        )

    def test_each_check_input_must_have_its_own_credible_source(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["sources"].append(source("S_LEAD", "lead_only", "social:revenue"))
        payload["facts"].append(
            copy.deepcopy(payload["facts"][1])
            | {"id": "F_LEAD", "source_refs": ["S_LEAD"]}
        )
        payload["checks"][0]["references"].append(value_ref("F_LEAD"))
        payload["checks"][0]["source_gate"] = gate(1, "official", "official")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "UNTRUSTED_RECORD_SOURCE",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_report_under_audit_expected_claim_is_comparable_but_not_a_gate_origin(self) -> None:
        payload = self.market_cap_payload()
        payload["sources"][2]["source_type"] = "report_under_audit"
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(
            result["checks"][0]["source_gate"]["independent_origin_count"], 2
        )
        payload["facts"][2]["value"] = "900000000"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "MATERIAL_CONFLICT",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.generic_valuation_payload("pe")
        payload["sources"].append(
            source(
                "S_REPORT",
                "report_under_audit",
                "report:valuation",
                source_date="2026-07-27",
            )
        )
        price_period = payload["facts"][0]["period"]
        payload["facts"].extend(
            [
                fact(
                    "F_EXPECTED_LOW",
                    "pe",
                    "20",
                    "multiple",
                    None,
                    price_period,
                    "ttm_net_profit",
                    ["S_REPORT"],
                ),
                fact(
                    "F_EXPECTED_HIGH",
                    "pe",
                    "20",
                    "multiple",
                    None,
                    price_period,
                    "ttm_net_profit",
                    ["S_REPORT"],
                ),
            ]
        )
        payload["checks"][0].update(
            {
                "expected_low": value_ref("F_EXPECTED_LOW"),
                "expected_high": value_ref("F_EXPECTED_HIGH"),
                "tolerance": {"relative_pct": "0", "absolute_base": "0"},
            }
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        payload["facts"][2]["value"] = "19"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)

        payload = self.percentage_payload(expected=True)
        payload["sources"].append(
            source("S_REPORT", "report_under_audit", "report:percentage")
        )
        payload["facts"][2]["source_refs"] = ["S_REPORT"]
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        payload["facts"][2]["value"] = "9"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)

        payload = self.derived_pe_payload()
        payload["sources"][2]["source_type"] = "credible_secondary"
        payload["sources"][3]["source_type"] = "official_filing"
        payload["checks"][1]["source_gate"] = gate(1, "any_credible", "official")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "UNTRUSTED_RECORD_SOURCE",
            {issue["code"] for issue in result["checks"][1]["issues"]},
        )

        payload = self.generic_valuation_payload("pe")
        payload["sources"].append(source("S_LEAD", "lead_only", "social:valuation"))
        payload["facts"][0]["source_refs"] = ["S_LEAD"]
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "UNTRUSTED_RECORD_SOURCE",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.percentage_payload(expected=False)
        payload["sources"].append(source("S_LEAD", "lead_only", "social:percentage"))
        payload["facts"][0]["source_refs"] = ["S_LEAD"]
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "UNTRUSTED_RECORD_SOURCE",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_derived_expectation_and_pe_chain_preserves_provenance(self) -> None:
        code, result = self.audit(self.derived_pe_payload())
        self.assertEqual(code, 0)
        expectation = result["checks"][1]
        pe = result["checks"][2]
        self.assertEqual(expectation["details"]["annualized_core_gap_status"], "straddles")
        self.assertEqual(expectation["details"]["formal_surprise_status"], "N/A")
        self.assertEqual(pe["outputs"]["low"]["value"], "5")
        self.assertEqual(pe["outputs"]["high"]["value"], "6.25")
        self.assertEqual(
            set(pe["outputs"]["low"]["source_ids"]),
            {"S_PRICE", "S_SHARES", "S_QUARTER", "S_CONSENSUS"},
        )

    def test_expectation_surprise_supports_us_revenue_and_eps(self) -> None:
        code, result = self.audit(self.surprise_payload())
        self.assertEqual(code, 0, result)
        check = result["checks"][0]
        self.assertEqual(check["state"], "beat")
        self.assertEqual(check["outputs"]["absolute_low"]["value"], "5")
        self.assertEqual(check["outputs"]["percentage_low"]["value"], "5")

        payload = self.surprise_payload(
            metric="adjusted_eps",
            actual_low="0.90",
            actual_high="0.90",
            consensus="1.00",
            basis="us_non_gaap_adjusted",
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["state"], "miss")
        self.assertEqual(
            result["checks"][0]["outputs"]["percentage_low"]["value"], "-10"
        )

        payload = self.surprise_payload(
            actual_low="100.5", actual_high="100.5", consensus="100"
        )
        payload["checks"][0]["tolerance"] = {
            "relative_pct": "1",
            "absolute_base": "0",
        }
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["state"], "meet")

    def test_reported_actual_information_time_must_equal_event(self) -> None:
        payload = self.surprise_payload()
        event_at = payload["checks"][0]["event_at"]
        self.assertEqual(payload["facts"][0]["available_at"], event_at)
        self.assertEqual(payload["facts"][1]["available_at"], event_at)
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)

        payload = self.surprise_payload()
        payload["sources"][0]["source_date"] = "2026-07-20"
        payload["sources"][1]["source_date"] = "2026-07-22"
        for index in (0, 1):
            payload["facts"][index]["available_at"] = (
                "2026-07-20T16:00:00-04:00"
            )
        payload["facts"][2]["period"]["expectation_as_of"] = "2026-07-22"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "ACTUAL_INFORMATION_NOT_AT_EVENT",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_expectation_surprise_supports_revenue_and_eps_guidance_ranges(self) -> None:
        code, result = self.audit(self.guidance_surprise_payload())
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["state"], "beat")

        payload = self.guidance_surprise_payload(
            metric="adjusted_eps",
            guidance_low="0.95",
            guidance_high="1.05",
            consensus="1.00",
            basis="us_non_gaap_guidance",
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["state"], "straddles")

    def test_guidance_surprise_enforces_pit_source_target_and_basis(self) -> None:
        payload = self.guidance_surprise_payload()
        payload["sources"][1]["source_date"] = "2026-07-26"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "EXPECTATION_SOURCE_NOT_POINT_IN_TIME",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.guidance_surprise_payload()
        payload["sources"][0]["source_type"] = "credible_secondary"
        payload["checks"][0]["source_gate"] = gate(1, "any_credible", "none")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "UNTRUSTED_RECORD_SOURCE",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.guidance_surprise_payload()
        payload["facts"][2]["period"].update(
            {
                "target_start": "2026-10-01",
                "target_end": "2026-12-31",
                "label": "Q4 2026E",
            }
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.guidance_surprise_payload()
        payload["facts"][2]["basis"] = "us_non_gaap_guidance"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "BASIS_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.guidance_surprise_payload()
        for index in (0, 1):
            payload["facts"][index]["period"]["expectation_as_of"] = (
                "2026-07-25T17:00:00-04:00"
            )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "EXPECTATION_NOT_POINT_IN_TIME",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_expectation_surprise_range_negative_and_zero_consensus(self) -> None:
        payload = self.surprise_payload(actual_low="98", actual_high="102")
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["state"], "straddles")

        payload = self.surprise_payload(
            metric="net_income",
            actual_low="-8",
            actual_high="-8",
            consensus="-10",
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["state"], "beat")
        self.assertEqual(
            result["checks"][0]["outputs"]["percentage_low"]["value"], "20"
        )

        payload = self.surprise_payload(actual_low="1", actual_high="1", consensus="0")
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["state"], "not_meaningful")
        self.assertIsNone(
            result["checks"][0]["outputs"]["percentage_low"]["value"]
        )

    def test_expectation_surprise_rejects_post_event_or_unavailable_sources(self) -> None:
        payload = self.surprise_payload()
        payload["sources"][1]["source_date"] = "2026-07-26"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "EXPECTATION_SOURCE_NOT_POINT_IN_TIME",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.surprise_payload()
        payload["sources"][0]["source_date"] = "2026-07-26"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "ACTUAL_SOURCE_AFTER_EVENT",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.surprise_payload()
        payload["facts"][0].update(
            {"value": None, "missing_reason": "official_missing", "source_refs": []}
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)

    def test_expectation_surprise_blocks_metric_basis_and_period_mismatch(self) -> None:
        mutations = (
            ("metric", "net_income", "METRIC_MISMATCH"),
            ("basis", "us_non_gaap_adjusted", "BASIS_MISMATCH"),
        )
        for field, value, expected_code in mutations:
            with self.subTest(field=field):
                payload = self.surprise_payload()
                payload["facts"][2][field] = value
                code, result = self.audit(payload)
                self.assertEqual(code, 1)
                self.assertIn(
                    expected_code,
                    {issue["code"] for issue in result["checks"][0]["issues"]},
                )

        payload = self.surprise_payload()
        payload["facts"][2]["period"].update(
            {
                "target_start": "2026-01-01",
                "target_end": "2026-03-31",
                "label": "Q1 2026E",
            }
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_expectation_surprise_audits_report_claim_without_counting_it(self) -> None:
        payload = self.surprise_payload(expected_percentage="5")
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)
        self.assertEqual(
            result["checks"][0]["source_gate"]["independent_origin_count"], 2
        )

        payload = self.surprise_payload(expected_percentage="4")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "MATERIAL_CONFLICT",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_post_event_consensus_fails_and_blocks_dependent_pe(self) -> None:
        payload = self.derived_pe_payload()
        payload["facts"][4]["period"]["expectation_as_of"] = "2026-07-26"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        expectation_codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        pe_codes = {issue["code"] for issue in result["checks"][2]["issues"]}
        self.assertIn("EXPECTATION_NOT_POINT_IN_TIME", expectation_codes)
        self.assertIn("DEPENDENCY_FAILED", pe_codes)

    def test_expectation_gap_actual_information_time_blocks_post_actual_consensus_and_pe(
        self,
    ) -> None:
        payload = self.derived_pe_payload()
        event_at = payload["checks"][1]["event_at"]
        self.assertEqual(payload["facts"][2]["available_at"], event_at)
        self.assertEqual(payload["facts"][3]["available_at"], event_at)
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)

        payload = self.derived_pe_payload()
        payload["sources"][2]["source_date"] = "2026-07-20"
        payload["sources"][3]["source_date"] = "2026-07-22"
        for index in (2, 3):
            payload["facts"][index]["available_at"] = (
                "2026-07-20T18:00:00+08:00"
            )
        payload["facts"][4]["period"]["expectation_as_of"] = "2026-07-22"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        expectation_codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        pe_codes = {issue["code"] for issue in result["checks"][2]["issues"]}
        self.assertIn("ACTUAL_INFORMATION_NOT_AT_EVENT", expectation_codes)
        self.assertIn("DEPENDENCY_FAILED", pe_codes)

        payload = self.derived_pe_payload()
        payload["sources"][2]["source_date"] = "2026-07-26"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "ACTUAL_SOURCE_AFTER_EVENT",
            {issue["code"] for issue in result["checks"][1]["issues"]},
        )

    def test_consensus_source_must_itself_be_published_before_event(self) -> None:
        payload = self.derived_pe_payload()
        payload["sources"][3]["source_date"] = "2026-07-26"
        self.assertEqual(
            payload["facts"][4]["period"]["expectation_as_of"], "2026-07-20"
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        expectation_codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        pe_codes = {issue["code"] for issue in result["checks"][2]["issues"]}
        self.assertIn("EXPECTATION_SOURCE_NOT_POINT_IN_TIME", expectation_codes)
        self.assertIn("DEPENDENCY_FAILED", pe_codes)

        payload = self.derived_pe_payload()
        payload["sources"][3]["source_date"] = "2026-07-25"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        expectation_codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        self.assertIn("EXPECTATION_SOURCE_NOT_POINT_IN_TIME", expectation_codes)

        payload = self.derived_pe_payload()
        payload["sources"][3]["checked_at"] = "2026-07-27T15:00:00+08:00"
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)

    def test_expectation_gap_blocks_wrong_target_year_and_future_company_quarter(self) -> None:
        payload = self.derived_pe_payload()
        payload["facts"][4]["period"].update(
            {
                "target_start": "2030-01-01",
                "target_end": "2030-12-31",
                "label": "FY2030E",
            }
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        expectation_codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        pe_codes = {issue["code"] for issue in result["checks"][2]["issues"]}
        self.assertIn("PERIOD_MISMATCH", expectation_codes)
        self.assertIn("DEPENDENCY_FAILED", pe_codes)

        payload = self.derived_pe_payload()
        payload["checks"][1]["event_at"] = "2026-06-15T18:00:00+08:00"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        expectation_codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        self.assertIn("PERIOD_MISMATCH", expectation_codes)

    def test_expectation_gap_requires_the_project_factor_four_contract(self) -> None:
        payload = self.derived_pe_payload()
        payload["checks"][1]["annualization_factor"] = "3"
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "SCHEMA_ERROR")

    def test_frequency_label_cannot_turn_one_day_into_a_quarter(self) -> None:
        payload = self.derived_pe_payload()
        one_day_quarter = duration(
            "2026-06-30", "2026-07-01", "quarter", "fake Q2 FY2026"
        )
        payload["facts"][2]["period"] = one_day_quarter
        payload["facts"][3]["period"] = one_day_quarter
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "INVALID_PERIOD_SPAN")

    def test_expectation_gap_requires_fixed_metrics_in_check_and_facts(self) -> None:
        payload = self.derived_pe_payload()
        payload["checks"][1]["company_metric"] = "attributable_net_profit"
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "SCHEMA_ERROR")

        payload = self.derived_pe_payload()
        payload["facts"][2]["metric"] = "attributable_net_profit"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        self.assertIn("METRIC_MISMATCH", codes)

    def test_expectation_gap_rejects_non_gaap_or_post_event_basis(self) -> None:
        payload = self.derived_pe_payload()
        payload["facts"][2]["basis"] = "non_gaap_adjusted"
        payload["facts"][3]["basis"] = "non_gaap_adjusted"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "BASIS_MISMATCH",
            {issue["code"] for issue in result["checks"][1]["issues"]},
        )
        self.assertIn(
            "DEPENDENCY_FAILED",
            {issue["code"] for issue in result["checks"][2]["issues"]},
        )

        payload = self.derived_pe_payload()
        payload["facts"][4]["basis"] = "post_event_current_consensus"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "BASIS_MISMATCH",
            {issue["code"] for issue in result["checks"][1]["issues"]},
        )
        self.assertIn(
            "DEPENDENCY_FAILED",
            {issue["code"] for issue in result["checks"][2]["issues"]},
        )

        payload = self.derived_pe_payload()
        payload["facts"][4]["metric"] = "revenue"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        codes = {issue["code"] for issue in result["checks"][1]["issues"]}
        self.assertIn("METRIC_MISMATCH", codes)

    def valuation_not_meaningful_payload(self, *, expected: bool) -> dict:
        period = instant("2026-07-27T15:00:00+08:00")
        annual = duration("2025-07-01", "2026-06-30", "ttm", "TTM 2026-06-30")
        payload = {
            "schema_version": "1.0",
            "audit_id": "not-meaningful-pe",
            "as_of": "2026-07-27T15:00:00+08:00",
            "sources": [
                source(
                    "S_OFFICIAL",
                    "official_filing",
                    "issuer:q2",
                    source_date="2026-07-27",
                )
            ],
            "facts": [
                fact("F_CAP", "total_market_cap", "500", "currency", "CNY", period, "total_market_cap", ["S_OFFICIAL"]),
                fact("F_LOW", "net_profit", "-10", "currency", "CNY", annual, "ttm_net_profit", ["S_OFFICIAL"]),
                fact("F_HIGH", "net_profit", "-5", "currency", "CNY", annual, "ttm_net_profit", ["S_OFFICIAL"]),
            ],
            "checks": [
                {
                    "id": "C_PE",
                    "kind": "valuation",
                    "materiality": "material",
                    "metric": "pe",
                    "numerator": value_ref("F_CAP"),
                    "denominator_low": value_ref("F_LOW"),
                    "denominator_high": value_ref("F_HIGH"),
                    "valuation_basis": "ttm_net_profit",
                    "source_gate": gate(),
                }
            ],
        }
        if expected:
            payload["facts"].extend(
                [
                    fact("F_PE_LOW", "pe", "10", "multiple", None, period, "ttm_net_profit", ["S_OFFICIAL"]),
                    fact("F_PE_HIGH", "pe", "12", "multiple", None, period, "ttm_net_profit", ["S_OFFICIAL"]),
                ]
            )
            payload["checks"][0].update(
                {
                    "expected_low": value_ref("F_PE_LOW"),
                    "expected_high": value_ref("F_PE_HIGH"),
                    "tolerance": {"relative_pct": "0", "absolute_base": "0"},
                }
            )
        return payload

    def generic_valuation_payload(self, metric: str) -> dict:
        as_of = "2026-07-27T15:00:00+08:00"
        ttm = duration("2025-07-01", "2026-06-30", "ttm", "TTM 2026-06-30")
        specifications = {
            "pe": (
                ("total_market_cap", "500", instant(as_of), "total_market_cap"),
                ("net_profit", "25", ttm, "ttm_net_profit"),
                "ttm_net_profit",
            ),
            "pb": (
                ("total_market_cap", "500", instant(as_of), "total_market_cap"),
                ("book_value", "250", instant(as_of), "book_value"),
                "book_value",
            ),
            "ps": (
                ("total_market_cap", "500", instant(as_of), "total_market_cap"),
                ("revenue", "100", ttm, "ttm_revenue"),
                "ttm_revenue",
            ),
            "p_fcf": (
                ("total_market_cap", "500", instant(as_of), "total_market_cap"),
                ("free_cash_flow", "50", ttm, "ttm_free_cash_flow"),
                "ttm_free_cash_flow",
            ),
            "dividend_yield": (
                ("cash_dividend", "10", ttm, "ttm_cash_dividend"),
                ("total_market_cap", "500", instant(as_of), "total_market_cap"),
                "ttm_cash_dividend",
            ),
            "earnings_yield": (
                ("net_profit", "25", ttm, "ttm_net_profit"),
                ("total_market_cap", "500", instant(as_of), "total_market_cap"),
                "ttm_net_profit",
            ),
        }
        numerator, denominator, valuation_basis = specifications[metric]
        return {
            "schema_version": "1.0",
            "audit_id": f"generic-{metric}",
            "as_of": as_of,
            "sources": [
                source(
                    "S_OFFICIAL",
                    "official_filing",
                    "issuer:valuation",
                    source_date="2026-07-27",
                )
            ],
            "facts": [
                fact(
                    "F_NUMERATOR",
                    numerator[0],
                    numerator[1],
                    "currency",
                    "CNY",
                    numerator[2],
                    numerator[3],
                    ["S_OFFICIAL"],
                ),
                fact(
                    "F_DENOMINATOR",
                    denominator[0],
                    denominator[1],
                    "currency",
                    "CNY",
                    denominator[2],
                    denominator[3],
                    ["S_OFFICIAL"],
                ),
            ],
            "checks": [
                {
                    "id": "C_VALUATION",
                    "kind": "valuation",
                    "materiality": "material",
                    "metric": metric,
                    "numerator": value_ref("F_NUMERATOR"),
                    "denominator_low": value_ref("F_DENOMINATOR"),
                    "denominator_high": value_ref("F_DENOMINATOR"),
                    "valuation_basis": valuation_basis,
                    "source_gate": gate(),
                }
            ],
        }

    def test_nonpositive_profit_returns_valid_not_meaningful_state(self) -> None:
        code, result = self.audit(self.valuation_not_meaningful_payload(expected=False))
        self.assertEqual(code, 0)
        check = result["checks"][0]
        self.assertEqual(check["state"], "not_meaningful")
        self.assertIsNone(check["outputs"]["low"]["value"])

    def test_numeric_pe_claim_on_loss_is_blocked(self) -> None:
        code, result = self.audit(self.valuation_not_meaningful_payload(expected=True))
        self.assertEqual(code, 1)
        codes = {issue["code"] for issue in result["checks"][0]["issues"]}
        self.assertIn("NUMERIC_CLAIM_NOT_MEANINGFUL", codes)

    def test_numeric_expectation_always_requires_explicit_tolerance(self) -> None:
        payload = self.valuation_not_meaningful_payload(expected=True)
        payload["checks"][0].pop("tolerance")
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "SCHEMA_ERROR")

    def test_generic_valuation_metric_pairings_are_enforced(self) -> None:
        for metric in ("pe", "pb", "ps", "p_fcf", "dividend_yield", "earnings_yield"):
            with self.subTest(metric=metric, case="valid"):
                code, result = self.audit(self.generic_valuation_payload(metric))
                self.assertEqual(code, 0, result)

            with self.subTest(metric=metric, case="illegal_pair"):
                payload = self.generic_valuation_payload(metric)
                payload["facts"][1].update(
                    {
                        "metric": "revenue" if metric != "ps" else "free_cash_flow",
                        "basis": "ttm_revenue" if metric != "ps" else "ttm_free_cash_flow",
                        "period": duration(
                            "2025-07-01", "2026-06-30", "ttm", "TTM 2026-06-30"
                        ),
                        "available_at": "2026-06-30",
                    }
                )
                code, result = self.audit(payload)
                self.assertEqual(code, 1)
                codes = {issue["code"] for issue in result["checks"][0]["issues"]}
                self.assertIn("METRIC_MISMATCH", codes)

    def test_generic_valuation_rejects_bad_basis_period_and_eps_as_price(self) -> None:
        payload = self.generic_valuation_payload("pe")
        payload["facts"][1]["basis"] = "ttm_revenue"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "BASIS_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.generic_valuation_payload("pe")
        payload["facts"][1]["period"] = duration(
            "2026-04-01", "2026-06-30", "quarter", "Q2 FY2026"
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.generic_valuation_payload("pe")
        payload["facts"][0].update(
            {
                "metric": "eps",
                "unit": "currency_per_share",
                "basis": "ttm_eps",
            }
        )
        payload["facts"][1].update(
            {"metric": "eps", "unit": "currency_per_share", "basis": "ttm_eps"}
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "METRIC_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.generic_valuation_payload("pe")
        payload["facts"][0].update(
            {
                "metric": "close_price",
                "unit": "currency_per_share",
                "basis": "adjusted_close",
            }
        )
        payload["facts"][1].update(
            {
                "metric": "eps",
                "unit": "currency_per_share",
                "basis": "ttm_eps",
            }
        )
        payload["checks"][0]["valuation_basis"] = "ttm_eps"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "BASIS_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_generic_valuation_requires_temporally_aligned_market_snapshot(self) -> None:
        payload = self.generic_valuation_payload("pe")
        payload["facts"][0]["period"] = instant("2020-12-31T15:00:00+08:00")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.generic_valuation_payload("pe")
        payload["facts"][0]["period"] = instant("2026-07-20T15:00:00+08:00")
        payload["facts"][1]["period"] = estimate("2026-07-25", "FY2026E")
        payload["facts"][1]["available_at"] = "2026-07-25"
        payload["facts"][1]["basis"] = "fy_net_profit"
        payload["checks"][0]["valuation_basis"] = "fy_net_profit"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.generic_valuation_payload("pb")
        payload["facts"][0]["period"] = instant("2026-06-29T15:00:00+08:00")
        payload["facts"][1]["period"] = instant("2026-06-30T15:00:00+08:00")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_pe_user_defined_requires_fixed_derived_chain(self) -> None:
        payload = self.derived_pe_payload()
        payload["checks"][2]["numerator"] = value_ref("F_Q_LOW")
        payload["checks"][2]["denominator_low"] = value_ref("F_Q_LOW")
        payload["checks"][2]["denominator_high"] = value_ref("F_Q_HIGH")
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        codes = {issue["code"] for issue in result["checks"][2]["issues"]}
        self.assertIn("METRIC_MISMATCH", codes)
        self.assertIn("DERIVATION_CONTRACT_MISMATCH", codes)

    def percentage_payload(self, *, base: str = "100", expected: bool = True) -> dict:
        q1 = duration("2026-01-01", "2026-03-31", "quarter", "Q1 FY2026")
        q2 = duration("2026-04-01", "2026-06-30", "quarter", "Q2 FY2026")
        payload = {
            "schema_version": "1.0",
            "audit_id": "percentage",
            "as_of": "2026-07-27T15:00:00+08:00",
            "sources": [source("S_OFFICIAL", "official_filing", "issuer:h1")],
            "facts": [
                fact("F_CURRENT", "revenue", "110", "currency", "CNY", q2, "reported_consolidated_prc_gaap", ["S_OFFICIAL"]),
                fact("F_BASE", "revenue", base, "currency", "CNY", q1, "reported_consolidated_prc_gaap", ["S_OFFICIAL"]),
            ],
            "checks": [
                {
                    "id": "C_QOQ",
                    "kind": "percentage",
                    "materiality": "material",
                    "mode": "change",
                    "current": value_ref("F_CURRENT"),
                    "base": value_ref("F_BASE"),
                    "period_relation": "qoq",
                    "output_metric": "revenue_qoq_pct",
                    "output_basis": "reported_consolidated_prc_gaap_qoq",
                    "source_gate": gate(),
                }
            ],
        }
        if expected:
            payload["facts"].append(
                fact(
                    "F_EXPECTED",
                    "revenue_qoq_pct",
                    "10",
                    "percent",
                    None,
                    q2,
                    "reported_consolidated_prc_gaap_qoq",
                    ["S_OFFICIAL"],
                )
            )
            payload["checks"][0].update(
                {
                    "expected": value_ref("F_EXPECTED"),
                    "tolerance": {"relative_pct": "0", "absolute_base": "0"},
                }
            )
        return payload

    def ratio_payload(self) -> dict:
        annual = duration("2025-01-01", "2025-12-31", "year", "FY2025")
        basis = "reported_consolidated_prc_gaap"
        return {
            "schema_version": "1.0",
            "audit_id": "gross-margin",
            "as_of": "2026-07-27T15:00:00+08:00",
            "sources": [source("S_OFFICIAL", "official_filing", "issuer:FY2025")],
            "facts": [
                fact(
                    "F_GROSS_PROFIT",
                    "gross_profit",
                    "30",
                    "currency",
                    "CNY",
                    annual,
                    basis,
                    ["S_OFFICIAL"],
                ),
                fact(
                    "F_REVENUE",
                    "revenue",
                    "100",
                    "currency",
                    "CNY",
                    annual,
                    basis,
                    ["S_OFFICIAL"],
                ),
            ],
            "checks": [
                {
                    "id": "C_GROSS_MARGIN",
                    "kind": "percentage",
                    "materiality": "material",
                    "mode": "ratio",
                    "numerator": value_ref("F_GROSS_PROFIT"),
                    "denominator": value_ref("F_REVENUE"),
                    "period_relation": "same",
                    "output_metric": "gross_margin_pct",
                    "output_basis": f"{basis}_over_{basis}",
                    "source_gate": gate(),
                }
            ],
        }

    def test_percentage_change_is_exact_and_zero_base_is_not_meaningful(self) -> None:
        code, result = self.audit(self.percentage_payload())
        self.assertEqual(code, 0)
        self.assertEqual(result["checks"][0]["outputs"]["value"]["value"], "10")

        code, result = self.audit(self.percentage_payload(base="0", expected=False))
        self.assertEqual(code, 0)
        self.assertEqual(result["checks"][0]["state"], "not_meaningful")

        code, result = self.audit(self.percentage_payload(base="0", expected=True))
        self.assertEqual(code, 1)

    def test_percentage_period_relation_cannot_mislabel_yoy_as_qoq(self) -> None:
        payload = self.percentage_payload(expected=False)
        payload["facts"][1]["period"] = duration(
            "2025-04-01", "2025-06-30", "quarter", "Q2 FY2025"
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        codes = {issue["code"] for issue in result["checks"][0]["issues"]}
        self.assertIn("PERIOD_MISMATCH", codes)

        payload = self.percentage_payload(expected=False)
        payload["checks"][0]["period_relation"] = "same"
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "SCHEMA_ERROR")

    def test_percentage_change_output_contract_cannot_be_relabelled(self) -> None:
        payload = self.percentage_payload(expected=False)
        payload["checks"][0]["output_metric"] = "eps_qoq_pct"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "METRIC_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.percentage_payload(expected=False)
        payload["checks"][0]["output_basis"] = "adjusted_non_gaap_qoq"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "BASIS_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_percentage_ratio_requires_whitelisted_pair_and_output(self) -> None:
        code, result = self.audit(self.ratio_payload())
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"][0]["outputs"]["value"]["value"], "30")

        payload = self.ratio_payload()
        payload["facts"][0]["metric"] = "revenue"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "UNSUPPORTED_RATIO_CONTRACT",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

        payload = self.ratio_payload()
        payload["checks"][0]["output_metric"] = "eps_margin_pct"
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "METRIC_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_income_sector_distribution_ratio_contracts_are_explicit(self) -> None:
        pairings = (
            ("cash_distribution", "affo", "distribution_payout_pct"),
            ("cash_distribution", "ffo", "distribution_payout_pct"),
            (
                "cash_distribution",
                "distributable_amount",
                "distribution_payout_pct",
            ),
            (
                "cash_distribution",
                "net_investment_income",
                "distribution_payout_pct",
            ),
            ("affo", "cash_distribution", "distribution_coverage_pct"),
            ("ffo", "cash_distribution", "distribution_coverage_pct"),
            (
                "distributable_amount",
                "cash_distribution",
                "distribution_coverage_pct",
            ),
            (
                "net_investment_income",
                "cash_distribution",
                "distribution_coverage_pct",
            ),
            (
                "operating_cash_flow",
                "cash_dividend",
                "operating_cash_flow_dividend_coverage_pct",
            ),
        )
        for numerator_metric, denominator_metric, output_metric in pairings:
            with self.subTest(pair=f"{numerator_metric}/{denominator_metric}"):
                payload = self.ratio_payload()
                payload["facts"][0]["metric"] = numerator_metric
                payload["facts"][0]["basis"] = f"reported_{numerator_metric}"
                payload["facts"][1]["metric"] = denominator_metric
                payload["facts"][1]["basis"] = f"reported_{denominator_metric}"
                payload["checks"][0]["output_metric"] = output_metric
                payload["checks"][0]["output_basis"] = (
                    f"reported_{numerator_metric}_over_reported_{denominator_metric}"
                )
                code, result = self.audit(payload)
                self.assertEqual(code, 0, result)

        payload = self.ratio_payload()
        payload["facts"][0].update(
            {"metric": "cash_distribution", "basis": "reported_cash_distribution"}
        )
        payload["facts"][1].update({"metric": "affo", "basis": "reported_affo"})
        payload["checks"][0].update(
            {
                "output_metric": "distribution_payout_pct",
                "output_basis": "reported_cash_distribution_over_reported_affo",
            }
        )
        payload["facts"][1]["period"] = duration(
            "2024-01-01", "2024-12-31", "year", "FY2024"
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_percentage_qoq_periods_must_have_comparable_spans(self) -> None:
        payload = self.percentage_payload(expected=False)
        payload["facts"][0]["period"] = duration(
            "2026-03-12", "2026-06-30", "quarter", "long Q2 FY2026"
        )
        payload["facts"][1]["period"] = duration(
            "2026-01-01", "2026-03-17", "quarter", "short Q1 FY2026"
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertIn(
            "PERIOD_MISMATCH",
            {issue["code"] for issue in result["checks"][0]["issues"]},
        )

    def test_supporting_numeric_conflict_blocks_valid_material_check(self) -> None:
        payload = self.valid_cross_source_payload()
        warning = copy.deepcopy(payload["checks"][0])
        warning["id"] = "C_SUPPORTING"
        warning["materiality"] = "supporting"
        payload["facts"].append(
            copy.deepcopy(payload["facts"][1]) | {"id": "F_BAD", "value": "80"}
        )
        warning["references"] = [value_ref("F_BAD")]
        payload["checks"].append(warning)
        payload["provisional_context"] = {
            "requested": True,
            "fallback_completed": True,
            "missing_materials": ["claimed supporting gap"],
            "recheck_after": "2026-07-28T15:00:00+08:00",
        }
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(result["release_status"], "blocked")
        self.assertEqual(result["summary"]["warning_count"], 1)
        self.assertEqual(result["summary"]["blocking_warning_count"], 1)

    def test_provisional_only_applies_to_complete_official_source_gap(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["facts"][1].update(
            {"value": None, "missing_reason": "official_missing", "source_refs": []}
        )
        payload["provisional_context"] = {
            "requested": True,
            "fallback_completed": True,
            "missing_materials": ["official FY2025 filing value"],
            "recheck_after": "2026-07-28T15:00:00+08:00",
        }
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["release_status"], "provisional")

        payload = self.valid_cross_source_payload()
        payload["facts"][1]["value"] = "80"
        payload["provisional_context"] = {
            "requested": True,
            "fallback_completed": True,
            "missing_materials": ["claimed gap"],
            "recheck_after": "2026-07-28T15:00:00+08:00",
        }
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(result["release_status"], "blocked")

    def test_official_anchor_plus_missing_second_vendor_is_not_provisional(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["checks"][0]["source_gate"] = gate(2, "any_credible", "official")
        payload["provisional_context"] = {
            "requested": True,
            "fallback_completed": True,
            "missing_materials": ["second market-data vendor"],
            "recheck_after": "2026-07-28T15:00:00+08:00",
        }
        code, result = self.audit(payload)
        self.assertEqual(code, 1)
        self.assertEqual(result["release_status"], "blocked")
        source_issue = next(
            issue
            for issue in result["checks"][0]["issues"]
            if issue["code"] == "MISSING_REQUIRED_SOURCE"
        )
        self.assertFalse(source_issue["provisional_eligible"])

    def test_excluded_source_is_retained_but_cannot_be_referenced(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["sources"].append(
            source("S_EXCLUDED", "credible_secondary", "media:wrong", status="excluded")
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 0)
        self.assertEqual(result["excluded_sources"][0]["id"], "S_EXCLUDED")

        payload["facts"][1]["source_refs"] = ["S_EXCLUDED"]
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "EXCLUDED_SOURCE_REFERENCE")

    def test_schema_rejects_numeric_literals_nan_duplicate_ids_and_forward_refs(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["facts"][0]["value"] = 100
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "NUMERIC_LITERAL_NOT_STRING")

        payload = self.valid_cross_source_payload()
        payload["facts"][0]["value"] = float("nan")
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "NON_FINITE_DECIMAL")

        payload = self.valid_cross_source_payload()
        payload["facts"].append(copy.deepcopy(payload["facts"][0]))
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "DUPLICATE_ID")

        payload = self.valid_cross_source_payload()
        payload["checks"].insert(
            0,
            {
                "id": "C_FORWARD",
                "kind": "valuation",
                "materiality": "material",
                "metric": "pe",
                "numerator": check_ref("C_REVENUE", "value"),
                "denominator_low": value_ref("F_OFFICIAL"),
                "denominator_high": value_ref("F_OFFICIAL"),
                "valuation_basis": "test",
                "source_gate": gate(),
            },
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "FORWARD_REFERENCE")

    def test_normalized_locator_cannot_claim_two_origins(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["sources"][1]["locator"] = "  HTTPS://EXAMPLE.COM/S_REPORT  "
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "LOCATOR_ORIGIN_CONFLICT")

    def test_root_as_of_rejects_future_sources_facts_and_event_dates(self) -> None:
        cases: list[tuple[str, dict]] = []

        payload = self.market_cap_payload()
        payload["sources"][0]["source_date"] = "2026-07-28"
        cases.append(("source_date", payload))

        payload = self.market_cap_payload()
        payload["sources"][0]["checked_at"] = "2026-07-28T09:00:00+08:00"
        cases.append(("checked_at", payload))

        payload = self.market_cap_payload()
        payload["facts"][0]["period"] = instant("2026-07-28T15:00:00+08:00")
        cases.append(("instant_fact", payload))

        payload = self.valid_cross_source_payload()
        payload["facts"][0]["period"] = duration(
            "2025-07-29", "2026-07-28", "year", "future duration"
        )
        cases.append(("duration_fact", payload))

        payload = self.derived_pe_payload()
        payload["facts"][4]["period"]["expectation_as_of"] = "2026-07-28"
        cases.append(("estimate_as_of", payload))

        payload = self.derived_pe_payload()
        payload["checks"][1]["event_at"] = "2026-07-28T18:00:00+08:00"
        cases.append(("event_at", payload))

        for label, payload in cases:
            with self.subTest(label=label):
                code, result = self.audit(payload)
                self.assertEqual(code, 2)
                self.assertEqual(result["code"], "LOOKAHEAD_DATE")

        payload = self.market_cap_payload()
        payload["as_of"] = "2025-01-01T15:00:00+08:00"
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "LOOKAHEAD_DATE")

    def test_required_event_and_audit_timestamps_must_be_timezone_aware(self) -> None:
        cases: list[tuple[str, dict]] = []

        payload = self.valid_cross_source_payload()
        payload["as_of"] = "2026-07-27"
        cases.append(("root_date", payload))

        payload = self.valid_cross_source_payload()
        payload["sources"][0]["checked_at"] = "2026-07-27T15:00:00"
        cases.append(("checked_at_naive", payload))

        payload = self.market_cap_payload()
        payload["facts"][0]["period"] = instant("2026-07-27T15:00:00")
        cases.append(("instant_naive", payload))

        payload = self.derived_pe_payload()
        payload["checks"][1]["event_at"] = "2026-07-25T18:00:00"
        cases.append(("event_naive", payload))

        for label, payload in cases:
            with self.subTest(label=label):
                code, result = self.audit(payload)
                self.assertEqual(code, 2)
                self.assertEqual(result["code"], "INVALID_TIMESTAMP")

    def test_same_day_afternoon_values_are_blocked_at_morning_cutoff(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["as_of"] = "2026-07-27T10:00:00+08:00"
        for item in payload["sources"]:
            item["checked_at"] = "2026-07-27T09:00:00+08:00"
        payload["sources"][0]["checked_at"] = "2026-07-27T15:00:00+08:00"
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "LOOKAHEAD_DATE")

        payload = self.valid_cross_source_payload()
        payload["as_of"] = "2026-07-27T10:00:00+08:00"
        for item in payload["sources"]:
            item["checked_at"] = "2026-07-27T09:00:00+08:00"
        payload["sources"][0]["source_date"] = "2026-07-27T15:00:00+08:00"
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "LOOKAHEAD_DATE")

        payload = self.market_cap_payload()
        payload["as_of"] = "2026-07-27T10:00:00+08:00"
        for item in payload["sources"]:
            item["checked_at"] = "2026-07-27T09:00:00+08:00"
        payload["facts"][0]["period"] = instant("2026-07-27T15:00:00+08:00")
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "LOOKAHEAD_DATE")

        payload = self.derived_pe_payload()
        payload["as_of"] = "2026-07-27T10:00:00+08:00"
        for item in payload["sources"]:
            item["checked_at"] = "2026-07-27T09:00:00+08:00"
        payload["facts"][0]["period"] = instant("2026-07-25T15:00:00+08:00")
        payload["checks"][1]["event_at"] = "2026-07-27T15:00:00+08:00"
        code, result = self.audit(payload)
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "LOOKAHEAD_DATE")

    def test_date_cutoffs_are_allowed_and_estimate_target_may_be_future(self) -> None:
        payload = self.valid_cross_source_payload()
        payload["facts"].append(
            fact(
                "F_FUTURE_ESTIMATE",
                "revenue",
                "120",
                "currency",
                "CNY",
                {
                    "kind": "estimate",
                    "expectation_as_of": "2026-07-27",
                    "target_start": "2030-01-01",
                    "target_end": "2030-12-31",
                    "frequency": "year",
                    "label": "FY2030E",
                },
                "fy_revenue",
                ["S_OFFICIAL"],
            )
        )
        code, result = self.audit(payload)
        self.assertEqual(code, 0, result)

    def test_audit_rejects_same_resolved_input_output_without_mutation(self) -> None:
        path = self.write_payload(self.valid_cross_source_payload())
        original = path.read_bytes()
        code, result = self.run_cli(
            "audit", "--input", str(path), "--output", str(path.resolve())
        )
        self.assertEqual(code, 2)
        self.assertEqual(result["code"], "OUTPUT_OVERWRITES_INPUT")
        self.assertEqual(path.read_bytes(), original)

    def test_same_input_produces_byte_identical_machine_output(self) -> None:
        path = self.write_payload(self.valid_cross_source_payload())
        first = subprocess.run(
            [sys.executable, str(SCRIPT), "audit", "--input", str(path)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        second = subprocess.run(
            [sys.executable, str(SCRIPT), "audit", "--input", str(path)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)


if __name__ == "__main__":
    unittest.main()
