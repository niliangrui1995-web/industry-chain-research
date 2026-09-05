# Prompt Playbook

Use these prompts as starting points. Replace bracketed fields before sending. Do not ask Grok, Gemini, or any other web assistant to make the final investment call.

## Generic Evidence Collection

Use this for Gemini or similar assistant/search products when the task is evidence collection. For Grok, prefer the X-only prompt below.

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

Grok is primarily for X/Twitter-native collection. Keep it focused on posts, accounts, repost chains, engagement heat, and sentiment. Use Codex for final verification. Gemini can be added later when source gaps or counter-evidence matter.

```text
这是实时新闻/爆料任务。请优先使用 Grok 的 X 原生搜索能力，重点收集 X/Twitter 上的帖子、账号、转发链、引用链、互动热度和情绪。

默认不要把 Grok 的普通网页搜索、联网搜索或 web-grounded research 当作最终证据。若帖子里有网页来源，请列为“待 Codex 核验的来源线索”。

请优先使用当前网页中可用的最强 Grok 模型和最适合 X 原生搜索/社交情绪收集的会员可用选项；如果模型名或模式名不确定，请选择看起来最适合 X 搜索的选项。

请收集最近 [24/48/72] 小时 [AI产业链/具体赛道] 在 X 上的新增消息、爆料、热度、情绪和可交易线索。

时间范围：[YYYY-MM-DD HH:mm] 至 [YYYY-MM-DD HH:mm]，时区：[北京时间/美东/当地时区]。

搜索语言规则：
- 默认多语言搜索；不要只用中文关键词。
- 优先非中文搜索，再用中文做A股映射和本地市场补充。
- 默认顺序：英文 -> 日文 -> 韩文 -> 繁体中文 -> 简体中文。
- 每个核心环节至少尝试英文关键词；涉及日本材料/设备时加日文，涉及HBM/存储时加韩文，涉及台系PCB/ABF/CoWoS/ODM时加繁中。
- 记录原始语言来源，不要把机器翻译后的中文当作原始证据。

范围：
1. 全球主线公司：[NVIDIA, AMD, Broadcom, Marvell, TSMC, SK hynix, Micron, Samsung, Microsoft, Google, Amazon, Meta, Oracle, OpenAI, xAI 等，按任务删减]
2. 产业链环节：[GPU/ASIC, HBM, CoWoS/SoIC, ABF, PCB/CCL, electronic cloth, copper foil, resin, optical modules, silicon photonics, CPO/OCS, liquid cooling, power, connectors, server ODM, switches, data-center power]
3. 公司线索：记录来源明确提及的 A股、港股、台股、美股公司、产品，以及订单、客户验证、产能、价格或技术相关原文主张；不要自行判定真实受益或补出未具名公司。

输出要求：
- 优先保留新增变量，不重复旧闻；若旧闻正在窗口内被重新定价或发酵，可标成“旧闻再发酵/背景”。
- 每条尽量给发布时间、来源链接或账号、信息类型；没有链接但有明确账号/截图/来源指向的高信号线索可放入 C3 观察池。
- 证据等级：A=官方/公告/财报/交易所；B=可信媒体/供应链媒体/券商；C= X爆料/论坛/未经证实传闻。
- C级必须标注待核实，不得写成事实。
- 默认用表格输出：消息 | 发布时间/事件时间 | 原始作者/来源链接 | 证据等级 | 产业链环节 | 来源提及公司/产品 | 来源原文主张 | 核验状态 | 下一步核验。来源中的受益判断或因果解释须明确归因，不能改写成已验证事实。
- 如果表格会遗漏脉络，可在表格前加 3-5 条“发现摘要”，但不要给投资结论。
请用中文回答。
```

## Grok/X Rumor-Only Pass

Use this when the user asks for 爆料, rumors, market chatter, or weak-but-early supply-chain leads.

```text
这是爆料/传闻任务，请优先使用 Grok 的 X 原生搜索能力；没有 X 链接或账号的传闻原则上不要列为有效线索，但可以把高互动截图/明确转述源放入 C3 观察池并标注“待核实”。

请优先使用当前网页中可用的最强 Grok 模型和最适合 X 原生搜索/社交情绪收集的会员可用选项；重点利用 X 原生搜索能力，不要把 Grok 的普通网页搜索结果当作已验证事实。

继续补充一轮：重点查最近 [24/48/72] 小时内 X 平台、供应链论坛、券商路演纪要中关于 [赛道] 的爆料/传闻/未完全证实信息。尽量不重复硬新闻；若硬新闻引发新的市场解读或供应链二阶反馈，可标为“硬新闻后的社交发酵”。

重点找：[采购、订单、停产、涨价、良率、认证、量产、客户导入、扩产、取消订单、延期]。

搜索语言规则：
- 优先英文、日文、韩文、繁体中文；最后再用简体中文补充。
- 针对同一关键词尽量尝试不同语言写法，例如：HBM / HBM4 / 高帯域メモリ / 고대역폭 메모리；CoWoS / 先進封裝 / 先端パッケージ；optical module / 光トランシーバ / 光模組。
- 表格中保留原始来源语言。

默认输出中文表格：
爆料内容 | 发布时间/事件时间 | 来源链接/账号 | 来源语言 | 可信度C1-C3 | 涉及环节 | 来源提及公司/产品 | 来源原文主张 | 如何验证 | 如何证伪

要求：优先列有链接或账号的线索；明显旧闻一般不列，除非窗口内重新发酵；无法确认必须写“待核实”。
```

## Gemini Source Search And Counter-Evidence

Use this only when Gemini is requested or when it can improve source discovery, counter-evidence, long-context review, or official/media/PDF coverage.

```text
You are a source-discovery tool, not the final investment analyst.

Topic: [topic]
Time range: [YYYY-MM-DD HH:mm to YYYY-MM-DD HH:mm, timezone]
Scope: [industry segment / market / companies]

Task:
Collect open-web, source-backed news items, official releases, reputable media reports, and factual claims for the topic and time range below. If the time window is strict and source-backed items are sparse, include clearly labeled near-window background and source gaps instead of forcing weak matches into the window.

Rules:
- Avoid investment advice, rankings, target prices, trading conclusions, or unsupported causal interpretation.
- Keep factual items anchored to source text; if you add a brief scope note, separate it from source facts.
- Prefer primary sources: company releases, IR pages, exchange filings, regulator notices, earnings call transcripts, official datasets, and direct media reports. Reputable media and supply-chain media are useful when primary sources are not available.
- Include source URLs for factual items whenever possible. If a potentially important item has no usable source URL, keep it in a source-gap or unverified section rather than mixing it with verified facts.
- Mark X posts, forum posts, screenshots, and unsourced market chatter as unverified unless backed by primary sources or multiple independent reputable sources.
- Separate model-generated summaries from source facts.
- Use English or original market language for global AI, semiconductor, datacenter, and supply-chain topics unless the task is China-local. For narrow or fast scans, use the most relevant language set and state any coverage limits.

Optional topic seeds or known leads:
[paste topic seeds, company names, event keywords, or Grok/X lead table if available]

Default output:

1. Optional 2-4 line scope note if the search window, source availability, or coverage limits matter.
2. Main source table:
| source_type | date_time | entity/company | original_source_or_author | factual_item | numbers_or_terms | source_url | verification_status |

After the table, add a short "source gaps / near-window background" list only if important evidence is missing, a claim has no usable source URL, or older items are needed to understand current chatter.
```

## Gemini Deep Research

Use this when the user explicitly asks for Gemini web Deep Research or the topic is broad enough that a long-context source-gathering pass is worth the extra time.

```text
请使用 Gemini Deep Research 或当前网页中最强的研究/长上下文模式，做“资料收集报告”，不要做最终投资结论。

研究主题：[topic]
市场范围：[A股/港股/美股/台股/日股/全球]
产业链范围：[segments]
时间范围：[time range]

请重点收集：
1. 官方公告、交易所披露、公司IR、财报/电话会、监管或政府来源。
2. 可信媒体、供应链媒体、产业数据库中的事实性信息。
3. 每个重要结论背后的原始链接、日期、涉及公司和具体产品/工艺/客户。
4. 源头冲突、旧闻重复、无法确认的传闻和数据缺口。

输出结构：
- source_table：source_type | date | company | factual_item | source_url | confidence
- source_gaps：缺什么证据、为什么影响判断
- stale_or_conflicting_items：可能是旧闻或互相冲突的信息
- useful_leads_for_codex：值得 Codex 继续核验的线索

不要给股票推荐、排名、目标价、买卖建议或最终产业判断。
```

## Focused Gemini Verification

Use this when a small set of important leads needs counter-evidence or source checking.

```text
请优先使用当前网页中可用的最强 Gemini 模型和最强长上下文/资料审阅模式。请对下面这些 AI产业链线索做核验和反证，不要直接相信原结论。

任务：
1. 为每条线索寻找官方公告、财报、交易所披露、公司IR、可信媒体或产业媒体来源。
2. 判断是否为最近 [24/48/72] 小时新增变量，还是旧闻重复。
3. 找反证：公司是否否认、订单是否无法验证、数据是否来自二手转述、是否有时间错配。
4. 给证据等级 A/B/C，并说明为什么。
5. 列出原文支持的事实、仍缺证据的主张及其来源；涉及受益或因果关系时保留来源归因，不自行形成投资结论。

线索：
[粘贴Grok/X/Codex收集到的候选表]

输出字段：
线索 | 核验结果 | 最强来源链接 | 反证/疑点 | 证据等级 | 原文支持的事实 | 仍缺证据的主张 | 下一步验证
```

## Codex Synthesis Checklist

Before finalizing, check:

- Did every current fact that can change use web or local market-data verification?
- Are source links attached to hard claims?
- Are C-level rumors separated from conclusions?
- Are A-share/HK/US/Taiwan tickers normalized?
- Are company links and causal claims attributed to their original sources rather than inferred by the collection model?
- Are beneficiary judgments, company rankings, and earnings/trading elasticity left to the subsequent industry-chain or company analysis when requested?
- Are follow-up indicators concrete enough to monitor?

## Default Table

```text
Claim | Published at | Event at | Original source / URL | Grade | Chain segment | Source-mentioned company / product | Attributed source claim | Verification status | Next verification
```
