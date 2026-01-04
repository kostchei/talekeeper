"""Abstractions for interacting with the Claude Code VS Code extension."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .planning import TaskRecord

LOGGER = logging.getLogger(__name__)


@dataclass
class ClaudeCommandResult:
    """Represents the result of invoking a Claude Code command."""

    command: str
    payload_path: Optional[Path]
    return_code: Optional[int]
    stdout: str
    stderr: str


class ClaudeCodeInterface:
    """Thin wrapper around the VS Code Claude Code extension automation hooks."""

    def __init__(
        self,
        *,
        vscode_binary: str | None = None,
        command_id: str | None = None,
        inbox_path: Path | None = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> None:
        self.vscode_binary = vscode_binary or os.environ.get("VSCODE_CLAUDE_BINARY", "code")
        self.command_id = command_id or os.environ.get("VSCODE_CLAUDE_COMMAND", "claude-code.runTask")
        self.inbox_path = inbox_path or self._resolve_inbox()
        self.environment = environment or {}

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def send_task(self, task: TaskRecord, *, context: Dict[str, Any]) -> ClaudeCommandResult:
        """Send a task request to the Claude Code extension."""

        payload = self._build_payload("task", task, context)
        return self._deliver_payload(payload)

    def request_revision(self, task: TaskRecord, failure_output: str) -> ClaudeCommandResult:
        """Request a revision from Claude Code when verification fails."""

        context = {
            "failure_output": failure_output,
            "instructions": textwrap.dedent(
                """
                Verification failed. Investigate the failing Qt6 tests, address the issues, and prepare
                updated code along with documentation adjustments. Re-run the tests locally before marking
                the task ready again.
                """
            ).strip(),
        }
        payload = self._build_payload("revision", task, context)
        return self._deliver_payload(payload)

    def request_documentation_update(self, task: TaskRecord, proof: str) -> ClaudeCommandResult:
        """Ask Claude Code to document verified changes."""

        context = {
            "proof": proof,
            "instructions": textwrap.dedent(
                """
                Functional Qt6 verification has passed. Update the planning document with a summary of the
                work performed, reference the tests that prove the change, and ensure code documentation is
                aligned with the delivered behavior.
                """
            ).strip(),
        }
        payload = self._build_payload("documentation", task, context)
        return self._deliver_payload(payload)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_inbox(self) -> Optional[Path]:
        env_path = os.environ.get("CLAUDE_CODE_INBOX")
        return Path(env_path) if env_path else None

    def _build_payload(self, intent: str, task: TaskRecord, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "intent": intent,
            "task": {
                "id": task.task_id,
                "description": task.description,
                "tests": task.tests,
                "documentation_targets": task.documentation_targets,
            },
            "context": context,
        }

    def _deliver_payload(self, payload: Dict[str, Any]) -> ClaudeCommandResult:
        serialized = json.dumps(payload, indent=2)
        inbox_file: Optional[Path] = None
        stdout = ""
        stderr = ""
        return_code: Optional[int] = None

        if self.inbox_path:
            self.inbox_path.parent.mkdir(parents=True, exist_ok=True)
            inbox_file = self.inbox_path
            inbox_file.write_text(serialized, encoding="utf-8")
            LOGGER.info("Wrote Claude Code payload to inbox: %s", inbox_file)
            command_repr = f"write:{inbox_file}"
        else:
            command = [self.vscode_binary, "--command", self.command_id, serialized]
            env = os.environ.copy()
            env.update(self.environment)
            LOGGER.info("Invoking VS Code command: %s", " ".join(command))
            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    env=env,
                )
            except OSError as error:
                LOGGER.exception("Unable to invoke VS Code CLI for Claude Code: %s", error)
                raise
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            return_code = completed.returncode
            command_repr = " ".join(command)
        return ClaudeCommandResult(
            command=command_repr,
            payload_path=inbox_file,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
        )

