# Skill Map For Industry And Company Research

## Routing Protocol

1. Start with `industry-research-router` for every industry-chain, company, valuation, leader, substitution, moat, ranking, or trading-elasticity question.
2. Classify the user's real request before answering:
   - Learn the industry: chain position, value share, moat, verification cycle, domestic substitution.
   - Compare companies: true leader, concept follower, customer quality, margin structure, order conversion.
   - Evaluate stocks: fundamental quality, earnings elasticity, trading elasticity, valuation and risk.
   - Build data output: table, scorecard, watchlist, Excel workbook, factor strategy.
   - Collect evidence: filings, announcements, news, official pages, PDFs, market data.
   - Digest sources: annual reports, quarterly reports, whitepapers, sell-side reports, transcripts, long PDFs, and multi-source evidence sets.
   - Assess technology: AI, software stack, chips, embedded systems, architecture defensibility.
3. Choose the smallest useful skill mix. Add live-data or web skills whenever the task depends on current price, market cap, PE/PB, volume, financial reports, orders, policy, regulation, or news.
4. Use Grok/X through the logged-in Chrome plugin path for live AI-chain or rumor discovery by default. Use Gemini through Chrome only when it adds value: user explicitly asks, Gemini web Deep Research is useful, source gaps matter, conflicting evidence needs counter-checking, or hard-to-find official/media/PDF sources are needed.
5. Keep three investment rankings separate: fundamental quality, earnings elasticity, and trading elasticity. Do not turn "best company" into "highest stock elasticity" without market-data evidence.
6. If a referenced skill is unavailable, keep the same framework and state the gap only when it changes confidence.

## Boundary Rules

| Skill / Layer | Allowed Role | Boundary |
|---|---|---|
| `industry-research-router` | Entry classification, evidence discipline, and minimal route selection | Does not score the full segment universe or pick final stocks alone |
| `a-share-company-tracking` | A-share watchlist daily tracking, baseline/state/events maintenance, per-company worker batching, run-status reconciliation | Does not replace company research or make final investment conclusions by itself |
| `a-share-disclosure-trading-data` | CNINFO, exchange announcements, IR records, dragon-tiger lists, block trades, and T/T+1 announcement-window checks | Evidence/data layer only; does not prove business quality or trading recommendation |
| `ai-chain-research-orchestrator` | AI-chain evidence coordination, Grok/X rumor discipline, Gemini source-gap discipline | Collector/coordinator only; not the final stock selector |
| `browser-grok-gemini-research` | Webpage operation and collector prompt discipline for Grok/X and Gemini | Does not verify or conclude; hands objective items back to Codex |
| `semiconductor-ai-chain-investment-researcher` | Main top-down AI/semiconductor investment skill: segment priority, technology bottleneck, overseas oligarchs, A-share mapping, within-segment comparison | Must start from segment universe, not from hot stock names |
| `serenity-alpha` | News/event to observable demand, financial-statement transmission, small-cap elasticity, market-misclassification, and validation-checkpoint hypotheses | Hypothesis layer only; does not replace source discovery, official evidence, market data, beneficiary proof, or final ranking |
| `advanced-evaluation` | Three-layer score consistency, rank sanity checks, and bias control | Does not replace domain judgment or source verification |
| `stock-fundamental-moat-triad` | Company-level future-highlight test: what can change, how it becomes earnings, and whether value-chain, peers, competition, and customer milestones support it | Does not replace source collection, financial data, valuation, or trading-elasticity analysis |
| `stock-evaluator` + `business-analyst` | Company fundamentals, valuation, financial quality, and hard-evidence checks after segment selection | Does not decide segment priority alone |
| `allstock-data` + `banana-farmer` | Quotes, K-lines, liquidity, trend, timing, and risk context | Cannot prove beneficiary status |
| HTSC plugin tools: `query-indicator`, `select-stock`, `financial-analysis`, `watchlist-management`, `a-share-paper-trading` | A-share indicator lookup, candidate screening, quick external diagnosis, HTSC watchlist service, and simulated trading | Data/candidate/service/execution layer only; not a primary individual-stock research, primary real-time quote, historical行情, VCP, factor, backtesting, or final-conclusion source |
| `search-specialist` + `research-summarizer` | Source discovery, source-quality ranking, contradiction tracking, long-source digestion, and citation extraction | Does not make final investment conclusions |
| `dividend-premium-tracker` | Dividend/low-volatility style backdrop and stock-bond yield spread interpretation | Does not prove individual-stock payout durability or trading elasticity |
| `20-andruia-niche-intelligence` | Optional background framing for non-semiconductor niche work | Not the primary AI/semiconductor investment skill |

## Quick Trigger Matrix

| User Intent / Trigger | First Skill Mix | Notes |
|---|---|---|
| News/rumor/order/product launch/price hike/supply-chain change -> small-cap alpha or financial-statement transmission | `industry-research-router` + `search-specialist` / `ai-chain-research-orchestrator` + `serenity-alpha` + `allstock-data` + `advanced-evaluation` | First prove observable demand and source quality, then translate to financial lines and validation conditions. |
| AI/半导体产业链怎么拆、行业本质、价值量、壁垒 | `industry-research-router` + `semiconductor-ai-chain-investment-researcher` + `deep-research` | If current news or rumors matter, add `ai-chain-research-orchestrator`. |
| 最近24/48/72小时 AI 产业链消息、爆料、涨价、短缺、停产 | `industry-research-router` + `ai-chain-research-orchestrator` + `browser-grok-gemini-research` + `semiconductor-ai-chain-investment-researcher` + `allstock-data` | Grok/X first for X-native discovery. Gemini is used when requested or useful for source gaps/counter-evidence/Gemini web Deep Research. Codex verifies and concludes. |
| 非半导体产业链怎么拆、行业本质、价值量、壁垒 | `industry-research-router` + `deep-research`; optionally `20-andruia-niche-intelligence` | Output chain map, value distribution, moat, verification cycle, substitution difficulty. |
| 成长行业瓶颈、BOM、交货时滞、当前堵点/卡点、未来卡点迁移、HHI、定价权、利润池迁移、用户提供 CSV/JSON/XLSX 研究数据 | `industry-research-router` + `industry-chain-deep-disassembly`; load its matching adapter for PCB/CCL, 液冷, 光模块, or 数据中心电力; use its data-interface normalizer for raw files; add `search-specialist` when hard-source discovery is needed; add `stock-evaluator` / market-data skills only when the user asks for listed-company mapping after node selection | Here 堵点/卡点 means an obvious supply gap: demand exceeds qualified supply in the stated window. Start from terminal demand, chain topology, current supply-gap ledger, and future supply-gap scenarios. Avoid starting from hot stock names. |
| 谁是真龙头、谁蹭概念、竞争格局、海外寡头 | `industry-research-router` + `competitive-landscape` + `competitive-intel` | Separate market share, customer validation, profitability, and narrative heat. |
| AI/半导体国产替代、卡脖子、进口替代难度 | `industry-research-router` + `semiconductor-ai-chain-investment-researcher` + `competitive-landscape` | Focus on exact segment exposure, customer certification, yield, process know-how, reliability, switching cost, and A-share hard evidence. |
| 单只股票能买吗、估值、买卖点、仓位 | `industry-research-router` + `stock-evaluator` + market data skill | Never fabricate numbers. Do not substitute HTSC quick diagnosis for the upstream/downstream, demand pass-through, core-product price/unit-economics, and official-evidence checks. |
| 多家公司谁更好、基本面排序 | `industry-research-router` + `stock-fundamental-moat-triad` + `stock-evaluator` + `business-analyst` + `advanced-evaluation` | Build explicit rubric and cite hard data. |
| 谁股票弹性最大、短线弹性、交易弹性 | `industry-research-router` + `allstock-data` + `banana-farmer` + `advanced-evaluation` | Prioritize float market cap, turnover, volatility, 20/60-day trend, catalyst density, crowding risk. |
| A股公司持续跟踪、watchlist日更、baseline/state/events维护 | `industry-research-router` + `a-share-company-tracking` + `a-share-disclosure-trading-data` + `search-specialist` + `research-summarizer` | At or after 20:00 Beijing time, check both announcement date T and T+1. Keep one company per worker when sub-agent tools are available. |
| A股公告、CNINFO、交易所披露、龙虎榜、大宗交易核验 | `industry-research-router` + `a-share-disclosure-trading-data` + `search-specialist`; add `allstock-data` for market reaction | Treat trading events as liquidity/elasticity signals, not fundamental proof. |
| A股/港股/美股实时行情、K线、盘口 | `allstock-data` for CN/HK/US quick checks; `yfinance-mcp-server` / `stocks` for global; `alpha-vantage` for indicators | Tencent API returns GBK text and may delay up to 15 minutes. Always normalize exchange/ticker suffix. |
| A股最新价、PE/PB、成交额、换手率、多股指标对比 | `query-indicator`; fall back to `allstock-data` / other market-data skills if unavailable | Fast indicator lookup only. Record date/time and do not use market data to prove beneficiary status. |
| 按自然语言条件筛股票/ETF/基金候选池 | `select-stock` + `advanced-evaluation`; add project research skills before final ranking | Screening output is a candidate list, not a recommendation or real-beneficiary proof. |
| 大盘、板块、个股快速诊断或资讯利好利空整理 | `financial-analysis`; add source and project research skills for final conclusion | Use as external context. Verify important claims and do not copy its investment conclusion blindly. |
| 查询或添加华泰自选股 | `watchlist-management` | HTSC external watchlist only; keep separate from repository watchlists and company-tracking state. |
| A股模拟盘查资金、持仓、挂单、成交，或明确模拟下单/撤单 | `a-share-paper-trading` | Simulated trading only; never execute order/cancel actions without explicit user instruction. |
| 海外公司、ETF、期权、股息、财报历史 | `yfinance-mcp-server` + `stocks` + `alpha-vantage` | Use official filings and reputable data sources for financial claims. |
| 官方资料、公告、年报、官网、PDF、客户/供应商证据检索 | `industry-research-router` + `search-specialist` + `web-scraper` / `firecrawl-scraper` / `tavily-web` | Design queries and source priority first, then extract. Cite official or primary-adjacent sources whenever possible. |
| 研报、白皮书、公告、会议纪要、多来源材料消化 | `industry-research-router` + `research-summarizer` + `advanced-evaluation` | Extract claim-evidence-limitations before final industry or stock synthesis. |
| 红利低波、股息率溢价、股债性价比、防御风格 | `industry-research-router` + `dividend-premium-tracker` + `stock-evaluator` + market data skill | Use as style and macro backdrop only. Check dividend sustainability and valuation separately. |
| 表格、评分卡、watchlist、Excel模型 | `spreadsheet` + `xlsx-official` + `advanced-evaluation` | Preserve existing formatting; formulas must recalc without errors. |
| 多因子选股、量化规则、策略配置 | `multi-factor-strategy` + `data-scientist` + `senior-data-scientist` | Define factor universe, rebalance rules, risk controls, and validation method. |
| AI、软件、芯片、技术栈壁垒 | `ai-engineer` / `ai-ml` + `tech-stack-evaluator` + `cto-advisor` / `senior-architect` | Judge whether moat comes from architecture, ecosystem, data, deployment, or switching cost. |
| ARM、MCU、边缘计算、嵌入式芯片 | `arm-cortex-expert` + `senior-architect` | Focus on firmware, instruction set, peripherals, reliability, and supply-chain constraints. |
| 产品商业化、PMF、用户购买逻辑 | `product-manager` + `product-manager-toolkit` + `business-analyst` | Useful when research needs adoption barrier and buyer workflow analysis. |

## Data Discipline

- Latest price, market cap, PE/PB, turnover, volume, K-line, financial reports, orders, policy, regulation, and news require web or local market-data verification.
- Preferred evidence order: official announcements, exchange filings, annual/interim/quarterly reports, prospectuses, company investor relations, then reputable financial data vendors.
- HTSC plugin outputs are supplemental for indicators, screening, quick diagnosis, external watchlist, and simulated trading. Do not treat them as the primary real-time quote source, primary historical OHLCV source, VCP/factor/backtest data source, or sufficient evidence for individual-stock conclusions.
- HTSC write-capable actions, including external watchlist changes and simulated order/cancel operations, require explicit user instruction. Read-only indicator, diagnosis, screening, and account-status checks still need source labeling when used in research output.
- For A-share, Hong Kong, US, Japan, Korea, and Taiwan listings, explicitly identify exchange and ticker suffix before comparing companies.
- When data is missing, write `N/A` or explain the missing source. Do not infer exact numeric values from memory.

## Core Research

| Skill | Use Case |
|---|---|
| `semiconductor-ai-chain-investment-researcher` | Main AI/semiconductor investment deep-research skill: subsegment priority, technology bottleneck, overseas oligarchs, hard-evidence A-share mapping, within-segment comparison, 1-3 picks or observation-only. |
| `20-andruia-niche-intelligence` | Optional non-semiconductor niche/domain framing. Do not use as the main AI/semiconductor investment-research skill. |
| `deep-research` | Long-form research planning, evidence grading, contradiction handling, and synthesis framework. It is not a local Gemini API executor and has no `scripts/research.py`. |
| `industry-chain-deep-disassembly` | Cross-industry deep disassembly for demand transmission, chain topology, BOM/value nodes, current堵点/卡点 ledgers with explicit supply-gap evidence, constraint mechanisms, future supply-gap migration, HHI as a supporting test, profit-pool migration, user-provided data normalization, and adapter-guided PCB/CCL, liquid-cooling, optical-module, or data-center-power node mapping. Stock mapping is optional after node diagnosis. |
| `competitive-landscape` | Competitive landscape, Porter-style structure, differentiation, true leader vs concept stock. |
| `competitive-intel` | Competitor tracking, market moves, positioning, battlecards. |
| `business-analyst` | Business model, KPI logic, operating indicators, strategic analysis. |
| `stock-fundamental-moat-triad` | Future-first fundamental framework that judges future highlight potential and earnings path, then uses exact value-chain exposure, same-node international peers, five-forces competition, and customer-certification evidence as support. |
| `product-manager` / `product-manager-toolkit` | Customer purchase logic, product-market fit, buyer workflow, adoption barriers. |

## Stock And Financial Data

| Skill | Use Case |
|---|---|
| `stock-evaluator` | Project-local stock evaluation after route/source collection, separating fundamental quality, earnings elasticity, trading elasticity, valuation, evidence strength, and risks. |
| `stock-fundamental-moat-triad` | Pre-valuation future-highlight filter that starts with future drivers and earnings path, then tests value-chain position, international peers, Porter Five Forces, and customer-certification barriers. |
| `serenity-alpha` | Event-driven alpha hypothesis translation: news -> observable demand -> revenue/profit transmission -> small-cap elasticity -> market-misclassification and validation path. |
| `a-share-company-tracking` | A-share watchlist baseline, daily update, per-company worker isolation, Grok/open-web fallback status, and durable `artifacts/company_tracking` records. |
| `a-share-disclosure-trading-data` | CNINFO, exchange announcements, IR records, dragon-tiger lists, block trades, and T/T+1 announcement-window evidence. |
| `allstock-data` | A-share, Hong Kong, US quotes, K-lines, order book, lightweight China market data. |
| `query-indicator` | HTSC A-share indicator lookup: latest/recent price,涨跌幅,成交额,换手率, PE/PB,财务指标, short historical point checks, and multi-stock comparison. Suitable for quick supplemental checks; unsuitable as a structured historical OHLCV warehouse. |
| `select-stock` | HTSC natural-language screening for stock/ETF/fund candidate pools. Suitable for discovery; unsuitable as final recommendation, strict audit screen, or true-beneficiary proof. |
| `financial-analysis` | HTSC quick market insight, individual-stock diagnosis, and news context. Suitable as external context; unsuitable as final thesis or replacement for official evidence. Avoid defaulting to slow investment-calendar requests. |
| `watchlist-management` | HTSC external watchlist query/add operations. Suitable only for explicit HTSC watchlist work; keep separate from repo `watchlists/*.xlsx` and company-tracking state. |
| `a-share-paper-trading` | HTSC simulated A-share account, position, order, cancellation, sparse quote, and trade-history operations. Suitable for explicit paper-trading work; unsuitable for live trading, unrequested simulated orders, or primary quote/history storage. |
| `banana-farmer` | Momentum, RSI, position risk, volatility, and trading-oriented scans. |
| `stock-data-skill` | Supplemental stock data utilities when available. |
| `finance` | Broad quotes, time series, FX, and market snapshots. |
| `yfinance-mcp-server` / `stocks` | Overseas quotes, history, financials, earnings, dividends, options, news. |
| `alpha-vantage` | Global market data, macro, company fundamentals, technical indicators. |
| `dividend-premium-tracker` | China high-dividend/low-volatility style backdrop: dividend premium, bond-yield comparison, and defensive-equity timing context. |
| `stock-copilot-pro` | Optional market dashboard and news radar. Do not import its scheduled-brief/cron workflow unless the user asks. |
| `finance-news` | Optional headline/news context. Do not import its scheduled briefing workflow into this project by default. |

## Source Discovery And Evidence Digest

| Skill | Use Case |
|---|---|
| `search-specialist` | Query design, official-source priority, contradiction tracking, source credibility ranking, and multilingual search plans. |
| `research-summarizer` | Summarize and compare filings, reports, whitepapers, PDFs, transcripts, articles, and multiple sources before final synthesis. |

## Scoring And Structured Output

| Skill | Use Case |
|---|---|
| `spreadsheet` | Read/write/analyze tables, preserve spreadsheet formatting, maintain watchlists. |
| `xlsx-official` | Excel formulas, charts, structured analysis, xlsx outputs. |
| `advanced-evaluation` | Build rubrics, score companies, compare model outputs, reduce ranking bias. |
| `data-scientist` | Data analysis, predictive modeling, business intelligence. |
| `senior-data-scientist` | Statistical rigor, causality, robustness checks. |
| `multi-factor-strategy` | Factor-based stock selection rules and strategy configuration. |

## Information Collection

| Skill | Use Case |
|---|---|
| `browser-grok-gemini-research` | Use the logged-in Chrome plugin path by default for Grok/X discovery and Gemini source/counter-evidence collection. |
| `web-scraper` | Extract web pages, news, metadata, structured entities. |
| `firecrawl-scraper` | Crawl websites, parse PDFs, extract structured data from pages. |
| `tavily-web` | Web/news/finance search and extraction with filters and citations. |
| `apify-market-research` | Broader market condition and geographic opportunity research. |
| `apify-competitor-intelligence` | Competitor strategy, pricing, ads, positioning, social signals. |
| `ai-chain-research-orchestrator` | AI supply-chain latest-news workflow: Grok/X discovery first when live rumors matter, Gemini only when helpful, then Codex supplemental verification, local market data, and ranked stock mapping. |

## Technical Moat Specialists

| Skill | Use Case |
|---|---|
| `ai-engineer` / `ai-ml` | AI infrastructure, model applications, RAG, agents, inference stack. |
| `ai-product` | AI product commercial quality and whether a product is more than a demo. |
| `tech-stack-evaluator` | Technology stack moat, migration cost, ecosystem health, TCO. |
| `cto-advisor` | Technical strategy, architecture decisions, long-term defensibility. |
| `senior-architect` | Complex systems, dependencies, architecture-level moat. |
| `arm-cortex-expert` | Embedded/chip architecture and edge computing topics. |

## Default Combinations

| User Question | Recommended Combination |
|---|---|
| "Which company has the most alpha from this news?" | `industry-research-router` + `search-specialist` / `ai-chain-research-orchestrator` + `serenity-alpha` + `allstock-data` + `advanced-evaluation` |
| “AI/半导体产业链怎么拆？” | `industry-research-router` + `semiconductor-ai-chain-investment-researcher` + `deep-research` |
| “AI产业链最近48小时消息/爆料并映射股票？” | `industry-research-router` + `ai-chain-research-orchestrator` + `browser-grok-gemini-research` + `semiconductor-ai-chain-investment-researcher` + `allstock-data` |
| “非半导体产业链怎么拆？” | `industry-research-router` + `deep-research`; optionally `20-andruia-niche-intelligence` |
| “这个成长行业真正卡脖子的瓶颈节点在哪？” | `industry-research-router` + `industry-chain-deep-disassembly` + matching adapter when available |
| “谁是真龙头，谁蹭概念？” | `industry-research-router` + `competitive-landscape` + `competitive-intel` |
| “这几家公司谁最值得关注？” | `industry-research-router` + `stock-fundamental-moat-triad` + `stock-evaluator` + `spreadsheet` + `advanced-evaluation` |
| “谁股票弹性最大？” | `industry-research-router` + `allstock-data` + `banana-farmer` + `advanced-evaluation` |
| “跑一下A股公司跟踪/更新watchlist公司状态” | `industry-research-router` + `a-share-company-tracking` + `a-share-disclosure-trading-data` |
| “查这几家公司今晚有没有公告/龙虎榜/大宗交易” | `industry-research-router` + `a-share-disclosure-trading-data` + `search-specialist` |
| “AI/半导体国产替代谁最有机会？” | `industry-research-router` + `semiconductor-ai-chain-investment-researcher` + `competitive-landscape` |
| “帮我做公司对比表/打分表” | `industry-research-router` + `spreadsheet` + `xlsx-official` |
| “帮我找公告/年报/官网/客户证据” | `industry-research-router` + `search-specialist` + `web-scraper` / `firecrawl-scraper` |
| “帮我总结这几篇研报/PDF/会议纪要” | `industry-research-router` + `research-summarizer` + `advanced-evaluation` |
| “红利低波现在有没有股债性价比？” | `industry-research-router` + `dividend-premium-tracker` + `stock-evaluator` + market data skill |
| “研究 AI/芯片/软件技术壁垒” | `industry-research-router` + `ai-engineer` or `tech-stack-evaluator` + `cto-advisor` |
