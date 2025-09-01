"""
Test that equipment loads properly after character generation without needing to save/exit.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_equipment_loading():
    """Test that equipment and inventory load immediately after character creation."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create a test barbarian
    character_data = {
        'name': 'TestEquipmentLoad',
        'race_id': 'human',
        'class_id': 'barbarian',
        'background_id': 'Soldier',
        'level': 1,
        'experience_points': 0,
        'strength': 16,
        'dexterity': 13,
        'constitution': 15,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'feats': [],
        'armor_class': 12,
        'hit_points_max': 13,
        'hit_points_current': 13,
        'hit_dice_max': 1,
        'hit_dice_current': 1,
        'proficiencies': [],
        'features': {},
        'equipment_choices': {'barbarian_choice': 'Greataxe'},
        'notes': 'Test equipment loading after creation'
    }
    
    print("Creating barbarian to test equipment loading...")
    
    created = engine.create_new_character_sync(character_data, save_slot=109)
    
    if created:
        print(f"SUCCESS: Character created: {created.name}")
        
        # Test that we can immediately get the inventory
        inventory = engine.get_character_inventory_sync(created.id)
        
        print(f"\nInventory loaded ({len(inventory)} items):")
        equipped_scimitars = 0
        unequipped_scimitars = 0
        
        # Check the character_inventory table directly
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, quantity, equipped
            FROM character_inventory
            WHERE character_id = ? 
            ORDER BY item_name, equipped DESC
        """, (created.id,))
        
        all_items = cursor.fetchall()
        
        for item_name, quantity, equipped in all_items:
            equipped_status = "equipped" if equipped else "unequipped"
            print(f"  - {item_name} (qty: {quantity}, {equipped_status})")
            
            if item_name == 'Scimitar':
                if equipped:
                    equipped_scimitars += 1
                else:
                    unequipped_scimitars += 1
        
        conn.close()
        
        # Verify the fix works
        if len(inventory) > 0:
            print(f"\nSUCCESS: Inventory has {len(inventory)} items (can be loaded immediately)")
            
            if equipped_scimitars == 1 and unequipped_scimitars == 1:
                print("SUCCESS: Found 1 equipped and 1 unequipped scimitar for dual-wielding")
                result = True
            else:
                print(f"ISSUE: Expected 1 equipped + 1 unequipped scimitar, got {equipped_scimitars} equipped + {unequipped_scimitars} unequipped")
                result = False
        else:
            print("FAIL: Inventory is empty - equipment not loading properly")
            result = False
        
        # Clean up
        conn = sqlite3.connect("talekeeper.db")
        conn.execute("DELETE FROM characters WHERE name = ?", (created.name,))
        conn.commit()
        conn.close()
        
        return result
    else:
        print("FAIL: Character creation failed")
        return False

if __name__ == "__main__":
    test_equipment_loading()