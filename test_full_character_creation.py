"""
Test full character creation flow for human with bonus feat.
"""

import sys
import sqlite3
from core.game_engine_sqlite import GameEngineSQLite

def test_full_character_creation():
    """Test the full character creation flow for a human with bonus feat."""
    
    # Initialize the game engine
    engine = GameEngineSQLite("talekeeper.db")
    
    # Prepare character data as it would come from the UI
    character_data = {
        'name': 'TestHumanFighter',
        'race_id': 'human',
        'class_id': 'fighter',
        'background_id': 'Soldier',
        'level': 1,
        'experience_points': 0,
        
        # Ability scores
        'strength': 15,
        'dexterity': 14,
        'constitution': 13,
        'intelligence': 12,
        'wisdom': 11,
        'charisma': 10,
        
        # The key part - feats array should contain BOTH feats
        'feats': ['Savage Attacker', 'Tough'],  # Background feat + Human bonus feat
        
        # Other required fields
        'armor_class': 14,
        'hit_points_max': 12,  # Should become 14 after Tough is applied
        'hit_points_current': 12,
        'hit_dice_max': 1,
        'hit_dice_current': 1,
        'proficiencies': [],
        'features': {},
        'notes': 'Test character with human bonus feat'
    }
    
    print(f"Creating character with feats: {character_data['feats']}")
    
    # Find an empty save slot
    save_slots = engine.get_save_slots_sync()
    occupied_numbers = {slot.slot_number for slot in save_slots if slot.is_occupied}
    save_slot = 100  # Use a high number to avoid conflicts
    while save_slot in occupied_numbers:
        save_slot += 1
    
    print(f"Using save slot: {save_slot}")
    
    # Create the character
    created_character = engine.create_new_character_sync(character_data, save_slot=save_slot)
    
    if created_character:
        print(f"\nCharacter created successfully: {created_character.name}")
        print(f"Character ID: {created_character.id}")
        
        # Check the feats in the database
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT feat_name, feat_source 
            FROM character_feats 
            WHERE character_id = ?
            ORDER BY feat_name
        """, (created_character.id,))
        
        saved_feats = cursor.fetchall()
        conn.close()
        
        print(f"\nFeats saved to database:")
        for feat_name, feat_source in saved_feats:
            print(f"  - {feat_name} (source: {feat_source})")
        
        # Verify both feats were saved
        feat_names = [f[0] for f in saved_feats]
        if 'Savage Attacker' in feat_names and 'Tough' in feat_names:
            print("\n[PASS] Both feats saved correctly!")
            return True
        else:
            print(f"\n[FAIL] Expected ['Savage Attacker', 'Tough'], got {feat_names}")
            return False
    else:
        print("[FAIL] Character creation failed")
        return False

if __name__ == "__main__":
    success = test_full_character_creation()
    sys.exit(0 if success else 1)