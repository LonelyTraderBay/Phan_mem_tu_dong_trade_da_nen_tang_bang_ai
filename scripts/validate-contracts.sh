#!/usr/bin/env bash
# Validate contracts (Bash)
# Usage: ./scripts/validate-contracts.sh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

fail() { echo "FAIL: $*" >&2; FAILED=1; }
ok() { echo "OK:   $*"; }

OPENAPI="$ROOT/packages/contracts/openapi/openapi.yaml"
if [[ ! -f "$OPENAPI" ]]; then
  fail "Missing packages/contracts/openapi/openapi.yaml"
else
  ok "openapi.yaml exists"
  if ! grep -qE '^openapi:' "$OPENAPI"; then
    fail "openapi.yaml does not look like OpenAPI (missing openapi: key)"
  else
    ok "openapi.yaml has openapi: key"
  fi
  if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
    PY="$(command -v python3 || command -v python)"
    set +e
    OUT="$("$PY" - "$OPENAPI" <<'PY'
import sys
path = sys.argv[1]
try:
    import yaml
except ImportError:
    print("SKIP_YAML_PARSE")
    sys.exit(0)
with open(path, encoding="utf-8") as f:
    yaml.safe_load(f)
print("YAML_OK")
PY
)"
    RC=$?
    set -e
    if [[ $RC -ne 0 ]]; then
      fail "openapi.yaml YAML parse error: $OUT"
    elif [[ "$OUT" == *YAML_OK* ]]; then
      ok "openapi.yaml parseable YAML (PyYAML)"
    else
      ok "openapi.yaml YAML parse skipped (install PyYAML for strict parse)"
    fi
  else
    ok "openapi.yaml YAML parse skipped (no python)"
  fi
fi

EVENTS="$ROOT/packages/contracts/events"
if [[ ! -d "$EVENTS" ]]; then
  fail "Missing packages/contracts/events/"
else
  shopt -s nullglob
  schemas=("$EVENTS"/*.schema.json)
  if [[ ${#schemas[@]} -lt 1 ]]; then
    fail "No events/*.schema.json files found"
  else
    ok "Found ${#schemas[@]} event schema(s)"
    for s in "${schemas[@]}"; do
      if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
        PY="$(command -v python3 || command -v python)"
        if "$PY" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" "$s"; then
          ok "JSON OK $(basename "$s")"
        else
          fail "Invalid JSON: $(basename "$s")"
        fi
      elif command -v jq >/dev/null 2>&1; then
        if jq empty "$s" >/dev/null; then
          ok "JSON OK $(basename "$s")"
        else
          fail "Invalid JSON: $(basename "$s")"
        fi
      else
        ok "JSON check skipped for $(basename "$s") (no python/jq)"
      fi
    done
  fi
fi

VERSION="$ROOT/packages/contracts/VERSION"
if [[ ! -f "$VERSION" ]]; then
  fail "Missing packages/contracts/VERSION"
else
  ok "VERSION present"
fi

echo
if [[ "$FAILED" -ne 0 ]]; then
  echo "RESULT: FAIL"
  exit 1
fi
echo "RESULT: PASS"
exit 0
