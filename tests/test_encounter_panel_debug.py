#test
#!/usr/bin/env python3
"""
Debug EncounterPanel Campaign Frame Loading
"""

import sys
import os
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_encounter_panel_debug():
    print("Debugging EncounterPanel Campaign Frame Loading...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from encounter_pane.campaign_frame import CampaignFrame
        
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Test loading the JSON file directly
        print("\n1. Testing JSON file loading...")
        campaign_path = os.path.join('encounter_pane', 'campaign', 'conan.json')
        with open(campaign_path, 'r') as f:
            frame_data = json.load(f)
        print(f"JSON data loaded: {frame_data.keys()}")
        
        # Test CampaignFrame construction with loaded data
        print("\n2. Testing CampaignFrame construction...")
        campaign_frame = CampaignFrame(
            name=frame_data.get('name', 'Conan'),
            monster_type_weights=frame_data.get('monster_type_weights', {}),
            difficulty_distribution=frame_data.get('difficulty_distribution', {}),
            rest_rules=frame_data.get('rest_rules', {}),
            style=frame_data.get('style', 'conan'),
            available_classes=frame_data.get('available_classes', [])
        )
        print(f"Campaign frame created: {campaign_frame.name}")
        print(f"Available classes: {campaign_frame.available_classes}")
        
        # Now test EncounterPanel
        print("\n3. Testing EncounterPanel creation...")
        from encounter_pane.encounter_panel import EncounterPanel
        
        # Create encounter panel - this should load campaign frame
        encounter_panel = EncounterPanel()
        print("EncounterPanel created successfully")
        
        if hasattr(encounter_panel, 'campaign_frame') and encounter_panel.campaign_frame:
            print(f"Campaign frame loaded in panel: {encounter_panel.campaign_frame.name}")
            print(f"Available classes in panel: {encounter_panel.campaign_frame.available_classes}")
        else:
            print("No campaign frame loaded in panel")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = test_encounter_panel_debug()
    sys.exit(0 if success else 1)