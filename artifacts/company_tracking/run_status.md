# A 股公司持续跟踪运行状态

- run_date: 2026-08-27
- run_started_at_beijing: 2026-08-27T00:06:59+08:00
- announcement_window_checked: T_and_T_plus_1
- trading_as_of: 2026-08-26
- run_status: completed
- run_finished_at_beijing: 2026-08-27T00:31:53+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 1
- events_appended_count: 4
- excel_last_update_date_synced_count: 13
- open_web_company_count: 13
- open_web_promoted_after_official_confirmation_count: 1
- multi_agent_status: not_used_by_policy
- snapshot_status: snapshot_created
- snapshot_path: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-27T00:21:00+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "223840607b9814d4d960aec4d2ab728ebf2e08be8b4d4cb82e8d659db8b9c3fb",
  "skill_revision": "git:8c2fae139eda312c06f55fea4ded3c08fff878eb",
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

- CNINFO topSearch/query 返回 HTTP 500；已以 hisAnnouncement/query 精确公司名和日期窗口回退。301217.SZ 由该正式路径确认 9 份当日公告。
- 深交所 annList 对深市公司返回 HTTP 500；不将其写成无公告。
- 东方财富二级龙虎榜及大宗交易查询对 2026-08-26 返回 code=9201、返回数据为空；不等同于交易所官方零记录。
- 301217.SZ 已追加 4 条符合五维归因字段的 events.jsonl；其余公司无新增可升级硬事实，历史账本未改写。
- Excel 仅更新 enabled 行的 last_update_date，并已逐项回读为 2026-08-27。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；中报实际披露待复扫 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端电子级玻纤布客户和放量仍缺官方证据 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 光纤需求与海外项目兑现待持续核验 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；加工费和客户认证待核验 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 光电互连和并购整合仍需公告原文验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 8月25日小额大宗交易已去重；800G/1.6T待核验 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 8月27日股东会决议、项目与授信待核验 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 激励落地、连接器订单与毛利率待核验 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 8月26日激励对象核查已去重；高速光器件待核验 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 后续中报、算力电源与现金流待核验 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 后续中报、MLCC景气与产能利用率待核验 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_open_web_only | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 诉讼调解履约、回款与减值转回待核验 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_open_web_only | CNINFO 9 已入账；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_4_events | HVLP分代、现金流、财务负责人和分红决议待核验 | not_used_by_policy |

## 验证

- postwrite_validation: passed
- validator_result: {"completion_table_count":13,"enabled_company_count":13,"event_append_only":"passed","new_event_count":4,"status":"passed","workbook_round_trip":"passed"}
