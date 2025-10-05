"""
Comprehensive tests for Paladin Divine Smite functionality.

Tests the complete Divine Smite flow including:
- Dialog appearance conditions (HP threshold, spell slots)
- Damage calculation and critical hits
- Spell slot consumption
- UI interaction and dialog behavior
"""

import pytest
import sqlite3
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from action_cards.action_panel import ActionPanel
from action_cards.divine_smite_dialog import DivineSmiteDialog
from services.paladin_abilities import PaladinAbilitiesService
from services.spellcasting_service import get_spellcasting_service
from core.game_engine_sqlite import GameEngineSQLite
from database.database_init import DatabaseInitializer
import tempfile
import os


class TestDivineSmiteFunctionality:
    """Test Paladin Divine Smite mechanics."""

    @pytest.fixture
    def qapp(self):
        """Create or get QApplication instance."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    @pytest.fixture
    def temp_db(self):
        """Create temporary database with test data."""
        test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        test_db.close()
        db_path = test_db.name

        # Initialize database
        initializer = DatabaseInitializer(db_path)
        initializer.initialize(force=True)

        yield db_path

        # Cleanup - try to remove file
        try:
            os.unlink(db_path)
        except (PermissionError, FileNotFoundError):
            pass  # File might be locked, cleanup will happen later

    @pytest.fixture
    def paladin_character(self, temp_db):
        """Create a test Paladin character with spell slots."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create level 5 Paladin
        character_id = 'paladin-test-1'
        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, subclass_id, level,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                hit_points_current, hit_points_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, 'TestPaladin', 'paladin', 'devotion', 5,
            16, 12, 14, 10, 13, 16,  # CHA 16 for spellcasting
            38, 38
        ))

        # Initialize Paladin features
        paladin_service = PaladinAbilitiesService(temp_db)
        paladin_service.initialize_paladin_character(character_id, 'devotion')

        # Initialize spellcasting
        spellcasting_service = get_spellcasting_service(temp_db)
        spellcasting_service.initialize_character_spellcasting(character_id, 'paladin')

        # Add spell slots for level 5 Paladin (4 1st level, 2 2nd level)
        cursor.execute("""
            INSERT OR REPLACE INTO character_spell_slots
            (character_id, spell_level, max_slots, used_slots, slot_type)
            VALUES (?, ?, ?, ?, ?)
        """, (character_id, 1, 4, 0, 'standard'))

        cursor.execute("""
            INSERT OR REPLACE INTO character_spell_slots
            (character_id, spell_level, max_slots, used_slots, slot_type)
            VALUES (?, ?, ?, ?, ?)
        """, (character_id, 2, 2, 0, 'standard'))

        # Add a weapon
        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, (character_id, 'Longsword', 1, 1))

        conn.commit()
        conn.close()

        return character_id

    @pytest.fixture
    def action_panel(self, qapp, temp_db, paladin_character):
        """Create ActionPanel with Paladin character."""
        # Create mock parent window
        mock_parent = MagicMock()
        mock_parent.db_path = temp_db
        mock_parent.game_engine = GameEngineSQLite(temp_db)
        mock_parent.log_panel = MagicMock()
        mock_parent.encounter_pane = MagicMock()
        mock_parent.character_sheet = MagicMock()

        # Create action panel
        panel = ActionPanel(parent=mock_parent)

        # Load Paladin character
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM characters WHERE id = ?
        """, (paladin_character,))
        char_data = cursor.fetchone()

        # Convert to dict - check the actual column count
        col_names = [desc[0] for desc in cursor.description]
        character_context = dict(zip(col_names, char_data))

        panel.character_context = character_context
        conn.close()

        yield panel

        panel.close()

    def test_smite_dialog_appears_when_monster_survives(self, action_panel, temp_db):
        """Test that Divine Smite dialog appears when monster would survive base damage."""
        # Create a mock monster with enough HP to survive
        mock_monster = {
            'id': 'monster-1',
            'name': 'Orc',
            'type': 'Humanoid',
            'current_hp': 30,
            'max_hp': 30,
            'ac': 12
        }

        # Mock the encounter panel to return our monster
        action_panel.parent().encounter_pane.get_selected_monster = MagicMock(return_value=mock_monster)

        # Track if dialog was shown
        dialog_shown = False
        original_exec = QDialog.exec

        def mock_exec(self):
            nonlocal dialog_shown
            if isinstance(self, DivineSmiteDialog):
                dialog_shown = True
                # Simulate declining smite
                self.smite_declined.emit()
                return QDialog.DialogCode.Rejected
            return original_exec(self)

        with patch.object(QDialog, 'exec', mock_exec):
            # Simulate successful attack with base damage of 8
            with patch('random.randint') as mock_roll:
                # Roll sequence: attack(15), damage(6), no smite
                mock_roll.side_effect = [15, 6]

                context = {
                    'name': 'Longsword',
                    'damage': '1d8',
                    'damage_type': 'slashing',
                    'properties': ['versatile'],
                    'target_monster_id': 'monster-1'
                }

                # Execute attack
                action_panel._execute_attack_without_initiative(
                    action_panel.ActionType.ATTACK_MAIN_HAND,
                    context,
                    action_panel.parent().encounter_pane
                )

        # Dialog should have appeared since monster survives (30 HP > ~8 damage)
        assert dialog_shown, "Divine Smite dialog should appear when monster survives"

    def test_smite_dialog_not_shown_when_monster_dies(self, action_panel, temp_db):
        """Test that Divine Smite dialog doesn't appear when monster would die anyway."""
        # Create a low HP monster
        mock_monster = {
            'id': 'monster-2',
            'name': 'Goblin',
            'type': 'Humanoid',
            'current_hp': 5,
            'max_hp': 7,
            'ac': 10
        }

        action_panel.parent().encounter_pane.get_selected_monster = MagicMock(return_value=mock_monster)

        dialog_shown = False
        original_exec = QDialog.exec

        def mock_exec(self):
            nonlocal dialog_shown
            if isinstance(self, DivineSmiteDialog):
                dialog_shown = True
            return original_exec(self)

        with patch.object(QDialog, 'exec', mock_exec):
            with patch('random.randint') as mock_roll:
                # High damage roll that would kill goblin
                mock_roll.side_effect = [15, 8]

                context = {
                    'name': 'Longsword',
                    'damage': '1d8',
                    'damage_type': 'slashing',
                    'properties': ['versatile'],
                    'target_monster_id': 'monster-2'
                }

                action_panel._execute_attack_without_initiative(
                    action_panel.ActionType.ATTACK_MAIN_HAND,
                    context,
                    action_panel.parent().encounter_pane
                )

        # Dialog should NOT appear since monster dies (5 HP < ~11 damage)
        assert not dialog_shown, "Divine Smite dialog should not appear when monster would die anyway"

    def test_smite_damage_on_critical_hit(self, action_panel, temp_db):
        """Test that Divine Smite damage is doubled on critical hits."""
        mock_monster = {
            'id': 'monster-3',
            'name': 'Ogre',
            'type': 'Giant',
            'current_hp': 50,
            'max_hp': 50,
            'ac': 11
        }

        action_panel.parent().encounter_pane.get_selected_monster = MagicMock(return_value=mock_monster)

        smite_damage_captured = 0

        def mock_exec(self):
            if isinstance(self, DivineSmiteDialog):
                # Check that dialog shows it's a critical hit
                assert self.is_critical, "Dialog should indicate critical hit"
                # Choose 1st level spell slot
                self.smite_chosen.emit(1, False)
                return QDialog.DialogCode.Accepted
            return QDialog.DialogCode.Rejected

        with patch.object(QDialog, 'exec', mock_exec):
            with patch('random.randint') as mock_roll:
                # Natural 20 (crit), weapon damage, smite damage
                # For crit: weapon dice doubled, smite dice doubled
                mock_roll.side_effect = [
                    20,  # Attack roll (critical)
                    6, 6,  # Weapon damage (1d8 doubled)
                    3, 4,  # Smite damage (2d8 base)
                    5, 6   # Smite crit damage (2d8 doubled)
                ]

                context = {
                    'name': 'Longsword',
                    'damage': '1d8',
                    'damage_type': 'slashing',
                    'properties': ['versatile'],
                    'target_monster_id': 'monster-3'
                }

                # Track damage application
                def capture_damage(monster_id, damage):
                    nonlocal smite_damage_captured
                    smite_damage_captured = damage

                action_panel.parent().encounter_pane._apply_damage_to_monster = capture_damage

                action_panel._execute_attack_without_initiative(
                    action_panel.ActionType.ATTACK_MAIN_HAND,
                    context,
                    action_panel.parent().encounter_pane
                )

        # Verify damage includes doubled smite dice
        # Base: 6+6 (weapon crit) + 3 (STR) + 3+4+5+6 (smite crit) = 33
        assert smite_damage_captured >= 30, f"Critical hit should double smite dice, got {smite_damage_captured}"

    def test_spell_slot_consumption(self, action_panel, temp_db, paladin_character):
        """Test that using Divine Smite properly consumes spell slots."""
        mock_monster = {
            'id': 'monster-4',
            'name': 'Zombie',
            'type': 'Undead',  # Bonus damage!
            'current_hp': 25,
            'max_hp': 25,
            'ac': 8
        }

        action_panel.parent().encounter_pane.get_selected_monster = MagicMock(return_value=mock_monster)

        def mock_exec(self):
            if isinstance(self, DivineSmiteDialog):
                # Use 2nd level spell slot
                self.smite_chosen.emit(2, True)  # True for undead
                return QDialog.DialogCode.Accepted
            return QDialog.DialogCode.Rejected

        # Check initial spell slots
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT used_slots FROM character_spell_slots
            WHERE character_id = ? AND spell_level = 2
        """, (paladin_character,))
        initial_used = cursor.fetchone()[0]
        assert initial_used == 0, "Should start with unused spell slots"

        with patch.object(QDialog, 'exec', mock_exec):
            with patch('random.randint') as mock_roll:
                # Standard hit and damage
                mock_roll.side_effect = [15] + [4] * 10  # Hit, then damage rolls

                context = {
                    'name': 'Longsword',
                    'damage': '1d8',
                    'damage_type': 'slashing',
                    'properties': ['versatile'],
                    'target_monster_id': 'monster-4'
                }

                action_panel._execute_attack_without_initiative(
                    action_panel.ActionType.ATTACK_MAIN_HAND,
                    context,
                    action_panel.parent().encounter_pane
                )

        # Check spell slot was consumed
        cursor.execute("""
            SELECT used_slots FROM character_spell_slots
            WHERE character_id = ? AND spell_level = 2
        """, (paladin_character,))
        final_used = cursor.fetchone()[0]
        conn.close()

        assert final_used == 1, "Spell slot should be consumed after using Divine Smite"

    def test_no_dialog_for_non_paladin(self, qapp, temp_db):
        """Test that Divine Smite dialog doesn't appear for non-Paladin classes."""
        # Create a Fighter character
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        fighter_id = 'fighter-test-1'
        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                hit_points_current, hit_points_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fighter_id, 'TestFighter', 'fighter', 5,
            16, 14, 15, 10, 12, 13,
            44, 44
        ))

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, (fighter_id, 'Longsword', 1, 1))

        conn.commit()
        conn.close()

        # Create action panel with Fighter
        mock_parent = MagicMock()
        mock_parent.db_path = temp_db
        mock_parent.game_engine = GameEngineSQLite(temp_db)
        mock_parent.log_panel = MagicMock()
        mock_parent.encounter_pane = MagicMock()

        panel = ActionPanel(parent=mock_parent)
        panel.character_context = {'id': fighter_id, 'class_id': 'fighter', 'level': 5}

        mock_monster = {
            'id': 'monster-5',
            'name': 'Orc',
            'type': 'Humanoid',
            'current_hp': 30,
            'max_hp': 30,
            'ac': 12
        }

        panel.parent().encounter_pane.get_selected_monster = MagicMock(return_value=mock_monster)

        dialog_shown = False

        def mock_exec(self):
            nonlocal dialog_shown
            if isinstance(self, DivineSmiteDialog):
                dialog_shown = True
            return QDialog.DialogCode.Rejected

        with patch.object(QDialog, 'exec', mock_exec):
            with patch('random.randint', side_effect=[15, 6]):
                context = {
                    'name': 'Longsword',
                    'damage': '1d8',
                    'damage_type': 'slashing',
                    'target_monster_id': 'monster-5'
                }

                panel._execute_attack_without_initiative(
                    panel.ActionType.ATTACK_MAIN_HAND,
                    context,
                    panel.parent().encounter_pane
                )

        assert not dialog_shown, "Divine Smite should not appear for non-Paladin classes"

        panel.close()


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])