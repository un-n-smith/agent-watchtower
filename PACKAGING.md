# Packaging Notes

## Environment

- Python 3.11 or newer
- Writable local filesystem
- macOS, Linux, or Windows
- No external API keys, accounts, adapters, or background daemon

Current release smoke checks are run on macOS. The core package is a plain Python
CLI and is intended to run on Linux and Windows with Python 3.11+; add CI matrix
coverage before claiming broad production-grade cross-platform support.

## Install Smoke Check

From the release candidate root:

```bash
python3 -m pip install .
agent-watchtower --help
```

Expected result:

- install completes without extra dependencies
- help shows only `init`, `task-add`, `worker-status`, `worker-run`, and `artifact-path`

For an isolated install smoke test without touching the default site-packages:

```bash
TARGET="$(mktemp -d)"
python3 -m pip install . --target "$TARGET"
PYTHONPATH="$TARGET" python3 -m agent_watchtower.cli --help
```

## Demo Verification

Run the public v0 acceptance loop:

```bash
./scripts/acceptance_v0.sh
```

For a stronger packaging check that also scans for private-surface leakage:

```bash
./scripts/release_preflight.sh
```

Expected result:

- `status=pass`
- `release_preflight=pass`

## Runtime Cleanup

Remove installed package:

```bash
python3 -m pip uninstall agent-watchtower-core
```

Remove default runtime files:

```bash
rm -rf ~/.agent-watchtower
```

If you used `--root <dir>` during demos, remove that directory separately.
