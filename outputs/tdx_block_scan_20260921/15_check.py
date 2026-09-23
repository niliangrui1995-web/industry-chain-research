# -*- coding: utf-8 -*-
import os, re, io

OUT = r'D:/vcp_hunter/产业链投研/deliverables/technical-analyst/2026-09-21'
p = os.path.join(OUT, '关注个股与AI硬件-本周重点名单.html')
print('exists:', os.path.exists(p), 'bytes:', os.path.getsize(p) if os.path.exists(p) else 0)
s = io.open(p, encoding='utf-8').read()
print('U+FFFD:', s.count('\ufffd'), '| >None<:', s.count('>None<'), '| nan:', s.count('nan'), '| %s:', s.count('%s'))
print('sections:', len(re.findall(r'<section', s)), '| data-nav:', len(re.findall(r'data-nav=', s)),
      '| tr:', len(re.findall(r'<tr', s)))
print('footer:', s.count('<footer'), '| nav:', s.count('<nav'))
print('阈值卡数量(dim):', len(re.findall(r'class="dim"', s)))
# 清理上一版明日文件
for f in ['关注个股与AI硬件-明日盯盘面板.html', '关注个股与AI硬件-明日盯盘报告.md']:
    fp = os.path.join(OUT, f)
    if os.path.exists(fp):
        os.remove(fp)
        print('removed(上一版明日口径):', f)
print('\n当前目录:')
for f in sorted(os.listdir(OUT)):
    print(' ->', f, os.path.getsize(os.path.join(OUT, f)))

# 日志
p2 = r'D:/vcp_hunter/产业链投研/.workbuddy/memory/2026-09-21.md'
s2 = """

## 口径再调整：明日 → 本周剩余 4 个交易日（2026-09-21 22:20）

用户第三次调整口径（下周 → 明天 → **本周接下来几个交易日**）。本次改用**「周线收盘阈值」**方法，是本轮最有价值的方法创新：

**核心方法（可复用）**
- 4 日窗口夹在 1 日（噪声）与 5 日（弱）之间，但本周恰好是**周线完整收出的一周** ⇒ 可观察锚点＝"本周收盘价能否站上周线信号阈值"。
- **周线 MACD 柱翻正价 P\***：DIF、DEA 关于本周收盘价 P 都是线性函数 ⇒ hist(P) 线性 ⇒ 取 P=0 与 P=1 求 hist，线性解出 hist(P\*)=0。（无需二分）
- **周线 MA4 站上价**：P > 前三周收盘和 ÷ 3；**MA12**：P > 前 11 周和 ÷ 11。闭式解。
- **收复上周高点**：P > 上一完整周最高价。
- **衍生风险判据（很实用）**：**周线柱翻正阈值远低于现价 ⇒ 周线多头已充分展开 ⇒ 过度延伸**。
  本池回测"过度延伸"IC 恒为负，故这类应列风险而不列关注。例：百普赛斯 −83%、奥浦迈 −55%、成都先导 −34%、德科立 −35%。

**本周名单（周线阈值离现价最近）**
- 关注个股核心：联影医疗 SH688271（上周周线柱 −0.078 近零；**柱翻正 103.77 / 周线MA4 104.23 / 上周高 103.88 三重阈值重合在 104 一带**，pos60 仅 14.8%、BIAS −1.57% 不透支）、
  潞安环能 SH601699（15.91 同时收复上周高+周线MA4 15.80+MA12 15.76）、陕西煤业 SH601225（周线MA4 需 25.83，+0.51%）。
- AI硬件核心：中际旭创 SZ300308（**站上周线 MA12 仅需 941.15，差 +0.02%**）、
  联特科技 SZ301205（按现价本周周线柱已会翻正，阈值 319.87 < 现价 321）、杰普特 SH688025（柱翻正 458.21，+2.51%）。
- 次要：澜起科技（周线MA12 需 210.31，+0.10%）、中科飞测、瑞芯微。

**重要认知修正**：联影医疗在前两版（下周/明日）被判为"趋势走坏"而排除；
切到本周视角后它反而是**最清晰的周线转折标的**——说明"趋势走坏"不等于"不值得关注"，
**位置低 + 周线阈值可达**本身就是一类机会（且符合回测中"低 RSI 为正"的读数）。

产物：`deliverables/technical-analyst/2026-09-21/关注个股与AI硬件-本周重点名单.{html,md}`，前两版同名文件已清理。
"""
io.open(p2, 'a', encoding='utf-8').write(s2)
d = io.open(p2, encoding='utf-8').read()
assert '周线收盘阈值' in d
print('daily bytes:', len(d.encode('utf-8')))
