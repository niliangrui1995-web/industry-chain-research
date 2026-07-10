# 产业链投研

Last verified: 2026-07-10

这是一个面向产业链、公司、全球龙头、技术壁垒、国产替代、基本面与交易弹性研究的 Codex 本地工作区。研究主线是：

```text
当前证据 -> 终端需求与产业节点 -> 公司真实暴露 -> 基本面/业绩/交易弹性 -> 风险与跟踪
```

## 技能架构

项目技能已迁到 Codex 标准仓库路径 `.agents/skills/`，自动发现。项目只保留无法由全局技能或插件替代的 7 个工作流：

| Skill | 用途 |
|---|---|
| `user-investment-framework` | 轻量投研框架、证据硬门和最小技能选择 |
| `research-industry-chain` | 产业链、BOM、真实供需瓶颈、未来约束迁移和可选公司映射 |
| `ai-chain-research-orchestrator` | 最近 AI 产业链消息、Grok/X、Gemini 与原始来源核验 |
| `a-share-company-tracking` | A 股 watchlist、baseline/state/events、日报和完成对账 |
| `a-share-disclosure-trading-data` | CNINFO、交易所、IR、龙虎榜、大宗交易和 T/T+1 公告窗口 |
| `earnings-call-investment-analyst` | 财报、指引、电话会、前季比较、需求与瓶颈抽取 |
| `ht-local-market-data` | 只读检查 `C:\zd_huatai` 盘后本地行情文件 |

普通文档、Excel、PDF、PPT、搜索、行情、金融数据和统计任务直接使用当前会话已安装的全局技能、插件或原生工具，不在仓库重复 vendoring。

## 使用原则

- 简单问题直接回答；复杂投研先用 `user-investment-framework`，通常再选 0-1 个领域技能和 0-1 个数据/产物技能。
- 最新价格、市值、估值、财报、订单、公告、政策和新闻必须当前核验。
- 官方披露优先；行情、概念、社交和模型输出不能单独证明真实受益。
- 产业链研究从终端需求和节点出发；瓶颈必须有“需求超过合格供给”的证据。
- 只有涉及选股或排序时才强制拆分基本面质量、业绩弹性和交易弹性。
- 外部账户、watchlist、模拟交易、自动化和消息发送需要明确授权。

## 主要目录

- `.agents/skills/`：项目专属技能及按需 references/scripts。
- `.agents/plugins/`：项目本地插件市场配置。
- `plugins/document-skills/`：项目维护的文档技能插件源码；不是根级重复技能入口。
- `artifacts/`：研究证据、公司跟踪和专题输出。
- `watchlists/`：观察池和持续跟踪名单。
- `docs/`：自动化合同、证据规范和专题说明。
- `scripts/`：确定性项目辅助脚本。
- `SKILL_PACK_MANIFEST.md`：精简后的技能清单和迁移边界。

## 健康检查

```powershell
python scripts\repo_health_check.py --skip-slow
```

完整检查会额外运行 earnings-parent dry-run：

```powershell
python scripts\repo_health_check.py
```

修改后先报告并等待用户测试确认；确认后再提交和推送。
