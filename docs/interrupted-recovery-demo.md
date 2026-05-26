# Interrupted Recovery Demo

This demo shows the smallest useful loop:

1. a coding agent starts work
2. the session stops
3. a later session checks the local Watchtower state
4. work resumes from the last recorded goal, next action, and artifact path

No background service is involved. No external account is needed.

## The Problem

Without a local continuity record, an interrupted agent session usually leaves the human guessing:

```text
The agent was working.
The terminal closed.
The next session does not know what happened.
The human has to explain the project again.
```

Agent Watchtower does not make the agent autonomous by itself. It gives the next session a small, durable work notebook.

## Run The Demo

From an installed package:

```bash
ROOT="$(mktemp -d)"
agent-watchtower --root "$ROOT" init
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" worker-run
agent-watchtower --root "$ROOT" artifact-path
```

From a source checkout:

```bash
./scripts/demo_interrupted_recovery.sh
```

## What To Notice

After `init`, the runtime has one demo goal and one open task.

After `worker-run`, the runtime has:

- a completed run receipt
- a markdown artifact
- a next safe action

After the terminal is closed and reopened, the next session can run:

```bash
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" artifact-path
```

The agent can then say:

```text
I found the local Watchtower state. The last bounded step completed, the artifact is here, and the next safe action is recorded. I can continue from that instead of asking you to explain everything again.
```

## Before And After

Before Watchtower:

```text
Human: Where did you stop?
Agent: I do not have the previous session context. Please explain the task again.
```

After Watchtower:

```text
Human: Where did you stop?
Agent: I checked the local Watchtower state. The last artifact is recorded, the task status is known, and the next safe action is available.
```

That is the v0 promise: not full autonomy, not memory magic, just a reliable local continuity record for interrupted coding-agent work.
