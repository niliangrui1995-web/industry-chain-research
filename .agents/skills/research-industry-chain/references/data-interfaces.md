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
python .agents/skills/research-industry-chain/scripts/normalize_research_inputs.py --input data.xlsx --as-of 2026-07-27 --pretty
python .agents/skills/research-industry-chain/scripts/normalize_research_inputs.py --input leaders.csv --table global_leaders --as-of 2026-07-27 --pretty
python .agents/skills/research-industry-chain/scripts/normalize_research_inputs.py --input research.json --as-of 2026-07-27 --out normalized.json
```

Accepted formats:

- CSV: one file per table, or use `--table`.
- JSON: either `{ "global_leaders": [...] }` style, or a list with `--table`.
- JSONL: one row per line with `--table`.
- XLSX: one sheet per table. Sheet names can use table names or common aliases.
- stdin: use `--input - --table <table_name>` for CSV input.

`--as-of YYYY-MM-DD` is required for deterministic normalization and is preserved as top-level `as_of`. `stage_evidence_date`, bottleneck claim/evidence dates, `market_snapshot.date`, and `source_evidence.date` must be valid ISO dates/timestamps and cannot be later than this cutoff. The tool never substitutes the machine date.

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
| 未来证据最大年龄天数 | `future_max_age_days` | `future_bottleneck_scenarios` |
| 毛利率 / 净利率 | `gross_margin` / `net_margin` | `financial_validation` |
| 应收账款周转率 / 存货周转率 | `receivables_turnover` / `inventory_turnover` | `financial_validation` |
| 市值 / 流通市值 / 换手率 | `market_cap` / `float_market_cap` / `turnover` | `market_snapshot` |
| 5日涨幅 / 20日涨幅 / 60日涨幅 | `pct_chg_5d` / `pct_chg_20d` / `pct_chg_60d` | `market_snapshot` |
| 纯度 / 收入占比 | `pure_play_level` / `revenue_materiality` | `china_candidates` |
| 商业化阶段 / 阶段证据 / 阶段日期 / 阶段来源 | `commercialization_stage` / `stage_evidence` / `stage_evidence_date` / `stage_source` | `china_candidates` |
| 阶段来源类型 / 阶段来源定位 | `stage_source_type` / `stage_source_locator` | `china_candidates` |
| 阶段声明窗口 / 阶段最大证据年龄天数 | `stage_claim_window` / `stage_max_age_days` | `china_candidates` |
| 声明时点 / 需求证据日期 / 供给证据日期 / 缺口证据日期 / 来源日期 | `claim_as_of` / `demand_evidence_date` / `supply_evidence_date` / `gap_evidence_date` / `source_date` | `bottleneck_evidence_checks` |
| 最大证据年龄天数 | `max_age_days` | `bottleneck_evidence_checks` |
| 纳入理由 / 淘汰理由 / 下一验证证据 | `inclusion_reason` / `rejection_reason` / `next_evidence` | `china_candidates` |
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

Required: `bottleneck_node`, `demand_evidence`, `supply_evidence`, `supply_gap_evidence`, `constraint_mechanism`, `severity`, `time_horizon`, `substitution_path`, `second_source_status`, `relief_window`, `positive_validation`, `counterevidence`, `status_change`, `key_reversal`, `evidence_grade`, `source`. Strict normalization rejects blank values and bare semantic placeholders such as `N/A`, `unknown`, `blocked`, `pending`, `TODO`, `TBD`, `-`, `--`, `evidence_absent`, and `not_found`. Unknown items must instead describe the search scope or evidence gap. `prior_status` may be `N/A` for a genuinely new node.

`severity` is limited to `hard_bottleneck|soft_bottleneck|watch|rejected`; `status_change` is limited to `new|upgraded|unchanged|downgraded|resolved|rejected`. A `hard_bottleneck` claim must also pass the structured severity-consistency gate in `validate_bottleneck_evidence.py`.

Every hard/soft ledger row must provide `claim_as_of`, `evidence_check_id`, and `evidence_review_status`. The ID must uniquely match a same-packet `bottleneck_evidence_checks.check_id` with `claim_window=current`, the same node/severity/time horizon, and ledger/check `claim_as_of` both equal to top-level `as_of`. The claimed status must equal the normalizer-computed `eligible_for_bottleneck_review`. Historical evidence stays watch/rejected; future claims use `future_bottleneck_scenarios`.

Recommended fields:

| field | use |
|---|---|
| affected_chain_layer | upstream/midstream/downstream nodes constrained by the bottleneck |
| claim_as_of / evidence_check_id / evidence_review_status | current cutoff, unique companion packet, and computed eligibility |
| demand_evidence | orders, capex, utilization, customer ramp, attach rate, backlog, policy, or guidance proving demand |
| supply_evidence | qualified capacity, usable capacity, yield, vendor availability, delivery capability, capex lag, or certification queue |
| supply_gap_evidence | direct proof that demand exceeds qualified supply: allocation, extended lead time, price pressure, unsatisfied orders, ramp delay, or explicit shortage |
| constraint_mechanism | capacity, yield, lead time, qualification, equipment, raw material, regulation, customer lock-in, or logistics |
| severity | hard_bottleneck, soft_bottleneck, watch, or rejected |
| time_horizon | current quarter, 6 months, 12 months, or longer |
| substitution_path | alternative technology, material, supplier, capacity, or architecture |
| second_source_status | none/evaluating/qualifying/qualified/ramping/active/N/A |
| relief_window | when and why the gap may ease |
| positive_validation | observable evidence that confirms the shortage mechanism |
| counterevidence | evidence that weakens the claim, or N/A with search scope |
| prior_status / status_change | previous state and new/upgraded/unchanged/downgraded/resolved/rejected |
| key_reversal | what removes or reduces the bottleneck |
| evidence_grade | A/B/C/N/A |
| source | source note |

Preferred data path: A/B evidence from filings, customer or supplier disclosures, credible industry data, lead-time and price evidence, and source-backed capacity or yield records.

### future_bottleneck_scenarios

Use for 6-24 month supply-gap migration after current bottlenecks are diagnosed. Future scenarios may be probabilistic but must show demand trigger, supply-lag mechanism, and evidence gap. A node with only high HHI, high margin, technical difficulty, or domestic-substitution difficulty is not a future bottleneck unless it is expected to create a supply gap.

Required: `node`, `future_status`, `demand_trigger`, `supply_lag_mechanism`. When `future_status=likely_future_bottleneck`, strict mode additionally requires non-placeholder `likely_timing`, `confidence`, `evidence_gap`, `reversal_indicator`, `evidence_date`, `source_type`, `source_locator`, `evidence_grade`, and `source`. `evidence_date` must be ISO, no later than `as_of`, and by default within 365 days; optional `future_max_age_days` can only be 1-365. Likely/high scenarios require fresh A/B-grade `regulatory|official|company_original|official_counterparty|credible_third_party`; stale or `social|anonymous|lead_only` evidence is limited to low-confidence watch.

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
| evidence_date / source_type / source_locator | dated source tier and reproducible URL, filing ID, or file locator |
| future_max_age_days | optional freshness window; default and maximum 365 |
| evidence_grade | A/B/C/N/A |
| source | source note |

Preferred data path: technology roadmaps, customer architecture changes, capacity schedules, yield ramp evidence, second-source qualification cycles, resource/regulatory constraints, and profit-pool migration evidence.

### china_candidates

Use only after the bottleneck node is selected and the user asks for listed exposure. This table is for A-share, HK-share, or China-local tradable mapping; it is not the default industry-chain output.

Required: `company`, `ticker`, `exchange`, `linked_node`, `exposure_evidence`, `commercialization_stage`, `stage_evidence`, `stage_evidence_date`, `stage_claim_window`, `stage_source`, `stage_source_type`, `stage_source_locator`, `evidence_grade`, `verdict`. Stage must be one of `rd_plan|sampling|validation|design_win|qualification|mass_production|shipment|revenue|profit_cashflow`; `stage_claim_window` is `current|historical`; `stage_evidence_date` must be an ISO-8601 date/timestamp no later than top-level `as_of`. Optional `stage_max_age_days` defaults to 365 and is limited to 1-365.

Current stage evidence older than `stage_max_age_days` is invalid. Preserve older evidence only as `historical` with `watch_only|theme_adjacent|reject`; historical evidence can never support `main_candidate`. For a long-standing revenue/profit stage, use the most recent formal report or current official confirmation as `stage_evidence` and its publication date as `stage_evidence_date`.

`stage_source_type` is `regulatory|official|company_original|official_counterparty|third_party|social|anonymous|lead_only`. `revenue`, `profit_cashflow`, or `main_candidate` requires A-grade evidence, a traceable `stage_source_locator`, and `regulatory|official|company_original|official_counterparty`; `social|anonymous|lead_only` can only remain `watch_only|theme_adjacent|reject`, never a realized stage or main candidate.

`revenue` or `profit_cashflow` also requires a traceable non-placeholder `source` and `revenue_materiality`; a non-main candidate may use a specific `evidence_gap` instead of undisclosed revenue materiality. `main_candidate` always requires connected `linked_node`, `exposure_evidence`, `source`, and, at realized-revenue stages, `revenue_materiality`.

Recommended fields:

| field | use |
|---|---|
| exchange | SSE/SZSE/BSE/HKEX or N/A |
| linked_node | selected bottleneck node |
| exposure_evidence | product, customer, order, capacity, certification, or filing evidence |
| commercialization_stage | highest stage directly supported by current evidence |
| stage_evidence / stage_evidence_date / stage_source | stage-specific proof, date, and source description |
| stage_claim_window / stage_max_age_days | current vs historical claim and bounded freshness window |
| stage_source_type / stage_source_locator | source tier enum and reproducible URL, filing ID, or file locator |
| pure_play_level | high/medium/low |
| revenue_materiality | exact percentage or qualitative disclosure |
| evidence_gap | specific missing evidence when revenue materiality is not disclosed |
| fundamental_quality | high/medium/low/N/A |
| earnings_elasticity | high/medium/low/N/A |
| trading_elasticity | high/medium/low/N/A |
| verdict | main_candidate, watch_only, theme_adjacent, reject; never proof of realized revenue |
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

`date` must be an ISO date/timestamp no later than top-level `as_of`.

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

### bottleneck_evidence_checks

Use with `scripts/validate_bottleneck_evidence.py`. This validates whether the evidence packet is complete enough for human/agent review; it never turns a weighted score into a bottleneck conclusion.

Required: `check_id`, `node`, `severity`, `claim_window`, `claim_as_of`, `demand_evidence_kind`, `supply_evidence_kind`, `demand_evidence`, `demand_evidence_date`, `demand_source_type`, `demand_source_locator`, `supply_evidence`, `supply_evidence_date`, `supply_source_type`, `supply_source_locator`, `supply_gap_evidence`, `gap_evidence_date`, `gap_source_type`, `gap_source_locator`, `direct_gap_consequence`, `constraint_mechanism`, `time_horizon`, `substitution_path`, `second_source_status`, `relief_window`, `positive_validation`, `counterevidence`, `key_reversal`, `evidence_grade`, `source`, `source_date`. `check_id` must be unique in one normalized packet. Optional `max_age_days` defaults to 180 and must be an integer from 1 to 365.

`claim_window` is `current|future|historical`; every claim/evidence date must be an ISO date/timestamp no later than top-level `as_of`, and evidence dates cannot be later than `claim_as_of`. For `current` hard/soft, every evidence date must also be within `max_age_days` of `claim_as_of`. Stale evidence may remain historical/watch/incomplete but cannot be eligible for a current hard/soft claim.

Demand kind is `quantified_demand|demand_step|qualitative_signal`; supply kind is `qualified_supply_limit|usable_capacity_limit|yield_limit|delivery_limit|certified_supplier_limit|qualitative_constraint`. For `hard_bottleneck`, the validator requires `current`, A-grade evidence, a quantified/step demand kind, a non-qualitative supply-limit kind, a direct consequence, and no `qualified|ramping|active` second source. Soft claims require A/B evidence; watch claims remain observation status. The validator rejects inconsistent claims but never assigns a severity.

Demand, supply, and gap legs each require a `*_source_type` plus traceable `*_source_locator`. Hard requires all three legs from `regulatory|official|company_original|official_counterparty`; soft may also use `credible_third_party`. `social|anonymous|lead_only` cannot support hard/soft even when self-labelled A-grade or recently dated.

`N/A` 只能与检索范围或尚缺证据一起说明；空白或裸语义占位符不具备评审资格，也不能支持 hard/soft 声明。

### source_evidence

Use when tracking claim-to-source mapping across files and web evidence.

Required: `claim`, `source`

Recommended fields: `claim_type`, `entity`, `url_or_file`, `date`, `evidence_grade`, `limitation`

When supplied, `date` must be an ISO date/timestamp no later than top-level `as_of`.

## Connector Boundary

- Global leader market data: use `finance`, `alpha-vantage`, iFinD global stock MCP, official filings, and company IR.
- China market data: use `allstock-data`, `finance`, `stock-evaluator`, exchange filings, and company IR.
- Live AI news or rumor discovery: use `ai-chain-research-orchestrator` only when needed, then verify original sources.
- The data-interface script does not fetch from the internet. It normalizes verified or user-provided inputs.
