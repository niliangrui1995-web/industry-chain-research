---
name: financial-evidence-audit
description: Audit decision-critical investment figures with deterministic Decimal arithmetic, source-origin independence, derived-value provenance, and currency/unit/period/accounting-basis release gates. Use for 市值、PE、预期差、单季年化、百分比、股息覆盖、跨来源数字、报告准出，或任何数字错误会改变个股、财报、产业链映射和收益型投资结论的任务.
---

# Financial Evidence Audit

把本技能作为投资数字的强制准出门。它验证输入数字和派生链是否可用于投资结论，不判断公司是否值得投资。

## 工作合同

1. 先固定上市主体、ticker、研究截止时点 `as_of`、报告期间、行情时点、币种、单位、指标和会计口径；`as_of`、核验时点、instant fact 和事件时点必须带时区，来源、事实及预期形成时点不得越过 `as_of`，预测目标期可在其后。
2. 把原始或外部报告值写入 `facts`，把来源写入 `sources`；不得把模型心算的派生值伪装成 fact。
3. 把跨源核验、市值、预期差、估值和百分比写入顺序执行的 `checks`。后续 check 只能引用前序 PASS check 的输出。
4. 给每个数值比较显式设置相对和绝对容忍度；不要使用跨行业默认阈值。
5. 运行审计器并按退出码处理。非零退出时不得把相关数字写成已核验正式结论。

完整输入合同见 [references/audit-schema.md](references/audit-schema.md)。选择来源和划分 `origin_id` 时读 [references/source-contract.md](references/source-contract.md)。

## 确定性执行

只使用以下两个入口：

```powershell
python .agents/skills/financial-evidence-audit/scripts/financial_evidence_audit.py calc --expr "0.1 + 0.2"
python .agents/skills/financial-evidence-audit/scripts/financial_evidence_audit.py audit --input evidence-audit.json --output audit-result.json --pretty
```

- `calc` 使用受限 AST 和 Decimal；它只是计算器，不计入报告的 `verified_count`。
- `audit` 只接受 `sources -> facts -> checks` 合同。所有财务值和容忍度必须写成 JSON decimal string。
- Fact 的 `value * scale` 必须在 50 位 Decimal 精度内精确表示；发生 `Rounded` 或 `Inexact` 即为无效输入，不允许带精度损失继续比对。
- `origin_id` 表示底层原始文件或数据集。一份公告被十个平台转载仍然只有一个 origin。
- locator 去除首尾空白并忽略大小写后若相同，不能声明成不同 `origin_id`。
- `lead_only` 永远不能满足正式来源数量或锚点门。
- 来源门不仅检查所有输入的并集；每个非缺失决策输入还必须独立拥有该 check 要求的 accepted credible source，不能让 lead-only fact 搭便车在另一 fact 的官方来源上。
- 每个 fact 的来源日期还必须不早于其信息可得时点：instant 用 `as_of`，estimate 用 `expectation_as_of`，duration 必须显式填写真实披露/可得时点 `available_at`；旧来源不能包装当前值。
- `expected`/`expected_low/high` 作为待核对报告 claim 可引用 `report_under_audit`，但它不计 gate origin/anchor，计算输入仍须各自可信。
- Duration/estimate 的 `frequency` 必须与实际日期跨度一致；一日区间不能自报 quarter 后乘四年化。
- 工具不自动做汇率、期间、单位或会计口径转换；先建立有来源的标准化 fact，再审计。
- `audit --input X --output X`（含解析后同一路径）会以无效输入退出且不修改原文件。

## 六种 Check

- `cross_source`：同时检查报告值、每个可信 reference 值以及来源之间的 pairwise 冲突；target 可来自 `report_under_audit`，不取中位数掩盖差异。
- `market_cap`：价格必须独立来自 vendor/official，股本和 expected 各自可信；检查 metric/basis、时点和资本化口径。`adjusted_close` 不得用于点时市值。
- `expectation_gap`：固定检查事件前 `fy_attributable_net_profit` 共识与最新单季度 `deducted_attributable_net_profit` 的 x4 年化比较；季度必须是 official 的 actual/preannouncement/derived 单季扣非归母 PRC-GAAP 合法 basis，其 `available_at` 必须是带时区且精确等于 `event_at`，共识必须是 vendor/credible 的 pre-event FY 归母 PRC-GAAP basis，且其每个来源 `source_date` 必须证明事件前已发布或已有快照，不能把 actual 后形成的共识靠自报更晚事件洗成 pre-event。
- `expectation_surprise`：用必填 `subject_kind=reported_actual|company_guidance` 分开核验已报告 actual/range 或公司 guidance range 对事件前 consensus 的 deterministic beat/meet/miss/straddles；reported actual 的 `available_at` 与 guidance 的形成/可得时点都必须是带时区且精确等于 `event_at`；支持 revenue、EPS、net income 等合法指标，强制 metric、单位、币种、accounting basis、目标期间和各自 PIT 一致，并同时输出绝对与百分比差异。
- `valuation`：计算 PE/PB/PS/P-FCF 或收益率区间；强制合法分子/分母 metric、basis、period 和各自可信来源，点时价格禁用 `adjusted_close`，市场快照不得早于历史 flow 期末、estimate 形成时点或 PB 账面价值时点。已获可信来源证实的零现金股息或零每股股息，在正市值/价格下可准出 `0%`；缺失股息不能填零。
- `percentage`：变化率的 current/base 必须同 metric，`output_metric=input_metric+relation+_pct` 且 basis 同步派生；ratio 仅允许明确的 margin、股息 payout/coverage 白名单配对，另检查相同报表范围、底层会计框架和 margin 计量口径。已知 basis 可解析，否则必须提供有来源的 `accounting_context`；范围未知或冲突不能准出，AFFO/FFO 与 distribution 的合法不同指标不能用 basis 字符串相同代替检查。

派生引用使用 `{ "check_id": "C1", "output": "value" }`；原始引用使用 `{ "fact_id": "F1" }`。前向引用、未知输出和循环依赖属于无效输入。

## 准出语义

- `PASS / publishable`，退出码 `0`：至少一个 check 已核验，且没有 material 失败，也没有 supporting 数值、来源、币种、单位、期间、metric 或 basis 冲突。
- `FAIL / blocked`，退出码 `1`：重大数值冲突、来源不足、零核验、币种、单位、期间、口径或依赖失败。
- `FAIL / provisional`，退出码 `1`：只允许真正缺官方来源或官方值；必须显式提供完整 fallback、缺失材料和未来复查时间。已有官方 anchor 但仅缺第二个 vendor，以及任何 material/supporting 冲突，都不能降格为 provisional。
- `ERROR / invalid_input`，退出码 `2`：schema、Decimal、日期、ID 或引用无效。

`N/A`、`N/M` 和 `not_meaningful` 是合法计算状态。非正利润下不生成数字 PE；如果报告仍声称数字 PE，审计必须失败。

研究结论还必须单独评估生意质量、产业传导、管理层、预期、估值假设和风险；数字通过不等于值得投资。
