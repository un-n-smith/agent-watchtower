from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


class InvalidRuntimeStateError(Exception):
    def __init__(self, code: str, path: Path, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def to_dict(self) -> dict:
        return {"code": self.code, "path": str(self.path), "message": self.message}


class WatchtowerStore:
    def __init__(self, root: Path):
        self.root = root.expanduser()
        self.goals_path = self.root / "goals.json"
        self.work_queue_path = self.root / "work-queue.json"
        self.run_receipts_path = self.root / "run-receipts.json"
        self.worker_runs_path = self.root / "worker-runs.jsonl"
        self.work_artifacts_dir = self.root / "work-artifacts"

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.work_artifacts_dir.mkdir(parents=True, exist_ok=True)
        if not self.goals_path.exists():
            self.write_goals([])
        if not self.work_queue_path.exists():
            self.write_work_queue([])
        if not self.run_receipts_path.exists():
            self.write_run_receipts([])
        if not self.worker_runs_path.exists():
            self.worker_runs_path.write_text("", encoding="utf-8")

    def _read_json(self, path: Path, code: str) -> list[dict]:
        self.ensure()
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise InvalidRuntimeStateError(code, path, str(error)) from error
        if not isinstance(value, list):
            raise InvalidRuntimeStateError(code, path, "expected a JSON array")
        return value

    def _atomic_write_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                delete=False,
                dir=path.parent,
                encoding="utf-8",
                prefix=f".{path.name}.",
                suffix=".tmp",
            ) as handle:
                temp_path = Path(handle.name)
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
            temp_path = None
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink()
                except FileNotFoundError:
                    pass

    def read_goals(self) -> list[dict]:
        return self._read_json(self.goals_path, "invalid_goals_json")

    def write_goals(self, goals: list[dict]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._atomic_write_text(
            self.goals_path,
            json.dumps(goals, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )

    def read_work_queue(self) -> list[dict]:
        return self._read_json(self.work_queue_path, "invalid_work_queue_json")

    def write_work_queue(self, queue: list[dict]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._atomic_write_text(
            self.work_queue_path,
            json.dumps(queue, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )

    def read_run_receipts(self) -> list[dict]:
        return self._read_json(self.run_receipts_path, "invalid_run_receipts_json")

    def write_run_receipts(self, receipts: list[dict]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._atomic_write_text(
            self.run_receipts_path,
            json.dumps(receipts, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )

    def append_worker_run(self, run: dict) -> None:
        self.ensure()
        with self.worker_runs_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(run, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
