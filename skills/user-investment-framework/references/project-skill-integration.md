# Project Skill Integration Map

Use this reference when `user-investment-framework` needs to choose companion skills for a non-trivial investment research task.

Rule: start with `user-investment-framework`; load the smallest useful supporting set; preserve each supporting skill's boundary.

## Contents

- Entry And Backbone
- AI Chain And Semiconductor
- Industry Chain, Bottlenecks, And Competition
- Company And Stock Research
- Event-Driven Alpha And Financial Translation
- Public Equity Investing Plugin Workflows
- A-Share Tracking And Disclosure
- Market Data And Trading Context
- HTSC Plugin Tools
- Source Discovery And Evidence Digest
- Style, Factors, And Data Products
- Technical Moat And Product Logic
- Documents, Tables, And Output Files
- Broad Market Research Helpers
- Non-Investment Generated Skills
- Routing Patterns

## Entry And Backbone

| Skill | Role inside the master framework | Boundary |
|---|---|---|
| `user-investment-framework` | Master entrypoint, research logic, evidence discipline, ranking structure, and final output shape. | Does not fetch all data by itself. |
| `industry-research-router` | Legacy project router and compatibility layer for existing task categories. | Supporting router only; do not let it override the master framework. |
| `deep-research` | Long-form source map, evidence grading, contradiction handling, and synthesis plan. | Not a local Gemini API executor. |
| `20-andruia-niche-intelligence` | Optional background framing for non-semiconductor niche markets. | Reference framing only unless the domain truly needs it. |

## AI Chain And Semiconductor

| Skill | Use When | Boundary |
|---|---|---|
| `semiconductor-ai-chain-investment-researcher` | AI/semiconductor segment priority, bottlenecks, overseas leaders, A-share hard-evidence mapping. | Start from segment universe, not stock names. |
| `ai-chain-research-orchestrator` | Current AI-chain evidence, Grok/X discovery, Gemini source gaps, rumor discipline. | Evidence coordinator, not final stock selector. |
| `browser-grok-gemini-research` | Logged-in Chrome collection for Grok/X or Gemini webpages. | Collector only; Codex verifies and concludes. |

Before loading companion skills for AI data-center or semiconductor-chain bottleneck and stock-mapping tasks, consult `references/ai-chain-node-taxonomy.md` when the task needs exact node selection. It is a local node map for Level 3 / Level 4 P0 granularity and P5 search hints; it is not evidence for demand, supply gaps, pricing, or listed-company exposure.

## Industry Chain, Bottlenecks, And Competition

| Skill | Use When | Boundary |
|---|---|---|
| `industry-chain-deep-disassembly` | Terminal demand, topology, BOM/value nodes, supply-gap bottlenecks, future migration, HHI support tests. | Stock mapping is optional and only after node diagnosis. |
| `competitive-landscape` | True leader vs concept follower, Porter-style structure, differentiation. | Must stay at exact market or node level. |
| `competitive-intel` | Competitor moves, positioning, battlecards, market tracking. | Useful for context; not hard financial evidence by itself. |
| `apify-competitor-intelligence` | External competitor strategy, ads, pricing, positioning collection. | Use only when web/platform scraping adds evidence. |

## Company And Stock Research

| Skill | Use When | Boundary |
|---|---|---|
| `stock-fundamental-moat-triad` | Future highlight, inflection point, value-chain position, downstream demand path, international peers, customer certification. | Pre-valuation and future-first; must not analyze a company in isolation from upstream/downstream demand. |
| `stock-evaluator` | Company-level fundamental quality, earnings elasticity, trading elasticity, valuation, risks. | Requires verified chain position, downstream demand pass-through, and current data when needed. |
| `business-analyst` | Business model, KPI logic, unit economics, strategy, operating indicators. | Supplements company research; must connect operating indicators to downstream demand. |
| `earnings-call-investment-analyst` | Earnings release, guidance, conference call, expectation gap, post-earnings reaction. | Use original sources or transcripts where possible. |

## Event-Driven Alpha And Financial Translation

| Skill | Use When | Boundary |
|---|---|---|
| `serenity-alpha` | Market-moving news, product launches, technology breakthroughs, procurement/order signals, supply-chain changes, price changes, earnings-call clues, or "news to financial statement" questions where the user wants small-cap elasticity, market misclassification, validation metrics, and conditional posture. | Hypothesis translation only. It does not verify demand, prove beneficiary status, fetch current prices/market caps, replace filings or official evidence, or make final recommendations. Use source and market-data skills before naming securities or ranking. |

Preferred sequence: collect and grade evidence -> use `serenity-alpha` to translate observable demand into financial lines and validation checkpoints -> use `stock-evaluator` / `advanced-evaluation` / market-data skills for final ranking and risk.

## Public Equity Investing Plugin Workflows

Use Public Equity Investing plugin skills only as companion PM workflow layers. The project still owns source verification, industry-chain mapping, downstream-demand transmission, core-product price/unit-economics checks, true-beneficiary proof, and the final fundamental-quality / earnings-elasticity / trading-elasticity ranking.

Do not route generic company research, share-price questions, or industry-chain learning directly into the plugin router. Start with `user-investment-framework`; add the smallest Public Equity Investing skill only when the task has a clear listed-equity PM workflow.

| Plugin skill | Use when | Boundary |
|---|---|---|
| `Public Equity Investing:thesis-tracker` | The user wants to maintain a thesis over time, update a watch/holding thesis after new evidence, define KPI thresholds, kill criteria, action thresholds, or an append-only evidence ledger. | Not first-pass research, not a news summary, not a replacement for `a-share-company-tracking` durable state. |
| `Public Equity Investing:catalyst-calendar` | The user wants upcoming or historical catalysts organized by date, next proof point, source status, and monitoring action. | Calendar only; use `event-driven-analyzer` for full probability/payoff underwriting. |
| `Public Equity Investing:event-driven-analyzer` | A dated event controls the public-equity setup: merger, spin, split-off, activism, regulatory/litigation decision, tender, index event, lockup, rights offering, or other special situation. | Not generic `news -> financial statement` work; use `serenity-alpha` first for broad news-driven alpha translation. |
| `Public Equity Investing:earnings-preview` | Before results, the user wants expectation bar, KPI focus, guidance credibility, scenario setup, or call questions. | Not post-results analysis; keep official/company sources first. |
| `Public Equity Investing:earnings-deep-dive` | After results, guidance, transcript, or call commentary, the user wants what changed, estimate/model impact, scenario change, and action gates. | Does not replace `earnings-call-investment-analyst` source hierarchy, status fields, or official-vs-third-party transcript labeling. |
| `Public Equity Investing:scenario-sensitivity-generator` | A base case, model, thesis, catalyst, or event needs scenario skew, sensitivities, breakpoints, and PM action thresholds. | Not first-pass model building and not a license for false precision when assumptions are unsupported. |
| `Public Equity Investing:portfolio-risk-management` | After a thesis exists, the user wants position sizing, hedge alternatives, retained exposure, size-down/no-hedge comparison, liquidity/exit posture, or add/trim/exit rules. | Not thesis construction, not trade execution, not personal investment advice, and not credit-instrument hedge work. |
| `Public Equity Investing:financials-normalizer` | Public-company financials need normalization from source materials before analysis or model updates. | Not private data-room cleanup and not non-financial data cleanup. |
| `Public Equity Investing:equity-model-update` | A public-company Excel model copy needs source-to-model updates with logs and support files. | Not pure earnings notes and not broad workbook audits. |
| `Public Equity Investing:model-audit-tieout` | Existing public-equity models or spreadsheets need formula/source/tie-out audit. | Not new model building from scratch. |
| `Public Equity Investing:comps-valuation` | Peer selection, multiple analysis, implied price, refreshable comps table, or comps workbook QA is needed after the investment thesis is already grounded. | Not DCF-only work and not generic market commentary. |
| `Public Equity Investing:dcf-model-builder`, `Public Equity Investing:three-statement-model-builder` | The user explicitly asks for DCF or three-statement operating model workbooks for a public company. | Not a substitute for upstream/downstream demand proof or current source collection. |
| `Public Equity Investing:memo-builder`, `Public Equity Investing:long-short-pitch`, `Public Equity Investing:company-tearsheet`, `Public Equity Investing:deck-report-qc` | The user asks to package or review an already-supported idea as a memo, long/short pitch, tearsheet, or report/deck QC pass. | Output packaging only; do not use to create conviction before evidence and ranking work. |

Preferred sequences:

- Thesis maintenance: `user-investment-framework` -> source/market-data skills -> `stock-fundamental-moat-triad` / `stock-evaluator` -> `Public Equity Investing:thesis-tracker`.
- Catalyst monitoring: `user-investment-framework` -> source skills -> `Public Equity Investing:catalyst-calendar`; if payoff math matters, add `Public Equity Investing:event-driven-analyzer`.
- Earnings work: `user-investment-framework` -> `earnings-call-investment-analyst` -> `Public Equity Investing:earnings-preview` before results or `Public Equity Investing:earnings-deep-dive` after results.
- Scenario and sensitivity: `user-investment-framework` -> `stock-evaluator` / `advanced-evaluation` -> `Public Equity Investing:scenario-sensitivity-generator`.
- Position and risk: `user-investment-framework` -> verified thesis and current market data -> `Public Equity Investing:portfolio-risk-management`.
- Model and workbook: `user-investment-framework` -> source skills -> `spreadsheet` / `xlsx-official` -> `Public Equity Investing:financials-normalizer` / `equity-model-update` / `model-audit-tieout`.
- Formal packaging: `user-investment-framework` -> evidence/ranking complete -> `Public Equity Investing:memo-builder` / `long-short-pitch` / `company-tearsheet` / `deck-report-qc`.

Do not let plugin artifact defaults force a full HTML report, workbook, or deck for quick project answers unless the user asks for that output. When the user explicitly requests a model, tracker, memo, pitch, tearsheet, or report, follow the owning plugin skill's artifact rules after the route is selected.

## A-Share Tracking And Disclosure

| Skill | Use When | Boundary |
|---|---|---|
| `a-share-company-tracking` | Watchlist baselines, state/events maintenance, daily updates, durable company records. | Tracking layer, not final investment conclusion. |
| `a-share-disclosure-trading-data` | CNINFO, exchange announcements, IR records, dragon-tiger lists, block trades, T/T+1 evening windows. | Evidence and trading-event layer only. |

## Market Data And Trading Context

| Skill | Use When | Boundary |
|---|---|---|
| `allstock-data` | China A-share, HK, and US quick quotes, K-lines, order book, China market data. | Market context; cannot prove beneficiary status. |
| `finance` | Broad stocks, ETFs, indices, FX, crypto where available, US company facts with provider fallbacks. | Supplemental data source. |
| `stocks` | Yahoo Finance prices, fundamentals, earnings, dividends, options, news. | Overseas market-data support. |
| `yfinance-mcp-server` | Overseas prices, history, financials, options, dividends, news, screeners. | Not proof of original company facts. |
| `alpha-vantage` | Global market data, macro, fundamentals, indicators. | Use when its official API coverage helps. |
| `banana-farmer` | Momentum, RSI, volatility, technical risk, trading scans. | Trading-elasticity supplement only after exposure is established. |
| `stock-data-skill` | Simplywall.st supplemental stock data. | Supplemental only after official and project data sources. |
| `stock-copilot-pro` | Optional QVeris/OpenClaw quotes, fundamentals, technicals, news radar, sentiment. | Do not import scheduled briefs or default recommendations. |

## HTSC Plugin Tools

Use the HTSC skills as data, candidate-generation, external-watchlist, or simulated-trading tools inside the master framework. They do not replace source verification, industry-chain mapping, downstream demand transmission, true-beneficiary checks, or the final three-layer ranking.

For individual-stock research, HTSC output is supplemental only. Do not use it to skip the upstream/downstream map, downstream demand bridge, core-product demand and price/unit-economics check, official filings, customer/supplier evidence, or structured historical market-data checks. The tested HTSC plugin paths do not provide a stable structured historical OHLCV series, so they are not the primary source for deep historical行情, VCP pattern analysis, factor research, or backtesting.

Tested behavior to remember:

- `query-indicator` returns natural-language or Markdown `answer` content, not a stable structured time-series API. It can answer latest/recent indicators and short historical point/table questions, but row completeness and schema are not guaranteed.
- `a-share-paper-trading.getQuote` is structured but sparse. Off-market tests returned fields such as `stockName`, `currentPrice`, `prevClose`, `limitUp`, `limitDown`, `change`, and `isSuspended`; first bid/ask may appear in some sessions, but open/high/low/volume/amount/time and full order book are not guaranteed.
- `select-stock` can rewrite or relax impossible screening conditions. Treat output as discovery, not a strict executable screen.
- `financial-analysis` can produce useful market or stock context, but may include investment-style conclusions. Keep it as external context and verify facts.
- `financial-analysis.investCalendar` timed out in tests, so do not make it a default route.
- `watchlist-management` and `a-share-paper-trading` can change external HTSC state or simulated account state. Use write actions only after explicit user instruction.

| Skill | Appropriate use | Unsuitable use | Output handling |
|---|---|---|---|
| `query-indicator` | A-share latest/recent price action, PE/PB, turnover, volume, transaction amount, financial indicators, short historical point checks, and multi-stock indicator comparison. | Primary historical OHLCV warehouse, factor research, VCP pattern analysis, backtesting, or official company-fact proof. | Timestamp the answer, quote only as supplemental market/indicator data, and verify hard claims elsewhere. |
| `select-stock` | Natural-language screening for an initial stock/ETF/fund candidate pool, including industry, valuation, financial, technical, fund-flow, performance, or combined conditions. | Final recommendations, strict auditable screen results, true-beneficiary proof, or replacing project ranking. | Re-run project research and `advanced-evaluation` before ranking or acting on candidates. |
| `financial-analysis` | Quick market, sector, individual-stock, fund, ETF, news, sentiment, or diagnosis context; use `marketInsight`, `diagnosisStock`, and news-style analysis as supplementary views. | Final thesis, causal explanation, ranking, buy/sell language, or replacement for official filings and demand-chain evidence. | Label as external HTSC context and independently verify important claims. |
| `watchlist-management` | Query or explicitly add stocks to the HTSC external watchlist service when the user asks for HTSC/self-selected stocks. | Repository `watchlists/*.xlsx`, durable `a-share-company-tracking` state, or automatic watchlist synchronization. | Keep HTSC watchlist state separate from project records; never write without explicit instruction. |
| `a-share-paper-trading` | Explicit simulated A-share operations: search stocks, sparse quote, account balance, positions, pending orders, trade history, simulated orders, and cancellations. | Live trading, primary real-time quote provider, primary historical data source, or unrequested order/cancel actions. | Treat quotes as sparse supplemental data; place/cancel simulated orders only when requested. |

## Source Discovery And Evidence Digest

| Skill | Use When | Boundary |
|---|---|---|
| `search-specialist` | Query design, official-source priority, contradiction tracking, source credibility. | Search strategy and evidence trail; not final conclusion. |
| `research-summarizer` | Filings, reports, PDFs, whitepapers, transcripts, multi-source evidence briefs. | Digest claims and limitations before synthesis. |
| `web-scraper` | General page extraction, content comprehension, structured metadata. | Extractor only. |
| `firecrawl-scraper` | Deep crawl, page extraction, screenshot, PDF parsing. | Use when crawl/extract depth matters. |
| `tavily-web` | Filtered search, extract, research API with citations. | Optional source coverage tool. |
| `finance-news` | Market-news briefings, alerts, delivery workflows. | Use only when explicitly requested; not default research route. |

## Style, Factors, And Data Products

| Skill | Use When | Boundary |
|---|---|---|
| `advanced-evaluation` | Rubrics, score consistency, bias control, three-layer investment ranking. | Does not replace domain judgment or source verification. |
| `multi-factor-strategy` | Factor universe, rebalance rules, risk controls, YAML strategy configuration. | Needs explicit factor and validation design. |
| `data-scientist` | Data analysis, predictive modeling, business intelligence. | Use for data tasks, not narrative-only research. |
| `senior-data-scientist` | Statistical rigor, causality, experiments, robustness checks. | Use when statistical proof or model validation matters. |
| `dividend-premium-tracker` | China high-dividend, low-volatility, stock-bond yield spread context. | Style/macro backdrop, not individual-stock proof. |

## Technical Moat And Product Logic

| Skill | Use When | Boundary |
|---|---|---|
| `ai-engineer` | AI infrastructure, RAG, agents, inference stack, technical feasibility. | Technical support for moat analysis. |
| `ai-ml` | ML workflow, LLM application, ML pipeline, AI features. | Technical support only. |
| `ai-product` | Whether an AI product is commercially real or only a demo. | Product-quality lens. |
| `tech-stack-evaluator` | Technology stack moat, TCO, ecosystem, migration path. | Helps judge technical defensibility. |
| `cto-advisor` | Architecture, technical strategy, engineering metrics, tech-debt context. | Technical strategy support. |
| `senior-architect` | System architecture, dependencies, scalability, architecture decisions. | Use for architecture-level moats. |
| `arm-cortex-expert` | Embedded, MCU, firmware, ARM Cortex technical topics. | Use for edge/chip/firmware-specific questions. |
| `product-manager` | Customer workflow, adoption barriers, product-market fit. | Commercial adoption lens. |
| `product-manager-toolkit` | Discovery, PRD, RICE, go-to-market, user research synthesis. | Product/process output support. |

## Documents, Tables, And Output Files

| Skill | Use When | Boundary |
|---|---|---|
| `spreadsheet` | Read/write/analyze tabular data with schema memory. | Use when table or workbook manipulation matters. |
| `xlsx` | Spreadsheet file is primary input/output. | Use for `.xlsx`, `.xlsm`, `.csv`, `.tsv` operations. |
| `xlsx-official` | Excel formulas, formatting, charts, structured workbook analysis. | Preserve workbook formatting and recalculation. |
| `docx` | Word document output or editing. | Not for spreadsheet/PDF work. |
| `pdf` | PDF extraction, creation, splitting, merging, OCR, forms. | Use for PDF files. |
| `pptx` | Slide deck creation, reading, editing, templates. | Use whenever `.pptx` is involved. |

## Broad Market Research Helpers

| Skill | Use When | Boundary |
|---|---|---|
| `apify-market-research` | Geographic market conditions, pricing, consumer behavior, product validation. | Broad market research, not securities proof. |

## Non-Investment Generated Skills

| Skill | Location | Boundary |
|---|---|---|
| `typer` | Python virtual environments under `.venv_earnings_asr` and `artifacts/*/.venv_asr` | Generated dependency skill for Typer CLI usage. Do not route investment research through it. Use only if the user asks to edit or inspect CLI code that explicitly depends on Typer. |

## Routing Patterns

| User request | Start with | Add only if needed |
|---|---|---|
| Learn an industry chain | `user-investment-framework` | `industry-chain-deep-disassembly`, `deep-research`, adapter/source skills |
| AI/semiconductor stock mapping | `user-investment-framework` | `semiconductor-ai-chain-investment-researcher`, current-evidence skills, market-data skills |
| Single stock evaluation | `user-investment-framework` | `stock-fundamental-moat-triad`, `industry-chain-deep-disassembly` for upstream/downstream demand, `stock-evaluator`, market-data/source skills |
| News-driven alpha / small-cap elasticity | `user-investment-framework` | `search-specialist` or current-evidence skills first, then `serenity-alpha`, `allstock-data`, `advanced-evaluation` |
| Dated event with probability/payoff | `user-investment-framework` | source skills, `serenity-alpha` if event came from news, then `Public Equity Investing:event-driven-analyzer` |
| Thesis tracker or kill criteria | `user-investment-framework` | `a-share-company-tracking`, source/market-data skills, then `Public Equity Investing:thesis-tracker` |
| Catalyst calendar | `user-investment-framework` | source skills, `a-share-company-tracking`, then `Public Equity Investing:catalyst-calendar` |
| Pre/post earnings PM workflow | `user-investment-framework` | `earnings-call-investment-analyst`, then `Public Equity Investing:earnings-preview` or `Public Equity Investing:earnings-deep-dive` |
| Scenario sensitivity or action thresholds | `user-investment-framework` | `stock-evaluator`, `advanced-evaluation`, then `Public Equity Investing:scenario-sensitivity-generator` |
| Position sizing or hedge plan | `user-investment-framework` | verified thesis, current market data, then `Public Equity Investing:portfolio-risk-management` |
| "Who has most elasticity?" | `user-investment-framework` | `allstock-data`, `banana-farmer`, `advanced-evaluation` |
| Official evidence search | `user-investment-framework` | `search-specialist`, scraper/extract skills, `research-summarizer` |
| A-share watchlist update | `user-investment-framework` | `a-share-company-tracking`, `a-share-disclosure-trading-data` |
| Earnings-call analysis | `user-investment-framework` | `earnings-call-investment-analyst`, market-data/source skills |
| Model audit, model update, or normalized financials | `user-investment-framework` | `spreadsheet`/`xlsx-official`, then `Public Equity Investing:financials-normalizer`, `Public Equity Investing:equity-model-update`, or `Public Equity Investing:model-audit-tieout` |
| Report or workbook output | `user-investment-framework` | `spreadsheet`/`xlsx`/`docx`/`pptx`/`pdf` according to artifact; add Public Equity Investing packaging skills only for formal memo/pitch/tearsheet/QC requests |
