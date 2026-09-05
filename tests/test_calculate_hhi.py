from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents" / "skills" / "research-industry-chain" / "scripts" / "calculate_hhi.py"
SPEC = importlib.util.spec_from_file_location("calculate_hhi", SCRIPT)
assert SPEC and SPEC.loader
HHI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HHI)


class CalculateHhiTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def test_explicit_percent_suffix_keeps_partial_market_coverage(self) -> None:
        result = HHI.calculate_hhi(["0.9%", "0.1%"])
        self.assertEqual(result["hhi"], 0.82)
        self.assertEqual(result["share_total"], 1.0)
        self.assertEqual(result["shares_percent"], [0.9, 0.1])
        self.assertIn("coverage_warning", result)

    def test_percent_and_fraction_units_are_explicit_and_equivalent(self) -> None:
        percent = HHI.calculate_hhi([30, 30, 20, 20], unit="percent")
        fraction = HHI.calculate_hhi([0.3, 0.3, 0.2, 0.2], unit="fraction")
        self.assertEqual(percent["hhi"], 2600)
        self.assertEqual(percent["hhi"], fraction["hhi"])
        partial = HHI.calculate_hhi([0.9, 0.1], unit="percent")
        self.assertEqual(partial["hhi"], 0.82)

    def test_bare_numbers_without_unit_are_rejected(self) -> None:
        for shares in ([0.9, 0.1], [90, 10], ["0.9%", "0.1"]):
            with self.subTest(shares=shares), self.assertRaisesRegex(ValueError, "unit"):
                HHI.calculate_hhi(shares)

    def test_complete_and_nearly_complete_coverage_are_distinguished(self) -> None:
        complete = HHI.calculate_hhi([100], unit="percent")
        self.assertEqual(complete["hhi"], 10000)
        self.assertNotIn("coverage_warning", complete)
        partial = HHI.calculate_hhi([99.5], unit="percent")
        self.assertEqual(partial["share_total"], 99.5)
        self.assertIn("coverage_warning", partial)

    def test_invalid_values_and_overcoverage_are_rejected(self) -> None:
        for shares, unit in (
            ([float("nan"), 1], "percent"),
            ([float("inf")], "percent"),
            ([-1, 99], "percent"),
            ([101], "percent"),
            ([60, 41], "percent"),
            ([1.01], "fraction"),
            ([0.6, 0.5], "fraction"),
            ([0, 0], "percent"),
            ([], "percent"),
            (["0.9%", "0.1%"], "fraction"),
            (["1%%"], "percent"),
        ):
            with self.subTest(shares=shares, unit=unit), self.assertRaises(ValueError):
                HHI.calculate_hhi(shares, unit=unit)

    def test_cli_accepts_suffix_and_rejects_ambiguous_numbers(self) -> None:
        proc = self.run_cli("--shares", "0.9%", "0.1%")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["hhi"], 0.82)
        self.assertEqual(self.run_cli("--shares", "0.9", "0.1").returncode, 2)
        proc = self.run_cli("--shares", "0.9", "0.1", "--unit", "fraction")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["hhi"], 8200)

    def test_csv_preserves_percent_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shares.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerows([["company", "share"], ["a", "0.9%"], ["b", "0.1%"]])
            proc = self.run_cli("--csv", str(path), "--company-column", "company")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["hhi"], 0.82)
        self.assertEqual(payload["share_total"], 1.0)
        self.assertIn("coverage_warning", payload)


if __name__ == "__main__":
    unittest.main()
