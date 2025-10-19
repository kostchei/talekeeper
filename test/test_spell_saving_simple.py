# test
import sys
import sqlite3
sys.path.insert(0, '..')

def test_spell_table_structure():
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='character_spells'")
    result = cursor.fetchone()

    assert result is not None, "character_spells table should exist"
    print("[OK] character_spells table exists")

    cursor.execute("PRAGMA table_info(character_spells)")
    columns = {row[1] for row in cursor.fetchall()}

    required_columns = {'character_id', 'spell_id', 'spell_level', 'is_prepared', 'source', 'source_level', 'always_prepared'}
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    print(f"[OK] character_spells table has all required columns")

    conn.close()

def test_spell_data_available():
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM spells WHERE level = 0")
    cantrip_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM spells WHERE level = 1")
    spell_count = cursor.fetchone()[0]

    assert cantrip_count >= 20, f"Expected at least 20 cantrips, got {cantrip_count}"
    assert spell_count >= 40, f"Expected at least 40 level-1 spells, got {spell_count}"

    print(f"[OK] Spell data available: {cantrip_count} cantrips, {spell_count} level-1 spells")

    conn.close()

def test_spell_saving_logic_exists():
    import inspect
    from core.game_engine_sqlite import GameEngineSQLite

    source = inspect.getsource(GameEngineSQLite.create_new_character_sync)

    assert 'selected_cantrips' in source, "create_new_character_sync should handle selected_cantrips"
    assert 'selected_spells' in source, "create_new_character_sync should handle selected_spells"
    assert 'character_spells' in source, "create_new_character_sync should insert into character_spells"

    print("[OK] Spell saving logic is present in create_new_character_sync")

def test_existing_character_spell_data():
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.name, c.class_id, COUNT(cs.spell_id) as spell_count
        FROM characters c
        LEFT JOIN character_spells cs ON c.id = cs.character_id
        WHERE c.class_id IN ('wizard', 'cleric', 'warlock', 'paladin')
        GROUP BY c.id, c.name, c.class_id
        LIMIT 5
    """)

    characters = cursor.fetchall()

    if characters:
        print("[INFO] Spell data for existing spellcaster characters:")
        for name, class_id, spell_count in characters:
            print(f"  - {name} ({class_id}): {spell_count} spells")
    else:
        print("[INFO] No existing spellcaster characters found to check")

    conn.close()

def main():
    print("=" * 60)
    print("SPELL SAVING LOGIC VERIFICATION")
    print("=" * 60)

    try:
        print("\n[1/5] Testing character_spells table structure...")
        test_spell_table_structure()

        print("\n[2/5] Testing spell data availability...")
        test_spell_data_available()

        print("\n[3/5] Testing spell saving logic in code...")
        test_spell_saving_logic_exists()

        print("\n[4/5] Checking existing character spell data...")
        test_existing_character_spell_data()

        print("\n[5/5] Verifying spell selection widget integration...")
        from encounter_pane.encounter_panel import EncounterPanel
        import inspect
        source = inspect.getsource(EncounterPanel._setup_spell_selection)
        assert 'SpellSelectionWidget' in source, "EncounterPanel should use SpellSelectionWidget"
        print("[OK] Spell selection widget is integrated into character creation")

        print("\n" + "=" * 60)
        print("[PASS] ALL VERIFICATION TESTS PASSED!")
        print("=" * 60)
        print("\nSpell selection system is properly implemented.")
        print("\nTo test character creation with spells:")
        print("  1. Run: python main.py")
        print("  2. Create a new Wizard/Warlock/Cleric/Paladin character")
        print("  3. You should see spell selection UI in the Class Features step")
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())