import os
import json
from core.runtime.logs import write_log

VALID_CHANNELS = ("stable", "edge", "dev")
VERSION_PATH = "/aura/local/cache/version.json"

_DEFAULT = {
    "version": "0.9.0",
    "channel": "stable",
    "history": []
}

_MAX_HISTORY = 20

def _ensure_dir():
    os.makedirs(os.path.dirname(VERSION_PATH), exist_ok=True)

def _load():
    _ensure_dir()
    if not os.path.exists(VERSION_PATH):
        _save(_DEFAULT.copy())
    with open(VERSION_PATH, "r") as f:
        return json.load(f)

def _save(data):
    _ensure_dir()
    with open(VERSION_PATH, "w") as f:
        json.dump(data, f)


class AUSVersion:
    """AURa Update System — manages version channels and rollback."""

    def status(self):
        data = _load()
        return {"version": data["version"], "channel": data["channel"]}

    def set_channel(self, channel):
        if channel not in VALID_CHANNELS:
            return {"error": f"Unknown channel '{channel}'. Valid: {VALID_CHANNELS}"}
        data = _load()
        data["channel"] = channel
        _save(data)
        write_log(f"AUS channel changed to {channel}")
        return {"channel": channel}

    def update(self, new_version):
        data = _load()
        old_version = data["version"]
        data["history"].append({"version": old_version, "channel": data["channel"]})
        if len(data["history"]) > _MAX_HISTORY:
            data["history"] = data["history"][-_MAX_HISTORY:]
        data["version"] = new_version
        _save(data)
        write_log(f"AUS update: {old_version} → {new_version}")
        return {"previous": old_version, "current": new_version}

    def rollback(self):
        data = _load()
        if not data["history"]:
            return {"error": "No previous version to roll back to"}
        prev = data["history"].pop()
        current = data["version"]
        data["version"] = prev["version"]
        data["channel"] = prev["channel"]
        _save(data)
        write_log(f"AUS rollback: {current} → {prev['version']}")
        return {"rolled_back_from": current, "current": prev["version"]}

    def history(self):
        data = _load()
        return data["history"]
