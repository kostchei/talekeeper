#test
"""
Quick test to verify Galahad can use Divine Smite
"""

import sys
import os
import sqlite3

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from services.spellcasting_service import get_spellcasting_service

def test_galahad_smite():
    galahad_id = '3c17a911-88d7-422d-8999-949074b7f2ca'

    print("=== Testing Galahad's Divine Smite Availability ===")

    # Check database spell slots
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT spell_level, max_slots, used_slots
        FROM character_spell_slots
        WHERE character_id = ?
    ''', (galahad_id,))

    db_slots = cursor.fetchall()
    print(f"Database spell slots: {db_slots}")

    # Test spellcasting service
    spellcasting_service = get_spellcasting_service("talekeeper.db")
    service_slots = spellcasting_service.get_character_spell_slots(galahad_id)

    print(f"Service spell slots: {[(s.level, s.max_slots, s.used_slots, s.available_slots) for s in service_slots]}")

    # Check if smite would work
    available_slots = {}
    for slot in service_slots:
        if slot.available_slots > 0 and slot.level <= 5:
            available_slots[slot.level] = slot.available_slots

    print(f"Available slots for Divine Smite: {available_slots}")

    if available_slots:
        print("✅ SUCCESS: Galahad can use Divine Smite!")
        print("The issue is likely that the UI needs refreshing or the character context needs updating.")
        print("\nTry:")
        print("1. Restart the application")
        print("2. Or refresh the character (if there's a refresh button)")
        print("3. Or start a new encounter to reload the character data")
    else:
        print("❌ ISSUE: No available spell slots for Divine Smite")

    conn.close()

if __name__ == "__main__":
    test_galahad_smite()