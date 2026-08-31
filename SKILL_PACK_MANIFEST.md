# 项目技能清单

项目技能根目录：`.agents/skills/`。清单记录项目专属能力及已登记的账户级数据伴侣；全局技能、插件和 MCP 不在仓库复制。

## 活跃技能

| Skill | 触发范围 | 关键边界 |
|---|---|---|
| `research-listed-company` | 上市公司、个股比较、护城河、管理层、预期和估值 | 上游公司研究方法取优，本地官方证据与 point-in-time 门禁覆盖；无组合输入不编造仓位 |
| `research-industry-chain` | 上下游、BOM、堵点、卡点、AI/半导体节点，以及明确点名 Serenity 的候选咽喉命题 | 瓶颈必须有合格供给缺口；Serenity 仅生成 `watch` 候选，股票映射放在节点判断之后 |
| `income-investment` | 股息、配息、分红持续性、REIT/银行/保险/BDC/资源股收入 | 使用行业专用可分配现金口径；税务、币种和组合输入不足时不输出税后收入或动作 |
| `user-investment-discipline` | 市场周期、MA30、双头、过热、追涨、扩仓或杠杆冲动 | 仅执行用户条件纪律；不承担公司、产业链、财报或估值研究 |
| `financial-evidence-audit` | 市值、预期差、估值、覆盖率、单位换算及报告准出 | Decimal 确定性计算；来源冲突、期间/单位/币种不一致时 fail closed |
| `ai-chain-research-orchestrator` | 最近 AI 消息、爆料、Grok/X、Gemini | 采集与核验层；模型输出不直接成为投资证据 |
| `a-share-company-tracking` | watchlist 日更、baseline/state/events | 仅写命名的项目状态文件；逐公司完成并对账 |
| `a-share-disclosure-trading-data` | 公告、CNINFO、IR、龙虎榜、大宗交易 | 官方事实与交易结构分开；执行 T/T+1 晚间窗口 |
| `a-share-leverage-capitulation-analyst` | 大盘压力、两融去杠杆、暴跌共振、抱团拥挤与顶部风险 | 日更与逐股明细均保留 DFCF 厂商边界；见底三因子与顶部研究独立；价格拥挤负责顶部排序，融资流出只作瓦解确认；所有可执行口径从 T+1 起 |
| `earnings-call-investment-analyst` | 财报、指引、电话会、QoQ、需求/瓶颈 | 原始来源优先；完整深挖才加载详细 checklist 和采集脚本 |
| `ht-local-market-data` | 本地 `D:\HT` 日线、板块池、厂商表 | 只读、非官方、非实时；账户/订单/日志默认禁读 |

## 已接入的账户级厂商数据 Skill

| Skill | 触发范围 | 关键边界 |
|---|---|---|
| `hithink-finance` | 用户明确提及同花顺 Financial API，或需 A 股行情、财报、最新估值、指数/板块或基金数据 | 账户级已安装 Skill，不复制入 `.agents/skills/`；厂商数据须标注来源与时点，凭据仅从安全来源读取，决策关键数字仍经 `financial-evidence-audit` |

## 已移出项目技能层

- 旧的宽泛投资总入口：其公司方法、产业链分类、数据边界和用户纪律已分别迁入唯一领域所有者；不保留兼容入口，避免双流程竞争。
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
