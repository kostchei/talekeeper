#test
#!/usr/bin/env python3
"""
Simple CampaignFrame Test
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_campaign_frame():
    print("Testing CampaignFrame...")
    
    try:
        from encounter_pane.campaign_frame import CampaignFrame
        print("Import successful")
        
        # Test constructor with all parameters
        campaign = CampaignFrame(
            name="Test",
            monster_type_weights={'humanoid': 1.0},
            difficulty_distribution={'low': 1.0},
            rest_rules={'short': 1},
            style='test',
            available_classes=['fighter', 'rogue']
        )
        print(f"Campaign created: {campaign.name}")
        print(f"Available classes: {campaign.available_classes}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = test_campaign_frame()
    sys.exit(0 if success else 1)