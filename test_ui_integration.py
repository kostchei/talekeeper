#!/usr/bin/env python3
"""Test UI integration with dictionary-based data flow."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.game_engine_sqlite import GameEngineSQLite

def test_ui_integration():
    """Test that UI properly handles dictionary data."""
    print("="*60)
    print("Testing UI Integration with Dictionary Data")
    print("="*60)
    
    # Create Qt application (required for UI)
    app = QApplication(sys.argv)
    
    try:
        # Test 1: Initialize main window
        print("\nTest 1: Initializing MainWindow...")
        window = MainWindow()
        print("  - MainWindow created successfully")
        
        # Test 2: Check game engine is using dictionaries
        print("\nTest 2: Checking game engine...")
        assert hasattr(window, 'game_engine'), "MainWindow should have game_engine"
        assert isinstance(window.game_engine, GameEngineSQLite), "Should be using SQLite engine"
        print("  - Game engine properly initialized")
        
        # Test 3: Test _convert_dto_to_display method
        print("\nTest 3: Testing data conversion...")
        
        # Create a sample character dictionary (not a DTO)
        sample_char = {
            'id': 'test-123',
            'name': 'Test Hero',
            'level': 5,
            'race_name': 'Human',
            'class_name': 'Fighter',
            'background_name': 'Soldier',
            'hit_points_current': 40,
            'hit_points_max': 45,
            'armor_class': 16,
            'strength': 18,
            'dexterity': 14,
            'constitution': 16,
            'intelligence': 10,
            'wisdom': 12,
            'charisma': 8,
            'experience_points': 6500,
            'features': {'Second Wind': {'type': 'action'}},
            'feats': ['Great Weapon Master']
        }
        
        # Test the conversion method
        display_data = window._convert_dto_to_display(sample_char)
        
        # Verify the conversion worked
        assert isinstance(display_data, dict), "Should return a dictionary"
        assert display_data['name'] == 'Test Hero', "Name should match"
        assert display_data['level'] == 5, "Level should match"
        assert display_data['current_hit_points'] == 40, "HP mapping should work"
        assert display_data['hit_points'] == 45, "Max HP mapping should work"
        assert display_data['armor_class'] == 16, "AC should match"
        assert 'feats' in display_data, "Feats should be included"
        
        print("  - Data conversion works correctly")
        print(f"  - Converted {len(sample_char)} keys to {len(display_data)} display keys")
        
        # Test 4: Test save slot handling
        print("\nTest 4: Testing save slot handling...")
        save_slots = window.game_engine.get_save_slots_sync()
        
        if save_slots:
            # Verify UI can handle dictionary-based save slots
            for slot in save_slots[:3]:  # Check first 3 slots
                assert isinstance(slot, dict), f"Slot should be dict, got {type(slot)}"
                assert 'slot_number' in slot, "Slot should have slot_number"
                assert 'is_occupied' in slot, "Slot should have is_occupied"
                
                # Test the UI would correctly access these
                slot_num = slot['slot_number']
                is_occupied = slot['is_occupied']
                
                if is_occupied:
                    char_name = slot.get('character_name', 'Unknown')
                    print(f"  - Slot {slot_num}: {char_name} (occupied)")
                else:
                    print(f"  - Slot {slot_num}: Empty")
        
        print("\n" + "="*60)
        print("UI INTEGRATION TEST PASSED!")
        print("UI properly handles dictionary-based data flow")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up Qt application
        app.quit()

if __name__ == "__main__":
    success = test_ui_integration()
    sys.exit(0 if success else 1)