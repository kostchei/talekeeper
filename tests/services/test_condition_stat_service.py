"""
Test suite for the Condition Stat Service.
Tests automatic stat modifications from conditions.
"""

import sys
import os
import unittest
import tempfile
import sqlite3
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.condition_manager import (
    ConditionManager, ConditionType, ActiveCondition
)
from services.condition_stat_service import ConditionStatService


class TestConditionStatService(unittest.TestCase):
    """Test the condition stat modification system."""

    def setUp(self):
        """Create a test database and services."""
        # Create temporary database
        self.test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.test_db_path = self.test_db.name
        self.test_db.close()

        # Create test database schema
        self._create_test_schema()

        # Create services with test database
        self.condition_manager = ConditionManager(self.test_db_path)
        self.stat_service = ConditionStatService(self.test_db_path)

        # Make sure they use the same database path
        self.assertEqual(self.condition_manager.db_path, self.stat_service.db_path)

        # Test character ID
        self.test_character_id = "test_fighter_001"

    def tearDown(self):
        """Clean up test database."""
        try:
            os.unlink(self.test_db_path)
        except:
            pass

    def _create_test_schema(self):
        """Create minimal schema for testing."""
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    speed INTEGER DEFAULT 30
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, level, speed)
                VALUES ('test_fighter_001', 'Test Fighter', 5, 30)
            """)
            conn.commit()

    def test_movement_speed_modification(self):
        """Test movement speed modifications from conditions."""
        base_speed = 30

        # No conditions - should return base speed
        speed = self.stat_service.get_movement_speed_modifier(self.test_character_id, base_speed)
        self.assertEqual(speed, 30)

        # Add grappled condition (speed = 0)
        grappled = ActiveCondition(
            condition_type=ConditionType.GRAPPLED,
            source="Monster Grapple",
            duration_type="until_escape"
        )
        result = self.condition_manager.add_condition(self.test_character_id, grappled)
        self.assertTrue(result, "Failed to add grappled condition")

        # Debug: Check that condition was actually added
        conditions = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(conditions), 1, "Should have 1 condition")
        self.assertEqual(conditions[0].condition_type, ConditionType.GRAPPLED)

        # Debug: Clear cache and test the stat service condition manager
        if hasattr(self.stat_service.condition_manager, '_condition_cache'):
            self.stat_service.condition_manager._condition_cache.clear()

        stat_conditions = self.stat_service.condition_manager.get_active_conditions(self.test_character_id)
        print(f"Conditions from stat service: {len(stat_conditions)}")

        if stat_conditions:
            from services.condition_manager import ConditionEffects
            effects = ConditionEffects.get_effects(stat_conditions[0].condition_type)
            print(f"Effects from stat service: {effects}")

        speed = self.stat_service.get_movement_speed_modifier(self.test_character_id, base_speed)
        print(f"Speed result: {speed}")
        self.assertEqual(speed, 0)

        # Remove grappled, add exhaustion level 2
        self.condition_manager.remove_condition(self.test_character_id, ConditionType.GRAPPLED)

        exhaustion = ActiveCondition(
            condition_type=ConditionType.EXHAUSTION,
            source="Forced March",
            duration_type="permanent",
            exhaustion_level=2
        )
        self.condition_manager.add_condition(self.test_character_id, exhaustion)

        # Clear cache again after condition changes
        if hasattr(self.stat_service.condition_manager, '_condition_cache'):
            self.stat_service.condition_manager._condition_cache.clear()

        speed = self.stat_service.get_movement_speed_modifier(self.test_character_id, base_speed)
        self.assertEqual(speed, 20)  # 30 - (2 * 5) = 20

    def test_attack_roll_modifiers(self):
        """Test attack roll modifiers from conditions."""
        # No conditions
        modifiers = self.stat_service.get_attack_roll_modifier(self.test_character_id)
        self.assertFalse(modifiers["advantage"])
        self.assertFalse(modifiers["disadvantage"])
        self.assertEqual(modifiers["penalty"], 0)

        # Add poisoned (disadvantage on attacks)
        poisoned = ActiveCondition(
            condition_type=ConditionType.POISONED,
            source="Poison Dart",
            duration_type="minutes",
            duration_remaining=10
        )
        self.condition_manager.add_condition(self.test_character_id, poisoned)

        modifiers = self.stat_service.get_attack_roll_modifier(self.test_character_id)
        self.assertTrue(modifiers["disadvantage"])
        self.assertIn("poisoned", modifiers["sources"][0].lower())

        # Remove poisoned, add invisible (advantage on attacks)
        self.condition_manager.remove_condition(self.test_character_id, ConditionType.POISONED)

        invisible = ActiveCondition(
            condition_type=ConditionType.INVISIBLE,
            source="Invisibility Spell",
            duration_type="minutes",
            duration_remaining=10
        )
        self.condition_manager.add_condition(self.test_character_id, invisible)

        modifiers = self.stat_service.get_attack_roll_modifier(self.test_character_id)
        self.assertTrue(modifiers["advantage"])
        self.assertIn("invisible", modifiers["sources"][0].lower())

    def test_saving_throw_modifiers(self):
        """Test saving throw modifiers from conditions."""
        # No conditions
        modifiers = self.stat_service.get_saving_throw_modifier(self.test_character_id, "strength")
        self.assertFalse(modifiers["auto_fail"])
        self.assertFalse(modifiers["disadvantage"])

        # Add paralyzed (auto-fail STR and DEX saves)
        paralyzed = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.test_character_id, paralyzed)

        # Check strength save (should auto-fail)
        str_modifiers = self.stat_service.get_saving_throw_modifier(self.test_character_id, "strength")
        self.assertTrue(str_modifiers["auto_fail"])

        # Check dexterity save (should auto-fail)
        dex_modifiers = self.stat_service.get_saving_throw_modifier(self.test_character_id, "dexterity")
        self.assertTrue(dex_modifiers["auto_fail"])

        # Check wisdom save (should be normal)
        wis_modifiers = self.stat_service.get_saving_throw_modifier(self.test_character_id, "wisdom")
        self.assertFalse(wis_modifiers["auto_fail"])

        # Remove paralyzed, add restrained (disadvantage on DEX saves)
        self.condition_manager.remove_condition(self.test_character_id, ConditionType.PARALYZED)

        restrained = ActiveCondition(
            condition_type=ConditionType.RESTRAINED,
            source="Net",
            duration_type="until_escape"
        )
        self.condition_manager.add_condition(self.test_character_id, restrained)

        dex_modifiers = self.stat_service.get_saving_throw_modifier(self.test_character_id, "dexterity")
        self.assertTrue(dex_modifiers["disadvantage"])
        self.assertIn("restrained", dex_modifiers["sources"][0].lower())

    def test_ability_check_modifiers(self):
        """Test ability check modifiers from conditions."""
        # No conditions
        modifiers = self.stat_service.get_ability_check_modifier(self.test_character_id, "strength")
        self.assertFalse(modifiers["disadvantage"])
        self.assertEqual(modifiers["penalty"], 0)

        # Add poisoned (disadvantage on ability checks)
        poisoned = ActiveCondition(
            condition_type=ConditionType.POISONED,
            source="Spider Venom",
            duration_type="hours",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.test_character_id, poisoned)

        modifiers = self.stat_service.get_ability_check_modifier(self.test_character_id, "strength")
        self.assertTrue(modifiers["disadvantage"])

        # Add exhaustion level 1 (penalty to all checks)
        exhaustion = ActiveCondition(
            condition_type=ConditionType.EXHAUSTION,
            source="Starvation",
            duration_type="permanent",
            exhaustion_level=1
        )
        self.condition_manager.add_condition(self.test_character_id, exhaustion)

        modifiers = self.stat_service.get_ability_check_modifier(self.test_character_id, "intelligence")
        self.assertTrue(modifiers["disadvantage"])  # Still poisoned
        self.assertEqual(modifiers["penalty"], 2)  # Exhaustion penalty

    def test_action_economy_restrictions(self):
        """Test action economy restrictions from conditions."""
        # No conditions - can do everything
        actions = self.stat_service.can_take_actions(self.test_character_id)
        self.assertTrue(actions["actions"])
        self.assertTrue(actions["bonus_actions"])
        self.assertTrue(actions["reactions"])
        self.assertTrue(actions["movement"])
        self.assertEqual(len(actions["restrictions"]), 0)

        # Add incapacitated (no actions, bonus actions, or reactions)
        incapacitated = ActiveCondition(
            condition_type=ConditionType.INCAPACITATED,
            source="Hypnotic Pattern",
            duration_type="minutes",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.test_character_id, incapacitated)

        actions = self.stat_service.can_take_actions(self.test_character_id)
        self.assertFalse(actions["actions"])
        self.assertFalse(actions["bonus_actions"])
        self.assertFalse(actions["reactions"])
        self.assertTrue(actions["movement"])  # Can still move when just incapacitated
        self.assertGreater(len(actions["restrictions"]), 0)

        # Add paralyzed (also stops movement)
        paralyzed = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.test_character_id, paralyzed)

        actions = self.stat_service.can_take_actions(self.test_character_id)
        self.assertFalse(actions["actions"])
        self.assertFalse(actions["bonus_actions"])
        self.assertFalse(actions["reactions"])
        self.assertFalse(actions["movement"])  # Now can't move either

    def test_exhaustion_penalties(self):
        """Test exhaustion level penalties across all systems."""
        # Test different exhaustion levels
        for level in range(1, 7):
            # Clear previous conditions
            self.condition_manager.clear_all_conditions(self.test_character_id)

            # Add exhaustion at this level
            exhaustion = ActiveCondition(
                condition_type=ConditionType.EXHAUSTION,
                source=f"Test Level {level}",
                duration_type="permanent",
                exhaustion_level=level
            )
            self.condition_manager.add_condition(self.test_character_id, exhaustion)

            expected_penalty = level * 2

            # Check attack roll penalty
            attack_mod = self.stat_service.get_attack_roll_modifier(self.test_character_id)
            self.assertEqual(attack_mod["penalty"], expected_penalty)

            # Check saving throw penalty
            save_mod = self.stat_service.get_saving_throw_modifier(self.test_character_id, "constitution")
            self.assertEqual(save_mod["penalty"], expected_penalty)

            # Check ability check penalty
            ability_mod = self.stat_service.get_ability_check_modifier(self.test_character_id, "strength")
            self.assertEqual(ability_mod["penalty"], expected_penalty)

            # Check speed reduction
            expected_speed = max(0, 30 - (level * 5))
            speed = self.stat_service.get_movement_speed_modifier(self.test_character_id, 30)
            self.assertEqual(speed, expected_speed)

    def test_comprehensive_stat_modifiers(self):
        """Test the comprehensive stat modifier function."""
        base_stats = {
            "movement_speed": 30,
            "armor_class": 15,
            "hit_points": 50
        }

        # Add multiple conditions
        conditions = [
            ActiveCondition(
                condition_type=ConditionType.POISONED,
                source="Test",
                duration_type="rounds",
                duration_remaining=3
            ),
            ActiveCondition(
                condition_type=ConditionType.EXHAUSTION,
                source="Test",
                duration_type="permanent",
                exhaustion_level=1
            )
        ]

        for condition in conditions:
            self.condition_manager.add_condition(self.test_character_id, condition)

        # Get comprehensive modifiers
        modified_stats = self.stat_service.get_all_stat_modifiers(self.test_character_id, base_stats)

        # Check that base stats are preserved
        self.assertEqual(modified_stats["armor_class"], 15)
        self.assertEqual(modified_stats["hit_points"], 50)

        # Check movement speed modification (exhaustion level 1 = -5 ft)
        self.assertEqual(modified_stats["movement_speed"], 25)

        # Check that condition modifiers are present
        self.assertIn("condition_modifiers", modified_stats)

        condition_mods = modified_stats["condition_modifiers"]

        # Attack rolls should have disadvantage (poisoned) and penalty (exhaustion)
        self.assertTrue(condition_mods["attack_rolls"]["disadvantage"])
        self.assertEqual(condition_mods["attack_rolls"]["penalty"], 2)

        # All saving throws should have disadvantage and penalty
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            save_mods = condition_mods["saving_throws"][ability]
            if ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                # Poisoned affects ability checks, exhaustion affects saves
                self.assertEqual(save_mods["penalty"], 2)  # Exhaustion penalty

    def test_damage_resistances_and_immunities(self):
        """Test damage resistance and immunity from conditions."""
        # No conditions
        resistances = self.stat_service.get_damage_resistances(self.test_character_id)
        immunities = self.stat_service.get_damage_immunities(self.test_character_id)
        self.assertEqual(len(resistances), 0)
        self.assertEqual(len(immunities), 0)

        # Add petrified (resistance to all damage, immunity to poison/disease)
        petrified = ActiveCondition(
            condition_type=ConditionType.PETRIFIED,
            source="Medusa Gaze",
            duration_type="permanent"
        )
        self.condition_manager.add_condition(self.test_character_id, petrified)

        resistances = self.stat_service.get_damage_resistances(self.test_character_id)
        immunities = self.stat_service.get_damage_immunities(self.test_character_id)

        self.assertIn("all", resistances)
        self.assertIn("poison", immunities)
        self.assertIn("disease", immunities)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)