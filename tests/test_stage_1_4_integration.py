"""
Test Stage 1.4: Full Condition Integration
Tests complete integration of conditions with advantage system, action economy, and combat mechanics.
"""

import sys
import os
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.condition_manager import ConditionManager, ConditionType, ActiveCondition
from services.condition_stat_service import ConditionStatService
from services.advantage_system import AdvantageSystem, RollType
from services.barbarian_abilities import BarbarianAbilitiesService


def test_condition_advantage_integration():
    """Test that conditions properly integrate with advantage system."""
    print("Testing condition-advantage system integration...")

    # Create temporary database
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, level)
                VALUES ('advantage_test', 'Advantage Test', 5)
            """)
            conn.commit()

        condition_stat_service = ConditionStatService(test_db_path)
        condition_manager = condition_stat_service.condition_manager
        character_id = 'advantage_test'

        # Test 1: No conditions - no modifiers
        attack_mods = condition_stat_service.get_attack_roll_modifier(character_id)
        assert not attack_mods["advantage"], "Should have no advantage without conditions"
        assert not attack_mods["disadvantage"], "Should have no disadvantage without conditions"
        print("[OK] Baseline: No conditions = no modifiers")

        # Test 2: Add poisoned condition - should give attack disadvantage
        poisoned = ActiveCondition(
            condition_type=ConditionType.POISONED,
            source="Test Poison",
            duration_type="rounds",
            duration_remaining=3
        )
        condition_manager.add_condition(character_id, poisoned)

        attack_mods = condition_stat_service.get_attack_roll_modifier(character_id)
        assert attack_mods["disadvantage"], "Poisoned should give attack disadvantage"
        assert "poisoned" in attack_mods["sources"][0].lower(), "Should list poisoned as source"
        print("[OK] Poisoned condition gives attack disadvantage")

        # Test 3: Add invisible condition - should give attack advantage
        invisible = ActiveCondition(
            condition_type=ConditionType.INVISIBLE,
            source="Invisibility Spell",
            duration_type="minutes",
            duration_remaining=10
        )
        condition_manager.add_condition(character_id, invisible)

        attack_mods = condition_stat_service.get_attack_roll_modifier(character_id)
        assert attack_mods["advantage"], "Invisible should give attack advantage"
        assert attack_mods["disadvantage"], "Should still have disadvantage from poisoned"
        print("[OK] Multiple conditions tracked correctly (advantage + disadvantage)")

        # Test 4: Advantage system should calculate normal roll when both present
        context = {'character_id': character_id}
        advantage_sources = AdvantageSystem.get_common_advantage_sources(RollType.ATTACK, context)
        disadvantage_sources = AdvantageSystem.get_common_disadvantage_sources(RollType.ATTACK, context)

        advantage_state = AdvantageSystem.calculate_advantage_state(advantage_sources, disadvantage_sources)

        # Both advantage and disadvantage should result in normal roll
        from services.advantage_system import AdvantageState
        assert advantage_state == AdvantageState.NORMAL, "Advantage + Disadvantage should cancel to normal"
        print("[OK] Advantage system correctly cancels advantage and disadvantage")

        print("[OK] All condition-advantage integration tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_condition_movement_restrictions():
    """Test movement speed modifications from conditions."""
    print("\nTesting movement speed modifications...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    speed INTEGER DEFAULT 30
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, speed)
                VALUES ('movement_test', 'Movement Test', 30)
            """)
            conn.commit()

        condition_stat_service = ConditionStatService(test_db_path)
        condition_manager = condition_stat_service.condition_manager
        character_id = 'movement_test'

        # Test 1: Normal speed
        speed = condition_stat_service.get_movement_speed_modifier(character_id)
        assert speed == 30, f"Base speed should be 30, got {speed}"
        print("[OK] Base movement speed correct")

        # Test 2: Grappled - speed = 0
        grappled = ActiveCondition(
            condition_type=ConditionType.GRAPPLED,
            source="Monster Grapple",
            duration_type="until_escape"
        )
        condition_manager.add_condition(character_id, grappled)

        speed = condition_stat_service.get_movement_speed_modifier(character_id)
        assert speed == 0, f"Grappled speed should be 0, got {speed}"
        print("[OK] Grappled condition reduces speed to 0")

        # Test 3: Replace with exhaustion - speed reduction
        condition_manager.remove_condition(character_id, ConditionType.GRAPPLED)

        exhausted = ActiveCondition(
            condition_type=ConditionType.EXHAUSTION,
            source="Forced March",
            duration_type="permanent",
            exhaustion_level=2
        )
        condition_manager.add_condition(character_id, exhausted)

        speed = condition_stat_service.get_movement_speed_modifier(character_id)
        expected_speed = 30 - (2 * 5)  # Base 30 - (2 levels * 5 ft each) = 20
        assert speed == expected_speed, f"Exhaustion 2 speed should be {expected_speed}, got {speed}"
        print(f"[OK] Exhaustion level 2 reduces speed correctly (30 -> {speed})")

        print("[OK] All movement restriction tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_action_economy_restrictions():
    """Test that conditions properly block actions."""
    print("\nTesting action economy restrictions...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name)
                VALUES ('action_test', 'Action Test')
            """)
            conn.commit()

        condition_stat_service = ConditionStatService(test_db_path)
        condition_manager = condition_stat_service.condition_manager
        character_id = 'action_test'

        # Test 1: No conditions - can take all actions
        actions = condition_stat_service.can_take_actions(character_id)
        assert actions["actions"], "Should be able to take actions"
        assert actions["bonus_actions"], "Should be able to take bonus actions"
        assert actions["reactions"], "Should be able to take reactions"
        assert actions["movement"], "Should be able to move"
        print("[OK] Baseline: Can take all actions without conditions")

        # Test 2: Paralyzed - blocks all actions (incapacitated)
        paralyzed = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )
        condition_manager.add_condition(character_id, paralyzed)

        actions = condition_stat_service.can_take_actions(character_id)
        assert not actions["actions"], "Paralyzed should block actions"
        assert not actions["bonus_actions"], "Paralyzed should block bonus actions"
        assert not actions["reactions"], "Paralyzed should block reactions"
        assert not actions["movement"], "Paralyzed should block movement"
        assert len(actions["restrictions"]) > 0, "Should have restriction messages"
        print("[OK] Paralyzed condition blocks all actions")

        # Test 3: Replace with just incapacitated
        condition_manager.remove_condition(character_id, ConditionType.PARALYZED)

        incapacitated = ActiveCondition(
            condition_type=ConditionType.INCAPACITATED,
            source="Some Effect",
            duration_type="rounds",
            duration_remaining=2
        )
        condition_manager.add_condition(character_id, incapacitated)

        actions = condition_stat_service.can_take_actions(character_id)
        assert not actions["actions"], "Incapacitated should block actions"
        assert not actions["bonus_actions"], "Incapacitated should block bonus actions"
        assert not actions["reactions"], "Incapacitated should block reactions"
        assert actions["movement"], "Incapacitated should allow movement"
        print("[OK] Incapacitated blocks actions but allows movement")

        print("[OK] All action economy restriction tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_saving_throw_integration():
    """Test saving throw modifications from conditions."""
    print("\nTesting saving throw modifications...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name)
                VALUES ('save_test', 'Save Test')
            """)
            conn.commit()

        condition_stat_service = ConditionStatService(test_db_path)
        condition_manager = condition_stat_service.condition_manager
        character_id = 'save_test'

        # Test 1: Paralyzed - auto-fail STR and DEX saves
        paralyzed = ActiveCondition(
            condition_type=ConditionType.PARALYZED,
            source="Hold Person",
            duration_type="minutes",
            duration_remaining=1
        )
        condition_manager.add_condition(character_id, paralyzed)

        str_save = condition_stat_service.get_saving_throw_modifier(character_id, "strength")
        dex_save = condition_stat_service.get_saving_throw_modifier(character_id, "dexterity")
        con_save = condition_stat_service.get_saving_throw_modifier(character_id, "constitution")

        assert str_save["auto_fail"], "Paralyzed should auto-fail Strength saves"
        assert dex_save["auto_fail"], "Paralyzed should auto-fail Dexterity saves"
        assert not con_save["auto_fail"], "Paralyzed should not auto-fail Constitution saves"
        print("[OK] Paralyzed condition auto-fails STR and DEX saves")

        # Test 2: Replace with restrained - DEX save disadvantage
        condition_manager.remove_condition(character_id, ConditionType.PARALYZED)

        restrained = ActiveCondition(
            condition_type=ConditionType.RESTRAINED,
            source="Net",
            duration_type="until_escape"
        )
        condition_manager.add_condition(character_id, restrained)

        dex_save = condition_stat_service.get_saving_throw_modifier(character_id, "dexterity")
        str_save = condition_stat_service.get_saving_throw_modifier(character_id, "strength")

        assert dex_save["disadvantage"], "Restrained should give Dexterity save disadvantage"
        assert not str_save["disadvantage"], "Restrained should not affect Strength saves"
        print("[OK] Restrained condition gives Dexterity save disadvantage")

        print("[OK] All saving throw integration tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_danger_sense_full_integration():
    """Test Danger Sense with full condition system integration."""
    print("\nTesting full Danger Sense integration...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema with barbarian
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
                VALUES ('danger_test', 'Danger Barbarian', 5, 'barbarian')
            """)
            cursor.execute("""
                INSERT INTO barbarian_features (character_id, level, danger_sense_active)
                VALUES ('danger_test', 5, 1)
            """)
            conn.commit()

        condition_stat_service = ConditionStatService(test_db_path)
        condition_manager = condition_stat_service.condition_manager
        barbarian_service = BarbarianAbilitiesService(test_db_path)
        character_id = 'danger_test'

        # Test 1: Danger Sense works normally
        has_danger_sense = barbarian_service.has_danger_sense_advantage_enhanced(character_id, 'dexterity')
        assert has_danger_sense, "Danger Sense should work without conditions"
        print("[OK] Danger Sense works without incapacitating conditions")

        # Test 2: Add stunned condition - should block Danger Sense
        stunned = ActiveCondition(
            condition_type=ConditionType.STUNNED,
            source="Monk Strike",
            duration_type="rounds",
            duration_remaining=1
        )
        condition_manager.add_condition(character_id, stunned)

        has_danger_sense = barbarian_service.has_danger_sense_advantage_enhanced(character_id, 'dexterity')
        assert not has_danger_sense, "Stunned should block Danger Sense"
        print("[OK] Stunned condition blocks Danger Sense")

        # Test 3: Condition also blocks DEX saves and gives auto-fail STR/DEX
        dex_save_mod = condition_stat_service.get_saving_throw_modifier(character_id, 'dexterity')
        str_save_mod = condition_stat_service.get_saving_throw_modifier(character_id, 'strength')

        assert dex_save_mod["auto_fail"], "Stunned should auto-fail DEX saves"
        assert str_save_mod["auto_fail"], "Stunned should auto-fail STR saves"
        print("[OK] Stunned condition affects saves correctly")

        print("[OK] All full integration tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_exhaustion_comprehensive():
    """Test comprehensive exhaustion effects across all systems."""
    print("\nTesting comprehensive exhaustion effects...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    speed INTEGER DEFAULT 30
                )
            """)
            cursor.execute("""
                INSERT INTO characters (id, name, speed)
                VALUES ('exhaustion_test', 'Exhaustion Test', 30)
            """)
            conn.commit()

        condition_stat_service = ConditionStatService(test_db_path)
        condition_manager = condition_stat_service.condition_manager
        character_id = 'exhaustion_test'

        # Test Level 3 exhaustion
        exhausted = ActiveCondition(
            condition_type=ConditionType.EXHAUSTION,
            source="Starvation",
            duration_type="permanent",
            exhaustion_level=3
        )
        condition_manager.add_condition(character_id, exhausted)

        # Test movement speed reduction
        speed = condition_stat_service.get_movement_speed_modifier(character_id)
        expected_speed = 30 - (3 * 5)  # 30 - 15 = 15
        assert speed == expected_speed, f"Exhaustion 3 speed should be {expected_speed}, got {speed}"

        # Test attack roll penalties
        attack_mod = condition_stat_service.get_attack_roll_modifier(character_id)
        expected_penalty = 3 * 2  # -6
        assert attack_mod["penalty"] == expected_penalty, f"Exhaustion 3 attack penalty should be {expected_penalty}, got {attack_mod['penalty']}"

        # Test saving throw penalties
        con_save = condition_stat_service.get_saving_throw_modifier(character_id, "constitution")
        assert con_save["penalty"] == expected_penalty, f"Exhaustion 3 save penalty should be {expected_penalty}, got {con_save['penalty']}"

        # Test ability check penalties
        str_check = condition_stat_service.get_ability_check_modifier(character_id, "strength")
        assert str_check["penalty"] == expected_penalty, f"Exhaustion 3 ability check penalty should be {expected_penalty}, got {str_check['penalty']}"

        # Test initiative penalties
        init_mod = condition_stat_service.get_initiative_modifier(character_id)
        assert init_mod["penalty"] == expected_penalty, f"Exhaustion 3 initiative penalty should be {expected_penalty}, got {init_mod['penalty']}"

        print(f"[OK] Exhaustion level 3 affects all systems correctly (-{expected_penalty} to all d20 tests, speed {speed})")
        print("[OK] All exhaustion comprehensive tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


if __name__ == '__main__':
    print("=== Stage 1.4 Validation: Full Condition Integration ===")

    success = True

    try:
        success &= test_condition_advantage_integration()
        success &= test_condition_movement_restrictions()
        success &= test_action_economy_restrictions()
        success &= test_saving_throw_integration()
        success &= test_danger_sense_full_integration()
        success &= test_exhaustion_comprehensive()

        if success:
            print("\n[SUCCESS] STAGE 1.4 COMPLETE")
            print("+ Condition-advantage system integration working")
            print("+ Movement restrictions applied correctly")
            print("+ Action economy properly restricted")
            print("+ Saving throw modifications functional")
            print("+ Full Danger Sense integration confirmed")
            print("+ Comprehensive exhaustion effects working")
            print("\n*** PHASE 1 COMPLETE: Condition System Foundation ***")
        else:
            print("\n[FAILED] STAGE 1.4 TESTS FAILED")
            exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)