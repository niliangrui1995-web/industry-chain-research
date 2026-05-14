# Providers & symbol formats

## Stocks / ETFs / Indices (default: Yahoo via yfinance)
Pros:
- Very broad symbol coverage, no API key.
Cons:
- Unofficial access patterns can be rate-limited or break.

Common examples:
- AAPL, MSFT, TSLA
- Indices: ^GSPC (S&P 500), ^DJI, ^IXIC
- ETFs: VOO, SPY, QQQ

## US company fundamentals and disclosures (Financial Datasets supplement)
Use `scripts/financial_datasets.py` when the task is US public-company research, especially:
- company facts and SEC identifiers
- price snapshots and short historical OHLCV checks
- income statements, balance sheets, cash flow statements, and TTM metrics
- SEC filings, earnings releases, segmented financials
- institutional ownership, insider trades, company news, and analyst estimates

Configuration:
- Read API key from `FINANCIAL_DATASETS_API_KEY`.
- The helper also loads `FINANCIAL_DATASETS_API_KEY` from an ignored project `.env` file.
- Do not hardcode the API key in tracked skill files.

Cost and fallback discipline:
- Keep `--limit` small by default.
- Treat `402 Insufficient credits`, `404`, transport errors, and empty payloads as partial-data outcomes.
- When Financial Datasets cannot answer, continue with official SEC/company filings, web search, yfinance, Alpha Vantage, or other available sources.

Examples:
- `python scripts/financial_datasets.py NVDA`
- `python scripts/financial_datasets.py NVDA --endpoint metrics --limit 2`
- `python scripts/financial_datasets.py AAPL --endpoint filings --limit 5`

## FX (default: ExchangeRate-API Open Access)
Endpoint: https://open.er-api.com/v6/latest/<BASE>
- No API key
- Updates once per day
- Rate-limited
- Attribution required by their terms

Symbol formats accepted by this skill:
- USD/ZAR
- USDZAR
- GBP-JPY
- EURUSD

We normalize to BASE/QUOTE and fetch BASE->all then pick QUOTE.

## Why not exchangerate.host by default?
It now requires an API key for most useful endpoints and has limited free quotas, so it’s not a great no-key default.

## Paid providers (optional future upgrade)
If you need many symbols or frequent polling:
- Twelve Data
- Alpha Vantage
- Polygon
- Finnhub

This skill includes environment variable placeholders, but does not implement these providers yet.
