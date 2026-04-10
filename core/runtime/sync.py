import os
import shutil
from core.runtime.identity import load_identity
from core.runtime.logs import write_log
from core.runtime.paths import aura_path

CLOUD_ROOT  = aura_path("cloud")
LOCAL_CACHE = aura_path("local", "cache")

def sync_push():
    write_log("Sync push started")
    for root, dirs, files in os.walk(LOCAL_CACHE):
        for f in files:
            src = os.path.join(root, f)
            dst = src.replace(LOCAL_CACHE, CLOUD_ROOT)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    write_log("Sync push completed")
    return "Push complete"

def sync_pull():
    write_log("Sync pull started")
    for root, dirs, files in os.walk(CLOUD_ROOT):
        for f in files:
            src = os.path.join(root, f)
            dst = src.replace(CLOUD_ROOT, LOCAL_CACHE)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    write_log("Sync pull completed")
    return "Pull complete"

def sync_status():
    ident = load_identity()
    return {
        "device_uuid": ident["device_uuid"],
        "cloud_uuid": ident["cloud_uuid"],
        "cloud_path": CLOUD_ROOT,
        "local_cache": LOCAL_CACHE
    }
