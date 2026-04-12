"""
health.py — AURa OS health and metrics reporter.

Provides a comprehensive health snapshot: CPU, memory, disk, process, and
AURa-specific subsystem status.  All probing uses only the standard library;
optional psutil results are included when psutil is installed.
"""

import os
import platform as _platform
import datetime

from core.runtime.paths import aura_path, AURA_ROOT
from core.runtime.logs  import LOG_PATH, write_log


# ── OS-level helpers ──────────────────────────────────────────────────────────

def _load_avg():
    """Return 1-minute load average as a float (Linux/Android/Termux)."""
    try:
        with open("/proc/loadavg", "r") as f:
            return float(f.read().split()[0])
    except Exception:
        pass
    try:
        import psutil  # type: ignore
        return psutil.getloadavg()[0]
    except Exception:
        return 0.0


def _memory_info():
    """Return a dict with total_mb, available_mb, used_pct."""
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                mem[parts[0].rstrip(":")] = int(parts[1])
        total = mem.get("MemTotal", 0)
        avail = mem.get("MemAvailable", mem.get("MemFree", 0))
        used  = total - avail
        pct   = (used / total * 100) if total else 0.0
        return {
            "total_mb":     round(total / 1024, 1),
            "available_mb": round(avail / 1024, 1),
            "used_pct":     round(pct, 1),
        }
    except Exception:
        pass
    try:
        import psutil  # type: ignore
        vm = psutil.virtual_memory()
        return {
            "total_mb":     round(vm.total    / 1024 / 1024, 1),
            "available_mb": round(vm.available / 1024 / 1024, 1),
            "used_pct":     vm.percent,
        }
    except Exception:
        return {"total_mb": 0, "available_mb": 0, "used_pct": 0}


def _disk_info():
    """Return free/total MB for AURA_ROOT."""
    try:
        st    = os.statvfs(AURA_ROOT)
        total = st.f_blocks * st.f_frsize
        free  = st.f_bavail * st.f_frsize
        used  = total - free
        pct   = (used / total * 100) if total else 0.0
        return {
            "path":     AURA_ROOT,
            "total_mb": round(total / 1024 / 1024, 1),
            "free_mb":  round(free  / 1024 / 1024, 1),
            "used_pct": round(pct, 1),
        }
    except Exception:
        return {"path": AURA_ROOT, "total_mb": 0, "free_mb": 0, "used_pct": 0}


def _log_size_kb():
    """Return log file size in KB."""
    try:
        return round(os.path.getsize(LOG_PATH) / 1024, 1)
    except Exception:
        return 0.0


# ── Public API ────────────────────────────────────────────────────────────────

def get_health():
    """
    Return a comprehensive health snapshot as a dict.

    Keys: timestamp, status, cpu, memory, disk, process, aura
    """
    cores    = os.cpu_count() or 1
    load     = _load_avg()
    load_pct = min(100.0, round(load / cores * 100, 1))

    health = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status":    "healthy",
        "cpu": {
            "cores":    cores,
            "load_1m":  load,
            "load_pct": load_pct,
            "arch":     _platform.machine(),
        },
        "memory": _memory_info(),
        "disk":   _disk_info(),
        "process": {
            "pid":    os.getpid(),
            "python": _platform.python_version(),
            "node":   _platform.node(),
        },
        "aura": {
            "root":   AURA_ROOT,
            "log_kb": _log_size_kb(),
        },
    }

    # Degrade status if resources are critically low
    if health["memory"]["used_pct"] > 90:
        health["status"] = "degraded"
    if health["disk"]["used_pct"] > 95:
        health["status"] = "critical"

    write_log(
        f"Health check: status={health['status']} "
        f"cpu={load_pct}% mem={health['memory']['used_pct']}%"
    )
    return health


def health_report_text():
    """Return a human-readable multi-line health report string."""
    h    = get_health()
    cpu  = h["cpu"]
    mem  = h["memory"]
    disk = h["disk"]
    proc = h["process"]
    aura = h["aura"]
    lines = [
        "═══════════════════════════════════════════",
        "       AURa OS — Health Report",
        f"       {h['timestamp']}",
        "═══════════════════════════════════════════",
        "",
        f"  Status  : {h['status'].upper()}",
        "",
        "── CPU ───────────────────────────────────",
        f"  Arch    : {cpu['arch']}",
        f"  Cores   : {cpu['cores']}",
        f"  Load 1m : {cpu['load_1m']}  ({cpu['load_pct']}%)",
        "",
        "── Memory ────────────────────────────────",
        f"  Total   : {mem['total_mb']} MB",
        f"  Free    : {mem['available_mb']} MB",
        f"  Used    : {mem['used_pct']}%",
        "",
        "── Disk ──────────────────────────────────",
        f"  Path    : {disk['path']}",
        f"  Total   : {disk['total_mb']} MB",
        f"  Free    : {disk['free_mb']} MB",
        f"  Used    : {disk['used_pct']}%",
        "",
        "── Process ───────────────────────────────",
        f"  PID     : {proc['pid']}",
        f"  Python  : {proc['python']}",
        f"  Host    : {proc['node']}",
        "",
        "── AURa ──────────────────────────────────",
        f"  Root    : {aura['root']}",
        f"  Log     : {aura['log_kb']} KB",
        "═══════════════════════════════════════════",
    ]
    return "\n".join(lines)
