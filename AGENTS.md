# 产业链投研项目说明

本项目专门用于产业链研究、公司研究、全球龙头梳理、技术壁垒分析、国产替代研究、股票基本面比较和交易弹性判断。

## 默认研究路由

- 新对话或新任务先使用本项目内的 `skills/industry-research-router` 作为入口技能，再按问题类型选择最小必要技能组合。
- AI/半导体产业链任务分两层：需要实时消息、爆料、Grok/X、Gemini 或网页证据时，先用 `skills/ai-chain-research-orchestrator` 协调证据；需要网页操作时再用 `skills/browser-grok-gemini-research` 作为浏览器采集辅助；之后用 `skills/semiconductor-ai-chain-investment-researcher` 做细分环节深研和 A 股硬证据映射。
- 非实时、非消息驱动的产业链学习或公司对比，不默认调用网页 Grok/Gemini；先用本地 skill 框架和必要的公开资料核对即可。
- 需要找官方资料、公告、年报、PDF、客户/供应商证据或多来源反证时，先用 `skills/search-specialist` 设计检索与证据优先级，再用网页/抓取技能获取材料；长文、研报、白皮书和多来源材料用 `skills/research-summarizer` 先结构化消化。
- 红利、低波、股息率溢价、股债性价比和防御风格问题可加 `skills/dividend-premium-tracker`，但它只提供风格和宏观背景，不替代个股基本面判断。
- 当技能选择不明确时，先读 `skills/industry-research-router/references/skill-map.md` 的路由表，再选择最小必要技能组合。

## 网页 Grok/Gemini 原则

- Grok/Gemini 网页端默认使用 `@chrome` / Chrome 插件，因为用户的 Grok 与 Gemini 账号在 Chrome 中保持登录。除非用户明确指定 `@浏览器` / Browser Use，或 Chrome 不可用且用户接受 fallback，不默认切换到内置浏览器。
- Playwright 只作为诊断或脚本化 fallback；除非能连接同一个已登录 Chrome 上下文，不能把 Playwright 结果当成默认 Chrome 会员账号结果。
- Grok/X 是实时消息、爆料、社交热度和 X/Twitter 线索的优先发现层，尤其适合最近 24/48/72 小时的 AI 产业链突发变化。
- Gemini 网页端是适当时使用的补充证据层：用户明确要求、需要 Gemini web Deep Research、需要找官方/媒体链接、Grok 线索冲突、或需要反证时再调用。
- Grok、X、Gemini 以及其他网页模型只作为信息采集工具；Codex 必须负责核验、证据分级、产业链映射、股票筛选和最终结论。
- 不把网页模型的投资结论、排名、目标价、因果解释直接作为本项目结论。

## 项目边界

- 本项目不是 `每日战报_浏览器自动化`，默认不创建 cron、heartbeat、邮件发送、批量报告守护脚本或自动化流水线产物。
- 如用户明确要求自动化、定时报送、日报、邮件或浏览器批量采集，再单独讨论是否接入相应项目或工具。
- `finance-news`、`stock-copilot-pro` 等带简报/定时任务语义的 skill 在本项目中只作为可选数据或新闻工具，不进入默认投研路由。

## 研究原则

- 先判断问题类型：产业链拆解、公司对比、技术壁垒、国产替代、基本面排序、交易弹性排序、数据表整理。
- 行业研究必须区分：产业链位置、价值量、技术壁垒、客户验证周期、国产替代难度、全球龙头。
- 股票研究必须区分：基本面质量、业绩弹性、交易弹性。不要把“公司好”直接等同于“股价弹性最大”。
- 涉及最新价格、市值、PE/PB、换手率、涨跌幅、财报、订单、政策、监管和公司公告时，必须联网或用本地行情工具核对。
- 优先引用官方公告、交易所披露、公司年报/季报、招股书和可信财经数据源。
- 对 A 股、港股、美股、日股、韩股、台股要明确交易所和 ticker 后缀，避免混淆上市主体。

## 常用技能组合

- AI/半导体产业链本质和 A 股映射：`industry-research-router` + `semiconductor-ai-chain-investment-researcher` + `deep-research`（长研究框架）；如涉及实时消息或爆料，加 `ai-chain-research-orchestrator` 和 `browser-grok-gemini-research`
- 非半导体产业链本质：`industry-research-router` + `deep-research`（长研究框架），必要时加 `20-andruia-niche-intelligence`
- 龙头/竞格：`industry-research-router` + `competitive-landscape` + `competitive-intel`
- 公司基本面：`industry-research-router` + `stock-evaluator` + `business-analyst`
- 股票弹性：`industry-research-router` + `allstock-data` + `banana-farmer` + `advanced-evaluation`
- 官方资料/公告/PDF/来源反证：`industry-research-router` + `search-specialist` + `web-scraper` / `firecrawl-scraper` / `tavily-web`；材料较长时加 `research-summarizer`
- 研报/白皮书/多来源消化：`industry-research-router` + `research-summarizer` + `advanced-evaluation`
- 红利低波/股息率溢价：`industry-research-router` + `dividend-premium-tracker` + `stock-evaluator` + 市场数据技能
- 海外寡头：`industry-research-router` + `yfinance-mcp-server` + `stocks` + `alpha-vantage`
- 表格打分：`industry-research-router` + `spreadsheet` + `xlsx-official` + `advanced-evaluation`
- 公告/网页抓取：`industry-research-router` + `web-scraper` + `firecrawl-scraper` + `tavily-web`

## 输出要求

默认结论先行。涉及排序时，至少给出：

- 基本面质量排名
- 业绩弹性排名
- 交易弹性排名
- 最大风险点
- 后续跟踪指标
