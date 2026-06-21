# Skill Map For Industry And Company Research

This is the compatibility route table for `industry-research-router`. The project master entrypoint remains `user-investment-framework`.

For full boundaries of every project skill and visible MCP/plugin surface, read:

```text
skills/user-investment-framework/references/skill-mcp-boundary-matrix.md
```

## Routing Protocol

1. Start from `user-investment-framework` for investment research.
2. Use this table only to refine the companion skill mix.
3. Choose the smallest useful skill mix.
4. Add live-data or web skills whenever the task depends on current price, market cap, PE/PB, volume, financial reports, orders, policy, regulation, or news.
5. Keep fundamental quality, earnings elasticity, and trading elasticity separate.
6. If a referenced skill is unavailable, keep the same analytical framework and state the gap only when it changes confidence.

## Boundary Rules

| Skill / Layer | Allowed Role | Boundary |
|---|---|---|
| `industry-research-router` | Compatibility classification and minimal route selection | Does not score the full universe or pick final stocks alone |
| `a-share-company-tracking` | A-share watchlist daily tracking and durable company files | Does not replace company research |
| `a-share-disclosure-trading-data` | CNINFO, exchange announcements, IR, dragon-tiger, block trades, T/T+1 windows | Evidence/data layer only |
| `ai-chain-research-orchestrator` | AI-chain evidence coordination and rumor discipline | Collector/coordinator only |
| `browser-grok-gemini-research` | Logged-in Chrome collection for Grok/X and Gemini | Collector only; Codex verifies |
| `semiconductor-ai-chain-investment-researcher` | AI/semiconductor segment and company mapping | Must start from segment/node universe |
| `serenity-alpha` | News/event to financial statement hypothesis | Hypothesis layer only |
| `advanced-evaluation` | Ranking consistency and bias checks | Does not replace domain judgment |
| `stock-fundamental-moat-triad` | Future-first company thesis and moat checks | Requires source collection and demand bridge |
| `stock-evaluator` / `business-analyst` | Financial quality, valuation, operating logic | After segment and evidence selection |
| TDX / iFinD / HTSC / DFCF / Yahoo / Alpha Vantage / QVeris | Market, vendor, screening, context data | Cannot prove beneficiary status or replace official evidence |
| `search-specialist` / `research-summarizer` | Source discovery and source digestion | Do not make final investment conclusions |
| Public Equity Investing plugin workflows | PM trackers, calendars, events, scenarios, risk, model, memo/pitch packaging | Companion layer only |

## Quick Trigger Matrix

| User intent / trigger | First skill mix | Notes |
|---|---|---|
| News/order/product launch/price hike/supply-chain change -> alpha | `user-investment-framework` + source skills + `serenity-alpha` + market-data skills + `advanced-evaluation` | Prove observable demand and source quality before naming stocks. |
| AI/半导体产业链怎么拆、行业本质、价值量、壁垒 | `user-investment-framework` + `semiconductor-ai-chain-investment-researcher` + `deep-research` | Add current-evidence skills only when needed. |
| 最近 24/48/72 小时 AI 产业链消息/爆料 | `user-investment-framework` + `ai-chain-research-orchestrator` + `browser-grok-gemini-research` + market-data skills | Grok/X first for discovery; Gemini for source gaps or counter-evidence. |
| 非半导体产业链怎么拆 | `user-investment-framework` + `industry-chain-deep-disassembly` + `deep-research` | Output chain map, value distribution, moat, verification cycle. |
| 成长行业瓶颈、BOM、交付时滞、未来卡点迁移 | `user-investment-framework` + `industry-chain-deep-disassembly` | Start from terminal demand and supply-gap evidence. |
| 谁是真龙头、谁蹭概念、竞争格局 | `user-investment-framework` + `competitive-landscape` + `competitive-intel` | Separate market share, customer validation, profitability, heat. |
| 单只股票估值、买卖点、仓位 | `user-investment-framework` + `stock-fundamental-moat-triad` + `stock-evaluator` + market-data skills | Do not skip upstream/downstream and evidence checks. |
| 多家公司谁更好、基本面排序 | `user-investment-framework` + `stock-fundamental-moat-triad` + `stock-evaluator` + `business-analyst` + `advanced-evaluation` | Build explicit rubric and cite hard data. |
| 谁股票弹性最大、短线弹性、交易弹性 | `user-investment-framework` + TDX/iFinD/`allstock-data` + `banana-farmer` + `advanced-evaluation` | Prioritize float market cap, turnover, volatility, trend, catalyst density, crowding risk. |
| A 股公司持续跟踪、watchlist 日更、baseline/state/events | `user-investment-framework` + `a-share-company-tracking` + `a-share-disclosure-trading-data` + source skills | At/after 20:00 Beijing time, check announcement date T and T+1. |
| 公告、CNINFO、交易所披露、龙虎榜、大宗交易 | `user-investment-framework` + `a-share-disclosure-trading-data` + `search-specialist`; add market-data skills for reaction | Trading events are liquidity/elasticity signals, not fundamental proof. |
| A 股涨停/跌停、封单、连板、板型、概念热度 | `user-investment-framework` + TDX; add iFinD/HTSC/DFCF if needed | Label as market or secondary trading context. |
| 官方资料、公告、年报、官网、PDF、客户/供应商证据 | `user-investment-framework` + `search-specialist` + `firecrawl-scraper` / `tavily-web` / global `web-scraper` | Design source priority first. |
| 研报、白皮书、公告、会议纪要、多来源材料消化 | `user-investment-framework` + `research-summarizer` + `advanced-evaluation` | Extract claim/evidence/limitations before synthesis. |
| 红利低波、股息率溢价、股债性价比 | `user-investment-framework` + `dividend-premium-tracker` + `stock-evaluator` + market-data skill | Style backdrop only. |
| 表格、评分卡、watchlist、Excel 模型 | `user-investment-framework` + `spreadsheet` / `xlsx-official` + `advanced-evaluation` | Preserve formatting; formulas must recalc. |

## Data Discipline

- Latest facts require current verification.
- Official disclosure outranks data vendors.
- Data vendors outrank social/model chatter for quantitative values, but still do not prove business exposure.
- TDX and iFinD are useful but should be labeled as vendor data unless original filings are retrieved.
- Write-capable plugin tools require explicit user instruction.
