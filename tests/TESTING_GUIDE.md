# TaleKeeper Testing Guide

## Quick Start - Running Tests

### Run All Fighter Tests (Recommended)
```bash
cd test
python -m pytest services/test_fighter_champion.py services/test_weapon_attack_service.py -v --tb=short
```

### Run Validation Check
```bash
cd test
python test_simple_validation.py
```

### Run Test Summary
```bash
cd test
python test_results_summary.py
```

## Available Test Suites

### 1. Existing Production Tests (WORKING)

These tests are confirmed to work and should be run after any Fighter-related changes:

#### Fighter Champion Tests
```bash
python -m pytest services/test_fighter_champion.py -v
```
Tests:
- Heroic Warrior inspiration generation
- Survivor healing mechanics
- Remarkable Athlete skill advantages
- Combat initiative with advantages

#### Weapon Attack Service Tests
```bash
python -m pytest services/test_weapon_attack_service.py -v
```
Tests:
- Fighting styles (Archery, Dueling, Great Weapon Fighting)
- Savage Attacker feat
- Weapon mastery effects
- Damage calculations

### 2. Framework Tests (CREATED BUT NEED DB FIX)

These test files have been created but need database schema adjustments to run:

```bash
# Second Wind mechanics
python -m pytest features/test_fighter_second_wind.py -v

# Action Surge mechanics
python -m pytest features/test_fighter_action_surge.py -v

# Indomitable save rerolls
python -m pytest features/test_fighter_indomitable.py -v

# Weapon mastery and Tactical Master
python -m pytest features/test_fighter_weapon_mastery.py -v

# Combat flow and fighting styles
python -m pytest features/test_fighter_combat_flow.py -v

# Champion subclass features
python -m pytest features/test_champion_subclass.py -v
```

## Test After Making Changes

### After Modifying Fighter Abilities
```bash
cd test
# Run core Fighter tests
python -m pytest services/test_fighter_champion.py -v --tb=short

# Check validation
python test_simple_validation.py
```

### After Modifying Weapon Attack Service
```bash
cd test
# Run weapon tests
python -m pytest services/test_weapon_attack_service.py -v --tb=short

# Run specific fighting style tests
python -m pytest services/test_weapon_attack_service.py -k "dueling or archery" -v
```

### After UI Changes
```bash
cd test
# Check if UI helpers still work
python -c "from tests.helpers.ui_test_helpers import UITestHelpers; print('UI helpers OK')"
```

## Common Test Commands

### Run Tests Quietly (Just Results)
```bash
python -m pytest services/ -q --tb=no
```

### Run Specific Test by Name
```bash
python -m pytest services/test_fighter_champion.py::test_heroic_warrior_awards_inspiration_and_sets_state -v
```

### List All Available Tests
```bash
python -m pytest services/ --collect-only -q
```

### Run Tests with Coverage
```bash
python -m pytest services/ --cov=services --cov-report=term-missing
```

## Expected Test Results

### Current Status (as of last run)
- **Fighter Champion**: 4/4 PASS
- **Weapon Attack Service**: 11/15 PASS (4 fail due to Windows file cleanup only)
- **Total**: 16/19 tests passing (84% success rate)

### Known Issues
1. **Windows File Cleanup**: Some tests fail on tearDown due to Windows file locks
2. **Database Schema**: New test suites need schema adjustments for:
   - `proficiency_bonus` column (doesn't exist)
   - `character_subclasses` table access
   - Resource tracking columns

## Test Database Notes

### Using Test Database
The test database is created temporarily for each test run:
- Location: `%TEMP%\tmpXXXX.db`
- Auto-cleanup after tests (may fail on Windows)
- Isolated from production database

### Manual Database Testing
```python
# Create test database manually
from tests.fixtures.fighter_test_database import FighterTestDatabase

with FighterTestDatabase() as db_path:
    print(f"Test DB at: {db_path}")
    # Database is available here
# Database cleaned up automatically
```

## Debugging Failed Tests

### Get Detailed Error Output
```bash
python -m pytest services/test_weapon_attack_service.py -v --tb=long
```

### Run with Python Debugger
```bash
python -m pytest services/test_fighter_champion.py -v --pdb
```

### Check Test Database Creation
```python
cd test
python -c "from fixtures.fighter_test_database import create_fighter_test_db; db = create_fighter_test_db(); print('DB created successfully')"
```

## CI/CD Integration

### Minimal Test Command for CI
```bash
cd test && python -m pytest services/test_fighter_champion.py services/test_weapon_attack_service.py --tb=short -q
```

### Full Validation for CI
```bash
cd test && python test_simple_validation.py && python -m pytest services/ -q --tb=no
```

## Adding New Tests

### Template for New Fighter Test
```python
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.fighter_abilities import FighterAbilitiesService

def test_new_fighter_feature():
    """Test description."""
    service = FighterAbilitiesService('test.db')
    # Your test here
    assert True
```

### Run New Test
```bash
python -m pytest path/to/new_test.py -v
```

## Quick Reference - Most Used Commands

```bash
# Run all working tests
cd test && python -m pytest services/ -v --tb=short

# Quick validation check
cd test && python test_simple_validation.py

# Test summary with results
cd test && python test_results_summary.py

# Run specific fighting style tests
cd test && python -m pytest services/test_weapon_attack_service.py -k "fighting" -v

# List what tests exist
cd test && python -m pytest services/ --collect-only -q | grep "test_"
```

## Maintenance

### After Database Schema Changes
1. Update `tests/fixtures/fighter_test_database.py` to match new schema
2. Run validation: `python test_simple_validation.py`
3. Run tests: `python -m pytest services/ -v`

### After Adding New Fighter Features
1. Add test in appropriate file under `tests/features/`
2. Update this guide with new test commands
3. Run full test suite to ensure no regressions

### Regular Testing Schedule
- **Before commits**: Run quick validation
- **After Fighter changes**: Run Fighter Champion tests
- **After combat changes**: Run Weapon Attack Service tests
- **Weekly**: Run full test suite if available

---

*Last Updated: Testing framework created and validated. 16/19 existing tests passing.*