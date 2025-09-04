#!/usr/bin/env python3
"""
Utility script to fix characters with double-counted Tough feat HP.
"""

import sqlite3
from services.level_up import LevelUpService

def fix_character_hp(character_name=None):
    """Fix HP for characters affected by Tough feat double-counting."""
    
    conn = sqlite3.connect("talekeeper.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Find characters with Tough feat
        if character_name:
            cursor.execute("""
                SELECT c.id, c.name, c.level, c.hit_points_max, c.constitution, c.class_id, c.race_id
                FROM characters c
                INNER JOIN character_feats cf ON c.id = cf.character_id
                WHERE cf.feat_name = 'Tough' AND c.name = ?
            """, (character_name,))
        else:
            cursor.execute("""
                SELECT c.id, c.name, c.level, c.hit_points_max, c.constitution, c.class_id, c.race_id
                FROM characters c
                INNER JOIN character_feats cf ON c.id = cf.character_id
                WHERE cf.feat_name = 'Tough'
            """)
        
        characters = cursor.fetchall()
        
        if not characters:
            print(f"No characters found with Tough feat" + (f" named '{character_name}'" if character_name else ""))
            return
        
        level_up_service = LevelUpService()
        
        for char in characters:
            char_id = char['id']
            name = char['name']
            level = char['level']
            current_max_hp = char['hit_points_max']
            constitution = char['constitution']
            class_id = char['class_id']
            race_id = char['race_id']
            
            print(f"\n=== Analyzing {name} (Level {level} {race_id.title()} {class_id}) ===")
            print(f"Current HP: {current_max_hp}")
            
            # Calculate what HP should actually be
            hit_die = level_up_service._get_hit_die_for_class(class_id)
            con_modifier = (constitution - 10) // 2
            
            # Base HP calculation (first level gets max hit die, others get average)
            if level == 1:
                base_hp = hit_die + con_modifier
            else:
                # First level: max hit die + CON
                # Additional levels: average hit die + CON per level
                avg_hp_per_level = (hit_die // 2 + 1) + con_modifier
                base_hp = hit_die + con_modifier + (avg_hp_per_level * (level - 1))
            
            # Add species bonuses
            species_hp_bonus = 0
            if race_id.lower() in ['dwarf', 'dwarves']:
                species_hp_bonus = level  # +1 per level
            
            # Add correct Tough feat bonus
            tough_hp_bonus = level * 2  # +2 per level
            
            correct_max_hp = base_hp + species_hp_bonus + tough_hp_bonus
            hp_difference = correct_max_hp - current_max_hp
            
            print(f"Calculated HP breakdown:")
            print(f"  Base HP: {base_hp} (d{hit_die} + CON)")
            print(f"  Species bonus: +{species_hp_bonus}")
            print(f"  Tough feat: +{tough_hp_bonus}")
            print(f"  Total should be: {correct_max_hp}")
            print(f"  Difference: {hp_difference:+d}")
            
            if hp_difference != 0:
                print(f"[FIXING] Adjusting {name}'s HP by {hp_difference:+d}")
                
                # Update character HP
                cursor.execute("""
                    UPDATE characters 
                    SET hit_points_max = ?,
                        max_hit_points = ?,
                        hit_points_current = hit_points_current + ?,
                        current_hit_points = current_hit_points + ?
                    WHERE id = ?
                """, (correct_max_hp, correct_max_hp, hp_difference, hp_difference, char_id))
                
                print(f"[SUCCESS] Fixed {name}: {current_max_hp} -> {correct_max_hp} HP")
            else:
                print(f"[OK] {name}'s HP is already correct")
        
        conn.commit()
        print(f"\nHP fix completed for {len(characters)} character(s)")
        
    except Exception as e:
        print(f"Error fixing character HP: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    print("Tough Feat HP Fix Utility")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        character_name = sys.argv[1]
        print(f"Fixing HP for character: {character_name}")
        fix_character_hp(character_name)
    else:
        print("Fixing HP for all characters with Tough feat")
        fix_character_hp()
    
    print("\nTo fix a specific character: python fix_tough_feat_hp.py \"Character Name\"")