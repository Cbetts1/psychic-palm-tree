from core.runtime.apm import list_packages, install_package, remove_package, update_packages
from core.runtime.identity_banner import aura_status_line
from core.shell.main_shell import start_shell
from core.runtime.scheduler import JobScheduler
from core.runtime.ai_interface import ai_chat
from core.runtime.vfs import HybridVFS
from core.runtime.logs import read_log
from core.runtime.sync import sync_push, sync_pull, sync_status

def launch_menu():
    scheduler = JobScheduler()
    vfs = HybridVFS()
    vfs.ensure_paths()

    while True:
        print(aura_status_line())
        print("""
AURa OS — Operator Console
────────────────────────────────────────
[1] Shell Console
[2] Cloud Jobs (list)
[3] Filesystem Mounts
[4] AI Interface
[5] System Logs
[6] Diagnostics Panel
[7] Sync Status
[8] Sync Push
[9] Sync Pull
[10] Package Manager
[0] Exit
────────────────────────────────────────
        """)

        choice = input("Select option: ").strip()

        if choice == "0":
            print("Exiting AURa…")
            break

        elif choice == "1":
            start_shell()

        elif choice == "2":
            print("Processes:", scheduler.status()["processes"])

        elif choice == "3":
            print("Mounts:", vfs.list_mounts())

        elif choice == "4":
            ai_chat()

        elif choice == "5":
            print(read_log())

        elif choice == "6":
            print("CPU:", scheduler.status()["cpu"])
            print("Processes:", scheduler.status()["processes"])
            print("Mounts:", vfs.list_mounts())

        elif choice == "7":
            print(sync_status())

        elif choice == "8":
            print(sync_push())

        elif choice == "9":
            print(sync_pull())

        elif choice == "10":
            print("Installed:", list_packages())
            print("Install with: apm-install <pkg>")
            print("Remove with: apm-remove <pkg>")
            print("Update with: apm-update")

        else:
            print(f"Selected option {choice} — not implemented yet.")
