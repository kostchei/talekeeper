#test
"""
Warlock test database setup utilities.

Creates comprehensive test databases with Warlock characters at various levels,
complete with spells, invocations, and proper Pact Magic configurations.
"""

import sqlite3
import tempfile
import os
from pathlib import Path
import sys
import json

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database.database_init import DatabaseInitializer


class WarlockTestDatabase:
    """Manages test database creation for Warlock testing."""

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
        """Initialize database with full schema and Warlock test data."""
        # Initialize with full production schema
        initializer = DatabaseInitializer(self.db_path)
        initializer.initialize(force=True)

        # Add Warlock-specific test data
        self._create_warlock_characters()
        self._setup_pact_magic()
        self._setup_eldritch_invocations()
        self._setup_warlock_subclasses()
        self._setup_spellcasting()

    def cleanup(self):
        """Clean up temporary database if needed."""
        if self.is_temp and os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _create_warlock_characters(self):
        """Create Warlock characters at various levels for comprehensive testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Simple character insertions matching actual schema
        characters = [
            ('warlock-1', 'Novice Warlock', 'warlock', 1, 10, 14, 12, 12, 13, 16, 8, 8, 12),
            ('warlock-3', 'Fiend Warlock', 'warlock', 3, 10, 14, 14, 12, 13, 16, 20, 20, 13),
            ('warlock-5', 'Experienced Warlock', 'warlock', 5, 10, 14, 14, 12, 13, 18, 32, 32, 13),
            ('warlock-9', 'Patron Contact', 'warlock', 9, 10, 14, 14, 12, 13, 18, 60, 60, 14),
            ('warlock-12', 'Arcane Adept', 'warlock', 12, 10, 14, 14, 12, 13, 20, 82, 82, 14),
            ('warlock-18', 'Infernal Champion', 'warlock', 18, 10, 14, 16, 12, 13, 20, 125, 125, 15),
            ('warlock-20', 'Eldritch Master', 'warlock', 20, 10, 14, 16, 12, 13, 20, 140, 140, 15),
        ]

        for char_data in characters:
            cursor.execute("""
                INSERT INTO characters (
                    id, name, class_id, level, strength, dexterity, constitution,
                    intelligence, wisdom, charisma, hit_points_current, hit_points_max, armor_class
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, char_data)

        conn.commit()
        conn.close()

    def _setup_pact_magic(self):
        """Set up Pact Magic spell slots based on Warlock level."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Pact Magic slot progression: (level, slots, slot_level)
        pact_progression = {
            'warlock-1': (1, 1),
            'warlock-3': (2, 2),
            'warlock-5': (2, 3),
            'warlock-9': (2, 5),
            'warlock-12': (3, 5),
            'warlock-18': (4, 5),
            'warlock-20': (4, 5),
        }

        for character_id, (slots_max, slot_level) in pact_progression.items():
            # Check if warlock_features table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='warlock_features'
            """)

            if cursor.fetchone():
                cursor.execute("""
                    INSERT OR REPLACE INTO warlock_features (
                        character_id, pact_slots_current, pact_slots_max,
                        pact_slot_level, magical_cunning_used
                    ) VALUES (?, ?, ?, ?, 0)
                """, (character_id, slots_max, slots_max, slot_level))
            else:
                # Store in character_resources if warlock_features doesn't exist
                cursor.execute("""
                    UPDATE characters
                    SET spell_slots_1 = ?, spell_slots_max_1 = ?
                    WHERE id = ?
                """, (slots_max, slots_max, character_id))

        conn.commit()
        conn.close()

    def _setup_eldritch_invocations(self):
        """Assign eldritch invocations to test various combinations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if warlock_invocations table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_invocations'
        """)

        has_invocations_table = cursor.fetchone() is not None

        invocation_assignments = {
            'warlock-1': ['Pact of the Tome'],
            'warlock-3': ['Pact of the Blade', 'Armor of Shadows', 'Eldritch Mind'],
            'warlock-5': ['Pact of the Blade', 'Thirsting Blade', 'Eldritch Smite', 'Ascendant Step', 'Gift of the Depths'],
            'warlock-9': ['Pact of the Chain', 'Investment of the Chain Master', 'Lifedrinker', 'Visions of Distant Realms', 'Whispers of the Grave', 'Gift of the Protectors', 'Gaze of Two Minds'],
            'warlock-12': ['Pact of the Blade', 'Thirsting Blade', 'Devouring Blade', 'Lifedrinker', 'Eldritch Smite', 'Eldritch Mind', 'Fiendish Vigor', 'Mask of Many Faces'],
            'warlock-18': ['Pact of the Blade', 'Thirsting Blade', 'Devouring Blade', 'Lifedrinker', 'Eldritch Smite', 'Eldritch Mind', 'Master of Myriad Forms', 'One with Shadows', 'Visions of Distant Realms', 'Witch Sight'],
            'warlock-20': ['Pact of the Blade', 'Thirsting Blade', 'Devouring Blade', 'Lifedrinker', 'Witch Sight', 'Eldritch Smite', 'Eldritch Mind', 'Visions of Distant Realms', 'Master of Myriad Forms', 'One with Shadows'],
        }

        for character_id, invocations in invocation_assignments.items():
            for invocation in invocations:
                if has_invocations_table:
                    cursor.execute("""
                        INSERT INTO warlock_invocations (character_id, invocation_id, invocation_name)
                        VALUES (?, ?, ?)
                    """, (character_id, invocation.lower().replace(' ', '_'), invocation))
                else:
                    # Store as character features if table doesn't exist
                    cursor.execute("""
                        INSERT INTO character_features (character_id, feature_name, feature_type, source)
                        VALUES (?, ?, ?, ?)
                    """, (character_id, invocation, 'eldritch_invocation', 'Warlock'))

        conn.commit()
        conn.close()

    def _setup_warlock_subclasses(self):
        """Assign Warlock subclasses."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # All level 3+ characters are Fiend patrons
        subclass_data = [
            ('warlock-3', 'warlock', 'fiend', 3),
            ('warlock-5', 'warlock', 'fiend', 5),
            ('warlock-9', 'warlock', 'fiend', 9),
            ('warlock-12', 'warlock', 'fiend', 12),
            ('warlock-18', 'warlock', 'fiend', 18),
            ('warlock-20', 'warlock', 'fiend', 20),
        ]

        for character_id, class_id, subclass_id, level in subclass_data:
            cursor.execute("""
                INSERT OR IGNORE INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, ?, ?, ?)
            """, (character_id, class_id, subclass_id, level))

        # Add Fiend patron features
        fiend_features = [
            ('warlock-3', 'Dark Ones Blessing', 'patron_feature'),
            ('warlock-5', 'Dark Ones Blessing', 'patron_feature'),
            ('warlock-9', 'Dark Ones Blessing', 'patron_feature'),
            ('warlock-9', 'Dark Ones Own Luck', 'patron_feature'),
            ('warlock-12', 'Dark Ones Blessing', 'patron_feature'),
            ('warlock-12', 'Dark Ones Own Luck', 'patron_feature'),
            ('warlock-12', 'Fiendish Resilience', 'patron_feature'),
            ('warlock-18', 'Dark Ones Blessing', 'patron_feature'),
            ('warlock-18', 'Dark Ones Own Luck', 'patron_feature'),
            ('warlock-18', 'Fiendish Resilience', 'patron_feature'),
            ('warlock-18', 'Hurl Through Hell', 'patron_feature'),
            ('warlock-20', 'Dark Ones Blessing', 'patron_feature'),
            ('warlock-20', 'Dark Ones Own Luck', 'patron_feature'),
            ('warlock-20', 'Fiendish Resilience', 'patron_feature'),
            ('warlock-20', 'Hurl Through Hell', 'patron_feature'),
        ]

        for character_id, feature_name, feature_type in fiend_features:
            cursor.execute("""
                INSERT INTO character_features (character_id, feature_name, feature_type, source)
                VALUES (?, ?, ?, ?)
            """, (character_id, feature_name, feature_type, 'Fiend Patron'))

        conn.commit()
        conn.close()

    def _setup_spellcasting(self):
        """Set up spellcasting data for Warlock characters."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        spellcasting_data = [
            ('warlock-1', 'Charisma', 2, 11, 5, json.dumps({'0': ['eldritch_blast', 'mage_hand']}), json.dumps(['charm_person', 'hex'])),
            ('warlock-3', 'Charisma', 2, 12, 5, json.dumps({'0': ['eldritch_blast', 'chill_touch']}), json.dumps(['burning_hands', 'command', 'hex', 'scorching_ray'])),
            ('warlock-5', 'Charisma', 3, 13, 6, json.dumps({'0': ['eldritch_blast', 'prestidigitation', 'minor_illusion']}), json.dumps(['hex', 'charm_person', 'counterspell', 'fireball', 'fly', 'hypnotic_pattern'])),
            ('warlock-9', 'Charisma', 3, 15, 7, json.dumps({'0': ['eldritch_blast', 'mage_hand', 'prestidigitation']}), json.dumps(['hex', 'counterspell', 'fireball', 'dimension_door', 'hold_monster', 'contact_other_plane', 'geas', 'insect_plague', 'mislead', 'scrying'])),
            ('warlock-12', 'Charisma', 4, 16, 8, json.dumps({'0': ['eldritch_blast', 'mage_hand', 'prestidigitation', 'poison_spray']}), json.dumps(['hex', 'counterspell', 'dimension_door', 'hold_monster', 'scrying', 'banishment', 'fireball', 'fly', 'suggestion', 'invisibility', 'misty_step'])),
            ('warlock-18', 'Charisma', 4, 17, 9, json.dumps({'0': ['eldritch_blast', 'mage_hand', 'prestidigitation', 'poison_spray']}), json.dumps(['hex', 'counterspell', 'dimension_door', 'hold_monster', 'scrying', 'banishment', 'fireball', 'fly', 'suggestion', 'invisibility', 'misty_step', 'wall_of_fire', 'etherealness', 'finger_of_death'])),
            ('warlock-20', 'Charisma', 4, 17, 9, json.dumps({'0': ['eldritch_blast', 'mage_hand', 'prestidigitation', 'poison_spray']}), json.dumps(['hex', 'counterspell', 'dimension_door', 'hold_monster', 'scrying', 'banishment', 'fireball', 'fly', 'suggestion', 'invisibility', 'misty_step', 'wall_of_fire', 'foresight', 'power_word_kill'])),
        ]

        for character_id, ability, cantrips_known, spell_save_dc, spell_attack, known_spells, prepared_spells in spellcasting_data:
            cursor.execute("""
                INSERT OR REPLACE INTO character_spellcasting (
                    character_id, spellcasting_class, spellcasting_ability,
                    cantrips_known, spell_save_dc, spell_attack_bonus,
                    known_spells, prepared_spells
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (character_id, 'warlock', ability, cantrips_known, spell_save_dc, spell_attack, known_spells, prepared_spells))

        # Add Mystic Arcanum spells for high-level warlocks
        arcanum_data = [
            ('warlock-12', 'circle_of_death', 6),
            ('warlock-18', 'circle_of_death', 6),
            ('warlock-18', 'finger_of_death', 7),
            ('warlock-18', 'demiplane', 8),
            ('warlock-20', 'circle_of_death', 6),
            ('warlock-20', 'finger_of_death', 7),
            ('warlock-20', 'demiplane', 8),
            ('warlock-20', 'foresight', 9),
        ]

        # Check if mystic_arcanum table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            for character_id, spell_name, spell_level in arcanum_data:
                cursor.execute("""
                    INSERT INTO mystic_arcanum (character_id, spell_name, spell_level, used)
                    VALUES (?, ?, ?, 0)
                """, (character_id, spell_name, spell_level))
        else:
            # Store as character features if table doesn't exist
            for character_id, spell_name, spell_level in arcanum_data:
                cursor.execute("""
                    INSERT INTO character_features (character_id, feature_name, feature_type, source)
                    VALUES (?, ?, ?, ?)
                """, (character_id, f'Mystic Arcanum: {spell_name}', f'mystic_arcanum_{spell_level}', 'Warlock'))

        conn.commit()
        conn.close()

    def get_character_ids(self):
        """Get all Warlock character IDs for testing."""
        return {
            'level_1': 'warlock-1',
            'level_3_fiend': 'warlock-3',
            'level_5': 'warlock-5',
            'level_9_contact': 'warlock-9',
            'level_12_arcanum': 'warlock-12',
            'level_18_infernal': 'warlock-18',
            'level_20_master': 'warlock-20',
        }

    def damage_character(self, character_id, damage_amount):
        """Damage a character for healing/temp HP testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters
            SET hit_points_current = hit_points_current - ?
            WHERE id = ?
        """, (damage_amount, character_id))

        conn.commit()
        conn.close()

    def use_pact_slot(self, character_id):
        """Use a pact magic slot."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if warlock_features table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = pact_slots_current - 1
                WHERE character_id = ? AND pact_slots_current > 0
            """, (character_id,))
        else:
            cursor.execute("""
                UPDATE characters
                SET spell_slots_1 = spell_slots_1 - 1
                WHERE id = ? AND spell_slots_1 > 0
            """, (character_id,))

        conn.commit()
        conn.close()

    def reset_resources(self, character_id, rest_type='long'):
        """Reset limited-use resources for testing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Reset pact slots (short or long rest)
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = pact_slots_max
                WHERE character_id = ?
            """, (character_id,))

            if rest_type == 'long':
                cursor.execute("""
                    UPDATE warlock_features
                    SET magical_cunning_used = 0
                    WHERE character_id = ?
                """, (character_id,))

        # Reset Mystic Arcanum (long rest only)
        if rest_type == 'long':
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='mystic_arcanum'
            """)

            if cursor.fetchone():
                cursor.execute("""
                    UPDATE mystic_arcanum
                    SET used = 0
                    WHERE character_id = ?
                """, (character_id,))

        conn.commit()
        conn.close()


def create_warlock_test_db():
    """Convenience function to create a Warlock test database."""
    return WarlockTestDatabase()


if __name__ == '__main__':
    # Demo usage
    with create_warlock_test_db() as db_path:
        print(f"Created test database at: {db_path}")

        # Verify character creation
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, level, class_id FROM characters WHERE class_id = 'warlock'")
        warlocks = cursor.fetchall()

        print(f"Created {len(warlocks)} Warlock characters:")
        for warlock in warlocks:
            print(f"  {warlock[0]}: {warlock[1]} (Level {warlock[2]})")

        conn.close()
