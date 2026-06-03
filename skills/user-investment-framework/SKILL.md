---
name: user-investment-framework
description: Primary project-local entrypoint for all investment research in 产业链投研. Use first for any industry, sector, supply-chain, upstream/downstream map, downstream demand transmission, company, individual-stock, A-share, HK, US, Japan, Korea, Taiwan, valuation, announcement, filing, earnings, market-data, watchlist, dividend, technology-moat, domestic-substitution, global-leader, true-beneficiary-vs-concept, trading-elasticity, spreadsheet, or research-output request. Also trigger on 我的投资框架, 我的研究框架, 投资逻辑, 产业链研究, 上下游, 下游需求, 需求传导, 个股研究, 行业研究, 公司对比, 股票弹性, 业绩弹性, 基本面排序, 交易弹性排序.
---

# User Investment Framework

## Role

Use this as the first loaded project skill for investment research. It is the user's master framework and orchestration layer. Other project skills are supporting capabilities selected from this framework, not competing entrypoints.

The core lens is:

`terminal demand -> downstream application/customer demand -> industry-chain topology -> BOM/value node -> demand-vs-qualified-supply gap -> bottleneck mechanism -> global leader validation -> listed-company hard-evidence mapping -> three-layer ranking -> risks and tracking signals`

This skill is a decision discipline, not a data source. It decides the research route, evidence standard, ranking logic, and final output shape, then loads only the smallest necessary companion skills.

## Companion Skill Map

For non-trivial routing or when choosing among project skills, read `references/project-skill-integration.md`.

Default companion layers:

| Need | Companion skills |
|---|---|
| Legacy route alignment | `industry-research-router` |
| Long industry/company research | `deep-research`, `20-andruia-niche-intelligence` |
| AI/semiconductor chain | `semiconductor-ai-chain-investment-researcher`, `ai-chain-research-orchestrator`, `browser-grok-gemini-research` |
| Cross-industry bottlenecks | `industry-chain-deep-disassembly` |
| Company fundamentals and downstream demand | `stock-fundamental-moat-triad`, `stock-evaluator`, `business-analyst`, `industry-chain-deep-disassembly` |
| Competitive landscape | `competitive-landscape`, `competitive-intel`, `apify-competitor-intelligence` |
| Source discovery and digestion | `search-specialist`, `research-summarizer`, `web-scraper`, `firecrawl-scraper`, `tavily-web` |
| News-to-alpha financial translation | `serenity-alpha`, `search-specialist`, `research-summarizer`, `allstock-data`, `advanced-evaluation` |
| A-share tracking and disclosures | `a-share-company-tracking`, `a-share-disclosure-trading-data` |
| Earnings and guidance | `earnings-call-investment-analyst` |
| Public equity PM workflows | `Public Equity Investing:thesis-tracker`, `Public Equity Investing:catalyst-calendar`, `Public Equity Investing:event-driven-analyzer`, `Public Equity Investing:earnings-preview`, `Public Equity Investing:earnings-deep-dive`, `Public Equity Investing:scenario-sensitivity-generator`, `Public Equity Investing:portfolio-risk-management` |
| Market data and trading context | `allstock-data`, `finance`, `stocks`, `yfinance-mcp-server`, `alpha-vantage`, `banana-farmer`, `stock-data-skill`, `stock-copilot-pro` |
| HTSC market/service tools | `query-indicator`, `select-stock`, `financial-analysis`, `watchlist-management`, `a-share-paper-trading` |
| Scoring, factors, tables, workbooks | `advanced-evaluation`, `multi-factor-strategy`, `spreadsheet`, `xlsx`, `xlsx-official`, `data-scientist`, `senior-data-scientist`, `Public Equity Investing:financials-normalizer`, `Public Equity Investing:equity-model-update`, `Public Equity Investing:model-audit-tieout` |
| Documents and deliverables | `docx`, `pdf`, `pptx`, `Public Equity Investing:memo-builder`, `Public Equity Investing:long-short-pitch`, `Public Equity Investing:company-tearsheet`, `Public Equity Investing:deck-report-qc` |
| Technical moat and product logic | `ai-engineer`, `ai-ml`, `ai-product`, `tech-stack-evaluator`, `cto-advisor`, `senior-architect`, `arm-cortex-expert`, `product-manager`, `product-manager-toolkit` |
| Dividend/defensive style | `dividend-premium-tracker` |

Do not load every companion skill. Start here, classify the request, then load the smallest useful combination.

## HTSC Plugin Use Boundaries

HTSC plugin skills are optional tool sources inside this framework, not a shortcut around company or industry research.

Default rule: use HTSC for fast A-share indicators, candidate discovery, quick external context, HTSC watchlist service, and simulated trading only. Do not let HTSC replace the upstream/downstream map, downstream demand bridge, core-product demand and price/unit-economics check, official disclosures, customer/supplier evidence, or the final three-layer ranking.

| HTSC skill | Appropriate use | Do not use for |
|---|---|---|
| `query-indicator` | Fast latest/recent A-share indicators, PE/PB, turnover, transaction amount, short historical point checks, and multi-stock indicator comparison. | Primary structured K-line or OHLCV history, factor research, VCP pattern work, backtesting, or hard company-fact proof. |
| `select-stock` | First-pass candidate pools from natural-language screening conditions. | Final recommendations, true-beneficiary proof, or strict auditable screening without re-verification. |
| `financial-analysis` | Quick market, sector, news, sentiment, or individual-stock diagnosis as external context. | Final thesis, causal explanation, ranking, buy/sell language, or replacement for project evidence checks. |
| `watchlist-management` | Explicit HTSC external watchlist query/add operations. | Repository watchlist state, durable `a-share-company-tracking` records, or automatic watchlist changes. |
| `a-share-paper-trading` | Explicit simulated A-share search, sparse quote, balance, position, order, cancellation, and trade-history operations. | Live trading, unrequested simulated orders/cancellations, primary real-time quote feeds, or historical market-data storage. |

For individual-stock or company research, label any HTSC output as supplemental market/indicator/service data. Verify hard claims with official filings, exchange disclosures, company IR, project-local market-data sources, or other structured data sources. The tested HTSC plugin paths do not expose a stable structured historical OHLCV series suitable for deep research, VCP pattern work, factor research, or backtesting.

## Public Equity Investing Plugin Use Boundaries

Public Equity Investing plugin skills are optional PM workflow layers inside this framework. They do not replace the chain-first research path, official-evidence hierarchy, downstream-demand bridge, core-product demand and price/unit-economics check, or the final three-layer ranking.

Default sequence:

`project evidence and chain map -> company and earnings thesis -> scenario / catalyst / event / tracker / risk plugin workflow -> final project ranking or action posture`

Do not start a project research task from the plugin router. Start from `user-investment-framework`; use the plugin only when the user's task is clearly a listed-equity PM workflow or when the project framework has already established the issuer/security context.

| Public Equity Investing skill | Appropriate use | Do not use for |
|---|---|---|
| `Public Equity Investing:thesis-tracker` | Build or update falsifiable thesis pillars, KPI thresholds, catalysts, kill criteria, evidence ledger, and action thresholds after an initial company thesis exists. | First-pass company research, generic news summaries, proof of beneficiary status, or replacing `a-share-company-tracking` state. |
| `Public Equity Investing:catalyst-calendar` | Maintain upcoming earnings, product, policy, regulatory, index, order, or validation events and next proof points. | Full event underwriting, final alpha ranking, or automatic recurring jobs. |
| `Public Equity Investing:event-driven-analyzer` | Analyze dated public-equity events with conditions, timing, scenarios, probabilities, payoffs, expected return, and red-team risks. | Generic news-to-alpha translation, source verification, portfolio sizing, or credit/security restructuring analysis. |
| `Public Equity Investing:earnings-preview` | Prepare pre-earnings expectation bar, likely KPI focus, scenario setup, guidance credibility, and call questions. | Post-results analysis or short earnings summaries. |
| `Public Equity Investing:earnings-deep-dive` | Analyze results, guidance, transcript/call commentary, estimate changes, and what changed after earnings. | Replacing `earnings-call-investment-analyst` source discipline or using third-party transcripts as official originals. |
| `Public Equity Investing:scenario-sensitivity-generator` | Turn a base case, thesis, event, or catalyst into scenario skew, sensitivities, breakpoints, and PM action thresholds. | First-pass model building, unsupported precision, or generic planning. |
| `Public Equity Investing:portfolio-risk-management` | Size positions, compare size-down/no-hedge/hedged packages, identify retained exposure, basis risk, liquidity, exit, add/trim/exit rules. | Thesis construction, trade execution, personal investment advice, or credit-instrument hedges. |
| `Public Equity Investing:financials-normalizer`, `Public Equity Investing:equity-model-update`, `Public Equity Investing:model-audit-tieout` | Normalize public-company financials, update model copies, and audit model/spreadsheet tie-outs when workbook/model integrity matters. | Pure narrative notes, original source proof, or building investment conclusions before evidence is verified. |
| `Public Equity Investing:comps-valuation`, `Public Equity Investing:dcf-model-builder`, `Public Equity Investing:three-statement-model-builder` | Optional valuation/modeling after chain position, earnings path, and current market context are verified. | Replacing industry-chain diagnosis, official evidence, or the three-layer ranking. |
| `Public Equity Investing:memo-builder`, `Public Equity Investing:long-short-pitch`, `Public Equity Investing:company-tearsheet`, `Public Equity Investing:deck-report-qc` | Package an already-supported idea into a memo, pitch, tearsheet, or report/deck QC pass. | Default answers, source discovery, live trade construction, or making unsupported recommendations look finished. |

For simple questions, do not let a plugin's formal artifact defaults turn the task into a full report or workbook unless the user asks for that output. For model, tracker, memo, or report requests, follow the owning plugin skill's artifact rules after the project framework has chosen it.

## AI Chain Node Taxonomy Reference

For AI data-center, AI hardware, semiconductor-chain, and AI产业链 tasks, use `references/ai-chain-node-taxonomy.md` as the local node map before selecting bottlenecks, comparing nodes, or mapping listed companies.

This taxonomy points to the cleaned Level 1-5 AI chain mind map in `docs/ai_chain_disassembly/`:

- use Level 1 and Level 2 for chain-family orientation;
- use Level 3 and Level 4 P0 as the normal research, bottleneck, value-share, and company-mapping granularity;
- use P5 summaries only as material, equipment, component, process, or search-keyword hints;
- never treat the taxonomy itself as evidence for demand, orders, pricing, supply gaps, customer validation, or stock exposure.

After the taxonomy identifies the exact node, still run the evidence workflow below: downstream demand bridge, current evidence check when needed, bottleneck proof, global-leader calibration, listed-company hard-evidence mapping, and three-layer ranking.

## Unknown Stock Node Discovery Gate

For individual-stock or company prompts, do not assume the AI-chain node from the stock name. If the company's exact product, service, or value-chain exposure is not already known, run a short identity and exposure discovery step before using the AI chain taxonomy:

1. identify the listed entity, ticker, market, main business lines, and latest segment/product disclosure;
2. extract the specific products, services, materials, equipment, components, processes, or customer applications that may connect to AI data-center or semiconductor demand;
3. grade each exposure as `confirmed`, `partial clue`, `rumor only`, or `not found` using official filings, announcements, IR records, product pages, or credible primary-adjacent sources;
4. map only the confirmed or partial-clue product terms to candidate Level 3 / Level 4 P0 taxonomy paths;
5. if no direct or partial AI-chain exposure is found, say the company is outside the current AI taxonomy scope or keep it as `theme_adjacent` / `watch`, not a main AI-chain candidate.

Use `search-specialist`, `a-share-disclosure-trading-data`, `stock-fundamental-moat-triad`, and source-digestion skills when the identity or exposure is unclear. The taxonomy is used after this discovery step, not before it.

## Workflow

### 1. Classify The Real Task

Before answering, classify the request as one or more of:

- industry-chain learning or node disassembly;
- AI data-center or semiconductor-chain node lookup against the local AI chain taxonomy;
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
- downstream capex, cloud/customer guidance, carrier bidding, shipment, utilization, inventory, lead-time, or pricing data;
- recent 24/48/72 hour rumors, X/Grok signals, Gemini source gaps, or market reaction.

For evergreen education or framework explanation, avoid live collection unless the user asks or the answer depends on current facts.

### 3. Start From Demand, Not Stock Names

Do not start from hot A-share names and reverse-map a story.

For any individual-stock or company question, do not start with "this company is good/bad." First prove the chain context:

`upstream inputs/equipment -> company product/node -> downstream product/system -> end customer -> terminal demand driver`

If the company product/node is unknown, first run the Unknown Stock Node Discovery Gate above. Only after the product or exposure is identified should you select candidate AI taxonomy paths.

First define:

- terminal demand and who pays;
- downstream product or system;
- end-customer type: carrier, cloud vendor, AI data center, industrial customer, consumer, government, or other;
- chain layers and exact nodes;
- BOM/value share or value-capture proxy;
- demand multiplier from terminal demand to the node;
- uncertainty: real expansion, inventory pull-forward, early signal, or unverified narrative.

Minimum downstream demand table for company research:

| Field | Required Answer |
|---|---|
| downstream application | Which concrete product/system consumes the company's product |
| end customer / buyer | Who ultimately buys or deploys it |
| demand driver | Capex, traffic, AI cluster buildout, replacement cycle, policy, price, or other driver |
| demand evidence | A/B source, latest data point, or `N/A` |
| pass-through path | How downstream demand becomes volume/ASP/margin for the company |
| timing | current quarter, 6 months, 12 months, 24 months, or `N/A` |
| key risk | Inventory pull-forward, capex delay, customer concentration, substitution, price pressure, or overcapacity |

### 3A. Run The Core Product Demand And Price Trend Check

Use this check for every company or stock research task where the earnings thesis depends on a core product, core service, business line, SKU, product mix, price, ASP, ARPU, take rate, fee rate, spread, unit economics, or capacity utilization.

This is industry-neutral. For non-product businesses, translate "price" into the relevant monetization metric: ARPU, subscription price, take rate, fee rate, commission rate, interest spread, occupancy rate, utilization rate, yield, renewal price, or unit revenue.

Do not stop at company financials, valuation, or a concept label. Rebuild the thesis through two main lines:

1. Downstream demand transmission:
   `terminal demand -> downstream application/customer -> core product/service demand -> company offering mix -> volume/ASP/ARPU/take rate/margin`
2. Core product price and unit-economics trend:
   `market price/rate -> company realized ASP/ARPU/take rate/fee/spread -> input/delivery/funding cost -> unit spread/gross margin -> sustainability`

Minimum downstream-demand bridge:

| Field | Required Answer |
|---|---|
| core product/service | Exact product, service, SKU, business line, grade, or specification that drives the thesis |
| downstream application/customer | Concrete product, system, user group, channel, or customer that consumes or pays for it |
| end buyer / demand driver | Capex, shipment, usage, traffic, replacement cycle, policy, income, price, credit cycle, utilization, or other driver |
| same-chain validation | Downstream customer/peer revenue, order, backlog, capex, utilization, traffic, shipment, lead time, inventory, monthly revenue, or renewal evidence |
| company proof | Segment revenue, volume, ARPU, take rate, order, backlog, certification, utilization, customer lock-in, or named/credible customer evidence |
| pass-through path | How demand becomes company volume, ASP, ARPU, take rate, mix, margin, utilization, or share gain |
| timing | Current quarter, 6 months, 12 months, 24 months, or `N/A` |
| reversal risk | Pull-forward, capex delay, demand slowdown, customer churn, dual-source, substitution, price pressure, competition, or new capacity |

Minimum core-product price and unit-economics bridge:

| Field | Required Answer |
|---|---|
| reported price/unit metric and volume | Company realized ASP, ARPU, take rate, fee rate, spread, utilization, shipment, users, orders, revenue, and whether the metric is mix-distorted |
| external price/rate signal | Spot, contract, channel, peer, platform, regulator, customer, or market price/rate trend if available |
| input/delivery/funding cost | Key raw material, labor, bandwidth, compute, logistics, depreciation, funding, traffic-acquisition, or service-delivery cost |
| mix effect | Separate low-end/common offerings from premium/high-value offerings and one-time mix effects from durable mix upgrades |
| unit spread / margin | Whether realized price or unit revenue rose faster than unit cost, and whether gross margin, contribution margin, or spread confirms it |
| supply-demand or competition reason | Qualified capacity, yield, certification, lead time, allocation, scarce inventory, customer demand, utilization, competition, regulation, or pricing discipline |
| sustainability verdict | `structural_mix_upgrade`, `qualified_supply_shortage`, `demand_led_pricing`, `commodity_cycle`, `cost_push`, `utilization_or_operating_leverage`, `inventory_pull_forward`, `competitive_price_pressure`, or `unclear` |
| reversal indicator | Price decline, ARPU/take-rate/spread compression, margin compression, lower utilization, inventory build, churn, customer destocking, competition, or capacity release |

If a core offering's price, ASP, ARPU, take rate, fee rate, spread, or utilization drove the earnings inflection, the final answer must explicitly state: whether the change is real, what caused it, how it reaches the company's margin, how long it may last, and what would prove it is reversing. A company-reported ASP or ARPU alone is not enough; separate external price/rate signal, company realized metric, mix effect, and unit cost.

### 4. Identify Real Bottlenecks

Treat a bottleneck as a demand-vs-qualified-supply gap, not a popularity label.

For AI data-center and semiconductor-chain questions, first locate the candidate path in `references/ai-chain-node-taxonomy.md`, normally at Level 3 or Level 4 P0. Use that path to define the exact node before judging bottleneck status. P5 summaries can guide evidence searches for materials, equipment, components, and processes, but they do not by themselves prove a bottleneck.

A real bottleneck needs demand-side evidence and supply-side constraint evidence, such as:

- qualified capacity shortage;
- usable capacity or yield limits;
- long lead time, allocation, or price pressure tied to shortage;
- customer certification queue or vendor availability limit;
- downstream ramp delay;
- expansion or second-source qualification lag.

High margin, high HHI, high value share, technical difficulty, domestic-substitution difficulty, and stock-market heat are supporting clues only. Without visible or forecast supply gap evidence, classify the node as `strategic_node`, `pricing_power_node`, or `watch`, not as a bottleneck.

### 5. Forecast Future Migration

After current bottlenecks, ask where the next 6-24 month supply gap may move.

Check:

- next technology generation;
- architecture shift;
- customer design change;
- product specification upgrade;
- capacity expansion timing;
- yield learning curve;
- second-source qualification;
- regulation, energy, material, equipment, or logistics constraints;
- profit-pool migration.

State timing, confidence, evidence gap, and reversal indicator. Do not extrapolate today's shortage mechanically.

### 6. Validate With Global Leaders

Use overseas or global leaders to calibrate the real industrial path before mapping local stocks.

Check:

- same-node global peers;
- technical route and product generation;
- customer or platform validation;
- share, capacity, margin, and pricing power when verified;
- whether the local company is catching up, near parity, behind, or not comparable.

Do not claim parity from one headline parameter. Compare specs, reliability, customer status, manufacturing moat, and commercial scale that matter for the node.

### 7. Map Listed Companies Only After Node Selection

Do not map or rate a company before the upstream/downstream map and downstream demand table are present. A company profile, financial summary, valuation, or stock chart is incomplete if it does not explain who downstream buys, why demand grows, and how that demand reaches the company's exact node.

For AI-chain mapping, record the exact taxonomy path when available, such as `AI 数据中心 / 智算中心 > ... > Level 3 node > Level 4 P0 node`. Use the path to reject theme-adjacent companies that do not expose the same node.

For each candidate, verify:

- exact exposure to the selected node;
- upstream dependencies and whether they constrain margin or delivery;
- downstream application, end customer, demand driver, and demand pass-through;
- product, capacity, yield, certification, order, or customer evidence;
- revenue or profit materiality;
- customer quality and switching cost;
- margin, cash-flow, receivables, inventory, and balance-sheet support;
- valuation, market cap, float, turnover, trend, and crowding for timing only.

Classify candidates:

- `main_candidate`: direct exposure plus strong customer/financial evidence.
- `watch`: plausible but missing evidence, timing, or valuation support.
- `event_trade_only`: catalyst exists but business evidence is weak.
- `theme_adjacent`: related theme, weak node exposure.
- `reject`: no hard evidence, wrong node, or financial contradiction.

### 8. Keep Three Rankings Separate

Always separate these layers when stocks are involved:

| Layer | Question | Core checks |
|---|---|---|
| Fundamental quality | Is this a high-quality business or value-chain position? | moat, value share, customer quality, margin durability, cash flow, governance, disclosure |
| Earnings elasticity | Can the industry change become revenue, margin, or profit? | revenue exposure, orders, backlog, ASP, utilization, yield, mix, operating leverage, report/guidance direction |
| Trading elasticity | Can the stock react strongly if the thesis is recognized? | market cap, float, liquidity, turnover, volatility, trend, catalyst density, expectation gap, valuation, crowding |

High-quality company does not automatically mean highest short-term stock elasticity. High trading elasticity with weak business evidence is event-only, not a hard-strength company.

### 9. Grade Evidence

Use explicit evidence grades:

| Grade | Meaning |
|---|---|
| A | official announcement, filing, exchange disclosure, annual/interim/quarterly report, prospectus, company IR, official customer/supplier source |
| B | reputable data vendor, industry association, credible media with named source, broker note summary with cited source |
| C | social post, Grok/X, forum, model output, unsourced concept-board label |
| N/A | no usable evidence |

C-grade evidence can guide search priority only. It cannot support a main bottleneck conclusion, future bottleneck forecast, or main stock pick without A/B confirmation.

Use `N/A` for missing current facts. Do not infer exact numbers from memory.

## Output Pattern

Start with the conclusion, then show the logic path.

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

一、产业链位置
terminal demand -> downstream application/customer -> chain node -> company exposure

二、下游需求传导
| downstream application | end customer/buyer | demand driver | demand evidence | pass-through to company | timing | risk |

三、上下游链条
| upstream input/equipment | company product/node | downstream product/system | customer validation | margin/delivery constraint |

四、瓶颈判断
| node | demand evidence | supply-gap evidence | constraint mechanism | current/future | confidence | reversal signal |

五、全球龙头校准
| global peer | same node? | technical/customer proof | gap vs local candidate | implication |

六、公司映射
| company | ticker | exact exposure | hard evidence | fundamental quality | earnings elasticity | trading elasticity | verdict |

七、风险与跟踪
- 证据缺口：
- 下游需求失效条件：
- 估值/拥挤风险：
- 财报/订单/客户认证信号：
- 失效条件：
```

For quick answers, keep the same structure but compress tables into ranked bullets.

## Anti-Patterns

- Do not start from hot stock names.
- Do not answer an individual-stock question by describing only the company, financials, valuation, and stock price; always map upstream, downstream, and downstream demand first.
- Do not treat downstream demand as a slogan. Name the application, buyer, demand driver, evidence, pass-through path, timing, and risk.
- Do not accept a reported ASP, ARPU, fee-rate, take-rate, spread, or utilization increase as proof of durable pricing power. Separate external price/rate signal, company realized metric, unit cost, mix effect, unit spread, and reversal indicators.
- Do not mix common/low-end offerings with premium/high-value offerings when judging demand, pricing, margin, or supply-demand tightness.
- Do not equate theme heat with real beneficiary status.
- Do not equate a good company with highest trading elasticity.
- Do not promote C-grade chatter to a main conclusion.
- Do not use market reaction or K-line strength as proof of business exposure.
- Do not compare companies across different value-chain nodes before explaining whether the nodes are comparable.
- Do not rank only by PE; include growth, market cap, float, liquidity, volatility, expectation gap, and crowding when trading elasticity matters.
- Do not turn the output into a buy/sell call unless valuation, current market data, and trading context have been checked.
