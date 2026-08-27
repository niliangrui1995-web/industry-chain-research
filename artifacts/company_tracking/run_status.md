# A 股公司持续跟踪运行状态

- run_date: 2026-08-27
- run_started_at_beijing: 2026-08-27T20:32:45+08:00
- announcement_window_checked: T_and_T_plus_1
- trading_as_of: 2026-08-27
- run_status: completed
- run_finished_at_beijing: 2026-08-27T20:59:25+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 6
- events_appended_count: 9
- excel_last_update_date_synced_count: 13
- open_web_company_count: 13
- open_web_promoted_after_official_confirmation_count: 6
- multi_agent_status: not_used_by_policy
- snapshot_status: snapshot_created
- snapshot_path: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-27T20:48:35+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "223840607b9814d4d960aec4d2ab728ebf2e08be8b4d4cb82e8d659db8b9c3fb",
  "skill_revision": "git:577341bacc143006cfa92b414aa6acfdf91065c9",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-company-tracking",
    "a-share-disclosure-trading-data",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
~~~

## 来源限制与写入边界

- 本次北京时间 20:00 后按 T=2026-08-27 和 T+1=2026-08-28 逐家公司核验。T+1 排期文件若在 T 日晚间已可公开访问，则保留公告标示日期并记录实际可访问时点；不将预约、媒体转载或普通联网结果升级为正式事实。
- CNINFO 为公告主证据；深交所 annList 对深市公司为 HTTP 500，均作为 source_gap，不表述为无公告。沪市公司公告由 CNINFO 和上交所查询交叉。
- 深市龙虎榜和大宗交易以深交所公开信息为准；沪市交易二级接口 code=9201 空结果仅是厂商查询结果，不等同交易所官方零记录。
- 两份 H1 文件的收入、归母、扣非和经营现金流同比均经 financial-evidence-audit 复算 PASS；公司管理层关于客户、生态或产品路线的表述严格保留在 management claim 边界。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
|---|---:|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO 5；SZSE HTTP 500 source_gap | SZSE 官方 recordcount=0 | SZSE 官方 recordcount=0 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_1_event | T+1 标示日期与晚间可访问时点差异；InP 合同履约/回款待核验 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_open_web_only | CNINFO 4；SSE 4 | 东财二级 code=9201 空结果 | 东财二级 1 笔低重要性记录 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_2_events | 减持计划未完成；2.75% 解禁后实际供给待观察 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 光纤需求、海外项目和订单兑现待持续核验 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_open_web_only | CNINFO 1；SZSE HTTP 500 source_gap | SZSE 官方 recordcount=0 | SZSE 官方 recordcount=0 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_1_event | 权益分派不证明高端铜箔经营；客户与现金回款待核验 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | SZSE 官方 recordcount=0 | SZSE 官方 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市公告交叉源故障；光电互连及并购整合待核验 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_open_web_only | CNINFO 2；SZSE HTTP 500 source_gap | SZSE 官方 recordcount=0 | SZSE 官方去重后 1 笔低重要性记录 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_1_event | H 股资金用途、800G/1.6T 客户和收入拆分待核验 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_open_web_only | CNINFO 2；SSE 2 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_1_event | 项目手续、实际融资、开工和订单仍为证据缺口 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 连接器订单、毛利率和激励执行待核验 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | SZSE 官方 recordcount=0 | SZSE 官方 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高速光器件收入、产品节奏和客户待核验 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_open_web_only | CNINFO 9；SZSE HTTP 500 source_gap | SZSE 官方 recordcount=0 | SZSE 官方 recordcount=0 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_3_events | AIDC 客户/订单/收入拆分缺口；现金流与扣非需跟踪 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | SZSE 官方 recordcount=0 | SZSE 官方 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 8 月 28 日中报预约信息不替代正式公告；MLCC 景气待核验 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 诉讼调解履约、回款和经营影响待核验 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_open_web_only | CNINFO T+1 0；8 月 27 日 9 份已于早间入账 | SZSE 官方 recordcount=0 | SZSE 官方 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 当日早间 H1 事件已去重；HVLP 分代和现金流待核验 | not_used_by_policy |

## 验证

- postwrite_validation: passed
- validator_result: {"completion_table_count":13,"enabled_company_count":13,"event_append_only":"passed","new_event_count":9,"status":"passed","workbook_round_trip":"passed"}
