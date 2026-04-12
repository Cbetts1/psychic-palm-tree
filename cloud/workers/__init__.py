import os
import uuid
from core.runtime.paths import aura_path


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _write_result(path, prefix, content=""):
    _ensure_dir(path)
    file_path = os.path.join(path, f"{prefix}_{uuid.uuid4().hex[:8]}.txt")
    with open(file_path, "w") as f:
        f.write(content if content else f"{prefix} job output placeholder")
    return file_path


# ── Core workers ──────────────────────────────────────────────────────────────

def run_image_job(payload):
    out = _write_result(aura_path("cloud", "images"), "image")
    return {"type": "image", "output": out}


def run_video_job(payload):
    out = _write_result(aura_path("cloud", "videos"), "video")
    return {"type": "video", "output": out}


def run_apk_job(payload):
    out = _write_result(aura_path("cloud", "apk"), "apk")
    return {"type": "apk", "output": out}


def run_docs_job(payload):
    prompt = payload.get("prompt", "") if isinstance(payload, dict) else str(payload)
    out = _write_result(aura_path("cloud", "docs"), "doc", prompt)
    return {"type": "docs", "output": out}


# ── Expanded workers ──────────────────────────────────────────────────────────

def run_models_job(payload):
    """Run an inference job via the model registry."""
    from core.runtime.model_registry import infer
    model  = payload.get("model", "aura-nano") if isinstance(payload, dict) else "aura-nano"
    prompt = payload.get("prompt", "")         if isinstance(payload, dict) else str(payload)
    result = infer(model, prompt)
    out    = _write_result(aura_path("cloud", "models"), "model", result)
    return {"type": "models", "model": model, "result": result, "output": out}


def run_index_job(payload):
    """Index files under a given path, write a manifest."""
    from core.runtime.paths import aura_path as _ap
    target = (payload.get("path", _ap("local", "cache"))
              if isinstance(payload, dict) else _ap("local", "cache"))
    index  = {}
    if os.path.exists(target):
        for root, _dirs, files in os.walk(target):
            for f in files:
                full = os.path.join(root, f)
                index[full] = os.path.getsize(full)
    content = "\n".join(f"{size}\t{path}" for path, size in index.items())
    out     = _write_result(aura_path("cloud", "index"), "index", content)
    return {"type": "index", "files_indexed": len(index), "output": out}


def run_search_job(payload):
    """Search for filenames matching a query string."""
    from core.runtime.paths import AURA_ROOT
    query  = payload.get("query", "")   if isinstance(payload, dict) else str(payload)
    root   = payload.get("path", AURA_ROOT) if isinstance(payload, dict) else AURA_ROOT
    hits   = []
    if os.path.exists(root):
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                if query.lower() in f.lower():
                    hits.append(os.path.join(dirpath, f))
    content = "\n".join(hits)
    out     = _write_result(aura_path("cloud", "search"), "search", content)
    return {"type": "search", "query": query, "matches": len(hits), "output": out}
