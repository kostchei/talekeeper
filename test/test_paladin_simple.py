# test
"""
Simple Paladin Implementation Test

Tests the current paladin implementation basics without complex setup.
"""

import sys
import os
import sqlite3

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_paladin_class_exists():
    """Test if paladin class is defined in database."""
    try:
        # Use the database from the project root
        db_path = os.path.join(os.path.dirname(__file__), "..", "talekeeper.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE LOWER(name) = 'paladin'")
            paladin_class = cursor.fetchone()

            if paladin_class:
                print(f"PASS: Paladin class found: {paladin_class}")
                return True
            else:
                print("FAIL: Paladin class not found in database")
                return False

    except Exception as e:
        print(f"ERROR: Database error checking paladin class: {e}")
        return False


def test_paladin_service_import():
    """Test paladin service can be imported."""
    try:
        from services.paladin_abilities import PaladinAbilitiesService, get_paladin_service
        # Use the database from the project root
        db_path = os.path.join(os.path.dirname(__file__), "..", "talekeeper.db")
        service = PaladinAbilitiesService(db_path)
        if service:
            print("PASS: Paladin service imported and created")
            return True
        else:
            print("FAIL: Failed to create paladin service")
            return False
    except Exception as e:
        print(f"ERROR: Error importing paladin service: {e}")
        return False


def test_divine_smite_calculation():
    """Test Divine Smite damage calculation without database."""
    try:
        from services.paladin_abilities import PaladinAbilitiesService
        # Use the database from the project root
        db_path = os.path.join(os.path.dirname(__file__), "..", "talekeeper.db")
        service = PaladinAbilitiesService(db_path)

        # Test basic Divine Smite with 1st level slot
        result = service.divine_smite(
            character_id="test",
            spell_slot_level=1,
            target_is_undead_or_fiend=False
        )

        if result.get("success"):
            expected_dice = 2  # 2d8 for 1st level slot
            actual_dice = result.get("damage_dice", 0)

            if actual_dice == expected_dice:
                print(f"PASS: Divine Smite calculation correct: {actual_dice}d8")
                return True
            else:
                print(f"FAIL: Divine Smite incorrect: {actual_dice}d8, expected {expected_dice}d8")
                return False
        else:
            print(f"FAIL: Divine Smite calculation failed: {result}")
            return False

    except Exception as e:
        print(f"ERROR: Error testing Divine Smite: {e}")
        return False


def test_divine_smite_vs_undead():
    """Test Divine Smite bonus damage vs undead/fiends."""
    try:
        from services.paladin_abilities import PaladinAbilitiesService
        # Use the database from the project root
        db_path = os.path.join(os.path.dirname(__file__), "..", "talekeeper.db")
        service = PaladinAbilitiesService(db_path)

        result = service.divine_smite(
            character_id="test",
            spell_slot_level=1,
            target_is_undead_or_fiend=True
        )

        if result.get("success"):
            expected_dice = 3  # 2d8 + 1d8 bonus vs undead/fiends
            actual_dice = result.get("damage_dice", 0)

            if actual_dice == expected_dice:
                print(f"PASS: Divine Smite vs undead correct: {actual_dice}d8")
                return True
            else:
                print(f"FAIL: Divine Smite vs undead incorrect: {actual_dice}d8, expected {expected_dice}d8")
                return False
        else:
            print(f"FAIL: Divine Smite vs undead failed: {result}")
            return False

    except Exception as e:
        print(f"ERROR: Error testing Divine Smite vs undead: {e}")
        return False


def test_paladin_tables_needed():
    """Test what paladin-specific tables exist."""
    try:
        # Use the database from the project root
        db_path = os.path.join(os.path.dirname(__file__), "..", "talekeeper.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check for paladin_features table
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='paladin_features'
            """)
            paladin_table = cursor.fetchone()

            if paladin_table:
                print("PASS: paladin_features table exists")
                return True
            else:
                print("FAIL: paladin_features table missing - this needs to be created")
                return False

    except Exception as e:
        print(f"ERROR: Error checking database tables: {e}")
        return False


def test_action_cards_exist():
    """Test if paladin action card files exist."""
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    action_card_files = [
        os.path.join(project_root, "action_cards", "divine_smite_dialog.py"),
        os.path.join(project_root, "action_cards", "action_panel.py")
    ]

    all_exist = True
    for file_path in action_card_files:
        relative_path = os.path.relpath(file_path, project_root)
        if os.path.exists(file_path):
            print(f"PASS: {relative_path} exists")
        else:
            print(f"FAIL: {relative_path} missing")
            all_exist = False

    return all_exist


def test_divine_smite_dialog():
    """Test if Divine Smite dialog can be imported."""
    try:
        from action_cards.divine_smite_dialog import DivineSmiteDialog
        print("PASS: Divine Smite dialog can be imported")
        return True
    except Exception as e:
        print(f"ERROR: Failed to import Divine Smite dialog: {e}")
        return False


def test_devotion_subclass():
    """Test if Devotion subclass exists."""
    try:
        from services.subclasses.paladin.devotion import DevotionDefinition
        definition = DevotionDefinition.create()
        if definition:
            print(f"PASS: Devotion subclass definition exists")
            print(f"INFO: Devotion features: {len(definition.features)} features")
            return True
        else:
            print("FAIL: Devotion subclass definition failed")
            return False
    except Exception as e:
        print(f"ERROR: Failed to load Devotion subclass: {e}")
        return False


def run_all_tests():
    """Run all simple paladin tests."""
    print("=== SIMPLE PALADIN TEST SUITE ===\n")

    tests = [
        ("Paladin Class Definition", test_paladin_class_exists),
        ("Paladin Service Import", test_paladin_service_import),
        ("Divine Smite Basic", test_divine_smite_calculation),
        ("Divine Smite vs Undead", test_divine_smite_vs_undead),
        ("Paladin Tables", test_paladin_tables_needed),
        ("Action Card Files", test_action_cards_exist),
        ("Divine Smite Dialog", test_divine_smite_dialog),
        ("Devotion Subclass", test_devotion_subclass),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n--- Testing: {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"ERROR: {test_name} - {e}")
            failed += 1

    print(f"\n=== RESULTS ===")
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Success Rate: {(passed / (passed + failed)) * 100:.1f}%")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\nALL TESTS PASSED!")
    else:
        print("\nSOME TESTS FAILED - Check implementation")