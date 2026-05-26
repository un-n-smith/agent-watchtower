from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class RuntimeErrorDiagnostic:
    code: str
    path: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Goal:
    id: str
    title: str
    created_at: str
    status: str = "active"
    success_criteria: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkTask:
    id: str
    goal_id: str
    title: str
    next_action: str
    created_at: str
    updated_at: str
    status: str = "open"
    priority: int = 100
    done_definition: str = ""
    artifact_path: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RunReceipt:
    run_id: str
    task_id: str
    task_title: str
    goal_id: str
    status: str
    artifact_path: str
    next_safe_action: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)
