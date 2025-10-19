#test
import sys
import os
import unittest
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from PyQt6.QtWidgets import QApplication
from talekeeper.ui.condition_display import ConditionDisplayWidget, SpellEffectBadge


class TestSpellEffectDisplay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

        cls.db_path = 'test_spell_effect_display.db'
        cls._create_test_database()

    @classmethod
    def _create_test_database(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

        with sqlite3.connect(cls.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    current_hit_points INTEGER,
                    max_hit_points INTEGER,
                    hit_points_temporary INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_spell_effects (
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
                INSERT INTO characters (id, name, current_hit_points, max_hit_points)
                VALUES ('test-char', 'Test Paladin', 45, 45)
            """)

            conn.commit()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_spell_effect_badge_creation(self):
        badge = SpellEffectBadge(
            spell_name="Shield of Faith",
            effect_type="ac_bonus",
            effect_data={'value': 2},
            rounds_remaining=100,
            concentration=True
        )

        self.assertEqual(badge.text(), "SoF*")
        self.assertIn("Shield of Faith", badge.toolTip())
        self.assertIn("Concentration", badge.toolTip())
        self.assertIn("+2 AC", badge.toolTip())

    def test_spell_effect_badge_divine_favor(self):
        badge = SpellEffectBadge(
            spell_name="Divine Favor",
            effect_type="damage_bonus_per_hit",
            effect_data={'damage_dice': '1d4', 'damage_type': 'radiant'},
            rounds_remaining=10,
            concentration=True
        )

        self.assertEqual(badge.text(), "DvF*")
        self.assertIn("Divine Favor", badge.toolTip())
        self.assertIn("+1d4 radiant damage per hit", badge.toolTip())

    def test_spell_effect_badge_bless(self):
        badge = SpellEffectBadge(
            spell_name="Bless",
            effect_type="attack_and_save_bonus",
            effect_data={'bonus_dice': '1d4'},
            rounds_remaining=10,
            concentration=True
        )

        self.assertEqual(badge.text(), "BLS*")
        self.assertIn("Bless", badge.toolTip())
        self.assertIn("1d4 to attacks/saves", badge.toolTip())

    def test_condition_widget_initialization(self):
        widget = ConditionDisplayWidget(
            character_id='test-char',
            db_path=self.db_path
        )

        self.assertIsNotNone(widget.spell_effects_service)
        self.assertEqual(widget.character_id, 'test-char')

    def test_condition_widget_displays_spell_effects(self):
        from talekeeper.services.spell_effects_service import SpellEffectsService

        spell_service = SpellEffectsService(self.db_path)

        buff_data = {
            'type': 'ac_bonus',
            'value': 2,
            'source': 'shield_of_faith'
        }

        spell_service.apply_buff('test-char', buff_data, duration_rounds=100)

        widget = ConditionDisplayWidget(
            character_id='test-char',
            db_path=self.db_path
        )

        widget.refresh_conditions()

        self.assertEqual(len(widget.badges), 1)
        self.assertIsInstance(widget.badges[0], SpellEffectBadge)

    def test_condition_widget_no_effects(self):
        widget = ConditionDisplayWidget(
            character_id='test-char-empty',
            db_path=self.db_path
        )

        widget.refresh_conditions()

        self.assertEqual(len(widget.badges), 0)
        self.assertEqual(widget.no_conditions_label.text(), "No active conditions or effects")


if __name__ == '__main__':
    unittest.main()
