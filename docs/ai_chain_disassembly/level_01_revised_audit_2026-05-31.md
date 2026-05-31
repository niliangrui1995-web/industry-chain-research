# AI 产业链逐级拆解 - Level 1 修订版审计表

日期：2026-05-31

任务类型：审计

被审计文件：`docs/ai_chain_disassembly/level_01_from_data_center_revised_2026-05-31.md`

审计结论：通过

下一任务：进入 Level 2 梳理，不做瓶颈判断，不做股票映射。

## 结论先行

修订版 Level 1 表通过审计。它已经把主链拆解口径从“数据中心价值池大杂烩”修正为“可继续向上游拆解的硬件、设备、工艺、制造服务链”，并把电力资源、工程交付、软件生态、安全可靠性、运维服务移到附表，解决了上一轮审计中的主表混杂问题。

下一轮可以进入 Level 2 梳理。建议先覆盖全部通过的 Level 1 主链，但在工作顺序上优先 P0/P1：

1. P0：GPU/ASIC 加速计算链、高速网络与光/铜互连链、高密度供配电设备链、热管理与液冷链。
2. P1：AI 服务器与机架级整机集成链、高性能存储与数据通路链。
3. P2：机柜结构与物理连接链，进入 Level 2 时保留，但需要继续观察是否并入整机集成链。

## 审计总表

| audit_item | 审计问题 | 修订版证据 | verdict | 备注 |
|---|---|---|---|---|
| 目标一致性 | 是否符合“数据中心为 0 级，一级一级往上游拆解”？ | 修订版把 Level 0 定义为 AI 数据中心，并把 Level 1 主表限定为数据中心直接依赖、且能继续拆到 Level 2 的产品、器件、材料、工艺、设备或制造服务链。 | pass | 可以作为逐级上游拆解入口。 |
| 主链纯度 | 是否只把可继续拆的硬件/设备/制造服务放入主表？ | 主表保留 7 条可拆主链；电力资源、工程交付、软件生态、安全可靠性、运维服务进入附表。 | pass | 上轮“主表混杂”问题已解决。 |
| 计算链口径 | GPU/ASIC、服务器整机、HBM、PCB 的层级关系是否自洽？ | DC-L1R-001 明确 GPU/ASIC 是 Level 1 主入口，HBM、ABF、PCB 是 Level 2 候选；DC-L1R-003 只统计整机集成与制造服务。 | pass | 仍需在 Level 2 中区分芯片本体、封装、内存、板级承载。 |
| 重叠归属 | PSU、PCB、光模块、液冷、机柜等跨链项是否有唯一主归属？ | PSU 归供配电；光模块归网络互连；液冷归热管理；PCB 按计算板、交换板、整机集成用途进入对应 Level 2；机柜结构单列 P2。 | pass_with_watch | 机柜结构链与整机集成仍需在 Level 2 后复核是否合并。 |
| 下一层可执行性 | 是否能直接进入 Level 2 梳理？ | 每个主表节点均列出 Level 2 候选，并给出下一任务审计问题。 | pass | 下一轮应只做 Level 2 梳理，不能同时审计。 |
| 投研可用性 | 是否利于后续做 BOM、供应缺口、瓶颈和公司映射？ | P0/P1 节点均能继续拆到 BOM、器件、材料、工艺、设备或制造服务；附表项不参与主链拆解。 | pass | 还不能做瓶颈或个股映射，需等 Level 2 梳理和审计完成。 |

## 节点逐项审计

| node_id | node_name | verdict | 审计意见 | 下一轮 Level 2 梳理要求 |
|---|---|---|---|---|
| DC-L1R-001 | GPU/ASIC 加速计算链 | pass | 与用户示例“GPU 是 1 级”一致，且修订版避免了把 HBM/PCB 提前放入 Level 1。 | Level 2 至少拆 GPU/ASIC die、HBM/DRAM、先进封装、硅中介层、ABF/IC 载板、算力板 PCB、晶圆制造、封测、关键设备与材料。 |
| DC-L1R-002 | 高速网络与光/铜互连链 | pass | 光模块归网络互连链，层级清楚；交换芯片、NIC/DPU 与计算链交叉但主归属合理。 | Level 2 至少拆交换机、交换芯片、NIC/DPU、光模块、光引擎、CPO/OCS、DAC/ACC/AOC、retimer/SerDes、光纤连接器和线缆。 |
| DC-L1R-003 | AI 服务器与机架级整机集成链 | pass | 已明确只统计整机集成与制造服务，不重复统计 GPU、光模块、PSU、冷板等组件价值。 | Level 2 重点拆 ODM/OEM 组装、主板/基板组件装配、机架集成、系统测试、可靠性验证、供应链管理和现场交付。 |
| DC-L1R-004 | 高密度供配电设备链 | pass | 服务器 PSU 统一归本节点，电力资源转入附表，主链纯度合格。 | Level 2 至少拆变压器、开关柜/断路器、UPS、母线槽、PDU、rack power shelf、服务器 PSU、功率器件、电容/电池、铜排和监控计量。 |
| DC-L1R-005 | 热管理与液冷链 | pass | 液冷作为热管理链的 Level 2 候选，不单独提升 Level 1，符合层级原则。 | Level 2 按板级/服务器级、机柜级、园区级拆冷板、CDU、manifold、泵阀、快接头、密封件、冷却液、chiller、冷却塔和漏液检测。 |
| DC-L1R-006 | 高性能存储与数据通路链 | pass | 保留硬件和数据通路，软件治理进入附表或附属项，边界可接受。 | Level 2 至少拆 SSD/NVMe、NAND、企业级 HDD、存储控制器、DRAM 缓存、存储服务器、存储网络和备份归档硬件。 |
| DC-L1R-007 | 机柜结构与物理连接链 | pass_with_watch | 作为独立 Level 1 可以保留，但价值池和整机集成有潜在重叠。 | Level 2 梳理时必须标记与 DC-L1R-003 的边界；若后续审计发现独立性不足，再并入整机集成链。 |

## 附表审计

| side_id | item | verdict | 审计意见 |
|---|---|---|---|
| DC-SIDE-001 | 电网接入、变电站容量、并网排队、PPA、绿电、区域电价、能耗指标 | pass | 放入附表合理。它影响供配电需求和项目节奏，但不是硬件上游主链节点。 |
| DC-SIDE-002 | 土建、机房工程、消防、EPC、项目管理、验收 | pass | 放入附表合理。后续若单独研究数据中心工程服务，可另建工程链。 |
| DC-SIDE-003 | CUDA/ROCm、驱动、编译器、调度、Kubernetes/Slurm、监控计费 | pass | 放入附表合理。软件影响利用率和生态锁定，但不参与硬件 Level 2 主链。 |
| DC-SIDE-004 | 消防安全、网络安全、物理安防、合规审计、可靠性测试 | pass | 放入横向支撑合理。后续可作为各节点的测试/认证字段。 |
| DC-SIDE-005 | 现场运维、备件、故障定位、能耗优化、SLA 服务 | pass | 放入附表合理。运维服务不作为当前硬件上游拆解入口。 |

## 下一轮 Level 2 梳理约束

| rule_id | 约束 | 说明 |
|---|---|---|
| L2-R1 | 下一轮只做梳理 | 不能同时审计、判定瓶颈、映射股票或做交易弹性判断。 |
| L2-R2 | 每个 Level 2 节点必须有唯一父节点 | 父节点使用 `DC-L1R-001` 至 `DC-L1R-007`，避免 HBM、PCB、PSU、测试等跨链重复计数。 |
| L2-R3 | Level 2 只列产品/器件/材料/工艺/设备/制造服务 | 不能把“涨价”“短缺”“国产替代”“某公司”作为 Level 2 节点。 |
| L2-R4 | 保留后续审计字段 | 每个 Level 2 节点应包含定义、需求传导、上游候选、边界、审计问题、priority、status。 |
| L2-R5 | 先全量覆盖，再排序优先级 | Level 2 梳理应覆盖全部通过的 Level 1 主链；优先级只用于后续深拆顺序，不用于删节点。 |
| L2-R6 | 证据口径保持 `N/A` | 本阶段不需要实时行情或公司数据；涉及价值量、份额、价格、产能、供应缺口时先标 `N/A`，留给后续证据任务。 |

## 建议的下一任务文件

| next_file | task_type | 说明 |
|---|---|---|
| `docs/ai_chain_disassembly/level_02_from_level_01_revised_2026-05-31.md` | mapping | 基于通过审计的 7 条 Level 1 主链，梳理 Level 2 节点表。 |

## 机器可读状态

```yaml
artifact_type: ai_chain_level_audit
task_type: audit
audited_file: docs/ai_chain_disassembly/level_01_from_data_center_revised_2026-05-31.md
audited_level: 1
audit_result: passed
may_enter_next_level: true
next_required_task: map_level_2_from_revised_level_1
approved_parent_nodes:
  - DC-L1R-001
  - DC-L1R-002
  - DC-L1R-003
  - DC-L1R-004
  - DC-L1R-005
  - DC-L1R-006
  - DC-L1R-007
watch_items:
  - DC-L1R-007 boundary with DC-L1R-003
live_data_used: false
stock_mapping_included: false
```
