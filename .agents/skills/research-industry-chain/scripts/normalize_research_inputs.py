#!/usr/bin/env python3
"""Normalize industry-chain research input files into canonical JSON tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Iterator


COMMERCIALIZATION_STAGES = {
    "rd_plan",
    "sampling",
    "validation",
    "design_win",
    "qualification",
    "mass_production",
    "shipment",
    "revenue",
    "profit_cashflow",
}

BOTTLENECK_SEVERITIES = {"hard_bottleneck", "soft_bottleneck", "watch", "rejected"}
BOTTLENECK_STATUS_CHANGES = {
    "new",
    "upgraded",
    "unchanged",
    "downgraded",
    "resolved",
    "rejected",
}
FUTURE_CURRENT_STATUSES = {
    "hard_bottleneck",
    "soft_bottleneck",
    "watch",
    "downgraded",
    "resolved",
}
FUTURE_STATUSES = {"likely_future_bottleneck", "watch", "downgraded", "resolved"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
CANDIDATE_VERDICTS = {"main_candidate", "watch_only", "theme_adjacent", "reject"}
STAGE_CLAIM_WINDOWS = {"current", "historical"}
DEFAULT_STAGE_MAX_AGE_DAYS = 365
MAX_STAGE_MAX_AGE_DAYS = 365
DEFAULT_FUTURE_MAX_AGE_DAYS = 365
MAX_FUTURE_MAX_AGE_DAYS = 365
STAGE_SOURCE_TYPES = {
    "regulatory",
    "official",
    "company_original",
    "official_counterparty",
    "third_party",
    "social",
    "anonymous",
    "lead_only",
}
REALIZED_STAGE_SOURCE_TYPES = {
    "regulatory",
    "official",
    "company_original",
    "official_counterparty",
}
WEAK_STAGE_SOURCE_TYPES = {"social", "anonymous", "lead_only"}
FUTURE_SOURCE_TYPES = {
    "regulatory",
    "official",
    "company_original",
    "official_counterparty",
    "credible_third_party",
    "social",
    "anonymous",
    "lead_only",
}
CREDIBLE_FUTURE_SOURCE_TYPES = {
    "regulatory",
    "official",
    "company_original",
    "official_counterparty",
    "credible_third_party",
}
WEAK_FUTURE_SOURCE_TYPES = {"social", "anonymous", "lead_only"}
BOTTLENECK_SOURCE_TYPES = {
    "regulatory",
    "official",
    "company_original",
    "official_counterparty",
    "credible_third_party",
    "social",
    "anonymous",
    "lead_only",
}
EVIDENCE_REVIEW_STATUSES = {
    "eligible_for_bottleneck_review",
    "ineligible_for_claimed_severity",
    "incomplete",
    "watch_only",
}
EVIDENCE_KINDS = {
    "demand": {"quantified_demand", "demand_step", "qualitative_signal"},
    "supply": {
        "qualified_supply_limit",
        "usable_capacity_limit",
        "yield_limit",
        "delivery_limit",
        "certified_supplier_limit",
        "qualitative_constraint",
    },
}
CLAIM_WINDOWS = {"current", "future", "historical"}
DEFAULT_BOTTLENECK_MAX_AGE_DAYS = 180
MAX_BOTTLENECK_MAX_AGE_DAYS = 365

SEMANTIC_PLACEHOLDERS = {
    "",
    "-",
    "--",
    "—",
    "–",
    "n/a",
    "na",
    "null",
    "unknown",
    "not_mentioned",
    "evidence_absent",
    "not_available",
    "not_found",
    "blocked",
    "pending",
    "todo",
    "tbd",
    "missing",
    "unavailable",
    "待定",
    "待补",
    "待核验",
    "未找到",
    "未提及",
    "证据缺失",
    "暂无",
    "无数据",
    "缺失",
}

ENUM_FIELDS = {
    "bottleneck_ledger": {
        "severity": BOTTLENECK_SEVERITIES,
        "status_change": BOTTLENECK_STATUS_CHANGES,
        "evidence_review_status": EVIDENCE_REVIEW_STATUSES,
    },
    "future_bottleneck_scenarios": {
        "current_status": FUTURE_CURRENT_STATUSES,
        "future_status": FUTURE_STATUSES,
        "confidence": CONFIDENCE_LEVELS,
        "source_type": FUTURE_SOURCE_TYPES,
    },
    "china_candidates": {
        "commercialization_stage": COMMERCIALIZATION_STAGES,
        "stage_claim_window": STAGE_CLAIM_WINDOWS,
        "stage_source_type": STAGE_SOURCE_TYPES,
        "verdict": CANDIDATE_VERDICTS,
    },
    "bottleneck_evidence_checks": {
        "severity": BOTTLENECK_SEVERITIES,
        "claim_window": CLAIM_WINDOWS,
        "demand_evidence_kind": EVIDENCE_KINDS["demand"],
        "supply_evidence_kind": EVIDENCE_KINDS["supply"],
        "demand_source_type": BOTTLENECK_SOURCE_TYPES,
        "supply_source_type": BOTTLENECK_SOURCE_TYPES,
        "gap_source_type": BOTTLENECK_SOURCE_TYPES,
    },
}


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
            "physical_level",
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
    "bottleneck_ledger": {
        "required": [
            "bottleneck_node",
            "demand_evidence",
            "supply_evidence",
            "supply_gap_evidence",
            "constraint_mechanism",
            "severity",
            "time_horizon",
            "substitution_path",
            "second_source_status",
            "relief_window",
            "positive_validation",
            "counterevidence",
            "status_change",
            "key_reversal",
            "evidence_grade",
            "source",
        ],
        "fields": [
            "bottleneck_node",
            "claim_as_of",
            "evidence_check_id",
            "evidence_review_status",
            "affected_chain_layer",
            "demand_evidence",
            "supply_evidence",
            "supply_gap_evidence",
            "constraint_mechanism",
            "severity",
            "time_horizon",
            "substitution_path",
            "second_source_status",
            "relief_window",
            "positive_validation",
            "counterevidence",
            "prior_status",
            "status_change",
            "key_reversal",
            "evidence_grade",
            "source",
        ],
    },
    "future_bottleneck_scenarios": {
        "required": ["node", "future_status", "demand_trigger", "supply_lag_mechanism"],
        "fields": [
            "node",
            "current_status",
            "future_status",
            "demand_trigger",
            "supply_lag_mechanism",
            "likely_timing",
            "confidence",
            "evidence_gap",
            "reversal_indicator",
            "evidence_date",
            "future_max_age_days",
            "source_type",
            "source_locator",
            "evidence_grade",
            "source",
        ],
    },
    "china_candidates": {
        "required": [
            "company",
            "ticker",
            "exchange",
            "linked_node",
            "exposure_evidence",
            "commercialization_stage",
            "stage_evidence",
            "stage_evidence_date",
            "stage_claim_window",
            "stage_source",
            "stage_source_type",
            "stage_source_locator",
            "evidence_grade",
            "verdict",
        ],
        "fields": [
            "company",
            "ticker",
            "exchange",
            "linked_node",
            "exposure_evidence",
            "commercialization_stage",
            "stage_evidence",
            "stage_evidence_date",
            "stage_claim_window",
            "stage_max_age_days",
            "stage_source",
            "stage_source_type",
            "stage_source_locator",
            "pure_play_level",
            "revenue_materiality",
            "evidence_gap",
            "fundamental_quality",
            "earnings_elasticity",
            "trading_elasticity",
            "verdict",
            "inclusion_reason",
            "rejection_reason",
            "next_evidence",
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
    "bottleneck_evidence_checks": {
        "required": [
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
        ],
        "fields": [
            "check_id",
            "node",
            "severity",
            "claim_window",
            "claim_as_of",
            "max_age_days",
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
            "evidence_grade",
            "source",
            "source_date",
            "counterevidence",
            "substitution_path",
            "second_source_status",
            "relief_window",
            "positive_validation",
            "key_reversal",
            "review_status",
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
    "bottleneckledger": "bottleneck_ledger",
    "bottlenecks": "bottleneck_ledger",
    "currentbottlenecks": "bottleneck_ledger",
    "chokepoints": "bottleneck_ledger",
    "堵点台账": "bottleneck_ledger",
    "卡点台账": "bottleneck_ledger",
    "futurebottlenecks": "future_bottleneck_scenarios",
    "futurebottleneckscenarios": "future_bottleneck_scenarios",
    "bottleneckscenarios": "future_bottleneck_scenarios",
    "未来卡点": "future_bottleneck_scenarios",
    "未来堵点": "future_bottleneck_scenarios",
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
    "bottleneckevidencechecks": "bottleneck_evidence_checks",
    "bottleneckchecks": "bottleneck_evidence_checks",
    "瓶颈证据检查": "bottleneck_evidence_checks",
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
    "physicallevel": "physical_level",
    "物理层级": "physical_level",
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
    "bottlenecknode": "bottleneck_node",
    "堵点": "bottleneck_node",
    "卡点": "bottleneck_node",
    "evidencecheckid": "evidence_check_id",
    "证据检查id": "evidence_check_id",
    "证据包id": "evidence_check_id",
    "evidencereviewstatus": "evidence_review_status",
    "证据评审状态": "evidence_review_status",
    "checkid": "check_id",
    "检查id": "check_id",
    "affectedchainlayer": "affected_chain_layer",
    "影响层级": "affected_chain_layer",
    "demandevidence": "demand_evidence",
    "需求证据": "demand_evidence",
    "supplyevidence": "supply_evidence",
    "供给证据": "supply_evidence",
    "supplygapevidence": "supply_gap_evidence",
    "供应缺口证据": "supply_gap_evidence",
    "缺口证据": "supply_gap_evidence",
    "constraintmechanism": "constraint_mechanism",
    "约束机制": "constraint_mechanism",
    "卡点机制": "constraint_mechanism",
    "evidencedetail": "evidence",
    "evidencenote": "evidence",
    "证据内容": "evidence",
    "severity": "severity",
    "严重程度": "severity",
    "claimwindow": "claim_window",
    "声明窗口": "claim_window",
    "claimasof": "claim_as_of",
    "声明时点": "claim_as_of",
    "demandevidencedate": "demand_evidence_date",
    "需求证据日期": "demand_evidence_date",
    "demandsourcetype": "demand_source_type",
    "需求来源类型": "demand_source_type",
    "demandsourcelocator": "demand_source_locator",
    "需求来源定位": "demand_source_locator",
    "supplyevidencedate": "supply_evidence_date",
    "供给证据日期": "supply_evidence_date",
    "supplysourcetype": "supply_source_type",
    "供给来源类型": "supply_source_type",
    "supplysourcelocator": "supply_source_locator",
    "供给来源定位": "supply_source_locator",
    "gapevidencedate": "gap_evidence_date",
    "缺口证据日期": "gap_evidence_date",
    "gapsourcetype": "gap_source_type",
    "缺口来源类型": "gap_source_type",
    "gapsourcelocator": "gap_source_locator",
    "缺口来源定位": "gap_source_locator",
    "sourcedate": "source_date",
    "来源日期": "source_date",
    "maxagedays": "max_age_days",
    "最大证据年龄天数": "max_age_days",
    "demand_evidence_kind": "demand_evidence_kind",
    "demandevidencekind": "demand_evidence_kind",
    "需求证据类型": "demand_evidence_kind",
    "supply_evidence_kind": "supply_evidence_kind",
    "supplyevidencekind": "supply_evidence_kind",
    "供给证据类型": "supply_evidence_kind",
    "directgapconsequence": "direct_gap_consequence",
    "直接缺口后果": "direct_gap_consequence",
    "timehorizon": "time_horizon",
    "时间维度": "time_horizon",
    "substitutionpath": "substitution_path",
    "替代路径": "substitution_path",
    "secondsourcestatus": "second_source_status",
    "第二供应商状态": "second_source_status",
    "二供状态": "second_source_status",
    "reliefwindow": "relief_window",
    "缓解窗口": "relief_window",
    "positivevalidation": "positive_validation",
    "正面验证": "positive_validation",
    "counterevidence": "counterevidence",
    "反证": "counterevidence",
    "priorstatus": "prior_status",
    "前次状态": "prior_status",
    "statuschange": "status_change",
    "状态变化": "status_change",
    "keyreversal": "key_reversal",
    "反转因素": "key_reversal",
    "关键反转": "key_reversal",
    "currentstatus": "current_status",
    "当前状态": "current_status",
    "futurestatus": "future_status",
    "未来状态": "future_status",
    "demandtrigger": "demand_trigger",
    "需求触发": "demand_trigger",
    "supplylagmechanism": "supply_lag_mechanism",
    "供给滞后机制": "supply_lag_mechanism",
    "trigger": "demand_trigger",
    "触发因素": "demand_trigger",
    "likelytiming": "likely_timing",
    "预计时间": "likely_timing",
    "confidence": "confidence",
    "置信度": "confidence",
    "evidencegap": "evidence_gap",
    "证据缺口": "evidence_gap",
    "reversalindicator": "reversal_indicator",
    "反转指标": "reversal_indicator",
    "evidencedate": "evidence_date",
    "证据日期": "evidence_date",
    "sourcetype": "source_type",
    "来源类型": "source_type",
    "sourcelocator": "source_locator",
    "来源定位": "source_locator",
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
    "commercializationstage": "commercialization_stage",
    "商业化阶段": "commercialization_stage",
    "stageevidence": "stage_evidence",
    "阶段证据": "stage_evidence",
    "stageevidencedate": "stage_evidence_date",
    "阶段日期": "stage_evidence_date",
    "stageclaimwindow": "stage_claim_window",
    "阶段声明窗口": "stage_claim_window",
    "stagemaxagedays": "stage_max_age_days",
    "阶段最大证据年龄天数": "stage_max_age_days",
    "futuremaxagedays": "future_max_age_days",
    "未来证据最大年龄天数": "future_max_age_days",
    "stagesource": "stage_source",
    "阶段来源": "stage_source",
    "stagesourcetype": "stage_source_type",
    "阶段来源类型": "stage_source_type",
    "stagesourcelocator": "stage_source_locator",
    "阶段来源定位": "stage_source_locator",
    "阶段证据定位": "stage_source_locator",
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
    "inclusionreason": "inclusion_reason",
    "纳入理由": "inclusion_reason",
    "rejectionreason": "rejection_reason",
    "淘汰理由": "rejection_reason",
    "nextevidence": "next_evidence",
    "下一验证证据": "next_evidence",
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
        "bottleneck_ledger": {
            "node": "bottleneck_node",
            "linked_node": "bottleneck_node",
            "evidence": "supply_gap_evidence",
        },
        "future_bottleneck_scenarios": {
            "trigger": "demand_trigger",
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


def _placeholder_key(value: str) -> str:
    text = value.strip().casefold()
    if text in {"-", "--", "—", "–"}:
        return text
    return re.sub(r"[\s_-]+", "_", text)


SEMANTIC_PLACEHOLDER_KEYS = {_placeholder_key(value) for value in SEMANTIC_PLACEHOLDERS}


def is_semantic_placeholder(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return _placeholder_key(value) in SEMANTIC_PLACEHOLDER_KEYS


def normalize_iso_date_or_timestamp(value: object) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    text = value.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            date.fromisoformat(text)
        elif "T" in text:
            datetime.fromisoformat(text.replace("Z", "+00:00"))
        else:
            return None
    except ValueError:
        return None
    return text


def iso_calendar_date(value: object) -> date | None:
    normalized = normalize_iso_date_or_timestamp(value)
    if normalized is None:
        return None
    if "T" in normalized:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00")).date()
    return date.fromisoformat(normalized)


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


def normalize_row(
    table: str,
    row: dict[str, object],
    source: str,
    index: int,
    issues: list[dict[str, object]],
    as_of: date,
) -> dict[str, object]:
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

    def add_error(message: str) -> None:
        issues.append(
            {
                "level": "error",
                "table": table,
                "source": source,
                "row": index,
                "message": message,
            }
        )

    for field, allowed_values in ENUM_FIELDS.get(table, {}).items():
        value = mapped.get(field)
        if is_semantic_placeholder(value):
            if field not in spec["required"] and value != "N/A":
                add_error(f"invalid {field}: {value}")
            continue
        if value not in allowed_values:
            add_error(f"invalid {field}: {value}")

    if table == "bottleneck_ledger":
        ledger_claim_as_of = mapped.get("claim_as_of")
        if not is_semantic_placeholder(ledger_claim_as_of):
            normalized_date = normalize_iso_date_or_timestamp(ledger_claim_as_of)
            if normalized_date is None:
                add_error(f"invalid claim_as_of: {ledger_claim_as_of}")
            else:
                mapped["claim_as_of"] = normalized_date
                claim_date = iso_calendar_date(normalized_date)
                if claim_date is not None and claim_date > as_of:
                    add_error(f"claim_as_of cannot be after as_of {as_of.isoformat()}")

    if table == "china_candidates":
        stage_date = mapped.get("stage_evidence_date")
        stage_calendar_date: date | None = None
        if not is_semantic_placeholder(stage_date):
            normalized_date = normalize_iso_date_or_timestamp(stage_date)
            if normalized_date is None:
                add_error(f"invalid stage_evidence_date: {stage_date}")
            else:
                mapped["stage_evidence_date"] = normalized_date
                stage_calendar_date = iso_calendar_date(normalized_date)
                if stage_calendar_date is not None and stage_calendar_date > as_of:
                    add_error(
                        f"stage_evidence_date cannot be after as_of {as_of.isoformat()}"
                    )

        raw_stage_max_age = mapped.get("stage_max_age_days")
        stage_max_age_days = DEFAULT_STAGE_MAX_AGE_DAYS
        if is_semantic_placeholder(raw_stage_max_age):
            mapped["stage_max_age_days"] = stage_max_age_days
        else:
            normalized_stage_max_age: int | None = None
            if isinstance(raw_stage_max_age, bool):
                normalized_stage_max_age = None
            elif isinstance(raw_stage_max_age, int):
                normalized_stage_max_age = raw_stage_max_age
            elif isinstance(raw_stage_max_age, float) and raw_stage_max_age.is_integer():
                normalized_stage_max_age = int(raw_stage_max_age)
            elif isinstance(raw_stage_max_age, str) and re.fullmatch(
                r"[+-]?\d+", raw_stage_max_age.strip()
            ):
                normalized_stage_max_age = int(raw_stage_max_age)

            if (
                normalized_stage_max_age is None
                or not 1 <= normalized_stage_max_age <= MAX_STAGE_MAX_AGE_DAYS
            ):
                add_error(
                    "stage_max_age_days must be an integer between 1 and "
                    f"{MAX_STAGE_MAX_AGE_DAYS}"
                )
            else:
                stage_max_age_days = normalized_stage_max_age
                mapped["stage_max_age_days"] = stage_max_age_days

        stage = mapped.get("commercialization_stage")
        stage_claim_window = mapped.get("stage_claim_window")
        verdict = mapped.get("verdict")
        stage_source_type = mapped.get("stage_source_type")
        if stage_calendar_date is not None and stage_calendar_date <= as_of:
            stage_age_days = (as_of - stage_calendar_date).days
            if stage_age_days > stage_max_age_days and not (
                stage_claim_window == "historical"
                and verdict in {"watch_only", "theme_adjacent", "reject"}
            ):
                add_error(
                    f"stage evidence older than {stage_max_age_days} days must be "
                    "historical and watch_only|theme_adjacent|reject"
                )
        if stage_claim_window == "historical" and verdict == "main_candidate":
            add_error("historical stage evidence cannot support main_candidate")
        if stage in {"revenue", "profit_cashflow"} or verdict == "main_candidate":
            if is_semantic_placeholder(mapped.get("source")):
                add_error("revenue/main_candidate requires a non-placeholder source")
            if stage_source_type not in REALIZED_STAGE_SOURCE_TYPES:
                add_error(
                    "revenue/profit_cashflow or main_candidate requires stage_source_type "
                    "regulatory|official|company_original|official_counterparty"
                )
            if mapped.get("evidence_grade") != "A":
                add_error("revenue/profit_cashflow or main_candidate requires A-grade evidence")
            if is_semantic_placeholder(mapped.get("stage_source_locator")):
                add_error(
                    "revenue/profit_cashflow or main_candidate requires a traceable stage_source_locator"
                )
        if stage_source_type in WEAK_STAGE_SOURCE_TYPES and (
            stage in {"revenue", "profit_cashflow"} or verdict == "main_candidate"
        ):
            add_error(
                "social|anonymous|lead_only evidence cannot support a realized stage or main_candidate"
            )
        if stage in {"revenue", "profit_cashflow"} and is_semantic_placeholder(
            mapped.get("revenue_materiality")
        ):
            if verdict == "main_candidate":
                add_error("revenue main_candidate requires non-placeholder revenue_materiality")
            elif is_semantic_placeholder(mapped.get("evidence_gap")):
                add_error(
                    "revenue/profit_cashflow requires revenue_materiality or a non-placeholder evidence_gap"
                )

    if table == "future_bottleneck_scenarios":
        future_status = mapped.get("future_status")
        confidence = mapped.get("confidence")
        source_type = mapped.get("source_type")
        raw_future_max_age = mapped.get("future_max_age_days")
        future_max_age_days = DEFAULT_FUTURE_MAX_AGE_DAYS
        if is_semantic_placeholder(raw_future_max_age):
            mapped["future_max_age_days"] = future_max_age_days
        else:
            normalized_future_max_age: int | None = None
            if isinstance(raw_future_max_age, bool):
                normalized_future_max_age = None
            elif isinstance(raw_future_max_age, int):
                normalized_future_max_age = raw_future_max_age
            elif isinstance(raw_future_max_age, float) and raw_future_max_age.is_integer():
                normalized_future_max_age = int(raw_future_max_age)
            elif isinstance(raw_future_max_age, str) and re.fullmatch(
                r"[+-]?\d+", raw_future_max_age.strip()
            ):
                normalized_future_max_age = int(raw_future_max_age)
            if (
                normalized_future_max_age is None
                or not 1 <= normalized_future_max_age <= MAX_FUTURE_MAX_AGE_DAYS
            ):
                add_error(
                    "future_max_age_days must be an integer between 1 and "
                    f"{MAX_FUTURE_MAX_AGE_DAYS}"
                )
            else:
                future_max_age_days = normalized_future_max_age
                mapped["future_max_age_days"] = future_max_age_days

        evidence_date = mapped.get("evidence_date")
        evidence_calendar_date: date | None = None
        if not is_semantic_placeholder(evidence_date):
            normalized_date = normalize_iso_date_or_timestamp(evidence_date)
            if normalized_date is None:
                add_error(f"invalid evidence_date: {evidence_date}")
            else:
                mapped["evidence_date"] = normalized_date
                evidence_calendar_date = iso_calendar_date(normalized_date)
                if evidence_calendar_date is not None and evidence_calendar_date > as_of:
                    add_error(f"evidence_date cannot be after as_of {as_of.isoformat()}")
        if evidence_calendar_date is not None and evidence_calendar_date <= as_of:
            evidence_age_days = (as_of - evidence_calendar_date).days
            if evidence_age_days > future_max_age_days and not (
                future_status == "watch" and confidence == "low"
            ):
                add_error(
                    f"future evidence older than {future_max_age_days} days is limited "
                    "to low-confidence watch"
                )

        if future_status == "likely_future_bottleneck":
            required_for_likely = (
                "likely_timing",
                "confidence",
                "evidence_gap",
                "reversal_indicator",
                "evidence_date",
                "source_type",
                "source_locator",
                "source",
                "evidence_grade",
            )
            missing_likely = [
                field for field in required_for_likely if is_semantic_placeholder(mapped.get(field))
            ]
            if missing_likely:
                add_error(
                    "likely_future_bottleneck missing or placeholder fields: "
                    + ", ".join(missing_likely)
                )
        if confidence == "high" and mapped.get("evidence_grade") not in {"A", "B"}:
            add_error("high confidence requires A/B evidence_grade")
        if future_status == "likely_future_bottleneck" or confidence == "high":
            if source_type not in CREDIBLE_FUTURE_SOURCE_TYPES:
                add_error(
                    "likely/high future scenario requires regulatory|official|company_original|"
                    "official_counterparty|credible_third_party source_type"
                )
            if mapped.get("evidence_grade") not in {"A", "B"}:
                add_error("likely/high future scenario requires A/B evidence_grade")
            for field in ("evidence_date", "source_locator"):
                if is_semantic_placeholder(mapped.get(field)):
                    add_error(f"likely/high future scenario requires {field}")
        if source_type in WEAK_FUTURE_SOURCE_TYPES and not (
            future_status == "watch" and confidence == "low"
        ):
            add_error(
                "social|anonymous|lead_only future evidence is limited to low-confidence watch"
            )

    if table == "bottleneck_evidence_checks":
        packet_dates: dict[str, date] = {}
        for field in (
            "claim_as_of",
            "demand_evidence_date",
            "supply_evidence_date",
            "gap_evidence_date",
            "source_date",
        ):
            raw_date = mapped.get(field)
            if is_semantic_placeholder(raw_date):
                continue
            normalized_date = normalize_iso_date_or_timestamp(raw_date)
            if normalized_date is None:
                add_error(f"invalid {field}: {raw_date}")
            else:
                mapped[field] = normalized_date
                calendar_date = iso_calendar_date(normalized_date)
                if calendar_date is not None:
                    packet_dates[field] = calendar_date
                    if calendar_date > as_of:
                        add_error(f"{field} cannot be after as_of {as_of.isoformat()}")

        claim_date = packet_dates.get("claim_as_of")
        if claim_date is not None:
            for field in (
                "demand_evidence_date",
                "supply_evidence_date",
                "gap_evidence_date",
                "source_date",
            ):
                evidence_date = packet_dates.get(field)
                if evidence_date is not None and evidence_date > claim_date:
                    add_error(f"{field} cannot be after claim_as_of")

        raw_max_age = mapped.get("max_age_days")
        if is_semantic_placeholder(raw_max_age):
            mapped["max_age_days"] = DEFAULT_BOTTLENECK_MAX_AGE_DAYS
        else:
            normalized_max_age: int | None = None
            if isinstance(raw_max_age, bool):
                normalized_max_age = None
            elif isinstance(raw_max_age, int):
                normalized_max_age = raw_max_age
            elif isinstance(raw_max_age, float) and raw_max_age.is_integer():
                normalized_max_age = int(raw_max_age)
            elif isinstance(raw_max_age, str) and re.fullmatch(r"[+-]?\d+", raw_max_age.strip()):
                normalized_max_age = int(raw_max_age)

            if (
                normalized_max_age is None
                or not 1 <= normalized_max_age <= MAX_BOTTLENECK_MAX_AGE_DAYS
            ):
                add_error(
                    "max_age_days must be an integer between 1 and "
                    f"{MAX_BOTTLENECK_MAX_AGE_DAYS}"
                )
            else:
                mapped["max_age_days"] = normalized_max_age

        from validate_bottleneck_evidence import validate_row as review_bottleneck_row

        review_input = {
            field: str(value) if value is not None else ""
            for field, value in mapped.items()
            if field != "review_status"
        }
        mapped["review_status"] = review_bottleneck_row(review_input, as_of)[
            "review_status"
        ]

    if table in {"market_snapshot", "source_evidence"}:
        raw_date = mapped.get("date")
        if not is_semantic_placeholder(raw_date):
            normalized_date = normalize_iso_date_or_timestamp(raw_date)
            if normalized_date is None:
                add_error(f"invalid date: {raw_date}")
            else:
                mapped["date"] = normalized_date
                if iso_calendar_date(normalized_date) > as_of:
                    add_error(f"date cannot be after as_of {as_of.isoformat()}")

    missing = [
        field for field in spec["required"] if is_semantic_placeholder(mapped.get(field))
    ]
    if missing:
        add_error(f"missing or placeholder required fields: {', '.join(missing)}")
    if extra:
        mapped["_extra"] = extra

    return mapped


def add_rows(
    result: dict[str, list[dict[str, object]]],
    issues: list[dict[str, object]],
    table_name: str | None,
    rows: list[dict[str, object]],
    source: str,
    as_of: date,
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
        result.setdefault(table, []).append(
            normalize_row(table, row, source, idx, issues, as_of)
        )


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


def validate_bottleneck_companions(
    tables: dict[str, list[dict[str, object]]],
    issues: list[dict[str, object]],
    as_of: date,
) -> None:
    checks_by_id: dict[str, list[tuple[int, dict[str, object]]]] = {}
    for row_number, row in enumerate(tables.get("bottleneck_evidence_checks", []), 1):
        check_id = str(row.get("check_id", "")).strip()
        if not is_semantic_placeholder(check_id):
            checks_by_id.setdefault(check_id, []).append((row_number, row))

    for check_id, matches in checks_by_id.items():
        if len(matches) > 1:
            issues.append(
                {
                    "level": "error",
                    "table": "bottleneck_evidence_checks",
                    "source": "normalized packet",
                    "message": f"check_id must be unique: {check_id}",
                }
            )

    for row_number, ledger in enumerate(tables.get("bottleneck_ledger", []), 1):
        severity = str(ledger.get("severity", "")).strip()
        if severity not in {"hard_bottleneck", "soft_bottleneck"}:
            continue

        check_id = str(ledger.get("evidence_check_id", "")).strip()
        claimed_review = str(ledger.get("evidence_review_status", "")).strip()
        ledger_claim_as_of = str(ledger.get("claim_as_of", "")).strip()

        def add_link_error(message: str) -> None:
            issues.append(
                {
                    "level": "error",
                    "table": "bottleneck_ledger",
                    "source": "normalized packet",
                    "row": row_number,
                    "message": message,
                }
            )

        if (
            is_semantic_placeholder(check_id)
            or is_semantic_placeholder(claimed_review)
            or is_semantic_placeholder(ledger_claim_as_of)
        ):
            add_link_error(
                "hard/soft bottleneck_ledger requires claim_as_of, evidence_check_id, and "
                "evidence_review_status; otherwise use watch/rejected"
            )
            continue

        matches = checks_by_id.get(check_id, [])
        if len(matches) != 1:
            add_link_error(
                f"evidence_check_id must uniquely match bottleneck_evidence_checks.check_id: {check_id}"
            )
            continue

        _, check = matches[0]
        check_review = str(check.get("review_status", "")).strip()
        if str(check.get("node", "")).strip() != str(
            ledger.get("bottleneck_node", "")
        ).strip():
            add_link_error("linked evidence check node must equal bottleneck_node")
        if str(check.get("severity", "")).strip() != severity:
            add_link_error("linked evidence check severity must equal ledger severity")
        if str(check.get("claim_window", "")).strip() != "current":
            add_link_error(
                "hard/soft bottleneck_ledger requires a current claim_window companion; "
                "route future scenarios separately and keep historical records watch/rejected"
            )
        check_claim_as_of = iso_calendar_date(check.get("claim_as_of"))
        ledger_claim_date = iso_calendar_date(ledger_claim_as_of)
        if check_claim_as_of != as_of or ledger_claim_date != as_of:
            add_link_error(
                "current hard/soft ledger and companion claim_as_of must equal top-level as_of"
            )
        if check_claim_as_of != ledger_claim_date:
            add_link_error("ledger claim_as_of must equal companion claim_as_of")
        if str(check.get("time_horizon", "")).strip() != str(
            ledger.get("time_horizon", "")
        ).strip():
            add_link_error("ledger time_horizon must equal companion time_horizon")
        if claimed_review != check_review:
            add_link_error(
                "evidence_review_status must equal the normalizer-computed check review_status"
            )
        if check_review != "eligible_for_bottleneck_review":
            add_link_error(
                "hard/soft bottleneck_ledger requires an eligible_for_bottleneck_review companion"
            )


def build_output(
    inputs: list[str], table_hint: str | None, as_of: date
) -> dict[str, object]:
    issues: list[dict[str, object]] = []
    tables: dict[str, list[dict[str, object]]] = {name: [] for name in TABLES}
    for table_name, rows, source in iter_inputs(inputs, table_hint):
        add_rows(tables, issues, table_name, rows, source, as_of)
    validate_bottleneck_companions(tables, issues, as_of)
    tables = {name: rows for name, rows in tables.items() if rows}
    return {
        "schema_version": "industry-chain-data-v2",
        "as_of": as_of.isoformat(),
        "tables": tables,
        "issues": issues,
        "table_counts": {name: len(rows) for name, rows in tables.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize industry-chain research inputs into canonical JSON.")
    parser.add_argument("--input", nargs="+", help="Input file(s), directory, or '-' for stdin CSV.")
    parser.add_argument("--table", help="Table name for stdin, list-style JSON, or single CSV files.")
    parser.add_argument(
        "--as-of",
        help="Required deterministic research cutoff date in YYYY-MM-DD format.",
    )
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
    if not args.as_of:
        parser.error("--as-of is required unless --list-tables is used")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.as_of):
        parser.error("--as-of must use YYYY-MM-DD")
    try:
        as_of = date.fromisoformat(args.as_of)
    except ValueError:
        parser.error("--as-of must be a valid YYYY-MM-DD date")

    try:
        output = build_output(args.input, args.table, as_of)
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
