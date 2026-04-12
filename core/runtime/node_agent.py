"""
node_agent.py — AURa OS virtual-node agent.

Responsibilities
----------------
- Maintain this node's virtual identity (node_id, name, capabilities).
- Register with a remote Command Center (CC) over HTTP.
- Run a background heartbeat thread that POSTs to CC periodically.
- Execute commands received from the command channel.
- Manage peer nodes via the PeerRegistry.

All network calls use the stdlib (urllib) — no external dependencies.
"""

import json
import os
import threading
import urllib.request
import urllib.error
import datetime

from core.runtime.identity      import load_identity
from core.runtime.version       import load_version
from core.runtime.config        import get as cfg_get, set_value
from core.runtime.health        import get_health
from core.runtime.logs          import write_log
from core.runtime.paths         import AURA_ROOT
from core.runtime.peer_registry import (
    list_peers, register_peer, remove_peer, ping_all_peers,
)

# ── Capabilities this node exposes to the Command Center ─────────────────────

NODE_CAPABILITIES = [
    "shell",
    "apm",
    "sync",
    "vfs",
    "vnet",
    "ai-interface",
    "cloud-workers",
    "builder",
    "health-api",
    "peer-mesh",
]


# ── NodeAgent ─────────────────────────────────────────────────────────────────

class NodeAgent:
    """Central virtual-node agent for AURa OS."""

    def __init__(self):
        ident    = load_identity()
        ver      = load_version()
        cfg_name = cfg_get("node", "name") or ""

        self.node_id      = ident["device_uuid"]
        self.name         = cfg_name or f"aura-{self.node_id[:8]}"
        self.version      = ver["version"]
        self.channel      = ver["channel"]
        self.capabilities = list(NODE_CAPABILITIES)
        self.started_at   = datetime.datetime.now().isoformat()
        self.registered   = False

        self._stop_event = threading.Event()
        self._hb_thread  = None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _cc_url(self):
        return (cfg_get("node", "cc_url") or "").rstrip("/")

    def _token(self):
        return cfg_get("node", "token") or ""

    def _cc_headers(self):
        headers = {"Content-Type": "application/json"}
        tok = self._token()
        if tok:
            headers["Authorization"] = f"Bearer {tok}"
        return headers

    # ── Registration ──────────────────────────────────────────────────────────

    def register_with_cc(self, timeout=5):
        """
        POST /register to the configured Command Center.

        Returns True on success, False otherwise.
        If the CC returns a cloud_uuid it is persisted via set_cloud_uuid().
        """
        cc = self._cc_url()
        if not cc:
            write_log("NodeAgent: no cc_url configured — skipping registration")
            return False

        local_port = int(cfg_get("command_channel", "port") or 8731)
        payload = json.dumps({
            "node_id":       self.node_id,
            "name":          self.name,
            "version":       self.version,
            "channel":       self.channel,
            "capabilities":  self.capabilities,
            "api_port":      local_port,
            "registered_at": self.started_at,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{cc}/register",
                data=payload,
                headers=self._cc_headers(),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("cloud_uuid"):
                    from core.runtime.identity import set_cloud_uuid
                    set_cloud_uuid(data["cloud_uuid"])
            self.registered = True
            write_log(f"NodeAgent registered with CC: {cc}")
            return True
        except Exception as exc:
            write_log(f"NodeAgent registration failed: {exc}")
            return False

    # ── Heartbeat ─────────────────────────────────────────────────────────────

    def _heartbeat_payload(self):
        h = get_health()
        return {
            "node_id":   self.node_id,
            "name":      self.name,
            "version":   self.version,
            "timestamp": datetime.datetime.now().isoformat(),
            "health": {
                "status":   h["status"],
                "cpu_pct":  h["cpu"]["load_pct"],
                "mem_pct":  h["memory"]["used_pct"],
                "disk_pct": h["disk"]["used_pct"],
            },
        }

    def _send_heartbeat(self, timeout=5):
        cc = self._cc_url()
        if not cc:
            return
        payload = json.dumps(self._heartbeat_payload()).encode("utf-8")
        try:
            req = urllib.request.Request(
                f"{cc}/heartbeat",
                data=payload,
                headers=self._cc_headers(),
                method="POST",
            )
            urllib.request.urlopen(req, timeout=timeout)
            write_log("NodeAgent heartbeat sent")
        except Exception as exc:
            write_log(f"NodeAgent heartbeat failed: {exc}")

    def _heartbeat_loop(self):
        interval = int(cfg_get("node", "heartbeat_interval") or 30)
        while not self._stop_event.wait(interval):
            self._send_heartbeat()

    def start_heartbeat(self):
        """Start the background heartbeat daemon thread."""
        if self._hb_thread and self._hb_thread.is_alive():
            return
        self._stop_event.clear()
        self._hb_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
            name="aura-heartbeat",
        )
        self._hb_thread.start()
        write_log("NodeAgent heartbeat thread started")

    def stop_heartbeat(self):
        """Signal the heartbeat thread to stop."""
        self._stop_event.set()
        write_log("NodeAgent heartbeat thread stopped")

    # ── Command dispatch ──────────────────────────────────────────────────────

    def execute_command(self, cmd, payload=None):
        """
        Dispatch an incoming command and return a result dict.

        Supported commands
        ------------------
        status           Full node status dict
        health           Health snapshot
        capabilities     List of capability strings
        version          Version / channel info
        apm-list         List installed packages
        apm-install      Install a package     (payload: {name})
        apm-remove       Remove a package      (payload: {name})
        sync-push        Push local → cloud
        sync-pull        Pull cloud → local
        log              Last N log lines      (payload: {lines: 50})
        peer-list        List known peers
        peer-add         Add a peer            (payload: {node_id, url[, capabilities]})
        peer-ping        Ping all peers
        peer-remove      Remove a peer         (payload: {node_id})
        build-worker     Generate a worker     (payload: {name})
        build-command    Generate a command    (payload: {name})
        build-config     Generate a config stub(payload: {name})
        restart          Return restart advisory
        """
        payload = payload or {}
        write_log(f"NodeAgent.execute_command: {cmd} payload={str(payload)[:80]}")

        try:
            if cmd == "status":
                return self.node_status()

            elif cmd == "health":
                return get_health()

            elif cmd == "capabilities":
                return {"capabilities": self.capabilities}

            elif cmd == "version":
                return load_version()

            # ── APM ───────────────────────────────────────────────────────────
            elif cmd == "apm-list":
                from core.runtime.apm import list_packages
                return {"packages": list_packages()}

            elif cmd == "apm-install":
                name = payload.get("name", "")
                if not name:
                    return {"error": "payload.name is required"}
                from core.runtime.apm import install_package
                return {"result": install_package(name)}

            elif cmd == "apm-remove":
                name = payload.get("name", "")
                if not name:
                    return {"error": "payload.name is required"}
                from core.runtime.apm import remove_package
                return {"result": remove_package(name)}

            # ── Sync ──────────────────────────────────────────────────────────
            elif cmd == "sync-push":
                from core.runtime.sync import sync_push
                return {"result": sync_push()}

            elif cmd == "sync-pull":
                from core.runtime.sync import sync_pull
                return {"result": sync_pull()}

            # ── Logs ──────────────────────────────────────────────────────────
            elif cmd == "log":
                from core.runtime.logs import read_log
                lines = int(payload.get("lines", 50))
                raw   = read_log()
                tail  = "\n".join(raw.splitlines()[-lines:])
                return {"log": tail}

            # ── Peer mesh ─────────────────────────────────────────────────────
            elif cmd == "peer-list":
                return {"peers": list_peers()}

            elif cmd == "peer-add":
                nid  = payload.get("node_id", "")
                url  = payload.get("url", "")
                if not nid or not url:
                    return {"error": "payload.node_id and payload.url are required"}
                caps = payload.get("capabilities", [])
                return {"peer": register_peer(nid, url, caps)}

            elif cmd == "peer-ping":
                return {"results": ping_all_peers()}

            elif cmd == "peer-remove":
                nid = payload.get("node_id", "")
                if not nid:
                    return {"error": "payload.node_id is required"}
                return {"result": remove_peer(nid)}

            # ── Builder ───────────────────────────────────────────────────────
            elif cmd == "build-worker":
                name = payload.get("name", "")
                if not name:
                    return {"error": "payload.name is required"}
                from core.runtime.builder import build_worker
                return build_worker(name)

            elif cmd == "build-command":
                name = payload.get("name", "")
                if not name:
                    return {"error": "payload.name is required"}
                from core.runtime.builder import build_command
                return build_command(name)

            elif cmd == "build-config":
                name = payload.get("name", "")
                if not name:
                    return {"error": "payload.name is required"}
                from core.runtime.builder import build_config_stub
                return build_config_stub(name)

            elif cmd == "restart":
                return {
                    "result":  "restart-advisory",
                    "message": "Restart this process to apply changes.",
                }

            else:
                return {"error": f"Unknown command: '{cmd}'"}

        except Exception as exc:
            write_log(f"NodeAgent command error [{cmd}]: {exc}")
            return {"error": str(exc)}

    # ── Status ────────────────────────────────────────────────────────────────

    def node_status(self):
        """Return a full node status dict."""
        ident = load_identity()
        ver   = load_version()
        h     = get_health()
        peers = list_peers()
        return {
            "node_id":      self.node_id,
            "name":         self.name,
            "version":      ver["version"],
            "channel":      ver["channel"],
            "capabilities": self.capabilities,
            "registered":   self.registered,
            "started_at":   self.started_at,
            "cloud_uuid":   ident.get("cloud_uuid"),
            "health":       h,
            "peer_count":   len(peers),
            "aura_root":    AURA_ROOT,
        }


# ── Module-level singleton ────────────────────────────────────────────────────

_agent = None


def get_agent():
    """Return (creating if necessary) the module-level NodeAgent singleton."""
    global _agent
    if _agent is None:
        _agent = NodeAgent()
    return _agent
