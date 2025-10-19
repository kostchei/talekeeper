# core
#utility
# core
import sqlite3
import re

RARITY_CREATION_COSTS = {
    'common': 50,
    'uncommon': 200,
    'rare': 2000,
    'very rare': 20000,
    'legendary': 100000
}

CONSUMABLE_ITEM_TYPES = ['consumable', 'potion', 'scroll']

def get_base_item_cost(cursor, magic_item_name):
    patterns = [
        (r'\+\d+\s+(.+)', lambda m: m.group(1)),
        (r'(.+?)\s+\+\d+', lambda m: m.group(1)),
        (r'(.+?)\s+of\s+', lambda m: m.group(1)),
    ]

    for pattern, extractor in patterns:
        match = re.match(pattern, magic_item_name, re.IGNORECASE)
        if match:
            base_name = extractor(match)
            cursor.execute(
                "SELECT cost_gp FROM equipment WHERE name = ? AND is_magical = 0",
                (base_name,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]

    return 0

def calculate_magic_item_price(cursor, item_id, name, rarity, current_cost, item_type):
    rarity_lower = rarity.lower() if rarity else 'common'

    if rarity_lower not in RARITY_CREATION_COSTS:
        print(f"Unknown rarity '{rarity}' for {name}, skipping")
        return None

    creation_cost = RARITY_CREATION_COSTS[rarity_lower]

    is_consumable = item_type in CONSUMABLE_ITEM_TYPES

    if is_consumable:
        multiplier = 1
    else:
        multiplier = 2

    base_cost = get_base_item_cost(cursor, name)

    final_price = base_cost + (creation_cost * multiplier)

    return final_price

def update_magic_item_pricing(db_path='../../talekeeper.db', dry_run=True):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, rarity, cost_gp, item_type
        FROM equipment
        WHERE is_magical = 1
        ORDER BY name
    """)

    items = cursor.fetchall()

    print(f"Found {len(items)} magical items\n")
    print("=" * 80)

    updates = []

    for item_id, name, rarity, current_cost, item_type in items:
        new_price = calculate_magic_item_price(cursor, item_id, name, rarity, current_cost, item_type)

        if new_price is None:
            continue

        is_consumable = item_type in CONSUMABLE_ITEM_TYPES
        multiplier = 1 if is_consumable else 2
        base_cost = get_base_item_cost(cursor, name)
        creation_cost = RARITY_CREATION_COSTS.get(rarity.lower(), 0)

        print(f"{name}")
        print(f"  Rarity: {rarity}")
        print(f"  Type: {item_type} {'(CONSUMABLE)' if is_consumable else ''}")
        print(f"  Base item cost: {base_cost} gp")
        print(f"  Creation cost: {creation_cost} gp x {multiplier}")
        print(f"  Old price: {current_cost} gp")
        print(f"  New price: {new_price} gp")
        print()

        updates.append((new_price, item_id))

    print("=" * 80)
    print(f"\nTotal items to update: {len(updates)}")

    if not dry_run:
        cursor.executemany(
            "UPDATE equipment SET cost_gp = ? WHERE id = ?",
            updates
        )
        conn.commit()
        print(f"\nDatabase updated successfully!")
    else:
        print(f"\nDRY RUN - No changes made to database")
        print(f"Run with dry_run=False to apply changes")

    conn.close()

if __name__ == '__main__':
    import sys

    dry_run = '--apply' not in sys.argv

    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("Add --apply flag to update the database\n")
    else:
        print("APPLY MODE - Database will be updated\n")

    update_magic_item_pricing(dry_run=dry_run)
