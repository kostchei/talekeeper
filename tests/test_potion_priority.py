#test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import sqlite3
from talekeeper.ui.action_cards.action_panel import ActionPanel

def test_potion_priority():
    """Test that the best healing potion is selected correctly."""

    print("Testing potion priority system...")

    # Create a test character in database
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()

    # Use an existing test character to avoid table constraint issues
    cursor.execute("SELECT id FROM characters LIMIT 1")
    result = cursor.fetchone()

    if not result:
        print("ERROR: No characters in database. Please run the application first to initialize data.")
        return False

    test_char_id = result[0]
    print(f"Using test character: {test_char_id}")

    # Clean up any existing test potion data
    cursor.execute("""
        DELETE FROM character_inventory
        WHERE character_id = ?
        AND item_name LIKE '%Potion%Healing%'
    """, (test_char_id,))
    conn.commit()

    # Test 1: No potions
    print("\n[Test 1] No potions available")
    panel = ActionPanel()
    result = panel._get_best_healing_potion(test_char_id)
    assert result is None, "Should return None when no potions available"
    print("  PASS: Returns None when no potions")

    # Test 2: Only basic Potion of Healing
    print("\n[Test 2] Only basic Potion of Healing")
    cursor.execute("""
        INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, value_gp)
        VALUES ('inv1', ?, 'Potion of Healing', 'consumable', 3, 0.5, 50.0)
    """, (test_char_id,))
    conn.commit()

    result = panel._get_best_healing_potion(test_char_id)
    assert result is not None, "Should find basic potion"
    assert result[0] == 'Potion of Healing', f"Should find basic potion, got {result[0]}"
    assert result[1:] == (2, 4, 2), f"Should be 2d4+2, got {result[1:]}"
    print(f"  PASS: Found {result[0]} with {result[1]}d{result[2]}+{result[3]}")

    # Test 3: Add Greater Healing Potion
    print("\n[Test 3] Add Greater Healing Potion")
    cursor.execute("""
        INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, value_gp)
        VALUES ('inv2', ?, 'Potion of Greater Healing', 'consumable', 2, 0.5, 200.0)
    """, (test_char_id,))
    conn.commit()

    result = panel._get_best_healing_potion(test_char_id)
    assert result is not None, "Should find greater potion"
    assert result[0] == 'Potion of Greater Healing', f"Should prioritize greater potion, got {result[0]}"
    assert result[1:] == (4, 4, 4), f"Should be 4d4+4, got {result[1:]}"
    print(f"  PASS: Found {result[0]} with {result[1]}d{result[2]}+{result[3]}")

    # Test 4: Add Superior Healing Potion
    print("\n[Test 4] Add Superior Healing Potion")
    cursor.execute("""
        INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, value_gp)
        VALUES ('inv3', ?, 'Potion of Superior Healing', 'consumable', 1, 0.5, 2000.0)
    """, (test_char_id,))
    conn.commit()

    result = panel._get_best_healing_potion(test_char_id)
    assert result is not None, "Should find superior potion"
    assert result[0] == 'Potion of Superior Healing', f"Should prioritize superior potion, got {result[0]}"
    assert result[1:] == (8, 4, 8), f"Should be 8d4+8, got {result[1:]}"
    print(f"  PASS: Found {result[0]} with {result[1]}d{result[2]}+{result[3]}")

    # Test 5: Add Supreme Healing Potion
    print("\n[Test 5] Add Supreme Healing Potion")
    cursor.execute("""
        INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, value_gp)
        VALUES ('inv4', ?, 'Potion of Supreme Healing', 'consumable', 1, 0.5, 20000.0)
    """, (test_char_id,))
    conn.commit()

    result = panel._get_best_healing_potion(test_char_id)
    assert result is not None, "Should find supreme potion"
    assert result[0] == 'Potion of Supreme Healing', f"Should prioritize supreme potion, got {result[0]}"
    assert result[1:] == (10, 4, 20), f"Should be 10d4+20, got {result[1:]}"
    print(f"  PASS: Found {result[0]} with {result[1]}d{result[2]}+{result[3]}")

    # Test 6: Consume supreme potion, should fall back to superior
    print("\n[Test 6] Consume supreme potion, fall back to superior")
    panel._consume_healing_potion(test_char_id, 'Potion of Supreme Healing')

    result = panel._get_best_healing_potion(test_char_id)
    assert result is not None, "Should find superior potion after consuming supreme"
    assert result[0] == 'Potion of Superior Healing', f"Should fall back to superior, got {result[0]}"
    print(f"  PASS: Fell back to {result[0]} with {result[1]}d{result[2]}+{result[3]}")

    # Test 7: Consume superior potion, should fall back to greater
    print("\n[Test 7] Consume superior potion, fall back to greater")
    panel._consume_healing_potion(test_char_id, 'Potion of Superior Healing')

    result = panel._get_best_healing_potion(test_char_id)
    assert result is not None, "Should find greater potion after consuming superior"
    assert result[0] == 'Potion of Greater Healing', f"Should fall back to greater, got {result[0]}"
    print(f"  PASS: Fell back to {result[0]} with {result[1]}d{result[2]}+{result[3]}")

    # Test 8: Consume all greater potions, should fall back to basic
    print("\n[Test 8] Consume all greater potions, fall back to basic")
    panel._consume_healing_potion(test_char_id, 'Potion of Greater Healing')
    panel._consume_healing_potion(test_char_id, 'Potion of Greater Healing')

    result = panel._get_best_healing_potion(test_char_id)
    assert result is not None, "Should find basic potion after consuming all greater"
    assert result[0] == 'Potion of Healing', f"Should fall back to basic, got {result[0]}"
    print(f"  PASS: Fell back to {result[0]} with {result[1]}d{result[2]}+{result[3]}")

    # Cleanup - remove test potions only
    cursor.execute("""
        DELETE FROM character_inventory
        WHERE character_id = ?
        AND item_name LIKE '%Potion%Healing%'
    """, (test_char_id,))
    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("ALL POTION PRIORITY TESTS PASSED!")
    print("="*60)
    return True

if __name__ == '__main__':
    try:
        test_potion_priority()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
