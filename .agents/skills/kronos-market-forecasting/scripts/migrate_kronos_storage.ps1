[CmdletBinding()]
param(
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$MigrationMutex = New-Object System.Threading.Mutex($false, 'Local\KronosAshareStorageMigration')
$MutexAcquired = $false
try {
    $MutexAcquired = $MigrationMutex.WaitOne(0)
}
catch [System.Threading.AbandonedMutexException] {
    $MutexAcquired = $true
}
if (-not $MutexAcquired) {
    throw '另一个 Kronos 存储迁移或审计进程正在运行'
}

$ExpectedUserProfile = 'C:\Users\Administrator'
$TrainingRoot = 'D:\vcp_hunter\产业链投研\_training\kronos_ashare'

$LayoutPaths = [ordered]@{
    Runtime = Join-Path $TrainingRoot 'runtime'
    UvCache = Join-Path $TrainingRoot 'runtime\uv-cache'
    UvPython = Join-Path $TrainingRoot 'runtime\uv-python'
    PipCache = Join-Path $TrainingRoot 'runtime\pip-cache'
    Venvs = Join-Path $TrainingRoot 'runtime\venvs'
    HuggingFace = Join-Path $TrainingRoot 'runtime\huggingface'
    Torch = Join-Path $TrainingRoot 'runtime\torch'
    Temp = Join-Path $TrainingRoot 'runtime\tmp'
    Data = Join-Path $TrainingRoot 'data'
    Runs = Join-Path $TrainingRoot 'runs'
    Registry = Join-Path $TrainingRoot 'registry'
}

$MigrationSpecs = @(
    [pscustomobject]@{
        Name = 'uv-cache'
        Source = 'C:\Users\Administrator\AppData\Local\uv\cache'
        Target = $LayoutPaths.UvCache
        Backup = 'C:\Users\Administrator\AppData\Local\uv\cache.kronos-storage-backup'
        EnvironmentName = 'UV_CACHE_DIR'
        VerifyCommand = 'uv-cache'
    },
    [pscustomobject]@{
        Name = 'pip-cache'
        Source = 'C:\Users\Administrator\AppData\Local\pip\cache'
        Target = $LayoutPaths.PipCache
        Backup = 'C:\Users\Administrator\AppData\Local\pip\cache.kronos-storage-backup'
        EnvironmentName = 'PIP_CACHE_DIR'
        VerifyCommand = 'pip-cache'
    },
    [pscustomobject]@{
        Name = 'uv-python'
        Source = 'C:\Users\Administrator\AppData\Roaming\uv\python'
        Target = $LayoutPaths.UvPython
        Backup = 'C:\Users\Administrator\AppData\Roaming\uv\python.kronos-storage-backup'
        EnvironmentName = 'UV_PYTHON_INSTALL_DIR'
        VerifyCommand = 'uv-python'
    }
)

# These paths are deliberately outside this migration contract.
$ExcludedPaths = @(
    'C:\Users\Administrator\.cache\huggingface\token',
    'C:\Users\Administrator\AppData\Local\huggingface\token',
    'C:\Users\Administrator\AppData\Roaming\huggingface\token',
    'C:\Users\Administrator\AppData\Roaming\uv\tools',
    'C:\Python314',
    'C:\Users\Administrator\AppData\Roaming\Python'
)


function Get-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $full = [System.IO.Path]::GetFullPath($LiteralPath)
    if ($full.Length -gt 3) {
        return $full.TrimEnd([char]'\')
    }
    return $full
}


function Test-PathWithin {
    param(
        [Parameter(Mandatory = $true)][string]$Candidate,
        [Parameter(Mandatory = $true)][string]$Root,
        [switch]$AllowEqual
    )

    $candidateFull = Get-NormalizedPath $Candidate
    $rootFull = Get-NormalizedPath $Root
    if ($AllowEqual -and $candidateFull.Equals($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }
    return $candidateFull.StartsWith(
        $rootFull + '\',
        [System.StringComparison]::OrdinalIgnoreCase
    )
}


function Assert-ExpectedMachine {
    $actualProfile = Get-NormalizedPath $env:USERPROFILE
    $expectedProfile = Get-NormalizedPath $ExpectedUserProfile
    if (-not $actualProfile.Equals($expectedProfile, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "用户目录与迁移合同不匹配：expected=$expectedProfile, actual=$actualProfile"
    }
    if (-not (Get-NormalizedPath $TrainingRoot).StartsWith('D:\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "训练根必须固定在 D 盘：$TrainingRoot"
    }
}


function Assert-NotExcluded {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $candidate = Get-NormalizedPath $LiteralPath
    foreach ($excludedPath in $ExcludedPaths) {
        $excluded = Get-NormalizedPath $excludedPath
        if ($candidate.Equals($excluded, [System.StringComparison]::OrdinalIgnoreCase) -or
            (Test-PathWithin -Candidate $candidate -Root $excluded)) {
            throw "迁移路径命中明确排除项：$candidate"
        }
    }
}


function Assert-NoReparseAncestors {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $current = Get-NormalizedPath $LiteralPath
    while (-not (Test-Path -LiteralPath $current)) {
        $parent = Split-Path -Parent $current
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
            throw "找不到可核验的路径祖先：$LiteralPath"
        }
        $current = $parent
    }
    while (-not [string]::IsNullOrWhiteSpace($current)) {
        $item = Get-Item -LiteralPath $current -Force
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "训练根或目标祖先不得是 reparse point：$current"
        }
        $parent = Split-Path -Parent $current
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
            break
        }
        $current = $parent
    }
}


function Assert-SpecPaths {
    param(
        [Parameter(Mandatory = $true)]$Spec,
        [string]$StagePath
    )

    $allowedSources = @($MigrationSpecs | ForEach-Object { Get-NormalizedPath $_.Source })
    $source = Get-NormalizedPath $Spec.Source
    if (-not ($allowedSources -contains $source)) {
        throw "来源不在精确迁移白名单：$source"
    }
    Assert-NotExcluded $source

    $target = Get-NormalizedPath $Spec.Target
    if (-not (Test-PathWithin -Candidate $target -Root $TrainingRoot)) {
        throw "目标越出统一训练根：$target"
    }

    $expectedBackup = Get-NormalizedPath ($Spec.Source + '.kronos-storage-backup')
    $backup = Get-NormalizedPath $Spec.Backup
    if (-not $backup.Equals($expectedBackup, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "备份路径不是精确来源的固定后缀：$backup"
    }
    Assert-NotExcluded $backup

    if ($StagePath) {
        $stage = Get-NormalizedPath $StagePath
        if (-not (Test-PathWithin -Candidate $stage -Root $LayoutPaths.Temp)) {
            throw "stage 越出 runtime\\tmp：$stage"
        }
    }
}


function Get-RelativeLiteralPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$File
    )

    $rootWithSeparator = (Get-NormalizedPath $Root) + '\'
    $rootUri = New-Object System.Uri($rootWithSeparator)
    $fileUri = New-Object System.Uri((Get-NormalizedPath $File))
    return [System.Uri]::UnescapeDataString(
        $rootUri.MakeRelativeUri($fileUri).ToString()
    ).Replace('/', '\')
}


function Get-JunctionTarget {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $item = Get-Item -LiteralPath $LiteralPath -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq 0) {
        return $null
    }
    $targets = @($item.Target)
    if ($targets.Count -ne 1 -or [string]::IsNullOrWhiteSpace([string]$targets[0])) {
        throw "无法唯一解析 junction 目标：$LiteralPath"
    }
    $target = [string]$targets[0]
    if (-not [System.IO.Path]::IsPathRooted($target)) {
        $target = Join-Path $item.Parent.FullName $target
    }
    return Get-NormalizedPath $target
}


function Get-DirectoryAudit {
    param([Parameter(Mandatory = $true)]$Spec)

    Assert-SpecPaths $Spec
    $sourceItem = Get-Item -LiteralPath $Spec.Source -Force -ErrorAction SilentlyContinue
    $sourceExists = $null -ne $sourceItem
    $targetExists = Test-Path -LiteralPath $Spec.Target
    $backupExists = Test-Path -LiteralPath $Spec.Backup
    $sourceKind = 'missing'
    $junctionTarget = $null
    if ($sourceExists) {
        if (-not $sourceItem.PSIsContainer) {
            $sourceKind = 'invalid_file'
        }
        elseif (($sourceItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            $sourceKind = 'junction'
            $junctionTarget = Get-JunctionTarget $Spec.Source
        }
        else {
            $sourceKind = 'directory'
        }
    }

    $targetNonempty = $false
    if ($targetExists) {
        $targetItem = Get-Item -LiteralPath $Spec.Target -Force
        if (-not $targetItem.PSIsContainer) {
            $targetNonempty = $true
        }
        else {
            $targetNonempty = $null -ne (
                Get-ChildItem -LiteralPath $Spec.Target -Force | Select-Object -First 1
            )
        }
    }

    return [ordered]@{
        name = $Spec.Name
        source = Get-NormalizedPath $Spec.Source
        source_exists = $sourceExists
        source_kind = $sourceKind
        junction_target = $junctionTarget
        target = Get-NormalizedPath $Spec.Target
        target_exists = $targetExists
        target_nonempty = $targetNonempty
        backup = Get-NormalizedPath $Spec.Backup
        backup_exists = $backupExists
        action = if ($backupExists) { 'blocked_backup_exists' }
                 elseif ($sourceKind -eq 'directory') { 'ready_to_migrate' }
                 elseif ($sourceKind -eq 'junction' -and $junctionTarget -and
                         $junctionTarget.Equals((Get-NormalizedPath $Spec.Target), [System.StringComparison]::OrdinalIgnoreCase)) {
                     'already_migrated'
                 }
                 elseif ($sourceKind -eq 'missing') { 'source_missing' }
                 else { 'blocked' }
    }
}


function Get-DirectoryPayloadStats {
    param([Parameter(Mandatory = $true)][string]$LiteralRoot)

    $root = Get-NormalizedPath $LiteralRoot
    $reparsePoints = @(
        Get-ChildItem -LiteralPath $root -Force -Recurse |
            Where-Object { ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 }
    )
    $fileCount = [int64]0
    $totalBytes = [int64]0
    foreach ($file in @(
        Get-ChildItem -LiteralPath $root -File -Force -Recurse |
            Where-Object {
                $candidate = $_.FullName
                -not ($reparsePoints | Where-Object {
                    Test-PathWithin -Candidate $candidate -Root $_.FullName
                })
            }
    )) {
        $fileCount += 1
        $totalBytes += [int64]$file.Length
    }
    return [ordered]@{
        file_count = $fileCount
        total_bytes = $totalBytes
    }
}


function Get-HashManifest {
    param(
        [Parameter(Mandatory = $true)][string]$LiteralRoot,
        [string]$RelocatedFromRoot
    )

    $root = Get-NormalizedPath $LiteralRoot
    $rootItem = Get-Item -LiteralPath $root -Force
    if (-not $rootItem.PSIsContainer) {
        throw "manifest 根不是目录：$root"
    }
    $nestedReparsePoints = @(
        Get-ChildItem -LiteralPath $root -Force -Recurse |
            Where-Object { ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 } |
            Sort-Object FullName
    )
    $junctionEntries = @()
    foreach ($junction in $nestedReparsePoints) {
        if (-not $junction.PSIsContainer -or $junction.LinkType -ne 'Junction') {
            throw "目录包含非 Junction 的嵌套 reparse point：$($junction.FullName)"
        }
        if (-not (Get-NormalizedPath $junction.Parent.FullName).Equals($root, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "只允许根目录直接子级的 uv 版本别名 Junction：$($junction.FullName)"
        }
        $target = Get-JunctionTarget $junction.FullName
        $targetRoot = $root
        if (-not (Test-PathWithin -Candidate $target -Root $root)) {
            if ([string]::IsNullOrWhiteSpace($RelocatedFromRoot) -or
                -not (Test-PathWithin -Candidate $target -Root $RelocatedFromRoot)) {
                throw "嵌套 Junction 目标越出允许根：$($junction.FullName) -> $target"
            }
            $targetRoot = Get-NormalizedPath $RelocatedFromRoot
        }
        $targetItem = Get-Item -LiteralPath $target -Force
        if (-not $targetItem.PSIsContainer -or
            ($targetItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "嵌套 Junction 必须指向根内真实目录：$($junction.FullName) -> $target"
        }
        $junctionEntries += [ordered]@{
            relative_path = Get-RelativeLiteralPath -Root $root -File $junction.FullName
            target_relative_path = Get-RelativeLiteralPath -Root $targetRoot -File $target
        }
    }

    $entries = @()
    $totalBytes = [int64]0
    $files = @(
        Get-ChildItem -LiteralPath $root -File -Force -Recurse |
            Where-Object {
                $candidate = $_.FullName
                -not ($nestedReparsePoints | Where-Object {
                    Test-PathWithin -Candidate $candidate -Root $_.FullName
                })
            } |
            Sort-Object FullName
    )
    foreach ($file in $files) {
        $hash = Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
        $relative = Get-RelativeLiteralPath -Root $root -File $file.FullName
        $entries += [ordered]@{
            relative_path = $relative
            length = [int64]$file.Length
            sha256 = $hash.Hash.ToLowerInvariant()
        }
        $totalBytes += [int64]$file.Length
    }
    return [ordered]@{
        root = $root
        file_count = $entries.Count
        total_bytes = $totalBytes
        files = $entries
        junction_count = $junctionEntries.Count
        junctions = $junctionEntries
    }
}


function Assert-ManifestsEqual {
    param(
        [Parameter(Mandatory = $true)]$Expected,
        [Parameter(Mandatory = $true)]$Actual,
        [Parameter(Mandatory = $true)][string]$Label,
        [switch]$IgnoreJunctions
    )

    if ([int64]$Expected.file_count -ne [int64]$Actual.file_count -or
        [int64]$Expected.total_bytes -ne [int64]$Actual.total_bytes) {
        throw "$Label 文件数量或总字节不一致"
    }
    for ($index = 0; $index -lt [int]$Expected.file_count; $index++) {
        $left = $Expected.files[$index]
        $right = $Actual.files[$index]
        if (-not ([string]$left.relative_path).Equals([string]$right.relative_path, [System.StringComparison]::OrdinalIgnoreCase) -or
            [int64]$left.length -ne [int64]$right.length -or
            -not ([string]$left.sha256).Equals([string]$right.sha256, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "$Label manifest 不一致：$($left.relative_path)"
        }
    }
    if ($IgnoreJunctions) {
        return
    }
    if ([int]$Expected.junction_count -ne [int]$Actual.junction_count) {
        throw "$Label Junction 数量不一致"
    }
    for ($index = 0; $index -lt [int]$Expected.junction_count; $index++) {
        $left = $Expected.junctions[$index]
        $right = $Actual.junctions[$index]
        if (-not ([string]$left.relative_path).Equals([string]$right.relative_path, [System.StringComparison]::OrdinalIgnoreCase) -or
            -not ([string]$left.target_relative_path).Equals([string]$right.target_relative_path, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "$Label Junction manifest 不一致：$($left.relative_path)"
        }
    }
}


function Write-JsonAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$LiteralPath,
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string]$OperationId
    )

    $destination = Get-NormalizedPath $LiteralPath
    if (-not (Test-PathWithin -Candidate $destination -Root $LayoutPaths.Registry)) {
        throw "迁移 JSON 必须写入 registry：$destination"
    }
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $temporary = $destination + '.' + $OperationId + '.tmp'
    if (-not (Test-PathWithin -Candidate $temporary -Root $LayoutPaths.Registry)) {
        throw "临时 JSON 越出 registry：$temporary"
    }
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        $temporary,
        (($Value | ConvertTo-Json -Depth 20) + [Environment]::NewLine),
        $encoding
    )
    Move-Item -LiteralPath $temporary -Destination $destination -Force
}


function Copy-DirectoryContents {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    foreach ($entry in @(Get-ChildItem -LiteralPath $Source -Force)) {
        if (($entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            continue
        }
        if ($entry.PSIsContainer) {
            $childDestination = Join-Path $Destination $entry.Name
            New-Item -ItemType Directory -Path $childDestination -Force | Out-Null
            Copy-DirectoryContents -Source $entry.FullName -Destination $childDestination
        }
        else {
            Copy-Item -LiteralPath $entry.FullName -Destination $Destination -Force
        }
    }
}


function Restore-InternalJunctions {
    param(
        [Parameter(Mandatory = $true)][string]$LiteralRoot,
        [Parameter(Mandatory = $true)]$Manifest
    )

    $root = Get-NormalizedPath $LiteralRoot
    foreach ($junction in @($Manifest.junctions)) {
        $linkPath = Join-Path $root ([string]$junction.relative_path)
        $targetPath = Join-Path $root ([string]$junction.target_relative_path)
        if (-not (Test-PathWithin -Candidate $linkPath -Root $root) -or
            -not (Test-PathWithin -Candidate $targetPath -Root $root)) {
            throw "拒绝重建越界的内部 Junction：$linkPath -> $targetPath"
        }
        if (Test-Path -LiteralPath $linkPath) {
            throw "内部 Junction 路径已存在：$linkPath"
        }
        $targetItem = Get-Item -LiteralPath $targetPath -Force
        if (-not $targetItem.PSIsContainer -or
            ($targetItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "内部 Junction 目标不是根内真实目录：$targetPath"
        }
        New-Item -ItemType Junction -Path $linkPath -Target $targetPath | Out-Null
    }
}


function Invoke-ToolVerification {
    param([Parameter(Mandatory = $true)]$Spec)

    $previous = [Environment]::GetEnvironmentVariable($Spec.EnvironmentName, 'Process')
    try {
        [Environment]::SetEnvironmentVariable(
            $Spec.EnvironmentName,
            (Get-NormalizedPath $Spec.Target),
            'Process'
        )
        switch ($Spec.VerifyCommand) {
            'uv-cache' {
                if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
                    throw '找不到 uv，无法完成 cache 功能验证'
                }
                $output = (& uv cache dir 2>&1 | Out-String).Trim()
            }
            'uv-python' {
                if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
                    throw '找不到 uv，无法完成 managed python 功能验证'
                }
                $output = (& uv python dir 2>&1 | Out-String).Trim()
            }
            'pip-cache' {
                if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
                    throw '找不到 python，无法完成 pip cache 功能验证'
                }
                $output = (& python -m pip cache dir 2>&1 | Out-String).Trim()
            }
            default {
                throw "未知功能验证类型：$($Spec.VerifyCommand)"
            }
        }
        if ($LASTEXITCODE -ne 0) {
            throw "功能验证命令失败：$($Spec.VerifyCommand): $output"
        }
        $actual = Get-NormalizedPath $output
        $expected = Get-NormalizedPath $Spec.Target
        if (-not $actual.Equals($expected, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "功能验证目录不匹配：expected=$expected, actual=$actual"
        }
    }
    finally {
        [Environment]::SetEnvironmentVariable($Spec.EnvironmentName, $previous, 'Process')
    }
}


function Assert-NoActiveMigrationClients {
    $sourceRoots = @($MigrationSpecs | ForEach-Object { Get-NormalizedPath $_.Source })
    $active = @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object {
                if ($_.ProcessName -match '^(uv|pip|pip3)([0-9.]*)$') {
                    return $true
                }
                if ($_.ProcessName -notmatch '^(python|pythonw)([0-9.]*)$') {
                    return $false
                }
                $loadedPaths = @()
                try {
                    if ($_.Path) {
                        $loadedPaths += Get-NormalizedPath $_.Path
                    }
                    $loadedPaths += @(
                        $_.Modules |
                            Where-Object { $_.FileName } |
                            ForEach-Object { Get-NormalizedPath $_.FileName }
                    )
                }
                catch {
                    # 无法证明与迁移源无关时按 fail-closed 处理。
                    return $true
                }
                foreach ($loadedPath in $loadedPaths) {
                    foreach ($sourceRoot in $sourceRoots) {
                        if ($loadedPath.Equals($sourceRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
                            $loadedPath.StartsWith($sourceRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
                            return $true
                        }
                    }
                }
                return $false
            } |
            Select-Object ProcessName, Id, Path
    )
    if ($active.Count -gt 0) {
        $summary = @($active | ForEach-Object { "$($_.ProcessName)#$($_.Id)" }) -join ', '
        throw "迁移前必须停止正在使用迁移源的 Python/uv/pip 进程：$summary"
    }
}


function Assert-StoredHashManifestShape {
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $files = @($Manifest.files)
    if ([int64]$Manifest.file_count -ne $files.Count) {
        throw "$Label 文件计数与数组长度不一致"
    }
    $seen = @{}
    $totalBytes = [int64]0
    foreach ($entry in $files) {
        $relative = [string]$entry.relative_path
        if ([string]::IsNullOrWhiteSpace($relative) -or
            [int64]$entry.length -lt 0 -or
            [string]$entry.sha256 -notmatch '^[0-9a-f]{64}$') {
            throw "$Label 含无效文件 SHA 条目：$relative"
        }
        $key = $relative.ToLowerInvariant()
        if ($seen.ContainsKey($key)) {
            throw "$Label 含重复相对路径：$relative"
        }
        $seen[$key] = $true
        $totalBytes += [int64]$entry.length
    }
    if ($totalBytes -ne [int64]$Manifest.total_bytes) {
        throw "$Label 文件字节汇总不一致"
    }
    if ([int]$Manifest.junction_count -ne @($Manifest.junctions).Count) {
        throw "$Label Junction 计数与数组长度不一致"
    }
}


function Assert-AlreadyMigratedIntegrity {
    param([Parameter(Mandatory = $true)]$Spec)

    if (Test-Path -LiteralPath $Spec.Backup) {
        throw "已迁移项仍有固定备份，拒绝继续：$($Spec.Backup)"
    }
    $manifestRoot = Join-Path $LayoutPaths.Registry 'storage-migrations'
    $storedPath = @(
        Get-ChildItem -LiteralPath $manifestRoot -Filter ($Spec.Name + '.target.json') -File -Recurse -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending |
            Select-Object -First 1
    )
    if ($storedPath.Count -ne 1) {
        throw "找不到已迁移项的历史目标 manifest：$($Spec.Name)"
    }
    $manifestDirectory = $storedPath[0].Directory.FullName
    $historicalOperationId = Split-Path -Leaf $manifestDirectory
    $sourcePath = Join-Path $manifestDirectory ($Spec.Name + '.source.json')
    $stagePath = Join-Path $manifestDirectory ($Spec.Name + '.stage.json')
    $resultPath = Join-Path $manifestDirectory 'result.json'
    foreach ($requiredManifest in @($sourcePath, $stagePath, $storedPath[0].FullName, $resultPath)) {
        if (-not (Test-Path -LiteralPath $requiredManifest -PathType Leaf)) {
            throw "历史迁移证据不完整：$requiredManifest"
        }
    }
    try {
        $sourceStored = Get-Content -LiteralPath $sourcePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $stageStored = Get-Content -LiteralPath $stagePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $targetStored = Get-Content -LiteralPath $storedPath[0].FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $resultStored = Get-Content -LiteralPath $resultPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        throw "历史迁移 JSON 无法解析：$manifestDirectory"
    }
    if (-not ([string]$resultStored.operation_id).Equals(
        $historicalOperationId,
        [System.StringComparison]::OrdinalIgnoreCase
    ) -or [string]$resultStored.status -ne 'ok' -or
        -not (Get-NormalizedPath ([string]$resultStored.training_root)).Equals(
            (Get-NormalizedPath $TrainingRoot),
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
        throw "历史迁移 result 与目录或训练根不一致：$manifestDirectory"
    }
    $resultItems = @($resultStored.items | Where-Object { [string]$_.name -eq $Spec.Name })
    if ($resultItems.Count -ne 1 -or [string]$resultItems[0].status -ne 'migrated' -or
        -not [bool]$resultItems[0].backup_removed -or
        -not (Get-NormalizedPath ([string]$resultItems[0].source)).Equals(
            (Get-NormalizedPath $Spec.Source),
            [System.StringComparison]::OrdinalIgnoreCase
        ) -or
        -not (Get-NormalizedPath ([string]$resultItems[0].target)).Equals(
            (Get-NormalizedPath $Spec.Target),
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
        throw "历史迁移 result item 与当前合同不一致：$($Spec.Name)"
    }
    if (-not (Get-NormalizedPath ([string]$sourceStored.root)).Equals(
        (Get-NormalizedPath $Spec.Source),
        [System.StringComparison]::OrdinalIgnoreCase
    ) -or -not (Get-NormalizedPath ([string]$targetStored.root)).Equals(
        (Get-NormalizedPath $Spec.Target),
        [System.StringComparison]::OrdinalIgnoreCase
    ) -or -not (Test-PathWithin -Candidate ([string]$stageStored.root) -Root $LayoutPaths.Temp)) {
        throw "历史迁移 manifest 根路径与当前合同不一致：$($Spec.Name)"
    }
    Assert-StoredHashManifestShape $sourceStored "$($Spec.Name) source manifest"
    Assert-StoredHashManifestShape $stageStored "$($Spec.Name) stage manifest"
    Assert-StoredHashManifestShape $targetStored "$($Spec.Name) target manifest"
    Assert-ManifestsEqual `
        -Expected $sourceStored `
        -Actual $stageStored `
        -Label "$($Spec.Name) stored source/stage" `
        -IgnoreJunctions
    Assert-ManifestsEqual `
        -Expected $sourceStored `
        -Actual $targetStored `
        -Label "$($Spec.Name) stored source/target"
    $junctionTarget = Get-JunctionTarget $Spec.Source
    if (-not $junctionTarget.Equals(
        (Get-NormalizedPath $Spec.Target),
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "已迁移 junction 目标漂移：$($Spec.Source) -> $junctionTarget"
    }
    return [ordered]@{
        status = 'verified'
        operation_id = $historicalOperationId
        file_count = [int64]$targetStored.file_count
        total_bytes = [int64]$targetStored.total_bytes
        current_target_policy = 'mutable_runtime_verified_by_junction_and_tools'
        manifest_sha256 = [ordered]@{
            source = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
            stage = (Get-FileHash -LiteralPath $stagePath -Algorithm SHA256).Hash.ToLowerInvariant()
            target = (Get-FileHash -LiteralPath $storedPath[0].FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            result = (Get-FileHash -LiteralPath $resultPath -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
}


function Invoke-ReadOnlyRuntimeVerification {
    $managedPython = Join-Path `
        $LayoutPaths.UvPython `
        'cpython-3.12.13-windows-x86_64-none\python.exe'
    if (-not (Test-Path -LiteralPath $managedPython -PathType Leaf)) {
        throw "D 盘 managed Python 不存在：$managedPython"
    }
    $previousEnvironment = [ordered]@{}
    foreach ($spec in $MigrationSpecs) {
        $previousEnvironment[$spec.EnvironmentName] = [Environment]::GetEnvironmentVariable(
            $spec.EnvironmentName,
            'Process'
        )
        [Environment]::SetEnvironmentVariable(
            $spec.EnvironmentName,
            (Get-NormalizedPath $spec.Target),
            'Process'
        )
    }
    try {
        foreach ($spec in $MigrationSpecs) {
            Invoke-ToolVerification $spec
        }
        $pythonProbe = @'
import json
import os
from pathlib import Path
import pip
import sys

print(json.dumps({
    'executable': str(Path(sys.executable).resolve()),
    'base_prefix': str(Path(sys.base_prefix).resolve()),
    'pip_cache': str(Path(os.environ['PIP_CACHE_DIR']).resolve()),
    'pip_version': pip.__version__,
}, ensure_ascii=True, separators=(',', ':')))
'@
        $previousErrorAction = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $probeOutput = @(& $managedPython -I -B -c $pythonProbe 2>&1)
            $probeExitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $previousErrorAction
        }
        if ($probeExitCode -ne 0 -or $probeOutput.Count -ne 1) {
            throw "D 盘 managed Python/pip 只读验证失败：$($probeOutput -join ' | ')"
        }
        try {
            $probe = ([string]$probeOutput[0]) | ConvertFrom-Json
        }
        catch {
            throw 'D 盘 managed Python/pip 验证输出不是有效 JSON'
        }
        if (-not (Get-NormalizedPath ([string]$probe.executable)).Equals(
            (Get-NormalizedPath $managedPython),
            [System.StringComparison]::OrdinalIgnoreCase
        ) -or -not (Test-PathWithin `
            -Candidate ([string]$probe.base_prefix) `
            -Root $LayoutPaths.UvPython `
            -AllowEqual
        ) -or -not (Get-NormalizedPath ([string]$probe.pip_cache)).Equals(
            (Get-NormalizedPath $LayoutPaths.PipCache),
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
            throw 'D 盘 managed Python/pip 路径验证失败'
        }
        return [ordered]@{
            status = 'verified'
            uv_cache = Get-NormalizedPath $LayoutPaths.UvCache
            uv_python = Get-NormalizedPath $LayoutPaths.UvPython
            pip_cache = Get-NormalizedPath $LayoutPaths.PipCache
            python = Get-NormalizedPath ([string]$probe.executable)
            python_base_prefix = Get-NormalizedPath ([string]$probe.base_prefix)
            pip_version = [string]$probe.pip_version
        }
    }
    finally {
        foreach ($spec in $MigrationSpecs) {
            [Environment]::SetEnvironmentVariable(
                $spec.EnvironmentName,
                $previousEnvironment[$spec.EnvironmentName],
                'Process'
            )
        }
    }
}


function New-StageContext {
    param(
        [Parameter(Mandatory = $true)]$Spec,
        [Parameter(Mandatory = $true)][string]$OperationTemp
    )

    $stagePath = Join-Path $OperationTemp $Spec.Name
    Assert-SpecPaths -Spec $Spec -StagePath $stagePath
    return [ordered]@{
        Spec = $Spec
        Stage = $stagePath
        Status = 'pending'
        SourceManifest = $null
        TargetWasEmpty = $false
        BackupCreated = $false
        TargetPromoted = $false
        JunctionCreated = $false
    }
}


function Invoke-MigrationStage {
    param(
        [Parameter(Mandatory = $true)]$Context,
        [Parameter(Mandatory = $true)][string]$ManifestDirectory,
        [Parameter(Mandatory = $true)][string]$OperationId
    )

    $spec = $Context.Spec
    $audit = Get-DirectoryAudit $spec
    if ($audit.action -eq 'source_missing') {
        $Context.Status = 'skipped_missing'
        return
    }
    if ($audit.action -eq 'already_migrated') {
        Assert-AlreadyMigratedIntegrity $spec
        Invoke-ToolVerification $spec
        $Context.Status = 'already_migrated'
        return
    }
    if ($audit.action -ne 'ready_to_migrate') {
        throw "迁移项状态不允许执行：$($spec.Name), state=$($audit.action)"
    }
    if (Test-Path -LiteralPath $spec.Backup) {
        throw "固定备份路径已存在，需先人工核验：$($spec.Backup)"
    }
    if (Test-Path -LiteralPath $Context.Stage) {
        throw "stage 已存在，拒绝复用：$($Context.Stage)"
    }

    $sourceManifest = Get-HashManifest $spec.Source
    New-Item -ItemType Directory -Path $Context.Stage -Force | Out-Null
    Copy-DirectoryContents -Source $spec.Source -Destination $Context.Stage
    $stageManifest = Get-HashManifest $Context.Stage
    Assert-ManifestsEqual -Expected $sourceManifest -Actual $stageManifest -Label "$($spec.Name) source/stage" -IgnoreJunctions
    $Context.SourceManifest = $sourceManifest
    Write-JsonAtomic -LiteralPath (Join-Path $ManifestDirectory ($spec.Name + '.source.json')) -Value $sourceManifest -OperationId $OperationId
    Write-JsonAtomic -LiteralPath (Join-Path $ManifestDirectory ($spec.Name + '.stage.json')) -Value $stageManifest -OperationId $OperationId

    if (Test-Path -LiteralPath $spec.Target) {
        $targetItem = Get-Item -LiteralPath $spec.Target -Force
        if (-not $targetItem.PSIsContainer -or
            $null -ne (Get-ChildItem -LiteralPath $spec.Target -Force | Select-Object -First 1)) {
            throw "目标已存在且非空，拒绝合并：$($spec.Target)"
        }
        $Context.TargetWasEmpty = $true
        Remove-Item -LiteralPath $spec.Target -Force
    }

    Move-Item -LiteralPath $spec.Source -Destination $spec.Backup
    $Context.BackupCreated = $true
    Move-Item -LiteralPath $Context.Stage -Destination $spec.Target
    $Context.TargetPromoted = $true
    Restore-InternalJunctions -LiteralRoot $spec.Target -Manifest $sourceManifest
    New-Item -ItemType Junction -Path $spec.Source -Target $spec.Target | Out-Null
    $Context.JunctionCreated = $true

    $junctionTarget = Get-JunctionTarget $spec.Source
    if (-not $junctionTarget.Equals((Get-NormalizedPath $spec.Target), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "junction 目标不匹配：$($spec.Source) -> $junctionTarget"
    }
    $targetManifest = Get-HashManifest $spec.Target
    $junctionManifest = Get-HashManifest $spec.Source -RelocatedFromRoot $spec.Target
    Assert-ManifestsEqual -Expected $sourceManifest -Actual $targetManifest -Label "$($spec.Name) source/target"
    Assert-ManifestsEqual -Expected $sourceManifest -Actual $junctionManifest -Label "$($spec.Name) source/junction"
    Write-JsonAtomic -LiteralPath (Join-Path $ManifestDirectory ($spec.Name + '.target.json')) -Value $targetManifest -OperationId $OperationId
    Invoke-ToolVerification $spec
    $Context.Status = 'migrated'
}


function Undo-MigrationStage {
    param([Parameter(Mandatory = $true)]$Context)

    $spec = $Context.Spec
    Assert-SpecPaths -Spec $spec -StagePath $Context.Stage

    if ($Context.JunctionCreated -and (Test-Path -LiteralPath $spec.Source)) {
        $item = Get-Item -LiteralPath $spec.Source -Force
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq 0) {
            throw "回滚拒绝删除非 junction 来源：$($spec.Source)"
        }
        $target = Get-JunctionTarget $spec.Source
        if (-not $target.Equals((Get-NormalizedPath $spec.Target), [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "回滚拒绝删除指向未知目标的 junction：$($spec.Source)"
        }
        Remove-Item -LiteralPath $spec.Source -Force
        $Context.JunctionCreated = $false
    }

    if ($Context.TargetPromoted -and (Test-Path -LiteralPath $spec.Target)) {
        if ($null -eq $Context.SourceManifest) {
            throw "缺少 source manifest，拒绝删除 promoted target：$($spec.Target)"
        }
        $targetManifest = Get-HashManifest $spec.Target
        Assert-ManifestsEqual -Expected $Context.SourceManifest -Actual $targetManifest -Label "$($spec.Name) rollback target" -IgnoreJunctions
        if (-not (Test-PathWithin -Candidate $spec.Target -Root $TrainingRoot)) {
            throw "回滚目标越出训练根：$($spec.Target)"
        }
        Remove-Item -LiteralPath $spec.Target -Recurse -Force
        $Context.TargetPromoted = $false
    }

    if ($Context.BackupCreated -and (Test-Path -LiteralPath $spec.Backup)) {
        if (Test-Path -LiteralPath $spec.Source) {
            throw "来源已存在，拒绝覆盖式恢复备份：$($spec.Source)"
        }
        Move-Item -LiteralPath $spec.Backup -Destination $spec.Source
        $Context.BackupCreated = $false
    }

    if (Test-Path -LiteralPath $Context.Stage) {
        if (-not (Test-PathWithin -Candidate $Context.Stage -Root $LayoutPaths.Temp)) {
            throw "回滚 stage 越出 runtime\\tmp：$($Context.Stage)"
        }
        Remove-Item -LiteralPath $Context.Stage -Recurse -Force
    }
    if ($Context.TargetWasEmpty -and -not (Test-Path -LiteralPath $spec.Target)) {
        New-Item -ItemType Directory -Path $spec.Target -Force | Out-Null
    }
    $Context.Status = 'rolled_back'
}


function Remove-VerifiedBackup {
    param([Parameter(Mandatory = $true)]$Context)

    if (-not $Context.BackupCreated) {
        return
    }
    $spec = $Context.Spec
    if (-not (Test-Path -LiteralPath $spec.Backup)) {
        throw "成功清理前找不到固定备份：$($spec.Backup)"
    }
    $backupManifest = Get-HashManifest $spec.Backup -RelocatedFromRoot $spec.Source
    Assert-ManifestsEqual -Expected $Context.SourceManifest -Actual $backupManifest -Label "$($spec.Name) backup cleanup"
    $expectedBackup = Get-NormalizedPath ($spec.Source + '.kronos-storage-backup')
    if (-not (Get-NormalizedPath $spec.Backup).Equals($expectedBackup, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "拒绝删除非固定备份路径：$($spec.Backup)"
    }
    Remove-Item -LiteralPath $spec.Backup -Recurse -Force
    $Context.BackupCreated = $false
}


Assert-ExpectedMachine
Assert-NoReparseAncestors $TrainingRoot
foreach ($spec in $MigrationSpecs) {
    Assert-NoReparseAncestors $spec.Target
}
$auditRecords = @($MigrationSpecs | ForEach-Object { Get-DirectoryAudit $_ })
$bytesToCopy = [int64]0
$filesToCopy = [int64]0
foreach ($record in $auditRecords) {
    if ($record.action -eq 'ready_to_migrate') {
        $payload = Get-DirectoryPayloadStats -LiteralRoot $record.source
        $bytesToCopy += [int64]$payload.total_bytes
        $filesToCopy += [int64]$payload.file_count
    }
}
$driveRoot = [System.IO.Path]::GetPathRoot((Get-NormalizedPath $TrainingRoot))
$driveInfo = New-Object System.IO.DriveInfo($driveRoot)
$reserveBytes = [Math]::Max([int64](1GB), [int64][Math]::Ceiling($bytesToCopy * 0.20))
$requiredBytes = $bytesToCopy + $reserveBytes
$spacePreflight = [ordered]@{
    files_to_copy = $filesToCopy
    bytes_to_copy = $bytesToCopy
    reserve_bytes = $reserveBytes
    required_free_bytes = $requiredBytes
    available_free_bytes = [int64]$driveInfo.AvailableFreeSpace
    status = if ([int64]$driveInfo.AvailableFreeSpace -ge $requiredBytes) { 'ok' } else { 'blocked' }
}
$runtimeVerification = $null
if (-not $Apply) {
    $alreadyMigratedRecords = @(
        $auditRecords | Where-Object { $_.action -eq 'already_migrated' }
    )
    foreach ($record in $alreadyMigratedRecords) {
        $spec = @($MigrationSpecs | Where-Object { $_.Name -eq $record.name })[0]
        $record['historical_manifest_integrity'] = Assert-AlreadyMigratedIntegrity $spec
    }
    if ($alreadyMigratedRecords.Count -eq $MigrationSpecs.Count) {
        $runtimeVerification = Invoke-ReadOnlyRuntimeVerification
        foreach ($record in $alreadyMigratedRecords) {
            $record['functional_verification'] = 'verified'
        }
    }
    else {
        foreach ($record in $alreadyMigratedRecords) {
            $spec = @($MigrationSpecs | Where-Object { $_.Name -eq $record.name })[0]
            Invoke-ToolVerification $spec
            $record['functional_verification'] = 'verified'
        }
    }
}
$auditReport = [ordered]@{
    mode = if ($Apply) { 'apply_requested' } else { 'audit_only' }
    training_root = Get-NormalizedPath $TrainingRoot
    generated_at = [DateTime]::UtcNow.ToString('o')
    exclusions = @($ExcludedPaths | ForEach-Object { Get-NormalizedPath $_ })
    items = $auditRecords
    space_preflight = $spacePreflight
    runtime_verification = $runtimeVerification
}

if (-not $Apply) {
    Write-Output 'Kronos 存储迁移只读审计完成；未创建、复制、移动或删除任何路径。'
    $auditReport | ConvertTo-Json -Depth 10
    $MigrationMutex.ReleaseMutex()
    $MigrationMutex.Dispose()
    exit 0
}

if ($spacePreflight.status -ne 'ok') {
    throw "D 盘空间预检失败：required=$($spacePreflight.required_free_bytes), available=$($spacePreflight.available_free_bytes)"
}
Assert-NoActiveMigrationClients

$operationId = [guid]::NewGuid().ToString('N')
$operationTemp = Join-Path $LayoutPaths.Temp ('m-' + $operationId.Substring(0, 12))
$manifestDirectory = Join-Path $LayoutPaths.Registry ('storage-migrations\' + $operationId)
if (-not (Test-PathWithin -Candidate $operationTemp -Root $LayoutPaths.Temp) -or
    -not (Test-PathWithin -Candidate $manifestDirectory -Root $LayoutPaths.Registry)) {
    throw '迁移工作目录未通过统一训练根包含关系检查'
}

foreach ($path in $LayoutPaths.Values) {
    $normalized = Get-NormalizedPath $path
    if (-not (Test-PathWithin -Candidate $normalized -Root $TrainingRoot -AllowEqual)) {
        throw "布局路径越出统一训练根：$normalized"
    }
    New-Item -ItemType Directory -Path $normalized -Force | Out-Null
}
New-Item -ItemType Directory -Path $operationTemp -Force | Out-Null
New-Item -ItemType Directory -Path $manifestDirectory -Force | Out-Null

$contexts = @()
$applyError = $null
$previousUserEnvironment = [ordered]@{}
try {
    foreach ($spec in $MigrationSpecs) {
        $context = New-StageContext -Spec $spec -OperationTemp $operationTemp
        $contexts += $context
        Invoke-MigrationStage -Context $context -ManifestDirectory $manifestDirectory -OperationId $operationId
    }
    foreach ($spec in $MigrationSpecs) {
        $previousUserEnvironment[$spec.EnvironmentName] = [Environment]::GetEnvironmentVariable(
            $spec.EnvironmentName,
            'User'
        )
        [Environment]::SetEnvironmentVariable(
            $spec.EnvironmentName,
            (Get-NormalizedPath $spec.Target),
            'User'
        )
        $readback = [Environment]::GetEnvironmentVariable($spec.EnvironmentName, 'User')
        if (-not (Get-NormalizedPath $readback).Equals((Get-NormalizedPath $spec.Target), [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "用户级环境变量写后回读失败：$($spec.EnvironmentName)"
        }
    }
}
catch {
    $applyError = $_
    $rollbackErrors = @()
    foreach ($name in @($previousUserEnvironment.Keys)) {
        try {
            [Environment]::SetEnvironmentVariable($name, $previousUserEnvironment[$name], 'User')
        }
        catch {
            $rollbackErrors += "用户级环境变量回滚失败：${name}: $($_.Exception.Message)"
        }
    }
    for ($index = $contexts.Count - 1; $index -ge 0; $index--) {
        $context = $contexts[$index]
        if ($context.BackupCreated -or $context.TargetPromoted -or $context.JunctionCreated -or
            (Test-Path -LiteralPath $context.Stage)) {
            try {
                Undo-MigrationStage $context
            }
            catch {
                $rollbackErrors += $_.Exception.Message
            }
        }
    }
    if ($rollbackErrors.Count -gt 0) {
        throw "迁移失败且回滚不完整：$($applyError.Exception.Message)；rollback=$($rollbackErrors -join ' | ')"
    }
    throw "迁移失败，已完成回滚：$($applyError.Exception.Message)"
}

foreach ($context in $contexts) {
    if ($context.Status -eq 'migrated') {
        $targetManifest = Get-HashManifest $context.Spec.Target
        $backupManifest = Get-HashManifest $context.Spec.Backup -RelocatedFromRoot $context.Spec.Source
        Assert-ManifestsEqual -Expected $context.SourceManifest -Actual $targetManifest -Label "$($context.Spec.Name) target cleanup preflight"
        Assert-ManifestsEqual -Expected $context.SourceManifest -Actual $backupManifest -Label "$($context.Spec.Name) backup cleanup preflight"
    }
}
foreach ($context in $contexts) {
    if ($context.Status -eq 'migrated') {
        Remove-VerifiedBackup $context
    }
}

if (Test-Path -LiteralPath $operationTemp) {
    if (-not (Test-PathWithin -Candidate $operationTemp -Root $LayoutPaths.Temp)) {
        throw "拒绝清理越界 operation temp：$operationTemp"
    }
    Remove-Item -LiteralPath $operationTemp -Recurse -Force
}

$result = [ordered]@{
    status = 'ok'
    operation_id = $operationId
    completed_at = [DateTime]::UtcNow.ToString('o')
    training_root = Get-NormalizedPath $TrainingRoot
    items = @($contexts | ForEach-Object {
        [ordered]@{
            name = $_.Spec.Name
            status = $_.Status
            source = Get-NormalizedPath $_.Spec.Source
            target = Get-NormalizedPath $_.Spec.Target
            backup_removed = -not (Test-Path -LiteralPath $_.Spec.Backup)
        }
    })
}
Write-JsonAtomic -LiteralPath (Join-Path $manifestDirectory 'result.json') -Value $result -OperationId $operationId
Write-Output 'Kronos 存储迁移成功；功能验证通过，固定备份已删除。'
$result | ConvertTo-Json -Depth 10
$MigrationMutex.ReleaseMutex()
$MigrationMutex.Dispose()
