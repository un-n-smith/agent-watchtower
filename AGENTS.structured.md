# Agent Watchtower Structured Rules

This file is the stricter, machine-oriented version of `AGENTS.md` for CLI agents that follow explicit procedures better than prose.

## Resume Algorithm

1. Run:

```bash
agent-watchtower worker-status
```

2. Parse JSON fields:

```text
state_health
runnable
goal_count
next_task
next_safe_action
latest_artifact_path
```

3. If `state_health` is `blocked`, stop and report `diagnostics`.

4. If `goal_count` is `0`, run:

```bash
agent-watchtower init
agent-watchtower worker-status
```

5. If `runnable` is `true`, do the real local work described by `next_safe_action`.

6. After the real work, run:

```bash
agent-watchtower worker-run --result "Concise markdown summary of the actual work, verification, and output paths."
```

Use `--result-file <path>` when the result is multi-line.

7. If interrupted after starting but before completion, record the task as in progress:

```bash
agent-watchtower task-add \
  --title "Continue interrupted task" \
  --next-action "resume the concrete safe action" \
  --status in_progress
```

## Hard Rules

- Do not call `worker-run` before doing real work unless this is only the disposable demo.
- Do not report completion without checking the generated `artifact_path`.
- Do not invent external actions, spend money, create accounts, or change credentials.
- Do not ask the human to repeat context until `worker-status` and `artifact-path` have been checked.
- Do not use private project communication adapters; this public package only has the five CLI commands.
