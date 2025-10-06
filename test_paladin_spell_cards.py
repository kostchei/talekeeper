import sqlite3

char_id = '3c17a911-88d7-422d-8999-949074b7f2ca'
db_path = 'talekeeper.db'

print("=== Checking Paladin Galahad Spell Card Setup ===\n")

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    cursor.execute("SELECT name, class_id, level, charisma FROM characters WHERE id = ?", (char_id,))
    char = cursor.fetchone()
    print(f"Character: {char[0]}")
    print(f"Class: {char[1]} Level {char[2]}")
    print(f"Charisma: {char[3]} (modifier: {(char[3] - 10) // 2})\n")

    cursor.execute("""
        SELECT spellcasting_ability, spell_attack_bonus, spell_save_dc
        FROM character_spellcasting WHERE character_id = ?
    """, (char_id,))
    spellcasting = cursor.fetchone()
    if spellcasting:
        print(f"Spellcasting Ability: {spellcasting[0]}")
        print(f"Spell Attack Bonus: +{spellcasting[1]}")
        print(f"Spell Save DC: {spellcasting[2]}\n")

    cursor.execute("""
        SELECT spell_level, max_slots, used_slots, slot_type
        FROM character_spell_slots WHERE character_id = ?
        ORDER BY spell_level
    """, (char_id,))
    print("Spell Slots:")
    for row in cursor.fetchall():
        available = row[1] - row[2]
        print(f"  Level {row[0]}: {available}/{row[1]} available ({row[3]})")

    cursor.execute("""
        SELECT s.name, s.level, cs.is_prepared, cs.always_prepared, cs.source
        FROM character_spells cs
        JOIN spells s ON cs.spell_id = s.id
        WHERE cs.character_id = ?
        ORDER BY s.level, s.name
    """, (char_id,))

    print("\nKnown Spells:")
    prepared_spells = []
    for row in cursor.fetchall():
        status = "PREPARED" if row[2] else "known"
        if row[3]:
            status += " (always)"
        print(f"  [{status}] {row[0]} (Level {row[1]}) - {row[4]}")
        if row[2] or row[3]:
            prepared_spells.append(row[0])

    print(f"\n✅ Total Prepared Spells: {len(prepared_spells)}")
    print(f"✅ Spell cards should appear for: {', '.join(prepared_spells)}")

print("\n=== Expected Spell Card Display ===")
print("In the Action Panel, you should see:")
print("  [1⭐] Level 1: Divine Favor")
print("  Slots: ●●● (3/3) | Time: 1 bonus action | (4 spells available)")
print("\nClicking it will let you choose from:")
for spell in prepared_spells:
    print(f"  - {spell}")
