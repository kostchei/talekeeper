#test
"""
Test suite for the Condition Manager system.
Tests the condition system in isolation before integration.
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
    ConditionManager, ConditionType, ActiveCondition, ConditionEffects
)


class TestConditionManager(unittest.TestCase):
    """Test the condition management system."""

    def setUp(self):
        """Create a test database and condition manager."""
        # Create temporary database
        self.test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.test_db_path = self.test_db.name
        self.test_db.close()

        # Create test database schema
        self._create_test_schema()

        # Create condition manager with test database
        self.condition_manager = ConditionManager(self.test_db_path)

        # Test character ID
        self.test_character_id = "test_barbarian_001"

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
                    level INTEGER
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, level)
                VALUES ('test_barbarian_001', 'Test Barbarian', 5)
            """)
            conn.commit()

    def test_condition_type_enum(self):
        """Test that all D&D 2024 conditions are defined."""
        expected_conditions = [
            'BLINDED', 'CHARMED', 'DEAFENED', 'EXHAUSTION', 'FRIGHTENED',
            'GRAPPLED', 'INCAPACITATED', 'INVISIBLE', 'PARALYZED', 'PETRIFIED',
            'POISONED', 'PRONE', 'RESTRAINED', 'STUNNED', 'UNCONSCIOUS'
        ]

        for condition_name in expected_conditions:
            self.assertTrue(hasattr(ConditionType, condition_name),
                          f"Missing condition: {condition_name}")

    def test_add_simple_condition(self):
        """Test adding a simple condition."""
        condition = ActiveCondition(
            condition_type=ConditionType.POISONED,
            source="Poison Dart Trap",
            duration_type="minutes",
            duration_remaining=10
        )

        result = self.condition_manager.add_condition(self.test_character_id, condition)
        self.assertTrue(result)

        # Verify condition was added
        active = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].condition_type, ConditionType.POISONED)

    def test_conditions_dont_stack(self):
        """Test that conditions don't stack (except exhaustion)."""
        condition1 = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Dragon Fear",
            duration_type="rounds",
            duration_remaining=3
        )

        condition2 = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Wraith",
            duration_type="rounds",
            duration_remaining=5
        )

        # Add first condition
        result1 = self.condition_manager.add_condition(self.test_character_id, condition1)
        self.assertTrue(result1)

        # Try to add second condition of same type
        result2 = self.condition_manager.add_condition(self.test_character_id, condition2)
        self.assertFalse(result2)  # Should fail

        # Verify only one condition exists
        active = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].source, "Dragon Fear")  # Original source

    def test_exhaustion_stacking(self):
        """Test that exhaustion levels stack."""
        # Add first exhaustion level
        condition1 = ActiveCondition(
            condition_type=ConditionType.EXHAUSTION,
            source="Forced March",
            duration_type="permanent",
            exhaustion_level=1
        )
        self.condition_manager.add_condition(self.test_character_id, condition1)

        level = self.condition_manager.get_exhaustion_level(self.test_character_id)
        self.assertEqual(level, 1)

        # Add another exhaustion level
        condition2 = ActiveCondition(
            condition_type=ConditionType.EXHAUSTION,
            source="Starvation",
            duration_type="permanent",
            exhaustion_level=1
        )
        self.condition_manager.add_condition(self.test_character_id, condition2)

        level = self.condition_manager.get_exhaustion_level(self.test_character_id)
        self.assertEqual(level, 2)  # Should stack to 2

    def test_exhaustion_death_at_level_6(self):
        """Test exhaustion caps at level 6 (death)."""
        # Add 6 levels of exhaustion
        for i in range(7):  # Try to add 7
            condition = ActiveCondition(
                condition_type=ConditionType.EXHAUSTION,
                source=f"Test {i}",
                duration_type="permanent",
                exhaustion_level=1
            )
            self.condition_manager.add_condition(self.test_character_id, condition)

        level = self.condition_manager.get_exhaustion_level(self.test_character_id)
        self.assertEqual(level, 6)  # Should cap at 6

    def test_incapacitating_conditions(self):
        """Test detection of incapacitating conditions."""
        # Initially no incapacitating conditions
        self.assertFalse(self.condition_manager.has_incapacitating_condition(self.test_character_id))

        # Add incapacitated condition
        condition = ActiveCondition(
            condition_type=ConditionType.INCAPACITATED,
            source="Test",
            duration_type="rounds",
            duration_remaining=3
        )
        self.condition_manager.add_condition(self.test_character_id, condition)
        self.assertTrue(self.condition_manager.has_incapacitating_condition(self.test_character_id))

        # Remove incapacitated
        self.condition_manager.remove_condition(self.test_character_id, ConditionType.INCAPACITATED)
        self.assertFalse(self.condition_manager.has_incapacitating_condition(self.test_character_id))

        # Add paralyzed (which includes incapacitated)
        paralyzed = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.test_character_id, paralyzed)
        self.assertTrue(self.condition_manager.has_incapacitating_condition(self.test_character_id))

        # Verify stunned is also incapacitating
        self.condition_manager.remove_condition(self.test_character_id, ConditionType.PARALYZED)
        stunned = ActiveCondition(
            condition_type=ConditionType.STUNNED,
            source="Monk Stunning Strike",
            duration_type="rounds",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.test_character_id, stunned)
        self.assertTrue(self.condition_manager.has_incapacitating_condition(self.test_character_id))

    def test_condition_immunity(self):
        """Test condition immunity system."""
        # Add immunity to frightened
        self.condition_manager.add_immunity(
            self.test_character_id,
            ConditionType.FRIGHTENED,
            "Berserker Mindless Rage"
        )

        # Try to add frightened condition
        condition = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Dragon Fear",
            duration_type="save_ends",
            save_dc=15,
            save_ability="wisdom"
        )
        result = self.condition_manager.add_condition(self.test_character_id, condition)
        self.assertFalse(result)  # Should fail due to immunity

        # Verify no condition was added
        active = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(active), 0)

        # Remove immunity
        self.condition_manager.remove_immunity(
            self.test_character_id,
            ConditionType.FRIGHTENED,
            "Berserker Mindless Rage"
        )

        # Now condition can be added
        result = self.condition_manager.add_condition(self.test_character_id, condition)
        self.assertTrue(result)

    def test_remove_condition_with_immunity(self):
        """Test that gaining immunity removes existing condition."""
        # Add frightened condition
        condition = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Wraith",
            duration_type="rounds",
            duration_remaining=3
        )
        self.condition_manager.add_condition(self.test_character_id, condition)
        self.assertTrue(self.condition_manager.has_condition(self.test_character_id, ConditionType.FRIGHTENED))

        # Add immunity (should remove existing condition)
        self.condition_manager.add_immunity(
            self.test_character_id,
            ConditionType.FRIGHTENED,
            "Rage Activated"
        )

        # Condition should be removed
        self.assertFalse(self.condition_manager.has_condition(self.test_character_id, ConditionType.FRIGHTENED))

    def test_condition_duration_tracking(self):
        """Test duration countdown on turns."""
        # Add condition with duration
        condition = ActiveCondition(
            condition_type=ConditionType.PRONE,
            source="Tripped",
            duration_type="rounds",
            duration_remaining=3
        )
        self.condition_manager.add_condition(self.test_character_id, condition)

        # Process turn start - should reduce duration
        messages = self.condition_manager.process_turn_start(self.test_character_id, 1)

        # Check duration reduced
        prone_condition = self.condition_manager.get_condition(self.test_character_id, ConditionType.PRONE)
        self.assertEqual(prone_condition.duration_remaining, 2)

        # Process more turns
        self.condition_manager.process_turn_start(self.test_character_id, 2)
        prone_condition = self.condition_manager.get_condition(self.test_character_id, ConditionType.PRONE)
        self.assertEqual(prone_condition.duration_remaining, 1)

        # Final turn - condition should be removed
        messages = self.condition_manager.process_turn_start(self.test_character_id, 3)
        self.assertFalse(self.condition_manager.has_condition(self.test_character_id, ConditionType.PRONE))
        self.assertIn("Prone ended", messages)

    def test_save_ends_conditions(self):
        """Test conditions that require saves."""
        # Add condition with save
        condition = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Intimidating Presence",
            duration_type="save_ends",
            save_dc=15,
            save_ability="wisdom",
            save_frequency="end_of_turn"
        )
        self.condition_manager.add_condition(self.test_character_id, condition)

        # Process turn end - should prompt for save
        messages = self.condition_manager.process_turn_end(self.test_character_id, 1)
        self.assertIn("Make a wisdom save (DC 15) for frightened", messages)

    def test_condition_summary(self):
        """Test readable condition summary."""
        # No conditions
        summary = self.condition_manager.get_condition_summary(self.test_character_id)
        self.assertEqual(summary, "No active conditions")

        # Add multiple conditions
        self.condition_manager.add_condition(self.test_character_id, ActiveCondition(
            condition_type=ConditionType.POISONED,
            source="Poison",
            duration_type="minutes",
            duration_remaining=10
        ))
        self.condition_manager.add_condition(self.test_character_id, ActiveCondition(
            condition_type=ConditionType.PRONE,
            source="Tripped",
            duration_type="rounds",
            duration_remaining=2
        ))
        self.condition_manager.add_condition(self.test_character_id, ActiveCondition(
            condition_type=ConditionType.EXHAUSTION,
            source="Fatigue",
            duration_type="permanent",
            exhaustion_level=2
        ))

        summary = self.condition_manager.get_condition_summary(self.test_character_id)
        self.assertIn("Poisoned", summary)
        self.assertIn("Prone [2 rounds]", summary)
        self.assertIn("Exhaustion (Level 2)", summary)

    def test_clear_all_conditions(self):
        """Test clearing all conditions."""
        # Add multiple conditions
        conditions = [
            ActiveCondition(condition_type=ConditionType.POISONED, source="Test", duration_type="rounds", duration_remaining=5),
            ActiveCondition(condition_type=ConditionType.BLINDED, source="Test", duration_type="minutes", duration_remaining=1),
            ActiveCondition(condition_type=ConditionType.RESTRAINED, source="Test", duration_type="permanent")
        ]

        for condition in conditions:
            self.condition_manager.add_condition(self.test_character_id, condition)

        # Verify conditions exist
        active = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(active), 3)

        # Clear all
        self.condition_manager.clear_all_conditions(self.test_character_id, "Greater Restoration")

        # Verify all cleared
        active = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(active), 0)

    def test_condition_effects_lookup(self):
        """Test looking up mechanical effects of conditions."""
        # Test paralyzed effects
        effects = ConditionEffects.get_effects(ConditionType.PARALYZED)
        self.assertTrue(effects['has_incapacitated'])
        self.assertEqual(effects['movement_speed'], 0)
        self.assertTrue(effects['critical_hits_within_5ft'])

        # Test exhaustion effects
        effects = ConditionEffects.get_effects(ConditionType.EXHAUSTION)
        self.assertTrue(effects['levels'])
        self.assertEqual(effects['d20_test_penalty'], 'minus_2_per_level')
        self.assertTrue(effects['death_at_level_6'])

    def test_unconscious_condition_effects(self):
        """Test that unconscious has all correct nested conditions."""
        effects = ConditionEffects.get_effects(ConditionType.UNCONSCIOUS)
        self.assertTrue(effects['has_incapacitated'])
        self.assertTrue(effects['has_prone'])
        self.assertTrue(effects['drops_held_items'])
        self.assertEqual(effects['movement_speed'], 0)

    def test_condition_caching(self):
        """Test that condition caching works correctly."""
        # Add condition
        condition = ActiveCondition(
            condition_type=ConditionType.GRAPPLED,
            source="Monster Grapple",
            duration_type="until_escape"
        )
        self.condition_manager.add_condition(self.test_character_id, condition)

        # First call should query DB and cache
        conditions1 = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(conditions1), 1)

        # Second call should use cache
        conditions2 = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(conditions1, conditions2)

        # Adding new condition should clear cache
        new_condition = ActiveCondition(
            condition_type=ConditionType.PRONE,
            source="Knocked Down",
            duration_type="rounds",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.test_character_id, new_condition)

        # Should get fresh data
        conditions3 = self.condition_manager.get_active_conditions(self.test_character_id)
        self.assertEqual(len(conditions3), 2)


class TestDangerSenseIntegration(unittest.TestCase):
    """Test Danger Sense integration with conditions."""

    def setUp(self):
        """Set up for Danger Sense tests."""
        self.test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.test_db_path = self.test_db.name
        self.test_db.close()

        # Create test schema
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    class_id TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id)
                VALUES ('barbarian_test', 'Test Barbarian', 5, 'barbarian')
            """)
            conn.commit()

        self.condition_manager = ConditionManager(self.test_db_path)
        self.barbarian_id = 'barbarian_test'

    def tearDown(self):
        """Clean up."""
        try:
            os.unlink(self.test_db_path)
        except:
            pass

    def test_danger_sense_with_no_conditions(self):
        """Danger Sense should work when not incapacitated."""
        # No conditions - should not be incapacitated
        self.assertFalse(self.condition_manager.has_incapacitating_condition(self.barbarian_id))

    def test_danger_sense_blocked_by_incapacitated(self):
        """Danger Sense should be blocked by incapacitated."""
        # Add incapacitated
        condition = ActiveCondition(
            condition_type=ConditionType.INCAPACITATED,
            source="Some Effect",
            duration_type="rounds",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.barbarian_id, condition)

        # Should be incapacitated
        self.assertTrue(self.condition_manager.has_incapacitating_condition(self.barbarian_id))

    def test_danger_sense_blocked_by_paralyzed(self):
        """Danger Sense should be blocked by paralyzed (includes incapacitated)."""
        # Add paralyzed
        condition = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )
        self.condition_manager.add_condition(self.barbarian_id, condition)

        # Should be incapacitated (paralyzed includes incapacitated)
        self.assertTrue(self.condition_manager.has_incapacitating_condition(self.barbarian_id))

    def test_danger_sense_not_blocked_by_frightened(self):
        """Danger Sense should work when only frightened."""
        # Add frightened
        condition = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Dragon Fear",
            duration_type="save_ends",
            save_dc=15,
            save_ability="wisdom"
        )
        self.condition_manager.add_condition(self.barbarian_id, condition)

        # Should NOT be incapacitated
        self.assertFalse(self.condition_manager.has_incapacitating_condition(self.barbarian_id))


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)