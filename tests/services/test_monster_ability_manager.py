"""
Tests for Monster Ability Manager

Tests breath weapons, limited use abilities, and save-based effects.
"""

import pytest
import sqlite3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from talekeeper.services.monster_ability_manager import (
    MonsterAbilityManager,
    MonsterAbility,
    AbilityType,
    RechargeType,
    PREDEFINED_ABILITIES
)


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    db_path = "test_monster_abilities.db"

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass

    yield db_path


@pytest.fixture
def manager(test_db):
    """Create a MonsterAbilityManager instance."""
    mgr = MonsterAbilityManager(test_db)
    yield mgr
    del mgr


@pytest.fixture
def sample_character():
    """Sample character data for testing saves."""
    return {
        'id': 'test_char_1',
        'dexterity': 14,
        'constitution': 16,
        'wisdom': 12,
        'proficiency_bonus': 3,
        'save_proficiencies': ['dexterity', 'constitution']
    }


def test_initialize_recharge_ability(manager):
    """Test initializing a recharge ability like dragon breath."""
    encounter_id = "test_encounter_1"
    monster_id = "red_dragon_1"

    fire_breath = PREDEFINED_ABILITIES['fire_breath']

    manager.initialize_ability(encounter_id, monster_id, fire_breath)

    state = manager.get_ability_state(encounter_id, monster_id, "Fire Breath")

    assert state is not None
    assert state.is_available is True
    assert state.ability_name == "Fire Breath"


def test_recharge_mechanics(manager):
    """Test breath weapon recharge mechanics."""
    encounter_id = "test_encounter_1"
    monster_id = "blue_dragon_1"

    lightning_breath = PREDEFINED_ABILITIES['lightning_breath']
    manager.initialize_ability(encounter_id, monster_id, lightning_breath)

    used = manager.use_ability(encounter_id, monster_id, "Lightning Breath")
    assert used is True

    state = manager.get_ability_state(encounter_id, monster_id, "Lightning Breath")
    assert state.is_available is False

    for _ in range(10):
        success, roll = manager.attempt_recharge(encounter_id, monster_id, "Lightning Breath")
        if success:
            assert roll >= 5
            state = manager.get_ability_state(encounter_id, monster_id, "Lightning Breath")
            assert state.is_available is True
            break


def test_limited_use_ability(manager):
    """Test limited use ability like Aboleth's Dominate Mind (2/Day)."""
    encounter_id = "test_encounter_1"
    monster_id = "aboleth_1"

    dominate = PREDEFINED_ABILITIES['dominate_mind']
    manager.initialize_ability(encounter_id, monster_id, dominate)

    state = manager.get_ability_state(encounter_id, monster_id, "Dominate Mind")
    assert state.uses_remaining == 2

    manager.use_ability(encounter_id, monster_id, "Dominate Mind")
    state = manager.get_ability_state(encounter_id, monster_id, "Dominate Mind")
    assert state.uses_remaining == 1
    assert state.is_available is True

    manager.use_ability(encounter_id, monster_id, "Dominate Mind")
    state = manager.get_ability_state(encounter_id, monster_id, "Dominate Mind")
    assert state.uses_remaining == 0
    assert state.is_available is False

    cannot_use = manager.use_ability(encounter_id, monster_id, "Dominate Mind")
    assert cannot_use is False


def test_execute_ability_with_save(manager, sample_character):
    """Test executing an ability that requires a saving throw."""
    encounter_id = "test_encounter_1"
    monster_id = "dragon_1"

    frightful_presence = PREDEFINED_ABILITIES['frightful_presence']
    manager.initialize_ability(encounter_id, monster_id, frightful_presence)

    result = manager.execute_ability(
        encounter_id,
        monster_id,
        "Ancient Red Dragon",
        frightful_presence,
        sample_character['id'],
        sample_character
    )

    assert result['success'] is True
    assert 'save_roll' in result
    assert 'save_total' in result
    assert 'save_success' in result
    assert result['save_dc'] == 19
    assert len(result['messages']) >= 2


def test_execute_breath_weapon_damage(manager, sample_character):
    """Test breath weapon execution with damage."""
    encounter_id = "test_encounter_1"
    monster_id = "red_dragon_1"

    fire_breath = PREDEFINED_ABILITIES['fire_breath']
    manager.initialize_ability(encounter_id, monster_id, fire_breath)

    result = manager.execute_ability(
        encounter_id,
        monster_id,
        "Adult Red Dragon",
        fire_breath,
        sample_character['id'],
        sample_character
    )

    assert result['success'] is True
    assert 'damage' in result
    assert result['damage'] > 0
    assert result['damage_type'] == 'fire'

    if result['save_success']:
        expected_damage = manager.dice_roller.roll("18d6") // 2
    else:
        expected_damage = manager.dice_roller.roll("18d6")


def test_condition_application(manager, sample_character):
    """Test that failed saves apply conditions."""
    encounter_id = "test_encounter_1"
    monster_id = "ghoul_1"

    paralyzing_touch = PREDEFINED_ABILITIES['paralyzing_touch']
    manager.initialize_ability(encounter_id, monster_id, paralyzing_touch)

    result = manager.execute_ability(
        encounter_id,
        monster_id,
        "Ghoul",
        paralyzing_touch,
        sample_character['id'],
        sample_character
    )

    if not result.get('save_success'):
        assert 'condition_applied' in result
        assert result['condition_applied'] == 'paralyzed'


def test_reset_daily_abilities(manager):
    """Test resetting daily abilities on long rest."""
    encounter_id = "test_encounter_1"
    monster_id = "aboleth_1"

    dominate = PREDEFINED_ABILITIES['dominate_mind']
    manager.initialize_ability(encounter_id, monster_id, dominate)

    manager.use_ability(encounter_id, monster_id, "Dominate Mind")
    manager.use_ability(encounter_id, monster_id, "Dominate Mind")

    state = manager.get_ability_state(encounter_id, monster_id, "Dominate Mind")
    assert state.uses_remaining == 0

    manager.reset_daily_abilities(encounter_id, monster_id)

    state = manager.get_ability_state(encounter_id, monster_id, "Dominate Mind")
    assert state.uses_remaining == 2
    assert state.is_available is True


def test_get_all_monster_abilities(manager):
    """Test retrieving all abilities for a monster."""
    encounter_id = "test_encounter_1"
    monster_id = "dragon_1"

    manager.initialize_ability(encounter_id, monster_id, PREDEFINED_ABILITIES['fire_breath'])
    manager.initialize_ability(encounter_id, monster_id, PREDEFINED_ABILITIES['frightful_presence'])

    abilities = manager.get_all_monster_abilities(encounter_id, monster_id)

    assert len(abilities) == 2
    ability_names = [a.ability_name for a in abilities]
    assert "Fire Breath" in ability_names
    assert "Frightful Presence" in ability_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
