#test
import unittest
import sqlite3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from talekeeper.services.spell_effects_service import SpellEffectsService


class TestSpellEffectsService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_spell_effects.db"
        cls._create_test_database()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

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
                    current_hit_points INTEGER DEFAULT 20,
                    max_hit_points INTEGER DEFAULT 20,
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

            cursor.execute("INSERT INTO characters (id, name) VALUES ('char1', 'Test Paladin')")
            cursor.execute("INSERT INTO spells (id, name) VALUES ('cure_wounds', 'Cure Wounds')")
            cursor.execute("INSERT INTO spells (id, name) VALUES ('shield_of_faith', 'Shield of Faith')")

            conn.commit()

    def setUp(self):
        self.service = SpellEffectsService(self.test_db)
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET current_hit_points = 20, hit_points_temporary = 0 WHERE id = 'char1'")
            cursor.execute("DELETE FROM active_spell_effects")
            conn.commit()

    def test_apply_healing(self):
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET current_hit_points = 10 WHERE id = 'char1'")
            conn.commit()

        result = self.service.apply_healing('char1', 8, 'cure_wounds')

        self.assertTrue(result['success'])
        self.assertEqual(result['healing'], 8)
        self.assertEqual(result['new_hp'], 18)

    def test_apply_healing_max_cap(self):
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET current_hit_points = 18 WHERE id = 'char1'")
            conn.commit()

        result = self.service.apply_healing('char1', 10, 'cure_wounds')

        self.assertTrue(result['success'])
        self.assertEqual(result['healing'], 2)
        self.assertEqual(result['new_hp'], 20)

    def test_apply_damage(self):
        result = self.service.apply_damage('char1', 5, 'fire', 'searing_smite')

        self.assertTrue(result['success'])
        self.assertEqual(result['damage'], 5)
        self.assertEqual(result['new_hp'], 15)

    def test_apply_damage_with_temp_hp(self):
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET hit_points_temporary = 8 WHERE id = 'char1'")
            conn.commit()

        result = self.service.apply_damage('char1', 5, 'fire', 'test_spell')

        self.assertTrue(result['success'])
        self.assertEqual(result['temp_hp_absorbed'], 5)
        self.assertEqual(result['actual_damage'], 0)
        self.assertEqual(result['new_hp'], 20)

    def test_apply_damage_overflow_temp_hp(self):
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET hit_points_temporary = 3 WHERE id = 'char1'")
            conn.commit()

        result = self.service.apply_damage('char1', 8, 'fire', 'test_spell')

        self.assertTrue(result['success'])
        self.assertEqual(result['temp_hp_absorbed'], 3)
        self.assertEqual(result['actual_damage'], 5)
        self.assertEqual(result['new_hp'], 15)

    def test_apply_temp_hp(self):
        result = self.service.apply_temp_hp('char1', 5, 'heroism')

        self.assertTrue(result['success'])
        self.assertEqual(result['temp_hp_granted'], 5)
        self.assertEqual(result['temp_hp_total'], 5)

    def test_apply_temp_hp_higher_value_wins(self):
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET hit_points_temporary = 8 WHERE id = 'char1'")
            conn.commit()

        result = self.service.apply_temp_hp('char1', 5, 'heroism')

        self.assertTrue(result['success'])
        self.assertEqual(result['temp_hp_total'], 8)

        result2 = self.service.apply_temp_hp('char1', 12, 'aid')
        self.assertEqual(result2['temp_hp_total'], 12)

    def test_get_set_temp_hp(self):
        self.service.set_temp_hp('char1', 10, 'heroism')
        temp_hp = self.service.get_temp_hp('char1')
        self.assertEqual(temp_hp, 10)

    def test_clear_temp_hp(self):
        self.service.set_temp_hp('char1', 10, 'heroism')
        self.service.clear_temp_hp('char1')
        temp_hp = self.service.get_temp_hp('char1')
        self.assertEqual(temp_hp, 0)

    def test_apply_buff(self):
        buff_data = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        result = self.service.apply_buff('char1', buff_data, 100)

        self.assertTrue(result['success'])
        self.assertEqual(result['spell_id'], 'shield_of_faith')
        self.assertEqual(result['duration_rounds'], 100)

    def test_remove_buff(self):
        buff_data = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        self.service.apply_buff('char1', buff_data, 100)
        removed = self.service.remove_buff('char1', 'shield_of_faith')

        self.assertTrue(removed)
        self.assertFalse(self.service.has_buff('char1', 'shield_of_faith'))

    def test_has_buff(self):
        buff_data = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        self.assertFalse(self.service.has_buff('char1', 'shield_of_faith'))

        self.service.apply_buff('char1', buff_data, 100)

        self.assertTrue(self.service.has_buff('char1', 'shield_of_faith'))

    def test_get_buff(self):
        buff_data = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        self.service.apply_buff('char1', buff_data, 100)

        buff = self.service.get_buff('char1', 'shield_of_faith')

        self.assertIsNotNone(buff)
        self.assertEqual(buff['spell_name'], 'Shield of Faith')
        self.assertEqual(buff['effect_type'], 'ac_bonus')
        self.assertEqual(buff['rounds_remaining'], 100)

    def test_get_active_buffs(self):
        buff1 = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        buff2 = {
            'source': 'bless',
            'spell_name': 'Bless',
            'spell_level': 1,
            'type': 'attack_and_save_bonus',
            'bonus_dice': '1d4'
        }

        self.service.apply_buff('char1', buff1, 100)
        self.service.apply_buff('char1', buff2, 100)

        buffs = self.service.get_active_buffs('char1')

        self.assertEqual(len(buffs), 2)

    def test_get_active_buffs_filtered(self):
        buff1 = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        buff2 = {
            'source': 'bless',
            'spell_name': 'Bless',
            'spell_level': 1,
            'type': 'attack_and_save_bonus',
            'bonus_dice': '1d4'
        }

        self.service.apply_buff('char1', buff1, 100)
        self.service.apply_buff('char1', buff2, 100)

        ac_buffs = self.service.get_active_buffs('char1', 'ac_bonus')

        self.assertEqual(len(ac_buffs), 1)
        self.assertEqual(ac_buffs[0]['spell_name'], 'Shield of Faith')

    def test_get_ac_modifier(self):
        buff_data = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        self.service.apply_buff('char1', buff_data, 100)

        ac_mod = self.service.get_ac_modifier('char1')

        self.assertEqual(ac_mod, 2)

    def test_get_attack_bonus(self):
        buff_data = {
            'source': 'bless',
            'spell_name': 'Bless',
            'spell_level': 1,
            'type': 'attack_and_save_bonus',
            'bonus_dice': '1d4'
        }

        self.service.apply_buff('char1', buff_data, 100)

        attack_bonus = self.service.get_attack_bonus('char1')

        self.assertEqual(attack_bonus['total'], 0)
        self.assertEqual(len(attack_bonus['dice_bonuses']), 1)
        self.assertEqual(attack_bonus['dice_bonuses'][0]['dice'], '1d4')

    def test_decrement_effect_durations(self):
        buff_data = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        self.service.apply_buff('char1', buff_data, 2)

        self.service.decrement_effect_durations('char1')
        buff = self.service.get_buff('char1', 'shield_of_faith')
        self.assertEqual(buff['rounds_remaining'], 1)

        expired = self.service.decrement_effect_durations('char1')
        self.assertEqual(len(expired), 1)
        self.assertIn('shield_of_faith', expired)

        self.assertFalse(self.service.has_buff('char1', 'shield_of_faith'))

    def test_remove_all_buffs(self):
        buff1 = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': 1,
            'type': 'ac_bonus',
            'value': 2
        }

        buff2 = {
            'source': 'bless',
            'spell_name': 'Bless',
            'spell_level': 1,
            'type': 'attack_and_save_bonus',
            'bonus_dice': '1d4'
        }

        self.service.apply_buff('char1', buff1, 100)
        self.service.apply_buff('char1', buff2, 100)

        count = self.service.remove_all_buffs('char1')

        self.assertEqual(count, 2)
        self.assertEqual(len(self.service.get_active_buffs('char1')), 0)


if __name__ == '__main__':
    unittest.main()
