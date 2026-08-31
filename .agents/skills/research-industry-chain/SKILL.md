---
name: research-industry-chain
description: Research industry chains through terminal demand, supply-chain topology, BOM/value nodes, qualified-supply bottlenecks, bottleneck duration, future constraint migration, global leaders, and optional listed-company mapping. Use for 产业链拆解、上下游、BOM、价值量、堵点、卡点、供需缺口、交期、产能、良率、国产替代、AI/半导体细分环节或海外龙头映射. When the user explicitly requests Serenity or serenity-stock-choke, use its choke-point lens only to generate candidate nodes, then validate them under this skill's same evidence gates.
---

# Research Industry Chain

从产业节点而不是热门股票出发。根据问题深度自由裁剪流程；只保留可验证的结论，不为填模板而制造精确度。

## 核心定义

把瓶颈定义为：在明确时间窗口内，需求超过合格供给、可用产能、良率、交付能力或已认证供应商能力。

高价值量、高毛利、高 HHI、技术难度、认证周期或市场热度只能说明战略性或定价权，不能单独证明供应缺口。缺少直接供需证据时使用 `strategic_node`、`pricing_power_node` 或 `watch`。

- `hard_bottleneck`：当期 A 级证据闭环同时覆盖需求量/阶跃、合格供给/可用产能/良率/交付上限、直接缺口后果，且窗口内没有已认证可替代来源。
- `soft_bottleneck`：已有 A/B 级直接证据，但闭环尚未完全建立，或存在可信的二供、扩产、良率改善等缓解路径。
- `watch`：只有约束机制、前置指标或待验证情景，尚不能证明当前合格供给缺口。

结构化 hard/soft 声明必须通过 `validate_bottleneck_evidence.py` 的等级一致性门。当前 hard/soft 还必须提供 `claim_as_of` 与需求、供给、缺口、来源四类 ISO 日期；默认新鲜度窗口为 180 天，`max_age_days` 只能在 1-365 天内覆盖。三条关键证据腿分别记录来源类型和可复核定位：hard 必须全部来自 `regulatory|official|company_original|official_counterparty`，soft 可增加 `credible_third_party`；`social|anonymous|lead_only` 只能观察。陈旧证据可保留为 `historical`、`watch` 或未完成记录，但不能支持当前 hard/soft。`eligible_for_bottleneck_review` 只表示证据包与声明等级相容，不能自动授予瓶颈结论。

## Serenity 候选模式（仅显式点名）

用户明确要求 `Serenity` 或 `serenity-stock-choke` 时，先从终端向上游提出“某节点断供会影响哪个产品、在何时、为何无法替代”的候选命题，并列出合格供给、替代/二供、扩产和反证路径。技术壁垒、国产替代、小市值、资金信号或市场热度都不是瓶颈证明；候选默认是 `watch`，只有完成下列同一套供需、时点和来源闭环后才可升级为 `soft_bottleneck` 或 `hard_bottleneck`。不输出买卖、仓位或时点指令。

## 自适应流程

1. **限定问题**：明确终端产品、需求驱动、时间窗口、地域和是否需要上市公司映射。
2. **建立物理拓扑**：从终端系统向下拆到模块、组件、材料/设备/工艺（通常对应 Layer 2/3/4），再连接上游制造与下游客户；只对决策有用的节点估算 BOM 或价值量，并跨 A/H/美/台/日/韩/欧市场校准技术路径，避免熟悉市场偏差。
3. **验证供需**：分别收集需求证据与供给约束，区分真实供应缺口、普通量增、定价权节点和概念热度。
4. **深拆瓶颈**：对确认的瓶颈说明精确短缺对象、相邻产能为何不能替代、合格产能/良率/认证约束、替代路线、第二供应商状态、扩产路径、持续窗口和反转指标。
5. **判断迁移与变化**：检查未来 6-24 个月的技术代际、需求阶跃、扩产、良率、第二供应商、架构变化和监管/资源约束；与上次状态比较新增、升级、降级或解除，不把旧结论当当前事实。`likely_future_bottleneck` 或 high confidence 必须有不晚于 `as_of` 且默认 365 天内的 A/B 级、可定位 `regulatory|official|company_original|official_counterparty|credible_third_party` 来源；`future_max_age_days` 只能在 1-365 天内收紧，陈旧或弱来源只能 low-confidence `watch`。
6. **按需映射公司**：只有用户要求可投资标的时，才核对准确产品、商业化阶段及其证据/日期/来源、收入重要性、产能兑现、财务质量和估值/交易上下文，并保留候选纳入/淘汰理由与下一验证点。阶段只允许 `rd_plan | sampling | validation | design_win | qualification | mass_production | shipment | revenue | profit_cashflow`；不得从当前阶段推断下一阶段。规范化时必须显式传入研究截止日 `--as-of YYYY-MM-DD`，阶段证据不得晚于该日；`stage_claim_window=current` 默认要求 365 天内的证据（或把最近正式报告/当前官方确认作为阶段证据），陈旧记录只能 `historical` + `watch_only|theme_adjacent|reject`。`revenue`、`profit_cashflow` 或 `main_candidate` 必须由 A 级、可定位的 `regulatory|official|company_original|official_counterparty` 原始来源支持。

如果问题只问一个节点或一个事实，直接完成对应步骤，不强制生成全产业链报告。

## 证据纪律

- 当前价格、产能、交期、订单、客户、财务和政策必须实时核验。
- A 级官方材料可支撑硬结论；可靠行业/媒体/数据商用于交叉验证；社交、模型和概念标签只作为线索。
- 未验证的 BOM 份额、市场份额、交期、良率、产能和财务数字写 `N/A`。
- 当前瓶颈和未来瓶颈分开；未来判断必须写明需求触发、供给滞后机制、时间和证据缺口。
- 全球龙头用于校准真实技术路径；本地上市公司不能因名称相似就视为可比。
- 正面验证和反证同时保留；第二供应商通过认证、良率提升、交期缩短或需求下修都可能解除瓶颈。
- 产品规划、送样、客户验证、design win、认证、量产、出货、收入和利润/现金流严格分开。`main_candidate` 只表示研究优先级；未到 `revenue`/`profit_cashflow` 时不得写成已兑现业绩受益。
- `social|anonymous|lead_only` 只能作为观察、主题相邻或否决线索，不能证明 `revenue`/`profit_cashflow`，也不能支持 `main_candidate`。
- `bottleneck_ledger` 的 hard/soft 行必须用 `evidence_check_id` 唯一关联同包 `claim_window=current` 的证据检查，并且 ledger/check 的 `claim_as_of` 均等于顶层 `as_of`、`time_horizon` 一致，`evidence_review_status` 等于 normalizer 重新计算的 `eligible_for_bottleneck_review`；历史记录只能 watch/rejected，未来情景走 `future_bottleneck_scenarios`。

## 领域参考

只读命中的参考：

| 场景 | 参考 |
|---|---|
| AI/半导体、HBM、先进封装、PCB/CCL、光模块、液冷、数据中心电力 | [references/ai-semiconductor.md](references/ai-semiconductor.md) |
| PCB/CCL | [references/adapters/pcb-ccl.md](references/adapters/pcb-ccl.md) |
| 光模块/硅光/CPO/OCS | [references/adapters/optical-module.md](references/adapters/optical-module.md) |
| 液冷 | [references/adapters/liquid-cooling.md](references/adapters/liquid-cooling.md) |
| 数据中心电力 | [references/adapters/data-center-power.md](references/adapters/data-center-power.md) |
| 来源缺口 | [references/source-priority.md](references/source-priority.md) |
| 用户提供 CSV/JSON/JSONL/XLSX | [references/data-interfaces.md](references/data-interfaces.md) |
| 可复用节点表 | [references/node-table-schema.md](references/node-table-schema.md) |

AI 数据中心节点层级需要更细时，读 [references/ai-chain-node-taxonomy.md](references/ai-chain-node-taxonomy.md)。

## 确定性脚本

只有已有结构化数据或用户要求可复现计算时才运行：

```powershell
python .agents/skills/research-industry-chain/scripts/normalize_research_inputs.py --input data.xlsx --as-of 2026-07-27 --pretty
python .agents/skills/research-industry-chain/scripts/calculate_hhi.py --shares 35 25 15 10 5
python .agents/skills/research-industry-chain/scripts/validate_bottleneck_evidence.py --csv nodes.csv --as-of 2026-07-27 --pretty
```

脚本只做规范化、显式时点截断、完整性门和一致性计算，不获取事实、不打万能分，也不自动授予瓶颈等级。`--as-of` 是可复现研究时点，不使用机器当前日期替代。没有可靠份额数据时不计算 HHI。

## 输出

结论先行，并按任务需要给：物理层级、产业链位置、需求证据、供应缺口、替代/第二供应商、约束机制、持续时间、相对上次变化、未来迁移、反证和反转风险。涉及股票时再补准确暴露、当前商业化阶段及证据/日期/来源、收入重要性、纳入/淘汰理由，以及基本面质量、业绩弹性、交易弹性三层判断。证据不足时允许只给观察池。
