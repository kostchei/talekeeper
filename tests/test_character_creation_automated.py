#test
#!/usr/bin/env python3
"""
Automated Character Creation Test (No GUI)

Tests the character creation process automatically and reports results.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import traceback


def run_automated_tests():
    """Run all character creation tests automatically"""
    results = []
    
    def log_test(test_name: str, success: bool, message: str = "", error: Exception = None):
        """Log test result"""
        status = "✓ PASS" if success else "✗ FAIL"
        result = f"[{status}] {test_name}"
        
        if message:
            result += f": {message}"
        
        if error:
            result += f"\nError: {str(error)}"
            result += f"\nTraceback:\n{traceback.format_exc()}"
        
        results.append(result)
        print(result)
        print("-" * 60)
    
    # Test 1: Basic imports
    print("=== TEST 1: BASIC IMPORTS ===")
    try:
        from ui.main_window import MainWindow
        log_test("Import MainWindow", True, "Successfully imported")
        
        from encounter_pane.encounter_panel import EncounterPanel
        log_test("Import EncounterPanel", True, "Successfully imported")
        
        from encounter_pane.town_encounter import TownEncounterPanel
        log_test("Import TownEncounterPanel", True, "Successfully imported")
        
        from services.subclass_manager import SubclassManager
        log_test("Import SubclassManager", True, "Successfully imported")
        
    except Exception as e:
        log_test("Basic Imports", False, error=e)
        return results
    
    # Test 2: Create encounter panel with dummy data
    print("\n=== TEST 2: ENCOUNTER PANEL CREATION ===")
    try:
        from encounter_pane.encounter_panel import EncounterPanel
        
        # Create dummy character data
        dummy_character = {
            'id': 'test-char-001',
            'name': 'TestChar',
            'level': 1,
            'class_id': 'fighter',
            'race_name': 'Human',
            'experience_points': 0
        }
        
        # Try to create encounter panel (without showing UI)
        panel = EncounterPanel(dummy_character)
        log_test("Create EncounterPanel", True, f"Created with character: {dummy_character['name']}")
        
        # Test setting character creation mode
        panel.set_character_creation_mode()
        log_test("Set Character Creation Mode", True, "Mode set successfully")
        
    except Exception as e:
        log_test("Encounter Panel Creation", False, error=e)
    
    # Test 3: Character creation mode with minimal data
    print("\n=== TEST 3: CHARACTER CREATION MODE ===")
    try:
        from encounter_pane.encounter_panel import EncounterPanel
        from encounter_pane.town_encounter import TownEncounterPanel
        
        # Test with minimal character data (like during creation)
        minimal_character = {
            'id': '',
            'name': '',
            'level': 0,
            'class_id': '',
            'race_name': ''
        }
        
        # Try creating town encounter panel with minimal data
        town_panel = TownEncounterPanel(minimal_character)
        log_test("Create TownEncounterPanel with minimal data", True, "Panel created")
        
        # Try encounter panel
        encounter_panel = EncounterPanel(minimal_character)
        log_test("Create EncounterPanel with minimal data", True, "Panel created")
        
        # Try setting character creation mode
        encounter_panel.set_character_creation_mode()
        log_test("Character Creation Mode Activation", True, "Mode activated successfully")
        
    except Exception as e:
        log_test("Character Creation Mode Test", False, error=e)
    
    # Test 4: Main window creation (without showing)
    print("\n=== TEST 4: MAIN WINDOW CREATION ===")
    try:
        # Import QApplication first
        from PyQt6.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from ui.main_window import MainWindow
        
        # Create main window (but don't show)
        main_window = MainWindow()
        log_test("Create MainWindow", True, "Main window created")
        
        # Test character creation trigger
        main_window._start_character_creation()
        log_test("Start Character Creation", True, "Character creation started")
        
        # Clean up
        main_window.close()
        
    except Exception as e:
        log_test("Main Window Creation", False, error=e)
    
    return results


if __name__ == "__main__":
    # Change to project directory for proper imports and database access
    os.chdir(Path(__file__).parent.parent)
    
    print("Character Creation Workflow Test - Automated")
    print("=" * 60)
    
    results = run_automated_tests()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for r in results if "✓ PASS" in r)
    failed = sum(1 for r in results if "✗ FAIL" in r)
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFAILED TESTS:")
        for result in results:
            if "✗ FAIL" in result:
                print(result)
    
    sys.exit(0 if failed == 0 else 1)