from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = (
    ROOT
    / ".agents"
    / "skills"
    / "research-industry-chain"
    / "scripts"
    / "normalize_research_inputs.py"
)
VALIDATOR = (
    ROOT
    / ".agents"
    / "skills"
    / "research-industry-chain"
    / "scripts"
    / "validate_bottleneck_evidence.py"
)
TEMPLATES = (
    ROOT / "artifacts" / "weekly_chain_tracking" / "ai_chain" / "BASELINE_TEMPLATE.md",
    ROOT / "artifacts" / "weekly_chain_tracking" / "ai_pcb" / "BASELINE_TEMPLATE.md",
    ROOT
    / "artifacts"
    / "weekly_chain_tracking"
    / "optical_module"
    / "BASELINE_TEMPLATE.md",
)

TABLE_HEADINGS = {
    "bottleneck_ledger": "## 当前堵点账本",
    "bottleneck_evidence_checks": "### 瓶颈证据检查",
    "future_bottleneck_scenarios": "## 未来 6-24 个月卡点迁移",
    "china_candidates": "## 上市公司映射",
}

EXPECTED_HEADERS = {
    "bottleneck_ledger": (
        "堵点",
        "声明时点",
        "证据检查ID",
        "证据评审状态",
        "影响层级",
        "需求证据",
        "供给证据",
        "供应缺口证据",
        "约束机制",
        "严重程度",
        "时间维度",
        "替代路径",
        "二供状态",
        "缓解窗口",
        "正面验证",
        "反证",
        "前次状态",
        "状态变化",
        "关键反转",
        "证据等级",
        "来源",
    ),
    "bottleneck_evidence_checks": (
        "检查ID",
        "节点",
        "严重程度",
        "声明窗口",
        "声明时点",
        "最大证据年龄天数",
        "需求证据类型",
        "供给证据类型",
        "需求证据",
        "需求证据日期",
        "需求来源类型",
        "需求来源定位",
        "供给证据",
        "供给证据日期",
        "供给来源类型",
        "供给来源定位",
        "供应缺口证据",
        "缺口证据日期",
        "缺口来源类型",
        "缺口来源定位",
        "直接缺口后果",
        "约束机制",
        "时间维度",
        "替代路径",
        "二供状态",
        "缓解窗口",
        "正面验证",
        "反证",
        "关键反转",
        "证据等级",
        "来源",
        "来源日期",
    ),
    "future_bottleneck_scenarios": (
        "节点",
        "当前状态",
        "未来状态",
        "需求触发",
        "供给滞后机制",
        "预计时间",
        "置信度",
        "证据缺口",
        "反转指标",
        "证据日期",
        "未来证据最大年龄天数",
        "来源类型",
        "来源定位",
        "证据等级",
        "来源",
    ),
    "china_candidates": (
        "公司",
        "代码",
        "交易所",
        "对应节点",
        "敞口证据",
        "商业化阶段",
        "阶段证据",
        "阶段日期",
        "阶段声明窗口",
        "阶段最大证据年龄天数",
        "阶段来源",
        "阶段来源类型",
        "阶段来源定位",
        "纯度",
        "收入占比",
        "证据缺口",
        "基本面质量",
        "业绩弹性",
        "交易弹性",
        "结论",
        "纳入理由",
        "淘汰理由",
        "下一验证证据",
        "证据等级",
        "来源",
    ),
}

FIELD_VALUES = {
    "堵点": "qualified component",
    "声明时点": "2026-07-27",
    "证据检查ID": "check-qualified-component-20260727",
    "证据评审状态": "eligible_for_bottleneck_review",
    "影响层级": "upstream qualified supply",
    "需求证据": "dated customer platform ramp disclosure",
    "供给证据": "dated qualified-capacity limit disclosure",
    "供应缺口证据": "dated allocation and delivery-delay notice",
    "约束机制": "qualification and yield",
    "严重程度": "soft_bottleneck",
    "时间维度": "next two quarters",
    "替代路径": "second-source qualification",
    "二供状态": "qualifying",
    "缓解窗口": "two quarters if qualification succeeds",
    "正面验证": "allocation persists after announced ramp",
    "反证": "second-source trial has started but is not qualified",
    "前次状态": "watch",
    "状态变化": "upgraded",
    "关键反转": "qualified second source reaches volume",
    "证据等级": "B",
    "来源": "official disclosure bundle",
    "检查ID": "check-qualified-component-20260727",
    "节点": "qualified component",
    "声明窗口": "current",
    "最大证据年龄天数": "180",
    "需求证据类型": "demand_step",
    "供给证据类型": "qualified_supply_limit",
    "需求证据日期": "2026-07-20",
    "需求来源类型": "official_counterparty",
    "需求来源定位": "https://example.com/customer-ramp",
    "供给证据日期": "2026-07-18",
    "供给来源类型": "company_original",
    "供给来源定位": "https://example.com/qualified-capacity",
    "缺口证据日期": "2026-07-25",
    "缺口来源类型": "official_counterparty",
    "缺口来源定位": "https://example.com/allocation-notice",
    "直接缺口后果": "allocation and delayed customer delivery",
    "来源日期": "2026-07-25",
    "当前状态": "watch",
    "未来状态": "likely_future_bottleneck",
    "需求触发": "next platform ramp",
    "供给滞后机制": "qualification lead time lags the demand step",
    "预计时间": "2027H1",
    "置信度": "medium",
    "证据缺口": "independent qualified-capacity update remains missing",
    "反转指标": "second source qualifies before the platform ramp",
    "证据日期": "2026-07-20",
    "未来证据最大年龄天数": "365",
    "来源类型": "official",
    "来源定位": "https://example.com/official-roadmap",
    "公司": "示例公司",
    "代码": "000001.SZ",
    "交易所": "SZSE",
    "对应节点": "qualified component",
    "敞口证据": "official product and qualification disclosure",
    "商业化阶段": "qualification",
    "阶段证据": "customer qualification disclosure",
    "阶段日期": "2026-07-20",
    "阶段声明窗口": "current",
    "阶段最大证据年龄天数": "365",
    "阶段来源": "company announcement",
    "阶段来源类型": "company_original",
    "阶段来源定位": "https://example.com/company-announcement",
    "纯度": "low",
    "收入占比": "not separately disclosed; verify the next formal report",
    "基本面质量": "medium",
    "业绩弹性": "low",
    "交易弹性": "medium",
    "结论": "watch_only",
    "纳入理由": "product exposure and current qualification evidence",
    "淘汰理由": "not rejected; realized revenue evidence is still absent",
    "下一验证证据": "customer qualification completion and revenue disclosure",
}


def table_headers(markdown: str, heading: str) -> tuple[str, ...]:
    lines = markdown.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration as exc:
        raise AssertionError(f"missing template heading: {heading}") from exc

    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if stripped.startswith("|") and stripped.endswith("|"):
            return tuple(cell.strip() for cell in stripped.strip("|").split("|"))
    raise AssertionError(f"missing Markdown table after heading: {heading}")


class WeeklyChainTemplatePipelineTests(unittest.TestCase):
    maxDiff = None

    def test_each_template_runs_through_normalizer_and_validator(self) -> None:
        for template in TEMPLATES:
            with self.subTest(template=template.parent.name):
                markdown = template.read_text(encoding="utf-8")
                packet: dict[str, list[dict[str, str]]] = {}
                for table, heading in TABLE_HEADINGS.items():
                    headers = table_headers(markdown, heading)
                    self.assertEqual(headers, EXPECTED_HEADERS[table])
                    packet[table] = [{header: FIELD_VALUES[header] for header in headers}]

                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_root = Path(temp_dir)
                    packet_path = temp_root / "template-evidence.json"
                    packet_path.write_text(
                        json.dumps(packet, ensure_ascii=False), encoding="utf-8"
                    )
                    normalized = subprocess.run(
                        [
                            sys.executable,
                            str(NORMALIZER),
                            "--input",
                            str(packet_path),
                            "--as-of",
                            "2026-07-27",
                            "--strict",
                        ],
                        cwd=ROOT,
                        text=True,
                        encoding="utf-8",
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(
                        normalized.returncode,
                        0,
                        msg=f"{normalized.stdout}\n{normalized.stderr}",
                    )
                    normalized_packet = json.loads(normalized.stdout)
                    self.assertEqual(normalized_packet["issues"], [])

                    check = normalized_packet["tables"]["bottleneck_evidence_checks"][0]
                    ledger = normalized_packet["tables"]["bottleneck_ledger"][0]
                    self.assertEqual(
                        check["review_status"], "eligible_for_bottleneck_review"
                    )
                    self.assertEqual(
                        ledger["evidence_review_status"], check["review_status"]
                    )
                    for table_rows in normalized_packet["tables"].values():
                        for row in table_rows:
                            self.assertNotIn("_extra", row)

                    checks_csv = temp_root / "bottleneck_evidence_checks.csv"
                    with checks_csv.open("w", encoding="utf-8", newline="") as handle:
                        writer = csv.DictWriter(handle, fieldnames=list(check))
                        writer.writeheader()
                        writer.writerow(check)

                    validated = subprocess.run(
                        [
                            sys.executable,
                            str(VALIDATOR),
                            "--csv",
                            str(checks_csv),
                            "--as-of",
                            "2026-07-27",
                        ],
                        cwd=ROOT,
                        text=True,
                        encoding="utf-8",
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(
                        validated.returncode,
                        0,
                        msg=f"{validated.stdout}\n{validated.stderr}",
                    )
                    validation = json.loads(validated.stdout)
                    self.assertEqual(
                        validation["nodes"][0]["review_status"],
                        "eligible_for_bottleneck_review",
                    )


if __name__ == "__main__":
    unittest.main()
