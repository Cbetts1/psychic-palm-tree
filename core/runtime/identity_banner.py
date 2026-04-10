import os
import json
from core.runtime.identity import load_identity
from core.runtime.logs import write_log
from core.runtime.scheduler import JobScheduler
from core.runtime.sync import sync_status

def aura_banner():
    ident = load_identity()
    return f"""
────────────────────────────────────────
        A U R a   O S   v0.9
────────────────────────────────────────
 Device UUID : {ident["device_uuid"]}
 Cloud UUID  : {ident["cloud_uuid"]}
────────────────────────────────────────
"""

def aura_status_line():
    scheduler = JobScheduler()
    sync = sync_status()
    cpu = scheduler.status()["cpu"]
    return f"[CPU {cpu['load']*100:.0f}%]  [Jobs {len(scheduler.status()['processes'])}]  [Cloud {sync['cloud_uuid']}]"

def print_boot_banner():
    banner = aura_banner()
    write_log("Boot banner displayed")
    print(banner)
