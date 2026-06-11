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
    if not value:
        return None
    return float(value)


def fmt_num(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text if text else "0"


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
    return f"{sign}{fmt_num(diff)} {current.unit} / {sign}{pct:.2f}% vs {previous.date.isoformat()}"


def generate_report(history_path: Path, report_dir: Path, target_date: date) -> Path:
    rows = as_price_rows(load_rows(history_path))
    grouped: dict[str, list[PriceRow]] = defaultdict(list)
    for row in sorted(rows, key=lambda r: (r.indicator, r.date, r.source_name)):
        grouped[row.indicator].append(row)

    today_rows = [r for r in rows if r.date == target_date]
    today_rows.sort(key=lambda r: (r.indicator, r.source_name))

    core_rows = grouped.get("black_tungsten_concentrate_65", [])
    latest_core = [r for r in core_rows if r.date <= target_date]
    core_verdict = "N/A"
    if latest_core:
        current = latest_core[-1]
        peak = max(core_rows, key=lambda r: r.mid)
        low_after_peak_candidates = [r for r in core_rows if r.date >= peak.date]
        trough = min(low_after_peak_candidates, key=lambda r: r.mid) if low_after_peak_candidates else None
        prev = previous_for(current, grouped)
        parts = [f"65%黑钨精矿最新 {fmt_num(current.mid)} {current.unit}"]
        if prev:
            parts.append(f"较上一观测点 {change_text(current, prev)}")
        parts.append(f"较历史种子峰值 {fmt_num(peak.mid)} {peak.unit} 回落 {(current.mid / peak.mid - 1) * 100:.2f}%")
        if trough and current.date > trough.date:
            parts.append(f"较阶段低点 {fmt_num(trough.mid)} {trough.unit} 反弹 {(current.mid / trough.mid - 1) * 100:.2f}%")
        core_verdict = "；".join(parts)

    lines = [
        f"# 钨价跟踪日报 - {target_date.isoformat()}",
        "",
        "## 结论",
        "",
        f"- {core_verdict}",
        "- 重点判断：先看65%黑钨精矿是否继续上行，再看APT和钨粉是否同步跟进；若废钨先行回落，说明情绪和流动性转弱。",
        "",
        "## 当日价格",
        "",
        "| 品种 | 均价 | 单位 | 较上一观测 | 来源 |",
        "|---|---:|---|---|---|",
    ]

    if today_rows:
        for row in today_rows:
            prev = previous_for(row, grouped)
            source = row.source_name
            if row.source_url:
                source = f"[{row.source_name}]({row.source_url})"
            lines.append(
                f"| {row.name} | {fmt_num(row.mid)} | {row.unit} | {change_text(row, prev)} | {source} |"
            )
    else:
        lines.append("| N/A | N/A | N/A | 当日未采集到新价格 | N/A |")

    lines.extend(
        [
            "",
            "## 跟踪口径",
            "",
            "- 历史库：`automation_snapshots/tungsten-price-tracker/price_history.csv`",
            "- 若当天公开价格缺失，写 N/A，不用旧价冒充新价。",
            "- 只把有公开来源链接或明确来源名称的数据写入历史库。",
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
