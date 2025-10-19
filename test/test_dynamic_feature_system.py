# test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tempfile
import sqlite3
sys.path.append('..')
from services.dynamic_feature_manager import DynamicFeatureManager
from services.level_up_integration import LevelUpIntegration

class TestDynamicFeatureSystem(unittest.TestCase):
    def setUp(self):
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Initialize database with schema
        self._setup_test_database()

        self.feature_manager = DynamicFeatureManager(self.db_path)
        self.level_up_integration = LevelUpIntegration(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)

    def _setup_test_database(self):
        """Setup test database with minimal schema and data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create tables
            cursor.executescript("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    subclass_id TEXT,
                    level INTEGER DEFAULT 1
                );

                CREATE TABLE class_features_progression (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    feature_name TEXT NOT NULL,
                    feature_type TEXT NOT NULL,
                    description TEXT,
                    mechanics TEXT,
                    prerequisites TEXT
                );

                CREATE TABLE subclass_features_progression (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subclass_id TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    feature_name TEXT NOT NULL,
                    feature_type TEXT NOT NULL,
                    description TEXT,
                    mechanics TEXT,
                    prerequisites TEXT
                );

                CREATE TABLE character_feature_instances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    feature_source TEXT NOT NULL,
                    feature_id INTEGER,
                    feature_name TEXT NOT NULL,
                    level_gained INTEGER NOT NULL,
                    current_uses INTEGER DEFAULT 0,
                    max_uses INTEGER DEFAULT 0,
                    recharge_type TEXT,
                    configuration TEXT,
                    active BOOLEAN DEFAULT TRUE
                );

                CREATE TABLE rogue_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    sneak_attack_dice INTEGER DEFAULT 1,
                    cunning_action_available BOOLEAN DEFAULT FALSE,
                    uncanny_dodge_available BOOLEAN DEFAULT FALSE,
                    evasion_available BOOLEAN DEFAULT FALSE,
                    cunning_strike_available BOOLEAN DEFAULT FALSE,
                    reliable_talent_active BOOLEAN DEFAULT FALSE,
                    slippery_mind_active BOOLEAN DEFAULT FALSE,
                    elusive_active BOOLEAN DEFAULT FALSE,
                    stroke_of_luck_uses_max INTEGER DEFAULT 0
                );
            """)

            # Insert test data
            cursor.executescript("""
                INSERT INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
                ('rogue', 1, 'Expertise', 'passive', 'Double proficiency bonus on two skills', '{"expertise_count": 2}'),
                ('rogue', 1, 'Sneak Attack', 'passive', 'Deal extra damage when you have advantage', '{"damage_dice": 1, "damage_type": "d6"}'),
                ('rogue', 2, 'Cunning Action', 'bonus_action', 'Dash, Disengage, or Hide as bonus action', '{"bonus_actions": ["dash", "disengage", "hide"]}'),
                ('rogue', 3, 'Roguish Archetype', 'passive', 'Choose your rogue subclass', '{"subclass_selection": true}'),
                ('rogue', 5, 'Uncanny Dodge', 'reaction', 'Half damage from one attack', '{"damage_reduction": 0.5}');

                INSERT INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
                ('thief', 3, 'Fast Hands', 'bonus_action', 'Use Cunning Action for object interactions', '{"additional_cunning_actions": ["use_object", "sleight_of_hand"]}'),
                ('thief', 3, 'Second-Story Work', 'passive', 'Climbing and jumping bonuses', '{"climb_speed": "walking_speed"}');

                INSERT INTO characters (id, name, class_id, level) VALUES
                ('test_rogue', 'Test Rogue', 'rogue', 1);
            """)

    def test_grant_class_features_level_1(self):
        """Test granting level 1 rogue features"""
        features = self.feature_manager.grant_class_features_for_level('test_rogue', 'rogue', 1)

        self.assertEqual(len(features), 2)
        feature_names = [f.feature_name for f in features]
        self.assertIn('Expertise', feature_names)
        self.assertIn('Sneak Attack', feature_names)

        # Check expertise configuration
        expertise_feature = next(f for f in features if f.feature_name == 'Expertise')
        self.assertEqual(expertise_feature.configuration['expertise_count'], 2)

    def test_grant_class_features_level_2(self):
        """Test granting level 2 rogue features"""
        features = self.feature_manager.grant_class_features_for_level('test_rogue', 'rogue', 2)

        self.assertEqual(len(features), 1)
        self.assertEqual(features[0].feature_name, 'Cunning Action')
        self.assertEqual(features[0].feature_type, 'bonus_action')

    def test_subclass_selection_detection(self):
        """Test detecting subclass selection level"""
        is_subclass_level = self.level_up_integration.is_subclass_selection_level('rogue', 3)
        self.assertTrue(is_subclass_level)

        is_not_subclass_level = self.level_up_integration.is_subclass_selection_level('rogue', 2)
        self.assertFalse(is_not_subclass_level)

    def test_grant_subclass_features(self):
        """Test granting thief subclass features at level 3"""
        # First set the character's subclass
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE characters SET subclass_id = ? WHERE id = ?", ('thief', 'test_rogue'))

        features = self.feature_manager.grant_subclass_features_for_level('test_rogue', 'thief', 3)

        self.assertEqual(len(features), 2)
        feature_names = [f.feature_name for f in features]
        self.assertIn('Fast Hands', feature_names)
        self.assertIn('Second-Story Work', feature_names)

    def test_level_up_integration(self):
        """Test complete level up process"""
        # Level up to 2
        result = self.level_up_integration.handle_level_up('test_rogue', 2)

        self.assertEqual(result['level'], 2)
        self.assertIn('Cunning Action', result['class_features_granted'])
        self.assertEqual(len(result['subclass_features_granted']), 0)  # No subclass yet

        # Check that rogue progression was updated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level, cunning_action_available FROM rogue_features WHERE character_id = ?", ('test_rogue',))
            result = cursor.fetchone()
            self.assertEqual(result[0], 2)  # Level
            self.assertTrue(result[1])      # Cunning Action available

    def test_get_character_features(self):
        """Test retrieving character features"""
        # Grant some features first
        self.feature_manager.grant_class_features_for_level('test_rogue', 'rogue', 1)
        self.feature_manager.grant_class_features_for_level('test_rogue', 'rogue', 2)

        features = self.feature_manager.get_character_features('test_rogue')

        self.assertEqual(len(features), 3)  # Expertise, Sneak Attack, Cunning Action
        feature_names = [f.feature_name for f in features]
        self.assertIn('Expertise', feature_names)
        self.assertIn('Sneak Attack', feature_names)
        self.assertIn('Cunning Action', feature_names)

    def test_level_up_preview(self):
        """Test level up preview functionality"""
        preview = self.level_up_integration.get_level_up_preview('test_rogue', 3)

        self.assertEqual(preview['level'], 3)
        self.assertIn('Roguish Archetype', preview['class_features'])
        self.assertTrue(preview['requires_subclass_selection'])

    def test_feature_progression_summary(self):
        """Test getting feature progression summary"""
        summary = self.feature_manager.get_feature_progression_summary('rogue', 'thief')

        self.assertIn(1, summary)
        self.assertIn(2, summary)
        self.assertIn(3, summary)

        # Check that both class and subclass features are included
        level_3_features = summary[3]
        class_features = [f for f in level_3_features if f.endswith('(Class)')]
        subclass_features = [f for f in level_3_features if f.endswith('(Subclass)')]

        self.assertTrue(len(class_features) > 0)
        self.assertTrue(len(subclass_features) > 0)

if __name__ == '__main__':
    unittest.main()