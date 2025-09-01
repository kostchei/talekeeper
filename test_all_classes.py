"""
Test that all available classes save correctly with the fixed class ID lookup.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_all_classes():
    """Test that all classes save with correct class_id."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Get available classes
    classes = engine.get_available_classes_sync()
    
    print("Testing all available classes...")
    results = {}
    
    for cls in classes:
        class_name = cls.name
        expected_id = class_name.lower().replace(' ', '_')
        
        # Basic character data
        character_data = {
            'name': f'Test{class_name}',
            'race_id': 'human',
            'class_id': class_name.lower(),
            'background_id': 'Soldier',
            'level': 1,
            'experience_points': 0,
            'strength': 15,
            'dexterity': 14,
            'constitution': 13,
            'intelligence': 12,
            'wisdom': 10,
            'charisma': 8,
            'feats': [],
            'armor_class': 10,
            'hit_points_max': 10,
            'hit_points_current': 10,
            'hit_dice_max': 1,
            'hit_dice_current': 1,
            'proficiencies': [],
            'features': {},
            'equipment_choices': {},
            'notes': f'Test {class_name} character'
        }
        
        print(f"\nTesting {class_name}...")
        
        # Use unique slot for each test
        slot = 200 + cls.id
        created = engine.create_new_character_sync(character_data, save_slot=slot)
        
        if created:
            # Check database directly
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            cursor.execute("SELECT class_id FROM characters WHERE name = ?", (created.name,))
            db_class = cursor.fetchone()[0]
            conn.close()
            
            print(f"  Expected: {expected_id}")
            print(f"  Got: {db_class}")
            
            if db_class == expected_id:
                print(f"  SUCCESS: {class_name} saved correctly!")
                results[class_name] = True
            else:
                print(f"  FAIL: {class_name} saved as {db_class}")
                results[class_name] = False
            
            # Clean up
            conn = sqlite3.connect("talekeeper.db")
            conn.execute("DELETE FROM characters WHERE name = ?", (created.name,))
            conn.commit()
            conn.close()
        else:
            print(f"  FAIL: {class_name} character creation failed")
            results[class_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY:")
    all_passed = True
    for class_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {class_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall result: {'ALL CLASSES WORKING' if all_passed else 'SOME CLASSES FAILING'}")
    return all_passed

if __name__ == "__main__":
    test_all_classes()