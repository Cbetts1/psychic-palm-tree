import os
import threading


class ProcessManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._counter = 0
        self.processes = {}
        # Register the main OS process itself
        self._register_main()

    def _register_main(self):
        with self._lock:
            self._counter += 1
            self.processes[self._counter] = {
                "name":      "aura:main",
                "status":    "running",
                "os_pid":    os.getpid(),
                "thread_id": threading.get_ident(),
            }

    def spawn(self, name):
        """Register a new logical process and return its internal PID."""
        with self._lock:
            self._counter += 1
            pid = self._counter
            self.processes[pid] = {
                "name":      name,
                "status":    "running",
                "os_pid":    os.getpid(),
                "thread_id": threading.get_ident(),
            }
        return pid

    def complete(self, pid):
        """Mark a logical process as completed."""
        with self._lock:
            if pid in self.processes:
                self.processes[pid]["status"] = "complete"

    def list(self):
        return self.processes

    def kill(self, pid):
        with self._lock:
            if pid in self.processes:
                self.processes[pid]["status"] = "terminated"
                return True
        return False
