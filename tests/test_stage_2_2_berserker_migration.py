"""
Test Stage 2.2: Berserker Feature Migration
Tests migration of Berserker features to the new system with condition integration.
"""

import sys
import os
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.enhanced_subclass_manager import EnhancedSubclassManager
from services.condition_manager import ConditionManager, ConditionType, ActiveCondition


def test_mindless_rage_integration():
    """Test Mindless Rage with condition immunity system."""
    print("Testing Mindless Rage condition immunity...")

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
                    level INTEGER,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    is_raging BOOLEAN DEFAULT FALSE,
                    level INTEGER
                )
            """)

            # Insert level 6 berserker
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id)
                VALUES ('mindless_test', 'Mindless Berserker', 6, 'barbarian', 'berserker')
            """)
            cursor.execute("""
                INSERT INTO barbarian_features (character_id, is_raging, level)
                VALUES ('mindless_test', FALSE, 6)
            """)
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)
        condition_manager = ConditionManager(test_db_path)
        character_id = 'mindless_test'

        # Test 1: Not raging - no immunities
        result = manager.apply_mindless_rage(character_id)
        assert not result['success'], "Should fail when not raging"
        print("[OK] Mindless Rage requires raging")

        # Test 2: Start raging - apply immunities
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE barbarian_features SET is_raging = TRUE
                WHERE character_id = ?
            """, (character_id,))
            conn.commit()

        # Apply existing conditions before rage
        charmed = ActiveCondition(
            condition_type=ConditionType.CHARMED,
            source="Charm Person",
            duration_type="minutes",
            duration_remaining=10
        )
        frightened = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Dragon Fear",
            duration_type="rounds",
            duration_remaining=3
        )
        condition_manager.add_condition(character_id, charmed)
        condition_manager.add_condition(character_id, frightened)

        # Apply Mindless Rage
        result = manager.apply_mindless_rage(character_id)
        assert result['success'], "Should succeed when raging"
        assert "charmed" in result['immunities_applied']
        assert "frightened" in result['immunities_applied']
        assert "charmed" in result['conditions_removed']
        assert "frightened" in result['conditions_removed']
        print("[OK] Mindless Rage removes and prevents charmed/frightened")

        # Test 3: Try to apply charm/fear while immune
        new_charm = ActiveCondition(
            condition_type=ConditionType.CHARMED,
            source="Hypnotic Pattern",
            duration_type="minutes",
            duration_remaining=1
        )
        condition_manager.add_condition(character_id, new_charm)

        # Should be immune
        has_charmed = condition_manager.has_condition(character_id, ConditionType.CHARMED)
        assert not has_charmed, "Should be immune to charmed while raging"
        print("[OK] Immunity blocks new charm effects during rage")

        # Test 4: End rage - remove immunities
        result = manager.remove_rage_immunities(character_id)
        assert result['success']

        # Now charm should work
        condition_manager.add_condition(character_id, new_charm)
        has_charmed = condition_manager.has_condition(character_id, ConditionType.CHARMED)
        assert has_charmed, "Should be vulnerable to charmed after rage ends"
        print("[OK] Immunities removed when rage ends")

        print("[OK] All Mindless Rage integration tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_frenzy_damage_mechanics():
    """Test Frenzy damage bonus mechanics."""
    print("\nTesting Frenzy damage mechanics...")

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
                    level INTEGER,
                    class_id TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    is_raging BOOLEAN,
                    level INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE character_combat_state (
                    character_id TEXT PRIMARY KEY,
                    reckless_attack_active BOOLEAN
                )
            """)

            # Test different level berserkers
            levels = [3, 9, 16]
            for level in levels:
                char_id = f'frenzy_test_{level}'
                cursor.execute("""
                    INSERT INTO characters (id, name, level, class_id)
                    VALUES (?, ?, ?, 'barbarian')
                """, (char_id, f'Level {level} Berserker', level))
                cursor.execute("""
                    INSERT INTO barbarian_features (character_id, is_raging, level)
                    VALUES (?, TRUE, ?)
                """, (char_id, level))
                cursor.execute("""
                    INSERT INTO character_combat_state (character_id, reckless_attack_active)
                    VALUES (?, TRUE)
                """, (char_id,))
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)

        # Test Level 3 - 1d6
        result = manager.check_frenzy_trigger('frenzy_test_3')
        assert result['triggered']
        assert result['damage_dice'] == '1d6'
        print("[OK] Level 3 Frenzy: 1d6 damage")

        # Test Level 9 - 1d8
        result = manager.check_frenzy_trigger('frenzy_test_9')
        assert result['triggered']
        assert result['damage_dice'] == '1d8'
        print("[OK] Level 9 Frenzy: 1d8 damage")

        # Test Level 16 - 1d10
        result = manager.check_frenzy_trigger('frenzy_test_16')
        assert result['triggered']
        assert result['damage_dice'] == '1d10'
        print("[OK] Level 16 Frenzy: 1d10 damage")

        # Test without reckless attack
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_combat_state
                SET reckless_attack_active = FALSE
                WHERE character_id = 'frenzy_test_3'
            """)
            conn.commit()

        result = manager.check_frenzy_trigger('frenzy_test_3')
        assert not result['triggered']
        print("[OK] Frenzy requires Reckless Attack")

        # Test without rage
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE barbarian_features
                SET is_raging = FALSE
                WHERE character_id = 'frenzy_test_9'
            """)
            conn.commit()

        result = manager.check_frenzy_trigger('frenzy_test_9')
        assert not result['triggered']
        print("[OK] Frenzy requires Rage")

        print("[OK] All Frenzy mechanics tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_retaliation_mechanics():
    """Test Retaliation reaction mechanics."""
    print("\nTesting Retaliation mechanics...")

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
                    level INTEGER,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT PRIMARY KEY,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)

            # Insert level 10 berserker
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id)
                VALUES ('retaliation_test', 'Retaliation Berserker', 10, 'barbarian', 'berserker')
            """)
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)

        # Get berserker features
        features = manager.get_character_subclass_features('retaliation_test', 10)
        retaliation = next(f for f in features if f.name == "Retaliation")

        # Verify Retaliation properties
        from services.enhanced_subclass_manager import FeatureType, ActionCost
        assert retaliation.feature_type == FeatureType.REACTION
        assert retaliation.action_cost == ActionCost.REACTION
        assert retaliation.level == 10
        assert retaliation.mechanics['range'] == 5
        assert retaliation.mechanics['trigger'] == 'damaged_by_adjacent_enemy'
        assert retaliation.mechanics['adds_rage_damage'] is True
        print("[OK] Retaliation properties correct")

        # Check prerequisites
        assert 'enemy_within_5ft' in retaliation.prerequisites
        assert 'took_damage' in retaliation.prerequisites
        print("[OK] Retaliation has correct prerequisites")

        print("[OK] All Retaliation mechanics tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_intimidating_presence_mechanics():
    """Test Intimidating Presence mechanics."""
    print("\nTesting Intimidating Presence mechanics...")

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
                    level INTEGER,
                    class_id TEXT,
                    subclass_id TEXT,
                    strength INTEGER,
                    proficiency_bonus INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT PRIMARY KEY,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)

            # Insert level 14 berserker with STR 20
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id, strength, proficiency_bonus)
                VALUES ('intimidate_test', 'Intimidating Berserker', 14, 'barbarian', 'berserker', 20, 5)
            """)
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)

        # Get berserker features
        features = manager.get_character_subclass_features('intimidate_test', 14)
        intimidating = next(f for f in features if f.name == "Intimidating Presence")

        # Verify feature properties
        from services.enhanced_subclass_manager import FeatureType, ActionCost
        assert intimidating.feature_type == FeatureType.ACTIVATED
        assert intimidating.action_cost == ActionCost.BONUS_ACTION
        assert intimidating.uses_per_rest == 1
        assert intimidating.rest_type == "long"
        assert intimidating.duration == "1 minute"
        print("[OK] Intimidating Presence properties correct")

        # Test mechanics
        assert intimidating.mechanics['area'] == '30ft_emanation'
        assert intimidating.mechanics['save'] == 'wisdom'
        assert intimidating.mechanics['condition_applied'] == 'frightened'
        assert intimidating.mechanics['once_per_target'] is True
        print("[OK] Intimidating Presence mechanics correct")

        # Test usage
        result = manager.use_intimidating_presence('intimidate_test')
        assert result['success']
        assert result['save_dc'] == 8 + 5 + 5  # 8 + STR(5) + prof(5) = 18
        assert result['uses_remaining'] == 0
        print(f"[OK] Intimidating Presence DC calculation correct (DC {result['save_dc']})")

        # Test resource limit
        result2 = manager.use_intimidating_presence('intimidate_test')
        assert not result2['success']
        print("[OK] Intimidating Presence limited to once per long rest")

        print("[OK] All Intimidating Presence mechanics tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_berserker_legacy_compatibility():
    """Test that new system doesn't break existing Berserker functionality."""
    print("\nTesting legacy Berserker compatibility...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema with legacy structure
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    is_raging BOOLEAN,
                    level INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT PRIMARY KEY,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)

            # Insert berserker without new tables
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id)
                VALUES ('legacy_test', 'Legacy Berserker', 14, 'barbarian', 'berserker')
            """)
            cursor.execute("""
                INSERT INTO barbarian_features (character_id, is_raging, level)
                VALUES ('legacy_test', TRUE, 14)
            """)
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)

        # Should still be able to get features
        features = manager.get_character_subclass_features('legacy_test', 14)
        assert len(features) == 4
        print("[OK] Legacy character can access new features")

        # Test with character_subclasses table
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_subclasses (character_id, class_id, subclass_id)
                VALUES ('legacy_test', 'barbarian', 'berserker')
            """)
            conn.commit()

        features2 = manager.get_character_subclass_features('legacy_test', 14)
        assert len(features2) == 4
        print("[OK] Works with both subclass storage methods")

        print("[OK] All legacy compatibility tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


if __name__ == '__main__':
    print("=== Stage 2.2 Validation: Berserker Feature Migration ===")

    success = True

    try:
        success &= test_mindless_rage_integration()
        success &= test_frenzy_damage_mechanics()
        success &= test_retaliation_mechanics()
        success &= test_intimidating_presence_mechanics()
        success &= test_berserker_legacy_compatibility()

        if success:
            print("\n[SUCCESS] STAGE 2.2 COMPLETE")
            print("+ Mindless Rage integrated with condition immunity system")
            print("+ Frenzy damage scaling by level (1d6/1d8/1d10)")
            print("+ Retaliation reaction mechanics defined")
            print("+ Intimidating Presence with resource tracking")
            print("+ Legacy Berserker compatibility maintained")
            print("\n*** Ready for Stage 2.3: UI Integration ***")
        else:
            print("\n[FAILED] STAGE 2.2 TESTS FAILED")
            exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)