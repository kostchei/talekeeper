import sqlite3
import tempfile
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from talekeeper.services.class_abilities_service import ClassAbilitiesService
from talekeeper.services.barbarian_abilities import BarbarianAbilitiesService
from talekeeper.services.fighter_abilities import FighterAbilitiesService


def setup_test_database():
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db.close()
    db_path = test_db.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE characters (
            id TEXT PRIMARY KEY,
            name TEXT,
            class_id TEXT,
            level INTEGER,
            strength INTEGER,
            dexterity INTEGER,
            constitution INTEGER,
            intelligence INTEGER,
            wisdom INTEGER,
            charisma INTEGER
        )
    """)

    cursor.execute("""
        INSERT INTO characters VALUES
        ('barb_test', 'Test Barbarian', 'barbarian', 5, 16, 14, 16, 10, 12, 8)
    """)

    with open('database/migrations/030_unified_class_abilities.sql', 'r') as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    return db_path


def test_barbarian_rage_unified():
    print("\n" + "="*60)
    print("TESTING: Barbarian Rage - Unified Service")
    print("="*60)

    db_path = setup_test_database()

    try:
        unified_service = ClassAbilitiesService(db_path)

        character_id = 'barb_test'

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO character_ability_usage (character_id, ability_id, current_uses, max_uses)
            VALUES (?, 'rage', 0, 4)
        """, (character_id,))

        conn.commit()
        conn.close()

        print("\n[TEST] Using Rage...")
        result = unified_service.use_ability(character_id, 'rage')
        print(f"  Success: {result.get('success')}")
        print(f"  Damage Bonus: {result.get('damage_bonus')}")
        print(f"  Resistances: {result.get('resistances')}")
        print(f"  Duration: {result.get('duration')} turns")
        print(f"  Message: {result.get('message', 'N/A')}")

        print("\n[TEST] Get Character Abilities...")
        abilities = unified_service.get_character_abilities(character_id)
        print(f"  Found {len(abilities)} abilities for level 5 Barbarian:")
        for ability in abilities[:8]:
            uses_info = f"{ability['current_uses']}/{ability['max_uses']}" if ability['max_uses'] > 0 else "unlimited"
            print(f"    - {ability['ability_name']} ({uses_info})")

        print("\n[TEST] Calculate max uses at different levels...")
        for level in [1, 5, 10, 15, 20]:
            max_uses = unified_service.calculate_max_uses('rage', level)
            print(f"    Level {level}: {max_uses} rage uses")

        print("\n[SUCCESS] Test completed!")

    finally:
        try:
            os.unlink(db_path)
        except:
            pass


def test_fighter_second_wind_unified():
    print("\n" + "="*60)
    print("TESTING: Fighter Second Wind - Unified Service")
    print("="*60)

    db_path = setup_test_database()

    try:
        unified_service = ClassAbilitiesService(db_path)

        character_id = 'fighter_test'

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters VALUES
            ('fighter_test', 'Test Fighter', 'fighter', 3, 16, 14, 14, 10, 12, 8)
        """)

        cursor.execute("""
            INSERT INTO character_ability_usage (character_id, ability_id, current_uses, max_uses)
            VALUES (?, 'second_wind', 0, 1)
        """, (character_id,))

        conn.commit()
        conn.close()

        print("\n[TEST] Using Second Wind...")
        result = unified_service.use_ability(character_id, 'second_wind')
        print(f"  Success: {result.get('success')}")
        print(f"  Healing: {result.get('healing')} HP")
        print(f"  Roll: {result.get('roll')}")
        print(f"  Message: {result.get('message')}")

        print("\n[TEST] Get Fighter Abilities...")
        abilities = unified_service.get_character_abilities(character_id)
        print(f"  Found {len(abilities)} abilities for level 3 Fighter:")
        for ability in abilities:
            uses_info = f"{ability['current_uses']}/{ability['max_uses']}" if ability['max_uses'] > 0 else "unlimited"
            print(f"    - {ability['ability_name']} ({uses_info})")

        print("\n[SUCCESS] Test completed!")

    finally:
        try:
            os.unlink(db_path)
        except:
            pass


def test_unified_service_coverage():
    print("\n" + "="*60)
    print("TESTING: Unified Service Coverage")
    print("="*60)

    db_path = setup_test_database()

    try:
        service = ClassAbilitiesService(db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT class_name, COUNT(*) FROM class_abilities GROUP BY class_name")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} abilities")

        cursor.execute("SELECT COUNT(*) FROM ability_scaling_formulas")
        formula_count = cursor.fetchone()[0]
        print(f"  Scaling formulas: {formula_count}")

        conn.close()

        print("\n[LEVEL SCALING] Testing rage uses by level...")
        for level in [1, 3, 6, 12, 17, 20]:
            uses = service.calculate_max_uses('rage', level)
            print(f"    Level {level}: {uses} rage uses")

        print("\n[LEVEL SCALING] Testing proficiency bonus by level...")
        for level in [1, 5, 9, 13, 17]:
            bonus = service._get_proficiency_bonus(level)
            print(f"    Level {level}: +{bonus} proficiency")

        print("\n[SUCCESS] Coverage test completed!")

    finally:
        try:
            os.unlink(db_path)
        except:
            pass


if __name__ == '__main__':
    print("\n" + "="*60)
    print("UNIFIED CLASS ABILITIES SERVICE - TEST SUITE")
    print("="*60)

    test_unified_service_coverage()
    test_barbarian_rage_unified()
    test_fighter_second_wind_unified()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)
