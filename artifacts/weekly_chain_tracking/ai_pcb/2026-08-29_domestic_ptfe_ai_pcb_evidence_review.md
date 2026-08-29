# 国内 PTFE 应用于 AI PCB：证据化研究

**研究截止日：2026-08-29（Asia/Shanghai）**
**范围：国内企业公开资料；以交易所/法定披露、公司官网产品资料、下游 CCL/PCB 厂资料为主。**
**结论口径：本报告不把“耐腐蚀 PTFE”“通信线缆用 PTFE”“通用高频 CCL”或“公司另有 AI 业务”写成 AI PCB 已兑现。**

## 结论先行

截至截止日，**未发现任何国内企业公开披露完成以下同一料号闭环：**

```text
PTFE 树脂/薄膜（明确牌号）
  → 同一 CCL 或 bondply/粘结片商品牌号
  → 高层板压合、PTH 与可靠性验证
  → AI 服务器/AI 交换机/224G 背板的板厂 AVL 或终端认证
  → 板卡批量出货
  → 同一 PTFE 料号的订单或收入
```

因此，不能写“国内已有 PTFE 厂商在 AI PCB 上实现量产收入”。最接近这个方向的是沃特股份：其受监管披露载体中的管理层表述称 PTFE 薄膜获高频高速 PCB 头部客户认可，并覆盖“服务器用 PCB”；但没有 PTFE 商品牌号、CCL/粘结片牌号、AI 客户、AVL、出货量、订单或 PTFE 专项收入，且同一记录中“AI 服务器”对应的是 LCP 材料，不能迁移给 PTFE。

当前 AI PCB 账本把 `M9+/PTFE/M10 CCL-prepreg` 放在 **2027–2028 的 `watch`**，并非已确认的本土 AI PCB 供货节点；账本也没有牌号级材料、板厂 AVL、交付或收入证据。[当前账本](/D:/vcp_hunter/产业链投研/artifacts/weekly_chain_tracking/ai_pcb/state.md)

## 口径、边界与证据等级

### 本次所说的“AI PCB”

仅指 AI 服务器、AI 交换机、224G/112G 高速互连、背板及相近的刚性多层/高多层 PCB 的材料体系。ABF/BT 封装基板、数据中心铜缆、散热件、耐腐蚀密封件、消费电子 FPC，以及“公司产品可服务 AI 行业”的泛化表述均不在本结论范围。

PTFE 作为低损耗介质体系在高速数字板中**技术上可以成立**，但通常须由完整的 laminate + bondply + 铜箔 + 压合/孔金属化可靠性体系共同实现。Rogers 的 RO1200 官方数据表可作为技术锚：该陶瓷填充、无玻纤增强 PTFE bondply 面向 56/112Gbps，高性能服务器/交换机/存储和背板；这证明材料体系的技术可行性，**不证明任何国产 SKU 已被 AI 客户认证或量产**。[RO1200 官方数据表](https://www.rogerscorp.com/-/media/project/rogerscorp/documents/advanced-electronics-solutions/english/data-sheets/ro1200-bondply-data-sheet.pdf)

| 标签 | 含义 | 本报告中的处理 |
|---|---|---|
| `official_fact`（A） | 交易所/法定披露、公司官网产品资料或下游披露直接证明的事实 | 可写明产品、用途或已披露的非 AI 商业化事实 |
| `management_claim`（B） | 公司调研纪要/管理层表述，缺少命名客户或下游交叉验证 | 只写为“公司称”“客户认可线索”，不等同 AVL、订单或收入 |
| `inference`（C） | 由高速数字材料要求推导的技术可能性 | 仅作背景，不可转成供应关系或兑现事实 |
| `evidence_absent` | 同一 PTFE 料号与 AI 板级材料、客户或收入之间没有公开绑定 | 一律填 `N/A`，不以同公司另一产品线补足 |
| `negative_official` | 公司法定披露明确否认应用 | 明确排除，不写为潜在 AI PCB 兑现 |

阶段字段的含义也严格分开：

- **可用于**：该具体 PTFE 料号被产品资料列为 CCL/高频 PCB 材料，或有清晰的技术适配说明；不等于 AI 导入。
- **已送样/认证**：需要同一料号的客户测试、终端认证或 AVL 证据。“头部客户认可”而没有客户、料号或文件编号，只能算验证线索。
- **已量产导入**：需要同一料号已在所述 AI 板卡/平台持续批供；传统基站、雷达或泛高频 PCB 的量产不外推。
- **已形成收入**：需要同一料号的 AI 相关收入、订单、出货或可核验的客户采购；公司总营收、材料大类收入均不代替。

## 公司逐一核验

表中“AI 阶段”只判断**该 PTFE 产品与 AI PCB 的交集**；若行内写到量产或收入而注明“非 AI”，是为了避免把已经存在的通信/射频商业化错计进 AI。

| 公司 | PTFE 产品/牌号（直接证据） | 已证实的高频/高速 CCL 或 PCB 应用 | 直接下游验证 | AI 阶段判定：可用于 / 送样或认证 / 量产导入 / 收入 | 证据等级、结论与缺口 |
|---|---|---|---|---|---|
| **沃特股份** `002886.SZ` | `PTFE 薄膜`、`ePTFE 薄膜`；公开资料未给商品牌号。[2025 年报](https://static.cninfo.com.cn/finalpage/2026-04-21/1225131686.PDF) | 年报称其 PTFE 薄膜获高频高速 PCB 线路板头部客户认可，是支持“服务器用 PCB”更快传输/响应的可选方案；[2025-08-25 投资者关系记录](https://static.cninfo.com.cn/finalpage/2025-08-25/1224567542.PDF)称 PTFE 薄膜和氟材料制品覆盖服务器用 PCB、高频高速数据传输。 | 下游仅为未命名的国内/美国高频高速 PCB 线路板客户；无 CCL/bondply SKU、PCB 厂名、材料堆叠、AVL 或终端名称。记录中 AI 服务器的明确材料是 LCP，不是 PTFE。 | **△ / △ / — / —**。PTFE→高频高速 PCB 的“客户认可”可记为 `management_claim` 验证线索；AI 同料号、AI 客户认证、量产、收入均 `N/A`。 | **B**。这是最接近 AI 高速板方向的国内公开线索，但仍差“具体膜料→具体 CCL/粘结片→AI 板厂/终端”的三段链。历史或泛 PCB 的规模化应用不能改写为 AI 量产。 |
| **生益科技** `600183.SH`（含全资子公司江苏生益特种材料） | 官网 PTFE Type 总表列 `SG7350D/D2`、`mmWave77`、`SCGA-500 GF220/GF255/GF265/GF300` 等；为玻纤增强或陶瓷填充 PTFE 射频覆铜板。[PTFE Type 产品总表](https://www.syst.com.cn/cn/product/list_18.aspx?lcid=77) | `mmWave77` 官方用途为汽车雷达、基站天线、卫星通信、天线馈电和射频无源件；`SCGA-500 GF220` 为基站/卫星天线、滤波器、PA、相控阵和航电。[mmWave77](https://www.syst.com.cn/cn/product/info_18.aspx?itemid=5702)；[SCGA-500 GF220](https://www.syst.com.cn/cn/product/info_18.aspx?itemid=539)。另公司 2026H1 披露覆铜板/粘结片广泛用于高算力、AI 服务器并有多品种批量供应，但没有把该事实映射到上述任一 PTFE SKU。[2026H1](https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-08-15/600183_20260815_LHIK.pdf) | PTFE SKU 的官方用途是 RF/微波场景；AI 相关披露只在公司级材料产品层面，未给同一 PTFE 牌号、下游板厂或 AI 客户。 | **△（仅 RF/微波技术用途） / — / — / —**。集团高速材料的 AI 批供事实不可计入 PTFE；PTFE→AI 的认证、导入、收入均 `N/A`。 | **A + evidence_absent**。生益证明“同一公司同时具有 PTFE 高频 CCL 与 AI 高速材料业务”不能证明二者交集。缺 PTFE 料号映射、AI 板厂 AVL、订单和专项收入。 |
| **南亚新材** `688519.SH` | 官网列 `NYHP-220D/255D/265D/300D` PTFE 高频材料，以及 `NYHP-7300MW-P`；为 PCB 用 PTFE 高频材料。[NYHP-220D/255D/265D/300D](https://www.nouyatec.com/product/microwave-rf-material/73)；[NYHP-7300MW-P](https://www.nouyatec.com/product/microwave-rf-material/61) | NYHP 官方应用是低损耗基站天线、军事雷达、数字广播天线、PA、毫米波/汽车雷达。2025 年报另一条 `NOUYA` 高速板路线则覆盖 AI 服务器 UBB、AI 加速卡、交换机、数据中心和背板；年报披露 M6–M8 批量进入国内头部算力客户、M9 NPI、M10 高速背板认证。该年报同时将 PTFE CCL 定义在无线通信、天线、滤波器、雷达、5G 领域，未把 NYHP 与 `NOUYA` 高速路线对应。[2025 年报](https://static.cninfo.com.cn/finalpage/2026-03-26/1225031388.PDF) | AI 的量产/认证证据存在于未披露树脂体系的 `NOUYA` 高速板；PTFE NYHP 没有命名的 AI PCB/CCL 客户、AVL 或采购信息。 | **△（RF/PTFE 牌号） / — / — / —**。M6–M8 的算力客户批用不可标到 NYHP；NYHP→AI 的认证、量产和收入均 `N/A`。 | **A + evidence_absent**。这是“PTFE 射频 SKU”与“AI 高速 SKU”平行而不相交的典型。严禁把公司层面的 AI 客户或 M9/M10 概念嫁接到 NYHP。 |
| **华正新材** `603186.SH` | 官网高频材料目录列 `H5220/H5255/H5265/H5300/H5350P/H5300S/HN30/H5350T/HN30X`，说明为玻纤增强/陶瓷填充 PTFE 覆铜板。[高频材料目录](https://www.wazam.com.cn/product/list/41.html)；[H5220](https://www.wazam.com.cn/product/detail-263.html)；[HN30](https://www.wazam.com.cn/product/detail-6092.html) | 2025 年报把高频覆铜板用途表述为 5G、基站天线、PA；同段另披露 ULL/ELL 的服务器终端认可、低 CTE 智算材料通过头部终端认证并有小批订单、ELL 处于国际芯片终端测试，但未把这些 ULL/ELL 化学体系指向上述 PTFE SKU。[2025 年报](https://static.cninfo.com.cn/finalpage/2026-04-16/1225107720.PDF) | PTFE 目录没有 AI 板厂/终端、材料堆叠或客户；服务器/智算的认证和小批订单属于另列 ULL/ELL，不能归属 PTFE。 | **△（高频 PTFE） / — / — / —**。非 PTFE ULL/ELL 另有认证/小批订单，但 PTFE→AI 的认证、导入、收入均 `N/A`。 | **A + evidence_absent**。华正参与《高频高速电路用 PTFE 覆铜板》团体标准起草可作技术参与旁证，却不是商业化或 AI 客户证据。[标准页](https://www.ttbz.org.cn/standardDetail.html?id=x5evym2fmj03t3v5j734udk7w5txrws) |
| **高斯贝尔** `002848.SZ` | 官网高频 CCL 系列列 `GT1650/GT1350/GT1300/GT1265/GT1220/GT1020`；产品页表述高频 CCL 采用高介电 PTFE/碳氢材料与玻纤布。页面没有把每一型号逐一映射为纯 PTFE，故不把上述全部称为 PTFE 牌号。[产品页](https://www.gospell.com/products.aspx?Id=83&TypeId=83&fid=t3%3A83%3A3) | 2026H1 法定披露将两条路线分开：AI 服务器/GPU/光模块/超算互连/高速交换机的**高速 CCL**以改性聚苯醚为核心；PTFE/碳氢**高频 CCL**用于 77GHz 雷达、5G/6G 基站天线、卫星、军工雷达，仅提 AI 边缘 RF 前端。[2026H1](https://disc.static.szse.cn/disc/disk03/finalpage/2026-07-28/7d2fe1f7-8e25-4279-9785-cc50ca58a040.PDF#page=11) | 没有某个 PTFE 型号进入 AI 板厂/终端的证据；披露的 Eaglestream 关键测试也未标明 PTFE SKU。 | **— / — / — / —**。当前 AI 高速 CCL 路线被官方表述为改性聚苯醚，不能把 PTFE 高频系列并入；PTFE→AI 的所有商业化字段 `N/A`。 | **A + evidence_absent**。这是最明确的“同公司两条材料路线分列”反证之一。 |
| **中英科技** `300936.SZ` | 2025 年报定义其高频覆铜板由铜箔、PTFE、玻纤布组成；募投项目为“年产 30 万平方米 PTFE 高频覆铜板”。未披露商品牌号。[2025 年报](https://static.cninfo.com.cn/finalpage/2026-04-22/1225134348.PDF) | 年报列产品用途为 4G/5G 基站天线、射频、功放、路由器、卫星导航、汽车雷达、移动通信。对该 PTFE 募投项目，年报明确下游终端主要集中通信基站、具体为基站天线；该高频覆铜板业务已有营业收入，但随基站投资放缓下滑。 | 高频 CCL 的销售流程需要终端检测/认证、进入采购目录后由指定 PCB 厂下单，但年报没有将任何 PTFE 项目连到数据中心或 AI 终端。 | **△（通信高频） / — / — / —**。通信基站的量产/收入是已披露事实，**非 AI**；PTFE→AI 认证、导入和收入 `N/A`。 | **A + evidence_absent**。实际商业化终端被年报限定为基站天线，不能利用公司其他封装或散热产品的 AI/数据中心文字来升级 PTFE CCL。 |
| **中昊晨光 / 昊华科技** `600378.SH` | 电子领域 PTFE 乳液；公开资料没有面向 AI PCB 的可核验商品级树脂牌号。昊华科技 2022 年报称电子领域用四氟乳液已成果转化，并在 PCB 板应用市场份额进一步稳固；同时开发高洁净度 CCL/FCCL 用氟树脂关键技术。[2022 年报](https://static.cninfo.com.cn/finalpage/2023-04-22/1216515888.PDF) | 中英科技招股说明书披露 2017–2019 年采购中昊晨光 PTFE 乳液作为高频 CCL 原料，2019 年该项采购占比 99.88%，是“PTFE 上游→高频 CCL”的历史商业链，但终端不是 AI。[招股书问询回复](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc/RAS_000172DCE0A8663FE908826FDE5F4C3F.pdf) | 有 CCL 原料的历史采购证据；没有树脂牌号→CCL 型号→AI 板厂/终端的绑定。公司 2025 年报所述高性能 PTFE 树脂与产能也未给该映射。[2025 年报](https://static.cninfo.com.cn/finalpage/2026-04-24/1225170201.PDF) | **△（上游 CCL 原料） / — / — / —**。历史 PCB/CCL 商业化不等于 AI；AI 认证、导入、收入 `N/A`。 | **A + evidence_absent**。可作为上游历史供应能力观察项，不能列为 AI PCB 已兑现供应商。 |
| **肯特股份** `301591.SZ` | 高介电 PTFE 膜（`Dk 2.6–3.2@10GHz`）被披露用作高频/多层高速 CCL 基材；低介电损耗 PTFE 膜（`Df 0.0015@10GHz`）用于 CCL 制造的离型/基材膜。[技术披露](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc1/202206/RAS_202206_0001811F6B20FD3FE5D52899E484A13F.pdf) | 四氟膜用于高频覆铜板已有交易所文件披露；该文件列举过生益科技、蓝姆材料、华通线缆、久耀电子等非 AI 客户/下游线索。[交易所文件](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc1/202303/RAS_202303_F7FB6BE0035841B29B769C6EE32C7C84.pdf) | 非 AI 高频 CCL 的下游线索存在；公司已直接否认 AI 服务器 PCB 覆铜板应用。 | **✗ / ✗ / ✗ / ✗**。截至截止日不可列为 AI PCB PTFE 候选。 | **negative_official**。其通用 CCL、通信线缆、耐腐蚀/密封等 PTFE 业务不构成 AI PCB 证据。 |

## 不能纳入“AI PCB 已兑现”的相邻证据

| 对象 | 可被证实的事实 | 为什么仍不能计入本题 |
|---|---|---|
| **景旺电子** `603228.SH`（下游 PCB 厂） | 官网与 2026H1 证明其 GPU HDI、112G、AI224G 交换机及新一代 AI 高速 PCB 的制造/量产能力；但未披露 CCL、树脂、PTFE 供应商或材料堆叠。[官网](https://www.kinwong.com/markets/computing/)；[2026H1](https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-08-22/603228_20260822_03Q4.pdf) | 下游能加工 AI 板不等于任一上游 PTFE 已进入其 AVL。景旺 2025-04-03 调研还明确 PTFE 量产出货在车载毫米波雷达、通信无线基站、高速传输，更高阶数据中心仍为技术储备/不同方案投入。[IR 记录](https://sns.sseinfo.com/resources/images/upload/202504/202504061412042130458844.pdf) |
| **胜宏科技** `300476.SZ`（下游 PCB 厂） | 2025-03 调研中将 PTFE 置于 112G 向 224G 演进下的前期认证/试样和终端匹配阶段，同时称 AI 服务器板实用 M7/M8 高速材料。[IR 记录](https://static.cninfo.com.cn/finalpage/2025-03-11/1222768395.PDF) | 这只说明下游对 PTFE 的未来测试需求，且没有披露上游供应商、具体 CCL/树脂牌号、通过认证或量产；不能反推任何上游公司已导入。 |
| **泛亚微透** `688386.SH` | 再融资材料讨论面向 6G 的低介电损耗 FCCL/FPC，绝缘体系为聚酰亚胺/含氟聚合物复合，并称相关客户验证。 | FCCL/FPC 与本报告的 AI 服务器刚性多层板/背板边界不同；未披露 PTFE 占比或 SKU、AI 客户、AVL、订单、收入，不作为主表的 AI PCB PTFE 候选。[再融资文件](https://static.cninfo.com.cn/finalpage/2025-08-27/1224575863.PDF) |
| **久耀电子等通信高频 CCL 供应链** | 交易所问询回复显示，部分 PTFE 高频板曾按信科移动指定用于基站天线 PCB；这能证明通信端的历史采购链。[交易所文件](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc1/202307/RAS_202307_3845F537B5A24A189269C0B133EAA60B.pdf) | 终端是通信基站天线，并非 AI 服务器/交换机/背板。它反而说明：有真实采购和终端指定时，公开资料可将用途写得很清楚；缺少相同粒度的 AI 证据时不能补推。 |
| **东岳高分子 / 东岳集团** | 中英科技交易所文件披露，其 2017–2019 年采购的 PTFE 细粉、乳液用作高频 CCL 原料；2019 年东岳细粉采购 480 吨、该项占比 100%。这是历史实物采购，未披露电子级牌号。[交易所文件](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc/RAS_000172DCE0A8663FE908826FDE5F4C3F.pdf) | 可证实的是向高频 CCL 厂的历史原料发货，并非 AI 板材料导入；没有当前连续供货、CCL 型号、112G/224G 测试、AI 板厂 AVL 或收入归因。 |
| **巨化股份** `600160.SH` | 同一交易所文件记载 2017–2018 年中英科技对巨化 PTFE 细粉/乳液的采购；公开未披露牌号与具体 CCL 型号。巨化披露的高性能 PTFE 项目建设并不等于电子级 AI PCB 供货。[交易所文件](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc/RAS_000172DCE0A8663FE908826FDE5F4C3F.pdf)；[2025 年行动报告](https://static.cninfo.com.cn/finalpage/2026-04-23/1225147857.PDF) | 仅是历史非 AI 高频 CCL 原料路径。不能将产能建设、通用树脂或品牌覆盖写成 AI PCB 的认证、量产或收入。 |
| **泰州市旺灵绝缘材料厂** | 官网列 `F4BM/F4BME`（PTFE 树脂/薄膜/玻纤 CCL）、`F4BTMS`（陶瓷/PTFE/超细玻纤 CCL，称适合多层/高多层/背板加工）及可配 PTFE 的 `WL-PP280` 粘结片；这是供应商产品主张，未见独立板厂核验到具体料号。[F4BM/F4BME](https://www.wang-ling.com.cn/product/126.html)；[F4BTMS](https://www.wang-ling.com.cn/product/108.html)；[WL-PP280](https://www.wang-ling.com.cn/product/159.html) | 本川智能交易所文件证明 2017–2020 年曾采购旺灵高频 CCL，但未把采购批次对应到上述具体 PTFE SKU，且没有 AI 终端信息。[交易所文件](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc/RAS_000176888A4C2E3FE2A5D182BAEB463F.pdf) |
| **久耀电子**（非上市） | `FJY250A` 产品资料为 PTFE 玻纤覆铜板，标示 `Dk 2.50`、`Df 0.0016@10GHz`、支持 PTH，标称用途为基站天线、微波、GPS、雷达、WiFi。[规格书](https://www.ptfe-pcb-laminate.com/FJY250A.pdf) | 龙腾电子交易所文件披露，信科移动自 2019-12 起指定部分产品使用久耀 PTFE 高频板；2020/2021/2022 年采购额为 91.87/1,764.89/816.83 万元，相关终端是通信基础设施。该文件没有把 `FJY250A` 指为实际供货型号，也无 AI 客户/板型/收入。[交易所文件](https://reportdocs.static.szse.cn/UpFiles/rasinfodisc1/202307/RAS_202307_3845F537B5A24A189269C0B133EAA60B.pdf) |

## 逐项回答：谁“可以”与谁“已兑现”

| 判断层次 | 截至 2026-08-29 的答案 | 依据与限制 |
|---|---|---|
| 国内是否有企业具备 PTFE 高频 CCL/薄膜/树脂能力？ | **有。**生益、南亚、华正、中英、高斯贝尔、沃特、中昊晨光等均可从公开资料证实不同层级的 PTFE 高频 CCL、薄膜或上游树脂能力。 | 这是材料/产品能力结论，不是 AI 板级客户结论。 |
| 这些 PTFE 是否已被公开证明用于 AI 服务器/交换机/224G 背板？ | **未证明。** | 生益、南亚、华正的“AI 高速材料”与其 PTFE SKU 不能对应；高斯贝尔甚至把 AI 高速 PPO 路线和 PTFE 高频路线分别披露；中英的实际终端在基站。 |
| 是否有 PTFE 送样/认证？ | **沃特有“头部高频高速 PCB 客户认可”的管理层线索；其余候选对 AI 同 SKU 无公开证据。** | “认可”未给客户、PTFE SKU、CCL SKU、认证报告或 AVL，不能写为已完成 AI 认证。 |
| 是否有 PTFE 已量产导入 AI PCB？ | **没有公开闭环。** | 普通高频 PCB、车载雷达、基站、卫星等量产均非 AI 板级量产。 |
| 是否有 PTFE 已形成 AI PCB 收入？ | **没有公开闭环。** | 没有公司披露同一 PTFE 料号的 AI 订单、出货或收入；分部/公司总收入不可替代。肯特则被法定披露直接排除。 |

## 最值得跟踪的 3 个验证触发点

1. **同料号材料认证触发**：沃特或任何 CCL 厂披露“PTFE 膜/树脂具体牌号 → 具体 CCL 或 bondply 牌号”，并取得命名 AI server/switch/224G 平台或命名板厂的 AVL/认证。应至少给出认证对象、日期、料号和适用的层压/可靠性条件；泛“客户认可”不够。
2. **下游批供触发**：景旺、胜宏、沪电、深南或其他 AI 板厂披露同一 AI 板的材料堆叠、合格 CCL 供应商/牌号，或供应商披露与之可核验的采购订单、批量交付、板型和时间。只有这样才能把“板厂有 AI 能力”接到“上游 PTFE 已导入”。
3. **收入归因触发**：供应商定期报告或客户交叉披露同一 PTFE SKU 的 AI 板出货量、订单、收入（最好含客户/板型/时期），或可复核的专项营收/毛利。总“特种材料”“高频 CCL”或“服务器材料”收入不满足归因要求。

## 仍需保留的风险

- **树脂路线不能由性能指标反推。**M7/M8/M9/M10、低损耗、112G/224G、服务器或 AI 等词本身不说明是 PTFE；可为改性 PPE/PPO、烃树脂、改性环氧或其他体系。
- **PTFE 在高频天线/雷达的成熟供货不能外推到高层 AI 背板。**后者需关注层压、PTH、热机械、阻燃、吸湿、翘曲、损耗和供货一致性的联合验证。
- **未披露不等于不存在。**本结论是“截至截止日的公开一手证据不足”，不是断言企业没有非公开送样、验证或供货。

## 一手来源清单

除表内逐项链接外，主要检索并交叉使用了：公司年报/半年报和投资者关系记录、公司产品页、深沪交易所/巨潮法定披露、下游 PCB 厂的官方资料，以及 Rogers 官方技术数据表。访问日均为 2026-08-29；其中交易所或公司法定披露优先于媒体转载、概念标签和二手研报。
