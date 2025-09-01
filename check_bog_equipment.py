"""
Check Bog's equipment setup.
"""

import sqlite3

def check_bog_equipment():
    """Check Bog's equipment and dual-wielding setup."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Find character named Bog
    cursor.execute("SELECT id, name, class_id FROM characters WHERE name LIKE '%og%' OR name LIKE '%arbarian%' ORDER BY created_at DESC")
    characters = cursor.fetchall()
    
    print("=== RECENT CHARACTERS ===")
    for char_id, name, class_id in characters:
        print(f"  {name} ({class_id}) - ID: {char_id}")
    
    if not characters:
        print("No characters found matching 'Bog' or recent Barbarians")
        return
        
    # Use the first match (most recent)
    char_id, name, class_id = characters[0]
    
    print(f"\n=== {name.upper()} EQUIPMENT CHECK ===")
    
    # Get character equipment slots
    cursor.execute("""
        SELECT equipment_main_hand, equipment_off_hand, equipment_armor, equipment_shield
        FROM characters WHERE id = ?
    """, (char_id,))
    
    main_hand, off_hand, armor, shield = cursor.fetchone()
    
    print(f"Equipment slots:")
    print(f"  Main hand: {main_hand}")
    print(f"  Off hand: {off_hand}")
    print(f"  Armor: {armor}")
    print(f"  Shield: {shield}")
    
    # Get equipped weapons from inventory
    cursor.execute("""
        SELECT item_name, item_type, equipped, quantity
        FROM character_inventory
        WHERE character_id = ? AND item_type = 'weapon'
        ORDER BY equipped DESC, item_name
    """, (char_id,))
    
    weapons = cursor.fetchall()
    
    print(f"\nWeapons in inventory:")
    equipped_count = 0
    for weapon_name, item_type, equipped, quantity in weapons:
        status = "EQUIPPED" if equipped else "unequipped"
        print(f"  {weapon_name} x{quantity} - {status}")
        if equipped:
            equipped_count += 1
    
    print(f"\nTotal equipped weapons: {equipped_count}")
    
    # Check if this matches the expected dual-wield setup
    scimitars_equipped = sum(1 for w in weapons if w[0] == 'Scimitar' and w[2] == 1)
    print(f"Scimitars equipped: {scimitars_equipped}")
    
    if scimitars_equipped == 2 and not main_hand and not off_hand:
        print("\nISSUE FOUND: 2 scimitars equipped but equipment slots are empty")
        print("This explains why off-hand attacks aren't appearing!")
    elif scimitars_equipped >= 1 and main_hand and off_hand:
        print(f"\nDual-wield setup looks correct")
    else:
        print(f"\nSetup needs fixing for proper dual-wielding")
    
    conn.close()

if __name__ == "__main__":
    check_bog_equipment()