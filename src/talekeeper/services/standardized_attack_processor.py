# core
# category: utility
"""
Standardized Monster Attack Processor

Processes monster attacks using the new standardized JSON format.
Much simpler than regex parsing - uses direct property access.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AttackType(Enum):
    MELEE = "melee"
    RANGED = "ranged"
    AREA = "area"
    BREATH_WEAPON = "breath_weapon"
    AURA = "aura"
    SPECIAL = "special"


class EffectType(Enum):
    SAVE_OR_CONDITION = "save_or_condition"
    SAVE_OR_DAMAGE = "save_or_damage"
    AUTOMATIC_CONDITION = "automatic_condition"
    CONDITIONAL_CONDITION = "conditional_condition"
    LINKED_CONDITION = "linked_condition"
    SIZE_CONDITION = "size_condition"
    AREA_SAVE = "area_save"
    SAVE_OR_MULTIPLE = "save_or_multiple"


@dataclass
class AttackDamage:
    dice: str
    type: str


@dataclass
class AttackEffect:
    type: EffectType
    condition: Optional[str] = None
    save_dc: Optional[int] = None
    save_ability: Optional[str] = None
    duration: Optional[str] = None
    save_frequency: Optional[str] = None
    escape_dc: Optional[int] = None
    escape_type: Optional[str] = None
    damage_fail: Optional[AttackDamage] = None
    damage_success: Optional[AttackDamage] = None
    trigger: Optional[str] = None
    while_condition: Optional[str] = None
    also_condition: Optional[str] = None
    max_size: Optional[str] = None
    immunity_on_success: Optional[str] = None
    effects_on_fail: Optional[List[Dict]] = None
    effects_on_success: Optional[List[Dict]] = None


@dataclass
class StandardizedAttack:
    name: str
    attack_type: AttackType
    attack_bonus: int
    reach: Optional[int] = None
    range_normal: Optional[int] = None
    range_long: Optional[int] = None
    recharge: Optional[str] = None
    primary_damage: Optional[AttackDamage] = None
    additional_damage: Optional[List[AttackDamage]] = None
    effects: List[AttackEffect] = None
    description: str = ""

    def __post_init__(self):
        if self.effects is None:
            self.effects = []
        if self.additional_damage is None:
            self.additional_damage = []


class StandardizedAttackProcessor:
    """Process monster attacks using standardized JSON format."""

    def process_monster_attacks(self, actions_json: str) -> List[StandardizedAttack]:
        """
        Process monster actions JSON into standardized attack objects.

        Args:
            actions_json: JSON string containing standardized attack data

        Returns:
            List of StandardizedAttack objects
        """
        if not actions_json:
            return []

        try:
            actions_data = json.loads(actions_json)
        except json.JSONDecodeError:
            return []

        attacks = []
        for action_data in actions_data:
            if self._is_attack(action_data):
                attack = self._parse_standardized_attack(action_data)
                if attack:
                    attacks.append(attack)

        return attacks

    def _is_attack(self, action_data: Dict[str, Any]) -> bool:
        """Check if action data represents an attack."""
        return (
            "attack_type" in action_data and
            action_data.get("attack_type") in [e.value for e in AttackType]
        )

    def _parse_standardized_attack(self, action_data: Dict[str, Any]) -> Optional[StandardizedAttack]:
        """Parse standardized attack data into StandardizedAttack object."""
        try:
            # Basic attack properties
            attack = StandardizedAttack(
                name=action_data["name"],
                attack_type=AttackType(action_data["attack_type"]),
                attack_bonus=action_data.get("attack_bonus", 0),
                reach=action_data.get("reach"),
                range_normal=action_data.get("range_normal"),
                range_long=action_data.get("range_long"),
                recharge=action_data.get("recharge"),
                description=action_data.get("description", "")
            )

            # Parse damage
            damage_data = action_data.get("damage", {})
            if "primary" in damage_data:
                primary = damage_data["primary"]
                attack.primary_damage = AttackDamage(
                    dice=primary["dice"],
                    type=primary["type"]
                )

            if "additional" in damage_data:
                for additional in damage_data["additional"]:
                    attack.additional_damage.append(AttackDamage(
                        dice=additional["dice"],
                        type=additional["type"]
                    ))

            # Parse effects
            for effect_data in action_data.get("effects", []):
                effect = self._parse_effect(effect_data)
                if effect:
                    attack.effects.append(effect)

            return attack

        except (KeyError, ValueError) as e:
            print(f"Error parsing attack {action_data.get('name', 'Unknown')}: {e}")
            return None

    def _parse_effect(self, effect_data: Dict[str, Any]) -> Optional[AttackEffect]:
        """Parse effect data into AttackEffect object."""
        try:
            effect_type = EffectType(effect_data["type"])

            effect = AttackEffect(
                type=effect_type,
                condition=effect_data.get("condition"),
                save_dc=effect_data.get("save_dc"),
                save_ability=effect_data.get("save_ability"),
                duration=effect_data.get("duration"),
                save_frequency=effect_data.get("save_frequency"),
                escape_dc=effect_data.get("escape_dc"),
                escape_type=effect_data.get("escape_type"),
                trigger=effect_data.get("trigger"),
                while_condition=effect_data.get("while_condition"),
                also_condition=effect_data.get("also_condition"),
                max_size=effect_data.get("max_size"),
                immunity_on_success=effect_data.get("immunity_on_success"),
                effects_on_fail=effect_data.get("effects_on_fail"),
                effects_on_success=effect_data.get("effects_on_success")
            )

            # Parse damage effects
            if "damage_fail" in effect_data:
                damage_fail = effect_data["damage_fail"]
                effect.damage_fail = AttackDamage(
                    dice=damage_fail["dice"],
                    type=damage_fail["type"]
                )

            if "damage_success" in effect_data:
                damage_success = effect_data["damage_success"]
                effect.damage_success = AttackDamage(
                    dice=damage_success["dice"],
                    type=damage_success["type"]
                )

            return effect

        except (KeyError, ValueError) as e:
            print(f"Error parsing effect {effect_data.get('type', 'Unknown')}: {e}")
            return None

    def get_attack_summary(self, attack: StandardizedAttack) -> str:
        """Generate a human-readable summary of an attack."""
        summary = f"{attack.name} ({attack.attack_type.value})"

        if attack.attack_bonus:
            summary += f" +{attack.attack_bonus} to hit"

        if attack.reach:
            summary += f", reach {attack.reach} ft."

        if attack.range_normal:
            summary += f", range {attack.range_normal}"
            if attack.range_long:
                summary += f"/{attack.range_long}"
            summary += " ft."

        if attack.recharge:
            summary += f" (Recharge {attack.recharge})"

        if attack.primary_damage and attack.primary_damage.dice != "0":
            summary += f". {attack.primary_damage.dice} {attack.primary_damage.type} damage"

        for additional in attack.additional_damage:
            summary += f" plus {additional.dice} {additional.type} damage"

        return summary

    def get_effect_summary(self, effect: AttackEffect) -> str:
        """Generate a human-readable summary of an effect."""
        if effect.type == EffectType.SAVE_OR_CONDITION:
            return f"DC {effect.save_dc} {effect.save_ability} save or be {effect.condition}"

        elif effect.type == EffectType.SAVE_OR_DAMAGE:
            fail_dmg = f"{effect.damage_fail.dice} {effect.damage_fail.type}" if effect.damage_fail else "damage"
            success_dmg = f"{effect.damage_success.dice} {effect.damage_success.type}" if effect.damage_success else "half damage"
            return f"DC {effect.save_dc} {effect.save_ability} save: {fail_dmg} on failure, {success_dmg} on success"

        elif effect.type == EffectType.AUTOMATIC_CONDITION:
            escape_text = ""
            if effect.escape_dc and effect.escape_type:
                escape_text = f" (escape DC {effect.escape_dc} {effect.escape_type})"
            return f"Automatically {effect.condition}{escape_text}"

        elif effect.type == EffectType.SIZE_CONDITION:
            return f"{effect.max_size} or smaller creatures are {effect.condition}"

        else:
            return f"{effect.type.value} effect"


# Test function
def test_standardized_processor():
    """Test the standardized processor with migrated data."""
    import sqlite3

    processor = StandardizedAttackProcessor()
    test_monsters = ["Giant Spider", "Ankheg", "Ghast", "Air Elemental", "Basilisk", "Adult Black Dragon", "Aarakocra", "Aboleth", "Acolyte", "Balor", "Deva"]

    with sqlite3.connect("talekeeper.db") as conn:
        cursor = conn.cursor()

        for monster_name in test_monsters:
            cursor.execute("SELECT name, actions FROM monsters WHERE name = ?", (monster_name,))
            row = cursor.fetchone()

            if row:
                name, actions_json = row
                attacks = processor.process_monster_attacks(actions_json)

                print(f"\n{name} Attacks:")
                for attack in attacks:
                    print(f"  {processor.get_attack_summary(attack)}")
                    for effect in attack.effects:
                        print(f"    - {processor.get_effect_summary(effect)}")

                if not attacks:
                    print("  No attacks found")
            else:
                print(f"\n{monster_name}: Not found in database")

    return True


if __name__ == "__main__":
    test_standardized_processor()