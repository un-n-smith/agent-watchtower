from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import Goal, RunReceipt, WorkTask, utc_now
from .store import InvalidRuntimeStateError, WatchtowerStore


DEMO_GOAL_ID = "goal-watchtower-demo"
DEMO_TASK_ID = "task-watchtower-demo-first-step"


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return slug or "artifact"


def _generated_task_id(title: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", title.lower()).strip("-")
    if slug:
        return f"task-{slug}"
    digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]
    return f"task-artifact-{digest}"


def _validate_goals(goals: list[dict], store: WatchtowerStore) -> None:
    for index, goal in enumerate(goals):
        if not isinstance(goal, dict):
            raise InvalidRuntimeStateError(
                "invalid_goals_json",
                store.goals_path,
                f"goal at index {index} must be an object",
            )
        if "id" in goal and not isinstance(goal["id"], str):
            raise InvalidRuntimeStateError(
                "invalid_goals_json",
                store.goals_path,
                f"goal at index {index} has non-string id",
            )


def _validate_work_queue(queue: list[dict], store: WatchtowerStore) -> None:
    for index, task in enumerate(queue):
        if not isinstance(task, dict):
            raise InvalidRuntimeStateError(
                "invalid_work_queue_json",
                store.work_queue_path,
                f"task at index {index} must be an object",
            )
        try:
            int(task.get("priority", 100))
        except (TypeError, ValueError) as error:
            raise InvalidRuntimeStateError(
                "invalid_work_queue_json",
                store.work_queue_path,
                f"task at index {index} has non-integer priority",
            ) from error


def _validate_run_receipts(receipts: list[dict], store: WatchtowerStore) -> None:
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict):
            raise InvalidRuntimeStateError(
                "invalid_run_receipts_json",
                store.run_receipts_path,
                f"receipt at index {index} must be an object",
            )


def _read_goals_and_queue(store: WatchtowerStore) -> tuple[list[dict], list[dict]]:
    goals = store.read_goals()
    queue = store.read_work_queue()
    _validate_goals(goals, store)
    _validate_work_queue(queue, store)
    return goals, queue


def _read_runtime(store: WatchtowerStore) -> tuple[list[dict], list[dict], list[dict]]:
    goals, queue = _read_goals_and_queue(store)
    receipts = store.read_run_receipts()
    _validate_run_receipts(receipts, store)
    return goals, queue, receipts


def _active_goal_ids(goals: list[dict]) -> set[str]:
    return {goal["id"] for goal in goals if goal.get("id") and goal.get("status", "active") == "active"}


def _open_tasks(queue: list[dict], active_goal_ids: set[str]) -> list[dict]:
    return sorted(
        [
            task
            for task in queue
            if task.get("status") == "open" and task.get("goal_id") in active_goal_ids
        ],
        key=lambda row: (int(row.get("priority", 100)), row.get("created_at", ""), row.get("id", "")),
    )


def _latest_artifact(receipts: list[dict]) -> str:
    for receipt in reversed(receipts):
        if receipt.get("artifact_path"):
            return receipt["artifact_path"]
    return ""


def init_runtime(store: WatchtowerStore) -> dict:
    store.ensure()
    goals = store.read_goals()
    queue = store.read_work_queue()
    now = utc_now()

    if not goals:
        goals = [
            Goal(
                id=DEMO_GOAL_ID,
                title="Keep one coding-agent work loop recoverable",
                created_at=now,
                success_criteria=[
                    "The next task is visible after interruption.",
                    "The latest artifact path is discoverable.",
                    "The run receipt explains what happened.",
                ],
            ).to_dict()
        ]
        store.write_goals(goals)

    if not queue:
        queue = [
            WorkTask(
                id=DEMO_TASK_ID,
                goal_id=goals[0]["id"],
                title="Write the first continuity artifact",
                next_action="write one local artifact and record the next safe action",
                done_definition="A markdown artifact exists and worker-status can report completion.",
                created_at=now,
                updated_at=now,
                priority=10,
            ).to_dict()
        ]
        store.write_work_queue(queue)

    return {
        "action": "initialized",
        "root": str(store.root),
        "goal_count": len(goals),
        "open_task_count": len([task for task in queue if task.get("status") == "open"]),
        "next_safe_action": "run worker-status, then worker-run",
    }


def add_task(
    store: WatchtowerStore,
    title: str,
    next_action: str,
    goal_id: str = DEMO_GOAL_ID,
    task_id: str = "",
    priority: int = 100,
    done_definition: str = "",
) -> dict:
    store.ensure()
    try:
        goals, queue = _read_goals_and_queue(store)
    except InvalidRuntimeStateError as error:
        return _invalid_state_response(error)
    active_goals = _active_goal_ids(goals)
    if goal_id not in active_goals:
        return {
            "action": "blocked",
            "reason": "unknown_or_inactive_goal",
            "goal_id": goal_id,
            "next_safe_action": "run init or choose an active goal id",
        }

    now = utc_now()
    new_task = WorkTask(
        id=task_id or _generated_task_id(title),
        goal_id=goal_id,
        title=title,
        next_action=next_action,
        done_definition=done_definition,
        created_at=now,
        updated_at=now,
        priority=priority,
    ).to_dict()
    if any(task.get("id") == new_task["id"] for task in queue):
        return {
            "action": "duplicate",
            "task_id": new_task["id"],
            "message": "Task already exists; no duplicate was added.",
        }
    queue.append(new_task)
    store.write_work_queue(queue)
    return {"action": "added", "task": new_task}


def _invalid_state_response(error: InvalidRuntimeStateError) -> dict:
    return {
        "summary": "Runtime state is invalid.",
        "runnable": False,
        "state_health": "blocked",
        "reason": "invalid_runtime_state",
        "diagnostics": [error.to_dict()],
        "next_safe_action": f"repair or replace {Path(error.path).name}, then run worker-status again",
    }


def worker_status(store: WatchtowerStore) -> dict:
    try:
        goals, queue, receipts = _read_runtime(store)
    except InvalidRuntimeStateError as error:
        return _invalid_state_response(error)

    active_goals = _active_goal_ids(goals)
    open_tasks = _open_tasks(queue, active_goals)
    next_task = open_tasks[0] if open_tasks else {}
    latest_artifact = _latest_artifact(receipts)
    return {
        "summary": (
            f"{len(open_tasks)} open task(s) ready."
            if open_tasks
            else "No runnable task is open."
        ),
        "runnable": bool(open_tasks),
        "state_health": "ok",
        "reason": "open_task" if open_tasks else "no_open_task",
        "goal_count": len(goals),
        "active_goal_count": len(active_goals),
        "open_task_count": len(open_tasks),
        "next_task": next_task,
        "latest_artifact_path": latest_artifact,
        "next_safe_action": (
            next_task.get("next_action", "run worker-run") if next_task else "add a bounded task with task-add"
        ),
    }


def _artifact_path(store: WatchtowerStore, task: dict) -> Path:
    if task.get("artifact_path"):
        path = Path(task["artifact_path"]).expanduser()
    else:
        path = store.work_artifacts_dir / f"{_safe_slug(task.get('id', 'artifact'))}.md"
        task["artifact_path"] = str(path)
    artifact_root = store.work_artifacts_dir.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(artifact_root)
    except ValueError:
        path = store.work_artifacts_dir / f"{_safe_slug(task.get('id', 'artifact'))}.md"
        task["artifact_path"] = str(path)
    return path


def _render_artifact(task: dict, goal: dict, artifact_path: Path, next_safe_action: str, created_at: str) -> str:
    criteria = goal.get("success_criteria", [])
    criteria_lines = [f"- {item}" for item in criteria] or ["- No success criteria recorded."]
    return "\n".join(
        [
            f"# Worker Run: {task.get('title', task.get('id', 'untitled task'))}",
            "",
            f"- Created at: {created_at}",
            f"- Goal: {goal.get('title', task.get('goal_id', 'unknown goal'))}",
            f"- Task id: {task.get('id', '')}",
            f"- Selected action: {task.get('next_action', '')}",
            f"- Artifact path: {artifact_path}",
            "",
            "## Result",
            "",
            "Completed one bounded local step and recorded the work in durable state.",
            "",
            "## Goal Success Criteria",
            "",
            *criteria_lines,
            "",
            "## Next Safe Action",
            "",
            next_safe_action,
            "",
        ]
    )


def worker_run(store: WatchtowerStore) -> dict:
    try:
        goals, queue, receipts = _read_runtime(store)
    except InvalidRuntimeStateError as error:
        return _invalid_state_response(error)

    active_goals = {goal["id"]: goal for goal in goals if goal.get("status", "active") == "active"}
    open_tasks = _open_tasks(queue, set(active_goals))
    if not open_tasks:
        return {
            "action": "no_op",
            "status": "idle",
            "reason": "no_open_task",
            "next_safe_action": "add a bounded task with task-add",
        }

    task = open_tasks[0]
    goal = active_goals[task["goal_id"]]
    remaining = [item for item in open_tasks[1:] if item.get("id") != task.get("id")]
    next_safe_action = (
        remaining[0].get("next_action", "run worker-run") if remaining else "add a bounded task with task-add"
    )
    created_at = utc_now()
    artifact_path = _artifact_path(store, task)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        _render_artifact(task, goal, artifact_path, next_safe_action, created_at),
        encoding="utf-8",
    )

    for item in queue:
        if item.get("id") == task.get("id"):
            item["status"] = "done"
            item["updated_at"] = created_at
            item["artifact_path"] = str(artifact_path)
            break
    store.write_work_queue(queue)

    receipt = RunReceipt(
        run_id=f"run-{_safe_slug(task.get('id', 'task'))}-{created_at.replace(':', '').replace('-', '')}",
        task_id=task["id"],
        task_title=task.get("title", ""),
        goal_id=task["goal_id"],
        status="done",
        artifact_path=str(artifact_path),
        next_safe_action=next_safe_action,
        created_at=created_at,
    ).to_dict()
    receipts.append(receipt)
    store.write_run_receipts(receipts)
    store.append_worker_run(receipt)
    return {"action": "completed_task", **receipt}


def artifact_path(store: WatchtowerStore, task_id: str = "") -> dict:
    try:
        receipts = store.read_run_receipts()
        _validate_run_receipts(receipts, store)
    except InvalidRuntimeStateError as error:
        return _invalid_state_response(error)
    selected = None
    for receipt in reversed(receipts):
        if task_id and receipt.get("task_id") != task_id:
            continue
        if receipt.get("artifact_path"):
            selected = receipt
            break
    if selected is None:
        return {
            "artifact_path": "",
            "message": "No artifact has been recorded yet.",
            "next_safe_action": "run worker-run after adding or initializing a task",
        }
    return {
        "artifact_path": selected["artifact_path"],
        "task_id": selected.get("task_id", ""),
        "exists": Path(selected["artifact_path"]).exists(),
    }
