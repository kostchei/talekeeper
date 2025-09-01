"""
Test Jarl's specific AC calculation.
User said Jarl should have 17 AC (10+3+4), so let's verify the exact stats.
"""

from core.game_engine_sqlite import GameEngineSQLite
import sqlite3

def test_jarl_specific_ac():
    """Test Jarl's specific Unarmored Defense AC."""
    
    # Test different stat combinations that give AC 17
    test_cases = [
        {"name": "Jarl_Case1", "dex": 16, "con": 18, "expected_ac": 17, "description": "DEX 16 (+3), CON 18 (+4)"},
        {"name": "Jarl_Case2", "dex": 14, "con": 20, "expected_ac": 17, "description": "DEX 14 (+2), CON 20 (+5)"},
        {"name": "Jarl_Case3", "dex": 18, "con": 16, "expected_ac": 17, "description": "DEX 18 (+4), CON 16 (+3)"},
    ]
    
    engine = GameEngineSQLite("talekeeper.db")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {test_case['description']} ===")
        
        character_data = {
            'name': test_case['name'],
            'race_id': 'human',
            'class_id': 'barbarian',
            'background_id': 'Soldier',
            'level': 1,
            'experience_points': 0,
            'strength': 16,
            'dexterity': test_case['dex'],
            'constitution': test_case['con'],
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
            'notes': 'Test Jarl AC calculation'
        }
        
        dex_mod = (test_case['dex'] - 10) // 2
        con_mod = (test_case['con'] - 10) // 2
        calculated_ac = 10 + dex_mod + con_mod
        
        print(f"Stats: DEX {test_case['dex']} ({dex_mod:+d}) CON {test_case['con']} ({con_mod:+d})")
        print(f"Expected AC: 10 + {dex_mod} + {con_mod} = {calculated_ac}")
        
        created = engine.create_new_character_sync(character_data, save_slot=110 + i)
        
        if created:
            print(f"Actual AC: {created.armor_class}")
            
            if created.armor_class == test_case['expected_ac']:
                print(f"✅ SUCCESS: AC matches expected {test_case['expected_ac']}")
            else:
                print(f"❌ FAIL: Expected {test_case['expected_ac']}, got {created.armor_class}")
            
            # Clean up
            conn = sqlite3.connect("talekeeper.db")
            conn.execute("DELETE FROM characters WHERE name = ?", (created.name,))
            conn.commit()
            conn.close()

if __name__ == "__main__":
    test_jarl_specific_ac()