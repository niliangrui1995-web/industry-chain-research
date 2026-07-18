from __future__ import annotations

import argparse
import hashlib
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


SSE_URL = "https://query.sse.com.cn/marketdata/tradedata/queryMargin.do"
SZSE_URL = "https://www.szse.cn/api/report/ShowReport/data"
EASTMONEY_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
EASTMONEY_REPORT = "RPTA_WEB_RZRQ_LSSH"
EASTMONEY_PAGE_SIZE = 500
EASTMONEY_MARKETS = {
    "SH": ("007", "sh_margin_y"),
    "SZ": ("001", "sz_margin_y"),
}
HEADERS = {
    "Referer": "https://www.sse.com.cn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
}
EASTMONEY_HEADERS = {
    "Referer": "https://data.eastmoney.com/rzrq/total/all.1.html",
    "User-Agent": HEADERS["User-Agent"],
}
THREAD_LOCAL = threading.local()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def http_session() -> requests.Session:
    session = getattr(THREAD_LOCAL, "session", None)
    if session is None:
        session = requests.Session()
        THREAD_LOCAL.session = session
    return session


def request_json(url: str, *, params: dict[str, str], headers: dict[str, str], retries: int = 4) -> object:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = http_session().get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(min(8, 2**attempt))
    raise RuntimeError(f"request failed after {retries} attempts: {last_error}")


def fetch_sse(start_date: str, end_date: str) -> pd.DataFrame:
    common = {
        "isPagination": "true",
        "beginDate": start_date.replace("-", ""),
        "endDate": end_date.replace("-", ""),
        "tabType": "",
        "stockCode": "",
        "pageHelp.pageSize": "2000",
        "pageHelp.cacheSize": "1",
        "pageHelp.endPage": "20",
    }
    rows: list[dict[str, object]] = []
    page_no = 1
    expected_total: int | None = None
    while True:
        payload = request_json(
            SSE_URL,
            params={
                **common,
                "pageHelp.pageNo": str(page_no),
                "pageHelp.beginPage": str(page_no),
            },
            headers=HEADERS,
        )
        if not isinstance(payload, dict):
            raise ValueError("unexpected SSE response type")
        page_rows = payload.get("result", [])
        page = payload.get("pageHelp", {})
        if expected_total is None:
            expected_total = int(page.get("total", len(page_rows)))
        for row in page_rows:
            rows.append(
                {
                    "date": pd.to_datetime(str(row["opDate"]), format="%Y%m%d"),
                    "sh_margin_y": float(row["rzye"]) / 100_000_000.0,
                }
            )
        if not page_rows or len(rows) >= expected_total or page_no >= int(page.get("pageCount", page_no)):
            break
        page_no += 1
    frame = pd.DataFrame(rows).drop_duplicates("date", keep="last").sort_values("date")
    if expected_total is None or len(frame) != expected_total:
        raise ValueError(f"SSE pagination incomplete: expected={expected_total}, received={len(frame)}")
    return frame.reset_index(drop=True)


def fetch_eastmoney_market(
    market: str,
    start_date: str,
    end_date: str,
) -> tuple[pd.DataFrame, dict[str, int]]:
    try:
        market_code, value_column = EASTMONEY_MARKETS[market]
    except KeyError as exc:
        raise ValueError(f"unsupported Eastmoney market: {market}") from exc
    rows: list[dict[str, object]] = []
    page_no = 1
    expected_total: int | None = None
    expected_pages: int | None = None
    fetched_at = utc_now()
    while True:
        payload = request_json(
            EASTMONEY_URL,
            params={
                "reportName": EASTMONEY_REPORT,
                "columns": "ALL",
                "source": "WEB",
                "sortColumns": "DIM_DATE",
                "sortTypes": "-1",
                "pageNumber": str(page_no),
                "pageSize": str(EASTMONEY_PAGE_SIZE),
                "filter": (
                    f'(SCDM="{market_code}")'
                    f"(DIM_DATE>='{start_date}')"
                    f"(DIM_DATE<='{end_date}')"
                ),
            },
            headers=EASTMONEY_HEADERS,
        )
        if not isinstance(payload, dict) or payload.get("success") is not True:
            raise ValueError(f"unexpected Eastmoney {market} response")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise ValueError(f"Eastmoney {market} response has no result")
        if expected_total is None:
            expected_total = int(result.get("count", 0))
            expected_pages = int(result.get("pages", 0))
        page_rows = result.get("data") or []
        for row in page_rows:
            rows.append(
                {
                    "date": pd.to_datetime(row["DIM_DATE"], errors="raise"),
                    value_column: float(row["RZYE"]) / 100_000_000.0,
                    "source": EASTMONEY_URL,
                    "fetched_at_utc": fetched_at,
                }
            )
        print(
            f"eastmoney_{market.lower()}_page={page_no}/{expected_pages} "
            f"accumulated={len(rows)}/{expected_total}",
            flush=True,
        )
        if expected_pages is None or page_no >= expected_pages:
            break
        page_no += 1
    frame = pd.DataFrame(rows)
    if expected_total is None or expected_pages is None or len(frame) != expected_total:
        raise ValueError(
            f"Eastmoney {market} pagination incomplete: "
            f"expected={expected_total}, received={len(frame)}"
        )
    if frame.empty:
        raise ValueError(f"Eastmoney {market} returned no rows")
    if frame["date"].duplicated().any():
        raise ValueError(f"Eastmoney {market} snapshot contains duplicate dates")
    if frame[value_column].isna().any() or frame[value_column].le(0).any():
        raise ValueError(f"Eastmoney {market} snapshot contains invalid balances")
    if not frame["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)).all():
        raise ValueError(f"Eastmoney {market} returned dates outside the requested range")
    frame = frame.sort_values("date").reset_index(drop=True)
    return frame, {"requests": expected_pages, "rows": expected_total}


def load_official_szse_cache(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["date", "sz_margin_y", "source", "fetched_at_utc"])
    frame = pd.read_csv(path)
    required = {"date", "sz_margin_y", "source", "fetched_at_utc"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"existing SZSE snapshot missing columns: {sorted(missing)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    if frame["date"].duplicated().any():
        raise ValueError("official SZSE cache contains duplicate dates")
    if frame["sz_margin_y"].isna().any() or frame["sz_margin_y"].le(0).any():
        raise ValueError("official SZSE cache contains invalid balances")
    return frame.sort_values("date").reset_index(drop=True)


def load_eastmoney_snapshot(
    path: Path,
    market: str,
    start_date: str,
    end_date: str,
) -> tuple[pd.DataFrame, dict[str, int]]:
    if not path.exists():
        raise FileNotFoundError(f"Eastmoney snapshot not found: {path}")
    try:
        _, value_column = EASTMONEY_MARKETS[market]
    except KeyError as exc:
        raise ValueError(f"unsupported Eastmoney market: {market}") from exc
    frame = pd.read_csv(path)
    required = {"date", value_column, "source", "fetched_at_utc"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Eastmoney {market} snapshot missing columns: {sorted(missing)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame[value_column] = pd.to_numeric(frame[value_column], errors="raise")
    if frame["date"].duplicated().any():
        raise ValueError(f"Eastmoney {market} snapshot contains duplicate dates")
    if frame[value_column].isna().any() or frame[value_column].le(0).any():
        raise ValueError(f"Eastmoney {market} snapshot contains invalid balances")
    if not frame["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)).all():
        raise ValueError(f"Eastmoney {market} snapshot contains dates outside the requested range")
    frame = frame.sort_values("date").reset_index(drop=True)
    pages = (len(frame) + EASTMONEY_PAGE_SIZE - 1) // EASTMONEY_PAGE_SIZE
    return frame, {"requests": pages, "rows": len(frame)}


def load_official_sse_snapshot(path: Path, start_date: str, end_date: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"official SSE snapshot not found: {path}")
    frame = pd.read_csv(path)
    required = {"date", "sh_margin_y"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"official SSE snapshot missing columns: {sorted(missing)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame["sh_margin_y"] = pd.to_numeric(frame["sh_margin_y"], errors="raise")
    if frame["date"].duplicated().any():
        raise ValueError("official SSE snapshot contains duplicate dates")
    if frame["sh_margin_y"].isna().any() or frame["sh_margin_y"].le(0).any():
        raise ValueError("official SSE snapshot contains invalid balances")
    frame = frame.loc[
        frame["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    ].copy()
    if frame.empty:
        raise ValueError("official SSE snapshot has no rows in the requested range")
    return frame.sort_values("date").reset_index(drop=True)


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig")
    temporary.replace(path)


def compare_official_szse_cache(
    eastmoney_szse: pd.DataFrame,
    official_cache: pd.DataFrame,
) -> dict[str, object]:
    if official_cache.empty:
        return {
            "official_szse_checks": 0,
            "official_szse_mismatches_at_0_01_yi_precision": 0,
            "official_szse_max_abs_error_y": None,
        }
    compared = official_cache[["date", "sz_margin_y"]].merge(
        eastmoney_szse[["date", "sz_margin_y"]],
        on="date",
        how="inner",
        suffixes=("_official", "_eastmoney"),
        validate="one_to_one",
    )
    compared["abs_error_y"] = (
        compared["sz_margin_y_official"] - compared["sz_margin_y_eastmoney"]
    ).abs()
    return {
        "official_szse_checks": int(len(compared)),
        "official_szse_mismatches_at_0_01_yi_precision": int(
            compared["abs_error_y"].gt(0.01000001).sum()
        ),
        "official_szse_max_abs_error_y": (
            None if compared.empty else float(compared["abs_error_y"].max())
        ),
    }


def compare_history(
    local_path: Path,
    verified: pd.DataFrame,
    discrepancy_path: Path,
) -> dict[str, object]:
    local = pd.read_csv(local_path)
    required = {"date", "sh_margin_y", "sz_margin_y", "total_margin_y"}
    missing = required - set(local.columns)
    if missing:
        raise ValueError(f"local margin CSV missing columns: {sorted(missing)}")
    local["date"] = pd.to_datetime(local["date"], errors="raise")
    verified_start = verified["date"].min()
    verified_end = verified["date"].max()
    local = local.loc[local["date"].between(verified_start, verified_end)].copy()
    local_duplicate_dates = int(local["date"].duplicated().sum())
    local = local.drop_duplicates("date", keep="last")
    compared = verified.merge(
        local[["date", "sh_margin_y", "sz_margin_y", "total_margin_y"]],
        on="date",
        how="outer",
        suffixes=("_verified", "_local"),
        indicator=True,
    )
    compared["sh_abs_error_y"] = (compared["sh_margin_y_verified"] - compared["sh_margin_y_local"]).abs()
    compared["sz_abs_error_y"] = (compared["sz_margin_y_verified"] - compared["sz_margin_y_local"]).abs()
    compared["total_abs_error_y"] = (
        compared["total_margin_y_verified"] - compared["total_margin_y_local"]
    ).abs()
    compared["sh_matches"] = compared["sh_abs_error_y"].le(0.00000001)
    compared["sz_matches_published_precision"] = compared["sz_abs_error_y"].le(0.01000001)
    compared["total_matches_published_precision"] = compared["total_abs_error_y"].le(0.01000002)
    discrepancy_mask = (
        compared["_merge"].ne("both")
        | ~compared["sh_matches"]
        | ~compared["sz_matches_published_precision"]
        | ~compared["total_matches_published_precision"]
    )
    discrepancies = compared.loc[discrepancy_mask].sort_values("date")
    write_csv(discrepancies, discrepancy_path)
    both = compared["_merge"].eq("both")
    return {
        "verified_rows": int(len(verified)),
        "verified_start": verified["date"].min().strftime("%Y-%m-%d"),
        "verified_end": verified["date"].max().strftime("%Y-%m-%d"),
        "local_rows": int(len(local)),
        "local_start": local["date"].min().strftime("%Y-%m-%d"),
        "local_end": local["date"].max().strftime("%Y-%m-%d"),
        "local_duplicate_dates": local_duplicate_dates,
        "verified_missing_in_local": int(compared["_merge"].eq("left_only").sum()),
        "local_absent_from_verified": int(compared["_merge"].eq("right_only").sum()),
        "sse_mismatches": int((both & ~compared["sh_matches"]).sum()),
        "szse_mismatches_at_0_01_yi_precision": int(
            (both & ~compared["sz_matches_published_precision"]).sum()
        ),
        "total_mismatches_at_published_precision": int(
            (both & ~compared["total_matches_published_precision"]).sum()
        ),
        "discrepancy_rows": int(len(discrepancies)),
        "max_sse_abs_error_y": float(compared.loc[both, "sh_abs_error_y"].max()),
        "max_szse_abs_error_y": float(compared.loc[both, "sz_abs_error_y"].max()),
        "max_total_abs_error_y": float(compared.loc[both, "total_abs_error_y"].max()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Eastmoney margin balances and validate them against exchange data"
    )
    parser.add_argument(
        "--local-csv",
        type=Path,
        help="Optional explicit comparison file; no legacy local-history fallback is used",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start-date", default="2016-01-01")
    parser.add_argument("--end-date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    parser.add_argument("--min-official-szse-checks", type=int, default=100)
    parser.add_argument(
        "--reuse-snapshots",
        action="store_true",
        help="Re-audit existing Eastmoney and SSE snapshots without network downloads",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.min_official_szse_checks < 1:
        raise ValueError("--min-official-szse-checks must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    eastmoney_sse_path = args.output_dir / "eastmoney_sse_margin.csv"
    eastmoney_szse_path = args.output_dir / "eastmoney_szse_margin.csv"
    official_sse_path = args.output_dir / "official_sse_margin.csv"
    if args.reuse_snapshots:
        eastmoney_sse, eastmoney_sse_meta = load_eastmoney_snapshot(
            eastmoney_sse_path, "SH", args.start_date, args.end_date
        )
        eastmoney_szse, eastmoney_szse_meta = load_eastmoney_snapshot(
            eastmoney_szse_path, "SZ", args.start_date, args.end_date
        )
        sse = load_official_sse_snapshot(
            official_sse_path, args.start_date, args.end_date
        )
    else:
        eastmoney_sse, eastmoney_sse_meta = fetch_eastmoney_market(
            "SH", args.start_date, args.end_date
        )
        eastmoney_szse, eastmoney_szse_meta = fetch_eastmoney_market(
            "SZ", args.start_date, args.end_date
        )
        write_csv(eastmoney_sse, eastmoney_sse_path)
        write_csv(eastmoney_szse, eastmoney_szse_path)
        sse = fetch_sse(args.start_date, args.end_date)
        sse_snapshot = sse.assign(source=SSE_URL, fetched_at_utc=utc_now())
        write_csv(sse_snapshot, official_sse_path)

    effective_end = min(
        sse["date"].max(),
        eastmoney_sse["date"].max(),
        eastmoney_szse["date"].max(),
    )
    official_sse_target = sse.loc[sse["date"].le(effective_end)].copy()
    eastmoney_sse_target = eastmoney_sse.loc[
        eastmoney_sse["date"].le(effective_end), ["date", "sh_margin_y"]
    ].copy()
    eastmoney_szse_target = eastmoney_szse.loc[
        eastmoney_szse["date"].le(effective_end), ["date", "sz_margin_y"]
    ].copy()
    expected_dates = set(official_sse_target["date"])
    sse_date_set_match = set(eastmoney_sse_target["date"]) == expected_dates
    szse_date_set_match = set(eastmoney_szse_target["date"]) == expected_dates

    sse_compared = official_sse_target[["date", "sh_margin_y"]].merge(
        eastmoney_sse_target,
        on="date",
        how="inner",
        suffixes=("_official", "_eastmoney"),
        validate="one_to_one",
    )
    sse_compared["abs_error_y"] = (
        sse_compared["sh_margin_y_official"] - sse_compared["sh_margin_y_eastmoney"]
    ).abs()
    official_szse_cache = load_official_szse_cache(
        args.output_dir / "official_szse_margin.csv"
    )
    official_szse_checks = compare_official_szse_cache(
        eastmoney_szse_target, official_szse_cache
    )

    verified = official_sse_target[["date", "sh_margin_y"]].merge(
        eastmoney_szse_target,
        on="date",
        how="inner",
        validate="one_to_one",
    )
    if verified[["sh_margin_y", "sz_margin_y"]].isna().any().any():
        raise ValueError("verified margin snapshot contains null balances")
    if verified["date"].duplicated().any():
        raise ValueError("verified margin snapshot contains duplicate dates")
    if verified[["sh_margin_y", "sz_margin_y"]].le(0).any().any():
        raise ValueError("verified margin snapshot contains non-positive balances")
    verified["total_margin_y"] = verified["sh_margin_y"] + verified["sz_margin_y"]
    verified_path = args.output_dir / "verified_margin_balances.csv"
    write_csv(verified, verified_path)
    discrepancy_path = args.output_dir / "margin_discrepancies.csv"
    audit: dict[str, object] = {
        "verified_rows": int(len(verified)),
        "verified_start": verified["date"].min().strftime("%Y-%m-%d"),
        "verified_end": verified["date"].max().strftime("%Y-%m-%d"),
        "local_comparison_status": "not_requested",
        "local_comparison_csv": None,
        "discrepancy_rows": 0,
    }
    if args.local_csv is not None:
        audit.update(compare_history(args.local_csv, verified, discrepancy_path))
        audit["local_comparison_status"] = "completed"
        audit["local_comparison_csv"] = str(args.local_csv.resolve())
    else:
        write_csv(pd.DataFrame(columns=["date", "reason"]), discrepancy_path)
    audit.update(
        {
            "requested_start_date": args.start_date,
            "requested_end_date": args.end_date,
            "effective_end_date": effective_end.strftime("%Y-%m-%d"),
            "eastmoney_sse_latest": eastmoney_sse["date"].max().strftime("%Y-%m-%d"),
            "eastmoney_szse_latest": eastmoney_szse["date"].max().strftime("%Y-%m-%d"),
            "eastmoney_sse_rows": int(len(eastmoney_sse)),
            "eastmoney_szse_rows": int(len(eastmoney_szse)),
            "eastmoney_sse_requests": eastmoney_sse_meta["requests"],
            "eastmoney_szse_requests": eastmoney_szse_meta["requests"],
            "eastmoney_total_requests": (
                eastmoney_sse_meta["requests"] + eastmoney_szse_meta["requests"]
            ),
            "snapshot_mode": "reuse" if args.reuse_snapshots else "network_refresh",
            "eastmoney_network_requests_this_run": (
                0
                if args.reuse_snapshots
                else eastmoney_sse_meta["requests"] + eastmoney_szse_meta["requests"]
            ),
            "official_sse_rows": int(len(sse)),
            "verified_calendar_rows": int(len(official_sse_target)),
            "eastmoney_sse_date_set_match": sse_date_set_match,
            "eastmoney_szse_date_set_match": szse_date_set_match,
            "official_sse_mismatches": int(sse_compared["abs_error_y"].gt(0.00000001).sum()),
            "official_sse_max_abs_error_y": float(sse_compared["abs_error_y"].max()),
            "official_szse_cache_rows": int(len(official_szse_cache)),
            "minimum_required_official_szse_checks": args.min_official_szse_checks,
            **official_szse_checks,
            "verified_duplicate_dates": int(verified["date"].duplicated().sum()),
            "verified_null_balance_cells": int(
                verified[["sh_margin_y", "sz_margin_y", "total_margin_y"]].isna().sum().sum()
            ),
            "eastmoney_source": EASTMONEY_URL,
            "eastmoney_report": EASTMONEY_REPORT,
            "official_sse_source": SSE_URL,
            "official_szse_source": SZSE_URL,
            "official_szse_validation_scope": "cached_overlap_only",
            "official_sse_unit_precision": "yuan",
            "official_szse_public_display_precision": "0.01 yi yuan",
            "legacy_root_history_fallback": "disabled",
            "eastmoney_sse_margin_sha256": sha256_file(eastmoney_sse_path),
            "eastmoney_szse_margin_sha256": sha256_file(eastmoney_szse_path),
            "verified_margin_balances_sha256": sha256_file(verified_path),
            "audited_at_utc": utc_now(),
        }
    )
    audit["verified_snapshot_complete"] = bool(
        audit["verified_rows"] == audit["verified_calendar_rows"]
        and audit["eastmoney_sse_date_set_match"]
        and audit["eastmoney_szse_date_set_match"]
        and audit["official_sse_mismatches"] == 0
        and audit["official_szse_checks"] >= audit["minimum_required_official_szse_checks"]
        and audit["official_szse_mismatches_at_0_01_yi_precision"] == 0
        and audit["verified_duplicate_dates"] == 0
        and audit["verified_null_balance_cells"] == 0
        and audit["verified_start"] >= "2016-01-01"
    )
    (args.output_dir / "margin_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2), flush=True)
    return 0 if audit["verified_snapshot_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
