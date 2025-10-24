# core
# core
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

    # Classes that get unlimited weapon mastery access in D&D 2024
    UNLIMITED_MASTERY_CLASSES = ['fighter', 'barbarian', 'rogue', 'paladin', 'ranger']

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
                               disadvantage: bool = False,
                               action_type: str = 'main_hand',
                               is_hidden: bool = False) -> Dict[str, Any]:
        """
        Calculate attack roll and damage for a weapon attack.

        Args:
            weapon: Weapon data dictionary
            character: Character data dictionary
            target: Target data (optional)
            is_critical: Whether this is a critical hit
            advantage: Attack has advantage
            disadvantage: Attack has disadvantage
            action_type: 'main_hand', 'off_hand', 'ranged', etc.

        Returns:
            Dict containing:
            - attack_roll: int
            - attack_total: int
            - damage_rolls: List[int]
            - damage_total: int
            - damage_breakdown: str
            - modifiers_applied: List[str]
        """
        import random

        modifiers_applied = []

        # Check if attacking from hidden grants advantage
        if is_hidden and not disadvantage:
            advantage = True
            modifiers_applied.append('Attacking from Hidden')

        # Roll attack
        if advantage and disadvantage:
            attack_roll = random.randint(1, 20)
        elif advantage:
            attack_roll = max(random.randint(1, 20), random.randint(1, 20))
            if 'Attacking from Hidden' not in modifiers_applied:
                modifiers_applied.append('Advantage')
        elif disadvantage:
            attack_roll = min(random.randint(1, 20), random.randint(1, 20))
            modifiers_applied.append('Disadvantage')
        else:
            attack_roll = random.randint(1, 20)

        # Calculate attack bonus
        weapon_properties = self._normalize_weapon_properties(weapon.get('weapon_properties'))
        weapon_name = weapon.get('name')
        if not weapon_name:
            raise ValueError("Weapon name is required but missing")
        is_ranged = 'ranged' in weapon_properties or any(x in weapon_name.lower() for x in ['bow', 'crossbow', 'sling'])
        is_finesse = 'finesse' in weapon_properties

        # Determine ability modifier and track if using Strength
        str_mod = (character.get('strength', 10) - 10) // 2
        dex_mod = (character.get('dexterity', 10) - 10) // 2
        is_strength_based = False

        if is_finesse:
            # Finesse weapons can use STR or DEX, whichever is higher
            if str_mod >= dex_mod:
                ability_mod = str_mod
                is_strength_based = True
            else:
                ability_mod = dex_mod
                is_strength_based = False
        elif is_ranged:
            ability_mod = dex_mod
            is_strength_based = False
        else:
            # Melee weapons without finesse use Strength
            ability_mod = str_mod
            is_strength_based = True

        # Proficiency bonus
        level = character.get('level', 1)
        prof_bonus = 2 + ((level - 1) // 4)

        # Fighting style bonuses to attack
        fighting_style_attack = self.get_fighting_style_attack_bonus(weapon, character)
        if fighting_style_attack > 0:
            modifiers_applied.append(f'Fighting Style +{fighting_style_attack}')

        attack_total = attack_roll + ability_mod + prof_bonus + fighting_style_attack

        # Check if critical
        if attack_roll == 20:
            is_critical = True
            modifiers_applied.append('Critical Hit!')

        # Calculate damage
        damage_dice = weapon.get('damage_dice')
        if not damage_dice:
            raise ValueError(f"Weapon '{weapon.get('name', 'Unknown')}' missing damage_dice")
        num_dice, die_size = self._parse_damage_dice(damage_dice)

        # Roll damage dice
        if is_critical:
            # Double dice on critical
            damage_rolls = [random.randint(1, die_size) for _ in range(num_dice * 2)]
        else:
            damage_rolls = [random.randint(1, die_size) for _ in range(num_dice)]

        # Apply fighting style damage effects to dice
        fighting_styles = self.get_character_fighting_styles(character.get('id'))
        damage_rolls, style_desc = self.apply_fighting_style_effects(
            damage_rolls, fighting_styles, weapon, character, action_type
        )
        if style_desc:
            modifiers_applied.append(style_desc)

        # Calculate damage bonuses
        damage_bonus = ability_mod

        # Fighting style flat damage bonuses
        fighting_damage = self.get_fighting_style_damage_bonus(
            weapon, character, action_type, fighting_styles
        )
        if fighting_damage > 0:
            damage_bonus += fighting_damage
            modifiers_applied.append(f'Fighting Style +{fighting_damage} damage')

        # Two-Weapon Fighting special case for off-hand
        if action_type == 'off_hand' and 'light' in weapon_props:
            if 'Two-Weapon Fighting' not in fighting_styles:
                # Normally off-hand doesn't get ability mod
                damage_bonus -= ability_mod
                modifiers_applied.append('Off-hand (no ability mod)')
            else:
                modifiers_applied.append('Two-Weapon Fighting (ability mod to off-hand)')

        damage_total = sum(damage_rolls) + damage_bonus

        # Apply Frenzy damage bonus (Berserker 3+)
        # SRD: Only applies to Strength-based attacks while Raging and using Reckless Attack
        weapon_damage_type = weapon.get('damage_type', 'bludgeoning')
        frenzy_bonus = self._consume_frenzy_damage(character.get('id'), is_strength_based, weapon_damage_type)
        frenzy_damage = 0
        frenzy_rolls: List[int] = []
        frenzy_dice: Optional[str] = None
        frenzy_damage_type: Optional[str] = None
        if frenzy_bonus:
            frenzy_damage = frenzy_bonus['damage']
            frenzy_rolls = frenzy_bonus['rolls']
            frenzy_dice = frenzy_bonus['dice']
            frenzy_damage_type = frenzy_bonus['damage_type']
            damage_total += frenzy_damage
            modifiers_applied.append(f"Frenzy +{frenzy_damage} {frenzy_damage_type} damage ({frenzy_dice})")

        # Apply Sneak Attack if eligible (Rogue class)
        sneak_attack_data = self._apply_sneak_attack_if_eligible(
            character, weapon, target, advantage or is_hidden, disadvantage, is_hidden
        )

        sneak_attack_damage = 0
        cunning_strike_effects = []
        if sneak_attack_data['eligible']:
            sneak_attack_rolls = sneak_attack_data['damage_rolls']
            sneak_attack_damage = sum(sneak_attack_rolls)
            damage_total += sneak_attack_damage
            modifiers_applied.append(f"Sneak Attack {sneak_attack_data['damage_dice']} ({sneak_attack_data['source']})")

            cunning_strike_effects = sneak_attack_data.get('cunning_strike_effects', [])
            if cunning_strike_effects:
                effect_names = [eff['effect_name'] for eff in cunning_strike_effects]
                modifiers_applied.append(f"Cunning Strike: {', '.join(effect_names)}")

        # Build damage breakdown string
        if is_critical:
            damage_breakdown = f'{num_dice*2}d{die_size}'
        else:
            damage_breakdown = f'{num_dice}d{die_size}'
        if damage_bonus != 0:
            damage_breakdown += f'{damage_bonus:+d}'
        if sneak_attack_damage > 0:
            damage_breakdown += f' + {sneak_attack_data["damage_dice"]} sneak attack'
        if frenzy_dice:
            damage_breakdown += f' + {frenzy_dice} frenzy'

        return {
            'attack_roll': attack_roll,
            'attack_total': attack_total,
            'damage_rolls': damage_rolls,
            'sneak_attack_rolls': sneak_attack_data.get('damage_rolls', []),
            'sneak_attack_damage': sneak_attack_damage,
            'cunning_strike_effects': cunning_strike_effects,
            'damage_total': max(0, damage_total),  # Damage can't be negative
            'damage_breakdown': damage_breakdown,
            'modifiers_applied': modifiers_applied,
            'frenzy_rolls': frenzy_rolls,
            'frenzy_damage': frenzy_damage,
            'frenzy_dice': frenzy_dice,
            'frenzy_damage_type': frenzy_damage_type
        }

    def apply_fighting_style_effects(self,
                                    dice_rolls: List[int],
                                    fighting_styles: List[str],
                                    weapon: Dict[str, Any],
                                    character: Dict[str, Any],
                                    action_type: str = 'main_hand') -> Tuple[List[int], str]:
        """
        Apply fighting style effects to damage dice.

        Args:
            dice_rolls: Original damage dice rolls
            fighting_styles: List of fighting style names the character has
            weapon: Weapon data
            character: Character data
            action_type: Type of action being performed

        Returns:
            Tuple of (modified_dice_rolls, description)
        """
        modified_rolls = dice_rolls.copy()
        descriptions = []

        # Check for Great Weapon Fighting
        if any('Great Weapon Fighting' in style for style in fighting_styles):
            # Handle weapon_properties that might be a list or None
            weapon_props = weapon.get('weapon_properties', '')
            if isinstance(weapon_props, list):
                weapon_props = ', '.join(weapon_props)
            elif weapon_props is None:
                weapon_props = ''
            weapon_properties = weapon_props.lower()

            # GWF applies to two-handed, heavy, or versatile weapons
            if any(prop in weapon_properties for prop in ['two-handed', 'heavy', 'versatile']):
                # D&D 2024 rules: treat 1s and 2s as 3s
                changes = 0
                new_rolls = []
                for roll in modified_rolls:
                    if roll <= 2:
                        new_rolls.append(3)
                        changes += 1
                    else:
                        new_rolls.append(roll)

                if changes > 0:
                    modified_rolls = new_rolls
                    descriptions.append(f"Great Weapon Fighting: treated {changes} low rolls as 3")

        return modified_rolls, '; '.join(descriptions)

    def get_fighting_style_damage_bonus(self,
                                       weapon: Dict[str, Any],
                                       character: Dict[str, Any],
                                       action_type: str,
                                       fighting_styles: List[str]) -> int:
        """
        Calculate flat damage bonuses from fighting styles.

        Args:
            weapon: Weapon data
            character: Character data
            action_type: Type of action being performed
            fighting_styles: List of fighting styles the character has

        Returns:
            Total damage bonus from fighting styles
        """
        bonus = 0
        weapon_properties = self._normalize_weapon_properties(weapon.get('weapon_properties', ''))

        weapon_name = weapon.get('name')
        if not weapon_name:
            raise ValueError("Weapon name is required but missing")
        weapon_name = weapon_name.lower()

        # Dueling: +2 damage when wielding a melee weapon in one hand with no other weapons
        if any('Dueling' in style for style in fighting_styles):
            # Must be melee (not ranged)
            is_ranged = 'ranged' in weapon_properties or any(x in weapon_name for x in ['bow', 'crossbow', 'sling'])
            if not is_ranged:
                # Must not be two-handed
                if 'two-handed' not in weapon_properties:
                    # Must be main hand attack (off-hand implies two weapons)
                    if action_type != 'off_hand':
                        bonus += 2

        # Thrown Weapon Fighting: +2 damage to thrown weapons used at range
        if any('Thrown Weapon Fighting' in style for style in fighting_styles):
            if 'thrown' in weapon_properties and action_type == 'ranged':
                bonus += 2

        return bonus

    def _consume_frenzy_damage(self, character_id: Optional[str], is_strength_based: bool = False, weapon_damage_type: str = 'bludgeoning') -> Optional[Dict[str, Any]]:
        """Apply Frenzy damage bonus once per turn if active.

        Per SRD: "roll a number of d6s equal to your Rage Damage bonus"
        "The damage has the same type as the weapon or Unarmed Strike used for the attack."
        Only applies to Strength-based attacks.

        Args:
            character_id: The character's ID
            is_strength_based: Whether this attack uses Strength modifier
            weapon_damage_type: The damage type of the weapon (e.g., 'slashing', 'piercing')

        Returns:
            Dict with damage, dice, rolls, and damage_type, or None if not applicable
        """
        if not character_id:
            return None

        # SRD: Frenzy only applies to Strength-based attacks
        if not is_strength_based:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT frenzy_active, level, rage_damage_bonus
                FROM barbarian_features
                WHERE character_id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if not row or not self._is_truthy(row['frenzy_active']):
                return None

            # SRD: Roll a number of d6s equal to your Rage Damage bonus
            rage_damage_bonus = row['rage_damage_bonus'] or 2
            num_dice = rage_damage_bonus
            dice = f"{num_dice}d6"

            # Roll the damage
            rolls = [random.randint(1, 6) for _ in range(num_dice)]
            total_damage = sum(rolls)

            # Consume the Frenzy effect (only applies to first hit)
            cursor.execute("""
                UPDATE barbarian_features
                SET frenzy_active = 0
                WHERE character_id = ?
            """, (character_id,))

            try:
                cursor.execute("""
                    UPDATE character_combat_state
                    SET frenzy_active = 0
                    WHERE character_id = ?
                """, (character_id,))
            except sqlite3.OperationalError:
                # Legacy databases may not have this column yet
                pass

            conn.commit()

            # SRD: Damage type matches the weapon
            return {
                'damage': total_damage,
                'dice': dice,
                'rolls': rolls,
                'damage_type': weapon_damage_type
            }

    @staticmethod
    def _is_truthy(value) -> bool:
        """Normalize SQLite truthy values."""
        if isinstance(value, (bool, int)):
            return bool(value)
        if value is None:
            return False
        return str(value).strip().lower() in {"1", "true", "t", "yes", "on"}

    def get_fighting_style_attack_bonus(self, weapon: Dict[str, Any], character: Dict[str, Any]) -> int:
        """
        Calculate attack bonuses from fighting styles.

        Args:
            weapon: Weapon data
            character: Character data

        Returns:
            Total attack bonus from fighting styles
        """
        bonus = 0
        fighting_styles = self.get_character_fighting_styles(character.get('id'))

        weapon_properties = self._normalize_weapon_properties(weapon.get('weapon_properties', ''))

        weapon_name = weapon.get('name')
        if not weapon_name:
            raise ValueError("Weapon name is required but missing")
        weapon_name = weapon_name.lower()

        # Archery: +2 to ranged weapon attacks
        if any('Archery' in style for style in fighting_styles):
            is_ranged = 'ranged' in weapon_properties or any(x in weapon_name for x in ['bow', 'crossbow', 'sling'])
            if is_ranged:
                bonus += 2

        return bonus

    def get_character_fighting_styles(self, character_id: str) -> List[str]:
        """
        Get all fighting styles for a character.

        Args:
            character_id: Character ID

        Returns:
            List of fighting style names
        """
        if not character_id:
            return []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feature_name FROM character_features
                WHERE character_id = ? AND feature_name LIKE 'Fighting Style:%'
            """, (character_id,))

            styles = cursor.fetchall()
            return [style['feature_name'] for style in styles]

    def apply_savage_attacker(self,
                             dice_rolls: List[int],
                             num_dice: int,
                             die_size: int,
                             character: Dict[str, Any],
                             is_first_attack: bool = True) -> Tuple[List[int], str]:
        """
        Apply Savage Attacker feat - reroll damage dice and use higher result.
        Only applies to the first attack per round.

        Args:
            dice_rolls: Original damage rolls
            num_dice: Number of dice
            die_size: Size of each die
            character: Character data
            is_first_attack: Whether this is the first attack this round

        Returns:
            Tuple of (best_rolls, description)
        """
        # Only applies to first attack per round
        if not is_first_attack:
            return dice_rolls, ""

        # Check if character has Savage Attacker feat
        character_feats = character.get('feats', [])
        if 'Savage Attacker' not in character_feats:
            # Check database for feat
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM character_features
                    WHERE character_id = ? AND feature_name = 'Savage Attacker'
                    LIMIT 1
                """, (character.get('id', ''),))

                if not cursor.fetchone():
                    return dice_rolls, ""

        # Roll a second set
        second_rolls = [random.randint(1, die_size) for _ in range(num_dice)]

        # Compare totals and use the better set
        first_total = sum(dice_rolls)
        second_total = sum(second_rolls)

        if second_total > first_total:
            return second_rolls, f"Savage Attacker: rerolled for {second_total} (was {first_total})"
        else:
            return dice_rolls, f"Savage Attacker: kept original {first_total} (reroll was {second_total})"

    def apply_weapon_mastery_effects(self,
                                    weapon: Dict[str, Any],
                                    character: Dict[str, Any],
                                    target: Optional[Dict[str, Any]],
                                    hit: bool,
                                    damage_total: int = 0,
                                    attack_total: int = 0,
                                    chosen_mastery: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply weapon mastery effects based on the weapon's mastery property.

        Args:
            weapon: Weapon data including mastery property
            character: Character data
            target: Target data (optional)
            hit: Whether the attack hit
            damage_total: Total damage dealt
            attack_total: Total attack roll
            chosen_mastery: Override mastery (for Tactical Master)

        Returns:
            Dict describing mastery effects applied
        """
        effects = {}

        # Check if character has access to weapon mastery
        has_mastery_access = False
        if self.has_character_unlimited_mastery(character.get('id')):
            has_mastery_access = True
        else:
            # Check if they have limited mastery access
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT weapon_mastery_count FROM characters WHERE id = ?
                """, (character.get('id'),))
                result = cursor.fetchone()
                if result and result['weapon_mastery_count'] > 0:
                    has_mastery_access = True

        # If character can't use mastery, don't require weapon to have mastery property
        if not has_mastery_access:
            return effects

        # Get weapon's mastery property (only required if character can use mastery)
        mastery_type = weapon.get('mastery_property')
        if not mastery_type:
            raise ValueError(f"Weapon '{weapon.get('name', 'Unknown')}' missing mastery_property")

        # Apply Tactical Master override if provided
        if chosen_mastery and chosen_mastery != 'original':
            effects['tactical_master_used'] = {
                'original': mastery_type,
                'chosen': chosen_mastery.capitalize()
            }
            mastery_type = chosen_mastery.capitalize()

        weapon_name = weapon.get('name')
        if not weapon_name:
            raise ValueError("Weapon name is required but missing")

        mastery_effects = self._apply_specific_mastery(mastery_type, weapon_name, hit, damage_total, character)
        effects.update(mastery_effects)
        return effects

    def _apply_specific_mastery(self,
                               mastery_type: str,
                               weapon_name: str,
                               hit: bool,
                               damage_total: int,
                               character: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply specific weapon mastery effects.

        Returns:
            Dict describing the mastery effects
        """
        effects = {}

        if not mastery_type:
            return effects

        mastery_lower = mastery_type.lower()

        if mastery_lower == 'cleave' and hit:
            # Calculate ability modifier for cleave damage
            str_mod = (character.get('strength', 10) - 10) // 2
            effects['cleave'] = {
                'description': f'Can make an attack against a second creature within 5 feet for {str_mod} damage',
                'damage': str_mod,
                'type': 'ability_modifier_only'
            }
        elif mastery_lower == 'graze' and not hit:
            # Calculate ability modifier for graze damage
            str_mod = (character.get('strength', 10) - 10) // 2
            dex_mod = (character.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod) if 'finesse' in weapon_name.lower() else str_mod
            effects['graze'] = {
                'description': f'Deal {ability_mod} damage on a miss',
                'damage': ability_mod,
                'type': 'ability_modifier'
            }
        elif mastery_lower == 'nick' and hit:
            effects['nick'] = {
                'description': 'Make an additional attack as part of the Attack action',
                'restriction': 'Must have Light weapon in other hand',
                'type': 'extra_attack'
            }
        elif mastery_lower == 'push' and hit:
            effects['push'] = {
                'description': 'Push Large or smaller creature 10 feet away',
                'distance': 10,
                'size_limit': 'Large',
                'type': 'forced_movement'
            }
        elif mastery_lower == 'sap' and hit:
            effects['sap'] = {
                'description': 'Target has disadvantage on next attack roll',
                'duration': 'Until start of your next turn',
                'type': 'debuff'
            }
        elif mastery_lower == 'slow' and hit:
            effects['slow'] = {
                'description': 'Reduce target speed by 10 feet',
                'duration': 'Until start of your next turn',
                'amount': 10,
                'type': 'speed_reduction'
            }
        elif mastery_lower == 'topple' and hit:
            # Calculate save DC
            prof_bonus = 2 + ((character.get('level', 1) - 1) // 4)
            str_mod = (character.get('strength', 10) - 10) // 2
            save_dc = 8 + prof_bonus + str_mod
            effects['topple'] = {
                'description': f'Target must make Constitution save (DC {save_dc}) or be knocked prone',
                'save_dc': save_dc,
                'save_type': 'Constitution',
                'type': 'knockdown'
            }
        elif mastery_lower == 'vex' and hit:
            effects['vex'] = {
                'description': 'Gain advantage on next attack against this target',
                'duration': 'Before end of your next turn',
                'type': 'advantage'
            }

        return effects

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

    def _normalize_weapon_properties(self, weapon_props) -> str:
        """Normalize weapon properties from various formats to a string."""
        if isinstance(weapon_props, list):
            return ', '.join(weapon_props).lower()
        elif weapon_props is None:
            return ''
        else:
            return str(weapon_props).lower()

    def _get_die_size_from_weapon(self, weapon: Dict[str, Any]) -> int:
        """Extract die size from weapon damage dice string.

        Raises:
            ValueError: If damage_dice is missing from weapon
        """
        damage_dice = weapon.get('damage_dice')
        if not damage_dice:
            raise ValueError(f"Weapon '{weapon.get('name', 'Unknown')}' missing damage_dice")
        _, die_size = self._parse_damage_dice(damage_dice)
        return die_size

    def _parse_damage_dice(self, damage_dice: str) -> Tuple[int, int]:
        """Parse damage dice string into number of dice and die size.

        Args:
            damage_dice: String like '2d6', '1d8+2', etc.

        Returns:
            Tuple of (num_dice, die_size)

        Raises:
            ValueError: If damage_dice format is invalid
        """
        if not damage_dice:
            raise ValueError(f"Invalid damage dice format: '{damage_dice}' - cannot be empty")

        if 'd' not in damage_dice:
            raise ValueError(f"Invalid damage dice format: '{damage_dice}' - must contain 'd'")

        parts = damage_dice.split('d')
        if len(parts) != 2:
            raise ValueError(f"Invalid damage dice format: '{damage_dice}' - must be in format 'XdY'")

        try:
            # Parse number of dice (left side of 'd')
            if not parts[0]:
                raise ValueError(f"Missing number of dice in '{damage_dice}' - use '1d6' not 'd6'")
            num_dice = int(parts[0])

            # Parse die size (right side of 'd', strip modifiers)
            die_part = parts[1].split('+')[0].split('-')[0].strip()
            if not die_part:
                raise ValueError(f"Missing die size in '{damage_dice}'")
            die_size = int(die_part)

            if num_dice <= 0:
                raise ValueError(f"Number of dice must be positive: {num_dice}")
            if die_size <= 0:
                raise ValueError(f"Die size must be positive: {die_size}")

            return num_dice, die_size

        except ValueError as e:
            if "invalid literal for int()" in str(e):
                raise ValueError(f"Invalid number in damage dice '{damage_dice}': {e}")
            raise  # Re-raise our custom ValueError messages

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

    def can_use_tactical_master(self, character_id: str) -> bool:
        """Check if character can use Tactical Master (Fighter level 9+)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT class_id, level FROM characters WHERE id = ?
            """, (character_id,))
            result = cursor.fetchone()

            if not result:
                return False

            return result['class_id'].lower() == 'fighter' and result['level'] >= 9

    def _apply_sneak_attack_if_eligible(self,
                                       character: Dict[str, Any],
                                       weapon: Dict[str, Any],
                                       target: Optional[Dict[str, Any]],
                                       has_advantage: bool,
                                       has_disadvantage: bool,
                                       is_hidden: bool = False) -> Dict[str, Any]:
        """
        Apply Sneak Attack damage if the character is eligible.

        Args:
            character: Character data dictionary
            weapon: Weapon being used
            target: Target data (optional)
            has_advantage: Whether attack has advantage
            has_disadvantage: Whether attack has disadvantage

        Returns:
            Dict with sneak attack information
        """
        # Check if character is a rogue
        character_id = character.get('id')
        if not character_id:
            return self._no_sneak_attack("No character ID")

        # Import RogueAbilitiesService here to avoid circular imports
        try:
            from services.rogue_abilities import RogueAbilitiesService
        except ImportError:
            return self._no_sneak_attack("RogueAbilitiesService not available")

        rogue_service = RogueAbilitiesService(self.db_path)
        level = rogue_service.get_rogue_level(character_id)

        if level < 1:
            return self._no_sneak_attack("Not a rogue")

        # Check if weapon is eligible (finesse or ranged)
        if not self._is_sneak_attack_weapon(weapon):
            return self._no_sneak_attack("Weapon not eligible")

        # Check conditions for sneak attack
        sneak_attack_source = None

        # Priority 1: Attacking from hidden
        if is_hidden:
            sneak_attack_source = "hidden"

        # Condition 2: Has advantage (and no disadvantage)
        elif has_advantage and not has_disadvantage:
            sneak_attack_source = "advantage"

        # Condition 2: Tactical advantage (and no disadvantage)
        elif not has_disadvantage:
            # Check for tactical advantages that enable Sneak Attack in solo play
            tactical_advantage = self._check_allies_near_target(character_id, target)
            if tactical_advantage:
                sneak_attack_source = "tactical_advantage"

        if not sneak_attack_source:
            return self._no_sneak_attack("Conditions not met")

        # Check if sneak attack already used this turn
        if self._sneak_attack_used_this_turn(character_id):
            return self._no_sneak_attack("Already used this turn")

        # Calculate sneak attack damage
        base_damage_dice = rogue_service._calculate_sneak_attack_dice(level)

        # Check for active Cunning Strike effects and their costs
        cunning_strike_effects = self._get_active_cunning_strike_effects(character_id)
        total_dice_cost = sum(effect['cost'] for effect in cunning_strike_effects)

        # Ensure we don't spend more dice than we have
        if total_dice_cost > base_damage_dice:
            return self._no_sneak_attack(f"Insufficient dice for Cunning Strike effects (need {total_dice_cost}, have {base_damage_dice})")

        # Calculate actual damage dice after paying costs
        actual_damage_dice = base_damage_dice - total_dice_cost
        damage_dice_str = f"{actual_damage_dice}d6"

        # Roll the damage
        import random
        damage_rolls = [random.randint(1, 6) for _ in range(actual_damage_dice)] if actual_damage_dice > 0 else []

        # Mark sneak attack as used this turn
        self._mark_sneak_attack_used(character_id)

        # Apply Cunning Strike effects
        cunning_strike_results = []
        if cunning_strike_effects:
            cunning_strike_results = self._apply_cunning_strike_effects(character_id, cunning_strike_effects, target)

        return {
            'eligible': True,
            'damage_dice': damage_dice_str,
            'damage_rolls': damage_rolls,
            'damage_total': sum(damage_rolls),
            'source': sneak_attack_source,
            'level': level,
            'cunning_strike_effects': cunning_strike_results,
            'dice_spent_on_effects': total_dice_cost
        }

    def _no_sneak_attack(self, reason: str) -> Dict[str, Any]:
        """Return a no-sneak-attack result."""
        return {
            'eligible': False,
            'damage_dice': "0d6",
            'damage_rolls': [],
            'damage_total': 0,
            'source': None,
            'reason': reason
        }

    def _is_sneak_attack_weapon(self, weapon: Dict[str, Any]) -> bool:
        """Check if weapon is eligible for sneak attack (finesse or ranged)."""
        if not weapon:
            return False

        weapon_properties = self._normalize_weapon_properties(weapon.get('weapon_properties'))
        weapon_type = weapon.get('weapon_type', '').lower()

        # Check for finesse property
        if 'finesse' in weapon_properties:
            return True

        # Check for ranged weapons
        if weapon_type in ['ranged', 'simple ranged', 'martial ranged']:
            return True

        # Check for specific ranged weapon types by name
        weapon_name = weapon.get('name', '').lower()
        ranged_weapons = ['shortbow', 'longbow', 'light crossbow', 'heavy crossbow',
                         'hand crossbow', 'dart', 'sling', 'blowgun']

        return any(ranged_weapon in weapon_name for ranged_weapon in ranged_weapons)

    def _check_allies_near_target(self, character_id: str, target: Optional[Dict[str, Any]]) -> bool:
        """
        Check for favorable tactical conditions for Sneak Attack in solo play.
        In solo play, this checks for tactical advantages rather than allies.
        """
        if not target:
            return False

        # For solo play, check for tactical advantages that would allow Sneak Attack:
        # 1. Target is engaged with summoned creatures/familiars
        # 2. Target is distracted (casting, reloading, etc.)
        # 3. Target is flanked by environmental hazards
        # 4. Target is focused on another threat

        # Simplified implementation for solo play:
        # Check if target has any conditions that would make them vulnerable
        target_conditions = target.get('conditions', [])
        vulnerable_conditions = ['prone', 'restrained', 'stunned', 'paralyzed', 'incapacitated', 'surprised']

        if any(condition in target_conditions for condition in vulnerable_conditions):
            return True

        # Check if target is distracted (e.g., casting a spell, reloading)
        target_state = target.get('current_action', '')
        distracted_states = ['casting', 'reloading', 'concentrating', 'channeling']

        if any(state in target_state.lower() for state in distracted_states):
            return True

        # For general solo play balance, provide some chance for tactical positioning
        # This represents finding an opening in combat
        import random
        return random.randint(1, 6) >= 5  # 33% chance of finding a tactical opening

    def _sneak_attack_used_this_turn(self, character_id: str) -> bool:
        """Check if sneak attack has been used this turn."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sneak_attack_used_this_turn
                FROM rogue_features
                WHERE character_id = ?
            """, (character_id,))

            result = cursor.fetchone()
            return result and result['sneak_attack_used_this_turn']

    def _mark_sneak_attack_used(self, character_id: str) -> None:
        """Mark sneak attack as used this turn."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE rogue_features
                SET sneak_attack_used_this_turn = 1
                WHERE character_id = ?
            """, (character_id,))
            conn.commit()

    def _get_active_cunning_strike_effects(self, character_id: str) -> List[Dict[str, Any]]:
        """Get list of active Cunning Strike effects from character context."""
        try:
            from services.cunning_strike_manager import CunningStrikeManager
            manager = CunningStrikeManager(self.db_path)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT cunning_strike_selection
                    FROM character_combat_state
                    WHERE character_id = ?
                """, (character_id,))
                result = cursor.fetchone()

                if not result or not result['cunning_strike_selection']:
                    return []

                import json
                effect_ids = json.loads(result['cunning_strike_selection'])

                effects = []
                for effect_id in effect_ids:
                    from services.cunning_strike_manager import CunningStrikeEffect
                    effect_enum = CunningStrikeEffect(effect_id)
                    option = manager.CUNNING_STRIKE_OPTIONS[effect_enum]
                    effects.append({
                        'effect': effect_enum,
                        'name': option.name,
                        'cost': option.dice_cost,
                        'save_type': option.save_type,
                        'condition': option.condition,
                        'duration': option.duration
                    })

                return effects

        except Exception as e:
            print(f"[WeaponAttackService] Error getting cunning strike effects: {e}")
            return []

    def _apply_cunning_strike_effects(self, character_id: str, effects: List[Dict[str, Any]], target: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply Cunning Strike effects to the target with saves and conditions."""
        if not target or not effects:
            return []

        results = []
        target_id = target.get('id')
        if not target_id:
            return []

        try:
            from services.condition_manager import ConditionManager, ConditionType, ActiveCondition
            condition_manager = ConditionManager(self.db_path)
        except Exception as e:
            print(f"[WeaponAttackService] Error importing condition manager: {e}")
            return []

        save_dc = self._calculate_cunning_strike_save_dc(character_id)

        for effect_data in effects:
            effect_name = effect_data['name']
            effect_cost = effect_data['cost']
            save_type = effect_data['save_type']
            condition_type = effect_data.get('condition')
            duration = effect_data.get('duration', 'instant')

            effect_result = {
                'effect_name': effect_name,
                'dice_cost': effect_cost,
                'save_dc': save_dc
            }

            if save_type != 'none' and condition_type:
                save_roll = self._roll_saving_throw(target, save_type, save_dc)
                effect_result['save_type'] = save_type
                effect_result['save_roll'] = save_roll['roll']
                effect_result['save_result'] = save_roll['success']

                if not save_roll['success']:
                    try:
                        condition = ActiveCondition(
                            condition_type=ConditionType(condition_type),
                            source=f"Cunning Strike: {effect_name}",
                            duration_type='rounds' if 'minute' in duration else 'turns',
                            duration_remaining=10 if 'minute' in duration else 1,
                            save_dc=save_dc,
                            save_ability=save_type,
                            save_frequency='end_of_turn' if 'minute' in duration else 'none'
                        )

                        applied = condition_manager.add_condition(target_id, condition)
                        effect_result['condition_applied'] = applied
                        effect_result['condition'] = condition_type
                        effect_result['message'] = f"{effect_name}: Save failed, {condition_type} applied!"
                    except Exception as e:
                        print(f"[WeaponAttackService] Error applying condition: {e}")
                        effect_result['condition_applied'] = False
                        effect_result['message'] = f"{effect_name}: Save failed (condition not applied due to error)"
                else:
                    effect_result['condition_applied'] = False
                    effect_result['message'] = f"{effect_name}: Save successful, no effect"
            else:
                effect_result['message'] = f"{effect_name}: Applied (no save)"
                effect_result['condition_applied'] = True

            results.append(effect_result)

        self._clear_cunning_strike_selection(character_id)
        return results

    def _roll_saving_throw(self, target: Dict[str, Any], ability: str, dc: int) -> Dict[str, Any]:
        """Roll a saving throw for a target."""
        import random
        ability_score = target.get(ability, 10)
        ability_mod = (ability_score - 10) // 2

        roll = random.randint(1, 20)
        total = roll + ability_mod

        return {
            'roll': roll,
            'modifier': ability_mod,
            'total': total,
            'success': total >= dc,
            'dc': dc
        }

    def _clear_cunning_strike_selection(self, character_id: str):
        """Clear Cunning Strike selection after use."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE character_combat_state
                    SET cunning_strike_selection = NULL
                    WHERE character_id = ?
                """, (character_id,))
                conn.commit()
        except Exception as e:
            print(f"[WeaponAttackService] Error clearing cunning strike selection: {e}")

    def _calculate_cunning_strike_save_dc(self, character_id: str) -> int:
        """Calculate save DC for Cunning Strike effects: 8 + DEX mod + proficiency bonus."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dexterity, level FROM characters WHERE id = ?
            """, (character_id,))
            result = cursor.fetchone()

            if not result:
                return 8  # Fallback

            dexterity = result['dexterity']
            level = result['level']

            dex_mod = (dexterity - 10) // 2
            prof_bonus = 2 + ((level - 1) // 4)  # Standard D&D proficiency progression

            return 8 + dex_mod + prof_bonus
