
import sqlite3
import json
import os

def inspect_zagor():
    db_path = "talekeeper.db"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"Inspecting database: {db_path}")

    # Find Zagor
    cursor.execute("SELECT * FROM characters WHERE name LIKE '%Zagor%'")
    zagor = cursor.fetchone()

    if not zagor:
        print("Character 'Zagor' not found.")
        return

    print(f"Found Zagor: ID={zagor['id']}, Level={zagor['level']}, Class={zagor['class_id']}")

    # Check Invocations
    print("\n--- Warlock Invocations (warlock_invocations table) ---")
    try:
        cursor.execute("SELECT * FROM warlock_invocations WHERE character_id = ?", (zagor['id'],))
        rows = cursor.fetchall()
        if not rows:
            print("No rows in warlock_invocations.")
        for row in rows:
            print(dict(row))
    except sqlite3.OperationalError as e:
        print(f"Error querying warlock_invocations: {e}")

    # Check Features
    print("\n--- Character Features (character_features table) ---")
    cursor.execute("SELECT feature_name, feature_type, mechanics FROM character_features WHERE character_id = ?", (zagor['id'],))
    features = cursor.fetchall()
    found_invocations = False
    for f in features:
        if "invocation" in f['feature_name'].lower() or "invocation" in f['feature_type'].lower():
            found_invocations = True
            print(f"Feature: {f['feature_name']} ({f['feature_type']})")
            print(f"  Mechanics: {f['mechanics']}")
    
    if not found_invocations:
        print("No invocation features found in character_features.")

    # Check Warlock Features table
    print("\n--- Warlock Features (warlock_features table) ---")
    try:
        cursor.execute("SELECT * FROM warlock_features WHERE character_id = ?", (zagor['id'],))
        wf = cursor.fetchone()
        if wf:
            print(dict(wf))
        else:
            print("No entry in warlock_features.")
    except sqlite3.OperationalError as e:
        print(f"Error querying warlock_features: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_zagor()
