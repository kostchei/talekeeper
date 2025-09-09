#!/usr/bin/env python
"""
Test that saving throw proficiencies are properly initialized for new characters.
"""

import sqlite3
import uuid
from services.proficiency_system import ProficiencySystem

def test_saving_throw_proficiencies():
    print("Testing Saving Throw Proficiencies...")
    print("=" * 50)
    
    prof_system = ProficiencySystem()
    
    # Test different classes
    classes_to_test = [
        ('fighter', ['strength', 'constitution']),
        ('wizard', ['intelligence', 'wisdom']),
        ('rogue', ['dexterity', 'intelligence'])
    ]
    
    for class_id, expected_saves in classes_to_test:
        # Check what saves are in the database for this class
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ability FROM class_saving_throws 
            WHERE class_id = ? ORDER BY ability
        """, (class_id,))
        db_saves = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not db_saves:
            print(f"\n{class_id.title()}: No saving throws in database, skipping...")
            continue
        
        print(f"\n{class_id.title()} Class:")
        print(f"  Expected saves from DB: {', '.join(db_saves)}")
        
        # Create a test character
        test_char_id = str(uuid.uuid4())
        
        # Initialize proficiencies
        success = prof_system.initialize_character_proficiencies(test_char_id, class_id)
        print(f"  Initialization: {'SUCCESS' if success else 'FAILED'}")
        
        # Get all proficiencies
        proficiencies = prof_system.get_character_proficiencies(test_char_id)
        
        # Check saving throws
        save_profs = proficiencies.get('saving_throw', [])
        print(f"  Saving throw proficiencies: {', '.join(save_profs) if save_profs else 'None'}")
        
        # Verify they match
        if set(save_profs) == set(db_saves):
            print(f"  Result: PASS - All saving throws assigned correctly")
        else:
            print(f"  Result: FAIL - Missing or incorrect saving throws")
        
        # Also show other proficiencies
        print(f"  Armor: {', '.join(proficiencies.get('armor', []))}")
        print(f"  Weapons: {', '.join(proficiencies.get('weapon', []))}")
        print(f"  Skills: {len(proficiencies.get('skill', []))} skills")
        
        # Clean up
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (test_char_id,))
        conn.commit()
        conn.close()
    
    print("\n" + "=" * 50)
    print("Saving Throw Proficiency Test Complete!")

if __name__ == "__main__":
    test_saving_throw_proficiencies()