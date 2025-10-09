import sqlite3

character_id = '38140dc8-38e9-4fda-84b6-d43fc5b3e807'

conn = sqlite3.connect('talekeeper.db')
cursor = conn.cursor()

print("Adding default Warlock spells for Lesahn...")

cursor.execute("""
    INSERT INTO character_spells (
        character_id, spell_id, spell_level, is_prepared,
        source, source_level, always_prepared
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", (character_id, 'eldritch_blast', 0, True, 'class', 1, True))

cursor.execute("""
    INSERT INTO character_spells (
        character_id, spell_id, spell_level, is_prepared,
        source, source_level, always_prepared
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", (character_id, 'chill_touch', 0, True, 'class', 1, True))

cursor.execute("""
    INSERT INTO character_spells (
        character_id, spell_id, spell_level, is_prepared,
        source, source_level, always_prepared
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", (character_id, 'hex', 1, True, 'class', 1, False))

cursor.execute("""
    INSERT INTO character_spells (
        character_id, spell_id, spell_level, is_prepared,
        source, source_level, always_prepared
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", (character_id, 'hellish_rebuke', 1, True, 'class', 1, False))

conn.commit()

cursor.execute("""
    SELECT cs.spell_id, s.name, s.level
    FROM character_spells cs
    JOIN spells s ON cs.spell_id = s.id
    WHERE cs.character_id = ?
    ORDER BY s.level, s.name
""", (character_id,))

print("\nLesahn's spells:")
for row in cursor.fetchall():
    print(f"  - {row[1]} (Level {row[2]})")

conn.close()
print("\nDone! Reload the character to see spell action cards.")
