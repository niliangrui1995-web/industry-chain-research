---
name: ht-local-market-data
description: 只读检查 D:\HT 本地 A 股日线、板块池、厂商财务包和盘后新鲜度。适用于用户指定本地数据或历史日线快照；不用于实时行情、官方披露或账户、委托与日志诊断。
---

# HT Local Market Data

只读使用 `D:\HT` 的盘后本地行情数据。该目录不是官方披露源，也不是实时交易接口。

## 边界

- `.day` 日线、`vipdoc\cw` 财务包和 `hq_cache` 属于 `market_data_vendor`。
- `T0002\blocknew`、概念和自定义板块只属 `secondary_trading_context`。
- 本地数据不能证明客户、订单、收入、真实受益或公司基本面。
- 不读取或总结账户目录、`.pass`、委托/订单、交易历史、密码缓存和日志；本技能绝不写入 `D:\HT`。
- 需要实时分时、当前估值、涨跌停细节或资金流时，改用当前可用行情工具。

2026-07-10 的已验证目录快照见 [references/tested-snapshot-2026-07-10.md](references/tested-snapshot-2026-07-10.md)；当前任务仍需重新检查新鲜度，不能把旧快照当成今日状态。

## 工作流

1. 确认本地文件是用户指定来源，或盘后日线快照已经足够。
2. 先运行窄范围只读检查；说明数据是当日盘后、陈旧、部分还是不可用。
3. 需要个股时先确认市场与代码，只读取对应的 `vipdoc/<市场>/lday/<市场><代码>.day`；例如 `sz300750` 对应 `D:\HT\vipdoc\sz\lday\sz300750.day`。文件不存在或日期不足时报告缺口，避免无目的扫描全目录。
4. `.day` 每条 32 字节，格式为 `<IIIIIfII`：日期、开高低收（价格乘 100）、成交额、成交量、保留字段。
5. `.blk` 只作为候选池；常见市场标记为 `0 -> sz`、`1 -> sh`、`2 -> bj`。
6. `gpcw` 是厂商转换数据；硬财务结论必须回到公告、交易所、CNINFO 或公司 IR。
7. 输出时保留数据路径、最新记录日、覆盖范围、缺口和证据标签。

除非重新发现有效 `.lc1` 文件，否则不要把本目录当分钟数据源。`.lc1` 的结构和 packed date 仅在专项诊断中再解析。

## 只读脚本

下列脚本用于行情目录覆盖率或环境诊断，只枚举 `vipdoc/{sh,sz,bj,ds}/lday` 的市场代码 `.day`、`vipdoc/{sh,sz,bj}/minline` 的市场代码 `.lc1`、`vipdoc/cw` 的 `gpcw` 财务包及个股 `gp` 财务文件、`T0002/blocknew` 的 `.blk`/`blocknew.cfg` 和 `T0002/hq_cache` 的明确核心文件。文件名先通过白名单才查询元数据，不递归扫描或枚举安装根目录、账户和日志目录；所有入口拒绝符号链接、目录联接及其他 reparse point，包括路径祖先。`--codes` 只接受市场前缀和六位代码，仅选择附带展示的样本，不限制行情白名单扫描范围；单只或少量证券的新鲜度查询按上文指定路径读取，不调用全库检查。

```powershell
python .agents/skills/ht-local-market-data/scripts/inspect_ht_data.py --root D:\HT --json
python .agents/skills/ht-local-market-data/scripts/inspect_ht_data.py --root D:\HT --codes sh000001 sz000001 sh600000 sz300750 --json
python .agents/skills/ht-local-market-data/scripts/inspect_ht_data.py --root D:\HT --skip-block-samples --json
```

脚本会拒绝缺少有效市场数据哨兵的空目录。`top_dirs` 只汇总白名单行情文件，并非安装目录总量；`scan_scope` 输出实际白名单、非递归和不跟随链接的范围合同。
