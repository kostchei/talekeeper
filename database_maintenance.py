"""
Database maintenance script for TaleKeeper.
"""

import sqlite3

def cleanup_database():
    """Clean up orphaned records and inconsistent data."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    print("TaleKeeper Database Maintenance")
    print("=" * 40)
    
    # 1. Clean up orphaned save slots (slots marked as occupied but no character)
    cursor.execute("""
        SELECT COUNT(*) FROM save_slots s
        WHERE s.is_occupied = 1 
        AND s.id NOT IN (SELECT save_slot_id FROM characters WHERE save_slot_id IS NOT NULL)
    """)
    orphaned_slots = cursor.fetchone()[0]
    
    if orphaned_slots > 0:
        print(f"Fixing {orphaned_slots} orphaned save slots...")
        cursor.execute("""
            UPDATE save_slots 
            SET is_occupied = 0, character_name = NULL, save_name = NULL, 
                last_played = NULL, current_location = NULL
            WHERE is_occupied = 1 
            AND id NOT IN (SELECT save_slot_id FROM characters WHERE save_slot_id IS NOT NULL)
        """)
        conn.commit()
        print(f"  Fixed {orphaned_slots} orphaned save slots")
    
    # 2. Clean up characters without valid save slots
    cursor.execute("""
        SELECT COUNT(*) FROM characters 
        WHERE save_slot_id IS NULL 
        OR save_slot_id NOT IN (SELECT id FROM save_slots)
    """)
    orphaned_chars = cursor.fetchone()[0]
    
    if orphaned_chars > 0:
        print(f"Removing {orphaned_chars} characters without valid save slots...")
        # Get IDs for cascade deletion
        cursor.execute("""
            SELECT id FROM characters 
            WHERE save_slot_id IS NULL 
            OR save_slot_id NOT IN (SELECT id FROM save_slots)
        """)
        char_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete characters and related data
        for char_id in char_ids:
            cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
        conn.commit()
        print(f"  Removed {orphaned_chars} orphaned characters")
    
    # 3. Clean up orphaned character-related records
    tables_to_clean = [
        'character_inventory',
        'character_feats', 
        'character_features',
        'character_proficiencies',
        'character_weapon_masteries'
    ]
    
    total_orphaned = 0
    for table in tables_to_clean:
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table} 
            WHERE character_id NOT IN (SELECT id FROM characters)
        """)
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute(f"""
                DELETE FROM {table} 
                WHERE character_id NOT IN (SELECT id FROM characters)
            """)
            total_orphaned += count
    
    if total_orphaned > 0:
        conn.commit()
        print(f"Cleaned up {total_orphaned} orphaned character records")
    
    # Final report
    cursor.execute("SELECT COUNT(*) FROM save_slots WHERE is_occupied = 1")
    occupied_slots = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM characters")
    total_chars = cursor.fetchone()[0]
    
    print("-" * 40)
    print(f"Final state:")
    print(f"  Occupied save slots: {occupied_slots}")
    print(f"  Total characters: {total_chars}")
    
    if occupied_slots == total_chars:
        print("  Database is consistent!")
    else:
        print("  WARNING: Database inconsistency detected!")
    
    conn.close()

if __name__ == "__main__":
    cleanup_database()