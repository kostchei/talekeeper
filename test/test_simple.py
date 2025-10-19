#!/usr/bin/env python3
# test
"""
Simple Character Creation Test
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_character_creation():
    print("Character Creation Test Started")
    print("=" * 50)
    
    # Test 1: Basic imports
    print("TEST 1: Import modules...")
    try:
        from ui.main_window import MainWindow
        print("PASS: MainWindow imported")
        
        from encounter_pane.encounter_panel import EncounterPanel
        print("PASS: EncounterPanel imported")
        
        from encounter_pane.town_encounter import TownEncounterPanel
        print("PASS: TownEncounterPanel imported")
        
        from services.subclass_manager import SubclassManager
        print("PASS: SubclassManager imported")
        
    except Exception as e:
        print(f"FAIL: Import error - {e}")
        return False
    
    # Test 2: Create encounter panel
    print("\nTEST 2: Create encounter panel...")
    try:
        dummy_character = {
            'id': 'test-char-001',
            'name': 'TestChar',
            'level': 1,
            'class_id': 'fighter',
            'race_name': 'Human',
            'experience_points': 0
        }
        
        panel = EncounterPanel(dummy_character)
        print("PASS: EncounterPanel created")
        
        panel.set_character_creation_mode()
        print("PASS: Character creation mode set")
        
    except Exception as e:
        print(f"FAIL: Encounter panel error - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test with minimal data
    print("\nTEST 3: Test with minimal character data...")
    try:
        minimal_character = {
            'id': '',
            'name': '',
            'level': 0,
            'class_id': '',
            'race_name': ''
        }
        
        town_panel = TownEncounterPanel(minimal_character)
        print("PASS: TownEncounterPanel created with minimal data")
        
        encounter_panel = EncounterPanel(minimal_character)
        print("PASS: EncounterPanel created with minimal data")
        
        encounter_panel.set_character_creation_mode()
        print("PASS: Character creation mode activated")
        
    except Exception as e:
        print(f"FAIL: Minimal data test error - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nAll tests passed!")
    return True

if __name__ == "__main__":
    # Change to project directory
    os.chdir(Path(__file__).parent.parent)
    
    success = test_character_creation()
    sys.exit(0 if success else 1)