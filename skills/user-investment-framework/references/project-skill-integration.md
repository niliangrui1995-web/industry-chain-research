# Project Skill Integration Map

Use this reference when `user-investment-framework` needs to choose companion skills for a non-trivial investment research task.

Rule: start with `user-investment-framework`; load the smallest useful supporting set; preserve each supporting skill's boundary.

## Contents

- Entry And Backbone
- AI Chain And Semiconductor
- Industry Chain, Bottlenecks, And Competition
- Company And Stock Research
- A-Share Tracking And Disclosure
- Market Data And Trading Context
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
| "Who has most elasticity?" | `user-investment-framework` | `allstock-data`, `banana-farmer`, `advanced-evaluation` |
| Official evidence search | `user-investment-framework` | `search-specialist`, scraper/extract skills, `research-summarizer` |
| A-share watchlist update | `user-investment-framework` | `a-share-company-tracking`, `a-share-disclosure-trading-data` |
| Earnings-call analysis | `user-investment-framework` | `earnings-call-investment-analyst`, market-data/source skills |
| Report or workbook output | `user-investment-framework` | `spreadsheet`/`xlsx`/`docx`/`pptx`/`pdf` according to artifact |
