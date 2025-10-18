import sys
sys.path.insert(0, 'src')

from talekeeper.services.downtime_activities import DowntimeActivityService
import sqlite3


def test_inspiration_on_load():
    print("Testing inspiration initialization on character load...")

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.name, c.inspiration_uses_current, c.inspiration_uses_max
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id
        WHERE s.is_occupied = 1
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        print("No characters found in database")
        return False

    char_id, char_name, insp_current, insp_max = row
    print(f"Character: {char_name}")
    print(f"  Inspiration: {insp_current}/{insp_max}")

    if insp_current >= 1 and insp_max >= 1:
        print("  SUCCESS: Character has at least 1 inspiration")
        return True
    else:
        print("  FAILED: Character does not have 1 inspiration")
        return False


def test_downtime_service():
    print("\nTesting downtime activities service...")

    service = DowntimeActivityService('talekeeper.db')

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.name, c.level
        FROM characters c
        JOIN save_slots s ON c.save_slot_id = s.id
        WHERE s.is_occupied = 1
        LIMIT 1
    """)

    row = cursor.fetchone()
    if not row:
        print("No characters found")
        conn.close()
        return False

    char_id, char_name, char_level = row

    cursor.execute("""
        SELECT quantity FROM character_inventory
        WHERE character_id = ? AND item_name = 'Gold Pieces'
    """, (char_id,))

    gold_row = cursor.fetchone()
    current_gold = gold_row[0] if gold_row else 0

    print(f"Character: {char_name} (Level {char_level})")
    print(f"  Gold: {current_gold}")

    prayer_cost = (5 * char_level) + (10 * 2)
    print(f"\n  Prayer cost: {prayer_cost} gp")

    if current_gold >= prayer_cost:
        cursor.execute("""
            UPDATE character_inventory
            SET quantity = quantity + 1000
            WHERE character_id = ? AND item_name = 'Gold Pieces'
        """, (char_id,))
        conn.commit()
        print(f"  Added 1000 gold for testing")

    conn.close()

    print(f"\n  Testing prayer activity...")
    result = service.prayer(char_id, char_level)

    if result['success']:
        print(f"  SUCCESS: Prayer completed")
        print(f"    Gold spent: {result['gold_spent']}")
        print(f"    Inspiration gained: {result['inspiration_gained']}")
        print(f"    New gold: {result['new_gold']}")
        return True
    else:
        print(f"  FAILED: {result.get('error', 'Unknown error')}")
        return False


def main():
    print("=" * 60)
    print("DOWNTIME & INSPIRATION SYSTEM TEST")
    print("=" * 60)

    test1 = test_inspiration_on_load()
    test2 = test_downtime_service()

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Inspiration initialization: {'PASS' if test1 else 'FAIL'}")
    print(f"Downtime activities: {'PASS' if test2 else 'FAIL'}")

    if test1 and test2:
        print("\nAll tests PASSED!")
        return 0
    else:
        print("\nSome tests FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
