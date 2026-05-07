# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-05-07  
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-05-07.md`  
覆盖窗口：2026-04-30 至 2026-05-07  
当前阶段：首次实际报告完成，已建立全链基线。

## 任务边界

本任务负责 AI 产业链横向雷达和赛道优先级，不重复展开光模块和 AI PCB 专项细节。执行时必须读取：

- `artifacts/weekly_chain_tracking/optical_module/state.md`
- `artifacts/weekly_chain_tracking/ai_pcb/state.md`

如果两个专项已有最新状态，本任务只吸收结论并做全链横向排序。

研究宇宙：

- 云厂商 / AI CapEx / 数据中心建设
- GPU / ASIC / 加速卡
- HBM / DRAM / 存储
- 先进封装 / CoWoS / SoIC / 封装设备材料
- ABF / BT / 封装载板
- AI PCB / CCL / 上游材料
- 光模块 / 硅光 / CPO / OCS / 光互连
- 交换机 / 以太网 / InfiniBand / DSP / retimer / NIC / DPU
- 液冷
- 数据中心电力：变压器、开关柜、UPS、母线、PDU、rack power
- 服务器 / ODM / 连接器 / 关键材料与设备

## 本期总览结论

本期为首期实际报告，没有上期 AI 全链实际报告可回访。光模块和 AI PCB 专项均已有 2026-05-07 最新报告，本任务已吸收其结论。

本期进入全链排序的主线：

1. `HBM / AI memory / 高端 DRAM / eSSD`：全链最强硬堵点，证据来自云 capex、AMD 数据中心增长、Samsung/SK hynix AI memory 需求和扩产口径。
2. `高速 EML / InP / CW laser`：光模块专项确认的硬堵点，进入全链第二梯队。
3. `M7/M8/M9 CCL/prepreg`：AI PCB 专项确认的软堵点，进入全链第三梯队。
4. `数据中心电力 / 液冷 / 预制化基础设施`：本期新增全链深挖方向，当前列 `soft_bottleneck/watch`。
5. `AI networking / retimer / PCIe / Ethernet`：需求强但缺短缺证据，列 `strategic_watch`。

本期未升级为当前硬堵点的高结构赛道：

- `CoWoS / advanced packaging`：结构重要性极高，但本周新增缺口证据不足，维持 `strategic_watch`。
- `DSP / driver / TIA / CDR`：光模块专项已降级为 `rejected/watch`。
- `成品 AI PCB 板厂加工产能`：订单兑现增强，但未证明全行业产能、良率或交期瓶颈。

## 专项吸收状态

| 专项任务 | 最新状态文件 | 本期吸收结论 | 对全链排序的影响 |
|---|---|---|---|
| 光模块及上游 | `../optical_module/state.md` | 高速 EML/InP/CW laser 为硬堵点；模块整机关键物料同步为软堵点；FAU/ELS/微透镜/隔离器为未来迁移观察；DSP/TIA 暂不成立。 | 高速 EML/InP/CW laser 排入全链硬堵点第二梯队。 |
| AI PCB 及上游 | `../ai_pcb/state.md` | M7/M8/M9 CCL/prepreg 为软堵点；电子布/T-glass、HVLP 铜箔为候选硬卡点；成品板厂订单兑现增强但未成加工瓶颈。 | CCL/prepreg 排入全链软堵点；电子布/T-glass 与 HVLP 铜箔进入迁移池。 |

## 当前全链堵点账本

| 节点 | 所属赛道 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| HBM / HBM4 / AI memory / high-capacity eSSD | HBM/存储 | 当前主堵点 | hard_bottleneck | AI accelerator 与云 capex 需求超过高价值内存合格供给；约束来自堆叠良率、先进封装、客户认证和容量锁定 | new | Microsoft/Meta/Amazon capex，AMD 数据中心增长，Samsung/SK hynix AI memory 口径 | HBM ASP/毛利回落、客户不再锁货、HBM4 多供方充足 | 查客户 allocation、HBM4 认证、价格和产能节奏 |
| 高速 EML / InP / CW laser | 光模块上游 | 当前主堵点 | hard_bottleneck | 1.6T/800G/CPO 需求超过合格激光器、InP 6 英寸和 CW laser 供给；约束来自良率、可靠性和客户锁产能 | new_absorbed | 光模块专项，Lumentum/Coherent/中际旭创/新易盛 | 激光器不再 allocation，模块厂不再预付锁料，6 英寸 InP 产能兑现 | 由光模块专项跟踪官方 transcript/10-Q |
| M7/M8/M9 CCL/prepreg | AI PCB/CCL | 当前软堵点 | soft_bottleneck | 高端材料涨价和上游材料紧张；约束来自电子布、铜箔、树脂、配方、认证和批量良率 | new_absorbed | AI PCB 专项，Panasonic 官方调价，台系/建滔涨价线索 | 提价落空、交期缩短、二供通过、库存回升 | 由 AI PCB 专项跟踪 5 月成交价和交期 |
| 高端电子布/T-glass/低 CTE 布 | PCB 上游材料 | 候选硬卡点 | soft_bottleneck/watch | 低端布不能替代高端低损耗、低 CTE 需求；约束来自窑炉、纱、织布、良率和认证 | new_absorbed | AI PCB 专项 B 级产业媒体和历史线索 | 高端布库存回升、报价回落、官方扩产快速认证 | 查 Nittobo/Asahi/中材/宏和/国际复材官方证据 |
| HVLP4/HVLP5 铜箔 | PCB 上游材料 | 候选卡点 | watch | 表面处理、粗糙度一致性和客户认证约束 | unchanged_absorbed | AI PCB 专项历史官方进度 + B 级线索 | 多家稳定批量供货、价格回落 | 查德福/嘉元/诺德 PCB 级 HVLP 批量交付 |
| 数据中心电力 / 液冷 / 预制化基础设施 | 数据中心基础设施 | 新增观察主线 | soft_bottleneck/watch | AI 数据中心功率密度提升，电气设备、thermal、预制模块和工程交付可能成为建设速度约束 | new | Vertiv、Eaton、Schneider 官方订单、积压和收入增长 | backlog 回落、交期缩短、项目不再因电力/冷却延迟 | 查单品交期、北美订单和 A 股映射纯度 |
| AI networking / retimer / PCIe / Ethernet | 高速互连 | 战略观察 | strategic_watch | 网络需求强，但电互连和交换机整机尚未证明供给不足 | new | Arista、Astera 官方 Q1 结果 | 出现 allocation/交期证据则升级；需求放缓则降级 | 跟 Arista/Astera/Broadcom/Marvell 订单和交期 |
| CoWoS / advanced packaging | 先进封装 | 战略观察 | strategic_watch | AI accelerator 结构核心，但本周缺新的供需缺口量化 | unchanged | TSMC Q1 transcript | CoWoS 产能释放快于需求或客户不再受限 | 下周补 TSMC/OSAT/封装基板最新证据 |

## 本期深挖方向

- 主深挖 1：`HBM / AI memory`。目标是确认 HBM3E/HBM4 供需缺口、客户 allocation、产能扩张、ASP 和毛利持续时间。
- 主深挖 2：`数据中心电力 / 液冷 / 预制化基础设施`。目标是确认 backlog 是否对应真实交期瓶颈，并拆分变压器、switchgear、UPS、rack PDU、CDU/冷板和工程交付。

## 三类排名快照

| 类型 | 排名 | 对象 | 理由 | 证据等级 | 风险 |
|---|---:|---|---|---|---|
| 结构重要性 | 1 | HBM / AI memory | AI 计算平台最直接的供给约束，合格产能和客户锁定强 | A/B | HBM4 二供放量 |
| 结构重要性 | 2 | GPU/ASIC + CoWoS | AI 计算核心，但本周缺新增缺口量化 | A | 仅结构强，不等于本周堵点 |
| 结构重要性 | 3 | 高速 EML / InP / CW laser | 1.6T/800G/CPO 光互连关键上游 | A/B | 6 英寸 InP 扩产缓解 |
| 结构重要性 | 4 | 数据中心电力/液冷 | 影响 AI 数据中心落地速度 | A | 单品交期不足 |
| 结构重要性 | 5 | 高端 CCL/prepreg | AI server/switch 规格升级关键材料 | A/B | 涨价传导不确定 |
| 业绩弹性 | 1 | HBM/AI memory 供应商 | HBM ASP、产能利用和产品结构直接拉动利润 | A/B | 周期和供应放量 |
| 业绩弹性 | 2 | 光模块上游和模块厂 | 1.6T/800G 放量叠加上游紧缺 | A/B | 年降和估值 |
| 业绩弹性 | 3 | 数据中心电力/液冷 | backlog 和订单传导到收入 | A/B | 项目周期 |
| 业绩弹性 | 4 | AI PCB 高端材料 | 涨价和产品结构升级有利润弹性 | A/B | 成交价和认证 |
| 业绩弹性 | 5 | AI networking/retimer | 增长强但非缺口驱动 | A | 竞争和估值 |
| 交易弹性 | 1 | A 股光模块弹性组 | 催化密度、涨幅和换手高，部分有硬证据 | A/B/C | 拥挤和主题泛化 |
| 交易弹性 | 2 | PCB 上游材料组 | 高端布/HVLP/树脂交易弹性强 | B | 硬证据不足 |
| 交易弹性 | 3 | 数据中心电力 A 股组 | 电力约束成为新叙事，部分小市值弹性高 | B/A 待补 | 数据中心订单纯度 |
| 交易弹性 | 4 | 美股互连/电力组 | Astera/Arista/Vertiv 官方增长强 | A | 估值已高 |
| 交易弹性 | 5 | HBM 全球龙头 | 基本面强但 A 股映射弱 | A/B | 内存周期 |

## 下期默认跟踪问题

1. HBM/HBM4 是否出现更明确的客户 allocation、价格、产能扩张和二供认证数据？
2. CoWoS/advanced packaging 是否出现新的官方产能、客户排产、封装基板或设备交期证据？
3. 光模块专项是否补齐 Lumentum/Coherent 官方 transcript、10-Q 以及国内模块厂具体物料偏紧来源？
4. AI PCB 专项是否验证 5 月 CCL/prepreg 成交价、电子布/T-glass 官方交期、HVLP4/HVLP5 批量交付？
5. 数据中心电力/液冷是否能补到 Vertiv/Eaton/Schneider backlog 的单品交期，并验证金盘科技、思源电气、伊戈尔、特变电工、中国西电的数据中心订单纯度？
