# Enhanced Systems Guide for TaleKeeper

## Overview

TaleKeeper now includes three major enhanced systems that implement D&D 2024 rules with full mechanical integration:

1. **Condition System** - Complete D&D 2024 condition support
2. **Scalable Subclass Architecture** - Modular system for 44+ subclasses
3. **Action Economy Enforcement** - Full turn-based action validation

## Condition System

### What It Does
The condition system implements all D&D 2024 conditions with proper mechanical effects:
- Advantage/disadvantage on attacks and saves
- Movement speed modifications
- Action restrictions
- Automatic condition saves
- Condition immunity tracking

### Key Features
- **Condition Types**: All 15 D&D 2024 conditions (Blinded, Charmed, Deafened, etc.)
- **Duration Management**: Rounds, minutes, hours, save-ends, permanent
- **Exhaustion Levels**: 1-6 with cumulative effects
- **Immunity System**: Barbarian Mindless Rage, etc.
- **Integration**: Works with Danger Sense, combat mechanics, UI display

### Developer Usage
```python
from services.condition_manager import ConditionManager, ConditionType, ActiveCondition

# Apply a condition
manager = ConditionManager()
condition = ActiveCondition(
    condition_type=ConditionType.STUNNED,
    source="Hold Person spell",
    duration_type="save_ends",
    save_dc=15,
    save_ability="wisdom"
)
manager.add_condition(character_id, condition)

# Check for specific effects
if manager.has_incapacitating_condition(character_id):
    # Block Danger Sense, prevent actions, etc.
```

### UI Integration
- Conditions appear on character sheet with tooltips
- Combat log shows condition applications/removals
- Action cards are disabled when conditions prevent actions
- Automatic saves happen at turn start/end

### Testing
```bash
cd test && python test_stage_1_4_integration.py
```

## Scalable Subclass Architecture

### What It Does
A modular system designed to handle all D&D 2024 subclasses efficiently:
- **44+ subclasses** across 11 classes
- **Lazy loading** for memory efficiency
- **Feature type system** (passive, activated, triggered, reaction)
- **Resource tracking** for limited-use features
- **UI integration** with feature panels

### Architecture Design
```
services/
├── enhanced_subclass_manager.py  # Core manager
├── subclass_registry.py         # Registration system
└── subclasses/                  # Modular subclass definitions
    ├── barbarian/
    │   ├── berserker.py
    │   ├── totem_warrior.py
    │   └── ...
    ├── fighter/
    │   ├── champion.py
    │   ├── battle_master.py
    │   └── ...
    └── ...
```

### Feature Types
- **Passive**: Always active (Brutal Critical)
- **Activated**: Player triggers (Intimidating Presence)
- **Triggered**: Automatic under conditions (Frenzy with Reckless Attack)
- **Reaction**: Response to events (Retaliation)

### Developer Usage
```python
from services.enhanced_subclass_manager import EnhancedSubclassManager

manager = EnhancedSubclassManager()

# Get all features for a character's subclass
features = manager.get_character_subclass_features(character_id, "barbarian")

# Check if feature is available
available = manager.is_feature_available(character_id, "intimidating_presence")

# Use a feature (consumes resources)
result = manager.use_subclass_feature(character_id, "intimidating_presence")
```

### Example: Creating a New Subclass
```python
# services/subclasses/fighter/eldritch_knight.py
from services.enhanced_subclass_manager import SubclassDefinition, SubclassFeature

def get_eldritch_knight_definition():
    return SubclassDefinition(
        id="eldritch_knight",
        name="Eldritch Knight",
        class_id="fighter",
        features=[
            SubclassFeature(
                name="Spellcasting",
                description="You learn spells from the wizard spell list",
                level=3,
                feature_type="passive"
            ),
            SubclassFeature(
                name="War Magic",
                description="Cast a cantrip and make a weapon attack",
                level=7,
                feature_type="activated",
                action_cost="action"
            )
        ]
    )
```

### Testing
```bash
cd test && python test_scalable_subclass_architecture.py
cd test && python test_stage_2_1_subclass_definitions.py
```

## Action Economy Enforcement

### What It Does
Enforces D&D 2024 action economy rules in combat:
- **One action per turn** (unless Action Surge)
- **One bonus action per turn**
- **One reaction per round**
- **Movement allocation**
- **Resource consumption tracking**

### Key Components
- **Action Registry**: Defines all class actions and their costs
- **Economy Tracking**: Monitors what's been used each turn
- **Validation Layer**: Prevents invalid actions
- **UI Integration**: Shows availability on action cards

### Developer Usage
```python
from models.action_economy import CombatActionEconomy, ActionEconomyType

# Create combat tracker
combat = CombatActionEconomy(combat_session_id="encounter_1")
combat.add_combatant(character_id, "Hero", "character")

# Use an action
success = combat.use_action(character_id, ActionEconomyType.ACTION, "Attack")

# Check availability
state = combat.get_combatant_state(character_id)
can_use_bonus = state.bonus_action_available
```

### Action Types
- **Action**: Main action (Attack, Cast a Spell, Dash, etc.)
- **Bonus Action**: Secondary action (Rage, Healing Word, etc.)
- **Reaction**: Response action (Opportunity Attack, Shield spell, etc.)
- **Free Action**: No cost (Draw weapon, speak, etc.)
- **Movement**: Distance-based (30ft normal speed)

### UI Features
- Action cards show economy cost badges
- Disabled state when economy is exhausted
- Clear reason messages for unavailable actions
- Economy resets at turn/round boundaries

### Testing
```bash
cd test && python test_action_economy_enforcement.py
```

## Configuration System

### What It Does
Centralized configuration for all enhanced systems:
- **Performance settings** for optimization
- **Debug options** for development
- **Feature toggles** for system control
- **UI preferences** for display

### Configuration File
`talekeeper_config.json` (auto-created):
```json
{
  "performance": {
    "enable_action_card_caching": true,
    "condition_cache_size": 100,
    "lazy_load_subclass_features": true
  },
  "debug": {
    "log_database_queries": false,
    "show_performance_metrics": false,
    "enable_test_commands": true
  },
  "features": {
    "use_enhanced_subclass_manager": true,
    "enable_condition_immunity_optimization": true,
    "enable_enhanced_monster_logging": true
  },
  "ui": {
    "theme": "dark",
    "enable_animations": true,
    "show_advanced_tooltips": true
  }
}
```

### Developer Usage
```python
from core.config import get_config, is_feature_enabled

config = get_config()

# Check feature status
if is_feature_enabled("use_enhanced_subclass_manager"):
    # Use enhanced system
    pass

# Modify settings
config.set_debug_setting("log_database_queries", True)

# Enable preset modes
config.enable_developer_mode()  # All debug options on
config.enable_performance_mode()  # Optimized for speed
```

## Debug Commands

### What It Does
In-application debug utilities for development and testing:
- **Performance monitoring** with timing metrics
- **System state inspection** for debugging
- **Test utilities** for feature validation
- **Configuration management** for settings

### Available Commands
```
Performance Analysis:
  /debug performance - Show timing metrics
  /debug memory - Display memory usage
  /debug queries - Toggle database query logging
  /debug cache - Show cache statistics

System State:
  /debug conditions <character> - Show active conditions
  /debug economy <character> - Display action economy state
  /debug features <character> - List available features
  /debug combat - Show combat state

Testing Utilities:
  /debug test_rage <character> - Test rage mechanics
  /debug test_conditions <character> <type> - Apply test condition
  /debug test_economy - Reset action economy
  /debug test_features <character> - Reload character features

Configuration:
  /debug config - Show current config
  /debug config set <section> <setting> <value> - Modify config
  /debug dev_mode - Enable developer settings
  /debug perf_mode - Enable performance settings
```

### Usage Example
```
/debug conditions barbarian_test
=== Active Conditions for barbarian_test ===
- CHARMED: Enchantment spell (3 rounds)
- RAGING: Barbarian feature (Permanent)

/debug test_rage barbarian_test
=== Testing Rage for barbarian_test ===
✓ Rage prerequisites checked
✓ Resource consumption validated
✓ Condition immunity applied
✓ Damage bonuses activated
Test completed successfully
```

### Performance Monitoring
```python
from core.debug_commands import log_performance_metric

# Log timing data
start = time.time()
# ... some operation ...
duration_ms = (time.time() - start) * 1000
log_performance_metric("condition_check", duration_ms)
```

## Integration Between Systems

### Condition + Subclass Integration
- Berserker Mindless Rage provides condition immunity during rage
- Condition system blocks/allows subclass features appropriately
- UI shows condition effects on feature availability

### Condition + Action Economy Integration
- Incapacitated conditions block actions/bonus actions
- Paralyzed prevents all actions except reactions
- Economy system respects condition restrictions

### Subclass + Action Economy Integration
- Subclass features consume appropriate action types
- Resource tracking integrates with economy validation
- Feature activation follows action economy rules

### All Systems + UI Integration
- Character sheet shows all conditions, features, and economy state
- Action cards reflect availability from all three systems
- Combat log provides detailed information from all systems
- Debug commands work across all systems

## Best Practices

### For Developers
1. **Use the configuration system** to toggle features during development
2. **Enable debug commands** for testing and validation
3. **Follow the modular subclass pattern** when adding new subclasses
4. **Integrate condition checks** into new features appropriately
5. **Respect action economy** in all combat-related code

### For Testing
1. **Run the comprehensive test suite** after changes
2. **Use debug commands** to verify system state
3. **Test edge cases** with multiple conditions/features active
4. **Validate UI responsiveness** with performance monitoring

### For Performance
1. **Enable caching** for production use
2. **Use lazy loading** for large datasets
3. **Monitor performance metrics** during development
4. **Profile memory usage** for optimization opportunities

## Troubleshooting

### Common Issues
1. **Features not loading**: Check if enhanced subclass manager is enabled
2. **Conditions not applying**: Verify condition immunity and prerequisites
3. **Actions blocked**: Check action economy state and condition restrictions
4. **Performance issues**: Enable performance mode and caching

### Debug Steps
1. **Check configuration**: `/debug config`
2. **Verify system status**: `/debug status`
3. **Monitor performance**: `/debug performance`
4. **Test specific features**: `/debug test_<feature> <character>`

### Log Analysis
- Enable query logging to trace database issues
- Use performance metrics to identify bottlenecks
- Check condition tracing for complex interactions
- Monitor memory usage for optimization needs