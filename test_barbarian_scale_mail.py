"""
Test barbarian with scale mail choice.
"""

import sqlite3
from core.game_engine_sqlite import GameEngineSQLite

def test_barbarian_scale_mail():
    """Test that barbarian gets scale mail when chosen."""
    
    # Initialize the game engine
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create a barbarian character choosing scale mail
    character_data = {
        'name': 'TestBarbarianArmor',
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
        'features': {},
        'equipment_choices': {'barbarian_choice': 'Scale Mail'},  # Choose scale mail
        'notes': 'Test barbarian with scale mail choice'
    }
    
    print(f"Creating barbarian with equipment choice: {character_data['equipment_choices']}")
    
    # Find an empty save slot
    save_slot = 102
    
    # Create the character
    created_character = engine.create_new_character_sync(character_data, save_slot=save_slot)
    
    if created_character:
        print(f"\nCharacter created: {created_character.name}")
        
        # Check inventory
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, item_type, quantity
            FROM character_inventory
            WHERE character_id = ? AND (item_type = 'armor' OR item_name = 'Greataxe')
            ORDER BY item_name
        """, (created_character.id,))
        
        relevant_items = cursor.fetchall()
        
        print(f"\nRelevant equipment:")
        for item_name, item_type, quantity in relevant_items:
            print(f"  - {item_name} x{quantity} ({item_type})")
        
        # Check for expected items
        item_names = [item[0] for item in relevant_items]
        
        has_scale_mail = 'Scale Mail' in item_names
        has_greataxe = 'Greataxe' in item_names
        
        conn.close()
        
        if has_scale_mail and not has_greataxe:
            print("\n[PASS] Barbarian correctly has Scale Mail and no Greataxe!")
            return True
        else:
            print(f"\n[FAIL] Expected Scale Mail (no Greataxe), got: {item_names}")
            return False
    else:
        print("[FAIL] Character creation failed")
        return False

if __name__ == "__main__":
    success = test_barbarian_scale_mail()
    
    # Clean up test character
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM characters WHERE name = 'TestBarbarianArmor'")
    conn.commit()
    conn.close()