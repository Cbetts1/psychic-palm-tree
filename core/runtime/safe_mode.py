class SafeMode:
    def __init__(self):
        self.enabled = True

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def status(self):
        return {"safe_mode": self.enabled}
