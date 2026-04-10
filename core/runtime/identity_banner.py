import os
import json
from core.runtime.identity import load_identity
from core.runtime.logs import write_log
from core.runtime.scheduler import JobScheduler
from core.runtime.sync import sync_status
from core.runtime.version import load_version

def aura_banner():
    ident = load_identity()
    ver = load_version()
    cloud = ident["cloud_uuid"] or "unlinked"
    return f"""
────────────────────────────────────────
        A U R a   O S   v{ver['version']}
────────────────────────────────────────
 Device UUID : {ident["device_uuid"]}
 Cloud UUID  : {cloud}
 Channel     : {ver['channel']}
────────────────────────────────────────
"""

def aura_status_line():
    scheduler = JobScheduler()
    sync = sync_status()
    ver = load_version()
    cpu = scheduler.status()["cpu"]
    cloud = sync["cloud_uuid"] or "unlinked"
    return (
        f"[v{ver['version']}]"
        f"  [CPU {cpu['load']*100:.0f}%]"
        f"  [Jobs {len(scheduler.status()['processes'])}]"
        f"  [Cloud {cloud}]"
    )

def print_boot_banner():
    banner = aura_banner()
    write_log("Boot banner displayed")
    print(banner)
