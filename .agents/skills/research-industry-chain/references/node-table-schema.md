# Node Table Schema

Use this reference when building a reusable industry-chain table or spreadsheet.

## Required Tables

For full data-interface contracts and connector boundaries, read `data-interfaces.md`.

### demand_indicators

| column | type | note |
|---|---|---|
| indicator | string | order, capex, utilization, backlog, attach rate, inventory, policy, guidance |
| value | string/number | exact value or qualitative status |
| direction | string | positive, neutral, negative, mixed, N/A |
| source | string | source name or file |
| evidence_grade | string | A, B, C, or N/A |
| caveat | string | what could make the signal misleading |

### chain_nodes

Alias: `supply_chain_nodes` in the data-interface normalizer.

| column | type | note |
|---|---|---|
| layer | string | upstream, midstream, downstream |
| node | string | precise product/material/equipment/process/service |
| BOM_or_value_share | string/number | unit cost share, value share, revenue share, or N/A |
| margin_proxy | string/number | gross margin, operating margin, spread proxy, or N/A |
| lead_time | string/number | delivery cycle or capacity expansion cycle |
| capacity_rigidity | string | low, medium, high, N/A |
| substitution_elasticity | string | low, medium, high, N/A |
| top_players | string | global and domestic leaders |
| market_share | string | company shares if verified |
| hhi | number | from calculate_hhi.py, or N/A |
| pricing_mechanism | string | spot, contract, cost-plus, LTA, allocation, qualification lock-in |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

### bottleneck_ledger

| column | type | note |
|---|---|---|
| bottleneck_node | string | precise material/component/equipment/process/capacity/qualification step |
| affected_chain_layer | string | upstream, midstream, downstream, or cross-layer |
| demand_evidence | string | orders, capex, utilization, customer ramp, attach rate, backlog, policy, or guidance proving demand |
| supply_evidence | string | qualified capacity, usable capacity, yield, vendor availability, delivery capability, capex lag, or certification queue |
| supply_gap_evidence | string | proof that demand exceeds qualified supply: allocation, extended lead time, price pressure, unsatisfied orders, ramp delay, or explicit shortage |
| constraint_mechanism | string | capacity, yield, lead time, qualification, IP, equipment, raw material, regulation, customer lock-in, or logistics |
| severity | string | hard_bottleneck, soft_bottleneck, watch, or rejected |
| time_horizon | string | current quarter, 6 months, 12 months, or longer |
| key_reversal | string | what removes or reduces the bottleneck |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

### future_bottleneck_scenarios

| column | type | note |
|---|---|---|
| node | string | precise future bottleneck candidate |
| current_status | string | current bottleneck status or N/A |
| future_status | string | likely_future_bottleneck, watch, downgraded, or resolved |
| demand_trigger | string | product ramp, customer architecture, capex cycle, policy, or technology change that raises demand |
| supply_lag_mechanism | string | capacity, yield, qualification, equipment, raw material, regulation, or logistics lag that can create a supply gap |
| likely_timing | string | expected scenario window |
| confidence | string | high, medium, low, or N/A |
| evidence_gap | string | missing evidence needed to raise confidence |
| reversal_indicator | string | data point that breaks the scenario |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

### stock_candidates

Alias: `china_candidates` in the data-interface normalizer.

Use only when the user asks for listed exposure after node diagnosis.

| column | type | note |
|---|---|---|
| company | string | listed company name |
| ticker | string | include exchange suffix when known |
| linked_node | string | selected bottleneck node |
| exposure_evidence | string | product, customer, order, capacity, certification, or filing evidence |
| pure_play_level | string | high, medium, low |
| revenue_materiality | string | exact percentage or qualitative disclosure |
| gross_margin_trend | string | latest verified trend or N/A |
| net_margin_trend | string | latest verified trend or N/A |
| receivables_turnover | string/number | verified value or N/A |
| inventory_turnover | string/number | verified value or N/A |
| operating_cash_flow | string/number | verified value or N/A |
| fundamental_quality | string | high, medium, low, N/A |
| earnings_elasticity | string | high, medium, low, N/A |
| trading_elasticity | string | high, medium, low, N/A |
| verdict | string | main_candidate, watch_only, theme_adjacent, reject |

### global_leaders

| column | type | note |
|---|---|---|
| company | string | global or overseas leader name |
| ticker | string | ticker with market suffix when needed |
| exchange | string | listing venue |
| country | string | domicile or primary market |
| linked_node | string | supply-chain node |
| segment_exposure | string | product or segment exposure |
| revenue_mix | string/number | segment mix or N/A |
| gross_margin | string/number | verified gross margin or N/A |
| capex | string/number | capex or expansion signal |
| backlog_or_orders | string | backlog, bookings, orders, or guidance |
| market_cap | string/number | market cap with date/source |
| valuation | string/number | PE/PB/EV multiple or N/A |
| price_trend | string | 5/20/60-day trend or qualitative trend |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

### financial_validation

| column | type | note |
|---|---|---|
| company | string | company name |
| ticker | string | ticker |
| period | string | reporting period |
| revenue | string/number | revenue |
| gross_margin | string/number | gross margin |
| net_margin | string/number | net margin |
| receivables_turnover | string/number | receivables turnover |
| inventory_turnover | string/number | inventory turnover |
| operating_cash_flow | string/number | operating cash flow |
| capex | string/number | capex |
| debt_or_net_cash | string/number | leverage or net cash |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

### market_snapshot

| column | type | note |
|---|---|---|
| company | string | company name |
| ticker | string | ticker |
| exchange | string | listing venue |
| date | string | snapshot date |
| market_cap | string/number | total market cap |
| float_market_cap | string/number | float market cap when available |
| pe | string/number | PE or N/A |
| pb | string/number | PB or N/A |
| turnover | string/number | turnover rate or traded value |
| pct_chg_5d | string/number | 5-day performance |
| pct_chg_20d | string/number | 20-day performance |
| pct_chg_60d | string/number | 60-day performance |
| volume | string/number | volume |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

### node_scores

This table can be passed to `scripts/score_bottleneck_nodes.py`.

| column | type | note |
|---|---|---|
| node | string | precise node name |
| demand_pass_through | number | 0-5 |
| supply_gap_severity | number | 0-5 supply-gap score |
| supply_rigidity | number | 0-5 |
| lead_time_pressure | number | 0-5 |
| substitution_resistance | number | 0-5 |
| concentration_pricing | number | 0-5 |
| profit_pool_migration | number | 0-5 |
| financial_confirmation | number | 0-5 |
| evidence_strength | number | optional 0-5 evidence-strength score |
| evidence_grade | string | A, B, C, or N/A |
| reason | string | short evidence-backed explanation |
