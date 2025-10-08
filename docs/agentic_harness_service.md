# Talekeeper Agentic Harness Windows Service

This document explains how to run the Talekeeper agentic harness on Windows and how it collaborates with the Claude Code
Visual Studio Code extension to deliver verified work.

## Overview
The harness continuously reviews the planning document (`docs/agentic_harness_plan.yaml`), assigns the next open task to
Claude Code, and requires successful Qt6 functional tests before marking the task as complete. Every test run must prove
that the user-facing behaviour is present in the game UI. After verification succeeds the harness prompts Claude Code to
update the planning document with a summary of the work and the associated evidence.

## Service Components
- **Planning document** – YAML file that lists each automation task, their required Qt6 tests, and any documentation that
  must be updated.
- **Reference document** – Read-only markdown file (`docs/agentic_harness_reference.md`) that describes the non-negotiable
  acceptance criteria and required Qt6 tests.
- **Qt6 verifier** – Executes the specified pytest cases (usually from the `tests/` folder) and captures stdout/stderr as
  proof of success or failure.
- **Claude Code interface** – Sends JSON payloads to the Claude Code extension via the VS Code command line or a file
  inbox specified by `CLAUDE_CODE_INBOX`.

## Installation
1. Ensure Python and the Talekeeper dependencies are installed, including the optional `PyYAML` dependency.
2. Install `pywin32` to enable Python Windows services.
3. From an elevated command prompt, install the service:
   ```powershell
   python -m talekeeper.services.agentic_harness.service install
   ```
4. Start the service:
   ```powershell
   python -m talekeeper.services.agentic_harness.service start
   ```

## Configuration Options
The harness reads the following environment variables:
- `VSCODE_CLAUDE_BINARY` – override the `code` executable used to issue commands.
- `VSCODE_CLAUDE_COMMAND` – command identifier inside VS Code (defaults to `claude-code.runTask`).
- `CLAUDE_CODE_INBOX` – path to a file inbox; when set the harness writes payloads instead of calling the CLI, allowing
  the VS Code extension to poll the file for new instructions.

The default configuration expects the planning document to live at `docs/agentic_harness_plan.yaml` and the reference
criteria at `docs/agentic_harness_reference.md`. Update these paths inside `AgenticHarnessConfig` if your project uses a
different structure.

## Operational Flow
1. **Task selection** – The harness looks for tasks marked `pending` or `needs_revision` in the planning document.
2. **Instruction dispatch** – It sends Claude Code a JSON payload containing the task summary, required tests, and
   context from the reference document.
3. **Verification** – The harness runs the Qt6 tests listed for the task. Failures create remediation subtasks and trigger
   a revision prompt for Claude Code.
4. **Documentation hand-off** – After the tests succeed, the harness requests that Claude Code updates the planning
   document and any target documentation.
5. **Completion** – The task is marked `completed`, including timestamps and captured stdout/stderr from the successful
   tests. The harness then moves to the next pending task.

## Troubleshooting
- Review the `pauses` section of the planning document to see why the harness stopped processing tasks.
- Each task retains a history of status changes, retries, and subtask creation, making it easier to resume progress when
  the service restarts.
- The `CLAUDE_CODE_INBOX` integration is useful during development because it allows inspection of the payloads the
  harness sends to Claude Code without needing to run VS Code.

