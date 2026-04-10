import platform as _platform
import subprocess


def detect_capabilities():
    features = ["termux", "user-space"]
    arch = _platform.machine()

    # Try to read real Android version via getprop
    android_ver = "unknown"
    try:
        result = subprocess.run(
            ["getprop", "ro.build.version.release"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            android_ver = result.stdout.strip()
    except Exception:
        pass

    # Try to detect available Termux features
    try:
        result = subprocess.run(
            ["termux-info"], capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0:
            features.append("termux-api")
    except Exception:
        pass

    return {
        "os":       f"Android {android_ver}",
        "cpu_arch": arch,
        "python":   _platform.python_version(),
        "node":     _platform.node(),
        "features": features,
    }
