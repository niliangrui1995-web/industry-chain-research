---
name: industry-chain-deep-disassembly
description: Use when researching a growth industry through supply-chain topology, BOM cost nodes, lead-time bottlenecks, profit-pool migration, HHI concentration, pricing power, pure-play exposure, and A-share or global stock screening.
---

# Industry Chain Deep Disassembly

## Purpose

Use this skill after `industry-research-router` when the user wants to find the scarce, high-premium node in a growing industry rather than rank companies by a static industry label.

The core lens is:

`terminal demand -> BOM/value node -> capacity and lead-time constraint -> pricing power -> pure-play stock exposure -> financial and market validation`

## When To Use

Use for:

- Growth industries where demand is accelerating but the winning node is unclear.
- AI hardware, manufacturing equipment, new materials, energy equipment, robotics, data-center infrastructure, high-end components, and other multi-layer supply chains.
- Questions about bottlenecks, choke points, shortages, delivery cycles, BOM value share, profit pools, HHI, oligopoly, domestic substitution, or true beneficiary stocks.
- Stock screening after the user provides `target_industry` and optionally `target_stocks`.

Do not use this as a live-news collector by itself. If the thesis depends on fresh news, rumors, Grok/X, Gemini, policy, prices, or filings, first use the project evidence route (`ai-chain-research-orchestrator`, `search-specialist`, web tools, or market-data skills as appropriate).

## Data Discipline

- Never invent financial ratios, market shares, BOM cost shares, lead times, capacity, prices, valuation, or stock data.
- Use official filings, annual/interim/quarterly reports, prospectuses, exchange disclosures, company IR, reputable industry sources, market-data tools, user-provided files, or local datasets.
- If a required value is not verified, write `N/A` and mark `evidence_gap`.
- Use `scripts/calculate_hhi.py` when market-share data is available. If no share data exists, explain why HHI cannot be calculated.
- Use `scripts/score_bottleneck_nodes.py` when a node scoring CSV exists. Treat it as a consistency aid, not a substitute for evidence.
- There is no universal automatic BOM fetcher. If a project-specific `scripts/fetch_bom_data.py` or local BOM file exists, use it; otherwise design a source search and extract BOM evidence manually.
- Read `references/source-priority.md` when source discovery, BOM, lead time, market share, or financial-validation evidence is incomplete.
- Read a matching `references/adapters/*.md` file when the target industry matches a supported adapter. If no adapter exists, continue with the generic workflow and do not invent industry-specific node data.
- Read `references/data-interfaces.md` when the user provides CSV/JSON/JSONL/XLSX files, asks for data connectors, or wants reusable evidence tables.
- Run `scripts/normalize_research_inputs.py` on user-provided raw data before HHI, bottleneck scoring, financial validation, or stock screening. Missing required fields must stay as `N/A` and be treated as evidence gaps.
- Separate global leader benchmarking from China tradable mapping: identify overseas/global oligarchs and the real technology path first, then map A-share/HK-share/China-local candidates after the bottleneck node is selected.

Evidence grades:

| Grade | Meaning |
|---|---|
| A | Filing, official announcement, prospectus, audited report, exchange disclosure, customer or supplier primary source |
| B | Reputable data vendor, industry association, sell-side report with cited source, credible media with named source |
| C | Unsourced web claim, social post, model output, concept-board label, or unverifiable secondary summary |

C-grade evidence can guide search priority only. It cannot support a main conclusion or stock pick without A/B confirmation.

## Industry Adapters

Load only the adapter that matches the target industry:

| Adapter | Trigger Keywords |
|---|---|
| `references/adapters/pcb-ccl.md` | AI PCB, PCB, CCL, copper clad laminate, electronic cloth, glass fiber, copper foil, resin, ABF, HDI, substrate-like PCB |
| `references/adapters/liquid-cooling.md` | liquid cooling, cold plate, CDU, coolant distribution, pump, valve, quick connector, leak reliability, AI server cooling |
| `references/adapters/optical-module.md` | optical module, EML, DSP, silicon photonics, InP, CPO, OCS, fiber connector, datacenter optics |
| `references/adapters/data-center-power.md` | data-center power, UPS, transformer, switchgear, busway, power module, grid interconnect, AI datacenter electricity |

## Data Interfaces

Use the data-interface contract when source data exists but arrives in mixed formats. The script normalizes fields; it does not fetch or verify current facts.

```powershell
python skills/industry-chain-deep-disassembly/scripts/normalize_research_inputs.py --input data.xlsx --pretty
python skills/industry-chain-deep-disassembly/scripts/normalize_research_inputs.py --input leaders.csv --table global_leaders --pretty
```

Canonical tables:

| Table | Role | Use Timing |
|---|---|---|
| `global_leaders` | Overseas/global oligarchs, technology path, profit-pool benchmark | Before China stock mapping |
| `supply_chain_nodes` | BOM/value nodes, lead time, rigidity, substitution, concentration | Before bottleneck scoring and HHI |
| `china_candidates` | A-share/HK-share/China-local tradable exposure mapping | After node selection |
| `financial_validation` | Margin, turnover, cash flow, capex, leverage checks | Before final stock verdict |
| `market_snapshot` | Market cap, float, valuation, turnover, trend, crowding | For timing and trading elasticity only |
| `source_evidence` | Claim-to-source ledger and limitations | Whenever evidence is mixed or disputed |

Connector boundary:

- Global market and financial data: use official filings/IR first, then `yfinance-mcp-server`, `stocks`, `alpha-vantage`, or equivalent market-data tools.
- China market and financial data: use official filings, exchange disclosures, company IR, `allstock-data`, `finance`, and `stock-evaluator`.
- Live news, rumors, orders, policy, or recent price moves require the project evidence route before conclusions.

## Workflow

### 1. Define Demand Transmission

Identify the terminal product and demand driver before mapping stocks.

Output one demand table:

| Field | Required Check |
|---|---|
| terminal demand | What end demand pays for the product or service |
| leading indicators | Orders, capex, utilization, backlog, inventory, attach rate, policy, customer guidance |
| demand multiplier | How one unit of terminal demand converts into upstream volume/value |
| demand uncertainty | Whether downstream flexibility creates option value or only inventory risk |
| evidence | A/B/C grade and source note |

Flag demand as `confirmed_expansion`, `early_signal`, `inventory_pull_forward`, or `unverified`.

### 2. Build The Network And BOM Node Table

Decompose the industry into at least three layers:

- Upstream: raw materials, equipment, core components, consumables, software/IP.
- Midstream: processing, manufacturing, packaging, assembly, integration, testing.
- Downstream: terminal products, channels, system integrators, end customers.

Create a node table. Use `references/node-table-schema.md` when the user wants a reusable table.

Required columns:

| Column | Meaning |
|---|---|
| layer | upstream/midstream/downstream |
| node | precise product, material, equipment, process, or service |
| BOM_or_value_share | unit cost share, value share, or revenue share, with source |
| margin_proxy | gross margin, operating margin, or spread proxy |
| lead_time | delivery cycle or capacity expansion cycle |
| capacity_rigidity | low/medium/high, based on capex cycle, yield, qualification, permits, equipment availability |
| substitution_elasticity | low/medium/high, with short-term and long-term distinction |
| top_players | global and domestic leaders |
| market_share | share data if verified |
| pricing_mechanism | contract, spot, cost-plus, allocation, long-term agreement, qualification lock-in |
| evidence_grade | A/B/C/N/A |

### 3. Identify Bottleneck And Pricing Power

Score each key node separately. Keep the raw reason next to every score.

| Dimension | Score Guide |
|---|---|
| demand_pass_through | 0-5: terminal demand growth converts into this node's volume or ASP |
| supply_rigidity | 0-5: new capacity, yield, certification, equipment, and permits are hard to add quickly |
| lead_time_pressure | 0-5: delivery or capacity cycle is long relative to demand change |
| substitution_resistance | 0-5: customers cannot switch technology or vendor quickly |
| concentration_pricing | 0-5: HHI, CR3/CR5, customer switching cost, allocation power, cost pass-through |
| profit_pool_migration | 0-5: margin, ASP, mix, or bargaining power is moving toward this node |
| financial_confirmation | 0-5: gross margin, net margin, receivables, inventory, and cash conversion confirm power |

Suggested classification:

| Pattern | Interpretation |
|---|---|
| high demand + high rigidity + low substitution | true choke point |
| high demand + low rigidity | volume beneficiary, not pricing-power asset |
| high HHI + weak demand | oligopoly without near-term elasticity |
| high concept heat + weak financial confirmation | story risk |
| high working-capital stress + rising revenue | possible forced shipment or weak bargaining power |

When a node scoring table is available, run:

```powershell
python skills/industry-chain-deep-disassembly/scripts/score_bottleneck_nodes.py --csv path/to/nodes.csv --pretty
```

The scoring script is a consistency aid. A node with only C-grade or missing evidence cannot be promoted above watch level.

### 4. Calculate Concentration

When share data exists:

```powershell
python skills/industry-chain-deep-disassembly/scripts/calculate_hhi.py --shares 35 25 15 10 5
```

Interpretation:

- `HHI < 1500`: fragmented, pricing power must come from technology or certification, not concentration.
- `1500 <= HHI < 2500`: moderately concentrated; check cost pass-through and customer lock-in.
- `HHI >= 2500`: highly concentrated; if demand and supply rigidity are also strong, prioritize as a possible high-premium node.
- User's stricter watch line: `HHI > 1800` can be used as the first screen, but do not treat it as sufficient proof.

Gate rules:

- No verified market-share data: HHI is `N/A`; use concentration language only qualitatively.
- Share data not summing to about 100%: treat HHI as partial coverage and state the residual gap.
- HHI can upgrade confidence only when demand pass-through, supply rigidity, and substitution resistance are also supported by A/B evidence.

### 5. Map Stocks Only After Node Selection

Do not start from hot stock names. First select bottleneck nodes, then map companies.

For every candidate stock, verify:

| Test | Pass Condition |
|---|---|
| exact exposure | Product or revenue is directly tied to the selected node |
| pure-play quality | Bottleneck node is material enough to move revenue, margin, or valuation |
| customer proof | Customer certification, order, qualification, capacity, or official project evidence exists |
| financial proof | Gross margin, net margin, receivables turnover, inventory turnover, operating cash flow trend support the thesis |
| capacity proof | Capacity, yield, process generation, equipment, or expansion schedule is disclosed or well sourced |
| market proof | Market cap, float, turnover, valuation, trend, and crowding support or limit trading elasticity |

Classify candidates as:

- `main_candidate`: direct exposure and financial/customer evidence are both strong.
- `watch_only`: exposure exists but evidence, timing, or valuation is incomplete.
- `theme_adjacent`: concept relation exists but exposure is weak or diluted.
- `reject`: no hard evidence, wrong node, or financials contradict the story.

### 6. Separate The Three Rankings

Always separate:

- Fundamental quality: moat, customer quality, margin durability, balance-sheet quality, long-term competitive position.
- Earnings elasticity: revenue contribution, ASP leverage, capacity utilization, operating leverage, gross margin sensitivity.
- Trading elasticity: float market cap, liquidity, volatility, catalyst density, expectation gap, crowding, technical position.

Do not merge these into one vague "best stock" score.

### 7. Risk And Reversal Watch

For every selected node and stock, state what would break the thesis:

- Downstream inventory-to-sales ratio rises or orders are pulled forward.
- Lead time normalizes faster than expected.
- New capacity release, yield improvement, or second-source qualification.
- Substitute technology crosses cost/performance threshold.
- Customers internalize the component or redesign the BOM.
- Profit pool moves downstream or upstream.
- Financial mismatch: revenue rises but margin, cash conversion, or receivable quality deteriorates.

## Output Contract

Start with conclusion, then evidence tables.

```text
结论先行：
- 当前最大供需矛盾：
- 最可能拥有高溢价的瓶颈节点：
- 可进入主结论的股票：
- 只能观察或剔除的股票：
- 最大反转风险：

产业链拓扑与 BOM：
| layer | node | BOM/value share | lead time | supply rigidity | substitution | top players | evidence |

瓶颈评分：
| node | demand | rigidity | lead time | substitution | HHI/pricing | profit migration | verdict |

个股交叉验证：
| company | ticker | node exposure | pure-play | customer proof | financial proof | fundamental quality | earnings elasticity | trading elasticity | verdict |

跟踪指标：
- 下游：
- 中游：
- 上游：
- 财务：
- 市场：
```

## Common Mistakes

- Starting from `target_stocks` and reverse-writing an industry story.
- Treating HHI as proof of pricing power without demand and switching-cost evidence.
- Calling every long lead-time product a bottleneck while ignoring capacity expansion already under way.
- Mixing board-level PCB, ABF substrate, CCL, resin, glass fiber, copper foil, equipment, and assembly as one undifferentiated "AI hardware" bucket.
- Using concept-board names instead of exact product exposure and revenue materiality.
- Ignoring working capital. Real bargaining power usually improves cash conversion or at least prevents severe deterioration.
