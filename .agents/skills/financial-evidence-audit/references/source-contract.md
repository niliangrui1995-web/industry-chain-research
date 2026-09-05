# 投资数据来源合同

需要选择外部数据、核对来源独立性或决定一项证据能支撑什么结论时读取。

## 证据层级

| 等级 | 典型来源 | 可以支撑 |
|---|---|---|
| `official` | 公告、交易所、监管、公司 IR、财报、招股书、官方客户/供应商材料 | 公司硬事实、正式财务数据、已披露客户/项目/产能 |
| `credible_secondary` | 具名行业协会、可靠媒体、研究机构 | 行业背景、交叉验证、待官方确认的具体线索 |
| `market_data_vendor` | iFinD、东方财富、HTSC、TDX、Yahoo、Alpha Vantage、本地 HT | 行情、共识、估值、流动性和交易上下文 |
| `lead_only` | Grok/X、Gemini、论坛、匿名截图、模型摘要、概念标签 | 搜索线索和反证方向 |

`report_under_audit` 只表示当前被核对的报告或工作稿，不是独立验证来源。

工具品牌不决定等级；只有工具直接返回可核验的官方原文时，原文本身才按官方来源使用。

## 决策边界

- 客户、订单、认证、量产、收入和供应缺口不能由行情、概念或模型输出证明。
- 历史 point-in-time 共识必须同时保留事件前 `expectation_as_of` 和可核验的事件前发布物/快照 `source_date`；当前滚动页面或事件后发布页面不能靠自报的历史成分日期冒充事件前快照。同日仅有 date 而无具体发布时间时保守视为未证明事件前可得；事后核验的 `checked_at` 可以晚于事件。
- Fact 与来源还必须绑定信息可得时间：instant 用 `as_of`，estimate 用 `expectation_as_of`，duration 显式记录真实披露时点 `available_at`。参与决策 check 的每个非缺失 fact 至少有一个角色合格来源满足 `source_date >= information_at`；报表期末不能冒充披露日，旧来源不能包装当前值。
- TDX、HTSC、iFinD、东方财富等可支持价格和交易结构，但不能单独证明真实受益。
- 跨市场比较先统一币种、股本、会计期间和 GAAP/non-GAAP；无法统一就分列，不强算。
- 一份官方文件和十个转载仍然只有一个原始来源。
- `origin_id` 必须指向底层原始文件或独立数据集；转载域名、模型名称和抓取工具名称都不能制造新 origin。
- locator 去除首尾空白并忽略大小写后视为同一定位符；同一规范化 locator 不得分配不同 `origin_id`，否则输入无效。这一约束同时适用于 accepted 与 excluded source。
- 来源门同时包含 `counted_tier`、独立 origin 数量和可选 anchor。`lead_only`、被审报告及 excluded source 永远不计数。
- 来源门还逐 record 执行：跨源 reference、估值与百分比计算输入必须各自 credible；market-cap price 必须各自 vendor/official；expectation quarter 必须各自 official、consensus 必须各自来自 vendor 或 credible-secondary。一个输入的强来源不能替另一个 lead-only 输入过门。
- `market_cap.expected`、`valuation.expected_low/high`、`percentage.expected` 是待核对的报告 claim，可来自 `report_under_audit`；它们可以被比较但仍不计入 origin 数量或 anchor，也不能替代计算输入的可信来源。
- 多个来源都接近报告值仍不代表彼此一致；正式准出还必须通过来源之间的 pairwise 数值检查。
- 点时价格、市值和估值只接受未复权或真实时点价格；`adjusted_close` 只可用于收益率/趋势序列，不能作为当时可交易价格或市值基础。
- Actual-vs-consensus 合同中的 `event_at` 必须是真实 actual/guidance 首次可得事件：A 股 `expectation_gap` 的 quarterly low/high 与全球 `expectation_surprise.reported_actual` 的 actual low/high 都要求 `available_at` 为带时区且精确等于 `event_at`；`company_guidance` 的形成/可得时点同样精确等于事件。Subject 必须来自 official release/filing 或 official company source，consensus 必须来自事件前 vendor 或可信历史快照。不得把 actual 发布后形成的共识靠自报更晚事件伪装成 pre-event。
- `expectation_surprise` 的 Subject 与 consensus 必须同 metric、币种、单位、accounting basis 和目标期间，GAAP、adjusted 和 non-GAAP 不得跨口径比较。A 股 `expectation_gap` 按专用合同比较最新单季度 `deducted_attributable_net_profit` 乘 4 与事件前 `fy_attributable_net_profit` 全年共识；两者币种、单位和 PRC-GAAP 口径一致，季度必须完整落在共识目标年度内，分别使用合同规定的 basis。该跨指标、跨期间比较固定 `formal_surprise_status=N/A`，不得改装成同口径正式 beat/miss。

## 缺源与冲突

- 只有真正缺官方来源或官方值且已有完整 fallback 时，可以请求 `provisional`；必须记录缺失材料、fallback 完成状态和未来复查时间，退出码仍为非零。
- 已有官方 anchor、只是缺第二个 vendor 或可信次级来源，不是官方缺口，不能 provisional。
- Material 或 supporting 的数值偏差、币种、单位、期间、metric、合并范围、GAAP/non-GAAP、归母/扣非、basis、来源内部或派生链冲突只能 `blocked`，不得降格为 provisional。
- 弱来源与强来源冲突时不自动取平均。先解释并修正口径，再重新运行审计。

## 写入边界

本技能只读核验输入文件。改变外部 watchlist、组合、订单、消息、云文件或自动化仍须用户明确授权。
