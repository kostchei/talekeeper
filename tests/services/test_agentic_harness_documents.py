"""Unit tests for the agentic harness planning and reference modules."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from talekeeper.services.agentic_harness.claude_interface import ClaudeCodeInterface
from talekeeper.services.agentic_harness.planning import PlanningDocument, TaskRecord
from talekeeper.services.agentic_harness.qt_test_verifier import QtTestVerifier
from talekeeper.services.agentic_harness.reference import ReferenceDocument


def test_planning_document_tracks_status(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.yaml"
    document = PlanningDocument(plan_path)

    task = TaskRecord(
        task_id="example",
        description="Example task",
        tests=["tests/sample.py::test_ok"],
        documentation_targets=["docs/example.md"],
    )
    document.update_task(task)

    fetched = document.get_next_task()
    assert fetched is not None
    assert fetched.task_id == "example"

    document.mark_status("example", "in_progress", note="started")
    document.record_failure("example", "Assertion failed", tests=task.tests)
    document.mark_status("example", "needs_revision")
    refreshed = PlanningDocument(plan_path)
    saved_task = refreshed.get_next_task(allowed_statuses=["needs_revision"])
    assert saved_task is not None
    assert saved_task.retries == 1
    assert saved_task.subtasks, "Failure should have created a remediation subtask"

    document.record_success("example", "All tests passed")
    completed = document.get_next_task(allowed_statuses=["completed"])
    assert completed is not None
    assert completed.status == "completed"
    assert completed.last_success_at is not None

    document.record_pause("manual stop")
    stored = document.to_dict()
    assert stored["pauses"], "Pause entries should be recorded"


def test_reference_document_parses_sections(tmp_path: Path) -> None:
    reference_path = tmp_path / "reference.md"
    reference_path.write_text(
        """# Reference\n\n## Objective\nDo the thing.\n\n## Acceptance Criteria\n- first\n- second\n\n## Required Qt6 Tests\n- a\n- b\n""",
        encoding="utf-8",
    )
    reference = ReferenceDocument.load(reference_path)
    assert reference.final_objective == "Do the thing."
    assert reference.acceptance_criteria == ["first", "second"]
    assert reference.required_tests == ["a", "b"]


def test_claude_interface_writes_inbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inbox_path = tmp_path / "inbox.json"
    monkeypatch.setenv("CLAUDE_CODE_INBOX", str(inbox_path))
    interface = ClaudeCodeInterface(inbox_path=inbox_path)
    task = TaskRecord(task_id="t1", description="Example", tests=[], documentation_targets=[])
    result = interface.send_task(task, context={"demo": True})
    assert result.payload_path == inbox_path
    payload = json.loads(inbox_path.read_text(encoding="utf-8"))
    assert payload["task"]["id"] == "t1"
    assert payload["context"]["demo"] is True


def test_qt_test_verifier_runs_pytest(tmp_path: Path) -> None:
    test_file = tmp_path / "test_example.py"
    test_file.write_text(
        """def test_ok():\n    assert True\n""",
        encoding="utf-8",
    )
    verifier = QtTestVerifier(working_directory=tmp_path)
    result = verifier.run_tests([str(test_file)])
    assert result.success
    assert "1 passed" in result.output


