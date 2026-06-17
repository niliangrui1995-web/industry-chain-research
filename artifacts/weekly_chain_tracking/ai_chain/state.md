# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-06-17
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-06-14.md`
覆盖窗口：2026-06-08 至 2026-06-14，北京时间
当前阶段：第八期全链雷达，已吸收光模块专项 2026-06-14 状态与 AI PCB 专项 2026-06-14 状态；2026-06-17 补入韩国预拌混凝土运输罢工的 HBM 施工扰动观察。

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
2. `InP substrate / 6 英寸合格 InP 产能 / EML / CW-DFB / UHP pump / ELS`：吸收光模块专项，维持 `hard_bottleneck`。AXT SEC 文件、TrendForce EML/CW-DFB、Ciena Q2 FY26 与专项状态继续支持。预计 EML/InP `2026H2-2027H1`，CW/ELS/UHP/InP 尾部可到 `2027H2-2028H1`。
3. `高端电子玻纤布 + M7/M8/M9/M10 CCL / prepreg`：吸收 AI PCB 专项，维持 `soft_bottleneck+`。台玻称高端玻纤布缺货预计至 2027 年底，Vexos 指向玻纤布/铜箔/树脂同步挤压 CCL。预计玻纤布 `2026H2-2027年底`，CCL `2026H2-2027H1`；HVLP4/5 继续 `watch`。
4. `数据中心电力 / 并网 / transformer / switchgear / UPS / busway / rack power / CDU / 冷板 / 800VDC`：维持 `soft_bottleneck`，区域并网按 `regional hard operational bottleneck`。Oracle Q4 FY26 的 $638B RPO、AI cloud buildout 融资和 $55.7B FY26 CapEx 强化需求侧。区域并网预计 `2026H2-2030`；全球设备/液冷/rack power 预计 `6-24 个月`，单品精确交期 `N/A`。
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
| 韩国 HBM fab 土建/cleanroom 施工扰动 / ready-mix concrete logistics | Memory/storage capex execution | 施工扰动观察 | watch | 预拌混凝土交付中断可短期影响土建浇筑、cleanroom 交付和 equipment move-in 节奏；本次为 6 月 8-15 日运输停摆后的短期扰动 | new_then_downgraded_to_watch | 06-16 08:48 邮件线索、Newsis、MBC、BusinessKorea | N/A；目前缺三星/SK 官方工期顺延、设备进场延后或 wafer-start 调整证据；低置信 | 运输恢复、施工赶工完成、公司维持 P4/P5/龙仁 cleanroom/equipment move-in 节奏、材料订单无增量 | 跟 8 个月协议到期风险、三星 P4/P5 与 SK 龙仁 fab 1 工期、cleanroom handover、tool move-in、HBM wafer-start、材料订单/ASP/毛利 |
| AI server BOM / parts supply | Server/ODM | 当前软堵点 | soft_bottleneck+ | memory、CPU/GPU、storage、PCB、power/cooling、trailing-node semis 同步约束 backlog 转收入 | strengthened | HPE transcript、Dell 上期 evidence | 2-4 个季度；memory/CPU/PCB 释放可降级；中置信 | ODM 不再提 parts constraint，backlog/shipments 比例回落，ASP 不再由 DRAM/NAND 成本推升 | 找 10-Q、ODM/SMCI 二次验证 |
| InP substrate / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS | Optical source | 当前主堵点 | hard_bottleneck | 出口许可、InP 衬底集中、6 英寸良率、老化测试、capacity rights、客户认证、ELS 热稳定共同约束可交付供给 | refined/unchanged | 光模块专项、AXT SEC、TrendForce 6/3、Ciena Q2 FY26 | EML/InP 2026H2-2027H1；CW/ELS/UHP 尾部 2027H2-2028H1；中高/中置信 | 许可正常化、6 英寸良率兑现、二供认证、交期/allocation/价格回落 | 交给光模块专项追 AXT/Coherent/Lumentum/Ciena/Corning |
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth | PCB upstream | 当前软堵点 | soft_bottleneck+ | 窑炉、拉丝、电子级纱、织布、后处理、良率、专利、客户 AVL 限制 qualified output | worsened/confirmed | PCB 专项、台玻股东会媒体、TrendForce/Vexos 交叉 | 2026H2-2027年底中高置信；Q cloth/NER 2027H2-2028 watch | 高端布报价回落、交期缩短、库存恢复，多供应商进入核心 AVL | 交给 PCB 专项跟台玻/Nittobo/高端布分产品 |
| M7/M8/M9/M10 CCL / prepreg | AI PCB/CCL | 当前软堵点 | soft_bottleneck+ | 低损耗配方、高端玻纤布、树脂、HVLP 铜箔、新线 qualified output 和客户认证共同约束 | unchanged_to_worsened | PCB 专项、Vexos、台系涨价/营收线索 | 2026H2 中高置信；2027H1 中等偏高 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入 AVL | 跟台系/大陆 CCL 6 月营收、M8/M9/M10 lead time |
| HVLP/VLP/RTF PCB 铜箔 | PCB upstream | 候选卡点 | watch | 低粗糙度一致性、表面处理、添加剂和客户认证约束；HVLP4/5 批量证据不足 | unchanged | PCB 专项：诺德 HVLP1/2/3、HVLP4 测试、HVLP5 开发 | 2026H2-2027 watch；精确持续 N/A | HVLP4/5 多客户批量供货、加工费回落、国产良率确认 | 跟德福/诺德/嘉元/铜冠 |
| 数据中心并网 / grid operations | Power infrastructure | 当前软堵点；区域 hard | soft_bottleneck；regional hard operational | firm power、并网、输配电建设、备用容量、动态负载稳定性、成本分摊规则 | strengthened | Oracle、FERC、JLL、NVIDIA DSX/MGX | 区域 2026H2-2030；中高置信 | reserve margin 改善，容量/电价压力回落，大负载项目延期减少 | 跟 FERC/PJM/ERCOT/utility |
| transformer / switchgear / UPS / busway / rack PDU / CDU / 冷板 | Power/thermal equipment | 当前软堵点观察 | soft_bottleneck/watch | 高功率 rack 与液冷系统认证、可靠性、现场集成、交付和服务网络 | strengthened | JLL、NVIDIA DSX/MGX、Oracle CapEx | 6-24 个月；单品精确交期 N/A；中置信 | transformer/switchgear/CDU/PDU 交期正常化，项目不再因设备延期 | 跟单品 lead time 和订单纯度 |
| 800VDC / SST / SiC / GaN power conversion | Rack power / power semis | 未来迁移观察 | watch_to_soft | 高功率 rack 推动 medium-voltage-to-rack、GaN/SiC、hot-swap/protection 和系统认证 | upgraded_watch | NVIDIA DSX/MGX、Infineon/EPC/Microchip/TI 过往路线证据 | 2026H2-2028；精确持续 N/A | 800VDC 推迟，传统架构继续满足；design win 无法转收入 | 跟 design win 转量产 |
| Infineon 部分 GaN 产品在华禁售 | Power semis / GaN IP | 事件催化观察 | event_watch | 中国市场特定 Infineon GaN 产品禁售可能强化国产 GaN/SiC 替代预期，但不证明 AI 电源订单 | new_patch | 2026-06-16 邮箱战报；英诺赛科公告；Infineon/IP 媒体程序和范围反向口径 | 2026H2-2028 观察；持续性 N/A | 主案/禁令范围变化、Infineon 替代产品或和解、国产厂无 design win 转收入 | 跟英诺赛科、三安、斯达的订单/收入/毛利和 NVIDIA MGX/800V design win |
| CoWoS / EFB / SoIC / advanced packaging / substrate | Advanced packaging | 当前软堵点观察 | soft_bottleneck/watch+ | GPU/ASIC multi-die 和 HBM 需求推高 2.5D/3D 封装、基板、键合、测试和设备负荷 | unchanged | Broadcom、NVIDIA、Oracle、TrendForce HBM | 2026H2-2027H1 偏紧，2027 后边际缓解 | TSMC/OSAT 交期恢复，客户不再锁封装产能 | 跟 TSMC/ASE/Amkor/基板/设备 |
| AI networking switch ASIC / NIC / DPU / retimer / custom XPU | AI networking | 战略观察 | strategic_watch/watch_to_soft | 需求强，但缺 silicon allocation、lead time 或出货受限证据 | attention_up | Broadcom Q2 FY26、Marvell Q1 FY27、NVIDIA/Oracle | N/A；出现 allocation 后升级 | 出货顺畅，客户部署不推迟 | 跟 Broadcom/Marvell/NVIDIA/Arista |

## 本期深挖方向

- 主深挖 1：`HBM/DRAM/LPDRAM/NAND/eSSD + AI server parts supply`。重点跟踪 HPE 10-Q、TrendForce eSSD/LPDRAM 能否被内存厂官方财报验证、HBM4/HBM4E 认证与 LTA、eSSD/NAND 价格库存、约束是否从 memory 扩散到 CPU、PCB、power/cooling。
- 主深挖 2：`AI cloud capex -> 数据中心电力/并网 + 800VDC/SST/rack power/液冷`。重点把区域 hard operational 约束和全球设备/液冷单品 soft/watch 分开，跟踪 Oracle/Meta/Google/Microsoft/Amazon CapEx、FERC/PJM/ERCOT、JLL/CBRE、transformer/switchgear/UPS/CDU/PDU lead time、800VDC design win 转收入。

## 未来 6-24 个月卡点迁移

| 节点/赛道 | 当前状态 | 未来状态 | 需求触发 | 供给滞后机制 | 可能时间 | 升级触发阈值 | 证据缺口 | 反转指标 |
|---|---|---|---|---|---|---|---|---|
| HBM4E base die / HBM test / TSV stack / LPDRAM / eSSD | hard | likely_future_bottleneck | Rubin Ultra、custom ASIC、AI Agent、long-context inference | HBM stack/test、DRAM wafer allocation、LPDRAM prioritization、enterprise SSD validation | 2026H2-2027H2 | 内存厂披露供不应求、LTA 占满、eSSD 订单延期/涨价 | 供应商财报和客户 allocation | 多供方认证、库存恢复、价格涨幅回落 |
| 韩国 fab 施工物流 / cleanroom handover / tool move-in | watch | construction_delay_monitor | HBM4E/HBM4 扩产需要三星平泽 P4/P5、SK 海力士龙仁等新线按期推进 | 土建浇筑、cleanroom、设备搬入和公用工程必须顺序衔接，劳务/运输扰动可能造成局部工期滑移 | 2026H2-2027H1 | 三星/SK 或承包商披露工期顺延，cleanroom open、tool move-in 或量产 ramp 推迟；罢工/运价争议复燃 | 官方工期、设备进场、wafer-start 和材料订单证据 | 运输正常化、施工赶工、官方维持投产节奏 |
| 1.6T/3.2T optical driver/TIA/DSP/GaN/FAU/test/thermal | watch_to_soft | likely_future_bottleneck | 1.6T/3.2T、CPO/NPO/ELS | 高速 analog、精密耦合、测试节拍、热稳定 | 2026H2-2028 | 多供应商 lead time/allocation、客户预付、良率拖累 | 单品交期/良率 | 扩产兑现、二供认证 |
| M9/M10/Q cloth/NER/HVLP4/5 | soft+/watch | likely_future_bottleneck | Rubin、AI switch、224G+ high-speed board | 新材料认证、AVL、良率和二供慢 | 2026H2-2028 | 官方 allocation、报价上涨、订单延期、客户提前锁料 | 分产品、客户、交期 | 多家供应商稳定量产，报价回落 |
| 800VDC/SST/GaN/SiC + transformer/switchgear/CDU | soft/watch | likely_future_bottleneck | 高功率 rack 与 AI factory 投产 | system certification、设备 lead time、现场集成 | 2026H2-2028 | design win 转量产、交期拉长、项目因设备延期 | 单品 allocation | 800VDC 推迟、传统架构满足、设备交期正常 |
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
| 交易弹性 | 3 | A 股电力/液冷/800VDC 组 | Oracle CapEx + FERC/JLL 形成预期差，A 股映射多但纯度分化；行情 N/A | A/B | 订单纯度不足 |
| 交易弹性 | 4 | 美/台 networking silicon 与 custom ASIC 组 | Broadcom/Marvell/NVIDIA 需求强，但多为大市值且非当前 hard | A | 预期定价充分 |
| 交易弹性 | 5 | 美/韩 memory/packaging leaders | 基本面和业绩弹性强，但市值大、全球定价，短线弹性相对低；行情 N/A | A/B | 供应周期与估值 |

## 下期默认跟踪问题

1. HPE 是否发布 Q2 FY26 10-Q，能否进一步拆分 AI Systems backlog、DRAM/NAND/LTA、purchase commitments、inventory 和 working capital？
2. TrendForce eSSD/LPDRAM 线索能否被 Micron/Samsung/SK hynix/Kioxia/SanDisk 的最新财报、客户 LTA、库存和价格数据确认？
3. Oracle、Meta、Google、Microsoft、Amazon 的 AI datacenter CapEx 是否继续上修，是否披露电力、设备、液冷或 GPU/customer-supplied hardware 对投产节奏的影响？
4. Broadcom/Marvell/Arista/NVIDIA 是否出现 networking silicon、switch ASIC、retimer、substrate、advanced packaging 的 allocation、交期或客户排产延期证据？
5. 专项吸收：光模块继续跟 AXT/Coherent/Lumentum/Ciena 的 InP/EML/CW-DFB/ELS 单品证据；PCB 继续跟台玻/Nittobo/台系 CCL/HVLP4/5/板厂良率和测试。
6. 韩国预拌混凝土运输扰动是否复燃，是否出现三星平泽 P4/P5、SK 海力士龙仁 fab 1 的官方工期顺延、cleanroom handover、tool move-in、wafer-start 或材料订单/ASP/毛利变化；未出现这些指标前，只保留 `watch`，不得写成雅克科技/有研新材直接订单利好。

## 最近证据源

- HPE Q2 FY26 transcript: https://investors.hpe.com/~/media/Files/H/HP-Enterprise-IR/documents/q2-2026/q2-2026-transcript.pdf
- Oracle Q4/FY26 results: https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/default.aspx
- TrendForce HBM/DRAM pricing: https://www.trendforce.com/presscenter/news/20260602-13074.html
- TrendForce enterprise SSD supply crunch: https://www.trendforce.com/presscenter/news/20260611-13092.html
- TrendForce LPDRAM report page: https://www.trendforce.com/research/download/RP260605RY
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
- Optical module weekly report/state: `artifacts/weekly_chain_tracking/optical_module/2026-06-14.md`
- AI PCB weekly report/state: `artifacts/weekly_chain_tracking/ai_pcb/2026-06-14.md`
- Korean ready-mix strike disruption: https://www.newsis.com/view/NISX20260612_0003666673
- Korean ready-mix strike withdrawal / transport normalization: https://www.newsis.com/view/NISX20260615_0003670038
- Ready-mix strike ends after union ratifies deal: https://www.businesskorea.co.kr/news/articleView.html?idxno=271329
