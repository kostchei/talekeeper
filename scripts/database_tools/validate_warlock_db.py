# core
#utility
# core
import sqlite3

def validate_warlock_database():
    """Validate Warlock database schema and data."""
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    print("=== Warlock Database Validation ===\n")

    # 1. Check warlock_features table
    cursor.execute("PRAGMA table_info(warlock_features)")
    columns = [row[1] for row in cursor.fetchall()]

    required_columns = [
        'character_id', 'level', 'pact_slots_current', 'pact_slots_max',
        'pact_slot_level', 'patron', 'pact_boon', 'eldritch_invocations',
        'magical_cunning_used', 'arcanum_6_used', 'arcanum_7_used',
        'arcanum_8_used', 'arcanum_9_used', 'dark_ones_luck_uses',
        'fiendish_resilience_type', 'hurl_through_hell_used'
    ]

    print("1. warlock_features table:")
    missing = [col for col in required_columns if col not in columns]
    if missing:
        print(f"   MISSING COLUMNS: {missing}")
    else:
        print(f"   All {len(required_columns)} required columns present")

    # 2. Check warlock_pact_progression
    cursor.execute("SELECT COUNT(*) FROM warlock_pact_progression")
    progression_count = cursor.fetchone()[0]
    print(f"\n2. warlock_pact_progression: {progression_count} levels")
    if progression_count != 20:
        print("   ERROR: Should have 20 levels")
    else:
        print("   OK")

    # Validate progression data
    cursor.execute("""
        SELECT level, num_slots, slot_level, invocations_known
        FROM warlock_pact_progression
        WHERE level IN (1, 5, 11, 20)
    """)
    print("\n   Key Level Progression:")
    for row in cursor.fetchall():
        level, slots, slot_lvl, inv = row
        print(f"   Level {level}: {slots} slots (level {slot_lvl}), {inv} invocations")

    # 3. Check invocations
    cursor.execute("SELECT COUNT(*) FROM invocations")
    inv_count = cursor.fetchone()[0]
    print(f"\n3. invocations table: {inv_count} invocations")

    # Check key invocations
    key_invocations = [
        'agonizing_blast', 'eldritch_smite', 'thirsting_blade',
        'eldritch_mind', 'devils_sight', 'pact_of_blade',
        'pact_of_chain', 'pact_of_tome'
    ]

    cursor.execute(f"""
        SELECT id FROM invocations
        WHERE id IN ({','.join('?' * len(key_invocations))})
    """, key_invocations)

    found_invocations = [row[0] for row in cursor.fetchall()]
    missing_inv = [inv for inv in key_invocations if inv not in found_invocations]

    if missing_inv:
        print(f"   MISSING KEY INVOCATIONS: {missing_inv}")
    else:
        print(f"   All key invocations present")

    # 4. Check patron features
    cursor.execute("SELECT COUNT(*) FROM warlock_patron_features WHERE patron = 'Fiend'")
    fiend_features = cursor.fetchone()[0]
    print(f"\n4. warlock_patron_features (Fiend): {fiend_features} features")

    cursor.execute("""
        SELECT level, feature_name
        FROM warlock_patron_features
        WHERE patron = 'Fiend'
        ORDER BY level
    """)
    print("   Fiend Patron Features:")
    for row in cursor.fetchall():
        print(f"   Level {row[0]}: {row[1]}")

    # 5. Check spell list
    cursor.execute("""
        SELECT COUNT(*)
        FROM spell_class_lists
        WHERE class_id = 'warlock'
        AND is_bonus_spell = FALSE
    """)
    spell_count = cursor.fetchone()[0]
    print(f"\n5. Warlock spell list: {spell_count} spells")

    # Count by level
    cursor.execute("""
        SELECT s.level, COUNT(*)
        FROM spell_class_lists scl
        JOIN spells s ON s.id = scl.spell_id
        WHERE scl.class_id = 'warlock'
        AND scl.is_bonus_spell = FALSE
        GROUP BY s.level
        ORDER BY s.level
    """)
    print("   Spells by level:")
    for row in cursor.fetchall():
        print(f"   Level {row[0]}: {row[1]} spells")

    # 6. Check Fiend bonus spells
    cursor.execute("""
        SELECT COUNT(*)
        FROM spell_class_lists
        WHERE class_id = 'warlock'
        AND is_bonus_spell = TRUE
        AND source_feature = 'fiend_patron'
    """)
    bonus_count = cursor.fetchone()[0]
    print(f"\n6. Fiend Patron bonus spells: {bonus_count} spells")

    # 7. Check key spells exist
    key_spells = ['eldritch_blast', 'hex', 'hellish_rebuke']
    cursor.execute(f"""
        SELECT id, name FROM spells
        WHERE id IN ({','.join('?' * len(key_spells))})
    """, key_spells)
    found_spells = {row[0]: row[1] for row in cursor.fetchall()}

    print("\n7. Key Warlock spells:")
    for spell_id in key_spells:
        if spell_id in found_spells:
            print(f"   {found_spells[spell_id]}")
        else:
            print(f"   MISSING: {spell_id}")

    # 8. Check warlock class
    cursor.execute("SELECT name, hit_die, primary_ability FROM classes WHERE id = 'warlock'")
    result = cursor.fetchone()
    print(f"\n8. Warlock class:")
    if result:
        print(f"   Name: {result[0]}")
        print(f"   Hit Die: d{result[1]}")
        print(f"   Primary Ability: {result[2]}")
    else:
        print("   ERROR: Warlock class not found")

    # 9. Check subclasses
    cursor.execute("SELECT name FROM subclasses WHERE class_id = 'warlock'")
    subclasses = [row[0] for row in cursor.fetchall()]
    print(f"\n9. Warlock subclasses: {', '.join(subclasses)}")

    conn.close()

    print("\n=== Validation Complete ===")

if __name__ == '__main__':
    validate_warlock_database()
