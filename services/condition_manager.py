"""
Condition Management System for D&D 2024

Handles all condition tracking, application, and mechanical effects.
This is a new system that doesn't break existing functionality.
"""

import sqlite3
import json
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class ConditionType(Enum):
    """D&D 2024 Conditions from SRD."""
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    EXHAUSTION = "exhaustion"  # Special: Has levels 1-6
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"  # Key for Danger Sense
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"


@dataclass
class ActiveCondition:
    """Represents an active condition on a character."""
    condition_type: ConditionType
    source: str  # "Spell: Hold Person", "Monster: Medusa's Gaze"
    duration_type: str  # "rounds", "minutes", "hours", "save_ends", "permanent"
    duration_remaining: int = -1  # -1 for indefinite
    save_dc: Optional[int] = None
    save_ability: Optional[str] = None  # "constitution", "wisdom", etc.
    save_frequency: str = "end_of_turn"  # "start_of_turn", "end_of_turn"
    concentration_caster: Optional[str] = None  # ID of caster maintaining concentration
    applied_at_round: int = 0
    exhaustion_level: int = 0  # For exhaustion condition
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        data['condition_type'] = self.condition_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActiveCondition':
        """Create from dictionary."""
        data['condition_type'] = ConditionType(data['condition_type'])
        return cls(**data)


class ConditionEffects:
    """Mechanical effects of each condition per D&D 2024 rules."""

    EFFECTS = {
        ConditionType.BLINDED: {
            "auto_fail_sight_checks": True,
            "attack_rolls": "disadvantage",
            "attack_rolls_against": "advantage"
        },
        ConditionType.CHARMED: {
            "cannot_attack_charmer": True,
            "charmer_social_checks": "advantage"
        },
        ConditionType.DEAFENED: {
            "auto_fail_hearing_checks": True
        },
        ConditionType.EXHAUSTION: {
            "levels": True,  # Special handling
            "d20_test_penalty": "minus_2_per_level",
            "speed_reduction": "minus_5ft_per_level",
            "death_at_level_6": True
        },
        ConditionType.FRIGHTENED: {
            "ability_checks": "disadvantage_if_source_visible",
            "attack_rolls": "disadvantage_if_source_visible",
            "movement_restriction": "cannot_move_closer_to_source"
        },
        ConditionType.GRAPPLED: {
            "movement_speed": 0,
            "attack_rolls_not_grappler": "disadvantage",
            "can_be_dragged": True
        },
        ConditionType.INCAPACITATED: {
            "no_actions": True,
            "no_bonus_actions": True,
            "no_reactions": True,
            "breaks_concentration": True,
            "cannot_speak": True,
            "initiative_disadvantage": True
        },
        ConditionType.INVISIBLE: {
            "attack_rolls": "advantage",
            "attack_rolls_against": "disadvantage",
            "can_be_detected": "other_senses"
        },
        ConditionType.PARALYZED: {
            "has_incapacitated": True,  # Includes incapacitated
            "movement_speed": 0,
            "saving_throws": {"strength": "auto_fail", "dexterity": "auto_fail"},
            "attack_rolls_against": "advantage",
            "critical_hits_within_5ft": True
        },
        ConditionType.PETRIFIED: {
            "has_incapacitated": True,
            "attack_rolls_against": "advantage",
            "saving_throws": {"strength": "auto_fail", "dexterity": "auto_fail"},
            "damage_resistance": "all",
            "poison_immunity": True,
            "disease_immunity": True,
            "aging_immunity": True,
            "weight_times_10": True
        },
        ConditionType.POISONED: {
            "ability_checks": "disadvantage",
            "attack_rolls": "disadvantage"
        },
        ConditionType.PRONE: {
            "movement_options": "crawl_or_half_speed_to_stand",
            "attack_rolls": "disadvantage",
            "melee_attacks_against_within_5ft": "advantage",
            "ranged_attacks_against": "disadvantage"
        },
        ConditionType.RESTRAINED: {
            "movement_speed": 0,
            "attack_rolls": "disadvantage",
            "attack_rolls_against": "advantage",
            "dexterity_saves": "disadvantage"
        },
        ConditionType.STUNNED: {
            "has_incapacitated": True,
            "saving_throws": {"strength": "auto_fail", "dexterity": "auto_fail"},
            "attack_rolls_against": "advantage"
        },
        ConditionType.UNCONSCIOUS: {
            "has_incapacitated": True,
            "has_prone": True,
            "drops_held_items": True,
            "movement_speed": 0,
            "attack_rolls_against": "advantage",
            "saving_throws": {"strength": "auto_fail", "dexterity": "auto_fail"},
            "critical_hits_within_5ft": True,
            "unaware_of_surroundings": True
        }
    }

    @classmethod
    def get_effects(cls, condition_type: ConditionType) -> Dict[str, Any]:
        """Get the mechanical effects of a condition."""
        return cls.EFFECTS.get(condition_type, {})

    @classmethod
    def is_incapacitating(cls, condition_type: ConditionType) -> bool:
        """Check if a condition is incapacitating."""
        if condition_type == ConditionType.INCAPACITATED:
            return True

        effects = cls.get_effects(condition_type)
        return effects.get("has_incapacitated", False)


class ConditionManager:
    """Manages all character conditions."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._ensure_tables()
        # Cache for active conditions to minimize DB queries
        self._condition_cache: Dict[str, List[ActiveCondition]] = {}

    def _ensure_tables(self):
        """Create condition tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Active conditions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    condition_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    duration_type TEXT NOT NULL DEFAULT 'rounds',
                    duration_remaining INTEGER DEFAULT -1,
                    save_dc INTEGER,
                    save_ability TEXT,
                    save_frequency TEXT DEFAULT 'end_of_turn',
                    concentration_caster TEXT,
                    applied_at_round INTEGER DEFAULT 0,
                    exhaustion_level INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            """)

            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_character_conditions_character
                ON character_conditions(character_id)
            """)

            # Condition immunities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_condition_immunities (
                    character_id TEXT NOT NULL,
                    condition_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    duration TEXT DEFAULT 'permanent',
                    PRIMARY KEY (character_id, condition_type, source),
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def add_condition(self, character_id: str, condition: ActiveCondition) -> bool:
        """Add a condition to a character."""
        # Check for immunity
        if self.is_immune_to_condition(character_id, condition.condition_type):
            print(f"[ConditionManager] {character_id} is immune to {condition.condition_type.value}")
            return False

        # Special handling for exhaustion (levels stack)
        if condition.condition_type == ConditionType.EXHAUSTION:
            return self._add_exhaustion_level(character_id, condition.exhaustion_level or 1, condition.source)

        # Check if condition already exists (conditions don't stack except exhaustion)
        existing = self.get_condition(character_id, condition.condition_type)
        if existing:
            print(f"[ConditionManager] {character_id} already has {condition.condition_type.value}")
            return False

        # Add to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_conditions
                (character_id, condition_type, source, duration_type, duration_remaining,
                 save_dc, save_ability, save_frequency, concentration_caster,
                 applied_at_round, exhaustion_level, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                character_id, condition.condition_type.value, condition.source,
                condition.duration_type, condition.duration_remaining,
                condition.save_dc, condition.save_ability, condition.save_frequency,
                condition.concentration_caster, condition.applied_at_round,
                condition.exhaustion_level, json.dumps(condition.metadata),
                condition.created_at
            ))
            conn.commit()

        # Clear cache for this character
        if character_id in self._condition_cache:
            del self._condition_cache[character_id]

        print(f"[ConditionManager] Applied {condition.condition_type.value} to {character_id}")
        return True

    def remove_condition(self, character_id: str, condition_type: ConditionType,
                        reason: str = "effect_ended") -> bool:
        """Remove a condition from a character."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Special handling for exhaustion
            if condition_type == ConditionType.EXHAUSTION:
                return self._reduce_exhaustion_level(character_id, 1, reason)

            cursor.execute("""
                DELETE FROM character_conditions
                WHERE character_id = ? AND condition_type = ?
            """, (character_id, condition_type.value))

            affected = cursor.rowcount > 0
            conn.commit()

        # Clear cache
        if character_id in self._condition_cache:
            del self._condition_cache[character_id]

        if affected:
            print(f"[ConditionManager] Removed {condition_type.value} from {character_id} ({reason})")

        return affected

    def get_active_conditions(self, character_id: str) -> List[ActiveCondition]:
        """Get all active conditions on a character."""
        # Check cache first
        if character_id in self._condition_cache:
            return self._condition_cache[character_id]

        conditions = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM character_conditions
                WHERE character_id = ?
            """, (character_id,))

            for row in cursor.fetchall():
                condition = ActiveCondition(
                    condition_type=ConditionType(row['condition_type']),
                    source=row['source'],
                    duration_type=row['duration_type'],
                    duration_remaining=row['duration_remaining'],
                    save_dc=row['save_dc'],
                    save_ability=row['save_ability'],
                    save_frequency=row['save_frequency'],
                    concentration_caster=row['concentration_caster'],
                    applied_at_round=row['applied_at_round'],
                    exhaustion_level=row['exhaustion_level'],
                    metadata=json.loads(row['metadata']),
                    created_at=row['created_at']
                )
                conditions.append(condition)

        # Cache the result
        self._condition_cache[character_id] = conditions
        return conditions

    def get_condition(self, character_id: str, condition_type: ConditionType) -> Optional[ActiveCondition]:
        """Get a specific condition on a character."""
        conditions = self.get_active_conditions(character_id)
        for condition in conditions:
            if condition.condition_type == condition_type:
                return condition
        return None

    def has_condition(self, character_id: str, condition_type: ConditionType) -> bool:
        """Check if a character has a specific condition."""
        return self.get_condition(character_id, condition_type) is not None

    def has_incapacitating_condition(self, character_id: str) -> bool:
        """Check if character has any incapacitating condition (for Danger Sense)."""
        conditions = self.get_active_conditions(character_id)
        for condition in conditions:
            if ConditionEffects.is_incapacitating(condition.condition_type):
                return True
        return False

    def get_exhaustion_level(self, character_id: str) -> int:
        """Get current exhaustion level (0-6)."""
        condition = self.get_condition(character_id, ConditionType.EXHAUSTION)
        return condition.exhaustion_level if condition else 0

    def _add_exhaustion_level(self, character_id: str, levels: int = 1, source: str = "effect") -> bool:
        """Add exhaustion levels (special stacking condition)."""
        current_level = self.get_exhaustion_level(character_id)
        new_level = min(6, current_level + levels)

        if new_level == current_level:
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if current_level == 0:
                # Add new exhaustion condition
                cursor.execute("""
                    INSERT INTO character_conditions
                    (character_id, condition_type, source, exhaustion_level, duration_type)
                    VALUES (?, 'exhaustion', ?, ?, 'permanent')
                """, (character_id, source, new_level))
            else:
                # Update existing exhaustion level
                cursor.execute("""
                    UPDATE character_conditions
                    SET exhaustion_level = ?, source = ?
                    WHERE character_id = ? AND condition_type = 'exhaustion'
                """, (new_level, source, character_id))

            conn.commit()

        # Clear cache
        if character_id in self._condition_cache:
            del self._condition_cache[character_id]

        print(f"[ConditionManager] {character_id} exhaustion level: {current_level} -> {new_level}")

        if new_level >= 6:
            print(f"[ConditionManager] {character_id} has died from exhaustion!")

        return True

    def _reduce_exhaustion_level(self, character_id: str, levels: int = 1, reason: str = "long_rest") -> bool:
        """Reduce exhaustion levels."""
        current_level = self.get_exhaustion_level(character_id)
        if current_level == 0:
            return False

        new_level = max(0, current_level - levels)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if new_level == 0:
                # Remove exhaustion completely
                cursor.execute("""
                    DELETE FROM character_conditions
                    WHERE character_id = ? AND condition_type = 'exhaustion'
                """, (character_id,))
            else:
                # Update exhaustion level
                cursor.execute("""
                    UPDATE character_conditions
                    SET exhaustion_level = ?
                    WHERE character_id = ? AND condition_type = 'exhaustion'
                """, (new_level, character_id))

            conn.commit()

        # Clear cache
        if character_id in self._condition_cache:
            del self._condition_cache[character_id]

        print(f"[ConditionManager] {character_id} exhaustion reduced: {current_level} -> {new_level} ({reason})")
        return True

    def add_immunity(self, character_id: str, condition_type: ConditionType,
                    source: str = "feature", duration: str = "permanent"):
        """Add immunity to a condition."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO character_condition_immunities
                (character_id, condition_type, source, duration)
                VALUES (?, ?, ?, ?)
            """, (character_id, condition_type.value, source, duration))
            conn.commit()

        # If character has this condition and gained immunity, remove it
        if self.has_condition(character_id, condition_type):
            self.remove_condition(character_id, condition_type, "gained_immunity")

    def remove_immunity(self, character_id: str, condition_type: ConditionType, source: str = "feature"):
        """Remove immunity to a condition."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM character_condition_immunities
                WHERE character_id = ? AND condition_type = ? AND source = ?
            """, (character_id, condition_type.value, source))
            conn.commit()

    def is_immune_to_condition(self, character_id: str, condition_type: ConditionType) -> bool:
        """Check if character is immune to a condition."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM character_condition_immunities
                WHERE character_id = ? AND condition_type = ?
                LIMIT 1
            """, (character_id, condition_type.value))

            return cursor.fetchone() is not None

    def process_turn_start(self, character_id: str, current_round: int) -> List[str]:
        """Process condition effects at start of turn."""
        messages = []
        conditions = self.get_active_conditions(character_id)

        for condition in conditions:
            # Handle duration
            if condition.duration_type == "rounds" and condition.duration_remaining > 0:
                condition.duration_remaining -= 1
                if condition.duration_remaining == 0:
                    self.remove_condition(character_id, condition.condition_type, "duration_expired")
                    messages.append(f"{condition.condition_type.value.title()} ended")
                else:
                    self._update_duration(character_id, condition.condition_type, condition.duration_remaining)

            # Handle start-of-turn saves
            if condition.save_frequency == "start_of_turn" and condition.save_dc:
                messages.append(f"Make a {condition.save_ability} save (DC {condition.save_dc}) for {condition.condition_type.value}")

        return messages

    def process_turn_end(self, character_id: str, current_round: int) -> List[str]:
        """Process condition effects at end of turn."""
        messages = []
        conditions = self.get_active_conditions(character_id)

        for condition in conditions:
            # Handle end-of-turn saves
            if condition.save_frequency == "end_of_turn" and condition.save_dc:
                messages.append(f"Make a {condition.save_ability} save (DC {condition.save_dc}) for {condition.condition_type.value}")

        return messages

    def _update_duration(self, character_id: str, condition_type: ConditionType, new_duration: int):
        """Update the duration of a condition."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_conditions
                SET duration_remaining = ?
                WHERE character_id = ? AND condition_type = ?
            """, (new_duration, character_id, condition_type.value))
            conn.commit()

        # Clear cache
        if character_id in self._condition_cache:
            del self._condition_cache[character_id]

    def clear_all_conditions(self, character_id: str, reason: str = "effect"):
        """Remove all conditions from a character (e.g., Greater Restoration)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM character_conditions
                WHERE character_id = ?
            """, (character_id,))
            conn.commit()

        # Clear cache
        if character_id in self._condition_cache:
            del self._condition_cache[character_id]

        print(f"[ConditionManager] Cleared all conditions from {character_id} ({reason})")

    def get_condition_summary(self, character_id: str) -> str:
        """Get a readable summary of active conditions."""
        conditions = self.get_active_conditions(character_id)
        if not conditions:
            return "No active conditions"

        summary = []
        for condition in conditions:
            desc = condition.condition_type.value.title()
            if condition.condition_type == ConditionType.EXHAUSTION:
                desc += f" (Level {condition.exhaustion_level})"
            if condition.duration_remaining > 0:
                desc += f" [{condition.duration_remaining} rounds]"
            summary.append(desc)

        return ", ".join(summary)


# Singleton instance
condition_manager = ConditionManager()