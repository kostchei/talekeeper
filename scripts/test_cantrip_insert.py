"""Test if cantrip insertion works directly"""
import sys
import sqlite3
import uuid
sys.path.insert(0, 'src')

db_path = 'talekeeper.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a temporary test character
test_char_id = str(uuid.uuid4())
print(f"Creating test character: {test_char_id}")

try:
    # Insert minimal character
    cursor.execute("""
        INSERT INTO characters (
            id, name, class_id, level, experience_points,
            strength, dexterity, constitution, intelligence, wisdom, charisma,
            hit_points_max, hit_points_current, armor_class, save_slot_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        test_char_id, 'TempTestWarlock', 'warlock', 1, 0,
        10, 14, 13, 12, 10, 16,
        8, 8, 12, 99  # Using save slot 99 which shouldn't exist
    ))

    # Initialize spellcasting
    cursor.execute("""
        INSERT INTO character_spellcasting (
            character_id, spellcasting_class, spellcasting_ability,
            spell_attack_bonus, spell_save_dc, ritual_casting,
            spellcasting_focus, cantrips_known
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (test_char_id, 'warlock', 'charisma', 5, 13, 0, 'component_pouch', 0))

    print("\nAttempting to insert cantrips:")
    cantrips = ['eldritch_blast', 'chill_touch']

    for cantrip_id in cantrips:
        print(f"  Inserting {cantrip_id}...")
        cursor.execute("""
            INSERT INTO character_spells (
                character_id, spell_id, spell_level, is_prepared,
                source, source_level, always_prepared
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (test_char_id, cantrip_id, 0, True, 'class', 1, True))
        print(f"    SUCCESS")

    print("\nAttempting to insert spells:")
    spells = ['hex', 'hellish_rebuke']

    for spell_id in spells:
        print(f"  Inserting {spell_id}...")
        cursor.execute("""
            INSERT INTO character_spells (
                character_id, spell_id, spell_level, is_prepared,
                source, source_level, always_prepared
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (test_char_id, spell_id, 1, True, 'class', 1, False))
        print(f"    SUCCESS")

    # Verify
    cursor.execute('''
        SELECT s.name, s.level, cs.is_prepared
        FROM character_spells cs
        JOIN spells s ON cs.spell_id = s.id
        WHERE cs.character_id = ?
        ORDER BY s.level, s.name
    ''', (test_char_id,))

    spells_in_db = cursor.fetchall()
    print(f"\nVerification: {len(spells_in_db)} spells saved:")
    for spell_name, spell_level, is_prepared in spells_in_db:
        level_text = 'Cantrip' if spell_level == 0 else f'Level {spell_level}'
        print(f"    - {spell_name} ({level_text}, prepared={is_prepared})")

    conn.commit()

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()

finally:
    # Clean up
    cursor.execute('DELETE FROM characters WHERE id = ?', (test_char_id,))
    conn.commit()
    conn.close()
    print(f"\nCleanup complete")
