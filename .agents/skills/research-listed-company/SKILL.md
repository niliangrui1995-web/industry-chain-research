---
name: research-listed-company
description: Evidence-first listed-company fundamental and investment research covering business economics, demand transmission, true exposure, moat falsification, management and capital allocation, financial quality, point-in-time expectations, valuation, strongest bear case, scenarios, and thesis invalidation. Use for 上市公司深研、个股研究、公司比较、护城河、管理层、资本配置、盈利预期、估值、安全边际、基本面质量、业绩弹性、真假受益或是否值得投资. Do not use for pure industry-chain discovery, isolated earnings-call review, dividend-income safety, daily tracking, quote-only requests, or market-cycle discipline.
---

# Research Listed Company

回答“这家上市公司是什么生意、凭什么持续赚钱、市场已计价什么、什么证据会推翻投资逻辑”。按问题裁剪深度，但不得跳过会改变结论的证据门。

## 强制起点

1. 确认上市主体、交易所、ticker、证券类型、报告币种和研究截止时间；无法唯一确认时停止公司结论。
2. 分开标注 `official_fact`、`management_claim`、`credible_secondary`、`inference` 和 `evidence_absent`。
3. 概念标签、供应链传闻、股价强度或上游线索不能证明客户、订单、量产、收入和真实受益。
4. 严格分开研发计划、送样、客户导入、design win、认证、量产、出货、收入和利润贡献。
5. 当前价格、市值、财报、共识、公告、管理层和监管状态必须实时核验并标时点。

## 自适应研究流程

1. **定义决策问题**：说明研究目的是公司质量、估值、比较、催化还是现有 thesis 复核。
2. **评估信息质量**：资料丰富度只影响研究置信度，不自动提高投资确定性；资料不足时缩小结论，不填补空白。
3. **解释生意本质**：一句话说明客户、付费原因、替代方案、复购/锁定来源和核心利润变量。
4. **建立财务传导**：验证 `终端需求 -> 产品/服务 -> 量/价/份额/利用率 -> 毛利/费用 -> 现金流`，排除产品结构、并表和一次性项目造成的假改善。
5. **验证真实暴露**：确认产品、客户/应用、商业化阶段、收入重要性、产能/良率/交付和财务确认。
6. **证伪护城河**：逐项检查定价权、转换成本、网络效应、规模、渠道/资源和技术壁垒；给出变宽/变窄证据与摧毁条件。
7. **评估管理层**：看承诺兑现、困难时期行为、资本配置、治理、关联交易、稀释和接班，不做人格模拟或万能评分。
8. **检查财务质量**：利润与现金转换、营运资本、资本化、债务、或有负债、SBC、并购和会计口径是否支持经营叙事。
9. **检查预期与估值**：完整研究必须检查最近业绩相对事件前 point-in-time 预期；再分析当前价格隐含的增长、利润率和资本回报假设。
10. **建立反方**：写最强空头论点、失败路径、最可能的分析错误、论文失效条件和 3-5 个领先跟踪指标。

公司方法细节见 [references/company-research-method.md](references/company-research-method.md)。管理层与资本配置见 [references/management-capital-allocation.md](references/management-capital-allocation.md)。涉及预期差或估值必须读 [references/expectation-valuation.md](references/expectation-valuation.md)。

## 强制验证

市值、估值、预期差、财务比率和情景数字必须使用 `financial-evidence-audit`。未解决数值/口径冲突或 `FAIL / blocked` 时不得输出相关确定性结论；只有不存在数值冲突而关键官方材料暂缺、且已列 fallback 与复查时间时，才可输出 `provisional`。

财报、指引或电话会本身是核心问题时，改用 `earnings-call-investment-analyst`；产业节点和真实瓶颈是核心时，改用 `research-industry-chain`；分红安全性是核心时，改用 `income-investment`。

## 投资结论

分开输出：

- `business_quality`：生意、护城河、管理层和财务质量；
- `earnings_elasticity`：需求变化转化为收入、利润和现金流的能力；
- `valuation_expectation`：当前价格隐含假设和安全边际；
- `trading_elasticity`：仅在用户要求排序或交易判断时加入；
- `thesis_status`：`supported | mixed | weakened | insufficient`；
- 最大风险、失效条件和下一验证点。

可以判断研究资格和条件性投资吸引力；缺少组合、期限和风险承受能力时，不编造仓位、个性化买卖动作或精确目标价。
