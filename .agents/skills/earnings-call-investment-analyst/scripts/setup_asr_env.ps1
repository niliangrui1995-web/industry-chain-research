param(
    [string]$VenvPath = ".venv_earnings_asr"
)

$ErrorActionPreference = "Stop"
$skillRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$requirements = Join-Path $skillRoot "requirements-asr.txt"

if (-not (Test-Path -LiteralPath $VenvPath)) {
    py -3.10 -m venv $VenvPath
}

$python = Join-Path $VenvPath "Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r $requirements
& $python (Join-Path $skillRoot "scripts\audio_transcriber.py") --check-deps
