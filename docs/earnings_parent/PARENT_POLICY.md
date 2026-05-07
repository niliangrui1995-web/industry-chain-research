# 寡头财报母任务运行政策

本文是自动化 `22-30-2` 的详细政策文件。母任务的 live prompt 只保留执行骨架；遇到歧义时，以本文和 `CHILD_PROMPT_TEMPLATE.md` 为准。

## 角色和边界

- 母任务只读取紫金研选寡头财报日历，并为严格未来 72 小时内需要启动分析的上市公司创建、更新或暂停独立的一次性“财报电话会深挖”子任务。
- 母任务不得调用或执行 `earnings-call-investment-analyst`；该 skill 只允许单公司子任务运行时调用。
- 所有母任务和子任务只在 `D:\vcp_hunter\产业链投研` 运行。
- `D:\vcp_hunter\紫金研选` 只作为财报日历数据源和官方电话会时间写回目标。
- 单公司子任务运行时必须使用项目本地 skill：`D:\vcp_hunter\产业链投研\skills\earnings-call-investment-analyst`。
- 读取或写回紫金研选代码时，优先使用 `D:\vcp_hunter\紫金研选\.venv\Scripts\python.exe`。若从产业链投研启动 Python，必须先把 `D:\vcp_hunter\紫金研选` 插入 `sys.path` 后再 import `domains.global_earnings_calendar.service`。

## 硬停条件

出现以下情况时停止受影响操作并报告，不得创建或更新受影响子任务：

- `D:\vcp_hunter\紫金研选`、`D:\vcp_hunter\产业链投研`、或项目本地 `earnings-call-investment-analyst` skill 缺失。
- venv Python 无法 import `requests`、`GlobalEarningsCalendarService` 或 `EarningsCalendarEvent`，报告 `environment_preflight_failed`。
- 候选事件出现 ticker/company 不一致、ticker 后缀和 market 不一致、同 ticker 多公司、同 company 冲突 ticker、相邻串位或反向错配信号，且联网核验后仍无法解释，报告 `candidate_mapping_failed`。
- 台湾 PCB 回归硬门失败：Wus 必须是 `2316.TW`，Compeq 必须是 `2313.TW`，Tripod 必须是 `3044.TW`。若本轮涉及台湾 PCB 且发现错配、重复、缺失或无法确认，报告 `ticker_company_mapping_failed`。
- 同一 `TASK_KEY` 或兜底同 ticker + report_date 命中多场明显冲突财报，报告 `duplicate_key_ambiguous`。
- 子任务 rrule 无法保持 `DTSTART + RRULE:FREQ=WEEKLY;...;COUNT=1`，报告 `child_rrule_update_failed`。
- 官方电话会、webcast、results briefing 或 investor meeting 时间已经核验，但无法在 child header 保留官方时间、URL、时区和 `call_time_source_type`，报告 `writeback_verify_failed`，不得创建或更新受影响子任务。
- 任何操作需要手工写 `confirmed_events.json`、手工执行 SQLite SQL、写 `kv_store.trade_dates`、调用 `MarketCalendar.load_trade_dates()`、`MarketCalendar._schedule_trade_dates_refresh()` 或其他交易日历刷新路径时，停止并报告 unsafe write path。

## 读取和候选范围

- 主读取必须调用 `GlobalEarningsCalendarService().load_events(today=dt.date.today() - dt.timedelta(days=1), lookahead_days=5, allow_network=False)`。
- 最终只处理 `now <= planned_child_start_beijing <= now + 72 hours` 的事件。
- 读取窗口必须允许 report_date 为北京时间今天前一日的事件进入候选池，用于覆盖“北京时间今天凌晨/上午 = 美股前一交易日盘后”的跨日财报。
- 不得因为 `report_date < dt.date.today()` 直接跳过；只有 `planned_child_start_beijing < now` 才能跳过候选处理。
- SQLite raw JSON 只作诊断兜底，不得替代 `load_events()` 主读取。
- 只有缓存缺失、为空、明显过期、关键 ticker 缺失、或用户明确要求刷新时，才允许调用 `refresh_events(lookahead_days=90)`。刷新只允许写入 `kv_store.global_earnings_calendar`，不得触碰 `trade_dates` 或 MarketCalendar 交易日历刷新路径。

## 候选校验和去重

- 每条事件用 `ticker + report_date + fiscal_period` 生成 `TASK_KEY`。
- 查找已有子任务时扫描 `$CODEX_HOME\automations\*\automation.toml`，按以下方式识别：
  - name 包含 `财报电话会深挖`
  - prompt 中含 `TASK_KEY:`
  - 同一 `ticker + report_date + fiscal_period`
  - 兜底同一 `ticker + report_date`
- 必须兼容旧 id `earnings-call-*` 和新 id `ec-*`。
- 同一 `TASK_KEY` 已存在时只能更新，不得重复创建。
- 若 fiscal_period 文本从空值变为 `Mar/2026`、`FY2026 Qx` 等导致 TASK_KEY 未命中，但 ticker + report_date 相同且公司、市场、计划时间或事件来源无明显冲突，视为同一任务并更新已有子任务。

## 官方来源和写回

- 本地 `beijing_time` 只有在 `status=confirmed` 且存在官方 `conference_url` 或官方 `call_time_source_url` 时，才视为已确认电话会或 webcast 时间。
- 缺少可信官方电话会时间的事件，必须联网查询 official earnings call / webcast / results call 时间。
- 可写回的官方证据只包括公司 IR、SEC、交易所公告、或官方 IR 页面明确链出的 webcast。
- Yahoo、Nasdaq、Alpha Vantage、第三方财经日历和媒体转载只能作为线索，不得写入 confirmed events，不得作为 `official_call_plus_3h` 依据。
- 如果只查到财报发布时间、第三方时间、或查不到电话会时间，不写本地，报告 `call_time_not_found`、`third_party_unconfirmed` 或 `no_call_announced`。
- 官方电话会时间必须保留 `original_call_time_text`、`original_timezone`、`call_time_source_url`、`call_time_source_type`。
- 写回 `beijing_time` 必须使用完整北京时间格式 `YYYY-MM-DD HH:MM`。
- 必须用 IANA 时区和 DST 规则换算北京时间：ET=`America/New_York`，PT=`America/Los_Angeles`，JST=`Asia/Tokyo`，KST=`Asia/Seoul`，HKT=`Asia/Hong_Kong`，CST/China/Taiwan=`Asia/Shanghai`。
- 官方电话会时间写回只能调用 `GlobalEarningsCalendarService().upsert_confirmed_event(EarningsCalendarEvent(...))`。
- 写回后必须立即用 `load_events(..., allow_network=False)` 验证对应 ticker 可读，且 company/ticker/status/beijing_time/call_time_source_type 与写入值一致。
- 若官方电话会、webcast、results briefing 或 investor meeting 时间已由官方来源核验，但 `upsert_confirmed_event()` 抛出 `ConfirmedEventWriteError`、写后无法读回、或读回字段不一致，不得降级为默认代理排期。此时只允许在 child prompt header 中保留已核验的官方时间、原始时间文本、IANA 时区、URL 和 `call_time_source_type`，`Schedule basis` 仍写 `official_call_plus_3h`，并在 `Calendar caveat` 中追加 `writeback_failed_not_persisted`；最终报告 `confirmed_event_write_failed` 或 `writeback_failed_not_persisted`。如果这些官方证据不能被完整保留，停止受影响事件并报告 `writeback_verify_failed`。

## 排期规则

- 有可信官方电话会、webcast、results briefing 或 investor meeting 北京时间：子任务开始时间 = 该官方事件北京时间 + 3 小时，计划依据写 `official_call_plus_3h`。
- 没有可信官方电话会、webcast、results briefing 或 investor meeting 时间：计划依据写 `default_proxy_not_call_time`，不写本地确认时间，不得写 `official_call_plus_3h`。
- 默认代理排期必须确定：
  - US 盘后或只知道盘后财报日期 -> 财报日次日北京时间 08:00。
  - US 盘前 -> 财报日北京时间 23:30。
  - TW/HK/JP/KR 日期-only -> 财报日北京时间 20:00。
  - 欧洲日期-only -> 财报日次日北京时间 02:30。
- 如果默认代理排期落在严格未来 72 小时内，必须创建或更新子任务，不得因为 status=estimated、source=Yahoo/Nasdaq、conference_url 为空、beijing_time 为空或缺少官方 call time 而跳过。

## Guardrail helper

若 `D:\vcp_hunter\产业链投研\scripts\earnings_parent_guardrail.py` 存在，子任务 create/update/pause 前必须先 dry-run：

```powershell
D:\vcp_hunter\紫金研选\.venv\Scripts\python.exe D:\vcp_hunter\产业链投研\scripts\earnings_parent_guardrail.py --output json
```

- 该脚本只做确定性 guardrail 和软审计：路径/import 预检、`load_events` 窗口、TASK_KEY 匹配、ticker/company/market 校验、rrule 校验、重复检测、stale-child pause 候选、review_items、soft_probe_candidates、soft_warnings、轻量 snapshot。
- 可选 `--probe-official-sources` 只输出候选官方来源线索，例如 IR-linked Airtime 事件；不得自动写回。
- 可选 `--write-snapshot` 写入 `automation_snapshots/earnings-parent-22-30-2/latest.json`，只作审计和备份证据，不作决策来源。
- `review_items`、`soft_probe_candidates`、`soft_probe_errors`、`soft_warnings`、source conflicts 和 missing official call time 仍必须由母任务按官方来源规则判断。
- 该脚本不得 refresh events、upsert confirmed event、写 `confirmed_events.json`、直接写 SQLite、写 `trade_dates` 或调用 MarketCalendar 刷新路径。
- `--apply-mechanical` 只能在审核 blockers 和 review_items 后使用。若 `automation_update` 暴露，优先用 `automation_update`；若未暴露，direct TOML 维护必须走 guardrail-style 路径，并强制 TOML parse、rrule regex、duplicate check、ACTIVE + memory 检查和 no active past-planned children。

## Calendar source contract

- 官方 calendar/date source stack：Company IR / JPX / TDnet / DART / KIND / MOPS / SEC EDGAR 6-K / confirmed。
- Yahoo Finance `estimated_unverified` 不是官方来源，只能创建或更新 `default_proxy_not_call_time` 子任务，且 child prompt header 必须标注非官方 Yahoo estimate。
- Yahoo Finance `estimated_conflict` 不得静默创建正式子任务。必须先用官方来源核验；无法核验时报告 `yahoo_estimate_conflict_needs_official_check` 并不创建或显式 caveat。
- Nasdaq 和 Alpha Vantage 是第三方 calendar source，除非独立官方确认，否则只能作线索。
- 若 `OPENDART_API_KEY` 缺失，报告 DART skipped，不报告 DART failed，并继续 JPX / TDnet / KIND / MOPS / SEC EDGAR 6-K / Company IR 检查。
- 每个未来 ACTIVE 子任务 prompt header 必须包含且只使用这些 source header 字段：`Calendar source`、`Event status`、`Source confidence`、`Official source URL`、`Calendar caveat`。
- 只为未来 ACTIVE 子任务回填 source header。不要为了补 header 重写已完成历史子任务。

## 子任务自动化合同

- 每家公司必须创建独立 cron 子任务，命名：`财报电话会深挖 {ticker} {company} {report_date}`。
- 子任务工作区仅 `D:\vcp_hunter\产业链投研`，`executionEnvironment=local`，`model=gpt-5.5`，UI/提示词标签可写 `reasoningEffort=xhigh`，实际 TOML 字段必须写 `reasoning_effort = "xhigh"`。
- 子任务 rrule 必须使用一次性周规则：

```text
DTSTART:YYYYMMDDTHHMMSS
RRULE:FREQ=WEEKLY;BYDAY=<weekday>;BYHOUR=<hour>;BYMINUTE=<minute>;COUNT=1
```

- DTSTART、BYDAY、BYHOUR、BYMINUTE 必须全部来自同一个最终计划开始北京时间；不加 Z，不换算 UTC。
- 禁止裸 DTSTART，禁止 `RRULE:FREQ=DAILY;COUNT=1`、`FREQ=DAILY`、`FREQ=HOURLY` 或任何没有 `COUNT=1` 的重复规则。
- 创建或更新后必须读取 child `automation.toml`，用正则校验：

```text
^DTSTART:\d{8}T\d{6}\nRRULE:FREQ=WEEKLY;BYDAY=(SU|MO|TU|WE|TH|FR|SA);BYHOUR=\d{1,2};BYMINUTE=\d{1,2};COUNT=1$
```

- 子任务 prompt 必须按 `CHILD_PROMPT_TEMPLATE.md` 生成，并保留其中的 literal hard gate、project-local skill resolution、baseline、upstream bottleneck evidence、source-quality、prior-quarter period resolution、QoQ growth、prior-quarter conference-call / earnings-webcast / results-briefing / investor-meeting comparison 和最终中文输出要求。子任务 prompt 正文必须使用英文；除本地路径和最终中文输出标签外，不要混用中文说明。
- 已存在的未来 ACTIVE 子任务如果缺少上述 prior-quarter / QoQ / prior-call comparison 标记，必须更新为当前 `CHILD_PROMPT_TEMPLATE.md` 正文；不得仅因 header、rrule、model、reasoningEffort 正确就视为有效。

## 子任务收尾清理

- 每轮候选处理和 child create/update 后，扫描所有单公司 earnings-call child TOML。
- 通过 prompt marker `TASK_KEY:` 和 `CHILD TASK SKILL HARD GATE` 识别，兼容 legacy id 和缺失 parent marker 的旧任务。
- 若 child 为 ACTIVE 且 `memory.md`、run history 或 final inbox item 显示已完成，先保留或修复一次性 weekly COUNT=1 rrule，再设为 PAUSED，并报告 `executed_child_paused` 或 `stale_child_paused`。
- 不暂停尚未运行且没有 completion evidence 的未来 ACTIVE children；只校验其 one-shot rrule，并报告 `pending_child_validated`。

## 最终汇报

母任务完成后用中文汇报：

- 72 小时窗口和候选事件。
- 官方电话会 +3H 子任务。
- 默认代理排期子任务。
- 官方写回成功/失败和未写本地原因。
- 创建/更新/跳过结果。
- 子任务 rrule 校验结果。
- `executed_child_paused`、`stale_child_paused`、`pending_child_validated`。
- 是否触碰 `trade_dates` 或交易日历路径。
