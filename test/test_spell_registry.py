# test
"""
Test Spell Registry

Phase 1.2: Testing - Verify action economy still works for non-spellcasters
Implementation Plan Reference: Phase 1 > Step 1.2
"""

import unittest
import tempfile
import os
import sqlite3
from services.spell_registry import SpellRegistry, SpellDefinition, SpellSchool


class TestSpellRegistry(unittest.TestCase):
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Create minimal schema
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create spell tables
            cursor.executescript("""
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
                    higher_levels TEXT,
                    source TEXT DEFAULT 'PHB',
                    classes TEXT
                );

                CREATE TABLE spell_class_lists (
                    spell_id TEXT NOT NULL,
                    class_id TEXT NOT NULL,
                    is_bonus_spell BOOLEAN DEFAULT FALSE,
                    source_feature TEXT,
                    PRIMARY KEY (spell_id, class_id, source_feature)
                );
            """)

            # Insert test spells
            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                   components, duration, description, concentration, ritual, classes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'fireball', 'Fireball', 3, 'evocation', '1 action', '150 feet',
                'V,S,M', 'Instantaneous', 'A bright streak...', False, False,
                '["wizard", "sorcerer"]'
            ))

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                   components, duration, description, concentration, ritual, classes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'cure_wounds', 'Cure Wounds', 1, 'evocation', '1 action', 'Touch',
                'V,S', 'Instantaneous', 'A creature you touch...', False, False,
                '["cleric", "paladin"]'
            ))

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                   components, duration, description, concentration, ritual, classes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'detect_magic', 'Detect Magic', 1, 'divination', '1 action', 'Self',
                'V,S', '10 minutes', 'For the duration...', True, True,
                '["wizard", "cleric", "paladin"]'
            ))

            # Insert class mappings
            class_mappings = [
                ('fireball', 'wizard'),
                ('fireball', 'sorcerer'),
                ('cure_wounds', 'cleric'),
                ('cure_wounds', 'paladin'),
                ('detect_magic', 'wizard'),
                ('detect_magic', 'cleric'),
                ('detect_magic', 'paladin')
            ]

            for spell_id, class_id in class_mappings:
                cursor.execute("""
                    INSERT INTO spell_class_lists (spell_id, class_id, source_feature)
                    VALUES (?, ?, ?)
                """, (spell_id, class_id, 'class'))

            conn.commit()

        self.registry = SpellRegistry(self.db_path)

    def tearDown(self):
        """Clean up test database."""
        try:
            os.unlink(self.db_path)
        except (PermissionError, FileNotFoundError):
            pass

    def test_get_spell_by_id(self):
        """Test retrieving a spell by ID."""
        spell = self.registry.get_spell('fireball')

        self.assertIsNotNone(spell)
        self.assertEqual(spell.name, 'Fireball')
        self.assertEqual(spell.level, 3)
        self.assertEqual(spell.school, SpellSchool.EVOCATION)
        self.assertFalse(spell.concentration)
        self.assertFalse(spell.ritual)

    def test_get_nonexistent_spell(self):
        """Test retrieving a spell that doesn't exist."""
        spell = self.registry.get_spell('nonexistent')
        self.assertIsNone(spell)

    def test_get_spells_by_class(self):
        """Test retrieving spells by class."""
        wizard_spells = self.registry.get_spells_by_class('wizard')

        self.assertEqual(len(wizard_spells), 2)  # fireball, detect_magic
        spell_names = [s.name for s in wizard_spells]
        self.assertIn('Fireball', spell_names)
        self.assertIn('Detect Magic', spell_names)

    def test_get_spells_by_class_and_level(self):
        """Test retrieving spells by class and level."""
        wizard_level_1 = self.registry.get_spells_by_class('wizard', level=1)

        self.assertEqual(len(wizard_level_1), 1)
        self.assertEqual(wizard_level_1[0].name, 'Detect Magic')

    def test_get_ritual_spells(self):
        """Test retrieving ritual spells."""
        ritual_spells = self.registry.get_ritual_spells()

        self.assertEqual(len(ritual_spells), 1)
        self.assertEqual(ritual_spells[0].name, 'Detect Magic')
        self.assertTrue(ritual_spells[0].ritual)

    def test_get_ritual_spells_by_class(self):
        """Test retrieving ritual spells for a specific class."""
        wizard_rituals = self.registry.get_ritual_spells('wizard')

        self.assertEqual(len(wizard_rituals), 1)
        self.assertEqual(wizard_rituals[0].name, 'Detect Magic')

    def test_spell_caching(self):
        """Test that spells are cached properly."""
        # First retrieval
        spell1 = self.registry.get_spell('fireball')

        # Second retrieval should be from cache
        spell2 = self.registry.get_spell('fireball')

        # Should be the same object instance (cached)
        self.assertIs(spell1, spell2)

    def test_search_spells_by_name(self):
        """Test searching spells by name."""
        results = self.registry.search_spells(name_filter='Fire')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Fireball')

    def test_search_spells_by_school(self):
        """Test searching spells by school."""
        results = self.registry.search_spells(school_filter=SpellSchool.EVOCATION)

        self.assertEqual(len(results), 2)  # Fireball, Cure Wounds

    def test_search_spells_by_level(self):
        """Test searching spells by level."""
        results = self.registry.search_spells(level_filter=1)

        self.assertEqual(len(results), 2)  # Cure Wounds, Detect Magic

    def test_search_spells_ritual_only(self):
        """Test searching for ritual spells only."""
        results = self.registry.search_spells(ritual_only=True)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Detect Magic')

    def test_search_spells_concentration_only(self):
        """Test searching for concentration spells only."""
        results = self.registry.search_spells(concentration_only=True)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Detect Magic')

    def test_get_spell_count_by_class(self):
        """Test getting spell counts by level for a class."""
        counts = self.registry.get_spell_count_by_class('wizard')

        self.assertEqual(counts[1], 1)  # 1 level-1 spell
        self.assertEqual(counts[3], 1)  # 1 level-3 spell

    def test_get_available_classes(self):
        """Test getting all classes that have spells."""
        classes = self.registry.get_available_classes()

        expected_classes = {'wizard', 'sorcerer', 'cleric', 'paladin'}
        self.assertEqual(classes, expected_classes)

    def test_clear_cache(self):
        """Test clearing the spell cache."""
        # Load a spell to cache it
        spell1 = self.registry.get_spell('fireball')
        self.assertIsNotNone(spell1)

        # Clear cache
        self.registry.clear_cache()

        # Next retrieval should load from database again
        spell2 = self.registry.get_spell('fireball')
        self.assertIsNotNone(spell2)
        self.assertIsNot(spell1, spell2)  # Different objects now


if __name__ == '__main__':
    unittest.main()