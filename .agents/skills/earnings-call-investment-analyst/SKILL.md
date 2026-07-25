---
name: earnings-call-investment-analyst
description: Analyze public-company earnings releases, financial results, guidance, conference calls, earnings webcasts, results briefings, investor meetings, transcripts, replay audio, expectation gaps, downstream demand, upstream bottlenecks, and post-earnings stock reactions. Use for 财报、业绩会、电话会、指引、超预期/低于预期、QoQ、管理层问答或财报后投资判断.
---

# Earnings Call Investment Analyst

围绕“本季度改变了什么”开展分析。根据用户问题选择必要深度；预览、数字核对、电话会深挖和自动化子任务不使用同一固定模板。

## 先回答

1. 公司实际业务和本季度关键变量是什么？
2. 结果相对公司指引、市场预期和前一季度是 beat、meet、miss 还是证据不足？
3. 指引和管理层表述改变了未来 1-4 个季度的哪些假设？
4. 哪些下游需求、订单、价格、产能、库存或上游约束决定兑现质量？
5. 结果对基本面、业绩弹性和交易弹性分别意味着什么？

## 来源层级

优先使用公司 IR、官方财报/公告、监管或交易所文件、公司 presentation 和官方 webcast/replay。官方没有完整电话会内容时，可使用可靠第三方全文 transcript 或托管的原始电话会音频，但必须标明来源类型、完整性和缺口。

- 报告数字与指引以公司/监管原文为准。
- 可靠全文 transcript 可作主要工作材料；有原始音频时只核验关键措辞或争议段落，默认不做全量 ASR。
- 只有音频而无可靠全文时，才考虑转录。
- 当前日期、预期、价格、市值和财报后反应必须实时核验。
- 官方字幕播放列表缺少 `EXT-X-ENDLIST` 时，按不完整滑动窗口处理。

找不到官方 transcript 或 replay 不是停止理由；换用搜索、浏览器、页面源码、网络请求、直接下载或可靠 provider。脚本失败也不是停止理由。

## 自适应流程

1. **建立公司基线**：用一段话说明卖什么、客户是谁、如何赚钱；只列会影响本季度解读的业务线、竞争位置和 KPI。
2. **确定比较口径**：确认当前财季和前一财季，收集事件前市场最后可得的 point-in-time 全年归母共识、前期指引和前一季度官方实际值；不要求机构预测在前一日更新，但要记录预测发布日期和新鲜度。A 股正式报告、预告和快报均先取得或由累计官方数据反推最新单季度扣非归母，再乘 4 对比机构全年归母共识；正式报告发布后替换预告值。记录 `comparison_basis=annualized_quarterly_deducted_vs_fy_attributable_consensus`；指标含义或单季扣非无法确认时写 `N/A`。
3. **核对结果与指引**：分开归母与扣非、GAAP 与 non-GAAP，检查收入、利润率、EPS、现金流、资产负债和关键分部；结论写明这是用户定义的单季年化 run-rate 判断。需要 PE(TTM) 时按 `当前总市值/(最新单季度扣非归母×4)` 计算并标注市值时点，年化利润不为正时写 `N/A/不适用`。
4. **提取电话会增量**：关注需求、订单、客户、价格、产能、良率、库存、供应链、监管、融资和分析师 Q&A；与前一季度同类事件比较。
5. **检查需求和瓶颈**：明确管理层是否提及下游需求和上游约束；没有提及就写 `not_mentioned`，不要用行业新闻补成管理层观点。
6. **形成投资解读**：区分事实、管理层主张、外部分析和自身推断；给反转条件与后续 KPI。只有重要且不确定性可量化时才做情景分析。

自动化深挖或完整 post-earnings 任务必须读 [references/analysis-checklist.md](references/analysis-checklist.md)。化合物半导体、衬底、光模块、InP/GaAs/Ge/SiC 或出口管制公司再读 [references/compound-semiconductor-checks.md](references/compound-semiconductor-checks.md)。

## 资源选择

只在能提高可靠性或复现性时使用：

- 原始来源、webcast、transcript 或音频收集：[references/source-workflow.md](references/source-workflow.md)
- 证据包字段：[references/evidence-schema.md](references/evidence-schema.md)
- 官方来源清单：`scripts/source_discovery.py`
- webcast 资产探测：`scripts/webcast_asset_fetcher.py`
- HLS 字幕合并：`scripts/caption_playlist_fetcher.py`
- 音频转录：`scripts/audio_transcriber.py`；先运行 `--check-deps`
- Windows ASR 环境：`scripts/setup_asr_env.ps1`
- 结构化证据包：`scripts/earnings_pack_builder.py`

脚本是可选加速器。实际使用时才记录 `script_used`、`script_result`、`script_limitation`、`manual_fallback_path` 和 `final_source_type`。

## 输出

结论先行，按问题需要展示数字对比、指引、电话会增量、前季变化、下游需求、上游瓶颈、投资解读、风险和跟踪指标。完整深挖必须说明：

`company_original_status`、`call_content_status`、`final_source_type`、`missing_materials`、`provisional true/false`、`confidence level`。

资料不完整时给 provisional 结论和明确缺口，不为满足模板编造数字、管理层表述或上游瓶颈。
