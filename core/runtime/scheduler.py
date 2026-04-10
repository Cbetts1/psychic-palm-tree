from core.runtime.process_manager import ProcessManager
from core.runtime.vcpu import VCPU
from core.runtime.worker_router import route_worker

class JobScheduler:
    def __init__(self):
        self.pm = ProcessManager()
        self.vcpu = VCPU()

    def queue(self, job_type, payload):
        pid = self.pm.spawn(f"job:{job_type}")
        result = route_worker(job_type, payload)
        return {"pid": pid, "result": result}

    def status(self):
        return {
            "processes": self.pm.list(),
            "cpu": self.vcpu.status()
        }
