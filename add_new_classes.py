#!/usr/bin/env python3
"""
Add new classes (Barbarian, Paladin, Warlock, Wizard, Cleric) with equipment choices.
"""

import sqlite3
import json

def add_missing_equipment():
    """Add equipment items that don't exist yet."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Equipment needed for the new classes
    new_equipment = [
        # name, description, item_type, cost_gp, weight_lb, armor_class, armor_type, dex_bonus_max
        ("Scale Mail", "Medium armor made of overlapping scales", "armor", 50, 45.0, 14, "medium", 2),
        ("Warhammer", "Heavy war hammer", "weapon", 15, 2.0, None, None, None),
        ("Maul", "Heavy two-handed hammer", "weapon", 10, 10.0, None, None, None),
        ("Sickle", "Curved farming tool used as weapon", "weapon", 1, 2.0, None, None, None),
        ("Scimitar", "Curved one-handed sword", "weapon", 25, 3.0, None, None, None),
        ("Mace", "Heavy club with metal head", "weapon", 5, 4.0, None, None, None),
        ("Staff", "Simple wooden staff", "weapon", 2, 4.0, None, None, None),
        ("Arcane Focus", "Crystal or orb for focusing magic", "gear", 20, 1.0, None, None, None),
        ("Spellbook", "Book containing wizard spells", "gear", 50, 3.0, None, None, None),
        ("Shield", "Wooden shield with metal rim", "armor", 10, 6.0, None, None, None),
    ]
    
    for name, description, item_type, cost_gp, weight_lb, armor_class, armor_type, dex_bonus_max in new_equipment:
        # Check if item already exists
        cursor.execute("SELECT name FROM equipment WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"  Item '{name}' already exists, skipping")
            continue
        
        # Set weapon properties based on weapon type
        damage_dice = None
        damage_type = None
        weapon_properties = None
        
        if item_type == "weapon":
            weapon_stats = {
                "Warhammer": ("1d8", "bludgeoning", "versatile"),
                "Maul": ("2d6", "bludgeoning", "heavy,two-handed"), 
                "Sickle": ("1d4", "slashing", "light"),
                "Scimitar": ("1d6", "slashing", "finesse,light"),
                "Mace": ("1d6", "bludgeoning", ""),
                "Staff": ("1d6", "bludgeoning", "versatile"),
            }
            if name in weapon_stats:
                damage_dice, damage_type, weapon_properties = weapon_stats[name]
        
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
            'simple' if item_type == 'weapon' else None,
            damage_dice, damage_type, weapon_properties, None,
            None, None, None, None,
            armor_class, armor_type, dex_bonus_max, None, None,
            0
        ))
        
        print(f"  + Added '{name}'")
    
    conn.commit()
    conn.close()

def add_new_classes():
    """Add new classes with their equipment choices."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Class equipment choices
    class_choices = {
        'barbarian': [
            {
                'choice_group': 'armor',
                'choice_name': 'Armor Choice',
                'options': ['Scale Mail', 'Chain Mail', 'Unarmored']
            },
            {
                'choice_group': 'weapon',
                'choice_name': 'Primary Weapon',
                'options': ['Greataxe', 'Scimitar + Scimitar']
            }
        ],
        'paladin': [
            {
                'choice_group': 'armor',
                'choice_name': 'Armor Choice', 
                'options': ['Breastplate', 'Chain Mail']
            },
            {
                'choice_group': 'weapon',
                'choice_name': 'Weapon Choice',
                'options': ['Longsword + Shield', 'Warhammer + Shield']
            },
            {
                'choice_group': 'weapon2',
                'choice_name': 'Secondary Weapon',
                'options': ['Maul', 'Greatsword']
            }
        ],
        'warlock': [
            {
                'choice_group': 'armor',
                'choice_name': 'Armor Choice',
                'options': ['Studded Leather']
            },
            {
                'choice_group': 'weapon',
                'choice_name': 'Weapon Choice',
                'options': ['Spear', 'Sickle']
            },
            {
                'choice_group': 'gear',
                'choice_name': 'Magic Focus',
                'options': ['Arcane Focus']
            }
        ],
        'cleric': [
            {
                'choice_group': 'armor',
                'choice_name': 'Armor Choice',
                'options': ['Scale Mail']
            },
            {
                'choice_group': 'weapon',
                'choice_name': 'Weapon Choice',
                'options': ['Mace + Shield', 'Warhammer + Shield']
            },
            {
                'choice_group': 'gear',
                'choice_name': 'Holy Symbol',
                'options': ['Holy Symbol']
            }
        ],
        'wizard': [
            {
                'choice_group': 'gear',
                'choice_name': 'Arcane Focus',
                'options': ['Arcane Focus']
            },
            {
                'choice_group': 'gear2', 
                'choice_name': 'Spellbook',
                'options': ['Spellbook']
            },
            {
                'choice_group': 'weapon',
                'choice_name': 'Weapon Choice',
                'options': ['Staff', 'Dagger']
            }
        ]
    }
    
    for class_id, choices in class_choices.items():
        print(f"Adding equipment choices for {class_id}:")
        
        for choice in choices:
            cursor.execute("""
                INSERT OR REPLACE INTO class_equipment_choices (class_id, choice_group, choice_name, options)
                VALUES (?, ?, ?, ?)
            """, (
                class_id, 
                choice['choice_group'],
                choice['choice_name'],
                json.dumps(choice['options'])
            ))
            print(f"  + {choice['choice_name']}: {choice['options']}")
    
    conn.commit()
    conn.close()
    print("\nNew classes with equipment choices added successfully!")

if __name__ == "__main__":
    print("Adding missing equipment...")
    add_missing_equipment()
    print("\nAdding new classes...")
    add_new_classes()