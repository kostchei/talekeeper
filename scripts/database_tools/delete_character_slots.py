# core
#utility
# core
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

    cursor.execute("""
        SELECT s.id, c.id, c.name, c.class_id, s.slot_number
        FROM save_slots s
        LEFT JOIN characters c ON c.save_slot_id = s.id
        WHERE s.slot_number IN ({})
    """.format(','.join('?' * len(slots))), slots)

    characters = cursor.fetchall()

    characters_to_delete = [(slot_uuid, char_id, name, class_id, slot_num)
                            for slot_uuid, char_id, name, class_id, slot_num in characters
                            if char_id is not None]

    if not characters_to_delete:
        print(f"No characters found in slots: {slots}")
        conn.close()
        return

    print(f"\nFound {len(characters_to_delete)} character(s) to delete:")
    for slot_uuid, char_id, name, class_id, slot_num in characters_to_delete:
        print(f"  Slot {slot_num}: {name} ({class_id})")

    confirm = input("\nDelete these characters? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        conn.close()
        return

    for slot_uuid, char_id, name, class_id, slot_num in characters_to_delete:
        print(f"Deleting {name} from slot {slot_num}...")

        cursor.execute("DELETE FROM character_inventory WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_feats WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_spells WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_conditions WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM character_magical_bonuses WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM barbarian_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM warlock_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM warlock_invocations WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM fighter_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM paladin_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM rogue_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM cleric_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM wizard_features WHERE character_id = ?", (char_id,))
        cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
        cursor.execute("DELETE FROM save_slots WHERE id = ?", (slot_uuid,))

    conn.commit()
    conn.close()

    print(f"\nDeleted {len(characters_to_delete)} character(s) and cleared their save slots successfully!")

if __name__ == "__main__":
    db_path = Path(__file__).parent.parent.parent / "talekeeper.db"

    print(f"Database path: {db_path}")
    print(f"Database exists: {db_path.exists()}")

    if len(sys.argv) < 3 or sys.argv[1] != '--slots':
        print("Usage: python delete_character_slots.py --slots 8-19")
        print("       python delete_character_slots.py --slots 8,9,10")
        sys.exit(1)

    slot_range = sys.argv[2]
    delete_character_slots(str(db_path), slot_range)
