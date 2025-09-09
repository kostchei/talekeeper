#!/usr/bin/env python
"""
Fix existing characters by initializing their proficiencies based on their class.
This script retroactively adds proficiencies to characters created before
the proficiency system was implemented.
"""

import sqlite3
from services.proficiency_system import ProficiencySystem

def fix_existing_characters():
    print("Fixing Proficiencies for Existing Characters")
    print("=" * 50)
    
    prof_system = ProficiencySystem()
    
    # Get all characters
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, class_id, level 
        FROM characters 
        ORDER BY name
    """)
    
    characters = cursor.fetchall()
    
    print(f"Found {len(characters)} characters to check\n")
    
    fixed_count = 0
    
    for char_id, name, class_id, level in characters:
        # Check if character already has proficiencies
        cursor.execute("""
            SELECT COUNT(*) FROM character_proficiencies 
            WHERE character_id = ?
        """, (char_id,))
        
        prof_count = cursor.fetchone()[0]
        
        if prof_count == 0:
            print(f"Character: {name} (Level {level} {class_id.title()})")
            print(f"  Status: No proficiencies found - FIXING...")
            
            # Initialize proficiencies
            success = prof_system.initialize_character_proficiencies(char_id, class_id)
            
            if success:
                # Get the new proficiencies
                proficiencies = prof_system.get_character_proficiencies(char_id)
                
                print(f"  Added proficiencies:")
                if proficiencies.get('armor'):
                    print(f"    Armor: {', '.join(proficiencies['armor'])}")
                if proficiencies.get('weapon'):
                    print(f"    Weapons: {', '.join(proficiencies['weapon'][:5])}{'...' if len(proficiencies['weapon']) > 5 else ''}")
                if proficiencies.get('skill'):
                    print(f"    Skills: {len(proficiencies['skill'])} skills")
                if proficiencies.get('saving_throw'):
                    print(f"    Saving Throws: {', '.join(proficiencies['saving_throw'])}")
                
                fixed_count += 1
                print(f"  Result: SUCCESS\n")
            else:
                print(f"  Result: FAILED\n")
        else:
            print(f"Character: {name} - Already has {prof_count} proficiencies (SKIPPED)\n")
    
    conn.close()
    
    print("=" * 50)
    print(f"Fixed {fixed_count} characters")
    print("All existing characters now have proper proficiencies!")

def verify_character(character_name: str):
    """Verify a specific character's proficiencies"""
    print(f"\nVerifying proficiencies for: {character_name}")
    print("-" * 40)
    
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, c.name, c.class_id, c.level 
        FROM characters c
        WHERE LOWER(c.name) LIKE LOWER(?)
    """, (f'%{character_name}%',))
    
    char_data = cursor.fetchone()
    
    if not char_data:
        print(f"Character '{character_name}' not found!")
        return
    
    char_id, name, class_id, level = char_data
    
    print(f"Found: {name} (Level {level} {class_id.title()})")
    
    # Get proficiencies
    prof_system = ProficiencySystem()
    proficiencies = prof_system.get_character_proficiencies(char_id)
    
    print("\nCurrent Proficiencies:")
    print(f"  Armor: {', '.join(proficiencies.get('armor', [])) or 'None'}")
    print(f"  Weapons: {', '.join(proficiencies.get('weapon', [])) or 'None'}")
    print(f"  Skills: {', '.join(proficiencies.get('skill', [])) or 'None'}")
    print(f"  Saving Throws: {', '.join(proficiencies.get('saving_throw', [])) or 'None'}")
    print(f"  Tools: {', '.join(proficiencies.get('tool', [])) or 'None'}")
    print(f"  Languages: {', '.join(proficiencies.get('language', [])) or 'None'}")
    
    conn.close()

if __name__ == "__main__":
    # Fix all existing characters
    fix_existing_characters()
    
    # Verify specific character
    print("\n" + "=" * 50)
    verify_character("Adventurerer")