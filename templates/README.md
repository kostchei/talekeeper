# Character Templates for TaleKeeper

This directory contains JSON and YAML templates for creating D&D 2024 characters programmatically.

## Available Templates

### Martial Characters

#### [fighter_soldier.json](fighter_soldier.json)
- **Build**: Sword and Board Tank
- **Class**: Fighter (Defense fighting style)
- **Key Features**: Longsword + Shield, Chain Mail, Second Wind
- **Role**: Frontline tank with high AC

#### [barbarian_berserker.json](barbarian_berserker.json)
- **Build**: Raging Greataxe Warrior
- **Class**: Barbarian
- **Key Features**: Greataxe, Rage, Unarmored Defense
- **Role**: High damage striker with rage resistance

#### [paladin_devotion.json](paladin_devotion.json)
- **Build**: Holy Smiter
- **Class**: Paladin (Defense fighting style)
- **Key Features**: Longsword + Shield, Divine Smite, Lay on Hands
- **Role**: Tanky striker with healing and burst damage

#### [rogue_assassin.json](rogue_assassin.json)
- **Build**: Stealth Striker
- **Class**: Rogue
- **Key Features**: Rapier, Sneak Attack, Expertise in Stealth
- **Role**: High single-target damage, skill monkey

### Spellcasters

#### [warlock_bladelock.json](warlock_bladelock.json)
- **Build**: Eldritch Blast Spammer
- **Class**: Warlock (Fiend patron, Pact of the Blade)
- **Key Features**: Eldritch Blast, Hex, Agonizing Blast invocation
- **Role**: Ranged damage with limited spell slots

#### [cleric_life.json](cleric_life.json)
- **Build**: Support Healer
- **Class**: Cleric (Life Domain)
- **Key Features**: Cure Wounds, Bless, Shield of Faith
- **Role**: Tank/healer hybrid with heavy armor

#### [wizard_evoker.json](wizard_evoker.json)
- **Build**: Blaster Wizard
- **Class**: Wizard
- **Key Features**: Fire Bolt, Magic Missile, Shield, Ritual casting
- **Role**: Ranged AoE damage and utility

## Quick Start

### Validate a Template
```bash
python scripts/character_tools/template_validator.py templates/fighter_soldier.json
```

### Create a Character
```bash
python scripts/character_tools/programmatic_character_creator.py templates/fighter_soldier.json
```

### Use in Python Code
```python
from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator

creator = ProgrammaticCharacterCreator('talekeeper.db')
character = creator.create_from_template('templates/barbarian_berserker.json')

print(f"Created: {character['name']}")
print(f"HP: {character['hit_points_max']}")
print(f"AC: {character['armor_class']}")
```

## Template Format

### Required Fields

```json
{
  "class": "Fighter",           // Must match database class name
  "species": "Human",           // Must match database race name
  "background": "Soldier"       // Must match database background name
}
```

### Optional Fields (Class-Specific)

#### All Classes
```json
{
  "name": "random",                  // "random" = auto-generate, or specify name
  "level": 1,                         // Default: 1
  "experience_points": 0,             // Default: 0
  "ability_scores": {                 // Default: uses class-optimized array
    "strength": 16,
    "dexterity": 14,
    "constitution": 15,
    "intelligence": 8,
    "wisdom": 12,
    "charisma": 10
  },
  "class_skills": ["Athletics", "Perception"],  // Skills from class
  "species_skills": [],                          // Skills from species (Human gets 1)
  "feats": ["Tough"],                            // Species bonus feats
  "equipment_choices": {                         // Starting equipment
    "martial_weapon": "Longsword",
    "armor": "Chain Mail",
    "shield": "Shield"
  }
}
```

#### Fighter/Paladin/Ranger (Martial)
```json
{
  "fighting_style": "Defense",       // Archery, Defense, Dueling, Great Weapon Fighting, Protection, Two-Weapon Fighting
  "weapon_masteries": [               // Fighter: 3, Paladin: 2, Ranger: 2
    "longsword",
    "shield",
    "longbow"
  ]
}
```

#### Barbarian
```json
{
  "weapon_masteries": ["greataxe", "handaxe", "javelin"]  // 2 weapon masteries at level 1
}
```

#### Warlock
```json
{
  "patron": "fiend",                          // fiend, great_old_one, archfey, etc.
  "pact_boon": "pact_of_the_blade",           // Gets at level 3 (cosmetic at level 1)
  "invocations": ["agonizing_blast"],         // 1 invocation at level 1
  "cantrips": ["eldritch_blast", "mage_hand"],  // 2 cantrips
  "spells_known": ["hex", "armor_of_agathys"]   // 2 level 1 spells
}
```

#### Cleric/Wizard/Druid/Sorcerer/Bard (Full Casters)
```json
{
  "cantrips": ["sacred_flame", "guidance", "light"],          // 3-4 cantrips (varies by class)
  "spells_prepared": ["cure_wounds", "bless", "shield_of_faith"]  // Prepared/known spells
}
```

#### Rogue
```json
{
  "expertise_skills": ["Stealth", "Sleight of Hand"]  // 2 expertise skills at level 1
}
```

## Ability Score Generation

Templates support three methods:

### 1. Explicit Scores (Recommended)
```json
{
  "ability_scores": {
    "strength": 16,
    "dexterity": 14,
    "constitution": 15,
    "intelligence": 8,
    "wisdom": 12,
    "charisma": 10
  }
}
```

### 2. Omit (Uses Class Defaults)
If you omit `ability_scores`, the system uses optimized defaults for each class:
- **Fighter**: STR 16, DEX 14, CON 15, WIS 12, CHA 10, INT 8
- **Barbarian**: STR 16, DEX 13, CON 15, WIS 12, CHA 10, INT 8
- **Warlock**: CHA 16, DEX 14, CON 14, INT 12, WIS 10, STR 10
- **Wizard**: INT 16, DEX 14, CON 14, WIS 12, CHA 10, STR 8
- etc.

### 3. Background Ability Score Increases

**IMPORTANT**: D&D 2024 backgrounds grant +2/+1 ability score increases!

The system automatically applies background ASI:
- **Soldier**: +2 STR, +1 CON
- **Acolyte**: +2 WIS, +1 INT
- **Criminal**: +2 DEX, +1 INT
- **Sage**: +2 INT, +1 WIS

Example:
```json
{
  "background": "Soldier",
  "ability_scores": {
    "strength": 15,      // Will become 17 after +2 from Soldier
    "constitution": 13    // Will become 14 after +1 from Soldier
  }
}
```

## Skill Proficiencies

Skills come from three sources:

### 1. Class Skills
Number varies by class:
- Fighter: 2 skills from Athletics, Acrobatics, Animal Handling, History, Insight, Intimidation, Perception, Survival
- Rogue: 4 skills from Acrobatics, Athletics, Deception, Insight, Intimidation, Investigation, Perception, Performance, Persuasion, Sleight of Hand, Stealth

### 2. Background Skills
Automatically granted (2 skills):
- Soldier: Athletics, Intimidation
- Acolyte: Insight, Religion
- Criminal: Deception, Stealth
- Sage: Arcana, History

### 3. Species Skills
Some species grant bonus skill proficiencies:
- Human: 1 skill of your choice
- Half-Elf: 2 skills of your choice

## Equipment Choices

Equipment is class-specific. The system queries `class_equipment_choices` table for valid options.

### Fighter Equipment
```json
{
  "equipment_choices": {
    "martial_weapon": "Longsword",       // Or "Greatsword", "Battleaxe", etc.
    "armor": "Chain Mail",                // Or "Plate Mail", "Scale Mail", etc.
    "shield": "Shield",                   // Optional
    "simple_weapon": "Javelin"            // Ranged option
  }
}
```

### Warlock Equipment
```json
{
  "equipment_choices": {
    "simple_weapon": "Dagger",
    "arcane_focus": "Wand",               // Or "Crystal", "Orb", "Rod", "Staff"
    "pack": "Scholar's Pack"              // Or "Dungeoneer's Pack", "Explorer's Pack"
  }
}
```

## Feats

### Origin Feats (Automatic)
Backgrounds grant one origin feat automatically:
- Soldier → Savage Attacker
- Acolyte → Magic Initiate
- Criminal → Alert
- Sage → Keen Mind

### Species Bonus Feats
Specify in template:
```json
{
  "feats": ["Tough"]  // Human gets 1 bonus feat
}
```

Common level 1 feats:
- **Tough**: +2 HP per level
- **Alert**: +5 initiative, can't be surprised
- **Lucky**: 3 luck points per long rest
- **Savage Attacker**: Reroll damage dice once per turn
- **Great Weapon Master**: -5 to hit, +10 damage

### Fighting Style Feats
For Fighter/Paladin/Ranger, fighting styles are technically feats with category='FS':
```json
{
  "fighting_style": "Defense"  // Stored as feat in database
}
```

## Name Generation

### Random Names
```json
{
  "name": "random"  // Generates campaign-appropriate name
}
```

Output examples:
- Fighter + Soldier → "Gareth Ironhand", "Helena Steelhart"
- Warlock + Charlatan → "Zephyr Shadowweaver", "Lyra Darkwhisper"

### Custom Names
```json
{
  "name": "Sir Maximillian the Bold"
}
```

## Validation

Before creating characters, validate your template:

```bash
python scripts/character_tools/template_validator.py templates/my_character.json
```

The validator checks:
- ✓ Required fields present
- ✓ Class/species/background exist in database
- ✓ Ability scores in valid range (3-20)
- ✓ Skills are valid
- ✓ Feats exist in database
- ✓ Class-specific features (fighting styles, spells, etc.)

Example output:
```
=== Validating fighter_soldier.json ===

  WARNINGS (2):
    - No equipment choices specified
    - Total ability scores unusual: 75 (expected ~72)

  ✓ Template is valid!
```

## Tips for Creating Templates

### 1. Start with an Example
Copy an existing template and modify it:
```bash
cp templates/fighter_soldier.json templates/my_fighter.json
```

### 2. Validate Early and Often
```bash
python scripts/character_tools/template_validator.py templates/my_fighter.json
```

### 3. Use YAML for Readability
YAML is more human-friendly than JSON:
```yaml
name: random
class: Fighter
species: Human
background: Soldier
fighting_style: Defense
weapon_masteries:
  - longsword
  - shield
  - longbow
```

### 4. Check Database for Valid Values
```bash
# List all classes
sqlite3 talekeeper.db "SELECT name FROM classes ORDER BY name"

# List all backgrounds
sqlite3 talekeeper.db "SELECT name FROM backgrounds ORDER BY name"

# List all species
sqlite3 talekeeper.db "SELECT name FROM races ORDER BY name"

# List all feats
sqlite3 talekeeper.db "SELECT name, category FROM feats ORDER BY category, name"
```

## Troubleshooting

### "Invalid class: 'X' not found in database"
- Check spelling (case-sensitive)
- Verify class exists: `sqlite3 talekeeper.db "SELECT name FROM classes"`

### "Invalid feat: 'X' not found in database"
- Check feat spelling
- Some feats may not be in database yet
- List available feats: `sqlite3 talekeeper.db "SELECT name FROM feats WHERE category='O'"`

### "Template has errors"
- Run validator: `python scripts/character_tools/template_validator.py <template>`
- Check error messages for specific issues

### Character created but missing equipment
- Verify equipment_choices match class options
- Check `class_equipment_choices` table for valid values
- Equipment application happens in Step 11 (may fail silently)

## Contributing Templates

Have a cool build? Share it!

1. Create template in `templates/` directory
2. Follow naming convention: `<class>_<build>.json`
3. Add description at top with "notes" field
4. Validate template
5. Test character creation
6. Submit pull request

Example template header:
```json
{
  "name": "random",
  "class": "Fighter",
  "species": "Human",
  "background": "Soldier",
  "notes": "Tank build - high AC, defensive fighting style, great for beginners",
  ...
}
```

## See Also

- [Programmatic Character Creator](../scripts/character_tools/README_PROGRAMMATIC_CREATION.md)
- [Template Validator](../scripts/character_tools/template_validator.py)
- [SRD 5.2.1](../docs/SRD_CC_v5.2.1.md) - Official D&D 2024 rules
