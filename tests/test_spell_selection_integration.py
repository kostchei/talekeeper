import sys
import sqlite3
import uuid
sys.path.insert(0, '..')

from core.game_engine_sqlite import GameEngineSQLite

def test_wizard_character_creation_with_spells():
    engine = GameEngineSQLite('talekeeper.db')

    character_id = str(uuid.uuid4())

    character_data = {
        'name': 'Test Wizard',
        'class_id': 'wizard',
        'race_id': 'human',
        'background_id': 'sage',
        'level': 1,
        'experience_points': 0,
        'strength': 10,
        'dexterity': 14,
        'constitution': 12,
        'intelligence': 16,
        'wisdom': 13,
        'charisma': 8,
        'hit_points_max': 8,
        'hit_points_current': 8,
        'selected_cantrips': ['fire_bolt', 'mage_hand', 'prestidigitation'],
        'selected_spells': ['shield', 'mage_armor', 'magic_missile', 'detect_magic', 'identify', 'find_familiar'],
        'selected_class_skills': ['Arcana', 'History'],
        'feats': []
    }

    try:
        character = engine.create_new_character_sync(character_data, save_slot=8)

        conn = sqlite3.connect('../talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM character_spells
            WHERE character_id = ? AND spell_level = 0
        """, (character['id'],))
        cantrip_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM character_spells
            WHERE character_id = ? AND spell_level = 1
        """, (character['id'],))
        spell_count = cursor.fetchone()[0]

        assert cantrip_count == 3, f"Expected 3 cantrips, got {cantrip_count}"
        assert spell_count == 6, f"Expected 6 level-1 spells, got {spell_count}"

        cursor.execute("""
            SELECT spell_id, is_prepared FROM character_spells
            WHERE character_id = ? AND spell_level = 0
            ORDER BY spell_id
        """, (character['id'],))
        cantrips = cursor.fetchall()

        print(f"[OK] Wizard character created with {cantrip_count} cantrips and {spell_count} spells")
        print("  Cantrips:")
        for spell_id, is_prepared in cantrips:
            print(f"    - {spell_id} (prepared: {bool(is_prepared)})")

        cursor.execute("""
            SELECT spell_id, is_prepared FROM character_spells
            WHERE character_id = ? AND spell_level = 1
            ORDER BY spell_id
        """, (character['id'],))
        spells = cursor.fetchall()

        print("  Level 1 Spells:")
        for spell_id, is_prepared in spells[:3]:
            print(f"    - {spell_id} (prepared: {bool(is_prepared)})")
        if len(spells) > 3:
            print(f"    ... and {len(spells) - 3} more")

        engine.delete_character_sync(8)
        print("[OK] Test character cleaned up")

        conn.close()

    except Exception as e:
        print(f"[FAIL] Error creating wizard: {e}")
        import traceback
        traceback.print_exc()
        engine.delete_character_sync(8)
        raise

def test_warlock_character_creation_with_spells():
    engine = GameEngineSQLite('talekeeper.db')

    character_data = {
        'name': 'Test Warlock',
        'class_id': 'warlock',
        'race_id': 'human',
        'background_id': 'charlatan',
        'level': 1,
        'experience_points': 0,
        'strength': 8,
        'dexterity': 14,
        'constitution': 13,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 16,
        'hit_points_max': 10,
        'hit_points_current': 10,
        'selected_cantrips': ['eldritch_blast', 'chill_touch'],
        'selected_spells': ['hex', 'hellish_rebuke'],
        'selected_class_skills': ['Deception', 'Intimidation'],
        'feats': []
    }

    try:
        character = engine.create_new_character_sync(character_data, save_slot=9)

        conn = sqlite3.connect('../talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM character_spells
            WHERE character_id = ? AND spell_level = 0
        """, (character['id'],))
        cantrip_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM character_spells
            WHERE character_id = ? AND spell_level = 1
        """, (character['id'],))
        spell_count = cursor.fetchone()[0]

        assert cantrip_count == 2, f"Expected 2 cantrips, got {cantrip_count}"
        assert spell_count == 2, f"Expected 2 level-1 spells, got {spell_count}"

        print(f"[OK] Warlock character created with {cantrip_count} cantrips and {spell_count} spells")

        engine.delete_character_sync(9)
        print("[OK] Test character cleaned up")

        conn.close()

    except Exception as e:
        print(f"[FAIL] Error creating warlock: {e}")
        import traceback
        traceback.print_exc()
        engine.delete_character_sync(9)
        raise

def test_cleric_character_creation_no_spells():
    engine = GameEngineSQLite('talekeeper.db')

    character_data = {
        'name': 'Test Cleric',
        'class_id': 'cleric',
        'race_id': 'dwarf',
        'background_id': 'acolyte',
        'level': 1,
        'experience_points': 0,
        'strength': 14,
        'dexterity': 10,
        'constitution': 13,
        'intelligence': 8,
        'wisdom': 16,
        'charisma': 12,
        'hit_points_max': 10,
        'hit_points_current': 10,
        'selected_cantrips': ['sacred_flame', 'spare_the_dying', 'thaumaturgy'],
        'selected_spells': [],
        'selected_class_skills': ['Insight', 'Religion'],
        'feats': []
    }

    try:
        character = engine.create_new_character_sync(character_data, save_slot=10)

        conn = sqlite3.connect('../talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM character_spells
            WHERE character_id = ? AND spell_level = 0
        """, (character['id'],))
        cantrip_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM character_spells
            WHERE character_id = ? AND spell_level = 1
        """, (character['id'],))
        spell_count = cursor.fetchone()[0]

        assert cantrip_count == 3, f"Expected 3 cantrips, got {cantrip_count}"
        assert spell_count == 0, f"Expected 0 level-1 spells (prepares later), got {spell_count}"

        print(f"[OK] Cleric character created with {cantrip_count} cantrips (prepares spells separately)")

        engine.delete_character_sync(10)
        print("[OK] Test character cleaned up")

        conn.close()

    except Exception as e:
        print(f"[FAIL] Error creating cleric: {e}")
        import traceback
        traceback.print_exc()
        engine.delete_character_sync(10)
        raise

def main():
    print("=" * 60)
    print("SPELL SELECTION INTEGRATION TESTS")
    print("=" * 60)

    try:
        print("\n[1/3] Testing Wizard character creation with spell selection...")
        test_wizard_character_creation_with_spells()

        print("\n[2/3] Testing Warlock character creation with spell selection...")
        test_warlock_character_creation_with_spells()

        print("\n[3/3] Testing Cleric character creation with cantrips only...")
        test_cleric_character_creation_no_spells()

        print("\n" + "=" * 60)
        print("[PASS] ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\nSpell selection is fully integrated into character creation.")
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())