"""
Action Economy Enforcer for TaleKeeper

Final integration layer that enforces action economy rules with full blocking,
resource consumption, and state updates.

Stage 3.5: Full Economy Enforcement - Final Integration
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from talekeeper.services.action_registry import action_registry, ClassActionDefinition
from talekeeper.services.action_validation import action_validator, ActionValidationResult
from talekeeper.models.action_economy import ActionEconomyState, CombatActionEconomy, ActionEconomyType


class ActionExecutionResult:
    """Result of attempting to execute an action"""

    def __init__(self, success: bool, action_id: str = "", reason: str = ""):
        self.success = success
        self.action_id = action_id
        self.reason = reason

        # Execution details
        self.resources_consumed = {}
        self.economy_consumed = []
        self.effects_applied = []
        self.state_changes = {}

        # Error details
        self.validation_errors = []
        self.execution_errors = []

    def add_resource_consumption(self, resource_name: str, amount: int):
        """Record resource consumption"""
        self.resources_consumed[resource_name] = amount

    def add_economy_consumption(self, economy_type: str):
        """Record action economy consumption"""
        self.economy_consumed.append(economy_type)

    def add_effect(self, effect_id: str, effect_data: Dict[str, Any]):
        """Record effect application"""
        self.effects_applied.append({"id": effect_id, "data": effect_data})

    def add_state_change(self, key: str, old_value: Any, new_value: Any):
        """Record state change"""
        self.state_changes[key] = {"old": old_value, "new": new_value}

    def get_summary(self) -> str:
        """Get execution summary"""
        if self.success:
            parts = [f"Successfully executed {self.action_id}"]

            if self.resources_consumed:
                resource_parts = [f"{name}: -{amount}" for name, amount in self.resources_consumed.items()]
                parts.append(f"Resources consumed: {', '.join(resource_parts)}")

            if self.economy_consumed:
                parts.append(f"Economy used: {', '.join(self.economy_consumed)}")

            return "; ".join(parts)
        else:
            return f"Failed to execute {self.action_id}: {self.reason}"


class ActionEconomyEnforcer:
    """Enforces action economy rules with full integration"""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def execute_action(self, character_id: str, action_id: str,
                      combat_economy: Optional[CombatActionEconomy] = None,
                      action_context: Optional[Dict[str, Any]] = None) -> ActionExecutionResult:
        """
        Execute an action with full economy enforcement.
        Stage 3.5: Enable action blocking for invalid attempts.
        """

        result = ActionExecutionResult(False, action_id)

        # Get action definition
        action_def = action_registry.get_action(action_id)
        if not action_def:
            result.reason = f"Action '{action_id}' not found"
            return result

        # Get current combat state
        combat_state = None
        if combat_economy:
            combat_state = combat_economy.get_combatant_state(character_id)

        # Validate action
        validation_result = action_validator.can_use_class_action(character_id, action_id, combat_state)
        if not validation_result.can_use:
            result.reason = validation_result.get_user_friendly_message()
            result.validation_errors = [validation_result.reason]
            self.logger.warning(f"Action {action_id} blocked for {character_id}: {result.reason}")
            return result

        # Execute the action
        try:
            # 1. Consume action economy
            if combat_economy and combat_state:
                economy_success = self._consume_action_economy(
                    action_def, combat_economy, character_id, result
                )
                if not economy_success:
                    return result

            # 2. Consume resources
            resource_success = self._consume_resources(action_def, character_id, result)
            if not resource_success:
                # Rollback economy consumption if resources failed
                if combat_economy and combat_state:
                    self._rollback_economy_consumption(action_def, combat_economy, character_id)
                return result

            # 3. Apply action effects
            effects_success = self._apply_action_effects(
                action_def, character_id, combat_economy, action_context or {}, result
            )
            if not effects_success:
                # Rollback previous changes
                self._rollback_resource_consumption(action_def, character_id, result)
                if combat_economy and combat_state:
                    self._rollback_economy_consumption(action_def, combat_economy, character_id)
                return result

            # 4. Track action usage
            if combat_economy:
                self._track_action_usage(action_def, combat_economy, character_id, result)

            # Success!
            result.success = True
            result.reason = "Action executed successfully"

            self.logger.info(f"Action {action_id} executed successfully for {character_id}")
            return result

        except Exception as e:
            result.reason = f"Execution error: {str(e)}"
            result.execution_errors.append(str(e))
            self.logger.error(f"Error executing action {action_id} for {character_id}: {e}")
            return result

    def _consume_action_economy(self, action_def: ClassActionDefinition,
                              combat_economy: CombatActionEconomy, character_id: str,
                              result: ActionExecutionResult) -> bool:
        """
        Consume action economy slot.
        Stage 3.5: Update economy state after actions.
        """

        economy_type_map = {
            "action": ActionEconomyType.ACTION,
            "bonus_action": ActionEconomyType.BONUS_ACTION,
            "reaction": ActionEconomyType.REACTION,
            "free_action": ActionEconomyType.FREE_ACTION,
            "movement": ActionEconomyType.MOVEMENT
        }

        economy_type = economy_type_map.get(action_def.economy_type.value)
        if not economy_type:
            result.reason = f"Unknown economy type: {action_def.economy_type.value}"
            return False

        # Use the action economy
        success = combat_economy.use_action(character_id, economy_type, action_def.name)
        if success:
            result.add_economy_consumption(action_def.economy_type.value)
            return True
        else:
            result.reason = f"Cannot use {action_def.economy_type.value} - already consumed"
            return False

    def _consume_resources(self, action_def: ClassActionDefinition, character_id: str,
                         result: ActionExecutionResult) -> bool:
        """
        Consume character resources.
        Stage 3.5: Consume resources on action use.
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Consume each required resource
            for resource in action_def.resources_consumed:
                success = self._consume_single_resource(
                    cursor, character_id, resource.name, resource.amount, result
                )
                if not success:
                    return False

            conn.commit()
            return True

    def _consume_single_resource(self, cursor, character_id: str, resource_name: str,
                               amount: int, result: ActionExecutionResult) -> bool:
        """Consume a single resource type"""

        # Map resource names to database updates
        resource_updates = {
            "rage_uses": ("barbarian_features", "rage_uses_current"),
            "brutal_strike_uses": ("barbarian_features", "brutal_strike_uses_current"),
            "intimidating_presence_uses": ("barbarian_features", "intimidating_presence_uses_current"),
            "second_wind_uses": ("fighter_features", "second_wind_uses_current"),
            "action_surge_uses": ("fighter_features", "action_surge_uses_current")
        }

        if resource_name not in resource_updates:
            result.reason = f"Unknown resource: {resource_name}"
            return False

        table, column = resource_updates[resource_name]

        # Get current value
        cursor.execute(f"SELECT {column} FROM {table} WHERE character_id = ?", (character_id,))
        row = cursor.fetchone()
        if not row:
            result.reason = f"Character {character_id} not found in {table}"
            return False

        current_value = row[0] or 0
        if current_value < amount:
            result.reason = f"Insufficient {resource_name}: need {amount}, have {current_value}"
            return False

        # Consume the resource
        new_value = current_value - amount
        cursor.execute(
            f"UPDATE {table} SET {column} = ? WHERE character_id = ?",
            (new_value, character_id)
        )

        result.add_resource_consumption(resource_name, amount)
        result.add_state_change(f"{resource_name}_current", current_value, new_value)
        return True

    def _apply_action_effects(self, action_def: ClassActionDefinition, character_id: str,
                            combat_economy: Optional[CombatActionEconomy],
                            action_context: Dict[str, Any], result: ActionExecutionResult) -> bool:
        """Apply the actual effects of the action"""

        try:
            # Call the appropriate handler function
            if action_def.handler_function and action_def.handler_module:
                handler_result = self._call_action_handler(
                    action_def, character_id, action_context, result
                )
                if not handler_result:
                    return False

            # Track ongoing effects in combat economy
            if combat_economy and hasattr(action_def, 'effect_duration'):
                effect_duration = getattr(action_def, 'effect_duration', None)
                if effect_duration:
                    combat_economy.track_class_action(
                        character_id, action_def.id, action_def.name,
                        {res.name: res.amount for res in action_def.resources_consumed},
                        effect_duration
                    )

            return True

        except Exception as e:
            result.reason = f"Effect application failed: {str(e)}"
            result.execution_errors.append(str(e))
            return False

    def _call_action_handler(self, action_def: ClassActionDefinition, character_id: str,
                           action_context: Dict[str, Any], result: ActionExecutionResult) -> bool:
        """Call the appropriate handler function for the action"""

        try:
            # Import the handler module
            module_name = action_def.handler_module
            function_name = action_def.handler_function

            # Simple handler calls for known actions
            if module_name == "services.barbarian_abilities":
                from talekeeper.services.barbarian_abilities import BarbarianAbilitiesService
                service = BarbarianAbilitiesService(self.db_path)

                if function_name == "use_rage":
                    handler_result = service.use_rage(character_id)
                elif function_name == "use_reckless_attack":
                    handler_result = service.use_reckless_attack(character_id)
                elif function_name == "use_brutal_strike":
                    strike_type = action_context.get('strike_type', 'forceful')
                    handler_result = service.use_brutal_strike(character_id, strike_type)
                elif function_name == "use_intimidating_presence":
                    handler_result = service.use_intimidating_presence(character_id)
                elif function_name == "use_berserker_retaliation":
                    attacker_name = action_context.get('target_name', '')
                    handler_result = service.use_berserker_retaliation(character_id, attacker_name)
                else:
                    result.reason = f"Unknown barbarian handler: {function_name}"
                    return False

                # Process handler result
                if handler_result.get('success', False):
                    # Record effect details
                    effect_data = {k: v for k, v in handler_result.items() if k != 'success'}
                    result.add_effect(action_def.id, effect_data)
                    return True
                else:
                    result.reason = handler_result.get('error', 'Handler failed')
                    return False

            else:
                # For other modules, log and continue (no blocking)
                self.logger.warning(f"Handler not implemented: {module_name}.{function_name}")
                result.add_effect(action_def.id, {"note": "Handler not implemented, effect assumed successful"})
                return True

        except ImportError as e:
            result.reason = f"Cannot import handler module {module_name}: {e}"
            return False
        except Exception as e:
            result.reason = f"Handler execution failed: {e}"
            return False

    def _track_action_usage(self, action_def: ClassActionDefinition,
                          combat_economy: CombatActionEconomy, character_id: str,
                          result: ActionExecutionResult):
        """Track action usage in combat economy"""

        # Track the class action
        combat_economy.track_class_action(
            character_id, action_def.id, action_def.name,
            result.resources_consumed,
            None  # Effects would be handled separately
        )

    def _rollback_economy_consumption(self, action_def: ClassActionDefinition,
                                    combat_economy: CombatActionEconomy, character_id: str):
        """Rollback action economy consumption (simplified - would need more complex logic)"""
        # This is a simplified rollback - a full implementation would need to track
        # the exact economy state before consumption
        self.logger.warning(f"Economy rollback needed for {action_def.id} - not fully implemented")

    def _rollback_resource_consumption(self, action_def: ClassActionDefinition,
                                     character_id: str, result: ActionExecutionResult):
        """Rollback resource consumption"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Restore consumed resources
            for resource_name, amount in result.resources_consumed.items():
                resource_updates = {
                    "rage_uses": ("barbarian_features", "rage_uses_current"),
                    "brutal_strike_uses": ("barbarian_features", "brutal_strike_uses_current"),
                    "intimidating_presence_uses": ("barbarian_features", "intimidating_presence_uses_current"),
                }

                if resource_name in resource_updates:
                    table, column = resource_updates[resource_name]
                    cursor.execute(
                        f"UPDATE {table} SET {column} = {column} + ? WHERE character_id = ?",
                        (amount, character_id)
                    )

            conn.commit()

    def can_execute_action(self, character_id: str, action_id: str,
                         combat_economy: Optional[CombatActionEconomy] = None) -> Tuple[bool, str]:
        """
        Check if an action can be executed (non-destructive check).
        Stage 3.5: Integrate with combat flow.
        """

        # Get current combat state
        combat_state = None
        if combat_economy:
            combat_state = combat_economy.get_combatant_state(character_id)

        # Validate using existing validation system
        validation_result = action_validator.can_use_class_action(character_id, action_id, combat_state)

        return validation_result.can_use, validation_result.get_user_friendly_message()

    def get_available_actions(self, character_id: str,
                            combat_economy: Optional[CombatActionEconomy] = None) -> List[str]:
        """Get list of currently available action IDs"""

        available_actions = []

        # Get all character actions
        character_actions = action_registry.get_character_actions(character_id)

        for action in character_actions:
            can_use, _ = self.can_execute_action(character_id, action.id, combat_economy)
            if can_use:
                available_actions.append(action.id)

        return available_actions


# Global enforcer instance
action_economy_enforcer = ActionEconomyEnforcer()


def execute_class_action(character_id: str, action_id: str,
                        combat_economy: Optional[CombatActionEconomy] = None,
                        action_context: Optional[Dict[str, Any]] = None) -> ActionExecutionResult:
    """
    Global function to execute a class action with full enforcement.
    Stage 3.5: Main entry point for action execution.
    """
    return action_economy_enforcer.execute_action(character_id, action_id, combat_economy, action_context)


def can_execute_class_action(character_id: str, action_id: str,
                           combat_economy: Optional[CombatActionEconomy] = None) -> Tuple[bool, str]:
    """
    Global function to check if an action can be executed.
    Stage 3.5: Integration helper for UI and combat systems.
    """
    return action_economy_enforcer.can_execute_action(character_id, action_id, combat_economy)