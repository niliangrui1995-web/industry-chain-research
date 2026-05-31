# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-05-31  
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-05-31.md`  
覆盖窗口：2026-05-24 至 2026-05-31，北京时间  
当前阶段：第五期全链雷达，已吸收光模块专项 2026-05-31 状态与 AI PCB 专项 2026-05-31 状态。

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

1. `HBM / 高端 DRAM / enterprise SSD / AI server parts supply`：维持并强化为全链最硬 `hard_bottleneck`。Dell Q1 FY27 官方财报和业绩会同时给出 AI orders 244 亿美元、AI server revenue 161 亿美元、AI backlog 513 亿美元，并明确 demand outpacing supply、parts supply/memory 是主约束；TrendForce 指 Agentic AI 推动 HBM/DRAM/KV cache/高性能 SSD 需求且供给缺口短期难补。预计 `2026H2-2027H1`，若 HBM4E/eSSD/CPU/packaging ramp 慢可延至 `2027H2`。
2. `高端 EML / InP / CW / pump / 1.6T 光互连组件`：吸收光模块专项，维持 `hard_bottleneck`；1.6T driver/TIA/GaN/LPO-LRO/NPO-CPO 由 Semtech/Marvell/NVIDIA 证据强化为 `soft_bottleneck/watch+`。预计 EML/InP `2026H2-2027H1`，CW/pump/ELS/CPO 与 1.6T 组件可到 `2027H2-2028H1`，Semtech 分项仍需二供验证。
3. `M7/M8/M9 CCL / prepreg + 高端电子布 / HVLP`：吸收 AI PCB 专项，维持 `soft_bottleneck` 到 `soft_bottleneck+`。AI PCB 专项把 CCL 和电子布偏紧进一步增强；HVLP 仍为 `soft_bottleneck/watch+`。预计 CCL `2026H2` 偏紧、`2027H1` 仍观察；电子布 `2026H2-2027H1`；Q 布/石英布偏 `2027H2-2028`。
4. `数据中心电力 / 并网 / 800VDC / rack power / 液冷`：维持全链 `soft_bottleneck`，PJM/Ohio/PA 区域按 `regional hard operational bottleneck`。DOE/OCC/Ohio 证据强化大负载接入与电网运行约束；Schneider/Microchip/Infineon 证明 800VDC/SST/rack power 产品化。区域并网预计 `2026H2-2030`，全球电力/液冷单品预计 `6-24 个月` 但精确交期 `N/A`。
5. `CoWoS / EFB / SoIC / advanced packaging / substrate`：维持 `soft_bottleneck/watch+`，不升 hard。本周 Marvell、NVIDIA、AMD 证据证明 demand 和 ecosystem，但缺 TSMC/OSAT 官方交期、allocation、良率或客户排产延期。预计 `2026H2-2027H1` 偏紧，2027 后边际缓解。
6. `AI networking switch ASIC / NIC / DPU / retimer / custom XPU`：维持 `strategic_watch`，未来可能升 `watch_to_soft`。Marvell/NVIDIA 需求和生态强，但未见 networking silicon 供应短缺、lead time 或 allocation。

## 专项吸收状态

| 专项任务 | 最新状态文件 | 本期吸收结论 | 对全链排序的影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | 高端 EML/InP/CW/pump/ELS 为 hard；模块整机软堵点缓解；FAU/MT/主动对准/测试和热管理为未来迁移观察 | 光源链排当前核心卡点第 2；1.6T 光互连组件列未来潜在卡点 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | M7/M8/M9 CCL/prepreg soft worsened；高端电子布 soft+ worsened；HVLP watch+；板厂良率/测试仍 watch | PCB 材料链排当前核心卡点第 3；M9/M10/Q 布/HVLP/板厂测试列未来迁移池 |

## 当前全链堵点账本

| 节点 | 所属赛道 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|---|
| HBM / HBM4E / server DRAM / NAND / enterprise SSD | 存储 | 当前主堵点 | hard_bottleneck | AI server 与 agentic AI/KV cache 需求超过合格 memory/storage 供给，晶圆分配、HBM 堆叠、客户认证和 LTA 锁量共同约束 | worsened/strengthened | Dell Q1 FY27、Dell transcript、TrendForce、Samsung HBM4E 送样 | 2026H2-2027H1；可延至 2027H2 | DRAM/NAND/HBM 价格涨幅收敛、库存回升、多供方 HBM4E 认证 | 跟 Micron/Samsung/SK hynix、Dell/HPE/SMCI |
| AI server BOM / parts supply | 服务器/ODM | 当前软堵点 | soft_bottleneck+ | ODM 有制造能力但受 memory、microprocessors、NAND/DRAM/HDD/PCB 等 parts supply 同步约束 | new/upgraded | Dell transcript | 2-4 个季度；若 memory/CPU 释放可降级 | ODM 交付不再受 parts 约束，backlog/shipments 比例回落 | 找 HPE/SMCI/ODM 二次验证 |
| 高端 EML / InP / CW / pump / ELS | 光互连 | 当前主堵点 | hard_bottleneck | 1.6T/3.2T、CPO/NPO/ELS 对高速光源和 InP 合格产能需求超过供给 | unchanged/worsened | 光模块专项、Coherent 6 英寸 InP、Lumentum 既有 allocation | EML/InP 2026H2-2027H1；CW/pump/ELS/CPO 可到 2027H2-2028H1 | allocation 解除、交期恢复、6 英寸 InP 合格产能兑现 | 交给光模块专项追单品和客户认证 |
| 1.6T/3.2T optical driver/TIA/GaN/LPO-LRO/NPO-CPO | 高速互连 | 候选软堵点 | soft_bottleneck/watch+ | 1.6T/3.2T 对高速模拟、GaN、功耗、测试和认证要求上升 | new | Semtech Q1 FY27、Semtech transcript、Marvell/NVIDIA | 2026H2-2027；精确持续 N/A，需二供验证 | 同业不再提产能缺口，交期/价格正常化 | 找 Credo/Marvell/Coherent/Lumentum/Corning/Fujikura 验证 |
| M7/M8/M9 CCL / prepreg | AI PCB/材料 | 当前软堵点 | soft_bottleneck | 低损耗配方、电子布、HVLP、树脂、层压良率和客户 AVL 共同约束 | worsened | AI PCB 专项：沪电、建滔、联茂、Evertiq/NCAB | 2026H2 偏紧，2027H1 观察 | 报价停涨/回落，lead time 回常态，二供进入 AVL | 交给 PCB 专项跟台系营收和报价 |
| 高端电子布 / Low CTE / T-glass / Low Dk/Df | PCB 上游材料 | 当前软堵点 | soft_bottleneck+ | 窑炉、拉丝、织布、后处理、良率和客户认证约束 | worsened | 中材科技、沪电 IR、Evertiq | 2026H2-2027H1；Q cloth/石英布 2027H2-2028 | 高端布库存恢复、报价回落、交期缩短 | 跟分产品交期、配额和 AVL |
| HVLP/VLP/RTF PCB 铜箔 | PCB 上游 | 候选卡点 | soft_bottleneck/watch+ | 低粗糙度一致性、表面处理、添加剂和客户认证约束 | unchanged_to_future_supply_response | 德福高端 AI 电子电路铜箔项目、专项既有认证线索 | 2026H2-2027 watch；精确持续 N/A | HVLP4/5 多客户批量供货、加工费回落 | 跟德福/嘉元/诺德/铜冠 |
| 数据中心电力 / 并网 / grid operations | 电力基础设施 | 当前软堵点；区域 hard | soft_bottleneck；regional hard operational | 大负载建设速度超过电网、备用容量和并网供给建设速度，动态负载增加运行稳定性压力 | strengthened | DOE、OCC、Ohio/PJM、Schneider/TeraWulf | 区域 2026H2-2030；全球设备链 6-24 个月 | reserve margin 改善，容量拍卖价格回落，备电调用减少 | 跟 RTO/utility、tariff、项目延期 |
| transformer / switchgear / UPS / busway / rack PDU / CDU / 冷板 | 电力/热管理 | 当前软堵点观察 | soft_bottleneck/watch | 高功率机柜和液冷系统认证、可靠性、集成和现场交付约束，但本周缺单品短缺证据 | unchanged | Schneider/Motivair、Microchip、Infineon、既有 Eaton/nVent/Vertiv | 6-18 个月；精确交期 N/A | CDU/冷板/PDU 交期缩短，ASP/毛利回落 | 跟单品 lead time、订单纯度 |
| CoWoS / EFB / SoIC / advanced packaging / substrate | 先进封装 | 当前软堵点观察 | soft_bottleneck/watch+ | GPU/ASIC multi-die 和 HBM 需求推高 2.5D/3D 封装、基板、键合、测试和设备负荷 | unchanged | Marvell、NVIDIA NVLink Fusion、AMD advanced packaging 生态 | 2026H2-2027H1 偏紧，2027 后边际缓解 | TSMC/OSAT 交期恢复，客户不再锁封装产能 | 跟 TSMC/ASE/Amkor/基板/设备 |
| AI networking switch ASIC / NIC / DPU / retimer / custom XPU | 高速互连 | 战略观察 | strategic_watch | 需求强，但缺 silicon allocation、lead time 或出货受限证据 | unchanged/attention_up | Marvell Q1 FY27、NVIDIA NVLink Fusion | N/A | 出现 allocation/交期则升级 | 跟 Marvell/Broadcom/NVIDIA/Arista |

## 本期深挖方向

- 主深挖 1：`HBM/DRAM/NAND/eSSD + AI server parts supply`。重点跟踪 Dell 证据是否被 HPE/SMCI/ODM/云厂验证，约束是否仍集中在 memory，还是扩散到 CPU、microprocessors、PCB、HDD/eSSD。
- 主深挖 2：`数据中心电力/并网 + 800VDC/SST/rack power/液冷`。重点把区域 hard operational 约束和全球设备/液冷单品 soft/watch 分开，跟踪 RTO/utility、备电调用、tariff、项目延期、transformer/switchgear/CDU/PDU 单品 lead time。

## 三类排名快照

| 类型 | 排名 | 对象 | 理由 | 证据等级 | 风险 |
|---|---:|---|---|---|---|
| 结构重要性 | 1 | HBM / DRAM / NAND / eSSD | AI server 与 agentic AI 的直接容量/带宽/存储约束，本周有 Dell + TrendForce 强证据 | A/B | HBM4E 认证和供给释放 |
| 结构重要性 | 2 | CoWoS / EFB / advanced packaging / substrate | GPU/ASIC/HBM 组合的核心工艺与交付节点 | A/B | 本周缺官方交期，不能升 hard |
| 结构重要性 | 3 | 高端 EML / InP / 1.6T 光互连 | AI scale-out 和 CPO/NPO 的下一轮瓶颈迁移核心 | A/B | 扩产兑现后 ASP 回落 |
| 结构重要性 | 4 | 数据中心电力 / 并网 / rack power / 液冷 | AI factory 从芯片订单转向投产，电力决定可用算力 | A/B | 区域 hard 与全球设备 hard 混同 |
| 结构重要性 | 5 | AI PCB / CCL / 电子布 / HVLP | 高速材料升级和板级交付的重要中游 | A/B/C | 高端分产品证据不足 |
| 业绩弹性 | 1 | HBM/DRAM/NAND/eSSD 供应商 | ASP、LTA、结构升级、紧供给同时出现 | A/B | 2027 供给释放 |
| 业绩弹性 | 2 | 光源/InP/1.6T 光互连组件 | hard 瓶颈 + 1.6T 迁移，单品 margin/收入弹性大 | A/B | 单公司 Semtech 缺口需验证 |
| 业绩弹性 | 3 | CCL/高端电子布/HVLP | 涨价、认证、材料代际升级共同驱动 | A/B/C | A 股高端收入占比和 AVL 缺口 |
| 业绩弹性 | 4 | 数据中心电力/液冷/rack power | backlog 转收入、项目交付、液冷 attach rate | A/B | 单品交期不清，项目延期 |
| 业绩弹性 | 5 | Advanced packaging/设备/OSAT | 客户共投和合格产能爬坡，但 A 股映射弱 | A/B | 交期证据不足 |
| 交易弹性 | 1 | A 股 PCB 上游材料/设备组 | 专项证据连续强化，低市值/高换手弹性强；行情未刷新写 N/A | A/B/C | 高端收入和交易拥挤 |
| 交易弹性 | 2 | A 股光模块/光器件/CPO 组 | 光源 hard 与 1.6T 迁移共同催化；行情未刷新写 N/A | A/B/C | 估值和年降 |
| 交易弹性 | 3 | A 股电力/液冷/800VDC 组 | 区域电力 hard + 800VDC/SST 迁移有预期差；行情未刷新写 N/A | A/B | 订单纯度不足 |
| 交易弹性 | 4 | 美/台 networking silicon 与 ASIC 组 | Marvell/NVLink Fusion 改变关注度，但缺 shortage 证据 | A | 预期高、非当前硬堵点 |
| 交易弹性 | 5 | 美/韩/台 memory/packaging leaders | 基本面强但大市值，交易弹性相对低 | A/B | 供给周期和估值 |

## 下期默认跟踪问题

1. Dell 的 parts supply 约束是否被 HPE/SMCI/ODM 或云厂再次验证，是否从 memory 扩散到 CPU、PCB、HDD/eSSD 或 microprocessors？
2. HBM/HBM4E：Samsung 送样是否进入客户认证/量产时间表，Micron/SK hynix 是否补出 HBM4E、LTA、库存天数和 2027 capex？
3. 光互连：Semtech 的 HIFU/GaN 产能缺口是否能被 Credo、Marvell、Coherent、Lumentum、Corning、Fujikura 等第二来源验证？
4. 电力/并网：PJM/Ohio/PA 是否有官方 transcript、tariff 落地、备用电调用或大负载项目延期；transformer/switchgear/UPS/CDU 是否出现 lead time/allocation？
5. AI PCB：台系 5 月营收、M8/M9/M10 交期、电子布分产品报价/配额、HVLP4/5 收入和板厂良率/测试是否补 A/B 证据？

## 最近证据源

- Dell Q1 FY27 8-K exhibit: https://www.sec.gov/Archives/edgar/data/1571996/000157199626000021/exhibit991earnings8kq1fy27.htm
- Dell Q1 FY27 transcript: https://investors.delltechnologies.com/static-files/b63ffff9-b729-403b-a231-c6af05667759
- TrendForce memory/Agentic AI: https://www.trendforce.cn/presscenter/news/20260529-13066.html
- Samsung HBM4E samples: https://news.samsung.com/global/samsung-electronics-begins-shipment-of-industry-first-hbm4e-samples
- Marvell Q1 FY27 results: https://investor.marvell.com/news-events/press-releases/detail/1023/marvell-technology-inc-reports-first-quarter-of-fiscal-year-2027-financial-results
- Marvell 10-Q: https://investor.marvell.com/sec-filings/all-sec-filings/content/0001835632-26-000019/mrvl-20260502.htm
- NVIDIA NVLink Fusion: https://nvidianews.nvidia.com/_gallery/download_pdf/682aab363d633270c96f8bae/
- Semtech Q1 FY27 8-K exhibit: https://www.sec.gov/Archives/edgar/data/88941/000008894126000009/smtc-04262026x8k991.htm
- Schneider/TeraWulf/Motivair: https://www.prnewswire.com/news-releases/schneider-electric-progresses-phased-delivery-of-over-290m-in-ai-infrastructure-solutions-including-motivair-technologies-at-terawulfs-google-backed-lake-mariner-campus-302781489.html
- Microchip 3.3kV SiC/SST: https://ir.microchip.com/news-events/press-releases/detail/1390/microchip-launches-3-3-kv-hvd3-msic-power-modules-to-enable-solid-state-transformers-for-ai-data-centers
- Infineon / NVIDIA MGX 800VDC: https://www.prnewswire.com/news-releases/infineon-joins-nvidias-mgx-ai-factory-ecosystem-to-transform-power-delivery-architecture-for-next-generation-ai-server-racks-302785037.html
- DOE large data center oscillations: https://www.energy.gov/oe/articles/monitoring-oscillations-large-data-centers
- OCC data center testimony: https://www.occ.ohio.gov/testimony/committee-meeting/2026-05-27
- Optical module weekly report: `artifacts/weekly_chain_tracking/optical_module/2026-05-31.md`
- AI PCB weekly report: `artifacts/weekly_chain_tracking/ai_pcb/2026-05-31.md`
