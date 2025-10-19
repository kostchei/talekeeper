# core
# core
"""
Spell Registry for TaleKeeper

Central registry for all spell definitions. Provides lazy loading and caching
similar to the subclass registry to efficiently manage all D&D spells.

Phase 1.2: Spell Registry Service
Implementation Plan Reference: Phase 1 > Step 1.2
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum

class SpellSchool(Enum):
    """D&D spell schools."""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"

class CastingTime(Enum):
    """Standard casting times."""
    ACTION = "1 action"
    BONUS_ACTION = "1 bonus action"
    REACTION = "1 reaction"
    MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    HOUR = "1 hour"
    RITUAL = "1 minute (ritual)"

@dataclass
class SpellDefinition:
    """Complete spell definition."""
    id: str
    name: str
    level: int
    school: SpellSchool
    casting_time: str
    range_value: str
    components: str
    duration: str
    concentration: bool = False
    ritual: bool = False
    description: str = ""
    higher_levels: Optional[str] = None
    source: str = "PHB"
    classes: List[str] = None

    def __post_init__(self):
        if self.classes is None:
            self.classes = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['school'] = self.school.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpellDefinition':
        """Create from dictionary."""
        data = data.copy()
        data['school'] = SpellSchool(data['school'].lower())
        if 'classes' in data and isinstance(data['classes'], str):
            data['classes'] = json.loads(data['classes'])
        return cls(**data)

    def is_available_to_class(self, class_name: str) -> bool:
        """Check if this spell is available to a specific class."""
        return class_name.lower() in [c.lower() for c in self.classes]

class SpellRegistry:
    """
    Registry for all spell definitions.

    Provides centralized access to spell data with caching for performance.
    """

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._spell_cache: Dict[str, SpellDefinition] = {}
        self._class_spell_cache: Dict[str, List[str]] = {}

    def get_spell(self, spell_id: str) -> Optional[SpellDefinition]:
        """
        Get a spell definition by ID.

        Args:
            spell_id: The spell's unique identifier

        Returns:
            SpellDefinition or None if not found
        """
        # Check cache first
        if spell_id in self._spell_cache:
            return self._spell_cache[spell_id]

        # Load from database
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, level, school, casting_time, range_value,
                       components, duration, concentration, ritual, description,
                       higher_levels, source, classes
                FROM spells
                WHERE id = ?
            """, (spell_id,))

            row = cursor.fetchone()
            if not row:
                return None

            # Convert to SpellDefinition
            spell_data = dict(row)
            if spell_data.get('classes'):
                spell_data['classes'] = json.loads(spell_data['classes'])
            else:
                spell_data['classes'] = []

            spell_def = SpellDefinition.from_dict(spell_data)

            # Cache it
            self._spell_cache[spell_id] = spell_def

            return spell_def

    def get_spells_by_class(self, class_name: str, level: Optional[int] = None) -> List[SpellDefinition]:
        """
        Get all spells available to a specific class.

        Args:
            class_name: The class name (e.g., "wizard", "cleric")
            level: Optional spell level filter

        Returns:
            List of SpellDefinition objects
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build query with optional level filter
            query = """
                SELECT s.id, s.name, s.level, s.school, s.casting_time, s.range_value,
                       s.components, s.duration, s.concentration, s.ritual, s.description,
                       s.higher_levels, s.source, s.classes
                FROM spells s
                JOIN spell_class_lists scl ON s.id = scl.spell_id
                WHERE scl.class_id = ?
            """
            params = [class_name.lower()]

            if level is not None:
                query += " AND s.level = ?"
                params.append(level)

            query += " ORDER BY s.level, s.name"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            spells = []
            for row in rows:
                spell_data = dict(row)
                if spell_data.get('classes'):
                    spell_data['classes'] = json.loads(spell_data['classes'])
                else:
                    spell_data['classes'] = []

                spell_def = SpellDefinition.from_dict(spell_data)
                spells.append(spell_def)

                # Cache individual spell
                self._spell_cache[spell_def.id] = spell_def

            return spells

    def get_spells_by_level(self, level: int) -> List[SpellDefinition]:
        """Get all spells of a specific level."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, level, school, casting_time, range_value,
                       components, duration, concentration, ritual, description,
                       higher_levels, source, classes
                FROM spells
                WHERE level = ?
                ORDER BY name
            """, (level,))

            rows = cursor.fetchall()
            spells = []

            for row in rows:
                spell_data = dict(row)
                if spell_data.get('classes'):
                    spell_data['classes'] = json.loads(spell_data['classes'])
                else:
                    spell_data['classes'] = []

                spell_def = SpellDefinition.from_dict(spell_data)
                spells.append(spell_def)

                # Cache it
                self._spell_cache[spell_def.id] = spell_def

            return spells

    def get_ritual_spells(self, class_name: Optional[str] = None) -> List[SpellDefinition]:
        """Get all ritual spells, optionally filtered by class."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if class_name:
                cursor.execute("""
                    SELECT s.id, s.name, s.level, s.school, s.casting_time, s.range_value,
                           s.components, s.duration, s.concentration, s.ritual, s.description,
                           s.higher_levels, s.source, s.classes
                    FROM spells s
                    JOIN spell_class_lists scl ON s.id = scl.spell_id
                    WHERE s.ritual = 1 AND scl.class_id = ?
                    ORDER BY s.level, s.name
                """, (class_name.lower(),))
            else:
                cursor.execute("""
                    SELECT id, name, level, school, casting_time, range_value,
                           components, duration, concentration, ritual, description,
                           higher_levels, source, classes
                    FROM spells
                    WHERE ritual = 1
                    ORDER BY level, name
                """)

            rows = cursor.fetchall()
            spells = []

            for row in rows:
                spell_data = dict(row)
                if spell_data.get('classes'):
                    spell_data['classes'] = json.loads(spell_data['classes'])
                else:
                    spell_data['classes'] = []

                spell_def = SpellDefinition.from_dict(spell_data)
                spells.append(spell_def)

                # Cache it
                self._spell_cache[spell_def.id] = spell_def

            return spells

    def add_spell(self, spell: SpellDefinition) -> bool:
        """
        Add a new spell to the registry.

        Args:
            spell: SpellDefinition to add

        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert spell
                cursor.execute("""
                    INSERT OR REPLACE INTO spells
                    (id, name, level, school, casting_time, range_value, components,
                     duration, concentration, ritual, description, higher_levels,
                     source, classes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    spell.id, spell.name, spell.level, spell.school.value,
                    spell.casting_time, spell.range_value, spell.components,
                    spell.duration, spell.concentration, spell.ritual,
                    spell.description, spell.higher_levels, spell.source,
                    json.dumps(spell.classes)
                ))

                # Add to class lists
                cursor.execute("DELETE FROM spell_class_lists WHERE spell_id = ?", (spell.id,))
                for class_name in spell.classes:
                    cursor.execute("""
                        INSERT INTO spell_class_lists (spell_id, class_id)
                        VALUES (?, ?)
                    """, (spell.id, class_name.lower()))

                conn.commit()

                # Update cache
                self._spell_cache[spell.id] = spell

                return True

        except Exception as e:
            print(f"[SpellRegistry] Error adding spell {spell.id}: {e}")
            return False

    def get_spell_count_by_class(self, class_name: str) -> Dict[int, int]:
        """Get count of spells by level for a class."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT s.level, COUNT(*) as count
                FROM spells s
                JOIN spell_class_lists scl ON s.id = scl.spell_id
                WHERE scl.class_id = ?
                GROUP BY s.level
                ORDER BY s.level
            """, (class_name.lower(),))

            return {row[0]: row[1] for row in cursor.fetchall()}

    def search_spells(self,
                     name_filter: Optional[str] = None,
                     school_filter: Optional[SpellSchool] = None,
                     level_filter: Optional[int] = None,
                     class_filter: Optional[str] = None,
                     ritual_only: bool = False,
                     concentration_only: bool = False) -> List[SpellDefinition]:
        """Advanced spell search with multiple filters."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                SELECT DISTINCT s.id, s.name, s.level, s.school, s.casting_time, s.range_value,
                       s.components, s.duration, s.concentration, s.ritual, s.description,
                       s.higher_levels, s.source, s.classes
                FROM spells s
            """

            conditions = []
            params = []

            if class_filter:
                query += " JOIN spell_class_lists scl ON s.id = scl.spell_id"
                conditions.append("scl.class_id = ?")
                params.append(class_filter.lower())

            if name_filter:
                conditions.append("s.name LIKE ?")
                params.append(f"%{name_filter}%")

            if school_filter:
                conditions.append("s.school = ?")
                params.append(school_filter.value)

            if level_filter is not None:
                conditions.append("s.level = ?")
                params.append(level_filter)

            if ritual_only:
                conditions.append("s.ritual = 1")

            if concentration_only:
                conditions.append("s.concentration = 1")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY s.level, s.name"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            spells = []
            for row in rows:
                spell_data = dict(row)
                if spell_data.get('classes'):
                    spell_data['classes'] = json.loads(spell_data['classes'])
                else:
                    spell_data['classes'] = []

                spell_def = SpellDefinition.from_dict(spell_data)
                spells.append(spell_def)

                # Cache it
                self._spell_cache[spell_def.id] = spell_def

            return spells

    def clear_cache(self):
        """Clear all cached spell data."""
        self._spell_cache.clear()
        self._class_spell_cache.clear()

    def get_available_classes(self) -> Set[str]:
        """Get all classes that have spells defined."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT class_id FROM spell_class_lists")
            return {row[0] for row in cursor.fetchall()}

# Singleton instance
spell_registry = SpellRegistry()