# Fighter Class Testing Framework

This directory contains a comprehensive testing framework for the TaleKeeper Fighter class implementation, as specified in `docs/Fighter_Class.md` line 205 onwards.

## Framework Overview

The testing framework provides systematic validation of all Fighter features according to D&D 2024 rules:

### Core Components

1. **Database Fixtures** (`fixtures/fighter_test_database.py`)
   - Automated test database creation with Fighter characters at various levels
   - Proper equipment, fighting styles, and subclass configurations
   - Isolated testing environment with cleanup

2. **UI Testing Helpers** (`helpers/ui_test_helpers.py`)
   - PyQt6 widget interaction utilities
   - Button clicking, text input, and UI state verification
   - ActionPanel-specific testing functions

3. **Feature Test Suites** (`features/`)
   - `test_fighter_second_wind.py` - Second Wind healing and resource management
   - `test_fighter_action_surge.py` - Action Surge activation and cooldown
   - `test_fighter_indomitable.py` - Save reroll mechanics and tracking
   - `test_fighter_weapon_mastery.py` - Mastery effects and Tactical Master
   - `test_fighter_combat_flow.py` - Fighting styles and complete combat sequences
   - `test_champion_subclass.py` - Champion-specific features

4. **UI Integration Tests** (`ui/test_action_panel_integration.py`)
   - ActionPanel button interactions
   - Resource counter updates
   - Combat flow validation

5. **Comprehensive Validation** (`test_fighter_comprehensive.py`)
   - End-to-end feature validation
   - Performance testing
   - Detailed reporting

## Tested Features

### Core Fighter Features
- ✅ **Second Wind**: Healing calculation (1d10 + level), resource tracking, rest recovery
- ✅ **Action Surge**: Additional action provision, level 2 availability, short rest recovery
- ✅ **Indomitable**: Save reroll mechanics, level 9+ availability, long rest recovery
- ✅ **Fighting Styles**: All 6 styles with D&D 2024 rule implementations
- ✅ **Weapon Mastery**: All mastery effects, reordering, no slot limitations

### Champion Subclass Features
- ✅ **Improved Critical**: 19-20 crit range at level 3, 18-20 at level 15
- ✅ **Remarkable Athlete**: Advantage on STR/DEX/CON checks and initiative
- ✅ **Heroic Warrior**: Inspiration generation at level 10
- ✅ **Studied Attacks**: Advantage tracking after missing same target
- ✅ **Survivor**: Healing when bloodied, Defy Death at 0 HP

### Advanced Features
- ✅ **Tactical Master**: Level 9+ mastery substitution (Push/Sap/Slow only)
- ✅ **Resource Management**: Independent tracking per character
- ✅ **Rest Recovery**: Short vs long rest resource restoration
- ✅ **Multiclass Support**: Fighter levels for feature availability

### Combat Integration
- ✅ **Attack Sequences**: Extra Attack, Action Surge combinations
- ✅ **Damage Calculations**: Fighting style bonuses, critical hits
- ✅ **Mastery + Style**: Combined effect applications
- ✅ **Edge Cases**: Natural 1/20, unconscious characters, resistance

## Usage

### Running All Tests
```bash
cd test
python run_fighter_tests.py
```

### Running Specific Test Categories
```bash
# Core Fighter features
python -m pytest features/test_fighter_second_wind.py -v
python -m pytest features/test_fighter_action_surge.py -v
python -m pytest features/test_fighter_indomitable.py -v

# Weapon systems
python -m pytest features/test_fighter_weapon_mastery.py -v
python -m pytest features/test_fighter_combat_flow.py -v

# Champion subclass
python -m pytest features/test_champion_subclass.py -v

# UI integration (requires Qt environment)
python -m pytest ui/test_action_panel_integration.py -v
```

### Comprehensive Validation
```bash
python test_fighter_comprehensive.py
```

### Framework Validation
```bash
python test_simple_validation.py
```

## Test Database Setup

The framework automatically creates isolated test databases with:

- Fighter characters at levels 1, 2, 3, 5, 9, 10, 15
- Appropriate equipment loadouts for each level
- Fighting style assignments for testing different styles
- Champion subclass assignments where applicable
- Proper resource initialization (Second Wind, Action Surge, etc.)

## Custom Test Creation

```python
from tests.fixtures.fighter_test_database import FighterTestDatabase
from services.fighter_abilities import FighterAbilitiesService

def test_custom_fighter_feature():
    with FighterTestDatabase() as db_path:
        service = FighterAbilitiesService(db_path)

        # Test your Fighter feature here
        result = service.some_fighter_method('fighter-3')
        assert result['success'] is True
```

## Implementation Status

### ✅ Completed Components
- Database fixture system
- All core Fighter feature tests
- Champion subclass feature tests
- UI interaction helpers
- Comprehensive validation framework
- Test runners and configuration

### 🔄 Integration Notes
The framework is designed to work with the existing TaleKeeper codebase:

- Uses actual `FighterAbilitiesService` implementation
- Tests against real database schema
- Validates UI components with PyQt6
- Follows project coding conventions

### 📋 Manual Testing Checklist

Some aspects require manual validation in the actual UI:

1. **Second Wind Button States**
   - Button shows correct resource count (e.g., "Second Wind (1/1)")
   - Button disables after use
   - Button re-enables after short rest

2. **Action Surge Visual Feedback**
   - Clear indication when Action Surge is active
   - Additional action becomes available in UI

3. **Weapon Mastery Tooltips**
   - Hover tooltips show correct mastery information
   - Substituted masteries show asterisk indication

4. **Champion Critical Range**
   - Attack rolls of 19 register as critical hits
   - Damage dice are properly doubled

## Performance Considerations

The framework includes performance testing to ensure:
- Fighter ability calculations complete within acceptable time
- Database operations are optimized
- UI updates don't cause noticeable lag

## Extending the Framework

To add tests for new Fighter features:

1. Create new test file in `features/`
2. Use `FighterTestDatabase` fixture
3. Import relevant services
4. Add to `run_fighter_tests.py` configuration
5. Update this README with new test coverage

## Dependencies

- pytest
- pytest-qt (for UI tests)
- sqlite3
- pathlib
- unittest.mock

## Integration with CI/CD

The framework is designed to work in automated testing environments:
- No external dependencies beyond Python standard library
- Isolated test databases prevent conflicts
- Clear exit codes for pass/fail status
- Comprehensive reporting for debugging

---

*This framework implements the testing infrastructure described in `docs/Fighter_Class.md` lines 205-225, providing systematic validation of the Fighter class implementation in TaleKeeper.*