"""
Test Action Surge implementation for Fighter characters
"""

import sqlite3
import json

def test_fighter_features():
    """Check if Fighter characters have Action Surge feature"""
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Find Fighter characters level 2+
    cursor.execute("""
        SELECT id, name, level, class_id FROM characters 
        WHERE class_id = 'fighter' AND level >= 2 
        LIMIT 5
    """)
    fighters = cursor.fetchall()
    
    print("=== LEVEL 2+ FIGHTERS ===")
    for fighter_id, name, level, class_id in fighters:
        print(f"{name} (Level {level})")
        
        # Check character features
        cursor.execute("""
            SELECT feature_name, level_gained, description FROM character_features 
            WHERE character_id = ? 
            ORDER BY level_gained
        """, (fighter_id,))
        features = cursor.fetchall()
        
        has_action_surge = False
        for feature_name, level_gained, description in features:
            if 'Action Surge' in feature_name:
                has_action_surge = True
                print(f"  [OK] {feature_name} (Level {level_gained})")
            elif feature_name in ['Second Wind', 'Fighting Style', 'Extra Attack']:
                print(f"  [OK] {feature_name} (Level {level_gained})")
        
        if not has_action_surge and level >= 2:
            print(f"  [MISSING] Missing Action Surge feature!")
        
        # Check Action Surge resources
        cursor.execute("""
            SELECT action_surge_uses_current, action_surge_uses_max 
            FROM characters WHERE id = ?
        """, (fighter_id,))
        surge_data = cursor.fetchone()
        if surge_data:
            current, max_uses = surge_data
            print(f"  Action Surge: {current}/{max_uses} uses")
        else:
            print(f"  [MISSING] No Action Surge resource data")
        
        print()
    
    conn.close()

def test_action_surge_service():
    """Test the Action Surge service directly"""
    try:
        from services.fighter_abilities import FighterAbilitiesService
        service = FighterAbilitiesService()
        
        # Get a level 2+ fighter
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, level FROM characters 
            WHERE class_id = 'fighter' AND level >= 2 
            LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            fighter_id, name, level = result
            print(f"=== TESTING ACTION SURGE SERVICE ===")
            print(f"Character: {name} (Level {level})")
            
            # Test Action Surge
            result = service.use_action_surge(fighter_id)
            print(f"Action Surge result: {result}")
        else:
            print("No level 2+ Fighter found for testing")
            
    except Exception as e:
        print(f"Error testing Action Surge service: {e}")

if __name__ == "__main__":
    print("Testing Action Surge Implementation")
    print("=" * 50)
    
    test_fighter_features()
    test_action_surge_service()
    
    print("\nExpected for Level 2+ Fighters:")
    print("- Action Surge feature in character_features table")
    print("- action_surge_uses_current/max columns with proper values")
    print("- Action Surge card should appear in FREE actions tab")