from cloud.workers import run_image_job, run_video_job, run_apk_job, run_docs_job

def route_worker(job_type, payload):
    if job_type == "image":
        return run_image_job(payload)
    if job_type == "video":
        return run_video_job(payload)
    if job_type == "apk":
        return run_apk_job(payload)
    if job_type == "docs":
        return run_docs_job(payload)
    return {"error": "unknown job type"}
