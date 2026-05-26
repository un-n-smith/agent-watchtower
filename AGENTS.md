# Agent Watchtower Usage Rules For Coding Agents

This file is for coding agents and agent harnesses. Human users can read `README.md` first.

Agent Watchtower is a local continuity CLI. Use it to leave a durable trail of:

- the current goal
- the next safe action
- the latest work artifact
- the run receipt for the last bounded step

It does not replace your reasoning. It does not run a background service. It does not call external APIs.

## What This Solves

For the human, it solves the "AI work got interrupted" problem:

- The terminal closed.
- The computer restarted.
- The chat became too long.
- The user came back later.
- A different agent window or tool needs to continue.

For the agent, it solves the "I lost my place" problem:

- You may lose chat context.
- You may be restarted in a new session.
- You may need to continue work started by another agent.
- You may need to explain clearly what happened without guessing.

Use Watchtower to avoid asking the human to explain everything again when local continuity state already exists.

## Public Commands

Use only these commands:

```text
agent-watchtower init
agent-watchtower task-add
agent-watchtower worker-status
agent-watchtower worker-run
agent-watchtower artifact-path
```

Use `--root <dir>` when the user or project requires project-local state.

## When Starting Work

1. Run `agent-watchtower worker-status`.
2. If the runtime does not exist, run `agent-watchtower init`.
3. If `goal_count` is `0`, run `agent-watchtower init` before adding tasks.
4. If there is a runnable task, inspect `next_safe_action` and continue from there.
5. If there is no runnable task and the user gave a concrete goal, add one bounded task with `task-add`.

Do not ask the human to repeat old context until you have checked Watchtower state.

## When Talking With The Human

Explain Watchtower in plain language. Do not start with internal terms like "run receipt", "queue", or "artifact" unless the human asks.

Good explanation:

```text
This is a work notebook for AI agents. If the chat stops, the computer restarts, or we switch tools, I can look at the local record and see what I was doing, what I should do next, and where the last useful file is.
```

If the human asks why it helps you as an agent, say:

```text
It helps me avoid losing my place. Instead of guessing after an interruption, I can read the last goal, next step, and result file, then continue from there.
```

If the human is worried it is too big or too automatic, say:

```text
It is not a new AI and it does not take over the computer. It only writes a small local record so interrupted work can resume more cleanly.
```

## When The Human Does Not Reply

Do not wait forever just because a message was sent to the human.

Use this rule:

1. If the next action is safe, local, reversible, and already implied by the goal, continue working.
2. If the next action requires money, credentials, account changes, destructive edits, legal/business confirmation, or a subjective product decision, stop and ask.
3. If you asked the human a question but there is still safe local work available, record the waiting point in your status message or artifact, then continue with the safe work.
4. If there is no safe next action, report the blocker and preserve the current state with Watchtower.

The goal is not to ignore the human. The goal is to avoid unnecessary dead time when the work can safely continue.

Plain explanation to the human:

```text
I asked you about the part that needs your judgment. While waiting, I continued the safe local work and recorded where I stopped, so we do not lose the thread.
```

## When Adding A Task

Add only one bounded task at a time:

```bash
agent-watchtower task-add \
  --title "Short task title" \
  --next-action "the next safe concrete action" \
  --done-definition "what evidence proves this small step is done"
```

A good task is small enough to complete in one worker cycle and concrete enough that another agent can resume it later.

If you started a task and were interrupted before completion, record it as in progress:

```bash
agent-watchtower task-add \
  --title "Continue interrupted task" \
  --next-action "resume the concrete safe action" \
  --status in_progress
```

## When Completing A Step

After you do the real local work, record the actual result. Prefer a concise markdown result over a generic completion note.

```bash
agent-watchtower worker-run --result "What changed, what was verified, and where the useful output is."
```

Then read the JSON output:

- `action`
- `task_id`
- `artifact_path`
- `next_safe_action`

If `action` is `completed_task`, mention the artifact path when reporting status.

If there is another safe task after this one, continue with the next bounded step instead of asking the human to tell you to continue.

If the result is too long for a shell argument, write it to a file and run:

```bash
agent-watchtower worker-run --result-file result.md
```

## When Resuming After Interruption

Run:

```bash
agent-watchtower worker-status
agent-watchtower artifact-path
```

Use the latest artifact and `next_safe_action` to rebuild context before asking the user for help.

For agents that need a stricter machine-oriented prompt, see `AGENTS.structured.md`.

## What Not To Do

- Do not invent tasks that are not grounded in the user's goal or the project state.
- Do not claim work is complete unless a real artifact or verification result exists.
- Do not promise that Watchtower can automatically finish an entire project by itself.
- Do not treat Watchtower as a daemon, scheduler, memory database, messaging system, or multi-agent platform.
- Do not call external services, spend money, modify credentials, or touch real accounts because of this file.
- Do not expose private local paths in public documentation.

## Human-Facing Explanation

If a human asks what this tool does, explain it simply:

```text
It helps an AI coding agent avoid losing its place. It records what the goal is, what the next safe step is, and where the last artifact is, so interrupted work can resume without starting over.
```
