from core.runtime.identity_banner import print_boot_banner
from core.runtime.identity_banner import aura_status_line
from core.runtime.vnet import VNet
from core.runtime.cloud_link import CloudLink
from core.runtime.safe_mode import SafeMode
from core.runtime.vfs import HybridVFS
from core.runtime.logs import write_log
from core.runtime.version import load_version
import importlib.util
import os

def _load_bridge(path):
    platform = os.path.basename(os.path.dirname(path))
    module_name = f"host_bridge_{platform}_detect_capabilities"
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def detect_host():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        import termux  # noqa: F401
        path = os.path.join(repo_root, "host-bridge", "android", "detect_capabilities.py")
    except Exception:
        path = os.path.join(repo_root, "host-bridge", "linux", "detect_capabilities.py")
    bridge = _load_bridge(path)
    return bridge.detect_capabilities()

def main():
    print_boot_banner()

    ver = load_version()
    write_log(f"AURa version {ver['version']} channel={ver['channel']}")
    print(f"Version : {ver['version']}  [{ver['channel']}]")

    host = detect_host()
    write_log(f"Host detected: {host['os']} ({host['cpu_arch']})")
    print(f"Host    : {host['os']} ({host['cpu_arch']})")

    vnet = VNet()
    cloud = CloudLink()
    safe = SafeMode()
    vfs = HybridVFS()
    vfs.ensure_paths()

    cloud.connect()
    write_log("Cloud link checked")

    print("Boot OK — launching menu…")
    print(aura_status_line())

    from ui.menu.main_menu import launch_menu
    launch_menu()

if __name__ == "__main__":
    main()
