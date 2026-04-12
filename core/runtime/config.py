import os
import json
from core.runtime.paths import aura_path

CONFIG_PATH = aura_path("local", "cache", "aura.json")

_DEFAULTS = {
    "cloud": {
        "endpoint": "",
        "timeout": 5,
        "api_key": None,
    },
    "workers": {
        "enabled": ["image", "video", "apk", "docs", "models", "index", "search"],
        "max_concurrent": 4,
    },
    "update": {
        "channel": "stable",
        "auto_check": False,
    },
    "storage": {
        "cloud_root":   aura_path("cloud"),
        "local_cache":  aura_path("local", "cache"),
        "packages":     aura_path("local", "packages"),
        "models":       aura_path("local", "cache", "models"),
    },
    "network": {
        "mode": "auto",
        "fallback": "offline",
    },
    "node": {
        "enabled":            True,
        "name":               "",
        "cc_url":             "",
        "token":              "",
        "heartbeat_interval": 30,
    },
    "command_channel": {
        "enabled": True,
        "port":    8731,
        "bind":    "0.0.0.0",
        "token":   "",
    },
    "safe_mode": False,
}


def _ensure_dir():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)


def load_config():
    _ensure_dir()
    if not os.path.exists(CONFIG_PATH):
        save_config(_DEFAULTS)
        return {k: (dict(v) if isinstance(v, dict) else v) for k, v in _DEFAULTS.items()}
    with open(CONFIG_PATH, "r") as f:
        saved = json.load(f)
    # Deep merge: saved values win, but missing keys fall back to defaults
    cfg = {}
    for section, default in _DEFAULTS.items():
        if isinstance(default, dict):
            cfg[section] = {**default, **saved.get(section, {})}
        else:
            cfg[section] = saved.get(section, default)
    return cfg


def save_config(cfg):
    _ensure_dir()
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get(section, key=None):
    cfg = load_config()
    if key is None:
        return cfg.get(section)
    return cfg.get(section, {}).get(key)


def set_value(section, key, value):
    cfg = load_config()
    if key is None:
        # Top-level scalar (e.g. safe_mode)
        cfg[section] = value
    else:
        if section not in cfg or not isinstance(cfg[section], dict):
            cfg[section] = {}
        cfg[section][key] = value
    save_config(cfg)


def show_config():
    cfg = load_config()
    lines = ["AURa Config (aura.json):"]
    for section, val in cfg.items():
        if isinstance(val, dict):
            lines.append(f"  [{section}]")
            for k, v in val.items():
                lines.append(f"    {k} = {v}")
        else:
            lines.append(f"  {section} = {val}")
    return "\n".join(lines)
