# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-05-24
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-05-24.md`
覆盖窗口：2026-05-18 至 2026-05-24，北京时间
当前阶段：第四期全链雷达，已吸收光模块专项 2026-05-17 状态与 AI PCB 专项 2026-05-24 状态。

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

## 本期全链结论

1. `HBM / 高端 DRAM / enterprise SSD`：维持全链最硬约束，`hard_bottleneck`。NVIDIA FY2027 Q1 Data Center 收入 752 亿美元、同比 +92%，TrendForce 指向 AI server 出货继续上修，叠加 Micron/Samsung/TrendForce 既有供需和涨价证据，支持需求超过合格 HBM/DRAM/NAND/eSSD 供给。预计持续 `2026H2-2027H1`，若 HBM4E、packaging 或 eSSD ramp 慢可延至 `2027H2`。
2. `CoWoS / EFB / advanced packaging`：从 `strategic_watch` 上调为 `soft_bottleneck/watch+`。AMD 宣布超过 100 亿美元台湾生态投资并扩大先进封装能力，Lam 建 Panel-Level Packaging CoE，B 级来源称 CoWoS 扩产仍未完全解决 AI 芯片需求下的供应瓶颈。缺 TSMC/OSAT 官方交期和 allocation，暂不升 hard。预计 `2026H2-2027H1` 偏紧，2027 后边际缓解。
3. `高端 EML / InP / CW laser / pump laser`：继续吸收光模块专项，维持 `hard_bottleneck`。Lumentum 10-Q 的 demand outpacing supply/allocation 口径和 Coherent 6 英寸 InP ramp 支撑。预计 `2026H2-2027H1`，CPO/OCS 上修可延至 `2027H2`。
4. `M7/M8/M9 CCL / prepreg`：吸收 AI PCB 专项 2026-05-24 报告，维持并强化为 `soft_bottleneck`。NVIDIA/Cisco/TTM 需求、Panasonic 涨价、Vexos lead time 和 TrendForce/DigiTimes 价格/预购共同支持。预计 `2026Q2-2026H2` 偏紧，`2027H1` 仍需观察。
5. `高端电子布 / Low CTE / T-glass / Low Dk/Df`：吸收 AI PCB 专项，维持 `soft_bottleneck+`。Nittobo 上调 FY2027 目标和 Special Glass capex，支持供给刚性；仍缺官方交期、配额、断供证据。预计 `2026H2-2027H1`，Q 布/石英布偏 `2027H2-2028`。
6. `数据中心电力 / 并网 / transformer / switchgear / UPS / rack power / 液冷`：从 `soft_bottleneck/watch` 升级为 `soft_bottleneck`。DOE 对 PJM 的 5/18 和 5/21 应急授权证明区域电力和可调度电源存在运营性硬约束；Siemens Energy、Eaton、GE Vernova、nVent、CoreWeave 等 A 级证据支撑订单和 backlog 强。全链不升 hard，因为缺逐项单品 lead time 和 allocation。预计 `6-24 个月`，输电侧更长。
7. `HVLP/VLP/RTF PCB 铜箔`：吸收 AI PCB 专项，从 watch 强化为 `soft_bottleneck/watch+`。德福科技年报证明 PCB 级 HVLP 导入进展，但 HVLP5 批量收入和多客户证据不足。预计 `2026H2-2027`，精确月度 `N/A`。
8. `AI networking / retimer / NIC / DPU / Ethernet switch`：需求强、结构重要，但仍缺 allocation、交期、缺料证据，维持 `strategic_watch`。

## 专项吸收状态

| 专项任务 | 最新状态文件 | 本期吸收结论 | 对全链排序的影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | 高端 EML/InP/CW/pump laser 为硬堵点；模块整机装配 soft 已缓解；FAU/MT/光连接/主动对准/热管理为未来迁移 watch | 光源链排当前核心卡点第 3；光连接和无源精密件进入未来卡点池 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | M7/M8/M9 CCL/prepreg 为 soft；高端电子布为 soft+；HVLP 为 watch+；板厂良率/测试仍 watch | PCB 材料链排当前核心卡点第 4；Q 布/HVLP/板厂测试进入未来迁移池 |

## 当前全链堵点账本

| 节点 | 所属赛道 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|---|
| HBM / HBM4 / 高端 DRAM / enterprise SSD | 存储 | 当前主堵点 | hard_bottleneck | AI server、GPU/ASIC、KV cache/eSSD 需求超过合格 HBM/DRAM/NAND/eSSD 供给；晶圆分配、堆叠、封装、客户认证和 LTA 锁量共同约束 | unchanged/strengthened | NVIDIA FY2027 Q1、TrendForce AI server、Micron/Samsung/TrendForce 既有证据 | 2026H2-2027H1；可延至 2027H2 | 价格涨幅收敛、库存回升、客户不锁量、HBM4E 多供方认证 | 跟 HBM4E 认证、capex、库存天数、价格 |
| CoWoS / EFB / advanced packaging | 先进封装 | 当前软堵点/观察增强 | soft_bottleneck/watch+ | GPU/ASIC 多 die 与 HBM4E 抬高 2.5D 封装、基板、键合、测试、热管理和设备负荷 | upgraded | AMD 台湾生态投资、Lam PLP CoE、ASML/Reuters、Taipei Times | 2026H2-2027H1 偏紧；精确交期 N/A | TSMC/OSAT 交期恢复、客户不共投封装、替代封装顺利 | 跟 TSMC/ASE/Amkor/基板/设备交期 |
| 高端 EML / InP / CW laser / pump laser | 光模块上游 | 当前主堵点 | hard_bottleneck | 800G/1.6T/CPO/OCS 需求超过合格光源和 InP 产能，良率、客户锁定和封装测试约束 | unchanged | Lumentum 10-Q/Q3、Coherent Q3、光模块专项 | 2026H2-2027H1；CPO/OCS 上修可至 2027H2 | allocation 解除、交期恢复、6 英寸 InP 合格产能兑现 | 交给光模块专项追 transcript/单品缺口 |
| M7/M8/M9 CCL / prepreg | AI PCB/CCL | 当前软堵点 | soft_bottleneck | 低损耗配方、电子布、HVLP 铜箔、树脂、层压良率和客户认证共同约束 | worsened | AI PCB 专项、NVIDIA/Cisco/TTM、Panasonic、Vexos | 2026Q2-2026H2；2027H1 观察 | 报价停涨、交期回 4-8 周、二供进 AVL | 交给 PCB 专项跟台系 5/6 月营收和成交价 |
| 高端电子布 / Low CTE / T-glass / Low Dk/Df | PCB 上游材料 | 当前软堵点 | soft_bottleneck+ | 窑炉、成纤、织布、良率和客户 AVL 限制短期合格供给 | unchanged_to_worsened | Nittobo、TrendForce/DigiTimes、PCB 专项 | 2026H2-2027H1；Q 布/石英布 2027H2-2028 | 高端布库存恢复、价格回落、交期缩短 | 跟分产品交期、配额、AVL |
| 数据中心电力 / 并网 / transformer / switchgear | 数据中心基础设施 | 当前软堵点 | soft_bottleneck；PJM 区域 hard operational | AI factory 从芯片订单转向 GW 级建设，firm power、并网和电力设备可能限制投产 | upgraded | DOE/PJM、CoreWeave、Siemens Energy、Eaton、GEV、WoodMac | 6-24 个月；输电侧更长 | DOE/PJM 应急不再复现、队列缩短、backlog 回落、交期正常化 | 跟单品 lead time 与项目延期 |
| UPS / busway / rack PDU / CDU / 冷板 / 液冷 | 数据中心电力/热管理 | 当前软堵点观察 | soft_bottleneck/watch | 机柜功率密度提升，rack power 和液冷系统认证、集成、可靠性约束 | upgraded_watch | nVent、Vertiv、Eaton、Schneider | 6-18 个月；精确交期 N/A | PDU/CDU/冷板交期缩短，液冷项目不延期 | 跟官方订单、交期和 A 股订单纯度 |
| HVLP/VLP/RTF PCB 铜箔 | PCB 上游材料 | 候选卡点 | soft_bottleneck/watch+ | 低粗糙度表面处理、一致性、添加剂和客户认证约束 | strengthened | 德福科技年报、DigiTimes、PCB 专项 | 2026H2-2027；精确月度 N/A | PCB 级 HVLP4/5 多客户批量供货、加工费回落 | 跟德福/嘉元/诺德/铜冠披露 |
| 光连接 / MT ferrule / FAU / 主动对准测试 | 光互连迁移 | 未来迁移 | watch | CPO/OCS/ELS 和 AI factory 光密度提升可能迁移瓶颈 | watch_enhanced | Corning/NVIDIA、光模块专项 | N/A | Corning 扩产按期释放，无源件无涨价/交期 | 跟 Corning 会议和 A/台股传导 |
| AI networking / retimer / Ethernet | 高速互连 | 战略观察 | strategic_watch | 网络需求强，但未见电互连/交换机/retimer 短缺证据 | unchanged | NVIDIA/Cisco/Arista/Astera/Marvell/Broadcom | N/A | 出现 allocation/交期则升级 | 跟订单、交期和客户导入 |

## 本期深挖方向

- 主深挖 1：`HBM / 高端 DRAM / enterprise SSD + CoWoS / 2.5D advanced packaging`。重点跟踪 HBM4/HBM4E 客户认证、DRAM/NAND 晶圆分配、enterprise SSD/KV cache offload、TSMC/OSAT 封装排产、EFB/EMIB/FOPLP 替代路径和先进封装设备交期。
- 主深挖 2：`数据中心电力 / 并网 / 变压器 / switchgear / UPS / rack power / 液冷`。重点把 DOE/PJM 区域约束、CoreWeave active power、Siemens/Eaton/GEV/nVent/Vertiv backlog 拆成单品 lead time、项目延期和 A 股订单纯度。

## 三类排名快照

| 类型 | 排名 | 对象 | 理由 | 证据等级 | 风险 |
|---|---:|---|---|---|---|
| 结构重要性 | 1 | GPU/ASIC + TSMC/advanced packaging | AI 算力核心入口，决定全链需求传导 | A | 不等于 GPU 成品短缺 |
| 结构重要性 | 2 | HBM / 高端 DRAM / enterprise SSD | 合格内存与存储供给直接限制 AI accelerator 和推理扩张 | A/B | 2027 供给释放 |
| 结构重要性 | 3 | 数据中心电力/并网/液冷/rack power | AI factory 建设进入 GW 级 power 与 thermal 约束 | A/B | 单品交期仍待补 |
| 结构重要性 | 4 | 高端 EML / InP / CW / pump laser | 光互连瓶颈支撑 1.6T/CPO/OCS | A/B | 扩产兑现 |
| 结构重要性 | 5 | AI PCB/CCL/电子布/HVLP | 高速高层材料规格升级 | A/B/C2 | 高端收入和交期证据不足 |
| 基本面质量 | 1 | NVIDIA / TSMC / SK hynix / Samsung / Micron | 控制算力、先进制造和 HBM 利润池 | A/B | 估值与地缘 |
| 基本面质量 | 2 | Lumentum / Coherent | 控制高速光源和 InP/CW 核心节点 | A | 扩产和年降 |
| 基本面质量 | 3 | Vertiv / Eaton / Schneider / Siemens Energy / GE Vernova | 数据中心电力和 thermal 全球龙头 | A/B | 项目周期 |
| 基本面质量 | 4 | Panasonic / 台光电 / 生益科技 / Nittobo | CCL/电子布材料卡点映射最硬 | A/B | 涨价传导与客户认证 |
| 基本面质量 | 5 | 中际旭创 / 新易盛 / 天孚通信 / 沪电股份 / TTM | 光模块与板厂交付能力强 | A/B | 拥挤与毛利年降 |
| 业绩弹性 | 1 | HBM/AI memory/eSSD 供应商 | ASP、LTA、产品结构和 capex 向高价值内存倾斜 | A/B | 供给释放 |
| 业绩弹性 | 2 | Lumentum / Coherent | EML/CW/pump/InP 产能爬坡与客户锁单 | A | 单品扩产后价格回落 |
| 业绩弹性 | 3 | 数据中心电力/液冷龙头 | backlog 转收入、液冷 attach rate、系统交付 | A/B | 项目延期 |
| 业绩弹性 | 4 | CCL/电子布/HVLP | 涨价和材料代际升级 | A/B/C2 | 认证和成交价不确定 |
| 业绩弹性 | 5 | advanced packaging/设备链 | 客户共投、合格产能爬坡和设备需求 | A/B | A 股映射弱 |
| 交易弹性 | 1 | PCB 上游高弹性组 | 本周涨幅和成交放大，材料卡点和设备迁移预期强 | A/B/C | 高端收入证据不足 |
| 交易弹性 | 2 | A 股光模块/CPO 弹性组 | 光源 hard 与 NVIDIA 光学合作继续催化 | A/B/C | 拥挤和估值 |
| 交易弹性 | 3 | 数据中心电力/液冷 A 股组 | 电力从 watch 升 soft，订单纯度若验证有预期差 | A/B 待补 | 订单纯度不足 |
| 交易弹性 | 4 | 美股光源/光连接组 | LITE/COHR/GLW 官方证据强 | A | 扩产兑现压制 ASP |
| 交易弹性 | 5 | 美股互连/电力/先进设备 | ALAB/ANET/VRT/ETN/AMAT 流动性好、成长明确 | A/B | 预期高 |

## 下期默认跟踪问题

1. HBM/HBM4E：Micron、Samsung、SK hynix 是否披露客户 allocation、HBM4E 认证、LTA、库存天数、2027 capex 与封装瓶颈？
2. CoWoS/advanced packaging：TSMC、ASE/SPIL/PTI、Amkor、基板厂、AMAT/Lam/ASML 是否披露新增交期、排产延迟、设备/基板 allocation？
3. 数据中心电力：DOE/PJM 应急是否复现，CoreWeave/云厂是否点名并网、电力设备或液冷导致项目延期，Eaton/Siemens/GEV/nVent/Vertiv 是否披露单品 lead time？
4. 光模块专项：Lumentum/Coherent/Corning 是否补出 EML/CW/pump、InP、光连接、FAU/MT/主动对准和热管理的单品缺口？
5. AI PCB 专项：台系 5 月营收、CCL/prepreg 成交价、高端电子布分产品交期/AVL、HVLP4/5 批量收入和板厂良率/测试瓶颈是否被 A/B 级证据验证？

## 最近证据源

- NVIDIA FY2027 Q1 results: https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2027/default.aspx
- TrendForce AI server forecast: https://www.trendforce.com/presscenter/news/20260520-13053.html
- AMD Taiwan ecosystem investment: https://ir.amd.com/news-events/press-releases/detail/1286/amd-announces-more-than-10-billion-in-taiwan-ecosystem-investments-to-accelerate-ai-infrastructure
- Lam Panel-Level Packaging CoE: https://newsroom.lamresearch.com/Lam-Research-Establishes-Panel-Level-Packaging-CoE
- DOE PJM emergency order 2026-05-18: https://www.energy.gov/articles/energy-secretary-issues-emergency-order-deploy-backup-generation-mid-atlantic-amid
- DOE Mid-Atlantic grid reliability 2026-05-21: https://www.energy.gov/articles/energy-secretary-strengthens-mid-atlantic-grid-reliability
- Wood Mackenzie AI data center power race: https://www.globenewswire.com/news-release/2026/05/21/3299471/0/en/breaking-the-speed-limit-wood-mackenzie-warns-ai-data-centre-power-race-threatens-projects-and-consumers.html
- Siemens Energy Q2 FY2026 shareholder letter: https://assets.siemens-energy.com/dam/352bf02e-bbc1-4061-b00d-b45200cd6b3b/2026-05-22-Shareholder-Letter-Q2-FY2026_EN-pdf_Original%20file.pdf
- nVent Q1 2026 release: https://s22.q4cdn.com/268397047/files/doc_financials/2026/q1/Q1-2026-NVT-Press-Release.pdf
- CoreWeave Q1 2026 results: https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-First-Quarter-2026-Results/default.aspx
- Micron FY2Q26 results and prepared remarks: https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-results-second-quarter-fiscal-2026
- TrendForce 2Q26 memory pricing survey: https://www.trendforce.com/presscenter/news/20260331-12995.html
- Samsung Electronics 1Q26 presentation: https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2026_1Q_conference_eng.pdf
- Lumentum FY3Q26 10-Q: https://www.sec.gov/Archives/edgar/data/1633978/000162828026030777/lite-20260328.htm
- Coherent Q3 FY26 results: https://www.coherent.com/news/press-releases/third-quarter-fiscal-year-2026-results
- Corning/NVIDIA partnership: https://investor.corning.com/news-and-events/news/news-details/2026/NVIDIA-and-Corning-Announce-Long-Term-Partnership-To-Strengthen-U-S--Manufacturing-for-AI-Infrastructure/default.aspx
- AI PCB weekly report: `artifacts/weekly_chain_tracking/ai_pcb/2026-05-24.md`
