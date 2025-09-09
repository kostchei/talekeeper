"""
Feature Definitions for All Classes

This module contains the complete definitions of all class features following D&D 2024 rules.
It provides a centralized registry of features with their progression by level.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class FeatureDefinition:
    """Definition of a class feature."""
    name: str
    description: str
    level_acquired: int
    feature_type: str
    mechanics: Dict[str, Any]
    usage: Optional[str] = None  # "bonus_action", "action", "reaction", etc.
    recharge: Optional[str] = None  # "short_rest", "long_rest", etc.
    scaling: Optional[Dict[int, Any]] = None  # How feature scales with level


class ClassFeatures:
    """Registry of all class features by class and level."""
    
    FIGHTER_FEATURES = {
        1: [
            FeatureDefinition(
                name="Fighting Style",
                description="Choose a specialized form of combat training",
                level_acquired=1,
                feature_type="passive",
                mechanics={"choices": ["archery", "defense", "dueling", "great_weapon_fighting", "protection", "two_weapon_fighting"]}
            ),
            FeatureDefinition(
                name="Second Wind", 
                description="Regain hit points equal to 1d10 + Fighter level",
                level_acquired=1,
                feature_type="resource",
                usage="bonus_action",
                recharge="short_rest",
                mechanics={"healing": "1d10+level"},
                scaling={1: {"uses": 2}, 4: {"uses": 3}, 10: {"uses": 4}}
            ),
            FeatureDefinition(
                name="Weapon Mastery",
                description="Use mastery properties of weapons",
                level_acquired=1,
                feature_type="progression",
                mechanics={"weapon_choices": 3},
                scaling={1: 3, 4: 4, 10: 5, 16: 6}
            )
        ],
        2: [
            FeatureDefinition(
                name="Action Surge",
                description="Take one additional action on your turn",
                level_acquired=2,
                feature_type="resource",
                usage="free",
                recharge="short_rest",
                mechanics={"extra_actions": 1},
                scaling={2: {"uses": 1}, 17: {"uses": 2}}
            ),
            FeatureDefinition(
                name="Tactical Mind",
                description="Add 1d10 to failed ability checks using Second Wind",
                level_acquired=2,
                feature_type="triggered",
                mechanics={"trigger": "failed_ability_check", "bonus": "1d10"}
            )
        ],
        5: [
            FeatureDefinition(
                name="Extra Attack",
                description="Attack twice when taking the Attack action",
                level_acquired=5,
                feature_type="progression",
                mechanics={"attacks": 2},
                scaling={5: 2, 11: 3, 20: 4}
            ),
            FeatureDefinition(
                name="Tactical Shift",
                description="Move half speed without opportunity attacks after Second Wind",
                level_acquired=5,
                feature_type="triggered",
                mechanics={"trigger": "second_wind", "movement": "half_speed_no_aoo"}
            )
        ],
        9: [
            FeatureDefinition(
                name="Indomitable",
                description="Reroll a failed saving throw",
                level_acquired=9,
                feature_type="resource",
                usage="reaction",
                recharge="long_rest",
                mechanics={"reroll_save": True, "bonus": "fighter_level"},
                scaling={9: {"uses": 1}, 13: {"uses": 2}, 17: {"uses": 3}}
            ),
            FeatureDefinition(
                name="Tactical Master",
                description="Replace weapon mastery property with Push, Sap, or Slow",
                level_acquired=9,
                feature_type="modal",
                mechanics={"replace_mastery": ["push", "sap", "slow"]}
            )
        ],
        13: [
            FeatureDefinition(
                name="Studied Attacks",
                description="Advantage on attack rolls using Strength or Dexterity",
                level_acquired=13,
                feature_type="triggered",
                mechanics={"trigger": "study_target", "effect": "advantage_on_attacks"}
            )
        ]
    }
    
    BARBARIAN_FEATURES = {
        1: [
            FeatureDefinition(
                name="Rage",
                description="Enter a battle rage for damage resistance and bonuses",
                level_acquired=1,
                feature_type="resource",
                usage="bonus_action",
                recharge="long_rest",
                mechanics={
                    "damage_resistance": ["bludgeoning", "piercing", "slashing"],
                    "advantage": ["strength_checks", "strength_saves"],
                    "duration": "10_minutes"
                },
                scaling={
                    1: {"uses": 2, "damage_bonus": 2},
                    3: {"uses": 3, "damage_bonus": 2},
                    6: {"uses": 4, "damage_bonus": 2},
                    9: {"uses": 4, "damage_bonus": 3},
                    12: {"uses": 5, "damage_bonus": 3},
                    16: {"uses": 5, "damage_bonus": 4},
                    17: {"uses": 6, "damage_bonus": 4}
                }
            ),
            FeatureDefinition(
                name="Unarmored Defense",
                description="AC equals 10 + Dexterity modifier + Constitution modifier",
                level_acquired=1,
                feature_type="passive",
                mechanics={"ac_calculation": "10+dex+con", "requires": "no_armor"}
            ),
            FeatureDefinition(
                name="Weapon Mastery",
                description="Use mastery properties of melee weapons",
                level_acquired=1,
                feature_type="progression",
                mechanics={"weapon_choices": 2},
                scaling={1: 2, 4: 3, 10: 4}
            )
        ],
        2: [
            FeatureDefinition(
                name="Danger Sense",
                description="Advantage on Dexterity saving throws",
                level_acquired=2,
                feature_type="passive",
                mechanics={"advantage": "dex_saves", "condition": "not_incapacitated"}
            ),
            FeatureDefinition(
                name="Reckless Attack",
                description="Gain advantage on attacks, enemies gain advantage against you",
                level_acquired=2,
                feature_type="modal",
                usage="free",
                mechanics={
                    "player_advantage": "strength_attacks",
                    "enemy_advantage": "all_attacks",
                    "duration": "until_next_turn"
                }
            )
        ],
        3: [
            FeatureDefinition(
                name="Primal Knowledge",
                description="Gain skill proficiency and can use Strength for some checks while raging",
                level_acquired=3,
                feature_type="passive",
                mechanics={
                    "bonus_skill": 1,
                    "rage_skills_use_str": ["acrobatics", "intimidation", "perception", "stealth", "survival"]
                }
            )
        ],
        5: [
            FeatureDefinition(
                name="Extra Attack",
                description="Attack twice when taking the Attack action",
                level_acquired=5,
                feature_type="progression",
                mechanics={"attacks": 2}
            ),
            FeatureDefinition(
                name="Fast Movement",
                description="Speed increases by 10 feet",
                level_acquired=5,
                feature_type="passive",
                mechanics={"speed_bonus": 10, "requires": "no_heavy_armor"}
            )
        ],
        7: [
            FeatureDefinition(
                name="Feral Instinct",
                description="Advantage on initiative rolls",
                level_acquired=7,
                feature_type="passive",
                mechanics={"advantage": "initiative"}
            ),
            FeatureDefinition(
                name="Instinctive Pounce",
                description="Move half speed when entering rage",
                level_acquired=7,
                feature_type="triggered",
                mechanics={"trigger": "enter_rage", "movement": "half_speed"}
            )
        ],
        9: [
            FeatureDefinition(
                name="Brutal Strike",
                description="Forgo advantage to deal extra damage and apply effects",
                level_acquired=9,
                feature_type="modal",
                mechanics={
                    "extra_damage": "1d10",
                    "effects": ["hamstring", "push", "stagger"]
                },
                scaling={
                    9: {"damage": "1d10"},
                    13: {"damage": "2d10"},
                    17: {"damage": "3d10"}
                }
            )
        ],
        11: [
            FeatureDefinition(
                name="Relentless Rage",
                description="Keep fighting at 0 hit points while raging",
                level_acquired=11,
                feature_type="triggered",
                mechanics={"trigger": "drop_to_0_hp", "dc": 10, "dc_increase": 5}
            )
        ],
        15: [
            FeatureDefinition(
                name="Persistent Rage",
                description="Rage doesn't end early unless you choose or fall unconscious",
                level_acquired=15,
                feature_type="passive",
                mechanics={"rage_persistent": True}
            )
        ],
        18: [
            FeatureDefinition(
                name="Indomitable Might",
                description="Strength checks minimum equals Strength score",
                level_acquired=18,
                feature_type="passive",
                mechanics={"str_check_minimum": "str_score"}
            )
        ],
        20: [
            FeatureDefinition(
                name="Primal Champion",
                description="+4 to Strength and Constitution (max 24)",
                level_acquired=20,
                feature_type="passive",
                mechanics={"str_bonus": 4, "con_bonus": 4, "max_score": 24}
            )
        ]
    }
    
    ROGUE_FEATURES = {
        1: [
            FeatureDefinition(
                name="Expertise",
                description="Double proficiency bonus on chosen skills",
                level_acquired=1,
                feature_type="passive",
                mechanics={"expertise_skills": 2},
                scaling={1: 2, 6: 4}
            ),
            FeatureDefinition(
                name="Sneak Attack",
                description="Deal extra damage with advantage or ally nearby",
                level_acquired=1,
                feature_type="triggered",
                mechanics={
                    "trigger": ["has_advantage", "ally_within_5ft"],
                    "requirements": ["finesse_or_ranged_weapon"],
                    "once_per_turn": True
                },
                scaling={
                    1: "1d6", 3: "2d6", 5: "3d6", 7: "4d6", 9: "5d6",
                    11: "6d6", 13: "7d6", 15: "8d6", 17: "9d6", 19: "10d6"
                }
            ),
            FeatureDefinition(
                name="Thieves' Cant",
                description="Secret language of rogues",
                level_acquired=1,
                feature_type="passive",
                mechanics={"language": "thieves_cant"}
            ),
            FeatureDefinition(
                name="Weapon Mastery",
                description="Use mastery properties of weapons",
                level_acquired=1,
                feature_type="progression",
                mechanics={"weapon_choices": 2},
                scaling={1: 2}
            )
        ],
        2: [
            FeatureDefinition(
                name="Cunning Action",
                description="Dash, Disengage, or Hide as bonus action",
                level_acquired=2,
                feature_type="bonus_action",
                mechanics={"bonus_actions": ["dash", "disengage", "hide"]}
            )
        ],
        3: [
            FeatureDefinition(
                name="Steady Aim",
                description="Gain advantage on next attack, speed becomes 0",
                level_acquired=3,
                feature_type="bonus_action",
                mechanics={"effect": "advantage_next_attack", "cost": "speed_0"}
            )
        ],
        5: [
            FeatureDefinition(
                name="Cunning Strike",
                description="Add effects to Sneak Attack by reducing damage",
                level_acquired=5,
                feature_type="modal",
                mechanics={
                    "options": {
                        "poison": {"cost": "1d6", "save": "con", "effect": "poisoned_1min"},
                        "trip": {"cost": "1d6", "save": "dex", "effect": "prone"},
                        "withdraw": {"cost": "1d6", "effect": "move_half_no_aoo"}
                    }
                },
                scaling={
                    11: {"uses_per_attack": 2}
                }
            ),
            FeatureDefinition(
                name="Uncanny Dodge",
                description="Halve damage from one attack as reaction",
                level_acquired=5,
                feature_type="reaction",
                mechanics={"trigger": "hit_by_attack", "effect": "half_damage"}
            )
        ],
        7: [
            FeatureDefinition(
                name="Evasion",
                description="No damage on successful Dex saves, half on failure",
                level_acquired=7,
                feature_type="passive",
                mechanics={"dex_save_improvement": True}
            ),
            FeatureDefinition(
                name="Reliable Talent",
                description="Treat rolls of 9 or lower as 10 on proficient checks",
                level_acquired=7,
                feature_type="passive",
                mechanics={"minimum_roll": 10, "applies_to": "proficient_checks"}
            )
        ],
        14: [
            FeatureDefinition(
                name="Devious Strikes",
                description="Additional Cunning Strike options",
                level_acquired=14,
                feature_type="modal",
                mechanics={
                    "new_options": {
                        "daze": {"cost": "2d6", "save": "con", "effect": "limited_action"},
                        "knock_out": {"cost": "6d6", "save": "con", "effect": "unconscious_1min"},
                        "obscure": {"cost": "3d6", "save": "dex", "effect": "blinded"}
                    }
                }
            )
        ],
        15: [
            FeatureDefinition(
                name="Slippery Mind",
                description="Proficiency in Wisdom and Charisma saves",
                level_acquired=15,
                feature_type="passive",
                mechanics={"save_proficiencies": ["wisdom", "charisma"]}
            )
        ],
        18: [
            FeatureDefinition(
                name="Elusive",
                description="No attack has advantage against you unless incapacitated",
                level_acquired=18,
                feature_type="passive",
                mechanics={"negate_advantage": True, "unless": "incapacitated"}
            )
        ],
        20: [
            FeatureDefinition(
                name="Stroke of Luck",
                description="Turn a failed d20 test into a 20",
                level_acquired=20,
                feature_type="resource",
                usage="free",
                recharge="short_rest",
                mechanics={"auto_success": 20}
            )
        ]
    }
    
    # Subclass features
    CHAMPION_FEATURES = {
        3: [
            FeatureDefinition(
                name="Improved Critical",
                description="Critical hits on 19-20",
                level_acquired=3,
                feature_type="passive",
                mechanics={"crit_range": 19}
            ),
            FeatureDefinition(
                name="Remarkable Athlete",
                description="Add half proficiency to physical checks and increase jump distance",
                level_acquired=3,
                feature_type="passive",
                mechanics={
                    "half_prof_to": ["str_checks", "dex_checks", "con_checks"],
                    "jump_bonus": "str_modifier_feet"
                }
            )
        ],
        7: [
            FeatureDefinition(
                name="Additional Fighting Style",
                description="Learn another Fighting Style",
                level_acquired=7,
                feature_type="passive",
                mechanics={"extra_fighting_style": 1}
            )
        ],
        10: [
            FeatureDefinition(
                name="Heroic Warrior",
                description="Choose Defensive or Offensive focus",
                level_acquired=10,
                feature_type="modal",
                mechanics={
                    "defensive": {"ac_bonus": 1, "save_bonus": 1},
                    "offensive": {"attack_bonus": 1, "damage_bonus": 1}
                }
            )
        ],
        15: [
            FeatureDefinition(
                name="Superior Critical",
                description="Critical hits on 18-20",
                level_acquired=15,
                feature_type="passive",
                mechanics={"crit_range": 18}
            )
        ],
        18: [
            FeatureDefinition(
                name="Survivor",
                description="Regain hit points at start of turn if below half",
                level_acquired=18,
                feature_type="triggered",
                mechanics={
                    "trigger": "start_of_turn",
                    "condition": "hp_below_half",
                    "healing": "5+con_modifier"
                }
            )
        ]
    }
    
    @classmethod
    def get_features_by_level(cls, class_name: str, level: int, subclass: Optional[str] = None) -> List[FeatureDefinition]:
        """Get all features for a character of given class and level."""
        features = []
        
        # Get base class features
        class_features = getattr(cls, f"{class_name.upper()}_FEATURES", {})
        for feature_level, feature_list in class_features.items():
            if level >= feature_level:
                features.extend(feature_list)
        
        # Get subclass features if applicable
        if subclass:
            subclass_features = getattr(cls, f"{subclass.upper()}_FEATURES", {})
            for feature_level, feature_list in subclass_features.items():
                if level >= feature_level:
                    features.extend(feature_list)
        
        return features
    
    @classmethod
    def get_feature_at_level(cls, class_name: str, level: int, subclass: Optional[str] = None) -> List[FeatureDefinition]:
        """Get only the features gained at a specific level."""
        features = []
        
        # Check base class features
        class_features = getattr(cls, f"{class_name.upper()}_FEATURES", {})
        if level in class_features:
            features.extend(class_features[level])
        
        # Check subclass features
        if subclass:
            subclass_features = getattr(cls, f"{subclass.upper()}_FEATURES", {})
            if level in subclass_features:
                features.extend(subclass_features[level])
        
        return features