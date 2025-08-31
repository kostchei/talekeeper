#!/usr/bin/env python3
"""
Create weapon mastery system with proper database tables.
"""

import sqlite3

def create_mastery_tables():
    """Create weapon mastery tables."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Weapon mastery definitions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weapon_masteries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            trigger_type TEXT NOT NULL, -- 'on_hit', 'on_miss', 'on_attack'
            description TEXT NOT NULL,
            requires_save BOOLEAN DEFAULT FALSE,
            save_ability TEXT, -- 'constitution', 'dexterity', etc.
            effect_data TEXT -- JSON for complex effects
        )
    """)
    
    # Weapon mastery properties for each weapon
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weapon_mastery_properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weapon_name TEXT NOT NULL,
            mastery_name TEXT NOT NULL,
            FOREIGN KEY (mastery_name) REFERENCES weapon_masteries(name)
        )
    """)
    
    conn.commit()
    conn.close()

def populate_masteries():
    """Populate weapon masteries with D&D 2024 data."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Mastery definitions
    masteries = [
        {
            'name': 'Cleave',
            'trigger_type': 'on_hit',
            'description': 'If you hit a creature with a melee attack roll using this weapon, you can make a melee attack roll with the weapon against a second creature within 5 feet of the first that is also within your reach. On a hit, the second creature takes the weapon\'s damage, but don\'t add your ability modifier to that damage unless that modifier is negative. You can make this extra attack only once per turn.',
            'requires_save': False
        },
        {
            'name': 'Graze',
            'trigger_type': 'on_miss', 
            'description': 'If your attack roll with this weapon misses a creature, you can deal damage to that creature equal to the ability modifier you used to make the attack roll. This damage is the same type dealt by the weapon, and the damage can be increased only by increasing the ability modifier.',
            'requires_save': False
        },
        {
            'name': 'Nick',
            'trigger_type': 'on_attack',
            'description': 'When you make the extra attack of the Light property, you can make it as part of the Attack action instead of as a Bonus Action. You can make this extra attack only once per turn.',
            'requires_save': False
        },
        {
            'name': 'Push',
            'trigger_type': 'on_hit',
            'description': 'If you hit a creature with this weapon, you can push the creature up to 10 feet straight away from yourself if it is Large or smaller.',
            'requires_save': False
        },
        {
            'name': 'Sap',
            'trigger_type': 'on_hit',
            'description': 'If you hit a creature with this weapon, that creature has Disadvantage on its next attack roll before the start of your next turn.',
            'requires_save': False
        },
        {
            'name': 'Slow',
            'trigger_type': 'on_hit',
            'description': 'If you hit a creature with this weapon and deal damage to it, you can reduce its Speed by 10 feet until the start of your next turn. If the creature is hit more than once by weapons that have this property, the Speed reduction doesn\'t exceed 10 feet.',
            'requires_save': False
        },
        {
            'name': 'Topple',
            'trigger_type': 'on_hit',
            'description': 'If you hit a creature with this weapon, you can force the creature to make a Constitution saving throw (DC 8 plus the ability modifier used to make the attack roll and your Proficiency Bonus). On a failed save, the creature has the Prone condition.',
            'requires_save': True,
            'save_ability': 'constitution'
        },
        {
            'name': 'Vex',
            'trigger_type': 'on_hit',
            'description': 'If you hit a creature with this weapon and deal damage to the creature, you have Advantage on your next attack roll against that creature before the end of your next turn.',
            'requires_save': False
        }
    ]
    
    for mastery in masteries:
        cursor.execute("""
            INSERT OR REPLACE INTO weapon_masteries 
            (name, trigger_type, description, requires_save, save_ability)
            VALUES (?, ?, ?, ?, ?)
        """, (
            mastery['name'],
            mastery['trigger_type'], 
            mastery['description'],
            mastery['requires_save'],
            mastery.get('save_ability')
        ))
        print(f"Added mastery: {mastery['name']}")
    
    conn.commit()
    conn.close()

def populate_weapon_masteries():
    """Assign masteries to weapons."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Weapon -> Mastery mapping
    weapon_masteries = {
        # Simple Melee Weapons
        "Club": "Slow",
        "Dagger": "Nick", 
        "Dart": "Vex",
        "Handaxe": "Vex",
        "Javelin": "Slow",
        "Light Hammer": "Nick",
        "Mace": "Sap", 
        "Quarterstaff": "Topple",
        "Sickle": "Nick",
        "Spear": "Sap",
        
        # Simple Ranged Weapons
        "Light Crossbow": "Slow",
        "Shortbow": "Vex",
        "Sling": "Slow",
        
        # Martial Melee Weapons
        "Battleaxe": "Topple",
        "Flail": "Sap", 
        "Glaive": "Graze",
        "Greataxe": "Cleave",
        "Greatsword": "Graze",
        "Halberd": "Cleave",
        "Lance": "Topple",
        "Longsword": "Sap",
        "Maul": "Topple",
        "Morningstar": "Sap",
        "Pike": "Push",
        "Rapier": "Vex",
        "Scimitar": "Nick",
        "Shortsword": "Vex", 
        "Trident": "Topple",
        "War Pick": "Sap",
        "Warhammer": "Push",
        "Whip": "Slow",
        
        # Martial Ranged Weapons
        "Hand Crossbow": "Vex",
        "Heavy Crossbow": "Push",
        "Longbow": "Slow",
        "Musket": "Slow",
        "Pistol": "Vex"
    }
    
    for weapon, mastery in weapon_masteries.items():
        cursor.execute("""
            INSERT OR REPLACE INTO weapon_mastery_properties (weapon_name, mastery_name)
            VALUES (?, ?)
        """, (weapon, mastery))
        print(f"Assigned {weapon} -> {mastery}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Creating weapon mastery system...")
    create_mastery_tables()
    populate_masteries()
    populate_weapon_masteries()
    print("\nWeapon mastery system created successfully!")