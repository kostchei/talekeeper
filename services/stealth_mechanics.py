"""
Stealth Mechanics Service for TaleKeeper

Handles stealth mechanics for encounters:
- Pre-encounter stealth checks
- Hidden state management
- Monster perception checks
- Advantage/disadvantage from equipment
- Integration with combat system
"""

import sqlite3
import random
from typing import Dict, List, Any, Optional, Tuple
from services.proficiency_system import ProficiencySystem
from services.proficiency_bonus import get_proficiency_bonus
from services.advantage_system import advantage_system, RollType, AdvantageState


class StealthMechanicsService:
    """Service for managing stealth mechanics during encounters."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.proficiency_system = ProficiencySystem(db_path)
        self.STEALTH_DC = 15  # Base DC for stealth checks

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def check_stealth_proficiency(self, character_id: str) -> bool:
        """Check if character has stealth proficiency."""
        proficiencies = self.proficiency_system.get_character_proficiencies(character_id)
        skills = proficiencies.get('skill', [])
        # Normalize skill names for comparison
        normalized_skills = [s.lower().replace(' ', '').replace('_', '') for s in skills]
        return 'stealth' in normalized_skills or 'Stealth' in skills

    def get_stealth_modifiers(self, character_id: str) -> Dict[str, Any]:
        """
        Get stealth roll modifiers from equipment.

        Returns:
            Dict with 'advantage', 'disadvantage', and 'modifier' values
        """
        modifiers = {
            'advantage': False,
            'disadvantage': False,
            'modifier': 0,
            'sources': []
        }

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check equipped armor for disadvantage using character_inventory and equipment tables
            cursor.execute("""
                SELECT e.name, e.armor_type, e.stealth_disadvantage
                FROM character_inventory ci
                JOIN equipment e ON ci.item_name = e.name
                WHERE ci.character_id = ? AND ci.equipped = 1
                AND e.item_type = 'armor'
            """, (character_id,))

            armor = cursor.fetchone()
            if armor:
                armor_name = armor['name'].lower()

                # Check stealth_disadvantage flag or armor type
                if armor['stealth_disadvantage'] or armor['armor_type'] == 'heavy':
                    # Check if it's mithral (no disadvantage)
                    if 'mithral' not in armor_name:
                        modifiers['disadvantage'] = True
                        modifiers['sources'].append(f"Disadvantage from {armor['name']}")

            # Check for items that give advantage (cloaks, etc.)
            cursor.execute("""
                SELECT e.name, e.description
                FROM character_inventory ci
                JOIN equipment e ON ci.item_name = e.name
                WHERE ci.character_id = ? AND ci.equipped = 1
                AND (LOWER(e.name) LIKE '%elven%cloak%' OR LOWER(e.name) LIKE '%cloak%elven%'
                     OR LOWER(e.description) LIKE '%stealth%advantage%')
            """, (character_id,))

            cloaks = cursor.fetchall()
            for cloak in cloaks:
                modifiers['advantage'] = True
                modifiers['sources'].append(f"Advantage from {cloak['name']}")

            # Check character abilities and features
            cursor.execute("""
                SELECT dexterity, level, class_id, subclass_id
                FROM characters
                WHERE id = ?
            """, (character_id,))

            char = cursor.fetchone()
            if char:
                # Add DEX modifier
                dex_mod = (char['dexterity'] - 10) // 2
                modifiers['modifier'] += dex_mod

                # Check for Pass Without Trace spell effect (would need to track active spells)
                # This is a placeholder for future spell system integration

        return modifiers

    def perform_stealth_check(self, character_id: str, character_level: int) -> Dict[str, Any]:
        """
        Perform a stealth check for encounter initialization.

        Returns:
            Dict with 'success', 'roll', 'total', 'dc_to_spot', and 'breakdown'
        """
        # Check if character has stealth proficiency
        has_proficiency = self.check_stealth_proficiency(character_id)
        if not has_proficiency:
            return {
                'success': False,
                'reason': 'no_proficiency',
                'message': 'Character lacks Stealth proficiency'
            }

        # Get modifiers from equipment and abilities
        modifiers = self.get_stealth_modifiers(character_id)

        # Calculate proficiency bonus
        prof_bonus = get_proficiency_bonus(character_level)

        # Determine roll type based on advantage/disadvantage
        roll_type = AdvantageState.NORMAL
        if modifiers['advantage'] and not modifiers['disadvantage']:
            roll_type = AdvantageState.ADVANTAGE
        elif modifiers['disadvantage'] and not modifiers['advantage']:
            roll_type = AdvantageState.DISADVANTAGE

        # Make the stealth roll
        base_roll, roll_breakdown = advantage_system.roll_d20_with_advantage(roll_type, 0)  # 0 modifier since we add it separately

        # Calculate total
        total = base_roll + modifiers['modifier'] + prof_bonus

        # Check success against DC 15
        success = total >= self.STEALTH_DC

        # If successful, the DC to spot is the roll total
        dc_to_spot = total if success else 0

        breakdown = {
            'base_roll': base_roll,
            'dex_modifier': modifiers['modifier'],
            'proficiency_bonus': prof_bonus,
            'roll_type': roll_type.value,
            'sources': modifiers['sources'],
            'rolls': roll_breakdown.get('rolls', [base_roll]),
            'roll_description': roll_breakdown.get('description', f'd20({base_roll})')
        }

        return {
            'success': success,
            'roll': base_roll,
            'total': total,
            'dc_to_spot': dc_to_spot,
            'breakdown': breakdown
        }

    def check_monster_perception(self, monster_data: Dict[str, Any], stealth_dc: int) -> Dict[str, Any]:
        """
        Check if a monster spots the hidden character.

        Args:
            monster_data: Monster stats including perception bonus
            stealth_dc: The DC the monster needs to beat to spot the character

        Returns:
            Dict with 'spotted', 'roll', 'total', and 'breakdown'
        """
        # Get monster's perception bonus
        perception_bonus = 0
        skills = monster_data.get('skills', {})

        # Parse skills if it's a string
        if isinstance(skills, str):
            import json
            try:
                skills = json.loads(skills) if skills else {}
            except:
                # Try to parse manual format like "Perception +5"
                if 'Perception' in skills:
                    parts = skills.split('Perception')
                    if len(parts) > 1:
                        try:
                            perception_bonus = int(parts[1].strip().replace('+', '').split(',')[0].split()[0])
                        except:
                            pass
                skills = {}

        if isinstance(skills, dict):
            perception_bonus = skills.get('Perception', 0)

        # If no perception skill, use Wisdom modifier
        if perception_bonus == 0:
            wis = monster_data.get('wisdom', 10)
            perception_bonus = (wis - 10) // 2

        # Roll perception check
        roll = random.randint(1, 20)
        total = roll + perception_bonus

        # Check if monster spots the character
        spotted = total >= stealth_dc

        return {
            'spotted': spotted,
            'roll': roll,
            'total': total,
            'perception_bonus': perception_bonus,
            'breakdown': {
                'base_roll': roll,
                'perception_bonus': perception_bonus,
                'dc': stealth_dc
            }
        }

    def check_encounter_stealth(self, character_id: str, character_data: Dict[str, Any],
                                monsters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if character successfully hides at encounter start.

        Args:
            character_id: Character ID
            character_data: Character stats
            monsters: List of monster data

        Returns:
            Dict with overall success and detailed results
        """
        # Perform stealth check
        stealth_result = self.perform_stealth_check(
            character_id,
            character_data.get('level', 1)
        )

        if not stealth_result.get('success', False):
            return {
                'hidden': False,
                'reason': stealth_result.get('reason', 'failed_stealth'),
                'stealth_result': stealth_result,
                'monster_results': []
            }

        # Check each monster's perception
        dc_to_spot = stealth_result['dc_to_spot']
        monster_results = []
        any_spotted = False

        for monster in monsters:
            perception_result = self.check_monster_perception(monster, dc_to_spot)
            monster_results.append({
                'monster': monster.get('name', 'Unknown'),
                'perception_check': perception_result
            })
            if perception_result['spotted']:
                any_spotted = True

        return {
            'hidden': not any_spotted,
            'reason': 'spotted_by_monster' if any_spotted else 'successful_stealth',
            'stealth_result': stealth_result,
            'monster_results': monster_results
        }

    def apply_hidden_attack_bonuses(self, attack_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply bonuses for attacking from hidden.

        Args:
            attack_context: Current attack context

        Returns:
            Modified attack context with hidden bonuses
        """
        if attack_context.get('is_hidden', False):
            # Attacking from hidden grants advantage
            attack_context['has_advantage'] = True
            attack_context['advantage_source'] = 'attacking_from_hidden'

            # Ensure sneak attack is eligible
            attack_context['sneak_attack_eligible'] = True
            attack_context['sneak_attack_source'] = 'hidden'

            # Check for D&D 2024 assassin features
            subclass = attack_context.get('subclass', '')
            level = attack_context.get('level', 1)
            current_round = attack_context.get('current_round', 1)

            if subclass and 'assassin' in subclass.lower():
                # Assassinate feature at level 3 (D&D 2024)
                if level >= 3:
                    # Initiative advantage (handled elsewhere)
                    attack_context['assassin_init_advantage'] = True

                    # Surprising Strikes - first round only
                    if current_round == 1:
                        attack_context['surprising_strikes'] = True
                        attack_context['surprising_strikes_damage'] = level  # Rogue level in extra damage
                        # Target that hasn't taken a turn gets advantage on attack
                        if attack_context.get('target_hasnt_acted', False):
                            attack_context['has_advantage'] = True
                            attack_context['advantage_source'] = 'assassinate_first_round'

                # Death Strike at level 17 (D&D 2024)
                if level >= 17 and current_round == 1:
                    attack_context['death_strike'] = True
                    # Calculate save DC
                    dex_mod = attack_context.get('dex_modifier', 0)
                    prof_bonus = attack_context.get('proficiency_bonus', 2)
                    attack_context['death_strike_dc'] = 8 + dex_mod + prof_bonus

        return attack_context

    def end_hidden_state(self, character_id: str, reason: str = 'attacked') -> None:
        """
        End the hidden state for a character.

        Args:
            character_id: Character ID
            reason: Reason for ending hidden state
        """
        # This would typically update a combat state tracker
        # For now, we'll just return the reason
        print(f"[Stealth] Character {character_id} is no longer hidden: {reason}")