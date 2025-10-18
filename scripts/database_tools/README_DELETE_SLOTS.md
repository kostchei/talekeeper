# Character Slot Deletion Script

## Overview
Script to delete characters from specified save slots in TaleKeeper database. Removes all associated data including inventory, features, feats, spells, conditions, and class-specific features.

## Location
`scripts/database_tools/delete_character_slots.py`

## Usage

### Delete a range of slots
```bash
python scripts/database_tools/delete_character_slots.py --slots 8-19
```

### Delete specific slots
```bash
python scripts/database_tools/delete_character_slots.py --slots 8,9,10,15
```

### Delete a single slot
```bash
python scripts/database_tools/delete_character_slots.py --slots 5
```

## How It Works

1. **Queries save_slots table** by `slot_number` (not by character UUID)
   - The save_slots table has both `id` (UUID) and `slot_number` (1-20)
   - Characters displayed as "Slot 8" in the UI use `slot_number` field

2. **Joins with characters table** to find actual character data
   - Uses LEFT JOIN since slots can be empty
   - Filters only slots that have characters (`character_id IS NOT NULL`)

3. **Shows preview** of characters to be deleted
   - Lists slot number, character name, class
   - Asks for confirmation before proceeding

4. **Deletes all related data**:
   - `character_inventory` - Items and equipment
   - `character_features` - Class features and abilities
   - `character_feats` - Feats and fighting styles
   - `character_spells` - Known and prepared spells
   - `character_conditions` - Active conditions
   - `character_magical_bonuses` - Magical item bonuses
   - Class-specific tables:
     - `barbarian_features`
     - `fighter_features`
     - `paladin_features`
     - `rogue_features`
     - `cleric_features`
     - `wizard_features`
     - `warlock_features`
     - `warlock_invocations`
   - `characters` - Main character record
   - `save_slots` - The save slot entry itself

5. **Commits transaction** and confirms deletion

## Safety Features

- **Confirmation prompt**: Requires typing "yes" to proceed
- **Preview before delete**: Shows exactly what will be deleted
- **No-op if empty**: Won't delete anything if slots are already empty
- **Transactional**: All deletes happen in one transaction (all or nothing)

## Database Schema Notes

The TaleKeeper database has two key tables for character storage:

### save_slots
- `id` (UUID) - Primary key, referenced by characters.save_slot_id
- `slot_number` (INTEGER 1-20) - Display number shown in UI
- `character_name` - Cached name for quick display
- `character_class` - Cached class for quick display
- `character_level` - Cached level for quick display
- `is_occupied` - Boolean flag
- `last_played` - Timestamp
- `current_location` - Location text

### characters
- `id` (UUID) - Primary key
- `save_slot_id` (UUID) - Foreign key to save_slots.id
- All character stats, equipment, HP, etc.

## Example Output

```
Database path: d:\Code\TaleKeeper\talekeeper.db
Database exists: True

Found 12 character(s) to delete:
  Slot 8: Kael Battleborn (fighter)
  Slot 9: Jenna Strongarm (fighter)
  Slot 10: Cedric Valorheart (fighter)
  Slot 11: Marcus Shieldwall (fighter)
  Slot 12: Kael Battleborn (fighter)
  Slot 13: Jenna Steelhart (fighter)
  Slot 14: Ivan Valorheart (barbarian)
  Slot 15: Galahad (paladin)
  Slot 16: Lyra (cleric)
  Slot 17: Gareth (rogue)
  Slot 18: Fiona (wizard)
  Slot 19: Petra (paladin)

Delete these characters? (yes/no): yes
Deleting Kael Battleborn from slot 8...
Deleting Jenna Strongarm from slot 9...
...
Deleted 12 character(s) and cleared their save slots successfully!
```

## Troubleshooting

### Script says "No characters found" but UI shows characters

This was an issue with the initial implementation. The script now correctly:
- Queries `save_slots` by `slot_number` field
- Joins to `characters` via `save_slot_id`
- The UI displays `slot_number` as "Slot 8", not the UUID

### Characters deleted but still show in UI

- Restart the application to refresh the save slot cache
- The UI caches save slot information on startup

### Want to delete all test characters

```bash
# Delete slots 8-19 (common test range)
python scripts/database_tools/delete_character_slots.py --slots 8-19

# Delete slots 10-20 (keep first 9 slots)
python scripts/database_tools/delete_character_slots.py --slots 10-20
```

## Related Files

- Main database: `talekeeper.db` (root directory)
- Load character dialog: `src/talekeeper/ui/main_window.py` (line 1210)
- Game engine: `src/talekeeper/core/game_engine_sqlite.py`
- Database schema: `database/schema/`

## History

- 2025-10-17: Created script with proper save_slots.slot_number handling
- Fixed issue where script was querying wrong columns
- Added save_slots deletion to fully clear slots
