# test
"""
Test suite for Rogue Abilities Service

Tests core Rogue functionality:
- Sneak Attack damage scaling
- Cunning Action usage
- Steady Aim mechanics
- Cunning Strike system
- Resource management
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock

from services.rogue_abilities import RogueAbilitiesService


class TestRogueAbilitiesService(unittest.TestCase):
    """Test the RogueAbilitiesService functionality."""

    def setUp(self):
        """Set up test database and service."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name

        # Create test database with basic structure
        self._create_test_database()

        # Initialize service
        self.service = RogueAbilitiesService(self.db_path)

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _create_test_database(self):
        """Create minimal test database structure."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create characters table
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    level INTEGER,
                    strength INTEGER DEFAULT 10,
                    dexterity INTEGER DEFAULT 10,
                    constitution INTEGER DEFAULT 10,
                    intelligence INTEGER DEFAULT 10,
                    wisdom INTEGER DEFAULT 10,
                    charisma INTEGER DEFAULT 10
                )
            """)

            # Create rogue_features table
            cursor.execute("""
                CREATE TABLE rogue_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER,
                    sneak_attack_dice INTEGER DEFAULT 1,
                    expertise_skills TEXT DEFAULT '[]',
                    cunning_action_available BOOLEAN DEFAULT FALSE,
                    uncanny_dodge_available BOOLEAN DEFAULT FALSE,
                    uncanny_dodge_used BOOLEAN DEFAULT FALSE,
                    evasion_available BOOLEAN DEFAULT FALSE,
                    reliable_talent_active BOOLEAN DEFAULT FALSE,
                    slippery_mind_active BOOLEAN DEFAULT FALSE,
                    elusive_active BOOLEAN DEFAULT FALSE,
                    stroke_of_luck_uses_current INTEGER DEFAULT 0,
                    stroke_of_luck_uses_max INTEGER DEFAULT 0,
                    sneak_attack_used_this_turn BOOLEAN DEFAULT FALSE,
                    steady_aim_active BOOLEAN DEFAULT FALSE,
                    expertise_count INTEGER DEFAULT 2,
                    subclass_features TEXT DEFAULT '{}'
                )
            """)

            # Create character_resources table
            cursor.execute("""
                CREATE TABLE character_resources (
                    id INTEGER PRIMARY KEY,
                    character_id TEXT,
                    resource_name TEXT,
                    current_uses INTEGER DEFAULT 0,
                    max_uses INTEGER DEFAULT 0,
                    rest_type TEXT,
                    source_class TEXT,
                    source_level INTEGER
                )
            """)

            conn.commit()

    def _create_test_rogue(self, level: int = 1, character_id: str = "test_rogue") -> str:
        """Create a test rogue character."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level, dexterity)
                VALUES (?, 'Test Rogue', 'rogue', ?, 16)
            """, (character_id, level))
            conn.commit()

        # Initialize rogue resources
        self.service.update_rogue_resources_for_level(character_id, level)
        return character_id

    def test_get_rogue_level(self):
        """Test getting rogue level for characters."""
        # Test with rogue character
        rogue_id = self._create_test_rogue(5)
        level = self.service.get_rogue_level(rogue_id)
        self.assertEqual(level, 5)

        # Test with non-rogue character
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level)
                VALUES ('fighter', 'Test Fighter', 'fighter', 3)
            """)
            conn.commit()

        level = self.service.get_rogue_level('fighter')
        self.assertEqual(level, 0)

    def test_sneak_attack_dice_scaling(self):
        """Test Sneak Attack dice scaling by level."""
        test_cases = [
            (1, 1), (2, 1), (3, 2), (4, 2), (5, 3),
            (6, 3), (7, 4), (8, 4), (9, 5), (10, 5),
            (11, 6), (12, 6), (13, 7), (14, 7), (15, 8),
            (16, 8), (17, 9), (18, 9), (19, 10), (20, 10)
        ]

        for level, expected_dice in test_cases:
            with self.subTest(level=level):
                actual_dice = self.service._calculate_sneak_attack_dice(level)
                self.assertEqual(actual_dice, expected_dice,
                               f"Level {level} should have {expected_dice}d6 Sneak Attack")

    def test_calculate_sneak_attack_damage(self):
        """Test Sneak Attack damage string calculation."""
        rogue_id = self._create_test_rogue(5)  # Should have 3d6
        damage_str = self.service.calculate_sneak_attack_damage(rogue_id)
        self.assertEqual(damage_str, "3d6")

    def test_update_rogue_resources_for_level(self):
        """Test resource updates for different levels."""
        rogue_id = self._create_test_rogue(1)

        # Test level 2 (Cunning Action)
        self.service.update_rogue_resources_for_level(rogue_id, 2)
        features = self.service.get_rogue_features(rogue_id)
        self.assertTrue(features['cunning_action_available'])
        self.assertFalse(features['uncanny_dodge_available'])

        # Test level 5 (Uncanny Dodge)
        self.service.update_rogue_resources_for_level(rogue_id, 5)
        features = self.service.get_rogue_features(rogue_id)
        self.assertTrue(features['uncanny_dodge_available'])
        self.assertEqual(features['sneak_attack_dice'], 3)

        # Test level 20 (Stroke of Luck)
        self.service.update_rogue_resources_for_level(rogue_id, 20)
        features = self.service.get_rogue_features(rogue_id)
        self.assertEqual(features['stroke_of_luck_uses_max'], 1)

    def test_cunning_action(self):
        """Test Cunning Action usage."""
        rogue_id = self._create_test_rogue(2)

        # Test valid actions
        for action in ['dash', 'disengage', 'hide']:
            with self.subTest(action=action):
                result = self.service.use_cunning_action(rogue_id, action)
                self.assertTrue(result['success'])
                self.assertIn(action, result['message'].lower())

        # Test invalid action
        result = self.service.use_cunning_action(rogue_id, 'invalid')
        self.assertFalse(result['success'])

        # Test level 1 rogue (no Cunning Action)
        level1_rogue = self._create_test_rogue(1, "level1_rogue")
        result = self.service.use_cunning_action(level1_rogue, 'dash')
        self.assertFalse(result['success'])

    def test_steady_aim(self):
        """Test Steady Aim usage."""
        rogue_id = self._create_test_rogue(3)

        # Test successful use
        result = self.service.use_steady_aim(rogue_id)
        self.assertTrue(result['success'])
        self.assertTrue(result['grants_advantage'])
        self.assertTrue(result['sets_speed_to_zero'])

        # Test level 2 rogue (no Steady Aim)
        level2_rogue = self._create_test_rogue(2, "level2_rogue")
        result = self.service.use_steady_aim(level2_rogue)
        self.assertFalse(result['success'])

    def test_uncanny_dodge(self):
        """Test Uncanny Dodge usage."""
        rogue_id = self._create_test_rogue(5)

        # Test successful use
        result = self.service.use_uncanny_dodge(rogue_id, 20)
        self.assertTrue(result['success'])
        self.assertEqual(result['original_damage'], 20)
        self.assertEqual(result['reduced_damage'], 10)
        self.assertEqual(result['damage_prevented'], 10)

        # Test already used this turn
        result = self.service.use_uncanny_dodge(rogue_id, 15)
        self.assertFalse(result['success'])

        # Test level 4 rogue (no Uncanny Dodge)
        level4_rogue = self._create_test_rogue(4, "level4_rogue")
        result = self.service.use_uncanny_dodge(level4_rogue, 10)
        self.assertFalse(result['success'])

    def test_reliable_talent(self):
        """Test Reliable Talent application."""
        rogue_id = self._create_test_rogue(7)

        # Test rolls that should be modified
        for roll in range(1, 10):
            with self.subTest(roll=roll):
                result = self.service.apply_reliable_talent(rogue_id, roll, 'stealth')
                self.assertEqual(result['modified_roll'], 10)
                self.assertTrue(result['reliable_talent_applied'])

        # Test rolls that shouldn't be modified
        for roll in range(10, 21):
            with self.subTest(roll=roll):
                result = self.service.apply_reliable_talent(rogue_id, roll, 'stealth')
                self.assertEqual(result['modified_roll'], roll)
                self.assertFalse(result['reliable_talent_applied'])

    def test_stroke_of_luck(self):
        """Test Stroke of Luck usage."""
        rogue_id = self._create_test_rogue(20)

        # Test successful use
        result = self.service.use_stroke_of_luck(rogue_id, 5)
        self.assertTrue(result['success'])
        self.assertEqual(result['original_roll'], 5)
        self.assertEqual(result['new_roll'], 20)

        # Test no uses remaining
        result = self.service.use_stroke_of_luck(rogue_id, 10)
        self.assertFalse(result['success'])

        # Test level 19 rogue (no Stroke of Luck)
        level19_rogue = self._create_test_rogue(19, "level19_rogue")
        result = self.service.use_stroke_of_luck(level19_rogue, 5)
        self.assertFalse(result['success'])

    def test_rest_rogue_resources(self):
        """Test resource restoration on rest."""
        rogue_id = self._create_test_rogue(5)

        # Use Uncanny Dodge to mark it as used
        self.service.use_uncanny_dodge(rogue_id, 10)

        # Short rest should reset per-turn abilities
        self.service.rest_rogue_resources(rogue_id, 'short')
        features = self.service.get_rogue_features(rogue_id)
        self.assertFalse(features['uncanny_dodge_used'])

    def test_weapon_eligibility_for_sneak_attack(self):
        """Test weapon eligibility for Sneak Attack."""
        # Test finesse weapon
        finesse_weapon = {'weapon_properties': 'finesse, light'}
        self.assertTrue(self.service._is_sneak_attack_weapon(finesse_weapon))

        # Test ranged weapon
        ranged_weapon = {'weapon_type': 'ranged', 'name': 'shortbow'}
        self.assertTrue(self.service._is_sneak_attack_weapon(ranged_weapon))

        # Test non-eligible weapon
        heavy_weapon = {'weapon_properties': 'heavy, two-handed', 'weapon_type': 'melee'}
        self.assertFalse(self.service._is_sneak_attack_weapon(heavy_weapon))

    def test_sneak_attack_eligibility(self):
        """Test Sneak Attack eligibility checks."""
        rogue_id = self._create_test_rogue(3)

        # Mock weapon
        weapon = {'weapon_properties': 'finesse', 'name': 'rapier'}

        # Test with advantage
        context = {'weapon': weapon, 'has_advantage': True, 'has_disadvantage': False}
        result = self.service.check_sneak_attack_eligibility(rogue_id, 'target1', context)
        self.assertTrue(result['eligible'])
        self.assertEqual(result['source'], 'advantage')

        # Test with disadvantage (should fail)
        context = {'weapon': weapon, 'has_advantage': False, 'has_disadvantage': True}
        result = self.service.check_sneak_attack_eligibility(rogue_id, 'target1', context)
        self.assertFalse(result['eligible'])

    def test_get_rogue_features(self):
        """Test getting rogue features."""
        rogue_id = self._create_test_rogue(7)
        features = self.service.get_rogue_features(rogue_id)

        # Check expected features are present
        self.assertIn('character_id', features)
        self.assertIn('sneak_attack_dice', features)
        self.assertIn('cunning_action_available', features)
        self.assertTrue(features['evasion_available'])
        self.assertTrue(features['reliable_talent_active'])


if __name__ == '__main__':
    unittest.main()