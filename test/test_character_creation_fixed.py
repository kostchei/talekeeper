#!/usr/bin/env python3
# test
"""
Test Character Creation Fix
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_character_creation_fix():
    print("Character Creation Fix Test")
    print("=" * 50)
    
    # Test 1: Import QApplication first
    print("TEST 1: Create QApplication...")
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("PASS: QApplication created")
    except Exception as e:
        print(f"FAIL: QApplication error - {e}")
        return False
    
    # Test 2: Create EncounterPanel correctly
    print("\nTEST 2: Create EncounterPanel...")
    try:
        from encounter_pane.encounter_panel import EncounterPanel
        
        # Create with no parameters (parent defaults to None)
        panel = EncounterPanel()
        print("PASS: EncounterPanel created")
        
        # Test character creation mode
        panel.set_character_creation_mode()
        print("PASS: Character creation mode set")
        
        # Test that the tab index is stored
        if hasattr(panel, 'character_creation_tab_index'):
            print(f"PASS: character_creation_tab_index = {panel.character_creation_tab_index}")
        else:
            print("FAIL: character_creation_tab_index not found")
            return False
        
        # Test exit character creation
        panel.exit_character_creation()
        print("PASS: Character creation exit successful")
        
    except Exception as e:
        print(f"FAIL: EncounterPanel error - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test main window character creation trigger
    print("\nTEST 3: Test MainWindow character creation...")
    try:
        from ui.main_window import MainWindow
        
        main_window = MainWindow()
        print("PASS: MainWindow created")
        
        # Test the character creation trigger
        main_window._start_character_creation()
        print("PASS: Character creation started via MainWindow")
        
        # Clean up
        main_window.close()
        print("PASS: MainWindow cleaned up")
        
    except Exception as e:
        print(f"FAIL: MainWindow character creation error - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nAll character creation tests passed!")
    print("✓ Character creation functionality is fixed")
    return True

if __name__ == "__main__":
    # Change to project directory
    os.chdir(Path(__file__).parent.parent)
    
    success = test_character_creation_fix()
    sys.exit(0 if success else 1)