#!/usr/bin/env python3
# test
"""
Test script to verify Rogue subclass selection is working properly.
"""

import sqlite3
from services.subclass_manager import SubclassManager
from services.level_up import LevelUpService

def test_rogue_subclass_selection():
    """Test that level 3 rogues can choose between Thief and Assassin subclasses."""

    print("=== Testing Rogue Subclass Selection ===\n")

    # Test 1: Check available subclasses for rogue
    subclass_manager = SubclassManager()
    available_subclasses = subclass_manager.get_available_subclasses('rogue')

    print("Available Rogue Subclasses:")
    for subclass in available_subclasses:
        print(f"  - {subclass['name']}: {subclass['description']}")
        print(f"    Selection Level: {subclass['selection_level']}")
    print()

    # Test 2: Verify Thief and Assassin are both available
    subclass_names = [sc['name'] for sc in available_subclasses]

    if 'Thief' in subclass_names:
        print("✅ Thief subclass is available")
    else:
        print("❌ Thief subclass is missing")

    if 'Assassin' in subclass_names:
        print("✅ Assassin subclass is available")
    else:
        print("❌ Assassin subclass is missing")

    # Test 3: Check selection level requirement
    selection_levels = [sc['selection_level'] for sc in available_subclasses if sc['name'] in ['Thief', 'Assassin']]
    if all(level == 3 for level in selection_levels):
        print("✅ Both subclasses require level 3 selection")
    else:
        print(f"❌ Selection levels mismatch: {selection_levels}")

    print()

    # Test 4: Check subclass features exist
    print("Checking Subclass Features:")

    with sqlite3.connect('talekeeper.db') as conn:
        cursor = conn.cursor()

        # Check Thief features
        cursor.execute("SELECT COUNT(*) FROM subclass_features WHERE subclass_id = 'thief'")
        thief_features = cursor.fetchone()[0]
        print(f"  - Thief features: {thief_features} (expected: 5)")

        # Check Assassin features
        cursor.execute("SELECT COUNT(*) FROM subclass_features WHERE subclass_id = 'assassin'")
        assassin_features = cursor.fetchone()[0]
        print(f"  - Assassin features: {assassin_features} (expected: 5)")

    print()
    print("=== Summary ===")
    print("When a Rogue reaches level 3, they should see a subclass selection UI")
    print("with both Thief and Assassin options available.")
    print("The selection is made in the Town encounter level-up interface.")

if __name__ == "__main__":
    test_rogue_subclass_selection()