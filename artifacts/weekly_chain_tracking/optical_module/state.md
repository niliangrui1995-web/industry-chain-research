# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-07-03（A 股公司跟踪交易与治理边界最小同步）
最新报告：`artifacts/weekly_chain_tracking/optical_module/2026-06-28.md`
覆盖窗口：2026-06-21 至 2026-06-28

2026-07-03 A 股公司跟踪最小同步：中际旭创 300308.SZ 新增两笔平价大宗交易，只提高高价位机构换手观察优先级，不证明 1.6T/800G、硅光、客户需求、上游物料或毛利率兑现；东山精密 002384.SZ 因日价格振幅 18.85% 上龙虎榜，属于索尔思/AI PCB 预期下的交易分歧和拥挤度信号，不等于光模块、AI PCB 或索尔思经营基本面被证实或证伪；云南锗业 002428.SZ 高管离任为治理和职责变化，公告称不影响正常生产经营，仍不构成 InP/GaAs 客户、订单、良率、6 英寸稳定量产、出口许可或利润兑现证据。

## 任务边界

本任务只跟踪光模块及其上游/中游关键环节。PCB/CCL、数据中心电力、机柜级液冷、CDU、冷板总成、光纤预制棒和普通通信用光缆只作为接口或外部变量；只有出现 A/B 级证据证明其直接限制光模块或光引擎交付、良率、客户认证或可靠性时，才纳入观察或深挖。

研究宇宙：

- 光模块整机：400G / 800G / 1.6T / 3.2T。
- 光引擎 / TOSA / ROSA / CPO / OCS / ELS。
- EML / DML / CW Laser / CW-DFB LD / InP / GaAs / 硅光 / 薄膜铌酸锂。
- DSP / driver / TIA / CDR。
- FAU / MT ferrule / MPO / Receptacle / AWG / 透镜 / 微透镜阵列 / 耦合透镜 / isolator / Faraday rotator / connector。
- 数据中心光纤 / 跳线 / 光纤阵列 / PM fiber / MCF / 空芯光纤：仅限 AI 数据中心、CPO/ELS、光引擎或高密度光连接的明确传导。
- 光模块/光引擎热管理与液冷兼容：IHS、cage、riding heatsink、TIM、cold plate interface、浸没兼容、ELSFP thermal stability、热可靠性和返修。
- 封装耦合、主动对准、WLBI/OWAT、光电联合测试、测试设备、代工和模块装配。

## 执行补充要求

- 每次更新报告时，必须对当前 `hard_bottleneck` 和 `soft_bottleneck` 预估可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A`，并说明缺哪类证据。
- 每次必须扫描未进入本期主深挖的其他产业链环节，判断未来 6-24 个月最可能出现新卡点或卡点迁移的环节，并写明需求触发、供给滞后机制、可能时间、升级触发阈值、证据缺口和反转指标。
- 对话窗口摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`。
- 子代理输出只能作为信息采集，主代理必须负责最终证据分级、交叉验证、堵点判断、排名和报告合成。

## 当前主结论

- 当前主硬堵点仍为 `InP substrate / epiwafer / 6 英寸合格 InP 平台 / EML / CW-DFB / UHP pump / ELS`。堵点定义是短期需求超过合格供给、可用产能、良率爬坡、老化测试和客户认证能力；高壁垒、高毛利、高 HHI 或股票热度本身不构成堵点。
- 2026-06-28 本轮最强增量来自 InP 链条的 B 级产业媒体证据：DigiTimes 6/22 报道 InP 出口缓解不足，6/23 指向 6 英寸 InP wafer 供给墙，6/25 指出 IntelliEPI 仍受 InP substrate shortage 约束。该证据强化主硬堵点，但不能替代 AXT/JX/Coherent/Lumentum/客户的 A 级闭环。
- EML/InP 偏紧预计持续至 `2026H2-2027H1`，置信度中高；CW-DFB/UHP/ELS 若随 2027-2028 CPO/NPO/scale-up 光互连放量，尾部可能延至 `2027H2-2028H1`，置信度中；长期 InP 衬底若 JX/Coherent/Lumentum/非中国供给扩产并通过客户认证，`2028-2030` 起缓解概率上升。
- 光模块整机装配与关键原材料同步维持 `soft_bottleneck/eased`，预计 `2026Q2-Q3` 继续缓解。本窗口没有中际、新易盛、天孚、光迅、东山等披露新的交付受限、关键料短缺、客户认证失败或订单延期。
- 高密度 data-center fiber/cable/connectivity 维持边界内 `soft_bottleneck/watch`。长飞光纤异动公告承认市场关注 AI 数据中心光纤光缆价格波动，但同时提示经营正常、行业环境未发生重大变化，业绩影响需要结合市场环境和业务结构判断；不能外推为 FAU/MT/PM fiber/fiber array 当前短缺。
- 光库科技并购安捷讯修订稿把 `光无源器件 / FAU / MT / MPO / Receptacle / Lens / 高速光互联组件` 的 A 股映射增强，但这是并购和产品布局证据，不是交期、涨价、良率或客户排队证据。
- 罗博特科 H 股备案获证监会确认，但没有 CPO-specific 订单、客户采购路径、设备交期、验收收入或毛利证据，仍只能作为未来设备迁移观察。
- 源杰科技、云南锗业本周官方风险/异动公告强化交易热度和估值风险，均不能升级为主候选或经营兑现证据。

## 本期主深挖与次级跟踪

- 主深挖：`InP substrate / epiwafer / 6 英寸合格 InP 平台` 对 EML、CW-DFB、UHP pump、ELS 和 CPO/SiPh 外置光源的约束。
- 次级跟踪 1：`FAU / fiber array / MT ferrule / MPO / Receptacle / Lens / 光无源器件`，重点吸收光库科技并购安捷讯和长飞光纤异动公告边界。
- 次级跟踪 2：`A 股光芯片 / InP 材料 / 高密连接候选公司的交易风险边界`，重点看源杰科技、云南锗业、长飞光纤。
- 次级跟踪 3：`CPO 制造测试设备 / 主动对准 / WLBI / OWAT`，重点看罗博特科 H 股备案是否仅为融资路径，而不是订单兑现。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| Coherent/JX/IQE/Tower 扩产是否披露客户认证、产能释放、良率、订单或毛利兑现？ | 未见新增 A 级兑现；既有官方扩产路径仍有效，但不解除 2026-2027 短缺。 | 仍待跟踪 |
| Lumentum 是否发布可引用的 Mizuho 官方逐字稿/PDF 或后续 SEC 业务披露？ | 未发现 Lumentum 官网逐字稿、PDF 或 6/21 后 SEC 业务披露。 | 仍待跟踪 |
| AXT 和中国 InP 出口许可是否出现官方进展，DigiTimes 首批发货是否被验证？ | AXT 官方层面无新披露；DigiTimes 本周连续报道出口缓解不足和 6 英寸供给墙。 | B 级强化，未 A 级闭环 |
| 罗博特科/ficonTEC 是否出现 CPO-specific 订单、客户采购路径、交期排队、验收收入或毛利验证？ | 新增 H 股备案公告，未披露 CPO 订单、验收收入或毛利。 | 资本路径增强，商业化仍未证实 |
| 东山精密索尔思扩建是否披露审批、资金、设备、客户、产能、良率和毛利率量化？ | 本窗口 CNINFO/公司名检索未见新增相关公告。 | unchanged |
| 中际、新易盛、天孚、源杰、太辰光是否在 Q2 财报/投关中拆出客户、订单、交付、毛利、缺料或二供认证？ | 中际、天孚、太辰光无新增公告；新易盛新增董事更换/股东会公告，非经营证据；源杰新增风险提示公告。 | 多数仍待跟踪；源杰风险边界增强 |
| Corning/Amazon/NVIDIA 光连接长协、长飞光纤 AI 数据中心光纤价格线索是否披露 minimum capacity、prepayment、交付时间和单品传导？ | 长飞承认价格关注度但称经营正常、影响需看业务结构；未披露 capacity/prepayment/交付时间/单品传导。 | 观察增强但不升级短缺 |
| FAU/fiber array、MT ferrule、PM fiber、ELSFP thermal、主动对准/WLBI/测试设备是否出现交期、涨价、订单排队、良率或返修证据？ | 光库并购安捷讯增强 FAU/MT/MPO/Lens 映射；未证明短缺。 | future watch 增强 |
| 2026-06-22 邮件四条 C/lead 是否能升级？ | 光模块散单涨价、新易盛 DSP 5100 万颗、中际出口 80 亿、MPO/FAU 保底扩产仍未 A/B 闭环。 | 维持 C/lead |
| 云南锗业 InP 是否出现客户、订单、良率、6 英寸稳定量产、出口许可或利润兑现？ | 新增异动公告再次确认化合物半导体材料收入占比 12.93%、毛利占比 14.29%，PE/PB 显著高于行业。 | 交易风险增强，经营兑现未升级 |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| InP substrate / epiwafer / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS | 当前主堵点 | hard_bottleneck | 衬底/外延/6 英寸良率、老化测试、客户认证、出口许可、锁产能共同约束高端光源可交付供给 | unchanged/evidence_strengthened | DigiTimes 本周 InP 出口缓解不足、6 英寸供给墙、IntelliEPI 受 substrate shortage；Coherent/JX/IQE/Tower 既有官方扩产路径 | EML/InP：2026H2-2027H1；CW/ELS/UHP 尾部：2027H2-2028H1；长期衬底缓解看 2028-2030；置信度中高/中 | 许可正常化、6 英寸良率/认证兑现、交期/allocation/价格回落、客户停止锁产能 | 跟 AXT/JX/Coherent/Lumentum/客户 A 级闭环 |
| 光模块整机装配与关键原材料同步 | 当前软堵点 | soft_bottleneck | 模块产线需光芯片、电芯片、无源件、PCB、测试资源和客户认证同步；上游主堵点仍可传导 | unchanged/eased | 中际/天孚/光迅/东山等 CNINFO 无经营新增；新易盛仅治理公告；既有 Q2 缓解口径未被推翻 | 2026Q2-Q3 继续缓解；置信度中 | Q2/Q3 交付兑现、毛利和存货周转改善；若模块厂重提缺料/测试短缺则反转 | 跟 Q2/Q3 财报、投关、ASP/毛利/存货 |
| 数据中心 optical fiber / cable / connectivity | 边界内观察增强 | soft_bottleneck/watch | AI 数据中心光连接密度上升，客户长协和专用产能可能使合格 fiber/cable/connectivity 紧张 | unchanged/watch | 长飞异动公告承认 AI 数据中心光纤光缆价格关注度，但称经营正常、影响需看业务结构；Corning/Amazon/NVIDIA 既有合作 | 当前 N/A；0-12 个月可能升温；置信度中 | minimum capacity/prepayment、交期拉长、订单/毛利拆分、FAU/MT/PM fiber 传导；若扩产释放则反转 | 跟长飞/Corning/Fujikura/Sumitomo 订单、交期、合同细节 |
| FAU / fiber array / MT / MPO / Receptacle / Lens | 未来迁移观察 | watch_to_soft | CPO/ELS 通道数和 fiber attach 密度上升，提高精密连接和低损耗耦合门槛 | evidence_up_but_not_current_bottleneck | 光库并购安捷讯修订稿确认光无源器件、FAU、MT、MPO、Lens、高速光互联产品矩阵 | 当前 N/A；2026H2-2028 watch；置信度中低 | 客户定点、量产订单、交期拉长、涨价、良率/返修压力；二供或 CPO 延后则降级 | 跟安捷讯客户/订单/毛利/交期和并购进展 |
| 主动对准 / CPO 制造测试设备 | 未来迁移观察核心 | watch_to_soft | CPO/硅光光引擎需要更高精度对准、晶圆级/芯片级测试和验收；商业化订单仍未落地 | unchanged | 罗博特科 H 股备案获证监会确认；既有 ficonTEC/NVIDIA 合作仍缺订单/收入 | 当前 N/A；2026H2-2027 watch；置信度中低 | CPO-specific 订单、设备排队、验收收入、良率瓶颈；若无订单或 CPO 延后则降级 | 跟罗博特科港股进展、募资用途、订单、验收收入 |
| DSP / driver / TIA / CDR | 战略节点，不是当前堵点 | watch/rejected as current bottleneck | 需求和代际升级明确，但无交期、allocation 或模块厂点名短缺 | unchanged_watch；新易盛 5100 万颗仍 C/lead | Broadcom/Marvell 既有路线；本窗口无新 A/B 短缺证据 | N/A；未来 2027-2028 观察；置信度低中 | 模块厂点名电芯片短缺、客户 allocation、交期拉长；多源稳定供给则维持 strategic node | 核验 2027 DSP 订单数量、供应商分配、交期/allocation |

## 候选观察池

| 候选节点 | 当前判断 | 需要验证的堵点问题 | 不可直接下结论的原因 |
|---|---|---|---|
| InP 衬底 / 外延 / 6 英寸平台 | 主堵点组成，本期主深挖 | 出口许可、6 英寸良率、非中国产能、客户二供认证、交期和价格 | 本周 B 级强化，但缺 AXT/客户官方闭环 |
| EML / 高速激光芯片 | 主堵点 | 200G/lane EML 缺口比例、交期、老化测试和扩产兑现 | A/B 支持偏紧，但单品比例仍缺官方量化 |
| CW-DFB / UHP pump / ELS | 主堵点组成和未来迁移核心 | CPO/SiPh/scale-up/scale-across 是否形成独立短缺 | 长协/扩产支持供需紧，但订单、交期、收入单列不完整 |
| 主动对准 / 封装测试设备 / WLBI | 未来迁移观察 | CPO/光引擎量产后设备、测试节拍和良率是否拖累爬坡 | 罗博特科新增 H 股备案，不是订单/收入证据 |
| FAU / fiber array / MT / MPO / Lens / Receptacle | 观察增强 | CPO/ELS 是否拉长交期或导致良率瓶颈 | 光库/安捷讯证明暴露，不证明当前短缺 |
| 光连接/光纤/连接器 | 未来迁移增强 | Corning/Amazon/NVIDIA 长协和长飞光纤价格关注度是否传导到 MT/FAU/连接器、PM fiber、光纤阵列 | 普通光纤上行不等于模块上游单品短缺 |
| 光模块/光引擎热管理与液冷兼容 | 观察 | 是否迁移到 IHS/cage/TIM/cold plate interface、ELSFP 稳定光源、浸没兼容、热可靠性和返修 | 机柜级液冷热度不能直接证明模块级卡点 |
| SiPh / TFLN | SiPh 路线期权增强，TFLN 仍 watch/rejected | 是否从路线验证进入客户定点与批量出货 | 当前更多是平台/路线证据，不是供需缺口 |

## 公司映射基线

| 公司 | ticker | 市场 | 当前角色 | 状态 |
|---|---|---|---|
| Coherent | COHR.US | 美股 | 6 英寸 InP、EML、CW laser、photodiode、CPO/OCS、PM fiber/FAU | 全球主候选，也是主堵点缓解方 |
| Lumentum | LITE.US | 美股 | EML、InP、UHP pump、CW/ELS、OCS/CPO | 全球主候选；Mizuho replay 不升交期/锁产能 A 级 |
| JX Advanced Metals | 5016.T | 日股 | InP substrate | 长期衬底缓解核心，FY2030 7-10x 目标 |
| IQE | IQE.L | 英股 | InP epiwafer | Tower 多年供应协议强化外延片锁供 |
| Tower Semiconductor | TSEM.US | 美股 | InP photonic devices / OCS modulator | SiPh/OCS 代工路径观察 |
| Corning | GLW.US | 美股 | 光连接、光纤、AI 数据中心 optical connectivity、FAU | 未来迁移观察增强 |
| 中际旭创 | 300308.SZ | A 股 | 800G/1.6T 模块、硅光、规模交付、前端供应链锁定 | A 股基本面核心；本窗口无新增经营公告 |
| 新易盛 | 300502.SZ | A 股 | 800G/1.6T 模块、硅光、海外产能 | A 股业绩弹性核心；本窗口仅治理公告，DSP 5100 万颗仍 C/lead |
| 天孚通信 | 300394.SZ | A 股 | 光器件、1.6T 光引擎、FAU/ELS/CPO 配套 | 次级跟踪核心，个别物料待拆 |
| 光库科技 | 300620.SZ | A 股 | 光无源器件、FAU/MT/MPO/Lens、TFLN | 本周并购安捷讯增强 future watch，但不证明短缺 |
| 东山精密 | 002384.SZ | A 股 | 索尔思光芯片/光模块、EML 与硅光并行、AI PCB 协同 | A 股垂直一体化强观察；本窗口无新增 |
| 源杰科技 | 688498.SH | A 股 | CW laser、EML/DFB 光芯片 | 2026-06-23 风险提示强化估值和客户导入不确定性，降为 watch |
| 云南锗业 | 002428.SZ | A 股 | InP/GaAs 晶片材料观察 | 2026-06-25 异动公告强化估值/业绩风险，经营兑现未升级 |
| 长飞光纤 | 601869.SH | A 股 | 数据中心光纤/光缆、空芯/多芯光纤观察 | 2026-06-24 异动公告确认价格关注度但影响不确定，不升级短缺 |
| 光迅科技 | 002281.SZ | A 股 | 光模块、光器件、硅光/CPO/NPO、海外产能 | 高交易弹性观察，需订单/收入验证 |
| 长光华芯 | 688048.SH | A 股 | 高功率半导体激光平台、光通信 EML/DFB/VCSEL/CW DFB 观察 | `watch_to_soft/evidence_gap_card`，不能等同 InP/CW 主堵点 |
| 罗博特科 | 300757.SZ | A 股 | ficonTEC 光子封装/测试设备 | H 股备案增强资本路径；仍无订单/收入 |
| 鼎通科技 | 688668.SH | A 股 | CAGE/高速通讯连接器结构件、液冷散热器观察 | 可转债进入发行进展，仍不等于客户订单或毛利兑现 |
| 太辰光 | 300570.SZ | A 股 | MT ferrule、连接器/精密连接件、FAU 观察 | 光连接高波动观察池 |
| 光圣科技 | 6442.TW | 台股 | datacenter optics、合圣 FAU/ELS/CPO 零组件 | 台股重点观察，仍为认证/试产阶段 |
| 上诠 | 3363.TWO | 台股 | FAU/无源精密件、PIC 封装 | 台股观察 |
| 波若威 | 3163.TWO | 台股 | 光纤阵列/连接组件 | 台股观察 |

## 本期三类排名快照

- 基本面质量：`Coherent > Lumentum > Corning > 中际旭创 > 新易盛 > 光库科技 > 天孚通信`。
- 业绩弹性：`东山精密/索尔思 > Coherent > Lumentum > 新易盛 > 光库科技 > 源杰科技 watch > 罗博特科 option`。
- 交易弹性：`源杰科技 > 云南锗业 > 长飞光纤 > 光库科技 > 罗博特科 > 东山精密 > 新易盛 > 中际旭创 > 天孚通信`。本排名仅使用本窗口官方风险/异动公告披露的 PE/PB、涨幅和事件信息作交易风险校准；未取得稳定 A 股行情工具的个股最新价格、市值、PE/PB、换手率均保持 `N/A`。

## 本期 A 股披露与行情辅助

| 项目 | 结果 | 处理 |
|---|---|---|
| CNINFO 2026-06-21~2026-06-28 | 中际、天孚、光迅、东山、太辰光、长光华芯等无新增经营相关公告；新易盛为治理公告；源杰、长飞、云南为风险/异动公告；光库为并购修订稿；罗博特科为 H 股备案；鼎通为可转债发行进展 | 经营短缺不升级；风险边界和 future watch 更新 |
| 源杰科技风险提示 | 5/18~6/22 股价累计涨幅 74.16%，滚动 PE 655.12 倍，客户导入/量产/项目实施存在不确定 | 交易弹性高但基本面证据缺，降为 watch |
| 云南锗业异动公告 | PE/PB 极高，2025 化合物半导体材料收入约 1.38 亿元、占营收 12.93%、毛利占比 14.29%，InP 供需影响不确定 | InP 材料观察，不升级主候选 |
| 长飞光纤异动公告 | AI 数据中心光纤光缆价格关注度高，但经营正常、行业环境未发生重大变化，影响需看业务结构 | 只强化边界内 watch，不升级短缺 |
| 行情辅助 | 当前未取得稳定 A 股行情工具；除官方风险公告披露的 PE/PB/涨幅外，最新价格、市值、PE/PB、换手率为 N/A | 行情不作为产业证据 |

## 下期默认跟踪问题

1. DigiTimes InP 供给墙线索能否被 AXT、JX、Coherent、Lumentum、客户或监管许可的 A 级材料验证。
2. Coherent/JX/IQE/Tower/Lumentum 扩产是否披露良率、客户认证、产能释放、订单、毛利或库存周转。
3. Lumentum 是否发布可引用的 Mizuho 官方逐字稿/PDF 或后续 SEC 披露。
4. 光库科技并购安捷讯是否披露 FAU/MT/MPO/Lens 的客户、订单、毛利、产能和交期；是否只是产品矩阵增强。
5. 长飞/Corning/Amazon/NVIDIA 光连接线索是否披露 minimum capacity、prepayment、交付时间、收入拆分、毛利率和向 FAU/MT/PM fiber/fiber array 的传导。
6. 罗博特科/ficonTEC 是否出现 CPO-specific 在手订单、客户采购路径、交期排队、验收收入或毛利验证。
7. 中际、新易盛、天孚、东山、源杰、太辰光是否在 Q2 财报/投关中拆出客户、订单、交付、毛利、缺料或二供认证。
8. 继续复核光模块散单涨价、新易盛 2027 DSP 5100 万颗/Broadcom 主供、中际出口 80 亿、MPO/FAU 保底扩产四条 C/lead；没有 A/B 级来源前不升级。

## 对话窗口摘要源表

| 当前核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| InP substrate / epiwafer / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS | 合格衬底、外延、6 英寸良率、老化测试、客户认证和出口许可共同限制高端光源供给；低端或未认证产能不能替代 | DigiTimes 本周 InP 出口缓解不足、6 英寸供给墙、IntelliEPI 仍受 substrate shortage 约束；Coherent/JX/IQE/Tower 既有官方扩产路径 | EML/InP：2026H2-2027H1；CW/ELS/UHP 尾部：2027H2-2028H1；长期衬底缓解看 2028-2030 | 许可常态化、6 英寸良率/认证兑现、交期和价格回落、客户停止锁产能 |
| 光模块整机装配与关键原材料同步 | 模块交付仍依赖光芯片、电芯片、无源件、PCB、测试和客户认证同步，但本窗口未见重新短缺证据 | 中际/天孚/光迅/东山等 CNINFO 未见经营相关新增；新易盛仅治理公告；既有 Q2 供应链缓解口径未被推翻 | 2026Q2-Q3 继续缓解；置信度中 | Q2/Q3 交付、毛利、存货周转改善；若模块厂重提关键料或测试短缺则反转 |
| 数据中心 fiber/cable/connectivity | AI 数据中心光连接密度上升，客户长协和光纤光缆上行周期可能传导到连接组件 | 长飞异动公告承认 AI 数据中心光纤光缆价格关注度，但称经营正常、价格影响需看业务结构；Corning/Amazon/NVIDIA 既有官方合作 | 当前 N/A；0-12 个月可能升温 | minimum capacity/prepayment、交期拉长、订单/毛利拆分、FAU/MT/PM fiber 传导；若扩产充分释放则反转 |
| FAU / fiber array / MT / MPO / Lens / 光无源器件 | CPO/ELS 和高速模块提升精密耦合、低损耗连接和自动化交付要求 | 光库并购安捷讯修订稿确认 FAU/MT/MPO/Lens/高速光互联产品矩阵；但无交期、涨价、良率或订单排队 | 当前 N/A；2026H2-2028 watch_to_soft | 客户定点、量产订单、交期拉长、涨价、良率/返修压力；二供认证或 CPO 延后则降级 |
| 主动对准 / CPO 制造测试设备 | CPO/SiPh 光引擎需要更高精度对准、晶圆级/芯片级测试和验收节拍；资本路径不等于订单 | 罗博特科 H 股备案获证监会确认；既有 ficonTEC/NVIDIA 合作仍缺订单/收入 | 当前 N/A；2026H2-2027 watch_to_soft | CPO-specific 订单、设备排队、验收收入、良率瓶颈；若无订单或 CPO 延后则降级 |

| 未来潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| CPO/NPO 光引擎与 ELS package | 2026-2028 CPO/ELS 放量会提高外置光源、热稳定、可维护连接和光引擎良率要求 | NVIDIA/ficonTEC 既有路线支持方向；本周无量产订单和交付瓶颈新证据 | 2026H2-2028 | NVIDIA/交换机厂/光源厂披露量产、allocation、客户锁产能或交付瓶颈 | CPO 延后、可插拔继续主导、ELS 多供稳定 |
| FAU / fiber array / MT / MPO / Lens | 通道数和光连接密度上升，精密耦合和低损耗连接要求提高 | 光库/安捷讯 A 级映射增强；缺短缺、涨价、良率证据 | 2026H2-2028 | 客户定点、量产订单、交期拉长、涨价、良率/返修压力 | 二供认证、自动化良率提升、CPO 放量推迟 |
| 主动对准 / WLBI / OWAT / 光电联合测试 | 光子芯片和光引擎量产需要 known-good optical engine 与更长测试节拍 | 罗博特科 H 股备案是融资/上市路径，不是订单；ficonTEC/NVIDIA 合作仍待商业化 | 2026H2-2027 | 设备订单排队、交期拉长、验收收入放量、测试节拍瓶颈 | 设备产能充足、客户验证顺利、CPO 商业化延后 |
| 光模块/光引擎热管理与液冷兼容 | ELSFP、CPO 和高功率光源对 IHS/cage/TIM/cold plate interface 和热可靠性要求提高 | 当前缺 A/B 级交付受限证据 | 2026H2-2028 watch | 模块厂或交换机厂点名热可靠性、液冷兼容、返修或认证限制交付 | 标准化完成、多供应商稳定交付、热问题未影响良率 |
| DSP / driver / TIA / CDR | 1.6T/3.2T 和 LPO/LRO/CPO 会提高电芯片性能要求 | Broadcom/Marvell 证明需求和路线，不证明当前短缺；新易盛 5100 万颗说法仍为 C/lead | 2027-2028 watch | 模块厂点名电芯片短缺、客户 allocation、交期拉长 | 多供应商稳定供给或架构改变 BOM |
