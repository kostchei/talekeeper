# test
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
from services.parlay_system import ParlaySystem


class ParlaySystemTest:
    def __init__(self):
        self.parlay = ParlaySystem()
        self.test_character_id = None

    def setup_test_character(self):
        """Get a test character from the database."""
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, level FROM characters LIMIT 1")
        result = cursor.fetchone()

        if result:
            self.test_character_id = result[0]
            print(f"Using character: {self.test_character_id} (Level {result[1]})")
            return True
        else:
            print("No characters found. Please create a character first.")
            return False

        conn.close()

    def test_evil_monster_parlay(self):
        print("\n[TEST 1] Evil Monster Parlay Check")

        evil_monster = {
            'name': 'Evil Goblin',
            'alignment': 'lawful evil',
            'experience_points': 50
        }

        can_parlay = self.parlay.can_parlay_with_monster(evil_monster)
        print(f"  Evil monster can parlay: {can_parlay}")

        if not can_parlay:
            print("  [PASS] Evil monsters cannot be parlayed with")
            return True
        else:
            print("  [FAIL] Evil monsters should not be available for parlay")
            return False

    def test_neutral_monster_parlay(self):
        print("\n[TEST 2] Neutral Monster Parlay Check")

        neutral_monster = {
            'name': 'Neutral Goblin',
            'alignment': 'neutral',
            'experience_points': 50
        }

        attempts = 10
        parlay_count = 0

        for _ in range(attempts):
            if self.parlay.can_parlay_with_monster(neutral_monster):
                parlay_count += 1

        percentage = (parlay_count / attempts) * 100
        print(f"  Parlay available {parlay_count}/{attempts} times ({percentage}%)")

        if 50 <= percentage <= 100:
            print(f"  [PASS] Neutral monsters can sometimes be parlayed with")
            return True
        else:
            print(f"  [FAIL] Expected 50-100% parlay rate for neutral monsters")
            return False

    def test_good_monster_parlay(self):
        print("\n[TEST 3] Good Monster Parlay Check")

        good_monster = {
            'name': 'Good Goblin',
            'alignment': 'lawful good',
            'experience_points': 50
        }

        attempts = 10
        parlay_count = 0

        for _ in range(attempts):
            if self.parlay.can_parlay_with_monster(good_monster):
                parlay_count += 1

        percentage = (parlay_count / attempts) * 100
        print(f"  Parlay available {parlay_count}/{attempts} times ({percentage}%)")

        if 50 <= percentage <= 100:
            print(f"  [PASS] Good monsters can often be parlayed with")
            return True
        else:
            print(f"  [FAIL] Expected 50-100% parlay rate for good monsters")
            return False

    def test_parlay_skills(self):
        print("\n[TEST 4] Parlay Skills Selection")

        skills = self.parlay.get_parlay_skills()
        print(f"  Selected skills: {', '.join(skills)}")

        cha_skills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']
        int_skills = ['Arcana', 'History', 'Investigation', 'Nature', 'Religion']
        wis_skills = ['Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival']

        if len(skills) != 4:
            print(f"  [FAIL] Expected 4 skills, got {len(skills)}")
            return False

        cha_count = sum(1 for s in skills if s in cha_skills)
        if cha_count != 3:
            print(f"  [FAIL] Expected 3 CHA skills, got {cha_count}")
            return False

        has_int_or_wis = any(s in int_skills or s in wis_skills for s in skills)
        if not has_int_or_wis:
            print(f"  [FAIL] Expected 1 INT/WIS skill")
            return False

        print(f"  [PASS] Correct skill distribution (3 CHA + 1 INT/WIS)")
        return True

    def test_xp_calculation(self):
        print("\n[TEST 5] Parlay XP Calculation")

        monsters = [
            {'name': 'Goblin', 'experience_points': 50},
            {'name': 'Hobgoblin', 'experience_points': 100},
            {'name': 'Bugbear', 'experience_points': 200},
        ]

        xp = self.parlay.calculate_parlay_xp_reward(monsters)
        expected_xp = 200 // 2

        print(f"  Most powerful monster: Bugbear (200 XP)")
        print(f"  Expected parlay XP: {expected_xp}")
        print(f"  Calculated parlay XP: {xp}")

        if xp == expected_xp:
            print(f"  [PASS] XP calculation correct (1/2 of highest monster)")
            return True
        else:
            print(f"  [FAIL] XP calculation incorrect")
            return False

    def test_encounter_parlay_check(self):
        print("\n[TEST 6] Encounter Parlay Check")

        all_evil = [
            {'name': 'Devil', 'alignment': 'lawful evil'},
            {'name': 'Demon', 'alignment': 'chaotic evil'},
        ]

        can_parlay, reason = self.parlay.can_parlay_with_encounter(all_evil)
        print(f"  All evil encounter: can_parlay={can_parlay}")
        print(f"    Reason: {reason}")

        if not can_parlay:
            print(f"  [PASS] All-evil encounters cannot be parlayed")
        else:
            print(f"  [FAIL] All-evil encounters should not allow parlay")
            return False

        mixed_alignment = [
            {'name': 'Goblin', 'alignment': 'neutral evil'},
            {'name': 'Orc', 'alignment': 'neutral'},
        ]

        attempts = 10
        parlay_count = 0
        for _ in range(attempts):
            can_parlay, reason = self.parlay.can_parlay_with_encounter(mixed_alignment)
            if can_parlay:
                parlay_count += 1

        print(f"  Mixed alignment: parlay available {parlay_count}/{attempts} times")

        if parlay_count > 0:
            print(f"  [PASS] Mixed encounters can sometimes be parlayed")
            return True
        else:
            print(f"  [FAIL] Expected some parlay opportunities for mixed encounters")
            return False

    def run_all_tests(self):
        print("\n" + "="*60)
        print("PARLAY SYSTEM TEST")
        print("="*60)

        if not self.setup_test_character():
            print("\nERROR: No test character available")
            return False

        test1 = self.test_evil_monster_parlay()
        test2 = self.test_neutral_monster_parlay()
        test3 = self.test_good_monster_parlay()
        test4 = self.test_parlay_skills()
        test5 = self.test_xp_calculation()
        test6 = self.test_encounter_parlay_check()

        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Evil Monster Parlay: {'PASS' if test1 else 'FAIL'}")
        print(f"Neutral Monster Parlay: {'PASS' if test2 else 'FAIL'}")
        print(f"Good Monster Parlay: {'PASS' if test3 else 'FAIL'}")
        print(f"Parlay Skills: {'PASS' if test4 else 'FAIL'}")
        print(f"XP Calculation: {'PASS' if test5 else 'FAIL'}")
        print(f"Encounter Parlay Check: {'PASS' if test6 else 'FAIL'}")

        all_passed = all([test1, test2, test3, test4, test5, test6])

        print("\n" + "="*60)
        if all_passed:
            print("ALL TESTS PASSED [OK]")
        else:
            print("SOME TESTS FAILED [ERROR]")
        print("="*60 + "\n")

        return all_passed


if __name__ == '__main__':
    tester = ParlaySystemTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)