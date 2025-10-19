# core
# core
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
from typing import List, Tuple, Dict, Any, Optional, Set
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
    def _normalize_feature_name(candidate: Any) -> Optional[str]:
        """Normalize feature descriptors to lowercase names when possible."""
        if isinstance(candidate, str):
            return candidate.strip().lower()
        if isinstance(candidate, dict):
            name = candidate.get('name') or candidate.get('feature_name')
            if isinstance(name, str):
                return name.strip().lower()
        return None

    @classmethod
    def _collection_has_feature(cls, candidate: Any, candidate_names: Set[str]) -> bool:
        """Check nested feature collections (dicts/lists) for a matching feature name."""
        if candidate is None:
            return False
        normalized = cls._normalize_feature_name(candidate)
        if normalized and normalized in candidate_names:
            return True
        if isinstance(candidate, dict):
            for key, value in candidate.items():
                if cls._collection_has_feature(key, candidate_names):
                    return True
                if cls._collection_has_feature(value, candidate_names):
                    return True
            return False
        if isinstance(candidate, (list, tuple, set)):
            for entry in candidate:
                if cls._collection_has_feature(entry, candidate_names):
                    return True
        return False

    @classmethod
    def _context_has_feature(cls, context: Dict[str, Any], *names: str) -> bool:
        """Determine if any of the provided feature names appear in the roll context."""
        if not context:
            return False
        candidate_names: Set[str] = set()
        for name in names:
            if not name:
                continue
            normalized = name.strip().lower()
            candidate_names.add(normalized)
            candidate_names.add(normalized.replace('_', ' '))
            candidate_names.add(normalized.replace(' ', '_'))
        if not candidate_names:
            return False
        for key in list(candidate_names):
            if context.get(key):
                return True
        feature_flags = context.get('feature_flags')
        if isinstance(feature_flags, dict):
            for key in candidate_names:
                flag_value = feature_flags.get(key)
                if isinstance(flag_value, bool) and flag_value:
                    return True
                if isinstance(flag_value, str) and flag_value.strip():
                    return True
        for collection_key in ('character_features', 'features', 'feature_list', 'feats'):
            if cls._collection_has_feature(context.get(collection_key), candidate_names):
                return True
        return False

    @classmethod
    def _context_has_remarkable_athlete(cls, context: Dict[str, Any]) -> bool:
        """Check whether Remarkable Athlete is present in the context."""
        return cls._context_has_feature(context, 'remarkable athlete', 'remarkable_athlete')

    @staticmethod
    def _is_athletics_check(context: Dict[str, Any]) -> bool:
        """Determine if the current context refers to an Athletics skill check."""
        for key in ('skill_name', 'skill', 'skill_id', 'skill_key'):
            value = context.get(key) if context else None
            if isinstance(value, str) and value.strip().lower() == 'athletics':
                return True
        return False

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
        advantage_sources: List[str] = []

        def append_unique(label: str) -> None:
            if label and label not in advantage_sources:
                advantage_sources.append(label)

        if context.get('has_help', False):
            append_unique('Help action')

        if roll_type == RollType.ATTACK and context.get('target_prone', False):
            append_unique('Target is prone (melee)')

        if roll_type == RollType.ATTACK and context.get('unseen_attacker', False):
            append_unique('Unseen attacker')

        if context.get('lucky_feat_used', False):
            append_unique('Lucky feat')

        if roll_type == RollType.ATTACK and context.get('reckless_attack', False):
            append_unique('Reckless Attack')

        if roll_type == RollType.ATTACK and context.get('sneak_attack_advantage', False):
            append_unique('Sneak attack conditions')

        if roll_type == RollType.INITIATIVE:
            if AdvantageSystem._context_has_feature(context, 'alert'):
                append_unique('Alert feat')
            if AdvantageSystem._context_has_feature(context, 'feral instinct'):
                append_unique('Feral Instinct')
            if AdvantageSystem._context_has_remarkable_athlete(context):
                append_unique('Remarkable Athlete')
        elif roll_type == RollType.SKILL_CHECK:
            if (AdvantageSystem._context_has_remarkable_athlete(context) and
                    AdvantageSystem._is_athletics_check(context)):
                append_unique('Remarkable Athlete')

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

        # Check for condition-based disadvantage
        character_id = context.get('character_id')
        if character_id:
            condition_disadvantage = AdvantageSystem._get_condition_disadvantage_sources(
                character_id, roll_type, context
            )
            disadvantage_sources.extend(condition_disadvantage)

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

        # Check for condition-based advantage
        character_id = context.get('character_id')
        if character_id:
            condition_advantage = AdvantageSystem._get_condition_advantage_sources(
                character_id, roll_type, context
            )
            advantage_sources.extend(condition_advantage)

        # Check for general advantage conditions
        if context.get('target_prone', False) and roll_type == RollType.ATTACK and not context.get('ranged_attack', False):
            advantage_sources.append("Target is prone (melee)")

        if context.get('unseen_attacker', False) and roll_type == RollType.ATTACK:
            advantage_sources.append("Unseen attacker")

        return advantage_sources

    @staticmethod
    def _get_condition_disadvantage_sources(character_id: str, roll_type: RollType, context: Dict[str, Any]) -> List[str]:
        """Get disadvantage sources from character conditions."""
        try:
            from services.condition_stat_service import condition_stat_service

            sources = []

            if roll_type == RollType.ATTACK:
                modifiers = condition_stat_service.get_attack_roll_modifier(character_id)
                if modifiers.get("disadvantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "disadvantage" in s])

            elif roll_type == RollType.SAVING_THROW:
                ability = context.get('ability', 'constitution')
                modifiers = condition_stat_service.get_saving_throw_modifier(character_id, ability)
                if modifiers.get("disadvantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "disadvantage" in s])

            elif roll_type in [RollType.ABILITY_CHECK, RollType.SKILL_CHECK]:
                ability = context.get('ability', 'strength')
                modifiers = condition_stat_service.get_ability_check_modifier(character_id, ability)
                if modifiers.get("disadvantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "disadvantage" in s])

            elif roll_type == RollType.INITIATIVE:
                modifiers = condition_stat_service.get_initiative_modifier(character_id)
                if modifiers.get("disadvantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "disadvantage" in s])

            return sources

        except ImportError:
            return []
        except Exception as e:
            print(f"[AdvantageSystem] Error getting condition disadvantage: {e}")
            return []

    @staticmethod
    def _get_condition_advantage_sources(character_id: str, roll_type: RollType, context: Dict[str, Any]) -> List[str]:
        """Get advantage sources from character conditions."""
        try:
            from services.condition_stat_service import condition_stat_service

            sources = []

            if roll_type == RollType.ATTACK:
                modifiers = condition_stat_service.get_attack_roll_modifier(character_id)
                if modifiers.get("advantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "advantage" in s])

            elif roll_type == RollType.SAVING_THROW:
                ability = context.get('ability', 'constitution')
                modifiers = condition_stat_service.get_saving_throw_modifier(character_id, ability)
                if modifiers.get("advantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "advantage" in s])

            elif roll_type in [RollType.ABILITY_CHECK, RollType.SKILL_CHECK]:
                ability = context.get('ability', 'strength')
                modifiers = condition_stat_service.get_ability_check_modifier(character_id, ability)
                if modifiers.get("advantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "advantage" in s])

            elif roll_type == RollType.INITIATIVE:
                modifiers = condition_stat_service.get_initiative_modifier(character_id)
                if modifiers.get("advantage"):
                    sources.extend([s for s in modifiers.get("sources", []) if "advantage" in s])

            return sources

        except ImportError:
            return []
        except Exception as e:
            print(f"[AdvantageSystem] Error getting condition advantage: {e}")
            return []

# Global instance for easy access
advantage_system = AdvantageSystem()