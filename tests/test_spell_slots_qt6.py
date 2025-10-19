#test
"""
TESTING FRAMEWORK - Qt6 test to diagnose spell slot issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from ui.main_window import MainWindow


def test_spell_slots():
    """Test spell slot availability."""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    QTest.qWait(2000)

    print("\n=== SPELL SLOT DIAGNOSTIC ===")

    action_panel = window.action_panel

    if action_panel and hasattr(action_panel, 'character_context'):
        char_id = action_panel.character_context.get('id')
        char_class = action_panel.character_context.get('class_id')
        char_level = action_panel.character_context.get('level', 1)
        print(f"Character: {char_id}")
        print(f"Class: {char_class}, Level: {char_level}")

        # Get spell slots
        spellcasting_service = action_panel._get_spellcasting_service()
        if spellcasting_service:
            spell_slots = spellcasting_service.get_character_spell_slots(char_id)
            print(f"\nSpell Slots:")
            for slot in spell_slots:
                print(f"  Level {slot.level}: {slot.available_slots}/{slot.max_slots} available")

        # Get spells
        spells = action_panel._get_character_castable_spells(char_id)
        print(f"\nCastable Spells: {len(spells)}")
        for spell in spells:
            print(f"  - {spell['name']} (Level {spell['spell_level']})")

        # Check database directly
        import sqlite3
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        print(f"\nDatabase Check:")
        cursor.execute("""
            SELECT s.name, s.level, cs.is_prepared
            FROM character_spells cs
            JOIN spells s ON cs.spell_id = s.id
            WHERE cs.character_id = ?
            ORDER BY s.level, s.name
        """, (char_id,))

        for name, level, is_prepared in cursor.fetchall():
            prepared = "PREPARED" if is_prepared else "not prepared"
            print(f"  - {name} (Level {level}, {prepared})")

        conn.close()


if __name__ == "__main__":
    test_spell_slots()
    sys.exit(0)