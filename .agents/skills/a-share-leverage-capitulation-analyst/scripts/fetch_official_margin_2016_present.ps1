param(
    [string]$Python = "python",
    [string]$EndDate = (Get-Date -Format "yyyy-MM-dd"),
    [ValidateRange(1, 4)]
    [int]$Workers = 2,
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
if ($PSBoundParameters.ContainsKey("Workers")) {
    Write-Host "Workers is no longer used; Eastmoney data is fetched with fixed 500-row pagination."
}
& (Join-Path $PSScriptRoot "fetch_eastmoney_margin_2016_present.ps1") `
    -Python $Python `
    -EndDate $EndDate `
    -OutputDir $OutputDir
