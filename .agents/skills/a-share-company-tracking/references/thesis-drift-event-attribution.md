# Thesis 漂移与事件归因

本参考文件用于建立公司基线、处理日更事件和判断 thesis 是否真正发生漂移。核心原则是：新表述、新预测或新价格不等于新基本面事实。

## 目录

- 基线合同：可证伪假设、管理层承诺和资本配置账本
- 日更变化分类
- 基本面 Thesis 更新硬门
- 五维事件归因
- 事件和状态字段

## 基线合同

### 可证伪核心假设

在 `baseline.md` 中为每条核心假设记录：

- `assumption_id`、假设和它对投资论文的必要性；
- 从终端需求、公司产品到收入、利润或现金流的因果链；
- 当前硬证据、反证和尚未解决的证据缺口；
- 可观测的支持信号和反转信号；
- 明确失效条件，以及最早可验证的日期、报告期或事件；
- `status=active|partially_supported|falsified|unresolved` 和 `as_of`。

假设必须能被未来证据推翻。“赛道好”、“管理层优秀”或“将持续增长”不是合格假设，除非已定义传导机制和可观测失效条件。

### 商业化阶段账本

对每个重要产品、客户导入或受益逻辑记录：

- `commercialization_stage=rd_plan|sampling|validation|design_win|qualification|mass_production|shipment|revenue|profit_cashflow`；
- `stage_evidence`、`stage_evidence_date`、`stage_source`；
- `revenue_materiality`，未披露时写 `evidence_absent`；
- 进入当前阶段仍缺少什么，以及验证下一阶段的最早证据。

阶段是“当前直接证据支持的最高状态”，不是自动流水线。送样、验证、design win、认证、量产、出货、收入和利润/现金流严格分开；不得从任一阶段推断下一阶段。

### 管理层承诺账本

只收录具体、可衡量且有期限的承诺，记录：

- `promise_id`、日期、原始来源和原话摘要；
- 指标、基准、目标值/区间和截止时间；
- 最新官方结果和 `status=pending|met|partly_met|missed|withdrawn|not_assessable`；
- 变更后的指引必须保留原承诺，不得用新口径覆盖旧口径。

愿景、定性展望和营销措辞可放入主张记录，但不进入承诺兑现分母，也不计算固定兑现率评分。

### 资本配置账本

对并购、回购、分红、融资、大额资本开支和新业务投入记录：

- 决策日期、金额、资金来源、稀释/负债代价和管理层声称的逻辑；
- 事前可验证目标、预计兑现窗口和反转条件；
- 事后官方结果，包括现金回报、盈利、减值、整合、稀释和资产负债表影响；
- `status=pending|value_creating|mixed|value_destroying|not_assessable` 和下一验证点。

不使用通用权重或单一评分把不可比的资本配置决策合成一个数字。

## 日更变化分类

每条事件选择一个主 `change_type`；若一份材料同时包含多类变化，拆成多条事件：

| `change_type` | 判定标准 | 不能单独导出 |
|---|---|---|
| `fact_change` | 新官方数据、已生效的监管/合同事项或等价可核验硬证据 | 若与核心因果链无关，仍不得改变 thesis |
| `management_claim_change` | 新指引、预期、解释或定性表述，尚未被结果验证 | 已兑现的业绩或硬事实 |
| `estimate_change` | 分析师、数据商或模型对未来的预测改变 | 公司真实经营已改变 |
| `valuation_price_change` | 股价、市值、估值倍数、成交或拥挤度改变 | 基本面 thesis 改变 |
| `wording_only` | 重述、措辞强弱或无新可验证内容的摘要 | 任何方向的 thesis 漂移 |
| `evidence_gap` | 应有材料缺失、来源冲突、口径不明或无法核验 | 基本面好转或恶化；只改变研究置信度 |

## 基本面 Thesis 更新硬门

`thesis_effect=strengthened|weakened` 必须同时满足：

1. 存在新的官方或等价可核验硬证据；
2. 证据改变了某条已登记核心假设、因果链、失效条件或其实现概率；
3. 已记录直接反证、口径变化和替代解释；
4. 结论能指向具体 `assumption_id`。

仅有管理层表述、外部预期、价格反应、行情原因、概念标签、新闻重复或证据缺口时，必须写 `thesis_effect=unchanged|not_assessable`。可以调整研究置信度、估值状态或监测优先级，但不得偷换成基本面强化/弱化。

## 五维事件归因

对每条实质事件检查五个维度：

| 维度 | 典型证据 |
|---|---|
| `company` | 公司官方业绩、订单、产能、治理、融资或公告事件 |
| `regulatory` | 已发布或已生效的法规、政策、处罚、审批、准入或限制 |
| `peer` | 可比同行的业绩、价格、产能、指引或交易反应 |
| `industry` | 产业供需、库存、价格、认证、技术路线或终端需求 |
| `market` | 宽基指数、风格、利率、流动性、风险偏好和市场整体定价 |

每个维度都记录：

- `evidence`：支持该归因的定时、可追溯证据；
- `counterevidence`：与归因不一致的价格、同行、时间或业务证据；
- `confidence=high|medium|low|none`；
- `persistence_window`：预计开始/结束、报告期或下一复核日；无法支撑时写 `unknown`；
- `next_validation`：能最早区分该归因与替代解释的新证据。

时间同步、事件后股价反应或多个模型给出相同原因，都不是因果证明。若多个维度都有支持，保留多因素归因；无法区分时写 `primary_attribution=unknown`。

## 事件和状态字段

`events.jsonl` 的实质事件至少包含：

```text
date, ticker, name, source_type, source_name, title, url, summary,
verification_status, change_type, hard_evidence_new, assumption_ids,
thesis_effect, previous_commercialization_stage, new_commercialization_stage,
stage_evidence, stage_evidence_date, stage_source, revenue_materiality,
attribution_dimensions, evidence, counterevidence,
confidence, persistence_window, next_validation
```

`state.md` 要分开维护：

- 基本面 thesis 和相关 `assumption_id`；
- 新硬事实；
- 管理层主张及承诺兑现；
- 各重要产品的商业化阶段、阶段证据/日期/来源和收入重要性；
- 外部预期；
- 估值与价格状态；
- 证据缺口和研究置信度；
- 下一验证点和时间窗口。

跟踪输出只用于更新事实、论文、风险和监测问题，不从 `thesis_effect`、置信度或事件归因自动生成买卖、加减仓、止损或目标价。
