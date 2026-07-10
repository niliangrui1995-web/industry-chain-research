# Skill And MCP Boundary Matrix

Use this matrix when integrating, pruning, auditing, or routing the `产业链投研` skill library. It covers project-local skills plus account-level plugin/MCP capabilities that can influence this repository's research workflow.

Status labels:

- `default`: safe to route when the task clearly matches.
- `companion`: load after the master framework selects the task.
- `optional`: use only when it adds specific data, source coverage, or artifact handling.
- `explicit`: use only when the user explicitly asks or when the task would otherwise be impossible.
- `write-gated`: can change external state; requires explicit user instruction.
- `reference`: keep as reference or legacy compatibility, not a default execution route.

Evidence labels:

- `confirmed_official`: original filings, exchange announcements, company IR, prospectus, official customer/supplier material.
- `credible_secondary`: reputable data vendor, industry association, credible media with named sources.
- `market_data_vendor`: quote, valuation, trading, fund, macro, or vendor data.
- `secondary_trading_context`: concept labels, limit-board reasons, sentiment, market attention, model/vendor summaries.
- `lead_only`: search or hypothesis lead that needs verification.
- `artifact`: document, table, dashboard, or file creation capability.

## Project-Local Skills

| Skill | Status | Boundary |
|---|---|---|
| `user-investment-framework` | default | Master route, evidence hierarchy, demand bridge, bottleneck logic, three-layer ranking. Does not fetch all data by itself. |
| `industry-research-router` | companion | Compatibility route matrix after the master framework. Does not override `user-investment-framework`. |
| `deep-research` | companion | Long research plan, source map, evidence grading, contradiction handling. Not a Gemini/API executor. |
| `semiconductor-ai-chain-investment-researcher` | companion | AI/semiconductor segment priority, bottlenecks, overseas leaders, A-share hard-evidence mapping. Start from node, not stock name. |
| `ai-chain-research-orchestrator` | companion | Current AI-chain evidence coordination, Grok/X and Gemini collection discipline. Collector/coordinator only. |
| `browser-grok-gemini-research` | explicit | Logged-in Chrome collection for Grok/X/Gemini. Web model output is `lead_only` until verified. |
| `industry-chain-deep-disassembly` | companion | Terminal demand, topology, BOM/value nodes, supply-gap bottlenecks, future migration. Stock mapping only after node diagnosis. |
| `competitive-landscape` | companion | Market structure, differentiation, true leader vs concept follower. Must stay at exact market/node level. |
| `competitive-intel` | optional | Competitor moves, positioning, battlecards, tracking. Context, not hard financial evidence. |
| `apify-competitor-intelligence` | optional | Competitor platform scraping through Apify. Requires `APIFY_TOKEN`; external evidence is `lead_only` or `credible_secondary` after source review. |
| `business-analyst` | companion | Business model, KPI, unit economics, operating indicators. Must connect to demand and financial result. |
| `product-manager` | optional | Buyer workflow, adoption barriers, product-market fit. Product logic support only. |
| `product-manager-toolkit` | optional | PRD, RICE, discovery, GTM templates. Useful for product artifacts, not securities proof. |
| `stock-fundamental-moat-triad` | companion | Future highlight, downstream demand, value-chain migration, international peers, customer certification. Pre-valuation thesis layer. |
| `stock-evaluator` | companion | Fundamental quality, earnings elasticity, trading elasticity, valuation, risks. Requires verified chain/source context. |
| `serenity-alpha` | companion | News/event to financial-statement hypothesis, small-cap elasticity, misclassification. Hypothesis layer; needs evidence and market-data validation. |
| `earnings-call-investment-analyst` | companion | Earnings releases, guidance, transcripts, expectation gap. Prefer original company materials. |
| `a-share-company-tracking` | companion | Watchlist baselines, daily updates, durable state/events, completion table. Tracking layer, not final conclusion. |
| `a-share-disclosure-trading-data` | companion | CNINFO, exchange announcements, IR, dragon-tiger list, block trades, T/T+1 windows. Evidence/trading-event layer. |
| `search-specialist` | companion | Query design, official-source priority, contradiction tracking. Search strategy, not conclusion. |
| `research-summarizer` | companion | Digest filings, reports, PDFs, transcripts, multi-source evidence. Produces claim/evidence/limitations. |
| `firecrawl-scraper` | optional | Firecrawl API crawl/extract/PDF/screenshot. Requires API key; external extraction layer only. |
| `tavily-web` | optional | Tavily Search/Extract/Research. Requires `TAVILY_API_KEY`; use after `search-specialist` when it adds coverage. |
| `apify-market-research` | optional | Apify Actors for market, pricing, consumer, geography. Requires `APIFY_TOKEN`; not securities proof. |
| `advanced-evaluation` | companion | Rubrics, scoring consistency, bias checks, three-layer ranking sanity. Does not replace domain judgment. |
| `spreadsheet` | optional | General table read/write/analysis with formatting awareness. Artifact/data handling. |
| `xlsx` | optional | Spreadsheet file input/output. Use when `.xlsx`, `.xlsm`, `.csv`, or `.tsv` is the deliverable. |
| `xlsx-official` | optional | Excel formulas, formatting, charts, structured workbook. Preserve formatting and recalc. |
| `multi-factor-strategy` | optional | Factor strategy YAML/config design. Needs explicit universe, factors, rebalance, validation. |
| `data-scientist` | optional | Data analysis, modeling, BI. Data task support, not narrative investment proof. |
| `senior-data-scientist` | optional | Statistics, causality, experiments, robustness. Use for proof/validation tasks. |
| `docx` | optional | Word document creation/editing/extraction. Artifact layer. |
| `pdf` | optional | PDF read, split, merge, OCR, forms, extraction. Artifact/source layer depending on task. |
| `pptx` | optional | Slide deck creation/editing/reading. Artifact layer. |
| `ai-engineer` | optional | AI infrastructure, RAG, agent, inference-stack technical judgment. Technical moat support. |
| `ai-ml` | optional | ML workflows and AI features. Technical support only. |
| `ai-product` | optional | AI product commercial reality and product quality. Product lens only. |
| `tech-stack-evaluator` | optional | Technology stack moat, TCO, ecosystem, migration path. Technical defensibility support. |
| `cto-advisor` | optional | Architecture and technical strategy. Engineering context, not financial evidence. |
| `senior-architect` | optional | System architecture, dependencies, scalability. Technical moat support. |
| `arm-cortex-expert` | optional | ARM/MCU/firmware/edge computing. Use for embedded/chip technical questions. |
| `ht-local-market-data` | optional | Read-only local `C:\zd_huatai` HT/TongdaXin data inspector for post-close A-share `.day` K-lines, unavailable `.lc1` checks, `vipdoc\cw` financial packages, `T0002\blocknew` pools, and `hq_cache` vendor tables. Labels: `market_data_vendor` and `secondary_trading_context`; never official evidence; do not inspect trading-account/password/order/log details unless explicitly requested. |
| `allstock-data` | optional | Tencent/adata style CN/HK/US quote/K-line/order-book data. `market_data_vendor`; cannot prove beneficiary status. |
| `finance` | optional | Yahoo/Financial Datasets/TwelveData/Alpha Vantage style quotes, FX, US company data. `market_data_vendor`; cache/watchlist files are created only on explicit write paths; verify hard claims elsewhere. |
| `alpha-vantage` | optional | Alpha Vantage official API. Requires `ALPHAVANTAGE_API_KEY`; respect rate limits and terms. |
| `banana-farmer` | optional | Momentum, RSI, volatility, technical-risk scans. Requires `BF_API_KEY`; trading elasticity only. |
| `stock-copilot-pro` | explicit | QVeris/OpenClaw quotes, fundamentals, technicals, news, sentiment. Requires `QVERIS_API_KEY`; local evolution writes are disabled by default; no default actionable conclusions, briefs, pushes, or cron in this repo. |
| `finance-news` | explicit | News briefings, alerts, delivery workflows. Do not route ordinary research here by default; use only when the user explicitly asks for briefings, alerts, or delivery. |
| `dividend-premium-tracker` | companion | Dividend/low-volatility style and stock-bond yield context. Does not prove stock payout durability. |

## Removed From Project-Local Routing

| Skill | Reason |
|---|---|
| `20-andruia-niche-intelligence` | Global routing marks it archived, and its original framing does not fit this repo's current evidence-first industry-chain workflow. |
| local `web-scraper` | Duplicate of the installed global `web-scraper`; keep the capability as a global fallback instead of maintaining a local copy. |
| `stocks` | Local runtime is broken in the current workspace and overlaps with `finance`, `alpha-vantage`, iFinD global stock, and official filings. |
| `yfinance-mcp-server` | Installer/setup skill only; no active MCP surface is enabled for this project. Reinstall separately only on explicit request. |
| `stock-data-skill` | SimplyWallSt URL smoke test fails and the global health registry already archives it. Do not route project work here. |

## Account-Level Finance MCP And Plugin Skills

| Capability | Status | Tool or skill surface | Boundary |
|---|---|---|---|
| TongdaXin TDX | optional | `tdx-finance-data`, `mcp__tdx.tdx_wenda_quotes` | A-share/HK/fund/index/sector natural-language market data. Single subject per call. Labels: `market_data_vendor`, `secondary_trading_context`. Not official evidence. |
| iFinD A-share stock | optional | `ifind-finance-data`, `get_stock_summary`, `search_stocks`, `get_stock_performance`, `get_stock_info`, `get_stock_shareholders`, `get_stock_financials`, `get_risk_indicators`, `get_stock_events`, `get_esg_data`, `stock_highfreq_quotes` | Structured A-share data, screening, finance, events, high-frequency snapshots. Vendor data; official claims still need source documents. |
| iFinD fund | optional | `get_fund_profile`, `get_fund_financials` and related fund tools when exposed | Fund profile, financials, ownership/portfolio/performance when available. Vendor data; verify fund reports for official holdings. |
| iFinD EDB | optional | `get_edb_data` | Macro, industry, commodity, production/price/inventory time series. Use for demand/background; cite as vendor data. |
| iFinD news/notice | optional | `search_news`, `search_notice` | News and announcement snippets. Snippets are leads; retrieve original notice or company filing before hard claims. |
| iFinD bond | optional | `bond_basic_info`, `bond_market_data`, `bond_financial_data` | Bond and issuer data. Use for credit/context tasks, not default equity research. |
| iFinD global stock | optional | `global_stock_profile`, `global_stock_quotes`, `global_stock_financial`, `global_stock_events` | HK/US/global profile, quotes, financials, events. Vendor data; filings remain official source. |
| iFinD index/sector | optional | `index_data`, `sector_data`, `index_highfreq_quotes` | Index/sector quote, valuation, breadth, high-frequency snapshot. Market context. |
| HTSC `query-indicator` | optional | plugin skill | Fast A-share indicators and short point checks. Natural-language output, not stable OHLCV warehouse. |
| HTSC `select-stock` | optional | plugin skill | Candidate discovery from conditions. Candidate list only; not recommendation or proof. |
| HTSC `financial-analysis` | optional | plugin skill | Quick market/stock/news diagnosis. External context; verify facts and ignore unverified conclusions. |
| HTSC `watchlist-management` | write-gated | plugin skill | External HTSC watchlist query/add. Keep separate from repo watchlists; write only on explicit instruction. |
| HTSC `a-share-paper-trading` | write-gated | plugin skill | Simulated A-share quote/account/order/cancel/history. Never live trading; order/cancel only when explicit. |
| DFCF Miaoxiang `mx-data` | optional | plugin skill | Eastmoney Miaoxiang data. Requires `MX_APIKEY`; vendor data/context. |
| DFCF Miaoxiang `mx-search` | optional | plugin skill | Financial news/notice/report/policy search. Search layer; verify originals. |
| DFCF Miaoxiang `mx-xuangu` | optional | plugin skill | Intelligent stock screening. Candidate layer only. |
| DFCF Miaoxiang `mx-zixuan` | write-gated | plugin skill | External watchlist management. Write only on explicit instruction. |
| DFCF Miaoxiang `mx-moni` | write-gated | plugin skill | Simulated portfolio and orders. Write/trade actions only on explicit instruction. |
| Tiantian Fund `ttfund-ttskill` | explicit | plugin skill | Tiantian Fund account/fund/portfolio/trading-style operations. Account state and trading-related actions require explicit instruction. |
| Alpaca | explicit | `mcp__codex_apps__alpaca` | US market data and possibly trading-account-style surfaces. Use only when user asks or project needs supported Alpaca data; confirm any write/trade action. |

## General MCP Surfaces Visible In This Thread

| MCP / plugin | Status for this project | Boundary |
|---|---|---|
| Browser / Chrome / `node_repl` | optional | Use for logged-in Grok/Gemini/website workflows and screenshots when needed. Web model output stays `lead_only`. |
| Global `web-scraper` skill | optional | General page extraction fallback when installed. Extractor only; use after source-priority planning. |
| Computer Use | explicit | Use only when browser/automation cannot reach the needed UI or user asks. |
| Data Analytics `datascienceWidgets` | explicit | Use for rendered reports/dashboards only when the user requests a dashboard/report artifact. |
| Cloudflare | explicit | Deployment/publishing only, not research. |
| Codex Security | explicit | Security scans only. Not part of normal investment research. |
| OpenAI key local confirmation | explicit | API-key setup only. Not part of research. |
| GitHub / Google Drive / Gmail / Calendar / Notion | explicit | Use only when the user asks for those connected services or source files live there. |
| Creative Production / Product Design / HeyGen / Hyperframes / build-* plugins | explicit | Creative or app-building work only. Not part of default investment research. |
| Pencil / Antigravity MCP | explicit | IDE integration only. Not research evidence. |

## Default Routing Rules

1. Start with `user-investment-framework`.
2. Use project-local source skills before external API search when official evidence can be found directly.
3. Use TDX for fast A-share trading context, iFinD for structured financial data, and `ht-local-market-data` for the user's refreshed local `C:\zd_huatai` daily files or block pools when the task needs current or vendor data.
4. Use TDX/iFinD/HTSC/DFCF/`ht-local-market-data` outputs as vendor data or leads unless the tool returns or links to original official documents.
5. Split official-evidence tasks from market-reaction tasks. The first goes to `search-specialist` / `a-share-disclosure-trading-data`; the second can use TDX/iFinD/HTSC/`ht-local-market-data`/market-data helpers.
6. Write-capable external state needs explicit user instruction, even when the skill itself is installed and enabled.
7. Do not import scheduled-brief, alert, delivery, cron, watchlist-sync, or simulated-trading workflows into this project by default.
