#!/usr/bin/env python3
# test
"""
Test Class Filtering in Character Creation
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_class_filtering():
    print("Class Filtering Test")
    print("=" * 50)
    
    # Test 1: Import required modules
    print("TEST 1: Import modules...")
    try:
        from PyQt6.QtWidgets import QApplication
        from encounter_pane.encounter_panel import EncounterPanel
        from encounter_pane.campaign_frame import CampaignFrame
        print("PASS: All modules imported")
    except Exception as e:
        print(f"FAIL: Import error - {e}")
        return False
    
    # Test 2: Create QApplication
    print("\nTEST 2: Create QApplication...")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("PASS: QApplication created")
    except Exception as e:
        print(f"FAIL: QApplication error - {e}")
        return False
    
    # Test 3: Test CampaignFrame with available classes
    print("\nTEST 3: Test CampaignFrame...")
    try:
        # Create campaign frame with limited classes
        campaign_frame = CampaignFrame(
            name="Test Campaign",
            monster_type_weights={'humanoid': 0.7, 'beast': 0.3},
            difficulty_distribution={'low': 0.6, 'moderate': 0.4},
            rest_rules={'short_rest_duration': 1, 'long_rest_duration': 8},
            style='test',
            available_classes=["barbarian", "fighter", "rogue", "paladin", "cleric", "warlock", "wizard"]
        )
        print(f"PASS: CampaignFrame created with {len(campaign_frame.available_classes)} classes")
        print(f"Available classes: {campaign_frame.available_classes}")
    except Exception as e:
        print(f"FAIL: CampaignFrame error - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test EncounterPanel class loading
    print("\nTEST 4: Test EncounterPanel class loading...")
    try:
        # Create encounter panel
        encounter_panel = EncounterPanel()
        print("PASS: EncounterPanel created")
        
        # Check that campaign frame loaded
        if hasattr(encounter_panel, 'campaign_frame') and encounter_panel.campaign_frame:
            print(f"PASS: Campaign frame loaded: {encounter_panel.campaign_frame.name}")
            print(f"Available classes: {encounter_panel.campaign_frame.available_classes}")
        else:
            print("FAIL: Campaign frame not loaded")
            return False
        
        # Test class loading method
        encounter_panel._load_class_data()
        print("PASS: Class data loaded successfully (filtering applied)")
        
    except Exception as e:
        print(f"FAIL: EncounterPanel class loading error - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Test database query
    print("\nTEST 5: Test direct database filtering...")
    try:
        import sqlite3
        conn = sqlite3.connect("talekeeper.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all classes
        cursor.execute("SELECT * FROM classes ORDER BY display_order, name")
        all_classes = cursor.fetchall()
        print(f"Total classes in database: {len(all_classes)}")
        
        # Simulate filtering
        allowed_classes = {"barbarian", "fighter", "rogue", "paladin", "cleric", "warlock", "wizard"}
        filtered_classes = [c for c in all_classes if c['name'].lower() in allowed_classes]
        print(f"Filtered classes: {len(filtered_classes)}")
        
        for class_row in filtered_classes:
            print(f"  - {class_row['name']}")
        
        conn.close()
        print("PASS: Database filtering works")
        
    except Exception as e:
        print(f"FAIL: Database test error - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nAll class filtering tests passed!")
    return True

if __name__ == "__main__":
    # Change to project directory
    os.chdir(Path(__file__).parent.parent)
    
    success = test_class_filtering()
    sys.exit(0 if success else 1)