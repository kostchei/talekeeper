"""
Test Barbarian Unarmored Defense AC calculation.
Should be 10 + Dex modifier + Con modifier when no armor is equipped.

For Jarl: STR 16, DEX 13 (+1), CON 18 (+4) = 10 + 1 + 4 = 15 AC
But user mentioned it should be 17 (10+3+4), which suggests DEX 16 (+3), CON 18 (+4)
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_unarmored_defense():
    """Test Barbarian Unarmored Defense AC calculation."""
    
    engine = GameEngineSQLite("talekeeper.db")
    
    # Create Jarl-like Barbarian with high Dex and Con for Unarmored Defense
    character_data = {
        'name': 'TestJarl',
        'race_id': 'human',
        'class_id': 'barbarian',
        'background_id': 'Soldier',
        'level': 1,
        'experience_points': 0,
        'strength': 16,  # +3 mod
        'dexterity': 16, # +3 mod (to match user's example: 10+3+4=17)
        'constitution': 18,  # +4 mod
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'feats': [],
        'armor_class': 10,  # This should be overridden by calculation
        'hit_points_max': 13,
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
        'notes': 'Test Unarmored Defense AC calculation'
    }
    
    print("Creating Barbarian to test Unarmored Defense...")
    print(f"Stats: STR {character_data['strength']} DEX {character_data['dexterity']} CON {character_data['constitution']}")
    
    dex_mod = (character_data['dexterity'] - 10) // 2
    con_mod = (character_data['constitution'] - 10) // 2
    expected_ac = 10 + dex_mod + con_mod
    print(f"Expected Unarmored Defense AC: 10 + {dex_mod} (Dex) + {con_mod} (Con) = {expected_ac}")
    
    created = engine.create_new_character_sync(character_data, save_slot=110)
    
    if created:
        print(f"SUCCESS: Character created: {created.name}")
        print(f"Actual AC: {created.armor_class}")
        
        # Check database directly
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("SELECT armor_class FROM characters WHERE name = ?", (created.name,))
        db_ac = cursor.fetchone()[0]
        conn.close()
        
        print(f"AC in database: {db_ac}")
        
        if db_ac == expected_ac:
            print(f"SUCCESS: Unarmored Defense working! AC is {db_ac} (10 + Dex {dex_mod} + Con {con_mod})")
            result = True
        else:
            print(f"FAIL: Expected AC {expected_ac}, got {db_ac}")
            result = False
        
        # Verify no armor is equipped
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM character_inventory 
            WHERE character_id = ? AND item_type = 'armor' AND equipped = 1
        """, (created.id,))
        equipped_armor_count = cursor.fetchone()[0]
        conn.close()
        
        if equipped_armor_count == 0:
            print("CONFIRMED: No armor equipped (Unarmored Defense should apply)")
        else:
            print(f"WARNING: Found {equipped_armor_count} equipped armor pieces")
        
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
    test_unarmored_defense()