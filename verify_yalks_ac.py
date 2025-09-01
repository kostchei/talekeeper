"""
Verify Yalks has correct AC in database and force update if needed.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def verify_yalks_ac():
    """Check and fix Yalks' AC."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Check current database state
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, armor_class, strength, dexterity, constitution, class_id
        FROM characters 
        WHERE name = 'Yalks'
    """)
    
    yalks_data = cursor.fetchone()
    
    if not yalks_data:
        print("Yalks not found in database")
        return
    
    char_id, name, current_ac, strength, dexterity, constitution, class_id = yalks_data
    
    print(f"=== Current State ===")
    print(f"Character: {name}")
    print(f"Class: {class_id}")
    print(f"Stats: STR {strength}, DEX {dexterity} (+{(dexterity-10)//2}), CON {constitution} (+{(constitution-10)//2})")
    print(f"Current AC in DB: {current_ac}")
    
    # Calculate correct AC
    correct_ac = engine._calculate_armor_class(char_id, strength, dexterity, constitution, class_id)
    print(f"Calculated AC (with Unarmored Defense): {correct_ac}")
    
    if current_ac != correct_ac:
        print(f"\n=== Fixing AC ===")
        cursor.execute("""
            UPDATE characters 
            SET armor_class = ?
            WHERE id = ?
        """, (correct_ac, char_id))
        conn.commit()
        print(f"Updated AC from {current_ac} to {correct_ac}")
    else:
        print(f"\nAC is already correct ({correct_ac})")
    
    conn.close()
    
    print("\n=== Testing Load ===")
    # Find Yalks' slot number
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.slot_number
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id
        WHERE c.name = 'Yalks'
    """)
    slot = cursor.fetchone()[0]
    conn.close()
    
    # Load the character
    loaded = engine.load_character_sync(slot)
    if loaded:
        print(f"Loaded character: {loaded.name}")
        print(f"CharacterDTO AC: {loaded.armor_class}")
        
        if loaded.armor_class == correct_ac:
            print(f"SUCCESS: Character loads with correct AC ({correct_ac})")
        else:
            print(f"ISSUE: Character loads with AC {loaded.armor_class} instead of {correct_ac}")

if __name__ == "__main__":
    verify_yalks_ac()