# test
"""
Regression Test: Paladin Channel Divinity Action Panel Integration

Tests that Channel Divinity integrates properly with the action panel.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from action_cards.action_panel import ActionPanel, ActionType
from action_cards.channel_divinity_dialog import create_channel_divinity_options
from services.paladin_abilities import PaladinAbilitiesService


class ChannelDivinityActionIntegrationTest:
    """Test framework for Channel Divinity action panel integration."""

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

            print("Channel Divinity action integration test environment ready")
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

    def test_channel_divinity_action_type_exists(self):
        """Test that CHANNEL_DIVINITY action type is defined."""
        try:
            if hasattr(ActionType, 'CHANNEL_DIVINITY'):
                print("CHANNEL_DIVINITY action type found")
                return True
            else:
                print("CHANNEL_DIVINITY action type not found")
                return False
        except Exception as e:
            print(f"Error checking action type: {e}")
            return False

    def test_channel_divinity_import_in_action_panel(self):
        """Test that ChannelDivinityDialog is imported in action panel."""
        try:
            # Check if the import exists in the action panel module
            import action_cards.action_panel as ap_module
            if hasattr(ap_module, 'ChannelDivinityDialog'):
                print("ChannelDivinityDialog import found in action panel")
                return True
            else:
                print("ChannelDivinityDialog import not found in action panel")
                return False
        except Exception as e:
            print(f"Error checking import: {e}")
            return False

    def test_channel_divinity_methods_exist(self):
        """Test that Channel Divinity methods exist in action panel."""
        try:
            method_checks = [
                ('_use_channel_divinity', '_use_channel_divinity method'),
                ('_has_channel_divinity_uses', '_has_channel_divinity_uses method'),
                ('_apply_channel_divinity_effect', '_apply_channel_divinity_effect method'),
                ('_execute_channel_divinity_effect', '_execute_channel_divinity_effect method')
            ]

            all_found = True
            for method_name, description in method_checks:
                if hasattr(self.action_panel, method_name):
                    print(f"{description} found")
                else:
                    print(f"{description} not found")
                    all_found = False

            return all_found

        except Exception as e:
            print(f"Error checking methods: {e}")
            return False

    def test_paladin_character_context_with_channel_divinity(self):
        """Test setting up paladin character context for Channel Divinity."""
        try:
            # Create test paladin character context
            paladin_context = {
                'id': 'test_paladin_cd_integration',
                'name': 'Test Paladin CD',
                'class_id': 'paladin',
                'subclass_id': 'devotion',
                'level': 3,
                'hit_points_current': 30,
                'hit_points_max': 40,
                'charisma': 16
            }

            # Set character context
            self.action_panel.set_character_context(paladin_context)

            # Verify context was set
            if self.action_panel.character_context == paladin_context:
                print("Paladin character context with Channel Divinity set successfully")
                return True
            else:
                print("Failed to set paladin character context")
                return False

        except Exception as e:
            print(f"Error setting character context: {e}")
            return False

    def test_channel_divinity_options_generation(self):
        """Test Channel Divinity options generation."""
        try:
            # Test level 3 Devotion paladin
            options_level_3 = create_channel_divinity_options(3, "devotion")
            expected_options_3 = ["Divine Sense", "Sacred Weapon", "Turn the Unholy"]

            option_names_3 = [opt['name'] for opt in options_level_3]
            for expected in expected_options_3:
                if expected not in option_names_3:
                    print(f"Missing level 3 option: {expected}")
                    return False

            print(f"Level 3 options correct: {option_names_3}")

            # Test level 9 paladin (should have Abjure Foes)
            options_level_9 = create_channel_divinity_options(9, "devotion")
            if "Abjure Foes" not in [opt['name'] for opt in options_level_9]:
                print("Level 9 missing Abjure Foes")
                return False

            print("Level 9 options include Abjure Foes")
            return True

        except Exception as e:
            print(f"Error testing options generation: {e}")
            return False

    def test_channel_divinity_feature_check(self):
        """Test checking for Channel Divinity feature."""
        try:
            # Set up paladin character context
            paladin_context = {
                'id': 'test_paladin_cd_integration',
                'name': 'Test Paladin CD',
                'class_id': 'paladin',
                'subclass_id': 'devotion',
                'level': 3,
                'charisma': 16
            }

            self.action_panel.set_character_context(paladin_context)

            # Mock the feature check to return True
            self.action_panel.character_features = {'Channel Divinity': {'name': 'Channel Divinity'}}

            # Test the check
            if hasattr(self.action_panel, '_has_channel_divinity_uses'):
                has_uses = self.action_panel._has_channel_divinity_uses()
                print(f"Channel Divinity uses check result: {has_uses}")
                return True  # Method exists and runs
            else:
                print("Channel Divinity method not found")
                return False

        except Exception as e:
            print(f"Error in feature check: {e}")
            return False

    def test_channel_divinity_action_card_creation(self):
        """Test that Channel Divinity action card can be created."""
        try:
            # Set up paladin context
            paladin_context = {
                'id': 'test_paladin_cd_integration',
                'name': 'Test Paladin CD',
                'class_id': 'paladin',
                'subclass_id': 'devotion',
                'level': 3,
                'charisma': 16
            }

            self.action_panel.set_character_context(paladin_context)

            # Mock Channel Divinity feature
            self.action_panel.character_features = {
                'Channel Divinity': {
                    'name': 'Channel Divinity',
                    'description': 'Channel divine energy for various effects'
                }
            }

            # Try to create feature cards
            try:
                self.action_panel.load_character_features(self.action_panel.character_features)
                print("Channel Divinity feature loaded successfully")
                return True
            except Exception as fe:
                print(f"Feature loading error: {fe}")
                return False

        except Exception as e:
            print(f"Error in action card creation: {e}")
            return False

    def test_action_type_mapping_channel_divinity(self):
        """Test that Channel Divinity action type is properly mapped."""
        try:
            # Check if action panel has the proper action type mapping
            if hasattr(self.action_panel, 'action_cards'):
                print("Action cards dictionary exists")

                # Check if CHANNEL_DIVINITY is in the action type enum
                if hasattr(ActionType, 'CHANNEL_DIVINITY'):
                    action_type = ActionType.CHANNEL_DIVINITY
                    print(f"CHANNEL_DIVINITY action type: {action_type}")
                    return True
                else:
                    print("CHANNEL_DIVINITY action type not found")
                    return False
            else:
                print("Action cards dictionary not found")
                return False

        except Exception as e:
            print(f"Error in action type mapping: {e}")
            return False

    def test_different_oath_options(self):
        """Test Channel Divinity options for different oaths."""
        try:
            # Test Devotion oath
            devotion_options = create_channel_divinity_options(3, "devotion")
            devotion_names = [opt['name'] for opt in devotion_options]

            if "Sacred Weapon" not in devotion_names:
                print("Devotion missing Sacred Weapon")
                return False

            # Test Vengeance oath
            vengeance_options = create_channel_divinity_options(3, "vengeance")
            vengeance_names = [opt['name'] for opt in vengeance_options]

            if "Vow of Enmity" not in vengeance_names:
                print("Vengeance missing Vow of Enmity")
                return False

            # Test Ancients oath
            ancients_options = create_channel_divinity_options(3, "ancients")
            ancients_names = [opt['name'] for opt in ancients_options]

            if "Nature's Wrath" not in ancients_names:
                print("Ancients missing Nature's Wrath")
                return False

            print("Different oath options correct")
            return True

        except Exception as e:
            print(f"Error testing different oaths: {e}")
            return False

    def run_all_tests(self):
        """Run all Channel Divinity action integration tests."""
        print("=== CHANNEL DIVINITY ACTION INTEGRATION TEST SUITE ===\n")

        if not self.setup():
            print("Failed to set up test environment")
            return False

        # Run all tests
        self.run_test("CHANNEL_DIVINITY Action Type Exists", self.test_channel_divinity_action_type_exists)
        self.run_test("ChannelDivinityDialog Import", self.test_channel_divinity_import_in_action_panel)
        self.run_test("Channel Divinity Methods Exist", self.test_channel_divinity_methods_exist)
        self.run_test("Paladin Character Context Setup", self.test_paladin_character_context_with_channel_divinity)
        self.run_test("Channel Divinity Options Generation", self.test_channel_divinity_options_generation)
        self.run_test("Channel Divinity Feature Check", self.test_channel_divinity_feature_check)
        self.run_test("Action Card Creation", self.test_channel_divinity_action_card_creation)
        self.run_test("Action Type Mapping", self.test_action_type_mapping_channel_divinity)
        self.run_test("Different Oath Options", self.test_different_oath_options)

        # Print summary
        self.print_summary()

        return self.test_results["tests_failed"] == 0

    def print_summary(self):
        """Print test results summary."""
        print(f"\n=== CHANNEL DIVINITY ACTION INTEGRATION TEST RESULTS ===")
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
    """Run the Channel Divinity action integration test suite."""
    tester = ChannelDivinityActionIntegrationTest()
    success = tester.run_all_tests()

    if success:
        print("\nALL CHANNEL DIVINITY ACTION INTEGRATION TESTS PASSED!")
        return 0
    else:
        print("\nSOME CHANNEL DIVINITY ACTION INTEGRATION TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())