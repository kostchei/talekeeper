# core
# core
"""
Treasure rarity system for TaleKeeper.
Determines item rarity based on character level using D&D 5e treasure tables.
"""

import sqlite3
import random
from typing import Optional, List, Dict, Any


class TreasureRaritySystem:
    """Helper class for determining treasure rarity based on level."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
    
    def get_rarity_for_level(self, character_level: int) -> str:
        """
        Roll for item rarity based on character level.
        
        Args:
            character_level: The character's current level (1-20)
            
        Returns:
            Rarity string: 'common', 'uncommon', 'rare', 'very rare', or 'legendary'
        """
        roll = random.randint(1, 100)
        return self.get_rarity_for_level_and_roll(character_level, roll)
    
    def get_rarity_for_level_and_roll(self, character_level: int, roll: int) -> str:
        """
        Get item rarity for a specific level and roll.
        
        Args:
            character_level: The character's current level (1-20)
            roll: The d100 roll result (1-100)
            
        Returns:
            Rarity string: 'common', 'uncommon', 'rare', 'very rare', or 'legendary'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT rarity 
                FROM item_rarity_table 
                WHERE min_level <= ? AND max_level >= ? 
                  AND roll_min <= ? AND roll_max >= ?
                LIMIT 1
            """, (character_level, character_level, roll, roll))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                # Fallback for invalid levels
                return 'common' if character_level < 5 else 'uncommon'
                
        finally:
            conn.close()
    
    def get_rarity_ranges_for_level(self, character_level: int) -> List[Dict[str, Any]]:
        """
        Get all possible rarity ranges for a given level.
        
        Args:
            character_level: The character's current level (1-20)
            
        Returns:
            List of dictionaries with rarity info
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT level_range, rarity, roll_min, roll_max 
                FROM item_rarity_table 
                WHERE min_level <= ? AND max_level >= ?
                ORDER BY roll_min
            """, (character_level, character_level))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_rarity_probability(self, character_level: int, target_rarity: str) -> float:
        """
        Get the probability (0.0-1.0) of getting a specific rarity at a level.
        
        Args:
            character_level: The character's current level (1-20)
            target_rarity: The rarity to check probability for
            
        Returns:
            Probability as a float (0.0 = 0%, 1.0 = 100%)
        """
        ranges = self.get_rarity_ranges_for_level(character_level)
        
        total_range = 0
        for range_info in ranges:
            if range_info['rarity'] == target_rarity:
                range_size = range_info['roll_max'] - range_info['roll_min'] + 1
                total_range += range_size
        
        return total_range / 100.0  # Convert to probability (out of 100 possible rolls)
    
    def get_level_bracket(self, character_level: int) -> str:
        """Get the level bracket name for a character level."""
        if 1 <= character_level <= 4:
            return "1-4"
        elif 5 <= character_level <= 10:
            return "5-10"
        elif 11 <= character_level <= 16:
            return "11-16"
        elif 17 <= character_level <= 20:
            return "17-20"
        else:
            return "1-4"  # Default fallback


# Example usage and testing
if __name__ == "__main__":
    rarity_system = TreasureRaritySystem()
    
    # Test different level brackets
    test_levels = [2, 7, 13, 19]
    
    for level in test_levels:
        print(f"\nLevel {level} ({rarity_system.get_level_bracket(level)}):")
        
        ranges = rarity_system.get_rarity_ranges_for_level(level)
        for range_info in ranges:
            prob = rarity_system.get_rarity_probability(level, range_info['rarity'])
            print(f"  {range_info['rarity'].title()}: {range_info['roll_min']}-{range_info['roll_max']} ({prob*100:.0f}%)")
        
        # Test some sample rolls
        print("  Sample rolls:")
        for _ in range(3):
            rarity = rarity_system.get_rarity_for_level(level)
            print(f"    {rarity}")