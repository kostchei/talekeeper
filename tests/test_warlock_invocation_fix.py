#!/usr/bin/env python3
"""
Test that level 1 warlocks can see the correct invocations.
Verifies the fix for missing Pact invocations and incorrect prerequisites.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.talekeeper.services.warlock_service import WarlockService


def test_level_1_warlock_invocations():
    """Test that level 1 warlocks can see the correct invocations."""

    print("Testing Level 1 Warlock Invocations...")
    print("=" * 60)

    # Use actual database
    db_path = 'talekeeper.db'

    # Create a test character
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create test warlock character
    test_char_id = 'test_warlock_invocation_check'

    # Clean up any existing test character
    cursor.execute("DELETE FROM characters WHERE id = ?", (test_char_id,))
    cursor.execute("DELETE FROM warlock_features WHERE character_id = ?", (test_char_id,))

    # Create level 1 warlock
    cursor.execute("""
        INSERT INTO characters (id, name, class_id, level, charisma, hit_points_current, hit_points_max)
        VALUES (?, 'Test Warlock', 'warlock', 1, 16, 10, 10)
    """, (test_char_id,))

    conn.commit()

    # Initialize warlock features
    warlock_service = WarlockService(db_path)
    warlock_service.initialize_warlock_features(test_char_id, level=1, patron='Fiend')

    # Get available invocations
    available = warlock_service.invocation_service.get_available_invocations(test_char_id)

    print(f"\nFound {len(available)} available invocations for level 1 warlock:")
    print("-" * 60)

    expected_level_1_invocations = {
        'armor_of_shadows': 'Armor of Shadows',
        'eldritch_mind': 'Eldritch Mind',
        'pact_of_the_blade': 'Pact of the Blade',
        'pact_of_the_chain': 'Pact of the Chain',
        'pact_of_the_tome': 'Pact of the Tome'
    }

    should_not_be_available = {
        'fiendish_vigor': 'Fiendish Vigor (Level 2+ required)'
    }

    available_ids = {inv['id']: inv['name'] for inv in available}

    # Check for expected invocations
    print("\n[+] Checking for EXPECTED level 1 invocations:")
    all_expected_found = True
    for inv_id, inv_name in expected_level_1_invocations.items():
        if inv_id in available_ids:
            print(f"  [OK] {inv_name}")
        else:
            print(f"  [FAIL] MISSING: {inv_name}")
            all_expected_found = False

    # Check that level 2+ invocations are NOT available
    print("\n[+] Checking that level 2+ invocations are NOT available:")
    no_restricted_found = True
    for inv_id, inv_name in should_not_be_available.items():
        if inv_id in available_ids:
            print(f"  [FAIL] INCORRECTLY AVAILABLE: {inv_name}")
            no_restricted_found = False
        else:
            print(f"  [OK] Correctly restricted: {inv_name}")

    # Clean up
    cursor.execute("DELETE FROM characters WHERE id = ?", (test_char_id,))
    cursor.execute("DELETE FROM warlock_features WHERE character_id = ?", (test_char_id,))
    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    if all_expected_found and no_restricted_found:
        print("[PASS] TEST PASSED: All level 1 invocations are correctly available!")
        print("[PASS] Level 2+ invocations are correctly restricted!")
        return True
    else:
        print("[FAIL] TEST FAILED: Some invocations are incorrectly configured!")
        return False


if __name__ == '__main__':
    success = test_level_1_warlock_invocations()
    sys.exit(0 if success else 1)
