#test
"""
Unit tests for WeaponAttackService.

Tests weapon attack calculations, fighting style effects, feat applications,
and weapon mastery effects.
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch

from services.weapon_attack_service import WeaponAttackService


class TestWeaponAttackService(unittest.TestCase):
    """Test cases for WeaponAttackService."""

    def setUp(self):
        """Set up test database and service."""
        self.test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.test_db.close()
        self.db_path = self.test_db.name

        # Initialize test database schema
        self._create_test_schema()
        self._insert_test_data()

        self.service = WeaponAttackService(self.db_path)

    def tearDown(self):
        """Clean up test database."""
        os.unlink(self.db_path)

    def _create_test_schema(self):
        """Create minimal database schema for testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                class_id TEXT,
                level INTEGER,
                strength INTEGER,
                dexterity INTEGER,
                constitution INTEGER,
                intelligence INTEGER,
                wisdom INTEGER,
                charisma INTEGER,
                weapon_mastery_count INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE character_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT,
                feature_name TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(id)
            )
        """)

        conn.commit()
        conn.close()

    def _insert_test_data(self):
        """Insert test character data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Test fighter with fighting styles
        cursor.execute("""
            INSERT INTO characters (id, class_id, level, strength, dexterity, constitution,
                                  intelligence, wisdom, charisma, weapon_mastery_count)
            VALUES ('test_fighter', 'fighter', 5, 16, 14, 15, 10, 12, 13, -1)
        """)

        # Add fighting styles
        cursor.execute("""
            INSERT INTO character_features (character_id, feature_name)
            VALUES ('test_fighter', 'Fighting Style: Great Weapon Fighting')
        """)

        cursor.execute("""
            INSERT INTO character_features (character_id, feature_name)
            VALUES ('test_fighter', 'Fighting Style: Dueling')
        """)

        # Test character with Savage Attacker
        cursor.execute("""
            INSERT INTO characters (id, class_id, level, strength, dexterity, constitution,
                                  intelligence, wisdom, charisma, weapon_mastery_count)
            VALUES ('test_barbarian', 'barbarian', 3, 18, 12, 16, 8, 10, 11, -1)
        """)

        cursor.execute("""
            INSERT INTO character_features (character_id, feature_name)
            VALUES ('test_barbarian', 'Savage Attacker')
        """)

        # Test non-mastery class (wizard)
        cursor.execute("""
            INSERT INTO characters (id, class_id, level, strength, dexterity, constitution,
                                  intelligence, wisdom, charisma, weapon_mastery_count)
            VALUES ('test_wizard', 'wizard', 5, 10, 14, 12, 18, 16, 13, 0)
        """)

        conn.commit()
        conn.close()

    def test_parse_damage_dice(self):
        """Test damage dice parsing."""
        # Standard dice
        self.assertEqual(self.service._parse_damage_dice('1d6'), (1, 6))
        self.assertEqual(self.service._parse_damage_dice('2d8'), (2, 8))
        self.assertEqual(self.service._parse_damage_dice('1d12'), (1, 12))

        # Dice with modifiers
        self.assertEqual(self.service._parse_damage_dice('1d8+2'), (1, 8))
        self.assertEqual(self.service._parse_damage_dice('2d6-1'), (2, 6))

    def test_parse_damage_dice_invalid_formats(self):
        """Test that invalid damage dice formats raise ValueError."""
        # Invalid formats should raise ValueError
        with self.assertRaises(ValueError) as cm:
            self.service._parse_damage_dice('invalid')
        self.assertIn("Invalid number", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            self.service._parse_damage_dice('')
        self.assertIn("cannot be empty", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            self.service._parse_damage_dice('123')
        self.assertIn("must contain 'd'", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            self.service._parse_damage_dice('d6')
        self.assertIn("Missing number of dice", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            self.service._parse_damage_dice('2d')
        self.assertIn("Missing die size", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            self.service._parse_damage_dice('0d6')
        self.assertIn("must be positive", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            self.service._parse_damage_dice('2d0')
        self.assertIn("must be positive", str(cm.exception))

    def test_get_character_fighting_styles(self):
        """Test retrieving character fighting styles."""
        styles = self.service.get_character_fighting_styles('test_fighter')
        self.assertIn('Fighting Style: Great Weapon Fighting', styles)
        self.assertIn('Fighting Style: Dueling', styles)

        # Non-existent character
        styles = self.service.get_character_fighting_styles('nonexistent')
        self.assertEqual(styles, [])

    def test_great_weapon_fighting(self):
        """Test Great Weapon Fighting style effects."""
        weapon = {
            'name': 'Greatsword',
            'weapon_properties': 'two-handed, heavy',
            'damage_dice': '2d6'
        }

        character = {'id': 'test_fighter'}
        fighting_styles = ['Fighting Style: Great Weapon Fighting']

        # Test with rolls that should be modified (1s and 2s become 3s)
        dice_rolls = [1, 2, 4, 6]
        modified_rolls, description = self.service.apply_fighting_style_effects(
            dice_rolls, fighting_styles, weapon, character
        )

        # 1s and 2s should become 3s
        self.assertEqual(modified_rolls, [3, 3, 4, 6])
        self.assertIn('Great Weapon Fighting', description)
        self.assertIn('2', description)  # Should mention 2 rolls were changed

    def test_dueling_damage_bonus(self):
        """Test Dueling fighting style damage bonus."""
        weapon = {
            'name': 'Longsword',
            'weapon_properties': 'versatile',
            'damage_dice': '1d8'
        }

        character = {'id': 'test_fighter'}
        fighting_styles = ['Fighting Style: Dueling']

        # Should get +2 damage for one-handed weapon
        bonus = self.service.get_fighting_style_damage_bonus(
            weapon, character, 'main_hand', fighting_styles
        )
        self.assertEqual(bonus, 2)

        # Should not get bonus for off-hand attack (implies two weapons)
        bonus = self.service.get_fighting_style_damage_bonus(
            weapon, character, 'off_hand', fighting_styles
        )
        self.assertEqual(bonus, 0)

        # Two-handed weapon should not get dueling bonus
        two_handed_weapon = {
            'name': 'Greatsword',
            'weapon_properties': 'two-handed, heavy',
            'damage_dice': '2d6'
        }

        bonus = self.service.get_fighting_style_damage_bonus(
            two_handed_weapon, character, 'main_hand', fighting_styles
        )
        self.assertEqual(bonus, 0)

    def test_archery_attack_bonus(self):
        """Test Archery fighting style attack bonus."""
        ranged_weapon = {
            'name': 'Longbow',
            'weapon_properties': 'ranged, two-handed',
            'damage_dice': '1d8'
        }

        character = {'id': 'test_fighter'}

        # Mock the character having Archery fighting style
        with patch.object(self.service, 'get_character_fighting_styles') as mock_styles:
            mock_styles.return_value = ['Fighting Style: Archery']

            bonus = self.service.get_fighting_style_attack_bonus(ranged_weapon, character)
            self.assertEqual(bonus, 2)

        # Melee weapon should not get archery bonus
        melee_weapon = {
            'name': 'Sword',
            'weapon_properties': 'versatile',
            'damage_dice': '1d8'
        }

        with patch.object(self.service, 'get_character_fighting_styles') as mock_styles:
            mock_styles.return_value = ['Fighting Style: Archery']

            bonus = self.service.get_fighting_style_attack_bonus(melee_weapon, character)
            self.assertEqual(bonus, 0)

    @patch('random.randint')
    def test_savage_attacker_feat(self, mock_random):
        """Test Savage Attacker feat application."""
        # Mock dice rolls: first set [3, 4], second set [5, 6]
        mock_random.side_effect = [5, 6]  # Second roll is better

        character = {'id': 'test_barbarian', 'feats': ['Savage Attacker']}
        first_rolls = [3, 4]  # Total: 7

        result_rolls, description = self.service.apply_savage_attacker(
            first_rolls, 2, 6, character, is_first_attack=True
        )

        # Should use the better second roll
        self.assertEqual(result_rolls, [5, 6])
        self.assertIn('rerolled for 11', description)
        self.assertIn('was 7', description)

    @patch('random.randint')
    def test_savage_attacker_first_roll_better(self, mock_random):
        """Test Savage Attacker when first roll is better."""
        # Mock dice rolls: second set [1, 2] (worse than first)
        mock_random.side_effect = [1, 2]

        character = {'id': 'test_barbarian', 'feats': ['Savage Attacker']}
        first_rolls = [5, 6]  # Total: 11

        result_rolls, description = self.service.apply_savage_attacker(
            first_rolls, 2, 6, character, is_first_attack=True
        )

        # Should keep the original better roll
        self.assertEqual(result_rolls, [5, 6])
        self.assertIn('kept original 11', description)
        self.assertIn('reroll was 3', description)

    def test_savage_attacker_not_first_attack(self):
        """Test Savage Attacker doesn't apply if not first attack."""
        character = {'id': 'test_barbarian', 'feats': ['Savage Attacker']}
        dice_rolls = [3, 4]

        result_rolls, description = self.service.apply_savage_attacker(
            dice_rolls, 2, 6, character, is_first_attack=False
        )

        # Should return unchanged
        self.assertEqual(result_rolls, dice_rolls)
        self.assertEqual(description, '')

    def test_weapon_mastery_unlimited_access(self):
        """Test characters with unlimited weapon mastery access."""
        # Fighter should have unlimited access
        self.assertTrue(self.service.has_character_unlimited_mastery('test_fighter'))

        # Barbarian should have unlimited access
        self.assertTrue(self.service.has_character_unlimited_mastery('test_barbarian'))

        # Wizard should NOT have unlimited access
        self.assertFalse(self.service.has_character_unlimited_mastery('test_wizard'))

    def test_non_mastery_class_no_errors(self):
        """Test that non-mastery classes don't cause errors when weapons lack mastery."""
        weapon = {
            'name': 'Test Weapon',
            'weapon_properties': 'simple',
            'damage_dice': '1d6',
            'damage_type': 'bludgeoning'
            # Deliberately missing mastery_property
        }

        character = {'id': 'test_wizard', 'class_id': 'wizard', 'level': 5}

        # Should return empty effects without throwing error
        effects = self.service.apply_weapon_mastery_effects(
            weapon, character, target=None, hit=True, damage_total=8
        )

        self.assertEqual(effects, {})

    def test_mastery_class_requires_mastery_property(self):
        """Test that mastery classes require weapons to have mastery property."""
        weapon = {
            'name': 'Test Weapon',
            'weapon_properties': 'simple',
            'damage_dice': '1d6',
            'damage_type': 'bludgeoning'
            # Deliberately missing mastery_property
        }

        character = {'id': 'test_fighter', 'class_id': 'fighter', 'level': 5}

        # Should throw ValueError for missing mastery
        with self.assertRaises(ValueError) as cm:
            self.service.apply_weapon_mastery_effects(
                weapon, character, target=None, hit=True, damage_total=8
            )

        self.assertIn("missing mastery_property", str(cm.exception))

    def test_weapon_mastery_effects_cleave(self):
        """Test Cleave weapon mastery effect."""
        weapon = {
            'name': 'Handaxe',
            'mastery_property': 'Cleave'
        }

        character = {'id': 'test_fighter', 'strength': 16}  # +3 STR mod

        effects = self.service._apply_specific_mastery(
            'Cleave', 'Handaxe', hit=True, damage_total=8, character=character
        )

        self.assertIn('cleave', effects)
        self.assertEqual(effects['cleave']['damage'], 3)  # STR modifier
        self.assertIn('second creature', effects['cleave']['description'])

    def test_weapon_mastery_effects_graze(self):
        """Test Graze weapon mastery effect."""
        weapon = {'name': 'Pike', 'mastery_property': 'Graze'}
        character = {'id': 'test_fighter', 'strength': 16, 'dexterity': 14}  # +3 STR, +2 DEX

        effects = self.service._apply_specific_mastery(
            'Graze', 'Pike', hit=False, damage_total=0, character=character
        )

        self.assertIn('graze', effects)
        self.assertEqual(effects['graze']['damage'], 3)  # STR modifier (not finesse)
        self.assertIn('damage on a miss', effects['graze']['description'])

    def test_weapon_mastery_effects_topple(self):
        """Test Topple weapon mastery save DC calculation."""
        character = {
            'id': 'test_fighter',
            'level': 5,
            'strength': 16  # +3 STR mod, +3 prof bonus at level 5
        }

        effects = self.service._apply_specific_mastery(
            'Topple', 'Warhammer', hit=True, damage_total=10, character=character
        )

        self.assertIn('topple', effects)
        expected_dc = 8 + 3 + 3  # 8 + prof + STR = 14
        self.assertEqual(effects['topple']['save_dc'], expected_dc)
        self.assertIn('Constitution save', effects['topple']['description'])


if __name__ == '__main__':
    unittest.main()