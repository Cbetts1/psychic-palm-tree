from core.runtime.identity_banner import print_boot_banner
from core.runtime.identity_banner import aura_status_line
from core.runtime.vnet import VNet
from core.runtime.cloud_link import CloudLink
from core.runtime.safe_mode import SafeMode
from core.runtime.vfs import HybridVFS
from core.runtime.logs import write_log
import importlib

def detect_host():
    try:
        import termux
        bridge = importlib.import_module("host-bridge.android.detect_capabilities")
    except Exception:
        bridge = importlib.import_module("host-bridge.linux.detect_capabilities")
    return bridge.detect_capabilities()

def main():
    print_boot_banner()

    host = detect_host()
    write_log(f"Host detected: {host[os]} ({host[cpu_arch]})")
    print(f"Host: {host[os]} ({host[cpu_arch]})")

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
