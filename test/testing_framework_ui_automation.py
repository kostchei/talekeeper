# test
"""
UI Automation Testing Framework - PyQt6 Application Testing
==========================================================

TESTING FRAMEWORK - Exclude from ongoing work

Comprehensive framework for automated testing of TaleKeeper's PyQt6 interface.
Provides utilities for:
- Character creation automation
- Spell action card testing
- Combat interaction testing
- UI element discovery and interaction
- Screenshot capture and verification

Usage:
    python testing_framework_ui_automation.py --test spell_action_cards
    python testing_framework_ui_automation.py --test character_creation
    python testing_framework_ui_automation.py --test all
"""

import sys
import os
import time
import sqlite3
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QComboBox,
    QCheckBox, QSpinBox, QTextEdit, QScrollArea, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtTest import QTest

# Import main application components
from ui.main_window import MainWindow


@dataclass
class TestResult:
    """Represents the result of a UI test."""
    test_name: str
    success: bool
    message: str
    timestamp: datetime
    screenshot_path: Optional[str] = None
    duration_ms: int = 0


class UIAutomationFramework:
    """Core UI automation framework for TaleKeeper testing."""

    def __init__(self, app: QApplication, main_window: MainWindow):
        self.app = app
        self.main_window = main_window
        self.test_results: List[TestResult] = []
        self.screenshot_dir = "testing_framework_screenshots"
        self.current_character_id: Optional[str] = None

        # Create screenshot directory
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def take_screenshot(self, name: str) -> str:
        """Take a screenshot of the main window."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        pixmap = self.main_window.grab()
        pixmap.save(filepath)
        return filepath

    def wait_for_widget(self, widget_finder, timeout_ms: int = 5000) -> Optional[QWidget]:
        """Wait for a widget to become available."""
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout_ms:
            widget = widget_finder()
            if widget and widget.isVisible():
                return widget
            QTest.qWait(100)
        return None

    def find_widget_by_text(self, text: str, widget_type=None) -> Optional[QWidget]:
        """Find a widget by its text content."""
        for widget in self.main_window.findChildren(widget_type or QWidget):
            if hasattr(widget, 'text') and text in widget.text():
                return widget
            elif hasattr(widget, 'currentText') and text in widget.currentText():
                return widget
        return None

    def find_widget_by_object_name(self, object_name: str) -> Optional[QWidget]:
        """Find a widget by its objectName."""
        return self.main_window.findChild(QWidget, object_name)

    def click_widget(self, widget: QWidget) -> bool:
        """Click a widget if it's clickable."""
        if not widget or not widget.isVisible() or not widget.isEnabled():
            return False

        # Ensure widget is visible by scrolling if needed
        self._ensure_widget_visible(widget)

        QTest.mouseClick(widget, Qt.MouseButton.LeftButton)
        QTest.qWait(250)  # Wait for UI to respond
        return True

    def _ensure_widget_visible(self, widget: QWidget):
        """Ensure a widget is visible by scrolling its parent scroll area if needed."""
        parent = widget.parent()
        while parent:
            if isinstance(parent, QScrollArea):
                parent.ensureWidgetVisible(widget)
                break
            parent = parent.parent()

    def set_combo_box_value(self, combo_box: QComboBox, text: str) -> bool:
        """Set a combo box to a specific value."""
        for i in range(combo_box.count()):
            if text in combo_box.itemText(i):
                combo_box.setCurrentIndex(i)
                QTest.qWait(100)
                return True
        return False

    def check_checkbox(self, checkbox: QCheckBox, checked: bool = True) -> bool:
        """Check or uncheck a checkbox."""
        if checkbox.isChecked() != checked:
            self.click_widget(checkbox)
        return checkbox.isChecked() == checked

    def set_spinbox_value(self, spinbox: QSpinBox, value: int) -> bool:
        """Set a spinbox to a specific value."""
        spinbox.setValue(value)
        QTest.qWait(100)
        return spinbox.value() == value


class CharacterCreationAutomator:
    """TESTING FRAMEWORK - Automates character creation process."""

    def __init__(self, framework: UIAutomationFramework):
        self.framework = framework
        self.main_window = framework.main_window

    def create_test_wizard(self, name: str = "TestWizard") -> TestResult:
        """Create a test wizard character with spells."""
        start_time = time.time()

        try:
            # Navigate to character creation
            if not self._start_character_creation():
                return TestResult("create_test_wizard", False, "Failed to start character creation", datetime.now())

            # Select Wizard class
            if not self._select_class("Wizard"):
                return TestResult("create_test_wizard", False, "Failed to select Wizard class", datetime.now())

            # Select spells
            if not self._select_wizard_spells():
                return TestResult("create_test_wizard", False, "Failed to select wizard spells", datetime.now())

            # Complete character creation
            if not self._complete_character_creation(name):
                return TestResult("create_test_wizard", False, "Failed to complete character creation", datetime.now())

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot("wizard_created")

            return TestResult(
                "create_test_wizard", True,
                f"Successfully created wizard '{name}'",
                datetime.now(), screenshot, duration
            )

        except Exception as e:
            return TestResult("create_test_wizard", False, f"Exception: {e}", datetime.now())

    def _start_character_creation(self) -> bool:
        """Start character creation process."""
        # Look for "Create Character" button or menu option
        create_btn = self.framework.find_widget_by_text("Create Character", QPushButton)
        if create_btn:
            return self.framework.click_widget(create_btn)

        # Alternative: Check if already in character creation
        class_selection = self.framework.find_widget_by_text("Class", QLabel)
        return class_selection is not None

    def _select_class(self, class_name: str) -> bool:
        """Select a character class."""
        # Find class selection widgets
        class_widgets = self.main_window.findChildren(QWidget)

        for widget in class_widgets:
            if hasattr(widget, 'text') and class_name in widget.text():
                if self.framework.click_widget(widget):
                    QTest.qWait(500)  # Wait for class features to load
                    return True

        return False

    def _select_wizard_spells(self) -> bool:
        """Select spells for a wizard character."""
        # Look for spell selection interface
        spell_widgets = self.main_window.findChildren(QComboBox)

        # Select cantrips (Fire Bolt, Prestidigitation, Light)
        cantrip_count = 0
        target_cantrips = ["Fire Bolt", "Prestidigitation", "Light"]

        for widget in spell_widgets:
            if cantrip_count >= 3:
                break

            # Try to set cantrip if this looks like a cantrip selector
            parent_text = ""
            if widget.parent():
                parent_labels = widget.parent().findChildren(QLabel)
                parent_text = " ".join([label.text() for label in parent_labels]).lower()

            if "cantrip" in parent_text and cantrip_count < len(target_cantrips):
                if self.framework.set_combo_box_value(widget, target_cantrips[cantrip_count]):
                    cantrip_count += 1

        # Select level 1 spells (Magic Missile, Shield, Mage Armor, etc.)
        spell_checkboxes = self.main_window.findChildren(QCheckBox)
        spell_count = 0
        target_spells = ["Magic Missile", "Shield", "Mage Armor", "Detect Magic", "Burning Hands", "Feather Fall"]

        for checkbox in spell_checkboxes:
            if spell_count >= 6:  # Wizard gets 6 level 1 spells
                break

            checkbox_text = checkbox.text()
            for target_spell in target_spells:
                if target_spell in checkbox_text and not checkbox.isChecked():
                    self.framework.check_checkbox(checkbox, True)
                    spell_count += 1
                    break

        QTest.qWait(500)
        return cantrip_count >= 3 and spell_count >= 6

    def _complete_character_creation(self, name: str) -> bool:
        """Complete the character creation process."""
        # Set character name
        name_input = self.main_window.findChild(QComboBox, "characterNameInput")
        if name_input:
            name_input.setEditText(name)

        # Find and click through creation steps
        next_buttons = self.framework.find_widget_by_text("Next", QPushButton)
        continue_buttons = self.framework.find_widget_by_text("Continue", QPushButton)
        finish_buttons = self.framework.find_widget_by_text("Create Character", QPushButton)

        # Click through steps
        for _ in range(10):  # Max 10 steps to prevent infinite loop
            if finish_buttons and finish_buttons.isVisible():
                return self.framework.click_widget(finish_buttons)
            elif next_buttons and next_buttons.isVisible():
                self.framework.click_widget(next_buttons)
                QTest.qWait(500)
            elif continue_buttons and continue_buttons.isVisible():
                self.framework.click_widget(continue_buttons)
                QTest.qWait(500)
            else:
                break

        return False


class SpellActionCardTester:
    """TESTING FRAMEWORK - Tests spell action card functionality."""

    def __init__(self, framework: UIAutomationFramework):
        self.framework = framework
        self.main_window = framework.main_window

    def test_spell_cards_appear(self, character_id: str) -> TestResult:
        """Test that spell action cards appear for a spellcasting character."""
        start_time = time.time()

        try:
            # Load character
            if not self._load_character(character_id):
                return TestResult("spell_cards_appear", False, "Failed to load character", datetime.now())

            # Start an encounter to see action cards
            if not self._start_test_encounter():
                return TestResult("spell_cards_appear", False, "Failed to start encounter", datetime.now())

            # Look for spell action cards
            spell_cards = self._find_spell_action_cards()

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot("spell_cards_test")

            if spell_cards:
                return TestResult(
                    "spell_cards_appear", True,
                    f"Found {len(spell_cards)} spell action cards",
                    datetime.now(), screenshot, duration
                )
            else:
                return TestResult(
                    "spell_cards_appear", False,
                    "No spell action cards found",
                    datetime.now(), screenshot, duration
                )

        except Exception as e:
            return TestResult("spell_cards_appear", False, f"Exception: {e}", datetime.now())

    def test_spell_casting(self, character_id: str) -> TestResult:
        """Test actually casting a spell from action cards."""
        start_time = time.time()

        try:
            # Load character and start encounter
            if not self._load_character(character_id):
                return TestResult("spell_casting", False, "Failed to load character", datetime.now())

            if not self._start_test_encounter():
                return TestResult("spell_casting", False, "Failed to start encounter", datetime.now())

            # Find and click a spell action card
            spell_cards = self._find_spell_action_cards()
            if not spell_cards:
                return TestResult("spell_casting", False, "No spell cards to test", datetime.now())

            # Click the first spell card
            first_spell = spell_cards[0]
            if not self.framework.click_widget(first_spell):
                return TestResult("spell_casting", False, "Failed to click spell card", datetime.now())

            QTest.qWait(1000)  # Wait for spell casting

            # Check for spell casting feedback in log
            cast_success = self._check_spell_cast_feedback()

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot("spell_cast_test")

            if cast_success:
                return TestResult(
                    "spell_casting", True,
                    "Successfully cast spell from action card",
                    datetime.now(), screenshot, duration
                )
            else:
                return TestResult(
                    "spell_casting", False,
                    "Spell casting did not provide expected feedback",
                    datetime.now(), screenshot, duration
                )

        except Exception as e:
            return TestResult("spell_casting", False, f"Exception: {e}", datetime.now())

    def _load_character(self, character_id: str) -> bool:
        """Load a specific character."""
        # This would need to interact with the character loading UI
        # Implementation depends on how character loading works in the main UI
        return True

    def _start_test_encounter(self) -> bool:
        """Start a test encounter to see action cards."""
        # Look for encounter start button or menu
        encounter_btn = self.framework.find_widget_by_text("Start Encounter", QPushButton)
        if encounter_btn:
            return self.framework.click_widget(encounter_btn)

        # Alternative: check if already in encounter
        action_panel = self.framework.find_widget_by_text("Action", QWidget)
        return action_panel is not None

    def _find_spell_action_cards(self) -> List[QWidget]:
        """Find spell action cards in the UI."""
        spell_cards = []

        # Look for widgets that look like spell cards
        all_widgets = self.main_window.findChildren(QWidget)

        for widget in all_widgets:
            # Check if widget looks like a spell action card
            if hasattr(widget, 'text'):
                text = widget.text().lower()
                if any(keyword in text for keyword in ['spell', 'cantrip', '✨', '⭐', 'fire bolt', 'magic missile']):
                    if isinstance(widget, QPushButton):
                        spell_cards.append(widget)

        return spell_cards

    def _check_spell_cast_feedback(self) -> bool:
        """Check if spell casting produced expected feedback."""
        # Look for combat log or feedback messages
        log_widgets = self.main_window.findChildren(QTextEdit)

        for log in log_widgets:
            log_text = log.toPlainText().lower()
            if any(keyword in log_text for keyword in ['cast', 'spell', 'firebolt', 'magic missile']):
                return True

        return False


class TestRunner:
    """TESTING FRAMEWORK - Main test runner and reporter."""

    def __init__(self):
        self.app = None
        self.main_window = None
        self.framework = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        """Initialize the testing environment."""
        try:
            self.app = QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)

            # Create main window
            self.main_window = MainWindow()
            self.framework = UIAutomationFramework(self.app, self.main_window)

            # Show main window
            self.main_window.show()
            QTest.qWait(1000)  # Wait for UI to load

            return True

        except Exception as e:
            print(f"Setup failed: {e}")
            return False

    def run_character_creation_tests(self):
        """Run character creation tests."""
        print("Running character creation tests...")
        automator = CharacterCreationAutomator(self.framework)

        # Test wizard creation
        result = automator.create_test_wizard("AutoTestWizard")
        self.results.append(result)
        print(f"  Wizard creation: {'PASS' if result.success else 'FAIL'} - {result.message}")

    def run_spell_action_card_tests(self):
        """Run spell action card tests."""
        print("Running spell action card tests...")
        tester = SpellActionCardTester(self.framework)

        # Get a test character (preferably one with spells)
        test_character_id = self._get_test_character_with_spells()

        if test_character_id:
            # Test spell cards appear
            result = tester.test_spell_cards_appear(test_character_id)
            self.results.append(result)
            print(f"  Spell cards appear: {'PASS' if result.success else 'FAIL'} - {result.message}")

            # Test spell casting
            result = tester.test_spell_casting(test_character_id)
            self.results.append(result)
            print(f"  Spell casting: {'PASS' if result.success else 'FAIL'} - {result.message}")
        else:
            print("  No test character with spells found - skipping spell tests")

    def _get_test_character_with_spells(self) -> Optional[str]:
        """Get a character ID that has spells for testing."""
        try:
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()

            # Find a character with spells
            cursor.execute("""
                SELECT DISTINCT c.id, c.name
                FROM characters c
                JOIN character_spells cs ON c.id = cs.character_id
                WHERE c.class_id IN ('wizard', 'cleric', 'warlock', 'paladin')
                LIMIT 1
            """)

            result = cursor.fetchone()
            conn.close()

            if result:
                print(f"  Using test character: {result[1]} ({result[0]})")
                return result[0]

        except Exception as e:
            print(f"  Error finding test character: {e}")

        return None

    def generate_report(self):
        """Generate and save a test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"testing_framework_report_{timestamp}.html"

        html_content = self._generate_html_report()

        with open(report_path, 'w') as f:
            f.write(html_content)

        print(f"\nTest report saved: {report_path}")
        print(f"Screenshots saved in: {self.framework.screenshot_dir}")

    def _generate_html_report(self) -> str:
        """Generate HTML test report."""
        passed = sum(1 for r in self.results if r.success)
        failed = len(self.results) - passed

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TaleKeeper UI Testing Framework Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        .test-result {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
        .screenshot {{ max-width: 300px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>TaleKeeper UI Testing Framework Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><span class="pass">Passed: {passed}</span> | <span class="fail">Failed: {failed}</span></p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <h2>Test Results</h2>
"""

        for result in self.results:
            status_class = "pass" if result.success else "fail"
            status_text = "PASS" if result.success else "FAIL"

            html += f"""
    <div class="test-result">
        <h3>{result.test_name} - <span class="{status_class}">{status_text}</span></h3>
        <p><strong>Message:</strong> {result.message}</p>
        <p><strong>Duration:</strong> {result.duration_ms}ms</p>
        <p><strong>Timestamp:</strong> {result.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</p>
"""

            if result.screenshot_path:
                html += f'<img src="{result.screenshot_path}" class="screenshot" alt="Screenshot for {result.test_name}">'

            html += "</div>"

        html += """
</body>
</html>
"""
        return html

    def cleanup(self):
        """Clean up testing environment."""
        if self.main_window:
            self.main_window.close()
        if self.app:
            self.app.quit()


def main():
    """Main entry point for testing framework."""
    parser = argparse.ArgumentParser(description='TaleKeeper UI Automation Testing Framework')
    parser.add_argument('--test', choices=['all', 'character_creation', 'spell_action_cards'],
                       default='all', help='Which tests to run')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (no GUI)')

    args = parser.parse_args()

    print("TaleKeeper UI Automation Testing Framework")
    print("=" * 50)

    runner = TestRunner()

    try:
        if not runner.setup():
            print("Failed to setup testing environment")
            return 1

        if args.test in ['all', 'character_creation']:
            runner.run_character_creation_tests()

        if args.test in ['all', 'spell_action_cards']:
            runner.run_spell_action_card_tests()

        runner.generate_report()

        # Print summary
        passed = sum(1 for r in runner.results if r.success)
        total = len(runner.results)
        print(f"\nTesting completed: {passed}/{total} tests passed")

        return 0 if passed == total else 1

    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
        return 1
    except Exception as e:
        print(f"Testing failed with exception: {e}")
        return 1
    finally:
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())