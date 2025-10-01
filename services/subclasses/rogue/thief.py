"""
Thief Subclass for Rogue

A mix of burglar, treasure hunter, and explorer, you are the epitome of an adventurer.
In addition to improving your agility and stealth, you gain abilities useful for delving
into ruins and getting maximum benefit from the magic items you find there.
"""

from services.enhanced_subclass_manager import (
    SubclassDefinition, SubclassFeature, FeatureType, ActionCost
)


class ThiefDefinition:
    """Thief subclass definition for Rogue."""

    @staticmethod
    def create() -> SubclassDefinition:
        """Create the Thief subclass definition."""
        return SubclassDefinition(
            class_name="rogue",
            subclass_name="thief",
            description="A mix of burglar, treasure hunter, and explorer, you are the epitome of an adventurer.",
            flavor_text="Hunt for treasure as a classic adventurer, improving your agility and stealth while gaining abilities useful for delving into ruins.",
            recommended_abilities=["Dexterity", "Intelligence"],
            features=[
                SubclassFeature(
                    name="Fast Hands",
                    description="As a Bonus Action, you can do one of the following: Make a Dexterity (Sleight of Hand) check to pick a lock or disarm a trap with Thieves' Tools or to pick a pocket; OR Take the Utilize action, or take the Magic action to use a magic item that requires that action.",
                    level=3,
                    feature_type=FeatureType.ACTIVATED,
                    action_cost=ActionCost.BONUS_ACTION,
                    mechanics={
                        "options": [
                            {
                                "name": "Sleight of Hand",
                                "skill_check": "sleight_of_hand",
                                "requires_tool": "thieves_tools",
                                "actions": ["pick_lock", "disarm_trap", "pick_pocket"]
                            },
                            {
                                "name": "Use Object",
                                "actions": ["utilize", "magic_action"],
                                "applies_to": "magic_items"
                            }
                        ]
                    },
                    tooltip_extended="Use bonus action for Sleight of Hand or using objects/magic items"
                ),

                SubclassFeature(
                    name="Second-Story Work",
                    description="You've trained to get into especially hard-to-reach places. You gain a Climb Speed equal to your Speed. You can determine your jump distance using your Dexterity rather than your Strength.",
                    level=3,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "climb_speed": "base_speed",
                        "jump_ability": "dexterity",
                        "replaces": "strength_for_jumps"
                    },
                    tooltip_extended="Gain climb speed and use DEX for jump distance"
                ),

                SubclassFeature(
                    name="Supreme Sneak",
                    description="You gain the following Cunning Strike option: Stealth Attack (Cost: 1d6). If you have the Hide action's Invisible condition, this attack doesn't end that condition on you if you end the turn behind Three-Quarters Cover or Total Cover.",
                    level=9,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "adds_cunning_strike": "stealth_attack",
                        "cost": "1d6",
                        "condition_required": "invisible",
                        "condition_maintained_if": ["three_quarters_cover", "total_cover"],
                        "trigger": "end_of_turn"
                    },
                    tooltip_extended="Cunning Strike option to maintain Invisibility with cover"
                ),

                SubclassFeature(
                    name="Use Magic Device",
                    description="You've learned how to maximize use of magic items. You can attune to up to four magic items at once. Whenever you use a magic item property that expends charges, roll 1d6. On a roll of 6, you use the property without expending the charges. You can use any Spell Scroll, using Intelligence as your spellcasting ability for the spell.",
                    level=13,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "attunement_slots": 4,
                        "charge_conservation": {
                            "roll": "1d6",
                            "success_on": 6,
                            "effect": "no_charge_expended"
                        },
                        "scroll_casting": {
                            "ability": "intelligence",
                            "cantrip_level1": "automatic",
                            "higher_level": {
                                "check": "arcana",
                                "dc": "10 + spell_level",
                                "on_fail": "scroll_disintegrates"
                            }
                        }
                    },
                    tooltip_extended="Attune to 4 items, conserve charges on 6, use any scroll with INT"
                ),

                SubclassFeature(
                    name="Thief's Reflexes",
                    description="You are adept at laying ambushes and quickly escaping danger. You can take two turns during the first round of any combat. You take your first turn at your normal Initiative and your second turn at your Initiative minus 10.",
                    level=17,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "double_turn_round_1": True,
                        "first_turn_initiative": "normal",
                        "second_turn_initiative": "normal - 10",
                        "applies_to": "first_round_only"
                    },
                    tooltip_extended="Take two turns in the first round of combat"
                )
            ]
        )
