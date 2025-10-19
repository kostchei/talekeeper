#test
import unittest
import sqlite3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from talekeeper.services.spell_handlers.healing_handlers import CureWoundsHandler, PrayerOfHealingHandler


class TestHealingSpells(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_healing_spells.db"
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
                    charisma INTEGER DEFAULT 16,
                    current_hit_points INTEGER DEFAULT 20,
                    max_hit_points INTEGER DEFAULT 30,
                    hit_points_temporary INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE spells (
                    id TEXT PRIMARY KEY,
                    name TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE active_spell_effects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    spell_id TEXT NOT NULL,
                    spell_name TEXT NOT NULL,
                    spell_level_cast INTEGER NOT NULL,
                    effect_type TEXT NOT NULL,
                    effect_data TEXT,
                    duration_type TEXT NOT NULL,
                    duration_remaining INTEGER,
                    rounds_remaining INTEGER,
                    concentration BOOLEAN DEFAULT FALSE,
                    caster_id TEXT,
                    target_id TEXT,
                    applied_at TEXT DEFAULT (datetime('now')),
                    expires_at TEXT,

                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                    FOREIGN KEY (spell_id) REFERENCES spells(id),
                    FOREIGN KEY (caster_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("INSERT INTO characters (id, name, current_hit_points) VALUES ('paladin1', 'Test Paladin', 10)")
            cursor.execute("INSERT INTO spells (id, name) VALUES ('cure_wounds', 'Cure Wounds')")
            cursor.execute("INSERT INTO spells (id, name) VALUES ('prayer_of_healing', 'Prayer of Healing')")

            conn.commit()

    def setUp(self):
        self.cure_wounds = CureWoundsHandler(self.test_db)
        self.prayer_healing = PrayerOfHealingHandler(self.test_db)

        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET current_hit_points = 10 WHERE id = 'paladin1'")
            conn.commit()

    def test_cure_wounds_level_1(self):
        result = self.cure_wounds.execute('paladin1', ['paladin1'], slot_level=1, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['spell_name'], 'Cure Wounds')
        self.assertEqual(result['slot_level'], 1)
        self.assertEqual(result['dice'], '1d8')
        self.assertEqual(result['modifier'], 3)
        self.assertGreater(result['new_hp'], 10)
        self.assertLessEqual(result['new_hp'], 30)

    def test_cure_wounds_level_2(self):
        result = self.cure_wounds.execute('paladin1', ['paladin1'], slot_level=2, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['dice'], '2d8')
        self.assertGreater(result['healing_roll'], result['healing_roll'] - result['modifier'])

    def test_cure_wounds_level_3(self):
        result = self.cure_wounds.execute('paladin1', ['paladin1'], slot_level=3, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['dice'], '3d8')

    def test_cure_wounds_healing_cap(self):
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET current_hit_points = 28 WHERE id = 'paladin1'")
            conn.commit()

        result = self.cure_wounds.execute('paladin1', ['paladin1'], slot_level=5, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['new_hp'], 30)
        self.assertEqual(result['max_hp'], 30)

    def test_prayer_of_healing_level_2(self):
        result = self.prayer_healing.execute('paladin1', ['paladin1'], slot_level=2, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['spell_name'], 'Prayer of Healing')
        self.assertEqual(result['slot_level'], 2)
        self.assertEqual(result['dice'], '2d8')
        self.assertEqual(result['modifier'], 3)
        self.assertIn('cast_time', result)
        self.assertEqual(result['cast_time'], '10 minutes')
        self.assertGreater(result['new_hp'], 10)

    def test_prayer_of_healing_level_3(self):
        result = self.prayer_healing.execute('paladin1', ['paladin1'], slot_level=3, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['dice'], '3d8')

    def test_prayer_of_healing_level_5(self):
        result = self.prayer_healing.execute('paladin1', ['paladin1'], slot_level=5, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['dice'], '5d8')

    def test_cure_wounds_healing_range(self):
        results = []
        for _ in range(10):
            with sqlite3.connect(self.test_db) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE characters SET current_hit_points = 10 WHERE id = 'paladin1'")
                conn.commit()

            result = self.cure_wounds.execute('paladin1', ['paladin1'], slot_level=1, context={})
            healing = result['healing']
            results.append(healing)

        min_healing = 1 + 3
        max_healing = 8 + 3

        self.assertGreaterEqual(min(results), min_healing)
        self.assertLessEqual(max(results), max_healing)


if __name__ == '__main__':
    unittest.main()
