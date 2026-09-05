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
| physical_level | string | system, module, component, material, equipment, process, service |
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
| claim_as_of | string | current ledger cutoff; must equal companion and top-level `as_of` |
| evidence_check_id | string | unique same-packet bottleneck evidence check ID |
| evidence_review_status | string | must equal normalizer-computed eligible_for_bottleneck_review for hard/soft |
| affected_chain_layer | string | upstream, midstream, downstream, or cross-layer |
| demand_evidence | string | orders, capex, utilization, customer ramp, attach rate, backlog, policy, or guidance proving demand |
| supply_evidence | string | qualified capacity, usable capacity, yield, vendor availability, delivery capability, capex lag, or certification queue |
| supply_gap_evidence | string | proof that demand exceeds qualified supply: allocation, extended lead time, price pressure, unsatisfied orders, ramp delay, or explicit shortage |
| constraint_mechanism | string | capacity, yield, lead time, qualification, IP, equipment, raw material, regulation, customer lock-in, or logistics |
| severity | string | hard_bottleneck, soft_bottleneck, watch, or rejected |
| time_horizon | string | current quarter, 6 months, 12 months, or longer |
| substitution_path | string | feasible alternative technology, material, capacity, or architecture |
| second_source_status | string | none, evaluating, qualifying, qualified, ramping, active, N/A |
| relief_window | string | expected easing window and basis |
| positive_validation | string | evidence that confirms the shortage mechanism |
| counterevidence | string | evidence that weakens or disproves the shortage |
| prior_status | string | previous recorded status or N/A |
| status_change | string | new, upgraded, unchanged, downgraded, resolved, rejected |
| key_reversal | string | what removes or reduces the bottleneck |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

Strict mode rejects blank/bare semantic placeholders in required fields. `severity` and `status_change` must use the enums shown above. Every hard/soft row must uniquely match a same-node, same-severity, same-time-horizon current evidence check; ledger/check `claim_as_of` must equal top-level `as_of`. The normalizer recomputes eligibility and rejects self-reported status. Historical rows are watch/rejected; future claims use `future_bottleneck_scenarios`.

For hard/soft rows, all repeated evidence fields must equal the authoritative companion after normalization and surrounding-whitespace trimming: demand/supply/gap evidence, constraint mechanism, substitution path, second-source status, relief window, positive validation, counterevidence, key reversal, evidence grade, and source. Use report prose for summaries; changes require an updated and revalidated companion.

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
| evidence_date | string | ISO evidence date/timestamp no later than explicit `as_of` |
| future_max_age_days | integer | optional freshness window; default and maximum 365 |
| source_type | string | regulatory, official, company_original, official_counterparty, credible_third_party, social, anonymous, or lead_only |
| source_locator | string | reproducible URL, filing ID, or file locator |
| evidence_grade | string | A, B, C, or N/A |
| source | string | source note |

For `likely_future_bottleneck`, `likely_timing`, `confidence`, `evidence_gap`, `reversal_indicator`, `evidence_date`, `source_type`, `source_locator`, `evidence_grade`, and `source` are strict-required. Likely/high requires evidence within `future_max_age_days` and traceable A/B `regulatory|official|company_original|official_counterparty|credible_third_party`; stale or weak evidence is limited to low-confidence watch.

### stock_candidates

Alias: `china_candidates` in the data-interface normalizer.

Use only when the user asks for listed exposure after node diagnosis.

| column | type | note |
|---|---|---|
| company | string | listed company name |
| ticker | string | include exchange suffix when known |
| exchange | string | SSE, SZSE, BSE, HKEX, or other exact venue |
| linked_node | string | selected bottleneck node |
| exposure_evidence | string | product, customer, order, capacity, certification, or filing evidence |
| commercialization_stage | string | rd_plan, sampling, validation, design_win, qualification, mass_production, shipment, revenue, or profit_cashflow |
| stage_evidence | string | evidence supporting this stage only; do not imply the next stage |
| stage_evidence_date | string | ISO date/timestamp of the stage evidence, not later than explicit `as_of` |
| stage_claim_window | string | current or historical |
| stage_max_age_days | integer | optional freshness window; default and maximum 365 |
| stage_source | string | source description for the stage |
| stage_source_type | string | regulatory, official, company_original, official_counterparty, third_party, social, anonymous, or lead_only |
| stage_source_locator | string | reproducible URL, filing ID, announcement number, or file locator |
| pure_play_level | string | high, medium, low |
| revenue_materiality | string | exact percentage or qualitative disclosure |
| evidence_gap | string | specific missing evidence when materiality is undisclosed |
| gross_margin_trend | string | latest verified trend or N/A |
| net_margin_trend | string | latest verified trend or N/A |
| receivables_turnover | string/number | verified value or N/A |
| inventory_turnover | string/number | verified value or N/A |
| operating_cash_flow | string/number | verified value or N/A |
| fundamental_quality | string | high, medium, low, N/A |
| earnings_elasticity | string | high, medium, low, N/A |
| trading_elasticity | string | high, medium, low, N/A |
| verdict | string | main_candidate, watch_only, theme_adjacent, reject; research priority, not realized-benefit status |
| inclusion_reason | string | evidence-backed reason to retain the candidate |
| rejection_reason | string | reason for exclusion or downgrade |
| next_evidence | string | next source or KPI needed to change the verdict |
| evidence_grade | string | A, B, C, or N/A |
| source | string | traceable source note |

Strict candidates require `company`, `ticker`, `exchange`, `linked_node`, `exposure_evidence`, the stage evidence/date/window/source/type/locator fields, `evidence_grade`, and `verdict`. `stage_evidence_date` must be ISO-8601 and no later than explicit `as_of`. Current evidence must be within `stage_max_age_days`; older evidence is valid only as historical watch/theme-adjacent/reject and can never support a main candidate. Long-standing realized stages use the latest formal report/current official confirmation date. `revenue`, `profit_cashflow`, or `main_candidate` requires A-grade, traceable `regulatory|official|company_original|official_counterparty` evidence; weak source types cannot support a realized stage or main candidate. Realized-revenue stages require `revenue_materiality` or a specific `evidence_gap`; `main_candidate` cannot use the gap fallback and cannot be disconnected from its node, exposure evidence, or source.

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
| date | string | ISO snapshot date/timestamp, not later than explicit `as_of` |
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

### bottleneck_evidence_checks

This table can be passed to `scripts/validate_bottleneck_evidence.py`. It checks completeness and declared-severity consistency, but never assigns a bottleneck score or conclusion.

| column | type | note |
|---|---|---|
| check_id | string | unique evidence packet ID used by hard/soft ledger companions |
| node | string | precise node name |
| severity | string | hard_bottleneck, soft_bottleneck, watch, or rejected |
| claim_window | string | current, future, or historical |
| claim_as_of | string | ISO date/timestamp at which the bottleneck claim is evaluated |
| max_age_days | integer | optional freshness window; default 180, allowed 1-365 |
| demand_evidence_kind | string | quantified_demand, demand_step, or qualitative_signal |
| supply_evidence_kind | string | qualified_supply_limit, usable_capacity_limit, yield_limit, delivery_limit, certified_supplier_limit, or qualitative_constraint |
| demand_evidence | string | dated evidence of demand |
| demand_evidence_date | string | ISO date/timestamp of demand evidence |
| demand_source_type / demand_source_locator | string | structured source tier and reproducible locator for demand evidence |
| supply_evidence | string | qualified/usable supply evidence |
| supply_evidence_date | string | ISO date/timestamp of supply evidence |
| supply_source_type / supply_source_locator | string | structured source tier and reproducible locator for supply evidence |
| supply_gap_evidence | string | evidence demand exceeds qualified supply |
| gap_evidence_date | string | ISO date/timestamp of direct gap evidence |
| gap_source_type / gap_source_locator | string | structured source tier and reproducible locator for direct gap evidence |
| direct_gap_consequence | string | allocation, unmet order, delivery delay, or another direct consequence |
| constraint_mechanism | string | capacity, yield, qualification, equipment, material, regulation, logistics |
| time_horizon | string | window in which the claimed gap exists |
| evidence_grade | string | A, B, C, or N/A |
| source | string | traceable source note |
| source_date | string | ISO publication/access date for the cited source |
| substitution_path | string | feasible substitute, or N/A with search scope |
| second_source_status | string | none, evaluating, qualifying, qualified, ramping, active, or N/A |
| relief_window | string | expected easing window and evidence basis |
| positive_validation | string | evidence that would confirm the shortage mechanism |
| counterevidence | string | evidence weakening the claim, or N/A with search scope |
| key_reversal | string | observable event that removes or reduces the bottleneck |

All claim/evidence dates must be no later than explicit `as_of`, and evidence dates cannot be later than `claim_as_of`. Current hard/soft evidence older than `max_age_days` is ineligible; stale evidence may remain historical/watch/incomplete. Hard requires primary traceable source types on all three legs; soft may additionally use `credible_third_party`; weak sources are watch-only. The validator otherwise checks completeness and declared-severity consistency only. A hard claim requires a current A-grade closed loop and no qualified/ramping/active alternative; it never receives hard status merely because the packet passes.
