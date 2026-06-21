# TDX Finance Data MCP Boundary

Use this reference when project tasks need to decide whether to call `TDX Finance Data:tdx-finance-data`, account skill `tdx-finance-data`, or native MCP tool `mcp__tdx.tdx_wenda_quotes`.

The tested TDX MCP shape is one natural-language tool:

```text
mcp__tdx.tdx_wenda_quotes(question, range, page, size)
```

`range` values:

- `AG`: A-share, default.
- `HK-GP`: Hong Kong stocks.
- `JJ`: funds and ETFs.
- `ZS`: indexes and TDX sector/index codes.

The return shape is usually:

```json
{
  "meta": { "code": 0, "total": 1 },
  "headers": ["field"],
  "data": [["value"]]
}
```

## High-Confidence Uses

Use TDX first for A-share trading context and market reaction:

- single-stock latest quote: current price, change, open/high/low/close, amplitude, volume, turnover, amount;
- valuation snapshot: dynamic PE, TTM PE when requested, PB, circulating/free-float market cap;
- recent price action: daily close columns, interval change, interval volume, daily volume and turnover;
- technical indicators: MACD/DIF/DEA, KDJ, RSI, volume ratio, 5/20-day averages;
- financial snapshot when the natural-language query maps cleanly: revenue, cost, revenue/profit growth, parent net profit, gross margin, net margin, ROE, debt ratio;
- index and sector quote: use `range=ZS`, especially for known TDX codes such as `881319`;
- industry/concept constituent screens: industry or concept name plus ranking condition, such as positive TTM PE lowest,涨幅前 10,成交额前 10;
- 涨停/跌停 lists: first/last limit time, open count, sealed amount, consecutive days,几天几板,板型,涨停/跌停原因,原因揭秘, industry;
- fund/ETF snapshot: latest NAV/date, cumulative NAV, near-period returns,申购状态, listed ETF trading fields;
- Hong Kong quick quote: price, change, and some valuation fields when `range=HK-GP`.

## Weak Or Unsuitable Uses

Do not rely on TDX for:

- official announcements, CNINFO, exchange filings, annual/interim/quarterly reports, IR records, or official customer/supplier evidence;
- research-report text, analyst thesis, or full broker-note retrieval;
- stable资金流/北向/主力净流入 fields unless a specific query is verified live;
- one-call multi-stock comparison; split calls when row completeness matters;
- market-wide aggregated breadth such as exact上涨/下跌家数 when the response is a stock list rather than totals;
- durable historical OHLCV warehouse, factor backtesting, VCP pattern research, or auditable quantitative datasets.

## Evidence Treatment

Classify TDX output as:

- `market_data_vendor` for price, valuation, volume, turnover, technical, index, sector, fund, and ETF fields;
- `secondary_trading_context` for涨停/跌停原因,原因揭秘,板型,连板,封单 and concept labels;
- never `official_announcement` or `confirmed_official`.

TDX can support trading elasticity, timing, liquidity, valuation context, market attention, and follow-up source prioritization. It cannot prove true beneficiary status, order/customer evidence, supply-chain exposure, or durable earnings inflection.

## Query Discipline

- Query one stock, one fund, one index, one sector/concept, or one screen per call.
- Include ticker and name when possible: `贵州茅台 600519 最新行情`.
- Use `range=ZS` for sector/index codes and `range=JJ` for funds/ETFs.
- For comparisons, call each security separately, then synthesize.
- If a query returns `meta.total=0`, rewrite shorter with fewer mixed dimensions before declaring data unavailable.
- Record the date embedded in returned headers, because TDX often labels fields with trading dates.

## Recommended Project Routing

- A-share quote, valuation, technical timing,涨停/跌停, concept or sector screen: call TDX early after the research route is chosen.
- Company baseline or official evidence: use `search-specialist`, `a-share-disclosure-trading-data`, CNINFO/exchange/company IR first; use TDX only for market reaction.
- Daily tracking: use TDX to add market-reaction context only when a company had material price/limit-board activity or the user asks for trading elasticity.
- AI/semiconductor concept screens: use TDX to discover market-attention names, then verify true exposure through official filings and industry-chain skills before any ranking.
