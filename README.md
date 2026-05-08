# 产业链投研

Last verified: 2026-05-09

这是一个面向产业链研究、公司研究、全球龙头梳理、技术壁垒分析、国产替代研究、股票基本面比较和交易弹性判断的 Codex 本地工作区。它的核心目标不是生成日报或自动化流水线，而是把“证据收集 -> 产业链拆解 -> 公司映射 -> 基本面/业绩/交易弹性分层判断”固定成可复用的投研流程。

## 项目定位

- 研究对象：AI/半导体产业链、非半导体成长行业、海外寡头、A 股/港股/美股/台股/日股/韩股上市主体、红利低波和防御风格资产。
- 研究问题：产业链位置、价值量、技术壁垒、客户验证周期、国产替代难度、真实受益链条、基本面质量、业绩弹性、交易弹性和风险点。
- 默认方法：先用本地技能路由确定最小技能组合，再根据任务需要调用公开资料、公告、网页证据、行情数据或 Grok/Gemini 采集。
- 结论纪律：不把“好公司”“热门概念”“网页模型回答”直接等同于投资结论；Codex 负责证据分级、产业链映射、股票筛选和最终判断。

## 主要目录

- `AGENTS.md`：本项目的默认规则、浏览器/Grok/Gemini 使用边界、备份流程和输出要求。
- `SKILL_PACK_MANIFEST.md`：项目内技能清单和每类技能的用途。
- `skills/industry-research-router/`：所有产业链、公司、估值、排序、龙头识别和交易弹性问题的入口技能。
- `skills/industry-research-router/references/skill-map.md`：任务类型到技能组合的路由表。
- `skills/semiconductor-ai-chain-investment-researcher/`：AI/半导体细分环节深研、海外寡头和 A 股硬证据映射主技能。
- `skills/ai-chain-research-orchestrator/`：AI 产业链实时消息、Grok/X 线索、Gemini 辅助证据和股票映射协调技能。
- `skills/browser-grok-gemini-research/`：网页 Grok/Gemini 采集辅助技能，只负责浏览器采集和结果交接。
- `skills/search-specialist/`：公告、年报、官网、客户/供应商证据、PDF 和反证材料的检索设计。
- `skills/research-summarizer/`：研报、白皮书、公告、会议纪要、PDF 和多来源材料的结构化消化。
- `artifacts/`：研究过程材料、证据包、公司跟踪、周度跟踪和专题输出。
- `watchlists/`：观察池、跟踪名单和后续维护表。
- `docs/`：项目说明、父任务或专题研究文档。
- `scripts/`：项目辅助脚本。不要把临时抓取、浏览器缓存或外部自动化默认写进这里。

## 默认工作流

1. 先读 `skills/industry-research-router`，判断任务属于产业链拆解、公司对比、技术壁垒、国产替代、基本面排序、交易弹性排序、资料检索、长材料消化或表格整理。
2. 当技能选择不明确时，读 `skills/industry-research-router/references/skill-map.md`，只选最小必要技能组合。
3. 如果涉及最新价格、市值、PE/PB、换手率、涨跌幅、财报、订单、政策、监管、公司公告或实时新闻，必须联网或使用本地行情工具核对。
4. 如果只是非实时、非消息驱动的产业链学习或公司对比，不默认打开 Grok/Gemini；先走本地技能框架和必要的公开资料核对。
5. 输出时先给结论，再说明证据、排序、风险和后续跟踪指标。

## 常用技能组合

- AI/半导体产业链本质和 A 股映射：`industry-research-router` + `semiconductor-ai-chain-investment-researcher` + `deep-research`。
- AI 产业链最近 24/48/72 小时消息、爆料、涨价、短缺或停产：`industry-research-router` + `ai-chain-research-orchestrator` + `browser-grok-gemini-research` + `semiconductor-ai-chain-investment-researcher` + `allstock-data`。
- 非半导体产业链本质：`industry-research-router` + `deep-research`，必要时加 `20-andruia-niche-intelligence`。
- 成长行业瓶颈、BOM、交货时滞、HHI、定价权和利润池迁移：`industry-research-router` + `industry-chain-deep-disassembly`。
- 龙头/竞争格局/真假受益：`industry-research-router` + `competitive-landscape` + `competitive-intel`。
- 公司基本面和估值：`industry-research-router` + `stock-evaluator` + `business-analyst` + 市场数据技能。
- 股票弹性和短线催化：`industry-research-router` + `allstock-data` + `banana-farmer` + `advanced-evaluation`。
- 官方资料、公告、PDF、客户/供应商证据和来源反证：`industry-research-router` + `search-specialist` + `web-scraper` / `firecrawl-scraper` / `tavily-web`。
- 研报、白皮书、会议纪要和多来源材料消化：`industry-research-router` + `research-summarizer` + `advanced-evaluation`。
- 红利低波、股息率溢价和股债性价比：`industry-research-router` + `dividend-premium-tracker` + `stock-evaluator` + 市场数据技能。
- 表格、评分卡、watchlist 或 Excel 模型：`industry-research-router` + `spreadsheet` + `xlsx-official` + `advanced-evaluation`。

## Grok/Gemini 使用边界

- Grok/X 是实时消息、爆料、社交热度和 X/Twitter 线索的优先发现层，适合最近 24/48/72 小时的 AI 产业链突发变化。
- Gemini 网页端是补充证据层：用户明确要求、需要 Gemini web Deep Research、需要官方/媒体链接、Grok 线索冲突或需要反证时再调用。
- 网页端 Grok/Gemini 默认走已登录 Chrome 账号路径；除非用户明确指定 `@浏览器` / Browser Use，或 Chrome 不可用且用户接受 fallback，不默认切到内置浏览器。
- Grok、X、Gemini 和其他网页模型只作为信息采集工具；不得把它们的投资结论、排名、目标价或因果解释直接作为本项目结论。
- Playwright 只作为诊断或脚本化 fallback；除非连接的是同一个已登录 Chrome 上下文，不能把结果当成默认 Chrome 会员账号结果。

## 输出要求

默认结论先行。涉及排序时，至少拆成三层：

- 基本面质量排名：业务质量、壁垒、客户质量、盈利结构、长期竞争力。
- 业绩弹性排名：收入增长、毛利率改善、产能利用率、订单转换、经营杠杆。
- 交易弹性排名：流通市值、成交额、换手率、波动率、技术位置、催化密度、预期差和拥挤度。

还需要给出：

- 最大风险点。
- 证据强弱和缺口。
- 后续跟踪指标。
- 需要刷新行情或公告时，明确数据时间和来源状态。

## 项目边界

- 本项目不是 `每日战报_浏览器自动化`，默认不创建 cron、heartbeat、邮件发送、批量报告守护脚本或自动化流水线产物。
- `finance-news`、`stock-copilot-pro` 等带简报或定时任务语义的技能，只作为可选数据/新闻工具，不进入默认投研路由。
- 如果用户明确要求自动化、定时报送、日报、邮件或浏览器批量采集，再单独讨论是否接入相应项目或工具。
- 对代码、脚本和文档做实质修改后，先报告变更并等待确认；确认后再执行提交和推送备份。

## 示例请求

```text
在 D:\vcp_hunter\产业链投研 这个项目里，用产业链与公司研究路由，研究 CPO 光模块产业链。
```

```text
最近 48 小时有没有 AI 产业链涨价、供应短缺或停产爆料？按证据强弱映射到 A 股。
```

```text
谁是真龙头，谁是蹭概念？请分基本面质量、业绩弹性、交易弹性三张表。
```

```text
帮我找这家公司最新年报、公告和客户证据，并把证据分层。
```
