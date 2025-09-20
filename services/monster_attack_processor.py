"""
Monster Attack Processor

Handles parsing and executing monster attacks with condition effects,
saving throws, and special mechanics. Integrates with the condition system
to automatically apply conditions like prone, grappled, poisoned, etc.
"""

import re
import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from services.condition_manager import ConditionManager, ConditionType, ActiveCondition
except ImportError:
    ConditionManager = None
    ConditionType = None
    ActiveCondition = None


class AttackResult(Enum):
    """Result of an attack roll."""
    MISS = "miss"
    HIT = "hit"
    CRITICAL_HIT = "critical_hit"


@dataclass
class SavingThrow:
    """Represents a saving throw requirement."""
    dc: int
    ability: str  # "constitution", "dexterity", etc.
    condition_on_failure: ConditionType
    damage_on_failure: Optional[int] = None
    damage_on_success: Optional[int] = None  # Half damage on success
    duration_type: str = "save_ends"
    duration_rounds: int = -1  # -1 for until saved
    save_frequency: str = "end_of_turn"


@dataclass
class AttackEffect:
    """Represents a special effect from an attack."""
    effect_type: str  # "condition", "damage", "movement", "special"
    condition: Optional[ConditionType] = None
    saving_throw: Optional[SavingThrow] = None
    automatic: bool = False  # No save required
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    description: str = ""


@dataclass
class MonsterAttack:
    """Parsed monster attack with all effects."""
    name: str
    attack_bonus: int
    reach: int
    damage_dice: str
    damage_type: str
    base_damage: int
    effects: List[AttackEffect]
    description: str


class MonsterAttackProcessor:
    """Processes monster attacks and applies condition effects."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        if ConditionManager:
            self.condition_manager = ConditionManager(db_path)
        else:
            self.condition_manager = None

    def parse_monster_actions(self, actions_json: str) -> List[MonsterAttack]:
        """Parse monster actions from database JSON into structured attacks."""
        try:
            actions = json.loads(actions_json)
            parsed_attacks = []

            for action in actions:
                if self._is_attack_action(action):
                    attack = self._parse_attack_action(action)
                    if attack:
                        parsed_attacks.append(attack)

            return parsed_attacks
        except (json.JSONDecodeError, Exception) as e:
            print(f"[MonsterAttackProcessor] Error parsing actions: {e}")
            return []

    def _is_attack_action(self, action: Dict[str, Any]) -> bool:
        """Check if an action is an attack."""
        entries = action.get('entries', [])
        if not entries:
            return False

        first_entry = entries[0] if isinstance(entries, list) else str(entries)

        # Look for attack indicators
        attack_indicators = ['{@atk mw}', '{@atk rw}', 'Melee Attack', 'Ranged Attack', '@hit']
        return any(indicator in str(first_entry) for indicator in attack_indicators)

    def _parse_attack_action(self, action: Dict[str, Any]) -> Optional[MonsterAttack]:
        """Parse a single attack action."""
        name = action.get('name', 'Unknown Attack')
        entries = action.get('entries', [])

        if not entries:
            return None

        # Join all entries for full parsing
        full_text = ' '.join(str(entry) for entry in entries)

        # Parse attack bonus
        attack_bonus = self._extract_attack_bonus(full_text)

        # Parse reach
        reach = self._extract_reach(full_text)

        # Parse damage
        damage_dice, damage_type, base_damage = self._extract_damage(full_text)

        # Parse special effects
        effects = self._extract_effects(full_text, name)

        return MonsterAttack(
            name=name,
            attack_bonus=attack_bonus,
            reach=reach,
            damage_dice=damage_dice,
            damage_type=damage_type,
            base_damage=base_damage,
            effects=effects,
            description=full_text
        )

    def _extract_attack_bonus(self, text: str) -> int:
        """Extract attack bonus from attack text."""
        # Look for {@hit X} pattern
        hit_match = re.search(r'\{@hit (\d+)\}', text)
        if hit_match:
            return int(hit_match.group(1))

        # Look for "+X to hit" pattern
        to_hit_match = re.search(r'\+(\d+) to hit', text)
        if to_hit_match:
            return int(to_hit_match.group(1))

        return 0

    def _extract_reach(self, text: str) -> int:
        """Extract reach from attack text."""
        reach_match = re.search(r'reach (\d+) ft', text)
        if reach_match:
            return int(reach_match.group(1))
        return 5  # Default melee reach

    def _extract_damage(self, text: str) -> Tuple[str, str, int]:
        """Extract damage dice, type, and average from attack text."""
        # Look for {@damage XdY + Z} pattern or {@h}X ({@damage XdY + Z}) type
        damage_match = re.search(r'\{@damage ([^}]+)\} (\w+)', text)
        if damage_match:
            dice_expr = damage_match.group(1)
            damage_type = damage_match.group(2).lower()
            average = self._calculate_average_damage(dice_expr)
            return dice_expr, damage_type, average

        # Look for simpler patterns
        simple_match = re.search(r'(\d+) \(([^)]+)\) (\w+)', text)
        if simple_match:
            average = int(simple_match.group(1))
            dice_expr = simple_match.group(2)
            damage_type = simple_match.group(3).lower()
            return dice_expr, damage_type, average

        return "1d4", "bludgeoning", 2

    def _calculate_average_damage(self, dice_expr: str) -> int:
        """Calculate average damage from dice expression."""
        try:
            # Handle XdY+Z format
            if 'd' in dice_expr:
                parts = dice_expr.replace(' ', '').replace('+', ' +').replace('-', ' -').split()
                total = 0

                for part in parts:
                    if 'd' in part:
                        # XdY format
                        if part.startswith('+') or part.startswith('-'):
                            multiplier = -1 if part.startswith('-') else 1
                            part = part[1:]
                        else:
                            multiplier = 1

                        num_dice, die_size = part.split('d')
                        num_dice = int(num_dice) if num_dice else 1
                        die_size = int(die_size)
                        average = num_dice * (die_size + 1) / 2
                        total += multiplier * average
                    else:
                        # Flat modifier
                        total += int(part)

                return int(total)
            else:
                return int(dice_expr)
        except:
            return 1

    def _extract_effects(self, text: str, attack_name: str) -> List[AttackEffect]:
        """Extract special effects from attack text."""
        effects = []

        # Look for conditions with saves
        effects.extend(self._extract_condition_effects(text, attack_name))

        # Look for automatic conditions (like grappled on hit)
        effects.extend(self._extract_automatic_conditions(text))

        # Look for poison damage with conditions
        effects.extend(self._extract_poison_effects(text))

        return effects

    def _extract_condition_effects(self, text: str, attack_name: str) -> List[AttackEffect]:
        """Extract conditions that require saving throws."""
        effects = []

        # Pattern: "must succeed on a DC X [ability] saving throw or be [condition]"
        save_pattern = r'must succeed on a \{@dc (\d+)\} (\w+) saving throw or be \{@condition ([^}]+)\}'

        for match in re.finditer(save_pattern, text):
            dc = int(match.group(1))
            ability = match.group(2).lower()
            condition_name = match.group(3).lower()

            # Map condition names to our enum
            condition_type = self._map_condition_name(condition_name)
            if condition_type:
                saving_throw = SavingThrow(
                    dc=dc,
                    ability=ability,
                    condition_on_failure=condition_type,
                    duration_type="save_ends",
                    save_frequency="end_of_turn"
                )

                effects.append(AttackEffect(
                    effect_type="condition",
                    condition=condition_type,
                    saving_throw=saving_throw,
                    automatic=False,
                    description=f"{attack_name} save effect"
                ))

        # Alternative pattern: "DC X [ability] saving throw. Failure: [condition]"
        alt_pattern = r'(\w+) Saving Throw:\s*DC (\d+)[^.]*Failure:\s*[^{]*\{@condition ([^}]+)\}'

        for match in re.finditer(alt_pattern, text):
            ability = match.group(1).lower()
            dc = int(match.group(2))
            condition_name = match.group(3).lower()

            condition_type = self._map_condition_name(condition_name)
            if condition_type:
                saving_throw = SavingThrow(
                    dc=dc,
                    ability=ability,
                    condition_on_failure=condition_type,
                    duration_type="save_ends" if condition_name != "prone" else "instant",
                    save_frequency="end_of_turn"
                )

                effects.append(AttackEffect(
                    effect_type="condition",
                    condition=condition_type,
                    saving_throw=saving_throw,
                    automatic=False,
                    description=f"{attack_name} save effect"
                ))

        return effects

    def _extract_automatic_conditions(self, text: str) -> List[AttackEffect]:
        """Extract conditions applied automatically on hit."""
        effects = []

        # Pattern: "target is {@condition [condition]}"
        auto_pattern = r'target is \{@condition ([^}]+)\}'

        for match in re.finditer(auto_pattern, text):
            condition_name = match.group(1).lower()
            condition_type = self._map_condition_name(condition_name)

            if condition_type:
                effects.append(AttackEffect(
                    effect_type="condition",
                    condition=condition_type,
                    automatic=True,
                    description=f"Automatic {condition_name} on hit"
                ))

        # Pattern: "be knocked {@condition prone}"
        prone_pattern = r'knocked \{@condition prone\}'
        if re.search(prone_pattern, text):
            effects.append(AttackEffect(
                effect_type="condition",
                condition=ConditionType.PRONE,
                automatic=True,
                description="Knocked prone on hit"
            ))

        return effects

    def _extract_poison_effects(self, text: str) -> List[AttackEffect]:
        """Extract poison damage with potential condition effects."""
        effects = []

        # Pattern for poison that causes conditions on 0 HP
        poison_pattern = r'if the poison damage reduces the target to 0 hit points.*\{@condition ([^}]+)\}'

        for match in re.finditer(poison_pattern, text):
            condition_name = match.group(1).lower()
            condition_type = self._map_condition_name(condition_name)

            if condition_type:
                effects.append(AttackEffect(
                    effect_type="condition",
                    condition=condition_type,
                    automatic=False,  # Only if reduced to 0 HP
                    description=f"Poison causes {condition_name} if reduced to 0 HP"
                ))

        return effects

    def _map_condition_name(self, condition_name: str) -> Optional[ConditionType]:
        """Map condition name strings to ConditionType enum."""
        if not ConditionType:
            return None

        condition_map = {
            'blinded': ConditionType.BLINDED,
            'charmed': ConditionType.CHARMED,
            'deafened': ConditionType.DEAFENED,
            'exhaustion': ConditionType.EXHAUSTION,
            'frightened': ConditionType.FRIGHTENED,
            'grappled': ConditionType.GRAPPLED,
            'incapacitated': ConditionType.INCAPACITATED,
            'invisible': ConditionType.INVISIBLE,
            'paralyzed': ConditionType.PARALYZED,
            'petrified': ConditionType.PETRIFIED,
            'poisoned': ConditionType.POISONED,
            'prone': ConditionType.PRONE,
            'restrained': ConditionType.RESTRAINED,
            'stunned': ConditionType.STUNNED,
            'unconscious': ConditionType.UNCONSCIOUS
        }

        return condition_map.get(condition_name.lower())

    def execute_monster_attack(self, attack: MonsterAttack, target_character_id: str,
                             attack_roll: int, target_ac: int) -> Dict[str, Any]:
        """Execute a monster attack against a character."""
        result = {
            'attack_result': AttackResult.MISS,
            'damage_dealt': 0,
            'conditions_applied': [],
            'saving_throws_required': [],
            'messages': []
        }

        # Determine if attack hits
        total_attack = attack_roll + attack.attack_bonus

        if attack_roll == 20:
            result['attack_result'] = AttackResult.CRITICAL_HIT
        elif total_attack >= target_ac:
            result['attack_result'] = AttackResult.HIT
        else:
            result['attack_result'] = AttackResult.MISS
            result['messages'].append(f"{attack.name} misses! (rolled {attack_roll}+{attack.attack_bonus}={total_attack} vs AC {target_ac})")
            return result

        # Attack hits - calculate damage
        damage_multiplier = 2 if result['attack_result'] == AttackResult.CRITICAL_HIT else 1
        damage = attack.base_damage * damage_multiplier
        result['damage_dealt'] = damage

        hit_type = "critically hits" if result['attack_result'] == AttackResult.CRITICAL_HIT else "hits"
        result['messages'].append(f"{attack.name} {hit_type}! ({attack_roll}+{attack.attack_bonus}={total_attack} vs AC {target_ac})")
        result['messages'].append(f"Deals {damage} {attack.damage_type} damage")

        # Process attack effects
        for effect in attack.effects:
            if effect.effect_type == "condition":
                self._process_condition_effect(effect, target_character_id, result)

        return result

    def _process_condition_effect(self, effect: AttackEffect, character_id: str, result: Dict[str, Any]):
        """Process a condition effect from an attack."""
        if not self.condition_manager or not effect.condition:
            return

        if effect.automatic:
            # Apply condition automatically
            condition = ActiveCondition(
                condition_type=effect.condition,
                source=f"Monster Attack: {effect.description}",
                duration_type="instant" if effect.condition == ConditionType.PRONE else "permanent"
            )

            if self.condition_manager.add_condition(character_id, condition):
                result['conditions_applied'].append(effect.condition.value)
                result['messages'].append(f"Applied {effect.condition.value}!")

                # Special handling for prone
                if effect.condition == ConditionType.PRONE:
                    result['messages'].append("You can spend half your movement to stand up")

        elif effect.saving_throw:
            # Require saving throw
            save = effect.saving_throw
            result['saving_throws_required'].append({
                'dc': save.dc,
                'ability': save.ability,
                'condition': effect.condition.value,
                'save_frequency': save.save_frequency,
                'duration_type': save.duration_type
            })
            result['messages'].append(f"Make a DC {save.dc} {save.ability.title()} saving throw or be {effect.condition.value}!")

    def apply_saving_throw_result(self, character_id: str, save_data: Dict[str, Any],
                                roll_result: int, success: bool) -> List[str]:
        """Apply the result of a saving throw."""
        messages = []

        if not self.condition_manager:
            return ["Condition system not available"]

        if success:
            messages.append(f"Saving throw successful! (rolled {roll_result} vs DC {save_data['dc']})")
        else:
            messages.append(f"Saving throw failed! (rolled {roll_result} vs DC {save_data['dc']})")

            # Apply condition
            condition_type = ConditionType(save_data['condition'])
            condition = ActiveCondition(
                condition_type=condition_type,
                source=f"Failed save (DC {save_data['dc']})",
                duration_type=save_data.get('duration_type', 'save_ends'),
                save_dc=save_data['dc'],
                save_ability=save_data['ability'],
                save_frequency=save_data.get('save_frequency', 'end_of_turn')
            )

            if self.condition_manager.add_condition(character_id, condition):
                messages.append(f"Applied {condition_type.value}!")

                # Condition-specific messages
                if condition_type == ConditionType.PRONE:
                    messages.append("You are knocked prone. Spend half your movement to stand up.")
                elif condition_type == ConditionType.GRAPPLED:
                    messages.append("You are grappled. Use an action to make a Strength (Athletics) or Dexterity (Acrobatics) check to escape.")
                elif condition_type == ConditionType.PARALYZED:
                    messages.append("You are paralyzed! You cannot move or act.")
                elif condition_type == ConditionType.POISONED:
                    messages.append("You are poisoned! Disadvantage on attack rolls and ability checks.")

        return messages


# Singleton instance
monster_attack_processor = MonsterAttackProcessor()