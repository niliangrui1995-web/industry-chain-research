# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-05-10
最新报告：`artifacts/weekly_chain_tracking/optical_module/2026-05-10.md`
覆盖窗口：2026-05-07 至 2026-05-10

## 任务边界

本任务只跟踪光模块及其上游/中游关键环节。PCB/CCL、数据中心电力、液冷等只在影响光模块交付或需求时作为外部变量记录，不在本任务内展开。

研究宇宙：
- 光模块整机：400G / 800G / 1.6T / 3.2T。
- 光引擎 / TOSA / ROSA / CPO / OCS / ELS。
- EML / DML / CW Laser / InP / GaAs / 硅光 / 薄膜铌酸锂。
- DSP / driver / TIA / CDR。
- FAU / MT ferrule / AWG / 透镜 / 微透镜阵列 / 耦合透镜 / isolator / Faraday rotator / connector。
- 封装耦合、主动对准、测试设备、代工和模块装配。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| Lumentum 官方 transcript/10-Q 是否确认 EML/pump/CW laser 缺口和产能计划？ | 10-Q 和官方 presentation 已确认 demand outpacing current supply、allocation、EML/CW laser/1.6T/CPO/OCS 方向；“>30% 缺口”仍待官方逐字稿。 | 部分证实 |
| Coherent 6 英寸 InP ramp 是否有官方数据？ | Coherent 官方 presentation 已确认内部 InP output 年底翻倍、2027 年再翻倍以上。 | 证实 |
| 中际旭创/新易盛原材料偏紧具体指什么？ | 中际旭创拆到光芯片、电芯片、PCB、无源器件；新易盛仍未拆细，只确认 Q2 起缓解、下半年趋稳。 | 部分证实 |
| 天孚通信个别物料缺料到底是什么？ | 仍缺正式原文和具体物料拆分。 | 仍待跟踪 |
| CPO/OCS 卡点是否迁移到 ELS、FAU、主动对准测试和热管理？ | Lumentum/Corning/Coherent 给出更强观察信号，但仍不足以升级为当前堵点。 | 新增观察 |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|
| 高端 EML / InP / CW laser | 当前主堵点 | hard_bottleneck | AI 数据中心 800G/1.6T/CPO/OCS 需求超过合格激光器、InP 平台、CW laser 和客户锁定产能；约束来自良率、可靠性认证、6 英寸 InP 迁移和 LTA/产能权 | confirmed/worsened | Lumentum 10-Q 明示 demand outpacing current supply 和 allocation；Lumentum presentation 证实 100G/200G EML 创纪录、200G EML revenue 环比翻倍、1.6T 集成内部 CW laser；Coherent presentation 证实 InP output 扩产 | EML/CW laser 不再 allocation；模块厂预付款下降；Coherent/Lumentum 新产能良率兑现；1.6T 毛利回落 | 找 Lumentum 官方逐字稿，验证 >30% 缺口；跟踪 Coherent InP 良率/产能兑现 |
| 光模块整机装配与关键原材料同步 | 当前软堵点 | soft_bottleneck | 1.6T/800G 订单强，模块厂交付需要光芯片、电芯片、无源器件、PCB、测试产线同步；但原材料紧张有 Q2-Q3 缓解口径 | easing_watch | 中际旭创 IR；新易盛业绩说明会口径；三家 Q1 预付款显著上升 | 新易盛 Q2/Q3 供应链稳定兑现；模块厂交付不再受物料影响；毛利不再受供给紧张支撑 | 跟踪新易盛 Q2 交付、毛利和预付款/存货 |
| FAU / ELS / 微透镜 / 隔离器 / PM fiber | 观察卡点 | watch | CPO/ELS 提升外部光源和高精密无源件价值量，但缺全行业短缺、交期或 allocation 证据 | unchanged/new_evidence | Lumentum CPO/OCS；Coherent CPO/Datacenter；天孚 1.6T 光引擎个别物料缺料线索；Corning/NVIDIA 光连接扩产 | CPO 出货未按期放量；无源件未被客户/模块厂点名约束 | 找天孚正式 IR 原文，拆清缺料物料；跟踪 Corning 是否传导到 MT ferrule/FAU |
| CPO/OCS/主动对准与封装测试设备 | 未来迁移观察 | watch | CPO/ELS/NPO/XPO 会提高光引擎封装、主动对准、测试复杂度；当前缺设备交期短缺证据 | unchanged | Lumentum OCS/CPO ramp；Fabrinet datacom 增长；罗博特科/ficonTEC 属观察映射 | 设备交付顺利、模块厂自建/多供应商解决 | 保持 2027-2028 观察，不作为当前主结论 |
| DSP / driver / TIA / CDR | 战略节点，不是当前堵点 | rejected/watch | 先进制程、SerDes/IP 和客户导入壁垒高，但未见交期拉长、allocation 或模块厂点名短缺证据 | unchanged | N/A | 出现 A/B 级客户 allocation、交期拉长、模块厂明确点名电芯片短缺 | 不进入主结论，等 3.2T 代际证据 |
| 光连接/光纤/高密度连接器 | 新观察变量 | watch | NVIDIA-Corning 长协显示 AI 光连接被客户战略锁产能，但光纤/连接扩产不等同于 EML/InP/FAU 短缺 | new | Corning 官方公告、SEC 8-K | Corning 扩产按期兑现，客户不再锁产能 | 跟踪是否传导到 MT ferrule、连接器、FAU 和 A 股/台股映射 |

## 候选观察池

| 候选节点 | 当前判断 | 需要验证的堵点问题 | 不可直接下结论的原因 |
|---|---|---|---|
| EML / 高速激光芯片 | 主堵点 | 200G per lane EML、CW laser、pump laser 的缺口比例、交期、良率和扩产兑现 | 已有 A 级 supply allocation 与产品 ramp 证据，但单品缺口仍缺官方量化 |
| InP 衬底 / 外延 / 6 英寸平台 | 主堵点组成 | Coherent 6 英寸 ramp 是否转化为合格供给；2027 再翻倍是否能覆盖 CPO/1.6T 需求 | 扩产不等于可交付，需看良率和客户认证 |
| CW Laser / ELS | 主堵点组成和未来迁移核心 | CPO/硅光对外部光源的拉动是否形成独立短缺 | CPO 量产仍早，不能只靠战略协议推出全行业短缺 |
| 透镜 / 微透镜阵列 / 耦合透镜 | 观察 | 是否因 CPO/ELS/光引擎精密耦合形成瓶颈 | 缺交期和缺口比例 |
| FAU / MT ferrule / connector | 观察 | Corning/NVIDIA 光连接扩产是否向高密度连接器和 FAU 传导 | 光纤/光连接扩产不是模块上游单品短缺证明 |
| DSP / driver / TIA | 观察/暂不成立 | 是否因 1.6T/3.2T 电芯片导入造成模块交付瓶颈 | 本期无 A/B 短缺证据 |
| 光引擎 / 主动对准 / 封装测试 | 观察 | CPO/NPO/XPO 放量后，设备交付和良率是否限制爬坡 | 当前无本周直接短缺证据 |
| 模块装配与测试 | 软堵点 | 模块厂扩产是否仍被关键原材料或测试产能限制 | 新易盛给出 Q2 起缓解口径，不能继续简单升级 |

## 本期主深挖与次级跟踪

- 主深挖：高端 EML / InP / CW laser。
- 次级跟踪 1：光模块整机装配与关键原材料同步。
- 次级跟踪 2：FAU / ELS / 微透镜 / 隔离器等无源和光引擎组件。
- 次级跟踪 3：CPO/OCS/光连接产能迁移，含 Corning/NVIDIA 光连接扩产。

## 公司映射基线

| 公司 | ticker | 市场 | 当前角色 | 状态 |
|---|---|---|---|---|
| Lumentum | LITE.US | 美股 | EML、pump/narrow-linewidth laser、CW laser、OCS/CPO | 全球主候选 |
| Coherent | COHR.US | 美股 | InP 6 英寸、EML、CW laser、photodiode、CPO/OCS | 全球主候选 |
| Fabrinet | FN.US | 美股 | 高级光封装、模块装配和测试 | 量受益候选 |
| Corning | GLW.US | 美股 | 光连接、光纤、AI 数据中心光连接产能 | 新观察 |
| 中际旭创 | 300308.SZ | A 股 | 800G/1.6T 模块、硅光、规模交付、前端供应链锁定 | A 股基本面核心 |
| 新易盛 | 300502.SZ | A 股 | 800G/1.6T 模块、硅光、海外产能 | A 股业绩弹性核心 |
| 天孚通信 | 300394.SZ | A 股 | 光器件、1.6T 光引擎、FAU/ELS/CPO 配套 | 次级跟踪核心 |
| 光迅科技 | 002281.SZ | A 股 | 光模块、光器件、硅光/CPO/NPO 扩产 | 高交易弹性观察 |
| 源杰科技 | 688498.SH | A 股 | 激光芯片/EML 观察 | 需 200G EML/AI 客户硬证据 |
| 光库科技 | 300620.SZ | A 股 | 隔离器、铌酸锂、无源器件 | 观察 |
| 罗博特科 | 300757.SZ | A 股 | ficonTEC 光子封装/测试设备 | 观察 |
| 太辰光 | 300570.SZ | A 股 | MT ferrule、连接器/精密连接件 | 观察 |
| 光圣科技 | 6442.TW | 台股 | 光收发/Datacenter optics | 台股观察 |
| 上诠 | 3363.TWO | 台股 | FAU/无源精密件 | 台股观察 |
| 波若威 | 3163.TWO | 台股 | 光纤阵列/连接组件 | 台股观察 |

## 下期默认跟踪问题

1. Lumentum 是否发布官方 webcast transcript 或 IR Q&A，能否确认 EML、pump laser、CW laser 的缺口比例、产能计划和客户 LTA 细节？
2. Coherent 6 英寸 InP ramp 是否披露更细的 capex、良率、客户认证和产能爬坡数据？
3. 新易盛 Q2 物料缓解是否兑现，具体缓解的是 EML/CW laser、无源器件、电芯片、PCB 还是测试资源？
4. 天孚通信 1.6T 光引擎“个别物料缺料”是否有正式投资者关系记录表原文，物料是否为 FAU、透镜、隔离器、磁光材料、ELS 或其他？
5. NVIDIA-Corning 光连接扩产是否开始传导到 MT ferrule、连接器、FAU、光纤阵列和国内/台股可映射公司？
