# Best-in-Slot Loot Drop System

## Overview
The TaleKeeper loot system prioritizes dropping Best-in-Slot (BiS) items for the player's class based on rarity tiers. The system ensures players receive optimal gear progression while avoiding duplicate drops.

## System Rules

### Priority Order
1. Check BiS items for player's class at the specified rarity tier
2. Drop BiS items in slot order (1, 2, 3, 4, 5...)
3. Skip any items already in player's inventory
4. When all BiS items of that rarity are owned, fall back to "Other" category
5. Randomly select from "Other" items at that rarity tier
6. Only drop items not currently in player's inventory

### Database Structure
- **Table**: `best_in_slot_items`
- **Columns**:
  - `class_build` - Player class/build variant
  - `rarity` - Common, Uncommon, Rare, Very Rare, Legendary
  - `slot_number` - Priority order (1-5+)
  - `item_name` - Name matching equipment table

### Class Build Matching
- Fighter
- Fighter Dex higher than Str
- Barbarian
- Barbarian Dex + Con under 32
- Barbarian Dex higher than Str
- Rogue
- Paladin
- Cleric
- Wizard
- Warlock
- Other (fallback items for any class)

## Implementation Checklist

### [x] Phase 1: Documentation
- [x] Document system overview
- [x] Define priority rules
- [x] Specify database structure
- [x] Complete implementation plan

### [x] Phase 2: Core Service
- [x] Create `services/loot_drop_service.py`
- [x] Implement `get_character_build()` - determine class variant
- [x] Implement `get_player_inventory()` - fetch owned items
- [x] Implement `get_bis_items_for_rarity()` - query BiS table
- [x] Implement `get_other_items_for_rarity()` - query Other category
- [x] Implement `drop_loot()` - main drop logic
- [x] Implement `cr_to_rarity()` - convert CR to rarity tier

### [x] Phase 3: Integration
- [x] Modify `encounter_panel.py::_roll_equipment_drops()`
- [x] Replace equipment selection with BiS system
- [x] Preserve existing drop chance and character checks
- [x] Handle edge cases (no valid items, equipment not found)

### [x] Phase 4: Testing
- [x] Create test script for BiS drops - `test/test_bis_loot_system.py`
- [x] Test Fighter with 2-3 items at each rarity - PASS
- [x] Test Barbarian with 2-3 items at each rarity - PASS (with missing items)
- [x] Test Wizard with 2-3 items at each rarity - PASS (with missing items)
- [x] Test fallback to "Other" category - PASS
- [x] Verify inventory checking works - PASS
- [x] Verify items save correctly to database - PASS

**Test Results**:
- ✅ BiS priority ordering works correctly
- ✅ Inventory deduplication works (no duplicate drops)
- ✅ Fallback to "Other" category works
- ✅ STR vs DEX Fighter variant detection works
- ✅ Barbarian DEX+CON variant detection works
- ⚠️ Some BiS items missing from equipment table (see below)

**Missing Equipment Items**:
- Half Plate +1, Half Plate +3
- Spear +3, Vicious Spear
- Shortsword of Answering, Iron Flash
- 1st/2nd/3rd/4th Level Scroll
- Hat of Wizardry, Wand of the War Mage +3
- Scroll of Titan Summoning, Deck of Many Things
- Simple Weapons (generic category item)
- Quest items (generic category)

## Implementation Details

### File: `services/loot_drop_service.py`

#### Function: `get_character_build(character_data)`
**Purpose**: Determine the specific BiS class build for a character
**Logic**:
- Check character class
- For Fighter/Barbarian, check DEX vs STR to determine variant
- For Barbarian, check DEX+CON under 32 variant
- Return matching `class_build` string

#### Function: `get_player_inventory(character_id, db_path)`
**Purpose**: Get list of all item names in player's inventory
**Returns**: Set of item names for fast lookup

#### Function: `get_bis_items_for_rarity(class_build, rarity, db_path)`
**Purpose**: Get ordered list of BiS items for class/rarity
**Returns**: List of (slot_number, item_name) tuples, ordered by slot_number

#### Function: `get_other_items_for_rarity(rarity, owned_items, db_path)`
**Purpose**: Get "Other" category items not owned by player
**Returns**: List of item names

#### Function: `drop_loot(character_id, character_data, rarity, db_path)`
**Purpose**: Main entry point - determine and return loot drop
**Returns**: Item name string or None

**Algorithm**:
1. Determine character build variant
2. Get player's inventory
3. Query BiS items for build/rarity
4. Iterate through BiS items in slot order:
   - If item not in inventory, return it
5. If all BiS items owned:
   - Query "Other" items for rarity
   - Filter out owned items
   - Randomly select from remaining
6. Return selected item or None

### Integration Point: `core/combat_engine.py`

**Current loot drop location**: Search for equipment drops after monster defeat
**Replace with**:
```python
from services.loot_drop_service import drop_loot

item_name = drop_loot(character_id, character_data, rarity, db_path)
if item_name:
    # Add to inventory
```

## Edge Cases

1. **No valid items available**: Return None, log warning
2. **Item name mismatch with equipment table**: Log error, skip item
3. **Character class not in BiS table**: Fall back to "Other" category
4. **Multiple builds match character**: Use most specific match (DEX vs STR checks)

## Testing Strategy

1. **Fighter Common Tier Test**:
   - Drop should give: Silvered Weapon (Longsword), Chain Mail, Shield in order
   - After all 3 owned, should drop from "Other" Common items

2. **Barbarian Rare Tier Test**:
   - Should get: Greataxe +2, Bracers of Defense, Shield +2, etc.
   - Verify DEX/STR variant selection works correctly

3. **Fallback Test**:
   - Give player all BiS items for a rarity
   - Verify drops from "Other" category
   - Verify no duplicates

4. **Empty Inventory Test**:
   - New character should get slot 1 BiS item for each rarity tier

## Future Enhancements

- Add quest items to BiS system
- Support multi-class builds
- Dynamic rarity scaling based on character level
- Track item preferences/play style
- Add missing equipment items to database

## Summary

The BiS Loot System successfully prioritizes equipment drops for each character class, ensuring players receive optimal gear progression without duplicates. The system:

1. **Determines character build** - Detects class variants (STR/DEX Fighters, DEX+CON Barbarians)
2. **Checks inventory** - Avoids dropping items already owned
3. **Follows BiS priority** - Drops items in slot order (1, 2, 3...)
4. **Falls back to "Other"** - When all BiS items owned, drops from general pool
5. **Preserves existing mechanics** - Drop chance, CR-to-rarity mapping, inventory saving

**Integration**: Fully integrated into `encounter_panel.py::_roll_equipment_drops()`

**Test Coverage**: Fighter, Fighter DEX, Barbarian, Wizard tested across all 5 rarity tiers