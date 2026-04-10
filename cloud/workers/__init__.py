import os
import uuid

def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def _write_dummy(path, prefix):
    _ensure_dir(path)
    file_path = os.path.join(path, f"{prefix}_{uuid.uuid4().hex}.txt")
    with open(file_path, "w") as f:
        f.write(f"{prefix} job output placeholder")
    return file_path

def run_image_job(payload):
    out_dir = "/aura/cloud/images"
    return {"type": "image", "output": _write_dummy(out_dir, "image")}

def run_video_job(payload):
    out_dir = "/aura/cloud/videos"
    return {"type": "video", "output": _write_dummy(out_dir, "video")}

def run_apk_job(payload):
    out_dir = "/aura/cloud/apk"
    return {"type": "apk", "output": _write_dummy(out_dir, "apk")}

def run_docs_job(payload):
    out_dir = "/aura/cloud/docs"
    return {"type": "docs", "output": _write_dummy(out_dir, "doc")}
