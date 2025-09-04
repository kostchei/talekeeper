#!/usr/bin/env python3
"""
Test that equipment choices are properly applied to a character.
"""

from core.game_engine_sqlite import GameEngineSQLite
import json

def test_equipment_application():
    """Test applying equipment choices to a character."""
    
    ge = GameEngineSQLite()
    
    # Simulate character data with equipment choices
    character_data = {
        'name': 'Test Fighter',
        'class_id': 'fighter',
        'level': 1,
        'inventory': []
    }
    
    # Test Case 1: Single armor item
    print("Test Case 1: Armor choice (Chain Mail)")
    equipment_choices = {
        'armor_choice': 'Chain Mail'
    }
    
    ge.apply_equipment_choices_sync(character_data, equipment_choices)
    print(f"  Inventory after armor: {character_data.get('inventory', [])}")
    print(f"  Equipped armor: {character_data.get('equipment_armor', 'None')}")
    
    # Test Case 2: Single weapon
    print("\nTest Case 2: Weapon choice (Greatsword)")
    character_data['inventory'] = []  # Reset inventory
    equipment_choices = {
        'weapon_choice': 'Greatsword'
    }
    
    ge.apply_equipment_choices_sync(character_data, equipment_choices)
    print(f"  Inventory after weapon: {character_data.get('inventory', [])}")
    print(f"  Equipped main hand: {character_data.get('equipment_main_hand', 'None')}")
    
    # Test Case 3: Weapon + Shield combo
    print("\nTest Case 3: Weapon + Shield combo")
    character_data = {
        'name': 'Test Fighter 2',
        'class_id': 'fighter', 
        'level': 1,
        'inventory': []
    }
    
    # Simulate how the UI breaks down "Longsword + Shield"
    equipment_choices = {
        'weapon_choice_item_1': 'Longsword',
        'weapon_choice_item_2': 'Shield'
    }
    
    ge.apply_equipment_choices_sync(character_data, equipment_choices)
    print(f"  Inventory after combo: {character_data.get('inventory', [])}")
    print(f"  Equipped main hand: {character_data.get('equipment_main_hand', 'None')}")
    print(f"  Equipped off hand: {character_data.get('equipment_off_hand', 'None')}")
    
    print("\n✓ All equipment choice tests completed!")

if __name__ == "__main__":
    test_equipment_application()