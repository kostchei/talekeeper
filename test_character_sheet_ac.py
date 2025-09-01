"""
Test that character sheet displays the correct AC including Unarmored Defense.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_character_sheet_ac():
    """Test character sheet AC display after creating a Barbarian."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create a test barbarian
    character_data = {
        'name': 'TestCharSheetAC',
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
        'armor_class': 10,  # This should be overridden
        'hit_points_max': 13,
        'hit_points_current': 13,
        'hit_dice_max': 1,
        'hit_dice_current': 1,
        'proficiencies': [],
        'features': {},
        'equipment_choices': {},
        'notes': 'Test character sheet AC display'
    }
    
    print("Creating Barbarian to test character sheet AC display...")
    print("Expected Unarmored Defense AC: 10 + 3 (Dex) + 4 (Con) = 17")
    
    # Create character
    created = engine.create_new_character_sync(character_data, save_slot=111)
    
    if created:
        print(f"Character created: {created.name}")
        print(f"CharacterDTO AC: {created.armor_class}")
        
        # Simulate what the main window does when loading character
        from ui.main_window import MainWindow
        
        # Create a mock conversion like main_window._convert_dto_to_display
        character_display_data = {
            'name': created.name,
            'level': created.level,
            'race_name': created.race_name,
            'class_name': created.class_name,
            'background_name': created.background_name,
            'current_hit_points': created.hit_points_current,
            'hit_points': created.hit_points_max,
            'armor_class': created.armor_class,  # This is what character sheet gets
            'strength': created.strength,
            'dexterity': created.dexterity,
            'constitution': created.constitution,
            'intelligence': created.intelligence,
            'wisdom': created.wisdom,
            'charisma': created.charisma,
            'experience_points': created.experience_points,
            'features': created.features,
            'feats': created.feats,
            'speed': 30
        }
        
        print(f"Display data AC (what character sheet sees): {character_display_data['armor_class']}")
        
        # Check database AC directly
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("SELECT armor_class FROM characters WHERE name = ?", (created.name,))
        db_ac = cursor.fetchone()[0]
        conn.close()
        
        print(f"Database AC: {db_ac}")
        
        if db_ac == 17 and character_display_data['armor_class'] == 17:
            print("SUCCESS: Character sheet should display correct AC (17)")
            result = True
        else:
            print(f"ISSUE: Expected AC 17, but CharacterDTO has {created.armor_class} and DB has {db_ac}")
            result = False
        
        # Clean up
        conn = sqlite3.connect("talekeeper.db")
        conn.execute("DELETE FROM characters WHERE name = ?", (created.name,))
        conn.commit()
        conn.close()
        
        return result
    else:
        print("FAIL: Character creation failed")
        return False

if __name__ == "__main__":
    test_character_sheet_ac()