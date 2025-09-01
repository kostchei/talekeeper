"""
Fix Bog in slot 3 with dual-wielding setup.
"""

import sqlite3

def fix_bog_slot3():
    """Set up Bog (slot 3) with proper dual-wielding scimitars."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get Bog from slot 3
    cursor.execute("""
        SELECT c.id, c.name
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id  
        WHERE s.slot_number = 3
    """)
    
    result = cursor.fetchone()
    if not result:
        print("No character found in slot 3")
        return
        
    char_id, name = result
    print(f"Fixing dual-wielding for {name} in slot 3")
    
    # Check current equipment slots
    cursor.execute("""
        SELECT equipment_main_hand, equipment_off_hand
        FROM characters WHERE id = ?
    """, (char_id,))
    
    main_hand, off_hand = cursor.fetchone()
    print(f"Current equipment: main_hand={main_hand}, off_hand={off_hand}")
    
    # Get both scimitar inventory entries
    cursor.execute("""
        SELECT id, equipped
        FROM character_inventory
        WHERE character_id = ? AND item_name = 'Scimitar'
        ORDER BY equipped DESC
    """, (char_id,))
    
    scimitars = cursor.fetchall()
    print(f"Found {len(scimitars)} scimitars in inventory")
    
    if len(scimitars) < 2:
        print(f"ERROR: Only found {len(scimitars)} scimitars, need 2 for dual wielding")
        return
    
    for i, (scimitar_id, equipped) in enumerate(scimitars):
        print(f"  Scimitar {i+1}: equipped={equipped}")
    
    # Make sure both scimitars are equipped
    scimitar_ids = [s[0] for s in scimitars]
    cursor.execute(f"""
        UPDATE character_inventory 
        SET equipped = 1 
        WHERE id IN ({','.join(['?' for _ in scimitar_ids])})
    """, scimitar_ids)
    
    print("SUCCESS: Both scimitars set as equipped in inventory")
    
    # Assign to main hand and off hand slots
    cursor.execute("""
        UPDATE characters 
        SET equipment_main_hand = 'Scimitar', equipment_off_hand = 'Scimitar'
        WHERE id = ?
    """, (char_id,))
    
    print("SUCCESS: Equipment slots updated: main_hand=Scimitar, off_hand=Scimitar")
    
    conn.commit()
    conn.close()
    
    print(f"\n{name} (slot 3) is now set up for dual-wielding!")
    print("Reload the character to see off-hand attacks in Bonus Actions tab")

if __name__ == "__main__":
    fix_bog_slot3()