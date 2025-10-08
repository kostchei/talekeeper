# Agentic Harness Design for TaleKeeper

## 1. Overview

This document outlines the design for an "agentic harness" to enable an AI coding assistant (the "Agent") to autonomously work on the TaleKeeper project. The primary objective is to systematically implement the features listed in the project's `ToDo` list, with the ultimate goal of achieving full mechanical implementation of the D&D 5e 2024 SRD.

The harness is a loop-driven system that provides the Agent with the tools and context necessary to:
1.  **Perceive**: Analyze the current state of the codebase, documentation, and goals.
2.  **Plan**: Break down high-level goals into concrete, verifiable implementation steps.
3.  **Act**: Modify the codebase, create new files, and run tests.
4.  **Verify**: Confirm that changes work as intended and don't introduce regressions.
5.  **Learn**: Incorporate feedback from failed tests or implementation issues into subsequent attempts.

This system is inspired by concepts from how-to-build-a-coding-agent and is designed to run as a persistent background process, as suggested by the `create-windows-service-for-agentic-harness` branch concept.

## 2. Core Goal

The Agent's long-term directive is:

> "Work through the `ToDo` list in `readme.md` until every spell, action, skill, and mechanic from the D&D 5e 2024 SRD is mechanically implemented and verified within the TaleKeeper application."

## 3. System Architecture

The harness will be a Python application that orchestrates the interaction between the Agent (an LLM API like Claude) and the TaleKeeper codebase.

```
+-------------------------+      +------------------------+      +----------------------+
|   Orchestrator          |----->|   Agent (LLM API)      |<---->|   Knowledge Base     |
| (main_harness.py)       |      +------------------------+      | (SRD, Project Docs)  |
+-----------+-------------+                                      +----------------------+
            |
            |
+-----------v-------------+      +------------------------+      +----------------------+
|   Toolbelt              |----->|   TaleKeeper Codebase  |<---->|   Verification       |
| (file_io, git, shell)   |      | (src/, data/, tests/)  |      | (pytest, pylint)     |
+-------------------------+      +------------------------+      +----------------------+
```

### Components

1.  **Orchestrator (`harness/orchestrator.py`)**:
    *   The main loop of the harness.
    *   Manages the overall state (e.g., current task, plan).
    *   Calls the Agent with a structured prompt.
    *   Parses the Agent's response (plan, code, tool usage).
    *   Invokes tools from the Toolbelt.
    *   Gathers verification results and feeds them back to the Agent.

2.  **Agent (LLM API Wrapper)**:
    *   A service that communicates with a powerful code-generation LLM.
    *   Receives a large context prompt from the Orchestrator.
    *   Returns a structured response, typically JSON, specifying actions to take.

3.  **Knowledge Base**:
    *   A collection of static documents providing essential context.
    *   **Primary Goal**: The `ToDo` list from `readme.md`.
    *   **Domain Knowledge**: The D&D 5e 2024 SRD, converted to markdown or text files for easy parsing.
    *   **Project Knowledge**: Key documents like `REORGANIZATION_SUMMARY.md`, `NARRATIVE_GENERATION_PLAN.md`, and other files in `docs/`.

4.  **Toolbelt (`harness/tools/`)**:
    *   A set of functions the Agent can ask the Orchestrator to execute. This is the Agent's only way to interact with the system.
    *   `read_file(path)`: Reads a file's content.
    *   `write_file(path, content)`: Writes or overwrites a file.
    *   `list_files(directory)`: Lists directory contents.
    *   `run_shell_command(command)`: Executes a shell command (e.g., `pytest`, `git status`).
    *   `git_diff()`: Shows the current `git diff`.
    *   `ask_human(question)`: Pauses the loop and prompts for human input for clarification or decisions.

5.  **Verification Suite**:
    *   Uses existing project tools.
    *   `pytest`: The primary tool for verifying correctness. The Agent will be instructed to write tests for all new functionality. The existing `tests/` structure is perfect for this.
    *   `pylint`/`mypy`: For static analysis to maintain code quality.

## 4. The Agentic Loop (Workflow)

The harness will execute the following loop for each top-level task from the `ToDo` list.

### Phase 1: Task Selection & Planning

1.  **Orchestrator**: Reads `readme.md` and identifies the next incomplete `ToDo` item (e.g., "List all fighter abilities for each level in a doc.").
2.  **Orchestrator**: Gathers initial context: the selected task, the SRD document for "Fighter", and the project's file structure.
3.  **Orchestrator**: Prompts the Agent:
    > **System Prompt**: "You are an expert software engineer working on TaleKeeper. Your task is to `[TASK]`. Analyze the provided context and create a detailed, step-by-step implementation plan. Your plan should include which files to create or modify and what tests to write. The project structure is `[...file tree...]`. The SRD says `[...SRD text...]`. Output your plan as a JSON object."
4.  **Agent**: Returns a structured plan, for example:
    ```json
    {
      "plan": [
        { "step": 1, "action": "tool.write_file", "params": { "path": "docs/development/FIGHTER_ABILITIES.md", "content": "..." } },
        { "step": 2, "action": "tool.write_file", "params": { "path": "docs/development/FIGHTER_IMPLEMENTATION_PLAN.md", "content": "..." } },
        { "step": 3, "action": "human_review", "params": { "message": "Review the generated planning documents before I proceed with implementation." } }
      ]
    }
    ```

### Phase 2: Code Implementation

1.  **Orchestrator**: Executes the plan step-by-step. For each step involving code changes:
2.  **Orchestrator**: Prompts the Agent with a focused request:
    > **System Prompt**: "Implement Step `[N]` of the plan: `[Step Description]`. You need to modify `[file_path]`. Here is its current content: `[...file content...]`. Here are the relevant SRD rules: `[...SRD text...]`. Provide the complete, updated file content."
3.  **Agent**: Returns the full content of the modified file.
4.  **Orchestrator**: Uses the `write_file` tool to apply the change.
5.  **Orchestrator**: Repeats for all files to be modified, including new test files (e.g., `tests/unit/test_fighter_abilities.py`).

### Phase 3: Verification

1.  **Orchestrator**: After applying all code changes for a sub-task, it runs the verification suite.
2.  **Orchestrator**: Executes `pytest tests/`.
3.  **Orchestrator**: Captures the output (pass/fail, errors, coverage).

### Phase 4: Feedback and Iteration

1.  **If Verification Succeeds**:
    *   **Orchestrator**: Commits the changes with a descriptive message generated by the Agent (e.g., "feat(fighter): Implement Second Wind ability").
    *   **Orchestrator**: Updates `readme.md` to mark the sub-task as complete.
    *   **Orchestrator**: Moves to the next step in the plan or the next `ToDo` item.

2.  **If Verification Fails**:
    *   **Orchestrator**: Gathers the `git diff` of the failed changes and the full error output from `pytest`.
    *   **Orchestrator**: Prompts the Agent:
        > **System Prompt**: "Your previous attempt failed. Here is the `git diff` of your changes: `[...diff...]`. Here is the error from `pytest`: `[...error log...]`. Analyze the error and provide a corrected version of the files."
    *   **Agent**: Provides new file content.
    *   **Orchestrator**: Reverts the previous changes and applies the new ones. The loop returns to the Verification phase. This "self-healing" loop continues until tests pass or a human intervention is requested.

## 5. Implementation Details

### Directory Structure

A new `harness/` directory will be created at the project root to contain the agentic system. This keeps it separate from the main `src/talekeeper` application code.

```
TaleKeeper/
├── harness/
│   ├── main_harness.py         # Main entry point for the agent
│   ├── orchestrator.py         # The main control loop
│   ├── agent.py                # Wrapper for the LLM API
│   ├── knowledge.py            # Functions to load SRD/docs
│   └── tools/
│       ├── __init__.py
│       ├── file_system.py      # read_file, write_file, etc.
│       ├── shell.py            # run_shell_command
│       └── git.py              # git_diff, git_commit
├── src/talekeeper/
...
```

### Knowledge Base Preparation

The D&D 5e SRD needs to be acquired and stored in a machine-readable format (e.g., plain text or markdown files) within the repository, perhaps under `data/srd/`. This will be a critical one-time setup task.

*   `data/srd/classes/fighter.md`
*   `data/srd/spells/fireball.md`
*   `data/srd/mechanics/conditions.md`

### State Management

The Orchestrator will maintain a `state.json` file to track its progress. This allows the harness to be stopped and restarted without losing its place.

```json
{
  "current_task": "Implement Fighter class features.",
  "current_plan_step": 4,
  "last_commit": "a1b2c3d",
  "session_history": [
    { "prompt": "...", "response": "...", "verification_result": "PASS" }
  ]
}
```

### Human in the Loop

The Agent must have an "eject button" or a way to request help. The `ask_human(question)` tool is essential. The harness will pause and wait for input when this tool is invoked. This is critical for:
*   Ambiguous requirements in the SRD.
*   Architectural decisions with long-term consequences.
*   Resolving persistent, circular test failures.

## 6. Getting Started: The First Task

The first task for the harness will be the first item on the `ToDo` list: **"Record all actions taken to a file for future reference"**.

This is an excellent starting point because:
1.  It's self-referential: the agent's own actions will be logged.
2.  It's a small, well-defined task.
3.  It requires the agent to understand the existing logging system (`talekeeper.log`) and decide how to augment it.
4.  It forces the agent to use the `read_file`, `write_file`, and `run_shell_command` tools.

The Orchestrator would start by prompting the Agent to create a plan for this task, and the loop would begin.

## 7. Running the Harness

The harness will be executed from the command line.

```bash
# Start the agentic loop
python harness/main_harness.py

# Start from a specific task
python harness/main_harness.py --task "Implement Barbarian class"

# Run a single cycle (plan, act, verify) and then stop
python harness/main_harness.py --single-cycle
```

For a persistent process, this script can be wrapped in a Windows Service or a `systemd` service on Linux, fulfilling the vision of the `create-windows-service-for-agentic-harness` branch.

## 8. Risks and Mitigations

*   **Risk**: LLM Hallucination / Poor Code Quality.
    *   **Mitigation**: Strict verification with `pytest` and `pylint`. The "fail-and-retry" loop is the primary defense. The Agent will be instructed to always write tests before or alongside implementation.

*   **Risk**: Infinite Loops (e.g., repeatedly failing the same test).
    *   **Mitigation**: The Orchestrator will track failure counts for a given step. After 3-5 failed attempts, it will automatically invoke `ask_human("I am stuck on this step...")`.

*   **Risk**: High Cost of LLM API Calls.
    *   **Mitigation**: Start with smaller, more focused tasks. Use extensive caching for knowledge base lookups. Implement robust state management to avoid re-doing work. Use smaller/cheaper models for planning and larger/smarter models for coding and debugging.

*   **Risk**: Agent makes a catastrophic change (e.g., deletes `src/`).
    *   **Mitigation**: The harness will operate on a dedicated git branch. All actions are contained and can be easily reverted. The `Toolbelt` can have safety checks (e.g., disallow `rm -rf /`).

This design provides a robust framework for building an agentic harness capable of tackling the ambitious goal of fully implementing the D&D 5e SRD in TaleKeeper. It balances automation with crucial human oversight and leverages the project's existing high-quality structure and test suites.