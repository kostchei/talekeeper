"""
Fighting Style Effects for TaleKeeper

This service handles the mechanical effects of fighting styles on character abilities,
combat actions, and other game mechanics. It is designed to be a centralized
place for all fighting style logic.
"""

import sqlite3
import random
from typing import Dict, Any, List, Tuple

class FightingStyleEffects:
    """Processes fighting style effects and applies them to characters."""

    def __init__(self, db_path: str = "talekeeper.db"):
        """Initialize with a database connection."""
        self.db_path = db_path
        self._style_cache = {}

    def _get_character_styles(self, character_id: str) -> List[str]:
        """Get all fighting styles for a character, with caching."""
        if character_id in self._style_cache:
            return self._style_cache[character_id]

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT configuration FROM character_features
                WHERE character_id = ? AND feature_name = 'Fighting Style'
            """, (character_id,))

            results = cursor.fetchall()
            conn.close()

            styles = [row[0] for row in results if row[0]]
            self._style_cache[character_id] = styles
            return styles

        except sqlite3.Error as e:
            print(f"Database error in _get_character_styles: {e}")
            return []

    def does_character_have_style(self, character_id: str, style_name: str) -> bool:
        """Check if a character has a specific fighting style."""
        return style_name in self._get_character_styles(character_id)

    def should_add_ability_mod_to_offhand(self, character_id: str) -> bool:
        """Check if the Two-Weapon Fighting style allows adding the ability modifier."""
        return self.does_character_have_style(character_id, "two_weapon_fighting")

    def get_attack_bonus(self, character_id: str, weapon_data: Dict[str, Any]) -> int:
        """Get attack bonus from fighting styles like Archery."""
        bonus = 0
        styles = self._get_character_styles(character_id)

        if "archery" in styles:
            weapon_props = weapon_data.get('weapon_properties', [])
            if 'ranged' in weapon_props:
                bonus += 2
        return bonus

    def get_damage_bonus(self, character_id: str, weapon_data: Dict[str, Any], all_equipped_items: List[Dict[str, Any]]) -> int:
        """Get damage bonus from fighting styles like Dueling."""
        bonus = 0
        styles = self._get_character_styles(character_id)

        if "dueling" in styles:
            # Check if only one melee weapon is equipped. A shield is not a weapon.
            equipped_weapons = [item for item in all_equipped_items if item.get('item_type') == 'weapon']

            if len(equipped_weapons) == 1:
                weapon = equipped_weapons[0]
                # Ensure the weapon is a melee weapon
                if 'ranged' not in weapon.get('weapon_properties', []):
                    bonus += 2
        return bonus

    def apply_great_weapon_fighting(self, character_id: str, dice_rolls: List[int], weapon_data: Dict[str, Any], die_size: int) -> Tuple[List[int], bool]:
        """Reroll 1s and 2s on damage dice once for Great Weapon Fighting. Returns new rolls and if a change was made."""
        styles = self._get_character_styles(character_id)
        if "great_weapon_fighting" not in styles:
            return dice_rolls, False

        weapon_props = weapon_data.get('weapon_properties', [])
        if 'two-handed' in weapon_props or 'versatile' in weapon_props:
            rerolled_dice = []
            changed = False
            for roll in dice_rolls:
                if roll in [1, 2]:
                    new_roll = random.randint(1, die_size)
                    rerolled_dice.append(new_roll)
                    changed = True
                else:
                    rerolled_dice.append(roll)
            return rerolled_dice, changed

        return dice_rolls, False
