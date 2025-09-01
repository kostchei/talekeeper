"""
Test loading an existing Barbarian character to see if AC gets fixed.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_load_existing_barbarian():
    """Test loading Yalks to see if AC gets recalculated."""
    
    # First check current AC in database
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.slot_number, c.name, c.armor_class, c.dexterity, c.constitution
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id  
        WHERE c.name = 'Yalks'
    """)
    
    yalks_data = cursor.fetchone()
    conn.close()
    
    if not yalks_data:
        print("Yalks character not found")
        return
    
    slot_number, name, current_ac, dexterity, constitution = yalks_data
    dex_mod = (dexterity - 10) // 2
    con_mod = (constitution - 10) // 2
    expected_ac = 10 + dex_mod + con_mod
    
    print(f"=== BEFORE LOADING ===")
    print(f"Character: {name} (slot {slot_number})")
    print(f"Current AC in DB: {current_ac}")
    print(f"Expected AC: 10 + {dex_mod} + {con_mod} = {expected_ac}")
    
    print(f"\n=== LOADING CHARACTER ===")
    engine = GameEngineSQLite("talekeeper.db")
    loaded_character = engine.load_character_sync(slot_number)
    
    if loaded_character:
        print(f"Loaded: {loaded_character.name}")
        print(f"AC after loading: {loaded_character.armor_class}")
        
        # Check database again
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("SELECT armor_class FROM characters WHERE name = ?", (name,))
        new_db_ac = cursor.fetchone()[0]
        conn.close()
        
        print(f"DB AC after loading: {new_db_ac}")
        
        if loaded_character.armor_class == expected_ac and new_db_ac == expected_ac:
            print(f"SUCCESS: AC fixed from {current_ac} to {expected_ac}")
        else:
            print(f"ISSUE: AC not properly fixed")
            print(f"  Expected: {expected_ac}")
            print(f"  Character DTO: {loaded_character.armor_class}")  
            print(f"  Database: {new_db_ac}")
    else:
        print("Failed to load character")

if __name__ == "__main__":
    test_load_existing_barbarian()