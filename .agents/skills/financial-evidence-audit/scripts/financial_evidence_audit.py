#!/usr/bin/env python3
"""Deterministic, fail-closed financial evidence audit for investment research."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import date, datetime
from decimal import (
    Decimal,
    DecimalException,
    Inexact,
    InvalidOperation,
    Rounded,
    localcontext,
)
import hashlib
from io import StringIO
import json
import re
import sys
import tokenize
from pathlib import Path
from typing import Any, Iterable


TOOL_VERSION = "1.4.1"
SCHEMA_VERSION = "1.0"
DECIMAL_PRECISION = 50
MAX_EXPRESSION_LENGTH = 512
MAX_AST_NODES = 128
MAX_POWER = 1000
MAX_DECIMAL_DIGITS = 200
MAX_ADJUSTED_EXPONENT = 10_000

DECIMAL_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
MONETARY_UNITS = {"currency", "currency_per_share"}
NONMONETARY_UNITS = {"share", "percent", "ratio", "multiple", "count"}
ALL_UNITS = MONETARY_UNITS | NONMONETARY_UNITS

OFFICIAL_TYPES = {
    "official_filing",
    "exchange",
    "regulator",
    "company_ir",
    "official_customer_supplier",
}
VENDOR_OR_OFFICIAL_TYPES = OFFICIAL_TYPES | {"market_data_vendor"}
ANY_CREDIBLE_TYPES = VENDOR_OR_OFFICIAL_TYPES | {"credible_secondary"}
ALL_SOURCE_TYPES = ANY_CREDIBLE_TYPES | {"lead_only", "report_under_audit"}
SOURCE_TIERS = {
    "official": OFFICIAL_TYPES,
    "vendor_or_official": VENDOR_OR_OFFICIAL_TYPES,
    "any_credible": ANY_CREDIBLE_TYPES,
}

CHECK_KINDS = {
    "cross_source",
    "market_cap",
    "expectation_gap",
    "expectation_surprise",
    "valuation",
    "percentage",
}
MULTIPLE_METRICS = {"pe_user_defined", "pe", "pb", "ps", "p_fcf"}
YIELD_METRICS = {"dividend_yield", "earnings_yield"}
VALUATION_METRICS = MULTIPLE_METRICS | YIELD_METRICS
PERIOD_FREQUENCIES = {"quarter", "half", "nine_month", "year", "ttm"}
PERIOD_SPAN_DAYS = {
    "quarter": (75, 110),
    "half": (160, 205),
    "nine_month": (250, 295),
    "year": (350, 380),
    "ttm": (350, 380),
}

PRICE_METRIC_BASES = {
    "close_price": {"unadjusted_close", "official_close"},
    "share_price": {"current_price", "official_close", "last_trade"},
    "current_price": {"current_price", "last_trade"},
}
MARKET_CAP_METRIC_BASES = {
    "total_market_cap": {"total_market_cap"},
    "free_float_market_cap": {"free_float_market_cap"},
}
VALUATION_FUNDAMENTAL_BASES = {
    "net_profit": {"ttm_net_profit", "fy_net_profit", "reported_consolidated_net_profit"},
    "attributable_net_profit": {
        "ttm_attributable_net_profit",
        "fy_attributable_net_profit",
        "reported_attributable_net_profit",
    },
    "deducted_attributable_net_profit": {
        "ttm_deducted_attributable_net_profit",
        "fy_deducted_attributable_net_profit",
    },
    "eps": {"ttm_eps", "fy_eps", "basic_eps", "diluted_eps"},
    "earnings_per_share": {"ttm_eps", "fy_eps", "basic_eps", "diluted_eps"},
    "equity_attributable_to_parent": {
        "equity_attributable_to_parent",
        "book_value_attributable_to_parent",
    },
    "book_value": {"book_value", "equity_attributable_to_parent"},
    "book_value_per_share": {"book_value_per_share"},
    "bvps": {"book_value_per_share", "bvps"},
    "revenue": {"ttm_revenue", "fy_revenue", "reported_consolidated_revenue"},
    "revenue_per_share": {"ttm_revenue_per_share", "fy_revenue_per_share"},
    "free_cash_flow": {"ttm_free_cash_flow", "fy_free_cash_flow"},
    "free_cash_flow_per_share": {
        "ttm_free_cash_flow_per_share",
        "fy_free_cash_flow_per_share",
    },
    "cash_dividend": {"ttm_cash_dividend", "fy_cash_dividend"},
    "dividend_per_share": {"ttm_dividend_per_share", "fy_dividend_per_share"},
}
FLOW_FUNDAMENTAL_METRICS = {
    "net_profit",
    "attributable_net_profit",
    "deducted_attributable_net_profit",
    "eps",
    "earnings_per_share",
    "revenue",
    "revenue_per_share",
    "free_cash_flow",
    "free_cash_flow_per_share",
    "cash_dividend",
    "dividend_per_share",
}
STOCK_FUNDAMENTAL_METRICS = {
    "equity_attributable_to_parent",
    "book_value",
    "book_value_per_share",
    "bvps",
}
RATIO_OUTPUT_METRICS = {
    ("gross_profit", "revenue"): "gross_margin_pct",
    ("operating_profit", "revenue"): "operating_margin_pct",
    ("net_profit", "revenue"): "net_margin_pct",
    ("attributable_net_profit", "revenue"): "attributable_net_margin_pct",
    (
        "deducted_attributable_net_profit",
        "revenue",
    ): "deducted_attributable_net_margin_pct",
    ("cash_dividend", "net_profit"): "dividend_payout_pct",
    ("cash_dividend", "attributable_net_profit"): "dividend_payout_pct",
    ("net_profit", "cash_dividend"): "dividend_coverage_pct",
    ("attributable_net_profit", "cash_dividend"): "dividend_coverage_pct",
    ("free_cash_flow", "cash_dividend"): "fcf_dividend_coverage_pct",
    ("operating_cash_flow", "cash_dividend"): (
        "operating_cash_flow_dividend_coverage_pct"
    ),
    ("cash_distribution", "affo"): "distribution_payout_pct",
    ("cash_distribution", "ffo"): "distribution_payout_pct",
    ("cash_distribution", "distributable_amount"): "distribution_payout_pct",
    ("cash_distribution", "net_investment_income"): "distribution_payout_pct",
    ("affo", "cash_distribution"): "distribution_coverage_pct",
    ("ffo", "cash_distribution"): "distribution_coverage_pct",
    ("distributable_amount", "cash_distribution"): "distribution_coverage_pct",
    ("net_investment_income", "cash_distribution"): "distribution_coverage_pct",
    ("cash_dividend", "distributable_profit"): "dividend_payout_pct",
    ("distributable_profit", "cash_dividend"): "dividend_coverage_pct",
    ("cash_dividend", "capital_available_for_distribution"): "dividend_payout_pct",
    ("capital_available_for_distribution", "cash_dividend"): (
        "dividend_coverage_pct"
    ),
}
EXPECTATION_COMPANY_BASES = {
    "actual_quarterly_deducted_attributable_net_profit_prc_gaap",
    "preannouncement_quarterly_deducted_attributable_net_profit_prc_gaap",
    "derived_single_quarter_deducted_attributable_net_profit_prc_gaap",
}
EXPECTATION_CONSENSUS_BASIS = (
    "pre_event_fy_attributable_net_profit_consensus_prc_gaap"
)
SURPRISE_METRICS = {
    "revenue",
    "net_income",
    "net_profit",
    "attributable_net_profit",
    "adjusted_net_income",
    "operating_income",
    "operating_profit",
    "gross_profit",
    "free_cash_flow",
    "ebit",
    "ebitda",
    "eps",
    "earnings_per_share",
    "basic_eps",
    "diluted_eps",
    "gaap_eps",
    "adjusted_eps",
    "non_gaap_eps",
}
SURPRISE_PER_SHARE_METRICS = {
    "eps",
    "earnings_per_share",
    "basic_eps",
    "diluted_eps",
    "gaap_eps",
    "adjusted_eps",
    "non_gaap_eps",
}
SUPPORTING_BLOCKING_CODES = {
    "MATERIAL_CONFLICT",
    "ORIGIN_INTERNAL_CONFLICT",
    "CURRENCY_MISMATCH",
    "UNIT_MISMATCH",
    "PERIOD_MISMATCH",
    "METRIC_MISMATCH",
    "BASIS_MISMATCH",
    "EXPECTATION_NOT_POINT_IN_TIME",
    "EXPECTATION_SOURCE_NOT_POINT_IN_TIME",
    "ACTUAL_INFORMATION_NOT_AT_EVENT",
    "ACTUAL_SOURCE_AFTER_EVENT",
    "GUIDANCE_SOURCE_AFTER_EVENT",
    "DERIVATION_CONTRACT_MISMATCH",
    "NUMERIC_CLAIM_NOT_MEANINGFUL",
    "UNTRUSTED_RECORD_SOURCE",
    "STALE_RECORD_SOURCE",
    "UNSUPPORTED_RATIO_CONTRACT",
}


class AuditInputError(ValueError):
    """A structural input error that must exit with code 2."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class AuditDependencyError(RuntimeError):
    """A valid reference whose upstream check did not pass."""

    def __init__(self, check_id: str, message: str):
        super().__init__(message)
        self.check_id = check_id


@dataclass(frozen=True)
class ValueRecord:
    value: Decimal | None
    metric: str
    unit: str
    currency: str | None
    period: dict[str, Any]
    basis: str
    source_ids: frozenset[str]
    missing_reason: str | None = None
    information_at: str | None = None


def _required_text(obj: dict[str, Any], field: str, context: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        raise AuditInputError("SCHEMA_ERROR", f"{context}.{field} must be a non-empty string")
    return value.strip()


def _required_bool(obj: dict[str, Any], field: str, context: str) -> bool:
    value = obj.get(field)
    if not isinstance(value, bool):
        raise AuditInputError("SCHEMA_ERROR", f"{context}.{field} must be boolean")
    return value


def _required_int(
    obj: dict[str, Any], field: str, context: str, *, minimum: int = 0
) -> int:
    value = obj.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise AuditInputError(
            "SCHEMA_ERROR", f"{context}.{field} must be an integer >= {minimum}"
        )
    return value


def decimal_from_string(value: Any, field: str) -> Decimal:
    """Parse a financial decimal without accepting JSON numeric literals or floats."""
    if not isinstance(value, str):
        raise AuditInputError(
            "NUMERIC_LITERAL_NOT_STRING",
            f"{field} must be a decimal JSON string, not {type(value).__name__}",
        )
    text = value.strip().replace("_", "")
    if not DECIMAL_RE.fullmatch(text):
        raise AuditInputError("INVALID_DECIMAL", f"{field} is not a valid decimal: {value!r}")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise AuditInputError(
            "INVALID_DECIMAL", f"{field} is not a valid decimal: {value!r}"
        ) from exc
    if not number.is_finite():
        raise AuditInputError("NON_FINITE_DECIMAL", f"{field} must be finite")
    if len(number.as_tuple().digits) > MAX_DECIMAL_DIGITS:
        raise AuditInputError("DECIMAL_TOO_LARGE", f"{field} has too many significant digits")
    if number and abs(number.adjusted()) > MAX_ADJUSTED_EXPONENT:
        raise AuditInputError("DECIMAL_TOO_LARGE", f"{field} exponent is out of range")
    return number


def decimal_text(value: Decimal) -> str:
    """Serialize Decimal without applying the ambient decimal context."""
    if not value.is_finite():
        raise AuditInputError("NON_FINITE_DECIMAL", "cannot serialize a non-finite decimal")
    if value.is_zero():
        return "0"
    if -100 <= value.adjusted() <= 100:
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text
    return str(value)


def json_ready(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_text(value)
    if isinstance(value, ValueRecord):
        return json_ready(record_payload(value))
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(json_ready(item) for item in value)
    return value


def record_payload(record: ValueRecord) -> dict[str, Any]:
    return {
        "value": record.value,
        "metric": record.metric,
        "unit": record.unit,
        "currency": record.currency,
        "period": record.period,
        "basis": record.basis,
        "source_ids": sorted(record.source_ids),
        "missing_reason": record.missing_reason,
        "information_at": record.information_at,
    }


def emit(payload: dict[str, Any], *, pretty: bool, output: str | None = None) -> None:
    rendered = json.dumps(
        json_ready(payload), ensure_ascii=False, indent=2 if pretty else None
    )
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def _decimal_expression_tokens(expression: str) -> tuple[str, dict[str, Decimal]]:
    if not expression.strip():
        raise AuditInputError("INVALID_EXPRESSION", "expression must not be empty")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise AuditInputError("EXPRESSION_TOO_COMPLEX", "expression is too long")
    values: dict[str, Decimal] = {}
    rewritten: list[tuple[int, str]] = []
    allowed_operators = {"+", "-", "*", "/", "**", "(", ")"}
    try:
        tokens = tokenize.generate_tokens(StringIO(expression).readline)
        for token in tokens:
            if token.type == tokenize.NUMBER:
                name = f"_n{len(values)}"
                values[name] = decimal_from_string(token.string, "literal")
                rewritten.append((tokenize.NAME, name))
            elif token.type == tokenize.OP and token.string in allowed_operators:
                rewritten.append((token.type, token.string))
            elif token.type in {tokenize.NEWLINE, tokenize.ENDMARKER}:
                rewritten.append((token.type, token.string))
            elif token.type in {tokenize.NL, tokenize.INDENT, tokenize.DEDENT}:
                continue
            elif token.type == tokenize.ERRORTOKEN and token.string.isspace():
                continue
            else:
                raise AuditInputError(
                    "UNSUPPORTED_EXPRESSION",
                    f"unsupported token in expression: {token.string!r}",
                )
    except (tokenize.TokenError, IndentationError) as exc:
        raise AuditInputError("INVALID_EXPRESSION", f"invalid expression: {exc}") from exc
    if not values:
        raise AuditInputError("INVALID_EXPRESSION", "expression contains no numbers")
    return tokenize.untokenize(rewritten), values


def _eval_decimal_node(node: ast.AST, values: dict[str, Decimal]) -> Decimal:
    if isinstance(node, ast.Expression):
        return _eval_decimal_node(node.body, values)
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval_decimal_node(node.operand, values)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left = _eval_decimal_node(node.left, values)
        right = _eval_decimal_node(node.right, values)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise AuditInputError("DIVISION_BY_ZERO", "division by zero")
            return left / right
        if isinstance(node.op, ast.Pow):
            if right != right.to_integral_value() or abs(right) > MAX_POWER:
                raise AuditInputError(
                    "INVALID_EXPONENT",
                    f"exponent must be an integer between {-MAX_POWER} and {MAX_POWER}",
                )
            return left ** int(right)
    raise AuditInputError(
        "UNSUPPORTED_EXPRESSION", f"unsupported expression node: {type(node).__name__}"
    )


def exact_calculate(expression: str) -> tuple[Decimal, bool]:
    rewritten, values = _decimal_expression_tokens(expression)
    try:
        tree = ast.parse(rewritten, mode="eval")
    except SyntaxError as exc:
        raise AuditInputError("INVALID_EXPRESSION", f"invalid expression: {exc.msg}") from exc
    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise AuditInputError("EXPRESSION_TOO_COMPLEX", "expression has too many AST nodes")
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.Emax = MAX_ADJUSTED_EXPONENT
        context.Emin = -MAX_ADJUSTED_EXPONENT
        context.clear_flags()
        try:
            result = _eval_decimal_node(tree, values)
            result = +result
        except AuditInputError:
            raise
        except (DecimalException, OverflowError) as exc:
            raise AuditInputError("DECIMAL_ARITHMETIC_ERROR", str(exc)) from exc
        rounded = bool(context.flags[Inexact] or context.flags[Rounded])
    if not result.is_finite():
        raise AuditInputError("NON_FINITE_DECIMAL", "calculation produced a non-finite value")
    return result, rounded


def _parse_iso(value: str, field: str) -> date | datetime:
    text = value.strip()
    try:
        if "T" in text or " " in text:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        return date.fromisoformat(text)
    except ValueError as exc:
        raise AuditInputError("INVALID_DATE", f"{field} must be ISO-8601: {value!r}") from exc


def _parse_aware_timestamp(value: str, field: str) -> datetime:
    parsed = _parse_iso(value, field)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise AuditInputError(
            "INVALID_TIMESTAMP",
            f"{field} must be a timezone-aware ISO-8601 timestamp",
        )
    return parsed


def _parse_date_or_aware_timestamp(value: str, field: str) -> date | datetime:
    parsed = _parse_iso(value, field)
    if isinstance(parsed, datetime) and (
        parsed.tzinfo is None or parsed.utcoffset() is None
    ):
        raise AuditInputError(
            "INVALID_TIMESTAMP",
            f"{field} timestamp must include a timezone offset",
        )
    return parsed


def _moment_date(value: str, field: str) -> date:
    parsed = _parse_iso(value, field)
    return parsed.date() if isinstance(parsed, datetime) else parsed


def _strictly_before(left: str, right: str, left_field: str, right_field: str) -> bool:
    left_value = _parse_date_or_aware_timestamp(left, left_field)
    right_value = _parse_date_or_aware_timestamp(right, right_field)
    if isinstance(left_value, datetime) and isinstance(right_value, datetime):
        return left_value < right_value
    return (
        left_value.date() if isinstance(left_value, datetime) else left_value
    ) < (right_value.date() if isinstance(right_value, datetime) else right_value)


def _not_after(left: str, right: str, left_field: str, right_field: str) -> bool:
    left_value = _parse_date_or_aware_timestamp(left, left_field)
    right_value = _parse_date_or_aware_timestamp(right, right_field)
    if isinstance(left_value, datetime) and isinstance(right_value, datetime):
        return left_value <= right_value
    return (
        left_value.date() if isinstance(left_value, datetime) else left_value
    ) <= (right_value.date() if isinstance(right_value, datetime) else right_value)


def _validate_frequency_span(
    start: str, end: str, frequency: str, context: str
) -> None:
    elapsed_days = (
        _moment_date(end, f"{context}.end")
        - _moment_date(start, f"{context}.start")
    ).days
    minimum, maximum = PERIOD_SPAN_DAYS[frequency]
    if not minimum <= elapsed_days <= maximum:
        raise AuditInputError(
            "INVALID_PERIOD_SPAN",
            f"{context} {frequency} span is {elapsed_days} days; expected {minimum}..{maximum}",
        )


def _validate_period(period: Any, context: str) -> dict[str, Any]:
    if not isinstance(period, dict):
        raise AuditInputError("SCHEMA_ERROR", f"{context} must be an object")
    kind = _required_text(period, "kind", context)
    if kind == "instant":
        as_of = _required_text(period, "as_of", context)
        _parse_aware_timestamp(as_of, f"{context}.as_of")
        return {"kind": kind, "as_of": as_of}
    if kind == "duration":
        start = _required_text(period, "start", context)
        end = _required_text(period, "end", context)
        frequency = _required_text(period, "frequency", context)
        label = _required_text(period, "label", context)
        _parse_date_or_aware_timestamp(start, f"{context}.start")
        _parse_date_or_aware_timestamp(end, f"{context}.end")
        if frequency not in PERIOD_FREQUENCIES:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.frequency is invalid")
        if _moment_date(start, f"{context}.start") > _moment_date(end, f"{context}.end"):
            raise AuditInputError("INVALID_PERIOD", f"{context}.start is after end")
        _validate_frequency_span(start, end, frequency, context)
        return {
            "kind": kind,
            "start": start,
            "end": end,
            "frequency": frequency,
            "label": label,
        }
    if kind == "estimate":
        expectation_as_of = _required_text(period, "expectation_as_of", context)
        target_start = _required_text(period, "target_start", context)
        target_end = _required_text(period, "target_end", context)
        frequency = _required_text(period, "frequency", context)
        label = _required_text(period, "label", context)
        _parse_date_or_aware_timestamp(
            expectation_as_of, f"{context}.expectation_as_of"
        )
        _parse_date_or_aware_timestamp(target_start, f"{context}.target_start")
        _parse_date_or_aware_timestamp(target_end, f"{context}.target_end")
        if frequency not in PERIOD_FREQUENCIES:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.frequency is invalid")
        if _moment_date(target_start, f"{context}.target_start") > _moment_date(
            target_end, f"{context}.target_end"
        ):
            raise AuditInputError("INVALID_PERIOD", f"{context}.target_start is after end")
        _validate_frequency_span(
            target_start, target_end, frequency, f"{context}.target"
        )
        return {
            "kind": kind,
            "expectation_as_of": expectation_as_of,
            "target_start": target_start,
            "target_end": target_end,
            "frequency": frequency,
            "label": label,
        }
    raise AuditInputError("SCHEMA_ERROR", f"{context}.kind is invalid: {kind!r}")


def _issue(
    code: str,
    message: str,
    *,
    refs: Iterable[str] = (),
    provisional_eligible: bool = False,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "refs": sorted(set(refs)),
        "provisional_eligible": provisional_eligible,
    }


def _union_sources(records: Iterable[ValueRecord]) -> frozenset[str]:
    source_ids: set[str] = set()
    for record in records:
        source_ids.update(record.source_ids)
    return frozenset(source_ids)


class AuditEngine:
    def __init__(self, payload: dict[str, Any], input_sha256: str):
        self.payload = payload
        self.input_sha256 = input_sha256
        self.sources: dict[str, dict[str, Any]] = {}
        self.facts: dict[str, ValueRecord] = {}
        self.checks: list[dict[str, Any]] = []
        self.check_ids: set[str] = set()
        self.check_results: dict[str, dict[str, Any]] = {}
        self.check_outputs: dict[str, dict[str, ValueRecord]] = {}
        self.excluded_sources: list[dict[str, Any]] = []
        self.provisional_context: dict[str, Any] | None = None
        self.locator_origins: dict[str, str] = {}
        self._validate_and_load()

    def _validate_and_load(self) -> None:
        if self.payload.get("schema_version") != SCHEMA_VERSION:
            raise AuditInputError(
                "SCHEMA_ERROR", f"schema_version must equal {SCHEMA_VERSION!r}"
            )
        _required_text(self.payload, "audit_id", "root")
        as_of = _required_text(self.payload, "as_of", "root")
        _parse_aware_timestamp(as_of, "root.as_of")
        self.as_of = as_of

        sources = self.payload.get("sources")
        facts = self.payload.get("facts")
        checks = self.payload.get("checks")
        if not isinstance(sources, list) or not isinstance(facts, list) or not isinstance(checks, list):
            raise AuditInputError(
                "SCHEMA_ERROR", "root.sources, root.facts, and root.checks must be arrays"
            )

        for index, source in enumerate(sources):
            self._load_source(source, index)
        for index, fact in enumerate(facts):
            self._load_fact(fact, index)

        for index, check in enumerate(checks):
            if not isinstance(check, dict):
                raise AuditInputError("SCHEMA_ERROR", f"checks[{index}] must be an object")
            check_id = _required_text(check, "id", f"checks[{index}]")
            if check_id in self.check_ids:
                raise AuditInputError("DUPLICATE_ID", f"duplicate check id: {check_id}")
            self.check_ids.add(check_id)
            self.checks.append(check)

        context = self.payload.get("provisional_context")
        if context is not None:
            self.provisional_context = self._validate_provisional_context(context)

    def _load_source(self, source: Any, index: int) -> None:
        context = f"sources[{index}]"
        if not isinstance(source, dict):
            raise AuditInputError("SCHEMA_ERROR", f"{context} must be an object")
        source_id = _required_text(source, "id", context)
        if source_id in self.sources:
            raise AuditInputError("DUPLICATE_ID", f"duplicate source id: {source_id}")
        source_type = _required_text(source, "source_type", context)
        if source_type not in ALL_SOURCE_TYPES:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.source_type is invalid")
        origin_id = _required_text(source, "origin_id", context)
        locator = _required_text(source, "locator", context)
        normalized_locator = locator.casefold()
        prior_origin = self.locator_origins.get(normalized_locator)
        if prior_origin is not None and prior_origin != origin_id:
            raise AuditInputError(
                "LOCATOR_ORIGIN_CONFLICT",
                f"{context}.locator is already assigned to origin_id {prior_origin!r}",
            )
        self.locator_origins[normalized_locator] = origin_id
        source_date = _required_text(source, "source_date", context)
        checked_at = _required_text(source, "checked_at", context)
        _parse_date_or_aware_timestamp(source_date, f"{context}.source_date")
        _parse_aware_timestamp(checked_at, f"{context}.checked_at")
        for field, value in (("source_date", source_date), ("checked_at", checked_at)):
            if not _not_after(value, self.as_of, f"{context}.{field}", "root.as_of"):
                raise AuditInputError(
                    "LOOKAHEAD_DATE", f"{context}.{field} must not be after root.as_of"
                )
        status = _required_text(source, "status", context)
        if status not in {"accepted", "excluded"}:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.status is invalid")
        normalized = {
            "id": source_id,
            "source_type": source_type,
            "origin_id": origin_id,
            "locator": locator,
            "source_date": source_date,
            "checked_at": checked_at,
            "status": status,
        }
        if status == "excluded":
            normalized["exclusion_code"] = _required_text(source, "exclusion_code", context)
            normalized["exclusion_reason"] = _required_text(source, "exclusion_reason", context)
            self.excluded_sources.append(normalized)
        self.sources[source_id] = normalized

    def _load_fact(self, fact: Any, index: int) -> None:
        context = f"facts[{index}]"
        if not isinstance(fact, dict):
            raise AuditInputError("SCHEMA_ERROR", f"{context} must be an object")
        fact_id = _required_text(fact, "id", context)
        if fact_id in self.facts:
            raise AuditInputError("DUPLICATE_ID", f"duplicate fact id: {fact_id}")
        metric = _required_text(fact, "metric", context)
        unit = _required_text(fact, "unit", context)
        if unit not in ALL_UNITS:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.unit is invalid")
        currency = fact.get("currency")
        if unit in MONETARY_UNITS:
            if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
                raise AuditInputError(
                    "SCHEMA_ERROR", f"{context}.currency must be a three-letter code"
                )
        elif currency is not None:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.currency must be null for {unit}"
            )
        scale = decimal_from_string(fact.get("scale"), f"{context}.scale")
        if scale <= 0:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.scale must be positive")
        if unit in {"percent", "ratio", "multiple"} and scale != 1:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.scale must be 1 for {unit}")
        period = _validate_period(fact.get("period"), f"{context}.period")
        cutoff_field = {
            "instant": "as_of",
            "duration": "end",
            "estimate": "expectation_as_of",
        }[period["kind"]]
        if not _not_after(
            period[cutoff_field],
            self.as_of,
            f"{context}.period.{cutoff_field}",
            "root.as_of",
        ):
            raise AuditInputError(
                "LOOKAHEAD_DATE",
                f"{context}.period.{cutoff_field} must not be after root.as_of",
            )
        raw_available_at = fact.get("available_at")
        if period["kind"] == "duration":
            available_at = _required_text(fact, "available_at", context)
        elif raw_available_at is None:
            available_at = None
        elif isinstance(raw_available_at, str) and raw_available_at.strip():
            available_at = raw_available_at.strip()
        else:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.available_at must be a non-empty string"
            )
        information_at = period[cutoff_field]
        if available_at is not None:
            _parse_date_or_aware_timestamp(
                available_at, f"{context}.available_at"
            )
            if not _not_after(
                information_at,
                available_at,
                f"{context}.period.{cutoff_field}",
                f"{context}.available_at",
            ):
                raise AuditInputError(
                    "INVALID_AVAILABLE_AT",
                    f"{context}.available_at must not precede the fact's base information time",
                )
            if not _not_after(
                available_at,
                self.as_of,
                f"{context}.available_at",
                "root.as_of",
            ):
                raise AuditInputError(
                    "LOOKAHEAD_DATE", f"{context}.available_at must not be after root.as_of"
                )
            information_at = available_at
        basis = _required_text(fact, "basis", context)

        if "value" not in fact:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.value is required")
        raw_value = fact.get("value")
        missing_reason: str | None = None
        value: Decimal | None
        if raw_value is None:
            value = None
            missing_reason = _required_text(fact, "missing_reason", context)
        else:
            with localcontext() as decimal_context:
                decimal_context.prec = DECIMAL_PRECISION
                decimal_context.Emax = MAX_ADJUSTED_EXPONENT
                decimal_context.Emin = -MAX_ADJUSTED_EXPONENT
                decimal_context.clear_flags()
                try:
                    value = decimal_from_string(raw_value, f"{context}.value") * scale
                except DecimalException as exc:
                    raise AuditInputError("DECIMAL_ARITHMETIC_ERROR", str(exc)) from exc
                if decimal_context.flags[Inexact] or decimal_context.flags[Rounded]:
                    raise AuditInputError(
                        "DECIMAL_PRECISION_LOSS",
                        f"{context}.value * scale cannot be represented exactly at "
                        f"precision {DECIMAL_PRECISION}",
                    )

        source_refs = fact.get("source_refs")
        if not isinstance(source_refs, list) or any(
            not isinstance(source_id, str) or not source_id for source_id in source_refs
        ):
            raise AuditInputError("SCHEMA_ERROR", f"{context}.source_refs must be a string array")
        if value is not None and not source_refs:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.source_refs must not be empty")
        for source_id in source_refs:
            if source_id not in self.sources:
                raise AuditInputError("UNKNOWN_REFERENCE", f"{context} references unknown {source_id}")
            if self.sources[source_id]["status"] != "accepted":
                raise AuditInputError(
                    "EXCLUDED_SOURCE_REFERENCE",
                    f"{context} references excluded source {source_id}",
                )
        self.facts[fact_id] = ValueRecord(
            value=value,
            metric=metric,
            unit=unit,
            currency=currency,
            period=period,
            basis=basis,
            source_ids=frozenset(source_refs),
            missing_reason=missing_reason,
            information_at=information_at,
        )

    def _validate_provisional_context(self, context: Any) -> dict[str, Any]:
        if not isinstance(context, dict):
            raise AuditInputError("SCHEMA_ERROR", "provisional_context must be an object")
        requested = _required_bool(context, "requested", "provisional_context")
        fallback_completed = _required_bool(
            context, "fallback_completed", "provisional_context"
        )
        missing = context.get("missing_materials")
        if not isinstance(missing, list) or not missing or any(
            not isinstance(item, str) or not item.strip() for item in missing
        ):
            raise AuditInputError(
                "SCHEMA_ERROR", "provisional_context.missing_materials must be non-empty"
            )
        recheck_after = _required_text(context, "recheck_after", "provisional_context")
        _parse_date_or_aware_timestamp(
            recheck_after, "provisional_context.recheck_after"
        )
        if not _strictly_before(
            _required_text(self.payload, "as_of", "root"),
            recheck_after,
            "root.as_of",
            "provisional_context.recheck_after",
        ):
            raise AuditInputError(
                "INVALID_DATE", "provisional_context.recheck_after must be after root.as_of"
            )
        return {
            "requested": requested,
            "fallback_completed": fallback_completed,
            "missing_materials": [item.strip() for item in missing],
            "recheck_after": recheck_after,
        }

    def _resolve_ref(self, ref: Any, context: str) -> ValueRecord:
        if not isinstance(ref, dict):
            raise AuditInputError("SCHEMA_ERROR", f"{context} must be a ValueRef object")
        has_fact = "fact_id" in ref
        has_check = "check_id" in ref
        if has_fact == has_check:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context} must contain exactly one of fact_id/check_id"
            )
        if has_fact:
            fact_id = _required_text(ref, "fact_id", context)
            if fact_id not in self.facts:
                raise AuditInputError("UNKNOWN_REFERENCE", f"{context} unknown fact {fact_id}")
            return self.facts[fact_id]
        check_id = _required_text(ref, "check_id", context)
        output = _required_text(ref, "output", context)
        if check_id not in self.check_ids:
            raise AuditInputError("UNKNOWN_REFERENCE", f"{context} unknown check {check_id}")
        if check_id not in self.check_results:
            raise AuditInputError(
                "FORWARD_REFERENCE", f"{context} references non-prior check {check_id}"
            )
        if self.check_results[check_id]["status"] != "PASS":
            raise AuditDependencyError(check_id, f"upstream check {check_id} did not pass")
        if output not in self.check_outputs.get(check_id, {}):
            raise AuditInputError(
                "UNKNOWN_CHECK_OUTPUT", f"{context} unknown output {check_id}.{output}"
            )
        return self.check_outputs[check_id][output]

    def _source_gate(
        self, records: Iterable[ValueRecord], gate: Any, context: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        if not isinstance(gate, dict):
            raise AuditInputError("SCHEMA_ERROR", f"{context} must be an object")
        minimum = _required_int(gate, "min_independent_origins", context, minimum=1)
        counted_tier = _required_text(gate, "counted_tier", context)
        anchor_tier = _required_text(gate, "required_anchor_tier", context)
        if counted_tier not in SOURCE_TIERS:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.counted_tier is invalid")
        if anchor_tier not in {*SOURCE_TIERS, "none"}:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.required_anchor_tier is invalid"
            )
        source_ids = sorted(_union_sources(records))
        counted_sources = [
            self.sources[source_id]
            for source_id in source_ids
            if self.sources[source_id]["source_type"] in SOURCE_TIERS[counted_tier]
        ]
        origins = sorted({source["origin_id"] for source in counted_sources})
        issues: list[dict[str, Any]] = []
        if len(origins) < minimum:
            issues.append(
                _issue(
                    "MISSING_REQUIRED_SOURCE",
                    f"independent origins {len(origins)} below required {minimum}",
                    refs=source_ids,
                    provisional_eligible=counted_tier == "official",
                )
            )
        anchor_present = True
        if anchor_tier != "none":
            anchor_present = any(
                self.sources[source_id]["source_type"] in SOURCE_TIERS[anchor_tier]
                for source_id in source_ids
            )
            if not anchor_present:
                issues.append(
                    _issue(
                        "MISSING_REQUIRED_SOURCE",
                        f"no source satisfies required anchor tier {anchor_tier}",
                        refs=source_ids,
                        provisional_eligible=anchor_tier == "official",
                    )
                )
        return {
            "source_ids": source_ids,
            "counted_tier": counted_tier,
            "required_anchor_tier": anchor_tier,
            "independent_origins": origins,
            "independent_origin_count": len(origins),
            "minimum_required": minimum,
            "anchor_present": anchor_present,
        }, issues

    def _tolerance(self, obj: Any, context: str) -> tuple[Decimal, Decimal]:
        if not isinstance(obj, dict):
            raise AuditInputError("SCHEMA_ERROR", f"{context} must be an object")
        relative = decimal_from_string(obj.get("relative_pct"), f"{context}.relative_pct")
        absolute = decimal_from_string(obj.get("absolute_base"), f"{context}.absolute_base")
        if relative < 0 or absolute < 0:
            raise AuditInputError("SCHEMA_ERROR", f"{context} values must be non-negative")
        return relative, absolute

    @staticmethod
    def _missing_issue(record: ValueRecord, ref: str) -> dict[str, Any] | None:
        if record.value is not None:
            return None
        eligible = record.missing_reason == "official_missing"
        return _issue(
            "MISSING_OFFICIAL_VALUE" if eligible else "MISSING_VALUE",
            f"{ref} has no numeric value ({record.missing_reason})",
            refs=[ref],
            provisional_eligible=eligible,
        )

    def _record_source_issue(
        self,
        record: ValueRecord,
        ref: str,
        allowed_types: set[str],
        requirement: str,
    ) -> dict[str, Any] | None:
        if record.value is None:
            return None
        type_eligible_source_ids = sorted(
            source_id
            for source_id in record.source_ids
            if self.sources[source_id]["source_type"] in allowed_types
        )
        if not type_eligible_source_ids:
            return _issue(
                "UNTRUSTED_RECORD_SOURCE",
                f"{ref} requires its own accepted {requirement} source",
                refs=record.source_ids,
            )
        if record.information_at is None:
            return None
        fresh_source_ids = [
            source_id
            for source_id in type_eligible_source_ids
            if _not_after(
                record.information_at,
                self.sources[source_id]["source_date"],
                f"{ref}.information_at",
                f"sources[{source_id}].source_date",
            )
        ]
        if fresh_source_ids:
            return None
        return _issue(
            "STALE_RECORD_SOURCE",
            f"{ref} has no {requirement} source dated on or after its information_at",
            refs=type_eligible_source_ids,
        )

    def _append_record_source_issue(
        self,
        issues: list[dict[str, Any]],
        record: ValueRecord,
        ref: str,
        allowed_types: set[str],
        requirement: str,
    ) -> None:
        issue = self._record_source_issue(
            record, ref, allowed_types, requirement
        )
        if issue:
            issues.append(issue)

    @staticmethod
    def _metadata_issues(
        left: ValueRecord,
        right: ValueRecord,
        left_ref: str,
        right_ref: str,
        *,
        metric: bool = True,
        period: bool = True,
        basis: bool = True,
    ) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        refs = [left_ref, right_ref]
        if metric and left.metric != right.metric:
            issues.append(_issue("METRIC_MISMATCH", "metric mismatch", refs=refs))
        if left.unit != right.unit:
            issues.append(_issue("UNIT_MISMATCH", "unit mismatch", refs=refs))
        if left.currency != right.currency:
            issues.append(_issue("CURRENCY_MISMATCH", "currency mismatch", refs=refs))
        if period and left.period != right.period:
            issues.append(_issue("PERIOD_MISMATCH", "period mismatch", refs=refs))
        if basis and left.basis != right.basis:
            issues.append(_issue("BASIS_MISMATCH", "metric basis mismatch", refs=refs))
        return issues

    @staticmethod
    def _numeric_conflict(
        left: Decimal,
        right: Decimal,
        relative_pct: Decimal,
        absolute_base: Decimal,
        refs: Iterable[str],
        *,
        symmetric: bool,
    ) -> dict[str, Any] | None:
        difference = abs(left - right)
        anchor = max(abs(left), abs(right)) if symmetric else abs(right)
        allowed = max(absolute_base, anchor * relative_pct / Decimal(100))
        if difference <= allowed:
            return None
        return _issue(
            "MATERIAL_CONFLICT",
            f"numeric difference {decimal_text(difference)} exceeds allowed {decimal_text(allowed)}",
            refs=refs,
        )

    def _origins(self, record: ValueRecord) -> set[str]:
        return {self.sources[source_id]["origin_id"] for source_id in record.source_ids}

    def _execute_cross_source(
        self, check: dict[str, Any], context: str
    ) -> tuple[dict[str, ValueRecord], list[dict[str, Any]], dict[str, Any], dict[str, Any], str]:
        target = self._resolve_ref(check.get("target"), f"{context}.target")
        raw_references = check.get("references")
        if not isinstance(raw_references, list) or not raw_references:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.references must not be empty")
        references = [
            self._resolve_ref(ref, f"{context}.references[{index}]")
            for index, ref in enumerate(raw_references)
        ]
        relative, absolute = self._tolerance(check.get("tolerance"), f"{context}.tolerance")
        gate_details, issues = self._source_gate(
            references, check.get("source_gate"), f"{context}.source_gate"
        )
        named = [("target", target)] + [
            (f"reference[{index}]", record) for index, record in enumerate(references)
        ]
        for name, record in named:
            missing = self._missing_issue(record, name)
            if missing:
                issues.append(missing)
        self._append_record_source_issue(
            issues,
            target,
            "target",
            ANY_CREDIBLE_TYPES | {"report_under_audit"},
            "credible or report_under_audit",
        )
        for index, reference in enumerate(references):
            self._append_record_source_issue(
                issues,
                reference,
                f"reference[{index}]",
                ANY_CREDIBLE_TYPES,
                "credible",
            )
        if target.value is not None:
            for index, reference in enumerate(references):
                name = f"reference[{index}]"
                metadata = self._metadata_issues(target, reference, "target", name)
                issues.extend(metadata)
                if not metadata and reference.value is not None:
                    conflict = self._numeric_conflict(
                        target.value,
                        reference.value,
                        relative,
                        absolute,
                        ["target", name],
                        symmetric=False,
                    )
                    if conflict:
                        issues.append(conflict)
        for left_index in range(len(references)):
            for right_index in range(left_index + 1, len(references)):
                left = references[left_index]
                right = references[right_index]
                refs = [f"reference[{left_index}]", f"reference[{right_index}]"]
                metadata = self._metadata_issues(left, right, refs[0], refs[1])
                issues.extend(metadata)
                if left.value is None or right.value is None or metadata:
                    continue
                if self._origins(left) & self._origins(right) and left.value != right.value:
                    issues.append(
                        _issue(
                            "ORIGIN_INTERNAL_CONFLICT",
                            "the same origin reports different values",
                            refs=refs,
                        )
                    )
                conflict = self._numeric_conflict(
                    left.value,
                    right.value,
                    relative,
                    absolute,
                    refs,
                    symmetric=True,
                )
                if conflict:
                    issues.append(conflict)
        output = ValueRecord(
            value=target.value,
            metric=target.metric,
            unit=target.unit,
            currency=target.currency,
            period=target.period,
            basis=target.basis,
            source_ids=_union_sources([target, *references]),
            missing_reason=target.missing_reason,
        )
        details = {"reference_count": len(references)}
        return {"value": output}, issues, gate_details, details, "verified"

    def _execute_market_cap(
        self, check: dict[str, Any], context: str
    ) -> tuple[dict[str, ValueRecord], list[dict[str, Any]], dict[str, Any], dict[str, Any], str]:
        price = self._resolve_ref(check.get("price"), f"{context}.price")
        shares = self._resolve_ref(check.get("shares"), f"{context}.shares")
        expected_ref = check.get("expected")
        expected = (
            self._resolve_ref(expected_ref, f"{context}.expected")
            if expected_ref is not None
            else None
        )
        records = [price, shares] + ([expected] if expected else [])
        gate_details, issues = self._source_gate(
            records, check.get("source_gate"), f"{context}.source_gate"
        )
        capitalization_basis = _required_text(check, "capitalization_basis", context)
        basis_map = {
            "total": (
                {"total_shares", "total_shares_outstanding"},
                "total_shares_outstanding",
                "total_market_cap",
            ),
            "free_float": (
                {"free_float_shares"},
                "free_float_shares",
                "free_float_market_cap",
            ),
        }
        if capitalization_basis not in basis_map:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.capitalization_basis is invalid")
        max_age = _required_int(check, "max_share_age_days", context, minimum=0)
        for name, record in (("price", price), ("shares", shares), ("expected", expected)):
            if record is not None:
                missing = self._missing_issue(record, name)
                if missing:
                    issues.append(missing)
        self._append_record_source_issue(
            issues,
            price,
            "price",
            VENDOR_OR_OFFICIAL_TYPES,
            "vendor_or_official",
        )
        self._append_record_source_issue(
            issues,
            shares,
            "shares",
            ANY_CREDIBLE_TYPES,
            "credible",
        )
        if expected is not None:
            self._append_record_source_issue(
                issues,
                expected,
                "expected",
                ANY_CREDIBLE_TYPES | {"report_under_audit"},
                "credible or report_under_audit claim",
            )
        if price.unit != "currency_per_share":
            issues.append(_issue("UNIT_MISMATCH", "price must be currency_per_share", refs=["price"]))
        if shares.unit != "share":
            issues.append(_issue("UNIT_MISMATCH", "shares must use share unit", refs=["shares"]))
        allowed_share_metrics, share_basis, output_basis = basis_map[capitalization_basis]
        if price.metric not in PRICE_METRIC_BASES:
            issues.append(
                _issue(
                    "METRIC_MISMATCH",
                    "price metric is not a recognized per-share market price",
                    refs=["price"],
                )
            )
        elif price.basis not in PRICE_METRIC_BASES[price.metric]:
            issues.append(
                _issue(
                    "BASIS_MISMATCH",
                    f"price basis {price.basis!r} is invalid for metric {price.metric}",
                    refs=["price"],
                )
            )
        if shares.metric not in allowed_share_metrics:
            issues.append(
                _issue(
                    "METRIC_MISMATCH",
                    f"shares metric is invalid for {capitalization_basis} capitalization",
                    refs=["shares"],
                )
            )
        if shares.basis != share_basis:
            issues.append(_issue("BASIS_MISMATCH", f"shares basis must be {share_basis}", refs=["shares"]))
        if price.period.get("kind") != "instant" or shares.period.get("kind") != "instant":
            issues.append(_issue("PERIOD_MISMATCH", "price and shares must be instant facts"))
        else:
            price_date = _moment_date(price.period["as_of"], "price.period.as_of")
            shares_date = _moment_date(shares.period["as_of"], "shares.period.as_of")
            age = (price_date - shares_date).days
            if age < 0 or age > max_age:
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        f"share count age {age} days is outside 0..{max_age}",
                        refs=["price", "shares"],
                    )
                )
        if price.value is not None and price.value <= 0:
            issues.append(_issue("NONPOSITIVE_INPUT", "price must be positive", refs=["price"]))
        if shares.value is not None and shares.value <= 0:
            issues.append(_issue("NONPOSITIVE_INPUT", "shares must be positive", refs=["shares"]))
        calculated = (
            price.value * shares.value
            if price.value is not None and shares.value is not None
            else None
        )
        output = ValueRecord(
            value=calculated,
            metric=output_basis,
            unit="currency",
            currency=price.currency,
            period=price.period,
            basis=output_basis,
            source_ids=_union_sources(records),
            missing_reason="dependency_missing" if calculated is None else None,
        )
        if expected is not None:
            if expected.unit != "currency":
                issues.append(_issue("UNIT_MISMATCH", "expected market cap must use currency"))
            if expected.currency != price.currency:
                issues.append(_issue("CURRENCY_MISMATCH", "expected market cap currency mismatch"))
            if expected.period != price.period:
                issues.append(_issue("PERIOD_MISMATCH", "expected market cap timestamp mismatch"))
            if expected.metric != output_basis:
                issues.append(
                    _issue(
                        "METRIC_MISMATCH",
                        f"expected market cap metric must be {output_basis}",
                        refs=["expected"],
                    )
                )
            if expected.basis != output_basis:
                issues.append(_issue("BASIS_MISMATCH", "expected market cap basis mismatch"))
            relative, absolute = self._tolerance(
                check.get("tolerance"), f"{context}.tolerance"
            )
            if calculated is not None and expected.value is not None:
                conflict = self._numeric_conflict(
                    calculated,
                    expected.value,
                    relative,
                    absolute,
                    ["calculated", "expected"],
                    symmetric=False,
                )
                if conflict:
                    issues.append(conflict)
        elif "tolerance" in check:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.tolerance is only valid when expected is present"
            )
        details = {"formula": "price * shares", "capitalization_basis": capitalization_basis}
        return {"value": output}, issues, gate_details, details, "verified"

    def _execute_expectation_gap(
        self, check: dict[str, Any], context: str
    ) -> tuple[dict[str, ValueRecord], list[dict[str, Any]], dict[str, Any], dict[str, Any], str]:
        low = self._resolve_ref(check.get("quarterly_low"), f"{context}.quarterly_low")
        high = self._resolve_ref(check.get("quarterly_high"), f"{context}.quarterly_high")
        consensus = self._resolve_ref(check.get("consensus"), f"{context}.consensus")
        factor = decimal_from_string(
            check.get("annualization_factor"), f"{context}.annualization_factor"
        )
        if factor != 4:
            raise AuditInputError(
                "SCHEMA_ERROR",
                f"{context}.annualization_factor must be 4 for this comparison basis",
            )
        event_at = _required_text(check, "event_at", context)
        event_moment = _parse_aware_timestamp(event_at, f"{context}.event_at")
        if not _not_after(event_at, self.as_of, f"{context}.event_at", "root.as_of"):
            raise AuditInputError(
                "LOOKAHEAD_DATE", f"{context}.event_at must not be after root.as_of"
            )
        comparison_basis = _required_text(check, "comparison_basis", context)
        required_basis = "annualized_quarterly_deducted_vs_fy_attributable_consensus"
        if comparison_basis != required_basis:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.comparison_basis must be {required_basis}"
            )
        company_metric = _required_text(check, "company_metric", context)
        consensus_metric = _required_text(check, "consensus_metric", context)
        required_company_metric = "deducted_attributable_net_profit"
        required_consensus_metric = "fy_attributable_net_profit"
        if company_metric != required_company_metric:
            raise AuditInputError(
                "SCHEMA_ERROR",
                f"{context}.company_metric must be {required_company_metric}",
            )
        if consensus_metric != required_consensus_metric:
            raise AuditInputError(
                "SCHEMA_ERROR",
                f"{context}.consensus_metric must be {required_consensus_metric}",
            )
        records = [low, high, consensus]
        gate_details, issues = self._source_gate(
            records, check.get("source_gate"), f"{context}.source_gate"
        )
        for name, record in (("quarterly_low", low), ("quarterly_high", high), ("consensus", consensus)):
            missing = self._missing_issue(record, name)
            if missing:
                issues.append(missing)
        for name, record in (("quarterly_low", low), ("quarterly_high", high)):
            self._append_record_source_issue(
                issues,
                record,
                name,
                OFFICIAL_TYPES,
                "official",
            )
        self._append_record_source_issue(
            issues,
            consensus,
            "consensus",
            {"market_data_vendor", "credible_secondary"},
            "market-data vendor or credible-secondary",
        )
        issues.extend(
            self._metadata_issues(
                low, high, "quarterly_low", "quarterly_high", period=True, basis=True
            )
        )
        if low.metric != required_company_metric or high.metric != required_company_metric:
            issues.append(
                _issue(
                    "METRIC_MISMATCH",
                    f"quarterly facts must use metric {required_company_metric}",
                    refs=["quarterly_low", "quarterly_high"],
                )
            )
        if consensus.metric != required_consensus_metric:
            issues.append(
                _issue(
                    "METRIC_MISMATCH",
                    f"consensus fact must use metric {required_consensus_metric}",
                    refs=["consensus"],
                )
            )
        for name, record in (("quarterly_low", low), ("quarterly_high", high)):
            if record.basis not in EXPECTATION_COMPANY_BASES:
                issues.append(
                    _issue(
                        "BASIS_MISMATCH",
                        f"{name} basis is not an allowed PRC-GAAP quarterly "
                        "deducted-attributable basis",
                        refs=[name],
                    )
                )
        if consensus.basis != EXPECTATION_CONSENSUS_BASIS:
            issues.append(
                _issue(
                    "BASIS_MISMATCH",
                    "consensus basis must be pre-event FY attributable-net-profit "
                    "consensus under PRC-GAAP",
                    refs=["consensus"],
                )
            )
        if low.unit != "currency" or high.unit != "currency" or consensus.unit != "currency":
            issues.append(_issue("UNIT_MISMATCH", "expectation inputs must use currency unit"))
        if not (low.currency == high.currency == consensus.currency):
            issues.append(_issue("CURRENCY_MISMATCH", "expectation input currencies differ"))
        company_period_valid = (
            low.period.get("kind") == "duration"
            and low.period.get("frequency") == "quarter"
            and high.period == low.period
        )
        consensus_period_valid = (
            consensus.period.get("kind") == "estimate"
            and consensus.period.get("frequency") == "year"
        )
        if not company_period_valid:
            issues.append(_issue("PERIOD_MISMATCH", "company values must be one fiscal quarter"))
        if not consensus_period_valid:
            issues.append(_issue("PERIOD_MISMATCH", "consensus must be a full-year estimate"))
        elif not _strictly_before(
            consensus.period["expectation_as_of"],
            event_at,
            "consensus.expectation_as_of",
            f"{context}.event_at",
        ):
            issues.append(
                _issue(
                    "EXPECTATION_NOT_POINT_IN_TIME",
                    "consensus expectation_as_of is not before the event",
                    refs=["consensus"],
                )
            )
        if company_period_valid:
            for name, record in (("quarterly_low", low), ("quarterly_high", high)):
                information_moment = _parse_aware_timestamp(
                    record.information_at or "",
                    f"{name}.information_at",
                )
                if information_moment != event_moment:
                    issues.append(
                        _issue(
                            "ACTUAL_INFORMATION_NOT_AT_EVENT",
                            f"{name} actual information_at must equal event_at",
                            refs=[name],
                        )
                    )
        late_consensus_sources = [
            source_id
            for source_id in sorted(consensus.source_ids)
            if not _strictly_before(
                self.sources[source_id]["source_date"],
                event_at,
                f"sources[{source_id}].source_date",
                f"{context}.event_at",
            )
        ]
        if late_consensus_sources:
            issues.append(
                _issue(
                    "EXPECTATION_SOURCE_NOT_POINT_IN_TIME",
                    "every consensus source_date must establish pre-event publication "
                    "or snapshot availability",
                    refs=late_consensus_sources,
                )
            )
        late_actual_sources = sorted(
            {
                source_id
                for record in (low, high)
                for source_id in record.source_ids
                if not _not_after(
                    self.sources[source_id]["source_date"],
                    event_at,
                    f"sources[{source_id}].source_date",
                    f"{context}.event_at",
                )
            }
        )
        if late_actual_sources:
            issues.append(
                _issue(
                    "ACTUAL_SOURCE_AFTER_EVENT",
                    "quarterly actual source_date must not be after the earnings event",
                    refs=late_actual_sources,
                )
            )
        if company_period_valid and not _not_after(
            low.period["end"],
            event_at,
            "company_quarter.end",
            f"{context}.event_at",
        ):
            issues.append(
                _issue(
                    "PERIOD_MISMATCH",
                    "company quarter ends after the stated earnings event",
                    refs=["quarterly_low", "quarterly_high"],
                )
            )
        if company_period_valid and consensus_period_valid:
            quarter_start = _moment_date(low.period["start"], "company_quarter.start")
            quarter_end = _moment_date(low.period["end"], "company_quarter.end")
            target_start = _moment_date(
                consensus.period["target_start"], "consensus.target_start"
            )
            target_end = _moment_date(
                consensus.period["target_end"], "consensus.target_end"
            )
            if not (target_start <= quarter_start <= quarter_end <= target_end):
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        "company quarter is not contained in the consensus target fiscal year",
                        refs=["quarterly_low", "quarterly_high", "consensus"],
                    )
                )
        if low.value is not None and high.value is not None and low.value > high.value:
            raise AuditInputError("INVALID_RANGE", f"{context} quarterly_low exceeds quarterly_high")
        annualized_low = low.value * factor if low.value is not None else None
        annualized_high = high.value * factor if high.value is not None else None
        gap_low = (
            annualized_low - consensus.value
            if annualized_low is not None and consensus.value is not None
            else None
        )
        gap_high = (
            annualized_high - consensus.value
            if annualized_high is not None and consensus.value is not None
            else None
        )
        if annualized_low is None or annualized_high is None or consensus.value is None:
            status = "insufficient"
        elif annualized_low > consensus.value:
            status = "above"
        elif annualized_high < consensus.value:
            status = "below"
        else:
            status = "straddles"
        source_ids = _union_sources(records)
        annualized_basis = "latest_single_quarter_deducted_attributable_net_profit_x4"
        outputs = {
            "annualized_low": ValueRecord(
                annualized_low, required_company_metric, "currency", low.currency, low.period,
                annualized_basis, source_ids, "dependency_missing" if annualized_low is None else None,
            ),
            "annualized_high": ValueRecord(
                annualized_high, required_company_metric, "currency", high.currency, high.period,
                annualized_basis, source_ids, "dependency_missing" if annualized_high is None else None,
            ),
            "gap_low": ValueRecord(
                gap_low, "expectation_gap", "currency", low.currency, low.period,
                comparison_basis, source_ids, "dependency_missing" if gap_low is None else None,
            ),
            "gap_high": ValueRecord(
                gap_high, "expectation_gap", "currency", high.currency, high.period,
                comparison_basis, source_ids, "dependency_missing" if gap_high is None else None,
            ),
        }
        details = {
            "annualization_factor": factor,
            "annualized_core_gap_status": status,
            "formal_surprise_status": "N/A",
            "comparison_basis": comparison_basis,
        }
        return outputs, issues, gate_details, details, status

    def _execute_expectation_surprise(
        self, check: dict[str, Any], context: str
    ) -> tuple[dict[str, ValueRecord], list[dict[str, Any]], dict[str, Any], dict[str, Any], str]:
        subject_kind = _required_text(check, "subject_kind", context)
        if subject_kind == "reported_actual":
            low_field, high_field = "actual_low", "actual_high"
        elif subject_kind == "company_guidance":
            low_field, high_field = "guidance_low", "guidance_high"
        else:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.subject_kind is invalid"
            )
        actual_low = self._resolve_ref(check.get(low_field), f"{context}.{low_field}")
        actual_high = self._resolve_ref(check.get(high_field), f"{context}.{high_field}")
        consensus = self._resolve_ref(check.get("consensus"), f"{context}.consensus")
        event_at = _required_text(check, "event_at", context)
        event_moment = _parse_aware_timestamp(event_at, f"{context}.event_at")
        if not _not_after(event_at, self.as_of, f"{context}.event_at", "root.as_of"):
            raise AuditInputError(
                "LOOKAHEAD_DATE", f"{context}.event_at must not be after root.as_of"
            )
        relative, absolute = self._tolerance(
            check.get("tolerance"), f"{context}.tolerance"
        )

        expected_low_ref = check.get("expected_low")
        expected_high_ref = check.get("expected_high")
        if (expected_low_ref is None) != (expected_high_ref is None):
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.expected_low and expected_high must appear together"
            )
        expected_low = (
            self._resolve_ref(expected_low_ref, f"{context}.expected_low")
            if expected_low_ref is not None
            else None
        )
        expected_high = (
            self._resolve_ref(expected_high_ref, f"{context}.expected_high")
            if expected_high_ref is not None
            else None
        )
        expected_kind: str | None = None
        claim_tolerance: tuple[Decimal, Decimal] | None = None
        if expected_low is not None:
            expected_kind = _required_text(check, "expected_kind", context)
            if expected_kind not in {"absolute", "percentage"}:
                raise AuditInputError(
                    "SCHEMA_ERROR", f"{context}.expected_kind is invalid"
                )
            claim_tolerance = self._tolerance(
                check.get("claim_tolerance"), f"{context}.claim_tolerance"
            )
        elif "expected_kind" in check or "claim_tolerance" in check:
            raise AuditInputError(
                "SCHEMA_ERROR",
                f"{context}.expected_kind/claim_tolerance require expected_low/high",
            )

        calc_records = [actual_low, actual_high, consensus]
        records = calc_records + (
            [expected_low, expected_high]
            if expected_low is not None and expected_high is not None
            else []
        )
        gate_details, issues = self._source_gate(
            records, check.get("source_gate"), f"{context}.source_gate"
        )
        for name, record in (
            (low_field, actual_low),
            (high_field, actual_high),
            ("consensus", consensus),
            ("expected_low", expected_low),
            ("expected_high", expected_high),
        ):
            if record is None:
                continue
            missing = self._missing_issue(record, name)
            if missing:
                issues.append(missing)
            if name in {low_field, high_field}:
                allowed_types = OFFICIAL_TYPES
                requirement = "official"
            elif name == "consensus":
                allowed_types = {"market_data_vendor", "credible_secondary"}
                requirement = "market-data vendor or credible-secondary"
            else:
                allowed_types = ANY_CREDIBLE_TYPES | {"report_under_audit"}
                requirement = "credible or report_under_audit claim"
            self._append_record_source_issue(
                issues, record, name, allowed_types, requirement
            )

        issues.extend(
            self._metadata_issues(
                actual_low, actual_high, low_field, high_field
            )
        )
        for name, record in ((low_field, actual_low), (high_field, actual_high)):
            issues.extend(
                self._metadata_issues(
                    record,
                    consensus,
                    name,
                    "consensus",
                    period=False,
                    basis=True,
                )
            )
        metric = actual_low.metric
        if metric not in SURPRISE_METRICS:
            issues.append(
                _issue(
                    "METRIC_MISMATCH",
                    f"metric {metric!r} is not allowed for expectation_surprise",
                )
            )
        required_unit = (
            "currency_per_share"
            if metric in SURPRISE_PER_SHARE_METRICS
            else "currency"
        )
        if any(record.unit != required_unit for record in calc_records):
            issues.append(
                _issue(
                    "UNIT_MISMATCH",
                    f"metric {metric} requires unit {required_unit}",
                    refs=[low_field, high_field, "consensus"],
                )
            )

        required_subject_period_kind = (
            "duration" if subject_kind == "reported_actual" else "estimate"
        )
        actual_period_valid = (
            actual_low.period.get("kind") == required_subject_period_kind
            and actual_high.period == actual_low.period
        )
        consensus_period_valid = consensus.period.get("kind") == "estimate"
        if not actual_period_valid:
            issues.append(
                _issue(
                    "PERIOD_MISMATCH",
                    f"{low_field}/{high_field} must use the same "
                    f"{required_subject_period_kind} period",
                    refs=[low_field, high_field],
                )
            )
        if not consensus_period_valid:
            issues.append(
                _issue(
                    "PERIOD_MISMATCH",
                    "consensus must use an estimate period",
                    refs=["consensus"],
                )
            )
        if actual_period_valid and consensus_period_valid:
            if subject_kind == "reported_actual":
                subject_start = actual_low.period.get("start")
                subject_end = actual_low.period.get("end")
            else:
                subject_start = actual_low.period.get("target_start")
                subject_end = actual_low.period.get("target_end")
            period_compatible = (
                subject_start == consensus.period.get("target_start")
                and subject_end == consensus.period.get("target_end")
                and actual_low.period.get("frequency")
                == consensus.period.get("frequency")
            )
            if not period_compatible:
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        "subject period must exactly match the consensus target period",
                        refs=[low_field, high_field, "consensus"],
                    )
                )
        if subject_kind == "reported_actual" and actual_period_valid:
            for name, record in ((low_field, actual_low), (high_field, actual_high)):
                information_moment = _parse_aware_timestamp(
                    record.information_at or "",
                    f"{name}.information_at",
                )
                if information_moment != event_moment:
                    issues.append(
                        _issue(
                            "ACTUAL_INFORMATION_NOT_AT_EVENT",
                            f"{name} actual information_at must equal event_at",
                            refs=[name],
                        )
                    )
        if subject_kind == "company_guidance" and actual_period_valid:
            for name, record in ((low_field, actual_low), (high_field, actual_high)):
                formed_at = _parse_aware_timestamp(
                    record.period["expectation_as_of"],
                    f"{name}.expectation_as_of",
                )
                information_at = _parse_aware_timestamp(
                    record.information_at or record.period["expectation_as_of"],
                    f"{name}.information_at",
                )
                if formed_at != event_moment or information_at != event_moment:
                    issues.append(
                        _issue(
                            "EXPECTATION_NOT_POINT_IN_TIME",
                            f"{name} guidance formation/information time must equal event_at",
                            refs=[name],
                        )
                    )
        if consensus_period_valid and not _strictly_before(
            consensus.period["expectation_as_of"],
            event_at,
            "consensus.expectation_as_of",
            f"{context}.event_at",
        ):
            issues.append(
                _issue(
                    "EXPECTATION_NOT_POINT_IN_TIME",
                    "consensus expectation_as_of is not before the event",
                    refs=["consensus"],
                )
            )

        late_consensus_sources = [
            source_id
            for source_id in sorted(consensus.source_ids)
            if not _strictly_before(
                self.sources[source_id]["source_date"],
                event_at,
                f"sources[{source_id}].source_date",
                f"{context}.event_at",
            )
        ]
        if late_consensus_sources:
            issues.append(
                _issue(
                    "EXPECTATION_SOURCE_NOT_POINT_IN_TIME",
                    "every consensus source_date must establish pre-event publication "
                    "or snapshot availability",
                    refs=late_consensus_sources,
                )
            )
        late_actual_sources = sorted(
            {
                source_id
                for record in (actual_low, actual_high)
                for source_id in record.source_ids
                if not _not_after(
                    self.sources[source_id]["source_date"],
                    event_at,
                    f"sources[{source_id}].source_date",
                    f"{context}.event_at",
                )
            }
        )
        if late_actual_sources:
            source_issue_code = (
                "ACTUAL_SOURCE_AFTER_EVENT"
                if subject_kind == "reported_actual"
                else "GUIDANCE_SOURCE_AFTER_EVENT"
            )
            issues.append(
                _issue(
                    source_issue_code,
                    "subject source_date must not be after the stated earnings event",
                    refs=late_actual_sources,
                )
            )

        if (
            actual_low.value is not None
            and actual_high.value is not None
            and actual_low.value > actual_high.value
        ):
            raise AuditInputError(
                "INVALID_RANGE", f"{context} actual_low exceeds actual_high"
            )
        gap_low = (
            actual_low.value - consensus.value
            if actual_low.value is not None and consensus.value is not None
            else None
        )
        gap_high = (
            actual_high.value - consensus.value
            if actual_high.value is not None and consensus.value is not None
            else None
        )
        not_meaningful = (
            actual_low.value is None
            or actual_high.value is None
            or consensus.value is None
            or consensus.value == 0
        )
        allowed = (
            max(absolute, abs(consensus.value) * relative / Decimal(100))
            if consensus.value is not None
            else None
        )
        if not_meaningful:
            status = "not_meaningful"
            percentage_low = percentage_high = None
        else:
            assert gap_low is not None and gap_high is not None and allowed is not None
            percentage_low = gap_low / abs(consensus.value) * Decimal(100)
            percentage_high = gap_high / abs(consensus.value) * Decimal(100)
            if gap_low > allowed:
                status = "beat"
            elif gap_high < -allowed:
                status = "miss"
            elif gap_low >= -allowed and gap_high <= allowed:
                status = "meet"
            else:
                status = "straddles"

        output_basis = f"{actual_low.basis}_vs_pre_event_consensus"
        source_ids = _union_sources(calc_records)
        outputs = {
            "absolute_low": ValueRecord(
                gap_low,
                f"{metric}_surprise_absolute",
                actual_low.unit,
                actual_low.currency,
                actual_low.period,
                output_basis,
                source_ids,
                "dependency_missing" if gap_low is None else None,
            ),
            "absolute_high": ValueRecord(
                gap_high,
                f"{metric}_surprise_absolute",
                actual_high.unit,
                actual_high.currency,
                actual_high.period,
                output_basis,
                source_ids,
                "dependency_missing" if gap_high is None else None,
            ),
            "percentage_low": ValueRecord(
                percentage_low,
                f"{metric}_surprise_pct",
                "percent",
                None,
                actual_low.period,
                output_basis,
                source_ids,
                "not_meaningful" if percentage_low is None else None,
            ),
            "percentage_high": ValueRecord(
                percentage_high,
                f"{metric}_surprise_pct",
                "percent",
                None,
                actual_high.period,
                output_basis,
                source_ids,
                "not_meaningful" if percentage_high is None else None,
            ),
        }
        if expected_low is not None and expected_high is not None:
            if not_meaningful:
                if expected_low.value is not None or expected_high.value is not None:
                    issues.append(
                        _issue(
                            "NUMERIC_CLAIM_NOT_MEANINGFUL",
                            "numeric surprise claim is not meaningful with a zero or missing consensus",
                        )
                    )
            else:
                assert expected_kind is not None and claim_tolerance is not None
                output_low = outputs[f"{expected_kind}_low"]
                output_high = outputs[f"{expected_kind}_high"]
                claim_relative, claim_absolute = claim_tolerance
                for label, calculated, expected in (
                    ("low", output_low, expected_low),
                    ("high", output_high, expected_high),
                ):
                    metadata = self._metadata_issues(
                        calculated,
                        expected,
                        f"calculated_{label}",
                        f"expected_{label}",
                    )
                    issues.extend(metadata)
                    if not metadata and expected.value is not None:
                        conflict = self._numeric_conflict(
                            calculated.value,
                            expected.value,
                            claim_relative,
                            claim_absolute,
                            [f"calculated_{label}", f"expected_{label}"],
                            symmetric=False,
                        )
                        if conflict:
                            issues.append(conflict)
        details = {
            "status": status,
            "subject_kind": subject_kind,
            "formula_absolute": "subject - consensus",
            "formula_percentage": "(subject - consensus) / abs(consensus) * 100",
            "meet_band": "max(absolute_base, abs(consensus) * relative_pct / 100)",
            "allowed_absolute_difference": allowed,
            "expected_kind": expected_kind,
        }
        return outputs, issues, gate_details, details, status

    @staticmethod
    def _valuation_period_issues(record: ValueRecord, ref: str) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        kind = record.period.get("kind")
        if record.metric in {
            *PRICE_METRIC_BASES,
            *MARKET_CAP_METRIC_BASES,
            *STOCK_FUNDAMENTAL_METRICS,
        }:
            if kind != "instant":
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        f"{ref} metric {record.metric} must use an instant period",
                        refs=[ref],
                    )
                )
        elif record.metric in FLOW_FUNDAMENTAL_METRICS:
            frequency = record.period.get("frequency")
            if kind not in {"duration", "estimate"}:
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        f"{ref} metric {record.metric} must use a duration or estimate period",
                        refs=[ref],
                    )
                )
            elif kind == "duration" and frequency not in {"year", "ttm"}:
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        f"{ref} flow must be FY or TTM for a generic valuation",
                        refs=[ref],
                    )
                )
            elif kind == "estimate" and frequency != "year":
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        f"{ref} estimate must target a full fiscal year",
                        refs=[ref],
                    )
                )
        return issues

    @staticmethod
    def _valuation_temporal_alignment_issues(
        metric: str,
        numerator: ValueRecord,
        denominator_low: ValueRecord,
        denominator_high: ValueRecord,
    ) -> list[dict[str, Any]]:
        if metric in YIELD_METRICS:
            pairs = [
                ("denominator_low", denominator_low, "numerator", numerator),
                ("denominator_high", denominator_high, "numerator", numerator),
            ]
        else:
            pairs = [
                ("numerator", numerator, "denominator_low", denominator_low),
                ("numerator", numerator, "denominator_high", denominator_high),
            ]
        issues: list[dict[str, Any]] = []
        for market_ref, market_record, fundamental_ref, fundamental_record in pairs:
            market_as_of = market_record.period.get("as_of")
            if market_record.period.get("kind") != "instant" or not isinstance(
                market_as_of, str
            ):
                continue
            fundamental_kind = fundamental_record.period.get("kind")
            if fundamental_kind == "duration":
                fundamental_cutoff = fundamental_record.period.get("end")
                cutoff_name = "period.end"
            elif fundamental_kind == "estimate":
                fundamental_cutoff = fundamental_record.period.get("expectation_as_of")
                cutoff_name = "expectation_as_of"
            elif fundamental_kind == "instant":
                fundamental_cutoff = fundamental_record.period.get("as_of")
                cutoff_name = "as_of"
            else:
                continue
            if isinstance(fundamental_cutoff, str) and not _not_after(
                fundamental_cutoff,
                market_as_of,
                f"{fundamental_ref}.{cutoff_name}",
                f"{market_ref}.as_of",
            ):
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        f"{market_ref}.as_of is earlier than "
                        f"{fundamental_ref}.{cutoff_name}",
                        refs=[market_ref, fundamental_ref],
                    )
                )
        return issues

    def _valuation_contract_issues(
        self,
        check: dict[str, Any],
        metric: str,
        numerator: ValueRecord,
        denominator_low: ValueRecord,
        denominator_high: ValueRecord,
        valuation_basis: str,
    ) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        if metric == "pe_user_defined":
            annualized_basis = (
                "latest_single_quarter_deducted_attributable_net_profit_x4"
            )
            if numerator.metric != "total_market_cap":
                issues.append(
                    _issue(
                        "METRIC_MISMATCH",
                        "pe_user_defined numerator must be total_market_cap",
                        refs=["numerator"],
                    )
                )
            if numerator.basis != "total_market_cap":
                issues.append(
                    _issue(
                        "BASIS_MISMATCH",
                        "pe_user_defined numerator basis must be total_market_cap",
                        refs=["numerator"],
                    )
                )
            if numerator.period.get("kind") != "instant":
                issues.append(
                    _issue(
                        "PERIOD_MISMATCH",
                        "pe_user_defined market-cap numerator must be instant",
                        refs=["numerator"],
                    )
                )
            for name, record in (
                ("denominator_low", denominator_low),
                ("denominator_high", denominator_high),
            ):
                if record.metric != "deducted_attributable_net_profit":
                    issues.append(
                        _issue(
                            "METRIC_MISMATCH",
                            f"{name} must be deducted_attributable_net_profit",
                            refs=[name],
                        )
                    )
                if record.basis != annualized_basis:
                    issues.append(
                        _issue(
                            "BASIS_MISMATCH",
                            f"{name} must use the fixed x4 annualization basis",
                            refs=[name],
                        )
                    )
            raw_low = check.get("denominator_low")
            raw_high = check.get("denominator_high")
            derived_pair = (
                isinstance(raw_low, dict)
                and isinstance(raw_high, dict)
                and raw_low.get("check_id") == raw_high.get("check_id")
                and raw_low.get("output") == "annualized_low"
                and raw_high.get("output") == "annualized_high"
                and isinstance(raw_low.get("check_id"), str)
            )
            upstream_id = raw_low.get("check_id") if derived_pair else None
            upstream = self.check_results.get(upstream_id) if upstream_id else None
            if not derived_pair or not upstream or upstream.get("kind") != "expectation_gap":
                issues.append(
                    _issue(
                        "DERIVATION_CONTRACT_MISMATCH",
                        "pe_user_defined denominators must be annualized_low/high from "
                        "the same prior expectation_gap check",
                        refs=["denominator_low", "denominator_high"],
                    )
                )
            return issues

        price_metrics = set(PRICE_METRIC_BASES)
        profit_metrics = {
            "net_profit",
            "attributable_net_profit",
            "deducted_attributable_net_profit",
        }
        eps_metrics = {"eps", "earnings_per_share"}
        pairings: dict[str, list[tuple[set[str], set[str]]]] = {
            "pe": [({"total_market_cap"}, profit_metrics), (price_metrics, eps_metrics)],
            "pb": [
                (
                    {"total_market_cap"},
                    {"equity_attributable_to_parent", "book_value"},
                ),
                (price_metrics, {"book_value_per_share", "bvps"}),
            ],
            "ps": [
                ({"total_market_cap"}, {"revenue"}),
                (price_metrics, {"revenue_per_share"}),
            ],
            "p_fcf": [
                ({"total_market_cap"}, {"free_cash_flow"}),
                (price_metrics, {"free_cash_flow_per_share"}),
            ],
            "dividend_yield": [
                ({"cash_dividend"}, {"total_market_cap"}),
                ({"dividend_per_share"}, price_metrics),
            ],
            "earnings_yield": [
                (profit_metrics, {"total_market_cap"}),
                (eps_metrics, price_metrics),
            ],
        }
        if not any(
            numerator.metric in numerator_metrics
            and denominator_low.metric in denominator_metrics
            for numerator_metrics, denominator_metrics in pairings[metric]
        ):
            issues.append(
                _issue(
                    "METRIC_MISMATCH",
                    f"illegal numerator/denominator metric pairing for {metric}",
                    refs=["numerator", "denominator_low", "denominator_high"],
                )
            )

        for name, record in (
            ("numerator", numerator),
            ("denominator_low", denominator_low),
            ("denominator_high", denominator_high),
        ):
            if record.metric in PRICE_METRIC_BASES:
                allowed_bases = PRICE_METRIC_BASES[record.metric]
            elif record.metric in MARKET_CAP_METRIC_BASES:
                allowed_bases = MARKET_CAP_METRIC_BASES[record.metric]
            else:
                allowed_bases = VALUATION_FUNDAMENTAL_BASES.get(record.metric, set())
            if record.basis not in allowed_bases:
                issues.append(
                    _issue(
                        "BASIS_MISMATCH",
                        f"{name} basis {record.basis!r} is invalid for metric {record.metric}",
                        refs=[name],
                    )
                )
            issues.extend(self._valuation_period_issues(record, name))

        fundamental_basis = (
            numerator.basis if metric in YIELD_METRICS else denominator_low.basis
        )
        if valuation_basis != fundamental_basis:
            issues.append(
                _issue(
                    "BASIS_MISMATCH",
                    f"valuation_basis must equal the paired fundamental basis {fundamental_basis!r}",
                )
            )
        issues.extend(
            self._valuation_temporal_alignment_issues(
                metric,
                numerator,
                denominator_low,
                denominator_high,
            )
        )
        return issues

    def _execute_valuation(
        self, check: dict[str, Any], context: str
    ) -> tuple[dict[str, ValueRecord], list[dict[str, Any]], dict[str, Any], dict[str, Any], str]:
        metric = _required_text(check, "metric", context)
        if metric not in VALUATION_METRICS:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.metric is invalid")
        numerator = self._resolve_ref(check.get("numerator"), f"{context}.numerator")
        denominator_low = self._resolve_ref(
            check.get("denominator_low"), f"{context}.denominator_low"
        )
        denominator_high = self._resolve_ref(
            check.get("denominator_high"), f"{context}.denominator_high"
        )
        expected_low_ref = check.get("expected_low")
        expected_high_ref = check.get("expected_high")
        if (expected_low_ref is None) != (expected_high_ref is None):
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.expected_low and expected_high must appear together"
            )
        expected_low = (
            self._resolve_ref(expected_low_ref, f"{context}.expected_low")
            if expected_low_ref is not None
            else None
        )
        expected_high = (
            self._resolve_ref(expected_high_ref, f"{context}.expected_high")
            if expected_high_ref is not None
            else None
        )
        tolerance: tuple[Decimal, Decimal] | None = None
        if expected_low is not None:
            tolerance = self._tolerance(check.get("tolerance"), f"{context}.tolerance")
        elif "tolerance" in check:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.tolerance requires expected_low/high"
            )
        valuation_basis = _required_text(check, "valuation_basis", context)
        if metric == "pe_user_defined" and valuation_basis != (
            "latest_single_quarter_deducted_attributable_net_profit_x4"
        ):
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.valuation_basis is invalid for pe_user_defined"
            )
        records = [numerator, denominator_low, denominator_high] + (
            [expected_low, expected_high] if expected_low and expected_high else []
        )
        gate_details, issues = self._source_gate(
            records, check.get("source_gate"), f"{context}.source_gate"
        )
        for name, record in (
            ("numerator", numerator),
            ("denominator_low", denominator_low),
            ("denominator_high", denominator_high),
            ("expected_low", expected_low),
            ("expected_high", expected_high),
        ):
            if record is not None:
                missing = self._missing_issue(record, name)
                if missing:
                    issues.append(missing)
                self._append_record_source_issue(
                    issues,
                    record,
                    name,
                    (
                        ANY_CREDIBLE_TYPES | {"report_under_audit"}
                        if name in {"expected_low", "expected_high"}
                        else ANY_CREDIBLE_TYPES
                    ),
                    (
                        "credible or report_under_audit claim"
                        if name in {"expected_low", "expected_high"}
                        else "credible"
                    ),
                )
        issues.extend(
            self._metadata_issues(
                denominator_low,
                denominator_high,
                "denominator_low",
                "denominator_high",
            )
        )
        issues.extend(
            self._valuation_contract_issues(
                check,
                metric,
                numerator,
                denominator_low,
                denominator_high,
                valuation_basis,
            )
        )
        if numerator.unit != denominator_low.unit or numerator.unit != denominator_high.unit:
            issues.append(_issue("UNIT_MISMATCH", "valuation numerator and denominators differ"))
        if numerator.unit not in {"currency", "currency_per_share"}:
            issues.append(_issue("UNIT_MISMATCH", "valuation inputs must be monetary"))
        if not (numerator.currency == denominator_low.currency == denominator_high.currency):
            issues.append(_issue("CURRENCY_MISMATCH", "valuation currencies differ"))
        if numerator.value is not None and numerator.value <= 0:
            issues.append(_issue("NONPOSITIVE_INPUT", "valuation numerator must be positive"))
        if (
            denominator_low.value is not None
            and denominator_high.value is not None
            and denominator_low.value > denominator_high.value
        ):
            raise AuditInputError("INVALID_RANGE", f"{context} denominator_low exceeds high")
        output_unit = "multiple" if metric in MULTIPLE_METRICS else "percent"
        output_period = numerator.period
        source_ids = _union_sources(records)
        not_meaningful = (
            denominator_low.value is None
            or denominator_high.value is None
            or denominator_low.value <= 0
            or denominator_high.value <= 0
            or numerator.value is None
        )
        if not_meaningful:
            low_value = high_value = None
            state = "not_meaningful"
            if expected_low is not None and (
                expected_low.value is not None or expected_high.value is not None
            ):
                issues.append(
                    _issue(
                        "NUMERIC_CLAIM_NOT_MEANINGFUL",
                        "a numeric valuation was claimed for a non-meaningful denominator",
                    )
                )
        else:
            multiplier = Decimal(100) if metric in YIELD_METRICS else Decimal(1)
            low_value = numerator.value / denominator_high.value * multiplier
            high_value = numerator.value / denominator_low.value * multiplier
            state = "meaningful"
        outputs = {
            "low": ValueRecord(
                low_value, metric, output_unit, None, output_period, valuation_basis,
                source_ids, "not_meaningful" if low_value is None else None,
            ),
            "high": ValueRecord(
                high_value, metric, output_unit, None, output_period, valuation_basis,
                source_ids, "not_meaningful" if high_value is None else None,
            ),
        }
        if expected_low is not None and not not_meaningful:
            assert tolerance is not None
            relative, absolute = tolerance
            for label, calculated, expected in (
                ("low", outputs["low"], expected_low),
                ("high", outputs["high"], expected_high),
            ):
                metadata = self._metadata_issues(
                    calculated, expected, f"calculated_{label}", f"expected_{label}"
                )
                issues.extend(metadata)
                if not metadata and expected.value is not None:
                    conflict = self._numeric_conflict(
                        calculated.value,
                        expected.value,
                        relative,
                        absolute,
                        [f"calculated_{label}", f"expected_{label}"],
                        symmetric=False,
                    )
                    if conflict:
                        issues.append(conflict)
        details = {
            "formula": (
                "numerator / denominator * 100"
                if metric in YIELD_METRICS
                else "numerator / denominator"
            ),
            "valuation_basis": valuation_basis,
            "state": state,
        }
        return outputs, issues, gate_details, details, state

    def _execute_percentage(
        self, check: dict[str, Any], context: str
    ) -> tuple[dict[str, ValueRecord], list[dict[str, Any]], dict[str, Any], dict[str, Any], str]:
        mode = _required_text(check, "mode", context)
        if mode not in {"ratio", "change"}:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.mode is invalid")
        period_relation = _required_text(check, "period_relation", context)
        if period_relation not in {"same", "sequential", "yoy", "qoq"}:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.period_relation is invalid")
        output_metric = _required_text(check, "output_metric", context)
        output_basis = _required_text(check, "output_basis", context)
        if mode == "ratio":
            left = self._resolve_ref(check.get("numerator"), f"{context}.numerator")
            right = self._resolve_ref(check.get("denominator"), f"{context}.denominator")
            left_name, right_name = "numerator", "denominator"
            if period_relation != "same":
                raise AuditInputError(
                    "SCHEMA_ERROR", f"{context}.ratio requires period_relation=same"
                )
        else:
            if period_relation == "same":
                raise AuditInputError(
                    "SCHEMA_ERROR",
                    f"{context}.change requires sequential, yoy, or qoq period_relation",
                )
            left = self._resolve_ref(check.get("current"), f"{context}.current")
            right = self._resolve_ref(check.get("base"), f"{context}.base")
            left_name, right_name = "current", "base"
        expected_ref = check.get("expected")
        expected = (
            self._resolve_ref(expected_ref, f"{context}.expected")
            if expected_ref is not None
            else None
        )
        tolerance: tuple[Decimal, Decimal] | None = None
        if expected is not None:
            tolerance = self._tolerance(check.get("tolerance"), f"{context}.tolerance")
        elif "tolerance" in check:
            raise AuditInputError(
                "SCHEMA_ERROR", f"{context}.tolerance requires expected"
            )
        records = [left, right] + ([expected] if expected else [])
        gate_details, issues = self._source_gate(
            records, check.get("source_gate"), f"{context}.source_gate"
        )
        for name, record in ((left_name, left), (right_name, right), ("expected", expected)):
            if record is not None:
                missing = self._missing_issue(record, name)
                if missing:
                    issues.append(missing)
                self._append_record_source_issue(
                    issues,
                    record,
                    name,
                    (
                        ANY_CREDIBLE_TYPES | {"report_under_audit"}
                        if name == "expected"
                        else ANY_CREDIBLE_TYPES
                    ),
                    (
                        "credible or report_under_audit claim"
                        if name == "expected"
                        else "credible"
                    ),
                )
        if mode == "change":
            contracted_output_metric = f"{left.metric}_{period_relation}_pct"
            contracted_output_basis = f"{left.basis}_{period_relation}"
        else:
            contracted_output_metric = RATIO_OUTPUT_METRICS.get(
                (left.metric, right.metric)
            )
            contracted_output_basis = f"{left.basis}_over_{right.basis}"
            if contracted_output_metric is None:
                issues.append(
                    _issue(
                        "UNSUPPORTED_RATIO_CONTRACT",
                        f"ratio pairing {left.metric}/{right.metric} is not auditable",
                        refs=[left_name, right_name],
                    )
                )
        if (
            contracted_output_metric is not None
            and output_metric != contracted_output_metric
        ):
            issues.append(
                _issue(
                    "METRIC_MISMATCH",
                    f"output_metric must be {contracted_output_metric}",
                )
            )
        if output_basis != contracted_output_basis:
            issues.append(
                _issue(
                    "BASIS_MISMATCH",
                    f"output_basis must be {contracted_output_basis}",
                )
            )
        issues.extend(
            self._metadata_issues(
                left,
                right,
                left_name,
                right_name,
                metric=mode == "change",
                period=period_relation == "same",
                basis=mode == "change",
            )
        )
        if period_relation != "same":
            if left.period.get("kind") != "duration" or right.period.get("kind") != "duration":
                issues.append(_issue("PERIOD_MISMATCH", "change inputs must be duration periods"))
            else:
                if left.period.get("frequency") != right.period.get("frequency"):
                    issues.append(_issue("PERIOD_MISMATCH", "change frequencies differ"))
                if period_relation == "qoq" and left.period.get("frequency") != "quarter":
                    issues.append(_issue("PERIOD_MISMATCH", "qoq requires quarter frequency"))
                left_span = (
                    _moment_date(left.period["end"], f"{left_name}.period.end")
                    - _moment_date(left.period["start"], f"{left_name}.period.start")
                ).days
                right_span = (
                    _moment_date(right.period["end"], f"{right_name}.period.end")
                    - _moment_date(right.period["start"], f"{right_name}.period.start")
                ).days
                if period_relation in {"qoq", "yoy"} and abs(left_span - right_span) > 15:
                    issues.append(
                        _issue(
                            "PERIOD_MISMATCH",
                            f"comparison period spans differ by {abs(left_span - right_span)} days",
                            refs=[left_name, right_name],
                        )
                    )
                left_end = _moment_date(left.period["end"], f"{left_name}.period.end")
                right_end = _moment_date(right.period["end"], f"{right_name}.period.end")
                elapsed_days = (left_end - right_end).days
                if elapsed_days <= 0:
                    issues.append(_issue("PERIOD_MISMATCH", "current period is not after base"))
                elif period_relation == "qoq" and not 75 <= elapsed_days <= 110:
                    issues.append(
                        _issue(
                            "PERIOD_MISMATCH",
                            f"qoq period ends are {elapsed_days} days apart",
                        )
                    )
                elif period_relation == "yoy" and not 350 <= elapsed_days <= 380:
                    issues.append(
                        _issue(
                            "PERIOD_MISMATCH",
                            f"yoy period ends are {elapsed_days} days apart",
                        )
                    )
        not_meaningful = right.value is None or right.value == 0 or left.value is None
        if not_meaningful:
            calculated = None
            state = "not_meaningful"
            if expected is not None and expected.value is not None:
                issues.append(
                    _issue(
                        "NUMERIC_CLAIM_NOT_MEANINGFUL",
                        "a numeric percentage was claimed with a zero or missing denominator",
                    )
                )
        else:
            if mode == "ratio":
                calculated = left.value / right.value * Decimal(100)
            else:
                calculated = (left.value - right.value) / abs(right.value) * Decimal(100)
            state = "meaningful"
        output = ValueRecord(
            calculated,
            output_metric,
            "percent",
            None,
            left.period,
            output_basis,
            _union_sources(records),
            "not_meaningful" if calculated is None else None,
        )
        if expected is not None and not not_meaningful:
            assert tolerance is not None
            relative, absolute = tolerance
            metadata = self._metadata_issues(output, expected, "calculated", "expected")
            issues.extend(metadata)
            if not metadata and expected.value is not None:
                conflict = self._numeric_conflict(
                    calculated,
                    expected.value,
                    relative,
                    absolute,
                    ["calculated", "expected"],
                    symmetric=False,
                )
                if conflict:
                    issues.append(conflict)
        details = {
            "formula": (
                "numerator / denominator * 100"
                if mode == "ratio"
                else "(current - base) / abs(base) * 100"
            ),
            "state": state,
            "period_relation": period_relation,
            "contracted_output_metric": contracted_output_metric,
            "contracted_output_basis": contracted_output_basis,
        }
        return {"value": output}, issues, gate_details, details, state

    def _execute_check(self, check: dict[str, Any], index: int) -> dict[str, Any]:
        context = f"checks[{index}]"
        check_id = _required_text(check, "id", context)
        kind = _required_text(check, "kind", context)
        materiality = _required_text(check, "materiality", context)
        if kind not in CHECK_KINDS:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.kind is invalid")
        if materiality not in {"material", "supporting"}:
            raise AuditInputError("SCHEMA_ERROR", f"{context}.materiality is invalid")
        try:
            if kind == "cross_source":
                outputs, issues, gate, details, state = self._execute_cross_source(check, context)
            elif kind == "market_cap":
                outputs, issues, gate, details, state = self._execute_market_cap(check, context)
            elif kind == "expectation_gap":
                outputs, issues, gate, details, state = self._execute_expectation_gap(check, context)
            elif kind == "expectation_surprise":
                outputs, issues, gate, details, state = self._execute_expectation_surprise(
                    check, context
                )
            elif kind == "valuation":
                outputs, issues, gate, details, state = self._execute_valuation(check, context)
            else:
                outputs, issues, gate, details, state = self._execute_percentage(check, context)
        except AuditDependencyError as exc:
            issues = [
                _issue(
                    "DEPENDENCY_FAILED",
                    str(exc),
                    refs=[exc.check_id],
                )
            ]
            outputs, gate, details, state = {}, {}, {}, "dependency_failed"
        if issues:
            status = "FAIL" if materiality == "material" else "WARN"
            verified = False
            stored_outputs: dict[str, ValueRecord] = {}
        else:
            status = "PASS"
            verified = True
            stored_outputs = outputs
        result = {
            "id": check_id,
            "kind": kind,
            "materiality": materiality,
            "status": status,
            "verified": verified,
            "state": state,
            "source_gate": gate,
            "outputs": outputs if status == "PASS" else {},
            "details": details,
            "issues": issues,
        }
        self.check_results[check_id] = result
        self.check_outputs[check_id] = stored_outputs
        return result

    def run(self) -> tuple[dict[str, Any], int]:
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            context.Emax = MAX_ADJUSTED_EXPONENT
            context.Emin = -MAX_ADJUSTED_EXPONENT
            try:
                results = [
                    self._execute_check(check, index)
                    for index, check in enumerate(self.checks)
                ]
            except DecimalException as exc:
                raise AuditInputError("DECIMAL_ARITHMETIC_ERROR", str(exc)) from exc
        verified_count = sum(result["verified"] for result in results)
        material_failures = [
            result
            for result in results
            if result["materiality"] == "material" and result["status"] == "FAIL"
        ]
        warnings = [result for result in results if result["status"] == "WARN"]
        blocking_warnings = [
            result
            for result in warnings
            if any(
                issue.get("code") in SUPPORTING_BLOCKING_CODES
                for issue in result.get("issues", [])
            )
        ]
        blocking_results = [*material_failures, *blocking_warnings]
        global_issues: list[dict[str, Any]] = []
        if verified_count == 0:
            global_issues.append(_issue("NO_VERIFIED_CHECKS", "zero checks were verified"))
        verdict = "PASS" if not blocking_results and verified_count > 0 else "FAIL"
        release_status = "publishable" if verdict == "PASS" else "blocked"
        if verdict == "FAIL" and self._provisional_allowed(blocking_results, global_issues):
            release_status = "provisional"
        payload = {
            "schema_version": SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "audit_id": self.payload["audit_id"],
            "input_sha256": self.input_sha256,
            "verdict": verdict,
            "release_status": release_status,
            "summary": {
                "checks_total": len(results),
                "verified_count": verified_count,
                "material_failure_count": len(material_failures),
                "warning_count": len(warnings),
                "blocking_warning_count": len(blocking_warnings),
            },
            "global_issues": global_issues,
            "excluded_sources": self.excluded_sources,
            "checks": results,
        }
        return payload, 0 if verdict == "PASS" else 1

    def _provisional_allowed(
        self,
        blocking_results: list[dict[str, Any]],
        global_issues: list[dict[str, Any]],
    ) -> bool:
        context = self.provisional_context
        if not context or not context["requested"] or not context["fallback_completed"]:
            return False
        blocking_issues = [
            issue for result in blocking_results for issue in result.get("issues", [])
        ]
        if not blocking_issues:
            return False
        if not all(issue.get("provisional_eligible", False) for issue in blocking_issues):
            return False
        return all(issue["code"] == "NO_VERIFIED_CHECKS" for issue in global_issues)


def _reject_json_constant(value: str) -> None:
    raise AuditInputError("NON_FINITE_DECIMAL", f"JSON constant {value} is forbidden")


def load_json(path: str) -> tuple[dict[str, Any], str]:
    try:
        text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditInputError("INPUT_READ_ERROR", f"cannot read audit input: {exc}") from exc
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    try:
        payload = json.loads(
            text,
            parse_float=Decimal,
            parse_constant=_reject_json_constant,
        )
    except AuditInputError:
        raise
    except json.JSONDecodeError as exc:
        raise AuditInputError("INVALID_JSON", f"cannot parse audit input: {exc}") from exc
    if not isinstance(payload, dict):
        raise AuditInputError("SCHEMA_ERROR", "audit input must be an object")
    return payload, digest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic financial arithmetic and evidence audit."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    calc = subparsers.add_parser("calc", help="Evaluate a restricted Decimal expression.")
    calc.add_argument("--expr", required=True)
    calc.add_argument("--pretty", action="store_true")

    audit = subparsers.add_parser("audit", help="Audit a sources/facts/checks JSON package.")
    audit.add_argument("--input", required=True, help="JSON path or '-' for stdin")
    audit.add_argument("--output", help="Optional path for the same machine-readable result")
    audit.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "calc":
            result, rounded = exact_calculate(args.expr)
            payload = {
                "verdict": "PASS",
                "result": result,
                "precision": DECIMAL_PRECISION,
                "rounded": rounded,
            }
            emit(payload, pretty=args.pretty)
            return 0
        if args.input != "-" and args.output is not None:
            input_path = Path(args.input).resolve(strict=False)
            output_path = Path(args.output).resolve(strict=False)
            if input_path == output_path:
                raise AuditInputError(
                    "OUTPUT_OVERWRITES_INPUT",
                    "audit --output must not resolve to the input path",
                )
        audit_payload, digest = load_json(args.input)
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            context.Emax = MAX_ADJUSTED_EXPONENT
            context.Emin = -MAX_ADJUSTED_EXPONENT
            try:
                result, code = AuditEngine(audit_payload, digest).run()
            except DecimalException as exc:
                raise AuditInputError("DECIMAL_ARITHMETIC_ERROR", str(exc)) from exc
        emit(result, pretty=args.pretty, output=args.output)
        return code
    except AuditInputError as exc:
        emit(
            {
                "verdict": "ERROR",
                "release_status": "invalid_input",
                "code": exc.code,
                "error": str(exc),
            },
            pretty=getattr(args, "pretty", False),
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
