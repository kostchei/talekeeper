# core
# core
"""
Subclass Manager Service for TaleKeeper

Handles all subclass-related operations:
- Subclass selection during level-up
- Feature progression
- Mechanical effects of subclass features
- Integration with action cards and combat
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SubclassLevel(Enum):
    """Standard subclass progression levels."""
    SELECTION = 3
    FIRST_UPGRADE = 7
    SECOND_UPGRADE = 10
    THIRD_UPGRADE = 15
    FINAL_UPGRADE = 18


@dataclass
class SubclassFeature:
    """Represents a subclass feature."""
    name: str
    description: str
    level: int
    mechanics: Dict[str, Any]
    action_type: Optional[str] = None
    uses_per_rest: Optional[int] = None
    rest_type: Optional[str] = None


class SubclassManager:
    """Manages subclass selection, features, and mechanics."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._run_migration()
    
    def _run_migration(self):
        """Ensure subclass tables exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                try:
                    with open('database/migrations/004_add_subclass_system.sql', 'r') as f:
                        conn.executescript(f.read())
                except FileNotFoundError:
                    print("[SubclassManager] Migration note: missing 004_add_subclass_system.sql")
                except Exception as migration_error:
                    print(f"[SubclassManager] Migration note: {migration_error}")
                self._ensure_class_subclass_support(conn)
                conn.commit()
        except Exception as e:
            print(f"[SubclassManager] Migration note: {e}")
    
    def _ensure_class_subclass_support(self, conn):
        """Create tables and backfill data for per-class subclass tracking."""
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS character_subclasses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                class_id TEXT NOT NULL,
                subclass_id TEXT NOT NULL,
                class_level INTEGER NOT NULL DEFAULT 3,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(character_id, class_id),
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                FOREIGN KEY (subclass_id) REFERENCES subclasses(id)
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_character_subclasses_character
            ON character_subclasses(character_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_character_subclasses_class
            ON character_subclasses(class_id)
            """
        )

        cursor.execute(
            """
            SELECT id, class_id, subclass_id, level
            FROM characters
            WHERE COALESCE(subclass_id, '') <> ''
            """
        )

        for char_id, primary_class, legacy_subclass, total_level in cursor.fetchall():
            if not legacy_subclass:
                continue

            class_id = (primary_class or '').strip().lower()
            if not class_id:
                cursor.execute(
                    "SELECT class_id FROM subclasses WHERE id = ?",
                    (legacy_subclass,)
                )
                row = cursor.fetchone()
                class_id = (row[0].strip().lower() if row and row[0] else '')

            if not class_id:
                continue

            class_level = total_level or 3
            if class_level < 3:
                class_level = 3

            cursor.execute(
                """
                INSERT OR IGNORE INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, ?, ?, ?)
                """,
                (char_id, class_id, legacy_subclass, class_level)
            )
    def get_available_subclasses(self, class_id: str) -> List[Dict[str, Any]]:
        """Get all available subclasses for a class."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, description, flavor_text, selection_level
                FROM subclasses
                WHERE LOWER(class_id) = LOWER(?)
                ORDER BY name
            """, (class_id,))

            subclasses = []
            for row in cursor:
                subclasses.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'flavor_text': row['flavor_text'],
                    'selection_level': row['selection_level']
                })

            # Apply release subclass filtering if enabled
            from core.config import config
            if config.features.release_subclass_filter and config.features.release_subclasses:
                class_lower = class_id.lower()
                if class_lower in config.features.release_subclasses:
                    allowed_subclasses = config.features.release_subclasses[class_lower]
                    # Filter to only include allowed subclasses
                    subclasses = [sc for sc in subclasses if sc['id'] in allowed_subclasses]

            return subclasses


    def get_character_subclass(self, character_id: str, class_id: str) -> Optional[str]:
        """Return the subclass id for a given character/class pairing."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT subclass_id
                FROM character_subclasses
                WHERE character_id = ? AND LOWER(class_id) = LOWER(?)
                """,
                (character_id, class_id)
            )
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]

            cursor.execute(
                """
                SELECT class_id, subclass_id
                FROM characters
                WHERE id = ?
                """,
                (character_id,)
            )
            legacy = cursor.fetchone()
            if not legacy or not legacy[1]:
                return None

            legacy_class = (legacy[0] or '').strip().lower()
            if not class_id:
                return legacy[1]

            if legacy_class and legacy_class == class_id.strip().lower():
                return legacy[1]

            return None
    def select_subclass(self, character_id: str, subclass_id: str, class_level: Optional[int] = None) -> bool:
        """Assign a subclass to a character for its associated class."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, class_id, selection_level
                    FROM subclasses
                    WHERE id = ?
                    """,
                    (subclass_id,)
                )
                subclass_row = cursor.fetchone()
                if not subclass_row:
                    print(f"[SubclassManager] Unknown subclass: {subclass_id}")
                    return False

                class_id = (subclass_row["class_id"] or '').strip().lower()
                if not class_id:
                    print(f"[SubclassManager] Subclass {subclass_id} missing class association")
                    return False

                cursor.execute(
                    """
                    SELECT subclass_id
                    FROM character_subclasses
                    WHERE character_id = ? AND LOWER(class_id) = ?
                    """,
                    (character_id, class_id)
                )
                existing = cursor.fetchone()
                if existing and existing[0]:
                    if existing[0] == subclass_id:
                        target_level = class_level or subclass_row["selection_level"] or 3
                        if target_level < subclass_row["selection_level"]:
                            target_level = subclass_row["selection_level"]
                        self._grant_subclass_features(cursor, character_id, subclass_id, target_level)
                        conn.commit()
                        return True

                    print(f"[SubclassManager] Character already has subclass {existing[0]} for class {class_id}")
                    return False

                if class_level is None:
                    cursor.execute(
                        """
                        SELECT level FROM character_class_levels
                        WHERE character_id = ? AND LOWER(class_name) = ?
                        """,
                        (character_id, class_id)
                    )
                    level_row = cursor.fetchone()
                    if level_row and level_row[0]:
                        class_level = level_row[0]
                    else:
                        cursor.execute(
                            """
                            SELECT level, class_id
                            FROM characters
                            WHERE id = ?
                            """,
                            (character_id,)
                        )
                        primary_row = cursor.fetchone()
                        if primary_row and primary_row[0] and (primary_row[1] or '').strip().lower() == class_id:
                            class_level = primary_row[0]

                if class_level is None:
                    class_level = max(subclass_row["selection_level"], 3)

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                    VALUES (?, ?, ?, ?)
                    """,
                    (character_id, class_id, subclass_id, class_level)
                )

                cursor.execute(
                    """
                    SELECT class_id, subclass_id
                    FROM characters
                    WHERE id = ?
                    """,
                    (character_id,)
                )
                primary_row = cursor.fetchone()
                primary_class = (primary_row["class_id"] or '').strip().lower() if primary_row and primary_row["class_id"] else ''
                current_primary_subclass = primary_row["subclass_id"] if primary_row else None

                if not current_primary_subclass or primary_class == class_id:
                    cursor.execute(
                        """
                        UPDATE characters
                        SET subclass_id = ?, updated_at = datetime('now')
                        WHERE id = ?
                        """,
                        (subclass_id, character_id)
                    )

                self._grant_subclass_features(cursor, character_id, subclass_id, class_level)

                conn.commit()
                print(f"[SubclassManager] Assigned subclass {subclass_id} to character {character_id} for class {class_id}")
                return True

        except Exception as e:
            print(f"[SubclassManager] Error selecting subclass: {e}")
            return False
    def _grant_subclass_features(self, cursor, character_id: str, subclass_id: str, up_to_level: int):
        """Grant subclass features up to specified level."""
        cursor.execute("""
            SELECT level, feature_name, description, mechanics, action_type
            FROM subclass_features
            WHERE subclass_id = ? AND level <= ?
            ORDER BY level
        """, (subclass_id, up_to_level))
        
        for row in cursor:
            # Add to character_features table
            cursor.execute("""
                INSERT OR IGNORE INTO character_features 
                (character_id, feature_name, feature_type, description, level_gained)
                VALUES (?, ?, ?, ?, ?)
            """, (character_id, row[1], row[4] or 'passive', row[2], row[0]))
            
            # Apply immediate mechanical effects
            self._apply_feature_mechanics(cursor, character_id, row[1], row[3])
    
    def _apply_feature_mechanics(self, cursor, character_id: str, feature_name: str, mechanics_json: str):
        """Apply mechanical effects of a feature."""
        if not mechanics_json:
            return
        
        try:
            mechanics = json.loads(mechanics_json)
            
            # Handle critical range modifications (Champion)
            if 'critical_range_min' in mechanics:
                cursor.execute("""
                    INSERT INTO character_combat_state (character_id, critical_range_min)
                    VALUES (?, ?)
                    ON CONFLICT(character_id) DO UPDATE SET
                        critical_range_min = ?
                """, (character_id, mechanics['critical_range_min'], mechanics['critical_range_min']))
            
            # Handle skill proficiencies (Gladiator, Assassin)
            if 'skills' in mechanics:
                for skill in mechanics['skills']:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_skills (character_id, skill_name, proficient)
                        VALUES (?, ?, 1)
                    """, (character_id, skill))
            
            # Handle tool proficiencies (Assassin)
            if 'tool_proficiencies' in mechanics:
                for tool in mechanics['tool_proficiencies']:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies (character_id, proficiency_type, proficiency_name)
                        VALUES (?, 'tool', ?)
                    """, (character_id, tool))
                    
        except json.JSONDecodeError as e:
            print(f"[SubclassManager] Error parsing mechanics for {feature_name}: {e}")
    
    def get_subclass_features(self, subclass_id: str, level: int) -> List[SubclassFeature]:
        """Get all features for a subclass up to specified level."""
        features = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT feature_name, description, level, mechanics, 
                       action_type, uses_per_rest, rest_type
                FROM subclass_features
                WHERE subclass_id = ? AND level <= ?
                ORDER BY level
            """, (subclass_id, level))
            
            for row in cursor:
                mechanics = {}
                if row['mechanics']:
                    try:
                        mechanics = json.loads(row['mechanics'])
                    except:
                        pass
                
                features.append(SubclassFeature(
                    name=row['feature_name'],
                    description=row['description'],
                    level=row['level'],
                    mechanics=mechanics,
                    action_type=row['action_type'],
                    uses_per_rest=row['uses_per_rest'],
                    rest_type=row['rest_type']
                ))
        
        return features
    
    def check_subclass_requirement(self, character_id: str) -> Tuple[bool, str]:
        """Check if character needs to select a subclass."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT level, class_id, subclass_id
                FROM characters
                WHERE id = ?
            """, (character_id,))
            
            row = cursor.fetchone()
            if not row:
                return False, ""
            
            level, class_id, subclass_id = row
            
            # Check if approaching subclass selection level without a subclass
            if level >= 2 and not subclass_id:
                # Next level would be 3 (subclass selection)
                return True, class_id
            
            return False, ""
    
    def update_features_for_level(self, character_id: str, new_level: int, class_id: Optional[str] = None):
        """Update subclass features when a character gains a level."""
        if new_level < 1:
            return

        target_class = (class_id or '').strip().lower()

        if not target_class:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT class_id
                    FROM character_subclasses
                    WHERE character_id = ?
                    ORDER BY class_level DESC
                    LIMIT 1
                    """,
                    (character_id,)
                )
                row = cursor.fetchone()
                if row and row[0]:
                    target_class = (row[0] or '').strip().lower()
                else:
                    cursor.execute(
                        """
                        SELECT class_id
                        FROM characters
                        WHERE id = ?
                        """,
                        (character_id,)
                    )
                    fallback = cursor.fetchone()
                    target_class = (fallback[0] or '').strip().lower() if fallback and fallback[0] else ''

        if not target_class:
            return

        self.update_features_for_class(character_id, target_class, new_level)

    def update_features_for_class(self, character_id: str, class_id: str, class_level: int):
        """Ensure subclass features are granted up to the specified class level."""
        subclass_id = self.get_character_subclass(character_id, class_id)
        if not subclass_id:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            self._grant_subclass_features(cursor, character_id, subclass_id, class_level)
            conn.commit()
    def has_feature(self, character_id: str, feature_name: str) -> bool:
        """Check if character has a specific subclass feature."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 1 FROM character_features
                WHERE character_id = ? AND feature_name = ?
            """, (character_id, feature_name))
            
            return cursor.fetchone() is not None
    
    def get_feature_uses(self, character_id: str, feature_name: str) -> Tuple[int, int]:
        """Get current and max uses for a resource-based feature."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check character_resources table for tracking
            cursor.execute("""
                SELECT current_uses, max_uses
                FROM character_resources
                WHERE character_id = ? AND resource_name = ?
            """, (character_id, feature_name))
            
            row = cursor.fetchone()
            if row:
                return row[0], row[1]
            
            return 0, 0
    
    def use_feature(self, character_id: str, feature_name: str) -> bool:
        """Use a resource-based subclass feature."""
        current, max_uses = self.get_feature_uses(character_id, feature_name)
        
        if current <= 0:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE character_resources
                SET current_uses = current_uses - 1
                WHERE character_id = ? AND resource_name = ?
            """, (character_id, feature_name))
            
            conn.commit()
            return True
    
    def apply_combat_modifiers(self, character_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply subclass-specific combat modifiers."""
        modifiers = {}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            class_hint = (context.get('class_id') or context.get('class') or '').strip().lower()
            subclass_id = self.get_character_subclass(character_id, class_hint) if class_hint else None

            cursor.execute(
                """
                SELECT level, class_id, subclass_id, hit_points_current, hit_points_max
                FROM characters
                WHERE id = ?
                """,
                (character_id,)
            )
            char_row = cursor.fetchone()
            if not char_row:
                return modifiers

            total_level, primary_class, primary_subclass, current_hp, max_hp = char_row

            if not subclass_id:
                if primary_subclass:
                    subclass_id = primary_subclass
                    class_hint = (primary_class or '').strip().lower()
                else:
                    return modifiers

            class_level = None
            if class_hint:
                cursor.execute(
                    """
                    SELECT level
                    FROM character_class_levels
                    WHERE character_id = ? AND LOWER(class_name) = ?
                    """,
                    (character_id, class_hint)
                )
                class_level_row = cursor.fetchone()
                if class_level_row and class_level_row[0]:
                    class_level = class_level_row[0]

            if class_level is None:
                class_level = total_level

            subclass_key = subclass_id.strip().lower()

            if subclass_key == 'champion':
                if class_level >= 15:
                    modifiers['critical_range_min'] = 18
                elif class_level >= 3:
                    modifiers['critical_range_min'] = 19
            elif subclass_key == 'gladiator' and class_level >= 15:
                if current_hp <= max_hp // 2:
                    modifiers['damage_resistance'] = ['all_except_psychic']
            elif subclass_key == 'assassin' and class_level >= 3:
                if context.get('target_has_not_acted'):
                    modifiers['advantage'] = True
                if context.get('target_surprised'):
                    modifiers['auto_crit'] = True
            elif subclass_key == 'thief' and class_level >= 3:
                modifiers['bonus_action_use_object'] = True

        return modifiers
# Singleton instance
subclass_manager = SubclassManager()











