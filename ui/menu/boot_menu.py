"""
boot_menu.py — AURa OS pre-boot host/environment selection.

Presents the three-way boot choice before the main operator console:
  1. Detach Main Host  — standalone virtual environment
  2. Stay with Host    — shared / bridge mode
  3. Customize         — configure preferences before launching
"""

from core.runtime.logs import write_log
from core.runtime.identity_banner import aura_status_line


# ── Boot mode constants ───────────────────────────────────────────────────────

BOOT_MODE_VHOST  = "vhost"    # detached virtual host
BOOT_MODE_SHARED = "shared"   # joint host+virtual
BOOT_MODE_CUSTOM = "custom"   # user-configured


# ── Customise sub-menu ────────────────────────────────────────────────────────

def _customize_menu(env_ctx):
    """Let the user tweak options before launch; returns (possibly modified) env_ctx."""
    while True:
        print()
        print("  ┌─────────────────────────────────────────┐")
        print("  │  AURa OS — Customize Boot Options       │")
        print("  └─────────────────────────────────────────┘")
        print()
        net_mode = env_ctx.get("net_mode", "offline")
        host_os  = env_ctx["host"].get("os", "Unknown")
        print(f"  [1]  Network mode      : {net_mode}")
        print(f"  [2]  Host OS override  : {host_os}")
        print(f"  [3]  Safe mode         : {env_ctx.get('safe_mode', True)}")
        print()
        print(f"  [0]  Back / Launch with current settings")
        print()
        choice = input("  Select option: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            new_mode = input("  Network mode [online/offline/degraded]: ").strip()
            vnet = env_ctx.get("vnet")
            if vnet:
                result = vnet.set_mode(new_mode)
                print(f"  → {result}")
                env_ctx["net_mode"] = vnet.mode
            else:
                print("  → VNet not available.")

        elif choice == "2":
            new_os = input("  Enter host OS label: ").strip()
            if new_os:
                env_ctx["host"] = dict(env_ctx["host"])
                env_ctx["host"]["os"] = new_os
                print(f"  → Host OS set to '{new_os}'")

        elif choice == "3":
            safe = env_ctx.get("safe")
            if safe:
                current = safe.status()["safe_mode"]
                if current:
                    safe.disable()
                    env_ctx["safe_mode"] = False
                    print("  → Safe mode disabled.")
                else:
                    safe.enable()
                    env_ctx["safe_mode"] = True
                    print("  → Safe mode enabled.")
            else:
                print("  → Safe mode module not available.")

        else:
            print(f"  Unknown option: {choice}")

    return env_ctx


# ── Public entry point ────────────────────────────────────────────────────────

def show_boot_menu(env_ctx):
    """
    Display the boot selection menu and return the chosen boot mode string.

    Parameters
    ----------
    env_ctx : dict  — boot context produced by run_boot_sequence()

    Returns
    -------
    str  — one of BOOT_MODE_VHOST | BOOT_MODE_SHARED | BOOT_MODE_CUSTOM
    """
    host_os  = env_ctx["host"].get("os", "Unknown")
    net_mode = env_ctx.get("net_mode", "offline")

    while True:
        print()
        print("  ╔══════════════════════════════════════════╗")
        print("  ║     AURa OS — Boot Configuration         ║")
        print("  ╚══════════════════════════════════════════╝")
        print()
        print(f"  Host : {host_os}   Network : {net_mode}")
        print()
        print("  ┌─────────────────────────────────────────┐")
        print("  │  How would you like to start?           │")
        print("  ├─────────────────────────────────────────┤")
        print("  │  [1]  Detach Main Host                  │")
        print("  │       Stabilize virtual host and load   │")
        print("  │       the isolated virtual environment  │")
        print("  │                                         │")
        print("  │  [2]  Stay with Host — Shared System    │")
        print("  │       Bridge host and virtual env as    │")
        print("  │       a joint system                    │")
        print("  │                                         │")
        print("  │  [3]  Customize                         │")
        print("  │       Configure host / environment      │")
        print("  │       options before launching          │")
        print("  └─────────────────────────────────────────┘")
        print()
        print("  " + aura_status_line())
        print()
        choice = input("  Select [1-3]: ").strip()

        if choice == "1":
            write_log("Boot mode selected: vhost (detached)")
            print()
            print("  → Detaching main host…")
            print("  → Stabilizing virtual host…")
            print("  → Loading virtual environment…")
            print("  → OS online in virtual mode.")
            print()
            return BOOT_MODE_VHOST

        elif choice == "2":
            write_log("Boot mode selected: shared (joint)")
            print()
            print("  → Bridging host and virtual environment…")
            print("  → Joint system online.")
            print()
            return BOOT_MODE_SHARED

        elif choice == "3":
            env_ctx = _customize_menu(env_ctx)
            # After customising, loop back to show boot menu again
            continue

        else:
            print(f"  Invalid selection '{choice}'. Please enter 1, 2, or 3.")
