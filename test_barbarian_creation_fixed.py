"""
Test Barbarian character creation after fixing the class ID bug.
"""

from core.game_engine_sqlite import GameEngineSQLite

def test_fixed_barbarian_creation():
    """Test that Barbarian characters are now saved correctly."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Barbarian character data as would come from UI
    character_data = {
        'name': 'TestFixedBarbarian',
        'race_id': 'human',
        'class_id': 'barbarian',  # This should now work correctly
        'background_id': 'Soldier',
        'level': 1,
        'experience_points': 0,
        'strength': 16,
        'dexterity': 13,
        'constitution': 15,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'feats': [],
        'armor_class': 12,  # Should be 12 without armor: 10 + 1 (Dex) + 2 (Con) = 13
        'hit_points_max': 13,  # 12 (d12) + 2 (Con mod) = 14
        'hit_points_current': 13,
        'hit_dice_max': 1,
        'hit_dice_current': 1,
        'proficiencies': [],
        'features': {
            'Rage': {
                'type': 'bonus_action',
                'usage': 'long_rest',
                'description': '+2 damage on Str-based melee attacks, resistance to physical damage',
                'level_acquired': 1
            },
            'Unarmored Defense': {
                'type': 'passive',
                'usage': 'permanent', 
                'description': 'While not wearing armor, your AC equals 10 + Dex modifier + Con modifier',
                'level_acquired': 1
            }
        },
        'equipment_choices': {'barbarian_choice': 'Greataxe'},
        'notes': 'Test Barbarian with correct class_id'
    }
    
    print("Testing Barbarian creation with fixed class lookup...")
    
    created = engine.create_new_character_sync(character_data, save_slot=107)
    
    if created:
        print(f"SUCCESS: Character created: {created.name}")
        print(f"SUCCESS: Class ID: {created.class_id}")
        print(f"SUCCESS: Features: {list(created.features.keys()) if created.features else 'None'}")
        
        # Check database directly
        import sqlite3
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("SELECT class_id FROM characters WHERE name = ?", (created.name,))
        db_class = cursor.fetchone()[0]
        conn.close()
        
        print(f"SUCCESS: Class in database: {db_class}")
        
        if db_class == 'barbarian':
            print("\nSUCCESS! Barbarian is now saved with correct class_id!")
            
            # Clean up
            conn = sqlite3.connect("talekeeper.db")
            conn.execute("DELETE FROM characters WHERE name = ?", (created.name,))
            conn.commit()
            conn.close()
            return True
        else:
            print(f"\nFAIL: Expected 'barbarian', got '{db_class}'")
            return False
    else:
        print("FAIL: Character creation failed")
        return False

if __name__ == "__main__":
    test_fixed_barbarian_creation()