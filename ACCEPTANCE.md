# Acceptance

Agent Watchtower Core v0 is acceptable when a clean local runtime can prove this loop:

```text
init -> worker-status -> worker-run -> artifact-path
```

## Checks

- Top-level help lists only `init`, `task-add`, `worker-status`, `worker-run`, and `artifact-path`.
- Package metadata requires Python 3.11+ and no external service configuration.
- `init` creates one demo goal and one open task in an empty runtime directory.
- `worker-status` reports a runnable task before execution.
- `worker-run` completes one bounded local step and writes a markdown artifact.
- `artifact-path` returns a path that exists on disk.
- `run-receipts.json` records the completed run and leaves a readable next action.
- Invalid `goals.json` or `work-queue.json` returns structured diagnostics instead of a traceback.

Run:

```bash
./scripts/acceptance_v0.sh
```

Optional release packaging check:

```bash
./scripts/release_preflight.sh
```
