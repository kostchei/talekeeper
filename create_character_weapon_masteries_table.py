#!/usr/bin/env python3
"""
Create the missing character_weapon_masteries table.
"""

import sqlite3

def create_character_weapon_masteries_table():
    """Create character_weapon_masteries table."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Create character_weapon_masteries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS character_weapon_masteries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id TEXT NOT NULL,
            weapon_name TEXT NOT NULL,
            mastery_type TEXT NOT NULL,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    """)
    
    print("Created character_weapon_masteries table")
    
    conn.commit()
    conn.close()
    print("Table creation complete!")

if __name__ == "__main__":
    create_character_weapon_masteries_table()