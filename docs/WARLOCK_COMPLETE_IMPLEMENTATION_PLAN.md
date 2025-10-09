# Complete Warlock Implementation Plan
**Pact Magic, Invocations, Patrons & Spells - Database, Mechanics, UI, Testing**
**Created**: 2025-10-08
**Status**: Planning Phase

## Executive Summary

This document provides a comprehensive plan to implement the **Warlock class** with full D&D 2024 mechanics including Pact Magic, Eldritch Invocations, Otherworldly Patrons (starting with Fiend), and complete spell integration.

**Scope**: Warlock levels 1-20, Fiend Patron subclass, 22 Eldritch Invocations, Pact Magic system
**Estimated Time**: 45-55 hours over 5-7 weeks
**Complexity**: HIGH - Unique spell slot mechanics, invocation system, patron features
**Status**: Foundation exists (DB migration + service stub), needs full implementation

---

## Table of Contents

1. [Current State Assessment](#current-state-assessment)
2. [Warlock Unique Mechanics](#warlock-unique-mechanics)
3. [Database Schema](#database-schema)
4. [Service Architecture](#service-architecture)
5. [Implementation Phases](#implementation-phases)
6. [Spell Integration](#spell-integration)
7. [Eldritch Invocations](#eldritch-invocations)
8. [Fiend Patron Features](#fiend-patron-features)
9. [UI Integration](#ui-integration)
10. [Testing Strategy](#testing-strategy)
11. [Success Criteria](#success-criteria)

---

## Current State Assessment

### Existing Infrastructure ✅
- ✅ Database migration `015_warlock_class.sql` exists
- ✅ `warlock_features` table created
- ✅ `warlock_invocations` table created
- ✅ `invocations` reference table with 22 invocations
- ✅ Warlock class entry in `classes` table
- ✅ Warlock subclasses (Fiend, Archfey, Great Old One) in `subclasses` table
- ✅ Service stub `warlock_service.py` exists
- ✅ Test file `test_warlock_fiend.py` exists

### What Needs Implementation ❌
- ❌ Pact Magic spell slot system (different from standard spellcasting)
- ❌ Eldritch Invocations mechanics (22 invocations)
- ❌ Pact Boons (Blade, Chain, Tome)
- ❌ Mystic Arcanum (levels 6-9 spells)
- ❌ Magical Cunning (short rest slot recovery)
- ❌ Patron features (Fiend Patron levels 3, 6, 10, 14)
- ❌ Warlock spell list integration (38 spells levels 0-5, plus 6-9 via Mystic Arcanum)
- ❌ Integration with combat system
- ❌ UI components (spell slots display, invocation selection, pact boon UI)
- ❌ Complete testing suite

---

## Warlock Unique Mechanics

### 1. Pact Magic vs Spellcasting

**Key Difference**: Warlocks don't use the standard spellcasting system.

| Feature | Standard Spellcasting (Paladin) | Pact Magic (Warlock) |
|---------|--------------------------------|----------------------|
| **Slot Levels** | Multiple levels (1st-5th) | All slots same level |
| **Slot Recovery** | Long rest only | Short or long rest |
| **Slots at Level 2** | Level 1 slots: 2 | Level 1 slots: 2 |
| **Slots at Level 5** | 1st: 4, 2nd: 3, 3rd: 2 | Level 3 slots: 2 |
| **Upcasting** | Manual choice | Automatic (all slots max level) |
| **Max Slot Level** | 5th level | 5th level (6-9 via Mystic Arcanum) |

**Example**: A level 5 Warlock has 2 spell slots, both 3rd level. Casting *Hex* (1st level spell) uses a 3rd level slot automatically.

### 2. Warlock Spell Slot Progression

| Level | Spell Slots | Slot Level | Cantrips | Spells Known | Invocations |
|-------|-------------|------------|----------|--------------|-------------|
| 1 | 1 | 1st | 2 | 2 | 1 |
| 2 | 2 | 1st | 2 | 3 | 3 |
| 3 | 2 | 2nd | 2 | 4 | 3 |
| 4 | 2 | 2nd | 3 | 5 | 3 |
| 5 | 2 | 3rd | 3 | 6 | 5 |
| 6 | 2 | 3rd | 3 | 7 | 5 |
| 7 | 2 | 4th | 3 | 8 | 6 |
| 8 | 2 | 4th | 3 | 9 | 6 |
| 9 | 2 | 5th | 3 | 10 | 7 |
| 10 | 2 | 5th | 4 | 10 | 7 |
| 11 | 3 | 5th | 4 | 11 | 7 |
| 12-16 | 3 | 5th | 4 | 11-13 | 8-9 |
| 17-20 | 4 | 5th | 4 | 14-15 | 9-10 |

**Note**: At level 11+, Warlock gains Mystic Arcanum for 6th-9th level spells (1 spell per level, 1/long rest each).

### 3. Eldritch Invocations

Warlock's unique customization system - choose from 22+ invocations:

**Categories**:
- **At-Will Spells**: Cast certain spells without slots (Armor of Shadows, Mask of Many Faces)
- **Spell Modifications**: Enhance cantrips (Agonizing Blast, Repelling Blast)
- **Passive Abilities**: Darkvision, skill proficiencies (Devil's Sight, Beguiling Influence)
- **Pact Boon Enhancements**: Require specific pact (Thirsting Blade, Voice of Chain Master)
- **Level-Gated**: Unlock at higher levels (Lifedrinker at 12, Witch Sight at 15)

### 4. Pact Boons (Level 3)

Choose one:
- **Pact of the Blade**: Summon pact weapon, use CHA for attacks
- **Pact of the Chain**: Enhanced Find Familiar with special forms
- **Pact of the Tome**: Book of Shadows with 3 cantrips + 2 rituals from any class

### 5. Mystic Arcanum (Level 11+)

- Level 11: Learn one 6th-level spell (1/long rest, no slot)
- Level 13: Learn one 7th-level spell (1/long rest, no slot)
- Level 15: Learn one 8th-level spell (1/long rest, no slot)
- Level 17: Learn one 9th-level spell (1/long rest, no slot)

### 6. Magical Cunning (Level 2)

- 1-minute ritual to regain expended slots
- Regain up to half maximum slots (round up)
- Once per long rest (all slots at level 20 with Eldritch Master)

---

## Database Schema

### Existing Tables (From Migration 015)

#### warlock_features
```sql
CREATE TABLE warlock_features (
    character_id TEXT PRIMARY KEY,
    level INTEGER,
    patron TEXT, -- 'Fiend', 'Archfey', 'Great Old One'
    pact_boon TEXT, -- 'blade', 'chain', 'tome'
    invocations_known TEXT, -- JSON array
    mystic_arcanum_spells TEXT, -- JSON array {level: spell_id}
    last_pact_reset TEXT, -- Timestamp
    pact_slots INTEGER, -- Current slots available
    pact_slot_level INTEGER, -- Level of slots (1-5)
    pact_slots_current INTEGER, -- Current available
    pact_slots_max INTEGER, -- Maximum slots
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

#### warlock_invocations
```sql
CREATE TABLE warlock_invocations (
    character_id TEXT NOT NULL,
    invocation_id TEXT NOT NULL,
    learned_at_level INTEGER,
    PRIMARY KEY (character_id, invocation_id),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

#### invocations
```sql
CREATE TABLE invocations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    prerequisites TEXT, -- JSON: {"level": 5, "pact": "blade", "cantrip": "eldritch_blast"}
    effect_type TEXT, -- 'passive', 'active', 'spell_modification'
    effect_data TEXT -- JSON effect details
);
```

### Modifications Needed

#### Add to warlock_features
```sql
-- Track Magical Cunning usage
ALTER TABLE warlock_features ADD COLUMN magical_cunning_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN last_magical_cunning TEXT;

-- Track Contact Patron usage (level 9+)
ALTER TABLE warlock_features ADD COLUMN contact_patron_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN last_contact_patron TEXT;

-- Track Mystic Arcanum uses (levels 11+)
ALTER TABLE warlock_features ADD COLUMN arcanum_6_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN arcanum_7_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN arcanum_8_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN arcanum_9_used BOOLEAN DEFAULT 0;
```

#### New Table: warlock_pact_progression
```sql
CREATE TABLE warlock_pact_progression (
    level INTEGER PRIMARY KEY,
    spell_slots INTEGER NOT NULL,
    slot_level INTEGER NOT NULL,
    cantrips_known INTEGER NOT NULL,
    spells_known INTEGER NOT NULL,
    invocations_known INTEGER NOT NULL
);

-- Insert progression data (levels 1-20)
INSERT INTO warlock_pact_progression VALUES
    (1, 1, 1, 2, 2, 1),
    (2, 2, 1, 2, 3, 3),
    (3, 2, 2, 2, 4, 3),
    (4, 2, 2, 3, 5, 3),
    (5, 2, 3, 3, 6, 5),
    (6, 2, 3, 3, 7, 5),
    (7, 2, 4, 3, 8, 6),
    (8, 2, 4, 3, 9, 6),
    (9, 2, 5, 3, 10, 7),
    (10, 2, 5, 4, 10, 7),
    (11, 3, 5, 4, 11, 7),
    (12, 3, 5, 4, 11, 8),
    (13, 3, 5, 4, 12, 8),
    (14, 3, 5, 4, 12, 8),
    (15, 3, 5, 4, 13, 9),
    (16, 3, 5, 4, 13, 9),
    (17, 4, 5, 4, 14, 9),
    (18, 4, 5, 4, 14, 10),
    (19, 4, 5, 4, 15, 10),
    (20, 4, 5, 4, 15, 10);
```

#### New Table: warlock_patron_features
```sql
CREATE TABLE warlock_patron_features (
    id TEXT PRIMARY KEY,
    patron TEXT NOT NULL, -- 'Fiend', 'Archfey', etc.
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    description TEXT,
    effect_type TEXT, -- 'passive', 'active', 'spell_list'
    effect_data TEXT -- JSON
);

-- Fiend Patron features (will populate in implementation)
```

---

## Service Architecture

### Core Service: WarlockService

**Location**: `src/talekeeper/services/warlock_service.py`

```python
class WarlockService:
    """Central service for Warlock class mechanics."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.pact_magic = PactMagicService(db_path)
        self.invocations = InvocationService(db_path)
        self.patron_manager = PatronManager(db_path)

    # === INITIALIZATION ===
    def initialize_warlock(self, character_id: str, level: int, patron: str) -> bool
    def level_up_warlock(self, character_id: str, new_level: int) -> Dict

    # === PACT MAGIC ===
    def get_pact_slots(self, character_id: str) -> Dict  # {current, max, level}
    def use_pact_slot(self, character_id: str) -> bool
    def restore_pact_slots(self, character_id: str, rest_type: str) -> int  # 'short' or 'long'
    def get_spell_slot_level(self, character_id: str) -> int

    # === MAGICAL CUNNING ===
    def use_magical_cunning(self, character_id: str) -> Dict  # Returns slots restored
    def can_use_magical_cunning(self, character_id: str) -> bool

    # === INVOCATIONS ===
    def learn_invocation(self, character_id: str, invocation_id: str) -> bool
    def replace_invocation(self, character_id: str, old_id: str, new_id: str) -> bool
    def get_learned_invocations(self, character_id: str) -> List[Dict]
    def can_learn_invocation(self, character_id: str, invocation_id: str) -> Tuple[bool, str]
    def get_available_invocations(self, character_id: str) -> List[Dict]

    # === PACT BOONS ===
    def select_pact_boon(self, character_id: str, boon: str) -> bool  # 'blade', 'chain', 'tome'
    def get_pact_boon(self, character_id: str) -> Optional[str]
    def summon_pact_weapon(self, character_id: str, weapon_type: str) -> Dict
    def dismiss_pact_weapon(self, character_id: str) -> bool

    # === MYSTIC ARCANUM ===
    def learn_arcanum_spell(self, character_id: str, spell_level: int, spell_id: str) -> bool
    def cast_arcanum_spell(self, character_id: str, spell_level: int) -> Tuple[bool, str]
    def has_arcanum_available(self, character_id: str, spell_level: int) -> bool
    def get_mystic_arcanum_spells(self, character_id: str) -> Dict  # {6: spell_id, 7: spell_id, ...}

    # === PATRON FEATURES ===
    def get_patron_features(self, character_id: str) -> List[Dict]
    def trigger_patron_feature(self, character_id: str, feature_id: str, context: Dict) -> Dict
```

### Supporting Services

#### PactMagicService
```python
class PactMagicService:
    """Handles Pact Magic spell slot mechanics."""

    def calculate_slots_for_level(self, level: int) -> Tuple[int, int]  # (num_slots, slot_level)
    def short_rest_recovery(self, character_id: str) -> int  # Returns slots restored
    def long_rest_recovery(self, character_id: str) -> int
    def get_upcast_level(self, character_id: str, base_spell_level: int) -> int
    def validate_spell_cast(self, character_id: str, spell_id: str) -> Tuple[bool, str]
```

#### InvocationService
```python
class InvocationService:
    """Manages Eldritch Invocations."""

    def get_invocation_effect(self, invocation_id: str) -> Dict
    def check_prerequisites(self, character_id: str, invocation_id: str) -> Tuple[bool, str]
    def apply_invocation_bonus(self, character_id: str, invocation_id: str, context: Dict) -> Any
    def get_at_will_spells(self, character_id: str) -> List[str]
    def modify_cantrip(self, character_id: str, cantrip_id: str, invocation_id: str) -> Dict
```

#### PatronManager
```python
class PatronManager:
    """Handles patron-specific features."""

    def get_patron_spells(self, patron: str, level: int) -> List[str]
    def apply_patron_feature(self, character_id: str, feature_id: str, context: Dict) -> Dict
    def get_fiend_blessing(self, character_id: str) -> int  # Temp HP on kill
    def use_dark_ones_luck(self, character_id: str, roll_value: int) -> int  # Add d10
    def set_fiendish_resilience(self, character_id: str, damage_type: str) -> bool
    def hurl_through_hell(self, character_id: str, target_id: str) -> Dict
```

---

## Implementation Phases

### Phase 0: Database Foundation (Week 1) - 6 hours

**Goal**: Complete database schema for Warlock

#### Tasks
1. ✅ **DONE** - Migration 015 exists with base tables
2. ❌ **TODO** - Create migration 015b with modifications:
   - Add Magical Cunning tracking columns
   - Add Mystic Arcanum usage tracking
   - Create `warlock_pact_progression` table
   - Create `warlock_patron_features` table
   - Populate Fiend patron features
3. ❌ **TODO** - Add Warlock spell list to database
4. ❌ **TODO** - Verify all 22 invocations have correct data

**Deliverables**:
- Migration script `015b_warlock_enhancements.sql`
- Warlock spell list in `spells` table
- Complete invocations data
- Fiend patron features populated

**Testing**:
- Verify tables created successfully
- Check foreign key constraints
- Validate JSON data format

---

### Phase 1: Pact Magic Core (Week 1-2) - 8 hours

**Goal**: Implement unique Pact Magic spell slot system

#### 1.1 PactMagicService Implementation

```python
class PactMagicService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def calculate_slots_for_level(self, level: int) -> Tuple[int, int]:
        """Get (num_slots, slot_level) for Warlock level."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT spell_slots, slot_level
            FROM warlock_pact_progression
            WHERE level = ?
        """, (level,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result
        return (1, 1)  # Default level 1

    def restore_pact_slots(self, character_id: str, rest_type: str) -> int:
        """Restore slots on short or long rest."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get max slots
        cursor.execute("""
            SELECT pact_slots_max, pact_slots_current
            FROM warlock_features
            WHERE character_id = ?
        """, (character_id,))

        max_slots, current = cursor.fetchone()
        slots_to_restore = max_slots - current

        # Update to full
        cursor.execute("""
            UPDATE warlock_features
            SET pact_slots_current = pact_slots_max,
                last_pact_reset = ?
            WHERE character_id = ?
        """, (datetime.now().isoformat(), character_id))

        conn.commit()
        conn.close()

        return slots_to_restore

    def use_pact_slot(self, character_id: str) -> bool:
        """Expend one pact slot."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE warlock_features
            SET pact_slots_current = pact_slots_current - 1
            WHERE character_id = ?
            AND pact_slots_current > 0
        """, (character_id,))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def get_upcast_level(self, character_id: str) -> int:
        """Get the level all spells are cast at (automatic upcasting)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT pact_slot_level
            FROM warlock_features
            WHERE character_id = ?
        """, (character_id,))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 1
```

#### 1.2 Integration with SpellcastingService

Modify `spellcasting_service.py` to recognize Warlock's unique system:

```python
def cast_spell(self, character_id: str, spell_id: str, slot_level: int = None) -> Dict:
    character_class = self._get_character_class(character_id)

    if character_class == 'warlock':
        # Use Pact Magic system
        warlock_service = WarlockService(self.db_path)

        # All warlock spells cast at max slot level
        actual_slot_level = warlock_service.pact_magic.get_upcast_level(character_id)

        if not warlock_service.pact_magic.use_pact_slot(character_id):
            return {'success': False, 'reason': 'No pact slots available'}

        # Cast at upcast level
        return self._execute_spell_effect(character_id, spell_id, actual_slot_level)

    else:
        # Standard spellcasting for other classes
        return self._cast_standard_spell(character_id, spell_id, slot_level)
```

**Testing**:
- ✅ Level 1 Warlock has 1 slot, level 1
- ✅ Level 5 Warlock has 2 slots, level 3
- ✅ Casting 1st level spell at level 5 uses 3rd level slot
- ✅ Short rest restores all slots
- ✅ Long rest restores all slots

---

### Phase 2: Magical Cunning & Short Rest (Week 2) - 4 hours

**Goal**: Implement Magical Cunning feature

```python
def use_magical_cunning(self, character_id: str) -> Dict:
    """1-minute ritual to restore pact slots (level 2+)."""

    # Check if already used
    if not self.can_use_magical_cunning(character_id):
        return {'success': False, 'reason': 'Already used since last long rest'}

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Get current state
    cursor.execute("""
        SELECT level, pact_slots_max, pact_slots_current
        FROM warlock_features
        WHERE character_id = ?
    """, (character_id,))

    level, max_slots, current_slots = cursor.fetchone()

    # Calculate restoration
    if level >= 20:
        # Eldritch Master: restore all slots
        slots_restored = max_slots - current_slots
    else:
        # Restore half (round up)
        max_restore = (max_slots + 1) // 2
        slots_restored = min(max_restore, max_slots - current_slots)

    # Update slots
    new_current = current_slots + slots_restored

    cursor.execute("""
        UPDATE warlock_features
        SET pact_slots_current = ?,
            magical_cunning_used = 1,
            last_magical_cunning = ?
        WHERE character_id = ?
    """, (new_current, datetime.now().isoformat(), character_id))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'slots_restored': slots_restored,
        'slots_current': new_current,
        'slots_max': max_slots
    }

def reset_magical_cunning_on_long_rest(self, character_id: str):
    """Reset Magical Cunning availability."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE warlock_features
        SET magical_cunning_used = 0
        WHERE character_id = ?
    """, (character_id,))

    conn.commit()
    conn.close()
```

**Testing**:
- ✅ Level 2 Warlock with 2 max slots, 0 current → restores 1 slot (half, rounded up)
- ✅ Can't use twice before long rest
- ✅ Level 20 Warlock restores all slots (Eldritch Master)
- ✅ Long rest resets availability

---

### Phase 3: Eldritch Invocations (Week 2-3) - 10 hours

**Goal**: Implement all 22 invocations with effects

#### 3.1 InvocationService Core

```python
class InvocationService:
    def can_learn_invocation(self, character_id: str, invocation_id: str) -> Tuple[bool, str]:
        """Check if character meets prerequisites."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get invocation prerequisites
        cursor.execute("""
            SELECT prerequisites
            FROM invocations
            WHERE id = ?
        """, (invocation_id,))

        prereq_json = cursor.fetchone()[0]
        prereqs = json.loads(prereq_json)

        # Get character data
        cursor.execute("""
            SELECT wf.level, wf.pact_boon, cs.known_spells
            FROM warlock_features wf
            JOIN character_spellcasting cs ON cs.character_id = wf.character_id
            WHERE wf.character_id = ?
        """, (character_id,))

        level, pact_boon, known_spells_json = cursor.fetchone()
        known_spells = json.loads(known_spells_json)

        conn.close()

        # Check level requirement
        if 'level' in prereqs and level < prereqs['level']:
            return (False, f"Requires Warlock level {prereqs['level']}")

        # Check pact boon requirement
        if 'pact' in prereqs and pact_boon != prereqs['pact']:
            return (False, f"Requires Pact of the {prereqs['pact'].title()}")

        # Check cantrip requirement
        if 'cantrip' in prereqs and prereqs['cantrip'] not in known_spells:
            return (False, f"Requires {prereqs['cantrip']} cantrip")

        return (True, "")

    def learn_invocation(self, character_id: str, invocation_id: str) -> bool:
        """Add invocation to character."""
        can_learn, reason = self.can_learn_invocation(character_id, invocation_id)

        if not can_learn:
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current level
        cursor.execute("""
            SELECT level FROM warlock_features WHERE character_id = ?
        """, (character_id,))
        level = cursor.fetchone()[0]

        # Add to learned invocations
        cursor.execute("""
            INSERT OR IGNORE INTO warlock_invocations
            (character_id, invocation_id, learned_at_level)
            VALUES (?, ?, ?)
        """, (character_id, invocation_id, level))

        conn.commit()
        conn.close()

        return True

    def get_at_will_spells(self, character_id: str) -> List[str]:
        """Get spells that can be cast at will from invocations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT i.effect_data
            FROM warlock_invocations wi
            JOIN invocations i ON i.id = wi.invocation_id
            WHERE wi.character_id = ?
            AND i.effect_type = 'active'
        """, (character_id,))

        at_will_spells = []
        for row in cursor.fetchall():
            effect_data = json.loads(row[0])
            if 'spell' in effect_data and effect_data.get('cost') == 'none':
                at_will_spells.append(effect_data['spell'])

        conn.close()
        return at_will_spells
```

#### 3.2 Invocation Categories

**At-Will Spell Invocations** (8 invocations):
- Armor of Shadows (Mage Armor)
- Beast Speech (Speak with Animals)
- Eldritch Sight (Detect Magic)
- Fiendish Vigor (False Life)
- Mask of Many Faces (Disguise Self)
- Master of Myriad Forms (Alter Self) - Level 5+
- Misty Visions (Silent Image)
- Whispers of the Grave (Speak with Dead) - Level 9+

**Eldritch Blast Modifications** (3 invocations):
- Agonizing Blast - Add CHA to damage (Level 2+)
- Eldritch Spear - Range 300 feet (Level 2+)
- Repelling Blast - Push 10 feet (Level 2+)

**Passive Abilities** (6 invocations):
- Beguiling Influence - Proficiency in Deception & Persuasion
- Devil's Sight - 120 ft darkvision through magical darkness (Level 2+)
- Eyes of the Rune Keeper - Read all writing
- Gift of the Depths - Swim speed, Water Breathing 1/long rest (Level 5+)
- One with Shadows - Invisibility in darkness (Level 5+)
- Witch Sight - Truesight 30 ft (Level 15+)

**Pact Boon Enhancements** (5 invocations):
- **Blade**: Thirsting Blade (Extra Attack, Level 5+), Lifedrinker (+CHA necrotic, Level 12+)
- **Chain**: Voice of Chain Master (telepathy/perception with familiar, Level 5+), Investment of Chain Master (enhanced familiar, Level 5+)
- **Tome**: Book of Ancient Secrets (ritual casting), Gift of the Protectors (prevent death, Level 9+)

**Testing**:
- ✅ Can't learn level-gated invocation early
- ✅ Can't learn pact-specific invocation without pact
- ✅ At-will spells don't consume slots
- ✅ Agonizing Blast adds CHA to Eldritch Blast damage
- ✅ Can replace invocation on level up

---

### Phase 4: Pact Boons (Week 3) - 8 hours

**Goal**: Implement 3 pact boons

#### 4.1 Pact of the Blade

```python
def select_pact_of_blade(self, character_id: str):
    """Grant Pact of the Blade at level 3."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE warlock_features
        SET pact_boon = 'blade'
        WHERE character_id = ?
    """, (character_id,))

    # Grant pact weapon feature
    cursor.execute("""
        INSERT INTO character_features (character_id, feature_id, feature_source)
        VALUES (?, 'pact_weapon', 'warlock_pact')
    """, (character_id,))

    conn.commit()
    conn.close()

def summon_pact_weapon(self, character_id: str, weapon_type: str = 'longsword') -> Dict:
    """Summon or bond with a weapon (bonus action)."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Get character's CHA modifier
    cursor.execute("""
        SELECT charisma FROM characters WHERE id = ?
    """, (character_id,))
    charisma = cursor.fetchone()[0]
    cha_mod = (charisma - 10) // 2

    # Get weapon base stats
    cursor.execute("""
        SELECT name, damage_dice, damage_type, properties
        FROM equipment
        WHERE id = ?
    """, (weapon_type,))

    weapon_data = cursor.fetchone()

    # Create pact weapon with CHA-based attacks
    pact_weapon = {
        'id': f'pact_weapon_{character_id}',
        'name': f'Pact Weapon ({weapon_data[0]})',
        'damage_dice': weapon_data[1],
        'damage_type': weapon_data[2],
        'attack_ability': 'Charisma',  # Use CHA instead of STR/DEX
        'attack_bonus': cha_mod,
        'damage_bonus': cha_mod,
        'magical': True,
        'properties': weapon_data[3]
    }

    conn.close()
    return pact_weapon
```

**Pact Weapon Features**:
- Use Charisma for attack/damage rolls
- Can choose damage type (normal, necrotic, psychic, or radiant)
- Counts as magical for overcoming resistance
- Can bond with magic weapon instead of conjuring
- Weapon disappears if >5 feet away for 1 minute

#### 4.2 Pact of the Chain

```python
def select_pact_of_chain(self, character_id: str):
    """Grant enhanced Find Familiar."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE warlock_features
        SET pact_boon = 'chain'
        WHERE character_id = ?
    """, (character_id,))

    # Grant Find Familiar spell (always prepared, no slot cost)
    cursor.execute("""
        INSERT INTO character_spellcasting_always_prepared
        (character_id, spell_id, source)
        VALUES (?, 'find_familiar', 'pact_of_chain')
    """, (character_id,))

    conn.commit()
    conn.close()
```

**Special Familiar Forms**: Imp, Pseudodragon, Quasit, Skeleton, Sprite, Venomous Snake

**Chain Benefits**:
- Cast Find Familiar as magic action (no slot)
- Forgo 1 attack to let familiar attack (using its reaction)
- Investment of Chain Master invocation adds: fly/swim speed, bonus action attack, CHA-based save DC

#### 4.3 Pact of the Tome

```python
def select_pact_of_tome(self, character_id: str):
    """Grant Book of Shadows with bonus cantrips/rituals."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE warlock_features
        SET pact_boon = 'tome'
        WHERE character_id = ?
    """, (character_id,))

    # Grant 3 cantrips from any class (player chooses)
    # Grant 2 level 1 ritual spells from any class (player chooses)

    conn.commit()
    conn.close()
```

**Book of Shadows**:
- Appears at end of short/long rest
- Choose 3 cantrips from any class spell list
- Choose 2 level 1 ritual spells from any class
- Book acts as spellcasting focus
- Book of Ancient Secrets invocation adds more ritual casting

**Testing**:
- ✅ Can select pact boon at level 3
- ✅ Pact weapon uses CHA for attacks
- ✅ Chain familiar has special forms
- ✅ Tome grants 3 bonus cantrips

---

### Phase 5: Mystic Arcanum (Week 3-4) - 6 hours

**Goal**: Implement 6th-9th level spell casting

```python
def learn_arcanum_spell(self, character_id: str, spell_level: int, spell_id: str) -> bool:
    """Learn a Mystic Arcanum spell (levels 6-9)."""

    # Validate level
    if spell_level not in [6, 7, 8, 9]:
        return False

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Check character level
    cursor.execute("""
        SELECT level, mystic_arcanum_spells
        FROM warlock_features
        WHERE character_id = ?
    """, (character_id,))

    char_level, arcanum_json = cursor.fetchone()

    # Check if character has access to this arcanum level
    required_level = {6: 11, 7: 13, 8: 15, 9: 17}[spell_level]
    if char_level < required_level:
        return False

    # Update arcanum spells
    arcanum_spells = json.loads(arcanum_json) if arcanum_json else {}
    arcanum_spells[str(spell_level)] = spell_id

    cursor.execute("""
        UPDATE warlock_features
        SET mystic_arcanum_spells = ?
        WHERE character_id = ?
    """, (json.dumps(arcanum_spells), character_id))

    conn.commit()
    conn.close()

    return True

def cast_arcanum_spell(self, character_id: str, spell_level: int) -> Tuple[bool, str]:
    """Cast a Mystic Arcanum spell (once per long rest, no slot)."""

    # Check if already used
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    usage_column = f'arcanum_{spell_level}_used'
    cursor.execute(f"""
        SELECT {usage_column}
        FROM warlock_features
        WHERE character_id = ?
    """, (character_id,))

    already_used = cursor.fetchone()[0]

    if already_used:
        return (False, "Mystic Arcanum already used (recharges on long rest)")

    # Mark as used
    cursor.execute(f"""
        UPDATE warlock_features
        SET {usage_column} = 1
        WHERE character_id = ?
    """, (character_id,))

    conn.commit()
    conn.close()

    return (True, "")

def reset_mystic_arcanum_on_long_rest(self, character_id: str):
    """Reset all Mystic Arcanum uses."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE warlock_features
        SET arcanum_6_used = 0,
            arcanum_7_used = 0,
            arcanum_8_used = 0,
            arcanum_9_used = 0
        WHERE character_id = ?
    """, (character_id,))

    conn.commit()
    conn.close()
```

**Mystic Arcanum Spells** (chosen from Warlock spell list):
- **6th Level**: Circle of Death, Create Undead, Eyebite, True Seeing
- **7th Level**: Etherealness, Finger of Death, Forcecage, Plane Shift
- **8th Level**: Befuddlement, Demiplane, Dominate Monster, Glibness, Power Word Stun
- **9th Level**: Astral Projection, Foresight, Gate, Imprisonment, Power Word Kill, True Polymorph, Weird

**Testing**:
- ✅ Can't learn 6th level spell before level 11
- ✅ Can cast arcanum spell once per long rest without slot
- ✅ Long rest resets all arcanum uses
- ✅ Can replace arcanum spell on level up

---

### Phase 6: Fiend Patron Features (Week 4) - 8 hours

**Goal**: Implement all 4 Fiend Patron features

#### Level 3: Dark One's Blessing

```python
def apply_dark_ones_blessing(self, character_id: str, enemy_defeated_by: Optional[str] = None) -> int:
    """Grant temp HP when enemy reduced to 0 HP."""

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Get Warlock level and CHA
    cursor.execute("""
        SELECT wf.level, c.charisma
        FROM warlock_features wf
        JOIN characters c ON c.id = wf.character_id
        WHERE wf.character_id = ?
        AND wf.patron = 'Fiend'
    """, (character_id,))

    result = cursor.fetchone()
    if not result:
        return 0

    level, charisma = result
    cha_mod = (charisma - 10) // 2

    # Calculate temp HP
    temp_hp = max(1, cha_mod + level)

    # Check if ally defeated enemy within 10 feet
    if enemy_defeated_by and enemy_defeated_by != character_id:
        # Check distance (would need combat positioning system)
        # For now, assume if ally, then within range in solo play
        pass

    # Grant temp HP
    cursor.execute("""
        INSERT OR REPLACE INTO character_temp_hp
        (character_id, temp_hp_current, temp_hp_source)
        VALUES (?, ?, 'dark_ones_blessing')
    """, (character_id, temp_hp))

    conn.commit()
    conn.close()

    return temp_hp
```

#### Level 3: Fiend Spells (Always Prepared)

```python
FIEND_SPELLS = {
    3: ['burning_hands', 'command', 'scorching_ray', 'suggestion'],
    5: ['fireball', 'stinking_cloud'],
    7: ['fire_shield', 'wall_of_fire'],
    9: ['geas', 'insect_plague']
}

def grant_fiend_spells(self, character_id: str, level: int):
    """Grant patron spells based on level."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    for patron_level, spells in FIEND_SPELLS.items():
        if level >= patron_level:
            for spell_id in spells:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_spellcasting_always_prepared
                    (character_id, spell_id, source)
                    VALUES (?, ?, 'fiend_patron')
                """, (character_id, spell_id))

    conn.commit()
    conn.close()
```

#### Level 6: Dark One's Own Luck

```python
def use_dark_ones_luck(self, character_id: str) -> Dict:
    """Add d10 to ability check or save (CHA mod uses per long rest)."""

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Check uses remaining
    cursor.execute("""
        SELECT c.charisma, wf.dark_ones_luck_uses
        FROM warlock_features wf
        JOIN characters c ON c.id = wf.character_id
        WHERE wf.character_id = ?
    """, (character_id,))

    charisma, uses = cursor.fetchone()
    cha_mod = max(1, (charisma - 10) // 2)

    if uses >= cha_mod:
        return {'success': False, 'reason': 'No uses remaining'}

    # Roll d10
    bonus = random.randint(1, 10)

    # Increment uses
    cursor.execute("""
        UPDATE warlock_features
        SET dark_ones_luck_uses = dark_ones_luck_uses + 1
        WHERE character_id = ?
    """, (character_id,))

    conn.commit()
    conn.close()

    return {'success': True, 'bonus': bonus}
```

#### Level 10: Fiendish Resilience

```python
def set_fiendish_resilience(self, character_id: str, damage_type: str) -> bool:
    """Choose resistance after short/long rest (not Force)."""

    if damage_type.lower() == 'force':
        return False

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE warlock_features
        SET fiendish_resilience_type = ?
        WHERE character_id = ?
    """, (damage_type, character_id))

    conn.commit()
    conn.close()

    return True
```

#### Level 14: Hurl Through Hell

```python
def hurl_through_hell(self, character_id: str, target_id: str) -> Dict:
    """Transport target through Lower Planes (once per long rest or pact slot)."""

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Check if used
    cursor.execute("""
        SELECT hurl_through_hell_used
        FROM warlock_features
        WHERE character_id = ?
    """, (character_id,))

    used = cursor.fetchone()[0]

    if used:
        return {'success': False, 'reason': 'Already used (recharge: long rest or pact slot)'}

    # Get spell save DC
    cursor.execute("""
        SELECT spell_save_dc FROM character_spellcasting
        WHERE character_id = ?
    """, (character_id,))

    save_dc = cursor.fetchone()[0]

    # Target makes CHA save
    target_save = self._make_saving_throw(target_id, 'charisma', save_dc)

    if target_save:
        return {'success': True, 'target_saved': True, 'damage': 0}

    # Check if target is fiend
    is_fiend = self._is_creature_type(target_id, 'fiend')
    damage = 0 if is_fiend else random.randint(8, 80)  # 8d10

    # Apply incapacitated condition
    cursor.execute("""
        INSERT INTO character_conditions
        (character_id, condition, duration_rounds, source)
        VALUES (?, 'incapacitated', 1, 'hurl_through_hell')
    """, (target_id,))

    # Mark as used
    cursor.execute("""
        UPDATE warlock_features
        SET hurl_through_hell_used = 1
        WHERE character_id = ?
    """, (character_id,))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'target_saved': False,
        'damage': damage,
        'incapacitated': True
    }
```

**Testing**:
- ✅ Dark One's Blessing grants temp HP on kill
- ✅ Fiend spells auto-prepared at correct levels
- ✅ Dark One's Own Luck adds d10 (CHA mod times per long rest)
- ✅ Fiendish Resilience grants damage resistance
- ✅ Hurl Through Hell deals 8d10 psychic, incapacitates

---

### Phase 7: Spell Integration (Week 4-5) - 6 hours

**Goal**: Integrate Warlock spell list with existing spell system

#### Warlock Spell List

**Cantrips (7)**:
- Chill Touch
- Eldritch Blast (signature)
- Mage Hand
- Minor Illusion
- Poison Spray
- Prestidigitation
- True Strike

**Level 1 (12 spells)**:
- Bane, Charm Person, Comprehend Languages, Detect Magic, Expeditious Retreat
- Hellish Rebuke (signature)
- Hex (signature)
- Hideous Laughter, Illusory Script, Protection from Evil and Good, Speak with Animals, Unseen Servant

**Level 2 (10 spells)**:
- Darkness, Enthrall, Hold Person, Invisibility, Mind Spike, Mirror Image, Misty Step, Ray of Enfeeblement, Spider Climb, Suggestion

**Level 3 (11 spells)**:
- Counterspell, Dispel Magic, Fear, Fly, Gaseous Form, Hypnotic Pattern, Magic Circle, Major Image, Remove Curse, Tongues, Vampiric Touch

**Level 4 (5 spells)**:
- Banishment, Blight, Charm Monster, Dimension Door, Hallucinatory Terrain

**Level 5 (7 spells)**:
- Contact Other Plane, Dream, Hold Monster, Mislead, Planar Binding, Scrying, Teleportation Circle

**Total**: 52 spells (levels 0-5) + 25 higher-level spells (levels 6-9) = **77 spells**

#### Warlock-Specific Spell Implementations

**Hex** - Level 1 Enchantment (Concentration, 1 hour):
```python
class HexHandler(SpellHandler):
    def execute(self, caster_id, targets, slot_level, context):
        target_id = targets[0]

        # Start concentration
        self.concentration.start_concentration(caster_id, 'hex', slot_level, duration_rounds=600)

        # Choose ability to curse
        cursed_ability = context.get('cursed_ability', 'strength')

        # Apply hex effect
        buff_data = {
            'type': 'damage_bonus_per_hit',
            'damage_dice': '1d6',
            'damage_type': 'necrotic',
            'cursed_ability': cursed_ability,  # Disadvantage on checks
            'source': 'hex'
        }

        self.effects.apply_buff(target_id, buff_data, duration_rounds=600)

        return {
            'success': True,
            'target': target_id,
            'bonus_damage': '1d6 necrotic',
            'cursed_ability': cursed_ability
        }
```

**Hellish Rebuke** - Level 1 Evocation (Reaction):
```python
class HellishRebukeHandler(SpellHandler):
    def execute(self, caster_id, targets, slot_level, context):
        """Reaction: Deal fire damage when hit."""
        attacker_id = targets[0]

        # Get spell save DC
        save_dc = self._get_spell_save_dc(caster_id)

        # Target makes DEX save
        save_successful = self._make_save(attacker_id, 'dexterity', save_dc)

        # Calculate damage (2d10 + 1d10 per level above 1st)
        num_dice = 2 + (slot_level - 1)
        damage = sum(random.randint(1, 10) for _ in range(num_dice))

        if save_successful:
            damage //= 2

        self.effects.apply_damage(attacker_id, damage, 'fire', 'hellish_rebuke')

        return {
            'success': True,
            'damage': damage,
            'target_saved': save_successful
        }
```

**Eldritch Blast** - Cantrip (Warlock signature):
```python
class EldritchBlastHandler(SpellHandler):
    def execute(self, caster_id, targets, slot_level, context):
        """1d10 force per beam (1 beam per 5 levels)."""

        # Get Warlock level
        level = self._get_warlock_level(caster_id)
        num_beams = 1 + (level - 1) // 5  # 1 at 1st, 2 at 5th, 3 at 11th, 4 at 17th

        # Check for invocations
        agonizing = self._has_invocation(caster_id, 'agonizing_blast')
        repelling = self._has_invocation(caster_id, 'repelling_blast')
        eldritch_spear = self._has_invocation(caster_id, 'eldritch_spear')

        # Get CHA modifier for Agonizing Blast
        cha_mod = self._get_ability_mod(caster_id, 'charisma') if agonizing else 0

        # Range
        range_feet = 300 if eldritch_spear else 120

        results = []
        for i in range(num_beams):
            target_id = targets[i] if i < len(targets) else targets[0]

            # Attack roll
            attack_roll = self._make_attack_roll(caster_id, target_id)

            if attack_roll['hit']:
                damage = random.randint(1, 10) + cha_mod
                self.effects.apply_damage(target_id, damage, 'force', 'eldritch_blast')

                # Repelling Blast
                if repelling:
                    self._push_creature(target_id, 10)

                results.append({'hit': True, 'damage': damage, 'target': target_id})
            else:
                results.append({'hit': False, 'target': target_id})

        return {
            'success': True,
            'beams': results,
            'num_beams': num_beams
        }
```

**Testing**:
- ✅ Warlock can prepare spells from Warlock list only
- ✅ Hex applies d6 necrotic per hit and disadvantage on ability checks
- ✅ Hellish Rebuke triggers as reaction when hit
- ✅ Eldritch Blast fires multiple beams at higher levels
- ✅ Agonizing Blast adds CHA to each beam

---

### Phase 8: UI Integration (Week 5-6) - 8 hours

**Goal**: Build UI components for Warlock features

#### 8.1 Pact Magic Slot Display

Modify `action_panel.py` to show Warlock slots differently:

```python
class SpellSlotsDisplay(QWidget):
    def update_spell_slots(self, character_id: str):
        character_class = self._get_character_class(character_id)

        if character_class == 'warlock':
            # Show Pact Magic slots
            warlock_service = WarlockService(self.db_path)
            slots_data = warlock_service.get_pact_slots(character_id)

            # Display: "Pact Slots: 2/2 (Level 3)"
            self.slots_label.setText(
                f"Pact Slots: {slots_data['current']}/{slots_data['max']} "
                f"(Level {slots_data['level']})"
            )
        else:
            # Standard spellcasting display
            self._show_standard_slots(character_id)
```

#### 8.2 Invocation Selection Dialog

```python
class InvocationSelectionDialog(QDialog):
    """Dialog for selecting Eldritch Invocations on level up."""

    def __init__(self, character_id: str, num_to_select: int, parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.num_to_select = num_to_select
        self.selected_invocations = []

        self.warlock_service = WarlockService('talekeeper.db')
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"Choose {self.num_to_select} Eldritch Invocation(s)")
        layout.addWidget(title)

        # Get available invocations
        available = self.warlock_service.invocations.get_available_invocations(
            self.character_id
        )

        # Invocation list with checkboxes
        self.invocation_list = QListWidget()
        for inv in available:
            item = QListWidgetItem()
            checkbox = QCheckBox(f"{inv['name']} - {inv['description']}")

            # Disable if prerequisites not met
            can_learn, reason = self.warlock_service.invocations.can_learn_invocation(
                self.character_id, inv['id']
            )

            if not can_learn:
                checkbox.setEnabled(False)
                checkbox.setText(f"{checkbox.text()} [{reason}]")

            self.invocation_list.addItem(item)
            self.invocation_list.setItemWidget(item, checkbox)

        layout.addWidget(self.invocation_list)

        # Confirm button
        confirm_btn = QPushButton("Confirm Selection")
        confirm_btn.clicked.connect(self._confirm_selection)
        layout.addWidget(confirm_btn)

    def _confirm_selection(self):
        # Validate selection count
        selected = self._get_selected_invocations()

        if len(selected) != self.num_to_select:
            QMessageBox.warning(self, "Invalid Selection",
                              f"You must select exactly {self.num_to_select} invocation(s)")
            return

        self.selected_invocations = selected
        self.accept()
```

#### 8.3 Pact Boon Selection

```python
class PactBoonDialog(QDialog):
    """Dialog for choosing Pact Boon at level 3."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_boon = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Choose Your Pact Boon (Level 3)")
        layout.addWidget(title)

        # Blade
        blade_btn = QPushButton("Pact of the Blade")
        blade_btn.setToolTip(
            "Summon a pact weapon. Use Charisma for attack/damage rolls."
        )
        blade_btn.clicked.connect(lambda: self._select_boon('blade'))
        layout.addWidget(blade_btn)

        # Chain
        chain_btn = QPushButton("Pact of the Chain")
        chain_btn.setToolTip(
            "Gain Find Familiar with special forms (Imp, Pseudodragon, etc.)"
        )
        chain_btn.clicked.connect(lambda: self._select_boon('chain'))
        layout.addWidget(chain_btn)

        # Tome
        tome_btn = QPushButton("Pact of the Tome")
        tome_btn.setToolTip(
            "Gain Book of Shadows with 3 bonus cantrips + 2 ritual spells"
        )
        tome_btn.clicked.connect(lambda: self._select_boon('tome'))
        layout.addWidget(tome_btn)

    def _select_boon(self, boon: str):
        self.selected_boon = boon
        self.accept()
```

#### 8.4 Mystic Arcanum Selection

```python
class MysticArcanumDialog(QDialog):
    """Dialog for choosing Mystic Arcanum spell."""

    def __init__(self, character_id: str, spell_level: int, parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.spell_level = spell_level
        self.selected_spell = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(f"Choose Level {self.spell_level} Mystic Arcanum")
        layout.addWidget(title)

        # Get available spells
        warlock_spells = self._get_warlock_spells(self.spell_level)

        self.spell_list = QListWidget()
        for spell in warlock_spells:
            item = QListWidgetItem(f"{spell['name']} - {spell['description'][:100]}")
            item.setData(Qt.UserRole, spell['id'])
            self.spell_list.addItem(item)

        layout.addWidget(self.spell_list)

        # Confirm
        confirm_btn = QPushButton("Select")
        confirm_btn.clicked.connect(self._confirm_selection)
        layout.addWidget(confirm_btn)

    def _confirm_selection(self):
        current_item = self.spell_list.currentItem()
        if current_item:
            self.selected_spell = current_item.data(Qt.UserRole)
            self.accept()
```

#### 8.5 Active Invocation Effects Display

Add to character sheet:

```python
def update_warlock_features(self, character_id: str):
    """Display active Warlock features."""

    warlock_service = WarlockService(self.db_path)

    # Show pact boon
    pact_boon = warlock_service.get_pact_boon(character_id)
    if pact_boon:
        self.pact_boon_label.setText(f"Pact: {pact_boon.title()}")

    # Show invocations
    invocations = warlock_service.get_learned_invocations(character_id)
    inv_text = ", ".join([inv['name'] for inv in invocations])
    self.invocations_label.setText(f"Invocations: {inv_text}")

    # Show patron
    features = warlock_service.get_patron_features(character_id)
    self.patron_label.setText(f"Patron: {features[0]['patron']}")
```

**Testing**:
- ✅ Pact slots display correctly (2/2 Level 3)
- ✅ Can select invocations on level up
- ✅ Can choose pact boon at level 3
- ✅ Can select Mystic Arcanum spells at 11/13/15/17
- ✅ Character sheet shows invocations and pact boon

---

### Phase 9: Testing & Polish (Week 6-7) - 8 hours

**Goal**: Comprehensive testing of all Warlock systems

#### Test Suite Structure

```
tests/
├── unit/
│   ├── test_pact_magic_service.py
│   ├── test_invocation_service.py
│   ├── test_patron_manager.py
│   └── test_warlock_spells.py
├── integration/
│   ├── test_warlock_level_progression.py
│   ├── test_warlock_combat.py
│   ├── test_pact_boons.py
│   └── test_mystic_arcanum.py
└── regression/
    └── test_warlock_full_campaign.py
```

#### Master Test: Warlock Levels 1-20

```python
class TestWarlockProgression(unittest.TestCase):
    """Test Warlock from level 1 to 20."""

    def test_level_1_warlock(self):
        """Test level 1 features: Pact Magic, 1 invocation."""
        warlock = self.create_warlock(level=1, patron='Fiend')

        # Check pact slots
        slots = self.get_pact_slots(warlock)
        self.assertEqual(slots['max'], 1)
        self.assertEqual(slots['level'], 1)

        # Check invocations
        invocations = self.get_invocations(warlock)
        self.assertEqual(len(invocations), 1)

        # Check cantrips
        cantrips = self.get_cantrips(warlock)
        self.assertEqual(len(cantrips), 2)

    def test_level_3_pact_boon(self):
        """Test level 3 pact boon selection."""
        warlock = self.create_warlock(level=3, patron='Fiend')

        # Select Pact of the Blade
        self.select_pact_boon(warlock, 'blade')

        # Verify
        self.assertEqual(self.get_pact_boon(warlock), 'blade')

        # Summon pact weapon
        weapon = self.summon_pact_weapon(warlock, 'longsword')
        self.assertEqual(weapon['attack_ability'], 'Charisma')

    def test_level_5_extra_slots(self):
        """Test level 5: 2 slots, level 3."""
        warlock = self.create_warlock(level=5, patron='Fiend')

        slots = self.get_pact_slots(warlock)
        self.assertEqual(slots['max'], 2)
        self.assertEqual(slots['level'], 3)

        # Cast 1st level spell - uses 3rd level slot
        self.cast_spell(warlock, 'hex', slot_level=None)  # Auto-upcast

        # Check slot consumed
        slots_after = self.get_pact_slots(warlock)
        self.assertEqual(slots_after['current'], 1)

    def test_level_11_mystic_arcanum(self):
        """Test level 11: Mystic Arcanum (6th level)."""
        warlock = self.create_warlock(level=11, patron='Fiend')

        # Learn 6th level spell
        self.learn_arcanum(warlock, 6, 'circle_of_death')

        # Cast without slot
        result = self.cast_arcanum(warlock, 6)
        self.assertTrue(result['success'])

        # Can't cast again
        result2 = self.cast_arcanum(warlock, 6)
        self.assertFalse(result2['success'])

        # Long rest resets
        self.long_rest(warlock)
        result3 = self.cast_arcanum(warlock, 6)
        self.assertTrue(result3['success'])

    def test_short_rest_slot_recovery(self):
        """Test Pact Magic short rest recovery."""
        warlock = self.create_warlock(level=5, patron='Fiend')

        # Use both slots
        self.cast_spell(warlock, 'hex')
        self.cast_spell(warlock, 'hex')

        # 0 slots remaining
        slots = self.get_pact_slots(warlock)
        self.assertEqual(slots['current'], 0)

        # Short rest
        self.short_rest(warlock)

        # Both slots restored
        slots_after = self.get_pact_slots(warlock)
        self.assertEqual(slots_after['current'], 2)

    def test_fiend_patron_features(self):
        """Test Fiend Patron features."""
        warlock = self.create_warlock(level=14, patron='Fiend')

        # Dark One's Blessing (level 3)
        goblin = self.spawn_monster('goblin')
        self.defeat_enemy(warlock, goblin)
        temp_hp = self.get_temp_hp(warlock)
        self.assertGreater(temp_hp, 0)

        # Dark One's Own Luck (level 6)
        result = self.use_dark_ones_luck(warlock)
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['bonus'], 1)
        self.assertLessEqual(result['bonus'], 10)

        # Fiendish Resilience (level 10)
        self.set_fiendish_resilience(warlock, 'fire')
        self.assertTrue(self.has_resistance(warlock, 'fire'))

        # Hurl Through Hell (level 14)
        orc = self.spawn_monster('orc')
        result = self.hurl_through_hell(warlock, orc)
        self.assertTrue(result['success'])
```

#### Regression Tests

```bash
# Add to run_regression_tests.py

def test_warlock_fiend_level_1_to_20():
    """Full progression test for Warlock."""
    print("Testing Warlock Fiend (levels 1-20)...")

    warlock = create_warlock(patron='Fiend')

    for level in range(1, 21):
        level_up(warlock, level)

        # Validate progression
        assert_pact_slots_correct(warlock, level)
        assert_invocations_correct(warlock, level)
        assert_patron_features_unlocked(warlock, level)

        if level == 3:
            select_pact_boon(warlock, 'blade')

        if level >= 11:
            assert_mystic_arcanum_available(warlock, level)

    print("✓ Warlock progression 1-20 validated")
```

**Test Coverage Goals**:
- ✅ Pact Magic slot mechanics (short rest recovery)
- ✅ Magical Cunning (half slots, 1/long rest)
- ✅ All 22 invocations functional
- ✅ All 3 pact boons work correctly
- ✅ Mystic Arcanum (6th-9th level spells)
- ✅ Fiend Patron features (all 4)
- ✅ Eldritch Blast with invocation modifiers
- ✅ Hex, Hellish Rebuke combat integration
- ✅ Pact weapon uses Charisma
- ✅ Level 1-20 progression validates

---

## Success Criteria

### Minimum Viable Product (MVP) - Phases 0-4
- ✅ Pact Magic system fully functional (short rest recovery)
- ✅ Magical Cunning works (level 2+)
- ✅ At least 10 core invocations implemented
- ✅ Pact of the Blade working
- ✅ Eldritch Blast with Agonizing Blast
- ✅ Hex spell integrated

### Full Implementation - All Phases
- ✅ All 22 invocations functional
- ✅ All 3 pact boons (Blade, Chain, Tome)
- ✅ Mystic Arcanum (levels 6-9) working
- ✅ Fiend Patron complete (all 4 features)
- ✅ All 52 Warlock spells (levels 0-5) integrated
- ✅ UI for invocation selection, pact boon, slot display
- ✅ 100% test coverage on Warlock systems
- ✅ Levels 1-20 progression validated

---

## Timeline Summary

| Phase | Weeks | Hours | Key Deliverables |
|-------|-------|-------|------------------|
| Phase 0 | 1 | 6 | Database foundation complete |
| Phase 1 | 1-2 | 8 | Pact Magic system working |
| Phase 2 | 2 | 4 | Magical Cunning implemented |
| Phase 3 | 2-3 | 10 | All invocations functional |
| Phase 4 | 3 | 8 | Pact boons implemented |
| Phase 5 | 3-4 | 6 | Mystic Arcanum working |
| Phase 6 | 4 | 8 | Fiend Patron complete |
| Phase 7 | 4-5 | 6 | Spell integration done |
| Phase 8 | 5-6 | 8 | UI components built |
| Phase 9 | 6-7 | 8 | Testing complete |
| **TOTAL** | **7** | **72** | **Warlock fully playable** |

**Realistic Estimate**: 6-8 weeks for complete implementation

---

## Risk Mitigation

### Technical Risks
1. **Pact Magic Conflicts** - Ensure Warlock slots don't interfere with standard spellcasting
   - Mitigation: Separate table (`warlock_features`), distinct service methods
2. **Invocation Prerequisites** - Complex validation logic
   - Mitigation: JSON-based prerequisite system, clear validation messages
3. **Spell Upcast Confusion** - Players may not understand auto-upcasting
   - Mitigation: Clear UI messaging "Casting at 3rd level (Pact Magic)"

### Scope Risks
1. **22 Invocations is Large** - Each needs custom logic
   - Mitigation: Group by type, implement passive/active separately
2. **77 Spells Total** - Large spell list
   - Mitigation: Many spells shared with other classes (use existing handlers)
3. **Solo Play Limitations** - Pact of Chain less useful without party
   - Mitigation: Document limitations, focus on Blade/Tome

---

## Dependencies

### Required Before Starting
- ✅ SpellcastingService must support class-specific systems
- ✅ SpellEffectsService for spell mechanics
- ✅ ConcentrationSystem for concentration spells
- ✅ ConditionManager for status effects

### Blocks Future Work
- Warlock Subclasses (Archfey, Great Old One) - requires this foundation
- Multiclassing with Warlock - requires Pact Magic/Spellcasting distinction
- Invocation expansion (more invocations in future)

---

## Next Steps

1. ✅ Review and approve this plan
2. ⏭️ Create migration `015b_warlock_enhancements.sql`
3. ⏭️ Implement PactMagicService core
4. ⏭️ Test Pact Magic system (Phase 1)
5. ⏭️ Implement Magical Cunning (Phase 2)
6. ⏭️ Begin invocation implementation (Phase 3)

---

*Plan Version: 1.0*
*Created: October 8, 2025*
*For: TaleKeeper D&D 2024 Warlock Class Implementation*
