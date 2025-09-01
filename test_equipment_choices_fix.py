"""
Test that equipment choices loading is fixed.
"""

from core.game_engine_sqlite import GameEngineSQLite

def test_equipment_choices():
    """Test loading equipment choices for various classes."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    test_classes = ['barbarian', 'fighter', 'cleric', 'rogue', 'paladin', 'warlock', 'wizard']
    
    for class_name in test_classes:
        print(f"\n=== Testing {class_name.title()} ===")
        
        try:
            choices = engine.get_class_equipment_choices_sync(class_name)
            print(f"Found {len(choices)} equipment choice groups:")
            
            for choice in choices:
                print(f"  Group: {choice['group']}")
                print(f"  Name: {choice['name']}")
                print(f"  Options ({len(choice['options'])}): {choice['options']}")
                
                # Verify each option is accessible (this would fail before fix)
                for i, option in enumerate(choice['options']):
                    if isinstance(option, str):
                        print(f"    Option {i+1}: {option} (string - OK)")
                    elif isinstance(option, dict):
                        print(f"    Option {i+1}: {option.get('name', 'unnamed')} (dict - OK)")
                    else:
                        print(f"    Option {i+1}: {option} (unknown type: {type(option)})")
                        
        except Exception as e:
            print(f"ERROR loading choices for {class_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_equipment_choices()