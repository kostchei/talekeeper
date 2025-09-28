"""Fix spell slots for existing spellcaster characters."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.spellcasting_service import SpellcastingService
import sqlite3

def fix_all_spellcasters():
    """Initialize spell slots for all spellcaster characters that don't have them."""
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    # Find all spellcaster characters
    cursor.execute("""
        SELECT id, name, class_id, level
        FROM characters
        WHERE class_id IN ('wizard', 'cleric', 'warlock', 'paladin')
    """)

    spellcasters = cursor.fetchall()
    conn.close()

    if not spellcasters:
        print("No spellcaster characters found")
        return

    spellcasting_service = SpellcastingService()

    for char_id, name, class_id, level in spellcasters:
        print(f"\nProcessing {name} (Level {level} {class_id})...")

        # Check if they already have spell slots
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM character_spell_slots WHERE character_id = ?", (char_id,))
        slot_count = cursor.fetchone()[0]
        conn.close()

        if slot_count > 0:
            print(f"  Already has {slot_count} spell slot entries - skipping")
        else:
            print(f"  No spell slots found - initializing...")
            spellcasting_service.initialize_character_spellcasting(char_id, class_id)
            print(f"  Spell slots initialized!")

if __name__ == "__main__":
    fix_all_spellcasters()
    print("\nDone!")