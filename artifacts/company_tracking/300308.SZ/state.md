# 中际旭创滚动跟踪状态

metadata:
- company: 中际旭创股份有限公司
- ticker: 300308.SZ
- exchange: SZSE
- updated_at: 2026-05-20
- state_type: company_tracking
- grok_status: unavailable_chrome_plugin_not_exposed
- open_web_fallback_status: searched/observation_only_no_new_hard_signal
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
