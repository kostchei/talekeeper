"""
Test Ritual Casting Service - Phase 4.1 Testing
Tests ritual casting mechanics for D&D 2024
"""

import unittest
import sqlite3
import tempfile
import os
from services.ritual_casting_service import RitualCastingService

class TestRitualCasting(unittest.TestCase):
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
                    level INTEGER
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
                    ritual BOOLEAN DEFAULT FALSE,
                    description TEXT NOT NULL,
                    classes TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE character_spellcasting (
                    character_id TEXT NOT NULL,
                    spellcasting_class TEXT NOT NULL,
                    spellcasting_ability TEXT,
                    ritual_casting INTEGER DEFAULT 0,
                    PRIMARY KEY (character_id, spellcasting_class)
                )
            """)

            cursor.execute("""
                CREATE TABLE character_spells (
                    character_id TEXT NOT NULL,
                    spell_id TEXT NOT NULL,
                    is_prepared BOOLEAN DEFAULT TRUE,
                    always_prepared BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (character_id, spell_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE wizard_spellbook (
                    character_id TEXT NOT NULL,
                    spell_id TEXT NOT NULL,
                    PRIMARY KEY (character_id, spell_id)
                )
            """)

            # Insert test data
            cursor.execute("""
                INSERT INTO characters (id, name, class_name, level)
                VALUES ('test_cleric', 'Test Cleric', 'cleric', 3)
            """)

            cursor.execute("""
                INSERT INTO characters (id, name, class_name, level)
                VALUES ('test_wizard', 'Test Wizard', 'wizard', 3)
            """)

            cursor.execute("""
                INSERT INTO characters (id, name, class_name, level)
                VALUES ('test_fighter', 'Test Fighter', 'fighter', 3)
            """)

            # Insert ritual spells
            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                  components, duration, ritual, description, classes)
                VALUES ('detect_magic', 'Detect Magic', 1, 'Divination', '1 action', 'Self',
                       'V, S', 'Concentration, up to 10 minutes', 1,
                       'Sense magic within 30 feet', '["cleric", "wizard"]')
            """)

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                  components, duration, ritual, description, classes)
                VALUES ('identify', 'Identify', 1, 'Divination', '1 minute', 'Touch',
                       'V, S, M', '1 minute', 1,
                       'Learn properties of magic item', '["wizard"]')
            """)

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                  components, duration, ritual, description, classes)
                VALUES ('magic_missile', 'Magic Missile', 1, 'Evocation', '1 action', '120 feet',
                       'V, S', 'Instantaneous', 0,
                       'Create darts of force', '["wizard"]')
            """)

            # Set up spellcasting abilities
            cursor.execute("""
                INSERT INTO character_spellcasting (character_id, spellcasting_class, ritual_casting)
                VALUES ('test_cleric', 'cleric', 1)
            """)

            cursor.execute("""
                INSERT INTO character_spellcasting (character_id, spellcasting_class, ritual_casting)
                VALUES ('test_wizard', 'wizard', 1)
            """)

            # Give spells to characters
            cursor.execute("""
                INSERT INTO character_spells (character_id, spell_id, is_prepared)
                VALUES ('test_cleric', 'detect_magic', 1)
            """)

            cursor.execute("""
                INSERT INTO wizard_spellbook (character_id, spell_id)
                VALUES ('test_wizard', 'identify')
            """)

            cursor.execute("""
                INSERT INTO wizard_spellbook (character_id, spell_id)
                VALUES ('test_wizard', 'detect_magic')
            """)

            conn.commit()

        self.service = RitualCastingService(self.db_path)

    def tearDown(self):
        """Clean up test database."""
        # Close any connections first
        if hasattr(self, 'service'):
            del self.service
        try:
            os.unlink(self.db_path)
        except (PermissionError, FileNotFoundError):
            pass  # File may already be cleaned up or in use

    def test_cleric_can_ritual_cast_detect_magic(self):
        """Test that cleric can ritual cast Detect Magic."""
        can_cast, reason = self.service.can_cast_as_ritual('test_cleric', 'detect_magic')
        self.assertTrue(can_cast, f"Cleric should be able to ritual cast Detect Magic: {reason}")

    def test_wizard_can_ritual_cast_from_spellbook(self):
        """Test that wizard can ritual cast spells from spellbook."""
        can_cast, reason = self.service.can_cast_as_ritual('test_wizard', 'identify')
        self.assertTrue(can_cast, f"Wizard should be able to ritual cast from spellbook: {reason}")

    def test_fighter_cannot_ritual_cast(self):
        """Test that fighter cannot ritual cast."""
        can_cast, reason = self.service.can_cast_as_ritual('test_fighter', 'detect_magic')
        self.assertFalse(can_cast, "Fighter should not be able to ritual cast")
        self.assertIn("ritual casting ability", reason)

    def test_cannot_ritual_cast_non_ritual_spell(self):
        """Test that non-ritual spells cannot be cast as rituals."""
        can_cast, reason = self.service.can_cast_as_ritual('test_wizard', 'magic_missile')
        self.assertFalse(can_cast, "Non-ritual spells should not be castable as rituals")
        self.assertIn("cannot be cast as a ritual", reason)

    def test_ritual_casting_time_calculation(self):
        """Test ritual casting time calculation."""
        normal_times = [
            ("1 action", "10 minutes 1 action"),
            ("1 minute", "11 minutes"),
            ("10 minutes", "20 minutes"),
            ("1 hour", "1 hour + 10 minutes")
        ]

        for normal, expected in normal_times:
            result = self.service._calculate_ritual_casting_time(normal)
            self.assertEqual(result, expected, f"Ritual time for {normal} should be {expected}")

    def test_get_ritual_spells_for_cleric(self):
        """Test getting available ritual spells for cleric."""
        spells = self.service.get_ritual_spells_for_character('test_cleric')

        self.assertGreater(len(spells), 0, "Cleric should have ritual spells available")

        # Check detect magic is included
        detect_magic = next((s for s in spells if s['id'] == 'detect_magic'), None)
        self.assertIsNotNone(detect_magic, "Detect Magic should be available to cleric")
        self.assertEqual(detect_magic['ritual_casting_time'], "10 minutes 1 action")

    def test_get_ritual_spells_for_wizard(self):
        """Test getting available ritual spells for wizard."""
        spells = self.service.get_ritual_spells_for_character('test_wizard')

        self.assertGreater(len(spells), 0, "Wizard should have ritual spells available")

        # Check both spells are included
        spell_ids = [s['id'] for s in spells]
        self.assertIn('identify', spell_ids, "Identify should be available to wizard")
        self.assertIn('detect_magic', spell_ids, "Detect Magic should be available to wizard")

    def test_cast_ritual_spell_success(self):
        """Test successful ritual spell casting."""
        result = self.service.cast_ritual_spell('test_cleric', 'detect_magic')

        self.assertTrue(result['success'], f"Ritual casting should succeed: {result.get('message')}")
        self.assertFalse(result['spell_slot_consumed'], "Ritual casting should not consume spell slots")
        self.assertEqual(result['spell_name'], 'Detect Magic')
        self.assertIn('effects', result)

    def test_cast_ritual_spell_failure(self):
        """Test failed ritual spell casting."""
        result = self.service.cast_ritual_spell('test_fighter', 'detect_magic')

        self.assertFalse(result['success'], "Fighter should not be able to ritual cast")
        self.assertFalse(result['spell_slot_consumed'], "Failed casting should not consume slots")

if __name__ == '__main__':
    unittest.main()