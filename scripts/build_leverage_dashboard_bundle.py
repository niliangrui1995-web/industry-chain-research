from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import os
import re
import struct
import sys
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


_SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(_SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIRECTORY))
from official_pre2017_contract import (
    parse_sse_cal_date,
    parse_sse_stockday_mapping_evidence,
    parse_sse_tx_num,
)
from update_eastmoney_mx_pre2017_market_cap_vendor import (
    AUDIT_FILENAME as MX_PRE2017_AUDIT_FILENAME,
    CSV_COLUMNS as MX_PRE2017_CSV_COLUMNS_ORDERED,
    MANIFEST_FILENAME as MX_PRE2017_MANIFEST_FILENAME,
    OUTPUT_DIRECTORY as MX_PRE2017_OUTPUT_DIRECTORY,
    RATIO_REVIEW_STATUS as MX_PRE2017_REVIEW_STATUS,
    SOURCE_NAME as MX_PRE2017_SOURCE_NAME,
    SOURCE_URL as MX_PRE2017_URL,
    TABLE_FILENAME as MX_PRE2017_TABLE_FILENAME,
    _parse_mx_response,
)


DAY_STRUCT = struct.Struct("<IIIIIfII")
DFCF_STATUS = "dfcf_vendor_only_unverified_by_exchange"
RATIO_QUANTUM = Decimal("0.00000001")
PRE2017_END = date(2016, 12, 30)
POST2017_START = date(2017, 1, 3)
PRE2017_REQUIRED_START = "2011-08-03"
PRE2017_REQUIRED_END = "2016-12-30"
PRE2017_REQUIRED_DATE_COUNT = 1316
OUTPUT_DIRECTORY = Path("artifacts/leverage_capitulation/dashboard_bundle")
PUBLISH_DIRECTORY = Path(r"D:\vcp_hunter\基金持仓\public\data")
VENDOR_OUTPUT_DIRECTORY = Path(
    "artifacts/leverage_capitulation/eastmoney_post2017_market_cap_vendor"
)
OFFICIAL_PRE2017_OUTPUT_DIRECTORY = Path(
    "artifacts/leverage_capitulation/official_pre2017_market_cap"
)
OFFICIAL_PRE2017_TABLE_FILENAME = "official_pre2017_market_cap.csv"
OFFICIAL_PRE2017_MANIFEST_FILENAME = "official_pre2017_market_cap_manifest.json"
OFFICIAL_PRE2017_AUDIT_FILENAME = "official_pre2017_market_cap_audit.json"
OFFICIAL_PRE2017_SOURCE = "official_exchange_pre2017_raw_chain_audited"
OFFICIAL_PRE2017_UNAVAILABLE_SOURCE = "pre2017_official_unavailable"
OFFICIAL_PRE2017_REVIEW_STATUS = "official_exchange_pre2017_raw_chain_audited"
MIXED_AUDITED_REVIEW_STATUS = (
    "mixed_official_pre2017_raw_chain_audited_eastmoney_vendor_unverified"
)
MIXED_OFFICIAL_UNAVAILABLE_REVIEW_STATUS = (
    "mixed_official_pre2017_unavailable_eastmoney_vendor_unverified"
)
MX_PRE2017_SOURCE = "mx_pre2017_vendor_unverified"
MX_PRE2017_UNAVAILABLE_SOURCE = "pre2017_mx_vendor_unavailable"
MIXED_MX_VENDOR_REVIEW_STATUS = (
    "mixed_mx_pre2017_vendor_unverified_eastmoney_vendor_unverified"
)
MIXED_MX_UNAVAILABLE_REVIEW_STATUS = (
    "mixed_mx_pre2017_unavailable_eastmoney_vendor_unverified"
)
MX_PRE2017_SCOPE_WARNING = (
    "2011-08-03 至 2016-12-30 分母为东方财富妙想厂商口径；"
    "2017-01-03 起分母为东方财富 Choice 厂商口径。两段均未经交易所复核、未经完整审计，"
    "且口径边界可能造成水平不可直接拼接比较；分子为 DFCF 厂商两融余额，可能含非 A 股融资标的，"
    "该聚合比例不是正式财务比例。"
)
OFFICIAL_PRE2017_SSE_URL = "https://query.sse.com.cn/commonQuery.do"
OFFICIAL_PRE2017_SSE_MAPPING_URL = (
    "https://www.sse.com.cn/xhtml/home/public/querySearch/search_addhsl.js"
)
OFFICIAL_PRE2017_SZSE_URL = "https://www.szse.cn/api/report/ShowReport"
OFFICIAL_PRE2017_SSE_SCHEMA_VERSION = "legacy_product_type"
OFFICIAL_PRE2017_MAPPING_SCHEMA_VERSION = "search_addhsl_product_type_mapping_v1"
OFFICIAL_PRE2017_SZSE_SCHEMA_VERSION = "show_report_xlsx"
OFFICIAL_PRE2017_SZSE_GAP_DATE = "2015-06-11"
OFFICIAL_PRE2017_SSE_TOTAL_TOLERANCE = Decimal("0.00000001")
OFFICIAL_PRE2017_TX_NUM_TOLERANCE = Decimal("0")
OFFICIAL_PRE2017_SZSE_TOTAL_TOLERANCE_YUAN = Decimal("0.10")
VENDOR_TABLE_FILENAME = "eastmoney_post2017_market_cap_vendor.csv"
VENDOR_MANIFEST_FILENAME = "eastmoney_post2017_market_cap_vendor_manifest.json"
EASTMONEY_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
EASTMONEY_REPORT_NAME = "RPT_VALUEMARKET"
EASTMONEY_MARKET_CODE = "000300"
EASTMONEY_SOURCE = "东方财富Choice厂商数据"
EASTMONEY_REVIEW_STATUS = "eastmoney_vendor_unverified"
VENDOR_SCOPE_WARNING = (
    "东方财富 Choice 厂商口径／未经交易所复核、未经完整审计；"
    "仅覆盖 2017-01-03 及以后与 DFCF 共同日期精确重合的记录；"
    "A/B、CDR、基金等资产范围未核验，分子可能含非 A 股融资标的。"
)
PRE2017_REASON = (
    "2011-08-03 至 2016-12-30 官方市值原始链尚未完整通过 manifest、哈希、"
    "DFCF 日期绑定和独立审计；此前比例为 N/A。"
)
INDEX_PATHS = {
    "000001": Path(r"D:\HT\vipdoc\sh\lday\sh000001.day"),
    "399106": Path(r"D:\HT\vipdoc\sz\lday\sz399106.day"),
    "399006": Path(r"D:\HT\vipdoc\sz\lday\sz399006.day"),
}
INDEX_SOURCE = "本地 TDX 厂商日线（用于三指数收盘价；未做交易所或指数编制方原始链复核）"
INDEX_SNAPSHOT_HASH_RECORDED = "recorded"
MANIFEST_DESCRIPTION = (
    "DFCF 两融余额与三指数静态数据包；"
    "三指数收盘价来自本地 TDX 厂商日线，未做交易所或指数编制方原始链复核；"
    "两融余额下降仅为去杠杆压力代理，不证明强平、底部或反弹。"
)
VENDOR_CSV_COLUMNS = {
    "date",
    "market_cap_yi",
    "source",
    "source_market_code",
    "source_trade_date",
    "raw_total_market_cap",
    "unit_conversion",
    "status",
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SOURCE_DATE_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})(?:[ T]00:00:00(?:\.0+)?)?\Z"
)


@dataclass(frozen=True)
class MarginInput:
    frame: pd.DataFrame
    audit: dict[str, object]
    paths: dict[str, Path]


@dataclass(frozen=True)
class VendorMarketCapInput:
    frame: pd.DataFrame
    manifest: dict[str, object]
    paths: dict[str, Path]


@dataclass(frozen=True)
class OfficialPre2017Input:
    frame: pd.DataFrame
    manifest: dict[str, object]
    audit: dict[str, object]
    paths: dict[str, Path]


@dataclass(frozen=True)
class MxPre2017VendorInput:
    frame: pd.DataFrame
    manifest: dict[str, object]
    audit: dict[str, object]
    paths: dict[str, Path]


def beijing_now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_date(value: object, name: str = "日期") -> str:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError(f"{name} 必须为 YYYY-MM-DD")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError as exc:
        raise ValueError(f"{name} 必须为 YYYY-MM-DD") from exc


def _source_trade_date(value: object, name: str = "source_trade_date") -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} 必须为日期或精确的 00:00:00 后缀日期")
    match = SOURCE_DATE_RE.fullmatch(value.strip())
    if match is None:
        raise ValueError(f"{name} 必须为日期或精确的 00:00:00 后缀日期")
    return _strict_date(match.group(1), name)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"输入文件不存在: {path}")
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def _validate_dates(frame: pd.DataFrame, name: str) -> list[str]:
    if "date" not in frame.columns:
        raise ValueError(f"{name} 缺少 date 列")
    dates = [_strict_date(value, f"{name} date") for value in frame["date"].tolist()]
    if not dates or len(dates) != len(set(dates)) or dates != sorted(dates):
        raise ValueError(f"{name} 日期必须唯一且升序")
    return dates


def _positive_decimal(value: object, name: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{name} 必须为正数")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} 必须为正数") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError(f"{name} 必须为正数")
    return result


def _positive_szse_market_cap_decimal(value: object) -> Decimal:
    name = "SZSE 总市值"
    if isinstance(value, str):
        normalized = value.strip()
        if "," in normalized:
            if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", normalized) is None:
                raise ValueError(f"{name} 必须为正数")
            value = normalized.replace(",", "")
    return _positive_decimal(value, name)


def _integer(value: object, name: str, minimum: int) -> int:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{name} 必须为整数")
    try:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} 必须为整数") from exc
    if not decimal_value.is_finite() or decimal_value != decimal_value.to_integral_value():
        raise ValueError(f"{name} 必须为整数")
    result = int(decimal_value)
    if result < minimum:
        raise ValueError(f"{name} 超出允许范围")
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"JSON 包含非有限值: {value}")


def _load_json_bytes(path: Path, name: str) -> dict[str, object]:
    try:
        value = json.loads(
            path.read_bytes().decode("utf-8"),
            parse_float=Decimal,
            parse_int=Decimal,
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{name} 不是有效 UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{name} 必须是 JSON 对象")
    return value


def _require_sha256(value: object, name: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{name} 必须为 64 位小写十六进制 SHA-256")
    return value


def verify_dfcf_inputs(project_root: Path) -> MarginInput:
    daily = project_root / "artifacts/leverage_capitulation/dfcf_daily"
    paths = {
        "sse": daily / "dfcf_sse_margin.csv",
        "szse": daily / "dfcf_szse_margin.csv",
        "balances": daily / "dfcf_margin_balances.csv",
        "audit": daily / "dfcf_margin_audit.json",
    }
    audit = json.loads(paths["audit"].read_text(encoding="utf-8"))
    if audit.get("dfcf_only") is not True:
        raise ValueError("DFCF audit 的 dfcf_only 不为 true")
    if audit.get("exchange_requests") != 0:
        raise ValueError("DFCF audit 的 exchange_requests 不为 0")
    if audit.get("sample_status") != DFCF_STATUS:
        raise ValueError("DFCF audit 的 sample_status 异常")
    expected = {
        "dfcf_sse_margin_sha256": paths["sse"],
        "dfcf_szse_margin_sha256": paths["szse"],
        "dfcf_margin_balances_sha256": paths["balances"],
    }
    for field, path in expected.items():
        if audit.get(field) != sha256_file(path):
            raise ValueError(f"DFCF audit 哈希不匹配: {field}")
    frame = _read_csv(paths["balances"])
    required = {"date", "sh_margin_y", "sz_margin_y", "total_margin_y", "sample_status"}
    if required - set(frame.columns):
        raise ValueError("DFCF 合并表缺少必要列")
    _validate_dates(frame, "DFCF 合并表")
    if not frame["sample_status"].eq(DFCF_STATUS).all():
        raise ValueError("DFCF 合并表 sample_status 异常")
    for row in frame.itertuples(index=False):
        sh = _positive_decimal(row.sh_margin_y, "sh_margin_y")
        sz = _positive_decimal(row.sz_margin_y, "sz_margin_y")
        total = _positive_decimal(row.total_margin_y, "total_margin_y")
        if sh + sz != total:
            raise ValueError("DFCF 合并表不满足 sh_margin_y + sz_margin_y = total_margin_y")
    return MarginInput(frame=frame, audit=audit, paths=paths)


def _vendor_paths(project_root: Path) -> dict[str, Path]:
    output_dir = project_root / VENDOR_OUTPUT_DIRECTORY
    return {
        "directory": output_dir,
        "table": output_dir / VENDOR_TABLE_FILENAME,
        "manifest": output_dir / VENDOR_MANIFEST_FILENAME,
        "raw": output_dir / "raw",
    }


def _validate_vendor_manifest(manifest: dict[str, object]) -> list[dict[str, object]]:
    if manifest.get("source") != EASTMONEY_SOURCE:
        raise ValueError("东方财富 manifest source 不匹配")
    if manifest.get("source_url") != EASTMONEY_URL:
        raise ValueError("东方财富 manifest source_url 不匹配")
    if manifest.get("report_name") != EASTMONEY_REPORT_NAME:
        raise ValueError("东方财富 manifest report_name 不匹配")
    if manifest.get("source_market_code") != EASTMONEY_MARKET_CODE:
        raise ValueError("东方财富 manifest source_market_code 不匹配")
    _require_sha256(manifest.get("csv_sha256"), "东方财富 manifest csv_sha256")
    if manifest.get("reporting_eligible") is not False:
        raise ValueError("东方财富 manifest reporting_eligible 必须为 false")
    if manifest.get("ratio_review_status") != EASTMONEY_REVIEW_STATUS:
        raise ValueError("东方财富 manifest ratio_review_status 不匹配")
    scope_warning = manifest.get("scope_warning")
    if not isinstance(scope_warning, str) or not scope_warning.strip():
        raise ValueError("东方财富 manifest 缺少中文范围警示")
    if not all(term in scope_warning for term in ("未经交易所复核", "未经完整审计", "非 A 股")):
        raise ValueError("东方财富 manifest 范围警示不完整")
    manifest_version = manifest.get("manifest_version")
    if manifest_version is None:
        pages = manifest.get("pages")
        if not isinstance(pages, list) or not pages:
            raise ValueError("东方财富 manifest pages 缺失")
        requested_start = _strict_date(
            manifest.get("requested_start"), "东方财富 manifest requested_start"
        )
        requested_end = _strict_date(
            manifest.get("requested_end"), "东方财富 manifest requested_end"
        )
        if requested_start > requested_end:
            raise ValueError("东方财富 manifest requested 日期范围倒序")
        return [
            {
                "batch_id": "legacy-full-snapshot",
                "sequence": 1,
                "raw_directory": "raw",
                "requested_start": requested_start,
                "requested_end": requested_end,
                "pages": pages,
            }
        ]
    if manifest_version != 2:
        raise ValueError("东方财富 manifest_version 不受支持")
    batches = manifest.get("batches")
    if not isinstance(batches, list) or not batches:
        raise ValueError("东方财富增量 manifest batches 缺失")
    normalized: list[dict[str, object]] = []
    for sequence, batch in enumerate(batches, start=1):
        if not isinstance(batch, dict):
            raise ValueError("东方财富增量 manifest batch 不是对象")
        batch_id = batch.get("batch_id")
        if not isinstance(batch_id, str) or re.fullmatch(r"[a-z0-9][a-z0-9-]{0,127}", batch_id) is None:
            raise ValueError("东方财富增量 manifest batch_id 不符合固定契约")
        if _integer(batch.get("sequence"), "东方财富增量 batch sequence", 1) != sequence:
            raise ValueError("东方财富增量 manifest batch sequence 必须连续")
        raw_directory = batch.get("raw_directory")
        if not isinstance(raw_directory, str):
            raise ValueError("东方财富增量 manifest raw_directory 缺失")
        expected_directory = (
            "raw"
            if batch_id == "legacy-full-snapshot" and sequence == 1
            else f"raw/batches/{batch_id}"
        )
        if raw_directory != expected_directory:
            raise ValueError("东方财富增量 manifest raw_directory 不符合固定契约")
        requested_start = _strict_date(
            batch.get("requested_start"), "东方财富增量 batch requested_start"
        )
        requested_end = _strict_date(
            batch.get("requested_end"), "东方财富增量 batch requested_end"
        )
        if requested_start > requested_end:
            raise ValueError("东方财富增量 batch 请求区间倒序")
        pages = batch.get("pages")
        if not isinstance(pages, list) or not pages:
            raise ValueError("东方财富增量 batch pages 缺失")
        normalized.append(
            {
                "batch_id": batch_id,
                "raw_directory": raw_directory,
                "requested_start": requested_start,
                "requested_end": requested_end,
                "pages": pages,
            }
        )
    active_missing_dates = manifest.get("active_missing_dfcf_common_dates")
    if not isinstance(active_missing_dates, list):
        raise ValueError("东方财富增量 manifest active_missing_dfcf_common_dates 缺失")
    parsed_missing_dates = [
        _strict_date(value, "东方财富增量 active_missing_dfcf_common_dates")
        for value in active_missing_dates
    ]
    if len(parsed_missing_dates) != len(set(parsed_missing_dates)) or parsed_missing_dates != sorted(parsed_missing_dates):
        raise ValueError("东方财富增量 active_missing_dfcf_common_dates 必须唯一且升序")
    return normalized


def _validate_vendor_page_request(
    page: dict[str, object], expected_page_number: int, requested_start: str, requested_end: str
) -> None:
    request = page.get("request")
    if not isinstance(request, dict):
        raise ValueError("东方财富 manifest page request 缺失")
    parameters = request.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("东方财富 manifest page request.parameters 缺失")
    expected_filter = (
        f'(TRADE_MARKET_CODE="{EASTMONEY_MARKET_CODE}")'
        f"(TRADE_DATE>='{requested_start}')"
        f"(TRADE_DATE<='{requested_end}')"
    )
    expected_values = {
        "reportName": EASTMONEY_REPORT_NAME,
        "columns": "ALL",
        "filter": expected_filter,
        "source": "WEB",
        "client": "WEB",
        "sortColumns": "TRADE_DATE",
        "sortTypes": "1",
    }
    for field, expected in expected_values.items():
        if parameters.get(field) != expected:
            raise ValueError(f"东方财富 manifest page request {field} 不匹配")
    if _integer(parameters.get("pageNumber"), "东方财富 request pageNumber", 1) != expected_page_number:
        raise ValueError("东方财富 manifest page request pageNumber 不匹配")
    _integer(parameters.get("pageSize"), "东方财富 request pageSize", 1)
    _integer(request.get("attempts"), "东方财富 request attempts", 1)


def _validated_vendor_raw_records(
    paths: dict[str, Path], batches: list[dict[str, object]]
) -> dict[str, tuple[str, Decimal]]:
    raw_root = paths["raw"].resolve()
    active_by_date: dict[str, tuple[str, Decimal]] = {}
    for batch in batches:
        requested_start = str(batch["requested_start"])
        requested_end = str(batch["requested_end"])
        raw_directory = Path(str(batch["raw_directory"]))
        raw_directory_path = (paths["directory"] / raw_directory).resolve()
        try:
            raw_directory_path.relative_to(raw_root)
        except ValueError as exc:
            raise ValueError("东方财富增量 raw 目录越界") from exc
        records: list[tuple[str, str, Decimal]] = []
        pages = batch["pages"]
        if not isinstance(pages, list):
            raise ValueError("东方财富增量 batch pages 不是列表")
        reported_count: int | None = None
        reported_pages: int | None = None
        for expected_page_number, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                raise ValueError("东方财富 manifest page 不是对象")
            if _integer(page.get("page_number"), "东方财富 page_number", 1) != expected_page_number:
                raise ValueError("东方财富 manifest pages 必须从 1 连续编号")
            _validate_vendor_page_request(page, expected_page_number, requested_start, requested_end)
            expected_relative = raw_directory / f"page-{expected_page_number:04d}.json"
            if page.get("relative_path") != expected_relative.as_posix():
                raise ValueError("东方财富 raw 相对路径不符合固定契约")
            raw_path = (paths["directory"] / expected_relative).resolve()
            try:
                raw_path.relative_to(raw_root)
            except ValueError as exc:
                raise ValueError("东方财富 raw 路径越界") from exc
            if not raw_path.is_file():
                raise ValueError("东方财富 raw 文件不存在")
            if _integer(page.get("bytes"), "东方财富 raw bytes", 1) != raw_path.stat().st_size:
                raise ValueError("东方财富 raw bytes 不匹配")
            if _require_sha256(page.get("sha256"), "东方财富 raw sha256") != sha256_file(raw_path):
                raise ValueError("东方财富 raw SHA-256 不匹配")
            payload = _load_json_bytes(raw_path, "东方财富 raw 响应")
            if payload.get("success") is not True:
                raise ValueError("东方财富 raw 响应 success 不为 true")
            result = payload.get("result")
            if not isinstance(result, dict):
                raise ValueError("东方财富 raw 响应缺少 result 对象")
            rows = result.get("data")
            if not isinstance(rows, list):
                raise ValueError("东方财富 raw 响应缺少 result.data 列表")
            if _integer(page.get("returned_rows"), "东方财富 manifest returned_rows", 0) != len(rows):
                raise ValueError("东方财富 raw returned_rows 不匹配")
            page_count = _integer(result.get("count"), "东方财富 raw result.count", 0)
            page_total = _integer(result.get("pages"), "东方财富 raw result.pages", 1)
            for field in ("pageNum", "pageNumber", "pageNo"):
                if field in result and _integer(result[field], f"东方财富 raw result.{field}", 1) != expected_page_number:
                    raise ValueError("东方财富 raw 返回页码与 manifest 页号不一致")
            if _integer(page.get("reported_count"), "东方财富 manifest reported_count", 0) != page_count:
                raise ValueError("东方财富 raw reported_count 不匹配")
            if _integer(page.get("reported_pages"), "东方财富 manifest reported_pages", 1) != page_total:
                raise ValueError("东方财富 raw reported_pages 不匹配")
            if reported_count is None:
                reported_count = page_count
                reported_pages = page_total
            elif reported_count != page_count or reported_pages != page_total:
                raise ValueError("东方财富 raw 分页元数据不一致")
            for raw_row in rows:
                if not isinstance(raw_row, dict):
                    raise ValueError("东方财富 raw 行不是对象")
                if raw_row.get("TRADE_MARKET_CODE") != EASTMONEY_MARKET_CODE:
                    raise ValueError("东方财富 raw TRADE_MARKET_CODE 不匹配")
                source_trade_date = raw_row.get("TRADE_DATE")
                trade_date = _source_trade_date(source_trade_date, "东方财富 raw TRADE_DATE")
                if not (requested_start <= trade_date <= requested_end):
                    raise ValueError("东方财富 raw TRADE_DATE 超出请求日期范围")
                if date.fromisoformat(trade_date) < POST2017_START:
                    raise ValueError("东方财富 raw TRADE_DATE 越过 2017-01-03 分段边界")
                raw_total = _positive_decimal(raw_row.get("TOTAL_MARKET_CAP"), "东方财富 raw TOTAL_MARKET_CAP")
                records.append((trade_date, str(source_trade_date).strip(), raw_total))
        if reported_pages != len(pages) or reported_count != len(records):
            raise ValueError("东方财富 raw 分页数量或总行数不匹配")
        dates = [record[0] for record in records]
        if not dates or len(dates) != len(set(dates)) or dates != sorted(dates):
            raise ValueError("东方财富 raw 日期必须唯一且升序")
        for trade_date in list(active_by_date):
            if requested_start <= trade_date <= requested_end:
                del active_by_date[trade_date]
        active_by_date.update(
            {
                trade_date: (source_trade_date, raw_total)
                for trade_date, source_trade_date, raw_total in records
            }
        )
    return active_by_date


def _validate_vendor_csv(
    table_path: Path, manifest: dict[str, object], raw_by_date: dict[str, tuple[str, Decimal]]
) -> pd.DataFrame:
    if _require_sha256(manifest.get("csv_sha256"), "东方财富 manifest csv_sha256") != sha256_file(table_path):
        raise ValueError("东方财富 CSV SHA-256 不匹配")
    frame = _read_csv(table_path)
    if VENDOR_CSV_COLUMNS != set(frame.columns):
        raise ValueError("东方财富 CSV 列集合不符合固定契约")
    dates = _validate_dates(frame, "东方财富 CSV")
    for row in frame.itertuples(index=False):
        if row.source != EASTMONEY_SOURCE:
            raise ValueError("东方财富 CSV source 不匹配")
        if row.source_market_code != EASTMONEY_MARKET_CODE:
            raise ValueError("东方财富 CSV source_market_code 不匹配")
        if row.status != "pass":
            raise ValueError("东方财富 CSV status 不为 pass")
        if row.unit_conversion != "raw_divided_by_10000":
            raise ValueError("东方财富 CSV unit_conversion 不匹配")
        source_date = _source_trade_date(row.source_trade_date, "东方财富 CSV source_trade_date")
        if source_date != row.date:
            raise ValueError("东方财富 CSV date 与 source_trade_date 不一致")
        if date.fromisoformat(row.date) < POST2017_START:
            raise ValueError("东方财富 CSV date 越过 2017-01-03 分段边界")
        market_cap = _positive_decimal(row.market_cap_yi, "东方财富 CSV market_cap_yi")
        raw_total = _positive_decimal(row.raw_total_market_cap, "东方财富 CSV raw_total_market_cap")
        if raw_total / Decimal("10000") != market_cap:
            raise ValueError("东方财富 CSV 市值单位换算不一致")
        raw_match = raw_by_date.get(row.date)
        if raw_match is None:
            raise ValueError("东方财富 CSV 日期未在原始分页中找到")
        if raw_match != (row.source_trade_date, raw_total):
            raise ValueError("东方财富 CSV 与原始分页内容不一致")
    if manifest.get("output_records") is not None:
        if _integer(manifest.get("output_records"), "东方财富 manifest output_records", 0) != len(frame):
            raise ValueError("东方财富 manifest output_records 不匹配")
    if manifest.get("data_range") is not None:
        data_range = manifest.get("data_range")
        if not isinstance(data_range, dict):
            raise ValueError("东方财富 manifest data_range 不是对象")
        if data_range.get("start_date") != dates[0] or data_range.get("end_date") != dates[-1]:
            raise ValueError("东方财富 manifest data_range 不匹配")
    return frame


def verify_post2017_vendor_inputs(
    project_root: Path,
) -> tuple[VendorMarketCapInput | None, str | None]:
    """验证已落盘的东方财富厂商链；无论失败原因均降级为余额包而非抛出。"""

    paths = _vendor_paths(project_root)
    try:
        manifest = _load_json_bytes(paths["manifest"], "东方财富 manifest")
        batches = _validate_vendor_manifest(manifest)
        raw_by_date = _validated_vendor_raw_records(paths, batches)
        frame = _validate_vendor_csv(paths["table"], manifest, raw_by_date)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        return None, f"东方财富后 2017 市值数据不可安全读取，比例为 N/A：{exc}"
    return VendorMarketCapInput(frame=frame, manifest=manifest, paths=paths), None


def _mx_pre2017_paths(project_root: Path) -> dict[str, Path]:
    directory = project_root / MX_PRE2017_OUTPUT_DIRECTORY
    return {
        "directory": directory,
        "table": directory / MX_PRE2017_TABLE_FILENAME,
        "manifest": directory / MX_PRE2017_MANIFEST_FILENAME,
        "audit": directory / MX_PRE2017_AUDIT_FILENAME,
    }


def _pre2017_dfcf_dates(margin: MarginInput) -> list[str]:
    values = [
        str(value)
        for value in margin.frame["date"].tolist()
        if date.fromisoformat(str(value)) < POST2017_START
    ]
    if (
        len(values) != PRE2017_REQUIRED_DATE_COUNT
        or not values
        or values[0] != PRE2017_REQUIRED_START
        or values[-1] != PRE2017_REQUIRED_END
    ):
        raise ValueError(
            "DFCF 前段共同日期不满足 2011-08-03 至 2016-12-30 的 1316 日合同"
        )
    return values


def _date_sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode("ascii")).hexdigest()


def _validate_mx_pre2017_manifest(
    manifest: dict[str, object], pre_dates: list[str]
) -> dict[str, object]:
    if manifest.get("schema_version") != 1:
        raise ValueError("东方财富妙想前段 manifest schema_version 不匹配")
    if manifest.get("source") != MX_PRE2017_SOURCE_NAME:
        raise ValueError("东方财富妙想前段 manifest source 不匹配")
    if manifest.get("source_url") != MX_PRE2017_URL:
        raise ValueError("东方财富妙想前段 manifest source_url 不匹配")
    if manifest.get("reporting_eligible") is not False:
        raise ValueError("东方财富妙想前段 manifest reporting_eligible 必须为 false")
    if manifest.get("ratio_review_status") != MX_PRE2017_REVIEW_STATUS:
        raise ValueError("东方财富妙想前段 manifest ratio_review_status 不匹配")
    if not isinstance(manifest.get("scope_warning"), str) or not manifest["scope_warning"].strip():
        raise ValueError("东方财富妙想前段 manifest 缺少 scope_warning")
    query = manifest.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("东方财富妙想前段 manifest 缺少 query")
    if _require_sha256(manifest.get("query_sha256"), "东方财富妙想前段 query_sha256") != hashlib.sha256(query.encode("utf-8")).hexdigest():
        raise ValueError("东方财富妙想前段 query_sha256 不匹配")
    contract = manifest.get("dfcf_pre2017_date_contract")
    expected_contract = {
        "start": pre_dates[0],
        "end": pre_dates[-1],
        "count": len(pre_dates),
        "date_sequence_sha256": _date_sequence_sha256(pre_dates),
    }
    if contract != expected_contract:
        raise ValueError("东方财富妙想前段 DFCF 日期合同不匹配")
    for field in ("requested_dfcf_common_dates", "matched_dfcf_common_dates"):
        if manifest.get(field) != pre_dates:
            raise ValueError(f"东方财富妙想前段 manifest {field} 不匹配")
    if manifest.get("missing_dfcf_common_dates") != []:
        raise ValueError("东方财富妙想前段 manifest 存在缺失 DFCF 日期")
    if manifest.get("returned_non_dfcf_dates") != []:
        raise ValueError("东方财富妙想前段 manifest 存在非 DFCF 日期")
    if _integer(manifest.get("output_records"), "东方财富妙想前段 output_records", 0) != len(pre_dates):
        raise ValueError("东方财富妙想前段 manifest output_records 不匹配")
    _require_sha256(manifest.get("csv_sha256"), "东方财富妙想前段 csv_sha256")
    financial_evidence_audit = {
        "applicable": False,
        "status": "N/A",
        "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
    }
    if manifest.get("financial_evidence_audit") != financial_evidence_audit:
        raise ValueError("东方财富妙想前段 financial_evidence_audit 不匹配")
    raw_response = manifest.get("raw_response")
    if not isinstance(raw_response, dict):
        raise ValueError("东方财富妙想前段 manifest 缺少 raw_response")
    if raw_response.get("relative_path") != "raw/mx-response.json":
        raise ValueError("东方财富妙想前段 raw_response relative_path 不匹配")
    _require_sha256(raw_response.get("sha256"), "东方财富妙想前段 raw_response sha256")
    _integer(raw_response.get("bytes"), "东方财富妙想前段 raw_response bytes", 1)
    if not isinstance(raw_response.get("question_id"), str) or not raw_response["question_id"].strip():
        raise ValueError("东方财富妙想前段 raw_response question_id 无效")
    return raw_response


def _validate_mx_pre2017_csv(
    table_path: Path,
    manifest: dict[str, object],
    pre_dates: list[str],
    raw_records: list[object],
    question_id: str,
    raw_response_sha256: str,
) -> pd.DataFrame:
    if _require_sha256(manifest.get("csv_sha256"), "东方财富妙想前段 CSV SHA-256") != sha256_file(table_path):
        raise ValueError("东方财富妙想前段 CSV SHA-256 不匹配")
    frame = _read_csv(table_path)
    if set(frame.columns) != set(MX_PRE2017_CSV_COLUMNS_ORDERED):
        raise ValueError("东方财富妙想前段 CSV 列集合不符合固定契约")
    if _validate_dates(frame, "东方财富妙想前段 CSV") != pre_dates:
        raise ValueError("东方财富妙想前段 CSV 日期与 DFCF 前段共同日期不一致")
    raw_by_date = {
        record.trade_date.isoformat(): record
        for record in raw_records
    }
    if set(raw_by_date) != set(pre_dates):
        raise ValueError("东方财富妙想前段原始响应日期与 DFCF 前段共同日期不一致")
    for row in frame.itertuples(index=False):
        if row.source != MX_PRE2017_SOURCE_NAME:
            raise ValueError("东方财富妙想前段 CSV source 不匹配")
        if _source_trade_date(row.source_trade_date, "东方财富妙想前段 source_trade_date") != row.date:
            raise ValueError("东方财富妙想前段 CSV date 与 source_trade_date 不一致")
        if row.source_question_id != question_id:
            raise ValueError("东方财富妙想前段 CSV question_id 与原始响应不一致")
        if (
            row.source_universe != "沪深A股"
            or row.source_metric_code != "ZSZ"
            or row.source_metric_name != "总市值(合计)_板块"
            or row.source_entity_code != "001004"
        ):
            raise ValueError("东方财富妙想前段 CSV 范围或指标字段不匹配")
        if row.raw_unit != "yuan" or row.unit_conversion != "raw_yuan_divided_by_100000000":
            raise ValueError("东方财富妙想前段 CSV 单位换算字段不匹配")
        if row.raw_response_sha256 != raw_response_sha256:
            raise ValueError("东方财富妙想前段 CSV 原始响应 SHA-256 不匹配")
        if row.status != "pass":
            raise ValueError("东方财富妙想前段 CSV status 不为 pass")
        raw_record = raw_by_date.get(row.date)
        if raw_record is None:
            raise ValueError("东方财富妙想前段 CSV 日期未在原始响应中找到")
        raw_market_cap = _positive_decimal(row.raw_market_cap, "东方财富妙想前段 raw_market_cap")
        market_cap = _positive_decimal(row.market_cap_yi, "东方财富妙想前段 market_cap_yi")
        if raw_market_cap != raw_record.raw_total_market_cap:
            raise ValueError("东方财富妙想前段 CSV 原始市值与原始响应不一致")
        if market_cap != raw_market_cap / Decimal("100000000"):
            raise ValueError("东方财富妙想前段 CSV 市值单位换算不一致")
    return frame


def verify_pre2017_mx_vendor_inputs(
    project_root: Path, margin: MarginInput
) -> tuple[MxPre2017VendorInput | None, str | None]:
    """复核前段东方财富妙想厂商链；失败时仅使前段比例降级为 N/A。"""

    paths = _mx_pre2017_paths(project_root)
    try:
        pre_dates = _pre2017_dfcf_dates(margin)
        manifest = _load_json_bytes(paths["manifest"], "东方财富妙想前段 manifest")
        audit = _load_json_bytes(paths["audit"], "东方财富妙想前段 audit")
        raw_response = _validate_mx_pre2017_manifest(manifest, pre_dates)
        _, raw_payload = _validated_bound_file(
            paths["directory"],
            raw_response.get("relative_path"),
            raw_response.get("sha256"),
            raw_response.get("bytes"),
            "东方财富妙想前段原始响应",
        )
        raw_records, question_id, source_profile = _parse_mx_response(
            raw_payload,
            expected_dates=[date.fromisoformat(value) for value in pre_dates],
        )
        if raw_response.get("question_id") != question_id:
            raise ValueError("东方财富妙想前段 question_id 与原始响应不一致")
        if manifest.get("source_profile") != source_profile:
            raise ValueError("东方财富妙想前段 source_profile 与原始响应不一致")
        frame = _validate_mx_pre2017_csv(
            paths["table"],
            manifest,
            pre_dates,
            raw_records,
            question_id,
            _require_sha256(raw_response.get("sha256"), "东方财富妙想前段 raw_response sha256"),
        )
        financial_evidence_audit = {
            "applicable": False,
            "status": "N/A",
            "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
        }
        expected_audit = {
            "schema_version": 1,
            "source": MX_PRE2017_SOURCE_NAME,
            "raw_response_sha256": manifest["raw_response"]["sha256"],
            "csv_sha256": manifest["csv_sha256"],
            "date_linkage_status": "pass",
            "scope_mapping_status": "pass",
            "decimal_calculation_status": "pass",
            "ratio_reporting_eligible": False,
            "dfcf_pre2017_date_contract": manifest["dfcf_pre2017_date_contract"],
            "financial_evidence_audit": financial_evidence_audit,
        }
        for field, value in expected_audit.items():
            if audit.get(field) != value:
                raise ValueError(f"东方财富妙想前段 audit {field} 不匹配")
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        return None, f"2011–2016 东方财富妙想厂商市值链不可安全读取，前段比例为 N/A：{exc}"
    return MxPre2017VendorInput(frame=frame, manifest=manifest, audit=audit, paths=paths), None


def _official_pre2017_paths(project_root: Path) -> dict[str, Path]:
    directory = project_root / OFFICIAL_PRE2017_OUTPUT_DIRECTORY
    return {
        "directory": directory,
        "table": directory / OFFICIAL_PRE2017_TABLE_FILENAME,
        "manifest": directory / OFFICIAL_PRE2017_MANIFEST_FILENAME,
        "audit": directory / OFFICIAL_PRE2017_AUDIT_FILENAME,
    }


def _official_mapping_contract() -> dict[str, object]:
    return {
        "schema_version": OFFICIAL_PRE2017_MAPPING_SCHEMA_VERSION,
        "header_order": ["股票", "主板A", "主板B", "科创板", "股票回购"],
        "product_type_order": ["40", "1", "2", "48", "43"],
        "product_type_mapping": {
            "40": "股票",
            "1": "主板A",
            "2": "主板B",
            "48": "科创板",
            "43": "股票回购",
        },
    }


def _normalise_official_text(value: object) -> str:
    return re.sub(r"\s+", "", str(value))


def _validate_official_mapping_payload(payload: bytes) -> dict[str, object]:
    expected = _official_mapping_contract()
    parsed = parse_sse_stockday_mapping_evidence(payload)
    if parsed != expected:
        raise ValueError("SSE 映射证据解析结果不符合既定契约")
    return parsed


def _validated_bound_file(
    root: Path, relative_path: object, sha256: object, byte_count: object, name: str
) -> tuple[Path, bytes]:
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError(f"{name} relative_path 无效")
    expected_sha = _require_sha256(sha256, f"{name} sha256")
    expected_bytes = _integer(byte_count, f"{name} bytes", 1)
    resolved_root = root.resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{name} raw 路径越界") from exc
    if not path.is_file():
        raise ValueError(f"{name} raw 文件不存在")
    payload = path.read_bytes()
    if len(payload) != expected_bytes or sha256_file(path) != expected_sha:
        raise ValueError(f"{name} raw SHA-256 或字节数不匹配")
    return path, payload


def _validate_official_sse_payload(payload: bytes, day: str) -> Decimal:
    def reject_constant(value: str) -> None:
        raise ValueError(f"SSE JSON 包含非有限值: {value}")

    try:
        decoded = json.loads(
            payload.decode("utf-8"),
            parse_float=Decimal,
            parse_int=Decimal,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("SSE 原始响应不是有效 JSON") from exc
    rows = decoded.get("result") if isinstance(decoded, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("SSE 原始响应缺少 result 列表")
    values: dict[str, Decimal] = {}
    tx_numbers: dict[str, Decimal] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("SSE 原始响应行不是对象")
        if parse_sse_cal_date(row.get("CAL_DATE")).isoformat() != day:
            raise ValueError("SSE CAL_DATE 与 DFCF 日期不一致")
        product_type = _normalise_official_text(row.get("PRODUCT_TYPE", ""))
        if product_type not in {"1", "2", "12"}:
            raise ValueError("SSE PRODUCT_TYPE 不在 1/2/12 严格集合")
        if product_type in values:
            raise ValueError("SSE PRODUCT_TYPE 重复")
        values[product_type] = _positive_decimal(
            row.get("MKT_VALUE_FULL"), "SSE MKT_VALUE_FULL"
        )
        tx_numbers[product_type] = parse_sse_tx_num(row.get("TX_NUM"))
    if set(values) != {"1", "2", "12"}:
        raise ValueError("SSE PRODUCT_TYPE 必须精确为 1、2、12")
    if abs(values["12"] - values["1"] - values["2"]) > OFFICIAL_PRE2017_SSE_TOTAL_TOLERANCE:
        raise ValueError("SSE PRODUCT_TYPE=12 市值不等于 1+2")
    if set(tx_numbers) != {"1", "2", "12"}:
        raise ValueError("SSE TX_NUM 必须在 1/2/12 同时存在")
    if abs(tx_numbers["12"] - tx_numbers["1"] - tx_numbers["2"]) > OFFICIAL_PRE2017_TX_NUM_TOLERANCE:
        raise ValueError("SSE PRODUCT_TYPE=12 TX_NUM 不等于 1+2")
    return values["1"]


def _validate_official_szse_workbook(payload: bytes) -> Decimal:
    try:
        frame = pd.read_excel(BytesIO(payload), header=0, dtype=object)
    except Exception as exc:
        raise ValueError("SZSE 原始工作簿不能解析") from exc
    expected_headers = ("证券类别", "数量(只)", "成交金额(元)", "总市值(元)", "流通市值(元)")
    headers = tuple(_normalise_official_text(value) for value in frame.columns)
    if headers[: len(expected_headers)] != expected_headers:
        raise ValueError("SZSE 工作簿表头不符合历史契约")
    category_map = {
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
        category = category_map.get(_normalise_official_text(row[category_column]))
        if category is None:
            continue
        if category in values:
            raise ValueError("SZSE 五个市值类别存在重复")
        values[category] = _positive_szse_market_cap_decimal(row[market_cap_column])
    required = {"stock_total", "main_a", "main_b", "sme_a", "chinext_a"}
    if set(values) != required:
        raise ValueError("SZSE 五个必需市值类别不完整")
    a_value = values["main_a"] + values["sme_a"] + values["chinext_a"]
    if abs(values["stock_total"] - a_value - values["main_b"]) > OFFICIAL_PRE2017_SZSE_TOTAL_TOLERANCE_YUAN:
        raise ValueError("SZSE 股票总市值不等于 A+B")
    return a_value / Decimal("100000000")


def _require_exact_dates(values: object, expected: list[str], name: str) -> None:
    if values != expected:
        raise ValueError(f"{name} 与 DFCF 前段共同日期不精确一致")


def verify_pre2017_official_inputs(
    project_root: Path, margin: MarginInput
) -> tuple[OfficialPre2017Input | None, str | None]:
    """独立复核前段官方原始链；任一门失败时只禁用前段比例。"""

    paths = _official_pre2017_paths(project_root)
    try:
        pre_dates = [
            str(value)
            for value in margin.frame["date"].tolist()
            if date.fromisoformat(str(value)) < POST2017_START
        ]
        if (
            len(pre_dates) != PRE2017_REQUIRED_DATE_COUNT
            or not pre_dates
            or pre_dates[0] != PRE2017_REQUIRED_START
            or pre_dates[-1] != PRE2017_REQUIRED_END
        ):
            raise ValueError(
                "DFCF 前段共同日期不满足 2011-08-03 至 2016-12-30 的 1316 日合同"
            )
        manifest = _load_json_bytes(paths["manifest"], "前段官方市值 manifest")
        audit = _load_json_bytes(paths["audit"], "前段官方市值 audit")
        if manifest.get("schema_version") != "2":
            raise ValueError("前段官方市值 manifest schema_version 不匹配")
        if manifest.get("source_segment") != "official_exchange_pre_2017":
            raise ValueError("前段官方市值 manifest source_segment 不匹配")
        if manifest.get("finalized") is not True or manifest.get("final_output_ready") is not True:
            raise ValueError("前段官方市值 manifest 未最终准出")
        if manifest.get("reporting_eligible") is not True:
            raise ValueError("前段官方市值 manifest reporting_eligible 不为 true")
        dfcf_input = manifest.get("dfcf_input")
        if not isinstance(dfcf_input, dict):
            raise ValueError("前段官方市值 manifest 缺少 dfcf_input")
        if dfcf_input.get("relative_path") != "artifacts/leverage_capitulation/dfcf_daily/dfcf_margin_balances.csv":
            raise ValueError("前段官方市值 manifest DFCF 路径不匹配")
        if dfcf_input.get("sha256") != sha256_file(margin.paths["balances"]):
            raise ValueError("前段官方市值 manifest DFCF SHA-256 不匹配")
        contract = manifest.get("dfcf_date_contract")
        if not isinstance(contract, dict):
            raise ValueError("前段官方市值 manifest 缺少 DFCF 日期合同")
        expected_contract = {
            "required_start": PRE2017_REQUIRED_START,
            "required_end": PRE2017_REQUIRED_END,
            "required_common_date_count": PRE2017_REQUIRED_DATE_COUNT,
            "available_common_date_count": PRE2017_REQUIRED_DATE_COUNT,
            "available_common_date_first": PRE2017_REQUIRED_START,
            "available_common_date_last": PRE2017_REQUIRED_END,
            "requested_is_full_contract": True,
        }
        for field, value in expected_contract.items():
            if contract.get(field) != value:
                raise ValueError(f"前段官方市值 DFCF 日期合同 {field} 不匹配")
        _require_exact_dates(manifest.get("requested_dates"), pre_dates, "manifest requested_dates")
        _require_exact_dates(manifest.get("completed_dates"), pre_dates, "manifest completed_dates")
        if manifest.get("missing_dates") != []:
            raise ValueError("前段官方市值 manifest 存在缺失日期")
        if _require_sha256(manifest.get("csv_sha256"), "前段官方市值 CSV SHA-256") != sha256_file(paths["table"]):
            raise ValueError("前段官方市值 CSV SHA-256 不匹配")

        mapping_entry = manifest.get("sse_mapping_evidence")
        if not isinstance(mapping_entry, dict):
            raise ValueError("前段官方市值缺少 SSE 映射证据")
        expected_mapping_fields = {
            "source_url": OFFICIAL_PRE2017_SSE_MAPPING_URL,
            "relative_path": "raw/sse_mapping/search_addhsl.js",
            "schema_version": OFFICIAL_PRE2017_MAPPING_SCHEMA_VERSION,
        }
        for field, value in expected_mapping_fields.items():
            if mapping_entry.get(field) != value:
                raise ValueError(f"SSE 映射证据 {field} 不匹配")
        _, mapping_payload = _validated_bound_file(
            paths["directory"],
            mapping_entry.get("relative_path"),
            mapping_entry.get("sha256"),
            mapping_entry.get("bytes"),
            "SSE 映射证据",
        )
        if mapping_entry.get("parsed") != _validate_official_mapping_payload(mapping_payload):
            raise ValueError("SSE 映射证据解析快照不匹配")

        sse_entries = manifest.get("sse_raw_entries")
        szse_entries = manifest.get("szse_raw_entries")
        if not isinstance(sse_entries, list) or not isinstance(szse_entries, list):
            raise ValueError("前段官方市值原始条目不是列表")
        if len(sse_entries) != len(pre_dates) or len(szse_entries) != len(pre_dates):
            raise ValueError("前段官方市值原始条目数量不等于 DFCF 共同日数量")
        sse_by_day: dict[str, tuple[str, Decimal]] = {}
        for entry in sse_entries:
            if not isinstance(entry, dict):
                raise ValueError("SSE 原始条目不是对象")
            day = entry.get("date")
            if not isinstance(day, str) or day not in pre_dates or day in sse_by_day:
                raise ValueError("SSE 原始条目日期缺失、越界或重复")
            expected_parameters = {
                "sqlId": "COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C",
                "stockType": "90",
                "searchDate": day,
            }
            if (
                entry.get("source_url") != OFFICIAL_PRE2017_SSE_URL
                or entry.get("request_parameters") != expected_parameters
                or entry.get("relative_path") != f"raw/sse/{day}.json"
                or entry.get("schema_version") != OFFICIAL_PRE2017_SSE_SCHEMA_VERSION
            ):
                raise ValueError("SSE 原始条目来源或请求参数不匹配")
            _, payload = _validated_bound_file(
                paths["directory"],
                entry.get("relative_path"),
                entry.get("sha256"),
                entry.get("bytes"),
                "SSE 原始条目",
            )
            sse_by_day[day] = (_require_sha256(entry.get("sha256"), "SSE 条目 SHA-256"), _validate_official_sse_payload(payload, day))
        if set(sse_by_day) != set(pre_dates):
            raise ValueError("SSE 原始条目未覆盖全部 DFCF 前段共同日")

        legacy_root_raw = manifest.get("legacy_raw_root")
        if not isinstance(legacy_root_raw, str) or not legacy_root_raw:
            raise ValueError("前段官方市值缺少 legacy_raw_root")
        legacy_root = Path(legacy_root_raw).resolve()
        expected_legacy_root = (
            project_root / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
        ).resolve()
        if legacy_root != expected_legacy_root:
            raise ValueError("legacy_raw_root 不是受控旧 SZSE 原始目录")
        legacy_manifest_path = legacy_root / "raw_response_manifest.json"
        if _require_sha256(manifest.get("legacy_raw_manifest_sha256"), "旧 SZSE manifest SHA-256") != sha256_file(legacy_manifest_path):
            raise ValueError("旧 SZSE manifest SHA-256 不匹配")
        legacy_manifest = json.loads(legacy_manifest_path.read_text(encoding="utf-8"))
        if not isinstance(legacy_manifest, list):
            raise ValueError("旧 SZSE manifest 不是列表")
        szse_by_day: dict[str, tuple[str, Decimal]] = {}
        for entry in szse_entries:
            if not isinstance(entry, dict):
                raise ValueError("SZSE 原始条目不是对象")
            day = entry.get("date")
            if not isinstance(day, str) or day not in pre_dates or day in szse_by_day:
                raise ValueError("SZSE 原始条目日期缺失、越界或重复")
            expected_parameters = {
                "SHOWTYPE": "xlsx",
                "CATALOGID": "1803_sczm",
                "TABKEY": "tab1",
                "txtQueryDate": day,
            }
            storage = entry.get("storage")
            if (
                entry.get("market") != "SZSE"
                or entry.get("source_url") != OFFICIAL_PRE2017_SZSE_URL
                or entry.get("request_parameters") != expected_parameters
                or entry.get("schema_version") != OFFICIAL_PRE2017_SZSE_SCHEMA_VERSION
                or storage not in {"legacy_read_only", "official_pre2017_output"}
            ):
                raise ValueError("SZSE 原始条目来源或请求参数不匹配")
            if storage == "legacy_read_only":
                if entry.get("relative_path") != f"raw/{day}_szse.xlsx":
                    raise ValueError("旧 SZSE 原始条目路径不匹配")
                legacy_matches = [
                    item for item in legacy_manifest
                    if isinstance(item, dict)
                    and {key: value for key, value in entry.items() if key != "storage"} == item
                ]
                if len(legacy_matches) != 1:
                    raise ValueError("SZSE 输出条目未精确绑定旧 manifest")
                raw_root = legacy_root
            else:
                if day != OFFICIAL_PRE2017_SZSE_GAP_DATE or entry.get("relative_path") != f"raw/szse/{day}.xlsx":
                    raise ValueError("新 SZSE 原始条目仅允许 2015-06-11 缺口")
                raw_root = paths["directory"]
            _, payload = _validated_bound_file(
                raw_root,
                entry.get("relative_path"),
                entry.get("sha256"),
                entry.get("bytes"),
                "SZSE 原始条目",
            )
            szse_by_day[day] = (_require_sha256(entry.get("sha256"), "SZSE 条目 SHA-256"), _validate_official_szse_workbook(payload))
        if set(szse_by_day) != set(pre_dates):
            raise ValueError("SZSE 原始条目未覆盖全部 DFCF 前段共同日")

        frame = _read_csv(paths["table"])
        expected_columns = {
            "date", "sh_a_market_cap_yi", "sz_a_market_cap_yi", "market_cap_yi",
            "source_segment", "status", "sse_raw_sha256", "szse_raw_sha256",
        }
        if set(frame.columns) != expected_columns:
            raise ValueError("前段官方市值 CSV 列集合不符合契约")
        _require_exact_dates(_validate_dates(frame, "前段官方市值 CSV"), pre_dates, "前段官方市值 CSV")
        for row in frame.itertuples(index=False):
            if row.source_segment != "official_exchange_pre_2017" or row.status != "pass":
                raise ValueError("前段官方市值 CSV source_segment 或 status 异常")
            sh = _positive_decimal(row.sh_a_market_cap_yi, "前段官方市值沪市")
            sz = _positive_decimal(row.sz_a_market_cap_yi, "前段官方市值深市")
            total = _positive_decimal(row.market_cap_yi, "前段官方市值合计")
            if sh + sz != total:
                raise ValueError("前段官方市值 CSV 沪深加总不一致")
            if sh != sse_by_day[row.date][1] or sz != szse_by_day[row.date][1]:
                raise ValueError("前段官方市值 CSV 数值与原始链不一致")
            if row.sse_raw_sha256 != sse_by_day[row.date][0] or row.szse_raw_sha256 != szse_by_day[row.date][0]:
                raise ValueError("前段官方市值 CSV 原始 SHA-256 关联不一致")

        expected_financial_audit = {
            "applicable": False,
            "status": "N/A",
            "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
        }
        raw_chain = manifest.get("raw_chain_audit")
        if not isinstance(raw_chain, dict):
            raise ValueError("前段官方市值 manifest 缺少 raw_chain_audit")
        for field, expected in {
            "official_raw_chain_status": "pass",
            "scope_mapping_status": "pass",
            "date_linkage_status": "pass",
            "decimal_calculation_status": "pass",
            "ratio_reporting_eligible": True,
        }.items():
            if raw_chain.get(field) != expected:
                raise ValueError(f"前段官方市值 raw_chain_audit {field} 不通过")
        if manifest.get("financial_evidence_audit") != expected_financial_audit:
            raise ValueError("前段官方市值 financial_evidence_audit 不符合非正式比例合同")
        if "audit_sha256" in audit:
            raise ValueError("前段官方市值 audit 不得自引用 SHA-256")
        for field, expected in {
            "source_segment": "official_exchange_pre_2017",
            "official_raw_chain_status": "pass",
            "scope_mapping_status": "pass",
            "date_linkage_status": "pass",
            "decimal_calculation_status": "pass",
            "ratio_reporting_eligible": True,
            "csv_sha256": manifest["csv_sha256"],
            "dfcf_input": manifest["dfcf_input"],
            "requested_dates": pre_dates,
            "completed_dates": pre_dates,
            "missing_dates": [],
            "sse_mapping_evidence": mapping_entry,
            "sse_raw_entry_count": len(pre_dates),
            "szse_raw_entry_count": len(pre_dates),
            "financial_evidence_audit": expected_financial_audit,
        }.items():
            if audit.get(field) != expected:
                raise ValueError(f"前段官方市值 audit {field} 不匹配")
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        return None, f"2011–2016 官方市值原始链不可安全读取，前段比例为 N/A：{exc}"
    return OfficialPre2017Input(frame=frame, manifest=manifest, audit=audit, paths=paths), None


def parse_day_bytes(payload: bytes) -> pd.DataFrame:
    if not payload or len(payload) % DAY_STRUCT.size:
        raise ValueError("TDX .day 文件为空或长度不是 32 字节的整数倍")
    records: list[dict[str, object]] = []
    for offset in range(0, len(payload), DAY_STRUCT.size):
        raw_date, _, _, _, close, _, _, _ = DAY_STRUCT.unpack(payload[offset : offset + DAY_STRUCT.size])
        close_value = Decimal(close) / Decimal("100")
        if close_value <= 0:
            raise ValueError("TDX .day 文件包含非正收盘价")
        records.append({"date": datetime.strptime(str(raw_date), "%Y%m%d").date().isoformat(), "close": close_value})
    frame = pd.DataFrame(records)
    _validate_dates(frame, "TDX .day")
    return frame


def _index_value(frame: pd.DataFrame, day: str) -> float | None:
    match = frame.loc[frame["date"].eq(day), "close"]
    if len(match) != 1:
        return None
    return float(_positive_decimal(match.iloc[0], "指数收盘价"))


def _ratio(numerator: Decimal, denominator: Decimal) -> float:
    with localcontext() as context:
        context.prec = 50
        value = (numerator / denominator * Decimal("100")).quantize(RATIO_QUANTUM, rounding=ROUND_HALF_UP)
    return float(value)


def _ratio_range(records: list[dict[str, object]]) -> dict[str, str | None]:
    days = [str(record["date"]) for record in records if record["ratio_pct"] is not None]
    return {"start": days[0] if days else None, "end": days[-1] if days else None}


def build_dashboard_records(
    margin: pd.DataFrame,
    vendor: VendorMarketCapInput | None,
    indices: dict[str, pd.DataFrame],
    vendor_reason: str | None,
    *,
    pre2017_mx_vendor: MxPre2017VendorInput | None = None,
    pre2017_mx_vendor_reason: str | None = None,
    official_pre2017: OfficialPre2017Input | None = None,
    official_pre2017_reason: str | None = None,
    official_pre2017_requested: bool = False,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    _validate_dates(margin, "DFCF 输出表")
    vendor_by_date: dict[str, object] = {}
    mx_pre2017_by_date: dict[str, object] = {}
    official_by_date: dict[str, object] = {}
    if vendor is not None:
        _validate_dates(vendor.frame, "东方财富市值输出表")
        vendor_by_date = {str(row.date): row for row in vendor.frame.itertuples(index=False)}
    if pre2017_mx_vendor is not None:
        _validate_dates(pre2017_mx_vendor.frame, "东方财富妙想前段市值输出表")
        mx_pre2017_by_date = {
            str(row.date): row
            for row in pre2017_mx_vendor.frame.itertuples(index=False)
        }
    if official_pre2017 is not None:
        _validate_dates(official_pre2017.frame, "前段官方市值输出表")
        official_by_date = {
            str(row.date): row
            for row in official_pre2017.frame.itertuples(index=False)
        }
    for ticker in INDEX_PATHS:
        if ticker not in indices:
            raise ValueError(f"缺少指数 {ticker}")
        _validate_dates(indices[ticker], f"指数 {ticker}")

    records: list[dict[str, object]] = []
    for row in margin.itertuples(index=False):
        day = str(row.date)
        denominator: float | None = None
        ratio: float | None = None
        if date.fromisoformat(day) < POST2017_START:
            source = OFFICIAL_PRE2017_UNAVAILABLE_SOURCE
            review_status = "unavailable"
            mx_row = mx_pre2017_by_date.get(day)
            official_row = official_by_date.get(day)
            if mx_row is not None:
                denominator_decimal = _positive_decimal(
                    mx_row.market_cap_yi, "mx_pre2017 market_cap_yi"
                )
                denominator = float(denominator_decimal)
                ratio = _ratio(
                    _positive_decimal(row.total_margin_y, "total_margin_y"),
                    denominator_decimal,
                )
                source = MX_PRE2017_SOURCE
                review_status = MX_PRE2017_REVIEW_STATUS
            elif official_row is not None:
                denominator_decimal = _positive_decimal(
                    official_row.market_cap_yi, "official_pre2017 market_cap_yi"
                )
                denominator = float(denominator_decimal)
                ratio = _ratio(
                    _positive_decimal(row.total_margin_y, "total_margin_y"),
                    denominator_decimal,
                )
                source = OFFICIAL_PRE2017_SOURCE
                review_status = OFFICIAL_PRE2017_REVIEW_STATUS
            elif pre2017_mx_vendor_reason is not None:
                source = MX_PRE2017_UNAVAILABLE_SOURCE
        else:
            source = "eastmoney_post2017_vendor_unverified"
            review_status = "unavailable"
            vendor_row = vendor_by_date.get(day)
            if vendor_row is not None:
                denominator_decimal = _positive_decimal(vendor_row.market_cap_yi, "market_cap_yi")
                denominator = float(denominator_decimal)
                ratio = _ratio(_positive_decimal(row.total_margin_y, "total_margin_y"), denominator_decimal)
                review_status = EASTMONEY_REVIEW_STATUS
        records.append(
            {
                "date": day,
                "sh_margin_yi": float(_positive_decimal(row.sh_margin_y, "sh_margin_y")),
                "sz_margin_yi": float(_positive_decimal(row.sz_margin_y, "sz_margin_y")),
                "total_margin_yi": float(_positive_decimal(row.total_margin_y, "total_margin_y")),
                "denominator_market_cap_yi": denominator,
                "market_cap_source": source,
                "market_cap_review_status": review_status,
                "ratio_pct": ratio,
                "index_000001_close": _index_value(indices["000001"], day),
                "index_399106_close": _index_value(indices["399106"], day),
                "index_399006_close": _index_value(indices["399006"], day),
            }
        )

    ratio_data_range = _ratio_range(records)
    ratio_available = ratio_data_range["start"] is not None
    if ratio_available:
        unavailable_reason = None
        if pre2017_mx_vendor is not None:
            scope_warning = MX_PRE2017_SCOPE_WARNING
        elif official_pre2017 is not None:
            scope_warning = (
                "2011-08-03 至 2016-12-30 分母已通过交易所原始链准出；"
                "但分子为 DFCF 厂商两融余额，financial-evidence-audit 对该聚合比值为 "
                "UNSUPPORTED_RATIO_CONTRACT，不能称为正式财务比例或严格证券类别匹配。"
            )
        else:
            scope_warning = vendor.manifest["scope_warning"] if vendor is not None else VENDOR_SCOPE_WARNING
    else:
        unavailable_reason = pre2017_mx_vendor_reason or official_pre2017_reason or vendor_reason or (
            "没有与 DFCF 日期精确匹配且通过校验的 2017-01-03 后东方财富市值记录，比例为 N/A。"
        )
        scope_warning = MX_PRE2017_SCOPE_WARNING if pre2017_mx_vendor_reason is not None else (
            "2011-08-03 至 2016-12-30 官方原始链未通过读取门，前段比例为 N/A；"
            + VENDOR_SCOPE_WARNING
        )
    provenance = {
        "ratio_available": ratio_available,
        "ratio_unavailable_reason": unavailable_reason,
        "ratio_scope_warning": scope_warning,
        "ratio_data_range": ratio_data_range,
        "source_switch_date": POST2017_START.isoformat(),
    }
    mx_schema = pre2017_mx_vendor is not None or (
        pre2017_mx_vendor_reason is not None and official_pre2017 is None
    )
    if mx_schema:
        provenance["mx_pre2017_chain_status"] = (
            "available" if pre2017_mx_vendor is not None else "unavailable"
        )
        provenance["mx_pre2017_unavailable_reason"] = pre2017_mx_vendor_reason
    else:
        provenance["official_pre2017_chain_status"] = (
            "available" if official_pre2017 is not None else "unavailable"
        )
        provenance["official_pre2017_unavailable_reason"] = official_pre2017_reason
    return records, provenance


def _json_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write_bytes(payload: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def build_payload(records: list[dict[str, object]], provenance: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "1",
        "generated_at_beijing": beijing_now(),
        "records": records,
        "provenance": provenance,
    }


def _source_segments(
    records: list[dict[str, object]],
    vendor_reason: str | None,
    official_pre2017_reason: str | None,
    pre2017_mx_vendor_reason: str | None,
) -> list[dict[str, object]]:
    mx_pre_records = [
        record
        for record in records
        if record["market_cap_source"] == MX_PRE2017_SOURCE
    ]
    mx_unavailable_pre_records = [
        record
        for record in records
        if record["market_cap_source"] == MX_PRE2017_UNAVAILABLE_SOURCE
    ]
    official_pre_records = [
        record
        for record in records
        if record["market_cap_source"] == OFFICIAL_PRE2017_SOURCE
    ]
    unavailable_pre_records = [
        record
        for record in records
        if record["market_cap_source"] == OFFICIAL_PRE2017_UNAVAILABLE_SOURCE
    ]
    post_records = [record for record in records if record["market_cap_source"] == "eastmoney_post2017_vendor_unverified"]
    segments: list[dict[str, object]] = []
    if mx_pre_records:
        segments.append(
            {
                "start": mx_pre_records[0]["date"],
                "end": mx_pre_records[-1]["date"],
                "market_cap_source": MX_PRE2017_SOURCE,
                "market_cap_review_status": MX_PRE2017_REVIEW_STATUS,
                "ratio_available": True,
                "reason": MX_PRE2017_SCOPE_WARNING,
            }
        )
    if mx_unavailable_pre_records:
        segments.append(
            {
                "start": mx_unavailable_pre_records[0]["date"],
                "end": mx_unavailable_pre_records[-1]["date"],
                "market_cap_source": MX_PRE2017_UNAVAILABLE_SOURCE,
                "market_cap_review_status": "unavailable",
                "ratio_available": False,
                "reason": pre2017_mx_vendor_reason or "东方财富妙想前段厂商市值链不可用，比例为 N/A。",
            }
        )
    if official_pre_records:
        segments.append(
            {
                "start": official_pre_records[0]["date"],
                "end": official_pre_records[-1]["date"],
                "market_cap_source": OFFICIAL_PRE2017_SOURCE,
                "market_cap_review_status": OFFICIAL_PRE2017_REVIEW_STATUS,
                "ratio_available": True,
                "reason": (
                    "分母原始链通过交易所哈希、日期和 Decimal 校验；"
                    "聚合比例仍为 UNSUPPORTED_RATIO_CONTRACT，非正式财务比例。"
                ),
            }
        )
    if unavailable_pre_records:
        segments.append(
            {
                "start": unavailable_pre_records[0]["date"],
                "end": unavailable_pre_records[-1]["date"],
                "market_cap_source": OFFICIAL_PRE2017_UNAVAILABLE_SOURCE,
                "market_cap_review_status": "unavailable",
                "ratio_available": False,
                "reason": official_pre2017_reason or PRE2017_REASON,
            }
        )
    if post_records:
        segments.append(
            {
                "start": post_records[0]["date"],
                "end": post_records[-1]["date"],
                "market_cap_source": "eastmoney_post2017_vendor_unverified",
                "market_cap_review_status": EASTMONEY_REVIEW_STATUS if vendor_reason is None else "unavailable",
                "ratio_available": any(record["ratio_pct"] is not None for record in post_records),
                "reason": vendor_reason,
            }
        )
    return segments


def _manifest_reason(
    provenance: dict[str, object],
    vendor_reason: str | None,
    official_pre2017_reason: str | None,
    *,
    pre2017_mx_vendor: MxPre2017VendorInput | None,
    pre2017_mx_vendor_reason: str | None,
    official_pre2017: OfficialPre2017Input | None,
) -> str:
    if vendor_reason:
        return (
            f"2011–2016 前段状态：{pre2017_mx_vendor_reason or official_pre2017_reason or PRE2017_REASON}；"
            f"2017 后厂商分母亦不可用：{vendor_reason}"
        )
    if provenance["ratio_available"] is True:
        if pre2017_mx_vendor is not None:
            return (
                "2011–2016 前段分母为东方财富妙想厂商口径，2017-01-03 起为东方财富 Choice 厂商口径；"
                "两段均未经交易所复核和完整审计，且口径边界可能造成水平不可直接拼接比较。"
                "全段聚合比例不是正式 financial-evidence-audit 准出指标。"
            )
        if official_pre2017 is None:
            return (
                f"2011–2016 前段状态：{(pre2017_mx_vendor_reason or official_pre2017_reason or PRE2017_REASON).rstrip('。')}；"
                "2017-01-03 起分母仅为东方财富 Choice 厂商口径，"
                "未经交易所复核或完整审计。全段聚合比例不是正式 financial-evidence-audit 准出指标。"
            )
        return (
            "前段分母使用交易所原始链；后段分母仅为东方财富 Choice 厂商口径，"
            "未经交易所复核或完整审计。全段聚合比例不是正式 financial-evidence-audit 准出指标。"
        )
    return (
        f"2011–2016 前段状态：{pre2017_mx_vendor_reason or official_pre2017_reason or PRE2017_REASON}；"
        "2017-01-03 起没有可精确匹配 DFCF 日期的合格厂商分母。"
    )


def build_manifest(
    records: list[dict[str, object]],
    provenance: dict[str, object],
    margin: MarginInput,
    vendor: VendorMarketCapInput | None,
    vendor_reason: str | None,
    index_metadata: dict[str, object],
    *,
    pre2017_mx_vendor: MxPre2017VendorInput | None = None,
    pre2017_mx_vendor_reason: str | None = None,
    official_pre2017: OfficialPre2017Input | None = None,
    official_pre2017_reason: str | None = None,
    official_pre2017_requested: bool = False,
) -> dict[str, object]:
    missing_records = sum(record["ratio_pct"] is None for record in records)
    dfcf_inputs = {
        path.name: sha256_file(path)
        for name, path in margin.paths.items()
        if name in {"sse", "szse", "balances"}
    }
    if pre2017_mx_vendor is not None:
        ratio_review_status = MIXED_MX_VENDOR_REVIEW_STATUS
    elif official_pre2017 is not None:
        ratio_review_status = MIXED_AUDITED_REVIEW_STATUS
    elif pre2017_mx_vendor_reason is not None:
        ratio_review_status = MIXED_MX_UNAVAILABLE_REVIEW_STATUS
    else:
        ratio_review_status = MIXED_OFFICIAL_UNAVAILABLE_REVIEW_STATUS
    if pre2017_mx_vendor is not None:
        scope_definition = (
            "分子为 DFCF 两市融资余额厂商口径，可能含非 A 股融资标的；"
            "2011-08-03 至 2016-12-30 的分母为东方财富妙想沪深A股日度总市值，"
            "2017-01-03 起分母为东方财富 Choice RPT_VALUEMARKET / TRADE_MARKET_CODE=000300。"
            "两段均未经交易所复核和完整审计，口径边界可能造成水平不可直接拼接比较；"
            "全段均不能称为严格证券类别匹配或正式财务比例。"
        )
    else:
        scope_definition = (
            "分子为 DFCF 两市融资余额厂商口径，可能含非 A 股融资标的；"
            "2011-08-03 至 2016-12-30 的分母仅在官方原始链、DFCF 日期绑定和独立审计均通过时启用；"
            "2017-01-03 起分母为东方财富 Choice RPT_VALUEMARKET / TRADE_MARKET_CODE=000300，"
            "未经交易所复核和完整审计。全段均不能称为严格证券类别匹配或正式财务比例。"
        )
    market_cap: dict[str, object] = {
        "reporting_eligible": False,
        "ratio_available": provenance["ratio_available"] is True,
        "ratio_review_status": ratio_review_status,
        "reason": _manifest_reason(
            provenance,
            vendor_reason,
            official_pre2017_reason,
            pre2017_mx_vendor=pre2017_mx_vendor,
            pre2017_mx_vendor_reason=pre2017_mx_vendor_reason,
            official_pre2017=official_pre2017,
        ),
        "ratio_data_range": provenance["ratio_data_range"],
        "ratio_missing_records": missing_records,
        "source_switch_date": POST2017_START.isoformat(),
        "source_segments": _source_segments(
            records, vendor_reason, official_pre2017_reason, pre2017_mx_vendor_reason
        ),
        "scope_definition": scope_definition,
        "source_url": vendor.manifest["source_url"] if vendor is not None else None,
        "csv_sha256": vendor.manifest["csv_sha256"] if vendor is not None else None,
    }
    if pre2017_mx_vendor is not None or (
        pre2017_mx_vendor_reason is not None and official_pre2017 is None
    ):
        market_cap["mx_pre2017"] = {
            "available": pre2017_mx_vendor is not None,
            "reason": pre2017_mx_vendor_reason,
            "table_sha256": (
                pre2017_mx_vendor.manifest["csv_sha256"]
                if pre2017_mx_vendor is not None
                else None
            ),
            "raw_response_sha256": (
                pre2017_mx_vendor.manifest["raw_response"]["sha256"]
                if pre2017_mx_vendor is not None
                else None
            ),
            "date_contract_status": (
                "pass" if pre2017_mx_vendor is not None else "blocked"
            ),
            "financial_evidence_audit": (
                pre2017_mx_vendor.audit["financial_evidence_audit"]
                if pre2017_mx_vendor is not None
                else {
                    "applicable": False,
                    "status": "N/A",
                    "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
                }
            ),
        }
    else:
        market_cap["official_pre2017"] = {
            "available": official_pre2017 is not None,
            "reason": official_pre2017_reason,
            "table_sha256": (
                official_pre2017.manifest["csv_sha256"]
                if official_pre2017 is not None
                else None
            ),
            "raw_chain_status": (
                official_pre2017.audit["official_raw_chain_status"]
                if official_pre2017 is not None
                else ("blocked" if official_pre2017_requested else "not_requested")
            ),
            "financial_evidence_audit": (
                official_pre2017.audit["financial_evidence_audit"]
                if official_pre2017 is not None
                else {
                    "applicable": False,
                    "status": "N/A",
                    "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
                }
            ),
        }
    return {
        "schema_version": "1",
        "payload_sha256": None,
        "payload_records": len(records),
        "data_range": {
            "start": records[0]["date"] if records else None,
            "end": records[-1]["date"] if records else None,
        },
        "dfcf": {
            "dfcf_only": margin.audit["dfcf_only"],
            "exchange_requests": margin.audit["exchange_requests"],
            "sample_status": margin.audit["sample_status"],
            "inputs": dfcf_inputs,
        },
        "market_cap": market_cap,
        "indices": index_metadata,
        "description": MANIFEST_DESCRIPTION,
    }


def write_bundle(
    output_dir: Path, payload: dict[str, object], manifest: dict[str, object]
) -> tuple[Path, Path]:
    payload_path = output_dir / "leverage-dashboard.json"
    manifest_path = output_dir / "leverage-dashboard.manifest.json"
    _atomic_write_bytes(_json_bytes(payload), payload_path)
    completed_manifest = dict(manifest)
    completed_manifest["payload_sha256"] = sha256_file(payload_path)
    _atomic_write_bytes(_json_bytes(completed_manifest), manifest_path)
    return payload_path, manifest_path


def _verify_artifact_bundle(payload_path: Path, manifest_path: Path) -> dict[str, object]:
    manifest = _load_json_bytes(manifest_path, "dashboard manifest")
    if _require_sha256(manifest.get("payload_sha256"), "dashboard manifest payload_sha256") != sha256_file(payload_path):
        raise ValueError("发布前 payload SHA-256 自检失败")
    payload = _load_json_bytes(payload_path, "dashboard payload")
    records = payload.get("records")
    if not isinstance(records, list) or manifest.get("payload_records") != len(records):
        raise ValueError("发布前 payload_records 自检失败")
    return manifest


def _verify_existing_published_bundle(payload_path: Path, manifest_path: Path) -> dict[str, object]:
    """校验可被 Task 4b 覆盖的旧对；只兼容旧 manifest 的 row_count 快照字段。"""

    manifest = _load_json_bytes(manifest_path, "已发布 dashboard manifest")
    if _require_sha256(manifest.get("payload_sha256"), "已发布 dashboard payload_sha256") != sha256_file(payload_path):
        raise ValueError("已发布 dashboard payload SHA-256 不匹配")
    payload = _load_json_bytes(payload_path, "已发布 dashboard payload")
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("已发布 dashboard records 不是列表")
    record_count = manifest.get("payload_records", manifest.get("row_count"))
    if _integer(record_count, "已发布 dashboard 记录数", 0) != len(records):
        raise ValueError("已发布 dashboard 记录数不匹配")
    return manifest


def _published_bundle_snapshot(
    payload_target: Path, manifest_target: Path
) -> tuple[bytes, bytes] | None:
    payload_exists = payload_target.exists()
    manifest_exists = manifest_target.exists()
    if payload_exists != manifest_exists:
        raise ValueError("发布目录已有不完整 dashboard JSON 对，拒绝覆盖")
    if not payload_exists:
        return None
    _verify_existing_published_bundle(payload_target, manifest_target)
    return payload_target.read_bytes(), manifest_target.read_bytes()


def _restore_published_bundle(
    snapshot: tuple[bytes, bytes] | None, payload_target: Path, manifest_target: Path
) -> None:
    if snapshot is None:
        for path in (payload_target, manifest_target):
            if path.exists():
                path.unlink()
        return
    previous_payload, previous_manifest = snapshot
    _atomic_write_bytes(previous_payload, payload_target)
    _atomic_write_bytes(previous_manifest, manifest_target)
    _verify_existing_published_bundle(payload_target, manifest_target)


def publish_bundle_atomically(payload_path: Path, manifest_path: Path, publish_dir: Path) -> None:
    if publish_dir.resolve() != PUBLISH_DIRECTORY.resolve():
        raise ValueError(f"publish-dir 必须为已授权路径: {PUBLISH_DIRECTORY}")
    _verify_artifact_bundle(payload_path, manifest_path)
    payload_target = publish_dir / payload_path.name
    manifest_target = publish_dir / manifest_path.name
    snapshot = _published_bundle_snapshot(payload_target, manifest_target)
    try:
        # Manifest 是提交标记：在它原子替换前，任何读取方都只能看到旧 manifest，
        # 新 payload 与旧 manifest 的哈希不匹配会被读取方拒绝，而不会被当成有效新版本。
        _atomic_write_bytes(payload_path.read_bytes(), payload_target)
        _atomic_write_bytes(manifest_path.read_bytes(), manifest_target)
        if sha256_file(payload_target) != sha256_file(payload_path):
            raise ValueError("发布后 payload SHA-256 自检失败")
        if sha256_file(manifest_target) != sha256_file(manifest_path):
            raise ValueError("发布后 manifest SHA-256 自检失败")
        _verify_artifact_bundle(payload_target, manifest_target)
    except Exception:
        try:
            _restore_published_bundle(snapshot, payload_target, manifest_target)
        except Exception as rollback_error:
            raise RuntimeError("dashboard JSON 发布失败且回滚失败；发布对可能不一致") from rollback_error
        raise


def _load_indices() -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    indices: dict[str, pd.DataFrame] = {}
    metadata: dict[str, object] = {}
    for ticker, path in INDEX_PATHS.items():
        payload = path.read_bytes()
        indices[ticker] = parse_day_bytes(payload)
        last_date = indices[ticker].iloc[-1]["date"]
        metadata[ticker] = {
            "source": INDEX_SOURCE,
            "path": str(path),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "sha256_covers_through": last_date,
            "source_snapshot_hash_status": INDEX_SNAPSHOT_HASH_RECORDED,
            "first_date": indices[ticker].iloc[0]["date"],
            "last_date": last_date,
        }
    return indices, metadata


def resolve_project_root(value: str | None) -> Path:
    root = Path(value).expanduser().resolve() if value else Path(__file__).resolve().parents[1]
    if not (root / "AGENTS.md").exists():
        raise FileNotFoundError(f"cannot confirm project root: {root}")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="构建两融网页静态发布包")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--publish-dir", default=None)
    parser.add_argument(
        "--allow-official-pre2017-fallback",
        action="store_true",
        help="仅当东方财富妙想前段厂商链不可用时，才读取既有官方前段链。",
    )
    args = parser.parse_args()
    project_root = resolve_project_root(args.project_root)
    output_dir = project_root / OUTPUT_DIRECTORY
    margin = verify_dfcf_inputs(project_root)
    pre2017_mx_vendor, pre2017_mx_vendor_reason = verify_pre2017_mx_vendor_inputs(
        project_root, margin
    )
    official_pre2017: OfficialPre2017Input | None = None
    official_pre2017_reason: str | None = None
    official_pre2017_requested = False
    if pre2017_mx_vendor is None and args.allow_official_pre2017_fallback:
        official_pre2017_requested = True
        official_pre2017, official_pre2017_reason = verify_pre2017_official_inputs(
            project_root, margin
        )
    vendor, vendor_reason = verify_post2017_vendor_inputs(project_root)
    indices, index_metadata = _load_indices()
    records, provenance = build_dashboard_records(
        margin.frame,
        vendor,
        indices,
        vendor_reason,
        pre2017_mx_vendor=pre2017_mx_vendor,
        pre2017_mx_vendor_reason=pre2017_mx_vendor_reason,
        official_pre2017=official_pre2017,
        official_pre2017_reason=official_pre2017_reason,
        official_pre2017_requested=official_pre2017_requested,
    )
    payload = build_payload(records, provenance)
    manifest = build_manifest(
        records,
        provenance,
        margin,
        vendor,
        vendor_reason,
        index_metadata,
        pre2017_mx_vendor=pre2017_mx_vendor,
        pre2017_mx_vendor_reason=pre2017_mx_vendor_reason,
        official_pre2017=official_pre2017,
        official_pre2017_reason=official_pre2017_reason,
        official_pre2017_requested=official_pre2017_requested,
    )
    payload_path, manifest_path = write_bundle(output_dir, payload, manifest)
    if args.publish_dir:
        publish_bundle_atomically(payload_path, manifest_path, Path(args.publish_dir).expanduser().resolve())
    _verify_artifact_bundle(payload_path, manifest_path)
    print(manifest_path.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
