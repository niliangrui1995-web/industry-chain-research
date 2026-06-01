# 技能包清单

## 核心入口

- `user-investment-framework`：本项目所有投资研究任务的主入口技能。先用它统一判断产业链、个股、行情、公告、证据、输出文件等任务类型，再选择最小必要 companion skills。
- `industry-research-router`：产业链、公司研究、股票弹性、估值、国产替代、龙头识别和排序问题的入口路由技能。
- `ai-chain-research-orchestrator`：AI 产业链实时消息、Grok/X 线索、Gemini 辅助证据、Codex 复核、证据分级和股票映射协调技能。
- `browser-grok-gemini-research`：网页 Grok/Gemini 采集辅助技能。只负责浏览器采集、提示词边界和采集结果交接，不负责最终投资判断。
- `semiconductor-ai-chain-investment-researcher`：AI/半导体细分环节优先级、技术瓶颈、海外寡头、A 股硬证据映射和环节内横向比较主技能。
- `a-share-company-tracking`：A 股 watchlist 持续跟踪、baseline/state/events 维护、公司级 worker 批处理、Grok/open-web fallback 记录和 run_status 核对技能。
- `a-share-disclosure-trading-data`：CNINFO、交易所公告、IR 记录、龙虎榜、大宗交易和 T/T+1 公告窗口检查技能。

## 行业与竞争格局

- `20-andruia-niche-intelligence`
- `deep-research`：长周期研究规划、证据分层和综合框架；不包含本地 `scripts/research.py` 或 Gemini API 执行脚本。
- `industry-chain-deep-disassembly`：成长行业供需传导、产业链拓扑、BOM/价值节点、交货时滞、HHI、利润池迁移、定价权、纯度筛股和财务验证技能；识别供应缺口堵点后必须继续深拆该节点并判断可能持续时间；内置 PCB/CCL、液冷、光模块、数据中心电力适配器，并提供 CSV/JSON/JSONL/XLSX 数据接口归一化脚本。
- `competitive-landscape`
- `competitive-intel`
- `business-analyst`
- `product-manager`
- `product-manager-toolkit`

## 检索、证据消化与来源质量

- `search-specialist`：官方公告、年报、官网、客户/供应商证据、PDF、反证材料和多语言检索的查询设计与来源优先级。
- `research-summarizer`：研报、白皮书、公告、PDF、会议纪要和多来源材料的结构化消化；输出 claim-evidence-limitations，不直接给最终股票结论。

## 股票与财务数据

- `stock-evaluator`
- `serenity-alpha`: event/news-to-alpha financial translation; use for observable demand changes, revenue/profit transmission, small-cap elasticity, market misclassification, and 1-4 quarter validation paths. It produces testable hypotheses only and does not replace filings, official evidence, market data, or final ranking.
- `a-share-disclosure-trading-data`
- `allstock-data`
- `banana-farmer`
- `stock-data-skill`
- `finance`
- `yfinance-mcp-server`
- `stocks`
- `alpha-vantage`
- `dividend-premium-tracker`：红利低波、股息率溢价、股债性价比和防御风格的辅助判断；不替代个股基本面研究。
- `stock-copilot-pro`：可选行情/技术/简报工具，不进入默认投研路由。
- `finance-news`：可选新闻工具；其 cron/briefing 能力不属于本项目默认路由。

## 表格、评分与量化比较

- `spreadsheet`
- `xlsx-official`
- `advanced-evaluation`
- `data-scientist`
- `senior-data-scientist`
- `multi-factor-strategy`

## 信息抓取

- `web-scraper`
- `firecrawl-scraper`
- `tavily-web`
- `apify-market-research`
- `apify-competitor-intelligence`

## 技术壁垒专项

- `ai-engineer`
- `ai-ml`
- `ai-product`
- `tech-stack-evaluator`
- `cto-advisor`
- `senior-architect`
- `arm-cortex-expert`
