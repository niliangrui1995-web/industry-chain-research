# 源杰科技（688498.SH）滚动跟踪状态

updated_at: 2026-05-09T05:16:18+08:00  
company: 源杰科技  
ticker: 688498.SH  
exchange: SSE STAR  
coverage_type: daily_update_after_first_baseline  
grok_status: unavailable_chrome_tool_not_exposed  
open_web_fallback_status: searched_no_signal  
not_investment_advice: true

## 当前跟踪结论

当前主线是“数据中心硅光 CW 光源已经兑现收入，高速 EML/200G EML仍处验证和后续放量观察期”。源杰科技不是单纯主题股：2025 年数据中心类产品收入 3.93 亿元、同比 +719.06%，2026Q1 收入和利润继续高增，说明产业链受益已经进入财务报表。但当前股价和市值已经显著反映 AI 硅光预期，后续需要用连续季度收入、回款、客户扩散和 200G EML 订单证据来消化估值。

## 关键假设

- 假设 1：2026 年 70mW/100mW CW 光源需求仍由 AI 数据中心可插拔硅光模块驱动，客户订单不会快速降速。
- 假设 2：公司 2025 年最大客户放量不是一次性补库存，而是下游客户硅光模块产品持续出货。
- 假设 3：公司高速 EML 技术路线有效，但 200G PAM4 EML 从验证到批量收入仍需单独证据。
- 假设 4：公司扩产能保持良率和一致性，不因快速放量导致质量、交付或回款风险。
- 假设 5：高毛利的数据中心业务占比可以维持，否则利润率会向下修正。

## 最新证据

- 2025 年报：全年收入 6.01 亿元，同比 +138.50%；归母净利润 1.91 亿元，扭亏为盈。
- 2025 年报：数据中心类产品收入 3.93 亿元，同比 +719.06%，毛利率 72.21%；电信类产品收入 2.06 亿元，同比 +2.06%，毛利率 31.17%。
- 2025 年报：CW 70mW 大批量交付，CW 100mW 批量交付；100G PAM4 EML 完成客户验证，200G PAM4 EML 开始推进客户验证。
- 2026Q1：收入 3.55 亿元，同比 +320.94%；归母净利润 1.79 亿元，同比 +1153.07%；公司解释为数据中心 CW 光源产品销售额增长及产品结构优化。
- 港交所申请版：2025 年前五大客户收入占比 71.8%，最大客户 F 收入占比 53.4%；客户 F 是主要从事光互连光模块业务的深交所上市公司。
- 市场快照：2026-05-08 腾讯行情显示收盘附近价格 1575.00 元，总市值约 1353.68 亿元；20 个交易日约 +38.5%，60 个交易日约 +95.0%。

## 2026-05-09 日更

核对窗口：2026-05-08 至 2026-05-09（北京）。

- 官方公告/交易所披露：东方财富 `np-anotice-stock` 按 `stock_list=688498.SH`、`begin_time=2026-05-08`、`end_time=2026-05-09` 返回 `total_hits=0`；上交所公告查询最新可见记录仍为 2026-04-28 一季报，未见 2026-05-08 至 2026-05-09 新公告。
- CNINFO：`new/hisAnnouncement/query` 按 `stock=688498`、`seDate=2026-05-08~2026-05-09` 返回 `totalAnnouncement=0`。
- 龙虎榜：东方财富 `RPT_DAILYBILLBOARD_DETAILSNEW` 按 `SECURITY_CODE=688498`、`TRADE_DATE=2026-05-08~2026-05-09` 返回空数据；未发现本窗口龙虎榜记录。
- 大宗交易：东方财富 `RPT_DATA_BLOCKTRADE` 与 `RPT_BLOCKTRADE_STA` 按同一窗口返回空数据；未发现本窗口大宗交易记录。
- 公司 IR：公司官网投资者关系页可见“公司公告”跳转上交所、“一图读懂 | 财报”含 2026 年一季度财报入口；未见 2026-05-08 至 2026-05-09 新增独立 IR 事件。
- Grok/X：当前没有 `@chrome` 工具暴露，按任务要求记录为 `grok_status=unavailable_chrome_tool_not_exposed`，未以普通网页搜索冒充 Grok/X 或 Chrome 会员账号结果。
- open-web fallback：已用 Codex 自身联网能力搜索“源杰科技/688498”最近消息，返回结果主要是一季报解读、公告列表、旧龙虎榜/旧 H 股申请与 IR 记录；未发现 2026-05-08 至 2026-05-09 新增公司特异性信号，状态记为 `open_web_fallback_status=searched_no_signal`。该层仅为公开网页观察层，不等同于 Grok/X 发现层。

日更结论：本窗口无新增官方公告、无龙虎榜、无大宗交易、无 open-web 新信号；不追加 `events.jsonl` 新事件。当前 baseline 主线不变，继续跟踪 CW 光源订单持续性、200G PAM4 EML 验证转量产、客户集中度和回款质量。

## 观察池

- CW 光源：70mW 是否保持主力需求，100mW 是否从批量交付进入更高占比，300mW 是否进入客户验证。
- EML：100G PAM4 EML 是否贡献明确收入，200G PAM4 EML 是否有客户定点、批量订单、收入占比或出货披露。
- 客户：客户 F 订单持续性，客户 H/I/E/B 是否转化为更大规模数据中心订单。
- 现金流：应收账款和存货随收入高增后的回款质量。
- 毛利率：数据中心产品毛利率是否维持，电信业务毛利率是否继续拖累或改善。
- 竞争：海外供应商产能恢复、国内光模块厂商自研芯片、其他国产 EML/CW 光源厂商进展。
- 资本市场：H 股申请审核进度、发行规模、资金用途和对 A 股估值的影响。

## Source Gaps

- N/A：未找到公司官方披露的 70mW/100mW CW 分产品收入、出货颗数或单价。
- N/A：未找到 200G PAM4 EML 的批量收入、批量出货颗数、客户名称或订单规模披露。
- N/A：未找到晶圆片数、月产能、各产品线产能利用率的明确公开数据。
- N/A：未找到客户 F 的公开实名确认；只能按港交所申请版背景描述推断，不应在档案中直接点名。
- N/A：`@chrome`/Grok 工具未暴露，未运行 Grok/X；本次仅执行 open-web fallback 公开网页观察层，且未发现 2026-05-08 至 2026-05-09 新信号。

## Next Questions

1. 2026Q2 是否延续 3 亿元以上单季收入和高利润率，还是 Q1 有集中交付因素。
2. 2026 年客户 F 之外的新增大客户收入占比能否抬升，客户集中度是否下降。
3. 200G PAM4 EML 从“客户验证”到“量产销售”的里程碑是什么，是否会在半年报或投资者关系中披露。
4. 扩产资本开支对应的瓶颈是外延、光刻、刻蚀、镀膜、测试还是封装。
5. 应收账款从 2025 年末 2.64 亿元升至 2026Q1 末 4.10 亿元，后续回款节奏是否健康。
6. 当前估值隐含多少 2026/2027 利润增速；若数据中心 CW 光源毛利率下降，安全边际在哪里。

## Sources

- 2025 年年度报告：https://stockmc.xueqiu.com/202603/688498_20260325_XXO9.pdf
- 2026 年第一季度报告：https://stockmc.xueqiu.com/202604/688498_20260428_3QQQ.pdf
- 港交所 H 股申请版本：https://www1.hkexnews.hk/app/sehk/2026/108326/documents/sehk26032500809.pdf
- 上交所科创板 2025 年报报道：https://www.sse.com.cn/cpc/cpctheme/4th20thcpc/4th20thcpcgcxx/c/c_20260424_10816458.shtml
- 腾讯行情接口：http://qt.gtimg.cn/q=sh688498
- 2026-05-09 日更公告核对（东方财富公告接口）：https://np-anotice-stock.eastmoney.com/api/security/ann?sr=-1&page_size=50&page_index=1&ann_type=A&client_source=web&stock_list=688498.SH&f_node=0&s_node=0&begin_time=2026-05-08&end_time=2026-05-09
- 2026-05-09 日更交易核对（东方财富数据中心）：https://datacenter-web.eastmoney.com/
- 2026-05-09 日更公司 IR 核对：https://www.yj-semitech.com/index.php?c=category&id=36
- 2026-05-09 open-web fallback 参考：新浪财经公告页 https://money.finance.sina.com.cn/corp/go.php/vCB_AllBulletin/stockid/688498.phtml
