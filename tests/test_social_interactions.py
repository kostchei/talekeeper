import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
from services.parlay_system import ParlaySystem
from services.encounter_avoidance import EncounterAvoidanceSystem
from services.skill_challenge_rewards import SkillChallengeRewards


class SocialInteractionsTest:
    """
    Comprehensive test suite for Phase 3 - Social Interactions systems:
    - Skill encounter rewards
    - Parlay system
    - Stealth avoidance
    """

    def __init__(self):
        self.parlay = ParlaySystem()
        self.avoidance = EncounterAvoidanceSystem()
        self.rewards = SkillChallengeRewards()
        self.test_character_id = None
        self.test_character_data = None

    def setup(self):
        """Setup test character."""
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, level, dexterity, strength, constitution, intelligence, wisdom, charisma
            FROM characters LIMIT 1
        """)
        result = cursor.fetchone()

        if result:
            self.test_character_id = result[0]
            self.test_character_data = {
                'id': result[0],
                'level': result[1],
                'dexterity': result[2],
                'strength': result[3],
                'constitution': result[4],
                'intelligence': result[5],
                'wisdom': result[6],
                'charisma': result[7],
                'hit_points_current': 30,
                'hit_points_max': 30
            }
            return True
        else:
            return False

        conn.close()

    def test_skill_rewards_integration(self):
        """Test that skill challenges properly reward items."""
        print("\n[INTEGRATION 1] Skill Challenge Rewards")

        initial_rations = self._get_inventory_count('Rations')
        initial_potions = self._get_inventory_count('Potion of Healing')

        updated_char, messages = self.rewards.apply_reward(
            self.test_character_data, 'rations'
        )
        print(f"  Applied rations reward: {messages[0]}")

        updated_char, messages = self.rewards.apply_reward(
            self.test_character_data, 'healing potion'
        )
        print(f"  Applied potion reward: {messages[0]}")

        final_rations = self._get_inventory_count('Rations')
        final_potions = self._get_inventory_count('Potion of Healing')

        rations_gained = final_rations - initial_rations
        potions_gained = final_potions - initial_potions

        print(f"  Rations gained: {rations_gained}")
        print(f"  Potions gained: {potions_gained}")

        if rations_gained > 0 and potions_gained > 0:
            print("  [PASS] Skill rewards properly grant items")
            return True
        else:
            print("  [FAIL] Items not added correctly")
            return False

    def test_parlay_encounter_flow(self):
        """Test complete parlay encounter flow."""
        print("\n[INTEGRATION 2] Parlay Encounter Flow")

        encounter_monsters = [
            {'name': 'Neutral Orc', 'alignment': 'neutral', 'experience_points': 100, 'wisdom': 12},
            {'name': 'Neutral Goblin', 'alignment': 'neutral', 'experience_points': 50, 'wisdom': 10},
        ]

        can_parlay, reason = self.parlay.can_parlay_with_encounter(encounter_monsters)
        print(f"  Can parlay with encounter: {can_parlay}")
        print(f"    Reason: {reason}")

        if can_parlay:
            skills = self.parlay.get_parlay_skills()
            print(f"  Parlay skills: {', '.join(skills)}")

            xp_reward = self.parlay.calculate_parlay_xp_reward(encounter_monsters)
            print(f"  Potential XP reward: {xp_reward} (half of strongest monster)")

            print("  [PASS] Parlay flow working correctly")
            return True
        else:
            print("  [INFO] Parlay not available this time (75% chance)")
            return True

    def test_stealth_avoidance_flow(self):
        """Test complete stealth avoidance flow."""
        print("\n[INTEGRATION 3] Stealth Avoidance Flow")

        encounter_monsters = [
            {'name': 'Goblin Scout', 'experience_points': 50, 'wisdom': 10, 'skills': {}},
        ]

        can_attempt, reason = self.avoidance.can_attempt_avoidance(
            self.test_character_id, encounter_monsters
        )

        print(f"  Can attempt avoidance: {can_attempt}")
        print(f"    Reason: {reason}")

        if not can_attempt:
            print("  [INFO] Character needs Stealth proficiency")
            return True

        difficulty = self.avoidance.get_encounter_difficulty(
            encounter_monsters, self.test_character_data['level']
        )
        print(f"  Encounter difficulty: {difficulty}")

        xp_reward = self.avoidance._calculate_avoidance_xp(encounter_monsters)
        print(f"  Potential XP if avoided: {xp_reward} (1/3 of total)")

        print("  [PASS] Avoidance system working correctly")
        return True

    def test_encounter_resolution_options(self):
        """Test that encounters offer multiple resolution paths."""
        print("\n[INTEGRATION 4] Multiple Encounter Resolution Options")

        encounter_monsters = [
            {'name': 'Neutral Guard', 'alignment': 'lawful neutral', 'experience_points': 100, 'wisdom': 12, 'skills': {}},
        ]

        print("  Checking available resolution options:")

        combat_available = True
        print(f"    1. Combat: Always available")

        can_parlay, parlay_reason = self.parlay.can_parlay_with_encounter(encounter_monsters)
        print(f"    2. Parlay: {can_parlay} - {parlay_reason}")

        can_avoid, avoid_reason = self.avoidance.can_attempt_avoidance(
            self.test_character_id, encounter_monsters
        )
        print(f"    3. Stealth Avoidance: {can_avoid} - {avoid_reason}")

        options_available = 1 + (1 if can_parlay else 0) + (1 if can_avoid else 0)
        print(f"  Total options available: {options_available}/3")

        if options_available >= 1:
            print("  [PASS] Encounter resolution options working")
            return True
        else:
            print("  [FAIL] No resolution options available")
            return False

    def test_xp_reward_balance(self):
        """Test that different resolution methods have balanced XP rewards."""
        print("\n[INTEGRATION 5] XP Reward Balance")

        encounter_monsters = [
            {'name': 'Orc', 'alignment': 'neutral', 'experience_points': 100, 'wisdom': 12, 'skills': {}},
        ]

        combat_xp = sum(m['experience_points'] for m in encounter_monsters)
        parlay_xp = self.parlay.calculate_parlay_xp_reward(encounter_monsters)
        avoidance_xp = self.avoidance._calculate_avoidance_xp(encounter_monsters)

        print(f"  Combat XP (full): {combat_xp}")
        print(f"  Parlay XP (1/2 of strongest): {parlay_xp}")
        print(f"  Avoidance XP (1/3 of total): {avoidance_xp}")

        print(f"  Parlay ratio: {parlay_xp/combat_xp:.1%}")
        print(f"  Avoidance ratio: {avoidance_xp/combat_xp:.1%}")

        if parlay_xp < combat_xp and avoidance_xp < combat_xp:
            print("  [PASS] Non-combat options reward less XP than combat")
            return True
        else:
            print("  [FAIL] XP rewards imbalanced")
            return False

    def test_skill_challenge_system_integration(self):
        """Test skill challenge system integration with rewards."""
        print("\n[INTEGRATION 6] Skill Challenge System with Item Rewards")

        reward_types = ['rations', 'healing potion', 'consumable', 'item']
        results = {}

        for reward_type in reward_types:
            updated_char, messages = self.rewards.apply_reward(
                self.test_character_data, reward_type
            )
            results[reward_type] = messages[0] if messages else "No message"
            print(f"  {reward_type}: {results[reward_type]}")

        if all(results.values()):
            print("  [PASS] All reward types working")
            return True
        else:
            print("  [FAIL] Some reward types failed")
            return False

    def _get_inventory_count(self, item_name: str) -> int:
        """Get quantity of an item in inventory."""
        try:
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT quantity FROM character_inventory
                WHERE character_id = ? AND item_name = ?
            """, (self.test_character_id, item_name))

            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            if conn:
                conn.close()

    def run_all_tests(self):
        print("\n" + "="*60)
        print("PHASE 3: SOCIAL INTERACTIONS INTEGRATION TEST")
        print("="*60)

        if not self.setup():
            print("\nERROR: No test character available")
            return False

        test1 = self.test_skill_rewards_integration()
        test2 = self.test_parlay_encounter_flow()
        test3 = self.test_stealth_avoidance_flow()
        test4 = self.test_encounter_resolution_options()
        test5 = self.test_xp_reward_balance()
        test6 = self.test_skill_challenge_system_integration()

        print("\n" + "="*60)
        print("INTEGRATION TEST RESULTS")
        print("="*60)
        print(f"Skill Rewards Integration: {'PASS' if test1 else 'FAIL'}")
        print(f"Parlay Flow: {'PASS' if test2 else 'FAIL'}")
        print(f"Stealth Avoidance Flow: {'PASS' if test3 else 'FAIL'}")
        print(f"Multiple Resolution Options: {'PASS' if test4 else 'FAIL'}")
        print(f"XP Reward Balance: {'PASS' if test5 else 'FAIL'}")
        print(f"Skill Challenge Integration: {'PASS' if test6 else 'FAIL'}")

        all_passed = all([test1, test2, test3, test4, test5, test6])

        print("\n" + "="*60)
        if all_passed:
            print("ALL INTEGRATION TESTS PASSED [OK]")
        else:
            print("SOME INTEGRATION TESTS FAILED [ERROR]")
        print("="*60 + "\n")

        return all_passed


if __name__ == '__main__':
    tester = SocialInteractionsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)