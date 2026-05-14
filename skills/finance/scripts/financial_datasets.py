#!/usr/bin/env python3
"""
Financial Datasets helper.

Fetch cost-controlled US company data from https://api.financialdatasets.ai.
The API key is read from FINANCIAL_DATASETS_API_KEY in the environment, or from
an ignored .env file in the current workspace.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests

BASE_URL = "https://api.financialdatasets.ai"
DEFAULT_TIMEOUT = 30


def _load_dotenv() -> None:
    if os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        return

    candidates = [Path.cwd() / ".env"]
    here = Path(__file__).resolve()
    candidates.extend(parent / ".env" for parent in here.parents[:6])

    for path in candidates:
        if not path.exists():
            continue
        try:
            for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip().lstrip("\ufeff")
                if key == "FINANCIAL_DATASETS_API_KEY":
                    os.environ[key] = value.strip().strip('"').strip("'")
                    return
        except OSError:
            continue


def _api_key() -> str:
    _load_dotenv()
    value = os.environ.get("FINANCIAL_DATASETS_API_KEY")
    if not value:
        raise SystemExit(
            "Missing FINANCIAL_DATASETS_API_KEY. Set it in the environment or an ignored .env file."
        )
    return value


def _request(
    session: requests.Session,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    try:
        response = session.get(url, params=params or {}, timeout=DEFAULT_TIMEOUT)
        try:
            body: Any = response.json()
        except ValueError:
            body = {"raw_preview": response.text[:500]}
        return {
            "ok": response.ok,
            "status": response.status_code,
            "path": path,
            "params": params or {},
            "data": body if response.ok else None,
            "error": None if response.ok else body,
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status": None,
            "path": path,
            "params": params or {},
            "data": None,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "X-API-KEY": _api_key(),
            "User-Agent": "codex-finance-skill/financial-datasets",
        }
    )
    return session


def _company_pack(ticker: str, limit: int, price_days: int) -> Dict[str, Any]:
    ticker = ticker.upper()
    end = time.strftime("%Y-%m-%d")
    start = time.strftime("%Y-%m-%d", time.localtime(time.time() - price_days * 86400))
    requests_to_make = {
        "company_facts": ("/company/facts", {"ticker": ticker}),
        "price_snapshot": ("/prices/snapshot", {"ticker": ticker}),
        "historical_prices": (
            "/prices",
            {"ticker": ticker, "interval": "day", "start_date": start, "end_date": end},
        ),
        "financials": ("/financials", {"ticker": ticker, "period": "annual", "limit": limit}),
        "financial_metrics_ttm": (
            "/financial-metrics",
            {"ticker": ticker, "period": "ttm", "limit": min(limit, 4)},
        ),
        "earnings": ("/earnings", {"ticker": ticker, "limit": limit}),
        "filings": ("/filings", {"ticker": ticker, "limit": limit}),
        "insider_trades": ("/insider-trades", {"ticker": ticker, "limit": limit}),
        "institutional_ownership": (
            "/institutional-ownership",
            {"ticker": ticker, "limit": limit},
        ),
        "segments": ("/financials/segments", {"ticker": ticker, "period": "annual", "limit": limit}),
        "news": ("/news", {"ticker": ticker, "limit": min(limit, 10)}),
        "analyst_estimates": ("/analyst-estimates", {"ticker": ticker, "period": "annual"}),
        "kpi_metrics": ("/kpi/metrics", {"ticker": ticker, "limit": limit}),
        "kpi_guidance": ("/kpi/guidance", {"ticker": ticker, "limit": limit}),
        "kpi_non_gaap": ("/kpi/non-gaap", {"ticker": ticker, "limit": limit}),
    }

    session = _session()
    results = {
        name: _request(session, path, params)
        for name, (path, params) in requests_to_make.items()
    }
    return {"ticker": ticker, "source": "Financial Datasets", "results": results}


def _single_endpoint(ticker: str, endpoint: str, limit: int) -> Dict[str, Any]:
    endpoint_map: Dict[str, tuple[str, Dict[str, Any]]] = {
        "facts": ("/company/facts", {"ticker": ticker}),
        "snapshot": ("/prices/snapshot", {"ticker": ticker}),
        "financials": ("/financials", {"ticker": ticker, "period": "annual", "limit": limit}),
        "metrics": ("/financial-metrics", {"ticker": ticker, "period": "ttm", "limit": limit}),
        "earnings": ("/earnings", {"ticker": ticker, "limit": limit}),
        "filings": ("/filings", {"ticker": ticker, "limit": limit}),
        "insiders": ("/insider-trades", {"ticker": ticker, "limit": limit}),
        "ownership": ("/institutional-ownership", {"ticker": ticker, "limit": limit}),
        "segments": ("/financials/segments", {"ticker": ticker, "period": "annual", "limit": limit}),
        "news": ("/news", {"ticker": ticker, "limit": min(limit, 10)}),
        "estimates": ("/analyst-estimates", {"ticker": ticker, "period": "annual"}),
    }
    if endpoint not in endpoint_map:
        available = ", ".join(sorted(endpoint_map))
        raise SystemExit(f"Unknown endpoint '{endpoint}'. Available: {available}")
    path, params = endpoint_map[endpoint]
    return _request(_session(), path, params)


def _summarize_value(value: Any) -> Any:
    if isinstance(value, list):
        return {"count": len(value), "sample": _summarize_value(value[0]) if value else None}
    if isinstance(value, dict):
        return {k: _summarize_value(v) for k, v in list(value.items())[:16]}
    return value


def _summarize_pack(pack: Dict[str, Any]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"ticker": pack["ticker"], "source": pack["source"], "results": {}}
    for name, result in pack["results"].items():
        item: Dict[str, Any] = {"ok": result["ok"], "status": result["status"], "path": result["path"]}
        if result["ok"]:
            item["summary"] = _summarize_value(result["data"])
        else:
            item["error"] = result["error"]
        summary["results"][name] = item
    return summary


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", help="US ticker, e.g. NVDA or AAPL")
    parser.add_argument(
        "--endpoint",
        default="pack",
        help="pack, facts, snapshot, financials, metrics, earnings, filings, insiders, ownership, segments, news, estimates",
    )
    parser.add_argument("--limit", type=int, default=3, help="Small result limit to control credits")
    parser.add_argument("--price-days", type=int, default=14, help="Historical price lookback for pack")
    parser.add_argument("--raw", action="store_true", help="Print full response instead of compact summary")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.endpoint == "pack":
        payload = _company_pack(args.ticker, args.limit, args.price_days)
        if not args.raw:
            payload = _summarize_pack(payload)
    else:
        payload = _single_endpoint(args.ticker.upper(), args.endpoint, args.limit)
        if not args.raw and payload.get("ok"):
            payload = {
                "ok": payload["ok"],
                "status": payload["status"],
                "path": payload["path"],
                "summary": _summarize_value(payload["data"]),
            }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
