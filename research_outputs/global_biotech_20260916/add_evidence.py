# -*- coding: utf-8 -*-
"""向 evidence_ledger.json 追加 E-041~E-046（周期复盘与前瞻章节用），幂等：已存在则跳过。"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PATH = "evidence_ledger.json"

NEW = [
    {
        "id": "E-041",
        "title": "XBI（SPDR 标普生物科技 ETF）历史价格：2021-02-09 盘中历史最高 174.79 美元，2022-05-12 低点 61.78 美元",
        "publisher": "Stocks Price History（行情数据库）",
        "type": "行情数据",
        "url": "https://stockspricehistory.com/quotes/XBI/history/2021-02-09",
        "access": "公开",
        "publishedAt": "2023-02-23",
        "region": "美国",
        "metric": "XBI 历史最高价 174.79 美元（2021-02-09 盘中）；前一日 2021-02-08 收盘 173.99 美元为收盘最高；2022-05-12 最低 61.78 美元，区间最大回撤 -64.5%",
        "strength": "高",
        "limitation": "第三方行情库，与交易所原始数据可能存在微小差异"
    },
    {
        "id": "E-042",
        "title": "CDE《以临床价值为导向的抗肿瘤药物临床研发指导原则》公开征求意见",
        "publisher": "国家药品监督管理局药品审评中心（CDE）",
        "type": "政策/官方",
        "url": "https://www.cde.org.cn/main/news/viewInfoCommon/efae4018f18e00dfcf4433e75cb6ea03",
        "access": "公开",
        "publishedAt": "2021-07-02",
        "region": "中国",
        "metric": "2021-07-02 发布征求意见稿，要求抗肿瘤药临床以最佳治疗方式/药物为对照，直接抬高 me-too 类药物门槛；发布后 A 股/港股医药板块 2021-07-06 集体大跌",
        "strength": "高",
        "limitation": "征求意见稿（正式稿 2021-11 发布），政策影响为市场解读"
    },
    {
        "id": "E-043",
        "title": "港交所生物科技生态圈：2021 年 20 家 18A 公司上市创纪录新高",
        "publisher": "香港交易所",
        "type": "交易所/官方",
        "url": "https://www.hkex.com.hk/Join-Our-Market/Highlight/Biotech-Hub?sc_lang=zh-HK",
        "access": "公开",
        "publishedAt": "2021-12-31",
        "region": "中国香港",
        "metric": "2021 年共 20 家未盈利生物科技公司经 18A 章上市（历史最高）；据市场统计当年募资约 377 亿港元，2018-2021 累计 48 家、约 1,126 亿港元",
        "strength": "高",
        "limitation": "家数为港交所官方口径；募资金额引自市场统计（财华社/沙利文），口径含首发募资"
    },
    {
        "id": "E-044",
        "title": "美联储对疫后高通胀的政策应对（FEDS Notes）",
        "publisher": "美国联邦储备委员会",
        "type": "央行/官方",
        "url": "https://www.federalreserve.gov/econres/notes/feds-notes/the-federal-reserves-responses-to-the-post-covid-period-of-high-inflation-20240214.html",
        "access": "公开",
        "publishedAt": "2024-02-14",
        "region": "美国",
        "metric": "2020-03 降至 0-0.25% 并启动无上限 QE；2021-11 启动 taper（每月减购 150 亿美元），2021-12 加倍提速并删除“暂时性”表述；2022-03 结束购债并首次加息，2022 全年累计加息 425bp 至 4.25-4.50%；2021-10 CPI 同比 6.2%",
        "strength": "高",
        "limitation": "官方复盘文件，无"
    },
    {
        "id": "E-045",
        "title": "美国会调查：FDA 于 2021-06-07 加速批准 Biogen 阿尔茨海默药 Aduhelm 及定价审查",
        "publisher": "美国众议院监督与改革委员会/能源与商务委员会",
        "type": "政府/官方",
        "url": "https://democrats-energycommerce.house.gov/newsroom/press-releases/maloney-and-pallone-release-staff-report-on-review-approval-and-pricing-of",
        "access": "公开",
        "publishedAt": "2022-12-29",
        "region": "美国",
        "metric": "2021-06-07 FDA 不顾咨询委员会全票反对加速批准 Aduhelm（替代终点：淀粉样斑块清除），年费 5.6 万美元；三名咨询委员辞职抗议；2022-04 CMS 严格限制报销，2024-01 Biogen 停产撤市",
        "strength": "高",
        "limitation": "国会调查报告（多数党立场），事实部分与公开记录一致"
    },
    {
        "id": "E-046",
        "title": "默沙东 2024 年报：Keytruda（K药，帕博利珠单抗）销售 295 亿美元（+18%）",
        "publisher": "Merck & Co.（默沙东）",
        "type": "公司/官方",
        "url": "https://www.merck.com/?p=3663043/",
        "access": "公开",
        "publishedAt": "2025-02-04",
        "region": "美国",
        "metric": "2024 年 KEYTRUDA 全球销售 295 亿美元（同比 +18%，剔除汇率 +22%），为全球最畅销药物，占默沙东总营收约 46%；其美国核心专利 2028 年到期，为史上最大单一专利悬崖",
        "strength": "高",
        "limitation": "销售额为官方口径；2028 年专利到期时点引自公开报道与分析师测算"
    },
]

d = json.load(open(PATH, encoding="utf-8"))
ev = d["evidence"]
ids = {e["id"] for e in ev}
added = 0
for item in NEW:
    if item["id"] in ids:
        print("SKIP", item["id"])
        continue
    ev.append(item)
    added += 1
    print("ADD ", item["id"])
json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 回读校验
d2 = json.load(open(PATH, encoding="utf-8"))
ev2 = d2["evidence"]
assert len(ev2) == len(ev) == (40 + added) or len(ev2) == 46, len(ev2)
ids2 = [e["id"] for e in ev2]
assert ids2 == [f"E-{i:03d}" for i in range(1, 47)], ids2[-6:]
for e in ev2:
    assert all(k in e for k in ("id","title","publisher","type","url","access","publishedAt","region","metric","strength","limitation")), e["id"]
print("READBACK_OK total=", len(ev2), "added=", added)
