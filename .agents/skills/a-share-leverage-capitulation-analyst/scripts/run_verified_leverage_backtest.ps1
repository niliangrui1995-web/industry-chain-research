param(
    [string]$Python = "python",
    [string]$EndDate = (Get-Date -Format "yyyy-MM-dd"),
    [ValidateRange(1, 4)]
    [int]$Workers = 2,
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $OutputRoot) {
    $OutputRoot = Join-Path $repoRoot "artifacts\leverage_capitulation\verified_2016_present"
}
$OutputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$auditDir = Join-Path $OutputRoot "official_margin_audit"
$marketAuditDir = Join-Path $OutputRoot "market_data_audit"
$backtestDir = Join-Path $OutputRoot "backtest_2019_present"

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

Write-Host "[1/3] Fetching Eastmoney margin balances and validating exchange checks..."
if ($PSBoundParameters.ContainsKey("Workers")) {
    Write-Host "Workers is retained for command compatibility; the bulk API uses fixed pagination."
}
& $Python (Join-Path $PSScriptRoot "audit_margin_history.py") `
    --output-dir $auditDir `
    --start-date "2016-01-01" `
    --end-date $EndDate
if ($LASTEXITCODE -ne 0) {
    throw "Margin fetch or exchange validation failed."
}

$auditJson = Join-Path $auditDir "margin_audit.json"
$audit = Get-Content -LiteralPath $auditJson -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $audit.verified_snapshot_complete) {
    throw "Verified margin snapshot is incomplete; backtest is blocked."
}
if ($audit.verified_start -ne "2016-01-04") {
    throw "Unexpected first verified trading date: $($audit.verified_start)"
}
if ($audit.verified_rows -ne $audit.verified_calendar_rows) {
    throw "Verified rows do not match the official SSE calendar."
}

Write-Host "[2/3] Auditing local market K-lines and official factor indexes..."
& $Python (Join-Path $PSScriptRoot "audit_market_data.py") `
    --output-dir $marketAuditDir `
    --start-date "2014-01-01" `
    --end-date $audit.verified_end
if ($LASTEXITCODE -ne 0) {
    throw "Market-data audit failed; backtest is blocked."
}

$marketAudit = Get-Content -LiteralPath (Join-Path $marketAuditDir "market_data_audit.json") `
    -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $marketAudit.pass_for_backtest) {
    throw "Market-data audit did not pass; backtest is blocked."
}

Write-Host "[3/3] Running the 2019-present no-lookahead backtest..."
& $Python (Join-Path $PSScriptRoot "leverage_capitulation_backtest.py") `
    --margin-csv (Join-Path $auditDir "verified_margin_balances.csv") `
    --margin-audit-json $auditJson `
    --index-source "cnindex" `
    --start-date "2019-01-01" `
    --output-dir $backtestDir
if ($LASTEXITCODE -ne 0) {
    throw "Backtest failed."
}

Write-Host "Completed."
Write-Host "Margin audit: $auditJson"
Write-Host "Market audit: $(Join-Path $marketAuditDir 'market_data_audit.json')"
Write-Host "Backtest: $(Join-Path $backtestDir 'backtest_results.json')"
