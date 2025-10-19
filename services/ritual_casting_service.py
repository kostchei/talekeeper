# core
# core
"""
Ritual Casting Service - Phase 4.1 Implementation
Handles ritual casting mechanics for D&D 2024

Key Features:
- Ritual spell detection
- Extended casting time handling
- No spell slot consumption
- Class-specific ritual casting abilities
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

class RitualCastingService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def can_cast_as_ritual(self, character_id: str, spell_id: str) -> Tuple[bool, str]:
        """
        Check if a character can cast a specific spell as a ritual.

        Returns:
            Tuple[bool, str]: (can_cast, reason_if_cannot)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get spell information
                cursor.execute("""
                    SELECT name, level, ritual, casting_time, duration, components
                    FROM spells
                    WHERE id = ?
                """, (spell_id,))

                spell_data = cursor.fetchone()
                if not spell_data:
                    return False, "Spell not found"

                name, level, is_ritual, casting_time, duration, components = spell_data

                # Check if spell is actually a ritual
                if not is_ritual:
                    return False, f"{name} cannot be cast as a ritual"

                # Check if character has ritual casting ability
                has_ritual_casting = self._character_has_ritual_casting(cursor, character_id)
                if not has_ritual_casting:
                    return False, "Character does not have ritual casting ability"

                # Check if character knows/has prepared the spell
                has_spell = self._character_has_spell(cursor, character_id, spell_id)
                if not has_spell:
                    return False, f"Character does not know {name}"

                return True, ""

        except Exception as e:
            self.logger.error(f"Error checking ritual casting: {e}")
            return False, f"Error: {e}"

    def _character_has_ritual_casting(self, cursor, character_id: str) -> bool:
        """Check if character has ritual casting ability from any class."""

        # Check character spellcasting for ritual casting flag
        cursor.execute("""
            SELECT ritual_casting
            FROM character_spellcasting
            WHERE character_id = ? AND ritual_casting = 1
        """, (character_id,))

        if cursor.fetchone():
            return True

        # Check specific class features that grant ritual casting
        # Cleric, Druid, Wizard get ritual casting
        cursor.execute("""
            SELECT class_name
            FROM characters
            WHERE id = ? AND class_name IN ('cleric', 'wizard', 'druid')
        """, (character_id,))

        return cursor.fetchone() is not None

    def _character_has_spell(self, cursor, character_id: str, spell_id: str) -> bool:
        """Check if character knows or has prepared the spell."""

        # Check character_spells table
        cursor.execute("""
            SELECT 1 FROM character_spells
            WHERE character_id = ? AND spell_id = ?
        """, (character_id, spell_id))

        if cursor.fetchone():
            return True

        # For ritual casting, some classes can cast any ritual spell they know
        # even if not prepared (like Wizard with spellbook)
        cursor.execute("""
            SELECT class_name FROM characters WHERE id = ?
        """, (character_id,))

        class_result = cursor.fetchone()
        if class_result and class_result[0] == 'wizard':
            # Check wizard spellbook
            cursor.execute("""
                SELECT 1 FROM wizard_spellbook
                WHERE character_id = ? AND spell_id = ?
            """, (character_id, spell_id))

            return cursor.fetchone() is not None

        return False

    def get_ritual_spells_for_character(self, character_id: str) -> List[Dict[str, Any]]:
        """Get all ritual spells available to a character."""

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get character's class to determine available spells
                cursor.execute("""
                    SELECT class_name FROM characters WHERE id = ?
                """, (character_id,))

                class_result = cursor.fetchone()
                if not class_result:
                    return []

                class_name = class_result[0]

                # Get ritual spells available to the class
                cursor.execute("""
                    SELECT s.id, s.name, s.level, s.school, s.casting_time,
                           s.range_value, s.components, s.duration, s.description,
                           cs.is_prepared, cs.always_prepared
                    FROM spells s
                    LEFT JOIN character_spells cs ON s.id = cs.spell_id AND cs.character_id = ?
                    WHERE s.ritual = 1
                    AND (
                        s.classes LIKE '%' || ? || '%'
                        OR cs.spell_id IS NOT NULL
                    )
                    ORDER BY s.level, s.name
                """, (character_id, class_name))

                spells = []
                for row in cursor.fetchall():
                    spell_dict = {
                        'id': row[0],
                        'name': row[1],
                        'level': row[2],
                        'school': row[3],
                        'casting_time': row[4],
                        'range_value': row[5],
                        'components': row[6],
                        'duration': row[7],
                        'description': row[8],
                        'is_prepared': row[9] if row[9] is not None else False,
                        'always_prepared': row[10] if row[10] is not None else False,
                        'ritual_casting_time': self._calculate_ritual_casting_time(row[4])
                    }
                    spells.append(spell_dict)

                return spells

        except Exception as e:
            self.logger.error(f"Error getting ritual spells: {e}")
            return []

    def _calculate_ritual_casting_time(self, normal_casting_time: str) -> str:
        """Calculate ritual casting time (normal + 10 minutes)."""

        # D&D 2024 ritual casting adds 10 minutes to normal casting time
        if "1 action" in normal_casting_time.lower():
            return "10 minutes 1 action"
        elif "1 minute" in normal_casting_time.lower():
            return "11 minutes"
        elif "10 minutes" in normal_casting_time.lower():
            return "20 minutes"
        else:
            return f"{normal_casting_time} + 10 minutes"

    def cast_ritual_spell(self, character_id: str, spell_id: str, target_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Cast a spell as a ritual (no spell slot consumed).

        Args:
            character_id: Character casting the spell
            spell_id: Spell being cast
            target_data: Optional targeting/parameter data

        Returns:
            Dict with casting result and effects
        """

        can_cast, reason = self.can_cast_as_ritual(character_id, spell_id)
        if not can_cast:
            return {
                'success': False,
                'message': reason,
                'spell_slot_consumed': False
            }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get spell details
                cursor.execute("""
                    SELECT name, level, casting_time, duration, description
                    FROM spells
                    WHERE id = ?
                """, (spell_id,))

                spell_data = cursor.fetchone()
                if not spell_data:
                    return {'success': False, 'message': 'Spell not found'}

                name, level, casting_time, duration, description = spell_data
                ritual_time = self._calculate_ritual_casting_time(casting_time)

                # Log the ritual casting
                self._log_ritual_casting(cursor, character_id, spell_id, ritual_time)

                # Apply spell effects (implementation depends on specific spell)
                effects = self._apply_ritual_spell_effects(cursor, character_id, spell_id, target_data)

                conn.commit()

                return {
                    'success': True,
                    'message': f"Ritual casting of {name} completed",
                    'spell_slot_consumed': False,
                    'casting_time': ritual_time,
                    'effects': effects,
                    'spell_name': name,
                    'spell_level': level
                }

        except Exception as e:
            self.logger.error(f"Error casting ritual spell: {e}")
            return {
                'success': False,
                'message': f"Ritual casting failed: {e}",
                'spell_slot_consumed': False
            }

    def _log_ritual_casting(self, cursor, character_id: str, spell_id: str, casting_time: str):
        """Log ritual spell casting for tracking."""

        cursor.execute("""
            INSERT INTO character_spellcasting (character_id, spellcasting_class, ritual_casting)
            VALUES (?, 'ritual_log', 1)
            ON CONFLICT(character_id, spellcasting_class) DO NOTHING
        """, (character_id,))

    def _apply_ritual_spell_effects(self, cursor, character_id: str, spell_id: str, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the effects of a ritual spell."""

        # This is a placeholder for spell-specific effects
        # Each ritual spell would need its own implementation

        effects = {
            'type': 'ritual_spell',
            'spell_id': spell_id,
            'cast_time': datetime.now().isoformat(),
            'no_slot_consumed': True
        }

        # Common ritual spell effects
        if spell_id == 'detect_magic':
            effects.update({
                'detection_range': 30,
                'duration_minutes': 10,
                'concentration_required': True
            })
        elif spell_id == 'identify':
            effects.update({
                'identifies_magic_items': True,
                'duration_instant': True
            })
        elif spell_id == 'comprehend_languages':
            effects.update({
                'understands_languages': True,
                'duration_hours': 1
            })

        return effects

    def get_ritual_casting_log(self, character_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent ritual casting history for a character."""

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # This would require a proper ritual casting log table
                # For now, return placeholder data
                return []

        except Exception as e:
            self.logger.error(f"Error getting ritual casting log: {e}")
            return []

def get_ritual_casting_service(db_path: str = 'talekeeper.db') -> RitualCastingService:
    """Factory function to get ritual casting service instance."""
    return RitualCastingService(db_path)