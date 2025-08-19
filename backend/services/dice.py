"""
File: backend/services/dice.py
Path: /backend/services/dice.py

Dice rolling system for D&D 2024.
Handles all dice notation parsing and rolling with modifiers.

Pseudo Code:
1. Parse dice notation using regex (e.g., "2d6+3", "1d20")
2. Roll individual dice with random number generation
3. Apply advantage/disadvantage by rolling twice and taking best/worst
4. Handle complex expressions with multiple dice types
5. Return detailed results with individual rolls and totals

AI Agents: Supported formats:
- Simple: "1d20", "2d6", "3d4"
- With modifiers: "1d20+5", "2d6-2"
- Multiple dice: "1d8+1d6+3"
- Advantage/Disadvantage: roll("1d20", advantage=True)
"""

import random
import re
from typing import List, Tuple, Optional
from loguru import logger

class DiceRoller:
    """
    Comprehensive dice rolling system.
    
    AI Agents: Add new dice mechanics here (exploding dice, rerolls, etc.)
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize dice roller.
        
        Args:
            seed: Random seed for testing/reproducibility
        """
        if seed:
            random.seed(seed)
        
        # Regex pattern for dice notation
        self.dice_pattern = re.compile(r'(\d+)d(\d+)')
        self.modifier_pattern = re.compile(r'([+-]\d+)(?!d)')
    
    def roll(self, notation: str, advantage: bool = False, disadvantage: bool = False) -> int:
        """
        Roll dice using standard notation.
        
        Args:
            notation: Dice notation string (e.g., "1d20+5")
            advantage: Roll twice and take higher (for d20 only)
            disadvantage: Roll twice and take lower (for d20 only)
            
        Returns:
            Total result of all dice and modifiers
            
        Examples:
            roll("1d20") -> 15
            roll("2d6+3") -> 10
            roll("1d20", advantage=True) -> 18
        """
        try:
            # Handle advantage/disadvantage for d20 rolls
            if "1d20" in notation and (advantage or disadvantage):
                return self._roll_with_advantage(notation, advantage)
            
            # Parse dice and modifiers
            total = 0
            
            # Find all dice groups (e.g., "2d6")
            dice_matches = self.dice_pattern.findall(notation)
            for num_dice, die_size in dice_matches:
                num_dice = int(num_dice)
                die_size = int(die_size)
                
                # Roll each die
                for _ in range(num_dice):
                    roll = random.randint(1, die_size)
                    total += roll
            
            # Find all modifiers (e.g., "+5", "-2")
            modifier_matches = self.modifier_pattern.findall(notation)
            for modifier in modifier_matches:
                total += int(modifier)
            
            return max(0, total)  # Never return negative
            
        except Exception as e:
            logger.error(f"Error rolling dice '{notation}': {e}")
            return 0
    
    def _roll_with_advantage(self, notation: str, advantage: bool) -> int:
        """Handle advantage/disadvantage for d20 rolls"""
        # Remove the 1d20 part to get modifiers
        modifiers = notation.replace("1d20", "")
        
        # Roll twice
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        
        # Take higher or lower
        base_roll = max(roll1, roll2) if advantage else min(roll1, roll2)
        
        # Add modifiers
        modifier_total = 0
        modifier_matches = self.modifier_pattern.findall(modifiers)
        for modifier in modifier_matches:
            modifier_total += int(modifier)
        
        logger.debug(f"Advantage/Disadvantage: rolled {roll1} and {roll2}, used {base_roll}")
        
        return base_roll + modifier_total
    
    def roll_stats(self, method: str = "standard") -> List[int]:
        """
        Roll ability scores for character creation.
        
        Args:
            method: Rolling method
                - "standard": 4d6 drop lowest
                - "classic": 3d6 straight
                - "heroic": 5d6 drop 2 lowest
                
        Returns:
            List of 6 ability scores
            
        AI Agents: Add new stat generation methods here
        """
        scores = []
        
        for _ in range(6):
            if method == "standard":
                # Roll 4d6, drop lowest
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.sort(reverse=True)
                scores.append(sum(rolls[:3]))
            
            elif method == "classic":
                # Roll 3d6
                scores.append(sum(random.randint(1, 6) for _ in range(3)))
            
            elif method == "heroic":
                # Roll 5d6, drop 2 lowest
                rolls = [random.randint(1, 6) for _ in range(5)]
                rolls.sort(reverse=True)
                scores.append(sum(rolls[:3]))
            
            else:
                # Default to standard array
                return [15, 14, 13, 12, 10, 8]
        
        return scores
    
    def roll_hit_points(self, hit_die: int, con_modifier: int, level: int) -> int:
        """
        Roll hit points for leveling up.
        
        Args:
            hit_die: Size of hit die (6, 8, 10, 12)
            con_modifier: Constitution modifier
            level: Character level
            
        Returns:
            Total hit points
        """
        # Level 1 gets max hit die + con
        hp = hit_die + con_modifier
        
        # Additional levels roll
        for _ in range(2, level + 1):
            roll = random.randint(1, hit_die)
            hp += roll + con_modifier
        
        return max(1, hp)  # Minimum 1 HP
    
    def roll_initiative(self, dex_modifier: int, bonus: int = 0) -> int:
        """
        Roll initiative for combat.
        
        Args:
            dex_modifier: Dexterity modifier
            bonus: Additional bonuses (e.g., from feats)
            
        Returns:
            Initiative result
        """
        return self.roll("1d20") + dex_modifier + bonus
    
    def roll_percentile(self) -> int:
        """Roll d100 (percentile dice)"""
        return random.randint(1, 100)
    
    def roll_on_table(self, table: List[Tuple[int, any]]) -> any:
        """
        Roll on a weighted table.
        
        Args:
            table: List of (weight, result) tuples
            
        Returns:
            Selected result based on weights
            
        Example:
            table = [(50, "common"), (30, "uncommon"), (20, "rare")]
            roll_on_table(table) -> "common" (50% chance)
        """
        total_weight = sum(weight for weight, _ in table)
        roll = random.randint(1, total_weight)
        
        current = 0
        for weight, result in table:
            current += weight
            if roll <= current:
                return result
        
        return table[-1][1]  # Fallback to last item
    
    def roll_multiple(self, notation: str, count: int) -> List[int]:
        """
        Roll the same dice notation multiple times.
        
        Args:
            notation: Dice notation
            count: Number of times to roll
            
        Returns:
            List of results
        """
        return [self.roll(notation) for _ in range(count)]
    
    def roll_with_reroll(self, notation: str, reroll_on: List[int], max_rerolls: int = 1) -> int:
        """
        Roll with reroll mechanic.
        
        Args:
            notation: Dice notation
            reroll_on: Values that trigger a reroll
            max_rerolls: Maximum number of rerolls
            
        Returns:
            Final result
            
        AI Agents: Use for abilities like "Great Weapon Fighting"
        """
        result = self.roll(notation)
        rerolls = 0
        
        while result in reroll_on and rerolls < max_rerolls:
            logger.debug(f"Rerolling {result}")
            result = self.roll(notation)
            rerolls += 1
        
        return result
    
    def roll_exploding(self, notation: str, explode_on: Optional[List[int]] = None) -> int:
        """
        Roll with exploding dice (roll again on max).
        
        Args:
            notation: Dice notation (single die type)
            explode_on: Values that trigger explosion (default: max value)
            
        Returns:
            Total including explosions
            
        AI Agents: Use for critical hit mechanics or special abilities
        """
        # Parse the dice notation
        match = self.dice_pattern.search(notation)
        if not match:
            return self.roll(notation)
        
        num_dice, die_size = int(match.group(1)), int(match.group(2))
        
        if explode_on is None:
            explode_on = [die_size]
        
        total = 0
        for _ in range(num_dice):
            roll = random.randint(1, die_size)
            total += roll
            
            # Keep rolling while exploding
            while roll in explode_on:
                roll = random.randint(1, die_size)
                total += roll
                logger.debug(f"Explosion! Rolled {roll}")
        
        # Add modifiers
        modifier_matches = self.modifier_pattern.findall(notation)
        for modifier in modifier_matches:
            total += int(modifier)
        
        return total

# Global instance for convenience
dice = DiceRoller()

# Utility functions for common rolls
def d20(modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> int:
    """Quick d20 roll with modifier"""
    notation = f"1d20{modifier:+d}" if modifier else "1d20"
    return dice.roll(notation, advantage, disadvantage)

def attack_roll(bonus: int, advantage: bool = False, disadvantage: bool = False) -> Tuple[int, bool, bool]:
    """
    Make an attack roll.
    
    Returns:
        (total, is_critical, is_fumble)
    """
    base_roll = random.randint(1, 20)
    
    if advantage or disadvantage:
        second_roll = random.randint(1, 20)
        base_roll = max(base_roll, second_roll) if advantage else min(base_roll, second_roll)
    
    total = base_roll + bonus
    is_critical = base_roll == 20
    is_fumble = base_roll == 1
    
    return total, is_critical, is_fumble

def saving_throw(ability_mod: int, proficiency: int = 0, advantage: bool = False) -> int:
    """Make a saving throw"""
    return d20(ability_mod + proficiency, advantage)

def skill_check(ability_mod: int, proficiency: int = 0, expertise: bool = False, advantage: bool = False) -> int:
    """Make a skill check"""
    bonus = ability_mod + (proficiency * 2 if expertise else proficiency)
    return d20(bonus, advantage)

__all__ = [
    'DiceRoller',
    'dice',
    'd20',
    'attack_roll',
    'saving_throw',
    'skill_check'
]