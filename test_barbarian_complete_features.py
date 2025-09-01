"""
Test complete Barbarian class features implementation.
"""

import sqlite3
from core.game_engine_sqlite import GameEngineSQLite

def test_barbarian_complete_features():
    """Test that Barbarian gets all appropriate class features."""
    
    # Initialize the game engine
    engine = GameEngineSQLite("talekeeper.db")
    
    print("Testing Barbarian Class Features")
    print("=" * 50)
    
    # Test Level 1 Barbarian
    print("\n1. Testing Level 1 Barbarian...")
    character_data = {
        'name': 'TestBarbLvl1',
        'race_id': 'human',
        'class_id': 'barbarian',
        'background_id': 'Soldier',
        'level': 1,
        'experience_points': 0,
        'strength': 16,
        'dexterity': 14,
        'constitution': 15,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'feats': [],
        'armor_class': 14,
        'hit_points_max': 14,
        'hit_points_current': 14,
        'hit_dice_max': 1,
        'hit_dice_current': 1,
        'proficiencies': [],
        'features': {},  # Will be populated by character creation
        'equipment_choices': {'barbarian_choice': 'Greataxe'},
        'notes': 'Test Level 1 Barbarian features'
    }
    
    # Create Level 1 character
    created_l1 = engine.create_new_character_sync(character_data, save_slot=104)
    
    if created_l1:
        # Check features in database
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT feature_name, description, level_gained
            FROM character_features
            WHERE character_id = ?
            ORDER BY level_gained, feature_name
        """, (created_l1.id,))
        
        l1_features = cursor.fetchall()
        
        print(f"Level 1 features ({len(l1_features)} total):")
        expected_l1 = ['Rage', 'Unarmored Defense']
        found_l1 = []
        
        for feature_name, description, level_gained in l1_features:
            found_l1.append(feature_name)
            print(f"  • {feature_name} (Level {level_gained})")
            print(f"    {description[:80]}{'...' if len(description) > 80 else ''}")
        
        # Verify expected features
        l1_success = all(feat in found_l1 for feat in expected_l1)
        if l1_success:
            print("  [PASS] All Level 1 features present!")
        else:
            missing = [f for f in expected_l1 if f not in found_l1]
            print(f"  [FAIL] Missing Level 1 features: {missing}")
        
        conn.close()
        engine.create_new_character_sync({'name': 'DELETE_L1'}, save_slot=104)  # Clean up
    else:
        print("  [FAIL] Level 1 character creation failed")
        l1_success = False
    
    # Test Level 2 Barbarian
    print("\n2. Testing Level 2 Barbarian...")
    character_data['name'] = 'TestBarbLvl2'
    character_data['level'] = 2
    character_data['notes'] = 'Test Level 2 Barbarian features'
    
    created_l2 = engine.create_new_character_sync(character_data, save_slot=105)
    
    if created_l2:
        # Check features in database
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT feature_name, description, level_gained
            FROM character_features
            WHERE character_id = ?
            ORDER BY level_gained, feature_name
        """, (created_l2.id,))
        
        l2_features = cursor.fetchall()
        
        print(f"Level 2 features ({len(l2_features)} total):")
        expected_l2 = ['Rage', 'Unarmored Defense', 'Reckless Attack', 'Danger Sense']
        found_l2 = []
        
        for feature_name, description, level_gained in l2_features:
            found_l2.append(feature_name)
            print(f"  • {feature_name} (Level {level_gained})")
            print(f"    {description[:80]}{'...' if len(description) > 80 else ''}")
        
        # Verify expected features
        l2_success = all(feat in found_l2 for feat in expected_l2)
        if l2_success:
            print("  [PASS] All Level 2 features present!")
        else:
            missing = [f for f in expected_l2 if f not in found_l2]
            print(f"  [FAIL] Missing Level 2 features: {missing}")
        
        conn.close()
        engine.create_new_character_sync({'name': 'DELETE_L2'}, save_slot=105)  # Clean up
    else:
        print("  [FAIL] Level 2 character creation failed")
        l2_success = False
    
    # Final results
    print("\n" + "=" * 50)
    if l1_success and l2_success:
        print("🎉 ALL TESTS PASSED! Barbarian features implemented correctly!")
        return True
    else:
        print("❌ Some tests failed. Check implementation.")
        return False

if __name__ == "__main__":
    success = test_barbarian_complete_features()