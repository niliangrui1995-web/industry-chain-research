# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-05-11
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-05-10.md`
覆盖窗口：2026-05-07 至 2026-05-10
当前阶段：第二期全链雷达，已吸收光模块与 AI PCB 专项 2026-05-10 状态。

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
- 可以根据研究复杂度自主拆分任务并调用子代理进行并行研究；子代理默认使用超高智能。若子代理达到上限，应排队等待前面的子代理完成，再继续新建后续子代理。主代理负责最终证据分级、交叉验证、堵点判断、排名和报告合成。

## 本期全链结论

1. `HBM / AI memory / server DRAM / enterprise SSD`：全链最硬约束仍在，维持 `hard_bottleneck`。本期缺新增官方客户 allocation 细表，但 TrendForce 价格/LTA 背景证据、前期内存供应商官方证据和 AI cloud capex/backlog 继续支持偏紧。
2. `高速 EML / InP / CW laser`：由光模块专项吸收并被 Lumentum/Coherent 官方 2026-05-05/06 结果强化，维持 `hard_bottleneck`，本期状态 `confirmed / worsened`。
3. `M7/M8/M9 CCL/prepreg`：由 AI PCB 专项吸收，Panasonic 5 月调价生效，高端 CCL/prepreg 维持 `soft_bottleneck`，本期状态 `worsened`。
4. `高端电子布 / T-glass / 低 CTE 布`：AI PCB 专项将其从 `soft_bottleneck/watch` 上调为 `soft_bottleneck`，但官方分产品交期、合格产能和客户认证仍不足。
5. `数据中心电力 / 液冷 / rack power / 预制化基础设施`：本期新增全链深挖方向，证据来自 CoreWeave、Eaton、Schneider 的 A 级资料，状态升级为 `soft_bottleneck/watch`，暂不升硬堵点。
6. `光连接 / 光纤 / 高密连接 / FAU/MT ferrule`：Corning/NVIDIA 长协使其进入未来 6-24 个月迁移池；当前是 `watch`，不是现成短缺结论。
7. `CoWoS / advanced packaging`：结构重要性极高，但本期新增证据仍不足以证明当前新增供需缺口，维持 `strategic_watch`。
8. `AI networking / retimer / PCIe / Ethernet`：需求强，Astera/Arista 等仍是高成长观察；未见供给缺口证据，维持 `strategic_watch`。

## 专项吸收状态

| 专项任务 | 最新状态文件 | 本期吸收结论 | 对全链排序的影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | 高速 EML/InP/CW laser 为硬堵点；模块整机关键物料同步为 easing_watch；FAU/ELS/微透镜/隔离器/PM fiber 为迁移观察；DSP/TIA/CDR 仍未成立 | 高速光源链排全链第 2；光连接/FAU/ELS 进入未来迁移池 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | M7/M8/M9 CCL/prepreg 为最明确软堵点；高端电子布/T-glass 升级为 soft；HVLP/VLP/RTF 铜箔为 worsened_watch；成品板厂未证明加工产能瓶颈 | CCL/prepreg 排全链第 3；T-glass/HVLP 进入未来迁移池 |

## 当前全链堵点账本

| 节点 | 所属赛道 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| HBM / HBM4 / AI memory / enterprise SSD | 存储 | 当前主堵点 | hard_bottleneck | AI accelerator 与 AI cloud 需求超过高价值内存合格供给；约束来自 DRAM 晶圆分配、堆叠良率、封装、客户认证和 LTA 锁量 | unchanged / 加剧观察 | TrendForce 2Q26 价格/LTA；前期 Micron/Samsung/SK hynix；CoreWeave backlog/capex | HBM ASP/毛利回落、客户不再锁货、HBM4 多供方充分认证 | 查客户 allocation、HBM4 认证、价格和产能节奏 |
| 高速 EML / InP / CW laser | 光模块上游 | 当前主堵点 | hard_bottleneck | 800G/1.6T/CPO/OCS 需求超过合格激光器、InP 平台、CW laser 和客户锁定产能 | confirmed/worsened | Lumentum Q3 FY26；Coherent Q3 FY26；光模块专项 | laser 不再 allocation、模块厂预付款下降、6 英寸 InP 合格产能兑现 | 专项继续补官方 transcript/10-Q 与单品缺口比例 |
| M7/M8/M9 CCL/prepreg | AI PCB/CCL | 当前软堵点 | soft_bottleneck | 高端材料涨价和上游玻纤布、铜箔、树脂、配方、认证、批量良率共同约束 | worsened | Panasonic 官方调价；AI PCB 专项；台系材料线索 | 提价落空、交期缩短、二供通过、库存回补 | 跟 5 月成交价、台系营收、客户认证 |
| 高端电子布 / T-glass / 低 CTE 布 | PCB 上游材料 | 当前软堵点 | soft_bottleneck | 低端布不可替代高端低损耗/低 CTE 需求；约束来自窑炉、纱、织布、良率和认证 | upgraded_to_soft | AI PCB 专项 B/C2 证据 | 高端布库存回升、报价回落、新产能快速认证 | 找 Nittobo/Asahi/台玻/泰山/中材/宏和/国际复材官方证据 |
| HVLP / VLP / RTF 铜箔 | PCB 上游材料 | 候选卡点 | soft_bottleneck/watch | 表面处理、粗糙度一致性、客户认证和批量交付约束 | worsened_watch | AI PCB 专项和 Digitimes 线索 | 多家稳定批量供货、价格回落 | 跟德福、嘉元、诺德及日台铜箔厂披露 |
| 数据中心电力 / 液冷 / rack power | 数据中心基础设施 | 新增深挖主线 | soft_bottleneck/watch | AI cloud 建设强度抬升，电气设备、thermal、预制模块、并网和工程交付可能限制建设速度 | upgraded_to_soft_watch | CoreWeave 1Q26；Eaton 1Q26；Schneider Q1 | backlog 回落、交期缩短、项目不再延误 | 补单品交期、项目延误、A 股订单纯度 |
| 光连接 / 光纤 / 高密连接 / FAU/MT ferrule | 光互连迁移 | 新增观察 | watch | NVIDIA/Corning 长协说明光连接成为 AI factory 战略锁产能对象 | new | Corning/NVIDIA 官方长协 | 扩产按期兑现且未传导至连接器/FAU/无源件短缺 | 跟 Corning 是否传导到 MT ferrule/FAU/连接器 |
| CoWoS / advanced packaging | 先进封装 | 战略观察 | strategic_watch | AI accelerator 结构核心，但本期缺新增供需缺口量化 | unchanged | TSMC 4 月收入、前期 TSMC transcript | TSMC/OSAT 产能释放快于需求 | 补客户排产、封装基板、设备交期证据 |
| AI networking / retimer / PCIe / Ethernet | 高速互连 | 战略观察 | strategic_watch | 网络需求强，但电互连/交换机/retimer 未证明当前供给不足 | unchanged | Arista/Astera 前期官方结果 | 出现 allocation/交期证据则升级 | 跟 Arista/Astera/Broadcom/Marvell 订单和交期 |

## 本期深挖方向

- 主深挖 1：`HBM / AI memory / enterprise SSD`。目标是确认 HBM3E/HBM4 客户 allocation、价格、LTA、产能扩张、二供认证和 enterprise SSD 是否从存储副线升级为独立卡点。
- 主深挖 2：`数据中心电力 / 液冷 / rack power / 预制化基础设施`。目标是把 CoreWeave/Eaton/Schneider 的订单和 backlog 拆成可验证的变压器、switchgear、UPS、rack PDU、CDU/冷板、预制模块、并网和工程交付约束。

## 三类排名快照

| 类型 | 排名 | 对象 | 理由 | 证据等级 | 风险 |
|---|---:|---|---|---|---|
| 结构重要性 | 1 | GPU/ASIC + advanced packaging/CoWoS | AI 算力核心入口，决定全链需求传导 | A | 本期缺新增堵点证据 |
| 结构重要性 | 2 | HBM / AI memory | 合格供给直接限制 AI accelerator 与推理/训练扩张 | A/B | 供应释放和价格周期 |
| 结构重要性 | 3 | 高速 EML / InP / CW laser | 1.6T/CPO/OCS 把光源链推成网络瓶颈 | A/B | 扩产兑现 |
| 结构重要性 | 4 | 数据中心电力/液冷 | AI factory 建设受电力、冷却、并网和工程交付制约 | A | 单品短缺未证实 |
| 结构重要性 | 5 | AI PCB/CCL/T-glass/HVLP | 高速高层板材料规格升级 | A/B | 涨价传导和二供 |
| 基本面质量 | 1 | TSMC / NVIDIA / SK hynix / Samsung / Micron | 控制算力、先进制造、封装和 HBM 利润池 | A | 估值、地缘、周期 |
| 基本面质量 | 2 | Lumentum / Coherent | 控制高速光源和 InP/CW 关键节点 | A/B | 新产能兑现 |
| 基本面质量 | 3 | Vertiv / Eaton / Schneider | 数据中心电力和 thermal 全球龙头 | A | 项目周期 |
| 基本面质量 | 4 | Corning | 光连接/光纤进入 AI factory 战略长协 | A | 扩产兑现 |
| 基本面质量 | 5 | 中际旭创 / 新易盛 / 生益科技 / 沪电股份 | A 股光模块、CCL、AI PCB 硬证据较清楚 | A/B | 拥挤和年降 |
| 业绩弹性 | 1 | 光模块上游和模块厂 | 本期官方财报与专项证据最集中 | A/B | 年降和估值 |
| 业绩弹性 | 2 | HBM/AI memory | ASP、LTA、产品结构最直接 | A/B | 供给释放 |
| 业绩弹性 | 3 | 数据中心电力/液冷 | 订单/backlog 向收入传导 | A/B | 收入确认慢 |
| 业绩弹性 | 4 | AI PCB 高端材料 | 涨价和材料升级带来利润弹性 | A/B/C2 | 认证和传导不确定 |
| 业绩弹性 | 5 | AI networking/retimer | 高增长但非短缺主线 | A | 估值和竞争 |
| 交易弹性 | 1 | A 股光模块/CPO 弹性组 | 催化密度、成交额、波动最高 | A/B/C | 拥挤和 C 级扩散 |
| 交易弹性 | 2 | PCB 上游高弹性组 | T-glass/HVLP/高端材料主题强 | B/C2 | 高端收入证据不足 |
| 交易弹性 | 3 | 美股光连接与光源组 | LITE/COHR/GLW 官方催化密集 | A | 估值已反映 |
| 交易弹性 | 4 | 数据中心电力 A 股组 | 电力/液冷进入全链视野 | B/A 待补 | 订单纯度不足 |
| 交易弹性 | 5 | 美股互连/电力组 | ALAB/ANET/VRT 增长强、流动性好 | A | 高预期 |

## 下期默认跟踪问题

1. HBM/HBM4 是否出现官方或可核验的客户 allocation、HBM4 认证、ASP、LTA、capex 和供应商可用产能数据？
2. Lumentum 官方 transcript/10-Q 是否补出 pump laser、CW laser、EML、OCS/CPO 的 supply-demand imbalance、LTA、allocation 或单品缺口比例？
3. AI PCB 专项是否验证 5 月 CCL/prepreg 成交价、台系 5 月营收、高端电子布/T-glass 官方交期、HVLP4/HVLP5 批量交付和客户认证？
4. CoreWeave、Vertiv、Eaton、Schneider 是否披露变压器、switchgear、rack PDU、CDU/冷板、预制模块的单品交期或项目延误？
5. CoWoS/advanced packaging 是否出现 TSMC/OSAT/基板/设备新增合格产能不足、客户排产或交期证据？
6. Corning/NVIDIA 光连接长协是否向 MT ferrule、FAU、连接器、光纤阵列和国内/台股映射公司传导？

## 最近证据源

- CoreWeave 1Q26 presentation: https://s205.q4cdn.com/133937190/files/doc_financials/2026/q1/CoreWeave-1Q26-Earnings-Presentation.pdf
- Lumentum Q3 FY26 results: https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Third-Quarter-of-Fiscal-Year-2026-Financial-Results/default.aspx
- Lumentum Q3 FY26 presentation: https://s21.q4cdn.com/377324469/files/doc_financials/2026/q3/Q3-FY26-Earnings-Presentation_final.pdf
- Coherent Q3 FY26 results: https://www.coherent.com/news/press-releases/third-quarter-fiscal-year-2026-results
- Coherent Q3 FY26 presentation: https://www.coherent.com/content/dam/coherent/site/en/documents/investors/investor-presentations/2026/may-6/investor-presentation-20260506.pdf
- Corning/NVIDIA official release: https://investor.corning.com/news-and-events/news/news-details/2026/NVIDIA-and-Corning-Announce-Long-Term-Partnership-To-Strengthen-U-S--Manufacturing-for-AI-Infrastructure/default.aspx
- Eaton 1Q26 release: https://www.eaton.com/us/en-us/company/news-insights/news-releases/2026/eaton-reports-record-first-quarter-2026-results.html
- Eaton 1Q26 presentation: https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q1/q1-2026-analyst-presentation.pdf
- Schneider Electric Q1 2026 revenues: https://www.se.com/ww/en/assets/pdf/release-q1-revenues-2026
- Panasonic CCL/prepreg price revision: https://industrial.panasonic.com/ww/electronic-materials/news/2026-04-09-em-ccl
- TSMC monthly revenue: https://investor.tsmc.com/english/monthly-revenue/2026
- TrendForce memory pricing survey: https://www.trendforce.com/presscenter/news/20260331-12995.html
