"""共享的 2011--2016 上交所原始页面证据准出契约。"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
import re


SSE_MAPPING_SCHEMA_VERSION = "search_addhsl_product_type_mapping_v1"
SSE_DAILY_SQL_ID = "COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C"
SSE_MAPPING_PRODUCT_ORDER = ("40", "1", "2", "48", "43")
SSE_MAPPING_LABEL_ORDER = ("股票", "主板A", "主板B", "科创板", "股票回购")
_SSE_STOCKDAY_BLOCK = re.compile(
    r"\bif\s*\(\s*\$stockday\s*\.\s*length\s*>\s*0\s*\)\s*\{"
)
_SSE_STOCKDAY_OBJECT = re.compile(r"\bvar\s+stockDay\s*=\s*\{")
_SSE_HEADER = re.compile(r"\bvar\s+header\s*=\s*\[")
_SSE_RESULT_LOOP = re.compile(
    r"\bfor\s*\(\s*var\s+i\s*=\s*0\s*;\s*"
    r"i\s*<\s*item\s*\.\s*length\s*;\s*i\s*\+\+\s*\)\s*\{"
)
_SSE_LIST = re.compile(r"\bvar\s+list\s*=\s*\[")
_SSE_BRANCH = re.compile(
    r"(?:\bif|\belse\s+if)\s*\(\s*result\s*\.\s*PRODUCT_TYPE\s*={2,3}\s*"
    r"['\"]([^'\"]+)['\"]\s*\)\s*\{\s*"
    r"([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*createArr\s*\(\s*result\s*\)\s*;?\s*\}",
    re.DOTALL,
)
_SSE_CAL_DATE = re.compile(
    r"(\d{4}-\d{2}-\d{2})(?:[ T]00:00:00(?:\.0+)?)?\Z"
)


def parse_sse_cal_date(value: object) -> date:
    """只接受官方日字段的纯日期或精确零时后缀。"""
    if not isinstance(value, str):
        raise ValueError("SSE CAL_DATE is invalid")
    match = _SSE_CAL_DATE.fullmatch(value.strip())
    if match is None:
        raise ValueError("SSE CAL_DATE is invalid")
    try:
        return date.fromisoformat(match.group(1))
    except ValueError as exc:
        raise ValueError("SSE CAL_DATE is invalid") from exc


def parse_sse_tx_num(value: object) -> Decimal:
    """挂牌数只能是非负整数 Decimal，不接受小数或非有限数。"""
    if value is None or isinstance(value, bool):
        raise ValueError("SSE TX_NUM must be a non-negative integer")
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("SSE TX_NUM must be a non-negative integer") from exc
    if (
        not parsed.is_finite()
        or parsed < 0
        or parsed != parsed.to_integral_value()
    ):
        raise ValueError("SSE TX_NUM must be a non-negative integer")
    return parsed


def _unique_match(pattern: re.Pattern[str], text: str, name: str) -> re.Match[str]:
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"SSE mapping evidence must contain exactly one {name}")
    return matches[0]


def _balanced_body(
    text: str, opening_index: int, opening: str, closing: str, name: str
) -> str:
    """返回 JS 字符串/注释感知的成对分隔符内部内容。"""
    if opening_index < 0 or text[opening_index] != opening:
        raise ValueError(f"SSE mapping evidence has invalid {name} boundary")

    depth = 0
    state = "code"
    index = opening_index
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "'":
                state = "single_quote"
            elif char == '"':
                state = "double_quote"
            elif char == "`":
                state = "template_quote"
            elif char == "/" and next_char == "/":
                state = "line_comment"
                index += 1
            elif char == "/" and next_char == "*":
                state = "block_comment"
                index += 1
            elif char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    return text[opening_index + 1 : index]
                if depth < 0:
                    break
        elif state in {"single_quote", "double_quote", "template_quote"}:
            quote = {
                "single_quote": "'",
                "double_quote": '"',
                "template_quote": "`",
            }[state]
            if char == "\\":
                index += 1
            elif char == quote:
                state = "code"
        elif state == "line_comment":
            if char in "\r\n":
                state = "code"
        elif state == "block_comment" and char == "*" and next_char == "/":
            state = "code"
            index += 1
        index += 1
    raise ValueError(f"SSE mapping evidence has unclosed {name}")


def _split_top_level_js_object_segments(text: str, name: str) -> list[str]:
    """按顶层逗号切开对象属性，不把字符串或注释内文本当作代码。"""
    segments: list[str] = []
    start = 0
    nested_depth = 0
    state = "code"
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "'":
                state = "single_quote"
            elif char == '"':
                state = "double_quote"
            elif char == "`":
                state = "template_quote"
            elif char == "/" and next_char == "/":
                state = "line_comment"
                index += 1
            elif char == "/" and next_char == "*":
                state = "block_comment"
                index += 1
            elif char in "{[(":
                nested_depth += 1
            elif char in "}])":
                nested_depth -= 1
                if nested_depth < 0:
                    raise ValueError(f"SSE mapping evidence has invalid {name}")
            elif char == "," and nested_depth == 0:
                segments.append(text[start:index])
                start = index + 1
        elif state in {"single_quote", "double_quote", "template_quote"}:
            quote = {
                "single_quote": "'",
                "double_quote": '"',
                "template_quote": "`",
            }[state]
            if char == "\\":
                index += 1
            elif char == quote:
                state = "code"
        elif state == "line_comment":
            if char in "\r\n":
                state = "code"
        elif state == "block_comment" and char == "*" and next_char == "/":
            state = "code"
            index += 1
        index += 1
    if state in {"single_quote", "double_quote", "template_quote", "block_comment"}:
        raise ValueError(f"SSE mapping evidence has unclosed {name}")
    if nested_depth != 0:
        raise ValueError(f"SSE mapping evidence has invalid {name}")
    segments.append(text[start:])
    return segments


def _strip_js_comments(text: str) -> str:
    cleaned: list[str] = []
    state = "code"
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char in {"'", '"', "`"}:
                state = {"'": "single_quote", '"': "double_quote", "`": "template_quote"}[char]
                cleaned.append(char)
            elif char == "/" and next_char == "/":
                state = "line_comment"
                cleaned.append(" ")
                index += 1
            elif char == "/" and next_char == "*":
                state = "block_comment"
                cleaned.append(" ")
                index += 1
            else:
                cleaned.append(char)
        elif state in {"single_quote", "double_quote", "template_quote"}:
            quote = {
                "single_quote": "'",
                "double_quote": '"',
                "template_quote": "`",
            }[state]
            cleaned.append(char)
            if char == "\\" and index + 1 < len(text):
                index += 1
                cleaned.append(text[index])
            elif char == quote:
                state = "code"
        elif state == "line_comment":
            if char in "\r\n":
                cleaned.append(char)
                state = "code"
        elif state == "block_comment" and char == "*" and next_char == "/":
            state = "code"
            index += 1
        index += 1
    if state in {"single_quote", "double_quote", "template_quote", "block_comment"}:
        raise ValueError("SSE mapping evidence has unclosed stockDay parms")
    return "".join(cleaned)


def _direct_js_object_properties(text: str, name: str) -> dict[str, str]:
    properties: dict[str, str] = {}
    for segment in _split_top_level_js_object_segments(text, name):
        cleaned = _strip_js_comments(segment).strip()
        if not cleaned:
            continue
        match = re.fullmatch(
            r"([A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*(.+?)\s*", cleaned, re.DOTALL
        )
        if match is None:
            raise ValueError(f"SSE mapping evidence has invalid {name} property")
        key, value = match.groups()
        if key in properties:
            raise ValueError(f"SSE mapping evidence has duplicate {name} property {key}")
        properties[key] = value
    return properties


def _is_exact_js_string(value: str, expected: str) -> bool:
    match = re.fullmatch(r"\s*(['\"])(.*?)\1\s*", value, re.DOTALL)
    return match is not None and match.group(2) == expected


def _direct_braced_js_object_body(value: str, name: str) -> str:
    cleaned = _strip_js_comments(value).strip()
    if not cleaned.startswith("{"):
        raise ValueError(f"SSE mapping evidence has invalid {name}")
    body = _balanced_body(cleaned, 0, "{", "}", name)
    closing_index = len(body) + 1
    if cleaned[closing_index + 1 :].strip():
        raise ValueError(f"SSE mapping evidence has invalid {name}")
    return body


def _ordered_positions(text: str, values: tuple[str, ...], name: str) -> None:
    cursor = 0
    for value in values:
        position = text.find(value, cursor)
        if position < 0:
            raise ValueError(f"SSE mapping evidence is missing {name} {value}")
        cursor = position + len(value)


def _require_stockday_parameter_contract(stockday_object: str) -> None:
    stockday_properties = _direct_js_object_properties(
        stockday_object, "stockDay object"
    )
    parms_value = stockday_properties.get("parms")
    if parms_value is None:
        raise ValueError("SSE mapping evidence is missing stockDay parms")
    parms = _direct_braced_js_object_body(parms_value, "stockDay parms")
    properties = _direct_js_object_properties(parms, "stockDay parms")
    if "searchDate" not in properties or not properties["searchDate"].strip():
        raise ValueError("SSE stockDay parms is missing searchDate")
    if not _is_exact_js_string(properties.get("sqlId", ""), SSE_DAILY_SQL_ID):
        raise ValueError("SSE stockDay parms must bind daily SQL id through sqlId")
    if not _is_exact_js_string(properties.get("stockType", ""), "90"):
        raise ValueError("SSE stockDay parms is missing stockType=90")
    if set(properties) != {"searchDate", "sqlId", "stockType"}:
        raise ValueError("SSE stockDay parms property keys are not exact")


def _require_stockday_header(stockday_object: str) -> None:
    header_match = _unique_match(_SSE_HEADER, stockday_object, "stockDay header")
    header = _balanced_body(
        stockday_object,
        header_match.end() - 1,
        "[",
        "]",
        "stockDay header",
    )
    _ordered_positions(
        header,
        ("单日情况",) + SSE_MAPPING_LABEL_ORDER,
        "stockDay header",
    )


def _require_stockday_product_type_mapping(stockday_object: str) -> None:
    loop_match = _unique_match(_SSE_RESULT_LOOP, stockday_object, "stockDay item loop")
    loop = _balanced_body(
        stockday_object,
        loop_match.end() - 1,
        "{",
        "}",
        "stockDay item loop",
    )
    if re.search(r"\bvar\s+result\s*=\s*item\s*\[\s*i\s*\]\s*;", loop) is None:
        raise ValueError("SSE stockDay item loop is missing result binding")
    observed = [(match.group(1), match.group(2)) for match in _SSE_BRANCH.finditer(loop)]
    expected = [
        ("40", "arrA"),
        ("1", "arrB"),
        ("2", "arrC"),
        ("43", "arrF"),
        ("48", "arrG"),
    ]
    if observed != expected:
        raise ValueError("SSE stockDay PRODUCT_TYPE branch mapping is not exact")


def _require_stockday_market_cap_render_order(stockday_object: str) -> None:
    list_match = _unique_match(_SSE_LIST, stockday_object, "stockDay list")
    list_body = _balanced_body(
        stockday_object,
        list_match.end() - 1,
        "[",
        "]",
        "stockDay list",
    )
    market_row_matches = list(
        re.finditer(r"\[\s*['\"]市价总值\(亿元\)['\"]", list_body)
    )
    if len(market_row_matches) != 1:
        raise ValueError("SSE stockDay list must contain exactly one 市价总值(亿元) row")
    market_row = _balanced_body(
        list_body,
        market_row_matches[0].start(),
        "[",
        "]",
        "stockDay 市价总值 row",
    )
    reference_patterns = (
        r"arrA\s*\[\s*5\s*\]",
        r"arrB\s*\[\s*5\s*\]",
        r"arrC\s*\[\s*5\s*\]",
        r"arrG\s*\[\s*5\s*\]",
        r"arrF\s*\[\s*5\s*\]",
    )
    cursor = 0
    for pattern in reference_patterns:
        matches = list(re.finditer(pattern, market_row))
        if len(matches) != 1 or matches[0].start() < cursor:
            raise ValueError("SSE stockDay 市价总值 row render order is not exact")
        cursor = matches[0].end()


def parse_sse_stockday_mapping_evidence(payload: bytes) -> dict[str, object]:
    """只认可 `$stockday` 顶层块内、`stockType=90` 日股票对象的映射。"""
    if not payload:
        raise ValueError("SSE mapping evidence is empty")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("SSE mapping evidence is not UTF-8") from exc

    stockday_match = _unique_match(
        _SSE_STOCKDAY_BLOCK, text, "$stockday top-level block"
    )
    stockday_block = _balanced_body(
        text,
        stockday_match.end() - 1,
        "{",
        "}",
        "$stockday top-level block",
    )
    stockday_object_match = _unique_match(
        _SSE_STOCKDAY_OBJECT, stockday_block, "stockDay object"
    )
    stockday_object = _balanced_body(
        stockday_block,
        stockday_object_match.end() - 1,
        "{",
        "}",
        "stockDay object",
    )
    _require_stockday_parameter_contract(stockday_object)
    _require_stockday_header(stockday_object)
    _require_stockday_product_type_mapping(stockday_object)
    _require_stockday_market_cap_render_order(stockday_object)
    return {
        "schema_version": SSE_MAPPING_SCHEMA_VERSION,
        "header_order": list(SSE_MAPPING_LABEL_ORDER),
        "product_type_order": list(SSE_MAPPING_PRODUCT_ORDER),
        "product_type_mapping": {
            "40": "股票",
            "1": "主板A",
            "2": "主板B",
            "48": "科创板",
            "43": "股票回购",
        },
    }
