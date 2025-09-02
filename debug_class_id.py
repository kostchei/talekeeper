"""
Debug script to check class_id loading for Bog character.
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.game_engine_sqlite import GameEngineSQLite

def debug_class_id():
    """Debug class_id loading."""
    print("=== CLASS_ID DEBUG ===")
    
    # Initialize game engine
    engine = GameEngineSQLite("talekeeper.db")
    
    # Load character from slot 3 (Bog)
    character = engine.load_character_sync(3)
    
    if character:
        print(f"Character loaded: {character.name}")
        print(f"Character class_id: '{character.class_id}' (type: {type(character.class_id)})")
        print(f"Character class_id is None: {character.class_id is None}")
        print(f"Character class_id is empty string: {character.class_id == ''}")
        if character.class_id:
            print(f"Character class_id length: {len(character.class_id)}")
        
        # Also check what's in the character stats dict that would be passed
        character_stats = {
            'id': character.id,
            'class_id': character.class_id,
            'name': character.name
        }
        print(f"Character stats dict: {character_stats}")
        print(f"class_id in character_stats: {'class_id' in character_stats}")
        print(f"character_stats['class_id']: '{character_stats['class_id']}'")
        
    else:
        print("No character found in slot 3")

if __name__ == "__main__":
    debug_class_id()