# 周度跟踪：AI PCB 及上游材料设备 - 滚动状态

更新时间：2026-06-17
最近报告：`artifacts/weekly_chain_tracking/ai_pcb/2026-06-17_hvlp_tglass_nvidia_capacity_evidence_layering.md`
官方证据追杀补充：`artifacts/weekly_chain_tracking/ai_pcb/2026-06-17_hvlp_tglass_nvidia_official_lock_capacity_chase.md`
A股供给压力卡：`artifacts/weekly_chain_tracking/ai_pcb/2026-06-17_defu_block_trade_supply_pressure_card.md`

当前阶段：完成 2026-06-16 08:48《AI产业链战报》`HVLP4 铜箔 / T-glass 玻纤布被 NVIDIA 直签寄售锁产能` 单线证据分层，并在 2026-06-17 对 NVIDIA、Nittobo、Mitsui、Co-Tech 官方/IR/年报/SEC 文件和 DIGITIMES 一级媒体原文做窄口径追杀。本期不升级任何节点为 `hard_bottleneck`；`高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth` 与 `M7/M8/M9/M10 CCL / prepreg` 仍为 `soft_bottleneck+`。`锁产能` 总判定为 `仍未闭环`：DIGITIMES 可支持 NVIDIA 接洽 Co-Tech 讨论长期产能规划的 B 级线索；`寄售/consignment`、`LTA`、`capacity reservation`、`prepayment` 均未在相关官方材料中形成 A 级闭环。`HVLP4/HVLP5 PCB 铜箔` 维持 `watch_to_soft / 高优先级验证`，但不得写成硬证据。公司分层同步为：生益科技 `基本面主受益/质量锚`，宏和科技 `交易弹性/高优先观察`，德福科技 `交易弹性/条件式 HVLP 期权`，中英科技 `仅观察/PTFE-M10 相邻线索`。

晚间 A 股映射补充：德福科技 2026-06-04 至 2026-06-17 连续 10 个交易日出现 50.00 万股同规格大宗交易，累计 500.00 万股、69,382.00 万元；该线索只下修交易弹性质量、上调筹码供给和减持风险权重，不上调 HVLP4/5 基本面或业绩弹性。HVLP4/5 升级仍只看客户认证、正式订单、收入占比、加工费和毛利率兑现。

## 任务边界

本任务只跟踪板级 AI PCB 及其上游材料、设备和耗材：
- AI 服务器 / 交换机板级 PCB。
- 高速多层板、HDI/mSAP、类载板工艺；不等同于 ABF/BT 封装载板。
- 高端 CCL / prepreg：M7/M8/M9/M10 低损耗材料。
- 低 Dk / 低 Df / 低 CTE 电子布、T-glass、NER-glass、Q cloth、石英布、超薄布。
- HVLP / VLP / RTF PCB 铜箔。
- PPO / PPE / 碳氢 / 活性酯 / BMI 等高频高速树脂体系。
- 钻针、铣刀、压合、曝光、钻孔、电镀、测试设备。
- 湿化学、油墨、PCB 光刻胶等工艺材料。

## 执行补充要求

- 每次更新报告时，必须对当前 `hard_bottleneck` 和 `soft_bottleneck` 预估可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A`，并说明缺哪类证据。
- 每次不能只分析主深挖节点，还要扫描其他材料、设备、耗材、化学品和成品板环节，判断未来 6-24 个月可能出现的新卡点或卡点迁移。
- 对话窗口最终摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`。
- 行情快照必须按项目 `skills/allstock-data` 的多源 fallback 规则执行：A/H/美股优先腾讯 `qt.gtimg.cn`，台股优先 TWSE MIS；行情只用于交易弹性上下文，不证明产业受益或堵点成立。

## 上期问题回访状态

| 待验证问题 | 当前状态 | 结论 |
|---|---|---|
| 台光电、台燿、联茂、建滔积层板 6 月涨价执行、报价有效期、提前锁料或 M8/M9/M10 订单能见度 | 部分证实，仍待跟踪 | 台燿 6 月涨价和台系营收强劲有 B 级支持，但仍缺官方涨价函、报价有效期、客户锁料和二供认证证据。 |
| Panasonic、台系 CCL、生益科技、南亚新材是否出现官方分产品 lead time、allocation、二供 AVL、订单延期或高端 CCL/prepreg 收入占比 | 证据增强但未 hard | Broadcom/Marvell 需求、Vexos 采购端压力和台系涨价线索支持 `soft_bottleneck+`；仍缺官方分产品 allocation、订单延期和客户 AVL 排队。 |
| Nittobo、台玻、宏和、中材、国际复材、菲利华是否披露 Low Dk/Low CTE/T-glass/Q cloth 分布种交期、配额、价格和客户认证 | 强化为本周最强 `soft_bottleneck+` | 台玻管理层称高端玻纤布供不应求预计至 2027 年底，并有高阶产能翻倍和 2027 扩产路径；仍缺官方分产品交期、配额和客户 AVL 排队数量。 |
| 德福、诺德、嘉元、铜冠是否出现 PCB 级 HVLP4/HVLP5 批量供货、客户认证、收入或毛利贡献 | 未证实，维持观察 | 诺德 IR 显示 HVLP1/2/3 有订单，但 HVLP4 仍在客户测试、HVLP5 开发中；对 HVLP4/5 当前硬短缺叙事构成约束。 |
| 2026-06-15 08:48 邮件称 T-glass 缺口 >40%、HVLP4 铜箔缺口 2027 扩至 2500 吨、NVIDIA 直接锁上游 | 三条均未形成 A 级闭环 | T-glass 偏紧和高端 HVLP 需求增长有 A/B 级支撑；精确缺口数和 NVIDIA 直接锁产主要来自 DIGITIMES/市场人士、华尔街见闻转述和 X/Grok 线索，未见 NVIDIA 或供应商正式公告。 |
| 2026-06-16 08:48 邮件称 NVIDIA 对 HVLP4/T-glass 采用直签寄售、提前一年锁产能 | 官方追杀后仍未闭环 | DIGITIMES 可支持 NVIDIA 接洽 Co-Tech 讨论长期产能规划的 B 级线索；Co-Tech 年报、Mitsui 法说和 Nittobo 年报支持 HVLP4/T-glass 供需偏紧、扩产慢和客户催产能；但 NVIDIA、Nittobo、Mitsui、Co-Tech 官方/IR/SEC 材料未给出直签、寄售、LTA、capacity reservation、prepayment 或提前一年锁产能的硬证据。 |
| 沪电、生益电子、深南、胜宏、TTM、Sanmina、金像电、臻鼎、尖点、大族数控、鼎泰高科是否披露交期拉长、良率/测试瓶颈、设备 backlog 或耗材认证排队 | 需求证实，瓶颈仍 watch | 胜宏、深南、尖点等证据证明需求与扩产，但仍无两家以上板厂或设备耗材厂披露交期失控、良率瓶颈、测试产能不足或客户排队。 |

## 当前堵点账本

| 节点 | 定位 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 缓解路径 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|---|
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth | 本期主深挖卡点 | `soft_bottleneck+` | 窑炉、拉丝、电子级纱、织布、后处理、良率、专利和客户 AVL 限制 qualified output；普通布/工业纱不可替代 | `worsened/confirmed` | Nittobo 官方确认 AI server 驱动 Special Glass 需求并扩产；台玻管理层称高端玻纤布供不应求预计至 2027 年底；TrendForce 交叉验证 Nittobo/高端布供给集中；`>40%` 缺口数仍非官方 | 2026H2-2027年底中高置信；Q cloth/NER 2027H2-2028 watch | 台玻一期/二期/三期扩产，Nittobo 2027-2028 扩产，二供验证 | 报价回落、交期缩短、库存恢复，多供应商进入核心客户 AVL | 查 Nittobo/台玻正式法说、分布种交期、客户认证、良率和 allocation |
| M7/M8/M9/M10 CCL / prepreg | 当前最明确板级材料卡点 | `soft_bottleneck+` | AI server/networking 拉动低损耗材料；玻纤布、树脂、HVLP 铜箔、新线 qualified output 和客户认证共同约束 | `unchanged_to_worsened` | Broadcom/Marvell AI demand；台燿涨价线索；Vexos 采购端 lead time；上游玻纤布证据强化 | 2026H2 中高置信偏紧；2027H1 中等偏高；2027H2 取决于高端布和 CCL 新线释放 | CCL 高端线投产，二供通过终端认证，上游布/铜箔/树脂同步放松 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入核心 AVL | 查台系/大陆 CCL 的 6 月营收、M8/M9/M10 lead time 和报价有效期 |
| HVLP/VLP/RTF PCB 铜箔 | 次级跟踪 | `watch_to_soft` | 表面处理、低粗糙度一致性、添加剂配方、客户认证和进口供应集中限制高端供给；锂电铜箔不能替代 PCB 级铜箔 | `watch_priority_up / lock_capacity_unclosed` | Mitsui 官方确认高端 HVLP 需求增长、客户催产能和扩产；Co-Tech 年报确认 HVLP4 供需缺口、认证时间长和良率爬坡慢；DIGITIMES 称 NVIDIA 接洽 Co-Tech 讨论长期产能规划；诺德 IR 仍显示 HVLP4 测试、HVLP5 开发；本轮未见直签、寄售、LTA、capacity reservation 或 prepayment 硬证据 | 2026H2-2027 watch_to_soft；持续时间 N/A，缺 HVLP4/5 多客户批量收入、客户和毛利证据，也缺锁产合同证据 | 国内外多供应商稳定量产，并被 CCL/板厂客户认证 | PCB 级 HVLP4/5 多客户批量供货、加工费回落、国产良率确认；或官方确认/否认客户锁产 | 查 Mitsui/Co-Tech/德福/诺德/嘉元/铜冠 PCB 级 HVLP4/5 交付、收入、加工费、客户和毛利证据；继续监控 NVIDIA/供应商是否出现正式锁产证据 |
| 成品 AI PCB 高层板良率 / 测试 / 交付 | 次级跟踪 | `watch` | 高层压合、背钻、钻孔、电镀、阻抗测试和客户审厂可能成为材料之后的制程瓶颈 | `unchanged` | 胜宏/深南 IR 证明需求和高端产品放量；仍缺交期/良率/测试硬证据 | 2026H2-2027 watch | 板厂扩产达产、客户二供补足 | 交期恢复、订单延期减少、未出现良率/测试瓶颈 | 查沪电、生益电子、深南、胜宏、TTM、Sanmina、金像电、臻鼎 backlog、交期、良率、测试产能 |
| 钻针/测试设备/湿化学/油墨/PCB 光刻胶 | 观察 | `watch` | 板厂 capex 和高端工艺升级带动设备、耗材和工艺材料需求 | `unchanged` | 尖点扩产说明需求与供给响应；缺 A/B 级 backlog、短缺或客户认证排队 | 2026H2-2028 watch；中低置信 | 国产设备/耗材供应与客户验证顺利 | 设备交付恢复，价格稳定，客户认证不排队 | 跟踪 backlog、交期、认证排队 |
| ABF/BT 封装载板 | 单独观察 | `watch_separate` | 封装载板链路，和板级 AI PCB 不同 | `separate_only` | 只能作为相邻链路背景 | 6-24 个月单独跟踪 | 单独载板扩产和良率改善 | 与板级 PCB 混同即无效 | 如有载板证据单独开表 |
| 载板 T-glass / Q glass 与板级 CCL Low Dk-Low CTE 电子布 | 强制拆分 | `taxonomy_guardrail` | 载板属于 ABF/BT/FC-BGA/IC substrate，板级电子布属于 CCL/prepreg 增强材料；两者可能共享供应商但客户、用途和证据锚不同 | `new_guardrail` | 2026-06-17 单线复核后新增 | 长期执行 | 后续所有记录增加 `end_use`：IC substrate、board-level CCL、finished PCB、PCB copper foil | 任何跨用途自动升级均无效 | 表格和报告同步分列 |

## 候选观察池

| 候选节点 | 需要验证的堵点问题 | 当前处理 |
|---|---|---|
| 高端电子玻纤布分产品 | Low Dk/Df、Low CTE、T-glass、NER-glass、Q cloth 是否出现交期/配额硬证据 | 当前最重要主线，2026H2-2027年底维持偏紧 |
| M9/M10 低损耗 CCL/prepreg | 是否从未来升级路线变成当前供需缺口 | `likely_future_bottleneck`，重点看 Rubin/112G+/224G+、客户认证、实际成交价、交期和二供排队 |
| HVLP4/HVLP5 PCB 铜箔 | 是否有 PCB 级批量交付、客户认证、收入贡献和加工费上调 | `watch_to_soft`，DIGITIMES/金居采访提高验证优先级，但诺德 IR 后对 HVLP4/5 当前批量硬短缺保持谨慎 |
| 成品板良率/测试 | 是否从订单兑现升级为制程瓶颈 | `watch_to_soft` |
| 钻孔/压合/电镀/测试设备 | 是否出现设备交期拉长和板厂 capex 排队 | 未来迁移观察 |
| 湿化学/油墨/PCB 光刻胶 | 是否出现客户认证排队和高端产品短缺 | 未来迁移观察 |

## 下期默认跟踪问题

1. 台玻是否发布更正式的股东会资料或法说资料，披露 Low DK/Low CTE 分产品交期、价格、客户认证、产能和良率。
2. Nittobo、台玻、宏和、中材、国际复材、菲利华是否出现分布种 allocation、客户 AVL 排队或订单延期证据。
3. 台光电、台燿、联茂、建滔、生益、南亚是否披露 M8/M9/M10 CCL/prepreg 分产品 lead time、报价有效期、客户提前锁料或二供认证。
4. 德福、诺德、嘉元、铜冠是否出现 PCB 级 HVLP4/HVLP5 多客户批量供货、客户认证、收入、良率或毛利贡献。
5. 沪电、生益电子、深南、胜宏、TTM、Sanmina、金像电、臻鼎、尖点、大族数控、鼎泰高科是否披露交期拉长、良率/测试瓶颈、设备 backlog 或耗材认证排队。
6. NVIDIA、AWS、Google、Meta、Nittobo、Mitsui、Co-Tech 是否出现 LTA、consignment、prepayment、allocation 或 capacity reservation 官方表述，以验证“直接锁定上游”是否成立。本轮已查 NVIDIA/Nittobo/Mitsui/Co-Tech 与 DIGITIMES，结论为 `锁产能仍未闭环`；后续只在出现新增官方/IR/SEC/一级媒体原文时再上调。
7. 后续所有 T-glass/Low CTE/Q glass 记录必须标注 `end_use`，严格区分 ABF/IC 载板与板级 PCB/CCL；同一供应商同一材料词不自动跨用途升级。

## 对话窗口摘要

| 当前核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / Q cloth | 窑炉、拉丝、织布、后处理、良率、专利和客户 AVL 限制 qualified output；普通电子布/工业纱不可替代 | Nittobo 官方确认 AI server 需求和扩产；台玻管理层称供不应求预计至 2027 年底；TrendForce 交叉验证 2027 年中前难明显缓解；`>40%` 缺口数未获官方确认 | 2026H2-2027年底中高置信；Q cloth/NER 2027H2-2028 watch | 台玻/Nittobo/二供产能转为 qualified output；高端布报价回落、交期缩短、库存恢复，多供应商进入核心客户 AVL |
| M7/M8/M9/M10 CCL / prepreg | AI server/networking 推动低损耗材料升级；玻纤布、树脂、HVLP 铜箔、新线 qualified output 和客户认证共同约束 | Broadcom/Marvell 证明需求；TechNews 与 Vexos 支持涨价和 lead-time 压力 | 2026H2 中高置信偏紧；2027H1 中等偏高；2027H2 取决于高端布和 CCL 新线释放 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入核心 AVL |

| 未来潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| HVLP4/HVLP5 PCB 铜箔 | 224G/1.6T/M9/M10 对低粗糙度和表面处理一致性要求提升，进口高端供应集中 | Mitsui 官方确认需求增长、客户催产能和扩产；Co-Tech 年报确认 HVLP4 供需缺口、认证时间长和良率爬坡慢；DIGITIMES 称 NVIDIA 接洽 Co-Tech 讨论长期产能规划；但直签、寄售、LTA、capacity reservation、prepayment 均未形成官方闭环；诺德 IR 显示 HVLP4 仍测试、HVLP5 开发中 | 2026H2-2027 watch_to_soft | HVLP4/5 多客户批量收入、客户认证、加工费上调、毛利贡献；NVIDIA/供应商正式锁产证据 | 多供应商稳定供货，加工费回落，国产良率确认；或官方否认/淡化锁产叙事 |
| 成品 AI PCB 高层板良率/测试 | 材料缓解后瓶颈可能迁移到高层压合、背钻、电镀、阻抗/可靠性测试和客户审厂 | 胜宏/深南 IR 证明需求，但交期/良率硬证据不足 | 2026H2-2027 watch_to_soft | 两家以上板厂披露交期拉长、良率瓶颈、测试产能不足、订单延期或客户转单 | 扩产达产，订单延期减少，交期正常 |
| 钻针/测试设备/湿化学/PCB 光刻胶 | HDI/mSAP/N+M、高层高速板提升设备精度、耗材寿命、药水稳定性和认证要求 | 尖点扩产证明需求，缺 A/B 级 backlog/短缺/认证排队 | 2027-2028 watch | 设备 backlog 或交期显著拉长，耗材/药水客户认证排队，高端收入放量且供应不足 | 设备交付恢复，价格稳定，客户认证不排队 |

## 2026-06-16 晚间 PDF 补充状态

补充来源：`D:/Downloads/JP_Morgan_Asia_Components_Chinese_Report.pdf`，J.P. Morgan Asia Pacific Equity Research, June 2026 中文整理版。按 B 级卖方估算和结构判断处理，不作为 A 股订单、客户、涨价或量产的 A 级证据。

| 节点 | 状态调整 | 原因 | 下一步验证 |
|---|---|---|---|
| AI server 高端 MLCC | `secondary_track_up` | 报告估算 AI server MLCC TAM 150%+ CAGR，高端 MLCC 产能消耗会挤压低阶/中阶供给。 | 三环集团、风华高科的 AI server 高端 MLCC 客户、规格、ASP、收入占比和毛利率。 |
| ABF / IC package substrate | `watch_to_soft_separate` | 报告估算载板 UTR 2027e 超过 100%，AI server & switch 面积需求 2028e 占比 75%，stepper、T-glass 与 LTA 是供给约束。 | Unimicron、Ibiden、南电、兴森、深南的 capacity reservation、advance payment、FC-BGA 量产、良率、收入和毛利。 |
| M8/M9 HPC CCL / prepreg | `soft_bottleneck+` 维持 | 报告强化 HPC CCL/PCB TAM、M9 升级、HDI 良率和 switch 层数提升，但仍是卖方估算。 | M8/M9/M10 分产品 lead time、报价有效期、客户锁料和二供 AVL。 |
| AI 系统级测试设备 | `new_watch` | 报告新增 SLT、光通信/CPO、数据中心电源测试三条 100%+ CAGR 方向，海外锚为 Chroma。 | A 股测试设备公司需拆分验证 SLT、光通信测试、rack power/HVDC 测试订单和收入，不能泛化为普通半导体测试设备。 |
