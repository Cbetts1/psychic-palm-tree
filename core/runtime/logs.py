import os
import datetime
from core.runtime.paths import aura_path

LOG_PATH = aura_path("local", "cache", "system.log")

def _ensure_log():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            f.write("AURa System Log Initialized\n")

def write_log(msg):
    _ensure_log()
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def read_log():
    _ensure_log()
    with open(LOG_PATH, "r") as f:
        return f.read()
