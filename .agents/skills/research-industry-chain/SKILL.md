---
name: research-industry-chain
description: Research industry chains through terminal demand, supply-chain topology, BOM/value nodes, qualified-supply bottlenecks, bottleneck duration, future constraint migration, global leaders, and optional listed-company mapping. Use for 产业链拆解、上下游、BOM、价值量、堵点、卡点、供需缺口、交期、产能、良率、国产替代、AI/半导体细分环节或海外龙头映射.
---

# Research Industry Chain

从产业节点而不是热门股票出发。根据问题深度自由裁剪流程；只保留可验证的结论，不为填模板而制造精确度。

## 核心定义

把瓶颈定义为：在明确时间窗口内，需求超过合格供给、可用产能、良率、交付能力或已认证供应商能力。

高价值量、高毛利、高 HHI、技术难度、认证周期或市场热度只能说明战略性或定价权，不能单独证明供应缺口。缺少直接供需证据时使用 `strategic_node`、`pricing_power_node` 或 `watch`。

## 自适应流程

1. **限定问题**：明确终端产品、需求驱动、时间窗口、地域和是否需要上市公司映射。
2. **建立拓扑**：拆出上游材料/设备/组件、中游制造/封装/集成、下游系统/客户；只对决策有用的节点估算 BOM 或价值量。
3. **验证供需**：分别收集需求证据与供给约束，区分真实供应缺口、普通量增、定价权节点和概念热度。
4. **深拆瓶颈**：对确认的瓶颈说明精确短缺对象、替代为何无效、合格产能/良率/认证约束、扩产路径、持续窗口和反转指标。
5. **判断迁移**：检查未来 6-24 个月的技术代际、需求阶跃、扩产、良率、第二供应商、架构变化和监管/资源约束。
6. **按需映射公司**：只有用户要求可投资标的时，才核对准确产品、客户/认证/订单、收入重要性、产能兑现、财务质量和估值/交易上下文。

如果问题只问一个节点或一个事实，直接完成对应步骤，不强制生成全产业链报告。

## 证据纪律

- 当前价格、产能、交期、订单、客户、财务和政策必须实时核验。
- A 级官方材料可支撑硬结论；可靠行业/媒体/数据商用于交叉验证；社交、模型和概念标签只作为线索。
- 未验证的 BOM 份额、市场份额、交期、良率、产能和财务数字写 `N/A`。
- 当前瓶颈和未来瓶颈分开；未来判断必须写明需求触发、供给滞后机制、时间和证据缺口。
- 全球龙头用于校准真实技术路径；本地上市公司不能因名称相似就视为可比。

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

AI 数据中心节点层级需要更细时，再读相邻技能的 `../user-investment-framework/references/ai-chain-node-taxonomy.md`。

## 确定性脚本

只有已有结构化数据或用户要求可复现计算时才运行：

```powershell
python .agents/skills/research-industry-chain/scripts/normalize_research_inputs.py --input data.xlsx --pretty
python .agents/skills/research-industry-chain/scripts/calculate_hhi.py --shares 35 25 15 10 5
python .agents/skills/research-industry-chain/scripts/score_bottleneck_nodes.py --csv nodes.csv --pretty
```

脚本只做规范化和一致性计算，不获取事实，也不替代证据判断。没有可靠份额数据时不计算 HHI。

## 输出

结论先行，并按任务需要给：产业链位置、需求证据、供应缺口、约束机制、持续时间、未来迁移、反转风险。涉及股票时再补准确暴露、公司证据，以及基本面质量、业绩弹性、交易弹性三层判断。证据不足时允许只给观察池。
