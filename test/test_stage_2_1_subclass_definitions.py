# test
"""
Test Stage 2.1: Enhanced Subclass Definitions
Tests the new subclass definition system in isolation.
"""

import sys
import os
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.enhanced_subclass_manager import (
    EnhancedSubclassManager, SubclassFeature, SubclassDefinition,
    FeatureType, ActionCost, BerserkerDefinition
)


def test_subclass_feature_creation():
    """Test creating individual subclass features."""
    print("Testing subclass feature creation...")

    # Test Frenzy feature
    frenzy = SubclassFeature(
        name="Frenzy",
        description="Deal extra damage when using Reckless Attack while Raging",
        level=3,
        feature_type=FeatureType.TRIGGERED,
        action_cost=ActionCost.NONE,
        prerequisites={"raging": True, "reckless_attack": True},
        mechanics={
            "damage_bonus_dice": {3: "1d6", 9: "1d8", 16: "1d10"}
        }
    )

    assert frenzy.name == "Frenzy"
    assert frenzy.feature_type == FeatureType.TRIGGERED
    assert frenzy.level == 3
    print("[OK] Frenzy feature created correctly")

    # Test Mindless Rage feature
    mindless_rage = SubclassFeature(
        name="Mindless Rage",
        description="Immune to charmed and frightened while raging",
        level=6,
        feature_type=FeatureType.PASSIVE,
        condition_immunities=["charmed", "frightened"]
    )

    assert mindless_rage.feature_type == FeatureType.PASSIVE
    assert "charmed" in mindless_rage.condition_immunities
    print("[OK] Mindless Rage feature created correctly")

    # Test Retaliation feature
    retaliation = SubclassFeature(
        name="Retaliation",
        description="React to damage with an attack",
        level=10,
        feature_type=FeatureType.REACTION,
        action_cost=ActionCost.REACTION
    )

    assert retaliation.action_cost == ActionCost.REACTION
    print("[OK] Retaliation feature created correctly")

    # Test serialization
    frenzy_dict = frenzy.to_dict()
    assert frenzy_dict['feature_type'] == 'triggered'
    assert frenzy_dict['action_cost'] == 'none'

    # Test deserialization
    frenzy_restored = SubclassFeature.from_dict(frenzy_dict)
    assert frenzy_restored.name == frenzy.name
    assert frenzy_restored.feature_type == frenzy.feature_type
    print("[OK] Feature serialization/deserialization works")

    print("[OK] All feature creation tests passed")
    return True


def test_berserker_definition():
    """Test the Berserker subclass definition."""
    print("\nTesting Berserker subclass definition...")

    berserker = BerserkerDefinition.create()

    assert berserker.class_name == "barbarian"
    assert berserker.subclass_name == "berserker"
    assert len(berserker.features) == 4
    print(f"[OK] Berserker has {len(berserker.features)} features")

    # Test feature progression
    level_3_features = berserker.get_features_at_level(3)
    assert len(level_3_features) == 1
    assert level_3_features[0].name == "Frenzy"
    print("[OK] Level 3: Frenzy available")

    level_6_features = berserker.get_features_at_level(6)
    assert len(level_6_features) == 2
    feature_names = [f.name for f in level_6_features]
    assert "Frenzy" in feature_names
    assert "Mindless Rage" in feature_names
    print("[OK] Level 6: Frenzy and Mindless Rage available")

    level_10_features = berserker.get_features_at_level(10)
    assert len(level_10_features) == 3
    print("[OK] Level 10: 3 features available")

    level_14_features = berserker.get_features_at_level(14)
    assert len(level_14_features) == 4
    print("[OK] Level 14: All 4 features available")

    # Test feature type filtering
    passive_features = berserker.get_features_by_type(FeatureType.PASSIVE)
    assert len(passive_features) == 1
    assert passive_features[0].name == "Mindless Rage"
    print("[OK] Passive features filtered correctly")

    reaction_features = berserker.get_features_by_type(FeatureType.REACTION)
    assert len(reaction_features) == 1
    assert reaction_features[0].name == "Retaliation"
    print("[OK] Reaction features filtered correctly")

    print("[OK] All Berserker definition tests passed")
    return True


def test_enhanced_subclass_manager():
    """Test the enhanced subclass manager."""
    print("\nTesting enhanced subclass manager...")

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
                    subclass_id TEXT,
                    strength INTEGER DEFAULT 16,
                    proficiency_bonus INTEGER DEFAULT 3
                )
            """)
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT PRIMARY KEY,
                    class_id TEXT,
                    subclass_id TEXT,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    is_raging BOOLEAN DEFAULT FALSE,
                    level INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE character_combat_state (
                    character_id TEXT PRIMARY KEY,
                    reckless_attack_active BOOLEAN DEFAULT FALSE
                )
            """)

            # Insert test barbarian
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id)
                VALUES ('test_berserker', 'Test Berserker', 14, 'barbarian', 'berserker')
            """)
            cursor.execute("""
                INSERT INTO character_subclasses (character_id, class_id, subclass_id)
                VALUES ('test_berserker', 'barbarian', 'berserker')
            """)
            cursor.execute("""
                INSERT INTO barbarian_features (character_id, is_raging, level)
                VALUES ('test_berserker', TRUE, 14)
            """)
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)

        # Test subclass definition retrieval
        berserker_def = manager.get_subclass_definition("barbarian", "berserker")
        assert berserker_def is not None
        assert berserker_def.subclass_name == "berserker"
        print("[OK] Subclass definition retrieved")

        # Test character feature retrieval
        features = manager.get_character_subclass_features('test_berserker', 14)
        assert len(features) == 4
        feature_names = [f.name for f in features]
        assert "Frenzy" in feature_names
        assert "Mindless Rage" in feature_names
        assert "Retaliation" in feature_names
        assert "Intimidating Presence" in feature_names
        print("[OK] Character features retrieved correctly")

        # Test Intimidating Presence
        result = manager.use_intimidating_presence('test_berserker')
        assert result['success']
        assert result['save_dc'] == 8 + 3 + 3  # 8 + str_mod(3) + prof(3) = 14
        assert result['uses_remaining'] == 0
        print(f"[OK] Intimidating Presence used (DC {result['save_dc']})")

        # Try to use again - should fail
        result2 = manager.use_intimidating_presence('test_berserker')
        assert not result2['success']
        assert "No uses remaining" in result2['reason']
        print("[OK] Intimidating Presence correctly limited to 1 use")

        # Test resource reset
        manager.reset_resources('test_berserker', 'long')
        result3 = manager.use_intimidating_presence('test_berserker')
        assert result3['success']
        print("[OK] Resources reset on long rest")

        # Test Frenzy trigger check
        cursor.execute("""
            INSERT OR REPLACE INTO character_combat_state (character_id, reckless_attack_active)
            VALUES ('test_berserker', TRUE)
        """)
        conn.commit()

        frenzy = manager.check_frenzy_trigger('test_berserker')
        assert frenzy['triggered']
        assert frenzy['damage_dice'] == "1d8"  # Level 14 gets d8
        print(f"[OK] Frenzy triggers with {frenzy['damage_dice']} damage")

        print("[OK] All enhanced subclass manager tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_feature_type_handlers():
    """Test different feature type handling."""
    print("\nTesting feature type handlers...")

    # Create features of each type
    passive = SubclassFeature(
        name="Test Passive",
        description="Always active",
        level=1,
        feature_type=FeatureType.PASSIVE
    )

    activated = SubclassFeature(
        name="Test Activated",
        description="Uses bonus action",
        level=1,
        feature_type=FeatureType.ACTIVATED,
        action_cost=ActionCost.BONUS_ACTION
    )

    triggered = SubclassFeature(
        name="Test Triggered",
        description="Triggers on condition",
        level=1,
        feature_type=FeatureType.TRIGGERED,
        prerequisites={"condition": True}
    )

    reaction = SubclassFeature(
        name="Test Reaction",
        description="Uses reaction",
        level=1,
        feature_type=FeatureType.REACTION,
        action_cost=ActionCost.REACTION
    )

    # Verify types
    assert passive.feature_type == FeatureType.PASSIVE
    assert passive.action_cost == ActionCost.NONE
    print("[OK] Passive feature has no action cost")

    assert activated.action_cost == ActionCost.BONUS_ACTION
    print("[OK] Activated feature has bonus action cost")

    assert triggered.prerequisites.get("condition") is True
    print("[OK] Triggered feature has prerequisites")

    assert reaction.action_cost == ActionCost.REACTION
    print("[OK] Reaction feature uses reaction")

    print("[OK] All feature type handler tests passed")
    return True


if __name__ == '__main__':
    print("=== Stage 2.1 Validation: Enhanced Subclass Definitions ===")

    success = True

    try:
        success &= test_subclass_feature_creation()
        success &= test_berserker_definition()
        success &= test_enhanced_subclass_manager()
        success &= test_feature_type_handlers()

        if success:
            print("\n[SUCCESS] STAGE 2.1 COMPLETE")
            print("+ SubclassFeature and SubclassDefinition classes working")
            print("+ Berserker definition complete with all 4 features")
            print("+ Feature type handlers (passive, activated, triggered, reaction)")
            print("+ Enhanced subclass manager functional")
            print("+ Resource tracking for limited-use features")
        else:
            print("\n[FAILED] STAGE 2.1 TESTS FAILED")
            exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)