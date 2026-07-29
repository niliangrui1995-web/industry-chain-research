# SK hynix 2026Q2 证据包索引

本文件是结构化证据层的可读索引；完整字段见 `evidence_pack.json`，投资分析见 `analysis/report.md`。

## 状态

- `company_original_status`: `found`
- `call_content_status`: `official_complete`
- `final_source_type`: `company_original + official_event_platform + exchange_announcement + local_derivative`
- `provisional`: `false`
- `confidence level`: 中高
- 核心数字审计：`PASS / publishable`，22/22 checks verified
- EPS 比较审计：`FAIL / blocked`，只封锁 Q1 basic EPS 比较及其下游结论

## 核心来源

| ID | 来源 | 类型 | 用途 |
|---|---|---|---|
| S001 | SK hynix Q2 2026 Business Results | company_original | 当季报告值 |
| S002 | FY2026 Q2 Earnings Presentation | company_original | 财务报表、产品、指引 |
| S003 | Q2 Official English Replay | official_event_platform | 管理层陈述与 Q&A |
| S004 | KIND IR Schedule | regulatory_filing | 时间与事件性质 |
| S005/S006/S007 | Q1 release/deck/replay | company_original / official_event_platform | 上一季度同源比较 |
| S008 | Yonhap Infomax 14-broker consensus | credible_secondary | 事前收入与经营利润共识 |
| S009 | Yahoo Finance intraday snapshot | market_data_vendor | 盘中方向性反应 |

## 关键缺口

- 官方书面逐字稿和完整官方字幕未发布；完整官方回放已取得。
- Q2 外部审阅尚未完成，半年度报告附注缺失。
- LTA 收入覆盖、取消条款、客户名单和个别价格未披露。
- Q3 收入、经营利润、利润率和 EPS 指引未披露。
- Q1 basic EPS 在 Q2 与 Q1 演示稿之间存在未解决冲突。

## 审计文件

- `audit/core_evidence_audit_input.json`
- `audit/core_evidence_audit_result.json`
- `audit/eps_conflict_audit_input.json`
- `audit/eps_conflict_audit_result.json`
