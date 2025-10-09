import sqlite3

character_id = '38140dc8-38e9-4fda-84b6-d43fc5b3e807'

conn = sqlite3.connect('talekeeper.db')
cursor = conn.cursor()

print("Adding Warlock pact magic slots for Lesahn (Level 1)...")

cursor.execute("DELETE FROM character_spell_slots WHERE character_id = ?", (character_id,))

cursor.execute("""
    INSERT INTO character_spell_slots
    (character_id, spell_level, max_slots, used_slots, slot_type)
    VALUES (?, 1, 1, 0, 'pact')
""", (character_id,))

print("  - Added 1 Pact Magic slot at 1st level")

conn.commit()

cursor.execute("""
    SELECT spell_level, max_slots, used_slots, slot_type
    FROM character_spell_slots
    WHERE character_id = ?
""", (character_id,))

print("\nLesahn's spell slots:")
for row in cursor.fetchall():
    print(f"  - Level {row[0]}: {row[1]} slots ({row[3]} type)")

conn.close()
print("\nDone! Pact magic slots initialized. Reload character to see spell action cards.")
