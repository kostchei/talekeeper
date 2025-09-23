"""
Test Concentration System - Phase 4.2 Testing
Tests concentration mechanics for D&D 2024
"""

import unittest
import sqlite3
import tempfile
import os
from services.concentration_system import ConcentrationSystem

class TestConcentrationSystem(unittest.TestCase):
    def setUp(self):
        """Set up test database with minimal data."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name

        # Create test database schema
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create required tables
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_name TEXT,
                    level INTEGER,
                    current_hp INTEGER DEFAULT 10
                )
            """)

            cursor.execute("""
                CREATE TABLE spells (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    school TEXT NOT NULL,
                    casting_time TEXT NOT NULL,
                    range_value TEXT NOT NULL,
                    components TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    concentration BOOLEAN DEFAULT FALSE,
                    description TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE character_concentration (
                    character_id TEXT PRIMARY KEY,
                    spell_id TEXT,
                    spell_level INTEGER,
                    start_time TEXT DEFAULT (datetime('now')),
                    duration_remaining INTEGER,
                    concentration_dc INTEGER DEFAULT 10,
                    FOREIGN KEY (character_id) REFERENCES characters(id),
                    FOREIGN KEY (spell_id) REFERENCES spells(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE character_conditions (
                    character_id TEXT NOT NULL,
                    condition_name TEXT NOT NULL,
                    PRIMARY KEY (character_id, condition_name)
                )
            """)

            cursor.execute("""
                CREATE TABLE character_features (
                    character_id TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    PRIMARY KEY (character_id, feature_name)
                )
            """)

            # Insert test data
            cursor.execute("""
                INSERT INTO characters (id, name, class_name, level, current_hp)
                VALUES ('test_wizard', 'Test Wizard', 'wizard', 5, 25)
            """)

            cursor.execute("""
                INSERT INTO characters (id, name, class_name, level, current_hp)
                VALUES ('test_fighter', 'Test Fighter', 'fighter', 5, 45)
            """)

            # Insert concentration spells
            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                  components, duration, concentration, description)
                VALUES ('hold_person', 'Hold Person', 2, 'Enchantment', '1 action', '60 feet',
                       'V, S, M', 'Concentration, up to 1 minute', 1,
                       'Paralyze a humanoid')
            """)

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                  components, duration, concentration, description)
                VALUES ('mage_armor', 'Mage Armor', 1, 'Abjuration', '1 action', 'Touch',
                       'V, S, M', '8 hours', 0,
                       'Provide magical protection')
            """)

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                  components, duration, concentration, description)
                VALUES ('web', 'Web', 2, 'Conjuration', '1 action', '60 feet',
                       'V, S, M', 'Concentration, up to 1 hour', 1,
                       'Create sticky webs')
            """)

            conn.commit()

        self.system = ConcentrationSystem(self.db_path)

    def tearDown(self):
        """Clean up test database."""
        if hasattr(self, 'system'):
            del self.system
        try:
            os.unlink(self.db_path)
        except (PermissionError, FileNotFoundError):
            pass

    def test_start_concentration_success(self):
        """Test successfully starting concentration on a spell."""
        result = self.system.start_concentration('test_wizard', 'hold_person', 2, 10)
        self.assertTrue(result, "Should be able to start concentration on Hold Person")

        # Verify concentration is active
        concentration = self.system.get_concentration_spell('test_wizard')
        self.assertIsNotNone(concentration, "Character should be concentrating")
        self.assertEqual(concentration['spell_name'], 'Hold Person')
        self.assertEqual(concentration['spell_level'], 2)
        self.assertEqual(concentration['duration_remaining'], 10)

    def test_start_concentration_non_concentration_spell(self):
        """Test trying to start concentration on a non-concentration spell."""
        result = self.system.start_concentration('test_wizard', 'mage_armor', 1, 10)
        self.assertFalse(result, "Should not be able to concentrate on non-concentration spell")

    def test_concentration_replaces_previous(self):
        """Test that new concentration replaces previous concentration."""
        # Start first concentration
        self.system.start_concentration('test_wizard', 'hold_person', 2, 10)

        # Start second concentration
        result = self.system.start_concentration('test_wizard', 'web', 2, 60)
        self.assertTrue(result, "Should be able to start new concentration")

        # Verify only the new concentration is active
        concentration = self.system.get_concentration_spell('test_wizard')
        self.assertEqual(concentration['spell_name'], 'Web')

    def test_end_concentration_voluntary(self):
        """Test voluntarily ending concentration."""
        # Start concentration
        self.system.start_concentration('test_wizard', 'hold_person', 2, 10)

        # End concentration
        result = self.system.end_concentration('test_wizard', "voluntary")
        self.assertTrue(result, "Should be able to end concentration")

        # Verify concentration is gone
        concentration = self.system.get_concentration_spell('test_wizard')
        self.assertIsNone(concentration, "Concentration should be ended")

    def test_concentration_save_success(self):
        """Test successful concentration saving throw."""
        # Start concentration
        self.system.start_concentration('test_wizard', 'hold_person', 2, 10)

        # Mock a low damage concentration save (should succeed most of the time)
        success, dc, roll = self.system.make_concentration_save('test_wizard', 8, 2)  # DC 10, roll + 2

        self.assertEqual(dc, 10, "DC should be 10 for 8 damage")
        self.assertIsInstance(roll, int, "Roll should be an integer")
        self.assertGreaterEqual(roll, 3, "Roll should be at least d20 min + modifier")

        # If successful, concentration should still be active
        if success:
            concentration = self.system.get_concentration_spell('test_wizard')
            self.assertIsNotNone(concentration, "Concentration should still be active on success")

    def test_concentration_save_high_damage(self):
        """Test concentration save with high damage."""
        # Start concentration
        self.system.start_concentration('test_wizard', 'hold_person', 2, 10)

        # High damage should increase DC
        success, dc, roll = self.system.make_concentration_save('test_wizard', 30, 2)  # DC 15

        self.assertEqual(dc, 15, "DC should be 15 for 30 damage")

    def test_update_concentration_duration(self):
        """Test updating concentration duration during combat."""
        # Start concentration
        self.system.start_concentration('test_wizard', 'hold_person', 2, 3)

        # Pass 1 round
        active = self.system.update_concentration_duration('test_wizard', 1)
        self.assertTrue(active, "Concentration should still be active after 1 round")

        concentration = self.system.get_concentration_spell('test_wizard')
        self.assertEqual(concentration['duration_remaining'], 2)

        # Pass 2 more rounds (should end spell)
        active = self.system.update_concentration_duration('test_wizard', 2)
        self.assertFalse(active, "Concentration should end after duration expires")

        # Verify concentration is gone
        concentration = self.system.get_concentration_spell('test_wizard')
        self.assertIsNone(concentration, "Concentration should be ended")

    def test_duration_parsing(self):
        """Test spell duration parsing to rounds."""
        test_cases = [
            ("Concentration, up to 1 minute", 10),
            ("Concentration, up to 10 minutes", 100),
            ("Concentration, up to 1 hour", 600),
        ]

        for duration, expected_rounds in test_cases:
            result = self.system._parse_spell_duration_to_rounds(duration)
            self.assertEqual(result, expected_rounds, f"Duration '{duration}' should be {expected_rounds} rounds")

    def test_get_all_concentrating_characters(self):
        """Test getting all characters currently concentrating."""
        # Start concentration for multiple characters
        self.system.start_concentration('test_wizard', 'hold_person', 2, 10)
        self.system.start_concentration('test_fighter', 'web', 2, 60)

        concentrating = self.system.get_all_concentrating_characters()
        self.assertEqual(len(concentrating), 2, "Should have 2 concentrating characters")

        character_names = [c['character_name'] for c in concentrating]
        self.assertIn('Test Wizard', character_names)
        self.assertIn('Test Fighter', character_names)

if __name__ == '__main__':
    # Set a fixed seed for reproducible tests
    import random
    random.seed(42)
    unittest.main()