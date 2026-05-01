---
name: industry-research-router
description: Route industry-chain, company research, competitive landscape, fundamental stock research, valuation, trading elasticity, domestic substitution, technology moat, oligopoly, leader-vs-concept, and sector ranking questions to the right project skill mix. Use for 产业链研究、公司研究、行业本质、技术壁垒、国产替代、全球龙头、寡头、谁最有弹性、股票弹性、交易弹性、估值、PE、业绩弹性、公司排序、赛道拆解、谁是真龙头、谁是蹭概念.
---

# Industry Research Router

## Purpose

Use this as the first-stop router for investment-oriented industry and company research. It selects the smallest useful skill combination and enforces the project output discipline.

This router is for the `产业链投研` project. It is not a daily-report automation router and should not create cron jobs, heartbeat tasks, email reports, or batch browser pipelines unless the user explicitly asks for automation.

## Skill Selection

Choose the smallest useful combination:

- Semiconductor/AI-chain structure and A-share mapping: `semiconductor-ai-chain-investment-researcher`; add `ai-chain-research-orchestrator` when current evidence, rumors, Grok/X, Gemini, or live web verification matters.
- Browser Grok/Gemini collection: `browser-grok-gemini-research` only when the user asks for webpage Grok/Gemini, when X/Grok discovery is needed, or when Gemini can materially help with source discovery, counter-evidence, or Gemini web Deep Research.
- General industry essence and technology moat: `deep-research` as a long-research framework, not a local API executor; use `20-andruia-niche-intelligence` only as optional background framing for non-semiconductor niche work.
- Competitive landscape and true leaders: `competitive-landscape`, `competitive-intel`.
- Company fundamentals and valuation after segment selection: `stock-evaluator`, `business-analyst`, plus market-data skills according to listing market.
- A-share/HK/US live data and K-line checks: `allstock-data`, `banana-farmer`, `stock-data-skill`, or `finance`; market data cannot prove beneficiary status.
- Overseas oligarch data: `yfinance-mcp-server`, `stocks`, `alpha-vantage`.
- Structured comparison, score consistency, bias control, or watchlist tables: `spreadsheet`, `xlsx-official`, `advanced-evaluation`; scoring helpers do not replace domain judgment.
- Web/news/filings collection: `web-scraper`, `firecrawl-scraper`, `tavily-web`; use browser Grok/Gemini only when it adds a distinct discovery or source-gap value.
- Source discovery and dense-source digestion: use `search-specialist` for official-source search strategy, source priority, and contradiction tracking; use `research-summarizer` to digest long reports, filings, whitepapers, transcripts, PDFs, and multi-source evidence sets.
- Dividend/low-volatility style backdrop: use `dividend-premium-tracker` for CSI Dividend Low Volatility dividend premium, bond-yield comparison, and high-dividend style context. It is not a default individual-stock selector.

## Boundary Rules

- `industry-research-router` classifies the request and picks the route; it does not score the full segment universe or pick final stocks by itself.
- `ai-chain-research-orchestrator` coordinates evidence collection and rumor discipline; it does not make final A-share recommendations.
- `browser-grok-gemini-research` operates webpages and collector prompts only; it is not a final analyst.
- `semiconductor-ai-chain-investment-researcher` is the main top-down AI/semiconductor investment skill: segment priority, bottleneck, overseas oligarchs, A-share mapping, and within-segment comparison.
- `advanced-evaluation` checks score consistency and bias; it does not replace source verification or domain judgment.
- `stock-evaluator` and `business-analyst` are used after segment selection for company-level fundamentals.
- `allstock-data` and local market data provide timing, liquidity, valuation, and risk context only.
- `search-specialist` and `research-summarizer` improve evidence quality and source digestion; they do not replace industry judgment or stock ranking skills.
- `dividend-premium-tracker` is a macro/style lens for dividend assets; it cannot prove payout sustainability or stock elasticity.
- `finance-news` and `stock-copilot-pro` can be useful, but their briefing/cron workflows are not default behavior in this project.

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
   - Latest news, rumor, or source-gap verification
   - Official-source search or long-source summarization
   - Dividend, low-volatility, or bond-yield comparison

2. Decide whether live collection is actually needed:
   - Use Grok/X first for real-time news, X/Twitter chatter, supply-chain leaks, rumors, and 爆料.
   - Use Gemini when the user asks for it, when source gaps or conflicts matter, when Gemini web Deep Research is useful, or when official/media/PDF source discovery can improve verification.
   - Do not call browser Grok/Gemini for evergreen industry education unless the user asks or the answer depends on current facts.

3. Use current data when facts may have changed:
   - Prices, PE/PB, market cap, turnover, volume, 5/20/60-day performance, earnings reports, guidance, order news, regulations, and policy must be verified with tools or web sources.
   - Prefer official filings, exchange disclosures, company reports, investor relations pages, and reputable financial data sources for hard claims.
   - Treat X/Twitter, Grok, Gemini, and similar assistant/search products as evidence collection only; Codex must do the final synthesis, evidence weighting, risk judgment, stock mapping, and conclusion.

4. Separate three rankings:
   - Fundamental quality ranking: business quality, moat, customer quality, margin structure, long-term competitiveness.
   - Earnings elasticity ranking: revenue growth, gross margin leverage, capacity utilization, operating leverage, order conversion.
   - Trading elasticity ranking: market cap, float market cap, turnover, volatility, technical position, catalyst density, expectation gap, crowding risk.

5. Avoid common errors:
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

Read `references/skill-map.md` when the user asks which skills should be used, when the routing choice is ambiguous, or when you need to verify the project-local skill names.
