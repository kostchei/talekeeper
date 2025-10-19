# core
# core
"""
Cleric Abilities Service

Handles Cleric-specific abilities including Channel Divinity, divine domains,
and spellcasting features.

Phase 2.1: Cleric Base Class Implementation
Implementation Plan Reference: Phase 2 > Phase 2.1
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from services.spellcasting_service import get_spellcasting_service, SpellcastingAbility
from services.spell_registry import spell_registry


class ClericAbilitiesService:
    """Service for Cleric abilities and features."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.spellcasting_service = get_spellcasting_service(db_path)

    def initialize_cleric_character(self, character_id: str, domain: str = "life") -> Dict[str, Any]:
        """
        Initialize a character as a Cleric with the specified domain.

        Args:
            character_id: Character to initialize
            domain: Divine domain (default: 'life')

        Returns:
            Dict with initialization results
        """
        result = {"success": False, "features_added": [], "spells_added": []}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get character level
                cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                if not char_row:
                    result["reason"] = "Character not found"
                    return result

                level = char_row['level']

                # Initialize spellcasting
                spellcasting_init = self.spellcasting_service.initialize_character_spellcasting(
                    character_id, 'cleric'
                )
                if not spellcasting_init:
                    result["reason"] = "Failed to initialize spellcasting"
                    return result

                # Initialize cleric features
                max_channel_divinity = 1 if level < 6 else (2 if level < 18 else 3)

                cursor.execute("""
                    INSERT OR REPLACE INTO cleric_features
                    (character_id, domain, channel_divinity_uses, max_channel_divinity,
                     divine_intervention_used, last_cd_reset)
                    VALUES (?, ?, 0, ?, 0, datetime('now'))
                """, (character_id, domain, max_channel_divinity))

                # Initialize Channel Divinity options
                self._initialize_channel_divinity(cursor, character_id, domain, level)

                # Add domain spells
                domain_spells = self._add_domain_spells(cursor, character_id, domain, level)
                result["spells_added"] = domain_spells

                # Apply domain features
                domain_features = self._apply_domain_features(cursor, character_id, domain, level)
                result["features_added"] = domain_features

                conn.commit()
                result["success"] = True
                result["domain"] = domain
                result["channel_divinity_uses"] = max_channel_divinity

        except Exception as e:
            result["reason"] = f"Initialization failed: {str(e)}"

        return result

    def _initialize_channel_divinity(self, cursor, character_id: str, domain: str, level: int):
        """Initialize Channel Divinity options for a cleric."""
        # Get available Channel Divinity options
        cursor.execute("""
            SELECT id, name, domain FROM channel_divinity_options
            WHERE (domain IS NULL OR domain = ?) AND level_requirement <= ?
        """, (domain, level))

        options = cursor.fetchall()

        for option in options:
            cursor.execute("""
                INSERT OR REPLACE INTO character_channel_divinity
                (character_id, option_id, uses_remaining)
                VALUES (?, ?, 0)
            """, (character_id, option['id']))

    def _add_domain_spells(self, cursor, character_id: str, domain: str, level: int) -> List[str]:
        """Add domain spells to character's spell list."""
        # Get domain definition
        cursor.execute("""
            SELECT domain_spells FROM divine_domains WHERE id = ?
        """, (domain,))

        domain_row = cursor.fetchone()
        if not domain_row or not domain_row['domain_spells']:
            return []

        domain_spells_data = json.loads(domain_row['domain_spells'])
        spells_added = []

        # Add spells for each level the character has access to
        for spell_level_str, spell_list in domain_spells_data.items():
            spell_level = int(spell_level_str)

            # Characters get domain spells when they can cast that spell level
            # Level 1: 1st level spells, Level 3: 2nd level spells, etc.
            required_char_level = 1 + (spell_level - 1) * 2

            if level >= required_char_level:
                for spell_id in spell_list:
                    # Add spell as always prepared
                    cursor.execute("""
                        INSERT OR REPLACE INTO character_spells
                        (character_id, spell_id, spell_level, is_prepared, source,
                         source_level, always_prepared)
                        VALUES (?, ?, ?, 1, 'domain', ?, 1)
                    """, (character_id, spell_id, spell_level, required_char_level))

                    spells_added.append(spell_id)

        return spells_added

    def _apply_domain_features(self, cursor, character_id: str, domain: str, level: int) -> List[str]:
        """Apply domain-specific features."""
        # Get domain features
        cursor.execute("""
            SELECT features FROM divine_domains WHERE id = ?
        """, (domain,))

        domain_row = cursor.fetchone()
        if not domain_row or not domain_row['features']:
            return []

        features_data = json.loads(domain_row['features'])
        features_applied = []

        for feature in features_data:
            if feature.get('level', 1) <= level:
                feature_name = feature.get('name', 'Unknown Feature')

                # Apply specific feature logic
                if feature_name == "Bonus Proficiency" and domain == "life":
                    # Life Domain heavy armor proficiency
                    # This would typically be handled by the character creation system
                    features_applied.append("Heavy Armor Proficiency")

                elif feature_name in ["Disciple of Life", "Blessed Healer", "Divine Strike", "Supreme Healing"]:
                    # Passive features tracked in domain system
                    features_applied.append(feature_name)

        return features_applied

    def use_channel_divinity(self, character_id: str, option_id: str, targets: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Use a Channel Divinity option.

        Args:
            character_id: Character using the ability
            option_id: Channel Divinity option to use
            targets: Optional list of target character IDs

        Returns:
            Dict with usage results
        """
        result = {"success": False, "effects": []}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Check if character has uses remaining
                cursor.execute("""
                    SELECT cf.channel_divinity_uses, cf.max_channel_divinity,
                           ccd.uses_remaining, cdo.name, cdo.description, cdo.action_cost
                    FROM cleric_features cf
                    JOIN character_channel_divinity ccd ON cf.character_id = ccd.character_id
                    JOIN channel_divinity_options cdo ON ccd.option_id = cdo.id
                    WHERE cf.character_id = ? AND cdo.id = ?
                """, (character_id, option_id))

                row = cursor.fetchone()
                if not row:
                    result["reason"] = "Channel Divinity option not available"
                    return result

                if row['channel_divinity_uses'] >= row['max_channel_divinity']:
                    result["reason"] = "No Channel Divinity uses remaining"
                    return result

                # Use Channel Divinity
                cursor.execute("""
                    UPDATE cleric_features
                    SET channel_divinity_uses = channel_divinity_uses + 1
                    WHERE character_id = ?
                """, (character_id,))

                cursor.execute("""
                    UPDATE character_channel_divinity
                    SET uses_remaining = uses_remaining + 1, last_used = datetime('now')
                    WHERE character_id = ? AND option_id = ?
                """, (character_id, option_id))

                # Apply specific Channel Divinity effects
                effects = self._apply_channel_divinity_effect(
                    cursor, character_id, option_id, targets
                )

                result["success"] = True
                result["ability_used"] = row['name']
                result["effects"] = effects
                result["remaining_uses"] = row['max_channel_divinity'] - row['channel_divinity_uses'] - 1

                conn.commit()

        except Exception as e:
            result["reason"] = f"Channel Divinity failed: {str(e)}"

        return result

    def _apply_channel_divinity_effect(self, cursor, character_id: str, option_id: str, targets: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Apply the specific effects of a Channel Divinity option."""
        effects = []

        if option_id == "turn_undead":
            # Turn Undead - would require integration with combat system
            effects.append({
                "type": "save_or_effect",
                "save_type": "wisdom",
                "effect": "turned",
                "duration": "1 minute",
                "area": "30 feet",
                "targets": "undead"
            })

        elif option_id == "preserve_life":
            # Life Domain - Preserve Life
            # Get cleric level for healing calculation
            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            level = cursor.fetchone()['level']

            healing_pool = 5 * level

            effects.append({
                "type": "healing",
                "healing_pool": healing_pool,
                "area": "30 feet",
                "restriction": "cannot_exceed_half_max_hp",
                "distribution": "choose"
            })

        elif option_id == "destroy_undead":
            # Higher level Turn Undead enhancement
            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            level = cursor.fetchone()['level']

            # Destroy undead of appropriate CR
            if level >= 17:
                cr_threshold = 4
            elif level >= 14:
                cr_threshold = 3
            elif level >= 11:
                cr_threshold = 2
            elif level >= 8:
                cr_threshold = 1
            else:
                cr_threshold = 0.5

            effects.append({
                "type": "destroy_undead",
                "cr_threshold": cr_threshold,
                "trigger": "after_turn_undead"
            })

        return effects

    def get_character_cleric_info(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get complete cleric information for a character."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT cf.domain, cf.channel_divinity_uses, cf.max_channel_divinity,
                       cf.divine_intervention_used, dd.name as domain_name,
                       dd.description as domain_description
                FROM cleric_features cf
                JOIN divine_domains dd ON cf.domain = dd.id
                WHERE cf.character_id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if not row:
                return None

            # Get available Channel Divinity options
            cursor.execute("""
                SELECT cdo.id, cdo.name, cdo.description, cdo.action_cost,
                       ccd.uses_remaining
                FROM character_channel_divinity ccd
                JOIN channel_divinity_options cdo ON ccd.option_id = cdo.id
                WHERE ccd.character_id = ?
            """, (character_id,))

            channel_options = [dict(option) for option in cursor.fetchall()]

            # Get domain spells
            cursor.execute("""
                SELECT cs.spell_id, cs.spell_level, cs.always_prepared
                FROM character_spells cs
                WHERE cs.character_id = ? AND cs.source = 'domain'
                ORDER BY cs.spell_level, cs.spell_id
            """, (character_id,))

            domain_spells = [dict(spell) for spell in cursor.fetchall()]

            return {
                "domain": row['domain'],
                "domain_name": row['domain_name'],
                "domain_description": row['domain_description'],
                "channel_divinity_uses": row['channel_divinity_uses'],
                "max_channel_divinity": row['max_channel_divinity'],
                "channel_divinity_remaining": row['max_channel_divinity'] - row['channel_divinity_uses'],
                "divine_intervention_used": bool(row['divine_intervention_used']),
                "channel_options": channel_options,
                "domain_spells": domain_spells
            }

    def reset_cleric_resources(self, character_id: str, rest_type: str = "long") -> Dict[str, Any]:
        """Reset cleric resources on rest."""
        result = {"channel_divinity_reset": False, "divine_intervention_reset": False}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if rest_type in ["long", "short"]:
                # Reset Channel Divinity on short or long rest
                cursor.execute("""
                    UPDATE cleric_features
                    SET channel_divinity_uses = 0, last_cd_reset = datetime('now')
                    WHERE character_id = ?
                """, (character_id,))

                cursor.execute("""
                    UPDATE character_channel_divinity
                    SET uses_remaining = 0
                    WHERE character_id = ?
                """, (character_id,))

                result["channel_divinity_reset"] = True

            if rest_type == "long":
                # Reset Divine Intervention on long rest (if used)
                cursor.execute("""
                    UPDATE cleric_features
                    SET divine_intervention_used = 0
                    WHERE character_id = ?
                """, (character_id,))

                result["divine_intervention_reset"] = True

            conn.commit()

        return result

    def apply_disciple_of_life(self, character_id: str, spell_level: int, base_healing: int) -> int:
        """
        Apply Disciple of Life bonus healing for Life Domain clerics.

        Args:
            character_id: Cleric character
            spell_level: Level of the healing spell cast
            base_healing: Base healing amount

        Returns:
            Total healing including Disciple of Life bonus
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if character is Life Domain cleric
            cursor.execute("""
                SELECT domain FROM cleric_features
                WHERE character_id = ? AND domain = 'life'
            """, (character_id,))

            if cursor.fetchone() and spell_level >= 1:
                # Disciple of Life: +2 + spell level healing
                bonus_healing = 2 + spell_level
                return base_healing + bonus_healing

        return base_healing

    def apply_blessed_healer(self, character_id: str, spell_level: int) -> int:
        """
        Apply Blessed Healer self-healing for Life Domain clerics.

        Returns the amount of self-healing to apply.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check if character is Life Domain cleric level 6+
            cursor.execute("""
                SELECT c.level FROM characters c
                JOIN cleric_features cf ON c.id = cf.character_id
                WHERE c.id = ? AND cf.domain = 'life' AND c.level >= 6
            """, (character_id,))

            if cursor.fetchone() and spell_level >= 1:
                # Blessed Healer: 2 + spell level self-healing
                return 2 + spell_level

        return 0