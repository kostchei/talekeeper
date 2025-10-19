#test
"""
TaleKeeper UI Testing Framework - Master Controller
===================================================

TESTING FRAMEWORK - Exclude from ongoing work

Master script that coordinates all UI testing frameworks for TaleKeeper.
Provides a unified interface to run comprehensive UI tests for:

- Character creation (all classes with spell selection)
- Spell action card functionality
- Combat interactions and mechanics
- Action economy enforcement
- Concentration tracking

Usage Examples:
    # Test everything for spell action cards
    python testing_framework_master.py --focus spell_cards --character Nathlas

    # Test character creation for all spellcasters
    python testing_framework_master.py --focus character_creation --spellcasters-only

    # Run comprehensive test suite
    python testing_framework_master.py --full-suite

    # Quick spell action card validation
    python testing_framework_master.py --quick-spell-test

    # Create test data and run tests
    python testing_framework_master.py --setup-and-test
"""

import sys
import os
import argparse
import time
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication

# Import all testing framework components
from testing_framework_ui_automation import UIAutomationFramework, TestResult, TestRunner
from testing_framework_spell_actions import SpellActionCardValidator, TestDataCreator
from testing_framework_character_creation import CharacterCreationAutomator, CharacterClass, SpellSelectionValidator
from testing_framework_combat_interactions import CombatInteractionTester, CombatTestType


class MasterTestController:
    """TESTING FRAMEWORK - Master controller for all UI tests."""

    def __init__(self):
        self.app = None
        self.runner = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        """Initialize the testing environment."""
        try:
            self.app = QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)

            self.runner = TestRunner()
            return self.runner.setup()

        except Exception as e:
            print(f"Setup failed: {e}")
            return False

    def run_spell_action_card_tests(self, character_id: Optional[str] = None) -> List[TestResult]:
        """Run comprehensive spell action card tests."""
        print("RUNNING SPELL ACTION CARD TESTS")
        print("=" * 50)

        validator = SpellActionCardValidator(self.runner.framework)
        test_data_creator = TestDataCreator()

        # Create test character if none provided
        if not character_id:
            print("Creating test wizard character...")
            character_id = test_data_creator.create_test_wizard_with_spells("TestWizardSpells")
            if not character_id:
                print("Failed to create test character")
                return []

        print(f"Testing with character: {character_id}")

        # Run all spell card tests
        tests = [
            ("Spell Card Generation", validator.test_spell_card_generation),
            ("Spell Slot Consumption", validator.test_spell_slot_consumption),
            ("Cantrip Unlimited Casting", validator.test_cantrip_unlimited_casting)
        ]

        results = []
        for test_name, test_func in tests:
            print(f"  {test_name}...")
            result = test_func(character_id)
            results.append(result)
            status = "PASS" if result.success else "FAIL"
            print(f"     {status} - {result.message}")

        return results

    def run_character_creation_tests(self, spellcasters_only: bool = False) -> List[TestResult]:
        """Run character creation tests."""
        print("👤 Running Character Creation Tests")
        print("=" * 50)

        automator = CharacterCreationAutomator(self.runner.framework)
        validator = SpellSelectionValidator(self.runner.framework)

        # Determine which classes to test
        if spellcasters_only:
            test_classes = [CharacterClass.WIZARD, CharacterClass.CLERIC,
                           CharacterClass.WARLOCK, CharacterClass.PALADIN]
            print("Testing spellcasting classes only...")
        else:
            test_classes = list(CharacterClass)
            print("Testing all character classes...")

        results = []

        # Test spell UI validation for spellcasters
        spellcaster_classes = [CharacterClass.WIZARD, CharacterClass.CLERIC,
                              CharacterClass.WARLOCK, CharacterClass.PALADIN]

        for char_class in spellcaster_classes:
            if char_class in test_classes:
                print(f"  🔮 Validating spell UI for {char_class.value}...")
                result = validator.validate_spell_selection_ui(char_class)
                results.append(result)
                status = "PASS" if result.success else "FAIL"
                print(f"     {status} - {result.message}")

        # Test character creation
        for char_class in test_classes:
            char_name = f"Test{char_class.value.title()}"
            print(f"  👤 Creating {char_class.value} character...")
            result = automator.create_complete_character(char_class, char_name)
            results.append(result)
            status = "PASS" if result.success else "FAIL"
            print(f"     {status} - {result.message}")

        return results

    def run_combat_interaction_tests(self, character_id: Optional[str] = None) -> List[TestResult]:
        """Run combat interaction tests."""
        print("⚔️ Running Combat Interaction Tests")
        print("=" * 50)

        tester = CombatInteractionTester(self.runner.framework)

        # Get test character
        if not character_id:
            character_id = self._get_test_character_with_spells()
            if not character_id:
                print("❌ No suitable test character found")
                return []

        print(f"Testing with character: {character_id}")

        # Run combat tests
        tests = [
            ("Spell Casting in Combat", tester.test_spell_casting_in_combat),
            ("Action Economy Enforcement", tester.test_action_economy_enforcement),
            ("Concentration Mechanics", tester.test_concentration_mechanics),
            ("Weapon Attacks", tester.test_weapon_attacks),
            ("Class Features", tester.test_class_features)
        ]

        results = []
        for test_name, test_func in tests:
            print(f"  ⚔️ {test_name}...")
            result = test_func(character_id)
            results.append(result)
            status = "PASS" if result.success else "FAIL"
            print(f"     {status} - {result.message}")

        return results

    def run_full_test_suite(self) -> List[TestResult]:
        """Run the complete test suite."""
        print("🎯 Running Full TaleKeeper UI Test Suite")
        print("=" * 60)

        all_results = []

        # 1. Character Creation Tests
        creation_results = self.run_character_creation_tests(spellcasters_only=True)
        all_results.extend(creation_results)

        print("\n" + "=" * 60)

        # 2. Spell Action Card Tests
        spell_results = self.run_spell_action_card_tests()
        all_results.extend(spell_results)

        print("\n" + "=" * 60)

        # 3. Combat Interaction Tests
        combat_results = self.run_combat_interaction_tests()
        all_results.extend(combat_results)

        return all_results

    def quick_spell_test(self, character_id: Optional[str] = None) -> List[TestResult]:
        """Run a quick spell action card validation."""
        print("QUICK SPELL ACTION CARD TEST")
        print("=" * 40)

        if not character_id:
            # Look for existing character with spells
            character_id = self._get_test_character_with_spells()
            if not character_id:
                # Create a simple test wizard
                creator = TestDataCreator()
                character_id = creator.create_test_wizard_with_spells("QuickTestWizard")

        if character_id:
            validator = SpellActionCardValidator(self.runner.framework)
            result = validator.test_spell_card_generation(character_id)
            status = "PASS" if result.success else "FAIL"
            print(f"  {status} - {result.message}")
            return [result]
        else:
            print("Could not create or find test character")
            return []

    def setup_test_data_and_run(self) -> List[TestResult]:
        """Set up test data and run comprehensive tests."""
        print("🛠️ Setting Up Test Data and Running Tests")
        print("=" * 50)

        # Create test characters
        creator = TestDataCreator()

        print("Creating test characters...")
        test_chars = []

        # Create a wizard with spells
        wizard_id = creator.create_test_wizard_with_spells("TestWizardMaster")
        if wizard_id:
            test_chars.append(("Wizard", wizard_id))

        print(f"Created {len(test_chars)} test characters")

        # Run tests with created characters
        all_results = []

        for char_type, char_id in test_chars:
            print(f"\nTesting {char_type} character: {char_id}")

            # Test spell cards
            spell_results = self.run_spell_action_card_tests(char_id)
            all_results.extend(spell_results)

            # Test combat interactions
            combat_results = self.run_combat_interaction_tests(char_id)
            all_results.extend(combat_results)

        return all_results

    def _get_test_character_with_spells(self) -> Optional[str]:
        """Get a character ID that has spells for testing."""
        try:
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT c.id, c.name, c.class_id
                FROM characters c
                JOIN character_spells cs ON c.id = cs.character_id
                WHERE c.class_id IN ('wizard', 'cleric', 'warlock', 'paladin')
                ORDER BY c.name
                LIMIT 1
            """)

            result = cursor.fetchone()
            conn.close()

            if result:
                print(f"Found test character: {result[1]} ({result[2]}) - {result[0]}")
                return result[0]

        except Exception as e:
            print(f"Error finding test character: {e}")

        return None

    def generate_comprehensive_report(self, results: List[TestResult]):
        """Generate a comprehensive test report."""
        self.runner.results.extend(results)
        self.runner.generate_report()

        # Print summary
        passed = sum(1 for r in results if r.success)
        total = len(results)

        print("\n" + "=" * 60)
        print("🎯 TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests run")

        if total > 0:
            print(f"\nReport generated: {self.runner.framework.screenshot_dir}")

    def cleanup(self):
        """Clean up testing environment."""
        if self.runner:
            self.runner.cleanup()


def main():
    """Main entry point for the testing framework."""
    parser = argparse.ArgumentParser(
        description='TaleKeeper UI Testing Framework Master Controller',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test spell action cards for specific character
  python testing_framework_master.py --focus spell_cards --character a32ee99b-a49f-4cf5-adc7-86edc1711922

  # Test character creation for spellcasters
  python testing_framework_master.py --focus character_creation --spellcasters-only

  # Quick spell validation
  python testing_framework_master.py --quick-spell-test

  # Full test suite
  python testing_framework_master.py --full-suite

  # Set up test data and run comprehensive tests
  python testing_framework_master.py --setup-and-test
        """
    )

    parser.add_argument('--focus', choices=['spell_cards', 'character_creation', 'combat'],
                       help='Focus on specific test area')
    parser.add_argument('--character', help='Character ID for testing')
    parser.add_argument('--spellcasters-only', action='store_true',
                       help='Test only spellcasting classes')
    parser.add_argument('--full-suite', action='store_true',
                       help='Run complete test suite')
    parser.add_argument('--quick-spell-test', action='store_true',
                       help='Run quick spell action card test')
    parser.add_argument('--setup-and-test', action='store_true',
                       help='Create test data and run tests')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up test characters')

    args = parser.parse_args()

    if args.cleanup:
        creator = TestDataCreator()
        creator.cleanup_test_characters()
        print("✅ Test character cleanup completed")
        return 0

    controller = MasterTestController()

    try:
        if not controller.setup():
            print("❌ Failed to setup testing environment")
            return 1

        results = []

        if args.quick_spell_test:
            results = controller.quick_spell_test(args.character)

        elif args.setup_and_test:
            results = controller.setup_test_data_and_run()

        elif args.full_suite:
            results = controller.run_full_test_suite()

        elif args.focus == 'spell_cards':
            results = controller.run_spell_action_card_tests(args.character)

        elif args.focus == 'character_creation':
            results = controller.run_character_creation_tests(args.spellcasters_only)

        elif args.focus == 'combat':
            results = controller.run_combat_interaction_tests(args.character)

        else:
            # Default: run spell card tests
            print("No specific test specified, running spell action card tests...")
            results = controller.run_spell_action_card_tests(args.character)

        # Generate report
        controller.generate_comprehensive_report(results)

        # Return appropriate exit code
        passed = sum(1 for r in results if r.success)
        return 0 if passed == len(results) else 1

    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"Testing failed with exception: {e}")
        return 1
    finally:
        controller.cleanup()


if __name__ == "__main__":
    sys.exit(main())