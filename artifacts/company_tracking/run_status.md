# A-share company tracking run status

- run_date_beijing: 2026-07-13
- run_started_at_beijing: 2026-07-13 20:33:18 +08:00
- run_finished_at_beijing: 2026-07-13 20:53:06 +08:00
- automation_id: a-grok
- run_status: completed
- enabled_company_count: 11
- completed_company_count: 11
- failed_company_count: 0
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 2
- events_appended_count: 2
- announcement_window_checked: T_and_T_plus_1
- announcement_query_window: 2026-07-13 to 2026-07-14; weekend catchup 2026-07-12
- trading_event_date_checked: 2026-07-13
- collection_scope: controller_open_web_only
- multi_agent_status: not_used_by_policy
- company_worker_queue: cancelled_by_policy
- open_web_policy: Codex open-web search only; no browser plugin, external browser, third-party web model, or social-search tool
- source_priority: official disclosure -> company-authored investor-relations record -> exchange/trading data -> reputable media -> open-web observation pool
- source_limitations: 中际旭创 2026-07-12 正式 IR 文档取得公告镜像并经可信媒体交叉，但 CNINFO 主站公司名/代码查询未返回该记录；已标注 primary-link source gap

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

## Company task blocks

- 11 家 enabled 公司均按 watchlist 顺序建立独立任务块；每块均读取本公司 baseline、state 和 recent events，再分别执行公告、龙虎榜、大宗交易和最近 24 小时 open-web 检查。
- 20:00 后硬门已完成：全部公司核验公告日期 2026-07-13（T）和 2026-07-14（T+1），并补扫上一轮后的 2026-07-12 周末窗口。
- CNINFO 公司名优先、ticker 复核；返回结果按 secCode/secName 过滤。交易事件按公司代码独立查询，不使用多公司泛查询。
- 云南锗业新增 1 条 CNINFO 官方业绩预告；中际旭创新增 1 条正式 IR 文档事件。其余公司无达到事件账本门槛的新增事项。
- 2026-07-13 全部 enabled 公司无龙虎榜命中。仅中际旭创有 1 笔低重要性大宗交易，因规模过小未追加 events.jsonl。
- 未使用子智能体、worker、外部浏览器、浏览器插件、第三方网页模型或社交搜索工具。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_official_earnings_forecast | controller_open_web_only | CNINFO T+1 hit: 2026年半年度业绩预告 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | searched | upgraded_to_watch_earnings_turnaround | InP/GaAs分拆、客户、订单、良率、6英寸量产、产品毛利率与现金流待验证 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | Low CTE/T-glass客户、订单、收入占比、毛利率及减持链仍待验证 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | 光纤价格、扩产周期、数据中心产品订单、海外收入和毛利率仍待验证 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | 减持归属、定增审核、HVLP/RTF客户、订单、收入占比和毛利率仍待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14; 互动问答无实质增量 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | AI PCB/索尔思客户、订单、收入、毛利率和资本开支兑现仍待验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_investor_relations_update | controller_open_web_only | CNINFO no issuer hit; 7/12 formal IR document mirror captured | 2026-07-13 no_hit | 0.25万股/232.47万元低重要性命中，未入账本 | T_and_T_plus_1 | searched | updated_order_visibility_and_supply | 主站IR直链、订单金额、客户结构、出货拆分、毛利率与现金流待验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | 200G EML/CW客户扩散、收入占比、良率和毛利率仍待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | 高速连接器、液冷客户订单、产能利用率和毛利率仍待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | 泰国产能利用率、CPO/1.6T收入与毛利率、客户及H股节点待验证 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14; 金刚石设备互动问答与跟踪主线无关 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | AIDC具名客户、订单金额、收入占比、毛利率、交付节奏和H股节点待验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-12/13/14 | 2026-07-13 no_hit | 2026-07-13 no_hit | T_and_T_plus_1 | no_signal | no_change | 高端/AI MLCC收入、ASP、毛利率、现金流待半年报验证；英伟达边界不变 | not_used_by_policy |

## Reconciliation

- enabled_watchlist_count: 11
- completion_table_count: 11
- completed_enabled_count: 11
- missing_enabled_tickers: none
- duplicated_completion_tickers: none
- watchlist_order_preserved: yes
- baseline_pending_or_refresh_needed: none
- all_company_baseline_state_events_read: yes
- company_worker_queue: cancelled_by_policy
- multi_agent_status: not_used_by_policy
- watchlist_last_update_date: 2026-07-13 for all enabled rows
