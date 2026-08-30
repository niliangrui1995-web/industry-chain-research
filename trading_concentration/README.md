# 交易集中度（C5）与 AI 产业链成交额占比

这个目录只保存本任务的计算代码、加工后的日度结果和校验清单；不复制 `D:\HT` 的任何原始 `.day` 日线。

## 指标口径

- 指标名：`通达信全A等权 AMOUNT 口径 C5`。
- 分子：当日成交活跃普通 A 股中，按成交额排序前 `ceil(5% × N)` 只个股的成交额之和。成交活跃指 `close > 0`、`amount > 0`、`volume > 0`。
- 分母：全期间使用 `sh880008.day.amount`。
- 分子候选：沪市 `600/601/603/605/688/689`，深市 `000/001/002/003/300/301`；自 `2022-08-02` 起加北交所 `43/83/87/88/92`。
- 不设覆盖率门槛，不插值。只有分母缺失或非正、或当日没有有效候选股时才不输出该日，并记入 manifest。
- 图表叠加：使用 `sz399006.day` 的创业板指收盘价（`close / 100`）作为独立右轴序列；网页会按所选观察区间首个有效日 = 100 归一化。它不参与 C5 的分子、分母或样本筛选。若单日指数源缺失，则该点为缺口，不插值。
- AI 产业链曲线：自 `2025-01-01` 起，分子为当前 `watchlists/AI产业链.xlsx` 的“AI产业链”工作表中全部当日成交活跃、去重后的 A/BJ 成分股 `AMOUNT` 之和，分母仍为 `sh880008.day.amount`。仅在 C5 成功发布的交易日输出；若当日全 A 无有效样本，C5 与 AI 均不输出。它表示主题成交额占全A等权 AMOUNT，不是 AI 池内的 C5，也不是持仓拥挤或买卖信号。
- AI 股票池按当前工作簿快照回溯，因此不代表历史逐日成分；工作簿 SHA、代码指纹与剔除的非股票占位行都会写入 manifest。成分变化会阻断后续增量追加，要求人工确认后回填。

该指标以通达信全A等权品种的 `AMOUNT` 字段为分母，并以通达信厂商盘后日线的交易活跃 A 股为分子代理；不是官方逐日全市场成分清单。分子自 `2022-08-02` 纳入北交所候选股；`sh880008` 的历史成分与纳入规则未作为本包的官方逐日成分清单使用。

## 运行

使用项目内带有 NumPy 的 Python 环境执行：

```powershell
& .\.venv_earnings_asr\Scripts\python.exe .\trading_concentration\build_tdx_trading_concentration.py --publish-dir D:\vcp_hunter\基金持仓\public\data
```

脚本两次流式扫描原始 `.day`：第一步形成每个候选股在交易日历上的有效成交额矩阵，第二步按日做前 5% 分位计算。原始数据不被复制到本目录；运行内存主要是约 80 MiB 的临时矩阵。

已存在的 C5 发布包首次加入 AI 曲线时，不要全量重算 C5；使用专用迁移入口。它会先校验旧包，仅新增 JSON 顶层 `ai_chain_series`，并断言既有 C5 `records` 与 CSV 字节不变。若工作簿仅修正代码文字、实际成分指纹未变，同一入口只刷新工作簿快照元数据，不重算 AI 或 C5 历史：

```powershell
& .\.venv_earnings_asr\Scripts\python.exe .\trading_concentration\backfill_ai_chain_turnover_share.py --publish-dir D:\vcp_hunter\基金持仓\public\data
```

后续新交易日只能运行 `append_tdx_trading_concentration_tail.py`；它会同步追加 C5 和 AI 子序列，绝不回扫或改写旧 C5 历史。

## 产物

- `data/trading-concentration-dashboard.json`：网页读取的日度数据包；
- `data/trading-concentration-dashboard.manifest.json`：日期范围、哈希、来源快照和口径；
- `data/trading-concentration-daily.csv`：便于人工复核的同口径日度表。

网页发布副本只包含 JSON 与 manifest，位于 `D:\vcp_hunter\基金持仓\public\data\`；C5 保持在 legacy `records` 和 CSV 中，AI 曲线位于 JSON 顶层独立 `ai_chain_series`。脚本先原子替换 payload，再替换带有 payload SHA-256 的 manifest。
