#!/usr/bin/env python3
"""Comprehensive test script to verify DTO removal works correctly."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game_engine_sqlite import GameEngineSQLite
import traceback

def test_dto_removal():
    """Test that the game engine works without DTOs."""
    print("="*60)
    print("Testing DTO Removal - Comprehensive Test Suite")
    print("="*60)
    
    try:
        # Initialize game engine
        engine = GameEngineSQLite()
        print("[PASS] Game engine initialized")
        
        # Test 1: Get save slots - should return list of dictionaries
        print("\nTest 1: Checking save slots...")
        save_slots = engine.get_save_slots_sync()
        print(f"  - Found {len(save_slots)} save slots")
        
        # Verify slots are dictionaries, not DTOs
        if save_slots:
            slot = save_slots[0]
            assert isinstance(slot, dict), f"Expected dict, got {type(slot)}"
            
            # Check required keys
            required_keys = ['slot_number', 'is_occupied', 'id', 'save_name', 
                           'character_name', 'character_level', 'current_location']
            for key in required_keys:
                assert key in slot, f"Missing required key: {key}"
            
            print(f"  - Save slots are dictionaries with correct structure")
            print(f"  - Sample slot keys: {list(slot.keys())[:5]}...")
        else:
            print("  - No save slots found (empty database)")
        
        # Test 2: Load a character if any occupied slots exist
        print("\nTest 2: Loading character data...")
        occupied_slots = [s for s in save_slots if s['is_occupied']]
        
        if occupied_slots:
            print(f"  - Found {len(occupied_slots)} occupied slots")
            slot_num = occupied_slots[0]['slot_number']
            print(f"  - Attempting to load from slot {slot_num}")
            
            character = engine.load_character_sync(slot_num)
            
            if character:
                # Verify character is a dictionary
                assert isinstance(character, dict), f"Expected dict, got {type(character)}"
                
                # Check core required keys
                core_keys = ['id', 'name', 'level', 'experience_points',
                           'race_id', 'race_name', 'class_id', 'class_name',
                           'strength', 'dexterity', 'constitution', 
                           'intelligence', 'wisdom', 'charisma',
                           'hit_points_max', 'hit_points_current', 'armor_class']
                
                missing_keys = []
                for key in core_keys:
                    if key not in character:
                        missing_keys.append(key)
                
                if missing_keys:
                    print(f"  - WARNING: Missing keys: {missing_keys}")
                else:
                    print(f"  - All core keys present")
                
                print(f"  - Loaded character: {character['name']} (Level {character['level']})")
                print(f"  - Character is a dictionary with {len(character)} keys")
                
                # Test ability modifiers are calculated
                for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                    modifier_key = f"{ability}_modifier"
                    assert modifier_key in character, f"Missing {modifier_key}"
                    expected_mod = (character[ability] - 10) // 2
                    assert character[modifier_key] == expected_mod, f"Incorrect {modifier_key}"
                print("  - Ability modifiers correctly calculated")
                
            else:
                print(f"  - No character data in slot {slot_num} (might be corrupted)")
        else:
            print("  - No occupied slots to test character loading")
        
        # Test 3: Create a test character
        print("\nTest 3: Creating new test character...")
        
        # Find an empty slot
        empty_slot = None
        for i in range(1, 20):
            slot_occupied = any(s['slot_number'] == i and s['is_occupied'] for s in save_slots)
            if not slot_occupied:
                empty_slot = i
                break
        
        if empty_slot:
            print(f"  - Using empty slot {empty_slot}")
            
            test_character = {
                'name': 'DTO Test Character',
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
                'feats': [],
                'proficiencies': ['Athletics', 'Intimidation'],
                'features': {
                    'Second Wind': {
                        'type': 'action',
                        'usage': 'short_rest',
                        'level_gained': 1,
                        'description': 'Regain 1d10 + level hit points'
                    }
                }
            }
            
            # Create the character
            created = engine.create_new_character_sync(test_character, empty_slot)
            
            # Verify it's a dictionary
            assert isinstance(created, dict), f"Created character should be dict, got {type(created)}"
            assert created['name'] == 'DTO Test Character', "Character name mismatch"
            assert created['level'] == 1, "Character level mismatch"
            
            print(f"  - Successfully created test character in slot {empty_slot}")
            print(f"  - Character returned as dictionary with {len(created)} keys")
            
            # Clean up - delete the test character
            print(f"  - Cleaning up test character from slot {empty_slot}")
            engine.delete_character_sync(empty_slot)
            
        else:
            print("  - No empty slots available for test character creation")
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED - DTOs Successfully Removed!")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dto_removal()
    sys.exit(0 if success else 1)