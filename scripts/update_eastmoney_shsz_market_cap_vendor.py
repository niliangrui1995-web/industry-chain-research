from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
from typing import Any
from zoneinfo import ZoneInfo

import requests


EASTMONEY_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
REPORT_NAME = "RPT_VALUEMARKET"
MARKET_CODE = "000300"
POST2017_START = date(2017, 1, 3)
OUTPUT_DIRECTORY = Path(
    "artifacts/leverage_capitulation/eastmoney_post2017_market_cap_vendor"
)
TABLE_FILENAME = "eastmoney_post2017_market_cap_vendor.csv"
MANIFEST_FILENAME = "eastmoney_post2017_market_cap_vendor_manifest.json"
RAW_DIRECTORY = Path("raw")
SOURCE_NAME = "东方财富Choice厂商数据"
RATIO_REVIEW_STATUS = "eastmoney_vendor_unverified"
CSV_COLUMNS = [
    "date",
    "market_cap_yi",
    "source",
    "source_market_code",
    "source_trade_date",
    "raw_total_market_cap",
    "unit_conversion",
    "status",
]
_SOURCE_DATE_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?\Z"
)


@dataclass(frozen=True)
class VendorRecord:
    trade_date: date
    source_trade_date: str
    raw_total_market_cap: Decimal
    market_cap_yi: Decimal


@dataclass(frozen=True)
class ParsedPage:
    page_number: int
    pages: int
    count: int
    records: list[VendorRecord]
    payload: bytes


@dataclass(frozen=True)
class UpdateOptions:
    session: object | None
    page_size: int
    timeout_seconds: int
    max_retries: int
    sleep_seconds: float


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_date(value: object, *, field_name: str = "date") -> date:
    if isinstance(value, datetime):
        raise ValueError(f"{field_name} 必须是 YYYY-MM-DD")
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError(f"{field_name} 必须是 YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} 不是有效日期") from exc


def _source_date(value: object) -> tuple[date, str]:
    if not isinstance(value, str):
        raise ValueError("TRADE_DATE 必须是日期字符串")
    source_value = value.strip()
    match = _SOURCE_DATE_RE.fullmatch(source_value)
    if match is None:
        raise ValueError("TRADE_DATE 不是可验证的日期")
    return _strict_date(match.group(1), field_name="TRADE_DATE"), source_value


def _positive_decimal(value: object, *, field_name: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{field_name} 必须是正数")
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError(f"{field_name} 必须是正数")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} 必须是正数") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError(f"{field_name} 必须是正数")
    return amount


def decimal_to_yi(value: object) -> Decimal:
    return _positive_decimal(value, field_name="TOTAL_MARKET_CAP") / Decimal("10000")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"东方财富 JSON 包含非有限值: {value}")


def _integer_metadata(value: object, *, field_name: str, minimum: int) -> int:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{field_name} 缺失或不是整数")
    try:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} 缺失或不是整数") from exc
    if not decimal_value.is_finite() or decimal_value != decimal_value.to_integral_value():
        raise ValueError(f"{field_name} 缺失或不是整数")
    result = int(decimal_value)
    if result < minimum:
        raise ValueError(f"{field_name} 超出允许范围")
    return result


def _page_count(result: dict[str, object], *, page_size: int) -> int:
    for key in ("pages", "pageCount", "totalPages"):
        if key in result:
            return _integer_metadata(result[key], field_name=f"result.{key}", minimum=1)
    if "count" not in result:
        raise ValueError("result 缺少可证明分页完整性的 count/pages")
    count = _integer_metadata(result["count"], field_name="result.count", minimum=0)
    return max(1, math.ceil(count / page_size))


def _result_page_number(result: dict[str, object], expected_page_number: int) -> None:
    for key in ("pageNum", "pageNumber", "pageNo"):
        if key in result:
            actual = _integer_metadata(result[key], field_name=f"result.{key}", minimum=1)
            if actual != expected_page_number:
                raise ValueError("东方财富返回页码与请求页码不一致")
            return


def parse_page_payload(
    payload: bytes,
    *,
    expected_page_number: int,
    requested_start: date,
    requested_end: date,
    page_size: int = 500,
) -> ParsedPage:
    if not payload:
        raise ValueError("东方财富响应为空")
    try:
        decoded = json.loads(
            payload.decode("utf-8"),
            parse_float=Decimal,
            parse_int=Decimal,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("东方财富响应不是有效 JSON") from exc
    if not isinstance(decoded, dict) or decoded.get("success") is not True:
        raise ValueError("东方财富响应 success 不为 true")
    result = decoded.get("result")
    if not isinstance(result, dict):
        raise ValueError("东方财富响应缺少 result 对象")
    rows = result.get("data")
    if not isinstance(rows, list):
        raise ValueError("东方财富响应缺少 result.data 列表")
    count = _integer_metadata(result.get("count"), field_name="result.count", minimum=0)
    pages = _page_count(result, page_size=page_size)
    _result_page_number(result, expected_page_number)
    records: list[VendorRecord] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("东方财富 result.data 行不是对象")
        if row.get("TRADE_MARKET_CODE") != MARKET_CODE:
            raise ValueError("TRADE_MARKET_CODE 与请求的 000300 不一致")
        trade_date, source_trade_date = _source_date(row.get("TRADE_DATE"))
        if trade_date < requested_start or trade_date > requested_end:
            raise ValueError("TRADE_DATE 超出请求区间")
        raw_total_market_cap = _positive_decimal(
            row.get("TOTAL_MARKET_CAP"), field_name="TOTAL_MARKET_CAP"
        )
        records.append(
            VendorRecord(
                trade_date=trade_date,
                source_trade_date=source_trade_date,
                raw_total_market_cap=raw_total_market_cap,
                market_cap_yi=decimal_to_yi(raw_total_market_cap),
            )
        )
    return ParsedPage(
        page_number=expected_page_number,
        pages=pages,
        count=count,
        records=records,
        payload=payload,
    )


def validate_vendor_records(records: list[VendorRecord]) -> None:
    dates = [record.trade_date for record in records]
    if len(dates) != len(set(dates)) or dates != sorted(dates):
        raise ValueError("东方财富市值日期必须唯一且升序")


def _request_parameters(start_date: date, end_date: date, page_number: int, page_size: int) -> dict[str, object]:
    return {
        "reportName": REPORT_NAME,
        "columns": "ALL",
        "filter": (
            f'(TRADE_MARKET_CODE="{MARKET_CODE}")'
            f"(TRADE_DATE>='{start_date.isoformat()}')"
            f"(TRADE_DATE<='{end_date.isoformat()}')"
        ),
        "source": "WEB",
        "client": "WEB",
        "pageNumber": page_number,
        "pageSize": page_size,
        "sortColumns": "TRADE_DATE",
        "sortTypes": "1",
    }


def _request_page(
    options: UpdateOptions, *, start_date: date, end_date: date, page_number: int
) -> tuple[bytes, int, dict[str, object]]:
    if options.session is None:
        raise RuntimeError("东方财富 HTTP session 不可用")
    params = _request_parameters(start_date, end_date, page_number, options.page_size)
    last_error: Exception | None = None
    for attempt in range(options.max_retries + 1):
        try:
            response = options.session.get(
                EASTMONEY_URL,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
                    "Accept": "application/json, text/plain, */*",
                },
                timeout=options.timeout_seconds,
            )
            if getattr(response, "status_code", None) != 200:
                raise ValueError(f"东方财富 HTTP 状态异常: {getattr(response, 'status_code', None)}")
            payload = getattr(response, "content", None)
            if not isinstance(payload, bytes) or not payload:
                raise ValueError("东方财富 HTTP 响应为空")
            return payload, attempt + 1, params
        except (OSError, requests.RequestException, TypeError, ValueError) as exc:
            last_error = exc
            if attempt < options.max_retries:
                time.sleep(2**attempt)
    raise RuntimeError(
        f"东方财富请求第 {page_number} 页在 {options.max_retries + 1} 次尝试后失败: {last_error}"
    )


def fetch_vendor_pages(
    start_date: date, end_date: date, options: UpdateOptions
) -> tuple[list[ParsedPage], int, list[dict[str, object]]]:
    payload, attempts, parameters = _request_page(
        options, start_date=start_date, end_date=end_date, page_number=1
    )
    first = parse_page_payload(
        payload,
        expected_page_number=1,
        requested_start=start_date,
        requested_end=end_date,
        page_size=options.page_size,
    )
    pages = [first]
    request_log = [{"parameters": parameters, "attempts": attempts}]
    network_requests = attempts
    for page_number in range(2, first.pages + 1):
        if options.sleep_seconds:
            time.sleep(options.sleep_seconds)
        payload, attempts, parameters = _request_page(
            options,
            start_date=start_date,
            end_date=end_date,
            page_number=page_number,
        )
        page = parse_page_payload(
            payload,
            expected_page_number=page_number,
            requested_start=start_date,
            requested_end=end_date,
            page_size=options.page_size,
        )
        if page.pages != first.pages or page.count != first.count:
            raise ValueError("东方财富分页元数据在不同页之间不一致")
        pages.append(page)
        request_log.append({"parameters": parameters, "attempts": attempts})
        network_requests += attempts
    records = [record for page in pages for record in page.records]
    if len(records) != first.count:
        raise ValueError("东方财富返回行数不能证明与 count 一致")
    validate_vendor_records(records)
    return pages, network_requests, request_log


def _dfcf_balances_path(project_root: Path) -> Path:
    return project_root / "artifacts/leverage_capitulation/dfcf_daily/dfcf_margin_balances.csv"


def load_dfcf_post2017_common_dates(
    project_root: Path, start_date: date, end_date: date
) -> list[date]:
    if start_date < POST2017_START:
        raise ValueError("东方财富市值分段不得触及 2017-01-03 之前日期")
    if start_date > end_date:
        raise ValueError("--start-date 不能晚于 --end-date")
    path = _dfcf_balances_path(project_root)
    if not path.exists():
        raise FileNotFoundError(f"DFCF 合并表不存在: {path}")
    requested: list[date] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "date" not in reader.fieldnames:
            raise ValueError("DFCF 合并表缺少 date 列")
        for row in reader:
            day = _strict_date(row.get("date"), field_name="DFCF date")
            if start_date <= day <= end_date:
                requested.append(day)
    if len(requested) != len(set(requested)) or requested != sorted(requested):
        raise ValueError("DFCF 共同日期必须唯一且升序")
    return requested


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _atomic_write_bytes(payload: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _atomic_write_csv(rows: list[dict[str, str]], path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def _beijing_now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def _output_path(output_dir: Path, relative_path: Path) -> Path:
    root = output_dir.resolve()
    candidate = (output_dir / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("输出路径越过东方财富厂商目录边界")
    return candidate


def _table_rows(records: list[VendorRecord]) -> list[dict[str, str]]:
    return [
        {
            "date": record.trade_date.isoformat(),
            "market_cap_yi": format(record.market_cap_yi, "f"),
            "source": SOURCE_NAME,
            "source_market_code": MARKET_CODE,
            "source_trade_date": record.source_trade_date,
            "raw_total_market_cap": format(record.raw_total_market_cap, "f"),
            "unit_conversion": "raw_divided_by_10000",
            "status": "pass",
        }
        for record in records
    ]


def update_vendor_market_cap(
    project_root: Path, requested_dates: list[date], options: UpdateOptions
) -> dict[str, object]:
    if any(day < POST2017_START for day in requested_dates):
        raise ValueError("东方财富市值分段不得触及 2017-01-03 之前日期")
    if requested_dates != sorted(requested_dates) or len(requested_dates) != len(set(requested_dates)):
        raise ValueError("DFCF 请求日期必须唯一且升序")
    output_dir = project_root / OUTPUT_DIRECTORY
    if not requested_dates:
        return {
            "requested_dates": 0,
            "network_requests": 0,
            "output_dir": str(output_dir),
            "written": False,
        }
    start_date = requested_dates[0]
    end_date = requested_dates[-1]
    pages, network_requests, request_log = fetch_vendor_pages(start_date, end_date, options)
    all_records = [record for page in pages for record in page.records]
    requested_set = set(requested_dates)
    output_records = [record for record in all_records if record.trade_date in requested_set]
    available_dates = {record.trade_date for record in output_records}
    missing_dates = [day.isoformat() for day in requested_dates if day not in available_dates]
    non_dfcf_dates = [
        record.trade_date.isoformat()
        for record in all_records
        if record.trade_date not in requested_set
    ]

    page_manifest: list[dict[str, object]] = []
    for page in pages:
        relative_path = RAW_DIRECTORY / f"page-{page.page_number:04d}.json"
        raw_path = _output_path(output_dir, relative_path)
        _atomic_write_bytes(page.payload, raw_path)
        page_manifest.append(
            {
                "page_number": page.page_number,
                "relative_path": relative_path.as_posix(),
                "sha256": sha256_file(raw_path),
                "bytes": raw_path.stat().st_size,
                "returned_rows": len(page.records),
                "reported_count": page.count,
                "reported_pages": page.pages,
                "request": request_log[page.page_number - 1],
            }
        )

    table_path = _output_path(output_dir, Path(TABLE_FILENAME))
    manifest_path = _output_path(output_dir, Path(MANIFEST_FILENAME))
    _atomic_write_csv(_table_rows(output_records), table_path)
    manifest = {
        "source": SOURCE_NAME,
        "source_url": EASTMONEY_URL,
        "report_name": REPORT_NAME,
        "source_market_code": MARKET_CODE,
        "requested_start": start_date.isoformat(),
        "requested_end": end_date.isoformat(),
        "requested_dfcf_common_dates": len(requested_dates),
        "output_records": len(output_records),
        "data_range": {
            "start_date": output_records[0].trade_date.isoformat() if output_records else None,
            "end_date": output_records[-1].trade_date.isoformat() if output_records else None,
        },
        "missing_dfcf_common_dates": missing_dates,
        "returned_non_dfcf_dates": non_dfcf_dates,
        "pages": page_manifest,
        "network_requests": network_requests,
        "response_count": len(pages),
        "csv_sha256": sha256_file(table_path),
        "reporting_eligible": False,
        "ratio_review_status": RATIO_REVIEW_STATUS,
        "scope_warning": (
            "东方财富 Choice 厂商口径／未经交易所复核、未经完整审计；"
            "仅覆盖 2017-01-03 及以后与 DFCF 共同日期精确重合的记录；"
            "A/B、CDR、基金等资产范围未核验，分子可能含非 A 股融资标的。"
        ),
        "generated_at_beijing": _beijing_now(),
    }
    _atomic_write_bytes(_json_bytes(manifest), manifest_path)
    return {
        "requested_dates": len(requested_dates),
        "output_records": len(output_records),
        "network_requests": network_requests,
        "output_dir": str(output_dir),
        "written": True,
    }


def resolve_project_root(value: str | None) -> Path:
    root = Path(value).expanduser().resolve() if value else Path(__file__).resolve().parents[1]
    if not (root / "AGENTS.md").exists():
        raise FileNotFoundError(f"无法确认项目根目录: {root}")
    return root


def _parse_cli_date(value: str) -> date:
    try:
        return _strict_date(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("日期必须为 YYYY-MM-DD") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="更新东方财富2017年后沪深两市市值厂商序列")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--start-date", type=_parse_cli_date, default=POST2017_START)
    parser.add_argument("--end-date", type=_parse_cli_date, default=date.today())
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.start_date < POST2017_START:
        parser.error("--start-date 不得早于 2017-01-03")
    if args.start_date > args.end_date:
        parser.error("--start-date 不能晚于 --end-date")
    if args.page_size <= 0 or args.timeout_seconds <= 0 or args.max_retries < 0 or args.sleep_seconds < 0:
        parser.error("分页、超时、重试和等待参数超出允许范围")
    project_root = resolve_project_root(args.project_root)
    requested_dates = load_dfcf_post2017_common_dates(
        project_root, args.start_date, args.end_date
    )
    output_dir = project_root / OUTPUT_DIRECTORY
    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "requested_dates": len(requested_dates),
                    "requested_start": requested_dates[0].isoformat() if requested_dates else None,
                    "requested_end": requested_dates[-1].isoformat() if requested_dates else None,
                    "output_dir": str(output_dir),
                    "source_url": EASTMONEY_URL,
                },
                ensure_ascii=False,
            )
        )
        return
    result = update_vendor_market_cap(
        project_root,
        requested_dates,
        UpdateOptions(
            session=requests.Session(),
            page_size=args.page_size,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            sleep_seconds=args.sleep_seconds,
        ),
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
