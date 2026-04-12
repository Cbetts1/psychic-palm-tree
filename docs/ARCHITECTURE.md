# AURa OS — Architecture

## Overview

AURa is an AI-native operating environment built around three principles:

1. **The device is a thin terminal** — all state, storage, and heavy compute
   can be delegated to the cloud or peer nodes.
2. **AI is the control plane** — jobs, files, and services are managed through
   an AI interface rather than traditional system calls.
3. **The system must protect the host** — no root, no privileged operations,
   no modifications to the host OS.

---

## Boot Sequence

```
python3 -m core.runtime.vhost
         │
         ├─ print_boot_banner()          ← identity_banner.py
         ├─ load_version()               ← version.py
         ├─ detect_host()               ← host-bridge/android/ or linux/
         │
         ├─ run_boot_sequence()          ← boot_sequence.py
         │   ├─ HybridVFS.ensure_paths()
         │   ├─ VNet.detect_connectivity()
         │   ├─ CloudLink.connect()
         │   ├─ JobScheduler()
         │   ├─ SafeMode()
         │   └─ list_packages()
         │
         ├─ _start_node_services()
         │   ├─ start_command_channel()  ← command_channel.py  (port 8731)
         │   ├─ NodeAgent.register_with_cc()
         │   └─ NodeAgent.start_heartbeat()
         │
         ├─ show_boot_menu()             ← ui/menu/boot_menu.py
         └─ launch_menu()               ← ui/menu/main_menu.py
```

---

## Core Subsystems

### Identity (`core/runtime/identity.py`)

Each node has a permanent `device_uuid` (UUID4, generated once and
persisted in `~/.aura/local/cache/identity.json`).  When registered
with a Command Center the `cloud_uuid` is also stored.

### Virtual Filesystem (`core/runtime/vfs.py`)

`HybridVFS` maintains a map of named mount points:

| Mount     | Path |
|-----------|------|
| `cloud`   | `~/.aura/cloud/` |
| `cache`   | `~/.aura/local/cache/` |
| `packages`| `~/.aura/local/packages/` |

Sub-directories for each worker type are created under `cloud/`.

### Virtual Network (`core/runtime/vnet.py`)

`VNet` manages named routes, endpoint registrations, and a
connectivity mode (`online` / `offline` / `degraded`).  Connectivity
is determined by a DNS probe to `8.8.8.8`.

### Cloud Link (`core/runtime/cloud_link.py`)

`CloudLink` probes the configured cloud endpoint with an HTTP HEAD
request.  If an `api_key` is configured it is sent as a Bearer token.

### Job Scheduler (`core/runtime/scheduler.py`)

`JobScheduler` wraps `ProcessManager` (logical process registry) and
`VCPU` (real CPU load reader).  Jobs are dispatched to cloud workers
via `worker_router.py`.

### Node Agent (`core/runtime/node_agent.py`)

The node agent gives this AURa instance its virtual identity on the
Command Center mesh:

- Reads `device_uuid` from `identity.py`.
- POSTs `/register` to the CC URL with capabilities and API port.
- Runs a background heartbeat thread (default interval: 30 s).
- Dispatches remote commands received via the command channel.

### Command Channel (`core/runtime/command_channel.py`)

A `ThreadingTCPServer` (stdlib `http.server`) listening on port 8731
(configurable).  Serves a JSON HTTP API with Bearer-token auth.

### Peer Registry (`core/runtime/peer_registry.py`)

Persists sibling node registrations to `~/.aura/local/cache/peers.json`.
Provides `ping_peer()`, `broadcast()`, and `send_to_peer()`.

### Builder (`core/runtime/builder.py`)

Template-based code generation engine:

- `build_worker(name)` → `cloud/workers/<slug>.py`
  and registers it in `worker_router.py`.
- `build_command(name)` → `core/shell/ext/<slug>.py`
- `build_config_stub(name)` → `~/.aura/local/cache/<slug>.config.json`

### Health (`core/runtime/health.py`)

Reads `/proc/loadavg` and `/proc/meminfo` (Android/Linux) or falls
back to `psutil`.  Classifies status as `healthy`, `degraded`,
or `critical`.

---

## Module Structure

```
psychic-palm-tree/
├── core/
│   ├── runtime/
│   │   ├── vhost.py              ← entry point
│   │   ├── boot_sequence.py
│   │   ├── identity.py
│   │   ├── identity_banner.py
│   │   ├── version.py
│   │   ├── config.py
│   │   ├── paths.py
│   │   ├── logs.py
│   │   ├── vfs.py
│   │   ├── vnet.py
│   │   ├── cloud_link.py
│   │   ├── scheduler.py
│   │   ├── process_manager.py
│   │   ├── vcpu.py
│   │   ├── worker_router.py
│   │   ├── jobs.py
│   │   ├── apm.py
│   │   ├── aus.py
│   │   ├── ai_interface.py
│   │   ├── model_registry.py
│   │   ├── sync.py
│   │   ├── safe_mode.py
│   │   ├── diagnostics.py
│   │   ├── health.py             ← NEW
│   │   ├── node_agent.py         ← NEW
│   │   ├── command_channel.py    ← NEW
│   │   ├── builder.py            ← NEW
│   │   └── peer_registry.py      ← NEW
│   └── shell/
│       ├── main_shell.py
│       ├── commands.py
│       └── ext/                  ← generated command handlers
├── cloud/
│   ├── api/
│   │   └── server.py
│   └── workers/
│       └── __init__.py
├── host-bridge/
│   ├── android/detect_capabilities.py
│   └── linux/detect_capabilities.py
├── ui/
│   └── menu/
│       ├── boot_menu.py
│       └── main_menu.py
├── tools/
│   └── scripts/
│       ├── aura_boot.sh
│       ├── node_daemon.sh        ← NEW
│       └── health_check.sh       ← NEW
├── docs/
│   ├── vision.md
│   ├── ARCHITECTURE.md           ← this file
│   └── API.md                    ← NEW
├── README.md
├── INSTALL.md                    ← NEW
├── USAGE.md                      ← NEW
├── install.sh                    ← NEW
└── build.sh                      ← NEW
```

---

## Configuration

All persistent config lives in `~/.aura/local/cache/aura.json`.
Default values are defined in `core/runtime/config.py:_DEFAULTS`.

New sections added in this release:

```json
"node": {
  "enabled":            true,
  "name":               "",
  "cc_url":             "",
  "token":              "",
  "heartbeat_interval": 30
},
"command_channel": {
  "enabled": true,
  "port":    8731,
  "bind":    "0.0.0.0",
  "token":   ""
}
```

---

## Security Model

- No root or privileged ports (default port 8731 > 1024).
- Bearer-token auth on all write/execute endpoints.
- Public read-only endpoints: `GET /`, `GET /health`, `GET /capabilities`.
- Token is never logged.
- No arbitrary shell execution unless explicitly implemented in a
  worker or command handler by the operator.
- All file writes are confined to `AURA_ROOT` (`~/.aura/` by default).
