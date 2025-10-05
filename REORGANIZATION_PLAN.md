# TaleKeeper Repository Reorganization Plan

## Current State Analysis

### Issues Identified
1. **22 loose Python scripts in root directory** - clutters namespace, hard to package
2. **Multiple test directories** - `test/`, `tests/`, `testing/` causing confusion
3. **Scattered data files** - JSON, MD, CSV, PNG files in root
4. **Multiple bin/config/utilities folders** - unclear organization
5. **Duplicate/outdated folders** - `excess/`, `database_migrations/` vs `database/migrations/`
6. **No clear src/ separation** - application code mixed with tools

### Current Structure
```
TaleKeeper/
├── main.py (KEEP - entry point)
├── 22 loose .py scripts (MOVE)
├── Multiple .json/.md/.csv files (ORGANIZE)
├── action_cards/       (app code)
├── character_sheet/    (app code)
├── encounter_pane/     (app code)
├── equipment_layout/   (app code)
├── ui/                 (app code)
├── core/               (app code)
├── services/           (app code)
├── audio/              (app code)
├── menu/               (app code)
├── database/           (data)
├── test/, tests/, testing/ (CONSOLIDATE)
├── scripts/, tools/, utilities/ (CONSOLIDATE)
└── Many other folders...
```

## Target Structure (Production-Ready for EXE)

```
TaleKeeper/
├── main.py                     # Entry point (ONLY .py in root)
├── requirements.txt            # Dependencies
├── requirements-lora.txt       # Optional deps
├── environment.yml             # Conda env
├── pyinstaller.spec           # NEW - exe build spec
├── setup.py                    # NEW - package metadata
├── README.md                   # Main documentation
├── CLAUDE.md                   # Dev instructions
├── LICENSE                     # NEW - if needed
│
├── src/                        # NEW - All application code
│   ├── __init__.py
│   ├── talekeeper/            # NEW - Main package
│   │   ├── __init__.py
│   │   ├── core/              # Game engine
│   │   ├── services/          # Game services
│   │   ├── ui/               # UI components
│   │   │   ├── main_window.py
│   │   │   ├── themes.py
│   │   │   ├── action_cards/
│   │   │   ├── character_sheet/
│   │   │   ├── encounter_pane/
│   │   │   ├── equipment_layout/
│   │   │   └── menu/
│   │   ├── audio/            # TTS/audio systems
│   │   ├── database/         # DB layer
│   │   └── models/           # Data models
│   └── __main__.py           # Allow python -m talekeeper
│
├── data/                      # NEW - All game/runtime data
│   ├── database/
│   │   ├── schema/
│   │   ├── seeds/
│   │   └── migrations/
│   ├── monsters/
│   │   ├── monsters_extracted.json
│   │   ├── srd_monsters_parsed.json
│   │   └── validation/
│   ├── config/
│   │   └── talekeeper_config.json
│   └── assets/               # Images, sounds
│       ├── images/
│       ├── audio/
│       └── art/
│
├── scripts/                   # NEW - Dev/admin tools (NOT in exe)
│   ├── monster_tools/
│   │   ├── extract_monsters.py
│   │   ├── compare_monsters.py
│   │   ├── validate_monster_attacks.py
│   │   ├── cleanup_monster_data.py
│   │   ├── fix_monster_attacks.py
│   │   └── update_monsters_to_2024.py
│   ├── database_tools/
│   │   ├── populate_test_characters.py
│   │   └── fix_spell_slots.py
│   ├── character_tools/
│   │   └── create_level5_rogue.py
│   └── utilities/
│       ├── analyze_discrepancies.py
│       ├── generate_summary.py
│       └── priority_review_list.py
│
├── tests/                     # NEW - Consolidated testing
│   ├── __init__.py
│   ├── conftest.py           # pytest config
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── regression/           # Regression suite
│   │   └── run_regression_tests.py
│   └── qt_framework/         # Qt UI tests
│       └── test_framework.py
│
├── docs/                      # Documentation
│   ├── api/
│   ├── guides/
│   ├── reports/              # Monster/validation reports
│   │   ├── MONSTER_ATTACK_VALIDATION_REPORT.md
│   │   ├── MONSTER_UPDATE_SUMMARY.md
│   │   └── monster_comparison_summary.md
│   └── development/
│       ├── CLASS_FEATURE_SYSTEM_DESIGN.md
│       ├── INSTALLATION_COMPLETE.md
│       └── README_TESTING_FRAMEWORK.md
│
├── build/                     # NEW - Build artifacts (gitignored)
├── dist/                      # NEW - Distribution exe (gitignored)
├── logs/                      # Runtime logs (gitignored)
│   └── talekeeper.log
└── .github/                   # CI/CD workflows
```

## Migration Strategy

### Phase 1: Preparation
1. Create new directory structure (no file moves yet)
2. Update .gitignore for build/dist/logs
3. Create pyinstaller.spec and setup.py
4. Commit structure changes

### Phase 2: Code Migration
1. Move application code to src/talekeeper/
2. Update all import statements
3. Move UI components to src/talekeeper/ui/
4. Update __init__.py files with proper exports

### Phase 3: Data/Asset Organization
1. Consolidate monster JSON files to data/monsters/
2. Move database files to data/database/
3. Move assets (images, art) to data/assets/
4. Update file paths in code

### Phase 4: Script/Tool Consolidation
1. Move all loose .py scripts to scripts/ subdirectories
2. Consolidate test/, tests/, testing/ to tests/
3. Remove duplicate/outdated folders

### Phase 5: Configuration & Documentation
1. Update CLAUDE.md with new structure
2. Update README.md
3. Create setup.py for package metadata
4. Create pyinstaller.spec for exe building

### Phase 6: Validation
1. Run regression tests
2. Test database initialization
3. Test application startup
4. Verify all imports work

## Import Path Changes

### Before
```python
from core.game_engine_sqlite import GameEngine
from services.feat_effects import FeatEffects
from ui.main_window import MainWindow
```

### After
```python
from talekeeper.core.game_engine_sqlite import GameEngine
from talekeeper.services.feat_effects import FeatEffects
from talekeeper.ui.main_window import MainWindow
```

## File Path Changes

### Before
```python
db_path = 'talekeeper.db'
config_path = 'talekeeper_config.json'
monsters_path = 'monsters_extracted.json'
```

### After
```python
from talekeeper.core.paths import get_data_path, get_config_path

db_path = get_data_path('database/talekeeper.db')
config_path = get_config_path('talekeeper_config.json')
monsters_path = get_data_path('monsters/monsters_extracted.json')
```

## Benefits for EXE Conversion

1. **Clean namespace** - Only main.py in root
2. **Easy PyInstaller config** - All code in src/talekeeper/
3. **Data bundling** - data/ folder easily included in exe
4. **Development tools excluded** - scripts/ not in production build
5. **Standard Python package** - Can be installed with pip
6. **Clear separation** - App code vs tools vs data vs tests
7. **Better imports** - Explicit package structure prevents conflicts
8. **Professional** - Follows Python packaging best practices

## Risks & Mitigation

### Risk: Breaking existing imports
- Mitigation: Use search/replace, test after each phase

### Risk: File path issues
- Mitigation: Create path helper module, update incrementally

### Risk: Database/config not found
- Mitigation: Add fallback paths, create if missing

### Risk: Tests break
- Mitigation: Update test imports, run after each change

## Timeline

- Phase 1: 30 minutes
- Phase 2: 2-3 hours
- Phase 3: 1 hour
- Phase 4: 1 hour
- Phase 5: 30 minutes
- Phase 6: 1 hour

**Total: ~6-7 hours of careful work**

## Rollback Plan

Git branch: `feature/reorganize-for-production`
- Each phase is a separate commit
- Can revert to any phase if issues found
- Keep old structure in backup branch
