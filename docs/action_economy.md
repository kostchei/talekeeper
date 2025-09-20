# Action Economy Enhancement Plan for TaleKeeper

## Overview

While TaleKeeper has a solid foundation for action economy in `models/action_economy.py` and `docs/ACTION_ECONOMY_SPECIFICATION.md`, the Barbarian class implementation reveals gaps in integration with class-specific features. This document outlines enhancements to create a more robust, integrated action economy system.

## Current State Analysis

### Existing Infrastructure
- **Core System**: Well-designed `ActionEconomyState` and `CombatActionEconomy` classes
- **Documentation**: Comprehensive specification in ACTION_ECONOMY_SPECIFICATION.md
- **Data Models**: Proper tracking of actions, bonus actions, reactions, and movement

### Integration Gaps with Barbarian
1. **Rage Activation**: Uses bonus action but not tracked in action economy
2. **Brutal Strike**: Special action modification not integrated
3. **Retaliation**: Reaction usage not coordinated with system
4. **Feral Instinct**: Initiative advantage not connected
5. **Relentless Rage**: Death save reaction not tracked

## Enhanced Architecture

### Class-Specific Action Registry

```python
@dataclass
class ClassActionDefinition:
    """Defines class-specific action economy entries."""
    name: str
    action_type: ActionEconomyType
    class_name: str
    level_required: int
    resource_cost: Optional[Dict[str, int]]  # e.g., {"rage_uses": 1}
    conditions: List[str]  # e.g., ["not_wearing_heavy_armor"]
    duration: Optional[str]  # e.g., "1_minute", "until_rage_ends"
    effects: Dict[str, Any]

class ClassActionRegistry:
    """Registry of all class-specific action economy entries."""

    BARBARIAN_ACTIONS = {
        "rage": ClassActionDefinition(
            name="Rage",
            action_type=ActionEconomyType.BONUS_ACTION,
            class_name="barbarian",
            level_required=1,
            resource_cost={"rage_uses": 1},
            conditions=["not_wearing_heavy_armor", "not_incapacitated"],
            duration="1_minute",
            effects={
                "damage_resistance": ["bludgeoning", "piercing", "slashing"],
                "advantage_strength_checks": True,
                "rage_damage_bonus": True,
                "blocks_spellcasting": True
            }
        ),
        "reckless_attack": ClassActionDefinition(
            name="Reckless Attack",
            action_type=ActionEconomyType.FREE_ACTION,  # Modifies attack action
            class_name="barbarian",
            level_required=2,
            resource_cost=None,
            conditions=["first_attack_of_turn", "melee_weapon"],
            duration="until_end_of_turn",
            effects={
                "attack_advantage": True,
                "attacks_against_advantage": True
            }
        ),
        "brutal_strike": ClassActionDefinition(
            name="Brutal Strike",
            action_type=ActionEconomyType.FREE_ACTION,  # Enhances attack
            class_name="barbarian",
            level_required=9,
            resource_cost=None,
            conditions=["reckless_attack_active"],
            duration="instant",
            effects={
                "extra_damage": "1d10",
                "special_effects": ["forceful_blow", "hamstring_blow", "staggering_blow"]
            }
        ),
        "retaliation": ClassActionDefinition(
            name="Retaliation",
            action_type=ActionEconomyType.REACTION,
            class_name="barbarian",
            level_required=10,
            resource_cost=None,
            conditions=["subclass_berserker", "damage_taken_within_5ft"],
            duration="instant",
            effects={"melee_attack": True}
        ),
        "relentless_rage": ClassActionDefinition(
            name="Relentless Rage",
            action_type=ActionEconomyType.REACTION,
            class_name="barbarian",
            level_required=11,
            resource_cost=None,
            conditions=["raging", "reduced_to_0_hp", "not_instant_death"],
            duration="instant",
            effects={
                "constitution_save": "dc_10_plus_5_per_use",
                "success_effect": "drop_to_1_hp"
            }
        )
    }
```

### Enhanced Action Validation

```python
class EnhancedActionEconomy(CombatActionEconomy):
    """Extended action economy with class-specific validations."""

    def can_use_class_action(self, character_id: str, action_name: str) -> Tuple[bool, str]:
        """Validate if a character can use a class-specific action."""
        character = self.get_character_data(character_id)
        action_def = self.get_action_definition(action_name, character['class'])

        # Check level requirement
        if character['level'] < action_def.level_required:
            return False, f"Requires level {action_def.level_required}"

        # Check action economy availability
        if not self.can_take_action(character_id, action_def.action_type):
            return False, f"{action_def.action_type.value} already used"

        # Check resource availability
        if action_def.resource_cost:
            for resource, cost in action_def.resource_cost.items():
                current = self.get_resource_count(character_id, resource)
                if current < cost:
                    return False, f"Insufficient {resource}: {current}/{cost}"

        # Check conditions
        for condition in action_def.conditions:
            if not self.check_condition(character_id, condition):
                return False, f"Condition not met: {condition}"

        # Check for condition interactions
        if self.has_incapacitating_condition(character_id):
            return False, "Cannot act while incapacitated"

        return True, "Action available"

    def use_class_action(self, character_id: str, action_name: str) -> bool:
        """Execute a class-specific action with full tracking."""
        can_use, reason = self.can_use_class_action(character_id, action_name)
        if not can_use:
            self.log_failed_action(character_id, action_name, reason)
            return False

        action_def = self.get_action_definition(action_name)

        # Consume action economy
        self.use_action(character_id, action_def.action_type, action_name)

        # Consume resources
        if action_def.resource_cost:
            for resource, cost in action_def.resource_cost.items():
                self.consume_resource(character_id, resource, cost)

        # Apply effects
        self.apply_action_effects(character_id, action_def.effects)

        # Set duration if applicable
        if action_def.duration:
            self.set_effect_duration(character_id, action_name, action_def.duration)

        # Log successful action
        self.log_successful_action(character_id, action_name)

        return True
```

### UI Integration Enhancement

```python
class ActionCardEnhancement:
    """Enhanced action card system with economy awareness."""

    def generate_action_cards(self, character_id: str) -> List[ActionCard]:
        """Generate available action cards based on action economy state."""
        cards = []
        economy_state = self.get_economy_state(character_id)
        character_class = self.get_character_class(character_id)

        # Standard actions
        if economy_state.action_available:
            cards.extend(self.get_standard_action_cards())
            cards.extend(self.get_class_actions(character_class, ActionEconomyType.ACTION))

        # Bonus actions
        if economy_state.bonus_action_available:
            bonus_actions = self.get_class_actions(character_class, ActionEconomyType.BONUS_ACTION)
            for action in bonus_actions:
                if self.meets_requirements(character_id, action):
                    cards.append(self.create_action_card(action))

        # Reactions (always shown but disabled if used)
        reactions = self.get_class_actions(character_class, ActionEconomyType.REACTION)
        for reaction in reactions:
            card = self.create_action_card(reaction)
            if not economy_state.reaction_available:
                card.set_disabled("Reaction already used this round")
            cards.append(card)

        # Free actions and modifications
        free_actions = self.get_class_actions(character_class, ActionEconomyType.FREE_ACTION)
        cards.extend([self.create_action_card(fa) for fa in free_actions])

        return cards

    def update_card_states(self, character_id: str):
        """Update action card availability based on current economy state."""
        economy_state = self.get_economy_state(character_id)

        for card in self.action_cards:
            # Check action type availability
            if card.action_type == ActionEconomyType.ACTION:
                card.set_enabled(economy_state.action_available)
            elif card.action_type == ActionEconomyType.BONUS_ACTION:
                card.set_enabled(economy_state.bonus_action_available)
            elif card.action_type == ActionEconomyType.REACTION:
                card.set_enabled(economy_state.reaction_available)

            # Check specific conditions
            if card.has_conditions():
                can_use, reason = self.can_use_class_action(character_id, card.action_name)
                if not can_use:
                    card.set_disabled(reason)
```

### Barbarian-Specific Integration

```python
class BarbarianActionIntegration:
    """Specific integration for Barbarian class features."""

    def on_rage_activated(self, character_id: str):
        """Handle rage activation through action economy."""
        if self.use_class_action(character_id, "rage"):
            # Set rage state
            self.set_character_state(character_id, "raging", True)

            # Apply rage effects
            self.apply_damage_resistance(character_id, ["bludgeoning", "piercing", "slashing"])
            self.set_advantage_on_strength(character_id, True)

            # Start rage duration tracking
            self.start_duration_timer(character_id, "rage", rounds=10)

            # Update UI
            self.update_status_display(character_id, "Raging (10 rounds)")
            self.refresh_action_cards(character_id)

    def on_reckless_attack(self, character_id: str):
        """Handle reckless attack declaration."""
        if self.is_first_attack_this_turn(character_id):
            # No action economy cost (free modification)
            self.set_attack_mode(character_id, "reckless")

            # Apply effects for rest of turn
            self.grant_advantage_on_attacks(character_id)
            self.grant_advantage_against_character(character_id)

            # Enable Brutal Strike if level 9+
            if self.get_character_level(character_id) >= 9:
                self.enable_brutal_strike_options(character_id)

    def check_danger_sense(self, character_id: str, save_type: str) -> bool:
        """Check if Danger Sense applies, considering conditions."""
        if save_type != "dexterity":
            return False

        if self.get_character_level(character_id) < 2:
            return False

        # Key integration: Check for incapacitating conditions
        if self.condition_manager.has_incapacitating_condition(character_id):
            return False

        return True

    def process_retaliation_trigger(self, character_id: str, attacker_id: str):
        """Process Retaliation reaction trigger."""
        if not self.has_feature(character_id, "Retaliation"):
            return

        if not self.is_within_range(character_id, attacker_id, 5):
            return

        # Check reaction availability
        if not self.get_economy_state(character_id).reaction_available:
            self.log_message("Retaliation unavailable - reaction already used")
            return

        # Prompt for reaction use
        self.prompt_reaction_use(character_id, "Retaliation", attacker_id)
```

## Database Schema Enhancements

```sql
-- Track action economy history
CREATE TABLE action_economy_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    combat_session_id TEXT NOT NULL,
    character_id TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    turn_number INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    action_name TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    resources_consumed TEXT, -- JSON
    effects_applied TEXT, -- JSON
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Class-specific action definitions
CREATE TABLE class_action_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    action_name TEXT NOT NULL,
    action_type TEXT NOT NULL,
    level_required INTEGER NOT NULL,
    resource_cost TEXT, -- JSON
    conditions TEXT, -- JSON array
    duration TEXT,
    effects TEXT, -- JSON
    description TEXT,
    UNIQUE(class_name, action_name)
);

-- Track active duration effects
CREATE TABLE active_duration_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    effect_name TEXT NOT NULL,
    source_action TEXT NOT NULL,
    rounds_remaining INTEGER,
    expires_at_turn TEXT, -- "start" or "end"
    effects TEXT, -- JSON
    created_at_round INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

## Implementation Phases

### Phase 1: Core Enhancement
- [ ] Extend ActionEconomy classes with class-specific support
- [ ] Create ClassActionRegistry
- [ ] Implement enhanced validation system
- [ ] Add database tables for tracking

### Phase 2: Barbarian Integration
- [ ] Integrate all Barbarian actions with economy
- [ ] Connect rage tracking to duration system
- [ ] Implement Brutal Strike options
- [ ] Add Retaliation reaction handling

### Phase 3: UI Enhancement
- [ ] Update action card generation
- [ ] Add economy status display
- [ ] Implement reaction prompts
- [ ] Show duration timers

### Phase 4: Advanced Features
- [ ] Multi-class action handling
- [ ] Conditional action chains
- [ ] Simultaneous reaction resolution
- [ ] Action combo system

## Benefits

### Gameplay Improvements
- **Rules Enforcement**: Automatic D&D 2024 action economy compliance
- **Class Feature Integration**: Seamless handling of complex class abilities
- **Tactical Clarity**: Clear indication of available actions and resources

### System Architecture
- **Centralized Management**: All actions flow through unified system
- **Audit Trail**: Complete history of action usage
- **Extensibility**: Easy to add new classes and features

### Player Experience
- **Visual Feedback**: Real-time action availability updates
- **Resource Tracking**: Automatic resource consumption
- **Turn Flow**: Smooth progression through combat turns

## Testing Strategy

### Barbarian-Specific Tests
```python
def test_barbarian_action_economy():
    """Test Barbarian features with action economy."""
    # Test rage using bonus action
    assert economy.use_class_action(barbarian_id, "rage")
    assert not economy.get_state(barbarian_id).bonus_action_available

    # Test reckless attack (free action)
    assert economy.can_use_class_action(barbarian_id, "reckless_attack")[0]

    # Test Brutal Strike with reckless
    economy.use_class_action(barbarian_id, "reckless_attack")
    assert economy.can_use_class_action(barbarian_id, "brutal_strike")[0]

    # Test Retaliation reaction
    economy.trigger_reaction_opportunity(barbarian_id, "retaliation")
    assert economy.get_state(barbarian_id).reaction_available
    economy.use_class_action(barbarian_id, "retaliation")
    assert not economy.get_state(barbarian_id).reaction_available
```

This enhanced action economy system transforms the existing foundation into a comprehensive framework that properly integrates class-specific features, particularly addressing the gaps identified in the Barbarian implementation.