#!/usr/bin/env python
"""Test what the UI should show for saving throws"""

from services.proficiency_system import ProficiencySystem
from services.proficiency_bonus import get_proficiency_bonus
import sqlite3

def test_ui_saving_throws():
    char_id = 'c044f0b4-b994-4c0f-b142-b41f6b69d7e0'  # tt
    
    # Get character data like the UI does
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, level, strength, dexterity, constitution, intelligence, wisdom, charisma
        FROM characters WHERE id = ?
    """, (char_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("Character not found!")
        return
    
    name, level, str_val, dex_val, con_val, int_val, wis_val, cha_val = row
    
    # Calculate like the UI does
    proficiency_bonus = get_proficiency_bonus(level)
    proficiency_system = ProficiencySystem()
    
    character_data = {'id': char_id}
    character_id = character_data.get('id')
    char_proficiencies = proficiency_system.get_character_proficiencies(character_id) if character_id else {
        'skill': [], 'saving_throw': [], 'weapon': [], 'armor': [], 'tool': [], 'language': []
    }
    
    abilities = {
        'STRENGTH': str_val,
        'DEXTERITY': dex_val,
        'CONSTITUTION': con_val,
        'INTELLIGENCE': int_val,
        'WISDOM': wis_val,
        'CHARISMA': cha_val
    }
    
    print(f"{name} - Level {level} Fighter")
    print("=" * 40)
    print(f"Proficiency bonus: +{proficiency_bonus}")
    print(f"Save proficiencies: {char_proficiencies.get('saving_throw', [])}")
    print()
    
    # Update saving throws like the UI does
    save_proficiencies = char_proficiencies.get('saving_throw', [])
    
    saving_throw_widgets = {
        'STRENGTH': 'str_widget',
        'DEXTERITY': 'dex_widget', 
        'CONSTITUTION': 'con_widget',
        'INTELLIGENCE': 'int_widget',
        'WISDOM': 'wis_widget',
        'CHARISMA': 'cha_widget'
    }
    
    print("Saving Throw Calculations (as UI should show):")
    for ability_name, widget_name in saving_throw_widgets.items():
        if ability_name in abilities:
            ability_score = abilities.get(ability_name, 10)
            ability_mod = (ability_score - 10) // 2
            
            # Check for saving throw proficiency using new proficiency system
            is_proficient = ability_name.lower() in [save.lower() for save in save_proficiencies]
            
            save_bonus = ability_mod + (proficiency_bonus if is_proficient else 0)
            bonus_text = f"+{save_bonus}" if save_bonus >= 0 else str(save_bonus)
            
            diamond = "♦" if is_proficient else "○"
            
            print(f"{ability_name:12} {ability_score:2d} ({ability_mod:+2d}) = {bonus_text:3s} {diamond}")

if __name__ == "__main__":
    test_ui_saving_throws()