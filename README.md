# Agent Watchtower Core

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![OS](https://img.shields.io/badge/os-macOS%20%7C%20Linux%20%7C%20Windows-informational.svg)](#supported-systems)
[![CLI](https://img.shields.io/badge/interface-CLI-informational.svg)](#commands)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#boundaries)

**Languages:** English | [Simplified Chinese](README.zh-CN.md)

**Close the terminal, come back later, and your agent can check where to resume.**

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
agent-watchtower --root "$ROOT" worker-run --result "Created the first continuity artifact and verified the local receipt."
agent-watchtower --root "$ROOT" artifact-path
```

You should see one runnable task, one completed worker run, and one markdown artifact path.

Close the terminal. Come back later. The local Watchtower files still say what happened and where the next session should resume.

For a clearer before/after story, see the [interrupted recovery demo](https://github.com/un-n-smith/agent-watchtower/blob/main/docs/interrupted-recovery-demo.md).

## Two Readers

There are two different readers:

- Humans read this `README.md` to understand what the tool does and how to try it.
- Coding agents read [AGENTS.md](https://github.com/un-n-smith/agent-watchtower/blob/main/AGENTS.md) to learn exactly when and how to call the five public commands.
- Agents that need a stricter prompt can read [AGENTS.structured.md](https://github.com/un-n-smith/agent-watchtower/blob/main/AGENTS.structured.md).

The README explains the value. Agent instruction files explain the operating rules.

## Website

- English: http://www.adgwmuren.top/
- Chinese: http://www.adgwmuren.top/zh-CN.html

HTTPS is pending on GitHub Pages while the certificate is being issued.

## Install

Requirements:

- Python 3.11+
- A writable local runtime directory
- No background service, external account, or network dependency

## Supported Systems

Agent Watchtower is a plain Python CLI that stores local JSON and markdown files.

- macOS: tested in the current release flow.
- Linux: supported target with Python 3.11+.
- Windows: supported target with Python 3.11+; use `pip`, `pipx`, or `uv` instead of Homebrew.

### From PyPI

```bash
python3 -m pip install agent-watchtower-core
```

### Homebrew

```bash
brew tap un-n-smith/tap
brew install agent-watchtower
```

### From GitHub

```bash
python3 -m pip install "agent-watchtower-core @ git+https://github.com/un-n-smith/agent-watchtower.git"
```

### Pipx And Uv

For isolated CLI installs, `pipx` is also clean:

```bash
pipx install agent-watchtower-core
```

Or with `uv`:

```bash
uv tool install agent-watchtower-core
```

### From A Local Checkout

```bash
python3 -m pip install .
```

After install, the CLI is:

```bash
agent-watchtower --help
agent-watchtower --version
```

For development without installing:

```bash
PYTHONPATH=src python3 -m agent_watchtower.cli --help
```

## Run a local demo

For the default local runtime:

```bash
agent-watchtower init
agent-watchtower worker-status
agent-watchtower worker-run --result "Created the first continuity artifact and verified the local receipt."
agent-watchtower artifact-path
```

For a disposable demo runtime:

```bash
ROOT="$(mktemp -d)"
agent-watchtower --root "$ROOT" init
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" worker-run --result "Created the first continuity artifact and verified the local receipt."
agent-watchtower --root "$ROOT" artifact-path
```

What to look for:

- `worker-status` shows whether one task is runnable.
- `worker-run --result ...` writes the actual work result into one markdown artifact and records one run receipt.
- `artifact-path` prints the latest artifact path.
- `run-receipts.json` records the completed bounded step and next safe action.

After this, close the terminal and come back later. The point is that the local files still say what happened and where to resume.

## Use it in a real project

For project-local state, use a local Watchtower root:

```bash
agent-watchtower --root .watchtower init
agent-watchtower --root .watchtower task-add \
  --title "Inspect repository status" \
  --next-action "run git status and summarize pending changes" \
  --done-definition "artifact explains changed files and next safe action"
```

After doing the real work, record the actual result:

```bash
agent-watchtower --root .watchtower worker-run \
  --result "Ran git status. Found docs changes in README.md and no source changes."
agent-watchtower --root .watchtower artifact-path
```

The next agent can run `worker-status` and `artifact-path` before asking the human to repeat context.

## Why not TODO.md?

A plain TODO file is useful, but every agent has to guess its format. Watchtower gives agents a small fixed protocol:

- fixed files for goals, queue, receipts, and artifacts
- fixed CLI commands that any local coding agent can call
- separate records for what happened, where the result is, and what is safe to do next

If you want a stricter release check from a source checkout, run:

```bash
./scripts/release_preflight.sh
```

For a scripted interruption demo from a source checkout, run:

```bash
./scripts/demo_interrupted_recovery.sh
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

For install, acceptance, and cleanup notes, see [PACKAGING.md](https://github.com/un-n-smith/agent-watchtower/blob/main/PACKAGING.md).

## Feedback

This is an alpha project. Real interrupted-agent stories are more useful than abstract feature requests.

Please open an issue if:

- your agent lost track of work and Watchtower helped
- your agent could not understand the Watchtower state
- the install or quick demo failed
- you found a clearer way to explain this problem

Useful feedback includes:

- which agent you used
- your operating system and Python version
- the commands you ran
- the `artifact-path` output
- whether the next session could resume without you explaining everything again

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
