"""
paths.py — AURa OS root path resolution.

Priority order:
  1. $AURA_ROOT environment variable (explicit override)
  2. /aura          — if it already exists and is writable
  3. ~/.aura        — universal fallback (always works)
"""

import os


def _resolve_root():
    # 1. Explicit env override
    env = os.environ.get("AURA_ROOT", "").strip()
    if env:
        os.makedirs(env, exist_ok=True)
        return env

    # 2. System root exists and is writable
    if os.path.isdir("/aura") and os.access("/aura", os.W_OK):
        return "/aura"

    # 3. Try to create /aura (root / privileged install)
    try:
        os.makedirs("/aura", exist_ok=True)
        if os.access("/aura", os.W_OK):
            return "/aura"
    except PermissionError:
        pass

    # 4. User-home fallback — always create it
    home_root = os.path.join(os.path.expanduser("~"), ".aura")
    os.makedirs(home_root, exist_ok=True)
    return home_root


# Resolved once at import time; callers can override via AURA_ROOT
AURA_ROOT = _resolve_root()


def aura_path(*parts):
    """Return an absolute path inside the AURa root directory."""
    return os.path.join(AURA_ROOT, *parts)
