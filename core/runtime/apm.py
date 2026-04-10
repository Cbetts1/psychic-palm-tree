import os
import json
import uuid
from core.runtime.logs import write_log

PKG_ROOT  = "/aura/local/packages"
REGISTRY  = "/aura/cloud/packages"
META_PATH = "/aura/local/cache/packages.json"

_PKG_SUBDIRS = ["workers", "commands", "assets", "hooks"]


def _ensure_dirs():
    os.makedirs(PKG_ROOT,  exist_ok=True)
    os.makedirs(REGISTRY,  exist_ok=True)
    if not os.path.exists(META_PATH):
        with open(META_PATH, "w") as f:
            json.dump({"installed": {}}, f, indent=2)


def _load_meta():
    _ensure_dirs()
    with open(META_PATH, "r") as f:
        return json.load(f)


def _save_meta(meta):
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)


def list_packages():
    return _load_meta()["installed"]


def install_package(name):
    _ensure_dirs()
    meta   = _load_meta()
    pkg_id = str(uuid.uuid4())

    # Create package directory structure (Developer Guide §6)
    pkg_path = os.path.join(PKG_ROOT, name)
    os.makedirs(pkg_path, exist_ok=True)
    for sub in _PKG_SUBDIRS:
        os.makedirs(os.path.join(pkg_path, sub), exist_ok=True)

    # Write manifest
    manifest = {
        "name":    name,
        "id":      pkg_id,
        "version": "1.0.0",
        "workers": [],
        "commands": [],
    }
    with open(os.path.join(pkg_path, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    meta["installed"][name] = {"id": pkg_id, "version": "1.0.0"}
    _save_meta(meta)
    write_log(f"Package installed: {name}")
    return f"Installed {name}"


def remove_package(name):
    meta = _load_meta()
    if name not in meta["installed"]:
        return f"Package '{name}' is not installed"

    pkg_path = os.path.join(PKG_ROOT, name)
    if os.path.exists(pkg_path):
        import shutil
        shutil.rmtree(pkg_path)

    del meta["installed"][name]
    _save_meta(meta)
    write_log(f"Package removed: {name}")
    return f"Removed {name}"


def update_packages():
    meta = _load_meta()
    for name in meta["installed"]:
        meta["installed"][name]["version"] = "1.0.1"
        pkg_path = os.path.join(PKG_ROOT, name, "manifest.json")
        if os.path.exists(pkg_path):
            with open(pkg_path, "r") as f:
                mf = json.load(f)
            mf["version"] = "1.0.1"
            with open(pkg_path, "w") as f:
                json.dump(mf, f, indent=2)
    _save_meta(meta)
    write_log("All packages updated")
    return "All packages updated to v1.0.1"

