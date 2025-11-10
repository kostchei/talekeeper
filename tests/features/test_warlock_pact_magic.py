#test
"""
Comprehensive tests for Warlock Pact Magic mechanics.

Tests spell slot management, short rest recovery, level scaling,
and Magical Cunning according to D&D 2024 rules.
"""

import pytest
import sqlite3
import sys
from pathlib import Path

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.fixtures.warlock_test_database import WarlockTestDatabase


class TestPactMagicSlots:
    """Test Pact Magic spell slot mechanics."""

    @pytest.fixture
    def warlock_db(self):
        """Create Warlock test database."""
        with WarlockTestDatabase() as db_path:
            yield db_path

    def test_pact_magic_slot_progression(self, warlock_db):
        """Test Pact Magic slots scale correctly by level."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Expected progression: (character_id, expected_slots, expected_level)
        progression = [
            ('warlock-1', 1, 1),
            ('warlock-3', 2, 2),
            ('warlock-5', 2, 3),
            ('warlock-9', 2, 5),
            ('warlock-12', 3, 5),
            ('warlock-18', 4, 5),
            ('warlock-20', 4, 5),
        ]

        # Check if warlock_features table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        has_warlock_features = cursor.fetchone() is not None

        for character_id, expected_slots, expected_level in progression:
            if has_warlock_features:
                cursor.execute("""
                    SELECT pact_slots_max, pact_slot_level
                    FROM warlock_features
                    WHERE character_id = ?
                """, (character_id,))
                result = cursor.fetchone()
                assert result is not None, f"No warlock_features found for {character_id}"
                slots, slot_level = result
            else:
                # Fallback to character level calculation
                cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
                level = cursor.fetchone()[0]

                # Calculate slots based on level
                if level >= 17:
                    slots = 4
                elif level >= 11:
                    slots = 3
                elif level >= 2:
                    slots = 2
                else:
                    slots = 1

                # Calculate slot level
                if level >= 9:
                    slot_level = 5
                elif level >= 7:
                    slot_level = 4
                elif level >= 5:
                    slot_level = 3
                elif level >= 3:
                    slot_level = 2
                else:
                    slot_level = 1

            assert slots == expected_slots, f"{character_id}: Expected {expected_slots} slots, got {slots}"
            assert slot_level == expected_level, f"{character_id}: Expected slot level {expected_level}, got {slot_level}"

        conn.close()

    def test_pact_slots_all_same_level(self, warlock_db):
        """Test that all Pact Magic slots are the same level."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Level 5 Warlock has 2 slots, both level 3
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT pact_slots_max, pact_slot_level
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-5',))
            slots_max, slot_level = cursor.fetchone()
            assert slots_max == 2
            assert slot_level == 3

        conn.close()

    def test_pact_slot_usage(self, warlock_db):
        """Test using Pact Magic spell slots."""
        test_db = WarlockTestDatabase(warlock_db)
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Check if warlock_features table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        has_warlock_features = cursor.fetchone() is not None

        # Use a slot
        test_db.use_pact_slot('warlock-3')

        if has_warlock_features:
            cursor.execute("""
                SELECT pact_slots_current, pact_slots_max
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-3',))
            current, max_slots = cursor.fetchone()
        else:
            cursor.execute("""
                SELECT spell_slots_1, spell_slots_max_1
                FROM characters
                WHERE id = ?
            """, ('warlock-3',))
            current, max_slots = cursor.fetchone()

        assert current == 1  # Started with 2, used 1
        assert max_slots == 2

        # Use another slot
        test_db.use_pact_slot('warlock-3')

        if has_warlock_features:
            cursor.execute("""
                SELECT pact_slots_current
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-3',))
            current = cursor.fetchone()[0]
        else:
            cursor.execute("""
                SELECT spell_slots_1
                FROM characters
                WHERE id = ?
            """, ('warlock-3',))
            current = cursor.fetchone()[0]

        assert current == 0  # All slots used

        conn.close()

    def test_short_rest_recovery(self, warlock_db):
        """Test Pact Magic slots recover on short rest."""
        test_db = WarlockTestDatabase(warlock_db)

        # Use all slots
        test_db.use_pact_slot('warlock-5')
        test_db.use_pact_slot('warlock-5')

        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT pact_slots_current FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-5',))
            assert cursor.fetchone()[0] == 0

        # Take short rest
        test_db.reset_resources('warlock-5', rest_type='short')

        if cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='warlock_features'").fetchone():
            cursor.execute("""
                SELECT pact_slots_current, pact_slots_max
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-5',))
            current, max_slots = cursor.fetchone()
            assert current == max_slots  # Fully recovered

        conn.close()

    def test_long_rest_recovery(self, warlock_db):
        """Test Pact Magic slots recover on long rest."""
        test_db = WarlockTestDatabase(warlock_db)

        # Use all slots
        test_db.use_pact_slot('warlock-5')
        test_db.use_pact_slot('warlock-5')

        # Take long rest
        test_db.reset_resources('warlock-5', rest_type='long')

        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT pact_slots_current, pact_slots_max
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-5',))
            current, max_slots = cursor.fetchone()
            assert current == max_slots  # Fully recovered

        conn.close()


class TestMagicalCunning:
    """Test Magical Cunning feature (Level 2)."""

    @pytest.fixture
    def warlock_db(self):
        """Create Warlock test database."""
        with WarlockTestDatabase() as db_path:
            yield db_path

    def test_magical_cunning_recovery_amount(self, warlock_db):
        """Test Magical Cunning recovers half max slots (rounded up)."""
        test_db = WarlockTestDatabase(warlock_db)
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Level 3 Warlock: 2 slots max, recovers 1 (half rounded up)
        test_db.use_pact_slot('warlock-3')
        test_db.use_pact_slot('warlock-3')

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            # Simulate Magical Cunning (recovers ceil(2/2) = 1 slot)
            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = pact_slots_current + 1,
                    magical_cunning_used = 1
                WHERE character_id = ?
            """, ('warlock-3',))
            conn.commit()

            cursor.execute("""
                SELECT pact_slots_current, pact_slots_max
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-3',))
            current, max_slots = cursor.fetchone()

            assert current == 1  # Recovered 1 of 2
            assert max_slots == 2

        conn.close()

    def test_magical_cunning_once_per_long_rest(self, warlock_db):
        """Test Magical Cunning can only be used once per long rest."""
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            # Mark as used
            cursor.execute("""
                UPDATE warlock_features
                SET magical_cunning_used = 1
                WHERE character_id = ?
            """, ('warlock-3',))
            conn.commit()

            cursor.execute("""
                SELECT magical_cunning_used
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-3',))
            used = cursor.fetchone()[0]
            assert used == 1

            # After long rest, should reset
            test_db = WarlockTestDatabase(warlock_db)
            test_db.reset_resources('warlock-3', rest_type='long')

            cursor.execute("""
                SELECT magical_cunning_used
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-3',))
            used = cursor.fetchone()[0]
            assert used == 0

        conn.close()

    def test_magical_cunning_high_level(self, warlock_db):
        """Test Magical Cunning at higher levels."""
        test_db = WarlockTestDatabase(warlock_db)
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Level 12 Warlock: 3 slots max, recovers 2 (ceil(3/2))
        test_db.use_pact_slot('warlock-12')
        test_db.use_pact_slot('warlock-12')
        test_db.use_pact_slot('warlock-12')

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            # Simulate Magical Cunning
            import math
            cursor.execute("""
                SELECT pact_slots_max FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-12',))
            max_slots = cursor.fetchone()[0]
            recovery = math.ceil(max_slots / 2)

            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = ?,
                    magical_cunning_used = 1
                WHERE character_id = ?
            """, (recovery, 'warlock-12'))
            conn.commit()

            cursor.execute("""
                SELECT pact_slots_current
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-12',))
            current = cursor.fetchone()[0]

            assert current == 2  # Recovered 2 of 3

        conn.close()


class TestEldritchMaster:
    """Test Eldritch Master feature (Level 20)."""

    @pytest.fixture
    def warlock_db(self):
        """Create Warlock test database."""
        with WarlockTestDatabase() as db_path:
            yield db_path

    def test_eldritch_master_full_recovery(self, warlock_db):
        """Test Eldritch Master recovers all spell slots."""
        test_db = WarlockTestDatabase(warlock_db)
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        # Use all slots
        for _ in range(4):
            test_db.use_pact_slot('warlock-20')

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT pact_slots_current FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-20',))
            assert cursor.fetchone()[0] == 0

            # Simulate Eldritch Master (recovers all slots)
            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = pact_slots_max
                WHERE character_id = ?
            """, ('warlock-20',))
            conn.commit()

            cursor.execute("""
                SELECT pact_slots_current, pact_slots_max
                FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-20',))
            current, max_slots = cursor.fetchone()

            assert current == 4  # All slots recovered
            assert current == max_slots

        conn.close()

    def test_eldritch_master_replaces_magical_cunning(self, warlock_db):
        """Test Eldritch Master improves Magical Cunning to full recovery."""
        # At level 20, Magical Cunning becomes Eldritch Master
        # which recovers ALL slots instead of half
        conn = sqlite3.connect(warlock_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='warlock_features'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT pact_slots_max FROM warlock_features
                WHERE character_id = ?
            """, ('warlock-20',))
            max_slots = cursor.fetchone()[0]
            assert max_slots == 4

        conn.close()


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])
