"""
Fix Action Surge features for all Fighter characters level 2+
"""

import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.feature_integration import FeatureSystemIntegration
from services.fighter_abilities import FighterAbilitiesService

def fix_action_surge_features():
    """Add missing Action Surge features to level 2+ Fighters"""
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Find all Fighter characters level 2+
    cursor.execute("""
        SELECT id, name, level FROM characters 
        WHERE class_id = 'fighter' AND level >= 2
    """)
    fighters = cursor.fetchall()
    
    print(f"Found {len(fighters)} Fighter characters level 2+")
    
    feature_system = FeatureSystemIntegration('talekeeper.db')
    
    for fighter_id, name, level in fighters:
        print(f"\nProcessing {name} (Level {level})...")
        
        # Check if they have Action Surge feature
        cursor.execute("""
            SELECT feature_name FROM character_features 
            WHERE character_id = ? AND feature_name LIKE '%Action Surge%'
        """, (fighter_id,))
        has_action_surge = cursor.fetchone() is not None
        
        if not has_action_surge:
            print(f"  Adding Action Surge feature...")
            try:
                # Add Action Surge feature manually
                cursor.execute("""
                    INSERT INTO character_features 
                    (character_id, feature_name, level_gained, description, feature_type) 
                    VALUES (?, 'Action Surge', 2, 'Gain one additional action on your turn (except Magic action). Once per Short/Long Rest.', 'ability')
                """, (fighter_id,))
                print(f"  [OK] Added Action Surge feature")
            except Exception as e:
                print(f"  [ERROR] Failed to add Action Surge: {e}")
        else:
            print(f"  [OK] Already has Action Surge feature")
        
        # Make sure resources are correct
        try:
            fighter_service = FighterAbilitiesService()
            fighter_service.update_fighter_resources_for_level(fighter_id, level)
            print(f"  [OK] Updated Fighter resources for level {level}")
        except Exception as e:
            print(f"  [ERROR] Failed to update resources: {e}")
    
    conn.commit()
    conn.close()
    print(f"\nCompleted fixing Action Surge features!")

if __name__ == "__main__":
    fix_action_surge_features()