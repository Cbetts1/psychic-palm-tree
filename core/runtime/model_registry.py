import json
import urllib.request
import urllib.error
import os
from core.runtime.paths import aura_path

_REGISTRY_PATH = aura_path("local", "cache", "models", "registry.json")
_CACHE_ROOT    = aura_path("local", "cache", "models")

_BUILT_IN = {
    "aura-nano": {
        "type":        "local",
        "backend":     "ollama",
        "model_id":    "llama3",
        "description": "Routes to a local Ollama instance (llama3)",
        "cached":      False,
    },
    "aura-cloud": {
        "type":        "remote",
        "backend":     "cloud",
        "description": "Cloud-hosted AURa inference model",
        "cached":      False,
    },
}


def _ensure_dir():
    os.makedirs(_CACHE_ROOT, exist_ok=True)


def load_registry():
    _ensure_dir()
    if not os.path.exists(_REGISTRY_PATH):
        _save_registry(_BUILT_IN)
        return dict(_BUILT_IN)
    with open(_REGISTRY_PATH, "r") as f:
        return json.load(f)


def _save_registry(reg):
    _ensure_dir()
    with open(_REGISTRY_PATH, "w") as f:
        json.dump(reg, f, indent=2)


def list_models():
    return load_registry()


def get_model(name):
    return load_registry().get(name)


def register_model(name, model_info):
    from core.runtime.logs import write_log
    reg = load_registry()
    reg[name] = model_info
    _save_registry(reg)
    write_log(f"Model registered: {name}")
    return f"Model '{name}' registered"


def cache_model(name):
    from core.runtime.logs import write_log
    reg = load_registry()
    if name not in reg:
        return f"Unknown model: {name}"
    reg[name]["cached"] = True
    _save_registry(reg)
    write_log(f"Model cached: {name}")
    return f"Model '{name}' marked as cached"


def _ollama_infer(model_id, prompt, base_url="http://localhost:11434"):
    """
    Call a local Ollama instance.  Returns the response string or raises.
    """
    payload = json.dumps({
        "model":  model_id,
        "prompt": prompt,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
        return body.get("response", "").strip()


def _cloud_infer(model_name, prompt):
    """
    Try the configured cloud endpoint.  Returns the response string or raises.
    """
    from core.runtime.config import get as cfg_get
    endpoint = cfg_get("cloud", "endpoint") or ""
    api_key  = cfg_get("cloud", "api_key")  or ""
    if not endpoint:
        raise RuntimeError("No cloud endpoint configured.")

    payload = json.dumps({"model": model_name, "prompt": prompt}).encode()
    req = urllib.request.Request(
        f"{endpoint}/infer",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read())
        return body.get("response", "").strip()


def infer(model_name, prompt):
    """
    Run real inference.

    Priority order:
      1. local/ollama  → Ollama REST API at localhost:11434
      2. remote/cloud  → configured cloud endpoint
      3. fallback      → honest error message (no silent echo)
    """
    from core.runtime.logs import write_log
    model = get_model(model_name)
    if model is None:
        return f"[error] Unknown model '{model_name}'. Run 'list models' to see available models."

    write_log(f"Infer [{model_name}/{model.get('type')}]: {prompt[:80]}")

    # ── 1. Local Ollama ───────────────────────────────────────────────────────
    if model.get("type") == "local" and model.get("backend") == "ollama":
        model_id = model.get("model_id", "llama3")
        try:
            response = _ollama_infer(model_id, prompt)
            write_log(f"Ollama [{model_id}] responded ({len(response)} chars)")
            return response
        except Exception as exc:
            write_log(f"Ollama unavailable: {exc}")
            return (
                f"[aura-nano] Ollama inference engine not reachable at localhost:11434.\n"
                f"To enable: install Ollama (https://ollama.com) and run: ollama pull {model_id}\n"
                f"Your prompt was: {prompt}"
            )

    # ── 2. Cloud endpoint ─────────────────────────────────────────────────────
    if model.get("type") == "remote" and model.get("backend") == "cloud":
        try:
            response = _cloud_infer(model_name, prompt)
            write_log(f"Cloud [{model_name}] responded ({len(response)} chars)")
            return response
        except Exception as exc:
            write_log(f"Cloud infer failed: {exc}")
            return (
                f"[aura-cloud] Cloud inference failed: {exc}\n"
                f"Configure endpoint + api_key in /aura/local/cache/aura.json.\n"
                f"Your prompt was: {prompt}"
            )

    # ── 3. Unknown backend ────────────────────────────────────────────────────
    return (
        f"[{model_name}] No inference backend configured for this model.\n"
        f"Edit the model registry or configure Ollama / cloud endpoint."
    )
