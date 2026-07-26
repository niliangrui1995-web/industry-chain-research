from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / ".agents"
    / "skills"
    / "research-industry-chain"
    / "scripts"
    / "normalize_research_inputs.py"
)


class IndustryResearchInputTests(unittest.TestCase):
    def run_csv(
        self,
        table: str,
        headers: list[str],
        row: list[str],
        as_of: str = "2026-07-27",
    ) -> tuple[int, dict[str, object]]:
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", encoding="utf-8-sig", newline="", delete=False
        )
        with handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerow(row)
        path = Path(handle.name)
        self.addCleanup(path.unlink, missing_ok=True)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(path),
                "--table",
                table,
                "--as-of",
                as_of,
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        return proc.returncode, json.loads(proc.stdout)

    def run_json(
        self, payload: dict[str, object], as_of: str = "2026-07-27"
    ) -> tuple[int, dict[str, object]]:
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        )
        with handle:
            json.dump(payload, handle, ensure_ascii=False)
        path = Path(handle.name)
        self.addCleanup(path.unlink, missing_ok=True)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(path),
                "--as-of",
                as_of,
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        return proc.returncode, json.loads(proc.stdout)

    def test_chinese_bottleneck_headers_preserve_decision_fields(self) -> None:
        headers = [
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
        ]
        row = [
            "check-qualified-material-20260727",
            "qualified material",
            "soft_bottleneck",
            "current",
            "2026-07-27",
            "180",
            "demand_step",
            "qualified_supply_limit",
            "customer ramp",
            "2026-07-20",
            "official_counterparty",
            "https://example.com/customer-ramp",
            "qualified capacity",
            "2026-07-18",
            "company_original",
            "https://example.com/capacity",
            "allocation",
            "2026-07-25",
            "official_counterparty",
            "https://example.com/allocation",
            "allocation and delayed delivery",
            "yield and qualification",
            "two quarters",
            "alternate grade",
            "qualifying",
            "2027Q1",
            "allocation persists",
            "second source trial",
            "second source reaches volume",
            "A",
            "official filings",
            "2026-07-25",
        ]
        code, payload = self.run_csv("瓶颈证据检查", headers, row)
        self.assertEqual(code, 0)
        self.assertEqual(payload["issues"], [])
        normalized = payload["tables"]["bottleneck_evidence_checks"][0]
        self.assertEqual(payload["schema_version"], "industry-chain-data-v2")
        self.assertEqual(payload["as_of"], "2026-07-27")
        self.assertEqual(normalized["second_source_status"], "qualifying")
        self.assertEqual(normalized["counterevidence"], "second source trial")
        self.assertEqual(normalized["max_age_days"], 180)
        self.assertEqual(normalized["review_status"], "eligible_for_bottleneck_review")
        self.assertNotIn("_extra", normalized)

        future_row = row.copy()
        future_row[headers.index("需求证据日期")] = "2099-01-01"
        code, payload = self.run_csv("瓶颈证据检查", headers, future_row)
        self.assertEqual(code, 2)
        self.assertIn(
            "demand_evidence_date cannot be after as_of",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

    def test_node_and_candidate_new_fields_are_not_dropped(self) -> None:
        code, node_payload = self.run_csv(
            "supply_chain_nodes",
            ["层级", "物理层级", "节点", "证据等级", "来源"],
            ["upstream", "material", "low-loss cloth", "B", "industry source"],
        )
        self.assertEqual(code, 0)
        node = node_payload["tables"]["supply_chain_nodes"][0]
        self.assertEqual(node["physical_level"], "material")
        self.assertNotIn("_extra", node)

        code, candidate_payload = self.run_csv(
            "china_candidates",
            [
                "公司",
                "代码",
                "交易所",
                "关联节点",
                "敞口证据",
                "商业化阶段",
                "阶段证据",
                "阶段日期",
                "阶段声明窗口",
                "阶段来源",
                "阶段来源类型",
                "阶段来源定位",
                "证据等级",
                "结论",
                "纳入理由",
                "淘汰理由",
                "下一验证证据",
            ],
            [
                "示例公司",
                "000001.SZ",
                "SZSE",
                "qualified material",
                "产品和客户认证证据",
                "qualification",
                "客户认证公告",
                "2026-07-20",
                "current",
                "公司公告",
                "company_original",
                "https://example.com/disclosure",
                "A",
                "watch_only",
                "产品证据",
                "N/A",
                "收入占比",
            ],
        )
        self.assertEqual(code, 0)
        candidate = candidate_payload["tables"]["china_candidates"][0]
        self.assertEqual(candidate["inclusion_reason"], "产品证据")
        self.assertEqual(candidate["next_evidence"], "收入占比")
        self.assertEqual(candidate["commercialization_stage"], "qualification")
        self.assertNotIn("_extra", candidate)

        code, invalid_payload = self.run_csv(
            "china_candidates",
            [
                "公司",
                "代码",
                "交易所",
                "关联节点",
                "敞口证据",
                "商业化阶段",
                "阶段证据",
                "阶段日期",
                "阶段声明窗口",
                "阶段来源",
                "阶段来源类型",
                "阶段来源定位",
                "证据等级",
                "结论",
                "来源",
            ],
            [
                "示例公司",
                "000001.SZ",
                "SZSE",
                "qualified material",
                "产品证据",
                "core_beneficiary",
                "概念标签",
                "2026-07-20",
                "current",
                "数据商",
                "third_party",
                "https://example.com/vendor",
                "B",
                "main_candidate",
                "数据商",
            ],
        )
        self.assertEqual(code, 2)
        self.assertIn("invalid commercialization_stage", invalid_payload["issues"][0]["message"])

    def test_bottleneck_ledger_cannot_pass_with_only_a_claimed_gap(self) -> None:
        code, payload = self.run_csv(
            "bottleneck_ledger",
            ["堵点", "供应缺口证据", "约束机制"],
            ["material", "claimed shortage", "capacity"],
        )
        self.assertEqual(code, 2)
        issue = payload["issues"][0]["message"]
        self.assertIn("demand_evidence", issue)
        self.assertIn("counterevidence", issue)
        self.assertIn("status_change", issue)

    def test_self_graded_hard_ledger_requires_unique_eligible_companion(self) -> None:
        ledger = {
            "bottleneck_node": "qualified material",
            "claim_as_of": "2026-07-27",
            "demand_evidence": "anonymous claim from 2010",
            "supply_evidence": "anonymous claim from 2010",
            "supply_gap_evidence": "anonymous rumor from 2010",
            "constraint_mechanism": "qualification",
            "severity": "hard_bottleneck",
            "time_horizon": "current",
            "substitution_path": "none claimed",
            "second_source_status": "none",
            "relief_window": "unknown",
            "positive_validation": "rumor repeats",
            "counterevidence": "none claimed",
            "status_change": "new",
            "key_reversal": "second source qualifies",
            "evidence_grade": "A",
            "source": "anonymous social post from 2010",
        }
        code, payload = self.run_json({"bottleneck_ledger": [ledger]})
        self.assertEqual(code, 2)
        self.assertIn(
            "requires claim_as_of, evidence_check_id",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

        ledger["evidence_check_id"] = "self-reported-check"
        ledger["evidence_review_status"] = "eligible_for_bottleneck_review"
        code, payload = self.run_json({"bottleneck_ledger": [ledger]})
        self.assertEqual(code, 2)
        self.assertIn(
            "must uniquely match bottleneck_evidence_checks.check_id",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

    def test_hard_ledger_accepts_only_normalizer_computed_eligible_companion(self) -> None:
        check = {
            "check_id": "check-qualified-material-20260727",
            "node": "qualified material",
            "severity": "hard_bottleneck",
            "claim_window": "current",
            "claim_as_of": "2026-07-27",
            "demand_evidence_kind": "demand_step",
            "supply_evidence_kind": "qualified_supply_limit",
            "demand_evidence": "customer ramp disclosure",
            "demand_evidence_date": "2026-07-20",
            "demand_source_type": "official_counterparty",
            "demand_source_locator": "https://example.com/customer-ramp",
            "supply_evidence": "qualified capacity disclosure",
            "supply_evidence_date": "2026-07-18",
            "supply_source_type": "company_original",
            "supply_source_locator": "https://example.com/capacity",
            "supply_gap_evidence": "allocation notice",
            "gap_evidence_date": "2026-07-25",
            "gap_source_type": "official_counterparty",
            "gap_source_locator": "https://example.com/allocation",
            "direct_gap_consequence": "allocation and delayed delivery",
            "constraint_mechanism": "qualification and yield",
            "time_horizon": "next two quarters",
            "substitution_path": "second-source qualification",
            "second_source_status": "qualifying",
            "relief_window": "two quarters if qualification succeeds",
            "positive_validation": "allocation persists",
            "counterevidence": "second-source trial",
            "key_reversal": "second source reaches volume",
            "evidence_grade": "A",
            "source": "official disclosures",
            "source_date": "2026-07-25",
        }
        ledger = {
            "bottleneck_node": "qualified material",
            "claim_as_of": check["claim_as_of"],
            "evidence_check_id": check["check_id"],
            "evidence_review_status": "eligible_for_bottleneck_review",
            "demand_evidence": check["demand_evidence"],
            "supply_evidence": check["supply_evidence"],
            "supply_gap_evidence": check["supply_gap_evidence"],
            "constraint_mechanism": check["constraint_mechanism"],
            "severity": "hard_bottleneck",
            "time_horizon": check["time_horizon"],
            "substitution_path": check["substitution_path"],
            "second_source_status": check["second_source_status"],
            "relief_window": check["relief_window"],
            "positive_validation": check["positive_validation"],
            "counterevidence": check["counterevidence"],
            "status_change": "new",
            "key_reversal": check["key_reversal"],
            "evidence_grade": "A",
            "source": "official disclosures",
        }
        code, payload = self.run_json(
            {
                "bottleneck_evidence_checks": [check],
                "bottleneck_ledger": [ledger],
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["issues"], [])
        normalized_check = payload["tables"]["bottleneck_evidence_checks"][0]
        self.assertEqual(
            normalized_check["review_status"], "eligible_for_bottleneck_review"
        )

        ledger["evidence_review_status"] = "watch_only"
        code, payload = self.run_json(
            {
                "bottleneck_evidence_checks": [check],
                "bottleneck_ledger": [ledger],
            }
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "must equal the normalizer-computed",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

        code, payload = self.run_json(
            {
                "bottleneck_evidence_checks": [check, dict(check)],
                "bottleneck_ledger": [ledger],
            }
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "check_id must be unique",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

    def test_historical_soft_check_cannot_back_current_soft_ledger(self) -> None:
        check = {
            "check_id": "historical-soft-2010",
            "node": "qualified material",
            "severity": "soft_bottleneck",
            "claim_window": "historical",
            "claim_as_of": "2010-07-27",
            "demand_evidence_kind": "demand_step",
            "supply_evidence_kind": "qualified_supply_limit",
            "demand_evidence": "historical customer ramp",
            "demand_evidence_date": "2010-07-20",
            "demand_source_type": "official_counterparty",
            "demand_source_locator": "https://example.com/2010-demand",
            "supply_evidence": "historical capacity disclosure",
            "supply_evidence_date": "2010-07-18",
            "supply_source_type": "company_original",
            "supply_source_locator": "https://example.com/2010-supply",
            "supply_gap_evidence": "historical allocation",
            "gap_evidence_date": "2010-07-25",
            "gap_source_type": "official_counterparty",
            "gap_source_locator": "https://example.com/2010-gap",
            "direct_gap_consequence": "historical delivery delay",
            "constraint_mechanism": "qualification",
            "time_horizon": "current quarter",
            "substitution_path": "second-source qualification",
            "second_source_status": "qualifying",
            "relief_window": "one quarter",
            "positive_validation": "allocation persists",
            "counterevidence": "second-source trial",
            "key_reversal": "second source reaches volume",
            "evidence_grade": "B",
            "source": "historical official disclosures",
            "source_date": "2010-07-25",
        }
        ledger = {
            "bottleneck_node": "qualified material",
            "claim_as_of": "2026-07-27",
            "evidence_check_id": check["check_id"],
            "evidence_review_status": "eligible_for_bottleneck_review",
            "demand_evidence": check["demand_evidence"],
            "supply_evidence": check["supply_evidence"],
            "supply_gap_evidence": check["supply_gap_evidence"],
            "constraint_mechanism": check["constraint_mechanism"],
            "severity": "soft_bottleneck",
            "time_horizon": "current quarter",
            "substitution_path": check["substitution_path"],
            "second_source_status": check["second_source_status"],
            "relief_window": check["relief_window"],
            "positive_validation": check["positive_validation"],
            "counterevidence": check["counterevidence"],
            "status_change": "new",
            "key_reversal": check["key_reversal"],
            "evidence_grade": "B",
            "source": "historical official disclosures",
        }
        code, payload = self.run_json(
            {
                "bottleneck_evidence_checks": [check],
                "bottleneck_ledger": [ledger],
            }
        )
        self.assertEqual(code, 2)
        normalized_check = payload["tables"]["bottleneck_evidence_checks"][0]
        self.assertEqual(
            normalized_check["review_status"], "eligible_for_bottleneck_review"
        )
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("requires a current claim_window companion", messages)
        self.assertIn("claim_as_of must equal top-level as_of", messages)

        check["claim_window"] = "current"
        check["claim_as_of"] = "2026-07-27"
        check["demand_evidence_date"] = "2026-07-20"
        check["supply_evidence_date"] = "2026-07-18"
        check["gap_evidence_date"] = "2026-07-25"
        check["source_date"] = "2026-07-25"
        code, payload = self.run_json(
            {
                "bottleneck_evidence_checks": [check],
                "bottleneck_ledger": [ledger],
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["issues"], [])

    def test_hard_bottleneck_placeholders_and_invalid_enums_are_rejected(self) -> None:
        headers = [
            "堵点",
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
            "状态变化",
            "关键反转",
            "证据等级",
            "来源",
        ]
        placeholder_row = [
            "qualified material",
            "blocked",
            "pending",
            "TODO",
            "TBD",
            "hard_bottleneck",
            "-",
            "alternate grade",
            "qualifying",
            "2027Q1",
            "allocation persists",
            "second source trial",
            "unchanged",
            "second source reaches volume",
            "A",
            "--",
        ]
        code, payload = self.run_csv("bottleneck_ledger", headers, placeholder_row)
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        for field in (
            "demand_evidence",
            "supply_evidence",
            "supply_gap_evidence",
            "constraint_mechanism",
            "time_horizon",
            "source",
        ):
            self.assertIn(field, messages)

        invalid_enum_row = [
            "qualified material",
            "dated customer ramp evidence",
            "dated qualified-capacity evidence",
            "dated allocation evidence",
            "yield and qualification",
            "critical_bottleneck",
            "two quarters",
            "alternate grade",
            "qualifying",
            "2027Q1",
            "allocation persists",
            "second source trial",
            "promoted",
            "second source reaches volume",
            "A",
            "official filings",
        ]
        code, payload = self.run_csv("bottleneck_ledger", headers, invalid_enum_row)
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("invalid severity", messages)
        self.assertIn("invalid status_change", messages)

    def test_revenue_main_candidate_placeholders_and_bad_date_are_rejected(self) -> None:
        code, payload = self.run_csv(
            "china_candidates",
            [
                "公司",
                "代码",
                "交易所",
                "关联节点",
                "敞口证据",
                "商业化阶段",
                "阶段证据",
                "阶段日期",
                "阶段声明窗口",
                "阶段来源",
                "阶段来源类型",
                "阶段来源定位",
                "证据等级",
                "结论",
                "收入占比",
                "证据缺口",
                "来源",
            ],
            [
                "示例公司",
                "000001.SZ",
                "SZSE",
                "qualified material",
                "产品和客户证据",
                "revenue",
                "evidence_absent",
                "2026-02-30",
                "current",
                "not_found",
                "anonymous",
                "N/A",
                "A",
                "main_candidate",
                "N/A",
                "N/A",
                "TODO",
            ],
        )
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("stage_evidence", messages)
        self.assertIn("stage_source", messages)
        self.assertIn("source", messages)
        self.assertIn("revenue_materiality", messages)
        self.assertIn("invalid stage_evidence_date", messages)

    def test_main_candidate_cannot_be_disconnected_from_a_node_or_exposure(self) -> None:
        code, payload = self.run_csv(
            "china_candidates",
            [
                "公司",
                "代码",
                "交易所",
                "关联节点",
                "敞口证据",
                "商业化阶段",
                "阶段证据",
                "阶段日期",
                "阶段声明窗口",
                "阶段来源",
                "阶段来源类型",
                "阶段来源定位",
                "证据等级",
                "结论",
                "来源",
            ],
            [
                "示例公司",
                "000001.SZ",
                "SZSE",
                "N/A",
                "pending",
                "qualification",
                "客户认证公告",
                "2026-07-20T18:00:00+08:00",
                "current",
                "公司公告",
                "company_original",
                "https://example.com/disclosure",
                "A",
                "main_candidate",
                "公司公告",
            ],
        )
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("linked_node", messages)
        self.assertIn("exposure_evidence", messages)

    def test_future_stage_evidence_cannot_cross_explicit_as_of(self) -> None:
        headers = [
            "公司",
            "代码",
            "交易所",
            "关联节点",
            "敞口证据",
            "商业化阶段",
            "阶段证据",
            "阶段日期",
            "阶段声明窗口",
            "阶段来源",
            "阶段来源类型",
            "阶段来源定位",
            "证据等级",
            "结论",
            "收入占比",
            "来源",
        ]
        row = [
            "示例公司",
            "000001.SZ",
            "SZSE",
            "qualified material",
            "产品收入披露",
            "revenue",
            "分部收入披露",
            "2099-01-01",
            "current",
            "公司年报",
            "company_original",
            "https://example.com/annual-report",
            "A",
            "main_candidate",
            "major",
            "公司年报",
        ]
        code, payload = self.run_csv("china_candidates", headers, row)
        self.assertEqual(code, 2)
        self.assertIn(
            "stage_evidence_date cannot be after as_of 2026-07-27",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

        row[headers.index("阶段日期")] = "2026-07-27"
        code, payload = self.run_csv("china_candidates", headers, row)
        self.assertEqual(code, 0)
        self.assertEqual(payload["as_of"], "2026-07-27")
        self.assertEqual(payload["issues"], [])

        row[headers.index("阶段日期")] = "2010-01-01"
        code, payload = self.run_csv("china_candidates", headers, row)
        self.assertEqual(code, 2)
        self.assertIn(
            "stage evidence older than 365 days",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

        row[headers.index("阶段声明窗口")] = "historical"
        row[headers.index("结论")] = "watch_only"
        code, payload = self.run_csv("china_candidates", headers, row)
        self.assertEqual(code, 0)
        candidate = payload["tables"]["china_candidates"][0]
        self.assertEqual(candidate["stage_claim_window"], "historical")
        self.assertEqual(candidate["stage_max_age_days"], 365)

    def test_anonymous_social_evidence_cannot_realize_revenue_or_main_candidate(self) -> None:
        headers = [
            "公司",
            "代码",
            "交易所",
            "关联节点",
            "敞口证据",
            "商业化阶段",
            "阶段证据",
            "阶段日期",
            "阶段声明窗口",
            "阶段来源",
            "阶段来源类型",
            "阶段来源定位",
            "证据等级",
            "结论",
            "收入占比",
            "来源",
        ]
        row = [
            "示例公司",
            "000001.SZ",
            "SZSE",
            "qualified material",
            "产品收入传闻",
            "revenue",
            "匿名帖子称已产生收入",
            "2026-07-20",
            "current",
            "anonymous social post",
            "anonymous",
            "https://example.com/social-post",
            "A",
            "main_candidate",
            "major",
            "anonymous social post",
        ]
        code, payload = self.run_csv("china_candidates", headers, row)
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("requires stage_source_type", messages)
        self.assertIn("cannot support a realized stage or main_candidate", messages)

        row[headers.index("商业化阶段")] = "qualification"
        row[headers.index("结论")] = "watch_only"
        row[headers.index("证据等级")] = "C"
        code, payload = self.run_csv("china_candidates", headers, row)
        self.assertEqual(code, 0)
        self.assertEqual(payload["issues"], [])

    def test_market_and_source_dates_respect_explicit_as_of(self) -> None:
        code, payload = self.run_csv(
            "market_snapshot",
            ["代码", "交易所", "日期"],
            ["000001.SZ", "SZSE", "2099-01-01"],
        )
        self.assertEqual(code, 2)
        self.assertIn("date cannot be after as_of", payload["issues"][0]["message"])

        code, payload = self.run_csv(
            "source_evidence",
            ["主张", "来源", "日期"],
            ["qualified capacity is constrained", "official filing", "2099-01-01"],
        )
        self.assertEqual(code, 2)
        self.assertIn("date cannot be after as_of", payload["issues"][0]["message"])

    def test_likely_future_bottleneck_requires_a_dated_falsifiable_packet(self) -> None:
        headers = [
            "node",
            "current_status",
            "future_status",
            "demand_trigger",
            "supply_lag_mechanism",
            "likely_timing",
            "confidence",
            "evidence_gap",
            "reversal_indicator",
            "evidence_date",
            "source_type",
            "source_locator",
            "evidence_grade",
            "source",
        ]
        code, payload = self.run_csv(
            "future_bottleneck_scenarios",
            headers,
            [
                "MagicNode",
                "watch",
                "likely_future_bottleneck",
                "next platform ramp",
                "qualification lag",
                "TBD",
                "pending",
                "evidence_absent",
                "not_found",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "--",
            ],
        )
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        for field in (
            "likely_timing",
            "confidence",
            "evidence_gap",
            "reversal_indicator",
            "evidence_date",
            "source_type",
            "source_locator",
            "evidence_grade",
            "source",
        ):
            self.assertIn(field, messages)

        code, payload = self.run_csv(
            "future_bottleneck_scenarios",
            headers,
            [
                "MagicNode",
                "watch",
                "likely_future_bottleneck",
                "next platform ramp",
                "qualification lag",
                "2027H1",
                "high",
                "qualified-capacity disclosure still missing",
                "second source qualifies",
                "2026-07-20",
                "credible_third_party",
                "https://example.com/industry-report",
                "C",
                "industry channel check",
            ],
        )
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("high confidence requires A/B", messages)

        code, payload = self.run_csv(
            "future_bottleneck_scenarios",
            headers,
            [
                "MagicNode",
                "magic_status",
                "certain_bottleneck",
                "next platform ramp",
                "qualification lag",
                "2027H1",
                "certain",
                "qualified-capacity disclosure still missing",
                "second source qualifies",
                "2026-07-20",
                "official",
                "https://example.com/official-roadmap",
                "A",
                "official roadmap",
            ],
        )
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("invalid current_status", messages)
        self.assertIn("invalid future_status", messages)
        self.assertIn("invalid confidence", messages)

        anonymous_high = [
            "MagicNode",
            "watch",
            "likely_future_bottleneck",
            "next platform ramp",
            "qualification lag",
            "2027H1",
            "high",
            "qualified-capacity disclosure still missing",
            "second source qualifies",
            "2010-01-01",
            "anonymous",
            "https://example.com/anonymous-post",
            "A",
            "anonymous social post from 2010",
        ]
        code, payload = self.run_csv(
            "future_bottleneck_scenarios", headers, anonymous_high
        )
        self.assertEqual(code, 2)
        messages = "\n".join(issue["message"] for issue in payload["issues"])
        self.assertIn("likely/high future scenario requires", messages)
        self.assertIn("limited to low-confidence watch", messages)

        stale_official = anonymous_high.copy()
        stale_official[headers.index("source_type")] = "official"
        stale_official[headers.index("source_locator")] = (
            "https://example.com/official-roadmap"
        )
        stale_official[headers.index("source")] = "official roadmap from 2010"
        code, payload = self.run_csv(
            "future_bottleneck_scenarios", headers, stale_official
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "future evidence older than 365 days",
            "\n".join(issue["message"] for issue in payload["issues"]),
        )

        fresh_official = stale_official.copy()
        fresh_official[headers.index("evidence_date")] = "2026-07-20"
        fresh_official[headers.index("source")] = "official roadmap"
        code, payload = self.run_csv(
            "future_bottleneck_scenarios", headers, fresh_official
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["issues"], [])
        scenario = payload["tables"]["future_bottleneck_scenarios"][0]
        self.assertEqual(scenario["future_max_age_days"], 365)


if __name__ == "__main__":
    unittest.main()
