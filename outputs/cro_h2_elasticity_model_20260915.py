# -*- coding: utf-8 -*-
"""
美迪西 vs 益诺思 —— 2026H2（Q3+Q4）扣非业绩弹性测算 + 报告章节生成

数据来源：westock data_finance（income，累计口径），全部为累计数相减得到的单季/半年数。
模型：H2扣非 = H2收入 x GM - H2收入 x 费用率 + 净其他项
      净其他项 = 扣非 - (毛利 - 期间费用)，即减值/税金/少数股东等"拖累项"的合成项
"""
import io, json, os

W = 10000.0            # 万元
Y = 100000000.0        # 亿元

# ---------------- 原始数据（累计口径，单位：元） ----------------
# 美迪西 sh688202
MDX = dict(
    name="美迪西", code="sh688202", mc=13233690124.0,
    # 累计收入
    rev25h1=540407246.88, rev25q3=842964828.95, rev25fy=1163062463.78,
    rev26q1=364644480.63, rev26h1=761474155.85,
    # 累计营业成本
    cost25h1=425621157.53, cost25q3=671463291.73, cost25fy=961177935.32,
    cost26q1=269636182.34, cost26h1=520870306.63,
    # 累计扣非
    dd25h1=-26730367.14, dd25q3=-54874403.88, dd25fy=-181156917.56,
    dd26q1=10876254.05, dd26h1=43026810.95,
    # 累计归母
    np25h1=-12898356.21, np26h1=51602435.50,
    # 费用（累计）: 销售 OperatingExpense / 管理 TotalAdminExpense / 研发 RAndD / 财务 FinancialExpense
    se25h1=40301221.76, se25fy=88980533.29, se26h1=45581543.90,
    ae25h1=53498501.37, ae25fy=118026264.25, ae26h1=59483473.57,
    rd25h1=49208967.13, rd25fy=104412783.09, rd26h1=53736749.66,
    fe25h1=3620872.48,  fe25fy=9238197.55,   fe26h1=11089618.83,
    # 季度毛利率（厂商直接给出，用于交叉校验）
    gm26q1=26.055, gm26h1=31.5971,
    # 共识
    cons_pre=0.50 * Y, cons_post=1.1798 * Y, cons_pre_note="浙商证券 2026-06-16", cons_post_note="westock 事件后共识",
)
# 益诺思 sh688710
YNS = dict(
    name="益诺思", code="sh688710", mc=12005824013.4,
    rev25h1=375228566.16, rev25q3=570688076.22, rev25fy=811325228.37,
    rev26q1=210075783.52, rev26h1=464985867.80,
    cost25h1=270080237.35, cost25q3=408927509.59, cost25fy=600734260.37,
    cost26q1=145454283.26, cost26h1=318196957.94,
    dd25h1=-32556590.28, dd25q3=-34759434.49, dd25fy=-53896835.82,
    dd26q1=8819622.89, dd26h1=32895283.98,
    np25h1=-15189524.22, np26h1=39172719.06,
    se25h1=13429762.13, se25fy=31860692.82, se26h1=14418728.68,
    ae25h1=60420225.69, ae25fy=121457475.74, ae26h1=51709497.44,
    rd25h1=22272917.89, rd25fy=45784168.50, rd26h1=24644667.60,
    fe25h1=-1988467.90, fe25fy=-8500858.81, fe26h1=-2187998.13,
    gm26q1=30.761, gm26h1=31.5685,
    cons_pre=1.24 * Y, cons_post=1.3231 * Y, cons_pre_note="华源证券 2026-07-07", cons_post_note="westock 事件后共识",
)


def derive(d):
    """把累计数差分成单季/半年，并计算费用率与净其他项。"""
    r = {}
    r["rev25h2"] = d["rev25fy"] - d["rev25h1"]
    r["rev25q3"] = d["rev25q3"] - d["rev25h1"]
    r["rev25q4"] = r["rev25h2"] - r["rev25q3"]
    r["rev26q2"] = d["rev26h1"] - d["rev26q1"]
    r["cost25h2"] = d["cost25fy"] - d["cost25h1"]
    r["cost25q3"] = d["cost25q3"] - d["cost25h1"]
    r["cost25q4"] = r["cost25h2"] - r["cost25q3"]
    r["cost26q1"] = d["cost26q1"]
    r["cost26q2"] = d["cost26h1"] - d["cost26q1"]
    r["dd25h2"] = d["dd25fy"] - d["dd25h1"]
    r["dd25q3"] = d["dd25q3"] - d["dd25h1"]
    r["dd25q4"] = r["dd25h2"] - r["dd25q3"]
    r["dd26q1"] = d["dd26q1"]
    r["dd26q2"] = d["dd26h1"] - d["dd26q1"]

    # 单季毛利率
    r["gm25q3"] = (d["rev25q3"] - d["cost25q3"] - (d["rev25h1"] - d["cost25h1"])) / r["rev25q3"]
    r["gm25q4"] = 1 - (d["cost25fy"] - d["cost25q3"]) / r["rev25q4"]
    r["gm25h2"] = 1 - r["cost25h2"] / r["rev25h2"]
    r["gm25h1"] = (d["rev25h1"] - d["cost25h1"]) / d["rev25h1"]
    r["gm26q1"] = (d["rev26q1"] - d["cost26q1"]) / d["rev26q1"]
    r["gm26q2"] = (r["rev26q2"] - r["cost26q2"]) / r["rev26q2"]
    r["gm26h1"] = (d["rev26h1"] - d["cost26h1"]) / d["rev26h1"]

    # 期间费用（半年/全年）与费用率
    exp = lambda h1, fy, key: (d[key + "fy"] if fy else d[key + "h1"])
    def fexp(h1=True):
        return ((d["se25h1"] if h1 else d["se25fy"]) + (d["ae25h1"] if h1 else d["ae25fy"])
                + (d["rd25h1"] if h1 else d["rd25fy"]) + (d["fe25h1"] if h1 else d["fe25fy"]))
    r["exp25h1"] = fexp(True)
    r["exp25h2"] = fexp(False) - fexp(True)
    r["exp26h1"] = d["se26h1"] + d["ae26h1"] + d["rd26h1"] + d["fe26h1"]
    r["exprate25h1"] = r["exp25h1"] / d["rev25h1"]
    r["exprate25h2"] = r["exp25h2"] / r["rev25h2"]
    r["exprate26h1"] = r["exp26h1"] / d["rev26h1"]

    # 净其他项（拖累项合成）：扣非 - (毛利 - 期间费用)
    r["other25h1"] = d["dd25h1"] - (r["gm25h1"] * d["rev25h1"] - r["exp25h1"])
    r["other25h2"] = r["dd25h2"] - (r["gm25h2"] * r["rev25h2"] - r["exp25h2"])
    r["other26h1"] = d["dd26h1"] - (r["gm26h1"] * d["rev26h1"] - r["exp26h1"])
    # 非经常性损益（归母 - 扣非）
    r["nonrec26h1"] = d["np26h1"] - d["dd26h1"]
    return r


M = derive(MDX)
N = derive(YNS)

# ---------------- 情景参数（低/中/高），两家对称的收入增速假设 ----------------
GROWTH = [0.20, 0.30, 0.40]
SCEN = {
    "MDX": dict(label=["谨慎", "基准", "乐观"], gm=[0.315, 0.340, 0.360],
                exprate=[0.225, 0.220, 0.215], other=[-2600 * W, -2400 * W, -2200 * W]),
    "YNS": dict(label=["谨慎", "基准", "乐观"], gm=[0.305, 0.320, 0.335],
                exprate=[0.195, 0.190, 0.185], other=[-2600 * W, -2400 * W, -2200 * W]),
}


def scen(d, r, key):
    out = []
    for i in range(3):
        rev = r["rev25h2"] * (1 + GROWTH[i])
        gp = rev * SCEN[key]["gm"][i]
        exp = rev * SCEN[key]["exprate"][i]
        dd = gp - exp + SCEN[key]["other"][i]
        d_rev = rev - r["rev25h2"]
        d_dd = dd - r["dd25h2"]
        out.append(dict(scen=SCEN[key]["label"][i], rev=rev, gm=SCEN[key]["gm"][i],
                        exprate=SCEN[key]["exprate"][i], other=SCEN[key]["other"][i],
                        gp=gp, exp=exp, dd=dd, d_rev=d_rev, d_dd=d_dd,
                        margin=d_dd / d["mc"], marginal=d_dd / d_rev))
    return out


SM, SN = scen(MDX, M, "MDX"), scen(YNS, N, "YNS")

# ---------------- 5x5 敏感性网格：收入同比 x 毛利率 -> 2026H2 扣非 ----------------
GRID_G = [0.10, 0.20, 0.30, 0.40, 0.50]
GRID_GM = {"MDX": [0.30, 0.32, 0.34, 0.36, 0.38], "YNS": [0.28, 0.30, 0.32, 0.34, 0.36]}


def grid(r, key, exprate, other):
    rows = []
    for gm in GRID_GM[key]:
        cells = []
        for g in GRID_G:
            rev = r["rev25h2"] * (1 + g)
            dd = rev * gm - rev * exprate + other
            cells.append(dict(g=g, gm=gm, rev=rev, dd=dd, d_dd=dd - r["dd25h2"]))
        rows.append(cells)
    return rows


GM_M = grid(M, "MDX", 0.22, -2400 * W)
GN_M = grid(N, "YNS", 0.19, -2400 * W)

# ---------------- 触及 FY2026 归母共识所需的 2026H2 毛利率（基准收入情景） ----------------
def need(d, r, s, cons):
    """返回在该收入情景下、触及全年归母共识所需的 H2 毛利率。"""
    need_np_h2 = cons - d["np26h1"]
    need_dd_h2 = need_np_h2 - r["nonrec26h1"]      # 假设 H2 非经常性损益 ≈ H1
    rev = s["rev"]
    need_gm = (need_dd_h2 - s["other"]) / rev + s["exprate"]
    return dict(need_np_h2=need_np_h2, need_dd_h2=need_dd_h2, need_gm=need_gm, rev=rev)


NEED = {
    "MDX": dict(pre=need(MDX, M, SM[1], MDX["cons_pre"]), post=need(MDX, M, SM[1], MDX["cons_post"])),
    "YNS": dict(pre=need(YNS, N, SN[1], YNS["cons_pre"]), post=need(YNS, N, SN[1], YNS["cons_post"])),
}

# ---------------- 摘要输出 ----------------
def pct(x, nd=2):
    return ("%." + str(nd) + "f%%") % (x * 100)


def yi(x, nd=2):
    return ("%." + str(nd) + "f") % (x / Y)


lines = []
lines.append("=== 基线（半年度） ===")
for tag, d, r in (("MDX", MDX, M), ("YNS", YNS, N)):
    lines.append("%s 2025H2: 收入 %.4f亿 GM %s 费用率 %s 净其他 %.0f万 扣非 %.4f亿"
                 % (tag, r["rev25h2"] / Y, pct(r["gm25h2"]), pct(r["exprate25h2"]), r["other25h2"] / W, r["dd25h2"] / Y))
    lines.append("%s 2026H1: 收入 %.4f亿 GM %s 费用率 %s 净其他 %.0f万 扣非 %.4f亿 归母 %.4f亿"
                 % (tag, d["rev26h1"] / Y, pct(r["gm26h1"]), pct(r["exprate26h1"]), r["other26h1"] / W,
                    d["dd26h1"] / Y, d["np26h1"] / Y))
lines.append("")
lines.append("=== 单季毛利率 ===")
for tag, r in (("MDX", M), ("YNS", N)):
    lines.append("%s Q3-25 %s | Q4-25 %s | Q1-26 %s | Q2-26 %s"
                 % (tag, pct(r["gm25q3"]), pct(r["gm25q4"]), pct(r["gm26q1"]), pct(r["gm26q2"])))
lines.append("")
lines.append("=== 单季扣非（万元） ===")
for tag, r in (("MDX", M), ("YNS", N)):
    lines.append("%s Q3-25 %.0f | Q4-25 %.0f | Q1-26 %.0f | Q2-26 %.0f"
                 % (tag, r["dd25q3"] / W, r["dd25q4"] / W, r["dd26q1"] / W, r["dd26q2"] / W))
lines.append("")
lines.append("=== 情景（2026H2） ===")
for tag, S, d in (("MDX", SM, MDX), ("YNS", SN, YNS)):
    for s in S:
        lines.append("%s %s: 收入 %.4f亿(+%s) GM %s 费用率 %s -> H2扣非 %.4f亿 | D扣非 %.4f亿 | D扣非/市值 %s | 边际扣非率 %s"
                     % (tag, s["scen"], s["rev"] / Y, pct(s["rev"] / M["rev25h2"] - 1 if tag == "MDX" else s["rev"] / N["rev25h2"] - 1),
                        pct(s["gm"]), pct(s["exprate"]), s["dd"] / Y, s["d_dd"] / Y, pct(s["margin"]), pct(s["marginal"], 1)))
lines.append("")
lines.append("=== 倍数 ===")
for i in range(3):
    lines.append("%s: %.2fx  (MDX %.4f亿 / YNS %.4f亿)"
                 % (SM[i]["scen"], SM[i]["d_dd"] / SN[i]["d_dd"], SM[i]["d_dd"] / Y, SN[i]["d_dd"] / Y))
lines.append("")
lines.append("=== 触及共识所需 H2 毛利率（基准收入情景） ===")
for tag, d, r, ND, S in (("MDX", MDX, M, NEED["MDX"], SM), ("YNS", YNS, N, NEED["YNS"], SN)):
    lines.append("%s 事件前共识 %.4f亿 -> H2归母需 %.4f亿 H2扣非需 %.4f亿 需GM %s (Q2实际 %s, 缺口 %s)"
                 % (tag, d["cons_pre"] / Y, ND["pre"]["need_np_h2"] / Y, ND["pre"]["need_dd_h2"] / Y,
                    pct(ND["pre"]["need_gm"]), pct(r["gm26q2"]), pct(ND["pre"]["need_gm"] - r["gm26q2"])))
    lines.append("%s 事件后共识 %.4f亿 -> H2归母需 %.4f亿 H2扣非需 %.4f亿 需GM %s (Q2实际 %s, 缺口 %s)"
                 % (tag, d["cons_post"] / Y, ND["post"]["need_np_h2"] / Y, ND["post"]["need_dd_h2"] / Y,
                    pct(ND["post"]["need_gm"]), pct(r["gm26q2"]), pct(ND["post"]["need_gm"] - r["gm26q2"])))
lines.append("")
lines.append("=== 网格 MDX (H2扣非 亿元) ===")
for row in GM_M:
    lines.append("GM %s | " % pct(row[0]["gm"], 1) + " | ".join(yi(c["dd"]) for c in row))
lines.append("=== 网格 YNS (H2扣非 亿元) ===")
for row in GN_M:
    lines.append("GM %s | " % pct(row[0]["gm"], 1) + " | ".join(yi(c["dd"]) for c in row))

io.open("outputs/cro_h2_elasticity_output_20260915.txt", "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))

# 把中间量存盘，供 HTML 生成使用
snap = dict(
    M={k: v for k, v in M.items()}, N={k: v for k, v in N.items()},
    SM=SM, SN=SN, NEED=NEED,
    GM_M=[[c for c in row] for row in GM_M], GN_M=[[c for c in row] for row in GN_M],
    GRID_G=GRID_G,
)
io.open("outputs/cro_h2_elasticity_snapshot_20260915.json", "w", encoding="utf-8").write(
    json.dumps(snap, ensure_ascii=False, default=str))
