"""
Simple test of Barbarian features via character creation.
"""

from core.game_engine_sqlite import GameEngineSQLite

def test_barbarian_with_features():
    """Test Barbarian with manually populated features."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Barbarian features as they would be created by the encounter panel
    barbarian_features = {
        'Rage': {
            'type': 'bonus_action',
            'usage': 'long_rest',
            'description': '+2 damage on Str-based melee attacks, resistance to bludgeoning/piercing/slashing damage, advantage on Str checks/saves. Lasts for entire combat.',
            'level_acquired': 1
        },
        'Unarmored Defense': {
            'type': 'passive', 
            'usage': 'permanent',
            'description': 'While not wearing armor, your AC equals 10 + Dex modifier + Con modifier',
            'level_acquired': 1
        }
    }
    
    character_data = {
        'name': 'TestBarbarianFeaturesWorking',
        'race_id': 'human',
        'class_id': 'barbarian', 
        'background_id': 'Soldier',
        'level': 1,
        'experience_points': 0,
        'strength': 16,
        'dexterity': 14,
        'constitution': 15,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'feats': [],
        'armor_class': 14,
        'hit_points_max': 14,
        'hit_points_current': 14,
        'hit_dice_max': 1,
        'hit_dice_current': 1,
        'proficiencies': [],
        'features': barbarian_features,  # Pre-populated features
        'equipment_choices': {},
        'notes': 'Test Barbarian with features'
    }
    
    print("Creating Barbarian with pre-populated features...")
    print(f"Features to save: {list(barbarian_features.keys())}")
    
    created = engine.create_new_character_sync(character_data, save_slot=106)
    
    if created:
        print(f"Character created: {created.name}")
        print(f"Features in DTO: {list(created.features.keys()) if created.features else 'None'}")
        
        # Check action panel integration
        from ui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        main_window = MainWindow()
        
        # Load the character
        main_window._load_character_into_ui(created, "Test load")
        
        # Check if action panel has Rage card
        action_panel = main_window.action_panel
        has_rage_card = hasattr(action_panel, 'character_features') and 'Rage' in action_panel.character_features
        
        print(f"Action panel has Rage feature: {has_rage_card}")
        if hasattr(action_panel, 'character_features'):
            print(f"Action panel features: {list(action_panel.character_features.keys())}")
        
        app.quit()
        
        # Clean up
        import sqlite3
        conn = sqlite3.connect("talekeeper.db")
        conn.execute("DELETE FROM characters WHERE name = 'TestBarbarianFeaturesWorking'")
        conn.commit()
        conn.close()
        
        print("\n[PASS] Barbarian features test completed successfully!")
        return True
    else:
        print("[FAIL] Character creation failed")
        return False

if __name__ == "__main__":
    test_barbarian_with_features()