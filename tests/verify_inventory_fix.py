import sqlite3
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from talekeeper.core.game_engine_sqlite import GameEngineSQLite

def verify_inventory_fix():
    db_path = 'talekeeper.db'
    engine = GameEngineSQLite(db_path)
    
    # Create a test character with all required fields
    character_data = {
        'name': 'InventoryTestChar',
        'class_id': 'fighter',
        'background_id': 'Soldier',
        'level': 1,
        'race_id': 'Human',
        'strength': 15,
        'dexterity': 14,
        'constitution': 13,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'hit_points_max': 11,  # 10 (Fighter d10) + 1 (CON mod)
        'hit_points_current': 11,
        'equipment_choices': {
            'fighter_choice_1': 'Chain Mail',
            'fighter_choice_2': '2 Handaxes'  # Should be normalized to Handaxe
        },
        'skip_automatic_equipment': False
    }
    
    print("Creating test character...")
    try:
        # Use save slot 99 for testing
        char_id = engine.create_new_character_sync(character_data, save_slot=99)
        print(f"Character created with ID: {char_id}")
        
        # Check inventory
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, item_type, quantity, value_gp, weight_lb FROM character_inventory WHERE character_id = ?", (char_id,))
        items = cursor.fetchall()
        conn.close()
        
        print("\nInventory Items:")
        found_rations = False
        found_handaxe = False
        found_pouch = False
        
        for item in items:
            name, type_, qty, val, weight = item
            print(f"- {name} (Type: {type_}, Qty: {qty}, Val: {val}, Wgt: {weight})")
            
            if name == 'Rations (1 day)':
                found_rations = True
            if name == 'Handaxe':
                found_handaxe = True
            if name == 'Pouch':
                found_pouch = True
                
        success = True
        if not found_rations:
            print("FAIL: 'Rations (1 day)' not found (check if 'Rations' was mapped correctly)")
            success = False
        else:
            print("PASS: 'Rations (1 day)' found")
            
        if not found_handaxe:
            print("FAIL: 'Handaxe' not found (check if '2 Handaxes' was normalized)")
            success = False
        else:
            print("PASS: 'Handaxe' found (normalization worked)")
            
        # Pouch might not be in Soldier background, let's check background content first or just check if it exists in DB
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM equipment WHERE name = 'Pouch'")
        pouch_db = cursor.fetchone()
        conn.close()
        
        if pouch_db:
            print("PASS: 'Pouch' exists in equipment database")
        else:
            print("FAIL: 'Pouch' NOT found in equipment database")
            success = False

        if success:
            print("\nVERIFICATION SUCCESSFUL!")
        else:
            print("\nVERIFICATION FAILED!")
            
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_inventory_fix()
