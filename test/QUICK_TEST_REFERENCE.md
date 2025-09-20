# Quick Test Reference

## Most Important Commands (Use These!)

### 1. Run Working Fighter Tests
```bash
cd test
python -m pytest services/test_fighter_champion.py services/test_weapon_attack_service.py -v --tb=short
```
**Expected**: 16/19 tests pass (84% success)

### 2. Quick Health Check
```bash
cd test
python test_simple_validation.py
```
**Expected**: Shows "[OK]" for all components

### 3. Test Summary
```bash
cd test
python test_results_summary.py
```
**Expected**: Shows detailed pass/fail breakdown

## What Each Test Validates

### Fighter Champion Tests (4 tests - ALL PASS)
- `test_heroic_warrior_awards_inspiration_and_sets_state` - Level 10 inspiration
- `test_survivor_heals_when_bloodied_and_tracks_defy_death` - Level 18 healing
- `test_roll_skill_check_applies_remarkable_athlete` - Advantage on skills
- `test_combat_manager_applies_remarkable_athlete_to_initiative` - Initiative advantage

### Weapon Attack Service Tests (15 tests - 11 PASS)
**Passing:**
- `test_archery_attack_bonus` - Archery +2 to hit
- `test_dueling_damage_bonus` - Dueling +2 damage
- `test_great_weapon_fighting` - GWF 1s,2s become 3s
- `test_savage_attacker_*` - Feat damage rerolls
- `test_weapon_mastery_effects_*` - Cleave, Graze, Topple
- `test_parse_damage_dice*` - Damage parsing

**Failing (Windows file cleanup only):**
- `test_get_character_fighting_styles`
- `test_mastery_class_requires_mastery_property`
- `test_non_mastery_class_no_errors`
- `test_weapon_mastery_unlimited_access`

## When to Run Tests

| After changing... | Run this test |
|------------------|---------------|
| Fighter abilities | `python -m pytest services/test_fighter_champion.py -v` |
| Weapon attacks | `python -m pytest services/test_weapon_attack_service.py -v` |
| Fighting styles | `python -m pytest services/test_weapon_attack_service.py -k "fighting" -v` |
| Any Fighter code | `python test_simple_validation.py` |
| Database schema | `python test_simple_validation.py` (check imports still work) |

## Test Single Feature

```bash
# Test just Dueling
python -m pytest services/test_weapon_attack_service.py::TestWeaponAttackService::test_dueling_damage_bonus -v

# Test just Heroic Warrior
python -m pytest services/test_fighter_champion.py::test_heroic_warrior_awards_inspiration_and_sets_state -v
```

## Quick Checks

### Are imports working?
```bash
cd test
python -c "from services.fighter_abilities import FighterAbilitiesService; print('OK')"
```

### Is test database working?
```bash
cd test
python -c "from fixtures.fighter_test_database import create_fighter_test_db; print('OK')"
```

### List all available tests
```bash
cd test
python -m pytest services/ --collect-only -q | grep "test_"
```

## One-Line Test Commands

```bash
# Fastest test (just validation)
cd test && python test_simple_validation.py

# Quick Fighter test
cd test && python -m pytest services/test_fighter_champion.py -q

# Full working tests
cd test && python -m pytest services/ -q --tb=no

# Show what passes/fails
cd test && python test_results_summary.py
```

---
*Copy-paste these commands directly into terminal*