#!/usr/bin/env python3
"""Append tungsten price rows and generate a compact trend report."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HISTORY = ROOT / "automation_snapshots" / "tungsten-price-tracker" / "price_history.csv"
DEFAULT_REPORT_DIR = ROOT / "automation_snapshots" / "tungsten-price-tracker" / "daily_reports"

FIELDNAMES = [
    "date",
    "indicator",
    "name",
    "low",
    "high",
    "mid",
    "unit",
    "currency",
    "source_name",
    "source_url",
    "source_grade",
    "notes",
]

DISPLAY_NAMES = {
    "black_tungsten_concentrate_55": "55%\u9ed1\u94a8\u7cbe\u77ff",
    "black_tungsten_concentrate_65": "65%\u9ed1\u94a8\u7cbe\u77ff",
    "white_tungsten_concentrate_30_40": "30-40%\u767d\u94a8\u7cbe\u77ff",
    "white_tungsten_concentrate_55": "55%\u767d\u94a8\u7cbe\u77ff",
    "white_tungsten_concentrate_65": "65%\u767d\u94a8\u7cbe\u77ff",
    "domestic_apt": "\u4ef2\u94a8\u9178\u94f5\uff08APT\uff09",
    "europe_apt": "\u6b27\u6d32APT",
    "domestic_tungsten_powder": "\u56fd\u4ea7\u94a8\u7c89",
    "domestic_tungsten_carbide_powder": "\u56fd\u4ea7\u78b3\u5316\u94a8\u7c89",
    "recycled_tungsten_carbide_powder": "\u518d\u751f\u78b3\u5316\u94a8\u7c89",
    "scrap_tungsten_bar": "\u5e9f\u94a8\u68d2\u6750",
    "scrap_tungsten_drill": "\u5e9f\u94a8\u94bb\u5934",
}

DISPLAY_UNITS = {
    "black_tungsten_concentrate_55": "\u4e07\u5143/\u6807\u5428",
    "black_tungsten_concentrate_65": "\u4e07\u5143/\u6807\u5428",
    "white_tungsten_concentrate_30_40": "\u4e07\u5143/\u6807\u5428",
    "white_tungsten_concentrate_55": "\u4e07\u5143/\u6807\u5428",
    "white_tungsten_concentrate_65": "\u4e07\u5143/\u6807\u5428",
    "domestic_apt": "\u4e07\u5143/\u5428",
    "europe_apt": "\u7f8e\u5143/\u5428\u5ea6",
    "domestic_tungsten_powder": "\u5143/\u5343\u514b",
    "domestic_tungsten_carbide_powder": "\u5143/\u5343\u514b",
    "recycled_tungsten_carbide_powder": "\u5143/\u5343\u514b",
    "scrap_tungsten_bar": "\u5143/\u5343\u514b",
    "scrap_tungsten_drill": "\u5143/\u5343\u514b",
}


@dataclass(frozen=True)
class PriceRow:
    date: date
    indicator: str
    name: str
    mid: float
    unit: str
    source_name: str
    source_url: str
    notes: str


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_float(value: str) -> float | None:
    value = str(value or "").strip()
    if not value or value.upper() == "N/A":
        return None
    return float(value)


def fmt_num(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text if text else "0"


def display_name(indicator: str, fallback: str) -> str:
    return DISPLAY_NAMES.get(indicator, fallback)


def display_unit(indicator: str, fallback: str) -> str:
    return DISPLAY_UNITS.get(indicator, fallback)


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def normalize_row(row: dict[str, object]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for field in FIELDNAMES:
        value = row.get(field, "")
        normalized[field] = "" if value is None else str(value).strip()

    if not normalized["date"]:
        raise ValueError("missing date")
    if not normalized["indicator"]:
        raise ValueError("missing indicator")
    if not normalized["name"]:
        raise ValueError("missing name")
    if not normalized["mid"]:
        low = parse_float(normalized["low"])
        high = parse_float(normalized["high"])
        if low is None or high is None:
            raise ValueError(f"missing mid for {normalized['date']} {normalized['indicator']}")
        normalized["mid"] = fmt_num((low + high) / 2)
    parse_date(normalized["date"])
    parse_float(normalized["mid"])
    return normalized


def append_rows(path: Path, new_rows: Iterable[dict[str, object]]) -> int:
    existing = [normalize_row(row) for row in load_rows(path)]
    seen = {(r["date"], r["indicator"], r["source_name"], r["source_url"]) for r in existing}
    appended = 0
    for raw in new_rows:
        row = normalize_row(raw)
        key = (row["date"], row["indicator"], row["source_name"], row["source_url"])
        if key in seen:
            continue
        existing.append(row)
        seen.add(key)
        appended += 1

    existing.sort(key=lambda r: (r["date"], r["indicator"], r["source_name"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(existing)
    return appended


def as_price_rows(rows: Iterable[dict[str, str]]) -> list[PriceRow]:
    parsed: list[PriceRow] = []
    for row in rows:
        mid = parse_float(row.get("mid", ""))
        if mid is None:
            continue
        parsed.append(
            PriceRow(
                date=parse_date(row["date"]),
                indicator=row["indicator"],
                name=row["name"],
                mid=mid,
                unit=row["unit"],
                source_name=row["source_name"],
                source_url=row["source_url"],
                notes=row.get("notes", ""),
            )
        )
    return parsed


def previous_for(row: PriceRow, grouped: dict[str, list[PriceRow]]) -> PriceRow | None:
    candidates = [r for r in grouped[row.indicator] if r.date < row.date]
    if not candidates:
        return None
    return candidates[-1]


def change_text(current: PriceRow, previous: PriceRow | None) -> str:
    if previous is None:
        return "N/A"
    diff = current.mid - previous.mid
    pct = diff / previous.mid * 100 if previous.mid else 0
    sign = "+" if diff > 0 else ""
    unit = display_unit(current.indicator, current.unit)
    return f"{sign}{fmt_num(diff)} {unit} / {sign}{pct:.2f}% vs {previous.date.isoformat()}"


def generate_report(history_path: Path, report_dir: Path, target_date: date) -> Path:
    raw_rows = load_rows(history_path)
    rows = as_price_rows(raw_rows)
    grouped: dict[str, list[PriceRow]] = defaultdict(list)
    for row in sorted(rows, key=lambda r: (r.indicator, r.date, r.source_name)):
        grouped[row.indicator].append(row)

    today_rows = [r for r in rows if r.date == target_date]
    today_rows.sort(key=lambda r: (r.indicator, r.source_name))
    today_unavailable_rows = [
        r
        for r in raw_rows
        if r.get("date") == target_date.isoformat()
        and str(r.get("mid", "")).strip().upper() == "N/A"
    ]
    today_unavailable_rows.sort(key=lambda r: (r.get("indicator", ""), r.get("source_name", "")))

    core_rows = grouped.get("black_tungsten_concentrate_65", [])
    latest_core = [r for r in core_rows if r.date <= target_date]
    core_verdict = "N/A"
    if latest_core:
        current = latest_core[-1]
        peak = max(core_rows, key=lambda r: r.mid)
        low_after_peak_candidates = [r for r in core_rows if r.date >= peak.date]
        trough = min(low_after_peak_candidates, key=lambda r: r.mid) if low_after_peak_candidates else None
        prev = previous_for(current, grouped)
        unit = display_unit(current.indicator, current.unit)
        parts = [f"65%\u9ed1\u94a8\u7cbe\u77ff\u53ef\u7528\u6700\u65b0\u6570\u503c\uff08{current.date.isoformat()}\uff09 {fmt_num(current.mid)} {unit}"]
        if current.date < target_date:
            parts.append(f"{target_date.isoformat()} \u5f53\u65e5\u516c\u5f00\u65b0\u4ef7 N/A")
        if prev:
            parts.append(f"\u8f83\u4e0a\u4e00\u89c2\u5bdf\u70b9 {change_text(current, prev)}")
        parts.append(f"\u8f83\u5386\u53f2\u79cd\u5b50\u5cf0\u503c {fmt_num(peak.mid)} {unit} \u56de\u843d {(current.mid / peak.mid - 1) * 100:.2f}%")
        if trough and current.date > trough.date:
            parts.append(f"\u8f83\u9636\u6bb5\u4f4e\u70b9 {fmt_num(trough.mid)} {unit} \u53cd\u5f39 {(current.mid / trough.mid - 1) * 100:.2f}%")
        core_verdict = "\uff1b".join(parts)

    lines = [
        f"# \u94a8\u4ef7\u8ddf\u8e2a\u65e5\u62a5 - {target_date.isoformat()}",
        "",
        "## \u7ed3\u8bba",
        "",
        f"- {core_verdict}",
        "- \u91cd\u70b9\u5224\u65ad\uff1a\u5148\u770b 65%\u9ed1\u94a8\u7cbe\u77ff\u662f\u5426\u7ee7\u7eed\u4e0a\u884c\uff0c\u518d\u770b APT \u548c\u94a8\u7c89\u662f\u5426\u540c\u6b65\u8ddf\u8fdb\uff1b\u82e5\u5e9f\u94a8\u5148\u884c\u56de\u843d\uff0c\u8bf4\u660e\u60c5\u7eea\u548c\u6d41\u52a8\u6027\u8f6c\u5f31\u3002",
        "",
        "## \u5f53\u65e5\u4ef7\u683c",
        "",
        "| \u54c1\u79cd | \u5747\u4ef7 | \u5355\u4f4d | \u8f83\u4e0a\u4e00\u89c2\u5bdf | \u6765\u6e90 |",
        "|---|---:|---|---|---|",
    ]

    if today_rows or today_unavailable_rows:
        for row in today_rows:
            prev = previous_for(row, grouped)
            source = row.source_name
            if row.source_url:
                source = f"[{row.source_name}]({row.source_url})"
            lines.append(
                f"| {display_name(row.indicator, row.name)} | {fmt_num(row.mid)} | {display_unit(row.indicator, row.unit)} | {change_text(row, prev)} | {source} |"
            )
        for row in today_unavailable_rows:
            source_name = row.get("source_name", "N/A")
            source_url = row.get("source_url", "")
            source = source_name
            if source_url:
                source = f"[{source_name}]({source_url})"
            lines.append(
                f"| {display_name(row.get('indicator', ''), row.get('name', 'N/A'))} | N/A | {display_unit(row.get('indicator', ''), row.get('unit', 'N/A'))} | N/A | {source} |"
            )
    else:
        lines.append("| N/A | N/A | N/A | \u5f53\u65e5\u672a\u91c7\u96c6\u5230\u65b0\u4ef7\u683c | N/A |")

    lines.extend(
        [
            "",
            "## \u8ddf\u8e2a\u53e3\u5f84",
            "",
            "- \u5386\u53f2\u5e93\uff1a`automation_snapshots/tungsten-price-tracker/price_history.csv`",
            "- \u82e5\u5f53\u5929\u516c\u5f00\u4ef7\u683c\u7f3a\u5931\uff0c\u5199 N/A\uff0c\u4e0d\u7528\u65e7\u4ef7\u5192\u5145\u65b0\u4ef7\u3002",
            "- \u53ea\u628a\u6709\u516c\u5f00\u6765\u6e90\u94fe\u63a5\u6216\u660e\u786e\u6765\u6e90\u540d\u79f0\u7684\u6570\u636e\u5199\u5165\u5386\u53f2\u5e93\u3002",
            "",
        ]
    )

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{target_date.isoformat()}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    target_date = parse_date(args.date)
    appended = 0
    if args.input_json and not args.report_only:
        new_rows = json.loads(args.input_json.read_text(encoding="utf-8"))
        if not isinstance(new_rows, list):
            raise ValueError("input JSON must be a list of row objects")
        appended = append_rows(args.history, new_rows)

    report_path = generate_report(args.history, args.report_dir, target_date)
    print(f"appended={appended}")
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
