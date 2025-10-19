#test
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.loot_drop_service import LootDropService

def create_test_character(class_name, strength=15, dexterity=10, constitution=14):
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO characters
        (id, name, class_id, race_id, level, strength, dexterity, constitution, intelligence, wisdom, charisma, hit_points_max, hit_points_current)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f'test_{class_name}',
        f'Test {class_name}',
        class_name.lower(),
        'human',
        5,
        strength,
        dexterity,
        constitution,
        10,
        10,
        10,
        50,
        50
    ))

    conn.commit()
    conn.close()

    return f'test_{class_name}'

def clean_test_character(character_id):
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM character_inventory WHERE character_id = ?", (character_id,))
    cursor.execute("DELETE FROM characters WHERE id = ?", (character_id,))

    conn.commit()
    conn.close()

def test_bis_drops():
    loot_service = LootDropService('talekeeper.db')

    print("=" * 80)
    print("BiS LOOT DROP SYSTEM TEST")
    print("=" * 80)

    test_classes = [
        ('Fighter', 'fighter', {'strength': 18, 'dexterity': 10, 'constitution': 16}),
        ('Fighter DEX', 'fighter', {'strength': 10, 'dexterity': 18, 'constitution': 14}),
        ('Barbarian', 'barbarian', {'strength': 18, 'dexterity': 14, 'constitution': 16}),
        ('Wizard', 'wizard', {'strength': 8, 'dexterity': 14, 'constitution': 12}),
    ]

    rarities = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary']

    for class_label, class_name, stats in test_classes:
        print(f"\n{'=' * 80}")
        print(f"Testing: {class_label}")
        print(f"Stats: STR={stats['strength']} DEX={stats['dexterity']} CON={stats['constitution']}")
        print(f"{'=' * 80}")

        character_id = create_test_character(
            class_name,
            strength=stats['strength'],
            dexterity=stats['dexterity'],
            constitution=stats['constitution']
        )

        try:
            character_data = {
                'id': character_id,
                'class_name': class_name,
                'strength': stats['strength'],
                'dexterity': stats['dexterity'],
                'constitution': stats['constitution']
            }

            class_build = loot_service.get_character_build(character_data)
            print(f"\nDetermined Build: {class_build}")

            for rarity in rarities:
                print(f"\n--- {rarity} Tier ---")

                drops = []
                for drop_num in range(3):
                    item = loot_service.drop_loot(character_id, character_data, rarity)

                    if item:
                        drops.append(item['name'])
                        print(f"  Drop {drop_num + 1}: {item['name']}")

                        conn = sqlite3.connect('talekeeper.db')
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO character_inventory
                            (character_id, item_name, item_type, quantity, equipped)
                            VALUES (?, ?, ?, 1, 0)
                        """, (character_id, item['name'], item.get('item_type', 'weapon')))
                        conn.commit()
                        conn.close()
                    else:
                        print(f"  Drop {drop_num + 1}: No item available")
                        break

                if not drops:
                    print("  WARNING: No drops available!")
                elif len(drops) < 3:
                    print(f"  Note: Only {len(drops)} unique items available")

            inventory = loot_service.get_player_inventory(character_id)
            print(f"\nFinal Inventory Count: {len(inventory)} items")

        finally:
            clean_test_character(character_id)

    print(f"\n{'=' * 80}")
    print("TEST FALLBACK TO 'OTHER' CATEGORY")
    print(f"{'=' * 80}")

    character_id = create_test_character('fighter', strength=18, dexterity=10, constitution=16)

    try:
        character_data = {
            'id': character_id,
            'class_name': 'fighter',
            'strength': 18,
            'dexterity': 10,
            'constitution': 16
        }

        print("\nGiving Fighter all BiS Common items...")

        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT item_name
            FROM best_in_slot_items
            WHERE class_build = 'Fighter' AND rarity = 'Common'
        """)

        bis_items = [row[0] for row in cursor.fetchall()]
        print(f"BiS Common items: {bis_items}")

        for item_name in bis_items:
            cursor.execute("""
                INSERT INTO character_inventory
                (character_id, item_name, item_type, quantity, equipped)
                VALUES (?, ?, 'weapon', 1, 0)
            """, (character_id, item_name))

        conn.commit()
        conn.close()

        print("\nTrying to drop more Common items (should use 'Other' category):")
        for i in range(3):
            item = loot_service.drop_loot(character_id, character_data, 'Common')
            if item:
                print(f"  Drop {i + 1}: {item['name']} (from 'Other' category)")
            else:
                print(f"  Drop {i + 1}: No more items available")
                break

    finally:
        clean_test_character(character_id)

    print(f"\n{'=' * 80}")
    print("TEST COMPLETE")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    test_bis_drops()