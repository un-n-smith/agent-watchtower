from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .store import WatchtowerStore
from .worker import add_task, artifact_path, init_runtime, worker_run, worker_status


DEFAULT_ROOT = Path("~/.agent-watchtower")


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-watchtower")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="initialize a clean local Watchtower runtime")

    status = sub.add_parser("worker-status", help="inspect runnable tasks and next safe action")
    status.add_argument("--compact", action="store_true", help="print one-line JSON")

    run = sub.add_parser("worker-run", help="run one bounded worker cycle")
    run.add_argument("--result", default="", help="markdown summary of the real work completed")
    run.add_argument(
        "--result-file",
        default="",
        help="read markdown result text from a file; use '-' to read stdin",
    )

    task_add = sub.add_parser("task-add", help="add one bounded worker task")
    task_add.add_argument("--title", required=True)
    task_add.add_argument("--next-action", required=True)
    task_add.add_argument("--goal-id", default="goal-watchtower-demo")
    task_add.add_argument("--task-id", default="")
    task_add.add_argument("--priority", type=int, default=100)
    task_add.add_argument("--status", choices=["open", "in_progress"], default="open")
    task_add.add_argument("--done-definition", default="")

    artifact = sub.add_parser("artifact-path", help="print the latest or task-specific artifact path")
    artifact.add_argument("--task-id", default="")

    return parser


def _load_result_text(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    parts = []
    if args.result:
        parts.append(args.result.strip("\n"))
    if args.result_file:
        try:
            if args.result_file == "-":
                file_text = sys.stdin.read()
            else:
                file_text = Path(args.result_file).read_text(encoding="utf-8")
        except OSError as error:
            parser.error(f"could not read --result-file: {error}")
        parts.append(file_text.strip("\n"))
    return "\n\n".join(part for part in parts if part)


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
        payload = worker_run(store, result=_load_result_text(args, parser))
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
            status=args.status,
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
