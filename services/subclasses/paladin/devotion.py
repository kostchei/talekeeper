"""
Oath of Devotion Paladin Subclass

Implementation using the scalable subclass architecture.

Phase 2.3: Oath of Devotion Subclass Implementation
Implementation Plan Reference: Phase 2 > Phase 2.3 > Step 2.3.2
"""

from services.enhanced_subclass_manager import (
    SubclassDefinition, SubclassFeature, FeatureType, ActionCost
)


class DevotionDefinition:
    """Oath of Devotion subclass definition for Paladin."""

    @staticmethod
    def create() -> SubclassDefinition:
        """Create the Oath of Devotion subclass definition."""
        return SubclassDefinition(
            class_name="paladin",
            subclass_name="devotion",
            description="The Oath of Devotion binds a paladin to the loftiest ideals of justice, virtue, and order. Sometimes called cavaliers, white knights, or holy warriors, these paladins meet the ideal of the knight in shining armor.",
            flavor_text="Your oath compels you to fight against the forces of evil and protect the innocent.",
            recommended_abilities=["Strength", "Charisma"],
            features=[
                # Level 3: Channel Divinity - Sacred Weapon
                SubclassFeature(
                    name="Sacred Weapon",
                    description="As an action, you can imbue one weapon that you are holding with positive energy, using your Channel Divinity. For 1 minute, you add your Charisma modifier to attack rolls made with that weapon (with a minimum bonus of +1). The weapon also emits bright light in a 20-foot radius and dim light 20 feet beyond that. If the weapon is not already magical, it becomes magical for the duration.",
                    level=3,
                    feature_type=FeatureType.ACTIVATED,
                    action_cost=ActionCost.ACTION,
                    uses_per_rest=1,
                    rest_type="short",
                    resource_name="Channel Divinity",
                    mechanics={
                        "duration": "1 minute",
                        "attack_bonus": "charisma_modifier_minimum_1",
                        "light_bright": 20,
                        "light_dim": 40,
                        "makes_magical": True,
                        "requires_weapon": True
                    },
                    tooltip_extended="Imbue weapon with divine power, adding Charisma to attacks and creating light"
                ),

                # Level 3: Channel Divinity - Turn the Unholy
                SubclassFeature(
                    name="Turn the Unholy",
                    description="As an action, you present your holy symbol and speak a prayer censuring fiends and undead, using your Channel Divinity. Each fiend or undead that can see or hear you within 30 feet of you must make a Wisdom saving throw. If the creature fails its saving throw, it is turned for 1 minute or until it takes damage.",
                    level=3,
                    feature_type=FeatureType.ACTIVATED,
                    action_cost=ActionCost.ACTION,
                    uses_per_rest=1,
                    rest_type="short",
                    resource_name="Channel Divinity",
                    mechanics={
                        "save_type": "wisdom",
                        "save_dc": "spell_save_dc",
                        "range": 30,
                        "area_type": "all_within_range",
                        "targets": "fiends_and_undead",
                        "duration": "1 minute",
                        "effect": "turned",
                        "ends_on": "damage_taken"
                    },
                    tooltip_extended="Turn fiends and undead within 30 feet using divine authority"
                ),

                # Level 7: Aura of Devotion
                SubclassFeature(
                    name="Aura of Devotion",
                    description="You and friendly creatures within 10 feet of you can't be charmed while you are conscious. At 18th level, the range of this aura increases to 30 feet.",
                    level=7,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "aura_range_10": 10,
                        "aura_range_18": 30,
                        "immunity": "charmed",
                        "affects": "self_and_allies",
                        "requires_conscious": True
                    },
                    tooltip_extended="You and nearby allies are immune to being charmed"
                ),

                # Level 15: Purity of Spirit
                SubclassFeature(
                    name="Purity of Spirit",
                    description="You are always under the effects of a protection from evil and good spell.",
                    level=15,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "spell_effect": "protection_from_evil_and_good",
                        "permanent": True,
                        "cannot_be_dispelled": True
                    },
                    tooltip_extended="Permanent protection from aberrations, celestials, elementals, fey, fiends, and undead"
                ),

                # Level 15: Smite of Protection
                SubclassFeature(
                    name="Smite of Protection",
                    description="When you use your Divine Smite, you or an ally you can see within 30 feet of you gains half cover (+2 AC, +2 Dex saves) until the start of your next turn.",
                    level=15,
                    feature_type=FeatureType.TRIGGERED,
                    action_cost=ActionCost.NONE,
                    mechanics={
                        "trigger": "divine_smite_used",
                        "range": 30,
                        "target": "self_or_ally",
                        "effect": "half_cover",
                        "ac_bonus": 2,
                        "dex_save_bonus": 2,
                        "duration": "until_start_of_your_next_turn"
                    },
                    tooltip_extended="Grant half cover when using Divine Smite"
                ),

                # Level 20: Holy Nimbus
                SubclassFeature(
                    name="Holy Nimbus",
                    description="As an action, you can emanate an aura of sunlight. For 1 minute, bright light shines from you in a 30-foot radius, and dim light shines 30 feet beyond that. Whenever an enemy creature starts its turn in the bright light, the creature takes 10 radiant damage. In addition, for the duration, you have advantage on saving throws against spells cast by fiends or undead.",
                    level=20,
                    feature_type=FeatureType.ACTIVATED,
                    action_cost=ActionCost.ACTION,
                    uses_per_rest=1,
                    rest_type="long",
                    mechanics={
                        "duration": "1 minute",
                        "light_bright": 30,
                        "light_dim": 60,
                        "damage_per_turn": 10,
                        "damage_type": "radiant",
                        "damage_trigger": "enemy_turn_start_in_light",
                        "save_advantage_vs": "fiend_and_undead_spells",
                        "transformation": True
                    },
                    tooltip_extended="Transform into a beacon of divine light dealing damage to enemies"
                ),
            ]
        )

    @staticmethod
    def get_oath_spells(level: int) -> list:
        """Get oath spells available at a given level."""
        oath_spells = {
            3: ["protection_from_evil_and_good", "sanctuary"],
            5: ["lesser_restoration", "zone_of_truth"],
            9: ["beacon_of_hope", "dispel_magic"],
            13: ["freedom_of_movement", "guardian_of_faith"],
            17: ["commune", "flame_strike"]
        }

        spells = []
        for oath_level, spell_list in oath_spells.items():
            if level >= oath_level:
                spells.extend(spell_list)

        return spells

    @staticmethod
    def get_oath_features(level: int) -> list:
        """Get oath features available at a given level."""
        features = []

        if level >= 3:
            features.extend(["Sacred Weapon", "Turn the Unholy"])
        if level >= 7:
            features.append("Aura of Devotion")
        if level >= 15:
            features.extend(["Purity of Spirit", "Smite of Protection"])
        if level >= 20:
            features.append("Holy Nimbus")

        return features

    @staticmethod
    def get_channel_divinity_options(level: int) -> list:
        """Get Channel Divinity options available at a given level."""
        options = []

        if level >= 3:
            options.extend([
                {
                    "name": "Sacred Weapon",
                    "description": "Imbue weapon with divine power",
                    "action_cost": "action",
                    "duration": "1 minute"
                },
                {
                    "name": "Turn the Unholy",
                    "description": "Turn fiends and undead within 30 feet",
                    "action_cost": "action",
                    "save": "Wisdom",
                    "range": "30 feet"
                }
            ])

        return options

    @staticmethod
    def calculate_sacred_weapon_bonus(charisma_modifier: int) -> int:
        """Calculate Sacred Weapon attack bonus."""
        return max(1, charisma_modifier)

    @staticmethod
    def get_aura_range(level: int) -> int:
        """Get Aura of Devotion range based on level."""
        return 30 if level >= 18 else 10