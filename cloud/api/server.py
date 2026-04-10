from core.runtime.logs import write_log

def submit_job(job_type, payload):
    write_log(f"Cloud job submitted: {job_type} {payload}")
    return {"status": "queued", "job_type": job_type, "payload": payload}
