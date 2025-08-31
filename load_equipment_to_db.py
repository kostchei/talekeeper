"""
Load equipment.json data into the equipment database table.
Run this to populate the equipment table with all D&D items.
"""

import sqlite3
import json
import os

def load_equipment_to_db():
    """Load equipment.json data into the database."""
    
    # Load equipment.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    equipment_file = os.path.join(current_dir, "data", "equipment.json")
    
    with open(equipment_file, 'r') as f:
        equipment_list = json.load(f)
    
    print(f"Loaded {len(equipment_list)} items from equipment.json")
    
    # Connect to database
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Create equipment table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            item_type TEXT NOT NULL,
            rarity TEXT,
            cost_gp REAL NOT NULL DEFAULT 0,
            weight_lb REAL NOT NULL DEFAULT 0.0,
            
            -- Weapon properties (nullable for non-weapons)
            weapon_category TEXT,
            damage_dice TEXT,
            damage_type TEXT,
            weapon_properties TEXT,  -- JSON array
            weapon_mastery TEXT,
            range_normal INTEGER,
            range_long INTEGER,
            versatile_damage TEXT,
            ammunition TEXT,
            
            -- Armor properties (nullable for non-armor)
            armor_class INTEGER,
            armor_type TEXT,
            dex_bonus_max INTEGER,  -- NULL means unlimited
            strength_requirement INTEGER,
            stealth_disadvantage BOOLEAN,
            
            -- General properties
            is_magical BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_name ON equipment(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_item_type ON equipment(item_type)")
    
    # Clear existing data
    cursor.execute("DELETE FROM equipment")
    
    # Insert all equipment
    items_inserted = 0
    for item in equipment_list:
        try:
            # Extract weapon properties
            weapon_category = item.get('weapon_category')
            damage_dice = item.get('damage_dice')
            damage_type = item.get('damage_type')
            weapon_properties = json.dumps(item.get('weapon_properties', [])) if item.get('weapon_properties') else None
            weapon_mastery = item.get('weapon_mastery')
            versatile_damage = item.get('versatile_damage')
            ammunition = item.get('ammunition')
            
            # Parse range if present
            range_normal, range_long = None, None
            if 'range' in item:
                range_str = item['range']
                if '/' in range_str:
                    range_parts = range_str.split('/')
                    range_normal = int(range_parts[0])
                    range_long = int(range_parts[1])
            
            # Extract armor properties
            armor_props = item.get('armor_properties', {})
            armor_class = armor_props.get('armor_class')
            armor_type = armor_props.get('armor_type')
            dex_bonus_max = armor_props.get('dex_bonus_max')
            strength_requirement = armor_props.get('strength_requirement')
            stealth_disadvantage = armor_props.get('stealth_disadvantage')
            
            # General properties
            is_magical = item.get('is_magical', False)
            
            cursor.execute("""
                INSERT INTO equipment (
                    name, description, item_type, rarity, cost_gp, weight_lb,
                    weapon_category, damage_dice, damage_type, weapon_properties, weapon_mastery,
                    range_normal, range_long, versatile_damage, ammunition,
                    armor_class, armor_type, dex_bonus_max, strength_requirement, stealth_disadvantage,
                    is_magical
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item['name'], item.get('description', ''), item['item_type'], item.get('rarity', 'common'),
                item.get('cost_gp', 0), item.get('weight_lb', 0),
                weapon_category, damage_dice, damage_type, weapon_properties, weapon_mastery,
                range_normal, range_long, versatile_damage, ammunition,
                armor_class, armor_type, dex_bonus_max, strength_requirement, stealth_disadvantage,
                is_magical
            ))
            
            items_inserted += 1
            
        except Exception as e:
            print(f"Error inserting {item.get('name', 'unknown')}: {e}")
    
    conn.commit()
    print(f"Successfully inserted {items_inserted} equipment items into database")
    
    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM equipment")
    count = cursor.fetchone()[0]
    print(f"Total equipment items in database: {count}")
    
    # Show some examples
    cursor.execute("SELECT name, item_type FROM equipment WHERE item_type = 'armor' LIMIT 5")
    print("\nSample armor items:")
    for row in cursor.fetchall():
        print(f"  {row[0]} ({row[1]})")
    
    cursor.execute("SELECT name, item_type FROM equipment WHERE item_type = 'weapon' LIMIT 5")
    print("\nSample weapon items:")
    for row in cursor.fetchall():
        print(f"  {row[0]} ({row[1]})")
    
    conn.close()
    print("\nEquipment database populated successfully!")

if __name__ == "__main__":
    load_equipment_to_db()