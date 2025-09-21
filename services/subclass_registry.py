"""
Subclass Registry for TaleKeeper

Central registry for all subclass definitions. Provides lazy loading and caching
to efficiently manage 44+ subclasses across 11 classes.
"""

from typing import Dict, Optional, Tuple, Type
from importlib import import_module
from services.enhanced_subclass_manager import SubclassDefinition


class SubclassRegistry:
    """
    Registry for all subclass definitions.

    Handles lazy loading of subclass modules to keep memory usage low
    and startup times fast while supporting 44+ subclasses.
    """

    # Map of (class_name, subclass_name) -> module path
    SUBCLASS_MODULES = {
        # Barbarian subclasses
        ("barbarian", "berserker"): "services.enhanced_subclass_manager.BerserkerDefinition",
        ("barbarian", "totem_warrior"): "services.subclasses.barbarian.totem_warrior.TotemWarriorDefinition",
        ("barbarian", "ancestral_guardian"): "services.subclasses.barbarian.ancestral_guardian.AncestralGuardianDefinition",
        ("barbarian", "wild_heart"): "services.subclasses.barbarian.wild_heart.WildHeartDefinition",

        # Fighter subclasses
        ("fighter", "champion"): "services.subclasses.fighter.champion.ChampionDefinition",
        ("fighter", "battle_master"): "services.subclasses.fighter.battle_master.BattleMasterDefinition",
        ("fighter", "eldritch_knight"): "services.subclasses.fighter.eldritch_knight.EldritchKnightDefinition",
        ("fighter", "psi_warrior"): "services.subclasses.fighter.psi_warrior.PsiWarriorDefinition",

        # Rogue subclasses
        ("rogue", "thief"): "services.subclasses.rogue.thief.ThiefDefinition",
        ("rogue", "assassin"): "services.subclasses.rogue.assassin.AssassinDefinition",
        ("rogue", "arcane_trickster"): "services.subclasses.rogue.arcane_trickster.ArcaneTricksterDefinition",
        ("rogue", "swashbuckler"): "services.subclasses.rogue.swashbuckler.SwashbucklerDefinition",

        # Wizard subclasses
        ("wizard", "evocation"): "services.subclasses.wizard.evocation.EvocationDefinition",
        ("wizard", "abjuration"): "services.subclasses.wizard.abjuration.AbjurationDefinition",
        ("wizard", "divination"): "services.subclasses.wizard.divination.DivinationDefinition",
        ("wizard", "necromancy"): "services.subclasses.wizard.necromancy.NecromancyDefinition",

        # Cleric subclasses
        ("cleric", "life"): "services.subclasses.cleric.life.LifeDefinition",
        ("cleric", "light"): "services.subclasses.cleric.light.LightDefinition",
        ("cleric", "war"): "services.subclasses.cleric.war.WarDefinition",
        ("cleric", "trickery"): "services.subclasses.cleric.trickery.TrickeryDefinition",

        # Paladin subclasses
        ("paladin", "devotion"): "services.subclasses.paladin.devotion.DevotionDefinition",
        ("paladin", "ancients"): "services.subclasses.paladin.ancients.AncientsDefinition",
        ("paladin", "vengeance"): "services.subclasses.paladin.vengeance.VengeanceDefinition",
        ("paladin", "glory"): "services.subclasses.paladin.glory.GloryDefinition",

        # Ranger subclasses
        ("ranger", "hunter"): "services.subclasses.ranger.hunter.HunterDefinition",
        ("ranger", "beast_master"): "services.subclasses.ranger.beast_master.BeastMasterDefinition",
        ("ranger", "gloom_stalker"): "services.subclasses.ranger.gloom_stalker.GloomStalkerDefinition",
        ("ranger", "fey_wanderer"): "services.subclasses.ranger.fey_wanderer.FeyWandererDefinition",

        # Warlock subclasses
        ("warlock", "fiend"): "services.subclasses.warlock.fiend.FiendDefinition",
        ("warlock", "archfey"): "services.subclasses.warlock.archfey.ArchfeyDefinition",
        ("warlock", "great_old_one"): "services.subclasses.warlock.great_old_one.GreatOldOneDefinition",
        ("warlock", "celestial"): "services.subclasses.warlock.celestial.CelestialDefinition",

        # Bard subclasses
        ("bard", "lore"): "services.subclasses.bard.lore.LoreDefinition",
        ("bard", "valor"): "services.subclasses.bard.valor.ValorDefinition",
        ("bard", "glamour"): "services.subclasses.bard.glamour.GlamourDefinition",
        ("bard", "whispers"): "services.subclasses.bard.whispers.WhispersDefinition",

        # Druid subclasses
        ("druid", "land"): "services.subclasses.druid.land.LandDefinition",
        ("druid", "moon"): "services.subclasses.druid.moon.MoonDefinition",
        ("druid", "dreams"): "services.subclasses.druid.dreams.DreamsDefinition",
        ("druid", "stars"): "services.subclasses.druid.stars.StarsDefinition",

        # Sorcerer subclasses
        ("sorcerer", "draconic_bloodline"): "services.subclasses.sorcerer.draconic_bloodline.DraconicBloodlineDefinition",
        ("sorcerer", "wild_magic"): "services.subclasses.sorcerer.wild_magic.WildMagicDefinition",
        ("sorcerer", "divine_soul"): "services.subclasses.sorcerer.divine_soul.DivineSoulDefinition",
        ("sorcerer", "aberrant_mind"): "services.subclasses.sorcerer.aberrant_mind.AberrantMindDefinition",
    }

    def __init__(self):
        """Initialize the registry with an empty cache."""
        self._cache: Dict[Tuple[str, str], SubclassDefinition] = {}
        self._available_cache: Dict[str, Dict[str, str]] = {}

    def get_subclass(self, class_name: str, subclass_name: str) -> Optional[SubclassDefinition]:
        """
        Get a subclass definition, loading it if necessary.

        Args:
            class_name: The base class (e.g., "fighter")
            subclass_name: The subclass name (e.g., "champion")

        Returns:
            The SubclassDefinition or None if not found
        """
        key = (class_name.lower(), subclass_name.lower())

        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Try to load the subclass
        module_path = self.SUBCLASS_MODULES.get(key)
        if not module_path:
            return None

        try:
            # Split module path and class name
            module_name, class_name = module_path.rsplit('.', 1)

            # Import the module
            module = import_module(module_name)

            # Get the definition class
            definition_class = getattr(module, class_name)

            # Create the subclass definition
            subclass_def = definition_class.create()

            # Cache it
            self._cache[key] = subclass_def

            return subclass_def

        except (ImportError, AttributeError, TypeError) as e:
            print(f"[SubclassRegistry] Failed to load {key}: {e}")
            return None

    def get_available_subclasses(self, class_name: str) -> Dict[str, str]:
        """
        Get all available subclass names and descriptions for a class.

        Args:
            class_name: The base class name

        Returns:
            Dict mapping subclass_id to display name
        """
        class_lower = class_name.lower()

        if class_lower in self._available_cache:
            return self._available_cache[class_lower]

        available = {}
        for (cls, sub), _ in self.SUBCLASS_MODULES.items():
            if cls == class_lower:
                # Try to get the display name from the definition
                subclass_def = self.get_subclass(cls, sub)
                if subclass_def:
                    # Use the subclass name from the definition if available
                    display_name = sub.replace('_', ' ').title()
                    available[sub] = display_name
                else:
                    # Fallback to formatted subclass name
                    available[sub] = sub.replace('_', ' ').title()

        self._available_cache[class_lower] = available
        return available

    def is_subclass_available(self, class_name: str, subclass_name: str) -> bool:
        """Check if a specific subclass is available."""
        key = (class_name.lower(), subclass_name.lower())
        return key in self.SUBCLASS_MODULES

    def get_all_classes_with_subclasses(self) -> Dict[str, int]:
        """
        Get all classes that have subclasses defined.

        Returns:
            Dict mapping class name to count of subclasses
        """
        class_counts = {}
        for (cls, _), _ in self.SUBCLASS_MODULES.items():
            class_counts[cls] = class_counts.get(cls, 0) + 1
        return class_counts

    def clear_cache(self):
        """Clear the cached subclass definitions."""
        self._cache.clear()
        self._available_cache.clear()


# Singleton instance
subclass_registry = SubclassRegistry()