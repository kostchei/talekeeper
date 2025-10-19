# core
# category: core
"""
Rogue Abilities Service for TaleKeeper

Handles all Rogue-specific abilities and features:
- Sneak Attack
- Cunning Action
- Steady Aim
- Cunning Strike
- Uncanny Dodge
- Evasion
- Reliable Talent
- Expertise
- Slippery Mind
- Elusive
- Stroke of Luck
"""

import sqlite3
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class RogueAbilitiesService:
    """Service for managing Rogue abilities and resources."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_rogue_level(self, character_id: str) -> int:
        """Get the rogue class level for a character."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level, class_id FROM characters WHERE id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if row and (row['class_id'] or '').lower() == 'rogue':
                return row['level']
            return 0

    def get_character_subclass(self, character_id: str) -> Optional[str]:
        """Get character's subclass."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT subclass_id FROM character_subclasses WHERE character_id = ?
            """, (character_id,))
            result = cursor.fetchone()
            return result['subclass_id'] if result else None

    def update_rogue_resources_for_level(self, character_id: str, level: int) -> None:
        """Update rogue resource maximums based on level."""
        # Get character's class to determine resources
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT class_id FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                return
            class_id = result['class_id'].lower()

        # Only update for rogues
        if class_id != 'rogue':
            return

        # Sneak Attack dice scaling
        sneak_attack_dice = self._calculate_sneak_attack_dice(level)

        # Stroke of Luck uses (Level 20 only)
        stroke_of_luck_max = 1 if level >= 20 else 0

        # Expertise skills count
        expertise_count = 2  # Level 1
        if level >= 6:
            expertise_count = 4  # Additional 2 at level 6

        # Weapon Mastery count - unlimited for Rogue
        weapon_mastery_count = -1  # Unlimited access

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Update stroke of luck resource if needed
            if stroke_of_luck_max > 0:
                cursor.execute("""
                    INSERT OR REPLACE INTO character_resources
                    (character_id, resource_name, current_uses, max_uses, rest_type, source_class, source_level)
                    VALUES (?, 'stroke_of_luck', ?, ?, 'short', 'rogue', ?)
                """, (character_id, stroke_of_luck_max, stroke_of_luck_max, level))

            # Update rogue_features table
            cursor.execute("""
                INSERT OR REPLACE INTO rogue_features
                (character_id, level, sneak_attack_dice, expertise_skills,
                 cunning_action_available, uncanny_dodge_available, evasion_available,
                 reliable_talent_active, slippery_mind_active, elusive_active,
                 stroke_of_luck_uses_current, stroke_of_luck_uses_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                character_id, level, sneak_attack_dice, "[]",  # Empty expertise skills initially
                level >= 2,  # Cunning Action
                level >= 5,  # Uncanny Dodge
                level >= 7,  # Evasion
                level >= 7,  # Reliable Talent
                level >= 15, # Slippery Mind
                level >= 18, # Elusive
                stroke_of_luck_max, stroke_of_luck_max
            ))

            conn.commit()

    def _calculate_sneak_attack_dice(self, level: int) -> int:
        """Calculate sneak attack dice based on level."""
        if level < 1:
            return 0
        elif level < 3:
            return 1
        elif level < 5:
            return 2
        elif level < 7:
            return 3
        elif level < 9:
            return 4
        elif level < 11:
            return 5
        elif level < 13:
            return 6
        elif level < 15:
            return 7
        elif level < 17:
            return 8
        elif level < 19:
            return 9
        else:
            return 10

    def calculate_sneak_attack_damage(self, character_id: str) -> str:
        """Get sneak attack damage dice string for character."""
        level = self.get_rogue_level(character_id)
        dice_count = self._calculate_sneak_attack_dice(level)
        return f"{dice_count}d6" if dice_count > 0 else "0d6"

    def check_sneak_attack_eligibility(self, character_id: str, target_id: str,
                                     attack_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if sneak attack is eligible for this attack.

        Returns:
            Dict with 'eligible' (bool), 'reason' (str), and 'source' (str)
        """
        level = self.get_rogue_level(character_id)
        if level < 1:
            return {"eligible": False, "reason": "not_rogue", "source": None}

        # Check if weapon is eligible (finesse or ranged)
        weapon = attack_context.get('weapon', {})
        if not self._is_sneak_attack_weapon(weapon):
            return {"eligible": False, "reason": "weapon_ineligible", "source": None}

        # Check for advantage
        has_advantage = attack_context.get('has_advantage', False)
        has_disadvantage = attack_context.get('has_disadvantage', False)

        if has_advantage and not has_disadvantage:
            return {"eligible": True, "reason": "has_advantage", "source": "advantage"}

        # Check for ally within 5 feet (if no disadvantage)
        if not has_disadvantage:
            ally_nearby = self._check_ally_within_5_feet(character_id, target_id, attack_context)
            if ally_nearby:
                return {"eligible": True, "reason": "ally_proximity", "source": "ally_nearby"}

        return {"eligible": False, "reason": "conditions_not_met", "source": None}

    def _is_sneak_attack_weapon(self, weapon: Dict[str, Any]) -> bool:
        """Check if weapon is eligible for sneak attack (finesse or ranged)."""
        if not weapon:
            return False

        # Check weapon_properties (can be string or list)
        properties = weapon.get('weapon_properties', weapon.get('properties', ''))
        if isinstance(properties, list):
            properties = ', '.join(properties)
        properties = properties.lower() if properties else ''

        weapon_type = weapon.get('weapon_type', '').lower()

        # Check for finesse property
        if 'finesse' in properties:
            return True

        # Check for ranged weapons
        if weapon_type in ['ranged', 'simple ranged', 'martial ranged']:
            return True

        # Check for specific ranged weapon types
        weapon_name = weapon.get('name', '').lower()
        ranged_weapons = ['shortbow', 'longbow', 'light crossbow', 'heavy crossbow',
                         'hand crossbow', 'dart', 'sling', 'blowgun']

        return any(ranged_weapon in weapon_name for ranged_weapon in ranged_weapons)

    def _check_ally_within_5_feet(self, character_id: str, target_id: str,
                                 attack_context: Dict[str, Any]) -> bool:
        """Check if an ally is within 5 feet of the target."""
        # This would integrate with the combat manager to check positioning
        # For now, return a basic implementation
        allies_nearby = attack_context.get('allies_within_5ft', [])

        # Filter out incapacitated allies
        active_allies = []
        for ally_id in allies_nearby:
            if not self._is_ally_incapacitated(ally_id):
                active_allies.append(ally_id)

        return len(active_allies) > 0

    def _is_ally_incapacitated(self, ally_id: str) -> bool:
        """Check if an ally is incapacitated."""
        # This would check for incapacitated condition
        # For now, return False (assume ally is active)
        return False

    def use_cunning_action(self, character_id: str, action_type: str) -> Dict[str, Any]:
        """
        Use Cunning Action (Dash, Disengage, or Hide as bonus action).

        Args:
            character_id: Character ID
            action_type: 'dash', 'disengage', or 'hide'

        Returns:
            Dict with result information
        """
        level = self.get_rogue_level(character_id)
        if level < 2:
            return {"success": False, "message": "Cunning Action not available until level 2"}

        valid_actions = ['dash', 'disengage', 'hide']
        if action_type not in valid_actions:
            return {"success": False, "message": f"Invalid action type: {action_type}"}

        # Check if bonus action is available
        # This would integrate with action economy system

        return {
            "success": True,
            "message": f"Used Cunning Action: {action_type.title()}",
            "action_type": action_type,
            "action_cost": "bonus"
        }

    def use_steady_aim(self, character_id: str) -> Dict[str, Any]:
        """
        Use Steady Aim to gain advantage on next attack.

        Returns:
            Dict with result information
        """
        level = self.get_rogue_level(character_id)
        if level < 3:
            return {"success": False, "message": "Steady Aim not available until level 3"}

        # Check if character has moved this turn
        # This would integrate with movement tracking
        has_moved = False  # Placeholder

        if has_moved:
            return {"success": False, "message": "Cannot use Steady Aim after moving"}

        return {
            "success": True,
            "message": "Used Steady Aim - gain advantage on next attack, speed becomes 0",
            "grants_advantage": True,
            "sets_speed_to_zero": True,
            "action_cost": "bonus"
        }

    def use_uncanny_dodge(self, character_id: str, incoming_damage: int) -> Dict[str, Any]:
        """
        Use Uncanny Dodge to halve incoming damage.

        Args:
            character_id: Character ID
            incoming_damage: Original damage amount

        Returns:
            Dict with result information
        """
        level = self.get_rogue_level(character_id)
        if level < 5:
            return {"success": False, "message": "Uncanny Dodge not available until level 5"}

        # Check if already used this turn
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT uncanny_dodge_used FROM rogue_features WHERE character_id = ?
            """, (character_id,))
            result = cursor.fetchone()

            if result and result['uncanny_dodge_used']:
                return {"success": False, "message": "Uncanny Dodge already used this turn"}

        # Calculate reduced damage
        reduced_damage = incoming_damage // 2
        damage_prevented = incoming_damage - reduced_damage

        # Mark as used this turn
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE rogue_features SET uncanny_dodge_used = 1 WHERE character_id = ?
            """, (character_id,))
            conn.commit()

        return {
            "success": True,
            "message": f"Used Uncanny Dodge - damage reduced from {incoming_damage} to {reduced_damage}",
            "original_damage": incoming_damage,
            "reduced_damage": reduced_damage,
            "damage_prevented": damage_prevented,
            "action_cost": "reaction"
        }

    def apply_evasion(self, character_id: str, save_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Evasion to a Dexterity saving throw.

        Args:
            character_id: Character ID
            save_result: Dict with save information

        Returns:
            Dict with modified save result
        """
        level = self.get_rogue_level(character_id)
        if level < 7:
            return save_result  # No change

        # Check if character is incapacitated
        if self._is_character_incapacitated(character_id):
            return save_result  # No change if incapacitated

        save_type = save_result.get('save_type', '').lower()
        if save_type != 'dexterity':
            return save_result  # Only affects Dexterity saves

        original_damage = save_result.get('damage_on_save', 0)
        was_successful = save_result.get('success', False)

        if was_successful:
            # Success: take no damage instead of half
            modified_result = save_result.copy()
            modified_result['damage_on_save'] = 0
            modified_result['evasion_applied'] = True
            modified_result['message'] = f"Evasion: No damage taken (was {original_damage // 2})"
            return modified_result
        else:
            # Failure: take half damage instead of full
            modified_result = save_result.copy()
            modified_result['damage_on_save'] = original_damage // 2
            modified_result['evasion_applied'] = True
            modified_result['message'] = f"Evasion: Half damage taken ({original_damage // 2} instead of {original_damage})"
            return modified_result

    def _is_character_incapacitated(self, character_id: str) -> bool:
        """Check if character is incapacitated."""
        # This would check for incapacitated condition
        # For now, return False
        return False

    def apply_reliable_talent(self, character_id: str, skill_roll: int,
                            skill_name: str) -> Dict[str, Any]:
        """
        Apply Reliable Talent to a skill check.

        Args:
            character_id: Character ID
            skill_roll: Original d20 roll
            skill_name: Name of the skill

        Returns:
            Dict with modified roll information
        """
        level = self.get_rogue_level(character_id)
        if level < 7:
            return {"modified_roll": skill_roll, "reliable_talent_applied": False}

        # Check if this is a skill the character is proficient in
        if not self._is_proficient_in_skill(character_id, skill_name):
            return {"modified_roll": skill_roll, "reliable_talent_applied": False}

        # Apply Reliable Talent if roll is 9 or lower
        if skill_roll <= 9:
            return {
                "modified_roll": 10,
                "reliable_talent_applied": True,
                "original_roll": skill_roll,
                "message": f"Reliable Talent: {skill_roll} becomes 10"
            }

        return {"modified_roll": skill_roll, "reliable_talent_applied": False}

    def _is_proficient_in_skill(self, character_id: str, skill_name: str) -> bool:
        """Check if character is proficient in a skill."""
        # This would check character's skill proficiencies
        # For now, return True for common rogue skills
        rogue_skills = ['stealth', 'sleight_of_hand', 'thieves_tools', 'perception',
                       'investigation', 'acrobatics', 'deception', 'insight']
        return skill_name.lower() in rogue_skills

    def use_stroke_of_luck(self, character_id: str, original_roll: int) -> Dict[str, Any]:
        """
        Use Stroke of Luck to turn a failed d20 test into a 20.

        Args:
            character_id: Character ID
            original_roll: Original d20 roll

        Returns:
            Dict with result information
        """
        level = self.get_rogue_level(character_id)
        if level < 20:
            return {"success": False, "message": "Stroke of Luck not available until level 20"}

        # Check if uses are available
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stroke_of_luck_uses_current FROM rogue_features WHERE character_id = ?
            """, (character_id,))
            result = cursor.fetchone()

            if not result or result['stroke_of_luck_uses_current'] <= 0:
                return {"success": False, "message": "No Stroke of Luck uses remaining"}

        # Use the feature
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE rogue_features
                SET stroke_of_luck_uses_current = stroke_of_luck_uses_current - 1
                WHERE character_id = ?
            """, (character_id,))
            conn.commit()

        return {
            "success": True,
            "message": f"Used Stroke of Luck - roll changed from {original_roll} to 20",
            "original_roll": original_roll,
            "new_roll": 20,
            "uses_remaining": 0  # Since it's once per short/long rest
        }

    def rest_rogue_resources(self, character_id: str, rest_type: str) -> None:
        """Reset rogue resources after a rest."""
        if rest_type not in ['short', 'long']:
            return

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Reset per-turn abilities
            cursor.execute("""
                UPDATE rogue_features
                SET uncanny_dodge_used = 0
                WHERE character_id = ?
            """, (character_id,))

            # Reset Stroke of Luck on short or long rest
            if rest_type in ['short', 'long']:
                cursor.execute("""
                    UPDATE rogue_features
                    SET stroke_of_luck_uses_current = stroke_of_luck_uses_max
                    WHERE character_id = ?
                """, (character_id,))

            conn.commit()

    def get_rogue_features(self, character_id: str) -> Dict[str, Any]:
        """Get all rogue features for a character."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM rogue_features WHERE character_id = ?
            """, (character_id,))
            result = cursor.fetchone()

            if result:
                return dict(result)
            else:
                # Return default empty features
                return {
                    'character_id': character_id,
                    'level': 0,
                    'sneak_attack_dice': 0,
                    'expertise_skills': '[]',
                    'cunning_action_available': False,
                    'uncanny_dodge_available': False,
                    'uncanny_dodge_used': False,
                    'evasion_available': False,
                    'reliable_talent_active': False,
                    'slippery_mind_active': False,
                    'elusive_active': False,
                    'stroke_of_luck_uses_current': 0,
                    'stroke_of_luck_uses_max': 0
                }