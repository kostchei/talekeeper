# core
# category: core
"""
Spellcasting Service for TaleKeeper

Core spellcasting mechanics integrated with the action economy system.
Handles spell slot management, preparation, casting, and concentration.

Phase 1.3: Spellcasting Service Foundation
Implementation Plan Reference: Phase 1 > Step 1.3
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from talekeeper.services.spell_registry import spell_registry, SpellDefinition
from talekeeper.services.action_economy_enforcer import ActionExecutionResult
from talekeeper.models.action_economy import ActionEconomyType


class SpellcastingAbility(Enum):
    """Spellcasting ability scores for different classes."""
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class SpellSlotType(Enum):
    """Types of spell slots."""
    STANDARD = "standard"  # Normal spell slots
    PACT = "pact"         # Warlock pact magic slots


@dataclass
class SpellSlot:
    """Represents a spell slot."""
    level: int
    slot_type: SpellSlotType = SpellSlotType.STANDARD
    max_slots: int = 0
    used_slots: int = 0

    @property
    def available_slots(self) -> int:
        """Get number of available spell slots."""
        return max(0, self.max_slots - self.used_slots)

    def can_cast_spell(self, spell_level: int) -> bool:
        """Check if this slot can cast a spell of given level."""
        return self.level >= spell_level and self.available_slots > 0

    def use_slot(self) -> bool:
        """Use one spell slot. Returns True if successful."""
        if self.available_slots > 0:
            self.used_slots += 1
            return True
        return False

    def restore_slot(self, amount: int = 1) -> int:
        """Restore spell slots. Returns actual amount restored."""
        can_restore = min(amount, self.used_slots)
        self.used_slots -= can_restore
        return can_restore


@dataclass
class SpellcastingCharacter:
    """Represents a character's spellcasting capabilities."""
    character_id: str
    spellcasting_ability: SpellcastingAbility
    spell_attack_bonus: int
    spell_save_dc: int
    ritual_casting: bool = False
    spellcasting_focus: Optional[str] = None


class SpellcastingResult:
    """Result of a spellcasting attempt."""

    def __init__(self, success: bool, spell_id: str = "", reason: str = ""):
        self.success = success
        self.spell_id = spell_id
        self.reason = reason

        # Casting details
        self.spell_level_cast: Optional[int] = None
        self.slot_level_used: Optional[int] = None
        self.slot_type_used: Optional[SpellSlotType] = None
        self.concentration_started: bool = False
        self.concentration_ended: Optional[str] = None  # Previous concentration spell ended

        # Effects
        self.action_economy_used: List[str] = []
        self.resource_changes: Dict[str, int] = {}


class SpellcastingService:
    """Core spellcasting service."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._ensure_spellcasting_tables()

    def _ensure_spellcasting_tables(self):
        """Ensure spellcasting tables exist (should be created by migration)."""
        # Tables should exist from migration 011, but verify
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN (
                    'character_spell_slots', 'character_spells', 'character_spellcasting',
                    'character_concentration'
                )
            """)

            existing_tables = {row[0] for row in cursor.fetchall()}
            required_tables = {
                'character_spell_slots', 'character_spells',
                'character_spellcasting', 'character_concentration'
            }

            if not required_tables.issubset(existing_tables):
                missing = required_tables - existing_tables
                raise RuntimeError(f"Spellcasting tables missing: {missing}. Run migration 011.")

    def get_character_spellcasting(self, character_id: str) -> Optional[SpellcastingCharacter]:
        """Get a character's spellcasting information."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT spellcasting_ability, spell_attack_bonus, spell_save_dc,
                       ritual_casting, spellcasting_focus
                FROM character_spellcasting
                WHERE character_id = ? LIMIT 1
            """, (character_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return SpellcastingCharacter(
                character_id=character_id,
                spellcasting_ability=SpellcastingAbility(row['spellcasting_ability']),
                spell_attack_bonus=row['spell_attack_bonus'],
                spell_save_dc=row['spell_save_dc'],
                ritual_casting=bool(row['ritual_casting']),
                spellcasting_focus=row['spellcasting_focus']
            )

    def initialize_character_spellcasting(self, character_id: str, class_name: str) -> bool:
        """Initialize spellcasting for a character based on their class."""
        # Get character stats for calculations
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT level, intelligence, wisdom, charisma
                FROM characters
                WHERE id = ?
            """, (character_id,))

            char_row = cursor.fetchone()
            if not char_row:
                return False

            level = char_row['level']
            intelligence = char_row['intelligence'] or 10
            wisdom = char_row['wisdom'] or 10
            charisma = char_row['charisma'] or 10

            # Calculate proficiency bonus based on level
            prof_bonus = 2 + ((level - 1) // 4)

            # Determine spellcasting ability by class
            ability_map = {
                'wizard': SpellcastingAbility.INTELLIGENCE,
                'cleric': SpellcastingAbility.WISDOM,
                'paladin': SpellcastingAbility.CHARISMA,
                'warlock': SpellcastingAbility.CHARISMA
            }

            spellcasting_ability = ability_map.get(class_name.lower())
            if not spellcasting_ability:
                return False  # Not a spellcasting class

            # Get ability modifier
            ability_scores = {
                SpellcastingAbility.INTELLIGENCE: intelligence,
                SpellcastingAbility.WISDOM: wisdom,
                SpellcastingAbility.CHARISMA: charisma
            }

            ability_score = ability_scores[spellcasting_ability]
            ability_mod = (ability_score - 10) // 2

            # Calculate spell attack bonus and save DC
            spell_attack_bonus = prof_bonus + ability_mod
            spell_save_dc = 8 + prof_bonus + ability_mod

            # Determine ritual casting ability
            ritual_casting = class_name.lower() in ['wizard', 'cleric']

            table_columns = self._get_spellcasting_table_columns(cursor)

            if 'spellcasting_class' in table_columns:
                cursor.execute("""
                    INSERT OR REPLACE INTO character_spellcasting
                    (character_id, spellcasting_class, spellcasting_ability, spell_attack_bonus, spell_save_dc,
                     ritual_casting, spellcasting_focus, cantrips_known)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    character_id, class_name, spellcasting_ability.value, spell_attack_bonus,
                    spell_save_dc, ritual_casting, 'component_pouch'
                ))
            else:
                # Legacy schema used by older tools/tests (no spellcasting_class column)
                cursor.execute("""
                    INSERT OR REPLACE INTO character_spellcasting
                    (character_id, spellcasting_ability, spell_attack_bonus, spell_save_dc,
                     ritual_casting, spellcasting_focus)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    character_id, spellcasting_ability.value, spell_attack_bonus,
                    spell_save_dc, ritual_casting, 'component_pouch'
                ))

            # Initialize spell slots based on class and level
            self._initialize_spell_slots(cursor, character_id, class_name, level)

            conn.commit()
            return True

    def _initialize_spell_slots(self, cursor, character_id: str, class_name: str, level: int):
        """Initialize spell slots for a character."""
        # Full caster spell slot progression (Wizard, Cleric)
        full_caster_slots = {
            1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
            2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
            3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
            4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
            5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
            6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
            7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
            8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
            9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
            10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
            11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
            18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
            19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
            20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
        }

        # Half caster spell slot progression (Paladin) - D&D 2024
        half_caster_slots = {
            1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
            2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
            3: [3, 0, 0, 0, 0, 0, 0, 0, 0],
            4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
            5: [4, 2, 0, 0, 0, 0, 0, 0, 0],
            6: [4, 2, 0, 0, 0, 0, 0, 0, 0],
            7: [4, 3, 0, 0, 0, 0, 0, 0, 0],
            8: [4, 3, 0, 0, 0, 0, 0, 0, 0],
            9: [4, 3, 2, 0, 0, 0, 0, 0, 0],
            10: [4, 3, 2, 0, 0, 0, 0, 0, 0],
            11: [4, 3, 3, 0, 0, 0, 0, 0, 0],
            12: [4, 3, 3, 0, 0, 0, 0, 0, 0],
            13: [4, 3, 3, 1, 0, 0, 0, 0, 0],
            14: [4, 3, 3, 1, 0, 0, 0, 0, 0],
            15: [4, 3, 3, 2, 0, 0, 0, 0, 0],
            16: [4, 3, 3, 2, 0, 0, 0, 0, 0],
            17: [4, 3, 3, 3, 1, 0, 0, 0, 0],
            18: [4, 3, 3, 3, 1, 0, 0, 0, 0],
            19: [4, 3, 3, 3, 2, 0, 0, 0, 0],
            20: [4, 3, 3, 3, 2, 0, 0, 0, 0]
        }

        # Warlock pact magic slots (separate system)
        warlock_pact_slots = {
            1: 1, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2,
            11: 3, 12: 3, 13: 3, 14: 3, 15: 3, 16: 3, 17: 4, 18: 4, 19: 4, 20: 4
        }

        warlock_slot_level = {
            1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5,
            11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5, 18: 5, 19: 5, 20: 5
        }

        # Clear existing slots
        cursor.execute("DELETE FROM character_spell_slots WHERE character_id = ?", (character_id,))

        # Set up slots based on class
        if class_name.lower() in ['wizard', 'cleric']:
            # Full caster
            slots = full_caster_slots.get(level, [0] * 9)
            for spell_level, max_slots in enumerate(slots, 1):
                if max_slots > 0:
                    cursor.execute("""
                        INSERT INTO character_spell_slots
                        (character_id, spell_level, max_slots, used_slots, slot_type)
                        VALUES (?, ?, ?, 0, 'standard')
                    """, (character_id, spell_level, max_slots))

        elif class_name.lower() == 'paladin':
            # Half caster
            slots = half_caster_slots.get(level, [0] * 9)
            for spell_level, max_slots in enumerate(slots, 1):
                if max_slots > 0:
                    cursor.execute("""
                        INSERT INTO character_spell_slots
                        (character_id, spell_level, max_slots, used_slots, slot_type)
                        VALUES (?, ?, ?, 0, 'standard')
                    """, (character_id, spell_level, max_slots))

        elif class_name.lower() == 'warlock':
            # Pact magic
            pact_slots = warlock_pact_slots.get(level, 1)
            slot_level = warlock_slot_level.get(level, 1)

            cursor.execute("""
                INSERT INTO character_spell_slots
                (character_id, spell_level, max_slots, used_slots, slot_type)
                VALUES (?, ?, ?, 0, 'pact')
            """, (character_id, slot_level, pact_slots))

    def get_character_spell_slots(self, character_id: str, attempt_repair: bool = True) -> List[SpellSlot]:
        """Get all spell slots for a character."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT spell_level, max_slots, used_slots, slot_type
                FROM character_spell_slots
                WHERE character_id = ?
                ORDER BY spell_level
            """, (character_id,))

            slots = []
            rows = cursor.fetchall()

        slots = []
        for row in rows:
                slot = SpellSlot(
                    level=row['spell_level'],
                    slot_type=SpellSlotType(row['slot_type']),
                    max_slots=row['max_slots'],
                    used_slots=row['used_slots']
                )
                slots.append(slot)

        if slots or not attempt_repair:
            return slots

        class_name = self._get_character_class_id(character_id)
        if class_name and class_name.lower() in ['wizard', 'cleric', 'paladin', 'warlock']:
            try:
                print(f"[SpellcastingService] Detected missing spell slots for {character_id} ({class_name}); rebuilding.")
                self.initialize_character_spellcasting(character_id, class_name)
                return self.get_character_spell_slots(character_id, attempt_repair=False)
            except Exception as exc:
                print(f"[SpellcastingService] Failed to rebuild spell slots for {character_id}: {exc}")

        return slots

    def _get_character_class_id(self, character_id: str) -> Optional[str]:
        """Fetch the stored class id for a character."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT class_id FROM characters WHERE id = ? LIMIT 1",
                    (character_id,)
                )
                row = cursor.fetchone()
                if row and row[0]:
                    return row[0]
        except Exception as exc:
            print(f"[SpellcastingService] Could not load class for {character_id}: {exc}")
        return None

    def _get_spellcasting_table_columns(self, cursor) -> set[str]:
        """Cache the column list for character_spellcasting to support legacy schemas."""
        cached = getattr(self, '_spellcasting_table_columns', None)
        if cached is not None:
            return cached

        cursor.execute("PRAGMA table_info(character_spellcasting)")
        columns = {row[1] for row in cursor.fetchall()}
        self._spellcasting_table_columns = columns
        return columns

    def can_cast_spell(self, character_id: str, spell_id: str,
                       spell_level: Optional[int] = None) -> Tuple[bool, str]:
        """
        Check if a character can cast a specific spell.

        Args:
            character_id: Character casting the spell
            spell_id: Spell to cast
            spell_level: Level to cast at (for upcasting)

        Returns:
            Tuple of (can_cast, reason)
        """
        # Get spell definition
        spell = spell_registry.get_spell(spell_id)
        if not spell:
            return False, f"Spell '{spell_id}' not found"

        # Check if character knows/has this spell prepared
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT is_prepared FROM character_spells
                WHERE character_id = ? AND spell_id = ?
            """, (character_id, spell_id))

            row = cursor.fetchone()
            if not row:
                return False, "Spell not known"

            if not row[0]:
                return False, "Spell not prepared"

        # Determine casting level
        cast_level = spell_level if spell_level is not None else spell.level
        if cast_level < spell.level:
            return False, f"Cannot cast {spell.name} at level {cast_level}"

        # Check for available spell slots (cantrips don't need slots)
        if cast_level > 0:
            slots = self.get_character_spell_slots(character_id)
            available_slots = [s for s in slots if s.can_cast_spell(cast_level)]

            if not available_slots:
                return False, f"No spell slots available for level {cast_level}"

        return True, ""

    def cast_spell(self, character_id: str, spell_id: str,
                   spell_level: Optional[int] = None,
                   action_economy_type: Optional[ActionEconomyType] = None) -> SpellcastingResult:
        """
        Cast a spell, consuming appropriate resources.

        Args:
            character_id: Character casting the spell
            spell_id: Spell to cast
            spell_level: Level to cast at (for upcasting)
            action_economy_type: Action economy cost override

        Returns:
            SpellcastingResult
        """
        result = SpellcastingResult(False, spell_id)

        # Get spell definition
        spell = spell_registry.get_spell(spell_id)
        if not spell:
            result.reason = f"Spell '{spell_id}' not found"
            return result

        # Check if can cast
        can_cast, reason = self.can_cast_spell(character_id, spell_id, spell_level)
        if not can_cast:
            result.reason = reason
            return result

        cast_level = spell_level if spell_level is not None else spell.level

        # Find and use appropriate spell slot (cantrips don't need slots)
        slot_to_use = None
        if cast_level > 0:
            slots = self.get_character_spell_slots(character_id)

            # Find the lowest level slot that can cast this spell
            for slot in sorted(slots, key=lambda s: s.level):
                if slot.can_cast_spell(cast_level):
                    slot_to_use = slot
                    break

            if not slot_to_use:
                result.reason = f"No spell slots available for level {cast_level}"
                return result

        # Use the spell slot (if not a cantrip)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if slot_to_use:
                # Update used slots in database
                cursor.execute("""
                    UPDATE character_spell_slots
                    SET used_slots = used_slots + 1
                    WHERE character_id = ? AND spell_level = ? AND slot_type = ?
                """, (character_id, slot_to_use.level, slot_to_use.slot_type.value))

            # Handle concentration
            if spell.concentration:
                # End any existing concentration
                cursor.execute("""
                    SELECT spell_id FROM character_concentration
                    WHERE character_id = ?
                """, (character_id,))

                old_concentration = cursor.fetchone()
                if old_concentration:
                    result.concentration_ended = old_concentration[0]
                    cursor.execute("""
                        DELETE FROM character_concentration
                        WHERE character_id = ?
                    """, (character_id,))

                # Start new concentration
                duration_rounds = self._parse_duration_to_rounds(spell.duration)
                cursor.execute("""
                    INSERT INTO character_concentration
                    (character_id, spell_id, spell_level, duration_remaining)
                    VALUES (?, ?, ?, ?)
                """, (character_id, spell_id, cast_level, duration_rounds))

                result.concentration_started = True

            conn.commit()

        # Set result details
        result.success = True
        result.spell_level_cast = cast_level
        if slot_to_use:
            result.slot_level_used = slot_to_use.level
            result.slot_type_used = slot_to_use.slot_type
            result.resource_changes[f"spell_slot_level_{slot_to_use.level}"] = -1

        # Determine action economy used
        if action_economy_type:
            result.action_economy_used.append(action_economy_type.value)
        else:
            # Infer from casting time
            if "bonus action" in spell.casting_time.lower():
                result.action_economy_used.append(ActionEconomyType.BONUS_ACTION.value)
            elif "reaction" in spell.casting_time.lower():
                result.action_economy_used.append(ActionEconomyType.REACTION.value)
            else:
                result.action_economy_used.append(ActionEconomyType.ACTION.value)

        return result

    def _parse_duration_to_rounds(self, duration: str) -> int:
        """Parse spell duration to combat rounds."""
        duration_lower = duration.lower()

        if "instantaneous" in duration_lower:
            return 0
        elif "1 round" in duration_lower:
            return 1
        elif "1 minute" in duration_lower:
            return 10  # 10 rounds = 1 minute
        elif "10 minutes" in duration_lower:
            return 100
        elif "1 hour" in duration_lower:
            return 600
        else:
            return 10  # Default to 1 minute

    def end_concentration(self, character_id: str) -> Optional[str]:
        """End concentration for a character. Returns the spell that was ended."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT spell_id FROM character_concentration
                WHERE character_id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if not row:
                return None

            spell_id = row[0]

            cursor.execute("""
                DELETE FROM character_concentration
                WHERE character_id = ?
            """, (character_id,))

            conn.commit()
            return spell_id

    def get_concentration_spell(self, character_id: str) -> Optional[Tuple[str, int]]:
        """Get the spell the character is concentrating on. Returns (spell_id, spell_level)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT spell_id, spell_level FROM character_concentration
                WHERE character_id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if row:
                return row[0], row[1]
            return None

    def restore_spell_slots(self, character_id: str, rest_type: str = "long") -> Dict[int, int]:
        """
        Restore spell slots on rest.

        Args:
            character_id: Character resting
            rest_type: "short" or "long"

        Returns:
            Dict of {spell_level: slots_restored}
        """
        restored = {}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if rest_type == "long":
                # Restore all spell slots
                cursor.execute("""
                    UPDATE character_spell_slots
                    SET used_slots = 0
                    WHERE character_id = ?
                """, (character_id,))

                cursor.execute("""
                    SELECT spell_level, max_slots FROM character_spell_slots
                    WHERE character_id = ?
                """, (character_id,))

                for spell_level, max_slots in cursor.fetchall():
                    restored[spell_level] = max_slots

            elif rest_type == "short":
                # Restore pact magic slots (Warlock)
                cursor.execute("""
                    UPDATE character_spell_slots
                    SET used_slots = 0
                    WHERE character_id = ? AND slot_type = 'pact'
                """, (character_id,))

                cursor.execute("""
                    SELECT spell_level, max_slots FROM character_spell_slots
                    WHERE character_id = ? AND slot_type = 'pact'
                """, (character_id,))

                for spell_level, max_slots in cursor.fetchall():
                    restored[spell_level] = max_slots

            conn.commit()

        return restored


# Singleton instance - will be initialized when first accessed
spellcasting_service = None

def get_spellcasting_service(db_path: str = "talekeeper.db") -> SpellcastingService:
    """Get the spellcasting service singleton."""
    global spellcasting_service
    if spellcasting_service is None or spellcasting_service.db_path != db_path:
        spellcasting_service = SpellcastingService(db_path)
    return spellcasting_service
