# AURa OS

**AURa** is an AI-native operating environment designed to run inside
[Termux](https://termux.dev/) on Android (ARM64) or on any Linux host,
with no root, no Docker, and no virtualisation required.

The device is a thin terminal and bridge.  All heavy compute and storage
live in the cloud (or a sibling repo node).  AI is the control plane for
jobs, files, and services.

---

## Architecture

```
Android / Termux                     Cloud / Command Center
┌──────────────────────────────┐     ┌──────────────────────────────┐
│  AURa OS node                │     │  Command Center (CC)          │
│  ─────────────────────────── │     │  ─────────────────────────── │
│  core/runtime/vhost.py       │     │  receives /register           │
│    ├─ boot_sequence          │     │  receives /heartbeat          │
│    ├─ VNet                   │◄───►│  sends   POST /cmd            │
│    ├─ HybridVFS              │     └──────────────────────────────┘
│    ├─ NodeAgent   ──────────►│────► heartbeat (every 30 s)
│    ├─ CommandChannel :8731   │◄───  remote commands
│    └─ Operator Console (TUI) │
└──────────────────────────────┘
         │
         │  peer mesh (virtual network of AURa nodes)
         ▼
  other AURa nodes  (POST /cmd, GET /health)
```

**Key modules**

| Path | Purpose |
|------|---------|
| `core/runtime/vhost.py`          | Entry point; boots all subsystems |
| `core/runtime/node_agent.py`     | Virtual node identity, CC registration, heartbeat |
| `core/runtime/command_channel.py`| HTTP API server (port 8731) |
| `core/runtime/health.py`         | CPU / memory / disk metrics |
| `core/runtime/peer_registry.py`  | Virtual mesh peer registry |
| `core/runtime/builder.py`        | Code-generation engine |
| `core/runtime/vnet.py`           | Virtual network layer |
| `core/runtime/vfs.py`            | Hybrid virtual filesystem |
| `core/runtime/apm.py`            | AURa package manager |
| `cloud/workers/__init__.py`      | Cloud job workers |
| `ui/menu/main_menu.py`           | Interactive operator console |

---

## Quick Start

### Termux (one command)

```sh
curl -fsSL https://raw.githubusercontent.com/Cbetts1/psychic-palm-tree/main/install.sh | sh
```

Then launch:

```sh
aura
```

### Manual install

```sh
git clone https://github.com/Cbetts1/psychic-palm-tree ~/aura-os
cd ~/aura-os
sh build.sh
python3 -m core.runtime.vhost
```

---

## Operator Console

On launch you are presented with the **Operator Console**:

```
  [1]  Shell Console
  [2]  Main Host
  [3]  Virtual Host (vHost)
  [4]  Virtual CPU (vCPU)
  [5]  Virtual Cloud (vCloud)
  [6]  Maintenance Tools
  [7]  System Info
  [8]  Sync & Jobs
  [9]  Settings
  [n]  Node Agent / Command Center
  [b]  Builder Engine
  [0]  Exit
```

---

## Remote Control (Command Center)

Set `cc_url` and `token` in `~/.aura/local/cache/aura.json`:

```json
{
  "node": {
    "cc_url": "https://your-command-center.example.com",
    "token":  "your-secret-token"
  },
  "command_channel": {
    "enabled": true,
    "port":    8731,
    "token":   "your-secret-token"
  }
}
```

The node will:
1. `POST /register` to the CC with its identity and capabilities.
2. Send a `POST /heartbeat` every 30 seconds.
3. Accept `POST /cmd` from the CC with remote commands.

See `docs/API.md` for the full API reference.

---

## Builder Engine

Generate new workers and commands without writing boilerplate:

```
AURa[Builder] » 1          # Generate worker
Worker name: transcribe
→ CREATED : ~/aura-os/cloud/workers/transcribe.py
```

Or via remote command:

```sh
curl -X POST http://localhost:8731/cmd \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"build-worker","payload":{"name":"transcribe"}}'
```

---

## Documentation

| File | Contents |
|------|---------|
| `INSTALL.md`           | Detailed installation guide |
| `USAGE.md`             | Full usage reference |
| `docs/ARCHITECTURE.md` | Architecture deep-dive |
| `docs/API.md`          | Command channel API reference |
| `docs/vision.md`       | Project vision |

---

## License

MIT

