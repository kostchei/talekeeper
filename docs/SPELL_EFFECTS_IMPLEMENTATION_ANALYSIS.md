# Spell Effects System - Implementation Analysis & Plan

## Executive Summary

This document analyzes existing TaleKeeper systems and provides a detailed plan to implement the missing spell effects infrastructure needed for the 38 paladin spells.

**Status**: Infrastructure is 60% complete. Core systems exist but spell-specific effect tracking is missing.

---

## Existing Systems (Already Implemented)

### 1. Spellcasting Foundation ✅
**Location**: `src/talekeeper/services/spellcasting_service.py`
- Spell slot management (tracking, consumption, restoration)
- Spell preparation system
- Casting action economy integration
- Ritual casting support

### 2. Concentration System ✅
**Location**: `src/talekeeper/services/concentration_system.py`
- Concentration tracking during combat
- Automatic concentration breaking on new concentration spell
- Constitution saves when damaged
- Duration tracking in rounds

### 3. Condition System ✅
**Location**: `src/talekeeper/services/condition_manager.py`
- Full D&D 2024 condition tracking
- Mechanical effects for all conditions
- Save-based removal
- Duration tracking (rounds, minutes, hours)
- **Missing**: Source spell tracking columns (need enhancement)

### 4. Combat Turn System ✅
**Location**: `src/talekeeper/core/combat_manager.py`
- Turn start/end processing (`advance_turn()`, `_start_new_round()`)
- Action economy tracking (action, bonus action, reaction)
- Initiative order management
- Champion turn-start automation (shows turn processing is extensible)

### 5. Magical Bonuses System ✅
**Location**: `src/talekeeper/services/item_effects.py`
- AC bonuses from magical items
- Attack/damage bonuses from items
- Ability score bonuses
- Skill bonuses
- **Database**: `character_magical_bonuses` table exists
- **Limitation**: Only tracks item bonuses, not spell buffs

### 6. Temporary HP (Partial) ⚠️
**Location**: `characters.hit_points_temporary` column
- Basic temp HP column exists in characters table
- **Missing**: Source tracking, turn-by-turn regeneration (Heroism)
- **Missing**: Service layer for temp HP management

### 7. Database Tables ✅
**Existing from migration 011**:
- `character_spell_slots` - Spell slot tracking
- `character_spells` - Known/prepared spells
- `character_spellcasting` - Spellcasting stats
- `character_concentration` - Concentration tracking
- `spells` - Spell definitions
- `spell_class_lists` - Class spell lists
- `character_conditions` - Condition tracking (needs enhancement)
- `character_magical_bonuses` - Item bonuses (could be extended for spell buffs)

---

## Missing Components (Need Implementation)

### 1. SpellEffectsService ❌
**Required Service**: `src/talekeeper/services/spell_effects_service.py`

**Purpose**: Central hub for applying and tracking spell effects

**Key Methods Needed**:
```python
# Core Effects
apply_healing(target_id, amount, source_spell)
apply_damage(target_id, damage, damage_type, source_spell)
apply_buff(target_id, buff_data, duration_rounds)
remove_buff(target_id, spell_id)

# Temp HP Management
apply_temp_hp(target_id, amount, source_spell)
get_temp_hp(character_id)
set_temp_hp(character_id, amount, source)

# Turn Processing
process_turn_start_effects(character_id)
process_turn_end_effects(character_id)
decrement_effect_durations(character_id)

# Bonus Queries (for combat integration)
get_ac_modifier(character_id)
get_attack_bonus(character_id)
get_damage_bonus(character_id)
get_condition_immunities(character_id)
get_resistances(character_id)
```

**Reuse Opportunity**: Can extend `ItemEffectsService` pattern for bonus calculation

### 2. Active Spell Effects Table ❌
**New Table Required**: `active_spell_effects`

**Purpose**: Track all active spell buffs/debuffs (not just concentration)

**Schema**:
```sql
CREATE TABLE active_spell_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_name TEXT NOT NULL,
    spell_level_cast INTEGER NOT NULL,
    effect_type TEXT NOT NULL,
    effect_data TEXT,
    duration_type TEXT NOT NULL,
    duration_remaining INTEGER,
    rounds_remaining INTEGER,
    concentration BOOLEAN DEFAULT FALSE,
    caster_id TEXT,
    target_id TEXT,
    applied_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (spell_id) REFERENCES spells(id),
    FOREIGN KEY (caster_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

**Effect Types**:
- `ac_bonus` - Shield of Faith (+2 AC)
- `attack_bonus` - Bless (+1d4 to attacks)
- `save_bonus` - Bless (+1d4 to saves)
- `damage_bonus_per_hit` - Divine Favor (+1d4 radiant per hit)
- `temp_hp_per_turn` - Heroism (CHA temp HP each turn)
- `condition_immunity` - Heroism (immune frightened)
- `hp_maximum_increase` - Aid (+5 max HP)
- `weapon_enchantment` - Magic Weapon (+1 weapon)
- `next_hit_bonus_damage` - Searing Smite (Xd6 fire on next hit)
- `creature_type_protection` - Protection from Evil and Good
- `death_prevention` - Death Ward

### 3. Enhanced Temp HP System ❌
**Option A**: New table `character_temp_hp`
```sql
CREATE TABLE character_temp_hp (
    character_id TEXT PRIMARY KEY,
    temp_hp_current INTEGER NOT NULL DEFAULT 0,
    temp_hp_source TEXT,
    temp_hp_granted_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

**Option B**: Use existing `characters.hit_points_temporary` + track source in `active_spell_effects`

**Recommendation**: Option B (reuse existing column, track source separately)

### 4. Spell Summons Table ❌
**New Table Required**: `spell_summons` (for Find Steed, future summons)

```sql
CREATE TABLE spell_summons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    summon_name TEXT NOT NULL,
    summon_type TEXT NOT NULL,
    stat_block TEXT NOT NULL,
    current_hp INTEGER NOT NULL,
    max_hp INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    summoned_at TEXT DEFAULT (datetime('now')),
    dismissed_at TEXT,

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);
```

### 5. Enhanced Condition Tracking ❌
**Enhancement Required**: Add columns to `character_conditions`

**Current Schema**:
```
id, character_id, condition_name, applied_at, duration
```

**Needed Additions**:
```sql
ALTER TABLE character_conditions ADD COLUMN source_spell_id TEXT;
ALTER TABLE character_conditions ADD COLUMN duration_rounds INTEGER;
ALTER TABLE character_conditions ADD COLUMN save_dc INTEGER;
ALTER TABLE character_conditions ADD COLUMN save_ability TEXT;
```

**Note**: `ConditionManager` service already exists and handles mechanics

### 6. SpellHandler Registry Pattern ❌
**New Architecture Required**: Registry pattern for spell execution

**Files Needed**:
- `src/talekeeper/services/spell_handlers/__init__.py`
- `src/talekeeper/services/spell_handlers/base_handler.py`
- `src/talekeeper/services/spell_handlers/healing_handlers.py`
- `src/talekeeper/services/spell_handlers/buff_handlers.py`
- `src/talekeeper/services/spell_handlers/smite_handlers.py`
- etc.

**Base Pattern**:
```python
class SpellHandler:
    def can_cast(self, caster_id, context) -> Tuple[bool, str]:
        pass

    def execute(self, caster_id, targets, slot_level, context) -> Dict:
        pass

    def on_turn_start(self, character_id) -> Optional[Dict]:
        pass

    def on_turn_end(self, character_id) -> Optional[Dict]:
        pass

class SpellHandlerRegistry:
    def __init__(self):
        self.handlers = {}

    def register(self, spell_id, handler):
        self.handlers[spell_id] = handler

    def execute_spell(self, spell_id, caster_id, targets, slot_level, context):
        handler = self.handlers.get(spell_id)
        return handler.execute(caster_id, targets, slot_level, context)
```

### 7. Integration Points ❌
**Modifications Required**:

**A. Combat Manager** - Turn processing
```python
# In combat_manager.py advance_turn() method
def advance_turn(self):
    current = self.get_current_combatant()

    # NEW: Process spell effects at turn start
    if current and current.type == CombatantType.PLAYER:
        spell_effects = self.spell_effects_service.process_turn_start_effects(current.id)
        for effect in spell_effects:
            self._apply_effect_result(effect)

    # Existing code...
```

**B. Weapon Attack Service** - Damage bonuses
```python
# In weapon_attack_service.py
def calculate_damage(self, character_id, weapon):
    base_damage = self._roll_weapon_damage(weapon)

    # Existing: Item bonuses
    item_bonus = self.item_effects.get_damage_bonus(character_id)

    # NEW: Spell bonuses (Divine Favor, etc.)
    spell_bonus = self.spell_effects.get_damage_bonus(character_id)

    return base_damage + item_bonus + spell_bonus['total']
```

**C. AC Calculation** - AC modifiers
```python
# In game_engine_sqlite.py or character resources
def calculate_ac(self, character_id):
    base_ac = self._get_base_ac()

    # Existing: Item bonuses
    item_bonus = self.item_effects.get_ac_bonus(character_id)

    # NEW: Spell bonuses (Shield of Faith)
    spell_bonus = self.spell_effects.get_ac_modifier(character_id)

    return base_ac + item_bonus + spell_bonus
```

**D. Attack Rolls** - Bless bonus
```python
# In weapon_attack_service.py
def calculate_attack_roll(self, character_id):
    roll = d20()
    modifiers = self._get_base_modifiers()

    # NEW: Check for Bless
    bless_buff = self.spell_effects.get_buff(character_id, 'bless')
    if bless_buff:
        bless_bonus = roll_dice(1, 4)
        modifiers += bless_bonus
        self._log(f"[BLESS] +{bless_bonus} to attack roll")

    return roll + modifiers
```

---

## Architecture Analysis

### What We Can Reuse

1. **ItemEffectsService pattern** - Similar bonus tracking for spells
2. **ConditionManager** - Already handles condition mechanics
3. **ConcentrationSystem** - Already handles concentration spells
4. **Combat turn hooks** - Turn start/end processing exists
5. **Database patterns** - Same FK/index patterns for new tables

### What's Unique to Spells

1. **Duration tracking in rounds** (not just permanent like items)
2. **Turn-by-turn effects** (Heroism temp HP refresh)
3. **Next-hit triggers** (Searing Smite consumes on hit)
4. **Stacking rules** (multiple buffs vs. same-name buffs)
5. **Concentration linkage** (buff ends when concentration breaks)

---

## Implementation Plan

### Phase 0: Foundation (Week 1) - 8-10 hours

#### Stage 0.1: Database Migration
**File**: `database/migrations/023_spell_effects_system.sql`

```sql
-- Create active_spell_effects table
CREATE TABLE IF NOT EXISTS active_spell_effects (
    -- Schema as defined above
);

-- Enhance character_conditions table
ALTER TABLE character_conditions ADD COLUMN source_spell_id TEXT;
ALTER TABLE character_conditions ADD COLUMN duration_rounds INTEGER;
ALTER TABLE character_conditions ADD COLUMN save_dc INTEGER;
ALTER TABLE character_conditions ADD COLUMN save_ability TEXT;

-- Create spell_summons table
CREATE TABLE IF NOT EXISTS spell_summons (
    -- Schema as defined above
);

-- Create indexes
CREATE INDEX idx_active_effects_character ON active_spell_effects(character_id);
CREATE INDEX idx_active_effects_spell ON active_spell_effects(spell_id);
CREATE INDEX idx_active_effects_caster ON active_spell_effects(caster_id);
CREATE INDEX idx_active_effects_expiration ON active_spell_effects(expires_at);
CREATE INDEX idx_conditions_spell ON character_conditions(source_spell_id);
CREATE INDEX idx_summons_character ON spell_summons(character_id);
CREATE INDEX idx_summons_active ON spell_summons(character_id, is_active);
```

**Test**: Run migration, verify tables created
```bash
python -m pytest tests/regression/test_database_integrity.py -v
```

#### Stage 0.2: SpellEffectsService Implementation
**File**: `src/talekeeper/services/spell_effects_service.py`

**Core Methods** (500+ lines):
- Buff management (apply, remove, query)
- Temp HP system
- Turn processing
- Bonus calculation

**Dependencies**:
- ConcentrationSystem (existing)
- ConditionManager (existing)
- Database connection

**Test**: Unit tests for each method
```bash
python -m pytest tests/unit/test_spell_effects_service.py -v
```

#### Stage 0.3: SpellHandler Base Classes
**File**: `src/talekeeper/services/spell_handlers/base_handler.py`

**Classes**:
- `SpellHandler` - Base class
- `SpellHandlerRegistry` - Registry pattern
- Helper utilities

**Test**: Test registry pattern
```bash
python -m pytest tests/unit/test_spell_handler_registry.py -v
```

**Regression Test**: Run quick regression
```bash
python tests/run_regression_tests.py --quick
```

---

### Phase 1: Healing Spells (Week 1-2) - 4 hours

#### Spells: Cure Wounds, Prayer of Healing

**File**: `src/talekeeper/services/spell_handlers/healing_handlers.py`

**Implementation**:
```python
class CureWoundsHandler(SpellHandler):
    def execute(self, caster_id, targets, slot_level, context):
        cha_mod = self._get_ability_mod(caster_id, 'charisma')
        healing = roll_dice(slot_level, 8) + cha_mod
        target_id = targets[0] if targets else caster_id
        return self.effects.apply_healing(target_id, healing, 'cure_wounds')
```

**Integration**: Auto-generates spell cards (existing system)

**Test**:
```bash
python -m pytest tests/spells/test_healing_spells.py -v
```

**Regression Test**:
```bash
python tests/run_regression_tests.py --quick
```

---

### Phase 2: Simple Buffs (Week 2) - 6 hours

#### Spells: Shield of Faith, Divine Favor, Aid

**File**: `src/talekeeper/services/spell_handlers/buff_handlers.py`

**Integration Points**:
- Shield of Faith → AC calculation
- Divine Favor → Damage calculation
- Aid → HP maximum

**Test**:
```bash
python -m pytest tests/spells/test_buff_spells.py -v
python -m pytest tests/integration/test_ac_calculation.py -v
```

**Regression Test**:
```bash
python tests/run_regression_tests.py --full
```

---

### Phase 3: Heroism & Temp HP (Week 2-3) - 4 hours

#### Spells: Heroism

**New Feature**: Turn-by-turn temp HP refresh

**Implementation**:
```python
class HeroismHandler(SpellHandler):
    def on_turn_start(self, character_id):
        heroism_buff = self.effects.get_buff(character_id, 'heroism')
        if heroism_buff:
            temp_hp = heroism_buff['temp_hp_per_turn']
            self.effects.set_temp_hp(character_id, temp_hp, 'heroism')
            return {'temp_hp_granted': temp_hp}
        return None
```

**Integration**: Combat manager turn start hook

**Test**:
```bash
python -m pytest tests/spells/test_heroism_temp_hp.py -v
```

**Regression Test**:
```bash
python tests/run_regression_tests.py --quick
```

---

### Phase 4: Bless & Attack Bonuses (Week 3) - 6 hours

#### Spells: Bless

**Complex Integration**: Attack rolls AND saving throws

**Implementation Points**:
- Weapon attack service (attack rolls)
- Concentration system (saves)
- Other save locations

**Test**:
```bash
python -m pytest tests/spells/test_bless_comprehensive.py -v
```

**Regression Test**:
```bash
python tests/run_regression_tests.py --full
```

---

### Phases 5-9: Remaining Spells (Weeks 3-6)

Follow same pattern:
1. Implement spell handler
2. Integrate with existing systems
3. Write tests
4. Run regression tests
5. Move to next spell

**Total Spells**: 38 paladin spells
**Estimated Total Time**: 60-80 hours (6-8 weeks)

---

## Testing Strategy

### Regression Testing at Each Stage

**Quick Tests** (30 seconds) - Run after EVERY change:
```bash
python tests/run_regression_tests.py --quick
```
- Core systems validation
- Character creation
- Combat basics
- Database integrity

**Full Tests** (2-3 minutes) - Run after each phase:
```bash
python tests/run_regression_tests.py --full
```
- All quick tests
- Subclass features
- Progression systems
- Comprehensive combat

**Detailed Tests** (4-5 minutes) - Run before commits:
```bash
python tests/run_regression_tests.py --detailed
```
- Full test suite
- Feature validation
- Edge cases

### Spell-Specific Tests

**Unit Tests** - Per spell handler:
```python
def test_cure_wounds_level_1():
    paladin = create_paladin(level=2, charisma=16)
    damage_character(paladin, 10)
    cast_spell(paladin, 'cure_wounds', slot_level=1)
    assert paladin.current_hp > paladin.max_hp - 10

def test_shield_of_faith_ac_bonus():
    paladin = create_paladin(level=2)
    base_ac = paladin.ac
    cast_spell(paladin, 'shield_of_faith')
    assert paladin.ac == base_ac + 2
```

**Integration Tests** - System interactions:
```python
def test_bless_attack_bonus_in_combat():
    paladin, goblin = setup_combat()
    cast_spell(paladin, 'bless')

    rolls = [make_attack(paladin, goblin) for _ in range(20)]
    # Verify 1d4 bonus variability
    assert max(r['attack_roll'] for r in rolls) - min(r['attack_roll'] for r in rolls) >= 3
```

---

## Risk Mitigation

### Technical Risks

1. **Performance** - Many DB queries per turn
   - Mitigation: Index all foreign keys, cache active effects

2. **Buff Stacking** - Complex rules
   - Mitigation: Clear stacking rules, same-name buffs don't stack

3. **Turn Processing** - Missing effect triggers
   - Mitigation: Centralized turn hooks in combat manager

4. **Concentration Edge Cases** - Multiple interactions
   - Mitigation: Leverage existing ConcentrationSystem

### Integration Risks

1. **Breaking Existing Systems** - Changes to core services
   - Mitigation: Regression tests at EVERY stage

2. **AC Calculation Changes** - Multiple sources of AC bonuses
   - Mitigation: Additive bonus system, test with items + spells

3. **Attack Bonus Complexity** - Items + spells + class features
   - Mitigation: Return breakdown dict, log all sources

---

## Success Criteria

### Phase 0 (Infrastructure) Complete When:
- ✅ Migration runs successfully
- ✅ `active_spell_effects` table exists with indexes
- ✅ `SpellEffectsService` implemented with all core methods
- ✅ Unit tests pass for service methods
- ✅ Regression tests pass (quick)

### Phase 1-9 (Spells) Complete When:
- ✅ Spell handler implemented
- ✅ Spell integrated with combat/AC/attack systems
- ✅ Unit tests pass for spell
- ✅ Integration tests pass
- ✅ Regression tests pass (quick or full)

### Full System Complete When:
- ✅ All 38 paladin spells functional
- ✅ Spell cards auto-generate correctly
- ✅ All buffs/debuffs track properly
- ✅ Concentration system integrated
- ✅ Turn-by-turn effects work
- ✅ Temp HP system functional
- ✅ UI displays all active effects
- ✅ 100% regression tests pass

---

## Next Steps

1. Review this analysis
2. Create migration `023_spell_effects_system.sql`
3. Implement `SpellEffectsService`
4. Run regression tests
5. Implement Phase 1 healing spells
6. Continue through phases with regression testing at each stage

---

**Document Version**: 1.0
**Date**: 2025-10-08
**Author**: Analysis based on TaleKeeper codebase review
