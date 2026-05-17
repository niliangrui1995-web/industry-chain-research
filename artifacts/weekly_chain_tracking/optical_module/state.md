# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-05-17
最新报告：`artifacts/weekly_chain_tracking/optical_module/2026-05-17.md`
覆盖窗口：2026-05-10 至 2026-05-17

## 任务边界

本任务只跟踪光模块及其上游/中游关键环节。PCB/CCL、数据中心电力、机柜级液冷等只在影响光模块交付或需求时作为外部变量记录，不在本任务内展开；但光模块/光引擎自身热管理与液冷兼容纳入研究宇宙。

研究宇宙：
- 光模块整机：400G / 800G / 1.6T / 3.2T。
- 光引擎 / TOSA / ROSA / CPO / OCS / ELS。
- EML / DML / CW Laser / InP / GaAs / 硅光 / 薄膜铌酸锂。
- DSP / driver / TIA / CDR。
- FAU / MT ferrule / AWG / 透镜 / 微透镜阵列 / 耦合透镜 / isolator / Faraday rotator / connector。
- 数据中心光纤 / 跳线 / 光纤阵列 / PM fiber / MCF / 空芯光纤：仅限 AI 数据中心、CPO/ELS、光引擎或高密度光连接的明确传导，不展开通信用普通光纤大周期。
- 光模块/光引擎热管理与液冷兼容：IHS、cage、riding heatsink、TIM、cold plate interface、浸没兼容、热可靠性和返修。
- 封装耦合、主动对准、测试设备、代工和模块装配。

## 执行补充要求

- 每次更新报告时，必须对当前 `hard_bottleneck` 和 `soft_bottleneck` 预估可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A`，但要说明缺哪类证据。
- 每次不能只分析本期主深挖节点，还要扫描研究宇宙中的其他产业链环节，判断未来 6-24 个月哪些环节最可能出现新卡点或卡点迁移，并写明需求触发、供给滞后机制、可能时间、升级触发阈值、证据缺口和反转指标。
- 对话窗口摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`；其他内容只写入报告正文，不在窗口重复。
- 可以根据研究复杂度自主拆分任务并调用子代理进行并行研究；子代理默认使用超高智能。若子代理达到上限，应排队等待前面的子代理完成，再继续新建后续子代理。主代理负责最终证据分级、交叉验证、堵点判断、排名和报告合成。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| Lumentum 官方 transcript/IR Q&A 是否量化 EML、pump laser、CW laser 缺口？ | 未找到公司官网官方逐字稿。10-Q A 级确认需求超过供给并需 allocation；Motley Fool B 级转写称 pump laser 缺口大于 30% 且需要分配供给。 | 部分证实 |
| Coherent 6 英寸 InP ramp 是否有更细 capex、良率、客户认证和爬坡数据？ | 官方 release 确认强需求和扩产；B 级电话会转写称 6 英寸 InP 产能提前一季、2027 再翻倍，并已生产 EML/CW/PD。 | 部分证实 |
| 新易盛 Q2 物料缓解是否兑现，具体是哪类物料？ | 本窗口无新增官方拆分，仍沿用 4 月“Q2 起缓解、下半年趋稳”口径。 | 仍待跟踪 |
| 天孚通信个别物料缺料到底是什么？ | 5/14 正式投关确认个别物料仍阶段性缺货，但同时称 CPO 配套 FAU、ELS 外置光源等产品已稳定交付。 | 部分证实，仍未拆细 |
| Corning/NVIDIA 光连接扩产是否传导到 MT ferrule、FAU 和 A/台股公司？ | 光连接/光纤权重上升，但未证明 MT ferrule、FAU 或国内/台股公司已形成短缺。 | 观察增强 |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| 高端 EML / InP / CW laser / pump laser | 当前主堵点 | hard_bottleneck | AI 数据中心 800G/1.6T、CPO/OCS 与 scale-across 需求超过合格 InP/激光器可用产能；约束来自良率、可靠性认证、6 英寸 InP ramp、fab 转产和客户锁产能 | unchanged/worsened | Lumentum 10-Q demand outpacing supply/allocation；Lumentum Q3 EML/CW/pump；B 级 transcript 的 pump 缺口；Coherent 6 英寸 InP ramp | 2026H2 至 2027H1 偏紧；若 CPO/OCS 需求上修可延至 2027H2；置信度中高 | 不再 allocation；交期恢复；6 英寸合格产能兑现；模块厂预付款回落 | 找 Lumentum 官方 transcript；跟 Coherent 10-Q/IR |
| 光模块整机装配与关键原材料同步 | 当前软堵点 | soft_bottleneck | 高端模块订单强，需要关键物料、测试资源、客户认证和产线同步；但模块厂已通过备货、二供、保障协议缓解 | eased | 中际旭创 5/15 投关称供应链稳定、核心料备货/二供/保障协议；新易盛 4 月称 Q2 起缓解；Fabrinet datacom demand > shipments | 2026Q2-Q3 缓解，3-6 个月；置信度中 | Q2 交付兑现、预付款/存货改善、毛利不再靠紧缺 | 跟中际/新易盛 Q2 财报和预付款、存货、毛利 |
| 天孚光引擎个别物料 | 公司级软堵点/观察 | soft_bottleneck/watch | 个别未披露物料阶段性缺货影响生产组织；但 FAU/ELS 已披露稳定交付，不能直接升级为行业硬堵点 | evidence_refined | 天孚 5/14 投关：FAU/ELS 稳定交付，个别物料仍阶段性缺货 | N/A；缺具体物料、缺口比例、交期和客户影响；置信度低 | 公司披露缺料解除或拆清物料；1.6T 光引擎产量达预期 | 继续追问物料类别和是否影响 1.6T 光引擎 |
| 光连接/光纤/高密度连接器 | 边界内观察 | watch/possible regional soft | AI factory 光纤密度提升、CPO/ELS 光纤路由和 NVIDIA-Corning 长协可能造成区域性光纤/连接产能压力 | new/watch | Corning/NVIDIA 10x 光连接和 50%+ 光纤扩产；本周媒体称需求强和交期拉长；CPO/ELS 设计需要高密度光纤/PM fiber 连接 | N/A；缺官方单品交期、PM fiber/光纤阵列短缺和 A/台股传导证据 | Corning 扩产按期释放；客户不再锁产能；连接件/光纤阵列二供快速认证 | 跟 Corning 5/19 J.P. Morgan TMC transcript；跟 PM fiber/光纤阵列是否被点名 |
| FAU / MT ferrule / 微透镜 / 隔离器 / PM fiber | 未来迁移观察 | watch | CPO/ELS 提升耦合密度和无源精密件要求，但天孚称 FAU/ELS 稳定交付，缺行业交期/涨价证据 | downgraded_to_watch | 天孚 5/14 投关；FAU 市场资料仅作 B/C 背景 | N/A | 模块厂或无源件厂点名交期/涨价/良率 | 不作为当前硬堵点，继续观察 |
| 主动对准/耦合/测试设备 | 未来迁移观察 | watch | 1.6T/3.2T 与 CPO 多通道并行提高耦合精度和测试节拍要求 | upgraded_watch | Fabrinet 扩 clean-room/制造能力；罗博特科 H 股申请为资本市场事件，非短缺证据 | 2026H2-2027 可能升温 | 设备交期/耦合 CT/良率被点名 | 跟设备订单和交付周期 |
| 光模块/光引擎热管理与液冷兼容 | 未来迁移观察 | watch | 1.6T/3.2T 可插拔、CPO/OCS 和高密度交换机提高模块热流密度，可能把约束迁移到 IHS/cage/TIM/cold plate interface、浸没兼容和热可靠性 | new/watch | Molex 热管理报告与 CPO JDF 均提示高功耗光 I/O 和 CPO 光模块热路径需要重新设计；当前缺短缺或交付约束证据 | 2026H2-2028 可能升温 | 模块厂/交换机厂点名散热限制交付、液冷 OSFP/IHS/cage/TIM 交期拉长、CPO 因热可靠性影响 qualification | 风冷/散热结构满足 1.6T/3.2T TCO，液冷接口标准化且多供应商稳定供给 |
| DSP / driver / TIA / CDR | 战略节点，不是当前堵点 | rejected/watch | 先进制程和客户导入壁垒高，但未见交期、allocation 或模块厂点名短缺 | unchanged | 光迅称 DSP 主要外购；Broadcom/Marvell 产品节奏清晰 | N/A | 出现明确客户 allocation、交期拉长、模块厂点名电芯片短缺 | 等 3.2T/LPO/LRO 代际证据 |

## 候选观察池

| 候选节点 | 当前判断 | 需要验证的堵点问题 | 不可直接下结论的原因 |
|---|---|---|---|
| EML / 高速激光芯片 | 主堵点 | 200G per lane EML、CW laser、pump laser 的缺口比例、交期、良率和扩产兑现 | 有 A 级 allocation 与 B 级缺口口径，但单品缺口仍缺官方量化 |
| InP 衬底 / 外延 / 6 英寸平台 | 主堵点组成 | Coherent/Lumentum 6 英寸 ramp 是否转化为合格供给 | 扩产不等于可交付，需看良率、客户认证、毛利和库存周转 |
| CW / ELS / pump laser | 主堵点组成和未来迁移核心 | CPO/硅光/scale-across 是否形成独立短缺 | CPO/OCS 放量仍在早期，需订单、交期和收入单列 |
| 光模块整机与测试 | 软堵点缓解观察 | 中际/新易盛 Q2 交付、预付款、存货、毛利是否验证缓解 | 中际已给供应链稳定口径，不能继续简单升级 |
| FAU / MT ferrule / 微透镜 / 隔离器 | 观察 | CPO/ELS 是否拉长交期或导致良率瓶颈 | 天孚已称 FAU/ELS 稳定交付，缺行业短缺证据 |
| 主动对准 / 封装测试设备 | 观察增强 | 光引擎/CPO 量产后设备和良率是否拖累爬坡 | 当前无设备交期 A/B 证据 |
| 光连接/光纤/连接器 | 边界内观察 | Corning/NVIDIA 是否传导到 MT/FAU/连接器、PM fiber、光纤阵列和 A/台股公司 | 光纤扩产不等于模块上游单品短缺，必须看到高密度数据中心/CPO/ELS 场景证据 |
| 光模块/光引擎热管理与液冷兼容 | 新增观察 | 1.6T/3.2T、CPO/OCS 是否把卡点迁移到 IHS/cage/TIM/cold plate interface、浸没兼容、热可靠性和返修 | 机柜级液冷热度不能直接证明光模块液冷卡点，必须看到模块级交付/良率/认证约束 |
| SiPh / TFLN | 路线期权 | 是否从路线验证进入客户定点与批量出货 | 当前更多是平台/路线证据，不是供需缺口 |

## 本期主深挖与次级跟踪

- 主深挖：高端 EML / InP / CW laser / pump laser。
- 次级跟踪 1：光模块整机装配与关键原材料同步。
- 次级跟踪 2：FAU / ELS / 微透镜 / 隔离器等无源和光引擎组件。
- 次级跟踪 3：光连接/光纤、OCS/CPO、光模块/光引擎热管理、主动对准/测试和光引擎制造卡点迁移。

## 公司映射基线

| 公司 | ticker | 市场 | 当前角色 | 状态 |
|---|---|---|---|
| Lumentum | LITE.US | 美股 | EML、pump/narrow-linewidth laser、CW laser、OCS/CPO | 全球主候选 |
| Coherent | COHR.US | 美股 | InP 6 英寸、EML、CW laser、photodiode、CPO/OCS | 全球主候选 |
| Fabrinet | FN.US | 美股 | 高级光封装、模块装配和测试 | 量受益候选 |
| Corning | GLW.US | 美股 | 光连接、光纤、AI 数据中心光连接产能 | 光纤/光连接边界内观察 |
| POET Technologies | POET.US | 美股 | optical interposer、光引擎平台、light source | 未来迁移观察 |
| 中际旭创 | 300308.SZ | A 股 | 800G/1.6T 模块、硅光、规模交付、前端供应链锁定 | A 股基本面核心 |
| 新易盛 | 300502.SZ | A 股 | 800G/1.6T 模块、硅光、海外产能 | A 股业绩弹性核心 |
| 天孚通信 | 300394.SZ | A 股 | 光器件、1.6T 光引擎、FAU/ELS/CPO 配套 | 次级跟踪核心 |
| 光迅科技 | 002281.SZ | A 股 | 光模块、光器件、硅光/CPO/NPO 扩产 | 高交易弹性观察 |
| 源杰科技 | 688498.SH | A 股 | 激光芯片/EML 观察 | 需 200G EML/AI 客户硬证据 |
| 光库科技 | 300620.SZ | A 股 | 隔离器、铌酸锂、无源器件 | 观察 |
| 罗博特科 | 300757.SZ | A 股 | ficonTEC 光子封装/测试设备 | 未来迁移观察 |
| 太辰光 | 300570.SZ | A 股 | MT ferrule、连接器/精密连接件 | 观察 |
| 光圣科技 | 6442.TW | 台股 | 光收发/Datacenter optics | 台股观察 |
| 上诠 | 3363.TWO | 台股 | FAU/无源精密件 | 台股观察 |
| 波若威 | 3163.TWO | 台股 | 光纤阵列/连接组件 | 台股观察 |

## 下期默认跟踪问题

1. Lumentum 是否出现官方 transcript、会议 replay 或 IR 材料，能否把 pump/EML/CW 的 `>30%` 缺口从 B 级转为 A 级？
2. Coherent 10-Q 或官方 IR 是否确认 6 英寸 InP 提前一季、三类器件良率高于 3 英寸、首批 transceiver 出货等细节？
3. 新易盛 Q2 物料缓解是否在财报或投关记录中兑现，具体缓解的是光芯片、电芯片、无源件、PCB 还是测试资源？
4. 天孚通信“个别物料阶段性缺货”到底是哪一类，是否影响 1.6T 光引擎产量和毛利？
5. Corning 5/19 J.P. Morgan TMC 是否披露 AI 光连接订单、交期、产能释放时间，是否可传导到 MT ferrule、FAU、PM fiber、光纤阵列、连接器和 A/台股公司？
6. 1.6T/3.2T、CPO/OCS 是否出现模块级热管理或液冷兼容约束，例如 IHS/cage/TIM/cold plate interface 交期、热可靠性、浸没兼容或客户 qualification 问题？
