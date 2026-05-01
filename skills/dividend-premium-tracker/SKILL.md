---
name: dividend-premium-tracker
description: Track and interpret the CSI Dividend Low Volatility Index dividend premium, defined as dividend yield minus China 10-year government bond yield. Use for China dividend, low-volatility, defensive equity, bond-yield comparison, high-dividend style timing, and dividend-stock valuation context. In this project it is an optional style and macro backdrop tool, not a default stock selector or automation workflow.
---

# Dividend Premium Tracker

Use this skill when a research task needs the macro valuation backdrop for China high-dividend or low-volatility equity assets.

## Scope

- Track the dividend premium: CSI Dividend Low Volatility Index dividend yield minus China 10-year government bond yield.
- Use the result as style context for high-dividend, utilities, coal, banks, telecom, infrastructure, and other defensive dividend assets.
- Treat it as a market-style signal. It does not prove that an individual stock has durable fundamentals or trading elasticity.

## Project Rules

- Do not create cron jobs, alerts, Telegram messages, email reports, or heartbeat monitors unless the user explicitly asks for monitoring automation.
- Do not copy the global skill's old automation scripts into the project route by default; those scripts were not clean enough for this Windows project.
- Verify current index yield, bond yield, and dates from official or reliable market-data sources before making a current conclusion.
- When data is missing, report `N/A` and explain the missing source instead of inventing the spread.

## Workflow

1. Confirm whether the user is asking about dividend style allocation, a dividend-stock candidate, or a broad defensive-equity comparison.
2. Gather current or historical dividend yield and China 10-year government bond yield.
3. Calculate:

```text
dividend_premium = dividend_yield - china_10y_government_bond_yield
```

4. Interpret in layers:
   - Absolute premium: whether dividend assets still compensate for bond-yield competition.
   - Direction: whether the premium is widening or narrowing.
   - Stock mapping: whether the target stock has real dividend capacity, payout stability, cash-flow quality, and valuation support.
   - Trading layer: whether dividend style is crowded, under-owned, or catalyst-driven.

## Output

For dividend-style questions, answer with:

```text
结论：红利风格当前吸引力为 强 / 中 / 弱
核心依据：股息率、10年国债收益率、股息率溢价、趋势变化
适用股票类型：高分红稳定现金流 / 周期高股息 / 类债资产 / 需剔除
最大风险：利率上行、盈利下行、分红不可持续、拥挤交易
需要跟踪：股息率、国债收益率、分红预案、自由现金流、估值分位
```

Use `industry-research-router` plus `stock-evaluator` and market-data skills for the final individual-stock judgment.
