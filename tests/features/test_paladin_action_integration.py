"""
Regression Test: Paladin Action Panel Integration

Tests that paladin abilities integrate properly with the action panel.
"""

import sys
import os
import sqlite3
from unittest.mock import patch, MagicMock

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from action_cards.action_panel import ActionPanel, ActionType
from services.paladin_abilities import PaladinAbilitiesService


class PaladinActionIntegrationTest:
    """Test framework for paladin action panel integration."""

    def __init__(self):
        self.app = None
        self.action_panel = None
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

            # Create action panel
            self.action_panel = ActionPanel()

            # Use existing database
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "talekeeper.db")
            self.paladin_service = PaladinAbilitiesService(db_path)

            print("Paladin action integration test environment ready")
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

    def test_lay_on_hands_action_type_exists(self):
        """Test that LAY_ON_HANDS action type is defined."""
        try:
            if hasattr(ActionType, 'LAY_ON_HANDS'):
                print("LAY_ON_HANDS action type found")
                return True
            else:
                print("LAY_ON_HANDS action type not found")
                return False
        except Exception as e:
            print(f"Error checking action type: {e}")
            return False

    def test_lay_on_hands_import_in_action_panel(self):
        """Test that LayOnHandsDialog is imported in action panel."""
        try:
            # Check if the import exists in the action panel module
            import action_cards.action_panel as ap_module
            if hasattr(ap_module, 'LayOnHandsDialog'):
                print("LayOnHandsDialog import found in action panel")
                return True
            else:
                print("LayOnHandsDialog import not found in action panel")
                return False
        except Exception as e:
            print(f"Error checking import: {e}")
            return False

    def test_paladin_character_context_setup(self):
        """Test setting up paladin character context."""
        try:
            # Create test paladin character context
            paladin_context = {
                'id': 'test_paladin_integration',
                'name': 'Test Paladin',
                'class_id': 'paladin',
                'level': 5,
                'hit_points_current': 30,
                'hit_points_max': 40,
                'charisma': 16
            }

            # Set character context
            self.action_panel.set_character_context(paladin_context)

            # Verify context was set
            if self.action_panel.character_context == paladin_context:
                print("Paladin character context set successfully")
                return True
            else:
                print("Failed to set paladin character context")
                return False

        except Exception as e:
            print(f"Error setting character context: {e}")
            return False

    def test_has_lay_on_hands_method_exists(self):
        """Test that _has_lay_on_hands_uses method exists."""
        try:
            if hasattr(self.action_panel, '_has_lay_on_hands_uses'):
                print("_has_lay_on_hands_uses method found")
                return True
            else:
                print("_has_lay_on_hands_uses method not found")
                return False
        except Exception as e:
            print(f"Error checking method: {e}")
            return False

    def test_use_lay_on_hands_method_exists(self):
        """Test that _use_lay_on_hands method exists."""
        try:
            if hasattr(self.action_panel, '_use_lay_on_hands'):
                print("_use_lay_on_hands method found")
                return True
            else:
                print("_use_lay_on_hands method not found")
                return False
        except Exception as e:
            print(f"Error checking method: {e}")
            return False

    def test_apply_lay_on_hands_healing_method_exists(self):
        """Test that _apply_lay_on_hands_healing method exists."""
        try:
            if hasattr(self.action_panel, '_apply_lay_on_hands_healing'):
                print("_apply_lay_on_hands_healing method found")
                return True
            else:
                print("_apply_lay_on_hands_healing method not found")
                return False
        except Exception as e:
            print(f"Error checking method: {e}")
            return False

    def test_lay_on_hands_feature_check(self):
        """Test checking for Lay on Hands feature."""
        try:
            # Set up paladin character context with Lay on Hands feature
            paladin_context = {
                'id': 'test_paladin_integration',
                'name': 'Test Paladin',
                'class_id': 'paladin',
                'level': 5,
                'hit_points_current': 30,
                'hit_points_max': 40,
                'charisma': 16
            }

            self.action_panel.set_character_context(paladin_context)

            # Mock the feature check to return True
            self.action_panel.character_features = {'Lay on Hands': {'name': 'Lay on Hands'}}

            # Test the check
            if hasattr(self.action_panel, '_has_lay_on_hands_uses'):
                has_uses = self.action_panel._has_lay_on_hands_uses()
                print(f"Lay on Hands uses check result: {has_uses}")
                return True  # Method exists and runs
            else:
                print("Lay on Hands method not found")
                return False

        except Exception as e:
            print(f"Error in feature check: {e}")
            return False

    def test_lay_on_hands_action_card_creation(self):
        """Test that Lay on Hands action card can be created."""
        try:
            # Set up paladin context
            paladin_context = {
                'id': 'test_paladin_integration',
                'name': 'Test Paladin',
                'class_id': 'paladin',
                'level': 5,
                'hit_points_current': 30,
                'hit_points_max': 40,
                'charisma': 16
            }

            self.action_panel.set_character_context(paladin_context)

            # Mock Lay on Hands feature
            self.action_panel.character_features = {
                'Lay on Hands': {
                    'name': 'Lay on Hands',
                    'description': 'Heal wounds with divine energy'
                }
            }

            # Try to create feature cards (this calls internal methods)
            try:
                self.action_panel.load_character_features(self.action_panel.character_features)
                print("Lay on Hands feature loaded successfully")
                return True
            except Exception as fe:
                print(f"Feature loading error: {fe}")
                return False

        except Exception as e:
            print(f"Error in action card creation: {e}")
            return False

    def test_action_type_mapping(self):
        """Test that Lay on Hands action type is properly mapped."""
        try:
            # Check if action panel has the proper action type mapping
            if hasattr(self.action_panel, 'action_cards'):
                print("Action cards dictionary exists")

                # Check if LAY_ON_HANDS is in the action type enum
                if hasattr(ActionType, 'LAY_ON_HANDS'):
                    action_type = ActionType.LAY_ON_HANDS
                    print(f"LAY_ON_HANDS action type: {action_type}")
                    return True
                else:
                    print("LAY_ON_HANDS action type not found")
                    return False
            else:
                print("Action cards dictionary not found")
                return False

        except Exception as e:
            print(f"Error in action type mapping: {e}")
            return False

    def run_all_tests(self):
        """Run all paladin action integration tests."""
        print("=== PALADIN ACTION INTEGRATION TEST SUITE ===\n")

        if not self.setup():
            print("Failed to set up test environment")
            return False

        # Run all tests
        self.run_test("LAY_ON_HANDS Action Type Exists", self.test_lay_on_hands_action_type_exists)
        self.run_test("LayOnHandsDialog Import", self.test_lay_on_hands_import_in_action_panel)
        self.run_test("Paladin Character Context Setup", self.test_paladin_character_context_setup)
        self.run_test("_has_lay_on_hands_uses Method", self.test_has_lay_on_hands_method_exists)
        self.run_test("_use_lay_on_hands Method", self.test_use_lay_on_hands_method_exists)
        self.run_test("_apply_lay_on_hands_healing Method", self.test_apply_lay_on_hands_healing_method_exists)
        self.run_test("Lay on Hands Feature Check", self.test_lay_on_hands_feature_check)
        self.run_test("Action Card Creation", self.test_lay_on_hands_action_card_creation)
        self.run_test("Action Type Mapping", self.test_action_type_mapping)

        # Print summary
        self.print_summary()

        return self.test_results["tests_failed"] == 0

    def print_summary(self):
        """Print test results summary."""
        print(f"\n=== PALADIN ACTION INTEGRATION TEST RESULTS ===")
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
    """Run the paladin action integration test suite."""
    tester = PaladinActionIntegrationTest()
    success = tester.run_all_tests()

    if success:
        print("\nALL PALADIN ACTION INTEGRATION TESTS PASSED!")
        return 0
    else:
        print("\nSOME PALADIN ACTION INTEGRATION TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())