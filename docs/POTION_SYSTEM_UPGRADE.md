# Potion System Upgrade

## Overview
Enhanced the healing potion system to automatically use the best available potion and seamlessly fall back to lesser potions as they are consumed.

## Changes Made

### 1. Potion Priority System
Implemented a priority ranking for all healing potion types:
1. **Potion of Supreme Healing** - 10d4+20 HP (Very Rare, 20,000 gp)
2. **Potion of Superior Healing** - 8d4+8 HP (Rare, 2,000 gp)
3. **Potion of Greater Healing** - 4d4+4 HP (Uncommon, 200 gp)
4. **Potion of Healing** - 2d4+2 HP (Common, 50 gp)

### 2. Smart Potion Selection
The bonus action "Use Potion" card now:
- Automatically selects the best available potion from inventory
- Displays the potion type and healing amount on the card
- Shows total count of all healing potions
- Example: "Drink Supreme Healing (10d4+20 HP) - 5 potions"

### 3. Automatic Fallback
When a potion is consumed:
- The system automatically checks for the next best available potion
- Updates the action card display immediately
- No manual intervention required

### 4. Accurate Healing Calculations
Fixed healing calculations to use the correct dice formula:
- **OLD**: All potions healed 2d4+4 (hardcoded)
- **NEW**: Each potion uses its proper healing formula

### 5. Detailed Combat Logging
Enhanced combat log messages:
- Shows which potion type was used
- Displays individual dice rolls
- Example: "[POTION] Used Potion of Supreme Healing: 10d4([4, 3, 2, 4, 1, 3, 4, 2, 3, 4]) + 20 = 50 healing"

## Technical Implementation

### Modified Files
- `src/talekeeper/ui/action_cards/action_panel.py`
  - `_use_healing_potion()` - Uses dynamic potion selection
  - `_get_best_healing_potion()` - NEW: Returns best available potion with stats
  - `_has_healing_potion()` - Updated to check all potion types
  - `_consume_healing_potion()` - Now accepts potion name parameter
  - `_update_potion_card()` - Displays best potion info

### Database Compatibility
All four potion types are already defined in the database:
- ID 50: Potion of Healing
- ID 188: Potion of Greater Healing
- ID 207: Potion of Superior Healing
- ID 228: Potion of Supreme Healing

### Testing
Created comprehensive test suite:
- `tests/test_potion_simple.py` - Validates priority selection and fallback
- All tests passing

## Usage

### In-Game
1. Acquire any healing potions (Healing, Greater, Superior, or Supreme)
2. During combat, the bonus action card will show the best available potion
3. Click "Use Potion" to consume the best potion
4. Card automatically updates to show next best potion

### Example Progression
```
Initial inventory:
- 2x Potion of Healing
- 1x Potion of Greater Healing
- 1x Potion of Supreme Healing

Card shows: "Drink Supreme Healing (10d4+20 HP) - 4 potions"
Use potion -> Consumes Supreme

Card shows: "Drink Greater Healing (4d4+4 HP) - 3 potions"
Use potion -> Consumes Greater

Card shows: "Drink Healing (2d4+2 HP) - 2 potions"
```

## Benefits
1. **Optimal Resource Usage**: Always uses the best healing when needed
2. **Automatic Management**: No manual potion selection required
3. **Clear Visibility**: Action card shows what will be used
4. **Accurate Mechanics**: Correct D&D 2024 healing formulas
5. **Smart Fallback**: Seamlessly transitions between potion tiers

## Future Enhancements (Optional)
- Add UI option to manually select potion type (if player wants to save better potions)
- Implement "smart healing" mode (use minimum needed potion based on damage taken)
- Add potion rarity indicators in inventory panel
- Track potion usage statistics

## Backward Compatibility
- Old characters with "Potion of Healing" in inventory still work
- Database schema unchanged
- Existing save games compatible
- No migration required
