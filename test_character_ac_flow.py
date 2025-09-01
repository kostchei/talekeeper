"""
Test the complete character creation -> loading -> display flow for AC.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_complete_ac_flow():
    """Test complete AC flow from creation to display."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create a test barbarian
    character_data = {
        'name': 'TestCompleteFlow',
        'race_id': 'human',
        'class_id': 'barbarian',
        'background_id': 'Soldier',
        'level': 1,
        'experience_points': 0,
        'strength': 16,
        'dexterity': 16,  # +3 mod
        'constitution': 18, # +4 mod  
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'feats': [],
        'armor_class': 10,
        'hit_points_max': 13,
        'hit_points_current': 13,
        'hit_dice_max': 1,
        'hit_dice_current': 1,
        'proficiencies': [],
        'features': {},
        'equipment_choices': {},
        'notes': 'Test complete AC flow'
    }
    
    print("=== STEP 1: CHARACTER CREATION ===")
    created = engine.create_new_character_sync(character_data, save_slot=112)
    
    if created:
        print(f"Created character: {created.name}")
        print(f"Creation AC: {created.armor_class}")
        
        print("\n=== STEP 2: DATABASE CHECK ===")
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("SELECT armor_class FROM characters WHERE name = ?", (created.name,))
        db_ac_after_creation = cursor.fetchone()[0]
        conn.close()
        print(f"DB AC after creation: {db_ac_after_creation}")
        
        print("\n=== STEP 3: CHARACTER LOADING ===")
        loaded = engine.load_character_sync(112)
        
        if loaded:
            print(f"Loaded character: {loaded.name}")
            print(f"Loading AC: {loaded.armor_class}")
            
            print("\n=== STEP 4: DATABASE CHECK AFTER LOADING ===")
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            cursor.execute("SELECT armor_class FROM characters WHERE name = ?", (loaded.name,))
            db_ac_after_loading = cursor.fetchone()[0]
            conn.close()
            print(f"DB AC after loading: {db_ac_after_loading}")
            
            print("\n=== STEP 5: DISPLAY DATA CONVERSION ===")
            # Simulate main_window._convert_dto_to_display
            display_data = {
                'armor_class': loaded.armor_class
            }
            print(f"Display data AC: {display_data['armor_class']}")
            
            print("\n=== SUMMARY ===")
            all_match = (
                created.armor_class == 17 and
                db_ac_after_creation == 17 and 
                loaded.armor_class == 17 and
                db_ac_after_loading == 17 and
                display_data['armor_class'] == 17
            )
            
            if all_match:
                print("SUCCESS: AC is 17 throughout the entire flow")
            else:
                print("ISSUE: AC values don't match expected 17")
                print(f"  Creation: {created.armor_class}")
                print(f"  DB after creation: {db_ac_after_creation}")
                print(f"  Loading: {loaded.armor_class}")
                print(f"  DB after loading: {db_ac_after_loading}")
                print(f"  Display: {display_data['armor_class']}")
        
        # Clean up
        conn = sqlite3.connect("talekeeper.db")
        conn.execute("DELETE FROM characters WHERE name = ?", (created.name,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    test_complete_ac_flow()