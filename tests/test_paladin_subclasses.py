#test
import sqlite3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.subclass_feature_manager import SubclassFeatureManager


def test_subclass_features():
    print("\n=== Testing Paladin Subclass Features ===\n")

    db_path = "talekeeper.db"
    manager = SubclassFeatureManager(db_path)

    print("1. Testing Oath of Devotion features:")
    devotion_features = manager.get_all_subclass_features('oath_of_devotion')
    print(f"   Found {len(devotion_features)} features")
    for feature in devotion_features:
        print(f"   - Level {feature['level']}: {feature['feature_name']} ({feature['action_type']})")

    print("\n2. Testing Oath of the Unbroken features:")
    unbroken_features = manager.get_all_subclass_features('oath_of_the_unbroken')
    print(f"   Found {len(unbroken_features)} features")
    for feature in unbroken_features:
        print(f"   - Level {feature['level']}: {feature['feature_name']} ({feature['action_type']})")

    print("\n3. Testing Oath Spells:")
    devotion_spells = manager.get_oath_spells('oath_of_devotion', 20)
    print(f"   Oath of Devotion has {len(devotion_spells)} oath spells:")
    for spell in devotion_spells:
        print(f"   - {spell}")

    unbroken_spells = manager.get_oath_spells('oath_of_the_unbroken', 20)
    print(f"\n   Oath of the Unbroken has {len(unbroken_spells)} oath spells:")
    for spell in unbroken_spells:
        print(f"   - {spell}")

    print("\n4. Testing feature granting:")
    test_character_id = "test_paladin_123"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM character_features WHERE character_id = ?", (test_character_id,))
        cursor.execute("DELETE FROM feature_states WHERE character_id = ?", (test_character_id,))
        conn.commit()

    level_3_features = manager.get_subclass_features_for_level('oath_of_devotion', 3)
    for feature in level_3_features:
        success = manager.grant_subclass_feature(test_character_id, feature['id'], 3)
        print(f"   Granted {feature['feature_name']}: {success}")

    character_features = manager.get_character_subclass_features(test_character_id)
    print(f"\n   Character has {len(character_features)} subclass features")
    for feature in character_features:
        print(f"   - {feature['feature_name']} (Level {feature['level_gained']})")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM character_features WHERE character_id = ?", (test_character_id,))
        cursor.execute("DELETE FROM feature_states WHERE character_id = ?", (test_character_id,))
        conn.commit()

    print("\n5. Testing subclass data integrity:")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM subclasses WHERE class_id = 'paladin' ORDER BY name")
        paladin_subclasses = cursor.fetchall()
        print(f"   Found {len(paladin_subclasses)} paladin subclasses:")
        for subclass_id, name in paladin_subclasses:
            cursor.execute("SELECT COUNT(*) FROM subclass_features WHERE subclass_id = ?", (subclass_id,))
            feature_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM subclass_spells WHERE subclass_id = ?", (subclass_id,))
            spell_count = cursor.fetchone()[0]
            print(f"   - {name} ({subclass_id}): {feature_count} features, {spell_count} spells")

    print("\n=== All Tests Completed ===\n")


if __name__ == "__main__":
    test_subclass_features()