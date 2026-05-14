---
name: finance
description: Track stocks, ETFs, indices, crypto (where available), FX pairs, and US public-company fundamentals with caching + provider fallbacks. Use Financial Datasets as a supplemental source for US company facts, prices, financials, SEC filings, ownership, insider trades, news, and estimates when FINANCIAL_DATASETS_API_KEY is available.
metadata: {"clawdbot":{"config":{"requiredEnv":["FINANCIAL_DATASETS_API_KEY","TWELVEDATA_API_KEY","ALPHAVANTAGE_API_KEY"],"stateDirs":[".cache/finance"],"example":"# Optional paid providers\n# export FINANCIAL_DATASETS_API_KEY=\"...\"\n# export TWELVEDATA_API_KEY=\"...\"\n# export ALPHAVANTAGE_API_KEY=\"...\"\n"}}}
---

# Market Tracker Skill

This skill helps you fetch **latest quotes** and **historical series** for:
- Stocks / ETFs / Indices (e.g., AAPL, MSFT, ^GSPC, VOO)
- FX pairs (e.g., USD/ZAR, EURUSD, GBP-JPY)
- Crypto tickers supported by the chosen provider (best-effort)
- US public-company fundamentals and disclosure data via Financial Datasets when configured

It is optimized for:
- fast “what’s the price now?” queries
- lightweight tracking with a local watchlist
- caching to avoid rate-limits

## When to use
Use this skill when the user asks:
- "Pull US company fundamentals / SEC filings / ownership / insider trades / news for NVDA, AAPL, etc."
- “What’s the latest price of ___?”
- “Track ___ and ___ and show me daily changes.”
- “Give me a 30-day series for ___.”
- “Convert USD to ZAR (or track USD/ZAR).”
- “Maintain a watchlist and summarize performance.”

## Provider strategy (important)
- **Stocks/ETFs/indices** default: Yahoo Finance via `yfinance` (no key, broad coverage), but it is unofficial and can rate-limit.
- **FX** default: ExchangeRate-API Open Access endpoint (no key, daily update).
- **US company data supplement**: Financial Datasets via `FINANCIAL_DATASETS_API_KEY`. Use it for US ticker fundamentals, SEC filings, ownership, insider trades, company news, analyst estimates, and price snapshots. If an endpoint returns `402 Insufficient credits`, `404`, empty data, or transport errors, keep the partial result and continue with official filings, web search, yfinance, Alpha Vantage, or other available sources.
- If the user needs high-frequency or many symbols, recommend adding a paid provider later.

See `providers.md` for details and symbol formats.

---

# Quick start (how you run it)
These scripts are intended to be run from a terminal. The agent should:
1) ensure dependencies installed
2) run the scripts
3) summarize results cleanly

Install:
- `python -m venv .venv && source .venv/bin/activate` (or Windows equivalent)
- `pip install -r requirements.txt`

## Commands

### 1) Latest quote (stock/ETF/index)
Examples:
- `python scripts/market_quote.py AAPL`
- `python scripts/market_quote.py ^GSPC`
- `python scripts/market_quote.py VOO`

### 2) Latest FX rate
Examples:
- `python scripts/market_quote.py USD/ZAR`
- `python scripts/market_quote.py EURUSD`
- `python scripts/market_quote.py GBP-JPY`

### 3) Historical series (CSV to stdout)
Examples:
- `python scripts/market_series.py AAPL --days 30`
- `python scripts/market_series.py USD/ZAR --days 30`

### 4) Watchlist summary (local file)
- Add tickers: `python scripts/market_watchlist.py add AAPL MSFT USD/ZAR`
- Remove: `python scripts/market_watchlist.py remove MSFT`
- Show summary: `python scripts/market_watchlist.py summary`

### 5) Financial Datasets company pack (US public companies)
The helper reads `FINANCIAL_DATASETS_API_KEY` from the environment or from an ignored `.env` file in the project root.

- Compact company pack: `python scripts/financial_datasets.py NVDA`
- Single endpoint: `python scripts/financial_datasets.py NVDA --endpoint financials --limit 3`
- Full raw JSON: `python scripts/financial_datasets.py NVDA --raw`

Supported endpoint names: `facts`, `snapshot`, `financials`, `metrics`, `earnings`, `filings`, `insiders`, `ownership`, `segments`, `news`, `estimates`.

---

# Output expectations (what you should return to the user)
- For quotes: price, change %, timestamp/source, and any caveats (like “FX updates daily”).
- For series: confirm date range, number of points, and show a small preview (first/last few rows).
- If rate-limited: explain what happened and retry with backoff OR advise to reduce frequency.

---

# Safety / correctness
- Never claim “real-time” unless the provider is truly real-time. FX open access updates daily.
- Always cache responses and throttle repeated calls.
- If Yahoo blocks requests, propose a paid provider or increase cache TTL.
