#!/usr/bin/env python3
"""Validate bottleneck evidence packet completeness without scoring the claim."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import TextIO


REQUIRED_FIELDS = (
    "check_id",
    "node",
    "severity",
    "claim_window",
    "claim_as_of",
    "demand_evidence_kind",
    "supply_evidence_kind",
    "demand_evidence",
    "demand_evidence_date",
    "demand_source_type",
    "demand_source_locator",
    "supply_evidence",
    "supply_evidence_date",
    "supply_source_type",
    "supply_source_locator",
    "supply_gap_evidence",
    "gap_evidence_date",
    "gap_source_type",
    "gap_source_locator",
    "direct_gap_consequence",
    "constraint_mechanism",
    "time_horizon",
    "substitution_path",
    "second_source_status",
    "relief_window",
    "positive_validation",
    "counterevidence",
    "key_reversal",
    "evidence_grade",
    "source",
    "source_date",
)
EVIDENCE_DATE_FIELDS = (
    "demand_evidence_date",
    "supply_evidence_date",
    "gap_evidence_date",
    "source_date",
)
DEFAULT_MAX_AGE_DAYS = 180
MAX_MAX_AGE_DAYS = 365
MAIN_EVIDENCE = {"A", "B"}
SEVERITIES = {"hard_bottleneck", "soft_bottleneck", "watch", "rejected"}
CLAIM_WINDOWS = {"current", "future", "historical"}
DEMAND_EVIDENCE_KINDS = {"quantified_demand", "demand_step", "qualitative_signal"}
SUPPLY_EVIDENCE_KINDS = {
    "qualified_supply_limit",
    "usable_capacity_limit",
    "yield_limit",
    "delivery_limit",
    "certified_supplier_limit",
    "qualitative_constraint",
}
HARD_DEMAND_KINDS = {"quantified_demand", "demand_step"}
HARD_SUPPLY_KINDS = {
    "qualified_supply_limit",
    "usable_capacity_limit",
    "yield_limit",
    "delivery_limit",
    "certified_supplier_limit",
}
SECOND_SOURCE_STATUSES = {"none", "evaluating", "qualifying", "qualified", "ramping", "active"}
CERTIFIED_ALTERNATIVE_STATUSES = {"qualified", "ramping", "active"}
SOURCE_TYPES = {
    "regulatory",
    "official",
    "company_original",
    "official_counterparty",
    "credible_third_party",
    "social",
    "anonymous",
    "lead_only",
}
PRIMARY_SOURCE_TYPES = {
    "regulatory",
    "official",
    "company_original",
    "official_counterparty",
}
CREDIBLE_SOURCE_TYPES = PRIMARY_SOURCE_TYPES | {"credible_third_party"}
WEAK_SOURCE_TYPES = {"social", "anonymous", "lead_only"}
EMPTY_VALUES = {
    "",
    "-",
    "--",
    "N/A",
    "NA",
    "UNKNOWN",
    "NOT_MENTIONED",
    "EVIDENCE_ABSENT",
    "NOT_AVAILABLE",
    "NOT_FOUND",
    "BLOCKED",
    "PENDING",
    "TODO",
    "TBD",
    "NULL",
}


def _open_csv(path: str) -> TextIO:
    if path == "-":
        return sys.stdin
    return Path(path).open("r", encoding="utf-8-sig", newline="")


def _parse_iso_date_or_timestamp(value: str) -> date:
    """Parse the documented ISO date/timestamp forms and return their calendar date."""
    text = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return date.fromisoformat(text)
    if "T" in text:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    raise ValueError("expected YYYY-MM-DD or an ISO timestamp containing 'T'")


def validate_row(row: dict[str, str], as_of: date) -> dict[str, object]:
    missing = [
        field
        for field in REQUIRED_FIELDS
        if (row.get(field) or "").strip().upper() in EMPTY_VALUES
    ]
    grade = (row.get("evidence_grade") or "N/A").strip().upper()
    severity = (row.get("severity") or "N/A").strip().lower()
    claim_window = (row.get("claim_window") or "N/A").strip().lower()
    demand_kind = (row.get("demand_evidence_kind") or "N/A").strip().lower()
    supply_kind = (row.get("supply_evidence_kind") or "N/A").strip().lower()
    second_source_status = (row.get("second_source_status") or "N/A").strip().lower()
    leg_source_types = {
        "demand": (row.get("demand_source_type") or "N/A").strip().lower(),
        "supply": (row.get("supply_source_type") or "N/A").strip().lower(),
        "gap": (row.get("gap_source_type") or "N/A").strip().lower(),
    }
    warnings: list[str] = []
    consistency_issues: list[str] = []
    parsed_dates: dict[str, date] = {}
    evidence_age_days: dict[str, int] = {}

    raw_max_age = (row.get("max_age_days") or "").strip()
    max_age_days = DEFAULT_MAX_AGE_DAYS
    max_age_valid = True
    if raw_max_age and raw_max_age.upper() not in EMPTY_VALUES:
        try:
            max_age_days = int(raw_max_age)
        except ValueError:
            max_age_valid = False
        else:
            max_age_valid = 1 <= max_age_days <= MAX_MAX_AGE_DAYS
        if not max_age_valid:
            consistency_issues.append(
                f"max_age_days must be an integer between 1 and {MAX_MAX_AGE_DAYS}"
            )
            max_age_days = DEFAULT_MAX_AGE_DAYS

    for field in ("claim_as_of", *EVIDENCE_DATE_FIELDS):
        if field in missing:
            continue
        raw_value = (row.get(field) or "").strip()
        try:
            parsed_dates[field] = _parse_iso_date_or_timestamp(raw_value)
        except ValueError:
            consistency_issues.append(
                f"invalid ISO date/timestamp for {field}: {raw_value}"
            )

    chronological_issue = False
    cutoff_issue = False
    for field, parsed_date in parsed_dates.items():
        if parsed_date > as_of:
            cutoff_issue = True
            consistency_issues.append(
                f"{field} cannot be after as_of {as_of.isoformat()}"
            )

    claim_date = parsed_dates.get("claim_as_of")
    if claim_date is not None:
        for field in EVIDENCE_DATE_FIELDS:
            evidence_date = parsed_dates.get(field)
            if evidence_date is None:
                continue
            age_days = (claim_date - evidence_date).days
            evidence_age_days[field] = age_days
            if age_days < 0:
                chronological_issue = True
                consistency_issues.append(f"{field} cannot be after claim_as_of")

    stale_fields = [
        field for field, age_days in evidence_age_days.items() if age_days > max_age_days
    ]
    if missing:
        freshness_status = "incomplete"
    elif (
        not max_age_valid
        or len(parsed_dates) != 1 + len(EVIDENCE_DATE_FIELDS)
        or chronological_issue
        or cutoff_issue
    ):
        freshness_status = "invalid"
    elif stale_fields:
        freshness_status = "stale"
    else:
        freshness_status = "fresh"

    if severity not in SEVERITIES and "severity" not in missing:
        consistency_issues.append(f"invalid severity: {severity}")
    if claim_window not in CLAIM_WINDOWS and "claim_window" not in missing:
        consistency_issues.append(f"invalid claim_window: {claim_window}")
    if demand_kind not in DEMAND_EVIDENCE_KINDS and "demand_evidence_kind" not in missing:
        consistency_issues.append(f"invalid demand_evidence_kind: {demand_kind}")
    if supply_kind not in SUPPLY_EVIDENCE_KINDS and "supply_evidence_kind" not in missing:
        consistency_issues.append(f"invalid supply_evidence_kind: {supply_kind}")
    if second_source_status not in SECOND_SOURCE_STATUSES and "second_source_status" not in missing:
        consistency_issues.append(f"invalid second_source_status: {second_source_status}")
    for leg, source_type in leg_source_types.items():
        field = f"{leg}_source_type"
        if source_type not in SOURCE_TYPES and field not in missing:
            consistency_issues.append(f"invalid {field}: {source_type}")

    if severity == "hard_bottleneck":
        if grade != "A":
            consistency_issues.append("hard_bottleneck requires A-grade evidence")
        if claim_window != "current":
            consistency_issues.append("hard_bottleneck requires current claim_window")
        if demand_kind not in HARD_DEMAND_KINDS:
            consistency_issues.append(
                "hard_bottleneck requires quantified demand or a demand step"
            )
        if supply_kind not in HARD_SUPPLY_KINDS:
            consistency_issues.append(
                "hard_bottleneck requires a qualified/usable supply, yield, delivery, or certified-supplier limit"
            )
        if second_source_status in CERTIFIED_ALTERNATIVE_STATUSES:
            consistency_issues.append(
                "hard_bottleneck cannot have a certified alternative in the claimed window"
            )
        non_primary_legs = [
            leg for leg, source_type in leg_source_types.items()
            if source_type not in PRIMARY_SOURCE_TYPES
        ]
        if non_primary_legs:
            consistency_issues.append(
                "hard_bottleneck requires regulatory/official/company_original/"
                "official_counterparty sources for demand, supply, and gap legs: "
                + ", ".join(non_primary_legs)
            )
    elif severity == "soft_bottleneck" and grade not in MAIN_EVIDENCE:
        consistency_issues.append("soft_bottleneck requires A/B evidence")
    if severity == "soft_bottleneck":
        non_credible_legs = [
            leg for leg, source_type in leg_source_types.items()
            if source_type not in CREDIBLE_SOURCE_TYPES
        ]
        if non_credible_legs:
            consistency_issues.append(
                "soft_bottleneck requires credible traceable sources for demand, supply, "
                "and gap legs: " + ", ".join(non_credible_legs)
            )
    if severity in {"hard_bottleneck", "soft_bottleneck"}:
        weak_legs = [
            leg for leg, source_type in leg_source_types.items()
            if source_type in WEAK_SOURCE_TYPES
        ]
        if weak_legs:
            consistency_issues.append(
                "social|anonymous|lead_only evidence is watch-only and cannot support "
                "hard/soft legs: " + ", ".join(weak_legs)
            )

    if (
        claim_window == "current"
        and severity in {"hard_bottleneck", "soft_bottleneck"}
        and freshness_status == "stale"
    ):
        consistency_issues.append(
            "current hard_bottleneck/soft_bottleneck requires all evidence dates "
            f"within {max_age_days} days of claim_as_of; stale fields: "
            + ", ".join(stale_fields)
        )
    elif freshness_status == "stale":
        warnings.append(
            "stale evidence may support only a historical, watch, or incomplete record; "
            "it cannot support a current hard/soft bottleneck claim"
        )

    if missing:
        review_status = "incomplete"
    elif consistency_issues:
        review_status = "ineligible_for_claimed_severity"
    elif severity in {"watch", "rejected"} or grade not in MAIN_EVIDENCE:
        review_status = "watch_only"
        warnings.append("A/B evidence is required before bottleneck review")
    else:
        review_status = "eligible_for_bottleneck_review"
    return {
        "check_id": (row.get("check_id") or "N/A").strip(),
        "node": (row.get("node") or "N/A").strip(),
        "review_status": review_status,
        "missing_fields": missing,
        "consistency_issues": consistency_issues,
        "warnings": warnings,
        "evidence_grade": grade,
        "severity": severity,
        "claim_window": claim_window,
        "claim_as_of": (row.get("claim_as_of") or "N/A").strip(),
        "max_age_days": max_age_days,
        "evidence_dates": {
            field: (row.get(field) or "N/A").strip() for field in EVIDENCE_DATE_FIELDS
        },
        "evidence_age_days": evidence_age_days,
        "freshness_status": freshness_status,
        "note": "Completeness is not proof; assess the cited demand and qualified-supply gap evidence.",
    }


def validate_csv(path: str, as_of: date) -> list[dict[str, object]]:
    with _open_csv(path) as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV must include a header row")
        missing_columns = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"CSV missing columns: {', '.join(missing_columns)}")
        rows = [validate_row(row, as_of) for row in reader]
        if not rows:
            raise ValueError("CSV must include at least one evidence row")
        return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate bottleneck evidence packet completeness.")
    parser.add_argument("--csv", required=True, help="CSV path, or '-' for stdin.")
    parser.add_argument(
        "--as-of",
        required=True,
        help="Deterministic research cutoff date in YYYY-MM-DD format.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.as_of):
        parser.error("--as-of must use YYYY-MM-DD")
    try:
        as_of = date.fromisoformat(args.as_of)
    except ValueError:
        parser.error("--as-of must be a valid YYYY-MM-DD date")
    try:
        rows = validate_csv(args.csv, as_of)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 2
    incomplete = sum(row["review_status"] == "incomplete" for row in rows)
    ineligible = sum(
        row["review_status"] == "ineligible_for_claimed_severity" for row in rows
    )
    eligible = sum(row["review_status"] == "eligible_for_bottleneck_review" for row in rows)
    packet_status = (
        "incomplete"
        if incomplete
        else "ineligible"
        if ineligible
        else "reviewable"
        if eligible
        else "watch_only"
    )
    payload = {
        "status": packet_status,
        "as_of": as_of.isoformat(),
        "incomplete_count": incomplete,
        "ineligible_count": ineligible,
        "eligible_count": eligible,
        "nodes": rows,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 1 if incomplete or ineligible else 0


if __name__ == "__main__":
    raise SystemExit(main())
