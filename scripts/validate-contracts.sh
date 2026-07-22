#!/usr/bin/env bash
# Validate contracts + enterprise governance (Bash)
# Usage: ./scripts/validate-contracts.sh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "FAIL: Python required for governance validation" >&2
  exit 1
fi

exec "$PY" "$ROOT/scripts/validate_governance.py"
