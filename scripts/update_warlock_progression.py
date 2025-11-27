
import sqlite3
import json
import os

def update_progression():
    db_path = "talekeeper.db"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SRD 5.2 Warlock Invocation Progression
    # Level 1: 1
    # Level 2: 3
    # Level 3: 3
    # Level 4: 3
    # Level 5: 5
    # Level 6: 5
    # Level 7: 6
    # Level 8: 6
    # Level 9: 7
    # Level 10: 7
    # Level 11: 7
    # Level 12: 8
    # Level 13: 8
    # Level 14: 8
    # Level 15: 9
    # Level 16: 9
    # Level 17: 9
    # Level 18: 10
    # Level 19: 10
    # Level 20: 10
    
    progression = {
        "1": 1, "2": 3, "3": 3, "4": 3,
        "5": 5, "6": 5, "7": 6, "8": 6,
        "9": 7, "10": 7, "11": 7, "12": 8,
        "13": 8, "14": 8, "15": 9, "16": 9,
        "17": 9, "18": 10, "19": 10, "20": 10
    }

    print(f"Updating 'invocations_by_level' formula in {db_path}...")
    
    try:
        cursor.execute("""
            UPDATE ability_scaling_formulas
            SET formula_data = ?
            WHERE formula_name = 'invocations_by_level'
        """, (json.dumps(progression),))
        
        if cursor.rowcount == 0:
            print("Formula 'invocations_by_level' not found. Inserting...")
            cursor.execute("""
                INSERT INTO ability_scaling_formulas (formula_name, formula_data)
                VALUES (?, ?)
            """, ('invocations_by_level', json.dumps(progression)))
            
        conn.commit()
        print("Successfully updated invocation progression.")
        
        # Verify
        cursor.execute("SELECT formula_data FROM ability_scaling_formulas WHERE formula_name = 'invocations_by_level'")
        row = cursor.fetchone()
        print(f"New formula data: {row[0]}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_progression()
