# Validate contracts + enterprise governance (PowerShell)
# Usage: .\scripts\validate-contracts.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
  $py = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $py) {
  Write-Host "FAIL: Python required for governance validation" -ForegroundColor Red
  exit 1
}

$gov = Join-Path $Root "scripts\validate_governance.py"
& $py.Source $gov
exit $LASTEXITCODE
