"""
boot_sequence.py — AURa OS boot stabilizer.

Runs a step-by-step animated boot checklist that loads all runtime
dependencies before handing control to the boot menu.
"""

import sys
import time
from core.runtime.logs import write_log


# ── Internal helpers ──────────────────────────────────────────────────────────

def _step(label, fn, *args, **kwargs):
    """Run *fn*, print a spinner line, return the result."""
    sys.stdout.write(f"  [ .. ]  {label}  ")
    sys.stdout.flush()
    try:
        result = fn(*args, **kwargs) if fn else None
        sys.stdout.write("\r  [ OK ]  " + label + "          \n")
        sys.stdout.flush()
        write_log(f"Boot step OK: {label}")
        return result
    except Exception as exc:
        sys.stdout.write("\r  [FAIL]  " + label + "          \n")
        sys.stdout.flush()
        write_log(f"Boot step FAIL: {label} — {exc}")
        return None


def _pause(secs=0.12):
    time.sleep(secs)


# ── Public API ────────────────────────────────────────────────────────────────

def run_boot_sequence(host_info, vnet, cloud, vfs):
    """
    Display an animated boot checklist and initialize all core subsystems.

    Parameters
    ----------
    host_info : dict   — result from detect_host()
    vnet      : VNet
    cloud     : CloudLink
    vfs       : HybridVFS

    Returns
    -------
    dict with keys: host, vnet, cloud, vfs, net_mode
    """

    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║     AURa OS — Boot Sequence Stabilizer   ║")
    print("  ╚══════════════════════════════════════════╝")
    print()

    # ── Step 1: identity & version (already loaded by caller) ─────────────
    _pause()
    _step("Identity & version registry", None)

    # ── Step 2: host capabilities (already detected by caller) ────────────
    _pause()
    os_name  = host_info.get("os", "Unknown")
    cpu_arch = host_info.get("cpu_arch", "Unknown")
    _step(f"Host capabilities detected  [{os_name} / {cpu_arch}]", None)

    # ── Step 3: virtual filesystem ─────────────────────────────────────────
    _pause()
    _step("Virtual filesystem paths", vfs.ensure_paths)

    # ── Step 4: virtual network ────────────────────────────────────────────
    _pause()
    net_mode = _step("Virtual network connectivity", vnet.detect_connectivity)
    net_mode = net_mode or "offline"

    # ── Step 5: cloud link ─────────────────────────────────────────────────
    _pause()
    cloud_ok = _step("Cloud link", cloud.connect)
    cloud_status = "online" if cloud_ok else "offline"

    # ── Step 6: scheduler / vCPU warmup ───────────────────────────────────
    _pause()
    from core.runtime.scheduler import JobScheduler
    scheduler = _step("Scheduler & vCPU warmup", JobScheduler)

    # ── Step 7: safe-mode check ────────────────────────────────────────────
    _pause()
    from core.runtime.safe_mode import SafeMode
    safe = _step("Safe-mode check", SafeMode)

    # ── Step 8: package registry ───────────────────────────────────────────
    _pause()
    from core.runtime.apm import list_packages
    _step("Package registry", list_packages)

    # ── Done ───────────────────────────────────────────────────────────────
    print()
    print(f"  Network : {net_mode}   Cloud : {cloud_status}")
    print()
    print("  Boot stabilizer complete — environment ready.")
    print()
    _pause(0.3)

    write_log("Boot sequence stabilizer completed")

    return {
        "host":      host_info,
        "vnet":      vnet,
        "cloud":     cloud,
        "vfs":       vfs,
        "net_mode":  net_mode,
        "scheduler": scheduler,
        "safe":      safe,
    }
