from core.runtime.config import get as cfg_get


class SafeMode:
    def __init__(self):
        # Read real safe_mode setting from persistent config
        self.enabled = bool(cfg_get("safe_mode"))

    def enable(self):
        self.enabled = True
        self._persist()

    def disable(self):
        self.enabled = False
        self._persist()

    def _persist(self):
        """Write current state back to config so it survives restarts."""
        from core.runtime.config import set_value
        set_value("safe_mode", None, self.enabled)  # top-level key

    def status(self):
        return {"safe_mode": self.enabled}
