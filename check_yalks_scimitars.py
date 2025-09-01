"""
Check exactly what scimitars Yalks has in his inventory.
"""

import sqlite3

def check_yalks_scimitars():
    """Check all of Yalks' scimitars in detail."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get Yalks' character ID
    cursor.execute("SELECT id, name FROM characters WHERE name = 'Yalks'")
    char_id, name = cursor.fetchone()
    
    print(f"=== {name}'s INVENTORY DETAILS ===")
    
    # Get ALL items, focusing on scimitars
    cursor.execute("""
        SELECT id, item_name, item_type, quantity, equipped
        FROM character_inventory
        WHERE character_id = ?
        ORDER BY item_name, equipped DESC
    """, (char_id,))
    
    all_items = cursor.fetchall()
    
    scimitar_count = 0
    equipped_scimitars = 0
    
    print("All inventory items:")
    for inv_id, item_name, item_type, quantity, equipped in all_items:
        status = "EQUIPPED" if equipped else "unequipped" 
        print(f"  {item_name} x{quantity} ({item_type}) - {status} [ID: {inv_id}]")
        
        if item_name == 'Scimitar':
            scimitar_count += quantity
            if equipped:
                equipped_scimitars += 1
    
    print(f"\nScimitar summary:")
    print(f"  Total scimitar entries: {scimitar_count}")
    print(f"  Equipped scimitar entries: {equipped_scimitars}")
    
    # The issue might be that we have 2 separate inventory entries for scimitars
    cursor.execute("""
        SELECT id, item_name, quantity, equipped
        FROM character_inventory
        WHERE character_id = ? AND item_name = 'Scimitar'
        ORDER BY equipped DESC
    """, (char_id,))
    
    scimitars = cursor.fetchall()
    
    print(f"\nDetailed scimitar breakdown:")
    for inv_id, item_name, quantity, equipped in scimitars:
        status = "EQUIPPED" if equipped else "unequipped"
        print(f"  Entry {inv_id}: {item_name} x{quantity} - {status}")
    
    conn.close()

if __name__ == "__main__":
    check_yalks_scimitars()