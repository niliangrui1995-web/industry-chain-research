param(
    [string]$Python = "python",
    [string]$EndDate = (Get-Date -Format "yyyy-MM-dd"),
    [string]$OutputDir = "",
    [ValidateRange(1, 32)]
    [int]$Workers = 8,
    [ValidateRange(1, 365)]
    [int]$RefreshDays = 14,
    [switch]$ForceAll
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
if (-not $OutputDir) {
    $OutputDir = Join-Path $repoRoot `
        "artifacts\leverage_capitulation\individual_margin_2016_present"
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host "Fetching DFCF per-security margin history from 2016-01-01 to $EndDate..."
Write-Host "Output: $OutputDir"
Write-Host "Workers: $Workers"

$arguments = @(
    (Join-Path $PSScriptRoot "fetch_eastmoney_individual_margin_history.py"),
    "--project-root", $repoRoot,
    "--output-dir", $OutputDir,
    "--start-date", "2016-01-01",
    "--end-date", $EndDate,
    "--workers", $Workers,
    "--refresh-days", $RefreshDays
)
if ($ForceAll) {
    $arguments += "--force-all"
}

& $Python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "DFCF per-security margin fetch is incomplete. Rerun the same command to resume."
}

$auditPath = Join-Path $OutputDir "individual_margin_audit.json"
$audit = Get-Content -LiteralPath $auditPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $audit.vendor_pagination_complete) {
    throw "DFCF detail pagination did not pass completeness checks."
}

Write-Host "DFCF per-security snapshot is complete at the vendor pagination layer."
Write-Host "Rows: $($audit.database_rows)"
Write-Host "Dates: $($audit.database_start) to $($audit.database_end)"
Write-Host "A-share stock rows: $($audit.rows_by_instrument_type.A_SHARE_STOCK)"
Write-Host "ETF rows retained separately: $($audit.rows_by_instrument_type.ETF)"
Write-Host "Audit: $auditPath"
Write-Host "Database: $(Join-Path $OutputDir 'eastmoney_individual_margin.sqlite')"
