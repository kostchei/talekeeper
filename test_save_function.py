#!/usr/bin/env python3
"""Test the save functionality to check for attribute errors."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_save_functionality():
    """Test character saving without attribute errors."""
    print("Testing save functionality...")
    
    try:
        from core.game_engine_sqlite import GameEngineSQLite
        
        # Initialize engine
        engine = GameEngineSQLite()
        print("Engine initialized")
        
        # Find a character to load
        slots = engine.get_save_slots_sync()
        occupied_slots = [s for s in slots if s['is_occupied']]
        
        if not occupied_slots:
            print("No characters found to test with")
            return False
        
        # Load a character
        slot = occupied_slots[0]
        print(f"Loading character from slot {slot['slot_number']}: {slot['character_name']}")
        
        character = engine.load_character_sync(slot['slot_number'])
        if not character:
            print("Failed to load character")
            return False
        
        print(f"Loaded character: {character['name']}")
        engine.current_character = character
        
        # Test save_character_sync
        print("Testing save_character_sync...")
        success = engine.save_character_sync()
        print(f"save_character_sync result: {success}")
        
        # Test save_game_sync  
        print("Testing save_game_sync...")
        success = engine.save_game_sync()
        print(f"save_game_sync result: {success}")
        
        print("SUCCESS: All save functions work without attribute errors!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_save_functionality()
    sys.exit(0 if success else 1)