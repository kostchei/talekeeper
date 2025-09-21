# Scalable Subclass Architecture for TaleKeeper

## Overview

TaleKeeper's subclass system is designed to efficiently handle **44+ subclasses across 11 classes** while maintaining:
- Clean code organization
- Fast startup times
- Low memory usage
- Easy navigation for future updates

## Architecture Components

### 1. Modular Directory Structure

```
services/subclasses/
├── __init__.py                     # Package initialization
├── barbarian/
│   ├── __init__.py
│   ├── berserker.py               # ✅ Implemented (legacy location)
│   ├── totem_warrior.py           # 📝 Future
│   ├── ancestral_guardian.py      # 📝 Future
│   └── wild_heart.py              # 📝 Future
├── fighter/
│   ├── __init__.py
│   ├── champion.py                # ✅ Implemented (new structure)
│   ├── battle_master.py           # 📝 Future
│   ├── eldritch_knight.py         # 📝 Future
│   └── psi_warrior.py             # 📝 Future
├── rogue/
│   ├── __init__.py
│   ├── thief.py                   # 📝 Future
│   ├── assassin.py                # 📝 Future
│   ├── arcane_trickster.py        # 📝 Future
│   └── swashbuckler.py            # 📝 Future
└── [7 more class directories...]
```

### 2. SubclassRegistry System

**File**: `services/subclass_registry.py`

Central registry that:
- Maps (class, subclass) pairs to module paths
- Provides lazy loading (modules loaded only when needed)
- Caches loaded definitions for performance
- Supports availability queries

```python
# Example usage
from services.subclass_registry import subclass_registry

# Load a specific subclass
champion = subclass_registry.get_subclass("fighter", "champion")

# Query available subclasses
fighter_subs = subclass_registry.get_available_subclasses("fighter")
```

### 3. Enhanced Feature System

Each subclass is defined using the enhanced feature system:

```python
# Example from Champion
SubclassFeature(
    name="Improved Critical",
    description="Your weapon attacks score a critical hit on a roll of 19 or 20.",
    level=3,
    feature_type=FeatureType.PASSIVE,
    action_cost=ActionCost.NONE,
    mechanics={
        "critical_range_min": 19,
        "applies_to": "weapon_attacks"
    }
)
```

#### Feature Types
- **PASSIVE**: Always active (e.g., Improved Critical)
- **ACTIVATED**: Requires action/bonus action (e.g., Intimidating Presence)
- **TRIGGERED**: Activates under conditions (e.g., Frenzy, Heroic Warrior)
- **REACTION**: Uses reaction (e.g., Retaliation)
- **RESOURCE**: Provides uses of something (e.g., Superiority Dice)

#### Action Costs
- **NONE**: Passive or automatic
- **ACTION**: Full action
- **BONUS_ACTION**: Bonus action
- **REACTION**: Reaction
- **FREE**: No action economy cost

### 4. EnhancedSubclassManager Integration

The manager seamlessly integrates with the registry:

```python
manager = EnhancedSubclassManager()

# Get character's subclass features
features = manager.get_character_subclass_features(character_id, level)

# Use specific abilities
result = manager.use_intimidating_presence(character_id)
```

## Adding New Subclasses

### Step 1: Create the Module

Create a new file in the appropriate class directory:

```python
# services/subclasses/fighter/battle_master.py
from services.enhanced_subclass_manager import (
    SubclassDefinition, SubclassFeature, FeatureType, ActionCost
)

class BattleMasterDefinition:
    @staticmethod
    def create() -> SubclassDefinition:
        return SubclassDefinition(
            class_name="fighter",
            subclass_name="battle_master",
            description="Masters of tactical combat",
            features=[
                SubclassFeature(
                    name="Combat Superiority",
                    description="You learn maneuvers and gain superiority dice",
                    level=3,
                    feature_type=FeatureType.RESOURCE,
                    mechanics={
                        "superiority_dice": "4d8",
                        "maneuvers_known": 3
                    }
                ),
                # ... more features
            ]
        )
```

### Step 2: Register in Registry

Add the mapping to `services/subclass_registry.py`:

```python
SUBCLASS_MODULES = {
    # ... existing entries
    ("fighter", "battle_master"): "services.subclasses.fighter.battle_master.BattleMasterDefinition",
}
```

### Step 3: Test

Create tests following the pattern in `test_scalable_subclass_architecture.py`.

## Performance Characteristics

### Memory Usage
- **Lazy Loading**: Subclass definitions loaded only when accessed
- **Caching**: Once loaded, definitions cached for subsequent use
- **Modular**: Only active subclasses consume memory

### Startup Time
- **Fast**: No upfront loading of all 44 subclasses
- **On-Demand**: Load time distributed across gameplay

### Scalability
- **Linear**: Adding new subclasses doesn't impact existing ones
- **Organized**: Clear structure prevents "god files"
- **Maintainable**: Each subclass in its own module

## Migration Strategy

### Current State
- **Berserker**: Implemented in `enhanced_subclass_manager.py` (legacy)
- **Champion**: Implemented in modular structure (new)

### Future Migration
1. Move Berserker to `services/subclasses/barbarian/berserker.py`
2. Update registry mapping
3. Implement remaining 42 subclasses using modular structure

## Testing

### Architecture Tests
- `test_scalable_subclass_architecture.py`: Validates the overall system
- Tests both legacy (Berserker) and new (Champion) approaches
- Verifies registry functionality and feature type compatibility

### Per-Subclass Tests
- Follow pattern: `test_[class]_[subclass].py`
- Test all features and mechanics
- Validate resource tracking and conditions

## Benefits for 44+ Subclasses

### 1. Organization
- Each subclass in its own file (max ~100 lines each)
- Clear class-based directory structure
- Easy to find and modify specific subclasses

### 2. Team Development
- Multiple developers can work on different subclasses simultaneously
- Minimal merge conflicts
- Clear ownership boundaries

### 3. Maintenance
- Changes to one subclass don't risk breaking others
- Easy to debug issues
- Simple to add new features to specific subclasses

### 4. Performance
- Memory usage scales with active subclasses, not total subclasses
- Fast startup regardless of total subclass count
- Efficient for typical gameplay (1-2 active subclasses per session)

### 5. Future-Proofing
- Easy to add new classes and subclasses
- Structure supports homebrew content
- Modular system allows for plugins/extensions

## Implementation Status

### ✅ Complete
- Registry system
- Enhanced feature definitions
- Modular directory structure
- Champion Fighter implementation
- Berserker Barbarian (legacy location)
- Architecture testing

### 🔄 In Progress
- Stage 2.3: UI Integration for Subclass Features
- Stage 2.4: Feature Activation System

### 📝 Future Work
- Migrate Berserker to modular structure
- Implement remaining 42 subclasses
- Add homebrew subclass support
- Performance optimizations

---

**The architecture is ready to scale to 44+ subclasses while maintaining clean, navigable, and performant code.**