#!/usr/bin/env sh
# node_daemon.sh — AURa OS node agent / command channel daemon
#
# Starts the AURa command channel HTTP server as a headless background
# process.  Suitable for use in Termux boot scripts or cron jobs.
#
# Usage:
#   sh node_daemon.sh start    — start in background, write PID file
#   sh node_daemon.sh stop     — stop the running daemon
#   sh node_daemon.sh restart  — stop then start
#   sh node_daemon.sh status   — show whether the daemon is running
#   sh node_daemon.sh health   — print a one-line health summary
#   sh node_daemon.sh logs     — tail the AURa system log
#
# POSIX-compliant; no root/sudo required.
set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
AURA_ROOT="${AURA_ROOT:-${HOME}/.aura}"
PID_FILE="${AURA_ROOT}/local/cache/node_daemon.pid"
LOG_FILE="${AURA_ROOT}/local/cache/system.log"

# ── Find Python ───────────────────────────────────────────────────────────────
_python() {
    command -v python3 2>/dev/null || command -v python 2>/dev/null || {
        echo "Python not found" >&2; exit 1
    }
}
PYTHON_BIN="$(_python)"
export PYTHONPATH="${REPO_ROOT}"

# ── Helpers ───────────────────────────────────────────────────────────────────
_read_pid() {
    [ -f "${PID_FILE}" ] && cat "${PID_FILE}" || echo ""
}

_is_running() {
    PID="$(_read_pid)"
    [ -n "${PID}" ] && kill -0 "${PID}" 2>/dev/null
}

# ── Actions ───────────────────────────────────────────────────────────────────
_start() {
    if _is_running; then
        echo "AURa node daemon already running (PID $(_read_pid))"
        return
    fi
    mkdir -p "$(dirname "${PID_FILE}")"
    cd "${REPO_ROOT}"
    nohup "${PYTHON_BIN}" -c "
import sys, os
sys.path.insert(0, '${REPO_ROOT}')
from core.runtime.node_agent      import get_agent
from core.runtime.command_channel import start_command_channel
import time
agent = get_agent()
start_command_channel(node_agent=agent)
agent.register_with_cc()
agent.start_heartbeat()
print('AURa node daemon started')
while True:
    time.sleep(60)
" >> "${LOG_FILE}" 2>&1 &
    echo "$!" > "${PID_FILE}"
    echo "AURa node daemon started (PID $(cat "${PID_FILE}"))"
    echo "  Log : ${LOG_FILE}"
}

_stop() {
    PID="$(_read_pid)"
    if [ -z "${PID}" ] || ! kill -0 "${PID}" 2>/dev/null; then
        echo "AURa node daemon is not running"
        rm -f "${PID_FILE}"
        return
    fi
    kill "${PID}"
    rm -f "${PID_FILE}"
    echo "AURa node daemon stopped (PID ${PID})"
}

_status() {
    if _is_running; then
        echo "AURa node daemon is RUNNING (PID $(_read_pid))"
    else
        echo "AURa node daemon is STOPPED"
    fi
}

_health() {
    cd "${REPO_ROOT}"
    "${PYTHON_BIN}" -c "
import sys
sys.path.insert(0, '${REPO_ROOT}')
from core.runtime.health import get_health
h = get_health()
cpu  = h['cpu']
mem  = h['memory']
disk = h['disk']
print(
    f\"AURa health: {h['status'].upper()}  \",
    f\"cpu={cpu['load_pct']}%  \",
    f\"mem={mem['used_pct']}%  \",
    f\"disk={disk['used_pct']}%\"
)
"
}

_logs() {
    LINES="${1:-50}"
    tail -n "${LINES}" "${LOG_FILE}" 2>/dev/null || echo "(no log yet)"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    start)   _start ;;
    stop)    _stop ;;
    restart) _stop; _start ;;
    status)  _status ;;
    health)  _health ;;
    logs)    _logs "${2}" ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|health|logs [N]}"
        exit 1
        ;;
esac
