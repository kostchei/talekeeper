#!/usr/bin/env python3
"""
HP Fix Script for TaleKeeper Characters

This script recalculates HP for all characters to include missing species bonuses 
(like Dwarven Toughness) and feat bonuses (like Tough feat).
"""

import sys
import sqlite3
from pathlib import Path

# Add the TaleKeeper services to the path
sys.path.append(str(Path(__file__).parent))

from services.level_up import LevelUpService


def fix_all_character_hp():
    """Fix HP for all characters in the database."""
    try:
        level_service = LevelUpService()
        
        # Get all characters
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM characters")
        characters = cursor.fetchall()
        conn.close()
        
        if not characters:
            print("No characters found in database.")
            return
        
        print(f"Found {len(characters)} characters. Checking HP calculations...")
        print("=" * 60)
        
        fixed_count = 0
        for character_id, character_name in characters:
            print(f"\nChecking {character_name} (ID: {character_id[:8]}...):")
            
            if level_service.recalculate_character_hp(character_id):
                fixed_count += 1
                print(f"  [FIXED] HP corrected for {character_name}")
            else:
                print(f"  [OK] {character_name} HP already correct")
        
        print("\n" + "=" * 60)
        print(f"HP fix complete! {fixed_count} characters had their HP corrected.")
        
        if fixed_count > 0:
            print("\nNote: Characters that were at full HP remain at full HP with their new maximum.")
            print("Characters that were injured will have their current HP increased by the same amount as their maximum.")
        
    except Exception as e:
        print(f"Error fixing character HP: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("TaleKeeper HP Fix Script")
    print("=" * 60)
    print("This script will recalculate HP for all characters to include:")
    print("- Dwarven Toughness: +1 HP per level for dwarves")
    print("- Tough feat: +2 HP per level")
    print("- Any other species/feat bonuses")
    print()
    
    # Auto-run for CLI environments
    print("Running HP fix...")
    fix_all_character_hp()