"""
Subclass Action Integration for TaleKeeper

Bridges the enhanced subclass manager with the action card system,
providing seamless integration for both Champion and Berserker features.
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import sqlite3

from services.enhanced_subclass_manager import (
    EnhancedSubclassManager, SubclassFeature, FeatureType, ActionCost
)


class ActionIntegrationType(Enum):
    """Types of action system integration."""
    ACTION_CARD = "action_card"  # Creates an action card
    AUTOMATIC_TRIGGER = "automatic_trigger"  # Triggers automatically
    COMBAT_MODIFIER = "combat_modifier"  # Modifies combat calculations
    REACTION_TRIGGER = "reaction_trigger"  # Available as reaction


class SubclassActionIntegration:
    """Handles integration between subclass features and action system."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.manager = EnhancedSubclassManager(db_path)

        # Register feature handlers
        self._feature_handlers = {
            # Berserker features
            "Intimidating Presence": self._handle_intimidating_presence,
            "Retaliation": self._handle_retaliation,
            "Mindless Rage": self._handle_mindless_rage,
            "Frenzy": self._handle_frenzy,

            # Champion features
            "Heroic Warrior": self._handle_heroic_warrior,
            "Survivor": self._handle_survivor,
            "Improved Critical": self._handle_improved_critical,
            "Superior Critical": self._handle_superior_critical,
            "Remarkable Athlete": self._handle_remarkable_athlete,
            "Additional Fighting Style": self._handle_additional_fighting_style
        }

    def get_action_cards_for_character(self, character_id: str, level: int) -> List[Dict[str, Any]]:
        """Get action cards that should be created for a character's subclass features."""
        features = self.manager.get_character_subclass_features(character_id, level)
        action_cards = []

        for feature in features:
            handler = self._feature_handlers.get(feature.name)
            if handler:
                card_data = handler(character_id, feature, ActionIntegrationType.ACTION_CARD)
                if card_data:
                    action_cards.append(card_data)

        return action_cards

    def get_automatic_triggers_for_character(self, character_id: str, level: int) -> List[Dict[str, Any]]:
        """Get automatic triggers that should be set up for a character."""
        features = self.manager.get_character_subclass_features(character_id, level)
        triggers = []

        for feature in features:
            handler = self._feature_handlers.get(feature.name)
            if handler:
                trigger_data = handler(character_id, feature, ActionIntegrationType.AUTOMATIC_TRIGGER)
                if trigger_data:
                    triggers.append(trigger_data)

        return triggers

    def get_combat_modifiers_for_character(self, character_id: str, level: int) -> List[Dict[str, Any]]:
        """Get combat modifiers that should be applied for a character."""
        features = self.manager.get_character_subclass_features(character_id, level)
        modifiers = []

        for feature in features:
            handler = self._feature_handlers.get(feature.name)
            if handler:
                modifier_data = handler(character_id, feature, ActionIntegrationType.COMBAT_MODIFIER)
                if modifier_data:
                    modifiers.append(modifier_data)

        return modifiers

    def activate_feature(self, character_id: str, feature_name: str) -> Dict[str, Any]:
        """Activate a subclass feature through the action system."""
        handler = self._feature_handlers.get(feature_name)
        if not handler:
            return {"success": False, "error": f"No handler for feature: {feature_name}"}

        # Get the feature definition
        features = self.manager.get_character_subclass_features(character_id, 20)  # Get all features
        feature = next((f for f in features if f.name == feature_name), None)

        if not feature:
            return {"success": False, "error": f"Feature not found: {feature_name}"}

        # Execute the handler
        try:
            result = handler(character_id, feature, "activate")
            return result if result else {"success": False, "error": "Handler returned no result"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== BERSERKER FEATURE HANDLERS ====================

    def _handle_intimidating_presence(self, character_id: str, feature: SubclassFeature,
                                    integration_type) -> Optional[Dict[str, Any]]:
        """Handle Intimidating Presence feature integration."""
        if integration_type == ActionIntegrationType.ACTION_CARD:
            return {
                "action_type": "INTIMIDATING_PRESENCE",
                "name": "Intimidating Presence",
                "description": "Frighten enemies in 30ft (DC Wis save)",
                "icon": "[FEAR]",
                "action_cost": "bonus_action",
                "uses_per_rest": 1,
                "rest_type": "long",
                "feature_data": feature
            }
        elif integration_type == "activate":
            return self.manager.use_intimidating_presence(character_id)

        return None

    def _handle_retaliation(self, character_id: str, feature: SubclassFeature,
                          integration_type) -> Optional[Dict[str, Any]]:
        """Handle Retaliation feature integration."""
        if integration_type == ActionIntegrationType.ACTION_CARD:
            return {
                "action_type": "RETALIATION",
                "name": "Retaliation",
                "description": "React when damaged by adjacent enemy (within 5ft)",
                "icon": "[COUNTER]",
                "action_cost": "reaction",
                "feature_data": feature
            }
        elif integration_type == ActionIntegrationType.REACTION_TRIGGER:
            return {
                "trigger": "damaged_by_adjacent_enemy",
                "name": "Retaliation",
                "description": "Make melee attack vs damaging enemy within 5ft",
                "prerequisites": {"enemy_within_5ft": True, "took_damage": True},
                "feature_data": feature
            }
        elif integration_type == "activate":
            return self._activate_retaliation(character_id, feature)

        return None

    def _handle_mindless_rage(self, character_id: str, feature: SubclassFeature,
                            integration_type) -> Optional[Dict[str, Any]]:
        """Handle Mindless Rage feature integration."""
        if integration_type == ActionIntegrationType.AUTOMATIC_TRIGGER:
            return {
                "trigger": "rage_start",
                "name": "Mindless Rage",
                "effect": "apply_condition_immunity",
                "conditions": ["charmed", "frightened"],
                "feature_data": feature
            }
        elif integration_type == "activate":
            return self.manager.apply_mindless_rage(character_id)

        return None

    def _handle_frenzy(self, character_id: str, feature: SubclassFeature,
                     integration_type) -> Optional[Dict[str, Any]]:
        """Handle Frenzy feature integration."""
        if integration_type == ActionIntegrationType.COMBAT_MODIFIER:
            return {
                "trigger": "reckless_attack_hit",
                "name": "Frenzy",
                "damage_bonus": self._get_frenzy_damage_dice(character_id),
                "applies_to": "first_hit_per_turn",
                "feature_data": feature
            }
        elif integration_type == "activate":
            # Frenzy is triggered automatically, not manually activated
            return {"success": True, "message": "Frenzy activates automatically with Reckless Attack while raging"}

        return None

    # ==================== CHAMPION FEATURE HANDLERS ====================

    def _handle_heroic_warrior(self, character_id: str, feature: SubclassFeature,
                             integration_type) -> Optional[Dict[str, Any]]:
        """Handle Heroic Warrior feature integration."""
        if integration_type == ActionIntegrationType.AUTOMATIC_TRIGGER:
            return {
                "trigger": "turn_start",
                "name": "Heroic Warrior",
                "effect": "gain_heroic_inspiration",
                "condition": "in_combat_and_no_inspiration",
                "limit": "once_per_turn",
                "feature_data": feature
            }
        elif integration_type == "activate":
            return self._activate_heroic_warrior(character_id)

        return None

    def _handle_survivor(self, character_id: str, feature: SubclassFeature,
                       integration_type) -> Optional[Dict[str, Any]]:
        """Handle Survivor feature integration."""
        if integration_type == ActionIntegrationType.AUTOMATIC_TRIGGER:
            return {
                "trigger": "turn_start",
                "name": "Survivor",
                "effect": "heal_if_below_half",
                "healing": "5 + constitution_modifier",
                "condition": "below_half_hp_and_at_least_1",
                "feature_data": feature
            }
        elif integration_type == "activate":
            return self._activate_survivor(character_id)

        return None

    def _handle_improved_critical(self, character_id: str, feature: SubclassFeature,
                                integration_type) -> Optional[Dict[str, Any]]:
        """Handle Improved Critical feature integration."""
        if integration_type == ActionIntegrationType.COMBAT_MODIFIER:
            return {
                "type": "critical_range",
                "name": "Improved Critical",
                "critical_range_min": 19,
                "applies_to": "weapon_attacks",
                "feature_data": feature
            }

        return None

    def _handle_superior_critical(self, character_id: str, feature: SubclassFeature,
                                integration_type) -> Optional[Dict[str, Any]]:
        """Handle Superior Critical feature integration."""
        if integration_type == ActionIntegrationType.COMBAT_MODIFIER:
            return {
                "type": "critical_range",
                "name": "Superior Critical",
                "critical_range_min": 18,
                "applies_to": "weapon_attacks",
                "replaces": "Improved Critical",
                "feature_data": feature
            }

        return None

    def _handle_remarkable_athlete(self, character_id: str, feature: SubclassFeature,
                                 integration_type) -> Optional[Dict[str, Any]]:
        """Handle Remarkable Athlete feature integration."""
        if integration_type == ActionIntegrationType.COMBAT_MODIFIER:
            return {
                "type": "ability_check_bonus",
                "name": "Remarkable Athlete",
                "bonus": "half_proficiency_rounded_up",
                "applies_to": ["strength_checks", "dexterity_checks", "constitution_checks"],
                "condition": "not_proficient",
                "feature_data": feature
            }

        return None

    def _handle_additional_fighting_style(self, character_id: str, feature: SubclassFeature,
                                        integration_type) -> Optional[Dict[str, Any]]:
        """Handle Additional Fighting Style feature integration."""
        # This is handled by the fighter abilities system, not action cards
        return None

    # ==================== ACTIVATION METHODS ====================

    def _activate_retaliation(self, character_id: str, feature: SubclassFeature) -> Dict[str, Any]:
        """Activate Retaliation reaction."""
        # Check if character can make reaction
        # For now, return success - actual combat mechanics handled elsewhere
        return {
            "success": True,
            "message": "Retaliation attack available",
            "attack_type": "melee_weapon_or_unarmed",
            "adds_rage_damage": True,
            "range": 5
        }

    def _activate_heroic_warrior(self, character_id: str) -> Dict[str, Any]:
        """Activate Heroic Warrior inspiration gain at turn start."""
        # Check if character is in combat and doesn't have Heroic Inspiration
        # For now, we'll assume this is called during the appropriate conditions
        return {
            "success": True,
            "message": "Heroic Inspiration gained at start of turn (can be used for advantage on attack, ability check, or saving throw)",
            "effect": "heroic_inspiration_gained",
            "duration": "until_used"
        }

    def _activate_survivor(self, character_id: str) -> Dict[str, Any]:
        """Activate Survivor healing."""
        # Check if conditions are met
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT current_hit_points, hit_points_max, constitution
                FROM characters WHERE id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Character not found"}

            current_hp, max_hp, constitution = row
            half_hp = max_hp // 2

            if current_hp <= 0:
                return {"success": False, "error": "Character is unconscious"}

            if current_hp > half_hp:
                return {"success": False, "error": "Character has more than half HP"}

            # Calculate healing
            con_mod = (constitution - 10) // 2 if constitution else 0
            healing = 5 + con_mod

            new_hp = min(current_hp + healing, max_hp)

            # Apply healing
            cursor.execute("""
                UPDATE characters SET current_hit_points = ? WHERE id = ?
            """, (new_hp, character_id))
            conn.commit()

            return {
                "success": True,
                "healing": healing,
                "new_hp": new_hp,
                "message": f"Survivor healing: {healing} HP (now {new_hp}/{max_hp})"
            }

    def _get_frenzy_damage_dice(self, character_id: str) -> str:
        """Get Frenzy damage dice based on character level."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            row = cursor.fetchone()

            if not row:
                return "1d6"

            level = row[0]
            if level >= 16:
                return "1d10"
            elif level >= 9:
                return "1d8"
            else:
                return "1d6"

    def trigger_automatic_feature(self, character_id: str, trigger_type: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Trigger automatic features based on game events."""
        results = []

        # Handle special rage_end triggers
        if trigger_type == "rage_end":
            features = self.manager.get_character_subclass_features(character_id, 20)
            for feature in features:
                if feature.name == "Mindless Rage":
                    result = self.manager.remove_rage_immunities(character_id)
                    result["feature_name"] = "Mindless Rage"
                    result["trigger_type"] = trigger_type
                    results.append(result)
            return results

        # Handle normal automatic triggers
        triggers = self.get_automatic_triggers_for_character(character_id, 20)  # Get all triggers

        for trigger in triggers:
            if trigger.get("trigger") == trigger_type or trigger_type in trigger.get("trigger", []):
                feature_name = trigger.get("name")
                result = self.activate_feature(character_id, feature_name)
                result["feature_name"] = feature_name
                result["trigger_type"] = trigger_type
                results.append(result)

        return results


# Singleton instance
subclass_action_integration = SubclassActionIntegration()