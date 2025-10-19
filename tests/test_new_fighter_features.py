#test
"""
Tests for newly implemented Fighter/Champion features:
- Remarkable Athlete jump distance
- Defy Death death save mechanics
"""

import sqlite3
import pytest
from services.fighter_abilities import FighterAbilitiesService


class TestRemarkableAthleteJumpDistance:
    """Test Remarkable Athlete jump distance bonus"""

    @pytest.fixture
    def db_path(self, tmp_path):
        db = tmp_path / "test_athlete.db"
        conn = sqlite3.connect(str(db))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                class_id TEXT,
                subclass_id TEXT,
                level INTEGER,
                strength INTEGER DEFAULT 16
            )
        """)

        cursor.execute("""
            CREATE TABLE character_subclasses (
                character_id TEXT,
                class_id TEXT,
                subclass_id TEXT,
                PRIMARY KEY (character_id, class_id)
            )
        """)

        conn.commit()
        conn.close()
        return str(db)

    def create_champion(self, db_path: str, level: int, strength: int = 16) -> str:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        char_id = f"champion_l{level}"
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, subclass_id, level, strength)
            VALUES (?, ?, 'fighter', 'champion', ?, ?)
        """, (char_id, f"Champion {level}", level, strength))

        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id)
            VALUES (?, 'fighter', 'champion')
        """, (char_id,))

        conn.commit()
        conn.close()
        return char_id

    def test_level_3_has_jump_bonus(self, db_path):
        """Level 3 Champion gets jump distance bonus"""
        char_id = self.create_champion(db_path, 3, strength=16)
        service = FighterAbilitiesService(db_path)

        bonus = service.get_remarkable_athlete_jump_bonus(char_id)
        assert bonus == 3  # STR 16 = +3 modifier

    def test_jump_bonus_scales_with_strength(self, db_path):
        """Jump bonus equals STR modifier"""
        char_id = self.create_champion(db_path, 5, strength=20)
        service = FighterAbilitiesService(db_path)

        bonus = service.get_remarkable_athlete_jump_bonus(char_id)
        assert bonus == 5  # STR 20 = +5 modifier

    def test_level_2_no_jump_bonus(self, db_path):
        """Level 2 Champion doesn't have Remarkable Athlete yet"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, subclass_id, level, strength)
            VALUES ('champ2', 'Champion 2', 'fighter', 'champion', 2, 16)
        """)
        conn.commit()
        conn.close()

        service = FighterAbilitiesService(db_path)
        bonus = service.get_remarkable_athlete_jump_bonus('champ2')
        assert bonus == 0


class TestDefyDeath:
    """Test Defy Death death save mechanics"""

    @pytest.fixture
    def db_path(self, tmp_path):
        db = tmp_path / "test_defy.db"
        conn = sqlite3.connect(str(db))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                class_id TEXT,
                subclass_id TEXT,
                level INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE character_subclasses (
                character_id TEXT,
                class_id TEXT,
                subclass_id TEXT,
                PRIMARY KEY (character_id, class_id)
            )
        """)

        conn.commit()
        conn.close()
        return str(db)

    def create_champion(self, db_path: str, level: int) -> str:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        char_id = f"champion_l{level}"
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, subclass_id, level)
            VALUES (?, ?, 'fighter', 'champion', ?)
        """, (char_id, f"Champion {level}", level))

        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id)
            VALUES (?, 'fighter', 'champion')
        """, (char_id,))

        conn.commit()
        conn.close()
        return char_id

    def test_level_18_has_defy_death(self, db_path):
        """Level 18 Champion has Defy Death"""
        char_id = self.create_champion(db_path, 18)
        service = FighterAbilitiesService(db_path)

        assert service.has_defy_death(char_id)

    def test_level_17_no_defy_death(self, db_path):
        """Level 17 Champion doesn't have Defy Death yet"""
        char_id = self.create_champion(db_path, 17)
        service = FighterAbilitiesService(db_path)

        assert not service.has_defy_death(char_id)

    def test_defy_death_grants_advantage(self, db_path):
        """Defy Death grants advantage on death saves"""
        char_id = self.create_champion(db_path, 18)
        service = FighterAbilitiesService(db_path)

        result = service.roll_death_save(char_id)

        assert result['defy_death_active']
        assert result['advantage_used']

    def test_defy_death_18_19_20_count_as_20(self, db_path):
        """Defy Death: rolls of 18-20 count as nat 20"""
        char_id = self.create_champion(db_path, 20)
        service = FighterAbilitiesService(db_path)

        # Run multiple rolls to test the 18-20 -> 20 conversion
        nat_20_count = 0
        trials = 100

        for _ in range(trials):
            result = service.roll_death_save(char_id)
            if result['critical_success']:
                nat_20_count += 1

        # With advantage and 18-20 counting as 20, should have high crit rate
        # Probability is complex but should be significantly higher than 5%
        assert nat_20_count > 10  # Should get many more than the 5 expected without Defy Death

    def test_no_defy_death_normal_roll(self, db_path):
        """Without Defy Death, death save is normal"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, level)
            VALUES ('fighter10', 'Fighter 10', 'fighter', 10)
        """)
        conn.commit()
        conn.close()

        service = FighterAbilitiesService(db_path)
        result = service.roll_death_save('fighter10')

        assert not result['defy_death_active']
        assert not result['advantage_used']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])