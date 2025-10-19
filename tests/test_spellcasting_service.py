#test
"""
Test Spellcasting Service

Phase 1.3: Testing spellcasting service foundation
Implementation Plan Reference: Phase 1 > Step 1.3
"""

import unittest
import tempfile
import os
import sqlite3
from services.spellcasting_service import (
    SpellcastingService, SpellcastingAbility, SpellSlotType,
    SpellSlot, SpellcastingCharacter
)
from services.spell_registry import spell_registry


class TestSpellcastingService(unittest.TestCase):
    def setUp(self):
        """Set up test database with minimal schema."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Create test database with required tables
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create required tables
            cursor.executescript("""
                -- Characters table (minimal)
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER DEFAULT 1,
                    intelligence INTEGER DEFAULT 10,
                    wisdom INTEGER DEFAULT 10,
                    charisma INTEGER DEFAULT 10,
                    proficiency_bonus INTEGER DEFAULT 2
                );

                -- Spellcasting tables from migration 011
                CREATE TABLE character_spell_slots (
                    character_id TEXT NOT NULL,
                    spell_level INTEGER NOT NULL,
                    max_slots INTEGER DEFAULT 0,
                    used_slots INTEGER DEFAULT 0,
                    slot_type TEXT DEFAULT 'standard',
                    last_reset TEXT,
                    PRIMARY KEY (character_id, spell_level, slot_type)
                );

                CREATE TABLE character_spells (
                    character_id TEXT NOT NULL,
                    spell_id TEXT NOT NULL,
                    spell_level INTEGER NOT NULL,
                    is_prepared BOOLEAN DEFAULT TRUE,
                    source TEXT NOT NULL,
                    source_level INTEGER,
                    always_prepared BOOLEAN DEFAULT FALSE,
                    ritual_only BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (character_id, spell_id)
                );

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

                CREATE TABLE character_spellcasting (
                    character_id TEXT PRIMARY KEY,
                    spellcasting_ability TEXT,
                    spell_attack_bonus INTEGER DEFAULT 0,
                    spell_save_dc INTEGER DEFAULT 8,
                    ritual_casting BOOLEAN DEFAULT FALSE,
                    spellcasting_focus TEXT,
                    spells_known INTEGER DEFAULT 0,
                    spells_prepared INTEGER DEFAULT 0,
                    last_preparation_reset TEXT
                );

                CREATE TABLE character_concentration (
                    character_id TEXT PRIMARY KEY,
                    spell_id TEXT,
                    spell_level INTEGER,
                    start_time TEXT DEFAULT (datetime('now')),
                    duration_remaining INTEGER,
                    concentration_dc INTEGER DEFAULT 10
                );
            """)

            # Insert test data
            cursor.execute("""
                INSERT INTO characters (id, name, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES ('wizard-1', 'Test Wizard', 3, 16, 12, 10, 2)
            """)

            cursor.execute("""
                INSERT INTO characters (id, name, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES ('cleric-1', 'Test Cleric', 2, 10, 15, 12, 2)
            """)

            cursor.execute("""
                INSERT INTO characters (id, name, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES ('warlock-1', 'Test Warlock', 3, 10, 12, 16, 2)
            """)

            # Insert test spells
            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                   components, duration, description, concentration, classes)
                VALUES ('magic_missile', 'Magic Missile', 1, 'evocation', '1 action', '120 feet',
                        'V,S', 'Instantaneous', 'Test spell', 0, '["wizard"]')
            """)

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                   components, duration, description, concentration, classes)
                VALUES ('fireball', 'Fireball', 3, 'evocation', '1 action', '150 feet',
                        'V,S,M', 'Instantaneous', 'Test spell', 0, '["wizard"]')
            """)

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                   components, duration, description, concentration, classes)
                VALUES ('cure_wounds', 'Cure Wounds', 1, 'evocation', '1 action', 'Touch',
                        'V,S', 'Instantaneous', 'Test spell', 0, '["cleric"]')
            """)

            cursor.execute("""
                INSERT INTO spells (id, name, level, school, casting_time, range_value,
                                   components, duration, description, concentration, classes)
                VALUES ('hex', 'Hex', 1, 'enchantment', '1 bonus action', '90 feet',
                        'V,S,M', '1 hour', 'Test spell', 1, '["warlock"]')
            """)

            # Insert spell-class mappings
            mappings = [
                ('magic_missile', 'wizard', 'class'),
                ('fireball', 'wizard', 'class'),
                ('cure_wounds', 'cleric', 'class'),
                ('hex', 'warlock', 'class')
            ]

            for spell_id, class_id, source in mappings:
                cursor.execute("""
                    INSERT INTO spell_class_lists (spell_id, class_id, source_feature)
                    VALUES (?, ?, ?)
                """, (spell_id, class_id, source))

            conn.commit()

        self.service = SpellcastingService(self.db_path)
        # Set up spell registry with our test database
        spell_registry.db_path = self.db_path

    def tearDown(self):
        """Clean up test database."""
        try:
            os.unlink(self.db_path)
        except (PermissionError, FileNotFoundError):
            pass

    def test_initialize_wizard_spellcasting(self):
        """Test initializing spellcasting for a wizard."""
        result = self.service.initialize_character_spellcasting('wizard-1', 'wizard')
        self.assertTrue(result)

        # Check spellcasting info
        spellcasting = self.service.get_character_spellcasting('wizard-1')
        self.assertIsNotNone(spellcasting)
        self.assertEqual(spellcasting.spellcasting_ability, SpellcastingAbility.INTELLIGENCE)
        self.assertEqual(spellcasting.spell_attack_bonus, 5)  # +3 Int mod + 2 prof
        self.assertEqual(spellcasting.spell_save_dc, 13)  # 8 + 3 + 2
        self.assertTrue(spellcasting.ritual_casting)

        # Check spell slots (level 3 wizard)
        slots = self.service.get_character_spell_slots('wizard-1')
        self.assertEqual(len(slots), 2)  # Level 1 and 2 slots

        # Level 1 slots
        level_1_slots = [s for s in slots if s.level == 1]
        self.assertEqual(len(level_1_slots), 1)
        self.assertEqual(level_1_slots[0].max_slots, 4)
        self.assertEqual(level_1_slots[0].used_slots, 0)

        # Level 2 slots
        level_2_slots = [s for s in slots if s.level == 2]
        self.assertEqual(len(level_2_slots), 1)
        self.assertEqual(level_2_slots[0].max_slots, 2)

    def test_initialize_cleric_spellcasting(self):
        """Test initializing spellcasting for a cleric."""
        result = self.service.initialize_character_spellcasting('cleric-1', 'cleric')
        self.assertTrue(result)

        spellcasting = self.service.get_character_spellcasting('cleric-1')
        self.assertEqual(spellcasting.spellcasting_ability, SpellcastingAbility.WISDOM)
        self.assertEqual(spellcasting.spell_attack_bonus, 4)  # +2 Wis mod + 2 prof
        self.assertEqual(spellcasting.spell_save_dc, 12)  # 8 + 2 + 2
        self.assertTrue(spellcasting.ritual_casting)

    def test_initialize_warlock_spellcasting(self):
        """Test initializing spellcasting for a warlock."""
        result = self.service.initialize_character_spellcasting('warlock-1', 'warlock')
        self.assertTrue(result)

        spellcasting = self.service.get_character_spellcasting('warlock-1')
        self.assertEqual(spellcasting.spellcasting_ability, SpellcastingAbility.CHARISMA)
        self.assertEqual(spellcasting.spell_attack_bonus, 5)  # +3 Cha mod + 2 prof
        self.assertEqual(spellcasting.spell_save_dc, 13)

        # Check warlock pact magic slots (level 3)
        slots = self.service.get_character_spell_slots('warlock-1')
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].level, 2)  # Level 3 warlock has 2nd level pact slots
        self.assertEqual(slots[0].max_slots, 2)
        self.assertEqual(slots[0].slot_type, SpellSlotType.PACT)

    def test_spell_slot_usage(self):
        """Test using and restoring spell slots."""
        # Initialize wizard
        self.service.initialize_character_spellcasting('wizard-1', 'wizard')

        # Add a prepared spell
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_spells (character_id, spell_id, spell_level,
                                            is_prepared, source)
                VALUES ('wizard-1', 'magic_missile', 1, 1, 'class')
            """)
            conn.commit()

        # Check can cast
        can_cast, reason = self.service.can_cast_spell('wizard-1', 'magic_missile')
        self.assertTrue(can_cast, f"Should be able to cast: {reason}")

        # Cast the spell
        result = self.service.cast_spell('wizard-1', 'magic_missile')
        self.assertTrue(result.success)
        self.assertEqual(result.spell_level_cast, 1)
        self.assertEqual(result.slot_level_used, 1)
        self.assertEqual(result.slot_type_used, SpellSlotType.STANDARD)

        # Check slots after casting
        slots = self.service.get_character_spell_slots('wizard-1')
        level_1_slot = [s for s in slots if s.level == 1][0]
        self.assertEqual(level_1_slot.used_slots, 1)
        self.assertEqual(level_1_slot.available_slots, 3)

    def test_concentration_mechanics(self):
        """Test concentration spell mechanics."""
        # Initialize wizard
        self.service.initialize_character_spellcasting('wizard-1', 'wizard')

        # Add a concentration spell
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_spells (character_id, spell_id, spell_level,
                                            is_prepared, source)
                VALUES ('wizard-1', 'hex', 1, 1, 'class')
            """)
            conn.commit()

        # Cast concentration spell
        result = self.service.cast_spell('wizard-1', 'hex')
        self.assertTrue(result.success)
        self.assertTrue(result.concentration_started)

        # Check concentration status
        concentration = self.service.get_concentration_spell('wizard-1')
        self.assertIsNotNone(concentration)
        self.assertEqual(concentration[0], 'hex')
        self.assertEqual(concentration[1], 1)

        # End concentration
        ended_spell = self.service.end_concentration('wizard-1')
        self.assertEqual(ended_spell, 'hex')

        # Check concentration is gone
        concentration = self.service.get_concentration_spell('wizard-1')
        self.assertIsNone(concentration)

    def test_upcasting(self):
        """Test casting spells at higher levels."""
        # Initialize wizard
        self.service.initialize_character_spellcasting('wizard-1', 'wizard')

        # Add a prepared spell
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_spells (character_id, spell_id, spell_level,
                                            is_prepared, source)
                VALUES ('wizard-1', 'magic_missile', 1, 1, 'class')
            """)
            conn.commit()

        # Cast at higher level
        result = self.service.cast_spell('wizard-1', 'magic_missile', spell_level=2)
        self.assertTrue(result.success)
        self.assertEqual(result.spell_level_cast, 2)
        self.assertEqual(result.slot_level_used, 2)

        # Check that level 2 slot was used
        slots = self.service.get_character_spell_slots('wizard-1')
        level_2_slot = [s for s in slots if s.level == 2][0]
        self.assertEqual(level_2_slot.used_slots, 1)

    def test_spell_slot_restoration(self):
        """Test spell slot restoration on rest."""
        # Initialize wizard and use some slots
        self.service.initialize_character_spellcasting('wizard-1', 'wizard')

        # Manually use some slots
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_spell_slots
                SET used_slots = 2
                WHERE character_id = 'wizard-1' AND spell_level = 1
            """)
            conn.commit()

        # Long rest should restore all slots
        restored = self.service.restore_spell_slots('wizard-1', 'long')
        self.assertIn(1, restored)
        self.assertEqual(restored[1], 4)  # 4 level 1 slots total

        # Check slots are restored
        slots = self.service.get_character_spell_slots('wizard-1')
        level_1_slot = [s for s in slots if s.level == 1][0]
        self.assertEqual(level_1_slot.used_slots, 0)

    def test_warlock_pact_magic_restoration(self):
        """Test warlock pact magic slot restoration on short rest."""
        # Initialize warlock and use pact slot
        self.service.initialize_character_spellcasting('warlock-1', 'warlock')

        # Use pact slot
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_spell_slots
                SET used_slots = 1
                WHERE character_id = 'warlock-1' AND slot_type = 'pact'
            """)
            conn.commit()

        # Short rest should restore pact slots
        restored = self.service.restore_spell_slots('warlock-1', 'short')
        self.assertIn(2, restored)  # Level 3 warlock has 2nd level pact slots

        # Check pact slots are restored
        slots = self.service.get_character_spell_slots('warlock-1')
        pact_slot = slots[0]  # Only one slot for warlock
        self.assertEqual(pact_slot.used_slots, 0)

    def test_spell_validation(self):
        """Test spell casting validation."""
        # Initialize wizard but don't prepare the spell
        self.service.initialize_character_spellcasting('wizard-1', 'wizard')

        # Try to cast unprepared spell
        can_cast, reason = self.service.can_cast_spell('wizard-1', 'magic_missile')
        self.assertFalse(can_cast)
        self.assertIn("not known", reason)

        # Try to cast non-existent spell
        can_cast, reason = self.service.can_cast_spell('wizard-1', 'nonexistent')
        self.assertFalse(can_cast)
        self.assertIn("not found", reason)


if __name__ == '__main__':
    unittest.main()