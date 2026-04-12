from cloud.workers import (
    run_image_job,
    run_video_job,
    run_apk_job,
    run_docs_job,
    run_models_job,
    run_index_job,
    run_search_job,
)

from cloud.workers.test_audio_gen import run_test_audio_gen_job

from cloud.workers.agent_test_worker import run_agent_test_worker_job

_WORKER_MAP = {
    "image":  run_image_job,
    "video":  run_video_job,
    "apk":    run_apk_job,
    "docs":   run_docs_job,
    "models": run_models_job,
    "index":  run_index_job,
    "search": run_search_job,
        "test_audio_gen":  run_test_audio_gen_job,
        "agent_test_worker":  run_agent_test_worker_job,
}


def route_worker(job_type, payload):
    fn = _WORKER_MAP.get(job_type)
    if fn is None:
        return {"error": f"unknown job type: '{job_type}'"}
    return fn(payload)


def list_workers():
    return list(_WORKER_MAP.keys())

