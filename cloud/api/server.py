from core.runtime.logs import write_log
from core.runtime.config import get as cfg_get

# In-memory job queue (persists for the lifetime of the process)
_JOB_QUEUE = []


def _next_id():
    return len(_JOB_QUEUE) + 1


def _auth_headers():
    api_key = cfg_get("cloud", "api_key")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def submit_job(job_type, payload):
    job = {
        "id":       _next_id(),
        "type":     job_type,
        "payload":  payload,
        "status":   "queued",
        "headers":  _auth_headers(),
    }
    _JOB_QUEUE.append(job)
    write_log(f"Cloud job submitted: #{job['id']} type={job_type}")
    return {"status": "queued", "job_id": job["id"], "job_type": job_type}


def get_job(job_id):
    for job in _JOB_QUEUE:
        if job["id"] == job_id:
            return job
    return {"error": f"Job #{job_id} not found"}


def list_jobs():
    return list(_JOB_QUEUE)


def cloud_status():
    endpoint   = cfg_get("cloud", "endpoint") or "https://example-cloud-endpoint.com"
    api_key_ok = bool(cfg_get("cloud", "api_key"))
    queued     = sum(1 for j in _JOB_QUEUE if j["status"] == "queued")
    return {
        "endpoint":    endpoint,
        "api_key_set": api_key_ok,
        "jobs_queued": queued,
        "jobs_total":  len(_JOB_QUEUE),
    }

