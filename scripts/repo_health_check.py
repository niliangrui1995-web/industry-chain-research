#!/usr/bin/env python3
"""Repository health checks for the investment-research workspace."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import py_compile
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills"
ZIJIN_ROOT = ROOT.parent / "紫金研选"
ZIJIN_PYTHON = ZIJIN_ROOT / ".venv" / "Scripts" / "python.exe"
EXPECTED_PROJECT_SKILLS = {
    "a-share-company-tracking",
    "a-share-disclosure-trading-data",
    "a-share-leverage-capitulation-analyst",
    "ai-chain-research-orchestrator",
    "earnings-call-investment-analyst",
    "financial-evidence-audit",
    "ht-local-market-data",
    "income-investment",
    "kronos-market-forecasting",
    "research-industry-chain",
    "research-listed-company",
    "user-investment-discipline",
}
EXPECTED_KRONOS_A_SHARE_COMMANDS = {
    "snapshot",
    "prepare",
    "check",
    "train-adapter",
    "train-scorer",
    "evaluate",
    "score-as-of",
    "inspect-checkpoint",
    "pipeline",
}
SKILL_HEALTH_OVERRIDES = Path.home() / ".codex" / "skill-routing" / "skill-health-overrides.json"
DEFAULT_DOCS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "SKILL_PACK_MANIFEST.md",
    SKILL_ROOT / "research-listed-company" / "SKILL.md",
    SKILL_ROOT / "financial-evidence-audit" / "SKILL.md",
]
PYTHON_FILES = [
    ROOT / "scripts" / "automation_run_metadata.py",
    ROOT / "scripts" / "update_tungsten_price_tracker.py",
    ROOT / "scripts" / "earnings_parent_guardrail.py",
    ROOT / "scripts" / "create_company_watchlist.py",
    ROOT / "scripts" / "repo_health_check.py",
    ROOT / "scripts" / "validate_company_tracking_run.py",
    SKILL_ROOT / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
    SKILL_ROOT / "a-share-leverage-capitulation-analyst" / "scripts" / "audit_margin_history.py",
    SKILL_ROOT / "a-share-leverage-capitulation-analyst" / "scripts" / "audit_market_data.py",
    SKILL_ROOT / "a-share-leverage-capitulation-analyst" / "scripts" / "fetch_szse_margin_repairs.py",
    SKILL_ROOT / "a-share-leverage-capitulation-analyst" / "scripts" / "leverage_capitulation_backtest.py",
    SKILL_ROOT / "financial-evidence-audit" / "scripts" / "financial_evidence_audit.py",
    SKILL_ROOT / "research-industry-chain" / "scripts" / "validate_bottleneck_evidence.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_baseline.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_data.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_dataset.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_evaluation.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_forward.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_model.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_public_data.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_runtime.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "kronos_a_share_training.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "run_kronos_a_share.py",
    SKILL_ROOT / "kronos-market-forecasting" / "scripts" / "run_kronos_forecast.py",
]
SECRET_PATTERNS = [
    ("openai_key", re.compile(r"\b(?:sk-proj-[A-Za-z0-9_-]{40,}|sk-[A-Za-z0-9]{32,})\b")),
    ("github_token", re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)?PRIVATE KEY-----")),
    (
        "secret_assignment",
        re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*=\s*['\"]?[A-Za-z0-9_./+=-]{24,}"),
    ),
]
ALLOWED_REFERENCE_CONTEXT = (
    "explicit",
    "reference",
    "archived",
    "optional",
    "可选",
    "显式",
    "参考",
    "归档",
    "移出",
    "删除",
    "不进入默认",
    "不自动",
    "不保留",
    "只有用户明确",
    "only when",
    "do not route",
)


@dataclass
class CheckResult:
    name: str
    status: str
    details: list[str] = field(default_factory=list)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def result(name: str, ok: bool, details: Iterable[str] = ()) -> CheckResult:
    return CheckResult(name=name, status="ok" if ok else "fail", details=list(details))


def skipped(name: str, why: str) -> CheckResult:
    return CheckResult(name=name, status="skipped", details=[why])


def run_cmd(args: list[str], *, timeout: int = 60) -> tuple[int, str, str]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def check_routing_consistency() -> CheckResult:
    readme = read_text(ROOT / "README.md")
    agents = read_text(ROOT / "AGENTS.md")
    manifest = read_text(ROOT / "SKILL_PACK_MANIFEST.md")
    company = read_text(SKILL_ROOT / "research-listed-company" / "SKILL.md")
    industry = read_text(SKILL_ROOT / "research-industry-chain" / "SKILL.md")
    income = read_text(SKILL_ROOT / "income-investment" / "SKILL.md")
    discipline = read_text(SKILL_ROOT / "user-investment-discipline" / "SKILL.md")
    audit = read_text(SKILL_ROOT / "financial-evidence-audit" / "SKILL.md")
    kronos = read_text(SKILL_ROOT / "kronos-market-forecasting" / "SKILL.md")

    problems: list[str] = []
    required_pairs = [
        ("README.md", readme, "项目技能位于 Codex 标准仓库路径 `.agents/skills/`"),
        ("AGENTS.md", agents, "仓库技能位于 `.agents/skills/`"),
        ("SKILL_PACK_MANIFEST.md", manifest, "项目技能根目录：`.agents/skills/`"),
        ("research-listed-company/SKILL.md", company, "financial-evidence-audit"),
        ("research-industry-chain/SKILL.md", industry, "需求超过合格供给"),
        ("income-investment/SKILL.md", income, "不得对所有行业机械使用 EPS payout"),
        ("user-investment-discipline/SKILL.md", discipline, "每一次都一样！！！"),
        ("financial-evidence-audit/SKILL.md", audit, "投资数字的强制准出门"),
        ("kronos-market-forecasting/SKILL.md", kronos, "evidence_class=model_output"),
    ]
    for path, text, needle in required_pairs:
        if needle not in text:
            problems.append(f"{path}: missing `{needle}`")
    active_route_docs = [
        ("README.md", readme),
        ("AGENTS.md", agents),
        ("research-listed-company/SKILL.md", company),
        ("research-industry-chain/SKILL.md", industry),
        ("income-investment/SKILL.md", income),
        ("user-investment-discipline/SKILL.md", discipline),
    ]
    for path, text in active_route_docs:
        for needle in [
            "user-investment-framework",
            "skills/industry-research-router",
            "`industry-research-router` +",
        ]:
            if needle in text:
                problems.append(f"{path}: legacy routing text still present: `{needle}`")

    return result("routing_consistency", not problems, problems)


def check_skill_library_layout() -> CheckResult:
    problems: list[str] = []
    legacy_root = ROOT / "skills"
    if legacy_root.exists():
        problems.append("legacy root skills/ still exists; repository skills must live under .agents/skills")
    if not SKILL_ROOT.is_dir():
        return result("skill_library_layout", False, [f"missing {rel(SKILL_ROOT)}"])

    actual = {path.name for path in SKILL_ROOT.iterdir() if path.is_dir()}
    for name in sorted(EXPECTED_PROJECT_SKILLS - actual):
        problems.append(f"missing project skill: {name}")
    for name in sorted(actual - EXPECTED_PROJECT_SKILLS):
        problems.append(f"unexpected project skill: {name}")

    forbidden_active_terms = [
        "industry-research-router",
        "browser-grok-gemini-research",
        "semiconductor-ai-chain-investment-researcher",
        "user-investment-framework",
    ]
    for name in sorted(actual & EXPECTED_PROJECT_SKILLS):
        skill_dir = SKILL_ROOT / name
        skill_file = skill_dir / "SKILL.md"
        metadata_file = skill_dir / "agents" / "openai.yaml"
        if not skill_file.is_file():
            problems.append(f"{name}: missing SKILL.md")
            continue
        text = read_text(skill_file)
        lines = text.splitlines()
        if len(lines) > 180:
            problems.append(f"{name}: SKILL.md is {len(lines)} lines; expected <= 180")
        if name == "user-investment-discipline" and len(lines) > 100:
            problems.append(f"{name}: discipline entrypoint is {len(lines)} lines; expected <= 100")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
        if not frontmatter:
            problems.append(f"{name}: invalid frontmatter")
        else:
            name_match = re.search(r"(?m)^name:\s*([^\n]+)$", frontmatter.group(1))
            if not name_match or name_match.group(1).strip().strip('"\'') != name:
                problems.append(f"{name}: frontmatter name mismatch")
        for term in forbidden_active_terms:
            if term in text:
                problems.append(f"{name}: active SKILL.md references removed route `{term}`")
        if not metadata_file.is_file():
            problems.append(f"{name}: missing agents/openai.yaml")
        else:
            metadata = read_text(metadata_file)
            if f"${name}" not in metadata:
                problems.append(f"{name}: agents/openai.yaml default prompt does not mention ${name}")

    agents_lines = read_text(ROOT / "AGENTS.md").splitlines()
    if len(agents_lines) > 60:
        problems.append(f"AGENTS.md is {len(agents_lines)} lines; expected <= 60")
    return result("skill_library_layout", not problems, problems)


def load_archived_slugs() -> list[str]:
    if not SKILL_HEALTH_OVERRIDES.exists():
        return []
    data = json.loads(SKILL_HEALTH_OVERRIDES.read_text(encoding="utf-8"))
    return list(data.get("archived_skill_slugs") or [])


def check_archived_default_references() -> CheckResult:
    archived = set(load_archived_slugs())
    problems: list[str] = []
    for path in DEFAULT_DOCS:
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            for slug in archived:
                if slug not in line:
                    continue
                lowered = line.lower()
                if any(token in lowered for token in ALLOWED_REFERENCE_CONTEXT):
                    continue
                problems.append(f"{rel(path)}:{line_no}: archived/reference skill `{slug}` appears in active context")
    return result("archived_reference_default_refs", not problems, problems)


def check_py_compile() -> CheckResult:
    problems: list[str] = []
    with tempfile.TemporaryDirectory(prefix="repo-health-pycompile-") as tmp:
        tmp_path = Path(tmp)
        for index, path in enumerate(PYTHON_FILES):
            if not path.exists():
                problems.append(f"{rel(path)}: missing")
                continue
            cfile = tmp_path / f"{index}-{path.stem}.pyc"
            try:
                py_compile.compile(str(path), cfile=str(cfile), doraise=True)
            except py_compile.PyCompileError as exc:
                problems.append(f"{rel(path)}: {exc.msg}")
    return result("py_compile", not problems, problems)


def check_kronos_runner_contract() -> CheckResult:
    code, stdout, stderr = run_cmd(
        [sys.executable, "-m", "unittest", "tests.test_kronos_market_forecasting", "-v"],
        timeout=60,
    )
    details = [item for item in [stdout, stderr] if item]
    return result("kronos_runner_contract", code == 0, details)


def check_kronos_a_share_skill_contract() -> CheckResult:
    skill_dir = SKILL_ROOT / "kronos-market-forecasting"
    cli_path = skill_dir / "scripts" / "run_kronos_a_share.py"
    migration_path = skill_dir / "scripts" / "migrate_kronos_storage.ps1"
    rebuild_path = skill_dir / "scripts" / "rebuild_kronos_envs.ps1"
    config_path = skill_dir / "configs" / "a_share_daily_v1.yaml"
    pit_normalization_example_path = (
        skill_dir / "configs" / "pit_normalization_v1.example.json"
    )
    reference_path = skill_dir / "references" / "a-share-finetuning.md"
    requirements_path = skill_dir / "requirements-training.in"
    training_lock_path = skill_dir / "requirements-training.lock"
    torch_input_path = skill_dir / "requirements-torch-cu118.txt"
    torch_lock_path = skill_dir / "requirements-torch-cu118.lock"
    lock_contract_path = skill_dir / "requirements-lock-contract.json"
    manifest_path = ROOT / "SKILL_PACK_MANIFEST.md"
    problems: list[str] = []

    required_files = [
        cli_path,
        migration_path,
        rebuild_path,
        config_path,
        pit_normalization_example_path,
        reference_path,
        requirements_path,
        training_lock_path,
        torch_input_path,
        torch_lock_path,
        lock_contract_path,
    ]
    for path in required_files:
        if not path.is_file():
            problems.append(f"missing {rel(path)}")
    if problems:
        return result("kronos_a_share_skill_contract", False, problems)

    skill = read_text(skill_dir / "SKILL.md")
    cli = read_text(cli_path)
    migration = read_text(migration_path)
    rebuild = read_text(rebuild_path)
    config = read_text(config_path)
    pit_normalization_example = read_text(pit_normalization_example_path)
    reference = read_text(reference_path)
    training_lock = read_text(training_lock_path)
    torch_input = read_text(torch_input_path)
    torch_lock = read_text(torch_lock_path)
    lock_contract_text = read_text(lock_contract_path)
    manifest = read_text(manifest_path)
    gitignore = read_text(ROOT / ".gitignore")
    training_root = r"D:\vcp_hunter\产业链投研\_training\kronos_ashare"
    training_python = training_root + r"\runtime\venvs\kronos-ashare\Scripts\python.exe"

    required_pairs = [
        ("SKILL.md", skill, "scripts/run_kronos_a_share.py"),
        ("SKILL.md", skill, r"_training\kronos_ashare"),
        ("SKILL.md", skill, "evidence_class=model_output"),
        ("SKILL.md", skill, "`N/A`"),
        ("a_share_daily_v1.yaml", config, "schema_version: kronos-a-share-v1"),
        ("a_share_daily_v1.yaml", config, f"training_root: '{training_root}'"),
        (
            "pit_normalization_v1.example.json",
            pit_normalization_example,
            '"schema_version": "kronos-a-share-pit-normalization-v1"',
        ),
        ("migrate_kronos_storage.ps1", migration, f"$TrainingRoot = '{training_root}'"),
        ("migrate_kronos_storage.ps1", migration, "UV_CACHE_DIR"),
        ("migrate_kronos_storage.ps1", migration, "UV_PYTHON_INSTALL_DIR"),
        ("migrate_kronos_storage.ps1", migration, "PIP_CACHE_DIR"),
        ("migrate_kronos_storage.ps1", migration, "-ItemType Junction"),
        ("rebuild_kronos_envs.ps1", rebuild, "requirements-training.lock"),
        ("rebuild_kronos_envs.ps1", rebuild, "requirements-torch-cu118.lock"),
        ("rebuild_kronos_envs.ps1", rebuild, "--require-hashes"),
        ("rebuild_kronos_envs.ps1", rebuild, "function Assert-LockConsistency"),
        ("rebuild_kronos_envs.ps1", rebuild, "requirements-lock-contract.json"),
        ("rebuild_kronos_envs.ps1", rebuild, "training input/lock contract drifted"),
        ("rebuild_kronos_envs.ps1", rebuild, "'--no-deps', '--require-hashes'"),
        ("rebuild_kronos_envs.ps1", rebuild, "'pip', 'check', '--python', $python"),
        ("rebuild_kronos_envs.ps1", rebuild, "function Assert-InstalledPackages"),
        ("rebuild_kronos_envs.ps1", rebuild, "kronos-package-manifest.json"),
        ("rebuild_kronos_envs.ps1", rebuild, "kronos-environment-packages-v1"),
        ("rebuild_kronos_envs.ps1", rebuild, "runtime_observation = $RuntimeObservation"),
        ("rebuild_kronos_envs.ps1", rebuild, "& $python -I -B -c $validation"),
        ("rebuild_kronos_envs.ps1", rebuild, "& $PythonPath -I -B -c $inventoryScript"),
        ("rebuild_kronos_envs.ps1", rebuild, "cleanup_status = $cleanupStatus"),
        ("SKILL.md", skill, training_python),
        ("a-share-finetuning.md", reference, "migrate_kronos_storage.ps1 -Apply"),
        ("a-share-finetuning.md", reference, "rebuild_kronos_envs.ps1"),
        ("a-share-finetuning.md", reference, training_python),
        ("a-share-finetuning.md", reference, "& $AsharePython $AshareCli"),
        ("a-share-finetuning.md", reference, "build_project_qlib_provider()"),
        ("a-share-finetuning.md", reference, "build_evaluation_companion()"),
        ("a-share-finetuning.md", reference, "gate-head.json"),
        ("a-share-finetuning.md", reference, "registry_root_sha256"),
        ("a-share-finetuning.md", reference, "--inference-snapshot"),
        ("a-share-finetuning.md", reference, ".research-only.csv"),
        ("a-share-finetuning.md", reference, "output_type=N/A"),
        ("a-share-finetuning.md", reference, "evidence_class=model_output"),
        ("SKILL_PACK_MANIFEST.md", manifest, "`kronos-market-forecasting`"),
        ("SKILL_PACK_MANIFEST.md", manifest, "`model_output`"),
        ("SKILL_PACK_MANIFEST.md", manifest, "`N/A`"),
        ("run_kronos_a_share.py", cli, 'evidence_class="model_output"'),
        ("run_kronos_a_share.py", cli, 'output_type="N/A"'),
    ]
    for path, text, needle in required_pairs:
        if needle not in text:
            problems.append(f"{path}: missing `{needle}`")
    if "_training/" not in {line.strip() for line in gitignore.splitlines()}:
        problems.append(".gitignore: missing exact `_training/` entry")
    if len(EXPECTED_PROJECT_SKILLS) != 12:
        problems.append(
            "project skill allowlist changed; Kronos A-share must extend the existing skill"
        )

    def parse_hashed_lock(text: str, label: str) -> dict[str, str]:
        matches = list(
            re.finditer(
                r"(?m)^([A-Za-z0-9][A-Za-z0-9_.-]*(?:\[[^\]]+\])?)==([^\s\\;]+)",
                text,
            )
        )
        pins: dict[str, str] = {}
        for index, match in enumerate(matches):
            name = re.sub(r"[-_.]+", "-", re.sub(r"\[.*$", "", match.group(1))).lower()
            if name in pins:
                problems.append(f"{label}: duplicate exact pin `{name}`")
                continue
            pins[name] = match.group(2)
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            if not re.search(r"--hash=sha256:[0-9a-f]{64}", text[match.start():end]):
                problems.append(f"{label}: `{name}` has no SHA256 hash")
        if not pins:
            problems.append(f"{label}: no exact package pins")
        return pins

    training_pins = parse_hashed_lock(training_lock, "requirements-training.lock")
    torch_pins = parse_hashed_lock(torch_lock, "requirements-torch-cu118.lock")
    overlap = sorted(set(training_pins) & set(torch_pins))
    if "torch" in training_pins:
        problems.append("requirements-training.lock: torch must be wheel-lock only")
    if torch_pins != {"torch": "2.7.1+cu118"}:
        problems.append("requirements-torch-cu118.lock: expected only torch==2.7.1+cu118")
    if overlap:
        problems.append(f"Kronos dependency locks overlap: {overlap}")
    torch_input_lines = [
        line for line in torch_input.splitlines() if line and not line.startswith("#")
    ]
    if torch_input_lines != [
        "--index-url https://download.pytorch.org/whl/cu118",
        "torch==2.7.1+cu118",
    ]:
        problems.append("requirements-torch-cu118.txt: official index or exact pin drifted")
    if not any(
        "--no-deps" in line
        for line in torch_lock.splitlines()
        if line.startswith("#")
    ):
        problems.append("requirements-torch-cu118.lock: compile provenance lacks --no-deps")
    try:
        declared_lock_contract = json.loads(lock_contract_text)
    except json.JSONDecodeError as exc:
        problems.append(f"requirements-lock-contract.json: invalid JSON: {exc}")
        declared_lock_contract = {}
    if not isinstance(declared_lock_contract, dict):
        problems.append("requirements-lock-contract.json: root must be an object")
        declared_lock_contract = {}
    if declared_lock_contract.get("schema_version") != "kronos-dependency-lock-contract-v1":
        problems.append("requirements-lock-contract.json: schema mismatch")
    lock_contract_sections = [
        ("training", requirements_path, training_lock_path, training_pins),
        ("torch_cu118", torch_input_path, torch_lock_path, torch_pins),
    ]
    for section, input_path, locked_path, pins in lock_contract_sections:
        declared = declared_lock_contract.get(section, {})
        expected_input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
        expected_lock_hash = hashlib.sha256(locked_path.read_bytes()).hexdigest()
        if declared.get("input_sha256") != expected_input_hash:
            problems.append(f"requirements-lock-contract.json: {section} input hash drift")
        if declared.get("lock_sha256") != expected_lock_hash:
            problems.append(f"requirements-lock-contract.json: {section} lock hash drift")
        if declared.get("package_count") != len(pins):
            problems.append(f"requirements-lock-contract.json: {section} package count drift")
    preflight = rebuild.find("$lockContract = Assert-LockConsistency")
    first_rebuild = rebuild.find("$packageManifests += Rebuild-Venv")
    if preflight < 0 or first_rebuild < 0 or preflight >= first_rebuild:
        problems.append("rebuild_kronos_envs.ps1: lock preflight must run before venv rebuild")
    commit = rebuild.find("# Commit boundary:")
    cleanup = rebuild.find("Remove-Item -LiteralPath $Backup -Recurse -Force", commit)
    rollback = rebuild.find("Move-Item -LiteralPath $Backup -Destination $Destination")
    if commit < 0 or cleanup < commit or rollback < 0 or rollback >= commit:
        problems.append("rebuild_kronos_envs.ps1: cleanup must be outside the rollback region")

    interpreter = (
        ROOT
        / "_training"
        / "kronos_ashare"
        / "runtime"
        / "venvs"
        / "kronos-ashare"
        / "Scripts"
        / "python.exe"
    )
    if not interpreter.is_file():
        interpreter = ROOT / ".venv_kronos" / "Scripts" / "python.exe"
    if not interpreter.is_file():
        interpreter = Path(sys.executable)
    code, stdout, stderr = run_cmd(
        [str(interpreter), "-B", str(cli_path), "--help"],
        timeout=30,
    )
    if code != 0:
        problems.append(f"run_kronos_a_share.py --help failed: {stderr or stdout}")
    else:
        command_groups = [
            {item.strip() for item in match.split(",")}
            for match in re.findall(r"\{([a-z][a-z,-]+)\}", stdout)
            if "snapshot" in match.split(",")
        ]
        if not command_groups:
            problems.append("run_kronos_a_share.py --help: subcommand list not found")
        elif command_groups[0] != EXPECTED_KRONOS_A_SHARE_COMMANDS:
            missing = sorted(EXPECTED_KRONOS_A_SHARE_COMMANDS - command_groups[0])
            extra = sorted(command_groups[0] - EXPECTED_KRONOS_A_SHARE_COMMANDS)
            problems.append(f"A-share CLI commands mismatch: missing={missing}, extra={extra}")

    return result("kronos_a_share_skill_contract", not problems, problems)


def check_tungsten_report_only() -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="repo-health-tungsten-") as tmp:
        tmp_path = Path(tmp)
        history = tmp_path / "price_history.csv"
        with history.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "date",
                    "indicator",
                    "name",
                    "low",
                    "high",
                    "mid",
                    "unit",
                    "currency",
                    "source_name",
                    "source_url",
                    "source_grade",
                    "notes",
                ],
            )
            writer.writeheader()
        report_dir = tmp_path / "reports"
        code, stdout, stderr = run_cmd(
            [
                sys.executable,
                str(ROOT / "scripts" / "update_tungsten_price_tracker.py"),
                "--history",
                str(history),
                "--report-dir",
                str(report_dir),
                "--date",
                "2026-06-24",
                "--report-only",
            ],
            timeout=60,
        )
        report_path = report_dir / "2026-06-24.md"
        details = [item for item in [stdout, stderr] if item]
        if code == 0 and not report_path.exists():
            details.append("temporary report was not generated")
            code = 1
        return result("tungsten_report_only", code == 0, details)


def check_ht_inspect_help() -> CheckResult:
    code, stdout, stderr = run_cmd(
        [sys.executable, str(SKILL_ROOT / "ht-local-market-data" / "scripts" / "inspect_ht_data.py"), "--help"],
        timeout=30,
    )
    expected_root = r"D:\HT"
    details = [line for line in [stdout.splitlines()[0] if stdout else "", stderr] if line]
    if code == 0 and expected_root not in stdout:
        details.append(f"default root missing from help: {expected_root}")
    return result("ht_inspect_help", code == 0 and expected_root in stdout, details)


def check_earnings_guardrail() -> CheckResult:
    interpreter = ZIJIN_PYTHON if ZIJIN_PYTHON.is_file() else Path(sys.executable)
    code, stdout, stderr = run_cmd(
        [
            str(interpreter),
            str(ROOT / "scripts" / "earnings_parent_guardrail.py"),
            "--project-root",
            str(ROOT),
            "--zijin-root",
            str(ZIJIN_ROOT),
            "--output",
            "json",
        ],
        timeout=120,
    )
    details: list[str] = []
    if stderr:
        details.append(stderr)
    json_start = stdout.find("{")
    json_text = stdout[json_start:] if json_start >= 0 else stdout
    if json_start > 0:
        details.append("guardrail emitted log lines before JSON; parsed JSON payload after first `{`")
    try:
        payload, _ = json.JSONDecoder().raw_decode(json_text)
    except json.JSONDecodeError:
        details.append("guardrail output was not valid JSON")
        if stdout:
            details.append(stdout[:500])
        return result("earnings_guardrail_dry_run", False, details)
    status = payload.get("status")
    details.append(f"status={status}")
    details.append(f"mode={payload.get('mode')}")
    written = payload.get("snapshot_result", {}).get("written", [])
    if written:
        details.append("guardrail wrote snapshots during dry-run")
    ok = code in (0, 2) and payload.get("mode") == "dry_run" and status != "environment_preflight_failed" and not written
    return result("earnings_guardrail_dry_run", ok, details)


def git_ls_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    names = [name for name in proc.stdout.decode("utf-8", errors="replace").split("\0") if name]
    return [ROOT / name for name in names]


def check_secret_paths() -> CheckResult:
    problems: list[str] = []
    for path in git_ls_files():
        relative = rel(path)
        name = path.name.lower()
        if name in {".env", ".env.local", ".env.production"} or "credential" in name or name.endswith(".pem"):
            problems.append(f"{relative}: tracked_sensitive_filename")
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rule_name, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                problems.append(f"{relative}: {rule_name}")
                break
    return result("secret_path_scan", not problems, problems)


def check_git_diff_check() -> CheckResult:
    code, stdout, stderr = run_cmd(["git", "diff", "--check"], timeout=60)
    details = [item for item in [stdout, stderr] if item]
    return result("git_diff_check", code == 0, details)


def run_checks(skip_slow: bool) -> list[CheckResult]:
    checks = [
        check_routing_consistency(),
        check_skill_library_layout(),
        check_archived_default_references(),
        check_py_compile(),
        check_kronos_runner_contract(),
        check_kronos_a_share_skill_contract(),
        check_tungsten_report_only(),
        check_ht_inspect_help(),
        skipped("earnings_guardrail_dry_run", "--skip-slow") if skip_slow else check_earnings_guardrail(),
        check_secret_paths(),
        check_git_diff_check(),
    ]
    return checks


def print_human(checks: list[CheckResult]) -> None:
    for item in checks:
        label = {"ok": "OK", "fail": "FAIL", "skipped": "SKIP"}[item.status]
        print(f"[{label}] {item.name}")
        for detail in item.details:
            print(f"  - {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository health checks.")
    parser.add_argument("--skip-slow", action="store_true", help="Skip slower environment-dependent checks.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    checks = run_checks(args.skip_slow)
    if args.json:
        print(json.dumps({"status": "ok" if all(c.status != "fail" for c in checks) else "fail", "checks": [asdict(c) for c in checks]}, ensure_ascii=False, indent=2))
    else:
        print_human(checks)
    return 1 if any(item.status == "fail" for item in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
