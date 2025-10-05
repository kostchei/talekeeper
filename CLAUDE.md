# CLAUDE.md - TaleKeeper Development Guide

## Project Overview
TaleKeeper is a single-player D&D 2024 tactical RPG for Windows built with PyQt6 and SQLite. The application features character creation, combat simulation, equipment management, and follows D&D 2024 rules.

## Architecture
- **Frontend**: PyQt6 with fixed-position UI panels
- **Backend**: SQLite database with game_engine_sqlite.py coordinator
- **Game Rules**: D&D 2024 (One D&D) ruleset implementation

## Key Commands

### Running the Application
```bash
python main.py
```

### Running Tests
```bash
# REGRESSION TESTS - Run after EVERY code change
python tests/run_regression_tests.py --quick      # 30 seconds - Always run
python tests/run_regression_tests.py --full       # 2-3 minutes - Before commits
python tests/run_regression_tests.py --detailed   # 4-5 minutes - Feature validation
run_tests.bat quick                                # Windows shortcut
./run_tests.sh quick                               # Unix/Linux shortcut

# Test Suite Breakdown:
# --quick: Core systems (6 tests) - character, combat, database, action economy
# --full: Quick + comprehensive (11 tests) - adds subclass, progression, conditions
# --detailed: Full + feature tests (12+ tests) - adds Hero Mode, future features

# Legacy tests (for reference)
cd test && python test_simple_validation.py       # Core validation
cd test && python test_results_summary.py         # Test summary
python testing/run_tests.py                       # Old Qt6 test suite
```

### Linting & Type Checking
```bash
# Lint Python code
python -m pylint main.py ui/ core/ services/

# Type check (if mypy is configured)
python -m mypy main.py
```

### Testing After Changes
```bash
# After Fighter changes - run these tests
cd test && python -m pytest services/test_fighter_champion.py -v

# After weapon/combat changes
cd test && python -m pytest services/test_weapon_attack_service.py -v

# Full validation
cd test && python test_simple_validation.py
```

## Project Structure (Production-Ready)

**NEW STRUCTURE** (as of Oct 2025 - reorganized for exe conversion):

```
TaleKeeper/
├── main.py                      # Entry point (ONLY .py in root)
├── setup.py                     # Package metadata
├── pyproject.toml               # Modern Python packaging
│
├── src/talekeeper/              # Main application package
│   ├── __init__.py
│   ├── __main__.py              # Allows: python -m talekeeper
│   ├── paths.py                 # Path helpers (dev + exe)
│   ├── core/                    # Game engine & systems
│   │   ├── game_engine_sqlite.py
│   │   ├── feature_integration.py
│   │   ├── combat_manager.py
│   │   ├── config.py
│   │   └── debug_commands.py
│   ├── services/                # Game services (50+ modules)
│   │   ├── feat_effects.py
│   │   ├── condition_manager.py
│   │   ├── subclass_registry.py
│   │   └── ...
│   ├── ui/                      # PyQt6 UI components
│   │   ├── main_window.py
│   │   ├── themes.py
│   │   ├── action_cards/
│   │   ├── character_sheet/
│   │   ├── encounter_pane/
│   │   ├── equipment_layout/
│   │   └── menu/
│   ├── audio/                   # TTS & narration
│   ├── database/                # DB initialization
│   │   └── database_init.py
│   └── models/                  # Data models
│
├── data/                        # Game data & runtime files
│   ├── database/
│   │   ├── schema/              # SQL schema files
│   │   ├── seeds/               # Game data (D&D rules)
│   │   ├── migrations/          # Database updates
│   │   └── talekeeper.db        # SQLite database (auto-created)
│   ├── monsters/                # Monster JSON data
│   ├── config/                  # Runtime configuration
│   │   └── talekeeper_config.json
│   └── assets/                  # Images, fonts, art
│
├── scripts/                     # Dev tools (excluded from exe)
│   ├── monster_tools/           # Monster data utilities
│   ├── database_tools/          # DB utilities
│   ├── character_tools/         # Character utilities
│   └── utilities/               # General utilities
│
├── tests/                       # Consolidated test suite
│   ├── run_regression_tests.py
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── qt_framework/
│
└── docs/                        # Documentation
    ├── development/
    └── reports/
```

**Import Pattern Changes:**
```python
# OLD (pre-Oct 2025)
from core.game_engine_sqlite import GameEngine
from services.feat_effects import FeatEffects

# NEW (current)
from talekeeper.core.game_engine_sqlite import GameEngine
from talekeeper.services.feat_effects import FeatEffects
```

## Testing System
The project includes a comprehensive Qt6-based testing framework that can:
- Automatically interact with UI elements (click, type, drag)
- Take screenshots for visual verification
- Test fighting styles, feats, and combat mechanics
- Generate HTML reports with test results

### Test Coverage Areas
- Character creation flow
- Equipment effects on stats
- Fighting styles (Defense, Dueling, etc.)
- Action card availability
- Combat calculations
- Level progression

## Database Initialization

### Fresh Clone Experience
When cloning the repository for the first time:
1. The database is automatically created on first run
2. Schema is loaded from `database/schema/`
3. Game data (classes, races, items) loaded from `database/seeds/`
4. Migrations are tracked in `schema_migrations` table

### Database Management Commands
```bash
# Force recreate database (backs up existing)
python database/database_init.py --force

# Initialize with dev/test data
python database/database_init.py --dev

# Verify database integrity
python database/database_init.py --verify

# Run application with dev mode
python main.py --dev
```

### Migration System
- Place new migrations in `database/migrations/` as SQL files
- Name format: `XXX_description.sql` (e.g., `002_add_fighter_features.sql`)
- Migrations run automatically on startup
- Failed migrations (e.g., duplicate columns) are handled gracefully

## Known Issues & Bug Areas

### Fighting Styles
Multiple implementation approaches exist in the codebase:
- Some in `feat_effects.py`
- Some in `combat_engine.py`
- Some in UI components
Test with: `python testing/run_tests.py --mode specific`

### Character Features
- Features may not initialize properly for new characters
- `feature_integration.py` handles the feature system
- Check `character_features` table in database

### Equipment System
- AC calculations involve multiple components
- Defense fighting style adds +1 AC when wearing armor
- Equipment changes should update action cards

### HP Tracking During Combat (CRITICAL)
Combat HP is tracked in `parent.character_sheet.character_data`, NOT in the database or character_context during active combat:
- **Damage Application**: Reads from character_sheet → applies damage → updates character_sheet
- **Healing MUST**: Read from character_sheet → apply healing → update character_sheet
- **NEVER**: Read HP from database or character_context for healing during combat (will be stale)
- **Pattern Location**: See `_apply_damage_to_player()` and Second Wind implementation in `src/talekeeper/ui/action_cards/action_panel.py`
- All healing abilities (potions, spells, class features) must follow this pattern

### Ollama LLM Integration (Optional)
The campaign description service can use Ollama for narrative generation:
- **Warning**: `[LLM] Ollama request failed: HTTPConnectionPool` is EXPECTED when Ollama isn't running
- **Fallback**: Service automatically uses deterministic text when Ollama unavailable
- **Not Critical**: Application works fine without Ollama
- **To Enable**: Install and run Ollama separately (`ollama serve`)

## Database Schema
Key tables in `talekeeper.db`:
- `characters` - Character data and stats
- `character_features` - Active features per character
- `character_inventory` - Item storage
- `classes` - D&D classes
- `races` - D&D species/races
- `feats` - Available feats
- `equipment` - Equipment definitions

## Combat System

### Attack Flow
1. Player selects action card
2. System calculates attack bonus (ability + proficiency + modifiers)
3. Roll d20 + bonuses vs target AC
4. On hit: roll damage + modifiers
5. Apply fighting style effects

### Fighting Style Effects
- **Defense**: +1 AC with armor (passive)
- **Dueling**: +2 damage one-handed (automatic)
- **Great Weapon Fighting**: Reroll 1-2 on damage (automatic)
- **Two-Weapon Fighting**: Add ability mod to off-hand (automatic)
- **Archery**: +2 attack with ranged (automatic)
- **Protection**: Reaction to impose disadvantage (manual)

## UI Panels & Coordinates
Fixed positions at 1920x1080 with 5% margins:
- **Game Menu**: (96, 54)
- **Character Sheet**: (96, 144)
- **Encounter Pane**: (744, 54) - center
- **Log Panel**: (1392, 54) - top right
- **Equipment Panel**: (1392, 540) - bottom right
- **Action Panel**: (96, 726) - bottom left

## Development Patterns

### Adding New Features
1. Update database schema if needed
2. Modify `game_engine_sqlite.py` for backend logic
3. Update relevant UI panels
4. Add tests in `testing/test_specific_features.py`
5. Run full test suite to verify

### Signal/Slot Connections
Main window connects panels via Qt signals:
```python
self.menu.create_character_requested.connect(self._start_character_creation)
self.equipment_panel.item_equipped.connect(self._on_item_equipped)
self.action_panel.action_triggered.connect(lambda action, context: ...)
```

### Theme System
- Light/dark themes in `ui/themes.py`
- Toggle with Ctrl+T or button
- Each panel has `update_theme()` method

## Performance Considerations
- Database queries are synchronous (_sync suffix)
- UI updates via Qt signals avoid blocking
- Screenshots in tests add ~100ms each
- Character loading queries multiple tables

## Debugging Tips

### Visual Testing
```bash
# See what's happening in the UI
python testing/run_tests.py --mode visual
```

### Check Database
```bash
sqlite3 talekeeper.db
.tables
SELECT * FROM characters;
SELECT * FROM character_features WHERE character_id = '...';
```

### Enable Debug Logging
Look for `print(f"[DEBUG] ...")` statements throughout code.

## Common Tasks

### Fix Character Features Not Loading
```python
# In main_window.py around line 845
from core.feature_integration import FeatureSystemIntegration
feature_system = FeatureSystemIntegration('talekeeper.db')
feature_system.initialize_character_features(character['id'])
```

### Refresh Equipment/Inventory
Use Force Refresh button or call:
```python
self.window._force_reload_character()
```

### Test Specific Fighting Style
```python
# In test_specific_features.py
tester = FightingStyleTester()
tester.setup()
tester.test_defense_style()  # or test_dueling_style(), etc.
```

## Code Style
- No comments unless specifically requested
- NEVER use Unicode characters - stick to ASCII only
- Follow existing patterns in codebase
- Use type hints where established
- Fixed UI positions, no responsive layout
- D&D 2024 rules (not 5e where different)

## Contact Points
- Main application: `main.py`
- Game logic: `core/game_engine_sqlite.py`
- UI coordination: `ui/main_window.py`
- Combat: `core/combat_engine.py`
- Testing: `testing/run_tests.py`

## Recent Additions (2024-2025)
- Comprehensive Qt6 testing framework (Dec 2024)
- Fighting style validation tests
- Visual debugging mode for UI testing
- HTML test reporting with screenshots
- **Enhanced Barbarian Systems (Sept 2024)**:
  - Condition system with D&D 2024 conditions
  - Scalable subclass architecture (44+ subclasses)
  - Action economy enforcement system
  - Enhanced monster attack logging
  - Configuration management system
  - Debug command utilities

## Enhanced Systems Documentation

### Condition System
- **Location**: `services/condition_manager.py`
- **Features**: D&D 2024 conditions with mechanical effects
- **Integration**: Danger Sense, advantage/disadvantage, movement restrictions
- **Testing**: `test/services/test_condition_manager.py`

### Subclass Architecture
- **Primary**: `services/enhanced_subclass_manager.py`
- **Registry**: `services/subclass_registry.py`
- **Features**: Modular, scalable design for 44+ subclasses across 11 classes
- **Example**: Champion Fighter, Berserker Barbarian implementations
- **Testing**: `test/test_scalable_subclass_architecture.py`

### Action Economy System
- **Enforcement**: Action/bonus action/reaction tracking and validation
- **Integration**: Works with class features and combat system
- **UI**: Action cards show availability based on economy state
- **Testing**: `test/test_action_economy_enforcement.py`

### Configuration System
- **Location**: `core/config.py`
- **Features**: Performance, debug, feature, and UI settings
- **Config File**: `talekeeper_config.json` (auto-created)
- **Modes**: Developer mode, performance mode presets

### Debug Commands
- **Location**: `core/debug_commands.py`
- **Usage**: `/debug <command>` in application
- **Commands**: performance, memory, conditions, test utilities
- **Configuration**: Enable with `debug.enable_test_commands = true`

## Enhanced Testing Commands

### Barbarian System Tests
```bash
# Run comprehensive Barbarian tests
cd test && python test_stage_1_4_integration.py    # Conditions
cd test && python test_stage_2_1_subclass_definitions.py  # Subclasses
cd test && python test_barbarian_level_progression.py     # Levels 1-20

# Run action economy tests
cd test && python test_action_economy_enforcement.py

# Run scalable architecture tests
cd test && python test_scalable_subclass_architecture.py
```

### Debug Commands (In-Application)
```
/debug performance     # Show timing metrics
/debug conditions <character>  # Show active conditions
/debug test_rage <character>   # Test rage mechanics
/debug config         # Show current configuration
/debug help          # Full command list
```

### Configuration Management
```python
# Enable developer mode
from core.config import config
config.enable_developer_mode()

# Check feature status
if config.is_feature_enabled("use_enhanced_subclass_manager"):
    # Use enhanced system
```

## System Integration Status

### ✅ Completed Systems
- **Condition System**: Full D&D 2024 condition support
- **Subclass Architecture**: Scalable system ready for all classes
- **Action Economy**: Complete enforcement and UI integration
- **Enhanced Monster Logging**: Detailed attack breakdowns
- **Configuration Management**: Centralized settings system
- **Debug Utilities**: Comprehensive development tools

### 🔄 Integration Points
- All systems tested together through Stage 4.1
- Barbarian levels 1-20 validated
- UI integration complete
- Database optimization implemented

## Next Priorities
- Complete spell system implementation
- Monster AI improvements
- Save slot management enhancements
- Expand subclass system to other classes
- never use unicode. Text or an image