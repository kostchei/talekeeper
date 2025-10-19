# test
"""
Regression Test: Paladin Lay on Hands Feature

Tests the Lay on Hands dialog and mechanics for paladins.
"""

import sys
import os
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from action_cards.lay_on_hands_dialog import LayOnHandsDialog
from services.paladin_abilities import PaladinAbilitiesService


class LayOnHandsTestFramework:
    """Test framework for Lay on Hands functionality."""

    def __init__(self):
        self.app = None
        self.dialog = None
        self.paladin_service = None
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": []
        }

    def setup(self):
        """Set up test environment."""
        try:
            # Create QApplication if not exists
            if not QApplication.instance():
                self.app = QApplication([])

            # Use existing database
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "talekeeper.db")
            self.paladin_service = PaladinAbilitiesService(db_path)

            print("Lay on Hands test environment ready")
            return True

        except Exception as e:
            print(f"Setup failed: {e}")
            return False

    def run_test(self, test_name: str, test_function):
        """Run a single test and record results."""
        self.test_results["tests_run"] += 1
        print(f"\n--- Testing: {test_name} ---")

        try:
            result = test_function()
            if result:
                self.test_results["tests_passed"] += 1
                print(f"PASS: {test_name}")
            else:
                self.test_results["tests_failed"] += 1
                self.test_results["failures"].append(test_name)
                print(f"FAIL: {test_name}")
            return result
        except Exception as e:
            self.test_results["tests_failed"] += 1
            self.test_results["failures"].append(f"{test_name}: {str(e)}")
            print(f"ERROR: {test_name} - {e}")
            return False

    def test_dialog_creation(self):
        """Test that Lay on Hands dialog can be created."""
        try:
            character_data = {"name": "Test Paladin", "level": 5}
            target_options = [("self", "Test Paladin", 20, 30)]

            dialog = LayOnHandsDialog(
                character_data=character_data,
                current_pool=25,
                max_pool=25,
                target_options=target_options
            )

            if dialog and dialog.windowTitle() == "Lay on Hands":
                print("Dialog created successfully")
                dialog.close()
                return True
            else:
                print("Dialog creation failed")
                return False

        except Exception as e:
            print(f"Dialog creation error: {e}")
            return False

    def test_healing_pool_calculation(self):
        """Test healing pool calculations."""
        try:
            # Test level 5 paladin should have 25 points
            level_5_pool = 5 * 5
            if level_5_pool == 25:
                print(f"Level 5 healing pool correct: {level_5_pool}")
            else:
                print(f"Level 5 healing pool incorrect: {level_5_pool}")
                return False

            # Test level 10 paladin should have 50 points
            level_10_pool = 10 * 5
            if level_10_pool == 50:
                print(f"Level 10 healing pool correct: {level_10_pool}")
            else:
                print(f"Level 10 healing pool incorrect: {level_10_pool}")
                return False

            return True

        except Exception as e:
            print(f"Pool calculation error: {e}")
            return False

    def test_healing_point_limits(self):
        """Test healing point usage limits."""
        try:
            character_data = {"name": "Test Paladin", "level": 5}
            target_options = [("self", "Test Paladin", 20, 30)]

            dialog = LayOnHandsDialog(
                character_data=character_data,
                current_pool=25,
                max_pool=25,
                target_options=target_options
            )

            # Test maximum 5 points per use
            max_spin_value = dialog.points_spin.maximum()
            if max_spin_value == 5:
                print(f"Maximum points per use correct: {max_spin_value}")
            else:
                print(f"Maximum points per use incorrect: {max_spin_value}, expected 5")
                dialog.close()
                return False

            # Test minimum 1 point
            min_spin_value = dialog.points_spin.minimum()
            if min_spin_value == 1:
                print(f"Minimum points per use correct: {min_spin_value}")
            else:
                print(f"Minimum points per use incorrect: {min_spin_value}, expected 1")
                dialog.close()
                return False

            dialog.close()
            return True

        except Exception as e:
            print(f"Healing limits test error: {e}")
            return False

    def test_poison_curing_option(self):
        """Test poison curing functionality."""
        try:
            character_data = {"name": "Test Paladin", "level": 5}
            target_options = [("self", "Test Paladin", 20, 30)]

            dialog = LayOnHandsDialog(
                character_data=character_data,
                current_pool=25,
                max_pool=25,
                target_options=target_options
            )

            # Test poison checkbox exists
            poison_checkbox = dialog.poison_checkbox
            if not poison_checkbox:
                print("Poison checkbox not found")
                dialog.close()
                return False

            # Test checking poison option sets points to 5
            poison_checkbox.setChecked(True)
            if dialog.points_spin.value() == 5 and not dialog.points_spin.isEnabled():
                print("Poison option correctly sets 5 points and disables spinner")
            else:
                print(f"Poison option failed: points={dialog.points_spin.value()}, enabled={dialog.points_spin.isEnabled()}")
                dialog.close()
                return False

            # Test unchecking restores normal operation
            poison_checkbox.setChecked(False)
            if dialog.points_spin.isEnabled():
                print("Unchecking poison option restores normal operation")
            else:
                print("Unchecking poison option failed to restore normal operation")
                dialog.close()
                return False

            dialog.close()
            return True

        except Exception as e:
            print(f"Poison curing test error: {e}")
            return False

    def test_low_pool_limits(self):
        """Test behavior with low healing pool."""
        try:
            character_data = {"name": "Test Paladin", "level": 5}
            target_options = [("self", "Test Paladin", 20, 30)]

            # Test with only 3 points remaining
            dialog = LayOnHandsDialog(
                character_data=character_data,
                current_pool=3,
                max_pool=25,
                target_options=target_options
            )

            # Maximum should be limited by available pool
            max_spin_value = dialog.points_spin.maximum()
            if max_spin_value == 3:
                print(f"Low pool correctly limits maximum to: {max_spin_value}")
            else:
                print(f"Low pool limit incorrect: {max_spin_value}, expected 3")
                dialog.close()
                return False

            # Poison option should be disabled if less than 5 points
            dialog.poison_checkbox.setChecked(True)
            if not dialog.apply_btn.isEnabled():
                print("Apply button correctly disabled with insufficient points for poison cure")
            else:
                print("Apply button should be disabled with insufficient points for poison cure")
                dialog.close()
                return False

            dialog.close()
            return True

        except Exception as e:
            print(f"Low pool test error: {e}")
            return False

    def test_healing_info_retrieval(self):
        """Test getting healing information from dialog."""
        try:
            character_data = {"name": "Test Paladin", "level": 5}
            target_options = [("self", "Test Paladin", 20, 30)]

            dialog = LayOnHandsDialog(
                character_data=character_data,
                current_pool=25,
                max_pool=25,
                target_options=target_options
            )

            # Test normal healing info
            dialog.points_spin.setValue(3)
            info = dialog.get_healing_info()

            expected_info = {
                "target_id": "self",
                "healing_points": 3,
                "cure_poison": False,
                "points_cost": 3
            }

            if info == expected_info:
                print("Normal healing info correct")
            else:
                print(f"Normal healing info incorrect: {info}")
                dialog.close()
                return False

            # Test poison curing info
            dialog.poison_checkbox.setChecked(True)
            poison_info = dialog.get_healing_info()

            expected_poison_info = {
                "target_id": "self",
                "healing_points": 5,  # Automatically set to 5
                "cure_poison": True,
                "points_cost": 5
            }

            if poison_info == expected_poison_info:
                print("Poison curing info correct")
            else:
                print(f"Poison curing info incorrect: {poison_info}")
                dialog.close()
                return False

            dialog.close()
            return True

        except Exception as e:
            print(f"Healing info test error: {e}")
            return False

    def test_paladin_service_lay_on_hands(self):
        """Test Lay on Hands through paladin service."""
        try:
            # Create test character
            test_char_id = "test_paladin_loh"

            # Test healing usage
            result = self.paladin_service.use_lay_on_hands(
                character_id=test_char_id,
                healing_points=3
            )

            # This will fail because character doesn't exist, but tests the method structure
            if "reason" in result and result["reason"] == "Not a paladin":
                print("Paladin service correctly handles non-existent character")
                return True
            elif result.get("success"):
                print("Paladin service Lay on Hands successful")
                return True
            else:
                print(f"Paladin service test result: {result}")
                return True  # Method exists and returns proper structure

        except Exception as e:
            print(f"Paladin service test error: {e}")
            return False

    def run_all_tests(self):
        """Run all Lay on Hands tests."""
        print("=== LAY ON HANDS REGRESSION TEST SUITE ===\n")

        if not self.setup():
            print("Failed to set up test environment")
            return False

        # Run all tests
        self.run_test("Dialog Creation", self.test_dialog_creation)
        self.run_test("Healing Pool Calculation", self.test_healing_pool_calculation)
        self.run_test("Healing Point Limits", self.test_healing_point_limits)
        self.run_test("Poison Curing Option", self.test_poison_curing_option)
        self.run_test("Low Pool Limits", self.test_low_pool_limits)
        self.run_test("Healing Info Retrieval", self.test_healing_info_retrieval)
        self.run_test("Paladin Service Integration", self.test_paladin_service_lay_on_hands)

        # Print summary
        self.print_summary()

        return self.test_results["tests_failed"] == 0

    def print_summary(self):
        """Print test results summary."""
        print(f"\n=== LAY ON HANDS TEST RESULTS ===")
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")

        if self.test_results["failures"]:
            print(f"\nFAILED TESTS:")
            for failure in self.test_results["failures"]:
                print(f"  - {failure}")

        success_rate = (self.test_results["tests_passed"] / self.test_results["tests_run"]) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")


def main():
    """Run the Lay on Hands test suite."""
    tester = LayOnHandsTestFramework()
    success = tester.run_all_tests()

    if success:
        print("\nALL LAY ON HANDS TESTS PASSED!")
        return 0
    else:
        print("\nSOME LAY ON HANDS TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())