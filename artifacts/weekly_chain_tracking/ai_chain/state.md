# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-05-18
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-05-18.md`
覆盖窗口：2026-05-10 至 2026-05-18
当前阶段：第三期全链雷达，已吸收光模块与 AI PCB 专项 2026-05-17 状态。

## 任务边界

本任务负责 AI 产业链横向雷达、堵点账本、赛道优先级和上市主体映射，不重复展开光模块和 AI PCB 专项细节。每次执行必须读取：

- `artifacts/weekly_chain_tracking/ai_chain/state.md`
- `artifacts/weekly_chain_tracking/ai_chain/BASELINE_TEMPLATE.md`
- `artifacts/weekly_chain_tracking/ai_chain/` 下最近一期日期报告
- `artifacts/weekly_chain_tracking/optical_module/state.md`
- `artifacts/weekly_chain_tracking/ai_pcb/state.md`

堵点定义仍按项目规则：必须意味着需求超过合格供给、可用产能、良率、交付能力或客户认证供应商。高壁垒、高毛利、高 HHI、长认证周期或股票热度不能单独作为堵点。

## 执行补充要求

- 每次更新报告时，必须对当前 `hard_bottleneck` 和 `soft_bottleneck` 预估可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A`，但要说明缺哪类证据。
- 每次不能只分析本期 1-2 个深挖方向，还要扫描未进入深挖的其他赛道和产业链环节，判断未来 6-24 个月哪些环节最可能出现新卡点或卡点迁移，并写明需求触发、供给滞后机制、可能时间、升级触发阈值、证据缺口和反转指标。
- 对话窗口摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`；其他内容只写入报告正文，不在窗口重复。
- 可以根据研究复杂度自主拆分任务并调用子代理进行并行研究；子代理默认使用超高智能。若子代理达到上限，应排队等待前面的子代理完成，再继续新建后续子代理。主代理负责最终证据分级、交叉验证、堵点判断、排名和报告合成。

## 本期全链结论

1. `HBM / AI memory / server DRAM / enterprise SSD`：维持全链最硬约束，`hard_bottleneck`。Micron 明确称 AI 和传统服务器需求受 DRAM/NAND 供给不足约束，TrendForce 继续给出 2Q26 大幅涨价和 CSP 长协锁量，Samsung 指向 AI 高价值产品受限供给。预计持续 `2026H2-2027H1`，若 HBM4E/packaging 爬坡慢可延至 `2027H2`。
2. `高端 EML / InP / CW laser / pump laser`：由光模块专项吸收，维持 `hard_bottleneck`。Lumentum 10-Q 的需求超过供给和 allocation 口径、Coherent 6 英寸 InP ramp 共同支持。预计 `2026H2-2027H1` 偏紧，CPO/OCS 上修则可能延至 `2027H2`。
3. `M7/M8 CCL/prepreg`：由 AI PCB 专项吸收，维持 `soft_bottleneck`。Panasonic 5 月 1 日涨价执行是 A 级证据，仍缺交易端交期与客户接受度。预计 `2026H2-2027H1`。
4. `高端电子布 / Low CTE / T-glass / Low Dk/Df`：由 AI PCB 专项吸收，强化为 `soft_bottleneck+`，但未升硬。预计 `2026H2-2027H1`；Q 布/石英布更可能在 `2027H2-2028` 成为迁移卡点。
5. `数据中心电力 / 液冷 / rack power / prefab`：本期主深挖方向，升级为 `soft_bottleneck/watch`。CoreWeave、Eaton、Schneider、Vertiv 证明需求和 backlog 强，但缺单品交期，持续时间精确写 `N/A`；若交期验证，可能覆盖 `2026H2-2027H2`。
6. `CoWoS / advanced packaging / 半导体设备`：结构重要性极高，Applied Materials Q2 FY26 强化 AI/DRAM/advanced packaging 设备需求，但缺新增供需缺口硬证据，维持 `strategic_watch`。
7. `光连接 / MT ferrule / FAU / 主动对准测试`：Corning/NVIDIA 长协和光模块专项使其进入未来迁移池；当前不是硬堵点。
8. `AI networking / retimer / NIC / DPU / Ethernet switch`：需求强、结构重要，但未见 allocation/交期证据，维持 `strategic_watch`。

## 专项吸收状态

| 专项任务 | 最新状态文件 | 本期吸收结论 | 对全链排序的影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | 高端 EML/InP/CW/pump laser 为硬堵点；模块整机物料同步已缓解；FAU/MT/微透镜/主动对准/测试为未来迁移观察 | 光源链排全链第 2；光连接和无源精密件进入未来卡点池 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | M7/M8 CCL/prepreg 为软堵点；高端电子布/T-glass 为 soft+；HVLP 铜箔为 soft_watch；板厂加工瓶颈未证实 | CCL/prepreg 与高端电子布排全链第 3；HVLP/Q 布/板厂测试进入未来迁移池 |

## 当前全链堵点账本

| 节点 | 所属赛道 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|---|
| HBM / HBM4 / server DRAM / enterprise SSD | 存储 | 当前主堵点 | hard_bottleneck | AI accelerator、AI cloud、KV cache/eSSD 需求超过合格 DRAM/NAND/HBM 供给；晶圆分配、HBM堆叠/封装、客户认证和 LTA 锁量共同约束 | strengthened | Micron FY2Q26、Samsung 1Q26、TrendForce 2Q26、CoreWeave Q1 | 2026H2-2027H1；可能延至 2027H2 | 价格涨幅收敛、库存回升、客户不锁量、HBM4E 多供方认证 | 跟 HBM4E 认证、capex、库存天数、价格 |
| 高端 EML / InP / CW laser / pump laser | 光模块上游 | 当前主堵点 | hard_bottleneck | 800G/1.6T/CPO/OCS 需求超过合格光源和 InP 产能，良率、客户锁定和封装测试约束 | unchanged/worsened | Lumentum 10-Q/Q3、Coherent Q3、光模块专项 | 2026H2-2027H1；CPO/OCS 上修则 2027H2 | allocation 解除、交期恢复、6 英寸 InP 合格产能兑现 | 交给光模块专项补 transcript/单品缺口 |
| M7/M8 CCL / prepreg | AI PCB/CCL | 当前软堵点 | soft_bottleneck | 低损耗材料、配方、布/铜箔/树脂、客户认证和批量良率共同约束 | unchanged_to_worsened | Panasonic 涨价、AI PCB 专项 | 2026H2-2027H1 | 报价停涨、交期缩短、二供通过 | 等 6 月台系营收和交易端交期 |
| 高端电子布 / Low CTE / T-glass / Low Dk/Df | PCB 上游材料 | 当前软堵点 | soft_bottleneck+ | 普通布不可替代，窑炉、纱、织布、良率和客户 AVL 约束 | strengthened_not_hard | AI PCB 专项 B/C2 证据 | 2026H2-2027H1；Q 布/石英布 2027H2-2028 | 库存恢复、价格回落、交期缩短 | 找官方分产品交期、配额、AVL |
| 数据中心电力 / 液冷 / rack power / prefab | 数据中心基础设施 | 本期主深挖 | soft_bottleneck/watch | AI factory GW 级部署拉动电力设备、液冷、预制模块、并网和工程交付 | upgraded_watch | CoreWeave、Eaton、Schneider、Vertiv | 精确 N/A；若单品交期验证则 2026H2-2027H2 | backlog 转收入顺畅、交期缩短、项目延期减少 | 补单品 lead time 和 A 股订单纯度 |
| HVLP/VLP/RTF PCB 铜箔 | PCB 上游材料 | 候选卡点 | soft_bottleneck/watch | 低粗糙度表面处理、一致性和客户认证约束 | unchanged_watch | AI PCB 专项 | 2026H2-2027；精确月度 N/A | PCB 级 HVLP4/5 批量供货、加工费回落 | 跟德福/嘉元/诺德/铜冠披露 |
| 光连接 / MT ferrule / FAU / 主动对准测试 | 光互连迁移 | 未来迁移 | watch | CPO/OCS/ELS 和 AI factory 光密度提升可能迁移瓶颈 | watch_enhanced | Corning/NVIDIA、光模块专项 | N/A | Corning 扩产按期释放，无源件无涨价/交期 | 跟 Corning 会议和 A/台股传导 |
| CoWoS / advanced packaging / equipment | 先进封装 | 战略观察 | strategic_watch | AI accelerator 结构核心，但本期缺新增供需缺口硬证据 | strengthened_watch | AMAT Q2、TSMC April revenue、Amkor Q1 | N/A | TSMC/OSAT 产能快于需求 | 跟 TSMC/OSAT/基板/设备交期 |
| AI networking / retimer / Ethernet | 高速互连 | 战略观察 | strategic_watch | 网络需求强，但未见电互连/交换机/retimer 短缺证据 | unchanged | Arista/Astera/Marvell/Broadcom 前期证据 | N/A | 出现 allocation/交期则升级 | 跟订单、交期和客户导入 |

## 本期深挖方向

- 主深挖 1：`HBM / AI memory / enterprise SSD`。重点跟踪 HBM4/HBM4E 客户认证、DRAM/NAND 晶圆分配、enterprise SSD/KV cache offload、HBM packaging 和 2027 产能释放。
- 主深挖 2：`数据中心电力 / 液冷 / rack power / 预制化基础设施`。重点把 backlog 拆成变压器、switchgear、UPS、busway、rack PDU、CDU、冷板、quick connector、预制模块、并网和工程交付约束。

## 三类排名快照

| 类型 | 排名 | 对象 | 理由 | 证据等级 | 风险 |
|---|---:|---|---|---|---|
| 结构重要性 | 1 | GPU/ASIC + TSMC/CoWoS/advanced packaging | AI 算力核心入口，决定全链需求传导 | A | 本期仍缺新增短缺量化 |
| 结构重要性 | 2 | HBM / AI memory / enterprise SSD | 合格内存与存储供给直接限制 AI accelerator 和推理扩张 | A/B | 2027 供给释放 |
| 结构重要性 | 3 | 高端 EML / InP / CW / pump laser | 光互连瓶颈支撑 1.6T/CPO/OCS | A/B | 扩产兑现 |
| 结构重要性 | 4 | 数据中心电力/液冷/rack power | AI factory 建设进入 GW 级 power 与 thermal 约束 | A | 单品交期未证实 |
| 结构重要性 | 5 | AI PCB/CCL/电子布/HVLP | 高速高层材料规格升级 | A/B/C2 | 交易端证据不足 |
| 基本面质量 | 1 | NVIDIA / TSMC / SK hynix / Samsung / Micron | 控制算力、先进制造和 HBM 利润池 | A/B | 估值与地缘 |
| 基本面质量 | 2 | Lumentum / Coherent | 控制高速光源和 InP/CW 核心节点 | A | 扩产和年降 |
| 基本面质量 | 3 | Vertiv / Eaton / Schneider | 数据中心电力和 thermal 全球龙头 | A | 项目周期 |
| 基本面质量 | 4 | 生益科技 / 沪电股份 / 深南电路 / 胜宏科技 | A 股 AI PCB/CCL 硬证据较多 | A/B | 涨价传导与客户认证 |
| 基本面质量 | 5 | 中际旭创 / 新易盛 / 天孚通信 | A 股光模块和光器件映射成熟 | A/B | 拥挤与毛利年降 |
| 业绩弹性 | 1 | HBM/AI memory 供应商 | ASP、LTA、产品结构和客户锁量最直接 | A/B | 供给释放 |
| 业绩弹性 | 2 | Lumentum / Coherent | EML/CW/pump/InP 产能爬坡与客户锁单 | A | 单品扩产后价格回落 |
| 业绩弹性 | 3 | 数据中心电力/液冷龙头 | backlog 转收入、液冷 attach rate、系统交付 | A | 单品瓶颈未拆清 |
| 业绩弹性 | 4 | CCL/电子布/HVLP | 涨价和材料代际升级 | A/B/C2 | 认证和成交价不确定 |
| 业绩弹性 | 5 | AI networking/retimer | 高增长但非短缺主线 | A | 估值和竞争 |
| 交易弹性 | 1 | A 股光模块/CPO 弹性组 | 催化密度、成交额、波动最高 | A/B/C | 拥挤和 C 级扩散 |
| 交易弹性 | 2 | PCB 上游高弹性组 | 电子布/Q 布/HVLP 市值弹性和主题弹性强 | B/C2 | 高端收入证据不足 |
| 交易弹性 | 3 | 数据中心电力/液冷 A 股组 | soft_watch 升温，订单纯度若验证有预期差 | A/B 待补 | 订单纯度不足 |
| 交易弹性 | 4 | 美股光源/光连接组 | LITE/COHR/GLW 官方催化密集 | A | 扩产兑现压制 ASP |
| 交易弹性 | 5 | 美股互连/电力组 | ALAB/ANET/VRT/ETN 流动性好、成长明确 | A | 预期高 |

## 下期默认跟踪问题

1. HBM/HBM4/HBM4E 是否出现官方客户认证、allocation、ASP、LTA、库存天数、capex 和 packaging 节奏的新 A/B 证据？
2. 光模块专项是否补出 Lumentum 官方 transcript、Coherent 10-Q、Corning 5/19 J.P. Morgan TMC 对光源、InP、光连接、FAU/MT/连接器的单品证据？
3. AI PCB 专项是否验证台系 5 月营收、CCL/prepreg 成交价、高端电子布分产品交期/配额和 HVLP4/5 批量交付？
4. CoreWeave、Vertiv、Eaton、Schneider、nVent 及 A 股公司是否披露变压器、switchgear、UPS、CDU、冷板、预制模块的单品交期或项目延期？
5. TSMC/ASE/Amkor/AMAT/Advantest/基板厂是否出现 CoWoS/advanced packaging 新增合格产能不足、客户排产或设备交期拉长证据？

## 最近证据源

- CoreWeave Q1 2026 results: https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-First-Quarter-2026-Results/default.aspx
- Micron FY2Q26 results and prepared remarks: https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-results-second-quarter-fiscal-2026
- TrendForce 2Q26 memory pricing survey: https://www.trendforce.com/presscenter/news/20260331-12995.html
- Samsung Electronics 1Q26 presentation: https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2026_1Q_conference_eng.pdf
- Lumentum FY3Q26 10-Q: https://www.sec.gov/Archives/edgar/data/1633978/000162828026030777/lite-20260328.htm
- Lumentum Q3 FY26 presentation: https://s21.q4cdn.com/377324469/files/doc_financials/2026/q3/Q3-FY26-Earnings-Presentation_final.pdf
- Coherent Q3 FY26 presentation: https://www.coherent.com/content/dam/coherent/site/en/documents/investors/investor-presentations/2026/may-6/investor-presentation-20260506.pdf
- Corning/NVIDIA partnership: https://investor.corning.com/news-and-events/news/news-details/2026/NVIDIA-and-Corning-Announce-Long-Term-Partnership-To-Strengthen-U-S--Manufacturing-for-AI-Infrastructure/default.aspx
- Panasonic CCL/prepreg price revision: https://industrial.panasonic.com/ww/electronic-materials/news/2026-04-09-em-ccl
- Applied Materials Q2 FY26 release: https://ir.appliedmaterials.com/static-files/c02d8253-7dc3-44d3-a9a9-29d07fb26f17
- Eaton Q1 2026 release: https://www.eaton.com/us/en-us/company/news-insights/news-releases/2026/eaton-reports-record-first-quarter-2026-results.html
- Schneider Electric Q1 2026 revenues: https://www.se.com/ww/en/about-us/investor-relations/financial-results/
- Vertiv Q1 2026 presentation: https://s205.q4cdn.com/554782763/files/doc_financials/2026/q1/Vertiv-First-Quarter-2026-Results-Presentation.pdf
- TSMC April 2026 revenue: https://www.sec.gov/Archives/edgar/data/1046179/000104617926000213/tsm-revenue20260508.htm
