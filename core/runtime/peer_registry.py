"""
peer_registry.py — AURa virtual mesh peer registry.

Maintains a list of known sibling AURa nodes, their URLs, last-seen
timestamps, and reported capabilities.  Provides helpers for pinging
peers and broadcasting commands to the mesh.

All network calls use the stdlib (urllib) — no external deps.
"""

import json
import os
import urllib.request
import urllib.error
import datetime

from core.runtime.paths import aura_path
from core.runtime.logs  import write_log

PEERS_PATH = aura_path("local", "cache", "peers.json")


# ── Internal I/O ──────────────────────────────────────────────────────────────

def _ensure_dir():
    os.makedirs(os.path.dirname(PEERS_PATH), exist_ok=True)


def _load():
    _ensure_dir()
    if not os.path.exists(PEERS_PATH):
        _save({})
        return {}
    with open(PEERS_PATH, "r") as f:
        return json.load(f)


def _save(peers):
    _ensure_dir()
    with open(PEERS_PATH, "w") as f:
        json.dump(peers, f, indent=2)


# ── Public API ────────────────────────────────────────────────────────────────

def register_peer(node_id, url, capabilities=None):
    """Add or update a peer node in the registry."""
    peers = _load()
    existing = peers.get(node_id, {})
    peers[node_id] = {
        "node_id":      node_id,
        "url":          url,
        "capabilities": capabilities or [],
        "registered":   existing.get("registered", datetime.datetime.now().isoformat()),
        "last_seen":    datetime.datetime.now().isoformat(),
        "status":       existing.get("status", "unknown"),
    }
    _save(peers)
    write_log(f"Peer registered: {node_id} @ {url}")
    return peers[node_id]


def update_peer_seen(node_id):
    """Update the last-seen timestamp for a peer."""
    peers = _load()
    if node_id in peers:
        peers[node_id]["last_seen"] = datetime.datetime.now().isoformat()
        _save(peers)


def remove_peer(node_id):
    """Remove a peer from the registry."""
    peers = _load()
    if node_id not in peers:
        return f"Peer '{node_id}' not found"
    del peers[node_id]
    _save(peers)
    write_log(f"Peer removed: {node_id}")
    return f"Peer '{node_id}' removed"


def list_peers():
    """Return dict of all known peers."""
    return _load()


def get_peer(node_id):
    """Return peer info dict or None."""
    return _load().get(node_id)


def ping_peer(node_id, timeout=3):
    """
    Probe a peer's /health endpoint.

    Returns True if the peer responds with HTTP 200, False otherwise.
    Updates the peer's status and last_seen in the registry.
    """
    peers = _load()
    peer  = peers.get(node_id)
    if not peer:
        return False
    url = peer["url"].rstrip("/") + "/health"
    try:
        req = urllib.request.Request(url)
        urllib.request.urlopen(req, timeout=timeout)
        peers[node_id]["status"]    = "online"
        peers[node_id]["last_seen"] = datetime.datetime.now().isoformat()
        _save(peers)
        write_log(f"Peer ping OK: {node_id}")
        return True
    except Exception:
        peers[node_id]["status"] = "offline"
        _save(peers)
        write_log(f"Peer ping FAIL: {node_id}")
        return False


def ping_all_peers(timeout=3):
    """Ping all peers; return dict of {node_id: bool}."""
    return {nid: ping_peer(nid, timeout) for nid in _load()}


def send_to_peer(node_id, cmd, payload=None, token="", timeout=5):
    """
    POST a command to a peer's /cmd endpoint.

    Returns the response dict or {"error": ...} on failure.
    """
    peer = get_peer(node_id)
    if not peer:
        return {"error": f"Unknown peer '{node_id}'"}

    url  = peer["url"].rstrip("/") + "/cmd"
    body = json.dumps({"cmd": cmd, "payload": payload or {}}).encode("utf-8")
    hdrs = {"Content-Type": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def broadcast(cmd, payload=None, token="", timeout=5):
    """Send a command to all known peers; return {node_id: response_dict}."""
    results = {}
    for node_id in _load():
        results[node_id] = send_to_peer(node_id, cmd, payload, token, timeout)
    return results
