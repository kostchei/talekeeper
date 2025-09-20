# Condition System Design for TaleKeeper

## Overview

The Condition System addresses the current gap where Barbarian features like Danger Sense check for "incapacitating conditions" but no formal condition tracking exists. This system will implement comprehensive D&D 2024 condition mechanics with automatic application, tracking, and resolution.

## Current State Analysis

### Existing Condition References
- **Danger Sense**: Checks `not_incapacitated` in barbarian_abilities.py:34
- **Paralyzed/Stunned/Restrained**: Referenced in database seeds but no tracking
- **Charmed/Frightened**: Monster abilities reference but no player tracking
- **Concentration**: Spell effects mentioned but no formal system

### Implementation Gaps
1. No unified condition state tracking
2. Condition effects not automatically applied to stats/abilities
3. No condition duration management (rounds, saves, etc.)
4. No UI indication of active conditions
5. Missing interaction with action economy system

## Design Architecture

### Core Data Models

#### ConditionType Enum
```python
class ConditionType(Enum):
    # Core D&D 2024 Conditions (from SRD)
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    EXHAUSTION = "exhaustion"  # Special: Has levels 1-6
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"  # Key condition for Danger Sense
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"

    # Special Game States (not formal conditions)
    CONCENTRATION = "concentration"
    RAGING = "raging"  # Barbarian-specific
```

#### Condition State Tracking
```python
@dataclass
class ActiveCondition:
    condition_type: ConditionType
    source: str                    # "Spell: Hold Person", "Monster: Paralyzing Touch"
    duration_type: str             # "rounds", "concentration", "save_ends", "permanent"
    duration_remaining: int        # Rounds left (-1 for indefinite)
    save_dc: Optional[int]         # DC for save-ends conditions
    save_ability: Optional[str]    # "constitution", "wisdom", etc.
    save_frequency: str            # "start_of_turn", "end_of_turn"
    concentration_caster: Optional[str]  # Character maintaining concentration
    applied_at_round: int
    metadata: Dict[str, Any]       # Level of exhaustion, spell slot, etc.
```

### Database Integration

#### New Tables
```sql
-- Active conditions on characters/monsters
CREATE TABLE character_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    condition_type TEXT NOT NULL,
    source TEXT NOT NULL,
    duration_type TEXT NOT NULL DEFAULT 'rounds',
    duration_remaining INTEGER DEFAULT -1,
    save_dc INTEGER,
    save_ability TEXT,
    save_frequency TEXT DEFAULT 'end_of_turn',
    concentration_caster TEXT,
    applied_at_round INTEGER,
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Condition definitions and effects
CREATE TABLE condition_definitions (
    condition_type TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    mechanical_effects TEXT NOT NULL,  -- JSON of stat modifications
    incapacitating BOOLEAN DEFAULT FALSE,
    blocks_actions BOOLEAN DEFAULT FALSE,
    blocks_bonus_actions BOOLEAN DEFAULT FALSE,
    blocks_reactions BOOLEAN DEFAULT FALSE,
    movement_restriction TEXT,  -- "none", "half", "zero"
    advantage_disadvantage TEXT DEFAULT '{}',  -- JSON of affected rolls
    ui_color TEXT DEFAULT '#ff6b35'
);
```

### Mechanical Effects System

#### Automatic Stat Modifications
Conditions automatically modify character capabilities per D&D 2024 rules:

```python
class ConditionEffects:
    MECHANICAL_EFFECTS = {
        ConditionType.BLINDED: {
            "auto_fail_sight_checks": True,
            "attack_rolls": "disadvantage",
            "attack_rolls_against": "advantage"
        },
        ConditionType.CHARMED: {
            "cannot_attack_charmer": True,
            "charmer_social_checks": "advantage"
        },
        ConditionType.DEAFENED: {
            "auto_fail_hearing_checks": True
        },
        ConditionType.EXHAUSTION: {
            "levels": True,  # Special handling: 1-6 levels
            "d20_test_penalty": "minus_2_per_level",
            "speed_reduction": "minus_5ft_per_level",
            "death_at_level_6": True
        },
        ConditionType.FRIGHTENED: {
            "ability_checks": "disadvantage_if_source_visible",
            "attack_rolls": "disadvantage_if_source_visible",
            "movement_restriction": "cannot_move_closer_to_source"
        },
        ConditionType.GRAPPLED: {
            "movement_speed": 0,
            "attack_rolls_not_grappler": "disadvantage",
            "can_be_dragged": True
        },
        ConditionType.INCAPACITATED: {
            "no_actions": True,
            "no_bonus_actions": True,
            "no_reactions": True,
            "breaks_concentration": True,
            "cannot_speak": True,
            "initiative_disadvantage": True
        },
        ConditionType.PARALYZED: {
            "has_incapacitated": True,
            "movement_speed": 0,
            "saving_throws": {"strength": "auto_fail", "dexterity": "auto_fail"},
            "attack_rolls_against": "advantage",
            "critical_hits_within_5ft": True
        },
        ConditionType.POISONED: {
            "ability_checks": "disadvantage",
            "attack_rolls": "disadvantage"
        },
        ConditionType.PRONE: {
            "movement_options": "crawl_or_half_speed_to_stand",
            "attack_rolls": "disadvantage",
            "melee_attacks_against_within_5ft": "advantage",
            "ranged_attacks_against": "disadvantage"
        },
        ConditionType.RESTRAINED: {
            "movement_speed": 0,
            "attack_rolls": "disadvantage",
            "attack_rolls_against": "advantage",
            "dexterity_saves": "disadvantage"
        },
        ConditionType.STUNNED: {
            "has_incapacitated": True,
            "saving_throws": {"strength": "auto_fail", "dexterity": "auto_fail"},
            "attack_rolls_against": "advantage"
        },
        ConditionType.UNCONSCIOUS: {
            "has_incapacitated": True,
            "has_prone": True,
            "drops_held_items": True,
            "movement_speed": 0,
            "attack_rolls_against": "advantage",
            "saving_throws": {"strength": "auto_fail", "dexterity": "auto_fail"}
        }
    }
```

### Integration Points

#### Action Economy Integration
Conditions integrate with the existing action economy system:
- **Incapacitated**: Blocks all actions except free actions
- **Paralyzed/Stunned**: Blocks actions, bonus actions, reactions
- **Unconscious**: Blocks all actions, auto-fails STR/DEX saves

#### Advantage System Enhancement
Extend existing advantage_system.py:
```python
def get_condition_advantage_effects(character_id: str, roll_type: str) -> List[str]:
    """Get advantage/disadvantage from active conditions."""
    active_conditions = condition_manager.get_active_conditions(character_id)
    effects = []

    for condition in active_conditions:
        if roll_type in CONDITION_EFFECTS[condition.condition_type].get('advantage_disadvantage', {}):
            effects.append(CONDITION_EFFECTS[condition.condition_type]['advantage_disadvantage'][roll_type])

    return effects
```

#### Combat Integration
Conditions interact with combat mechanics:
- **Automatic saves**: Start/end of turn saving throws
- **Duration tracking**: Countdown during turn progression
- **Concentration checks**: Damage triggers concentration saves
- **Death saves**: Unconscious condition triggers death save mechanics

### User Interface Integration

#### Character Sheet Display
- **Condition Icons**: Visual indicators next to character portrait
- **Tooltip Details**: Hover shows condition description and remaining duration
- **Status Bar**: "Paralyzed (2 rounds) | Poisoned (Save DC 14)"

#### Action Panel Integration
- **Disabled Actions**: Grayed out actions with "Cannot act while paralyzed" tooltips
- **Condition Actions**: Special actions for condition removal ("Shake Off Charm")
- **Save Prompts**: Automatic save roll prompts at appropriate times

#### Log Panel Events
- "Barbarian becomes paralyzed by Hold Person (Save DC 15, Constitution)"
- "Barbarian attempts Constitution save: 12 vs DC 15 - Failed"
- "Barbarian attempts Constitution save: 18 vs DC 15 - Success! Paralysis ends"

### Condition Management Workflows

#### Applying Conditions
```python
def apply_condition(character_id: str, condition_type: ConditionType,
                   source: str, duration: int = -1, save_dc: int = None):
    """Apply a condition to a character."""
    # Check for condition immunities
    if has_condition_immunity(character_id, condition_type):
        return False

    # Apply condition
    condition = ActiveCondition(
        condition_type=condition_type,
        source=source,
        duration_remaining=duration,
        save_dc=save_dc
    )

    # Store in database
    condition_manager.add_condition(character_id, condition)

    # Apply immediate mechanical effects
    apply_condition_effects(character_id, condition_type)

    # Update UI
    signal_condition_changed.emit(character_id)
```

#### Turn Progression Integration
```python
def process_condition_effects_start_of_turn(character_id: str):
    """Process conditions at start of character's turn."""
    conditions = get_active_conditions(character_id)

    for condition in conditions:
        # Decrement duration
        if condition.duration_type == "rounds" and condition.duration_remaining > 0:
            condition.duration_remaining -= 1

        # Process start-of-turn saves
        if condition.save_frequency == "start_of_turn" and condition.save_dc:
            if attempt_condition_save(character_id, condition):
                remove_condition(character_id, condition.condition_type)

        # Remove expired conditions
        if condition.duration_remaining == 0:
            remove_condition(character_id, condition.condition_type)
```

## Barbarian Integration

### Danger Sense Enhancement
Current implementation only checks a flag. Enhanced version:
```python
def has_danger_sense_advantage(character_id: str) -> bool:
    """Check if Danger Sense applies to Dexterity saves."""
    # Character must have Danger Sense feature
    if not has_feature(character_id, "Danger Sense"):
        return False

    # Must not be incapacitated
    active_conditions = condition_manager.get_active_conditions(character_id)
    for condition in active_conditions:
        if CONDITION_EFFECTS[condition.condition_type].get("incapacitated", False):
            return False

    return True
```

### Berserker Rage Enhancements
Rage could provide condition immunities:
```python
def apply_berserker_rage_immunities(character_id: str):
    """Apply condition immunities during rage."""
    if is_raging(character_id):
        # Immune to charmed and frightened while raging
        for condition_type in [ConditionType.CHARMED, ConditionType.FRIGHTENED]:
            if has_active_condition(character_id, condition_type):
                remove_condition(character_id, condition_type, "Rage immunity")
```

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Create condition database tables
- [ ] Implement ConditionManager service
- [ ] Basic condition application/removal
- [ ] Integration with existing advantage system

### Phase 2: Mechanical Effects
- [ ] Automatic stat modification system
- [ ] Action economy integration
- [ ] Turn-based duration tracking
- [ ] Saving throw automation

### Phase 3: UI Integration
- [ ] Character sheet condition display
- [ ] Action panel condition effects
- [ ] Log panel condition events
- [ ] Combat encounter condition management

### Phase 4: Advanced Features
- [ ] Concentration tracking
- [ ] Condition immunity system
- [ ] Complex condition interactions
- [ ] Monster condition AI

## Testing Strategy

### Core Functionality Tests
- Apply/remove conditions correctly
- Duration tracking works properly
- Saving throws trigger at correct times
- Mechanical effects apply automatically

### Integration Tests
- Danger Sense works with incapacitation check
- Action economy respects condition restrictions
- Advantage system includes condition effects
- Combat properly handles condition turns

### Edge Case Handling
- Multiple conditions of same type
- Concentration spell interruption
- Condition immunity interactions
- Save-or-die condition chains

## Benefits

### Gameplay Enhancement
- **Authentic D&D Experience**: Full condition mechanics as per D&D 2024 rules
- **Tactical Depth**: Conditions become meaningful tactical considerations
- **Automation**: Reduces manual tracking and rule lookups

### Code Quality
- **Unified System**: Replaces scattered condition references with centralized management
- **Extensibility**: Easy to add new conditions or modify existing ones
- **Integration**: Seamlessly works with existing combat and advantage systems

### Player Experience
- **Clear Feedback**: Visual and textual indication of all active conditions
- **Rule Compliance**: Prevents illegal actions due to conditions
- **Educational**: Helps players learn D&D condition interactions

This condition system transforms TaleKeeper from having scattered condition references to a comprehensive, automated condition management system that enhances both gameplay authenticity and tactical depth.