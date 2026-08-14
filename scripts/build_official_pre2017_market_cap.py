import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
from io import BytesIO
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import unicodedata

import pandas as pd
import requests


_SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(_SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIRECTORY))
from official_pre2017_contract import (
    parse_sse_cal_date,
    parse_sse_stockday_mapping_evidence,
    parse_sse_tx_num,
)


SSE_QUERY_URL = "https://query.sse.com.cn/commonQuery.do"
SSE_MAPPING_EVIDENCE_URL = (
    "https://www.sse.com.cn/xhtml/home/public/querySearch/search_addhsl.js"
)
SSE_HEADERS = {
    "Referer": "https://www.sse.com.cn/market/stockdata/overview/day/index_his.shtml",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
}
SSE_LEGACY_PARAMETERS = {
    "sqlId": "COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C",
    "stockType": "90",
}
SZSE_SHOW_REPORT_URL = "https://www.szse.cn/api/report/ShowReport"
SZSE_SHOW_REPORT_PARAMETERS = {
    "SHOWTYPE": "xlsx",
    "CATALOGID": "1803_sczm",
    "TABKEY": "tab1",
}
SZSE_HEADERS = {
    "Referer": "https://www.szse.cn/market/overview/index.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
}

EARLIEST_SUPPORTED_DATE = date(2011, 8, 3)
PRE2017_CUTOFF = date(2017, 1, 3)
LATEST_PRE2017_DATE = date(2016, 12, 30)
OUTPUT_DIRECTORY = Path("artifacts/leverage_capitulation/official_pre2017_market_cap")
LEGACY_RAW_RELATIVE_ROOT = Path(
    "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
)
DFCF_RELATIVE_PATH = Path(
    "artifacts/leverage_capitulation/dfcf_daily/dfcf_margin_balances.csv"
)
SSE_SCHEMA_VERSION = "legacy_product_type"
SSE_MAPPING_SCHEMA_VERSION = "search_addhsl_product_type_mapping_v1"
SZSE_SCHEMA_VERSION = "show_report_xlsx"
SOURCE_SEGMENT = "official_exchange_pre_2017"
SSE_EXPECTED_PRODUCT_TYPES = ("1", "2", "12")
SSE_MAPPING_PRODUCT_ORDER = ("40", "1", "2", "48", "43")
SSE_MAPPING_BRANCH_ORDER = ("40", "1", "2", "43", "48")
SSE_MAPPING_LABEL_ORDER = ("股票", "主板A", "主板B", "科创板", "股票回购")
SSE_DAILY_SQL_ID = "COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C"
SSE_PRODUCT_TOTAL_ABSOLUTE_TOLERANCE = Decimal("0.00000001")
SSE_TX_NUM_ABSOLUTE_TOLERANCE = Decimal("0")
SZSE_STOCK_TOTAL_ABSOLUTE_TOLERANCE_YUAN = Decimal("0.10")
SZSE_GAP_FETCH_DATE = date(2015, 6, 11)
OUTPUT_COLUMNS = [
    "date",
    "sh_a_market_cap_yi",
    "sz_a_market_cap_yi",
    "market_cap_yi",
    "source_segment",
    "status",
    "sse_raw_sha256",
    "szse_raw_sha256",
]
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_SZSE_HEADERS = (
    "证券类别",
    "数量(只)",
    "成交金额(元)",
    "总市值(元)",
    "流通市值(元)",
)
SSE_MAPPING_RELATIVE_PATH = Path("raw/sse_mapping/search_addhsl.js")
SZSE_OUTPUT_RAW_RELATIVE_DIRECTORY = Path("raw/szse")
OFFICIAL_AUDIT_FILENAME = "official_pre2017_market_cap_audit.json"


@dataclass(frozen=True)
class RequestOptions:
    session: object | None
    sleep_seconds: float
    timeout_seconds: int
    max_retries: int


@dataclass(frozen=True)
class LegacySzsePayload:
    payload: bytes
    entry: dict[str, object]
    market_cap_yi: Decimal
    storage: str = "legacy_read_only"


@dataclass(frozen=True)
class SseMappingEvidence:
    payload: bytes
    entry: dict[str, object]
    parsed: dict[str, object]


def _normalise_text(value: object) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(value)))


def _strict_date(value: object, *, field_name: str = "date") -> date:
    if isinstance(value, datetime):
        raise ValueError(f"{field_name} must not include a time")
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError(f"{field_name} must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} is invalid") from exc


def _source_date(value: object) -> date:
    return parse_sse_cal_date(value)


def _positive_decimal(value: object, *, field_name: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive Decimal")
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError(f"{field_name} must be a positive Decimal")
    try:
        amount = (
            value
            if isinstance(value, Decimal)
            else Decimal(str(value).strip().replace(",", ""))
        )
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive Decimal") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError(f"{field_name} must be a positive Decimal")
    return amount


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"SSE JSON contains non-finite value: {value}")


def parse_sse_mapping_evidence(payload: bytes) -> dict[str, object]:
    """验证上交所页面 JS 的历史 PRODUCT_TYPE 文字映射证据。"""
    return parse_sse_stockday_mapping_evidence(payload)


def parse_legacy_sse_payload(payload: bytes, trade_date: date) -> Decimal:
    """Return only SSE pre-2017 PRODUCT_TYPE=1 market cap, in 亿元."""
    if not payload:
        raise ValueError("SSE response is empty")
    try:
        decoded = json.loads(
            payload.decode("utf-8"),
            parse_float=Decimal,
            parse_int=Decimal,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("SSE response is not valid JSON") from exc
    if not isinstance(decoded, dict) or not isinstance(decoded.get("result"), list):
        raise ValueError("SSE response has no result list")
    rows = decoded["result"]
    if not rows:
        raise ValueError("SSE response result is empty")

    values: dict[str, Decimal] = {}
    tx_numbers: dict[str, Decimal] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("SSE result row is not an object")
        if _source_date(row.get("CAL_DATE")) != trade_date:
            raise ValueError("SSE CAL_DATE does not match requested date")
        product_type = _normalise_text(row.get("PRODUCT_TYPE", ""))
        if product_type not in SSE_EXPECTED_PRODUCT_TYPES:
            raise ValueError(f"unknown SSE PRODUCT_TYPE: {product_type}")
        if product_type in values:
            raise ValueError(f"duplicate SSE PRODUCT_TYPE: {product_type}")
        values[product_type] = _positive_decimal(
            row.get("MKT_VALUE_FULL"), field_name="SSE MKT_VALUE_FULL"
        )
        tx_numbers[product_type] = parse_sse_tx_num(row.get("TX_NUM"))
    if set(values) != set(SSE_EXPECTED_PRODUCT_TYPES):
        raise ValueError("SSE PRODUCT_TYPE set must be exactly 1, 2, 12")
    if abs(values["12"] - (values["1"] + values["2"])) > SSE_PRODUCT_TOTAL_ABSOLUTE_TOLERANCE:
        raise ValueError("SSE PRODUCT_TYPE=12 MKT_VALUE_FULL must equal 1 + 2")
    if set(tx_numbers) != set(SSE_EXPECTED_PRODUCT_TYPES):
        raise ValueError("SSE TX_NUM must be present for PRODUCT_TYPE 1, 2, 12")
    if abs(tx_numbers["12"] - (tx_numbers["1"] + tx_numbers["2"])) > SSE_TX_NUM_ABSOLUTE_TOLERANCE:
        raise ValueError("SSE PRODUCT_TYPE=12 TX_NUM must equal 1 + 2")
    return values["1"]


def parse_old_szse_workbook(payload: bytes, trade_date: date) -> Decimal:
    """Parse only the pre-2017 SZSE A-category rows from a verified old workbook."""
    del trade_date  # The historic workbook carries no authoritative date field.
    if not payload:
        raise ValueError("SZSE workbook is empty")
    try:
        frame = pd.read_excel(BytesIO(payload), header=0, dtype=object)
    except Exception as exc:
        raise ValueError("SZSE workbook cannot be parsed") from exc
    headers = tuple(_normalise_text(column) for column in frame.columns)
    if headers[: len(_SZSE_HEADERS)] != _SZSE_HEADERS:
        raise ValueError("SZSE workbook header does not match the historic schema")

    categories = {
        "股票": "stock_total",
        "主板A股": "main_a",
        "主板B股": "main_b",
        "中小板": "sme_a",
        "中小板A股": "sme_a",
        "创业板": "chinext_a",
        "创业板A股": "chinext_a",
    }
    values: dict[str, Decimal] = {}
    category_column = frame.columns[0]
    market_cap_column = frame.columns[3]
    for _, row in frame.iterrows():
        category = categories.get(_normalise_text(row[category_column]))
        if category is None:
            continue
        if category in values:
            raise ValueError(f"duplicate SZSE A category: {category}")
        values[category] = _positive_decimal(
            row[market_cap_column], field_name="SZSE total market cap"
        )
    required = {"stock_total", "main_a", "main_b", "sme_a", "chinext_a"}
    missing = required - set(values)
    if missing:
        raise ValueError(f"SZSE required category is missing: {sorted(missing)}")
    a_market_cap = values["main_a"] + values["sme_a"] + values["chinext_a"]
    residual = values["stock_total"] - (a_market_cap + values["main_b"])
    if abs(residual) > SZSE_STOCK_TOTAL_ABSOLUTE_TOLERANCE_YUAN:
        raise ValueError("SZSE 股票总市值 must equal A + B within 0.10 元")
    return a_market_cap / Decimal("100000000")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _csv_bytes(frame: pd.DataFrame) -> bytes:
    serializable = frame.copy()
    for column in serializable.columns:
        serializable[column] = serializable[column].map(
            lambda value: format(value, "f") if isinstance(value, Decimal) else value
        )
    return serializable.to_csv(index=False, lineterminator="\n").encode("utf-8")


def atomic_write_bytes(payload: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def atomic_write_json(payload: object, path: Path) -> None:
    atomic_write_bytes(_json_bytes(payload), path)


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    atomic_write_bytes(_csv_bytes(frame), path)


def _legacy_sse_parameters(trade_date: date) -> dict[str, object]:
    _strict_requested_dates([trade_date])
    return {
        **SSE_LEGACY_PARAMETERS,
        "searchDate": trade_date.isoformat(),
    }


def _request_with_retry(
    options: RequestOptions, *, params: dict[str, object]
) -> tuple[bytes, int]:
    if not isinstance(params, dict):
        raise ValueError("SSE legacy searchDate parameters are invalid")
    search_date = _strict_date(
        params.get("searchDate"), field_name="SSE legacy searchDate"
    )
    expected_params = _legacy_sse_parameters(search_date)
    if params != expected_params:
        raise ValueError("SSE legacy searchDate parameters are invalid")
    if options.session is None:
        raise RuntimeError("SSE request session is unavailable")
    last_error: Exception | None = None
    for attempt in range(options.max_retries + 1):
        try:
            response = options.session.get(
                SSE_QUERY_URL,
                params=params,
                headers=SSE_HEADERS,
                timeout=options.timeout_seconds,
            )
            if getattr(response, "status_code", None) != 200:
                raise ValueError(
                    f"SSE HTTP status is {getattr(response, 'status_code', None)}"
                )
            payload = getattr(response, "content", None)
            if not isinstance(payload, bytes) or not payload:
                raise ValueError("SSE HTTP response is empty")
            return payload, attempt + 1
        except (OSError, requests.RequestException, TypeError, ValueError) as exc:
            last_error = exc
            if attempt < options.max_retries:
                time.sleep(2**attempt)
    raise RuntimeError(
        f"SSE request failed after {options.max_retries + 1} attempts: {last_error}"
    )


def _request_static_sse_mapping(options: RequestOptions) -> tuple[bytes, int]:
    if options.session is None:
        raise RuntimeError("SSE mapping request session is unavailable")
    last_error: Exception | None = None
    for attempt in range(options.max_retries + 1):
        try:
            response = options.session.get(
                SSE_MAPPING_EVIDENCE_URL,
                params={},
                headers=SSE_HEADERS,
                timeout=options.timeout_seconds,
            )
            if getattr(response, "status_code", None) != 200:
                raise ValueError(
                    "SSE mapping HTTP status is "
                    f"{getattr(response, 'status_code', None)}"
                )
            payload = getattr(response, "content", None)
            if not isinstance(payload, bytes) or not payload:
                raise ValueError("SSE mapping HTTP response is empty")
            parse_sse_mapping_evidence(payload)
            return payload, attempt + 1
        except (OSError, requests.RequestException, TypeError, ValueError) as exc:
            last_error = exc
            if attempt < options.max_retries:
                time.sleep(2**attempt)
    raise RuntimeError(
        "SSE mapping request failed after "
        f"{options.max_retries + 1} attempts: {last_error}"
    )


def fetch_sse_mapping_evidence(
    options: RequestOptions,
) -> tuple[bytes, dict[str, object], int]:
    payload, attempts = _request_static_sse_mapping(options)
    return payload, parse_sse_mapping_evidence(payload), attempts


def _szse_parameters(trade_date: date) -> dict[str, object]:
    _strict_requested_dates([trade_date])
    return {
        **SZSE_SHOW_REPORT_PARAMETERS,
        "txtQueryDate": trade_date.isoformat(),
    }


def fetch_szse_show_report(
    trade_date: date, options: RequestOptions
) -> tuple[bytes, dict[str, object], int]:
    if trade_date != SZSE_GAP_FETCH_DATE:
        raise ValueError("only 2015-06-11 may be fetched into the new SZSE raw chain")
    if options.session is None:
        raise RuntimeError("SZSE request session is unavailable")
    params = _szse_parameters(trade_date)
    last_error: Exception | None = None
    for attempt in range(options.max_retries + 1):
        try:
            response = options.session.get(
                SZSE_SHOW_REPORT_URL,
                params=params,
                headers=SZSE_HEADERS,
                timeout=options.timeout_seconds,
            )
            if getattr(response, "status_code", None) != 200:
                raise ValueError(
                    f"SZSE HTTP status is {getattr(response, 'status_code', None)}"
                )
            payload = getattr(response, "content", None)
            if not isinstance(payload, bytes) or not payload:
                raise ValueError("SZSE HTTP response is empty")
            parse_old_szse_workbook(payload, trade_date)
            return payload, params, attempt + 1
        except (OSError, requests.RequestException, TypeError, ValueError) as exc:
            last_error = exc
            if attempt < options.max_retries:
                time.sleep(max(1, 2**attempt))
    raise RuntimeError(
        f"SZSE request failed after {options.max_retries + 1} attempts: {last_error}"
    )


def fetch_legacy_sse(
    trade_date: date, options: RequestOptions
) -> tuple[bytes, dict[str, object], int]:
    params = _legacy_sse_parameters(trade_date)
    payload, attempts = _request_with_retry(options, params=params)
    return payload, params, attempts


def _dfcf_path(project_root: Path) -> Path:
    return project_root / DFCF_RELATIVE_PATH


def load_dfcf_pre2017_common_dates(
    project_root: Path, start_date: date, end_date: date
) -> list[date]:
    if start_date > end_date:
        raise ValueError("--start-date cannot be later than --end-date")
    if start_date < EARLIEST_SUPPORTED_DATE:
        raise ValueError("pre-2017 official market-cap start cannot precede 2011-08-03")
    if end_date > LATEST_PRE2017_DATE:
        raise ValueError("pre-2017 official market-cap end cannot exceed 2016-12-30")
    input_path = _dfcf_path(project_root)
    if not input_path.exists():
        raise FileNotFoundError(f"DFCF common-date table is missing: {input_path}")
    frame = pd.read_csv(input_path, encoding="utf-8-sig", dtype={"date": "string"})
    if "date" not in frame.columns:
        raise ValueError("DFCF common-date table has no date column")
    dates = [_strict_date(value, field_name="DFCF date") for value in frame["date"]]
    if len(dates) != len(set(dates)):
        raise ValueError("DFCF common-date table has duplicate dates")
    if dates != sorted(dates):
        raise ValueError("DFCF common-date table dates are not ascending")
    return [
        value
        for value in dates
        if start_date <= value <= end_date and value < PRE2017_CUTOFF
    ]


def _strict_requested_dates(dates: list[date]) -> list[date]:
    if any(isinstance(value, datetime) or not isinstance(value, date) for value in dates):
        raise ValueError("requested dates must be date values without a time")
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError("requested dates must be unique and ascending")
    if any(
        value < EARLIEST_SUPPORTED_DATE or value >= PRE2017_CUTOFF for value in dates
    ):
        raise ValueError("requested dates must be in 2011-08-03..2016-12-30")
    return dates


def _require_dfcf_common_dates(project_root: Path, requested: list[date]) -> None:
    common_dates = set(
        load_dfcf_pre2017_common_dates(
            project_root, EARLIEST_SUPPORTED_DATE, LATEST_PRE2017_DATE
        )
    )
    unavailable = [
        value.isoformat() for value in requested if value not in common_dates
    ]
    if unavailable:
        raise ValueError(
            "requested date is not a DFCF common date: " + ", ".join(unavailable)
        )


def resolve_legacy_raw_root(project_root: Path, value: str | Path | None) -> Path:
    if value is None:
        return (project_root / LEGACY_RAW_RELATIVE_ROOT).resolve()
    candidate = Path(value)
    return (
        candidate.resolve()
        if candidate.is_absolute()
        else (project_root / candidate).resolve()
    )


def _read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _expected_old_szse_entry(trade_date: date) -> dict[str, object]:
    return {
        "date": trade_date.isoformat(),
        "market": "SZSE",
        "source_url": SZSE_SHOW_REPORT_URL,
        "request_parameters": {
            **SZSE_SHOW_REPORT_PARAMETERS,
            "txtQueryDate": trade_date.isoformat(),
        },
        "relative_path": f"raw/{trade_date.isoformat()}_szse.xlsx",
        "schema_version": SZSE_SCHEMA_VERSION,
    }


def _normalised_old_szse_entry(
    entry: dict[str, object], trade_date: date
) -> dict[str, object] | None:
    expected = _expected_old_szse_entry(trade_date)
    required = {
        *expected,
        "sha256",
        "bytes",
        "retrieved_at_utc",
    }
    if not required.issubset(entry):
        return None
    if any(entry[key] != value for key, value in expected.items()):
        return None
    if (
        not isinstance(entry["sha256"], str)
        or _SHA256_RE.fullmatch(entry["sha256"]) is None
        or not isinstance(entry["bytes"], int)
        or isinstance(entry["bytes"], bool)
        or entry["bytes"] <= 0
        or not isinstance(entry["retrieved_at_utc"], str)
        or not entry["retrieved_at_utc"]
    ):
        return None
    return {
        **expected,
        "sha256": entry["sha256"],
        "bytes": entry["bytes"],
        "retrieved_at_utc": entry["retrieved_at_utc"],
    }


def _load_old_szse(
    legacy_raw_root: Path, legacy_manifest: list[dict[str, object]], trade_date: date
) -> tuple[LegacySzsePayload | None, str]:
    entries = [
        entry
        for entry in legacy_manifest
        if entry.get("date") == trade_date.isoformat() and entry.get("market") == "SZSE"
    ]
    if len(entries) != 1:
        return None, "legacy SZSE manifest entry is missing or duplicate"
    entry = _normalised_old_szse_entry(entries[0], trade_date)
    if entry is None:
        return None, "legacy SZSE manifest entry is invalid"
    try:
        raw_root = legacy_raw_root.resolve()
        raw_path = (legacy_raw_root / str(entry["relative_path"])).resolve()
        if not raw_path.is_relative_to(raw_root):
            return None, "legacy SZSE raw path escapes configured root"
        payload = raw_path.read_bytes()
        if (
            len(payload) != entry["bytes"]
            or hashlib.sha256(payload).hexdigest() != entry["sha256"]
        ):
            return None, "legacy SZSE raw hash or byte count does not match manifest"
        return (
            LegacySzsePayload(
                payload=payload,
                entry=entry,
                market_cap_yi=parse_old_szse_workbook(payload, trade_date),
            ),
            "",
        )
    except (OSError, ValueError):
        return None, "legacy SZSE raw file is unreadable or cannot be parsed"


def _sse_relative_path(trade_date: date) -> Path:
    return Path("raw/sse") / f"{trade_date.isoformat()}.json"


def _sse_mapping_entry(payload: bytes, parsed: dict[str, object]) -> dict[str, object]:
    return {
        "source_url": SSE_MAPPING_EVIDENCE_URL,
        "relative_path": SSE_MAPPING_RELATIVE_PATH.as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "schema_version": SSE_MAPPING_SCHEMA_VERSION,
        "parsed": parsed,
    }


def _validated_sse_mapping(
    output_dir: Path, manifest: object
) -> SseMappingEvidence | None:
    if not isinstance(manifest, dict):
        return None
    entry = manifest.get("sse_mapping_evidence")
    if not isinstance(entry, dict):
        return None
    required = {
        "source_url": SSE_MAPPING_EVIDENCE_URL,
        "relative_path": SSE_MAPPING_RELATIVE_PATH.as_posix(),
        "schema_version": SSE_MAPPING_SCHEMA_VERSION,
    }
    if any(entry.get(key) != value for key, value in required.items()):
        return None
    if (
        not isinstance(entry.get("sha256"), str)
        or _SHA256_RE.fullmatch(entry["sha256"]) is None
        or not isinstance(entry.get("bytes"), int)
        or isinstance(entry["bytes"], bool)
        or entry["bytes"] <= 0
    ):
        return None
    try:
        root = output_dir.resolve()
        raw_path = (output_dir / str(entry["relative_path"])).resolve()
        if not raw_path.is_relative_to(root):
            return None
        payload = raw_path.read_bytes()
        if len(payload) != entry["bytes"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            return None
        parsed = parse_sse_mapping_evidence(payload)
        if entry.get("parsed") != parsed:
            return None
        return SseMappingEvidence(payload=payload, entry=entry, parsed=parsed)
    except (OSError, ValueError):
        return None


def _szse_output_relative_path(trade_date: date) -> Path:
    return SZSE_OUTPUT_RAW_RELATIVE_DIRECTORY / f"{trade_date.isoformat()}.xlsx"


def _new_szse_entry(
    trade_date: date, params: dict[str, object], payload: bytes
) -> dict[str, object]:
    if trade_date != SZSE_GAP_FETCH_DATE:
        raise ValueError("only 2015-06-11 may be stored in the new SZSE raw chain")
    return {
        "date": trade_date.isoformat(),
        "market": "SZSE",
        "source_url": SZSE_SHOW_REPORT_URL,
        "request_parameters": params,
        "relative_path": _szse_output_relative_path(trade_date).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema_version": SZSE_SCHEMA_VERSION,
        "storage": "official_pre2017_output",
    }


def _manifest_szse_entry(payload: LegacySzsePayload) -> dict[str, object]:
    return {
        **payload.entry,
        "storage": payload.storage,
    }


def _validated_new_szse(
    output_dir: Path, manifest: object, trade_date: date
) -> LegacySzsePayload | None:
    if trade_date != SZSE_GAP_FETCH_DATE:
        return None
    if not isinstance(manifest, dict):
        return None
    entries = manifest.get("szse_raw_entries")
    if not isinstance(entries, list):
        return None
    matching = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("date") == trade_date.isoformat()
        and entry.get("storage") == "official_pre2017_output"
    ]
    if len(matching) != 1:
        return None
    entry = matching[0]
    expected = {
        "date": trade_date.isoformat(),
        "market": "SZSE",
        "source_url": SZSE_SHOW_REPORT_URL,
        "request_parameters": _szse_parameters(trade_date),
        "relative_path": _szse_output_relative_path(trade_date).as_posix(),
        "schema_version": SZSE_SCHEMA_VERSION,
        "storage": "official_pre2017_output",
    }
    if any(entry.get(key) != value for key, value in expected.items()):
        return None
    if (
        not isinstance(entry.get("sha256"), str)
        or _SHA256_RE.fullmatch(entry["sha256"]) is None
        or not isinstance(entry.get("bytes"), int)
        or isinstance(entry["bytes"], bool)
        or entry["bytes"] <= 0
        or not isinstance(entry.get("retrieved_at_utc"), str)
        or not entry["retrieved_at_utc"]
    ):
        return None
    try:
        root = output_dir.resolve()
        raw_path = (output_dir / str(entry["relative_path"])).resolve()
        if not raw_path.is_relative_to(root):
            return None
        payload = raw_path.read_bytes()
        if len(payload) != entry["bytes"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            return None
        return LegacySzsePayload(
            payload=payload,
            entry={key: entry[key] for key in entry if key != "storage"},
            market_cap_yi=parse_old_szse_workbook(payload, trade_date),
            storage="official_pre2017_output",
        )
    except (OSError, ValueError):
        return None


def _new_sse_entry(
    trade_date: date, params: dict[str, object], payload: bytes
) -> dict[str, object]:
    return {
        "date": trade_date.isoformat(),
        "source_url": SSE_QUERY_URL,
        "request_parameters": params,
        "relative_path": _sse_relative_path(trade_date).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "schema_version": SSE_SCHEMA_VERSION,
    }


def _validated_new_sse(
    output_dir: Path, manifest: object, trade_date: date
) -> tuple[bytes, dict[str, object], Decimal] | None:
    if not isinstance(manifest, dict):
        return None
    entries = manifest.get("sse_raw_entries")
    if not isinstance(entries, list):
        return None
    matching = [
        entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("date") == trade_date.isoformat()
    ]
    if len(matching) != 1:
        return None
    entry = matching[0]
    expected = _new_sse_entry(
        trade_date,
        {
            **SSE_LEGACY_PARAMETERS,
            "searchDate": trade_date.isoformat(),
        },
        b"x",
    )
    required = {*expected, "sha256", "bytes"}
    if not required.issubset(entry):
        return None
    for key in ("date", "source_url", "request_parameters", "relative_path", "schema_version"):
        if entry.get(key) != expected[key]:
            return None
    if (
        not isinstance(entry.get("sha256"), str)
        or _SHA256_RE.fullmatch(entry["sha256"]) is None
        or not isinstance(entry.get("bytes"), int)
        or isinstance(entry["bytes"], bool)
        or entry["bytes"] <= 0
    ):
        return None
    try:
        root = output_dir.resolve()
        raw_path = (output_dir / str(entry["relative_path"])).resolve()
        if not raw_path.is_relative_to(root):
            return None
        payload = raw_path.read_bytes()
        if (
            len(payload) != entry["bytes"]
            or hashlib.sha256(payload).hexdigest() != entry["sha256"]
        ):
            return None
        return payload, entry, parse_legacy_sse_payload(payload, trade_date)
    except (OSError, ValueError):
        return None


def _record(
    trade_date: date, sh_a_market_cap_yi: Decimal, szse: LegacySzsePayload, sse_entry: dict[str, object]
) -> dict[str, object]:
    return {
        "date": trade_date.isoformat(),
        "sh_a_market_cap_yi": sh_a_market_cap_yi,
        "sz_a_market_cap_yi": szse.market_cap_yi,
        "market_cap_yi": sh_a_market_cap_yi + szse.market_cap_yi,
        "source_segment": SOURCE_SEGMENT,
        "status": "pass",
        "sse_raw_sha256": sse_entry["sha256"],
        "szse_raw_sha256": szse.entry["sha256"],
    }


def _build_manifest(
    *,
    project_root: Path,
    legacy_raw_root: Path,
    legacy_manifest_path: Path,
    requested: list[date],
    records: list[dict[str, object]],
    sse_entries: list[dict[str, object]],
    szse_by_date: dict[date, LegacySzsePayload],
    szse_unavailable: list[dict[str, str]],
    missing_details: list[dict[str, str]],
    mapping_evidence: SseMappingEvidence | None,
    mode: str,
    csv_sha256: str | None,
    finalized: bool,
) -> dict[str, object]:
    completed = [str(record["date"]) for record in records]
    requested_text = [value.isoformat() for value in requested]
    completed_set = set(completed)
    missing = [item for item in requested_text if item not in completed_set]
    full_dfcf_dates = load_dfcf_pre2017_common_dates(
        project_root, EARLIEST_SUPPORTED_DATE, LATEST_PRE2017_DATE
    )
    full_dfcf_contract = (
        len(full_dfcf_dates) == 1316
        and full_dfcf_dates
        and full_dfcf_dates[0] == EARLIEST_SUPPORTED_DATE
        and full_dfcf_dates[-1] == LATEST_PRE2017_DATE
    )
    requested_is_full_contract = full_dfcf_contract and requested == full_dfcf_dates
    decimal_calculation_ok = True
    for record in records:
        try:
            sh = _positive_decimal(record["sh_a_market_cap_yi"], field_name="CSV sh A market cap")
            sz = _positive_decimal(record["sz_a_market_cap_yi"], field_name="CSV sz A market cap")
            total = _positive_decimal(record["market_cap_yi"], field_name="CSV market cap")
            if sh + sz != total:
                decimal_calculation_ok = False
                break
        except (KeyError, ValueError):
            decimal_calculation_ok = False
            break
    scope_mapping_ok = mapping_evidence is not None
    requested_raw_complete = (
        len(sse_entries) == len(requested)
        and len(szse_by_date) == len(requested)
        and not missing
        and not szse_unavailable
    )
    legacy_dates = [
        value.isoformat()
        for value, payload in sorted(szse_by_date.items())
        if payload.storage == "legacy_read_only"
    ]
    new_szse_dates = [
        value.isoformat()
        for value, payload in sorted(szse_by_date.items())
        if payload.storage == "official_pre2017_output"
    ]
    new_szse_dates_are_only_gap = all(
        value == SZSE_GAP_FETCH_DATE.isoformat() for value in new_szse_dates
    )
    raw_chain_ok = (
        mode == "normal"
        and finalized
        and scope_mapping_ok
        and requested_is_full_contract
        and requested_raw_complete
        and len(records) == len(requested)
        and new_szse_dates_are_only_gap
    )
    ratio_reporting_eligible = raw_chain_ok and decimal_calculation_ok
    financial_evidence_audit = {
        "applicable": False,
        "status": "N/A",
        "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
    }
    return {
        "schema_version": "2",
        "source_segment": SOURCE_SEGMENT,
        "mode": mode,
        "finalized": finalized,
        "final_output_ready": ratio_reporting_eligible,
        "scope_definition": (
            "2011-08-03 至 2016-12-30：仅纳入上交所 PRODUCT_TYPE=1 主板A，"
            "及深交所主板A股、中小板、创业板总市值；排除B股、回购、总计、基金、"
            "债券、北交所及其他非指定类别。分子 DFCF 两融余额可能含非 A 股融资标的，"
            "因此不得声称该比值已经完成严格证券类别匹配。"
        ),
        "cdr_star_board_note": (
            "本 pre-2017 段不适用科创板；CDR 未在该历史分类中单列，"
            "不得将本段外推为含 CDR 的范围。"
        ),
        "dfcf_input": {
            "relative_path": DFCF_RELATIVE_PATH.as_posix(),
            "sha256": sha256_file(_dfcf_path(project_root)),
        },
        "legacy_raw_root": str(legacy_raw_root.resolve()),
        "legacy_raw_manifest_sha256": (
            sha256_file(legacy_manifest_path)
            if legacy_manifest_path.exists()
            else None
        ),
        "sse_source": {
            "source_url": SSE_QUERY_URL,
            "request_parameters": SSE_LEGACY_PARAMETERS,
            "schema_version": SSE_SCHEMA_VERSION,
            "mapping_evidence_url": SSE_MAPPING_EVIDENCE_URL,
            "mapping_schema_version": SSE_MAPPING_SCHEMA_VERSION,
        },
        "szse_source": {
            "source_url": SZSE_SHOW_REPORT_URL,
            "request_parameters": SZSE_SHOW_REPORT_PARAMETERS,
            "schema_version": SZSE_SCHEMA_VERSION,
            "reused_read_only": True,
        },
        "requested_dates": requested_text,
        "completed_dates": completed,
        "missing_dates": missing,
        "missing_details": missing_details,
        "dfcf_date_contract": {
            "required_start": EARLIEST_SUPPORTED_DATE.isoformat(),
            "required_end": LATEST_PRE2017_DATE.isoformat(),
            "required_common_date_count": 1316,
            "available_common_date_count": len(full_dfcf_dates),
            "available_common_date_first": (
                full_dfcf_dates[0].isoformat() if full_dfcf_dates else None
            ),
            "available_common_date_last": (
                full_dfcf_dates[-1].isoformat() if full_dfcf_dates else None
            ),
            "requested_is_full_contract": requested_is_full_contract,
        },
        "sse_mapping_evidence": (
            mapping_evidence.entry if mapping_evidence is not None else None
        ),
        "reusable_szse_dates": legacy_dates,
        "reusable_szse_count": len(legacy_dates),
        "new_szse_gap_dates": new_szse_dates,
        "new_szse_gap_count": len(new_szse_dates),
        "szse_unavailable_dates": szse_unavailable,
        "szse_raw_entries": [
            _manifest_szse_entry(szse_by_date[value]) for value in sorted(szse_by_date)
        ],
        "sse_raw_entries": sorted(sse_entries, key=lambda item: str(item["date"])),
        "csv_sha256": csv_sha256,
        "raw_chain_audit": {
            "official_raw_chain_status": "pass" if raw_chain_ok else "blocked",
            "scope_mapping_status": "pass" if scope_mapping_ok else "blocked",
            "date_linkage_status": (
                "pass" if requested_is_full_contract and not missing else "blocked"
            ),
            "decimal_calculation_status": (
                "pass" if decimal_calculation_ok else "blocked"
            ),
            "ratio_reporting_eligible": ratio_reporting_eligible,
        },
        "financial_evidence_audit": financial_evidence_audit,
        "reporting_eligible": ratio_reporting_eligible,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _build_official_pre2017_audit(manifest: dict[str, object]) -> dict[str, object]:
    raw_chain = manifest["raw_chain_audit"]
    assert isinstance(raw_chain, dict)
    return {
        "schema_version": "1",
        "source_segment": SOURCE_SEGMENT,
        "official_raw_chain_status": raw_chain["official_raw_chain_status"],
        "scope_mapping_status": raw_chain["scope_mapping_status"],
        "date_linkage_status": raw_chain["date_linkage_status"],
        "decimal_calculation_status": raw_chain["decimal_calculation_status"],
        "ratio_reporting_eligible": raw_chain["ratio_reporting_eligible"],
        "financial_evidence_audit": manifest["financial_evidence_audit"],
        "csv_sha256": manifest["csv_sha256"],
        "dfcf_input": manifest["dfcf_input"],
        "requested_dates": manifest["requested_dates"],
        "completed_dates": manifest["completed_dates"],
        "missing_dates": manifest["missing_dates"],
        "sse_mapping_evidence": manifest["sse_mapping_evidence"],
        "sse_raw_entry_count": len(manifest["sse_raw_entries"]),
        "szse_raw_entry_count": len(manifest["szse_raw_entries"]),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _write_final_manifest_and_audit(
    output_dir: Path, manifest: dict[str, object]
) -> None:
    atomic_write_json(manifest, output_dir / "official_pre2017_market_cap_manifest.json")
    atomic_write_json(
        _build_official_pre2017_audit(manifest), output_dir / OFFICIAL_AUDIT_FILENAME
    )


def _write_journal(
    output_dir: Path,
    *,
    project_root: Path,
    legacy_raw_root: Path,
    legacy_manifest_path: Path,
    requested: list[date],
    records: list[dict[str, object]],
    sse_entries: list[dict[str, object]],
    szse_by_date: dict[date, LegacySzsePayload],
    szse_unavailable: list[dict[str, str]],
    missing_details: list[dict[str, str]],
    mapping_evidence: SseMappingEvidence | None,
) -> None:
    manifest = _build_manifest(
        project_root=project_root,
        legacy_raw_root=legacy_raw_root,
        legacy_manifest_path=legacy_manifest_path,
        requested=requested,
        records=records,
        sse_entries=sse_entries,
        szse_by_date=szse_by_date,
        szse_unavailable=szse_unavailable,
        missing_details=missing_details,
        mapping_evidence=mapping_evidence,
        mode="normal",
        csv_sha256=None,
        finalized=False,
    )
    atomic_write_json(
        manifest, output_dir / "official_pre2017_market_cap_manifest.json"
    )


def _rebuild_would_overwrite_eligible_output(
    output_dir: Path, manifest: object
) -> bool:
    audit_path = output_dir / OFFICIAL_AUDIT_FILENAME
    audit = _read_json(audit_path)
    for candidate in (manifest, audit):
        if not isinstance(candidate, dict):
            continue
        if candidate.get("reporting_eligible") is True:
            return True
        if candidate.get("ratio_reporting_eligible") is True:
            return True
        raw_chain = candidate.get("raw_chain_audit")
        if isinstance(raw_chain, dict) and raw_chain.get("ratio_reporting_eligible") is True:
            return True
    return False


def _guard_rebuild_output_is_unapproved(output_dir: Path, manifest: object) -> None:
    manifest_path = output_dir / "official_pre2017_market_cap_manifest.json"
    audit_path = output_dir / OFFICIAL_AUDIT_FILENAME
    for path, payload in ((manifest_path, manifest), (audit_path, _read_json(audit_path))):
        if path.exists() and not isinstance(payload, dict):
            raise ValueError(
                "rebuild_from_existing cannot overwrite an unreadable existing output evidence file"
            )
    if _rebuild_would_overwrite_eligible_output(output_dir, manifest):
        raise ValueError(
            "rebuild_from_existing cannot overwrite an existing reporting-eligible output"
        )


def build_official_pre2017_market_cap(
    project_root: Path,
    dates: list[date],
    options: RequestOptions,
    *,
    rebuild_from_existing: bool,
    legacy_raw_root: Path | None = None,
) -> dict[str, object]:
    requested = _strict_requested_dates(dates)
    project_root = project_root.resolve()
    _require_dfcf_common_dates(project_root, requested)
    output_dir = project_root / OUTPUT_DIRECTORY
    legacy_root = resolve_legacy_raw_root(project_root, legacy_raw_root)
    legacy_manifest_path = legacy_root / "raw_response_manifest.json"
    decoded_legacy_manifest = _read_json(legacy_manifest_path)
    legacy_manifest = (
        decoded_legacy_manifest
        if isinstance(decoded_legacy_manifest, list)
        and all(isinstance(item, dict) for item in decoded_legacy_manifest)
        else []
    )
    output_manifest_path = output_dir / "official_pre2017_market_cap_manifest.json"
    existing_output_manifest = _read_json(output_manifest_path)
    if rebuild_from_existing:
        _guard_rebuild_output_is_unapproved(output_dir, existing_output_manifest)
    szse_by_date: dict[date, LegacySzsePayload] = {}
    szse_unavailable: list[dict[str, str]] = []
    for trade_date in requested:
        szse, reason = _load_old_szse(legacy_root, legacy_manifest, trade_date)
        if szse is not None:
            szse_by_date[trade_date] = szse
            continue
        resumed_szse = _validated_new_szse(
            output_dir, existing_output_manifest, trade_date
        )
        if resumed_szse is not None:
            szse_by_date[trade_date] = resumed_szse
            continue
        szse_unavailable.append({"date": trade_date.isoformat(), "reason": reason})

    sse_entries: list[dict[str, object]] = []
    records: list[dict[str, object]] = []
    missing_details: list[dict[str, str]] = []
    network_requests = 0
    mapping_evidence: SseMappingEvidence | None = None

    if rebuild_from_existing:
        for trade_date in requested:
            if trade_date in szse_by_date:
                missing_details.append(
                    {
                        "date": trade_date.isoformat(),
                        "reason": "rebuild_from_existing_does_not_fetch_sse",
                    }
                )
        frame = pd.DataFrame(records).reindex(columns=OUTPUT_COLUMNS)
        csv_path = output_dir / "official_pre2017_market_cap.csv"
        atomic_write_csv(frame, csv_path)
        manifest = _build_manifest(
            project_root=project_root,
            legacy_raw_root=legacy_root,
            legacy_manifest_path=legacy_manifest_path,
            requested=requested,
            records=records,
            sse_entries=sse_entries,
            szse_by_date=szse_by_date,
            szse_unavailable=szse_unavailable,
            missing_details=missing_details,
            mapping_evidence=None,
            mode="rebuild_from_existing",
            csv_sha256=sha256_file(csv_path),
            finalized=False,
        )
        _write_final_manifest_and_audit(output_dir, manifest)
        return {
            "requested_dates": len(requested),
            "network_requests": 0,
            "reusable_szse_dates": len(
                [item for item in szse_by_date.values() if item.storage == "legacy_read_only"]
            ),
            "missing_dates": len(manifest["missing_dates"]),
            "reporting_eligible": False,
            "output_dir": str(output_dir),
        }

    resumed_mapping = _validated_sse_mapping(output_dir, existing_output_manifest)
    try:
        if resumed_mapping is None:
            mapping_payload, mapping_parsed, attempts = fetch_sse_mapping_evidence(options)
            network_requests += attempts
            mapping_entry = _sse_mapping_entry(mapping_payload, mapping_parsed)
            atomic_write_bytes(
                mapping_payload,
                output_dir / Path(str(mapping_entry["relative_path"])),
            )
            mapping_evidence = SseMappingEvidence(
                payload=mapping_payload,
                entry=mapping_entry,
                parsed=mapping_parsed,
            )
        else:
            mapping_evidence = resumed_mapping
    except (OSError, RuntimeError, ValueError) as exc:
        missing_details.append({"date": "*", "reason": f"SSE mapping unavailable: {exc}"})

    for trade_date in requested:
        if trade_date in szse_by_date or trade_date != SZSE_GAP_FETCH_DATE:
            continue
        try:
            szse_payload, params, attempts = fetch_szse_show_report(trade_date, options)
            network_requests += attempts
            entry = _new_szse_entry(trade_date, params, szse_payload)
            atomic_write_bytes(
                szse_payload, output_dir / Path(str(entry["relative_path"]))
            )
            szse_by_date[trade_date] = LegacySzsePayload(
                payload=szse_payload,
                entry={key: entry[key] for key in entry if key != "storage"},
                market_cap_yi=parse_old_szse_workbook(szse_payload, trade_date),
                storage="official_pre2017_output",
            )
            _write_journal(
                output_dir,
                project_root=project_root,
                legacy_raw_root=legacy_root,
                legacy_manifest_path=legacy_manifest_path,
                requested=requested,
                records=records,
                sse_entries=sse_entries,
                szse_by_date=szse_by_date,
                szse_unavailable=[],
                missing_details=missing_details,
                mapping_evidence=mapping_evidence,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            missing_details.append(
                {"date": trade_date.isoformat(), "reason": f"SZSE gap unavailable: {exc}"}
            )

    for item in szse_unavailable:
        if date.fromisoformat(item["date"]) not in szse_by_date:
            missing_details.append(dict(item))

    for trade_date in requested:
        szse = szse_by_date.get(trade_date)
        if szse is None:
            continue
        if mapping_evidence is None:
            missing_details.append(
                {"date": trade_date.isoformat(), "reason": "SSE mapping evidence is unavailable"}
            )
            continue
        resumed = _validated_new_sse(output_dir, existing_output_manifest, trade_date)
        try:
            if resumed is None:
                sse_payload, params, attempts = fetch_legacy_sse(trade_date, options)
                network_requests += attempts
                sh_a_market_cap_yi = parse_legacy_sse_payload(sse_payload, trade_date)
                sse_entry = _new_sse_entry(trade_date, params, sse_payload)
                atomic_write_bytes(
                    sse_payload, output_dir / Path(str(sse_entry["relative_path"]))
                )
                sse_entries.append(sse_entry)
                _write_journal(
                    output_dir,
                    project_root=project_root,
                    legacy_raw_root=legacy_root,
                    legacy_manifest_path=legacy_manifest_path,
                    requested=requested,
                    records=records,
                    sse_entries=sse_entries,
                    szse_by_date=szse_by_date,
                    szse_unavailable=[],
                    missing_details=missing_details,
                    mapping_evidence=mapping_evidence,
                )
            else:
                _, sse_entry, sh_a_market_cap_yi = resumed
                sse_entries.append(sse_entry)
            records.append(_record(trade_date, sh_a_market_cap_yi, szse, sse_entry))
        except (OSError, RuntimeError, ValueError, KeyError) as exc:
            missing_details.append(
                {"date": trade_date.isoformat(), "reason": f"SSE unavailable: {exc}"}
            )
        if options.sleep_seconds and resumed is None:
            time.sleep(options.sleep_seconds)

    records.sort(key=lambda item: str(item["date"]))
    sse_entries = sorted(
        {str(entry["date"]): entry for entry in sse_entries}.values(),
        key=lambda item: str(item["date"]),
    )
    frame = pd.DataFrame(records).reindex(columns=OUTPUT_COLUMNS)
    csv_path = output_dir / "official_pre2017_market_cap.csv"
    atomic_write_csv(frame, csv_path)
    manifest = _build_manifest(
        project_root=project_root,
        legacy_raw_root=legacy_root,
        legacy_manifest_path=legacy_manifest_path,
        requested=requested,
        records=records,
        sse_entries=sse_entries,
        szse_by_date=szse_by_date,
        szse_unavailable=[
            item
            for item in szse_unavailable
            if date.fromisoformat(item["date"]) not in szse_by_date
        ],
        missing_details=missing_details,
        mapping_evidence=mapping_evidence,
        mode="normal",
        csv_sha256=sha256_file(csv_path),
        finalized=True,
    )
    _write_final_manifest_and_audit(output_dir, manifest)
    return {
        "requested_dates": len(requested),
        "network_requests": network_requests,
        "reusable_szse_dates": len(
            [item for item in szse_by_date.values() if item.storage == "legacy_read_only"]
        ),
        "missing_dates": len(manifest["missing_dates"]),
        "reporting_eligible": manifest["reporting_eligible"],
        "output_dir": str(output_dir),
    }


def resolve_project_root(value: str | None) -> Path:
    root = Path(value).expanduser().resolve() if value else Path(__file__).resolve().parents[1]
    if not (root / "AGENTS.md").exists():
        raise FileNotFoundError(f"cannot confirm project root: {root}")
    return root


def _parse_cli_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be YYYY-MM-DD") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="构建 2017-01-03 前的官方交易所市值分段"
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--legacy-raw-root", default=None)
    parser.add_argument("--start-date", type=_parse_cli_date, default=EARLIEST_SUPPORTED_DATE)
    parser.add_argument("--end-date", type=_parse_cli_date, default=date(2016, 12, 30))
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rebuild-from-existing", action="store_true")
    args = parser.parse_args()
    if args.sleep_seconds < 0 or args.timeout_seconds <= 0 or args.max_retries < 0:
        parser.error("sleep/timeout/retries arguments are out of range")
    if (
        args.start_date < EARLIEST_SUPPORTED_DATE
        or args.end_date > LATEST_PRE2017_DATE
    ):
        parser.error("--start-date/--end-date must be in 2011-08-03..2016-12-30")
    project_root = resolve_project_root(args.project_root)
    requested = load_dfcf_pre2017_common_dates(
        project_root, args.start_date, args.end_date
    )
    legacy_root = resolve_legacy_raw_root(project_root, args.legacy_raw_root)
    output_dir = project_root / OUTPUT_DIRECTORY
    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "requested_dates": len(requested),
                    "start_date": requested[0].isoformat() if requested else None,
                    "end_date": requested[-1].isoformat() if requested else None,
                    "legacy_raw_root": str(legacy_root),
                    "output_dir": str(output_dir),
                },
                ensure_ascii=False,
            )
        )
        return 0
    result = build_official_pre2017_market_cap(
        project_root,
        requested,
        RequestOptions(
            session=None if args.rebuild_from_existing else requests.Session(),
            sleep_seconds=args.sleep_seconds,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
        ),
        rebuild_from_existing=args.rebuild_from_existing,
        legacy_raw_root=legacy_root,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
