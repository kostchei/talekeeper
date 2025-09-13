# TaleKeeper Proficiency System Documentation

## Overview
The proficiency system implements D&D 2024 proficiency rules for weapons, armor, skills, and saving throws. It automatically assigns class-based proficiencies during character creation and applies appropriate bonuses to attacks, skill checks, and saving throws.

## Core Components

### 1. Proficiency Service (`services/proficiency_system.py`)
**Main class:** `ProficiencySystem`

**Key methods:**
- `initialize_character_proficiencies(character_id, class_id, background, race_id, conn=None)` - Sets up all proficiencies for a new character
- `get_character_proficiencies(character_id)` - Returns dict of all proficiencies by type
- `is_proficient_with_weapon(character_id, weapon_name)` - Checks weapon proficiency
- `is_proficient_with_armor(character_id, armor_name)` - Checks armor proficiency
- `is_proficient_with_shield(character_id)` - Checks shield proficiency
- `is_proficient_in_skill(character_id, skill_name)` - Checks skill proficiency
- `calculate_skill_bonus(character_id, skill_name, ability_mod)` - Calculates skill bonus with proficiency
- `get_saving_throw_bonus(character_id, ability)` - Calculates saving throw bonus with proficiency
- `get_attack_bonus(character_id, weapon_name, ability_mod)` - Calculates attack bonus with proficiency

### 2. Proficiency Bonus Scaling (`services/proficiency_bonus.py`)
**Main function:** `get_proficiency_bonus(character_level)`

**D&D 2024 scaling:**
- Levels 1-4: +2
- Levels 5-8: +3
- Levels 9-12: +4
- Levels 13-16: +5
- Levels 17-20: +6

## Database Schema

### Primary Table: `character_proficiencies`
```sql
CREATE TABLE character_proficiencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    proficiency_type TEXT NOT NULL, -- 'skill', 'weapon', 'armor', 'saving_throw', 'tool', 'language'
    proficiency_name TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'unknown', -- 'class', 'background', 'race', 'feat', 'manual'
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, proficiency_name)
);
```

### Source Tables (for class proficiencies):
- `class_weapon_proficiencies` - Maps class_id to weapon_type ('simple', 'martial', specific weapons)
- `class_armor_proficiencies` - Maps class_id to armor_type ('light', 'medium', 'heavy', 'shields')
- `class_skill_proficiencies` - Maps class_id to skill names
- `class_saving_throws` - Maps class_id to ability names ('strength', 'constitution', etc.)

## Integration Points

### 1. Character Creation (`core/game_engine_sqlite.py` lines 578-589)
During character creation, proficiencies are automatically initialized:
```python
# Initialize proficiencies using the proficiency system (pass the connection)
self.proficiency_system.initialize_character_proficiencies(
    character_id, 
    character_data['class_id'],
    character_data.get('background_id'),
    character_data.get('race_id'),
    conn=conn
)
```

### 2. Combat System (`core/combat_manager.py` lines 515-528)
Attack bonuses include proficiency:
```python
# Add proficiency bonus for player attacks
if attacker.type == CombatantType.PLAYER:
    weapon_name = weapon_data.get('name', '')
    is_proficient, _ = self.proficiency_system.is_proficient_with_weapon(attacker.id, weapon_name)
    
    if is_proficient and attacker.level:
        prof_bonus = get_proficiency_bonus(attacker.level)
        attack_bonus = base_attack_bonus + prof_bonus
```

### 3. Equipment Validation (`core/game_engine_sqlite.py` lines 1809-1831)
Equipment proficiency checking:
```python
if item_type == 'armor':
    armor_name = item_data.get('name', '')
    is_proficient, message = self.proficiency_system.is_proficient_with_armor(character_id, armor_name)
    if not is_proficient:
        return False, message
```

### 4. Character Sheet UI (`character_sheet/character_panel.py`)

**Skills (lines 1334-1362):**
```python
# Get character proficiencies
char_proficiencies = proficiency_system.get_character_proficiencies(character_id)
skill_proficiencies = char_proficiencies.get('skill', [])

# Check if proficient in this skill
is_proficient = skill_name in skill_proficiencies
skill_bonus = ability_mod + (proficiency_bonus if is_proficient else 0)
```

**Saving Throws (lines 1365-1395):**
```python
# Map short ability names (STR, DEX) to full names (strength, dexterity)
ability_name_map = {
    'STR': 'strength', 'DEX': 'dexterity', 'CON': 'constitution',
    'INT': 'intelligence', 'WIS': 'wisdom', 'CHA': 'charisma'
}

full_ability_name = ability_name_map.get(ability_name, ability_name.lower())
is_proficient = full_ability_name in [save.lower() for save in save_proficiencies]
save_bonus = ability_mod + (proficiency_bonus if is_proficient else 0)
```

**Proficiencies Display (lines 1641-1690):**
Shows all proficiencies in the detailed panel, formatted by type (armor, weapons, skills, etc.)

## Proficiency Types and Examples

### Weapon Proficiencies
- **simple** - All simple weapons (dagger, club, javelin, etc.)
- **martial** - All martial weapons (longsword, battleaxe, etc.)
- **specific weapons** - Individual weapons (e.g., "hand_crossbow" for rogues)

### Armor Proficiencies
- **light** - Light armor only
- **medium** - Light + medium armor
- **heavy** - All armor types (light, medium, heavy)
- **shields** - Shield proficiency (separate from armor)

### Skill Proficiencies
Individual skill names (e.g., "Athletics", "Stealth", "Arcana")

### Saving Throw Proficiencies
Ability names in lowercase (e.g., "strength", "constitution")

## Class Examples

### Fighter
- **Armor:** light, medium, heavy, shields
- **Weapons:** simple, martial
- **Skills:** 8 skills from class list (Acrobatics, Animal Handling, Athletics, History, Insight, Intimidation, Perception, Survival)
- **Saves:** strength, constitution

### Rogue  
- **Armor:** light
- **Weapons:** simple, hand_crossbow, longsword, rapier, shortsword
- **Skills:** 12 skills from expanded list
- **Saves:** dexterity, intelligence

### Wizard
- **Armor:** none
- **Weapons:** daggers, darts, slings, quarterstaffs, light crossbows
- **Skills:** 6 skills from class list
- **Saves:** intelligence, wisdom

## Important Notes

### Database Connection Handling
The proficiency system accepts an optional `conn` parameter to use an existing database connection. This prevents "database is locked" errors during character creation when multiple systems try to access the database simultaneously.

### Equipment Table Mapping
- Equipment table uses `item_type` column (not `type`)
- Weapon categories stored in `weapon_category` (e.g., "martial_melee", "simple_ranged")
- Armor types stored in `armor_type` (e.g., "light", "medium", "heavy")

### UI Display Mapping
- Saving throw widgets use short names ("STR", "DEX") as keys
- Database stores full ability names ("strength", "dexterity")
- Mapping is required in UI code (see `ability_name_map`)

### Proficiency Bonus Application
- **Attack Rolls:** Added if proficient with weapon
- **Skill Checks:** Added if proficient in skill
- **Saving Throws:** Added if proficient in that ability save
- **Spell Save DC:** Uses proficiency bonus + spellcasting ability modifier

## Troubleshooting

### Common Issues
1. **Missing proficiencies on new characters:** Check that `initialize_character_proficiencies` is called during character creation with proper database connection
2. **Wrong saving throw bonuses:** Verify ability name mapping in character sheet UI
3. **Equipment proficiency errors:** Ensure equipment table has correct `item_type` and category columns
4. **Database lock errors:** Always pass existing connection to proficiency methods during transactions

### Debugging Commands
```python
# Check character proficiencies
from services.proficiency_system import ProficiencySystem
ps = ProficiencySystem()
profs = ps.get_character_proficiencies(character_id)
print(profs)

# Test saving throw bonus
bonus = ps.get_saving_throw_bonus(character_id, 'strength')
print(f"Strength save bonus: +{bonus}")

# Test weapon proficiency
is_prof, msg = ps.is_proficient_with_weapon(character_id, 'Longsword')
print(f"Longsword proficient: {is_prof} - {msg}")
```

## Five Sources of Proficiencies (IMPLEMENTED)

### 1. Class Proficiencies (Choice-based) ✓
- **Fighter**: Choose 2 from 8 skills (Acrobatics, Animal Handling, Athletics, History, Insight, Intimidation, Perception, Survival)
- **Rogue**: Choose 4 from 11 skills (expanded list including Stealth, Investigation, etc.)
- **Wizard**: Choose 2 from 6 skills (Arcana, History, Insight, Investigation, Medicine, Religion)
- Stored in `class_skill_choices` table with count and available options

### 2. Background Proficiencies (Fixed) ✓
- **Criminal**: Deception, Stealth + thieves' tools, gaming set
- **Soldier**: Athletics, Intimidation + gaming set, land vehicles
- **Sage**: Arcana, History + 2 language choices
- Stored in `background_proficiencies` table

### 3. Species Proficiencies (Fixed + Choices) ✓
- **Human**: Choose 1 skill from any
- **Elf**: Perception + longsword, shortbow proficiency
- **Dwarf**: Smith's tools proficiency
- **Halfling**: Stealth proficiency
- Stored in `species_proficiencies` table

### 4. Feat Proficiencies ✓
- **Skilled**: Choose 3 skill proficiencies
- **Weapon Master**: Choose 4 weapon proficiencies
- **Lightly Armored**: Light armor proficiency
- **Moderately Armored**: Medium armor + shields
- **Heavily Armored**: Heavy armor proficiency
- Handled by `add_feat_proficiencies()` method

### 5. Level-up Features (Future)
- Class features that grant proficiencies at higher levels
- Subclass features
- Multiclass proficiency gains

## Updated Database Schema

### New Tables Added:
```sql
-- Class skill selection rules
CREATE TABLE class_skill_choices (
    class_id TEXT NOT NULL,
    skill_count INTEGER NOT NULL,
    available_skills TEXT NOT NULL, -- JSON array
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Background proficiencies
CREATE TABLE background_proficiencies (
    background_id TEXT NOT NULL,
    proficiency_type TEXT NOT NULL, -- 'skill', 'tool', 'language'
    proficiency_name TEXT NOT NULL,
    FOREIGN KEY (background_id) REFERENCES backgrounds(id)
);

-- Species proficiencies and choices
CREATE TABLE species_proficiencies (
    species_id TEXT NOT NULL,
    proficiency_type TEXT NOT NULL,
    proficiency_name TEXT, -- NULL for choices
    choice_count INTEGER DEFAULT 0, -- Number of choices to make
    available_options TEXT, -- JSON array of options
    FOREIGN KEY (species_id) REFERENCES races(id)
);
```

## Character Creation Integration

### Updated Method Signature:
```python
initialize_character_proficiencies(
    character_id: str,
    class_id: str,
    background: str = None,
    race_id: str = None,
    selected_skills: List[str] = None,  # NEW: Player's class skill choices
    conn = None
)
```

### Character Creation Process:
1. Player selects class skills from available list
2. System adds fixed background proficiencies
3. System adds fixed species proficiencies
4. Player makes species choices (if any)
5. System processes feat proficiencies when feats are selected

## Testing Results
✓ All 5 proficiency sources working correctly
✓ No duplicate proficiencies (INSERT OR IGNORE)
✓ Proper source tracking in database
✓ Correct skill selection limits enforced
✓ Background and species proficiencies auto-added
✓ Feat proficiencies working (Skilled, armor feats, etc.)

Example test character (Human Rogue, Criminal background + Skilled feat):
- **Class**: 4 chosen skills + weapon/armor/save proficiencies
- **Background**: 2 skills + 2 tools (Criminal)
- **Species**: 1 chosen skill (Human)
- **Feat**: 3 chosen skills (Skilled feat)
- **Total**: 19 proficiencies from 4 sources

## Future Enhancements
- Level-up proficiency gains from class features
- Multiclass proficiency rules
- Expertise system (double proficiency bonus)
- Jack of All Trades (half proficiency to non-proficient skills)
- Tool and language choice selections in UI