# 产业链投研

Last verified: 2026-07-27

这是一个面向产业链、公司、全球龙头、技术壁垒、国产替代、基本面与交易弹性研究的 Codex 本地工作区。研究主线是：

```text
当前证据 -> 终端需求与产业节点 -> 公司真实暴露 -> 基本面/业绩/交易弹性 -> 风险与跟踪
```

## 技能架构

项目技能位于 Codex 标准仓库路径 `.agents/skills/`，自动发现。项目保留 11 个具有独立研究问题、证据合同或确定性脚本的工作流：

| Skill | 用途 |
|---|---|
| `research-listed-company` | 上市公司生意、护城河、管理层、资本配置、预期、估值与最强反方 |
| `research-industry-chain` | 产业链、BOM、真实供需瓶颈、未来约束迁移和可选公司映射 |
| `income-investment` | 分红/配息覆盖、行业专用指标、减配情景、税币种与收益陷阱 |
| `user-investment-discipline` | 市场周期、过热、追涨、扩仓和加杠杆时的用户纪律 |
| `financial-evidence-audit` | 决策关键数字的来源、口径、单位、派生关系与准出审计 |
| `ai-chain-research-orchestrator` | 最近 AI 产业链消息、Grok/X、Gemini 与原始来源核验 |
| `a-share-company-tracking` | A 股 watchlist、baseline/state/events、日报和完成对账 |
| `a-share-disclosure-trading-data` | CNINFO、交易所、IR、龙虎榜、大宗交易和 T/T+1 公告窗口 |
| `a-share-leverage-capitulation-analyst` | 两融去杠杆、市场压力、拥挤与顶部/见底证据 |
| `earnings-call-investment-analyst` | 财报、指引、电话会、前季比较、需求与瓶颈抽取 |
| `ht-local-market-data` | 只读检查 `D:\HT` 盘后本地行情文件 |

普通文档、Excel、PDF、PPT、搜索、行情、金融数据和统计任务直接使用当前会话已安装的全局技能、插件或原生工具，不在仓库重复 vendoring。

## 使用原则

- 简单问题直接回答；复杂投研只选与问题匹配的一个领域技能，必要时再附加一个数据、文件或状态技能；命中决策关键数字时额外通过 `financial-evidence-audit` 准出，不设宽泛总入口。
- 上市公司、产业链、收益型投资和市场周期纪律各自独立；不要把一类问题的结论规则复制到另一类。
- 决策关键计算必须通过 `financial-evidence-audit`；缺少官方值、存在未解决冲突或口径不一致时标记阻断或 provisional。
- 最新价格、市值、估值、财报、订单、公告、政策和新闻必须当前核验。
- 官方披露优先；行情、概念、社交和模型输出不能单独证明真实受益。
- 产业链研究从终端需求和节点出发；瓶颈必须有“需求超过合格供给”的证据。
- 只有涉及选股或排序时才强制拆分基本面质量、业绩弹性和交易弹性。
- 外部账户、watchlist、模拟交易、自动化和消息发送需要明确授权。
- 自动化的最终结果、运行摘要、告警和失败原因统一使用中文，必要的 ticker、代码、URL、字段名与英文枚举除外。

## 主要目录

- `.agents/skills/`：项目专属技能及按需 references/scripts。
- `.agents/plugins/`：项目本地插件市场配置。
- `plugins/document-skills/`：项目维护的文档技能插件源码；不是根级重复技能入口。
- `artifacts/`：研究证据、公司跟踪和专题输出。
- `watchlists/`：观察池和持续跟踪名单。
- `docs/`：自动化合同、证据规范和专题说明。
- `scripts/`：确定性项目辅助脚本。
- `SKILL_PACK_MANIFEST.md`：精简后的技能清单和迁移边界。
- `THIRD_PARTY_NOTICES.md`：上游方法改写的版本归属与许可证全文。

## 健康检查

```powershell
python scripts\repo_health_check.py --skip-slow
```

完整检查会额外运行 earnings-parent dry-run：

```powershell
python scripts\repo_health_check.py
```

修改后先报告并等待用户测试确认；确认后再提交和推送。
