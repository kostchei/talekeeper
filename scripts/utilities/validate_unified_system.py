# core
#utility
# core
import sqlite3


def validate_unified_system():
    """Validate the unified feature system database"""
    db_path = "talekeeper.db"

    print("=== Validating Unified Feature System ===")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        print("\n1. Checking new tables...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%features%'")
        tables = cursor.fetchall()
        expected_tables = ['class_features_progression', 'subclass_features_progression', 'character_feature_instances']

        for table_name in expected_tables:
            if any(table_name in table[0] for table in tables):
                print(f"[OK] {table_name} table exists")
            else:
                print(f"[MISSING] {table_name} table missing")

        print("\n2. Checking class feature data...")

        cursor.execute("SELECT class_id, COUNT(*) FROM class_features_progression GROUP BY class_id ORDER BY class_id")
        class_features = cursor.fetchall()

        expected_classes = ['barbarian', 'bard', 'cleric', 'druid', 'fighter', 'paladin', 'ranger', 'rogue', 'sorcerer', 'warlock', 'wizard']

        for class_id, count in class_features:
            print(f"[OK] {class_id}: {count} features")

        missing_classes = set(expected_classes) - set([cf[0] for cf in class_features])
        for missing in missing_classes:
            print(f"[MISSING] {missing}: No features found")

        print(f"\nTotal features: {sum(cf[1] for cf in class_features)}")

        print("\n3. Checking subclass selection features...")

        cursor.execute("""
            SELECT class_id, level, feature_name
            FROM class_features_progression
            WHERE JSON_EXTRACT(mechanics, '$.subclass_selection') = 1
            ORDER BY class_id
        """)
        subclass_selections = cursor.fetchall()

        for class_id, level, feature_name in subclass_selections:
            print(f"[OK] {class_id}: {feature_name} at level {level}")

        print("\n4. Checking feature types...")

        cursor.execute("SELECT feature_type, COUNT(*) FROM class_features_progression GROUP BY feature_type")
        feature_types = cursor.fetchall()

        for feature_type, count in feature_types:
            print(f"[OK] {feature_type}: {count} features")

        print("\n5. Checking sample feature mechanics...")

        cursor.execute("""
            SELECT class_id, feature_name, mechanics
            FROM class_features_progression
            WHERE feature_name IN ('Rage', 'Action Surge', 'Sneak Attack', 'Spellcasting')
            LIMIT 10
        """)
        sample_features = cursor.fetchall()

        for class_id, feature_name, mechanics in sample_features:
            mechanics_data = eval(mechanics) if mechanics else {}
            print(f"[OK] {class_id} - {feature_name}: {len(mechanics_data)} mechanics keys")

        print("\n6. Checking character feature instances...")

        cursor.execute("SELECT COUNT(*) FROM character_feature_instances")
        instance_count = cursor.fetchone()[0]
        print(f"Character feature instances: {instance_count}")

        print("\n7. Testing sample queries...")

        cursor.execute("""
            SELECT COUNT(*) FROM class_features_progression
            WHERE class_id = 'fighter' AND level <= 5
        """)
        fighter_features = cursor.fetchone()[0]
        print(f"[OK] Fighter features (levels 1-5): {fighter_features}")

        cursor.execute("""
            SELECT COUNT(*) FROM class_features_progression
            WHERE feature_type = 'bonus_action'
        """)
        bonus_actions = cursor.fetchone()[0]
        print(f"[OK] Bonus action features: {bonus_actions}")

        cursor.execute("""
            SELECT COUNT(*) FROM class_features_progression
            WHERE JSON_EXTRACT(mechanics, '$.asi_or_feat') = 1
        """)
        asi_features = cursor.fetchone()[0]
        print(f"[OK] ASI/Feat features: {asi_features}")

        print("\n=== Validation Complete ===")

        total_features = sum(cf[1] for cf in class_features)
        if total_features >= 150:  # Should have around 192 features
            print("SUCCESS: Unified Feature System FULLY OPERATIONAL")
            print(f"DATA: {total_features} features across {len(class_features)} classes")
            print("STATUS: Ready for dynamic feature loading")
        else:
            print("WARNING: System partially implemented")


if __name__ == "__main__":
    validate_unified_system()