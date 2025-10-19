# core
# category: core
"""
Cunning Strike Manager for TaleKeeper

Manages Rogue Cunning Strike system including:
- Dice cost calculations
- Save DC calculations
- Effect application
- Multiple effect stacking (level 11+)
- Sneak Attack eligibility checking
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CunningStrikeEffect(Enum):
    POISON = "poison"
    TRIP = "trip"
    WITHDRAW = "withdraw"
    DAZE = "daze"
    KNOCK_OUT = "knock_out"
    OBSCURE = "obscure"


@dataclass
class CunningStrikeOption:
    effect: CunningStrikeEffect
    name: str
    dice_cost: int
    min_level: int
    save_type: str
    condition: Optional[str]
    duration: str
    description: str
    requires_poisoners_kit: bool = False


class CunningStrikeManager:
    """Manages Cunning Strike mechanics for Rogues"""

    CUNNING_STRIKE_OPTIONS = {
        CunningStrikeEffect.POISON: CunningStrikeOption(
            effect=CunningStrikeEffect.POISON,
            name="Poison Strike",
            dice_cost=1,
            min_level=5,
            save_type="constitution",
            condition="poisoned",
            duration="1 minute",
            description="Target makes Con save or is Poisoned for 1 minute (repeats save each turn)",
            requires_poisoners_kit=True
        ),
        CunningStrikeEffect.TRIP: CunningStrikeOption(
            effect=CunningStrikeEffect.TRIP,
            name="Trip Strike",
            dice_cost=1,
            min_level=5,
            save_type="dexterity",
            condition="prone",
            duration="instant",
            description="Target (Large or smaller) makes Dex save or is Prone"
        ),
        CunningStrikeEffect.WITHDRAW: CunningStrikeOption(
            effect=CunningStrikeEffect.WITHDRAW,
            name="Withdraw Strike",
            dice_cost=1,
            min_level=5,
            save_type="none",
            condition=None,
            duration="instant",
            description="Move up to half speed without provoking opportunity attacks"
        ),
        CunningStrikeEffect.DAZE: CunningStrikeOption(
            effect=CunningStrikeEffect.DAZE,
            name="Daze Strike",
            dice_cost=2,
            min_level=14,
            save_type="constitution",
            condition="dazed",
            duration="1 turn",
            description="Target makes Con save or can only move OR take action/bonus action on next turn"
        ),
        CunningStrikeEffect.KNOCK_OUT: CunningStrikeOption(
            effect=CunningStrikeEffect.KNOCK_OUT,
            name="Knock Out Strike",
            dice_cost=6,
            min_level=14,
            save_type="constitution",
            condition="unconscious",
            duration="1 minute",
            description="Target makes Con save or is Unconscious for 1 minute or until damaged"
        ),
        CunningStrikeEffect.OBSCURE: CunningStrikeOption(
            effect=CunningStrikeEffect.OBSCURE,
            name="Obscure Strike",
            dice_cost=3,
            min_level=14,
            save_type="dexterity",
            condition="blinded",
            duration="until end of target's next turn",
            description="Target makes Dex save or is Blinded until end of its next turn"
        )
    }

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_available_cunning_strikes(self, character_id: str) -> List[Dict[str, Any]]:
        """Get list of available Cunning Strike options for character"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.level, c.dexterity,
                       COALESCE(
                           (SELECT COUNT(*) FROM character_inventory
                            WHERE character_id = c.id
                            AND item_name LIKE '%Poisoner%Kit%'),
                           0
                       ) as has_poisoners_kit
                FROM characters c
                WHERE c.id = ? AND c.class_id = 'rogue'
            """, (character_id,))
            result = cursor.fetchone()

            if not result:
                return []

            level = result['level']
            has_kit = result['has_poisoners_kit'] > 0

        available = []
        for option in self.CUNNING_STRIKE_OPTIONS.values():
            if level >= option.min_level:
                is_available = True
                reason = None

                if option.requires_poisoners_kit and not has_kit:
                    is_available = False
                    reason = "Requires Poisoner's Kit in inventory"

                available.append({
                    'effect': option.effect.value,
                    'name': option.name,
                    'dice_cost': option.dice_cost,
                    'save_type': option.save_type,
                    'condition': option.condition,
                    'duration': option.duration,
                    'description': option.description,
                    'available': is_available,
                    'unavailable_reason': reason
                })

        return available

    def calculate_sneak_attack_with_cost(self, character_id: str,
                                         effects: List[CunningStrikeEffect]) -> Dict[str, Any]:
        """Calculate sneak attack damage after Cunning Strike costs"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level FROM characters WHERE id = ? AND class_id = 'rogue'
            """, (character_id,))
            result = cursor.fetchone()

            if not result:
                return {'error': 'Character not found or not a rogue'}

            level = result['level']

        base_dice = self._calculate_sneak_attack_dice(level)

        total_cost = sum(
            self.CUNNING_STRIKE_OPTIONS[effect].dice_cost
            for effect in effects
        )

        remaining_dice = max(0, base_dice - total_cost)

        return {
            'base_sneak_attack_dice': base_dice,
            'total_dice_cost': total_cost,
            'remaining_damage_dice': remaining_dice,
            'base_damage_string': f"{base_dice}d6",
            'remaining_damage_string': f"{remaining_dice}d6" if remaining_dice > 0 else "0",
            'effects_applied': [effect.value for effect in effects]
        }

    def _calculate_sneak_attack_dice(self, level: int) -> int:
        """Calculate sneak attack dice based on rogue level"""
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

    def calculate_save_dc(self, character_id: str) -> int:
        """Calculate Cunning Strike save DC (8 + DEX mod + proficiency)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level, dexterity FROM characters WHERE id = ?
            """, (character_id,))
            result = cursor.fetchone()

            if not result:
                return 8

            level = result['level']
            dexterity = result['dexterity']

        dex_mod = (dexterity - 10) // 2
        proficiency = self._get_proficiency_bonus(level)

        return 8 + dex_mod + proficiency

    def _get_proficiency_bonus(self, level: int) -> int:
        """Get proficiency bonus based on level"""
        if level < 5:
            return 2
        elif level < 9:
            return 3
        elif level < 13:
            return 4
        elif level < 17:
            return 5
        else:
            return 6

    def can_use_multiple_effects(self, character_id: str) -> bool:
        """Check if rogue can use multiple Cunning Strike effects (level 11+)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level FROM characters WHERE id = ? AND class_id = 'rogue'
            """, (character_id,))
            result = cursor.fetchone()

            if not result:
                return False

            return result['level'] >= 11

    def validate_cunning_strike_selection(self, character_id: str,
                                         effects: List[CunningStrikeEffect]) -> Dict[str, Any]:
        """Validate Cunning Strike effect selection"""
        if not effects:
            return {'valid': False, 'error': 'No effects selected'}

        max_effects = 2 if self.can_use_multiple_effects(character_id) else 1
        if len(effects) > max_effects:
            return {
                'valid': False,
                'error': f'Cannot select more than {max_effects} effect(s)'
            }

        available = self.get_available_cunning_strikes(character_id)
        available_effects = {opt['effect'] for opt in available if opt['available']}

        for effect in effects:
            if effect.value not in available_effects:
                return {
                    'valid': False,
                    'error': f'{effect.value} is not available'
                }

        damage_calc = self.calculate_sneak_attack_with_cost(character_id, effects)
        if damage_calc['remaining_damage_dice'] < 0:
            return {
                'valid': False,
                'error': 'Not enough sneak attack dice for selected effects'
            }

        return {'valid': True, 'damage_calculation': damage_calc}

    def apply_cunning_strike(self, character_id: str, target_id: str,
                           effects: List[CunningStrikeEffect],
                           attack_damage: int) -> Dict[str, Any]:
        """Apply Cunning Strike effects to target"""
        validation = self.validate_cunning_strike_selection(character_id, effects)
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error']
            }

        damage_calc = validation['damage_calculation']
        save_dc = self.calculate_save_dc(character_id)

        results = {
            'success': True,
            'final_damage': attack_damage,
            'sneak_attack_dice_remaining': damage_calc['remaining_damage_dice'],
            'sneak_attack_dice_spent': damage_calc['total_dice_cost'],
            'save_dc': save_dc,
            'effects': []
        }

        for effect in effects:
            option = self.CUNNING_STRIKE_OPTIONS[effect]
            effect_result = {
                'effect_name': option.name,
                'dice_cost': option.dice_cost,
                'save_type': option.save_type,
                'condition': option.condition,
                'duration': option.duration
            }

            if option.save_type != 'none':
                effect_result['requires_save'] = True
                effect_result['save_dc'] = save_dc
            else:
                effect_result['requires_save'] = False

            results['effects'].append(effect_result)

        return results

    def check_sneak_attack_eligibility(self, character_id: str,
                                      combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if Sneak Attack is eligible this attack"""
        has_advantage = combat_context.get('has_advantage', False)
        has_disadvantage = combat_context.get('has_disadvantage', False)
        allies_within_5ft = combat_context.get('allies_within_5ft', [])
        weapon = combat_context.get('weapon', {})

        if not self._is_sneak_attack_weapon(weapon):
            return {
                'eligible': False,
                'reason': 'Weapon must have Finesse or be Ranged'
            }

        if has_disadvantage:
            return {
                'eligible': False,
                'reason': 'Cannot use Sneak Attack with disadvantage'
            }

        if has_advantage:
            return {
                'eligible': True,
                'reason': 'Has advantage on attack'
            }

        if len(allies_within_5ft) > 0:
            return {
                'eligible': True,
                'reason': 'Ally within 5 feet of target'
            }

        return {
            'eligible': False,
            'reason': 'Need advantage or ally within 5ft of target'
        }

    def _is_sneak_attack_weapon(self, weapon: Dict[str, Any]) -> bool:
        """Check if weapon is eligible for sneak attack"""
        if not weapon:
            return False

        properties = weapon.get('weapon_properties', weapon.get('properties', ''))
        if isinstance(properties, list):
            properties = ', '.join(properties)
        properties = properties.lower() if properties else ''

        if 'finesse' in properties:
            return True

        weapon_type = weapon.get('weapon_type', '').lower()
        if weapon_type in ['ranged', 'simple ranged', 'martial ranged']:
            return True

        weapon_name = weapon.get('name', '').lower()
        ranged_weapons = ['shortbow', 'longbow', 'light crossbow', 'heavy crossbow',
                         'hand crossbow', 'dart', 'sling', 'blowgun']
        return any(ranged_weapon in weapon_name for ranged_weapon in ranged_weapons)

    def get_cunning_strike_preview(self, character_id: str,
                                   effects: List[CunningStrikeEffect]) -> Dict[str, Any]:
        """Get preview of Cunning Strike effects without applying"""
        if not effects:
            return {'error': 'No effects selected'}

        damage_calc = self.calculate_sneak_attack_with_cost(character_id, effects)
        save_dc = self.calculate_save_dc(character_id)

        preview = {
            'base_sneak_attack': f"{damage_calc['base_sneak_attack_dice']}d6",
            'dice_cost': damage_calc['total_dice_cost'],
            'remaining_damage': f"{damage_calc['remaining_damage_dice']}d6",
            'save_dc': save_dc,
            'effects': []
        }

        for effect in effects:
            option = self.CUNNING_STRIKE_OPTIONS[effect]
            preview['effects'].append({
                'name': option.name,
                'cost': f"{option.dice_cost}d6",
                'condition': option.condition,
                'save': option.save_type.title() if option.save_type != 'none' else 'None',
                'duration': option.duration,
                'description': option.description
            })

        return preview
