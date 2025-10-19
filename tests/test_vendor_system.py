#test
import unittest
import sqlite3
import os
import sys
import random

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from talekeeper.services.shop_service import ShopService, ShopSize
from talekeeper.services.hex_map_service import HexMapService


class TestVendorSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_path = "test_vendor.db"
        cls._setup_test_database()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    @classmethod
    def _setup_test_database(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                level INTEGER DEFAULT 1,
                charisma INTEGER DEFAULT 10,
                strength INTEGER DEFAULT 10,
                dexterity INTEGER DEFAULT 10,
                constitution INTEGER DEFAULT 10,
                intelligence INTEGER DEFAULT 10,
                wisdom INTEGER DEFAULT 10
            )
        ''')

        cursor.execute('''
            CREATE TABLE character_proficiencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                proficiency_type TEXT NOT NULL,
                proficiency_name TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'unknown',
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                UNIQUE(character_id, proficiency_name)
            )
        ''')

        cursor.execute('''
            CREATE TABLE character_feats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                feat_name TEXT NOT NULL,
                feat_id TEXT,
                feat_source TEXT NOT NULL DEFAULT 'unknown',
                level_acquired INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE character_hex_map (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                q INTEGER NOT NULL,
                r INTEGER NOT NULL,
                terrain_type TEXT NOT NULL,
                biome TEXT NOT NULL,
                encounter_seed INTEGER,
                settlement_type TEXT,
                revealed INTEGER DEFAULT 0,
                visited INTEGER DEFAULT 0,
                first_visited_date TEXT,
                last_visited_date TEXT,
                visit_count INTEGER DEFAULT 0,
                cleared INTEGER DEFAULT 0,
                cleared_date TEXT,
                UNIQUE(character_id, q, r),
                FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE character_hex_position (
                character_id TEXT PRIMARY KEY,
                current_q INTEGER NOT NULL DEFAULT 0,
                current_r INTEGER NOT NULL DEFAULT 0,
                facing_direction INTEGER DEFAULT 0,
                FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE hex_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                hex_q INTEGER NOT NULL,
                hex_r INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_date TEXT NOT NULL,
                character_level INTEGER,
                narrative TEXT,
                outcome TEXT,
                FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            INSERT INTO characters (id, name, level, charisma)
            VALUES ('test_char_1', 'Test Character', 5, 16)
        ''')

        cursor.execute('''
            INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
            VALUES ('test_char_1', 'skill', 'Persuasion', 'class')
        ''')

        cursor.execute('''
            INSERT INTO characters (id, name, level, charisma)
            VALUES ('test_char_crafter', 'Crafter Character', 5, 14)
        ''')

        cursor.execute('''
            INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
            VALUES ('test_char_crafter', 'skill', 'Deception', 'background')
        ''')

        cursor.execute('''
            INSERT INTO character_feats (character_id, feat_name, level_acquired)
            VALUES ('test_char_crafter', 'Crafter', 1)
        ''')

        cursor.execute('''
            INSERT INTO characters (id, name, level, charisma)
            VALUES ('test_char_no_skills', 'No Skills Character', 3, 10)
        ''')

        conn.commit()
        conn.close()

    def setUp(self):
        self.shop_service = ShopService(db_path=self.db_path)
        self.hex_service = HexMapService(db_path=self.db_path)

    def test_calculate_ability_modifier(self):
        self.assertEqual(self.shop_service._calculate_ability_modifier(10), 0)
        self.assertEqual(self.shop_service._calculate_ability_modifier(16), 3)
        self.assertEqual(self.shop_service._calculate_ability_modifier(20), 5)
        self.assertEqual(self.shop_service._calculate_ability_modifier(8), -1)

    def test_calculate_proficiency_bonus(self):
        self.assertEqual(self.shop_service._calculate_proficiency_bonus(1), 2)
        self.assertEqual(self.shop_service._calculate_proficiency_bonus(5), 3)
        self.assertEqual(self.shop_service._calculate_proficiency_bonus(9), 4)
        self.assertEqual(self.shop_service._calculate_proficiency_bonus(20), 6)

    def test_has_crafter_feat(self):
        char_with_crafter = {'id': 'test_char_crafter'}
        char_without_crafter = {'id': 'test_char_1'}

        self.assertTrue(self.shop_service.has_crafter_feat(char_with_crafter))
        self.assertFalse(self.shop_service.has_crafter_feat(char_without_crafter))

    def test_get_charisma_skill_roll_with_proficiency(self):
        char_data = {'id': 'test_char_1', 'charisma': 16, 'level': 5}

        random.seed(42)
        roll = self.shop_service.get_charisma_skill_roll(char_data)

        self.assertGreater(roll, 0)
        self.assertLessEqual(roll, 20 + 3 + 3)

    def test_get_charisma_skill_roll_no_proficiency(self):
        char_data = {'id': 'test_char_no_skills', 'charisma': 10, 'level': 3}

        random.seed(42)
        roll = self.shop_service.get_charisma_skill_roll(char_data)

        self.assertGreater(roll, 0)
        self.assertLessEqual(roll, 20)

    def test_settlement_to_shop_size_mapping(self):
        self.assertEqual(self.shop_service._settlement_to_shop_size('hamlet'), ShopSize.SMALL)
        self.assertEqual(self.shop_service._settlement_to_shop_size('village'), ShopSize.MEDIUM)
        self.assertEqual(self.shop_service._settlement_to_shop_size('town_small'), ShopSize.LARGE)
        self.assertEqual(self.shop_service._settlement_to_shop_size('town_medium'), ShopSize.LARGE)
        self.assertEqual(self.shop_service._settlement_to_shop_size('town_large'), ShopSize.LARGE)

    def test_generate_hex_shop_inventory_structure(self):
        char_data = {'id': 'test_char_1', 'charisma': 16, 'level': 5}

        random.seed(12345)
        shop_data = self.shop_service.generate_hex_shop_inventory(
            settlement_type='village',
            character_data=char_data,
            hex_seed=12345
        )

        self.assertIn('inventory', shop_data)
        self.assertIn('charisma_roll', shop_data)
        self.assertIn('has_crafter', shop_data)
        self.assertIn('pool_variance', shop_data)
        self.assertIn('cap_variance', shop_data)
        self.assertIn('settlement_type', shop_data)
        self.assertIn('shop_size', shop_data)

        self.assertEqual(shop_data['settlement_type'], 'village')
        self.assertEqual(shop_data['shop_size'], 'medium')
        self.assertFalse(shop_data['has_crafter'])

        self.assertGreaterEqual(shop_data['pool_variance'], 0.01)
        self.assertLessEqual(shop_data['pool_variance'], 2.0)

    def test_generate_hex_shop_inventory_with_crafter(self):
        char_data = {'id': 'test_char_crafter', 'charisma': 14, 'level': 5}

        random.seed(67890)
        shop_data = self.shop_service.generate_hex_shop_inventory(
            settlement_type='hamlet',
            character_data=char_data,
            hex_seed=67890
        )

        self.assertTrue(shop_data['has_crafter'])
        self.assertEqual(shop_data['shop_size'], 'small')

    def test_generate_hex_shop_inventory_pricing(self):
        char_data = {'id': 'test_char_1', 'charisma': 16, 'level': 5}

        random.seed(11111)
        shop_data = self.shop_service.generate_hex_shop_inventory(
            settlement_type='village',
            character_data=char_data,
            hex_seed=11111
        )

        for item in shop_data['inventory']:
            self.assertIn('buy_price_gp', item)
            self.assertIn('buy_price_display', item)
            self.assertIn('buy_discount_applied', item)

            base_cost = item.get('cost_gp', 0)
            if base_cost > 0:
                self.assertGreater(item['buy_price_gp'], 0)

    def test_calculate_sell_price_with_character(self):
        char_data = {'id': 'test_char_1', 'charisma': 16, 'level': 5}

        random.seed(22222)
        sell_price, display, charisma_roll = self.shop_service.calculate_sell_price_with_character(
            item_cost=100.0,
            character_data=char_data
        )

        self.assertGreater(sell_price, 40.0)
        self.assertLessEqual(sell_price, 100.0)
        self.assertGreater(charisma_roll, 0)
        self.assertIsInstance(display, str)

    def test_settlement_generation_distribution(self):
        settlement_types = []

        for i in range(1000):
            random.seed(i)
            settlement_type = self.hex_service._generate_settlement_type()
            settlement_types.append(settlement_type)

        empty_count = settlement_types.count('empty')
        hamlet_count = settlement_types.count('hamlet')
        village_count = settlement_types.count('village')
        town_count = sum(1 for s in settlement_types if s.startswith('town_'))

        self.assertGreater(empty_count, 0)
        self.assertLess(empty_count, 100)

        self.assertGreater(hamlet_count, 200)
        self.assertLess(hamlet_count, 300)

        self.assertGreater(village_count, 600)
        self.assertLess(village_count, 750)

        self.assertGreater(town_count, 0)
        self.assertLess(town_count, 30)

    def test_settlement_generation_in_hex(self):
        self.hex_service.initialize_character_position('test_char_1')

        hex_data = self.hex_service.get_hex('test_char_1', 0, 0)

        self.assertIn('settlement_type', hex_data)
        self.assertIsNotNone(hex_data['settlement_type'])
        self.assertIn(hex_data['settlement_type'], [
            'empty', 'hamlet', 'village', 'town_small', 'town_medium', 'town_large'
        ])

    def test_settlement_persistence(self):
        self.hex_service.initialize_character_position('test_char_1')

        first_read = self.hex_service._generate_hex('test_char_1', 2, 2)
        settlement_first = first_read['settlement_type']

        second_read = self.hex_service.get_hex('test_char_1', 2, 2)
        settlement_second = second_read['settlement_type']

        self.assertEqual(settlement_first, settlement_second)

    def test_get_hex_settlement_method(self):
        self.hex_service.initialize_character_position('test_char_1')

        settlement_type = self.hex_service.get_hex_settlement('test_char_1', 0, 0)
        self.assertIsNotNone(settlement_type)
        self.assertIn(settlement_type, [
            'empty', 'hamlet', 'village', 'town_small', 'town_medium', 'town_large'
        ])


if __name__ == '__main__':
    unittest.main(verbosity=2)
