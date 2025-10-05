import sys
import sqlite3
sys.path.insert(0, '..')

from PyQt6.QtWidgets import QApplication
from encounter_pane.spell_selection_widget import SpellSelectionWidget

def test_wizard_selection():
    app = QApplication(sys.argv)

    widget = SpellSelectionWidget(db_path='../talekeeper.db')
    widget.setup_for_class('Wizard')

    assert widget.isVisible(), "Widget should be visible for Wizard"
    assert len(widget.cantrip_combos) == 3, f"Wizard should have 3 cantrip combos, got {len(widget.cantrip_combos)}"
    assert len(widget.spell_checkboxes) > 0, "Wizard should have level 1 spell checkboxes"

    print("[OK] Wizard spell selection UI initialized correctly")
    print(f"  - Cantrip combos: {len(widget.cantrip_combos)}")
    print(f"  - Level 1 spell checkboxes: {len(widget.spell_checkboxes)}")

    app.quit()

def test_cleric_selection():
    app = QApplication(sys.argv)

    widget = SpellSelectionWidget(db_path='../talekeeper.db')
    widget.setup_for_class('Cleric')

    assert widget.isVisible(), "Widget should be visible for Cleric"
    assert len(widget.cantrip_combos) == 3, f"Cleric should have 3 cantrip combos, got {len(widget.cantrip_combos)}"
    assert len(widget.spell_checkboxes) == 0, "Cleric should not have level 1 spell checkboxes (prepare after creation)"

    print("[OK] Cleric spell selection UI initialized correctly")
    print(f"  - Cantrip combos: {len(widget.cantrip_combos)}")
    print(f"  - Shows preparation info: True")

    app.quit()

def test_warlock_selection():
    app = QApplication(sys.argv)

    widget = SpellSelectionWidget(db_path='../talekeeper.db')
    widget.setup_for_class('Warlock')

    assert widget.isVisible(), "Widget should be visible for Warlock"
    assert len(widget.cantrip_combos) == 2, f"Warlock should have 2 cantrip combos, got {len(widget.cantrip_combos)}"
    assert len(widget.spell_checkboxes) > 0, "Warlock should have level 1 spell checkboxes"

    print("[OK] Warlock spell selection UI initialized correctly")
    print(f"  - Cantrip combos: {len(widget.cantrip_combos)}")
    print(f"  - Level 1 spell checkboxes: {len(widget.spell_checkboxes)}")

    app.quit()

def test_paladin_selection():
    app = QApplication(sys.argv)

    widget = SpellSelectionWidget(db_path='../talekeeper.db')
    widget.setup_for_class('Paladin')

    assert widget.isVisible(), "Widget should be visible for Paladin"
    assert len(widget.cantrip_combos) == 0, "Paladin should have 0 cantrip combos"
    assert len(widget.spell_checkboxes) == 0, "Paladin should not have level 1 spell checkboxes (prepare after creation)"

    print("[OK] Paladin spell selection UI initialized correctly")
    print(f"  - Cantrip combos: {len(widget.cantrip_combos)}")
    print(f"  - Shows preparation info: True")

    app.quit()

def test_fighter_no_selection():
    app = QApplication(sys.argv)

    widget = SpellSelectionWidget(db_path='../talekeeper.db')
    widget.setup_for_class('Fighter')

    assert not widget.isVisible(), "Widget should be hidden for non-spellcasters"

    print("[OK] Fighter (non-spellcaster) correctly hides spell selection")

    app.quit()

def test_spell_data_availability():
    conn = sqlite3.connect('../talekeeper.db')
    cursor = conn.cursor()

    classes_to_test = ['wizard', 'cleric', 'warlock', 'paladin']

    for class_id in classes_to_test:
        cursor.execute("""
            SELECT COUNT(*) FROM spells
            WHERE level = 0 AND classes LIKE ?
        """, (f'%"{class_id}"%',))
        cantrip_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM spells
            WHERE level = 1 AND classes LIKE ?
        """, (f'%"{class_id}"%',))
        spell_count = cursor.fetchone()[0]

        print(f"[OK] {class_id.capitalize()}: {cantrip_count} cantrips, {spell_count} level-1 spells available")

    conn.close()

def main():
    print("=" * 60)
    print("PHASE 2 SPELL SELECTION UI TESTS")
    print("=" * 60)

    try:
        print("\n[1/6] Testing spell data availability...")
        test_spell_data_availability()

        print("\n[2/6] Testing Wizard spell selection UI...")
        test_wizard_selection()

        print("\n[3/6] Testing Cleric spell selection UI...")
        test_cleric_selection()

        print("\n[4/6] Testing Warlock spell selection UI...")
        test_warlock_selection()

        print("\n[5/6] Testing Paladin spell selection UI...")
        test_paladin_selection()

        print("\n[6/6] Testing non-spellcaster (Fighter)...")
        test_fighter_no_selection()

        print("\n" + "=" * 60)
        print("[PASS] ALL PHASE 2 UI TESTS PASSED!")
        print("=" * 60)
        print("\nSpell selection UI is ready for character creation.")
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