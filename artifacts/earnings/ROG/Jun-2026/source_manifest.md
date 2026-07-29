# Rogers（ROG）Jun/2026 来源与脚本记录

## 原始材料

| 材料 | 来源类型 | 状态 | 本地文件 / URL | SHA-256 |
|---|---|---|---|---|
| Q2 2026 Form 8-K | `official_filing` | 已取得 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\8k.html` / https://www.sec.gov/Archives/edgar/data/84748/000008474826000046/rog-20260728.htm | `F6D7873D234BEB30C6F878A2930465DEE096B1B02865E6C17EDB57B296C068D7` |
| Q2 2026 8-K Exhibit 99.1 | `official_filing` | 已取得 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\8k_ex99_1.html` / https://www.sec.gov/Archives/edgar/data/84748/000008474826000046/q22026resultsannouncement.htm | `B09FE3EE870D8DCB78D34DCC6E756B5C937D01EC0AD8DE6C3DF5AFF7A1788996` |
| Q2 2026 财报新闻稿 PDF | `company_original` | 已取得 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\earnings_release.pdf` / https://www.rogerscorp.com/-/media/project/rogerscorp/documents/investor-relations/english/press-releases/2026/rogers-corporation-reports-second-quarter-2026-results.pdf | `577D038A34C5A43E8EC44A11C9FB732F5C9D2DC9B80B577F8CD3F0FD824DC16E` |
| Q2 2026 演示稿 PDF | `company_original` | 已取得 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\investor_presentation.pdf` / https://www.rogerscorp.com/-/media/project/rogerscorp/documents/investor-relations/english/presentation-slides/2026/rogers-corporation-2026-second-quarter-conference-call-slides.pdf | `38DA584DD8F3E012AA5F8713011B81C09BF9DCDAB30E6EA4E4BF1CFA10122B65` |
| Q2 2026 官方 webcast 页 | `official_event_platform` | 注册页可达，未暴露 replay/captions | https://event.choruscall.com/mediaframe/webcast.html?webcastid=qyZXB7IS | N/A |
| Q2 2026 完整电话会音频 | `original_call_audio + third_party_hosted` | 已取得并完整覆盖 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\replay_audio.mpeg` / https://files.quartr.com/audio-files/30592066e9f6a71d428a8abfe446d240-2026-07-28-21-45-02.mpeg?ref=U0E= | `A56A287DD2EF7087799862800AA1250C0360F8CC14708B090890A4FA8F3591F7` |
| Q1 2026 财报新闻稿 PDF | `company_original` | 已取得 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\prior_quarter_earnings_release.pdf` / https://www.rogerscorp.com/news/2026/rogers-corporation-reports-first-quarter-2026-results | `5616B7B95E2AF091F7BEE6667B81FBACEDBE5071BCA5BC2205FEF467A66FA272` |
| Q1 2026 演示稿 PDF | `company_original` | 已取得 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\prior_quarter_investor_presentation.pdf` | `DAD08B1BF1DF6061693F51678151BA6A08EF84F0D690A85F3B6C8D1DF06FAC0C` |
| Q1 2026 Form 10-Q | `official_filing` | 已取得 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\prior_quarter_10q.html` / https://www.sec.gov/Archives/edgar/data/84748/000008474826000023/rog-20260331.htm | `8DD52F37269D73225ECBAB393CE5C880A6AB0453276C7129C4387052BC183C78` |
| Q1 2026 完整电话会文字稿 | `third_party_transcript` | 已取得并仅作前季措辞对照 | https://www.fool.com/earnings/call-transcripts/2026/04/28/rogers-rog-q1-2026-earnings-call-transcript/ | N/A |
| 2025 Form 10-K | `official_filing` | 已取得，用于事前公司基线 | `D:\vcp_hunter\产业链投研\artifacts\earnings\ROG\Jun-2026\raw\2025_10k.html` / https://www.sec.gov/Archives/edgar/data/84748/000008474826000007/rog-20251231.htm | `182609080239E52EE24C740A5EB1AE5402826E31D84257B3268ECDA398117BB5` |

## 脚本记录

| script_used | script_result | script_limitation | manual_fallback_path | final_source_type |
|---|---|---|---|---|
| `scripts/automation_run_metadata.py` | `PASS`，技能树 clean、合同版本匹配 | 只验证运行元数据，不收集业务证据 | N/A | `regulatory_filing` |
| `.agents/skills/earnings-call-investment-analyst/scripts/webcast_asset_fetcher.py` | `partial`，抓到当前与前季注册页及静态脚本 | 官方活动页未暴露媒体、字幕或逐字稿资产 | 搜索可靠完整事件内容，取得第三方托管的原始完整音频 | `original_call_audio` |
| `.agents/skills/earnings-call-investment-analyst/scripts/audio_transcriber.py` | 初次 `small.en` 因本机缺 CUDA `cublas64_12.dll`，CPU 回退又遇内存不足；分段后 `base.en / CPU / int8` 四段全部成功 | ASR 存在人名和数字误识别；数字不得脱离官方文件准出 | 用官方 8-K/演示稿校正数字；对关键 Q&A 逐段定位并保留音频 | `original_call_audio` |
| `.agents/skills/financial-evidence-audit/scripts/financial_evidence_audit.py` | 派生变化率 `PASS/publishable`；一致预期 `FAIL/blocked` | 无法替代缺失的同口径、财报前冻结共识快照 | 对共识冲突保留 `证据不足`，不发布 beat/miss | `regulatory_filing` |

## 行业最佳实践口径

- 按 SEC Non-GAAP C&DIs，将 GAAP 与 adjusted/non-GAAP 分开列示，并以公司 8-K 的 reconciliation 为准：https://www.sec.gov/rules-regulations/staff-guidance/corporation-finance-interpretations/non-gaap-financial-measures
- 事实锚定 SEC filing 与公司 IR 原件；第三方页面仅用于补足完整事件内容或共识线索，不覆盖官方数字。
