"""
Debug Yalks' equipped weapons to see why off-hand attack isn't showing.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def debug_yalks_equipment():
    """Check what equipment Yalks has and how it's stored."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Find Yalks' character data
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get Yalks' basic info and equipment slots
    cursor.execute("""
        SELECT id, name, equipment_main_hand, equipment_off_hand, equipment_armor, equipment_shield
        FROM characters
        WHERE name = 'Yalks'
    """)
    
    yalks_row = cursor.fetchone()
    if not yalks_row:
        print("Yalks not found in database")
        return
        
    char_id, name, main_hand, off_hand, armor, shield = yalks_row
    
    print("=== YALKS EQUIPMENT SLOTS ===")
    print(f"Character: {name} (ID: {char_id})")
    print(f"Main hand: {main_hand}")
    print(f"Off hand: {off_hand}")
    print(f"Armor: {armor}")
    print(f"Shield: {shield}")
    
    # Check inventory for equipped weapons
    cursor.execute("""
        SELECT item_name, item_type, equipped, quantity
        FROM character_inventory
        WHERE character_id = ? AND item_type = 'weapon'
        ORDER BY equipped DESC, item_name
    """, (char_id,))
    
    weapons = cursor.fetchall()
    
    print(f"\n=== WEAPONS IN INVENTORY ===")
    if weapons:
        for weapon_name, weapon_type, equipped, quantity in weapons:
            status = "EQUIPPED" if equipped else "unequipped"
            print(f"  {weapon_name} x{quantity} ({weapon_type}) - {status}")
    else:
        print("  No weapons found in inventory")
    
    # Test how main_window would load this data
    print(f"\n=== SIMULATING MAIN_WINDOW EQUIPMENT LOADING ===")
    
    # Load Yalks from slot
    slot_cursor = cursor.execute("""
        SELECT s.slot_number 
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id
        WHERE c.name = 'Yalks'
    """)
    slot = cursor.fetchone()[0]
    conn.close()
    
    print(f"Loading from slot {slot}...")
    saved_character = engine.load_character_sync(slot)
    
    if saved_character:
        print(f"Character loaded: {saved_character.name}")
        print(f"Equipment fields:")
        print(f"  equipment_main_hand: {saved_character.equipment_main_hand}")
        print(f"  equipment_off_hand: {saved_character.equipment_off_hand}")
        print(f"  equipment_armor: {saved_character.equipment_armor}")
        print(f"  equipment_shield: {saved_character.equipment_shield}")
        
        # Simulate what main_window does
        equipped_items = {}
        if saved_character.equipment_main_hand:
            item_data = engine.get_equipment_item_sync(saved_character.equipment_main_hand)
            equipped_items['main_hand'] = item_data if item_data else {'name': saved_character.equipment_main_hand, 'weight_lb': 0}
        if saved_character.equipment_off_hand:
            item_data = engine.get_equipment_item_sync(saved_character.equipment_off_hand)
            equipped_items['off_hand'] = item_data if item_data else {'name': saved_character.equipment_off_hand, 'weight_lb': 0}
            
        print(f"\n=== EQUIPPED_ITEMS DICT ===")
        for slot, item in equipped_items.items():
            print(f"  {slot}: {item}")
            if item and slot == 'off_hand':
                print(f"    item_type: {item.get('item_type', 'MISSING')}")
                print(f"    weapon_properties: {item.get('weapon_properties', 'MISSING')}")

if __name__ == "__main__":
    debug_yalks_equipment()