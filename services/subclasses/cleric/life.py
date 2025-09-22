"""
Life Domain Cleric Subclass

Implementation using the scalable subclass architecture.

Phase 2.1: Life Domain Subclass Implementation
Implementation Plan Reference: Phase 2 > Phase 2.1 > Step 2.1.2
"""

from services.enhanced_subclass_manager import (
    SubclassDefinition, SubclassFeature, FeatureType, ActionCost
)


class LifeDefinition:
    """Life Domain subclass definition for Cleric."""

    @staticmethod
    def create() -> SubclassDefinition:
        """Create the Life Domain subclass definition."""
        return SubclassDefinition(
            class_name="cleric",
            subclass_name="life",
            description="Gods of life promote vitality and health through healing the sick and wounded, caring for those in need, and driving away the forces of death and undeath.",
            flavor_text="Your spells and Channel Divinity options are focused on healing and protecting life.",
            recommended_abilities=["Wisdom", "Constitution"],
            features=[
                # Level 1: Bonus Proficiency
                SubclassFeature(
                    name="Bonus Proficiency",
                    description="You gain proficiency with heavy armor.",
                    level=1,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "proficiency_type": "armor",
                        "proficiencies_granted": ["heavy_armor"]
                    },
                    tooltip_extended="Life Domain clerics can wear heavy armor without penalty"
                ),

                # Level 1: Disciple of Life
                SubclassFeature(
                    name="Disciple of Life",
                    description="When you cast a healing spell of 1st level or higher, the creature regains additional hit points equal to 2 + the spell's level.",
                    level=1,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "healing_bonus_formula": "2 + spell_level",
                        "applies_to": "healing_spells_1st_or_higher",
                        "trigger": "spell_cast"
                    },
                    tooltip_extended="Automatically applies extra healing when you cast healing spells"
                ),

                # Level 2: Channel Divinity - Preserve Life
                SubclassFeature(
                    name="Preserve Life",
                    description="As an action, you present your holy symbol and evoke healing energy that can restore a number of hit points equal to five times your cleric level. Choose any creatures within 30 feet of you, and divide those hit points among them. This feature can restore a creature to no more than half of its hit point maximum.",
                    level=2,
                    feature_type=FeatureType.ACTIVATED,
                    action_cost=ActionCost.ACTION,
                    uses_per_rest=1,
                    rest_type="short",
                    resource_name="Channel Divinity",
                    mechanics={
                        "healing_pool_formula": "5 * cleric_level",
                        "range": 30,
                        "area_type": "choice_within_range",
                        "healing_limit": "half_max_hp",
                        "distribution": "player_choice"
                    },
                    tooltip_extended="Share a large healing pool among nearby allies"
                ),

                # Level 6: Blessed Healer
                SubclassFeature(
                    name="Blessed Healer",
                    description="When you cast a spell of 1st level or higher that restores hit points to a creature other than you, you regain hit points equal to 2 + the spell's level.",
                    level=6,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "self_healing_formula": "2 + spell_level",
                        "trigger": "healing_other_with_spell",
                        "applies_to": "spells_1st_or_higher",
                        "target_restriction": "not_self"
                    },
                    tooltip_extended="Gain health when you heal others with spells"
                ),

                # Level 8: Divine Strike
                SubclassFeature(
                    name="Divine Strike",
                    description="Once on each of your turns when you hit a creature with a weapon attack, you can cause the attack to deal an extra 1d8 radiant damage to the target. When you reach 14th level, the extra damage increases to 2d8.",
                    level=8,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "damage_bonus": "1d8",
                        "damage_type": "radiant",
                        "frequency": "once_per_turn",
                        "trigger": "weapon_hit",
                        "scaling": {
                            14: "2d8"
                        }
                    },
                    tooltip_extended="Add radiant damage to one weapon attack per turn"
                ),

                # Level 17: Supreme Healing
                SubclassFeature(
                    name="Supreme Healing",
                    description="When you would normally roll one or more dice to restore hit points with a spell, you instead use the highest number possible for each die. For example, instead of restoring 2d6 hit points to a creature, you restore 12.",
                    level=17,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "maximize_healing_dice": True,
                        "applies_to": "all_healing_spells",
                        "effect": "use_maximum_roll"
                    },
                    tooltip_extended="All healing spells use maximum possible dice rolls"
                )
            ]
        )