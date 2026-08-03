[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$TrainingRoot = Join-Path $ProjectRoot '_training\kronos_ashare'
$RuntimeRoot = Join-Path $TrainingRoot 'runtime'
$UvCache = Join-Path $RuntimeRoot 'uv-cache'
$UvPython = Join-Path $RuntimeRoot 'uv-python'
$PipCache = Join-Path $RuntimeRoot 'pip-cache'
$TaskTemp = Join-Path $RuntimeRoot 'tmp'
$BasePython = Join-Path $UvPython 'cpython-3.12.13-windows-x86_64-none\python.exe'
$ProjectVenv = Join-Path $ProjectRoot '.venv_kronos'
$ProjectBackup = Join-Path $ProjectRoot '.venv_kronos.pre-d-migration-backup'
$TrainingVenvRoot = Join-Path $RuntimeRoot 'venvs'
$TrainingVenv = Join-Path $TrainingVenvRoot 'kronos-ashare'
$TrainingBackup = Join-Path $TrainingVenvRoot 'kronos-ashare.rebuild-backup'
$ModelTrainingLock = Join-Path $TrainingRoot 'registry\.model-training.lock'
$TrainingInput = Join-Path $PSScriptRoot '..\requirements-training.in'
$TorchInput = Join-Path $PSScriptRoot '..\requirements-torch-cu118.txt'
$TrainingLock = Join-Path $PSScriptRoot '..\requirements-training.lock'
$TorchLock = Join-Path $PSScriptRoot '..\requirements-torch-cu118.lock'
$DependencyLockContract = Join-Path $PSScriptRoot '..\requirements-lock-contract.json'
$ExpectedTorchVersion = '2.7.1+cu118'
$PackageManifestName = 'kronos-package-manifest.json'
$PackageManifestHashName = 'kronos-package-manifest.sha256'

function Get-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    return [System.IO.Path]::GetFullPath($LiteralPath).TrimEnd([char]'\')
}

function Assert-ExactPath {
    param(
        [Parameter(Mandatory = $true)][string]$Actual,
        [Parameter(Mandatory = $true)][string]$Expected,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if (-not (Get-NormalizedPath $Actual).Equals(
        (Get-NormalizedPath $Expected),
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "$Label path contract failed: $Actual"
    }
}

function Get-NormalizedPackageName {
    param([Parameter(Mandatory = $true)][string]$Name)
    return ($Name.ToLowerInvariant() -replace '[-_.]+', '-')
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    return (Get-FileHash -LiteralPath $LiteralPath -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-VenvNotInUse {
    $targets = @(
        (Join-Path $ProjectVenv 'Scripts\python.exe'),
        (Join-Path $TrainingVenv 'Scripts\python.exe')
    ) | ForEach-Object { Get-NormalizedPath $_ }
    try {
        $pythonProcesses = @(Get-CimInstance Win32_Process -Filter (
            "Name='python.exe' OR Name='pythonw.exe'"
        ))
    }
    catch {
        throw "cannot prove Kronos venvs are idle; process inspection failed: $($_.Exception.Message)"
    }
    foreach ($process in $pythonProcesses) {
        $executable = [string]$process.ExecutablePath
        if ([string]::IsNullOrWhiteSpace($executable)) {
            continue
        }
        $normalized = Get-NormalizedPath $executable
        if ($targets -contains $normalized) {
            throw "Kronos venv is in use by PID $($process.ProcessId): $normalized"
        }
    }
}

function Enter-ModelTrainingMaintenanceLock {
    $parent = Split-Path -Parent $ModelTrainingLock
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $stream = [System.IO.File]::Open(
        $ModelTrainingLock,
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::ReadWrite
    )
    try {
        if ($stream.Length -eq 0) {
            $stream.WriteByte(0)
            $stream.Flush($true)
        }
        $stream.Lock(0, 1)
        return $stream
    }
    catch {
        $stream.Dispose()
        throw 'model training, scoring, or baseline generation is active; environment rebuild refused'
    }
}

function Get-LockPins {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $pins = @{}
    $currentPackage = $null
    $currentHashCount = 0
    foreach ($line in Get-Content -LiteralPath $LiteralPath -Encoding UTF8) {
        if ($line -match '^([A-Za-z0-9][A-Za-z0-9_.-]*(?:\[[^\]]+\])?)==([^\s\\;]+)') {
            if ($null -ne $currentPackage -and $currentHashCount -eq 0) {
                throw "lock pin has no SHA256 hash: $LiteralPath -> $currentPackage"
            }
            $name = Get-NormalizedPackageName (($Matches[1]) -replace '\[.*$', '')
            $version = [string]$Matches[2]
            if ($pins.ContainsKey($name)) {
                throw "duplicate package pin in lock: $LiteralPath -> $name"
            }
            $pins[$name] = $version
            $currentPackage = $name
            $currentHashCount = ([regex]::Matches(
                $line,
                '--hash=sha256:[0-9a-f]{64}'
            )).Count
        }
        elseif ($null -ne $currentPackage) {
            $currentHashCount += ([regex]::Matches(
                $line,
                '--hash=sha256:[0-9a-f]{64}'
            )).Count
        }
    }
    if ($pins.Count -eq 0) {
        throw "lock contains no exact package pins: $LiteralPath"
    }
    if ($currentHashCount -eq 0) {
        throw "lock pin has no SHA256 hash: $LiteralPath -> $currentPackage"
    }
    return $pins
}

function Assert-LockConsistency {
    $trainingPins = Get-LockPins $TrainingLock
    $torchPins = Get-LockPins $TorchLock
    if ($trainingPins.ContainsKey('torch')) {
        throw 'requirements-training.lock must not contain torch'
    }
    if ($torchPins.Count -ne 1 -or
        -not $torchPins.ContainsKey('torch') -or
        $torchPins['torch'] -ne $ExpectedTorchVersion) {
        throw "CU118 lock must contain only torch==$ExpectedTorchVersion"
    }
    $overlap = @($trainingPins.Keys | Where-Object { $torchPins.ContainsKey($_) })
    if ($overlap.Count -ne 0) {
        throw "training and CU118 locks must be disjoint: $($overlap -join ', ')"
    }
    $torchInputLines = @(
        Get-Content -LiteralPath $TorchInput -Encoding UTF8 |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and -not $_.StartsWith('#') }
    )
    if ($torchInputLines.Count -ne 2 -or
        $torchInputLines[0] -ne '--index-url https://download.pytorch.org/whl/cu118' -or
        $torchInputLines[1] -ne "torch==$ExpectedTorchVersion") {
        throw 'requirements-torch-cu118.txt must pin the official CU118 index and exact wheel'
    }
    try {
        $declaredContract = Get-Content `
            -LiteralPath $DependencyLockContract `
            -Raw `
            -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        throw "dependency lock contract is not valid JSON: $DependencyLockContract"
    }
    $trainingInputHash = Get-Sha256 $TrainingInput
    $torchInputHash = Get-Sha256 $TorchInput
    $trainingLockHash = Get-Sha256 $TrainingLock
    $torchLockHash = Get-Sha256 $TorchLock
    if ([string]$declaredContract.schema_version -ne 'kronos-dependency-lock-contract-v1') {
        throw 'dependency lock contract schema mismatch'
    }
    if ([string]$declaredContract.training.input -ne 'requirements-training.in' -or
        [string]$declaredContract.training.lock -ne 'requirements-training.lock' -or
        [string]$declaredContract.training.index_url -ne 'https://pypi.org/simple' -or
        [string]$declaredContract.training.input_sha256 -ne $trainingInputHash -or
        [string]$declaredContract.training.lock_sha256 -ne $trainingLockHash -or
        [int]$declaredContract.training.package_count -ne $trainingPins.Count) {
        throw 'training input/lock contract drifted; regenerate the lock and contract together'
    }
    if ([string]$declaredContract.torch_cu118.input -ne 'requirements-torch-cu118.txt' -or
        [string]$declaredContract.torch_cu118.lock -ne 'requirements-torch-cu118.lock' -or
        [string]$declaredContract.torch_cu118.index_url -ne 'https://download.pytorch.org/whl/cu118' -or
        [string]$declaredContract.torch_cu118.expected_torch -ne $ExpectedTorchVersion -or
        [bool]$declaredContract.torch_cu118.no_deps -ne $true -or
        [string]$declaredContract.torch_cu118.input_sha256 -ne $torchInputHash -or
        [string]$declaredContract.torch_cu118.lock_sha256 -ne $torchLockHash -or
        [int]$declaredContract.torch_cu118.package_count -ne $torchPins.Count) {
        throw 'CU118 input/lock contract drifted; regenerate the lock and contract together'
    }
    $combinedPins = @{}
    foreach ($name in $trainingPins.Keys) {
        $combinedPins[$name] = $trainingPins[$name]
    }
    foreach ($name in $torchPins.Keys) {
        $combinedPins[$name] = $torchPins[$name]
    }
    return [pscustomobject]@{
        training_pins = $trainingPins
        torch_pins = $torchPins
        combined_pins = $combinedPins
        training_input_sha256 = $trainingInputHash
        training_lock_sha256 = $trainingLockHash
        torch_input_sha256 = $torchInputHash
        torch_lock_sha256 = $torchLockHash
        dependency_contract_sha256 = Get-Sha256 $DependencyLockContract
    }
}

function Invoke-Uv {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    $previousErrorAction = $ErrorActionPreference
    try {
        # Windows PowerShell wraps native stderr as ErrorRecord. uv writes normal
        # progress to stderr, so capture it without turning a successful run into
        # a terminating PowerShell error; the native exit code remains decisive.
        $ErrorActionPreference = 'Continue'
        $output = @(& uv @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }
    foreach ($line in $output) {
        Write-Host ([string]$line)
    }
    if ($exitCode -ne 0) {
        throw "uv failed with exit code ${exitCode}: $($Arguments -join ' ')"
    }
}

function Test-Venv {
    param([Parameter(Mandatory = $true)][string]$VenvPath)
    $python = Join-Path $VenvPath 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw "venv python is missing: $python"
    }
    $validation = @'
import json
import os
from pathlib import Path
import sys
import tempfile
import torch
import numpy
import pandas
import yaml
import qlib
import lightgbm
import baostock
import pytest

expected_base = Path(os.environ['KRONOS_EXPECTED_BASE']).resolve()
actual_base = Path(sys.base_prefix).resolve()
if actual_base != expected_base and expected_base not in actual_base.parents:
    raise SystemExit(f'base_prefix_outside_d_drive: {sys.base_prefix}')
expected_venv = Path(os.environ['KRONOS_EXPECTED_VENV']).resolve()
actual_venv = Path(sys.prefix).resolve()
if actual_venv != expected_venv:
    raise SystemExit(f'unexpected_sys_prefix: {sys.prefix}')
expected_paths = json.loads(os.environ['KRONOS_EXPECTED_RUNTIME_PATHS'])
observed_paths = {name: os.environ.get(name) for name in expected_paths}
for name, expected in expected_paths.items():
    actual = observed_paths[name]
    if actual is None or Path(actual).resolve() != Path(expected).resolve():
        raise SystemExit(f'unexpected_runtime_path:{name}:{actual}')
actual_temp = Path(tempfile.gettempdir()).resolve()
expected_temp = Path(expected_paths['TEMP']).resolve()
if actual_temp != expected_temp:
    raise SystemExit(f'temp_outside_runtime:{actual_temp}')
if torch.__version__ != os.environ['KRONOS_EXPECTED_TORCH']:
    raise SystemExit(f'unexpected_torch: {torch.__version__}')
observation = {
    'prefix': sys.prefix,
    'base_prefix': sys.base_prefix,
    'temp_dir': str(actual_temp),
    'environment_paths': observed_paths,
    'torch': torch.__version__,
    'torch_cuda_build': torch.version.cuda,
    'numpy': numpy.__version__,
    'pandas': pandas.__version__,
}
print('KRONOS_RUNTIME_OBSERVATION=' + json.dumps(
    observation,
    ensure_ascii=True,
    separators=(',', ':'),
))
'@
    $previousErrorAction = $ErrorActionPreference
    $previousExpectedVenv = [Environment]::GetEnvironmentVariable(
        'KRONOS_EXPECTED_VENV',
        'Process'
    )
    try {
        [Environment]::SetEnvironmentVariable(
            'KRONOS_EXPECTED_VENV',
            (Get-NormalizedPath $VenvPath),
            'Process'
        )
        $ErrorActionPreference = 'Continue'
        $output = @(& $python -I -B -c $validation 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
        [Environment]::SetEnvironmentVariable(
            'KRONOS_EXPECTED_VENV',
            $previousExpectedVenv,
            'Process'
        )
    }
    foreach ($line in $output) {
        Write-Host ([string]$line)
    }
    if ($exitCode -ne 0) {
        throw "venv validation failed: $VenvPath"
    }
    $observationPrefix = 'KRONOS_RUNTIME_OBSERVATION='
    $observationLine = @(
        $output | Where-Object {
            ([string]$_).StartsWith($observationPrefix)
        }
    ) | Select-Object -Last 1
    if ($null -eq $observationLine) {
        throw "venv validation did not return runtime observation: $VenvPath"
    }
    try {
        return ([string]$observationLine).Substring($observationPrefix.Length) |
            ConvertFrom-Json
    }
    catch {
        throw "venv runtime observation is not valid JSON: $VenvPath"
    }
}

function Get-InstalledPackages {
    param([Parameter(Mandatory = $true)][string]$PythonPath)

    $inventoryScript = @'
import importlib.metadata as metadata
import json
import re

packages = {}
for distribution in metadata.distributions():
    raw_name = distribution.metadata.get('Name')
    if not raw_name:
        raise SystemExit('installed_distribution_without_name')
    name = re.sub(r'[-_.]+', '-', raw_name).lower()
    if name in packages:
        raise SystemExit(f'duplicate_installed_distribution:{name}')
    packages[name] = distribution.version
print(json.dumps([
    {'name': name, 'version': packages[name]}
    for name in sorted(packages)
], ensure_ascii=False, separators=(',', ':')))
'@
    $previousErrorAction = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& $PythonPath -I -B -c $inventoryScript 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }
    if ($exitCode -ne 0) {
        foreach ($line in $output) {
            Write-Host $line
        }
        throw "package inventory failed: $PythonPath"
    }
    try {
        return @((($output -join [Environment]::NewLine) | ConvertFrom-Json))
    }
    catch {
        throw "package inventory is not valid JSON: $PythonPath"
    }
}

function Assert-InstalledPackages {
    param(
        [Parameter(Mandatory = $true)]$Packages,
        [Parameter(Mandatory = $true)]$ExpectedPins
    )

    $observed = @{}
    foreach ($package in @($Packages)) {
        $name = Get-NormalizedPackageName ([string]$package.name)
        if ($observed.ContainsKey($name)) {
            throw "duplicate installed package after normalization: $name"
        }
        $observed[$name] = [string]$package.version
    }
    if ($observed.Count -ne $ExpectedPins.Count) {
        throw "installed package count differs from combined locks: " +
            "installed=$($observed.Count), locked=$($ExpectedPins.Count)"
    }
    foreach ($name in $ExpectedPins.Keys) {
        if (-not $observed.ContainsKey($name)) {
            throw "locked package is missing from environment: $name"
        }
        if ($observed[$name] -ne $ExpectedPins[$name]) {
            throw "installed package version mismatch: $name expected=$($ExpectedPins[$name]) " +
                "actual=$($observed[$name])"
        }
    }
    foreach ($name in $observed.Keys) {
        if (-not $ExpectedPins.ContainsKey($name)) {
            throw "environment contains package absent from locks: $name"
        }
    }
}

function Write-Utf8Atomic {
    param(
        [Parameter(Mandatory = $true)][string]$LiteralPath,
        [Parameter(Mandatory = $true)][string]$Content
    )

    $temporary = "$LiteralPath.$PID.$([guid]::NewGuid().ToString('N')).tmp"
    $encoding = New-Object System.Text.UTF8Encoding($false)
    try {
        [System.IO.File]::WriteAllText($temporary, $Content, $encoding)
        Move-Item -LiteralPath $temporary -Destination $LiteralPath -Force
    }
    finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force
        }
    }
}

function Write-PackageManifest {
    param(
        [Parameter(Mandatory = $true)][string]$Role,
        [Parameter(Mandatory = $true)][string]$VenvPath,
        [Parameter(Mandatory = $true)]$LockContract,
        [Parameter(Mandatory = $true)]$RuntimeObservation
    )

    $python = Join-Path $VenvPath 'Scripts\python.exe'
    $packages = @(Get-InstalledPackages -PythonPath $python)
    Assert-InstalledPackages `
        -Packages $packages `
        -ExpectedPins $LockContract.combined_pins
    $manifestPath = Join-Path $VenvPath $PackageManifestName
    $hashPath = Join-Path $VenvPath $PackageManifestHashName
    $manifest = [ordered]@{
        schema_version = 'kronos-environment-packages-v1'
        role = $Role
        generated_at_utc = [DateTime]::UtcNow.ToString('o')
        venv = Get-NormalizedPath $VenvPath
        python = Get-NormalizedPath $python
        base_python_root = Get-NormalizedPath $UvPython
        locks = [ordered]@{
            contract = [ordered]@{
                path = (Resolve-Path -LiteralPath $DependencyLockContract).Path
                sha256 = $LockContract.dependency_contract_sha256
            }
            training = [ordered]@{
                input_path = (Resolve-Path -LiteralPath $TrainingInput).Path
                input_sha256 = $LockContract.training_input_sha256
                path = (Resolve-Path -LiteralPath $TrainingLock).Path
                sha256 = $LockContract.training_lock_sha256
                package_count = $LockContract.training_pins.Count
            }
            torch_cu118 = [ordered]@{
                input_path = (Resolve-Path -LiteralPath $TorchInput).Path
                input_sha256 = $LockContract.torch_input_sha256
                path = (Resolve-Path -LiteralPath $TorchLock).Path
                sha256 = $LockContract.torch_lock_sha256
                package_count = $LockContract.torch_pins.Count
            }
        }
        validation = [ordered]@{
            pip_check = 'passed'
            exact_package_set = $true
            torch = $ExpectedTorchVersion
            runtime_paths_observed = $true
        }
        runtime_observation = $RuntimeObservation
        package_count = $packages.Count
        packages = $packages
    }
    Write-Utf8Atomic `
        -LiteralPath $manifestPath `
        -Content (($manifest | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
    $manifestHash = Get-Sha256 $manifestPath
    Write-Utf8Atomic `
        -LiteralPath $hashPath `
        -Content ($manifestHash + '  ' + $PackageManifestName + [Environment]::NewLine)
    $recordedHash = ((Get-Content -LiteralPath $hashPath -Raw -Encoding UTF8) -split '\s+')[0]
    if ($recordedHash -ne $manifestHash -or (Get-Sha256 $manifestPath) -ne $manifestHash) {
        throw "package manifest hash verification failed: $manifestPath"
    }
    return [pscustomobject]@{
        role = $Role
        path = $manifestPath
        sha256 = $manifestHash
        package_count = $packages.Count
    }
}

function Rebuild-Venv {
    param(
        [Parameter(Mandatory = $true)][string]$Role,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][string]$Backup,
        [Parameter(Mandatory = $true)][string]$ExpectedDestination,
        [Parameter(Mandatory = $true)][string]$ExpectedBackup,
        [Parameter(Mandatory = $true)]$LockContract
    )
    Assert-ExactPath -Actual $Destination -Expected $ExpectedDestination -Label 'destination'
    Assert-ExactPath -Actual $Backup -Expected $ExpectedBackup -Label 'backup'
    if (Test-Path -LiteralPath $Backup) {
        throw "fixed venv backup already exists: $Backup"
    }
    $backupCreated = $false
    if (Test-Path -LiteralPath $Destination) {
        Move-Item -LiteralPath $Destination -Destination $Backup
        $backupCreated = $true
    }
    try {
        Invoke-Uv @('venv', '--python', $BasePython, '--no-python-downloads', $Destination)
        $python = Join-Path $Destination 'Scripts\python.exe'
        Invoke-Uv @(
            'pip', 'install', '--python', $python, '--require-hashes',
            '--default-index', 'https://pypi.org/simple', '-r', $TrainingLock
        )
        Invoke-Uv @(
            'pip', 'install', '--python', $python, '--no-deps', '--require-hashes',
            '--default-index', 'https://download.pytorch.org/whl/cu118', '-r', $TorchLock
        )
        Invoke-Uv @('pip', 'check', '--python', $python)
        $runtimeObservation = Test-Venv -VenvPath $Destination
        $packageManifest = Write-PackageManifest `
            -Role $Role `
            -VenvPath $Destination `
            -LockContract $LockContract `
            -RuntimeObservation $runtimeObservation
    }
    catch {
        if (Test-Path -LiteralPath $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }
        if ($backupCreated -and (Test-Path -LiteralPath $Backup)) {
            Move-Item -LiteralPath $Backup -Destination $Destination
        }
        throw
    }

    # Commit boundary: the new environment and its hashed manifest are valid.
    # Backup cleanup must never re-enter rollback, because Remove-Item can fail
    # after partially deleting the backup on Windows.
    $cleanupStatus = if ($backupCreated) { 'pending' } else { 'not_required' }
    $cleanupError = $null
    if ($backupCreated) {
        try {
            Remove-Item -LiteralPath $Backup -Recurse -Force
            $cleanupStatus = 'cleaned'
        }
        catch {
            if (Test-Path -LiteralPath $Backup) {
                $cleanupStatus = 'cleanup_pending'
                $cleanupError = $_.Exception.Message
                Write-Warning (
                    "validated environment retained; backup cleanup is pending: $Backup"
                )
            }
            else {
                $cleanupStatus = 'cleaned'
            }
        }
    }
    return [pscustomobject]@{
        role = $packageManifest.role
        path = $packageManifest.path
        sha256 = $packageManifest.sha256
        package_count = $packageManifest.package_count
        cleanup_status = $cleanupStatus
        backup_path = if ($cleanupStatus -eq 'cleanup_pending') { $Backup } else { $null }
        cleanup_error = $cleanupError
    }
}

$RebuildMutexName = 'Global\KronosAshareEnvironmentRebuild'
$RebuildMutex = New-Object System.Threading.Mutex($false, $RebuildMutexName)
$RebuildMutexAcquired = $false
$ModelTrainingLockStream = $null
$RebuildExitCode = 0
try {
    try {
        $RebuildMutexAcquired = $RebuildMutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        $RebuildMutexAcquired = $true
    }
    if (-not $RebuildMutexAcquired) {
        throw 'another Kronos environment rebuild is already running on this machine'
    }
    Assert-VenvNotInUse
    $ModelTrainingLockStream = Enter-ModelTrainingMaintenanceLock

foreach ($required in @(
    $UvCache, $UvPython, $PipCache, $TaskTemp, $TrainingInput,
    $TorchInput, $TrainingLock, $TorchLock, $DependencyLockContract,
    $BasePython
)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "required D-drive artifact is missing: $required"
    }
}
foreach ($backup in @($ProjectBackup, $TrainingBackup)) {
    if (Test-Path -LiteralPath $backup) {
        throw "fixed venv backup already exists; resolve it before rebuilding either environment: $backup"
    }
}
$lockContract = Assert-LockConsistency
New-Item -ItemType Directory -Path $TrainingVenvRoot -Force | Out-Null

$runtimePathContract = [ordered]@{
    UV_CACHE_DIR = $UvCache
    UV_PYTHON_INSTALL_DIR = $UvPython
    PIP_CACHE_DIR = $PipCache
    HF_HOME = Join-Path $RuntimeRoot 'huggingface'
    TORCH_HOME = Join-Path $RuntimeRoot 'torch'
    TEMP = $TaskTemp
    TMP = $TaskTemp
}
foreach ($path in @($runtimePathContract.Values | Select-Object -Unique)) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
}
foreach ($item in $runtimePathContract.GetEnumerator()) {
    [Environment]::SetEnvironmentVariable($item.Key, $item.Value, 'Process')
}
[Environment]::SetEnvironmentVariable('KRONOS_EXPECTED_BASE', $UvPython, 'Process')
[Environment]::SetEnvironmentVariable('KRONOS_EXPECTED_TORCH', $ExpectedTorchVersion, 'Process')
[Environment]::SetEnvironmentVariable(
    'KRONOS_EXPECTED_RUNTIME_PATHS',
    ($runtimePathContract | ConvertTo-Json -Compress),
    'Process'
)

$packageManifests = @()
$packageManifests += Rebuild-Venv `
    -Role 'base-inference' `
    -Destination $ProjectVenv `
    -Backup $ProjectBackup `
    -ExpectedDestination (Join-Path $ProjectRoot '.venv_kronos') `
    -ExpectedBackup (Join-Path $ProjectRoot '.venv_kronos.pre-d-migration-backup') `
    -LockContract $lockContract
$packageManifests += Rebuild-Venv `
    -Role 'a-share-training' `
    -Destination $TrainingVenv `
    -Backup $TrainingBackup `
    -ExpectedDestination (Join-Path $TrainingVenvRoot 'kronos-ashare') `
    -ExpectedBackup (Join-Path $TrainingVenvRoot 'kronos-ashare.rebuild-backup') `
    -LockContract $lockContract

$cleanupPending = @(
    $packageManifests | Where-Object { $_.cleanup_status -eq 'cleanup_pending' }
)
$finalStatus = if ($cleanupPending.Count -eq 0) { 'ok' } else { 'cleanup_pending' }
$result = [pscustomobject]@{
    status = $finalStatus
    project_venv = $ProjectVenv
    training_venv = $TrainingVenv
    base_python = $BasePython
    locks = [ordered]@{
        contract_sha256 = $lockContract.dependency_contract_sha256
        training_input_sha256 = $lockContract.training_input_sha256
        training_sha256 = $lockContract.training_lock_sha256
        torch_input_sha256 = $lockContract.torch_input_sha256
        torch_cu118_sha256 = $lockContract.torch_lock_sha256
        overlap_count = 0
    }
    package_manifests = $packageManifests
    caches = [ordered]@{
        uv = $UvCache
        pip = $PipCache
        temp = $TaskTemp
    }
}
$result | ConvertTo-Json -Depth 6
if ($finalStatus -eq 'cleanup_pending') {
    $RebuildExitCode = 2
}
}
finally {
    if ($null -ne $ModelTrainingLockStream) {
        try {
            $ModelTrainingLockStream.Unlock(0, 1)
        }
        finally {
            $ModelTrainingLockStream.Dispose()
        }
    }
    if ($RebuildMutexAcquired) {
        $RebuildMutex.ReleaseMutex()
    }
    $RebuildMutex.Dispose()
}
if ($RebuildExitCode -ne 0) {
    exit $RebuildExitCode
}
