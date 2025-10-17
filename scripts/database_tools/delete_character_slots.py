"""
Delete characters from specified save slots.
Usage: python delete_character_slots.py --slots 8-19
       python delete_character_slots.py --slots 8,9,10
"""

import sqlite3
import sys
from pathlib import Path

def delete_character_slots(db_path: str, slot_range: str):
    """Delete characters from specified save slots."""

    if '-' in slot_range:
        start, end = map(int, slot_range.split('-'))
        slots = list(range(start, end + 1))
    elif ',' in slot_range:
        slots = [int(s.strip()) for s in slot_range.split(',')]
    else:
        slots = [int(slot_range)]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT save_slot_id, id, name, class_id
        FROM characters
        WHERE save_slot_id IN ({','.join('?' * len(slots))})
    """, slots)

    characters = cursor.fetchall()

    if not characters:
        print(f"No characters found in slots: {slots}")
        conn.close()
        return

    print(f"\nFound {len(characters)} character(s) to delete:")
    for slot_id, char_id, name, class_id in characters:
        print(f"  Slot {slot_id}: {name} ({class_id})")

    confirm = input("\nDelete these characters? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        conn.close()
        return

    for slot_id, char_id, name, class_id in characters:
        print(f"Deleting {name} from slot {slot_id}...")

        cursor.execute("DELETE FROM character_inventory WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_feats WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_spells WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_conditions WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_magical_bonuses WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM barbarian_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM warlock_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM warlock_invocations WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))

    conn.commit()
    conn.close()

    print(f"\nDeleted {len(characters)} character(s) successfully!")

if __name__ == "__main__":
    db_path = Path(__file__).parent.parent.parent / "talekeeper.db"

    if len(sys.argv) < 3 or sys.argv[1] != '--slots':
        print("Usage: python delete_character_slots.py --slots 8-19")
        print("       python delete_character_slots.py --slots 8,9,10")
        sys.exit(1)

    slot_range = sys.argv[2]
    delete_character_slots(str(db_path), slot_range)
