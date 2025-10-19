# core
# category: core
"""
School of Evocation Wizard Subclass

Implementation using the scalable subclass architecture.

Phase 2.2: Evocation School Subclass Implementation
Implementation Plan Reference: Phase 2 > Phase 2.2 > Step 2.2.2
"""

from talekeeper.services.enhanced_subclass_manager import (
    SubclassDefinition, SubclassFeature, FeatureType, ActionCost
)


class EvocationDefinition:
    """School of Evocation subclass definition for Wizard."""

    @staticmethod
    def create() -> SubclassDefinition:
        """Create the School of Evocation subclass definition."""
        return SubclassDefinition(
            class_name="wizard",
            subclass_name="evocation",
            description="Evokers focus their study on magic that creates powerful elemental effects such as bitter cold, searing flame, rolling thunder, crackling lightning, and burning acid.",
            flavor_text="Your magic is focused on creating and controlling elemental forces.",
            recommended_abilities=["Intelligence", "Dexterity"],
            features=[
                # Level 2: Sculpt Spells
                SubclassFeature(
                    name="Sculpt Spells",
                    description="When you cast an evocation spell that affects other creatures, you can choose a number of them equal to 1 + the spell's level. The chosen creatures automatically succeed on their saving throws against the spell, and take no damage if they would normally take half damage on a successful save.",
                    level=2,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "spell_school": "evocation",
                        "creatures_affected_formula": "1 + spell_level",
                        "effect": "auto_save_success",
                        "damage_reduction": "none_instead_of_half",
                        "trigger": "evocation_spell_cast"
                    },
                    tooltip_extended="Protect allies from your evocation spells automatically"
                ),

                # Level 6: Potent Cantrip
                SubclassFeature(
                    name="Potent Cantrip",
                    description="Your damaging cantrips affect even creatures that avoid the brunt of the effect. When a creature succeeds on a saving throw against your cantrip, the creature takes half the cantrip's damage (if any) but suffers no additional effect from the cantrip.",
                    level=6,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "applies_to": "damaging_cantrips",
                        "effect": "half_damage_on_save",
                        "trigger": "cantrip_save_success",
                        "damage_type": "same_as_cantrip"
                    },
                    tooltip_extended="Your cantrips always deal some damage, even on successful saves"
                ),

                # Level 10: Empowered Evocation
                SubclassFeature(
                    name="Empowered Evocation",
                    description="You can add your Intelligence modifier to one damage roll of any wizard evocation spell you cast.",
                    level=10,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "damage_bonus": "intelligence_modifier",
                        "applies_to": "wizard_evocation_spells",
                        "frequency": "once_per_spell",
                        "damage_roll": "one_damage_roll_per_spell",
                        "trigger": "evocation_spell_damage"
                    },
                    tooltip_extended="Add Intelligence modifier to one damage roll of evocation spells"
                ),

                # Level 14: Overchannel
                SubclassFeature(
                    name="Overchannel",
                    description="When you cast a wizard spell of 1st through 5th level that deals damage, you can deal maximum damage with that spell. The first time you do so, you suffer no adverse effect. If you use this feature again before you finish a long rest, you take 2d12 necrotic damage for each level of the spell, immediately after you cast it. Each time you use this feature again before finishing a long rest, the necrotic damage per spell level increases by 1d12.",
                    level=14,
                    feature_type=FeatureType.ACTIVATED,
                    action_cost=ActionCost.FREE,
                    uses_per_rest=None,  # Special tracking needed
                    rest_type="long",
                    mechanics={
                        "spell_levels": "1-5",
                        "effect": "maximum_damage",
                        "first_use_penalty": "none",
                        "subsequent_penalty_base": "2d12_necrotic_per_spell_level",
                        "penalty_escalation": "+1d12_per_use",
                        "penalty_timing": "immediately_after_cast",
                        "reset_condition": "long_rest"
                    },
                    tooltip_extended="Deal maximum damage with spells, but suffer increasing necrotic damage"
                ),
            ]
        )

    @staticmethod
    def get_school_bonus_spells() -> dict:
        """
        Get bonus spells known for School of Evocation.
        Note: Evocation wizards don't get bonus spells like domain clerics,
        but this method maintains consistency with the interface.
        """
        return {}

    @staticmethod
    def get_tradition_features(level: int) -> list:
        """Get tradition features available at a given level."""
        features = []

        if level >= 2:
            features.append("Sculpt Spells")
        if level >= 6:
            features.append("Potent Cantrip")
        if level >= 10:
            features.append("Empowered Evocation")
        if level >= 14:
            features.append("Overchannel")

        return features

    @staticmethod
    def calculate_overchannel_damage(uses_today: int, spell_level: int) -> int:
        """
        Calculate necrotic damage from Overchannel use.

        Args:
            uses_today: Number of times Overchannel has been used today
            spell_level: Level of the spell being overchanneled

        Returns:
            Necrotic damage to take (dice count, not rolled)
        """
        if uses_today == 0:
            return 0  # First use has no penalty

        # Base damage: 2d12 per spell level
        # Additional damage: +1d12 per spell level for each previous use
        base_dice = 2
        bonus_dice = uses_today - 1
        total_dice = (base_dice + bonus_dice) * spell_level

        return total_dice  # Return dice count for UI to roll