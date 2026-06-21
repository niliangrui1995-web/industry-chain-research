# Data Interfaces

Use this reference when the user provides research data files, asks to connect market or financial data, or needs a reusable evidence table for industry-chain disassembly.

## Principle

Data interfaces are evidence contracts, not automatic truth sources. They define what fields the skill needs and how to normalize inputs. Current prices, financials, filings, orders, lead times, market share, and BOM values still require live or source-backed verification.

Default analysis order:

1. `global_leaders`: overseas or global oligarch benchmarks that reveal the real technology path and profit pool.
2. `supply_chain_nodes`: BOM/value nodes, lead time, capacity rigidity, substitution, and concentration.
3. `bottleneck_ledger`: current堵点/卡点 with explicit supply-gap evidence, demand evidence, supply evidence, constraint mechanism, severity, and reversal watch.
4. `future_bottleneck_scenarios`: likely future supply-gap migration, demand trigger, supply-lag mechanism, timing, confidence, and evidence gap.
5. `china_candidates`: optional A-share/HK-share or China-local tradable mapping after node selection, only when the user asks for listed exposure.
6. `financial_validation`: margin, working capital, and cash-flow checks.
7. `market_snapshot`: valuation, liquidity, trend, and crowding context.

## Supported Input Formats

Use `scripts/normalize_research_inputs.py` to normalize raw inputs:

```powershell
python skills/industry-chain-deep-disassembly/scripts/normalize_research_inputs.py --input data.xlsx --pretty
python skills/industry-chain-deep-disassembly/scripts/normalize_research_inputs.py --input leaders.csv --table global_leaders --pretty
python skills/industry-chain-deep-disassembly/scripts/normalize_research_inputs.py --input research.json --out normalized.json
```

Accepted formats:

- CSV: one file per table, or use `--table`.
- JSON: either `{ "global_leaders": [...] }` style, or a list with `--table`.
- JSONL: one row per line with `--table`.
- XLSX: one sheet per table. Sheet names can use table names or common aliases.
- stdin: use `--input - --table <table_name>` for CSV input.

Windows note: when CSV headers contain Chinese, prefer passing a UTF-8 CSV/XLSX file path instead of a PowerShell here-string pipe unless the terminal encoding is explicitly controlled.

## Common Chinese Headers

脚本支持常见中文表头，便于把本地 Excel、CSV 或手工整理表直接归一化为标准字段。

| 中文表头 | Canonical Field | Typical Table |
|---|---|---|
| 公司 / 公司名称 | `company` | `global_leaders`, `china_candidates`, `financial_validation`, `market_snapshot` |
| 代码 / 证券代码 | `ticker` | company and market tables |
| 交易所 / 市场 | `exchange` | company and market tables |
| 国家 | `country` | `global_leaders` |
| 节点 / 环节 | `node` or `linked_node` | chain-node tables use `node`; company tables map it to `linked_node` |
| 层级 | `layer` | `supply_chain_nodes` |
| 价值量 / BOM价值 | `BOM_or_value_share` | `supply_chain_nodes` |
| 交期 / 交货时滞 | `lead_time` | `supply_chain_nodes` |
| 供给刚性 | `capacity_rigidity` | `supply_chain_nodes` |
| 替代弹性 | `substitution_elasticity` | `supply_chain_nodes` |
| 市占率 | `market_share` | `supply_chain_nodes` |
| 需求证据 | `demand_evidence` | `bottleneck_ledger` |
| 供给证据 | `supply_evidence` | `bottleneck_ledger` |
| 供应缺口证据 | `supply_gap_evidence` | `bottleneck_ledger` |
| 约束机制 / 卡点机制 | `constraint_mechanism` | `bottleneck_ledger` |
| 影响层级 | `affected_chain_layer` | `bottleneck_ledger` |
| 严重程度 | `severity` | `bottleneck_ledger` |
| 时间维度 | `time_horizon` | `bottleneck_ledger` |
| 未来状态 | `future_status` | `future_bottleneck_scenarios` |
| 需求触发 | `demand_trigger` | `future_bottleneck_scenarios` |
| 供给滞后机制 | `supply_lag_mechanism` | `future_bottleneck_scenarios` |
| 预计时间 | `likely_timing` | `future_bottleneck_scenarios` |
| 证据缺口 | `evidence_gap` | `future_bottleneck_scenarios` |
| 毛利率 / 净利率 | `gross_margin` / `net_margin` | `financial_validation` |
| 应收账款周转率 / 存货周转率 | `receivables_turnover` / `inventory_turnover` | `financial_validation` |
| 市值 / 流通市值 / 换手率 | `market_cap` / `float_market_cap` / `turnover` | `market_snapshot` |
| 5日涨幅 / 20日涨幅 / 60日涨幅 | `pct_chg_5d` / `pct_chg_20d` / `pct_chg_60d` | `market_snapshot` |
| 纯度 / 收入占比 | `pure_play_level` / `revenue_materiality` | `china_candidates` |
| 基本面质量 / 业绩弹性 / 交易弹性 | `fundamental_quality` / `earnings_elasticity` / `trading_elasticity` | `china_candidates` |
| 证据等级 / 来源 | `evidence_grade` / `source` | all tables |

## Canonical Tables

### global_leaders

Use for overseas or global leaders such as US, Taiwan, Japan, Korea, or Europe-listed oligarchs.

Required: `company`, `ticker`, `exchange`, `country`

Recommended fields:

| field | use |
|---|---|
| linked_node | supply-chain node or segment |
| segment_exposure | product or segment exposure |
| revenue_mix | segment revenue or qualitative mix |
| gross_margin | current or recent gross margin |
| capex | capex or expansion direction |
| backlog_or_orders | backlog, bookings, orders, or guidance |
| market_cap | market cap with date/source |
| valuation | PE/PB/EV multiple or N/A |
| price_trend | 5/20/60-day or qualitative trend |
| evidence_grade | A/B/C/N/A |
| source | source note |

Preferred data path: official filings and IR first; `finance`, `alpha-vantage`, iFinD global stock MCP, or other global market-data tools for market snapshot.

### supply_chain_nodes

Use for BOM/value and bottleneck nodes.

Required: `node`, `layer`

Recommended fields:

| field | use |
|---|---|
| BOM_or_value_share | BOM cost share, value share, revenue share, or N/A |
| margin_proxy | gross margin, operating margin, spread proxy, or N/A |
| lead_time | delivery cycle or capacity expansion cycle |
| capacity_rigidity | low/medium/high/N/A |
| substitution_elasticity | low/medium/high/N/A |
| top_players | global and domestic leaders |
| market_share | share data if verified |
| pricing_mechanism | spot, contract, cost-plus, LTA, allocation, qualification lock-in |
| evidence_grade | A/B/C/N/A |
| source | source note |

Preferred data path: official sources, prospectuses, industry associations, reputable data vendors, and `references/source-priority.md`.

### bottleneck_ledger

Use for current industry-chain堵点/卡点 after the topology and BOM/value-node table are built. In this table, a 堵点/卡点 must mean an obvious supply gap: demand exceeds qualified supply, usable capacity, yield, delivery capability, or customer-qualified vendor availability in the stated window. This table must exist before optional company mapping.

Required: `bottleneck_node`, `supply_gap_evidence`, `constraint_mechanism`

Recommended fields:

| field | use |
|---|---|
| affected_chain_layer | upstream/midstream/downstream nodes constrained by the bottleneck |
| demand_evidence | orders, capex, utilization, customer ramp, attach rate, backlog, policy, or guidance proving demand |
| supply_evidence | qualified capacity, usable capacity, yield, vendor availability, delivery capability, capex lag, or certification queue |
| supply_gap_evidence | direct proof that demand exceeds qualified supply: allocation, extended lead time, price pressure, unsatisfied orders, ramp delay, or explicit shortage |
| constraint_mechanism | capacity, yield, lead time, qualification, equipment, raw material, regulation, customer lock-in, or logistics |
| severity | hard_bottleneck, soft_bottleneck, watch, or rejected |
| time_horizon | current quarter, 6 months, 12 months, or longer |
| key_reversal | what removes or reduces the bottleneck |
| evidence_grade | A/B/C/N/A |
| source | source note |

Preferred data path: A/B evidence from filings, customer or supplier disclosures, credible industry data, lead-time and price evidence, and source-backed capacity or yield records.

### future_bottleneck_scenarios

Use for 6-24 month supply-gap migration after current bottlenecks are diagnosed. Future scenarios may be probabilistic but must show demand trigger, supply-lag mechanism, and evidence gap. A node with only high HHI, high margin, technical difficulty, or domestic-substitution difficulty is not a future bottleneck unless it is expected to create a supply gap.

Required: `node`, `future_status`, `demand_trigger`, `supply_lag_mechanism`

Recommended fields:

| field | use |
|---|---|
| current_status | current bottleneck state: hard_bottleneck, soft_bottleneck, watch, downgraded, resolved, or N/A |
| future_status | likely_future_bottleneck, watch, downgraded, or resolved |
| demand_trigger | product ramp, customer architecture, capex cycle, policy, or technology change that raises demand |
| supply_lag_mechanism | why qualified supply cannot catch up: capacity, yield, qualification, equipment, raw material, regulation, or logistics |
| likely_timing | expected timing or scenario window |
| confidence | high/medium/low/N/A |
| evidence_gap | missing evidence needed to raise confidence |
| reversal_indicator | data point that would break the scenario |
| evidence_grade | A/B/C/N/A |
| source | source note |

Preferred data path: technology roadmaps, customer architecture changes, capacity schedules, yield ramp evidence, second-source qualification cycles, resource/regulatory constraints, and profit-pool migration evidence.

### china_candidates

Use only after the bottleneck node is selected and the user asks for listed exposure. This table is for A-share, HK-share, or China-local tradable mapping; it is not the default industry-chain output.

Required: `company`, `ticker`

Recommended fields:

| field | use |
|---|---|
| exchange | SSE/SZSE/BSE/HKEX or N/A |
| linked_node | selected bottleneck node |
| exposure_evidence | product, customer, order, capacity, certification, or filing evidence |
| pure_play_level | high/medium/low |
| revenue_materiality | exact percentage or qualitative disclosure |
| fundamental_quality | high/medium/low/N/A |
| earnings_elasticity | high/medium/low/N/A |
| trading_elasticity | high/medium/low/N/A |
| verdict | main_candidate, watch_only, theme_adjacent, reject |
| evidence_grade | A/B/C/N/A |
| source | source note |

Preferred data path: `allstock-data`, `stock-evaluator`, official filings, exchange disclosures, and company IR.

### financial_validation

Use for both overseas leaders and China candidates when validating pricing power and bargaining position.

Required: `company`, `ticker`, `period`

Recommended fields:

| field | use |
|---|---|
| revenue | revenue for period |
| gross_margin | gross margin |
| net_margin | net margin |
| receivables_turnover | receivables turnover |
| inventory_turnover | inventory turnover |
| operating_cash_flow | operating cash flow |
| capex | capex |
| debt_or_net_cash | leverage or net cash |
| evidence_grade | A/B/C/N/A |
| source | source note |

### market_snapshot

Use for timing, valuation, liquidity, and trading elasticity. It cannot prove beneficiary status.

Required: `ticker`, `exchange`, `date`

Recommended fields:

| field | use |
|---|---|
| company | company name |
| market_cap | total market cap |
| float_market_cap | float market cap where available |
| pe | PE or N/A |
| pb | PB or N/A |
| turnover | turnover rate or traded value |
| pct_chg_5d | 5-day performance |
| pct_chg_20d | 20-day performance |
| pct_chg_60d | 60-day performance |
| volume | volume |
| evidence_grade | A/B/C/N/A |
| source | source note |

### demand_indicators

Use for terminal demand and forward indicators.

Required: `indicator`

Recommended fields: `value`, `direction`, `source`, `evidence_grade`, `caveat`

### node_scores

Use with `scripts/score_bottleneck_nodes.py`.

Required: `node`, `demand_pass_through`, `supply_gap_severity`, `supply_rigidity`, `lead_time_pressure`, `substitution_resistance`, `concentration_pricing`, `profit_pool_migration`, `financial_confirmation`

Recommended fields: `evidence_strength`, `evidence_grade`, `reason`

### source_evidence

Use when tracking claim-to-source mapping across files and web evidence.

Required: `claim`, `source`

Recommended fields: `claim_type`, `entity`, `url_or_file`, `date`, `evidence_grade`, `limitation`

## Connector Boundary

- Global leader market data: use `finance`, `alpha-vantage`, iFinD global stock MCP, official filings, and company IR.
- China market data: use `allstock-data`, `finance`, `stock-evaluator`, exchange filings, and company IR.
- Live news or rumor discovery: use the project route through `ai-chain-research-orchestrator`, Grok/X, Gemini only when needed, then verify.
- The data-interface script does not fetch from the internet. It normalizes verified or user-provided inputs.
