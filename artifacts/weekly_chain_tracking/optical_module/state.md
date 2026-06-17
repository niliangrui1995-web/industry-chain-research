# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-06-17
最新报告：`artifacts/weekly_chain_tracking/optical_module/2026-06-17.md`
覆盖窗口：2026-06-14 至 2026-06-17

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

- 当前主硬堵点维持在高端光源链，但本期从 `EML / InP / CW-DFB / pump / ELS` 进一步精确为 `InP 衬底出口许可 + 6 英寸合格 InP 产能 + EML/CW-DFB/UHP/ELS 客户认证和锁产能`。
- AXT 10-Q 把 InP 出口许可从传闻/产业链叙述升级为 A 级官方约束。Reuters 6 月 11 日产业链报道与 Lumentum、Coherent、TrendForce、Ciena 官方材料交叉验证，说明该约束会传导到 AI 数据中心光互连。
- EML/InP 偏紧预计持续至 2026H2-2027H1，置信度中高；InP 衬底、CW-DFB、UHP pump、ELS 若随 CPO/NPO/scale-up 光互连放量，尾部可能延至 2027H2-2028H1，置信度中。
- 光模块整机装配与关键原材料同步维持 `soft_bottleneck/eased`，预计 2026Q2-Q3 继续缓解；本周未发现 A/B 级证据证明整机装配重新成为硬堵点。
- Ciena optical systems / coherent modules / pluggables 的供需紧张已被 A 级官方 transcript 确认，但仍是系统级读数，不能直接拆为 EML、pump、modem 或模块光源单品缺口。
- FAU/fiber array/MT ferrule/高密连接、PM fiber、主动对准/WLBI/光电测试、ELSFP 热管理与液冷兼容进入未来 6-24 个月迁移观察；本周证据仍不足以升级为当前硬堵点。
- 2026-06-15 邮件短更新：未找到 A/B 级来源证明“`NVIDIA CFO 已确认 CPO 按计划推进`”原文；官方可确认的是 NVIDIA 2026 CPO 路线以及 Lumentum、Coherent capacity rights / purchase commitment，不足以单独升级 watch 项。
- 大立光 FA 自动化试产线和潜在 FAU 客户验证线索使 `FAU / fiber array / 高密连接` 的证据质量上升，但仍是试产/认证阶段，不是当前短缺、涨价、交期或良率瓶颈证据。
- 天孚“CPO 光引擎市占 >60%、订单排至 2028 年”未取得官方硬证据；罗博特科 ficonTEC 约 6 亿元订单为 A 级真订单，但指向可插拔硅光量产化耦合设备，不等同 CPO 当前设备瓶颈。
- 2026-06-16 ficonTEC 官网确认与 NVIDIA 围绕下一代 CPO 和 AI 光互连制造、对准、晶圆级/芯片级测试方案持续推进合作；该信息强化罗博特科 `300757.SZ` 的 A 股直接映射和设备迁移观察，但未披露 NVIDIA 采购金额、订单或验收收入，不能替代 CPO-specific 当前设备短缺证据。
- 新易盛 2026-06-15 互动问答支持 Q2 起供应链逐步缓解、下半年交付能力稳定，继续支撑光模块整机装配 `soft_bottleneck/eased`。
- 2026-06-17 东山精密 IR 确认索尔思收购事项已基本完成并并表，12 亿美元主要用于光芯片和光模块产能扩建，后续技术方案坚持 EML 与硅光并行；MOCVD 外延设备目前主要依赖进口，DSP 芯片和 InP 衬底已锁定未来一段时间核心物料储备。该证据把东山精密上调为 A 股光芯片/光模块垂直一体化强观察，但不改变 `InP/EML` 当前主硬堵点，也不把 `DSP` 升级为当前硬堵点。

## 2026-06-15 邮件线索短更新状态

| watch 项 | 本次处理 | 原因 | 下次升级触发 |
|---|---|---|---|
| NVIDIA CPO/NPO/ELS 进度 | 未来观察增强，不升级为当前硬堵点 | 官方路线仍指向 2026 商业化，ficonTEC 官网 2026-06 确认与 NVIDIA 在 CPO/AI 光互连制造测试方案上持续推进合作；但未披露 NVIDIA 设备采购金额、订单、交期或验收收入。 | NVIDIA 或交换机/光源供应商披露 CPO-specific 量产、交期、allocation、客户锁产能、设备订单或财务兑现。 |
| FAU / fiber array / MT ferrule / 微透镜 / 高密连接 | 维持 `watch_to_soft`，证据质量上升 | 大立光 9 月前 FA 自动化试产线和潜在客户验证说明产业准备提速，但仍未进入短缺和量产瓶颈证据层。 | 客户定点、量产订单、交期拉长、价格上行、良率或返修压力。 |
| 主动对准 / 耦合 / WLBI / 光电联合测试 | 维持 `watch_to_soft`，证据质量上升 | 罗博特科 ficonTEC 6 亿元订单真实但公告口径是可插拔硅光量产化耦合设备及服务；2026-06 ficonTEC/NVIDIA 官网合作进展强化 CPO 制造测试路线，但仍不是 CPO-specific 当前短缺。 | 新增 CPO/NPO 光引擎设备订单、设备交期排队、测试节拍瓶颈、良率爬坡证据或验收收入。 |
| 天孚光引擎个别物料 | 维持公司级 `soft_bottleneck/watch` | 公司硬证据仅确认 FAU/ELS 稳定交付和个别物料阶段性缺货；市占 >60%、订单到 2028 未核实。 | 公司点名具体缺料、缺口比例、客户影响，或披露订单/收入/产能锁定。 |
| 源杰 200G EML / 高端激光器 | 维持 watch | 未找到 2026-06-15 新客户定点、批量订单、收入拆分或毛利兑现证据。 | 200G PAM4 EML 客户设计定点、批量出货、订单或收入拆分。 |
| 光模块整机装配与关键原材料同步 | 维持 `soft_bottleneck/eased` | 新易盛 2026-06-15 互动问答称 Q2 起供应链逐步缓解、下半年交付能力稳定；昨晚 A 股跟踪未发现中际/天孚/源杰新增经营硬证据。 | 模块厂重新点名关键料、测试、封装或客户认证短缺并影响交付。 |

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| Lumentum Mizuho 2026-06-09 或后续官方 transcript 是否披露 EML/CW-DFB/pump/ELS 交期、allocation、订单可见度和 6 英寸 InP ramp？ | 找到第三方 transcript 页面和 TIKR 摘要，未找到 Lumentum 官网逐字稿。第三方摘要只能按 B/C 级使用。 | 部分证实，未转 A；继续跟踪 |
| Coherent 后续 10-Q/IR 是否把 6 英寸 InP 良率、产量目标转化为合格产能、客户认证、毛利和库存周转改善？ | Reuters 和 Coherent OFC deck 强化 6 英寸 InP、CW-DFB、CPO/ELS 缓解路径，但仍缺良率、客户认证和财务兑现。 | 缓解路径强化；兑现待跟踪 |
| 新易盛 Q2 物料缓解是否在财报或投关记录中拆明具体物料，天孚个别物料是否有类别、缺口比例和客户影响？ | CNINFO 2026-06-07 至 2026-06-14 查询中，300502、300394 及 A 股核心 8 家 total=0。 | 仍待跟踪 |
| Ciena 官方 replay/transcript 或后续 10-Q 是否确认 pump laser / modem / line-system 约束，并能否区分 EDFA/Raman pump、coherent modem 与数据中心模块光源？ | Ciena 官方 transcript 已确认 backlog 77 亿美元、400G/800G pluggables 强、supply not keeping pace with demand。仍未拆单品。 | broad optical supply tightness 已确认；细分仍待跟踪 |
| FAU/fiber array、ELSFP liquid cooling、主动对准/测试设备是否从 Computex 展示转入客户认证、交期拉长、良率/返修或批量订单证据？ | Amazon-Corning、Wiwynn/Ayar、Corning FAU、Coherent CPO stack 强化 future watch，但无当前交期/价格/良率/订单排队证据。 | 未来观察增强，未升级硬堵点 |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| InP substrate / 6 英寸合格 InP 产能 / EML / CW-DFB / UHP pump / ELS | 当前主堵点 | hard_bottleneck | 出口许可、InP 衬底集中、6 英寸良率、器件老化测试、客户认证、capacity rights、ELS 热稳定共同约束可交付供给 | worsened/refined | AXT 10-Q；Reuters 6/11；Lumentum/Coherent OFC；TrendForce 6/3；Ciena official transcript | EML/InP：2026H2-2027H1；CW/ELS/UHP/InP 尾部：2027H2-2028H1 可能偏紧；置信度中高/中 | 许可正常化、6 英寸良率兑现、二供认证、交期/allocation/价格回落、客户不再锁产能 | 跟 AXT/Coherent/Lumentum 10-Q、IR、许可、良率和客户认证 |
| Ciena scale-across optical systems / coherent modules / 400G-800G pluggables | 系统级供需紧张 | soft_bottleneck/read-through | AI optical networking backlog 高，系统供给未跟上需求，但单品拆分不足 | confirmed | Ciena Q2 FY2026 official transcript 和 10-Q | 2026H2-2027 watch；置信度中 | backlog 回落、Q3/Q4 交付兑现、无追加 supply-security 投入 | 跟 pump/modem/line-system 拆分 |
| 光模块整机装配与关键原材料同步 | 当前软堵点 | soft_bottleneck | 模块产线需光芯片、电芯片、无源件、PCB、测试资源和客户认证同步；备货、二供、保障协议和扩产仍在缓解 | eased/confirmed | CNINFO 2026-06-07~06-14 核心 8 家 total=0；2026-06-15 新易盛互动问答称 Q2 起供应链逐步缓解、下半年交付能力稳定 | 2026Q2-Q3 继续缓解；置信度中 | Q2/Q3 交付兑现、预付款和存货周转改善、毛利正常化；若模块厂重提关键料/测试短缺则反转 | 跟 Q2 财报、预付款、存货、毛利和订单 |
| 天孚光引擎个别物料 | 公司级软堵点/观察 | soft_bottleneck/watch | 公司级阶段性缺货仍未拆清；FAU/ELS 已被公司称为稳定交付，不能升级为行业硬堵点 | unchanged | 2026-05-14 CNINFO 投关确认 FAU/ELS 稳定交付和个别物料阶段性缺货；2026-06-15 日更无新增拆分 | N/A；缺具体物料、缺口比例、交期和客户影响；置信度低 | 公司披露缺料解除或拆清物料；若点名 FAU/透镜/隔离器/磁光材料短缺并影响产量，则升级 | 继续追问物料类别和是否影响 1.6T 光引擎 |
| 高密度数据中心光纤/光缆/连接组件 | 边界内观察增强 | soft_bottleneck/watch | AI cluster 光密度提升，客户长协和专用产能可能使合格 fiber/cable/connectivity 紧张 | upgraded_watch | Amazon-Corning 多年协议；Corning/Meta/NVIDIA 长协；Wiwynn CPO ecosystem | 当前 N/A；未来 0-12 个月可能升温；置信度中 | Corning/Fujikura 新产能释放、价格回落、交期正常化、连接件二供通过 | 跟 Corning transcript、Fujikura/Corning 产能、MT/FAU/PM fiber/fiber array 传导 |
| FAU / fiber array / MT ferrule / 高密度连接件 / 微透镜阵列 | 未来迁移观察增强 | watch_to_soft | CPO/ELS 通道数和 fiber attach 密度上升，可拆卸维护和低损耗耦合提高精密连接门槛 | upgraded_watch/evidence_quality_up | Corning FAU page；Wiwynn ecosystem；Coherent CPO stack；大立光 9 月前 FA 自动化试产线和潜在客户验证线索 | 2026H2-2028；置信度中低 | 稳定交付、二供认证通过、CPO 延后 | 跟认证是否转量产、交期/涨价/良率 |
| 主动对准 / 耦合 / WLBI / 光电联合测试 | 未来迁移观察 | watch_to_soft | 1.6T/3.2T、CPO/NPO 和 SiPh 光 I/O 提高耦合精度、测试节拍和 known-good optical engine 要求 | evidence_quality_up | Coherent CPO stack、Wiwynn/Ayar rack demo、罗博特科 ficonTEC 可插拔硅光耦合设备约 6 亿元订单、ficonTEC/NVIDIA 2026-06 官网合作进展 | 2026H2-2027 可能升温；置信度中 | 自动化设备交付增加、测试节拍下降、良率爬升 | 跟 CPO-specific 设备订单、设备交期、耦合 CT、WLBI/OWAT 成本、良率和验收收入 |
| 光模块/光引擎热管理与 ELSFP 液冷兼容 | 未来迁移观察 | watch_to_soft | 高功率 ELS、CPO 和光引擎对激光稳定性、IHS/cage/TIM/冷板接口和热可靠性提出新要求 | upgraded_watch | Lumentum ELSFP product page；Wiwynn ELSFP liquid cooling；Ayar rack demo | watch，2026H2-2028；置信度低中 | 接口标准化、风冷/液冷方案稳定，多供应商稳定交付 | 等模块厂/交换机厂点名热可靠性或液冷兼容 |
| DSP / driver / TIA / CDR | 战略节点，不是当前堵点 | watch/rejected as bottleneck | Broadcom/Marvell A 级财报证明 AI networking/electro-optics/CPO/NPO demand 强，但未见交期、allocation 或模块厂点名短缺 | unchanged_watch | Broadcom/Marvell 上期 official/transcript | N/A；未来 2027-2028 观察；置信度低中 | 出现明确客户 allocation、交期拉长、模块厂点名电芯片短缺；多源稳定供给则维持 strategic node | 等 3.2T/LPO/LRO/CPO 芯片交期证据 |

## 候选观察池

| 候选节点 | 当前判断 | 需要验证的堵点问题 | 不可直接下结论的原因 |
|---|---|---|---|
| InP 衬底 / 外延 / 6 英寸平台 | 主堵点组成，本期主深挖 | 出口许可获批节奏、6 英寸良率、非中国产能、客户二供认证 | 出口许可和扩产路径均明确，但缺实时缺口比例和客户名单 |
| EML / 高速激光芯片 | 主堵点 | 100/200G/400G lane EML 缺口比例、交期、老化测试和扩产兑现 | A/B 证据支持供给偏紧，但单品比例仍缺官方量化 |
| CW-DFB / UHP pump / ELS | 主堵点组成和未来迁移核心 | CPO/SiPh/scale-up/scale-across 是否形成独立短缺 | TrendForce/Ciena/Wiwynn 证据增强，但订单、交期、收入单列仍不完整 |
| 光模块整机与测试 | 软堵点缓解观察 | 中际/新易盛 Q2 交付、预付款、存货、毛利是否验证缓解 | 本周无新增整机缺料证据 |
| FAU / fiber array / MT ferrule / 微透镜 / 隔离器 | 观察增强 | CPO/ELS 是否拉长交期或导致良率瓶颈 | 产品页、展示、送样和大立光试产线证明路线准备，不证明当前短缺 |
| 主动对准 / 封装测试设备 / WLBI | 观察增强 | 光引擎/CPO 量产后设备、测试节拍和良率是否拖累爬坡 | 罗博特科 ficonTEC 订单证明可插拔硅光耦合设备需求，不证明 CPO-specific 设备短缺或排队 |
| 光连接/光纤/连接器 | 未来迁移增强 | Amazon/Corning、Meta/Corning、NVIDIA/Corning 是否传导到 MT/FAU/连接器、PM fiber、光纤阵列和 A/台股公司 | 普通光纤扩产不等于模块上游单品短缺，必须看到高密度数据中心/CPO/ELS 场景证据 |
| 光模块/光引擎热管理与液冷兼容 | 观察增强 | 是否把卡点迁移到 IHS/cage/TIM/cold plate interface、ELSFP 稳定光源、浸没兼容、热可靠性和返修 | 机柜级液冷热度不能直接证明模块级卡点；需模块或 ELSFP 场景证据 |
| SiPh / TFLN | SiPh 路线期权增强，TFLN 仍 watch/rejected | 是否从路线验证进入客户定点与批量出货 | 当前更多是平台/路线证据，不是供需缺口 |

## 本期主深挖与次级跟踪

- 主深挖：InP 衬底/6 英寸合格 InP 产能及其对 EML、CW-DFB、UHP pump、ELS 的约束。
- 次级跟踪 1：Ciena optical networking、coherent modules、400G/800G pluggables 和 pump/modem 供需读数。
- 次级跟踪 2：CPO/NPO、ELSFP 热稳定、光引擎封装、FAU/fiber array 和高密连接。
- 次级跟踪 3：高密度数据中心 fiber/cable/connectivity 与模块/光引擎边界内传导。

## 公司映射基线

| 公司 | ticker | 市场 | 当前角色 | 状态 |
|---|---|---|---|
| Lumentum | LITE.US | 美股 | EML、InP、UHP pump、CW/ELS、OCS/CPO | 全球主候选，第三方 Mizuho 信息待官方升级 |
| Coherent | COHR.US | 美股 | InP 6 英寸、EML、CW laser、photodiode、CPO/OCS、FAU/PM fiber | 全球主候选，也是缓解路径 |
| AXT | AXTI.US | 美股 | InP substrate、出口许可 | 本期新增纯敞口观察，政策和规模风险高 |
| Broadcom | AVGO.US | 美股 | AI networking、CPO、1.6T DSP、CW/EML lasers | 全球核心路线公司，不是单一短缺证明 |
| Ciena | CIEN.US | 美股 | Optical Networking、coherent modules、pluggables、line systems | 系统级 demand read-through，注意和组件供应商分层 |
| Fabrinet | FN.US | 美股 | 高级光封装、模块装配和测试 | 量受益候选 |
| Corning | GLW.US | 美股 | 光连接、光纤、AI 数据中心光连接产能、CPO fiber ecosystem、FAU | 未来迁移观察增强 |
| 中际旭创 | 300308.SZ | A 股 | 800G/1.6T 模块、硅光、规模交付、前端供应链锁定 | A 股基本面核心 |
| 新易盛 | 300502.SZ | A 股 | 800G/1.6T 模块、硅光、海外产能 | A 股业绩弹性核心，等 Q2 验证 |
| 天孚通信 | 300394.SZ | A 股 | 光器件、1.6T 光引擎、FAU/ELS/CPO 配套 | 次级跟踪核心，个别物料待拆 |
| 光迅科技 | 002281.SZ | A 股 | 光模块、光器件、硅光/CPO/NPO、海外产能 | 高交易弹性观察，需订单/收入验证 |
| 东山精密 | 002384.SZ | A 股 | 索尔思光芯片/光模块、EML 与硅光并行、AI PCB 协同 | A 股垂直一体化强观察；业绩弹性高、交易弹性很高但拥挤，需订单/客户/毛利率/良率和扩产审批量化 |
| 源杰科技 | 688498.SH | A 股 | CW laser、EML/DFB 光芯片 | 需 200G EML/AI 客户硬证据 |
| 光库科技 | 300620.SZ | A 股 | 隔离器、铌酸锂、无源器件 | 观察 |
| 罗博特科 | 300757.SZ | A 股 | ficonTEC 光子封装/测试设备 | ficonTEC 全资体系内资产；NVIDIA 合作进展增强观察，但仍需 CPO-specific 订单、交付和收入证据 |
| 太辰光 | 300570.SZ | A 股 | MT ferrule、连接器/精密连接件、FAU 观察 | 光连接高波动观察池 |
| 光圣科技 | 6442.TW | 台股 | datacenter optics、合圣 FAU/ELS/CPO 零组件 | 台股重点观察，仍为认证/试产阶段 |
| 上诠 | 3363.TWO | 台股 | FAU/无源精密件、PIC 封装 | 台股观察 |
| 波若威 | 3163.TWO | 台股 | 光纤阵列/连接组件 | 台股观察 |

## 下期默认跟踪问题

1. AXT、Coherent、Lumentum 是否披露 InP 出口许可、6 英寸 InP 良率、客户认证、库存和毛利变化？
2. Lumentum 是否发布 Mizuho 2026-06-09 官网 transcript/replay 或后续 10-Q，能否把第三方 EML undershipping 和 substrate tightened 升级为 A 级？
3. Ciena 10-Q、IR 或供应商信息是否把 supply not keeping pace with demand 拆成 pump、modem、coherent module、line system 或 pluggable 单品？
4. 新易盛、天孚、中际、源杰等 A 股公司是否在 Q2 财报、互动易、投关中拆出物料、客户、预付款、存货、毛利和交付？
5. FAU/fiber array、MT ferrule、PM fiber、ELSFP thermal、主动对准/WLBI/测试设备是否出现交期、涨价、订单排队、良率或返修证据？
6. NVIDIA 是否发布可核验的 CFO/SVP transcript、CPO product update 或 customer deployment 信息，能否确认 2026 路线没有推迟？
7. 大立光 FA 自动化试产线是否如期建成，潜在 FAU 客户是否从看线/验证进入定点、量产订单和收入贡献？
8. 天孚 CPO 光引擎市占、订单期限、FAU/ELS 产能和个别物料缺口是否能被公司公告、投关、订单或收入拆分证实？
9. 罗博特科 ficonTEC 是否出现新的 CPO-specific 设备订单、NVIDIA/客户采购路径、交期排队、产能瓶颈或验收收入证据？
10. 新易盛 Q2 起供应链缓解是否在 Q2/Q3 财报中兑现为交付、毛利、存货周转和现金流改善？
