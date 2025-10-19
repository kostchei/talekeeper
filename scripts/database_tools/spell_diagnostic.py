# core
#utility
# core
"""
TESTING FRAMEWORK - Simple spell diagnostic script
====================================================

Quick diagnostic to check spell action card issue without UI.
"""

import sqlite3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_character_spells():
    """Check what spells characters have in the database."""
    try:
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        print("=== CHARACTER SPELL DIAGNOSTIC ===")

        # Check all characters and their spells
        cursor.execute("""
            SELECT c.id, c.name, c.class_id, cs.spell_id, s.name as spell_name, cs.is_prepared
            FROM characters c
            LEFT JOIN character_spells cs ON c.id = cs.character_id
            LEFT JOIN spells s ON cs.spell_id = s.id
            WHERE c.class_id IN ('wizard', 'cleric', 'warlock', 'paladin')
            ORDER BY c.name, s.level, s.name
        """)

        results = cursor.fetchall()

        current_char = None
        char_spell_count = {}

        for row in results:
            char_id, char_name, class_id, spell_id, spell_name, is_prepared = row

            if char_name != current_char:
                if current_char is not None:
                    print()
                current_char = char_name
                char_spell_count[char_name] = 0
                print(f"Character: {char_name} ({class_id}) - ID: {char_id}")

            if spell_name:
                char_spell_count[char_name] += 1
                prepared_text = "PREPARED" if is_prepared else "not prepared"
                print(f"  - {spell_name} ({prepared_text})")
            else:
                print(f"  - NO SPELLS FOUND")

        print(f"\n=== SUMMARY ===")
        for char_name, count in char_spell_count.items():
            print(f"{char_name}: {count} spells")

        # Check specifically for Nathlas
        print(f"\n=== NATHLAS DETAILS ===")
        cursor.execute("""
            SELECT cs.spell_id, s.name, s.level, cs.is_prepared, cs.is_cantrip
            FROM characters c
            JOIN character_spells cs ON c.id = cs.character_id
            JOIN spells s ON cs.spell_id = s.id
            WHERE c.name = 'Nathlas'
            ORDER BY s.level, s.name
        """)

        nathlas_spells = cursor.fetchall()
        if nathlas_spells:
            print("Nathlas's spells:")
            for spell_id, spell_name, level, is_prepared, is_cantrip in nathlas_spells:
                spell_type = "Cantrip" if is_cantrip else f"Level {level}"
                prepared_text = "PREPARED" if is_prepared else "not prepared"
                print(f"  - {spell_name} ({spell_type}, {prepared_text})")
        else:
            print("Nathlas has NO SPELLS in character_spells table!")

        conn.close()

    except Exception as e:
        print(f"Error checking database: {e}")


def check_spells_table():
    """Check what spells exist in the spells table."""
    try:
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        print(f"\n=== SPELLS TABLE CHECK ===")

        # Check for Fire Bolt and Magic Missile specifically
        target_spells = ['fire_bolt', 'magic_missile']

        for spell_id in target_spells:
            cursor.execute("SELECT id, name, level FROM spells WHERE id = ?", (spell_id,))
            result = cursor.fetchone()
            if result:
                print(f"{spell_id}: Found - {result[1]} (Level {result[2]})")
            else:
                print(f"{spell_id}: NOT FOUND")

        conn.close()

    except Exception as e:
        print(f"Error checking spells table: {e}")


def simulate_action_panel_spell_query():
    """Simulate what the action panel does to get spells."""
    try:
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        print(f"\n=== ACTION PANEL SIMULATION ===")

        # Find Nathlas
        cursor.execute("SELECT id FROM characters WHERE name = 'Nathlas'")
        result = cursor.fetchone()

        if not result:
            print("Nathlas character not found!")
            return

        character_id = result[0]
        print(f"Nathlas ID: {character_id}")

        # This is what action_panel.py does to get spells (FIXED VERSION)
        cursor.execute("""
            SELECT cs.spell_id, s.level as spell_level, cs.is_prepared, cs.always_prepared,
                   s.name, s.school, s.casting_time, s.range_value, s.components,
                   s.duration, s.concentration, s.description
            FROM character_spells cs
            JOIN spells s ON cs.spell_id = s.id
            WHERE cs.character_id = ?
            AND (cs.is_prepared = 1 OR s.level = 0 OR cs.always_prepared = 1)
            ORDER BY s.level, s.name
        """, (character_id,))

        spells = cursor.fetchall()

        print(f"Action panel would find {len(spells)} castable spells:")
        for spell in spells:
            spell_id, spell_level, is_prepared, always_prepared, name, school, casting_time, range_val, components, duration, concentration, description = spell
            spell_type = "Cantrip" if spell_level == 0 else f"Level {spell_level}"
            prepared_text = "ALWAYS" if always_prepared else "PREPARED" if is_prepared else "not prepared"
            print(f"  - {name} ({spell_type}, {prepared_text})")

        conn.close()

    except Exception as e:
        print(f"Error simulating action panel: {e}")


if __name__ == "__main__":
    check_spells_table()
    check_character_spells()
    simulate_action_panel_spell_query()