# 项目技能清单

项目技能根目录：`.agents/skills/`。清单只记录项目专属能力；全局技能、插件和 MCP 不在仓库复制。

## 活跃技能

| Skill | 触发范围 | 关键边界 |
|---|---|---|
| `user-investment-framework` | 产业链、公司、个股、估值和排序 | 轻量主框架；简单任务直接回答，默认最多 1 个领域 + 1 个数据/产物技能 |
| `research-industry-chain` | 上下游、BOM、堵点、卡点、AI/半导体节点 | 瓶颈必须有合格供给缺口；股票映射放在节点判断之后 |
| `ai-chain-research-orchestrator` | 最近 AI 消息、爆料、Grok/X、Gemini | 采集与核验层；模型输出不直接成为投资证据 |
| `a-share-company-tracking` | watchlist 日更、baseline/state/events | 仅写命名的项目状态文件；逐公司完成并对账 |
| `a-share-disclosure-trading-data` | 公告、CNINFO、IR、龙虎榜、大宗交易 | 官方事实与交易结构分开；执行 T/T+1 晚间窗口 |
| `a-share-leverage-capitulation-analyst` | 大盘压力、两融去杠杆、暴跌共振、抱团拥挤与顶部风险 | 日更与逐股明细均保留 DFCF 厂商边界；见底三因子与顶部研究独立；价格拥挤负责顶部排序，融资流出只作瓦解确认；所有可执行口径从 T+1 起 |
| `earnings-call-investment-analyst` | 财报、指引、电话会、QoQ、需求/瓶颈 | 原始来源优先；完整深挖才加载详细 checklist 和采集脚本 |
| `ht-local-market-data` | 本地 `D:\HT` 日线、板块池、厂商表 | 只读、非官方、非实时；账户/订单/日志默认禁读 |

## 已移出项目技能层

- `industry-research-router`：删除兼容路由，避免主框架与叶子技能回环。
- `semiconductor-ai-chain-investment-researcher`：领域要点并入 `research-industry-chain/references/ai-semiconductor.md`。
- `browser-grok-gemini-research`：浏览器边界并入 `ai-chain-research-orchestrator`。
- 通用公司、搜索、摘要、评分、数据科学、技术、产品、行情、Apify、新闻和表格技能：使用当前已安装的全局技能/插件/原生工具。
- 根级 `docx/pdf/pptx/xlsx` 副本：删除；文档插件源码继续位于 `plugins/document-skills/`，安全测试只覆盖该单一来源。
- `finance-news`、`stock-copilot-pro`：不属于默认投研边界，不保留项目副本。

## 维护规则

- 新 skill 只在项目存在独特真相路径、脆弱流程或确定性脚本时增加。
- 通用知识、普通分析清单和第三方工具说明优先放全局技能、插件或当前工具文档，不复制进仓库。
- `SKILL.md` 保持短入口；字段表、领域变体和快照放一层 references；确定性操作放 scripts。
- 叶子技能不得反向要求 legacy router 或固定技能栈。
- 通过 `scripts/repo_health_check.py` 和 `tests/test_skill_library.py` 检查目录、名称、长度和旧路由残留。
