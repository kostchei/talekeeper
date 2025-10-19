# core
# core
import sqlite3
import random
from typing import Dict, List, Optional, Tuple
from uuid import uuid4


class ParlaySystem:
    """
    System for diplomatic resolution of encounters with non-evil monsters.

    - 75% of non-evil monsters can be parlayed with
    - Uses CHA skill challenge: pick up to 3 CHA skills + 1 random INT/WIS skill
    - Reward: 1/2 XP from most powerful monster, no combat
    """

    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path

    def can_parlay_with_monster(self, monster: Dict) -> bool:
        """
        Determine if a monster can be parlayed with.

        Rules:
        - Evil alignment monsters cannot be parlayed with
        - 75% of non-evil monsters can be parlayed with
        """
        alignment = monster.get('alignment', '').lower()

        if not alignment:
            return False

        if 'evil' in alignment:
            return False

        return random.random() < 0.75

    def can_parlay_with_encounter(self, monsters: List[Dict]) -> Tuple[bool, str]:
        """
        Check if an encounter can be parlayed with.
        Returns (can_parlay, reason)
        """
        if not monsters:
            return False, "No monsters in encounter"

        all_evil = all('evil' in m.get('alignment', '').lower() for m in monsters)
        if all_evil:
            return False, "These creatures are too evil to negotiate with"

        any_non_evil = any('evil' not in m.get('alignment', '').lower() for m in monsters)
        if not any_non_evil:
            return False, "These creatures cannot be reasoned with"

        if random.random() < 0.75:
            return True, "These creatures might be willing to talk"
        else:
            return False, "These creatures seem hostile and unwilling to parlay"

    def get_parlay_skills(self) -> List[str]:
        """
        Get the skills available for parlay.

        Returns list of 4 skills:
        - 3 CHA skills
        - 1 random INT or WIS skill
        """
        cha_skills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']
        int_skills = ['Arcana', 'History', 'Investigation', 'Nature', 'Religion']
        wis_skills = ['Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival']

        selected_cha = random.sample(cha_skills, 3)

        int_or_wis = random.choice([*int_skills, *wis_skills])

        return selected_cha + [int_or_wis]

    def calculate_parlay_xp_reward(self, monsters: List[Dict]) -> int:
        """
        Calculate XP reward for successful parlay.

        Award 1/2 XP from the most powerful monster.
        """
        if not monsters:
            return 0

        max_xp = max(m.get('experience_points', 0) for m in monsters)
        return max_xp // 2

    def create_parlay_challenge(self, character_id: str, monsters: List[Dict]) -> Optional[str]:
        """
        Create a skill challenge for parlay attempt.

        Returns the template_id of the created challenge, or None if failed.
        """
        from services.skill_challenge_manager import SkillChallengeManager

        parlay_skills = self.get_parlay_skills()
        xp_reward = self.calculate_parlay_xp_reward(monsters)

        level = self._get_character_level(character_id)
        base_dc = 10 + level // 2

        template_id = str(uuid4())
        template_name = "Diplomatic Parlay"
        template_description = f"Attempt to negotiate peaceful passage with {', '.join(m.get('name', 'creature') for m in monsters[:3])}."

        success_reward = f"Peaceful resolution - gain {xp_reward} XP without combat"
        failure_penalty = "Negotiations break down - combat begins with disadvantage on initiative"
        refuse_cost = "Walk away cautiously - no XP, no combat"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO skill_challenge_templates
                (id, name, description, base_dc)
                VALUES (?, ?, ?, ?)
            ''', (template_id, template_name, template_description, base_dc))

            for idx, skill in enumerate(parlay_skills):
                cursor.execute('''
                    INSERT INTO skill_challenge_template_skills
                    (template_id, skill_name, skill_order)
                    VALUES (?, ?, ?)
                ''', (template_id, skill, idx))

            cursor.execute('''
                INSERT INTO skill_challenge_template_success
                (template_id, success_option)
                VALUES (?, ?)
            ''', (template_id, success_reward))

            cursor.execute('''
                INSERT INTO skill_challenge_template_failure
                (template_id, failure_option)
                VALUES (?, ?)
            ''', (template_id, failure_penalty))

            cursor.execute('''
                INSERT INTO skill_challenge_template_refuse
                (template_id, refuse_option)
                VALUES (?, ?)
            ''', (template_id, refuse_cost))

            conn.commit()

            manager = SkillChallengeManager(self.db_path)
            template = manager.get_template_by_id(template_id)
            if template:
                session = manager.create_session(character_id, template)
                return session.id

            return None

        except Exception as e:
            print(f"Error creating parlay challenge: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def _get_character_level(self, character_id: str) -> int:
        """Get character level from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT level FROM characters WHERE id = ?', (character_id,))
            result = cursor.fetchone()

            return result[0] if result else 1

        except Exception as e:
            print(f"Error getting character level: {e}")
            return 1
        finally:
            if conn:
                conn.close()

    def apply_parlay_success(self, character_id: str, xp_reward: int) -> Dict[str, any]:
        """
        Apply the rewards for successful parlay.

        Returns dict with:
        - xp_gained: amount of XP awarded
        - message: success message
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE characters
                SET experience_points = experience_points + ?
                WHERE id = ?
            ''', (xp_reward, character_id))

            conn.commit()

            return {
                'xp_gained': xp_reward,
                'message': f"Diplomatic success! Gained {xp_reward} XP through peaceful negotiation."
            }

        except Exception as e:
            print(f"Error applying parlay success: {e}")
            return {'xp_gained': 0, 'message': 'Error applying parlay rewards'}
        finally:
            if conn:
                conn.close()