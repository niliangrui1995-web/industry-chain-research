---
name: industry-research-router
description: Route industry-chain, company research, competitive landscape, fundamental stock research, valuation, trading elasticity, domestic substitution, technology moat, oligopoly, leader-vs-concept, and sector ranking questions to the right skill mix. Use when the user asks in Chinese or English about 产业链研究、公司研究、行业本质、技术壁垒、国产替代、全球龙头、寡头、谁最有弹性、股票弹性、交易弹性、估值、PE、业绩弹性、公司排序、赛道拆解、谁是真龙头、谁是蹭概念.
---

# Industry Research Router

## Purpose

Use this as the first-stop router for investment-oriented industry and company research. It does not replace specialist skills; it selects the right combination and enforces a consistent research output.

## Skill Selection

Choose the smallest useful combination:

- Industry essence and technology moat: `20-andruia-niche-intelligence`, plus `deep-research` for long-form source gathering.
- Competitive landscape and true leaders: `competitive-landscape`, `competitive-intel`.
- Company fundamentals and stock evaluation: `stock-evaluator-v3`, plus `yfinance`, `stocks`, `allstock-data`, or `alpha-vantage` depending on market.
- A-share/HK/US live data and K-line checks: `allstock-data`, `stock-copilot-pro`, `financial-intel`.
- Overseas oligarch data: `yfinance`, `stocks`, `alpha-vantage`.
- Structured comparison, scoring, or watchlist tables: `Spreadsheet`, `xlsx-official`, `advanced-evaluation`.
- Web/news/filings collection: `web-scraper`, `firecrawl-scraper`, `tavily`, `finance-news`.
- AI supply-chain latest-news and rumor verification: `ai-chain-research-orchestrator`, plus `finance-news`, `web-scraper`, `allstock-data`, and `advanced-evaluation` as needed.
- AI/software/chip technical moat: `ai-engineer`, `ai-ml`, `tech-stack-evaluator`, `cto-advisor`, `senior-architect`.

If a named companion skill is unavailable in the current session, continue with the same analytical framework and say briefly which companion skill was unavailable only if it materially affects the answer.

## Workflow

1. Classify the task before answering:
   - Industry-chain map
   - Company comparison
   - Technology moat
   - Domestic substitution
   - Fundamental investment ranking
   - Trading elasticity ranking
   - Data table or watchlist construction

2. Use current data when facts may have changed:
   - Prices, PE/PB, market cap, turnover, volume, 5/20/60-day performance, earnings reports, guidance, order news, and regulations must be verified with tools or web sources.
   - Prefer official filings, exchange disclosures, company reports, and reputable financial data sources for hard claims.

3. Separate three rankings:
   - Fundamental quality ranking: business quality, moat, customer quality, margin structure, long-term competitiveness.
   - Earnings elasticity ranking: revenue growth, gross margin leverage, capacity utilization, operating leverage, order conversion.
   - Trading elasticity ranking: market cap, float market cap, turnover, volatility, technical position, catalyst density, expectation gap, crowding risk.

4. Avoid common errors:
   - Do not equate “good company” with “highest stock elasticity.”
   - Do not equate “hot theme” with “real beneficiary.”
   - Do not rank only by PE; include market cap, float, growth, volatility, and expectation gap.
   - Do not treat one-time low-base growth as durable growth without checking order quality and customer verification.
   - Do not mix mainland China, Taiwan, Hong Kong, US, Japan, and Korea listings without normalizing ticker suffixes and market rules.

## Output Pattern

Start with the answer, then explain:

```text
结论先行：
最大交易弹性：X
最大业绩弹性：Y
最稳趋势中军：Z
最大风险：W

排序：
1. 公司A：核心理由
2. 公司B：核心理由
3. 公司C：核心理由

关键观察指标：
- 公司A：订单/客户认证/毛利率/换手率/20日涨幅
- 公司B：价格/产能/库存/估值/催化剂
```

For industry-chain education, use:

```text
产业链拆解：
1. 上游材料/设备/耗材
2. 中游制造/封装/检测
3. 下游应用/客户

真正壁垒：
- 良率
- 客户验证
- 工艺参数
- 规模制造
- 供应链认证
```

## Reference

For the maintained list of recommended companion skills and use cases, read `references/skill-map.md` when the user asks which skills should be used or when the routing choice is ambiguous.
