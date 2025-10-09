# Unified Class Abilities System - Database Design

**Date:** 2025-10-09
**Purpose:** Design database schema for unified class abilities architecture

---

## Goal

Replace 6 separate ability services (3,533 lines) with a single unified service that stores class-specific data in the database, following the same pattern already used for **feats** and **character_features**.

---

## Current Pattern: Feats System (Template to Follow)

TaleKeeper already has a working database-driven system for feats:

### Feat Definition Table (All Feats)
```sql
CREATE TABLE feats (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    prerequisites TEXT,              -- JSON
    ability_score_increases TEXT,    -- JSON
    benefits TEXT,                   -- JSON
    source TEXT DEFAULT 'SRD',
    category TEXT DEFAULT 'general',
    repeatable INTEGER DEFAULT 0
);
```

### Character Feat Assignment (Per Character)
```sql
CREATE TABLE character_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    feature_type TEXT NOT NULL DEFAULT 'passive',        -- 'action', 'bonus_action', 'reaction', 'passive'
    usage_type TEXT NOT NULL DEFAULT 'permanent',        -- 'permanent', 'short_rest', 'long_rest', 'daily'
    level_gained INTEGER NOT NULL DEFAULT 1,
    description TEXT NOT NULL DEFAULT '',
    mechanics TEXT,                                       -- JSON for complex mechanics
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

### Feat Effects Processor (Service)
- `FeatEffectsProcessor` reads from `feats` table
- Applies effects to characters using `character_features` table
- Single service handles all feats
- No per-feat service files needed

**This is the pattern we want for class abilities.**

---

## Proposed Unified System

### 1. Class Abilities Definition Table (New)

Store ALL class ability definitions (replaces hardcoded logic in services):

```sql
CREATE TABLE class_abilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ability_id TEXT UNIQUE NOT NULL,              -- 'second_wind', 'rage', 'sneak_attack'
    class_name TEXT NOT NULL,                      -- 'Fighter', 'Barbarian', 'Rogue'
    ability_name TEXT NOT NULL,                    -- 'Second Wind', 'Rage', 'Sneak Attack'
    description TEXT,

    -- When does this ability unlock?
    level_gained INTEGER NOT NULL,                 -- 1, 2, 5, etc.
    subclass_requirement TEXT,                     -- NULL or 'Champion', 'Berserker', etc.

    -- How does it work?
    feature_type TEXT NOT NULL,                    -- 'action', 'bonus_action', 'reaction', 'passive'
    usage_type TEXT NOT NULL,                      -- 'unlimited', 'short_rest', 'long_rest', 'per_turn', 'permanent'

    -- Resource scaling
    uses_formula TEXT,                             -- '1', '2 + (level >= 17)', 'proficiency_bonus'
    scaling_type TEXT,                             -- 'fixed', 'level_based', 'ability_based', 'proficiency_based'

    -- Effects
    mechanics JSON NOT NULL,                       -- All ability-specific mechanics

    -- Metadata
    source TEXT DEFAULT 'SRD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_class_abilities_class ON class_abilities(class_name);
CREATE INDEX idx_class_abilities_level ON class_abilities(level_gained);
```

**Example Data:**

```sql
-- Fighter: Second Wind
INSERT INTO class_abilities VALUES (
    1, 'second_wind', 'Fighter', 'Second Wind',
    'You have a limited well of stamina. On your turn, you can use a Bonus Action to regain HP.',
    1, NULL,
    'bonus_action', 'short_rest',
    '1', 'fixed',
    '{
        "heal_formula": "1d10 + level",
        "heal_type": "healing",
        "action_cost": "bonus_action",
        "conditions": []
    }',
    'SRD', CURRENT_TIMESTAMP
);

-- Fighter: Action Surge
INSERT INTO class_abilities VALUES (
    2, 'action_surge', 'Fighter', 'Action Surge',
    'You can push yourself beyond normal limits. On your turn, you can take one additional action.',
    2, NULL,
    'special', 'short_rest',
    '1 + (level >= 17)', 'level_based',
    '{
        "effect": "grant_extra_action",
        "action_count": 1,
        "duration": "instant",
        "conditions": []
    }',
    'SRD', CURRENT_TIMESTAMP
);

-- Barbarian: Rage
INSERT INTO class_abilities VALUES (
    3, 'rage', 'Barbarian', 'Rage',
    'In battle, you fight with primal ferocity. On your turn, you can enter a rage as a bonus action.',
    1, NULL,
    'bonus_action', 'long_rest',
    'rage_uses_by_level(level)', 'level_based',
    '{
        "damage_bonus_formula": "2 + (level >= 9) + (level >= 16)",
        "resistance_types": ["physical"],
        "advantage_on": ["strength_checks", "strength_saves"],
        "duration_turns": 10,
        "ends_if": ["no_attack_two_turns", "unconscious"],
        "benefits": {
            "damage_resistance": ["bludgeoning", "piercing", "slashing"],
            "rage_damage": "calculated"
        }
    }',
    'SRD', CURRENT_TIMESTAMP
);

-- Rogue: Sneak Attack
INSERT INTO class_abilities VALUES (
    4, 'sneak_attack', 'Rogue', 'Sneak Attack',
    'You know how to strike subtly and exploit a foe''s distraction.',
    1, NULL,
    'passive', 'unlimited',
    NULL, 'fixed',
    '{
        "damage_dice_formula": "1 + ((level - 1) // 2)",
        "damage_type": "weapon",
        "requirements": ["finesse_or_ranged", "advantage_or_ally_nearby"],
        "frequency": "once_per_turn",
        "conditions": []
    }',
    'SRD', CURRENT_TIMESTAMP
);

-- Fighter: Indomitable (scales at levels 9, 13, 17)
INSERT INTO class_abilities VALUES (
    5, 'indomitable', 'Fighter', 'Indomitable',
    'You can reroll a saving throw that you fail.',
    9, NULL,
    'reaction', 'long_rest',
    '1 + (level >= 13) + (level >= 17)', 'level_based',
    '{
        "effect": "reroll_save",
        "trigger": "failed_save",
        "must_take_new_roll": true
    }',
    'SRD', CURRENT_TIMESTAMP
);
```

---

### 2. Character Ability Usage Tracking (New)

Track per-character resource consumption (replaces `*_features` tables):

```sql
CREATE TABLE character_ability_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    ability_id TEXT NOT NULL,                      -- References class_abilities.ability_id

    -- Resource tracking
    current_uses INTEGER NOT NULL DEFAULT 0,
    max_uses INTEGER NOT NULL DEFAULT 0,

    -- State tracking (for toggle/duration abilities)
    is_active BOOLEAN DEFAULT FALSE,               -- For Rage, Concentration, etc.
    turns_remaining INTEGER DEFAULT 0,             -- For duration-based abilities

    -- Metadata
    last_used TIMESTAMP,
    last_reset TIMESTAMP,

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (ability_id) REFERENCES class_abilities(ability_id),
    UNIQUE(character_id, ability_id)
);

CREATE INDEX idx_char_ability_usage_char ON character_ability_usage(character_id);
CREATE INDEX idx_char_ability_usage_ability ON character_ability_usage(ability_id);
```

**Example Data:**

```sql
-- Fighter level 5: Second Wind, Action Surge available
INSERT INTO character_ability_usage VALUES
(1, 'char_123', 'second_wind', 1, 1, FALSE, 0, NULL, '2025-10-09 08:00:00'),
(2, 'char_123', 'action_surge', 1, 1, FALSE, 0, NULL, '2025-10-09 08:00:00');

-- Barbarian level 3: Rage (used 1 of 3)
INSERT INTO character_ability_usage VALUES
(3, 'char_456', 'rage', 2, 3, TRUE, 8, '2025-10-09 10:30:00', '2025-10-09 08:00:00');

-- Rogue level 7: Sneak Attack (unlimited, just tracking)
INSERT INTO character_ability_usage VALUES
(4, 'char_789', 'sneak_attack', 0, 0, FALSE, 0, NULL, NULL);
```

---

### 3. Ability Scaling Formulas (New Helper Table - Optional)

Store reusable scaling formulas:

```sql
CREATE TABLE ability_scaling_formulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    formula_name TEXT UNIQUE NOT NULL,             -- 'rage_uses_by_level', 'proficiency_bonus'
    description TEXT,
    formula_type TEXT NOT NULL,                    -- 'lookup', 'calculation', 'conditional'
    formula_data JSON NOT NULL                     -- Level->value mapping or calculation
);
```

**Example Data:**

```sql
-- Rage uses by level (Barbarian)
INSERT INTO ability_scaling_formulas VALUES (
    1, 'rage_uses_by_level',
    'Number of rage uses available by level',
    'lookup',
    '{
        "1": 2, "2": 2,
        "3": 3, "4": 3, "5": 3,
        "6": 4, "7": 4, "8": 4, "9": 4, "10": 4, "11": 4,
        "12": 5, "13": 5, "14": 5, "15": 5, "16": 5,
        "17": 6, "18": 6, "19": 6,
        "20": 999
    }'
);

-- Proficiency bonus by level
INSERT INTO ability_scaling_formulas VALUES (
    2, 'proficiency_bonus',
    'Proficiency bonus by level',
    'lookup',
    '{
        "1": 2, "2": 2, "3": 2, "4": 2,
        "5": 3, "6": 3, "7": 3, "8": 3,
        "9": 4, "10": 4, "11": 4, "12": 4,
        "13": 5, "14": 5, "15": 5, "16": 5,
        "17": 6, "18": 6, "19": 6, "20": 6
    }'
);

-- Sneak attack dice by level (Rogue)
INSERT INTO ability_scaling_formulas VALUES (
    3, 'sneak_attack_dice',
    'Sneak attack damage dice by level',
    'calculation',
    '{"formula": "1 + ((level - 1) // 2)"}'
);
```

---

## Deprecate (But Keep Initially)

We'll **keep existing tables** during migration for safety:

```sql
-- Keep but mark deprecated
fighter_features
barbarian_features
rogue_features
wizard_features
cleric_features
paladin_features
warlock_features
```

**Migration strategy:**
1. Create new tables alongside old ones
2. Run unified service for one class (Barbarian)
3. Compare results against old service
4. If identical, migrate next class
5. Once all classes migrated, drop old tables

---

## Unified Service Architecture

### Single Service Class
```python
class ClassAbilitiesService:
    """Unified service for all class abilities."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._ability_cache = {}  # Cache ability definitions

    def get_character_abilities(self, character_id: str) -> List[Dict]:
        """Get all abilities available to this character."""
        # Query character class + level
        # Query class_abilities for matching class/level
        # Join with character_ability_usage for current state
        # Return list of available abilities

    def use_ability(self, character_id: str, ability_id: str, context: Dict) -> Dict:
        """Use an ability (Second Wind, Rage, etc.)."""
        # 1. Get ability definition from class_abilities
        # 2. Check if character has ability (class/level)
        # 3. Check uses remaining from character_ability_usage
        # 4. Execute mechanics from JSON
        # 5. Update usage tracking
        # 6. Return results

    def restore_abilities(self, character_id: str, rest_type: str):
        """Restore abilities after short/long rest."""
        # Query character_ability_usage WHERE character_id = ?
        # For each ability, check usage_type
        # If usage_type matches rest_type, restore to max_uses

    def calculate_max_uses(self, ability_id: str, level: int, character_stats: Dict) -> int:
        """Calculate max uses for an ability at given level."""
        # Get ability from class_abilities
        # Parse uses_formula
        # If formula references scaling table, look it up
        # Return calculated max uses

    def update_ability_resources_for_level(self, character_id: str, new_level: int):
        """Recalculate all ability max_uses when character levels up."""
        # Get all character abilities
        # Recalculate max_uses for each
        # Update character_ability_usage
        # Grant new abilities if level threshold reached
```

---

## Character Creation Flow (Preserve Inline Pattern)

```python
def _initialize_class_features(self, cursor, character_id: str, character_data: Dict):
    """Initialize class features - INLINE, no external calls."""
    class_id = character_data.get('class_id', '').lower()
    level = character_data.get('level', 1)

    # Query class_abilities for this class + level
    cursor.execute("""
        SELECT ability_id, ability_name, usage_type, uses_formula, mechanics
        FROM class_abilities
        WHERE class_name = ? AND level_gained <= ?
        ORDER BY level_gained
    """, (class_id.title(), level))

    abilities = cursor.fetchall()

    for ability in abilities:
        ability_id, name, usage_type, uses_formula, mechanics = ability

        # Calculate max uses (inline, using same cursor)
        max_uses = self._calculate_max_uses_inline(uses_formula, level)

        # Insert into character_ability_usage
        cursor.execute("""
            INSERT INTO character_ability_usage (
                character_id, ability_id, current_uses, max_uses, is_active, turns_remaining
            ) VALUES (?, ?, ?, ?, FALSE, 0)
        """, (character_id, ability_id, max_uses, max_uses))

        # Also add to character_features for UI/display
        cursor.execute("""
            INSERT INTO character_features (
                character_id, feature_name, feature_type, usage_type, level_gained, description
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (character_id, name, 'action', usage_type, level, mechanics))

    # Still insert into legacy *_features table during transition
    if class_id == 'fighter':
        self._initialize_fighter_features_legacy(cursor, character_id, character_data)
    # ... etc
```

**Key:** No external service calls, all inline with passed cursor.

---

## Migration Path

### Phase 1: Create New Tables
```sql
-- Run migration: 030_unified_class_abilities.sql
CREATE TABLE class_abilities (...);
CREATE TABLE character_ability_usage (...);
CREATE TABLE ability_scaling_formulas (...);
```

### Phase 2: Seed Ability Data
```sql
-- Populate class_abilities with all Fighter/Barbarian/Rogue abilities
INSERT INTO class_abilities VALUES (...);  -- All abilities for all classes
```

### Phase 3: Implement Unified Service
```python
# New file: src/talekeeper/services/class_abilities_service.py
class ClassAbilitiesService:
    # Implement unified logic
```

### Phase 4: Test One Class (Barbarian)
```python
# Keep BarbarianAbilitiesService
# Add ClassAbilitiesService.use_rage()
# Compare outputs
# If identical, mark Barbarian as migrated
```

### Phase 5: Migrate All Classes
```python
# Repeat Phase 4 for each class
# Once all pass, deprecate old services
```

### Phase 6: Remove Old Tables
```sql
-- After successful migration
DROP TABLE fighter_features;
DROP TABLE barbarian_features;
-- ... etc
```

---

## Advantages of New System

### 1. Single Source of Truth
All ability definitions in database, not scattered across 6 files (3,533 lines).

### 2. No Code Changes for New Abilities
Adding a new ability = SQL INSERT, not 50+ lines of Python.

### 3. Easy Balancing
Change max uses or damage formula in database, no code deployment.

### 4. Consistent Mechanics
All abilities use same activation/resource/rest logic.

### 5. Better Testing
Test one service instead of six.

### 6. Easier UI Integration
Query `class_abilities` to build action cards dynamically.

### 7. Future-Proof
11 D&D classes × ~10 abilities each = 110 abilities
Current: 110 × 50 lines = 5,500 lines of code
New: ~500 lines of service + database rows

---

## Data Migration Strategy

### Step 1: Extract Current Ability Data
```python
# Script to extract from existing services
abilities = []
abilities.append({
    'ability_id': 'second_wind',
    'class_name': 'Fighter',
    'ability_name': 'Second Wind',
    'level_gained': 1,
    'usage_type': 'short_rest',
    'uses_formula': '1',
    'mechanics': {'heal_formula': '1d10 + level'}
})
# ... extract all abilities from all 6 services
```

### Step 2: Generate SQL Inserts
```python
# Generate migration file
with open('database/migrations/030_unified_class_abilities.sql', 'w') as f:
    f.write('-- Unified Class Abilities Migration\n\n')
    f.write('CREATE TABLE class_abilities (...);\n\n')
    for ability in abilities:
        f.write(f"INSERT INTO class_abilities VALUES (...);\n")
```

### Step 3: Run Migration
```bash
python database/database_init.py --migrate
```

---

## JSON Mechanics Format

### Combat Abilities
```json
{
    "action_cost": "bonus_action",
    "damage_formula": "1d10 + level",
    "damage_type": "healing",
    "target": "self",
    "conditions": []
}
```

### Toggle Abilities (Rage)
```json
{
    "activation": "bonus_action",
    "duration_type": "turns",
    "duration": 10,
    "benefits": {
        "damage_resistance": ["bludgeoning", "piercing", "slashing"],
        "damage_bonus": "2 + (level >= 9) + (level >= 16)",
        "advantage_on": ["strength_checks", "strength_saves"]
    },
    "ends_if": ["no_attack_two_turns", "unconscious"]
}
```

### Passive Abilities (Sneak Attack)
```json
{
    "trigger": "weapon_attack",
    "damage_dice": "1d6",
    "dice_count_formula": "1 + ((level - 1) // 2)",
    "requirements": {
        "weapon_type": ["finesse", "ranged"],
        "condition": "advantage_or_ally_nearby"
    },
    "frequency": "once_per_turn"
}
```

### Resource Abilities (Action Surge)
```json
{
    "effect": "grant_extra_action",
    "action_count": 1,
    "duration": "instant",
    "restrictions": ["one_extra_attack_max"]
}
```

---

## Summary: What Needs to Be Added

### New Tables (3)
1. ✅ `class_abilities` - All ability definitions (110+ rows for all classes)
2. ✅ `character_ability_usage` - Per-character resource tracking
3. ✅ `ability_scaling_formulas` - Reusable scaling lookup tables (optional)

### New Service (1)
4. ✅ `src/talekeeper/services/class_abilities_service.py` - Unified ability handler

### Migration Script (1)
5. ✅ `database/migrations/030_unified_class_abilities.sql` - Schema + seed data

### Data Extraction Script (1)
6. ✅ `scripts/utilities/extract_class_abilities.py` - Generate ability data from current services

---

## Next Steps

1. **Design approval** - Review this design doc
2. **Create tables** - Write migration SQL
3. **Extract data** - Script to pull from existing services
4. **Implement service** - Build ClassAbilitiesService
5. **Test Barbarian** - Validate against existing BarbarianAbilitiesService
6. **Full migration** - All 6+ classes
7. **Deprecate old services** - Remove 3,533 lines of code

Would you like me to start with Step 2 (create the migration SQL)?
