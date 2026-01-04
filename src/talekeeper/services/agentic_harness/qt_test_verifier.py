"""Utilities for running Qt6 functional tests as proof of completion."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Sequence


LOGGER = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Outcome of a Qt6 verification test run."""

    success: bool
    command: List[str]
    output: str


class QtTestVerifier:
    """Runs Qt6-oriented pytest suites to validate Claude Code output."""

    def __init__(
        self,
        *,
        python_executable: str | None = None,
        working_directory: Path | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> None:
        self.python_executable = python_executable or sys.executable
        self.working_directory = working_directory
        self.extra_env = extra_env or {}

    def run_tests(self, tests: Sequence[str]) -> TestResult:
        """Run the given pytest tests and return the result."""

        if not tests:
            LOGGER.info("No tests specified for Qt verifier; treating as success.")
            return TestResult(success=True, command=[], output="No tests specified")

        command = [self.python_executable, "-m", "pytest", "-q"]
        command.extend(tests)
        env = os.environ.copy()
        env.update(self.extra_env)

        LOGGER.info("Running Qt verification: %s", " ".join(command))
        try:
            completed = subprocess.run(
                command,
                cwd=self.working_directory,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as error:
            LOGGER.exception("Failed to invoke pytest for Qt verification: %s", error)
            raise

        output = (completed.stdout or "") + (completed.stderr or "")
        success = completed.returncode == 0
        if success:
            LOGGER.info("Qt verification passed for tests: %s", tests)
        else:
            LOGGER.warning("Qt verification failed for tests %s with rc=%s", tests, completed.returncode)
        return TestResult(success=success, command=command, output=output)

    @staticmethod
    def expand_tests(tests: Iterable[str], *, base_directory: Path | None = None) -> List[str]:
        """Expand test paths relative to the provided base directory."""

        expanded: List[str] = []
        base = Path(base_directory) if base_directory else None
        for test in tests:
            candidate = Path(test)
            if base and not candidate.is_absolute():
                candidate = base / candidate
            expanded.append(str(candidate))
        return expanded

