#!/usr/bin/env python3
"""
Load backgrounds from JSON file into SQLite database.
"""

import sqlite3
import json
from pathlib import Path

def create_backgrounds_table(cursor):
    """Create backgrounds table with proper schema."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backgrounds (
            name TEXT PRIMARY KEY,
            description TEXT,
            ability_scores TEXT,  -- JSON array of ability scores
            feat TEXT,
            skill_proficiencies TEXT,  -- JSON array of skills
            tool_proficiencies TEXT,  -- JSON array of tools
            equipment_option_a TEXT,  -- JSON array of equipment
            equipment_option_a_gold INTEGER,
            equipment_option_b_gold INTEGER
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_backgrounds_name ON backgrounds(name)
    """)

def load_backgrounds_data(cursor):
    """Load backgrounds data from JSON file."""
    backgrounds_file = Path("data/backgrounds.json")
    
    if not backgrounds_file.exists():
        print(f"Error: {backgrounds_file} not found")
        return False
    
    with open(backgrounds_file, 'r') as f:
        backgrounds = json.load(f)
    
    print(f"Loading {len(backgrounds)} backgrounds...")
    
    for background in backgrounds:
        name = background['name']
        description = background['description']
        ability_scores = json.dumps(background['ability_scores'])
        feat = background['feat']
        skill_proficiencies = json.dumps(background['skill_proficiencies'])
        tool_proficiencies = json.dumps(background['tool_proficiencies'])
        
        # Extract equipment options
        starting_equipment = background['starting_equipment']
        option_a = starting_equipment['option_a']
        equipment_option_a = json.dumps(option_a['equipment'])
        equipment_option_a_gold = option_a['gold']
        equipment_option_b_gold = starting_equipment['option_b']['gold']
        
        cursor.execute("""
            INSERT OR REPLACE INTO backgrounds (
                name, description, ability_scores, feat, skill_proficiencies, 
                tool_proficiencies, equipment_option_a, equipment_option_a_gold, 
                equipment_option_b_gold
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, description, ability_scores, feat, skill_proficiencies,
            tool_proficiencies, equipment_option_a, equipment_option_a_gold,
            equipment_option_b_gold
        ))
        
        print(f"  + {name}")
    
    return True

def main():
    """Main function to load backgrounds into database."""
    db_path = "talekeeper.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Creating backgrounds table...")
        create_backgrounds_table(cursor)
        
        print("Loading backgrounds data...")
        if load_backgrounds_data(cursor):
            conn.commit()
            print("SUCCESS: Backgrounds loaded successfully!")
            
            # Show count
            cursor.execute("SELECT COUNT(*) FROM backgrounds")
            count = cursor.fetchone()[0]
            print(f"Total backgrounds in database: {count}")
        else:
            print("ERROR: Failed to load backgrounds")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()