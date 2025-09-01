"""
Test that scimitars are now added as separate items for dual-wielding.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_scimitar_fix():
    """Test that Barbarian scimitars don't stack."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create a test barbarian
    character_data = {
        'name': 'TestScimitarFix',
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
        'notes': 'Test scimitar dual-wield fix'
    }
    
    print("Creating barbarian to test scimitar stacking fix...")
    
    created = engine.create_new_character_sync(character_data, save_slot=108)
    
    if created:
        print(f"SUCCESS: Character created: {created.name}")
        
        # Check scimitars in inventory
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, quantity, equipped 
            FROM character_inventory 
            WHERE character_id = ? AND item_name = 'Scimitar'
            ORDER BY equipped DESC
        """, (created.id,))
        
        scimitars = cursor.fetchall()
        
        print(f"\nScimitars in inventory:")
        for item_name, quantity, equipped in scimitars:
            equipped_status = "equipped" if equipped else "unequipped"
            print(f"  - {item_name} (quantity: {quantity}, {equipped_status})")
        
        # Check total scimitar count
        cursor.execute("""
            SELECT COUNT(*) FROM character_inventory 
            WHERE character_id = ? AND item_name = 'Scimitar'
        """, (created.id,))
        
        scimitar_count = cursor.fetchone()[0]
        
        if scimitar_count == 2:
            print(f"SUCCESS: Found {scimitar_count} separate scimitar entries (not stacked)")
            
            # Check if one is equipped
            equipped_count = sum(1 for _, _, equipped in scimitars if equipped)
            if equipped_count == 1:
                print("SUCCESS: One scimitar is equipped, one is unequipped")
                result = True
            else:
                print(f"FAIL: Expected 1 equipped scimitar, found {equipped_count}")
                result = False
        else:
            print(f"FAIL: Expected 2 separate scimitar entries, found {scimitar_count}")
            result = False
        
        # Check javelins are still stacked
        cursor.execute("""
            SELECT item_name, quantity 
            FROM character_inventory 
            WHERE character_id = ? AND item_name = 'Javelin'
        """, (created.id,))
        
        javelins = cursor.fetchall()
        if javelins:
            javelin_name, javelin_qty = javelins[0]
            print(f"\nJavelins: {javelin_name} (quantity: {javelin_qty})")
            if javelin_qty == 4:
                print("SUCCESS: Javelins are properly stacked")
            else:
                print(f"FAIL: Expected 4 javelins, found {javelin_qty}")
        
        conn.close()
        
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
    test_scimitar_fix()