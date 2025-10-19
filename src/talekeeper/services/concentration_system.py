# core
# category: core
"""
Concentration System Service - Phase 4.2 Implementation
Handles concentration mechanics for D&D 2024

Key Features:
- Concentration tracking during combat
- Constitution saves when damaged
- Spell interruption mechanics
- Integration with combat system
"""

import sqlite3
import json
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

class ConcentrationSystem:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def start_concentration(self, character_id: str, spell_id: str, spell_level: int,
                           duration_rounds: Optional[int] = None) -> bool:
        """
        Start concentration on a spell for a character.

        Args:
            character_id: Character starting concentration
            spell_id: Spell being concentrated on
            spell_level: Level at which spell was cast
            duration_rounds: Duration in rounds (None for non-combat)

        Returns:
            bool: True if concentration started successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if character is already concentrating
                existing = self.get_concentration_spell(character_id)
                if existing:
                    # End previous concentration automatically
                    self.end_concentration(character_id)

                # Get spell info
                cursor.execute("""
                    SELECT name, concentration, duration
                    FROM spells
                    WHERE id = ?
                """, (spell_id,))

                spell_data = cursor.fetchone()
                if not spell_data:
                    self.logger.error(f"Spell {spell_id} not found")
                    return False

                name, requires_concentration, duration = spell_data

                if not requires_concentration:
                    self.logger.warning(f"Spell {name} does not require concentration")
                    return False

                # Calculate duration if not provided
                if duration_rounds is None:
                    duration_rounds = self._parse_spell_duration_to_rounds(duration)

                # Start concentration
                cursor.execute("""
                    INSERT OR REPLACE INTO character_concentration
                    (character_id, spell_id, spell_level, start_time, duration_remaining, concentration_dc)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (character_id, spell_id, spell_level,
                     datetime.now().isoformat(), duration_rounds, 10))

                conn.commit()

                self.logger.info(f"Character {character_id} started concentrating on {name}")
                return True

        except Exception as e:
            self.logger.error(f"Error starting concentration: {e}")
            return False

    def end_concentration(self, character_id: str, reason: str = "voluntary") -> bool:
        """
        End concentration for a character.

        Args:
            character_id: Character ending concentration
            reason: Reason for ending (voluntary, damage, incapacitated, etc.)

        Returns:
            bool: True if concentration ended successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get current concentration spell
                spell_info = self.get_concentration_spell(character_id)
                if not spell_info:
                    return False

                # Remove concentration
                cursor.execute("""
                    DELETE FROM character_concentration
                    WHERE character_id = ?
                """, (character_id,))

                conn.commit()

                self.logger.info(f"Character {character_id} ended concentration on {spell_info['spell_name']} ({reason})")
                return True

        except Exception as e:
            self.logger.error(f"Error ending concentration: {e}")
            return False

    def make_concentration_save(self, character_id: str, damage_taken: int,
                               constitution_modifier: int = 0) -> Tuple[bool, int, int]:
        """
        Make a concentration saving throw when taking damage.

        Args:
            character_id: Character making the save
            damage_taken: Amount of damage taken
            constitution_modifier: Character's Constitution modifier

        Returns:
            Tuple[bool, int, int]: (save_successful, dc, roll_result)
        """
        try:
            # Calculate concentration DC (minimum 10, or half damage taken)
            concentration_dc = max(10, math.floor(damage_taken / 2))

            # Roll d20 + Constitution modifier + proficiency (if proficient)
            import random
            d20_roll = random.randint(1, 20)

            # Check for proficiency in Constitution saves
            proficiency_bonus = self._get_concentration_save_proficiency(character_id)

            total_roll = d20_roll + constitution_modifier + proficiency_bonus

            save_successful = total_roll >= concentration_dc

            if not save_successful:
                # Concentration broken
                self.end_concentration(character_id, "failed concentration save")

            self.logger.info(f"Concentration save: {total_roll} vs DC {concentration_dc} = {'SUCCESS' if save_successful else 'FAILURE'}")

            return save_successful, concentration_dc, total_roll

        except Exception as e:
            self.logger.error(f"Error making concentration save: {e}")
            return False, 10, 0

    def _get_concentration_save_proficiency(self, character_id: str) -> int:
        """Get proficiency bonus for concentration saves."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if character has proficiency in Constitution saves
                cursor.execute("""
                    SELECT level, class_name FROM characters WHERE id = ?
                """, (character_id,))

                char_data = cursor.fetchone()
                if not char_data:
                    return 0

                level, class_name = char_data

                # Calculate proficiency bonus based on level
                proficiency_bonus = 2 + ((level - 1) // 4)

                # Check if class gives Constitution save proficiency
                constitution_save_classes = ['barbarian', 'fighter', 'ranger']
                if class_name.lower() in constitution_save_classes:
                    return proficiency_bonus

                # Check for specific feats or features that give proficiency
                cursor.execute("""
                    SELECT 1 FROM character_features
                    WHERE character_id = ?
                    AND (feature_name LIKE '%Constitution%' OR feature_name LIKE '%concentration%')
                """, (character_id,))

                if cursor.fetchone():
                    return proficiency_bonus

                return 0

        except Exception as e:
            self.logger.error(f"Error getting concentration save proficiency: {e}")
            return 0

    def get_concentration_spell(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the spell a character is currently concentrating on.

        Returns:
            Optional[Dict]: Concentration spell info or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT cc.spell_id, cc.spell_level, cc.start_time,
                           cc.duration_remaining, cc.concentration_dc,
                           s.name, s.duration, s.description
                    FROM character_concentration cc
                    JOIN spells s ON cc.spell_id = s.id
                    WHERE cc.character_id = ?
                """, (character_id,))

                result = cursor.fetchone()
                if not result:
                    return None

                return {
                    'spell_id': result[0],
                    'spell_level': result[1],
                    'start_time': result[2],
                    'duration_remaining': result[3],
                    'concentration_dc': result[4],
                    'spell_name': result[5],
                    'duration': result[6],
                    'description': result[7]
                }

        except Exception as e:
            self.logger.error(f"Error getting concentration spell: {e}")
            return None

    def update_concentration_duration(self, character_id: str, rounds_passed: int = 1) -> bool:
        """
        Update concentration duration during combat.

        Args:
            character_id: Character whose concentration to update
            rounds_passed: Number of rounds that have passed

        Returns:
            bool: True if concentration is still active
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get current concentration
                concentration = self.get_concentration_spell(character_id)
                if not concentration:
                    return False

                new_duration = concentration['duration_remaining'] - rounds_passed

                if new_duration <= 0:
                    # Concentration spell ends naturally
                    self.end_concentration(character_id, "spell duration expired")
                    return False
                else:
                    # Update remaining duration
                    cursor.execute("""
                        UPDATE character_concentration
                        SET duration_remaining = ?
                        WHERE character_id = ?
                    """, (new_duration, character_id))

                    conn.commit()
                    return True

        except Exception as e:
            self.logger.error(f"Error updating concentration duration: {e}")
            return False

    def _parse_spell_duration_to_rounds(self, duration: str) -> int:
        """Parse spell duration string to number of rounds."""
        duration_lower = duration.lower()

        if "concentration" in duration_lower:
            if "1 minute" in duration_lower:
                return 10  # 1 minute = 10 rounds
            elif "10 minutes" in duration_lower:
                return 100  # 10 minutes = 100 rounds
            elif "1 hour" in duration_lower:
                return 600  # 1 hour = 600 rounds
            elif "8 hours" in duration_lower:
                return 4800  # 8 hours = 4800 rounds
            elif "24 hours" in duration_lower:
                return 14400  # 24 hours = 14400 rounds

        # Default for unknown durations
        return 100

    def check_concentration_breaking_conditions(self, character_id: str) -> List[str]:
        """
        Check various conditions that could break concentration.

        Returns:
            List[str]: List of concentration-breaking conditions currently active
        """
        breaking_conditions = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if character is unconscious, incapacitated, etc.
                cursor.execute("""
                    SELECT condition_name FROM character_conditions
                    WHERE character_id = ?
                    AND condition_name IN ('unconscious', 'incapacitated', 'stunned')
                """, (character_id,))

                conditions = cursor.fetchall()
                for condition in conditions:
                    breaking_conditions.append(condition[0])

                # Check if character has 0 HP
                cursor.execute("""
                    SELECT current_hp FROM characters WHERE id = ?
                """, (character_id,))

                hp_result = cursor.fetchone()
                if hp_result and hp_result[0] <= 0:
                    breaking_conditions.append("0 hit points")

        except Exception as e:
            self.logger.error(f"Error checking concentration breaking conditions: {e}")

        return breaking_conditions

    def handle_concentration_breaking_conditions(self, character_id: str) -> bool:
        """
        Automatically end concentration if breaking conditions are met.

        Returns:
            bool: True if concentration was broken due to conditions
        """
        breaking_conditions = self.check_concentration_breaking_conditions(character_id)

        if breaking_conditions:
            reason = f"condition: {', '.join(breaking_conditions)}"
            self.end_concentration(character_id, reason)
            return True

        return False

    def get_all_concentrating_characters(self) -> List[Dict[str, Any]]:
        """Get all characters currently concentrating on spells."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT cc.character_id, c.name as character_name,
                           cc.spell_id, s.name as spell_name, cc.spell_level,
                           cc.start_time, cc.duration_remaining
                    FROM character_concentration cc
                    JOIN characters c ON cc.character_id = c.id
                    JOIN spells s ON cc.spell_id = s.id
                    ORDER BY cc.start_time
                """)

                concentrating_chars = []
                for row in cursor.fetchall():
                    concentrating_chars.append({
                        'character_id': row[0],
                        'character_name': row[1],
                        'spell_id': row[2],
                        'spell_name': row[3],
                        'spell_level': row[4],
                        'start_time': row[5],
                        'duration_remaining': row[6]
                    })

                return concentrating_chars

        except Exception as e:
            self.logger.error(f"Error getting concentrating characters: {e}")
            return []

def get_concentration_system(db_path: str = 'talekeeper.db') -> ConcentrationSystem:
    """Factory function to get concentration system instance."""
    return ConcentrationSystem(db_path)