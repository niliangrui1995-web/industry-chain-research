# -*- coding: utf-8 -*-
"""在 HTML/MD 顶部插入「与今日既有报告的区分」说明。"""
import os

DEL = r'D:\vcp_hunter\产业链投研\deliverables'

MD = os.path.join(DEL, '板块多周期共振分析_20260921.md')
HTML = os.path.join(DEL, '多周期共振_20260921.html')

MD_INSERT = (
    '---\n\n'
    '> **⚠ 与今日既有报告的区分**：2026-09-21 当日已存在一份同批标的的报告\n'
    '> `deliverables/technical-analyst/2026-09-21/关注个股与AI硬件-明日盯盘报告.md`，\n'
    '> 其采用**「临界度」框架**（最可能给出突破/破位信号的标的）。本份采用**多周期共振框架**（日/周/月趋势一致性），\n'
    '> 二者视角互补、名单不同，建议对照阅读而非互相印证。\n'
    '>\n'
    '> **本份的复权口径**：以通达信 MCP 官方前复权日线标定复权因子（非自行推算），\n'
    '> 检测窗口限定 130 个交易日——MACD 的 EMA 冲击响应在该窗口后衰减至 1e-10 量级，\n'
    '> 故更早期的历史除权对当前指标无实质影响，不纳入修正。\n\n'
    '---\n\n## 一、核心结论'
)

HTML_INSERT = (
    '<div class="warn"><b>⚠ 与今日既有报告的区分：</b>2026-09-21 当日已存在一份同批标的的报告 '
    '<span class="mono">deliverables/technical-analyst/2026-09-21/关注个股与AI硬件-明日盯盘报告.md</span>，'
    '其采用<b>「临界度」框架</b>（最可能给出突破/破位信号的标的）。本份采用<b>多周期共振框架</b>（日/周/月趋势一致性），'
    '二者视角互补、名单不同，建议对照阅读而非互相印证。<br>'
    '<b>本份的复权口径：</b>以通达信 MCP 官方前复权日线标定复权因子（非自行推算），'
    '检测窗口限定 130 个交易日——MACD 的 EMA 冲击响应在该窗口后衰减至 1e-10 量级，'
    '故更早期的历史除权对当前指标无实质影响，不纳入修正。</div>'
)

# ---- MD ----
s = open(MD, encoding='utf-8').read()
A = '---\n\n## 一、核心结论'
if '⚠ 与今日既有报告的区分' not in s:
    assert s.count(A) == 1, ('MD anchor count', s.count(A))
    s = s.replace(A, MD_INSERT)
    open(MD, 'w', encoding='utf-8').write(s)
print('MD ok')

# ---- HTML ----
h = open(HTML, encoding='utf-8').read()
A = '<h2>一、核心结论</h2><div class="card">'
if '⚠ 与今日既有报告的区分' not in h:
    assert h.count(A) == 1, ('HTML anchor count', h.count(A))
    h = h.replace(A, HTML_INSERT + A)
    open(HTML, 'w', encoding='utf-8').write(h)
print('HTML ok')

# ---- 校验 ----
for p, ext in [(MD, 'md'), (HTML, 'html')]:
    b = open(p, 'rb').read()
    t = b.decode('utf-8')
    print('%s bytes=%d 乱码=%d None=%d 锚点=%d' % (
        ext, len(b), t.count('\ufffd'), t.count('>None<'), t.count('⚠ 与今日既有报告的区分')))
    if ext == 'html':
        import re
        for tag in ['div', 'table', 'details']:
            o = len(re.findall('<%s[ >]' % tag, t))
            c = len(re.findall('</%s>' % tag, t))
            print('   <%s> %d/%d %s' % (tag, o, c, 'OK' if o == c else 'MISMATCH'))
