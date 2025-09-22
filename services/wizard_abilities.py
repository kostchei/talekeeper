"""
Wizard Abilities Service

Handles Wizard-specific abilities including spellbook management, Arcane Recovery,
arcane traditions, and Intelligence-based spellcasting.

Phase 2.2: Wizard Base Class Implementation
Implementation Plan Reference: Phase 2 > Phase 2.2
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from services.spellcasting_service import get_spellcasting_service, SpellcastingAbility
from services.spell_registry import spell_registry


class WizardAbilitiesService:
    """Service for Wizard abilities and features."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.spellcasting_service = get_spellcasting_service(db_path)

    def initialize_wizard_character(self, character_id: str, tradition: str = "evocation") -> Dict[str, Any]:
        """
        Initialize a character as a Wizard with the specified arcane tradition.

        Args:
            character_id: Character to initialize
            tradition: Arcane tradition (default: 'evocation')

        Returns:
            Dict with initialization results
        """
        result = {"success": False, "features_added": [], "spells_added": []}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get character info
                cursor.execute("SELECT level, intelligence FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                if not char_row:
                    result["reason"] = "Character not found"
                    return result

                level = char_row['level']
                intelligence_score = char_row['intelligence']
                int_modifier = (intelligence_score - 10) // 2

                # Initialize spellcasting
                spellcasting_init = self.spellcasting_service.initialize_character_spellcasting(
                    character_id, 'wizard'
                )
                if not spellcasting_init:
                    result["reason"] = "Failed to initialize spellcasting"
                    return result

                # Calculate max prepared spells
                max_prepared = max(1, int_modifier + level)

                # Initialize wizard features
                cursor.execute("""
                    INSERT OR REPLACE INTO wizard_features
                    (character_id, level, arcane_tradition, arcane_recovery_used,
                     arcane_recovery_last_reset, spells_prepared, max_spells_prepared)
                    VALUES (?, ?, ?, 0, datetime('now'), 0, ?)
                """, (character_id, level, tradition, max_prepared))

                # Add starting spells to spellbook (6 1st-level spells at level 1)
                starting_spells = self._add_starting_spells(cursor, character_id, level)
                result["spells_added"] = starting_spells

                # Apply arcane tradition features
                tradition_features = self._apply_tradition_features(cursor, character_id, tradition, level)
                result["features_added"] = tradition_features

                # Initialize Arcane Recovery
                self._initialize_arcane_recovery(cursor, character_id, level)

                conn.commit()
                result["success"] = True
                result["tradition"] = tradition
                result["max_prepared_spells"] = max_prepared

        except Exception as e:
            result["reason"] = f"Initialization failed: {str(e)}"

        return result

    def _add_starting_spells(self, cursor, character_id: str, level: int) -> List[str]:
        """Add starting spells to wizard's spellbook."""
        # Wizards start with 6 1st-level spells in their spellbook
        starting_wizard_spells = [
            'magic_missile', 'shield', 'mage_armor', 'detect_magic',
            'comprehend_languages', 'burning_hands'
        ]

        spells_added = []
        for spell_id in starting_wizard_spells:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO wizard_spellbook
                    (character_id, spell_id, spell_level, learned_at_level, source, notes)
                    VALUES (?, ?, 1, ?, 'starting', 'Starting wizard spell')
                """, (character_id, spell_id, level))

                # Also add to character_spells for preparation
                cursor.execute("""
                    INSERT OR IGNORE INTO character_spells
                    (character_id, spell_id, spell_level, is_prepared, source, source_level)
                    VALUES (?, ?, 1, 0, 'wizard_spellbook', ?)
                """, (character_id, spell_id, level))

                spells_added.append(spell_id)
            except Exception:
                pass  # Spell might not exist in database yet

        return spells_added

    def _apply_tradition_features(self, cursor, character_id: str, tradition: str, level: int) -> List[str]:
        """Apply arcane tradition features based on character level."""
        features_added = []

        # Level 2: Arcane Tradition feature
        if level >= 2:
            if tradition == "evocation":
                # Sculpt Spells feature
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'sculpt_spells', 'wizard_evocation', 2, 0, 0)
                """, (character_id,))
                features_added.append("Sculpt Spells")

        # Level 6: Tradition feature
        if level >= 6:
            if tradition == "evocation":
                # Potent Cantrip
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'potent_cantrip', 'wizard_evocation', 6, 0, 0)
                """, (character_id,))
                features_added.append("Potent Cantrip")

        # Level 10: Tradition feature
        if level >= 10:
            if tradition == "evocation":
                # Empowered Evocation
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'empowered_evocation', 'wizard_evocation', 10, 0, 0)
                """, (character_id,))
                features_added.append("Empowered Evocation")

        # Level 14: Tradition feature
        if level >= 14:
            if tradition == "evocation":
                # Overchannel
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'overchannel', 'wizard_evocation', 14, 0, 1)
                """, (character_id,))
                features_added.append("Overchannel")

        return features_added

    def _initialize_arcane_recovery(self, cursor, character_id: str, level: int):
        """Initialize Arcane Recovery feature."""
        cursor.execute("""
            INSERT OR IGNORE INTO character_features
            (character_id, feature_id, source, source_level, uses_current, uses_max)
            VALUES (?, 'arcane_recovery', 'wizard', 1, 0, 1)
        """, (character_id,))

    def use_arcane_recovery(self, character_id: str) -> Dict[str, Any]:
        """
        Use Arcane Recovery to regain spell slots.

        Arcane Recovery: Once per day when you finish a short rest, you can choose
        expended spell slots to recover. The spell slots can have a combined level
        that is equal to or less than half your wizard level (rounded up), and none
        of the slots can be 6th level or higher.

        Args:
            character_id: Character using Arcane Recovery

        Returns:
            Dict with recovery information
        """
        result = {"success": False, "slots_recovered": {}}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Check if already used
                cursor.execute("""
                    SELECT arcane_recovery_used FROM wizard_features
                    WHERE character_id = ?
                """, (character_id,))

                wizard_row = cursor.fetchone()
                if not wizard_row:
                    result["reason"] = "Not a wizard"
                    return result

                if wizard_row['arcane_recovery_used']:
                    result["reason"] = "Arcane Recovery already used today"
                    return result

                # Get character level
                cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                level = char_row['level']

                # Calculate recovery limit
                recovery_limit = (level + 1) // 2

                # Get current spell slots
                cursor.execute("""
                    SELECT spell_slots_1_current, spell_slots_1_max,
                           spell_slots_2_current, spell_slots_2_max,
                           spell_slots_3_current, spell_slots_3_max,
                           spell_slots_4_current, spell_slots_4_max,
                           spell_slots_5_current, spell_slots_5_max
                    FROM wizard_features WHERE character_id = ?
                """, (character_id,))

                slots_row = cursor.fetchone()

                # Simple recovery strategy: recover lowest level slots first
                slots_to_recover = {}
                remaining_recovery = recovery_limit

                for slot_level in range(1, 6):  # 1-5th level slots only
                    current_col = f'spell_slots_{slot_level}_current'
                    max_col = f'spell_slots_{slot_level}_max'

                    if slots_row[current_col] < slots_row[max_col] and remaining_recovery >= slot_level:
                        # Can recover some slots of this level
                        slots_used = slots_row[max_col] - slots_row[current_col]
                        recovery_possible = min(slots_used, remaining_recovery // slot_level)

                        if recovery_possible > 0:
                            slots_to_recover[slot_level] = recovery_possible
                            remaining_recovery -= recovery_possible * slot_level

                # Apply recovery
                for slot_level, count in slots_to_recover.items():
                    current_col = f'spell_slots_{slot_level}_current'
                    cursor.execute(f"""
                        UPDATE wizard_features
                        SET {current_col} = {current_col} + ?
                        WHERE character_id = ?
                    """, (count, character_id))

                # Mark as used
                cursor.execute("""
                    UPDATE wizard_features
                    SET arcane_recovery_used = 1,
                        arcane_recovery_last_reset = datetime('now')
                    WHERE character_id = ?
                """, (character_id,))

                conn.commit()
                result["success"] = True
                result["slots_recovered"] = slots_to_recover
                result["recovery_limit"] = recovery_limit

        except Exception as e:
            result["reason"] = f"Recovery failed: {str(e)}"

        return result

    def long_rest_recovery(self, character_id: str) -> Dict[str, Any]:
        """Handle long rest recovery for wizards."""
        result = {"success": False}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Reset Arcane Recovery
                cursor.execute("""
                    UPDATE wizard_features
                    SET arcane_recovery_used = 0,
                        arcane_recovery_last_reset = datetime('now')
                    WHERE character_id = ?
                """, (character_id,))

                # Let spellcasting service handle spell slot recovery
                spell_recovery = self.spellcasting_service.long_rest_recovery(character_id)

                conn.commit()
                result["success"] = True
                result["arcane_recovery_reset"] = True
                result["spell_recovery"] = spell_recovery

        except Exception as e:
            result["reason"] = f"Recovery failed: {str(e)}"

        return result

    def add_spell_to_spellbook(self, character_id: str, spell_id: str,
                              source: str = "level_up", cost: int = 0) -> Dict[str, Any]:
        """
        Add a spell to the wizard's spellbook.

        Args:
            character_id: Character learning the spell
            spell_id: Spell to learn
            source: How the spell was learned ('level_up', 'copied', 'found')
            cost: Gold cost if copied

        Returns:
            Dict with learning results
        """
        result = {"success": False}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get spell info
                spell = spell_registry.get_spell(spell_id)
                if not spell:
                    result["reason"] = "Spell not found"
                    return result

                # Get character level
                cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                level = char_row['level']

                # Add to spellbook
                cursor.execute("""
                    INSERT OR REPLACE INTO wizard_spellbook
                    (character_id, spell_id, spell_level, learned_at_level,
                     source, cost_paid, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, spell_id, spell.level, level, source, cost,
                     f"Learned at level {level} via {source}"))

                # Add to character_spells (unprepared by default)
                cursor.execute("""
                    INSERT OR IGNORE INTO character_spells
                    (character_id, spell_id, spell_level, is_prepared,
                     source, source_level)
                    VALUES (?, ?, ?, 0, 'wizard_spellbook', ?)
                """, (character_id, spell_id, spell.level, level))

                conn.commit()
                result["success"] = True
                result["spell_name"] = spell.name
                result["spell_level"] = spell.level

        except Exception as e:
            result["reason"] = f"Failed to add spell: {str(e)}"

        return result

    def get_wizard_info(self, character_id: str) -> Dict[str, Any]:
        """Get comprehensive wizard information."""
        result = {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get wizard features
                cursor.execute("""
                    SELECT * FROM wizard_features WHERE character_id = ?
                """, (character_id,))
                wizard_row = cursor.fetchone()

                if wizard_row:
                    result["wizard_features"] = dict(wizard_row)

                    # Get spellbook
                    cursor.execute("""
                        SELECT ws.*, s.name, s.school
                        FROM wizard_spellbook ws
                        JOIN spells s ON ws.spell_id = s.id
                        WHERE ws.character_id = ?
                        ORDER BY ws.spell_level, s.name
                    """, (character_id,))

                    result["spellbook"] = [dict(row) for row in cursor.fetchall()]

                    # Get prepared spells
                    cursor.execute("""
                        SELECT cs.*, s.name, s.school
                        FROM character_spells cs
                        JOIN spells s ON cs.spell_id = s.id
                        WHERE cs.character_id = ? AND cs.is_prepared = 1
                        ORDER BY cs.spell_level, s.name
                    """, (character_id,))

                    result["prepared_spells"] = [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            result["error"] = str(e)

        return result


# Global instance
_wizard_service = None

def get_wizard_service(db_path: str = "talekeeper.db") -> WizardAbilitiesService:
    """Get singleton wizard service instance."""
    global _wizard_service
    if _wizard_service is None:
        _wizard_service = WizardAbilitiesService(db_path)
    return _wizard_service