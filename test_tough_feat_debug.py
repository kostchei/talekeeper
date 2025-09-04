#!/usr/bin/env python3
"""
Debug script to test Tough feat HP calculation and identify double-counting.
"""

import sys
sys.path.append('.')

from services.feat_effects import FeatEffectsProcessor

def test_tough_feat_calculation():
    """Test the Tough feat HP calculation directly."""
    
    processor = FeatEffectsProcessor()
    
    # Test Case 1: Level 1 character with Tough feat
    print("=== Test Case 1: Level 1 Barbarian with Tough feat ===")
    character_data = {
        'name': 'Chut',
        'level': 1,
        'class_id': 'Barbarian',
        'constitution': 15,  # +2 CON mod
        'hit_points_max': 14,  # Base: 12 (Barb d12) + 2 (CON)
        'hit_points_current': 14
    }
    
    print(f"BEFORE Tough feat: {character_data['hit_points_max']} max HP")
    
    # Apply Tough feat
    modified_data = processor.apply_feat_effects_to_character(character_data, ['Tough'])
    
    print(f"AFTER Tough feat: {modified_data['hit_points_max']} max HP")
    print(f"HP Increase: {modified_data['hit_points_max'] - character_data['hit_points_max']}")
    
    # Expected: Should be +2 for level 1 (2 * 1 = 2)
    expected_increase = 2
    actual_increase = modified_data['hit_points_max'] - character_data['hit_points_max']
    
    print(f"Expected increase: +{expected_increase}")
    print(f"Actual increase: +{actual_increase}")
    
    if actual_increase != expected_increase:
        print(f"[ERROR] Expected +{expected_increase}, got +{actual_increase}")
        return False
    else:
        print(f"[CORRECT] Tough feat applied correctly for level 1")
    
    # Test Case 2: What happens if we apply it twice (double-counting scenario)
    print("\n=== Test Case 2: Applying Tough feat twice (simulating double-counting) ===")
    character_data_copy = character_data.copy()
    
    # First application
    first_application = processor.apply_feat_effects_to_character(character_data_copy, ['Tough'])
    print(f"After 1st application: {first_application['hit_points_max']} max HP")
    
    # Second application (this would be the bug)
    second_application = processor.apply_feat_effects_to_character(first_application, ['Tough'])
    print(f"After 2nd application: {second_application['hit_points_max']} max HP")
    
    if second_application['hit_points_max'] == 18:  # 14 + 2 + 2 = 18
        print("[ERROR] DOUBLE-COUNTING DETECTED: Tough feat applied twice!")
        return False
    
    return True

def test_dwarf_toughness():
    """Test if Dwarven Toughness might be contributing to extra HP."""
    print("\n=== Testing Dwarven Toughness ===")
    
    # Check level up service
    sys.path.append('.')
    from services.level_up import LevelUpService
    
    level_up = LevelUpService()
    
    # Simulate getting species HP bonus for a dwarf
    import sqlite3
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Mock a character with dwarf race
    cursor.execute("""
        SELECT character_id FROM characters 
        WHERE race_id LIKE '%warf%' 
        LIMIT 1
    """)
    
    dwarf_char = cursor.fetchone()
    if dwarf_char:
        species_bonus = level_up._get_species_hp_bonus(cursor, dwarf_char[0])
        print(f"Dwarven HP bonus per level: +{species_bonus}")
        if species_bonus > 0:
            print("Dwarven Toughness: +1 HP per level detected")
    else:
        print("No dwarf characters found to test")
        # Manually test the logic
        cursor.execute("INSERT INTO characters (id, race_id) VALUES ('test', 'Dwarf')")
        species_bonus = level_up._get_species_hp_bonus(cursor, 'test')
        print(f"Dwarven HP bonus per level: +{species_bonus}")
        cursor.execute("DELETE FROM characters WHERE id = 'test'")
    
    conn.close()

if __name__ == "__main__":
    print("[DEBUG] Debugging Tough Feat HP Calculation\n")
    
    tough_test_passed = test_tough_feat_calculation()
    test_dwarf_toughness()
    
    if tough_test_passed:
        print("\n[SUCCESS] Tough feat logic appears correct - issue might be elsewhere")
        print("[INFO] Possible causes of extra 2 HP:")
        print("   1. Feat effects applied during creation AND during loading")
        print("   2. Dwarven Toughness (+1 HP/level) being counted twice")
        print("   3. Some other HP bonus being applied")
    else:
        print("\n[ERROR] Tough feat logic has issues - this is likely the source of extra HP")