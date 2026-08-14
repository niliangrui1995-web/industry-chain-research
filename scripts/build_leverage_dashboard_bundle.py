from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


DAY_STRUCT = struct.Struct("<IIIIIfII")
DFCF_STATUS = "dfcf_vendor_only_unverified_by_exchange"
RATIO_QUANTUM = Decimal("0.00000001")
PRE2017_END = date(2016, 12, 30)
POST2017_START = date(2017, 1, 3)
OUTPUT_DIRECTORY = Path("artifacts/leverage_capitulation/dashboard_bundle")
PUBLISH_DIRECTORY = Path(r"D:\vcp_hunter\基金持仓\public\data")
VENDOR_OUTPUT_DIRECTORY = Path(
    "artifacts/leverage_capitulation/eastmoney_post2017_market_cap_vendor"
)
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
    "2017-01-03 前交易所市值分段尚未通过：SSE PRODUCT_TYPE=12 无官方日度分类映射，"
    "且 2015-06-11 缺少 SZSE 原始文件；此前比例为 N/A。"
)
INDEX_PATHS = {
    "000001": Path(r"D:\HT\vipdoc\sh\lday\sh000001.day"),
    "399106": Path(r"D:\HT\vipdoc\sz\lday\sz399106.day"),
    "399006": Path(r"D:\HT\vipdoc\sz\lday\sz399006.day"),
}
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


def _validate_vendor_manifest(manifest: dict[str, object]) -> tuple[list[dict[str, object]], str, str]:
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
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("东方财富 manifest pages 缺失")
    requested_start = _strict_date(manifest.get("requested_start"), "东方财富 manifest requested_start")
    requested_end = _strict_date(manifest.get("requested_end"), "东方财富 manifest requested_end")
    if requested_start > requested_end:
        raise ValueError("东方财富 manifest requested 日期范围倒序")
    return pages, requested_start, requested_end


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
    paths: dict[str, Path], pages: list[dict[str, object]], requested_start: str, requested_end: str
) -> dict[str, tuple[str, Decimal]]:
    raw_root = paths["raw"].resolve()
    records: list[tuple[str, str, Decimal]] = []
    reported_count: int | None = None
    reported_pages: int | None = None
    for expected_page_number, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            raise ValueError("东方财富 manifest page 不是对象")
        if _integer(page.get("page_number"), "东方财富 page_number", 1) != expected_page_number:
            raise ValueError("东方财富 manifest pages 必须从 1 连续编号")
        _validate_vendor_page_request(page, expected_page_number, requested_start, requested_end)
        expected_relative = Path("raw") / f"page-{expected_page_number:04d}.json"
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
    return {trade_date: (source_trade_date, raw_total) for trade_date, source_trade_date, raw_total in records}


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
        pages, requested_start, requested_end = _validate_vendor_manifest(manifest)
        raw_by_date = _validated_vendor_raw_records(paths, pages, requested_start, requested_end)
        frame = _validate_vendor_csv(paths["table"], manifest, raw_by_date)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        return None, f"东方财富后 2017 市值数据不可安全读取，比例为 N/A：{exc}"
    return VendorMarketCapInput(frame=frame, manifest=manifest, paths=paths), None


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
) -> tuple[list[dict[str, object]], dict[str, object]]:
    _validate_dates(margin, "DFCF 输出表")
    vendor_by_date: dict[str, object] = {}
    if vendor is not None:
        _validate_dates(vendor.frame, "东方财富市值输出表")
        vendor_by_date = {str(row.date): row for row in vendor.frame.itertuples(index=False)}
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
            source = "pre2017_official_pending"
            review_status = "unavailable"
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
        scope_warning = vendor.manifest["scope_warning"] if vendor is not None else VENDOR_SCOPE_WARNING
    else:
        unavailable_reason = vendor_reason or (
            "没有与 DFCF 日期精确匹配且通过校验的 2017-01-03 后东方财富市值记录，比例为 N/A。"
        )
        scope_warning = VENDOR_SCOPE_WARNING
    provenance = {
        "ratio_available": ratio_available,
        "ratio_unavailable_reason": unavailable_reason,
        "ratio_scope_warning": scope_warning,
        "ratio_data_range": ratio_data_range,
        "source_switch_date": POST2017_START.isoformat(),
    }
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


def _source_segments(records: list[dict[str, object]], vendor_reason: str | None) -> list[dict[str, object]]:
    pre_records = [record for record in records if record["market_cap_source"] == "pre2017_official_pending"]
    post_records = [record for record in records if record["market_cap_source"] == "eastmoney_post2017_vendor_unverified"]
    segments: list[dict[str, object]] = []
    if pre_records:
        segments.append(
            {
                "start": pre_records[0]["date"],
                "end": pre_records[-1]["date"],
                "market_cap_source": "pre2017_official_pending",
                "market_cap_review_status": "unavailable",
                "ratio_available": False,
                "reason": PRE2017_REASON,
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


def _manifest_reason(provenance: dict[str, object], vendor_reason: str | None) -> str:
    if vendor_reason:
        return f"{PRE2017_REASON} 后 2017 厂商分母亦不可用：{vendor_reason}"
    if provenance["ratio_available"] is True:
        return f"{PRE2017_REASON} 2017-01-03 起比例仅为东方财富 Choice 厂商口径，未经交易所复核或完整审计。"
    return f"{PRE2017_REASON} 2017-01-03 起没有可精确匹配 DFCF 日期的合格厂商分母。"


def build_manifest(
    records: list[dict[str, object]],
    provenance: dict[str, object],
    margin: MarginInput,
    vendor: VendorMarketCapInput | None,
    vendor_reason: str | None,
    index_metadata: dict[str, object],
) -> dict[str, object]:
    missing_records = sum(record["ratio_pct"] is None for record in records)
    dfcf_inputs = {
        path.name: sha256_file(path)
        for name, path in margin.paths.items()
        if name in {"sse", "szse", "balances"}
    }
    market_cap = {
        "reporting_eligible": False,
        "ratio_available": provenance["ratio_available"] is True,
        "ratio_review_status": "mixed_pre2017_pending_eastmoney_vendor_unverified",
        "reason": _manifest_reason(provenance, vendor_reason),
        "ratio_data_range": provenance["ratio_data_range"],
        "ratio_missing_records": missing_records,
        "source_switch_date": POST2017_START.isoformat(),
        "source_segments": _source_segments(records, vendor_reason),
        "scope_definition": (
            "分子为 DFCF 两市融资余额厂商口径；2011-08-03 至 2016-12-30 的交易所市值分段待定，"
            "比例为 N/A；2017-01-03 起分母为东方财富 Choice RPT_VALUEMARKET / "
            "TRADE_MARKET_CODE=000300，未经交易所复核和完整审计，不能称为严格沪深 A 股市值。"
        ),
        "source_url": vendor.manifest["source_url"] if vendor is not None else None,
        "csv_sha256": vendor.manifest["csv_sha256"] if vendor is not None else None,
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
        "description": "DFCF 两融余额与三指数静态数据包；两融余额下降仅为去杠杆压力代理，不证明强平、底部或反弹。",
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
        indices[ticker] = parse_day_bytes(path.read_bytes())
        metadata[ticker] = {
            "source": "本地TDX厂商日线",
            "path": str(path),
            "sha256": sha256_file(path),
            "first_date": indices[ticker].iloc[0]["date"],
            "last_date": indices[ticker].iloc[-1]["date"],
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
    args = parser.parse_args()
    project_root = resolve_project_root(args.project_root)
    output_dir = project_root / OUTPUT_DIRECTORY
    margin = verify_dfcf_inputs(project_root)
    vendor, vendor_reason = verify_post2017_vendor_inputs(project_root)
    indices, index_metadata = _load_indices()
    records, provenance = build_dashboard_records(margin.frame, vendor, indices, vendor_reason)
    payload = build_payload(records, provenance)
    manifest = build_manifest(records, provenance, margin, vendor, vendor_reason, index_metadata)
    payload_path, manifest_path = write_bundle(output_dir, payload, manifest)
    if args.publish_dir:
        publish_bundle_atomically(payload_path, manifest_path, Path(args.publish_dir).expanduser().resolve())
    _verify_artifact_bundle(payload_path, manifest_path)
    print(manifest_path.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
