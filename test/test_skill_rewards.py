import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
from services.skill_challenge_rewards import SkillChallengeRewards


class SkillRewardTest:
    def __init__(self):
        self.rewards = SkillChallengeRewards()
        self.test_character_id = None

    def setup_test_character(self):
        """Create a test character in the database."""
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM characters LIMIT 1")
        result = cursor.fetchone()

        if result:
            self.test_character_id = result[0]
            print(f"Using existing character: {self.test_character_id}")
        else:
            print("No characters found in database. Please create a character first.")
            return False

        conn.close()
        return True

    def get_inventory_count(self, item_name: str) -> int:
        """Get quantity of an item in test character inventory."""
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = ?
        """, (self.test_character_id, item_name))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 0

    def test_rations_reward(self):
        print("\n[TEST 1] Rations Reward")
        character_data = {'id': self.test_character_id, 'level': 1}

        initial_count = self.get_inventory_count('Rations')
        print(f"  Initial rations: {initial_count}")

        updated_char, messages = self.rewards.apply_reward(character_data, 'rations')
        print(f"  Message: {messages[0]}")

        final_count = self.get_inventory_count('Rations')
        print(f"  Final rations: {final_count}")

        if final_count > initial_count:
            print(f"  [PASS] Rations increased by {final_count - initial_count}")
            return True
        else:
            print(f"  [FAIL] Rations did not increase")
            return False

    def test_healing_potion_reward(self):
        print("\n[TEST 2] Healing Potion Reward")
        character_data = {'id': self.test_character_id, 'level': 1}

        initial_count = self.get_inventory_count('Potion of Healing')
        print(f"  Initial potions: {initial_count}")

        updated_char, messages = self.rewards.apply_reward(character_data, 'healing potion')
        print(f"  Message: {messages[0]}")

        final_count = self.get_inventory_count('Potion of Healing')
        print(f"  Final potions: {final_count}")

        if final_count == initial_count + 1:
            print(f"  [PASS] Healing potion added")
            return True
        else:
            print(f"  [FAIL] Healing potion not added correctly")
            return False

    def test_consumable_reward(self):
        print("\n[TEST 3] Random Consumable Reward")
        character_data = {'id': self.test_character_id, 'level': 1}

        updated_char, messages = self.rewards.apply_reward(character_data, 'consumable')
        print(f"  Message: {messages[0]}")

        consumables = ['Potion of Healing', 'Potion of Climbing', 'Oil of Slipperiness', 'Antitoxin', 'Holy Water']
        found = False
        for consumable in consumables:
            count = self.get_inventory_count(consumable)
            if count > 0:
                print(f"  Found {count}x {consumable} in inventory")
                found = True

        if found:
            print(f"  [PASS] Consumable added to inventory")
            return True
        else:
            print(f"  [FAIL] No consumable found in inventory")
            return False

    def test_item_reward(self):
        print("\n[TEST 4] Random Item Reward")
        character_data = {'id': self.test_character_id, 'level': 1}

        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM character_inventory WHERE character_id = ?
        """, (self.test_character_id,))
        initial_count = cursor.fetchone()[0]
        conn.close()

        updated_char, messages = self.rewards.apply_reward(character_data, 'item')
        print(f"  Message: {messages[0]}")

        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM character_inventory WHERE character_id = ?
        """, (self.test_character_id,))
        final_count = cursor.fetchone()[0]
        conn.close()

        if final_count > initial_count:
            print(f"  [PASS] Item added to inventory")
            return True
        else:
            print(f"  [FAIL] Item not added")
            return False

    def run_all_tests(self):
        print("\n" + "="*60)
        print("SKILL REWARD SYSTEM TEST")
        print("="*60)

        if not self.setup_test_character():
            print("\nERROR: No test character available")
            return False

        test1 = self.test_rations_reward()
        test2 = self.test_healing_potion_reward()
        test3 = self.test_consumable_reward()
        test4 = self.test_item_reward()

        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Rations Reward: {'PASS' if test1 else 'FAIL'}")
        print(f"Healing Potion Reward: {'PASS' if test2 else 'FAIL'}")
        print(f"Consumable Reward: {'PASS' if test3 else 'FAIL'}")
        print(f"Item Reward: {'PASS' if test4 else 'FAIL'}")

        all_passed = test1 and test2 and test3 and test4

        print("\n" + "="*60)
        if all_passed:
            print("ALL TESTS PASSED [OK]")
        else:
            print("SOME TESTS FAILED [ERROR]")
        print("="*60 + "\n")

        return all_passed


if __name__ == '__main__':
    tester = SkillRewardTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)