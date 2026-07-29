# KLAC Jun/2026 来源清单

核验截止：`2026-07-29T08:43:15+08:00`

## 公司与监管原始来源

| 材料 | 来源类型 | 完整性与用途 |
|---|---|---|
| [FY2026 Q4 earnings release](https://ir.kla.com/news-events/press-releases/detail/518/kla-corporation-reports-fiscal-2026-fourth-quarter-and-full) | `company_original` | 完整；报告数字、GAAP/non-GAAP 对账及 FY2027 Q1 指引 |
| [FY2026 Q4 shareholder letter](https://d1io3yog0oux5.cloudfront.net/_b9ee755a5f60dd0fb3f9e27967aed6af/klatencor/db/1117/10668/letter_to_shareholders/KLA+Earnings+Shareholder+Letter+-+Q4+FY26.pdf) | `company_original` | 完整；业务组合、终端需求、WFE、先进封装和毛利桥 |
| [FY2026 Q4 earnings slides](https://d1io3yog0oux5.cloudfront.net/_b9ee755a5f60dd0fb3f9e27967aed6af/klatencor/db/1117/10668/earnings_slide_presentation/KLA+Earnings+Slides+-+Q4+FY26.pdf) | `company_original` | 完整；季度摘要和指引 |
| [Form 8-K](https://www.sec.gov/Archives/edgar/data/319201/000031920126000024/klac-20260728.htm) | `regulatory_filing` | 完整；确认新闻稿提交时间与附件 |
| [官方 IR event](https://ir.kla.com/news-events/ir-calendar/event/fourth-quarter-fiscal-year-2026-earnings-call) | `company_original` | 完整；事件身份与官方回放入口 |
| [官方 ON24 回放](https://event.on24.com/wcc/r/5395899/6008DA167612920BB3D60F6AAA4113A5) | `official_event_platform` | 完整 1:07:40 音频；包括 prepared remarks 与 Q&A |
| [FY2026 Q3 earnings release](https://ir.kla.com/news-events/press-releases/detail/514/kla-corporation-reports-fiscal-2026-third-quarter-results) | `company_original` | 完整；上季实际和原指引 |
| [FY2026 Q3 IR event](https://ir.kla.com/news-events/ir-calendar/event/third-quarter-fiscal-year-2026-earnings-call) | `company_original` | 完整；上季事件身份与回放入口 |

## 转录与盘前预期来源

| 材料 | 来源类型 | 边界 |
|---|---|---|
| [MarketBeat FY2026 Q4 full transcript](https://www.marketbeat.com/earnings/reports/2026-7-28-kla-co-stock/) | `third_party_transcript` | 完整、含时间戳和 Q&A；存在少量 ASR 错词，关键措辞由官方音频定点复核 |
| [Motley Fool FY2026 Q3 transcript](https://www.fool.com/earnings/call-transcripts/2026/04/29/kla-klac-q3-2026-earnings-call-transcript/) | `third_party_transcript` | 上季完整对照稿；不是官方来源 |
| [MarketBeat 2026-07-21 preview](https://www.marketbeat.com/instant-alerts/kla-klac-to-release-quarterly-earnings-on-tuesday-2026-07-21/) | `market_data_vendor` | 盘前 EPS 1.00、收入 3.6016B |
| [Zacks 2026-07-24 preview](https://www.zacks.com/stock/news/2960402/klas-q4-earnings-loom-buy-sell-or-hold-the-klac-stock) | `market_data_vendor` | 盘前 EPS 1.00、收入 3.61B |
| [ChartMill pre-event snapshot](https://www.chartmill.com/stock/quote/KLAC/analyst-ratings) | `market_data_vendor` | 盘前 EPS 1.02、收入 3.67B；与前两项收入共识有实质分歧 |

## 脚本与人工回退记录

- `script_used`: `webcast_asset_fetcher.py --fetch-scripts --download none`，分别用于本季和上季官方 ON24 页面。
- `script_result`: 页面与脚本外壳保存成功，但没有产出可直接使用的媒体 URL。
- `script_limitation`: ON24 媒体清单由运行时 API/网络请求生成，静态解析器未命中。
- `manual_fallback_path`: 使用登录态浏览器检查官方 ON24 网络请求，取得 MPD；再下载官方音轨。第三方完整转录作为工作稿，只对关键投资措辞做官方音频定点复核。
- `final_source_type`: `company_original + regulatory_filing + official_event_platform + third_party_transcript`。
- 完整全量 ASR 未采用：GPU 路径缺少运行库，CPU 路径内存分配失败；已有可靠完整转录后，按技能规则切换为官方音频定点核词。

## 缺失材料

- 截止时点未发现 KLA 发布的官方逐字稿或完整 captions。
- 截止时点 FY2026 Form 10-K 尚未发布，电话会所述约 12.5B backlog/RPO 尚待正式申报文件复核。
- 公司未披露季度 orders/bookings 数值。
- 未取得可核验的 FY2027 Q1 盘前收入与 EPS 共识。
- 公司没有量化说明 FY2027 Q1 指引中已有 backlog、合同或确定排期覆盖的比例，也未披露 take-or-pay、定金或预付款覆盖。
