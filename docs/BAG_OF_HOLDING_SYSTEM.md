# Bag of Holding System

## Overview
The Bag of Holding system automatically manages gold and treasure storage based on D&D 2024 SRD rules. When characters find large amounts of treasure, the system intelligently converts excess coins into gems and art objects, and stores heavy items in the Bag of Holding if available.

## Features

### 1. Automatic Gold Storage
- Gold over 10 lb automatically stored in Bag of Holding (if character has one)
- Gold under 10 lb stored on character's person
- Weight calculated as: coins / 50 = pounds (D&D standard)

### 2. Treasure Conversion
For treasure drops over 1,000 GP, the system automatically converts a portion into:
- **Gems** (25% chance): 10,000 GP per pound
  - Value ranges from 10 GP to 5,000 GP per gem
  - Weight scales with value (higher value = heavier)
  - Based on monster CR tier

- **Art Objects** (50% chance): Variable value and weight
  - Small items: 0.5 lb (jewelry, carvings)
  - Medium items: 1.0-1.5 lb (chalices, statues)
  - Large items: 2.0 lb (tapestries, armor)
  - Value ranges from 25 GP to 2,500 GP

### 3. CR-Based Treasure Quality
Treasure quality scales with monster CR:
- **CR 0-4**: Gems 10-100 GP, Art 25-250 GP
- **CR 5-10**: Gems 50-500 GP, Art 250-750 GP
- **CR 11-16**: Gems 100-1000 GP, Art 750-2500 GP
- **CR 17+**: Gems 500-5000 GP, Art 750-2500 GP

## Database Schema

### New Columns in character_inventory
```sql
stored_in_bag INTEGER DEFAULT 0         -- 0 = on person, 1 = in bag
treasure_type TEXT DEFAULT 'standard'   -- 'coins', 'gem', 'art', 'standard'
unit_value_gp REAL DEFAULT NULL         -- Individual item value for stacking
```

## API Reference

### GameEngineSQLite Methods

#### character_has_bag_of_holding(character_id: str) -> bool
Check if character has a Bag of Holding in inventory.

#### get_bag_of_holding_weight(character_id: str) -> float
Calculate total weight stored in Bag of Holding.
- Returns weight in pounds
- Max capacity: 500 lb per SRD

#### add_gold_to_character_sync(character_id, gold_amount, store_in_bag=None) -> bool
Add gold to character with automatic bag storage.
- `store_in_bag=None`: Auto (bag if available and > 10 lb)
- `store_in_bag=True`: Force store in bag
- `store_in_bag=False`: Store on person

#### add_treasure_to_character_sync(character_id, treasure_item, store_in_bag=None) -> bool
Add gem or art object to character inventory.
- Automatically stores in bag if character has one
- Tracks individual item value for selling

### TreasureGenerator Methods

#### generate_gem(min_value, max_value) -> Dict
Generate a random gem within value range.
Returns dict with: name, value_gp, weight_lb, treasure_type, description

#### generate_art_object(min_value, max_value) -> Dict
Generate a random art object within value range.
Returns dict with: name, value_gp, weight_lb, treasure_type, description

#### convert_gold_to_treasure(gold_amount, cr) -> Tuple[List[Dict], int]
Convert gold into gems and art objects.
Returns: (treasure_items, remaining_coins)

#### should_use_treasure_conversion(gold_amount, threshold=1000) -> bool
Check if gold amount warrants conversion to treasure items.

## Usage Examples

### Adding Gold with Automatic Conversion
```python
from talekeeper.core.game_engine_sqlite import GameEngineSQLite

game_engine = GameEngineSQLite('talekeeper.db')
character_id = 'char_123'

# Small amount - stored as coins
game_engine.add_gold_to_character_sync(character_id, 100)  # 2 lb, on person

# Large amount - auto-stored in bag
game_engine.add_gold_to_character_sync(character_id, 2000)  # 40 lb, in bag
```

### Treasure Drop with Conversion
```python
from talekeeper.ui.encounter_pane.encounter_panel import EncounterPanel

# In encounter_panel._add_treasure_with_conversion():
# Large treasure (3000 GP from CR 8 encounter)
# System automatically:
# 1. Converts ~75% to gems/art (2250 GP worth)
# 2. Stores items in bag (3-5 lb total)
# 3. Keeps 750 GP as coins (15 lb in bag)
```

### Manual Treasure Addition
```python
from talekeeper.services.treasure_generator import TreasureGenerator

# Generate specific treasure
gem = TreasureGenerator.generate_gem(100, 1000)
art = TreasureGenerator.generate_art_object(250, 2500)

# Add to character
game_engine.add_treasure_to_character_sync(character_id, gem)
game_engine.add_treasure_to_character_sync(character_id, art)
```

## Bag of Holding Rules (SRD 2024)

### Capacity
- Volume: 64 cubic feet (roughly 2ft x 2ft x 4ft)
- Weight limit: 500 pounds
- Bag itself weighs: 5 pounds (regardless of contents)

### Retrieval
- Requires a Utilize action to retrieve items
- Items spill forth unharmed if turned inside out

### Dangers
- Overloading, piercing, or tearing destroys bag
- Contents scattered in Astral Plane if destroyed
- Placing inside another extradimensional space = catastrophic destruction

## Implementation Notes

### Weight Tracking
- Coins stored with total weight (quantity / 50)
- Gems and art stored with individual weight
- Weight updates on gold additions (UPDATE query includes weight_lb)

### Treasure Balance
- Conversion algorithm maintains total value
- Randomization prevents predictable patterns
- Remaining coins ensure exact GP amounts

### UI Integration
- Equipment panel shows bag contents separately
- Combat log indicates storage location
- Treasure notifications show weight and location

## Testing

Run the test script to verify functionality:
```bash
python scripts/test_bag_of_holding.py
```

Tests verify:
1. Gem and art generation
2. Gold to treasure conversion
3. Automatic bag storage
4. Weight calculations
5. Inventory tracking

## Future Enhancements

Potential improvements:
- UI panel for bag management
- Transfer items between bag and person
- Capacity warnings
- Encumbrance tracking
- Sell/trade treasure items
- Visual inventory display
