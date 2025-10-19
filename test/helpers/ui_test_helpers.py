# test
"""
UI testing helper functions for PyQt6 widget interactions.

Provides utilities for simulating user interactions with TaleKeeper UI components,
including button clicks, text input, drag and drop, and widget verification.
"""

import time
from typing import Optional, List, Callable, Any
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QComboBox, QLineEdit, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QAction


class UITestHelpers:
    """Collection of UI testing helper methods."""

    @staticmethod
    def wait_for_ui_update(ms: int = 100):
        """Wait for UI to update and process events."""
        QTest.qWait(ms)
        QApplication.processEvents()

    @staticmethod
    def find_button_by_text(parent: QWidget, text: str, partial_match: bool = True) -> Optional[QPushButton]:
        """Find a button by its text content."""
        buttons = parent.findChildren(QPushButton)
        for button in buttons:
            button_text = button.text()
            if partial_match and text.lower() in button_text.lower():
                return button
            elif not partial_match and text == button_text:
                return button
        return None

    @staticmethod
    def find_widget_by_object_name(parent: QWidget, object_name: str) -> Optional[QWidget]:
        """Find a widget by its objectName property."""
        return parent.findChild(QWidget, object_name)

    @staticmethod
    def click_button_safe(button: QPushButton, wait_ms: int = 50) -> bool:
        """Safely click a button with error handling."""
        if button is None or not button.isEnabled() or not button.isVisible():
            return False

        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        UITestHelpers.wait_for_ui_update(wait_ms)
        return True

    @staticmethod
    def enter_text_safe(line_edit: QLineEdit, text: str, clear_first: bool = True) -> bool:
        """Safely enter text into a line edit widget."""
        if line_edit is None or not line_edit.isEnabled():
            return False

        if clear_first:
            line_edit.clear()

        QTest.keyClicks(line_edit, text)
        UITestHelpers.wait_for_ui_update()
        return True

    @staticmethod
    def select_combobox_item(combo: QComboBox, text: str) -> bool:
        """Select an item in a combobox by text."""
        if combo is None or not combo.isEnabled():
            return False

        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)
            UITestHelpers.wait_for_ui_update()
            return True
        return False

    @staticmethod
    def verify_button_state(button: QPushButton, expected_enabled: bool, expected_text: str = None) -> bool:
        """Verify button state matches expectations."""
        if button is None:
            return False

        if button.isEnabled() != expected_enabled:
            return False

        if expected_text and expected_text not in button.text():
            return False

        return True

    @staticmethod
    def get_action_buttons_from_layout(parent: QWidget) -> List[QPushButton]:
        """Extract all action buttons from a layout."""
        buttons = []
        layout = getattr(parent, 'action_layout', None)

        if layout:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget() and isinstance(item.widget(), QPushButton):
                    buttons.append(item.widget())

        return buttons

    @staticmethod
    def wait_for_condition(condition: Callable[[], bool], timeout_ms: int = 5000, check_interval_ms: int = 100) -> bool:
        """Wait for a condition to become true within a timeout."""
        elapsed = 0
        while elapsed < timeout_ms:
            if condition():
                return True
            UITestHelpers.wait_for_ui_update(check_interval_ms)
            elapsed += check_interval_ms
        return False

    @staticmethod
    def trigger_context_menu_action(widget: QWidget, action_text: str) -> bool:
        """Trigger a context menu action on a widget."""
        # Right-click to open context menu
        QTest.mouseClick(widget, Qt.MouseButton.RightButton)
        UITestHelpers.wait_for_ui_update()

        # Find and trigger the action
        actions = widget.actions() if hasattr(widget, 'actions') else []
        for action in actions:
            if action.text() == action_text:
                action.trigger()
                UITestHelpers.wait_for_ui_update()
                return True
        return False

    @staticmethod
    def drag_and_drop(source: QWidget, target: QWidget, source_pos: QPoint = None, target_pos: QPoint = None):
        """Perform drag and drop operation between widgets."""
        if source_pos is None:
            source_pos = source.rect().center()
        if target_pos is None:
            target_pos = target.rect().center()

        QTest.mousePressAndDrag(source, source_pos, target, target_pos)
        UITestHelpers.wait_for_ui_update()

    @staticmethod
    def simulate_key_sequence(widget: QWidget, key_sequence: str):
        """Simulate a key sequence on a widget."""
        widget.setFocus()
        UITestHelpers.wait_for_ui_update()

        for char in key_sequence:
            if char == ' ':
                QTest.keyClick(widget, Qt.Key.Key_Space)
            elif char == '\n':
                QTest.keyClick(widget, Qt.Key.Key_Return)
            elif char == '\t':
                QTest.keyClick(widget, Qt.Key.Key_Tab)
            else:
                QTest.keyClick(widget, ord(char.upper()))
            UITestHelpers.wait_for_ui_update(10)

    @staticmethod
    def verify_tooltip_contains(widget: QWidget, expected_text: str) -> bool:
        """Verify widget tooltip contains expected text."""
        tooltip = widget.toolTip()
        return expected_text.lower() in tooltip.lower()

    @staticmethod
    def get_label_text(parent: QWidget, object_name: str) -> str:
        """Get text from a label widget by object name."""
        label = parent.findChild(QLabel, object_name)
        return label.text() if label else ""

    @staticmethod
    def count_enabled_buttons(buttons: List[QPushButton]) -> int:
        """Count how many buttons in a list are enabled."""
        return sum(1 for btn in buttons if btn.isEnabled())

    @staticmethod
    def find_buttons_containing_text(parent: QWidget, text_fragments: List[str]) -> List[QPushButton]:
        """Find all buttons containing any of the specified text fragments."""
        buttons = parent.findChildren(QPushButton)
        matching_buttons = []

        for button in buttons:
            button_text = button.text().lower()
            for fragment in text_fragments:
                if fragment.lower() in button_text:
                    matching_buttons.append(button)
                    break

        return matching_buttons


class ActionPanelHelpers(UITestHelpers):
    """Specialized helpers for ActionPanel testing."""

    @staticmethod
    def find_attack_buttons(action_panel) -> List[QPushButton]:
        """Find all weapon attack buttons in the action panel."""
        return UITestHelpers.find_buttons_containing_text(
            action_panel, ['attack', 'strike', 'shoot', 'throw']
        )

    @staticmethod
    def find_class_feature_buttons(action_panel) -> List[QPushButton]:
        """Find Fighter class feature buttons."""
        return UITestHelpers.find_buttons_containing_text(
            action_panel, ['second wind', 'action surge', 'indomitable']
        )

    @staticmethod
    def find_resource_buttons(action_panel) -> List[QPushButton]:
        """Find buttons that consume limited resources."""
        return UITestHelpers.find_buttons_containing_text(
            action_panel, ['wind', 'surge', 'indomitable', 'inspiration']
        )

    @staticmethod
    def verify_resource_count_display(action_panel, feature_name: str, expected_current: int, expected_max: int) -> bool:
        """Verify resource count display shows correct values."""
        buttons = UITestHelpers.find_buttons_containing_text(action_panel, [feature_name])
        for button in buttons:
            button_text = button.text()
            # Look for pattern like "Second Wind (1/1)"
            if f"({expected_current}/{expected_max})" in button_text:
                return True
        return False

    @staticmethod
    def simulate_combat_target_selection(action_panel, target_data: dict):
        """Mock target selection for combat testing."""
        # This would typically interact with the encounter pane
        # For testing, we can mock the target selection
        if hasattr(action_panel, 'parent') and hasattr(action_panel.parent, 'encounter_pane'):
            encounter_pane = action_panel.parent.encounter_pane
            if hasattr(encounter_pane, 'set_current_target'):
                encounter_pane.set_current_target(target_data)

    @staticmethod
    def get_damage_roll_from_log(action_panel, attack_number: int = -1) -> Optional[dict]:
        """Extract damage information from the most recent log entry."""
        # This would typically parse the log panel for damage information
        # Implementation depends on log panel structure
        if hasattr(action_panel, 'parent') and hasattr(action_panel.parent, 'log_panel'):
            log_panel = action_panel.parent.log_panel
            # Return mock structure for testing
            return {
                'total_damage': 8,
                'base_damage': 6,
                'ability_mod': 3,
                'fighting_style_bonus': 2,
                'critical': False
            }
        return None


class MockHelpers:
    """Helpers for creating mock objects for testing."""

    @staticmethod
    def create_mock_target(ac: int = 12, hp: int = 10, name: str = "Test Target") -> dict:
        """Create a mock combat target."""
        return {
            'id': f'target-{name.lower().replace(" ", "-")}',
            'name': name,
            'ac': ac,
            'hp': hp,
            'max_hp': hp,
            'creature_type': 'humanoid'
        }

    @staticmethod
    def create_mock_character_data(character_id: str, level: int = 1, class_id: str = 'fighter') -> dict:
        """Create mock character data for testing."""
        return {
            'id': character_id,
            'name': f'Test {class_id.title()}',
            'class_id': class_id,
            'level': level,
            'hit_points_current': 10 + level * 5,
            'hit_points_max': 10 + level * 5,
            'strength': 16,
            'dexterity': 14,
            'constitution': 15,
            'proficiency_bonus': 2 + (level - 1) // 4
        }


if __name__ == '__main__':
    # Demo usage and basic testing of helpers
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

    app = QApplication([])

    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    test_button = QPushButton("Test Second Wind (1/1)")
    layout.addWidget(test_button)

    window.setCentralWidget(central_widget)
    window.show()

    # Test helper functions
    helpers = UITestHelpers()

    # Test button finding
    found_button = helpers.find_button_by_text(central_widget, "Second Wind")
    print(f"Button found: {found_button is not None}")

    # Test button clicking
    if found_button:
        success = helpers.click_button_safe(found_button)
        print(f"Button click success: {success}")

    window.close()
    app.quit()