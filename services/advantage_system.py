"""
Centralized Advantage/Disadvantage System for D&D 5e

Handles advantage/disadvantage calculations for all d20 rolls:
- Attack rolls
- Saving throws 
- Initiative rolls
- Skill checks
- Ability checks

Rules:
- Advantage: Roll 2d20, take highest
- Disadvantage: Roll 2d20, take lowest  
- Multiple sources don't stack
- Advantage + Disadvantage = Normal roll (cancel out)
"""

from enum import Enum
from typing import List, Tuple, Dict, Any
import random

class RollType(Enum):
    """Types of d20 rolls that can have advantage/disadvantage."""
    ATTACK = "attack"
    SAVING_THROW = "saving_throw"
    INITIATIVE = "initiative"
    SKILL_CHECK = "skill_check"
    ABILITY_CHECK = "ability_check"

class AdvantageState(Enum):
    """Final advantage state after all sources are considered."""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"

class AdvantageSystem:
    """Centralized system for handling advantage/disadvantage on d20 rolls."""
    
    @staticmethod
    def calculate_advantage_state(advantage_sources: List[str], disadvantage_sources: List[str]) -> AdvantageState:
        """
        Calculate the final advantage state based on all sources.
        
        Args:
            advantage_sources: List of reasons for advantage
            disadvantage_sources: List of reasons for disadvantage
            
        Returns:
            Final advantage state (normal if they cancel out)
        """
        has_advantage = len(advantage_sources) > 0
        has_disadvantage = len(disadvantage_sources) > 0
        
        if has_advantage and has_disadvantage:
            return AdvantageState.NORMAL  # Cancel out
        elif has_advantage:
            return AdvantageState.ADVANTAGE
        elif has_disadvantage:
            return AdvantageState.DISADVANTAGE
        else:
            return AdvantageState.NORMAL
    
    @staticmethod
    def roll_d20_with_advantage(advantage_state: AdvantageState, modifier: int = 0) -> Tuple[int, Dict[str, Any]]:
        """
        Roll a d20 with advantage/disadvantage and return result with breakdown.
        
        Args:
            advantage_state: Whether to roll with advantage, disadvantage, or normal
            modifier: Modifier to add to the roll
            
        Returns:
            Tuple of (final_result, breakdown_dict)
        """
        if advantage_state == AdvantageState.ADVANTAGE:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            d20_result = max(roll1, roll2)
            breakdown = {
                'type': 'advantage',
                'rolls': [roll1, roll2],
                'd20_result': d20_result,
                'modifier': modifier,
                'total': d20_result + modifier,
                'description': f"d20({roll1}, {roll2}) advantage = {d20_result}",
                'has_natural_20': 20 in [roll1, roll2]  # Track if either die was 20
            }
        elif advantage_state == AdvantageState.DISADVANTAGE:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            d20_result = min(roll1, roll2)
            breakdown = {
                'type': 'disadvantage',
                'rolls': [roll1, roll2],
                'd20_result': d20_result,
                'modifier': modifier,
                'total': d20_result + modifier,
                'description': f"d20({roll1}, {roll2}) disadvantage = {d20_result}",
                'has_natural_20': 20 in [roll1, roll2]  # Track if either die was 20
            }
        else:  # Normal roll
            d20_result = random.randint(1, 20)
            breakdown = {
                'type': 'normal',
                'rolls': [d20_result],
                'd20_result': d20_result,
                'modifier': modifier,
                'total': d20_result + modifier,
                'description': f"d20({d20_result})",
                'has_natural_20': d20_result == 20
            }
        
        return breakdown['total'], breakdown
    
    @staticmethod
    def format_roll_description(breakdown: Dict[str, Any]) -> str:
        """
        Format a roll breakdown into a human-readable description.
        
        Args:
            breakdown: Roll breakdown from roll_d20_with_advantage
            
        Returns:
            Formatted description string
        """
        description = breakdown['description']
        modifier = breakdown['modifier']
        total = breakdown['total']
        
        if modifier != 0:
            modifier_str = f"+{modifier}" if modifier > 0 else str(modifier)
            description += f" {modifier_str} = {total}"
        
        return description
    
    @staticmethod
    def get_common_advantage_sources(roll_type: RollType, context: Dict[str, Any]) -> List[str]:
        """
        Get common sources of advantage for different roll types.
        
        Args:
            roll_type: Type of roll being made
            context: Context information (character stats, conditions, etc.)
            
        Returns:
            List of advantage source descriptions
        """
        advantage_sources = []
        
        # Check for general conditions
        if context.get('has_help', False):
            advantage_sources.append("Help action")
        
        if context.get('target_prone', False) and roll_type == RollType.ATTACK:
            advantage_sources.append("Target is prone (melee)")
        
        if context.get('unseen_attacker', False) and roll_type == RollType.ATTACK:
            advantage_sources.append("Unseen attacker")
        
        if context.get('lucky_feat_used', False):
            advantage_sources.append("Lucky feat")
        
        # Class-specific advantages
        if context.get('reckless_attack', False) and roll_type == RollType.ATTACK:
            advantage_sources.append("Reckless Attack")

        if context.get('sneak_attack_advantage', False) and roll_type == RollType.ATTACK:
            advantage_sources.append("Sneak attack conditions")

        # Feat-based and feature-based advantages for initiative
        if roll_type == RollType.INITIATIVE:
            feats = context.get('feats', [])
            if 'Alert' in feats:
                advantage_sources.append("Alert feat")

            # Class features (also check for feats stored in character_features)
            character_features = context.get('character_features', {})
            if 'Alert' in character_features:
                advantage_sources.append("Alert feat")
            if 'Feral Instinct' in character_features:
                advantage_sources.append("Feral Instinct")

        return advantage_sources
    
    @staticmethod
    def get_common_disadvantage_sources(roll_type: RollType, context: Dict[str, Any]) -> List[str]:
        """
        Get common sources of disadvantage for different roll types.
        
        Args:
            roll_type: Type of roll being made
            context: Context information (character stats, conditions, etc.)
            
        Returns:
            List of disadvantage source descriptions
        """
        disadvantage_sources = []
        
        # Check for general conditions
        if context.get('target_prone', False) and roll_type == RollType.ATTACK and context.get('ranged_attack', False):
            disadvantage_sources.append("Target is prone (ranged)")
        
        if context.get('attacker_prone', False) and roll_type == RollType.ATTACK:
            disadvantage_sources.append("Attacker is prone")
        
        if context.get('in_darkness', False):
            disadvantage_sources.append("Darkness/blinded")
        
        if context.get('long_range', False) and roll_type == RollType.ATTACK:
            disadvantage_sources.append("Long range")
        
        # Weapon mastery effects
        if context.get('sap_effect', False) and roll_type == RollType.ATTACK:
            disadvantage_sources.append("Sap weapon mastery")
        
        return disadvantage_sources

# Global instance for easy access
advantage_system = AdvantageSystem()