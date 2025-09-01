"""
Test barbarian starting equipment.
"""

import sqlite3
from core.game_engine_sqlite import GameEngineSQLite

def test_barbarian_equipment():
    """Test that barbarian gets correct starting equipment."""
    
    # Initialize the game engine
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create a barbarian character
    character_data = {
        'name': 'TestBarbarian',
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
        'equipment_choices': {'barbarian_choice': 'Greataxe'},  # Choose greataxe
        'notes': 'Test barbarian with greataxe choice'
    }
    
    print(f"Creating barbarian with equipment choice: {character_data['equipment_choices']}")
    
    # Find an empty save slot
    save_slot = 101
    
    # Create the character
    created_character = engine.create_new_character_sync(character_data, save_slot=save_slot)
    
    if created_character:
        print(f"\nCharacter created: {created_character.name}")
        
        # Check inventory
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, item_type, quantity, description
            FROM character_inventory
            WHERE character_id = ?
            ORDER BY item_type, item_name
        """, (created_character.id,))
        
        inventory = cursor.fetchall()
        
        print(f"\nInventory ({len(inventory)} items):")
        for item_name, item_type, quantity, description in inventory:
            print(f"  - {item_name} x{quantity} ({item_type}): {description}")
        
        # Check for expected items
        item_names = [item[0] for item in inventory]
        expected_items = ['Scimitar', 'Greataxe', 'Explorer\'s Pack', 'Javelin']
        
        missing = []
        for expected in expected_items:
            if expected not in item_names:
                missing.append(expected)
        
        conn.close()
        
        if not missing:
            print("\n[PASS] All expected barbarian equipment present!")
            return True
        else:
            print(f"\n[FAIL] Missing items: {missing}")
            return False
    else:
        print("[FAIL] Character creation failed")
        return False

if __name__ == "__main__":
    success = test_barbarian_equipment()
    
    # Clean up test character
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM characters WHERE name = 'TestBarbarian'")
    conn.commit()
    conn.close()