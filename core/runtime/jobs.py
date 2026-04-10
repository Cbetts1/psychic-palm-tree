from cloud.api.server import submit_job

def queue_job(job_type, payload):
    return submit_job(job_type, payload)
