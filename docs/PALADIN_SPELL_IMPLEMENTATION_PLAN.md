# Paladin Spell Mechanical Implementation Plan

## Executive Summary

This plan outlines the mechanical implementation of all 8 Paladin spells currently in the TaleKeeper database. The implementation follows a phased approach, starting with critical infrastructure and moving through spells by complexity and impact.

**Timeline**: 2-3 development sessions (~6-8 hours total)
**Testing**: Qt6 framework with automated UI validation

---

## Current System Analysis

### ✅ Existing Infrastructure
1. **Database Schema** - Complete
   - `spells` table with all spell data
   - `character_spells` for prepared spells
   - `character_spell_slots` for slot tracking
   - `spell_class_lists` for class associations

2. **Services Available**
   - `SpellcastingService` - Slot management, spell initialization
   - `ConcentrationSystem` - Concentration tracking, saves
   - `PaladinAbilitiesService` - Divine Smite (complete)
   - `spell_registry` - Spell data access

3. **UI Components**
   - `SpellCardStack` - Displays spell cards
   - Action panel integration
   - Spell preparation dialog
   - Divine Smite dialog (working example)

### ❌ Missing Infrastructure
1. **Spell Effect System** - No centralized effect application
2. **Active Buff Tracking** - No persistent buff storage
3. **Multi-target Selection** - No UI for selecting multiple targets
4. **Temporary HP System** - No temp HP tracking
5. **Condition Application** - Limited condition system integration

---

## Architecture Design

### New System: Spell Effects Service

Create `src/talekeeper/services/spell_effects_service.py`:

```python
class SpellEffectsService:
    """
    Central service for applying spell effects.
    Handles healing, damage, buffs, debuffs, conditions.
    """

    def apply_healing(self, target_id, amount, source_spell_id)
    def apply_damage(self, target_id, damage_dice, damage_type, source_spell_id)
    def apply_buff(self, target_id, buff_data, duration_rounds)
    def apply_condition(self, target_id, condition_name, duration_rounds)
    def apply_temp_hp(self, target_id, amount, source_spell_id)
    def remove_condition(self, target_id, condition_name)
```

### New Table: Active Spell Effects

```sql
CREATE TABLE active_spell_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_name TEXT NOT NULL,
    effect_type TEXT NOT NULL, -- 'ac_buff', 'temp_hp', 'attack_buff', etc.
    effect_value TEXT, -- JSON data for effect
    duration_rounds INTEGER,
    rounds_remaining INTEGER,
    concentration BOOLEAN DEFAULT FALSE,
    caster_id TEXT, -- Who cast the spell
    started_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);
```

### Integration Points

1. **Combat Manager** - Apply effects at start of turn
2. **Action Panel** - Trigger spell casting
3. **Encounter Panel** - Target selection
4. **Character Sheet** - Display active buffs
5. **Log Panel** - Spell cast/effect messages

---

## Implementation Phases

### Phase 0: Infrastructure (2 hours)

**Goal**: Build the spell effects foundation

#### 0.1 Create Spell Effects Service
**File**: `src/talekeeper/services/spell_effects_service.py`
**Tasks**:
- Create `SpellEffectsService` class
- Implement `apply_healing()` method
- Implement `apply_damage()` method
- Implement `apply_buff()` method
- Implement `apply_temp_hp()` method
- Implement `remove_buff()` method

#### 0.2 Create Active Effects Table
**File**: `database/migrations/015_active_spell_effects.sql`
**Tasks**:
- Create `active_spell_effects` table
- Add indexes for performance
- Add cleanup triggers

#### 0.3 Integrate with Combat System
**File**: `src/talekeeper/core/combat_manager.py`
**Tasks**:
- Add `process_active_effects()` at turn start
- Add `decrement_effect_durations()` at turn end
- Add `remove_expired_effects()` cleanup

**Testing**:
- Unit test for each effect type
- Integration test with combat round

---

### Phase 1: Healing Spells (1 hour)

**Priority**: HIGH - Core mechanic
**Spells**: Cure Wounds

#### 1.1 Cure Wounds
**Complexity**: LOW
**Mechanical Effect**: Heal 1d8 + CHA modifier (+1d8 per level above 1st)

**Implementation**:

**File**: `src/talekeeper/services/spell_effects_service.py`
```python
def cast_cure_wounds(self, caster_id: str, target_id: str, slot_level: int) -> Dict[str, Any]:
    """Cast Cure Wounds spell."""
    # Get caster's Charisma modifier
    cha_mod = self._get_ability_modifier(caster_id, 'charisma')

    # Calculate healing: 1d8 base + 1d8 per level above 1st
    base_dice = 1
    extra_dice = slot_level - 1
    total_dice = base_dice + extra_dice

    # Roll healing
    healing = self._roll_dice(total_dice, 8) + cha_mod

    # Apply healing
    result = self.apply_healing(target_id, healing, 'cure_wounds')

    return {
        'success': True,
        'healing_rolled': healing,
        'target_id': target_id,
        'slot_level': slot_level
    }
```

**UI Integration**:
- Add spell card to action panel (auto-generated)
- Self-targeting by default (solo play)
- Show healing amount in log
- Consume spell slot

**Testing**:
- Test level 1 slot: 1d8 + CHA
- Test level 2 slot: 2d8 + CHA
- Test level 5 slot: 5d8 + CHA
- Test slot consumption
- Test HP cap (max HP)

---

### Phase 2: Buff Spells (2 hours)

**Priority**: MEDIUM - Common combat buffs
**Spells**: Shield of Faith, Heroism, Bless

#### 2.1 Shield of Faith
**Complexity**: LOW
**Mechanical Effect**: +2 AC, Concentration, 10 minutes

**Implementation**:

**File**: `src/talekeeper/services/spell_effects_service.py`
```python
def cast_shield_of_faith(self, caster_id: str, target_id: str, slot_level: int) -> Dict[str, Any]:
    """Cast Shield of Faith spell."""
    # Start concentration
    self.concentration_system.start_concentration(
        caster_id, 'shield_of_faith', slot_level, duration_rounds=100
    )

    # Apply AC buff
    buff_data = {
        'type': 'ac_bonus',
        'value': 2,
        'source': 'shield_of_faith'
    }

    self.apply_buff(target_id, buff_data, duration_rounds=100)

    return {
        'success': True,
        'target_id': target_id,
        'ac_bonus': 2
    }
```

**AC Calculation Integration**:
**File**: `src/talekeeper/services/character_resources.py`
```python
def calculate_ac(self, character_id: str) -> int:
    # Existing AC calculation
    total_ac = base_ac + armor + shield + dex_mod

    # Add spell buffs
    active_buffs = self._get_active_ac_buffs(character_id)
    for buff in active_buffs:
        if buff['type'] == 'ac_bonus':
            total_ac += buff['value']

    return total_ac
```

**Testing**:
- Verify AC increases by 2
- Test concentration start
- Test concentration break (damage)
- Test 100 round duration
- Test self-targeting

---

#### 2.2 Heroism
**Complexity**: MEDIUM
**Mechanical Effect**: Immune to Frightened, Temp HP = CHA mod per turn, Concentration, 1 minute

**Implementation**:

**File**: `src/talekeeper/services/spell_effects_service.py`
```python
def cast_heroism(self, caster_id: str, target_id: str, slot_level: int) -> Dict[str, Any]:
    """Cast Heroism spell."""
    # Get CHA modifier
    cha_mod = self._get_ability_modifier(caster_id, 'charisma')

    # Start concentration
    self.concentration_system.start_concentration(
        caster_id, 'heroism', slot_level, duration_rounds=10
    )

    # Apply Frightened immunity
    buff_data = {
        'type': 'condition_immunity',
        'value': 'frightened',
        'source': 'heroism',
        'temp_hp_per_turn': cha_mod
    }

    self.apply_buff(target_id, buff_data, duration_rounds=10)

    # Apply initial temp HP
    self.apply_temp_hp(target_id, cha_mod, 'heroism')

    return {
        'success': True,
        'target_id': target_id,
        'temp_hp': cha_mod
    }
```

**Turn Start Integration**:
**File**: `src/talekeeper/core/combat_manager.py`
```python
def process_turn_start_effects(self, character_id: str):
    # Check for Heroism buff
    heroism_buff = self._get_active_buff(character_id, 'heroism')
    if heroism_buff:
        temp_hp = heroism_buff['temp_hp_per_turn']
        self.spell_effects.apply_temp_hp(character_id, temp_hp, 'heroism')
```

**Testing**:
- Verify Frightened immunity
- Test temp HP granted each turn
- Test temp HP replacement (not stacking)
- Test concentration
- Test multi-target at higher levels (future)

---

#### 2.3 Bless
**Complexity**: MEDIUM-HIGH
**Mechanical Effect**: +1d4 to attack rolls and saves, 3 targets, Concentration, 1 minute

**Implementation**:

**File**: `src/talekeeper/services/spell_effects_service.py`
```python
def cast_bless(self, caster_id: str, target_ids: List[str], slot_level: int) -> Dict[str, Any]:
    """Cast Bless spell (up to 3 targets in solo play = self only)."""
    # Start concentration
    self.concentration_system.start_concentration(
        caster_id, 'bless', slot_level, duration_rounds=10
    )

    # Apply buff to each target (solo play: just self)
    buff_data = {
        'type': 'attack_and_save_bonus',
        'value': '1d4',
        'source': 'bless'
    }

    for target_id in target_ids[:3]:  # Max 3 targets
        self.apply_buff(target_id, buff_data, duration_rounds=10)

    return {
        'success': True,
        'targets': target_ids[:3],
        'bonus': '1d4'
    }
```

**Attack Roll Integration**:
**File**: `src/talekeeper/services/weapon_attack_service.py`
```python
def calculate_attack_roll(self, character_id: str, weapon: Dict) -> int:
    # Existing calculation
    attack_roll = d20 + ability_mod + proficiency + weapon_bonus

    # Check for Bless buff
    bless_buff = self._get_active_buff(character_id, 'bless')
    if bless_buff:
        bless_bonus = self._roll_dice(1, 4)
        attack_roll += bless_bonus
        self._log(f"[BLESS] +{bless_bonus} to attack roll")

    return attack_roll
```

**Save Roll Integration**:
**File**: `src/talekeeper/services/concentration_system.py` and saving throw locations
```python
def make_saving_throw(self, character_id: str, save_type: str, dc: int) -> bool:
    # Existing save calculation
    save_roll = d20 + ability_mod + proficiency

    # Check for Bless buff
    bless_buff = self._get_active_buff(character_id, 'bless')
    if bless_buff:
        bless_bonus = self._roll_dice(1, 4)
        save_roll += bless_bonus
        self._log(f"[BLESS] +{bless_bonus} to save")

    return save_roll >= dc
```

**Testing**:
- Verify +1d4 to attack rolls
- Verify +1d4 to saving throws
- Test concentration
- Test 10 round duration
- Test self-targeting (solo play)

---

### Phase 3: Smite Spells (1.5 hours)

**Priority**: MEDIUM - Popular paladin mechanic
**Spells**: Searing Smite

**Note**: Divine Smite already implemented as class feature

#### 3.1 Searing Smite
**Complexity**: HIGH
**Mechanical Effect**: Next hit +1d6 fire (+1d6 per level), ignited (1d6/turn), Dex save to end, Concentration, 1 minute

**Implementation**:

**File**: `src/talekeeper/services/spell_effects_service.py`
```python
def cast_searing_smite(self, caster_id: str, slot_level: int) -> Dict[str, Any]:
    """Cast Searing Smite spell."""
    # Start concentration
    self.concentration_system.start_concentration(
        caster_id, 'searing_smite', slot_level, duration_rounds=10
    )

    # Apply "next hit" buff
    buff_data = {
        'type': 'next_hit_bonus',
        'damage_dice': slot_level,
        'damage_die_type': 6,
        'damage_type': 'fire',
        'source': 'searing_smite',
        'ongoing_damage': {'dice': 1, 'die_type': 6, 'type': 'fire'},
        'save_dc': self._get_spell_save_dc(caster_id),
        'save_ability': 'dexterity'
    }

    self.apply_buff(caster_id, buff_data, duration_rounds=10)

    return {
        'success': True,
        'ready': True,
        'damage_on_hit': f"{slot_level}d6 fire"
    }
```

**Attack Integration**:
**File**: `src/talekeeper/services/weapon_attack_service.py`
```python
def apply_on_hit_effects(self, attacker_id: str, target_id: str, hit_successful: bool):
    if not hit_successful:
        return

    # Check for Searing Smite buff
    smite_buff = self._get_active_buff(attacker_id, 'searing_smite')
    if smite_buff:
        # Apply initial fire damage
        fire_damage = self._roll_dice(smite_buff['damage_dice'], 6)
        self.spell_effects.apply_damage(target_id, fire_damage, 'fire', 'searing_smite')

        # Remove "next hit" buff
        self._remove_buff(attacker_id, 'searing_smite')

        # Apply ignited condition
        ignited_data = {
            'type': 'ignited',
            'damage_per_turn': {'dice': 1, 'die_type': 6},
            'save_dc': smite_buff['save_dc'],
            'save_ability': 'dexterity'
        }
        self.spell_effects.apply_condition(target_id, ignited_data, duration_rounds=10)

        self._log(f"[SEARING SMITE] {target_id} ignited! {fire_damage} fire damage")
```

**Turn Start - Ignited Damage**:
**File**: `src/talekeeper/core/combat_manager.py`
```python
def process_turn_start_effects(self, character_id: str):
    # Check for ignited condition
    ignited = self._get_active_condition(character_id, 'ignited')
    if ignited:
        # Apply fire damage
        fire_damage = self._roll_dice(1, 6)
        self.spell_effects.apply_damage(character_id, fire_damage, 'fire', 'ignited')

        # Allow action to make save
        self._log(f"[IGNITED] {character_id} takes {fire_damage} fire damage. Use action to save DC {ignited['save_dc']}")
```

**Testing**:
- Verify bonus action cast
- Test initial damage on hit
- Test ongoing fire damage per turn
- Test Dex save to extinguish
- Test higher level slots
- Test concentration break

---

### Phase 4: Utility Spells (1 hour)

**Priority**: LOW-MEDIUM - Niche utility
**Spells**: Lesser Restoration, Magic Weapon

#### 4.1 Lesser Restoration
**Complexity**: LOW
**Mechanical Effect**: Remove one condition (blinded, deafened, paralyzed, poisoned)

**Implementation**:

**File**: `src/talekeeper/services/spell_effects_service.py`
```python
def cast_lesser_restoration(self, caster_id: str, target_id: str,
                           condition_to_remove: str) -> Dict[str, Any]:
    """Cast Lesser Restoration spell."""
    allowed_conditions = ['blinded', 'deafened', 'paralyzed', 'poisoned']

    if condition_to_remove not in allowed_conditions:
        return {'success': False, 'reason': 'Invalid condition'}

    # Remove condition
    success = self.remove_condition(target_id, condition_to_remove)

    if success:
        self._log(f"[LESSER RESTORATION] Removed {condition_to_remove} from {target_id}")

    return {
        'success': success,
        'condition_removed': condition_to_remove,
        'target_id': target_id
    }
```

**UI**: Condition selection dialog (only if target has applicable condition)

**Testing**:
- Test removing each condition type
- Test when condition not present
- Test self-targeting

---

#### 4.2 Magic Weapon
**Complexity**: MEDIUM
**Mechanical Effect**: +1 to attack and damage, weapon becomes magical, Concentration, 1 hour

**Implementation**:

**File**: `src/talekeeper/services/spell_effects_service.py`
```python
def cast_magic_weapon(self, caster_id: str, weapon_id: str, slot_level: int) -> Dict[str, Any]:
    """Cast Magic Weapon spell."""
    # Start concentration
    self.concentration_system.start_concentration(
        caster_id, 'magic_weapon', slot_level, duration_rounds=600  # 1 hour
    )

    # Apply weapon buff
    buff_data = {
        'type': 'weapon_enchantment',
        'attack_bonus': 1,
        'damage_bonus': 1,
        'magical': True,
        'source': 'magic_weapon',
        'weapon_id': weapon_id
    }

    self.apply_buff(caster_id, buff_data, duration_rounds=600)

    return {
        'success': True,
        'weapon_id': weapon_id,
        'bonus': '+1'
    }
```

**Attack Calculation Integration**:
**File**: `src/talekeeper/services/weapon_attack_service.py`
```python
def calculate_attack_bonus(self, character_id: str, weapon: Dict) -> int:
    # Existing calculation
    bonus = ability_mod + proficiency + weapon_enchantment

    # Check for Magic Weapon buff
    magic_weapon_buff = self._get_weapon_buff(character_id, weapon['id'], 'magic_weapon')
    if magic_weapon_buff:
        bonus += magic_weapon_buff['attack_bonus']

    return bonus

def calculate_damage(self, character_id: str, weapon: Dict) -> int:
    # Existing calculation
    damage = weapon_dice + ability_mod + weapon_enchantment

    # Check for Magic Weapon buff
    magic_weapon_buff = self._get_weapon_buff(character_id, weapon['id'], 'magic_weapon')
    if magic_weapon_buff:
        damage += magic_weapon_buff['damage_bonus']

    return damage
```

**Testing**:
- Verify +1 to attack rolls
- Verify +1 to damage rolls
- Test weapon becomes magical (bypasses resistance)
- Test concentration
- Test 1 hour duration (600 rounds)

---

## Database Fixes

### Fix Lesser Restoration Duplicates

**File**: `scripts/database_tools/fix_spell_duplicates.py`
```python
import sqlite3

def fix_lesser_restoration_duplicates():
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    # Find duplicates
    cursor.execute("""
        SELECT id, rowid FROM spells
        WHERE id = 'lesser_restoration'
        ORDER BY rowid
    """)

    rows = cursor.fetchall()
    print(f"Found {len(rows)} entries for lesser_restoration")

    if len(rows) > 1:
        # Keep first, delete others
        keep_rowid = rows[0][1]
        delete_rowids = [r[1] for r in rows[1:]]

        for rowid in delete_rowids:
            cursor.execute("DELETE FROM spells WHERE rowid = ?", (rowid,))
            print(f"Deleted duplicate rowid {rowid}")

    conn.commit()
    conn.close()
    print("Fixed Lesser Restoration duplicates")

if __name__ == '__main__':
    fix_lesser_restoration_duplicates()
```

---

## Testing Strategy

### Unit Tests
**File**: `tests/unit/test_spell_effects_service.py`
- Test each spell effect method
- Test healing calculations
- Test buff application
- Test duration tracking

### Integration Tests
**File**: `tests/integration/test_paladin_spells.py`
- Test each spell end-to-end
- Test spell slot consumption
- Test concentration mechanics
- Test buff stacking rules

### Qt6 UI Tests
**File**: `tests/test_paladin_spells_qt6.py`
```python
class PaladinSpellTester(QtTestFramework):
    def test_cure_wounds_heals_self(self):
        """Test Cure Wounds heals the paladin."""
        # Create level 2 paladin with 2 spell slots
        paladin = self.create_character('paladin', level=2, charisma=16)

        # Damage paladin
        self.apply_damage(paladin, 10)

        # Open spell card
        cure_wounds_card = self.find_spell_card('Cure Wounds')
        self.assertIsNotNone(cure_wounds_card)

        # Cast spell
        self.click_button(cure_wounds_card, 'Cast')

        # Verify healing
        self.assertGreater(paladin.current_hp, paladin.max_hp - 10)

        # Verify slot consumed
        self.assertEqual(paladin.spell_slots[1], 1)  # 2 -> 1

    def test_shield_of_faith_increases_ac(self):
        """Test Shield of Faith increases AC by 2."""
        paladin = self.create_character('paladin', level=2)
        base_ac = paladin.armor_class

        # Cast Shield of Faith
        spell_card = self.find_spell_card('Shield of Faith')
        self.click_button(spell_card, 'Cast')

        # Verify AC increased
        self.assertEqual(paladin.armor_class, base_ac + 2)

        # Verify concentration
        self.assertTrue(paladin.is_concentrating)
        self.assertEqual(paladin.concentration_spell, 'shield_of_faith')
```

---

## Implementation Order

### Session 1 (2-3 hours): Foundation
1. ✅ Create `spell_effects_service.py`
2. ✅ Create migration `015_active_spell_effects.sql`
3. ✅ Implement `apply_healing()`
4. ✅ Implement `apply_buff()`
5. ✅ Implement Cure Wounds
6. ✅ Test Cure Wounds end-to-end

### Session 2 (2-3 hours): Buffs
1. ✅ Implement Shield of Faith
2. ✅ Integrate AC calculation
3. ✅ Implement Heroism
4. ✅ Implement temp HP system
5. ✅ Implement Bless
6. ✅ Integrate attack roll bonuses
7. ✅ Test all buffs

### Session 3 (2-3 hours): Advanced
1. ✅ Implement Searing Smite
2. ✅ Implement ignited condition
3. ✅ Implement Lesser Restoration
4. ✅ Implement Magic Weapon
5. ✅ Full integration testing
6. ✅ Fix database duplicates

---

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Cure Wounds heals correctly
- ✅ Shield of Faith increases AC
- ✅ Spell slots consumed properly
- ✅ Concentration tracked
- ✅ All spells have action cards

### Full Implementation
- ✅ All 8 spells mechanically functional
- ✅ Higher level casting works
- ✅ Concentration breaks on damage
- ✅ Buffs visible in UI
- ✅ Turn-by-turn effects work
- ✅ Comprehensive test coverage

---

## Risk Mitigation

### Technical Risks
1. **Buff Stacking**: Define clear rules (most don't stack)
2. **Performance**: Index `active_spell_effects` properly
3. **UI Complexity**: Start with self-targeting only
4. **Save System**: Ensure buffs persist across sessions

### Scope Risks
1. **Multi-targeting**: Defer to Phase 2 (post-MVP)
2. **Oath Spells**: Separate implementation after base spells
3. **Advanced UI**: Start with simple dialogs, enhance later

---

## Future Enhancements

### Post-MVP Features
1. Multi-target spell selection UI
2. Visual buff indicators on character sheet
3. Spell effect animations
4. Oath spell implementations (10+ additional spells)
5. Upcasting UI improvements
6. Buff tooltip system

---

## File Structure

```
src/talekeeper/services/
├── spell_effects_service.py          # NEW - Core spell effects
├── spellcasting_service.py           # EXISTS - Slot management
├── concentration_system.py           # EXISTS - Concentration tracking
├── paladin_abilities.py              # EXISTS - Divine Smite, Lay on Hands

database/migrations/
├── 015_active_spell_effects.sql      # NEW - Active effects table
├── 016_fix_spell_duplicates.sql      # NEW - Clean duplicates

tests/
├── unit/test_spell_effects_service.py      # NEW
├── integration/test_paladin_spells.py      # NEW
├── test_paladin_spells_qt6.py             # NEW
```

---

## Estimated Effort

| Phase | Hours | Priority |
|-------|-------|----------|
| Phase 0: Infrastructure | 2.0 | CRITICAL |
| Phase 1: Cure Wounds | 1.0 | HIGH |
| Phase 2: Buff Spells | 2.0 | MEDIUM |
| Phase 3: Searing Smite | 1.5 | MEDIUM |
| Phase 4: Utility Spells | 1.0 | LOW |
| Testing & Bug Fixes | 1.5 | HIGH |
| **TOTAL** | **9.0** | - |

**Realistic Timeline**: 3 development sessions over 1-2 weeks

---

## Conclusion

This plan provides a clear roadmap to implement all Paladin spells mechanically. The phased approach ensures:
- ✅ Critical infrastructure first
- ✅ High-value spells prioritized
- ✅ Incremental testing and validation
- ✅ Manageable scope per session
- ✅ Clear success criteria

**Next Step**: Begin Phase 0 - Create `spell_effects_service.py`
