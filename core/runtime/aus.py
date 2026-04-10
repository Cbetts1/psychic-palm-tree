from core.runtime.version import load_version, save_version, CHANNELS
from core.runtime.logs import write_log

def check_update():
    v = load_version()
    channel = v.get("channel", "stable")
    latest = CHANNELS.get(channel, v["version"])
    available = latest != v["version"]
    write_log(f"AUS check: current={v['version']} latest={latest} channel={channel}")
    return {
        "current": v["version"],
        "latest": latest,
        "channel": channel,
        "update_available": available,
    }

def apply_update():
    info = check_update()
    if not info["update_available"]:
        return f"Already up to date ({info['current']})"
    v = load_version()
    v["rollback"] = v["version"]
    v["version"] = info["latest"]
    save_version(v)
    write_log(f"AUS applied: {info['current']} → {info['latest']}")
    return f"Updated: {info['current']} → {info['latest']}"

def rollback_update():
    v = load_version()
    if not v.get("rollback"):
        return "No rollback target available"
    prev = v["version"]
    v["version"] = v["rollback"]
    v["rollback"] = None
    save_version(v)
    write_log(f"AUS rollback: {prev} → {v['version']}")
    return f"Rolled back: {prev} → {v['version']}"

def set_channel(channel):
    if channel not in CHANNELS:
        return f"Unknown channel '{channel}'. Available: {', '.join(CHANNELS)}"
    v = load_version()
    old = v.get("channel", "stable")
    v["channel"] = channel
    save_version(v)
    write_log(f"AUS channel changed: {old} → {channel}")
    return f"Channel: {old} → {channel}  (latest in channel: {CHANNELS[channel]})"

def list_channels():
    v = load_version()
    current = v.get("channel", "stable")
    lines = []
    for name, ver in CHANNELS.items():
        marker = "  ◀ active" if name == current else ""
        lines.append(f"  {name:<8} {ver}{marker}")
    return "\n".join(lines)
