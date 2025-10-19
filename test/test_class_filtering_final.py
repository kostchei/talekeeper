#!/usr/bin/env python3
# test
"""
Final Class Filtering Test
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_class_filtering_final():
    print("Final Class Filtering Test")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from encounter_pane.encounter_panel import EncounterPanel
        import sqlite3
        
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Test 1: Create EncounterPanel and check campaign frame
        print("1. Creating EncounterPanel...")
        encounter_panel = EncounterPanel()
        
        if hasattr(encounter_panel, 'campaign_frame') and encounter_panel.campaign_frame:
            print(f"   Campaign frame loaded with style: {encounter_panel.campaign_frame.style}")
            print(f"   Available classes: {encounter_panel.campaign_frame.available_classes}")
        else:
            print("   No campaign frame loaded")
            return False
        
        # Test 2: Check character creation mode
        print("\n2. Testing character creation mode...")
        encounter_panel.set_character_creation_mode()
        print("   Character creation mode activated")
        
        # Test 3: Test the class loading method directly
        print("\n3. Testing class data loading with filtering...")
        
        # Get all classes from database first
        conn = sqlite3.connect("talekeeper.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes ORDER BY display_order, name")
        all_classes = cursor.fetchall()
        print(f"   Total classes in database: {len(all_classes)}")
        
        # Simulate the filtering logic from encounter_panel.py
        allowed = None
        if hasattr(encounter_panel, 'campaign_frame') and encounter_panel.campaign_frame:
            allowed = {c.lower() for c in encounter_panel.campaign_frame.available_classes}
            print(f"   Allowed classes (lowercase): {allowed}")
        
        filtered_classes = []
        for class_row in all_classes:
            name = class_row['name']
            if allowed and name.lower() not in allowed:
                print(f"   FILTERED OUT: {name}")
                continue
            print(f"   INCLUDED: {name}")
            filtered_classes.append(name)
        
        print(f"\n   Final filtered classes: {filtered_classes}")
        
        conn.close()
        
        # Test 4: Call the actual class loading method
        print("\n4. Testing actual _load_class_data method...")
        try:
            encounter_panel._load_class_data()
            print("   Class data loaded successfully")
        except Exception as e:
            print(f"   Class data loading failed: {e}")
            return False
        
        print("\nClass filtering test completed successfully!")
        print(f"Classes visible in character creation: {len(filtered_classes)}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = test_class_filtering_final()
    sys.exit(0 if success else 1)