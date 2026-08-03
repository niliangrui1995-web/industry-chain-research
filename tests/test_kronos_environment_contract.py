from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "kronos-market-forecasting"
TRAINING_PYTHON = (
    r"D:\vcp_hunter\产业链投研\_training\kronos_ashare"
    r"\runtime\venvs\kronos-ashare\Scripts\python.exe"
)
EXPECTED_A_SHARE_COMMANDS = {
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


def canonicalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_hashed_lock(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    current_name: str | None = None
    current_hashes = 0

    def finish_current() -> None:
        if current_name is not None and current_hashes == 0:
            raise AssertionError(f"pin without SHA256 hashes: {path} -> {current_name}")

    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(
            r"^([A-Za-z0-9][A-Za-z0-9_.-]*(?:\[[^\]]+\])?)==([^\s\\;]+)",
            line,
        )
        if match:
            finish_current()
            current_name = canonicalize(re.sub(r"\[.*$", "", match.group(1)))
            if current_name in pins:
                raise AssertionError(f"duplicate lock pin: {path} -> {current_name}")
            pins[current_name] = match.group(2)
            current_hashes = len(re.findall(r"--hash=sha256:[0-9a-f]{64}", line))
        elif current_name is not None:
            current_hashes += len(re.findall(r"--hash=sha256:[0-9a-f]{64}", line))
    finish_current()
    if not pins:
        raise AssertionError(f"lock contains no exact pins: {path}")
    return pins


class KronosEnvironmentContractTests(unittest.TestCase):
    def test_training_and_cu118_locks_are_disjoint_and_hashed(self) -> None:
        training_lock = SKILL_DIR / "requirements-training.lock"
        torch_lock = SKILL_DIR / "requirements-torch-cu118.lock"
        torch_input = SKILL_DIR / "requirements-torch-cu118.txt"
        lock_contract = SKILL_DIR / "requirements-lock-contract.json"
        training_pins = parse_hashed_lock(training_lock)
        torch_pins = parse_hashed_lock(torch_lock)

        self.assertNotIn("torch", training_pins)
        self.assertEqual(torch_pins, {"torch": "2.7.1+cu118"})
        self.assertFalse(set(training_pins) & set(torch_pins))
        self.assertTrue(
            any(
                "--no-deps" in line
                for line in torch_lock.read_text(encoding="utf-8").splitlines()
                if line.startswith("#")
            )
        )
        self.assertEqual(
            [
                line
                for line in torch_input.read_text(encoding="utf-8").splitlines()
                if line and not line.startswith("#")
            ],
            [
                "--index-url https://download.pytorch.org/whl/cu118",
                "torch==2.7.1+cu118",
            ],
        )
        self.assertEqual(
            {name: training_pins[name] for name in [
                "filelock",
                "fsspec",
                "jinja2",
                "networkx",
                "setuptools",
                "sympy",
                "typing-extensions",
            ]},
            {
                "filelock": "3.29.0",
                "fsspec": "2026.4.0",
                "jinja2": "3.1.6",
                "networkx": "3.6.1",
                "setuptools": "78.1.0",
                "sympy": "1.14.0",
                "typing-extensions": "4.15.0",
            },
        )
        contract = json.loads(lock_contract.read_text(encoding="utf-8"))
        self.assertEqual(
            contract["schema_version"],
            "kronos-dependency-lock-contract-v1",
        )
        for section, input_path, locked_path, pins in [
            ("training", SKILL_DIR / "requirements-training.in", training_lock, training_pins),
            ("torch_cu118", torch_input, torch_lock, torch_pins),
        ]:
            with self.subTest(lock_contract_section=section):
                declared = contract[section]
                self.assertEqual(
                    declared["input_sha256"],
                    hashlib.sha256(input_path.read_bytes()).hexdigest(),
                )
                self.assertEqual(
                    declared["lock_sha256"],
                    hashlib.sha256(locked_path.read_bytes()).hexdigest(),
                )
                self.assertEqual(declared["package_count"], len(pins))

    def test_rebuild_preflights_checks_and_hashes_exact_manifest(self) -> None:
        script = (
            SKILL_DIR / "scripts" / "rebuild_kronos_envs.ps1"
        ).read_text(encoding="utf-8")
        for needle in [
            "function Assert-LockConsistency",
            "requirements-lock-contract.json",
            "training input/lock contract drifted",
            "$lockContract = Assert-LockConsistency",
            "'pip', 'check', '--python', $python",
            "'--no-deps', '--require-hashes'",
            "function Assert-InstalledPackages",
            "kronos-package-manifest.json",
            "kronos-package-manifest.sha256",
            "kronos-environment-packages-v1",
            "runtime_observation = $RuntimeObservation",
            "& $python -I -B -c $validation",
            "& $PythonPath -I -B -c $inventoryScript",
            "Get-Sha256 $manifestPath",
            "Move-Item -LiteralPath $Backup -Destination $Destination",
            "cleanup_status = $cleanupStatus",
            "status = $finalStatus",
        ]:
            with self.subTest(needle=needle):
                self.assertIn(needle, script)
        self.assertLess(
            script.index("$lockContract = Assert-LockConsistency"),
            script.index("$packageManifests += Rebuild-Venv"),
        )
        commit = script.index("# Commit boundary:")
        cleanup = script.index("Remove-Item -LiteralPath $Backup -Recurse -Force", commit)
        rollback = script.index("Move-Item -LiteralPath $Backup -Destination $Destination")
        self.assertLess(rollback, commit)
        self.assertLess(commit, cleanup)
        self.assertNotIn(
            "Remove-Item -LiteralPath $Destination -Recurse -Force",
            script[commit:],
        )

    def test_rebuild_holds_a_machine_named_mutex_before_main_mutations(self) -> None:
        script = (
            SKILL_DIR / "scripts" / "rebuild_kronos_envs.ps1"
        ).read_text(encoding="utf-8")
        for needle in [
            "$RebuildMutexName = 'Global\\KronosAshareEnvironmentRebuild'",
            "$RebuildMutex.WaitOne(0)",
            "catch [System.Threading.AbandonedMutexException]",
            "another Kronos environment rebuild is already running on this machine",
            "$RebuildMutex.ReleaseMutex()",
            "$RebuildMutex.Dispose()",
        ]:
            with self.subTest(needle=needle):
                self.assertIn(needle, script)

        main = script[script.index("$RebuildMutexName ="):]
        acquire = main.index("$RebuildMutex.WaitOne(0)")
        conflict = main.index("if (-not $RebuildMutexAcquired)")
        backup_preflight = main.index("foreach ($backup in @($ProjectBackup, $TrainingBackup))")
        first_rebuild = main.index("$packageManifests += Rebuild-Venv")
        release = main.index("$RebuildMutex.ReleaseMutex()")
        dispose = main.index("$RebuildMutex.Dispose()")
        self.assertLess(acquire, conflict)
        self.assertLess(conflict, backup_preflight)
        self.assertLess(backup_preflight, first_rebuild)
        self.assertLess(first_rebuild, release)
        self.assertLess(release, dispose)

    @unittest.skipUnless(shutil.which("powershell"), "Windows PowerShell is required")
    def test_machine_named_mutex_conflict_fails_before_mutation_boundary(self) -> None:
        rebuild_path = SKILL_DIR / "scripts" / "rebuild_kronos_envs.ps1"
        raw = rebuild_path.read_text(encoding="utf-8")
        start = raw.index("$RebuildMutexName =")
        end = raw.index("foreach ($required in @(", start)
        child = raw[start:end] + r"""
throw 'MUTATION_BOUNDARY_REACHED'
}
finally {
    if ($RebuildMutexAcquired) {
        $RebuildMutex.ReleaseMutex()
    }
    $RebuildMutex.Dispose()
}
"""
        holder = r"""
$ErrorActionPreference = 'Stop'
$mutex = New-Object System.Threading.Mutex(
    $false,
    'Global\KronosAshareEnvironmentRebuild'
)
$acquired = $false
try {
    $acquired = $mutex.WaitOne(0)
    if (-not $acquired) {
        throw 'test could not acquire rebuild mutex'
    }
    $previousErrorAction = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(
            & powershell -NoProfile -ExecutionPolicy Bypass -File '__CHILD__' 2>&1
        )
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }
    [pscustomobject]@{
        exit_code = $exitCode
        output = @($output | ForEach-Object { [string]$_ })
    } | ConvertTo-Json -Depth 4 -Compress
}
finally {
    if ($acquired) {
        $mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}
"""
        runtime_temp = ROOT / "_training" / "kronos_ashare" / "runtime" / "tmp"
        runtime_temp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="mutex-contract-", dir=runtime_temp) as temp_dir:
            temp_path = Path(temp_dir)
            child_path = temp_path / "mutex_child.ps1"
            holder_path = temp_path / "mutex_holder.ps1"
            child_path.write_text(child, encoding="utf-8-sig")
            holder_path.write_text(
                holder.replace("__CHILD__", str(child_path).replace("'", "''")),
                encoding="utf-8-sig",
            )
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(holder_path),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        payload_lines = [
            line for line in completed.stdout.splitlines() if line.startswith("{")
        ]
        self.assertTrue(payload_lines, repr(completed.stdout) + repr(completed.stderr))
        payload = json.loads(payload_lines[-1])
        self.assertNotEqual(payload["exit_code"], 0)
        output = "\n".join(payload["output"])
        self.assertIn(
            "another Kronos environment rebuild is already running on this machine",
            output,
        )
        self.assertNotIn("MUTATION_BOUNDARY_REACHED", output)

    @unittest.skipUnless(shutil.which("powershell"), "Windows PowerShell is required")
    def test_partial_backup_cleanup_failure_preserves_committed_environment(self) -> None:
        rebuild_path = SKILL_DIR / "scripts" / "rebuild_kronos_envs.ps1"
        powershell = r"""
$ErrorActionPreference = 'Stop'
$scriptPath = '__SCRIPT_PATH__'
$scriptDir = Split-Path -Parent $scriptPath
$raw = Get-Content -LiteralPath $scriptPath -Raw -Encoding UTF8
$offset = $raw.IndexOf('$RebuildMutexName =', [StringComparison]::Ordinal)
$quotedDir = "'" + $scriptDir.Replace("'", "''") + "'"
$prefix = $raw.Substring(0, $offset).Replace('$PSScriptRoot', $quotedDir)
. ([scriptblock]::Create($prefix))
$tempRoot = Join-Path '__TEMP_ROOT__' ('cleanup-fault-' + [guid]::NewGuid().ToString('N'))
$destination = Join-Path $tempRoot 'destination'
$backup = Join-Path $tempRoot 'backup'
New-Item -ItemType Directory -Path $destination -Force | Out-Null
Set-Content -LiteralPath (Join-Path $destination 'old.txt') -Value old -Encoding UTF8
$script:FaultBackup = $backup
function Invoke-Uv {
    param([string[]]$Arguments)
    if ($Arguments[0] -eq 'venv') {
        New-Item -ItemType Directory -Path $Arguments[-1] -Force | Out-Null
    }
}
function Test-Venv { param([string]$VenvPath); [pscustomobject]@{ prefix = $VenvPath } }
function Write-PackageManifest {
    param([string]$Role, [string]$VenvPath, $LockContract, $RuntimeObservation)
    [pscustomobject]@{ role = $Role; path = 'manifest'; sha256 = 'abc'; package_count = 1 }
}
function Remove-Item {
    param([string]$LiteralPath, [switch]$Recurse, [switch]$Force)
    if ((Get-NormalizedPath $LiteralPath) -eq (Get-NormalizedPath $script:FaultBackup)) {
        Microsoft.PowerShell.Management\Remove-Item `
            -LiteralPath (Join-Path $LiteralPath 'old.txt') -Force
        throw 'injected_partial_cleanup_failure'
    }
    Microsoft.PowerShell.Management\Remove-Item `
        -LiteralPath $LiteralPath -Recurse:$Recurse -Force:$Force
}
try {
    $record = Rebuild-Venv -Role test -Destination $destination -Backup $backup `
        -ExpectedDestination $destination -ExpectedBackup $backup `
        -LockContract ([pscustomobject]@{})
    [pscustomobject]@{
        cleanup_status = $record.cleanup_status
        destination_exists = Test-Path -LiteralPath $destination
        backup_exists = Test-Path -LiteralPath $backup
    } | ConvertTo-Json -Compress
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Microsoft.PowerShell.Management\Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
"""
        powershell = powershell.replace(
            "__SCRIPT_PATH__", str(rebuild_path).replace("'", "''")
        ).replace(
            "__TEMP_ROOT__",
            str(ROOT / "_training" / "kronos_ashare" / "runtime" / "tmp").replace("'", "''"),
        )
        runtime_temp = ROOT / "_training" / "kronos_ashare" / "runtime" / "tmp"
        runtime_temp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="env-contract-", dir=runtime_temp) as temp_dir:
            test_script = Path(temp_dir) / "cleanup_failure.ps1"
            test_script.write_text(powershell, encoding="utf-8-sig")
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(test_script),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        payload_lines = [
            line for line in completed.stdout.splitlines() if line.startswith("{")
        ]
        self.assertTrue(payload_lines, repr(completed.stdout) + repr(completed.stderr))
        payload_line = payload_lines[-1]
        payload = json.loads(payload_line)
        self.assertEqual(payload["cleanup_status"], "cleanup_pending")
        self.assertTrue(payload["destination_exists"])
        self.assertTrue(payload["backup_exists"])

    def test_a_share_commands_use_training_venv_and_base_keeps_project_venv(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        fine_tuning = (
            SKILL_DIR / "references" / "a-share-finetuning.md"
        ).read_text(encoding="utf-8")
        usage = (
            SKILL_DIR / "references" / "usage-and-capabilities.md"
        ).read_text(encoding="utf-8")

        for text in [skill, fine_tuning, usage]:
            self.assertIn(TRAINING_PYTHON, text)
            self.assertIn(r".venv_kronos\Scripts\python.exe", text)
        command_lines = [
            line.strip()
            for line in fine_tuning.splitlines()
            if line.strip().startswith("& $AsharePython $AshareCli ")
        ]
        self.assertEqual(len(command_lines), 9)
        self.assertEqual(
            {line.split()[3] for line in command_lines},
            EXPECTED_A_SHARE_COMMANDS,
        )
        self.assertNotIn(".venv_kronos\\Scripts\\python.exe $AshareCli", fine_tuning)


if __name__ == "__main__":
    unittest.main()
