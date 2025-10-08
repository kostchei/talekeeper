"""Planning document management for the agentic harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import threading
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


@dataclass
class SubtaskRecord:
    """Represents a remediation subtask captured in the planning document."""

    created_at: str
    summary: str
    details: str
    tests_attempted: List[str] = field(default_factory=list)


@dataclass
class TaskRecord:
    """Represents a single task tracked in the planning document."""

    task_id: str
    description: str
    status: str = "pending"
    tests: List[str] = field(default_factory=list)
    documentation_targets: List[str] = field(default_factory=list)
    subtasks: List[SubtaskRecord] = field(default_factory=list)
    history: List[Dict[str, str]] = field(default_factory=list)
    last_result: Optional[str] = None
    last_success_at: Optional[str] = None
    max_retries: int = 3
    retries: int = 0

    def to_dict(self) -> Dict[str, object]:
        """Convert the dataclass to a YAML-compatible dictionary."""

        return {
            "id": self.task_id,
            "description": self.description,
            "status": self.status,
            "tests": list(self.tests),
            "documentation_targets": list(self.documentation_targets),
            "subtasks": [
                {
                    "created_at": sub.created_at,
                    "summary": sub.summary,
                    "details": sub.details,
                    "tests_attempted": list(sub.tests_attempted),
                }
                for sub in self.subtasks
            ],
            "history": list(self.history),
            "last_result": self.last_result,
            "last_success_at": self.last_success_at,
            "max_retries": self.max_retries,
            "retries": self.retries,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "TaskRecord":
        """Create a :class:`TaskRecord` from YAML data."""

        subtasks = [
            SubtaskRecord(
                created_at=sub.get("created_at", ""),
                summary=sub.get("summary", ""),
                details=sub.get("details", ""),
                tests_attempted=list(sub.get("tests_attempted", [])),
            )
            for sub in data.get("subtasks", [])
        ]
        return cls(
            task_id=data.get("id", ""),
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            tests=list(data.get("tests", [])),
            documentation_targets=list(data.get("documentation_targets", [])),
            subtasks=subtasks,
            history=list(data.get("history", [])),
            last_result=data.get("last_result"),
            last_success_at=data.get("last_success_at"),
            max_retries=int(data.get("max_retries", 3)),
            retries=int(data.get("retries", 0)),
        )


class PlanningDocument:
    """Utility class for reading and writing the automation planning document."""

    def __init__(self, document_path: Path) -> None:
        self.path = Path(document_path)
        self._lock = threading.RLock()
        self._data: Dict[str, object] = {}
        self._tasks: List[TaskRecord] = []
        self.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Load the planning document from disk."""

        with self._lock:
            if not self.path.exists():
                self._data = self._default_document()
                self._tasks = [TaskRecord.from_dict(task) for task in self._data["tasks"]]
                self._write()
                return

            content = self.path.read_text(encoding="utf-8")
            raw = yaml.safe_load(content) or {}
            if "tasks" not in raw:
                raw["tasks"] = []

            self._data = raw
            self._tasks = [TaskRecord.from_dict(task) for task in raw["tasks"]]

    def list_tasks(self) -> List[TaskRecord]:
        """Return a copy of the tracked tasks."""

        with self._lock:
            return [TaskRecord.from_dict(task.to_dict()) for task in self._tasks]

    def get_next_task(self, *, allowed_statuses: Iterable[str] | None = None) -> Optional[TaskRecord]:
        """Return the next task that matches the allowed statuses."""

        if allowed_statuses is None:
            allowed_statuses = ("pending", "needs_revision")
        allowed = set(allowed_statuses)

        with self._lock:
            for task in self._tasks:
                if task.status in allowed:
                    return TaskRecord.from_dict(task.to_dict())
        return None

    def update_task(self, updated: TaskRecord) -> None:
        """Persist an updated task."""

        with self._lock:
            for idx, task in enumerate(self._tasks):
                if task.task_id == updated.task_id:
                    self._tasks[idx] = updated
                    break
            else:
                self._tasks.append(updated)
            self._data["tasks"] = [task.to_dict() for task in self._tasks]
            self._write()

    def mark_status(self, task_id: str, status: str, *, note: Optional[str] = None) -> TaskRecord:
        """Update the status of a task and persist the change."""

        with self._lock:
            task = self._get_task_mutable(task_id)
            timestamp = self._timestamp()
            history_entry = {"timestamp": timestamp, "status": status}
            if note:
                history_entry["note"] = note
            task.history.append(history_entry)
            task.status = status
            self.update_task(task)
            return TaskRecord.from_dict(task.to_dict())

    def append_subtask(
        self,
        task_id: str,
        summary: str,
        details: str,
        *,
        tests_attempted: Optional[Iterable[str]] = None,
    ) -> TaskRecord:
        """Record a new subtask entry when work is paused or fails."""

        with self._lock:
            task = self._get_task_mutable(task_id)
            subtask = SubtaskRecord(
                created_at=self._timestamp(),
                summary=summary,
                details=details,
                tests_attempted=list(tests_attempted or task.tests),
            )
            task.subtasks.append(subtask)
            note = f"Added subtask: {summary}"
            task.history.append({"timestamp": subtask.created_at, "status": task.status, "note": note})
            self.update_task(task)
            return TaskRecord.from_dict(task.to_dict())

    def record_failure(self, task_id: str, result: str, *, tests: Optional[Iterable[str]] = None) -> TaskRecord:
        """Record a failed verification attempt for a task."""

        with self._lock:
            task = self._get_task_mutable(task_id)
            task.last_result = result
            task.retries += 1
            task.status = "needs_revision"
            note = f"Verification failed (attempt {task.retries})"
            task.history.append({"timestamp": self._timestamp(), "status": task.status, "note": note})
            updated_tests = list(tests or task.tests)
            subtask = SubtaskRecord(
                created_at=self._timestamp(),
                summary="Verification failure",
                details=result,
                tests_attempted=updated_tests,
            )
            task.subtasks.append(subtask)
            task.history.append(
                {
                    "timestamp": subtask.created_at,
                    "status": task.status,
                    "note": "Created remediation subtask after failure",
                }
            )
            self.update_task(task)
            return TaskRecord.from_dict(task.to_dict())

    def record_success(self, task_id: str, result: str) -> TaskRecord:
        """Record a successful verification attempt."""

        with self._lock:
            task = self._get_task_mutable(task_id)
            task.last_result = result
            task.retries = 0
            task.status = "completed"
            timestamp = self._timestamp()
            task.last_success_at = timestamp
            task.history.append({"timestamp": timestamp, "status": "completed", "note": "Verification passed"})
            self.update_task(task)
            return TaskRecord.from_dict(task.to_dict())

    def to_dict(self) -> Dict[str, object]:
        """Return the current document representation."""

        with self._lock:
            data = dict(self._data)
            data["tasks"] = [task.to_dict() for task in self._tasks]
            return data

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _default_document(self) -> Dict[str, object]:
        return {
            "version": 1,
            "last_updated": self._timestamp(),
            "tasks": [],
            "pauses": [],
        }

    def _write(self) -> None:
        self._data["last_updated"] = self._timestamp()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self._data, handle, sort_keys=False)

    def _timestamp(self) -> str:
        return datetime.now().astimezone().strftime(ISO_FORMAT)

    def _get_task_mutable(self, task_id: str) -> TaskRecord:
        for task in self._tasks:
            if task.task_id == task_id:
                return task
        raise KeyError(f"Task '{task_id}' not found in planning document")

    # ------------------------------------------------------------------
    # Pause management
    # ------------------------------------------------------------------
    def record_pause(self, reason: str) -> None:
        """Record that the harness has paused execution."""

        with self._lock:
            pause_entry = {"timestamp": self._timestamp(), "reason": reason}
            pauses = list(self._data.get("pauses", []))
            pauses.append(pause_entry)
            self._data["pauses"] = pauses
            self._write()

