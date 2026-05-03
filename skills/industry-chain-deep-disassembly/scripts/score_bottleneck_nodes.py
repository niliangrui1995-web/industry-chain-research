#!/usr/bin/env python3
"""Score supply-chain bottleneck nodes from a CSV table."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import TextIO


SCORE_COLUMNS = {
    "demand_pass_through": 0.18,
    "supply_rigidity": 0.18,
    "lead_time_pressure": 0.14,
    "substitution_resistance": 0.16,
    "concentration_pricing": 0.14,
    "profit_pool_migration": 0.10,
    "financial_confirmation": 0.10,
}

MAIN_EVIDENCE = {"A", "B"}


def _parse_score(row: dict[str, str], column: str) -> float:
    raw = (row.get(column) or "").strip()
    if not raw:
        raise ValueError(f"missing score column {column}")
    value = float(raw)
    if value < 0 or value > 5:
        raise ValueError(f"{column} must be between 0 and 5")
    return value


def _normalize_grade(raw: str | None) -> str:
    grade = (raw or "N/A").strip().upper()
    return grade if grade in {"A", "B", "C", "N/A", "NA", ""} else "N/A"


def _classify(score: float, evidence_grade: str) -> tuple[str, str]:
    if evidence_grade not in MAIN_EVIDENCE:
        return "watch_only", "C-grade or missing evidence caps the node at watch level"
    if score >= 80:
        return "true_choke_point", "high weighted score with A/B evidence"
    if score >= 65:
        return "probable_bottleneck", "strong but not decisive bottleneck profile"
    if score >= 50:
        return "volume_beneficiary_or_watch", "beneficiary profile needs more proof of pricing power"
    return "reject_or_low_priority", "score is too weak for bottleneck status"


def score_row(row: dict[str, str]) -> dict[str, object]:
    weighted = 0.0
    raw_scores: dict[str, float] = {}
    for column, weight in SCORE_COLUMNS.items():
        value = _parse_score(row, column)
        raw_scores[column] = value
        weighted += value * weight

    score = round((weighted / 5) * 100, 2)
    evidence_grade = _normalize_grade(row.get("evidence_grade"))
    verdict, gate_note = _classify(score, evidence_grade)
    return {
        "node": (row.get("node") or "").strip() or "N/A",
        "bottleneck_score": score,
        "verdict": verdict,
        "evidence_grade": evidence_grade,
        "gate_note": gate_note,
        "scores": raw_scores,
        "reason": (row.get("reason") or "").strip(),
    }


def _open_csv(path: str) -> TextIO:
    if path == "-":
        return sys.stdin
    return Path(path).open("r", encoding="utf-8-sig", newline="")


def score_csv(path: str) -> list[dict[str, object]]:
    with _open_csv(path) as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV must include a header row")
        missing = [column for column in ("node", *SCORE_COLUMNS.keys()) if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(missing)}")
        return [score_row(row) for row in reader]


def main() -> int:
    parser = argparse.ArgumentParser(description="Score supply-chain bottleneck nodes from CSV.")
    parser.add_argument("--csv", required=True, help="CSV path, or '-' to read CSV from stdin.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    try:
        rows = score_csv(args.csv)
    except Exception as exc:  # noqa: BLE001 - command-line tool should print user-facing errors.
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({"nodes": rows}, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
