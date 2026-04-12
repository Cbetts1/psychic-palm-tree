# AURa OS — Installation Guide

## Requirements

| Requirement | Minimum |
|-------------|---------|
| OS          | Android 9+ (Termux) or Linux |
| CPU         | ARM64 or x86-64 |
| Python      | 3.11+ |
| RAM         | 512 MB free |
| Storage     | 200 MB free |
| Network     | Optional (offline mode available) |

No root, no sudo, no Docker, no virtualisation required.

---

## Termux (Android) — one command

Open Termux and run:

```sh
curl -fsSL https://raw.githubusercontent.com/Cbetts1/psychic-palm-tree/main/install.sh | sh
```

This will:
1. Install `python` and `git` via `pkg` if missing.
2. Clone the repo to `~/aura-os`.
3. Create the AURa filesystem at `~/.aura/`.
4. Install the `aura` launcher to `$PREFIX/bin/aura`.

Launch AURa:

```sh
aura
```

---

## Manual Installation

```sh
# 1. Clone
git clone https://github.com/Cbetts1/psychic-palm-tree ~/aura-os
cd ~/aura-os

# 2. Run build/setup script
sh build.sh

# 3. Launch
export PYTHONPATH="${HOME}/aura-os"
python3 -m core.runtime.vhost
```

---

## Custom AURa Root

By default AURa stores all data in `~/.aura/`.  Override with:

```sh
export AURA_ROOT="/path/to/your/aura"
```

This can be set permanently in `~/.bashrc` or `~/.profile`.

---

## Filesystem Layout

After installation the following directories are created:

```
~/.aura/
├── local/
│   ├── cache/         ← configs, logs, identity, version
│   │   └── models/    ← cached AI model files
│   └── packages/      ← installed AURa packages
└── cloud/
    ├── images/        ← image worker output
    ├── videos/        ← video worker output
    ├── apk/           ← APK builder output
    ├── docs/          ← docs worker output
    ├── models/        ← model inference output
    ├── index/         ← file index manifests
    ├── search/        ← search result output
    ├── manifests/     ← package manifests
    └── packages/      ← cloud package registry
```

---

## Updating

```sh
cd ~/aura-os
git pull --ff-only
sh build.sh
```

---

## Uninstalling

```sh
rm -rf ~/aura-os ~/.aura
rm -f "${PREFIX:-$HOME/.local}/bin/aura"
rm -f "${PREFIX:-$HOME/.local}/bin/aura-node"
```

---

## Troubleshooting

### Python not found
```sh
# Termux
pkg install python

# Debian/Ubuntu
apt-get install python3
```

### Port 8731 already in use
Edit `~/.aura/local/cache/aura.json` and change `command_channel.port` to
another unprivileged port (1024–65535).

### Command channel not starting
Check the log:
```sh
tail -50 ~/.aura/local/cache/system.log
```

### Import errors
Ensure `PYTHONPATH` includes the repo root:
```sh
export PYTHONPATH="${HOME}/aura-os"
```
