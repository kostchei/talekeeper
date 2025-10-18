import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from talekeeper.core.game_engine_sqlite import GameEngineSQLite
from talekeeper.services.treasure_generator import TreasureGenerator

def test_treasure_generator():
    print("\n=== Testing Treasure Generator ===")

    print("\n1. Testing Gem Generation:")
    for _ in range(5):
        gem = TreasureGenerator.generate_gem(min_value=10, max_value=1000)
        print(f"  - {gem['name']}: {gem['value_gp']} GP, {gem['weight_lb']:.4f} lb")

    print("\n2. Testing Art Object Generation:")
    for _ in range(5):
        art = TreasureGenerator.generate_art_object(min_value=25, max_value=2500)
        print(f"  - {art['name']}: {art['value_gp']} GP, {art['weight_lb']:.2f} lb")

    print("\n3. Testing Gold to Treasure Conversion:")
    for gold_amount in [500, 1500, 3000, 5000]:
        print(f"\n  Converting {gold_amount} GP:")
        treasures, remaining = TreasureGenerator.convert_gold_to_treasure(gold_amount, cr=5.0)
        total_value = sum(t['value_gp'] for t in treasures)
        total_weight = sum(t['weight_lb'] for t in treasures)
        print(f"    Generated {len(treasures)} items worth {total_value} GP ({total_weight:.2f} lb)")
        print(f"    Remaining coins: {remaining} GP ({remaining/50:.1f} lb)")
        if treasures:
            for t in treasures[:3]:
                print(f"      - {t['name']} ({t['treasure_type']}): {t['value_gp']} GP")
            if len(treasures) > 3:
                print(f"      ... and {len(treasures) - 3} more items")

def test_bag_of_holding_system():
    print("\n=== Testing Bag of Holding System ===")

    game_engine = GameEngineSQLite('talekeeper.db')

    print("\n1. Checking for existing test character...")
    import sqlite3
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM characters LIMIT 1")
    result = cursor.fetchone()

    if not result:
        print("  No test character found. Please create a character first.")
        conn.close()
        return

    character_id = result[0]
    character_name = result[1]
    print(f"  Using character: {character_name} (ID: {character_id})")

    print("\n2. Checking for Bag of Holding...")
    has_bag = game_engine.character_has_bag_of_holding(character_id)
    print(f"  Has Bag of Holding: {has_bag}")

    if not has_bag:
        print("\n  Adding Bag of Holding to character...")
        cursor.execute("""
            INSERT INTO character_inventory
            (id, character_id, item_name, item_type, quantity, weight_lb)
            VALUES (?, ?, 'Bag of Holding', 'wondrous', 1, 5.0)
        """, (f"{character_id}_bag_of_holding", character_id))
        conn.commit()
        print("  Bag of Holding added!")
        has_bag = True

    print("\n3. Testing gold addition with bag...")
    test_amounts = [100, 600, 2000]
    for amount in test_amounts:
        print(f"\n  Adding {amount} GP:")
        weight = amount / 50.0
        success = game_engine.add_gold_to_character_sync(character_id, amount)
        if success:
            print(f"    Success! ({weight:.1f} lb, auto-stored based on weight)")
        else:
            print(f"    Failed!")

    print("\n4. Testing treasure item addition...")
    test_gem = TreasureGenerator.generate_gem(100, 1000)
    print(f"  Adding gem: {test_gem['name']} ({test_gem['value_gp']} GP)")
    success = game_engine.add_treasure_to_character_sync(character_id, test_gem)
    print(f"    Success: {success}")

    test_art = TreasureGenerator.generate_art_object(250, 2500)
    print(f"  Adding art: {test_art['name']} ({test_art['value_gp']} GP)")
    success = game_engine.add_treasure_to_character_sync(character_id, test_art)
    print(f"    Success: {success}")

    print("\n5. Checking inventory contents...")
    cursor.execute("""
        SELECT item_name, treasure_type, quantity, weight_lb, stored_in_bag, unit_value_gp
        FROM character_inventory
        WHERE character_id = ?
        ORDER BY stored_in_bag DESC, item_type
    """, (character_id,))

    print("\n  Items in Bag of Holding:")
    for row in cursor.fetchall():
        name, ttype, qty, weight, in_bag, unit_val = row
        if in_bag:
            if ttype == 'coins':
                print(f"    - {name}: {qty} coins ({weight:.2f} lb)")
            else:
                print(f"    - {name} ({ttype}): {qty}x @ {unit_val} GP ({weight:.2f} lb)")

    print("\n  Items on Person:")
    cursor.execute("""
        SELECT item_name, treasure_type, quantity, weight_lb, stored_in_bag, unit_value_gp
        FROM character_inventory
        WHERE character_id = ? AND stored_in_bag = 0
        ORDER BY item_type
    """, (character_id,))

    for row in cursor.fetchall():
        name, ttype, qty, weight, in_bag, unit_val = row
        if ttype == 'coins':
            print(f"    - {name}: {qty} coins ({weight:.2f} lb)")
        else:
            print(f"    - {name} ({ttype}): {qty}x @ {unit_val} GP ({weight:.2f} lb)")

    print("\n6. Checking bag weight capacity...")
    bag_weight = game_engine.get_bag_of_holding_weight(character_id)
    print(f"  Total weight in bag: {bag_weight:.2f} lb / 500 lb capacity")
    print(f"  Remaining capacity: {500 - bag_weight:.2f} lb")

    conn.close()
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_treasure_generator()
    test_bag_of_holding_system()
