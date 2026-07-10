---
name: a-share-disclosure-trading-data
description: Verify A-share official disclosures and trading events from CNINFO, SSE, SZSE, BSE, company IR, investor-relations records, dragon-tiger lists, block trades, and T/T+1 evening announcement windows. Use for 公告核验、巨潮、交易所披露、投资者关系、龙虎榜、大宗交易、监管函或晚间公告漏检. It supplies evidence and trading context, not stock recommendations.
---

# A-Share Disclosure And Trading Data

为当前研究或公司跟踪提供可追溯的 A 股公告与交易事件。不要把本技能变成通用公司分析或选股流程。

## 来源优先级

1. CNINFO、SSE、SZSE、BSE、公司公告和公司 IR 原文；
2. 交易所龙虎榜、大宗交易、异常交易、监管或问询记录；
3. 官方投资者关系活动记录；
4. 可靠数据商或媒体作二次确认；
5. 社交、论坛、Grok/X 和模型摘要只作线索。

标题、摘要或行情厂商原因揭秘不能替代公告原文。

## 公告窗口

- 北京时间 20:00 前：检查当日公告日期；日结任务记录 `pending_evening_rescan`。
- 北京时间 20:00 及以后：同时检查 `T` 和 `T+1` 公告日期。
- 用户指出漏项时：按公司名、ticker 和 aliases 重扫可疑窗口。

记录：

`announcement_window_checked = T_only | T_and_T_plus_1 | pending_evening_rescan | failed_with_reason`

## 规范化字段

- ticker 使用 `600xxx.SH`、`000xxx.SZ`、`688xxx.SH`、`8xxxxx.BJ` 等明确后缀；
- 区分公告日期与事件日期；
- 保留原始 URL 和平台；
- `source_type` 使用 `official_announcement`、`exchange_disclosure`、`investor_relations`、`dragon_tiger`、`block_trade`、`reputable_media`、`open_web_fallback` 或 `social_observation`；
- `verification_status` 使用 `confirmed_official`、`confirmed_secondary`、`observation_only`、`contradicted` 或 `source_gap`。

## 交易事件边界

龙虎榜提取上榜原因、买卖席位和金额、机构/量化/北向等线索，以及是否与已确认催化一致。大宗交易提取价格、数量、金额、折溢价和席位；结合成交额或流通盘判断重要性，不解读小额普通交易。

TDX 或其他行情工具的涨跌停、封单、连板、板型、概念和原因揭秘标为 `secondary_trading_context`。它们可以解释市场反应或指导公告检索，不能确认订单、客户、产品暴露或业绩影响。

## 输出

返回紧凑证据表：

| ticker | name | date | source_type | title/event | source | verification_status | impact_hint | next_check |
|---|---|---|---|---|---|---|---|---|

用于公司跟踪时，只把有实质意义的行追加到 `events.jsonl`；`state.md` 和日报只记录真正变化。
