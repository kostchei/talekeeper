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
# Run complete test suite with UI interaction
python testing/run_tests.py

# Test specific features (fighting styles, feats)
python testing/run_tests.py --mode specific

# Interactive testing with pauses
python testing/run_tests.py --mode interactive

# Visual debugging mode
python testing/run_tests.py --mode visual
```

### Linting & Type Checking
```bash
# Lint Python code
python -m pylint main.py ui/ core/ services/

# Type check (if mypy is configured)
python -m mypy main.py
```

## Project Structure
```
TaleKeeper/
├── main.py                 # Entry point
├── talekeeper.db           # SQLite database (auto-created)
├── database/               # Database management
│   ├── database_init.py      # Database initialization
│   ├── schema/                # Database schema files
│   ├── seeds/                 # Game data (D&D rules)
│   └── migrations/            # Database updates
├── core/
│   ├── game_engine_sqlite.py  # Main game coordinator
│   ├── feature_integration.py # Feature system
│   └── combat_engine.py       # Combat mechanics
├── ui/
│   ├── main_window.py         # Main window with panels
│   └── themes.py               # Light/dark theme system
├── character_sheet/            # Character display
├── encounter_pane/             # Combat/exploration
├── action_cards/               # Combat actions UI
├── equipment_layout/           # Equipment/inventory
├── services/                   # Game services
│   └── feat_effects.py        # Feat implementations
└── testing/                   # Qt6-based testing framework
    ├── test_framework.py       # Core testing infrastructure
    ├── test_specific_features.py # Feature tests
    └── run_tests.py           # Test runner
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

## Recent Additions
- Comprehensive Qt6 testing framework (Dec 2024)
- Fighting style validation tests
- Visual debugging mode for UI testing
- HTML test reporting with screenshots

## Next Priorities
- Complete spell system implementation
- Monster AI improvements
- Save slot management enhancements
- Performance optimization for large encounters