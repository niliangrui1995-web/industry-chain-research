# A-share company tracking run status

- run_date_beijing: 2026-07-29
- run_started_at_beijing: 2026-07-29 01:01:40 +08:00
- run_finished_at_beijing: 2026-07-29 01:39:10 +08:00
- run_duration: 00:37:30
- automation_id: a-grok
- run_status: completed_pending_evening_rescan
- enabled_company_count: 13
- completed_company_count: 13
- failed_company_count: 0
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 8
- events_appended_count: 14
- announcement_window_checked: pending_evening_rescan
- announcement_query_window: 2026-07-21 to 2026-07-29
- trading_event_dates_checked: 2026-07-21 to 2026-07-28
- collection_scope: controller_open_web_only
- multi_agent_status: not_used_by_policy
- company_worker_queue: completed; controller processed all 13 enabled companies independently in watchlist order
- open_web_policy: Codex open-web per company; observation/discovery only; non-official results do not enter confirmed fact layer without official or issuer confirmation
- source_priority: official disclosure -> company-authored IR -> exchange trading data -> vendor cross-check -> reputable media -> open-web observation
- source_limitations: run completed before 20:00; 2026-07-29 evening disclosures require rescan; trading data complete only through 2026-07-28
- prompt_contract_version: 2026-07-27.1
- metadata_captured_at_beijing: 2026-07-29T01:32:58+08:00
- skill_revision: git:99ed4561a21ed617ea1430bf77e06e6aa69bd665
- skill_content_sha256: 223840607b9814d4d960aec4d2ab728ebf2e08be8b4d4cb82e8d659db8b9c3fb
- skill_tree_status: clean
- skills: a-share-company-tracking; a-share-disclosure-trading-data; financial-evidence-audit
- metadata_status: ok
- prewrite_snapshot_status: snapshot_created
- postwrite_validation_status: passed
- postwrite_validation_result: enabled_company_count=13; completion_table_count=13; new_event_count=14; workbook_round_trip=passed; event_append_only=passed
- validation_recovery_note: first validate call found the temporary snapshot missing and did not inspect business contents; event-prefix lengths, SHA-256 hashes and record counts were restored from byte-identical Git prefixes, then validator returned status=passed

## Company order current run

1. 002428.SZ 云南锗业
2. 603256.SH 宏和科技
3. 601869.SH 长飞光纤
4. 301511.SZ 德福科技
5. 002384.SZ 东山精密
6. 300308.SZ 中际旭创
7. 688498.SH 源杰科技
8. 688668.SH 鼎通科技
9. 300394.SZ 天孚通信
10. 002851.SZ 麦格米特
11. 000636.SZ 风华高科
12. 688048.SH 长光华芯
13. 301217.SZ 铜冠铜箔

## Material results

- Operating evidence strengthened: 云南锗业 InP contract; 源杰科技 H1 forecast with financial audit `PASS`.
- Capital/governance events: 东山精密 first repurchase; 中际旭创 H-share pricing and chairman buyback proposal; 鼎通科技 proposed conversion-price revision; 风华高科 board/secretary changes and proposed share cancellation; 铜冠铜箔 employee-director resignation.
- Trading events: 中际旭创、源杰科技、风华高科 dragon-tiger lists; 中际旭创、东山精密 block trades.
- Credible-media observation only: 长光华芯 chairman interview; 200G EML remains validation and planned mass-production timing is not treated as achieved.
- No new company-level hard event: 宏和科技、长飞光纤、德福科技、天孚通信、麦格米特.

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO/IR 7/21-7/29 hit重大合同 | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_beyond_official_contract | inp_contract_design_win_thesis_strengthened | 7/29晚间公告、实际采购量/交付/回款待核 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_open_web_only | SSE/CNINFO/IR 7/21-7/29 no_new_after_prior_entry | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_operating_signal | no_change | 7/29晚间公告及客户/收入拆分仍可能缺失 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_open_web_only | CNINFO/SSE/IR/HKEX 7/21-7/29 no_hit | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_media_restate_no_new_hard_signal | no_change | 7/29晚间公告及IR/HKEX异步更新风险 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/21-7/29 no_hit | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_operating_signal | no_change | 7/29晚间公告；HVLP分代/担保余额待核 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_open_web_only | CNINFO 7/21-7/29 hit首次回购 | 7/21-7/28 no_hit | 7/21-7/24 hit_4_small_flat_trades | pending_evening_rescan | searched_no_new_nonofficial_signal | repurchase_executed_fundamental_unchanged | 7/29晚间公告；累计回购及经营拆分待核 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_open_web_only | CNINFO/HKEX 7/21-7/29 hit发行定价及回购提议 | 7/28 hit_downside | 7/21-7/23 hit_5_flat_trades | pending_evening_rescan | searched_no_new_operating_signal | capital_events_and_higher_trading_risk | 7/29晚间公告；配售结果/回购审议待核 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_open_web_only | CNINFO/SSE/IR 7/21-7/29 hit_H1_forecast | 7/28 hit_downside | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_beyond_official_forecast | datacenter_h1_evidence_strengthened_and_higher_trading_risk | 7/29晚间公告；分产品/客户/现金流 N/A | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_open_web_only | CNINFO/SSE 7/21-7/29 hit转股价下修及评级 | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_operating_signal | convertible_bond_dilution_risk_higher_fundamental_unchanged | 7/29晚间公告；股东会/最终转股价待核 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/21-7/29 no_hit | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_operating_signal | no_change | 7/29晚间公告；1.6T/CPO拆分 N/A | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/21-7/29 no_hit | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_operating_signal | no_change | 7/29晚间公告；GB300订单/利润拆分 N/A | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_open_web_only | CNINFO/IR 7/21-7/29 hit治理及注销提议 | 7/27 hit_upside | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_operating_signal | governance_and_capital_change_higher_trading_heat | 7/29晚间公告；补选/股东会结果待核 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_open_web_only | SSE/CNINFO/IR 7/21-7/29 no_hit | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_management_interview_observation_only | management_claim_stage_update_thesis_unchanged | 7/29晚间公告；媒体口径待官方验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_open_web_only | CNINFO/SZSE 7/21-7/29 hit董事辞任 | 7/21-7/28 no_hit | 7/21-7/28 no_hit | pending_evening_rescan | searched_no_new_hard_signal | low_materiality_governance_change | 7/29晚间公告；补选及HVLP拆分待核 | not_used_by_policy |

## Final reconciliation

- enabled_watchlist_count: 13
- completion_table_count: 13
- missing_enabled_tickers: none
- duplicate_completion_tickers: none
- watchlist_order_match: true
- pending_or_refresh_needed_baselines: 0
- baseline_files_changed: 0
- state_updated_company_count: 8
- events_appended_count: 14
- financial_evidence_audit: PASS; publishable; 6/6 material checks
- project_files_only: true
- git_commit_or_push: false
- final_validation: passed
