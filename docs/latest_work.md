# TaleKeeper Progression & Ability Validation Plan

## Objective
Mechanically verify that every **supported** class ability (Barbarian, Fighter, Rogue, Cleric, Wizard, Warlock, Paladin) defined in `docs/SRD_CC_v5.2.1.md` is accessible and functional in TaleKeeper's Qt6 UI from levels 1‑20, minimizing new code by reusing existing services, databases, and harnesses.

## Current Strategy
- **SRD Traceability Matrix**  
  - Maintain `tests/fixtures/class_feature_matrix.yaml`, which maps SRD citations to TaleKeeper services/UI components for the seven in-scope classes.  
  - Seed entries from `docs/SRD_TO_TALEKEEPER_MAPPING.md` and the SRD class sections, and attach the correct template path plus expected UI surfaces for each feature.  
  - Keep unused class templates in `templates/archive/` so automation only touches the supported builds.

- **Backend Progression Harness**  
  - Duplicate/generalize `tests/test_fighter_progression_complete.py` across the supported classes while keeping `ProgrammaticCharacterCreator` and `UnifiedLevelUpService` in the loop.  
  - Externalize ASI/feat/spell choices into fixtures (modeled on `tests/fixtures/fighter_champion_choices.yaml`) and load them via `tests/helpers/choice_loader.py`.  
  - At every level-up, query the relevant ability service and compare results to the matrix, logging via `tests/helpers/progression_recorder.py`.

- **Feature Test Reuse**  
  - Pull in existing per-feature suites (fighter, paladin, warlock, etc.) inside each class progression test.  
  - When gaps remain for the supported classes, follow the `tests/test_warlock_comprehensive.py` pattern to aggregate backend-driven assertions.

- **UI Automation Coverage**  
  - Parameterize `tests/testing_framework_ui_automation.py` to run the same leveled characters through the Qt6 UI and assert that every matrix entry marked “UI” renders and behaves correctly.  
  - Extend `tests/ui/test_action_panel_integration.py` fixtures to accept arbitrary class snapshots so resource toggles, spell slots, and dialogs can be verified at milestone levels.

- **Reporting & Safety**  
  - Continue archiving/restoring the SQLite DB via `tests/helpers/database_archiver.py`.  
  - Emit JSON/Markdown progression reports per supported class (tooling documented in `tests/README_PROGRESSION_TESTING.md`).  
  - Schedule nightly jobs that iterate the seven supported classes using the shared harnesses.

## Next Implementation Steps
1. Fully populate `tests/fixtures/class_feature_matrix.yaml` (SRD refs, TaleKeeper services, template paths, UI expectations) for the seven supported classes.  
2. Create fixtures for each supported class/subclass progression (ASI/feat/spell choices).  
3. Generalize `tests/test_fighter_progression_complete.py` so it can iterate over the supported classes via the matrix.  
4. Wire `ProgressionRecorder` to ingest matrix data and produce consolidated reports.  
5. Parameterize the PyQt automation suite to validate UI availability for abilities at milestone levels.  
6. Add orchestration to run backend + UI validations consistently (pytest markers or runner script).

## Implementation Progress (current session)
- Scoped the plan to Barbarian, Fighter, Rogue, Cleric, Wizard, Warlock, and Paladin, archiving the other starter templates under `templates/archive/`.  
- Authored `tests/fixtures/class_feature_matrix.yaml` to capture SRD citations, template references, and verification hooks for the supported classes.  
- Introduced `tests/helpers/class_feature_matrix.py` plus a smoke test (`tests/test_class_feature_matrix_integrity.py`) that validates template availability and feature definitions.  
- Verified the new helper/test via `pytest tests/test_class_feature_matrix_integrity.py -q`.
