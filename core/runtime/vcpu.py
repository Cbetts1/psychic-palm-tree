import os
import platform as _platform


class VCPU:
    def __init__(self):
        # Real core count from the OS
        self.cores = os.cpu_count() or 1
        self._forced_load = None   # set by simulate_load(); None = use real value
        self.load = self._read_load()

    # ── Real CPU load ─────────────────────────────────────────────────────────

    def _read_load(self):
        """Return a 0.0–1.0 load fraction from the real OS."""
        if self._forced_load is not None:
            return self._forced_load

        # Linux: /proc/loadavg gives 1-min average jobs
        if _platform.system() == "Linux":
            try:
                with open("/proc/loadavg", "r") as f:
                    one_min = float(f.read().split()[0])
                return min(1.0, one_min / self.cores)
            except Exception:
                pass

        # Fallback: try psutil (optional dep)
        try:
            import psutil  # type: ignore
            return psutil.cpu_percent(interval=0.1) / 100.0
        except Exception:
            pass

        return 0.0

    # ── Public API ────────────────────────────────────────────────────────────

    def status(self):
        self.load = self._read_load()
        return {"cores": self.cores, "load": self.load}

    def simulate_load(self, amount):
        """Override the real load reading with a fixed value (for testing)."""
        self._forced_load = max(0.0, min(1.0, amount))
        self.load = self._forced_load

    def clear_simulated_load(self):
        """Remove the override and return to reading real CPU load."""
        self._forced_load = None
        self.load = self._read_load()
