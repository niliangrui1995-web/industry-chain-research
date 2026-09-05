# 财务证据审计 Schema

构造审计包时按本合同填写。所有财务值、比例、缩放因子、年化倍数和容忍度均使用 JSON string；结构计数和天数使用 JSON integer。

## 目录

- [顶层](#顶层)
- [Source](#source)
- [Fact](#fact)
- [ValueRef 与派生值](#valueref-与派生值)
- [公共 Check 字段](#公共-check-字段)
- [六种 Check](#1-cross_source)
- [准出结果](#准出结果)

## 顶层

```json
{
  "schema_version": "1.0",
  "audit_id": "example-20260727",
  "as_of": "2026-07-27T15:00:00+08:00",
  "sources": [],
  "facts": [],
  "checks": []
}
```

`checks` 可以为空，但会以 `NO_VERIFIED_CHECKS` 失败。ID 在各自数组内必须唯一。

`root.as_of` 是本次审计可使用的信息截止时点，必须是含 UTC offset 或 `Z` 的 ISO-8601 timestamp。`checked_at`、instant fact 的 `as_of`、expectation check 的 `event_at` 也必须是 timezone-aware timestamp，不能只写日期或无时区时间。

`source_date`、duration fact 的 `start/end/available_at`、estimate fact 的 `expectation_as_of/target_start/target_end` 可以写 ISO date；如写 timestamp 则必须带时区。`source_date`、`checked_at`、fact 的信息可得时点和 `event_at` 均不得晚于 `root.as_of`。两个 timestamp 精确比较到时分秒和 offset，因此上午 cutoff 不会接受同日下午值；date 按其日期粒度比较。Estimate 的未来目标期合法，不对 `target_start/target_end` 应用研究 cutoff。违反时以 `LOOKAHEAD_DATE` 拒绝输入。

## Source

```json
{
  "id": "S_OFFICIAL",
  "source_type": "official_filing",
  "origin_id": "issuer:FY2025:annual-report",
  "locator": "annual-report.pdf#page=10",
  "source_date": "2026-03-30",
  "checked_at": "2026-07-27T15:00:00+08:00",
  "status": "accepted"
}
```

允许的 `source_type`：

- 官方：`official_filing`、`exchange`、`regulator`、`company_ir`、`official_customer_supplier`
- 数据厂商：`market_data_vendor`
- 可信次级：`credible_secondary`
- 仅线索：`lead_only`
- 被审报告：`report_under_audit`

`origin_id` 标记底层原始文件或独立数据集，不是网页域名。locator 会先去除首尾空白并做大小写无关归一化；同一规范化 locator 若声明不同 `origin_id`，以 `LOCATOR_ORIGIN_CONFLICT` 拒绝输入。`lead_only` 和 `report_under_audit` 不计入任何可信来源等级。

排除来源必须保留：

```json
{
  "id": "S_EXCLUDED",
  "source_type": "credible_secondary",
  "origin_id": "media:old-copy",
  "locator": "https://example.com/old",
  "source_date": "2025-01-01",
  "checked_at": "2026-07-27T15:00:00+08:00",
  "status": "excluded",
  "exclusion_code": "wrong_period",
  "exclusion_reason": "FY2024 value cannot verify FY2025"
}
```

Excluded source 不得被 fact 引用，并会原样进入机器结果。

## Fact

```json
{
  "id": "F_REVENUE",
  "metric": "revenue",
  "value": "100.25",
  "unit": "currency",
  "currency": "CNY",
  "scale": "1000000",
  "period": {
    "kind": "duration",
    "start": "2025-01-01",
    "end": "2025-12-31",
    "frequency": "year",
    "label": "FY2025"
  },
  "available_at": "2026-03-30",
  "basis": "reported_consolidated_prc_gaap",
  "source_refs": ["S_OFFICIAL"]
}
```

`value * scale` 是内部 base value。允许单位：`currency`、`currency_per_share`、`share`、`percent`、`ratio`、`multiple`、`count`。货币单位必须填写三位币种；其他单位的 `currency` 必须为 `null`。Decimal context 精度为 50；51-200 位输入虽然可解析，但乘 `scale` 后只要触发 `Rounded` 或 `Inexact`，就以 `DECIMAL_PRECISION_LOSS` 拒绝，不能吞掉尾数冲突。

Fact 可另填 `accounting_context`，且填写时三个字段必须完整：`reporting_scope=consolidated|parent_only|standalone`、`accounting_framework=prc_gaap|us_gaap|ifrs`、`measurement_basis=reported|adjusted|issuer_defined`；另允许可选的非空 `measurement_definition`，其他未知字段均拒绝。这些字段必须来自 fact 对应报表及指标定义，不能从公司 ticker 或常识推定。`accounting_framework` 表示底层报表准则；AFFO 等派生指标仍保留自身 `basis` 和计量性质，不能因其底层报表为 US GAAP 就称 AFFO 为 GAAP 指标。

为兼容已有完整口径，未填写 `accounting_context` 时，仅精确匹配 `<reported|adjusted>_<consolidated|parent_only|parent|standalone>_<prc_gaap|us_gaap|ifrs>` 的 basis 可解析出等价元数据，其中 `parent` 等价于 `parent_only`。显式元数据不得覆盖该 basis 已表达的范围或准则；冲突报 `BASIS_MISMATCH`。其他 basis（如 `reported_affo`）不自动假定范围，参与 ratio 前必须补齐元数据。`cross_source` 检查及其派生引用保留元数据，不能通过前序核验丢掉范围。

每个 duration fact 必须另填 `available_at`，表示该数值真实披露或首次可得时点，而不是报表期末；它不得早于 `period.end` 或晚于 `root.as_of`。Instant/estimate 默认以 `as_of`/`expectation_as_of` 为 information time，也可用更晚的 `available_at`。每个参与 check 的非缺失 fact 必须至少有一个角色合格来源满足 `source_date >= information_at`，否则报 `STALE_RECORD_SOURCE`；因此 2020 来源不能支撑 2026 价格、股本或共识。

缺失值写成：

```json
{
  "value": null,
  "missing_reason": "official_missing",
  "source_refs": []
}
```

只有 `official_missing` 可以进入 provisional 判定。其他缺值仍是 blocked。

Period 只有三种：

```json
{"kind":"instant","as_of":"2026-07-27T15:00:00+08:00"}
{"kind":"duration","start":"2026-04-01","end":"2026-06-30","frequency":"quarter","label":"Q2 FY2026"}
{"kind":"estimate","expectation_as_of":"2026-07-20","target_start":"2026-01-01","target_end":"2026-12-31","frequency":"year","label":"FY2026E"}
```

`frequency` 不能只靠 label 自报。Duration 的 `start/end`、estimate 的 `target_start/target_end` 必须落入保守跨度门：quarter 75-110 天、half 160-205 天、nine_month 250-295 天、year/ttm 350-380 天；否则以 `INVALID_PERIOD_SPAN` 拒绝输入。

## ValueRef 与派生值

```json
{"fact_id":"F_PRICE"}
{"check_id":"C_MARKET_CAP","output":"value"}
```

Check 只能引用前序 PASS check。输出继承全部上游 `source_ids` 和 `origin_id`，因此派生市值、利润年化或 PE 不会被当成新来源。

## 公共 Check 字段

```json
{
  "id": "C1",
  "kind": "cross_source",
  "materiality": "material",
  "source_gate": {
    "min_independent_origins": 1,
    "counted_tier": "official",
    "required_anchor_tier": "official"
  }
}
```

`counted_tier` 和非 `none` 的 `required_anchor_tier` 可为 `official`、`vendor_or_official`、`any_credible`。独立数量只计算满足 `counted_tier` 的 distinct origin。

集合来源门通过还不够。每个非缺失决策输入必须独立拥有相应 accepted 来源：`cross_source` reference 要 credible；market-cap price 要 vendor/official、shares 至少 credible；expectation quarter 要 official、consensus 要 market-data vendor 或 credible-secondary；valuation/percentage 计算输入至少 credible。`market_cap.expected`、`valuation.expected_low/high`、`percentage.expected` 是待核对 claim，可来自 credible 或 `report_under_audit`，但后者永远不计 gate origin/anchor。派生引用只有在上游 check PASS 后才可进入本门，因此不会误伤已逐项验证的合法派生值。

只有 `counted_tier=official` 的官方来源缺口，或 `required_anchor_tier=official` 且没有官方 anchor，才可成为 provisional-eligible 来源缺口。已有官方 anchor、只是未满足第二个 vendor/credible origin，不可 provisional。

凡是比较报告值或外部预期值，必须显式填写：

```json
{"tolerance":{"relative_pct":"1","absolute_base":"0"}}
```

允许差额为 `max(absolute_base, abs(reference) * relative_pct / 100)`，没有隐藏默认值。

## 1. cross_source

```json
{
  "id": "C_REVENUE",
  "kind": "cross_source",
  "materiality": "material",
  "target": {"fact_id":"F_REPORT_REVENUE"},
  "references": [{"fact_id":"F_OFFICIAL_REVENUE"}],
  "source_gate": {
    "min_independent_origins": 1,
    "counted_tier": "official",
    "required_anchor_tier": "official"
  },
  "tolerance": {"relative_pct":"0","absolute_base":"0"}
}
```

Target 可来自 `report_under_audit` 或 credible source，但每个 reference 必须各自有 credible source，不能让 lead-only reference 借另一 reference 的官方来源搭便车。除 target-reference 外，还检查全部 reference-reference pair。所有被比较 fact 必须具有相同 metric；相同 origin 出现不同值直接报 `ORIGIN_INTERNAL_CONFLICT`。

## 2. market_cap

```json
{
  "id": "C_MARKET_CAP",
  "kind": "market_cap",
  "materiality": "material",
  "price": {"fact_id":"F_PRICE"},
  "shares": {"fact_id":"F_TOTAL_SHARES"},
  "expected": {"fact_id":"F_REPORTED_MARKET_CAP"},
  "capitalization_basis": "total",
  "max_share_age_days": 120,
  "source_gate": {
    "min_independent_origins": 2,
    "counted_tier": "vendor_or_official",
    "required_anchor_tier": "vendor_or_official"
  },
  "tolerance": {"relative_pct":"1","absolute_base":"0"}
}
```

`total` 要求 shares metric 为 `total_shares` 或 `total_shares_outstanding`、basis=`total_shares_outstanding`，输出及 expected metric/basis=`total_market_cap`；`free_float` 要求 shares metric/basis=`free_float_shares`，输出及 expected metric/basis=`free_float_market_cap`。

价格必须各自有 vendor/official 来源，是 `currency_per_share` 的 instant fact，并满足以下 metric/basis 之一：`close_price` 配 `unadjusted_close|official_close`；`share_price` 配 `current_price|official_close|last_trade`；`current_price` 配 `current_price|last_trade`。`adjusted_close` 只适用于收益率/趋势序列，不得用于点时市值，即使 expected 市值同步成同一结果也必须 blocked。Shares 必须各自有 credible source；expected（如有）可来自 credible 或 `report_under_audit` claim。

## 3. expectation_gap

```json
{
  "id": "C_EXPECTATION",
  "kind": "expectation_gap",
  "materiality": "material",
  "quarterly_low": {"fact_id":"F_Q_LOW"},
  "quarterly_high": {"fact_id":"F_Q_HIGH"},
  "consensus": {"fact_id":"F_FY_CONSENSUS"},
  "annualization_factor": "4",
  "event_at": "2026-07-25T18:00:00+08:00",
  "comparison_basis": "annualized_quarterly_deducted_vs_fy_attributable_consensus",
  "company_metric": "deducted_attributable_net_profit",
  "consensus_metric": "fy_attributable_net_profit",
  "source_gate": {
    "min_independent_origins": 2,
    "counted_tier": "vendor_or_official",
    "required_anchor_tier": "official"
  }
}
```

Consensus 必须是事件前的全年 estimate。Quarterly low/high 的 `available_at` 必须是含时区的 timestamp，且精确等于 `event_at`；`event_at` 因而只能表示 actual/preannouncement/derived 单季事实的真实首次可得事件，不能事后选一个更晚日期把 actual 发布后形成的 consensus 伪装成 pre-event。Quarterly official source_date 还必须不晚于该事件。输出 `annualized_low/high`、`gap_low/high`、`above|straddles|below|insufficient`，并固定 `formal_surprise_status=N/A`。

除 `expectation_as_of < event_at` 外，consensus fact 引用的每个 accepted source 还必须满足 `source_date < event_at`，以证明该发布物或历史快照在事件前真实可得。`source_date` 若只有 date 且与事件同日，因无法证明具体发布时间而保守失败；事件后的 `source_date` 不能用事件前的自报 `expectation_as_of` 绕过。`checked_at` 是审计取证时间，可以晚于事件，但仍不得晚于 `root.as_of`。

`company_metric` 必须精确为 `deducted_attributable_net_profit`，`consensus_metric` 必须精确为 `fy_attributable_net_profit`，三个输入 fact 的 metric 也必须分别同名；不能通过改 check 字段把归母、扣非或收入混成同一比较。

Quarterly low/high 必须各自有 official source，basis 只能是：`actual_quarterly_deducted_attributable_net_profit_prc_gaap`、`preannouncement_quarterly_deducted_attributable_net_profit_prc_gaap`、`derived_single_quarter_deducted_attributable_net_profit_prc_gaap`。Consensus 必须有 market-data vendor 或 credible-secondary source，basis 必须精确为 `pre_event_fy_attributable_net_profit_consensus_prc_gaap`。`non_gaap_adjusted`、`post_event_current_consensus` 等 basis 会阻断整个 check，不能由派生输出换名洗白。

公司季度 `end` 必须不晚于 `event_at`，且公司季度的 `start/end` 必须完整落在 consensus 的 `target_start/target_end` 内。不得用 label 猜财年，也不得把 FY2030E 等不同目标年度与 FY2026 季度混算。
该比较合同的 `annualization_factor` 必须等于字符串 `"4"`；其他因子不能沿用本项目的 x4 口径名称。
Quarter 的实际跨度还必须为 75-110 天；一日区间即使标成 quarter 也不能乘四准出。

## 4. expectation_surprise

这是全球财报活动的通用 actual-vs-pre-event-consensus 合同；它不替代上面的 A 股单季扣非 x4 专用口径。

```json
{
  "id": "C_Q2_REVENUE_SURPRISE",
  "kind": "expectation_surprise",
  "materiality": "material",
  "subject_kind": "reported_actual",
  "actual_low": {"fact_id":"F_Q2_REVENUE"},
  "actual_high": {"fact_id":"F_Q2_REVENUE"},
  "consensus": {"fact_id":"F_Q2_REVENUE_CONSENSUS"},
  "event_at": "2026-07-25T16:00:00-04:00",
  "tolerance": {"relative_pct":"1","absolute_base":"0"},
  "source_gate": {
    "min_independent_origins": 2,
    "counted_tier": "vendor_or_official",
    "required_anchor_tier": "official"
  }
}
```

`subject_kind` 必填且只能为 `reported_actual` 或 `company_guidance`。Reported actual 使用 `actual_low/high`；point actual 可让两者引用同一 fact，公司已报告范围则分别引用端点。Actual 必须是同一 duration period 的 official fact，且两个端点的 `available_at` 都必须是含时区并精确等于 `event_at`；这把 `event_at` 固定为 actual release event，阻止 actual 发布后形成的 consensus 被自报的更晚事件洗成 pre-event。Consensus 必须是 vendor/credible-secondary 的 estimate；metric、unit、currency、basis 必须完全相同，actual start/end/frequency 必须精确匹配 consensus target period。

Company guidance 使用 `guidance_low/high`，两个端点必须是同一 official company estimate。其 `expectation_as_of` 与 information time 必须是含时区且精确等于 `event_at`，表示 guidance 在该事件形成/可得；target_start/end/frequency 必须精确匹配事件前 consensus estimate。未来 guidance 目标期合法，但所有形成/来源/核验时点仍不得晚于 `root.as_of`。

两种 subject 都支持 `revenue`、`net_income|net_profit`、operating/gross profit、FCF、EBIT/EBITDA，以及 GAAP/adjusted/non-GAAP EPS 等显式 metric；EPS 类必须是 `currency_per_share`，其他指标必须是 `currency`。GAAP 与 non-GAAP 只能靠完全相同 basis 配对，不能混算。

Consensus 的 `expectation_as_of` 与每个 `source_date` 都必须严格早于 `event_at`；reported actual 的 `available_at` 或 guidance 的事件时形成/可得时点必须精确等于事件，subject source_date 不得晚于事件且仍需满足逐 fact 的 `source_date >= information_at` 新鲜度门。所有时点仍受 `root.as_of` cutoff。

分类容忍带为：

```text
allowed = max(absolute_base, abs(consensus) * relative_pct / 100)
absolute = actual - consensus
percentage = (actual - consensus) / abs(consensus) * 100
```

区间整体高于容忍带为 `beat`，整体低于为 `miss`，整体在带内为 `meet`，跨越边界为 `straddles`。负共识使用 `abs(consensus)`，因此仍可解释；共识为零或任一必要值缺失时为 `not_meaningful`，不生成百分比。输出 `absolute_low/high` 与 `percentage_low/high`。

如需审计报告声称的 surprise 数字，可另填 `expected_low/high`、`expected_kind=absolute|percentage` 与 `claim_tolerance`。Expected fact 的 metric 分别为 `<input_metric>_surprise_absolute|<input_metric>_surprise_pct`，basis 为 `<input_basis>_vs_pre_event_consensus`；可引用 `report_under_audit`，但不计 gate origin/anchor。声称值不符仍 blocked。

## 5. valuation

```json
{
  "id": "C_PE",
  "kind": "valuation",
  "materiality": "material",
  "metric": "pe_user_defined",
  "numerator": {"check_id":"C_MARKET_CAP","output":"value"},
  "denominator_low": {"check_id":"C_EXPECTATION","output":"annualized_low"},
  "denominator_high": {"check_id":"C_EXPECTATION","output":"annualized_high"},
  "valuation_basis": "latest_single_quarter_deducted_attributable_net_profit_x4",
  "source_gate": {
    "min_independent_origins": 2,
    "counted_tier": "vendor_or_official",
    "required_anchor_tier": "official"
  }
}
```

支持 `pe_user_defined`、`pe`、`pb`、`ps`、`p_fcf`、`dividend_yield`、`earnings_yield`。如填写 `expected_low/high`，还必须填写 tolerance。Multiple 输出高分母对应低估值；分母非正时输出 `not_meaningful`，不生成数字。

`dividend_yield` 的可信 cash-dividend 或 dividend-per-share fact 允许 `value="0"`，正市值或正价格下结果是有意义的 `0%`，无需额外布尔确认字段。仍须通过来源、metric、basis 和期间门。缺失/未披露的股息保留 `null` 和 `missing_reason`，不得用零替代；负股息仍阻断，零或负市值/价格仍为 `not_meaningful`。其他 valuation numerator 的正值合同不变。

`pe_user_defined` 是固定项目口径：numerator 的 metric/basis 必须都是 `total_market_cap` 且为 instant；denominator 必须直接引用同一个前序 `expectation_gap` 的 `annualized_low/high`，metric=`deducted_attributable_net_profit`、basis=`latest_single_quarter_deducted_attributable_net_profit_x4`。复制相同数字到普通 fact 也不能替代这条派生链。

通用估值只接受以下配对：

| metric | 合法分子 / 分母 |
|---|---|
| `pe` | `total_market_cap` / 年度或 TTM 净利润；或合法 share price / 年度或 TTM EPS |
| `pb` | `total_market_cap` / instant book value；或合法 share price / instant BVPS |
| `ps` | `total_market_cap` / 年度或 TTM revenue；或合法 share price / 年度或 TTM revenue per share |
| `p_fcf` | `total_market_cap` / 年度或 TTM free cash flow；或合法 share price / 年度或 TTM FCF per share |
| `dividend_yield` | 年度或 TTM cash dividend / `total_market_cap`；或 dividend per share / 合法 share price |
| `earnings_yield` | 年度或 TTM net profit / `total_market_cap`；或 EPS / 合法 share price |

各 fact 的 `basis` 必须来自其 metric 的白名单。通用 multiple 的 `valuation_basis` 必须等于 denominator basis；yield 的 `valuation_basis` 必须等于 numerator basis。Flow 只接受 FY、TTM 或 full-year estimate，存量项与价格/市值必须是 instant。

点时价格/市值 basis 同样禁用 `adjusted_close`，且各 valuation 输入必须各自有 credible source。通用估值还强制时间关系：市场价格或市值 `as_of` 不得早于 historical flow 的 `period.end`；estimate 时不得早于 `expectation_as_of`；PB 不得早于 book-value `as_of`。例如 2020 市值除以 2026 TTM 利润不可准出。所有时点仍必须不晚于 `root.as_of`。

当前通用估值 fundamental metric/basis 白名单如下（`|` 表示任选其一）：

- `net_profit`: `ttm_net_profit|fy_net_profit|reported_consolidated_net_profit`
- `attributable_net_profit`: `ttm_attributable_net_profit|fy_attributable_net_profit|reported_attributable_net_profit`
- `deducted_attributable_net_profit`: `ttm_deducted_attributable_net_profit|fy_deducted_attributable_net_profit`
- `eps|earnings_per_share`: `ttm_eps|fy_eps|basic_eps|diluted_eps`
- `equity_attributable_to_parent`: `equity_attributable_to_parent|book_value_attributable_to_parent`
- `book_value`: `book_value|equity_attributable_to_parent`
- `book_value_per_share`: `book_value_per_share`；`bvps`: `book_value_per_share|bvps`
- `revenue`: `ttm_revenue|fy_revenue|reported_consolidated_revenue`
- `revenue_per_share`: `ttm_revenue_per_share|fy_revenue_per_share`
- `free_cash_flow`: `ttm_free_cash_flow|fy_free_cash_flow`
- `free_cash_flow_per_share`: `ttm_free_cash_flow_per_share|fy_free_cash_flow_per_share`
- `cash_dividend`: `ttm_cash_dividend|fy_cash_dividend`
- `dividend_per_share`: `ttm_dividend_per_share|fy_dividend_per_share`

## 6. percentage

```json
{
  "id": "C_QOQ",
  "kind": "percentage",
  "materiality": "material",
  "mode": "change",
  "current": {"fact_id":"F_CURRENT"},
  "base": {"fact_id":"F_BASE"},
  "period_relation": "qoq",
  "output_metric": "revenue_qoq_pct",
  "output_basis": "reported_consolidated_prc_gaap_qoq",
  "source_gate": {
    "min_independent_origins": 1,
    "counted_tier": "official",
    "required_anchor_tier": "official"
  }
}
```

`change` 使用 `current/base`，relation 可为 `sequential`、`yoy` 或 `qoq`，要求 current/base metric 与 basis 完全相同；`output_metric` 固定为 `<input_metric>_<relation>_pct`，`output_basis` 固定为 `<input_basis>_<relation>`，不能把 revenue 变化率标成 `eps_qoq_pct`。`qoq/yoy` 两个输入除各自满足 frequency 跨度门外，跨度差不得超过 15 天。如填写 expected，必须填写 tolerance。

`ratio` 使用 `numerator/denominator` 且要求 `period_relation=same`；`output_basis` 固定为 `<numerator_basis>_over_<denominator_basis>`。可审计配对包括 gross/operating/net/attributable/deducted margin，普通公司 cash-dividend payout、profit/FCF/operating-cash-flow coverage，以及收益型行业的显式合同：`cash_distribution` 除以 `affo|ffo|distributable_amount|net_investment_income` 为 `distribution_payout_pct`，反向为 `distribution_coverage_pct`；另支持 `distributable_profit`、`capital_available_for_distribution` 与 cash dividend 的 payout/coverage。未知配对只能使用 `calc` 做非准出计算，在 audit 中报 `UNSUPPORTED_RATIO_CONTRACT`。

所有 ratio 输入必须具备上述 `accounting_context`（显式或已知 basis 解析），且 `reporting_scope`、`accounting_framework` 相同；任何范围缺失报 `MISSING_ACCOUNTING_CONTEXT`，即使 supporting check 也阻断准出。Margin 还必须有相同的 `measurement_basis`，但自由文本 basis 可使用不同指标标签，例如同一 reported context 的 `reported_gross_profit` 与 `reported_revenue` 可以配对。若 margin 两侧都是 `adjusted` 或 `issuer_defined`，还必须各自提供相同的 `measurement_definition`，指向同一份有来源的调整/计量定义；缺失定义阻断，不能因均叫 adjusted 就假定口径一致。Payout/coverage 则按指标白名单允许不同计量性质和不同 basis，例如同一合并范围、同一 US GAAP 底层报表的 `reported_cash_distribution` 与 `reported_affo`；该例两项均需显式元数据，AFFO 的 `measurement_basis` 按原文取 `issuer_defined` 或 `adjusted`。工具检查声明的合同，不替代原文对 AFFO 调整项与分派归属的核验。审计结果的 `details.accounting_contexts` 保留两侧口径，不能通过拼接 `output_basis` 洗掉母公司/合并报表冲突。
`qoq` 要求两个季度期末相隔 75-110 天；`yoy` 要求可比期间期末相隔 350-380 天，避免把跨季或跨年数据贴错标签。

## 准出结果

- Material check 失败：`FAIL/blocked`，退出码 1。
- Supporting check 失败：状态仍为 `WARN` 且不计 verified；但只要 issue 属于数值、来源内部、币种、单位、期间、metric、basis、事件时点或派生链冲突，整体仍为 `FAIL/blocked`。只有不构成上述冲突的辅助缺口才可保留为非阻断 warning。
- 零 verified：`FAIL/blocked`。
- 只有缺官方来源或值，并且顶层存在完整 `provisional_context` 时：`FAIL/provisional`，仍退出 1。
- Schema、Decimal、日期、ID、未知或前向引用错误：`ERROR/invalid_input`，退出 2。

`audit --input X --output X` 会在读取或写入审计结果前比较解析后的路径；同一路径以 `OUTPUT_OVERWRITES_INPUT` 退出 2，原输入文件保持不变。
