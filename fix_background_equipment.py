#!/usr/bin/env python3
"""
Fix background equipment names to match database.
"""

import sqlite3
import json

def fix_background_equipment():
    """Update background equipment names to match database."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Mapping from background names to corrected equipment
    background_fixes = {
        'Farmer': [
            "Carpenter's Tools", "Shovel", "Common Clothes", "Belt Pouch", 
            "Backpack", "Potion of Healing", "Rations"
        ],
        'Soldier': [
            "Spear", "Shortbow", "Arrows", "Gaming Set", "Healer's Kit", 
            "Quiver", "Traveler's Clothes"  
        ],
        'Acolyte': [
            "Calligrapher's Supplies", "Prayer Book", "Holy Symbol", 
            "Parchment", "Robe"
        ],
        'Sage': [
            "Quarterstaff", "Calligrapher's Supplies", "History Book", 
            "Parchment", "Robe"
        ]
    }
    
    for bg_name, equipment_list in background_fixes.items():
        cursor.execute(
            'UPDATE backgrounds SET equipment_option_a = ? WHERE name = ?', 
            (json.dumps(equipment_list), bg_name)
        )
        print(f"Updated {bg_name} background equipment")
    
    conn.commit()
    conn.close()
    print("Background equipment names fixed!")

if __name__ == "__main__":
    fix_background_equipment()