"""
Enhanced Subclass Manager for TaleKeeper

Provides a more comprehensive subclass system that includes:
- Feature type categorization (passive, activated, triggered, reaction)
- Resource tracking for feature uses
- Integration with condition system for immunities
- Structured feature definitions for all subclasses
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class FeatureType(Enum):
    """Types of subclass features."""
    PASSIVE = "passive"  # Always active (e.g., Danger Sense)
    ACTIVATED = "activated"  # Requires action/bonus action (e.g., Rage)
    TRIGGERED = "triggered"  # Activates under conditions (e.g., Relentless Rage)
    REACTION = "reaction"  # Uses reaction (e.g., Retaliation)
    RESOURCE = "resource"  # Provides uses of something (e.g., Rage uses)


class ActionCost(Enum):
    """Action economy cost for features."""
    NONE = "none"  # Passive or automatic
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    MOVEMENT = "movement"
    FREE = "free"  # Can be done without using action economy


@dataclass
class SubclassFeature:
    """Enhanced subclass feature definition."""
    name: str
    description: str
    level: int
    feature_type: FeatureType
    action_cost: ActionCost = ActionCost.NONE

    # Resource management
    uses_per_rest: Optional[int] = None
    rest_type: Optional[str] = None  # "short", "long", "none"
    resource_name: Optional[str] = None  # e.g., "Rage", "Superiority Dice"

    # Mechanical effects
    mechanics: Dict[str, Any] = field(default_factory=dict)
    prerequisites: Dict[str, Any] = field(default_factory=dict)  # Conditions to use
    duration: Optional[str] = None  # "instant", "1 round", "1 minute", etc.

    # Integration points
    condition_immunities: List[str] = field(default_factory=list)
    damage_modifications: Dict[str, Any] = field(default_factory=dict)
    saving_throw_modifiers: Dict[str, Any] = field(default_factory=dict)

    # UI/Display
    icon: Optional[str] = None
    tooltip_extended: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['feature_type'] = self.feature_type.value
        data['action_cost'] = self.action_cost.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubclassFeature':
        """Create from dictionary."""
        data = data.copy()
        data['feature_type'] = FeatureType(data['feature_type'])
        data['action_cost'] = ActionCost(data['action_cost'])
        return cls(**data)


@dataclass
class SubclassDefinition:
    """Complete subclass definition with all features."""
    class_name: str  # e.g., "barbarian"
    subclass_name: str  # e.g., "berserker"
    description: str
    features: List[SubclassFeature]

    # Flavor
    flavor_text: Optional[str] = None
    recommended_abilities: List[str] = field(default_factory=list)

    def get_features_at_level(self, level: int) -> List[SubclassFeature]:
        """Get all features available at a specific level."""
        return [f for f in self.features if f.level <= level]

    def get_features_by_type(self, feature_type: FeatureType) -> List[SubclassFeature]:
        """Get all features of a specific type."""
        return [f for f in self.features if f.feature_type == feature_type]


class BerserkerDefinition:
    """Berserker subclass definition for Barbarian."""

    @staticmethod
    def create() -> SubclassDefinition:
        """Create the Berserker subclass definition."""
        return SubclassDefinition(
            class_name="barbarian",
            subclass_name="berserker",
            description="Barbarians who follow the Path of the Berserker combine rage with bloodthirsty frenzy.",
            flavor_text="For some barbarians, rage is a means to an end—that end being violence. The Path of the Berserker is a path of untrammeled fury, slick with blood.",
            recommended_abilities=["Strength", "Constitution"],
            features=[
                # Level 3: Frenzy
                SubclassFeature(
                    name="Frenzy",
                    description="When you Reckless Attack while Raging, you deal extra damage equal to a roll of a d6 to the first enemy you hit on your turn. The d6 becomes a d8 at 9th level and a d10 at 16th level.",
                    level=3,
                    feature_type=FeatureType.TRIGGERED,
                    action_cost=ActionCost.NONE,
                    prerequisites={"raging": True, "reckless_attack": True},
                    mechanics={
                        "damage_bonus_dice": {
                            3: "1d6",
                            9: "1d8",
                            16: "1d10"
                        },
                        "trigger": "first_hit_while_reckless_and_raging",
                        "damage_type": "same_as_weapon"
                    },
                    tooltip_extended="Automatically triggers when you hit with Reckless Attack while Raging"
                ),

                # Level 6: Mindless Rage
                SubclassFeature(
                    name="Mindless Rage",
                    description="While Raging, you have Immunity to the Charmed and Frightened conditions. If you're Charmed or Frightened when you enter your Rage, the condition ends on you.",
                    level=6,
                    feature_type=FeatureType.PASSIVE,
                    action_cost=ActionCost.NONE,
                    prerequisites={"raging": True},
                    condition_immunities=["charmed", "frightened"],
                    mechanics={
                        "remove_on_rage_start": ["charmed", "frightened"],
                        "immunity_while_raging": ["charmed", "frightened"]
                    },
                    tooltip_extended="Provides complete immunity to fear and charm effects during rage"
                ),

                # Level 10: Retaliation
                SubclassFeature(
                    name="Retaliation",
                    description="When you take damage from a creature that is within 5 feet of you, you can use your Reaction to make one melee attack against that creature. This attack adds your Rage Damage bonus if you are Raging.",
                    level=10,
                    feature_type=FeatureType.REACTION,
                    action_cost=ActionCost.REACTION,
                    prerequisites={"enemy_within_5ft": True, "took_damage": True},
                    mechanics={
                        "trigger": "damaged_by_adjacent_enemy",
                        "range": 5,
                        "attack_type": "melee_weapon_or_unarmed",
                        "adds_rage_damage": True
                    },
                    tooltip_extended="React immediately when damaged by adjacent enemies"
                ),

                # Level 14: Intimidating Presence
                SubclassFeature(
                    name="Intimidating Presence",
                    description="As a Bonus Action, each creature of your choice in a 30-foot Emanation originating from you must make a Wisdom saving throw (DC 8 + your Strength modifier + your Proficiency Bonus). On a failed save, a creature has the Frightened condition for 1 minute. At the end of each of the Frightened creature's turns, it repeats the save, ending the effect on itself on a success.",
                    level=14,
                    feature_type=FeatureType.ACTIVATED,
                    action_cost=ActionCost.BONUS_ACTION,
                    uses_per_rest=1,
                    rest_type="long",
                    duration="1 minute",
                    mechanics={
                        "area": "30ft_emanation",
                        "save": "wisdom",
                        "dc_calculation": "8 + str_mod + prof_bonus",
                        "condition_applied": "frightened",
                        "duration": "1_minute",
                        "repeat_save": "end_of_turn",
                        "once_per_target": True  # Once a creature succeeds, immune for 24 hours
                    },
                    tooltip_extended="Frighten multiple enemies in a 30-foot area"
                )
            ]
        )


class EnhancedSubclassManager:
    """Enhanced manager for subclass features and mechanics."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._ensure_tables()

        # Use the registry for subclass definitions instead of local storage
        self._registry = None  # Lazy load to avoid circular imports

    def _ensure_tables(self):
        """Create enhanced subclass tables if needed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Enhanced subclass features table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_subclass_features (
                    character_id TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    feature_data TEXT NOT NULL,
                    uses_remaining INTEGER,
                    active BOOLEAN DEFAULT FALSE,
                    last_used TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    PRIMARY KEY (character_id, feature_name),
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)

            # Feature resource tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subclass_resources (
                    character_id TEXT NOT NULL,
                    resource_name TEXT NOT NULL,
                    current_uses INTEGER DEFAULT 0,
                    max_uses INTEGER DEFAULT 0,
                    last_reset TEXT,
                    PRIMARY KEY (character_id, resource_name),
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)

            conn.commit()

    def get_subclass_definition(self, class_name: str, subclass_name: str) -> Optional[SubclassDefinition]:
        """Get a subclass definition using the registry."""
        if self._registry is None:
            from services.subclass_registry import subclass_registry
            self._registry = subclass_registry
        return self._registry.get_subclass(class_name, subclass_name)

    def get_character_subclass_features(self, character_id: str, level: int) -> List[SubclassFeature]:
        """Get all subclass features available to a character at their level."""
        # Get character's class and subclass
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.class_id, cs.subclass_id
                FROM characters c
                LEFT JOIN character_subclasses cs ON c.id = cs.character_id
                WHERE c.id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if not row:
                return []

            class_id = row[0]
            subclass_id = row[1] if row[1] else None

            # Fallback to legacy subclass field if needed
            if not subclass_id:
                cursor.execute("SELECT subclass_id FROM characters WHERE id = ?", (character_id,))
                legacy = cursor.fetchone()
                if legacy:
                    subclass_id = legacy[0]

        if not class_id or not subclass_id:
            return []

        # Get subclass definition
        definition = self.get_subclass_definition(class_id, subclass_id)
        if not definition:
            return []

        return definition.get_features_at_level(level)

    def apply_mindless_rage(self, character_id: str) -> Dict[str, Any]:
        """Apply Mindless Rage immunity when raging."""
        try:
            from services.condition_manager import ConditionManager, ConditionType
            condition_manager = ConditionManager(self.db_path)

            # Check if character is raging
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT is_raging FROM barbarian_features WHERE character_id = ?
                """, (character_id,))
                row = cursor.fetchone()

                if not row or not row[0]:
                    return {"success": False, "reason": "Not raging"}

            # Check for existing conditions BEFORE applying immunities
            removed = []
            if condition_manager.has_condition(character_id, ConditionType.CHARMED):
                removed.append("charmed")

            if condition_manager.has_condition(character_id, ConditionType.FRIGHTENED):
                removed.append("frightened")

            # Apply immunities (this will also remove existing conditions)
            condition_manager.add_immunity(character_id, ConditionType.CHARMED, "Mindless Rage", "while_raging")
            condition_manager.add_immunity(character_id, ConditionType.FRIGHTENED, "Mindless Rage", "while_raging")

            return {
                "success": True,
                "immunities_applied": ["charmed", "frightened"],
                "conditions_removed": removed
            }

        except ImportError:
            return {"success": False, "reason": "Condition system not available"}

    def remove_rage_immunities(self, character_id: str):
        """Remove Mindless Rage immunities when rage ends."""
        try:
            from services.condition_manager import ConditionManager, ConditionType
            condition_manager = ConditionManager(self.db_path)

            condition_manager.remove_immunity(character_id, ConditionType.CHARMED, "Mindless Rage")
            condition_manager.remove_immunity(character_id, ConditionType.FRIGHTENED, "Mindless Rage")

            return {"success": True}

        except ImportError:
            return {"success": False, "reason": "Condition system not available"}

    def use_intimidating_presence(self, character_id: str) -> Dict[str, Any]:
        """Use Intimidating Presence ability."""
        # Check uses remaining
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if feature is available
            cursor.execute("""
                SELECT current_uses, max_uses
                FROM subclass_resources
                WHERE character_id = ? AND resource_name = 'Intimidating Presence'
            """, (character_id,))

            row = cursor.fetchone()
            if not row:
                # Initialize resource tracking
                cursor.execute("""
                    INSERT INTO subclass_resources (character_id, resource_name, current_uses, max_uses)
                    VALUES (?, 'Intimidating Presence', 0, 1)
                """, (character_id,))
                conn.commit()
                current_uses = 0
                max_uses = 1
            else:
                current_uses, max_uses = row

            if current_uses >= max_uses:
                return {"success": False, "reason": "No uses remaining (resets on long rest)"}

            # Calculate save DC
            cursor.execute("""
                SELECT strength, proficiency_bonus
                FROM characters WHERE id = ?
            """, (character_id,))

            char_row = cursor.fetchone()
            if not char_row:
                return {"success": False, "reason": "Character not found"}

            strength = char_row[0] or 10
            prof_bonus = char_row[1] or 2
            str_mod = (strength - 10) // 2
            save_dc = 8 + str_mod + prof_bonus

            # Use the ability
            cursor.execute("""
                UPDATE subclass_resources
                SET current_uses = current_uses + 1
                WHERE character_id = ? AND resource_name = 'Intimidating Presence'
            """, (character_id,))
            conn.commit()

            return {
                "success": True,
                "save_dc": save_dc,
                "area": "30ft emanation",
                "duration": "1 minute",
                "condition": "frightened",
                "uses_remaining": max_uses - current_uses - 1
            }

    def check_frenzy_trigger(self, character_id: str) -> Dict[str, Any]:
        """Check if Frenzy damage should be applied."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if raging and using reckless attack
            cursor.execute("""
                SELECT bf.is_raging, bf.level, cs.reckless_attack_active
                FROM barbarian_features bf
                LEFT JOIN character_combat_state cs ON bf.character_id = cs.character_id
                WHERE bf.character_id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if not row:
                return {"triggered": False}

            is_raging = row[0]
            level = row[1]
            reckless_active = row[2] if row[2] else False

            if not (is_raging and reckless_active and level >= 3):
                return {"triggered": False}

            # Determine damage dice based on level
            if level >= 16:
                damage_dice = "1d10"
            elif level >= 9:
                damage_dice = "1d8"
            else:
                damage_dice = "1d6"

            return {
                "triggered": True,
                "damage_dice": damage_dice,
                "applies_to": "first_hit_this_turn"
            }

    def reset_resources(self, character_id: str, rest_type: str):
        """Reset subclass resources on rest."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if rest_type == "long":
                # Reset all long rest resources
                cursor.execute("""
                    UPDATE subclass_resources
                    SET current_uses = 0
                    WHERE character_id = ?
                """, (character_id,))

            # Future: Handle short rest resources when added

            conn.commit()


# Singleton instance
enhanced_subclass_manager = EnhancedSubclassManager()