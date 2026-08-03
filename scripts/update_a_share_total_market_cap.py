from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests


SOURCE_PAGE_URL = "https://legulegu.com/stockdata/marketcap-gdp"
SOURCE_API_PATH = "/api/stockdata/marketcap-gdp/get-marketcap-gdp"
SOURCE_API_URL = f"https://legulegu.com{SOURCE_API_PATH}"
SAMPLE_STATUS = "vendor_only_unverified_by_official_source_with_date_quality_flags"
SOURCE_NAME = "乐咕乐股/LeguLegu厂商数据"
SOURCE_DEFINITION = "∑A股市值（上交所、深交所、北交所已上市股票）"
HEADERS = {
    "Referer": SOURCE_PAGE_URL,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def api_token(token_date: date) -> str:
    return hashlib.md5(token_date.isoformat().encode("utf-8")).hexdigest()


def fetch_market_cap_payload(
    session: requests.Session,
) -> tuple[list[dict[str, object]], str, str, str]:
    page = session.get(SOURCE_PAGE_URL, headers=HEADERS, timeout=30)
    page.raise_for_status()
    csrf_match = re.search(r'<meta name="_csrf" content="([^"]+)"', page.text)
    header_match = re.search(r'<meta name="_csrf_header" content="([^"]+)"', page.text)
    if not csrf_match or not header_match:
        raise ValueError("乐咕乐股页面未提供 CSRF 参数")

    token_date = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    api_url = f"{SOURCE_API_URL}?token={api_token(token_date)}"
    response = session.get(
        api_url,
        headers={**HEADERS, "Accept": "application/json, text/plain, */*", header_match.group(1): csrf_match.group(1)},
        timeout=30,
    )
    response.raise_for_status()
    payload_bytes = response.content
    payload = response.json()
    records = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("乐咕乐股接口未返回总市值历史数据")
    retrieved_at_bj = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    return records, token_date.isoformat(), retrieved_at_bj, hashlib.sha256(payload_bytes).hexdigest()


def build_frame(
    records: list[dict[str, object]], *, start_date: str, end_date: str
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    lower = pd.Timestamp(start_date)
    upper = pd.Timestamp(end_date)
    for source_record_index, record in enumerate(records):
        record_date = pd.to_datetime(record["date"], errors="raise")
        if lower <= record_date <= upper:
            rows.append(
                {
                    "source_date_raw": record_date,
                    "source_record_index": source_record_index,
                    "a_share_total_market_cap_yi": float(record["marketCap"]),
                }
            )
    frame = pd.DataFrame(rows).sort_values(["source_date_raw", "source_record_index"]).reset_index(drop=True)
    if frame.empty:
        raise ValueError("指定区间没有乐咕乐股总市值数据")
    values = pd.to_numeric(frame["a_share_total_market_cap_yi"], errors="raise")
    if values.isna().any() or values.le(0).any():
        raise ValueError("乐咕乐股总市值数据存在无效值")
    if not frame["source_date_raw"].between(lower, upper).all():
        raise ValueError("乐咕乐股总市值数据超出指定区间")
    frame["duplicate_count_for_date"] = (
        frame.groupby("source_date_raw")["source_date_raw"].transform("size").astype(int)
    )
    frame["is_weekend"] = frame["source_date_raw"].dt.dayofweek.ge(5)
    frame["date_mapping_status"] = "unverified"
    frame["quality_status"] = "vendor_date_unverified"
    frame.loc[frame["is_weekend"], "quality_status"] = "weekend_date_unverified"
    frame.loc[frame["duplicate_count_for_date"].gt(1), "quality_status"] = "duplicate_date_unverified"
    frame.loc[
        frame["duplicate_count_for_date"].gt(1) & frame["is_weekend"], "quality_status"
    ] = "duplicate_and_weekend_date_unverified"
    frame["quality_note"] = "未用独立交易日日历核验；不得直接与两融表按日联结。"
    frame["reporting_eligible"] = False
    return frame


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig", float_format="%.8f")
    os.replace(temporary, path)


def atomic_write_json(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def resolve_project_root(value: str | None) -> Path:
    root = Path(value).expanduser().resolve() if value else Path(__file__).resolve().parents[1]
    if not (root / "AGENTS.md").exists():
        raise FileNotFoundError(f"cannot confirm project root: {root}")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="更新乐咕乐股A股总市值历史表")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--start-date", default="2011-08-03")
    parser.add_argument("--end-date", default=date.today().isoformat())
    args = parser.parse_args()

    if pd.Timestamp(args.start_date) > pd.Timestamp(args.end_date):
        raise ValueError("--start-date 不能晚于 --end-date")
    project_root = resolve_project_root(args.project_root)
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else project_root / "artifacts" / "leverage_capitulation" / "market_cap"
    )

    session = requests.Session()
    records, token_date, retrieved_at_bj, raw_payload_sha256 = fetch_market_cap_payload(session)
    table = build_frame(records, start_date=args.start_date, end_date=args.end_date)
    table["source_name"] = SOURCE_NAME
    table["source_url"] = SOURCE_API_URL
    table["methodology_url"] = SOURCE_PAGE_URL
    table["vendor_scope"] = SOURCE_DEFINITION
    table["retrieved_at_bj"] = retrieved_at_bj
    table["raw_payload_sha256"] = raw_payload_sha256
    table["sample_status"] = SAMPLE_STATUS
    table = table[
        [
            "source_date_raw",
            "source_record_index",
            "a_share_total_market_cap_yi",
            "source_name",
            "source_url",
            "methodology_url",
            "vendor_scope",
            "retrieved_at_bj",
            "raw_payload_sha256",
            "is_weekend",
            "duplicate_count_for_date",
            "date_mapping_status",
            "quality_status",
            "quality_note",
            "reporting_eligible",
            "sample_status",
        ]
    ]
    table_path = output_dir / "a_share_total_market_cap_vendor_history.csv"
    audit_path = output_dir / "a_share_total_market_cap_audit.json"
    atomic_write_csv(table, table_path)
    audit = {
        "source_name": SOURCE_NAME,
        "source_page_url": SOURCE_PAGE_URL,
        "source_api_path": SOURCE_API_PATH,
        "source_definition": SOURCE_DEFINITION,
        "source_type": "vendor_data",
        "officially_verified": False,
        "sample_status": SAMPLE_STATUS,
        "requested_start": args.start_date,
        "requested_end": args.end_date,
        "returned_rows": len(records),
        "row_count": len(table),
        "unique_date_count": int(table["source_date_raw"].nunique()),
        "duplicate_date_count": int(
            table.loc[table["duplicate_count_for_date"].gt(1), "source_date_raw"].nunique()
        ),
        "duplicate_row_count": int(table["duplicate_count_for_date"].gt(1).sum()),
        "duplicate_excess_row_count": int(
            len(table) - table["source_date_raw"].nunique()
        ),
        "weekend_row_count": int(table["is_weekend"].sum()),
        "date_alignment_available": False,
        "date_quality_warning": (
            "保留厂商原始日期及质量标记；不得直接作为交易日序列与两融表按日联结。"
        ),
        "first_raw_date": table["source_date_raw"].min().date().isoformat(),
        "last_raw_date": table["source_date_raw"].max().date().isoformat(),
        "token_date_beijing": token_date,
        "retrieved_at_bj": retrieved_at_bj,
        "raw_payload_sha256": raw_payload_sha256,
        "a_share_total_market_cap_sha256": sha256_file(table_path),
        "updated_at_utc": utc_now(),
    }
    atomic_write_json(audit, audit_path)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
