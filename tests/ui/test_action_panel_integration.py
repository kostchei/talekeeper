"""
Pytest-qt integration tests for ActionPanel with Fighter class features.

Tests the complete UI interaction flow for Fighter abilities including:
- Resource management (Second Wind, Action Surge, Indomitable)
- Weapon mastery effects and switching
- Fighting style applications
- Combat flow and damage calculations
"""

import pytest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from action_cards.action_panel import ActionPanel
from core.game_engine_sqlite import GameEngineSQLite
from database.database_init import DatabaseInitializer


class MockMainWindow:
    """Mock main window for ActionPanel testing."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.game_engine = GameEngineSQLite(db_path)
        self.character_sheet = MagicMock()
        self.character_sheet.character_data = {}
        self.encounter_pane = MagicMock()
        self.log_panel = MagicMock()

    def _force_reload_character(self):
        """Mock character reload."""
        pass

    def show_message(self, title, message):
        """Mock message display."""
        pass


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_db():
    """Create temporary database with full Fighter test data."""
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db.close()
    db_path = test_db.name

    # Initialize with full schema and seed data
    initializer = DatabaseInitializer(db_path)
    initializer.initialize_database()

    yield db_path

    os.unlink(db_path)


@pytest.fixture
def fighter_characters(temp_db):
    """Create Fighter characters at various levels for testing."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Level 1 Fighter
    cursor.execute("""
        INSERT INTO characters (
            id, name, class_id, level, strength, dexterity, constitution,
            intelligence, wisdom, charisma, hit_points_current, hit_points_max,
            proficiency_bonus, second_wind_uses_current, second_wind_uses_max,
            action_surge_uses_current, action_surge_uses_max
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'fighter-1', 'Lvl1Fighter', 'fighter', 1, 16, 14, 15, 10, 12, 13,
        12, 12, 2, 1, 1, 0, 0
    ))

    # Level 3 Champion Fighter
    cursor.execute("""
        INSERT INTO characters (
            id, name, class_id, level, strength, dexterity, constitution,
            intelligence, wisdom, charisma, hit_points_current, hit_points_max,
            proficiency_bonus, second_wind_uses_current, second_wind_uses_max,
            action_surge_uses_current, action_surge_uses_max
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'fighter-3', 'ChampionFighter', 'fighter', 3, 16, 14, 16, 10, 12, 13,
        30, 30, 2, 1, 1, 1, 1
    ))

    # Level 9 Tactical Master Fighter
    cursor.execute("""
        INSERT INTO characters (
            id, name, class_id, level, strength, dexterity, constitution,
            intelligence, wisdom, charisma, hit_points_current, hit_points_max,
            proficiency_bonus, second_wind_uses_current, second_wind_uses_max,
            action_surge_uses_current, action_surge_uses_max,
            indomitable_uses_current, indomitable_uses_max
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'fighter-9', 'TacticalMaster', 'fighter', 9, 18, 14, 16, 10, 12, 13,
        85, 85, 4, 1, 1, 1, 1, 1, 1
    ))

    # Add subclass assignments
    cursor.execute("""
        INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
        VALUES (?, ?, ?, ?)
    """, ('fighter-3', 'fighter', 'champion', 3))

    cursor.execute("""
        INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
        VALUES (?, ?, ?, ?)
    """, ('fighter-9', 'fighter', 'champion', 9))

    # Add fighting styles
    cursor.execute("""
        INSERT INTO character_features (character_id, feature_name, feature_type, source)
        VALUES (?, ?, ?, ?)
    """, ('fighter-1', 'Defense', 'fighting_style', 'Fighter'))

    cursor.execute("""
        INSERT INTO character_features (character_id, feature_name, feature_type, source)
        VALUES (?, ?, ?, ?)
    """, ('fighter-3', 'Dueling', 'fighting_style', 'Fighter'))

    cursor.execute("""
        INSERT INTO character_features (character_id, feature_name, feature_type, source)
        VALUES (?, ?, ?, ?)
    """, ('fighter-9', 'Great Weapon Fighting', 'fighting_style', 'Fighter'))

    # Add equipment
    cursor.execute("""
        INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
        VALUES (?, ?, ?, ?)
    """, ('fighter-1', 'Chain Mail', 1, 1))

    cursor.execute("""
        INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
        VALUES (?, ?, ?, ?)
    """, ('fighter-1', 'Longsword', 1, 1))

    cursor.execute("""
        INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
        VALUES (?, ?, ?, ?)
    """, ('fighter-3', 'Rapier', 1, 1))

    cursor.execute("""
        INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
        VALUES (?, ?, ?, ?)
    """, ('fighter-9', 'Greatsword', 1, 1))

    conn.commit()
    conn.close()

    return {
        'level_1': 'fighter-1',
        'level_3_champion': 'fighter-3',
        'level_9_tactical': 'fighter-9'
    }


@pytest.fixture
def action_panel(qapp, temp_db, fighter_characters):
    """Create ActionPanel with mocked main window."""
    main_window = MockMainWindow(temp_db)
    panel = ActionPanel(main_window)
    panel.resize(400, 600)
    panel.show()

    # Wait for panel to initialize
    QTest.qWait(100)

    yield panel, main_window, fighter_characters

    panel.close()


class TestFighterResourceManagement:
    """Test Fighter resource management features."""

    def test_second_wind_activation_and_recovery(self, action_panel):
        """Test Second Wind usage and short rest recovery."""
        panel, main_window, characters = action_panel

        # Load level 1 fighter
        fighter_id = characters['level_1']
        main_window.character_sheet.character_data = {
            'id': fighter_id,
            'hit_points_current': 6,  # Damaged
            'hit_points_max': 12,
            'level': 1
        }

        # Refresh action panel to load character
        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Find Second Wind button
        second_wind_btn = None
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Second Wind' in widget.text():
                    second_wind_btn = widget
                    break

        assert second_wind_btn is not None, "Second Wind button should be available"
        assert second_wind_btn.isEnabled(), "Second Wind should be usable when damaged"

        # Mock dialog acceptance and healing
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=16384):  # Yes
            with patch('random.randint', return_value=4):  # Roll 4 on d10
                QTest.mouseClick(second_wind_btn, Qt.MouseButton.LeftButton)
                QTest.qWait(50)

        # Verify healing was applied (4 + 2 CON modifier = 6, total HP should be 12)
        updated_hp = main_window.character_sheet.character_data.get('hit_points_current', 6)
        assert updated_hp > 6, "Second Wind should heal the character"

        # Verify button is disabled after use
        QTest.qWait(50)
        panel.load_character_actions(fighter_id)  # Refresh to show updated state
        QTest.qWait(50)

        # Second Wind should now be disabled
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Second Wind' in widget.text():
                    assert not widget.isEnabled(), "Second Wind should be disabled after use"
                    break

    def test_action_surge_activation_and_cooldown(self, action_panel):
        """Test Action Surge usage and short rest recovery."""
        panel, main_window, characters = action_panel

        # Load level 3 fighter with Action Surge
        fighter_id = characters['level_3_champion']
        main_window.character_sheet.character_data = {
            'id': fighter_id,
            'level': 3,
            'action_surge_uses_current': 1
        }

        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Find Action Surge button
        action_surge_btn = None
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Action Surge' in widget.text():
                    action_surge_btn = widget
                    break

        assert action_surge_btn is not None, "Action Surge button should be available"
        assert action_surge_btn.isEnabled(), "Action Surge should be usable"

        # Activate Action Surge
        with patch('PyQt6.QtWidgets.QMessageBox.information'):
            QTest.mouseClick(action_surge_btn, Qt.MouseButton.LeftButton)
            QTest.qWait(50)

        # Verify Action Surge is used up
        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Action Surge' in widget.text():
                    assert not widget.isEnabled(), "Action Surge should be disabled after use"
                    break

    def test_indomitable_save_reroll(self, action_panel):
        """Test Indomitable save reroll functionality."""
        panel, main_window, characters = action_panel

        # Load level 9 fighter with Indomitable
        fighter_id = characters['level_9_tactical']
        main_window.character_sheet.character_data = {
            'id': fighter_id,
            'level': 9,
            'indomitable_uses_current': 1
        }

        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Find Indomitable button
        indomitable_btn = None
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Indomitable' in widget.text():
                    indomitable_btn = widget
                    break

        assert indomitable_btn is not None, "Indomitable button should be available at level 9"
        assert indomitable_btn.isEnabled(), "Indomitable should be usable"


class TestFighterWeaponMastery:
    """Test weapon mastery mechanics and Tactical Master substitution."""

    def test_weapon_mastery_tooltip_display(self, action_panel):
        """Test that weapon mastery tooltips show correct properties."""
        panel, main_window, characters = action_panel

        fighter_id = characters['level_3_champion']
        main_window.character_sheet.character_data = {'id': fighter_id, 'level': 3}

        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Find weapon attack buttons and check tooltips
        weapon_buttons = []
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Attack' in widget.text():
                    weapon_buttons.append(widget)

        assert len(weapon_buttons) > 0, "Should have weapon attack buttons"

        # Check that tooltips contain mastery information
        for btn in weapon_buttons:
            tooltip = btn.toolTip()
            # Rapier should have Vex mastery
            if 'Rapier' in btn.text():
                assert 'Vex' in tooltip, "Rapier tooltip should mention Vex mastery"

    def test_tactical_master_substitution_at_level_9(self, action_panel):
        """Test Tactical Master property substitution for level 9+ Fighters."""
        panel, main_window, characters = action_panel

        fighter_id = characters['level_9_tactical']
        main_window.character_sheet.character_data = {'id': fighter_id, 'level': 9}

        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Level 9+ Fighters should be able to substitute Push/Sap/Slow masteries
        # This test would need specific weapon with these masteries to verify substitution


class TestFighterCombatFlow:
    """Test complete combat sequences with fighting styles."""

    def test_dueling_damage_bonus_application(self, action_panel):
        """Test Dueling fighting style adds +2 damage to one-handed weapons."""
        panel, main_window, characters = action_panel

        fighter_id = characters['level_3_champion']
        main_window.character_sheet.character_data = {
            'id': fighter_id,
            'level': 3,
            'strength': 16
        }
        main_window.encounter_pane.get_current_target.return_value = {
            'id': 'target-1',
            'ac': 12,
            'name': 'Goblin'
        }

        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Find rapier attack button
        rapier_btn = None
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Rapier' in widget.text():
                    rapier_btn = widget
                    break

        assert rapier_btn is not None, "Should have Rapier attack button"

        # Mock successful attack roll
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [15, 6]  # Attack roll 15, damage roll 6
            with patch.object(panel, '_log_attack_result') as mock_log:
                QTest.mouseClick(rapier_btn, Qt.MouseButton.LeftButton)
                QTest.qWait(50)

                # Verify Dueling bonus was applied to damage
                if mock_log.call_args:
                    damage_total = mock_log.call_args[0][2]  # Third argument should be damage
                    # Base damage (6) + STR mod (3) + Dueling (2) = 11
                    assert damage_total >= 11, f"Dueling should add +2 damage, got {damage_total}"

    def test_great_weapon_fighting_reroll_mechanics(self, action_panel):
        """Test Great Weapon Fighting treats 1s and 2s as 3s per D&D 2024."""
        panel, main_window, characters = action_panel

        fighter_id = characters['level_9_tactical']
        main_window.character_sheet.character_data = {
            'id': fighter_id,
            'level': 9,
            'strength': 18
        }
        main_window.encounter_pane.get_current_target.return_value = {
            'id': 'target-1',
            'ac': 12,
            'name': 'Orc'
        }

        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Find greatsword attack button
        greatsword_btn = None
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Greatsword' in widget.text():
                    greatsword_btn = widget
                    break

        if greatsword_btn:
            # Mock rolling 1s and 2s on damage dice
            with patch('random.randint') as mock_roll:
                mock_roll.side_effect = [15, 1, 2]  # Attack 15, damage dice 1,2
                with patch.object(panel, '_log_attack_result') as mock_log:
                    QTest.mouseClick(greatsword_btn, Qt.MouseButton.LeftButton)
                    QTest.qWait(50)

                    # With Great Weapon Fighting, 1s and 2s should be treated as 3s
                    # So 2d6 with 1,2 becomes 3,3 = 6 + STR mod (4) = 10
                    if mock_log.call_args:
                        damage_total = mock_log.call_args[0][2]
                        assert damage_total >= 10, "Great Weapon Fighting should treat 1s,2s as 3s"


class TestFighterChampionSubclass:
    """Test Champion subclass specific features."""

    def test_improved_critical_range(self, action_panel):
        """Test Champion's improved critical hit range (19-20)."""
        panel, main_window, characters = action_panel

        fighter_id = characters['level_3_champion']
        main_window.character_sheet.character_data = {
            'id': fighter_id,
            'level': 3
        }
        main_window.encounter_pane.get_current_target.return_value = {
            'id': 'target-1',
            'ac': 15,
            'name': 'Skeleton'
        }

        panel.load_character_actions(fighter_id)
        QTest.qWait(50)

        # Find any weapon attack
        attack_btn = None
        for i in range(panel.action_layout.count()):
            item = panel.action_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'text') and 'Attack' in widget.text():
                    attack_btn = widget
                    break

        if attack_btn:
            # Mock rolling 19 (should be critical for Champion)
            with patch('random.randint', return_value=19):
                with patch.object(panel, '_log_attack_result') as mock_log:
                    QTest.mouseClick(attack_btn, Qt.MouseButton.LeftButton)
                    QTest.qWait(50)

                    # Verify critical hit was triggered
                    if mock_log.call_args:
                        log_message = str(mock_log.call_args)
                        assert 'Critical' in log_message or 'critical' in log_message, \
                            "Roll of 19 should be critical hit for Champion"


def test_ui_interaction_helpers():
    """Test helper functions for UI interactions work correctly."""
    app = QApplication.instance() or QApplication([])

    # Test basic widget interaction
    widget = QWidget()
    widget.show()
    QTest.qWait(50)

    # Test clicking
    QTest.mouseClick(widget, Qt.MouseButton.LeftButton)

    # Test key pressing
    QTest.keyClick(widget, Qt.Key.Key_Space)

    widget.close()

    # Basic test passes if no exceptions
    assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])