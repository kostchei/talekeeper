#test
"""
Integration Tests for Cunning Strike System

Tests the complete Cunning Strike flow:
- Selection UI
- Dice cost calculation
- Save DC calculation
- Effect application
- Multiple effects (level 11+)
- Poisoner's Kit requirement
- Context-sensitive enabling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import sqlite3
from typing import Dict, Any

from services.cunning_strike_manager import CunningStrikeManager, CunningStrikeEffect


class TestCunningStrikeIntegration:
    """Integration tests for Cunning Strike system"""

    def setup_method(self):
        """Setup test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self._setup_test_database()
        self.manager = CunningStrikeManager(self.db_path)

    def teardown_method(self):
        """Cleanup test database"""
        try:
            if os.path.exists(self.db_path):
                os.unlink(self.db_path)
        except PermissionError:
            pass

    def _setup_test_database(self):
        """Setup minimal database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    level INTEGER DEFAULT 1,
                    dexterity INTEGER DEFAULT 16
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

            conn.commit()

    def _create_test_rogue(self, level: int = 5, character_id: str = "test_rogue", dexterity: int = 18) -> str:
        """Create a test rogue character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level, dexterity)
                VALUES (?, 'Test Rogue', 'rogue', ?, ?)
            """, (character_id, level, dexterity))
            conn.commit()
        return character_id

    def test_available_options_level_5(self):
        """Test available Cunning Strike options at level 5"""
        rogue_id = self._create_test_rogue(level=5)
        options = self.manager.get_available_cunning_strikes(rogue_id)

        assert len(options) == 3, f"Level 5 should have 3 options, got {len(options)}"

        effect_names = [opt['name'] for opt in options]
        assert "Poison Strike" in effect_names
        assert "Trip Strike" in effect_names
        assert "Withdraw Strike" in effect_names

        print(f"[OK] Level 5 rogue has 3 Cunning Strike options")

    def test_available_options_level_14(self):
        """Test available Cunning Strike options at level 14"""
        rogue_id = self._create_test_rogue(level=14)
        options = self.manager.get_available_cunning_strikes(rogue_id)

        assert len(options) == 6, f"Level 14 should have 6 options, got {len(options)}"

        effect_names = [opt['name'] for opt in options]
        assert "Daze Strike" in effect_names
        assert "Knock Out Strike" in effect_names
        assert "Obscure Strike" in effect_names

        print(f"[OK] Level 14 rogue has all 6 Cunning Strike options (including Devious Strikes)")

    def test_damage_calculation_single_effect(self):
        """Test damage calculation with single Cunning Strike effect"""
        rogue_id = self._create_test_rogue(level=5)

        result = self.manager.calculate_sneak_attack_with_cost(
            rogue_id, [CunningStrikeEffect.TRIP]
        )

        assert result['base_sneak_attack_dice'] == 3, "Level 5 should have 3d6 sneak attack"
        assert result['total_dice_cost'] == 1, "Trip costs 1d6"
        assert result['remaining_damage_dice'] == 2, "Should have 2d6 remaining"
        assert result['remaining_damage_string'] == "2d6"

        print(f"[OK] Single effect: 3d6 - 1d6 (Trip) = 2d6 remaining")

    def test_damage_calculation_multiple_effects(self):
        """Test damage calculation with multiple Cunning Strike effects"""
        rogue_id = self._create_test_rogue(level=11)

        result = self.manager.calculate_sneak_attack_with_cost(
            rogue_id, [CunningStrikeEffect.TRIP, CunningStrikeEffect.POISON]
        )

        assert result['base_sneak_attack_dice'] == 6, "Level 11 should have 6d6 sneak attack"
        assert result['total_dice_cost'] == 2, "Trip + Poison costs 2d6"
        assert result['remaining_damage_dice'] == 4, "Should have 4d6 remaining"

        print(f"[OK] Multiple effects: 6d6 - 2d6 (Trip + Poison) = 4d6 remaining")

    def test_damage_calculation_high_cost(self):
        """Test damage calculation with high-cost Devious Strike"""
        rogue_id = self._create_test_rogue(level=20)

        result = self.manager.calculate_sneak_attack_with_cost(
            rogue_id, [CunningStrikeEffect.KNOCK_OUT]
        )

        assert result['base_sneak_attack_dice'] == 10, "Level 20 should have 10d6 sneak attack"
        assert result['total_dice_cost'] == 6, "Knock Out costs 6d6"
        assert result['remaining_damage_dice'] == 4, "Should have 4d6 remaining"

        print(f"[OK] High-cost effect: 10d6 - 6d6 (Knock Out) = 4d6 remaining")

    def test_save_dc_calculation(self):
        """Test Cunning Strike save DC calculation (8 + DEX + prof)"""
        rogue_id = self._create_test_rogue(level=5, dexterity=18)

        save_dc = self.manager.calculate_save_dc(rogue_id)

        dex_mod = (18 - 10) // 2  # +4
        prof_bonus = 3  # Level 5
        expected_dc = 8 + dex_mod + prof_bonus  # 8 + 4 + 3 = 15

        assert save_dc == expected_dc, f"Expected DC {expected_dc}, got {save_dc}"

        print(f"[OK] Save DC calculation: 8 + 4 (DEX) + 3 (prof) = 15")

    def test_can_use_multiple_effects_level_10(self):
        """Test that level 10 rogue cannot use multiple effects"""
        rogue_id = self._create_test_rogue(level=10)

        can_use_multiple = self.manager.can_use_multiple_effects(rogue_id)

        assert not can_use_multiple, "Level 10 should not allow multiple effects"

        print(f"[OK] Level 10 rogue cannot use multiple Cunning Strike effects")

    def test_can_use_multiple_effects_level_11(self):
        """Test that level 11+ rogue CAN use multiple effects"""
        rogue_id = self._create_test_rogue(level=11)

        can_use_multiple = self.manager.can_use_multiple_effects(rogue_id)

        assert can_use_multiple, "Level 11+ should allow multiple effects"

        print(f"[OK] Level 11+ rogue CAN use multiple Cunning Strike effects (Improved)")

    def test_validation_too_many_effects_level_5(self):
        """Test validation rejects multiple effects for level 5 rogue"""
        rogue_id = self._create_test_rogue(level=5)

        validation = self.manager.validate_cunning_strike_selection(
            rogue_id, [CunningStrikeEffect.TRIP, CunningStrikeEffect.POISON]
        )

        assert not validation['valid'], "Level 5 should not allow 2 effects"
        assert "Cannot select more than 1 effect" in validation['error']

        print(f"[OK] Validation blocks multiple effects for level 5 rogue")

    def test_validation_allows_multiple_effects_level_11(self):
        """Test validation allows multiple effects for level 11 rogue"""
        rogue_id = self._create_test_rogue(level=11)

        validation = self.manager.validate_cunning_strike_selection(
            rogue_id, [CunningStrikeEffect.TRIP, CunningStrikeEffect.POISON]
        )

        assert validation['valid'], f"Level 11 should allow 2 effects: {validation.get('error', '')}"

        print(f"[OK] Validation allows multiple effects for level 11+ rogue")

    def test_poisoners_kit_requirement(self):
        """Test Poison Strike requires Poisoner's Kit"""
        rogue_id = self._create_test_rogue(level=5)

        options = self.manager.get_available_cunning_strikes(rogue_id)
        poison_option = next(opt for opt in options if opt['effect'] == 'poison')

        assert not poison_option['available'], "Poison should not be available without kit"
        assert "Poisoner's Kit" in poison_option['unavailable_reason']

        print(f"[OK] Poison Strike disabled without Poisoner's Kit")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_inventory (character_id, item_name, quantity)
                VALUES (?, "Poisoner's Kit", 1)
            """, (rogue_id,))
            conn.commit()

        options = self.manager.get_available_cunning_strikes(rogue_id)
        poison_option = next(opt for opt in options if opt['effect'] == 'poison')

        assert poison_option['available'], "Poison should be available with kit"

        print(f"[OK] Poison Strike enabled with Poisoner's Kit in inventory")

    def test_sneak_attack_eligibility_with_advantage(self):
        """Test Sneak Attack eligibility with advantage"""
        rogue_id = self._create_test_rogue(level=5)

        context = {
            'has_advantage': True,
            'has_disadvantage': False,
            'allies_within_5ft': [],
            'weapon': {'weapon_properties': 'finesse'}
        }

        eligibility = self.manager.check_sneak_attack_eligibility(rogue_id, context)

        assert eligibility['eligible'], "Should be eligible with advantage"
        assert eligibility['reason'] == "Has advantage on attack"

        print(f"[OK] Sneak Attack eligible with advantage")

    def test_sneak_attack_eligibility_with_disadvantage(self):
        """Test Sneak Attack NOT eligible with disadvantage"""
        rogue_id = self._create_test_rogue(level=5)

        context = {
            'has_advantage': False,
            'has_disadvantage': True,
            'allies_within_5ft': ['ally1'],
            'weapon': {'weapon_properties': 'finesse'}
        }

        eligibility = self.manager.check_sneak_attack_eligibility(rogue_id, context)

        assert not eligibility['eligible'], "Should NOT be eligible with disadvantage"

        print(f"[OK] Sneak Attack blocked by disadvantage (even with ally nearby)")

    def test_sneak_attack_eligibility_non_finesse_weapon(self):
        """Test Sneak Attack not eligible with non-finesse weapon"""
        rogue_id = self._create_test_rogue(level=5)

        context = {
            'has_advantage': True,
            'has_disadvantage': False,
            'allies_within_5ft': [],
            'weapon': {'weapon_properties': 'heavy', 'weapon_type': 'martial melee'}
        }

        eligibility = self.manager.check_sneak_attack_eligibility(rogue_id, context)

        assert not eligibility['eligible'], "Should not be eligible with non-finesse weapon"

        print(f"[OK] Sneak Attack blocked by non-finesse weapon")

    def test_preview_generation(self):
        """Test Cunning Strike preview generation"""
        rogue_id = self._create_test_rogue(level=11, dexterity=18)

        preview = self.manager.get_cunning_strike_preview(
            rogue_id, [CunningStrikeEffect.TRIP, CunningStrikeEffect.POISON]
        )

        assert preview['base_sneak_attack'] == "6d6"
        assert preview['dice_cost'] == 2
        assert preview['remaining_damage'] == "4d6"
        assert preview['save_dc'] == 15

        assert len(preview['effects']) == 2
        assert preview['effects'][0]['name'] == "Trip Strike"
        assert preview['effects'][0]['cost'] == "1d6"
        assert preview['effects'][1]['name'] == "Poison Strike"

        print(f"[OK] Preview shows: 6d6 - 2d6 cost = 4d6 remaining, DC 15")

    def test_apply_cunning_strike(self):
        """Test applying Cunning Strike effects"""
        rogue_id = self._create_test_rogue(level=5, dexterity=18)

        result = self.manager.apply_cunning_strike(
            rogue_id, "target_id",
            [CunningStrikeEffect.TRIP],
            attack_damage=20
        )

        assert result['success'], f"Application should succeed: {result.get('error', '')}"
        assert result['sneak_attack_dice_remaining'] == 2
        assert result['sneak_attack_dice_spent'] == 1
        assert result['save_dc'] == 15

        assert len(result['effects']) == 1
        effect = result['effects'][0]
        assert effect['effect_name'] == "Trip Strike"
        assert effect['dice_cost'] == 1
        assert effect['save_type'] == "dexterity"
        assert effect['condition'] == "prone"

        print(f"[OK] Trip Strike applied: DC 15 Dex save or Prone")


def main():
    """Run all integration tests"""
    print("Running Cunning Strike Integration Tests")
    print("=" * 70)

    test_suite = TestCunningStrikeIntegration()

    tests = [
        ("Available Options (Level 5)", test_suite.test_available_options_level_5),
        ("Available Options (Level 14)", test_suite.test_available_options_level_14),
        ("Damage Calc: Single Effect", test_suite.test_damage_calculation_single_effect),
        ("Damage Calc: Multiple Effects", test_suite.test_damage_calculation_multiple_effects),
        ("Damage Calc: High Cost", test_suite.test_damage_calculation_high_cost),
        ("Save DC Calculation", test_suite.test_save_dc_calculation),
        ("Multiple Effects: Level 10", test_suite.test_can_use_multiple_effects_level_10),
        ("Multiple Effects: Level 11+", test_suite.test_can_use_multiple_effects_level_11),
        ("Validation: Too Many (L5)", test_suite.test_validation_too_many_effects_level_5),
        ("Validation: Allow Multiple (L11)", test_suite.test_validation_allows_multiple_effects_level_11),
        ("Poisoner's Kit Requirement", test_suite.test_poisoners_kit_requirement),
        ("Sneak Attack: Advantage", test_suite.test_sneak_attack_eligibility_with_advantage),
        ("Sneak Attack: Disadvantage", test_suite.test_sneak_attack_eligibility_with_disadvantage),
        ("Sneak Attack: Wrong Weapon", test_suite.test_sneak_attack_eligibility_non_finesse_weapon),
        ("Preview Generation", test_suite.test_preview_generation),
        ("Apply Cunning Strike", test_suite.test_apply_cunning_strike),
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

    return failed == 0


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
