#!/usr/bin/env python3
"""
Add basic adventuring gear to equipment database.
"""

import sqlite3

def add_adventuring_gear():
    """Add missing adventuring gear items."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Basic adventuring gear that backgrounds need
    gear_items = [
        # name, description, item_type, cost_gp, weight_lb
        ("Thieves' Tools", "Pick locks (DC 15) or disarm traps (DC 15)", "tool", 25, 1.0),
        ("Crowbar", "Iron crowbar, useful for breaking and entering", "gear", 2, 5.0), 
        ("Pouch", "Small pouch for carrying coins and small items", "gear", 0.5, 1.0),
        ("Traveler's Clothes", "Sturdy clothes for travel and adventure", "gear", 2, 4.0),
        ("Common Clothes", "Everyday clothing", "gear", 0.5, 3.0),
        ("Belt Pouch", "Small pouch worn on belt", "gear", 0.5, 1.0),
        ("Backpack", "Leather backpack for carrying gear", "gear", 2, 5.0),
        ("Bedroll", "Blankets and a sleeping pad", "gear", 1, 7.0),
        ("Rope", "Hemp rope, 50 feet", "gear", 1, 5.0),
        ("Rations", "One day's food for travel", "gear", 0.5, 2.0),
        ("Waterskin", "Leather container for water", "gear", 2, 5.0),
        ("Tinderbox", "Flint, fire steel, and tinder for making fire", "gear", 0.5, 1.0),
        ("Torch", "Wooden torch that burns for 1 hour", "gear", 0.01, 1.0),
        ("Blanket", "Wool blanket", "gear", 0.5, 3.0),
        ("Shovel", "Iron shovel for digging", "gear", 2, 5.0),
        
        # Tools and kits
        ("Carpenter's Tools", "Tools for woodworking and construction", "tool", 8, 6.0),
        ("Calligrapher's Supplies", "Ink, quills, and paper for fine writing", "tool", 10, 5.0),
        ("Healer's Kit", "Bandages and herbs for treating wounds", "gear", 5, 3.0),
        ("Gaming Set", "Dice, cards, or other games", "gear", 1, 1.0),
        
        # Books and papers
        ("Prayer Book", "Book of religious prayers and texts", "gear", 25, 3.0),
        ("History Book", "Scholarly book of historical knowledge", "gear", 25, 5.0),
        ("Parchment", "Writing material made from animal skin", "gear", 0.1, 0.0),
        
        # Religious items
        ("Holy Symbol", "Religious symbol worn as amulet", "gear", 5, 1.0),
        ("Robe", "Long flowing garment", "gear", 1, 4.0),
        
        # Ammunition and containers
        ("Arrows", "20 arrows for bow", "gear", 1, 1.0),
        ("Quiver", "Container for arrows", "gear", 1, 1.0),
        
        # Potions
        ("Potion of Healing", "Restores 2d4+2 hit points", "potion", 50, 0.5),
    ]
    
    for name, description, item_type, cost_gp, weight_lb in gear_items:
        # Check if item already exists
        cursor.execute("SELECT name FROM equipment WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"  Item '{name}' already exists, skipping")
            continue
            
        cursor.execute("""
            INSERT INTO equipment (
                name, description, item_type, rarity, cost_gp, weight_lb,
                weapon_category, damage_dice, damage_type, weapon_properties, weapon_mastery,
                range_normal, range_long, versatile_damage, ammunition,
                armor_class, armor_type, dex_bonus_max, strength_requirement, stealth_disadvantage,
                is_magical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, description, item_type, 'common', cost_gp, weight_lb,
            None, None, None, None, None,  # weapon fields
            None, None, None, None,  # more weapon fields  
            None, None, None, None, None,  # armor fields
            0  # is_magical
        ))
        
        print(f"  + Added '{name}'")
    
    conn.commit()
    conn.close()
    print("Adventuring gear added successfully!")

if __name__ == "__main__":
    add_adventuring_gear()