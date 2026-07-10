---
name: ht-local-market-data
description: Read and validate the user's local C:\zd_huatai HT/TongdaXin market-data folder. Use for manually refreshed A-share .day daily K-lines, local block pools, hq_cache vendor tables, gpcw financial packages, or post-close freshness checks. Output is market_data_vendor or secondary_trading_context only. Never inspect account, password, order,委托 or log details unless the user explicitly requests that diagnostic.
---

# HT Local Market Data

只读使用 `C:\zd_huatai` 的盘后本地行情数据。该目录不是官方披露源，也不是实时交易接口。

## 边界

- `.day` 日线、`vipdoc\cw` 财务包和 `hq_cache` 属于 `market_data_vendor`。
- `T0002\blocknew`、概念和自定义板块只属 `secondary_trading_context`。
- 本地数据不能证明客户、订单、收入、真实受益或公司基本面。
- 不读取或总结账户目录、`.pass`、委托/订单、交易历史、密码缓存和日志；本技能绝不写入 `C:\zd_huatai`。
- 需要实时分时、当前估值、涨跌停细节或资金流时，改用当前可用行情工具。

2026-07-10 的已验证目录快照见 [references/tested-snapshot-2026-07-10.md](references/tested-snapshot-2026-07-10.md)；当前任务仍需重新检查新鲜度，不能把旧快照当成今日状态。

## 工作流

1. 确认本地文件是用户指定来源，或盘后日线快照已经足够。
2. 先运行窄范围只读检查；说明数据是当日盘后、陈旧、部分还是不可用。
3. 需要个股时只解析指定代码，避免无目的扫描全目录。
4. `.day` 每条 32 字节，格式为 `<IIIIIfII`：日期、开高低收（价格乘 100）、成交额、成交量、保留字段。
5. `.blk` 只作为候选池；常见市场标记为 `0 -> sz`、`1 -> sh`、`2 -> bj`。
6. `gpcw` 是厂商转换数据；硬财务结论必须回到公告、交易所、CNINFO 或公司 IR。
7. 输出时保留数据路径、最新记录日、覆盖范围、缺口和证据标签。

除非重新发现有效 `.lc1` 文件，否则不要把本目录当分钟数据源。`.lc1` 的结构和 packed date 仅在专项诊断中再解析。

## 只读脚本

```powershell
python .agents/skills/ht-local-market-data/scripts/inspect_ht_data.py --root C:\zd_huatai --json
python .agents/skills/ht-local-market-data/scripts/inspect_ht_data.py --root C:\zd_huatai --codes sh000001 sz000001 sh600000 sz300750 --json
python .agents/skills/ht-local-market-data/scripts/inspect_ht_data.py --root C:\zd_huatai --skip-block-samples --json
```

脚本会拒绝缺少有效市场数据哨兵的空目录，并跳过账户、交易和日志边界。
