# Skill Map For Industry And Company Research

## Routing Protocol

1. Start with `industry-research-router` for every industry-chain, company, valuation, leader, substitution, moat, ranking, or trading-elasticity question.
2. Classify the user's real request before answering:
   - Learn the industry: chain position, value share, moat, verification cycle, domestic substitution.
   - Compare companies: true leader, concept follower, customer quality, margin structure, order conversion.
   - Evaluate stocks: fundamental quality, earnings elasticity, trading elasticity, valuation and risk.
   - Build data output: table, scorecard, watchlist, Excel workbook, factor strategy.
   - Collect evidence: filings, announcements, news, official pages, PDFs, market data.
   - Assess technology: AI, software stack, chips, embedded systems, architecture defensibility.
3. Choose the smallest useful skill mix. Add live-data or web skills whenever the task depends on current price, market cap, PE/PB, volume, financial reports, orders, policy, regulation, or news.
4. Keep three investment rankings separate: fundamental quality, earnings elasticity, and trading elasticity. Do not turn "best company" into "highest stock elasticity" without market-data evidence.
5. If a referenced skill is unavailable, keep the same framework and state the gap only when it changes confidence.

## Quick Trigger Matrix

| User Intent / Trigger | First Skill Mix | Notes |
|---|---|---|
| 产业链怎么拆、行业本质、价值量、壁垒 | `industry-research-router` + `20-andruia-niche-intelligence` + `deep-research` | Output chain map, value distribution, moat, verification cycle, substitution difficulty. |
| 谁是真龙头、谁蹭概念、竞争格局、海外寡头 | `industry-research-router` + `competitive-landscape` + `competitive-intel` | Separate market share, customer validation, profitability, and narrative heat. |
| 国产替代、卡脖子、进口替代难度 | `industry-research-router` + `20-andruia-niche-intelligence` + `competitive-landscape` | Focus on customer certification, yield, process know-how, reliability, and switching cost. |
| 单只股票能买吗、估值、买卖点、仓位 | `industry-research-router` + `stock-evaluator-v3` + market data skill | Never fabricate numbers. Use current data or mark unavailable values as `N/A`. |
| 多家公司谁更好、基本面排序 | `industry-research-router` + `stock-evaluator-v3` + `business-analyst` + `advanced-evaluation` | Build explicit rubric and cite hard data. |
| 谁股票弹性最大、短线弹性、交易弹性 | `industry-research-router` + `allstock-data` + `financial-intel` + `advanced-evaluation` | Prioritize float market cap, turnover, volatility, 20/60-day trend, catalyst density, crowding risk. |
| A股/港股/美股实时行情、K线、盘口 | `allstock-data` for CN/HK/US quick checks; `yfinance` / `stocks` for global; `alpha-vantage` for indicators | Tencent API returns GBK text and may delay up to 15 minutes. Always normalize exchange/ticker suffix. |
| 海外公司、ETF、期权、股息、财报历史 | `yfinance` + `stocks` + `alpha-vantage` | Use official filings and reputable data sources for financial claims. |
| 新闻、公告、年报、官网、PDF抓取 | `web-scraper` + `firecrawl-scraper` + `tavily` + `finance-news` | Try lightweight extraction first, escalate to browser/crawler only when needed, cite sources. |
| AI产业链最新消息、Grok/X爆料、Perplexity联网搜索、A股映射、必要时Gemini反证 | `industry-research-router` + `ai-chain-research-orchestrator` + `finance-news` + `allstock-data` + `advanced-evaluation` | For live news and rumors, Grok/X first-pass discovery is mandatory; then use Perplexity as a source finder, Codex web verification, and local market data. Use Gemini only for major unresolved or conflicting lines. |
| 表格、评分卡、watchlist、Excel模型 | `Spreadsheet` + `xlsx-official` + `advanced-evaluation` | Preserve existing formatting; formulas must recalc without errors. |
| 多因子选股、量化规则、策略配置 | `multi-factor-strategy` + `data-scientist` + `senior-data-scientist` | Define factor universe, rebalance rules, risk controls, and validation method. |
| AI、软件、芯片、技术栈壁垒 | `ai-engineer` / `ai-ml` + `tech-stack-evaluator` + `cto-advisor` / `senior-architect` | Judge whether moat comes from architecture, ecosystem, data, deployment, or switching cost. |
| ARM、MCU、边缘计算、嵌入式芯片 | `arm-cortex-expert` + `senior-architect` | Focus on firmware, instruction set, peripherals, reliability, and supply-chain constraints. |
| 产品商业化、PMF、用户购买逻辑 | `product-manager` + `product-manager-toolkit` + `business-analyst` | Useful when research needs adoption barrier and buyer workflow analysis. |

## Data Discipline

- Latest price, market cap, PE/PB, turnover, volume, K-line, financial reports, orders, policy, regulation, and news require web or local market-data verification.
- Preferred evidence order: official announcements, exchange filings, annual/interim/quarterly reports, prospectuses, company investor relations, then reputable financial data vendors.
- For A-share, Hong Kong, US, Japan, Korea, and Taiwan listings, explicitly identify exchange and ticker suffix before comparing companies.
- When data is missing, write `N/A` or explain the missing source. Do not infer exact numeric values from memory.

## Core Research

| Skill | Use Case |
|---|---|
| `20-andruia-niche-intelligence` | Industry essence, value chain, technology barriers, hidden pain points, customer verification, domestic substitution. |
| `deep-research` | Long-form multi-step research, market analysis, technical research, due diligence. |
| `competitive-landscape` | Competitive landscape, Porter-style structure, differentiation, true leader vs concept stock. |
| `competitive-intel` | Competitor tracking, market moves, positioning, battlecards. |
| `business-analyst` | Business model, KPI logic, operating indicators, strategic analysis. |
| `Product Manager` / `product-manager-toolkit` | Customer purchase logic, product-market fit, buyer workflow, adoption barriers. |

## Stock And Financial Data

| Skill | Use Case |
|---|---|
| `stock-evaluator-v3` | Comprehensive stock evaluation combining valuation, fundamentals, technicals, buy/hold/sell framing. |
| `stock-copilot-pro` | US/HK/CN quote, fundamentals, technicals, news radar, actionable market view. |
| `allstock-data` | A-share, Hong Kong, US quotes, K-lines, order book, lightweight China market data. |
| `yfinance` / `stocks` | Overseas quotes, history, financials, earnings, dividends, options, news. |
| `alpha-vantage` | Global market data, macro, company fundamentals, technical indicators. |
| `financial-intel` | Momentum, RSI, coil breakout, portfolio intelligence, trading-oriented scans. |
| `finance-news` | Market news briefings, headlines, stock news, alert context. |

## Scoring And Structured Output

| Skill | Use Case |
|---|---|
| `Spreadsheet` | Read/write/analyze tables, preserve spreadsheet formatting, maintain watchlists. |
| `xlsx-official` | Excel formulas, charts, structured analysis, xlsx outputs. |
| `advanced-evaluation` | Build rubrics, score companies, compare model outputs, reduce ranking bias. |
| `data-scientist` | Data analysis, predictive modeling, business intelligence. |
| `senior-data-scientist` | Statistical rigor, causality, robustness checks. |
| `multi-factor-strategy` | Factor-based stock selection rules and strategy configuration. |

## Information Collection

| Skill | Use Case |
|---|---|
| `web-scraper` | Extract web pages, news, metadata, structured entities. |
| `firecrawl-scraper` | Crawl websites, parse PDFs, extract structured data from pages. |
| `tavily` | Web/news/finance search and extraction with filters and citations. |
| `apify-market-research` | Broader market condition and geographic opportunity research. |
| `apify-competitor-intelligence` | Competitor strategy, pricing, ads, positioning, social signals. |
| `ai-chain-research-orchestrator` | AI supply-chain latest-news workflow that requires Grok/X first-pass discovery for live news and rumors, then coordinates Perplexity source search, Codex web checks, local market data, ranked stock mapping, and optional Gemini counter-checks. |

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
| “这个产业链怎么拆？” | `industry-research-router` + `20-andruia-niche-intelligence` + `deep-research` |
| “谁是真龙头，谁蹭概念？” | `industry-research-router` + `competitive-landscape` + `competitive-intel` |
| “这几家公司谁最值得关注？” | `industry-research-router` + `stock-evaluator-v3` + `Spreadsheet` + `advanced-evaluation` |
| “谁股票弹性最大？” | `industry-research-router` + `allstock-data` + `financial-intel` + `advanced-evaluation` |
| “国产替代谁最有机会？” | `industry-research-router` + `20-andruia-niche-intelligence` + `competitive-landscape` |
| “帮我做公司对比表/打分表” | `industry-research-router` + `Spreadsheet` + `xlsx-official` |
| “帮我抓公告/年报/官网资料” | `industry-research-router` + `web-scraper` + `firecrawl-scraper` |
| “帮我抓AI产业链最近48小时消息/爆料并映射股票” | `industry-research-router` + `ai-chain-research-orchestrator` + `finance-news` + `allstock-data`; Grok/X first-pass discovery is mandatory, followed by Perplexity source search and Codex verification |
| “研究 AI/芯片/软件技术壁垒” | `industry-research-router` + `ai-engineer` or `tech-stack-evaluator` + `cto-advisor` |
