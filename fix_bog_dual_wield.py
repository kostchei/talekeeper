"""
Fix Bog's dual-wielding setup.
"""

import sqlite3

def fix_bog_dual_wield():
    """Set up Bog with proper dual-wielding scimitars."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get Bog's character ID
    cursor.execute("SELECT id, name FROM characters WHERE name = 'Bog'")
    result = cursor.fetchone()
    
    if not result:
        print("Bog character not found")
        return
        
    char_id, name = result
    print(f"Fixing dual-wielding for {name}")
    
    # Get both scimitar inventory entries
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
    
    scimitar1_id, scimitar1_equipped = scimitars[0]  
    scimitar2_id, scimitar2_equipped = scimitars[1]  
    
    print(f"Scimitar 1: equipped={scimitar1_equipped}")
    print(f"Scimitar 2: equipped={scimitar2_equipped}")
    
    # Make sure both scimitars are equipped
    cursor.execute("""
        UPDATE character_inventory 
        SET equipped = 1 
        WHERE id IN (?, ?)
    """, (scimitar1_id, scimitar2_id))
    
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
    
    print(f"\n{name} is now set up for dual-wielding!")
    print("Next steps:")
    print("1. Reload the character in the game")
    print("2. Check the Bonus Actions tab for off-hand attack")
    print("3. Main-hand should show 1d6+STR/DEX damage")
    print("4. Off-hand should show 1d6 damage (no modifier)")

if __name__ == "__main__":
    fix_bog_dual_wield()