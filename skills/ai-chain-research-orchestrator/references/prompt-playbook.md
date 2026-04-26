# Prompt Playbook

Use these prompts as starting points. Replace bracketed fields before sending.

## Generic Evidence Collection

Use this for Grok, Gemini, Perplexity, or similar assistant/search products when the task is evidence collection. Do not ask these tools to rank stocks, make investment calls, or explain what the event means.

```text
You are an evidence collection tool, not an analyst.

Topic: [topic]
Time range: [time range]
Market/industry scope: [scope]

Collect objective, source-backed information only.

Rules:
- Do not provide investment advice, rankings, forecasts, target prices, conclusions, causal explanations, or "what it means" analysis.
- Do not infer beyond the source text.
- Prefer primary sources: company releases, exchange filings, regulator notices, official datasets, conference transcripts, direct posts, and original media reports.
- For social posts or rumors, mark them as unverified unless backed by a primary source or multiple independent sources.
- If you mention a claim, include the source link. If no source link is available, say "no source link".
- Keep model-generated summaries separate from source facts.

Return only this table:
| source_type | date_time | entity/company | original_source_or_author | factual_item | numbers_or_terms | source_url | verification_status |

After the table, add a short "source gaps" list only if important evidence is missing.
```

## Grok/X Discovery

```text
这是实时新闻/爆料任务，必须优先使用 Grok 的 X 原生搜索能力；不要只用普通网页搜索替代。

请优先使用当前网页中可用的最强 Grok 模型和最强搜索/研究/专家模式；如果模型名或模式名不确定，请选择看起来能力最高、最适合深度搜索的会员可用选项。

请用你的实时搜索能力和 X/网页公开信息，收集最近 [24/48/72] 小时 [AI产业链/具体赛道] 的新增消息、爆料和可交易线索。

时间范围：[YYYY-MM-DD HH:mm] 至 [YYYY-MM-DD HH:mm]，时区：[北京时间/美东/当地时区]。

搜索语言规则：
- 必须多语言搜索；不要只用中文关键词。
- 优先非中文搜索，再用中文做A股映射和本地市场补充。
- 默认顺序：英文 -> 日文 -> 韩文 -> 繁体中文 -> 简体中文。
- 每个核心环节至少尝试英文关键词；涉及日本材料/设备时加日文，涉及HBM/存储时加韩文，涉及台系PCB/ABF/CoWoS/ODM时加繁中。
- 记录原始语言来源，不要把机器翻译后的中文当作原始证据。

范围：
1. 全球主线公司：[NVIDIA, AMD, Broadcom, Marvell, TSMC, SK hynix, Micron, Samsung, Microsoft, Google, Amazon, Meta, Oracle, OpenAI, xAI 等，按任务删减]
2. 产业链环节：[GPU/ASIC, HBM, CoWoS/SoIC, ABF, PCB/CCL, electronic cloth, copper foil, resin, optical modules, silicon photonics, CPO/OCS, liquid cooling, power, connectors, server ODM, switches, data-center power]
3. 中国映射：A股、港股、台股、美股中真正有订单、客户验证、产能紧缺、价格上涨或技术壁垒的公司，过滤纯概念股。

输出要求：
- 只保留新增变量，不重复旧闻。
- 每条必须给发布时间、来源链接或账号、信息类型。
- 证据等级：A=官方/公告/财报/交易所；B=可信媒体/供应链媒体/券商；C= X爆料/论坛/未经证实传闻。
- C级必须标注待核实，不得写成事实。
- 表格字段：消息 | 时间 | 来源 | 证据等级 | 产业链环节 | 受益/受压公司 | A股/港美台映射 | 为什么重要 | 下一步核验。
请用中文回答。
```

## Grok/X Rumor-Only Pass

```text
这是爆料/传闻任务，必须优先使用 Grok 的 X 原生搜索能力；没有 X 链接或账号的传闻不要列为有效线索。

请优先使用当前网页中可用的最强 Grok 模型和最强搜索/研究/专家模式；重点利用 X 原生搜索能力。

继续补充一轮：只查最近 [24/48/72] 小时内 X 平台、供应链论坛、券商路演纪要中关于 [赛道] 的爆料/传闻/未完全证实信息。不要重复硬新闻。

重点找：[采购、订单、停产、涨价、良率、认证、量产、客户导入、扩产、取消订单、延期]。

搜索语言规则：
- 优先英文、日文、韩文、繁体中文；最后再用简体中文补充。
- 针对同一关键词必须尝试不同语言写法，例如：HBM / HBM4 / 高帯域メモリ / 고대역폭 메모리；CoWoS / 先進封裝 / 先端パッケージ；optical module / 光トランシーバ / 光模組。
- 表格中保留原始来源语言。

输出只要中文表格：
爆料内容 | 发布时间 | 来源链接/账号 | 来源语言 | 可信度C1-C3 | 涉及环节 | 可能映射标的 | 为什么值得跟踪 | 如何验证 | 如何证伪

严格要求：没有链接或账号的不列；明显旧闻不列；无法确认必须写“待核实”。
```

## Perplexity Source Search

Use this after Grok/X discovery and before Codex final verification. Perplexity is a source finder, not the final analyst.

```text
You are a source-discovery tool, not an investment analyst.

Topic: [topic]
Time range: [YYYY-MM-DD HH:mm to YYYY-MM-DD HH:mm, timezone]
Scope: [industry segment / market / companies]

Task:
Collect web-source-backed information that can verify, refute, or add context to the Grok/X leads below.

Rules:
- Do not provide investment advice, rankings, target prices, trading conclusions, or causal interpretation.
- Do not infer beyond the source text.
- Prefer primary sources: company releases, IR pages, exchange filings, regulator notices, earnings call transcripts, official datasets, and direct media reports.
- Include source URLs for every factual item. If no source URL is available, write "no source link".
- Mark X posts, forum posts, screenshots, and unsourced market chatter as unverified unless backed by primary sources or multiple independent reputable sources.
- Separate model-generated summaries from source facts.
- Use English or original market language for global AI, semiconductor, datacenter, and supply-chain topics unless the task is China-local.

Grok/X leads to check:
[paste lead table]

Return only this table:
| source_type | date_time | entity/company | original_source_or_author | factual_item | numbers_or_terms | source_url | verification_status |

After the table, add a short "source gaps" list only if important evidence is missing.
```

## Optional Gemini Verification And Counter-Evidence

Use this only when quick Grok/X discovery plus Codex web verification leaves a major unresolved or conflicting line.

```text
请优先使用当前网页中可用的最强 Gemini 模型和最强 Deep Research / web-grounded / 长上下文模式。

请对下面这些 AI产业链线索做核验和反证，不要直接相信原结论。

任务：
1. 为每条线索寻找官方公告、财报、交易所披露、公司IR、可信媒体或产业媒体来源。
2. 判断是否为最近 [24/48/72] 小时新增变量，还是旧闻重复。
3. 找反证：公司是否否认、订单是否无法验证、数据是否来自二手转述、是否有时间错配。
4. 给证据等级 A/B/C，并说明为什么。
5. 输出每条线索的“可用结论”和“不能下的结论”。

线索：
[粘贴Grok/X/Codex收集到的候选表]

输出字段：
线索 | 核验结果 | 最强来源链接 | 反证/疑点 | 证据等级 | 可用结论 | 不可用结论 | 下一步验证
```

## Codex Synthesis Checklist

Before finalizing, check:

- Did every current fact that can change use web or local market-data verification?
- Are source links attached to hard claims?
- Are C-level rumors separated from conclusions?
- Are A-share/HK/US/Taiwan tickers normalized?
- Are fundamental quality, earnings elasticity, and trading elasticity ranked separately?
- Are "true leader" names separated from concept followers?
- Are follow-up indicators concrete enough to monitor?

## Default Table

```text
Claim | Time | Source | Grade | Chain segment | Beneficiaries | Pressured names | Stock mapping | Elasticity | Risk | Next verification
```
