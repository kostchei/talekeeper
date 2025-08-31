#!/usr/bin/env python3
"""
Load classes from JSON to database tables.
"""

import sqlite3
import json

def create_classes_tables():
    """Create classes and related tables."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Classes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            hit_die INTEGER NOT NULL,
            primary_ability TEXT NOT NULL,
            skill_choices INTEGER NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0
        )
    """)
    
    # Class saving throw proficiencies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_saving_throws (
            class_id INTEGER,
            ability TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            PRIMARY KEY (class_id, ability)
        )
    """)
    
    # Class armor proficiencies  
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_armor_proficiencies (
            class_id INTEGER,
            armor_type TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            PRIMARY KEY (class_id, armor_type)
        )
    """)
    
    # Class weapon proficiencies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_weapon_proficiencies (
            class_id INTEGER,
            weapon_type TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            PRIMARY KEY (class_id, weapon_type)
        )
    """)
    
    # Class skill proficiencies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_skill_proficiencies (
            class_id INTEGER,
            skill TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            PRIMARY KEY (class_id, skill)
        )
    """)
    
    # Class features
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_features (
            class_id INTEGER,
            level INTEGER NOT NULL,
            feature_name TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            PRIMARY KEY (class_id, level, feature_name)
        )
    """)
    
    # Subclasses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subclasses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id)
        )
    """)
    
    # Subclass features
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subclass_features (
            subclass_id INTEGER,
            level INTEGER NOT NULL,
            feature_name TEXT NOT NULL,
            FOREIGN KEY (subclass_id) REFERENCES subclasses(id),
            PRIMARY KEY (subclass_id, level, feature_name)
        )
    """)
    
    conn.commit()
    conn.close()

def load_classes_to_db():
    """Load classes from JSON to database."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Load classes data
    with open('data/classes.json', 'r') as f:
        classes_data = json.load(f)
    
    # Define display order
    class_order = ["Fighter", "Barbarian", "Cleric", "Paladin", "Rogue", "Warlock", "Wizard"]
    
    for class_data in classes_data:
        class_name = class_data['name']
        display_order = class_order.index(class_name) if class_name in class_order else 999
        
        # Insert class
        cursor.execute("""
            INSERT OR REPLACE INTO classes (name, description, hit_die, primary_ability, skill_choices, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            class_name,
            class_data['description'],
            class_data['hit_die'],
            class_data['primary_ability'],
            class_data['skill_choices'],
            display_order
        ))
        
        class_id = cursor.lastrowid
        if class_id is None:
            cursor.execute("SELECT id FROM classes WHERE name = ?", (class_name,))
            class_id = cursor.fetchone()[0]
        
        print(f"Added class: {class_name} (ID: {class_id})")
        
        # Clear existing related data for this class
        cursor.execute("DELETE FROM class_saving_throws WHERE class_id = ?", (class_id,))
        cursor.execute("DELETE FROM class_armor_proficiencies WHERE class_id = ?", (class_id,))
        cursor.execute("DELETE FROM class_weapon_proficiencies WHERE class_id = ?", (class_id,))
        cursor.execute("DELETE FROM class_skill_proficiencies WHERE class_id = ?", (class_id,))
        cursor.execute("DELETE FROM class_features WHERE class_id = ?", (class_id,))
        
        # Add saving throw proficiencies
        for ability in class_data.get('saving_throw_proficiencies', []):
            cursor.execute("""
                INSERT INTO class_saving_throws (class_id, ability) VALUES (?, ?)
            """, (class_id, ability))
        
        # Add armor proficiencies
        for armor_type in class_data.get('armor_proficiencies', []):
            cursor.execute("""
                INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES (?, ?)
            """, (class_id, armor_type))
        
        # Add weapon proficiencies
        for weapon_type in class_data.get('weapon_proficiencies', []):
            cursor.execute("""
                INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES (?, ?)
            """, (class_id, weapon_type))
        
        # Add skill proficiencies
        for skill in class_data.get('skill_proficiencies', []):
            cursor.execute("""
                INSERT INTO class_skill_proficiencies (class_id, skill) VALUES (?, ?)
            """, (class_id, skill))
        
        # Add class features
        for level_str, features in class_data.get('class_features', {}).items():
            level = int(level_str)
            for feature in features:
                cursor.execute("""
                    INSERT INTO class_features (class_id, level, feature_name) VALUES (?, ?, ?)
                """, (class_id, level, feature))
        
        # Add subclasses
        for subclass_data in class_data.get('subclasses', []):
            cursor.execute("""
                INSERT OR REPLACE INTO subclasses (class_id, name, description)
                VALUES (?, ?, ?)
            """, (class_id, subclass_data['name'], subclass_data['description']))
            
            subclass_id = cursor.lastrowid
            if subclass_id is None:
                cursor.execute("SELECT id FROM subclasses WHERE class_id = ? AND name = ?", 
                             (class_id, subclass_data['name']))
                subclass_id = cursor.fetchone()[0]
            
            # Clear existing subclass features
            cursor.execute("DELETE FROM subclass_features WHERE subclass_id = ?", (subclass_id,))
            
            # Add subclass features
            for level_str, features in subclass_data.get('features', {}).items():
                level = int(level_str)
                for feature in features:
                    cursor.execute("""
                        INSERT INTO subclass_features (subclass_id, level, feature_name) 
                        VALUES (?, ?, ?)
                    """, (subclass_id, level, feature))
    
    conn.commit()
    conn.close()
    print("\nClasses loaded to database successfully!")

if __name__ == "__main__":
    create_classes_tables()
    load_classes_to_db()