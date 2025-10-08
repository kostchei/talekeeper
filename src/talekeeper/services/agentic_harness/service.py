"""Windows service orchestration for the Claude Code agentic harness."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .claude_interface import ClaudeCodeInterface
from .planning import PlanningDocument, TaskRecord
from .qt_test_verifier import QtTestVerifier
from .reference import ReferenceDocument

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - Windows-specific modules are optional in tests
    import win32event
    import win32service
    import win32serviceutil
    import servicemanager
except ImportError:  # pragma: no cover
    win32event = None
    win32service = None
    win32serviceutil = None
    servicemanager = None


@dataclass
class AgenticHarnessConfig:
    """Runtime configuration for the agentic harness."""

    planning_document: Path
    reference_document: Path
    idle_sleep_seconds: int = 120
    retry_sleep_seconds: int = 300
    max_retries: int = 5


class AgenticHarness:
    """Core orchestration logic for the automation harness."""

    def __init__(
        self,
        planning_document: PlanningDocument,
        reference_document: ReferenceDocument,
        claude_interface: ClaudeCodeInterface,
        qt_verifier: QtTestVerifier,
        *,
        config: Optional[AgenticHarnessConfig] = None,
    ) -> None:
        self.planning_document = planning_document
        self.reference_document = reference_document
        self.claude_interface = claude_interface
        self.qt_verifier = qt_verifier
        self.config = config or AgenticHarnessConfig(
            planning_document=planning_document.path,
            reference_document=reference_document.path,
        )
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------
    def run(self) -> None:
        LOGGER.info("Starting agentic harness loop")
        while not self._stop_event.is_set():
            task = self.planning_document.get_next_task()
            if not task:
                LOGGER.debug("No pending tasks found; sleeping for %s seconds", self.config.idle_sleep_seconds)
                time.sleep(self.config.idle_sleep_seconds)
                self.planning_document.record_pause("Idle - no pending tasks")
                continue

            LOGGER.info("Processing task %s", task.task_id)
            self._process_task(task)

    def stop(self) -> None:
        LOGGER.info("Stopping agentic harness loop")
        self._stop_event.set()
        self.planning_document.record_pause("Harness stop requested")

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------
    def _process_task(self, task: TaskRecord) -> None:
        self.planning_document.mark_status(task.task_id, "in_progress", note="Harness picked up task")
        context = self._build_task_context(task)
        result = self.claude_interface.send_task(task, context=context)
        LOGGER.debug("Sent task to Claude Code: %s", result.command)

        retries = 0
        max_retries = min(self.config.max_retries, task.max_retries)
        while not self._stop_event.is_set():
            verification = self.qt_verifier.run_tests(task.tests)
            if verification.success:
                LOGGER.info("Task %s passed verification", task.task_id)
                self.planning_document.record_success(task.task_id, verification.output)
                self.claude_interface.request_documentation_update(task, verification.output)
                break

            LOGGER.warning("Task %s verification failed; requesting revision", task.task_id)
            self.planning_document.record_failure(task.task_id, verification.output, tests=task.tests)
            self.claude_interface.request_revision(task, verification.output)
            retries += 1
            if retries >= max_retries:
                LOGGER.error("Task %s exceeded maximum retries; pausing", task.task_id)
                self.planning_document.record_pause(
                    f"Max retries exceeded for task {task.task_id}; awaiting manual intervention"
                )
                break
            LOGGER.debug(
                "Sleeping for %s seconds before retrying task %s",
                self.config.retry_sleep_seconds,
                task.task_id,
            )
            time.sleep(self.config.retry_sleep_seconds)

    def _build_task_context(self, task: TaskRecord) -> Dict[str, object]:
        return {
            "reference_objective": self.reference_document.final_objective,
            "acceptance_criteria": self.reference_document.acceptance_criteria,
            "required_tests": task.tests or self.reference_document.required_tests,
            "documentation_targets": task.documentation_targets,
        }


class AgenticHarnessServiceBase:  # pragma: no cover - service wrapper is not tested on CI
    """Base class wrapping the Windows service plumbing."""

    _svc_name_ = "TalekeeperAgenticHarness"
    _svc_display_name_ = "Talekeeper Agentic Harness"
    _svc_description_ = "Automates Claude Code tasks with Qt6 verification."

    def __init__(self, args):
        if win32serviceutil is None:
            raise RuntimeError("Windows service components are not available in this environment")
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.harness: Optional[AgenticHarness] = None

    def SvcStop(self):  # type: ignore[override]
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.harness:
            self.harness.stop()
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):  # type: ignore[override]
        servicemanager.LogInfoMsg("Talekeeper Agentic Harness service starting")
        try:
            self.harness = self.build_harness()
            self.harness.run()
        finally:
            servicemanager.LogInfoMsg("Talekeeper Agentic Harness service stopped")

    def build_harness(self) -> AgenticHarness:
        raise NotImplementedError


if win32serviceutil is not None:  # pragma: no cover
    class AgenticHarnessService(AgenticHarnessServiceBase, win32serviceutil.ServiceFramework):
        """Concrete Windows service implementation."""

        def build_harness(self) -> AgenticHarness:
            config = AgenticHarnessConfig(
                planning_document=Path("docs/agentic_harness_plan.yaml"),
                reference_document=Path("docs/agentic_harness_reference.md"),
            )
            planning = PlanningDocument(config.planning_document)
            reference = ReferenceDocument.load(config.reference_document)
            claude = ClaudeCodeInterface()
            verifier = QtTestVerifier()
            return AgenticHarness(planning, reference, claude, verifier, config=config)


__all__ = [
    "AgenticHarness",
    "AgenticHarnessConfig",
]


def main() -> None:  # pragma: no cover - entrypoint for Windows service tooling
    """Entry-point used for installing/running the Windows service."""

    if win32serviceutil is None:
        raise RuntimeError("Windows service utilities are not available on this platform")
    if "AgenticHarnessService" not in globals():
        raise RuntimeError("AgenticHarnessService is unavailable without pywin32 installed")
    service_class = globals()["AgenticHarnessService"]
    win32serviceutil.HandleCommandLine(service_class)  # type: ignore[arg-type]


if __name__ == "__main__":  # pragma: no cover
    main()

