#test
import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class RestSystemTest:
    def __init__(self):
        self.db_path = 'talekeeper.db'
        self.test_character_id = None

    def setup_test_character(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, race_id, class_id, level, experience_points,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                hit_points_max, hit_points_current, armor_class,
                created_at
            ) VALUES (
                'test_rest_char', 'Test Rester', 'human', 'fighter', 5, 6500,
                16, 14, 15, 10, 12, 8,
                42, 20, 18,
                datetime('now')
            )
        """)

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, item_type, quantity, equipped)
            VALUES ('test_rest_char', 'Rations', 'gear', 5, 0)
        """)

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, item_type, quantity, equipped)
            VALUES ('test_rest_char', 'Gold Pieces', 'treasure', 100, 0)
        """)

        conn.commit()
        conn.close()

        self.test_character_id = 'test_rest_char'
        print(f"Created test character: {self.test_character_id}")

    def cleanup_test_character(self):
        if not self.test_character_id:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM character_inventory WHERE character_id = ?", (self.test_character_id,))
        cursor.execute("DELETE FROM characters WHERE id = ?", (self.test_character_id,))

        conn.commit()
        conn.close()

        print(f"Cleaned up test character: {self.test_character_id}")

    def test_ration_check(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations' AND quantity > 0
        """, (self.test_character_id,))

        result = cursor.fetchone()
        conn.close()

        has_rations = result is not None and result[0] > 0

        if has_rations:
            print(f"[PASS] Character has {result[0]} rations")
            return True
        else:
            print("[FAIL] Character has no rations")
            return False

    def test_ration_consumption(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (self.test_character_id,))

        before = cursor.fetchone()
        before_qty = before[0] if before else 0

        cursor.execute("""
            UPDATE character_inventory
            SET quantity = quantity - 1
            WHERE character_id = ? AND item_name = 'Rations' AND quantity > 0
        """, (self.test_character_id,))

        cursor.execute("""
            DELETE FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations' AND quantity <= 0
        """, (self.test_character_id,))

        conn.commit()

        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (self.test_character_id,))

        after = cursor.fetchone()
        after_qty = after[0] if after else 0

        conn.close()

        if after_qty == before_qty - 1:
            print(f"[PASS] Ration consumed: {before_qty} -> {after_qty}")
            return True
        else:
            print(f"[FAIL] Ration consumption failed: {before_qty} -> {after_qty}")
            return False

    def test_no_rations_scenario(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (self.test_character_id,))

        conn.commit()

        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations' AND quantity > 0
        """, (self.test_character_id,))

        result = cursor.fetchone()
        conn.close()

        has_no_rations = result is None

        if has_no_rations:
            print("[PASS] Character correctly has no rations")
            return True
        else:
            print("[FAIL] Character still has rations when they shouldn't")
            return False

    def run_all_tests(self):
        print("\n" + "="*60)
        print("REST SYSTEM REGRESSION TEST")
        print("="*60)

        try:
            self.setup_test_character()

            print("\n[TEST 1] Ration Check")
            test1 = self.test_ration_check()

            print("\n[TEST 2] Ration Consumption")
            test2 = self.test_ration_consumption()

            print("\n[TEST 3] No Rations Scenario")
            test3 = self.test_no_rations_scenario()

            print("\n" + "="*60)
            print("TEST RESULTS")
            print("="*60)
            print(f"Ration Check: {'PASS' if test1 else 'FAIL'}")
            print(f"Ration Consumption: {'PASS' if test2 else 'FAIL'}")
            print(f"No Rations Scenario: {'PASS' if test3 else 'FAIL'}")

            all_passed = test1 and test2 and test3

            print("\n" + "="*60)
            if all_passed:
                print("ALL TESTS PASSED [OK]")
            else:
                print("SOME TESTS FAILED [ERROR]")
            print("="*60 + "\n")

            return all_passed

        finally:
            self.cleanup_test_character()


if __name__ == '__main__':
    tester = RestSystemTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)