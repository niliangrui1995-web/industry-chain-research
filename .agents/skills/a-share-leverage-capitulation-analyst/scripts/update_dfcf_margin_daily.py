from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests


DFCF_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
DFCF_REPORT = "RPTA_WEB_RZRQ_LSSH"
PAGE_SIZE = 500
MARKETS = {
    "SH": ("007", "sh_margin_y", "dfcf_sse_margin.csv"),
    "SZ": ("001", "sz_margin_y", "dfcf_szse_margin.csv"),
}
HEADERS = {
    "Referer": "https://data.eastmoney.com/rzrq/total/all.1.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
}
SAMPLE_STATUS = "dfcf_vendor_only_unverified_by_exchange"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request_json(
    session: requests.Session,
    *,
    params: dict[str, str],
    retries: int = 4,
) -> dict[str, object]:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(DFCF_URL, params=params, headers=HEADERS, timeout=30)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict) or payload.get("success") is not True:
                raise ValueError("unexpected DFCF response")
            return payload
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(min(8, 2**attempt))
    raise RuntimeError(f"DFCF request failed after {retries} attempts: {last_error}")


def fetch_market(
    market: str,
    start_date: str,
    end_date: str,
    *,
    session: requests.Session | None = None,
) -> tuple[pd.DataFrame, dict[str, int]]:
    try:
        market_code, value_column, _ = MARKETS[market]
    except KeyError as exc:
        raise ValueError(f"unsupported market: {market}") from exc

    http = session or requests.Session()
    fetched_at = utc_now()
    rows: list[dict[str, object]] = []
    page_no = 1
    expected_total: int | None = None
    expected_pages: int | None = None

    while True:
        payload = request_json(
            http,
            params={
                "reportName": DFCF_REPORT,
                "columns": "ALL",
                "source": "WEB",
                "sortColumns": "DIM_DATE",
                "sortTypes": "-1",
                "pageNumber": str(page_no),
                "pageSize": str(PAGE_SIZE),
                "filter": (
                    f'(SCDM="{market_code}")'
                    f"(DIM_DATE>='{start_date}')"
                    f"(DIM_DATE<='{end_date}')"
                ),
            },
        )
        result = payload.get("result")
        if not isinstance(result, dict):
            raise ValueError(f"DFCF {market} response has no result")
        if expected_total is None:
            expected_total = int(result.get("count", 0))
            expected_pages = int(result.get("pages", 0))
        for row in result.get("data") or []:
            rows.append(
                {
                    "date": pd.to_datetime(row["DIM_DATE"], errors="raise"),
                    value_column: float(row["RZYE"]) / 100_000_000.0,
                    "source": DFCF_URL,
                    "fetched_at_utc": fetched_at,
                }
            )
        if expected_pages is None or page_no >= expected_pages:
            break
        page_no += 1

    if expected_total is None or expected_pages is None or len(rows) != expected_total:
        raise ValueError(
            f"DFCF {market} pagination incomplete: expected={expected_total}, received={len(rows)}"
        )
    if not rows:
        raise ValueError(f"DFCF {market} returned no rows")
    frame = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    validate_market_frame(frame, value_column, market)
    if not frame["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)).all():
        raise ValueError(f"DFCF {market} returned dates outside requested range")
    return frame, {"requests": expected_pages, "rows": expected_total}


def validate_market_frame(frame: pd.DataFrame, value_column: str, market: str) -> None:
    required = {"date", value_column, "source", "fetched_at_utc"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{market} snapshot missing columns: {sorted(missing)}")
    if frame["date"].duplicated().any():
        raise ValueError(f"{market} snapshot contains duplicate dates")
    values = pd.to_numeric(frame[value_column], errors="raise")
    if values.isna().any() or values.le(0).any():
        raise ValueError(f"{market} snapshot contains invalid balances")


def load_market_snapshot(path: Path, value_column: str, market: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["date", value_column, "source", "fetched_at_utc"])
    frame = pd.read_csv(path, encoding="utf-8-sig")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    validate_market_frame(frame, value_column, market)
    return frame.sort_values("date").reset_index(drop=True)


def merge_market_snapshot(
    existing: pd.DataFrame,
    incoming: pd.DataFrame,
    value_column: str,
) -> tuple[pd.DataFrame, int]:
    if existing.empty:
        return incoming.sort_values("date").reset_index(drop=True), len(incoming)

    current = existing.set_index("date").copy()
    changed = 0
    for row in incoming.set_index("date").itertuples():
        row_date = row.Index
        new_value = float(getattr(row, value_column))
        if row_date in current.index and abs(float(current.at[row_date, value_column]) - new_value) <= 1e-8:
            continue
        current.loc[row_date, [value_column, "source", "fetched_at_utc"]] = [
            new_value,
            row.source,
            row.fetched_at_utc,
        ]
        changed += 1
    merged = current.reset_index().sort_values("date").reset_index(drop=True)
    return merged, changed


def build_merged_table(sh: pd.DataFrame, sz: pd.DataFrame) -> pd.DataFrame:
    merged = sh[["date", "sh_margin_y"]].merge(
        sz[["date", "sz_margin_y"]], on="date", how="inner", validate="one_to_one"
    )
    if merged.empty:
        raise ValueError("DFCF SH/SZ snapshots have no common dates")
    merged = merged.sort_values("date").reset_index(drop=True)
    merged["total_margin_y"] = merged["sh_margin_y"] + merged["sz_margin_y"]
    for prefix in ("sh", "sz", "total"):
        balance = f"{prefix}_margin_y"
        merged[f"{prefix}_change_y"] = merged[balance].diff()
        merged[f"{prefix}_change_pct"] = merged[balance].pct_change() * 100.0
    merged["source"] = "DFCF/东方财富Choice数据"
    merged["sample_status"] = SAMPLE_STATUS
    return merged


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
    if value:
        root = Path(value).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parents[4]
    if not (root / "AGENTS.md").exists():
        raise FileNotFoundError(f"cannot confirm project root: {root}")
    return root


def frames_equal(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    if list(left.columns) != list(right.columns) or len(left) != len(right):
        return False
    left_copy = left.copy()
    right_copy = right.copy()
    if "date" in left_copy:
        left_copy["date"] = pd.to_datetime(left_copy["date"], errors="raise")
        right_copy["date"] = pd.to_datetime(right_copy["date"], errors="raise")
    numeric_columns = left_copy.select_dtypes(include="number").columns
    left_copy[numeric_columns] = left_copy[numeric_columns].round(8)
    right_copy[numeric_columns] = right_copy[numeric_columns].round(8)
    return left_copy.equals(right_copy)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update DFCF-only SH/SZ margin balance tables")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--bootstrap-start", default="2016-01-01")
    parser.add_argument(
        "--backfill-start",
        default=None,
        help="explicit full-history fetch start; overrides the normal trailing refresh window",
    )
    parser.add_argument("--end-date", default=date.today().isoformat())
    parser.add_argument("--refresh-days", type=int, default=14)
    args = parser.parse_args()

    if args.refresh_days < 1:
        raise ValueError("--refresh-days must be positive")
    project_root = resolve_project_root(args.project_root)
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else project_root / "artifacts" / "leverage_capitulation" / "dfcf_daily"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    existing: dict[str, pd.DataFrame] = {}
    paths: dict[str, Path] = {}
    latest_dates: list[pd.Timestamp] = []
    for market, (_, value_column, filename) in MARKETS.items():
        path = output_dir / filename
        paths[market] = path
        existing[market] = load_market_snapshot(path, value_column, market)
        if not existing[market].empty:
            latest_dates.append(existing[market]["date"].max())

    if args.backfill_start:
        start_date = args.backfill_start
    elif len(latest_dates) == len(MARKETS):
        refresh_start = min(latest_dates) - timedelta(days=args.refresh_days)
        start_date = max(refresh_start, pd.Timestamp(args.bootstrap_start)).date().isoformat()
    else:
        start_date = args.bootstrap_start

    session = requests.Session()
    updated: dict[str, pd.DataFrame] = {}
    changed_rows: dict[str, int] = {}
    request_meta: dict[str, dict[str, int]] = {}
    for market, (_, value_column, _) in MARKETS.items():
        incoming, meta = fetch_market(market, start_date, args.end_date, session=session)
        updated[market], changed_rows[market] = merge_market_snapshot(
            existing[market], incoming, value_column
        )
        validate_market_frame(updated[market], value_column, market)
        request_meta[market] = meta
        if changed_rows[market] or not paths[market].exists():
            atomic_write_csv(updated[market], paths[market])

    table_path = output_dir / "dfcf_margin_balances.csv"
    old_table = (
        pd.read_csv(table_path, encoding="utf-8-sig", parse_dates=["date"])
        if table_path.exists()
        else pd.DataFrame()
    )
    table = build_merged_table(updated["SH"], updated["SZ"])
    old_latest = old_table["date"].max() if not old_table.empty else pd.NaT
    table_updated = not frames_equal(old_table, table)
    if table_updated:
        atomic_write_csv(table, table_path)

    sh_dates = set(updated["SH"]["date"])
    sz_dates = set(updated["SZ"]["date"])
    latest_common = table["date"].max()
    new_common_dates = int(table["date"].gt(old_latest).sum()) if pd.notna(old_latest) else len(table)
    audit_path = output_dir / "dfcf_margin_audit.json"
    audit = {
        "dfcf_only": True,
        "exchange_requests": 0,
        "source_name": "东方财富Choice数据",
        "source_url": DFCF_URL,
        "report_name": DFCF_REPORT,
        "market_codes": {"SH": "007", "SZ": "001"},
        "requested_start": start_date,
        "backfill_start": args.backfill_start,
        "requested_end": args.end_date,
        "network_requests": sum(meta["requests"] for meta in request_meta.values()),
        "sh_rows": len(updated["SH"]),
        "sz_rows": len(updated["SZ"]),
        "common_rows": len(table),
        "sh_latest": updated["SH"]["date"].max().date().isoformat(),
        "sz_latest": updated["SZ"]["date"].max().date().isoformat(),
        "latest_common_date": latest_common.date().isoformat(),
        "sh_only_dates": sorted(value.date().isoformat() for value in sh_dates - sz_dates),
        "sz_only_dates": sorted(value.date().isoformat() for value in sz_dates - sh_dates),
        "changed_rows": changed_rows,
        "new_common_dates": new_common_dates,
        "table_updated": table_updated,
        "sample_status": SAMPLE_STATUS,
        "vendor_warning": "DFCF vendor data only; not validated against exchange official aggregates.",
        "dfcf_sse_margin_sha256": sha256_file(paths["SH"]),
        "dfcf_szse_margin_sha256": sha256_file(paths["SZ"]),
        "dfcf_margin_balances_sha256": sha256_file(table_path),
        "updated_at_utc": utc_now(),
    }
    atomic_write_json(audit, audit_path)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
