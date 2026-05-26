# Agent Watchtower Core

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![CLI](https://img.shields.io/badge/interface-CLI-informational.svg)](#commands)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#boundaries)

**关掉终端再打开，Agent 记得做到哪了。**

You use Codex, Claude Code, Hermes, CodeWhale, or another coding agent for a few hours. Then the terminal closes, the session gets interrupted, or the next window starts cold.

Agent Watchtower keeps the small local trail that matters, so the next session can continue instead of starting over:

- what the goal is
- what the next safe action is
- where the last artifact is

It is for people who have felt this pain:

```text
"My AI agent was working, then it stopped. Now I don't know what it finished, what it planned next, or where the useful output is."
```

It stores plain local files:

- `goals.json`
- `work-queue.json`
- `run-receipts.json`
- `work-artifacts/*.md`

In one sentence: Agent Watchtower is a tiny local CLI that lets coding agents leave behind goals, next actions, run receipts, and artifacts so interrupted work can resume without rebuilding context from chat.

## Quick Demo

```bash
ROOT="$(mktemp -d)"
agent-watchtower --root "$ROOT" init
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" worker-run
agent-watchtower --root "$ROOT" artifact-path
```

You should see one runnable task, one completed worker run, and one markdown artifact path.

Close the terminal. Come back later. The local Watchtower files still say what happened and where the next session should resume.

## Two Readers

There are two different readers:

- Humans read this `README.md` to understand what the tool does and how to try it.
- Coding agents read `AGENTS.md` to learn exactly when and how to call the five public commands.

The README explains the value. `AGENTS.md` explains the operating rules.

For a plainer Chinese introduction, see `docs/landing-page.zh.md`.

中文说明见 `README.zh-CN.md`。

## Install

Requirements:

- Python 3.11+
- A writable local runtime directory
- No background service, external account, or network dependency

### From GitHub

```bash
python3 -m pip install "agent-watchtower-core @ git+https://github.com/un-n-smith/agent-watchtower.git"
```

For isolated CLI installs, `pipx` is usually cleaner:

```bash
pipx install "git+https://github.com/un-n-smith/agent-watchtower.git"
```

Or with `uv`:

```bash
uv tool install "git+https://github.com/un-n-smith/agent-watchtower.git"
```

### From A Local Checkout

```bash
python3 -m pip install .
```

After install, the CLI is:

```bash
agent-watchtower --help
```

For development without installing:

```bash
PYTHONPATH=src python3 -m agent_watchtower.cli --help
```

### Homebrew

Homebrew support is planned after the first public release proves useful. For now, use `pipx`, `uv tool install`, or `pip install` from GitHub.

## 60 秒看到价值

For the default local runtime:

```bash
agent-watchtower init
agent-watchtower worker-status
agent-watchtower worker-run
agent-watchtower artifact-path
```

For a disposable demo runtime:

```bash
ROOT="$(mktemp -d)"
agent-watchtower --root "$ROOT" init
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" worker-run
agent-watchtower --root "$ROOT" artifact-path
```

What to look for:

- `worker-status` shows whether one task is runnable.
- `worker-run` writes one markdown artifact and records one run receipt.
- `artifact-path` prints the latest artifact path.
- `run-receipts.json` records the completed bounded step and next safe action.

After this, close the terminal and come back later. The point is that the local files still say what happened and where to resume.

If you want a stricter release check, run:

```bash
./scripts/release_preflight.sh
```

## Commands

Only these commands are part of v0:

```text
init
task-add
worker-status
worker-run
artifact-path
```

## Runtime

By default, data is stored under:

```text
~/.agent-watchtower
```

Use `--root <dir>` for tests, demos, or project-local state.

For install, acceptance, and cleanup notes, see `PACKAGING.md`.

## Feedback

This is an alpha project. Real interrupted-agent stories are more useful than abstract feature requests.

Please open an issue if:

- your agent lost track of work and Watchtower helped
- your agent could not understand the Watchtower state
- the install or quick demo failed
- you found a clearer way to explain this problem

User feedback is the main way this project gets better.

## Uninstall

```bash
python3 -m pip uninstall agent-watchtower-core
```

To remove local runtime data:

```bash
rm -rf ~/.agent-watchtower
```

## Boundaries

v0 is only a local continuity layer. It does not run a background service, create accounts, call external APIs, or claim to finish complex projects by itself.
