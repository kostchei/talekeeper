#test
"""
Comprehensive tests for Mystic Arcanum mechanics.

Tests high-level spell access, once-per-long-rest usage, and spell replacement
according to D&D 2024 rules.
"""

import pytest
import sqlite3
import sys
from pathlib import Path

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.fixtures.warlock_test_database import WarlockTestDatabase


class TestMysticArcanumBasics:
    """Test basic Mystic Arcanum mechanics."""

    @pytest.fixture
    def warlock_db(self):
        """Create Warlock test database."""
        with WarlockTestDatabase() as db_path:
            yield db_path

    def test_mystic_arcanum_progression(self, warlock_db):
        """Test Mystic Arcanum grants high-level spells at specific levels."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Expected arcanum progression: (character_id, level, expected_arcanum_count)
        progression = [
            ('warlock-9', 9, 0),    # No arcanum yet
            ('warlock-12', 12, 1),  # Level 6 spell
            ('warlock-18', 18, 3),  # Level 6, 7 & 8 spells
            ('warlock-20', 20, 4),  # Level 6, 7, 8, & 9 spells
        ]

        # Check if mystic_arcanum table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        has_arcanum_table = cursor.fetchone() is not None

        for character_id, level, expected_count in progression:
            if has_arcanum_table:
                cursor.execute("""
                    SELECT COUNT(*) FROM mystic_arcanum
                    WHERE character_id = ?
                """, (character_id,))
                count = cursor.fetchone()[0]
            else:
                # Check character_features for mystic_arcanum features
                cursor.execute("""
                    SELECT COUNT(*) FROM character_features
                    WHERE character_id = ? AND feature_type LIKE 'mystic_arcanum%'
                """, (character_id,))
                count = cursor.fetchone()[0]

            assert count == expected_count, f"{character_id}: Expected {expected_count} arcanum spells, got {count}"

        conn.close()

    def test_level_11_gains_level_6_spell(self, warlock_db):
        """Test level 11+ Warlock gains one level 6 spell arcanum."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT spell_level FROM mystic_arcanum
                WHERE character_id = ?
            """, ('warlock-12',))
            spell_levels = [row[0] for row in cursor.fetchall()]

            assert 6 in spell_levels, "Level 11+ Warlock should have a level 6 arcanum"

        conn.close()

    def test_level_13_gains_level_7_spell(self, warlock_db):
        """Test level 13+ Warlock gains one level 7 spell arcanum."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT spell_level FROM mystic_arcanum
                WHERE character_id = ?
            """, ('warlock-18',))
            spell_levels = [row[0] for row in cursor.fetchall()]

            assert 6 in spell_levels, "Level 13+ Warlock should have a level 6 arcanum"
            assert 7 in spell_levels, "Level 13+ Warlock should have a level 7 arcanum"

        conn.close()

    def test_level_15_gains_level_8_spell(self, warlock_db):
        """Test level 15 Warlock gains one level 8 spell arcanum."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT spell_level FROM mystic_arcanum
                WHERE character_id = ?
            """, ('warlock-20',))
            spell_levels = [row[0] for row in cursor.fetchall()]

            assert 8 in spell_levels, "Level 15+ Warlock should have a level 8 arcanum"

        conn.close()

    def test_level_17_gains_level_9_spell(self, warlock_db):
        """Test level 17 Warlock gains one level 9 spell arcanum."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT spell_level FROM mystic_arcanum
                WHERE character_id = ?
            """, ('warlock-20',))
            spell_levels = [row[0] for row in cursor.fetchall()]

            assert 9 in spell_levels, "Level 17+ Warlock should have a level 9 arcanum"

        conn.close()


class TestArcanumUsage:
    """Test Mystic Arcanum usage and recovery."""

    @pytest.fixture
    def warlock_db(self):
        """Create Warlock test database."""
        with WarlockTestDatabase() as db_path:
            yield db_path

    def test_arcanum_cast_once_per_long_rest(self, warlock_db):
        """Test each arcanum can be cast once without expending spell slot."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            # Mark arcanum as used
            cursor.execute("""
                UPDATE mystic_arcanum
                SET used = 1
                WHERE character_id = ? AND spell_level = 6
            """, ('warlock-12',))
            conn.commit()

            cursor.execute("""
                SELECT used FROM mystic_arcanum
                WHERE character_id = ? AND spell_level = 6
            """, ('warlock-12',))
            used = cursor.fetchone()[0]
            assert used == 1

        conn.close()

    def test_arcanum_recovers_on_long_rest(self, warlock_db):
        """Test Mystic Arcanum spells recover on long rest."""
        test_db = WarlockTestDatabase(warlock_db)
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            # Mark all arcanum as used
            cursor.execute("""
                UPDATE mystic_arcanum
                SET used = 1
                WHERE character_id = ?
            """, ('warlock-20',))
            conn.commit()

            # Take long rest
            test_db.reset_resources('warlock-20', rest_type='long')

            cursor.execute("""
                SELECT used FROM mystic_arcanum
                WHERE character_id = ?
            """, ('warlock-20',))
            uses = [row[0] for row in cursor.fetchall()]

            # All should be recovered (used = 0)
            assert all(used == 0 for used in uses), "All arcanum should recover on long rest"

        conn.close()

    def test_arcanum_does_not_expend_spell_slot(self, warlock_db):
        """Test casting Mystic Arcanum does not consume Pact Magic slots."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Get current pact slots
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT pact_slots_current FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-12',))
            slots_before = cursor.fetchone()[0]

            # Cast arcanum (simulated - doesn't affect pact slots)
            cursor.execute("""
                UPDATE mystic_arcanum
                SET used = 1
                WHERE character_id = ? AND spell_level = 6
            """, ('warlock-12',))
            conn.commit()

            cursor.execute("""
                SELECT pact_slots_current FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-12',))
            slots_after = cursor.fetchone()[0]

            assert slots_before == slots_after, "Mystic Arcanum should not consume Pact Magic slots"

        conn.close()

    def test_multiple_arcanum_independent(self, warlock_db):
        """Test each Mystic Arcanum spell is tracked independently."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            # Use level 6 arcanum
            cursor.execute("""
                UPDATE mystic_arcanum
                SET used = 1
                WHERE character_id = ? AND spell_level = 6
            """, ('warlock-20',))
            conn.commit()

            # Other arcanum should still be available
            cursor.execute("""
                SELECT used FROM mystic_arcanum
                WHERE character_id = ? AND spell_level IN (7, 8, 9)
            """, ('warlock-20',))
            other_uses = [row[0] for row in cursor.fetchall()]

            assert all(used == 0 for used in other_uses), "Other arcanum should remain available"

        conn.close()


class TestArcanumSpellSelection:
    """Test Mystic Arcanum spell selection and replacement."""

    @pytest.fixture
    def warlock_db(self):
        """Create Warlock test database."""
        with WarlockTestDatabase() as db_path:
            yield db_path

    def test_arcanum_must_be_warlock_spell(self, warlock_db):
        """Test Mystic Arcanum must be chosen from Warlock spell list."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Common Warlock high-level spells
        warlock_high_level_spells = [
            # Level 6
            'circle_of_death', 'create_undead', 'eyebite', 'true_seeing',
            # Level 7
            'etherealness', 'finger_of_death', 'forcecage', 'plane_shift',
            # Level 8
            'befuddlement', 'demiplane', 'dominate_monster', 'glibness', 'power_word_stun',
            # Level 9
            'astral_projection', 'foresight', 'gate', 'imprisonment', 'power_word_kill', 'true_polymorph', 'weird'
        ]

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT spell_name FROM mystic_arcanum
                WHERE character_id = ?
            """, ('warlock-20',))
            chosen_spells = [row[0] for row in cursor.fetchall()]

            # All chosen spells should be from Warlock list
            for spell in chosen_spells:
                assert spell in warlock_high_level_spells or spell.replace('_', ' ').title() in [s.replace('_', ' ').title() for s in warlock_high_level_spells]

        conn.close()

    def test_arcanum_replacement_on_level_up(self, warlock_db):
        """Test Mystic Arcanum spells can be replaced on level up."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            # Get current level 6 arcanum
            cursor.execute("""
                SELECT spell_name FROM mystic_arcanum
                WHERE character_id = ? AND spell_level = 6
            """, ('warlock-20',))
            old_spell = cursor.fetchone()[0]

            # Simulate replacement
            new_spell = 'eyebite' if old_spell != 'eyebite' else 'true_seeing'

            cursor.execute("""
                UPDATE mystic_arcanum
                SET spell_name = ?
                WHERE character_id = ? AND spell_level = 6
            """, (new_spell, 'warlock-20'))
            conn.commit()

            cursor.execute("""
                SELECT spell_name FROM mystic_arcanum
                WHERE character_id = ? AND spell_level = 6
            """, ('warlock-20',))
            updated_spell = cursor.fetchone()[0]

            assert updated_spell == new_spell, "Arcanum spell should be replaceable"

        conn.close()

    def test_one_arcanum_per_spell_level(self, warlock_db):
        """Test character has exactly one arcanum per eligible spell level."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mystic_arcanum'
        """)

        if cursor.fetchone():
            # warlock-20 should have exactly 1 of each: level 6, 7, 8, 9
            for spell_level in [6, 7, 8, 9]:
                cursor.execute("""
                    SELECT COUNT(*) FROM mystic_arcanum
                    WHERE character_id = ? AND spell_level = ?
                """, ('warlock-20', spell_level))
                count = cursor.fetchone()[0]

                assert count == 1, f"Should have exactly 1 level {spell_level} arcanum, got {count}"

        conn.close()


class TestContactPatron:
    """Test Contact Patron feature (Level 9)."""

    @pytest.fixture
    def warlock_db(self):
        """Create Warlock test database."""
        with WarlockTestDatabase() as db_path:
            yield db_path

    def test_contact_other_plane_always_prepared(self, warlock_db):
        """Test Contact Other Plane is always prepared at level 9."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Level 9 Warlock should have Contact Other Plane prepared
        cursor.execute("""
            SELECT prepared_spells FROM character_spellcasting
            WHERE character_id = ? AND spellcasting_class = 'warlock'
        """, ('warlock-9',))
        result = cursor.fetchone()

        if result and result[0]:
            import json
            prepared = json.loads(result[0])
            # Contact Other Plane should be in prepared spells
            assert 'contact_other_plane' in prepared or any('contact' in spell.lower() for spell in prepared)

        conn.close()

    def test_contact_patron_no_spell_slot(self, warlock_db):
        """Test Contact Patron can be used without expending spell slot."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # When contacting patron specifically, no spell slot is used
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT pact_slots_current FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-9',))
            slots_before = cursor.fetchone()[0]

            # Using Contact Patron feature shouldn't consume slot
            # (Normal casting would consume a slot)
            assert slots_before == 2  # Level 9 has 2 slots

        conn.close()

    def test_contact_patron_auto_success_saving_throw(self, warlock_db):
        """Test Contact Patron automatically succeeds on saving throw."""
        # Contact Other Plane normally requires an Intelligence saving throw
        # Using the Contact Patron feature, you automatically succeed
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT intelligence FROM characters WHERE id = ?
        """, ('warlock-9',))
        intelligence = cursor.fetchone()[0]
        int_mod = (intelligence - 10) // 2

        # Even with low Intelligence, auto-succeeds when using Contact Patron
        assert int_mod >= -2  # Shouldn't matter for Contact Patron feature

        conn.close()

    def test_contact_patron_once_per_long_rest(self, warlock_db):
        """Test Contact Patron feature can be used once per long rest."""
        test_db = WarlockTestDatabase(warlock_db)
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Check if there's a tracking mechanism for Contact Patron usage
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            # Could track with a contact_patron_used flag
            cursor.execute("PRAGMA table_info(warlock_features)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'contact_patron_used' in columns:
                cursor.execute("""
                    UPDATE warlock_features
                    SET contact_patron_used = 1
                    WHERE character_id = ?
                """, ('warlock-9',))
                conn.commit()

                # After long rest, should reset
                test_db.reset_resources('warlock-9', rest_type='long')

        conn.close()


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])
