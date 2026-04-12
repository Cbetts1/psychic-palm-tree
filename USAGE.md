# AURa OS — Usage Reference

## Starting AURa

```sh
aura                          # via installed launcher
python3 -m core.runtime.vhost # direct (from repo root)
sh tools/scripts/aura_boot.sh # via boot script
```

---

## Operator Console

On startup the boot sequence runs, then you choose a boot mode:

| Mode    | Description |
|---------|-------------|
| vhost   | Fully detached virtual host environment |
| shared  | Joint host+virtual mode (bridge) |
| custom  | Configure settings before launching |

The main console provides numbered/lettered menus:

### [1] Shell Console

Interactive AURa shell with built-in commands:

| Command | Description |
|---------|-------------|
| `ls [path]`       | List directory |
| `cat <file>`      | Print file |
| `mounts`          | Show VFS mount points |
| `jobs`            | Show active jobs/processes |
| `log`             | Tail system log |
| `sync-status`     | Show sync state |
| `sync-push`       | Push local → cloud |
| `sync-pull`       | Pull cloud → local |
| `apm-list`        | List installed packages |
| `apm-install <p>` | Install a package |
| `apm-remove <p>`  | Remove a package |
| `apm-update`      | Update all packages |
| `exit`            | Return to main menu |

### [6] Maintenance Tools

- APM package management (install / remove / update)
- AUS update system (check / apply / rollback / channel)
- Safe mode toggle
- Diagnostics full report

### [n] Node Agent / Command Center

- View full node status and health report
- Register this node with a Command Center
- Start / stop the command channel HTTP server
- Manage peer nodes in the virtual mesh

### [b] Builder Engine

- Generate new cloud worker modules
- Generate new shell command handlers
- Generate new JSON config stubs
- List available templates

---

## Node Daemon (headless)

Run the command channel without the interactive console:

```sh
sh tools/scripts/node_daemon.sh start    # start in background
sh tools/scripts/node_daemon.sh stop     # stop
sh tools/scripts/node_daemon.sh restart  # restart
sh tools/scripts/node_daemon.sh status   # is it running?
sh tools/scripts/node_daemon.sh health   # one-line health
sh tools/scripts/node_daemon.sh logs 100 # last 100 log lines
```

---

## Health Check

```sh
sh tools/scripts/health_check.sh        # human-readable report
sh tools/scripts/health_check.sh --json # machine-readable JSON
```

Exit code: `0` = healthy, `1` = degraded or critical.

---

## Configuration

Config is stored in `~/.aura/local/cache/aura.json`.

Key sections:

```json
{
  "cloud": {
    "endpoint": "https://your-cloud.example.com",
    "api_key":  "your-api-key",
    "timeout":  5
  },
  "node": {
    "enabled":            true,
    "name":               "my-node",
    "cc_url":             "https://command-center.example.com",
    "token":              "secret",
    "heartbeat_interval": 30
  },
  "command_channel": {
    "enabled": true,
    "port":    8731,
    "bind":    "0.0.0.0",
    "token":   "secret"
  },
  "safe_mode": false
}
```

---

## Remote Command API

Once the command channel is running, control this node from anywhere:

```sh
# Health check (no auth required)
curl http://localhost:8731/health

# Full status (requires token)
curl http://localhost:8731/status \
  -H "Authorization: Bearer <token>"

# Execute a command
curl -X POST http://localhost:8731/cmd \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"apm-list"}'

# Build a new worker remotely
curl -X POST http://localhost:8731/cmd \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"build-worker","payload":{"name":"transcribe"}}'
```

See `docs/API.md` for the full command reference.

---

## Virtual Mesh

Register sibling AURa nodes so they can receive broadcasts:

```sh
# Via operator console  [n] → [7]
node_id url: abc12345-... http://192.168.1.42:8731

# Via API
curl -X POST http://localhost:8731/peer/register \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"node_id":"abc12345","url":"http://192.168.1.42:8731"}'

# Ping all peers
curl -X POST http://localhost:8731/cmd \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"peer-ping"}'
```

---

## Builder Engine

```sh
# Generate a worker from the shell console or [b] menu
aura-worker-name: transcribe
# → cloud/workers/transcribe.py  (fully functional scaffold)

# The new worker is automatically registered in:
#   cloud/workers/__init__.py
#   core/runtime/worker_router.py
```

---

## Logs

```sh
# System log location
cat ~/.aura/local/cache/system.log

# Via shell console
aura> log

# Via API
curl -X POST http://localhost:8731/cmd \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"log","payload":{"lines":100}}'
```
