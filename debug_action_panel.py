"""
Debug what equipped items the action panel gets for Bog.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def debug_action_panel_data():
    """Check what data the action panel would receive for Bog."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Find Bog's slot
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.slot_number 
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id
        WHERE c.name = 'Bog'
    """)
    slot = cursor.fetchone()[0]
    conn.close()
    
    # Load Bog
    bog = engine.load_character_sync(slot)
    
    print(f"=== BOG CHARACTER DATA ===")
    print(f"Name: {bog.name}")
    print(f"Main hand: {bog.equipment_main_hand}")
    print(f"Off hand: {bog.equipment_off_hand}")
    
    # Simulate what main_window._on_item_equipped does
    equipped_items = {}
    if bog.equipment_main_hand:
        item_data = engine.get_equipment_item_sync(bog.equipment_main_hand)
        equipped_items['main_hand'] = item_data
    if bog.equipment_off_hand:
        item_data = engine.get_equipment_item_sync(bog.equipment_off_hand)
        equipped_items['off_hand'] = item_data
    if bog.equipment_armor:
        item_data = engine.get_equipment_item_sync(bog.equipment_armor)
        equipped_items['armor'] = item_data
    if bog.equipment_shield and 'off_hand' not in equipped_items:
        item_data = engine.get_equipment_item_sync(bog.equipment_shield)
        equipped_items['off_hand'] = item_data
        
    print(f"\n=== EQUIPPED_ITEMS DICT (what action panel gets) ===")
    for slot, item_data in equipped_items.items():
        if item_data:
            print(f"{slot}:")
            print(f"  name: {item_data.get('name', 'NO NAME')}")
            print(f"  item_type: {item_data.get('item_type', 'NO TYPE')}")
            print(f"  weapon_properties: {item_data.get('weapon_properties', 'NO PROPS')}")
            print(f"  damage_dice: {item_data.get('damage_dice', 'NO DAMAGE')}")
            print(f"  damage_type: {item_data.get('damage_type', 'NO DAMAGE_TYPE')}")
        else:
            print(f"{slot}: None/Empty")
    
    # Test off-hand weapon card creation logic
    print(f"\n=== OFF-HAND WEAPON CARD TEST ===")
    off_hand = equipped_items.get('off_hand')
    if off_hand and off_hand.get('item_type') == 'weapon':
        print(f"OFF-HAND WEAPON DETECTED:")
        print(f"  Name: {off_hand.get('name', 'Unknown')}")
        print(f"  Type: {off_hand.get('item_type')}")
        print(f"  Properties: {off_hand.get('weapon_properties', [])}")
        print(f"RESULT: Off-hand attack card SHOULD be created")
    else:
        print(f"NO OFF-HAND WEAPON:")
        if off_hand:
            print(f"  Off-hand item: {off_hand.get('name')} (type: {off_hand.get('item_type')})")
        else:
            print(f"  Off-hand slot is empty")
        print(f"RESULT: Off-hand attack card will NOT be created")

if __name__ == "__main__":
    debug_action_panel_data()