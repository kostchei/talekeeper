"""
Test integration of condition system with existing Barbarian features.
This validates Stage 1.1 is complete before moving to Stage 1.2.
"""

import sys
import os
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.condition_manager import ConditionManager, ConditionType, ActiveCondition


def test_condition_system_standalone():
    """Test that condition system works independently."""
    print("Testing standalone condition system...")

    # Create temporary database
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create basic schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    class_id TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id)
                VALUES ('test_barbarian', 'Test Barbarian', 5, 'barbarian')
            """)
            conn.commit()

        # Initialize condition manager
        condition_manager = ConditionManager(test_db_path)
        character_id = 'test_barbarian'

        print("[OK] Condition manager initialized successfully")

        # Test 1: Basic condition application
        frightened = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Dragon Fear",
            duration_type="save_ends",
            save_dc=15,
            save_ability="wisdom"
        )

        result = condition_manager.add_condition(character_id, frightened)
        assert result, "Should be able to add frightened condition"
        print("[OK] Can apply frightened condition")

        # Test 2: Incapacitated detection (key for Danger Sense)
        assert not condition_manager.has_incapacitating_condition(character_id), "Frightened is not incapacitating"
        print("[OK] Frightened correctly not incapacitating")

        # Test 3: Add incapacitating condition
        paralyzed = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )

        condition_manager.add_condition(character_id, paralyzed)
        assert condition_manager.has_incapacitating_condition(character_id), "Paralyzed should be incapacitating"
        print("[OK] Paralyzed correctly incapacitating")

        # Test 4: Condition immunity (for Mindless Rage)
        condition_manager.add_immunity(character_id, ConditionType.FRIGHTENED, "Mindless Rage")

        # Remove existing frightened
        condition_manager.remove_condition(character_id, ConditionType.FRIGHTENED)

        # Try to add frightened again - should fail
        new_frightened = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Banshee Wail",
            duration_type="rounds",
            duration_remaining=3
        )

        result = condition_manager.add_condition(character_id, new_frightened)
        assert not result, "Should not be able to add frightened when immune"
        print("[OK] Condition immunity working")

        # Test 5: Exhaustion stacking
        for i in range(3):
            exhaustion = ActiveCondition(
                condition_type=ConditionType.EXHAUSTION,
                source=f"Source {i}",
                duration_type="permanent",
                exhaustion_level=1
            )
            condition_manager.add_condition(character_id, exhaustion)

        level = condition_manager.get_exhaustion_level(character_id)
        assert level == 3, f"Expected exhaustion level 3, got {level}"
        print("[OK] Exhaustion levels stack correctly")

        # Test 6: Condition summary
        summary = condition_manager.get_condition_summary(character_id)
        print(f"[OK] Condition summary: {summary}")

        print("\n[SUCCESS] All condition system tests passed!")
        return True

    finally:
        # Clean up
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_danger_sense_integration_prep():
    """Test that we're ready for Danger Sense integration."""
    print("\nTesting Danger Sense integration readiness...")

    # This simulates what we'll do in Stage 1.2
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create schema with barbarian
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    class_id TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id)
                VALUES ('barbarian_1', 'Grog', 5, 'barbarian')
            """)
            conn.commit()

        condition_manager = ConditionManager(test_db_path)
        barbarian_id = 'barbarian_1'

        # Function that simulates enhanced Danger Sense check
        def check_danger_sense_enhanced(character_id):
            """Enhanced Danger Sense that checks for incapacitating conditions."""
            # Simulate checking for Danger Sense feature (would be real check)
            has_danger_sense = True  # Level 2+ barbarian

            if not has_danger_sense:
                return False

            # NEW: Check for incapacitating conditions
            if condition_manager.has_incapacitating_condition(character_id):
                return False

            return True

        # Test scenarios
        assert check_danger_sense_enhanced(barbarian_id), "Should have Danger Sense when not incapacitated"

        # Add non-incapacitating condition
        condition_manager.add_condition(barbarian_id, ActiveCondition(
            condition_type=ConditionType.POISONED,
            source="Poison Dart",
            duration_type="hours",
            duration_remaining=1
        ))

        assert check_danger_sense_enhanced(barbarian_id), "Should still have Danger Sense when poisoned"

        # Add incapacitating condition
        condition_manager.add_condition(barbarian_id, ActiveCondition(
            condition_type=ConditionType.STUNNED,
            source="Stunning Strike",
            duration_type="rounds",
            duration_remaining=1
        ))

        assert not check_danger_sense_enhanced(barbarian_id), "Should lose Danger Sense when stunned"

        print("[OK] Danger Sense integration logic working")
        print("[OK] Ready for Stage 1.2 - Danger Sense integration")

        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


if __name__ == '__main__':
    print("=== Stage 1.1 Validation: Condition System Foundation ===")

    success = True

    try:
        success &= test_condition_system_standalone()
        success &= test_danger_sense_integration_prep()

        if success:
            print("\n[SUCCESS] STAGE 1.1 COMPLETE - READY FOR STAGE 1.2")
            print("Condition system is working and ready for integration!")
        else:
            print("\n[FAILED] STAGE 1.1 FAILED")
            exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)