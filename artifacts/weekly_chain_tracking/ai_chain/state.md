# 周度总览：AI产业链上下游雷达 - 滚动状态

## 2026-08-09 最新运行状态

更新时间：2026-08-09（北京时间；第十三期全链雷达）
研究截止日（as_of）：2026-08-09
最新报告：[2026-08-09.md](2026-08-09.md)；结构化证据包：[2026-08-09_research_inputs.json](2026-08-09_research_inputs.json)；规范化产物：[2026-08-09.normalized.json](2026-08-09.normalized.json)；证据检查：[2026-08-09.bottleneck_evidence_checks.csv](2026-08-09.bottleneck_evidence_checks.csv)。

### 运行合同元数据

| 字段 | 本轮实际值 |
|---|---|
| captured_at_beijing | 2026-08-09T19:02:44+08:00 |
| skill_revision | git:d02fac57d10911d2937cadd349fd096b46596ec8 |
| prompt_contract_version | 2026-07-27.1 |
| skill_content_sha256 | 656fd6486cebe6403278246e6d7424d8f25c1ae6894787f172b244eeec2bb5e0 |
| skill_tree_status | clean |
| skills | ai-chain-research-orchestrator；research-industry-chain |
| status | ok |

本轮在业务读取前完成合同预检；本期需要近周增量核验，故按两项实际Skill重跑元数据。normalizer 使用同一 as_of=2026-08-09 的严格模式，issues=0；validate_bottleneck_evidence.py 使用同一 as_of，返回 reviewable、eligible_count=5、incomplete_count=0、ineligible_count=0。eligible_for_bottleneck_review 仅表示包可供人工复核，不自动授予卡点结论。

### 当前主台账（2026-08-09）

| 节点 | check_id | 结论/时段 | 证据状态与边界 | 变化/反转指标 |
|---|---|---|---|---|
| Azure AI云有效算力容量 | ai-chain-20260809-azure-capacity-01 | 限Microsoft/Azure的hard_bottleneck；2026H2 | 三腿均为2026-07-29 company_original Microsoft FY26 Q4；需求持续超过可用容量、当季新增容量迅速变现。 | unchanged；可用容量增速持续超过需求且新增容量不再快速吸收时降级。 |
| AI服务器内存组合（HBM、server DRAM、eSSD） | ai-chain-20260809-memory-01 | hard_bottleneck；2026H2 | 三腿均为2026-07-30 company_original Samsung 2026Q2；SK hynix作交叉验证。仅为组合级结论。 | unchanged；三类产品同时供需平衡、库存回补或原厂撤回约束表述时降级。 |
| 领先逻辑与后端先进封装/测试有效产能 | ai-chain-20260809-leading-edge-backend-01 | 限TSMC披露范围的hard_bottleneck；2026H2 | 需求为2026Q2；供给为2026Q1 N3当前产能紧张及2026Q2后端shortage mode/测试机短缺；缺口由两期official披露闭环。 | unchanged；后端平衡、测试机短缺解除和外部替代稳定批供时降级。 |
| 1.6T高速光模块有效交付 | ai-chain-20260809-1p6t-delivery-01 | hard_bottleneck；2026H2 | 三腿均为2026-07-28 company_original 中际旭创；核心料、认证和大规模交付共同受限。 | unchanged；物料改善、交期常态化和多家认证供应商稳定批交时降级。 |
| M8/M9/M10 CCL/prepreg材料组合 | ai-chain-20260809-pcb-ccl-01 | soft_bottleneck；2026H2 | 需求为2026-07-22沪电，供给/缺口为2026-07-09南亚；南亚口径混列ABF，故不升hard。 | unchanged；分级报价/交期常态化、停止锁料且二供进入AVL时降级。 |

所有当前hard/soft行的 claim_as_of=2026-08-09、time_horizon一致，并用 evidence_check_id 唯一关联同包检查；没有使用匿名、social、lead_only或陈旧来源。专项中的200G/lane EML+合格InP仍为公司级soft、改善中，不并入全链主账；PCB铜箔与板级电子布留在专项跟踪，主账仅保留材料组合。

### 专项吸收与未来队列

- 光模块专项（2026-08-09）：1.6T维持hard；NPO/2.4T维持2027H2-2028的medium likely_future_bottleneck。AXT锁产能、扩产、CPO量产和连接器交付只能说明保供/需求或缓解路径。
- AI PCB专项（2026-08-09）：铜箔、板级电子布、CCL/prepreg均为soft；广义HVLP不能写成HVLP4/5，ABF/BT的T-glass/Low CTE不得混入板级PCB。
- HBM final/package test、probe card、Cube Prober；HVLP5/Q cloth/M10与板级良率；数据中心电力/液冷设施集成；网络交换与高速互连；玻璃基板/CoPoS均为low-confidence watch，future_max_age_days=365。

### 公司映射与下次动作

Microsoft、Samsung、TSMC、中际旭创、沪电股份、南亚塑胶均为 revenue/current/watch_only；阶段日期、来源类型和定位见本期报告。未复用任何专项行情、估值、市值或预期差，未标记main_candidate，也没有形成交易弹性排名。

下期优先核验：内存原厂allocation/交期/库存；Azure新增容量吸收；TSMC后端和tester；1.6T/200G EML/InP的物料与认证；以及PCB、电力、液冷、网络能否出现行业级同节点三腿闭环。

> 下方2026-08-02及更早内容为历史基线，不具有本期check_id、claim_as_of或normalizer资格，不能直接作为当前hard/soft准出依据。

## 2026-08-02 最新运行状态

更新时间：2026-08-02（北京时间；第十二期全链雷达）
研究截止日（`as_of`）：2026-08-02
最新报告：[`2026-08-02.md`](2026-08-02.md)；结构化证据包：[`2026-08-02_research_inputs.json`](2026-08-02_research_inputs.json)；规范化产物：[`2026-08-02.normalized.json`](2026-08-02.normalized.json)。

### 运行合同元数据

```json
{
  "captured_at_beijing": "2026-08-02T19:03:07+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "656fd6486cebe6403278246e6d7424d8f25c1ae6894787f172b244eeec2bb5e0",
  "skill_revision": "git:28e32cd0f4383dcb99ec0e6af8a8be5f12d55d4e",
  "skill_tree_status": "clean",
  "skills": [
    "ai-chain-research-orchestrator",
    "research-industry-chain"
  ],
  "status": "ok"
}
```

同一 `--as-of 2026-08-02` 下，normalizer 严格模式问题数为 0；`validate_bottleneck_evidence.py` 结果为 `status=reviewable`、`eligible_count=5`、`incomplete_count=0`、`ineligible_count=0`。`eligible_for_bottleneck_review` 只是证据包可供人工审阅，以下结论仍以三腿来源和反证边界为准。

### 当前主台账（2026-08-02）

| 节点 | check_id | 结论 / 时段 | 证据状态与边界 | 变化 / 反转指标 |
|---|---|---|---|---|
| Azure AI 云有效算力容量 | `ai-chain-20260802-azure-capacity-01` | Microsoft/Azure 范围内 `hard_bottleneck`；2026H2 | 三腿均为 2026-07-29 `company_original` [Microsoft FY26 Q4](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)，明示需求超过可用容量；`eligible_for_bottleneck_review`。 | `unchanged`；新容量不再迅速被吸收且容量增长快于需求时降级。 |
| AI 服务器内存组合（HBM、server DRAM、eSSD） | `ai-chain-20260802-memory-01` | `hard_bottleneck`；2026H2 | 2026-07-30 `company_original` [Samsung](https://news.samsung.com/global/samsung-electronics-announces-second-quarter-2026-results) 三腿，需求超供给由 2026-07-29 [SK hynix](https://news.skhynix.com/en/q2-2026-business-results/) 交叉验证；`eligible_for_bottleneck_review`。 | `unchanged`；不可推为特定料号/客户/配额。 |
| 先进制程逻辑与后端先进封装/测试有效产能 | `ai-chain-20260802-leading-edge-backend-01` | TSMC 披露范围内 `hard_bottleneck`；2026H2 | 三腿均为 2026-07-16 `official` [TSMC 业绩会](https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-07/547d1696765e05ce3adb81c108ce1c8c1682b80c/TSMC%202Q26%20Transcript.pdf)，后端 `shortage mode`、客户增长受限、测试机短缺；`eligible_for_bottleneck_review`。 | `unchanged`；不映射 OSAT、测试机、探针或材料公司订单。 |
| 1.6T 高速光模块有效交付 | `ai-chain-20260802-1p6t-delivery-01` | `hard_bottleneck`；2026H2 | 三腿均为 2026-07-28 `company_original` [中际旭创](https://static.cninfo.com.cn/finalpage/2026-07-28/1225445792.PDF)，核心料、认证和大规模交付共同受限；`eligible_for_bottleneck_review`。 | `upgraded`；多家认证供应商稳定批供/交期常态化则降级。 |
| M8/M9/M10 CCL/prepreg 材料组合 | `ai-chain-20260802-pcb-ccl-01` | `soft_bottleneck`；2026H2 | 需求为 2026-07-22 `company_original` [沪电](https://static.cninfo.com.cn/finalpage/2026-07-22/1225436914.PDF)，供给/缺口为 2026-07-09 `company_original` [南亚](https://www.npc.com.tw/npcfile/public/revenue/20260709170936065.pdf)；`eligible_for_bottleneck_review`。 | `unchanged`；无分级交期/ allocation /订单延期，不能升 hard。 |

上表全部 ledger 与 evidence check 的 `claim_as_of=2026-08-02`、`time_horizon=2026H2` 一致，且以 `evidence_check_id` 关联；当前 hard/soft 没有使用匿名、社交、`lead_only` 或陈旧来源。第二供应商状态是替代供给成熟度字段，不是证据包 companion：所有五项都有同包检查；Azure、内存均记录 `none`，先进后端、1.6T、CCL/prepreg 记录 `qualifying`。

### 专项吸收和非升级项

- 光模块专项：1.6T 有效交付升级为 hard；200G/lane EML + 合格 InP 已降为 soft、改善中。NPO/2.4T 是 2027H2–2028 的 `likely_future_bottleneck`（medium，`future_max_age_days=365`）。
- AI PCB 专项：高频高速铜箔、Low Dk/Df/超薄电子布和 CCL/prepreg 仍为 soft；全链主账只保留 CCL/prepreg 组合，未把 HVLP5、Q cloth、M10 分级材料写成当前缺货。
- 液冷：Modine 2026-07-29 SEC 原始披露只能支持公司级 soft；网络、电力仅有需求信号，继续 `watch`。

### 未来 6–24 个月观察队列

| 节点 | 状态 / 时点 | 置信度 | 必须补齐的反证或确认证据 |
|---|---|---|---|
| NPO/2.4T 光引擎硅光、电芯片、封装、客户认证 | `likely_future_bottleneck`；2027H2–2028 | medium | 同一客户的认证供应商数、单品产能/良率、交期、订单与未满足需求。 |
| HBM final/package test、probe card、Cube Prober | `watch`；2026H2–2027H2 | low | 原厂点名限制、两家供应方交期/认证/产能闭环。 |
| HVLP5、Q cloth、M10 与板级良率/测试 | `watch`；2027H2–2028 | low | 分等级产能、交期、allocation、良率和订单延期。 |
| 数据中心电力与液冷设施级集成 | `watch`；2026H2–2027 | low | 变压器、开关柜、UPS、CDU 或项目调试的行业有效供给/延期证据。 |
| AI 数据中心网络交换机与高速互连 | `watch`；2026H2–2027 | low | 交换芯片、光引擎、retimer、PCB/基板的 allocation、交期或客户延期。 |
| 玻璃基板/CoPoS 等替代封装路线 | `watch`；2027–2028 | low | 量产良率、客户认证、可交付产能、成本和项目交期。 |

未来队列每项均记录 `future_max_age_days=365`；除 NPO/2.4T 外，本期均为低置信度 watch，不因主题逻辑升级。

### 公司映射与下次动作

Microsoft（MSFT）、Samsung（005930.KS）、SK hynix（000660.KS）、TSMC（2330.TW）、中际旭创（300308.SZ）和沪电股份（002463.SZ）的直接商业化阶段均记录为 `revenue`、`stage_claim_window=current`，完整日期、`stage_source_type` 和 locator 见本期报告；全部为 `watch_only`，没有 `main_candidate`。基本面质量、实时交易弹性、估值和预期差未在本期重建，相关字段保持 N/A，不把阶段证据写成利润、现金流或估值结论。

下周按优先级继续核验：内存原厂的 allocation/交期/库存与可用产能、Azure 新容量吸收、TSMC 后端与测试机状态、1.6T 的物料/认证改善，以及 PCB/电力/液冷/网络能否形成行业级三腿闭环。

> 下方 2026-07-26 及更早内容为历史基线，不具有本期 `check_id` / companion / normalizer 资格，不能直接作为当前 hard/soft 准出依据。

更新时间：2026-07-26（北京时间；第十一期全链雷达）
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-07-26.md`
2026-07-26 全链周报完成：新增 [2026-07-26.md](2026-07-26.md)，主证据窗口为 2026-07-20 至 2026-07-26，并补扫 2026-06-29 至 2026-07-19。当前 5 个重点赛道为：云计算有效容量/服务器 CPU-memory-storage-parts、先进制程与后端封装测试、200G EML/合格 InP 前道、高频高速 PCB 材料组合、数据中心电力并网/电气设备/液冷。仅深挖前两项。
2026-07-26 状态增量：Alphabet、Intel 与 TSMC 的最新官方披露分别确认云计算有效容量、服务器 CPU/广义 memory-substrate-parts、先进制程与后端封装测试存在需求超过有效供给；先进制程与后端封装测试升级为 `hard_bottleneck`。光模块专项把 hard 收窄为 `200G/lane EML + 合格 InP substrate/epiwafer/器件前道`；AI PCB 专项把高频高速铜箔整体升级为 `soft_bottleneck+`，但全链仍无 PCB hard。美国重点区域并网维持 `hard operational`，电气设备 `soft+`，液冷设施集成 `watch_to_soft`。
覆盖窗口：2026-07-20 至 2026-07-26；补扫 2026-06-29 至 2026-07-19；北京时间
当前阶段：第十一期全链雷达。当前硬卡点集中在合格/有效产能而非名义产能；HBM test/probe/Cube Prober、CPO 对准测试、HVLP5/Q cloth/M10、液冷设施集成、800VDC 和玻璃/替代基板继续列未来迁移，不跨节点升级。

2026-07-08 A 股公司跟踪总账同步：云南锗业 002428.SZ 跌停龙虎榜、德福科技 301511.SZ 7 月 7-8 日同规格同卖方席位大宗交易、中际旭创 300308.SZ 7 月 7 日四笔平价大宗交易，分别由光模块专项与 AI PCB 专项承接；全链层只吸收交易结构、供给压力、席位/换手和拥挤度变化，不新增客户、订单、收入占比、ASP、毛利率或基本面兑现证据，主排序和堵点账本不变。
2026-07-03 A 股公司跟踪总账同步：宏和科技 603256.SH 减持进展与折价大宗交易、德福科技 301511.SZ 同规格同卖方席位大宗交易、中际旭创 300308.SZ 平价机构大宗交易、东山精密 002384.SZ 高振幅龙虎榜、云南锗业 002428.SZ 高管离任、风华高科 000636.SZ 分红实施，均只进入交易结构、治理或股东回报观察；不新增客户、订单、收入占比、ASP、毛利率或利润兑现证据。AI PCB 与光模块专项承接具体节点，全链主排序和堵点账本不变。
2026-07-03 江波龙 H1 预告最小同步：巨潮《2026 年半年度业绩预告》确认 301308.SZ 江波龙 2026H1 预计归母净利润 92.00-110.00 亿元、扣非净利润 90.00-105.00 亿元、营业收入 220.00-250.00 亿元，原因落在下游需求增加、全球存储晶圆产能总体增长有限、与全球主要存储晶圆原厂续签 LTA/MOU，以及 SPU 主控芯片、HLC 软件架构和自有高端封测产能支撑端侧 AI 存储需求。全链层只把它落到 `HBM / server DRAM / LPDRAM / NAND / enterprise SSD / AI server parts` 主链的 A 股公司侧验证和业绩弹性增强，不新增公司卡、不升级为江波龙长期利润率或持续高增长结论；继续盯存储晶圆 LTA/MOU 覆盖期限、实际采购价格、端侧 AI 存储放量、mSSD/HLC/SPU 对 ASP/毛利的真实贡献、经营现金流和库存。
2026-07-03 高端 MLCC 证据缺口同步：7 月 1 日上海证券报/新浪转引国巨涨价与代理商核验，叠加 TrendForce 6 月高端 X6S 结构性偏紧线索，只能作为行业侧 `credible_secondary / lead_only` 和交易催化；风华高科 6 月 30 日严重异常波动公告反而强化了公司侧边界，明确全线暂停接单和英伟达认证传闻不属实、新兴市场营收占比不超过 15%。本地 HT 日线显示风华、三环在 7 月 1-2 日均出现高波动；该行情只解释交易弹性和拥挤，不证明 A 股公司 AI server 客户、料号、订单、ASP、收入占比或毛利率兑现。全链层维持 `High-end MLCC / X6S / AI power passives = future_watch/watch_to_soft`，不升级为 hard。
2026-06-28 存储涨价时间线最小沉淀：新增 [2026-06-28_storage_price_timeline.md](2026-06-28_storage_price_timeline.md)，按 HBM / server DRAM / LPDDR / NAND / enterprise SSD / HDD 拆分启动时点、供需驱动、相互传导和证据层级；不新增 A 股订单、客户、收入或利润兑现判断。
2026-06-28 全链周报完成：新增 [2026-06-28.md](2026-06-28.md)，覆盖 2026-06-22 至 2026-06-28。全链层吸收光模块专项 2026-06-28、AI PCB 专项 2026-06-28、Micron FQ3 FY26 官方财报/prepared remarks、存储涨价时间线、FERC/Google/NVIDIA 电力液冷证据；该期只深挖 `memory/storage/LPDRAM/eSSD + HBM test/probe` 与 `data-center power/liquid/800VDC`，不重复展开光模块和 PCB 专项细节。

2026-06-22 08:53 邮件窄口径复核：建滔 CCL 单张毛利 80 元、铜冠 HVLP4 涨价和 HVLP5 送样、生益科技/南亚新材映射，均不改变全链主排序。邮件本身作为 `mixed-source / lead_only`；和沪电 IR、Mitsui、Co-Tech 证据合并后，只能更收敛地维持 AI PCB 材料链 `soft+ / watch_to_soft`，不能升 hard。全链层最关键 source gap 仍是 A 股公司在 M8/M9/M10 CCL、HVLP4/5、高频高速树脂上的分产品收入、ASP/加工费、毛利率和客户认证闭环。

2026-06-23 公司跟踪窄口径吸收：[长飞光纤 601869.SH](../../company_tracking/601869.SH/state.md) 异动公告只确认 AI 数据中心光纤光缆价格波动需结合市场环境、业务结构、订单、收入拆分和毛利率判断，不升级为光纤短缺或业绩兑现；[鼎通科技 688668.SH](../../company_tracking/688668.SH/state.md) 可转债进入 2026-06-24 配售/申购执行，只作为融资和扩产执行节点，不等于高速通讯连接器或液冷客户订单、产能消化、收入占比、毛利率兑现。对应日更汇总见 [2026-06-23 公司跟踪报告](../../company_tracking/2026-06-23.md)。本次不改变全链主排序。

2026-06-25 Micron 财报后最小吸收：Micron 官方 FQ3 2026 财报和 earnings call prepared remarks 确认 FQ4 指引大幅高于财报前基线，并把 DRAM/NAND/HBM/eSSD 紧张从“财报前待验证”收紧为 `confirmed_official` 主链证据；但官方未点名 HBM test/probe/Cube Prober、雅克科技、精测电子或 A 股公司订单。2026-06-24《AI产业链战报》仍为 `Grok未经审计 / mixed-source / lead_only`；SemiAnalysis 2026-06-23 CXMT 公开页只能作为 `credible_secondary / competition_watch`，提示 2028+ 标准 DRAM 竞争和价格天花板风险，不抵消 Micron 对 `2026-2027` 供需紧张的官方表述。

2026-06-25 长飞光纤最小核验卡窄口径吸收：[长飞光纤 601869.SH](../../company_tracking/601869.SH/state.md) 已把 08:49《AI产业链战报》中的 G.657.A2 涨价、Corning-Amazon/NVIDIA/Meta 长单和“中国厂商定价权”拆成 `confirmed_official / credible_secondary / lead_only` 三层。全链层只把高密度数据中心 optical fiber/cable/connectivity 的观察层边界再强化一次：Corning 长单和 G.657.A2 行业涨价可以支持行业景气、锁产能和价格观察，但仍不能写成长飞新增客户订单、数据中心收入拆分、G.657.A2 实现 ASP 或毛利兑现；不改变全链主排序。

2026-06-28 光纤上游窄口径同步：长飞公司卡进一步把普通光纤/光缆、预制棒/光棒、高纯石英材料、高密度数据中心连接/被动件四层拆开。全链层只把 `A2/G.657.A2 光棒/预制棒` 从泛光纤景气中单独列为更强的涨价/供给收紧观察层，并把高纯石英材料写成上游成本压力线索；普通光纤光缆景气、石英材料紧张、Corning 长协和高密度 connectivity 锁产能仍不能升级成长飞订单、收入、实现 ASP 或毛利兑现，不改变主堵点账本和排序。

2026-06-25 SK hynix / ASML EUV 光学元件线索最小吸收：新增 [茂莱光学 688502.SH 最小跟踪卡](../../company_tracking/688502.SH/state.md)。DART 确认 SK hynix EUV scanner 采购和 DR/ADR 资金用途包含 EUV scanner、Yongin 半导体集群一期 fab、Cheongju P&T7 Advanced Packaging fab，能强化 `晶圆制造与先进制程服务 > EUV lithography scanner / ASML 单一供应商节点` 的 capex 观察；但不能直接写成茂莱光学 ASML/SK hynix 订单、EUV scanner 指定部件收入占比或毛利兑现。福晶科技仅保留为邮件中的长期 EUV 光源晶体材料线索，本次不扩写公司卡、不改变全链主排序。

2026-06-25 Corning GlassBridge / 沃格光电 TGV-CPO 窄口径吸收：新增 [沃格光电 603773.SH 最小跟踪卡](../../company_tracking/603773.SH/state.md)。Corning 官方产品页、手册和 OFC 2026 材料只确认 GlassBridge 是面向 Fiber-to-PIC、NPO/CPO 和高密度 photonic modules 的玻璃接口/连接平台；The Elec 对 2026-06-24 展示的报道只能作为会议展示补充。沃格公司侧可确认 TGV/GCP、光模块/CPO 玻璃基封装载板、1.6T/CPO 合作开发、批量送样和 `5μm / 100:1` 等公开口径；2026-06 异动公告明确泛半导体仍处早期、研发验证或送样验证、尚未规模化工业量产、营收占比极低。全链层只强化 `CoPoS/FOPLP/glass core/TGV` 观察层，不升 hard，不把 `3μm / 150:1`、Corning/NVIDIA/Apple/Samsung 客户、订单、收入或毛利写成事实。

2026-06-26 公司跟踪 canonical 筛选：对应 [2026-06-26 公司跟踪报告](../../company_tracking/2026-06-26.md) 与四张公司卡。宏和科技 603256.SH 的 6 月 27 日 T+1 异常波动公告、无应披未披回复、UNICORN ACE 减持比例由 2.0% 下修至 1.5% 和 6 月 26 日龙虎榜，只进入“高端电子布/Low CTE 交易拥挤与筹码供给风险”边界，不改变 `高端电子玻纤布 / Low Dk / Low CTE / T-glass` 的 `soft_bottleneck+` 等级，也不写成 Low CTE/T-glass 客户、订单、价格、收入占比或毛利兑现。德福科技 301511.SZ 的同规格、同卖方席位大宗交易继续留在交易结构/减持线索，归属和剩余额度待后续官方减持进展确认，不升级 HVLP/RTF 客户认证、正式订单、收入占比或毛利率。中际旭创 300308.SZ 的两笔平价大宗交易只作为高价位机构换手观察，不改变 1.6T/800G、硅光、客户需求、上游物料或毛利率主线。麦格米特 002851.SZ 正式向港交所递交 H 股申请并刊发申请资料，申请版本确认其为某全球 GPU / AI 计算基础设施龙头 AIDC 电源 `designated supplier` / `recommended supplier`，并披露 800V HVDC MW 级 rack power、Sidecar / Power Shelf / CRPS / PDB / BBU / CBS 系统级产品矩阵和主要海外客户量产交付，进入 `800VDC / rack power / AI 数据中心电源` 的资本平台与募资用途跟踪，但仍是 `watch+ / catalyst_watch`，不升 `main_candidate`，不写成 NVIDIA/Google/云厂客户订单、收入占比、毛利率或交付节奏兑现。本次不改变全链主排序和堵点账本。

## 任务边界

本任务负责 AI 产业链横向雷达、堵点账本、赛道优先级和上市主体映射，不重复展开光模块和 AI PCB 专项细节。每次执行必须读取：

- `artifacts/weekly_chain_tracking/ai_chain/state.md`
- `artifacts/weekly_chain_tracking/ai_chain/BASELINE_TEMPLATE.md`
- `artifacts/weekly_chain_tracking/ai_chain/` 下最近一期日期报告
- `artifacts/weekly_chain_tracking/optical_module/state.md`
- `artifacts/weekly_chain_tracking/ai_pcb/state.md`

堵点定义：必须意味着需求超过合格供给、可用产能、良率、交付能力或客户认证供应商。高壁垒、高毛利、高 HHI、长认证周期或股票热度不能单独作为堵点。

对话窗口摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`。

## 2026-07-26 当前全链结论

1. `云计算有效容量 + 服务器 CPU / memory / substrate / storage / parts` 为当前第一优先级 `hard_bottleneck`。Alphabet 明确需求仍超过新增容量、需以第三方容量过桥；Intel 明确需求超过可供产品，内部产能及行业 memory/substrate/关键部件短缺预计至 2027；Micron、Dell、HPE 的既有 A 级证据继续支持 DRAM/NAND/eSSD/parts 约束。Alphabet 不能外推到具名 GPU/HBM 供应商；Intel 的广义 memory/substrate 不能拆成 HBM、DRAM、NAND、eSSD、ABF 或 BT。
2. `先进制程逻辑 + 先进封装 / 后端测试` 新升级为 `hard_bottleneck`。TSMC 明确先进制程供需缺口很大、后端仍短缺且缺口更大、客户产品所需 testers 处于短缺。精确持续期 `N/A`；替代基板/封装路径约仍需一年成熟。TSMC 通用 tester 语境不能升级 HBM test/probe/Cube Prober。
3. 光模块专项把当前 hard 收窄为 `200G/lane EML + 合格 InP substrate/epiwafer/器件前道`，预计公司端 2026H2 边际改善、系统性约束观察至 `2027H1`；模块核心料齐套 `soft/easing`，CPO 主动对准/OWAT/WLBI `watch_to_soft`。
4. AI PCB 专项确认高频高速铜箔整体 `soft_bottleneck+`、HVLP4 `soft`，高端电子布及 M8-M10 CCL `soft+`，PCB 光刻胶公司级 `soft`/链级 `watch_to_soft`；仍无任何 PCB `hard_bottleneck`。
5. 数据中心电力链需分层：美国重点区域并网为 `hard operational`；GE Vernova 自身燃机槽位为公司级 hard、全球行业缺口 `N/A`；变压器/开关柜/变电站设备 `soft+`；液冷设施集成 `watch_to_soft`，未见全行业延期/配额闭环。

### 当前 5 个重点赛道与账本

| 节点 | 状态 | 本期变化 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|
| 云计算有效容量 | `hard_bottleneck` | Alphabet 新增 A 级确认 | 至少未来数季；解除 `N/A` | 不再称 demand > capacity；第三方过桥退出；backlog/CapEx 不再同步上修 | 跟 Alphabet Q3 与其他 CSP |
| 服务器 CPU + 广义 memory/substrate/parts | `hard_bottleneck` | Intel 新增 A 级交叉验证；Micron/Dell/HPE 基线维持 | Intel 至 2027；memory/storage `2026H2-2027` | 取消供给不足表述；库存恢复；预付款、定金和提前锁量下降 | SK hynix 7/29 Q2；Intel/Dell/HPE/ODM |
| 先进制程逻辑 + 后端先进封装/测试 | `hard_bottleneck` | **由 soft/watch 升 hard** | 精确时点 `N/A`；替代路径约一年成熟 | TSMC 不再称后端短缺/封装限制客户增长/tester shortage；交期恢复 | 跟 TSMC/OSAT/ATE 同节点证据，不跨到 HBM test |
| 200G EML + 合格 InP 前道 | `hard_bottleneck` | hard 口径收窄并增强 | `2026H2-2027H1`；精确缺口 `N/A` | 订单—交付缺口消失；预付款/优先权取消；二供认证 | 交光模块专项跟天孚/中际/新易盛与 AXT/Coherent/IQE |
| 高频高速铜箔/高端电子布/高阶 CCL | `soft_bottleneck+` | 铜箔由 watch_to_soft 升 soft+；其余维持 | 至少贯穿 2026；正常化 `N/A` | 加工费/报价回落、配额与安全库存取消、多料号认证、交期恢复 | 交 PCB 专项拆 HVLP3/4/5、Q cloth、M10 |
| 数据中心并网 | 区域 `hard operational` | 维持并强化区域口径 | `2026-2028+` | 排队周期缩短、已获电容量兑现、弃建率下降 | 跟 FERC/PJM/ERCOT、现场发电 |
| 变压器/开关柜/变电站 | `soft+` | GE Vernova 提供多年积压 A 级样本 | 至少 `2027-2028` | book-to-bill<1、积压下降、交期正常 | 增加第二家设备厂/utility 交叉验证 |
| 液冷设施集成 | `watch_to_soft` | Vertiv 扩产与集成实验室强化观察，不升 hard | `2026H2-2027 watch` | 多厂商认证、交付周期与故障率稳定 | 跟项目级联调、延期和故障率 |

### 本期深挖方向

1. `云容量 -> server CPU/memory/storage/parts`：用 Alphabet、Intel、Micron、Dell、HPE 建立“下游 demand > capacity—中游可供产品不足—上游长协/预付款锁量”的跨层闭环；严格保留 product-grade 缺口。本周 HBM/DRAM/NAND/eSSD 新细分证据 `N/A`，待 SK hynix 2026-07-29 官方结果。
2. `先进制程逻辑 -> 先进封装 -> 后端测试`：TSMC 的需求缺口、后端 shortage 和 tester shortage 满足 hard 定义；但精确持续期、tester 类别、供应商和订单均 `N/A`。公司同时表示扩产计划没有被设备供应整体卡住，这是反对“全设备 hard”的重要缓解证据。

### 未来 6-24 个月卡点迁移

| 潜在节点 | 当前状态 | 预计窗口 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|
| HBM final/package test、probe card、Cube Prober | `watch_to_soft` | `2026H2-2027H2` | 内存厂点名出货限制，或两家供应商披露 lead time/allocation/延期 | 内存厂不点名；ATE/probe/handler 交期回落、二供顺畅 |
| CPO 主动对准、OWAT/WLBI、光电联合测试 | `watch_to_soft` | `2027-2028` | 客户量产延期、设备排队、专项合同/验收收入或良率拖累 | 多家设备批量验收、良率稳定 |
| HVLP5/Q cloth/M10 + 成品板良率/测试 | `soft/watch` | `2027H2-2028` | 分等级 allocation/涨价/延期或板厂点名良率 | 多源量产、价格/交期回落、良率改善 |
| 800VDC/SST/GaN/SiC + 液冷设施集成 | `watch_to_soft` | `2027-2028` | design win 转量产，或设施联调限制投产 | 传统架构满足；多厂商认证和故障率稳定 |
| 102.4T networking silicon/retimer/substrate | `strategic_watch` | `2026H2-2027` | 官方披露 silicon/substrate/package allocation 或客户延期 | 交付顺畅、客户不延期、封装/基板扩产跟上 |
| 玻璃/替代基板、CoPoS/FOPLP/TGV | `long_horizon_watch` | `2027-2028+` | 客户认证、量产良率、设备订单与产能上修 | CoWoS 扩产满足，替代路径延期 |
| 高端 MLCC/X6S/AI power passives | `future_watch` | `2026H2-2027` | 两家以上龙头披露 AI 料号、lead time、allocation/涨价 | 扩产兑现、价格不涨、lead time 正常 |

### 三类排名快照

- 结构重要性：①云容量+服务器 CPU/memory/storage/parts；②先进制程+先进封装/测试；③200G EML/InP；④并网/电气/液冷/800VDC；⑤高频高速 PCB 材料。
- 业绩弹性：①memory/storage 直接供应商；②200G EML/InP 与模块交付释放；③高频高速 PCB 直接材料/板厂；④先进封装/测试有效产能及缓解设备；⑤电气/firm power/液冷。未重建全体公司事件前点时共识，正式超预期 `N/A`。
- 交易弹性（专项 2026-07-24 收盘快照）：①A 股光模块/InP/CPO 设备；②A 股 AI PCB/HVLP/高端布/CCL；③A 股电力/液冷/800VDC；④US/KR/TW memory/foundry/advanced packaging；⑤US networking/custom ASIC。行情只描述交易属性，不证明卡点兑现。

### 下期默认跟踪问题

1. SK hynix 2026-07-29 Q2 是否拆出 HBM/DRAM/NAND/eSSD 的售罄期、allocation、价格、认证与 2027 供给？Samsung/Kioxia/Micron 是否交叉确认？
2. TSMC/OSAT/ATE/handler/probe card 是否披露后端 tester 的具体类别、lead time、追加订单或客户延期？是否继续排除对 HBM test 的跨节点外推？
3. Intel、Dell、HPE/ODM 是否继续披露 CPU、memory、substrate、SSD 和其他 parts 对 backlog 转收入的限制；Alphabet 第三方容量能否按期过桥？
4. 200G EML 缺料是否在 H2 转为交付/毛利改善；AXT/Coherent/IQE/云南能否披露 6 英寸良率、认证和可售出货？
5. 能否获得第二家板厂对同一 HVLP/电子布/CCL 等级的交期/allocation 交叉确认；并网、电气设备和液冷能否给出项目级延期、交期或故障率？

### 2026-07-26 主要新增来源

- Alphabet Q2 earnings transcript: https://s206.q4cdn.com/479360582/files/doc_events/2026/Jul/22/2026_Q2_Earnings_Transcript.pdf
- Alphabet Q2 10-Q: https://www.sec.gov/Archives/edgar/data/1652044/000165204426000071/goog-20260630.htm
- TSMC Q2 official page: https://investor.tsmc.com/english/quarterly-results/2026/q2
- TSMC Q2 transcript: https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-07/547d1696765e05ce3adb81c108ce1c8c1682b80c/TSMC%202Q26%20Transcript.pdf
- Intel Q2 10-Q: https://www.sec.gov/Archives/edgar/data/50863/000005086326000157/intc-20260627.htm
- GE Vernova transcript: https://www.gevernova.com/sites/default/files/gev_webcast_transcript_07222026.pdf
- 光模块专项：`artifacts/weekly_chain_tracking/optical_module/2026-07-26.md`
- AI PCB 专项：`artifacts/weekly_chain_tracking/ai_pcb/2026-07-26.md`
- 本期全链周报：`artifacts/weekly_chain_tracking/ai_chain/2026-07-26.md`

### 2026-07-26 对话窗口摘要

| 当前核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| 云容量 + 服务器 CPU/memory/storage/parts | 算力需求与 backlog 快于服务器、数据中心、网络和关键部件交付 | Alphabet、Intel、Micron、Dell/HPE 官方披露 | 数季至 2027；细分解除 `N/A` | 不再称需求超过容量/供给；库存恢复、预付款与提前锁量弱化 |
| 先进制程 + 先进封装/后端测试 | 先进制程与后端有效产能不足、测试机短缺 | TSMC 2026Q2 官方业绩会 | 精确时点 `N/A`；替代路径约一年成熟 | 后端不再短缺、testers 交期恢复、替代方案认证量产 |
| 200G EML + 合格 InP 前道 | 合格芯片、6 英寸扩产、良率、老化和认证限制模块交付 | 天孚/中际/新易盛 + AXT-Coherent | `2026H2-2027H1`，精确缺口 `N/A` | 订单—交付缺口消失、二供认证、预付款/优先权取消 |
| 高频高速 PCB 材料组合 | HVLP、特种布、树脂受工艺、良率、合格产能和 AVL 约束 | 铜冠、沪电官方披露 | 至少贯穿 2026；正常化 `N/A` | 加工费/报价回落、配额取消、多料号认证、交期恢复 |
| 区域并网 + 电气设备 | 接入制度、输配电建设和设备多年积压限制项目投产 | FERC、GE Vernova | 并网 `2026-2028+`；设备至少 `2027-2028` | 排队/交期缩短、积压下降、已获电容量兑现 |

| 未来潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| HBM test/probe/Cube Prober | HBM4/HBM4E 增加 KGD、stack/final test 负荷 | 只有负荷逻辑；TSMC 通用 tester 不可跨节点 | `2026H2-2027H2` | 内存厂点名或两家供应商披露 allocation/延期 | ATE/probe/handler 交期回落、二供顺畅 |
| CPO 对准/OWAT/WLBI/联合测试 | 光引擎与封装整体良率窗口收窄 | 设备路线推进；缺客户量产延期、合同和良率 | `2027-2028` | 客户延期、设备排队、专项验收收入或良率拖累 | 多家批量验收、良率稳定 |
| HVLP5/Q cloth/M10 + 成品板良率 | 224G+ 材料组合和加工窗口同步收窄 | 当前 soft/watch；具体等级有效产能 `N/A` | `2027H2-2028` | 分等级 allocation/涨价/延期或板厂点名良率 | 多源量产、价格/交期回落、良率改善 |
| 800VDC/SST/GaN/SiC + 液冷设施集成 | MW rack 推高供电转换、设施水环和整站可靠性难度 | 方向与扩产成立；全行业延期证据不足 | `2027-2028` | design win 转量产或集成限制投产 | 传统架构继续满足；多厂商认证和故障率稳定 |
| 玻璃/替代基板、CoPoS/FOPLP/TGV | 大封装面积/成本压力，但工艺良率与认证慢 | TSMC 称约仍需一年成熟，当前非有效供给 | `2027-2028+` | 客户认证、量产良率、设备订单和产能上修 | CoWoS 扩产满足、替代路径延期 |

## 2026-06-28 上期全链结论（历史基线）

1. `HBM / server DRAM / LPDRAM / NAND / enterprise SSD / AI server parts supply` 维持全链最硬 `hard_bottleneck`。Micron FQ3 2026 官方财报/业绩会将 `FQ4 revenue 50.0B USD ± 1.0B / gross margin ~86% / non-GAAP EPS 31.00 ± 1.00`、data center SSD 收入超过 50 亿美元且环比翻倍、DRAM/NAND 需求显著超过供给、紧张延续到 `calendar 2027` 之后、16 份 SCA/RPO/客户押金共同写成 A 级证据。预计 `2026H2-2027全年` 偏紧；2028 只写边际改善观察，不写短缺解除；中高置信。
2. `HBM final/package test / memory probe card / Cube Prober` 维持 `watch_to_soft / soft_bottleneck_candidate`，不升 hard。Micron 官方确认 HBM4 12-high ramp、HBM4 收入超过 10 亿美元和新加坡先进封装/HBM packaging capacity 2027H1 贡献路径，但未点名测试/探针/Cube Prober 交期、allocation 或供应商订单；The Elec/Techwing/MJC 仍需合同金额、数量、交期和内存厂官方瓶颈表述。预计 `2026H2-2027H2`，精确交期 `N/A`，中置信。
3. 光模块专项吸收结论：`InP substrate / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS` 维持 `hard_bottleneck`。预计 EML/InP `2026H2-2027H1`，CW/ELS/UHP 尾部 `2027H2-2028H1`。
4. AI PCB 专项吸收结论：本期不升级任何 PCB 节点为 hard；`高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth` 与 `M7/M8/M9/M10 CCL / prepreg` 维持 `soft_bottleneck+`。沪电股份 2026-06-18 IR 强化高端材料阶段性偏紧证据。
5. `数据中心电力 / 并网 / transformer / switchgear / UPS / busway / rack power / CDU / 冷板 / 800VDC` 维持 `soft_bottleneck`，区域并网按 `regional hard operational bottleneck`。FERC 2026-06-18 大负载行动和 Google Brazos 提供 A 级方向证据；NVIDIA 800VDC 仍为 2027 起架构迁移观察。
6. `高端 MLCC / X6S / AI power passives` 新增为 `future_watch/watch_to_soft`。TrendForce 线索说明 2H26 起可能出现结构性短缺，但缺供应商官方 allocation、客户料号和公司收入拆分。

## 2026-06-28 专项吸收状态（历史）

| 专项任务 | 最新状态 | 本期吸收结论 | 对全链排序影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | InP/6 英寸合格 InP/EML/CW-DFB/UHP/ELS 为 hard；整机装配 soft/eased；FAU/主动对准/WLBI/ELSFP thermal 为 future watch；长飞光纤 2026-06-24 异动公告和 2026-06-25 最小核验卡只补充 AI 数据中心光纤价格、Corning 锁产能和毛利验证边界。 | 光源链排当前核心卡点第 2；1.6T/3.2T driver/TIA/DSP/GaN/FAU/热管理列未来迁移；长飞不改变排序。 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | 高端电子玻纤布与 M7-M10 CCL/prepreg 并列 soft+；HVLP4/5、高频高速树脂、板厂良率/测试为 watch_to_soft。 | PCB 材料链排当前核心卡点第 3；M9/M10/Q cloth/HVLP/板厂测试列未来迁移。 |

## 2026-06-28 全链堵点账本（历史）

| 节点 | 状态 | 造成堵点的机制 | 本期变化 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|
| HBM / server DRAM / LPDRAM / NAND / enterprise SSD / AI server parts | `hard_bottleneck` | AI server、agentic inference、custom ASIC 和 AI cloud buildout 需求超过 qualified memory/storage/parts 供给；DRAM allocation、HBM stack/test、LPDRAM allocation、eSSD qualified output、SCA take-or-pay 和客户押金共同约束。 | strengthened_post_micron + 301308_H1_preview_company_side_validation | `2026H2-2027全年` 偏紧；2028 渐进改善但 Micron 尚无供给追上需求视野；中高置信 | FQ4 价格涨幅放缓后继续回落、库存恢复、多供方认证、客户不再提前锁量、SCA 押金/订单弱化、ODM 不再提 parts constraint | 跟 Micron FQ4 实际兑现、SCA RPO/押金、DRAM/NAND/eSSD 合约价、Samsung/SK hynix/Kioxia/SanDisk LTA 与库存；江波龙只作为存储周期景气、供应协议续签和端侧 AI 存储产品的公司侧验证，需核实 LTA/MOU 覆盖期限、实际采购价格、端侧 AI 存储放量、mSSD/HLC/SPU 对 ASP/毛利的真实贡献、经营现金流和库存。 |
| HBM final/package test / memory probe card / Cube Prober | `watch_to_soft / soft_bottleneck_candidate` | HBM4E/HBM4/custom HBM 提高 KGD、stack/final test、探针卡和 Cube Prober 负荷；Micron 只确认 HBM4 ramp 与 2027H1 新加坡 HBM packaging capacity，未确认测试/探针成为出货限制。 | boundary_tightened_post_micron | `2026H2-2027H2`；精确交期 `N/A`；中置信 | 内存厂未点名测试瓶颈、Techwing/MJC/ATE backlog 或交期回落、二供扩产兑现 | 跟 Techwing DART/公告、MJC、Advantest、Teradyne、FormFactor、Technoprobe、MPI、精测电子同节点订单/收入。 |
| NOR Flash / SLC NAND / 高可靠小容量存储 | `formal_observation/watch+` | HBM 和高层 3D NAND 抢占产能后，成熟节点 NOR/SLC 供给被挤压；边缘 AI、汽车、工业和高端网络需求拉动可靠存储。 | unchanged | `2026H2`，若 LTA 强化可延到 `2027`；中置信 | NOR/SLC 报价回落、补库结束、三家公司毛利/净利回落 | 跟 TrendForce 报价、兆易创新/东芯股份/普冉半导体 H1/H2 财报。 |
| InP substrate / 6 英寸合格 InP / EML / CW-DFB / UHP / ELS | `hard_bottleneck` | 出口许可、InP 衬底集中、6 英寸良率、老化测试、capacity rights、客户认证和 ELS 热稳定共同约束。 | unchanged | EML/InP `2026H2-2027H1`；CW/ELS/UHP 尾部 `2027H2-2028H1`；中高/中置信 | 许可正常化、6 英寸良率兑现、二供认证、交期/allocation/价格回落 | 交给光模块专项追 AXT/Coherent/Lumentum/Ciena/Corning。 |
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER / Q cloth | `soft_bottleneck+` | 窑炉、拉丝、电子级纱、织布、后处理、良率、专利和客户 AVL 限制 qualified output。 | strengthened | `2026H2-2027年底`；Q cloth/NER `2027H2-2028 watch`；中高置信 | 高端布报价回落、交期缩短、库存恢复，多供应商进入核心 AVL | 交给 PCB 专项跟台玻/Nittobo/高端布分产品。 |
| M7/M8/M9/M10 CCL / prepreg | `soft_bottleneck+` | 超低损耗树脂、高端玻纤布、HVLP 铜箔、新线 qualified output 和客户认证共同约束。 | strengthened | `2026H2-2027H1`；中高置信 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入 AVL | 跟沪电、生益、台系 CCL、M8/M9/M10 lead time。 |
| HVLP4/5 铜箔与高频高速树脂 | `watch_to_soft` | 低粗糙度一致性、表面处理、树脂配方和客户认证约束；批量证据不足。 | mixed_source_increment_no_upgrade | `2026H2-2027 watch`；精确持续 `N/A` | 多客户批量供货、加工费回落、国产良率确认 | 跟德福、诺德、嘉元、铜冠与树脂供应商；铜冠 2026-06-22 邮件线索需公告/IR/客户侧验证。 |
| 数据中心并网 / firm power / grid operations | `soft_bottleneck`；区域 `hard operational` | 大负载接入、成本分摊、电源与输配电建设、备用容量、动态负载稳定性约束。 | strengthened | 区域 `2026H2-2030`；中高置信 | reserve margin 改善，容量/电价压力回落，真实项目延期减少 | 跟 FERC/PJM/ERCOT/utility；项目级核对 site control、interconnection、permit、construction、equipment order/prepayment。 |
| Transformer / switchgear / UPS / busway / rack PDU / CDU / 冷板 | `soft_bottleneck/watch` | 高功率 rack、新建 AI factory 与存量风冷机房逐机架改造共同拉动长交期设备、系统认证和现场集成。 | strengthened | `6-24 个月`；单品精确交期 `N/A`；中置信 | 设备交期正常化，项目不再因设备延期；已锁队列订单取消且 slot 无法再分配 | 跟单品 lead time、预付款/排产锁定、Chinese OEM/prefab、Brazos/OCP 规格、A 股收入拆分。 |
| 800VDC / SST / SiC / GaN power conversion | `watch_to_soft` | 高功率 rack 推动 medium-voltage-to-rack、GaN/SiC、hot-swap/protection 和系统认证。 | attention_up | `2027-2028`；精确持续 `N/A` | 800VDC 推迟，传统架构继续满足；design win 无法转收入 | 跟 NVIDIA ecosystem、Delta/Lite-On/Megmeet、麦格米特等 design win 转量产。 |
| CoWoS / EFB / SoIC / advanced packaging / substrate | `soft_bottleneck/watch+` | GPU/ASIC multi-die 和 HBM 需求推高 2.5D/3D 封装、基板、键合、测试和设备负荷；Micron 新加坡 advanced packaging center 预计 2027H1 开始贡献 HBM packaging capacity，是供给缓解路径而非当前短缺解除。 | micron_supply_path_added | `2026H2-2027H1` 偏紧，2027 后边际缓解 | TSMC/OSAT/Micron HBM packaging 交期恢复，客户不再锁封装产能 | 跟 TSMC/ASE/Amkor/基板/设备、Micron Singapore HBM packaging ramp。 |
| AI networking switch ASIC / NIC / DPU / retimer / custom XPU | `strategic_watch/watch_to_soft` | Broadcom/Marvell/NVIDIA/Oracle 需求强，但缺 silicon allocation、lead time 或出货受限证据。 | attention_up | `N/A`；出现 allocation 后升级 | 出货顺畅，客户部署不推迟 | 跟 Broadcom/Marvell/NVIDIA/Arista。 |
| High-end MLCC / X6S / AI power passives | `future_watch/watch_to_soft` | AI ASIC/accelerator 板卡功率上升，带动小尺寸高容高温 MLCC 用量和可靠性要求。 | 7/1_price_hike_lead_no_upgrade | `2026H2-2027` 可能升级；中置信 | 扩产兑现、价格不涨、lead time 正常、客户多源认证顺利 | 跟村田/TDK/三星电机/国巨/风华高科/三环集团订单、料号、ASP、毛利；A 股公司未披露前不写经营兑现。 |

## 2026-06-21 芯碁微装先进封装设备最小跟踪卡

新增：[芯碁微装 688630.SH 最小跟踪卡](../../company_tracking/688630.SH/state.md)。定位为 `advanced_packaging_equipment_watch / evidence_gap_card`。可确认的是 WLP/PLP/IC 载板直写光刻设备、WLP 2000 重复订单/出货与多个头部客户验收量产、WLP 在手订单突破 1 亿元的 B 级公司官微转述；不能把 SK 海力士清州 HBM4 封装备产、Amkor-TSMC 美国先进封装协议或类 CoWoS-L 量产线索直接写成芯碁微装 HBM4/CoWoS 客户、订单、收入占比或交付节奏。

## 2026-06-22 三环集团高端 MLCC 最小跟踪卡

新增：[三环集团 300408.SZ 最小跟踪卡](../../company_tracking/300408.SZ/state.md)。定位为 `secondary_track_up / fundamental_main_beneficiary_candidate / evidence_gap_card`。可确认的是 AI server 高端 MLCC/X6S 与 AI power passives 需求上行已进入 `future_watch/watch_to_soft`，且既有 MLCC 次主线材料把三环集团列为更偏基本面主受益候选；不能把行业侧高端 MLCC 交期、TAM、涨价或 Rubin 价值量线索直接写成三环集团 AI server 客户、料号、订单、收入拆分或毛利兑现。

## 2026-06-22 联动科技 HBM 测试链线索卡

新增：[联动科技 301369.SZ 最小跟踪卡](../../company_tracking/301369.SZ/state.md)。定位为 `ai_soc_test_equipment_watch / hbm_test_chain_lead_only / event_trade_watch`。可确认的是 HBM test/probe/handler 链条仍处 `watch_to_soft / soft_bottleneck_candidate`，且 2026-06-22 08:53 邮件新增 TSE 下一代 HBM handler 速度提升 2 倍线索；联动科技公司证据目前更偏 AI SoC 测试机 QT-9800/QT-9800EXA、天数智芯战略合作、功率/数模/SoC 测试系统和探针台，不能写成 HBM 客户、HBM handler、memory probe card/探针卡、订单、收入、ASP 或毛利兑现。

## 2026-06-22 盛美上海前道湿法/清洗设备国产替代最小跟踪卡

新增：[盛美上海 688082.SH 最小跟踪卡](../../company_tracking/688082.SH/state.md)。定位为 `front_end_wet_clean_domestic_substitution_watch / advanced_packaging_wet_process_order_watch / ai_hbm_direct_revenue_gap_card`。可确认的是公司具备前道湿法/清洗、电镀、先进封装湿法和面板级设备平台，且 2026-06-22 08:53 邮件新增“中国设备进口 -24%、日本设备商中国销售 -10%、SCREEN/Entegris/KLA 行情强化、盛美上海近 20 日 +77.7%”的国产替代交易线索；不能把这些线索或先进封装湿法/电镀订单直接写成 AI/HBM/CoWoS/CoPoS 客户、订单、收入占比、毛利率或交付节奏兑现。

## 2026-06-25 Micron 财报后最小核验卡

Micron 2026-06-24 盘后官方财报与 earnings call prepared remarks 已落地；本节替代 2026-06-22 财报前复核。

| 项目 | Micron 官方落地口径 | 对主链写入 | 边界收紧 |
|---|---|---|---|
| FQ4 指引 | FQ3 revenue `41.456B USD`，non-GAAP gross margin `84.9%`，non-GAAP EPS `25.11`；FQ4 指引为 revenue `50.0B USD ± 1.0B`、gross margin 约 `86%`、non-GAAP EPS `31.00 ± 1.00`。 | 从“财报催化待验证”上调为 `confirmed_official / beat_and_raise`；继续支撑 memory/storage 主 hard。 | FQ4 毛利率口径同时提示“price increase rate moderation”，所以 sell-the-news 风险从“财报不及预期”转为“高位拥挤、涨价斜率放缓、2027 供给扩张预期提前交易”。 |
| HBM / SCA / long-term supply | HBM4 12-high ramp 速度为 HBM3E 12-high 的约 2 倍，HBM4 收入已超过 `1B USD`；HBM4E 预计 `calendar 2027` 量产。16 份 SCA 覆盖 data center/consumer/auto，通常 5 年期，约覆盖 DRAM volume `20%`、NAND volume `1/3`，RPO 约 `100B USD`，现金押金/相关承诺约 `22B USD`。 | HBM、DRAM/NAND 长协锁量和客户预付款共同强化 `hard_bottleneck` 与周期韧性。 | 官方没有说“所有 2027 HBM 配额已被客户下单”，也没有点名 HBM test/probe/Cube Prober 交期或供应商订单；6/24 战报里 SK hynix 放缓 HBM4、微软 DDR5 大单、A 股设备材料传导均留 `lead_only`。 |
| eSSD / NAND / LPDRAM 持续性 | Data center revenue 超过 `25B USD`，data center SSD revenue 超过 `5B USD`且环比翻倍；DRAM/NAND demand 显著超过 supply，紧张预计延续到 `calendar 2027` 之后；G9 PCIe Gen6 data center SSD 高量产，245TB QLC SSD 开始出货，LP5X SOCAMM2 高量产。 | eSSD/NAND 从 B 级 TrendForce + 旧 Micron 口径收紧为 A 级官方确认；LP server DRAM/SOCAMM 是 AI memory hierarchy 的方向性增强。 | LPDRAM 仍需拆口径：`LP5X SOCAMM2 / LP server DRAM` 可以写入 AI server memory hierarchy，手机 LPDDR5X 价格暴涨和 A 股 LPDDR 传导不能直接升级为 Micron 官方 allocation 或 A 股公司订单。 |
| Capex / advanced packaging supply | FQ3 capex `7.1B USD`，FQ4 capex 约 `10B USD`，FY2026 capex 约 `27B USD`；FY2027 quarterly capex 将高于 FQ4，过半增量来自 construction capex。ID1 预计 `mid-CY2027` 首片晶圆、ID2 `late-CY2028`；Tongluo 预计 `mid-CY2027` 有意义出货；Singapore advanced packaging 预计 `2027H1` 开始贡献 HBM packaging capacity。 | 供给端不是“马上缓解”，而是 `2027+ capacity relief path`；先进封装/HBM packaging 维持 watch+，不证伪 2026-2027 tight。 | 对 A 股只写观察：不能把 Micron Singapore/Tongluo/Idaho capex 直接写成北方华创、雅克科技、精测电子或其他 A 股公司的订单、收入占比、毛利率。 |
| CXMT / SemiAnalysis 冲突处理 | SemiAnalysis 2026-06-23 公开页题名指向 CXMT IPO、process-node deficit、China HBM、wafer adds 和 memory LTAs，属于可跟踪竞争风险。Micron 官方则明确 2026-2027 DRAM/NAND 供需 tight beyond CY2027，并称 2028 也只是 gradual improvement。 | 主链保留 `2026H2-2027` hard，不因 CXMT 公开页降级。 | CXMT 只进入 `2028+ standard DRAM competition / China supply watch`，不能拿来写成 HBM/eSSD 即期供给解除，也不能外推到雅克/精测订单。 |

## 2026-06-28 深挖方向（历史）

1. `HBM/DRAM/LPDRAM/NAND/eSSD + AI server parts supply + HBM test/probe`：Micron 已用官方财报/业绩会收紧为 FQ4 指引、HBM4 ramp、SCA/RPO/押金、DRAM/NAND tight beyond CY2027、data center SSD revenue >5B USD、capex/advanced packaging supply path。主链 hard 加强，但 HBM test/probe/Cube Prober 和 A 股设备/材料订单仍缺官方同节点闭环。Samsung/SK hynix/Kioxia-SanDisk 仍需各自最新官方财报/业绩会确认 LTA、库存和 capacity allocation；继续跟 eSSD/LPDRAM、HBM4/HBM4E 认证、Techwing/MJC/ATE/probe card 交期和合同规模。
2. `AI cloud capex -> 数据中心电力/并网 + 液冷 + 800VDC`：重点把区域 hard operational 约束和全球设备/液冷单品 soft/watch 分开；跟踪 FERC/PJM/ERCOT、Oracle/Meta/Google/Microsoft/Amazon CapEx、Google Brazos/OCP、NVIDIA 800VDC、transformer/switchgear/UPS/CDU/PDU lead time、A 股订单纯度。

## 2026-06-28 未来 6-24 个月卡点迁移（历史）

| 节点/赛道 | 当前状态 | 未来状态 | 需求触发 | 供给滞后机制 | 可能时间 | 升级触发阈值 | 证据缺口 | 反转指标 |
|---|---|---|---|---|---|---|---|---|
| HBM test / memory probe card / Cube Prober | watch_to_soft | soft_bottleneck_candidate | HBM4E/HBM4/custom HBM、Rubin Ultra 和更高 stack/带宽要求 | KGD/stack/final test 时间增加、探针卡设计切换、Cube Prober 全检导入、客户 qualification | `2026H2-2027H2` | 内存厂或两家以上测试/探针卡/handler 供应商披露 lead time/allocation、客户预付、交期推迟或追加订单 | 官方交期/allocation、合同规模、A 股订单/收入 | MJC/Techwing/ATE 产能兑现、二供认证、HBM qualification 顺畅。 |
| Enterprise SSD / LPDRAM | hard side expansion | likely_future_bottleneck | AI Agent、long-context inference、CSP storage hierarchy | 低库存、订单超过产出、企业级 qualification 慢，DRAM wafer allocation 竞争；Micron 已确认 data center SSD revenue >5B USD、LP5X SOCAMM2 高量产 | `2026H2-2027全年` | eSSD 合约价继续上行、CSP LTA、内存厂点名供应紧张；LP server DRAM/SOCAMM 出现 allocation 或 SCA 明细 | 内存厂财报、客户 allocation、LP server DRAM 与手机 LPDDR 拆分 | 库存恢复，合约价回落，LP server DRAM/SOCAMM 不再被点名紧张。 |
| 高端 MLCC / X6S / AI power passives | future_watch | watch_to_soft | CSP 自研 ASIC、高功率 AI 板卡、电源完整性要求 | 高容高温小尺寸 MLCC 扩产和认证慢 | `2026H2-2027` | 两家以上 MLCC 龙头披露 AI server/ASIC 订单、lead time 拉长或涨价；A 股披露料号、收入占比 | 客户料号、ASP、毛利、库存、订单 | 扩产兑现、价格不涨、lead time 正常。 |
| 1.6T/3.2T optical driver/TIA/DSP/GaN/FAU/test/thermal | watch_to_soft | likely_future_bottleneck | 1.6T/3.2T、CPO/NPO/ELS | 高速 analog、精密耦合、测试节拍、热稳定 | `2026H2-2028` | 多供应商 lead time/allocation、客户预付、良率拖累 | 单品交期/良率 | 扩产兑现、二供认证。 |
| M9/M10/Q cloth/NER/HVLP4/5 | soft+/watch | likely_future_bottleneck | Rubin、AI switch、224G+ high-speed board | 新材料认证、AVL、良率和二供慢 | `2026H2-2028` | 官方 allocation、报价上涨、订单延期、客户提前锁料 | 分产品、客户、交期 | 多家供应商稳定量产，报价回落。 |
| 800VDC/SST/GaN/SiC + 存量风冷液冷改造 | soft/watch | likely_future_bottleneck | 高功率 rack、AI factory 投产、Brazos 类逐机架改造 | system certification、设备 lead time、现场集成、OCP/客户规格统一 | `2027-2028` | design win 转量产、Brazos/OCP 多供应商量产、云厂商存量改造项目 | 单品 allocation、项目清单、订单/收入拆分 | 800VDC 推迟、传统架构满足、存量改造难规模化。 |
| CoPoS/FOPLP/glass core/TGV | watch | long_horizon_watch | Package 面积和成本压力 | TGV、对位、翘曲、良率和设备生态 | `2027-2028+` | 试产通过、客户 tape-out、设备订单 | 量产良率、成本、客户产品、设备产能 | CoWoS 扩产满足需求，面板化延后。 |
| AI networking silicon / retimer / substrate | strategic_watch | watch_to_soft | 102.4T switch、NVLink Fusion、custom XPU | SerDes/IP、advanced process、substrate/package | `2026H2-2027` | silicon/substrate/package 被点名限制出货 | 直接交期证据 | 交付顺畅，客户不延期。 |

## 2026-06-28 三类排名快照（历史）

### 细分赛道结构重要性

1. HBM / DRAM / LPDRAM / NAND / eSSD / HBM test
2. Advanced packaging / CoWoS / SoIC / substrate
3. Data-center power / grid / rack power / liquid cooling / 800VDC
4. Optical source / InP / EML / CW + 1.6T migration
5. AI PCB / high-end glass cloth / CCL / HVLP
6. AI networking / custom ASIC / retimer / NIC/DPU
7. High-end MLCC / passives

### 业绩弹性

1. eSSD/NAND/DRAM/HBM 供应商
2. AI PCB 高端材料/板厂
3. 光源/InP/CW-DFB/1.6T 光互连
4. Power/liquid/rack power/800VDC
5. 高端 MLCC/passives
6. HBM test/probe/tooling

### 交易弹性

1. A 股 PCB/CCL/HVLP/高端材料组
2. A 股光模块/光器件/设备组
3. A 股 power/liquid/800VDC 组
4. NOR/SLC 国内存储侧翼
5. US/KR/TW memory/HBM 龙头
6. US networking/custom ASIC 龙头

## 2026-06-28 下期跟踪问题（历史）

1. HPE/Dell/SMCI/ODM 是否继续披露 DRAM/NAND/eSSD/parts supply constraints、purchase commitments、inventory 或 backlog 转收入受限？
2. Micron：下一步验证 FQ4 指引兑现、price increase rate moderation 是否只是涨价斜率放缓、SCA RPO/客户押金是否继续增长、FY2027 capex/advanced packaging supply 是否形成供给缓解；Samsung、SK hynix、Kioxia/SanDisk：仍需各自最新官方财报/业绩会确认 eSSD/NAND/LPDRAM/HBM 价格、LTA、库存和 capacity allocation。
3. Techwing、MJC、Advantest、Teradyne、FormFactor、Technoprobe、MPI 或内存厂是否披露 HBM test/probe/Cube Prober lead time、合同规模、追加订单或 allocation？
4. FERC/PJM/ERCOT/utility 是否给出大负载接入规则变化；Oracle/Meta/Google/Microsoft/Amazon 是否继续上修 AI CapEx 或披露电力/设备/液冷对投产节奏的影响？
5. Google Brazos 是否进入 OCP 规格、多供应商量产或云厂商存量机房改造项目；A 股液冷/电源/高速连接器公司是否披露真实客户、订单、收入和毛利；鼎通科技可转债发行结果、包销比例和募投执行不能替代订单验证。
6. 沪电、台玻、Nittobo、台系 CCL、建滔、生益、南亚、德福/诺德/嘉元/铜冠是否继续披露高端玻纤布、M8/M9/M10、HVLP4/5 交期、报价、客户认证、分产品收入和毛利？
7. TrendForce MLCC 线索能否被村田、TDK、三星电机、国巨、风华高科、三环集团等官方订单、料号、ASP 或收入拆分验证？

## 2026-06-28 证据源（历史）

- HPE 10-Q: https://www.sec.gov/Archives/edgar/data/1645590/000164559026000055/hpe-20260430.htm
- HPE Q2 FY26 transcript: https://investors.hpe.com/~/media/Files/H/HP-Enterprise-IR/documents/q2-2026/q2-2026-transcript.pdf
- TrendForce enterprise SSD: https://www.trendforce.com/presscenter/news/20260611-13092.html
- DRAMeXchange / TrendForce LPDRAM: https://www.dramexchange.com/WeeklyResearch/Post/2/12731.html?type=News
- TrendForce NOR Flash / SLC NAND: https://www.trendforce.com/presscenter/news/20260616-13102.html
- Micron FQ3 FY26 results press release: https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-record-results-third-quarter
- Micron FQ3 FY26 prepared remarks: https://investors.micron.com/static-files/631b1a32-5537-46ae-8f40-82e42fc79dfe
- Micron FQ3 FY26 presentation: https://investors.micron.com/static-files/2354ecda-77a0-4ddd-8462-a631eb491356
- SemiAnalysis CXMT public page: https://newsletter.semianalysis.com/p/chinas-cxmt-is-set-to-challenge-dram
- Micron FQ3 FY26 earnings call date: https://investors.micron.com/news-releases/news-release-details/micron-technology-report-fiscal-third-quarter-results-june-24
- Micron Q2 FY26 results and FQ3 guidance: https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-results-second-quarter-fiscal-2026
- Micron Q2 FY26 prepared remarks: https://investors.micron.com/static-files/e089f8c0-065d-47b8-9d02-bfa863cdb357
- Micron Q2 FY26 10-Q: https://www.sec.gov/Archives/edgar/data/723125/000072312526000006/mu-20260226.htm
- Micron Q1 FY26 prepared remarks: https://investors.micron.com/static-files/088991c5-a249-4f66-a0a6-258d9b66f3f9
- The Elec / Techwing Cube Prober: https://www.thelec.net/news/articleView.html?idxno=11441
- FERC large-load action: https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration
- Google Brazos: https://cloud.google.com/blog/topics/systems/brazos-liquid-cooling-system-for-air-cooled-data-centers
- Oracle FY26 results: https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/default.aspx
- Broadcom Q2 FY26 results: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-second-quarter-fiscal-year-2026-financial
- Marvell Q1 FY27 results: https://investor.marvell.com/news-events/press-releases/detail/1023/marvell-technology-inc-reports-first-quarter-of-fiscal-year-2027-financial-results
- NVIDIA 800VDC: https://www.nvidia.com/en-us/data-center/technologies/800vdc/
- NVIDIA developer blog 800VDC: https://developer.nvidia.com/blog/nvidia-800-vdc-architecture-will-define-the-next-generation-of-ai-factories/
- 沪电股份投资者关系记录: https://data.eastmoney.com/notices/detail/002463/AN202606181823669664.html
- TrendForce high-end MLCC: https://www.trendforce.com/presscenter/news/20260617-13105.html
- 上海证券报/新浪财经 2026-07-01 MLCC 龙头涨价: https://finance.sina.com.cn/wm/2026-07-01/doc-inifhrqu1008061.shtml
- 风华高科 2026-06-30 严重异常波动公告: https://static.cninfo.com.cn/finalpage/2026-06-30/1225397295.PDF
- TrendForce CoPoS/FOPLP/glass substrate: https://www.trendforce.com/presscenter/news/20260617-13107.html
- Corning GlassBridge product page: https://www.corning.com/oem-solutions/worldwide/en/home/products-solutions/optical-communication-components/next-generation-optics/glassbridge-connector.html
- Corning GlassBridge brochure: https://www.corning.com/catalog/coc/documents/brochures/OEM-152-AEN.pdf
- Corning OFC 2026 GlassBridge / CPO note: https://www.corning.com/optical-communications/worldwide/en/home/the-signal-network-blog/corning-at-ofc-2026.html
- 沃格光电 2025 年半年度报告: https://static.cninfo.com.cn/finalpage/2025-08-28/1224594914.PDF
- 沃格光电 2026-06-10 股票交易异常波动公告镜像: https://stockmc.xueqiu.com/202606/603773_20260610_F6AC.pdf
- 2026-06-28 全链周报：`artifacts/weekly_chain_tracking/ai_chain/2026-06-28.md`
- 2026-06-28 存储涨价时间线：`artifacts/weekly_chain_tracking/ai_chain/2026-06-28_storage_price_timeline.md`

## 2026-06-28 对话窗口摘要（历史）

### 当前核心卡点表

| 核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| HBM/DRAM/LPDRAM/NAND/eSSD + AI server parts | Qualified memory/storage/parts 供给、HBM stack/packaging/test、DRAM allocation、eSSD validation 与 ODM 采购同时约束 backlog 转收入。 | Micron FQ3 FY26 官方财报/prepared remarks、TrendForce eSSD、存储时间线。 | `2026H2-2027全年` 偏紧；2028 只写渐进改善观察；中高置信。 | 合约价回落、库存恢复、客户不再提前锁量、SCA/RPO/押金弱化、ODM 不再提 supply constraints。 |
| HBM test/probe/Cube Prober | HBM4E/HBM4 提高 KGD、stack/final test、探针卡和 Cube Prober 负荷；但内存厂尚未点名测试/探针为出货限制。 | Micron HBM4 ramp + The Elec/Techwing/MJC 线索；合同规模和交期仍缺。 | `2026H2-2027H2`；精确交期 `N/A`，缺内存厂 allocation 和供应商 backlog。 | 内存厂不点名测试限制，Techwing/MJC/ATE backlog 或交期回落，二供认证顺畅。 |
| InP/EML/CW-DFB/UHP/ELS | 合格 InP 衬底、外延、6 英寸良率、老化测试、客户认证和出口许可共同限制高端光源供给。 | 光模块专项 2026-06-28；DigiTimes 本周 InP/6 英寸供给墙线索。 | EML/InP `2026H2-2027H1`；CW/ELS/UHP 尾部 `2027H2-2028H1`；中高/中置信。 | 许可正常化、二供认证、光源价格/交期/allocation 回落、客户停止锁产能。 |
| 高端电子玻纤布 + M7-M10 CCL/prepreg + 树脂/HVLP | 高端布、超低损耗树脂、HVLP 铜箔、新线 qualified output 和客户 AVL 同时约束材料供给；普通布/锂电铜箔不可替代。 | AI PCB 专项 2026-06-28；沪电 IR；台玻/富乔/Reuters-CNA/DIGITIMES B 级线索。 | 玻纤布 `2026H2-2027年底`；CCL `2026H2-2027H1`；树脂/HVLP 精确持续 `N/A`。 | 报价回落、lead time 常态化、多供应商进入核心 AVL；树脂牌号和 HVLP4/5 多客户批量供货闭环。 |
| 数据中心并网/电力设备/液冷/800VDC | Firm power、interconnection、transformer/switchgear/UPS、rack power、CDU/冷板和现场集成约束可投产算力。 | FERC 大负载行动、Google Brazos、NVIDIA 800VDC。 | 并网区域性 `2026H2-2030`；设备/液冷 `6-24 个月`；800VDC `2027-2028 watch`。 | Tariff 改革、设备交期正常、真实项目延期减少、Brazos 难规模化或 800VDC 推迟。 |

### 未来潜在卡点表

| 潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| Enterprise SSD / LPDRAM/SOCAMM | AI agent、long-context inference 和 server memory hierarchy 拉动 eSSD 与低功耗高密度 DRAM；企业级 qualification 慢。 | Micron/TrendForce 已强化 eSSD；LPDRAM/SOCAMM 仍需和手机 LPDDR 拆口径。 | `2026H2-2027全年` | eSSD 合约价继续上行、CSP LTA、LP server DRAM/SOCAMM 被内存厂或客户点名 allocation。 | 库存恢复、合约价回落、SOCAMM 不再被点名紧张。 |
| 高端 MLCC/X6S 与 AI power passives | AI ASIC/accelerator 板卡功率上升，带动小尺寸高容高温 MLCC 用量和可靠性要求。 | TrendForce B 级线索强；缺供应商官方 allocation 和 A 股客户料号。 | `2026H2-2027` | 两家以上 MLCC 龙头披露涨价/lead time/AI server 客户订单；A 股披露料号、收入占比和毛利。 | 扩产兑现、价格不涨、lead time 正常、客户多源认证顺利。 |
| 1.6T/3.2T 光电芯片/FAU/主动对准/热管理 | 高速 analog、精密耦合、老化测试和散热良率随 1.6T/3.2T 升级而收窄。 | Marvell 需求强，光模块专项列 future watch；缺单品交期。 | `2026H2-2028` | 多供应商披露 driver/TIA/DSP/FAU/thermal lead time、allocation 或良率拖累。 | 二供认证快，1.6T/3.2T 放量顺畅，交期回落。 |
| M9/M10/Q cloth/NER/HVLP4/5 与成品板良率/测试 | Rubin、AI switch、224G+ 高速板推动材料、加工和测试窗口同步收窄。 | PCB 专项为 soft+/watch_to_soft；沪电 IR 支持材料偏紧但成品板 hard 证据不足。 | `2026H2-2028` | 官方 allocation、报价上涨、交期延长、客户提前锁料或成品板良率被点名。 | 多家供应商稳定量产，报价回落，板厂良率改善。 |
| CoPoS/FOPLP/玻璃基板/TGV | Package 面积和成本压力推动面板化与玻璃基板，但 TGV、对位、翘曲和良率难。 | TrendForce 指向验证/试产路径；当前不是量产瓶颈。 | `2027-2028+` | TSMC/OSAT/设备/基板厂披露试产通过、客户导入、设备订单或产能上修。 | CoWoS 扩产满足需求，玻璃基板继续延后。 |
| AI networking ASIC/NIC/DPU/retimer/substrate | 51.2T/102.4T switch、custom XPU、CPO/NPO 拉动先进制程、SerDes、package/substrate。 | Broadcom/Marvell A 级需求强；缺 silicon/substrate allocation。 | `2026H2-2027` | 官方披露交期、allocation、客户排产延期或 substrate/package 限制。 | 交付顺畅，客户不延期，封装/基板扩产跟上。 |
| 800VDC-SST-GaN-SiC 与存量风冷液冷改造 | 1MW rack、电源转换效率、铜用量和逐机架改造推动架构迁移。 | NVIDIA/Google 为 A 级方向证据；量产订单和 A 股收入证据缺。 | `2027-2028` | 800VDC design win 转量产；Brazos/OCP 出现多供应商量产和云厂商改造项目。 | 传统架构继续满足，存量改造难规模化，design win 不转收入。 |
