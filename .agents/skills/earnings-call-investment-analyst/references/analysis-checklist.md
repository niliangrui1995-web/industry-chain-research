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

| Metric | Company Metric | Actual | Prior Guidance | Consensus Metric | Consensus | Comparison Basis | Prior Quarter | QoQ | YoY | Gap/Surprise Status | Source |
|---|---|---:|---:|---|---:|---|---:|---:|---:|---|---|

- 收入、分部收入、订单、库存、capex、现金流等水平值用 `(current-prior)/abs(prior)` 计算 QoQ；
- 毛利率等比率用基点变化；
- EPS/净利润为负、接近零或受一次性项目干扰时，用金额变化并说明百分比失真；
- 前季值无法核实时写 `prior-quarter source gap`，不从记忆估算；
- GAAP 与 non-GAAP 必须分开。
- Consensus 必须是事件前市场最后可得的 point-in-time 数据；不要求机构预测在前一日更新，同时记录 `expectation_as_of`、预测发布日期和 `expectation_age_days`。
- 无历史快照时，为每家机构只保留事件前最后一份目标年度归母净利润预测进行公开重建，并披露机构数、均值、中位数、区间和最新日期；少于 3 家标记小样本。
- 旧预测不因发布时间较早自动剔除；检查它是否仍是事件前最后可得值、是否已吸收此前重大公开信息，并把失效或明显滞后的样本单列说明。
- 当前滚动 F10、搜索缓存和事后页面须核对底层预测日期；只有能确认成分均形成于事件前且没有事后回填时，才可作为较低置信度的公开重建。
- F10 或研报只写“净利润”时先核对表头、脚注和定义；无法确认是否归母时记录 `consensus_metric=unresolved`，比较结果为 `N/A`。
- 非 A 股 reported actual 与公司 forward guidance 分别使用 `financial-evidence-audit` 的 `expectation_surprise`，设置 `subject_kind=reported_actual|company_guidance`；只比较事件前同目标期、同指标、同单位/币种和同 GAAP/non-GAAP 口径共识，明确 meet band。公司指引不能冒充 reported actual。
- A 股统一使用 `最新单季度扣非归母×4` 对比事件前机构目标年度归母共识；审计输入记录 `company_metric=deducted_attributable_net_profit`，派生输出记录 `derived_metric=annualized_single_quarter_deducted_attributable_net_profit`，并记录 `consensus_metric=fy_attributable_net_profit` 和 `comparison_basis=annualized_quarterly_deducted_vs_fy_attributable_consensus`。
- 使用 `(单季度扣非年化值-机构全年归母共识)/abs(机构全年归母共识)`；年化低值高于共识记 `above`，年化高值低于共识记 `below`，否则记 `straddles`，证据不足记 `insufficient`，字段为 `annualized_core_gap_status`。主结论写“按单季扣非年化口径超预期/区间跨越/低于预期/证据不足”，不得事后自设容忍带；该跨期间、跨指标判断的 `formal_surprise_status=N/A`。
- 正式定期报告、业绩预告和业绩快报使用同一计算逻辑；正式报告发布后以正式值替换预告值。凡累计值都必须先反推最新单季：`Q2扣非=H1扣非-Q1扣非`、`Q3扣非=前三季度扣非-H1扣非`、`Q4扣非=全年扣非-前三季度扣非`，再乘 4。记录 `company_value_type=actual_quarter|preannouncement_quarter_range|derived_quarter`、`derivation_formula`、`annualization_factor=4`、来源和舍入误差；无法取得或可靠反推单季度扣非时为 `N/A`。
- 同时列示公司归母、扣非与非经常性损益影响，解释单季年化 beat/miss 的质量；机构另有扣非预测时只作辅助同口径参照，不替代用户指定主口径。
- 公司归母与扣非均为区间且公告未说明端点对应同一情景时，不得机械用低值减低值；非经常性损益影响范围使用 `[归母低值-扣非高值, 归母高值-扣非低值]`。
- 机构全年归母共识为负、零或接近零时以金额差为主并把百分比标为 `N/M`。必须提示季节性、周期价格、补贴、费用或确认节奏可能使单季乘 4 失真。
- 仅当 `market=A-share` 且任务或用户明确要求用户 run-rate 时，才使用 `当前总市值/(最新单季度扣非归母×4)`，记录市值时点和 `valuation_basis=latest_single_quarter_deducted_attributable_net_profit_x4`；区间利润输出反向 PE 区间，年化利润不为正时写 `N/A/不适用`。输出标为“PE(TTM，用户口径)”，不得与市场标准 PE(TTM) 混写。非 A 股使用同一 GAAP/non-GAAP 口径的标准 TTM 或明确标注的 forward denominator，并通过 generic valuation 审计；缺少可比 denominator 时写 `N/A`。
- QoQ、YoY、预期差、单季度反推、单季年化、市值、PE、SBC 稀释和其他会改变投资结论的计算，必须使用 `financial-evidence-audit` 的确定性脚本和准出合同；记录输入期间、币种、单位、指标定义、来源和审计结果，不用 LLM 心算。
- 官方值、共识或行情来源存在未解决冲突时，相关数字和由其推导的 beat/miss、估值及业绩质量结论一律阻断。不得取平均掩盖口径差异，也不得用 `provisional` 绕过 `FAIL / blocked`。

解释 beat/miss 来自需求、价格、结构、拉货、成本、税率、股本、一次性项目还是会计因素。可用 `clean_beat`、`low_quality_beat`、`mixed`、`beat_and_raise`、`thesis_break` 或 `evidence_insufficient`，但不必为简单任务贴标签。

## 财务质量、附注与异常关系

完整深挖必须检查下列项目；未披露或不可比时明确写 `not_disclosed`、`not_comparable` 或 `evidence_absent`，不要把没有发现等同于不存在：

| 检查项 | 最低核对内容 | 可能影响 | 处理边界 |
|---|---|---|---|
| 关联交易 | 关联方、交易性质、金额、定价和余额变化 | 收入/利润真实性、利益输送、现金占用 | 以附注和监管披露为准；媒体线索不能单独定性 |
| SBC 与稀释 | 当期 SBC、占收入/经营费用/现金流的口径、基本与稀释股数变化、潜在期权/RSU | non-GAAP 质量、每股价值、回购是否仅抵消稀释 | 分开费用剔除与真实股本稀释；相关计算走审计 |
| 或有负债与承诺 | 诉讼、担保、采购/租赁/资本承诺、表外安排及可能时间窗 | 未来现金流、偿债和估值风险 | 无法可靠估计金额时写区间缺失，不补造概率 |
| 会计政策变化 | 收入确认、资本化、折旧摊销、存货计价、合并范围和关键估计变化 | 跨期可比性和利润质量 | 先重述可比口径；无法重述时阻断机械同比/QoQ |
| 分部重分类 | 分部定义、内部抵销、历史重述、未分配费用变化 | 增长来源、利润率和业务质量 | 旧分部与新分部不可直接拼接 |

异常关系至少做同期间、同币种、同合并范围比较：

| 关系 | 需要计算或核对 | 结论纪律 |
|---|---|---|
| 应收 vs 收入 | 应收及合同资产增速、DSO（可得时）与收入增速 | 应收更快只是回款/确认风险 lead；结合账期、客户结构、坏账和季节性核实 |
| 库存 vs 收入/成本 | 库存增速、结构、周转及减值与收入/成本增速 | 库存更快只是积压或备货 lead；结合原料、在制品、成品和供给保障解释 |
| 经营现金流 vs 净利润 | 现金转换、营运资金桥接、一次性收付款 | 单季背离不自动定性；检查连续期间及应收、库存、应付共同变化 |
| capex/资本化 vs 收入和折旧 | capex 强度、资本化开发支出、折旧摊销和在建工程变化 | 突增可能是扩产也可能推迟费用确认；结合项目、产能、投产与减值核实 |

所有比率、增速和桥接计算记录 `calculation_audit_status`。异常关系只能形成 `lead`、`explained`、`warning`、`material_risk`、`not_comparable` 或 `evidence_absent`，不能单凭一个比例判定造假或业绩质量恶化。

## 指引

核对收入/利润/EPS 区间与中点、利润率假设、分部驱动、产能、客户、订单、监管、出口许可和资格认证。区分已被 backlog/合同/已认证需求覆盖的收入，与仍依赖未来订单、许可、认证或爬坡的收入。

## 电话会与前季比较

只提取决策有用的信息：需求、订单/backlog、取消、客户、价格/结构、产能/良率、库存/渠道、供应链、监管、融资、管理层语气和 Q&A 回避点。

前季内容可得时，比较：

| Topic | Prior Quarter | Current Quarter | Change | Evidence Type | Meaning | Follow-Up |
|---|---|---|---|---|---|---|

变化可标 `improved`、`deteriorated`、`unchanged`、`new_disclosure`、`walked_back` 或 `prior-quarter source gap`。两期来源质量不同必须说明，不能把转录差异当作语气变化。

### 上期承诺与本期兑现

只追踪可衡量或可验证的承诺，不把“保持信心”“长期看好”等愿景句纳入兑现率：

| Commitment | Stated At | Due Period | Metric / Target | Current Evidence | Status | Explanation | Source |
|---|---|---|---|---|---|---|---|

`Status` 使用 `fulfilled`、`partially_fulfilled`、`missed`、`walked_back`、`not_yet_due` 或 `unverifiable`。只有已到期且原承诺、目标口径与本期结果均有来源时才能判定兑现；目标或口径变化必须保留原文语义并解释，不计算没有可比样本的“承诺兑现率”。

### 尖锐 Q&A 与回答质量

优先记录涉及指引缺口、利润率、现金流、客户流失、库存、监管、融资、会计口径或既有承诺的尖锐问题：

| Question | Why It Matters | Management Answer | Directness | Numeric/Timeline Support | Follow-Up Needed | Source |
|---|---|---|---|---|---|---|

`Directness` 使用 `direct`、`partial`、`evasive`、`not_answered` 或 `source_incomplete`。判断是否正面回答时看是否回应核心问题、给出可核验数字/时间表及承认限制；不要仅因回答短、语气谨慎或 transcript 标点差异判定回避。

语气、停顿、措辞或情绪变化一律标为 `tone_lead_only`。它们可以触发进一步检索或下季复查，但不能单独证明诚信、需求、订单或业绩发生变化；两期材料类型或完整性不同则不做语气比较。

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
- 财务质量/附注异常、上期可衡量承诺兑现和尖锐 Q&A 回答质量；
- 基本面、业绩弹性、交易弹性的变化；
- 3-7 个具体跟踪指标；
- `company_original_status`、`call_content_status`、`final_source_type`、`missing_materials`、`provisional`、`confidence`、`calculation_audit_status`、`audit_release_status`、`audit_artifact`、`audit_blockers`、`unresolved_numeric_conflicts`。

电话会官方 transcript/replay/audio/captions 缺失时，按 source workflow 获取可靠完整 fallback，列出检索路径与材料缺口，并将电话会相关判断标为 `provisional`。完整 fallback 可以支持 provisional 文字判断，但不能替代官方报告数字；任何未解决数值冲突、口径冲突或 `financial-evidence-audit` 的 `FAIL / blocked` 都必须继续阻断相关结论。
