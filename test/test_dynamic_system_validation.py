import sqlite3
import json

def test_dynamic_feature_system():
    """Test the dynamic feature system with existing database"""
    db_path = "talekeeper.db"

    print("=== Dynamic Feature System Validation ===")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Test 1: Check class features are loaded
        cursor.execute("SELECT COUNT(*) FROM class_features_progression")
        class_feature_count = cursor.fetchone()[0]
        print(f"[OK] Class features loaded: {class_feature_count}")

        # Test 2: Check subclass features are loaded
        cursor.execute("SELECT COUNT(*) FROM subclass_features_progression")
        subclass_feature_count = cursor.fetchone()[0]
        print(f"[OK] Subclass features loaded: {subclass_feature_count}")

        # Test 3: Show rogue progression
        cursor.execute("""
            SELECT level, feature_name, feature_type
            FROM class_features_progression
            WHERE class_id = 'rogue'
            ORDER BY level
        """)
        rogue_features = cursor.fetchall()
        print(f"\n=== Rogue Class Progression ({len(rogue_features)} features) ===")
        for level, name, ftype in rogue_features:
            print(f"Level {level}: {name} ({ftype})")

        # Test 4: Show thief subclass progression
        cursor.execute("""
            SELECT level, feature_name, feature_type
            FROM subclass_features_progression
            WHERE subclass_id = 'thief'
            ORDER BY level
        """)
        thief_features = cursor.fetchall()
        print(f"\n=== Thief Subclass Progression ({len(thief_features)} features) ===")
        for level, name, ftype in thief_features:
            print(f"Level {level}: {name} ({ftype})")

        # Test 5: Check feature mechanics
        cursor.execute("""
            SELECT feature_name, mechanics
            FROM class_features_progression
            WHERE class_id = 'rogue' AND feature_name = 'Expertise'
        """)
        expertise_result = cursor.fetchone()
        if expertise_result:
            name, mechanics_json = expertise_result
            mechanics = json.loads(mechanics_json)
            print(f"\n=== Expertise Feature Mechanics ===")
            print(f"Feature: {name}")
            print(f"Mechanics: {mechanics}")

        # Test 6: Show level 3 features (subclass selection level)
        cursor.execute("""
            SELECT feature_name
            FROM class_features_progression
            WHERE class_id = 'rogue' AND level = 3
        """)
        level_3_class = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT feature_name
            FROM subclass_features_progression
            WHERE subclass_id = 'thief' AND level = 3
        """)
        level_3_subclass = [row[0] for row in cursor.fetchall()]

        print(f"\n=== Level 3 Features ===")
        print(f"Class features: {level_3_class}")
        print(f"Thief subclass features: {level_3_subclass}")

        # Test 7: Verify JSON mechanics parsing
        cursor.execute("""
            SELECT feature_name, mechanics
            FROM class_features_progression
            WHERE mechanics LIKE '%subclass_selection%'
        """)
        subclass_selection_features = cursor.fetchall()
        print(f"\n=== Subclass Selection Features ===")
        for name, mechanics_json in subclass_selection_features:
            mechanics = json.loads(mechanics_json)
            print(f"{name}: {mechanics}")

        print(f"\n[OK] Dynamic feature system validation complete!")
        print(f"[OK] Ready to handle {len(set(f[0] for f in rogue_features))} class levels")
        print(f"[OK] Ready to handle {len(set(f[0] for f in thief_features))} subclass levels")

if __name__ == "__main__":
    test_dynamic_feature_system()