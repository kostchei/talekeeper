"""
Fix Yalks to have proper dual-wielding setup with both scimitars equipped.
"""

import sqlite3

def fix_yalks_dual_wield():
    """Set up Yalks with proper dual-wielding scimitars."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get Yalks' character ID
    cursor.execute("SELECT id, name FROM characters WHERE name = 'Yalks'")
    char_id, name = cursor.fetchone()
    
    print(f"Setting up dual-wielding for {name}")
    
    # Get both scimitar inventory IDs
    cursor.execute("""
        SELECT id, equipped
        FROM character_inventory
        WHERE character_id = ? AND item_name = 'Scimitar'
        ORDER BY equipped DESC
    """, (char_id,))
    
    scimitars = cursor.fetchall()
    
    if len(scimitars) < 2:
        print(f"ERROR: Only found {len(scimitars)} scimitars, need 2 for dual wielding")
        return
    
    scimitar1_id, scimitar1_equipped = scimitars[0]  # Currently equipped
    scimitar2_id, scimitar2_equipped = scimitars[1]  # Currently unequipped
    
    print(f"Scimitar 1: {scimitar1_id} (equipped: {scimitar1_equipped})")
    print(f"Scimitar 2: {scimitar2_id} (equipped: {scimitar2_equipped})")
    
    # Make sure both scimitars are equipped
    cursor.execute("""
        UPDATE character_inventory 
        SET equipped = 1 
        WHERE id IN (?, ?)
    """, (scimitar1_id, scimitar2_id))
    
    print("Both scimitars set as equipped")
    
    # Assign to main hand and off hand slots
    cursor.execute("""
        UPDATE characters 
        SET equipment_main_hand = 'Scimitar', equipment_off_hand = 'Scimitar'
        WHERE id = ?
    """, (char_id,))
    
    print("Equipment slots updated: main_hand=Scimitar, off_hand=Scimitar")
    
    conn.commit()
    conn.close()
    
    # Test the result
    print("\n=== TESTING DUAL WIELD SETUP ===")
    from core.game_engine_sqlite import GameEngineSQLite
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Find slot number
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.slot_number 
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id
        WHERE c.name = 'Yalks'
    """)
    slot = cursor.fetchone()[0]
    conn.close()
    
    loaded = engine.load_character_sync(slot)
    if loaded:
        print(f"Character: {loaded.name}")
        print(f"Main hand: {loaded.equipment_main_hand}")
        print(f"Off hand: {loaded.equipment_off_hand}")
        
        # Test how equipped_items would be built
        equipped_items = {}
        if loaded.equipment_main_hand:
            item_data = engine.get_equipment_item_sync(loaded.equipment_main_hand)
            equipped_items['main_hand'] = item_data
        if loaded.equipment_off_hand:
            item_data = engine.get_equipment_item_sync(loaded.equipment_off_hand)
            equipped_items['off_hand'] = item_data
            
        print(f"Equipped items dict:")
        for slot, item in equipped_items.items():
            print(f"  {slot}: {item.get('name')} - {item.get('damage_dice')} {item.get('damage_type')}")
            print(f"    Properties: {item.get('weapon_properties')}")

if __name__ == "__main__":
    fix_yalks_dual_wield()