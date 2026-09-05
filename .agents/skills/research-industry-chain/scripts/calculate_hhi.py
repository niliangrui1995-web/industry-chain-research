#!/usr/bin/env python3
"""Calculate Herfindahl-Hirschman Index (HHI) from market-share data."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Iterable


def _parse_share(value: str | float, unit: str) -> float:
    raw = str(value).strip()
    if raw.endswith("%"):
        if unit != "percent":
            raise ValueError("percent suffix conflicts with fraction unit")
        raw = raw[:-1].strip()
    if not raw:
        raise ValueError("empty share value")
    share = float(raw)
    if not math.isfinite(share):
        raise ValueError("shares must be finite numbers")
    return share


def _normalize_shares(values: Iterable[str | float], unit: str | None) -> list[float]:
    values = list(values)
    if not values:
        raise ValueError("at least one share is required")
    if unit is None:
        if not all(str(value).strip().endswith("%") for value in values):
            raise ValueError("bare shares require an explicit unit: percent or fraction")
        unit = "percent"
    if unit not in {"percent", "fraction"}:
        raise ValueError("unit must be percent or fraction")
    shares = [_parse_share(value, unit) for value in values]
    upper_bound = 100 if unit == "percent" else 1
    if any(not 0 <= value <= upper_bound for value in shares):
        raise ValueError(f"each {unit} share must be between 0 and {upper_bound}")

    total = math.fsum(shares)
    if total <= 0:
        raise ValueError("share total must be positive")
    if total > upper_bound and not math.isclose(total, upper_bound, rel_tol=1e-12):
        raise ValueError(f"{unit} share total cannot exceed {upper_bound}")

    if unit == "fraction":
        shares = [v * 100 for v in shares]

    return shares


def _read_csv(path: Path, share_column: str, company_column: str | None) -> tuple[list[str], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    shares: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or share_column not in reader.fieldnames:
            raise ValueError(f"CSV must contain share column: {share_column}")
        for row in reader:
            share = row.get(share_column, "") or ""
            shares.append(share)
            rows.append(
                {
                    "company": row.get(company_column, "") if company_column else "",
                    "share": share,
                }
            )
    return shares, rows


def _classify(hhi: float) -> str:
    if hhi < 1500:
        return "fragmented"
    if hhi < 2500:
        return "moderately_concentrated"
    return "highly_concentrated"


def calculate_hhi(shares: list[str | float], unit: str | None = None) -> dict[str, object]:
    normalized = _normalize_shares(shares, unit)
    hhi = math.fsum(v * v for v in normalized)
    sorted_shares = sorted(normalized, reverse=True)
    result: dict[str, object] = {
        "hhi": round(hhi, 2),
        "input_unit": unit or "percent",
        "classification": _classify(hhi),
        "share_total": round(sum(normalized), 4),
        "cr3": round(sum(sorted_shares[:3]), 4),
        "cr5": round(sum(sorted_shares[:5]), 4),
        "shares_percent": [round(v, 6) for v in normalized],
        "screen_hhi_gt_1800": hhi > 1800,
    }
    if not math.isclose(math.fsum(normalized), 100, rel_tol=1e-12):
        result["coverage_warning"] = (
            "market shares do not sum to 100%; HHI is based only on provided shares"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate HHI from market shares.")
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--shares", nargs="+", help="Market shares; bare numbers require --unit.")
    inputs.add_argument("--csv", type=Path, help="CSV file containing market share data.")
    parser.add_argument(
        "--unit", choices=("percent", "fraction"),
        help="Required for bare numbers; may be omitted only if every share ends in %%.",
    )
    parser.add_argument("--share-column", default="share", help="CSV share column name. Default: share")
    parser.add_argument("--company-column", default=None, help="Optional CSV company column name.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    try:
        if args.csv:
            shares, rows = _read_csv(args.csv, args.share_column, args.company_column)
            result = calculate_hhi(shares, unit=args.unit)
            if rows:
                result["rows"] = rows
        elif args.shares:
            result = calculate_hhi(args.shares, unit=args.unit)
        else:
            raise ValueError("provide --shares or --csv")
    except Exception as exc:  # noqa: BLE001 - command-line tool should print user-facing errors.
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
