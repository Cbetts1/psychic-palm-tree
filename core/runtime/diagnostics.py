import os
import datetime
import platform as _platform

from core.runtime.logs import read_log, write_log, LOG_PATH
from core.runtime.identity import load_identity
from core.runtime.version import load_version
from core.runtime.vfs import HybridVFS
from core.runtime.scheduler import JobScheduler
from core.runtime.safe_mode import SafeMode


def full_report():
    """Return a comprehensive system diagnostic report string."""
    ident     = load_identity()
    ver       = load_version()
    scheduler = JobScheduler()
    vfs       = HybridVFS()
    safe      = SafeMode()
    cpu       = scheduler.status()["cpu"]
    procs     = scheduler.status()["processes"]
    mounts    = vfs.list_mounts()

    lines = [
        "═══════════════════════════════════════════",
        "        AURa OS — Diagnostics Report",
        f"        {datetime.datetime.now().isoformat()}",
        "═══════════════════════════════════════════",
        "",
        "── Identity ──────────────────────────────",
        f"  Device UUID : {ident['device_uuid']}",
        f"  Cloud UUID  : {ident['cloud_uuid'] or 'unlinked'}",
        "",
        "── Version ───────────────────────────────",
        f"  Version  : {ver['version']}",
        f"  Channel  : {ver['channel']}",
        f"  Rollback : {ver.get('rollback') or 'none'}",
        "",
        "── Host ──────────────────────────────────",
        f"  Platform : {_platform.system()} {_platform.release()}",
        f"  Machine  : {_platform.machine()}",
        f"  Python   : {_platform.python_version()}",
        "",
        "── CPU / Scheduler ───────────────────────",
        f"  Cores    : {cpu['cores']}",
        f"  Load     : {cpu['load'] * 100:.1f}%",
        f"  Processes: {len(procs)}",
        "",
        "── Filesystem ────────────────────────────",
    ]
    for name, path in mounts.items():
        mark = "✓" if os.path.exists(path) else "✗"
        lines.append(f"  [{mark}] {name:<14} {path}")

    lines += [
        "",
        "── Safe Mode ─────────────────────────────",
        f"  Enabled  : {safe.status()['safe_mode']}",
        "",
        "═══════════════════════════════════════════",
    ]
    return "\n".join(lines)


def crash_report(exc):
    """Write a crash report to the log and return a formatted string."""
    import traceback
    tb = traceback.format_exc()
    write_log(f"CRASH: {type(exc).__name__}: {exc}\n{tb}")
    return "\n".join([
        "",
        "!! AURa CRASH REPORT !!",
        f"  Error : {type(exc).__name__}: {exc}",
        f"  Time  : {datetime.datetime.now().isoformat()}",
        "",
        "Traceback:",
        tb,
        f"State saved to: {LOG_PATH}",
    ])


def session_summary(start_time):
    """Return a brief session summary given the session start datetime."""
    elapsed = datetime.datetime.now() - start_time
    scheduler = JobScheduler()
    procs = scheduler.status()["processes"]
    return "\n".join([
        "────────────────────────────────────────────",
        "  AURa Session Summary",
        f"  Started  : {start_time.isoformat()}",
        f"  Ended    : {datetime.datetime.now().isoformat()}",
        f"  Duration : {str(elapsed).split('.')[0]}",
        f"  Jobs run : {len(procs)}",
        f"  Log      : {LOG_PATH}",
        "────────────────────────────────────────────",
    ])
