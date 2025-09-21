"""
Champion Subclass for Fighter

The archetypal Champion focuses on the development of raw physical power honed to deadly perfection.
"""

from services.enhanced_subclass_manager import (
    SubclassDefinition, SubclassFeature, FeatureType, ActionCost
)


class ChampionDefinition:
    """Champion subclass definition for Fighter."""

    @staticmethod
    def create() -> SubclassDefinition:
        """Create the Champion subclass definition."""
        return SubclassDefinition(
            class_name="fighter",
            subclass_name="champion",
            description="The archetypal Champion focuses on the development of raw physical power honed to deadly perfection.",
            flavor_text="Those who emulate this archetype combine rigorous training with physical excellence to deal devastating blows.",
            recommended_abilities=["Strength", "Constitution"],
            features=[
                # Level 3: Improved Critical
                SubclassFeature(
                    name="Improved Critical",
                    description="Your weapon attacks score a critical hit on a roll of 19 or 20 on the d20.",
                    level=3,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "critical_range_min": 19,
                        "applies_to": "weapon_attacks",
                        "stacks_with": []  # Does not stack with other crit range expansions
                    },
                    tooltip_extended="Passive effect that improves your critical hit range"
                ),

                # Level 3: Remarkable Athlete
                SubclassFeature(
                    name="Remarkable Athlete",
                    description="You add half your Proficiency Bonus (rounded up) to any Strength, Dexterity, or Constitution check you make that uses none of your skill proficiencies. In addition, the distance you can cover when you make a long jump increases by a number of feet equal to your Strength modifier.",
                    level=3,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "ability_check_bonus": "half_prof_rounded_up",
                        "applies_to": ["strength_checks", "dexterity_checks", "constitution_checks"],
                        "condition": "not_proficient",
                        "jump_distance_bonus": "strength_modifier"
                    },
                    tooltip_extended="Enhances physical ability checks and jumping"
                ),

                # Level 7: Additional Fighting Style
                SubclassFeature(
                    name="Additional Fighting Style",
                    description="You gain an additional Fighting Style option from the Fighter list. You can't take the same Fighting Style option more than once.",
                    level=7,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "grants": "fighting_style",
                        "count": 1,
                        "restriction": "unique_only"
                    },
                    tooltip_extended="Choose a second fighting style"
                ),

                # Level 10: Heroic Warrior
                SubclassFeature(
                    name="Heroic Warrior",
                    description="The thrill of battle drives you toward victory. During combat, you can gain Heroic Inspiration whenever you score a critical hit or reduce a creature to 0 hit points with an attack.",
                    level=10,
                    feature_type=FeatureType.TRIGGERED,
                    action_cost=ActionCost.NONE,
                    prerequisites={},
                    mechanics={
                        "trigger": ["critical_hit", "reduce_to_zero_hp"],
                        "effect": "gain_heroic_inspiration",
                        "limit": "once_per_turn",
                        "stacks": False
                    },
                    tooltip_extended="Gain Heroic Inspiration on crits or kills"
                ),

                # Level 15: Superior Critical
                SubclassFeature(
                    name="Superior Critical",
                    description="Your weapon attacks score a critical hit on a roll of 18-20 on the d20.",
                    level=15,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "critical_range_min": 18,
                        "applies_to": "weapon_attacks",
                        "replaces": "Improved Critical"
                    },
                    tooltip_extended="Further improves your critical hit range to 18-20"
                ),

                # Level 18: Survivor
                SubclassFeature(
                    name="Survivor",
                    description="You attain the pinnacle of resilience in battle. At the start of each of your turns, if you have no more than half of your hit points left and at least 1 hit point, you regain hit points equal to 5 + your Constitution modifier.",
                    level=18,
                    feature_type=FeatureType.TRIGGERED,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "trigger": "start_of_turn",
                        "condition": {
                            "current_hp": "less_than_half_max",
                            "minimum_hp": 1
                        },
                        "healing": "5 + constitution_modifier",
                        "automatic": True
                    },
                    tooltip_extended="Automatic healing when below half health"
                )
            ]
        )