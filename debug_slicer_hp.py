#!/usr/bin/env python3
"""Debug Slicer's HP calculation."""

import sqlite3

def debug_slicer_hp():
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get Slicer's data
    cursor.execute("""
        SELECT level, class_id, constitution, hit_points_max, race_id, name
        FROM characters WHERE name = 'Slicer'
    """)
    char_data = cursor.fetchone()
    
    if not char_data:
        print("Slicer not found!")
        return
        
    level, class_id, con_score, current_max_hp, race_id, name = char_data
    con_modifier = (con_score - 10) // 2
    
    print(f"=== {name} HP Debug ===")
    print(f"Level: {level}")
    print(f"Class: {class_id}")
    print(f"Constitution: {con_score} (modifier: {con_modifier:+d})")
    print(f"Race: {race_id}")
    print(f"Current Max HP: {current_max_hp}")
    print()
    
    # Calculate what HP should be
    hit_die_map = {'barbarian': 12, 'fighter': 10, 'rogue': 8, 'cleric': 8, 'wizard': 6}
    hit_die = hit_die_map.get(class_id.lower(), 8)
    
    print(f"Hit Die: d{hit_die}")
    
    # Level 1 HP (max hit die + CON)
    level_1_hp = hit_die + con_modifier
    print(f"Level 1: {hit_die} (max d{hit_die}) + {con_modifier:+d} (CON) = {level_1_hp}")
    
    # Subsequent levels (average hit die + CON)  
    avg_hp_per_level = (hit_die // 2 + 1) + con_modifier
    total_base_hp = level_1_hp
    
    for lv in range(2, level + 1):
        print(f"Level {lv}: {hit_die//2 + 1} (avg d{hit_die}) + {con_modifier:+d} (CON) = +{avg_hp_per_level}")
        total_base_hp += avg_hp_per_level
    
    print(f"Total Base HP: {total_base_hp}")
    print()
    
    # Check feats
    cursor.execute("SELECT feat_name FROM character_feats WHERE character_id = (SELECT id FROM characters WHERE name = 'Slicer')")
    feats = [row[0] for row in cursor.fetchall()]
    
    print("Feats:")
    feat_hp_bonus = 0
    for feat in feats:
        print(f"  - {feat}")
        if feat == 'Tough':
            tough_bonus = level * 2
            feat_hp_bonus += tough_bonus
            print(f"    -> Tough: +{tough_bonus} HP ({level} levels × 2)")
    
    print(f"Total Feat HP Bonus: +{feat_hp_bonus}")
    print()
    
    # Species bonus
    species_hp_bonus = 0
    if race_id.lower() in ['dwarf', 'dwarves']:
        species_hp_bonus = level
        print(f"Species HP Bonus: +{species_hp_bonus} (Dwarven Toughness)")
    else:
        print(f"Species HP Bonus: +{species_hp_bonus} (no bonus for {race_id})")
    
    print()
    
    # Final calculation
    correct_hp = total_base_hp + feat_hp_bonus + species_hp_bonus
    print(f"CORRECT HP CALCULATION:")
    print(f"  Base: {total_base_hp}")
    print(f"  Feats: +{feat_hp_bonus}")  
    print(f"  Species: +{species_hp_bonus}")
    print(f"  TOTAL: {correct_hp}")
    print()
    print(f"Current in DB: {current_max_hp}")
    print(f"Should be: {correct_hp}")
    print(f"Difference: {correct_hp - current_max_hp:+d}")
    
    conn.close()

if __name__ == "__main__":
    debug_slicer_hp()