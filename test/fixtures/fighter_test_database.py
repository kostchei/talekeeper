# test
"""
Fighter test database setup utilities.

Creates comprehensive test databases with Fighter characters at various levels,
complete with equipment, features, and proper fighting style configurations.
"""

import sqlite3
import tempfile
import os
from pathlib import Path
import sys

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database.database_init import DatabaseInitializer


class FighterTestDatabase:
    """Manages test database creation for Fighter testing."""

    def __init__(self, db_path=None):
        """Initialize with optional database path."""
        if db_path is None:
            self.temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            self.temp_file.close()
            self.db_path = self.temp_file.name
            self.is_temp = True
        else:
            self.db_path = db_path
            self.is_temp = False

    def __enter__(self):
        """Context manager entry."""
        self.setup_database()
        return self.db_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def setup_database(self):
        """Initialize database with full schema and Fighter test data."""
        # Initialize with full production schema
        initializer = DatabaseInitializer(self.db_path)
        initializer.initialize(force=True)

        # Add Fighter-specific test data
        self._create_fighter_characters()
        self._setup_fighter_equipment()
        self._configure_fighting_styles()
        self._setup_combat_state()

    def cleanup(self):
        """Clean up temporary database if needed."""
        if self.is_temp and os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _create_fighter_characters(self):
        """Create Fighter characters at various levels for comprehensive testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Simple character insertions matching actual schema
        characters = [
            ('fighter-1', 'Rookie Fighter', 'fighter', 1, 16, 14, 15, 10, 12, 13, 12, 12, 16),
            ('fighter-2', 'Veteran Fighter', 'fighter', 2, 16, 14, 15, 10, 12, 13, 19, 19, 16),
            ('fighter-3', 'Champion Fighter', 'fighter', 3, 16, 14, 16, 10, 12, 13, 30, 30, 17),
            ('fighter-5', 'Seasoned Fighter', 'fighter', 5, 18, 14, 16, 10, 12, 13, 45, 45, 17),
            ('fighter-9', 'Tactical Master', 'fighter', 9, 18, 14, 16, 10, 12, 13, 85, 85, 18),
            ('fighter-10', 'Heroic Champion', 'fighter', 10, 18, 14, 16, 10, 12, 13, 95, 95, 18),
            ('fighter-15', 'Legendary Survivor', 'fighter', 15, 20, 14, 18, 10, 12, 13, 80, 160, 19),
        ]

        for char_data in characters:
            cursor.execute("""
                INSERT INTO characters (
                    id, name, class_id, level, strength, dexterity, constitution,
                    intelligence, wisdom, charisma, hit_points_current, hit_points_max, armor_class
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, char_data)

        # Set appropriate resource values
        cursor.execute("UPDATE characters SET second_wind_uses_current = 1, second_wind_uses_max = 1 WHERE id LIKE 'fighter-%'")
        cursor.execute("UPDATE characters SET action_surge_uses_current = 1, action_surge_uses_max = 1 WHERE level >= 2 AND id LIKE 'fighter-%'")
        cursor.execute("UPDATE characters SET indomitable_uses_current = 1, indomitable_uses_max = 1 WHERE level >= 9 AND id LIKE 'fighter-%'")

        # Add subclass assignments
        subclass_data = [
            ('fighter-3', 'fighter', 'champion', 3),
            ('fighter-5', 'fighter', 'champion', 5),
            ('fighter-9', 'fighter', 'champion', 9),
            ('fighter-10', 'fighter', 'champion', 10),
            ('fighter-15', 'fighter', 'champion', 15),
        ]

        for character_id, class_id, subclass_id, level in subclass_data:
            cursor.execute("""
                INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, ?, ?, ?)
            """, (character_id, class_id, subclass_id, level))

        conn.commit()
        conn.close()

    def _setup_fighter_equipment(self):
        """Equip Fighter characters with appropriate weapons and armor."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Equipment assignments per character
        equipment_loadouts = {
            'fighter-1': [
                ('Chain Mail', 1, 1),  # AC 16
                ('Longsword', 1, 1),   # Versatile, Sap mastery
                ('Shield', 1, 1),      # +2 AC
            ],
            'fighter-2': [
                ('Chain Mail', 1, 1),
                ('Battleaxe', 1, 1),   # Versatile, Topple mastery
                ('Javelin', 5, 1),     # Ranged option
            ],
            'fighter-3': [
                ('Studded Leather', 1, 1),  # For Dueling style
                ('Rapier', 1, 1),           # Finesse, Vex mastery
                ('Dagger', 2, 1),           # Backup finesse
            ],
            'fighter-5': [
                ('Chain Mail', 1, 1),
                ('Longsword', 1, 1),
                ('Longbow', 1, 1),     # Slow mastery
                ('Arrow', 20, 0),
            ],
            'fighter-9': [
                ('Plate', 1, 1),       # AC 18
                ('Greatsword', 1, 1),  # Two-handed, Graze mastery
                ('+1 Greataxe', 1, 0), # Magical weapon variant
            ],
            'fighter-10': [
                ('Plate', 1, 1),
                ('Longsword', 1, 1),
                ('Shield', 1, 1),
                ('Handaxe', 2, 1),     # Light, Vex mastery
            ],
            'fighter-15': [
                ('+2 Plate', 1, 1),    # AC 20
                ('+1 Greatsword', 1, 1),
                ('Heavy Crossbow', 1, 0),
                ('Crossbow Bolt', 20, 0),
            ],
        }

        for character_id, items in equipment_loadouts.items():
            for item_name, quantity, equipped in items:
                cursor.execute("""
                    INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
                    VALUES (?, ?, ?, ?)
                """, (character_id, item_name, quantity, equipped))

        conn.commit()
        conn.close()

    def _configure_fighting_styles(self):
        """Assign fighting styles to test various combinations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fighting_styles = {
            'fighter-1': 'Defense',        # +1 AC with armor
            'fighter-2': 'Protection',     # Reaction defense
            'fighter-3': 'Dueling',        # +2 damage one-handed
            'fighter-5': 'Archery',        # +2 attack ranged
            'fighter-9': 'Great Weapon Fighting',  # Treat 1s,2s as 3s
            'fighter-10': 'Two-Weapon Fighting',   # Add ability mod to off-hand
            'fighter-15': 'Great Weapon Fighting', # High-level GWF user
        }

        for character_id, style in fighting_styles.items():
            cursor.execute("""
                INSERT INTO character_features (character_id, feature_name, feature_type, source)
                VALUES (?, ?, ?, ?)
            """, (character_id, style, 'fighting_style', 'Fighter'))

        # Add weapon masteries for Fighter characters
        mastery_assignments = [
            ('fighter-1', 'Longsword', 'Sap'),
            ('fighter-2', 'Battleaxe', 'Topple'),
            ('fighter-3', 'Rapier', 'Vex'),
            ('fighter-5', 'Longsword', 'Sap'),
            ('fighter-5', 'Longbow', 'Slow'),
            ('fighter-9', 'Greatsword', 'Graze'),
            ('fighter-10', 'Longsword', 'Sap'),
            ('fighter-10', 'Handaxe', 'Vex'),
            ('fighter-15', '+1 Greatsword', 'Graze'),
        ]

        for character_id, weapon, mastery in mastery_assignments:
            cursor.execute("""
                INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_name)
                VALUES (?, ?, ?)
            """, (character_id, weapon, mastery))

        conn.commit()
        conn.close()

    def _setup_combat_state(self):
        """Initialize combat state tables for testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create combat state entries for characters
        characters = ['fighter-1', 'fighter-2', 'fighter-3', 'fighter-5',
                     'fighter-9', 'fighter-10', 'fighter-15']

        for character_id in characters:
            cursor.execute("""
                INSERT INTO character_combat_state (
                    character_id, studied_target_id, last_miss_turn,
                    heroic_warrior_active, survivor_active, last_attack_missed,
                    critical_range_min
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (character_id, None, 0, 0, 0, 0, 20))

        # Set Champion critical range to 19-20 for level 3+ Champions
        champion_characters = ['fighter-3', 'fighter-5', 'fighter-9', 'fighter-10', 'fighter-15']
        for character_id in champion_characters:
            cursor.execute("""
                UPDATE character_combat_state
                SET critical_range_min = 19
                WHERE character_id = ?
            """, (character_id,))

        conn.commit()
        conn.close()

    def get_character_ids(self):
        """Get all Fighter character IDs for testing."""
        return {
            'level_1': 'fighter-1',
            'level_2': 'fighter-2',
            'level_3_champion': 'fighter-3',
            'level_5': 'fighter-5',
            'level_9_tactical': 'fighter-9',
            'level_10_heroic': 'fighter-10',
            'level_15_survivor': 'fighter-15',
        }

    def setup_damaged_character(self, character_id, damage_amount):
        """Damage a character for healing testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters
            SET hit_points_current = hit_points_current - ?
            WHERE id = ?
        """, (damage_amount, character_id))

        conn.commit()
        conn.close()

    def reset_resources(self, character_id):
        """Reset all limited-use resources for testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters
            SET second_wind_uses_current = second_wind_uses_max,
                action_surge_uses_current = action_surge_uses_max,
                indomitable_uses_current = indomitable_uses_max,
                inspiration_uses_current = inspiration_uses_max
            WHERE id = ?
        """, (character_id,))

        # Reset combat state flags
        cursor.execute("""
            UPDATE character_combat_state
            SET heroic_warrior_active = 0,
                survivor_active = 0,
                last_attack_missed = 0,
                last_miss_turn = 0
            WHERE character_id = ?
        """, (character_id,))

        conn.commit()
        conn.close()


def create_fighter_test_db():
    """Convenience function to create a Fighter test database."""
    return FighterTestDatabase()


if __name__ == '__main__':
    # Demo usage
    with create_fighter_test_db() as db_path:
        print(f"Created test database at: {db_path}")

        # Verify character creation
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, level, class_id FROM characters WHERE class_id = 'fighter'")
        fighters = cursor.fetchall()

        print(f"Created {len(fighters)} Fighter characters:")
        for fighter in fighters:
            print(f"  {fighter[0]}: {fighter[1]} (Level {fighter[2]})")

        conn.close()