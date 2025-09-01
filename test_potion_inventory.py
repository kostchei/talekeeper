#!/usr/bin/env python3
"""
Test script to verify healing potion inventory detection.
"""

import sqlite3
import pytest

def test_potion_detection():
    """Test if healing potions are detected in character inventories."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()

    # Get all characters if table exists
    try:
        cursor.execute("SELECT id, name FROM characters")
    except sqlite3.OperationalError:
        pytest.skip("characters table not found")

    characters = cursor.fetchall()
    if not characters:
        pytest.skip("No characters found")

    print(f"Found {len(characters)} characters")
    print("-" * 50)
    
    for char_id, char_name in characters:
        print(f"\nCharacter: {char_name} (ID: {char_id})")
        
        # Check for healing potions
        cursor.execute("""
            SELECT item_name, quantity 
            FROM character_inventory 
            WHERE character_id = ? AND item_name LIKE '%Potion%'
        """, (char_id,))
        
        potions = cursor.fetchall()
        if potions:
            for item_name, quantity in potions:
                print(f"  - {item_name}: {quantity}")
        else:
            print(f"  - No potions found")
        
        # Specific check for exact match
        cursor.execute("""
            SELECT quantity FROM character_inventory 
            WHERE character_id = ? AND item_name = 'Potion of Healing' AND quantity > 0
        """, (char_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"  [YES] Has {result[0]} Potion of Healing (exact match)")
        else:
            print(f"  [NO] No 'Potion of Healing' found (exact match)")
    
    conn.close()

if __name__ == "__main__":
    test_potion_detection()