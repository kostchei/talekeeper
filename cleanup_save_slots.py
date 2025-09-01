"""
Clean up orphaned save slots and character records.
"""

import sqlite3

def cleanup_save_slots():
    """Clean up the save slots and characters tables."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    print("Current state of save slots:")
    print("-" * 60)
    
    # Show current state
    cursor.execute("""
        SELECT s.slot_number, s.is_occupied, s.character_name, c.name, c.id 
        FROM save_slots s 
        LEFT JOIN characters c ON s.id = c.save_slot_id 
        ORDER BY s.slot_number
    """)
    
    slots = cursor.fetchall()
    orphaned_slots = []
    
    for slot_num, occupied, slot_char_name, char_name, char_id in slots:
        if occupied and not char_id:
            orphaned_slots.append(slot_num)
            print(f"Slot {slot_num}: ORPHANED (marked as '{slot_char_name}' but no character)")
        elif occupied and char_id:
            print(f"Slot {slot_num}: {char_name} (ID: {char_id})")
        else:
            print(f"Slot {slot_num}: Empty")
    
    if orphaned_slots:
        print(f"\nFound {len(orphaned_slots)} orphaned slots: {orphaned_slots}")
        print("Cleaning up orphaned slots...")
        
        # Reset orphaned slots
        for slot_num in orphaned_slots:
            cursor.execute("""
                UPDATE save_slots 
                SET is_occupied = 0, 
                    character_name = NULL, 
                    save_name = NULL,
                    last_played = NULL,
                    current_location = NULL
                WHERE slot_number = ?
            """, (slot_num,))
            print(f"  Reset slot {slot_num}")
        
        conn.commit()
        print("\nOrphaned slots cleaned!")
    else:
        print("\nNo orphaned slots found.")
    
    # Also check for any characters without save slots
    cursor.execute("""
        SELECT id, name, save_slot_id 
        FROM characters 
        WHERE save_slot_id NOT IN (SELECT id FROM save_slots)
    """)
    
    orphaned_chars = cursor.fetchall()
    if orphaned_chars:
        print(f"\nFound {len(orphaned_chars)} characters without valid save slots:")
        for char_id, char_name, slot_id in orphaned_chars:
            print(f"  {char_name} (ID: {char_id}, Invalid slot: {slot_id})")
        
        # Delete orphaned characters
        print("\nDeleting orphaned characters...")
        for char_id, char_name, _ in orphaned_chars:
            cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
            print(f"  Deleted {char_name}")
        
        conn.commit()
    
    # Final summary
    print("\n" + "=" * 60)
    print("Final state:")
    cursor.execute("""
        SELECT COUNT(*) FROM save_slots WHERE is_occupied = 1
    """)
    occupied_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM characters
    """)
    char_count = cursor.fetchone()[0]
    
    print(f"Occupied save slots: {occupied_count}")
    print(f"Total characters: {char_count}")
    
    if occupied_count == char_count:
        print("[OK] Database is consistent!")
    else:
        print("[WARNING] Mismatch between occupied slots and characters")
    
    conn.close()

if __name__ == "__main__":
    cleanup_save_slots()