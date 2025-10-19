import pytest
import sqlite3
import os
import sys
sys.path.insert(0, 'src')
from talekeeper.services.morale_manager import MoraleManager

TEST_DB = "test_morale.db"

@pytest.fixture
def setup_db():
    """Setup test database"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE monsters (
            id TEXT PRIMARY KEY,
            name TEXT,
            wisdom INTEGER,
            type TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO monsters (id, name, wisdom, type) VALUES
        ('goblin_1', 'Goblin', 10, 'humanoid'),
        ('goblin_2', 'Goblin', 10, 'humanoid'),
        ('goblin_3', 'Goblin', 12, 'humanoid'),
        ('ogre_1', 'Ogre', 8, 'giant'),
        ('wolf_1', 'Wolf', 12, 'beast')
    """)

    conn.commit()
    conn.close()

    yield TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_track_combat_start(setup_db):
    """Test initial morale tracking"""
    manager = MoraleManager(TEST_DB)

    manager.track_combat_start("encounter_1", "goblin_1", "Goblin", 3, 7)

    status = manager.get_morale_status("encounter_1", "goblin_1")
    assert status is not None
    assert status['monster_name'] == "Goblin"
    assert status['initial_count'] == 3
    assert status['current_count'] == 3
    assert status['initial_hp'] == 7


def test_morale_trigger_group(setup_db):
    """Test morale trigger for group (count-based)"""
    manager = MoraleManager(TEST_DB)

    manager.track_combat_start("encounter_1", "goblin_1", "Goblin", 4, 7)

    triggered = manager.check_morale_trigger("encounter_1", "goblin_1", 5, is_solo=False)
    assert not triggered

    manager.update_monster_count("encounter_1", "goblin_1", 1)

    triggered = manager.check_morale_trigger("encounter_1", "goblin_1", 5, is_solo=False)
    assert triggered


def test_morale_trigger_solo(setup_db):
    """Test morale trigger for solo monster (HP-based)"""
    manager = MoraleManager(TEST_DB)

    manager.track_combat_start("encounter_1", "ogre_1", "Ogre", 1, 59)

    triggered = manager.check_morale_trigger("encounter_1", "ogre_1", 30, is_solo=True)
    assert not triggered

    triggered = manager.check_morale_trigger("encounter_1", "ogre_1", 29, is_solo=True)
    assert triggered


def test_wisdom_modifier(setup_db):
    """Test Wisdom modifier calculation"""
    manager = MoraleManager(TEST_DB)

    wis_mod = manager.get_wisdom_modifier("goblin_1")
    assert wis_mod == 0

    wis_mod = manager.get_wisdom_modifier("goblin_3")
    assert wis_mod == 1

    wis_mod = manager.get_wisdom_modifier("ogre_1")
    assert wis_mod == -1

    wis_mod = manager.get_wisdom_modifier("wolf_1")
    assert wis_mod == 1


def test_highest_wisdom_modifier(setup_db):
    """Test getting highest WIS modifier from group"""
    manager = MoraleManager(TEST_DB)

    highest = manager.get_highest_wisdom_modifier(["goblin_1", "goblin_2", "goblin_3"])
    assert highest == 1

    highest = manager.get_highest_wisdom_modifier(["ogre_1"])
    assert highest == -1


def test_morale_check(setup_db):
    """Test morale check rolling"""
    manager = MoraleManager(TEST_DB)

    manager.track_combat_start("encounter_1", "goblin_1", "Goblin", 3, 7)

    result = manager.roll_morale_check("encounter_1", "goblin_1", ["goblin_1", "goblin_2", "goblin_3"])

    assert 'passed' in result
    assert 'roll' in result
    assert 'modifier' in result
    assert 'total' in result
    assert result['dc'] == 15
    assert 1 <= result['roll'] <= 20
    assert result['total'] == result['roll'] + result['modifier']


def test_morale_check_only_once(setup_db):
    """Test that morale check only happens once"""
    manager = MoraleManager(TEST_DB)

    manager.track_combat_start("encounter_1", "goblin_1", "Goblin", 4, 7)
    manager.update_monster_count("encounter_1", "goblin_1", 1)

    triggered = manager.check_morale_trigger("encounter_1", "goblin_1", 5, is_solo=False)
    assert triggered

    result = manager.roll_morale_check("encounter_1", "goblin_1")
    assert result is not None

    triggered_again = manager.check_morale_trigger("encounter_1", "goblin_1", 5, is_solo=False)
    assert not triggered_again


def test_clear_encounter(setup_db):
    """Test clearing encounter morale data"""
    manager = MoraleManager(TEST_DB)

    manager.track_combat_start("encounter_1", "goblin_1", "Goblin", 3, 7)
    manager.track_combat_start("encounter_1", "goblin_2", "Goblin", 3, 7)

    manager.clear_encounter_morale("encounter_1")

    status = manager.get_morale_status("encounter_1", "goblin_1")
    assert status is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
