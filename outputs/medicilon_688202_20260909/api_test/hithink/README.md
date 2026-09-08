# 同花顺 Financial-API 测试：688202.SH 美迪西

测试日期：2026-09-09（Asia/Shanghai）
数据源：同花顺 Financial-API 厂商口径；`thscode=688202.SH`。

## 结论

同花顺接口可识别标的，也能返回最近 20 个季度的合并利润表；但该利润表没有“扣除非经常性损益后归母净利润”金额字段，只有 `parent_holder_net_profit`（归母净利润）。财务指标接口只出现 `index_deduct_weighted_avg_roe`（扣非加权平均 ROE），不提供扣非归母净利润金额。

因此，它**不能单独作为美迪西自上市以来每个季度扣非归母净利润柱状图的完整数据源**。

## 覆盖与口径测试

- `get_a_share_financials_income_statements(period=quarterly, limit=20)` 成功，返回 20 期，覆盖 2021Q3 至 2026Q2。
- 尝试 `start/end` 获取 2019 年上市以来全区间时，服务返回 `code=1004`：`Parameter conflict: limit must not be set together with start/end`；调用方未传 `limit`，但服务端默认值仍被判为冲突。传入 `limit=null` 又返回 `code=1002`。因此当前 MCP 封装下无法用时间区间补齐早期季度。
- 返回字段见 `income_recent20_response_excerpt.json`，其中没有 `deducted_parent_holder_net_profit` 或等价字段。`parent_holder_net_profit` 应按报告期累计值处理；接口未给出单季/累计标记，不能把 Q2、Q3、Q4 直接视为单季度数。
- `get_a_share_financials_indicators` 已抽测 2019 年报、2025 年报、2026 年中报，均未返回扣非归母净利润金额；只有扣非 ROE 比率。

## 原始响应与复核文件

- `metadata_response.json`：代码检索成功响应。
- `income_recent20_response_excerpt.json`：利润表接口成功响应的字段、覆盖范围和首末样本。
- `income_range_attempts.json`：全区间请求的两次失败原始响应。
- `indicator_samples_response.json`：三个报告期的财务指标原始响应。

以上结论只评价该 API 的字段和覆盖能力，不以厂商数据替代交易所或公司披露。
