# 交易集中度（C5）

这个目录只保存本任务的计算代码、加工后的日度结果和校验清单；不复制 `D:\HT` 的任何原始 `.day` 日线。

## 指标口径

- 指标名：`通达信全A等权 AMOUNT 口径 C5`。
- 分子：当日成交活跃普通 A 股中，按成交额排序前 `ceil(5% × N)` 只个股的成交额之和。成交活跃指 `close > 0`、`amount > 0`、`volume > 0`。
- 分母：全期间使用 `sh880008.day.amount`。
- 分子候选：沪市 `600/601/603/605/688/689`，深市 `000/001/002/003/300/301`；自 `2022-08-02` 起加北交所 `43/83/87/88/92`。
- 不设覆盖率门槛，不插值。只有分母缺失或非正、或当日没有有效候选股时才不输出该日，并记入 manifest。
- 图表叠加：使用 `sz399006.day` 的创业板指收盘价（`close / 100`）作为独立右轴序列；网页会按所选观察区间首个有效日 = 100 归一化。它不参与 C5 的分子、分母或样本筛选。若单日指数源缺失，则该点为缺口，不插值。

该指标以通达信全A等权品种的 `AMOUNT` 字段为分母，并以通达信厂商盘后日线的交易活跃 A 股为分子代理；不是官方逐日全市场成分清单。分子自 `2022-08-02` 纳入北交所候选股；`sh880008` 的历史成分与纳入规则未作为本包的官方逐日成分清单使用。

## 运行

使用项目内带有 NumPy 的 Python 环境执行：

```powershell
& .\.venv_earnings_asr\Scripts\python.exe .\trading_concentration\build_tdx_trading_concentration.py --publish-dir D:\vcp_hunter\基金持仓\public\data
```

脚本两次流式扫描原始 `.day`：第一步形成每个候选股在交易日历上的有效成交额矩阵，第二步按日做前 5% 分位计算。原始数据不被复制到本目录；运行内存主要是约 80 MiB 的临时矩阵。

## 产物

- `data/trading-concentration-dashboard.json`：网页读取的日度数据包；
- `data/trading-concentration-dashboard.manifest.json`：日期范围、哈希、来源快照和口径；
- `data/trading-concentration-daily.csv`：便于人工复核的同口径日度表。

网页发布副本只包含 JSON 与 manifest，位于 `D:\vcp_hunter\基金持仓\public\data\`；脚本先原子替换 payload，再替换带有 payload SHA-256 的 manifest。
