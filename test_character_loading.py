#!/usr/bin/env python3
"""
Test what data is loaded when getting a character from the database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.game_engine_sqlite import GameEngineSQLite

def test_character_loading():
    """Test how characters are loaded from database."""
    print("=== Testing Character Loading ===")
    
    engine = GameEngineSQLite()
    
    # Test loading character from slot 1 (Valerius)
    print("Loading character from slot 1...")
    character = engine.load_character_sync(1)
    
    if character:
        print(f"Character name: {character.get('name', 'MISSING')}")
        print(f"Character keys: {list(character.keys())}")
        
        # Check for Lucky/Inspiration resources
        lucky_current = character.get('lucky_uses_current')
        lucky_max = character.get('lucky_uses_max')
        inspiration_current = character.get('inspiration_uses_current')
        inspiration_max = character.get('inspiration_uses_max')
        
        print(f"Lucky: {lucky_current}/{lucky_max}")
        print(f"Inspiration: {inspiration_current}/{inspiration_max}")
        
        if lucky_current is None:
            print("ERROR: lucky_uses_current is missing from character data")
        if inspiration_current is None:
            print("ERROR: inspiration_uses_current is missing from character data")
            
        return character
    else:
        print("ERROR: No character loaded from slot 1")
        return None

if __name__ == "__main__":
    test_character_loading()