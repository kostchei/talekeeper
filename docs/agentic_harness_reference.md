# Talekeeper Agentic Harness Reference

## Objective
Design a resilient automation harness that coordinates Claude Code inside Visual Studio Code on Windows, drives
implementation through a written plan, and validates each deliverable with Qt6 functional tests before accepting the
work.

## Acceptance Criteria
- Harness reads tasks from `docs/agentic_harness_plan.yaml` and updates their status as work progresses.
- Harness sends explicit task instructions, revision requests, and documentation prompts to the Claude Code extension.
- Harness executes Qt6 pytest suites and only marks tasks complete when the tests succeed.
- Harness records pauses and creates remediation subtasks when progress stalls or verification fails.
- Harness enforces a documentation hand-off once verification passes.

## Required Qt6 Tests
- tests/test_spell_cards_qt6.py::test_spell_action_cards
- tests/test_stage_1_3_ui.py::test_condition_badge_creation
- tests/test_spell_selection_ui.py::test_wizard_selection

