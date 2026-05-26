#!/usr/bin/env bash
set -euo pipefail

export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"

ROOT="${1:-$(mktemp -d)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if command -v agent-watchtower >/dev/null 2>&1; then
  WATCHTOWER=(agent-watchtower)
  WATCHTOWER_DISPLAY="agent-watchtower"
else
  export PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
  WATCHTOWER=(python3 -m agent_watchtower.cli)
  WATCHTOWER_DISPLAY="PYTHONPATH=$REPO_ROOT/src python3 -m agent_watchtower.cli"
fi

section() {
  printf '\n## %s\n' "$1"
}

section "demo runtime"
printf 'ROOT=%s\n' "$ROOT"

section "1. initialize local continuity state"
"${WATCHTOWER[@]}" --root "$ROOT" init

section "2. see what the next session would know"
"${WATCHTOWER[@]}" --root "$ROOT" worker-status

section "3. run one bounded worker step"
"${WATCHTOWER[@]}" --root "$ROOT" worker-run

section "4. find the latest artifact"
"${WATCHTOWER[@]}" --root "$ROOT" artifact-path

section "5. simulate coming back later"
printf 'Close the terminal, reopen it, then run:\n'
printf '%s --root %q worker-status\n' "$WATCHTOWER_DISPLAY" "$ROOT"
printf '%s --root %q artifact-path\n' "$WATCHTOWER_DISPLAY" "$ROOT"

section "result"
printf 'The local Watchtower files under %s preserve the goal, receipt, next safe action, and artifact path.\n' "$ROOT"
