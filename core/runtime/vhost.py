from core.runtime.identity_banner import print_boot_banner
from core.runtime.identity_banner import aura_status_line
from core.runtime.vnet import VNet
from core.runtime.cloud_link import CloudLink
from core.runtime.vfs import HybridVFS
from core.runtime.logs import write_log
from core.runtime.version import load_version
from core.runtime.config import get as cfg_get
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


def _start_node_services():
    """
    Optionally start the node agent and command channel in background threads.
    Both are skipped silently if disabled in config or if the port is busy.
    """
    from core.runtime.node_agent      import get_agent
    from core.runtime.command_channel import start_command_channel

    agent  = get_agent()
    result = start_command_channel(node_agent=agent)

    if result:
        host, port = result
        write_log(f"Command channel active on {host}:{port}")
        print(f"  API     : http://127.0.0.1:{port}/  (command channel)")

    if cfg_get("node", "enabled"):
        agent.register_with_cc()
        agent.start_heartbeat()
        write_log(f"Node agent active: {agent.node_id}")

    return agent


def main():
    print_boot_banner()

    ver = load_version()
    write_log(f"AURa version {ver['version']} channel={ver['channel']}")
    print(f"  Version : {ver['version']}  [{ver['channel']}]")

    host = detect_host()
    write_log(f"Host detected: {host['os']} ({host['cpu_arch']})")
    print(f"  Host    : {host['os']} ({host['cpu_arch']})")

    vnet  = VNet()
    cloud = CloudLink()
    vfs   = HybridVFS()

    # ── Boot sequence stabilizer ──────────────────────────────────────────────
    from core.runtime.boot_sequence import run_boot_sequence
    env_ctx = run_boot_sequence(host, vnet, cloud, vfs)

    # ── Node agent + command channel ──────────────────────────────────────────
    agent = _start_node_services()
    env_ctx["node_agent"] = agent

    # ── Boot menu: choose host mode ───────────────────────────────────────────
    from ui.menu.boot_menu import show_boot_menu
    boot_mode = show_boot_menu(env_ctx)
    env_ctx["boot_mode"] = boot_mode
    write_log(f"Boot mode selected: {boot_mode}")

    # ── Operator console ──────────────────────────────────────────────────────
    from ui.menu.main_menu import launch_menu
    launch_menu(env_ctx)


if __name__ == "__main__":
    main()
