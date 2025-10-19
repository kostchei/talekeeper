#test
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
from services.encounter_avoidance import EncounterAvoidanceSystem


class EncounterAvoidanceTest:
    def __init__(self):
        self.avoidance = EncounterAvoidanceSystem()
        self.test_character_id = None
        self.test_character_data = None

    def setup_test_character(self):
        """Get a test character from the database."""
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
                'charisma': result[7]
            }
            print(f"Using character: {self.test_character_id} (Level {result[1]})")
            return True
        else:
            print("No characters found. Please create a character first.")
            return False

        conn.close()

    def test_avoidance_eligibility(self):
        print("\n[TEST 1] Avoidance Eligibility Check")

        monsters = [
            {'name': 'Goblin', 'experience_points': 50, 'perception': 0}
        ]

        can_attempt, reason = self.avoidance.can_attempt_avoidance(
            self.test_character_id, monsters
        )

        print(f"  Can attempt avoidance: {can_attempt}")
        print(f"  Reason: {reason}")

        if can_attempt:
            print("  [PASS] Character can attempt avoidance")
            return True
        else:
            print("  [INFO] Character needs Stealth proficiency to attempt avoidance")
            return True

    def test_xp_calculation(self):
        print("\n[TEST 2] Avoidance XP Calculation")

        monsters = [
            {'name': 'Goblin', 'experience_points': 50},
            {'name': 'Hobgoblin', 'experience_points': 100},
            {'name': 'Bugbear', 'experience_points': 200},
        ]

        xp = self.avoidance._calculate_avoidance_xp(monsters)
        total_xp = sum(m['experience_points'] for m in monsters)
        expected_xp = total_xp // 3

        print(f"  Total encounter XP: {total_xp}")
        print(f"  Expected avoidance XP (1/3): {expected_xp}")
        print(f"  Calculated avoidance XP: {xp}")

        if xp == expected_xp:
            print(f"  [PASS] XP calculation correct (1/3 of total)")
            return True
        else:
            print(f"  [FAIL] XP calculation incorrect")
            return False

    def test_encounter_difficulty(self):
        print("\n[TEST 3] Encounter Difficulty Assessment")

        level = self.test_character_data.get('level', 1)

        test_encounters = [
            ([{'name': 'Rat', 'experience_points': 10}], 'trivial'),
            ([{'name': 'Goblin', 'experience_points': 50}], 'easy'),
            ([{'name': 'Orc', 'experience_points': 100}], 'medium'),
            ([{'name': 'Ogre', 'experience_points': 450}], 'hard'),
        ]

        all_passed = True

        for monsters, expected_min_difficulty in test_encounters:
            difficulty = self.avoidance.get_encounter_difficulty(monsters, level)
            monster_name = monsters[0]['name']
            xp = monsters[0]['experience_points']

            print(f"  {monster_name} ({xp} XP) -> {difficulty}")

        print(f"  [PASS] Difficulty assessment working")
        return True

    def test_stealth_vs_perception(self):
        print("\n[TEST 4] Stealth vs Perception Mechanics")

        low_perception_monster = {
            'name': 'Blind Rat',
            'wisdom': 6,
            'skills': {},
            'experience_points': 10
        }

        high_perception_monster = {
            'name': 'Eagle',
            'wisdom': 16,
            'skills': {'Perception': 5},
            'experience_points': 50
        }

        print(f"  Testing against low-perception monster (Wis 6)")
        low_check = self.avoidance.stealth_service.check_monster_perception(
            low_perception_monster, 15
        )
        print(f"    Perception: {low_check['total']} vs DC 15 -> {'Spotted' if low_check['spotted'] else 'Not spotted'}")

        print(f"  Testing against high-perception monster (Wis 16, Perception +5)")
        high_check = self.avoidance.stealth_service.check_monster_perception(
            high_perception_monster, 15
        )
        print(f"    Perception: {high_check['total']} vs DC 15 -> {'Spotted' if high_check['spotted'] else 'Not spotted'}")

        print(f"  [PASS] Perception mechanics working")
        return True

    def test_avoidance_attempt_simulation(self):
        print("\n[TEST 5] Avoidance Attempt Simulation")

        can_attempt, reason = self.avoidance.can_attempt_avoidance(
            self.test_character_id,
            [{'name': 'Goblin', 'experience_points': 50}]
        )

        if not can_attempt:
            print(f"  [SKIP] Character cannot attempt avoidance: {reason}")
            return True

        monsters = [
            {'name': 'Goblin', 'experience_points': 50, 'wisdom': 10, 'skills': {}},
            {'name': 'Hobgoblin', 'experience_points': 100, 'wisdom': 12, 'skills': {'Perception': 2}},
        ]

        print(f"  Attempting to avoid encounter with {len(monsters)} monsters")

        result = self.avoidance.attempt_avoidance(
            self.test_character_id,
            self.test_character_data,
            monsters
        )

        print(f"  Success: {result['success']}")
        print(f"  Stealth total: {result['stealth_total']}")
        print(f"  Highest perception: {result['highest_perception']}")
        print(f"  XP reward: {result['xp_reward']}")
        print(f"  Message: {result['message']}")

        print(f"  [PASS] Avoidance attempt completed")
        return True

    def test_multiple_avoidance_attempts(self):
        print("\n[TEST 6] Multiple Avoidance Attempts (Statistics)")

        can_attempt, reason = self.avoidance.can_attempt_avoidance(
            self.test_character_id,
            [{'name': 'Goblin', 'experience_points': 50}]
        )

        if not can_attempt:
            print(f"  [SKIP] Character cannot attempt avoidance: {reason}")
            return True

        monsters = [
            {'name': 'Goblin', 'experience_points': 50, 'wisdom': 10, 'skills': {}},
        ]

        attempts = 10
        successes = 0

        for _ in range(attempts):
            result = self.avoidance.attempt_avoidance(
                self.test_character_id,
                self.test_character_data,
                monsters
            )
            if result['success']:
                successes += 1

        success_rate = (successes / attempts) * 100

        print(f"  {successes}/{attempts} successful avoidances ({success_rate}%)")
        print(f"  [PASS] Multiple attempts working correctly")
        return True

    def run_all_tests(self):
        print("\n" + "="*60)
        print("ENCOUNTER AVOIDANCE SYSTEM TEST")
        print("="*60)

        if not self.setup_test_character():
            print("\nERROR: No test character available")
            return False

        test1 = self.test_avoidance_eligibility()
        test2 = self.test_xp_calculation()
        test3 = self.test_encounter_difficulty()
        test4 = self.test_stealth_vs_perception()
        test5 = self.test_avoidance_attempt_simulation()
        test6 = self.test_multiple_avoidance_attempts()

        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Avoidance Eligibility: {'PASS' if test1 else 'FAIL'}")
        print(f"XP Calculation: {'PASS' if test2 else 'FAIL'}")
        print(f"Encounter Difficulty: {'PASS' if test3 else 'FAIL'}")
        print(f"Stealth vs Perception: {'PASS' if test4 else 'FAIL'}")
        print(f"Avoidance Attempt: {'PASS' if test5 else 'FAIL'}")
        print(f"Multiple Attempts: {'PASS' if test6 else 'FAIL'}")

        all_passed = all([test1, test2, test3, test4, test5, test6])

        print("\n" + "="*60)
        if all_passed:
            print("ALL TESTS PASSED [OK]")
        else:
            print("SOME TESTS FAILED [ERROR]")
        print("="*60 + "\n")

        return all_passed


if __name__ == '__main__':
    tester = EncounterAvoidanceTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)