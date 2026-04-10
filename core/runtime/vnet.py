import socket
from core.runtime.logs import write_log

CONNECTIVITY_MODES = ("online", "offline", "degraded")


class VNet:
    def __init__(self):
        self.routes    = []
        self.endpoints = {}
        self.mode      = "offline"

    # ── Routes ──────────────────────────────────────────────────────────────

    def add_route(self, name, target):
        self.routes.append({"name": name, "target": target})

    def list_routes(self):
        return self.routes

    # ── Endpoints ────────────────────────────────────────────────────────────

    def register_endpoint(self, name, url):
        self.endpoints[name] = url

    def list_endpoints(self):
        return self.endpoints

    # ── Connectivity ─────────────────────────────────────────────────────────

    def detect_connectivity(self, probe_host="8.8.8.8"):
        """Probe DNS; set mode to online / degraded / offline."""
        try:
            socket.setdefaulttimeout(2)
            socket.gethostbyname(probe_host)
            self.mode = "online"
        except socket.gaierror:
            self.mode = "offline"
        except Exception:
            self.mode = "degraded"
        write_log(f"VNet connectivity detected: {self.mode}")
        return self.mode

    def set_mode(self, mode):
        if mode not in CONNECTIVITY_MODES:
            return f"Unknown mode '{mode}'. Valid: {', '.join(CONNECTIVITY_MODES)}"
        self.mode = mode
        write_log(f"VNet mode set manually: {mode}")
        return f"VNet mode → {mode}"

    def ping_cloud(self, host="8.8.8.8"):
        try:
            socket.setdefaulttimeout(2)
            socket.gethostbyname(host)
            return True
        except Exception:
            return False

    # ── Status ───────────────────────────────────────────────────────────────

    def status(self):
        return {
            "mode":      self.mode,
            "routes":    len(self.routes),
            "endpoints": list(self.endpoints.keys()),
        }

