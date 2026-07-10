# Project Skill Integration Map

Use this reference when `user-investment-framework` needs to choose companion skills for a non-trivial investment research task.

Rule: start with `user-investment-framework`; load the smallest useful supporting set; preserve each supporting skill's boundary.

For the full per-skill and per-MCP boundary table, read `skill-mcp-boundary-matrix.md`.

## Entry And Backbone

| Skill | Role inside the master framework | Boundary |
|---|---|---|
| `user-investment-framework` | Master entrypoint, research logic, evidence discipline, ranking structure, and final output shape. | Does not fetch all data by itself. |
| `industry-research-router` | Legacy project router and compatibility layer for existing task categories. | Supporting router only; do not let it override the master framework. |
| `deep-research` | Long-form source map, evidence grading, contradiction handling, and synthesis plan. | Not a local Gemini API executor. |

## Route Families

| User intent | Start with | Add only if needed |
|---|---|---|
| Learn an industry chain | `user-investment-framework` | `industry-chain-deep-disassembly`, `deep-research`, source skills |
| AI/semiconductor stock mapping | `user-investment-framework` | `semiconductor-ai-chain-investment-researcher`, `ai-chain-research-orchestrator`, `browser-grok-gemini-research`, market-data skills |
| Single stock evaluation | `user-investment-framework` | `stock-fundamental-moat-triad`, `stock-evaluator`, `business-analyst`, source and market-data skills |
| News-driven alpha / small-cap elasticity | `user-investment-framework` | `search-specialist` or current-evidence skills first, then `serenity-alpha`, market-data skills, `advanced-evaluation` |
| Dated event with probability/payoff | `user-investment-framework` | source skills, `serenity-alpha` if event came from news, then Public Equity Investing event workflow |
| Thesis tracker or kill criteria | `user-investment-framework` | source/market-data skills, `a-share-company-tracking`, then Public Equity Investing thesis workflow |
| Catalyst calendar | `user-investment-framework` | source skills, `a-share-company-tracking`, then Public Equity Investing catalyst workflow |
| Pre/post earnings PM workflow | `user-investment-framework` | `earnings-call-investment-analyst`, then Public Equity Investing earnings workflow |
| Scenario sensitivity or action thresholds | `user-investment-framework` | `stock-evaluator`, `advanced-evaluation`, then Public Equity Investing scenario workflow |
| Position sizing or hedge plan | `user-investment-framework` | verified thesis, current market data, then Public Equity Investing risk workflow |
| "Who has most elasticity?" | `user-investment-framework` | TDX/iFinD/`allstock-data`, `ht-local-market-data` for local post-close daily K-line checks, `banana-farmer`, `advanced-evaluation` |
| A-share涨停/跌停, concept heat, limit-board reason scan | `user-investment-framework` | TDX first, then iFinD/HTSC/DFCF if needed; `ht-local-market-data` only for local daily/block-pool context; official-source skills for proof |
| Official evidence search | `user-investment-framework` | `search-specialist`, `a-share-disclosure-trading-data`, scraper/extract skills, `research-summarizer` |
| A-share watchlist update | `user-investment-framework` | `a-share-company-tracking`, `a-share-disclosure-trading-data`, optional TDX/iFinD for market reaction |
| Earnings-call analysis | `user-investment-framework` | `earnings-call-investment-analyst`, source and market-data skills |
| Model audit, model update, or normalized financials | `user-investment-framework` | `spreadsheet` / `xlsx-official`, then Public Equity Investing model workflows |
| Report or workbook output | `user-investment-framework` | `spreadsheet` / `xlsx` / `docx` / `pptx` / `pdf`; add packaging skills only when requested |

## Evidence And Data Discipline

- Latest price, market cap, PE/PB, turnover, volume, K-line, financial reports, orders, policy, regulation, and news require current verification.
- Preferred hard-evidence order: official announcements, exchange filings, annual/interim/quarterly reports, prospectuses, company IR, official customer/supplier sources.
- Use TDX for fast A-share trading context, iFinD for structured financial data, and `ht-local-market-data` for the user's refreshed local HT/TongdaXin daily files or block pools, but keep them as vendor data unless they surface original official documents.
- HTSC, DFCF, QVeris, Banana Farmer, Yahoo, Alpha Vantage, Simplywall.st, Apify, Tavily, Firecrawl, Grok/X, Gemini, and model outputs do not prove beneficiary status by themselves.
- For A-share, Hong Kong, US, Japan, Korea, and Taiwan listings, explicitly identify exchange and ticker suffix before comparing companies.
- When data is missing, write `N/A` or explain the missing source. Do not infer exact numeric values from memory.

## External API / MCP Gate

Before using a remote API or MCP:

1. Check whether the task needs current or remote data.
2. Use the narrowest read-only call possible.
3. Do not expose secrets; rely on environment variables or installed MCP/plugin configuration.
4. Label the result by evidence tier.
5. For write-capable tools, get explicit user instruction first.
6. For broad API changes or flaky external dependencies, use a subagent for read-only deep testing before updating project routing.

Local `C:\zd_huatai` file reads through `ht-local-market-data` are not remote API calls, but they still have privacy boundaries: do not inspect trading-account, password, order,委托, or log details unless explicitly requested.

## Public Equity Investing Boundary

Public Equity Investing plugin skills are companion PM workflows only. Use them after source evidence, chain position, downstream demand, and issuer/security context are established.

They do not replace:

- upstream/downstream mapping;
- official evidence;
- beneficiary proof;
- core-product demand and unit-economics checks;
- final fundamental-quality / earnings-elasticity / trading-elasticity ranking.

## Output Discipline

For investment answers, keep:

- conclusion first;
- evidence tier visible;
- downstream demand bridge;
- core product/unit-economics bridge when company earnings depend on it;
- fundamental quality, earnings elasticity, and trading elasticity separated;
- risk and next tracking indicators explicit.
