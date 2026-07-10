---
name: a-share-company-tracking
description: Maintain the 产业链投研 A-share watchlist and durable per-company baseline, state, events, daily report, and run status. Use for watchlist 日更、公司持续跟踪、baseline 补建、state/events 更新、completion table 核对或晚间公告复扫. This skill writes only the named project tracking artifacts and does not make external watchlist or trading changes.
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

## 硬门

1. 把每家公司作为独立工作单元，完成后再汇总；不得用一次泛查询替代逐公司核验。
2. 官方公告、交易所、CNINFO 和公司 IR 才能更新确认状态；open-web、社交和模型摘要进入观察池，除非被可靠来源确认。
3. 北京时间 20:00 前运行时记录 `pending_evening_rescan`；20:00 及以后检查公告日期 `T` 和 `T+1`。
4. completion table 必须覆盖全部 enabled 公司；单家公司失败时记录原因并继续其余公司。
5. 行情、龙虎榜、大宗交易和概念原因只改变交易结构判断，不证明业务质量。
6. 是否使用子代理由当前任务或自动化 prompt 决定；本技能不建立额外固定代理链。

公告、龙虎榜和大宗交易的字段与证据规则按需使用 `a-share-disclosure-trading-data`。

## 基线

对 `baseline_status` 为 `pending`、`refresh_needed` 或空值的公司：

- 确认上市主体、业务分部、产品、产业链位置和客户/供应商/认证信息；
- 核对近期财报、公告、IR、产能、项目、融资、并购和主要风险；
- 区分真实受益证据与市场叙事；
- 分开记录基本面质量、业绩弹性和交易弹性；
- 创建或更新 `baseline.md`、`state.md`、`events.jsonl`，再更新 watchlist 日期与状态。

## 日常更新

对每家公司：

1. 读取既有 baseline、state 和近期 events。
2. 检查官方公告、交易所/CNINFO、IR 和配置的官方来源提示。
3. 应用 T/T+1 公告窗口规则；必要时核对最近交易日龙虎榜和大宗交易。
4. 仅在任务要求当前消息时做该公司独立的 24 小时 web 发现，并记录 `searched`、`no_signal` 或 `failed`。
5. 把有实质意义的新事件追加为单行 JSON：`date`、`ticker`、`name`、`source_type`、`source_name`、`title`、`url`、`summary`、`impact_hint`、`verification_status`。
6. 只有 thesis、风险、证据缺口或下一步问题发生变化时才更新 `state.md`。
7. 生成日报、run status 和逐公司 completion table，并对 enabled watchlist 做最终对账。

## 输出

最终对话只总结实质变化、重要公告/交易事件、相对基线的变化和下一步问题。路径、队列状态和逐公司完成字段写入文件，除非它们会影响用户决策，否则不堆进对话。
