# AURa OS — Command Channel API Reference

The command channel is a lightweight HTTP/JSON API that allows the
Command Center (or any authorised client) to query, control, and
orchestrate an AURa node remotely.

**Default URL:** `http://<device-ip>:8731`

---

## Authentication

If `command_channel.token` is non-empty in `aura.json`, every
non-public endpoint requires:

```
Authorization: Bearer <token>
```

Public endpoints (`GET /`, `GET /health`, `GET /capabilities`) never
require authentication.

---

## Endpoints

### GET /

Basic node info.  Always public.

**Response 200**
```json
{
  "service": "aura-command-channel",
  "node_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "0.9.0",
  "channel": "stable"
}
```

---

### GET /health

Live health metrics.  Always public.

**Response 200**
```json
{
  "timestamp": "2025-01-01T12:00:00.000000",
  "status":    "healthy",
  "cpu": {
    "cores":    8,
    "load_1m":  0.45,
    "load_pct": 5.6,
    "arch":     "aarch64"
  },
  "memory": {
    "total_mb":     7812.0,
    "available_mb": 4096.0,
    "used_pct":     47.6
  },
  "disk": {
    "path":     "/data/data/com.termux/files/home/.aura",
    "total_mb": 57344.0,
    "free_mb":  32768.0,
    "used_pct": 42.9
  },
  "process": {
    "pid":    12345,
    "python": "3.11.0",
    "node":   "localhost"
  },
  "aura": {
    "root":   "/data/data/com.termux/files/home/.aura",
    "log_kb": 12.3
  }
}
```

`status` values: `"healthy"` | `"degraded"` (mem > 90 %) | `"critical"` (disk > 95 %)

---

### GET /capabilities

List of capability strings.  Always public.

**Response 200**
```json
{
  "capabilities": [
    "shell", "apm", "sync", "vfs", "vnet",
    "ai-interface", "cloud-workers", "builder", "health-api", "peer-mesh"
  ]
}
```

---

### GET /status

Full node status.  **Requires auth.**

**Response 200**
```json
{
  "node_id":      "550e8400-...",
  "name":         "aura-550e8400",
  "version":      "0.9.0",
  "channel":      "stable",
  "capabilities": [...],
  "registered":   false,
  "started_at":   "2025-01-01T12:00:00",
  "cloud_uuid":   null,
  "health":       { ... },
  "peer_count":   2,
  "aura_root":    "/home/user/.aura"
}
```

---

### GET /peers

List known peer nodes.  **Requires auth.**

**Response 200**
```json
{
  "peers": {
    "abc12345-...": {
      "node_id":      "abc12345-...",
      "url":          "http://192.168.1.42:8731",
      "capabilities": ["shell", "apm"],
      "registered":   "2025-01-01T11:00:00",
      "last_seen":    "2025-01-01T12:00:00",
      "status":       "online"
    }
  }
}
```

---

### POST /cmd

Execute a command on this node.  **Requires auth.**

**Request body**
```json
{
  "cmd":     "<command>",
  "payload": {}
}
```

**Response 200** — result object (varies by command)

**Response 401** — `{"error": "Unauthorized"}`

#### Available commands

| Command | Payload | Description |
|---------|---------|-------------|
| `status` | — | Full node status |
| `health` | — | Health snapshot |
| `capabilities` | — | List capabilities |
| `version` | — | Version/channel info |
| `apm-list` | — | List installed packages |
| `apm-install` | `{"name":"<pkg>"}` | Install a package |
| `apm-remove` | `{"name":"<pkg>"}` | Remove a package |
| `sync-push` | — | Push local → cloud |
| `sync-pull` | — | Pull cloud → local |
| `log` | `{"lines":50}` | Last N log lines |
| `peer-list` | — | List peer nodes |
| `peer-add` | `{"node_id":"…","url":"…"}` | Add a peer |
| `peer-ping` | — | Ping all peers |
| `peer-remove` | `{"node_id":"…"}` | Remove a peer |
| `build-worker` | `{"name":"<name>"}` | Generate worker module |
| `build-command` | `{"name":"<name>"}` | Generate command handler |
| `build-config` | `{"name":"<name>"}` | Generate config stub |
| `restart` | — | Returns restart advisory |

---

### POST /peer/register

Register this node as a peer (called by other AURa nodes).
**Requires auth.**

**Request body**
```json
{
  "node_id":      "<uuid>",
  "url":          "http://<host>:<port>",
  "capabilities": ["shell", "apm"]
}
```

**Response 200**
```json
{
  "registered": {
    "node_id":    "…",
    "url":        "…",
    "last_seen":  "2025-01-01T12:00:00"
  }
}
```

---

## Command Center Integration

Your Command Center must expose two endpoints that AURa nodes will call:

### POST /register  (CC-side)

Receives node registration.  Optionally returns a `cloud_uuid`.

**Expected body** (sent by node)
```json
{
  "node_id":       "<uuid>",
  "name":          "aura-<short>",
  "version":       "0.9.0",
  "channel":       "stable",
  "capabilities":  [...],
  "api_port":      8731,
  "registered_at": "2025-01-01T12:00:00"
}
```

**Expected response**
```json
{ "cloud_uuid": "<optional-uuid-assigned-by-cc>" }
```

### POST /heartbeat  (CC-side)

Receives periodic heartbeats.

**Expected body** (sent by node)
```json
{
  "node_id":   "<uuid>",
  "name":      "aura-<short>",
  "version":   "0.9.0",
  "timestamp": "2025-01-01T12:00:30",
  "health": {
    "status":   "healthy",
    "cpu_pct":  5.6,
    "mem_pct":  47.6,
    "disk_pct": 42.9
  }
}
```

---

## Example: curl session

```sh
BASE="http://localhost:8731"
TOK="your-secret-token"

# Public endpoints
curl "${BASE}/"
curl "${BASE}/health"
curl "${BASE}/capabilities"

# Authenticated endpoints
curl "${BASE}/status" -H "Authorization: Bearer ${TOK}"
curl "${BASE}/peers"  -H "Authorization: Bearer ${TOK}"

# Execute a command
curl -X POST "${BASE}/cmd" \
  -H "Authorization: Bearer ${TOK}" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"apm-list"}'

# Build a new worker
curl -X POST "${BASE}/cmd" \
  -H "Authorization: Bearer ${TOK}" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"build-worker","payload":{"name":"audio"}}'

# Register a peer
curl -X POST "${BASE}/peer/register" \
  -H "Authorization: Bearer ${TOK}" \
  -H "Content-Type: application/json" \
  -d '{"node_id":"abc12345","url":"http://192.168.1.42:8731","capabilities":["shell"]}'
```
