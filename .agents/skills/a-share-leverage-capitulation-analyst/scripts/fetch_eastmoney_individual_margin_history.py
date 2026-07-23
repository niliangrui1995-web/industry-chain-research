from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, NamedTuple

import pandas as pd
import requests


DFCF_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
DETAIL_REPORT = "RPTA_WEB_RZRQ_GGMX"
CALENDAR_REPORT = "RPTA_WEB_RZRQ_LSSH"
PAGE_SIZE = 500
ETF_MARKET_CODES = {"069001001", "069001002"}
STOCK_MARKET_PREFIXES = ("069001001", "069001002")
BEIJING_MARKET_CODE = "069001017"
SAMPLE_STATUS = "dfcf_vendor_individual_detail_unverified_by_exchange"
HEADERS = {
    "Referer": "https://data.eastmoney.com/rzrq/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
}
DETAIL_COLUMNS = (
    "DATE,MARKET,SCODE,SECNAME,RZYE,RQYL,RZRQYE,RQYE,RQMCL,RZMRE,"
    "RZCHE,RZJME,RQCHL,SPJ,ZDF,TRADE_MARKET_CODE,TRADE_MARKET,SECUCODE"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


class NetworkStats:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.attempts = 0
        self.successes = 0
        self.retries = 0

    def record_attempt(self) -> None:
        with self._lock:
            self.attempts += 1

    def record_success(self) -> None:
        with self._lock:
            self.successes += 1

    def record_retry(self) -> None:
        with self._lock:
            self.retries += 1

    def as_dict(self) -> dict[str, int]:
        with self._lock:
            return {
                "attempts": self.attempts,
                "successes": self.successes,
                "retries": self.retries,
            }


_thread_local = threading.local()


class VendorNoDataError(RuntimeError):
    pass


def thread_session() -> requests.Session:
    session = getattr(_thread_local, "session", None)
    if session is None:
        session = requests.Session()
        _thread_local.session = session
    return session


def request_json(
    *,
    params: dict[str, str],
    stats: NetworkStats | None = None,
    retries: int = 6,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries):
        if stats:
            stats.record_attempt()
        try:
            response = thread_session().get(
                DFCF_URL,
                params=params,
                headers=HEADERS,
                timeout=45,
            )
            response.raise_for_status()
            payload = response.json()
            if (
                isinstance(payload, dict)
                and payload.get("success") is False
                and int(payload.get("code") or 0) == 9201
            ):
                raise VendorNoDataError(str(payload.get("message") or "DFCF returned no data"))
            if not isinstance(payload, dict) or payload.get("success") is not True:
                raise ValueError("unexpected DFCF response")
            if stats:
                stats.record_success()
            return payload
        except VendorNoDataError:
            raise
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                if stats:
                    stats.record_retry()
                time.sleep(min(12.0, (2**attempt) + 0.25 * (attempt + 1)))
    raise RuntimeError(f"DFCF request failed after {retries} attempts: {last_error}")


def result_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = payload.get("result")
    if not isinstance(result, dict):
        raise ValueError("DFCF response has no result object")
    return result


def fetch_trade_dates(
    start_date: str,
    end_date: str,
    *,
    stats: NetworkStats | None = None,
) -> tuple[list[str], int]:
    dates: list[str] = []
    page_number = 1
    expected_count: int | None = None
    expected_pages: int | None = None
    while True:
        result = result_from_payload(
            request_json(
                params={
                    "reportName": CALENDAR_REPORT,
                    "columns": "DIM_DATE",
                    "source": "WEB",
                    "client": "WEB",
                    "sortColumns": "DIM_DATE",
                    "sortTypes": "-1",
                    "pageNumber": str(page_number),
                    "pageSize": str(PAGE_SIZE),
                    "filter": (
                        '(SCDM="007")'
                        f"(DIM_DATE>='{start_date}')"
                        f"(DIM_DATE<='{end_date}')"
                    ),
                },
                stats=stats,
            )
        )
        if expected_count is None:
            expected_count = int(result.get("count", 0))
            expected_pages = int(result.get("pages", 0))
        dates.extend(str(row["DIM_DATE"])[:10] for row in result.get("data") or [])
        if expected_pages is None or page_number >= expected_pages:
            break
        page_number += 1

    unique_dates = sorted(set(dates))
    if expected_count is None or len(dates) != expected_count:
        raise ValueError(
            f"DFCF calendar pagination incomplete: expected={expected_count}, received={len(dates)}"
        )
    if len(unique_dates) != len(dates):
        raise ValueError("DFCF calendar contains duplicate dates")
    if not unique_dates:
        raise ValueError("DFCF calendar returned no dates")
    if unique_dates[0] < start_date or unique_dates[-1] > end_date:
        raise ValueError("DFCF calendar returned a date outside the requested range")
    return unique_dates, page_number


def classify_instrument(trade_market_code: str, secu_code: str) -> str:
    if trade_market_code in ETF_MARKET_CODES:
        return "ETF"
    if trade_market_code == BEIJING_MARKET_CODE:
        return "A_SHARE_STOCK"
    if trade_market_code.startswith(STOCK_MARKET_PREFIXES):
        return "A_SHARE_STOCK"
    if secu_code.endswith(".BJ"):
        return "A_SHARE_STOCK"
    return "UNKNOWN"


def optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


class DateFetch(NamedTuple):
    trade_date: str
    expected_rows: int
    pages: int
    rows: list[tuple[Any, ...]]


def normalize_detail_row(row: dict[str, Any], expected_date: str) -> tuple[Any, ...]:
    trade_date = str(row.get("DATE", ""))[:10]
    secu_code = str(row.get("SECUCODE") or "")
    stock_code = str(row.get("SCODE") or "")
    financing_balance = optional_int(row.get("RZYE"))
    if trade_date != expected_date:
        raise ValueError(f"detail row date mismatch: expected={expected_date}, got={trade_date}")
    if not secu_code or not stock_code:
        raise ValueError(f"detail row is missing a security code on {expected_date}")
    if financing_balance is None or financing_balance < 0:
        raise ValueError(f"invalid financing balance for {secu_code} on {expected_date}")

    trade_market_code = str(row.get("TRADE_MARKET_CODE") or "")
    return (
        trade_date,
        secu_code,
        stock_code,
        str(row.get("SECNAME") or ""),
        str(row.get("MARKET") or ""),
        trade_market_code,
        str(row.get("TRADE_MARKET") or ""),
        classify_instrument(trade_market_code, secu_code),
        financing_balance,
        optional_int(row.get("RZMRE")),
        optional_int(row.get("RZCHE")),
        optional_int(row.get("RZJME")),
        optional_int(row.get("RQYE")),
        optional_int(row.get("RQYL")),
        optional_int(row.get("RQMCL")),
        optional_int(row.get("RQCHL")),
        optional_int(row.get("RZRQYE")),
        optional_float(row.get("SPJ")),
        optional_float(row.get("ZDF")),
    )


def fetch_trade_date(
    trade_date: str,
    *,
    stats: NetworkStats | None = None,
) -> DateFetch:
    rows: list[dict[str, Any]] = []
    page_number = 1
    expected_rows: int | None = None
    expected_pages: int | None = None
    while True:
        result = result_from_payload(
            request_json(
                params={
                    "reportName": DETAIL_REPORT,
                    "columns": DETAIL_COLUMNS,
                    "source": "WEB",
                    "client": "WEB",
                    "sortColumns": "SCODE",
                    "sortTypes": "1",
                    "pageNumber": str(page_number),
                    "pageSize": str(PAGE_SIZE),
                    "filter": f"(DATE='{trade_date}')",
                },
                stats=stats,
            )
        )
        if expected_rows is None:
            expected_rows = int(result.get("count", 0))
            expected_pages = int(result.get("pages", 0))
        rows.extend(result.get("data") or [])
        if expected_pages is None or page_number >= expected_pages:
            break
        page_number += 1

    if expected_rows is None or expected_pages is None:
        raise ValueError(f"missing pagination metadata for {trade_date}")
    if expected_rows <= 0:
        raise ValueError(f"DFCF returned no individual margin rows for {trade_date}")
    if len(rows) != expected_rows:
        raise ValueError(
            f"incomplete detail pagination for {trade_date}: "
            f"expected={expected_rows}, received={len(rows)}"
        )
    normalized = [normalize_detail_row(row, trade_date) for row in rows]
    keys = {(row[0], row[1]) for row in normalized}
    if len(keys) != len(normalized):
        raise ValueError(f"duplicate security/date rows returned for {trade_date}")
    return DateFetch(
        trade_date=trade_date,
        expected_rows=expected_rows,
        pages=expected_pages,
        rows=normalized,
    )


SCHEMA = """
CREATE TABLE IF NOT EXISTS margin_daily (
    trade_date TEXT NOT NULL,
    secu_code TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    security_name TEXT NOT NULL,
    vendor_market TEXT NOT NULL,
    trade_market_code TEXT NOT NULL,
    trade_market TEXT NOT NULL,
    instrument_type TEXT NOT NULL,
    financing_balance_yuan INTEGER NOT NULL,
    financing_buy_yuan INTEGER,
    financing_repay_yuan INTEGER,
    financing_net_buy_yuan INTEGER,
    securities_lending_balance_yuan INTEGER,
    securities_lending_balance_shares INTEGER,
    securities_lending_sell_shares INTEGER,
    securities_lending_repay_shares INTEGER,
    margin_balance_yuan INTEGER,
    close_price REAL,
    change_pct REAL,
    PRIMARY KEY (trade_date, secu_code)
);
CREATE TABLE IF NOT EXISTS fetch_status (
    trade_date TEXT PRIMARY KEY,
    expected_rows INTEGER NOT NULL,
    received_rows INTEGER NOT NULL,
    pages INTEGER NOT NULL,
    status TEXT NOT NULL,
    fetched_at_utc TEXT NOT NULL,
    error TEXT
);
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_margin_daily_security_date
    ON margin_daily (secu_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_margin_daily_type_date
    ON margin_daily (instrument_type, trade_date);
CREATE VIEW IF NOT EXISTS a_share_stock_margin_daily AS
SELECT *
FROM margin_daily
WHERE instrument_type = 'A_SHARE_STOCK';
"""


INSERT_SQL = """
INSERT INTO margin_daily (
    trade_date, secu_code, stock_code, security_name, vendor_market,
    trade_market_code, trade_market, instrument_type,
    financing_balance_yuan, financing_buy_yuan, financing_repay_yuan,
    financing_net_buy_yuan, securities_lending_balance_yuan,
    securities_lending_balance_shares, securities_lending_sell_shares,
    securities_lending_repay_shares, margin_balance_yuan, close_price, change_pct
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def open_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute("PRAGMA temp_store=MEMORY")
    connection.executescript(SCHEMA)
    return connection


def store_date_fetch(
    connection: sqlite3.Connection,
    fetched: DateFetch,
    *,
    fetched_at_utc: str | None = None,
) -> None:
    timestamp = fetched_at_utc or utc_now()
    with connection:
        connection.execute(
            "DELETE FROM margin_daily WHERE trade_date = ?",
            (fetched.trade_date,),
        )
        connection.executemany(INSERT_SQL, fetched.rows)
        connection.execute(
            """
            INSERT INTO fetch_status (
                trade_date, expected_rows, received_rows, pages,
                status, fetched_at_utc, error
            ) VALUES (?, ?, ?, ?, 'complete', ?, NULL)
            ON CONFLICT(trade_date) DO UPDATE SET
                expected_rows = excluded.expected_rows,
                received_rows = excluded.received_rows,
                pages = excluded.pages,
                status = excluded.status,
                fetched_at_utc = excluded.fetched_at_utc,
                error = NULL
            """,
            (
                fetched.trade_date,
                fetched.expected_rows,
                len(fetched.rows),
                fetched.pages,
                timestamp,
            ),
        )


def store_failure(
    connection: sqlite3.Connection,
    trade_date: str,
    error: Exception,
) -> None:
    with connection:
        connection.execute(
            """
            INSERT INTO fetch_status (
                trade_date, expected_rows, received_rows, pages,
                status, fetched_at_utc, error
            ) VALUES (?, 0, 0, 0, 'failed', ?, ?)
            ON CONFLICT(trade_date) DO UPDATE SET
                status = excluded.status,
                fetched_at_utc = excluded.fetched_at_utc,
                error = excluded.error
            """,
            (trade_date, utc_now(), str(error)[:1000]),
        )


def store_vendor_gap(
    connection: sqlite3.Connection,
    trade_date: str,
    error: VendorNoDataError,
) -> None:
    with connection:
        connection.execute(
            """
            INSERT INTO fetch_status (
                trade_date, expected_rows, received_rows, pages,
                status, fetched_at_utc, error
            ) VALUES (?, 0, 0, 0, 'vendor_no_data', ?, ?)
            ON CONFLICT(trade_date) DO UPDATE SET
                expected_rows = 0,
                received_rows = 0,
                pages = 0,
                status = excluded.status,
                fetched_at_utc = excluded.fetched_at_utc,
                error = excluded.error
            """,
            (trade_date, utc_now(), str(error)[:1000]),
        )


def completed_dates(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            "SELECT trade_date FROM fetch_status WHERE status = 'complete'"
        )
    }


def settled_dates(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            """
            SELECT trade_date
            FROM fetch_status
            WHERE status IN ('complete', 'vendor_no_data')
            """
        )
    }


def scalar(connection: sqlite3.Connection, query: str) -> int:
    value = connection.execute(query).fetchone()[0]
    return int(value or 0)


def summarize(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "median": None, "max": None}
    return {
        "min": min(values),
        "median": statistics.median(values),
        "max": max(values),
    }


def reconcile_aggregate(
    connection: sqlite3.Connection,
    aggregate_csv: Path,
) -> dict[str, Any]:
    if not aggregate_csv.exists():
        return {
            "available": False,
            "aggregate_csv": str(aggregate_csv),
            "warning": "DFCF aggregate table was not found; no market-total reconciliation ran.",
        }

    aggregate = pd.read_csv(aggregate_csv, encoding="utf-8-sig")
    aggregate["date"] = pd.to_datetime(aggregate["date"], errors="raise").dt.strftime("%Y-%m-%d")
    detail_rows = connection.execute(
        """
        SELECT
            trade_date,
            CASE
                WHEN secu_code LIKE '%.SH' THEN 'SH'
                WHEN secu_code LIKE '%.SZ' THEN 'SZ'
                WHEN secu_code LIKE '%.BJ' THEN 'BJ'
                ELSE 'UNKNOWN'
            END AS exchange_code,
            SUM(financing_balance_yuan) AS detail_balance_yuan
        FROM margin_daily
        GROUP BY trade_date, exchange_code
        """
    ).fetchall()
    detail = pd.DataFrame(
        detail_rows,
        columns=["date", "exchange", "detail_balance_yuan"],
    )

    markets: dict[str, Any] = {}
    all_exact = True
    for exchange, aggregate_column in (("SH", "sh_margin_y"), ("SZ", "sz_margin_y")):
        market_detail = detail.loc[
            detail["exchange"].eq(exchange),
            ["date", "detail_balance_yuan"],
        ]
        merged = aggregate[["date", aggregate_column]].merge(
            market_detail,
            on="date",
            how="inner",
            validate="one_to_one",
        )
        merged["aggregate_balance_yuan"] = (
            pd.to_numeric(merged[aggregate_column], errors="raise") * 100_000_000.0
        )
        merged["difference_yuan"] = (
            merged["detail_balance_yuan"] - merged["aggregate_balance_yuan"]
        )
        merged["coverage_ratio"] = (
            merged["detail_balance_yuan"] / merged["aggregate_balance_yuan"]
        )
        exact = bool(merged["difference_yuan"].abs().le(1.0).all()) if not merged.empty else False
        all_exact = all_exact and exact
        latest = merged.sort_values("date").iloc[-1] if not merged.empty else None
        markets[exchange] = {
            "dates_compared": len(merged),
            "exact_reconciliation_passed": exact,
            "coverage_ratio": summarize(merged["coverage_ratio"].astype(float).tolist()),
            "latest_date": None if latest is None else str(latest["date"]),
            "latest_detail_balance_yuan": (
                None if latest is None else int(latest["detail_balance_yuan"])
            ),
            "latest_aggregate_balance_yuan": (
                None if latest is None else round(float(latest["aggregate_balance_yuan"]))
            ),
            "latest_difference_yuan": (
                None if latest is None else round(float(latest["difference_yuan"]))
            ),
        }
    return {
        "available": True,
        "aggregate_csv": str(aggregate_csv),
        "exact_reconciliation_passed": all_exact,
        "markets": markets,
        "interpretation": (
            "Pagination completeness only proves the DFCF detail endpoint was fully read. "
            "A non-zero aggregate difference means the detail table must not reconstruct "
            "or replace the SH/SZ market-total balance series."
        ),
    }


LATEST_COLUMNS = [
    "trade_date",
    "secu_code",
    "stock_code",
    "security_name",
    "trade_market",
    "financing_balance_yuan",
    "financing_buy_yuan",
    "financing_repay_yuan",
    "financing_net_buy_yuan",
    "securities_lending_balance_yuan",
    "margin_balance_yuan",
]


def export_latest_stocks(
    connection: sqlite3.Connection,
    path: Path,
) -> tuple[str, int]:
    latest_date = connection.execute(
        "SELECT MAX(trade_date) FROM a_share_stock_margin_daily"
    ).fetchone()[0]
    if not latest_date:
        raise ValueError("no A-share stock rows are available for latest export")
    rows = connection.execute(
        f"""
        SELECT {", ".join(LATEST_COLUMNS)}
        FROM a_share_stock_margin_daily
        WHERE trade_date = ?
        ORDER BY secu_code
        """,
        (latest_date,),
    ).fetchall()
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(LATEST_COLUMNS)
        writer.writerows(rows)
    os.replace(temporary, path)
    return str(latest_date), len(rows)


def build_audit(
    connection: sqlite3.Connection,
    *,
    database_path: Path,
    calendar_dates: list[str],
    aggregate_csv: Path,
    stats: NetworkStats,
    requested_start: str,
    requested_end: str,
    calendar_requests: int,
    latest_export_path: Path,
) -> dict[str, Any]:
    status_rows = {
        row[0]: {
            "expected": int(row[1]),
            "received": int(row[2]),
            "pages": int(row[3]),
            "status": row[4],
        }
        for row in connection.execute(
            """
            SELECT trade_date, expected_rows, received_rows, pages, status
            FROM fetch_status
            """
        )
    }
    missing_dates = [value for value in calendar_dates if value not in status_rows]
    vendor_no_data_dates = [
        value
        for value in calendar_dates
        if value in status_rows and status_rows[value]["status"] == "vendor_no_data"
    ]
    failed_dates = [
        value
        for value in calendar_dates
        if value in status_rows and status_rows[value]["status"] == "failed"
    ]
    row_mismatch_dates = [
        value
        for value in calendar_dates
        if value in status_rows
        and status_rows[value]["status"] == "complete"
        and status_rows[value]["expected"] != status_rows[value]["received"]
    ]
    pagination_complete = not missing_dates and not failed_dates and not row_mismatch_dates
    available_date_count = len(calendar_dates) - len(vendor_no_data_dates)

    rows_by_type = {
        row[0]: int(row[1])
        for row in connection.execute(
            "SELECT instrument_type, COUNT(*) FROM margin_daily GROUP BY instrument_type"
        )
    }
    rows_per_date = [
        int(row[0])
        for row in connection.execute(
            "SELECT COUNT(*) FROM margin_daily GROUP BY trade_date"
        )
    ]
    min_date, max_date = connection.execute(
        "SELECT MIN(trade_date), MAX(trade_date) FROM margin_daily"
    ).fetchone()
    latest_date, latest_stock_rows = export_latest_stocks(connection, latest_export_path)
    reconciliation = reconcile_aggregate(connection, aggregate_csv)

    audit: dict[str, Any] = {
        "dfcf_only": True,
        "exchange_requests": 0,
        "source_name": "东方财富数据中心",
        "source_url": DFCF_URL,
        "detail_report_name": DETAIL_REPORT,
        "calendar_report_name": CALENDAR_REPORT,
        "sample_status": SAMPLE_STATUS,
        "requested_start": requested_start,
        "requested_end": requested_end,
        "calendar_start": calendar_dates[0],
        "calendar_end": calendar_dates[-1],
        "calendar_dates": len(calendar_dates),
        "calendar_requests": calendar_requests,
        "network": stats.as_dict(),
        "database_rows": scalar(connection, "SELECT COUNT(*) FROM margin_daily"),
        "database_dates": scalar(
            connection,
            "SELECT COUNT(DISTINCT trade_date) FROM margin_daily",
        ),
        "database_start": min_date,
        "database_end": max_date,
        "rows_by_instrument_type": rows_by_type,
        "rows_per_date": summarize([float(value) for value in rows_per_date]),
        "unknown_instrument_rows": rows_by_type.get("UNKNOWN", 0),
        "null_financing_balance_rows": scalar(
            connection,
            "SELECT COUNT(*) FROM margin_daily WHERE financing_balance_yuan IS NULL",
        ),
        "negative_financing_balance_rows": scalar(
            connection,
            "SELECT COUNT(*) FROM margin_daily WHERE financing_balance_yuan < 0",
        ),
        "missing_calendar_dates": missing_dates,
        "vendor_no_data_dates": vendor_no_data_dates,
        "failed_dates": failed_dates,
        "row_mismatch_dates": row_mismatch_dates,
        "vendor_pagination_complete": pagination_complete,
        "calendar_coverage_complete": not vendor_no_data_dates,
        "calendar_date_coverage_ratio": (
            available_date_count / len(calendar_dates) if calendar_dates else None
        ),
        "latest_stock_export_date": latest_date,
        "latest_stock_export_rows": latest_stock_rows,
        "aggregate_reconciliation": reconciliation,
        "usage_boundary": {
            "security_level_history": (
                "Use the a_share_stock_margin_daily SQLite view for DFCF vendor "
                "security-level history."
            ),
            "market_total": (
                "Do not sum this detail table to replace dfcf_margin_balances.csv "
                "unless aggregate reconciliation is exact."
            ),
            "official_status": "Not exchange-official per-security raw data.",
        },
        "updated_at_utc": utc_now(),
    }
    return audit


def set_metadata(
    connection: sqlite3.Connection,
    values: dict[str, str],
) -> None:
    with connection:
        connection.executemany(
            """
            INSERT INTO metadata (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            list(values.items()),
        )


def resolve_project_root(value: str | None) -> Path:
    root = Path(value).expanduser().resolve() if value else Path(__file__).resolve().parents[4]
    if not (root / "AGENTS.md").exists():
        raise FileNotFoundError(f"cannot confirm project root: {root}")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch and audit DFCF per-security margin history into SQLite"
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--start-date", default="2016-01-01")
    parser.add_argument("--end-date", default=date.today().isoformat())
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--refresh-days", type=int, default=14)
    parser.add_argument("--force-all", action="store_true")
    parser.add_argument("--progress-every", type=int, default=10)
    args = parser.parse_args()

    if args.workers < 1 or args.workers > 32:
        raise ValueError("--workers must be between 1 and 32")
    if args.refresh_days < 1:
        raise ValueError("--refresh-days must be positive")
    if args.progress_every < 1:
        raise ValueError("--progress-every must be positive")
    start = date.fromisoformat(args.start_date)
    end = date.fromisoformat(args.end_date)
    if start > end:
        raise ValueError("--start-date must not be after --end-date")

    project_root = resolve_project_root(args.project_root)
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else project_root
        / "artifacts"
        / "leverage_capitulation"
        / "individual_margin_2016_present"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    database_path = output_dir / "eastmoney_individual_margin.sqlite"
    audit_path = output_dir / "individual_margin_audit.json"
    latest_export_path = output_dir / "latest_a_share_stock_margin.csv"
    aggregate_csv = (
        project_root
        / "artifacts"
        / "leverage_capitulation"
        / "dfcf_daily"
        / "dfcf_margin_balances.csv"
    )

    stats = NetworkStats()
    calendar_dates, calendar_requests = fetch_trade_dates(
        args.start_date,
        args.end_date,
        stats=stats,
    )
    connection = open_database(database_path)
    set_metadata(
        connection,
        {
            "source_url": DFCF_URL,
            "detail_report_name": DETAIL_REPORT,
            "sample_status": SAMPLE_STATUS,
            "requested_start": args.start_date,
            "requested_end": args.end_date,
        },
    )

    already_complete = settled_dates(connection)
    refresh_start = (end - timedelta(days=args.refresh_days)).isoformat()
    if args.force_all:
        target_dates = calendar_dates
    else:
        target_dates = [
            value
            for value in calendar_dates
            if value not in already_complete or value >= refresh_start
        ]

    print(
        json.dumps(
            {
                "event": "fetch_start",
                "calendar_dates": len(calendar_dates),
                "already_complete": len(already_complete & set(calendar_dates)),
                "target_dates": len(target_dates),
                "workers": args.workers,
                "database": str(database_path),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    failures: list[str] = []
    vendor_gaps: list[str] = []
    completed = 0
    started_at = time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(fetch_trade_date, value, stats=stats): value
                for value in target_dates
            }
            for future in as_completed(futures):
                trade_date = futures[future]
                try:
                    fetched = future.result()
                    store_date_fetch(connection, fetched)
                except VendorNoDataError as exc:
                    vendor_gaps.append(trade_date)
                    store_vendor_gap(connection, trade_date, exc)
                except Exception as exc:
                    failures.append(trade_date)
                    store_failure(connection, trade_date, exc)
                completed += 1
                if (
                    completed % args.progress_every == 0
                    or completed == len(target_dates)
                ):
                    elapsed = max(time.monotonic() - started_at, 0.001)
                    print(
                        json.dumps(
                            {
                                "event": "progress",
                                "completed_dates": completed,
                                "target_dates": len(target_dates),
                                "failed_dates": len(failures),
                                "vendor_no_data_dates": len(vendor_gaps),
                                "dates_per_minute": round(completed / elapsed * 60.0, 2),
                                "network": stats.as_dict(),
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )

        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        audit = build_audit(
            connection,
            database_path=database_path,
            calendar_dates=calendar_dates,
            aggregate_csv=aggregate_csv,
            stats=stats,
            requested_start=args.start_date,
            requested_end=args.end_date,
            calendar_requests=calendar_requests,
            latest_export_path=latest_export_path,
        )
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        connection.close()

    audit["database_sha256"] = sha256_file(database_path)
    audit["latest_stock_export_sha256"] = sha256_file(latest_export_path)
    audit["database_size_bytes"] = database_path.stat().st_size
    atomic_write_json(audit, audit_path)
    print(json.dumps(audit, ensure_ascii=False, indent=2), flush=True)

    if failures or not audit["vendor_pagination_complete"]:
        raise RuntimeError(
            "DFCF individual margin bootstrap is incomplete; rerun to resume failed dates"
        )


if __name__ == "__main__":
    main()
