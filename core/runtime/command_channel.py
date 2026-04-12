"""
command_channel.py — AURa OS remote command channel.

Exposes a lightweight HTTP/JSON API so the Command Center (or any
authorised client) can query, control, and orchestrate this AURa node.

Endpoints
---------
GET  /                  Basic node info          (public)
GET  /health            Health metrics           (public)
GET  /capabilities      List capabilities        (public)
GET  /status            Full node status         (requires token)
GET  /peers             List known peers         (requires token)
POST /cmd               Execute a command        (requires token)
POST /peer/register     Register a sibling node  (requires token)

Auth
----
If `command_channel.token` is non-empty in config, every non-public
endpoint must supply:
    Authorization: Bearer <token>

The HTTP server runs in a background daemon thread — it does not block
the main operator console.

Termux / ARM64 note
-------------------
Uses only the Python standard library (http.server, socketserver,
threading).  No privileged port required; the default port is 8731.
"""

import json
import threading
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer

from core.runtime.config        import get as cfg_get
from core.runtime.logs          import write_log
from core.runtime.health        import get_health
from core.runtime.peer_registry import register_peer, list_peers


# ── Public (no-token) endpoints ───────────────────────────────────────────────

_PUBLIC_PATHS = {"/", "/health", "/capabilities"}


# ── Threaded HTTP server ──────────────────────────────────────────────────────

class _ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle each connection in a separate daemon thread."""
    daemon_threads    = True
    allow_reuse_address = True


# ── Request handler ───────────────────────────────────────────────────────────

class _AURaHandler(BaseHTTPRequestHandler):
    """Handle AURa command-channel HTTP requests."""

    # Injected before the server starts
    node_agent = None
    token      = ""

    # ── Logging ───────────────────────────────────────────────────────────────

    def log_message(self, fmt, *args):  # suppress default stderr noise
        write_log(f"CommandChannel [{self.address_string()}] {fmt % args}")

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _authorized(self):
        if not self.token:
            return True
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {self.token}"

    # ── Response helpers ──────────────────────────────────────────────────────

    def _send_json(self, code, obj):
        body = json.dumps(obj, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    # ── GET ───────────────────────────────────────────────────────────────────

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            from core.runtime.identity import load_identity
            from core.runtime.version  import load_version
            ident = load_identity()
            ver   = load_version()
            self._send_json(200, {
                "service": "aura-command-channel",
                "node_id": ident["device_uuid"],
                "version": ver["version"],
                "channel": ver["channel"],
            })

        elif path == "/health":
            self._send_json(200, get_health())

        elif path == "/capabilities":
            agent = self.node_agent
            caps  = agent.capabilities if agent else []
            self._send_json(200, {"capabilities": caps})

        elif path == "/status":
            if not self._authorized():
                return self._send_json(401, {"error": "Unauthorized"})
            agent = self.node_agent
            if agent is None:
                return self._send_json(503, {"error": "Node agent not ready"})
            self._send_json(200, agent.node_status())

        elif path == "/peers":
            if not self._authorized():
                return self._send_json(401, {"error": "Unauthorized"})
            self._send_json(200, {"peers": list_peers()})

        else:
            self._send_json(404, {"error": f"Not found: {path}"})

    # ── POST ──────────────────────────────────────────────────────────────────

    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/cmd":
            if not self._authorized():
                return self._send_json(401, {"error": "Unauthorized"})
            body  = self._read_body()
            cmd   = body.get("cmd", "")
            pldr  = body.get("payload", {})
            agent = self.node_agent
            if agent is None:
                return self._send_json(503, {"error": "Node agent not ready"})
            result = agent.execute_command(cmd, pldr)
            self._send_json(200, result)

        elif path == "/peer/register":
            if not self._authorized():
                return self._send_json(401, {"error": "Unauthorized"})
            body = self._read_body()
            nid  = body.get("node_id", "")
            url  = body.get("url", "")
            caps = body.get("capabilities", [])
            if not nid or not url:
                return self._send_json(400, {"error": "node_id and url required"})
            peer = register_peer(nid, url, caps)
            self._send_json(200, {"registered": peer})

        else:
            self._send_json(404, {"error": f"Not found: {path}"})


# ── Server lifecycle ──────────────────────────────────────────────────────────

_server_instance = None
_server_thread   = None


def start_command_channel(node_agent=None):
    """
    Start the command-channel HTTP server in a background daemon thread.

    Parameters
    ----------
    node_agent : NodeAgent | None
        If provided, injected into the request handler so /cmd, /status,
        and /capabilities can delegate to it.

    Returns
    -------
    (host, port) tuple on success, None if disabled or unable to bind.
    """
    global _server_instance, _server_thread

    if not cfg_get("command_channel", "enabled"):
        write_log("CommandChannel: disabled in config")
        return None

    port  = int(cfg_get("command_channel", "port")  or 8731)
    bind  = cfg_get("command_channel", "bind")       or "0.0.0.0"
    token = cfg_get("command_channel", "token")      or ""

    _AURaHandler.node_agent = node_agent
    _AURaHandler.token      = token

    try:
        _server_instance = _ThreadedHTTPServer((bind, port), _AURaHandler)
        _server_thread   = threading.Thread(
            target=_server_instance.serve_forever,
            daemon=True,
            name="aura-command-channel",
        )
        _server_thread.start()
        write_log(f"CommandChannel started on {bind}:{port}")
        return (bind, port)
    except OSError as exc:
        write_log(f"CommandChannel failed to start on port {port}: {exc}")
        return None


def stop_command_channel():
    """Shut down the command-channel server gracefully."""
    global _server_instance
    if _server_instance:
        _server_instance.shutdown()
        write_log("CommandChannel stopped")
        _server_instance = None


def channel_status():
    """Return a status dict for the command channel."""
    if _server_instance is None:
        return {"running": False}
    port = int(cfg_get("command_channel", "port") or 8731)
    bind = cfg_get("command_channel", "bind") or "0.0.0.0"
    return {"running": True, "port": port, "bind": bind}
