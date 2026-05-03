#!/usr/bin/env python3
"""Calculate Herfindahl-Hirschman Index (HHI) from market-share data."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable


def _parse_share(value: str) -> float:
    raw = str(value).strip().replace("%", "")
    if not raw:
        raise ValueError("empty share value")
    return float(raw)


def _normalize_shares(values: Iterable[float]) -> list[float]:
    shares = [float(v) for v in values]
    if not shares:
        raise ValueError("at least one share is required")
    if any(v < 0 for v in shares):
        raise ValueError("shares must be non-negative")

    total = sum(shares)
    if total <= 0:
        raise ValueError("share total must be positive")

    # Accept either decimals that sum near 1 or percentage points.
    if max(shares) <= 1 and total <= 1.5:
        shares = [v * 100 for v in shares]

    return shares


def _read_csv(path: Path, share_column: str, company_column: str | None) -> tuple[list[float], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    shares: list[float] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or share_column not in reader.fieldnames:
            raise ValueError(f"CSV must contain share column: {share_column}")
        for row in reader:
            share = _parse_share(row.get(share_column, ""))
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


def calculate_hhi(shares: list[float]) -> dict[str, object]:
    normalized = _normalize_shares(shares)
    hhi = sum(v * v for v in normalized)
    sorted_shares = sorted(normalized, reverse=True)
    result: dict[str, object] = {
        "hhi": round(hhi, 2),
        "classification": _classify(hhi),
        "share_total": round(sum(normalized), 4),
        "cr3": round(sum(sorted_shares[:3]), 4),
        "cr5": round(sum(sorted_shares[:5]), 4),
        "shares_percent": [round(v, 6) for v in normalized],
        "screen_hhi_gt_1800": hhi > 1800,
    }
    if not 99 <= sum(normalized) <= 101:
        result["coverage_warning"] = (
            "market shares do not sum to about 100%; HHI is based only on provided shares"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate HHI from market shares.")
    parser.add_argument("--shares", nargs="*", type=float, help="Market shares as percentages or decimals.")
    parser.add_argument("--csv", type=Path, help="CSV file containing market share data.")
    parser.add_argument("--share-column", default="share", help="CSV share column name. Default: share")
    parser.add_argument("--company-column", default=None, help="Optional CSV company column name.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    try:
        if args.csv:
            shares, rows = _read_csv(args.csv, args.share_column, args.company_column)
            result = calculate_hhi(shares)
            if rows:
                result["rows"] = rows
        elif args.shares:
            result = calculate_hhi(args.shares)
        else:
            raise ValueError("provide --shares or --csv")
    except Exception as exc:  # noqa: BLE001 - command-line tool should print user-facing errors.
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
