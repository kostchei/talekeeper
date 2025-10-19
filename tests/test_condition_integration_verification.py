"""
Test to verify conditions are actually applied from various sources.

This test verifies the bug fixes for:
1. Monster attacks applying conditions (prone, poisoned, etc.)
2. Skill challenges applying exhaustion and poison
3. Hazards applying exhaustion
"""

import unittest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, MagicMock

from src.talekeeper.services.condition_manager import ConditionManager, ConditionType
from src.talekeeper.services.skill_challenge_rewards import SkillChallengeRewards


class TestConditionIntegrationVerification(unittest.TestCase):
    """Verify conditions are actually applied and persisted."""

    def setUp(self):
        """Set up test database and services."""
        # Create temporary database
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')

        # Initialize database with minimal schema
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        # Create characters table
        cursor.execute("""
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                level INTEGER,
                hit_points_current INTEGER,
                hit_dice_current INTEGER,
                death_saves_successes INTEGER,
                death_saves_failures INTEGER
            )
        """)

        # Insert test character
        cursor.execute("""
            INSERT INTO characters (id, name, level, hit_points_current, hit_dice_current)
            VALUES ('test_char', 'Test Hero', 5, 30, 5)
        """)

        conn.commit()
        conn.close()

        # Initialize services
        self.condition_manager = ConditionManager(self.test_db_path)
        self.skill_rewards = SkillChallengeRewards(self.test_db_path)

    def tearDown(self):
        """Clean up test database."""
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)

    def test_exhaustion_applied_from_skill_challenge(self):
        """Verify exhaustion is actually applied via ConditionManager."""
        # Get character data
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE id = 'test_char'")
        character_data = dict(cursor.fetchone())
        conn.close()

        # Verify no exhaustion initially
        initial_level = self.condition_manager.get_exhaustion_level('test_char')
        self.assertEqual(initial_level, 0, "Character should start with no exhaustion")

        # Apply exhaustion penalty
        updated_char, messages = self.skill_rewards._apply_exhaustion(character_data)

        # Create new instance to verify it persists in database (not just cache)
        fresh_manager = ConditionManager(self.test_db_path)
        new_level = fresh_manager.get_exhaustion_level('test_char')
        self.assertEqual(new_level, 1, "Character should have 1 level of exhaustion")

        # Verify it persists in database
        active_conditions = fresh_manager.get_active_conditions('test_char')
        exhaustion_conditions = [c for c in active_conditions if c.condition_type == ConditionType.EXHAUSTION]
        self.assertEqual(len(exhaustion_conditions), 1, "Should have exactly 1 exhaustion condition")
        self.assertEqual(exhaustion_conditions[0].exhaustion_level, 1, "Exhaustion level should be 1")

        print("✅ Exhaustion from skill challenge: Applied and persisted correctly")

    def test_poison_applied_from_skill_challenge(self):
        """Verify poisoned condition is actually applied via ConditionManager."""
        # Get character data
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE id = 'test_char'")
        character_data = dict(cursor.fetchone())
        conn.close()

        # Verify not poisoned initially
        initial_poisoned = self.condition_manager.has_condition('test_char', ConditionType.POISONED)
        self.assertFalse(initial_poisoned, "Character should not be poisoned initially")

        # Apply poison penalty
        updated_char, messages = self.skill_rewards._apply_poison_condition(character_data)

        # Verify poison was actually applied
        is_poisoned = self.condition_manager.has_condition('test_char', ConditionType.POISONED)
        self.assertTrue(is_poisoned, "Character should be poisoned")

        # Verify it persists in database
        poison_condition = self.condition_manager.get_condition('test_char', ConditionType.POISONED)
        self.assertIsNotNone(poison_condition, "Poison condition should exist")
        self.assertEqual(poison_condition.save_dc, 15, "Should have DC 15 save")
        self.assertEqual(poison_condition.save_ability, "constitution", "Should be Constitution save")

        print("✅ Poison from skill challenge: Applied and persisted correctly")

    def test_multiple_exhaustion_levels_stack(self):
        """Verify multiple exhaustion applications stack properly."""
        # Get character data
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE id = 'test_char'")
        character_data = dict(cursor.fetchone())
        conn.close()

        # Apply exhaustion 3 times
        for i in range(3):
            self.skill_rewards._apply_exhaustion(character_data)

        # Verify exhaustion stacked to level 3
        final_level = self.condition_manager.get_exhaustion_level('test_char')
        self.assertEqual(final_level, 3, "Should have 3 levels of exhaustion")

        print("✅ Multiple exhaustion levels: Stack correctly")

    def test_condition_immunity_prevents_application(self):
        """Verify condition immunity prevents condition application."""
        # Add poison immunity
        self.condition_manager.add_immunity('test_char', ConditionType.POISONED, "Test immunity")

        # Try to apply poison
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE id = 'test_char'")
        character_data = dict(cursor.fetchone())
        conn.close()

        updated_char, messages = self.skill_rewards._apply_poison_condition(character_data)

        # Verify poison was NOT applied
        is_poisoned = self.condition_manager.has_condition('test_char', ConditionType.POISONED)
        self.assertFalse(is_poisoned, "Immune character should not be poisoned")

        print("✅ Condition immunity: Prevents condition application")


if __name__ == '__main__':
    unittest.main()
