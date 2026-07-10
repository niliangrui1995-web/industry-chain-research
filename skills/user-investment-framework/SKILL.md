---
name: user-investment-framework
description: >-
  Primary project-local entrypoint for all investment research in 产业链投研. Use first for any industry-chain, sector, supply-chain, upstream/downstream map, downstream demand transmission, company, individual-stock, A-share, HK, US, Japan, Korea, Taiwan, valuation, announcement, filing, earnings, market-data, watchlist, dividend, technology-moat, domestic-substitution, global-leader, true-beneficiary-vs-concept, trading-elasticity, spreadsheet, or research-output request. Also trigger on 我的投资框架, 我的研究框架, 投资逻辑, 产业链研究, 上下游, 下游需求, 需求传导, 个股研究, 行业研究, 公司对比, 股票弹性, 业绩弹性, 基本面排序, 交易弹性排序.
---

# User Investment Framework

## Role

Use this as the first loaded project skill for investment research. It is the user's master framework and orchestration layer. Other project skills are supporting capabilities selected from this framework, not competing entrypoints.

Core lens:

```text
terminal demand -> downstream application/customer demand -> industry-chain topology -> BOM/value node -> demand-vs-qualified-supply gap -> bottleneck mechanism -> global leader validation -> listed-company hard-evidence mapping -> three-layer ranking -> risks and tracking signals
```

This skill is a decision discipline, not a data source. It decides the research route, evidence standard, ranking logic, and final output shape, then loads only the smallest necessary companion skills.

## Companion Skill Map

For non-trivial routing or when choosing among project skills, read `references/project-skill-integration.md`. For a full per-skill and per-MCP boundary audit, read `references/skill-mcp-boundary-matrix.md`.

Default companion layers:

| Need | Companion skills |
|---|---|
| Legacy route alignment | `industry-research-router` |
| Long industry/company research | `deep-research`, `industry-chain-deep-disassembly` |
| AI/semiconductor chain | `semiconductor-ai-chain-investment-researcher`, `ai-chain-research-orchestrator`, `browser-grok-gemini-research` |
| Company fundamentals and downstream demand | `stock-fundamental-moat-triad`, `stock-evaluator`, `business-analyst`, `industry-chain-deep-disassembly` |
| Competitive landscape | `competitive-landscape`, `competitive-intel`, `apify-competitor-intelligence` |
| Source discovery and digestion | `search-specialist`, `research-summarizer`, `firecrawl-scraper`, `tavily-web`, global `web-scraper` fallback |
| News-to-alpha financial translation | `search-specialist` or current-evidence skills, then `serenity-alpha`, `allstock-data` / `tdx-finance-data`, `advanced-evaluation` |
| A-share tracking and disclosures | `a-share-company-tracking`, `a-share-disclosure-trading-data` |
| Earnings and guidance | `earnings-call-investment-analyst` |
| Market data and trading context | `TDX Finance Data:tdx-finance-data`, `tdx-finance-data`, `ht-local-market-data`, `ifind-finance-data`, iFinD MCPs, HTSC data skills, DFCF Miaoxiang skills, `allstock-data`, `finance`, `alpha-vantage`, `banana-farmer`, `stock-copilot-pro` |
| Scoring, factors, tables, workbooks | `advanced-evaluation`, `multi-factor-strategy`, `spreadsheet`, `xlsx`, `xlsx-official`, `data-scientist`, `senior-data-scientist` |
| Documents and deliverables | `docx`, `pdf`, `pptx` |
| Technical moat and product logic | `ai-engineer`, `ai-ml`, `ai-product`, `tech-stack-evaluator`, `cto-advisor`, `senior-architect`, `arm-cortex-expert`, `product-manager`, `product-manager-toolkit` |
| Dividend/defensive style | `dividend-premium-tracker` |
| Public-equity PM workflows | Public Equity Investing plugin skills after source evidence and issuer/security context are established |

Do not load every companion skill. Start here, classify the request, then load the smallest useful combination.

## External API And MCP Gate

Use this gate before any skill that calls a paid API, a remote MCP, logged-in browser account, external watchlist, simulated trading account, or quota-bound service.

1. Confirm the task really needs current or remote data.
2. Prefer official filings, exchange disclosures, company IR, annual/quarterly reports, and original customer/supplier sources for hard claims.
3. Use API/MCP tools as data support only unless their source is itself official.
4. Never hardcode, print, or copy API keys. Use environment variables or installed MCP/plugin configuration.
5. Keep read-only calls narrow. For TDX, query one stock, fund, index, sector/concept, or screen per call.
6. Write-capable actions such as HTSC watchlist changes or simulated orders require explicit user instruction.
7. If maintaining or changing an API skill, run a minimal read-only smoke test when credentials/tools are available. Use a subagent for independent deep testing when the API surface is broad or failure modes are unclear.

Evidence labels:

| Source type | Label | Use |
|---|---|---|
| Filings, announcements, exchange, company IR, prospectus, official customer/supplier source | `confirmed_official` | Hard evidence |
| Reputable data vendor, industry association, credible media with named source | `credible_secondary` | Support and cross-check |
| Market data vendors, quote APIs, TDX quote tables, Yahoo/Alpha Vantage/Financial Datasets | `market_data_vendor` | Price, valuation, liquidity, technical and timing context |
| TDX concept labels, limit-board reasons, social signals, Grok/X, Gemini, QVeris summaries, model output | `secondary_trading_context` or `lead_only` | Search leads and market attention, not proof |

## TDX Finance Data MCP Boundary

TDX Finance Data is the preferred A-share trading-context tool when the task asks for latest quote, valuation snapshot, turnover/liquidity, K-line-style recent price action, technical indicators, ETF/fund snapshot, index/sector quote, concept/industry constituent screen,涨停/跌停列表,封单,连板,板型,涨停原因 or原因揭秘.

Use native `mcp__tdx.tdx_wenda_quotes` when available. It is a natural-language table-returning MCP, not a strict multi-endpoint database. Keep each call to one subject, one sector/concept, one index, or one screen; split multi-stock comparisons into separate calls.

Never use TDX output as official company evidence. It cannot replace CNINFO, exchange announcements, company IR, annual/quarterly reports, customer/supplier proof, or original research reports. Treat TDX concept labels,涨停原因, and原因揭秘 as market-data-vendor or secondary trading context that can guide follow-up source checks.

For detailed tested boundaries and query patterns, read `references/tdx-finance-data-boundary.md`.

## HT Local Market Data Boundary

Use `ht-local-market-data` when a task explicitly needs the user's local `C:\zd_huatai` data or when a post-close local HT/TongdaXin snapshot is enough for A-share daily K-line, block-pool, vendor classification, or financial-package freshness checks.

Treat it as `market_data_vendor` for parsed `.day` daily OHLCV and `secondary_trading_context` for `T0002\blocknew` pools, concept labels, and vendor classifications. It is not live intraday data, not official disclosure, and not proof of beneficiary status. The tested root contains no `.lc1` minute files, so use TDX/iFinD/current web data for current intraday or minute-level tasks.

Do not read HT trading-account, password, order,委托, or log details unless the user explicitly asks for that diagnostic. Never write to `C:\zd_huatai` through this project route.

## Public Equity Investing Plugin Boundary

Public Equity Investing plugin skills are optional PM workflow layers inside this framework. They do not replace chain-first research, official-evidence hierarchy, downstream-demand bridge, core-product demand and price/unit-economics checks, or the final three-layer ranking.

Default sequence:

```text
project evidence and chain map -> company and earnings thesis -> scenario / catalyst / event / tracker / risk plugin workflow -> final project ranking or action posture
```

Use plugin skills only when the user asks for thesis trackers, catalyst calendars, dated event underwriting, earnings preview/deep-dive, scenario sensitivity, portfolio risk, public-equity model update/audit, formal memo, pitch, tearsheet, or deck/report QC.

Do not let plugin artifact defaults turn a quick answer into a full HTML report, workbook, deck, or memo unless the user asks for that output.

## AI Chain Node Taxonomy

For AI data-center, AI hardware, semiconductor-chain, and AI 产业链 tasks, use `references/ai-chain-node-taxonomy.md` as the local node map before selecting bottlenecks, comparing nodes, or mapping listed companies.

This taxonomy points to the cleaned Level 1-5 AI chain mind map in `docs/ai_chain_disassembly/`.

- Use Level 1 and Level 2 for chain-family orientation.
- Use Level 3 and Level 4 P0 as normal research, bottleneck, value-share, and company-mapping granularity.
- Use P5 summaries only as material, equipment, component, process, or search-keyword hints.
- Never treat the taxonomy itself as evidence for demand, orders, pricing, supply gaps, customer validation, or stock exposure.

## Unknown Stock Node Discovery Gate

For individual-stock or company prompts, do not assume the AI-chain node from the stock name. If the company's exact product, service, or value-chain exposure is not already known, run a short identity and exposure discovery step before using the AI chain taxonomy:

1. identify the listed entity, ticker, market, main business lines, and latest segment/product disclosure;
2. extract the specific products, services, materials, equipment, components, processes, or customer applications that may connect to AI data-center or semiconductor demand;
3. grade each exposure as `confirmed`, `partial clue`, `rumor only`, or `not found` using official filings, announcements, IR records, product pages, or credible primary-adjacent sources;
4. map only confirmed or partial-clue product terms to candidate Level 3 / Level 4 P0 taxonomy paths;
5. if no direct or partial AI-chain exposure is found, say the company is outside the current AI taxonomy scope or keep it as `theme_adjacent` / `watch`, not a main AI-chain candidate.

## Workflow

### 1. Classify The Real Task

Before answering, classify the request as one or more of:

- industry-chain learning or node disassembly;
- AI data-center or semiconductor-chain node lookup;
- upstream/downstream chain mapping and downstream demand transmission;
- current or future bottleneck diagnosis;
- technology moat, domestic substitution, or global leader comparison;
- true beneficiary vs concept stock filtering;
- individual-stock or peer-company fundamental research;
- earnings release, guidance, conference call, or expectation-gap analysis;
- announcement, CNINFO, exchange disclosure, IR record, dragon-tiger list, or block-trade verification;
- market-data, valuation, liquidity, or trading-elasticity check;
- watchlist, tracking state, scorecard, or Excel workbook update;
- report, slide, PDF, Word, or other output artifact.

### 2. Decide Whether Current Evidence Is Required

Use current tools or web evidence for any claim involving:

- latest price, market cap, PE/PB, turnover, volume, K-line, valuation, or liquidity;
- latest filings, earnings, orders, guidance, announcements, policy, regulation, or news;
- downstream capex, cloud/customer guidance, carrier bidding, shipment, utilization, inventory, lead time, or pricing data;
- recent 24/48/72 hour rumors, X/Grok signals, Gemini source gaps, or market reaction.

For evergreen education or framework explanation, avoid live collection unless the user asks or the answer depends on current facts.

### 3. Start From Demand, Not Stock Names

Do not start from hot A-share names and reverse-map a story. For any company question, first prove the chain context:

```text
upstream inputs/equipment -> company product/node -> downstream product/system -> end customer -> terminal demand driver
```

Minimum downstream-demand bridge:

| Field | Required answer |
|---|---|
| core product/service | Exact product, service, SKU, business line, grade, or specification that drives the thesis |
| downstream application/customer | Concrete product, system, user group, channel, or customer that consumes or pays for it |
| end buyer / demand driver | Capex, shipment, usage, traffic, replacement cycle, policy, income, price, credit cycle, utilization, or other driver |
| same-chain validation | Downstream customer/peer revenue, order, backlog, capex, utilization, traffic, shipment, lead time, inventory, monthly revenue, or renewal evidence |
| company proof | Segment revenue, volume, ARPU, take rate, order, backlog, certification, utilization, customer lock-in, or named/credible customer evidence |
| pass-through path | How demand becomes company volume, ASP, ARPU, take rate, mix, margin, utilization, or share gain |
| timing | Current quarter, 6 months, 12 months, 24 months, or `N/A` |
| reversal risk | Pull-forward, capex delay, demand slowdown, customer churn, dual-source, substitution, price pressure, competition, or new capacity |

### 4. Run Core Product Price And Unit-Economics Check

Use this check for every company or stock research task where the earnings thesis depends on a core product, core service, business line, SKU, product mix, price, ASP, ARPU, take rate, fee rate, spread, unit economics, or capacity utilization.

For non-product businesses, translate price into the relevant monetization metric: ARPU, subscription price, take rate, fee rate, commission rate, interest spread, occupancy rate, utilization rate, yield, renewal price, or unit revenue.

Minimum bridge:

| Field | Required answer |
|---|---|
| reported price/unit metric and volume | Company realized ASP, ARPU, take rate, fee rate, spread, utilization, shipment, users, orders, revenue, and whether the metric is mix-distorted |
| external price/rate signal | Spot, contract, channel, peer, platform, regulator, customer, or market price/rate trend if available |
| input/delivery/funding cost | Raw material, labor, bandwidth, compute, logistics, depreciation, funding, traffic-acquisition, or service-delivery cost |
| mix effect | Separate low-end/common offerings from premium/high-value offerings and one-time mix effects from durable mix upgrades |
| unit spread / margin | Whether realized price or unit revenue rose faster than unit cost, and whether margin or spread confirms it |
| supply-demand or competition reason | Qualified capacity, yield, certification, lead time, allocation, scarce inventory, customer demand, utilization, competition, regulation, or pricing discipline |
| sustainability verdict | `structural_mix_upgrade`, `qualified_supply_shortage`, `demand_led_pricing`, `commodity_cycle`, `cost_push`, `utilization_or_operating_leverage`, `inventory_pull_forward`, `competitive_price_pressure`, or `unclear` |
| reversal indicator | Price decline, ARPU/take-rate/spread compression, margin compression, lower utilization, inventory build, churn, customer destocking, competition, or capacity release |

### 5. Identify Real Bottlenecks

Treat a bottleneck as a demand-vs-qualified-supply gap, not a popularity label.

A real bottleneck needs demand-side evidence and supply-side constraint evidence, such as qualified capacity shortage, yield limits, long lead time, allocation, price pressure tied to shortage, customer certification queues, downstream ramp delay, or second-source qualification lag.

High margin, high HHI, high value share, technical difficulty, domestic-substitution difficulty, and stock-market heat are supporting clues only. Without visible or forecast supply-gap evidence, classify the node as `strategic_node`, `pricing_power_node`, or `watch`, not as a bottleneck.

### 6. Validate With Global Leaders

Use overseas or global leaders to calibrate the real industrial path before mapping local stocks:

- same-node global peers;
- technical route and product generation;
- customer/platform validation;
- share, capacity, margin, and pricing power when verified;
- whether the local company is catching up, near parity, behind, or not comparable.

### 7. Map Listed Companies Only After Node Selection

For each candidate, verify exact exposure, upstream dependencies, downstream application, end customer, demand driver, product/capacity/yield/certification/order/customer evidence, revenue or profit materiality, customer quality, switching cost, margin, cash flow, receivables, inventory, balance sheet, valuation, float, turnover, trend, and crowding.

Candidate classes:

- `main_candidate`: direct exposure plus strong customer/financial evidence.
- `watch`: plausible but missing evidence, timing, or valuation support.
- `event_trade_only`: catalyst exists but business evidence is weak.
- `theme_adjacent`: related theme, weak node exposure.
- `reject`: no hard evidence, wrong node, or financial contradiction.

### 8. Keep Three Rankings Separate

| Layer | Question | Core checks |
|---|---|---|
| Fundamental quality | Is this a high-quality business or value-chain position? | moat, value share, customer quality, margin durability, cash flow, governance, disclosure |
| Earnings elasticity | Can the industry change become revenue, margin, or profit? | revenue exposure, orders, backlog, ASP, utilization, yield, mix, operating leverage, report/guidance direction |
| Trading elasticity | Can the stock react strongly if the thesis is recognized? | market cap, float, liquidity, turnover, volatility, trend, catalyst density, expectation gap, valuation, crowding |

High-quality company does not automatically mean highest short-term stock elasticity. High trading elasticity with weak business evidence is event-only, not a hard-strength company.

## Output Pattern

Start with the conclusion, then show the logic path. For stock-ranking tasks, include:

```text
结论先行：
- 当前最值得深研的环节：
- 真正卡点：
- 下游需求是否足以支撑未来业绩：
- 基本面质量第一：
- 业绩弹性第一：
- 交易弹性第一：
- 最大风险：
- 下一步跟踪指标：
```

Use compact tables only when they improve clarity:

- 产业链位置：terminal demand -> downstream application/customer -> chain node -> company exposure
- 下游需求传导：application / buyer / demand driver / evidence / pass-through / timing / risk
- 瓶颈判断：node / demand evidence / supply-gap evidence / mechanism / confidence / reversal signal
- 公司映射：company / ticker / exact exposure / hard evidence / fundamental quality / earnings elasticity / trading elasticity / verdict

For quick answers, keep the same structure but compress tables into ranked bullets.

## Anti-Patterns

- Do not start from hot stock names.
- Do not answer an individual-stock question by describing only company profile, financials, valuation, and stock price.
- Do not treat downstream demand as a slogan. Name the application, buyer, demand driver, evidence, pass-through path, timing, and risk.
- Do not accept reported ASP, ARPU, fee rate, take rate, spread, or utilization as durable pricing proof without external price/rate signal, company realized metric, unit cost, mix effect, and reversal indicator.
- Do not equate theme heat with real beneficiary status.
- Do not equate a good company with highest trading elasticity.
- Do not promote C-grade chatter to a main conclusion.
- Do not use market reaction or K-line strength as proof of business exposure.
- Do not compare companies across different value-chain nodes before explaining whether the nodes are comparable.
- Do not rank only by PE; include growth, market cap, float, liquidity, volatility, expectation gap, and crowding when trading elasticity matters.
- Do not turn the output into a buy/sell call unless valuation, current market data, and trading context have been checked.
