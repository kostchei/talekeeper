#!/usr/bin/env python3
"""
Populate the level_progression table with D&D 2024 progression data.
"""

import sqlite3

def populate_level_progression():
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # D&D 2024 level progression - Experience and Proficiency Bonus
    progression_data = [
        (1, 0, 2),
        (2, 300, 2),
        (3, 900, 2),
        (4, 2700, 2),
        (5, 6500, 3),
        (6, 14000, 3),
        (7, 23000, 3),
        (8, 34000, 3),
        (9, 48000, 4),
        (10, 64000, 4),
        (11, 85000, 4),
        (12, 100000, 4),
        (13, 120000, 5),
        (14, 140000, 5),
        (15, 165000, 5),
        (16, 195000, 5),
        (17, 225000, 6),
        (18, 265000, 6),
        (19, 305000, 6),
        (20, 355000, 6)
    ]
    
    # Clear existing data
    cursor.execute("DELETE FROM level_progression")
    
    # Insert new data
    cursor.executemany(
        "INSERT INTO level_progression (level, experience_points, proficiency_bonus) VALUES (?, ?, ?)",
        progression_data
    )
    
    conn.commit()
    print(f"Populated level_progression table with {len(progression_data)} levels")
    
    # Verify the data
    cursor.execute("SELECT COUNT(*) FROM level_progression")
    count = cursor.fetchone()[0]
    print(f"Level progression table now has {count} records")
    
    conn.close()

if __name__ == "__main__":
    populate_level_progression()