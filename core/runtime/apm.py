import os
import json
import uuid
from core.runtime.logs import write_log

PKG_ROOT = "/aura/local/packages"
REGISTRY = "/aura/cloud/packages"
META = "/aura/local/cache/packages.json"

def _ensure_dirs():
    os.makedirs(PKG_ROOT, exist_ok=True)
    os.makedirs(REGISTRY, exist_ok=True)
    if not os.path.exists(META):
        with open(META, "w") as f:
            json.dump({"installed": {}}, f)

def _load_meta():
    _ensure_dirs()
    with open(META, "r") as f:
        return json.load(f)

def _save_meta(meta):
    with open(META, "w") as f:
        json.dump(meta, f)

def list_packages():
    meta = _load_meta()
    return meta["installed"]

def install_package(name):
    _ensure_dirs()
    meta = _load_meta()

    pkg_id = str(uuid.uuid4())
    pkg_path = os.path.join(PKG_ROOT, name)
    os.makedirs(pkg_path, exist_ok=True)

    meta["installed"][name] = {"id": pkg_id, "version": "1.0.0"}
    _save_meta(meta)

    write_log(f"Package installed: {name}")
    return f"Installed {name}"

def remove_package(name):
    meta = _load_meta()
    if name not in meta["installed"]:
        return "Package not installed"

    pkg_path = os.path.join(PKG_ROOT, name)
    if os.path.exists(pkg_path):
        for root, dirs, files in os.walk(pkg_path, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(pkg_path)

    del meta["installed"][name]
    _save_meta(meta)

    write_log(f"Package removed: {name}")
    return f"Removed {name}"

def update_packages():
    meta = _load_meta()
    for name in meta["installed"]:
        meta["installed"][name]["version"] = "1.0.1"
    _save_meta(meta)
    write_log("Packages updated")
    return "All packages updated"
