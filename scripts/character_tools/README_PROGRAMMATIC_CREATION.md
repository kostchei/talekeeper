# Programmatic Character Creation for TaleKeeper

## Overview

This system allows you to create D&D 2024 characters from JSON or YAML templates **without using the UI**. It directly calls the backend APIs that the 6-step character creation wizard uses, enabling:

- **Automated testing** - Create test characters in seconds
- **Onboarding** - Pre-generate characters for new players
- **Templates** - Store and share character builds
- **Batch creation** - Generate multiple characters for testing

## Quick Start

### 1. Create a character from template:

```bash
python scripts/character_tools/programmatic_character_creator.py templates/fighter_soldier.json
```

### 2. Use in Python code:

```python
from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator

creator = ProgrammaticCharacterCreator('talekeeper.db')
character = creator.create_from_template('templates/fighter_soldier.json')

print(f"Created: {character['name']}")
print(f"HP: {character['hit_points_max']}")
print(f"AC: {character['armor_class']}")
```

## Template Format

Templates can be JSON or YAML. See `templates/fighter_soldier.json` for a complete example.

### Required Fields

```json
{
  "name": "random",           // "random" = auto-generate, or specify a name
  "species": "Human",         // Race/species name from database
  "class": "Fighter",         // Class name from database
  "background": "Soldier",    // Background name from database
  "ability_scores": {         // Base scores (before background ASI)
    "strength": 15,
    "dexterity": 14,
    "constitution": 13,
    "intelligence": 8,
    "wisdom": 12,
    "charisma": 10
  }
}
```

### Optional Fields

```json
{
  "feats": ["Tough"],                    // Species bonus feats
  "fighting_style": "Defense",           // Fighter-specific (required for Fighter)
  "weapon_masteries": [                  // Fighter-specific (required for Fighter)
    "longsword",
    "shield",
    "longbow"
  ],
  "class_skills": [                      // Skills from class
    "Athletics",
    "Perception"
  ],
  "species_skills": [],                  // Skills from species (Human gets 1)
  "equipment_choices": {                 // Starting equipment
    "martial_weapon": "Longsword",
    "armor": "Chain Mail",
    "shield": "Shield"
  },
  "level": 1,                            // Character level (default: 1)
  "experience_points": 0                 // XP (default: 0)
}
```

## How It Works: The 11 Steps

The programmatic creator mirrors the UI workflow from `encounter_panel.py` but calls backend APIs directly:

### Step 1: Bootstrap Engine Services
```python
game_engine = GameEngineSQLite('talekeeper.db')
feat_processor = FeatEffectsProcessor()
weapon_service = WeaponAttackService(db_path)
```

### Step 2: Load Class Data
Calls `GameEngineSQLite.get_available_classes_sync()` and queries full class metadata:
- Hit die
- Armor/weapon proficiencies
- Saving throws
- Skill choices

**API**: `src/talekeeper/core/game_engine_sqlite.py:909`

### Step 3: Select Fighter Features
Queries the `feats` table for fighting styles (category='FS'):
- Defense (+1 AC with armor)
- Dueling (+2 damage one-handed)
- Great Weapon Fighting (reroll 1-2 on damage)
- etc.

Also selects 3 weapon masteries.

**API**: `src/talekeeper/ui/encounter_pane/encounter_panel.py:1978`

### Step 4: Load Background & Species
Queries `backgrounds` and `races` tables:
- Background: skill proficiencies, origin feat, ASI (+2/+1)
- Species: speed, size, traits, species proficiencies

**API**: `src/talekeeper/ui/encounter_pane/encounter_panel.py:2667`

### Step 5: Select Feats
- **Background origin feat**: Automatically applied (e.g., Savage Attacker for Soldier)
- **Species bonus feat**: Choose from template (e.g., Tough for Human)

**API**: `src/talekeeper/ui/encounter_pane/encounter_panel.py:2759`

### Step 6: Allocate Abilities & Skills
- Start with base ability scores (point-buy, standard array, or custom)
- Apply background ASI: +2 to primary, +1 to secondary
- Select class skills (2 for Fighter)
- Select background skills (2 for Soldier: Athletics, Intimidation)
- Select species skills (1 for Human: any)

**API**: `src/talekeeper/ui/encounter_pane/encounter_panel.py:3190`

### Step 7: Select Equipment
Calls `GameEngineSQLite.get_class_equipment_choices_sync('fighter')` and selects:
- Martial weapon (Longsword)
- Shield
- Armor (Chain Mail)
- Simple weapon (Javelin)

**API**: `src/talekeeper/core/game_engine_sqlite.py:967`

### Step 8: Generate Name
Uses `NAMES_BY_HOMELAND` from `alt_encounters.py` or custom name pools.
Falls back to random fantasy names if template specifies `"name": "random"`.

**API**: `src/talekeeper/ui/encounter_pane/alt_encounters.py:87`

### Step 9: Assemble Payload
Builds the final character creation payload matching the format from `encounter_panel._finish_character_creation()`.

**API**: `src/talekeeper/ui/encounter_pane/encounter_panel.py:3240`

### Step 10: Prepare for Save
Converts to engine schema via `main_window._prepare_character_for_save()`:
- Map names to database IDs
- Calculate HP: `hit_die + CON_modifier`
- Apply feat effects (Tough: +2 HP per level)

**API**: `src/talekeeper/ui/main_window.py:1616`

### Step 11: Persist & Verify
1. Call `create_new_character_sync(save_data, save_slot)` to write to database
2. Apply equipment choices via `apply_equipment_choices_sync()`
3. Update mastery resources via `WeaponAttackService.update_character_mastery_resources()`
4. Load back with `load_character_sync()` to verify

**API**: `src/talekeeper/core/game_engine_sqlite.py:525`

## Example: Level 1 Human Fighter, Soldier Background

This example creates the character you requested:

```json
{
  "name": "random",
  "species": "Human",
  "class": "Fighter",
  "background": "Soldier",
  "feats": ["Tough"],
  "fighting_style": "Defense",
  "weapon_masteries": ["longsword", "shield", "longbow"],
  "ability_scores": {
    "strength": 15,
    "dexterity": 14,
    "constitution": 13,
    "intelligence": 8,
    "wisdom": 12,
    "charisma": 10
  },
  "class_skills": ["Athletics", "Perception"],
  "equipment_choices": {
    "martial_weapon": "Longsword",
    "armor": "Chain Mail",
    "shield": "Shield"
  }
}
```

### What Gets Created:

- **Name**: Randomly generated (e.g., "Gareth Ironhand")
- **Species**: Human
- **Class**: Fighter (Level 1)
- **Background**: Soldier
- **Ability Scores** (after background +2 STR, +1 CON):
  - STR 17 (+3)
  - DEX 14 (+2)
  - CON 14 (+2)
  - INT 8 (-1)
  - WIS 12 (+1)
  - CHA 10 (+0)
- **HP**: 12 (d10=10 + CON+2) → **14 with Tough** (+2 HP/level)
- **AC**: 17 (Chain Mail 16 + Defense fighting style +1)
- **Skills**: Athletics, Intimidation (Soldier) + Athletics, Perception (Fighter)
- **Feats**: Savage Attacker (Soldier origin), Tough (Human bonus)
- **Equipment**: Longsword, Shield, Chain Mail, Javelin
- **Fighting Style**: Defense (+1 AC with armor)
- **Weapon Masteries**: Longsword, Shield, Longbow

## Advanced Usage

### Batch Create Multiple Characters

```python
from pathlib import Path
from programmatic_character_creator import ProgrammaticCharacterCreator

creator = ProgrammaticCharacterCreator('talekeeper.db')

templates = Path('templates').glob('*.json')
for template_path in templates:
    character = creator.create_from_template(str(template_path))
    print(f"Created: {character['name']}")
```

### Integration with Testing Framework

```python
# In your test file
from programmatic_character_creator import ProgrammaticCharacterCreator

def test_fighter_champion_features():
    creator = ProgrammaticCharacterCreator('test_talekeeper.db')

    fighter = creator.create_from_dict({
        'name': 'Test Fighter',
        'species': 'Human',
        'class': 'Fighter',
        'background': 'Soldier',
        'feats': ['Tough'],
        'fighting_style': 'Dueling',
        'weapon_masteries': ['longsword', 'shield', 'longbow'],
        'ability_scores': {
            'strength': 16, 'dexterity': 14, 'constitution': 15,
            'intelligence': 8, 'wisdom': 12, 'charisma': 10
        }
    })

    assert fighter['hit_points_max'] == 14  # d10 + 2 CON + 2 Tough
    assert 'Dueling' in fighter.get('fighting_styles', [])
```

### Custom Name Pools

Extend `_step_8_generate_name()` to add campaign-specific names:

```python
CAMPAIGN_NAMES = {
    'nordic': ['Bjorn', 'Freya', 'Ragnar', 'Astrid'],
    'eastern': ['Kenji', 'Mei', 'Hiroshi', 'Sakura'],
    'desert': ['Rashid', 'Amara', 'Zayn', 'Layla']
}

def _step_8_generate_name(self, template, species_data, class_data, background_data):
    campaign_region = template.get('campaign_region', 'default')
    names = CAMPAIGN_NAMES.get(campaign_region, HUMAN_FIRST_NAMES)
    return random.choice(names)
```

## Database Schema Notes

### Key Tables Used

- `classes` - Class definitions (Fighter, Rogue, etc.)
- `races` - Species definitions (Human, Elf, etc.)
- `backgrounds` - Background definitions (Soldier, Criminal, etc.)
- `feats` - All feats including fighting styles (category='FS')
- `class_skill_choices` - Skills available per class
- `species_proficiencies` - Species-specific proficiencies
- `characters` - Saved character data
- `character_features` - Character class features
- `character_inventory` - Character items

### Important: Background ASI

Backgrounds grant **ability score increases** (+2/+1) in D&D 2024. The programmatic creator applies these automatically:

```sql
SELECT ability_score_increase_1, ability_score_increase_2
FROM backgrounds
WHERE name = 'Soldier'
-- Returns: 'strength', 'constitution'
```

Template base scores + background ASI = final scores.

## Comparison to UI Workflow

| UI Step | Programmatic Equivalent |
|---------|------------------------|
| Click "Create Character" | `creator.create_from_dict(template)` |
| Choose Class | `_step_2_load_class()` |
| Select Fighting Style | `_step_3_select_fighter_features()` |
| Choose Background & Species | `_step_4_load_background_species()` |
| Select Feats | `_step_5_select_feats()` |
| Allocate Ability Scores | `_step_6_allocate_abilities_skills()` |
| Choose Equipment | `_step_7_select_equipment()` |
| Enter Name | `_step_8_generate_name()` |
| Review & Confirm | `_step_9_assemble_payload()` |
| Save to Slot | `_step_11_persist_and_verify()` |

## Troubleshooting

### Character not appearing in UI

After creating programmatically, reload the save slots:
```python
game_engine.get_save_slots_sync()
```

### HP not matching expected value

Check if Tough feat was applied:
```python
print(f"Feats: {character['feats']}")
print(f"HP: {character['hit_points_max']}")
# Expected: base_hp + (level * 2) if Tough is present
```

### Equipment not equipped

Verify equipment choices were applied:
```python
print(f"Main hand: {character['equipment_main_hand']}")
print(f"Off hand: {character['equipment_off_hand']}")
print(f"Armor: {character['equipment_armor']}")
```

### Fighting style not working

Check if fighting style was saved as a feat:
```python
conn = sqlite3.connect('talekeeper.db')
cursor = conn.cursor()
cursor.execute("SELECT feats FROM characters WHERE id = ?", (character['id'],))
feats_json = cursor.fetchone()[0]
print(f"Feats: {json.loads(feats_json)}")
# Should include 'Defense' or chosen style
```

## Future Enhancements

- [ ] Support for other classes (Rogue, Cleric, Wizard, etc.)
- [ ] Spell selection for casters
- [ ] Multi-level character creation (levels 2-20)
- [ ] Subclass selection (Champion, Battle Master, etc.)
- [ ] CLI with interactive prompts
- [ ] Web API for character generation service
- [ ] Template validation schema (JSON Schema)

## References

- UI character creation: `src/talekeeper/ui/encounter_pane/encounter_panel.py`
- Game engine: `src/talekeeper/core/game_engine_sqlite.py`
- Main window save flow: `src/talekeeper/ui/main_window.py`
- Feat effects: `src/talekeeper/services/feat_effects.py`
- Weapon service: `src/talekeeper/services/weapon_attack_service.py`
