# unsure
#utility
# unsure
import sqlite3
import uuid

def add_potions_to_character(character_id: str, potion_type: str = 'all', quantity: int = 1):
    """
    Add healing potions to a character's inventory.

    Args:
        character_id: The character's ID
        potion_type: 'healing', 'greater', 'superior', 'supreme', or 'all'
        quantity: Number of potions to add
    """

    potion_data = {
        'healing': ('Potion of Healing', 0.5, 50.0, 'Heals 2d4+2 HP'),
        'greater': ('Potion of Greater Healing', 0.5, 200.0, 'Heals 4d4+4 HP'),
        'superior': ('Potion of Superior Healing', 0.5, 2000.0, 'Heals 8d4+8 HP'),
        'supreme': ('Potion of Supreme Healing', 0.5, 20000.0, 'Heals 10d4+20 HP'),
    }

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    # Verify character exists
    cursor.execute("SELECT name FROM characters WHERE id = ?", (character_id,))
    result = cursor.fetchone()

    if not result:
        print(f"Error: Character '{character_id}' not found")
        conn.close()
        return

    char_name = result[0]
    print(f"\nAdding potions to character: {char_name} ({character_id})")

    # Add potions
    if potion_type == 'all':
        types_to_add = potion_data.keys()
    else:
        if potion_type not in potion_data:
            print(f"Error: Invalid potion type '{potion_type}'")
            print(f"Valid types: {', '.join(potion_data.keys())}, or 'all'")
            conn.close()
            return
        types_to_add = [potion_type]

    for ptype in types_to_add:
        name, weight, value, desc = potion_data[ptype]

        # Check if character already has this potion type
        cursor.execute("""
            SELECT id, quantity FROM character_inventory
            WHERE character_id = ? AND item_name = ?
        """, (character_id, name))

        result = cursor.fetchone()

        if result:
            # Update existing entry
            inv_id, current_qty = result
            new_qty = current_qty + quantity
            cursor.execute("""
                UPDATE character_inventory
                SET quantity = ?
                WHERE id = ?
            """, (new_qty, inv_id))
            print(f"  Updated {name}: {current_qty} -> {new_qty}")
        else:
            # Add new entry
            inv_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO character_inventory
                (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped)
                VALUES (?, ?, ?, 'consumable', ?, ?, ?, ?, 0)
            """, (inv_id, character_id, name, quantity, weight, desc, value))
            print(f"  Added {quantity}x {name}")

    conn.commit()
    conn.close()

    print("\nDone! The potion action card will automatically use the best available potion.")


def show_character_potions(character_id: str):
    """Display all healing potions a character has."""

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM characters WHERE id = ?", (character_id,))
    result = cursor.fetchone()

    if not result:
        print(f"Error: Character '{character_id}' not found")
        conn.close()
        return

    char_name = result[0]
    print(f"\nHealing potions for {char_name}:")
    print("-" * 60)

    cursor.execute("""
        SELECT item_name, quantity, value_gp
        FROM character_inventory
        WHERE character_id = ? AND item_name LIKE '%Healing%'
        ORDER BY value_gp DESC
    """, (character_id,))

    results = cursor.fetchall()

    if not results:
        print("  No healing potions in inventory")
    else:
        for name, qty, value in results:
            print(f"  {qty}x {name} ({value} gp)")

    conn.close()


def list_characters():
    """List all characters in the database."""

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, class_id, level FROM characters ORDER BY name")
    results = cursor.fetchall()

    print("\nAvailable Characters:")
    print("-" * 60)

    for char_id, name, class_id, level in results:
        print(f"  {name} (Level {level} {class_id})")
        print(f"    ID: {char_id}")

    conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("POTION INVENTORY MANAGER")
    print("=" * 60)

    # List characters
    list_characters()

    print("\n" + "=" * 60)
    print("USAGE EXAMPLES:")
    print("=" * 60)

    print("\n1. Add 3 basic healing potions to a character:")
    print("   add_potions_to_character('character_id', 'healing', 3)")

    print("\n2. Add 1 supreme healing potion:")
    print("   add_potions_to_character('character_id', 'supreme', 1)")

    print("\n3. Add 1 of each potion type:")
    print("   add_potions_to_character('character_id', 'all', 1)")

    print("\n4. Show character's potions:")
    print("   show_character_potions('character_id')")

    print("\n" + "=" * 60)
    print("\nTo use this script, uncomment one of the examples below:")
    print("=" * 60)

    # Example: Add potions to test character
    # add_potions_to_character('test_valerius', 'all', 2)
    # show_character_potions('test_valerius')
