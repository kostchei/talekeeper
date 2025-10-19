#test
"""
Pytest-qt integration tests for Rest System restrictions.

Tests the complete UI interaction flow for rest restrictions including:
- Cannot rest during active combat (monsters present)
- Cannot rest during active hazards
- Ration consumption on long rest
- Short rest vs long rest mechanics
"""

import pytest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from action_cards.action_panel import ActionPanel, ActionType
from database.database_init import DatabaseInitializer


class MockEncounterInstance:
    """Mock for EncounterInstance to avoid database dependencies."""

    def __init__(self, id, encounter_id, monster_id, monster_name,
                 max_hit_points, current_hit_points, armor_class, initiative):
        self.id = id
        self.encounter_id = encounter_id
        self.monster_id = monster_id
        self.monster_name = monster_name
        self.max_hit_points = max_hit_points
        self.current_hit_points = current_hit_points
        self.armor_class = armor_class
        self.initiative = initiative

    @property
    def is_alive(self):
        return self.current_hit_points > 0


class MockLogPanel:
    """Mock log panel to capture messages."""

    def __init__(self):
        self.messages = []

    def log_combat(self, message):
        self.messages.append(message)
        print(f"[LOG] {message}")

    def add_message(self, message):
        self.messages.append(message)
        print(f"[LOG] {message}")

    def clear(self):
        self.messages = []

    def contains(self, text):
        return any(text in msg for msg in self.messages)


class MockMainWindow(QWidget):
    """Mock main window for ActionPanel testing."""

    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.character_sheet = MagicMock()
        self.character_sheet.character_data = {}
        self.encounter_panel = None
        self.log_panel = MockLogPanel()

    def _force_reload_character(self):
        pass

    def show_message(self, title, message):
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
    """Create temporary database with full schema and seed data."""
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db.close()
    db_path = test_db.name

    initializer = DatabaseInitializer(db_path)
    initializer.initialize(force=True)

    yield db_path

    try:
        os.unlink(db_path)
    except PermissionError:
        pass


@pytest.fixture
def test_character(temp_db):
    """Get an existing test character and add rations."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM characters LIMIT 1")
    result = cursor.fetchone()

    if result:
        character_id = result[0]

        cursor.execute("""
            INSERT OR REPLACE INTO character_inventory (character_id, item_name, item_type, quantity, equipped)
            VALUES (?, ?, ?, ?, ?)
        """, (character_id, 'Rations', 'gear', 5, 0))

        conn.commit()
        conn.close()
        return character_id

    conn.close()
    pytest.skip("No test character available in database")


@pytest.fixture
def action_panel_with_encounter(qapp, temp_db, test_character):
    """Create ActionPanel with mocked encounter panel for testing."""
    main_window = MockMainWindow(temp_db)

    encounter_panel = MagicMock()
    encounter_panel.encounter_instances = {}
    encounter_panel.current_encounter = None
    main_window.encounter_panel = encounter_panel

    panel = ActionPanel(main_window)
    panel.resize(800, 200)
    panel.show()

    main_window.character_sheet.character_data = {
        'id': test_character,
        'hit_points_current': 25,
        'hit_points_max': 45,
        'level': 5
    }

    QTest.qWait(100)

    yield panel, encounter_panel, main_window, test_character

    panel.close()
    main_window.close()


class TestRestRestrictionsDuringCombat:
    """Test that rest is blocked when monsters are present."""

    def test_rest_blocked_with_active_monster(self, action_panel_with_encounter):
        """Test that rest button is blocked when monsters are alive."""
        panel, encounter_panel, main_window, character_id = action_panel_with_encounter

        monster = MockEncounterInstance(
            id='monster-1',
            encounter_id='enc-1',
            monster_id='goblin',
            monster_name='Goblin',
            max_hit_points=7,
            current_hit_points=7,
            armor_class=13,
            initiative=10
        )
        encounter_panel.encounter_instances = {'monster-1': monster}
        encounter_panel.current_encounter = MagicMock()

        main_window.log_panel.clear()

        panel._handle_rest_action({'id': character_id})
        QTest.qWait(100)

        assert main_window.log_panel.contains("Cannot rest while monsters are present"), \
            "Rest should be blocked when monsters are alive"
        print("[PASS] Rest correctly blocked with active monster")

    def test_rest_allowed_after_monsters_defeated(self, action_panel_with_encounter):
        """Test that rest is allowed after all monsters are dead."""
        panel, encounter_panel, main_window, character_id = action_panel_with_encounter

        monster = MockEncounterInstance(
            id='monster-1',
            encounter_id='enc-1',
            monster_id='goblin',
            monster_name='Goblin',
            max_hit_points=7,
            current_hit_points=0,
            armor_class=13,
            initiative=10
        )
        encounter_panel.encounter_instances = {'monster-1': monster}
        encounter_panel.current_encounter = None

        main_window.log_panel.clear()

        with patch('PyQt6.QtWidgets.QDialog.exec'):
            panel._handle_rest_action({'id': character_id})
            QTest.qWait(100)

        assert not main_window.log_panel.contains("Cannot rest while monsters are present"), \
            "Rest should be allowed when monsters are dead"
        print("[PASS] Rest correctly allowed after monsters defeated")

    def test_rest_blocked_with_multiple_monsters(self, action_panel_with_encounter):
        """Test that rest is blocked when at least one monster is alive."""
        panel, encounter_panel, main_window, character_id = action_panel_with_encounter

        monster1 = MockEncounterInstance(
            id='monster-1',
            encounter_id='enc-1',
            monster_id='goblin',
            monster_name='Goblin',
            max_hit_points=7,
            current_hit_points=0,
            armor_class=13,
            initiative=10
        )

        monster2 = MockEncounterInstance(
            id='monster-2',
            encounter_id='enc-1',
            monster_id='goblin-2',
            monster_name='Goblin Archer',
            max_hit_points=7,
            current_hit_points=5,
            armor_class=13,
            initiative=12
        )

        encounter_panel.encounter_instances = {
            'monster-1': monster1,
            'monster-2': monster2
        }
        encounter_panel.current_encounter = MagicMock()

        main_window.log_panel.clear()

        panel._handle_rest_action({'id': character_id})
        QTest.qWait(100)

        assert main_window.log_panel.contains("Cannot rest while monsters are present"), \
            "Rest should be blocked when at least one monster is alive"
        print("[PASS] Rest correctly blocked with one alive monster among many")


class TestRestRationConsumption:
    """Test ration consumption mechanics for long rest."""

    def test_long_rest_consumes_ration(self, action_panel_with_encounter):
        """Test that long rest consumes one ration."""
        panel, encounter_panel, main_window, character_id = action_panel_with_encounter

        encounter_panel.encounter_instances = {}
        encounter_panel.current_encounter = None

        conn = sqlite3.connect(main_window.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (character_id,))
        initial_rations = cursor.fetchone()[0]
        conn.close()

        from PyQt6.QtWidgets import QDialog
        mock_dialog = MagicMock(spec=QDialog)
        mock_dialog.accept = MagicMock()

        with patch('PyQt6.QtWidgets.QDialog', return_value=mock_dialog):
            with patch.object(mock_dialog, 'exec'):
                panel._handle_rest_action({'id': character_id})
                QTest.qWait(50)

                long_rest_btn = None
                for child in mock_dialog.findChildren(QPushButton):
                    if 'Long Rest' in child.text():
                        long_rest_btn = child
                        break

                if long_rest_btn:
                    panel._take_long_rest(mock_dialog)
                    QTest.qWait(100)

        conn = sqlite3.connect(main_window.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (character_id,))
        final_rations = cursor.fetchone()[0]
        conn.close()

        assert final_rations == initial_rations - 1, \
            f"Long rest should consume 1 ration (had {initial_rations}, now {final_rations})"
        print(f"[PASS] Long rest consumed ration: {initial_rations} -> {final_rations}")

    def test_long_rest_blocked_without_rations(self, action_panel_with_encounter):
        """Test that long rest is blocked when character has no rations."""
        panel, encounter_panel, main_window, character_id = action_panel_with_encounter

        encounter_panel.encounter_instances = {}
        encounter_panel.current_encounter = None

        conn = sqlite3.connect(main_window.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (character_id,))
        conn.commit()
        conn.close()

        main_window.log_panel.clear()

        from PyQt6.QtWidgets import QDialog
        mock_dialog = MagicMock(spec=QDialog)

        with patch('PyQt6.QtWidgets.QDialog', return_value=mock_dialog):
            panel._take_long_rest(mock_dialog)
            QTest.qWait(100)

        assert main_window.log_panel.contains("need a ration"), \
            "Long rest should be blocked without rations"
        print("[PASS] Long rest correctly blocked without rations")


class TestShortRestMechanics:
    """Test short rest functionality."""

    def test_short_rest_does_not_consume_rations(self, action_panel_with_encounter):
        """Test that short rest does NOT consume rations."""
        panel, encounter_panel, main_window, character_id = action_panel_with_encounter

        encounter_panel.encounter_instances = {}
        encounter_panel.current_encounter = None

        conn = sqlite3.connect(main_window.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (character_id,))
        initial_rations = cursor.fetchone()[0]
        conn.close()

        from PyQt6.QtWidgets import QDialog
        mock_dialog = MagicMock(spec=QDialog)
        mock_dialog.accept = MagicMock()

        panel._take_short_rest(mock_dialog)
        QTest.qWait(100)

        conn = sqlite3.connect(main_window.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quantity FROM character_inventory
            WHERE character_id = ? AND item_name = 'Rations'
        """, (character_id,))
        final_rations = cursor.fetchone()[0]
        conn.close()

        assert final_rations == initial_rations, \
            f"Short rest should NOT consume rations (had {initial_rations}, now {final_rations})"
        print(f"[PASS] Short rest did not consume rations: {initial_rations} -> {final_rations}")


class TestRestHazardRestrictions:
    """Test that rest is blocked during active hazards."""

    def test_rest_blocked_with_active_hazard(self, action_panel_with_encounter):
        """Test that rest is blocked when hazards are active."""
        panel, encounter_panel, main_window, character_id = action_panel_with_encounter

        encounter_panel.encounter_instances = {}
        encounter_panel.current_encounter = None

        mock_hazard_widget = MagicMock()
        mock_hazard_widget.current_hazard = {'name': 'Fire Trap'}
        encounter_panel.hazard_widget = mock_hazard_widget

        main_window.log_panel.clear()

        panel._handle_rest_action({'id': character_id})
        QTest.qWait(100)

        assert main_window.log_panel.contains("Cannot rest while hazards are active"), \
            "Rest should be blocked when hazards are active"
        print("[PASS] Rest correctly blocked with active hazard")


def test_monsters_present_detection():
    """Unit test for _monsters_present() method."""
    app = QApplication.instance() or QApplication([])

    main_window = MagicMock()
    panel = ActionPanel(main_window)

    mock_encounter_panel = MagicMock()

    alive_monster = MagicMock()
    alive_monster.is_alive = True
    alive_monster.current_hit_points = 5
    alive_monster.monster_name = "Goblin"

    mock_encounter_panel.encounter_instances = {'monster-1': alive_monster}
    main_window.encounter_panel = mock_encounter_panel

    result = panel._monsters_present()
    assert result is True, "_monsters_present should return True with alive monsters"
    print("[PASS] _monsters_present() correctly detects alive monsters")

    mock_encounter_panel.encounter_instances = {}
    result = panel._monsters_present()
    assert result is False, "_monsters_present should return False with no monsters"
    print("[PASS] _monsters_present() correctly returns False with no monsters")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])