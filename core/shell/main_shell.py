from core.runtime.apm import install_package, remove_package, list_packages, update_packages
from core.shell.commands import ls, cat, mounts, jobs
from core.runtime.scheduler import JobScheduler
from core.runtime.sync import sync_push, sync_pull, sync_status
from core.runtime.logs import read_log
from core.runtime.identity_banner import aura_status_line
from core.runtime.version import AUSVersion

def start_shell():
    print("AURa Shell — type \"exit\" to return")
    print(aura_status_line())

    scheduler = JobScheduler()
    aus = AUSVersion()

    while True:
        cmd = input("aura> ").strip().split()

        if not cmd:
            continue

        if cmd[0] == "exit":
            break

        elif cmd[0] == "ls":
            print(ls(cmd[1] if len(cmd) > 1 else "."))

        elif cmd[0] == "cat":
            print(cat(cmd[1]) if len(cmd) > 1 else "Usage: cat <file>")

        elif cmd[0] == "mounts":
            print(mounts())

        elif cmd[0] == "jobs":
            print(jobs(scheduler))

        elif cmd[0] == "log":
            print(read_log())

        elif cmd[0] == "sync-status":
            print(sync_status())

        elif cmd[0] == "sync-push":
            print(sync_push())

        elif cmd[0] == "sync-pull":
            print(sync_pull())

        elif cmd[0] == "apm-install":
            print(install_package(cmd[1]) if len(cmd) > 1 else "Usage: apm-install <pkg>")

        elif cmd[0] == "apm-remove":
            print(remove_package(cmd[1]) if len(cmd) > 1 else "Usage: apm-remove <pkg>")

        elif cmd[0] == "apm-list":
            print(list_packages())

        elif cmd[0] == "apm-update":
            print(update_packages())

        elif cmd[0] == "sys-version":
            print(aus.status())

        elif cmd[0] == "sys-channel":
            if len(cmd) < 2:
                print("Usage: sys-channel <stable|edge|dev>")
            else:
                result = aus.set_channel(cmd[1])
                if "error" in result:
                    print(f"Error: {result['error']}")
                else:
                    print(f"Channel set to: {result['channel']}")

        elif cmd[0] == "sys-update":
            if len(cmd) < 2:
                print("Usage: sys-update <version>")
            else:
                result = aus.update(cmd[1])
                print(f"Updated: {result['previous']} → {result['current']}")

        elif cmd[0] == "sys-rollback":
            print(aus.rollback())

        else:
            print(f"Unknown command: {cmd[0]}")

        print(aura_status_line())
