# Global Codex Rules

## Response Language

- Always reply in Chinese, regardless of the language used in the user's input.
- Keep non-Chinese text only when it is required for code, commands, filenames, APIs, exact quotes, or user-requested artifacts.

## Skills First

- Before every answer or task execution, inspect the available skill library and choose the appropriate skill or skill combination.
- If a task clearly matches a skill, read the relevant `SKILL.md` and follow it before answering or editing files.
- For local skill routing, first consult `C:\Users\Administrator\.codex\skill-routing\README.md` and `C:\Users\Administrator\.codex\skill-routing\ROUTER.md`; use `skill-inventory.csv` or `skill-inventory.json` for keyword search across the full installed library.
- Also consult `C:\Users\Administrator\.codex\skill-routing\SKILL_HEALTH.md` and `skill-health-overrides.json`: do not route to quarantined skills unless explicitly restored, and treat `reference-only` skills as guidance only rather than executable automation.

## Dependency Policy

- Download missing dependencies directly as needed; do not use mirror sources.

## Code Editing Hygiene

- When modifying code, preserve the original formatting, structure, and encoding whenever possible.
- Be especially careful with Chinese text, comments, paths, and documentation. Do not introduce mojibake or rewrite files in a way that corrupts non-ASCII content.
- Keep edits focused on the requested task and avoid unrelated rewrites.
- After changes, clean obsolete code, temporary files, generated clutter, and old unused files when it is safe and relevant.

## Report Before Backup

- After any substantive code change, addition, or fix, do not immediately archive, commit, or push.
- First report what changed and wait for the user's test confirmation.
- Treat explicit approval phrases meaning "no problem", "done", "ready", "looks good", "ok", or "can proceed" as approval to perform the backup flow immediately.

## Confirmed Backup Flow

- Once the user confirms, automatically run the backup from the terminal without requiring another reminder.
- Use the current project branch and its upstream branch. Do not create, switch to, or push extra `backup/*` or `codex/*` backup branches unless the user explicitly asks for that.
- Before staging, run `git status --short` and avoid sweeping in unrelated changes blindly.
- Then run:
  1. `git add .`
  2. `git commit -m "type: description"`
  3. `git push`
- The backup must reach the cloud remote `origin`; do not stop at a local `.git` commit.
- If the current project has no `origin` remote or no upstream branch, inspect and configure or confirm the correct GitHub private repository before backing up.
- After the commit and push succeed, report a brief summary of the commit and push result.

## Behavioral Guidelines

### Think Before Coding

- State assumptions explicitly when they matter.
- If multiple interpretations exist, present them instead of picking silently.
- If a simpler approach exists, say so.
- If something is unclear and cannot be safely inferred, stop and ask.

### Simplicity First

- Use the minimum code or documentation change that solves the problem.
- Do not add speculative features, abstractions, or configurability.
- Do not add error handling for impossible scenarios.
- If a change grows much larger than necessary, simplify before finishing.

### Surgical Changes

- Touch only what the request requires.
- Do not improve adjacent code, comments, or formatting unless the task needs it.
- Match existing style unless that style is the thing being repaired.
- Remove imports, variables, functions, or files that your own changes made obsolete.
- Mention unrelated dead code instead of deleting it unless asked.

### Goal-Driven Execution

- Define success criteria before substantial work.
- Verify fixes with the closest practical check.
- For multi-step tasks, keep a brief plan and update it as work completes.

---

# Project Doc

## Current Primary Investment-Research Entrypoint

- For any investment research task in this repository, start with `skills/user-investment-framework`.
- Treat `skills/industry-research-router` and all other project skills as companion skills selected by `user-investment-framework`, not as competing first entrypoints.
- Use `skills/ht-local-market-data` only as a read-only local `D:\HT` HT/TongdaXin market-data layer for post-close daily K-lines, block pools, vendor tables, and freshness checks; it is not official evidence and must not inspect trading-account/password/order/log details unless explicitly requested.
- For news-driven alpha, small-cap elasticity, market misclassification, or news-to-financial-statement translation, use `skills/serenity-alpha` only after source and evidence collection, then validate with market data and the framework's final ranking layer.
- Treat Public Equity Investing plugin skills as companion PM workflow layers only. Use them for thesis trackers, catalyst calendars, dated event underwriting, earnings preview/deep-dive, scenario sensitivity, position risk, model update/audit, and formal memo/pitch/tearsheet packaging after the project framework has established source evidence, chain position, downstream demand, and issuer/security context.
- Do not route generic industry-chain, company, valuation, or share-price questions directly into the Public Equity Investing plugin router. It does not replace upstream/downstream mapping, official evidence, beneficiary proof, core-product unit-economics checks, or the final fundamental-quality / earnings-elasticity / trading-elasticity ranking.

## 项目定位

本项目用于产业链研究、公司研究、全球龙头梳理、技术壁垒分析、国产替代研究、股票基本面比较和交易弹性判断。

## 默认研究路由

- 新对话或新任务先使用 `skills/user-investment-framework` 作为主入口，再按问题类型选择最小必要 companion skills。
- `skills/industry-research-router` 是兼容和细分路由层，只在主框架选择后辅助分类。
- AI/半导体产业链任务需要实时消息、爆料、Grok/X、Gemini 或网页证据时，先用 `skills/ai-chain-research-orchestrator` 协调证据；需要网页登录采集时再用 `skills/browser-grok-gemini-research`；之后用 `skills/semiconductor-ai-chain-investment-researcher` 做细分环节深研和 A 股硬证据映射。
- 非实时、非消息驱动的产业链学习或公司对比，不默认调用网页 Grok/Gemini；先用本地 skill 框架和必要公开资料核对。
- 需要官方资料、公告、年报、PDF、客户/供应商证据或多来源反证时，先用 `skills/search-specialist` 设计检索与证据优先级，再用网页/抓取技能获取材料；长文、研报、白皮书和多来源材料用 `skills/research-summarizer` 先结构化消化。
- A 股公司持续跟踪、watchlist 日更、baseline/state/events 维护时，用 `skills/a-share-company-tracking`；涉及公告、CNINFO、交易所披露、龙虎榜、大宗交易或 20:00 后 T/T+1 公告窗口时，加 `skills/a-share-disclosure-trading-data`。
- 红利、低波、股息率溢价、股债性价比和防御风格问题可加 `skills/dividend-premium-tracker`，但它只提供风格和宏观背景，不替代个股基本面判断。
- 当技能选择不明确时，先读 `skills/user-investment-framework/references/project-skill-integration.md` 和 `skills/user-investment-framework/references/skill-mcp-boundary-matrix.md`；需要兼容旧路由时，再读 `skills/industry-research-router/references/skill-map.md`。

## 网页 Grok/Gemini 原则

- Grok/Gemini 网页端默认使用 `@chrome` / Chrome 插件，因为用户的 Grok 与 Gemini 账号在 Chrome 中保持登录。
- 除非用户明确指定 `@浏览器` / Browser Use，或 Chrome 不可用且用户接受 fallback，不默认切换到内置浏览器。
- Playwright 只作为诊断或脚本化 fallback；除非能连接同一个已登录 Chrome 上下文，不能把 Playwright 结果当成默认 Chrome 会员账号结果。
- Grok/X 是实时消息、爆料、社交热度和 X/Twitter 线索的优先发现层，尤其适合最近 24/48/72 小时的 AI 产业链突发变化。
- Gemini 网页端是补充证据层：用户明确要求、需要 Gemini web Deep Research、需要找官方/媒体链接、Grok 线索冲突、或需要反证时再调用。
- Grok、X、Gemini 以及其他网页模型只作为信息采集工具；Codex 必须负责核验、证据分级、产业链映射、股票筛选和最终结论。
- 不把网页模型的投资结论、排名、目标价、因果解释直接作为本项目结论。

## 项目边界

- 本项目不是 `每日战报_浏览器自动化`，默认不创建 cron、heartbeat、邮件发送、批量报告守护脚本或自动化流水线产物。
- 如用户明确要求自动化、定时报送、日报、邮件或浏览器批量采集，再单独讨论是否接入相应项目或工具。
- `finance-news`、`stock-copilot-pro` 等带简报、行动建议或定时任务语义的 skill 在本项目中只作为 explicit-only / reference-only 工具，不进入默认投研路由，不自动创建 cron、简报、推送或行动建议。

## 研究原则

- 先判断问题类型：产业链拆解、公司对比、技术壁垒、国产替代、基本面排序、交易弹性排序、数据表整理。
- 行业研究必须区分：产业链位置、价值量、技术壁垒、客户验证周期、国产替代难度、全球龙头。
- 股票研究必须区分：基本面质量、业绩弹性、交易弹性。不要把“公司好”直接等同于“股价弹性最大”。
- 涉及最新价格、市值、PE/PB、换手率、涨跌幅、财报、订单、政策、监管和公司公告时，必须联网或用本地行情工具核对。
- 优先引用官方公告、交易所披露、公司年报/季报、招股书和可信财经数据源。
- 对 A 股、港股、美股、日股、韩股、台股要明确交易所和 ticker 后缀，避免混淆上市主体。

## 常用技能组合

- AI/半导体产业链本质和 A 股映射：`user-investment-framework` + `semiconductor-ai-chain-investment-researcher` + `deep-research`；如涉及实时消息或爆料，加 `ai-chain-research-orchestrator` 和 `browser-grok-gemini-research`。
- 非半导体产业链本质：`user-investment-framework` + `industry-chain-deep-disassembly` + `deep-research`。
- 龙头/竞争格局：`user-investment-framework` + `competitive-landscape` + `competitive-intel`。
- 公司基本面：`user-investment-framework` + `stock-fundamental-moat-triad` + `stock-evaluator` + `business-analyst`。
- 股票弹性：`user-investment-framework` + `allstock-data` / `tdx-finance-data` + `banana-farmer` + `advanced-evaluation`。
- A 股公司持续跟踪：`user-investment-framework` + `a-share-company-tracking` + `a-share-disclosure-trading-data` + `search-specialist` + `research-summarizer`。
- 官方资料/公告/PDF/来源反证：`user-investment-framework` + `search-specialist` + `firecrawl-scraper` / `tavily-web` / 全局 `web-scraper`；材料较长时加 `research-summarizer`。
- 研报/白皮书/多来源消化：`user-investment-framework` + `research-summarizer` + `advanced-evaluation`。
- 红利低波/股息率溢价：`user-investment-framework` + `dividend-premium-tracker` + `stock-evaluator` + 市场数据 skill。
- 海外寡头：`user-investment-framework` + `finance` + `alpha-vantage` + iFinD global stock MCP + 官方披露/IR。
- 表格打分：`user-investment-framework` + `spreadsheet` + `xlsx-official` + `advanced-evaluation`。
- 公告/网页抓取：`user-investment-framework` + `search-specialist` + `firecrawl-scraper` + `tavily-web` / 全局 `web-scraper`。

## 输出要求

默认结论先行。涉及排序时，至少给出：

- 基本面质量排名
- 业绩弹性排名
- 交易弹性排名
- 最大风险点
- 后续跟踪指标
