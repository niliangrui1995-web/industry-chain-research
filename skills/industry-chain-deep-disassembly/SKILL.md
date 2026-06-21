---
name: industry-chain-deep-disassembly
description: Use when researching a growth industry through supply-chain topology, BOM/value nodes, current supply-gap bottlenecks, choke-point mechanisms, lead-time and qualified-capacity constraints, profit-pool migration, future supply-gap migration, and mandatory deep dives with duration estimates for identified bottleneck nodes. Stock mapping is optional and only follows node diagnosis.
---

# Industry Chain Deep Disassembly

## Purpose

Use this skill after `industry-research-router` when the user wants to understand how a growing industry works, where obvious supply gaps exist, what mechanism creates the bottleneck, and where the next supply gap may migrate.

This is an industry-chain research and node-disassembly skill first. A-share, HK-share, or global listed-company mapping is a downstream optional step after the bottleneck ledger is built; it must not drive the thesis.

Definition gate:

In this skill, 堵点/卡点 means an industry-chain node with an obvious supply gap in the stated time window: verified or strongly forecast demand exceeds qualified supply, usable capacity, yield, delivery capability, or customer-qualified vendor availability. High value share, high margin, high HHI, technical difficulty, long certification, domestic-substitution difficulty, or stock-market heat are not bottlenecks by themselves unless they create or prove a supply gap.

Mandatory follow-through: whenever a specified industry analysis identifies a node as `hard_bottleneck` or `soft_bottleneck`, continue with a deep dive on that exact node and estimate how long the bottleneck may persist before moving to final conclusions or optional stock mapping.

The core lens is:

`terminal demand -> chain topology -> BOM/value node -> demand-vs-qualified-supply gap -> current bottleneck -> constraint mechanism -> bottleneck-node deep dive -> persistence estimate -> future supply-gap migration -> evidence gap -> optional company mapping`

## When To Use

Use for:

- Growth industries where demand is accelerating but the winning node is unclear.
- AI hardware, manufacturing equipment, new materials, energy equipment, robotics, data-center infrastructure, high-end components, and other multi-layer supply chains.
- Questions about bottlenecks, choke points, shortages, delivery cycles, capacity expansion, yield ramps, BOM value share, profit pools, HHI, oligopoly, domestic substitution, or route-level supply constraints.
- Requests to identify current industry-chain堵点/卡点 and forecast likely future堵点/卡点 as technology generations, customer architectures, qualification cycles, or capacity plans change.
- Requests where 堵点/卡点 should specifically mean an obvious supply gap, not merely a moat, pricing-power node, or A-share concept label.
- Optional company or stock mapping only after the user asks for investable exposure, and only after the node-level bottleneck diagnosis is complete.

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
- Run `scripts/normalize_research_inputs.py` on user-provided raw data before HHI, bottleneck scoring, future-bottleneck scenarios, financial validation, or optional stock mapping. Missing required fields must stay as `N/A` and be treated as evidence gaps.
- Do not jump from A-share names to an industry conclusion. Stock mapping cannot replace chain topology, BOM/value-node analysis, current bottleneck diagnosis, or future bottleneck forecasting.
- Separate current bottlenecks from future bottlenecks. Current bottlenecks require demand-side evidence and supply-gap evidence such as extended lead time, allocation, price pressure, backlog, capacity utilization, qualified-capacity shortage, yield limit, certification queue, customer-lock-in, or downstream ramp delay. Future bottlenecks may be scenario-based but must state demand trigger, supply-lag mechanism, timing, and evidence gap.
- If any current supply-gap bottleneck is identified, do not stop at naming or ranking it. Deep-dive the node's exact constrained product or capacity, why adjacent supply cannot solve it, demand trigger, qualified vendor base, usable capacity/yield, expansion pipeline, customer qualification path, estimated persistence window, confidence, evidence basis, and reversal indicators.
- Do not classify a node as 堵点/卡点 if it only has high technology difficulty, high HHI, high gross margin, high BOM share, or long qualification cycle but no visible or forecast supply gap. Classify it as `strategic_node`, `pricing_power_node`, or `watch` instead.
- Separate global leader benchmarking from China tradable mapping: identify overseas/global oligarchs and the real technology path first, then map A-share/HK-share/China-local candidates only if the user asks for listed exposure after the bottleneck node is selected.

Evidence grades:

| Grade | Meaning |
|---|---|
| A | Filing, official announcement, prospectus, audited report, exchange disclosure, customer or supplier primary source |
| B | Reputable data vendor, industry association, sell-side report with cited source, credible media with named source |
| C | Unsourced web claim, social post, model output, concept-board label, or unverifiable secondary summary |

C-grade evidence can guide search priority only. It cannot support a main bottleneck conclusion, future bottleneck forecast, or stock pick without A/B confirmation.

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
| `global_leaders` | Overseas/global oligarchs, technology path, profit-pool benchmark | Before bottleneck diagnosis |
| `supply_chain_nodes` | BOM/value nodes, lead time, rigidity, substitution, concentration | Before bottleneck scoring and HHI |
| `bottleneck_ledger` | Current堵点/卡点 with explicit supply-gap evidence, constraint mechanism, affected downstream nodes | Before any company mapping |
| `future_bottleneck_scenarios` | Future supply-gap migration, trigger, supply-lag mechanism, timing, confidence, evidence gap | Before final conclusion |
| `china_candidates` | A-share/HK-share/China-local tradable exposure mapping | Optional, only after node selection |
| `financial_validation` | Margin, turnover, cash flow, capex, leverage checks | For pricing-power and optional company validation |
| `market_snapshot` | Market cap, float, valuation, turnover, trend, crowding | For timing and trading elasticity only |
| `source_evidence` | Claim-to-source ledger and limitations | Whenever evidence is mixed or disputed |

Connector boundary:

- Global market and financial data: use official filings/IR first, then `finance`, `alpha-vantage`, iFinD global stock MCP, or equivalent market-data tools.
- China market and financial data: use official filings, exchange disclosures, company IR, `allstock-data`, `finance`, and `stock-evaluator`.
- Live news, rumors, orders, policy, or recent price moves require the project evidence route before conclusions.

## Workflow

### 1. Define Demand Transmission

Identify the terminal product and demand driver before mapping companies.

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

### 3. Diagnose Current Bottlenecks And Constraint Mechanisms

Score each key node separately. Keep the raw reason next to every score, and distinguish "verified supply gap" from "high margin", "high value share", and "strategically important".

| Dimension | Score Guide |
|---|---|
| demand_pass_through | 0-5: terminal demand growth converts into this node's volume or ASP |
| supply_gap_severity | 0-5: verified demand exceeds qualified supply, usable capacity, yield, or delivery capability in the stated window |
| supply_rigidity | 0-5: new capacity, yield, certification, equipment, and permits are hard to add quickly |
| lead_time_pressure | 0-5: delivery or capacity cycle is long relative to demand change |
| substitution_resistance | 0-5: customers cannot switch technology or vendor quickly |
| concentration_pricing | 0-5: HHI, CR3/CR5, customer switching cost, allocation power, cost pass-through |
| profit_pool_migration | 0-5: margin, ASP, mix, or bargaining power is moving toward this node |
| financial_confirmation | 0-5: gross margin, net margin, receivables, inventory, and cash conversion confirm power |
| evidence_strength | 0-5: A/B evidence directly supports the supply gap rather than only a concept label |

Suggested classification:

| Pattern | Interpretation |
|---|---|
| high demand + clear supply gap + high rigidity + low substitution | true choke point |
| high demand + low rigidity | volume beneficiary, not pricing-power asset |
| high HHI + weak demand | oligopoly without near-term elasticity |
| high rigidity + no supply gap | strategic node or watch item, not a bottleneck |
| high concept heat + weak financial confirmation | story risk |
| high working-capital stress + rising revenue | possible forced shipment or weak bargaining power |

Build a current bottleneck ledger before moving on:

| Field | Required Check |
|---|---|
| bottleneck_node | precise material, component, equipment, process, capacity type, or qualification step |
| affected_chain_layer | upstream/midstream/downstream nodes constrained by it |
| demand_evidence | orders, capex, utilization, customer ramp, attach rate, backlog, policy, or guidance proving demand |
| supply_evidence | qualified capacity, usable capacity, yield, vendor availability, delivery capability, capex lag, or certification queue |
| supply_gap_evidence | direct proof that demand exceeds qualified supply: allocation, extended lead time, price pressure, unsatisfied orders, ramp delay, or explicit shortage |
| constraint_mechanism | capacity, yield, lead time, qualification, IP, equipment, raw material, regulation, customer lock-in, or logistics |
| severity | hard_bottleneck / soft_bottleneck / watch / rejected |
| time_horizon | current quarter, 6 months, 12 months, or longer |
| key_reversal | what would remove or reduce the bottleneck |

When a node scoring table is available, run:

```powershell
python skills/industry-chain-deep-disassembly/scripts/score_bottleneck_nodes.py --csv path/to/nodes.csv --pretty
```

The scoring script is a consistency aid. A node with only C-grade or missing evidence cannot be promoted above watch level.

### 4. Deep-Dive Confirmed Bottleneck Nodes And Estimate Duration

After the current bottleneck ledger, every node classified as `hard_bottleneck` or `soft_bottleneck` must receive a node-level deep dive before final synthesis or optional company mapping.

For each confirmed bottleneck, answer:

- What exact product, material grade, process step, capacity type, yield stage, or customer qualification is short.
- Why ordinary adjacent capacity, lower-end product capacity, or theme-adjacent supply cannot solve the shortage.
- Which demand trigger creates the gap and how terminal demand converts into this node's volume, value, or qualification load.
- Which supply constraints matter most: qualified vendors, usable capacity, yield ramp, equipment, permits, upstream raw material, logistics, or certification queue.
- What expansion or easing path exists, including announced capacity, second-source qualification, substitute route, yield improvement, or architecture redesign.
- How long the bottleneck may persist: give a quarter range, month range, or `N/A` if evidence is insufficient; include confidence and the evidence basis.
- What reversal indicators would show the bottleneck is easing.

Output a bottleneck deep-dive table:

| node | exact shortage | why adjacent supply cannot solve it | demand trigger | capacity/qualification constraint | expansion/easing path | estimated persistence | confidence | evidence basis | reversal indicator |
|---|---|---|---|---|---|---|---|---|---|

If persistence timing is not supported by A/B evidence or strong triangulation, mark the duration as `N/A` or `watch`, state the evidence gap, and avoid implying that the bottleneck will persist just because the stock theme is hot.

### 5. Forecast Future Bottleneck Migration

After current bottlenecks are identified and deep-dived, forecast how the supply-gap map can change over 6-24 months. Do not extrapolate today's shortage mechanically.

Check at least these migration drivers:

| Driver | Question |
|---|---|
| technology generation | Does the next product generation change material, component, process, power, thermal, packaging, or testing requirements? |
| demand step-up | Does a product ramp, customer architecture, policy, or capex cycle create demand above qualified supply? |
| capacity pipeline | Which announced capacity actually becomes qualified supply, and when? |
| yield ramp | Which node has hard yield learning curves or reliability requirements? |
| second-source qualification | Which customers can qualify alternative suppliers, and what cycle time is required? |
| architecture shift | Does customer architecture move value from one node to another? |
| regulation/resource constraint | Do export controls, permits, energy, water, mineral, or logistics constraints create a new choke point? |
| profit-pool migration | Is margin power moving upstream, midstream, downstream, or into equipment/software/IP? |

Classify future nodes as:

- `likely_future_bottleneck`: demand step-up and supply-lag mechanism are clear, and evidence is A/B or strongly triangulated.
- `watch`: plausible but demand trigger, supply-lag evidence, or timing is incomplete.
- `downgraded`: current bottleneck likely eases because capacity, yield, or second sourcing is improving.
- `resolved`: bottleneck evidence no longer holds under verified capacity or demand conditions.

Output a future scenario table:

| node | current status | future status | demand trigger | supply-lag mechanism | likely timing | confidence | evidence gap | reversal indicator |
|---|---|---|---|---|---|---|---|---|

### 6. Calculate Concentration As A Supporting Test

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
- HHI can upgrade confidence only when demand pass-through, an actual current or forecast supply gap, supply rigidity, substitution resistance, and the current/future constraint mechanism are also supported by A/B evidence.

### 7. Optional Company Or Stock Mapping After Node Selection

Skip this section unless the user explicitly asks for listed companies, tradable exposure, or investment mapping.

Do not start from hot stock names. First select bottleneck nodes and future-bottleneck scenarios, then map companies.

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

### 8. Separate The Three Rankings When Stocks Are Requested

When stocks are requested, always separate:

- Fundamental quality: moat, customer quality, margin durability, balance-sheet quality, long-term competitive position.
- Earnings elasticity: revenue contribution, ASP leverage, capacity utilization, operating leverage, gross margin sensitivity.
- Trading elasticity: float market cap, liquidity, volatility, catalyst density, expectation gap, crowding, technical position.

Do not merge these into one vague "best stock" score.

### 9. Risk And Reversal Watch

For every selected node, future scenario, and optional stock, state what would break the thesis:

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
- 当前产业链最大供需矛盾：
- 当前最关键堵点/卡点（必须是明显供应缺口）：
- 供应缺口证据：
- 堵点形成机制：
- 已识别堵点的深拆和持续时间判断：
- 未来 6-24 个月最可能迁移到的新供应缺口：
- 最大反转风险：

产业链拓扑与 BOM：
| layer | node | BOM/value share | lead time | supply rigidity | substitution | top players | evidence |

当前堵点台账：
| node | affected layer | demand evidence | supply evidence | supply gap evidence | constraint mechanism | severity | time horizon | reversal |

堵点深拆与持续时间：
| node | exact shortage | why adjacent supply cannot solve it | demand trigger | capacity/qualification constraint | expansion/easing path | estimated persistence | confidence | evidence basis | reversal indicator |

未来卡点预判：
| node | current status | future status | demand trigger | supply-lag mechanism | likely timing | confidence | evidence gap | reversal indicator |

集中度/定价权辅助验证：
| node | HHI/CR3 | pricing mechanism | demand pass-through | substitution resistance | verdict |

可选：个股交叉验证（只有用户要求股票映射时输出）：
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
- Letting A-share/HK-share/US-share mapping dominate a task that is asking for industry-chain structure and bottleneck disassembly.
- Treating HHI as proof of pricing power without demand and switching-cost evidence.
- Treating high HHI, high margin, high BOM value, high technical barrier, or domestic-substitution difficulty as 堵点/卡点 without evidence of a supply gap.
- Calling every long lead-time product a bottleneck while ignoring capacity expansion already under way.
- Confusing current堵点/卡点 with future potential bottlenecks, or listing current shortages without forecasting where the next choke point may migrate.
- Mixing board-level PCB, ABF substrate, CCL, resin, glass fiber, copper foil, equipment, and assembly as one undifferentiated "AI hardware" bucket.
- Using concept-board names instead of exact product exposure and revenue materiality.
- Ignoring working capital. Real bargaining power usually improves cash conversion or at least prevents severe deterioration.
