#!/usr/bin/env bash
set -euo pipefail

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${PYTHONPATH:-}:src"

python3 -m agent_watchtower.cli --help > "$ROOT/help.txt"

for command in init task-add worker-status worker-run artifact-path; do
  grep -q "$command" "$ROOT/help.txt"
done

python3 -m agent_watchtower.cli --root "$ROOT/runtime" init > "$ROOT/init.json"
python3 -m agent_watchtower.cli --root "$ROOT/runtime" worker-status > "$ROOT/status-before.json"
python3 -m agent_watchtower.cli --root "$ROOT/runtime" worker-run > "$ROOT/run.json"
python3 -m agent_watchtower.cli --root "$ROOT/runtime" artifact-path > "$ROOT/artifact.json"

python3 - "$ROOT" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
status = json.loads((root / "status-before.json").read_text())
run = json.loads((root / "run.json").read_text())
artifact = json.loads((root / "artifact.json").read_text())

assert status["runnable"] is True
assert status["open_task_count"] == 1
assert run["action"] == "completed_task"
artifact_path = Path(artifact["artifact_path"])
assert artifact_path.exists()
assert artifact_path == Path(run["artifact_path"])
print(json.dumps({"status": "pass", "artifact_path": str(artifact_path)}, sort_keys=True))
PY
