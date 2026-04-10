import os
import uuid
import json

IDENTITY_PATH = "/aura/local/cache/identity.json"

def _ensure_dir():
    os.makedirs(os.path.dirname(IDENTITY_PATH), exist_ok=True)

def load_identity():
    _ensure_dir()
    if not os.path.exists(IDENTITY_PATH):
        ident = {
            "device_uuid": str(uuid.uuid4()),
            "cloud_uuid": None
        }
        with open(IDENTITY_PATH, "w") as f:
            json.dump(ident, f)
        return ident
    with open(IDENTITY_PATH, "r") as f:
        return json.load(f)

def save_identity(ident):
    _ensure_dir()
    with open(IDENTITY_PATH, "w") as f:
        json.dump(ident, f)

def set_cloud_uuid(cloud_id):
    ident = load_identity()
    ident["cloud_uuid"] = cloud_id
    save_identity(ident)
    return ident
