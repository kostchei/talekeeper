# Phase 1: Spell Data Population - Detailed Implementation Plan

## Overview

**Goal**: Populate database with minimum viable D&D 2024 spells for level 1 character creation

**Timeline**: 2 days

**Scope**: Cantrips + Level 1 spells only (level 2-5 come later)

---

## Current Database Analysis

### Existing Infrastructure ✅
- `spells` table exists with correct schema
- `character_spells` table exists for tracking known/prepared spells
- `wizard_spellbook` table exists for wizard spells
- Seed file format established in `database/seeds/spells_basic.sql`

### Existing Spells (15 total)
Currently in database:
- **Cantrips (2)**: Guidance, Mage Hand
- **Level 1 (5)**: Detect Magic, Identify, Comprehend Languages, Cure Wounds, Magic Missile
- **Level 2-6 (8)**: Various utility/ritual spells

### What's Missing
- Most cantrips for all classes
- Essential level 1 combat/utility spells
- Class-specific signature spells

---

## Spell Requirements by Class (Level 1)

### Wizard (Priority: HIGHEST)
**Needs**: 3 cantrips + 6 level-1 spells in spellbook
- **Cantrips Required**: Fire Bolt (combat), Mage Hand (utility), Light (utility)
- **Level 1 Must-Haves**:
  - Combat: Magic Missile ✅, Shield, Mage Armor
  - Utility: Detect Magic ✅, Identify ✅, Find Familiar
  - Total needed for 6-spell selection: ~20 wizard level-1 spells

### Cleric (Priority: HIGH)
**Needs**: 3 cantrips + 4-5 prepared spells
- **Cantrips Required**: Sacred Flame (combat), Guidance (utility), Light (utility)
- **Level 1 Must-Haves**:
  - Healing: Cure Wounds ✅, Healing Word
  - Combat: Guiding Bolt, Inflict Wounds
  - Utility: Bless, Shield of Faith
  - Total needed: ~15 cleric level-1 spells

### Warlock (Priority: HIGH)
**Needs**: 2 cantrips + 2 known spells
- **Cantrips Required**: Eldritch Blast (signature), Mage Hand ✅
- **Level 1 Must-Haves**:
  - Combat: Hex, Hellish Rebuke
  - Utility: Charm Person, Detect Magic ✅
  - Total needed: ~10 warlock level-1 spells

### Paladin (Priority: MEDIUM)
**Needs**: 0 cantrips + 2 prepared spells
- **Level 1 Must-Haves**:
  - Heroism, Searing Smite (recommended in SRD)
  - Cure Wounds ✅, Bless, Shield of Faith, Divine Smite
  - Total needed: ~12 paladin level-1 spells

---

## Minimum Viable Spell List

### Cantrips (20 total)

#### Combat Cantrips (8)
1. Eldritch Blast - Warlock signature (1d10 force, 120 ft)
2. Fire Bolt - Wizard/Sorcerer (1d10 fire, 120 ft)
3. Sacred Flame - Cleric (1d8 radiant, 60 ft, Dex save)
4. Chill Touch - Wizard/Warlock (1d8 necrotic, 120 ft)
5. Ray of Frost - Wizard (1d8 cold, 60 ft, slows)
6. Poison Spray - Wizard/Warlock (1d12 poison, 10 ft, Con save)
7. Shocking Grasp - Wizard (1d8 lightning, touch)
8. Acid Splash - Wizard (1d6 acid, 60 ft, Dex save)

#### Utility Cantrips (12)
9. Mage Hand - Universal ✅
10. Light - Cleric/Wizard (illumination)
11. Guidance - Cleric ✅ (add d4 to check)
12. Prestidigitation - Wizard/Warlock (minor effects)
13. Minor Illusion - Wizard/Warlock (sound/image)
14. Message - Wizard (whisper 120 ft)
15. Mending - Cleric/Wizard (repair objects)
16. Thaumaturgy - Cleric (dramatic effects)
17. Spare the Dying - Cleric (stabilize)
18. Resistance - Cleric (add d4 to save)
19. True Strike - Warlock/Wizard (advantage)
20. Dancing Lights - Wizard (4 lights)

### Level 1 Spells (40 total)

#### Universal/Common (10)
1. Detect Magic ✅ - All classes
2. Cure Wounds ✅ - Cleric/Paladin/Ranger
3. Magic Missile ✅ - Wizard/Sorcerer
4. Shield - Wizard/Sorcerer (reaction, +5 AC)
5. Mage Armor - Wizard/Sorcerer (13+Dex AC)
6. Bless - Cleric/Paladin (add d4 to attacks/saves)
7. Healing Word - Cleric (bonus action heal)
8. Protection from Evil and Good - Multiple classes
9. Comprehend Languages ✅ - Multiple classes
10. Identify ✅ - Wizard

#### Wizard-Specific (15)
11. Find Familiar - Wizard (summon familiar)
12. Burning Hands - Wizard (15ft cone fire)
13. Thunderwave - Wizard (15ft cube thunder)
14. Feather Fall - Wizard (reaction, slow fall)
15. Grease - Wizard (difficult terrain)
16. Sleep - Wizard (put creatures to sleep)
17. Color Spray - Wizard (blind creatures)
18. Disguise Self - Wizard (change appearance)
19. Fog Cloud - Wizard (obscure area)
20. Jump - Wizard (triple jump distance)
21. Longstrider - Wizard (+10 ft speed)
22. Silent Image - Wizard (illusion)
23. Chromatic Orb - Wizard (3d8 elemental)
24. Ice Knife - Wizard (1d10 + 2d6 cold)
25. Ray of Sickness - Wizard (2d8 poison + poisoned)

#### Cleric-Specific (8)
26. Guiding Bolt - Cleric (4d6 radiant + advantage)
27. Inflict Wounds - Cleric (3d10 necrotic melee)
28. Shield of Faith - Cleric (bonus action +2 AC)
29. Sanctuary - Cleric (protect creature)
30. Command - Cleric (one-word command)
31. Bane - Cleric (subtract d4 from attacks/saves)
32. Detect Evil and Good - Cleric
33. Detect Poison and Disease - Cleric

#### Warlock-Specific (5)
34. Hex - Warlock (bonus damage + disadvantage)
35. Hellish Rebuke - Warlock (reaction damage)
36. Charm Person - Warlock
37. Expeditious Retreat - Warlock (bonus action dash)
38. Speak with Animals - Warlock

#### Paladin-Specific (2)
39. Heroism - Paladin (temp HP + immunity to frightened)
40. Searing Smite - Paladin (extra fire damage)

---

## Implementation Steps

### Step 1.1: Create Cantrip Seed File (4 hours)

**File**: `database/seeds/010_spells_cantrips.sql`

**Structure**:
```sql
-- D&D 2024 Core Cantrips
-- Level 0 spells for all spellcasting classes

INSERT OR IGNORE INTO spells (id, name, level, school, casting_time, range_value, components, duration, concentration, ritual, description, higher_levels, source, classes) VALUES

-- COMBAT CANTRIPS
('eldritch_blast', 'Eldritch Blast', 0, 'Evocation', '1 action', '120 feet', 'V, S', 'Instantaneous', 0, 0,
 'A beam of crackling energy streaks toward a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 Force damage.',
 'The spell creates more than one beam when you reach certain levels: two beams at level 5, three beams at level 11, and four beams at level 17. Each beam can target the same creature or different ones. Make a separate attack roll for each beam.',
 'PHB', '["warlock"]'),

('fire_bolt', 'Fire Bolt', 0, 'Evocation', '1 action', '120 feet', 'V, S', 'Instantaneous', 0, 0,
 'You hurl a mote of fire at a creature or an object within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 Fire damage. A flammable object hit by this spell starts burning if it isn''t being worn or carried.',
 'The spell''s damage increases by 1d10 when you reach level 5 (2d10), level 11 (3d10), and level 17 (4d10).',
 'PHB', '["wizard", "sorcerer"]'),

-- ... continue for all 20 cantrips
```

**Data Source**: D&D 2024 SRD lines 3570-3580 (Cleric), 6609-6617 (Warlock), 6974-6990 (Wizard)

**Tasks**:
- [ ] Copy spell names from SRD
- [ ] Look up full descriptions from PHB/SRD
- [ ] Format as SQL INSERT statements
- [ ] Verify school and components
- [ ] Test SQL syntax

### Step 1.2: Create Level 1 Spell Seed File (6 hours)

**File**: `database/seeds/011_spells_level1.sql`

**Structure**:
```sql
-- D&D 2024 Level 1 Spells
-- Essential spells for character creation

INSERT OR IGNORE INTO spells (id, name, level, school, casting_time, range_value, components, duration, concentration, ritual, description, higher_levels, source, classes) VALUES

-- UNIVERSAL SPELLS
('shield', 'Shield', 1, 'Abjuration', '1 reaction', 'Self', 'V, S', 'Until the start of your next turn', 0, 0,
 'An invisible barrier of magical force appears and protects you. Until the start of your next turn, you have a +5 bonus to AC, including against the triggering attack, and you take no damage from Magic Missile.',
 '',
 'PHB', '["wizard", "sorcerer"]'),

-- ... continue for all 40 level-1 spells
```

**Data Source**: SRD lines 3581-3597 (Cleric L1), 4997-5012 (Paladin L1), 6618-6631 (Warlock L1), 6991-7021 (Wizard L1)

**Tasks**:
- [ ] Extract spell names by class
- [ ] Prioritize based on character creation needs
- [ ] Format descriptions from SRD
- [ ] Add damage/healing formulas
- [ ] Include "at higher levels" text
- [ ] Verify class arrays match SRD

### Step 1.3: Run Seed Scripts (30 minutes)

**Commands**:
```bash
# Backup current database
copy talekeeper.db talekeeper_backup_pre_spells.db

# Run cantrip seed
sqlite3 talekeeper.db < database/seeds/010_spells_cantrips.sql

# Run level 1 seed
sqlite3 talekeeper.db < database/seeds/011_spells_level1.sql

# Verify spell counts
sqlite3 talekeeper.db "SELECT level, COUNT(*) FROM spells GROUP BY level"

# Expected output:
# 0|20   (cantrips)
# 1|40   (level 1 spells)
# Total: 60+ spells
```

**Validation Queries**:
```bash
# Check wizard cantrips
sqlite3 talekeeper.db "SELECT name FROM spells WHERE level=0 AND classes LIKE '%wizard%'"

# Check warlock spells
sqlite3 talekeeper.db "SELECT name FROM spells WHERE level=1 AND classes LIKE '%warlock%'"

# Check for duplicates
sqlite3 talekeeper.db "SELECT id, COUNT(*) FROM spells GROUP BY id HAVING COUNT(*) > 1"
```

### Step 1.4: Test Spell Registry Integration (1 hour)

**Test Script**: `test/test_spell_data_phase1.py`

```python
import sqlite3
from services.spell_registry import spell_registry

def test_cantrip_availability():
    """Test that all classes have their essential cantrips"""
    # Wizard
    wizard_cantrips = spell_registry.get_spells_for_class('wizard', max_level=0)
    assert len(wizard_cantrips) >= 15
    assert any(s.name == 'Fire Bolt' for s in wizard_cantrips)

    # Warlock
    warlock_cantrips = spell_registry.get_spells_for_class('warlock', max_level=0)
    assert len(warlock_cantrips) >= 7
    assert any(s.name == 'Eldritch Blast' for s in warlock_cantrips)

    # Cleric
    cleric_cantrips = spell_registry.get_spells_for_class('cleric', max_level=0)
    assert len(cleric_cantrips) >= 7
    assert any(s.name == 'Sacred Flame' for s in cleric_cantrips)

def test_level1_spell_availability():
    """Test that all classes have sufficient level 1 spells"""
    # Wizard needs 20+ for spellbook selection
    wizard_l1 = spell_registry.get_spells_for_class('wizard', min_level=1, max_level=1)
    assert len(wizard_l1) >= 20

    # Cleric needs 15+ for preparation
    cleric_l1 = spell_registry.get_spells_for_class('cleric', min_level=1, max_level=1)
    assert len(cleric_l1) >= 15

    # Warlock needs 10+ for selection
    warlock_l1 = spell_registry.get_spells_for_class('warlock', min_level=1, max_level=1)
    assert len(warlock_l1) >= 10

    # Paladin needs 12+ for preparation
    paladin_l1 = spell_registry.get_spells_for_class('paladin', min_level=1, max_level=1)
    assert len(paladin_l1) >= 12

def test_essential_spells():
    """Test that critical spells exist"""
    essential = [
        'eldritch_blast',  # Warlock signature
        'fire_bolt',        # Wizard combat
        'sacred_flame',     # Cleric combat
        'shield',           # Wizard defense
        'mage_armor',       # Wizard AC
        'hex',              # Warlock signature
        'cure_wounds',      # Healing
        'healing_word',     # Bonus action heal
        'guiding_bolt',     # Cleric damage
    ]

    for spell_id in essential:
        spell = spell_registry.get_spell(spell_id)
        assert spell is not None, f"Missing essential spell: {spell_id}"

if __name__ == '__main__':
    test_cantrip_availability()
    test_level1_spell_availability()
    test_essential_spells()
    print("✅ All Phase 1 spell data tests passed!")
```

**Run Test**:
```bash
cd test && python test_spell_data_phase1.py
```

---

## Spell Data Format Reference

### SQL Insert Template
```sql
INSERT OR IGNORE INTO spells (
    id,                -- snake_case identifier
    name,              -- Display name
    level,             -- 0 = cantrip, 1-9 = spell level
    school,            -- Abjuration, Conjuration, Divination, Enchantment, Evocation, Illusion, Necromancy, Transmutation
    casting_time,      -- '1 action', '1 bonus action', '1 reaction', '1 minute', etc.
    range_value,       -- 'Self', 'Touch', '30 feet', '120 feet', etc.
    components,        -- 'V', 'S', 'M (description)', or combinations
    duration,          -- 'Instantaneous', 'Concentration, up to X', '1 hour', etc.
    concentration,     -- 0 or 1
    ritual,            -- 0 or 1
    description,       -- Full spell description
    higher_levels,     -- Upcast text (empty string if not applicable)
    source,            -- 'PHB', 'XGE', etc.
    classes            -- JSON array: '["wizard", "sorcerer"]'
) VALUES (...);
```

### Conventions
- **IDs**: Use snake_case (e.g., `eldritch_blast`, `cure_wounds`)
- **Names**: Use title case with spaces (e.g., `Eldritch Blast`, `Cure Wounds`)
- **Schools**: Capitalize (e.g., `Evocation`, `Abjuration`)
- **Classes**: Lowercase in JSON array (e.g., `["wizard", "cleric"]`)
- **Concentration**: Use `0` for false, `1` for true
- **Ritual**: Use `0` for false, `1` for true
- **Description**: Single quotes for SQL, double single quotes for apostrophes (`''`)

---

## Work Breakdown

### Day 1 (6-8 hours)
- [x] Research spell requirements (DONE)
- [ ] Create cantrip seed file (4 hours)
  - [ ] Combat cantrips (8)
  - [ ] Utility cantrips (12)
  - [ ] Test SQL syntax
- [ ] Run cantrip seed and validate (30 min)
- [ ] Start level 1 spell seed file (3 hours)
  - [ ] Universal spells (10)
  - [ ] Wizard spells (15)

### Day 2 (6-8 hours)
- [ ] Complete level 1 spell seed file (3 hours)
  - [ ] Cleric spells (8)
  - [ ] Warlock spells (5)
  - [ ] Paladin spells (2)
- [ ] Run level 1 seed and validate (30 min)
- [ ] Write test script (1 hour)
- [ ] Run all tests (30 min)
- [ ] Document completion (1 hour)

---

## Success Criteria

### Phase 1 Complete When:
- [ ] 20+ cantrips in database
- [ ] 40+ level 1 spells in database
- [ ] Wizard has 15+ cantrips, 20+ level-1 spells
- [ ] Cleric has 7+ cantrips, 15+ level-1 spells
- [ ] Warlock has 7+ cantrips, 10+ level-1 spells
- [ ] Paladin has 0 cantrips, 12+ level-1 spells
- [ ] All spells have correct class associations
- [ ] Spell registry can query by class
- [ ] Test script passes all checks
- [ ] Essential spells (Shield, Eldritch Blast, Cure Wounds, etc.) present

---

## Notes

### Why These Spells?
- **Combat**: Each class needs viable attack cantrips and level-1 damage spells
- **Utility**: Essential spells like Mage Armor, Shield, Detect Magic
- **Healing**: Cure Wounds, Healing Word for Cleric/Paladin
- **Signature**: Class-defining spells (Eldritch Blast, Hex, etc.)

### What's NOT Included Yet
- Level 2-5 spells (Phase 1B)
- Domain/Oath/Patron bonus spells (handled in subclass code)
- Uncommon situational spells
- Non-core sourcebook spells

### Existing Spells to Keep
The current 15 spells in `spells_basic.sql` should remain - they're mostly ritual/utility spells that complement this list.

---

## Next Phase Preview

**Phase 2**: Character Creation UI (uses this spell data)
- Spell selection widget
- Cantrip selection UI
- Integration with character creation flow
- Spell saving to database

This Phase 1 data enables Phase 2 to proceed.