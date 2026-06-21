# 技能包清单

本清单是 `D:\vcp_hunter\产业链投研\skills` 的项目级索引。它只描述本项目内 skill 的推荐用法和边界，不替代每个 skill 自己的 `SKILL.md`。

## 总原则

- 主入口只有一个：`user-investment-framework`。
- `industry-research-router` 是兼容层和细分路由表，不再作为所有投研任务的第一入口。
- 外部 API / MCP / 网页模型类 skill 默认是数据层、采集层或交易上下文层，不能直接升级为官方证据或最终投资结论。
- 对外部 API skill 做维护或改动时，先做只读 smoke test；涉及付费额度、写外部状态或模拟交易下单时必须有明确用户指令。
- 本项目默认不创建定时任务、简报机器人、邮件/IM 推送、cron、heartbeat 或批量自动化流水线。

## 核心入口

| Skill | 角色 | 边界 |
|---|---|---|
| `user-investment-framework` | 投研任务总入口，负责需求分类、证据纪律、产业链框架、三层排序和最终输出形状。 | 不直接获取所有数据；只选择最小必要 companion skills。 |
| `industry-research-router` | 旧路由兼容层，细化产业链、公司、估值、交易弹性、公告和表格任务。 | 不覆盖 `user-investment-framework`。 |
| `deep-research` | 长研究计划、证据分级、反证、矛盾处理和综合框架。 | 不是本地 Gemini API 执行器。 |

## AI 与半导体产业链

| Skill | 使用场景 | 边界 |
|---|---|---|
| `semiconductor-ai-chain-investment-researcher` | AI/半导体细分环节优先级、技术瓶颈、海外寡头、A 股硬证据映射。 | 必须先从环节和节点出发，不从热门股票反推故事。 |
| `ai-chain-research-orchestrator` | 实时 AI 产业链消息、Grok/X 线索、Gemini 反证、证据协调。 | 采集协调层，不做最终选股。 |
| `browser-grok-gemini-research` | 使用已登录 Chrome 做 Grok/X/Gemini 网页采集。 | 只交接原始线索和来源，Codex 负责核验与结论。 |
| `industry-chain-deep-disassembly` | 供需传导、BOM/价值节点、当前供应缺口、未来卡点迁移、利润池迁移。 | 股票映射只在节点诊断后进行。 |

## 公司与股票研究

| Skill | 使用场景 | 边界 |
|---|---|---|
| `stock-fundamental-moat-triad` | 单公司或同行对比的未来亮点、下游需求、价值链位置、客户认证和护城河。 | 先判断未来能否变成业绩，再看估值和交易弹性。 |
| `stock-evaluator` | 基本面质量、业绩弹性、交易弹性、估值、风险。 | 需要已验证的产业链位置和必要当前数据。 |
| `business-analyst` | 商业模式、KPI、单位经济、运营指标。 | 必须连接到需求传导和财务结果。 |
| `serenity-alpha` | 新闻/事件到财务报表传导、小盘弹性、预期差和验证路径。 | 假设翻译层；先收集证据，再做市场数据和排名验证。 |
| `earnings-call-investment-analyst` | 财报、业绩会、指引、预期差、会后股价反应。 | 优先原始公告、财报和电话会材料。 |

## A 股跟踪与披露

| Skill | 使用场景 | 边界 |
|---|---|---|
| `a-share-company-tracking` | watchlist 日更、baseline/state/events、公司级状态文件、completion table。 | 跟踪层，不直接生成最终投资结论。 |
| `a-share-disclosure-trading-data` | CNINFO、交易所公告、IR 记录、龙虎榜、大宗交易、T/T+1 晚间公告窗口。 | 证据层和交易事件层，不证明业务质量。 |

## 来源发现与材料消化

| Skill | 使用场景 | 边界 |
|---|---|---|
| `search-specialist` | 官方来源优先级、检索式、多语种检索、反证和来源质量排序。 | 搜索设计和证据账本，不做最终投资判断。 |
| `research-summarizer` | 年报、公告、研报、白皮书、PDF、会议纪要和多来源材料结构化消化。 | 输出 claim/evidence/limitations，交给投研框架综合。 |
| 全局 `web-scraper` | 通用网页抽取和清洗。 | 仅作为已安装全局 skill 的 fallback；项目本地不保留重复副本。 |
| `firecrawl-scraper` | 深度抓取、页面抽取、PDF 解析和截图。 | 外部 API 工具，使用前确认 key 和额度。 |
| `tavily-web` | Tavily 搜索/抽取/研究 API，带日期、主题、域名和引用过滤。 | 可选来源覆盖工具，不替代官方来源和内置 web。 |
| `apify-market-research` | 地理市场、平台数据、消费者行为、价格和需求采集。 | 广义市场研究，不证明证券暴露。 |
| `apify-competitor-intelligence` | 竞品广告、内容、定价、平台表现采集。 | 外部采集层，不是财务证据。 |

## 行情、API 与交易上下文

| Skill | 使用场景 | 证据标签 |
|---|---|---|
| `tdx-finance-data` / `TDX Finance Data:tdx-finance-data` | A 股/HK/基金/指数/板块报价、估值、换手、技术指标、涨跌停、封单、连板、板型、概念热度。 | `market_data_vendor` 或 `secondary_trading_context`，绝不作为官方证据。 |
| `allstock-data` | A 股、港股、美股快速报价、K 线、盘口式轻量数据。 | 市场上下文。 |
| `finance` | 股票、ETF、指数、FX、部分 crypto、美国公司数据和 Financial Datasets 兜底。 | 补充数据源。 |
| `alpha-vantage` | Alpha Vantage 官方 API，全球市场、宏观、基本面和技术指标。 | 外部 API 数据源，注意 key、限速和条款。 |
| `banana-farmer` | 动量、RSI、波动率、技术风险、交易弹性辅助。 | 只用于交易弹性和技术风险。 |
| `stock-copilot-pro` | QVeris/OpenClaw 报价、基本面、技术、新闻和情绪。 | 可选工具，不自动生成默认结论、简报或行动建议。 |
| `finance-news` | 市场新闻简报、提醒、投递工作流。 | 只有用户明确要新闻简报或推送时使用。 |

## 表格、评分与模型

| Skill | 使用场景 | 边界 |
|---|---|---|
| `advanced-evaluation` | 评分表、排序一致性、偏差控制、三层排名。 | 不替代来源核验和产业判断。 |
| `spreadsheet` | 表格读写和格式保持。 | 用于表格数据任务。 |
| `xlsx` | `.xlsx` / `.xlsm` / `.csv` / `.tsv` 作为主输入或输出。 | 文件型表格交付。 |
| `xlsx-official` | Excel 公式、格式、图表和结构化工作簿。 | 保护格式和重算。 |
| `multi-factor-strategy` | 多因子选股和策略配置。 | 需要明确因子、样本、调仓和验证规则。 |
| `data-scientist` / `senior-data-scientist` | 数据分析、统计建模、因果和鲁棒性。 | 数据任务使用，不替代投研证据链。 |

## 文档与交付物

| Skill | 使用场景 |
|---|---|
| `docx` | Word 文档创建、读取、修改。 |
| `pdf` | PDF 读取、拆分、合并、OCR、表单和水印。 |
| `pptx` | PPT 创建、读取、修改和模板处理。 |

## 技术护城河与产品逻辑

| Skill | 使用场景 |
|---|---|
| `ai-engineer` / `ai-ml` | AI 基础设施、模型应用、RAG、Agent、推理栈。 |
| `ai-product` | AI 产品是否商业可用，而不是 demo。 |
| `tech-stack-evaluator` | 技术栈护城河、TCO、生态和迁移成本。 |
| `cto-advisor` / `senior-architect` | 架构、技术战略、系统依赖和可扩展性。 |
| `arm-cortex-expert` | ARM、MCU、边缘计算、嵌入式和芯片固件。 |
| `product-manager` / `product-manager-toolkit` | 用户购买逻辑、PMF、需求整理、路线图和商业化。 |

## Public Equity Investing 插件层

Public Equity Investing 插件只作为 PM 工作流 companion layer。它可以用于 thesis tracker、catalyst calendar、event underwriting、earnings preview/deep-dive、scenario sensitivity、portfolio risk、model update/audit、memo/pitch/tearsheet/deck QC。

它不能替代本项目的来源核验、产业链位置、下游需求传导、核心产品单位经济、真实受益者证明、基本面质量 / 业绩弹性 / 交易弹性排名。

## 建议整合状态

| 状态 | Skill |
|---|---|
| 主入口 | `user-investment-framework` |
| 兼容保留 | `industry-research-router` |
| 强推荐保留 | `semiconductor-ai-chain-investment-researcher`, `industry-chain-deep-disassembly`, `stock-fundamental-moat-triad`, `stock-evaluator`, `a-share-company-tracking`, `a-share-disclosure-trading-data`, `search-specialist`, `research-summarizer`, `advanced-evaluation` |
| 可选数据/API 层 | `tdx-finance-data`, `ifind-finance-data`, iFinD MCPs, HTSC/DFCF data skills, `allstock-data`, `finance`, `alpha-vantage`, `banana-farmer`, `stock-copilot-pro`, `finance-news`, `firecrawl-scraper`, `tavily-web`, `apify-*` |
| 可选技术/产品辅助 | `ai-engineer`, `ai-ml`, `ai-product`, `tech-stack-evaluator`, `cto-advisor`, `senior-architect`, `arm-cortex-expert`, `product-manager`, `product-manager-toolkit` |
| 文件交付 | `spreadsheet`, `xlsx`, `xlsx-official`, `docx`, `pdf`, `pptx` |
| 全局 fallback | 全局 `web-scraper`（仅在已安装且需要通用网页抽取时使用） |
