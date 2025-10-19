#test
import unittest
import sqlite3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from talekeeper.services.spell_handlers.buff_handlers import (
    ShieldOfFaithHandler, DivineFavorHandler, AidHandler, BlessHandler,
    HeroismHandler, MagicWeaponHandler, WardingBondHandler, DeathWardHandler,
    AuraOfLifeHandler, ProtectionFromEvilAndGoodHandler, ShiningSMiteHandler,
    ZoneOfTruthHandler
)


class TestBuffSpells(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_buff_spells.db"
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
                    max_hit_points INTEGER DEFAULT 20,
                    hit_points_temporary INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE spells (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER NOT NULL DEFAULT 1,
                    school TEXT NOT NULL DEFAULT 'abjuration',
                    casting_time TEXT NOT NULL DEFAULT '1 action',
                    range_value TEXT NOT NULL DEFAULT 'Self',
                    components TEXT NOT NULL DEFAULT 'V, S',
                    duration TEXT NOT NULL DEFAULT '1 minute',
                    concentration BOOLEAN DEFAULT FALSE,
                    ritual BOOLEAN DEFAULT FALSE,
                    description TEXT DEFAULT '',
                    higher_levels TEXT,
                    source TEXT DEFAULT 'PHB',
                    classes TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
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
                    expires_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE character_concentration (
                    character_id TEXT PRIMARY KEY,
                    spell_id TEXT,
                    spell_level INTEGER,
                    start_time TEXT DEFAULT (datetime('now')),
                    duration_remaining INTEGER,
                    concentration_dc INTEGER DEFAULT 10
                )
            """)

            cursor.execute("INSERT INTO characters (id, name) VALUES ('paladin1', 'Test Paladin')")
            cursor.execute("INSERT INTO spells (id, name, concentration, duration) VALUES ('shield_of_faith', 'Shield of Faith', TRUE, '10 minutes')")
            cursor.execute("INSERT INTO spells (id, name, concentration, duration) VALUES ('divine_favor', 'Divine Favor', TRUE, '1 minute')")
            cursor.execute("INSERT INTO spells (id, name, concentration, duration) VALUES ('aid', 'Aid', FALSE, '8 hours')")
            cursor.execute("INSERT INTO spells (id, name, concentration, duration) VALUES ('bless', 'Bless', TRUE, '1 minute')")

            conn.commit()

    def setUp(self):
        self.shield_faith = ShieldOfFaithHandler(self.test_db)
        self.divine_favor = DivineFavorHandler(self.test_db)
        self.aid = AidHandler(self.test_db)
        self.bless = BlessHandler(self.test_db)

        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM active_spell_effects")
            cursor.execute("DELETE FROM character_concentration")
            cursor.execute("UPDATE characters SET current_hit_points = 20 WHERE id = 'paladin1'")
            conn.commit()

    def test_shield_of_faith_applies_buff(self):
        result = self.shield_faith.execute('paladin1', ['paladin1'], slot_level=1, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['spell_name'], 'Shield of Faith')
        self.assertEqual(result['ac_bonus'], 2)
        self.assertTrue(result['concentration'])

        ac_mod = self.shield_faith.effects.get_ac_modifier('paladin1')
        self.assertEqual(ac_mod, 2)

    def test_shield_of_faith_concentration(self):
        result = self.shield_faith.execute('paladin1', ['paladin1'], slot_level=1, context={})

        self.assertTrue(result['success'])

        conc_spell = self.shield_faith.concentration.get_concentration_spell('paladin1')
        self.assertIsNotNone(conc_spell)
        self.assertEqual(conc_spell['spell_id'], 'shield_of_faith')

    def test_divine_favor_damage_bonus(self):
        result = self.divine_favor.execute('paladin1', [], slot_level=1, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['spell_name'], 'Divine Favor')
        self.assertTrue(result['concentration'])

        damage_bonus = self.divine_favor.effects.get_damage_bonus('paladin1')
        self.assertEqual(len(damage_bonus['dice_bonuses']), 1)
        self.assertEqual(damage_bonus['dice_bonuses'][0]['dice'], '1d4')
        self.assertEqual(damage_bonus['dice_bonuses'][0]['damage_type'], 'radiant')

    def test_aid_hp_increase(self):
        result = self.aid.execute('paladin1', ['paladin1'], slot_level=2, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['spell_name'], 'Aid')
        self.assertEqual(result['hp_increase'], 10)
        self.assertFalse(result['concentration'])

        buff = self.aid.effects.get_buff('paladin1', 'aid')
        self.assertIsNotNone(buff)
        self.assertEqual(buff['effect_type'], 'hp_maximum_increase')
        self.assertEqual(buff['effect_data']['value'], 10)

    def test_aid_healing(self):
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET current_hit_points = 15 WHERE id = 'paladin1'")
            conn.commit()

        result = self.aid.execute('paladin1', ['paladin1'], slot_level=2, context={})

        self.assertTrue(result['success'])
        self.assertGreater(result['healing'], 0)
        self.assertGreater(result['new_hp'], 15)

    def test_bless_attack_save_bonus(self):
        result = self.bless.execute('paladin1', ['paladin1'], slot_level=1, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['spell_name'], 'Bless')
        self.assertTrue(result['concentration'])

        attack_bonus = self.bless.effects.get_attack_bonus('paladin1')
        self.assertEqual(len(attack_bonus['dice_bonuses']), 1)
        self.assertEqual(attack_bonus['dice_bonuses'][0]['dice'], '1d4')

    def test_multiple_buffs_stack(self):
        self.shield_faith.execute('paladin1', ['paladin1'], slot_level=1, context={})

        self.divine_favor.execute('paladin1', [], slot_level=1, context={})

        ac_mod = self.shield_faith.effects.get_ac_modifier('paladin1')
        self.assertEqual(ac_mod, 2)

        damage_bonus = self.shield_faith.effects.get_damage_bonus('paladin1')
        self.assertEqual(len(damage_bonus['dice_bonuses']), 1)

    def test_concentration_breaks_previous_spell(self):
        result1 = self.shield_faith.execute('paladin1', ['paladin1'], slot_level=1, context={})
        self.assertTrue(result1['success'])

        result2 = self.divine_favor.execute('paladin1', [], slot_level=1, context={})
        self.assertTrue(result2['success'])

        conc_spell = self.divine_favor.concentration.get_concentration_spell('paladin1')
        self.assertEqual(conc_spell['spell_id'], 'divine_favor')


if __name__ == '__main__':
    unittest.main()
