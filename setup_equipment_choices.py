#!/usr/bin/env python3
"""
Setup equipment choices for character creation.
Creates and populates the class_equipment_choices table.
"""

import sqlite3
import json

def setup_equipment_choices():
    """Create and populate the class_equipment_choices table."""
    
    # Connect to database
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Create the table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_equipment_choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT NOT NULL,
            choice_group TEXT NOT NULL,
            choice_name TEXT NOT NULL,
            options TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(class_id, choice_group)
        )
    """)
    
    # Clear existing Fighter equipment choices
    cursor.execute("DELETE FROM class_equipment_choices WHERE class_id = 'fighter'")
    
    # Fighter equipment choices
    fighter_choices = [
        {
            'class_id': 'fighter',
            'choice_group': 'armor_choice',
            'choice_name': 'Armor Choice',
            'options': json.dumps([
                'Studded Leather',
                'Scale Mail',
                'Chain Mail'
            ])
        },
        {
            'class_id': 'fighter',
            'choice_group': 'weapon_choice',
            'choice_name': 'Weapon Choice',
            'options': json.dumps([
                'Greatsword',
                'Longsword + Shield'
            ])
        }
    ]
    
    # Insert Fighter choices
    for choice in fighter_choices:
        cursor.execute("""
            INSERT INTO class_equipment_choices (class_id, choice_group, choice_name, options)
            VALUES (?, ?, ?, ?)
        """, (choice['class_id'], choice['choice_group'], choice['choice_name'], choice['options']))
    
    # Commit changes
    conn.commit()
    
    # Verify the data was inserted
    cursor.execute("SELECT * FROM class_equipment_choices WHERE class_id = 'fighter'")
    results = cursor.fetchall()
    
    print("Fighter equipment choices added:")
    for row in results:
        print(f"  - {row[3]}: {json.loads(row[4])}")
    
    conn.close()
    print("\nEquipment choices setup complete!")

if __name__ == "__main__":
    setup_equipment_choices()