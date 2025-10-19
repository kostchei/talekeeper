# core
# category: utility
"""
Monster Attack Parser - Phase 1

Parses monster attack JSON entries from the database and extracts structured
attack data including conditions, saving throws, and special effects.

Follows the design document in docs/monster_attack_conditions.md
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from talekeeper.services.condition_manager import ConditionType
except ImportError:
    ConditionType = None


@dataclass
class AttackEffect:
    """Represents a special effect from a monster attack."""
    effect_type: str  # "condition", "save_damage", "automatic_condition", "conditional_condition"
    condition: Optional[str] = None  # Condition name as string
    save_dc: Optional[int] = None
    save_ability: Optional[str] = None  # "constitution", "dexterity", etc.
    damage_on_fail: Optional[str] = None  # Damage dice if save fails
    damage_on_success: Optional[str] = None  # Damage dice if save succeeds
    trigger: Optional[str] = None  # Special trigger for conditional effects
    duration: Optional[str] = None  # Duration description
    automatic: bool = False  # Applied automatically on hit
    description: str = ""  # Human-readable description


@dataclass
class ParsedAttack:
    """Structured representation of a monster attack."""
    name: str
    attack_type: str  # "melee", "ranged", "special"
    attack_bonus: int
    reach: int  # In feet
    range_normal: Optional[int] = None  # For ranged attacks
    range_long: Optional[int] = None  # For ranged attacks
    damage_dice: str = ""  # Primary damage dice (e.g., "1d8+3")
    damage_type: str = ""  # Primary damage type
    additional_damage: List[Tuple[str, str]] = None  # [(dice, type), ...] for poison, etc.
    effects: List[AttackEffect] = None  # Special effects
    raw_text: str = ""  # Original attack description

    def __post_init__(self):
        if self.additional_damage is None:
            self.additional_damage = []
        if self.effects is None:
            self.effects = []


class MonsterAttackParser:
    """Parses monster attacks from database JSON format."""

    # Regex patterns for D&D attack format
    ATTACK_PATTERNS = {
        'attack_bonus': r'\{@hit (\d+)\}',
        'damage': r'\{@damage ([^}]+)\}',
        'hit_damage': r'\{@h\}(\d+) \(\{@damage ([^}]+)\}\)',
        'save_dc': r'\{@dc (\d+)\}',
        'condition': r'\{@condition ([^}]+)\}',
        'reach': r'reach (\d+) ft',
        'range': r'range (\d+)/(\d+) ft',
        'range_single': r'range (\d+) ft',
        'melee_attack': r'\{@atk mw\}',
        'ranged_attack': r'\{@atk rw\}',
    }

    # Condition name mappings (database format -> our format)
    CONDITION_MAPPINGS = {
        'blinded': 'blinded',
        'charmed': 'charmed',
        'deafened': 'deafened',
        'exhaustion': 'exhaustion',
        'frightened': 'frightened',
        'grappled': 'grappled',
        'incapacitated': 'incapacitated',
        'invisible': 'invisible',
        'paralyzed': 'paralyzed',
        'petrified': 'petrified',
        'poisoned': 'poisoned',
        'prone': 'prone',
        'restrained': 'restrained',
        'stunned': 'stunned',
        'unconscious': 'unconscious'
    }

    def parse_monster_actions(self, actions_json: str) -> List[ParsedAttack]:
        """
        Parse monster actions from database JSON.

        Args:
            actions_json: JSON string from monster's actions field

        Returns:
            List of ParsedAttack objects
        """
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
            print(f"[MonsterAttackParser] Error parsing actions: {e}")
            return []

    def _is_attack_action(self, action: Dict[str, Any]) -> bool:
        """Check if an action represents an attack."""
        entries = action.get('entries', [])
        if not entries:
            return False

        # Convert entries to string for analysis
        text = self._entries_to_text(entries)

        # Look for attack indicators
        attack_indicators = [
            '{@atk mw}', '{@atk rw}',  # Melee/ranged attack tags
            'Melee Attack', 'Ranged Attack',  # Plain text indicators
            '@hit', 'to hit',  # Attack roll indicators
            '{@damage', 'damage'  # Damage indicators
        ]

        return any(indicator.lower() in text.lower() for indicator in attack_indicators)

    def _parse_attack_action(self, action: Dict[str, Any]) -> Optional[ParsedAttack]:
        """Parse a single attack action into structured data."""
        name = action.get('name', 'Unknown Attack')
        entries = action.get('entries', [])

        if not entries:
            return None

        # Convert entries to full text
        full_text = self._entries_to_text(entries)

        # Create base attack structure
        attack = ParsedAttack(
            name=name,
            attack_type=self._determine_attack_type(full_text),
            attack_bonus=self._extract_attack_bonus(full_text),
            reach=self._extract_reach(full_text),
            raw_text=full_text
        )

        # Extract range for ranged attacks
        if attack.attack_type == "ranged":
            attack.range_normal, attack.range_long = self._extract_range(full_text)

        # Extract damage information
        attack.damage_dice, attack.damage_type = self._extract_primary_damage(full_text)
        attack.additional_damage = self._extract_additional_damage(full_text)

        # Extract special effects
        attack.effects = self._extract_effects(full_text, name)

        return attack

    def _entries_to_text(self, entries: List[Any]) -> str:
        """Convert entries list to plain text."""
        if isinstance(entries, str):
            return entries

        text_parts = []
        for entry in entries:
            if isinstance(entry, str):
                text_parts.append(entry)
            elif isinstance(entry, dict):
                # Handle nested structures like lists, tables
                if 'entries' in entry:
                    text_parts.append(self._entries_to_text(entry['entries']))
                else:
                    text_parts.append(str(entry))
            else:
                text_parts.append(str(entry))

        return ' '.join(text_parts)

    def _determine_attack_type(self, text: str) -> str:
        """Determine if attack is melee, ranged, or special."""
        if re.search(self.ATTACK_PATTERNS['melee_attack'], text):
            return "melee"
        elif re.search(self.ATTACK_PATTERNS['ranged_attack'], text):
            return "ranged"
        elif 'melee' in text.lower():
            return "melee"
        elif 'ranged' in text.lower():
            return "ranged"
        else:
            return "special"

    def _extract_attack_bonus(self, text: str) -> int:
        """Extract attack bonus from text."""
        # Try {@hit X} pattern first
        match = re.search(self.ATTACK_PATTERNS['attack_bonus'], text)
        if match:
            return int(match.group(1))

        # Try "+X to hit" pattern
        match = re.search(r'\+(\d+) to hit', text)
        if match:
            return int(match.group(1))

        # Try "Attack Roll: +X" pattern (D&D 2024 format)
        match = re.search(r'Attack Roll:\s*\+(\d+)', text)
        if match:
            return int(match.group(1))

        return 0

    def _extract_reach(self, text: str) -> int:
        """Extract reach in feet."""
        match = re.search(self.ATTACK_PATTERNS['reach'], text)
        if match:
            return int(match.group(1))
        return 5  # Default melee reach

    def _extract_range(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract normal/long range for ranged attacks."""
        # Try "range X/Y ft" pattern
        match = re.search(self.ATTACK_PATTERNS['range'], text)
        if match:
            return int(match.group(1)), int(match.group(2))

        # Try "range X ft" pattern (no long range)
        match = re.search(self.ATTACK_PATTERNS['range_single'], text)
        if match:
            return int(match.group(1)), None

        return None, None

    def _extract_primary_damage(self, text: str) -> Tuple[str, str]:
        """Extract primary damage dice and type."""
        # Try {@h}X ({@damage Y}) type pattern
        match = re.search(self.ATTACK_PATTERNS['hit_damage'], text)
        if match:
            average_dmg = match.group(1)
            dice_expr = match.group(2)

            # Extract damage type after the closing parenthesis
            pos = match.end()
            remaining = text[pos:].strip()

            # Look for damage type word
            type_match = re.match(r'\s*(\w+)', remaining)
            damage_type = type_match.group(1) if type_match else "bludgeoning"

            return dice_expr, damage_type.lower()

        # Try simpler X (YdZ + A) type damage pattern
        match = re.search(r'(\d+) \(([^)]+)\) (\w+) damage', text)
        if match:
            dice_expr = match.group(2)
            damage_type = match.group(3)
            return dice_expr, damage_type.lower()

        return "1d4", "bludgeoning"

    def _extract_additional_damage(self, text: str) -> List[Tuple[str, str]]:
        """Extract additional damage (like poison) beyond primary damage."""
        additional = []

        # Look for "plus X ({@damage YdZ}) type damage" patterns first (more specific)
        plus_pattern = r'plus \d+ \(\{@damage ([^}]+)\}\) (\w+) damage'
        matches_found = set()

        for match in re.finditer(plus_pattern, text):
            dice_expr = match.group(1)
            damage_type = match.group(2).lower()
            additional.append((dice_expr, damage_type))
            # Track what we found to avoid duplicates
            matches_found.add((match.start(), match.end()))

        # Look for simpler "plus X (YdZ) type damage" patterns (less specific)
        simple_plus_pattern = r'plus \d+ \(([^)]+)\) (\w+) damage'
        for match in re.finditer(simple_plus_pattern, text):
            # Skip if this match overlaps with a previous match
            if any(match.start() >= start and match.end() <= end for start, end in matches_found):
                continue

            dice_expr = match.group(1)
            damage_type = match.group(2).lower()

            # Clean up any remaining {@damage } tags
            dice_expr = re.sub(r'\{@damage ([^}]+)\}', r'\1', dice_expr)

            additional.append((dice_expr, damage_type))

        return additional

    def _extract_effects(self, text: str, attack_name: str) -> List[AttackEffect]:
        """Extract special effects from attack text."""
        effects = []

        # Extract save-based effects
        effects.extend(self._extract_save_effects(text, attack_name))

        # Extract automatic conditions (applied on hit)
        effects.extend(self._extract_automatic_conditions(text, attack_name))

        # Extract conditional effects (special triggers)
        effects.extend(self._extract_conditional_effects(text, attack_name))

        return effects

    def _extract_save_effects(self, text: str, attack_name: str) -> List[AttackEffect]:
        """Extract effects that require saving throws."""
        effects = []

        # Pattern: "must make/succeed on a DC X [ability] saving throw or be [condition]"
        save_condition_pattern = r'must (?:make|succeed on) a \{@dc (\d+)\} (\w+) saving throw or be \{@condition ([^}]+)\}'

        for match in re.finditer(save_condition_pattern, text):
            dc = int(match.group(1))
            ability = match.group(2).lower()
            condition = match.group(3).lower()

            # Map to our condition format
            mapped_condition = self.CONDITION_MAPPINGS.get(condition, condition)

            effects.append(AttackEffect(
                effect_type="save_condition",
                condition=mapped_condition,
                save_dc=dc,
                save_ability=ability,
                description=f"{attack_name}: DC {dc} {ability} save or {condition}"
            ))

        # Pattern: "must succeed on a DC X [ability] saving throw, taking Y damage on failed save"
        save_damage_pattern = r'must make a \{@dc (\d+)\} (\w+) saving throw, taking (\d+) \(\{@damage ([^}]+)\}\) (\w+) damage on a failed save, or half as much damage on a successful one'

        for match in re.finditer(save_damage_pattern, text):
            dc = int(match.group(1))
            ability = match.group(2).lower()
            damage_dice = match.group(4)
            damage_type = match.group(5).lower()

            effects.append(AttackEffect(
                effect_type="save_damage",
                save_dc=dc,
                save_ability=ability,
                damage_on_fail=damage_dice,
                damage_on_success=f"half of {damage_dice}",
                description=f"{attack_name}: DC {dc} {ability} save or take {damage_dice} {damage_type} damage"
            ))

        # Alternative DC format: "Dexterity Saving Throw: DC X"
        alt_save_pattern = r'(\w+) Saving Throw:\s*DC (\d+)[^.]*Failure:[^{]*\{@condition ([^}]+)\}'

        for match in re.finditer(alt_save_pattern, text):
            ability = match.group(1).lower()
            dc = int(match.group(2))
            condition = match.group(3).lower()

            mapped_condition = self.CONDITION_MAPPINGS.get(condition, condition)

            effects.append(AttackEffect(
                effect_type="save_condition",
                condition=mapped_condition,
                save_dc=dc,
                save_ability=ability,
                description=f"{attack_name}: DC {dc} {ability} save or {condition}"
            ))

        return effects

    def _extract_automatic_conditions(self, text: str, attack_name: str) -> List[AttackEffect]:
        """Extract conditions applied automatically on hit (no save required)."""
        effects = []

        # Pattern: "target is {@condition [condition]}" (direct application)
        auto_pattern = r'target is \{@condition ([^}]+)\}'

        for match in re.finditer(auto_pattern, text, re.IGNORECASE):
            condition = match.group(1).lower()
            mapped_condition = self.CONDITION_MAPPINGS.get(condition, condition)

            effects.append(AttackEffect(
                effect_type="automatic_condition",
                condition=mapped_condition,
                automatic=True,
                description=f"{attack_name}: automatic {condition} on hit"
            ))

        # Pattern: "be knocked {@condition prone}" (trample, charge attacks)
        knocked_prone_pattern = r'knocked \{@condition prone\}'
        if re.search(knocked_prone_pattern, text):
            effects.append(AttackEffect(
                effect_type="automatic_condition",
                condition="prone",
                automatic=True,
                description=f"{attack_name}: knocked prone on hit"
            ))

        # Pattern: "is {@condition grappled} (escape DC X)" (automatic grapple)
        grapple_pattern = r'is \{@condition grappled\} \(escape \{@dc (\d+)\}\)'
        match = re.search(grapple_pattern, text)
        if match:
            escape_dc = int(match.group(1))
            effects.append(AttackEffect(
                effect_type="automatic_condition",
                condition="grappled",
                automatic=True,
                save_dc=escape_dc,  # Store escape DC for later use
                description=f"{attack_name}: grappled on hit (escape DC {escape_dc})"
            ))

        # Pattern: "If the target is [size], it is {@condition [condition]}" (conditional automatic)
        conditional_auto_pattern = r'If the target is a (\w+)(?: or smaller)? creature, it is \{@condition ([^}]+)\}'
        for match in re.finditer(conditional_auto_pattern, text):
            size_limit = match.group(1).lower()
            condition = match.group(2).lower()
            mapped_condition = self.CONDITION_MAPPINGS.get(condition, condition)

            effects.append(AttackEffect(
                effect_type="conditional_automatic",
                condition=mapped_condition,
                automatic=True,
                trigger=f"target_size_{size_limit}_or_smaller",
                description=f"{attack_name}: {condition} if target is {size_limit} or smaller"
            ))

        # Pattern: "creature must succeed on... or be knocked {@condition prone}" (trample with save)
        trample_save_pattern = r'creature must succeed on[^{]*or be knocked \{@condition prone\}'
        if re.search(trample_save_pattern, text):
            # This will be caught by save patterns, but mark it as a trample effect
            pass

        # Pattern for direct size-based effects: "If the target is Medium or smaller, it has the {@condition grappled} condition"
        size_grapple_pattern = r'If the target is a (\w+)(?: or smaller)? creature, it has the \{@condition grappled\} condition'
        match = re.search(size_grapple_pattern, text)
        if match:
            size_limit = match.group(1).lower()
            effects.append(AttackEffect(
                effect_type="conditional_automatic",
                condition="grappled",
                automatic=True,
                trigger=f"target_size_{size_limit}_or_smaller",
                description=f"{attack_name}: grappled if target is {size_limit} or smaller"
            ))

        return effects

    def _extract_conditional_effects(self, text: str, attack_name: str) -> List[AttackEffect]:
        """Extract effects with special triggers."""
        effects = []

        # Pattern: "If the poison damage reduces the target to 0 hit points, the target is ... {@condition [condition]}"
        zero_hp_pattern = r'if the poison damage reduces the target to 0 hit points[^{]*\{@condition ([^}]+)\}'

        for match in re.finditer(zero_hp_pattern, text, re.IGNORECASE):
            condition = match.group(1).lower()
            mapped_condition = self.CONDITION_MAPPINGS.get(condition, condition)

            effects.append(AttackEffect(
                effect_type="conditional_condition",
                condition=mapped_condition,
                trigger="reduced_to_0_hp_by_poison",
                description=f"{attack_name}: {condition} if reduced to 0 HP by poison"
            ))

        # Pattern: duration specifications
        duration_pattern = r'for (\d+) (minute|hour|day)s?'
        matches = list(re.finditer(duration_pattern, text))
        if matches and effects:
            # Apply duration to the last effect (assumption: duration applies to preceding condition)
            last_effect = effects[-1]
            duration_match = matches[-1]
            duration = f"{duration_match.group(1)} {duration_match.group(2)}{'s' if int(duration_match.group(1)) > 1 else ''}"
            last_effect.duration = duration

        return effects

    def get_attack_summary(self, attack: ParsedAttack) -> str:
        """Get a human-readable summary of the attack."""
        summary = f"{attack.name} ({attack.attack_type}): "
        summary += f"+{attack.attack_bonus} to hit, "

        if attack.attack_type == "melee":
            summary += f"reach {attack.reach} ft"
        elif attack.attack_type == "ranged":
            if attack.range_long:
                summary += f"range {attack.range_normal}/{attack.range_long} ft"
            else:
                summary += f"range {attack.range_normal} ft"

        summary += f". Damage: {attack.damage_dice} {attack.damage_type}"

        if attack.additional_damage:
            for dice, dmg_type in attack.additional_damage:
                summary += f" + {dice} {dmg_type}"

        if attack.effects:
            summary += f". Effects: {len(attack.effects)} special effects"

        return summary


# Singleton instance for easy access
monster_attack_parser = MonsterAttackParser()