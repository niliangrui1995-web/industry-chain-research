param(
    [string]$Python = "python",
    [string]$EndDate = (Get-Date -Format "yyyy-MM-dd"),
    [string]$OutputDir = "",
    [ValidateRange(1, 10000)]
    [int]$MinOfficialSzseChecks = 100,
    [switch]$ReuseSnapshots
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
if (-not $OutputDir) {
    $OutputDir = Join-Path $repoRoot `
        "artifacts\leverage_capitulation\verified_2016_present\official_margin_audit"
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host "Fetching Eastmoney SH/SZ margin balances from 2016-01-01 to $EndDate..."
Write-Host "Output: $OutputDir"
$arguments = @(
    (Join-Path $PSScriptRoot "audit_margin_history.py"),
    "--output-dir", $OutputDir,
    "--start-date", "2016-01-01",
    "--end-date", $EndDate,
    "--min-official-szse-checks", $MinOfficialSzseChecks
)
if ($ReuseSnapshots) {
    $arguments += "--reuse-snapshots"
}
& $Python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Fetch or exchange validation is incomplete. Review margin_audit.json."
}

$auditJson = Join-Path $OutputDir "margin_audit.json"
$audit = Get-Content -LiteralPath $auditJson -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $audit.verified_snapshot_complete) {
    throw "Verified snapshot did not pass completeness checks."
}
if ($audit.verified_start -ne "2016-01-04") {
    throw "Unexpected first trading date: $($audit.verified_start)"
}
if ($audit.verified_rows -ne $audit.verified_calendar_rows) {
    throw "Verified rows do not match the official SSE calendar."
}

Write-Host "Verified margin data is complete."
Write-Host "Eastmoney requests: $($audit.eastmoney_total_requests)"
Write-Host "Eastmoney SH/SZ rows: $($audit.eastmoney_sse_rows)/$($audit.eastmoney_szse_rows)"
Write-Host "Verified rows: $($audit.verified_rows)"
Write-Host "Date range: $($audit.verified_start) to $($audit.verified_end)"
Write-Host "Official SZSE checks: $($audit.official_szse_checks)"
Write-Host "Audit report: $auditJson"
Write-Host "Merged balances: $(Join-Path $OutputDir 'verified_margin_balances.csv')"
