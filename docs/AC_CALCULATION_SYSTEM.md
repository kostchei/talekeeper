# AC Calculation System

## Overview
The AC (Armor Class) calculation system is implemented across multiple components to provide real-time, accurate AC calculations based on equipped armor, shields, and character stats.

## Architecture

### 1. Equipment Service (`services/equipment.py`)
**Responsibility**: Central database-backed equipment data and AC calculation logic.

#### Key Methods:
- `get_armor_ac(armor_name, dex_modifier)` - Calculates AC for specific armor with D&D rules
- `get_shield_ac_bonus(shield_name)` - Returns shield AC bonus (typically +2)
- `get_item(item_name)` - Retrieves equipment data from database

#### AC Logic:
```python
# Light Armor: AC = base_ac + full_dex_modifier
# Medium Armor: AC = base_ac + min(dex_modifier, dex_bonus_max)  
# Heavy Armor: AC = base_ac + 0 (no dex bonus)
```

### 2. Equipment Panel (`equipment_layout/equipment_panel.py`)
**Responsibility**: Equipment management and real-time AC calculation.

#### Key Methods:
- `_calculate_armor_class()` - Combines armor + shield + dex for total AC
- `_update_stats_display()` - Triggers AC recalculation on equipment changes

#### Signals:
- `ac_changed(int)` - Emitted whenever AC changes from equipment

#### Flow:
1. User equips/unequips armor/shield
2. `_update_stats_display()` called
3. `_calculate_armor_class()` calculates new AC using equipment service
4. `ac_changed` signal emitted with new AC value

### 3. Main Window (`ui/main_window.py`)
**Responsibility**: Coordinates AC updates between equipment panel and character sheet.

#### Signal Connection:
```python
self.equipment_panel.ac_changed.connect(self._on_ac_changed)
```

#### AC Update Handler:
```python
def _on_ac_changed(self, new_ac):
    """Handle AC change from equipment panel - update character sheet display."""
    self.character_sheet.update_ac(new_ac)
    self.log_panel.log_info(f"AC updated to {new_ac}")
```

### 4. Character Sheet (`character_sheet/character_panel.py`)
**Responsibility**: Displays current AC value.

#### Key Methods:
- `update_ac(new_ac)` - Updates AC display when equipment changes
- `load_character_data()` - Sets initial AC from character data

## Data Flow

```
Equipment Change (Equip/Unequip Armor)
    ↓
Equipment Panel: _update_stats_display()
    ↓
Equipment Panel: _calculate_armor_class()
    ↓ (queries database)
Equipment Service: get_armor_ac() + get_shield_ac_bonus()
    ↓ (returns calculated AC)
Equipment Panel: ac_changed.emit(new_ac)
    ↓ (signal)
Main Window: _on_ac_changed()
    ↓
Character Sheet: update_ac()
    ↓
AC Display Updated
```

## Database Integration

### Equipment Table Schema:
```sql
CREATE TABLE equipment (
    armor_class INTEGER,        -- Base AC for armor
    armor_type TEXT,           -- 'light', 'medium', 'heavy'  
    dex_bonus_max INTEGER,     -- Max dex bonus (NULL = unlimited)
    -- ... other columns
);
```

### Example Data:
```sql
-- Chain Mail (Heavy Armor)
armor_class: 16, armor_type: 'heavy', dex_bonus_max: 0

-- Breastplate (Medium Armor)  
armor_class: 14, armor_type: 'medium', dex_bonus_max: 2

-- Studded Leather (Light Armor)
armor_class: 12, armor_type: 'light', dex_bonus_max: NULL
```

## Key Benefits

1. **Database-Driven**: All armor properties stored in database, not hardcoded
2. **Real-Time**: AC updates immediately when equipment changes
3. **Accurate D&D Rules**: Proper light/medium/heavy armor mechanics
4. **Reusable**: Works for any equipment source (character creation, treasure, shops)
5. **Extensible**: Easy to add new armor types or special rules
6. **Separation of Concerns**: Equipment logic separated from UI display

## Usage Examples

### Character Creation:
- User selects "Chain Mail" during character creation
- Equipment service calculates AC = 16 (heavy armor, no dex bonus)
- Character created with correct AC

### Equipment Change:
- User drags "Breastplate" to armor slot  
- Equipment panel calculates AC = 14 + min(dex_mod, 2)
- Character sheet display updates automatically
- Works same way for treasure drops, shop purchases, etc.

### Shield Addition:
- User equips shield in off-hand slot
- Equipment panel adds +2 AC from shield
- Total AC = armor_ac + shield_bonus
- Character sheet shows updated total

## Future Extensions

1. **Magical Armor**: Add `magic_ac_bonus` column to equipment table
2. **Class Features**: AC bonuses from Barbarian Unarmored Defense, Monk, etc.
3. **Temporary Bonuses**: Spell effects, cover bonuses
4. **Equipment Sets**: Set bonuses for matching armor pieces