import sqlite3
import sys

def validate_schema_fix(db_path='talekeeper.db'):
    print("Validating character_features schema...")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(character_features)")
        columns = {row[1] for row in cursor.fetchall()}

        print(f"\nCurrent columns: {columns}")

        required_new = {'character_id', 'feature_name', 'feature_type',
                       'usage_type', 'level_gained', 'description', 'mechanics'}
        old_columns = {'feature_id', 'feature_source', 'feature_data'}

        if required_new.issubset(columns):
            print("✓ New schema columns present")
        else:
            missing = required_new - columns
            print(f"✗ Missing new schema columns: {missing}")
            return False

        if old_columns & columns:
            print(f"✗ Old schema columns still present: {old_columns & columns}")
            print("  (Note: This is expected - old columns remain but aren't used)")

        cursor.execute("""
            SELECT COUNT(*) FROM character_features
            WHERE feature_name IS NOT NULL
        """)
        new_count = cursor.fetchone()[0]

        print(f"\nFeatures using new schema: {new_count}")

        if new_count > 0:
            cursor.execute("""
                SELECT feature_name, feature_type, usage_type, level_gained
                FROM character_features
                WHERE feature_name IS NOT NULL
                LIMIT 5
            """)
            print("\nSample features:")
            for row in cursor.fetchall():
                print(f"  - {row[0]} ({row[1]}, {row[2]}, level {row[3]})")

        print("\n✓ Schema validation complete")
        return True

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'talekeeper.db'
    validate_schema_fix(db_path)
