# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-05-24  
最新报告：`artifacts/weekly_chain_tracking/optical_module/2026-05-24.md`  
覆盖窗口：2026-05-17 至 2026-05-24

## 任务边界

本任务只跟踪光模块及其上游/中游关键环节。PCB/CCL、数据中心电力、机柜级液冷、CDU、冷板总成、光纤预制棒和普通通信用光缆只作为接口或外部变量；只有出现 A/B 级证据证明其直接限制光模块或光引擎交付、良率、客户认证或可靠性时，才纳入观察或深挖。

研究宇宙：
- 光模块整机：400G / 800G / 1.6T / 3.2T。
- 光引擎 / TOSA / ROSA / CPO / OCS / ELS。
- EML / DML / CW Laser / InP / GaAs / 硅光 / 薄膜铌酸锂。
- DSP / driver / TIA / CDR。
- FAU / MT ferrule / AWG / 透镜 / 微透镜阵列 / 耦合透镜 / isolator / Faraday rotator / connector。
- 数据中心光纤 / 跳线 / 光纤阵列 / PM fiber / MCF / 空芯光纤：仅限 AI 数据中心、CPO/ELS、光引擎或高密度光连接的明确传导。
- 光模块/光引擎热管理与液冷兼容：IHS、cage、riding heatsink、TIM、cold plate interface、浸没兼容、热可靠性和返修。
- 封装耦合、主动对准、测试设备、代工和模块装配。

## 执行补充要求

- 每次更新报告时，必须对当前 `hard_bottleneck` 和 `soft_bottleneck` 预估可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A`，并说明缺哪类证据。
- 每次必须扫描未进入本期主深挖的其他产业链环节，判断未来 6-24 个月最可能出现新卡点或卡点迁移的环节，并写明需求触发、供给滞后机制、可能时间、升级触发阈值、证据缺口和反转指标。
- 对话窗口摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`。
- 子代理输出只能作为信息采集，主代理必须负责最终证据分级、交叉验证、堵点判断、排名和报告合成。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| Lumentum 官方 transcript/IR Q&A 是否量化 EML、pump laser、CW laser 缺口？ | 未找到官网官方逐字稿。2026-05-18 J.P. Morgan transcript B 级进一步确认供需失衡、NVIDIA 锁定大量 InP 供给、5th InP fab 约两年出产、6 英寸仍有挑战。 | 部分证实，主堵点增强；仍缺 A 级 transcript |
| Coherent 6 英寸 InP ramp 是否有更细 capex、良率、客户认证和爬坡数据？ | 10-Q A 级确认强需求、Sherman InP 扩产、industry-wide shortage、NVIDIA purchase commitment/capacity rights；6 英寸 EML/CW/PD 良率高于 3 英寸仍来自 B 级电话会转写。 | A 级确认 shortage/扩产，良率细节仍 B |
| 新易盛 Q2 物料缓解是否兑现，具体是哪类物料？ | 本窗口无新易盛新增官方拆分，仍沿用 4 月“Q2 起缓解、下半年趋稳”口径。 | 仍待跟踪 |
| 天孚通信个别物料缺料到底是什么？ | 本窗口未新增拆分；维持 5/14 投关：FAU/ELS 稳定交付，个别物料阶段性缺货。 | 部分证实，仍未拆细 |
| Corning/NVIDIA 光连接扩产是否传导到 MT ferrule、FAU、PM fiber、光纤阵列和 A/台股公司？ | Corning J.P. Morgan 摘要显示 hyperscaler 长协、prepayment/minimum capacity commitments、2027 photonics 初始收入，但没有单品短缺或 A/台股传导证据。 | 观察增强，未升级当前堵点 |
| 模块级热管理或液冷兼容是否限制 1.6T/3.2T、CPO/OCS？ | 未发现 A/B 级证据证明 IHS/cage/TIM/cold plate interface、浸没兼容或热可靠性限制交付、良率或认证。 | 仍为 watch |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| 高端 EML / InP / CW / pump / ELS | 当前主堵点 | hard_bottleneck | 1.6T/3.2T、CPO/OCS、optical scale-up/scale-across 需求超过合格 InP/高功率光源可用产能；约束在 6 英寸良率、新 fab 两年周期、老化测试、客户认证和 NVIDIA capacity rights | worsened/validated | NVIDIA FY2027 Q1 networking revenue 148 亿美元，同比 +199%；Lumentum 5/18 transcript 称无法满足 NVIDIA 单一客户需求且新增 InP fab 约两年；Coherent 10-Q 写明 Sherman InP 扩产应对 industry-wide shortage | EML/InP：2026H2-2027H1；CW/pump/ELS/CPO：可能 2027H2-2028H1；置信度中高 | allocation 解除、交期恢复；6 英寸和新 fab 合格产能兑现；NVIDIA 不再追加 capacity rights；模块厂预付款和毛利回落 | 找 Lumentum 官网 transcript；跟 Coherent 6 英寸良率/产量官方化 |
| 光模块整机装配与关键原材料同步 | 当前软堵点 | soft_bottleneck | 模块产线需要光芯片、电芯片、无源件、PCB、测试资源和客户认证同步；模块厂通过备货、二供、保障协议和海外产能缓解 | eased/unchanged | 中际 5/15 投关供应链稳定；光迅 5/21 投关需求旺盛和东南亚产能；无新增整机缺料证据 | 2026Q2-Q3 继续缓解，约 3-6 个月；置信度中 | Q2/Q3 交付兑现、预付款和存货周转改善、毛利不靠紧缺 | 跟新易盛/中际 Q2 财报和物料拆分 |
| 天孚光引擎个别物料 | 公司级软堵点/观察 | soft_bottleneck/watch | 个别未披露物料阶段性缺货影响生产组织；FAU/ELS 已披露稳定交付，不能直接升级为行业硬堵点 | unchanged | 天孚 5/14 投关：FAU/ELS 稳定交付，个别物料仍阶段性缺货 | N/A；缺具体物料、缺口比例、交期和客户影响；置信度低 | 公司披露缺料解除或拆清物料；1.6T 光引擎产量达预期 | 继续追问物料类别和是否影响 1.6T 光引擎 |
| 光连接/光纤/高密度连接 | 边界内观察 | watch/possible future soft | AI factory 光密度提升和 hyperscaler 长协可能造成 fiber/cable/connectivity 专用产能压力，并向高精密连接件传导 | upgraded_watch | Corning/NVIDIA 10x connectivity、50%+ fiber 扩产；Corning J.P. Morgan 摘要提示 prepayment/minimum capacity | 当前 N/A；未来 2026H2-2028 观察；置信度中 | Corning 扩产按期释放，客户不再锁产能，连接件二供快速通过认证 | 跟 Corning 官方 transcript；跟 MT/FAU/PM fiber/fiber array 单品传导 |
| FAU / MT ferrule / 微透镜 / 隔离器 / PM fiber | 未来迁移观察 | watch | CPO/ELS 提升耦合密度和无源精密件要求，但天孚称 FAU/ELS 稳定交付，缺行业交期/涨价证据 | unchanged | 天孚 5/14 投关；本周无单品短缺 A/B 证据 | N/A | 模块厂或无源件厂点名交期/涨价/良率 | 不作为当前硬堵点，继续观察 |
| 主动对准/耦合/测试设备 | 未来迁移观察 | watch_to_soft | 1.6T/3.2T 与 CPO 多通道并行提高耦合精度、测试节拍和 known-good-die 要求 | unchanged/upgraded_watch | Lumentum/Coherent/GF/POET 路线支持复杂度；缺设备交期证据 | 2026H2-2027 可能升温；置信度中 | 设备交期/耦合 CT/良率被点名 | 跟设备订单、交付周期和模块厂良率 |
| 光模块/光引擎热管理与液冷兼容 | 未来迁移观察 | watch | 1.6T/3.2T、CPO 和高密度交换机提高 IHS/cage/TIM/cold plate interface、浸没兼容和热可靠性要求 | unchanged | 当前缺交付、良率或客户认证受限 A/B 证据 | watch，2026H2-2028；置信度低中 | 模块厂/交换机厂点名热可靠性或液冷兼容限制 qualification/交付 | 风冷或标准液冷接口满足 TCO，多供应商稳定交付 |
| DSP / driver / TIA / CDR | 战略节点，不是当前堵点 | rejected/watch | 先进制程和客户导入壁垒高，但未见交期、allocation 或模块厂点名短缺 | unchanged | 光迅称 DSP 主要外购；Broadcom/Marvell 路线清晰；无短缺证据 | N/A | 出现明确客户 allocation、交期拉长、模块厂点名电芯片短缺 | 等 3.2T/LPO/LRO 代际证据 |

## 候选观察池

| 候选节点 | 当前判断 | 需要验证的堵点问题 | 不可直接下结论的原因 |
|---|---|---|---|
| EML / 高速激光芯片 | 主堵点 | 200G/400G lane EML 缺口比例、交期、良率和扩产兑现 | A/B 证据支持供给缺口，但单品比例仍缺官方量化 |
| InP 衬底 / 外延 / 6 英寸平台 | 主堵点组成 | Coherent/Lumentum 6 英寸 ramp 是否转化为合格供给 | 扩产不等于可交付，需良率、客户认证、毛利和库存周转 |
| CW / ELS / pump laser | 主堵点组成和未来迁移核心 | CPO/SiPh/scale-up 是否形成独立短缺 | 需求上修明确，但订单/交期/收入单列仍不完整 |
| 光模块整机与测试 | 软堵点缓解观察 | 中际/新易盛 Q2 交付、预付款、存货、毛利是否验证缓解 | 中际已给供应链稳定口径，不能继续简单升级 |
| FAU / MT ferrule / 微透镜 / 隔离器 | 观察 | CPO/ELS 是否拉长交期或导致良率瓶颈 | 天孚已称 FAU/ELS 稳定交付，缺行业短缺证据 |
| 主动对准 / 封装测试设备 | 观察增强 | 光引擎/CPO 量产后设备和良率是否拖累爬坡 | 当前无设备交期 A/B 证据 |
| 光连接/光纤/连接器 | 边界内观察 | Corning/NVIDIA 是否传导到 MT/FAU/连接器、PM fiber、光纤阵列和 A/台股公司 | 光纤扩产不等于模块上游单品短缺，必须看到高密度数据中心/CPO/ELS 场景证据 |
| 光模块/光引擎热管理与液冷兼容 | 观察 | 是否把卡点迁移到 IHS/cage/TIM/cold plate interface、浸没兼容、热可靠性和返修 | 机柜级液冷热度不能直接证明模块级卡点 |
| SiPh / TFLN | 路线期权 | 是否从路线验证进入客户定点与批量出货 | 当前更多是平台/路线证据，不是供需缺口 |

## 本期主深挖与次级跟踪

- 主深挖：高端 EML / InP / CW / pump / ELS。
- 次级跟踪 1：光模块整机装配与关键原材料同步。
- 次级跟踪 2：光连接/光纤/高密度连接。
- 次级跟踪 3：CPO/OCS 光引擎、主动对准/测试、模块/光引擎热管理迁移。

## 公司映射基线

| 公司 | ticker | 市场 | 当前角色 | 状态 |
|---|---|---|---|
| Lumentum | LITE.US | 美股 | EML、InP、pump/narrow-linewidth laser、CW/ELS、OCS/CPO | 全球主候选，供需缺口最直接 |
| Coherent | COHR.US | 美股 | InP 6 英寸、EML、CW laser、photodiode、CPO/OCS | 全球主候选，缓解路径也在其手里 |
| Fabrinet | FN.US | 美股 | 高级光封装、模块装配和测试 | 量受益候选 |
| Corning | GLW.US | 美股 | 光连接、光纤、AI 数据中心光连接产能 | 未来迁移观察增强 |
| POET Technologies | POET.US | 美股 | optical interposer、光引擎平台、light source | 未来迁移观察 |
| 中际旭创 | 300308.SZ | A 股 | 800G/1.6T 模块、硅光、规模交付、前端供应链锁定 | A 股基本面核心 |
| 新易盛 | 300502.SZ | A 股 | 800G/1.6T 模块、硅光、海外产能 | A 股业绩弹性核心 |
| 天孚通信 | 300394.SZ | A 股 | 光器件、1.6T 光引擎、FAU/ELS/CPO 配套 | 次级跟踪核心 |
| 光迅科技 | 002281.SZ | A 股 | 光模块、光器件、硅光/CPO/NPO、海外产能 | 高交易弹性观察 |
| 源杰科技 | 688498.SH | A 股 | CW laser、EML/DFB 光芯片 | 需 200G EML/AI 客户硬证据 |
| 光库科技 | 300620.SZ | A 股 | 隔离器、铌酸锂、无源器件 | 观察 |
| 罗博特科 | 300757.SZ | A 股 | ficonTEC 光子封装/测试设备 | 未来迁移观察 |
| 太辰光 | 300570.SZ | A 股 | MT ferrule、连接器/精密连接件 | 观察 |
| 光圣科技 | 6442.TW | 台股 | 光收发/Datacenter optics | 台股观察 |
| 上诠 | 3363.TWO | 台股 | FAU/无源精密件 | 台股观察 |
| 波若威 | 3163.TWO | 台股 | 光纤阵列/连接组件 | 台股观察 |

## 下期默认跟踪问题

1. Lumentum 是否发布官网版 J.P. Morgan transcript/replay 或 IR 摘要，能否把 InP/EML/CW/pump/ELS 缺口从 B 级 transcript 提升为 A 级管理层材料？
2. Coherent 是否在后续 IR 进一步拆出 6 英寸 InP 的合格产能、良率、客户认证和 CPO/CW revenue ramp？
3. 新易盛 Q2 物料缓解是否在财报或投关记录中兑现，具体缓解光芯片、电芯片、无源件、PCB 还是测试资源？
4. 天孚通信“个别物料阶段性缺货”到底是哪一类，是否影响 1.6T 光引擎产量和毛利？
5. Corning 官方 transcript 是否披露 optical connectivity/fiber 的客户 minimum capacity、prepayment、产能释放节奏，是否传导到 MT ferrule、FAU、PM fiber、fiber array 和 A/台股公司？
6. 1.6T/3.2T、CPO/OCS 是否出现模块级热管理、主动对准/测试节拍、液冷兼容或光引擎可靠性约束的 A/B 级证据？
