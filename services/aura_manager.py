# core
# core
"""
Aura Manager for Paladin Auras

Manages passive aura effects that benefit the paladin and nearby allies.
Handles Aura of Protection, Aura of Courage, and oath-specific auras.
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AuraType(Enum):
    """Types of paladin auras."""
    PROTECTION = "protection"      # +Cha mod to saves
    COURAGE = "courage"            # Fear immunity
    DEVOTION = "devotion"          # Charm immunity (Oath of Devotion)
    ANCIENTS = "ancients"          # Spell resistance (Oath of Ancients)
    VENGEANCE = "vengeance"        # Advantage on opportunity attacks (Oath of Vengeance)


@dataclass
class AuraEffect:
    """Represents an active aura effect."""
    aura_type: AuraType
    source_character_id: str
    level: int
    range_feet: int
    description: str
    save_bonus: int = 0
    immunity_conditions: List[str] = None
    advantage_types: List[str] = None

    def __post_init__(self):
        if self.immunity_conditions is None:
            self.immunity_conditions = []
        if self.advantage_types is None:
            self.advantage_types = []


class AuraManager:
    """Manages paladin aura effects."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.active_auras: Dict[str, List[AuraEffect]] = {}  # character_id -> list of auras affecting them

    def get_character_auras(self, character_id: str) -> List[AuraEffect]:
        """Get all auras affecting a character."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get character's own auras
                own_auras = self._get_character_own_auras(cursor, character_id)

                # Get auras from nearby paladins (for now, assume single character)
                # In a full party system, this would check distance between characters
                nearby_auras = []

                return own_auras + nearby_auras

        except Exception as e:
            print(f"Error getting character auras: {e}")
            return []

    def _get_character_own_auras(self, cursor, character_id: str) -> List[AuraEffect]:
        """Get auras that a character generates for themselves."""
        auras = []

        try:
            # Get character info
            cursor.execute("""
                SELECT level, class_id, charisma, subclass_id
                FROM characters
                WHERE id = ?
            """, (character_id,))

            char_row = cursor.fetchone()
            if not char_row or char_row['class_id'].lower() != 'paladin':
                return auras

            level = char_row['level']
            charisma_score = char_row['charisma']
            cha_modifier = (charisma_score - 10) // 2
            subclass = char_row['subclass_id'] or 'devotion'

            # Aura range: 10 feet base, 30 feet at level 18+
            aura_range = 30 if level >= 18 else 10

            # Level 6: Aura of Protection
            if level >= 6:
                auras.append(AuraEffect(
                    aura_type=AuraType.PROTECTION,
                    source_character_id=character_id,
                    level=level,
                    range_feet=aura_range,
                    description=f"Aura of Protection: +{max(1, cha_modifier)} bonus to saving throws",
                    save_bonus=max(1, cha_modifier)
                ))

            # Level 10: Aura of Courage
            if level >= 10:
                auras.append(AuraEffect(
                    aura_type=AuraType.COURAGE,
                    source_character_id=character_id,
                    level=level,
                    range_feet=aura_range,
                    description="Aura of Courage: Immunity to being frightened",
                    immunity_conditions=["frightened"]
                ))

            # Oath-specific auras (level 7)
            if level >= 7:
                oath_aura = self._get_oath_aura(subclass, character_id, level, aura_range)
                if oath_aura:
                    auras.append(oath_aura)

        except Exception as e:
            print(f"Error getting character's own auras: {e}")

        return auras

    def _get_oath_aura(self, subclass: str, character_id: str, level: int, aura_range: int) -> Optional[AuraEffect]:
        """Get oath-specific aura effect."""
        subclass = subclass.lower()

        if subclass == 'devotion':
            # Aura of Devotion: Immunity to charm
            return AuraEffect(
                aura_type=AuraType.DEVOTION,
                source_character_id=character_id,
                level=level,
                range_feet=aura_range,
                description="Aura of Devotion: Immunity to being charmed",
                immunity_conditions=["charmed"]
            )

        elif subclass == 'ancients':
            # Aura of Warding: Spell resistance
            return AuraEffect(
                aura_type=AuraType.ANCIENTS,
                source_character_id=character_id,
                level=level,
                range_feet=aura_range,
                description="Aura of Warding: Resistance to spell damage",
                advantage_types=["spell_saves"]
            )

        elif subclass == 'vengeance':
            # Aura of Alacrity: Advantage on opportunity attacks
            return AuraEffect(
                aura_type=AuraType.VENGEANCE,
                source_character_id=character_id,
                level=level,
                range_feet=aura_range,
                description="Aura of Alacrity: Advantage on opportunity attacks",
                advantage_types=["opportunity_attacks"]
            )

        return None

    def calculate_save_bonus(self, character_id: str, save_type: str) -> int:
        """Calculate total saving throw bonus from auras."""
        auras = self.get_character_auras(character_id)
        total_bonus = 0

        for aura in auras:
            if aura.aura_type == AuraType.PROTECTION:
                total_bonus += aura.save_bonus

        return total_bonus

    def has_condition_immunity(self, character_id: str, condition: str) -> bool:
        """Check if character has immunity to a condition from auras."""
        auras = self.get_character_auras(character_id)

        for aura in auras:
            if condition.lower() in [c.lower() for c in aura.immunity_conditions]:
                return True

        return False

    def has_advantage_type(self, character_id: str, advantage_type: str) -> bool:
        """Check if character has advantage on specific types of rolls from auras."""
        auras = self.get_character_auras(character_id)

        for aura in auras:
            if advantage_type.lower() in [a.lower() for a in aura.advantage_types]:
                return True

        return False

    def get_aura_descriptions(self, character_id: str) -> List[str]:
        """Get descriptions of all active auras affecting a character."""
        auras = self.get_character_auras(character_id)
        return [aura.description for aura in auras]

    def update_character_level(self, character_id: str, new_level: int):
        """Update aura effects when character level changes."""
        # Auras are calculated dynamically, so no need to store state
        # This method exists for future optimization if needed
        pass

    def get_aura_range(self, character_level: int) -> int:
        """Get aura range based on character level."""
        return 30 if character_level >= 18 else 10

    def apply_aura_to_save(self, character_id: str, save_roll: int, save_type: str) -> Tuple[int, List[str]]:
        """Apply aura bonuses to a saving throw."""
        bonus = self.calculate_save_bonus(character_id, save_type)
        modified_roll = save_roll + bonus

        descriptions = []
        if bonus > 0:
            descriptions.append(f"Aura of Protection: +{bonus}")

        return modified_roll, descriptions

    def check_aura_condition_immunity(self, character_id: str, condition: str) -> Tuple[bool, Optional[str]]:
        """Check condition immunity and return the aura providing it."""
        auras = self.get_character_auras(character_id)

        for aura in auras:
            if condition.lower() in [c.lower() for c in aura.immunity_conditions]:
                return True, aura.description

        return False, None

    def get_active_aura_summary(self, character_id: str) -> Dict[str, Any]:
        """Get a summary of all active auras for UI display."""
        auras = self.get_character_auras(character_id)

        summary = {
            "total_auras": len(auras),
            "save_bonus": self.calculate_save_bonus(character_id, "all"),
            "immunities": [],
            "advantages": [],
            "descriptions": []
        }

        for aura in auras:
            summary["immunities"].extend(aura.immunity_conditions)
            summary["advantages"].extend(aura.advantage_types)
            summary["descriptions"].append(aura.description)

        # Remove duplicates
        summary["immunities"] = list(set(summary["immunities"]))
        summary["advantages"] = list(set(summary["advantages"]))

        return summary


# Global instance
_aura_manager = None

def get_aura_manager(db_path: str = "talekeeper.db") -> AuraManager:
    """Get singleton aura manager instance."""
    global _aura_manager
    if _aura_manager is None:
        _aura_manager = AuraManager(db_path)
    return _aura_manager