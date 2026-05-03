#!/usr/bin/env python3
"""Normalize industry-chain research input files into canonical JSON tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Iterable, Iterator


TABLES: dict[str, dict[str, list[str]]] = {
    "global_leaders": {
        "required": ["company", "ticker", "exchange", "country"],
        "fields": [
            "company",
            "ticker",
            "exchange",
            "country",
            "linked_node",
            "segment_exposure",
            "revenue_mix",
            "gross_margin",
            "capex",
            "backlog_or_orders",
            "market_cap",
            "valuation",
            "price_trend",
            "evidence_grade",
            "source",
        ],
    },
    "supply_chain_nodes": {
        "required": ["node", "layer"],
        "fields": [
            "layer",
            "node",
            "BOM_or_value_share",
            "margin_proxy",
            "lead_time",
            "capacity_rigidity",
            "substitution_elasticity",
            "top_players",
            "market_share",
            "pricing_mechanism",
            "evidence_grade",
            "source",
        ],
    },
    "china_candidates": {
        "required": ["company", "ticker"],
        "fields": [
            "company",
            "ticker",
            "exchange",
            "linked_node",
            "exposure_evidence",
            "pure_play_level",
            "revenue_materiality",
            "fundamental_quality",
            "earnings_elasticity",
            "trading_elasticity",
            "verdict",
            "evidence_grade",
            "source",
        ],
    },
    "financial_validation": {
        "required": ["company", "ticker", "period"],
        "fields": [
            "company",
            "ticker",
            "period",
            "revenue",
            "gross_margin",
            "net_margin",
            "receivables_turnover",
            "inventory_turnover",
            "operating_cash_flow",
            "capex",
            "debt_or_net_cash",
            "evidence_grade",
            "source",
        ],
    },
    "market_snapshot": {
        "required": ["ticker", "exchange", "date"],
        "fields": [
            "company",
            "ticker",
            "exchange",
            "date",
            "market_cap",
            "float_market_cap",
            "pe",
            "pb",
            "turnover",
            "pct_chg_5d",
            "pct_chg_20d",
            "pct_chg_60d",
            "volume",
            "evidence_grade",
            "source",
        ],
    },
    "demand_indicators": {
        "required": ["indicator"],
        "fields": ["indicator", "value", "direction", "source", "evidence_grade", "caveat"],
    },
    "node_scores": {
        "required": [
            "node",
            "demand_pass_through",
            "supply_rigidity",
            "lead_time_pressure",
            "substitution_resistance",
            "concentration_pricing",
            "profit_pool_migration",
            "financial_confirmation",
        ],
        "fields": [
            "node",
            "demand_pass_through",
            "supply_rigidity",
            "lead_time_pressure",
            "substitution_resistance",
            "concentration_pricing",
            "profit_pool_migration",
            "financial_confirmation",
            "evidence_grade",
            "reason",
        ],
    },
    "source_evidence": {
        "required": ["claim", "source"],
        "fields": [
            "claim",
            "claim_type",
            "entity",
            "source",
            "url_or_file",
            "date",
            "evidence_grade",
            "limitation",
        ],
    },
}

TABLE_ALIASES = {
    "leaders": "global_leaders",
    "globalleader": "global_leaders",
    "globalleaders": "global_leaders",
    "overseasleaders": "global_leaders",
    "chainnodes": "supply_chain_nodes",
    "nodes": "supply_chain_nodes",
    "bomnodes": "supply_chain_nodes",
    "supplychainnodes": "supply_chain_nodes",
    "stockcandidates": "china_candidates",
    "candidates": "china_candidates",
    "chinacandidates": "china_candidates",
    "asharecandidates": "china_candidates",
    "financials": "financial_validation",
    "financialvalidation": "financial_validation",
    "market": "market_snapshot",
    "marketsnapshot": "market_snapshot",
    "quotes": "market_snapshot",
    "demand": "demand_indicators",
    "demandindicators": "demand_indicators",
    "scores": "node_scores",
    "nodescores": "node_scores",
    "evidence": "source_evidence",
    "sourceevidence": "source_evidence",
}

HEADER_ALIASES = {
    "name": "company",
    "companyname": "company",
    "公司": "company",
    "公司名称": "company",
    "ticker": "ticker",
    "symbol": "ticker",
    "code": "ticker",
    "证券代码": "ticker",
    "代码": "ticker",
    "exchange": "exchange",
    "market": "exchange",
    "交易所": "exchange",
    "country": "country",
    "国家": "country",
    "node": "node",
    "节点": "node",
    "环节": "node",
    "linkednode": "linked_node",
    "关联节点": "linked_node",
    "关联环节": "linked_node",
    "对应节点": "linked_node",
    "layer": "layer",
    "层级": "layer",
    "segmentexposure": "segment_exposure",
    "业务敞口": "segment_exposure",
    "产品敞口": "segment_exposure",
    "revenuemix": "revenue_mix",
    "收入结构": "revenue_mix",
    "bomshare": "BOM_or_value_share",
    "bomorvalueshare": "BOM_or_value_share",
    "valueshare": "BOM_or_value_share",
    "价值量": "BOM_or_value_share",
    "bom价值": "BOM_or_value_share",
    "leadtime": "lead_time",
    "交期": "lead_time",
    "交货时滞": "lead_time",
    "capacityrigidity": "capacity_rigidity",
    "供给刚性": "capacity_rigidity",
    "substitutionelasticity": "substitution_elasticity",
    "替代弹性": "substitution_elasticity",
    "topplayers": "top_players",
    "leaders": "top_players",
    "龙头": "top_players",
    "marketshare": "market_share",
    "市占率": "market_share",
    "pricingmechanism": "pricing_mechanism",
    "定价机制": "pricing_mechanism",
    "backlogororders": "backlog_or_orders",
    "订单": "backlog_or_orders",
    "在手订单": "backlog_or_orders",
    "guidance": "backlog_or_orders",
    "指引": "backlog_or_orders",
    "evidencegrade": "evidence_grade",
    "evidence": "evidence_grade",
    "证据等级": "evidence_grade",
    "source": "source",
    "来源": "source",
    "grossmargin": "gross_margin",
    "毛利率": "gross_margin",
    "netmargin": "net_margin",
    "净利率": "net_margin",
    "marketcap": "market_cap",
    "市值": "market_cap",
    "floatmarketcap": "float_market_cap",
    "流通市值": "float_market_cap",
    "valuation": "valuation",
    "估值": "valuation",
    "pricetrend": "price_trend",
    "股价趋势": "price_trend",
    "period": "period",
    "报告期": "period",
    "期间": "period",
    "revenue": "revenue",
    "营收": "revenue",
    "收入": "revenue",
    "turnover": "turnover",
    "换手率": "turnover",
    "receivablesturnover": "receivables_turnover",
    "应收账款周转率": "receivables_turnover",
    "inventoryturnover": "inventory_turnover",
    "存货周转率": "inventory_turnover",
    "operatingcashflow": "operating_cash_flow",
    "经营现金流": "operating_cash_flow",
    "debtornetcash": "debt_or_net_cash",
    "净现金": "debt_or_net_cash",
    "有息负债": "debt_or_net_cash",
    "date": "date",
    "日期": "date",
    "pe": "pe",
    "市盈率": "pe",
    "pb": "pb",
    "市净率": "pb",
    "volume": "volume",
    "成交量": "volume",
    "pctchg5d": "pct_chg_5d",
    "5日涨跌幅": "pct_chg_5d",
    "5日涨幅": "pct_chg_5d",
    "pctchg20d": "pct_chg_20d",
    "20日涨跌幅": "pct_chg_20d",
    "20日涨幅": "pct_chg_20d",
    "pctchg60d": "pct_chg_60d",
    "60日涨跌幅": "pct_chg_60d",
    "60日涨幅": "pct_chg_60d",
    "exposureevidence": "exposure_evidence",
    "敞口证据": "exposure_evidence",
    "业务证据": "exposure_evidence",
    "pureplaylevel": "pure_play_level",
    "纯度": "pure_play_level",
    "revenuemateriality": "revenue_materiality",
    "收入占比": "revenue_materiality",
    "fundamentalquality": "fundamental_quality",
    "基本面质量": "fundamental_quality",
    "earningselasticity": "earnings_elasticity",
    "业绩弹性": "earnings_elasticity",
    "tradingelasticity": "trading_elasticity",
    "交易弹性": "trading_elasticity",
    "verdict": "verdict",
    "结论": "verdict",
    "indicator": "indicator",
    "指标": "indicator",
    "value": "value",
    "值": "value",
    "direction": "direction",
    "方向": "direction",
    "caveat": "caveat",
    "风险提示": "caveat",
    "claim": "claim",
    "主张": "claim",
    "claimtype": "claim_type",
    "主张类型": "claim_type",
    "entity": "entity",
    "实体": "entity",
    "urlorfile": "url_or_file",
    "链接或文件": "url_or_file",
    "limitation": "limitation",
    "限制": "limitation",
}

SUPPORTED_SUFFIXES = {".csv", ".json", ".jsonl", ".xlsx"}


def _key(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", value).lower()


def canonical_table(name: str | None) -> str | None:
    if not name:
        return None
    raw = name.strip()
    if raw in TABLES:
        return raw
    compact = _key(raw)
    if compact in TABLE_ALIASES:
        return TABLE_ALIASES[compact]
    snake = re.sub(r"[^0-9A-Za-z]+", "_", raw).strip("_").lower()
    return snake if snake in TABLES else None


def canonical_header(name: str) -> str:
    raw = name.strip()
    if raw in {field for spec in TABLES.values() for field in spec["fields"]}:
        return raw
    compact = _key(raw)
    if compact in HEADER_ALIASES:
        return HEADER_ALIASES[compact]
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", raw).strip("_").lower() or "unnamed"


def table_header(table: str, key: str) -> str:
    allowed = set(TABLES[table]["fields"])
    if key in allowed:
        return key
    table_specific = {
        "global_leaders": {
            "node": "linked_node",
            "revenue_materiality": "revenue_mix",
        },
        "china_candidates": {
            "node": "linked_node",
        },
    }
    return table_specific.get(table, {}).get(key, key)


def normalize_grade(value: object) -> str:
    grade = str(value or "N/A").strip().upper()
    if grade in {"A", "B", "C"}:
        return grade
    if grade in {"", "NA", "N/A", "NONE", "NULL"}:
        return "N/A"
    return "N/A"


def clean_value(value: object) -> object:
    if value is None:
        return "N/A"
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else "N/A"
    return value


def read_csv_rows(handle: Iterable[str]) -> list[dict[str, object]]:
    reader = csv.DictReader(handle)
    if not reader.fieldnames:
        return []
    return [dict(row) for row in reader]


def read_json_rows(path: Path, table_hint: str | None) -> Iterator[tuple[str | None, list[dict[str, object]]]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        yield table_hint or canonical_table(path.stem), data
    elif isinstance(data, dict):
        if all(isinstance(value, list) for value in data.values()):
            for key, value in data.items():
                yield canonical_table(key) or key, value
        else:
            yield table_hint or canonical_table(path.stem), [data]
    else:
        raise ValueError(f"unsupported JSON root in {path}")


def read_jsonl_rows(path: Path, table_hint: str | None) -> Iterator[tuple[str | None, list[dict[str, object]]]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        stripped = line.strip()
        if stripped:
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL line {line_no} is not an object")
            rows.append(value)
    yield table_hint or canonical_table(path.stem), rows


def read_xlsx_rows(path: Path) -> Iterator[tuple[str | None, list[dict[str, object]]]]:
    try:
        import openpyxl  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("openpyxl is required for .xlsx input") from exc

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for sheet in workbook.worksheets:
        values = list(sheet.iter_rows(values_only=True))
        if not values:
            continue
        header_index = next((idx for idx, row in enumerate(values) if any(cell is not None for cell in row)), None)
        if header_index is None:
            continue
        headers = [str(cell).strip() if cell is not None else "" for cell in values[header_index]]
        rows = []
        for raw_row in values[header_index + 1 :]:
            if not any(cell is not None for cell in raw_row):
                continue
            rows.append({headers[idx]: cell for idx, cell in enumerate(raw_row) if idx < len(headers) and headers[idx]})
        yield canonical_table(sheet.title), rows


def normalize_row(table: str, row: dict[str, object], source: str, index: int, issues: list[dict[str, object]]) -> dict[str, object]:
    spec = TABLES[table]
    mapped: dict[str, object] = {}
    extra: dict[str, object] = {}
    allowed = set(spec["fields"])

    for header, value in row.items():
        key = table_header(table, canonical_header(str(header)))
        cleaned = clean_value(value)
        if key in allowed:
            mapped[key] = cleaned
        else:
            extra[key] = cleaned

    for field in spec["fields"]:
        mapped.setdefault(field, "N/A")

    if "evidence_grade" in mapped:
        mapped["evidence_grade"] = normalize_grade(mapped["evidence_grade"])

    missing = [field for field in spec["required"] if mapped.get(field) in {"", "N/A", None}]
    if missing:
        issues.append(
            {
                "level": "error",
                "table": table,
                "source": source,
                "row": index,
                "message": f"missing required fields: {', '.join(missing)}",
            }
        )
    if extra:
        mapped["_extra"] = extra

    return mapped


def add_rows(
    result: dict[str, list[dict[str, object]]],
    issues: list[dict[str, object]],
    table_name: str | None,
    rows: list[dict[str, object]],
    source: str,
) -> None:
    table = canonical_table(table_name) if table_name else None
    if table not in TABLES:
        issues.append(
            {
                "level": "error",
                "table": table_name or "unknown",
                "source": source,
                "message": "unknown table; use --table or a supported filename/sheet name",
            }
        )
        return
    for idx, row in enumerate(rows, 1):
        result.setdefault(table, []).append(normalize_row(table, row, source, idx, issues))


def iter_inputs(inputs: list[str], table_hint: str | None) -> Iterator[tuple[str | None, list[dict[str, object]], str]]:
    for raw in inputs:
        if raw == "-":
            if not table_hint:
                raise ValueError("--table is required when reading CSV from stdin")
            yield table_hint, read_csv_rows(sys.stdin), "stdin"
            continue

        path = Path(raw)
        if path.is_dir():
            files = sorted(p for p in path.iterdir() if p.suffix.lower() in SUPPORTED_SUFFIXES)
        else:
            files = [path]

        for file in files:
            suffix = file.suffix.lower()
            if suffix == ".csv":
                with file.open("r", encoding="utf-8-sig", newline="") as handle:
                    yield table_hint or canonical_table(file.stem), read_csv_rows(handle), str(file)
            elif suffix == ".json":
                yield from ((table, rows, str(file)) for table, rows in read_json_rows(file, table_hint))
            elif suffix == ".jsonl":
                yield from ((table, rows, str(file)) for table, rows in read_jsonl_rows(file, table_hint))
            elif suffix == ".xlsx":
                yield from ((table, rows, str(file)) for table, rows in read_xlsx_rows(file))
            else:
                raise ValueError(f"unsupported input type: {file}")


def build_output(inputs: list[str], table_hint: str | None) -> dict[str, object]:
    issues: list[dict[str, object]] = []
    tables: dict[str, list[dict[str, object]]] = {name: [] for name in TABLES}
    for table_name, rows, source in iter_inputs(inputs, table_hint):
        add_rows(tables, issues, table_name, rows, source)
    tables = {name: rows for name, rows in tables.items() if rows}
    return {
        "schema_version": "industry-chain-data-v1",
        "tables": tables,
        "issues": issues,
        "table_counts": {name: len(rows) for name, rows in tables.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize industry-chain research inputs into canonical JSON.")
    parser.add_argument("--input", nargs="+", help="Input file(s), directory, or '-' for stdin CSV.")
    parser.add_argument("--table", help="Table name for stdin, list-style JSON, or single CSV files.")
    parser.add_argument("--out", type=Path, help="Optional output JSON path.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when validation issues are found.")
    parser.add_argument("--list-tables", action="store_true", help="Print supported table names and exit.")
    args = parser.parse_args()

    if args.list_tables:
        print(json.dumps(sorted(TABLES), ensure_ascii=False, indent=2))
        return 0

    if not args.input:
        parser.error("--input is required unless --list-tables is used")

    try:
        output = build_output(args.input, args.table)
    except Exception as exc:  # noqa: BLE001 - command-line tool should print user-facing errors.
        print(f"error: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

    if args.strict and output["issues"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
