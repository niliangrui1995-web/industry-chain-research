---
name: a-share-company-tracking
description: 维护本项目 A 股 watchlist 日更、公司基线、thesis 漂移、state/events 和晚间公告复扫。用于持续跟踪与状态写回；单次公司问答不触发，不修改外部 watchlist 或交易状态。
---

# A-Share Company Tracking

维护项目内的 A 股公司真相文件。只在用户要求跟踪、日更、基线或状态写回时使用；单次公司问答不需要加载本技能。

## 真相路径

- Watchlist：`watchlists/a_share_company_watchlist.xlsx`
- 公司目录：`artifacts/company_tracking/<ticker>/`
- 日报：`artifacts/company_tracking/YYYY-MM-DD.md`
- 运行状态：`artifacts/company_tracking/run_status.md`
- 自动化合同：`docs/company_tracking/A_SHARE_COMPANY_TRACKING_PROMPT.md`

只处理 `enabled=Y`。保留工作簿原格式和字段；不要触碰未命名的状态文件。

## 按任务读取合同

- 执行完整 watchlist 日更或跟踪自动化时，在业务采集或写入前读取[公司跟踪运行合同](../../../docs/company_tracking/A_SHARE_COMPANY_TRACKING_PROMPT.md)，按其中的命令先完成元数据预检，再于工作簿或事件写入前建立 snapshot，最后运行 validator；只有 `status=passed` 才可报告整轮完成。无新增、来源失败和提前结束也遵守合同中的状态记录要求。
- 单公司基线补建或指定状态的局部修改只处理用户要求的范围，保留来源、事件追加和工作簿回读检查；不自动扩展为全部 enabled 公司日更，也不创建调度任务。

## 硬门

1. 把每家公司作为独立工作单元，完成后再汇总；不得用一次泛查询替代逐公司核验。
2. 官方公告、交易所、CNINFO 和公司 IR 才能更新确认状态；open-web、社交和模型摘要进入观察池，除非被可靠来源确认。
3. 执行当日日更或公告复扫时，北京时间 20:00 前运行记录 `pending_evening_rescan`；20:00 及以后检查公告日期 `T` 和 `T+1`。
4. 整轮日更的 completion table 必须覆盖全部 enabled 公司；局部基线或状态修改只核对本次指定公司。单家公司失败时记录原因并继续本次范围内的其余公司。
5. 行情、龙虎榜、大宗交易和概念原因只改变交易结构判断，不证明业务质量。
6. 是否使用子代理由当前任务或自动化 prompt 决定；本技能不建立额外固定代理链。
7. 日更必须区分 `fact_change`、`management_claim_change`、`estimate_change`、`valuation_price_change`、`wording_only` 和 `evidence_gap`；不得把表述、预测或价格变化写成公司硬事实。
8. 没有新的官方或等价可核验硬证据，不得强化或弱化基本面 thesis；可单独更新管理层主张、外部预期、估值/价格、研究置信度或证据缺口。
9. 每条实质事件都要检查公司、监管、同行、行业和市场五个归因维度，分别记录证据、反证、置信度和持续窗口；不知原因时保持未知。
10. 本技能不新增自动买卖、加减仓、止损、目标价或外部组合写入。
11. 产品商业化阶段只允许 `rd_plan | sampling | validation | design_win | qualification | mass_production | shipment | revenue | profit_cashflow`；送样、验证、design win 或认证只更新对应阶段，不得自动推导量产、出货、收入或利润。

公告、龙虎榜和大宗交易的字段与证据规则按需使用 `a-share-disclosure-trading-data`。
补建基线、判断 thesis 漂移或对事件做归因时，读取 [references/thesis-drift-event-attribution.md](references/thesis-drift-event-attribution.md)。

## 基线

对 `baseline_status` 为 `pending`、`refresh_needed` 或空值的公司：

- 确认上市主体、业务分部、产品、产业链位置和客户/供应商/认证信息；
- 核对近期财报、公告、IR、产能、项目、融资、并购和主要风险；
- 区分真实受益证据与市场叙事；
- 分开记录基本面质量、业绩弹性和交易弹性；
- 建立可证伪核心假设，为每条写明因果链、支持与反证、可观测信号、失效条件和监测窗口；
- 建立管理层承诺账本和资本配置账本；只把具体、可衡量、有期限的承诺计入兑现判断，愿景和宣传不进入分母；
- 对每个重要产品/受益逻辑记录 `commercialization_stage`、`stage_evidence`、`stage_evidence_date`、`stage_source` 和 `revenue_materiality`；阶段缺证据时保持 `evidence_gap`，不跨级；
- 创建或更新 `baseline.md`、`state.md`、`events.jsonl`，再更新 watchlist 日期与状态。

## 日常更新

对每家公司：

1. 读取既有 baseline、可证伪假设、管理层承诺/资本配置账本、state 和近期 events。
2. 检查官方公告、交易所/CNINFO、IR 和配置的官方来源提示。
3. 应用 T/T+1 公告窗口规则；必要时核对最近交易日龙虎榜和大宗交易。
4. 仅在任务要求当前消息时做该公司独立的 24 小时 web 发现，并记录 `searched`、`no_signal` 或 `failed`。
5. 把有实质意义的新事件追加为单行 JSON；除基本来源字段外，至少记录 `change_type`、`thesis_effect`、`hard_evidence_new`、`previous_commercialization_stage`、`new_commercialization_stage`、`stage_evidence`、`stage_evidence_date`、`stage_source`、`revenue_materiality`、`attribution_dimensions`、`evidence`、`counterevidence`、`confidence`、`persistence_window` 和 `next_validation`。
6. 先应用基本面 thesis 更新硬门，再更新 `state.md`；只有新硬证据改变核心因果链、可证伪假设或失效条件时，`thesis_effect` 才可为 `strengthened` 或 `weakened`，否则为 `unchanged` 或 `not_assessable`。阶段进展只能改变与该阶段直接相关的假设，不能自动升级下一阶段或财务贡献。
7. 生成日报、run status 和逐公司 completion table，并对 enabled watchlist 做最终对账。

## 输出

最终对话只总结实质变化、重要公告/交易事件、相对基线的变化和下一步问题。分开硬事实、管理层主张、外部预期、估值/价格、措辞和证据缺口；若基本面 thesis 未变，明确写未变。不从跟踪结果自动生成交易动作。路径、队列状态和逐公司完成字段写入文件，除非它们会影响用户决策，否则不堆进对话。
