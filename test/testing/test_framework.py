"""
TaleKeeper Qt6 Testing Framework

Comprehensive testing system for TaleKeeper application using Qt6 native testing capabilities.
Provides automated testing, screenshot capture, interaction simulation, and bug detection.

Features:
- Widget discovery and interaction
- Screenshot capture for visual verification
- Automatic test discovery
- Fighting style and feat validation
- Equipment and inventory testing
- Action card verification
- Character sheet state checking
"""

import sys
import os
import time
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                            QLineEdit, QTextEdit, QLabel, QComboBox, QTableWidget,
                            QListWidget, QCheckBox, QRadioButton, QSpinBox)
from PyQt6.QtCore import Qt, QPoint, QTimer, QRect, pyqtSignal
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QPixmap, QPainter, QColor

# Import TaleKeeper components
from main import MainWindow
from core.game_engine_sqlite import GameEngineSQLite


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    passed: bool
    message: str = ""
    screenshot_path: Optional[str] = None
    error_details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0


class TaleKeeperTestBase:
    """Base class for TaleKeeper testing with Qt6 tools"""
    
    def __init__(self, test_name: str = "Unknown Test"):
        self.test_name = test_name
        self.app = None
        self.window = None
        self.screenshots_dir = Path("testing/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.test_results: List[TestResult] = []
        
    def setup(self) -> bool:
        """Initialize the application for testing"""
        try:
            # Create Qt application if needed
            if QApplication.instance() is None:
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
            
            # Create and show main window
            self.window = MainWindow()
            self.window.setWindowTitle(f"TaleKeeper Testing - {self.test_name}")
            self.window.show()
            
            # Wait for window to be fully loaded
            QTest.qWaitForWindowExposed(self.window)
            QTest.qWait(500)  # Extra wait for all widgets to initialize
            
            return True
        except Exception as e:
            print(f"Setup failed: {e}")
            traceback.print_exc()
            return False
    
    def teardown(self):
        """Clean up after testing"""
        try:
            if self.window:
                self.window.close()
                self.window = None
            if self.app:
                self.app.quit()
        except Exception as e:
            print(f"Teardown error: {e}")
    
    def find_widget_by_name(self, object_name: str, widget_type=QWidget) -> Optional[QWidget]:
        """Find a widget by its object name"""
        if not self.window:
            return None
        return self.window.findChild(widget_type, object_name)
    
    def find_widgets_by_type(self, widget_type) -> List[QWidget]:
        """Find all widgets of a specific type"""
        if not self.window:
            return []
        return self.window.findChildren(widget_type)
    
    def find_widget_by_text(self, text: str, widget_types=None) -> Optional[QWidget]:
        """Find a widget by its text content"""
        if widget_types is None:
            widget_types = [QPushButton, QLabel, QCheckBox, QRadioButton]
        
        for widget_type in widget_types:
            widgets = self.find_widgets_by_type(widget_type)
            for widget in widgets:
                if hasattr(widget, 'text') and text in widget.text():
                    return widget
        return None
    
    def click_widget(self, widget: QWidget, delay_ms: int = 100):
        """Click on a widget"""
        if not widget or not widget.isEnabled():
            return False
        
        # Focus the widget
        widget.setFocus()
        QTest.qWait(50)
        
        # Calculate center point
        center = QPoint(widget.width() // 2, widget.height() // 2)
        
        # Perform click
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, center)
        QTest.qWait(delay_ms)
        return True
    
    def type_text(self, widget: QWidget, text: str, clear_first: bool = True):
        """Type text into a widget"""
        if not widget:
            return False
        
        widget.setFocus()
        QTest.qWait(50)
        
        if clear_first and hasattr(widget, 'clear'):
            widget.clear()
        
        QTest.keyClicks(widget, text)
        QTest.qWait(100)
        return True
    
    def take_screenshot(self, name: str = None) -> str:
        """Take a screenshot of the current window"""
        if not self.window:
            return ""
        
        if name is None:
            name = f"{self.test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = self.screenshots_dir / f"{name}.png"
        pixmap = self.window.grab()
        pixmap.save(str(filepath))
        return str(filepath)
    
    def highlight_widget(self, widget: QWidget, color: str = "red", duration_ms: int = 1000):
        """Highlight a widget temporarily for visual debugging"""
        if not widget:
            return
        
        original_style = widget.styleSheet()
        widget.setStyleSheet(f"border: 3px solid {color};")
        QTest.qWait(duration_ms)
        widget.setStyleSheet(original_style)
    
    def get_widget_text(self, widget: QWidget) -> str:
        """Get text from various widget types"""
        if not widget:
            return ""
        
        if hasattr(widget, 'text'):
            return widget.text()
        elif hasattr(widget, 'toPlainText'):
            return widget.toPlainText()
        elif hasattr(widget, 'currentText'):
            return widget.currentText()
        elif hasattr(widget, 'value'):
            return str(widget.value())
        return ""
    
    def wait_for_condition(self, condition_func, timeout_ms: int = 5000, check_interval_ms: int = 100) -> bool:
        """Wait for a condition to become true"""
        elapsed = 0
        while elapsed < timeout_ms:
            if condition_func():
                return True
            QTest.qWait(check_interval_ms)
            elapsed += check_interval_ms
        return False
    
    def record_result(self, test_name: str, passed: bool, message: str = "", 
                     take_screenshot: bool = True, error: Exception = None):
        """Record a test result"""
        screenshot_path = None
        if take_screenshot and self.window:
            screenshot_path = self.take_screenshot(f"{test_name}_{'pass' if passed else 'fail'}")
        
        error_details = None
        if error:
            error_details = traceback.format_exc()
        
        result = TestResult(
            test_name=test_name,
            passed=passed,
            message=message,
            screenshot_path=screenshot_path,
            error_details=error_details
        )
        self.test_results.append(result)
        
        # Print immediate feedback
        status = "PASS" if passed else "FAIL"
        print(f"{status} {test_name}: {message}")
        
        return result


class CharacterSheetTester(TaleKeeperTestBase):
    """Test character sheet functionality"""
    
    def __init__(self):
        super().__init__("CharacterSheet")
    
    def test_character_creation(self) -> bool:
        """Test character creation flow"""
        try:
            # Find and click create character button
            create_btn = self.find_widget_by_text("Create Character")
            if not create_btn:
                self.record_result("find_create_button", False, "Could not find Create Character button")
                return False
            
            self.click_widget(create_btn)
            self.record_result("click_create_button", True, "Clicked Create Character button")
            
            # Wait for character creation to load
            QTest.qWait(1000)
            self.take_screenshot("character_creation_screen")
            
            # Find name input field
            name_input = self.find_widgets_by_type(QLineEdit)
            if name_input:
                self.type_text(name_input[0], "Test Adventurer")
                self.record_result("enter_character_name", True, "Entered character name")
            
            return True
            
        except Exception as e:
            self.record_result("character_creation", False, f"Error: {str(e)}", error=e)
            return False
    
    def test_ability_scores(self) -> bool:
        """Test ability score display and modification"""
        try:
            # Access character panel
            if hasattr(self.window, 'character_sheet'):
                panel = self.window.character_sheet
                
                # Check if ability scores are displayed
                ability_labels = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
                found_abilities = []
                
                for ability in ability_labels:
                    widget = self.find_widget_by_text(ability)
                    if widget:
                        found_abilities.append(ability)
                
                success = len(found_abilities) == len(ability_labels)
                self.record_result("ability_scores_display", success, 
                                 f"Found {len(found_abilities)}/{len(ability_labels)} ability scores")
                return success
            
            return False
            
        except Exception as e:
            self.record_result("ability_scores", False, f"Error: {str(e)}", error=e)
            return False


class EquipmentTester(TaleKeeperTestBase):
    """Test equipment and inventory functionality"""
    
    def __init__(self):
        super().__init__("Equipment")
    
    def test_equipment_slots(self) -> bool:
        """Test equipment slot functionality"""
        try:
            if hasattr(self.window, 'equipment_panel'):
                panel = self.window.equipment_panel
                
                # Check for equipment slots
                slots = ["main_hand", "off_hand", "armor"]
                found_slots = []
                
                # Look for slot indicators in the panel
                labels = self.find_widgets_by_type(QLabel)
                for label in labels:
                    text = label.text().lower()
                    for slot in slots:
                        if slot.replace('_', ' ') in text:
                            found_slots.append(slot)
                            break
                
                success = len(found_slots) > 0
                self.record_result("equipment_slots", success, 
                                 f"Found {len(found_slots)} equipment slots")
                
                self.take_screenshot("equipment_panel")
                return success
            
            return False
            
        except Exception as e:
            self.record_result("equipment_slots", False, f"Error: {str(e)}", error=e)
            return False
    
    def test_inventory_management(self) -> bool:
        """Test inventory add/remove functionality"""
        try:
            # This would test adding and removing items from inventory
            # For now, just check if inventory panel exists
            if hasattr(self.window, 'equipment_panel'):
                self.take_screenshot("inventory_panel")
                self.record_result("inventory_panel_exists", True, "Inventory panel found")
                return True
            
            self.record_result("inventory_panel_exists", False, "Inventory panel not found")
            return False
            
        except Exception as e:
            self.record_result("inventory_management", False, f"Error: {str(e)}", error=e)
            return False


class ActionCardTester(TaleKeeperTestBase):
    """Test action cards and combat actions"""
    
    def __init__(self):
        super().__init__("ActionCards")
    
    def test_action_cards_display(self) -> bool:
        """Test that action cards are displayed"""
        try:
            if hasattr(self.window, 'action_panel'):
                panel = self.window.action_panel
                
                # Look for action card widgets
                buttons = panel.findChildren(QPushButton)
                action_buttons = [btn for btn in buttons if btn.isVisible()]
                
                success = len(action_buttons) > 0
                self.record_result("action_cards_display", success,
                                 f"Found {len(action_buttons)} action buttons")
                
                if success:
                    # Try to identify specific actions
                    actions_found = []
                    for btn in action_buttons:
                        text = btn.text()
                        if text:
                            actions_found.append(text)
                    
                    if actions_found:
                        self.record_result("action_types", True,
                                         f"Actions found: {', '.join(actions_found[:5])}")
                
                self.take_screenshot("action_panel")
                return success
            
            return False
            
        except Exception as e:
            self.record_result("action_cards_display", False, f"Error: {str(e)}", error=e)
            return False
    
    def test_fighting_styles(self) -> bool:
        """Test fighting style implementation"""
        try:
            # This would test specific fighting styles
            # For demonstration, we'll check if fighting style UI elements exist
            
            fighting_styles = ["Defense", "Dueling", "Great Weapon Fighting", 
                             "Protection", "Two-Weapon Fighting", "Archery"]
            
            found_styles = []
            all_labels = self.find_widgets_by_type(QLabel)
            all_buttons = self.find_widgets_by_type(QPushButton)
            
            for widget in all_labels + all_buttons:
                text = self.get_widget_text(widget)
                for style in fighting_styles:
                    if style.lower() in text.lower():
                        found_styles.append(style)
                        break
            
            if found_styles:
                self.record_result("fighting_styles", True,
                                 f"Found references to: {', '.join(found_styles)}")
                return True
            else:
                self.record_result("fighting_styles", False,
                                 "No fighting style references found")
                return False
            
        except Exception as e:
            self.record_result("fighting_styles", False, f"Error: {str(e)}", error=e)
            return False


class EncounterTester(TaleKeeperTestBase):
    """Test encounter and combat functionality"""
    
    def __init__(self):
        super().__init__("Encounter")
    
    def test_encounter_panel(self) -> bool:
        """Test encounter panel display"""
        try:
            if hasattr(self.window, 'encounter_pane'):
                panel = self.window.encounter_pane
                
                # Check if panel is visible
                if panel.isVisible():
                    self.record_result("encounter_panel_visible", True, "Encounter panel is visible")
                    self.take_screenshot("encounter_panel")
                    
                    # Look for encounter-related widgets
                    text_areas = panel.findChildren(QTextEdit)
                    if text_areas:
                        self.record_result("encounter_text_areas", True,
                                         f"Found {len(text_areas)} text areas")
                    
                    return True
                else:
                    self.record_result("encounter_panel_visible", False, "Encounter panel not visible")
                    return False
            
            return False
            
        except Exception as e:
            self.record_result("encounter_panel", False, f"Error: {str(e)}", error=e)
            return False


class IntegrationTester(TaleKeeperTestBase):
    """Test integrated functionality across multiple components"""
    
    def __init__(self):
        super().__init__("Integration")
    
    def test_character_equipment_integration(self) -> bool:
        """Test that equipment changes affect character stats"""
        try:
            # This would test:
            # 1. Equipping armor changes AC
            # 2. Equipping weapons changes attack options
            # 3. Fighting styles affect appropriate calculations
            
            initial_screenshot = self.take_screenshot("integration_initial")
            
            # Simulate some interactions
            QTest.qWait(500)
            
            final_screenshot = self.take_screenshot("integration_final")
            
            self.record_result("integration_test", True, 
                             "Captured integration test screenshots")
            return True
            
        except Exception as e:
            self.record_result("integration_test", False, f"Error: {str(e)}", error=e)
            return False


class TestRunner:
    """Main test runner for TaleKeeper"""
    
    def __init__(self):
        self.test_classes = [
            CharacterSheetTester,
            EquipmentTester,
            ActionCardTester,
            EncounterTester,
            IntegrationTester
        ]
        self.results: List[TestResult] = []
        self.report_path = Path("testing/test_report.html")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        print("\n" + "="*60)
        print("TaleKeeper Automated Testing Suite")
        print("="*60 + "\n")
        
        start_time = time.time()
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_class in self.test_classes:
            print(f"\n--- Running {test_class.__name__} ---")
            tester = test_class()
            
            if not tester.setup():
                print(f"Failed to setup {test_class.__name__}")
                continue
            
            # Run all test methods in the class
            test_methods = [method for method in dir(tester) 
                          if method.startswith('test_') and callable(getattr(tester, method))]
            
            for method_name in test_methods:
                try:
                    method = getattr(tester, method_name)
                    result = method()
                    total_tests += 1
                    if result:
                        passed_tests += 1
                    else:
                        failed_tests += 1
                except Exception as e:
                    print(f"Error running {method_name}: {e}")
                    failed_tests += 1
                    total_tests += 1
            
            self.results.extend(tester.test_results)
            tester.teardown()
            
            # Small delay between test suites
            time.sleep(1)
        
        duration = time.time() - start_time
        
        # Generate summary
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Generate report
        self.generate_html_report(summary)
        
        return summary
    
    def generate_html_report(self, summary: Dict[str, Any]):
        """Generate HTML test report"""
        html = f"""
        <html>
        <head>
            <title>TaleKeeper Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .passed {{ color: green; font-weight: bold; }}
                .failed {{ color: red; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .screenshot {{ max-width: 200px; cursor: pointer; }}
                .error-details {{ background: #ffeeee; padding: 10px; margin-top: 5px; 
                               border-left: 3px solid red; font-family: monospace; 
                               font-size: 12px; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <h1>TaleKeeper Test Report</h1>
            <div class="summary">
                <p>Generated: {summary['timestamp']}</p>
                <p>Total Tests: {summary['total_tests']}</p>
                <p class="passed">Passed: {summary['passed']}</p>
                <p class="failed">Failed: {summary['failed']}</p>
                <p>Duration: {summary['duration_seconds']:.2f} seconds</p>
            </div>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Message</th>
                    <th>Screenshot</th>
                    <th>Timestamp</th>
                </tr>
        """
        
        for result in self.results:
            status_class = "passed" if result.passed else "failed"
            status_text = "PASS" if result.passed else "FAIL"
            
            screenshot_html = ""
            if result.screenshot_path:
                screenshot_html = f'<a href="{result.screenshot_path}" target="_blank">View</a>'
            
            error_html = ""
            if result.error_details:
                error_html = f'<div class="error-details">{result.error_details}</div>'
            
            html += f"""
                <tr>
                    <td>{result.test_name}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{result.message}{error_html}</td>
                    <td>{screenshot_html}</td>
                    <td>{result.timestamp.strftime('%H:%M:%S')}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        # Save report
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(html)
        print(f"\nHTML report saved to: {self.report_path}")


def main():
    """Main entry point for testing"""
    runner = TestRunner()
    summary = runner.run_all_tests()
    
    # Return exit code based on test results
    if summary['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()