# Validate contracts (PowerShell)
# Usage: .\scripts\validate-contracts.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$script:Failed = $false

function Fail([string]$Msg) {
  Write-Host ("FAIL: {0}" -f $Msg) -ForegroundColor Red
  $script:Failed = $true
}

function Ok([string]$Msg) {
  Write-Host ("OK:   {0}" -f $Msg) -ForegroundColor Green
}

$OpenApi = Join-Path $Root "packages\contracts\openapi\openapi.yaml"
if (-not (Test-Path $OpenApi)) {
  Fail "Missing packages/contracts/openapi/openapi.yaml"
}
else {
  Ok "openapi.yaml exists"
  $raw = Get-Content -Raw -Path $OpenApi
  if ($raw -notmatch '(?m)^openapi:\s*') {
    Fail "openapi.yaml missing openapi: key"
  }
  else {
    Ok "openapi.yaml has openapi: key"
  }

  $py = Get-Command python -ErrorAction SilentlyContinue
  if (-not $py) {
    $py = Get-Command python3 -ErrorAction SilentlyContinue
  }
  if ($py) {
    $tmpPy = Join-Path $env:TEMP "validate_openapi_yaml.py"
    @'
import sys
path = sys.argv[1]
try:
    import yaml
except ImportError:
    print("SKIP_YAML_PARSE")
    raise SystemExit(0)
with open(path, encoding="utf-8") as f:
    yaml.safe_load(f)
print("YAML_OK")
'@ | Set-Content -Path $tmpPy -Encoding UTF8
    $out = & $py.Source $tmpPy $OpenApi 2>&1
    $code = $LASTEXITCODE
    Remove-Item -Force $tmpPy -ErrorAction SilentlyContinue
    if ($code -ne 0) {
      Fail ("openapi.yaml YAML parse error: {0}" -f $out)
    }
    elseif ("$out" -match "YAML_OK") {
      Ok "openapi.yaml parseable YAML (PyYAML)"
    }
    else {
      Ok "openapi.yaml YAML parse skipped (install PyYAML for strict parse)"
    }
  }
  else {
    Ok "openapi.yaml YAML parse skipped (no python)"
  }
}

$EventsDir = Join-Path $Root "packages\contracts\events"
if (-not (Test-Path $EventsDir)) {
  Fail "Missing packages/contracts/events/"
}
else {
  $schemas = @(Get-ChildItem -Path $EventsDir -Filter "*.schema.json" -File)
  if ($schemas.Count -lt 1) {
    Fail "No events/*.schema.json files found"
  }
  else {
    Ok ("Found {0} event schema(s)" -f $schemas.Count)
    foreach ($s in $schemas) {
      try {
        Get-Content -Raw -Path $s.FullName | ConvertFrom-Json | Out-Null
        Ok ("JSON OK {0}" -f $s.Name)
      }
      catch {
        Fail ("Invalid JSON: {0} - {1}" -f $s.Name, $_.Exception.Message)
      }
    }
  }
}

$Version = Join-Path $Root "packages\contracts\VERSION"
if (-not (Test-Path $Version)) {
  Fail "Missing packages/contracts/VERSION"
}
else {
  Ok "VERSION present"
}

Write-Host ""
if ($script:Failed) {
  Write-Host "RESULT: FAIL" -ForegroundColor Red
  exit 1
}
Write-Host "RESULT: PASS" -ForegroundColor Green
exit 0
