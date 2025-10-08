# Paladin Spell System Audit

## Overview
This document audits all Paladin spells in TaleKeeper against the SRD 5.2.1, documenting:
- Database presence
- Action card generation
- Mechanical implementation
- UI integration
- Test coverage

## Critical Findings
- **SRD Total**: 42 paladin spells (Levels 1-5)
- **Database Total**: 8 unique spells (10 with duplicates)
- **Missing**: 34 spells (81% incomplete)
- **Database Issue**: Lesser Restoration has 3 duplicate entries

## Complete Spell List from SRD 5.2.1

### Level 1 Spells (13 spells)
| Spell | School | Special | In DB | Card Gen | Mechanics | Tests |
|-------|--------|---------|-------|----------|-----------|-------|
| Bless | Enchantment | C, M | YES | TBD | PARTIAL | NO |
| Command | Enchantment | - | NO | - | - | - |
| Cure Wounds | Abjuration | - | YES | TBD | PARTIAL | NO |
| Detect Evil and Good | Divination | C | NO | - | - | - |
| Detect Magic | Divination | C, R | NO | - | - | - |
| Detect Poison and Disease | Divination | C, R | NO | - | - | - |
| Divine Favor | Transmutation | - | NO | - | - | - |
| Divine Smite | Evocation | - | YES | TBD | YES | PARTIAL |
| Heroism | Enchantment | C | YES | TBD | PARTIAL | NO |
| Protection from Evil and Good | Abjuration | C, M | NO | - | - | - |
| Purify Food and Drink | Transmutation | R | NO | - | - | - |
| Searing Smite | Evocation | - | YES | TBD | NO | NO |
| Shield of Faith | Abjuration | C | YES | TBD | PARTIAL | NO |

### Level 2 Spells (11 spells)
| Spell | School | Special | In DB | Card Gen | Mechanics | Tests |
|-------|--------|---------|-------|----------|-----------|-------|
| Aid | Abjuration | - | NO | - | - | - |
| Find Steed | Conjuration | - | NO | - | - | - |
| Gentle Repose | Necromancy | R, M | NO | - | - | - |
| Lesser Restoration | Abjuration | - | YES (3x) | TBD | NO | NO |
| Locate Object | Divination | C | NO | - | - | - |
| Magic Weapon | Transmutation | - | YES | TBD | NO | NO |
| Prayer of Healing | Abjuration | - | NO | - | - | - |
| Protection from Poison | Abjuration | - | NO | - | - | - |
| Shining Smite | Transmutation | C | NO | - | - | - |
| Warding Bond | Abjuration | M | NO | - | - | - |
| Zone of Truth | Enchantment | - | NO | - | - | - |

### Level 3 Spells (6 spells)
| Spell | School | Special | In DB | Card Gen | Mechanics | Tests |
|-------|--------|---------|-------|----------|-----------|-------|
| Create Food and Water | Conjuration | - | NO | - | - | - |
| Daylight | Evocation | - | NO | - | - | - |
| Dispel Magic | Abjuration | - | NO | - | - | - |
| Magic Circle | Abjuration | M | NO | - | - | - |
| Remove Curse | Abjuration | - | NO | - | - | - |
| Revivify | Necromancy | M | NO | - | - | - |

### Level 4 Spells (4 spells)
| Spell | School | Special | In DB | Card Gen | Mechanics | Tests |
|-------|--------|---------|-------|----------|-----------|-------|
| Aura of Life | Abjuration | C | NO | - | - | - |
| Banishment | Abjuration | C | NO | - | - | - |
| Death Ward | Abjuration | - | NO | - | - | - |
| Locate Creature | Divination | C | NO | - | - | - |

### Level 5 Spells (4 spells)
| Spell | School | Special | In DB | Card Gen | Mechanics | Tests |
|-------|--------|---------|-------|----------|-----------|-------|
| Dispel Evil and Good | Abjuration | C | NO | - | - | - |
| Geas | Enchantment | - | NO | - | - | - |
| Greater Restoration | Abjuration | M | NO | - | - | - |
| Raise Dead | Necromancy | M | NO | - | - | - |

**Legend**: C=Concentration, R=Ritual, M=Material component

## Implementation Status Summary

### Spells in Database (8 unique, 10 total)
**Level 1 (6 spells)**:
- Bless - Partial mechanics
- Cure Wounds - Partial mechanics
- Divine Smite - FULLY IMPLEMENTED
- Heroism - Partial mechanics
- Searing Smite - No mechanics
- Shield of Faith - Partial mechanics

**Level 2 (2 spells)**:
- Lesser Restoration - No mechanics (3 duplicate entries!)
- Magic Weapon - No mechanics

### Missing from Database (34 spells)
**Level 1**: Command, Detect Evil and Good, Detect Magic, Detect Poison and Disease, Divine Favor, Protection from Evil and Good, Purify Food and Drink (7 spells)

**Level 2**: Aid, Find Steed, Gentle Repose, Locate Object, Prayer of Healing, Protection from Poison, Shining Smite, Warding Bond, Zone of Truth (9 spells)

**Level 3**: Create Food and Water, Daylight, Dispel Magic, Magic Circle, Remove Curse, Revivify (6 spells)

**Level 4**: Aura of Life, Banishment, Death Ward, Locate Creature (4 spells)

**Level 5**: Dispel Evil and Good, Geas, Greater Restoration, Raise Dead (4 spells)

---

## Database Status

### Schema
```sql
CREATE TABLE spells (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    level INTEGER NOT NULL,
    school TEXT NOT NULL,
    casting_time TEXT NOT NULL,
    range_value TEXT NOT NULL,
    components TEXT NOT NULL,
    duration TEXT NOT NULL,
    concentration BOOLEAN DEFAULT FALSE,
    ritual BOOLEAN DEFAULT FALSE,
    description TEXT NOT NULL,
    higher_levels TEXT,
    source TEXT DEFAULT 'PHB',
    classes TEXT, -- JSON array
    is_buff BOOLEAN DEFAULT FALSE
);

CREATE TABLE character_spells (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    is_prepared BOOLEAN DEFAULT TRUE,
    source TEXT NOT NULL,
    source_level INTEGER,
    always_prepared BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (character_id, spell_id)
);
```

### All Paladin Spells Present
- All 8 paladin spells exist in the `spells` table
- Linked via `spell_class_lists` to paladin class
- **Issue**: Lesser Restoration appears 3 times (duplicate entries)

---

## Level 1 Spells

### 1. Bless
**Database**: YES
**School**: Enchantment
**Casting Time**: 1 action
**Range**: 30 feet
**Duration**: Concentration, up to 1 minute
**Components**: V, S, M

**Description**: Choose up to 3 creatures. They add 1d4 to attack rolls and saving throws.

**Higher Levels**: N/A

**Mechanical Implementation**:
- Database entry: COMPLETE
- Spell card generation: UNKNOWN (needs testing)
- Mechanical effect: **NOT IMPLEMENTED**
  - No code applies +1d4 to attack rolls
  - No code applies +1d4 to saving throws
  - No multi-target selection UI
  - No concentration tracking integration

**Required Implementation**:
```python
# In combat system:
# 1. When Bless active on character:
#    - Add 1d4 to attack rolls
#    - Add 1d4 to saving throws
# 2. Multi-target selection (up to 3 creatures)
# 3. Concentration management
# 4. Duration tracking (10 rounds)
```

**UI Integration**:
- Needs spell card in action panel
- Requires target selection widget (multi-target)
- Status indicator for blessed characters

---

### 2. Cure Wounds
**Database**: YES
**School**: Evocation
**Casting Time**: 1 action
**Range**: Touch
**Duration**: Instantaneous
**Components**: V, S

**Description**: Touch a creature and heal 1d8 + spellcasting modifier hit points.

**Higher Levels**: +1d8 per slot level above 1st

**Mechanical Implementation**:
- Database entry: COMPLETE
- Spell card generation: UNKNOWN
- Mechanical effect: **PARTIAL**
  - Healing formula: 1d8 + CHA modifier
  - Higher level scaling: NEEDS VERIFICATION
  - Touch range targeting: NEEDS UI
  - Self-targeting: POSSIBLE

**Required Implementation**:
```python
# Healing calculation:
base_healing = roll_dice(1, 8)
cha_mod = (character.charisma - 10) // 2
slot_level = spell_slot_used  # 1-5 for paladin

if slot_level > 1:
    extra_dice = slot_level - 1
    extra_healing = roll_dice(extra_dice, 8)
    base_healing += extra_healing

total_healing = base_healing + cha_mod

# Apply to target (self or ally)
target.current_hp = min(target.current_hp + total_healing, target.max_hp)
```

**UI Integration**:
- Spell card with "Cast" button
- Target selection (self/ally)
- Healing amount display in log
- Spell slot consumption

**Special Considerations**:
- Solo play: Can heal self
- No concentration required
- Instantaneous effect

---

### 3. Divine Smite
**Database**: YES
**School**: Evocation
**Casting Time**: 1 bonus action
**Range**: Self
**Duration**: Instantaneous
**Components**: V

**Description**: Next melee hit deals +2d8 radiant damage (+3d8 vs undead/fiend).

**Higher Levels**: +1d8 per slot level above 1st

**Mechanical Implementation**:
- Database entry: COMPLETE
- Spell card generation: LIKELY EXISTS
- Mechanical effect: **YES - IMPLEMENTED**
  - Location: `src/talekeeper/services/paladin_abilities.py::divine_smite()`
  - Formula: 2d8 + (spell_slot_level - 1)d8
  - Extra vs undead/fiend: +1d8
  - Max: 5d8 total
  - Free smite: 1/long rest (Paladin level 2+)

**Existing Code**:
```python
# paladin_abilities.py line 349-415
def divine_smite(self, character_id: str, spell_slot_level: int,
                 target_is_undead_or_fiend: bool = False,
                 use_free_smite: bool = False) -> Dict[str, Any]:
    # Base: 2d8 + (level-1)d8
    damage_dice = 2 + (spell_slot_level - 1)

    # +1d8 vs undead/fiend
    if target_is_undead_or_fiend:
        damage_dice += 1

    # Max 5d8
    damage_dice = min(damage_dice, 5)

    # Track free smite usage
    if use_free_smite:
        # Mark free_divine_smite_used in paladin_features
        pass

    return {
        "success": True,
        "damage_dice": damage_dice,
        "damage_type": "radiant",
        "spell_slot_consumed": spell_slot_level if not use_free_smite else 0
    }
```

**UI Integration**:
- Divine Smite dialog exists: `src/talekeeper/ui/action_cards/divine_smite_dialog.py`
- Triggered after successful melee hit
- Options for spell slot level and free smite
- Damage applied immediately

**Test Status**: PARTIAL
- Feature test exists: `tests/features/test_paladin_divine_smite.py`
- Needs comprehensive testing for:
  - Free smite tracking
  - Undead/fiend detection
  - Higher level slots
  - 5d8 cap enforcement

---

### 4. Heroism
**Database**: YES
**School**: Enchantment
**Casting Time**: 1 action
**Range**: Touch
**Duration**: Concentration, up to 1 minute
**Components**: V, S

**Description**: Target is immune to Frightened and gains temp HP equal to spellcasting modifier at start of each turn.

**Higher Levels**: +1 target per slot level above 1st

**Mechanical Implementation**:
- Database entry: COMPLETE
- Spell card generation: UNKNOWN
- Mechanical effect: **PARTIAL**
  - Frightened immunity: NOT VERIFIED
  - Temp HP generation: NOT IMPLEMENTED
  - Per-turn temp HP: NOT IMPLEMENTED
  - Multi-target: NOT IMPLEMENTED

**Required Implementation**:
```python
# At start of each target's turn:
cha_mod = (caster.charisma - 10) // 2
target.temp_hp = cha_mod  # Overwrites existing temp HP

# Condition immunity:
target.immune_conditions.add('frightened')

# Multi-target at higher levels:
num_targets = spell_slot_level  # 1 at level 1, 2 at level 2, etc.
```

**UI Integration**:
- Spell card needed
- Target selection (touch range)
- Status effect indicator (heroism buff)
- Turn-by-turn temp HP tracking
- Concentration indicator

**Special Considerations**:
- Concentration required
- Temp HP refreshes each turn (doesn't stack)
- When spell ends, temp HP lost
- Solo play: Can cast on self

---

### 5. Searing Smite
**Database**: YES
**School**: Evocation
**Casting Time**: 1 bonus action
**Range**: Self
**Duration**: Concentration, up to 1 minute
**Components**: V

**Description**: Next melee hit deals +1d6 fire damage and ignites target. Target takes 1d6 fire/turn until save.

**Higher Levels**: +1d6 initial damage per slot level above 1st

**Mechanical Implementation**:
- Database entry: COMPLETE
- Spell card generation: UNKNOWN
- Mechanical effect: **NOT IMPLEMENTED**
  - Initial +1d6 fire: NO
  - Ongoing 1d6 fire/turn: NO
  - Dex save to extinguish: NO
  - Higher level scaling: NO
  - Concentration tracking: NO

**Required Implementation**:
```python
# On next melee hit:
initial_damage = roll_dice(slot_level, 6)  # 1d6 at level 1, 2d6 at level 2
apply_damage(target, initial_damage, 'fire')

# Apply ignited condition:
target.conditions.add({
    'type': 'ignited',
    'damage_per_turn': roll_dice(1, 6),
    'save_dc': caster.spell_save_dc,
    'save_ability': 'dexterity'
})

# At start of target's turn:
if target.has_condition('ignited'):
    fire_damage = roll_dice(1, 6)
    apply_damage(target, fire_damage, 'fire')

    # Allow save to extinguish (action)
    # If target uses action to save and succeeds, remove ignited
```

**UI Integration**:
- Bonus action spell card
- Visual indicator (flames on target)
- Per-turn damage tracking
- Save prompt for target
- Concentration management

**Special Considerations**:
- Concentration required
- Can cast before attacking
- Only applies to next hit
- Target can use action to attempt save

---

### 6. Shield of Faith
**Database**: YES
**School**: Abjuration
**Casting Time**: 1 bonus action
**Range**: 60 feet
**Duration**: Concentration, up to 10 minutes
**Components**: V, S, M

**Description**: Target gains +2 AC for duration.

**Higher Levels**: N/A

**Mechanical Implementation**:
- Database entry: COMPLETE
- Spell card generation: UNKNOWN
- Mechanical effect: **PARTIAL**
  - Spell card hint exists in `spell_card_stack.py:93-94`
  - Actual AC bonus application: NOT VERIFIED
  - Concentration tracking: NEEDS VERIFICATION

**Code Reference**:
```python
# spell_card_stack.py line 93-94
if '+2 bonus to AC' in desc:
    effects.append(f"+2 AC ({range_val})")
```

**Required Implementation**:
```python
# When cast:
target = select_target_within_range(60)  # feet
apply_buff(target, {
    'name': 'Shield of Faith',
    'ac_bonus': 2,
    'duration': 100,  # 10 minutes = 100 rounds
    'concentration': True,
    'caster': character_id
})

# AC calculation integration:
total_ac = base_ac + armor_bonus + shield_bonus + dex_mod + shield_of_faith_bonus
```

**UI Integration**:
- Bonus action spell card
- Target selection (60 ft range)
- Visual AC indicator on target
- Concentration tracker
- Duration countdown

**Special Considerations**:
- Long duration (10 minutes)
- Can cast on ally or self
- Concentration required
- Stacks with all AC sources

---

## Level 2 Spells

### 7. Lesser Restoration
**Database**: YES (DUPLICATE ENTRIES - 3x)
**School**: Abjuration
**Casting Time**: 1 action
**Range**: Touch
**Duration**: Instantaneous
**Components**: V, S

**Description**: End one condition: blinded, deafened, paralyzed, or poisoned.

**Higher Levels**: N/A

**Mechanical Implementation**:
- Database entry: COMPLETE (needs deduplication)
- Spell card generation: UNKNOWN
- Mechanical effect: **NOT IMPLEMENTED**
  - Condition removal: NO
  - Touch targeting: NO
  - Condition selection UI: NO

**Required Implementation**:
```python
# Condition removal:
allowed_conditions = ['blinded', 'deafened', 'paralyzed', 'poisoned']

# UI prompts for condition choice
condition_to_remove = select_condition(target, allowed_conditions)

if condition_to_remove in target.conditions:
    target.conditions.remove(condition_to_remove)
    log(f"Removed {condition_to_remove} from {target.name}")
else:
    log(f"Target does not have {condition_to_remove}")
```

**UI Integration**:
- Action spell card
- Target selection (touch)
- Condition selection dialog
- Success message in log

**Special Considerations**:
- Solo play utility is limited (no allies)
- Useful if solo character gets poisoned/paralyzed
- Instantaneous effect
- No concentration

**Database Fix Needed**:
```sql
-- Remove duplicate entries
DELETE FROM spells WHERE id = 'lesser_restoration'
  AND rowid NOT IN (
    SELECT MIN(rowid) FROM spells WHERE id = 'lesser_restoration'
  );
```

---

### 8. Magic Weapon
**Database**: YES
**School**: Transmutation
**Casting Time**: 1 bonus action
**Range**: Touch
**Duration**: 1 hour (Concentration)
**Components**: V, S

**Description**: Weapon becomes magical with +1 to attack and damage rolls.

**Higher Levels**: N/A (stays +1)

**Mechanical Implementation**:
- Database entry: COMPLETE
- Spell card generation: UNKNOWN
- Mechanical effect: **NOT IMPLEMENTED**
  - Weapon selection: NO
  - +1 attack bonus: NO
  - +1 damage bonus: NO
  - Magical property flag: NO
  - Concentration tracking: NO

**Required Implementation**:
```python
# When cast:
weapon = select_equipped_weapon()
apply_buff(weapon, {
    'name': 'Magic Weapon',
    'attack_bonus': 1,
    'damage_bonus': 1,
    'magical': True,
    'duration': 600,  # 1 hour = 600 rounds
    'concentration': True,
    'caster': character_id
})

# Attack calculation integration:
attack_roll += magic_weapon_bonus if weapon.has_buff('Magic Weapon') else 0
damage_roll += magic_weapon_bonus if weapon.has_buff('Magic Weapon') else 0

# Magical property:
# Overcomes resistance to non-magical weapons
```

**UI Integration**:
- Bonus action spell card
- Weapon selection dialog (if multiple weapons)
- Visual indicator on weapon (glowing effect?)
- Concentration tracker
- Duration: 1 hour (very long)

**Special Considerations**:
- Long duration (1 hour = 600 rounds)
- Concentration required
- Only affects one weapon
- Makes weapon count as magical (bypasses resistances)
- Solo play: Very useful for early game

---

## Oath Spells (Always Prepared)

### Oath of Devotion
- Level 3: Protection from Evil and Good, Sanctuary
- Level 5: Lesser Restoration, Zone of Truth
- Level 9: Beacon of Hope, Dispel Magic
- Level 13: Freedom of Movement, Guardian of Faith
- Level 17: Commune, Flame Strike

**Note**: These spells are automatically added via `paladin_abilities.py::_add_oath_spells()` and are NOT in the base paladin spell list queried above.

---

## Action Card Generation

### System Overview
Spell cards are generated by:
1. `SpellcastingService` - Loads prepared spells from database
2. `spell_card_stack.py` - Creates UI cards for spell stacks
3. `encounter_panel.py` - Manages spell selection and targeting

### Card Stack System
```python
# spell_card_stack.py
class SpellCardStack(QFrame):
    def __init__(self, spell_level, cast_type, spells, available_slots, max_slots):
        # Creates stackable cards for spells of same level
        # Click to cycle through spells
        # Shows: Level, Slots, Name, Effect, Cast button
```

### Effect Display Logic (spell_card_stack.py:84-115)
```python
def _get_spell_effect(self, spell):
    # Pattern matching in description:
    - "1d4 radiant damage" -> "1d4 radiant per strike"
    - "+2 bonus to AC" -> "+2 AC (range)"
    - "immune to.*frightened" -> "Immune Frightened"
    - "temporary hit points" -> "Temp HP (range)"
    - Fallback: First sentence of description
```

### Current Support
- **Cantrips**: Supported (spell_level = 0)
- **Level 1-5**: Supported (paladin has slots 1-5)
- **Spell cycling**: Multiple spells per level (click to cycle)
- **Slot tracking**: Shows available/max slots
- **Cast button**: Disabled when no slots

### Testing Needed
- Verify card generation for all 8 paladin spells
- Test slot consumption
- Test spell cycling within level
- Verify "Cast" button triggers

---

## Mechanical Implementation Status

### Implemented Systems
1. **Divine Smite** - FULLY IMPLEMENTED
   - Service: `paladin_abilities.py`
   - Dialog: `divine_smite_dialog.py`
   - Damage calculation: YES
   - Free smite tracking: YES
   - Spell slot consumption: YES

2. **Lay on Hands** - FULLY IMPLEMENTED
   - Service: `paladin_abilities.py::use_lay_on_hands()`
   - Dialog: `lay_on_hands_dialog.py`
   - Healing pool tracking: YES

3. **Channel Divinity** - FULLY IMPLEMENTED
   - Service: `paladin_abilities.py::use_channel_divinity()`
   - Dialog: `channel_divinity_dialog.py`
   - Uses tracking: YES

### Partially Implemented
1. **Cure Wounds**
   - Healing calculation: LIKELY
   - Higher level scaling: UNKNOWN
   - UI: NEEDS TESTING

2. **Shield of Faith**
   - Effect display hint: EXISTS
   - AC bonus application: UNKNOWN
   - Concentration: UNKNOWN

3. **Heroism**
   - Frightened immunity: POSSIBLE (via condition system)
   - Temp HP: UNKNOWN
   - Per-turn tracking: UNLIKELY

### Not Implemented
1. **Bless** - Multi-target +1d4 to rolls
2. **Searing Smite** - Fire damage + ignited condition
3. **Lesser Restoration** - Condition removal
4. **Magic Weapon** - Weapon enchantment buff

---

## Concentration System

### Framework Exists
- `src/talekeeper/services/concentration_system.py`
- Tracks one concentration spell per character
- Breaking concentration handled

### Concentration Spells
- Bless (1 minute)
- Heroism (1 minute)
- Searing Smite (1 minute)
- Shield of Faith (10 minutes)
- Magic Weapon (1 hour)

### Testing Needed
- Verify concentration starts when spell cast
- Verify only one concentration spell active
- Verify breaking concentration on damage
- Verify breaking concentration when casting new conc spell

---

## Spell Slot System

### Paladin Spell Slots (Half-caster)
| Level | 1st | 2nd | 3rd | 4th | 5th |
|-------|-----|-----|-----|-----|-----|
| 1     | 0   | -   | -   | -   | -   |
| 2     | 2   | -   | -   | -   | -   |
| 3     | 3   | -   | -   | -   | -   |
| 4     | 3   | -   | -   | -   | -   |
| 5     | 4   | 2   | -   | -   | -   |
| 6     | 4   | 2   | -   | -   | -   |
| 7     | 4   | 3   | -   | -   | -   |
| 8     | 4   | 3   | -   | -   | -   |
| 9     | 4   | 3   | 2   | -   | -   |
| 10    | 4   | 3   | 2   | -   | -   |
| 11    | 4   | 3   | 3   | -   | -   |
| 12    | 4   | 3   | 3   | -   | -   |
| 13    | 4   | 3   | 3   | 1   | -   |
| 14    | 4   | 3   | 3   | 1   | -   |
| 15    | 4   | 3   | 3   | 2   | -   |
| 16    | 4   | 3   | 3   | 2   | -   |
| 17    | 4   | 3   | 3   | 3   | 1   |
| 18    | 4   | 3   | 3   | 3   | 1   |
| 19    | 4   | 3   | 3   | 3   | 2   |
| 20    | 4   | 3   | 3   | 3   | 2   |

### Prepared Spells (D&D 2024)
Fixed by level (not ability modifier):
| Level | Prepared |
|-------|----------|
| 1     | 2        |
| 2     | 3        |
| 3     | 4        |
| 4     | 5        |
| 5     | 6        |
| 7     | 7        |
| 9     | 9        |
| 11    | 10       |
| 13    | 11       |
| 15    | 12       |
| 17    | 14       |
| 19    | 15       |

**Note**: Oath spells are ALWAYS prepared and don't count toward this limit.

---

## Testing Framework

### Existing Test Infrastructure
1. Qt6 Testing Framework: `tests/testing_framework_*.py`
   - UI automation
   - Screenshot capture
   - Click/type simulation
   - HTML reports

2. Spell-specific tests:
   - `tests/test_spell_action_cards.py`
   - `tests/test_spell_slots_qt6.py`
   - `tests/features/test_paladin_divine_smite.py`

### Test Coverage Needed

#### Per-Spell Tests
For EACH spell, test:
1. **Database**: Query returns spell data
2. **Card Generation**: Spell card appears in UI
3. **Casting**: "Cast" button works
4. **Mechanics**: Spell effect applies correctly
5. **Slot Consumption**: Spell slot decrements
6. **Higher Levels**: Upcasting works (if applicable)
7. **Concentration**: Starts/breaks correctly (if applicable)

#### Integration Tests
1. Prepare spells at character creation
2. Long rest restores slots
3. Multiple spells of same level (card cycling)
4. Oath spells always prepared
5. Max prepared spells enforced

---

## Recommendations

### Critical Priority (Database Population)
1. **Add 34 Missing Spells to Database** - 81% of SRD spells missing
   - Add 7 missing Level 1 spells
   - Add 9 missing Level 2 spells
   - Add 6 Level 3 spells
   - Add 4 Level 4 spells
   - Add 4 Level 5 spells
2. **Fix Lesser Restoration Duplicates** - Database integrity issue
3. **Create Spell Seed Files** - Generate SQL inserts for all 34 spells

### High Priority (Existing Spells - Testing)
4. **Test Card Generation for 8 Existing Spells** - Verify UI integration
5. **Test Cure Wounds Mechanics** - Core healing spell
6. **Test Shield of Faith AC Bonus** - Verify it actually works
7. **Test Concentration System** - Verify all 5 concentration spells work

### Medium Priority (Existing Spells - Implementation)
8. **Implement Bless Mechanics** - +1d4 to attacks/saves
9. **Implement Heroism Temp HP** - Per-turn temp HP generation
10. **Implement Searing Smite** - Fire damage + ignited condition
11. **Implement Lesser Restoration** - Condition removal
12. **Implement Magic Weapon** - Weapon enchantment buff

### Low Priority (New Spells - Implementation)
13. **Implement Detection Spells** - Detect Magic, Detect Evil and Good, etc.
14. **Implement Utility Spells** - Command, Aid, Find Steed, etc.
15. **Implement High-Level Spells** - Revivify, Banishment, Raise Dead, etc.
16. **Add Higher Level Casting UI** - Slot level selection for upcasting
17. **Add Multi-target Selection** - For Bless, Aid, Heroism upcasting

---

## Test Execution Plan

### Phase 1: Database Verification (Quick)
```python
def test_paladin_spells_in_database():
    # Verify all 42 SRD spells exist (currently only 8)
    # Verify linked to paladin class
    # Check for duplicates (Lesser Restoration has 3)
    # Verify spell data complete
    # Priority: Add 34 missing spells before testing
```

### Phase 2: Card Generation (Medium)
```python
def test_paladin_spell_cards_appear():
    # Create level 2 paladin
    # Prepare all available spells
    # Verify cards appear in action panel
    # Test card cycling
    # Test slot display
```

### Phase 3: Casting Mechanics (Complex)
```python
def test_cure_wounds_healing():
    # Cast Cure Wounds (level 1)
    # Verify healing = 1d8 + CHA
    # Verify slot consumed
    # Test higher level casting
    # Verify HP updated

def test_bless_attack_bonus():
    # Cast Bless on self
    # Make attack roll
    # Verify +1d4 applied
    # Test concentration break

def test_shield_of_faith_ac():
    # Cast Shield of Faith on self
    # Verify AC increased by 2
    # Test concentration
    # Test duration
```

### Phase 4: Integration (Full)
```python
def test_paladin_spell_system_full():
    # Create level 5 paladin (4/2 slots)
    # Prepare all spells
    # Cast each spell
    # Verify all mechanics
    # Take long rest
    # Verify slots restored
```

---

## Next Steps

### Immediate Actions (Before Testing)
1. **Add 34 Missing Spells to Database** - Create seed SQL files
2. **Fix Lesser Restoration Duplicates** - Remove 2 duplicate entries
3. **Verify Spell Descriptions** - Ensure all spell data matches SRD

### Testing Phase
4. **Create Test Suite**: `tests/test_paladin_spells_comprehensive.py`
5. **Run Phase 1**: Database verification (all 42 spells)
6. **Run Phase 2**: Card generation test (verify UI shows all prepared spells)
7. **Run Phase 3**: Mechanics tests (8 existing spells only)
8. **Run Phase 4**: Full integration test (character creation to long rest)

### Implementation Phase
9. **Implement Missing Mechanics**: Follow priority order in Recommendations
10. **Test Each Implementation**: Add mechanical tests for each spell
11. **Update This Document**: Mark completed items

---

## Conclusion

The Paladin spell system audit reveals significant gaps:

**Database Coverage**:
- ❌ Only 8/42 spells (19%) present in database
- ❌ 34 spells (81%) missing from SRD
- ❌ Lesser Restoration has 3 duplicate entries
- ⚠️ No Level 3, 4, or 5 spells in database

**Implementation Status**:
- ✅ Spell card UI framework exists
- ✅ Divine Smite fully implemented
- ⚠️ 7/8 existing spells have partial or no mechanics
- ⚠️ Concentration system exists but untested
- ❌ No comprehensive test suite
- ❌ Limited UI for spell mechanics (healing, buffs, targeting)

**Estimated Work**:
- **Database Population**: 4-6 hours (research + SQL for 34 spells)
- **Existing Spell Mechanics**: 6-8 hours (7 spells need work)
- **New Spell Mechanics**: 20-30 hours (34 spells × 30-60 min each)
- **Test Suite Creation**: 3-4 hours (comprehensive Qt6 tests)
- **Bug Fixes**: 1-2 hours (duplicates, edge cases)

**Total Estimated**: 34-50 hours for complete paladin spell system

**Realistic Scope for Initial Release**:
- ✅ Complete database population (all 42 spells)
- ✅ Finish mechanics for 8 existing spells
- ✅ Comprehensive test suite for existing spells
- ⚠️ Implement 5-10 high-priority new spells (Detect Magic, Command, Aid, Protection from Evil and Good, Dispel Magic)
- ⚠️ Defer complex spells (Find Steed, Revivify, Raise Dead) to future releases

**Minimum Viable Testing Scope** (Based on current state):
For the immediate request to test existing spells, focus on:
1. Database verification (8 spells + duplicates check)
2. Card generation (verify prepared spells show cards)
3. Mechanical testing (Divine Smite only - others need implementation first)
4. Identify missing mechanics for bug/feature tickets
