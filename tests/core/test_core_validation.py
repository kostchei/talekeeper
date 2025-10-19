#test
#!/usr/bin/env python3
"""
Core validation tests for TaleKeeper regression suite.

These tests validate the most fundamental systems and should NEVER fail.
If any of these fail, the application is broken.
"""

import sys
import sqlite3
from pathlib import Path

# Ensure project imports resolve
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

def test_database_exists():
    """Test that the database exists and is accessible."""
    db_path = project_root / "talekeeper.db"
    if not db_path.exists():
        raise AssertionError(f"Database not found at {db_path}")

    # Test connection
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    required_tables = ['characters', 'classes', 'races', 'equipment', 'character_features']
    missing_tables = [table for table in required_tables if table not in tables]

    if missing_tables:
        raise AssertionError(f"Missing required tables: {missing_tables}")

    print("[OK] Database validation passed")

def test_core_imports():
    """Test that core modules can be imported."""
    try:
        from core.game_engine_sqlite import GameEngineSQLite
        from ui.main_window import MainWindow
        from services.feat_effects import FeatEffectsProcessor
        print("[OK] Core imports successful")
    except ImportError as e:
        raise AssertionError(f"Failed to import core modules: {e}")

def test_character_classes_data():
    """Test that character classes are properly loaded."""
    db_path = project_root / "talekeeper.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM classes")
    class_count = cursor.fetchone()[0]

    cursor.execute("SELECT name FROM classes WHERE name = 'Fighter'")
    fighter_exists = cursor.fetchone()

    conn.close()

    if class_count == 0:
        raise AssertionError("No character classes found in database")

    if not fighter_exists:
        raise AssertionError("Fighter class not found in database")

    print(f"[OK] Character classes loaded ({class_count} classes)")

def test_equipment_data():
    """Test that equipment data is loaded."""
    db_path = project_root / "talekeeper.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM equipment")
    equipment_count = cursor.fetchone()[0]

    cursor.execute("SELECT name FROM equipment WHERE name = 'Longsword'")
    longsword_exists = cursor.fetchone()

    conn.close()

    if equipment_count == 0:
        raise AssertionError("No equipment found in database")

    if not longsword_exists:
        raise AssertionError("Basic equipment (Longsword) not found")

    print(f"[OK] Equipment data loaded ({equipment_count} items)")

def run_all_tests():
    """Run all core validation tests."""
    tests = [
        test_database_exists,
        test_core_imports,
        test_character_classes_data,
        test_equipment_data,
    ]

    print("Running core validation tests...")
    print("-" * 40)

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"[FAIL] {test.__name__} FAILED: {e}")
            return False

    print("-" * 40)
    print("[PASS] All core validation tests passed")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)