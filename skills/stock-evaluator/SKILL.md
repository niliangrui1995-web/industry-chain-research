---
name: stock-evaluator
description: Project-local stock evaluation workflow for 产业链投研. Use after industry route and source collection to evaluate A-share, HK, US, Japan, Taiwan, or Korea listed companies through fundamental quality, earnings elasticity, trading elasticity, valuation, evidence strength, and risks. Does not force a US-style dashboard, buy/sell call, target price, or entry price unless the user explicitly asks.
---

# Stock Evaluator

Use this skill for company-level stock evaluation inside `产业链投研`.

This is not a generic trading-dashboard skill. It does not start from price action, does not force BUY/HOLD/SELL, and does not fabricate metrics. It turns verified evidence into a company-level investment judgment after the relevant industry route has been chosen.

Default route:

`industry-research-router -> source / industry / market-data skills -> stock-evaluator -> advanced-evaluation when ranking or scoring is needed`

## When To Use

Use when the user asks:

- 单只股票是否值得研究、能不能买、估值贵不贵、风险在哪里；
- 多家公司基本面谁更好；
- 产业链映射后的 A 股/HK/US/JP/TW/KR 候选公司比较；
- 基本面质量、业绩弹性、交易弹性三层排序；
- 公告、财报、IR、订单、客户证据出来后如何影响公司判断。

If the question is only a quote or K-line check, use market-data skills first. If the question is only industry-chain structure, use industry skills first.

## Evidence Rules

Never fabricate numbers. If current data is required, verify it through tools, web, filings, or local datasets.

Required source hierarchy:

1. Official filings, exchange disclosures, annual/interim/quarterly reports, prospectuses, company IR, official announcements.
2. Official customer/supplier evidence and industry association or regulator sources.
3. Reputable financial data vendors and credible media.
4. Market-data tools for price, turnover, market cap, valuation, K-line, technical indicators, limit-board behavior, concept heat, and liquidity. Use TDX Finance Data for A-share quote/valuation/technical/涨停跌停 context when available.
5. Grok/X, social posts, forums, model summaries, and concept-board labels only as leads.

Use `N/A` for unavailable values. Do not substitute zero for missing data.

Always normalize listing identity:

| Market | Suffix / Format |
|---|---|
| Mainland A-share | `600xxx.SH`, `000xxx.SZ`, `688xxx.SH`, `8xxxxx.BJ` |
| Hong Kong | `0700.HK`, `9988.HK` |
| US | `AAPL`, `NVDA` |
| Japan | `6925.T`, `3110.T` |
| Taiwan | `3017.TW`, `2313.TW` |
| Korea | `005930.KS` |

## Core Workflow

### 1. State The Company And Chain Position

Before judging the stock, write a compact company identity:

- listed entity and ticker;
- main products and business segments;
- where it sits in the industry chain;
- which downstream demand actually drives its revenue and margin;
- whether it is a true beneficiary, indirect beneficiary, option-like candidate, or concept-adjacent name.

If the chain position is unclear, return to `industry-research-router`, `search-specialist`, or the relevant industry skill before scoring.

### 2. Build A Three-Lens Evaluation

Keep these three lenses separate. Do not average them into one vague score unless the user asks for a scorecard.

#### Fundamental Quality

Assess:

- business quality and product value share;
- competitive position and moat;
- customer quality and certification cycle;
- margin structure and cash conversion;
- management execution and disclosure quality;
- balance-sheet risk;
- durability of demand.

#### Earnings Elasticity

Assess:

- revenue exposure to the selected segment;
- order, backlog, capacity, utilization, ASP, and mix changes;
- gross-margin leverage and operating leverage;
- product generation upgrade;
- one-time versus durable drivers;
- whether official guidance or recent reports confirm the thesis.

#### Trading Elasticity

Assess only after beneficiary logic is established:

- market cap and float market cap when available;
- turnover, liquidity, and volatility;
- 20/60-day trend and price position;
- catalyst density and expectation gap;
- crowding and valuation risk;
- near-term announcements, earnings, IR, or policy events.

Trading elasticity cannot prove real beneficiary status.

### 3. Valuation And Risk

Use valuation as context, not as a stand-alone answer.

Check:

- PE/PB/PS/EV metrics when applicable and verified;
- revenue and profit growth direction;
- margin trend;
- cash flow and working capital;
- peer valuation only within the same route or business model;
- whether current valuation already prices in the catalyst.

Risks must include:

- evidence gap;
- customer concentration;
- capacity or yield uncertainty;
- order conversion risk;
- price/cost spread risk;
- accounting or working-capital stress;
- policy/export-control/regulatory risk;
- valuation and crowding risk.

### 4. Recommendation Framing

Default output is not a deterministic buy/sell order. Use one of:

- `main_candidate`: hard evidence and valuation/trading context support focused follow-up.
- `watch`: business route is plausible but evidence or timing is incomplete.
- `event_trade_only`: short-term catalyst exists but fundamental evidence is weak.
- `avoid_or_reject`: concept heat, weak evidence, poor fundamentals, or valuation/crowding risk dominates.
- `N/A`: data is insufficient.

Only provide explicit buy/sell, target price, entry zone, or position sizing when the user asks for trading execution. Even then, label the assumptions and data timestamp.

## Output Pattern

For a single company:

```text
结论先行：
- 评级框架：main_candidate / watch / event_trade_only / avoid_or_reject / N/A
- 核心理由：
- 最大风险：
- 需要补证的关键点：

公司和产业链位置：
| ticker | company | listing market | chain position | true exposure | evidence |

三层判断：
| lens | verdict | evidence | key risk | next indicator |
| fundamental quality | ... | ... | ... | ... |
| earnings elasticity | ... | ... | ... | ... |
| trading elasticity | ... | ... | ... | ... |

估值与风险：
- 估值：
- 财务质量：
- 催化与反转指标：
```

For multiple companies:

```text
结论先行：
- 基本面质量第一：
- 业绩弹性第一：
- 交易弹性第一：
- 最大风险：

排名：
| rank | company | ticker | fundamental quality | earnings elasticity | trading elasticity | evidence strength | verdict |
```

## Common Mistakes To Avoid

- Do not start from hot stock names and reverse-map an industry story.
- Do not equate "good company" with "highest stock elasticity".
- Do not use K-line strength, market heat, Grok chatter, or model prose as beneficiary proof.
- Do not compare companies from different value-chain nodes before explaining the node difference.
- Do not force a recommendation when current price, valuation, or filings have not been verified.
- Do not require a React dashboard, 60+ metrics, or US-only ratios for normal project research.

## Related Skills

- `industry-research-router`: required entry and routing discipline.
- `a-share-disclosure-trading-data`: A-share official announcement and trading-event evidence.
- `a-share-company-tracking`: watchlist baseline and daily state workflow.
- `search-specialist`: official source discovery and contradiction tracking.
- `research-summarizer`: filings, announcements, reports, PDFs, and transcripts.
- `TDX Finance Data:tdx-finance-data`: A-share quote, valuation, technical indicators, sector/concept screens,涨停/跌停,封单,连板,板型, and market-reaction context only.
- `allstock-data` / `finance` / `yfinance-mcp-server` / `stocks` / `alpha-vantage`: market and financial data.
- `advanced-evaluation`: score consistency, bias control, and three-layer ranking.
