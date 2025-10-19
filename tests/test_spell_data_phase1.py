#test
"""
Phase 1 Spell Data Validation Tests
Tests that essential spells for character creation are present in the database
"""

import sqlite3
import sys

def test_cantrip_counts():
    """Test that all classes have sufficient cantrips for character creation"""
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    # Wizard needs 15+ cantrips (choose 3 from 15+)
    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=0 AND classes LIKE '%wizard%'")
    wizard_cantrips = cursor.fetchone()[0]
    assert wizard_cantrips >= 14, f"Wizard has only {wizard_cantrips} cantrips, needs 14+"
    print(f"[OK] Wizard cantrips: {wizard_cantrips}/14+")

    # Warlock needs 7+ cantrips (choose 2 from 7+)
    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=0 AND classes LIKE '%warlock%'")
    warlock_cantrips = cursor.fetchone()[0]
    assert warlock_cantrips >= 7, f"Warlock has only {warlock_cantrips} cantrips, needs 7+"
    print(f"[OK] Warlock cantrips: {warlock_cantrips}/7+")

    # Cleric needs 7+ cantrips (choose 3 from 7+)
    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=0 AND classes LIKE '%cleric%'")
    cleric_cantrips = cursor.fetchone()[0]
    assert cleric_cantrips >= 7, f"Cleric has only {cleric_cantrips} cantrips, needs 7+"
    print(f"[OK] Cleric cantrips: {cleric_cantrips}/7+")

    conn.close()

def test_level1_spell_counts():
    """Test that all classes have sufficient level 1 spells"""
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    # Wizard needs 20+ level-1 spells (choose 6 for spellbook)
    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=1 AND classes LIKE '%wizard%'")
    wizard_l1 = cursor.fetchone()[0]
    assert wizard_l1 >= 20, f"Wizard has only {wizard_l1} level-1 spells, needs 20+"
    print(f"[OK] Wizard level-1 spells: {wizard_l1}/20+")

    # Cleric needs 13+ level-1 spells (choose 4-5 to prepare)
    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=1 AND classes LIKE '%cleric%'")
    cleric_l1 = cursor.fetchone()[0]
    assert cleric_l1 >= 13, f"Cleric has only {cleric_l1} level-1 spells, needs 13+"
    print(f"[OK] Cleric level-1 spells: {cleric_l1}/13+")

    # Warlock needs 10+ level-1 spells (choose 2 known)
    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=1 AND classes LIKE '%warlock%'")
    warlock_l1 = cursor.fetchone()[0]
    assert warlock_l1 >= 10, f"Warlock has only {warlock_l1} level-1 spells, needs 10+"
    print(f"[OK] Warlock level-1 spells: {warlock_l1}/10+")

    # Paladin needs 12+ level-1 spells (choose 2 to prepare)
    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=1 AND classes LIKE '%paladin%'")
    paladin_l1 = cursor.fetchone()[0]
    assert paladin_l1 >= 12, f"Paladin has only {paladin_l1} level-1 spells, needs 12+"
    print(f"[OK] Paladin level-1 spells: {paladin_l1}/12+")

    conn.close()

def test_essential_spells():
    """Test that critical spells exist for each class"""
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    essential_spells = {
        'eldritch_blast': 'Warlock signature damage cantrip',
        'fire_bolt': 'Wizard damage cantrip',
        'sacred_flame': 'Cleric damage cantrip',
        'shield': 'Wizard defensive reaction',
        'mage_armor': 'Wizard AC spell',
        'hex': 'Warlock signature spell',
        'hellish_rebuke': 'Warlock reaction spell',
        'cure_wounds': 'Healing spell',
        'healing_word': 'Bonus action healing',
        'guiding_bolt': 'Cleric damage spell',
        'bless': 'Support spell',
        'heroism': 'Paladin recommended spell',
        'searing_smite': 'Paladin recommended spell',
    }

    for spell_id, description in essential_spells.items():
        cursor.execute("SELECT name FROM spells WHERE id = ?", (spell_id,))
        result = cursor.fetchone()
        assert result is not None, f"Missing essential spell: {spell_id} ({description})"
        print(f"[OK] {result[0]} present ({description})")

    conn.close()

def test_total_spell_count():
    """Test overall spell counts"""
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=0")
    cantrip_count = cursor.fetchone()[0]
    assert cantrip_count >= 20, f"Only {cantrip_count} cantrips, need 20+"
    print(f"[OK] Total cantrips: {cantrip_count}/20+")

    cursor.execute("SELECT COUNT(*) FROM spells WHERE level=1")
    level1_count = cursor.fetchone()[0]
    assert level1_count >= 40, f"Only {level1_count} level-1 spells, need 40+"
    print(f"[OK] Total level-1 spells: {level1_count}/40+")

    conn.close()

def main():
    print("=" * 60)
    print("PHASE 1 SPELL DATA VALIDATION")
    print("=" * 60)

    try:
        print("\n[1/4] Testing cantrip availability by class...")
        test_cantrip_counts()

        print("\n[2/4] Testing level-1 spell availability by class...")
        test_level1_spell_counts()

        print("\n[3/4] Testing essential spells...")
        test_essential_spells()

        print("\n[4/4] Testing total spell counts...")
        test_total_spell_count()

        print("\n" + "=" * 60)
        print("[PASS] ALL PHASE 1 TESTS PASSED!")
        print("=" * 60)
        print("\nDatabase is ready for character creation spell selection.")
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        print("\nPlease review the spell seed files and re-run.")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())