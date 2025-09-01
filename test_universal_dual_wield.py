"""
Test universal dual-wielding system with different character classes.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_universal_dual_wield():
    """Test that dual-wielding works for any character class."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    print("=== TESTING UNIVERSAL DUAL-WIELDING SYSTEM ===\n")
    
    # Find all characters
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.class_id, s.slot_number,
               c.equipment_main_hand, c.equipment_off_hand
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id
        ORDER BY s.slot_number
    """)
    
    characters = cursor.fetchall()
    print(f"Found {len(characters)} characters to test:\n")
    
    for char_id, name, char_class, slot, main_hand, off_hand in characters:
        print(f"--- {name} ({char_class}) in slot {slot} ---")
        print(f"Main hand: {main_hand}")
        print(f"Off hand: {off_hand}")
        
        # Check if dual-wielding
        if main_hand and off_hand and main_hand != 'None' and off_hand != 'None':
            print("STATUS: DUAL-WIELDING DETECTED")
            
            # Load character and test action panel data
            character = engine.load_character_sync(slot)
            
            # Test what equipped items dict would contain
            equipped_items = {}
            if character.equipment_main_hand:
                main_item = engine.get_equipment_item_sync(character.equipment_main_hand)
                equipped_items['main_hand'] = main_item
            if character.equipment_off_hand:
                off_item = engine.get_equipment_item_sync(character.equipment_off_hand)
                equipped_items['off_hand'] = off_item
                
            # Check if off-hand weapon would create bonus action
            off_hand_item = equipped_items.get('off_hand')
            if off_hand_item and off_hand_item.get('item_type') == 'weapon':
                weapon_props = off_hand_item.get('weapon_properties', [])
                print(f"Off-hand weapon: {off_hand_item.get('name')} (properties: {weapon_props})")
                print("RESULT: Off-hand attack SHOULD appear in Bonus Actions")
            else:
                print("RESULT: Off-hand is not a weapon - no bonus action")
                
        else:
            print("STATUS: Not dual-wielding")
            
        print()
        
    conn.close()
    
    print("=== TEST COMPLETE ===")
    print("To fully test, run the game and:")
    print("1. Load a character")
    print("2. Equip two weapons")
    print("3. Check Bonus Actions tab for off-hand attack")
    print("4. Verify damage calculations (main hand gets ability mod, off hand doesn't)")

if __name__ == "__main__":
    test_universal_dual_wield()