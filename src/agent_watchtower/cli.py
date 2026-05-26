from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .store import WatchtowerStore
from .worker import add_task, artifact_path, init_runtime, worker_run, worker_status


DEFAULT_ROOT = Path("~/.agent-watchtower")


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-watchtower")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="initialize a clean local Watchtower runtime")

    status = sub.add_parser("worker-status", help="inspect runnable tasks and next safe action")
    status.add_argument("--compact", action="store_true", help="print one-line JSON")

    sub.add_parser("worker-run", help="run one bounded worker cycle")

    task_add = sub.add_parser("task-add", help="add one bounded worker task")
    task_add.add_argument("--title", required=True)
    task_add.add_argument("--next-action", required=True)
    task_add.add_argument("--goal-id", default="goal-watchtower-demo")
    task_add.add_argument("--task-id", default="")
    task_add.add_argument("--priority", type=int, default=100)
    task_add.add_argument("--done-definition", default="")

    artifact = sub.add_parser("artifact-path", help="print the latest or task-specific artifact path")
    artifact.add_argument("--task-id", default="")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = WatchtowerStore(Path(args.root))

    if args.command == "init":
        _print_json(init_runtime(store))
        return 0
    if args.command == "worker-status":
        payload = worker_status(store)
        if args.compact:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        else:
            _print_json(payload)
        return 0 if payload.get("state_health") != "blocked" else 1
    if args.command == "worker-run":
        payload = worker_run(store)
        _print_json(payload)
        return 0 if payload.get("state_health") != "blocked" else 1
    if args.command == "task-add":
        payload = add_task(
            store,
            title=args.title,
            next_action=args.next_action,
            goal_id=args.goal_id,
            task_id=args.task_id,
            priority=args.priority,
            done_definition=args.done_definition,
        )
        _print_json(payload)
        return 0 if payload.get("action") != "blocked" and payload.get("state_health") != "blocked" else 1
    if args.command == "artifact-path":
        payload = artifact_path(store, task_id=args.task_id)
        _print_json(payload)
        return 0 if payload.get("artifact_path") else 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
