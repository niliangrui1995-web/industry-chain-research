# -*- coding: utf-8 -*-
"""生成 HTML body 片段（供 render.py 套壳）"""
import json, os, html, re

BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
OUT = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260922/'
DELIV = 'D:/vcp_hunter/产业链投研/deliverables/technical-analyst/2026-09-22/'
os.makedirs(DELIV, exist_ok=True)

bm = json.load(open(BASE + 'block_members.json', encoding='utf-8'))
lab = {r['full']: r for r in json.load(open(BASE + 'labeled.json', encoding='utf-8'))['rows']}

md = open(OUT + 'report.md', encoding='utf-8').read()


def e(s):
    return html.escape(str(s), quote=False)


def cls_pct(v):
    try:
        f = float(str(v).replace('%', '').replace('+', ''))
    except Exception:
        return ''
    return 'up' if f > 0 else ('dn' if f < 0 else '')


def md_table_to_html(t):
    rows = [r for r in t.strip().split('\n') if r.strip().startswith('|')]
    out = ['<div class="table-scroll"><table>']
    for ri, r in enumerate(rows):
        cells = [c.strip() for c in r.strip().strip('|').split('|')]
        if set(''.join(cells)) <= set('-: '):
            continue
        tag = 'th' if ri == 0 else 'td'
        out.append('<tr>' + ''.join('<%s>%s</%s>' % (tag, e(c), tag) for c in cells) + '</tr>')
    out.append('</table></div>')
    return '\n'.join(out)


# ---- 解析 md 报告为 section ----
def grab(start, end=None):
    i = md.index(start)
    j = md.index(end, i) if end else len(md)
    return md[i:j]


sec_concl = grab('## 一、核心结论', '## 二、')
sec_pm = grab('## 二、筛选名单 · 维度一', '## 三、')
sec_nd = grab('## 三、筛选名单 · 维度二', '## 四、')
sec_snap = grab('## 四、盘中快照对照表', '## 五、')
sec_blocks = grab('## 五、两个板块的完整个股清单', '## 六、')
sec_flags = grab('## 六、数据不足', '## 七、')
sec_method = grab('## 七、方法、口径与限制', '## 八、')
sec_risk = grab('## 八、风险提示', '### 免责声明')


def md_block_to_html(t):
    """md 片段 -> HTML：表格、标题、列表、段落"""
    lines = t.split('\n')
    out = []
    buf = []
    tbl = []

    def flush_buf():
        if buf:
            txt = ' '.join(x.strip() for x in buf if x.strip())
            if txt:
                txt = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(txt))
                out.append('<p>%s</p>' % txt)
            buf.clear()

    def flush_tbl():
        nonlocal tbl
        if tbl:
            out.append(md_table_to_html('\n'.join(tbl)))
            tbl = []

    for ln in lines:
        s = ln.strip()
        if s.startswith('|'):
            flush_buf()
            tbl.append(s)
            continue
        flush_tbl()
        if s.startswith('### '):
            flush_buf()
            out.append('<h4>%s</h4>' % e(s[4:]))
        elif s.startswith('## '):
            flush_buf()
            continue
        elif s.startswith('> '):
            flush_buf()
            t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(s[2:]))
            out.append('<p style="color:var(--text-muted);font-size:.95rem">%s</p>' % t)
        elif re.match(r'^\d+\. ', s):
            flush_buf()
            t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(s))
            out.append('<p style="padding-left:1.2em;text-indent:-1.2em;margin-bottom:10px">%s</p>' % t)
        elif s.startswith('- '):
            flush_buf()
            t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(s[2:]))
            out.append('<p style="padding-left:1.2em;text-indent:-1.2em;margin-bottom:8px">• %s</p>' % t)
        elif s == '---' or s == '':
            flush_buf()
        else:
            buf.append(s)
    flush_buf()
    flush_tbl()
    return '\n'.join(out)


# ---- 逐只个股卡片 ----
def cards_from(sec):
    parts = re.split(r'\n### ', sec)
    body = md_block_to_html(parts[0].replace('## 二、筛选名单 · 维度一：今日下午（9/22 下午盘中）', '')
                            .replace('## 三、筛选名单 · 维度二：明后天（9/23–9/24）', ''))
    res = ['<div class="passage-card">', body, '</div>']
    for p in parts[1:]:
        lines = p.split('\n')
        title = lines[0]
        rest = '\n'.join(lines[1:])
        h = md_block_to_html(rest)
        res.append('<div class="passage-card"><h3>%s</h3>%s</div>' % (e(title), h))
    return '\n'.join(res)


# ---- 板块清单 ----
blocks_html = []
for b in ['关注个股', 'AI硬件']:
    d = bm[b]
    tbl = open(OUT + 'tbl_%s.md' % b, encoding='utf-8').read()
    blocks_html.append(
        '<div class="passage-card"><h3>%s　<span style="font-size:.9rem;color:var(--text-muted);font-weight:400">'
        '文件 D:\\HT\\T0002\\blocknew\\%s　共 %d 只</span></h3>%s</div>'
        % (e(b), e(d['file']), len(d['members']), md_table_to_html(tbl)))
blocks_html = '\n'.join(blocks_html)

B = []
A = B.append

A('<section id="conclusion" data-nav="核心结论">')
A('  <div class="conclusion-wrap">')
A('    <div class="conclusion-card">')
A('      <div class="cc-question">本次任务</div>')
A('      <div class="cc-question-text">解析通达信「关注个股」与「AI硬件」两个板块，并分「今日下午」「明后天」两个时间维度做纯技术面筛选</div>')
A('      <div class="cc-snapshot">')
A('        <div class="cc-snapshot-label">数据快照</div>')
A('        <div class="cc-snapshot-grid">')
A('          <div class="cc-snap-cell"><div class="cc-snap-cell-label">标的合计</div><div class="cc-snap-cell-value">126</div><div class="cc-snap-cell-sub">关注个股 42 + AI硬件 84</div></div>')
A('          <div class="cc-snap-cell"><div class="cc-snap-cell-label">日线截止</div><div class="cc-snap-cell-value" style="font-size:1.05rem">2026-09-21</div><div class="cc-snap-cell-sub">本地 vipdoc 完整日线</div></div>')
A('          <div class="cc-snap-cell"><div class="cc-snap-cell-label">盘中快照</div><div class="cc-snap-cell-value" style="font-size:1.05rem">09-22 11:30</div><div class="cc-snap-cell-sub">通达信实时行情</div></div>')
A('          <div class="cc-snap-cell"><div class="cc-snap-cell-label">两维度入选</div><div class="cc-snap-cell-value">10</div><div class="cc-snap-cell-sub">下午 5 + 明后天 5</div></div>')
A('        </div>')
A('      </div>')
A('      <div class="cc-headline-label">核心结论</div>')
A('      <div class="cc-headline">今日上午两个板块<strong>内部严重分化，不是板块整体行情</strong>：AI硬件高位股集体回调（源杰 <span class="dn">−2.59%</span>、仕佳 <span class="dn">−2.73%</span>、长芯博创 <span class="dn">−2.63%</span>、百奥赛图 <span class="dn">−2.90%</span>），而煤炭与部分医药、光通信个股逆势走强（诺诚健华 <span class="up">+3.09%</span>、亨通 <span class="up">+2.86%</span>、陕西煤业 <span class="up">+0.70%</span>、昊华能源 <span class="up">+0.59%</span>）。两个维度合计选出 <strong>10 只</strong>。</div>')
A('      <div class="cc-actions">')
A('        <div class="cc-action-row"><div class="cc-action-label">综合信心</div><div class="cc-action-detail"><strong>中</strong>　同向维度 3 个（日线动能、周线阈值、量价）；板块内部方向背离，不构成一致性共振。</div></div>')
A('        <div class="cc-action-row"><div class="cc-action-label">风险等级</div><div class="cc-action-detail"><strong>高</strong>　多只候选 RSI6 达 79–83、KDJ 的 J 值 95–105 处超买区，ATR 百分比普遍 5%–6.6%。</div></div>')
A('        <div class="cc-action-row"><div class="cc-action-label">最该盯的价位</div><div class="cc-action-detail">周线阈值四道关口 —— <strong>联影 103.77、潞安 15.91、联特 319.87、杰普特 458.21</strong>。这四个价位决定周线信号的翻正与否。</div></div>')
A('      </div>')
A('      <div class="cc-vote"><span class="cc-vote-label">三问速答</span>'
  '<span class="cc-vote-tag"><span class="dot" style="background:var(--neu)"></span>现在涨跌：分化，非同向</span>'
  '<span class="cc-vote-tag"><span class="dot" style="background:var(--up)"></span>位置：偏高，多只超买</span>'
  '<span class="cc-vote-tag"><span class="dot" style="background:var(--b1)"></span>盯什么：四个周线阈值</span></div>')
A('    </div>')
A('  </div>')
A('</section>')

A('<section id="pm" data-nav="今日下午">')
A('  <div class="section-head"><div class="section-num">维度一</div><div><h2 class="section-title">今日下午（9/22 下午盘中）</h2>'
  '<div class="section-lede">口径：今日上午已走出明确方向、或正处于关键技术位争夺中，下午为确认窗口。两个板块合计 5 只。</div></div></div>')
A(cards_from(sec_pm))
A('</section>')

A('<section id="nd" data-nav="明后天">')
A('  <div class="section-head"><div class="section-num">维度二</div><div><h2 class="section-title">明后天（9/23–9/24）</h2>'
  '<div class="section-lede">口径：周线阈值在 1–2 个交易日内可及、日线动能方向明确、位置未极端。两个板块合计 5 只。</div></div></div>')
A(cards_from(sec_nd))
A('</section>')

A('<section id="snapshot" data-nav="盘中快照">')
A('  <div class="section-head"><div class="section-num">对照</div><div><h2 class="section-title">盘中快照对照表</h2>'
  '<div class="section-lede">2026-09-22 11:30 前后，通达信实时行情接口。共取 16 只候选标的。</div></div></div>')
A('  <div class="passage-card">%s</div>' % md_block_to_html(sec_snap))
A('</section>')

A('<section id="blocks" data-nav="板块清单">')
A('  <div class="section-head"><div class="section-num">第一步</div><div><h2 class="section-title">两个板块的完整个股清单</h2>'
  '<div class="section-lede">GBK 编码解析 .blk，逐行 7 字符：首位为市场标志（0=深/1=沪/2=京），后 6 位为代码。</div></div></div>')
A(blocks_html)
A('</section>')

A('<section id="flags" data-nav="数据标注">')
A('  <div class="section-head"><div class="section-num">第二步</div><div><h2 class="section-title">数据不足 / 非个股标的标注</h2>'
  '<div class="section-lede">日线样本不足、非个股标的与历史停牌情况单独列出，不参与排序。</div></div></div>')
A('  <div class="passage-card">%s</div>' % md_block_to_html(sec_flags))
A('</section>')

A('<section id="method" data-nav="方法与限制">')
A('  <div class="section-head"><div class="section-num">口径</div><div><h2 class="section-title">方法、口径与限制</h2>'
  '<div class="section-lede">客观数据与主观推断严格分离。</div></div></div>')
A('  <div class="passage-card">%s</div>' % md_block_to_html(sec_method))
A('</section>')

A('<section id="risk" data-nav="风险提示">')
A('  <div class="section-head"><div class="section-num">风险</div><div><h2 class="section-title">风险提示</h2>'
  '<div class="section-lede">聚焦技术面风险，不含基本面与消息面判断。</div></div></div>')
A('  <div class="passage-card">%s</div>' % md_block_to_html(sec_risk))
A('</section>')

body = '\n'.join(B)
open(DELIV + 'panel.body.html', 'w', encoding='utf-8').write(body)
print('body ->', len(body))
