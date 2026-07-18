from __future__ import annotations

import argparse
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


SZSE_REPORT_URL = "https://www.szse.cn/api/report/ShowReport/data"
HEADERS = {
    "Referer": "https://www.szse.cn/disclosure/margin/object/index.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodexResearch/1.0",
}


def detect_dates(path: Path, start_date: str) -> list[str]:
    frame = pd.read_csv(path, usecols=["date", "sz_margin_y"])
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame["sz_margin_y"] = pd.to_numeric(frame["sz_margin_y"], errors="raise")
    repeated = frame["sz_margin_y"].eq(frame["sz_margin_y"].shift(1))
    invalid = repeated | repeated.shift(1, fill_value=False)
    return frame.loc[invalid & frame["date"].ge(pd.Timestamp(start_date)), "date"].dt.strftime("%Y-%m-%d").tolist()


def read_existing(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["date"]: row for row in csv.DictReader(handle)}


def fetch_date(date: str, retries: int = 4) -> dict[str, str]:
    params = {
        "SHOWTYPE": "JSON",
        "CATALOGID": "1837_xxpl",
        "txtDate": date,
        "tab1PAGENO": "1",
        "random": "0.7425245522795993",
    }
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requests.get(SZSE_REPORT_URL, params=params, headers=HEADERS, timeout=30)
            response.raise_for_status()
            payload = response.json()
            value = payload[0]["data"][0]["jrrzye"]
            balance = float(str(value).replace(",", ""))
            return {
                "date": date,
                "sz_margin_y": f"{balance:.8f}",
                "source": SZSE_REPORT_URL,
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Failed to fetch SZSE margin balance for {date}: {last_error}")


def write_rows(path: Path, rows: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["date", "sz_margin_y", "source", "fetched_at_utc"],
        )
        writer.writeheader()
        writer.writerows(rows[date] for date in sorted(rows))
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parents[4]
    parser = argparse.ArgumentParser(description="Fetch official SZSE balances for stale local rows")
    parser.add_argument("--margin-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start-date", default="2014-01-01")
    parser.add_argument("--workers", type=int, default=4)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError("--workers must be between 1 and 4")
    target_dates = detect_dates(args.margin_csv, args.start_date)
    rows = read_existing(args.output)
    pending = [date for date in target_dates if date not in rows]
    print(f"target_dates={len(target_dates)} existing={len(rows)} pending={len(pending)}")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch_date, date): date for date in pending}
        completed = 0
        failures: list[tuple[str, str]] = []
        for future in as_completed(futures):
            date = futures[future]
            try:
                row = future.result()
            except RuntimeError as exc:
                failures.append((date, str(exc)))
                print(f"failed={date}: {exc}")
                continue
            rows[row["date"]] = row
            completed += 1
            if completed % 10 == 0 or completed == len(pending):
                write_rows(args.output, rows)
                print(f"completed={completed}/{len(pending)}")
    write_rows(args.output, rows)
    if failures:
        print(f"failed_dates={len(failures)}; rerun the command to resume")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
