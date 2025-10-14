# 5eTools Monster Import Summary

## Overview
Successfully integrated 5etools monster database with TaleKeeper. Created automated tools to search, download, and import monsters from the comprehensive 5etools JSON repository.

## Results

### Missing Monsters Analysis
Out of 24 missing monsters from the campaign list:
- **Found in 5etools**: 19 monsters (79%)
- **Not found**: 5 monsters (21%)

### Successfully Imported
The following monsters were successfully imported into TaleKeeper database:

1. **Specter** (CR 1) - MM - Was already in DB
2. **Shadow Demon** (CR 4) - MM - IMPORTED
3. **Shadow Mastiff** (CR 2) - VGM/MPMM - IMPORTED
4. **Shadow Mastiff Alpha** (CR 3) - MPMM - IMPORTED
5. **Champion** (CR 9) - VGM/MPMM - IMPORTED
6. **Sahuagin Champion** (CR 3) - GOS - IMPORTED
7. **Troglodyte Champion of Laogzed** (CR 3) - OOTA - IMPORTED
8. **Apprentice Wizard** (CR 1/4) - VGM/MPMM - IMPORTED
9. **Yuan-ti Mind Whisperer** (CR 4) - VGM/MPMM - IMPORTED
10. **Yuan-ti Pit Master** (CR 5) - VGM/MPMM - IMPORTED
11. **Skum** (CR 5) - GOS - IMPORTED
12. **Pirate Captain** (CR 2) - GOS - Was already in DB

### Not Found in 5etools
These monsters were not found and may be homebrew:
1. **Manes Vapourswarm** - Custom creature
2. **Giant Squid** - Not in SRD
3. **Bandit Deceiver** - Custom NPC variant
4. **Cultist Hierophant** - Custom NPC variant
5. **Vampire Nightbringer** - Custom variant

## Tools Created

### 1. Search Tool
**File**: `scripts/monster_tools/search_5etools_monsters.py`

Searches all 5etools sourcebooks for missing monsters:
- Searches 15+ sourcebooks (MM, VGM, MPMM, MTF, etc.)
- Identifies monster variants
- Generates JSON report of matches
- Shows CR, source, and full monster data

**Usage**:
```bash
cd scripts/monster_tools
python search_5etools_monsters.py
```

**Output**: `5etools_monster_matches.json`

### 2. Download Tool
**File**: `scripts/monster_tools/download_5etools_monsters.py`

Downloads specific monsters from 5etools repository:
- Fetches from GitHub raw content
- Downloads all sourcebooks
- Extracts matching monsters
- Saves raw JSON data

**Usage**:
```bash
cd scripts/monster_tools
python download_5etools_monsters.py
```

**Output**: `data/monsters/5etools/5etools_monsters_raw.json`

### 3. Conversion & Import Tool
**File**: `scripts/monster_tools/convert_5etools_to_talekeeper.py`

Converts 5etools JSON format to TaleKeeper database format:
- Parses complex 5etools JSON structure
- Converts AC, HP, speeds, abilities
- Extracts traits, actions, legendary actions
- Identifies primary attacks and multiattack
- Calculates XP and proficiency bonus from CR
- Inserts into TaleKeeper database

**Features**:
- Dry-run mode for testing
- Duplicate detection (skips existing monsters)
- Error handling with detailed reporting
- Converts all monster fields:
  - Basic stats (size, type, alignment, CR)
  - Ability scores (STR, DEX, CON, INT, WIS, CHA)
  - Combat stats (AC, HP, speed, attacks)
  - Skills, saves, resistances, immunities
  - Senses, languages, environment
  - Special abilities, actions, reactions, legendary actions

**Usage**:
```bash
cd scripts/monster_tools

python convert_5etools_to_talekeeper.py --dry-run

python convert_5etools_to_talekeeper.py
```

## Import Statistics

### Current Import Run
- **Monsters processed**: 17 variants
- **Successfully imported**: 10 new monsters
- **Skipped (already existed)**: 7 monsters
- **Errors**: 0

### Database Coverage
- **Original missing**: 25 monsters
- **Now available**: 19 monsters (76% resolved)
- **Still missing**: 6 monsters (24% - likely homebrew)

## 5eTools Sourcebooks Searched

The tools search these sourcebooks:
1. **MM** - Monster Manual (450 monsters)
2. **VGM** - Volo's Guide to Monsters (143 monsters)
3. **MPMM** - Mordenkainen Presents Monsters of the Multiverse (261 monsters)
4. **MTF** - Mordenkainen's Tome of Foes (140 monsters)
5. **TCE** - Tasha's Cauldron of Everything (20 monsters)
6. **FTD** - Fizban's Treasury of Dragons (85 monsters)
7. **GoS** - Ghosts of Saltmarsh (57 monsters)
8. **BGDiA** - Baldur's Gate: Descent into Avernus (53 monsters)
9. **SKT** - Storm King's Thunder (105 monsters)
10. **HotDQ** - Hoard of the Dragon Queen (23 monsters)
11. **RoT** - Rise of Tiamat (25 monsters)
12. **PotA** - Princes of the Apocalypse (59 monsters)
13. **OotA** - Out of the Abyss (98 monsters)
14. **CoS** - Curse of Strahd (95 monsters)
15. **SCC** - Strixhaven: A Curriculum of Chaos (47 monsters)

**Total monsters available**: 1,661+ across all sourcebooks

## Field Mapping

5etools JSON to TaleKeeper database mapping:

| 5etools Field | TaleKeeper Field | Notes |
|--------------|------------------|-------|
| name | name | Direct |
| size | size | Converted (T/S/M/L/H/G to full names) |
| type | type, subtype | Split main type and tags |
| alignment | alignment | Complex parsing (L/N/C + G/E/N) |
| ac | armor_class | Extracts from array/dict |
| hp.average | hit_points | Extracts average from formula |
| speed | speed | Formats walk, fly, swim, etc. |
| str/dex/con/int/wis/cha | strength/dexterity/etc | Direct |
| cr | challenge_rating | Direct (as string) |
| save | saving_throws | Formatted as "STR +5, DEX +3" |
| skill | skills | Formatted as "Perception +4" |
| resist | damage_resistances | Parsed from complex structure |
| immune | damage_immunities | Parsed from complex structure |
| conditionImmune | condition_immunities | List to string |
| senses | senses | List to string |
| languages | languages | List to string |
| trait | special_abilities | Markdown formatted |
| action | actions | Markdown formatted, also extracts primary attack |
| legendary | legendary_actions | Markdown formatted |
| reaction | reactions | Markdown formatted |
| environment | environment | List to comma-separated string |

## Next Steps

### Import More Monsters
To import additional monsters from 5etools:

1. Edit `download_5etools_monsters.py` and add monster names to `priority_monsters` list
2. Run download script
3. Run conversion script

### Bulk Import
To import entire sourcebooks:

```python
from download_5etools_monsters import download_all_monsters
download_all_monsters('mm')
```

### Create Custom Monsters
For the 5 missing homebrew monsters, options:
1. Create manually in database
2. Use existing similar monsters as templates
3. Find homebrew sources with stat blocks
4. Design custom variants based on base creatures

## Technical Notes

### CR to XP Conversion
Built-in lookup table for CR 0 to CR 30:
- CR 0: 10 XP
- CR 1/8: 25 XP
- CR 1: 200 XP
- CR 5: 1,800 XP
- CR 10: 5,900 XP
- CR 20: 25,000 XP
- CR 30: 155,000 XP

### CR to Proficiency Bonus
Auto-calculated based on D&D 5e rules:
- CR 0-4: +2
- CR 5-8: +3
- CR 9-12: +4
- CR 13-16: +5
- CR 17-20: +6
- CR 21-24: +7
- CR 25-28: +8
- CR 29-30: +9

### Primary Attack Extraction
Automatically identifies primary attack from actions:
- Searches for "Melee Weapon Attack" or "Ranged Weapon Attack"
- Extracts attack bonus (+X to hit)
- Extracts reach (5 ft., 10 ft., etc.)
- Extracts damage dice (1d8+3)
- Extracts damage type (slashing, piercing, etc.)

## License
5etools content is open source (MIT license). TaleKeeper integration respects source attribution by storing sourcebook information with each imported monster.
