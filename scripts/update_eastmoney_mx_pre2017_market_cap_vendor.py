from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

import requests


SOURCE_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/query"
SOURCE_NAME = "东方财富妙想厂商数据"
SOURCE_ENTITY_ID = "001004"
SOURCE_ENTITY_NAME = "沪深A股"
SOURCE_ENTITY_CLASS = "市场类(沪深京)"
SOURCE_INDICATOR = "ZSZ"
DISPLAY_UNIT = "万亿"
RAW_UNIT = "yuan"
YUAN_PER_YI = Decimal("100000000")
EARLIEST_SUPPORTED_DATE = date(2011, 8, 3)
LATEST_PRE2017_DATE = date(2016, 12, 30)
OUTPUT_DIRECTORY = Path("artifacts/leverage_capitulation/mx_pre2017_market_cap_vendor")
TABLE_FILENAME = "mx_pre2017_market_cap_vendor.csv"
MANIFEST_FILENAME = "mx_pre2017_market_cap_vendor_manifest.json"
AUDIT_FILENAME = "mx_pre2017_market_cap_vendor_audit.json"
RATIO_REVIEW_STATUS = "mx_vendor_unverified"
CSV_COLUMNS = [
    "date",
    "market_cap_yi",
    "source",
    "source_trade_date",
    "source_question_id",
    "source_universe",
    "source_metric_code",
    "source_metric_name",
    "source_entity_code",
    "raw_market_cap",
    "raw_unit",
    "unit_conversion",
    "raw_response_sha256",
    "status",
]
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\(日\)\Z")
_MARKET_CAP_RE = re.compile(r"(\d+(?:\.\d+)?)万亿\Z")


@dataclass(frozen=True)
class VendorRecord:
    trade_date: date
    raw_total_market_cap: Decimal
    market_cap_yi: Decimal


@dataclass(frozen=True)
class UpdateOptions:
    session: requests.Session
    api_key: str
    timeout_seconds: int


def _required_dict(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"东方财富妙想响应缺少 {name}")
    return value


def _parse_trade_date(value: object) -> date:
    if not isinstance(value, str):
        raise ValueError("东方财富妙想日期不是字符串")
    match = _DATE_RE.fullmatch(value)
    if match is None:
        raise ValueError("东方财富妙想日期格式不符合日度合同")
    return date.fromisoformat(match.group(1))


def _parse_market_cap(value: object) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("东方财富妙想总市值不是字符串")
    match = _MARKET_CAP_RE.fullmatch(value)
    if match is None:
        raise ValueError("东方财富妙想总市值单位不是万亿")
    try:
        parsed = Decimal(match.group(1))
    except InvalidOperation as exc:
        raise ValueError("东方财富妙想总市值不是有限十进制") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise ValueError("东方财富妙想总市值必须为正数")
    return parsed


def _parse_raw_trade_date(value: object) -> date:
    if not isinstance(value, str):
        raise ValueError("东方财富妙想原始日期不是字符串")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("东方财富妙想原始日期格式无效") from exc


def _parse_raw_market_cap(value: object) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("东方财富妙想原始总市值不是字符串")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("东方财富妙想原始总市值不是有限十进制") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise ValueError("东方财富妙想原始总市值必须为正数")
    return parsed


def _parse_mx_response(
    payload_bytes: bytes, *, expected_dates: list[date]
) -> tuple[list[VendorRecord], str, dict[str, str]]:
    """把妙想沪深A股总市值日度响应严格转换为 DFCF 日期集合。"""
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("东方财富妙想响应不是 UTF-8 JSON") from exc
    root = _required_dict(payload, "顶层对象")
    if root.get("status") != 0:
        raise ValueError(f"东方财富妙想业务状态异常: {root.get('status')}")
    outer_data = _required_dict(root.get("data"), "data")
    inner_data = _required_dict(outer_data.get("data"), "data.data")
    search = _required_dict(inner_data.get("searchDataResultDTO"), "searchDataResultDTO")
    question_id = search.get("questionId")
    if not isinstance(question_id, str) or not question_id.strip():
        raise ValueError("东方财富妙想响应缺少 questionId")
    tables = search.get("dataTableDTOList")
    if not isinstance(tables, list) or len(tables) != 1:
        raise ValueError("东方财富妙想必须返回唯一沪深A股市值表")
    dto = _required_dict(tables[0], "市值表")
    entity = _required_dict(dto.get("entityTagDTO"), "实体标签")
    if (
        entity.get("entityId") != SOURCE_ENTITY_ID
        or entity.get("fullName") != SOURCE_ENTITY_NAME
        or entity.get("className") != SOURCE_ENTITY_CLASS
    ):
        raise ValueError("东方财富妙想实体范围不是沪深A股")
    field = _required_dict(dto.get("field"), "指标字段")
    if (
        field.get("returnSourceCode") != SOURCE_INDICATOR
        or field.get("dateGranularity") != "DAY"
        or field.get("returnName") != "总市值(合计)"
        or field.get("returnSourceName") != "总市值(合计)_板块"
        or field.get("unit") != "1"
    ):
        raise ValueError("东方财富妙想指标不是沪深A股日度总市值")
    table = _required_dict(dto.get("table"), "市值表数据")
    head_names = table.get("headName")
    if not isinstance(head_names, list) or not head_names:
        raise ValueError("东方财富妙想市值表没有日期列")
    indicator_columns = [key for key in table if key != "headName"]
    if len(indicator_columns) != 1:
        raise ValueError("东方财富妙想市值表指标列不唯一")
    indicator = indicator_columns[0]
    if field.get("returnCode") != indicator:
        raise ValueError("东方财富妙想市值表指标编码不匹配")
    display_values = table[indicator]
    if not isinstance(display_values, list) or len(display_values) != len(head_names):
        raise ValueError("东方财富妙想市值表日期和值数量不一致")

    raw_table = _required_dict(dto.get("rawTable"), "原始市值表")
    raw_dates = raw_table.get("headName")
    raw_values = raw_table.get(indicator)
    if (
        not isinstance(raw_dates, list)
        or not isinstance(raw_values, list)
        or len(raw_dates) != len(head_names)
        or len(raw_values) != len(head_names)
    ):
        raise ValueError("东方财富妙想原始市值表日期和值数量不一致")

    expected = list(expected_dates)
    if expected != sorted(expected) or len(expected) != len(set(expected)):
        raise ValueError("DFCF 预期日期必须唯一且升序")
    records_by_date: dict[date, VendorRecord] = {}
    for display_date, display_market_cap, raw_date, raw_market_cap in zip(
        head_names, display_values, raw_dates, raw_values, strict=True
    ):
        trade_date = _parse_trade_date(display_date)
        if _parse_raw_trade_date(raw_date) != trade_date:
            raise ValueError("东方财富妙想原始日期与展示日期不一致")
        if trade_date in records_by_date:
            raise ValueError("东方财富妙想市值表存在重复日期")
        display_total = _parse_market_cap(display_market_cap)
        raw_total = _parse_raw_market_cap(raw_market_cap)
        if (raw_total / Decimal("1000000000000")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ) != display_total:
            raise ValueError("东方财富妙想原始总市值与展示值不一致")
        records_by_date[trade_date] = VendorRecord(
            trade_date=trade_date,
            raw_total_market_cap=raw_total,
            market_cap_yi=raw_total / YUAN_PER_YI,
        )
    if set(records_by_date) != set(expected):
        raise ValueError("东方财富妙想日期与 DFCF 前段共同日期不精确一致")
    return (
        [records_by_date[value] for value in expected],
        question_id,
        {
            "entity_id": SOURCE_ENTITY_ID,
            "entity_name": SOURCE_ENTITY_NAME,
            "entity_class": SOURCE_ENTITY_CLASS,
            "return_code": indicator,
            "return_name": str(field["returnName"]),
            "return_source_code": SOURCE_INDICATOR,
            "return_source_name": str(field["returnSourceName"]),
            "date_granularity": "DAY",
            "raw_unit": RAW_UNIT,
        },
    )


def parse_mx_payload(
    payload_bytes: bytes, *, expected_dates: list[date]
) -> list[VendorRecord]:
    records, _, _ = _parse_mx_response(payload_bytes, expected_dates=expected_dates)
    return records


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _date_sequence_sha256(days: list[date]) -> str:
    return sha256_bytes(
        ("\n".join(value.isoformat() for value in days) + "\n").encode("ascii")
    )


def _zh_date(value: date) -> str:
    return f"{value.year}年{value.month}月{value.day}日"


def build_query(start_date: date, end_date: date) -> str:
    return f"{_zh_date(start_date)}至{_zh_date(end_date)}沪深A股每日总市值"


def load_dfcf_pre2017_common_dates(
    project_root: Path, start_date: date, end_date: date
) -> list[date]:
    if (
        start_date < EARLIEST_SUPPORTED_DATE
        or end_date > LATEST_PRE2017_DATE
        or start_date > end_date
    ):
        raise ValueError("前段日期必须在 2011-08-03 至 2016-12-30 内")
    table_path = (
        project_root
        / "artifacts"
        / "leverage_capitulation"
        / "dfcf_daily"
        / "dfcf_margin_balances.csv"
    )
    try:
        with table_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or "date" not in reader.fieldnames:
                raise ValueError("DFCF 合并表缺少 date 列")
            values = [
                date.fromisoformat(str(row["date"]))
                for row in reader
                if start_date <= date.fromisoformat(str(row["date"])) <= end_date
            ]
    except (OSError, ValueError) as exc:
        raise ValueError(f"无法读取 DFCF 前段共同日期: {exc}") from exc
    if not values or values != sorted(values) or len(values) != len(set(values)):
        raise ValueError("DFCF 前段共同日期必须非空、唯一且升序")
    return values


def _fetch_mx_payload(query: str, options: UpdateOptions) -> bytes:
    if not options.api_key:
        raise ValueError("MX_APIKEY 未配置")
    response = options.session.post(
        SOURCE_URL,
        headers={"Content-Type": "application/json", "apikey": options.api_key},
        json={"toolQuery": query},
        timeout=options.timeout_seconds,
    )
    response.raise_for_status()
    return response.content


def _csv_bytes(
    records: list[VendorRecord], *, question_id: str, raw_response_sha256: str
) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow(
            {
                "date": record.trade_date.isoformat(),
                "market_cap_yi": format(record.market_cap_yi, "f"),
                "source": SOURCE_NAME,
                "source_trade_date": record.trade_date.isoformat(),
                "source_question_id": question_id,
                "source_universe": SOURCE_ENTITY_NAME,
                "source_metric_code": SOURCE_INDICATOR,
                "source_metric_name": "总市值(合计)_板块",
                "source_entity_code": SOURCE_ENTITY_ID,
                "raw_market_cap": format(record.raw_total_market_cap, "f"),
                "raw_unit": RAW_UNIT,
                "unit_conversion": "raw_yuan_divided_by_100000000",
                "raw_response_sha256": raw_response_sha256,
                "status": "pass",
            }
        )
    return buffer.getvalue().encode("utf-8")


def _atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(value)
    os.replace(temporary, path)


def _beijing_now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def update_vendor_market_cap(
    project_root: Path, requested_dates: list[date], options: UpdateOptions
) -> dict[str, object]:
    if (
        not requested_dates
        or requested_dates != sorted(requested_dates)
        or len(requested_dates) != len(set(requested_dates))
        or requested_dates[0] < EARLIEST_SUPPORTED_DATE
        or requested_dates[-1] > LATEST_PRE2017_DATE
    ):
        raise ValueError("DFCF 前段请求日期必须唯一、有序且在受支持区间")
    query = build_query(requested_dates[0], requested_dates[-1])
    payload = _fetch_mx_payload(query, options)
    records, question_id, source_profile = _parse_mx_response(
        payload, expected_dates=requested_dates
    )
    output_dir = project_root / OUTPUT_DIRECTORY
    raw_path = output_dir / "raw/mx-response.json"
    table_path = output_dir / TABLE_FILENAME
    manifest_path = output_dir / MANIFEST_FILENAME
    audit_path = output_dir / AUDIT_FILENAME
    raw_sha256 = sha256_bytes(payload)
    csv_bytes = _csv_bytes(
        records, question_id=question_id, raw_response_sha256=raw_sha256
    )
    scope_warning = (
        "东方财富妙想厂商口径／未经交易所复核、未经完整审计；"
        "实体为沪深A股（entityId=001004），日度总市值指标 ZSZ；"
        "原始金额按展示值交叉核对后以元除以 100000000 转为亿元。"
        "分子为 DFCF 两融余额，可能含非 A 股融资标的；该聚合比例不是正式财务比例。"
    )
    date_contract = {
        "start": requested_dates[0].isoformat(),
        "end": requested_dates[-1].isoformat(),
        "count": len(requested_dates),
        "date_sequence_sha256": _date_sequence_sha256(requested_dates),
    }
    manifest = {
        "schema_version": 1,
        "source": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "reporting_eligible": False,
        "ratio_review_status": RATIO_REVIEW_STATUS,
        "scope_warning": scope_warning,
        "query": query,
        "query_sha256": sha256_bytes(query.encode("utf-8")),
        "source_profile": source_profile,
        "raw_response": {
            "relative_path": "raw/mx-response.json",
            "bytes": len(payload),
            "sha256": raw_sha256,
            "question_id": question_id,
        },
        "dfcf_pre2017_date_contract": date_contract,
        "requested_dfcf_common_dates": [value.isoformat() for value in requested_dates],
        "matched_dfcf_common_dates": [value.isoformat() for value in requested_dates],
        "missing_dfcf_common_dates": [],
        "returned_non_dfcf_dates": [],
        "output_records": len(records),
        "csv_sha256": sha256_bytes(csv_bytes),
        "financial_evidence_audit": {
            "applicable": False,
            "status": "N/A",
            "reason_code": "UNSUPPORTED_RATIO_CONTRACT",
        },
        "generated_at_beijing": _beijing_now(),
    }
    audit = {
        "schema_version": 1,
        "source": SOURCE_NAME,
        "raw_response_sha256": raw_sha256,
        "csv_sha256": manifest["csv_sha256"],
        "date_linkage_status": "pass",
        "scope_mapping_status": "pass",
        "decimal_calculation_status": "pass",
        "ratio_reporting_eligible": False,
        "dfcf_pre2017_date_contract": date_contract,
        "financial_evidence_audit": manifest["financial_evidence_audit"],
        "updated_at_beijing": _beijing_now(),
    }
    _atomic_write_bytes(raw_path, payload)
    _atomic_write_bytes(table_path, csv_bytes)
    _atomic_write_bytes(
        manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    _atomic_write_bytes(
        audit_path, (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    return {
        "output_records": len(records),
        "missing_dfcf_common_dates": [],
        "output_dir": str(output_dir),
        "reporting_eligible": False,
    }


def resolve_project_root(value: str | None) -> Path:
    project_root = Path(value).expanduser().resolve() if value else Path(__file__).resolve().parents[1]
    if not (project_root / "AGENTS.md").exists():
        raise FileNotFoundError("无法确认项目根目录")
    return project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="重建冻结的东方财富妙想前 2017 沪深A股市值快照")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--start-date", type=date.fromisoformat, default=EARLIEST_SUPPORTED_DATE)
    parser.add_argument("--end-date", type=date.fromisoformat, default=LATEST_PRE2017_DATE)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--rebuild-frozen-snapshot",
        action="store_true",
        help="仅限用户明确授权时重建完整前2017冻结快照；日常自动化不得使用。",
    )
    args = parser.parse_args()
    if args.start_date != EARLIEST_SUPPORTED_DATE or args.end_date != LATEST_PRE2017_DATE:
        parser.error("前2017冻结快照只能覆盖完整固定日期段")
    if not args.dry_run and not args.rebuild_frozen_snapshot:
        parser.error("前2017冻结快照默认只读；重建必须显式传入 --rebuild-frozen-snapshot")
    project_root = resolve_project_root(args.project_root)
    requested_dates = load_dfcf_pre2017_common_dates(
        project_root, args.start_date, args.end_date
    )
    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "requested_dates": len(requested_dates),
                    "query": build_query(requested_dates[0], requested_dates[-1]),
                    "output_dir": str(project_root / OUTPUT_DIRECTORY),
                },
                ensure_ascii=False,
            )
        )
        return
    api_key = os.environ.get("MX_APIKEY", "")
    result = update_vendor_market_cap(
        project_root,
        requested_dates,
        UpdateOptions(
            session=requests.Session(), api_key=api_key, timeout_seconds=args.timeout_seconds
        ),
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
