#test
"""
Comprehensive tests for Fighter Indomitable mechanics.

Tests save reroll functionality, usage tracking, level scaling,
and rest recovery according to D&D 2024 rules.
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
from services.advantage_system import AdvantageSystem
from core.game_engine_sqlite import GameEngineSQLite


class TestIndomitableMechanics:
    """Test Indomitable ability mechanics."""

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
    def advantage_system(self, fighter_db):
        """Create AdvantageSystem with test database."""
        return AdvantageSystem(fighter_db)

    @pytest.fixture
    def game_engine(self, fighter_db):
        """Create GameEngine with test database."""
        return GameEngineSQLite(fighter_db)

    def test_indomitable_availability_at_level_9(self, fighter_service):
        """Test Indomitable becomes available at Fighter level 9."""
        # Level 5 Fighter should not have Indomitable
        result1 = fighter_service.use_indomitable('fighter-5', 'strength', 8)
        assert result1['success'] is False
        assert 'not available' in result1['message'].lower()

        # Level 9 Fighter should have Indomitable
        result2 = fighter_service.use_indomitable('fighter-9', 'strength', 8)
        assert result2['success'] is True

    def test_indomitable_reroll_mechanic(self, fighter_service):
        """Test Indomitable allows rerolling a failed saving throw."""
        with patch('random.randint') as mock_roll:
            # First roll fails (8), second roll succeeds (15)
            mock_roll.side_effect = [8, 15]

            result = fighter_service.use_indomitable('fighter-9', 'dexterity', 12)

            assert result['success'] is True
            assert result['original_roll'] == 8
            assert result['reroll'] == 15
            assert result['final_result'] == 15
            assert result['save_succeeded'] is True  # 15 > DC 12

    def test_indomitable_must_use_reroll(self, fighter_service):
        """Test that Indomitable forces you to use the reroll result."""
        with patch('random.randint') as mock_roll:
            # First roll fails (10), second roll is worse (5)
            mock_roll.side_effect = [10, 5]

            result = fighter_service.use_indomitable('fighter-9', 'wisdom', 15)

            assert result['success'] is True
            assert result['original_roll'] == 10
            assert result['reroll'] == 5
            assert result['final_result'] == 5  # Must use worse reroll
            assert result['save_succeeded'] is False  # Both rolls failed

    def test_indomitable_resource_consumption(self, fighter_service):
        """Test Indomitable consumes one use per long rest."""
        # Use Indomitable
        with patch('random.randint', return_value=10):
            result = fighter_service.use_indomitable('fighter-9', 'constitution', 12)
            assert result['success'] is True
            assert result['uses_remaining'] == 0

        # Try to use again - should fail
        result2 = fighter_service.use_indomitable('fighter-9', 'constitution', 12)
        assert result2['success'] is False
        assert 'no uses remaining' in result2['message'].lower()

    def test_indomitable_multiple_uses_at_high_level(self, fighter_service, fighter_db):
        """Test Indomitable gets multiple uses at higher levels."""
        # Create level 13 Fighter (gets 2 uses)
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, indomitable_uses_current, indomitable_uses_max
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('fighter-13', 'Veteran Fighter', 'fighter', 13, 2, 2))

        conn.commit()
        conn.close()

        # Should be able to use Indomitable twice
        with patch('random.randint', return_value=8):
            result1 = fighter_service.use_indomitable('fighter-13', 'strength', 15)
            assert result1['success'] is True
            assert result1['uses_remaining'] == 1

            result2 = fighter_service.use_indomitable('fighter-13', 'dexterity', 15)
            assert result2['success'] is True
            assert result2['uses_remaining'] == 0

        # Third use should fail
        result3 = fighter_service.use_indomitable('fighter-13', 'wisdom', 15)
        assert result3['success'] is False

    def test_indomitable_level_17_three_uses(self, fighter_service, fighter_db):
        """Test Indomitable gets 3 uses at level 17."""
        # Create level 17 Fighter (gets 3 uses)
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, indomitable_uses_current, indomitable_uses_max
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('fighter-17', 'Legendary Fighter', 'fighter', 17, 3, 3))

        conn.commit()
        conn.close()

        # Should be able to use Indomitable three times
        with patch('random.randint', return_value=5):
            for i in range(3):
                result = fighter_service.use_indomitable('fighter-17', 'charisma', 15)
                assert result['success'] is True
                assert result['uses_remaining'] == 2 - i

        # Fourth use should fail
        result4 = fighter_service.use_indomitable('fighter-17', 'intelligence', 15)
        assert result4['success'] is False

    def test_indomitable_ability_modifier_application(self, fighter_service):
        """Test Indomitable properly applies ability modifiers to saves."""
        with patch('random.randint', return_value=10):
            # Level 9 Fighter has STR 18 (+4 modifier)
            result = fighter_service.use_indomitable('fighter-9', 'strength', 15)

            # Roll (10) + STR modifier (4) = 14
            assert result['total_with_modifier'] == 14
            assert result['ability_modifier'] == 4

    def test_indomitable_proficiency_bonus_application(self, fighter_service):
        """Test Indomitable applies proficiency bonus for proficient saves."""
        # Fighters are proficient in STR and CON saves
        with patch('random.randint', return_value=8):
            result = fighter_service.use_indomitable('fighter-9', 'strength', 15)

            # Should include proficiency bonus (+4 at level 9)
            assert result['proficiency_applied'] is True
            assert result['proficiency_bonus'] == 4
            # Roll (8) + STR (4) + Prof (4) = 16
            assert result['total_with_modifier'] == 16

    def test_indomitable_no_proficiency_bonus_for_non_proficient(self, fighter_service):
        """Test Indomitable doesn't apply proficiency for non-proficient saves."""
        # Fighters are not proficient in INT saves
        with patch('random.randint', return_value=12):
            result = fighter_service.use_indomitable('fighter-9', 'intelligence', 15)

            assert result['proficiency_applied'] is False
            # Roll (12) + INT (0) = 12
            assert result['total_with_modifier'] == 12

    def test_indomitable_long_rest_recovery(self, game_engine, fighter_service, fighter_db):
        """Test Indomitable recovers on long rest only."""
        # Use Indomitable
        with patch('random.randint', return_value=5):
            result = fighter_service.use_indomitable('fighter-9', 'dexterity', 15)
            assert result['uses_remaining'] == 0

        # Take short rest - should NOT recover
        game_engine.take_short_rest('fighter-9')

        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT indomitable_uses_current FROM characters WHERE id = ?
        """, ('fighter-9',))
        uses_after_short = cursor.fetchone()[0]
        conn.close()

        assert uses_after_short == 0  # Still used up

        # Take long rest - should recover
        game_engine.take_long_rest('fighter-9')

        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT indomitable_uses_current, indomitable_uses_max
            FROM characters WHERE id = ?
        """, ('fighter-9',))
        uses_current, uses_max = cursor.fetchone()
        conn.close()

        assert uses_current == uses_max  # Should be fully recovered

    def test_indomitable_death_save_interaction(self, fighter_service, fighter_db):
        """Test Indomitable can be used on death saving throws."""
        # Set Fighter to 0 HP but conscious (death saves)
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE characters SET hit_points_current = 0 WHERE id = ?
        """, ('fighter-9',))
        conn.commit()
        conn.close()

        with patch('random.randint') as mock_roll:
            # Fail death save (5), reroll succeeds (15)
            mock_roll.side_effect = [5, 15]

            result = fighter_service.use_indomitable('fighter-9', 'death', 10)

            assert result['success'] is True
            assert result['original_roll'] == 5
            assert result['reroll'] == 15
            assert result['save_succeeded'] is True

    def test_indomitable_legendary_resistance_interaction(self, fighter_service):
        """Test Indomitable doesn't stack with legendary resistance."""
        # This would test edge cases where creatures have both abilities
        # (theoretical scenario for high-level multiclass or magical effects)
        pass

    def test_indomitable_multiclass_availability(self, fighter_service, fighter_db):
        """Test Indomitable uses Fighter levels for multiclass characters."""
        # Create multiclass character (Fighter 9 / Paladin 3)
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, indomitable_uses_current, indomitable_uses_max
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('multiclass-indom', 'Fighter/Paladin', 'fighter', 12, 1, 1))

        # Add Fighter class level entry (level 9 Fighter)
        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
            VALUES (?, ?, ?, ?)
        """, ('multiclass-indom', 'fighter', None, 9))

        conn.commit()
        conn.close()

        # Should have Indomitable available
        with patch('random.randint', return_value=8):
            result = fighter_service.use_indomitable('multiclass-indom', 'wisdom', 15)
            assert result['success'] is True


class TestIndomitableDatabaseIntegration:
    """Test Indomitable database state management."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    def test_indomitable_resource_tracking_persistence(self, fighter_db):
        """Test Indomitable usage is properly tracked in database."""
        service = FighterAbilitiesService(fighter_db)

        with patch('random.randint', return_value=6):
            service.use_indomitable('fighter-9', 'constitution', 15)

        # Verify usage was recorded
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT indomitable_uses_current, indomitable_uses_max
            FROM characters WHERE id = ?
        """, ('fighter-9',))
        current, max_uses = cursor.fetchone()
        conn.close()

        assert current == 0  # Used up
        assert max_uses == 1  # Still has max of 1

    def test_indomitable_save_history_tracking(self, fighter_db):
        """Test saving throw history is tracked for analysis."""
        service = FighterAbilitiesService(fighter_db)

        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [7, 14]  # Failed then succeeded

            result = service.use_indomitable('fighter-9', 'wisdom', 12)

            # Could verify save history is stored for future reference
            # This depends on whether the system tracks save attempts

    def test_multiple_characters_independent_indomitable(self, fighter_db):
        """Test Indomitable tracking is independent per character."""
        service = FighterAbilitiesService(fighter_db)

        # Use Indomitable on first character
        with patch('random.randint', return_value=5):
            result1 = service.use_indomitable('fighter-9', 'dexterity', 15)
            assert result1['success'] is True

        # Second character should still have their use
        with patch('random.randint', return_value=6):
            result2 = service.use_indomitable('fighter-10', 'strength', 15)
            assert result2['success'] is True

        # First character should be out of uses
        result3 = service.use_indomitable('fighter-9', 'wisdom', 15)
        assert result3['success'] is False


class TestIndomitableAdvantageIntegration:
    """Test Indomitable interaction with advantage/disadvantage system."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    def test_indomitable_with_advantage(self, fighter_db):
        """Test Indomitable interaction with advantage on saves."""
        service = FighterAbilitiesService(fighter_db)
        advantage_system = AdvantageSystem(fighter_db)

        # Grant advantage on Wisdom saves (e.g., from magical effect)
        advantage_system.add_advantage_source(
            'fighter-9', 'wisdom_save', 'Blessing of Protection'
        )

        with patch('random.randint') as mock_roll:
            # Advantage rolls: 8, 12 (takes higher), then reroll: 6, 15 (takes higher)
            mock_roll.side_effect = [8, 12, 6, 15]

            result = service.use_indomitable('fighter-9', 'wisdom', 14)

            assert result['success'] is True
            assert result['original_roll'] == 12  # Higher of 8, 12
            assert result['reroll'] == 15  # Higher of 6, 15
            assert result['advantage_applied'] is True

    def test_indomitable_with_disadvantage(self, fighter_db):
        """Test Indomitable interaction with disadvantage on saves."""
        service = FighterAbilitiesService(fighter_db)
        advantage_system = AdvantageSystem(fighter_db)

        # Apply disadvantage on Constitution saves (e.g., from poison)
        advantage_system.add_disadvantage_source(
            'fighter-9', 'constitution_save', 'Poisoned'
        )

        with patch('random.randint') as mock_roll:
            # Disadvantage rolls: 15, 8 (takes lower), then reroll: 12, 7 (takes lower)
            mock_roll.side_effect = [15, 8, 12, 7]

            result = service.use_indomitable('fighter-9', 'constitution', 10)

            assert result['success'] is True
            assert result['original_roll'] == 8  # Lower of 15, 8
            assert result['reroll'] == 7  # Lower of 12, 7
            assert result['disadvantage_applied'] is True


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])