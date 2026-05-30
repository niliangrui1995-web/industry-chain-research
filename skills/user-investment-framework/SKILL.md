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
| A-share tracking and disclosures | `a-share-company-tracking`, `a-share-disclosure-trading-data` |
| Earnings and guidance | `earnings-call-investment-analyst` |
| Market data and trading context | `allstock-data`, `finance`, `stocks`, `yfinance-mcp-server`, `alpha-vantage`, `banana-farmer`, `stock-data-skill`, `stock-copilot-pro` |
| Scoring, factors, tables, workbooks | `advanced-evaluation`, `multi-factor-strategy`, `spreadsheet`, `xlsx`, `xlsx-official`, `data-scientist`, `senior-data-scientist` |
| Documents and deliverables | `docx`, `pdf`, `pptx` |
| Technical moat and product logic | `ai-engineer`, `ai-ml`, `ai-product`, `tech-stack-evaluator`, `cto-advisor`, `senior-architect`, `arm-cortex-expert`, `product-manager`, `product-manager-toolkit` |
| Dividend/defensive style | `dividend-premium-tracker` |

Do not load every companion skill. Start here, classify the request, then load the smallest useful combination.

## Workflow

### 1. Classify The Real Task

Before answering, classify the request as one or more of:

- industry-chain learning or node disassembly;
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

### 4. Identify Real Bottlenecks

Treat a bottleneck as a demand-vs-qualified-supply gap, not a popularity label.

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
- Do not equate theme heat with real beneficiary status.
- Do not equate a good company with highest trading elasticity.
- Do not promote C-grade chatter to a main conclusion.
- Do not use market reaction or K-line strength as proof of business exposure.
- Do not compare companies across different value-chain nodes before explaining whether the nodes are comparable.
- Do not rank only by PE; include growth, market cap, float, liquidity, volatility, expectation gap, and crowding when trading elasticity matters.
- Do not turn the output into a buy/sell call unless valuation, current market data, and trading context have been checked.
