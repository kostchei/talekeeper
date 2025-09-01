"""
Check if there are any existing Barbarian characters and what their AC values are.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def check_existing_barbarians():
    """Check existing Barbarian characters' AC values."""
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Find all Barbarian characters
    cursor.execute("""
        SELECT name, class_id, armor_class, strength, dexterity, constitution
        FROM characters 
        WHERE class_id = 'barbarian'
    """)
    
    barbarians = cursor.fetchall()
    
    if not barbarians:
        print("No Barbarian characters found in database")
        conn.close()
        return
    
    print(f"Found {len(barbarians)} Barbarian character(s):")
    
    for name, class_id, current_ac, strength, dexterity, constitution in barbarians:
        dex_mod = (dexterity - 10) // 2
        con_mod = (constitution - 10) // 2
        expected_ac = 10 + dex_mod + con_mod
        
        print(f"\n--- {name} ---")
        print(f"Stats: STR {strength}, DEX {dexterity} ({dex_mod:+d}), CON {constitution} ({con_mod:+d})")
        print(f"Current AC in DB: {current_ac}")
        print(f"Expected Unarmored Defense AC: 10 + {dex_mod} + {con_mod} = {expected_ac}")
        
        if current_ac == expected_ac:
            print("✓ AC is correct")
        else:
            print(f"✗ AC should be {expected_ac} but is {current_ac}")
    
    conn.close()

if __name__ == "__main__":
    check_existing_barbarians()