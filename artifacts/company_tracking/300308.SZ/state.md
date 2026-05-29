# 中际旭创滚动跟踪状态

metadata:
- company: 中际旭创股份有限公司
- ticker: 300308.SZ
- exchange: SZSE
- updated_at: 2026-05-28
- state_type: company_tracking
- grok_status: unavailable_chrome_plugin_not_exposed
- open_web_fallback_status: searched/observation_only_no_new_operating_signal
- advice_status: 不是买卖建议

## 当前跟踪结论

中际旭创当前处于“1.6T/800G 高景气兑现 + 硅光占比提升 + 上游物料锁定 + 高估值拥挤”的组合状态。公司基本面质量高、业绩弹性高，交易弹性中等偏高但受大市值和高预期约束。

最关键的跟踪点不是公司是否受益 AI，而是：

- 1.6T 是否按季度持续放量。
- 800G 是否仍保持高增长。
- 硅光占比和良率改善是否能继续支撑毛利率。
- 预付锁料能否保障交付，而不是变成库存和现金流压力。
- 客户年降和同行扩产是否开始压缩毛利率。

## 关键假设

1. AI 数据中心和海外 CSP 对高速光互联的需求在 2026 年仍保持高强度。
2. 1.6T 在 2026 年逐季放量，800G 未在短期快速失速。
3. 硅光占比提升和良率改善可以对冲部分年降。
4. 预付款锁定关键原材料和前端供应链产能，短期提升交付确定性。
5. 海外产能、全球采购和全球交付网络仍是核心客户认证的重要条件。

## 最新证据

| 日期 | 证据 | 状态 | 影响 |
|---|---|---|---|
| 2026-04-17 | 2026Q1 收入 194.96 亿元、归母净利润 57.35 亿元、经营现金流 33.68 亿元 | official_filing | 业绩弹性已在财报兑现 |
| 2026-04-17 | 2026Q1 预付账款升至约 14.88 亿元 | official_filing | 支撑锁料和排产逻辑，也增加营运资本跟踪必要性 |
| 2026-04-24 | 1.6T 已量产出货，未来几个季度出货量环比提升 | official_ir | 强化 1.6T 放量主线 |
| 2026-04-24 | 1.6T 和 800G 的硅光技术占比已超过一半以上 | official_ir | 硅光商业化证据增强 |
| 2026-04-24 | 核心原材料包括光芯片、电芯片、PCB、无源器件，部分原材料供给偏紧 | official_ir | 上游物料成为当前最重要的跟踪问题之一 |
| 2026-01-13 | 公司推进 H 股发行上市方案 | official_filing | 全球化融资、产能和供应链布局进一步明确 |
| 2026-05-09 | 第三期/第四期限制性股票激励计划归属价格调整、归属条件成就及部分作废 | official_filing | 偏治理和核心人才激励延续；不改变 1.6T/800G 与硅光主线，后续关注新增股份登记/上市流通提示 |

## 2026-05-09 日更

### Collection Checklist

| 项目 | 状态 | 结果 |
|---|---|---|
| baseline/state/events 读取 | done | 已读取 300308.SZ 独立公司档案 |
| 公告/交易所披露/CNINFO/IR | checked | 2026-05-09 有一组股权激励相关正式公告；未见新的经营订单、财报或 IR 记录 |
| 龙虎榜 | checked | 东方财富 RPT_DAILYBILLBOARD_DETAILSNEW 在 2026-05-08~2026-05-09 窗口返回空数据；最新历史上榜为 2025-07-15，非本窗口事件 |
| 大宗交易 | checked | 东方财富 RPT_BLOCKTRADE_STA / RPT_DATA_BLOCKTRADE 在 2026-05-08~2026-05-09 窗口返回空数据；最新历史大宗交易为 2026-04-21，非本窗口事件 |
| Grok/X | unavailable | `@chrome` 工具未暴露，记录为 `grok_status=unavailable_chrome_tool_not_exposed` |
| open_web_fallback | searched/no_signal | 使用 Codex 自身联网搜索中际旭创/300308 最近消息，未发现高于或独立于正式公告的新经营信号；公开网页结果主要为历史公告、二级数据页和 Q1 点评复述 |

### Official Updates

- CNINFO/巨潮资讯与东方财富公告接口均显示 2026-05-09 披露 11 条公告，核心为第五届董事会第三十二次会议及第三期、第四期限制性股票激励计划相关事项。
- 第三期限制性股票激励计划预留部分第一个归属期：符合归属条件激励对象 69 名，可归属 324,450 股，归属价格 35.16 元/股；同时作废 7 名激励对象已获授但尚未归属的 35,700 股。
- 第四期限制性股票激励计划首次授予部分第一个归属期：符合归属条件激励对象 734 名，可归属 1,309,657 股，归属价格 52.10 元/股；同时作废 20 名激励对象已获授但尚未归属的 144,063 股。
- 本次事件偏股权激励和人才绑定，短期不改公司“1.6T/800G 高景气兑现 + 硅光占比提升 + 上游物料锁定”的核心判断；后续需要跟踪归属股份登记、上市流通提示、股本摊薄和股份支付费用节奏。

## 观察池

| 主题 | 当前状态 | 观察指标 | 升级/降级条件 |
|---|---|---|---|
| 1.6T 放量 | 核心主线 | 出货、收入占比、客户验证、毛利率 | Q2/Q3 继续高增则强化；收入或毛利不及预期则降级 |
| 800G 持续性 | 核心主线 | 订单、年降、是否被 1.6T 替代 | 800G 仍高增长则延长景气；年降加速则降级 |
| 硅光 | 核心变量 | 占比、良率、成本、客户接受度 | 持续披露占比/良率改善则升级；只停留在占比口径则保持 |
| 上游物料 | 当前短板 | 光芯片、电芯片、PCB、无源器件交期/价格/预付款 | 预付回落且交付不受影响为正面；预付继续大增且库存累积需警惕 |
| 海外产能 | 交付壁垒 | 海外产能爬坡、H 股募资投向、客户认证 | H 股招股书披露更细产能和客户信息则升级 |
| 毛利率 | 财务核心 | 综合毛利率、光模块毛利率、硅光良率 | 继续维持高位或提升则强化；年降导致回落则降级 |
| 估值拥挤 | 风险变量 | 成交额、换手率、财报兑现、CSP capex 预期 | 股价先于业绩过度反应或财报不及预期时提高风险权重 |
| 股权激励归属 | 治理/人才绑定变量 | 归属股份登记、上市流通提示、股本摊薄、费用摊销 | 顺利归属且费用影响可控为中性偏正面；核心人员流失或作废比例异常上升则需降级观察 |

## Source Gaps

- 未披露具体客户名称和客户份额。

## 2026-05-19 晚间 T/T+1 复扫

- 公告窗口：北京时间 20:00 后补扫公告日期 `2026-05-19` 和 `2026-05-20`，CNINFO 按公司名和 ticker 检索均未发现新增公告或 IR 记录；completion 记录 `announcement_window_checked=T_and_T_plus_1`。
- 龙虎榜/大宗交易：深交所交易公开信息、大宗交易入口和东方财富接口均未发现 2026-05-19 新增龙虎榜或大宗交易记录。
- open-web fallback：仅观察到当日高位行情波动和资金流讨论，未发现高于 2026-05-15 IR 的 1.6T、800G、硅光、客户或物料供应硬经营信号。
- 本轮状态：无新增硬事件，核心跟踪问题不变；继续等待 1.6T 季度放量、硅光占比/良率、预付款锁料效果和毛利率持续性证据。
- 未披露 1.6T 单独收入、毛利率、客户结构和出货量。
- 未披露 800G 单独收入、毛利率和年降幅度。
- 未披露硅光模块具体良率、成本曲线和客户分布。
- 未披露“部分原材料偏紧”的具体物料、供应商、缺口比例和交期。
- Grok/X 未运行，本次按 `grok_status: unavailable_chrome_tool_not_exposed` 处理；未使用普通网页搜索冒充 Grok/X。
- 2026-05-09 已执行 open web fallback 搜索，状态为 `searched/no_signal`；公开网页结果主要为历史公告、二级数据页和 Q1 点评复述，未发现独立于正式公告的新经营信号。
- 2026-05-13 复扫上一轮 CNINFO 访问缺口：CNINFO hisAnnouncement 在 2026-05-10 至 2026-05-13 窗口正常返回 0 条，未复现 504；公司 IR 最新财报列表仍停留在 2026-04-20，未见新的 800G/1.6T、硅光、客户需求、上游物料或毛利率硬披露。

## Next Questions

1. 2026Q2 是否延续收入、毛利率、利润和经营现金流同步改善？
2. 预付账款是否继续上升，还是随着交付推进开始回落？
3. 1.6T 是否从“持续增加”进入“主流收入贡献”阶段？
4. 800G 是否在 2026H2 继续高增长，还是出现年降或代际切换压力？
5. 硅光占比超过一半后，能否看到良率、成本和毛利率的进一步可验证改善？
6. H 股招股书是否披露更细的客户、产品、区域和产能信息？
7. 本次股权激励归属股份何时完成登记并上市流通，股份支付费用和摊薄影响是否需要纳入 Q2/Q3 模型？
## 2026-05-09 Batch 2 Worker Recheck

- batch_no: 2
- checked_at_beijing: 2026-05-09
- browser_scope: not_available
- grok_status: unavailable: chrome plugin tool not exposed
- open_web_fallback_status: searched/no_new_confirmed_signal
- announcements_checked: 东方财富公告接口确认 2026-05-09 有 11 条公告，均为第五届董事会第三十二次会议及第三期/第四期限制性股票激励计划归属、价格调整、作废、法律意见书、薪酬与考核委员会核查意见；与已记录事件属于同一组事项，未重复追加 events.jsonl。
- lhb_checked: 东方财富 RPT_DAILYBILLBOARD_DETAILSNEW 在 2026-05-08 至 2026-05-09 窗口返回空数据，未见本窗口龙虎榜。
- block_trade_checked: 东方财富 RPT_BLOCKTRADE_STA 与 RPT_DATA_BLOCKTRADE 在 2026-05-08 至 2026-05-09 窗口返回空数据，未见本窗口大宗交易。
- material_changes: 无新增经营类、订单类、800G/1.6T、硅光、客户需求、上游物料或毛利率硬证据；维持上一轮“股权激励事项为治理/人才绑定，不改变核心产业判断”的结论。
- miss_risk_notes: CNINFO hisAnnouncement 条件查询本轮返回 0，但 CNINFO 静态 PDF 与东方财富公告接口可访问并相互印证；普通网页搜索只作观察池，不能替代 Grok/X 或官方确认。

## 2026-05-13 Batch 2 Worker Recheck

- batch_no: 2
- checked_at_beijing: 2026-05-13 晚间
- browser_scope: fallback_no_browser
- grok_status: unavailable_chrome_plugin_not_exposed
- open_web_fallback_status: searched/block_trade_signal_only
- task_block: 中际旭创 300308.SZ；aliases=中际旭创/旭创科技/Innolight；tracking_focus=800G/1.6T、硅光、客户需求、上游物料、毛利率、公告/交易事件
- checklist: baseline_read=done; state_read=done; events_read=done; announcements_checked=done; lhb_checked=done; block_trade_checked=done; grok_checked=unavailable; open_web_fallback=done; events_appended=1; state_updated=done
- announcements_checked: CNINFO hisAnnouncement 查询 2026-05-10 至 2026-05-13 返回 0 条，未复现上一轮 CNINFO 504；公司 IR 页面最新财务报告仍为 2026-04-20 的 2026Q1/2025年报，未见 2026-05-13 新公告或新投资者关系记录。
- lhb_checked: 东方财富 RPT_DAILYBILLBOARD_DETAILSNEW 在 2026-05-13 窗口返回空数据，未见当日龙虎榜。
- block_trade_checked: 东方财富 RPT_BLOCKTRADE_STA/RPT_DATA_BLOCKTRADE 显示 2026-05-13 有 3 笔大宗交易，合计 1.07 万股、1122.65 万元，成交价 1049.20 元，买卖双方均为机构专用；已追加 events.jsonl。
- open_web_fallback_observation: 新浪财经/证券时报系转载与东方财富数据口径一致，指向同一组大宗交易；证券之星资金流报道仅作二级市场观察，不作为经营硬证据。
- material_changes: 无新增经营类、订单类、800G/1.6T、硅光、客户需求、上游物料或毛利率硬披露；新增项仅为交易事件大宗交易。
- miss_risk_notes: Chrome/Grok/@chrome 工具面未暴露，未执行 Grok/X；本轮 open-web fallback 不能替代登录态 Grok/X。CNINFO 当前窗口返回 0 条可降低“504漏公告”风险，但仍需下轮继续跟踪 H 股招股书、Q2 经营口径和新增 IR 记录。

## 2026-05-14 recheck

browser_scope: fallback_no_browser
grok_status: unavailable_chrome_plugin_not_exposed
open_web_fallback_status: searched_trading_event_only

CNINFO 2026-05-10 至 2026-05-14 无新增公告，龙虎榜为空。新增 1 笔小额大宗交易：成交价 1078.00 元，成交 0.50 万股，成交金额 539.00 万元，机构专用对机构专用，折溢价率约 0%。

本轮结论：新增仅为交易层小额机构换手，不构成 800G/1.6T、硅光、客户需求、上游物料或毛利率的新经营披露。核心跟踪假设维持不变。

## 2026-05-15 日更
- browser_scope: `fallback_no_browser`；grok_status: `unavailable_chrome_plugin_not_exposed`；open_web_fallback_status: `searched_trading_event_only`。
- 公告/IR：2026-05-15 未见新增官方公告或新 IR 记录；最近硬公告仍停留在 2026-05-09 股权激励相关披露。
- 龙虎榜：2026-05-15 无新增记录。
- 大宗交易：2026-05-15 新增 1 笔机构对机构成交，成交价 1049.87 元，成交 0.55 万股，成交额 577.43 万元。
- 结论：本轮新增仅为小额机构大宗交易；800G、1.6T、硅光、客户需求、上游物料和毛利率主线判断不变。
## 2026-05-15 晚间公告补扫校正
- CNINFO 按公司名检索 `2026-05-15~2026-05-16` 确认新增 `投资者关系活动记录表20260515`。
- IR 要点：公司称高端光模块产品订单和出货持续增加；1.6T 产品早已批量出货且持续起量；3.2T 产品仍在持续研发和完善；供应链稳定，并通过核心原材料备货、备选供应商和保障协议保障交付；目前在手订单充足；H 股发行相关工作稳步推进；NPO 产品仍处于技术完善和客户验证阶段。公司同时强调未发布业绩指引，纪要不代表盈利预测和业绩指引。
- 结论修正：这条 IR 比小额大宗交易更重要，应从“仅交易层事件”修正为“交易层事件 + 经营层 IR 口径更新”。但其仍未量化收入、客户、毛利率或 H 股时间表，不能直接外推业绩指引。

## 2026-05-20 Batch 2 Worker Recheck

- batch_no: 2
- checked_at_beijing: 2026-05-20 20:02
- browser_scope: fallback_no_browser
- grok_status: unavailable_chrome_plugin_not_exposed
- open_web_fallback_status: searched/observation_only_no_new_hard_signal
- task_block: 中际旭创 300308.SZ；aliases=中际旭创/Innolight/800G/1.6T/optical module/silicon photonics；tracking_focus=800G/1.6T交付、硅光、客户需求、上游物料和毛利率
- checklist: baseline_read=done; state_read=done; events_read=done; announcements_checked=done; announcement_window_checked=T_and_T_plus_1; lhb_checked=done; block_trade_checked=done; grok_checked=unavailable; open_web_fallback=done; events_appended=0; state_updated=source_gap_only
- announcements_checked: CNINFO `hisAnnouncement/query` 按证券代码和公司名检索 `2026-05-20~2026-05-21` 均返回 0 条；东方财富公告接口按 `300308.SZ` 和 `0.300308` 同窗口均返回 0 条；公司官网投资者关系页最新公告仍停留在 2026-04-17 一季报，财务报告页最新为 2026-04-20 一季报/年报入口，未见 2026-05-20 或 2026-05-21 新公告。
- source_gap: 深交所 `annList` 本轮三种参数组合均返回 500，未能直接完成 SZSE 页面核验；已用 CNINFO、东方财富公告镜像和公司官网投资者关系页交叉替代，下一轮继续抽查深交所恢复情况。
- lhb_checked: 东方财富 `RPT_DAILYBILLBOARD_DETAILSNEW` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-20` 返回空数据，未发现当日新增龙虎榜。
- block_trade_checked: 东方财富 `RPT_DATA_BLOCKTRADE` 与 `RPT_BLOCKTRADE_STA` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-20` 均返回空数据，未发现当日新增大宗交易。
- open_web_fallback_observation: 普通网页检索仅观察到 2026-05-15 IR 复述、2026Q1 点评、5月19日行情/资金流和论坛级产业链讨论；未发现可升级为官方或交易硬事件的新 800G/1.6T、硅光、客户、物料或毛利率信号。
- material_changes: 无新增经营类、订单类、财务类、800G/1.6T、硅光、客户需求、上游物料或毛利率硬披露；无新增龙虎榜或大宗交易事件，`events.jsonl` 不追加。
- miss_risk_notes: Chrome/@chrome/Grok 工具面未暴露，未执行登录态 Grok/X；open-web fallback 仅作观察池，不替代 Grok/X 或官方确认。公司官网公告页存在同步滞后风险，正式公告仍以 CNINFO/交易所/公告镜像为主。

## 2026-05-21 晚间 T/T+1 复扫

- 公告窗口：北京时间 20:00 后核查公告日期 `2026-05-21` 和 `2026-05-22`，未发现新增正式公告或公司 IR；completion 记录 `announcement_window_checked=T_and_T_plus_1`。
- 龙虎榜：2026-05-21 未发现新增龙虎榜记录。
- 大宗交易：2026-05-21 发生 4 笔平价大宗交易，成交价均为 993.34 元，合计成交 19.72 万股、约 1.96 亿元，卖方均为机构专用，买方包括申万宏源上海第二分公司、广发证券深圳壹方中心、国泰海通深圳深南大道京基一百等席位。
- 本轮状态：新增交易结构信号，金额较此前小额大宗明显放大，后续观察是否延续和是否伴随股价/成交额异常；但不构成 800G/1.6T、硅光、客户需求、物料或毛利率的新经营披露。

## 2026-05-22 日更

- 公告窗口：北京时间 20:00 后检查公告日期 `2026-05-22` 和 `2026-05-23`，CNINFO 检出《特定股东部分股票进行质押交易及解除质押的公告》，2026-05-23 未见新增。
- 新增硬事件：特定股东苏州益兴福质押 35.00 万股给中信证券、138.00 万股给国泰海通，并解除 70.00 万股质押，净质押增加约 103.00 万股；益兴福及一致行动人累计质押 1,158.40 万股，占其持股 12.12%、总股本 1.04%。
- 交易事件：2026-05-22 未发现新增龙虎榜或大宗交易。
- 状态变化：新增股东质押/解押观察，累计质押占总股本比例不高；不改变 800G/1.6T、硅光、客户需求、物料和毛利率主线，后续观察质押比例是否继续上升并与大宗交易或减持联动。

## 2026-05-24 Batch 2 Worker Recheck

- batch_no: 2
- checked_at_beijing: 2026-05-24 20:04
- browser_scope: chrome_separate_tab_grok_available
- grok_status: searched/no_useful_new_signal
- open_web_fallback_status: searched/observation_only_no_new_hard_signal
- task_block: 中际旭创 300308.SZ；aliases=中际旭创/Innolight/800G/1.6T/optical module/silicon photonics；tracking_focus=800G/1.6T交付、硅光、客户需求、上游物料和毛利率
- checklist: baseline_read=done; state_read=done; events_read=done; announcements_checked=done; announcement_window_checked=T_and_T_plus_1; lhb_checked=done; block_trade_checked=done; grok_checked=done; open_web_fallback=done; events_appended=0; state_updated=source_gap_only
- announcements_checked: CNINFO `hisAnnouncement/query` 按公司名和证券代码检索 `2026-05-24~2026-05-25` 均返回 0 条；东方财富公告镜像按 `300308` 同窗口返回 0 条；公司官网投资者关系页最新公告仍停留在 2026-04-17 一季报、投资者活动页仍停留在历史调研记录，未见 2026-05-24 或 2026-05-25 新公告、IR、订单、产能、客户或毛利率披露。
- source_gap: 深交所 `annList` 按公告日期 `2026-05-24~2026-05-25` 和 `300308/中际旭创` 参数返回 500，未能直接完成 SZSE 公告页核验；已用 CNINFO、东方财富公告镜像和公司官网投资者关系页交叉替代，下一轮继续抽查深交所恢复情况。
- latest_trading_day: 腾讯行情快照时间戳为 `20260522161406`，本轮按 `2026-05-22` 作为最近 A 股交易日核对。
- lhb_checked: 东方财富 `RPT_DAILYBILLBOARD_DETAILSNEW` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-22` 返回空数据，未发现最近交易日新增龙虎榜。
- block_trade_checked: 东方财富 `RPT_DATA_BLOCKTRADE` 与 `RPT_BLOCKTRADE_STA` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-22` 均返回空数据，未发现最近交易日新增大宗交易；5 月内最近大宗交易仍为已入账的 `2026-05-21` 四笔平价机构换手。
- grok_observation: 独立 Chrome/Grok 标签页完成单公司最近 24 小时发现层查询；Grok 结果判断最近 24 小时无高价值新线索，提到的 800G/1.6T 市占率、硅光占比、北美客户需求、上游 EML 等瓶颈和扩产/招聘均为既有财报、IR、媒体或社交复述，需官方复核后才可升级。
- open_web_fallback_observation: 普通网页检索主要返回 2026Q1 点评、2026-05-15 IR 复述、既有公告镜像、研报/论坛/雪球类二级解读和官网旧新闻；未发现可升级为官方或交易硬事件的新 800G/1.6T、硅光、客户、物料、毛利率或异常交易信号。
- material_changes: 无新增经营类、订单类、财务类、800G/1.6T、硅光、客户需求、上游物料或毛利率硬披露；无新增龙虎榜或大宗交易事件，`events.jsonl` 不追加。
- miss_risk_notes: T+1 公告日期包含未来日期 `2026-05-25`，晚间披露可能继续刷新；深交所公告接口本轮 500，需下轮继续复核。Grok/X 和 open-web 均未作为确认事实写入事件账本。

## 2026-05-25 Batch 2 Worker Recheck

- batch_no: 2
- checked_at_beijing: 2026-05-25 20:47
- browser_scope: fallback_no_browser
- grok_status: unavailable_chrome_plugin_tool_not_exposed
- open_web_fallback_status: searched/observation_only_no_new_operating_signal
- task_block: 中际旭创 300308.SZ；aliases=中际旭创/Innolight/800G/1.6T/optical module/silicon photonics；tracking_focus=800G/1.6T交付、硅光、客户需求、上游物料和毛利率
- checklist: baseline_read=done; state_read=done; events_read=done; announcements_checked=done; announcement_window_checked=T_and_T_plus_1; lhb_checked=done; block_trade_checked=done; grok_checked=unavailable; open_web_fallback=done; events_appended=1; state_updated=done
- announcements_checked: CNINFO `hisAnnouncement/query` 按证券代码和公司名检索 `2026-05-25~2026-05-26` 均返回 0 条；东方财富公告镜像按 `300308.SZ` 同窗口返回 0 条；公司官网投资者关系页最新公告仍显示 2026-04-17 一季报，财务报告页最新为 2026-04-20 一季报/年报入口，未见 2026-05-25 或 2026-05-26 新公告、IR、订单、产能、客户或毛利率披露。
- source_gap: 深交所 `annList` 按 `listed_notice_disc`、`listedNotice_disc`、`fixed_disc` 查询 `2026-05-25~2026-05-26` 均返回 50x 维护页；深交所龙虎榜/大宗交易直连接口也返回 50x，未能直接完成 SZSE 页面核验。已用 CNINFO、东方财富公告镜像、公司官网投资者关系页和东方财富交易数据接口交叉替代，下一轮继续抽查深交所恢复情况。
- lhb_checked: 东方财富 `RPT_DAILYBILLBOARD_DETAILSNEW` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-25` 返回 `code=9201/返回数据为空`，未发现当日新增龙虎榜。
- block_trade_checked: 东方财富 `RPT_DATA_BLOCKTRADE` 与 `RPT_BLOCKTRADE_STA` 显示 2026-05-25 有 1 笔大宗交易，成交价 1093.00 元，成交 0.93 万股，成交金额 1016.49 万元，折溢价率 0%；买方为国信证券股份有限公司深圳后海分公司，卖方为机构专用；已追加 `events.jsonl`。
- open_web_fallback_observation: 普通网页检索主要返回 2026Q1 点评、2026-05-15 IR 复述、既有公告镜像、行情/资金流和论坛/研报类二级解读；未发现可升级为官方经营事件的新 800G/1.6T、硅光、客户、物料或毛利率量化信号。
- material_changes: 新增项为交易层小额平价大宗交易；不构成经营类、订单类、财务类、800G/1.6T、硅光、客户需求、上游物料或毛利率的新硬披露，核心跟踪假设维持不变。
- miss_risk_notes: 当前工具面未暴露可调用 Chrome/Grok 插件工具，未执行登录态 Grok/X，也未使用 Browser Use 或 Playwright 替代；open-web fallback 仅作观察池。T+1 公告日期 `2026-05-26` 仍可能在更晚时间继续刷新；深交所接口 50x 需下轮复核。

## 2026-05-28 Company Worker Recheck

- checked_at_beijing: 2026-05-28 13:40 前后；当前早于 20:00，公告窗口记录 `announcement_window_checked=pending_evening_rescan`。
- browser_scope: fallback_no_browser；grok_status: unavailable_no_callable_chrome_grok_tool；open_web_fallback_status: searched/observation_only_no_new_operating_signal。
- task_block: 中际旭创 300308.SZ；aliases=中际旭创/Innolight/800G/1.6T/optical module/silicon photonics；tracking_focus=800G/1.6T交付、硅光、客户需求、上游物料和毛利率。
- checklist: baseline_read=done; state_read=done; events_read=done; announcements_checked=done; announcement_window_checked=pending_evening_rescan; lhb_checked=done; block_trade_checked=done; grok_checked=unavailable; open_web_fallback=done; events_appended=2_block_trade_plus_1_governance_announcement; state_updated=done。
- announcements_checked: CNINFO `hisAnnouncement/query` 按 `中际旭创/300308` 检索 `2026-05-26~2026-05-28` 返回 10 条 2026-05-28 公告，核心为第五届董事会第三十三次会议决议、2026 年第二次临时股东会通知，以及独立董事候选人/提名人声明与承诺；未见订单、产能、财务、800G/1.6T、硅光、客户、物料或毛利率新增硬披露。
- source_gap: 深交所直连公告/交易接口本轮仍未形成稳定可复核结果；公司官网 IR/投资者关系入口未见高于 CNINFO 的新增经营记录。本轮以 CNINFO 官方公告、东方财富交易数据和公开网页交叉观察完成收口，晚间仍需复扫 2026-05-28 及可能的 T+1 披露。
- lhb_checked: 东方财富 `RPT_DAILYBILLBOARD_DETAILSNEW` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-26~2026-05-28` 返回 `code=9201/返回数据为空`；未发现 2026-05-26、2026-05-27 已完成交易日新增龙虎榜。2026-05-28 因仍在盘中，不写日终结论。
- block_trade_checked: 东方财富 `RPT_DATA_BLOCKTRADE` 与 `RPT_BLOCKTRADE_STA` 显示 2026-05-26 有 1 笔大宗交易，成交价 1103.00 元、成交 0.22 万股、成交金额 242.66 万元；2026-05-27 有 2 笔大宗交易，成交价均为 1111.37 元、合计 0.75 万股、成交金额 833.53 万元；买卖双方均为机构专用、折溢价率约 0%。公开网页对这两日大宗交易有同向记录，已追加 `events.jsonl`。
- open_web_fallback_observation: 普通网页检索主要返回 5 月 28 日治理公告、5 月 26/27 大宗交易页面、既有 2026Q1/5 月 15 日 IR 复述，以及论坛/研报类对 800G、1.6T、硅光和上游物料的二级解读；未发现可升级为官方或交易硬事件的新经营信号。
- material_changes: 新增正式公告为董事会换届/股东会安排，偏治理；新增两日小额平价大宗交易，偏交易结构。均不构成 800G/1.6T 交付、硅光、客户需求、上游物料或毛利率的新经营确认，核心跟踪假设维持不变。
- miss_risk_notes: 当前无可调用 Chrome/Grok 工具，未执行登录态 Grok/X；open-web fallback 仅作 observation_only。由于本轮早于 20:00，需晚间/T+1 对 CNINFO、SZSE 和公司 IR 再扫一次，避免漏掉 2026-05-28 晚间披露。
## 2026-05-28 晚间 T/T+1 复扫

- checked_at_beijing: 2026-05-28 20:32 后复扫。
- browser_scope: not_available_no_callable_chrome_tool；grok_status: `unavailable_no_callable_chrome_tool`；open_web_fallback_status: `searched/observation_only_no_new_operating_signal`。
- announcements_checked: CNINFO `hisAnnouncement/query` 按 `stock=300308,9900022016` 和公司名检索 `2026-05-28~2026-05-29`，确认早盘已记录的 2026-05-28 董事会/临时股东会/独董候选人公告组，并新增 2026-05-29《第四期限制性股票激励计划首次授予部分第一个归属期归属结果暨股份上市公告》。公告披露本次归属日/上市流通日为 2026-06-01，归属股票数量 1,309,657 股，占当前总股本 0.12%，归属人数 734 人，归属后总股本增至 1,114,910,191 股；募集资金用于补充流动资金。
- announcement_window_checked: `T_and_T_plus_1`。新增 2026-05-29 公告已追加 `events.jsonl`；早盘已记录的 2026-05-28 治理公告组不重复追加。
- SZSE/公司 IR: 深交所 `annList` 直连仍返回 50x 维护页，记录为 `szse_annlist_50x_source_gap`；公司官网投资者关系页最新公告/财报入口仍停留在 2026-04-17/2026-04-20 一季报和年报入口，未见高于 CNINFO 的新增经营类 IR。
- lhb_checked: 东方财富 `RPT_DAILYBILLBOARD_DETAILSNEW` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-28` 与 `2026-05-29` 均返回 `code=9201/返回数据为空`，未发现 2026-05-28 晚间新增龙虎榜记录；2026-05-29 在本轮运行时尚非已完成交易日，只作空结果记录。
- block_trade_checked: 东方财富 `RPT_DATA_BLOCKTRADE` 与 `RPT_BLOCKTRADE_STA` 按 `SECURITY_CODE=300308`、`TRADE_DATE=2026-05-28` 与 `2026-05-29` 均返回 `code=9201/返回数据为空`，未发现 2026-05-28 晚间新增大宗交易记录。
- open_web_fallback_observation: 普通联网检索主要返回 2026Q1/5 月 15 日 IR 复述、既有 800G/1.6T/硅光研报解读、公司官网产品页和 5 月 28 日治理公告镜像；未发现可升级为官方或交易硬事件的新 800G/1.6T、硅光、客户、物料或毛利率信号。
- material_changes: 新增事项为股权激励归属结果暨股份上市公告，偏治理/员工激励和轻微股本摊薄；不改变 800G/1.6T 交付、硅光、客户需求、上游物料和毛利率主线判断。
- miss_risk_notes: Chrome/Grok 工具面不可用，未覆盖登录态 Grok/X 原生线索；深交所直连接口 50x，已用 CNINFO 官方公告、公司官网投资者页、东方财富交易数据和 open-web 观察交叉补位；普通联网搜索仅作 observation_only。

## 2026-05-29 日更

核查窗口：北京时间 20:00 后运行，公告硬门覆盖公告日期 `2026-05-29` 与 `2026-05-30`，`announcement_window_checked=T_and_T_plus_1`。

- 公告 / CNINFO / 交易所披露：CNINFO 与 SZSE 同窗口仅返回已在上一轮 T+1 入账的《第四期限制性股票激励计划首次授予部分第一个归属期归属结果暨股份上市公告》，2026-05-30 未见新增公告。公司官网 IR/公告页更新滞后，未见高于 CNINFO 的新增经营记录。
- 龙虎榜：2026-05-29 未发现中际旭创新增龙虎榜记录。
- 大宗交易：东方财富大宗交易接口确认 2026-05-29 新增 3 笔平价大宗交易，成交价均为 1161.16 元，合计成交 1.11 万股、1288.89 万元，买卖双方均为机构专用。
- Grok/X：当前工具面没有可调用 Chrome/Grok/@chrome，记录为 `unavailable_no_callable_chrome_tool`；未使用 Browser Use 或 Playwright 冒充登录态 Chrome/Grok。
- open-web fallback：普通公开网页主要返回同一股权激励公告镜像、同一大宗交易新闻、旧 IR/研报/论坛复述；未发现可升级为官方事实的新 1.6T、800G、硅光、客户、物料或毛利率信号。
- 本次状态变化：不重复追加已入账的股权激励归属公告，追加 2026-05-29 小额平价大宗交易。核心基线不变，继续跟踪大宗交易是否延续为连续机构席位换手、6 月 1 日限制性股票上市流通后的股本/解禁/减持联动，以及下一条 IR 是否量化 1.6T、硅光、良率或毛利率。
