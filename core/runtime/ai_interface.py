import urllib.request
import urllib.error
import json
from core.runtime.model_registry import infer, list_models
from core.runtime.logs import write_log


# ── Ollama probe ──────────────────────────────────────────────────────────────

def _probe_ollama(base_url="http://localhost:11434"):
    """Return list of available Ollama model names, or [] if not reachable."""
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=3) as resp:
            data = json.loads(resp.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


# ── Public entry point ────────────────────────────────────────────────────────

def ai_chat():
    print()
    print("  AURa AI Interface — type \"exit\" to return")
    print("  Probing inference engines…")

    ollama_models = _probe_ollama()

    if ollama_models:
        backend = "ollama"
        active_model = ollama_models[0]
        print(f"  Backend    : Ollama (local) — reachable")
        print(f"  Available  : {', '.join(ollama_models)}")
        print(f"  Active     : {active_model}")
        print("  Tip: type 'model <name>' to switch models.")
    else:
        backend = "aura-nano"
        active_model = "aura-nano"
        reg = list_models()
        print("  Backend    : aura-nano (Ollama not detected at localhost:11434)")
        print(f"  Models     : {', '.join(reg.keys())}")
        print("  To enable Ollama: https://ollama.com → ollama pull llama3")

    write_log(f"AI chat started — backend={backend} model={active_model}")
    print()

    while True:
        try:
            msg = input("  ai> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not msg:
            continue

        if msg == "exit":
            break

        # Allow switching model mid-session
        if msg.startswith("model "):
            new_model = msg[6:].strip()
            active_model = new_model
            if backend == "ollama":
                print(f"  → Switched to Ollama model '{new_model}'")
            else:
                print(f"  → Switched to registry model '{new_model}'")
            write_log(f"AI model switched to {new_model}")
            continue

        write_log(f"AI prompt [{active_model}]: {msg[:80]}")

        if backend == "ollama":
            # Use model_registry which calls real Ollama
            response = infer("aura-nano", msg)
        else:
            response = infer(active_model, msg)

        print()
        print(f"  {response}")
        print()
