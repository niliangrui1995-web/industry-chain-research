# A-share company tracking run status

- run_date_beijing: 2026-07-16
- run_started_at_beijing: 2026-07-16 20:32:18 +08:00
- run_finished_at_beijing: 2026-07-16 21:35:25 +08:00
- automation_id: a-grok
- run_status: completed
- enabled_company_count: 13
- completed_company_count: 13
- failed_company_count: 0
- baseline_created_or_refreshed_count: 2
- state_updated_company_count: 7
- events_appended_count: 8
- announcement_window_checked: T_and_T_plus_1
- announcement_query_window: 2026-07-16 to 2026-07-17
- trading_event_dates_checked: 2026-07-16
- collection_scope: controller_plus_bounded_single_company_subagents
- multi_agent_status: used_by_explicit_user_permission
- company_worker_queue: completed; original 11-company daily run completed, then 2 user-added companies processed as isolated baseline work units with 3 bounded read-only subagent checks and controller-only writeback
- open_web_policy: Codex open-web per company; observation/discovery only; non-official results require official or issuer-source confirmation before fact status
- source_priority: official disclosure -> company-authored IR -> exchange trading data -> vendor cross-check -> reputable media -> open-web observation
- source_limitations: CNINFO returned one intermittent 504 during final rescan but succeeded on retry; SSE/HKEX static pages can refresh with delay; final CNINFO/exchange/vendor rescan found no unprocessed issuer or trading hit

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

- Official earnings forecast: 鼎通科技（T+1；收入/利润高增，112G/224G 量产，液冷仍为小批试产）。
- Official investor relations: 云南锗业（InP 认证/量价/项目/出口）；东山精密（光芯片 IDM/扩产/良率阶段）。
- Historical official IR backfill: 麦格米特（GB300 批量订单及 2026Q1 业绩贡献；客户与金额仍未披露）。
- Dragon-tiger event: 麦格米特（跌幅偏离值 -8.49%，成交 53.47 亿元）。
- Block-trade event: 中际旭创（5 笔平价交易，52.64 万股、5.859166 亿元，买方均为机构专用）。
- No material change: 宏和科技、长飞光纤、德福科技、源杰科技、天孚通信、风华高科。
- Baseline created: 长光华芯（高功率单管基本盘；100G EML 有收入但低毛利）、铜冠铜箔（HVLP/RTF 有批量供货；HVLP 分代和 AI PCB 边界已建立）。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | controller_official_plus_open_web | CNINFO: 7/16 issuer IR | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | strengthened_inp_certification_volume_price_export_execution | 客户名称/订单/良率/6英寸量产 N/A | controller |
| 603256.SH | 宏和科技 | 2 | completed | subagent_read_only_official_plus_open_web | CNINFO/SSE/IR: no_new_hit | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | no_change | Low CTE/T-glass 分产品证据仍缺 | used_by_explicit_user_permission |
| 601869.SH | 长飞光纤 | 3 | completed | subagent_read_only_official_plus_open_web | CNINFO/SSE/HKEX/IR: no_new_hit | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | no_change | T+1 静态页可能有刷新延迟 | used_by_explicit_user_permission |
| 301511.SZ | 德福科技 | 4 | completed | subagent_read_only_official_plus_open_web | CNINFO/SZSE/IR: no_new_hit | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | no_change | 剩余减持额度仍需跟踪 | used_by_explicit_user_permission |
| 002384.SZ | 东山精密 | 5 | completed | controller_official_plus_open_web | CNINFO: 7/15 IR disclosed 7/16 | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | strengthened_optical_idm_capacity_yield_stage_without_quantification | 产能/良率/订单/AI PCB利润 N/A | controller |
| 300308.SZ | 中际旭创 | 6 | completed | controller_official_plus_open_web | CNINFO/SZSE/IR: no_new_hit | 7/16 no_hit | 7/16 hit_5_flat_trades_5.859166bn | T_and_T_plus_1 | no_signal | higher_flat_institutional_block_turnover | 大宗交易不作经营解读 | controller |
| 688498.SH | 源杰科技 | 7 | completed | controller_official_plus_open_web | CNINFO/SSE/IR: no_new_hit | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | no_change | 200G EML 量产与客户 N/A | controller |
| 688668.SH | 鼎通科技 | 8 | completed | controller_official_plus_open_web | CNINFO/SSE: T+1 H1 forecast | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | strengthened_h1_profit_and_112g_224g_mass_production | 液冷仅小批试产；分产品拆分 N/A | controller |
| 300394.SZ | 天孚通信 | 9 | completed | controller_official_plus_open_web | CNINFO/SZSE/IR: no_new_hit | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | no_change | 1.6T/CPO 与客户结构仍需量化 | controller |
| 002851.SZ | 麦格米特 | 10 | completed | subagent_read_only_official_plus_open_web | CNINFO/SZSE: existing 7/16 dividend; 4/29 IR backfill | 7/16 hit_drop_deviation_minus_8_49pct | 7/16 no_hit | T_and_T_plus_1 | searched_lhb_media_no_new_operating_signal | gb300_batch_order_backfill_and_higher_downside_crowding | 客户/订单金额数量/AIDC利润拆分 N/A | used_by_explicit_user_permission |
| 000636.SZ | 风华高科 | 11 | completed | subagent_read_only_official_plus_open_web | CNINFO/SZSE/company IR: no_new_hit | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | no_change | AI MLCC 公司级兑现仍缺 | used_by_explicit_user_permission |
| 688048.SH | 长光华芯 | 12 | completed_with_baseline_created | subagent_research_plus_controller_writeback | SSE/CNINFO/company IR: no 7/16-7/17 hit; 7/10 inquiry integrated | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | full_baseline_created_100g_eml_revenue_confirmed_low_margin | 客户名称/200G EML量产/扩产良率/扣非盈利 N/A | used_by_explicit_user_permission |
| 301217.SZ | 铜冠铜箔 | 13 | completed_with_baseline_created | subagent_research_plus_controller_writeback | CNINFO/SZSE/company IR: no 7/16-7/17 hit | 7/16 no_hit | 7/16 no_hit | T_and_T_plus_1 | no_signal | full_baseline_created_hvlp_supply_confirmed_generation_boundary | HVLP分代收入毛利/具名客户/专属产能 N/A | used_by_explicit_user_permission |

## Final reconciliation

- enabled_watchlist_count: 13
- completion_table_count: 13
- missing_enabled_tickers: none
- duplicate_completion_tickers: none
- watchlist_order_match: true
- pending_or_refresh_needed_baselines: 0
- project_files_only: true
- git_commit_or_push: false
