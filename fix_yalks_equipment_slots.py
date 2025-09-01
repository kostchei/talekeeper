"""
Fix Yalks' equipment slots to match his equipped inventory items.
"""

import sqlite3
from core.game_engine_sqlite import GameEngineSQLite

def fix_yalks_equipment_slots():
    """Update Yalks' equipment slots based on equipped inventory."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get Yalks' character ID
    cursor.execute("SELECT id, name FROM characters WHERE name = 'Yalks'")
    yalks_data = cursor.fetchone()
    
    if not yalks_data:
        print("Yalks not found")
        return
        
    char_id, name = yalks_data
    print(f"Fixing equipment slots for {name} (ID: {char_id})")
    
    # Get equipped weapons from inventory
    cursor.execute("""
        SELECT item_name, item_type, equipped
        FROM character_inventory
        WHERE character_id = ? AND equipped = 1 AND item_type = 'weapon'
        ORDER BY item_name
    """, (char_id,))
    
    equipped_weapons = cursor.fetchall()
    
    print(f"Found {len(equipped_weapons)} equipped weapons:")
    for weapon_name, item_type, equipped in equipped_weapons:
        print(f"  - {weapon_name} ({item_type})")
    
    # For dual-wielding, we need to assign one to main hand and one to off hand
    main_hand_weapon = None
    off_hand_weapon = None
    
    if len(equipped_weapons) >= 1:
        main_hand_weapon = equipped_weapons[0][0]  # First scimitar to main hand
    if len(equipped_weapons) >= 2:
        off_hand_weapon = equipped_weapons[1][0]   # Second scimitar to off hand
    
    print(f"\nAssigning:")
    print(f"  Main hand: {main_hand_weapon}")
    print(f"  Off hand: {off_hand_weapon}")
    
    # Update character equipment slots
    cursor.execute("""
        UPDATE characters 
        SET equipment_main_hand = ?, equipment_off_hand = ?
        WHERE id = ?
    """, (main_hand_weapon, off_hand_weapon, char_id))
    
    conn.commit()
    conn.close()
    
    print("Equipment slots updated!")
    
    # Test loading the character to see if it works now
    print("\n=== TESTING CHARACTER LOADING ===")
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
        
        # Test equipment data loading
        equipped_items = {}
        if loaded.equipment_main_hand:
            item_data = engine.get_equipment_item_sync(loaded.equipment_main_hand)
            equipped_items['main_hand'] = item_data
            print(f"Main hand data: {item_data.get('damage_dice', 'NO DAMAGE')} {item_data.get('damage_type', 'NO TYPE')}")
        if loaded.equipment_off_hand:
            item_data = engine.get_equipment_item_sync(loaded.equipment_off_hand)
            equipped_items['off_hand'] = item_data
            print(f"Off hand data: {item_data.get('damage_dice', 'NO DAMAGE')} {item_data.get('damage_type', 'NO TYPE')}")

if __name__ == "__main__":
    fix_yalks_equipment_slots()