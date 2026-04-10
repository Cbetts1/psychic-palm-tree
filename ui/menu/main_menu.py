"""
main_menu.py — AURa OS Operator Console (1-9 main menu + sub-menus).

Boot flow:
  vhost.py  →  boot_sequence  →  boot_menu  →  launch_menu (here)

Each numbered entry opens a sub-menu with its own numbered prompts,
headers, and a [0] Back option.
"""

from core.runtime.apm import list_packages, install_package, remove_package, update_packages
from core.runtime.identity_banner import aura_status_line
from core.shell.main_shell import start_shell
from core.runtime.scheduler import JobScheduler
from core.runtime.ai_interface import ai_chat
from core.runtime.vfs import HybridVFS
from core.runtime.logs import read_log, write_log
from core.runtime.sync import sync_push, sync_pull, sync_status
from core.runtime.diagnostics import full_report, session_summary
from core.runtime.vnet import VNet
from core.runtime.cloud_link import CloudLink
from core.runtime.safe_mode import SafeMode
from core.runtime.identity import load_identity
from core.runtime.version import load_version
import datetime
import platform as _platform


# ── Header / prompt helpers ───────────────────────────────────────────────────

def _header(title):
    bar = "═" * 44
    print()
    print(f"  ╔{bar}╗")
    print(f"  ║  {title:<42}  ║")
    print(f"  ╚{bar}╝")
    print()


def _sub_header(title):
    print()
    print(f"  ┌── {title} {'─' * max(0, 40 - len(title))}┐")


def _divider():
    print("  " + "─" * 46)


def _prompt(context=""):
    tag = f" [{context}]" if context else ""
    return input(f"  AURa{tag} » ").strip()


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 1 — Shell Console
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_shell():
    _header("1 — Shell Console")
    print("  [1]  Interactive shell")
    print("  [2]  Run single command")
    print("  [0]  Back")
    _divider()
    choice = _prompt("Shell")

    if choice == "1":
        start_shell()

    elif choice == "2":
        cmd_line = input("  Command: ").strip()
        from core.shell.commands import ls, cat, mounts, jobs
        scheduler = JobScheduler()
        parts = cmd_line.split()
        if not parts:
            return
        if parts[0] == "ls":
            print(ls(parts[1] if len(parts) > 1 else "."))
        elif parts[0] == "cat":
            print(cat(parts[1]) if len(parts) > 1 else "Usage: cat <file>")
        elif parts[0] == "mounts":
            print(mounts())
        elif parts[0] == "jobs":
            print(jobs(scheduler))
        else:
            print(f"  Unknown command: {parts[0]}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 2 — Main Host
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_main_host(env_ctx):
    _header("2 — Main Host")
    host = env_ctx.get("host", {})
    boot_mode = env_ctx.get("boot_mode", "unknown")

    while True:
        _sub_header("Main Host Info")
        print(f"  OS       : {host.get('os', 'Unknown')}")
        print(f"  Arch     : {host.get('cpu_arch', 'Unknown')}")
        print(f"  Features : {', '.join(host.get('features', []))}")
        print(f"  Boot mode: {boot_mode}")
        print(f"  Platform : {_platform.system()} {_platform.release()}")
        print(f"  Python   : {_platform.python_version()}")
        print()
        print("  [1]  Refresh host detection")
        print("  [2]  Show raw host capabilities")
        print("  [3]  Set host OS label")
        print("  [0]  Back")
        _divider()
        choice = _prompt("Host")

        if choice == "0":
            break

        elif choice == "1":
            try:
                from core.runtime.vhost import detect_host
                env_ctx["host"] = detect_host()
                host = env_ctx["host"]
                print("  → Host re-detected.")
            except Exception as exc:
                print(f"  → Detection failed: {exc}")

        elif choice == "2":
            print(f"  {host}")

        elif choice == "3":
            label = input("  New OS label: ").strip()
            if label:
                env_ctx["host"] = dict(host)
                env_ctx["host"]["os"] = label
                host = env_ctx["host"]
                print(f"  → Host OS label set to '{label}'")

        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 3 — Virtual Host (vHost)
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_vhost(env_ctx):
    _header("3 — Virtual Host (vHost)")
    vfs = env_ctx.get("vfs") or HybridVFS()

    while True:
        _sub_header("vHost Status")
        mounts = vfs.list_mounts()
        for name, path in mounts.items():
            import os
            mark = "✓" if os.path.exists(path) else "✗"
            print(f"    [{mark}] {name:<16} {path}")
        print()
        print("  [1]  Ensure all vHost paths")
        print("  [2]  List virtual mounts")
        print("  [3]  Mount status detail")
        print("  [0]  Back")
        _divider()
        choice = _prompt("vHost")

        if choice == "0":
            break
        elif choice == "1":
            vfs.ensure_paths()
            print("  → vHost paths ensured.")
        elif choice == "2":
            print(f"  Mounts: {vfs.list_mounts()}")
        elif choice == "3":
            import os
            for name, path in vfs.list_mounts().items():
                exists = os.path.exists(path)
                print(f"  {name:<18} {path}  [{'OK' if exists else 'MISSING'}]")
        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 4 — Virtual CPU (vCPU)
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_vcpu(env_ctx):
    _header("4 — Virtual CPU (vCPU)")
    scheduler = env_ctx.get("scheduler") or JobScheduler()

    while True:
        cpu   = scheduler.status()["cpu"]
        procs = scheduler.status()["processes"]
        _sub_header("vCPU Status")
        print(f"  Cores   : {cpu['cores']}")
        print(f"  Load    : {cpu['load'] * 100:.1f}%")
        print(f"  Processes: {len(procs)}")
        print()
        print("  [1]  Show process list")
        print("  [2]  Simulate CPU load")
        print("  [3]  Reset CPU load")
        print("  [0]  Back")
        _divider()
        choice = _prompt("vCPU")

        if choice == "0":
            break
        elif choice == "1":
            if procs:
                for p in procs:
                    print(f"    {p}")
            else:
                print("  No active processes.")
        elif choice == "2":
            val = input("  Load value [0.0 – 1.0]: ").strip()
            try:
                scheduler.vcpu.simulate_load(float(val))
                print(f"  → Load set to {float(val)*100:.0f}%")
            except ValueError:
                print("  → Invalid value.")
        elif choice == "3":
            scheduler.vcpu.simulate_load(0.0)
            print("  → CPU load reset to 0%.")
        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 5 — Virtual Cloud (vCloud)
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_vcloud(env_ctx):
    _header("5 — Virtual Cloud (vCloud)")
    cloud = env_ctx.get("cloud") or CloudLink()
    vnet  = env_ctx.get("vnet")  or VNet()

    while True:
        cloud_status = cloud.status()
        vnet_status  = vnet.status()
        _sub_header("vCloud / VNet Status")
        print(f"  Cloud online : {cloud_status['cloud_online']}")
        print(f"  Endpoint     : {cloud_status['endpoint']}")
        print(f"  Net mode     : {vnet_status['mode']}")
        print(f"  Routes       : {vnet_status['routes']}")
        print(f"  Endpoints    : {vnet_status['endpoints']}")
        print()
        print("  [1]  Reconnect to cloud")
        print("  [2]  Detect network connectivity")
        print("  [3]  Set network mode [online/offline/degraded]")
        print("  [4]  Add VNet route")
        print("  [5]  List VNet routes")
        print("  [6]  AI Interface")
        print("  [0]  Back")
        _divider()
        choice = _prompt("vCloud")

        if choice == "0":
            break
        elif choice == "1":
            ok = cloud.connect()
            print(f"  → Cloud {'connected' if ok else 'unreachable'}.")
        elif choice == "2":
            mode = vnet.detect_connectivity()
            env_ctx["net_mode"] = mode
            print(f"  → Network mode: {mode}")
        elif choice == "3":
            new_mode = input("  Mode [online/offline/degraded]: ").strip()
            print(f"  → {vnet.set_mode(new_mode)}")
            env_ctx["net_mode"] = vnet.mode
        elif choice == "4":
            name   = input("  Route name : ").strip()
            target = input("  Target     : ").strip()
            vnet.add_route(name, target)
            print(f"  → Route '{name}' → '{target}' added.")
        elif choice == "5":
            routes = vnet.list_routes()
            if routes:
                for r in routes:
                    print(f"    {r['name']} → {r['target']}")
            else:
                print("  No routes defined.")
        elif choice == "6":
            ai_chat()
        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 6 — Maintenance Tools
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_maintenance():
    _header("6 — Maintenance Tools")

    while True:
        _sub_header("Maintenance")
        print("  [1]  Package Manager (APM)")
        print("  [2]  Sync — push local → cloud")
        print("  [3]  Sync — pull cloud → local")
        print("  [4]  Sync status")
        print("  [5]  Safe mode toggle")
        print("  [0]  Back")
        _divider()
        choice = _prompt("Maint")

        if choice == "0":
            break

        elif choice == "1":
            _submenu_apm()

        elif choice == "2":
            print(f"  → {sync_push()}")

        elif choice == "3":
            print(f"  → {sync_pull()}")

        elif choice == "4":
            st = sync_status()
            for k, v in st.items():
                print(f"    {k:<16} {v}")

        elif choice == "5":
            safe = SafeMode()
            current = safe.status()["safe_mode"]
            if current:
                safe.disable()
                print("  → Safe mode disabled.")
            else:
                safe.enable()
                print("  → Safe mode enabled.")

        else:
            print(f"  Unknown option: {choice}")


def _submenu_apm():
    _header("6.1 — Package Manager (APM)")
    while True:
        installed = list_packages()
        _sub_header("APM")
        print(f"  Installed packages: {len(installed)}")
        print()
        print("  [1]  List packages")
        print("  [2]  Install package")
        print("  [3]  Remove package")
        print("  [4]  Update all packages")
        print("  [0]  Back")
        _divider()
        choice = _prompt("APM")

        if choice == "0":
            break
        elif choice == "1":
            pkgs = list_packages()
            if pkgs:
                for name, info in pkgs.items():
                    print(f"    {name:<20} v{info['version']}")
            else:
                print("  No packages installed.")
        elif choice == "2":
            pkg = input("  Package name: ").strip()
            if pkg:
                print(f"  → {install_package(pkg)}")
        elif choice == "3":
            pkg = input("  Package name: ").strip()
            if pkg:
                print(f"  → {remove_package(pkg)}")
        elif choice == "4":
            print(f"  → {update_packages()}")
        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 7 — System Info
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_system_info(env_ctx, session_start):
    _header("7 — System Info")

    while True:
        _sub_header("System Info")
        print("  [1]  Full diagnostics report")
        print("  [2]  Session summary")
        print("  [3]  Identity info")
        print("  [4]  Version info")
        print("  [5]  View system log")
        print("  [0]  Back")
        _divider()
        choice = _prompt("SysInfo")

        if choice == "0":
            break
        elif choice == "1":
            print(full_report())
        elif choice == "2":
            print(session_summary(session_start))
        elif choice == "3":
            ident = load_identity()
            for k, v in ident.items():
                print(f"    {k:<16} {v}")
        elif choice == "4":
            ver = load_version()
            for k, v in ver.items():
                print(f"    {k:<16} {v}")
        elif choice == "5":
            print(read_log())
        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 8 — Sync & Jobs
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_sync_jobs(env_ctx):
    _header("8 — Sync & Jobs")
    scheduler = env_ctx.get("scheduler") or JobScheduler()

    while True:
        procs = scheduler.status()["processes"]
        _sub_header("Sync & Jobs")
        print(f"  Active jobs: {len(procs)}")
        print()
        print("  [1]  Sync push (local → cloud)")
        print("  [2]  Sync pull (cloud → local)")
        print("  [3]  Sync status")
        print("  [4]  Show active jobs / processes")
        print("  [0]  Back")
        _divider()
        choice = _prompt("Sync")

        if choice == "0":
            break
        elif choice == "1":
            print(f"  → {sync_push()}")
        elif choice == "2":
            print(f"  → {sync_pull()}")
        elif choice == "3":
            st = sync_status()
            for k, v in st.items():
                print(f"    {k:<16} {v}")
        elif choice == "4":
            if procs:
                for p in procs:
                    print(f"    {p}")
            else:
                print("  No active jobs.")
        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-menu 9 — Settings
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_settings(env_ctx):
    _header("9 — Settings")

    while True:
        boot_mode = env_ctx.get("boot_mode", "unknown")
        net_mode  = env_ctx.get("net_mode", "offline")
        _sub_header("Settings")
        print(f"  Boot mode  : {boot_mode}")
        print(f"  Net mode   : {net_mode}")
        print()
        print("  [1]  Change boot mode (restart required)")
        print("  [2]  Change network mode")
        print("  [3]  Reset to defaults")
        print("  [0]  Back")
        _divider()
        choice = _prompt("Settings")

        if choice == "0":
            break

        elif choice == "1":
            print("  Boot modes: vhost | shared | custom")
            new_mode = input("  New boot mode: ").strip()
            if new_mode in ("vhost", "shared", "custom"):
                env_ctx["boot_mode"] = new_mode
                write_log(f"Boot mode changed to {new_mode} (pending restart)")
                print(f"  → Boot mode set to '{new_mode}' (takes effect on next boot).")
            else:
                print("  → Unknown boot mode.")

        elif choice == "2":
            vnet = env_ctx.get("vnet") or VNet()
            new_mode = input("  Network mode [online/offline/degraded]: ").strip()
            result = vnet.set_mode(new_mode)
            print(f"  → {result}")
            env_ctx["net_mode"] = vnet.mode

        elif choice == "3":
            vnet = env_ctx.get("vnet") or VNet()
            vnet.set_mode("offline")
            env_ctx["net_mode"] = "offline"
            print("  → Settings reset to defaults.")

        else:
            print(f"  Unknown option: {choice}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main menu entry point
# ═══════════════════════════════════════════════════════════════════════════════

def launch_menu(env_ctx=None):
    """
    Display the AURa OS Operator Console main menu (1-9).

    Parameters
    ----------
    env_ctx : dict | None
        Runtime context from boot_sequence + boot_menu.  If None (legacy
        call path), a minimal context is built from scratch.
    """
    if env_ctx is None:
        vfs = HybridVFS()
        vfs.ensure_paths()
        env_ctx = {
            "host":       {"os": "Unknown", "cpu_arch": "Unknown", "features": []},
            "vfs":        vfs,
            "vnet":       VNet(),
            "cloud":      CloudLink(),
            "scheduler":  JobScheduler(),
            "safe":       SafeMode(),
            "boot_mode":  "unknown",
            "net_mode":   "offline",
        }

    session_start = datetime.datetime.now()
    write_log("Main menu launched")

    while True:
        boot_mode = env_ctx.get("boot_mode", "unknown")
        net_mode  = env_ctx.get("net_mode", "offline")

        print()
        print("  ╔══════════════════════════════════════════╗")
        print("  ║     AURa OS — Operator Console           ║")
        print("  ╚══════════════════════════════════════════╝")
        print(f"  {aura_status_line()}")
        print(f"  Mode : {boot_mode}   Network : {net_mode}")
        print()
        print("  ┌─────────────────────────────────────────┐")
        print("  │  [1]  Shell Console                     │")
        print("  │  [2]  Main Host                         │")
        print("  │  [3]  Virtual Host (vHost)              │")
        print("  │  [4]  Virtual CPU (vCPU)                │")
        print("  │  [5]  Virtual Cloud (vCloud)            │")
        print("  │  [6]  Maintenance Tools                 │")
        print("  │  [7]  System Info                       │")
        print("  │  [8]  Sync & Jobs                       │")
        print("  │  [9]  Settings                          │")
        print("  │  [0]  Exit                              │")
        print("  └─────────────────────────────────────────┘")
        print()

        choice = _prompt()

        if choice == "0":
            print()
            print(session_summary(session_start))
            write_log("Operator console exited")
            print("  Exiting AURa OS…")
            break

        elif choice == "1":
            _menu_shell()

        elif choice == "2":
            _menu_main_host(env_ctx)

        elif choice == "3":
            _menu_vhost(env_ctx)

        elif choice == "4":
            _menu_vcpu(env_ctx)

        elif choice == "5":
            _menu_vcloud(env_ctx)

        elif choice == "6":
            _menu_maintenance()

        elif choice == "7":
            _menu_system_info(env_ctx, session_start)

        elif choice == "8":
            _menu_sync_jobs(env_ctx)

        elif choice == "9":
            _menu_settings(env_ctx)

        else:
            print(f"  Unknown option '{choice}'. Enter 0–9.")
