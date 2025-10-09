# Class Abilities Architecture - Current State

## Overview
TaleKeeper currently uses **per-class ability services** - separate Python files for each class's runtime abilities. This document describes what exists before any refactoring.

**Date Documented:** 2025-10-09
**Purpose:** Baseline documentation before unified service architecture

---

## Current Architecture

### Ability Services (6 files, 3,533 total lines)
Located in `src/talekeeper/services/`:

| Service | Lines | Purpose |
|---------|-------|---------|
| `barbarian_abilities.py` | 770 | Rage, Reckless Attack, Brutal Strike, Relentless Rage |
| `fighter_abilities.py` | 804 | Second Wind, Action Surge, Indomitable, Tactical Mind |
| `rogue_abilities.py` | 517 | Sneak Attack, Cunning Action, Uncanny Dodge, Evasion |
| `wizard_abilities.py` | 426 | Arcane Recovery, spell slot management |
| `cleric_abilities.py` | 437 | Channel Divinity, Divine Intervention |
| `paladin_abilities.py` | 579 | Lay on Hands, Divine Smite, Channel Divinity |

**Total:** 3,533 lines of mostly duplicated patterns

### Database Tables (Class-Specific Features)
Each class has its own `*_features` table:

```sql
-- Fighter
CREATE TABLE fighter_features (
    character_id TEXT PRIMARY KEY,
    level INTEGER,
    fighting_style TEXT,
    action_surge_uses_current INTEGER DEFAULT 0,
    action_surge_uses_max INTEGER DEFAULT 0,
    second_wind_used BOOLEAN DEFAULT FALSE,
    indomitable_uses_current INTEGER DEFAULT 0,
    indomitable_uses_max INTEGER DEFAULT 0,
    extra_attacks INTEGER DEFAULT 1,
    weapon_masteries_known INTEGER DEFAULT 3
);

-- Barbarian
CREATE TABLE barbarian_features (
    character_id TEXT PRIMARY KEY,
    level INTEGER,
    rage_uses_current INTEGER DEFAULT 0,
    rage_uses_max INTEGER DEFAULT 2,
    rage_damage_bonus INTEGER DEFAULT 2,
    is_raging BOOLEAN DEFAULT FALSE,
    rage_turns_remaining INTEGER DEFAULT 0,
    unarmored_defense_active BOOLEAN DEFAULT TRUE,
    reckless_attack_available BOOLEAN DEFAULT FALSE,
    danger_sense_active BOOLEAN DEFAULT FALSE
);

-- Rogue
CREATE TABLE rogue_features (
    character_id TEXT PRIMARY KEY,
    level INTEGER,
    sneak_attack_dice INTEGER DEFAULT 1,
    expertise_skills TEXT,
    cunning_action_available BOOLEAN DEFAULT FALSE,
    uncanny_dodge_available BOOLEAN DEFAULT FALSE,
    uncanny_dodge_used BOOLEAN DEFAULT FALSE,
    evasion_available BOOLEAN DEFAULT FALSE,
    archetype TEXT,
    cunning_strike_available BOOLEAN DEFAULT FALSE
);

-- Also: wizard_features, cleric_features, paladin_features, warlock_features
```

---

## Common Patterns Across Services

### 1. Database Connection Management
Every service has identical connection pattern:
```python
class BarbarianAbilitiesService:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
```

### 2. Level-Based Resource Calculation
All services recalculate resources based on level:
```python
# Barbarian
def update_barbarian_resources_for_level(self, character_id: str, level: int):
    rage_uses_max = 2
    if level >= 17: rage_uses_max = 6
    elif level >= 12: rage_uses_max = 5
    elif level >= 6: rage_uses_max = 4
    elif level >= 3: rage_uses_max = 3

# Fighter
def update_fighter_resources_for_level(self, character_id: str, level: int):
    action_surge_max = 1
    if level >= 17: action_surge_max = 2

    indomitable_max = 0
    if level >= 9: indomitable_max = 1
    if level >= 13: indomitable_max = 2
    if level >= 17: indomitable_max = 3
```

### 3. Rest Recovery
Every service has a `rest_*_resources()` method:
```python
# Barbarian
def rest_barbarian_resources(self, character_id: str, rest_type: str):
    if rest_type in ['short', 'long']:
        # Reset rage uses
        # Reset brutal strike
    if rest_type == 'long':
        # Reset relentless rage

# Fighter
def rest_fighter_resources(self, character_id: str, rest_type: str):
    if rest_type in ['short', 'long']:
        # Reset action surge
        # Reset second wind
    if rest_type == 'long':
        # Reset indomitable

# Rogue
def rest_rogue_resources(self, character_id: str, rest_type: str):
    if rest_type == 'long':
        # Reset stroke of luck
        # Reset uncanny dodge
```

### 4. Ability Use Methods
Each ability has its own method with similar structure:
```python
def use_<ability_name>(self, character_id: str, **kwargs) -> Dict[str, Any]:
    # 1. Check if character has ability
    # 2. Check uses remaining
    # 3. Decrement uses
    # 4. Apply effects
    # 5. Return results dict
```

**Examples:**
- `use_rage()`, `use_reckless_attack()`, `use_brutal_strike()` (Barbarian)
- `use_second_wind()`, `use_action_surge()`, `use_indomitable()` (Fighter)
- `use_cunning_action()`, `use_uncanny_dodge()`, `use_steady_aim()` (Rogue)

---

## Key Methods by Service

### BarbarianAbilitiesService (19 methods)
- `get_barbarian_level()` - Level lookup
- `update_barbarian_resources_for_level()` - Resource scaling
- `use_rage()` - Start rage (uses, damage bonus)
- `end_rage()` - End rage state
- `use_reckless_attack()` - Gain advantage, enemies gain advantage
- `use_brutal_strike()` - Enhanced attacks during rage (4 types)
- `check_relentless_rage()` - Death saving throw advantage
- `rest_barbarian_resources()` - Short/long rest recovery
- `process_berserker_turn_start()` - Subclass feature
- `use_berserker_retaliation()` - Subclass feature
- `use_intimidating_presence()` - Subclass feature
- `has_danger_sense_advantage()` - Dex save advantage
- `has_feral_instinct()` - Initiative advantage
- `add_primal_knowledge_skill()` - Skill proficiency

### FighterAbilitiesService (17 methods)
- `get_fighter_level()` - Level lookup
- `update_fighter_resources_for_level()` - Resource scaling
- `use_second_wind()` - Heal 1d10 + level
- `use_action_surge()` - Extra action
- `use_tactical_mind()` - Add INT to failed check
- `use_indomitable()` - Reroll failed save
- `rest_fighter_resources()` - Short/long rest recovery
- `process_champion_turn_start()` - Subclass regeneration
- `check_heroic_warrior()` - Subclass feature (level 18)
- `check_survivor()` - Subclass regeneration (level 18)
- `has_remarkable_athlete()` - Half proficiency to STR/DEX/CON checks
- `get_remarkable_athlete_jump_bonus()` - Subclass feature
- `roll_skill_check()` - Skill checks with remarkable athlete

### RogueAbilitiesService (18 methods)
- `get_rogue_level()` - Level lookup
- `update_rogue_resources_for_level()` - Resource scaling
- `calculate_sneak_attack_damage()` - XdY based on level
- `check_sneak_attack_eligibility()` - Finesse weapon, advantage, or ally nearby
- `use_cunning_action()` - Bonus action Dash/Disengage/Hide
- `use_steady_aim()` - Trade movement for advantage
- `use_uncanny_dodge()` - Halve incoming damage
- `apply_evasion()` - No damage on Dex save success
- `apply_reliable_talent()` - Minimum 10 on proficient skill checks
- `use_stroke_of_luck()` - Auto-hit or auto-succeed (level 20)
- `rest_rogue_resources()` - Long rest recovery

---

## Character Creation Flow

When a character is created, `game_engine_sqlite.py` calls class-specific initializers:

```python
# game_engine_sqlite.py lines 1350-1367
def _initialize_class_features(self, cursor, character_id, character_data):
    class_id = character_data.get('class_id', '').lower()

    if class_id == 'fighter':
        self._initialize_fighter_features(cursor, character_id, character_data)
    elif class_id == 'barbarian':
        self._initialize_barbarian_features(cursor, character_id, character_data)
    elif class_id == 'rogue':
        self._initialize_rogue_features(cursor, character_id, character_data)
    # ... etc for all classes
```

**Initialization is INLINE** - no external service calls during character creation (avoids database lock issues).

Example from `_initialize_barbarian_features()`:
```python
def _initialize_barbarian_features(self, cursor, character_id: str, character_data: Dict):
    level = character_data.get('level', 1)

    # Calculate rage uses (2 at 1st, scales to 6 at 17th, unlimited at 20th)
    if level >= 20: rage_uses = 999
    elif level >= 17: rage_uses = 6
    elif level >= 12: rage_uses = 5
    elif level >= 6: rage_uses = 4
    elif level >= 3: rage_uses = 3
    else: rage_uses = 2

    # Calculate rage damage (+2 base, +3 at 9th, +4 at 16th)
    if level >= 16: rage_damage = 4
    elif level >= 9: rage_damage = 3
    else: rage_damage = 2

    # Insert into barbarian_features table
    cursor.execute("""
        INSERT INTO barbarian_features (
            character_id, level, rage_uses_max, rage_damage_bonus,
            unarmored_defense_active, reckless_attack_available, danger_sense_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (character_id, level, rage_uses, rage_damage,
          True, level >= 2, level >= 2))
```

---

## Runtime Ability Usage

**Ability services are ONLY used during gameplay**, not character creation.

Example flow for using Second Wind:
1. UI calls `FighterAbilitiesService.use_second_wind(character_id)`
2. Service opens its own connection (safe - outside character creation transaction)
3. Checks `fighter_features.second_wind_used`
4. Rolls healing (1d10 + level)
5. Updates HP and marks second_wind_used = TRUE
6. Returns result dict to UI

---

## Problems with Current Architecture

### 1. Code Duplication (3,533 lines)
- Every service has identical connection management
- Every service has similar level-based scaling logic
- Every service has similar rest recovery logic
- Every service has similar ability use patterns

### 2. Rigid Schema (11+ tables)
- Adding a new class requires:
  - New Python service file (500+ lines)
  - New database table schema
  - New initialization method in game_engine_sqlite.py
  - New rest recovery logic
  - New UI integration

### 3. Inconsistent Patterns
- Some abilities use `uses_current/uses_max` (Action Surge)
- Some use boolean flags (Second Wind)
- Some use JSON arrays (Expertise skills)
- No unified ability definition system

### 4. Testing Complexity
- 6 separate services to test
- Different test patterns for each class
- Hard to ensure consistency across classes

### 5. Scalability Issues
- 11 D&D classes total (6 implemented so far)
- Each new class = 500-800 new lines of code
- Full implementation = 8,800+ lines of duplicated patterns

---

## What Works Well

### 1. Character Creation (Inline Pattern)
- All class initialization is inline in `game_engine_sqlite.py`
- No external service calls during creation
- No database lock issues
- Fast and reliable

### 2. Clear Separation
- Services only used at runtime, not creation
- Each class's features are isolated
- Easy to find class-specific logic

### 3. Type Safety
- Each service returns `Dict[str, Any]` with predictable structure
- UI knows what to expect from each ability

---

## Next Steps (Testing Before Refactoring)

Before building a unified architecture, we need to validate current functionality:

### Test Suite Requirements
1. **Character Creation Tests**
   - Create Fighter, Barbarian, Rogue at levels 1, 5, 10, 15, 20
   - Verify `*_features` tables populated correctly
   - Verify resource maximums match level

2. **Character Save/Load Tests**
   - Create character with abilities used
   - Save to database
   - Load from database
   - Verify state persists (uses_current, boolean flags, etc.)

3. **Ability Usage Tests**
   - Test each major ability (Second Wind, Rage, Sneak Attack, etc.)
   - Verify uses decrement correctly
   - Verify effects apply correctly
   - Verify restrictions enforced (can't use if no uses left)

4. **Rest Recovery Tests**
   - Use abilities to deplete uses
   - Take short rest
   - Verify short rest abilities restore
   - Take long rest
   - Verify all abilities restore

5. **Level Progression Tests**
   - Create level 1 character
   - Level up to 20
   - Verify resources scale correctly at each level
   - Verify new abilities unlock at correct levels

---

## Files Involved

### Services (Runtime)
- `src/talekeeper/services/barbarian_abilities.py`
- `src/talekeeper/services/fighter_abilities.py`
- `src/talekeeper/services/rogue_abilities.py`
- `src/talekeeper/services/wizard_abilities.py`
- `src/talekeeper/services/cleric_abilities.py`
- `src/talekeeper/services/paladin_abilities.py`

### Initialization (Character Creation)
- `src/talekeeper/core/game_engine_sqlite.py`
  - `_initialize_class_features()` (line 1350)
  - `_initialize_fighter_features()` (line 1369)
  - `_initialize_barbarian_features()` (line 1396)
  - `_initialize_rogue_features()` (line 1619)
  - `_initialize_paladin_features()` (line 1647)
  - `_initialize_warlock_features()` (line 1466)

### Database Tables
- `fighter_features`
- `barbarian_features`
- `rogue_features`
- `wizard_features`
- `cleric_features`
- `paladin_features`
- `warlock_features`

---

## Comparison: Inline vs External Service Pattern

### Character Creation (Inline) ✅
```python
# SAFE - All in one transaction
def _initialize_barbarian_features(self, cursor, character_id, character_data):
    # Uses passed-in cursor from parent transaction
    cursor.execute("INSERT INTO barbarian_features ...")
    cursor.execute("INSERT INTO character_features ...")
    # No connection opens, no locks
```

### Runtime Abilities (External Service) ✅
```python
# SAFE - Outside any transaction
service = BarbarianAbilitiesService()
result = service.use_rage(character_id)
# Opens own connection, commits own transaction
```

### Previous Warlock Pattern (External During Creation) ❌
```python
# UNSAFE - Nested transaction
def _initialize_warlock_features(self, cursor, character_id, character_data):
    cursor.execute("INSERT INTO warlock_features ...")
    # BAD: Opens new connection while cursor still active
    patron_manager.initialize_patron_features(character_id, level)
    # Result: Database lock error
```

**Lesson:** Keep character creation inline, use external services only at runtime.

---

## Summary

**Current State:**
- 6 ability services, 3,533 lines of code
- 7+ class-specific feature tables
- Inline initialization (good)
- External runtime services (good)
- Lots of code duplication (problem)
- Rigid schema (problem)

**Before Refactoring:**
- Run comprehensive regression tests
- Document all current abilities
- Verify save/load functionality
- Ensure no regressions during migration

**After Testing:**
- Design unified ability service
- Database-driven ability definitions
- Single service handles all classes
- Maintain inline initialization pattern
