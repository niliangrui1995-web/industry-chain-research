# ASMPT 0522.HK Jun/2026 来源清单

信息截止：2026-07-29 11:50:15（北京时间）

| ID | 材料 | 来源类型 | 状态 | 用途/限制 |
|---|---|---|---|---|
| S01 | [Q2 2026 业绩公告](https://www.asmpt.com/site/assets/files/85468/q2_2026_en_announcement.pdf) | company_original | found | 当前季度财务、业务、指引、供应约束；原始 PDF 已保存 |
| S02 | [Q2 2026 新闻稿](https://www.asmpt.com/site/assets/files/85463/asmpt_2026_q2_press_release.pdf) | company_original | found | 当前季度摘要和管理层表述 |
| S03 | [Q2 2026 投资者演示](https://www.asmpt.com/site/assets/files/85461/asmpt_q2_2026_investor_presentation.pdf) | company_original | found | 当前季度产品、订单和展望图表 |
| S04 | [本次电话会公告](https://www.asmpt.com/en/investor-relations/announcements-circulars/q2-2026-results-announcement/) | company_original | found | 08:30 HKT 开始；公司承诺会后最迟六小时提供音频回放 |
| S05 | [财务资料页](https://www.asmpt.com/en/investor-relations/financial-information/) | company_original | checked_missing | 截止 11:50 未出现 Q2 2026 音频；仅有 Q1 2026 及更早录音 |
| S06 | [Q1 2026 业绩公告](https://www.asmpt.com/site/assets/files/85243/e0522_results_announcement_2026_q1.pdf) | company_original | found | 已解析的上一季度实际值和承诺基准 |
| S07 | [Q1 2026 投资者演示](https://www.asmpt.com/site/assets/files/85233/asmpt_q1_2026_investor_presentation.pdf) | company_original | found | Q2 指引及上一季度展望 |
| S08 | [Q1 2026 官方电话会音频](https://www.asmpt.com/site/assets/files/85245/asmpt_q1_fy2026_investor_conference_call_audio.mp3) | company_original | found | 官方原始音频；未做全量 ASR |
| S09 | [Q1 2026 全文电话会记录](https://www.roic.ai/quote/0522.HK/transcripts/2026-year/1-quarter) | third_party_transcript | found | 上一季度 Q&A 工作材料；不是官方逐字稿 |
| S10 | iFinD `global_stock_financial` | market_data_vendor | queried_empty | 没有返回事件前 Q2 收入/EPS或 Q3 收入共识数值，不能用于超预期审计 |
| S11 | iFinD `global_stock_quotes` | market_data_vendor | found_pre_event_only | 最新交易日为 2026-07-28；不能作为 7 月 29 日财报后反应 |
| S12 | [2025 年报](https://www.asmpt.com/site/assets/files/84854/e_00522ar-20260405.pdf) | company_original | found | 公司基本面基线 |
| S13 | [imec D2W hybrid-bonding PDK](https://www.imec-int.com/en/press/nanoic-opens-access-first-ever-fine-pitch-rdl-and-d2w-hybrid-bonding-interconnect-pdks) | industry_primary | found | 工艺成熟度外部基准；不用于证明 ASMPT 客户/订单 |
| S14 | [SEMI advanced packaging overview](https://www.semi.org/en/blogs/advanced-packaging-driving-innovation-performance-and-new-system-capabilities) | industry_primary | found | 行业最佳实践和系统级背景；不用于公司财务结论 |

## 当前缺失

- Q2 2026 官方电话会音频/回放、官方逐字稿、字幕及完整 Q&A。
- Q2 2026 可信第三方全文电话会记录或第三方托管原始音频。
- 事件前带数值的市场一致预期快照。
- 2026 中期报告中的完整现金流、资本开支、承诺及关联方附注。

## 脚本记录

- `script_used`: `pypdf` 内联提取器。
- `script_result`: 已从七份官方 PDF 提取可检索文本；原始 PDF 保留并计算 SHA-256。
- `script_limitation`: 两次初始 Windows 命令行引号调用失败；未改动原始文件，后用 PowerShell 标准输入方式成功。
- `manual_fallback_path`: ASMPT 实时 IR 页面发现链接 → 直接下载官方文件 → PowerShell 标准输入调用 `pypdf`。
- `final_source_type`: `company_original + third_party_transcript(prior-quarter only) + market_data_vendor`。
