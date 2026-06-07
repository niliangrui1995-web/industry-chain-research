# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-06-07
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-06-07.md`
覆盖窗口：2026-05-31 至 2026-06-07，北京时间
当前阶段：第六期全链雷达，已吸收光模块专项 2026-06-07 状态与 AI PCB 专项 2026-06-07 状态。

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

1. `HBM / server DRAM / NAND / enterprise SSD / AI server parts supply`：维持并强化为全链最硬 `hard_bottleneck`。HPE Q2 FY26 给出 AI Systems backlog 59 亿美元、新 AI Systems orders 18 亿美元；Broadcom Q2 FY26 给出 AI semiconductor revenue 108 亿美元、Q3 guidance 160 亿美元；TrendForce 6/1-6/2 继续证明 DRAM/HBM 供需紧张和 pricing power。预计 `2026H2-2027H1`，若 HBM4E/eSSD/CPU/packaging ramp 慢可延至 `2027H2`。
2. `高端 EML / InP / CW-DFB / pump / ELS / 1.6T 光互连组件`：吸收光模块专项，维持 `hard_bottleneck`。TrendForce 6/3 明确 NVIDIA、Google、Meta 等锁定 EML/CW-DFB LD 产能，2026 年 EML+CW-DFB LD 合计月产能预计约 5,070 万颗；Ciena/Lumentum 继续强化 optical demand。预计 EML/InP `2026H2-2027H1`，CW/pump/ELS/CPO 可到 `2027H2-2028H1`。
3. `M7/M8/M9/M10 CCL / prepreg + 高端电子布 / HVLP`：吸收 AI PCB 专项，维持 `soft_bottleneck+`。台光电、台燿、联茂等 5 月营收和涨价/lead time 线索支持 CCL/prepreg 偏紧；高端电子布仍 soft+；HVLP4/5 当前批量短缺证据不足，保持 `watch+`。预计 CCL `2026H2-2027H1`；电子布 `2026H2-2027H1`；Q cloth/石英布偏 `2027H2-2028`。
4. `数据中心电力 / 并网 / 800VDC / rack power / 液冷`：维持全链 `soft_bottleneck`，PJM/Ohio/PA 区域按 `regional hard operational bottleneck`。FERC large-load docket、Ohio 6/1 testimony、JLL 2026 outlook、NVIDIA DSX、Infineon/EPC 800VDC/MGX 证据增强。区域并网预计 `2026H2-2030`，全球设备/rack power/液冷预计 `6-24 个月`，但单品交期仍 `N/A`。
5. `CoWoS / EFB / SoIC / advanced packaging / substrate`：维持 `soft_bottleneck/watch+`，不升 hard。Broadcom/Marvell/NVIDIA/custom ASIC 和 HBM 需求强，但缺 TSMC/OSAT 官方交期、allocation、良率或客户排产延期。预计 `2026H2-2027H1` 偏紧，2027 后边际缓解。
6. `AI networking switch ASIC / NIC / DPU / retimer / custom XPU`：维持 `strategic_watch`，未来可能升 `watch_to_soft`。Broadcom Q2 FY26 证明 AI networking 和 custom ASIC 需求，但未见 networking silicon 供应短缺、lead time 或 allocation。

## 专项吸收状态

| 专项任务 | 最新状态文件 | 本期吸收结论 | 对全链排序的影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | 高端 EML/InP/CW-DFB/pump/ELS 为 hard；模块整机 soft/eased；FAU/MT/主动对准/WLBI/光电测试/热管理为 future watch | 光源链排当前核心卡点第 2；1.6T/3.2T 光互连组件、FAU/主动对准/热管理列未来迁移 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | M7/M8/M9/M10 CCL/prepreg soft+ confirmed；高端电子布 soft+；HVLP4/5 降级 watch；板厂良率/测试 watch+ | PCB 材料链排当前核心卡点第 3；M9/M10/Q cloth/HVLP/板厂测试列未来迁移池 |

## 当前全链堵点账本

| 节点 | 所属赛道 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|---|
| HBM / HBM4E / server DRAM / NAND / enterprise SSD | 存储 | 当前主堵点 | hard_bottleneck | AI server、agentic inference 和 custom ASIC 需求超过合格 memory/storage 供给；DRAM wafer allocation、HBM 堆叠/测试、HBM4E 认证、NAND/eSSD 产能、LTA 锁量共同约束 | worsened/strengthened | HPE Q2 FY26、Broadcom Q2 FY26、TrendForce 6/1-6/2、Samsung HBM4E、Micron Computex | 2026H2-2027H1；可延至 2027H2 | DRAM/NAND/HBM 价格涨幅收敛、库存回升、多供方 HBM4E 认证 | 跟 HPE 10-Q/transcript、Micron/SK hynix/Samsung、Dell/HPE/SMCI |
| AI server BOM / parts supply | 服务器/ODM | 当前软堵点 | soft_bottleneck+ | ODM/server 厂有订单与制造能力，但受 memory、CPU/GPU、storage、PCB、power/cooling 等 parts supply 同步约束 | strengthened | HPE transcript、Dell 上期 evidence | 2-4 个季度；若 memory/CPU/PCB 释放可降级 | ODM 交付不再受 parts 约束，backlog/shipments 比例回落 | 找 HPE 官方 transcript、SMCI/ODM 二次验证 |
| 高端 EML / InP / CW-DFB / pump / ELS | 光互连 | 当前主堵点 | hard_bottleneck | 1.6T/3.2T、CPO/OCS/ELS 对高速光源和 InP 合格产能需求超过供给 | unchanged/worsened | 光模块专项、TrendForce 6/3、Ciena Q2 FY26、Lumentum Q3 FY26 | EML/InP 2026H2-2027H1；CW/pump/ELS/CPO 可到 2027H2-2028H1 | allocation 解除、交期恢复、6 英寸 InP 合格产能兑现 | 交给光模块专项追 Lumentum/Coherent/Ciena/Corning |
| 1.6T/3.2T optical driver/TIA/DSP/GaN/LPO-LRO/NPO-CPO | 高速互连 | 候选软堵点 | soft_bottleneck/watch+ | 1.6T/3.2T 对高速模拟、DSP/SerDes、GaN、功耗、测试和认证要求上升 | strengthened | Broadcom Q2 FY26、TrendForce、光模块专项 | 2026H2-2027H2 watch；精确持续 N/A，需二供验证 | 同业不再提产能缺口，交期/价格正常化 | 找 Credo/Marvell/Broadcom/Lumentum/Coherent 二次验证 |
| M7/M8/M9/M10 CCL / prepreg | AI PCB/材料 | 当前软堵点 | soft_bottleneck+ | 低损耗配方、特种电子布、HVLP、树脂、层压良率和客户 AVL 共同约束 | confirmed/worsened | AI PCB 专项、台光电/台燿/联茂 5 月营收、涨价/lead time | 2026H2 中高置信；2027H1 中等置信 | 报价停涨/回落，lead time 回常态，二供进入 AVL | 交给 PCB 专项跟台系 6 月营收、M8/M9/M10 lead time |
| 高端电子布 / Low CTE / T-glass / Low Dk/Df | PCB 上游材料 | 当前软堵点 | soft_bottleneck+ | 窑炉、拉丝、织布、后处理、良率和客户认证约束 | unchanged_to_worsened | AI PCB 专项：中材科技、沪电、行业研究 | 2026H2-2027H1；Q cloth/石英布 2027H2-2028 | 高端布库存恢复、报价回落、交期缩短 | 跟分产品交期、配额和 AVL |
| HVLP/VLP/RTF PCB 铜箔 | PCB 上游 | 候选卡点 | soft_bottleneck/watch+ | 低粗糙度一致性、表面处理、添加剂和客户认证约束；HVLP4/5 批量证据不足 | downgraded_to_watch_for_HVLP4_5 | AI PCB 专项：诺德 HVLP1/2/3，HVLP4 仍送样；德福扩产 | 2026H2-2027 watch；精确持续 N/A | HVLP4/5 多客户批量供货、加工费回落 | 跟德福/诺德/嘉元/铜冠 |
| 数据中心电力 / 并网 / grid operations | 电力基础设施 | 当前软堵点；区域 hard | soft_bottleneck；regional hard operational | 大负载建设速度超过电网、备用容量、并网和输配电建设速度，动态负载增加运行稳定性压力 | strengthened | FERC、Ohio testimony、JLL、NVIDIA DSX | 区域 2026H2-2030；全球设备链 6-24 个月 | reserve margin 改善，容量拍卖价格回落，项目延期减少 | 跟 FERC June action、PJM/utility、tariff、项目延期 |
| transformer / switchgear / UPS / busway / rack PDU / CDU / 冷板 | 电力/热管理 | 当前软堵点观察 | soft_bottleneck/watch | 高功率机柜和液冷系统认证、可靠性、集成和现场交付约束；JLL 证明 lead time elevated | strengthened | JLL 2026 outlook、NVIDIA DSX、Schneider/Motivair 上期 | 6-24 个月；精确交期 N/A | CDU/冷板/PDU/transformer/switchgear 交期缩短 | 跟单品 lead time、订单纯度 |
| 800VDC / SST / SiC / GaN power conversion | Rack power / power semis | 未来迁移观察 | watch_to_soft | 高功率 rack 推动 800VDC、GaN/SiC、hot-swap/protection 和系统认证 | upgraded_watch | NVIDIA DSX/MGX、Infineon、EPC、Microchip/TI 上期 | 2026H2-2028；精确持续 N/A | 800VDC 推迟，传统架构继续满足；或 design win 无法转收入 | 跟 Infineon/EPC/TI/Microchip/Delta design win |
| CoWoS / EFB / SoIC / advanced packaging / substrate | 先进封装 | 当前软堵点观察 | soft_bottleneck/watch+ | GPU/ASIC multi-die 和 HBM 需求推高 2.5D/3D 封装、基板、键合、测试和设备负荷 | unchanged | Broadcom、Marvell/NVIDIA 上期、TrendForce HBM | 2026H2-2027H1 偏紧，2027 后边际缓解 | TSMC/OSAT 交期恢复，客户不再锁封装产能 | 跟 TSMC/ASE/Amkor/基板/设备 |
| AI networking switch ASIC / NIC / DPU / retimer / custom XPU | 高速互连 | 战略观察 | strategic_watch | 需求强，但缺 silicon allocation、lead time 或出货受限证据 | attention_up | Broadcom Q2 FY26 | N/A | 出现 allocation/交期则升级 | 跟 Broadcom/Marvell/NVIDIA/Arista |

## 本期深挖方向

- 主深挖 1：`HBM/DRAM/NAND/eSSD + AI server parts supply`。重点跟踪 HPE 证据能否官方化、Dell/HPE/SMCI/ODM 是否继续点名 parts supply、约束是否从 memory 扩散到 CPU、PCB、HDD/eSSD、power/cooling。
- 主深挖 2：`数据中心电力/并网 + 800VDC/SST/rack power/液冷`。重点把区域 hard operational 约束和全球设备/液冷单品 soft/watch 分开，跟踪 FERC/PJM/Ohio、JLL/CBRE、transformer/switchgear/UPS/CDU/PDU lead time、800VDC design win 转收入。

## 三类排名快照

| 类型 | 排名 | 对象 | 理由 | 证据等级 | 风险 |
|---|---:|---|---|---|---|
| 结构重要性 | 1 | HBM / DRAM / NAND / eSSD | AI server 与 agentic inference 的直接容量/带宽/存储约束，本周 HPE/Broadcom/TrendForce 强化 | A/B | 供给释放和认证 |
| 结构重要性 | 2 | CoWoS / advanced packaging / substrate | GPU/ASIC/HBM 组合的核心工艺与交付节点 | A/B | 缺官方交期，不能升 hard |
| 结构重要性 | 3 | 高端 EML / InP / 1.6T 光互连 | AI scale-out 和 CPO/OCS/ELS 的下一轮瓶颈迁移核心 | A/B | 扩产兑现后 ASP 回落 |
| 结构重要性 | 4 | 数据中心电力 / 并网 / rack power / 液冷 | AI factory 从芯片订单转向投产，电力决定可用算力 | A/B | 区域 hard 与全球设备 hard 混同 |
| 结构重要性 | 5 | AI PCB / CCL / 电子布 / HVLP | 高速材料升级和板级交付的重要中游 | A/B/C | 高端分产品证据不足 |
| 业绩弹性 | 1 | HBM/DRAM/NAND/eSSD 供应商 | ASP、LTA、结构升级、紧供给同时出现 | A/B | 2027-2028 供给释放 |
| 业绩弹性 | 2 | 光源/InP/1.6T 光互连组件 | hard 瓶颈 + 1.6T/3.2T/CPO 迁移，单品 margin/收入弹性大 | A/B | 单品分拆和二供证据不足 |
| 业绩弹性 | 3 | CCL/高端电子布/HVLP | 涨价、认证、材料代际升级共同驱动 | A/B/C | A 股高端收入占比和 AVL 缺口 |
| 业绩弹性 | 4 | Power/thermal/rack power/800VDC | backlog 转收入、项目交付、液冷 attach rate、power semis design win | A/B | 单品交期不清，项目延期 |
| 业绩弹性 | 5 | Custom ASIC/networking silicon/advanced packaging | 需求强，但 A 股映射弱且大市值 | A/B | 交期证据不足 |
| 交易弹性 | 1 | A 股 PCB 上游材料/设备组 | 专项证据连续强化，低市值/高换手弹性强；行情未刷新写 N/A | A/B/C | 高端收入和交易拥挤 |
| 交易弹性 | 2 | A 股光模块/光器件/CPO 组 | 光源 hard 与 1.6T/ELS/FAU 迁移共同催化；行情未刷新写 N/A | A/B/C | 估值和年降 |
| 交易弹性 | 3 | A 股电力/液冷/800VDC 组 | 区域电力 hard + 800VDC/SST 迁移有预期差；行情未刷新写 N/A | A/B | 订单纯度不足 |
| 交易弹性 | 4 | 美/台 networking silicon 与 ASIC 组 | Broadcom Q2 改变关注度，但缺 shortage 证据 | A/B | 预期高、非当前硬堵点 |
| 交易弹性 | 5 | 美/韩/台 memory/packaging leaders | 基本面强但大市值，交易弹性相对低 | A/B | 供给周期和估值 |

## 下期默认跟踪问题

1. HPE 是否发布官方 Q2 FY26 transcript 或 10-Q，能否把 DRAM/NAND supply constraints、AI systems backlog、procurement/LTA 从 B 级 transcript 升为 A 级？
2. HBM/HBM4E：Samsung HBM4E samples 是否进入客户认证节点；Micron/SK hynix 是否披露 HBM4E/HBM4 LTA、2027 capex、库存天数或交期？
3. Broadcom/Marvell/Arista/NVIDIA：AI networking silicon、DSP/laser、substrate/advanced packaging 是否出现 allocation、交期或客户排产延期，而不只是强需求？
4. 电力/并网：FERC June action、PJM/Ohio/PA 大负载 tariff、备电调用、transformer/switchgear/UPS/CDU lead time 是否补 A/B 级单品证据？
5. 专项吸收：光模块跟 Lumentum/Ciena/Coherent/Corning/Fujikura；PCB 跟台系 6 月营收、M9/M10/Q cloth、HVLP4/5、板厂良率/测试和耗材 backlog。

## 最近证据源

- HPE Q2 FY26 presentation: https://investors.hpe.com/~/media/Files/H/HP-Enterprise-IR/documents/q2-2026/q2-2026-earnings-presentation.pdf
- HPE Q2 FY26 transcript: https://www.fool.com/earnings/call-transcripts/2026/06/01/hpe-q2-2026-earnings-call-transcript/
- Broadcom Q2 FY26 official release: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-second-quarter-fiscal-year-2026-financial
- Broadcom Q2 FY26 transcript: https://www.fool.com/earnings/call-transcripts/2026/06/03/broadcom-avgo-q2-2026-earnings-transcript/
- TrendForce DRAM 1Q26/2Q26: https://www.trendforce.com/presscenter/news/20260601-13070.html
- TrendForce HBM pricing / HBM4 2027: https://www.trendforce.com/presscenter/news/20260602-13074.html
- Samsung HBM4E samples: https://semiconductor.samsung.com/news-events/news/samsung-electronics-begins-shipment-of-industry-first-hbm4e-samples/
- Micron Computex 2026: https://investors.micron.com/node/50566/pdf
- TrendForce SK chair / memory tightness: https://www.trendforce.com/news/2026/06/02/news-sk-chair-sees-memory-shortage-through-2030-eyes-capacity-doubling-and-stronger-tsmc-taiwan-ties/
- TrendForce EML/CW-DFB LD: https://www.trendforce.com/presscenter/news/20260603-13077.html
- Ciena Q2 FY26 SEC exhibit: https://www.sec.gov/Archives/edgar/data/936395/000162828026040614/ex9912026q2earningspressre.htm
- Ciena Q2 FY26 transcript: https://www.fool.com/earnings/call-transcripts/2026/06/05/ciena-cien-q2-2026-earnings-transcript/
- Lumentum Q3 FY26 presentation: https://s21.q4cdn.com/377324469/files/doc_financials/2026/q3/Q3-FY26-Earnings-Presentation_final.pdf
- Taiwan PCB/CCL May revenue summary: https://money.udn.com/money/story/5607/9548766
- Taiwan Union Technology May revenue: https://www.moneydj.com/kmdj/news/newsviewer.aspx?a=890a6936-9332-4995-ad7b-6b047ec1c460
- NVIDIA DSX: https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-DSX-Gives-Infrastructure-Builders-the-Playbook-for-AI-Factories/default.aspx
- FERC large-load interconnection docket: https://www.ferc.gov/news-events/news/ferc-act-large-load-interconnection-docket-june-2026
- Ohio data-center testimony: https://search-prod.lis.state.oh.us/api/v2/general_assembly_136/committees/cmte_h_data_centers_1/meetings/cmte_h_data_centers_1_2026-06-01-1200_1349/testimony/18082/bryden_pmo_dc_select_cmte_testimony.pdf
- JLL 2026 Global Data Center Outlook: https://www.jll.com/content/dam/jllcom/en/global/documents/reports/research-reports/26-research-global-data-center-outlook-new.pdf
- Infineon MGX / 800VDC: https://www.infineon.com/press-release/2026/infxx202605-092
- EPC 800V-to-12.5V MGX: https://epc-co.com/epc/about-epc/events-and-news/news/artmid/1627/articleid/3317/epc-supports-ai-infrastructure-built-on-nvidia-mgx%E2%84%A2-with-high-efficiency-800v-to-125v-power-conversion
- Optical module weekly report: `artifacts/weekly_chain_tracking/optical_module/2026-06-07.md`
- AI PCB weekly report: `artifacts/weekly_chain_tracking/ai_pcb/2026-06-07.md`
