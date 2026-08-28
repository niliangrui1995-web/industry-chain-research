# A 股公司持续跟踪运行状态

- run_date: 2026-08-28
- run_started_at_beijing: 2026-08-28T20:32:05+08:00
- announcement_window_checked: T_and_T_plus_1
- announcement_dates_checked: 2026-08-28, 2026-08-29
- trading_as_of: 2026-08-27（最近完整交易日；并复查 2026-08-28 当日二级返回）
- run_status: completed
- run_finished_at_beijing: 2026-08-28T21:03:12+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 4
- events_appended_count: 6
- excel_last_update_date_synced_count: 13
- open_web_company_count: 13
- open_web_promoted_after_official_confirmation_count: 2
- multi_agent_status: not_used_by_policy
- snapshot_status: snapshot_created
- snapshot_path: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-28T20:40:12+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "223840607b9814d4d960aec4d2ab728ebf2e08be8b4d4cb82e8d659db8b9c3fb",
  "skill_revision": "git:f2d12ead502c8805c4308e46afb0fd76e6e80606",
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

- 本次北京时间 20:00 后按 T=2026-08-28 与 T+1=2026-08-29 逐家公司核验；源杰科技的 T+1 标示日期文件于 8 月 28 日晚间可访问，保留公告日期与实际可访问时点的差异。
- CNINFO 为公告主证据。深交所 annList 对深市公司返回 HTTP 500，作为 `source_gap`；上交所查询返回 200 但本次未提取到可消费的发行人行，CNINFO 仍为主证据。
- 龙虎榜与大宗交易先查最近完整交易日 2026-08-27，再查 8 月 28 日二级返回。东方财富二级 `code=9201` 空结果不等于交易所官方零记录；宏和科技和中际旭创的平价大宗交易均明确标为 `confirmed_secondary`。
- 联网观察每家公司单独查询。非官方结果仅作线索；未将媒体、行情或泛行业叙事升级为客户、订单、收入或行业硬事实。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
|---|---:|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO 5（均已前轮入账）；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；InP合同履约/回款待核验 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_open_web_only | CNINFO 3（均已入账）；SSE 200未提取发行人行 | 东财二级 8/27、8/28 code=9201 空结果 | 8/27去重后1笔平价二级记录；8/28空 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_1_event | 交易所原始大宗记录未回读；解禁后供给待观察 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_open_web_only | CNINFO 0；SSE 200未提取发行人行 | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 光纤需求、海外项目和订单兑现待核验 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；高端铜箔客户和回款待核验 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 光电互连、并购整合与客户订单待核验 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 8/27 2笔平价机构二级记录；8/28空 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_1_event | 深交所原始大宗记录未回读；客户和收入拆分待核验 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_open_web_only | CNINFO 7（H1、分红等新增）；SSE 200未提取发行人行 | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_2_events | 客户、单产品收入、200G验证与回款待核验 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_open_web_only | CNINFO 0；SSE 200未提取发行人行 | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 连接器订单、毛利率和激励执行待核验 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高速光器件收入、物料与客户待核验 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_open_web_only | CNINFO 9（均已前轮T+1入账）；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | AIDC客户/订单/收入拆分及现金流待跟踪 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_open_web_only | CNINFO 9（H1、减值等新增）；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_promoted_after_official_confirmation | updated_2_events | AI MLCC拆分、减值、存货和现金回款待核验 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_open_web_only | CNINFO 0；SSE 200未提取发行人行 | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 诉讼调解履约、回款与200G EML验证待核验 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_open_web_only | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/27、8/28 code=9201 空结果 | 东财二级 8/27、8/28 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | HVLP分代、现金流、分红与财务负责人待核验 | not_used_by_policy |

## 验证

- postwrite_validation: passed
- validator_result: {"completion_table_count":13,"enabled_company_count":13,"event_append_only":"passed","new_event_count":6,"status":"passed","workbook_round_trip":"passed"}
