import os
import platform as _platform


def detect_capabilities():
    features = ["user-space"]

    # Real desktop detection
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        features.append("desktop")

    # Container / VM detection
    if os.path.exists("/.dockerenv"):
        features.append("container")
    elif os.path.exists("/run/.containerenv"):
        features.append("container")

    # WSL detection
    uname = _platform.uname()
    if "microsoft" in uname.release.lower() or "wsl" in uname.release.lower():
        features.append("wsl")

    return {
        "os":      f"{_platform.system()} {_platform.release()}",
        "cpu_arch": _platform.machine(),
        "python":  _platform.python_version(),
        "node":    _platform.node(),
        "features": features,
    }
