---
name: industry-research-router
description: >-
  Compatibility router for project-local industry-chain, company research, competitive landscape, fundamental stock research, valuation, trading elasticity, domestic substitution, technology moat, oligopoly, leader-vs-concept, and sector ranking questions. Use after user-investment-framework when a task needs the older project route matrix or when the user explicitly asks which project skills should be combined. Trigger on 产业链研究, 公司研究, 行业本质, 技术壁垒, 国产替代, 全球龙头, 寡头, 谁最有弹性, 股票弹性, 交易弹性, 估值, PE, 业绩弹性, 公司排序, 赛道拆解, 谁是真龙头, 谁是伪概念.
---

# Industry Research Router

## Purpose

Use this as a compatibility router inside the `产业链投研` project. The master entrypoint is `user-investment-framework`; this router refines the task category and selects the smallest useful companion skill mix.

This project is not a daily-report automation router. Do not create cron jobs, heartbeat tasks, email reports, or batch browser pipelines unless the user explicitly asks for automation.

For a larger route table, read `references/skill-map.md`.

## Skill Selection

Choose the smallest useful combination:

- Semiconductor/AI-chain structure and A-share mapping: `semiconductor-ai-chain-investment-researcher`; add `ai-chain-research-orchestrator` when current evidence, rumors, Grok/X, Gemini, or live web verification matters.
- Growth-industry bottleneck disassembly: `industry-chain-deep-disassembly`; use it for terminal demand, chain topology, BOM/value nodes, current supply-gap bottlenecks, future bottleneck migration, lead-time, qualified-capacity constraints, and adapter-guided node mapping.
- Browser Grok/Gemini collection: `browser-grok-gemini-research` only when the user asks for webpage Grok/Gemini, X/Grok discovery, Gemini Deep Research, source-gap collection, or counter-evidence.
- General industry essence and technology moat: `deep-research` and `industry-chain-deep-disassembly` for bottleneck/value-chain work.
- Competitive landscape and true leaders: `competitive-landscape`, `competitive-intel`.
- Earnings releases, management guidance, and conference-call analysis: `earnings-call-investment-analyst`.
- A-share watchlist tracking and daily state maintenance: `a-share-company-tracking`; add `a-share-disclosure-trading-data` whenever CNINFO, exchange announcements, investor-relations records, dragon-tiger lists, block trades, or T/T+1 evening announcement windows matter.
- Company fundamentals after segment/source selection: `stock-fundamental-moat-triad`, then `stock-evaluator`, `business-analyst`, plus market-data skills according to listing market.
- A-share/HK/US live data and K-line checks: `TDX Finance Data:tdx-finance-data`, `tdx-finance-data`, iFinD MCPs, `ht-local-market-data` for local `C:\zd_huatai` post-close daily files/block pools, `allstock-data`, `banana-farmer`, or `finance`. Market data cannot prove beneficiary status.
- Overseas oligarch data: `finance`, `alpha-vantage`, iFinD global stock MCP, and official filings/IR; still use official filings and company sources for hard claims.
- Structured comparison, score consistency, and watchlist tables: `spreadsheet`, `xlsx-official`, `advanced-evaluation`.
- Web/news/filings collection: `search-specialist`, then `firecrawl-scraper`, `tavily-web`, or global `web-scraper`; use `research-summarizer` for long sources.
- Dividend/low-volatility style backdrop: `dividend-premium-tracker`, not a default individual-stock selector.

## Boundary Rules

- `industry-research-router` classifies and routes; it does not make final stock picks alone.
- `ai-chain-research-orchestrator` coordinates evidence collection and rumor discipline; it does not make final A-share recommendations.
- `browser-grok-gemini-research` operates webpages and collector prompts only; it is not a final analyst.
- `semiconductor-ai-chain-investment-researcher` is the main top-down AI/semiconductor investment skill.
- `industry-chain-deep-disassembly` is the cross-industry bottleneck skill; listed-company mapping is optional after node diagnosis.
- `advanced-evaluation` checks score consistency and bias; it does not replace source verification or domain judgment.
- `stock-fundamental-moat-triad` answers the future first: what could change, how it could become earnings, and what must be verified.
- `stock-evaluator` and `business-analyst` handle company-level financial quality, valuation, and operating logic after segment selection.
- `a-share-company-tracking` owns watchlist-driven A-share tracking and durable company files.
- `a-share-disclosure-trading-data` owns official announcement and trading-event evidence discipline.
- TDX, `ht-local-market-data`, `allstock-data`, `finance`, Yahoo-style tools, QVeris, Banana Farmer, and other market-data helpers provide timing, liquidity, valuation, technical, market-attention, and risk context only.
- TDX涨停原因,原因揭秘, and concept labels are secondary trading context; they can guide source checks but cannot replace official filings, CNINFO, exchange disclosures, company IR, or customer/supplier evidence.
- `ht-local-market-data` reads only local HT/TongdaXin files such as `.day`, `.lc1`, `vipdoc\cw`, `T0002\blocknew`, and `hq_cache`; its output stays `market_data_vendor` or `secondary_trading_context`, and account/password/order/log details are out of scope unless explicitly requested.
- `search-specialist` and `research-summarizer` improve evidence quality and source digestion; they do not replace industry judgment or stock ranking skills.
- `finance-news` and `stock-copilot-pro` can be useful, but their briefing/cron workflows are not default behavior in this project.

If a named companion skill is unavailable in the current session, continue with the same analytical framework and state the gap only when it changes confidence.

## Workflow

1. Classify the task:
   - industry-chain map;
   - company comparison;
   - earnings release, guidance, conference call, or expectation-gap analysis;
   - technology moat;
   - supply-chain bottleneck, BOM, lead-time, HHI, or pricing-power disassembly;
   - domestic substitution;
   - fundamental investment ranking;
   - trading elasticity ranking;
   - A-share company tracking or watchlist maintenance;
   - A-share announcement, CNINFO, IR record, dragon-tiger list, or block-trade verification;
   - data table, normalized evidence pack, or watchlist construction;
   - latest news, rumor, or source-gap verification;
   - official-source search or long-source summarization;
   - dividend, low-volatility, or bond-yield comparison.
2. Decide whether live collection is needed. Prices, PE/PB, market cap, turnover, volume, financial reports, orders, policies, regulations, and news must be verified with current tools or web sources.
3. Separate three rankings: fundamental quality, earnings elasticity, trading elasticity.
4. Preserve source hierarchy: official disclosure first, credible secondary sources second, market data as context, social/model output as leads only.
5. Avoid turning a quick route selection into a full report unless the user asks for that artifact.

## Output Pattern

Start with the answer, then explain:

```text
结论先行：
- 最大交易弹性：
- 最大业绩弹性：
- 最稳趋势中军：
- 最大风险：

排序：
1. 公司A：核心理由
2. 公司B：核心理由
3. 公司C：核心理由

关键观察指标：
- 公司A：订单 / 客户认证 / 毛利率 / 换手率 / 20日涨幅
- 公司B：价格 / 产能 / 库存 / 估值 / 催化剂
```

For industry-chain education:

```text
产业链拆解：
1. 上游材料 / 设备 / 耗材
2. 中游制造 / 封装 / 检测
3. 下游应用 / 客户

真正壁垒：
- 良率
- 客户验证
- 工艺参数
- 规模制造
- 供应链认证
```

## Anti-Patterns

- Do not equate "good company" with "highest stock elasticity".
- Do not equate "hot theme" with "real beneficiary".
- Do not rank only by PE.
- Do not treat one-time low-base growth as durable growth without checking order quality and customer verification.
- Do not mix mainland China, Taiwan, Hong Kong, US, Japan, and Korea listings without normalizing ticker suffixes and market rules.
