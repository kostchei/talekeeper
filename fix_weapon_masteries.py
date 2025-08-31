#!/usr/bin/env python3
"""
Fix weapon masteries for existing characters.
Add default weapon masteries based on Fighter class.
"""

import sqlite3

def fix_weapon_masteries():
    """Add weapon masteries for existing Fighter characters."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get all Fighter characters
    cursor.execute("""
        SELECT c.id, c.name 
        FROM characters c 
        WHERE c.class_id LIKE '%fighter%' OR c.class_id = 'Fighter'
    """)
    
    fighters = cursor.fetchall()
    print(f"Found {len(fighters)} Fighter characters")
    
    weapon_mastery_map = {
        "Dagger": "nick", "Handaxe": "vex", "Javelin": "slow",
        "Light Hammer": "nick", "Scimitar": "nick", "Shortsword": "vex",
        "Battleaxe": "topple", "Flail": "sap", "Glaive": "graze",
        "Greataxe": "cleave", "Greatsword": "graze", "Halberd": "cleave",
        "Lance": "topple", "Longsword": "sap", "Maul": "topple",
        "Morningstar": "sap", "Pike": "push", "Rapier": "vex",
        "Trident": "topple", "War Pick": "sap", "Warhammer": "push", "Whip": "slow"
    }
    
    for fighter in fighters:
        character_id, character_name = fighter
        print(f"\nProcessing {character_name} (ID: {character_id})")
        
        # Default Fighter weapon masteries (common starting weapons)
        default_weapons = ["Greatsword", "Longsword", "Handaxe"]  # 3 masteries for level 1
        
        for weapon_name in default_weapons:
            mastery_type = weapon_mastery_map.get(weapon_name)
            if mastery_type:
                # Check if already exists
                cursor.execute("""
                    SELECT 1 FROM character_weapon_masteries 
                    WHERE character_id = ? AND weapon_name = ?
                """, (character_id, weapon_name))
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_type)
                        VALUES (?, ?, ?)
                    """, (character_id, weapon_name, mastery_type))
                    print(f"  Added: {weapon_name} -> {mastery_type}")
                else:
                    print(f"  Already exists: {weapon_name} -> {mastery_type}")
    
    conn.commit()
    conn.close()
    print("\nWeapon masteries migration complete!")

if __name__ == "__main__":
    fix_weapon_masteries()