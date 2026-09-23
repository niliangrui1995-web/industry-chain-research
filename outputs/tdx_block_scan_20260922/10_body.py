# -*- coding: utf-8 -*-
"""生成 HTML body 片段（供 render.py 套壳）"""
import json, os, re, html

BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
OUT = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260922/'
DELIV = 'D:/vcp_hunter/产业链投研/deliverables/technical-analyst/2026-09-22/'
os.makedirs(DELIV, exist_ok=True)

bm = json.load(open(BASE + 'block_members.json', encoding='utf-8'))
md = open(OUT + 'final.md', encoding='utf-8').read()


def e(s):
    return html.escape(str(s), quote=False)


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


def grab(a, b=None):
    i = md.index(a)
    j = md.index(b, i) if b else len(md)
    return md[i:j]


sec_concl = grab('## 一、核心结论', '## 二、')
sec_pick = grab('## 二、筛选名单', '## 三、')
sec_snap = grab('## 三、盘中快照对照表', '## 四、')
sec_flags = grab('## 五、数据不足', '## 六、')
sec_method = grab('## 六、方法、口径与限制', '## 七、')
sec_risk = grab('## 七、风险提示', '### 免责声明')


def md_block_to_html(t):
    lines = t.split('\n')
    out, buf, tbl = [], [], []

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
            flush_buf(); tbl.append(s); continue
        flush_tbl()
        if s.startswith('### '):
            flush_buf(); out.append('<h4>%s</h4>' % e(s[4:]))
        elif s.startswith('## '):
            flush_buf(); continue
        elif s.startswith('> '):
            flush_buf()
            out.append('<p style="color:var(--text-muted);font-size:.95rem">%s</p>'
                       % re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(s[2:])))
        elif re.match(r'^\d+\. ', s):
            flush_buf()
            out.append('<p style="padding-left:1.2em;text-indent:-1.2em;margin-bottom:10px">%s</p>'
                       % re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(s)))
        elif s.startswith('- '):
            flush_buf()
            out.append('<p style="padding-left:1.2em;text-indent:-1.2em;margin-bottom:8px">• %s</p>'
                       % re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(s[2:])))
        elif s in ('---', ''):
            flush_buf()
        else:
            buf.append(s)
    flush_buf(); flush_tbl()
    return '\n'.join(out)


def cards_from(sec):
    parts = re.split(r'\n### ', sec)
    body = md_block_to_html(parts[0].replace('## 二、筛选名单 · 明后天（9/23–9/24）· 两个板块合计 5 只', ''))
    res = ['<div class="passage-card">', body, '</div>']
    for p in parts[1:]:
        lines = p.split('\n')
        res.append('<div class="passage-card"><h3>%s</h3>%s</div>'
                   % (e(lines[0]), md_block_to_html('\n'.join(lines[1:]))))
    return '\n'.join(res)


blocks_html = []
for b in ['关注个股', 'AI硬件']:
    d = bm[b]
    tbl = open(OUT + 'tbl_%s.md' % b, encoding='utf-8').read()
    blocks_html.append(
        '<div class="passage-card"><h3>%s　<span style="font-size:.9rem;color:var(--text-muted);font-weight:400">'
        '文件 D:\\HT\\T0002\\blocknew\\%s　共 %d 只</span></h3>%s</div>'
        % (e(b), e(d['file']), len(d['members']), md_table_to_html(tbl)))

B = []
A = B.append

A('<section id="conclusion" data-nav="核心结论">')
A('  <div class="conclusion-wrap"><div class="conclusion-card">')
A('    <div class="cc-question">本次任务</div>')
A('    <div class="cc-question-text">解析通达信「关注个股」与「AI硬件」两个板块，并按「明后天」时间维度做纯技术面筛选</div>')
A('    <div class="cc-snapshot"><div class="cc-snapshot-label">数据快照</div><div class="cc-snapshot-grid">')
A('      <div class="cc-snap-cell"><div class="cc-snap-cell-label">标的合计</div><div class="cc-snap-cell-value">126</div><div class="cc-snap-cell-sub">关注个股 42 + AI硬件 84</div></div>')
A('      <div class="cc-snap-cell"><div class="cc-snap-cell-label">日线截止</div><div class="cc-snap-cell-value" style="font-size:1.05rem">2026-09-21</div><div class="cc-snap-cell-sub">本地 vipdoc 完整日线</div></div>')
A('      <div class="cc-snap-cell"><div class="cc-snap-cell-label">盘中快照</div><div class="cc-snap-cell-value" style="font-size:1.05rem">09-22 14:52</div><div class="cc-snap-cell-sub">大智慧实时行情</div></div>')
A('      <div class="cc-snap-cell"><div class="cc-snap-cell-label">入选</div><div class="cc-snap-cell-value">5</div><div class="cc-snap-cell-sub">两板块合计</div></div>')
A('    </div></div>')
A('    <div class="cc-headline-label">核心结论</div>')
A('    <div class="cc-headline">下午盘面<strong>发生反转，AI硬件内部分化加剧</strong>。上午 11:30 时联特科技还是 <span class="dn">−0.90%</span>、源杰科技 <span class="dn">−2.59%</span>；到 14:52，联特科技已拉至 <span class="up">+2.11%</span>（最高 335.12，突破上周高 326.56），而源杰科技跌幅扩大至 <span class="dn">−4.49%</span>（跌破 MA5 1793.03）。同板块内出现完全相反的方向。</div>')
A('    <div class="cc-actions">')
A('      <div class="cc-action-row"><div class="cc-action-label">综合信心</div><div class="cc-action-detail"><strong>中</strong>　同向维度 3 个（周线柱翻正、日线动能、量能配合）；但板块内部方向背离，AI硬件高位股仍在释放抛压。</div></div>')
A('      <div class="cc-action-row"><div class="cc-action-label">风险等级</div><div class="cc-action-detail"><strong>高</strong>　入选名单中 4 只 KDJ 的 J 值 ≥ 91（联特 109.1、诺诚健华 100.2、纳微 91.2），纳微 pos52=94.7 处 52 周极高位。</div></div>')
A('      <div class="cc-action-row"><div class="cc-action-label">最该盯的价位</div><div class="cc-action-detail">纳微 <strong>47.87</strong>（上周高，差 0.04%）、联特 <strong>326.56</strong>（上周高，刚突破）、陕煤 <strong>26.50</strong>（上周高，差 1.65%）。</div></div>')
A('    </div>')
A('    <div class="cc-vote"><span class="cc-vote-label">三问速答</span>'
  '<span class="cc-vote-tag"><span class="dot" style="background:var(--neu)"></span>现在涨跌：分化，非同向</span>'
  '<span class="cc-vote-tag"><span class="dot" style="background:var(--up)"></span>位置：偏高</span>'
  '<span class="cc-vote-tag"><span class="dot" style="background:var(--b1)"></span>盯什么：三个上周高点</span></div>')
A('  </div></div>')
A('</section>')

A('<section id="picks" data-nav="明后天名单">')
A('  <div class="section-head"><div class="section-num">筛选</div><div><h2 class="section-title">明后天（9/23–9/24）· 两个板块合计 5 只</h2>'
  '<div class="section-lede">口径：周线 MACD 柱已翻正或临界可及、日线动能方向明确、明后天有可量化的观察目标。</div></div></div>')
A(cards_from(sec_pick))
A('</section>')

A('<section id="snapshot" data-nav="盘中快照">')
A('  <div class="section-head"><div class="section-num">对照</div><div><h2 class="section-title">盘中快照对照表</h2>'
  '<div class="section-lede">2026-09-22 14:51–14:52，大智慧实时行情接口，共 20 只。</div></div></div>')
A('  <div class="passage-card">%s</div>' % md_block_to_html(sec_snap))
A('</section>')

A('<section id="blocks" data-nav="板块清单">')
A('  <div class="section-head"><div class="section-num">第一步</div><div><h2 class="section-title">两个板块的完整个股清单</h2>'
  '<div class="section-lede">GBK 编码解析 .blk，逐行 7 字符：首位为市场标志（0=深/1=沪/2=京），后 6 位为代码。</div></div></div>')
A('\n'.join(blocks_html))
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
print('body ->', len(body), '| section', body.count('<section'), body.count('</section>'))
