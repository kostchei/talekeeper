#test
"""
Tests for Tactical Shift (Fighter Level 5 Feature)

Tactical Shift allows Fighter to move up to half speed without provoking
opportunity attacks when using Second Wind as a bonus action.
"""

import sqlite3
import pytest
from services.fighter_abilities import FighterAbilitiesService


class TestTacticalShift:
    """Test Tactical Shift feature"""

    @pytest.fixture
    def db_path(self, tmp_path):
        """Create test database"""
        db = tmp_path / "test_shift.db"
        conn = sqlite3.connect(str(db))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                class_id TEXT,
                level INTEGER,
                hit_points_current INTEGER DEFAULT 50,
                hit_points_max INTEGER DEFAULT 100,
                max_hit_points INTEGER DEFAULT 100,
                current_hit_points INTEGER DEFAULT 50,
                second_wind_uses_current INTEGER DEFAULT 2,
                second_wind_uses_max INTEGER DEFAULT 2
            )
        """)

        cursor.execute("""
            CREATE TABLE character_combat_state (
                character_id TEXT PRIMARY KEY,
                tactical_shift_movement INTEGER DEFAULT 0,
                critical_range_min INTEGER DEFAULT 20
            )
        """)

        conn.commit()
        conn.close()
        return str(db)

    def create_fighter(self, db_path: str, level: int) -> str:
        """Create test fighter"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        char_id = f"fighter_l{level}"
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, level)
            VALUES (?, ?, 'fighter', ?)
        """, (char_id, f"Fighter {level}", level))

        conn.commit()
        conn.close()
        return char_id

    def test_level_4_no_tactical_shift(self, db_path):
        """Level 4: Second Wind does not grant Tactical Shift"""
        char_id = self.create_fighter(db_path, 4)
        service = FighterAbilitiesService(db_path)

        result = service.use_second_wind(char_id)

        assert result['success']
        assert 'tactical_shift_movement' not in result
        assert 'tactical_shift_active' not in result

    def test_level_5_tactical_shift_activates(self, db_path):
        """Level 5: Second Wind grants Tactical Shift movement"""
        char_id = self.create_fighter(db_path, 5)
        service = FighterAbilitiesService(db_path)

        result = service.use_second_wind(char_id)

        assert result['success']
        assert 'tactical_shift_movement' in result
        assert result['tactical_shift_movement'] == 15  # Half of default 30 speed
        assert result['tactical_shift_active']

    def test_tactical_shift_half_speed(self, db_path):
        """Tactical Shift grants half speed movement"""
        char_id = self.create_fighter(db_path, 8)
        service = FighterAbilitiesService(db_path)

        result = service.use_second_wind(char_id)

        assert result['tactical_shift_movement'] == 15

    def test_tactical_shift_stored_in_combat_state(self, db_path):
        """Tactical Shift movement is stored in combat state"""
        char_id = self.create_fighter(db_path, 10)
        service = FighterAbilitiesService(db_path)

        service.use_second_wind(char_id)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tactical_shift_movement
            FROM character_combat_state
            WHERE character_id = ?
        """, (char_id,))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 15

    def test_level_20_tactical_shift(self, db_path):
        """Level 20: Tactical Shift still works"""
        char_id = self.create_fighter(db_path, 20)
        service = FighterAbilitiesService(db_path)

        result = service.use_second_wind(char_id)

        assert result['tactical_shift_movement'] == 15
        assert result['tactical_shift_active']

    def test_non_fighter_no_tactical_shift(self, db_path):
        """Non-Fighter with Second Wind does not get Tactical Shift"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (id, name, class_id, level,
                                  second_wind_uses_current, second_wind_uses_max)
            VALUES ('monk1', 'Monk', 'monk', 10, 1, 1)
        """)
        conn.commit()
        conn.close()

        service = FighterAbilitiesService(db_path)
        result = service.use_second_wind('monk1')

        assert result['success']
        assert 'tactical_shift_movement' not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])