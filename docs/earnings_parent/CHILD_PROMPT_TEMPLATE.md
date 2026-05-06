# 财报电话会深挖子任务 Prompt 模板

母任务创建或更新单公司 child automation 时，必须按本模板生成 prompt。方括号内为运行时填充值；没有可信值时写 `N/A` 或 `not_found`，不要删除字段。

## Header

```text
TASK_KEY: [ticker]|[report_date]|[fiscal_period]
Company: [company]
Ticker: [ticker]
Market: [market]
Sector: [sector]
Report date: [YYYY-MM-DD]
Fiscal period: [fiscal_period or N/A]
Planned child start Beijing: [YYYY-MM-DD HH:MM]
Schedule basis: [official_call_plus_3h / default_proxy_not_call_time]
Official call Beijing time: [YYYY-MM-DD HH:MM or not_found]
Original call time text: [original text or N/A]
Original timezone: [IANA/source timezone or N/A]
Call time source URL: [official URL or N/A]
Call time source type: [official_ir_event / official_ir_webcast / official_ir_press_release / sec_filing / exchange_announcement / third_party_unconfirmed / not_found]
Calendar source: [Company IR / JPX / TDnet / DART / KIND / MOPS / SEC EDGAR 6-K / confirmed / Yahoo Finance / Nasdaq / Alpha Vantage / not_found_in_current_calendar]
Event status: [confirmed / estimated / estimated_unverified / estimated_conflict / unknown]
Source confidence: [official_confirmed / official_disclosure / third_party_calendar_estimate / non_official_estimate / conflict_requires_official_verification / official_date_mismatch / unknown_current_event_missing]
Official source URL: [official URL or N/A]
Calendar caveat: [one-line caveat explaining official, estimate, conflict, skipped DART, or mismatch status]
```

## Literal hard gate

Every generated child prompt must contain this block exactly:

```text
CHILD TASK SKILL HARD GATE: At the start of this single-company child task, before collecting or analyzing anything, invoke and follow the skill earnings-call-investment-analyst. The project-local skill directory hint is D:\vcp_hunter\产业链投研\skills\earnings-call-investment-analyst, so use that project skill location when resolving the skill. This skill is invoked only by the child task at runtime, not by the parent scheduler. If the child task cannot invoke earnings-call-investment-analyst from that project-local skill location, stop immediately and report missing_skill: earnings-call-investment-analyst. Do not silently substitute industry-research-router, finance-news, stock-evaluator, generic web search, or your own framework for this child task. Do not claim skill invocation by merely reading SKILL.md as a plain file; normal skill resolution may read that SKILL.md.
```

## Scope

- 只分析 header 指定的单一公司和 ticker，不扩展成行业通用研究或多公司横评。
- 开始时必须先调用 `earnings-call-investment-analyst`；该 skill 成功调用后，才允许进入资料抓取、财务核对、电话会分析和投资判断。
- 抓取和核对公司 IR、财报 PDF、presentation、SEC/交易所文件、conference call audio/video/transcript、Q&A。

## Fundamental baseline hard constraint

Before reading or analyzing the earnings release, conference call, transcript, or Q&A, the child task must first complete the earnings-call-investment-analyst Company Fundamental Baseline:

- one-paragraph business model
- business / product-line map
- competitive position by business
- AI exposure path by business
- quarter-sensitive KPIs
- earnings interpretation bridge

Beat/miss, guidance, Q&A, bottleneck analysis, and supply-chain impact must be based on that baseline.

## Upstream bottleneck evidence hard constraint

In the earnings release, prepared remarks, and Q&A, the child task must actively search for upstream bottleneck evidence and label each relevant item with mention status:

- `mentioned_current_bottleneck`
- `mentioned_future_risk`
- `mentioned_mitigated`
- `mentioned_not_bottleneck`
- `not_mentioned`
- `third_party_only`

If the company did not mention an alleged upstream bottleneck, write `not_mentioned` or `evidence_absent`; do not infer it from industry headlines, stock moves, or theme logic.

## Evidence and source rules

- 公司 IR、官方文件、SEC 或交易所、官方链出的 webcast/replay/transcript/captions 优先用于核对财务数字和管理层原话。
- 第三方财经日历只能用于确认事件线索，不能作为 reported facts 的最终依据。
- 若官方 transcript、audio replay、video replay、完整 captions 或 Q&A 尚未发布或不可完整访问，agent 必须继续寻找能支撑投资判断的完整电话会内容。
- 资料获取路径由 agent 自主选择：官方页面、SEC/交易所页面、联网搜索、可靠第三方 transcript/audio provider、浏览器检查、HTTP、页面源码、network request、直接下载或项目脚本均可。
- StockAnalysis、Quartr、Motley Fool、Seeking Alpha、Benzinga、Alpha Spread、EarningsCall.biz 等只是可选搜索种子，不是必须逐个检查的清单。
- 可靠第三方 full transcript 或第三方托管的原始电话会音频可作为 fallback 证据，但必须标注为 `third_party_transcript` 或 `original_call_audio + third_party_hosted`，不能列入官方来源。
- 如果可靠 full transcript 和原始电话会音频都可用，以 full transcript 为主要工作材料；音频只用于核验关键措辞、争议段落和转录质量，默认不要跑完整音频 ASR。
- hard gate 中禁止 generic web search 的含义是不得用通用搜索替代 skill invocation；skill 成功调用后，可按 `earnings-call-investment-analyst` 的 agent-first / source-quality-first 原则使用任意高效可靠路径找资料。
- 脚本只是可选辅助工具；不要因为脚本存在就必须先跑脚本。只有实际使用脚本时，才记录 `script_used`、`script_result`、`script_limitation`、`manual_fallback_path`、`final_source_type`。
- 脚本失败、无结果、401/403、页面 JS 化、provider stale 或 parser miss 都不能作为停止理由。

## Required analysis

核对并分析：

- 收入、EPS、利润率、订单、库存、资本开支、指引与一致预期。
- 电话会和 Q&A 的未来展望、客户下单意愿、AI/数据中心需求、价格、库存、交期、产能、上游瓶颈和产业链影响。
- 明确结论：超预期 / 符合 / 低于 / 证据不足。
- 给出 confidence level，并说明证据来源层级。

## Required final fields

最终中文输出必须说明：

- `company_original_status`
- `call_content_status`
- `final_source_type`
- `missing_materials`
- `provisional true/false`
- `confidence level`
