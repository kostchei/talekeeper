import unittest
import sqlite3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from talekeeper.services.spell_handlers.base_handler import SpellHandler, SpellHandlerRegistry


class TestSpellHandler(SpellHandler):
    def execute(self, caster_id, targets, slot_level, context):
        return {
            'success': True,
            'spell_name': 'Test Spell',
            'caster_id': caster_id,
            'targets': targets,
            'slot_level': slot_level
        }


class TestSpellHandlerRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_spell_registry.db"
        cls._create_test_database()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except:
                pass

    @classmethod
    def _create_test_database(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

        with sqlite3.connect(cls.test_db) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    charisma INTEGER DEFAULT 16
                )
            """)

            cursor.execute("""
                CREATE TABLE character_spellcasting (
                    character_id TEXT PRIMARY KEY,
                    spell_save_dc INTEGER DEFAULT 14
                )
            """)

            cursor.execute("INSERT INTO characters (id, name) VALUES ('char1', 'Test Paladin')")
            cursor.execute("INSERT INTO character_spellcasting (character_id) VALUES ('char1')")

            conn.commit()

    def setUp(self):
        self.registry = SpellHandlerRegistry(self.test_db)
        self.test_handler = TestSpellHandler(self.test_db)

    def test_register_handler(self):
        self.registry.register('test_spell', self.test_handler)

        handler = self.registry.get_handler('test_spell')

        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, TestSpellHandler)

    def test_get_handler_not_registered(self):
        handler = self.registry.get_handler('nonexistent_spell')

        self.assertIsNone(handler)

    def test_execute_spell(self):
        self.registry.register('test_spell', self.test_handler)

        result = self.registry.execute_spell(
            'test_spell',
            'char1',
            ['target1'],
            1,
            {}
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['caster_id'], 'char1')
        self.assertEqual(result['targets'], ['target1'])
        self.assertEqual(result['slot_level'], 1)

    def test_execute_spell_not_registered(self):
        result = self.registry.execute_spell(
            'nonexistent_spell',
            'char1',
            ['target1'],
            1,
            {}
        )

        self.assertFalse(result['success'])
        self.assertIn('No handler registered', result['reason'])

    def test_handler_get_ability_mod(self):
        mod = self.test_handler._get_ability_mod('char1', 'charisma')
        self.assertEqual(mod, 3)

    def test_handler_get_spell_save_dc(self):
        dc = self.test_handler._get_spell_save_dc('char1')
        self.assertEqual(dc, 14)


if __name__ == '__main__':
    unittest.main()
