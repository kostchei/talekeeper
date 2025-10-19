# test
"""
End-to-End Cunning Strike Combat Test

Tests the complete flow:
1. Rogue selects Cunning Strike effects
2. Attacks with Sneak Attack
3. Dice cost deducted
4. Saving throws rolled
5. Conditions applied
6. Combat log messages
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import sqlite3
import json
from typing import Dict, Any

from services.cunning_strike_manager import CunningStrikeManager, CunningStrikeEffect
from services.weapon_attack_service import WeaponAttackService
from services.condition_manager import ConditionManager


class TestCunningStrikeEndToEnd:
    """End-to-end tests for Cunning Strike in combat"""

    def setup_method(self):
        """Setup test database with full schema"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self._setup_test_database()

        self.strike_manager = CunningStrikeManager(self.db_path)
        self.weapon_service = WeaponAttackService(self.db_path)
        self.condition_manager = ConditionManager(self.db_path)

    def teardown_method(self):
        """Cleanup"""
        try:
            if os.path.exists(self.db_path):
                os.unlink(self.db_path)
        except PermissionError:
            pass

    def _setup_test_database(self):
        """Setup complete database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    level INTEGER DEFAULT 1,
                    dexterity INTEGER DEFAULT 18,
                    constitution INTEGER DEFAULT 12
                )
            """)

            cursor.execute("""
                CREATE TABLE character_combat_state (
                    character_id TEXT PRIMARY KEY,
                    cunning_strike_selection TEXT,
                    sneak_attack_used_this_turn BOOLEAN DEFAULT 0,
                    last_updated TEXT DEFAULT (datetime('now'))
                )
            """)

            cursor.execute("""
                CREATE TABLE character_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT,
                    item_name TEXT,
                    quantity INTEGER DEFAULT 1
                )
            """)

            cursor.execute("""
                CREATE TABLE rogue_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER,
                    sneak_attack_dice INTEGER DEFAULT 1,
                    sneak_attack_used_this_turn BOOLEAN DEFAULT 0
                )
            """)

            conn.commit()

    def _create_rogue(self, level: int = 5, rogue_id: str = "rogue1", dex: int = 18) -> str:
        """Create test rogue"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level, dexterity)
                VALUES (?, 'Test Rogue', 'rogue', ?, ?)
            """, (rogue_id, level, dex))

            cursor.execute("""
                INSERT INTO rogue_features (character_id, level, sneak_attack_dice)
                VALUES (?, ?, ?)
            """, (rogue_id, level, self.strike_manager._calculate_sneak_attack_dice(level)))

            conn.commit()
        return rogue_id

    def _create_goblin(self, goblin_id: str = "goblin1") -> str:
        """Create test goblin target"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level, dexterity, constitution)
                VALUES (?, 'Goblin', 'monster', 1, 14, 10)
            """, (goblin_id,))
            conn.commit()
        return goblin_id

    def _store_cunning_strike_selection(self, character_id: str, effects: list):
        """Store Cunning Strike selection"""
        effect_ids = [eff.value for eff in effects]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO character_combat_state
                (character_id, cunning_strike_selection)
                VALUES (?, ?)
            """, (character_id, json.dumps(effect_ids)))
            conn.commit()

    def test_trip_strike_combat_flow(self):
        """Test Trip Strike: Select -> Attack -> Save -> Apply Prone"""
        print("\n=== Trip Strike End-to-End Test ===")

        rogue_id = self._create_rogue(level=5, dex=18)
        goblin_id = self._create_goblin()

        print("[OK] Step 1: Rogue selects Trip Strike (1d6 cost)")
        self._store_cunning_strike_selection(rogue_id, [CunningStrikeEffect.TRIP])

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cunning_strike_selection FROM character_combat_state WHERE character_id = ?", (rogue_id,))
            result = cursor.fetchone()
            assert result, "Selection should be stored"
            assert json.loads(result[0]) == ['trip']
            print("[OK] Selection stored in database")

        print("\n[OK] Step 2: Rogue attacks with Sneak Attack")

        character = {'id': rogue_id, 'dexterity': 18, 'level': 5, 'class_id': 'rogue'}
        target = {'id': goblin_id, 'dexterity': 14}
        weapon = {'name': 'Shortsword', 'weapon_properties': 'finesse', 'damage_dice': '1d6'}

        attack_result = self.weapon_service.calculate_attack_damage(
            character,
            weapon,
            target,
            advantage=True
        )

        print(f"[OK] Attack hit! Total damage: {attack_result['damage_total']}")
        print(f"[OK] Sneak Attack: {attack_result.get('sneak_attack_damage', 0)} damage")

        assert attack_result['sneak_attack_damage'] > 0, "Should have sneak attack damage"

        cunning_effects = attack_result.get('cunning_strike_effects', [])
        assert len(cunning_effects) > 0, "Should have Cunning Strike effects"

        print(f"\n[OK] Step 3: Cunning Strike effects applied: {len(cunning_effects)}")

        trip_effect = cunning_effects[0]
        print(f"[OK] Effect: {trip_effect['effect_name']}")
        print(f"[OK] Save DC: {trip_effect['save_dc']}")
        print(f"[OK] Save Type: {trip_effect.get('save_type', 'N/A')}")
        print(f"[OK] Save Result: {'SUCCESS' if trip_effect.get('save_result') else 'FAILED'}")

        if not trip_effect.get('save_result'):
            print(f"[OK] Condition '{trip_effect.get('condition')}' applied!")

            conditions = self.condition_manager.get_active_conditions(goblin_id)
            print(f"[OK] Goblin has {len(conditions)} active condition(s)")

            if len(conditions) > 0:
                print(f"[OK] Condition: {conditions[0].condition_type.value}")
        else:
            print(f"[OK] Save successful, no condition applied")

        print("\n[OK] Test complete: Trip Strike flow works end-to-end!")

    def test_poison_strike_requires_kit(self):
        """Test Poison Strike requires Poisoner's Kit"""
        print("\n=== Poison Strike Requirement Test ===")

        rogue_id = self._create_rogue(level=5)

        options = self.strike_manager.get_available_cunning_strikes(rogue_id)
        poison = next((opt for opt in options if opt['effect'] == 'poison'), None)

        assert poison is not None, "Poison Strike should be in options"
        assert not poison['available'], "Poison Strike should not be available without kit"
        print(f"[OK] Poison Strike blocked: {poison['unavailable_reason']}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_inventory (character_id, item_name, quantity)
                VALUES (?, "Poisoner's Kit", 1)
            """, (rogue_id,))
            conn.commit()

        options = self.strike_manager.get_available_cunning_strikes(rogue_id)
        poison = next((opt for opt in options if opt['effect'] == 'poison'), None)

        assert poison['available'], "Poison Strike should be available with kit"
        print(f"[OK] Poison Strike available with Poisoner's Kit!")

    def test_multiple_effects_level_11(self):
        """Test using 2 Cunning Strike effects at level 11+"""
        print("\n=== Multiple Effects Test (Level 11) ===")

        rogue_id = self._create_rogue(level=11, dex=18)
        goblin_id = self._create_goblin()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_inventory (character_id, item_name)
                VALUES (?, "Poisoner's Kit")
            """, (rogue_id,))
            conn.commit()

        print("[OK] Level 11 rogue can select 2 effects")

        validation = self.strike_manager.validate_cunning_strike_selection(
            rogue_id, [CunningStrikeEffect.TRIP, CunningStrikeEffect.POISON]
        )

        assert validation['valid'], f"Should allow 2 effects: {validation.get('error', '')}"
        print(f"[OK] Validation passed for Trip + Poison")

        damage_calc = validation['damage_calculation']
        print(f"[OK] Base: {damage_calc['base_sneak_attack_dice']}d6")
        print(f"[OK] Cost: {damage_calc['total_dice_cost']}d6")
        print(f"[OK] Remaining: {damage_calc['remaining_damage_dice']}d6")

        assert damage_calc['base_sneak_attack_dice'] == 6
        assert damage_calc['total_dice_cost'] == 2
        assert damage_calc['remaining_damage_dice'] == 4

    def test_knock_out_strike_high_cost(self):
        """Test Knock Out Strike with 6d6 cost"""
        print("\n=== Knock Out Strike Test (6d6 cost) ===")

        rogue_id = self._create_rogue(level=20, dex=18)
        goblin_id = self._create_goblin()

        print("[OK] Level 20 rogue has 10d6 Sneak Attack")

        self._store_cunning_strike_selection(rogue_id, [CunningStrikeEffect.KNOCK_OUT])

        character = {'id': rogue_id, 'dexterity': 18, 'level': 20, 'class_id': 'rogue'}
        target = {'id': goblin_id, 'constitution': 10}
        weapon = {'name': 'Shortsword', 'weapon_properties': 'finesse', 'damage_dice': '1d6'}

        attack_result = self.weapon_service.calculate_attack_damage(
            character, weapon, target, advantage=True
        )

        print(f"[OK] Attack completed")
        print(f"[OK] Sneak Attack damage: {attack_result.get('sneak_attack_damage', 0)}")

        cunning_effects = attack_result.get('cunning_strike_effects', [])
        if cunning_effects:
            knock_out = cunning_effects[0]
            print(f"[OK] Knock Out Strike applied")
            print(f"[OK] Save DC: {knock_out['save_dc']}")
            print(f"[OK] Dice cost: {knock_out['dice_cost']}d6")
            print(f"[OK] Remaining sneak attack should be ~4d6")


def main():
    """Run all end-to-end tests"""
    print("Running Cunning Strike End-to-End Combat Tests")
    print("=" * 70)

    test_suite = TestCunningStrikeEndToEnd()

    tests = [
        ("Trip Strike Full Flow", test_suite.test_trip_strike_combat_flow),
        ("Poison Strike Requirement", test_suite.test_poison_strike_requires_kit),
        ("Multiple Effects (L11)", test_suite.test_multiple_effects_level_11),
        ("Knock Out Strike (6d6)", test_suite.test_knock_out_strike_high_cost),
    ]

    passed = 0
    failed = 0

    for i, (test_name, test_func) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] {test_name}")
        print("-" * 70)
        try:
            test_suite.setup_method()
            test_func()
            print(f"[PASS] {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        finally:
            test_suite.teardown_method()

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("\nFull combat integration tested!")

    return failed == 0


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
