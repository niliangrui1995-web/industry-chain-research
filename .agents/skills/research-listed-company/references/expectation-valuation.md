# 盈利预期与估值门

上市公司深研、公司比较、估值或投资判断必须读取。财报事件本身是核心时，由 `earnings-call-investment-analyst` 执行同一合同。

## 事件前预期

1. 固定业绩、预告、快报或指引的期间、披露时间和 `expectation_as_of`。
2. 优先使用历史 point-in-time 数据；否则每家机构只保留事件前最后一份目标年度预测，披露样本数、均值、中位数、区间、预测发布日期和 `expectation_age_days`。
3. 不要求预测恰好在前一日更新。旧预测仅在口径不一致、明确失效或未吸收此前重大公开信息时排除并说明影响。
4. 当前滚动 F10、一致预期网页或搜索缓存只有在确认所有成分形成于事件前且无事后回填时，才能作较低置信度重建；否则只是线索。
5. 公司指引、市场共识和前期实际值是三个独立基准，不混写。样本少于 3 家标记小样本。

## A 股用户主口径

先取得最新单季度扣非归母净利润，再计算：

```text
annualized_quarterly_deducted = latest_single_quarter_deducted_attributable_net_profit * 4
annualized_core_gap =
    (annualized_quarterly_deducted - pre_event_fy_attributable_consensus)
    / abs(pre_event_fy_attributable_consensus)
```

记录 `comparison_basis=annualized_quarterly_deducted_vs_fy_attributable_consensus` 和 `annualized_core_gap_status=above|straddles|below|insufficient`。区间年化低值高于共识为 `above`，高值低于共识为 `below`，其余为 `straddles`；`formal_surprise_status=N/A`。

累计披露必须先反推最新单季：`Q2扣非=H1扣非-Q1扣非`、`Q3扣非=前三季度扣非-H1扣非`、`Q4扣非=全年扣非-前三季度扣非`。记录 `company_value_type=actual_quarter|preannouncement_quarter_range|derived_quarter`、原始累计值、`derivation_formula` 和舍入误差。正式报告发布后以正式值替换预告值。

这是用户指定的跨期间、跨指标 run-rate 检验，不是市场标准同期间 surprise。必须提示季节性、补贴、费用节奏和周期价格可能使单季年化失真。机构共识为负、零或接近零时以金额差为主，百分比为 `N/M`。

非 A 股优先使用事件前、同期间、同指标的正式共识比较；只有用户明确要求时才套用上述 A 股主口径。

## A 股用户 PE 口径

仅当 `market=A-share` 且任务或用户明确要求该 run-rate 口径时：

```text
PE_TTM_user = total_market_cap_as_of / (latest_single_quarter_deducted_attributable_net_profit * 4)
```

使用总市值，币种一致并记录 `market_cap_as_of` 和 `valuation_basis=latest_single_quarter_deducted_attributable_net_profit_x4`。区间利润输出反向 PE 区间；年化利润不为正时写 `N/A/不适用`。必须标为 `PE(TTM，用户口径)`，不得冒充标准最近四季度 PE。

非 A 股使用同一 GAAP/non-GAAP 口径的标准 TTM，或明确标注 denominator 与形成时点的 forward PE；无法取得可比 denominator 时写 `N/A`，不得套用 A 股“扣非归母×4”。

## 强制验算与最少输出

A 股用户口径按 `financial-evidence-audit` 构造 `expectation_gap` 和 `pe_user_defined`；非 A 股实际/指引相对事件前同口径共识使用 `expectation_surprise`，估值使用 generic valuation。至少输出事件/预期时点、预测新鲜度、样本数、原始值、比较口径、差额、状态、公式、估值时点、置信度和证据缺口。
