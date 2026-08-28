# 两融网页新增缺口刷新合同

`two_rong_refresh_protocol_version=2026-08-28.1`

本合同仅约束日常自动化。已有历史数据是只读基线：直接使用，不扫描中间日期、不校验历史哈希、不回看、不补抓、不重建。历史文件缺失或异常时停止并报告，不以日常任务修复。

## 固定来源与水位线

| 数据段 | 唯一日常来源 | 仅处理的新增尾部 |
| --- | --- | --- |
| 两市融资余额 | 东方财富数据中心 `RPTA_WEB_RZRQ_LSSH`；沪 `SCDM=007`、深 `SCDM=001` | 仅本地 DFCF 合并表最后日期之后、且本地 TDX `sh000001.day` 已有的日期 |
| 2011-08-03 至 2016-12-30 市值 | 已有东方财富妙想 `entityId=001004`、`ZSZ` 基线 | 永不日常更新；直接复用 |
| 2017-01-03 起市值 | 东方财富 `RPT_VALUEMARKET`，`TRADE_MARKET_CODE=000300` | 仅后 2017 市值表最后日期之后、已落入 DFCF 合并表的日期 |
| 三指数收盘价 | 本地 TDX `sh000001.day`、`sz399106.day`、`sz399006.day`（厂商日线，未经交易所或指数编制方原始链复核） | 仅写入三来源均有同日收盘价的新增网页尾部 |
| 交易日哨兵 | 本地 TDX `sh000001.day` | 只用于判断 DFCF 新增尾部；不作为两融余额或市值数据来源 |

不得切换到交易所、乐咕乐股、旧探索图、官方回退或其他历史链。`RPTA_WEB_RZRQ_LSSH` 与 `RPT_VALUEMARKET` 均为厂商口径；融资余额占市值只能表述为趋势代理，`financial_evidence_audit=N/A/UNSUPPORTED_RATIO_CONTRACT`。

TDX 仅是三指数收盘价的本地厂商输入和交易日哨兵，不得标为交易所官方或指数编制方原始数据。每次成功追加都必须记录当时读入的 TDX 文件 SHA-256 及其覆盖终点；历史尾部若未留存该文件快照，必须在 manifest 中标注 `tail_snapshot_evidence_absent`，不得用之后读取到的文件哈希倒填。

## 唯一刷新入口

```powershell
python scripts/refresh_leverage_dashboard_incremental.py --project-root "D:\vcp_hunter\产业链投研" --fund-root "D:\vcp_hunter\基金持仓" --execute
```

入口只返回并处理尾部窗口：`dfcf_tail_gap_windows` 与 `post2017_market_cap_tail_gap_windows`。它不会把旧缺口扩展成从最早日期到今天的请求；后 2017 市值始终带 `--incremental`。基线不存在时返回 `blocked`，日常任务不得使用 `--bootstrap-full`。

- `no_changes`：没有新增尾部数据；不写数据、不构建、不备份、不发布。
- `pending_dfcf_source` 或 `pending_market_cap_source`：新增尾部尚不可得；报告并停止。
- `updated`：仅在本轮新增数据落地后，以基金项目 `public/data` 的既有网页 JSON 为基线追加新记录，并同步研究仓产物后进入备份与发布。旧记录直接复用，不调用 `build_leverage_dashboard_bundle.py` 重算或校验历史；JSON 文件的原子写回只是交付步骤，不是历史数据重建。

自动化只对返回的新增窗口负责；不得把历史数据质量、旧缺口或既有网页包差异当成本轮任务。
