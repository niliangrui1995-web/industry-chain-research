# 财报与电话会深挖检查表

完整 post-earnings 分析、自动化单公司子任务或用户明确要求深挖时读取。普通数字核对或简短问答按需裁剪。

## 公司基线

先写一段话：公司卖什么、谁购买、客户为何需要、收入由销量/ASP/结构/利用率/良率/服务附加或一次性项目中的什么驱动。

只保留对本季度重要的业务线：

| Business / Product Line | Role | Customers / End Market | Competitive Position | AI Exposure Path | Quarter-Sensitive KPIs |
|---|---|---|---|---|---|

解释哪些业务应驱动本季度收入、毛利率、现金流和指引，哪些只是周期噪声或非核心拖累。

## 当前与前一季度

在检索前明确当前财季和前一财季：

- 月份财季按季度回退三个月，例如 `Mar/2026 -> Dec/2025`；
- 财年 Q1 的前季是上一财年 Q4；
- 只有 `FY2026 Q3` 等标签时，用官方财历确认；
- `N/A` 时从官方财报、监管文件或 IR 标题确定；
- 无法确定时写 `prior-quarter period unresolved` 并降低比较置信度。

记录当前期证据、解析后的当前期、前一季度、来源和置信度。分别获取当前与前季官方财报材料，并尽量获取两期电话会/业绩会内容。

## 数字与 surprise

推荐表：

| Metric | Actual | Prior Guidance | Consensus | Prior Quarter | QoQ | YoY | Beat/Miss | Source |
|---|---:|---:|---:|---:|---:|---:|---|---|

- 收入、分部收入、订单、库存、capex、现金流等水平值用 `(current-prior)/abs(prior)` 计算 QoQ；
- 毛利率等比率用基点变化；
- EPS/净利润为负、接近零或受一次性项目干扰时，用金额变化并说明百分比失真；
- 前季值无法核实时写 `prior-quarter source gap`，不从记忆估算；
- GAAP 与 non-GAAP 必须分开。

解释 beat/miss 来自需求、价格、结构、拉货、成本、税率、股本、一次性项目还是会计因素。可用 `clean_beat`、`low_quality_beat`、`mixed`、`beat_and_raise`、`thesis_break` 或 `evidence_insufficient`，但不必为简单任务贴标签。

## 指引

核对收入/利润/EPS 区间与中点、利润率假设、分部驱动、产能、客户、订单、监管、出口许可和资格认证。区分已被 backlog/合同/已认证需求覆盖的收入，与仍依赖未来订单、许可、认证或爬坡的收入。

## 电话会与前季比较

只提取决策有用的信息：需求、订单/backlog、取消、客户、价格/结构、产能/良率、库存/渠道、供应链、监管、融资、管理层语气和 Q&A 回避点。

前季内容可得时，比较：

| Topic | Prior Quarter | Current Quarter | Change | Evidence Type | Meaning | Follow-Up |
|---|---|---|---|---|---|---|

变化可标 `improved`、`deteriorated`、`unchanged`、`new_disclosure`、`walked_back` 或 `prior-quarter source gap`。两期来源质量不同必须说明，不能把转录差异当作语气变化。

## 下游需求

主动查找终端需求、客户下单、backlog 转换、取消、长期协议、设计赢单、认证、拉货/推迟、渠道库存和指引覆盖。区分 durable ramp、pull-forward、inventory rebuild、price/mix、one-time shipment、cyclical recovery 和 weak/uncertain demand。

允许的 `Mention Status`：

`demand_accelerating`、`demand_stable`、`demand_decelerating`、`demand_uncertain`、`customer_pull_forward`、`inventory_digesting`、`not_mentioned`、`third_party_only`。

没有提及就写 `not_mentioned` 或 `evidence_absent`。中文报告中的标题、表头、项目名、证据、时间、需求质量和投资含义使用中文，仅保留枚举值英文。

## 上游瓶颈

按公司实际产品搜索 supplier、substrate、wafer、fab、material、component、equipment、lead time、yield、allocation、qualification、LTA、prepayment、shortage 和具体材料/组件名。

允许的 `Mention Status`：

`mentioned_current_bottleneck`、`mentioned_future_risk`、`mentioned_mitigated`、`mentioned_not_bottleneck`、`not_mentioned`、`third_party_only`。

分开当前约束、未来风险、已覆盖/缓解、未提及和第三方推断。行业热度或供应商评论不能改写成公司管理层表述。中文报告中的完整瓶颈章节使用中文，仅保留枚举值英文。

## 事实层级与输出

分开 hard fact、management claim、external analyst inference 和 own inference。完整深挖结尾至少包含：

- 结果分类、最大超预期与失望、指引质量；
- 当前/前季来源状态与关键变化；
- 下游需求和上游瓶颈是否被提及；
- 基本面、业绩弹性、交易弹性的变化；
- 3-7 个具体跟踪指标；
- `company_original_status`、`call_content_status`、`final_source_type`、`missing_materials`、`provisional`、`confidence`。
