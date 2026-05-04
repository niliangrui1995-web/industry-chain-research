#!/usr/bin/env python3
"""Build an initial official-source inventory for an earnings event.

This script uses public SEC endpoints for U.S.-listed companies when a ticker is
available, and also generates targeted search URLs for investor-relations,
earnings-release, webcast, transcript, and presentation discovery.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
DEFAULT_USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "earnings-call-investment-analyst/0.1 contact@example.com",
)


def fetch_json(url: str, user_agent: str) -> Any:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper().replace(".", "-")


def resolve_sec_company(ticker: str, user_agent: str) -> dict[str, Any] | None:
    ticker_norm = normalize_ticker(ticker)
    data = fetch_json(SEC_TICKERS_URL, user_agent)
    for row in data.values():
        if str(row.get("ticker", "")).upper() == ticker_norm:
            cik = str(row["cik_str"]).zfill(10)
            return {
                "ticker": row.get("ticker"),
                "title": row.get("title"),
                "cik": cik,
            }
    return None


def parse_recent_filings(submissions: dict[str, Any]) -> list[dict[str, Any]]:
    recent = submissions.get("filings", {}).get("recent", {})
    accessions = recent.get("accessionNumber", [])
    filings: list[dict[str, Any]] = []
    for i, accession in enumerate(accessions):
        filing = {key: values[i] for key, values in recent.items() if i < len(values)}
        filings.append(filing)
    return filings


def sec_filing_url(cik: str, accession: str, primary_doc: str | None = None) -> str:
    cik_int = str(int(cik))
    accession_clean = accession.replace("-", "")
    if primary_doc:
        return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_clean}/{primary_doc}"
    return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_clean}/"


def select_relevant_filings(
    filings: list[dict[str, Any]],
    forms: set[str],
    limit: int,
) -> list[dict[str, Any]]:
    selected = []
    for filing in filings:
        form = str(filing.get("form", ""))
        if form not in forms:
            continue
        selected.append(filing)
        if len(selected) >= limit:
            break
    return selected


def search_url(query: str, engine: str) -> str:
    encoded = urllib.parse.urlencode({"q": query})
    if engine == "bing":
        return f"https://www.bing.com/search?{encoded}"
    if engine == "sec":
        return f"https://www.sec.gov/edgar/search/#{urllib.parse.quote(query)}"
    return f"https://www.google.com/search?{encoded}"


def build_search_queries(company: str, ticker: str, quarter: str, fiscal_year: str) -> list[dict[str, str]]:
    identity = company or ticker
    terms = [
        f"{identity} {ticker} {quarter} fiscal {fiscal_year} earnings release investor relations",
        f"{identity} {ticker} {quarter} {fiscal_year} earnings call webcast replay",
        f"{identity} {ticker} {quarter} {fiscal_year} earnings call transcript",
        f"{identity} {ticker} {quarter} {fiscal_year} earnings call audio StockAnalysis Quartr",
        f"{identity} {ticker} {quarter} {fiscal_year} earnings call transcript Motley Fool Seeking Alpha Benzinga Alpha Spread EarningsCall.biz",
        f"site:stockanalysis.com/stocks {ticker} transcripts {quarter} {fiscal_year}",
        f"site:files.quartr.com/audio-files {ticker} {quarter} {fiscal_year}",
        f"{identity} {ticker} {quarter} {fiscal_year} investor presentation earnings",
        f"{identity} {ticker} {quarter} {fiscal_year} Form 8-K earnings",
    ]
    queries: list[dict[str, str]] = []
    for term in terms:
        queries.append({"engine": "google", "query": term, "url": search_url(term, "google")})
        queries.append({"engine": "bing", "query": term, "url": search_url(term, "bing")})
    return queries


def safe_name(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    return cleaned.strip("_") or "unknown"


def write_markdown(path: Path, inventory: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Earnings Source Inventory")
    lines.append("")
    lines.append(f"- Ticker: {inventory.get('ticker') or 'n/a'}")
    lines.append(f"- Company: {inventory.get('company') or 'n/a'}")
    lines.append(f"- Quarter: {inventory.get('quarter') or 'n/a'}")
    lines.append(f"- Fiscal year: {inventory.get('fiscal_year') or 'n/a'}")
    lines.append(f"- Retrieved at: {inventory.get('retrieved_at')}")
    lines.append("")

    sec_company = inventory.get("sec_company")
    if sec_company:
        lines.append("## SEC Company")
        lines.append("")
        lines.append(f"- CIK: {sec_company.get('cik')}")
        lines.append(f"- SEC title: {sec_company.get('title')}")
        lines.append("")

    filings = inventory.get("sec_filings", [])
    if filings:
        lines.append("## Recent Relevant SEC Filings")
        lines.append("")
        lines.append("| Filing date | Form | Description | URL |")
        lines.append("|---|---|---|---|")
        for filing in filings:
            filing_date = filing.get("filingDate", "")
            form = filing.get("form", "")
            description = filing.get("primaryDocDescription") or filing.get("primaryDocument") or ""
            url = filing.get("url", "")
            lines.append(f"| {filing_date} | {form} | {description} | {url} |")
        lines.append("")

    queries = inventory.get("search_queries", [])
    if queries:
        lines.append("## Targeted Search URLs")
        lines.append("")
        for item in queries:
            lines.append(f"- [{item['engine']}] {item['query']}: {item['url']}")
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover official earnings sources.")
    parser.add_argument("--ticker", default="", help="Ticker symbol, for example AXTI or LITE.")
    parser.add_argument("--company", default="", help="Company name.")
    parser.add_argument("--quarter", default="", help="Quarter label, for example Q1.")
    parser.add_argument("--fiscal-year", default="", help="Fiscal year, for example 2026.")
    parser.add_argument("--out-dir", default="artifacts/earnings_sources", help="Output root directory.")
    parser.add_argument("--filing-limit", type=int, default=12, help="Maximum relevant SEC filings to include.")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="SEC User-Agent header.")
    args = parser.parse_args()

    if not args.ticker and not args.company:
        parser.error("Provide at least --ticker or --company.")

    retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
    ticker = normalize_ticker(args.ticker) if args.ticker else ""
    folder_parts = [safe_name(ticker or args.company), safe_name(args.quarter or "period"), safe_name(args.fiscal_year or "year")]
    out_dir = Path(args.out_dir) / "_".join(folder_parts)
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory: dict[str, Any] = {
        "ticker": ticker,
        "company": args.company,
        "quarter": args.quarter,
        "fiscal_year": args.fiscal_year,
        "retrieved_at": retrieved_at,
        "sec_company": None,
        "sec_filings": [],
        "search_queries": build_search_queries(args.company, ticker, args.quarter, args.fiscal_year),
    }

    if ticker:
        try:
            sec_company = resolve_sec_company(ticker, args.user_agent)
            inventory["sec_company"] = sec_company
            if sec_company:
                submissions = fetch_json(SEC_SUBMISSIONS_URL.format(cik=sec_company["cik"]), args.user_agent)
                forms = {"8-K", "10-Q", "10-K", "6-K", "20-F", "40-F"}
                filings = select_relevant_filings(parse_recent_filings(submissions), forms, args.filing_limit)
                for filing in filings:
                    filing["url"] = sec_filing_url(
                        sec_company["cik"],
                        filing.get("accessionNumber", ""),
                        filing.get("primaryDocument"),
                    )
                inventory["sec_filings"] = filings
        except Exception as exc:
            inventory["sec_error"] = repr(exc)

    json_path = out_dir / "source_inventory.json"
    md_path = out_dir / "source_inventory.md"
    json_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, inventory)

    print(str(md_path))
    print(str(json_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
