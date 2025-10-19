# core
# category: core
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
import re

from talekeeper.core.feature_definitions import ClassFeatures


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
            
        if self.requirements.class_name and (character.get('class_name') or '').lower() != self.requirements.class_name.lower():
            return False
            
        if self.requirements.subclass and (character.get('subclass') or '').lower() != self.requirements.subclass.lower():
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
    
    STYLES = {
        "archery": {"attack_bonus_ranged": 2},
        "defense": {"armor_class": 1},
        "dueling": {"damage_bonus_one_handed": 2},
        "great_weapon_fighting": {"reroll_damage_1_2": True},
        "protection": {"shield_ally_bonus": True},
        "two_weapon_fighting": {"offhand_damage_ability": True}
    }
    
    def __init__(self, style: str):
        super().__init__(
            name=f"Fighting Style: {style.title()}",
            description=f"Specialized combat training in {style} style",
            modifiers=self.STYLES.get(style, {}),
            requirements=FeatureRequirement(class_name="Fighter")
        )
        self.style = style



class WeaponMasteryFeature(PassiveFeature):
    """Fighter's Weapon Mastery feature."""

    SLOTS_BY_LEVEL = {1: 3, 4: 4, 10: 5, 16: 6}

    def __init__(self):
        super().__init__(
            name="Weapon Mastery",
            description="Use mastery properties of weapons.",
            modifiers={"weapon_mastery_slots": self._get_slots},
            requirements=FeatureRequirement(level=1)
        )

    def _get_slots(self, character: Dict[str, Any]) -> int:
        level = character.get('level', 1)
        slots = self.SLOTS_BY_LEVEL[1]
        for lvl, value in sorted(self.SLOTS_BY_LEVEL.items()):
            if level >= lvl:
                slots = value
        return slots


class ExtraAttack(PassiveFeature):
    """Fighter's Extra Attack progression."""

    ATTACKS_BY_LEVEL = {5: 2, 11: 3, 20: 4}

    def __init__(self, feature_name: str = "Extra Attack", min_level: int = 5):
        super().__init__(
            name=feature_name,
            description="Attack multiple times when you take the Attack action.",
            modifiers={"extra_attacks": self._get_attacks},
            requirements=FeatureRequirement(level=min_level)
        )
        self._min_level = min_level

    def _get_attacks(self, character: Dict[str, Any]) -> int:
        level = character.get('level', 1)
        attacks = 1
        for lvl, value in sorted(self.ATTACKS_BY_LEVEL.items()):
            if level >= lvl:
                attacks = value
        return attacks


class TacticalMind(TriggeredFeature):
    """Fighter's Tactical Mind feature."""

    def __init__(self):
        super().__init__(
            name="Tactical Mind",
            description="When you fail an ability check, expend Second Wind to add 1d10.",
            trigger_condition=self._can_trigger,
            effect=self._apply_effect,
            requirements=FeatureRequirement(level=2, class_name="Fighter")
        )

    def _can_trigger(self, character: Dict[str, Any], context: Dict[str, Any]) -> bool:
        return context.get('failed_ability_check', False)

    def _apply_effect(self, character: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "bonus_die": "1d10",
            "consumes_second_wind": True
        }


class TacticalShift(TriggeredFeature):
    """Fighter's Tactical Shift feature."""

    def __init__(self):
        super().__init__(
            name="Tactical Shift",
            description="After using Second Wind, move up to half your speed without provoking Opportunity Attacks.",
            trigger_condition=self._can_trigger,
            effect=self._apply_effect,
            requirements=FeatureRequirement(level=5, class_name="Fighter")
        )

    def _can_trigger(self, character: Dict[str, Any], context: Dict[str, Any]) -> bool:
        return context.get('second_wind_used', False)

    def _apply_effect(self, character: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "movement": "half_speed_no_aoo"
        }


class Indomitable(ResourceFeature):
    """Fighter's Indomitable feature."""

    def __init__(self):
        super().__init__(
            name="Indomitable",
            description="Reroll a failed saving throw with a bonus equal to your Fighter level.",
            uses_by_level={9: 1, 13: 2, 17: 3},
            recharge=ResourceRecharge.LONG_REST,
            requirements=FeatureRequirement(level=9, class_name="Fighter")
        )


class TacticalMaster(TriggeredFeature):
    """Fighter's Tactical Master feature."""

    def __init__(self):
        super().__init__(
            name="Tactical Master",
            description="Replace a weapon's mastery property with Push, Sap, or Slow for that attack.",
            trigger_condition=self._can_trigger,
            effect=self._apply_effect,
            requirements=FeatureRequirement(level=9, class_name="Fighter")
        )

    def _can_trigger(self, character: Dict[str, Any], context: Dict[str, Any]) -> bool:
        return context.get('weapon_mastery_available', False)

    def _apply_effect(self, character: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "replacement_options": ["push", "sap", "slow"]
        }


class StudiedAttacks(TriggeredFeature):
    """Fighter's Studied Attacks feature."""

    def __init__(self):
        super().__init__(
            name="Studied Attacks",
            description="After you miss an attack, gain advantage on your next attack against that creature before the end of your next turn.",
            trigger_condition=self._can_trigger,
            effect=self._apply_effect,
            requirements=FeatureRequirement(level=13, class_name="Fighter")
        )

    def _can_trigger(self, character: Dict[str, Any], context: Dict[str, Any]) -> bool:
        return context.get('missed_attack', False)

    def _apply_effect(self, character: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "grants_advantage": True,
            "target": context.get('target_id')
        }


class EpicBoon(PassiveFeature):
    """Fighter's Epic Boon feature."""

    def __init__(self):
        super().__init__(
            name="Epic Boon",
            description="Gain an Epic Boon feat or another feat of your choice.",
            modifiers={},
            requirements=FeatureRequirement(level=19, class_name="Fighter")
        )

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



class RemarkableAthleteFeature(PassiveFeature):
    """Champion's Remarkable Athlete subclass feature."""

    def __init__(self):
        super().__init__(
            name="Remarkable Athlete",
            description="Gain advantage on initiative and Strength (Athletics) checks; move without provoking after a critical hit.",
            modifiers={
                "initiative_advantage": True,
                "athletics_advantage": True,
                "critical_hit_dash": "half_speed_no_aoo"
            },
            requirements=FeatureRequirement(level=3, class_name="Fighter", subclass="champion")
        )


class HeroicWarriorFeature(PassiveFeature):
    """Champion's Heroic Warrior subclass feature."""

    def __init__(self):
        super().__init__(
            name="Heroic Warrior",
            description="Automatically gain Heroic Inspiration at the start of your turn when you lack it.",
            modifiers={
                "start_of_turn_inspiration": True
            },
            requirements=FeatureRequirement(level=10, class_name="Fighter", subclass="champion")
        )


class SurvivorFeature(PassiveFeature):
    """Champion's Survivor subclass feature."""

    def __init__(self):
        super().__init__(
            name="Survivor",
            description="Gain Defy Death and Heroic Rally benefits.",
            modifiers={
                "defy_death_advantage": True,
                "defy_death_counts_as_20": True,
                "heroic_rally_heal": "5+con_modifier"
            },
            requirements=FeatureRequirement(level=18, class_name="Fighter", subclass="champion")
        )



class FeatureManager:
    """Manages all features for a character."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.features: Dict[str, Feature] = {}
        self.feature_registry = self._build_feature_registry()
    

    def _build_feature_registry(self) -> Dict[str, Callable[[Any, str, int], Feature]]:
        """Build registry of all available features keyed by normalized names."""
        return {
            # Fighter
            "second_wind": lambda fd, cid, lvl: SecondWind(),
            "action_surge": lambda fd, cid, lvl: ActionSurge(),
            "fighting_style": self._build_fighting_style_feature,
            "weapon_mastery": lambda fd, cid, lvl: WeaponMasteryFeature(),
            "extra_attack": lambda fd, cid, lvl: ExtraAttack(feature_name=fd.name, min_level=fd.level_acquired),
            "two_extra_attacks": lambda fd, cid, lvl: ExtraAttack(feature_name=fd.name, min_level=fd.level_acquired),
            "three_extra_attacks": lambda fd, cid, lvl: ExtraAttack(feature_name=fd.name, min_level=fd.level_acquired),
            "tactical_mind": lambda fd, cid, lvl: TacticalMind(),
            "tactical_shift": lambda fd, cid, lvl: TacticalShift(),
            "indomitable": lambda fd, cid, lvl: Indomitable(),
            "tactical_master": lambda fd, cid, lvl: TacticalMaster(),
            "studied_attacks": lambda fd, cid, lvl: StudiedAttacks(),
            "epic_boon": lambda fd, cid, lvl: EpicBoon(),
            "remarkable_athlete": lambda fd, cid, lvl: RemarkableAthleteFeature(),
            "heroic_warrior": lambda fd, cid, lvl: HeroicWarriorFeature(),
            "survivor": lambda fd, cid, lvl: SurvivorFeature(),

            # Barbarian
            "rage": lambda fd, cid, lvl: Rage(),
            "unarmored_defense": lambda fd, cid, lvl: UnarmoredDefense(),
            "reckless_attack": lambda fd, cid, lvl: RecklessAttack(),

            # Rogue
            "sneak_attack": lambda fd, cid, lvl: SneakAttack(),
            "cunning_action": lambda fd, cid, lvl: CunningAction(),
            "uncanny_dodge": lambda fd, cid, lvl: UncannyDodge(),
        }

    def load_character_features(self, character_id: str) -> None:
        """Load all features for a character from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

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
        subclass = char_row['subclass_id']

        # Load class-specific features based on level
        self._load_class_features(character_id, class_name, level, subclass)

        # Load any custom features from character_features table (reserved for future use)
        cursor.execute("""
            SELECT feature_name, feature_type, description
            FROM character_features
            WHERE character_id = ?
        """, (character_id,))

        for row in cursor:
            # Placeholder for integrating bespoke features defined per character
            pass

        conn.close()


    def _load_class_features(self, character_id: str, class_name: str, level: int, subclass: Optional[str]) -> None:
        """Load features for a specific class up to a given level."""
        self.features.clear()

        feature_definitions = ClassFeatures.get_features_by_level(class_name, level, subclass)

        for feature_def in feature_definitions:
            key = self._normalize_feature_name(feature_def.name)
            builder = self.feature_registry.get(key)
            if not builder:
                continue

            feature = builder(feature_def, character_id, level)
            setattr(feature, "display_name", feature_def.name)

            if isinstance(feature, ResourceFeature):
                feature.update_uses(level)
                feature.resource.current = feature.resource.maximum

            self.features[key] = feature


    def _build_fighting_style_feature(self, feature_def: Any, character_id: str, level: int) -> Feature:
        style = self._get_fighting_style(character_id)
        return FightingStyle(style)


    @staticmethod
    def _normalize_feature_name(name: str) -> str:
        """Normalize feature names to registry keys."""
        return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


    def _get_fighting_style(self, character_id: str) -> str:
        """Get fighting style from talekeeper.database."""
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

        if 'class_name' not in character and character.get('class_id'):
            character['class_name'] = character.get('class_id')

        if not character.get('subclass'):
            subclass_value = character.get('subclass_id')
            if subclass_value:
                character['subclass'] = subclass_value

        if character.get('subclass'):
            character['subclass'] = str(character['subclass']).lower()

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