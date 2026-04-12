#!/usr/bin/env sh
# build.sh — AURa OS reproducible build / environment setup script
#
# Verifies the environment, creates all required directories, and
# validates that the Python package structure is importable.
#
# Usage:
#   sh build.sh          # full setup
#   sh build.sh check    # syntax / import check only
#   sh build.sh clean    # remove generated __pycache__ dirs
#
# POSIX-compliant; no root/sudo required.
set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
AURA_ROOT="${AURA_ROOT:-${HOME}/.aura}"

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     AURa OS — Build System               ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""
echo "  Repo root  : ${REPO_ROOT}"
echo "  AURa root  : ${AURA_ROOT}"
echo ""

# ── Helpers ───────────────────────────────────────────────────────────────────
_ok()   { echo "  [ OK ] $*"; }
_fail() { echo "  [FAIL] $*"; exit 1; }
_info() { echo "  [ .. ] $*"; }

# ── Find Python ───────────────────────────────────────────────────────────────
PYTHON_BIN=""
for candidate in python3 python; do
    if command -v "${candidate}" >/dev/null 2>&1; then
        PYTHON_BIN="${candidate}"
        break
    fi
done
[ -z "${PYTHON_BIN}" ] && _fail "Python 3 not found. Install with: pkg install python"
_ok "Python: $(${PYTHON_BIN} --version 2>&1)"

# ── Check Python version >= 3.11 ──────────────────────────────────────────────
PY_VER=$(${PYTHON_BIN} -c "import sys; print(sys.version_info >= (3,11))")
[ "${PY_VER}" = "False" ] && _fail "Python 3.11+ is required."
_ok "Python version OK (>= 3.11)"

# ── Syntax check only mode ────────────────────────────────────────────────────
if [ "${1}" = "check" ]; then
    _info "Running syntax checks..."
    find "${REPO_ROOT}" -name "*.py" -not -path "*/__pycache__/*" | while read -r f; do
        ${PYTHON_BIN} -m py_compile "${f}" || _fail "Syntax error in ${f}"
    done
    _ok "All Python files pass syntax check."
    echo ""
    exit 0
fi

# ── Clean mode ────────────────────────────────────────────────────────────────
if [ "${1}" = "clean" ]; then
    _info "Removing __pycache__ directories..."
    find "${REPO_ROOT}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    _ok "Clean complete."
    echo ""
    exit 0
fi

# ── Full setup ────────────────────────────────────────────────────────────────

_info "Creating AURa filesystem..."
mkdir -p "${AURA_ROOT}/local/cache/models"
mkdir -p "${AURA_ROOT}/local/packages"
mkdir -p "${AURA_ROOT}/cloud/images"
mkdir -p "${AURA_ROOT}/cloud/videos"
mkdir -p "${AURA_ROOT}/cloud/apk"
mkdir -p "${AURA_ROOT}/cloud/docs"
mkdir -p "${AURA_ROOT}/cloud/models"
mkdir -p "${AURA_ROOT}/cloud/index"
mkdir -p "${AURA_ROOT}/cloud/search"
mkdir -p "${AURA_ROOT}/cloud/manifests"
mkdir -p "${AURA_ROOT}/cloud/packages"
_ok "Filesystem created"

_info "Verifying core imports..."
cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}"

${PYTHON_BIN} -c "
from core.runtime.paths    import aura_path, AURA_ROOT
from core.runtime.config   import load_config
from core.runtime.identity import load_identity
from core.runtime.version  import load_version
from core.runtime.health   import get_health
from core.runtime.vfs      import HybridVFS
from core.runtime.vnet     import VNet
from core.runtime.cloud_link import CloudLink
from core.runtime.node_agent import get_agent
from core.runtime.command_channel import channel_status
from core.runtime.builder  import list_templates
from core.runtime.peer_registry import list_peers
print('All core imports OK')
" || _fail "Import check failed (see above)"
_ok "Core imports verified"

_info "Verifying cloud/worker imports..."
${PYTHON_BIN} -c "
from cloud.workers import (
    run_image_job, run_video_job, run_apk_job, run_docs_job,
    run_models_job, run_index_job, run_search_job,
)
print('All worker imports OK')
" || _fail "Worker import check failed"
_ok "Worker imports verified"

_info "Verifying UI imports..."
${PYTHON_BIN} -c "
from ui.menu.boot_menu import show_boot_menu
from ui.menu.main_menu import launch_menu
print('UI imports OK')
" || _fail "UI import check failed"
_ok "UI imports verified"

_info "Running syntax check..."
find "${REPO_ROOT}" -name "*.py" -not -path "*/__pycache__/*" | while read -r f; do
    ${PYTHON_BIN} -m py_compile "${f}" || _fail "Syntax error in ${f}"
done
_ok "Syntax check passed"

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   AURa OS build complete — all OK!       ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""
echo "  Launch: python3 -m core.runtime.vhost"
echo "       or: sh tools/scripts/aura_boot.sh"
echo ""
