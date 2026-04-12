#!/usr/bin/env sh
# health_check.sh — AURa OS quick CLI health check
#
# Prints a formatted health report to stdout and exits with:
#   0 — healthy
#   1 — degraded or critical
#
# Usage:
#   sh tools/scripts/health_check.sh
#   sh tools/scripts/health_check.sh --json    (machine-readable JSON)
#
# POSIX-compliant; no root/sudo required.
set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
AURA_ROOT="${AURA_ROOT:-${HOME}/.aura}"

PYTHON_BIN=""
for candidate in python3 python; do
    if command -v "${candidate}" >/dev/null 2>&1; then
        PYTHON_BIN="${candidate}"
        break
    fi
done

if [ -z "${PYTHON_BIN}" ]; then
    echo "ERROR: Python not found" >&2
    exit 1
fi

export PYTHONPATH="${REPO_ROOT}"
cd "${REPO_ROOT}"

if [ "${1}" = "--json" ]; then
    "${PYTHON_BIN}" -c "
import sys, json
sys.path.insert(0, '${REPO_ROOT}')
from core.runtime.health import get_health
h = get_health()
print(json.dumps(h, indent=2, default=str))
sys.exit(0 if h['status'] == 'healthy' else 1)
"
else
    "${PYTHON_BIN}" -c "
import sys
sys.path.insert(0, '${REPO_ROOT}')
from core.runtime.health import health_report_text, get_health
print(health_report_text())
h = get_health()
sys.exit(0 if h['status'] == 'healthy' else 1)
"
fi
