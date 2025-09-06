"""
Test Fighter Abilities Implementation
Tests Second Wind, Action Surge, and other Fighter features using Qt6 testing framework
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from testing.test_framework import TaleKeeperTestBase, TestResult
from typing import List
import time

class FighterAbilitiesTest(TaleKeeperTestBase):
    """Test Fighter abilities by actually clicking action cards"""
    
    def __init__(self):
        super().__init__("Fighter Abilities Test")
    
    def test_second_wind_ability(self) -> TestResult:
        """Test Second Wind ability by clicking the action card"""
        start_time = time.time()
        
        try:
            # First load a Fighter character
            if not self._load_fighter_character():
                return TestResult("Second Wind", False, "Failed to load Fighter character")
            
            # Take screenshot before test
            before_screenshot = self.take_screenshot("second_wind_before")
            
            # Find Second Wind action card
            second_wind_button = None
            action_panel = self.find_widget_by_name("action_panel")
            if action_panel:
                # Look for Second Wind button in action cards
                buttons = action_panel.findChildren(QPushButton)
                print(f"Found {len(buttons)} buttons in action panel:")
                for i, button in enumerate(buttons):
                    print(f"  Button {i}: '{button.text()}' (enabled: {button.isEnabled()})")
                    if "Second Wind" in button.text() or "❤️" in button.text():
                        second_wind_button = button
                        break
            
            if not second_wind_button:
                return TestResult("Second Wind", False, "Could not find Second Wind action card")
            
            # Check character's HP before using Second Wind
            character_panel = self.find_widget_by_name("character_panel") 
            hp_before = self._get_current_hp()
            
            # Click Second Wind button
            print(f"Clicking Second Wind button: {second_wind_button.text()}")
            QTest.mouseClick(second_wind_button, Qt.MouseButton.LeftButton)
            QTest.qWait(1000)  # Wait for animation/effects
            
            # Check HP after
            hp_after = self._get_current_hp()
            
            # Take screenshot after test
            after_screenshot = self.take_screenshot("second_wind_after")
            
            # Verify HP increased
            if hp_after > hp_before:
                healing = hp_after - hp_before
                duration = (time.time() - start_time) * 1000
                return TestResult("Second Wind", True, 
                               f"Second Wind healed {healing} HP ({hp_before} → {hp_after})",
                               after_screenshot, None, duration_ms=duration)
            else:
                return TestResult("Second Wind", False, 
                               f"HP did not increase: {hp_before} → {hp_after}")
                
        except Exception as e:
            return TestResult("Second Wind", False, f"Error: {str(e)}", error_details=str(e))
    
    def test_action_surge_ability(self) -> TestResult:
        """Test Action Surge ability by clicking the action card"""
        start_time = time.time()
        
        try:
            # Find Action Surge action card
            action_surge_button = None
            action_panel = self.find_widget_by_name("action_panel")
            if action_panel:
                buttons = action_panel.findChildren(QPushButton)
                for button in buttons:
                    if "Action Surge" in button.text() or "⚡" in button.text():
                        action_surge_button = button
                        break
            
            if not action_surge_button:
                return TestResult("Action Surge", False, "Could not find Action Surge action card")
            
            # Take screenshot before
            before_screenshot = self.take_screenshot("action_surge_before")
            
            # Click Action Surge button
            print(f"Clicking Action Surge button: {action_surge_button.text()}")
            QTest.mouseClick(action_surge_button, Qt.MouseButton.LeftButton)
            QTest.qWait(1000)
            
            # Take screenshot after
            after_screenshot = self.take_screenshot("action_surge_after")
            
            # Check combat log for Action Surge message
            log_text = self._get_combat_log_text()
            if "Action Surge" in log_text:
                duration = (time.time() - start_time) * 1000
                return TestResult("Action Surge", True, "Action Surge activated successfully",
                               after_screenshot, None, duration_ms=duration)
            else:
                return TestResult("Action Surge", False, "No Action Surge message in combat log")
                
        except Exception as e:
            return TestResult("Action Surge", False, f"Error: {str(e)}", error_details=str(e))
    
    def test_critical_hit_mechanics(self) -> TestResult:
        """Test critical hit detection and double damage dice"""
        # This would require setting up a combat encounter and forcing a natural 20
        # For now, return a placeholder
        return TestResult("Critical Hits", False, "Test not yet implemented - requires combat setup")
    
    def _load_fighter_character(self) -> bool:
        """Load a Fighter character for testing"""
        try:
            # Navigate to load character or ensure Fighter is loaded
            if self.window and hasattr(self.window, 'game_engine'):
                # Try to load from slot 8 (which had the Fighter in the test output)
                character = self.window.game_engine.load_character_sync(8)
                if character and character.get('class_id') == 'fighter':
                    print(f"Loaded Fighter: {character['name']} (Level {character['level']})")
                    return True
            return False
        except Exception as e:
            print(f"Error loading Fighter: {e}")
            return False
    
    def _get_current_hp(self) -> int:
        """Get current HP from character display"""
        try:
            character_panel = self.find_widget_by_name("character_panel")
            if character_panel and hasattr(character_panel, 'character_data'):
                return character_panel.character_data.get('hit_points_current', 0)
            # Fallback - check game engine directly
            if self.window and hasattr(self.window, 'game_engine'):
                char = self.window.game_engine.current_character
                if char:
                    return char.get('hit_points_current', 0)
            return 0
        except:
            return 0
    
    def _get_combat_log_text(self) -> str:
        """Get text from combat log"""
        try:
            log_panel = self.find_widget_by_name("log_panel")
            if log_panel and hasattr(log_panel, 'combat_log'):
                return log_panel.combat_log.toPlainText()
            return ""
        except:
            return ""
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all Fighter ability tests"""
        results = []
        
        if not self.setup():
            results.append(TestResult("Setup", False, "Failed to initialize test environment"))
            return results
        
        try:
            # Test Second Wind
            print("Testing Second Wind...")
            results.append(self.test_second_wind_ability())
            QTest.qWait(2000)  # Wait between tests
            
            # Test Action Surge
            print("Testing Action Surge...")
            results.append(self.test_action_surge_ability())
            QTest.qWait(2000)
            
            # Test Critical Hits (placeholder)
            print("Testing Critical Hits...")
            results.append(self.test_critical_hit_mechanics())
            
        finally:
            self.teardown()
        
        return results

def main():
    """Run Fighter ability tests"""
    print("=" * 60)
    print("Fighter Abilities Test Suite")
    print("=" * 60)
    
    tester = FighterAbilitiesTest()
    results = tester.run_all_tests()
    
    # Print results
    print("\nTest Results:")
    print("-" * 40)
    passed = 0
    for result in results:
        status = "[PASS]" if result.passed else "[FAIL]"
        print(f"{status} {result.test_name}: {result.message}")
        if result.passed:
            passed += 1
        if result.error_details:
            print(f"    Error: {result.error_details}")
    
    print(f"\nSummary: {passed}/{len(results)} tests passed")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())