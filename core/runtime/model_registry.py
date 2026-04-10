import os
import json

_REGISTRY_PATH = "/aura/local/cache/models/registry.json"
_CACHE_ROOT    = "/aura/local/cache/models"

_BUILT_IN = {
    "aura-nano": {
        "type": "local",
        "backend": "stub",
        "description": "Lightweight stub model for offline testing",
        "cached": True,
    },
    "aura-cloud": {
        "type": "remote",
        "backend": "cloud",
        "description": "Cloud-hosted AURa inference model",
        "cached": False,
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


def infer(model_name, prompt):
    """Dispatch inference to local stub or remote cloud backend."""
    from core.runtime.logs import write_log
    model = get_model(model_name)
    if model is None:
        return f"[error] Unknown model: {model_name}"
    write_log(f"Infer [{model_name}/{model['type']}]: {prompt[:80]}")
    if model["type"] == "local":
        return f"[{model_name}] {prompt}"          # stub: echo
    # remote stub — no real network call in this build
    return f"[{model_name}@cloud] Response to: {prompt}"
