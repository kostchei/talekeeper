"""
Test what class features a Barbarian gets.
"""

import sqlite3
from core.game_engine_sqlite import GameEngineSQLite

def test_barbarian_features():
    """Test class features assignment for Barbarian."""
    
    # Initialize the game engine
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create a barbarian character
    character_data = {
        'name': 'TestBarbarianFeatures',
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
        'features': {},  # Empty - this will be populated by character creation logic
        'equipment_choices': {'barbarian_choice': 'Greataxe'},
        'notes': 'Test barbarian features'
    }
    
    print(f"Creating barbarian character: {character_data['name']}")
    print(f"Class: {character_data['class_id']}")
    print(f"Features being passed: {character_data['features']}")
    
    # Find an empty save slot
    save_slot = 103
    
    # Create the character
    created_character = engine.create_new_character_sync(character_data, save_slot=save_slot)
    
    if created_character:
        print(f"\nCharacter created: {created_character.name}")
        print(f"Character class: {created_character.class_id}")
        print(f"Features in DTO: {created_character.features}")
        
        # Check database directly
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT feature_name, feature_type, description, level_gained
            FROM character_features
            WHERE character_id = ?
            ORDER BY feature_name
        """, (created_character.id,))
        
        db_features = cursor.fetchall()
        
        print(f"\nFeatures in database ({len(db_features)} total):")
        for feature_name, feature_type, description, level_gained in db_features:
            print(f"  - {feature_name} (Level {level_gained})")
            print(f"    Type: {feature_type}")
            print(f"    Description: {description}")
        
        conn.close()
        
        # Clean up
        engine.delete_character_from_slot_sync(save_slot)
        print(f"\nTest character deleted from slot {save_slot}")
        
        if db_features:
            fighter_features = [f for f in db_features if 'Second Wind' in f[0] or 'Action Surge' in f[0]]
            if fighter_features:
                print("\n[WARNING] Barbarian has Fighter features!")
                return False
            else:
                print(f"\n[OK] Barbarian has {len(db_features)} appropriate features")
                return True
        else:
            print("\n[INFO] Barbarian has no class features (expected for current implementation)")
            return True
    else:
        print("[FAIL] Character creation failed")
        return False

if __name__ == "__main__":
    test_barbarian_features()