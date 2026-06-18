# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-06-18
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-06-14.md`
覆盖窗口：2026-06-08 至 2026-06-14，北京时间
当前阶段：第八期全链雷达，已吸收光模块专项 2026-06-14 状态与 AI PCB 专项 2026-06-14 状态；2026-06-17 补入韩国预拌混凝土运输罢工的 HBM 施工扰动观察；2026-06-18 窄口径补入 Google Brazos 与 KAIST 室温水冷线索，将“存量风冷机房改造”纳入液冷观察层；同日补入 NOR Flash / SLC NAND 涨价与国产小容量存储盈利兑现复核；同日追加 HBM test / probe card / Cube Prober 复核，将其从 future watch 上调为 watch_to_soft 观察。

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

1. `HBM / server DRAM / LPDRAM / NAND / enterprise SSD / AI server parts supply`：维持并强化全链最硬 `hard_bottleneck`。HPE 官方 transcript 把 DRAM/NAND 成本和 supply constraints、AI systems backlog、memory availability 对 2027 转化节奏的影响升为 A 级证据；TrendForce 新增 enterprise SSD supply crunch 与 LPDRAM supply bottleneck。2026-06-17 复核韩国龙仁/平泽预拌混凝土运输罢工：6 月中旬确曾影响三星平泽与 SK 海力士龙仁施工浇筑，但 6 月 15 日协议通过、6 月 16 日起运输恢复，因此只作为 `watch / construction_delay_monitor`，不改变 HBM 主堵点结论，也不能写成 A 股上游材料直接订单利好。预计 `2026H2-2027H1`，慢 ramp 可延至 `2027H2`。
   - 2026-06-18 窄口径复核：NOR Flash / SLC NAND 的涨价和 603986.SH、688110.SH、688766.SH Q1 利润兑现，足以把三家公司从泛化“国产存储观察”上调为 `AI memory hierarchy / reliable small-capacity memory formal_observation`；但该层级仍低于 HBM / LPDRAM / eSSD 主堵点，不进入 `hard_bottleneck` 或主受益候选。核心差异是：NOR/SLC 受益于 HBM/高层 3D NAND 产能优先级挤出、边缘 AI/汽车/工业/高端网络可靠存储需求和小容量成熟制程退出；HBM/LPDRAM/eSSD 则直接约束 AI server、long-context inference、agentic workload 与云厂商 backlog 转收入。
   - 2026-06-18 HBM test / probe card / Cube Prober 复核：SK 海力士 HBM4E 12 层样品提前、Micron 2026 HBM 产能售罄口径、Techwing 获 SK hynix Cube Prober 首单，以及 6871.T transcript 中 memory probe card 高需求、产能扩张和交期压力，足以把该链条从 `future watch` 上调为 `watch_to_soft / soft_bottleneck_candidate`；但仍缺内存厂官方点名“测试/探针卡/Cube Prober 限制 HBM 出货”和 Techwing 合同规模/交期/追加订单，因此暂不列为独立 `hard_bottleneck`。
2. `InP substrate / 6 英寸合格 InP 产能 / EML / CW-DFB / UHP pump / ELS`：吸收光模块专项，维持 `hard_bottleneck`。AXT SEC 文件、TrendForce EML/CW-DFB、Ciena Q2 FY26 与专项状态继续支持。预计 EML/InP `2026H2-2027H1`，CW/ELS/UHP/InP 尾部可到 `2027H2-2028H1`。
3. `高端电子玻纤布 + M7/M8/M9/M10 CCL / prepreg`：吸收 AI PCB 专项，维持 `soft_bottleneck+`。台玻称高端玻纤布缺货预计至 2027 年底，Vexos 指向玻纤布/铜箔/树脂同步挤压 CCL。预计玻纤布 `2026H2-2027年底`，CCL `2026H2-2027H1`；HVLP4/5 继续 `watch`。
4. `数据中心电力 / 并网 / transformer / switchgear / UPS / busway / rack power / CDU / 冷板 / 800VDC`：维持 `soft_bottleneck`，区域并网按 `regional hard operational bottleneck`。Oracle Q4 FY26 的 $638B RPO、AI cloud buildout 融资和 $55.7B FY26 CapEx 强化需求侧；Google Brazos 官方线索足以把“液冷只在新建 AI 数据中心兑现”的表述下调为“存量风冷数据中心逐机架升级到 60kW/机架也开始成立”的观察层，但仍不足以升级为全球液冷设备 hard bottleneck。区域并网预计 `2026H2-2030`；全球设备/液冷/rack power 预计 `6-24 个月`，单品精确交期 `N/A`。
5. `CoWoS / EFB / SoIC / advanced packaging / substrate`：维持 `soft_bottleneck/watch+`；`AI networking switch ASIC / NIC / DPU / retimer / custom XPU` 维持 `strategic_watch/watch_to_soft`。Broadcom、Marvell 与 Oracle 证明需求强，但直接交期/allocation 证据仍不足。

## 专项吸收状态

| 专项任务 | 最新状态文件 | 本期吸收结论 | 对全链排序的影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | InP substrate/6 英寸合格 InP/EML/CW-DFB/UHP pump/ELS 为 hard；整机装配 soft/eased；FAU/主动对准/WLBI/ELSFP thermal 为 future watch | 光源链排当前核心卡点第 2；1.6T/3.2T driver/TIA/DSP/GaN/FAU/热管理列未来迁移 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | 高端电子玻纤布与 M7/M8/M9/M10 CCL/prepreg 并列 soft+；HVLP4/5、板厂良率/测试、设备耗材为 watch | PCB 材料链排当前核心卡点第 3；M9/M10/Q cloth/HVLP/板厂测试列未来迁移 |

## 当前全链堵点账本

| 节点 | 所属赛道 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|---|
| HBM / HBM4E / HBM4 / server DRAM / LPDRAM / NAND / enterprise SSD | Memory/storage | 当前主堵点 | hard_bottleneck | AI server、agentic inference、custom ASIC 和 AI cloud buildout 需求超过 qualified memory/storage/parts 供给；DRAM wafer allocation、HBM stack/test、LPDRAM allocation、NAND/eSSD qualified output、LTA 锁量共同约束 | strengthened | HPE transcript、Oracle Q4/FY26、TrendForce HBM/eSSD/LPDRAM、Samsung/Micron | 2026H2-2027H1；慢 ramp 可至 2027H2；中高置信 | 价格涨幅回落、库存恢复、多供方认证、客户不再提前锁量、ODM 不再提 parts constraint | 跟 HPE 10-Q、Micron/Samsung/SK hynix/Kioxia/SanDisk、Dell/SMCI |
| HBM final/package test / memory probe card / Cube Prober | Memory test & inspection | 当前软堵点候选 | watch_to_soft | HBM4E/HBM4/custom HBM 提高 KGD、stack/final test、探针卡和后切割全检负荷；memory probe card 需求与交期压力开始从海外龙头 transcript 和设备首单显性化 | upgraded_from_future_watch | 6871.T Q1 supplement/forecast revision、6871.T Q4 transcript、ETNews/SK hynix HBM4E、The Elec/Techwing SK hynix Cube Prober、Micron Q2/Goldman | 2026H2-2027H2；中置信；精确交期 N/A | 内存厂未点名测试/探针卡为出货瓶颈、Techwing 合同规模和交期未披露、MJC 称尚未向 SK hynix 大批量交付、二供扩产兑现 | 跟 SK/Samsung/Micron 财报与 Q&A、MJC Q2、Techwing 公告/DART、Advantest/Teradyne/FormFactor/Technoprobe/MPI lead time、精测电子 IR/订单 |
| NOR Flash / SLC NAND / 高可靠小容量存储 | Memory/storage adjacent | 正式观察层 | formal_observation/watch+ | HBM 和高层 3D NAND 抢占产能后，成熟节点 NOR/SLC 供给被挤压；边缘 AI、汽车、工业、高端网络、server boot/buffer 等长生命周期应用拉动可靠存储需求 | upgraded_from_domestic_storage_watch | 2026-06-17/18 邮件线索、TrendForce 2026-06-16、兆易创新/东芯股份/普冉半导体 Q1 报告 | 2026H2；若 LTA/选择性接单强化可延至 2027；中置信 | NOR/SLC 报价回落、低密度产能释放、客户补库结束、三家公司毛利率或净利率回落 | 跟 TrendForce 后续报价、三家公司 H1/H2 财报、产品 ASP/毛利/库存和客户结构 |
| 韩国 HBM fab 土建/cleanroom 施工扰动 / ready-mix concrete logistics | Memory/storage capex execution | 施工扰动观察 | watch | 预拌混凝土交付中断可短期影响土建浇筑、cleanroom 交付和 equipment move-in 节奏；本次为 6 月 8-15 日运输停摆后的短期扰动 | new_then_downgraded_to_watch | 06-16 08:48 邮件线索、Newsis、MBC、BusinessKorea | N/A；目前缺三星/SK 官方工期顺延、设备进场延后或 wafer-start 调整证据；低置信 | 运输恢复、施工赶工完成、公司维持 P4/P5/龙仁 cleanroom/equipment move-in 节奏、材料订单无增量 | 跟 8 个月协议到期风险、三星 P4/P5 与 SK 龙仁 fab 1 工期、cleanroom handover、tool move-in、HBM wafer-start、材料订单/ASP/毛利 |
| AI server BOM / parts supply | Server/ODM | 当前软堵点 | soft_bottleneck+ | memory、CPU/GPU、storage、PCB、power/cooling、trailing-node semis 同步约束 backlog 转收入 | strengthened | HPE transcript、Dell 上期 evidence | 2-4 个季度；memory/CPU/PCB 释放可降级；中置信 | ODM 不再提 parts constraint，backlog/shipments 比例回落，ASP 不再由 DRAM/NAND 成本推升 | 找 10-Q、ODM/SMCI 二次验证 |
| InP substrate / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS | Optical source | 当前主堵点 | hard_bottleneck | 出口许可、InP 衬底集中、6 英寸良率、老化测试、capacity rights、客户认证、ELS 热稳定共同约束可交付供给 | refined/unchanged | 光模块专项、AXT SEC、TrendForce 6/3、Ciena Q2 FY26 | EML/InP 2026H2-2027H1；CW/ELS/UHP 尾部 2027H2-2028H1；中高/中置信 | 许可正常化、6 英寸良率兑现、二供认证、交期/allocation/价格回落 | 交给光模块专项追 AXT/Coherent/Lumentum/Ciena/Corning |
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth | PCB upstream | 当前软堵点 | soft_bottleneck+ | 窑炉、拉丝、电子级纱、织布、后处理、良率、专利、客户 AVL 限制 qualified output | worsened/confirmed | PCB 专项、台玻股东会媒体、TrendForce/Vexos 交叉 | 2026H2-2027年底中高置信；Q cloth/NER 2027H2-2028 watch | 高端布报价回落、交期缩短、库存恢复，多供应商进入核心 AVL | 交给 PCB 专项跟台玻/Nittobo/高端布分产品 |
| M7/M8/M9/M10 CCL / prepreg | AI PCB/CCL | 当前软堵点 | soft_bottleneck+ | 低损耗配方、高端玻纤布、树脂、HVLP 铜箔、新线 qualified output 和客户认证共同约束 | unchanged_to_worsened | PCB 专项、Vexos、台系涨价/营收线索 | 2026H2 中高置信；2027H1 中等偏高 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入 AVL | 跟台系/大陆 CCL 6 月营收、M8/M9/M10 lead time |
| HVLP/VLP/RTF PCB 铜箔 | PCB upstream | 候选卡点 | watch | 低粗糙度一致性、表面处理、添加剂和客户认证约束；HVLP4/5 批量证据不足 | unchanged | PCB 专项：诺德 HVLP1/2/3、HVLP4 测试、HVLP5 开发 | 2026H2-2027 watch；精确持续 N/A | HVLP4/5 多客户批量供货、加工费回落、国产良率确认 | 跟德福/诺德/嘉元/铜冠 |
| 数据中心并网 / grid operations | Power infrastructure | 当前软堵点；区域 hard | soft_bottleneck；regional hard operational | firm power、并网、输配电建设、备用容量、动态负载稳定性、成本分摊规则 | strengthened | Oracle、FERC、JLL、NVIDIA DSX/MGX | 区域 2026H2-2030；中高置信 | reserve margin 改善，容量/电价压力回落，大负载项目延期减少 | 跟 FERC/PJM/ERCOT/utility |
| transformer / switchgear / UPS / busway / rack PDU / CDU / 冷板 | Power/thermal equipment | 当前软堵点观察 | soft_bottleneck/watch | 高功率 rack、新建 AI factory 与存量风冷机房逐机架改造共同拉动液冷系统认证、可靠性、现场集成、交付和服务网络；Brazos 指向液-空侧车/机架歧管路径，KAIST 指向芯片内室温水冷的长期效率方向 | strengthened_to_legacy_retrofit_watch | JLL、NVIDIA DSX/MGX、Oracle CapEx、Google Brazos、KAIST 室温水冷论文/发布 | 6-24 个月；单品精确交期 N/A；中置信。Brazos 为 A 级存量改造可行性线索，KAIST 为技术观察，不等于商业订单 | transformer/switchgear/CDU/PDU 交期正常化，项目不再因设备延期；Brazos/OCP 规格未转供应商量产或存量改造项目；KAIST 技术停留在实验室 | 跟单品 lead time、OCP Brazos 规格、存量机房改造项目、订单纯度和 A 股收入拆分 |
| 800VDC / SST / SiC / GaN power conversion | Rack power / power semis | 未来迁移观察 | watch_to_soft | 高功率 rack 推动 medium-voltage-to-rack、GaN/SiC、hot-swap/protection 和系统认证 | upgraded_watch | NVIDIA DSX/MGX、Infineon/EPC/Microchip/TI 过往路线证据 | 2026H2-2028；精确持续 N/A | 800VDC 推迟，传统架构继续满足；design win 无法转收入 | 跟 design win 转量产 |
| Infineon 部分 GaN 产品在华禁售 | Power semis / GaN IP | 事件催化观察 | event_watch | 中国市场特定 Infineon GaN 产品禁售可能强化国产 GaN/SiC 替代预期，但不证明 AI 电源订单 | new_patch | 2026-06-16 邮箱战报；英诺赛科公告；Infineon/IP 媒体程序和范围反向口径 | 2026H2-2028 观察；持续性 N/A | 主案/禁令范围变化、Infineon 替代产品或和解、国产厂无 design win 转收入 | 跟英诺赛科、三安、斯达的订单/收入/毛利和 NVIDIA MGX/800V design win |
| CoWoS / EFB / SoIC / advanced packaging / substrate | Advanced packaging | 当前软堵点观察 | soft_bottleneck/watch+ | GPU/ASIC multi-die 和 HBM 需求推高 2.5D/3D 封装、基板、键合、测试和设备负荷 | unchanged | Broadcom、NVIDIA、Oracle、TrendForce HBM | 2026H2-2027H1 偏紧，2027 后边际缓解 | TSMC/OSAT 交期恢复，客户不再锁封装产能 | 跟 TSMC/ASE/Amkor/基板/设备 |
| AI networking switch ASIC / NIC / DPU / retimer / custom XPU | AI networking | 战略观察 | strategic_watch/watch_to_soft | 需求强，但缺 silicon allocation、lead time 或出货受限证据 | attention_up | Broadcom Q2 FY26、Marvell Q1 FY27、NVIDIA/Oracle | N/A；出现 allocation 后升级 | 出货顺畅，客户部署不推迟 | 跟 Broadcom/Marvell/NVIDIA/Arista |

## 2026-06-18 HBM test / probe card / Cube Prober 复核

| 对象 | 本次分层 | 证据影响 | 不升级为 hard 或 main 的缺口 |
|---|---|---|---|
| HBM test / memory probe card / Cube Prober | `watch_to_soft / soft_bottleneck_candidate` | SK hynix HBM4E 12 层样品提前、Techwing 获 SK hynix Cube Prober 首单、Micronics Japan memory probe card 创新高/交期压力、Micron/Goldman 供需紧张形成同向证据 | 缺内存厂官方确认测试/探针卡/Cube Prober 限制 HBM 出货；缺 Techwing 合同规模、交期、追加订单；缺多家 probe/ATE/handler 供应商 allocation |
| 雅克科技 002409.SZ | `event_trade_watch` 不上调 | HBM4E 加速支持 HBM 材料大方向，但本次是测试/探针卡链，不证明 UP Chemical 前驱体订单 | 需 UP Chemical/SK hynix 料号、订单、ASP、毛利或收入占比 A/B 证据 |
| 精测电子 300567.SZ | `node_mapping_watch+ / event_trade_watch+`，不进 `main_candidate` | 与 HBM 良率检测/测试设备叙事最贴近，节点关注度上调 | 缺公司公告/IR 披露 HBM test/probe/Cube Prober 同节点产品、客户、订单、收入或毛利；不能用 Techwing/MJC 订单直接映射 |
| 通富微电 002156.SZ | `event_trade_watch` 不上调 | HBM/advanced packaging 景气可作背景，但测试/探针卡/Cube Prober 不等同 OSAT 封测订单 | 需 HBM 相关封装/测试客户、订单、收入、产线或 CPO/NPO 官方证明 |

## 2026-06-18 雅克科技窄口径 HBM 材料证据卡

| 字段 | 当前判断 |
|---|---|
| taxonomy path | `AI 数据中心 / 智算中心 > GPU/ASIC 加速计算链 > HBM / 高带宽近端内存 > HBM DRAM/stack process materials（前驱体/SOD 为材料 P5 线索，不是独立 hard bottleneck）` |
| 需求传导 | AI 训练/推理算力 -> HBM4E/HBM4 与 DRAM fab 产能提升 -> ALD/CVD 前驱体、SOD 等工艺材料用量增加 -> UP Chemical / 江苏先科供货 -> 雅克科技电子材料收入、产品结构和毛利。 |
| A 级可确认 | 2025 年报确认公司半导体前驱体包括 high-k、硅基、金属材料等，应用于 3D NAND、NOR Flash、DRAM 和逻辑芯片先进制程，并开发人工智能先进封装复杂芯片组所需前驱体；2025 年前驱体材料销售收入继续增长、利润水平相应提高，前驱体设计产能 601.92 吨/年、产能利用率 59.31%。2026-05-19 业绩说明会确认 HBM 前驱体一直有供应，高端前驱体因技术壁垒和客户粘性价格稳定，并称在客户 HBM 已有稳定供应产品。2017 年证监会反馈意见可回溯确认 UP Chemical 历史上对 SK Hynix 销售占比较高、SOD 与 SK Hynix 有真实业务关系。 |
| B 级可确认 | SK hynix 2026-06-17/18 披露 12-high HBM4E 样品交付主要客户；The Elec 披露 Techwing 获 SK hynix HBM Cube Prober 首单但未披露合同金额；Goldman 相关报道显示 HBM/DRAM/NAND 供需延续偏紧。这些只证明 HBM 主链景气和测试链加速，不直接证明雅克新增订单。 |
| 邮件线索 | 2026-06-18 08:54《AI产业链战报》把雅克科技写入 HBM4E -> 前驱体/SOD 传导路径，并提示 WF6 线索已被证伪；该邮件含 Grok/Gemini/行情混合输入，只作 C 级触发线索，不作正式证据。 |
| 为什么只停在 `event_trade_watch` | A 级证据能确认产品、客户关系、HBM 前驱体稳定供应和前驱体出货增长，但缺“本轮 HBM4E/HBM4 扩产对应的 UP Chemical/SK hynix 料号、订单金额、ASP 调价、毛利率、收入占比、交付节奏”。B 级 HBM 景气证据是行业需求，不是公司兑现。 |
| 不纳入 WF6 | 公司 2026-06-12 异动公告明确含氟特气主要为 CF4/SF6，目前没有 WF6 相关业务；2025 年含氟特气收入占总体收入 5.79%。雅克的 HBM 材料线只保留前驱体/SOD，不与 WF6 混写。 |
| 分层 | `event_trade_watch / baseline_worthy`。可建最小公司跟踪 baseline，用于保存证据缺口；不升 `main_candidate`，也不改 HBM 主 hard_bottleneck 排序。 |
| 升级触发 | 客户或公司披露 HBM/HBM4E/HBM4 前驱体料号、订单、长协、ASP/价格稳定或涨价、毛利率、收入占比、产能利用率提升且与 HBM 需求绑定；或 SK hynix/Samsung/Micron 官方材料供应链指向 UP Chemical。 |
| 降级触发 | HBM 客户未扩产或认证推迟、公司前驱体出货/利用率/毛利走弱、价格竞争扩散到高端品、公司公告否认相关订单或无应披露事项、市场继续把 WF6 与雅克混同。 |

## 本期深挖方向

- 主深挖 1：`HBM/DRAM/LPDRAM/NAND/eSSD + AI server parts supply`。重点跟踪 HPE 10-Q、TrendForce eSSD/LPDRAM 能否被内存厂官方财报验证、HBM4/HBM4E 认证与 LTA、eSSD/NAND 价格库存、约束是否从 memory 扩散到 CPU、PCB、power/cooling。
- 新增最小公司跟踪：`雅克科技 002409.SZ / UP Chemical / 前驱体 / SOD` 建立 `event_trade_watch` baseline。重点跟踪订单、ASP、毛利、收入占比、客户认证和高端前驱体价格；不得把 HBM4E 样品出货或测试链订单直接写成雅克订单。
- 新增窄口径观察：`NOR Flash / SLC NAND / reliable small-capacity memory` 只作为 AI memory hierarchy 的侧翼观察层。重点跟踪小容量成熟节点供给退出、价格续涨、兆易创新/东芯股份/普冉半导体毛利率和净利率能否在 H1/H2 延续；不得与 HBM/LPDRAM/eSSD 主堵点混写。
- 主深挖 2：`AI cloud capex -> 数据中心电力/并网 + 800VDC/SST/rack power/液冷`。重点把区域 hard operational 约束和全球设备/液冷单品 soft/watch 分开，并把液冷拆成新建 AI factory 与存量风冷机房改造两条观察线；跟踪 Oracle/Meta/Google/Microsoft/Amazon CapEx、FERC/PJM/ERCOT、JLL/CBRE、Google Brazos/OCP 规格、transformer/switchgear/UPS/CDU/PDU lead time、800VDC design win 转收入。

## 未来 6-24 个月卡点迁移

| 节点/赛道 | 当前状态 | 未来状态 | 需求触发 | 供给滞后机制 | 可能时间 | 升级触发阈值 | 证据缺口 | 反转指标 |
|---|---|---|---|---|---|---|---|---|
| HBM4E base die / TSV stack / LPDRAM / eSSD | hard | likely_future_bottleneck | Rubin Ultra、custom ASIC、AI Agent、long-context inference | HBM stack、DRAM wafer allocation、LPDRAM prioritization、enterprise SSD validation | 2026H2-2027H2 | 内存厂披露供不应求、LTA 占满、eSSD 订单延期/涨价 | 供应商财报和客户 allocation | 多供方认证、库存恢复、价格涨幅回落 |
| HBM test / memory probe card / Cube Prober | watch_to_soft | soft_bottleneck_candidate | HBM4E/HBM4/custom HBM、Rubin Ultra 和更高 stack/带宽要求 | KGD/stack/final test 时间增加、探针卡设计切换、Cube Prober 全检导入、客户 qualification | 2026H2-2027H2 | 内存厂或两家以上测试/探针卡/handler 供应商披露 lead time/allocation、客户预付、交期推迟或追加订单 | 官方交期/allocation、合同规模、A 股订单/收入 | MJC/Techwing/ATE 产能兑现、二供认证、HBM qualification 顺畅、测试成本占比下降 |
| NOR Flash / SLC NAND 高可靠小容量存储 | formal_observation/watch+ | side_layer_watch | 边缘 AI、汽车、工业、高端网络和 server boot/buffer 需求叠加成熟节点退出 | 高价值 HBM/高层 3D NAND 挤出成熟节点，小容量产品缺专项扩产，客户转向 LTA/选择性接单 | 2026H2-2027 | H2 价格继续上行、三家公司披露 ASP/毛利率持续改善、长单或选择性接单 | 公司分产品 ASP、客户结构、库存天数和订单可见度 | 低密度 NOR/SLC 产能释放、补库结束、价格和毛利率回落 |
| 韩国 fab 施工物流 / cleanroom handover / tool move-in | watch | construction_delay_monitor | HBM4E/HBM4 扩产需要三星平泽 P4/P5、SK 海力士龙仁等新线按期推进 | 土建浇筑、cleanroom、设备搬入和公用工程必须顺序衔接，劳务/运输扰动可能造成局部工期滑移 | 2026H2-2027H1 | 三星/SK 或承包商披露工期顺延，cleanroom open、tool move-in 或量产 ramp 推迟；罢工/运价争议复燃 | 官方工期、设备进场、wafer-start 和材料订单证据 | 运输正常化、施工赶工、官方维持投产节奏 |
| 1.6T/3.2T optical driver/TIA/DSP/GaN/FAU/test/thermal | watch_to_soft | likely_future_bottleneck | 1.6T/3.2T、CPO/NPO/ELS | 高速 analog、精密耦合、测试节拍、热稳定 | 2026H2-2028 | 多供应商 lead time/allocation、客户预付、良率拖累 | 单品交期/良率 | 扩产兑现、二供认证 |
| M9/M10/Q cloth/NER/HVLP4/5 | soft+/watch | likely_future_bottleneck | Rubin、AI switch、224G+ high-speed board | 新材料认证、AVL、良率和二供慢 | 2026H2-2028 | 官方 allocation、报价上涨、订单延期、客户提前锁料 | 分产品、客户、交期 | 多家供应商稳定量产，报价回落 |
| 800VDC/SST/GaN/SiC + transformer/switchgear/CDU/存量风冷机房液冷改造 | soft/watch | likely_future_bottleneck | 高功率 rack、AI factory 投产，以及 Brazos 类逐机架改造把部分存量风冷机房拉入液冷需求池 | system certification、设备 lead time、现场集成、OCP/客户规格统一、存量机房电力和风道余量 | 2026H2-2028 | design win 转量产、交期拉长、项目因设备延期；Brazos/OCP 规格发布后出现多供应商量产或云厂商存量改造项目 | 单品 allocation、存量改造项目清单、A 股订单/收入拆分 | 800VDC 推迟、传统架构满足、设备交期正常；存量机房因电力/风道限制无法规模部署 |
| AI networking silicon / retimer / substrate | strategic_watch | watch_to_soft | 102.4T switch、NVLink Fusion、custom XPU | SerDes/IP、advanced process、substrate/package | 2026H2-2027 | silicon/substrate/package 被点名限制出货 | 直接交期证据 | 交付顺畅，客户不延期 |

## 三类排名快照

| 类型 | 排名 | 对象 | 理由 | 证据等级 | 风险 |
|---|---:|---|---|---|---|
| 结构重要性 | 1 | HBM / DRAM / LPDRAM / NAND / eSSD | 决定 AI server、agentic inference、storage hierarchy 与 backlog 转收入 | A/B | 2027 供给释放、客户认证变化 |
| 结构重要性 | 2 | CoWoS / EFB / SoIC / advanced packaging / substrate | GPU/ASIC/HBM 组合的核心交付节点 | A/B | 缺官方交期，不能升 hard |
| 结构重要性 | 3 | 数据中心电力 / 并网 / rack power / 液冷 | AI cloud CapEx 从订单转投产，电力和热管理决定可用算力 | A/B | 区域 hard 与全球设备 hard 混同 |
| 结构重要性 | 4 | 高端光源 / InP / EML / CW-DFB / 1.6T 光互连 | scale-out、CPO/ELS 和高密互连核心，供应商集中且客户锁产能 | A/B | 扩产和二供兑现 |
| 结构重要性 | 5 | AI PCB / 高端玻纤布 / CCL / HVLP | 高速材料升级支撑 AI server/switch board，A/台股映射较强 | A/B/C | 高端分产品证据缺口 |
| 基本面质量 | 1 | 全球 memory/HBM/eSSD 供应商 | 需求、价格、客户锁量、产品升级和供给纪律同时具备 | A/B | capex 释放、价格周期反转 |
| 基本面质量 | 2 | Foundry/advanced packaging/substrate 龙头 | 客户黏性、工艺壁垒和资本强度最高 | A/B | 短缺强度可能被需求热度高估 |
| 基本面质量 | 3 | Optical source / InP / CW-DFB 龙头 | 高端光源 hard bottleneck 有产能锁定、集中度和工艺壁垒支持 | A/B | CPO 节奏、二供、扩产 |
| 基本面质量 | 4 | Power/thermal/rack-power 龙头 | AI factory 约束延伸至电力与热管理，订单可见度改善 | A/B | 项目延期、区域差异 |
| 基本面质量 | 5 | High-end CCL / glass cloth 龙头 | 玻纤布和低损耗 CCL 受益明确，但需要分产品和客户认证验证 | A/B/C | 低端/高端混同 |
| 业绩弹性 | 1 | eSSD/NAND/DRAM/HBM 供应商 | 企业 SSD 合约价和收入弹性、DRAM/HBM pricing power、LPDRAM 供给紧张共同出现 | A/B | 2027-2028 capex 释放 |
| 业绩弹性 | 2 | 高端玻纤布 / CCL / prepreg | 涨价、交期、材料代际升级和 AVL 认证共同驱动 | B | 高端收入占比和正式报价 |
| 业绩弹性 | 3 | 光源/InP/CW-DFB/1.6T 光互连组件 | 当前 hard + 1.6T/3.2T/CPO 迁移 | A/B | 单品拆分和二供证据不足 |
| 业绩弹性 | 4 | Power/thermal/rack power/800VDC | backlog 转收入、AI datacenter project、液冷 attach rate、power semis design win | A/B | 项目延期，单品交期不清 |
| 业绩弹性 | 5 | Custom ASIC/networking silicon/advanced packaging | 需求强，但多为大市值和客户集中，且 A 股映射弱 | A/B | 交期证据不足，预期高 |
| 交易弹性 | 1 | A/台股 PCB 上游材料组 | 本周证据增量最大，低基期和小中市值标的较多；行情 N/A | A/B/C | 高端收入占比和交易拥挤 |
| 交易弹性 | 2 | A 股光模块/光器件/CPO 组 | 光源 hard 与 1.6T/ELS/FAU/主动对准迁移催化密集；行情 N/A | A/B/C | 估值拥挤、年降 |
| 交易弹性 | 3 | A 股电力/液冷/800VDC 组 | Oracle CapEx + FERC/JLL + Google Brazos 形成预期差，存量改造观察层开始成立；A 股映射多但纯度分化，英维克/飞荣达等需分别验证 CDU/机架液冷系统、冷板/热管理部件、客户项目、收入占比与毛利，而不能按“Google/Brazos 受益”直接推断；行情 N/A | A/B | 订单纯度不足、客户认证和收入拆分不足、主题拥挤 |
| 交易弹性 | 4 | 美/台 networking silicon 与 custom ASIC 组 | Broadcom/Marvell/NVIDIA 需求强，但多为大市值且非当前 hard | A | 预期定价充分 |
| 交易弹性 | 5 | 美/韩 memory/packaging leaders | 基本面和业绩弹性强，但市值大、全球定价，短线弹性相对低；行情 N/A | A/B | 供应周期与估值 |

## 下期默认跟踪问题

1. HPE 是否发布 Q2 FY26 10-Q，能否进一步拆分 AI Systems backlog、DRAM/NAND/LTA、purchase commitments、inventory 和 working capital？
2. TrendForce eSSD/LPDRAM 线索能否被 Micron/Samsung/SK hynix/Kioxia/SanDisk 的最新财报、客户 LTA、库存和价格数据确认？
3. NOR Flash / SLC NAND 线索能否在 2026H1/H2 财报中继续体现为兆易创新、东芯股份、普冉半导体的 ASP、毛利率、净利率和现金流改善；若只剩补库或低密度产能释放，则从正式观察层降回 `theme_adjacent/watch`。
4. HBM test/probe card/Cube Prober 是否出现内存厂官方点名的测试瓶颈、Techwing 追加订单/合同规模、MJC/Advantest/Teradyne/FormFactor/Technoprobe/MPI lead time，或精测电子订单/收入拆分？
5. Oracle、Meta、Google、Microsoft、Amazon 的 AI datacenter CapEx 是否继续上修，是否披露电力、设备、液冷或 GPU/customer-supplied hardware 对投产节奏的影响？
6. Broadcom/Marvell/Arista/NVIDIA 是否出现 networking silicon、switch ASIC、retimer、substrate、advanced packaging 的 allocation、交期或客户排产延期证据？
7. 专项吸收：光模块继续跟 AXT/Coherent/Lumentum/Ciena 的 InP/EML/CW-DFB/ELS 单品证据；PCB 继续跟台玻/Nittobo/台系 CCL/HVLP4/5/板厂良率和测试。
8. 韩国预拌混凝土运输扰动是否复燃，是否出现三星平泽 P4/P5、SK 海力士龙仁 fab 1 的官方工期顺延、cleanroom handover、tool move-in、wafer-start 或材料订单/ASP/毛利变化；未出现这些指标前，只保留 `watch`，不得写成雅克科技/有研新材直接订单利好。
9. Google Brazos 是否在 OCP 正式发布规格并出现多供应商量产、现有风冷机房改造项目、60kW/机架部署案例或订单证据；英维克、飞荣达等 A 股公司未披露客户/项目/收入拆分前，只能列为液冷存量改造观察，不得写成 Google 供应链确认。

## 最近证据源

- HPE Q2 FY26 transcript: https://investors.hpe.com/~/media/Files/H/HP-Enterprise-IR/documents/q2-2026/q2-2026-transcript.pdf
- Oracle Q4/FY26 results: https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/default.aspx
- TrendForce HBM/DRAM pricing: https://www.trendforce.com/presscenter/news/20260602-13074.html
- TrendForce enterprise SSD supply crunch: https://www.trendforce.com/presscenter/news/20260611-13092.html
- TrendForce LPDRAM report page: https://www.trendforce.com/research/download/RP260605RY
- SK hynix HBM4E 12-layer sample / ETNews: https://www.etnews.com/20260618000019
- HBM4E race and sample pull-in context / BusinessKorea: https://www.businesskorea.co.kr/news/articleView.html?idxno=271503
- Techwing SK hynix Cube Prober first order / The Elec: https://www.thelec.net/news/articleView.html?idxno=11441
- Micron Q2 FY26 prepared remarks: https://investors.micron.com/static-files/e089f8c0-065d-47b8-9d02-bfa863cdb357
- Micron HBM4 for NVIDIA Vera Rubin press release: https://investors.micron.com/news-releases/news-release-details/micron-high-volume-production-hbm4-designed-nvidia-vera-rubin
- Goldman memory shortage summary / Benzinga: https://www.benzinga.com/markets/tech/26/06/52907425/goldman-memory-shortage-2028-samsung-hynix-kioxia-sandisk-micron
- Micron Q&A HBM 2026 sold-out transcript highlight / MLQ: https://mlq.ai/earnings/highlight/MU-hbm4-for-2026-sold-out-pricing-and-volu-f4a898/
- Micronics Japan 6871.T Q1 materials / Q4 transcript: `artifacts/earnings/6871.T/2026_Q1/`
- TrendForce NOR Flash / SLC NAND 2H26 price outlook: https://www.trendforce.com/presscenter/news/20260616-13102.html
- 兆易创新 2026 年第一季度报告: https://static.cninfo.com.cn/finalpage/2026-04-30/1225257883.PDF
- 东芯股份 2026 年第一季度报告: https://file.finance.sina.com.cn/211.154.219.97%3A9494/MRGG/CNSESH_STOCK/2026/2026-4/2026-04-30/12273988.PDF
- 普冉半导体 2026 年第一季度报告: https://file.finance.sina.com.cn/211.154.219.97%3A9494/MRGG/CNSESH_STOCK/2026/2026-4/2026-04-29/12263897.PDF
- Broadcom Q2 FY26 results: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-second-quarter-fiscal-year-2026-financial
- Marvell Q1 FY27 results: https://investor.marvell.com/news-events/press-releases/detail/1023/marvell-technology-inc-reports-first-quarter-of-fiscal-year-2027-financial-results
- Marvell Q1 FY27 10-Q: https://investor.marvell.com/sec-filings/all-sec-filings/content/0001835632-26-000019/mrvl-20260502.htm
- TrendForce EML/CW-DFB: https://www.trendforce.com/presscenter/news/20260603-13077.html
- Ciena Q2 FY26 SEC exhibit: https://www.sec.gov/Archives/edgar/data/936395/000162828026040614/ex9912026q2earningspressre.htm
- AXT 10-Q / SEC source for InP export permit risk: https://www.sec.gov/Archives/edgar/data/1051627/000155837025007751/axti-20250331x10q.htm
- 台玻/高端玻纤布报道: https://www.peoplenews.tw/articles/economic-news/37718
- Vexos PCB/CCL constraints: https://cms.vexos.com/blog/how-oems-can-navigate-ai-driven-pcb-ccl-supply-constraints/
- FERC large-load docket: https://www.ferc.gov/news-events/news/ferc-act-large-load-interconnection-docket-june-2026
- JLL 2026 data center outlook: https://www.jll.com/en-us/insights/market-outlook/data-center-outlook
- Google Brazos liquid cooling system for air-cooled data centers: https://cloud.google.com/blog/topics/systems/brazos-liquid-cooling-system-for-air-cooled-data-centers
- KAIST room-temperature water liquid cooling release: https://www.eurekalert.org/news-releases/1132133
- Optical module weekly report/state: `artifacts/weekly_chain_tracking/optical_module/2026-06-14.md`
- AI PCB weekly report/state: `artifacts/weekly_chain_tracking/ai_pcb/2026-06-14.md`
- Korean ready-mix strike disruption: https://www.newsis.com/view/NISX20260612_0003666673
- Korean ready-mix strike withdrawal / transport normalization: https://www.newsis.com/view/NISX20260615_0003670038
- Ready-mix strike ends after union ratifies deal: https://www.businesskorea.co.kr/news/articleView.html?idxno=271329
