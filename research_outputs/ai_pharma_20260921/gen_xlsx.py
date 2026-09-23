# -*- coding: utf-8 -*-
"""生成 AI制药公司对比表.xlsx（冻结数据来自 evidence_ledger.md，研究时点 2026-09-21）"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:/vcp_hunter/产业链投研/research_outputs/ai_pharma_20260921/AI制药公司对比表.xlsx"

HDR_FILL = PatternFill("solid", fgColor="16324F")
HDR_FONT = Font(bold=True, color="FFFFFF", size=11)
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Border(*[Side(style="thin", color="C9D4DF")] * 4)

wb = Workbook()

# ---------- Sheet 1: 口径与字段说明 ----------
ws0 = wb.active
ws0.title = "口径与字段说明"
rows0 = [
    ["项目", "说明"],
    ["研究执行时点", "2026-09-21；数据为截至该时点可查的最新公开资料"],
    ["数据来源与证据等级", "官方披露（业绩公告/招股书/公司官网新闻稿）=硬证据；券商研报/权威媒体=次级证据；咨询机构估算=机构观点。每行数据标注证据编号E-xxx，完整链接见HTML报告页尾"],
    ["统一维度定义", "业务定位/技术平台与模型/研发方向/管线最高阶段/代表性合作与临床进展/融资与商业模式，与HTML报告第02章一致"],
    ["事实与推断分层", "本表只收录事实与公开报道；壁垒、趋势等推断性内容仅存在于HTML报告并单独标注"],
    ["口径冲突处理", "中国AI制药市场规模存在F&S口径（2026E约20.4亿元）与Grand View口径（2025年1.336亿美元）等差异，报告并列呈现、不做平均"],
    ["假设与限制", "未上市公司融资以公开报道最近轮次为准，可能存在未披露轮次；合作金额为“潜在总额”时非确定收入；查不到的字段写N/A"],
    ["配套文件", "决策看板_AI制药.html（叙事报告与证据链）；evidence_ledger.md（冻结证据台账，sha256=81c6326c...04054）"],
    ["免责声明", "本表基于公开资料整理，不构成投资建议"],
]
for r in rows0:
    ws0.append(r)
ws0.column_dimensions["A"].width = 22
ws0.column_dimensions["B"].width = 110
for c in ws0[1]:
    c.fill = HDR_FILL; c.font = HDR_FONT
for row in ws0.iter_rows(min_row=2):
    for c in row:
        c.alignment = WRAP; c.border = THIN
ws0.freeze_panes = "A2"

# ---------- Sheet 2: 公司对比主表 ----------
ws1 = wb.create_sheet("公司对比主表")
hdr = ["公司", "资本状态/代码", "成立时间/创始人", "核心业务定位", "AI技术平台与模型/算法类型",
       "主要研发方向", "管线最高阶段（截至2026-09）", "代表性合作/临床进展",
       "公开融资与商业模式", "2026年最新经营信号", "证据编号"]
ws1.append(hdr)
data = [
    ["晶泰控股 XtalPi", "港股 02228.HK", "2015/温书豪、马健、赖力鹏（MIT）",
     "AI+机器人驱动的药物发现与AI4S基础设施平台（药物发现50.8%+AI4S 49.2%）",
     "量子物理+AI+机器人实验；小分子/大分子/多肽/小核酸四大平台；300+自动化实验工站；科学智能体（L1-L5分级，部分场景L4）；XtalPi Science平台(2026-07)",
     "小分子、抗体/双抗、多肽、小核酸、分子胶；材料等AI4S场景",
     "3条临床（合作+自研）、10+条IND获批/准备、近10条PCC",
     "礼来：2.5亿美元小分子管线合作+3.45亿美元AI双抗合作（已收第二笔1900万美元）；交付礼来千万级化合物存储系统；孵化剂泰科技IPO",
     "已上市。2026H1收入3.936亿元(剔除高基数+73.8%)；净亏损2.249亿元、经调整净亏损1.055亿元；现金86.71亿元。模式：平台服务+模型授权+管线交易+生态投资",
     "AI4S收入1.935亿元(+136.4%)；累计50万+条真实实验记录(约80%失败负样本)",
     "E-004, E-005"],
    ["英矽智能 Insilico", "港股 03696.HK（2025-12-30上市）", "2014/Alex Zhavoronkov",
     "端到端生成式AI创新药Biotech：Pharma.AI平台+自研管线+BD授权",
     "PandaOmics(靶点发现)+Chemistry42(生成化学)；PandaClaw/LabClaw智能体；LifeStar2自动化实验室；ScienceMMAI Gym",
     "小分子（纤维化、肿瘤、免疫、代谢、衰老）",
     "III期：Rentosertib(TNIK/IPF)全球首个AI发现靶点+AI设计分子药物，2026-09-10 III期首例入组(北京协和医院)；累计31款PCC、13款IND",
     "2026年内签约合作约73亿美元(累计近110亿美元)：礼来、施维雅、SK生物制药、武田(最高6亿美元)等",
     "IPO募22.77亿港元(1427倍超购)。2026H1收入1.063亿美元(+287.2%)、经调整利润0.51亿美元(首次半年度盈利)；现金+定存约4.67亿美元。模式：管线BD授权为主+平台订阅",
     "2026H1扭亏；III期结果预计2029年前后读出",
     "E-006, E-007, E-008"],
    ["百图生科 BioMap", "未上市（2026-03港股保密递表）", "2020-08/李彦宏(董事长)、CEO刘维",
     "生物计算引擎驱动的创新药物研发平台（大模型即服务，不做药）",
     "xTrimo V4全模态生命科学大模型(2680亿参数、300+任务SOTA)；BioMap OS研发操作系统；干湿闭环",
     "大分子/蛋白质：抗体设计、蛋白药物、RNA(RNAGenesis)、免疫(ImmuBot)；靶点发现",
     "自主管线临床前；60+个PoC项目",
     "赛诺菲：1000万美元预付款、潜在总额超10亿美元；石药集团、大北农；800+机构用户、30+头部企业客户",
     "累计融资超2亿美元(GGV纪源、君联、蓝驰、百度；2024年香港投资管理公司领投)；2025-09百度系退出直接股东；2026-03保密递表(中金/大摩/瑞银)。模式：模型授权+研发服务+里程碑；尚未盈利",
     "IPO推进中；收入兑现依赖客户管线成功",
     "E-009"],
    ["深势科技 DP Technology", "未上市（2025-12 C轮，估值超60亿元）", "2018/张林峰、孙伟杰（鄂维南院士学派）",
     "AI for Science基础设施（制药为生命科学板块，另有材料/能源）",
     "深度势能DPA系列(DPA-4：Matbench Discovery与SPICE-MACE-OFF世界第一)；玻尔科研空间站；Hermite药物设计；SciMaster智能体",
     "微观尺度模拟、小分子/药物计算设计、材料与电池；无自研药物管线",
     "N/A（平台/工具公司）；服务客户100+条研发管线",
     "复星医药、国药集团、翰森、华东医药、东阳光药、齐鲁等70+生命科学企业；宁德时代、比亚迪(材料)；1000+高校、300万+科学家用户",
     "融资至C轮：天使(2020 BV百度风投)→A(2021高瓴)→B(2022启明)→B+(2023.8超7亿元,华为哈勃等)→B++(2024.1数亿元)→C(2025.12超8亿元,达晨/京国瑞/联想创投/元禾璞华)。模式：Science as a Service",
     "C轮后估值超60亿元；DPA-4国际榜单第一",
     "E-010"],
    ["剂泰科技 METiS", "港股 07666.HK（2026-05-13上市）", "2020/陈红敏(美国工程院院士)、赖才达、王文首（MIT）",
     "全球首家AI驱动纳米递送(LNP/制剂)平台公司（“AI药物递送第一股”）",
     "NanoForge：千万级可电离脂质库(全球最大)、脂质从头生成算法与脂质语言模型；AiLNP/AiRNA/AiProtein/AiTEM四大方案；智能体ALAN",
     "药物递送(8器官靶向,肝靶向超基准20倍)、mRNA疗法、小分子制剂改良、动物健康",
     "III期完成：MTS-004(PBA)为中国首个完成III期的AI赋能制剂新药；另有3条临床、1条pre-NDA、4条临床前、2条动物保健；肝癌mRNA管线获FDA孤儿药资格",
     "30+全球合作伙伴；AiTEM在恒瑞医药本地化部署；普洛药业“AI+CDMO”合作",
     "IPO发行价10.50港元、首日+170%、市值274亿港元、募超21亿港元(6911倍认购)；2025年收入1.05亿元(MTS-004首付款)；2026H1营收1.543亿元(+13399%)、经调整净亏损收窄56.4%。模式：平台合作+产品合作双轮",
     "晶泰科技为最早投资人；红杉种子单列后首个IPO",
     "E-011, E-012"],
    ["望石智慧 StoneWise", "未上市（B+轮后）", "2018/CEO周杰龙",
     "AI驱动小分子药物早研平台（平台+产业合作+自研管线）",
     "多模态AI 3D分子生成大模型(Nature Machine Intelligence 2024)；MolVado设计平台；MolVortex早研智能体(2025)；数据资产：200亿+小分子库、2亿+虚拟复合物库、300万+电子云密度库；自有化学实验室干湿闭环",
     "小分子（苗头发现、骨架跃迁、成药性优化）；内部管线聚焦肿瘤与自免",
     "I期：自研HPK1口服抑制剂SWA1211于2025-06获中美双报临床许可；内部10余条管线",
     "客户100+：武田、拜耳、辉瑞、齐鲁、微芯、泰德；某头部药企3个月获全新骨架百纳摩尔级分子(成本降约80%)；2026-05与广药集团、华为三方生态合作",
     "B轮+B+轮合计超1亿美元；2026-03福布斯中国行业发展领军企业(唯一AI制药)。模式：平台服务+自研管线",
     "助力客户发现20+早期候选药物",
     "E-013"],
    ["冰洲石生物 Accutar", "未上市（私营，中美双布局）", "2015/Dr. Jie Fan",
     "AI+物理建模驱动的靶向蛋白降解/诱导邻近新药公司",
     "深度学习+物理建模+语言模型干湿闭环；PROTAC、PPI-TAC、RIPTAC新模态；FDA申报辅助AI工具",
     "口服靶向蛋白降解剂(ER/AR/BTK)、诱导邻近；肿瘤为主",
     "3条I期(中美)：AC699(ERα,FDA快速通道,ASCO2024 ORR 21%/ESR1突变50%)、AC0176(AR,中美双报+快速通道)、AC0676(BTK PPI-TAC,ASH2024数据)；4个项目获FDA临床许可",
     "2026-06/07与东阳光药成立NewCo开发RIPTAC(首发mCRPC,全球市场2024年约120亿美元)；Evommune AI药物发现合作",
     "累计融资N/A（公开未披露最新总额）。模式：自研管线+NewCo合资+平台合作",
     "RIPTAC为全球前沿赛道(仅Halda/强生进入临床)",
     "E-014"],
    ["宇道生物 Nutshell", "未上市（2026-09 C1轮）", "2013/张健(上海交大特聘教授)",
     "AI原生Biotech：AI+变构机制攻克难成药靶点",
     "AlloMatrix蛋白构象调控数据库(全球规模领先,源于湿实验)；AlloStar平台；全球首个变构特异性分子力场APSF；AlloWaves位点识别；AlloLig生成式设计(Diffusion/Flow)",
     "变构小分子(激动/稳定/降解/PPI调节)；转录因子等难成药靶标；肿瘤、中枢神经、自免、代谢",
     "I期(国际多中心,将II期)：NTS071/Dalretapopt(p53 Y220C)，截至2026-06入组18例、200mg+剂量组多例PR含1例CR；近20条自研管线；NRF2分子胶2026Q4中美I期",
     "竞品参照：PMV同靶点rezatapopt已注册性II期；公司口径NTS071生化活性优于PMV分子约20倍",
     "2026-09-15完成数千万美元C1轮(信宸资本、德诚资本领投,达晨财智、中生锡创鼎祺参投)。模式：自研管线导向",
     "I期获人体PoC信号(样本小,初步数据)",
     "E-015"],
]
for r in data:
    ws1.append(r)
widths = [16, 16, 18, 30, 42, 26, 36, 40, 44, 30, 14]
for i, w in enumerate(widths, 1):
    ws1.column_dimensions[get_column_letter(i)].width = w
for c in ws1[1]:
    c.fill = HDR_FILL; c.font = HDR_FONT; c.alignment = Alignment(wrap_text=True, vertical="center")
for row in ws1.iter_rows(min_row=2):
    for c in row:
        c.alignment = WRAP; c.border = THIN
ws1.auto_filter.ref = f"A1:K{ws1.max_row}"
ws1.freeze_panes = "B2"

# ---------- Sheet 3: A股可比标的映射 ----------
ws2 = wb.create_sheet("A股可比标的映射")
hdr2 = ["公司（代码）", "市场", "AI相关布局（事实）", "与原生AI制药龙头的差距", "概念纯度(推断)", "证据编号"]
ws2.append(hdr2)
data2 = [
    ["成都先导 688222.SH", "A股", "全球最大DEL库(5000亿+分子)；“DEL+AI+自动化”平台HAILO、智能体HANDS；自研HG254完成PCC；设灵擎数智、入股科迈生物(晶泰+百奥赛图)", "AI服务于DEL筛选主业，无端到端自研管线", "中", "E-016"],
    ["泓博医药 301230.SZ", "A股", "DiOrion CADD/AIDD平台累计服务80个新药项目、6个I期、1个II期、40家药企客户", "项目制CRO属性强，模型与数据资产披露有限", "中", "E-016"],
    ["皓元医药 688131.SH", "A股", "分子砌块+CDMO；MedChemAI平台、一站式药物筛选平台", "AI为辅助工具，收入贡献占比小", "低-中", "E-016"],
    ["药明康德 603259.SH / 康龙化成 300759.SZ", "A股", "AI赋能CRO主业(内部研发工具)", "综合CRO，AI是效率变量", "低", "E-016"],
    ["恒瑞医药 600276.SH 等创新药企", "A股", "自建灵枢AI平台覆盖分子/临床/药学全流程", "估值由管线而非AI驱动", "低", "E-016"],
    ["百普赛斯/义翘神州/近岸蛋白/奥浦迈/纳微科技/百奥赛图2315.HK/华大智造", "A股/港股", "AI候选分子爆发带动蛋白表达、体外验证、模式动物、测序需求", "非AI公司，确定性最高弹性最低", "间接受益", "E-016"],
    ["维亚生物 01873.HK(参照)", "港股", "2025年收入17.29亿元、净利2.69亿元；AIDD累计196个项目、AI相关收入约占CRO总收入12%", "结构生物学+AI干湿闭环CRO，是“CRO+AI”标尺", "中", "E-017"],
]
for r in data2:
    ws2.append(r)
for i, w in enumerate([34, 10, 52, 34, 12, 10], 1):
    ws2.column_dimensions[get_column_letter(i)].width = w
for c in ws2[1]:
    c.fill = HDR_FILL; c.font = HDR_FONT
for row in ws2.iter_rows(min_row=2):
    for c in row:
        c.alignment = WRAP; c.border = THIN
ws2.auto_filter.ref = f"A1:F{ws2.max_row}"
ws2.freeze_panes = "A2"

wb.save(OUT)
print("saved", OUT)
