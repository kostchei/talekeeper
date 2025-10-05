"""
Test Danger Sense integration with condition system.
Stage 1.2 validation test.
"""

import sys
import os
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.barbarian_abilities import BarbarianAbilitiesService
from services.condition_manager import ConditionManager, ConditionType, ActiveCondition


def test_danger_sense_integration():
    """Test that enhanced Danger Sense works with condition system."""
    print("Testing Danger Sense integration with condition system...")

    # Create temporary database
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema with Barbarian
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()

            # Create basic tables
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    class_id TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER,
                    danger_sense_active BOOLEAN DEFAULT 1,
                    reckless_attack_available BOOLEAN DEFAULT 1,
                    rage_uses_max INTEGER DEFAULT 2,
                    rage_uses_current INTEGER DEFAULT 2,
                    rage_damage_bonus INTEGER DEFAULT 2,
                    fast_movement_active BOOLEAN DEFAULT 0,
                    brutal_strike_uses_max INTEGER DEFAULT 0,
                    brutal_strike_uses_current INTEGER DEFAULT 0,
                    brutal_strike_effects TEXT DEFAULT '',
                    feral_instinct_active BOOLEAN DEFAULT 0,
                    instinctive_pounce_available BOOLEAN DEFAULT 0,
                    relentless_rage_uses_current INTEGER DEFAULT 0,
                    persistent_rage_active BOOLEAN DEFAULT 0,
                    indomitable_might_active BOOLEAN DEFAULT 0,
                    primal_champion_active BOOLEAN DEFAULT 0,
                    intimidating_presence_uses_max INTEGER DEFAULT 0,
                    intimidating_presence_uses_current INTEGER DEFAULT 0,
                    weapon_mastery_count INTEGER DEFAULT 0,
                    extra_attacks INTEGER DEFAULT 0,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)

            # Insert test barbarian
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id)
                VALUES ('barbarian_test', 'Grog', 5, 'barbarian')
            """)

            cursor.execute("""
                INSERT INTO barbarian_features (character_id, level, danger_sense_active)
                VALUES ('barbarian_test', 5, 1)
            """)

            conn.commit()

        # Initialize services
        barbarian_abilities = BarbarianAbilitiesService(test_db_path)
        condition_manager = ConditionManager(test_db_path)
        character_id = 'barbarian_test'

        # Test 1: Original function still works
        original_result = barbarian_abilities.has_danger_sense_advantage(character_id, 'dexterity')
        assert original_result, "Original Danger Sense function should work"
        print("[OK] Original Danger Sense function still works")

        # Test 2: Enhanced function works when no conditions
        enhanced_result = barbarian_abilities.has_danger_sense_advantage_enhanced(character_id, 'dexterity')
        assert enhanced_result, "Enhanced Danger Sense should work when no conditions"
        print("[OK] Enhanced Danger Sense works with no conditions")

        # Test 3: Enhanced function blocked by incapacitating condition
        paralyzed = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )
        condition_manager.add_condition(character_id, paralyzed)

        enhanced_result_blocked = barbarian_abilities.has_danger_sense_advantage_enhanced(character_id, 'dexterity')
        assert not enhanced_result_blocked, "Enhanced Danger Sense should be blocked when paralyzed"
        print("[OK] Enhanced Danger Sense correctly blocked by paralyzed condition")

        # Test 4: Enhanced function works with non-incapacitating condition
        condition_manager.remove_condition(character_id, ConditionType.PARALYZED)

        poisoned = ActiveCondition(
            condition_type=ConditionType.POISONED,
            source="Poison Dart",
            duration_type="hours",
            duration_remaining=1
        )
        condition_manager.add_condition(character_id, poisoned)

        enhanced_result_poisoned = barbarian_abilities.has_danger_sense_advantage_enhanced(character_id, 'dexterity')
        assert enhanced_result_poisoned, "Enhanced Danger Sense should work when only poisoned"
        print("[OK] Enhanced Danger Sense works when poisoned (non-incapacitating)")

        # Test 5: Doesn't work for non-dexterity saves
        enhanced_result_str = barbarian_abilities.has_danger_sense_advantage_enhanced(character_id, 'strength')
        assert not enhanced_result_str, "Danger Sense should only work on Dexterity saves"
        print("[OK] Enhanced Danger Sense correctly limited to Dexterity saves")

        # Test 6: Doesn't work for low-level barbarian
        cursor.execute("UPDATE barbarian_features SET level = 1 WHERE character_id = ?", (character_id,))
        conn.commit()

        enhanced_result_low_level = barbarian_abilities.has_danger_sense_advantage_enhanced(character_id, 'dexterity')
        assert not enhanced_result_low_level, "Danger Sense should require level 2+"
        print("[OK] Enhanced Danger Sense correctly requires level 2+")

        print("\n[SUCCESS] All Danger Sense integration tests passed!")
        return True

    finally:
        # Clean up
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_backwards_compatibility():
    """Test that existing code still works unchanged."""
    print("\nTesting backwards compatibility...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create minimal schema
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
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER,
                    danger_sense_active BOOLEAN DEFAULT 1
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id)
                VALUES ('barbarian_legacy', 'Legacy Barbarian', 3, 'barbarian')
            """)
            cursor.execute("""
                INSERT INTO barbarian_features (character_id, level, danger_sense_active)
                VALUES ('barbarian_legacy', 3, 1)
            """)
            conn.commit()

        barbarian_abilities = BarbarianAbilitiesService(test_db_path)
        character_id = 'barbarian_legacy'

        # Test original function with conditions parameter (existing usage)
        result_no_conditions = barbarian_abilities.has_danger_sense_advantage(character_id, 'dexterity', [])
        assert result_no_conditions, "Should work with empty conditions list"

        result_with_incapacitating = barbarian_abilities.has_danger_sense_advantage(
            character_id, 'dexterity', ['stunned']
        )
        assert not result_with_incapacitating, "Should be blocked by stunned in conditions list"

        result_without_conditions = barbarian_abilities.has_danger_sense_advantage(character_id, 'dexterity')
        assert result_without_conditions, "Should work without conditions parameter"

        print("[OK] All backwards compatibility tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


if __name__ == '__main__':
    print("=== Stage 1.2 Validation: Danger Sense Integration ===")

    success = True

    try:
        success &= test_danger_sense_integration()
        success &= test_backwards_compatibility()

        if success:
            print("\n[SUCCESS] STAGE 1.2 TESTS PASSED")
            print("Enhanced Danger Sense integration working!")
        else:
            print("\n[FAILED] STAGE 1.2 TESTS FAILED")
            exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)