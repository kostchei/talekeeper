# TaleKeeper Feature System Guide

## Overview

The new feature system provides a scalable, professional implementation of D&D 2024 class features. It handles all types of features including resource management, passive modifiers, triggered effects, and modal states.

## Quick Start

### 1. Setup the System

```bash
cd TaleKeeper
python scripts/setup_feature_system.py --all
```

This will:
- Create required database tables
- Create sample test characters 
- Test the system functionality

### 2. Basic Usage

```python
from core.feature_integration import get_feature_integration

# Get the integration instance
integration = get_feature_integration()

# Initialize features for a new character
success = integration.initialize_character_features(character_id)

# Get available features
features = integration.get_available_features(character_id)

# Use a feature
result = integration.use_feature(character_id, "Second Wind")
```

## Architecture

### Core Components

1. **`core/class_features.py`** - Base feature classes and polymorphic system
2. **`core/feature_definitions.py`** - All feature data for Fighter, Barbarian, Rogue
3. **`core/feature_integration.py`** - Database integration and API

### Feature Types

- **Resource Features** - Limited uses (Second Wind, Rage, Action Surge)
- **Passive Features** - Always active (Fighting Style, Unarmored Defense)  
- **Triggered Features** - Activate on conditions (Sneak Attack, Brutal Strike)
- **Modal Features** - Change character state (Rage mode, Reckless Attack)
- **Action Features** - Use actions/bonus actions/reactions

## Adding New Features

### 1. Define the Feature

Add to `core/feature_definitions.py`:

```python
WIZARD_FEATURES = {
    1: [
        FeatureDefinition(
            name="Arcane Recovery",
            description="Recover spell slots on short rest", 
            level_acquired=1,
            feature_type="resource",
            mechanics={"spell_slot_recovery": "wizard_level_half"},
            recharge="short_rest"
        )
    ]
}
```

### 2. Implement the Logic

Add to `core/class_features.py` if complex behavior is needed:

```python
class ArcaneRecovery(ResourceFeature):
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None):
        # Custom implementation
        pass
```

### 3. Register in Integration

Update `_load_class_features()` in `core/feature_integration.py` to include the new class.

## Integration with UI

### Get Available Features for Buttons

```python
# Get features that can be used right now
features = integration.get_available_features(character_id, {
    "is_combat": True,
    "bonus_action_available": True
})

# Create UI buttons
for feature in features:
    if feature['type'] == 'bonus_action':
        create_button(feature['name'], feature['description'])
```

### Use Features from UI

```python
def on_feature_button_clicked(feature_name: str):
    context = {
        "is_attack": True,
        "weapon": current_weapon,
        "has_advantage": check_advantage()
    }
    
    result = integration.use_feature(character_id, feature_name, context)
    
    if result['success']:
        # Apply effects to UI/game state
        update_character_display(result)
    else:
        show_error(result['reason'])
```

### Rest Processing

```python
def take_short_rest(character_id: str):
    result = integration.process_rest(character_id, "short")
    if result['success']:
        refresh_character_display()
```

## Combat Integration Example

```python
class CombatManager:
    def __init__(self):
        self.integration = get_feature_integration()
    
    def start_turn(self, character_id: str):
        # Get available features for this turn
        context = {
            "is_combat": True,
            "is_start_of_turn": True,
            "bonus_action_available": True,
            "reaction_available": True
        }
        
        features = self.integration.get_available_features(character_id, context)
        self.display_available_features(features)
    
    def make_attack(self, character_id: str, target_id: str):
        # Check for attack-related features
        attack_context = {
            "is_attack": True,
            "is_first_attack": self.is_first_attack,
            "weapon": self.current_weapon,
            "has_advantage": self.check_advantage(),
            "ally_within_5ft": self.check_ally_nearby(target_id)
        }
        
        # Try to use Sneak Attack
        sneak_result = self.integration.use_feature(
            character_id, "Sneak Attack", attack_context
        )
        
        if sneak_result.get('success'):
            extra_damage = sneak_result['extra_damage_dice']
            self.add_damage_to_attack(extra_damage)
```

## Database Schema

The system uses two main tables:

### feature_states
```sql
CREATE TABLE feature_states (
    character_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    feature_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    uses_current INTEGER,
    uses_max INTEGER,
    configuration TEXT,  -- JSON config
    last_used TEXT,
    PRIMARY KEY (character_id, feature_name)
);
```

### Legacy Integration

The system maintains compatibility with existing tables:
- `fighter_features`
- `barbarian_features` 
- `rogue_features`

These are automatically updated when features are used.

## Testing

Run the examples:

```bash
python examples/feature_usage_example.py
```

This demonstrates:
- Combat feature usage
- Attack resolution with Sneak Attack
- Defense with Uncanny Dodge
- Rest processing
- Level up handling

## Performance Notes

- Features are cached in memory during combat
- Database updates are batched where possible
- Passive features are calculated once per character load
- Resource tracking is persistent across sessions

## Extending for More Classes

To add Wizard, Cleric, etc:

1. Add feature definitions to `feature_definitions.py`
2. Create class-specific feature table if needed
3. Update `_initialize_class_features()` method
4. Add any complex features to `class_features.py`

The system is designed to scale to all D&D classes with minimal code changes.