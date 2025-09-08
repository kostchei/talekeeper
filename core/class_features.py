"""
Unified Class Feature System for TaleKeeper

This module provides a scalable, polymorphic system for implementing D&D 2024 class features.
It uses composition and strategy patterns to handle diverse feature types while maintaining
compatibility with the existing database structure.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from abc import ABC, abstractmethod
import json
import sqlite3


class FeatureType(Enum):
    """Categories of class features for systematic handling."""
    RESOURCE = "resource"          # Features with limited uses (Second Wind, Rage)
    PASSIVE = "passive"            # Always-on features (Fighting Style, Unarmored Defense)
    TRIGGERED = "triggered"        # Features that activate on conditions (Sneak Attack)
    MODAL = "modal"               # Features that change character state (Rage mode)
    PROGRESSION = "progression"    # Features that scale with level (Extra Attack)
    REACTION = "reaction"         # Features using reactions (Uncanny Dodge)
    ACTION = "action"             # Features using actions (Action Surge)
    BONUS_ACTION = "bonus_action" # Features using bonus actions (Cunning Action)


class ResourceRecharge(Enum):
    """When a resource-based feature recharges."""
    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    TURN = "turn"
    ROUND = "round"
    DAWN = "dawn"
    NEVER = "never"  # One-time use features


@dataclass
class FeatureResource:
    """Tracks usage of resource-based features."""
    current: int = 0
    maximum: int = 0
    recharge: ResourceRecharge = ResourceRecharge.LONG_REST
    
    def use(self, amount: int = 1) -> bool:
        """Attempt to use the resource."""
        if self.current >= amount:
            self.current -= amount
            return True
        return False
    
    def restore(self, amount: Optional[int] = None):
        """Restore resource uses."""
        if amount is None:
            self.current = self.maximum
        else:
            self.current = min(self.current + amount, self.maximum)


@dataclass
class FeatureRequirement:
    """Requirements for a feature to be available/usable."""
    level: int = 1
    class_name: Optional[str] = None
    subclass: Optional[str] = None
    ability_score: Optional[Dict[str, int]] = None  # e.g., {"strength": 13}
    feat: Optional[str] = None
    custom_check: Optional[Callable] = None


class Feature(ABC):
    """Abstract base class for all features."""
    
    def __init__(
        self,
        name: str,
        description: str,
        feature_type: FeatureType,
        requirements: Optional[FeatureRequirement] = None
    ):
        self.name = name
        self.description = description
        self.feature_type = feature_type
        self.requirements = requirements or FeatureRequirement()
        self.active = False
        
    @abstractmethod
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Apply the feature's effects to the character."""
        pass
    
    @abstractmethod
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool:
        """Check if the feature can be used."""
        pass
    
    def meets_requirements(self, character: Dict[str, Any]) -> bool:
        """Check if character meets feature requirements."""
        if self.requirements.level > character.get('level', 1):
            return False
            
        if self.requirements.class_name and character.get('class_name') != self.requirements.class_name:
            return False
            
        if self.requirements.subclass and character.get('subclass') != self.requirements.subclass:
            return False
            
        if self.requirements.ability_score:
            for ability, min_score in self.requirements.ability_score.items():
                if character.get(ability, 10) < min_score:
                    return False
                    
        if self.requirements.custom_check and not self.requirements.custom_check(character):
            return False
            
        return True


class ResourceFeature(Feature):
    """Features with limited uses per rest."""
    
    def __init__(
        self,
        name: str,
        description: str,
        uses_by_level: Dict[int, int],
        recharge: ResourceRecharge = ResourceRecharge.LONG_REST,
        **kwargs
    ):
        super().__init__(name, description, FeatureType.RESOURCE, **kwargs)
        self.uses_by_level = uses_by_level
        self.resource = FeatureResource(recharge=recharge)
    
    def update_uses(self, level: int):
        """Update maximum uses based on level."""
        for lvl in sorted(self.uses_by_level.keys(), reverse=True):
            if level >= lvl:
                self.resource.maximum = self.uses_by_level[lvl]
                if self.resource.current > self.resource.maximum:
                    self.resource.current = self.resource.maximum
                break
    
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool:
        """Check if the feature can be used."""
        return self.meets_requirements(character) and self.resource.current > 0
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use the feature."""
        if not self.can_use(character, context):
            return {"success": False, "reason": "Feature cannot be used"}
        
        self.resource.use()
        return {"success": True, "uses_remaining": self.resource.current}


class PassiveFeature(Feature):
    """Always-active features that modify character stats."""
    
    def __init__(
        self,
        name: str,
        description: str,
        modifiers: Dict[str, Any],
        **kwargs
    ):
        super().__init__(name, description, FeatureType.PASSIVE, **kwargs)
        self.modifiers = modifiers
        self.active = True  # Passive features are always active when requirements are met
    
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool:
        """Passive features are always usable if requirements are met."""
        return self.meets_requirements(character)
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Apply passive modifiers to character."""
        if not self.can_use(character, context):
            return {"success": False, "reason": "Requirements not met"}
        
        result = {"success": True, "modifications": {}}
        
        for stat, modifier in self.modifiers.items():
            if callable(modifier):
                result["modifications"][stat] = modifier(character)
            else:
                result["modifications"][stat] = modifier
        
        return result


class TriggeredFeature(Feature):
    """Features that activate on specific conditions."""
    
    def __init__(
        self,
        name: str,
        description: str,
        trigger_condition: Callable[[Dict, Dict], bool],
        effect: Callable[[Dict, Dict], Dict],
        **kwargs
    ):
        super().__init__(name, description, FeatureType.TRIGGERED, **kwargs)
        self.trigger_condition = trigger_condition
        self.effect = effect
    
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool:
        """Check if trigger condition is met."""
        if not self.meets_requirements(character):
            return False
        return self.trigger_condition(character, context or {})
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Apply the triggered effect."""
        if not self.can_use(character, context):
            return {"success": False, "reason": "Trigger condition not met"}
        
        return self.effect(character, context or {})


# Fighter Features
class SecondWind(ResourceFeature):
    """Fighter's Second Wind feature."""
    
    def __init__(self):
        super().__init__(
            name="Second Wind",
            description="Regain hit points equal to 1d10 + Fighter level",
            uses_by_level={1: 2, 4: 3, 10: 4},
            recharge=ResourceRecharge.SHORT_REST,
            requirements=FeatureRequirement(class_name="Fighter")
        )
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use Second Wind to heal."""
        result = super().apply(character, context)
        if result["success"]:
            import random
            healing = random.randint(1, 10) + character.get('level', 1)
            result["healing"] = healing
            result["action_type"] = "bonus_action"
        return result


class ActionSurge(ResourceFeature):
    """Fighter's Action Surge feature."""
    
    def __init__(self):
        super().__init__(
            name="Action Surge",
            description="Take one additional action on your turn",
            uses_by_level={2: 1, 17: 2},
            recharge=ResourceRecharge.SHORT_REST,
            requirements=FeatureRequirement(level=2, class_name="Fighter")
        )
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use Action Surge."""
        result = super().apply(character, context)
        if result["success"]:
            result["extra_action"] = True
            result["action_type"] = "free"  # Doesn't cost an action to activate
        return result


class FightingStyle(PassiveFeature):
    """Fighter's Fighting Style feature."""

    def __init__(self, style: str):
        # The modifiers will be calculated dynamically in the apply method,
        # so we pass an empty dict to the super constructor.
        super().__init__(
            name=f"Fighting Style: {style.title()}",
            description=f"Specialized combat training in {style} style",
            modifiers={},
            requirements=FeatureRequirement(class_name="Fighter")
        )
        self.style = style.lower().replace(" ", "_")

    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Apply the fighting style's effects based on the character and context.
        The context dictionary can contain information about the action being taken,
        such as the weapon used, if it's an attack, etc.
        """
        if not self.can_use(character, context):
            return {"success": False, "reason": "Requirements not met"}

        context = context or {}
        modifications = {}

        if self.style == "archery":
            if context.get('is_ranged_attack', False):
                modifications['attack_bonus'] = 2

        elif self.style == "defense":
            # This requires knowing if the character is wearing armor.
            if context.get('is_wearing_armor', False):
                modifications['ac_bonus'] = 1

        elif self.style == "dueling":
            # Requires a melee weapon in one hand and no other weapons.
            is_melee = context.get('is_melee_attack', False)
            is_one_handed = context.get('is_one_handed', False)
            off_hand_empty = context.get('off_hand_empty', False)
            if is_melee and is_one_handed and off_hand_empty:
                modifications['damage_bonus'] = 2

        elif self.style == "great_weapon_fighting":
            # This affects dice rolls, not a flat bonus.
            # We add a flag that the combat calculation logic can use.
            is_melee = context.get('is_melee_attack', False)
            is_two_handed_weapon = context.get('is_two_handed_weapon', False)
            if is_melee and is_two_handed_weapon:
                modifications['reroll_damage_1_2'] = True

        elif self.style == "two_weapon_fighting":
            # Applies to the off-hand attack.
            if context.get('is_off_hand_attack', False):
                modifications['add_ability_mod_to_offhand_damage'] = True

        # Protection is a reaction and is handled separately.

        return {"success": True, "modifications": modifications}


# Barbarian Features  
class Rage(ResourceFeature):
    """Barbarian's Rage feature."""
    
    def __init__(self):
        super().__init__(
            name="Rage",
            description="Enter a battle rage for combat bonuses",
            uses_by_level={1: 2, 3: 3, 6: 4, 12: 5, 17: 6},
            recharge=ResourceRecharge.LONG_REST,
            requirements=FeatureRequirement(class_name="Barbarian")
        )
        self.rage_active = False
        self.rage_turns = 0
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Enter or maintain rage."""
        if not self.rage_active:
            # Entering rage
            result = super().apply(character, context)
            if result["success"]:
                self.rage_active = True
                self.rage_turns = 10  # 10 turns = 1 minute
                
                # Calculate rage damage bonus by level
                level = character.get('level', 1)
                rage_bonus = 2 if level < 9 else (3 if level < 16 else 4)
                
                result.update({
                    "rage_active": True,
                    "damage_resistance": ["bludgeoning", "piercing", "slashing"],
                    "rage_damage_bonus": rage_bonus,
                    "advantage_on": ["strength_checks", "strength_saves"],
                    "action_type": "bonus_action"
                })
        else:
            # Maintaining rage
            result = {"success": True, "rage_maintained": True, "action_type": "bonus_action"}
        
        return result
    
    def end_rage(self):
        """End the rage."""
        self.rage_active = False
        self.rage_turns = 0


class UnarmoredDefense(PassiveFeature):
    """Barbarian's Unarmored Defense feature."""
    
    def __init__(self):
        def calculate_ac(character: Dict) -> int:
            if character.get('armor_worn'):
                return 0  # No bonus if wearing armor
            base_ac = 10 + character.get('dexterity_modifier', 0) + character.get('constitution_modifier', 0)
            return base_ac
        
        super().__init__(
            name="Unarmored Defense",
            description="AC = 10 + Dex modifier + Con modifier (no armor)",
            modifiers={"armor_class_unarmored": calculate_ac},
            requirements=FeatureRequirement(class_name="Barbarian")
        )


class RecklessAttack(Feature):
    """Barbarian's Reckless Attack feature."""
    
    def __init__(self):
        super().__init__(
            name="Reckless Attack",
            description="Gain advantage on attacks, enemies gain advantage against you",
            feature_type=FeatureType.MODAL,
            requirements=FeatureRequirement(level=2, class_name="Barbarian")
        )
        self.active_until_next_turn = False
    
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool:
        """Can use on first attack of turn."""
        if not self.meets_requirements(character):
            return False
        return context and context.get('is_first_attack', False)
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Activate Reckless Attack."""
        if not self.can_use(character, context):
            return {"success": False, "reason": "Not first attack of turn"}
        
        self.active_until_next_turn = True
        return {
            "success": True,
            "advantage_on_attacks": True,
            "enemies_have_advantage": True,
            "duration": "until_next_turn"
        }


# Rogue Features
class SneakAttack(TriggeredFeature):
    """Rogue's Sneak Attack feature."""
    
    def __init__(self):
        def check_trigger(character: Dict, context: Dict) -> bool:
            if not context.get('is_attack'):
                return False
            
            weapon = context.get('weapon', {})
            if not (weapon.get('finesse') or weapon.get('ranged')):
                return False
            
            # Check for advantage or ally nearby
            has_advantage = context.get('has_advantage', False)
            ally_nearby = context.get('ally_within_5ft', False) and not context.get('has_disadvantage', False)
            
            return has_advantage or ally_nearby
        
        def apply_sneak_attack(character: Dict, context: Dict) -> Dict:
            level = character.get('level', 1)
            sneak_dice = (level + 1) // 2  # 1d6 at level 1, +1d6 every 2 levels
            
            return {
                "success": True,
                "extra_damage_dice": f"{sneak_dice}d6",
                "damage_type": context.get('weapon', {}).get('damage_type', 'piercing'),
                "once_per_turn": True
            }
        
        super().__init__(
            name="Sneak Attack",
            description="Deal extra damage when you have advantage or an ally is nearby",
            trigger_condition=check_trigger,
            effect=apply_sneak_attack,
            requirements=FeatureRequirement(class_name="Rogue")
        )


class CunningAction(Feature):
    """Rogue's Cunning Action feature."""
    
    def __init__(self):
        super().__init__(
            name="Cunning Action",
            description="Dash, Disengage, or Hide as a bonus action",
            feature_type=FeatureType.BONUS_ACTION,
            requirements=FeatureRequirement(level=2, class_name="Rogue")
        )
    
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool:
        """Can use if bonus action is available."""
        if not self.meets_requirements(character):
            return False
        return context and context.get('bonus_action_available', False)
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use Cunning Action."""
        if not self.can_use(character, context):
            return {"success": False, "reason": "Bonus action not available"}
        
        action = context.get('cunning_action_choice', 'dash')
        return {
            "success": True,
            "action_type": "bonus_action",
            "effect": action,
            "options": ["dash", "disengage", "hide"]
        }


class UncannyDodge(Feature):
    """Rogue's Uncanny Dodge feature."""
    
    def __init__(self):
        super().__init__(
            name="Uncanny Dodge",
            description="Halve damage from one attack as a reaction",
            feature_type=FeatureType.REACTION,
            requirements=FeatureRequirement(level=5, class_name="Rogue")
        )
        self.used_this_turn = False
    
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool:
        """Can use once per turn when hit."""
        if not self.meets_requirements(character):
            return False
        if self.used_this_turn:
            return False
        return context and context.get('is_hit_by_attack', False)
    
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use Uncanny Dodge."""
        if not self.can_use(character, context):
            return {"success": False, "reason": "Cannot use Uncanny Dodge"}
        
        self.used_this_turn = True
        damage = context.get('damage', 0)
        reduced_damage = damage // 2
        
        return {
            "success": True,
            "action_type": "reaction",
            "damage_reduced": damage - reduced_damage,
            "final_damage": reduced_damage
        }


class FeatureManager:
    """Manages all features for a character."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.features: Dict[str, Feature] = {}
        self.feature_registry = self._build_feature_registry()
    
    def _build_feature_registry(self) -> Dict[str, Callable]:
        """Build registry of all available features."""
        return {
            # Fighter
            "second_wind": SecondWind,
            "action_surge": ActionSurge,
            "fighting_style": FightingStyle,
            
            # Barbarian
            "rage": Rage,
            "unarmored_defense": UnarmoredDefense,
            "reckless_attack": RecklessAttack,
            
            # Rogue
            "sneak_attack": SneakAttack,
            "cunning_action": CunningAction,
            "uncanny_dodge": UncannyDodge,
        }
    
    def load_character_features(self, character_id: str) -> None:
        """Load all features for a character from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get character class and level
        cursor.execute("""
            SELECT class_id, level, subclass_id
            FROM characters
            WHERE id = ?
        """, (character_id,))
        
        char_row = cursor.fetchone()
        if not char_row:
            conn.close()
            return
        
        class_name = char_row['class_id']
        level = char_row['level']
        
        # Load class-specific features based on level
        self._load_class_features(character_id, class_name.title(), level)
        
        # Load any custom features from character_features table
        cursor.execute("""
            SELECT feature_name, feature_type, description
            FROM character_features
            WHERE character_id = ?
        """, (character_id,))
        
        for row in cursor:
            # Add custom features if needed
            pass
        
        conn.close()
    
    def _load_class_features(self, character_id: str, class_name: str, level: int) -> None:
        """Load features for a specific class up to a given level."""
        class_features = {
            "Fighter": [
                (1, ["second_wind", "fighting_style"]),
                (2, ["action_surge"]),
            ],
            "Barbarian": [
                (1, ["rage", "unarmored_defense"]),
                (2, ["reckless_attack"]),
            ],
            "Rogue": [
                (1, ["sneak_attack"]),
                (2, ["cunning_action"]),
                (5, ["uncanny_dodge"]),
            ]
        }
        
        if class_name not in class_features:
            return
        
        for req_level, feature_names in class_features[class_name]:
            if level >= req_level:
                for feature_name in feature_names:
                    if feature_name in self.feature_registry:
                        if feature_name == "fighting_style":
                            # Special handling for fighting style
                            # Get the actual style from database or default
                            style = self._get_fighting_style(character_id)
                            feature = FightingStyle(style)
                        else:
                            feature = self.feature_registry[feature_name]()
                        
                        # Update resource-based features with level-appropriate uses
                        if isinstance(feature, ResourceFeature):
                            feature.update_uses(level)
                        
                        self.features[feature_name] = feature
    
    def _get_fighting_style(self, character_id: str) -> str:
        """Get fighting style from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fighting_style
            FROM fighter_features
            WHERE character_id = ?
        """, (character_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row and row[0] else "defense"
    
    def get_available_features(self, character: Dict[str, Any], context: Optional[Dict] = None) -> List[str]:
        """Get list of features currently available to use."""
        available = []
        for name, feature in self.features.items():
            if feature.can_use(character, context):
                available.append(name)
        return available
    
    def use_feature(self, feature_name: str, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use a specific feature."""
        if feature_name not in self.features:
            return {"success": False, "reason": "Feature not found"}
        
        feature = self.features[feature_name]
        return feature.apply(character, context)
    
    def apply_passive_features(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all passive features to character stats."""
        modifications = {}
        
        for name, feature in self.features.items():
            if isinstance(feature, PassiveFeature) and feature.can_use(character):
                result = feature.apply(character)
                if result["success"]:
                    modifications.update(result.get("modifications", {}))
        
        return modifications
    
    def process_rest(self, rest_type: str) -> None:
        """Process rest and restore appropriate resources."""
        recharge_type = ResourceRecharge.SHORT_REST if rest_type == "short" else ResourceRecharge.LONG_REST
        
        for feature in self.features.values():
            if isinstance(feature, ResourceFeature):
                if feature.resource.recharge == recharge_type or (
                    rest_type == "long" and feature.resource.recharge == ResourceRecharge.SHORT_REST
                ):
                    feature.resource.restore()
            
            # Reset per-turn trackers
            if hasattr(feature, 'used_this_turn'):
                feature.used_this_turn = False
            if hasattr(feature, 'active_until_next_turn'):
                feature.active_until_next_turn = False


# Export the main classes
__all__ = [
    'Feature', 'ResourceFeature', 'PassiveFeature', 'TriggeredFeature',
    'FeatureManager', 'FeatureType', 'ResourceRecharge', 'FeatureRequirement'
]