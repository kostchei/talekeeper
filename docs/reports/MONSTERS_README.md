# TaleKeeper Monster Database

## Overview

Complete D&D 2024 SRD monster database with 331 monsters extracted and ready for use with image support and database validation.

## Files Created

### Data Files
1. **[monsters_extracted.json](monsters_extracted.json)** - All 331 monsters in JSON format (608 KB)
2. **[database/seeds/monsters_complete.xml](database/seeds/monsters_complete.xml)** - Complete XML database with image support
3. **[database/seeds/monsters.xml](database/seeds/monsters.xml)** - Sample template with 2 example monsters
4. **[monster_extraction_summary.txt](monster_extraction_summary.txt)** - Human-readable summary
5. **[monsters_sample_with_metadata.json](monsters_sample_with_metadata.json)** - Sample with extraction metadata

### Tools
1. **[tools/generate_monsters_xml.py](tools/generate_monsters_xml.py)** - Convert JSON to XML and validate against database
2. **[tools/load_monsters_to_db.py](tools/load_monsters_to_db.py)** - Import XML monsters into SQLite database

### Documentation
1. **[docs/MONSTERS_XML_GUIDE.md](docs/MONSTERS_XML_GUIDE.md)** - Complete guide to XML format and usage

## Quick Start

### 1. View Monster Data

**JSON Format:**
```bash
# View all monsters
cat monsters_extracted.json

# Search for specific monster
grep -A 20 "\"name\": \"Aboleth\"" monsters_extracted.json
```

**XML Format:**
```bash
# View complete XML database
cat database/seeds/monsters_complete.xml

# View just the template/sample
cat database/seeds/monsters.xml
```

### 2. Generate XML from JSON

```bash
python tools/generate_monsters_xml.py generate monsters_extracted.json database/seeds/monsters_complete.xml
```

### 3. Load Monsters into Database

```bash
# Load all monsters
python tools/load_monsters_to_db.py load database/seeds/monsters_complete.xml

# Specify database path
python tools/load_monsters_to_db.py load database/seeds/monsters_complete.xml talekeeper.db

# List loaded monsters
python tools/load_monsters_to_db.py list
```

### 4. Validate Monster Stats

```bash
# Check if monster exists in database and show stats
python tools/generate_monsters_xml.py validate "Aboleth"
python tools/generate_monsters_xml.py validate "Ancient Red Dragon"
```

## Monster Statistics

### Total Monsters: 331

### Challenge Rating Distribution
- **CR 0:** 29 monsters (rats, frogs, common animals)
- **CR 1/8 to 1/2:** 78 monsters (bandits, small creatures)
- **CR 1-5:** 132 monsters (common adventuring foes)
- **CR 6-10:** 37 monsters (mid-level threats)
- **CR 11-20:** 28 monsters (high-level challenges)
- **CR 21-30:** 12 monsters (legendary threats, includes Tarrasque)

### Creature Types
- **Beast:** 77 (horses, wolves, dinosaurs, giant animals)
- **Monstrosity:** 30 (owlbears, mimics, basilisks)
- **Humanoid:** 21 (bandits, guards, mages)
- **Dragon (Chromatic):** 20 (black, blue, green, red, white - wyrmling to ancient)
- **Dragon (Metallic):** 20 (brass, bronze, copper, gold, silver - wyrmling to ancient)
- **Elemental:** 15 (air, earth, fire, water)
- **Undead:** 12 (zombies, skeletons, vampires, liches)
- **Fiend:** 11 (devils, demons, including Balor and Pit Fiend)
- **Celestial:** 10 (angels, pegasi)
- **Construct:** 10 (golems, animated objects)
- **Other Types:** 105 (aberrations, fey, giants, oozes, plants)

## XML Structure

Each monster in the XML includes:

- **Basic Info:** Name, size, type, alignment
- **Combat Stats:** AC, HP, Initiative, Speed
- **Ability Scores:** STR, DEX, CON, INT, WIS, CHA with modifiers and saves
- **Skills:** Skill bonuses (if any)
- **Resistances/Immunities:** Damage and condition resistances/immunities
- **Senses:** Vision types, passive perception
- **Languages:** Spoken/understood languages
- **CR/XP:** Challenge rating and experience points
- **Traits:** Passive abilities and features
- **Actions:** Standard actions including Multiattack
- **Bonus Actions:** Bonus action options (if any)
- **Reactions:** Reaction options (if any)
- **Legendary Actions:** Legendary action options (if any)
- **Image Path:** Path to monster image (empty by default, ready to fill in)

## Adding Images

1. Create folder: `images/monsters/`
2. Add monster images (PNG, JPG, WEBP)
3. Update XML:
   ```xml
   <image_path>images/monsters/aboleth.png</image_path>
   ```

## Database Schema

Monsters are stored in the `monsters` table with these fields:

```sql
CREATE TABLE monsters (
    id TEXT PRIMARY KEY,                -- unique identifier
    name TEXT NOT NULL,                 -- monster name
    type TEXT,                          -- creature type
    subtype TEXT,                       -- creature subtype
    size TEXT,                          -- size category
    alignment TEXT,                     -- alignment
    armor_class INTEGER,                -- AC
    hit_points INTEGER,                 -- HP
    speed TEXT,                         -- movement speeds
    strength INTEGER,                   -- STR score
    dexterity INTEGER,                  -- DEX score
    constitution INTEGER,               -- CON score
    intelligence INTEGER,               -- INT score
    wisdom INTEGER,                     -- WIS score
    charisma INTEGER,                   -- CHA score
    challenge_rating TEXT,              -- CR
    experience_points INTEGER,          -- XP
    proficiency_bonus INTEGER,          -- proficiency bonus
    saving_throws TEXT,                 -- save bonuses (JSON)
    skills TEXT,                        -- skill bonuses
    damage_resistances TEXT,            -- damage resistances
    damage_immunities TEXT,             -- damage immunities
    condition_immunities TEXT,          -- condition immunities
    senses TEXT,                        -- senses
    languages TEXT,                     -- languages
    special_abilities TEXT,             -- traits (JSON)
    actions TEXT,                       -- actions (JSON)
    legendary_actions TEXT,             -- legendary actions (JSON)
    reactions TEXT,                     -- reactions (JSON)
    environment TEXT                    -- typical environment
);
```

## Example Monsters Included

### Iconic Creatures
- **Tarrasque** (CR 30) - The ultimate challenge
- **Ancient Dragons** (CR 20-24) - All chromatic and metallic varieties
- **Beholder** - Iconic aberration
- **Mind Flayer** - Psionic horror
- **Owlbear** - Classic monstrosity
- **Gelatinous Cube** - Dungeon cleaning service

### Dragons (All Age Categories)
- **Chromatic:** Black, Blue, Green, Red, White
- **Metallic:** Brass, Bronze, Copper, Gold, Silver
- **Ages:** Wyrmling, Young, Adult, Ancient

### Common Foes
- Goblins, Orcs, Kobolds
- Skeletons, Zombies
- Bandits, Guards, Knights
- Wolves, Bears, Giant Spiders

### Elementals
- Air, Earth, Fire, Water Elementals
- Various elemental mephits

### Fiends
- Balor (CR 19)
- Pit Fiend (CR 20)
- Various devils and demons

### Undead
- Vampire (CR 13)
- Lich (CR 21)
- Wraith, Specter, Ghost
- Various skeleton and zombie types

## Usage in TaleKeeper

### Loading Monsters
```python
import xml.etree.ElementTree as ET

tree = ET.parse('database/seeds/monsters_complete.xml')
root = tree.getroot()

for monster in root.findall('monster'):
    name = monster.find('name').text
    cr = monster.find('cr').text
    print(f'{name} (CR {cr})')
```

### Displaying Monster Images
```python
image_path = monster.find('image_path').text
if image_path:
    # Load and display image in UI
    pixmap = QPixmap(image_path)
    label.setPixmap(pixmap)
```

### Validating Stats
```python
from tools.generate_monsters_xml import validate_monster_against_db

validate_monster_against_db('Aboleth', 'talekeeper.db')
```

## Custom Monsters

Add custom monsters to XML:

```xml
<monster id="custom_monster" validate_stats="false" source="custom">
  <name>Volcanic Drake</name>
  <image_path>images/monsters/custom/volcanic_drake.png</image_path>
  <!-- Custom stats here -->
</monster>
```

## Next Steps

1. **Add Images:** Populate `image_path` fields with actual images
2. **Load to Database:** Run `load_monsters_to_db.py` to import all monsters
3. **Integrate UI:** Create monster browser in TaleKeeper
4. **Encounter Builder:** Use monster data for encounter generation
5. **Combat Integration:** Link monsters to combat system

## File Locations Summary

```
TaleKeeper/
├── monsters_extracted.json              # Source JSON (331 monsters)
├── monster_extraction_summary.txt       # Human-readable summary
├── monsters_sample_with_metadata.json   # Sample with metadata
├── MONSTERS_README.md                   # This file
├── database/
│   └── seeds/
│       ├── monsters.xml                 # Template (2 examples)
│       └── monsters_complete.xml        # Full database (331 monsters)
├── tools/
│   ├── generate_monsters_xml.py         # JSON to XML converter
│   └── load_monsters_to_db.py          # XML to database loader
├── docs/
│   └── MONSTERS_XML_GUIDE.md           # Complete XML guide
└── images/                              # (create this)
    └── monsters/                        # Monster images go here
```

## Credits

Monster data extracted from D&D 2024 System Reference Document v5.2.1
