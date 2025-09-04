"""
Test script for the town encounter system.
Tests XP-based level up availability and training hall functionality.
"""

import sqlite3
import sys
import os
from datetime import datetime

def test_town_encounter_system():
    """Test the town encounter system by setting up test conditions"""
    
    db_path = "talekeeper.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Find a test character
        cursor.execute("SELECT id, name, level, experience_points FROM characters LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            print("No characters found in database!")
            return False
        
        character_id, name, level, current_xp = result
        print(f"Found character: {name} (Level {level}, {current_xp} XP)")
        
        # XP thresholds for each level
        xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
            100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        
        if level >= 20:
            print("Character is already max level!")
            return True
        
        next_level_xp = xp_thresholds[level] if level < len(xp_thresholds) else xp_thresholds[-1]
        
        print(f"XP needed for level {level + 1}: {next_level_xp}")
        
        # Check if character can level up
        can_level_up = current_xp >= next_level_xp
        print(f"Can level up: {can_level_up}")
        
        if not can_level_up:
            # Give character enough XP to level up
            new_xp = next_level_xp + 50  # A bit extra
            print(f"Setting character XP to {new_xp} (was {current_xp})")
            
            cursor.execute("""
                UPDATE characters 
                SET experience_points = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (new_xp, character_id))
        
        # Check character's gold
        cursor.execute("""
            SELECT quantity FROM character_inventory 
            WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
        """, (character_id,))
        
        gold_result = cursor.fetchone()
        current_gold = gold_result[0] if gold_result else 0
        print(f"Character has {current_gold} gold pieces")
        
        # Check training costs
        cursor.execute("""
            SELECT training_cost_gp, training_days 
            FROM levelup_costs 
            WHERE ? BETWEEN level_range_start AND level_range_end
        """, (level + 1,))
        
        cost_result = cursor.fetchone()
        if cost_result:
            cost, days = cost_result
            print(f"Training cost for level {level + 1}: {cost} GP, {days} days")
            
            if current_gold < cost:
                # Give character enough gold
                needed_gold = cost + 50  # A bit extra
                print(f"Adding gold to character (need {needed_gold}, have {current_gold})")
                
                if gold_result:
                    # Update existing gold
                    cursor.execute("""
                        UPDATE character_inventory 
                        SET quantity = ?
                        WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
                    """, (needed_gold, character_id))
                else:
                    # Insert new gold entry
                    import uuid
                    cursor.execute("""
                        INSERT INTO character_inventory 
                        (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped)
                        VALUES (?, ?, 'Gold Pieces', 'treasure', ?, 0, 'Currency', 1, 0)
                    """, (str(uuid.uuid4()), character_id, needed_gold))
        else:
            print(f"No training cost data found for level {level + 1}")
        
        conn.commit()
        print("Test setup complete!")
        print(f"Character {name} should now be able to level up with sufficient gold.")
        print("Start TaleKeeper to see the town tab appear!")
        
        return True
        
    except Exception as e:
        print(f"Error during test setup: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def reset_character_for_testing():
    """Reset character to level 1 with 250 XP (just below level 2) for testing"""
    
    db_path = "talekeeper.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Find a test character
        cursor.execute("SELECT id, name FROM characters LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            print("No characters found!")
            return False
        
        character_id, name = result
        
        # Reset to level 1 with 250 XP (need 300 for level 2)
        cursor.execute("""
            UPDATE characters 
            SET level = 1, experience_points = 250, updated_at = datetime('now')
            WHERE id = ?
        """, (character_id,))
        
        print(f"Reset {name} to level 1 with 250 XP")
        print("Give them 50+ more XP to trigger level up availability!")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error resetting character: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("Town Encounter System Test")
    print("="*50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        print("Resetting character for testing...")
        reset_character_for_testing()
    else:
        print("Setting up character to test town encounter...")
        test_town_encounter_system()
    
    print("\nUsage:")
    print("  python test_town_encounter.py        - Setup character for level up")
    print("  python test_town_encounter.py reset  - Reset character to level 1")