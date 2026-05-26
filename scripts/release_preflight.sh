#!/usr/bin/env bash
set -euo pipefail

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${PYTHONPATH:-}:src"

status=0

section() {
  printf '\n## %s\n' "$1"
}

required_file() {
  if [[ -f "$1" ]]; then
    printf 'ok %s\n' "$1"
  else
    printf 'missing %s\n' "$1"
    status=1
  fi
}

section "required files"
for file in README.md README.zh-CN.md ACCEPTANCE.md LICENSE pyproject.toml docs/interrupted-recovery-demo.md docs/interrupted-recovery-demo.zh-CN.md scripts/acceptance_v0.sh scripts/demo_interrupted_recovery.sh src/agent_watchtower/cli.py src/agent_watchtower/worker.py tests/test_core.py; do
  required_file "$file"
done

section "generated files"
generated="$(find . \( -name '__pycache__' -o -name '*.pyc' -o -name '.env' -o -name '*.log' \) -print)"
if [[ -n "$generated" ]]; then
  printf '%s\n' "$generated"
  status=1
else
  printf 'ok\n'
fi

section "private implementation leakage"
if grep -RInE '(/Users/|\.cc-connect|QuantAI|phone-codex|window mailbox|LaunchAgent|CC Connect|Feishu|飞书|handoff|adapter-status|contact-ask|contact-reply|window-send|window-inbox|window-ack|drive --with-adapters|xiaodi|小弟|AAA)' . --exclude='release_preflight.sh' --exclude-dir='.git' --exclude-dir='__pycache__'; then
  status=1
else
  printf 'ok\n'
fi

section "secret-like strings"
if grep -RInE '(^|[^A-Za-z0-9_-])(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' . --exclude='release_preflight.sh' --exclude-dir='.git' --exclude-dir='__pycache__'; then
  status=1
else
  printf 'ok\n'
fi

section "public help"
help_text="$(python3 -m agent_watchtower.cli --help)"
printf '%s\n' "$help_text"
for command in init task-add worker-status worker-run artifact-path; do
  if ! grep -q "$command" <<<"$help_text"; then
    printf 'missing public command: %s\n' "$command"
    status=1
  fi
done
for hidden in drive adapter-status contact-ask contact-reply window-send window-inbox window-ack; do
  if grep -q "$hidden" <<<"$help_text"; then
    printf 'unexpected hidden command in help: %s\n' "$hidden"
    status=1
  fi
done

section "unit tests"
python3 -m unittest discover -s tests -q

section "acceptance"
./scripts/acceptance_v0.sh

section "result"
if [[ "$status" -eq 0 ]]; then
  printf 'release_preflight=pass\n'
else
  printf 'release_preflight=block\n'
fi
exit "$status"
