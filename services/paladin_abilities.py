# core
# core
"""
Paladin Abilities Service

Handles Paladin-specific abilities including Divine Smite, Lay on Hands,
sacred oaths, and Charisma-based half-caster spellcasting.

Phase 2.3: Paladin Base Class Implementation
Implementation Plan Reference: Phase 2 > Phase 2.3
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from services.spellcasting_service import get_spellcasting_service, SpellcastingAbility
from services.spell_registry import spell_registry


class PaladinAbilitiesService:
    """Service for Paladin abilities and features."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.spellcasting_service = None
        try:
            self.spellcasting_service = get_spellcasting_service(db_path)
        except Exception:
            # Spellcasting service not available - paladin will work without it
            pass

    def initialize_paladin_character(self, character_id: str, oath: str = "devotion") -> Dict[str, Any]:
        """
        Initialize a character as a Paladin with the specified sacred oath.

        Args:
            character_id: Character to initialize
            oath: Sacred oath (default: 'devotion')

        Returns:
            Dict with initialization results
        """
        result = {"success": False, "features_added": [], "spells_added": []}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get character info
                cursor.execute("SELECT level, charisma FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                if not char_row:
                    result["reason"] = "Character not found"
                    return result

                level = char_row['level']
                charisma_score = char_row['charisma']
                cha_modifier = (charisma_score - 10) // 2

                # Initialize spellcasting if level 2+
                if level >= 2 and self.spellcasting_service:
                    try:
                        spellcasting_init = self.spellcasting_service.initialize_character_spellcasting(
                            character_id, 'paladin'
                        )
                        if not spellcasting_init:
                            result["reason"] = "Failed to initialize spellcasting"
                            return result
                    except Exception:
                        # Continue without spellcasting
                        pass

                # Calculate max prepared spells (Cha modifier + half paladin level, minimum 1)
                max_prepared = max(1, cha_modifier + (level // 2)) if level >= 2 else 0

                # Calculate Lay on Hands pool (5 x paladin level)
                lay_on_hands_max = 5 * level

                # Calculate Channel Divinity uses
                channel_divinity_max = 1 if level >= 3 else 0
                if level >= 7:
                    channel_divinity_max = 2
                elif level >= 15:
                    channel_divinity_max = 3

                # Initialize paladin features
                cursor.execute("""
                    INSERT OR REPLACE INTO paladin_features
                    (character_id, level, sacred_oath, lay_on_hands_pool_current, lay_on_hands_pool_max,
                     channel_divinity_uses_current, channel_divinity_uses_max, channel_divinity_last_reset,
                     spells_prepared, max_spells_prepared)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), 0, ?)
                """, (character_id, level, oath, lay_on_hands_max, lay_on_hands_max,
                     channel_divinity_max, channel_divinity_max, max_prepared))

                # Add oath spells if level 3+
                oath_spells = []
                if level >= 3:
                    oath_spells = self._add_oath_spells(cursor, character_id, oath, level)
                    result["spells_added"] = oath_spells

                # Apply oath features
                oath_features = self._apply_oath_features(cursor, character_id, oath, level)
                result["features_added"] = oath_features

                # Initialize core features
                self._initialize_core_features(cursor, character_id, level)

                conn.commit()
                result["success"] = True
                result["oath"] = oath
                result["max_prepared_spells"] = max_prepared
                result["lay_on_hands_pool"] = lay_on_hands_max
                result["channel_divinity_uses"] = channel_divinity_max

        except Exception as e:
            result["reason"] = f"Initialization failed: {str(e)}"

        return result

    def _add_oath_spells(self, cursor, character_id: str, oath: str, level: int) -> List[str]:
        """Add oath spells that are always prepared."""
        oath_spell_lists = {
            "devotion": {
                3: ["protection_from_evil_and_good", "sanctuary"],
                5: ["lesser_restoration", "zone_of_truth"],
                9: ["beacon_of_hope", "dispel_magic"],
                13: ["freedom_of_movement", "guardian_of_faith"],
                17: ["commune", "flame_strike"]
            },
            "ancients": {
                3: ["ensnaring_strike", "speak_with_animals"],
                5: ["moonbeam", "misty_step"],
                9: ["plant_growth", "protection_from_energy"],
                13: ["ice_storm", "stoneskin"],
                17: ["commune_with_nature", "tree_stride"]
            },
            "vengeance": {
                3: ["bane", "hunters_mark"],
                5: ["hold_person", "misty_step"],
                9: ["haste", "protection_from_energy"],
                13: ["dimension_door", "banishment"],
                17: ["hold_monster", "scrying"]
            }
        }

        spells_added = []
        if oath in oath_spell_lists:
            oath_spells = oath_spell_lists[oath]
            for spell_level, spells in oath_spells.items():
                if level >= spell_level:
                    for spell_id in spells:
                        try:
                            # Add to character_spells as always prepared
                            cursor.execute("""
                                INSERT OR IGNORE INTO character_spells
                                (character_id, spell_id, spell_level, is_prepared, source, source_level, always_prepared)
                                VALUES (?, ?, ?, 1, 'oath', ?, 1)
                            """, (character_id, spell_id, self._get_spell_level(spell_id), spell_level))
                            spells_added.append(spell_id)
                        except Exception:
                            pass  # Spell might not exist in database yet

        return spells_added

    def _get_spell_level(self, spell_id: str) -> int:
        """Get spell level from spell registry."""
        try:
            spell = spell_registry.get_spell(spell_id)
            return spell.level if spell else 1
        except Exception:
            # Fallback spell levels for oath spells
            spell_levels = {
                'protection_from_evil_and_good': 1,
                'sanctuary': 1,
                'lesser_restoration': 2,
                'zone_of_truth': 2,
                'beacon_of_hope': 3,
                'dispel_magic': 3,
                'freedom_of_movement': 4,
                'guardian_of_faith': 4,
                'commune': 5,
                'flame_strike': 5
            }
            return spell_levels.get(spell_id, 1)

    def _apply_oath_features(self, cursor, character_id: str, oath: str, level: int) -> List[str]:
        """Apply oath features based on character level."""
        features_added = []

        # Level 3: Channel Divinity options
        if level >= 3:
            if oath == "devotion":
                # Sacred Weapon
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'sacred_weapon', 'oath_devotion', 3, 0, 0)
                """, (character_id,))
                features_added.append("Sacred Weapon")

                # Turn the Unholy
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'turn_the_unholy', 'oath_devotion', 3, 0, 0)
                """, (character_id,))
                features_added.append("Turn the Unholy")

        # Level 7: Oath features
        if level >= 7:
            if oath == "devotion":
                # Aura of Devotion
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'aura_of_devotion', 'oath_devotion', 7, 0, 0)
                """, (character_id,))
                features_added.append("Aura of Devotion")

        # Level 15: Oath features
        if level >= 15:
            if oath == "devotion":
                # Purity of Spirit
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'purity_of_spirit', 'oath_devotion', 15, 0, 0)
                """, (character_id,))
                features_added.append("Purity of Spirit")

        # Level 20: Oath capstone
        if level >= 20:
            if oath == "devotion":
                # Holy Nimbus
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_id, source, source_level, uses_current, uses_max)
                    VALUES (?, 'holy_nimbus', 'oath_devotion', 20, 0, 1)
                """, (character_id,))
                features_added.append("Holy Nimbus")

        return features_added

    def _initialize_core_features(self, cursor, character_id: str, level: int):
        """Initialize core paladin features."""
        # Level 1: Divine Sense
        cursor.execute("""
            INSERT OR IGNORE INTO character_features
            (character_id, feature_id, source, source_level, uses_current, uses_max)
            VALUES (?, 'divine_sense', 'paladin', 1, 0, ?)
        """, (character_id, 1 + ((level - 1) // 2)))  # Proficiency bonus uses

        # Level 1: Lay on Hands (tracked in paladin_features)

        # Level 2: Divine Smite (unlimited, uses spell slots)
        if level >= 2:
            cursor.execute("""
                INSERT OR IGNORE INTO character_features
                (character_id, feature_id, source, source_level, uses_current, uses_max)
                VALUES (?, 'divine_smite', 'paladin', 2, 0, 0)
            """, (character_id,))

        # Level 6: Aura of Protection
        if level >= 6:
            cursor.execute("""
                INSERT OR IGNORE INTO character_features
                (character_id, feature_id, source, source_level, uses_current, uses_max)
                VALUES (?, 'aura_of_protection', 'paladin', 6, 0, 0)
            """, (character_id,))

        # Level 10: Aura of Courage
        if level >= 10:
            cursor.execute("""
                INSERT OR IGNORE INTO character_features
                (character_id, feature_id, source, source_level, uses_current, uses_max)
                VALUES (?, 'aura_of_courage', 'paladin', 10, 0, 0)
            """, (character_id,))

        # Level 14: Cleansing Touch
        if level >= 14:
            cursor.execute("""
                INSERT OR IGNORE INTO character_features
                (character_id, feature_id, source, source_level, uses_current, uses_max)
                VALUES (?, 'cleansing_touch', 'paladin', 14, 0, ?)
            """, (character_id, ((level - 1) // 4) + 1))  # Charisma modifier uses

    def use_lay_on_hands(self, character_id: str, healing_points: int) -> Dict[str, Any]:
        """
        Use Lay on Hands to heal.

        Args:
            character_id: Character using Lay on Hands
            healing_points: Number of points to spend (max 5 per use)

        Returns:
            Dict with healing results
        """
        result = {"success": False, "healing_done": 0}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get current pool
                cursor.execute("""
                    SELECT lay_on_hands_pool_current, lay_on_hands_pool_max
                    FROM paladin_features WHERE character_id = ?
                """, (character_id,))

                paladin_row = cursor.fetchone()
                if not paladin_row:
                    result["reason"] = "Not a paladin"
                    return result

                current_pool = paladin_row['lay_on_hands_pool_current']
                max_pool = paladin_row['lay_on_hands_pool_max']

                # Validate healing amount
                healing_points = min(healing_points, current_pool, 5)  # Max 5 per use

                if healing_points <= 0:
                    result["reason"] = "No healing points available"
                    return result

                # Deduct from pool
                cursor.execute("""
                    UPDATE paladin_features
                    SET lay_on_hands_pool_current = lay_on_hands_pool_current - ?
                    WHERE character_id = ?
                """, (healing_points, character_id))

                conn.commit()
                result["success"] = True
                result["healing_done"] = healing_points
                result["pool_remaining"] = current_pool - healing_points

        except Exception as e:
            result["reason"] = f"Lay on Hands failed: {str(e)}"

        return result

    def divine_smite(self, character_id: str, spell_slot_level: int, target_is_undead_or_fiend: bool = False,
                     use_free_smite: bool = False) -> Dict[str, Any]:
        """
        Calculate Divine Smite damage.

        Args:
            character_id: Character using Divine Smite
            spell_slot_level: Level of spell slot to expend (or free smite level)
            target_is_undead_or_fiend: Whether target is undead or fiend
            use_free_smite: Whether to use the free Paladin's Smite (1/long rest)

        Returns:
            Dict with smite damage information and resource consumption
        """
        result = {"success": False, "damage_dice": 0, "damage_type": "radiant", "used_free_smite": False}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Check if using free smite
                if use_free_smite:
                    cursor.execute("""
                        SELECT free_divine_smite_used, level
                        FROM paladin_features
                        WHERE character_id = ?
                    """, (character_id,))
                    paladin_row = cursor.fetchone()

                    if not paladin_row or paladin_row['level'] < 2:
                        result["reason"] = "Paladin's Smite requires level 2+"
                        return result

                    if paladin_row['free_divine_smite_used']:
                        result["reason"] = "Free Divine Smite already used this long rest"
                        return result

                    # Mark free smite as used
                    cursor.execute("""
                        UPDATE paladin_features
                        SET free_divine_smite_used = TRUE,
                            free_divine_smite_last_reset = datetime('now')
                        WHERE character_id = ?
                    """, (character_id,))
                    conn.commit()
                    result["used_free_smite"] = True

                # Base damage: 2d8 + 1d8 per spell slot level above 1st
                damage_dice = 2 + (spell_slot_level - 1)

                # +1d8 against undead and fiends
                if target_is_undead_or_fiend:
                    damage_dice += 1

                # Maximum 5d8 total
                damage_dice = min(damage_dice, 5)

                result["success"] = True
                result["damage_dice"] = damage_dice
                result["spell_slot_consumed"] = spell_slot_level if not use_free_smite else 0
                result["extra_vs_undead_fiend"] = target_is_undead_or_fiend

        except Exception as e:
            result["reason"] = f"Divine Smite calculation failed: {str(e)}"

        return result

    def use_channel_divinity(self, character_id: str, ability_name: str) -> Dict[str, Any]:
        """
        Use Channel Divinity.

        Args:
            character_id: Character using Channel Divinity
            ability_name: Name of the Channel Divinity ability

        Returns:
            Dict with usage results
        """
        result = {"success": False}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Check uses
                cursor.execute("""
                    SELECT channel_divinity_uses_current, channel_divinity_uses_max
                    FROM paladin_features WHERE character_id = ?
                """, (character_id,))

                paladin_row = cursor.fetchone()
                if not paladin_row:
                    result["reason"] = "Not a paladin"
                    return result

                if paladin_row['channel_divinity_uses_current'] >= paladin_row['channel_divinity_uses_max']:
                    result["reason"] = "No Channel Divinity uses remaining"
                    return result

                # Use a charge
                cursor.execute("""
                    UPDATE paladin_features
                    SET channel_divinity_uses_current = channel_divinity_uses_current + 1
                    WHERE character_id = ?
                """, (character_id,))

                conn.commit()
                result["success"] = True
                result["ability_used"] = ability_name
                result["uses_remaining"] = paladin_row['channel_divinity_uses_max'] - paladin_row['channel_divinity_uses_current'] - 1

        except Exception as e:
            result["reason"] = f"Channel Divinity failed: {str(e)}"

        return result

    def long_rest_recovery(self, character_id: str) -> Dict[str, Any]:
        """Handle long rest recovery for paladins."""
        result = {"success": False}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Reset Lay on Hands pool, Channel Divinity, and free Divine Smite
                cursor.execute("""
                    UPDATE paladin_features
                    SET lay_on_hands_pool_current = lay_on_hands_pool_max,
                        channel_divinity_uses_current = 0,
                        channel_divinity_last_reset = datetime('now'),
                        free_divine_smite_used = FALSE,
                        free_divine_smite_last_reset = datetime('now')
                    WHERE character_id = ?
                """, (character_id,))

                # Let spellcasting service handle spell slot recovery
                spell_recovery = {}
                if self.spellcasting_service:
                    try:
                        spell_recovery = self.spellcasting_service.long_rest_recovery(character_id)
                    except Exception:
                        pass

                conn.commit()
                result["success"] = True
                result["lay_on_hands_reset"] = True
                result["channel_divinity_reset"] = True
                result["free_divine_smite_reset"] = True
                result["spell_recovery"] = spell_recovery

        except Exception as e:
            result["reason"] = f"Recovery failed: {str(e)}"

        return result

    def has_free_divine_smite(self, character_id: str) -> bool:
        """Check if the paladin has their free Divine Smite available."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT free_divine_smite_used, level
                    FROM paladin_features
                    WHERE character_id = ?
                """, (character_id,))
                row = cursor.fetchone()

                if row and row['level'] >= 2:
                    return not row['free_divine_smite_used']
                return False
        except Exception:
            return False

    def get_paladin_info(self, character_id: str) -> Dict[str, Any]:
        """Get comprehensive paladin information."""
        result = {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get paladin features
                cursor.execute("""
                    SELECT * FROM paladin_features WHERE character_id = ?
                """, (character_id,))
                paladin_row = cursor.fetchone()

                if paladin_row:
                    result["paladin_features"] = dict(paladin_row)

                    # Get prepared spells (including oath spells)
                    cursor.execute("""
                        SELECT cs.*, s.name, s.school
                        FROM character_spells cs
                        JOIN spells s ON cs.spell_id = s.id
                        WHERE cs.character_id = ? AND cs.is_prepared = 1
                        ORDER BY cs.spell_level, s.name
                    """, (character_id,))

                    result["prepared_spells"] = [dict(row) for row in cursor.fetchall()]

                    # Get oath spells specifically
                    cursor.execute("""
                        SELECT cs.*, s.name, s.school
                        FROM character_spells cs
                        JOIN spells s ON cs.spell_id = s.id
                        WHERE cs.character_id = ? AND cs.source = 'oath'
                        ORDER BY cs.spell_level, s.name
                    """, (character_id,))

                    result["oath_spells"] = [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            result["error"] = str(e)

        return result


# Global instance
_paladin_service = None

def get_paladin_service(db_path: str = "talekeeper.db") -> PaladinAbilitiesService:
    """Get singleton paladin service instance."""
    global _paladin_service
    if _paladin_service is None:
        _paladin_service = PaladinAbilitiesService(db_path)
    return _paladin_service