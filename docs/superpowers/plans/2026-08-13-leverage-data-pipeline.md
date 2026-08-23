# 严格沪深市值快照与两融发布包 Implementation Plan

> **已废弃运行手册（保留为历史实施记录）**：本计划描述的官方前段与旧脚本不再是日常两融网页数据链。当前唯一日常入口、厂商来源和缺口刷新规则见 `docs/automation/LEVERAGE_INCREMENTAL_REFRESH_CONTRACT.md`；不得按本文重建或调用历史脚本。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 构建可审计的官方逐日沪深 A 股市值快照，并将其与经过 DFCF 审计的两市融资余额和本地 TDX 三条指数合成为可供“基金持仓”离线网页消费的静态发布包。

**Architecture:** 新的官方市值脚本只在独立产物目录内工作：它以 DFCF 沪深共同日期为请求清单，保存交易所原始响应、分类解析表和审计结果。第二个构建脚本只读 DFCF、市值和 TDX 输入，通过哈希与口径门后输出 JSON 和 manifest；它可显式发布经验证的两个 JSON 文件到基金项目的 public/data 目录，但不会读取或改写基金季度数据。

**Tech Stack:** Python 3、requests、pandas、openpyxl、Decimal、pytest；输入为 DFCF CSV/JSON、沪深官方日度响应和本地 TDX .day 文件。

## Global Constraints

- DFCF 日更链保持 DFCF-only：不得改动 .agents 技能脚本、自动化配置，或由新脚本写入四个 DFCF 日更产物。
- 只允许新官方市值脚本访问上交所、深交所；DFCF audit 中的 dfcf_only=true 与 exchange_requests=0 只描述 DFCF 融资余额输入链，不能被新链路改写。
- 读取的 DFCF audit 必须同时满足 dfcf_only=true、exchange_requests=0、sample_status=dfcf_vendor_only_unverified_by_exchange，且三份 DFCF 文件 SHA-256 与 audit 一致。
- 市值分母是沪市主板 A、可核验的科创板 A、深市主板 A、创业板 A 和历史中小板 A；排除 B 股、北交所、基金、ETF、REIT、债券及无法单独剔除的 CDR。
- 所有金额计算使用 Decimal；只做精确同日连接，不补值、不前填、不后填、不移位、不以全 A（含北交所）序列替代。
- 比率名称固定为“沪深融资余额／沪深 A 股市值”；必须在 manifest 中标注分子可能包含非 A 股融资标的，故它是描述性比率。
- 新产物只能写入 artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily、artifacts/leverage_capitulation/dashboard_bundle，以及显式传入的基金项目 public/data 目标中的两个 JSON 文件。
- 不得覆盖 verified_2016_present、official_sse_margin.csv、official_szse_margin.csv、margin_audit.json、factor_panel.csv、历史信号、回测工作簿、market_cap/a_share_total_market_cap_vendor_history.csv、market_cap/a_share_total_market_cap_audit.json 或 exploratory_margin_market_cap。
- 测试期间沿用 pytest 临时目录合约；所有测试必须使用本地 fixture 或 mocked HTTP，不访问真实市场接口。
- 项目规则要求：每个实质改动完成并报告验证结果后，等待用户确认再提交或推送；本计划中的“检查点”不执行 git commit。

---

## File Structure

- Create: D:\vcp_hunter\产业链投研\scripts\update_sh_sz_a_share_market_cap_daily.py
  - 独立请求官方日度市值、保留原始响应、解析分类市值、校验范围并生成审计。
- Create: D:\vcp_hunter\产业链投研\scripts\build_leverage_dashboard_bundle.py
  - 只读校验 DFCF、市值和 TDX，生成并可原子发布网页 JSON 与 manifest。
- Create: D:\vcp_hunter\产业链投研\tests\test_update_sh_sz_a_share_market_cap_daily.py
  - 覆盖官方响应分类映射、CDR/B 股范围门、日期/哈希/审计和恢复逻辑。
- Create: D:\vcp_hunter\产业链投研\tests\test_build_leverage_dashboard_bundle.py
  - 覆盖 DFCF 与市值审计门、精确连接、Decimal 比率、TDX 解析、manifest 和发布原子性。
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\raw\sse\YYYY-MM-DD.json
  - 上交所每个共同日期的原始响应。
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\raw\szse\YYYY-MM-DD.xlsx
  - 深交所每个共同日期的原始 XLSX 响应。
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\raw_response_manifest.json
  - 每个日期、来源 URL、原始文件相对路径和 SHA-256 的清单。
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\sh_sz_a_share_market_cap.csv
  - 严格市值解析表。
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\sh_sz_a_share_market_cap_audit.json
  - 市值完整性、范围、哈希、日期与 reporting_eligible 审计。
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dashboard_bundle\leverage-dashboard.json
  - 网页消费的数据包。
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dashboard_bundle\leverage-dashboard.manifest.json
  - 数据包哈希、来源和可用性说明。
- Create: D:\vcp_hunter\产业链投研\docs\leverage_dashboard_data_runbook.md
  - 手动更新、构建、发布、失败回退与禁止改动清单。

## Shared Interfaces

市值脚本的解析记录：

    MarketCapRecord = {
      "date": "YYYY-MM-DD",
      "sh_main_a_market_cap_yi": Decimal | None,
      "sh_star_a_market_cap_yi": Decimal | None,
      "sz_main_a_market_cap_yi": Decimal | None,
      "sz_chinext_a_market_cap_yi": Decimal | None,
      "sz_sme_a_market_cap_yi": Decimal | None,
      "sh_a_market_cap_yi": Decimal | None,
      "sz_a_market_cap_yi": Decimal | None,
      "sh_sz_a_market_cap_yi": Decimal | None,
      "scope_status": "pass" | "cdr_unresolved" | "category_missing" | "identity_failed",
      "sse_source_url": str,
      "szse_source_url": str,
      "sse_raw_sha256": str,
      "szse_raw_sha256": str
    }

发布包记录：

    LeverageDashboardRecord = {
      "date": "YYYY-MM-DD",
      "sh_margin_yi": number,
      "sz_margin_yi": number,
      "total_margin_yi": number,
      "sh_a_market_cap_yi": number | null,
      "sz_a_market_cap_yi": number | null,
      "ratio_pct": number | null,
      "index_000001_close": number | null,
      "index_399106_close": number | null,
      "index_399006_close": number | null
    }

bundle 构建器内部输入对象：

    MarginInput = {
      "frame": pd.DataFrame,
      "audit": dict[str, object]
    }

    MarketCapInput = {
      "frame": pd.DataFrame | None,
      "audit": dict[str, object] | None,
      "flags": {
        "ratio_available": bool,
        "reason": str | None
      }
    }

manifest 的稳定字段：

    {
      "schema_version": "1",
      "payload_sha256": "64 位小写十六进制",
      "payload_records": number,
      "data_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
      "dfcf": {
        "dfcf_only": true,
        "exchange_requests": 0,
        "sample_status": "dfcf_vendor_only_unverified_by_exchange",
        "inputs": {"dfcf_sse_margin_csv": "...", "dfcf_szse_margin_csv": "...", "dfcf_margin_balances_csv": "..."}
      },
      "market_cap": {
        "reporting_eligible": boolean,
        "ratio_available": boolean,
        "reason": string | null,
        "csv_sha256": string | null,
        "scope_definition": string
      },
      "indices": {
        "000001": {"source": "TDX 本地当前数据", "first_date": "YYYY-MM-DD", "last_date": "YYYY-MM-DD", "sha256": "..."},
        "399106": {"source": "TDX 本地当前数据", "first_date": "YYYY-MM-DD", "last_date": "YYYY-MM-DD", "sha256": "..."},
        "399006": {"source": "TDX 本地当前数据", "first_date": "YYYY-MM-DD", "last_date": "YYYY-MM-DD", "sha256": "..."}
      }
    }

### Task 1: 严格市值分类与范围校验的纯函数

**Files:**

- Create: D:\vcp_hunter\产业链投研\scripts\update_sh_sz_a_share_market_cap_daily.py
- Create: D:\vcp_hunter\产业链投研\tests\test_update_sh_sz_a_share_market_cap_daily.py
- Read only: D:\vcp_hunter\产业链投研\.agents\skills\a-share-leverage-capitulation-analyst\scripts\update_dfcf_margin_daily.py
- Read only: D:\vcp_hunter\产业链投研\scripts\build_margin_market_cap_chinext_chart.py

**Interfaces:**

- Produces: parse_sse_rows(rows: list[dict[str, object]], trade_date: date, schema_version: str) -> dict[str, Decimal | None]
- Produces: parse_szse_workbook_bytes(payload: bytes, trade_date: date) -> dict[str, Decimal | None]
- Produces: build_market_cap_record(sse: dict[str, Decimal | None], szse: dict[str, Decimal | None], metadata: dict[str, str]) -> MarketCapRecord
- Produces: validate_market_cap_frame(frame: pd.DataFrame) -> dict[str, object]
- Consumed later by: update_market_cap_snapshot and build_leverage_dashboard_bundle.

- [ ] **Step 0: 建立可复用的测试辅助函数**

在测试文件顶部采用现有 importlib.util 模式加载脚本，并定义以下辅助函数，供本任务和 Task 2 使用：

    def metadata(day: str) -> dict[str, str]:
        return {
            "date": day,
            "sse_source_url": "https://query.sse.com.cn/commonQuery.do",
            "szse_source_url": "https://www.szse.cn/api/report/ShowReport",
            "sse_raw_sha256": "a" * 64,
            "szse_raw_sha256": "b" * 64,
        }

    def passing_record(day: str) -> dict[str, object]:
        return {
            **metadata(day),
            "sh_main_a_market_cap_yi": Decimal("100"),
            "sh_star_a_market_cap_yi": Decimal("20"),
            "sz_main_a_market_cap_yi": Decimal("80"),
            "sz_chinext_a_market_cap_yi": Decimal("30"),
            "sz_sme_a_market_cap_yi": Decimal("10"),
            "sh_a_market_cap_yi": Decimal("120"),
            "sz_a_market_cap_yi": Decimal("120"),
            "sh_sz_a_market_cap_yi": Decimal("240"),
            "scope_status": "pass",
        }

测试文件还必须 import Decimal、date、json、pandas as pd、pytest、Path，并按现有项目模式建立 MODULE。

- [ ] **Step 1: 写出分类和范围失败测试**

在 test_update_sh_sz_a_share_market_cap_daily.py 中添加以下测试数据和断言。测试中的金额均以亿元传入，避免隐式单位换算。

    def test_build_market_cap_record_adds_only_verified_a_categories() -> None:
        sse = {"main_a": Decimal("100"), "star_a": Decimal("20"), "main_b": Decimal("7"), "cdr_status": "pass"}
        szse = {"main_a": Decimal("80"), "chinext_a": Decimal("30"), "sme_a": Decimal("10"), "main_b": Decimal("5"), "cdr_status": "pass"}
        record = MODULE.build_market_cap_record(sse, szse, metadata("2021-12-27"))
        assert record["sh_a_market_cap_yi"] == Decimal("120")
        assert record["sz_a_market_cap_yi"] == Decimal("120")
        assert record["sh_sz_a_market_cap_yi"] == Decimal("240")
        assert record["scope_status"] == "pass"

    def test_build_market_cap_record_rejects_unresolved_star_cdr() -> None:
        sse = {"main_a": Decimal("100"), "star_a": Decimal("20"), "main_b": Decimal("7"), "cdr_status": "unresolved"}
        szse = {"main_a": Decimal("80"), "chinext_a": Decimal("30"), "sme_a": Decimal("10"), "main_b": Decimal("5"), "cdr_status": "pass"}
        record = MODULE.build_market_cap_record(sse, szse, metadata("2021-12-27"))
        assert record["scope_status"] == "cdr_unresolved"
        assert record["sh_sz_a_market_cap_yi"] is None

    def test_validate_market_cap_frame_rejects_duplicate_or_ineligible_date() -> None:
        frame = pd.DataFrame([passing_record("2026-08-11"), passing_record("2026-08-11")])
        with pytest.raises(ValueError, match="duplicate"):
            MODULE.validate_market_cap_frame(frame)

- [ ] **Step 2: 运行测试，确认尚未定义模块或接口**

运行：

    python -m pytest tests/test_update_sh_sz_a_share_market_cap_daily.py -q

预期：FAIL，原因是 update_sh_sz_a_share_market_cap_daily.py 或上述函数尚不存在。

- [ ] **Step 3: 实现分类映射、Decimal 转换和范围门**

在 update_sh_sz_a_share_market_cap_daily.py 中实现以下最小元素：

1. Decimal 解析函数 decimal_amount(value: object, unit: str)；拒绝 NaN、负数、空字符串和未知单位。
2. 常量 SSE_LEGACY_QUERY 与 SSE_CURRENT_QUERY：

       legacy sqlId = COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C
       legacy stockType = 90
       current sqlId = COMMON_SSE_SJ_GPSJ_CJGK_MRGK_C
       current PRODUCT_CODE = 01, 02, 03, 11, 17

   旧接口使用主板 A、主板 B、科创板分类；新接口使用 PRODUCT_CODE 01 主板 A、02 主板 B、03 科创板、11 回购、17 股票总计。不得把回购或股票总计直接纳入分母。
3. SZSE_SHOW_REPORT_URL：

       https://www.szse.cn/api/report/ShowReport

   请求参数固定为 SHOWTYPE=xlsx、CATALOGID=1803_sczm、TABKEY=tab1、txtQueryDate=YYYY-MM-DD。解析中文分类名时归一化空白和全角字符；只接收主板 A 股、创业板 A 股与历史中小板 A 股。
4. build_market_cap_record；主板 B、回购、股票总计、基金、债券和北交所只用于恒等式检查或审计，不参与分母。
5. 对不存在科创板的历史 schema，只有 schema_version 明确标记为 pre_star_board 时才以 Decimal("0") 处理；2019-07-22 之后缺少科创板分类一律 scope_status=category_missing。
6. 当接口未把 CDR 单独分出时设置 cdr_status=unresolved，不把该日比率标为合格。
7. validate_market_cap_frame；要求 date 唯一升序、scope_status=pass、三项合计为正，且 sh_a + sz_a = sh_sz_a。

- [ ] **Step 4: 运行纯函数测试**

运行：

    python -m pytest tests/test_update_sh_sz_a_share_market_cap_daily.py -q

预期：PASS，且每个失败分类产生明确的 ValueError 或 scope_status。

- [ ] **Step 5: 进行数据链隔离回归**

运行：

    python -m pytest tests/test_update_dfcf_margin_daily.py::test_daily_updater_contains_no_exchange_endpoint tests/test_pytest_storage_contract.py -q

预期：PASS，证明新官方市值端点没有被加入 DFCF 日更脚本。

- [ ] **Step 6: 报告检查点**

报告新增脚本与测试、通过的测试命令、严格范围门和任何 CDR 解析限制；不要执行 git add、git commit 或 git push，等待用户确认。

### Task 2: 官方原始响应、恢复运行与市值审计输出

**Files:**

- Modify: D:\vcp_hunter\产业链投研\scripts\update_sh_sz_a_share_market_cap_daily.py
- Modify: D:\vcp_hunter\产业链投研\tests\test_update_sh_sz_a_share_market_cap_daily.py
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\raw_response_manifest.json
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\sh_sz_a_share_market_cap.csv
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\sh_sz_a_share_market_cap_audit.json

**Interfaces:**

- Consumes: DFCF 日期列 date，以及 sha256_file、atomic_write_csv、atomic_write_json 的既有实现模式。
- Produces: update_market_cap_snapshot(project_root: Path, dates: list[date], options: UpdateOptions) -> dict[str, object]
- Produces: build_market_cap_audit(frame: pd.DataFrame, raw_manifest: list[dict[str, str]], requested_dates: list[date]) -> dict[str, object]
- Consumed later by: build_leverage_dashboard_bundle.py。

- [ ] **Step 0: 建立 mocked HTTP 与审计 fixture**

在同一测试文件中定义以下最小 fixture，不使用真实网络：

    class FakeResponse:
        def __init__(self, content: bytes, status_code: int = 200) -> None:
            self.content = content
            self.status_code = status_code

    class FakeSession:
        def __init__(self) -> None:
            self.calls: list[tuple[str, dict[str, object]]] = []

        def get(self, url: str, *, params: dict[str, object], headers: dict[str, str], timeout: int) -> FakeResponse:
            self.calls.append((url, params))
            if "szse.cn" in url:
                return FakeResponse(make_szse_xlsx_bytes())
            return FakeResponse(make_sse_json_bytes(params))

    def options_with_fake_session(resume: bool = False) -> MODULE.UpdateOptions:
        return MODULE.UpdateOptions(
            session=FakeSession(),
            resume=resume,
            sleep_seconds=0,
            timeout_seconds=1,
            max_retries=0,
        )

    def passing_frame_for_one_date() -> pd.DataFrame:
        return pd.DataFrame([passing_record("2021-12-24")])

    def raw_manifest_for_one_date() -> list[dict[str, str]]:
        return [
            {"date": "2021-12-24", "market": "SSE", "sha256": "a" * 64},
            {"date": "2021-12-24", "market": "SZSE", "sha256": "b" * 64},
        ]

make_sse_json_bytes 返回包含主板 A、主板 B、科创板、回购和股票总计分类的 UTF-8 JSON；make_szse_xlsx_bytes 使用 pandas.ExcelWriter 和 openpyxl 在内存 BytesIO 中创建主板 A、创业板 A、中小板 A 与 B 股分类行。

- [ ] **Step 1: 写出 mocked HTTP 与断点恢复的失败测试**

在 test_update_sh_sz_a_share_market_cap_daily.py 中加入 FakeSession，记录 URL、params 和调用次数；覆盖以下行为：

    def test_update_snapshot_requests_only_dfcf_common_dates_and_writes_raw_hashes(tmp_path: Path) -> None:
        dates = [date(2021, 12, 24), date(2021, 12, 27)]
        result = MODULE.update_market_cap_snapshot(tmp_path, dates, options_with_fake_session())
        raw_manifest = json.loads((tmp_path / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily/raw_response_manifest.json").read_text("utf-8"))
        assert [(item["date"], item["market"]) for item in raw_manifest] == [
            ("2021-12-24", "SSE"),
            ("2021-12-24", "SZSE"),
            ("2021-12-27", "SSE"),
            ("2021-12-27", "SZSE"),
        ]
        assert all(len(item["sha256"]) == 64 for item in raw_manifest)
        assert result["requested_dates"] == 2

    def test_resume_skips_only_hash_valid_completed_date(tmp_path: Path) -> None:
        first = MODULE.update_market_cap_snapshot(tmp_path, [date(2021, 12, 27)], options_with_fake_session())
        second = MODULE.update_market_cap_snapshot(tmp_path, [date(2021, 12, 27)], options_with_fake_session(resume=True))
        assert first["network_requests"] == 2
        assert second["network_requests"] == 0

    def test_audit_marks_partial_snapshot_not_reporting_eligible(tmp_path: Path) -> None:
        audit = MODULE.build_market_cap_audit(passing_frame_for_one_date(), raw_manifest_for_one_date(), [date(2021, 12, 24), date(2021, 12, 27)])
        assert audit["reporting_eligible"] is False
        assert audit["missing_dates"] == ["2021-12-27"]

- [ ] **Step 2: 运行新测试，确认采集接口尚未实现**

运行：

    python -m pytest tests/test_update_sh_sz_a_share_market_cap_daily.py -q

预期：FAIL，原因是 update_market_cap_snapshot、raw manifest 或审计函数尚未实现。

- [ ] **Step 3: 实现限速请求、原始文件和恢复检查**

在脚本内实现：

1. dataclass UpdateOptions，字段为 session: requests.Session、resume: bool、sleep_seconds: float、timeout_seconds: int、max_retries: int；测试可注入 FakeSession。
2. load_dfcf_common_dates，从 dfcf_margin_balances.csv 的唯一 date 列读取请求清单；只选取 --start-date 与 --end-date 范围内的日期。
3. request_with_retry，使用 requests.Session、明确 User-Agent 和 Referer、timeout、max_retries、指数退避；所有 HTTP 非 200、空响应、JSON/XLSX 解析失败记录为该日期失败，不伪造数据。
4. fetch_sse_payload，2021-12-24 及以前使用 legacy SQL，2021-12-27 及以后使用 current SQL；DFCF 请求日期不应落在二者之间的非交易日。响应以 UTF-8 JSON 原始字节保存。
5. fetch_szse_workbook，按固定 ShowReport 参数请求；响应以原始 XLSX 字节保存。
6. atomic_write_bytes，将每个原始文件先写到同目录临时文件并 os.replace。
7. raw_response_manifest.json，逐条存 date、market、source_url、request_parameters、relative_path、sha256、bytes、retrieved_at_utc 和 schema_version。
8. --resume 仅在 raw manifest 存在、原始文件存在、文件 SHA-256 匹配、解析记录 scope_status=pass 的日期跳过；其他任何状态重取。
9. CLI 参数：

       --project-root
       --start-date
       --end-date
       --resume
       --sleep-seconds
       --timeout-seconds
       --max-retries
       --dry-run

   --dry-run 只输出由 DFCF 共同日期导出的请求日期和路径，不发网络请求、不写文件。

- [ ] **Step 4: 实现 CSV 与 audit 的原子生成**

输出 CSV 使用 UTF-8、日期升序，并包含 Shared Interfaces 中的全部市值字段以及 retrieved_at_utc。输出 audit 至少包含：

    scope_definition
    requested_dates
    completed_dates
    missing_dates
    duplicate_date_count
    scope_status_counts
    identity_failure_dates
    raw_response_manifest_sha256
    sh_sz_a_share_market_cap_csv_sha256
    reporting_eligible
    source_schema_versions
    updated_at_utc

只有 requested_dates 全部完成、所有 scope_status=pass、日期唯一、身份式通过、raw manifest 与 CSV 哈希一致时，reporting_eligible=true。

- [ ] **Step 5: 运行采集与审计测试**

运行：

    python -m pytest tests/test_update_sh_sz_a_share_market_cap_daily.py tests/test_pytest_storage_contract.py -q

预期：PASS，测试不产生真实网络请求，所有临时响应位于 pytest 受控目录。

- [ ] **Step 6: 运行真实全量前的只读预检**

运行：

    $latest = (Get-Content -LiteralPath "D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dfcf_daily\dfcf_margin_audit.json" -Raw -Encoding utf8 | ConvertFrom-Json).latest_common_date
    python scripts\update_sh_sz_a_share_market_cap_daily.py --project-root "D:\vcp_hunter\产业链投研" --start-date 2011-08-03 --end-date $latest --dry-run

预期：输出的日期数等于 DFCF 合并表在该区间的日期数；不创建或修改 artifacts 文件。

- [ ] **Step 7: 报告检查点**

报告输出字段、恢复规则、预检日期数和严格范围仍可能因 CDR 无法拆分而拒绝部分日期；不要执行提交或推送，等待用户确认再启动长时间官方历史抓取。

### Task 3: 全量市值快照运行与审计准入

**Files:**

- Modify at runtime only: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\raw\**
- Modify at runtime only: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\raw_response_manifest.json
- Modify at runtime only: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\sh_sz_a_share_market_cap.csv
- Modify at runtime only: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily\sh_sz_a_share_market_cap_audit.json

**Interfaces:**

- Consumes: Task 2 的 CLI、DFCF common-date 输入和官方分类映射。
- Produces: reporting_eligible=true 的完整严格市值快照，或 reporting_eligible=false 与逐日缺口清单。
- Consumed later by: Task 4 的 bundle builder。

- [ ] **Step 1: 记录当前 DFCF 输入基线**

运行：

    $audit = Get-Content -LiteralPath "D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dfcf_daily\dfcf_margin_audit.json" -Raw -Encoding utf8 | ConvertFrom-Json
    $audit | Select-Object latest_common_date,dfcf_only,exchange_requests,dfcf_sse_margin_sha256,dfcf_szse_margin_sha256,dfcf_margin_balances_sha256 | Format-List

预期：dfcf_only 为 True、exchange_requests 为 0；将输出附入运行记录，作为本次市值快照的分子输入基线。

- [ ] **Step 2: 启动可恢复的官方全量抓取**

运行：

    $latest = (Get-Content -LiteralPath "D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dfcf_daily\dfcf_margin_audit.json" -Raw -Encoding utf8 | ConvertFrom-Json).latest_common_date
    python scripts\update_sh_sz_a_share_market_cap_daily.py --project-root "D:\vcp_hunter\产业链投研" --start-date 2011-08-03 --end-date $latest --resume --sleep-seconds 0.2 --timeout-seconds 30 --max-retries 4

预期：每个 DFCF 共同日期产生两份原始响应或明确失败记录。遇到网络中断后，使用同一命令恢复；不得删除 raw 目录或改写 DFCF 输入。

- [ ] **Step 3: 复核市值 audit 与文件哈希**

运行：

    $capDir = "D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\sh_sz_a_share_market_cap_daily"
    $capAudit = Get-Content -LiteralPath "$capDir\sh_sz_a_share_market_cap_audit.json" -Raw -Encoding utf8 | ConvertFrom-Json
    $actual = (Get-FileHash -LiteralPath "$capDir\sh_sz_a_share_market_cap.csv" -Algorithm SHA256).Hash.ToLower()
    [pscustomobject]@{
      reporting_eligible = $capAudit.reporting_eligible
      requested_dates = $capAudit.requested_dates
      completed_dates = $capAudit.completed_dates
      missing_dates = ($capAudit.missing_dates -join ",")
      scope_status_counts = ($capAudit.scope_status_counts | ConvertTo-Json -Compress)
      audit_sha256 = $capAudit.sh_sz_a_share_market_cap_csv_sha256
      actual_sha256 = $actual
    } | Format-List

预期：仅当 reporting_eligible=True、missing_dates 为空、audit_sha256 等于 actual_sha256 时，才能开放比例构建；否则比例保持 N/A。

- [ ] **Step 4: 执行回归测试**

运行：

    python -m pytest tests/test_update_dfcf_margin_daily.py tests/test_update_a_share_total_market_cap.py tests/test_build_margin_market_cap_chinext_chart.py tests/test_update_sh_sz_a_share_market_cap_daily.py tests/test_pytest_storage_contract.py -q

预期：PASS，既有全 A 厂商市值和探索图测试保持原状；它们不成为严格口径的输入。

- [ ] **Step 5: 报告检查点**

报告实际可用日期范围、缺失/范围失败日期数、raw manifest 哈希、CSV 哈希、reporting_eligible 和比例是否可开放；不要把融资余额变化解释为强平、市场底或必然反弹，也不要提交或推送。

### Task 4: 两融网页发布包构建器

**Files:**

- Create: D:\vcp_hunter\产业链投研\scripts\build_leverage_dashboard_bundle.py
- Create: D:\vcp_hunter\产业链投研\tests\test_build_leverage_dashboard_bundle.py
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dashboard_bundle\leverage-dashboard.json
- Create at runtime: D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dashboard_bundle\leverage-dashboard.manifest.json

**Interfaces:**

- Consumes: DFCF CSV/audit、Task 3 的 CSV/audit、本地 D:\HT\vipdoc\sh\lday\sh000001.day、本地 D:\HT\vipdoc\sz\lday\sz399106.day、本地 D:\HT\vipdoc\sz\lday\sz399006.day。
- Produces: verify_dfcf_inputs(...) -> MarginInput、verify_market_cap_inputs(...) -> MarketCapInput、parse_day_bytes(...) -> pd.DataFrame、build_dashboard_records(margin: pd.DataFrame, cap: pd.DataFrame | None, indices: dict[str, pd.DataFrame], market_cap_flags: dict[str, object]) -> tuple[list[LeverageDashboardRecord], dict[str, object]]、build_manifest(...) -> dict[str, object]、publish_bundle_atomically(...) -> None。
- Consumed later by: 基金持仓前端和其 verify:leverage 命令。

- [ ] **Step 0: 建立 bundle fixture 写入函数**

在 test_build_leverage_dashboard_bundle.py 中按 tmp_path 建立以下辅助函数：

    def write_csv(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")

    def valid_cap_csv() -> str:
        return (
            "date,sh_a_market_cap_yi,sz_a_market_cap_yi,sh_sz_a_market_cap_yi,scope_status\\n"
            "2026-08-11,6000,6000,12000,pass\\n"
            "2026-08-12,6050,6050,12100,pass\\n"
        )

    def write_valid_dfcf_fixture(root: Path, exchange_requests: int = 0) -> None:
        daily = root / "artifacts/leverage_capitulation/dfcf_daily"
        daily.mkdir(parents=True)
        write_csv(daily / "dfcf_sse_margin.csv", "date,sh_margin_y\\n2026-08-11,100\\n2026-08-12,101\\n")
        write_csv(daily / "dfcf_szse_margin.csv", "date,sz_margin_y\\n2026-08-11,80\\n2026-08-12,81\\n")
        write_csv(
            daily / "dfcf_margin_balances.csv",
            "date,sh_margin_y,sz_margin_y,total_margin_y,sample_status\\n"
            "2026-08-11,100,80,180,dfcf_vendor_only_unverified_by_exchange\\n"
            "2026-08-12,101,81,182,dfcf_vendor_only_unverified_by_exchange\\n",
        )
        write_matching_dfcf_audit(daily, exchange_requests)

    def write_cap_fixture(root: Path, reporting_eligible: bool) -> None:
        cap_dir = root / "artifacts/leverage_capitulation/sh_sz_a_share_market_cap_daily"
        cap_dir.mkdir(parents=True)
        write_csv(cap_dir / "sh_sz_a_share_market_cap.csv", valid_cap_csv())
        write_matching_cap_audit(cap_dir, reporting_eligible)

    def write_matching_dfcf_audit(daily: Path, exchange_requests: int) -> None:
        audit = {
            "dfcf_only": True,
            "exchange_requests": exchange_requests,
            "sample_status": "dfcf_vendor_only_unverified_by_exchange",
            "dfcf_sse_margin_sha256": MODULE.sha256_file(daily / "dfcf_sse_margin.csv"),
            "dfcf_szse_margin_sha256": MODULE.sha256_file(daily / "dfcf_szse_margin.csv"),
            "dfcf_margin_balances_sha256": MODULE.sha256_file(daily / "dfcf_margin_balances.csv"),
        }
        (daily / "dfcf_margin_audit.json").write_text(json.dumps(audit), encoding="utf-8")

    def write_matching_cap_audit(cap_dir: Path, reporting_eligible: bool) -> None:
        audit = {
            "reporting_eligible": reporting_eligible,
            "sh_sz_a_share_market_cap_csv_sha256": MODULE.sha256_file(cap_dir / "sh_sz_a_share_market_cap.csv"),
            "scope_definition": "沪市主板A、科创板A、深市主板A、创业板A、历史中小板A；排除B股、北交所、基金、ETF、REIT、债券和无法剔除的CDR。",
        }
        (cap_dir / "sh_sz_a_share_market_cap_audit.json").write_text(json.dumps(audit, ensure_ascii=False), encoding="utf-8")

    def index_frames_missing_second_date() -> dict[str, pd.DataFrame]:
        return {
            "000001": pd.DataFrame({"date": ["2026-08-11"], "close": [3000]}),
            "399106": pd.DataFrame({"date": ["2026-08-11"], "close": [10000]}),
            "399006": pd.DataFrame({"date": ["2026-08-11"], "close": [2000]}),
        }

    def margin_frame() -> pd.DataFrame:
        return pd.DataFrame({
            "date": ["2026-08-11", "2026-08-12"],
            "sh_margin_y": [100, 101],
            "sz_margin_y": [80, 81],
            "total_margin_y": [180, 182],
            "sample_status": ["dfcf_vendor_only_unverified_by_exchange"] * 2,
        })

    def cap_frame_missing_second_date() -> pd.DataFrame:
        return pd.DataFrame({
            "date": ["2026-08-11"],
            "sh_a_market_cap_yi": [6000],
            "sz_a_market_cap_yi": [6000],
            "sh_sz_a_market_cap_yi": [12000],
            "scope_status": ["pass"],
        })

    def sample_records() -> list[dict[str, object]]:
        return [{
            "date": "2026-08-11",
            "sh_margin_yi": 100.0,
            "sz_margin_yi": 80.0,
            "total_margin_yi": 180.0,
            "sh_a_market_cap_yi": 6000.0,
            "sz_a_market_cap_yi": 6000.0,
            "ratio_pct": 1.5,
            "index_000001_close": 3000.0,
            "index_399106_close": 10000.0,
            "index_399006_close": 2000.0,
        }]

    def sample_manifest_inputs() -> dict[str, object]:
        return {"ratio_available": True, "ratio_reason": None}

    def build_dashboard_records_from_fixtures(root: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
        margin_input = MODULE.verify_dfcf_inputs(root)
        cap_input = MODULE.verify_market_cap_inputs(root)
        return MODULE.build_dashboard_records(margin_input.frame, cap_input.frame, index_frames_missing_second_date(), cap_input.flags)

write_matching_dfcf_audit 与 write_matching_cap_audit 使用 MODULE.sha256_file 计算 fixture 真实哈希；不得手写伪造 audit 哈希。

- [ ] **Step 1: 写出 DFCF、市值和 TDX 门的失败测试**

在 test_build_leverage_dashboard_bundle.py 中添加以下测试：

    def test_bundle_refuses_dfcf_audit_with_exchange_requests(tmp_path: Path) -> None:
        write_valid_dfcf_fixture(tmp_path, exchange_requests=1)
        with pytest.raises(ValueError, match="exchange_requests"):
            MODULE.verify_dfcf_inputs(tmp_path)

    def test_bundle_keeps_margin_but_disables_ratio_when_cap_audit_is_ineligible(tmp_path: Path) -> None:
        write_valid_dfcf_fixture(tmp_path)
        write_cap_fixture(tmp_path, reporting_eligible=False)
        records, flags = build_dashboard_records_from_fixtures(tmp_path)
        assert records[0]["total_margin_yi"] == 180.0
        assert records[0]["ratio_pct"] is None
        assert flags["ratio_available"] is False

    def test_bundle_uses_exact_dates_and_never_fills_missing_index_or_cap() -> None:
        records, flags = MODULE.build_dashboard_records(
            margin_frame(),
            cap_frame_missing_second_date(),
            index_frames_missing_second_date(),
            {"ratio_available": False, "reason": "严格市值日期覆盖不完整。"},
        )
        assert records[1]["ratio_pct"] is None
        assert records[1]["index_399006_close"] is None
        assert flags["ratio_available"] is False

    def test_decimal_ratio_and_manifest_payload_hash_are_reproducible(tmp_path: Path) -> None:
        payload_path, manifest_path = MODULE.write_bundle(tmp_path, sample_records(), sample_manifest_inputs())
        manifest = json.loads(manifest_path.read_text("utf-8"))
        assert Decimal(str(sample_records()[0]["ratio_pct"])) == Decimal("1.50000000")
        assert manifest["payload_sha256"] == MODULE.sha256_file(payload_path)

- [ ] **Step 2: 运行测试，确认 bundle 模块尚未实现**

运行：

    python -m pytest tests/test_build_leverage_dashboard_bundle.py -q

预期：FAIL，原因是 build_leverage_dashboard_bundle.py 或受测接口尚不存在。

- [ ] **Step 3: 实现输入审计门与精确连接**

实现以下规则：

1. verify_dfcf_inputs 读取 dfcf_margin_audit.json，验证字段 dfcf_only、exchange_requests、sample_status，以及 dfcf_sse_margin_sha256、dfcf_szse_margin_sha256、dfcf_margin_balances_sha256 对应的真实文件哈希。
2. 同时验证合并表的 date 唯一升序、sh_margin_y + sz_margin_y = total_margin_y 和所有 sample_status 等于 dfcf_vendor_only_unverified_by_exchange。
3. verify_market_cap_inputs 验证市值 CSV 和 audit 的 SHA-256、reporting_eligible、scope_status、日期唯一性和范围定义。若它不合格，返回 ratio_available=False 和中文 reason，而不是拒绝融资余额输出。
4. parse_day_bytes 使用 <IIIIIfII>，第五个字段为 close；仅接受 sh000001、sz399106、sz399006 三个白名单路径。
5. 以融资余额日期作为输出骨架。市值和每个指数只用 date 的 one-to-one left merge；不要调用 fillna、ffill、bfill、asof 或重采样。
6. 当且仅当市值 audit 合格且所有融资余额日期都有通过范围门的市值时，ratio_available=True；比例用 Decimal(total_margin_y) / Decimal(sh_sz_a_market_cap_yi) * 100 量化至 8 位小数后写为 JSON number。

- [ ] **Step 4: 实现 manifest、原子写和显式发布**

实现：

1. JSON 使用 UTF-8 无 BOM、稳定键顺序、末尾一个换行；先写临时文件，再 os.replace。
2. manifest.payload_sha256 对应 leverage-dashboard.json 的原始字节 SHA-256。
3. manifest 写入 Shared Interfaces 中的 DFCF、市值、指数、首末日、行数、来源和描述性比率披露。
4. CLI 参数：

       --project-root
       --output-dir
       --publish-dir

   未传 --publish-dir 时只生成产业链投研 artifact。传入 --publish-dir 时，仅将已经写入并自检通过的 leverage-dashboard.json 和 leverage-dashboard.manifest.json 原子替换到指定目录；拒绝 publish-dir 不是 D:\vcp_hunter\基金持仓\public\data 的路径。
5. 发布前再次计算 artifact payload 与 manifest SHA-256；任一不符时拒绝复制。

- [ ] **Step 5: 运行 bundle 测试与既有数据回归**

运行：

    python -m pytest tests/test_build_leverage_dashboard_bundle.py tests/test_update_dfcf_margin_daily.py tests/test_build_margin_market_cap_chinext_chart.py tests/test_pytest_storage_contract.py -q

预期：PASS。所有 fixture 位于 pytest 临时目录；既有探索图不会成为 bundle 输入。

- [ ] **Step 6: 在完整市值 audit 合格后生成和发布包**

运行：

    python scripts\build_leverage_dashboard_bundle.py --project-root "D:\vcp_hunter\产业链投研" --output-dir "D:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\dashboard_bundle" --publish-dir "D:\vcp_hunter\基金持仓\public\data"

预期：artifact 与基金项目 public/data 中两个 JSON 的 SHA-256 完全一致。若市值 audit 不合格，命令仍可生成融资余额数据包，但 manifest.market_cap.ratio_available 必须为 false，前端比例选项将禁用。

- [ ] **Step 7: 报告检查点**

报告发布包首末日、payload SHA-256、ratio_available、ratio 的证据缺口和实际发布目标；不要提交或推送。

### Task 5: 数据运行手册与交付前复核

**Files:**

- Create: D:\vcp_hunter\产业链投研\docs\leverage_dashboard_data_runbook.md
- Read only: D:\vcp_hunter\产业链投研\docs\superpowers\plans\2026-08-13-leverage-data-pipeline.md
- Read only: D:\vcp_hunter\基金持仓\docs\superpowers\specs\2026-08-13-leverage-dashboard-design.md

**Interfaces:**

- Consumes: Task 2 至 Task 4 的 CLI 与 artifact 契约。
- Produces: 可复现的手动更新及发布流程，供后续自动化前人工运行。

- [ ] **Step 1: 写出运行手册**

在 leverage_dashboard_data_runbook.md 中写入以下具体章节：

1. 前置输入、两个项目的绝对路径和 DFCF 日更链不变更的声明。
2. 市值 dry-run、可恢复全量抓取、audit 哈希复核、bundle 构建与 publish 命令。
3. reporting_eligible=false、ratio_available=false、DFCF audit 失败、publish 哈希失败各自的停止条件。
4. 仅可写的新 artifact 目录和基金项目 public/data 的两个 JSON 文件。
5. “沪深融资余额／沪深 A 股市值”为描述性比率的固定文案，以及融资余额仅为去杠杆压力代理的限制。

- [ ] **Step 2: 校验文档命令与文件路径**

运行：

    rg -n "update_sh_sz_a_share_market_cap_daily.py|build_leverage_dashboard_bundle.py|reporting_eligible|ratio_available|public\\data" docs\leverage_dashboard_data_runbook.md

预期：每个命令、停止条件和发布目标均可在文档中找到。

- [ ] **Step 3: 执行最终数据侧测试集**

运行：

    python -m pytest tests/test_update_dfcf_margin_daily.py tests/test_update_a_share_total_market_cap.py tests/test_build_margin_market_cap_chinext_chart.py tests/test_update_sh_sz_a_share_market_cap_daily.py tests/test_build_leverage_dashboard_bundle.py tests/test_pytest_storage_contract.py -q

预期：PASS。

- [ ] **Step 4: 报告完成并等待用户验收**

报告新增文件、已发布的 JSON 哈希、测试结果、未满足的范围或数据缺口。不要提交或推送；仅在用户确认测试结果后，按两个项目各自的当前分支与上游执行备份流程。
