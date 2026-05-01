# 产业链投研

这是一个专门用于产业链和公司研究的 Codex 技能包项目，核心目标是把产业链拆解、公司基本面、海外龙头、技术壁垒、国产替代、A 股映射和交易弹性放在同一个可复用研究框架里。

## 目录

- `skills/`：项目内精选研究技能副本。
- `skills/industry-research-router/`：产业链与公司研究的入口路由技能。
- `skills/ai-chain-research-orchestrator/`：AI 产业链实时消息、Grok/X 线索、Gemini 辅助证据、Codex 复核和股票映射协调技能。
- `skills/browser-grok-gemini-research/`：网页 Grok/Gemini 采集辅助技能，只负责浏览器采集边界，不负责投资结论。
- `skills/semiconductor-ai-chain-investment-researcher/`：AI/半导体细分环节深研、海外寡头、A 股硬实力映射和环节内横向比较主技能。
- `skills/search-specialist/`：公告、年报、官网、客户/供应商证据和反证材料的检索设计技能。
- `skills/research-summarizer/`：研报、白皮书、公告、PDF 和多来源材料的结构化消化技能。
- `skills/dividend-premium-tracker/`：红利低波和股息率溢价的风格辅助技能，不替代个股研究。
- `skills/industry-research-router/references/skill-map.md`：研究技能组合清单。
- `AGENTS.md`：本项目的默认研究规则。

## 建议用法

新开对话时可直接说：

```text
在 D:\vcp_hunter\产业链投研 这个项目里，用产业链与公司研究路由，研究 XXX 赛道/公司。
```

也可以直接问：

```text
这个产业链怎么拆？
谁是真龙头，谁是蹭概念？
这几家公司谁的股票弹性最大？
国产替代里谁最有机会？
最近48小时有没有 AI 产业链涨价、供应短缺或停产爆料？
帮我找这家公司最新年报、公告和客户证据，并把证据分层。
红利低波现在还有没有股债性价比？
```

系统应优先使用 `industry-research-router`，再根据任务选择行情、财务、竞争格局、深度研究、表格和网页证据技能。AI/半导体产业链任务如果是结构性研究，先用 `semiconductor-ai-chain-investment-researcher` 做从上至下的环节深研和 A 股映射；如果涉及实时消息、爆料、Grok/X 或 Gemini，再用 `ai-chain-research-orchestrator` 和 `browser-grok-gemini-research` 做采集和证据分层。需要找资料时先用 `search-specialist` 规划检索，材料较长时用 `research-summarizer` 消化后再进入投研判断。

本项目不默认承接每日战报、cron、邮件投递或浏览器批量自动化。需要这类能力时，应明确转入相应自动化项目或另行配置。
