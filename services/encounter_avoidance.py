# core
# core
import sqlite3
import random
from typing import Dict, List, Optional, Tuple
from services.stealth_mechanics import StealthMechanicsService
from services.proficiency_bonus import get_proficiency_bonus


class EncounterAvoidanceSystem:
    """
    System for avoiding encounters using Stealth checks.

    - Use Stealth check vs monster Perception
    - Success: Partial XP (1/3 of total), no combat
    - Failure: Combat begins normally
    """

    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        self.stealth_service = StealthMechanicsService(db_path)

    def can_attempt_avoidance(self, character_id: str, monsters: List[Dict]) -> Tuple[bool, str]:
        """
        Check if character can attempt to avoid this encounter.

        Returns (can_attempt, reason)
        """
        if not monsters:
            return False, "No monsters to avoid"

        has_stealth = self.stealth_service.check_stealth_proficiency(character_id)
        if not has_stealth:
            return False, "You need Stealth proficiency to attempt avoidance"

        return True, "You can attempt to sneak past these creatures"

    def attempt_avoidance(self, character_id: str, character_data: Dict,
                         monsters: List[Dict]) -> Dict[str, any]:
        """
        Attempt to avoid an encounter using Stealth.

        Returns dict with:
        - success: bool
        - stealth_total: int
        - highest_perception: int
        - xp_reward: int (if successful)
        - message: str
        - breakdown: detailed results
        """
        stealth_result = self.stealth_service.perform_stealth_check(
            character_id,
            character_data.get('level', 1)
        )

        if not stealth_result.get('success', False):
            return {
                'success': False,
                'stealth_total': stealth_result.get('total', 0),
                'highest_perception': 0,
                'xp_reward': 0,
                'message': f"Your stealth attempt failed ({stealth_result.get('total', 0)}) - the creatures notice your presence",
                'breakdown': stealth_result
            }

        stealth_dc = stealth_result['dc_to_spot']

        monster_perceptions = []
        highest_perception = 0
        spotted = False

        for monster in monsters:
            perception_result = self.stealth_service.check_monster_perception(
                monster, stealth_dc
            )
            monster_perceptions.append({
                'name': monster.get('name', 'Unknown'),
                'result': perception_result
            })

            if perception_result['spotted']:
                spotted = True

            if perception_result['total'] > highest_perception:
                highest_perception = perception_result['total']

        if spotted:
            return {
                'success': False,
                'stealth_total': stealth_result['total'],
                'highest_perception': highest_perception,
                'xp_reward': 0,
                'message': f"Despite your stealth ({stealth_result['total']}), the creatures spot you (Perception: {highest_perception})",
                'breakdown': {
                    'stealth_result': stealth_result,
                    'monster_perceptions': monster_perceptions
                }
            }

        xp_reward = self._calculate_avoidance_xp(monsters)

        self._award_xp(character_id, xp_reward)

        return {
            'success': True,
            'stealth_total': stealth_result['total'],
            'highest_perception': highest_perception,
            'xp_reward': xp_reward,
            'message': f"You successfully sneak past the creatures! Gained {xp_reward} XP for clever avoidance.",
            'breakdown': {
                'stealth_result': stealth_result,
                'monster_perceptions': monster_perceptions
            }
        }

    def _calculate_avoidance_xp(self, monsters: List[Dict]) -> int:
        """
        Calculate XP reward for avoiding encounter.

        Award 1/3 of total encounter XP.
        """
        total_xp = sum(m.get('experience_points', 0) for m in monsters)
        return total_xp // 3

    def _award_xp(self, character_id: str, xp_amount: int):
        """Award XP to character."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE characters
                SET experience_points = experience_points + ?
                WHERE id = ?
            ''', (xp_amount, character_id))

            conn.commit()

        except Exception as e:
            print(f"Error awarding XP: {e}")
        finally:
            if conn:
                conn.close()

    def get_encounter_difficulty(self, monsters: List[Dict], character_level: int) -> str:
        """
        Estimate encounter difficulty for avoidance context.

        Returns: 'trivial', 'easy', 'medium', 'hard', 'deadly'
        """
        total_xp = sum(m.get('experience_points', 0) for m in monsters)

        thresholds = self._get_xp_thresholds(character_level)

        if total_xp < thresholds['easy']:
            return 'trivial'
        elif total_xp < thresholds['medium']:
            return 'easy'
        elif total_xp < thresholds['hard']:
            return 'medium'
        elif total_xp < thresholds['deadly']:
            return 'hard'
        else:
            return 'deadly'

    def _get_xp_thresholds(self, level: int) -> Dict[str, int]:
        """Get XP thresholds for encounter difficulty by character level."""
        thresholds_table = {
            1: {'easy': 25, 'medium': 50, 'hard': 75, 'deadly': 100},
            2: {'easy': 50, 'medium': 100, 'hard': 150, 'deadly': 200},
            3: {'easy': 75, 'medium': 150, 'hard': 225, 'deadly': 400},
            4: {'easy': 125, 'medium': 250, 'hard': 375, 'deadly': 500},
            5: {'easy': 250, 'medium': 500, 'hard': 750, 'deadly': 1100},
            6: {'easy': 300, 'medium': 600, 'hard': 900, 'deadly': 1400},
            7: {'easy': 350, 'medium': 750, 'hard': 1100, 'deadly': 1700},
            8: {'easy': 450, 'medium': 900, 'hard': 1400, 'deadly': 2100},
            9: {'easy': 550, 'medium': 1100, 'hard': 1600, 'deadly': 2400},
            10: {'easy': 600, 'medium': 1200, 'hard': 1900, 'deadly': 2800},
            11: {'easy': 800, 'medium': 1600, 'hard': 2400, 'deadly': 3600},
            12: {'easy': 1000, 'medium': 2000, 'hard': 3000, 'deadly': 4500},
            13: {'easy': 1100, 'medium': 2200, 'hard': 3400, 'deadly': 5100},
            14: {'easy': 1250, 'medium': 2500, 'hard': 3800, 'deadly': 5700},
            15: {'easy': 1400, 'medium': 2800, 'hard': 4300, 'deadly': 6400},
            16: {'easy': 1600, 'medium': 3200, 'hard': 4800, 'deadly': 7200},
            17: {'easy': 2000, 'medium': 3900, 'hard': 5900, 'deadly': 8800},
            18: {'easy': 2100, 'medium': 4200, 'hard': 6300, 'deadly': 9500},
            19: {'easy': 2400, 'medium': 4900, 'hard': 7300, 'deadly': 10900},
            20: {'easy': 2800, 'medium': 5700, 'hard': 8500, 'deadly': 12700},
        }

        return thresholds_table.get(level, thresholds_table[1])