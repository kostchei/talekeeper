"""
TaleKeeper Test Runner Script

Main script to run all TaleKeeper tests with options for:
- Full test suite
- Specific feature tests
- Interactive testing mode
- Visual debugging mode
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from test_framework import TestRunner
from test_specific_features import run_specific_tests


def run_interactive_test():
    """Run tests in interactive mode with visual feedback"""
    print("\n" + "="*60)
    print("TaleKeeper Interactive Testing Mode")
    print("="*60 + "\n")
    print("This mode will run tests with visual feedback and pauses.")
    print("You can observe the UI during testing.\n")
    
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    # Import and run specific interactive tests
    from test_framework import (
        CharacterSheetTester,
        EquipmentTester,
        ActionCardTester,
        EncounterTester
    )
    
    test_classes = [
        ("Character Sheet", CharacterSheetTester),
        ("Equipment Panel", EquipmentTester),
        ("Action Cards", ActionCardTester),
        ("Encounter Panel", EncounterTester)
    ]
    
    for name, test_class in test_classes:
        response = input(f"\nTest {name}? (y/n): ")
        if response.lower() != 'y':
            continue
        
        print(f"\nTesting {name}...")
        tester = test_class()
        
        if not tester.setup():
            print(f"Failed to setup {name}")
            continue
        
        # Run test methods with pauses
        test_methods = [m for m in dir(tester) if m.startswith('test_')]
        
        for method_name in test_methods:
            print(f"\n  Running: {method_name}")
            input("  Press Enter to continue...")
            
            try:
                method = getattr(tester, method_name)
                result = method()
                print(f"  Result: {'✓ PASS' if result else '✗ FAIL'}")
            except Exception as e:
                print(f"  Error: {e}")
        
        tester.teardown()
        input("\nPress Enter for next test suite...")


def run_visual_debug():
    """Run tests with enhanced visual debugging"""
    print("\n" + "="*60)
    print("TaleKeeper Visual Debug Mode")
    print("="*60 + "\n")
    print("This mode highlights UI elements during testing.\n")
    
    from test_framework import CharacterSheetTester
    
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    tester = CharacterSheetTester()
    if not tester.setup():
        print("Failed to setup test environment")
        return
    
    print("Visual debugging active. Watch the application window.")
    
    # Example: Highlight different panels
    panels_to_highlight = [
        ('character_sheet', 'blue'),
        ('equipment_panel', 'green'),
        ('action_panel', 'yellow'),
        ('encounter_pane', 'red')
    ]
    
    for panel_name, color in panels_to_highlight:
        if hasattr(tester.window, panel_name):
            panel = getattr(tester.window, panel_name)
            print(f"Highlighting {panel_name} in {color}...")
            tester.highlight_widget(panel, color, 2000)
    
    # Take annotated screenshot
    screenshot_path = tester.take_screenshot("visual_debug_complete")
    print(f"Screenshot saved: {screenshot_path}")
    
    tester.teardown()


def main():
    parser = argparse.ArgumentParser(description='Run TaleKeeper tests')
    parser.add_argument('--mode', choices=['full', 'specific', 'interactive', 'visual'],
                       default='full', help='Test mode to run')
    parser.add_argument('--suite', help='Specific test suite to run')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--screenshots', action='store_true', 
                       help='Take screenshots for all tests')
    
    args = parser.parse_args()
    
    print(f"TaleKeeper Testing System - Mode: {args.mode.upper()} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.mode == 'full':
        print("Running full test suite...")
        runner = TestRunner()
        summary = runner.run_all_tests()
        
        # Display results
        if summary['failed'] == 0:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print(f"\n❌ {summary['failed']} tests failed")
            sys.exit(1)
    
    elif args.mode == 'specific':
        print("Running specific feature tests...")
        success = run_specific_tests()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'interactive':
        run_interactive_test()
    
    elif args.mode == 'visual':
        run_visual_debug()


if __name__ == "__main__":
    main()