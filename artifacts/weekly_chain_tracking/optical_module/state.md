# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-06-07
最新报告：`artifacts/weekly_chain_tracking/optical_module/2026-06-07.md`
覆盖窗口：2026-05-31 至 2026-06-07

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

- 高端 EML / InP / CW-DFB / pump / ELS 维持当前主硬堵点，原因是 1.6T/3.2T、CPO/OCS、scale-up/scale-across 需求继续超过合格光源产能、良率、老化测试、客户认证和 capacity rights。
- EML/InP 偏紧预计持续至 2026H2-2027H1，置信度中高；CW/pump/ELS/CPO 相关光源若 2027-2028 年放量，可能延至 2027H2-2028H1，置信度中。
- 光模块整机装配与关键原材料同步维持 soft_bottleneck/eased，预计 2026Q2-Q3 继续缓解；未发现本周 A/B 级证据证明整机装配重新成为硬堵点。
- FAU/fiber array/MT ferrule/高密连接、主动对准/WLBI/光电测试、模块/光引擎热管理与 ELSFP 液冷兼容进入未来 6-24 个月迁移观察，但本周证据仍不足以升级为当前硬堵点。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| Lumentum 是否发布官网版 J.P. Morgan transcript/replay 或后续 IR/10-Q，能否把 InP/EML/CW/pump/ELS 缺口从 B 级 transcript 提升为 A 级？ | 未找到官网版 J.P. Morgan 或 BofA transcript。Lumentum 官网只确认 2026-06-03 BofA、2026-06-09 Mizuho 等活动安排。Quartr 对 BofA 的摘要仍按 B 级。 | 仍未转 A；继续跟踪 |
| Coherent 6 英寸 InP 官方良率/产量目标是否在后续披露中兑现为合格产能、客户认证、毛利和库存周转改善？ | 本周无新的 Coherent 官方季度披露；TrendForce 6/3 进一步确认 Coherent 正加速 6 英寸 InP epi-wafer 转换，并开发 400mW CW-DFB LD。仍缺客户认证、单品交期、毛利和库存周转验证。 | 缓解路径被强化；认证仍待跟踪 |
| 新易盛 Q2 物料缓解是否在财报或投关记录中兑现，具体缓解光芯片、电芯片、无源件、PCB 还是测试资源？ | 2026-05-31 至 2026-06-07 CNINFO 窗口查询 300502 新易盛 total=0，无新增官方公告或投关记录。 | 仍待跟踪 |
| 天孚通信“个别物料阶段性缺货”到底是哪一类，是否影响 1.6T 光引擎产量和毛利？ | 本窗口 CNINFO 查询 300394 天孚通信 total=0，无新增官方拆分。FAU/ELS 仍因公司前期披露稳定交付而不能升级为行业硬堵点。 | 仍待跟踪 |
| Corning 官方 transcript 能否拆出 optical connectivity/fiber 的 minimum capacity、prepayment、产能释放节奏，并是否传导到 MT ferrule、FAU、PM fiber、fiber array 和 A/台股公司？ | Corning/Meta、Corning/NVIDIA 长协仍为 A 级需求/扩产信号；Wiwynn Computex CPO 生态把 Corning/SENKO/TE/Molex/FOCI 纳入 CPO fiber/connectivity 方案，但没有证明 MT/FAU/PM fiber/fiber array 当前单品短缺。 | 观察增强，未升级当前堵点 |
| FAU/fiber array、主动对准/测试设备、WLBI/OWAT 和模块级热管理是否出现交期、良率、客户认证或订单排队的 A/B 级证据？ | FAU/fiber array 和 ELSFP 热管理证据增强，但多为展示、送样、生态合作。AuthenX 2D FAU、Wiwynn ELSFP liquid cooling、Largan FAU/光学件送样说明未来工程约束清楚；尚未出现交期、涨价、订单排队或良率拖累交付的 A/B 级证据。 | 升级 future watch，不升级当前堵点 |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| 高端 EML / InP / CW-DFB / pump / ELS | 当前主堵点 | hard_bottleneck | 1.6T/3.2T、CPO/OCS、scale-up/scale-across 需求超过合格光源产能；约束在 InP/6 英寸良率、老化测试、客户认证、capacity rights 和 ELS 热稳定 | validated/unchanged | TrendForce 6/3：NVIDIA/Google/Meta 锁定 EML/CW-DFB 产能，2026 年月产能预计 5,070 万颗；Lumentum Q3 官方强调 laser chips、pump/narrow-linewidth lasers；Ciena transcript 称 supply not keeping pace with demand | EML/InP：2026H2-2027H1；CW/pump/ELS/CPO：可能延至 2027H2-2028H1；置信度中高 | allocation 解除、交期恢复；Coherent/Lumentum 6 英寸和新 fab 合格产能兑现；大客户不再锁产能；模块厂预付款和毛利回落 | 跟 Lumentum Mizuho/10-Q、Coherent 6 英寸量产、Ciena pump/modem 约束 |
| 光模块整机装配与关键原材料同步 | 当前软堵点 | soft_bottleneck | 模块产线需光芯片、电芯片、无源件、PCB、测试资源和客户认证同步；但备货、二供、保障协议和扩产仍在缓解 | eased/unchanged | 本周 A 股核心公司 CNINFO 窗口无新增缺料公告；光迅前期定增是产能/研发缓解路径而非短缺证据 | 2026Q2-Q3 继续缓解，约 3-6 个月；置信度中 | Q2/Q3 交付兑现、预付款和存货周转改善、毛利正常化；若模块厂重新点名关键料/测试瓶颈则反转 | 跟新易盛/中际 Q2 财报和物料拆分 |
| 天孚光引擎个别物料 | 公司级软堵点/观察 | soft_bottleneck/watch | 公司级阶段性缺货仍未拆清；FAU/ELS 已被公司称为稳定交付，不能升级为行业硬堵点 | unchanged | 2026-05-31 至 2026-06-07 CNINFO 无新增拆分；台股 FAU/合圣送样认证是未来路线，不能解释天孚缺料 | N/A；缺具体物料、缺口比例、交期和客户影响；置信度低 | 公司披露缺料解除或拆清物料；若点名 FAU/透镜/隔离器/磁光材料短缺并影响产量，则升级 | 继续追问物料类别和是否影响 1.6T 光引擎 |
| 高密度数据中心光纤/光缆/连接组件 | 边界内观察增强 | soft_bottleneck/watch | AI cluster 光密度提升，客户长协和专用产能可能使合格 fiber/cable/connectivity 紧张 | upgraded_watch | Corning/Meta、Corning/NVIDIA 长协为 A 级需求/扩产信号；Wiwynn CPO ecosystem 把 Corning/SENKO/TE/Molex/FOCI 纳入高密连接方案 | 当前 watch/soft；0-12 个月可能升温；置信度中 | Corning/Fujikura 新产能释放、价格回落、交期正常化；连接件二供通过认证 | 跟 Corning transcript；跟 MT/FAU/PM fiber/fiber array 单品传导 |
| FAU / fiber array / MT ferrule / 高密度连接件 / 微透镜阵列 | 未来迁移观察增强 | watch_to_soft | CPO/ELS 通道数和 fiber attach 密度上升，可拆卸维护和低损耗耦合提高精密连接门槛 | upgraded_watch | AuthenX 2D FAU、光圣/合圣送样认证、大立光/先进光准备送样；尚未证明当前短缺或订单兑现 | 2026H2-2028；置信度中低 | 稳定交付、二供认证通过、CPO 延后 | 跟认证是否转量产、交期/涨价/良率 |
| 主动对准 / 耦合 / WLBI / 光电联合测试 | 未来迁移观察 | watch_to_soft | 1.6T/3.2T、CPO/NPO 和 SiPh 光 I/O 提高耦合精度、测试节拍和 known-good optical engine 要求 | unchanged/upgraded_watch | 上期 Aehr WLBI 与 CPO testing 资料，本周 Computex CPO 生态强化封装复杂度；缺设备交期/订单排队 A/B 证据 | 2026H2-2027 可能升温；置信度中 | 自动化设备交付增加，测试节拍下降，良率爬升，多设备商二供导入 | 跟设备交期、耦合 CT、WLBI/OWAT 成本和良率 |
| 光模块/光引擎热管理与 ELSFP 液冷兼容 | 未来迁移观察 | watch_to_soft | 高功率 ELS、CPO 和光引擎对激光稳定性、IHS/cage/TIM/冷板接口和热可靠性提出新要求 | upgraded_watch | Wiwynn 为 ELSFP 设计液冷以确保 consistent laser output；仍为展示，缺交付/认证受限证据 | watch，2026H2-2028；置信度低中 | 接口标准化、风冷/液冷方案稳定，多供应商稳定交付 | 等模块厂/交换机厂点名热可靠性或液冷兼容 |
| DSP / driver / TIA / CDR | 战略节点，不是当前堵点 | watch/rejected as bottleneck | Broadcom/Marvell A 级财报证明 AI networking/electro-optics/CPO/NPO demand 强，但未见交期、allocation 或模块厂点名短缺 | upgraded_watch | Broadcom Q2 FY2026 official + transcript；Marvell 上期 official | N/A；未来 2027-2028 观察；置信度低中 | 出现明确客户 allocation、交期拉长、模块厂点名电芯片短缺；多源稳定供给则维持 strategic node | 等 3.2T/LPO/LRO 代际证据和供应商交期 |

## 候选观察池

| 候选节点 | 当前判断 | 需要验证的堵点问题 | 不可直接下结论的原因 |
|---|---|---|---|
| EML / 高速激光芯片 | 主堵点 | 200G/400G lane EML 缺口比例、交期、良率和扩产兑现 | A/B 证据支持供给缺口，但单品比例仍缺官方量化 |
| InP 衬底 / 外延 / 6 英寸平台 | 主堵点组成 | Coherent/Lumentum 6 英寸 ramp 是否转化为合格供给 | 6 英寸良率/产量路径清楚，但扩产不等于可交付，仍需认证、毛利和库存周转 |
| CW-DFB / ELS / pump laser | 主堵点组成和未来迁移核心 | CPO/SiPh/scale-up/scale-across 是否形成独立短缺 | TrendForce/Ciena/Wiwynn 证据增强，但订单/交期/收入单列仍不完整 |
| 光模块整机与测试 | 软堵点缓解观察 | 中际/新易盛 Q2 交付、预付款、存货、毛利是否验证缓解 | 本周无新增整机缺料证据，光迅定增更偏缓解路径 |
| FAU / fiber array / MT ferrule / 微透镜 / 隔离器 | 观察增强 | CPO/ELS 是否拉长交期或导致良率瓶颈 | AuthenX/光圣/大立光线索证明路线，不证明当前短缺 |
| 主动对准 / 封装测试设备 / WLBI | 观察增强 | 光引擎/CPO 量产后设备、测试节拍和良率是否拖累爬坡 | 当前缺设备交期/订单排队 A/B 证据 |
| 光连接/光纤/连接器 | 未来迁移增强 | Corning/NVIDIA/Meta 是否传导到 MT/FAU/连接器、PM fiber、光纤阵列和 A/台股公司 | 光纤扩产不等于模块上游单品短缺，必须看到高密度数据中心/CPO/ELS 场景证据 |
| 光模块/光引擎热管理与液冷兼容 | 观察增强 | 是否把卡点迁移到 IHS/cage/TIM/cold plate interface、ELSFP 稳定光源、浸没兼容、热可靠性和返修 | 机柜级液冷热度不能直接证明模块级卡点；Wiwynn 是 ELSFP/CPO 展示 |
| SiPh / TFLN | SiPh 路线期权增强，TFLN 仍 watch/rejected | 是否从路线验证进入客户定点与批量出货 | 当前更多是平台/路线证据，不是供需缺口 |

## 本期主深挖与次级跟踪

- 主深挖：高端 EML / InP / CW-DFB / pump laser / ELS。
- 次级跟踪 1：Ciena optical networking、coherent modules、pump/modem 供需读数。
- 次级跟踪 2：Broadcom AI networking / CPO / 1.6T DSP / CW / EML 需求信号。
- 次级跟踪 3：CPO 生态中的 FAU/fiber array、ELSFP 热稳定、主动对准和封装测试。

## 公司映射基线

| 公司 | ticker | 市场 | 当前角色 | 状态 |
|---|---|---|---|
| Lumentum | LITE.US | 美股 | EML、InP、pump/narrow-linewidth laser、CW/ELS、OCS/CPO | 全球主候选，供需缺口直接；官网 transcript 仍待升级 |
| Coherent | COHR.US | 美股 | InP 6 英寸、EML、CW laser、photodiode、CPO/OCS | 全球主候选，缓解路径也在其手里 |
| Broadcom | AVGO.US | 美股 | AI networking、CPO、1.6T DSP、CW/EML lasers | 新增全球核心路线公司，不是单一短缺证明 |
| Ciena | CIEN.US | 美股 | Optical Networking、coherent modules、line systems、modems/pump demand | 系统级 demand read-through，注意和组件供应商分层 |
| Marvell | MRVL.US | 美股 | optical DSP、electro-optics、CPO/NPO、photonic fabric | 全球观察核心，需求/路线强，不是当前短缺证据 |
| Fabrinet | FN.US | 美股 | 高级光封装、模块装配和测试 | 量受益候选 |
| Corning | GLW.US | 美股 | 光连接、光纤、AI 数据中心光连接产能、CPO fiber ecosystem | 未来迁移观察增强 |
| POET Technologies | POET.US | 美股 | optical interposer、光引擎平台、light source | 未来迁移观察 |
| 中际旭创 | 300308.SZ | A 股 | 800G/1.6T 模块、硅光、规模交付、前端供应链锁定 | A 股基本面核心 |
| 新易盛 | 300502.SZ | A 股 | 800G/1.6T 模块、硅光、海外产能 | A 股业绩弹性核心，等 Q2 验证 |
| 天孚通信 | 300394.SZ | A 股 | 光器件、1.6T 光引擎、FAU/ELS/CPO 配套 | 次级跟踪核心，个别物料待拆 |
| 光迅科技 | 002281.SZ | A 股 | 光模块、光器件、硅光/CPO/NPO、海外产能 | 高交易弹性观察，定增增强中期产能/研发路径 |
| 源杰科技 | 688498.SH | A 股 | CW laser、EML/DFB 光芯片 | 需 200G EML/AI 客户硬证据 |
| 光库科技 | 300620.SZ | A 股 | 隔离器、铌酸锂、无源器件 | 观察 |
| 罗博特科 | 300757.SZ | A 股 | ficonTEC 光子封装/测试设备 | 未来迁移观察 |
| 太辰光 | 300570.SZ | A 股 | MT ferrule、连接器/精密连接件、FAU 观察 | 光连接高波动观察 |
| 光圣科技 | 6442.TW | 台股 | datacenter optics、合圣 FAU/ELS/CPO 零组件 | 台股重点观察 |
| 上诠 | 3363.TWO | 台股 | FAU/无源精密件、PIC 封装 | 台股观察 |
| 波若威 | 3163.TWO | 台股 | 光纤阵列/连接组件 | 台股观察 |
| 大立光 / 先进光 | 3008.TW / 3362.TW | 台股 | 微透镜阵列、FAU/fiber array、CPO 光学件 | 新增观察，仍为送样/认证阶段 |

## 下期默认跟踪问题

1. Lumentum Mizuho 2026-06-09 或后续官方 transcript 是否披露 EML/CW-DFB/pump/ELS 交期、allocation、订单可见度和 6 英寸 InP ramp？
2. Coherent 后续 10-Q/IR 是否把 6 英寸 InP 良率、产量目标转化为合格产能、客户认证、毛利和库存周转改善？
3. 新易盛 Q2 物料缓解是否在财报或投关记录中拆明具体物料，天孚个别物料是否有类别、缺口比例和客户影响？
4. Ciena 官方 replay/transcript 或后续 10-Q 是否确认 pump laser / modem / line-system 约束，并能否区分 EDFA/Raman pump、coherent modem 与数据中心模块光源？
5. FAU/fiber array、ELSFP liquid cooling、主动对准/测试设备是否从 Computex 展示转入客户认证、交期拉长、良率/返修或批量订单证据？
