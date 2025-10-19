# core
# core
"""
Action Validation Layer for TaleKeeper

Provides validation for class actions without blocking existing functionality.
Integrates action registry with current combat state to provide warnings
and feedback about action availability.

Stage 3.3: Safety layer that warns but doesn't block yet.
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from services.action_registry import action_registry, ClassActionDefinition
from models.action_economy import ActionEconomyState, CombatActionEconomy, ActionEconomyType


class ActionValidationResult:
    """Result of action validation with detailed feedback"""

    def __init__(self, can_use: bool, action_id: str = "", reason: str = ""):
        self.can_use = can_use
        self.action_id = action_id
        self.reason = reason
        self.warnings = []
        self.prerequisites_failed = []
        self.resources_insufficient = []
        self.economy_blocked = []

    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)

    def add_prerequisite_failure(self, prereq_type: str, expected: Any, actual: Any):
        """Add a failed prerequisite"""
        self.prerequisites_failed.append({
            "type": prereq_type,
            "expected": expected,
            "actual": actual
        })

    def add_resource_shortage(self, resource: str, needed: int, available: int):
        """Add a resource shortage"""
        self.resources_insufficient.append({
            "resource": resource,
            "needed": needed,
            "available": available
        })

    def add_economy_block(self, economy_type: str, reason: str):
        """Add an action economy block"""
        self.economy_blocked.append({
            "economy_type": economy_type,
            "reason": reason
        })

    def get_user_friendly_message(self) -> str:
        """Get a user-friendly explanation of why action can't be used"""
        if self.can_use:
            return "Action is available"

        messages = []

        # Prerequisites
        for failure in self.prerequisites_failed:
            if failure["type"] == "level":
                messages.append(f"Requires level {failure['expected']} (currently {failure['actual']})")
            elif failure["type"] == "class":
                messages.append(f"Requires {failure['expected']} class")
            elif failure["type"] == "subclass":
                messages.append(f"Requires {failure['expected']} subclass")
            elif failure["type"] == "combat_state":
                messages.append(f"Requires {failure['expected']} to be active")

        # Resources
        for shortage in self.resources_insufficient:
            available = shortage['available']
            needed = shortage['needed']
            resource = shortage['resource'].replace('_', ' ').title()
            if available == 0:
                messages.append(f"No {resource} remaining")
            else:
                messages.append(f"Insufficient {resource} ({available}/{needed})")

        # Action Economy
        for block in self.economy_blocked:
            economy_type = block['economy_type'].replace('_', ' ').title()
            messages.append(f"{economy_type} already used")

        return "; ".join(messages) if messages else self.reason


class ActionValidator:
    """Validates actions using registry and current state"""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def can_use_class_action(self, character_id: str, action_id: str,
                           combat_state: Optional[ActionEconomyState] = None) -> ActionValidationResult:
        """
        Check if a character can use a specific class action.
        Stage 3.3: Comprehensive validation with detailed feedback.
        """
        result = ActionValidationResult(False, action_id)

        # Get action definition
        action_def = action_registry.get_action(action_id)
        if not action_def:
            result.reason = f"Action '{action_id}' not found in registry"
            result.add_warning(f"Unknown action: {action_id}")
            return result

        # Check prerequisites using registry
        registry_check = action_registry.can_use_action(action_id, character_id)
        if not registry_check["can_use"]:
            result.reason = registry_check["reason"]
            self._parse_registry_failures(result, registry_check, action_def, character_id)

        # Check action economy if combat is active
        if combat_state:
            economy_check = self._check_action_economy(action_def, combat_state)
            if not economy_check["can_use"]:
                result.add_economy_block(action_def.economy_type.value, economy_check["reason"])
                if result.can_use:  # Only fail if not already failed
                    result.can_use = False
                    result.reason = economy_check["reason"]

        # If all checks passed
        if not result.prerequisites_failed and not result.resources_insufficient and not result.economy_blocked:
            result.can_use = True
            result.reason = "Action is available"

        return result

    def _parse_registry_failures(self, result: ActionValidationResult,
                                registry_check: Dict[str, Any], action_def: ClassActionDefinition,
                                character_id: str):
        """Parse failures from registry check into detailed result"""

        # Check individual prerequisites
        character_data = self._get_character_data(character_id)
        if not character_data:
            result.add_prerequisite_failure("character", "exists", "not found")
            return

        for prereq in action_def.prerequisites:
            if not self._check_single_prerequisite(prereq, character_data, character_id):
                if prereq.type.name == "LEVEL":
                    result.add_prerequisite_failure(
                        "level", prereq.value, character_data.get('level', 1)
                    )
                elif prereq.type.name == "CLASS":
                    result.add_prerequisite_failure(
                        "class", prereq.value, character_data.get('class_name', 'Unknown')
                    )
                elif prereq.type.name == "SUBCLASS":
                    result.add_prerequisite_failure(
                        "subclass", prereq.value, character_data.get('subclass_name', 'None')
                    )
                elif prereq.type.name == "COMBAT_STATE":
                    result.add_prerequisite_failure(
                        "combat_state", prereq.value, "inactive"
                    )

        # Check resources
        for resource in action_def.resources_consumed:
            available = self._get_resource_count(character_id, resource.name)
            if available < resource.amount:
                result.add_resource_shortage(resource.name, resource.amount, available)

    def _check_action_economy(self, action_def: ClassActionDefinition,
                            combat_state: ActionEconomyState) -> Dict[str, Any]:
        """Check if action economy allows this action"""

        economy_type = action_def.economy_type

        if economy_type == ActionEconomyType.ACTION:
            if not combat_state.action_available:
                return {"can_use": False, "reason": "Action already used this turn"}

        elif economy_type == ActionEconomyType.BONUS_ACTION:
            if not combat_state.bonus_action_available:
                return {"can_use": False, "reason": "Bonus action already used this turn"}

        elif economy_type == ActionEconomyType.REACTION:
            if not combat_state.reaction_available:
                return {"can_use": False, "reason": "Reaction already used this round"}

        elif economy_type == ActionEconomyType.MOVEMENT:
            # Movement checks would be more complex
            pass

        return {"can_use": True}

    def get_action_availability(self, character_id: str,
                              combat_state: Optional[ActionEconomyState] = None) -> Dict[str, ActionValidationResult]:
        """
        Get availability for all actions for a character.
        Stage 3.3: Action availability calculator.
        """

        results = {}

        # Get all character actions from registry
        character_actions = action_registry.get_character_actions(character_id)

        for action in character_actions:
            validation_result = self.can_use_class_action(character_id, action.id, combat_state)
            results[action.id] = validation_result

            # Log warnings but don't block (Stage 3.3 requirement)
            if not validation_result.can_use:
                self.logger.warning(
                    f"Action '{action.id}' unavailable for character {character_id}: "
                    f"{validation_result.get_user_friendly_message()}"
                )

        return results

    def validate_action_with_feedback(self, character_id: str, action_id: str,
                                    combat_state: Optional[ActionEconomyState] = None) -> Tuple[bool, str, List[str]]:
        """
        Validate action and return detailed feedback.
        Stage 3.3: Feedback system for unavailable actions.

        Returns:
            (can_use, primary_reason, detailed_warnings)
        """

        validation_result = self.can_use_class_action(character_id, action_id, combat_state)

        # Prepare detailed warnings
        detailed_warnings = []

        if validation_result.warnings:
            detailed_warnings.extend(validation_result.warnings)

        if validation_result.prerequisites_failed:
            for failure in validation_result.prerequisites_failed:
                if failure["type"] == "level":
                    detailed_warnings.append(
                        f"⚠️ Level requirement not met: need {failure['expected']}, have {failure['actual']}"
                    )
                elif failure["type"] == "class":
                    detailed_warnings.append(f"⚠️ Wrong class: need {failure['expected']}")
                elif failure["type"] == "subclass":
                    detailed_warnings.append(f"⚠️ Wrong subclass: need {failure['expected']}")

        if validation_result.resources_insufficient:
            for shortage in validation_result.resources_insufficient:
                resource_name = shortage['resource'].replace('_', ' ').title()
                detailed_warnings.append(
                    f"⚠️ Insufficient {resource_name}: need {shortage['needed']}, have {shortage['available']}"
                )

        if validation_result.economy_blocked:
            for block in validation_result.economy_blocked:
                economy_name = block['economy_type'].replace('_', ' ').title()
                detailed_warnings.append(f"⚠️ {economy_name} already used this turn")

        return validation_result.can_use, validation_result.get_user_friendly_message(), detailed_warnings

    def log_action_attempt(self, character_id: str, action_id: str, success: bool, reason: str = ""):
        """Log action attempts for debugging and analysis"""
        timestamp = datetime.now().isoformat()

        log_message = (
            f"[ACTION_VALIDATION] {timestamp} - Character {character_id} "
            f"{'SUCCESS' if success else 'FAILED'} using {action_id}"
        )

        if reason:
            log_message += f" - {reason}"

        if success:
            self.logger.info(log_message)
        else:
            self.logger.warning(log_message)

    def _check_single_prerequisite(self, prereq, character_data: Dict, character_id: str) -> bool:
        """Check a single prerequisite - reuse logic from action registry"""
        # This is a simplified version - the full logic is in action_registry
        from services.action_registry import ActionRegistry
        registry = ActionRegistry(self.db_path)
        return registry._check_prerequisite(prereq, character_data, character_id)

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

            # Map resource names to database columns (same as action registry)
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


# Global validator instance
action_validator = ActionValidator()


def can_use_class_action(character_id: str, action_id: str,
                        combat_state: Optional[ActionEconomyState] = None) -> ActionValidationResult:
    """
    Global function for checking if a class action can be used.
    Stage 3.3: Main validation entry point.
    """
    return action_validator.can_use_class_action(character_id, action_id, combat_state)


def get_action_feedback(character_id: str, action_id: str,
                       combat_state: Optional[ActionEconomyState] = None) -> Tuple[bool, str, List[str]]:
    """
    Global function for getting detailed action feedback.
    Stage 3.3: User-friendly feedback system.
    """
    return action_validator.validate_action_with_feedback(character_id, action_id, combat_state)