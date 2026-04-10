class ProcessManager:
    def __init__(self):
        self.pid = 0
        self.processes = {}

    def spawn(self, name):
        self.pid += 1
        self.processes[self.pid] = {"name": name, "status": "running"}
        return self.pid

    def list(self):
        return self.processes

    def kill(self, pid):
        if pid in self.processes:
            self.processes[pid]["status"] = "terminated"
            return True
        return False
