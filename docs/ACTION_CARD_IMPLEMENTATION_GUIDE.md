# Action Card Implementation Guide

## Overview
This guide explains how to add class-specific action cards to the action panel in TaleKeeper. Action cards appear in the bottom-left panel and represent abilities characters can use in combat and exploration.

## Architecture

### Key Files
- **`action_cards/action_panel.py`** - Main action panel with card generation logic
- **`action_cards/action_card.py`** - Individual action card widget
- **`services/action_registry.py`** - Action definitions and metadata
- **`models/action_economy.py`** - Action types and economy rules

### Card Generation Flow
1. **Static Cards** (lines 310-340): Universal actions like Dodge, Dash, Hide
2. **Weapon Cards** (line 343, `_create_weapon_cards()`): Main/off-hand weapon attacks
3. **Feature Cards** (line 5679, `_create_feature_cards()`): Class-specific abilities

## Adding a New Class-Specific Action Card

### Step 1: Add ActionType Enum
In `action_cards/action_panel.py`, find the `ActionType` class (~line 85):

```python
class ActionType(str, Enum):
    # ... existing types ...
    CHANNEL_DIVINITY = "channel_divinity"  # Add your new type
```

### Step 2: Add Card Generation Logic
In `_create_feature_cards()` method (~line 453), add your class check:

```python
def _create_feature_cards(self):
    """Create action cards for character features."""

    # Example: Channel Divinity for Paladins level 3+
    if (self.character_context
        and self.character_context.get('class_id', '').lower() == 'paladin'
        and self.character_context.get('level', 1) >= 3):

        card = ActionCard(
            ActionType.CHANNEL_DIVINITY,  # Type
            "⚡",                          # Icon
            "Channel Divinity",            # Name
            "Channel divine energy"        # Description
        )
        card.action_triggered.connect(self._trigger_action)
        card.action_hovered.connect(self._action_hovered)
        self.action_cards[ActionType.CHANNEL_DIVINITY] = card
```

### Step 3: Add Action Handler
In `_trigger_action()` method (~line 1680), add the case:

```python
def _trigger_action(self, action: ActionCard):
    """Handle action card triggers."""
    if action.action_type == ActionType.CHANNEL_DIVINITY:
        self._use_channel_divinity()
    # ... other cases ...
```

### Step 4: Implement the Action Method
Create a method to handle the action's logic:

```python
def _use_channel_divinity(self):
    """Use Channel Divinity with proper dialog."""
    # Check if character has uses remaining
    if not self._has_channel_divinity_uses():
        return

    try:
        # Get character data
        character_id = self.character_context.get('id', '')
        character_level = self.character_context.get('level', 1)

        # Show dialog or apply effect
        dialog = ChannelDivinityDialog(...)
        dialog.exec()

    except Exception as e:
        print(f"Error using Channel Divinity: {e}")
```

### Step 5: Add Database Support (if needed)
If your ability uses resources, add tracking to the appropriate table:

```sql
-- Example: paladin_features table
ALTER TABLE paladin_features
ADD COLUMN channel_divinity_uses_current INTEGER DEFAULT 0;
ADD COLUMN channel_divinity_uses_max INTEGER DEFAULT 2;
```

## Pattern Examples by Class

### Paladin (Resource-Based with Dialog)
```python
# Card creation (line ~518)
if (self.character_context.get('class_id', '').lower() == 'paladin'
    and self.character_context.get('level', 1) >= 3):
    card = ActionCard(ActionType.CHANNEL_DIVINITY, "⚡", "Channel Divinity", "...")
    self.action_cards[ActionType.CHANNEL_DIVINITY] = card

# Handler
def _use_channel_divinity(self):
    if not self._has_channel_divinity_uses():
        return
    dialog = ChannelDivinityDialog(...)
    dialog.exec()
```

### Fighter (Simple Resource)
```python
# Card creation (line ~467)
second_wind_feature = self._get_feature_data('Second Wind')
if second_wind_feature:
    card = ActionCard(ActionType.SECOND_WIND, "💨", "Second Wind", "...")
    card.feature_data = second_wind_feature
    self.action_cards[ActionType.SECOND_WIND] = card

# Handler
def _use_second_wind(self):
    resource_service.use_resource(character_id, 'Second Wind', 1)
    healing = roll_dice(f"1d10+{level}")
    # Apply healing...
```

### Barbarian (Toggle State)
```python
# Card creation (line ~487)
rage_feature = self._get_feature_data('Rage')
if rage_feature and self._has_rage_uses():
    card = ActionCard(ActionType.RAGE, "[RAGE]", "Rage", "...")
    self.action_cards[ActionType.RAGE] = card

# Handler
def _use_rage(self):
    # Toggle rage state
    barbarian_service.activate_rage(character_id)
    # Update UI...
```

### Rogue (Passive/Always Available)
```python
# Card creation (line ~539)
if (self.character_context.get('class_id', '').lower() == 'rogue'
    and self.character_context.get('subclass_id') == 'thief'
    and level >= 3):
    card = ActionCard(ActionType.FAST_HANDS, "🤲", "Fast Hands", "...")
    self.action_cards[ActionType.FAST_HANDS] = card
```

## Common Patterns

### Check if Feature Exists
```python
feature_data = self._get_feature_data('Feature Name')
if feature_data:
    # Feature exists in character_features table
```

### Check Class and Level
```python
if (self.character_context
    and self.character_context.get('class_id', '').lower() == 'wizard'
    and self.character_context.get('level', 1) >= 5):
```

### Check Subclass
```python
if 'devotion' in self.character_context.get('subclass_id', '').lower():
```

### Resource Tracking
```python
def _has_uses_remaining(self, resource_name: str) -> bool:
    resource_service = ResourceService()
    resource = resource_service.get_resource(character_id, resource_name)
    return resource and resource['uses_remaining'] > 0
```

## Database Requirements

### Option 1: Use character_features Table
Add features during character creation/level-up:

```sql
INSERT INTO character_features
(character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES
('char_id', 'Channel Divinity', 'action', 'short_rest', 3, 'Channel divine energy');
```

### Option 2: Use Class-Specific Table
Create/use class-specific tracking:

```python
# paladin_features table
sqlite3 talekeeper.db "
INSERT INTO paladin_features
(character_id, level, sacred_oath, channel_divinity_uses_max)
VALUES ('char_id', 3, 'devotion', 2)
"
```

## Debugging Checklist

If your action card doesn't appear:

1. **Is `_create_feature_cards()` being called?**
   - Check debug output: `[DEBUG] _create_feature_cards() called!`
   - Called from `load_character_equipment()` at line 5679

2. **Is your condition check correct?**
   ```python
   print(f"Class: {self.character_context.get('class_id')}")
   print(f"Level: {self.character_context.get('level')}")
   print(f"Subclass: {self.character_context.get('subclass_id')}")
   ```

3. **Is the ActionType enum defined?**
   - Check `class ActionType` has your new type

4. **Is the card being added to `self.action_cards`?**
   - Add debug: `print(f"Added card: {ActionType.YOUR_TYPE}")`

5. **Is `_update_visible_cards()` being called?**
   - Called after `_create_feature_cards()` at line 5682

## Testing

After adding a new action card:

1. **Restart the application** - Action cards are created when character loads
2. **Check the action panel** - Bottom-left panel should show your card
3. **Click the card** - Verify the handler is triggered
4. **Check resource tracking** - If applicable, verify uses decrement
5. **Test rest mechanics** - Verify resources restore on short/long rest

## Common Issues

### Card appears but does nothing
- Check `_trigger_action()` has your ActionType case
- Verify the handler method exists and is called

### Card doesn't appear at all
- Verify character meets all conditions (class, level, subclass)
- Check if `character_context` is populated
- Add debug prints in your condition check

### Wrong icon/description
- Icons use emoji or `[BRACKET]` notation
- Description appears in tooltip on hover

### Resource tracking broken
- Verify database table has correct columns
- Check resource service is being called
- Test restoration on rest

## Future Improvements

Consider these patterns for scalability:

1. **Registry-Based System**: Move card definitions to a central registry
2. **Data-Driven Cards**: Load card metadata from JSON/database
3. **Unified Resource System**: Standardize resource tracking across all classes
4. **Card Visibility Rules**: Separate condition checks from card creation

## Examples in Codebase

Reference these existing implementations:
- **Channel Divinity (Paladin)**: Lines 518-524, 7555-7596
- **Second Wind (Fighter)**: Lines 467-476, 895-920
- **Rage (Barbarian)**: Lines 487-495
- **Fast Hands (Rogue Thief)**: Lines 544-550
- **Holy Nimbus (Devotion Paladin)**: Lines 527-536

---

**Last Updated**: 2025-10-05
**Maintainer**: TaleKeeper Development Team
