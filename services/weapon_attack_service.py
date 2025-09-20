"""
Centralized service for weapon attack calculations and effects.
This service consolidates weapon-related logic previously scattered across UI components.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
import random
import json


class WeaponAttackService:
    """Service for calculating weapon attacks, damage, and applying combat effects."""

    # Classes that get unlimited weapon mastery access
    UNLIMITED_MASTERY_CLASSES = ['fighter', 'barbarian', 'rogue', 'paladin']

    def __init__(self, db_path: str):
        """Initialize the weapon attack service."""
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def update_character_mastery_resources(self, character_id: str) -> None:
        """
        Update weapon mastery resources for a character.
        Fighter, Barbarian, Rogue, and Paladin get unlimited access (-1).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get character's class
            cursor.execute("""
                SELECT class_id, level
                FROM characters
                WHERE id = ?
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return

            class_id = result['class_id'].lower()
            level = result['level']

            # Check if this class gets unlimited mastery
            if class_id in self.UNLIMITED_MASTERY_CLASSES:
                weapon_mastery_count = -1  # Unlimited access
            else:
                # Other classes might get limited mastery (future expansion)
                weapon_mastery_count = 0

            # Update the character's mastery count
            cursor.execute("""
                UPDATE characters
                SET weapon_mastery_count = ?
                WHERE id = ?
            """, (weapon_mastery_count, character_id))

            conn.commit()

    def calculate_attack_damage(self,
                               weapon: Dict[str, Any],
                               character: Dict[str, Any],
                               target: Optional[Dict[str, Any]] = None,
                               is_critical: bool = False,
                               advantage: bool = False,
                               disadvantage: bool = False) -> Dict[str, Any]:
        """
        Calculate attack roll and damage for a weapon attack.

        Returns:
            Dict containing:
            - attack_roll: int
            - attack_total: int
            - damage_rolls: List[int]
            - damage_total: int
            - damage_breakdown: str
            - modifiers_applied: List[str]
        """
        # This will be expanded to include all the attack calculation logic
        # Currently returns a placeholder
        return {
            'attack_roll': 10,
            'attack_total': 15,
            'damage_rolls': [6],
            'damage_total': 8,
            'damage_breakdown': '1d8+2',
            'modifiers_applied': []
        }

    def apply_fighting_style_effects(self,
                                    dice_rolls: List[int],
                                    fighting_style: str,
                                    weapon: Dict[str, Any],
                                    character: Dict[str, Any]) -> Tuple[List[int], str]:
        """
        Apply fighting style effects to damage dice.

        Args:
            dice_rolls: Original damage dice rolls
            fighting_style: Name of the fighting style
            weapon: Weapon data
            character: Character data

        Returns:
            Tuple of (modified_dice_rolls, description)
        """
        modified_rolls = dice_rolls.copy()
        description = ""

        if fighting_style == 'Great Weapon Fighting':
            # Reroll 1s and 2s on damage dice for two-handed weapons
            weapon_properties = weapon.get('weapon_properties', '').lower()
            if 'two-handed' in weapon_properties or 'versatile' in weapon_properties:
                new_rolls = []
                rerolled_count = 0
                for roll in modified_rolls:
                    if roll in [1, 2]:
                        new_roll = random.randint(1, self._get_die_size_from_weapon(weapon))
                        new_rolls.append(new_roll)
                        rerolled_count += 1
                    else:
                        new_rolls.append(roll)

                if rerolled_count > 0:
                    modified_rolls = new_rolls
                    description = f"Great Weapon Fighting: rerolled {rerolled_count} dice"

        return modified_rolls, description

    def calculate_dueling_bonus(self, weapon: Dict[str, Any], off_hand: Optional[str]) -> int:
        """
        Calculate the Dueling fighting style damage bonus.

        Returns:
            +2 if wielding a one-handed weapon with no off-hand weapon, 0 otherwise
        """
        weapon_properties = weapon.get('weapon_properties', '').lower()

        # Must be one-handed (not two-handed, not versatile being used two-handed)
        if 'two-handed' in weapon_properties:
            return 0

        # No weapon in off-hand (shield is OK)
        if off_hand and off_hand != 'shield':
            return 0

        return 2

    def apply_savage_attacker(self,
                             dice_rolls: List[int],
                             num_dice: int,
                             die_size: int) -> Tuple[List[int], str]:
        """
        Apply Savage Attacker feat - reroll damage dice and use higher result.

        Returns:
            Tuple of (best_rolls, description)
        """
        # Roll a second set
        second_rolls = [random.randint(1, die_size) for _ in range(num_dice)]

        # Compare totals and use the better set
        if sum(second_rolls) > sum(dice_rolls):
            return second_rolls, f"Savage Attacker: rerolled for {sum(second_rolls)} (was {sum(dice_rolls)})"
        else:
            return dice_rolls, ""

    def get_weapon_mastery_effects(self,
                                  mastery_type: str,
                                  weapon_name: str,
                                  hit: bool,
                                  damage_total: int = 0) -> Dict[str, Any]:
        """
        Get the effects of a weapon mastery property.

        Args:
            mastery_type: The mastery property name (Cleave, Nick, Vex, etc.)
            weapon_name: Name of the weapon
            hit: Whether the attack hit
            damage_total: Total damage dealt (for some masteries)

        Returns:
            Dict describing the mastery effects
        """
        effects = {}

        if not mastery_type:
            return effects

        mastery_lower = mastery_type.lower()

        if mastery_lower == 'cleave' and hit:
            effects['cleave'] = {
                'description': 'Can make an attack against a second creature within 5 feet',
                'damage': 'Ability modifier damage only'
            }
        elif mastery_lower == 'graze' and not hit:
            effects['graze'] = {
                'description': 'Deal ability modifier damage on a miss',
                'damage': 'Ability modifier'
            }
        elif mastery_lower == 'nick' and hit:
            effects['nick'] = {
                'description': 'Make an additional attack as part of the Attack action',
                'restriction': 'Light weapon in other hand'
            }
        elif mastery_lower == 'push' and hit:
            effects['push'] = {
                'description': 'Push Large or smaller creature 10 feet away',
                'distance': 10
            }
        elif mastery_lower == 'sap' and hit:
            effects['sap'] = {
                'description': 'Target has disadvantage on next attack roll',
                'duration': 'Until start of your next turn'
            }
        elif mastery_lower == 'slow' and hit:
            effects['slow'] = {
                'description': 'Reduce target speed by 10 feet',
                'duration': 'Until start of your next turn',
                'amount': 10
            }
        elif mastery_lower == 'topple' and hit:
            effects['topple'] = {
                'description': 'Target must make Constitution save or be knocked prone',
                'save_dc': 'Calculated from character stats'
            }
        elif mastery_lower == 'vex' and hit:
            effects['vex'] = {
                'description': 'Gain advantage on next attack against this target',
                'duration': 'Before end of your next turn'
            }

        return effects

    def _get_die_size_from_weapon(self, weapon: Dict[str, Any]) -> int:
        """Extract die size from weapon damage dice string."""
        damage_dice = weapon.get('damage_dice', '1d6')
        if 'd' in damage_dice:
            parts = damage_dice.split('d')
            if len(parts) == 2:
                try:
                    return int(parts[1].split('+')[0].split('-')[0].strip())
                except:
                    pass
        return 6  # Default to d6

    def has_character_unlimited_mastery(self, character_id: str) -> bool:
        """
        Check if a character has unlimited weapon mastery access.
        Fighter, Barbarian, Rogue, and Paladin get this benefit.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT class_id, weapon_mastery_count
                FROM characters
                WHERE id = ?
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return False

            class_id = result['class_id'].lower()
            mastery_count = result['weapon_mastery_count']

            # Check by class or by count
            return class_id in self.UNLIMITED_MASTERY_CLASSES or mastery_count == -1