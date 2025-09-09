#!/usr/bin/env python
"""
Test character creation to verify proficiencies are assigned.
"""

import uuid
from core.game_engine_sqlite import GameEngineSQLite

def test_character_creation():
    print("Testing Character Creation with Proficiencies")
    print("=" * 50)
    
    engine = GameEngineSQLite()
    
    # Create test character data
    test_character = {
        'name': f'TestFighter_{uuid.uuid4().hex[:6]}',
        'race_id': 'human',
        'class_id': 'fighter',
        'background_id': 'soldier',
        'level': 1,
        'experience_points': 0,
        'strength': 16,
        'dexterity': 14,
        'constitution': 15,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'hit_points_max': 12,
        'hit_points_current': 12,
        'feats': ['Tough'],
        'proficiencies': ['Athletics', 'Intimidation']  # Additional proficiencies
    }
    
    print(f"Creating character: {test_character['name']}")
    print(f"  Class: {test_character['class_id']}")
    print(f"  Race: {test_character['race_id']}")
    
    # Create character in slot 50 (test slot)
    try:
        created_char = engine.create_new_character_sync(test_character, 50)
        print(f"Character created successfully!")
        print(f"  ID: {created_char['id']}")
        
        # Now check proficiencies
        from services.proficiency_system import ProficiencySystem
        prof_system = ProficiencySystem()
        
        proficiencies = prof_system.get_character_proficiencies(created_char['id'])
        
        print(f"\nProficiencies assigned:")
        print(f"  Armor: {', '.join(proficiencies.get('armor', [])) or 'NONE'}")
        print(f"  Weapons: {', '.join(proficiencies.get('weapon', [])) or 'NONE'}")
        print(f"  Skills: {', '.join(proficiencies.get('skill', [])) or 'NONE'}")
        print(f"  Saving Throws: {', '.join(proficiencies.get('saving_throw', [])) or 'NONE'}")
        
        # Verify expected fighter proficiencies
        expected_armor = ['light', 'medium', 'heavy', 'shields']
        expected_weapons = ['simple', 'martial']
        expected_saves = ['strength', 'constitution']
        
        armor_ok = set(expected_armor) == set(proficiencies.get('armor', []))
        weapons_ok = set(expected_weapons) == set(proficiencies.get('weapon', []))
        saves_ok = set(expected_saves) == set(proficiencies.get('saving_throw', []))
        
        print(f"\nVerification:")
        print(f"  Armor proficiencies correct: {'YES' if armor_ok else 'NO'}")
        print(f"  Weapon proficiencies correct: {'YES' if weapons_ok else 'NO'}")
        print(f"  Saving throw proficiencies correct: {'YES' if saves_ok else 'NO'}")
        
        if armor_ok and weapons_ok and saves_ok:
            print("\nRESULT: SUCCESS - All proficiencies properly assigned!")
        else:
            print("\nRESULT: FAILURE - Some proficiencies missing!")
            
        # Clean up test character
        import sqlite3
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM characters WHERE id = ?", (created_char['id'],))
        cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (created_char['id'],))
        cursor.execute("DELETE FROM character_feats WHERE character_id = ?", (created_char['id'],))
        cursor.execute("DELETE FROM character_features WHERE character_id = ?", (created_char['id'],))
        conn.commit()
        conn.close()
        print("\nTest character cleaned up.")
        
    except Exception as e:
        print(f"Error creating character: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_character_creation()