---
name: user-investment-framework
description: Evidence-first investment research for industry chains, companies, listed securities, valuation, filings, market data, beneficiary checks, and stock comparisons in the 产业链投研 project. Use for 产业链研究、公司研究、个股研究、上下游、技术壁垒、国产替代、全球龙头、估值、基本面、业绩弹性、交易弹性或真假受益判断. Do not use for unrelated engineering or general writing tasks.
---

# User Investment Framework

把本技能作为项目投研任务的轻量决策框架。先判断能否直接回答；只有任务确实需要项目专属流程、实时数据或文件操作时，才加载叶子技能。

## 执行原则

- 简单、常识性或非实时问题直接回答，不为展示流程而追加技能。
- 默认最多选择 1 个领域技能和 1 个数据、文件或状态技能；确有独立脆弱流程时才增加。
- 不加载兼容路由、固定技能栈或仅重复通用推理清单的技能。
- 把技能当作方法和工具边界，不把技能输出当作证据。

## 硬边界

1. 最新价格、估值、财报、订单、公告、政策、监管、管理层和市场状态必须实时核验，并说明数据时间。
2. 官方公告、交易所文件、公司 IR、财报、招股书及官方客户/供应商材料才可支撑硬事实；行情厂商、概念标签、媒体、社交和模型输出按来源等级使用。
3. 行情、K 线、龙虎榜、概念热度和股价反应只能说明交易结构，不能证明业务暴露、客户、订单或收入受益。
4. 先确认上市主体、市场和 ticker，再比较公司；跨市场时说明口径差异。
5. 账户、外部 watchlist、模拟交易、自动化、消息发送或其他外部写入必须有用户明确授权；不得泄露密钥、账户、密码、订单或无关日志。
6. 缺少可靠数据时写 `N/A`、证据缺口和置信度，不用记忆补精确数字。

## 研究启发式

- 从终端需求和产业链节点出发，说明“需求如何传到公司的量、价、份额、利用率或利润率”。
- 只把“需求超过合格供给、可用产能、良率或交付能力”的节点称为瓶颈；高壁垒、高 HHI、高毛利或热门概念本身不是瓶颈。
- 公司映射至少核对准确产品、客户/认证/订单证据、收入或利润重要性，以及反转条件。
- 盈利逻辑依赖价格或单位经济时，分开检查销量、ASP/ARPU/take rate、成本、产品结构和持续性。
- 只有用户要求选股、排序或交易判断时，才强制分开基本面质量、业绩弹性和交易弹性。

复杂任务的详细检查表见 [references/research-method.md](references/research-method.md)。

## 叶子技能

按任务选择，不要预加载：

| 任务 | 项目技能 |
|---|---|
| 产业链、BOM、供需瓶颈、AI/半导体节点 | `research-industry-chain` |
| 最近 AI 产业链消息、Grok/X、Gemini、传闻核验 | `ai-chain-research-orchestrator` |
| A 股 watchlist、baseline/state/events 日常维护 | `a-share-company-tracking` |
| CNINFO、交易所公告、IR、龙虎榜、大宗交易 | `a-share-disclosure-trading-data` |
| 财报、指引、电话会、前后季度对比 | `earnings-call-investment-analyst` |
| 本地 `D:\HT` 盘后行情文件 | `ht-local-market-data` |

文档、表格、通用搜索、网页、行情和金融数据优先使用当前会话已安装的全局技能、插件或原生工具，不在项目内维护重复副本。选择外部工具前按需读 [references/tool-boundaries.md](references/tool-boundaries.md)；使用 TDX 时再读 [references/tdx-finance-data-boundary.md](references/tdx-finance-data-boundary.md)；AI 节点映射时再读 [references/ai-chain-node-taxonomy.md](references/ai-chain-node-taxonomy.md)。

## 输出

先给结论，再给足以支撑结论的证据、关键假设、最大风险和跟踪指标。涉及股票排序时分别输出基本面质量、业绩弹性、交易弹性；快速问题不强行生成大表或完整报告。
