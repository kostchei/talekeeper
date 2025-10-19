#test
"""
Comprehensive tests for Fighter Second Wind mechanics.

Tests usage, healing calculations, resource tracking, and rest recovery
according to D&D 2024 rules.
"""

import pytest
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.fixtures.fighter_test_database import FighterTestDatabase
from services.fighter_abilities import FighterAbilitiesService
from core.game_engine_sqlite import GameEngineSQLite


class TestSecondWindMechanics:
    """Test Second Wind ability mechanics."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def fighter_service(self, fighter_db):
        """Create FighterAbilitiesService with test database."""
        return FighterAbilitiesService(fighter_db)

    @pytest.fixture
    def game_engine(self, fighter_db):
        """Create GameEngine with test database."""
        return GameEngineSQLite(fighter_db)

    def test_second_wind_healing_calculation(self, fighter_service, fighter_db):
        """Test Second Wind healing: 1d10 + Fighter level."""
        # Set up level 5 Fighter with reduced HP
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-5', 20)  # Reduce HP by 20

        with patch('random.randint', return_value=7):  # Roll 7 on d10
            result = fighter_service.use_second_wind('fighter-5')

            assert result['success'] is True
            expected_healing = 7 + 5  # d10 roll + Fighter level
            assert result['healing'] == expected_healing
            assert result['new_hp'] == 25 + expected_healing  # Original reduced HP + healing

    def test_second_wind_resource_consumption(self, fighter_service, fighter_db):
        """Test Second Wind consumes one use per short rest."""
        # Use Second Wind
        with patch('random.randint', return_value=5):
            result = fighter_service.use_second_wind('fighter-3')

            assert result['success'] is True
            assert result['uses_remaining'] == 0

        # Try to use again - should fail
        result2 = fighter_service.use_second_wind('fighter-3')
        assert result2['success'] is False
        assert 'no uses remaining' in result2['message'].lower()

    def test_second_wind_wont_heal_at_max_hp(self, fighter_service):
        """Test Second Wind cannot be used at maximum HP."""
        # Character at full HP should not be able to use Second Wind
        result = fighter_service.use_second_wind('fighter-3')
        assert result['success'] is False
        assert 'already at maximum' in result['message'].lower()

    def test_second_wind_healing_cap_at_max_hp(self, fighter_service, fighter_db):
        """Test Second Wind healing cannot exceed maximum HP."""
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-3', 5)  # Damage for 5 HP

        # Roll high healing that would exceed max HP
        with patch('random.randint', return_value=10):  # Roll max on d10
            result = fighter_service.use_second_wind('fighter-3')

            assert result['success'] is True
            # Should heal to max HP (30), not beyond
            assert result['new_hp'] == 30

    def test_second_wind_minimum_healing(self, fighter_service, fighter_db):
        """Test Second Wind minimum healing (1 + level)."""
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-1', 5)

        with patch('random.randint', return_value=1):  # Roll 1 on d10
            result = fighter_service.use_second_wind('fighter-1')

            assert result['success'] is True
            expected_healing = 1 + 1  # Minimum roll + level 1
            assert result['healing'] == expected_healing

    def test_second_wind_high_level_scaling(self, fighter_service, fighter_db):
        """Test Second Wind scales with Fighter level."""
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-15', 30)

        with patch('random.randint', return_value=6):  # Average roll
            result = fighter_service.use_second_wind('fighter-15')

            assert result['success'] is True
            expected_healing = 6 + 15  # d10 + level 15
            assert result['healing'] == expected_healing

    def test_second_wind_rest_recovery(self, game_engine, fighter_db):
        """Test Second Wind recovers on short and long rests."""
        # Use Second Wind
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-3', 10)

        service = FighterAbilitiesService(fighter_db)
        with patch('random.randint', return_value=5):
            result = service.use_second_wind('fighter-3')
            assert result['uses_remaining'] == 0

        # Take short rest - should recover
        game_engine.take_short_rest('fighter-3')

        # Check resource recovery
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT second_wind_uses_current, second_wind_uses_max
            FROM characters WHERE id = ?
        """, ('fighter-3',))
        uses_current, uses_max = cursor.fetchone()
        conn.close()

        assert uses_current == uses_max  # Should be fully recovered

    def test_second_wind_unconscious_character(self, fighter_service, fighter_db):
        """Test Second Wind cannot be used when unconscious."""
        # Set character to 0 HP (unconscious)
        test_db = FighterTestDatabase(fighter_db)
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE characters SET hit_points_current = 0 WHERE id = ?
        """, ('fighter-3',))
        conn.commit()
        conn.close()

        result = fighter_service.use_second_wind('fighter-3')
        assert result['success'] is False
        assert 'unconscious' in result['message'].lower()

    def test_second_wind_multiclass_levels(self, fighter_service, fighter_db):
        """Test Second Wind uses Fighter levels only for multiclass characters."""
        # Create multiclass character (Fighter 3 / Wizard 2)
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, hit_points_current, hit_points_max,
                second_wind_uses_current, second_wind_uses_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('multiclass-1', 'Fighter/Wizard', 'fighter', 5, 20, 35, 1, 1))

        # Add Fighter class level entry
        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
            VALUES (?, ?, ?, ?)
        """, ('multiclass-1', 'fighter', None, 3))

        conn.commit()
        conn.close()

        with patch('random.randint', return_value=6):
            result = fighter_service.use_second_wind('multiclass-1')

            assert result['success'] is True
            # Should use Fighter level (3), not total level (5)
            expected_healing = 6 + 3
            assert result['healing'] == expected_healing


class TestSecondWindDatabaseIntegration:
    """Test Second Wind database state management."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    def test_second_wind_updates_character_hp(self, fighter_db):
        """Test Second Wind properly updates character HP in database."""
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-1', 6)  # Half HP

        service = FighterAbilitiesService(fighter_db)
        with patch('random.randint', return_value=4):
            result = service.use_second_wind('fighter-1')

            # Verify database was updated
            conn = sqlite3.connect(fighter_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hit_points_current FROM characters WHERE id = ?
            """, ('fighter-1',))
            current_hp = cursor.fetchone()[0]
            conn.close()

            expected_hp = 6 + 4 + 1  # Damaged HP + roll + level
            assert current_hp == expected_hp

    def test_second_wind_resource_tracking_persistence(self, fighter_db):
        """Test Second Wind usage is properly tracked in database."""
        service = FighterAbilitiesService(fighter_db)

        # Damage character to enable Second Wind
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-2', 8)

        with patch('random.randint', return_value=3):
            service.use_second_wind('fighter-2')

            # Verify usage was recorded
            conn = sqlite3.connect(fighter_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT second_wind_uses_current, second_wind_uses_max
                FROM characters WHERE id = ?
            """, ('fighter-2',))
            current, max_uses = cursor.fetchone()
            conn.close()

            assert current == 0  # Used up
            assert max_uses == 1  # Still has max of 1

    def test_multiple_characters_independent_tracking(self, fighter_db):
        """Test Second Wind tracking is independent per character."""
        test_db = FighterTestDatabase(fighter_db)
        test_db.setup_damaged_character('fighter-1', 5)
        test_db.setup_damaged_character('fighter-2', 5)

        service = FighterAbilitiesService(fighter_db)

        # Use Second Wind on first character
        with patch('random.randint', return_value=3):
            result1 = service.use_second_wind('fighter-1')
            assert result1['success'] is True

        # Second character should still have their use
        with patch('random.randint', return_value=4):
            result2 = service.use_second_wind('fighter-2')
            assert result2['success'] is True

        # First character should be out of uses
        result3 = service.use_second_wind('fighter-1')
        assert result3['success'] is False


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])