"""
Monster Knowledge Service

Implements D&D 5e-style knowledge checks for monsters.
Players can make skill checks to learn information about monsters they encounter.

DC = 10 + CR (e.g., CR 3 monster = DC 13)
Information revealed scales with how much they beat the DC.

Skill to Monster Type Mapping:
- Arcana: Aberration, Construct, Dragon, Elemental, Fey, Ooze
- Nature: Beast, Elemental, Fey, Monstrosity, Ooze, Plant
- Religion: Celestial, Fiend, Undead
- History: Dragon, Giant, Humanoid
- Insight: Giant, Humanoid
- Investigation: Construct
- Survival: Beast, Plant
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json


# Monster type to skill mapping
MONSTER_KNOWLEDGE_SKILLS: Dict[str, List[str]] = {
    'aberration': ['arcana'],
    'beast': ['nature', 'survival'],
    'celestial': ['religion'],
    'construct': ['arcana', 'investigation'],
    'dragon': ['arcana', 'history'],
    'elemental': ['arcana', 'nature'],
    'fey': ['arcana', 'nature'],
    'fiend': ['religion'],
    'giant': ['history', 'insight'],
    'humanoid': ['history', 'insight'],
    'monstrosity': ['nature'],
    'ooze': ['arcana', 'nature'],
    'plant': ['nature', 'survival'],
    'undead': ['religion']
}


@dataclass
class MonsterKnowledge:
    """Information revealed about a monster based on knowledge check."""
    dc: int
    success: bool
    margin: int  # How much the roll beat the DC
    revealed_info: List[Tuple[str, str]]  # (category, value) pairs


class MonsterKnowledgeService:
    """Service for handling monster knowledge checks and information reveals."""

    def __init__(self):
        """Initialize the monster knowledge service."""
        pass

    def get_applicable_skills(self, monster_type: str) -> List[str]:
        """
        Get list of skills that can be used to identify this monster type.

        Args:
            monster_type: The type of monster (e.g., 'dragon', 'undead')

        Returns:
            List of skill names that apply
        """
        monster_type_lower = monster_type.lower().strip()
        return MONSTER_KNOWLEDGE_SKILLS.get(monster_type_lower, [])

    def calculate_dc(self, challenge_rating: str) -> int:
        """
        Calculate the DC for a monster knowledge check.
        DC = 10 + CR

        Args:
            challenge_rating: CR as string (e.g., '3', '1/2', '1/4')

        Returns:
            The DC for the knowledge check
        """
        # Convert CR to numeric value
        cr_value = self._parse_cr(challenge_rating)

        # DC = 10 + CR
        dc = 10 + int(cr_value)

        return dc

    def _parse_cr(self, cr_string: str) -> float:
        """
        Parse CR string to numeric value.

        Args:
            cr_string: CR as string (e.g., '3', '1/2', '1/4')

        Returns:
            CR as float
        """
        cr_string = str(cr_string).strip()

        # Handle fractional CRs
        if '/' in cr_string:
            numerator, denominator = cr_string.split('/')
            return float(numerator) / float(denominator)

        try:
            return float(cr_string)
        except ValueError:
            return 0.0

    def check_knowledge(
        self,
        monster_data: Dict,
        skill_check_result: int,
        skill_used: str
    ) -> MonsterKnowledge:
        """
        Perform a monster knowledge check and determine what information is revealed.

        Information revealed by margin of success:
        - Success (0-1 over DC): Name + Type
        - +2 over DC: Add one additional property (vulnerability OR resistance)
        - +4 over DC: Add another property (AC OR HP)
        - +6 over DC: Add features or attacks
        - +8 over DC: Add all remaining basic stats

        Args:
            monster_data: Dictionary containing monster information
            skill_check_result: The total of the player's skill check
            skill_used: The skill they used (e.g., 'arcana', 'nature')

        Returns:
            MonsterKnowledge object with revealed information
        """
        cr = monster_data.get('challenge_rating', '0')
        dc = self.calculate_dc(cr)

        success = skill_check_result >= dc
        margin = skill_check_result - dc if success else 0

        revealed = []

        if success:
            # Always reveal name and type
            name = monster_data.get('name', 'Unknown')
            monster_type = monster_data.get('type', 'Unknown')
            size = monster_data.get('size', '')

            revealed.append(('Name', name))
            revealed.append(('Type', f"{size} {monster_type}".strip()))
            revealed.append(('CR', str(cr)))

            # +2 over DC: Add vulnerability or resistance
            if margin >= 2:
                vulns = self._parse_json_field(monster_data.get('damage_vulnerabilities'))
                resists = self._parse_json_field(monster_data.get('damage_resistances'))
                immunes = self._parse_json_field(monster_data.get('damage_immunities'))

                if vulns:
                    revealed.append(('Vulnerabilities', ', '.join(vulns)))
                if resists:
                    revealed.append(('Resistances', ', '.join(resists)))
                if immunes:
                    revealed.append(('Immunities', ', '.join(immunes)))

            # +4 over DC: Add AC or HP
            if margin >= 4:
                ac = monster_data.get('armor_class')
                hp = monster_data.get('hit_points')

                if ac:
                    revealed.append(('AC', str(ac)))
                if hp:
                    revealed.append(('HP', str(hp)))

            # +6 over DC: Add special abilities or attacks
            if margin >= 6:
                # Parse and summarize special abilities
                abilities = self._parse_special_abilities(monster_data.get('special_abilities'))
                if abilities:
                    revealed.append(('Special Abilities', abilities))

                # Parse and summarize attacks
                attacks = self._parse_attacks(monster_data.get('actions'))
                if attacks:
                    revealed.append(('Attacks', attacks))

            # +8 over DC: Add all remaining stats
            if margin >= 8:
                # Ability scores
                stats = []
                for stat in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                    value = monster_data.get(stat)
                    if value:
                        modifier = (value - 10) // 2
                        sign = '+' if modifier >= 0 else ''
                        stats.append(f"{stat[:3].upper()} {value} ({sign}{modifier})")

                if stats:
                    revealed.append(('Ability Scores', ', '.join(stats)))

                # Senses
                senses = monster_data.get('senses')
                if senses:
                    revealed.append(('Senses', senses))

                # Languages
                languages = monster_data.get('languages')
                if languages:
                    revealed.append(('Languages', languages))

                # Saving throws
                saves = monster_data.get('saving_throws')
                if saves:
                    revealed.append(('Saves', saves))

                # Skills
                skills = monster_data.get('skills')
                if skills:
                    revealed.append(('Skills', skills))

        return MonsterKnowledge(
            dc=dc,
            success=success,
            margin=margin,
            revealed_info=revealed
        )

    def _parse_json_field(self, field_value) -> List[str]:
        """Parse a JSON field that might be a string or already a list."""
        if not field_value:
            return []

        if isinstance(field_value, list):
            return field_value

        if isinstance(field_value, str):
            try:
                parsed = json.loads(field_value)
                if isinstance(parsed, list):
                    return parsed
                return [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                # Not JSON, treat as comma-separated string
                return [s.strip() for s in field_value.split(',') if s.strip()]

        return []

    def _parse_special_abilities(self, abilities_field) -> str:
        """Parse and summarize special abilities."""
        if not abilities_field:
            return ""

        try:
            if isinstance(abilities_field, str):
                abilities = json.loads(abilities_field)
            else:
                abilities = abilities_field

            if isinstance(abilities, list):
                # Extract ability names
                names = []
                for ability in abilities:
                    if isinstance(ability, dict):
                        name = ability.get('name', '')
                        if name:
                            names.append(name)
                    elif isinstance(ability, str):
                        names.append(ability)

                return ', '.join(names[:5])  # Limit to first 5

        except (json.JSONDecodeError, TypeError):
            pass

        return str(abilities_field)[:100] if abilities_field else ""

    def _parse_attacks(self, actions_field) -> str:
        """Parse and summarize attack actions."""
        if not actions_field:
            return ""

        try:
            if isinstance(actions_field, str):
                actions = json.loads(actions_field)
            else:
                actions = actions_field

            if isinstance(actions, list):
                # Extract attack names
                names = []
                for action in actions:
                    if isinstance(action, dict):
                        name = action.get('name', '')
                        if name:
                            names.append(name)
                    elif isinstance(action, str):
                        names.append(action)

                return ', '.join(names[:5])  # Limit to first 5

        except (json.JSONDecodeError, TypeError):
            pass

        return str(actions_field)[:100] if actions_field else ""

    def format_tooltip_html(self, knowledge: MonsterKnowledge, skill_used: str, roll_result: int) -> str:
        """
        Format monster knowledge as HTML for tooltip display.

        Args:
            knowledge: MonsterKnowledge object
            skill_used: The skill that was used
            roll_result: The dice roll result

        Returns:
            HTML string for tooltip
        """
        html = []

        # Header with check result
        html.append('<div style="padding: 8px; background-color: #2b2b2b; border-radius: 4px;">')

        if knowledge.success:
            html.append(f'<div style="color: #4CAF50; font-weight: bold; margin-bottom: 8px;">')
            html.append(f'{skill_used.title()} Check: {roll_result} vs DC {knowledge.dc} ✓')
            html.append(f'</div>')
        else:
            html.append(f'<div style="color: #f44336; font-weight: bold; margin-bottom: 8px;">')
            html.append(f'{skill_used.title()} Check: {roll_result} vs DC {knowledge.dc} ✗')
            html.append(f'</div>')
            html.append('<div style="color: #888;">Check failed - no information revealed</div>')
            html.append('</div>')
            return ''.join(html)

        # Revealed information
        for category, value in knowledge.revealed_info:
            if category == 'Name':
                html.append(f'<div style="font-size: 16px; font-weight: bold; color: #fff; margin-bottom: 4px;">')
                html.append(value)
                html.append('</div>')
            elif category in ['Type', 'CR']:
                html.append(f'<div style="color: #aaa; margin-bottom: 4px;">')
                html.append(f'{category}: {value}')
                html.append('</div>')
            else:
                html.append(f'<div style="margin-top: 8px;">')
                html.append(f'<span style="color: #64B5F6; font-weight: bold;">{category}:</span> ')
                html.append(f'<span style="color: #ddd;">{value}</span>')
                html.append('</div>')

        html.append('</div>')

        return ''.join(html)


# Singleton instance
monster_knowledge_service = MonsterKnowledgeService()
