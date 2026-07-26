---
name: income-investment
description: Analyze whether a listed security can provide durable or opportunistic distributable income through distribution history, cash available for distribution, sector-specific coverage, balance-sheet and refinancing risk, dividend-cut scenarios, valuation, tax, currency, and portfolio fit. Use for 股息、红利、高股息、分红可持续性、派息覆盖、股息陷阱、REIT 配息、银行或保险分红、BDC、资源股周期分红、公用事业或电信收入型投资. Do not use for quote-only dividend-yield requests or portfolio sizing without sufficient inputs.
---

# Income Investment

回答“这项证券能否产生足够耐久且有吸引力的可分配收入”，不把屏幕上的高股息率当作机会证据。本技能独立拥有收益质量结论，不要求同时加载通用公司研究 Skill。

## 强制起点

1. 确认主体、ticker、证券/基金类型、上市币种、分配币种、研究截止时间和普通/特别/浮动分配性质。
2. 缺少税收居民地、账户类型、注册地、条约和代扣处理时，只计算税前收入，税后值写 `N/A`。
3. 区分公司/资产质量和当前组合适配；没有持仓、集中度、期限和风险承受信息时 `portfolio_action=N/A`。
4. 当前价格、分配、财务、债务、监管资本和税务规则必须实时核验并标时点。

## 研究流程

1. **分配历史**：至少覆盖五年（不足则全覆盖），分开普通、特别和浮动分配，记录增加、维持、削减和暂停。
2. **追踪可分配现金**：检查利润、经营现金流、必要资本开支、营运资本、利息、债务到期、再融资、表外承诺、回购和稀释。
3. **使用行业口径**：不得对所有行业机械使用 EPS payout；按 [references/sector-distribution-metrics.md](references/sector-distribution-metrics.md) 选择法定或行业专用指标。
4. **检查耐久性**：最低限度评估生意模式、定价权、周期、管理层、资本配置、治理和分配政策。
5. **评估价格**：分开 trailing/forward yield、历史收益率区间、行业估值、现金流收益率和当前价格隐含假设；yield on cost 只作历史信息。
6. **三情景压力测试**：`base / adverse / severe` 均写经营、可分配现金、债务/再融资、分配结果和估值影响；adverse 与 severe 必须显式测试削减或暂停。
7. **按需检查税币种与组合**：见 [references/tax-currency-portfolio-boundaries.md](references/tax-currency-portfolio-boundaries.md)。

情景和计算口径见 [references/income-calculations-scenarios.md](references/income-calculations-scenarios.md)。所有关键计算必须通过 `financial-evidence-audit`。

## 阻断门

以下任一成立时，不得用其他维度高分抵消：

- 经常性分配没有可重复现金覆盖；
- 重大流动性、债务到期或再融资风险；
- 结构性业务恶化或周期顶部现金流被外推；
- 监管资本、法定可分配利润或契约限制；
- 有强证据支持的治理或诚信问题；
- 决策关键基本面资料不足。

## 输出

先给：

```text
income_quality = durable_income_candidate |
                 opportunistic_income_candidate |
                 watchlist | yield_trap |
                 unsuitable | insufficient_data
portfolio_action = candidate | hold_no_add | reduce | N/A
```

再说明分配现金来源、覆盖、行业专用指标、债务、减配情景、估值、税币种、最大风险和跟踪指标。没有组合输入时不得给仓位范围或个性化买卖动作。

本技能以 `xbtlin/ai-berkshire` commit `09ebc400a8815636e02f5b7d1d811a53164a0b92` 的 `income-investment` 为方法基座，按其 MIT License 保留归属；已替换其计算、审计和来源合同。
