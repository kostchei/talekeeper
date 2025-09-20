"""
Condition Stat Modification Service

Automatically applies condition effects to character stats and mechanics.
This service integrates with the condition system to provide automatic
stat modifications based on active conditions.
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

try:
    from services.condition_manager import ConditionManager, ConditionType, ConditionEffects
except ImportError:
    ConditionManager = None
    ConditionType = None
    ConditionEffects = None


class StatModificationType(Enum):
    """Types of stat modifications conditions can apply."""
    MOVEMENT_SPEED = "movement_speed"
    ATTACK_ROLL = "attack_roll"
    DAMAGE_ROLL = "damage_roll"
    SAVING_THROW = "saving_throw"
    ABILITY_CHECK = "ability_check"
    SKILL_CHECK = "skill_check"
    INITIATIVE = "initiative"
    ARMOR_CLASS = "armor_class"
    HIT_POINTS = "hit_points"


class ConditionStatService:
    """Service for applying condition effects to character stats."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        if ConditionManager:
            self.condition_manager = ConditionManager(db_path)
        else:
            self.condition_manager = None

    def get_character_base_speed(self, character_id: str) -> int:
        """Get character's base movement speed from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT speed FROM characters WHERE id = ?", (character_id,))
                row = cursor.fetchone()
                return row['speed'] if row else 30
        except Exception:
            return 30

    def get_movement_speed_modifier(self, character_id: str, base_speed: int = None) -> int:
        """Get modified movement speed based on conditions."""
        if not self.condition_manager:
            return base_speed or self.get_character_base_speed(character_id)

        # Use character's actual base speed if not provided
        if base_speed is None:
            base_speed = self.get_character_base_speed(character_id)

        conditions = self.condition_manager.get_active_conditions(character_id)
        final_speed = base_speed

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Check for speed = 0 effects (grappled, restrained, paralyzed, etc.)
            movement_speed_effect = effects.get("movement_speed")
            if movement_speed_effect == 0:
                return 0

            # Check for exhaustion speed reduction
            if condition.condition_type == ConditionType.EXHAUSTION:
                reduction = condition.exhaustion_level * 5
                final_speed = max(0, final_speed - reduction)

        return final_speed

    def get_attack_roll_modifier(self, character_id: str, attack_type: str = "any") -> Dict[str, Any]:
        """
        Get attack roll modifiers from conditions.

        Returns:
            dict with keys: advantage, disadvantage, bonus, penalty
        """
        if not self.condition_manager:
            return {"advantage": False, "disadvantage": False, "bonus": 0, "penalty": 0}

        conditions = self.condition_manager.get_active_conditions(character_id)
        result = {
            "advantage": False,
            "disadvantage": False,
            "bonus": 0,
            "penalty": 0,
            "sources": []
        }

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Check for attack disadvantage (poisoned, frightened, prone, restrained, blinded)
            if effects.get("attack_rolls") == "disadvantage":
                result["disadvantage"] = True
                result["sources"].append(f"{condition.condition_type.value} (disadvantage)")

            # Check for attack advantage (invisible)
            if effects.get("attack_rolls") == "advantage":
                result["advantage"] = True
                result["sources"].append(f"{condition.condition_type.value} (advantage)")


            # Check for exhaustion penalties
            if condition.condition_type == ConditionType.EXHAUSTION:
                penalty = condition.exhaustion_level * 2
                result["penalty"] += penalty
                result["sources"].append(f"Exhaustion {condition.exhaustion_level} (-{penalty})")

        return result

    def get_saving_throw_modifier(self, character_id: str, ability: str) -> Dict[str, Any]:
        """Get saving throw modifiers from conditions."""
        if not self.condition_manager:
            return {"advantage": False, "disadvantage": False, "auto_fail": False, "bonus": 0, "penalty": 0}

        conditions = self.condition_manager.get_active_conditions(character_id)
        result = {
            "advantage": False,
            "disadvantage": False,
            "auto_fail": False,
            "bonus": 0,
            "penalty": 0,
            "sources": []
        }

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Check for auto-fail saves
            auto_fails = effects.get("saving_throws", {})
            if isinstance(auto_fails, dict) and auto_fails.get(ability.lower()) == "auto_fail":
                result["auto_fail"] = True
                result["sources"].append(f"{condition.condition_type.value} (auto-fail)")

            # Check for dexterity save disadvantage (restrained)
            if ability.lower() == "dexterity" and effects.get("dexterity_saves") == "disadvantage":
                result["disadvantage"] = True
                result["sources"].append(f"{condition.condition_type.value} (disadvantage)")

            # Check for exhaustion penalties
            if condition.condition_type == ConditionType.EXHAUSTION:
                penalty = condition.exhaustion_level * 2
                result["penalty"] += penalty
                result["sources"].append(f"Exhaustion {condition.exhaustion_level} (-{penalty})")

        return result

    def get_ability_check_modifier(self, character_id: str, ability: str) -> Dict[str, Any]:
        """Get ability check modifiers from conditions."""
        if not self.condition_manager:
            return {"advantage": False, "disadvantage": False, "bonus": 0, "penalty": 0}

        conditions = self.condition_manager.get_active_conditions(character_id)
        result = {
            "advantage": False,
            "disadvantage": False,
            "bonus": 0,
            "penalty": 0,
            "sources": []
        }

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Check for ability check disadvantage (poisoned)
            if effects.get("ability_checks") == "disadvantage":
                result["disadvantage"] = True
                result["sources"].append(f"{condition.condition_type.value} (disadvantage)")


            # Check for sight/hearing auto-fails
            if ability.lower() in ["perception", "investigation"]:
                if effects.get("auto_fail_sight_checks") and "sight" in ability.lower():
                    result["penalty"] = 999  # Effectively auto-fail
                    result["sources"].append(f"{condition.condition_type.value} (sight auto-fail)")
                if effects.get("auto_fail_hearing_checks") and "hearing" in ability.lower():
                    result["penalty"] = 999  # Effectively auto-fail
                    result["sources"].append(f"{condition.condition_type.value} (hearing auto-fail)")

            # Check for exhaustion penalties
            if condition.condition_type == ConditionType.EXHAUSTION:
                penalty = condition.exhaustion_level * 2
                result["penalty"] += penalty
                result["sources"].append(f"Exhaustion {condition.exhaustion_level} (-{penalty})")

        return result

    def get_initiative_modifier(self, character_id: str) -> Dict[str, Any]:
        """Get initiative modifiers from conditions."""
        if not self.condition_manager:
            return {"advantage": False, "disadvantage": False, "bonus": 0, "penalty": 0}

        conditions = self.condition_manager.get_active_conditions(character_id)
        result = {
            "advantage": False,
            "disadvantage": False,
            "bonus": 0,
            "penalty": 0,
            "sources": []
        }

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Incapacitated gives disadvantage on initiative
            if effects.get("initiative_disadvantage"):
                result["disadvantage"] = True
                result["sources"].append(f"{condition.condition_type.value} (disadvantage)")

            # Exhaustion penalties
            if condition.condition_type == ConditionType.EXHAUSTION:
                penalty = condition.exhaustion_level * 2
                result["penalty"] += penalty
                result["sources"].append(f"Exhaustion {condition.exhaustion_level} (-{penalty})")

        return result

    def can_take_actions(self, character_id: str) -> Dict[str, Any]:
        """Check what actions a character can take based on conditions."""
        if not self.condition_manager:
            return {
                "actions": True,
                "bonus_actions": True,
                "reactions": True,
                "movement": True,
                "restrictions": []
            }

        conditions = self.condition_manager.get_active_conditions(character_id)
        result = {
            "actions": True,
            "bonus_actions": True,
            "reactions": True,
            "movement": True,
            "restrictions": []
        }

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Check for action restrictions
            if effects.get("no_actions"):
                result["actions"] = False
                result["restrictions"].append(f"{condition.condition_type.value}: Cannot take actions")

            if effects.get("no_bonus_actions"):
                result["bonus_actions"] = False
                result["restrictions"].append(f"{condition.condition_type.value}: Cannot take bonus actions")

            if effects.get("no_reactions"):
                result["reactions"] = False
                result["restrictions"].append(f"{condition.condition_type.value}: Cannot take reactions")

            # Check for movement restrictions
            if effects.get("movement_speed") == 0:
                result["movement"] = False
                result["restrictions"].append(f"{condition.condition_type.value}: Cannot move")

        return result

    def get_armor_class_modifier(self, character_id: str) -> Dict[str, Any]:
        """Get AC modifiers from conditions."""
        if not self.condition_manager:
            return {"bonus": 0, "penalty": 0, "advantage_against": False, "sources": []}

        conditions = self.condition_manager.get_active_conditions(character_id)
        result = {
            "bonus": 0,
            "penalty": 0,
            "advantage_against": False,  # Attackers get advantage
            "sources": []
        }

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Conditions that give attackers advantage (effectively lower AC)
            if effects.get("attack_rolls_against") == "advantage":
                result["advantage_against"] = True
                result["sources"].append(f"{condition.condition_type.value} (attackers have advantage)")

        return result

    def get_damage_resistances(self, character_id: str) -> List[str]:
        """Get damage resistances from conditions."""
        if not self.condition_manager:
            return []

        conditions = self.condition_manager.get_active_conditions(character_id)
        resistances = []

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Petrified gets resistance to all damage
            if effects.get("damage_resistance") == "all":
                resistances.append("all")

        return resistances

    def get_damage_immunities(self, character_id: str) -> List[str]:
        """Get damage immunities from conditions."""
        if not self.condition_manager:
            return []

        conditions = self.condition_manager.get_active_conditions(character_id)
        immunities = []

        for condition in conditions:
            effects = ConditionEffects.get_effects(condition.condition_type)

            # Petrified gets poison and disease immunity
            if effects.get("poison_immunity"):
                immunities.append("poison")
            if effects.get("disease_immunity"):
                immunities.append("disease")

        return immunities

    def get_all_stat_modifiers(self, character_id: str, base_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive stat modifications for a character."""
        if not self.condition_manager:
            return base_stats

        modified_stats = base_stats.copy()

        # Apply movement speed modifications
        if "movement_speed" in modified_stats:
            modified_stats["movement_speed"] = self.get_movement_speed_modifier(
                character_id, modified_stats["movement_speed"]
            )

        # Add condition-based modifiers
        modified_stats["condition_modifiers"] = {
            "attack_rolls": self.get_attack_roll_modifier(character_id),
            "saving_throws": {
                "strength": self.get_saving_throw_modifier(character_id, "strength"),
                "dexterity": self.get_saving_throw_modifier(character_id, "dexterity"),
                "constitution": self.get_saving_throw_modifier(character_id, "constitution"),
                "intelligence": self.get_saving_throw_modifier(character_id, "intelligence"),
                "wisdom": self.get_saving_throw_modifier(character_id, "wisdom"),
                "charisma": self.get_saving_throw_modifier(character_id, "charisma")
            },
            "ability_checks": {
                "strength": self.get_ability_check_modifier(character_id, "strength"),
                "dexterity": self.get_ability_check_modifier(character_id, "dexterity"),
                "constitution": self.get_ability_check_modifier(character_id, "constitution"),
                "intelligence": self.get_ability_check_modifier(character_id, "intelligence"),
                "wisdom": self.get_ability_check_modifier(character_id, "wisdom"),
                "charisma": self.get_ability_check_modifier(character_id, "charisma")
            },
            "initiative": self.get_initiative_modifier(character_id),
            "action_economy": self.can_take_actions(character_id),
            "armor_class": self.get_armor_class_modifier(character_id),
            "resistances": self.get_damage_resistances(character_id),
            "immunities": self.get_damage_immunities(character_id)
        }

        return modified_stats


# Singleton instance
condition_stat_service = ConditionStatService()