# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-06-22
最新报告：`artifacts/weekly_chain_tracking/optical_module/2026-06-21.md`
覆盖窗口：2026-06-17 至 2026-06-22（06-22 为邮件线索窄口径复核）

## 任务边界

本任务只跟踪光模块及其上游/中游关键环节。PCB/CCL、数据中心电力、机柜级液冷、CDU、冷板总成、光纤预制棒和普通通信用光缆只作为接口或外部变量；只有出现 A/B 级证据证明其直接限制光模块或光引擎交付、良率、客户认证或可靠性时，才纳入观察或深挖。

研究宇宙：

- 光模块整机：400G / 800G / 1.6T / 3.2T。
- 光引擎 / TOSA / ROSA / CPO / OCS / ELS。
- EML / DML / CW Laser / CW-DFB LD / InP / GaAs / 硅光 / 薄膜铌酸锂。
- DSP / driver / TIA / CDR。
- FAU / MT ferrule / AWG / 透镜 / 微透镜阵列 / 耦合透镜 / isolator / Faraday rotator / connector。
- 数据中心光纤 / 跳线 / 光纤阵列 / PM fiber / MCF / 空芯光纤：仅限 AI 数据中心、CPO/ELS、光引擎或高密度光连接的明确传导。
- 光模块/光引擎热管理与液冷兼容：IHS、cage、riding heatsink、TIM、cold plate interface、浸没兼容、ELSFP thermal stability、热可靠性和返修。
- 封装耦合、主动对准、WLBI/OWAT、光电联合测试、测试设备、代工和模块装配。

## 执行补充要求

- 每次更新报告时，必须对当前 `hard_bottleneck` 和 `soft_bottleneck` 预估可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A`，并说明缺哪类证据。
- 每次必须扫描未进入本期主深挖的其他产业链环节，判断未来 6-24 个月最可能出现新卡点或卡点迁移的环节，并写明需求触发、供给滞后机制、可能时间、升级触发阈值、证据缺口和反转指标。
- 对话窗口摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`。
- 子代理输出只能作为信息采集，主代理必须负责最终证据分级、交叉验证、堵点判断、排名和报告合成。

## 当前主结论

- 当前主硬堵点仍为 `InP 衬底 / 外延片 / 6 英寸合格 InP 平台 / EML / CW-DFB / UHP pump / ELS`。堵点定义是短期需求超过合格供给、可用产能、良率、老化测试和客户认证能力；高壁垒、高毛利或高热度本身不构成堵点。
- 2026-06-21 本轮增量主要是供给侧集中扩产和锁供：Coherent 与美国商务部 CHIPS LOI、JX Advanced Metals 上调 InP 衬底扩产、IQE/Tower 多年 InP 外延片供应协议、Nokia 光子芯片先进测试封装扩产。结论是：主堵点仍硬，但缓解路径更可见。
- EML/InP 偏紧预计持续至 `2026H2-2027H1`，置信度中高；CW-DFB/UHP/ELS 若随 2027-2028 CPO/NPO/scale-up 光互连放量，尾部可能延至 `2027H2-2028H1`，置信度中；长期 InP 衬底若 JX/Coherent/Lumentum/非中国供给扩产并通过客户认证，`2028-2030` 起缓解概率上升。
- 光模块整机装配与关键原材料同步维持 `soft_bottleneck/eased`，预计 `2026Q2-Q3` 继续缓解。本窗口 CNINFO 未发现核心 A 股重新披露整机交付受限、关键料短缺、客户认证失败或订单延期。
- 罗博特科/ficonTEC 与 NVIDIA 合作从官网线索升级为 CNINFO A 级公告确认，但同一公告明确相关业务早期、暂无在手订单和销售收入，因此 `主动对准 / CPO 制造测试设备` 只升级为未来迁移观察核心，不能升级为当前 hard_bottleneck。
- 东山精密/索尔思 12 亿美元光芯片和光模块扩建强化 A 股垂直一体化映射，但项目审批、客户、订单、单独毛利、良率和产能爬坡仍缺量化；不改变 InP/EML 当前主硬堵点。
- 数据中心 optical fiber / cable / connectivity 因 Amazon-Corning 与 NVIDIA-Corning 官方合作维持边界内 `soft_bottleneck/watch`；目前仍不能外推为 FAU/MT ferrule/PM fiber/fiber array 当前短缺。
- 2026-06-22 邮件《AI产业链战报》新增的光模块散单涨价、新易盛 2027 年 DSP 5100 万颗/Broadcom 主供、中际旭创 4-5 月出口可能破 80 亿、MPO/FAU 保底扩产均先归入 `mixed-source/C-lead`。新易盛 CNINFO 2026-06-01 投关和 Broadcom 官方 DSP 路线只支持需求、锁料和技术路线，不足以把模块涨价、DSP、FAU/MPO 供给升级为 A/B 级硬结论。

## 本期主深挖与次级跟踪

- 主深挖：InP 衬底 / 外延片 / 6 英寸合格 InP 平台及其对 EML、CW-DFB、UHP pump、ELS 的约束。
- 次级跟踪 1：CPO/NPO 光引擎制造、主动对准、WLBI/OWAT、光电联合测试和先进封装测试。
- 次级跟踪 2：数据中心高密度 optical fiber / cable / connectivity 与 FAU/fiber array/MT ferrule 的边界内传导。
- 次级跟踪 3：光模块整机装配和 A 股核心公司披露窗口。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| AXT、Coherent、Lumentum 是否披露 InP 出口许可、6 英寸 InP 良率、客户认证、库存和毛利变化？ | Coherent/JX/IQE/Tower 给出强扩产和锁供证据；Lumentum 仅有 Q3 FY26 官方材料和 Mizuho replay 入口，未见 6/9 后 SEC 业务披露或许可细节；AXT 未见新增官方许可细节。 | 缓解路径强化；主堵点未解除 |
| Lumentum 是否发布 Mizuho 2026-06-09 官网 transcript/replay 或后续 10-Q？ | 2026-06-22 复核：Lumentum IR archive 已列 Mizuho webcast link（KnowledgeVision registration/replay），但无 Lumentum 官网逐字稿、PDF/附件或 6/9 后 10-Q/8-K 业务更新；Q3 FY26 官网材料只支持 EML/CW/UHP ramp，不支持交期/allocation/锁产能。 | open_loop 收敛：replay 存在但不升 A；交期/锁产能仍限 B/C |
| Ciena 是否把 supply not keeping pace 拆成 pump、modem、coherent module、line system 或 pluggable 单品？ | 本窗口无新增单品拆分。Ciena broad optical tightness 仍是系统级 read-through。 | broad 确认，细分待跟踪 |
| 新易盛、天孚、中际、源杰等 A 股公司是否披露物料、客户、预付款、存货、毛利和交付？ | CNINFO 6 月 17-21 日：中际、新易盛、天孚、源杰、长光华芯、光库、太辰光、长飞无新增相关公告；东山和罗博特科新增公告。 | 多数仍待跟踪；东山/罗博特科已补证 |
| FAU/fiber array、MT ferrule、PM fiber、ELSFP thermal、主动对准/WLBI/测试设备是否出现交期、涨价、订单排队、良率或返修证据？ | ficonTEC/NVIDIA 与 Nokia 先进测试封装强化 future watch；罗博特科公告明确无订单/收入，未见交期/涨价/良率瓶颈。 | 未来观察增强，未升级当前堵点 |
| NVIDIA 是否发布可核验的 CFO/SVP transcript、CPO product update 或 customer deployment 信息？ | 未找到 CFO 原文；NVIDIA 官方产品页仍支持 2026 photonics 路线，ficonTEC 合作强化路线推进。 | 路线增强，CFO 表述仍 N/A |
| 大立光 FA 自动化试产线是否如期建成并转客户定点？ | 本窗口未见新 A/B 证据。 | 仍待跟踪 |
| 天孚 CPO 光引擎市占、订单期限、FAU/ELS 产能和个别物料缺口是否被证实？ | 本窗口未见公司公告或投关拆分；市占 >60%、订单至 2028 仍不入事实层。 | 仍待跟踪 |
| 罗博特科 ficonTEC 是否出现新的 CPO-specific 设备订单、NVIDIA/客户采购路径、交期排队、产能瓶颈或验收收入证据？ | CNINFO 确认合作开发，但同时确认暂无相关在手订单和销售收入。 | 合作证实；商业化证伪/降级 |
| 新易盛 Q2 起供应链缓解是否在 Q2/Q3 财报中兑现？ | 本窗口未到 Q2 财报，未见新增财务兑现。 | 仍待跟踪 |
| 2026-06-22 邮件提到的新易盛 2027 年 DSP 5100 万颗/Broadcom 主供、中际 4-5 月出口可能破 80 亿、光模块散单涨价和 MPO/FAU 扩产，是否能升级？ | 邮件原文属于 Grok 未经审计的 mixed-source 线索；新易盛 2026-06-01 CNINFO 投关仅支持锁料、预付、1.6T 订单增幅和供应链整体稳定；Broadcom 官方仅支持 200G/lane DSP 路线和 Eoptolink/Innolight 技术生态合作；海关/南京海关入口存在但本轮直连 504，未闭合到中际/江苏细项。 | 收紧为 C/lead；不升 A/B 硬证据 |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| InP substrate / epiwafer / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS | 当前主堵点 | hard_bottleneck | 衬底/外延/6 英寸良率、老化测试、客户认证、出口许可、锁产能共同约束高端光源可交付供给 | unchanged/refined/easing_path_clearer | Coherent CHIPS LOI；JX 7-10x 产能计划；IQE/Tower 多年外延片协议；Lumentum Q3 FY26 deck/10-Q（支持 ramp/Greensboro，不支持交期锁产能）；AXT/TrendForce/Reuters 既有偏紧证据 | EML/InP：2026H2-2027H1；CW/ELS/UHP 尾部：2027H2-2028H1；长期缓解看 2028-2030；置信度中高/中 | 许可正常化、6 英寸良率/认证兑现、交期/allocation/价格回落、客户停止锁产能 | 跟 Coherent/JX/IQE/Lumentum/AXT 产能、良率、认证、许可和客户锁产能 |
| 光模块整机装配与关键原材料同步 | 当前软堵点 | soft_bottleneck | 模块产线需光芯片、电芯片、无源件、PCB、测试资源和客户认证同步；上游主堵点仍可传导 | eased/unchanged；06-22 涨价/出口 mixed-source 线索待核 | 新易盛既有 Q2 供应链缓解；新易盛 2026-06-01 CNINFO 投关支持锁料/预付保障 2027/2028 物料、1.6T 订单大增和供应链整体稳定；CNINFO 6/17-21 核心公司无新增整机短缺公告；无散单涨价/ASP 硬证据 | 2026Q2-Q3 继续缓解；置信度中 | Q2/Q3 交付兑现、毛利和存货周转改善；若模块厂重提关键料/测试短缺或 ASP/散单价有 A/B 证据则反转 | 跟中际/新易盛/东山 Q2 财报、投关、ASP/毛利/存货和海关可复核表 |
| Ciena scale-across optical systems / coherent modules / 400G-800G pluggables | 系统级供需紧张 | soft_bottleneck/read-through | 系统级 optical networking backlog 和 pluggables 强，但单品拆分不足 | unchanged | Ciena Q2 FY2026 official transcript/10-Q 既有 | 2026H2-2027 watch；置信度中 | backlog 回落、交付兑现、供应约束拆分消失 | 跟 pump/modem/line-system/pluggable 拆分 |
| 天孚光引擎个别物料 | 公司级软堵点/观察 | soft_bottleneck/watch | 个别物料阶段性缺货仍未拆清；FAU/ELS 稳定交付口径未被新证据推翻 | unchanged | 2026-05-14 CNINFO 投关；本窗口无新增 | N/A；缺具体物料、缺口比例、交期和客户影响；置信度低 | 公司披露缺料解除或点名物料影响交付 | 继续追问物料类别和是否影响 1.6T 光引擎 |
| 主动对准 / CPO 制造测试设备 | 未来迁移观察核心 | watch_to_soft | CPO/硅光光引擎需要更高精度对准、晶圆级/芯片级测试和验收；但商业化订单未落地 | evidence_up_but_not_current_bottleneck | ficonTEC/NVIDIA 官网合作；罗博特科 CNINFO 明确暂无订单/收入；Nokia ATP 扩产 | 当前 N/A；2026H2-2027 可能升温；置信度中低 | CPO-specific 订单、设备排队、验收收入、良率瓶颈；若无订单或 CPO 延后则降级 | 跟罗博特科订单、验收收入和客户采购路径 |
| 高密度数据中心光纤/光缆/连接组件 | 边界内观察增强 | soft_bottleneck/watch | AI cluster 光密度提升，客户长协和专用产能可能使合格 fiber/cable/connectivity 紧张 | upgraded_watch | Amazon-Corning、NVIDIA-Corning 官方合作 | 当前 N/A；0-12 个月可能升温；置信度中 | 交期/涨价/长协 minimum capacity、FAU/MT/PM fiber/fiber array 单品短缺；若扩产充分释放则反转 | 跟 Corning/Fujikura/Sumitomo 产能、交期、合同细节和单品传导 |
| FAU / fiber array / MT ferrule / 高密度连接件 / 微透镜阵列 | 未来迁移观察 | watch_to_soft | CPO/ELS 通道数和 fiber attach 密度上升，提高精密连接和低损耗耦合门槛 | unchanged_watch；06-22 MPO/FAU 扩产线索仅 C/lead | Corning/FAU、台股试产/送样、Wiwynn/Ayar/Coherent 既有线索；06-22 邮件线索未见 A/B 级订单、保底、交期、涨价或良率证据 | 2026H2-2028；置信度中低 | 稳定交付、二供认证通过、CPO 延后 | 跟认证转量产、MPO/FAU 订单/保底、交期/涨价/良率和二供认证 |
| 光模块/光引擎热管理与 ELSFP 液冷兼容 | 未来迁移观察 | watch_to_soft | 高功率 ELS、CPO 和光引擎对 IHS/cage/TIM/cold plate interface 和热可靠性提出要求 | unchanged_watch | Lumentum ELSFP、Wiwynn/Ayar 既有线索 | watch，2026H2-2028；置信度低中 | 接口标准化、风冷/液冷方案稳定，多供应商稳定交付 | 等模块厂/交换机厂点名热可靠性或液冷兼容 |
| DSP / driver / TIA / CDR | 战略节点，不是当前堵点 | watch/rejected as current bottleneck | 需求和代际升级明确，但无交期、allocation 或模块厂点名短缺 | unchanged_watch；06-22 新易盛 2027 年 DSP 5100 万颗/Broadcom 主供仍为 C/lead | Broadcom 官方 Sian2/Sian3 支持 800G/1.6T 200G/lane DSP 路线和 Eoptolink/Innolight 生态合作；未披露 5100 万颗订单；东山称锁定 DSP 储备 | N/A；未来 2027-2028 观察；置信度低中 | 出现明确采购订单/供应商分配、客户 allocation、交期拉长、模块厂点名电芯片短缺；多源稳定供给则维持 strategic node | 核验 2027 DSP 订单数量、Broadcom/Marvell/其他供应商分配、交期/allocation 和模块厂点名短缺 |

## 候选观察池

| 候选节点 | 当前判断 | 需要验证的堵点问题 | 不可直接下结论的原因 |
|---|---|---|---|
| InP 衬底 / 外延 / 6 英寸平台 | 主堵点组成，本期主深挖 | 出口许可、6 英寸良率、非中国产能、客户二供认证、交期和价格 | 扩产路径增强，但短期缺口比例和客户认证节奏仍缺 |
| EML / 高速激光芯片 | 主堵点 | 200G/400G per lane EML 缺口比例、交期、老化测试和扩产兑现 | A/B 支持偏紧，但单品比例仍缺官方量化 |
| CW-DFB / UHP pump / ELS | 主堵点组成和未来迁移核心 | CPO/SiPh/scale-up/scale-across 是否形成独立短缺 | 长协/扩产支持供需紧，但订单、交期、收入单列不完整 |
| 主动对准 / 封装测试设备 / WLBI | 未来迁移观察增强 | CPO/光引擎量产后设备、测试节拍和良率是否拖累爬坡 | 合作证实但罗博特科公告明确暂无订单/收入；缺设备排队和验收收入 |
| FAU / fiber array / MT ferrule / 微透镜 / 隔离器 | 观察增强 | CPO/ELS 是否拉长交期或导致良率瓶颈 | 产品页、展示、试产/送样证明路线准备，不证明当前短缺 |
| 光连接/光纤/连接器 | 未来迁移增强 | Corning/Amazon/NVIDIA 长协是否传导到 MT/FAU/连接器、PM fiber、光纤阵列 | 普通光纤扩产不等于模块上游单品短缺 |
| 光模块/光引擎热管理与液冷兼容 | 观察增强 | 是否迁移到 IHS/cage/TIM/cold plate interface、ELSFP 稳定光源、浸没兼容、热可靠性和返修 | 机柜级液冷热度不能直接证明模块级卡点 |
| SiPh / TFLN | SiPh 路线期权增强，TFLN 仍 watch/rejected | 是否从路线验证进入客户定点与批量出货 | 当前更多是平台/路线证据，不是供需缺口 |

## 公司映射基线

| 公司 | ticker | 市场 | 当前角色 | 状态 |
|---|---|---|---|
| Coherent | COHR.US | 美股 | 6 英寸 InP、EML、CW laser、photodiode、CPO/OCS、PM fiber/FAU | 全球主候选，也是主堵点缓解方 |
| Lumentum | LITE.US | 美股 | EML、InP、UHP pump、CW/ELS、OCS/CPO | 全球主候选；Mizuho replay 已出现，但交期/锁产能仍待官方逐字稿、PDF 或 SEC 披露升级 |
| JX Advanced Metals | 5016.T | 日股 | InP substrate | 长期衬底缓解核心，FY2030 7-10x 目标 |
| IQE | IQE.L | 英股 | InP epiwafer | Tower 多年供应协议强化外延片锁供 |
| Tower Semiconductor | TSEM.US | 美股 | InP photonic devices / OCS modulator | SiPh/OCS 代工路径观察 |
| Nokia | NOK.US / NOKIA.HE | 美/芬 | Photonic chip advanced test and packaging | 测试封装缓解方，非模块单品短缺证明 |
| Corning | GLW.US | 美股 | 光连接、光纤、AI 数据中心 optical connectivity、FAU | 未来迁移观察增强 |
| 中际旭创 | 300308.SZ | A 股 | 800G/1.6T 模块、硅光、规模交付、前端供应链锁定 | A 股基本面核心；交易弹性被超大市值压制 |
| 新易盛 | 300502.SZ | A 股 | 800G/1.6T 模块、硅光、海外产能 | A 股业绩弹性核心；已补最小跟踪卡，硬证据限 CNINFO 2026-06-01 投关的锁料/1.6T/硅光/OCS 口径，DSP 5100 万颗仍为 C/lead |
| 天孚通信 | 300394.SZ | A 股 | 光器件、1.6T 光引擎、FAU/ELS/CPO 配套 | 次级跟踪核心，个别物料待拆 |
| 光迅科技 | 002281.SZ | A 股 | 光模块、光器件、硅光/CPO/NPO、海外产能 | 高交易弹性观察，需订单/收入验证 |
| 东山精密 | 002384.SZ | A 股 | 索尔思光芯片/光模块、EML 与硅光并行、AI PCB 协同 | A 股垂直一体化强观察；12 亿美元扩建增强，需订单/客户/毛利/良率量化 |
| 源杰科技 | 688498.SH | A 股 | CW laser、EML/DFB 光芯片 | 需 200G EML/AI 客户硬证据；估值和证据缺口高 |
| 长光华芯 | 688048.SH | A 股 | 高功率半导体激光平台、光通信 EML/DFB/VCSEL/CW DFB 观察 | `watch_to_soft/evidence_gap_card`，不能等同 InP/CW 主堵点 |
| 光库科技 | 300620.SZ | A 股 | 隔离器、铌酸锂、无源器件 | 观察 |
| 罗博特科 | 300757.SZ | A 股 | ficonTEC 光子封装/测试设备 | 官方合作证实但暂无订单/收入；未来设备迁移观察核心，不是当前主堵点 |
| 太辰光 | 300570.SZ | A 股 | MT ferrule、连接器/精密连接件、FAU 观察 | 光连接高波动观察池 |
| 光圣科技 | 6442.TW | 台股 | datacenter optics、合圣 FAU/ELS/CPO 零组件 | 台股重点观察，仍为认证/试产阶段 |
| 上诠 | 3363.TWO | 台股 | FAU/无源精密件、PIC 封装 | 台股观察 |
| 波若威 | 3163.TWO | 台股 | 光纤阵列/连接组件 | 台股观察 |

## 本期三类排名快照

- 基本面质量：`Coherent > Lumentum > Corning > 中际旭创 > 新易盛 > 天孚通信`。
- 业绩弹性：`东山精密/索尔思 > Coherent > Lumentum > 新易盛 > 源杰科技 watch > 罗博特科 option`。
- 交易弹性：`罗博特科 > 太辰光 > 源杰科技 > 东山精密 > 新易盛 > 中际旭创 > 天孚通信`。本排名使用 TDX 2026-06-18 行情辅助，行情只作交易弹性和拥挤度，不作产业证据。

## 2026-06-21 A 股披露与行情辅助

| 项目 | 结果 | 处理 |
|---|---|---|
| CNINFO 2026-06-17~2026-06-21 | 中际旭创、新易盛、天孚通信、源杰科技、长光华芯、光库科技、太辰光、长飞光纤无新增相关公告；东山精密 2 条扩建/董事会公告；罗博特科 1 条合作事项说明公告 | 东山/罗博特科入本期证据；其他维持待跟踪 |
| 罗博特科公告 | 确认 FSG 与 NVIDIA 合作开发 CPO/光互连制造测试方案；明确暂无相关在手订单、无销售收入、近期不重大影响 | 合作证实，商业化降噪，不升级设备硬堵点 |
| TDX 最近可用行情 | 2026-06-18；核心 A 股普遍估值和拥挤度高，罗博特科 PE 为负且公司公告提示 60 日涨幅超 80% | 只用于交易弹性和风险提示 |

## 下期默认跟踪问题

1. Coherent/JX/IQE/Tower 扩产是否披露客户认证、产能释放、良率、订单或毛利兑现。
2. Lumentum 是否发布可引用的 Mizuho 官方逐字稿/PDF 或后续 SEC 业务披露；未出现前，EML/CW/ELS 交期和锁产能仍不得从 B/C 升为 A。
3. AXT 和中国 InP 出口许可是否出现官方进展，DigiTimes 所称首批发货是否被 AXT/JX/客户披露验证。
4. 罗博特科/ficonTEC 是否出现 CPO-specific 在手订单、客户采购路径、交期排队、验收收入或毛利验证。
5. 东山精密索尔思扩建是否披露审批、资金、设备、客户、产能、良率和毛利率量化。
6. 中际、新易盛、天孚、源杰、太辰光是否在 Q2 财报/投关中拆出客户、订单、交付、毛利、缺料或二供认证。
7. Corning/Amazon/NVIDIA 光连接长协是否披露 minimum capacity、prepayment、交付时间和向 FAU/MT/PM fiber/fiber array 的传导。
8. FAU/fiber array、MT ferrule、PM fiber、ELSFP thermal、主动对准/WLBI/测试设备是否出现交期、涨价、订单排队、良率或返修证据。
9. 复核 2026-06-22 邮件中的四条 C/lead：光模块散单涨价、新易盛 2027 年 DSP 5100 万颗/Broadcom 主供、中际 4-5 月海关出口可能破 80 亿、MPO/FAU 保底翻倍扩产；只有公司公告/IR、海关可复核表、客户/供应商披露或可信 B 级来源交叉后才升级。

## 对话窗口摘要源表

| 当前核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| InP substrate / epiwafer / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS | 合格衬底、外延、6 英寸良率、老化测试、客户认证和出口许可共同限制高端光源供给；低端或未认证产能不能替代 | Coherent CHIPS LOI；JX 7-10x 扩产目标；IQE/Tower 多年外延片供给；AXT/TrendForce/Reuters 既有偏紧证据 | EML/InP：2026H2-2027H1；CW/ELS/UHP 尾部：2027H2-2028H1；长期衬底缓解看 2028-2030 | 许可正常化、6 英寸良率/认证兑现、交期和价格回落、客户停止锁产能 |
| 光模块整机装配与关键原材料同步 | 模块交付仍依赖光芯片、电芯片、无源件、PCB、测试和客户认证同步，但本窗口未见重新短缺证据 | 新易盛既有 Q2 供应链缓解口径；CNINFO 6/17-21 核心公司无整机短缺公告 | 2026Q2-Q3 继续缓解；置信度中 | Q2/Q3 交付、毛利、存货周转改善；若模块厂重提关键料或测试短缺则反转 |
| 主动对准 / CPO 制造测试设备 | CPO/硅光光引擎需要更高精度对准、晶圆级/芯片级测试和验收；但商业化订单未落地 | ficonTEC/NVIDIA 合作；罗博特科 CNINFO 明确暂无相关在手订单和销售收入；Nokia ATP 扩产 | 当前 N/A；2026H2-2027 watch_to_soft | CPO-specific 订单、设备排队、验收收入、良率瓶颈；若无订单或 CPO 延后则降级 |
| 高密度 data-center fiber/cable/connectivity | AI 数据中心光连接密度上升，客户长协和专用产能可能传导到连接组件 | Amazon-Corning、NVIDIA-Corning 官方合作 | 当前 N/A；0-12 个月可能升温 | minimum capacity/prepayment、交期拉长、FAU/MT/PM fiber 传导；若扩产充分释放则反转 |

| 未来潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| CPO/NPO 光引擎与 ELS package | 2026-2028 CPO/ELS 放量会提高外置光源、热稳定、可维护连接和光引擎良率要求 | NVIDIA 产品路线和 ficonTEC 合作支持方向；缺量产订单和交付瓶颈 | 2026H2-2028 | NVIDIA/交换机厂/光源厂披露量产、allocation、客户锁产能或交付瓶颈 | CPO 延后、可插拔继续主导、ELS 多供稳定 |
| FAU / fiber array / MT ferrule / 微透镜 / 隔离器 | 通道数和光连接密度上升，精密耦合和低损耗连接要求提高 | Corning/FAU、台股试产/送样和高密连接线索增强；06-22 MPO/FAU 翻倍扩产仍为 C/lead；缺短缺、涨价、良率证据 | 2026H2-2028 | 客户定点、量产订单、交期拉长、涨价、良率/返修压力 | 二供认证、自动化良率提升、CPO 放量推迟 |
| 主动对准 / WLBI / OWAT / 光电联合测试 | 光子芯片和光引擎量产需要 known-good optical engine 与更长测试节拍 | ficonTEC/NVIDIA、Nokia ATP 扩产；罗博特科无订单/收入是争议核心 | 2026H2-2027 | 设备订单排队、交期拉长、验收收入放量、测试节拍瓶颈 | 设备产能充足、客户验证顺利、CPO 商业化延后 |
| 光模块/光引擎热管理与液冷兼容 | ELSFP、CPO 和高功率光源对 IHS/cage/TIM/cold plate interface 和热可靠性要求提高 | Wiwynn/Ayar/Lumentum 既有线索，当前缺 A/B 级交付受限证据 | 2026H2-2028 watch | 模块厂或交换机厂点名热可靠性、液冷兼容、返修或认证限制交付 | 标准化完成、多供应商稳定交付、热问题未影响良率 |
| DSP / driver / TIA / CDR | 1.6T/3.2T 和 LPO/LRO/CPO 会提高电芯片性能要求 | Broadcom/Marvell 证明需求和路线，不证明当前短缺；东山称已锁定 DSP 储备；06-22 新易盛 5100 万颗说法仍为 C/lead | 2027-2028 watch | 模块厂点名电芯片短缺、客户 allocation、交期拉长 | 多供应商稳定供给或架构改变 BOM |
