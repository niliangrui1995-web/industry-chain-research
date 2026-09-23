# -*- coding: utf-8 -*-
"""向 MEMORY.md 的「本地数据契约」一节补充复权甄别方法论。"""
import os

P = r'D:\vcp_hunter\产业链投研\.workbuddy\memory\MEMORY.md'

ANCHOR = '## neodata 行情接口四大坑'

NEW = '''## ⭐ 本地 vipdoc 复权甄别与修正契约（2026-09-21 确立，做技术面必读）

本地 `.day` 是**不复权**数据，直接算 MA/MACD/KDJ 会失真。正确流程：

1. **不要尝试本地 gbbq**。`D:\\HT\\T0002\\hq_cache\\gbbq` 存在且配套 `gbbq.map`（文本：6位代码→偏移），
   但**正文疑似加密、无法解析**；`vipdoc\\cw` 只有 gpbj/gpcw（财务/股本），没有标准 gbbq.bin。别浪费时间。
2. **硬判据甄别真除权**：看单日涨跌幅**是否突破法定限制**（沪主板/深主板 ±10%、科创/创业 ±20%、北交所 ±30%，留 0.5pp 容差）。
   超限 = 必定除权/份额折算；未超限 = 真实成交。**这是唯一可靠的自动判据。**
   ⚠ 反例教训：2026 年 5-8 月系统性暴跌期间，130 日窗口内有 59 只单日跌超 11%，看着像大面积除权，
   实际只有 12 只是真除权。判定前**先对照当日宽基指数**——07-17 创业板 -7.15%/科创50 -7.12%、
   07-20 指数微涨(+0.42%)而 AI 板块个股成片跌停，都是真实行情。**不要一看到群体同步跳空就怀疑数据源。**
3. **检测窗口用 130 个交易日，不必扫全序列**。EMA 冲击响应按 (1-α)^N 衰减，EMA12 α=2/13，
   130 根后已降至 ~1e-10。全序列扫会命中 84 只（含 1993/2005 年历史除权），纯噪音。
4. **复权因子用 tdx MCP 前复权日线标定**，不要自己推算送转比例：
   `tdx_kline(code, setcode, period="4", tqFlag="1", startxh=M-1-i, wantNum=2)` 恰好返回除权日及其前一日两根。
   `f_prev = fq_close[prev]/raw_close[prev]` 应用于 index<=prev 的全部 OHLC；`f_cur` 同理（除权后通常为 1 或 ~0.998，含小额分红）。
5. **⚠ `.day` 有效记录数 ≠ len(file)//32**——文件里混有 `d<=0`/`c<=0` 的废行，read_day 会过滤。
   算 startxh / index **必须用过滤后的序列长度 M**，否则偏移整体差 1，MCP 返回日期对不上。

## neodata 行情接口四大坑'''

s = open(P, encoding='utf-8').read()
if '本地 vipdoc 复权甄别与修正契约' in s:
    print('already present, skip')
else:
    assert s.count(ANCHOR) == 1, ('anchor count', s.count(ANCHOR))
    s = s.replace(ANCHOR, NEW)
    open(P, 'w', encoding='utf-8').write(s)

t = open(P, encoding='utf-8').read()
print('MEMORY.md chars=%d 乱码=%d 锚点=%d' % (
    len(t), t.count('\ufffd'), t.count('本地 vipdoc 复权甄别与修正契约')))
