# core
# core
"""
Action Card Generator for Enhanced Action Economy

Generates action cards from the action registry with economy state awareness.
Stage 3.4: UI Integration for action economy system.
"""

from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from services.action_registry import action_registry, ClassActionDefinition
from services.action_validation import action_validator, ActionValidationResult
from models.action_economy import ActionEconomyState


class EnhancedActionCard:
    """Enhanced action card with economy state awareness"""

    def __init__(self, action_def: ClassActionDefinition, validation_result: ActionValidationResult):
        self.action_def = action_def
        self.validation_result = validation_result

        # Basic card properties
        self.action_id = action_def.id
        self.name = action_def.name
        self.description = action_def.description
        self.icon = action_def.icon or self._get_default_icon()
        self.tooltip = action_def.tooltip or action_def.description
        self.tooltip_extended = action_def.tooltip_extended

        # Economy and availability
        self.available = validation_result.can_use
        self.reason_unavailable = validation_result.get_user_friendly_message()
        self.economy_type = action_def.economy_type.value
        self.resource_costs = self._format_resource_costs()

        # Visual states
        self.disabled_reason = None if self.available else self.reason_unavailable
        self.warning_badges = self._get_warning_badges()
        self.cost_display = self._get_cost_display()

    def _get_default_icon(self) -> str:
        """Get default icon based on action type"""
        economy_icons = {
            "action": "⚔️",
            "bonus_action": "✨",
            "reaction": "🛡️",
            "free_action": "🔄",
            "movement": "👣"
        }
        return economy_icons.get(self.action_def.economy_type.value, "❓")

    def _format_resource_costs(self) -> List[str]:
        """Format resource costs for display"""
        costs = []
        for resource in self.action_def.resources_consumed:
            resource_name = resource.name.replace('_', ' ').title()
            if resource.amount == 1:
                costs.append(resource_name)
            else:
                costs.append(f"{resource_name} x{resource.amount}")
        return costs

    def _get_warning_badges(self) -> List[str]:
        """Get warning badges for the card"""
        badges = []

        if not self.available:
            if self.validation_result.prerequisites_failed:
                badges.append("⚠️ Prerequisites")
            if self.validation_result.resources_insufficient:
                badges.append("❌ Resources")
            if self.validation_result.economy_blocked:
                badges.append("🕐 Economy")

        return badges

    def _get_cost_display(self) -> str:
        """Get cost display string for the card"""
        parts = []

        # Economy cost
        economy_display = {
            "action": "Action",
            "bonus_action": "Bonus",
            "reaction": "Reaction",
            "free_action": "Free",
            "movement": "Movement"
        }
        parts.append(economy_display.get(self.economy_type, self.economy_type.title()))

        # Resource costs
        if self.resource_costs:
            parts.extend(self.resource_costs)

        return " + ".join(parts)

    def get_enhanced_description(self) -> str:
        """Get description with cost and availability info"""
        base_desc = self.description

        # Add cost information
        if self.cost_display:
            base_desc += f"\n\nCost: {self.cost_display}"

        # Add availability information
        if not self.available:
            base_desc += f"\n\n❌ Unavailable: {self.reason_unavailable}"

        return base_desc

    def get_card_style_class(self) -> str:
        """Get CSS class for card styling"""
        if not self.available:
            return "action-card-disabled"
        elif self.validation_result.warnings:
            return "action-card-warning"
        else:
            return "action-card-available"


class ActionCardGenerator:
    """Generates action cards from registry with economy awareness"""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def generate_character_action_cards(self, character_id: str,
                                      combat_state: Optional[ActionEconomyState] = None) -> List[EnhancedActionCard]:
        """
        Generate all available action cards for a character.
        Stage 3.4: Generate action cards from registry.
        """

        enhanced_cards = []

        # Get all character actions from registry
        character_actions = action_registry.get_character_actions(character_id)

        for action_def in character_actions:
            # Validate action availability
            validation_result = action_validator.can_use_class_action(
                character_id, action_def.id, combat_state
            )

            # Create enhanced action card
            enhanced_card = EnhancedActionCard(action_def, validation_result)
            enhanced_cards.append(enhanced_card)

        return enhanced_cards

    def generate_class_action_cards(self, character_id: str, class_name: str, level: int,
                                  combat_state: Optional[ActionEconomyState] = None) -> List[EnhancedActionCard]:
        """Generate action cards for a specific class at a given level"""

        enhanced_cards = []

        # Get class actions from registry
        class_actions = action_registry.get_class_actions(class_name, level)

        for action_def in class_actions:
            # Validate action availability
            validation_result = action_validator.can_use_class_action(
                character_id, action_def.id, combat_state
            )

            # Create enhanced action card
            enhanced_card = EnhancedActionCard(action_def, validation_result)
            enhanced_cards.append(enhanced_card)

        return enhanced_cards

    def get_action_cards_by_economy_type(self, character_id: str,
                                       combat_state: Optional[ActionEconomyState] = None) -> Dict[str, List[EnhancedActionCard]]:
        """
        Get action cards grouped by economy type.
        Stage 3.4: Show availability based on economy state.
        """

        all_cards = self.generate_character_action_cards(character_id, combat_state)

        grouped_cards = {
            "action": [],
            "bonus_action": [],
            "reaction": [],
            "free_action": [],
            "movement": []
        }

        for card in all_cards:
            economy_type = card.economy_type
            if economy_type in grouped_cards:
                grouped_cards[economy_type].append(card)

        return grouped_cards

    def get_available_action_cards(self, character_id: str,
                                 combat_state: Optional[ActionEconomyState] = None) -> List[EnhancedActionCard]:
        """Get only currently available action cards"""

        all_cards = self.generate_character_action_cards(character_id, combat_state)
        return [card for card in all_cards if card.available]

    def get_unavailable_action_cards(self, character_id: str,
                                   combat_state: Optional[ActionEconomyState] = None) -> List[EnhancedActionCard]:
        """
        Get unavailable action cards with reasons.
        Stage 3.4: Add disabled states with reasons.
        """

        all_cards = self.generate_character_action_cards(character_id, combat_state)
        return [card for card in all_cards if not card.available]

    def create_legacy_action_card(self, enhanced_card: EnhancedActionCard, parent: Optional[QWidget] = None):
        """
        Create a legacy ActionCard widget from an EnhancedActionCard.
        This allows integration with existing UI code.
        """

        # Import here to avoid circular imports
        from action_cards.action_panel import ActionCard, ActionType

        # Map action_id to ActionType enum if possible
        action_type_map = {
            "barbarian_rage": ActionType.RAGE,
            "barbarian_reckless_attack": ActionType.RECKLESS_ATTACK,
            "berserker_intimidating_presence": ActionType.INTIMIDATING_PRESENCE,
            "berserker_retaliation": ActionType.RETALIATION,
            # Add more mappings as needed
        }

        action_type = action_type_map.get(enhanced_card.action_id, enhanced_card.action_id)

        # Create legacy card
        card = ActionCard(
            action_type=action_type,
            icon=enhanced_card.icon,
            name=enhanced_card.name,
            description=enhanced_card.get_enhanced_description(),
            parent=parent
        )

        # Set availability and styling
        card.available = enhanced_card.available
        if enhanced_card.disabled_reason:
            card.setToolTip(f"{enhanced_card.tooltip}\n\nUnavailable: {enhanced_card.disabled_reason}")
        else:
            card.setToolTip(enhanced_card.tooltip)

        # Store enhanced data for reference
        card.enhanced_data = enhanced_card

        return card

    def get_resource_summary(self, character_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get summary of character resources for display.
        Stage 3.4: Display resource costs on cards.
        """

        resource_summary = {}

        # Get character actions to find all resources
        character_actions = action_registry.get_character_actions(character_id)

        # Collect all resource types
        resource_types = set()
        for action in character_actions:
            for resource in action.resources_consumed:
                resource_types.add(resource.name)

        # Get current counts for each resource
        for resource_name in resource_types:
            current = action_validator._get_resource_count(character_id, resource_name)

            # Get max from database (simplified - would need more complex logic for actual max)
            resource_display_name = resource_name.replace('_', ' ').title()

            resource_summary[resource_name] = {
                "display_name": resource_display_name,
                "current": current,
                "max": current,  # Simplified - actual max would come from character features
                "percent": 100 if current > 0 else 0
            }

        return resource_summary


# Global generator instance
action_card_generator = ActionCardGenerator()


def generate_action_cards_for_character(character_id: str,
                                       combat_state: Optional[ActionEconomyState] = None) -> List[EnhancedActionCard]:
    """
    Global function to generate action cards for a character.
    Stage 3.4: Main entry point for UI integration.
    """
    return action_card_generator.generate_character_action_cards(character_id, combat_state)


def get_action_cards_by_availability(character_id: str,
                                    combat_state: Optional[ActionEconomyState] = None) -> Tuple[List[EnhancedActionCard], List[EnhancedActionCard]]:
    """
    Get action cards split by availability.
    Returns: (available_cards, unavailable_cards)
    """
    available = action_card_generator.get_available_action_cards(character_id, combat_state)
    unavailable = action_card_generator.get_unavailable_action_cards(character_id, combat_state)
    return available, unavailable