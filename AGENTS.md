# 产业链投研项目说明

本项目专门用于产业链研究、公司研究、全球龙头梳理、技术壁垒分析、国产替代研究、股票基本面比较和交易弹性判断。

## 默认研究路由

新对话或新任务优先使用本项目内的 `skills/industry-research-router` 作为入口技能，再按问题类型组合调用其他技能。
当技能选择不明确时，先读 `skills/industry-research-router/references/skill-map.md` 的路由表，再选择最小必要技能组合。

## 研究原则

- 先判断问题类型：产业链拆解、公司对比、技术壁垒、国产替代、基本面排序、交易弹性排序、数据表整理。
- 行业研究必须区分：产业链位置、价值量、技术壁垒、客户验证周期、国产替代难度、全球龙头。
- 股票研究必须区分：基本面质量、业绩弹性、交易弹性。不要把“公司好”直接等同于“股价弹性最大”。
- 涉及最新价格、市值、PE/PB、换手率、涨跌幅、财报、订单、政策、监管和公司公告时，必须联网或用本地行情工具核对。
- 优先引用官方公告、交易所披露、公司年报/季报、招股书和可信财经数据源。
- 对 A 股、港股、美股、日股、韩股、台股要明确交易所和 ticker 后缀，避免混淆上市主体。

## 常用技能组合

- 产业链本质：`industry-research-router` + `20-andruia-niche-intelligence` + `deep-research`
- 龙头/竞格：`industry-research-router` + `competitive-landscape` + `competitive-intel`
- 公司基本面：`industry-research-router` + `stock-evaluator` + `business-analyst`
- 股票弹性：`industry-research-router` + `allstock-data` + `banana-farmer` + `advanced-evaluation`
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
