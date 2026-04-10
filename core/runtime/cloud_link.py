import urllib.request
import urllib.error
from core.runtime.config import get as cfg_get
from core.runtime.logs import write_log


class CloudLink:
    def __init__(self):
        self.url    = cfg_get("cloud", "endpoint") or ""
        self.online = False

    def connect(self):
        if not self.url:
            write_log("CloudLink: no endpoint configured — skipping probe")
            self.online = False
            return False

        timeout = int(cfg_get("cloud", "timeout") or 5)
        try:
            req = urllib.request.Request(self.url, method="HEAD")
            api_key = cfg_get("cloud", "api_key")
            if api_key:
                req.add_header("Authorization", f"Bearer {api_key}")
            urllib.request.urlopen(req, timeout=timeout)
            self.online = True
        except (urllib.error.URLError, OSError):
            self.online = False
        except Exception:
            self.online = False

        write_log(f"CloudLink probe {self.url} → {'online' if self.online else 'offline'}")
        return self.online

    def status(self):
        return {
            "cloud_online": self.online,
            "endpoint":     self.url or "(not configured)",
        }
