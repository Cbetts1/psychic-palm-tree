import os
import json
from core.runtime.paths import aura_path

VERSION_PATH = aura_path("local", "cache", "version.json")

CHANNELS = {
    "stable": "0.9.0",
    "beta":   "0.9.5",
    "dev":    "0.10.0-dev",
}

def _ensure_dir():
    os.makedirs(os.path.dirname(VERSION_PATH), exist_ok=True)

def load_version():
    _ensure_dir()
    if not os.path.exists(VERSION_PATH):
        v = {"version": CHANNELS["stable"], "channel": "stable", "rollback": None}
        with open(VERSION_PATH, "w") as f:
            json.dump(v, f, indent=2)
        return v
    with open(VERSION_PATH, "r") as f:
        return json.load(f)

def save_version(v):
    _ensure_dir()
    with open(VERSION_PATH, "w") as f:
        json.dump(v, f, indent=2)

def current_version():
    return load_version()["version"]

def current_channel():
    return load_version()["channel"]
