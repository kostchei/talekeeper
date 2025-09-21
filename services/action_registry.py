"""
Action Registry System for TaleKeeper

Provides a centralized registry for all character actions including:
- Class features (Rage, Second Wind, Action Surge)
- Subclass abilities (Intimidating Presence, Retaliation)
- Combat actions (Attack, Cast Spell, etc.)
- Prerequisites and validation

This system works alongside the existing action economy without
modifying core combat flow.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum


class ActionEconomyType(Enum):
    """Types of action economy slots"""
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    FREE_ACTION = "free_action"
    MOVEMENT = "movement"
    LEGENDARY_ACTION = "legendary_action"


class ActionTrigger(Enum):
    """When an action can be triggered"""
    MANUAL = "manual"           # Player chooses when to use
    AUTOMATIC = "automatic"     # Triggers automatically when conditions met
    REACTION = "reaction"       # Triggers in response to specific events
    TURN_START = "turn_start"   # Triggers at start of turn
    TURN_END = "turn_end"       # Triggers at end of turn
    ROUND_START = "round_start" # Triggers at start of round
    ROUND_END = "round_end"     # Triggers at end of round


class PrerequisiteType(Enum):
    """Types of prerequisites"""
    LEVEL = "level"
    CLASS = "class"
    SUBCLASS = "subclass"
    FEATURE = "feature"
    RESOURCE = "resource"
    CONDITION = "condition"
    EQUIPMENT = "equipment"
    COMBAT_STATE = "combat_state"


@dataclass
class ActionPrerequisite:
    """Defines a prerequisite for using an action"""
    type: PrerequisiteType
    value: Any
    operator: str = "="  # =, >=, <=, >, <, !=, in, not_in
    description: Optional[str] = None


@dataclass
class ActionResource:
    """Defines a resource consumed by an action"""
    name: str
    amount: int = 1
    restore_on: str = "long_rest"  # long_rest, short_rest, turn, round


@dataclass
class ClassActionDefinition:
    """Complete definition of a character action"""

    # Basic Properties
    id: str
    name: str
    description: str
    class_name: Optional[str] = None
    subclass_name: Optional[str] = None

    # Action Economy
    economy_type: ActionEconomyType = ActionEconomyType.ACTION
    trigger: ActionTrigger = ActionTrigger.MANUAL

    # Prerequisites
    prerequisites: List[ActionPrerequisite] = field(default_factory=list)

    # Resources
    resources_consumed: List[ActionResource] = field(default_factory=list)

    # Mechanics
    target_required: bool = False
    range_feet: Optional[int] = None
    area_of_effect: Optional[str] = None
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None

    # Implementation
    handler_function: Optional[str] = None  # Name of function to call
    handler_module: Optional[str] = None    # Module containing handler

    # UI Properties
    icon: Optional[str] = None
    tooltip: Optional[str] = None
    tooltip_extended: Optional[str] = None

    # Validation
    cooldown_turns: int = 0
    uses_per_combat: Optional[int] = None
    uses_per_rest: Optional[int] = None


class ActionRegistry:
    """Registry for all character actions"""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._actions: Dict[str, ClassActionDefinition] = {}
        self._class_actions: Dict[str, List[str]] = {}
        self._subclass_actions: Dict[str, Dict[str, List[str]]] = {}

        # Initialize with built-in actions
        self._register_core_actions()
        self._register_barbarian_actions()

    def register_action(self, action: ClassActionDefinition) -> None:
        """Register a new action definition"""
        self._actions[action.id] = action

        # Index by class
        if action.class_name:
            if action.class_name not in self._class_actions:
                self._class_actions[action.class_name] = []
            self._class_actions[action.class_name].append(action.id)

            # Index by subclass
            if action.subclass_name:
                if action.class_name not in self._subclass_actions:
                    self._subclass_actions[action.class_name] = {}
                if action.subclass_name not in self._subclass_actions[action.class_name]:
                    self._subclass_actions[action.class_name][action.subclass_name] = []
                self._subclass_actions[action.class_name][action.subclass_name].append(action.id)

    def get_action(self, action_id: str) -> Optional[ClassActionDefinition]:
        """Get action definition by ID"""
        return self._actions.get(action_id)

    def get_class_actions(self, class_name: str, level: int = 20) -> List[ClassActionDefinition]:
        """Get all actions available to a class at given level"""
        actions = []
        action_ids = self._class_actions.get(class_name, [])

        for action_id in action_ids:
            action = self._actions[action_id]
            if self._meets_level_requirement(action, level):
                actions.append(action)

        return actions

    def get_subclass_actions(self, class_name: str, subclass_name: str, level: int = 20) -> List[ClassActionDefinition]:
        """Get all actions available to a subclass at given level"""
        actions = []

        if class_name in self._subclass_actions and subclass_name in self._subclass_actions[class_name]:
            action_ids = self._subclass_actions[class_name][subclass_name]

            for action_id in action_ids:
                action = self._actions[action_id]
                if self._meets_level_requirement(action, level):
                    actions.append(action)

        return actions

    def get_character_actions(self, character_id: str) -> List[ClassActionDefinition]:
        """Get all actions available to a specific character"""
        character_data = self._get_character_data(character_id)
        if not character_data:
            return []

        actions = []

        # Add class actions
        class_actions = self.get_class_actions(
            character_data['class_name'],
            character_data['level']
        )
        actions.extend(class_actions)

        # Add subclass actions
        if character_data.get('subclass_name'):
            subclass_actions = self.get_subclass_actions(
                character_data['class_name'],
                character_data['subclass_name'],
                character_data['level']
            )
            actions.extend(subclass_actions)

        # Filter by prerequisites
        valid_actions = []
        for action in actions:
            if self.validate_prerequisites(action, character_id):
                valid_actions.append(action)

        return valid_actions

    def validate_prerequisites(self, action: ClassActionDefinition, character_id: str) -> bool:
        """Validate all prerequisites for an action"""
        character_data = self._get_character_data(character_id)
        if not character_data:
            return False

        for prereq in action.prerequisites:
            if not self._check_prerequisite(prereq, character_data, character_id):
                return False

        return True

    def can_use_action(self, action_id: str, character_id: str) -> Dict[str, Any]:
        """Check if character can currently use an action"""
        action = self.get_action(action_id)
        if not action:
            return {"can_use": False, "reason": "Action not found"}

        # Check prerequisites
        if not self.validate_prerequisites(action, character_id):
            return {"can_use": False, "reason": "Prerequisites not met"}

        # Check resources
        resource_check = self._check_resources(action, character_id)
        if not resource_check["available"]:
            return {"can_use": False, "reason": resource_check["reason"]}

        # Check action economy (if in combat)
        economy_check = self._check_action_economy(action, character_id)
        if not economy_check["available"]:
            return {"can_use": False, "reason": economy_check["reason"]}

        return {"can_use": True}

    def _register_core_actions(self):
        """Register core D&D actions available to all characters"""

        # Basic Combat Actions
        self.register_action(ClassActionDefinition(
            id="attack",
            name="Attack",
            description="Make a weapon or unarmed attack",
            economy_type=ActionEconomyType.ACTION,
            target_required=True,
            handler_function="handle_attack",
            handler_module="core.combat_manager"
        ))

        self.register_action(ClassActionDefinition(
            id="cast_spell",
            name="Cast Spell",
            description="Cast a spell",
            economy_type=ActionEconomyType.ACTION,
            handler_function="handle_cast_spell",
            handler_module="services.spell_service"
        ))

        self.register_action(ClassActionDefinition(
            id="dodge",
            name="Dodge",
            description="Take the Dodge action",
            economy_type=ActionEconomyType.ACTION,
            handler_function="handle_dodge",
            handler_module="core.combat_manager"
        ))

        self.register_action(ClassActionDefinition(
            id="dash",
            name="Dash",
            description="Take the Dash action",
            economy_type=ActionEconomyType.ACTION,
            handler_function="handle_dash",
            handler_module="core.combat_manager"
        ))

        self.register_action(ClassActionDefinition(
            id="help",
            name="Help",
            description="Take the Help action",
            economy_type=ActionEconomyType.ACTION,
            target_required=True,
            handler_function="handle_help",
            handler_module="core.combat_manager"
        ))

    def _register_barbarian_actions(self):
        """Register all Barbarian class actions"""

        # Rage (Level 1)
        self.register_action(ClassActionDefinition(
            id="barbarian_rage",
            name="Rage",
            description="Enter a battle rage for enhanced combat abilities",
            class_name="barbarian",
            economy_type=ActionEconomyType.BONUS_ACTION,
            prerequisites=[
                ActionPrerequisite(PrerequisiteType.LEVEL, 1, ">="),
                ActionPrerequisite(PrerequisiteType.CLASS, "barbarian")
            ],
            resources_consumed=[
                ActionResource("rage_uses", 1, "long_rest")
            ],
            handler_function="use_rage",
            handler_module="services.barbarian_abilities",
            tooltip="Enter rage: resistance to physical damage, +damage on Strength attacks",
            tooltip_extended="Gain resistance to bludgeoning, piercing, slashing damage. Add rage damage to Strength-based melee attacks. Advantage on Strength checks and saves. Cannot cast spells or maintain concentration."
        ))

        # Reckless Attack (Level 2)
        self.register_action(ClassActionDefinition(
            id="barbarian_reckless_attack",
            name="Reckless Attack",
            description="Attack with advantage but grant advantage to enemies",
            class_name="barbarian",
            economy_type=ActionEconomyType.FREE_ACTION,
            prerequisites=[
                ActionPrerequisite(PrerequisiteType.LEVEL, 2, ">="),
                ActionPrerequisite(PrerequisiteType.CLASS, "barbarian")
            ],
            handler_function="use_reckless_attack",
            handler_module="services.barbarian_abilities",
            tooltip="Toggle reckless attack: advantage on Strength attacks, enemies get advantage on you"
        ))

        # Brutal Strike (Level 9)
        self.register_action(ClassActionDefinition(
            id="barbarian_brutal_strike",
            name="Brutal Strike",
            description="Add brutal effects when using Reckless Attack",
            class_name="barbarian",
            economy_type=ActionEconomyType.FREE_ACTION,
            prerequisites=[
                ActionPrerequisite(PrerequisiteType.LEVEL, 9, ">="),
                ActionPrerequisite(PrerequisiteType.CLASS, "barbarian"),
                ActionPrerequisite(PrerequisiteType.COMBAT_STATE, "reckless_attack_active")
            ],
            resources_consumed=[
                ActionResource("brutal_strike_uses", 1, "short_rest")
            ],
            handler_function="use_brutal_strike",
            handler_module="services.barbarian_abilities",
            tooltip="Add brutal effects to reckless attacks (when available)"
        ))

        # Berserker Subclass Actions

        # Frenzy (Level 3, Berserker)
        self.register_action(ClassActionDefinition(
            id="berserker_frenzy",
            name="Frenzy",
            description="Automatic bonus when raging and using reckless attack",
            class_name="barbarian",
            subclass_name="berserker",
            economy_type=ActionEconomyType.FREE_ACTION,
            trigger=ActionTrigger.AUTOMATIC,
            prerequisites=[
                ActionPrerequisite(PrerequisiteType.LEVEL, 3, ">="),
                ActionPrerequisite(PrerequisiteType.SUBCLASS, "berserker"),
                ActionPrerequisite(PrerequisiteType.COMBAT_STATE, "raging"),
                ActionPrerequisite(PrerequisiteType.COMBAT_STATE, "reckless_attack_active")
            ],
            handler_function="process_berserker_turn_start",
            handler_module="services.barbarian_abilities",
            tooltip="Automatic: add rage damage dice to first hit when raging + reckless"
        ))

        # Mindless Rage (Level 6, Berserker)
        self.register_action(ClassActionDefinition(
            id="berserker_mindless_rage",
            name="Mindless Rage",
            description="Immunity to charmed and frightened while raging",
            class_name="barbarian",
            subclass_name="berserker",
            economy_type=ActionEconomyType.FREE_ACTION,
            trigger=ActionTrigger.AUTOMATIC,
            prerequisites=[
                ActionPrerequisite(PrerequisiteType.LEVEL, 6, ">="),
                ActionPrerequisite(PrerequisiteType.SUBCLASS, "berserker"),
                ActionPrerequisite(PrerequisiteType.COMBAT_STATE, "raging")
            ],
            handler_function="apply_mindless_rage",
            handler_module="services.enhanced_subclass_manager",
            tooltip="Automatic: immune to charmed/frightened while raging"
        ))

        # Retaliation (Level 10, Berserker)
        self.register_action(ClassActionDefinition(
            id="berserker_retaliation",
            name="Retaliation",
            description="Attack an enemy that damaged you",
            class_name="barbarian",
            subclass_name="berserker",
            economy_type=ActionEconomyType.REACTION,
            trigger=ActionTrigger.REACTION,
            prerequisites=[
                ActionPrerequisite(PrerequisiteType.LEVEL, 10, ">="),
                ActionPrerequisite(PrerequisiteType.SUBCLASS, "berserker")
            ],
            target_required=True,
            handler_function="use_berserker_retaliation",
            handler_module="services.barbarian_abilities",
            tooltip="Reaction: attack an enemy that just damaged you"
        ))

        # Intimidating Presence (Level 14, Berserker)
        self.register_action(ClassActionDefinition(
            id="berserker_intimidating_presence",
            name="Intimidating Presence",
            description="Frighten enemies in 30-foot emanation",
            class_name="barbarian",
            subclass_name="berserker",
            economy_type=ActionEconomyType.BONUS_ACTION,
            prerequisites=[
                ActionPrerequisite(PrerequisiteType.LEVEL, 14, ">="),
                ActionPrerequisite(PrerequisiteType.SUBCLASS, "berserker")
            ],
            resources_consumed=[
                ActionResource("intimidating_presence_uses", 1, "long_rest")
            ],
            area_of_effect="30 ft emanation",
            handler_function="use_intimidating_presence",
            handler_module="services.barbarian_abilities",
            tooltip="Bonus action: frighten all enemies within 30 ft (Wisdom save)"
        ))

    def _meets_level_requirement(self, action: ClassActionDefinition, level: int) -> bool:
        """Check if action meets level requirement"""
        for prereq in action.prerequisites:
            if prereq.type == PrerequisiteType.LEVEL:
                if prereq.operator == ">=" and level >= prereq.value:
                    return True
                elif prereq.operator == "=" and level == prereq.value:
                    return True
                elif prereq.operator == "<=" and level <= prereq.value:
                    return True
                elif prereq.operator == ">" and level > prereq.value:
                    return True
                elif prereq.operator == "<" and level < prereq.value:
                    return True
                else:
                    return False
        return True  # No level requirement

    def _check_prerequisite(self, prereq: ActionPrerequisite, character_data: Dict, character_id: str) -> bool:
        """Check a single prerequisite"""
        if prereq.type == PrerequisiteType.LEVEL:
            level = character_data.get('level', 1)
            return self._compare_values(level, prereq.value, prereq.operator)

        elif prereq.type == PrerequisiteType.CLASS:
            class_name = character_data.get('class_name', '').lower()
            target_class = str(prereq.value).lower()
            return class_name == target_class

        elif prereq.type == PrerequisiteType.SUBCLASS:
            subclass_name = character_data.get('subclass_name', '').lower()
            target_subclass = str(prereq.value).lower()
            return subclass_name == target_subclass

        elif prereq.type == PrerequisiteType.COMBAT_STATE:
            return self._check_combat_state(character_id, prereq.value)

        elif prereq.type == PrerequisiteType.RESOURCE:
            return self._check_resource_availability(character_id, prereq.value, prereq.operator)

        return True

    def _compare_values(self, actual: Any, expected: Any, operator: str) -> bool:
        """Compare two values using the given operator"""
        if operator == "=":
            return actual == expected
        elif operator == ">=":
            return actual >= expected
        elif operator == "<=":
            return actual <= expected
        elif operator == ">":
            return actual > expected
        elif operator == "<":
            return actual < expected
        elif operator == "!=":
            return actual != expected
        elif operator == "in":
            return actual in expected
        elif operator == "not_in":
            return actual not in expected
        return False

    def _check_combat_state(self, character_id: str, state_name: str) -> bool:
        """Check character's combat state"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if state_name == "raging":
                cursor.execute("SELECT is_raging FROM barbarian_features WHERE character_id = ?", (character_id,))
                row = cursor.fetchone()
                return bool(row and row['is_raging'])

            elif state_name == "reckless_attack_active":
                cursor.execute("SELECT reckless_attack_active FROM character_combat_state WHERE character_id = ?", (character_id,))
                row = cursor.fetchone()
                return bool(row and row['reckless_attack_active'])

        return False

    def _check_resources(self, action: ClassActionDefinition, character_id: str) -> Dict[str, Any]:
        """Check if character has required resources"""
        for resource in action.resources_consumed:
            available = self._get_resource_count(character_id, resource.name)
            if available < resource.amount:
                return {
                    "available": False,
                    "reason": f"Insufficient {resource.name} ({available}/{resource.amount})"
                }

        return {"available": True}

    def _check_action_economy(self, action: ClassActionDefinition, character_id: str) -> Dict[str, Any]:
        """Check if character has action economy available"""
        # This would integrate with the existing action economy system
        # For now, assume available
        return {"available": True}

    def _get_character_data(self, character_id: str) -> Optional[Dict]:
        """Get character data from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.*, cs.subclass_id as subclass_name
                FROM characters c
                LEFT JOIN character_subclasses cs ON c.id = cs.character_id
                WHERE c.id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)

        return None

    def _get_resource_count(self, character_id: str, resource_name: str) -> int:
        """Get current count of a resource"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Map resource names to database columns
            resource_mapping = {
                "rage_uses": ("barbarian_features", "rage_uses_current"),
                "brutal_strike_uses": ("barbarian_features", "brutal_strike_uses_current"),
                "intimidating_presence_uses": ("barbarian_features", "intimidating_presence_uses_current"),
                "second_wind_uses": ("fighter_features", "second_wind_uses_current"),
                "action_surge_uses": ("fighter_features", "action_surge_uses_current")
            }

            if resource_name in resource_mapping:
                table, column = resource_mapping[resource_name]
                cursor.execute(f"SELECT {column} FROM {table} WHERE character_id = ?", (character_id,))
                row = cursor.fetchone()
                if row:
                    return row[column] or 0

        return 0


# Global registry instance
action_registry = ActionRegistry()