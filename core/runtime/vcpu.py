class VCPU:
    def __init__(self):
        self.cores = 1
        self.load = 0.0

    def status(self):
        return {"cores": self.cores, "load": self.load}

    def simulate_load(self, amount):
        self.load = max(0.0, min(1.0, amount))
