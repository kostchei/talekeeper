"""
Create a Rogue character with dual shortswords to test universal dual-wielding.
"""

import sqlite3
import uuid

def create_rogue_dual_wield():
    """Create a Rogue in slot 4 with two shortswords."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Create save slot 4
    save_slot_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT OR REPLACE INTO save_slots (id, slot_number, character_name, last_played, created_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
    """, (save_slot_id, 4, 'Sneaky', ))
    
    # Create Rogue character
    char_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO characters (
            id, save_slot_id, name, race_id, class_id, background_id,
            level, strength, dexterity, constitution, intelligence, wisdom, charisma,
            armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
            hit_dice_max, hit_dice_current,
            equipment_main_hand, equipment_off_hand
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        char_id, save_slot_id, 'Sneaky', 'human', 'rogue', 'criminal',
        1, 8, 16, 12, 14, 13, 10,  # Rogue stats (high Dex)
        13, 9, 9, 9, 9,  # HP and AC
        1, 1,  # Hit dice
        'Shortsword', 'Shortsword'  # Dual shortswords
    ))
    
    # Add shortswords to inventory
    for i in range(2):
        inv_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO character_inventory (
                id, character_id, item_name, quantity, equipped
            ) VALUES (?, ?, ?, ?, ?)
        """, (inv_id, char_id, 'Shortsword', 1, 1))
    
    conn.commit()
    conn.close()
    
    print("SUCCESS: Created Sneaky the Rogue in slot 4")
    print("- Class: Rogue (high Dex for finesse weapons)")
    print("- Equipment: Dual shortswords")
    print("- Ready to test universal dual-wielding")
    print()
    print("Load slot 4 in-game to test off-hand attacks in Bonus Actions tab")

if __name__ == "__main__":
    create_rogue_dual_wield()