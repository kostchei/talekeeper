# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TaleKeeper is a single-player D&D 2024 tactical RPG for Windows built with PyQt6 and SQLite. Features character creation, turn-based combat, exploration, and full D&D 2024 rules implementation.

## Essential Commands

### Running & Testing
```bash
# Run the application
python main.py
python main.py --dev                              # With dev/test data

# Database management
python database/database_init.py --force          # Recreate database
python database/database_init.py --verify         # Verify integrity

# Testing (CRITICAL: Run after every code change)
pytest tests/ -v                                  # All tests
pytest tests/test_simple.py -v                    # Quick smoke test
pytest tests/core/ -v                             # Core systems
pytest tests/services/ -v                         # Service layer
pytest tests/integration/ -v                      # Integration tests
```

### Package Structure (October 2025 Reorganization)
```
TaleKeeper/
├── main.py                      # Entry point
├── src/talekeeper/              # Main package (USE THIS IN IMPORTS)
│   ├── core/                    # Game engine, combat, features
│   ├── services/                # 50+ service modules (dice, abilities, etc.)
│   ├── ui/                      # PyQt6 UI components
│   ├── database/                # DB initialization
│   ├── models/                  # Data models
│   └── audio/                   # TTS & narration
├── database/                    # Root DB files
│   ├── schema/                  # Database schema SQL
│   ├── seeds/                   # Game data (classes, races, items)
│   └── migrations/              # Database migrations
├── tests/                       # Test suite
└── docs/                        # Documentation
```

**CRITICAL IMPORT PATTERN:**
```python
# CORRECT (current structure)
from talekeeper.core.game_engine_sqlite import GameEngineSQLite
from talekeeper.services.dice import DiceService
from talekeeper.ui.main_window import MainWindow

# WRONG (old structure - DO NOT USE)
from core.game_engine_sqlite import GameEngineSQLite
```

## Architecture Overview

### Core Data Flow
1. **Database (SQLite)** - Single source of truth (`talekeeper.db` in root)
2. **Game Engine** (`src/talekeeper/core/game_engine_sqlite.py`) - Coordinates all systems
3. **Services** (`src/talekeeper/services/`) - Business logic (50+ modules)
4. **UI Components** (`src/talekeeper/ui/`) - PyQt6 panels with fixed positions
5. **Combat Manager** (`src/talekeeper/core/combat_manager.py`) - Turn-based combat

### Key Systems
- **Proficiency System** (`services/proficiency_system.py`) - Skills, weapons, armor, saves
- **Condition Manager** (`services/condition_manager.py`) - All 15 D&D conditions
- **Action Economy** (`services/action_economy_enforcer.py`) - Action/bonus/reaction tracking
- **Spell Effects** (`services/spell_effects_service.py`) - Active spell management
- **Class Abilities** (5 class-specific services) - Fighter, Barbarian, Rogue, Paladin, Warlock
- **Combat System** (`core/combat_manager.py`) - Initiative, attacks, damage, conditions
- **Weapon Mastery** (`services/weapon_mastery_service.py`) - Push, Sap, Slow, Cleave, etc.

### Database Schema Pattern
The database uses SQLite with migrations. Key tables:
- `characters` - Character data
- `character_proficiencies` - Skills, weapons, armor (with source tracking)
- `character_resources` - Limited-use abilities (Second Wind, Rage, etc.)
- `character_features` - Class/subclass features
- `character_spells` - Known/prepared spells
- `active_spell_effects` - Active buffs/debuffs
- `monsters` - Monster stat blocks
- `character_hex_map` - Hex-based exploration

### UI Panel Architecture
Fixed positions at 1920x1080. All panels connected via Qt signals:
- **MainWindow** (`ui/main_window.py`) - Coordinates all panels
- **ActionPanel** (`ui/action_cards/action_panel.py`) - Action cards (attacks, abilities, spells)
- **CharacterPanel** (`ui/character_sheet/character_panel.py`) - Character sheet
- **EncounterPanel** (`ui/encounter_pane/encounter_panel.py`) - Combat encounters
- **EquipmentPanel** (`ui/equipment_layout/equipment_panel.py`) - Inventory management
- **LogPanel** (`ui/log/log_panel.py`) - Combat log with optional TTS

## Critical Implementation Details

### HP Tracking During Combat (MOST IMPORTANT)
**NEVER read HP from database during active combat.** Combat HP is tracked in the UI:

```python
# CORRECT - How to heal/damage during combat
current_hp = parent.character_sheet.character_data.get('current_hit_points', 0)
max_hp = parent.character_sheet.character_data.get('max_hit_points', 1)
new_hp = min(current_hp + healing_amount, max_hp)
parent.character_sheet.character_data['current_hit_points'] = new_hp
parent.character_sheet.load_character_data()  # Refresh display

# WRONG - Will use stale data
current_hp = character_context.get('current_hit_points')  # STALE!
```

**Pattern Location:** `src/talekeeper/ui/action_cards/action_panel.py:_apply_damage_to_player()`

### Adding New Action Cards
All action cards live in `ActionPanel`. Follow this pattern:

1. Add to `ActionType` enum
2. Create card in `_create_feature_cards()`
3. Add handler in `_trigger_action()`
4. Implement action method
5. Check resources/prerequisites
6. Apply effects via appropriate service
7. Update UI via signals

**Reference:** `docs/ACTION_CARD_IMPLEMENTATION_GUIDE.md`

### Database Migrations
Place migration SQL files in `database/migrations/`. They auto-run on startup.

```sql
-- Migration naming: XXX_description.sql
-- Example: 042_add_warlock_invocations.sql

ALTER TABLE characters ADD COLUMN some_new_field TEXT;
```

Migrations handle duplicate columns gracefully (already-applied migrations are skipped).

### Service Layer Pattern
Services are stateless and database-driven. Common pattern:

```python
class MyAbilityService:
    def __init__(self, db_path='talekeeper.db'):
        self.db_path = db_path

    def use_ability(self, character_id: str, ability_name: str) -> dict:
        """Use an ability - check resources, apply effects, update DB."""
        conn = sqlite3.connect(self.db_path)
        # Check resources
        # Apply effects
        # Update database
        # Return result dict
        conn.close()
        return result
```

### Spell System Integration
Spells are handled by `SpellEffectsService` with handler classes:

```python
# In services/spell_handlers/
class CureWoundsHandler(BaseSpellHandler):
    def cast(self, caster, target, spell_level, context):
        healing = roll_dice(1, 8) + caster_cha_mod
        if spell_level > 1:
            healing += (spell_level - 1) * roll_dice(1, 8)
        # Apply healing...
```

**Auto-targeting:** Buff spells auto-target self in solo play (no dialog needed).

## Common Development Tasks

### Adding a New Class Feature
1. Add to appropriate class abilities service (e.g., `services/fighter_abilities.py`)
2. Add database entry if resources needed (`character_resources` table)
3. Create action card in `ActionPanel` if player-activated
4. Add UI handler in action panel
5. Update feature integration system if passive
6. Add tests in `tests/services/`

### Adding a New Spell
1. Insert into `spells` table via migration
2. Create handler in `services/spell_handlers/`
3. Register in `SpellEffectsService`
4. Add to appropriate class spell list
5. Test with pytest

### Adding Database Fields
1. Create migration SQL in `database/migrations/`
2. Use `ALTER TABLE` (handles existing DBs)
3. Provide defaults for existing rows
4. Update relevant service layer code
5. Test with `--force` database recreation

### Debugging Combat Issues
1. Check combat log (`LogPanel`) for detailed output
2. Verify action economy state (action/bonus/reaction available)
3. Check active conditions via `ConditionManager`
4. Verify HP tracking (character_sheet.character_data, NOT database)
5. Check weapon attack service for damage calculations
6. Review spell effects with `active_spell_effects` table

## Code Standards

### Required Patterns
- **No Unicode:** Use ASCII only (text or images for special chars)
- **No inline comments:** Unless specifically requested
- **Parameterized queries:** Always use `?` placeholders (prevent SQL injection)
- **Signal/slot connections:** For UI communication
- **Type hints:** Use where established
- **Error handling:** Graceful degradation, never crash

### Database Access
```python
# Always use context managers
with sqlite3.connect(self.db_path) as conn:
    conn.row_factory = sqlite3.Row  # Dict-like access
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
    result = cursor.fetchone()
```

### Qt Signal Pattern
```python
# Define signals in class
class MyPanel(QWidget):
    action_triggered = pyqtSignal(str, dict)

    def some_method(self):
        self.action_triggered.emit("action_name", context_data)

# Connect in main window
self.my_panel.action_triggered.connect(self._handle_action)
```

## Known Issues & Gotchas

### PyQt6 Version Pinning
**CRITICAL:** Must use PyQt6 6.7.0 exactly. Version 6.8+ breaks QtMultimedia on Windows.

```bash
pip install PyQt6==6.7.0
```

### Ollama Integration (Optional)
Campaign description service can use Ollama for narrative generation:
- Warning message "Ollama request failed" is EXPECTED if not running
- Application works fine without Ollama (uses fallback text)
- To enable: Install and run `ollama serve` separately

### Weapon Mastery Slots
Fighter, Barbarian, Rogue, and Paladin have UNLIMITED access to all weapon mastery properties - no slot tracking needed.

### Database Location
Database is in root directory (`talekeeper.db`), NOT in `src/` or `database/`. This is intentional for exe packaging.

## Testing Requirements

### Always Test After Changes
```bash
# Quick validation (30 seconds)
pytest tests/test_simple.py -v

# Core systems
pytest tests/core/ -v

# Service layer (class-specific)
pytest tests/services/test_fighter_abilities.py -v
pytest tests/services/test_weapon_attack_service.py -v

# Integration tests
pytest tests/integration/ -v
```

### Test Coverage Expectations
- All new class features must have tests
- Combat mechanics require integration tests
- UI changes should be manually verified
- Database migrations must be tested with both fresh and existing DBs

## Reference Documentation

### Class Implementation
- `docs/Fighter_Class.md` - Fighter features (complete)
- `docs/Barbarian_Class.md` - Barbarian features (complete)
- `docs/Rogue_Class.md` - Rogue features (complete)
- `docs/PALADIN_SUBCLASS_COMPLETE.md` - Paladin implementation
- `docs/WARLOCK_IMPLEMENTATION_STATUS.md` - Warlock progress

### System Documentation
- `docs/IMPLEMENTATION_GUIDE.md` - Comprehensive implementation reference
- `docs/HEX_MAP_SYSTEM.md` - Hex exploration system
- `docs/LONG_REST_IMPLEMENTATION_COMPLETE.md` - Rest mechanics
- `docs/SPELL_SYSTEM_COMPLETE_STATUS.md` - Spell implementation status
- `docs/BAG_OF_HOLDING_SYSTEM.md` - Inventory system
- `docs/ACTION_CARD_IMPLEMENTATION_GUIDE.md` - Action card patterns

## Quick Wins for New Features

### High-Impact, Low-Effort Changes
1. **New spells:** Add to database + create handler (1-2 hours)
2. **Class features:** Add to service + action card (2-3 hours)
3. **New monsters:** Insert JSON into seeds (30 min)
4. **UI themes:** Modify `ui/themes.py` (1 hour)
5. **Action cards:** Follow established pattern (1-2 hours)

### Complex Changes (Requires Planning)
1. **New class:** Full implementation (2-3 days)
2. **Multiclassing:** Requires engine redesign
3. **Multiplayer:** Major architecture change
4. **Mobile UI:** Complete UI rewrite needed
5. **Custom rule sets:** Requires new campaign frame system

## Development Workflow

1. **Read relevant docs** (`docs/IMPLEMENTATION_GUIDE.md` for deep dive)
2. **Check existing patterns** (find similar feature, copy pattern)
3. **Update database** (migration if schema change needed)
4. **Implement service layer** (business logic)
5. **Add UI integration** (action cards, panels)
6. **Write tests** (at minimum, smoke test)
7. **Verify manually** (run app, test feature)
8. **Check regression** (run test suite)

## Getting Help

- **Bug reports:** GitHub issues
- **Implementation questions:** See `docs/IMPLEMENTATION_GUIDE.md` (1800+ lines)
- **Architecture questions:** See this file + `src/talekeeper/core/game_engine_sqlite.py`
- **D&D rules questions:** Consult D&D 2024 Player's Handbook
