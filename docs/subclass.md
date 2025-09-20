# Subclass Architecture Enhancement for TaleKeeper

## Overview

While TaleKeeper has a functional subclass system in `services/subclass_manager.py`, the Barbarian Berserker implementation reveals opportunities for a more robust, extensible subclass architecture. This document proposes enhancements to create a comprehensive subclass framework supporting all D&D 2024 classes.

## Current State Analysis

### Existing Infrastructure
- **SubclassManager**: Basic subclass selection and feature tracking
- **Database Support**: Tables for subclasses and features
- **Multi-class Awareness**: Supports per-class subclass tracking

### Implementation Gaps
1. **Feature Activation**: No unified system for active vs passive features
2. **Resource Management**: Limited tracking of subclass-specific resources
3. **UI Integration**: Subclass features not prominently displayed
4. **Conditional Features**: No framework for level/situation-dependent features
5. **Berserker Example**: Mindless Rage, Retaliation not fully integrated

## Enhanced Subclass Architecture

### Core Subclass Framework

```python
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

class FeatureType(Enum):
    PASSIVE = "passive"           # Always active
    ACTIVATED = "activated"        # Requires activation
    TRIGGERED = "triggered"        # Automatic on condition
    REACTION = "reaction"         # Requires reaction
    MODIFIER = "modifier"         # Modifies existing abilities

@dataclass
class SubclassFeature:
    """Enhanced subclass feature definition."""
    name: str
    level: int
    feature_type: FeatureType
    description: str

    # Mechanical properties
    action_cost: Optional[str] = None  # "action", "bonus_action", "reaction", None
    resource_pool: Optional[str] = None  # e.g., "ki_points", "superiority_dice"
    resource_cost: int = 0
    uses_per_rest: Optional[int] = None
    rest_type: Optional[str] = None  # "short", "long"

    # Activation conditions
    prerequisites: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)

    # Effects
    effects: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[str] = None
    concentration: bool = False

    # UI properties
    icon: Optional[str] = None
    display_priority: int = 0
    show_in_action_cards: bool = False

@dataclass
class SubclassDefinition:
    """Complete subclass definition."""
    id: str
    name: str
    class_id: str
    description: str
    flavor_text: str
    selection_level: int = 3

    # Features by level
    features: Dict[int, List[SubclassFeature]] = field(default_factory=dict)

    # Subclass-specific resources
    resources: Dict[str, Dict] = field(default_factory=dict)

    # UI customization
    theme_color: str = "#ff6b35"
    icon_set: str = "default"
```

### Barbarian Subclass Implementation

```python
class BarbarianSubclasses:
    """Barbarian subclass definitions."""

    BERSERKER = SubclassDefinition(
        id="barbarian_berserker",
        name="Path of the Berserker",
        class_id="barbarian",
        description="Your rage is a fury that can carry you through anything",
        flavor_text="For some Barbarians, rage is a means to an end—that end being violence.",
        selection_level=3,
        theme_color="#8b0000",
        features={
            3: [
                SubclassFeature(
                    name="Frenzy",
                    level=3,
                    feature_type=FeatureType.MODIFIER,
                    description="When you Rage, you can go into a Frenzy",
                    effects={
                        "grants_bonus_action_attack": True,
                        "adds_exhaustion_on_rage_end": 1
                    },
                    show_in_action_cards=True
                )
            ],
            6: [
                SubclassFeature(
                    name="Mindless Rage",
                    level=6,
                    feature_type=FeatureType.PASSIVE,
                    description="You have immunity to Charmed and Frightened while raging",
                    effects={
                        "condition_immunity_while_raging": ["charmed", "frightened"],
                        "removes_conditions_on_rage": ["charmed", "frightened"]
                    }
                )
            ],
            10: [
                SubclassFeature(
                    name="Retaliation",
                    level=10,
                    feature_type=FeatureType.REACTION,
                    description="When damaged by a creature within 5 feet, you can react to attack",
                    action_cost="reaction",
                    triggers=["damage_taken_within_5ft"],
                    effects={"melee_attack": True},
                    show_in_action_cards=True
                )
            ],
            14: [
                SubclassFeature(
                    name="Intimidating Presence",
                    level=14,
                    feature_type=FeatureType.ACTIVATED,
                    description="Frighten a creature within 30 feet",
                    action_cost="action",
                    effects={
                        "save_type": "wisdom",
                        "save_dc": "8_plus_str_plus_prof",
                        "condition_on_fail": "frightened",
                        "duration": "1_minute"
                    },
                    show_in_action_cards=True
                )
            ]
        }
    )

    WILD_HEART = SubclassDefinition(
        id="barbarian_wild_heart",
        name="Path of the Wild Heart",
        class_id="barbarian",
        description="Your rage channels the power of animals",
        flavor_text="Barbarians who follow this path gain animal powers when they rage.",
        selection_level=3,
        theme_color="#228b22",
        resources={
            "animal_aspects": {
                "options": ["bear", "eagle", "wolf"],
                "can_change_on": "long_rest"
            }
        },
        features={
            3: [
                SubclassFeature(
                    name="Animal Speaker",
                    level=3,
                    feature_type=FeatureType.PASSIVE,
                    description="You can cast Beast Sense and Speak with Animals",
                    effects={
                        "ritual_spells": ["beast_sense", "speak_with_animals"]
                    }
                ),
                SubclassFeature(
                    name="Rage of the Wilds",
                    level=3,
                    feature_type=FeatureType.MODIFIER,
                    description="While raging, gain benefits based on chosen animal",
                    effects={
                        "bear": {"resistance": ["all_except_psychic"]},
                        "eagle": {"fly_speed": 20, "opportunity_attack_disadvantage": True},
                        "wolf": {"pack_tactics": True, "knock_prone_on_hit": True}
                    }
                )
            ],
            6: [
                SubclassFeature(
                    name="Aspect of the Beast",
                    level=6,
                    feature_type=FeatureType.PASSIVE,
                    description="Gain exploration benefit based on chosen animal",
                    effects={
                        "bear": {"carrying_capacity": "double", "push_drag_lift": "double"},
                        "eagle": {"sight_range": "1_mile", "dim_light_no_disadvantage": True},
                        "wolf": {"tracking_advantage": True, "travel_pace": "fast"}
                    }
                )
            ]
        }
    )
```

### Enhanced Subclass Manager

```python
class EnhancedSubclassManager:
    """Enhanced subclass management system."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.subclass_registry = {}
        self.feature_handlers = {}
        self.load_subclass_definitions()

    def load_subclass_definitions(self):
        """Load all subclass definitions from modules."""
        # Load from class-specific modules
        self.subclass_registry['barbarian'] = {
            'berserker': BarbarianSubclasses.BERSERKER,
            'wild_heart': BarbarianSubclasses.WILD_HEART
        }
        # Add other classes...

    def register_feature_handler(self, feature_name: str, handler: Callable):
        """Register a handler function for a feature."""
        self.feature_handlers[feature_name] = handler

    def select_subclass(self, character_id: str, subclass_id: str) -> bool:
        """Enhanced subclass selection with full feature initialization."""
        try:
            # Get subclass definition
            subclass = self.get_subclass_definition(subclass_id)
            if not subclass:
                return False

            # Check prerequisites
            if not self.meets_prerequisites(character_id, subclass):
                return False

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Record subclass selection
                self._record_subclass_selection(cursor, character_id, subclass)

                # Grant initial features
                character_level = self._get_character_level(cursor, character_id, subclass.class_id)
                self._grant_subclass_features_up_to_level(cursor, character_id, subclass, character_level)

                # Initialize subclass resources
                self._initialize_subclass_resources(cursor, character_id, subclass)

                # Create UI elements
                self._create_subclass_ui_elements(character_id, subclass)

                conn.commit()
                return True

        except Exception as e:
            print(f"[SubclassManager] Error selecting subclass: {e}")
            return False

    def _grant_subclass_features_up_to_level(self, cursor, character_id: str,
                                            subclass: SubclassDefinition, level: int):
        """Grant all subclass features up to specified level."""
        for feature_level, features in subclass.features.items():
            if feature_level > level:
                continue

            for feature in features:
                self._grant_feature(cursor, character_id, feature, subclass.id)

    def _grant_feature(self, cursor, character_id: str, feature: SubclassFeature, subclass_id: str):
        """Grant a specific feature to a character."""
        # Record in database
        cursor.execute("""
            INSERT OR IGNORE INTO character_features
            (character_id, feature_name, feature_type, source_type, source_id,
             level_gained, description, effects, action_cost, resource_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, feature.name, feature.feature_type.value,
            'subclass', subclass_id, feature.level,
            feature.description, json.dumps(feature.effects),
            feature.action_cost, feature.resource_cost
        ))

        # Handle specific feature types
        if feature.feature_type == FeatureType.PASSIVE:
            self._apply_passive_feature(cursor, character_id, feature)
        elif feature.feature_type == FeatureType.TRIGGERED:
            self._register_triggered_feature(character_id, feature)
        elif feature.feature_type == FeatureType.REACTION:
            self._register_reaction_feature(character_id, feature)

        # Initialize resource tracking if needed
        if feature.uses_per_rest:
            self._initialize_feature_uses(cursor, character_id, feature)

    def process_feature_triggers(self, character_id: str, trigger_type: str, context: Dict):
        """Process triggered features based on game events."""
        features = self.get_triggered_features(character_id, trigger_type)

        for feature in features:
            if self.check_feature_prerequisites(character_id, feature, context):
                self.execute_triggered_feature(character_id, feature, context)

    def get_available_actions(self, character_id: str) -> List[Dict]:
        """Get all available subclass actions for action cards."""
        actions = []
        features = self.get_character_subclass_features(character_id)

        for feature in features:
            if feature.show_in_action_cards:
                if self.can_use_feature(character_id, feature):
                    actions.append({
                        'name': feature.name,
                        'description': feature.description,
                        'action_cost': feature.action_cost,
                        'resource_cost': feature.resource_cost,
                        'effects': feature.effects,
                        'icon': feature.icon
                    })

        return actions
```

### UI Integration System

```python
class SubclassUIManager:
    """Manages subclass-specific UI elements."""

    def create_subclass_panel(self, character_id: str, subclass: SubclassDefinition) -> QWidget:
        """Create a panel showing subclass features and resources."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Subclass header with theme color
        header = self.create_styled_header(subclass.name, subclass.theme_color)
        layout.addWidget(header)

        # Feature list
        features_widget = self.create_features_list(character_id, subclass)
        layout.addWidget(features_widget)

        # Resource trackers
        if subclass.resources:
            resources_widget = self.create_resource_trackers(character_id, subclass)
            layout.addWidget(resources_widget)

        # Active effects indicator
        effects_widget = self.create_active_effects_display(character_id)
        layout.addWidget(effects_widget)

        panel.setLayout(layout)
        return panel

    def create_feature_action_card(self, feature: SubclassFeature) -> ActionCard:
        """Create an action card for an activated feature."""
        card = ActionCard()
        card.set_title(feature.name)
        card.set_description(feature.description)

        # Set card appearance based on feature type
        if feature.feature_type == FeatureType.REACTION:
            card.set_style("reaction")
            card.set_badge("Reaction")
        elif feature.action_cost == "bonus_action":
            card.set_style("bonus_action")
            card.set_badge("Bonus Action")

        # Add resource cost indicator
        if feature.resource_cost > 0:
            card.add_cost_indicator(f"Cost: {feature.resource_cost} {feature.resource_pool}")

        # Add usage counter if limited
        if feature.uses_per_rest:
            remaining = self.get_remaining_uses(feature.name)
            card.add_usage_counter(f"{remaining}/{feature.uses_per_rest}")

        return card

    def highlight_triggered_features(self, character_id: str, trigger_type: str):
        """Highlight features that can be triggered in current situation."""
        triggered_features = self.get_triggered_features(character_id, trigger_type)

        for feature in triggered_features:
            # Flash or highlight the feature in UI
            self.flash_feature_indicator(feature.name)

            # Show tooltip explaining the trigger
            self.show_feature_tooltip(
                feature.name,
                f"{feature.name} can be used! {feature.description}"
            )
```

### Berserker Integration Example

```python
class BerserkerIntegration:
    """Complete integration of Berserker subclass features."""

    def apply_frenzy(self, character_id: str):
        """Apply Frenzy when entering rage."""
        if not self.has_feature(character_id, "Frenzy"):
            return

        # Check if player wants to use Frenzy
        if self.prompt_frenzy_use(character_id):
            # Grant bonus action attack for duration of rage
            self.grant_bonus_action_attack(character_id, "rage_duration")

            # Mark that exhaustion will be gained
            self.set_pending_effect(character_id, "exhaustion_on_rage_end", 1)

            # Update UI
            self.add_status_indicator(character_id, "Frenzied", "red")

    def apply_mindless_rage(self, character_id: str):
        """Apply Mindless Rage immunity while raging."""
        if not self.has_feature(character_id, "Mindless Rage"):
            return

        if self.is_raging(character_id):
            # Remove existing conditions
            self.remove_condition(character_id, "charmed")
            self.remove_condition(character_id, "frightened")

            # Apply immunity for rage duration
            self.apply_condition_immunity(character_id, ["charmed", "frightened"], "while_raging")

    def trigger_retaliation(self, character_id: str, attacker_id: str, damage: int):
        """Check and process Retaliation trigger."""
        if not self.has_feature(character_id, "Retaliation"):
            return

        if not self.is_within_range(character_id, attacker_id, 5):
            return

        if not self.has_reaction_available(character_id):
            return

        # Prompt for reaction use
        if self.prompt_reaction(
            character_id,
            f"Use Retaliation against {self.get_creature_name(attacker_id)}?",
            "You can make one melee attack against the creature that damaged you."
        ):
            # Use reaction
            self.use_reaction(character_id)

            # Make melee attack
            self.make_melee_attack(character_id, attacker_id, "retaliation")

    def use_intimidating_presence(self, character_id: str, target_id: str):
        """Activate Intimidating Presence."""
        if not self.can_use_action(character_id):
            return False

        # Calculate save DC
        save_dc = 8 + self.get_strength_modifier(character_id) + self.get_proficiency_bonus(character_id)

        # Target makes Wisdom save
        if self.make_saving_throw(target_id, "wisdom", save_dc):
            self.log_message(f"{self.get_creature_name(target_id)} resists your Intimidating Presence!")
            return False

        # Apply frightened condition
        self.apply_condition(
            target_id,
            "frightened",
            source=character_id,
            duration="1_minute",
            save_ends=True,
            save_type="wisdom",
            save_dc=save_dc
        )

        self.log_message(f"{self.get_creature_name(target_id)} is frightened by your Intimidating Presence!")
        return True
```

## Database Schema

```sql
-- Enhanced subclass features table
CREATE TABLE subclass_features_enhanced (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subclass_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_type TEXT NOT NULL,
    description TEXT,
    action_cost TEXT,
    resource_pool TEXT,
    resource_cost INTEGER DEFAULT 0,
    uses_per_rest INTEGER,
    rest_type TEXT,
    prerequisites TEXT, -- JSON array
    triggers TEXT, -- JSON array
    effects TEXT, -- JSON
    duration TEXT,
    concentration BOOLEAN DEFAULT FALSE,
    icon TEXT,
    display_priority INTEGER DEFAULT 0,
    show_in_action_cards BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id)
);

-- Character feature usage tracking
CREATE TABLE character_feature_uses (
    character_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    current_uses INTEGER DEFAULT 0,
    max_uses INTEGER,
    last_reset TEXT,
    PRIMARY KEY (character_id, feature_name),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Subclass resource pools
CREATE TABLE subclass_resources (
    character_id TEXT NOT NULL,
    subclass_id TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    current_value INTEGER,
    max_value INTEGER,
    recharge_rate TEXT,
    metadata TEXT, -- JSON for additional properties
    PRIMARY KEY (character_id, resource_name),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

## Implementation Phases

### Phase 1: Core Framework
- [ ] Create enhanced SubclassDefinition structure
- [ ] Implement SubclassFeature with all properties
- [ ] Build feature type handlers
- [ ] Add database schema updates

### Phase 2: Berserker Complete Implementation
- [ ] Implement all Berserker features
- [ ] Add Mindless Rage condition immunity
- [ ] Create Retaliation reaction system
- [ ] Integrate Intimidating Presence

### Phase 3: UI Integration
- [ ] Create subclass feature panels
- [ ] Add feature action cards
- [ ] Implement trigger highlights
- [ ] Show resource tracking

### Phase 4: Extended Subclasses
- [ ] Implement Wild Heart (Barbarian)
- [ ] Add Fighter subclasses (Champion, Battle Master)
- [ ] Create Wizard subclasses
- [ ] Support all core classes

## Benefits

### System Architecture
- **Unified Framework**: All subclasses use same structure
- **Feature Types**: Clear distinction between passive, activated, triggered
- **Resource Management**: Built-in tracking for subclass resources
- **Condition Integration**: Seamless interaction with condition system

### Gameplay Enhancement
- **Feature Visibility**: Clear display of available features
- **Automatic Triggers**: System handles triggered features
- **Resource Tracking**: Automatic management of limited-use features
- **Rules Compliance**: Enforces D&D 2024 subclass rules

### Development Benefits
- **Extensibility**: Easy to add new subclasses
- **Maintainability**: Centralized feature definitions
- **Testing**: Comprehensive test framework for features
- **Documentation**: Self-documenting feature structure

This enhanced subclass architecture provides a robust foundation for implementing all D&D 2024 subclasses while addressing the specific gaps identified in the Barbarian Berserker implementation.