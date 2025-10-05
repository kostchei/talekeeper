"""
Comprehensive tests for Fighter Champion subclass features.

Tests Improved Critical, Remarkable Athlete, Additional Fighting Style,
Heroic Warrior, Studied Attacks, and Survivor according to D&D 2024 rules.
"""

import pytest
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.fixtures.fighter_test_database import FighterTestDatabase
from services.fighter_abilities import FighterAbilitiesService
from services.weapon_attack_service import WeaponAttackService
from services.advantage_system import AdvantageSystem
from core.combat_manager import CombatManager


class TestChampionImprovedCritical:
    """Test Champion's Improved Critical feature."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def weapon_service(self, fighter_db):
        """Create WeaponAttackService with test database."""
        return WeaponAttackService(fighter_db)

    def test_improved_critical_19_20_range(self, weapon_service):
        """Test Champion crits on 19-20 instead of just 20."""
        # Test roll of 19 - should be critical for Champion
        with patch('random.randint', return_value=19):
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3',  # Level 3 Champion
                weapon_name='Rapier',
                attack_type='melee',
                target_ac=12
            )

            assert attack_data['critical_hit'] is True
            assert attack_data['attack_roll']['natural_roll'] == 19
            assert attack_data['critical_range_min'] == 19

        # Test roll of 18 - should NOT be critical
        with patch('random.randint', return_value=18):
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3',
                weapon_name='Rapier',
                attack_type='melee',
                target_ac=12
            )

            assert attack_data['critical_hit'] is False

    def test_superior_critical_18_19_20_range(self, weapon_service, fighter_db):
        """Test Champion Superior Critical at level 15 (crits on 18-20)."""
        # Level 15 Champion should crit on 18-20
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE character_combat_state
            SET critical_range_min = 18
            WHERE character_id = 'fighter-15'
        """)

        conn.commit()
        conn.close()

        # Test roll of 18 - should be critical for level 15 Champion
        with patch('random.randint', return_value=18):
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-15',
                weapon_name='+1 Greatsword',
                attack_type='melee',
                target_ac=12
            )

            assert attack_data['critical_hit'] is True
            assert attack_data['critical_range_min'] == 18

    def test_non_champion_normal_critical_range(self, weapon_service, fighter_db):
        """Test non-Champions still crit only on 20."""
        # Create non-Champion Fighter
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, strength, dexterity
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('fighter-3-battlemaster', 'Battlemaster', 'fighter', 3, 16, 14))

        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
            VALUES (?, ?, ?, ?)
        """, ('fighter-3-battlemaster', 'fighter', 'battlemaster', 3))

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('fighter-3-battlemaster', 'Longsword', 1, 1))

        conn.commit()
        conn.close()

        # Roll 19 - should NOT be critical for non-Champion
        with patch('random.randint', return_value=19):
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3-battlemaster',
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=12
            )

            assert attack_data['critical_hit'] is False


class TestChampionRemarkableAthlete:
    """Test Champion's Remarkable Athlete feature."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def fighter_service(self, fighter_db):
        """Create FighterAbilitiesService with test database."""
        return FighterAbilitiesService(fighter_db)

    def test_remarkable_athlete_strength_athletics(self, fighter_service):
        """Test Remarkable Athlete grants advantage on STR (Athletics) checks."""
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [8, 15]  # Two rolls for advantage

            result = fighter_service.roll_skill_check(
                character_id='fighter-3',  # Level 3 Champion
                skill='Athletics',
                ability_modifier=3,
                proficiency_bonus=2,
                proficient=True
            )

            assert result['remarkable_athlete_applied'] is True
            assert result['advantage_state'] == 'advantage'
            assert 'Remarkable Athlete' in result['advantage_sources']
            assert result['total'] == 15 + 3 + 2  # Higher roll + ability + prof

    def test_remarkable_athlete_dexterity_acrobatics(self, fighter_service):
        """Test Remarkable Athlete grants advantage on DEX (Acrobatics) checks."""
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [12, 17]

            result = fighter_service.roll_skill_check(
                character_id='fighter-3',
                skill='Acrobatics',
                ability_modifier=2,
                proficiency_bonus=2,
                proficient=False
            )

            assert result['remarkable_athlete_applied'] is True
            assert result['advantage_state'] == 'advantage'
            assert result['total'] == 17 + 2  # No proficiency

    def test_remarkable_athlete_constitution_saves(self, fighter_service):
        """Test Remarkable Athlete grants advantage on CON saving throws."""
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [9, 14]

            result = fighter_service.roll_saving_throw(
                character_id='fighter-3',
                save_type='constitution',
                dc=13,
                ability_modifier=3,
                proficiency_bonus=2
            )

            assert result['remarkable_athlete_applied'] is True
            assert result['advantage_state'] == 'advantage'
            assert result['total'] == 14 + 3 + 2  # CON save proficiency

    def test_remarkable_athlete_initiative_rolls(self, fighter_service):
        """Test Remarkable Athlete grants advantage on initiative."""
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [7, 16]

            result = fighter_service.roll_initiative(
                character_id='fighter-3',
                dexterity_modifier=2
            )

            assert result['remarkable_athlete_applied'] is True
            assert result['advantage_state'] == 'advantage'
            assert result['total'] == 16 + 2

    def test_remarkable_athlete_not_applied_to_other_skills(self, fighter_service):
        """Test Remarkable Athlete doesn't apply to non-covered skills."""
        with patch('random.randint', return_value=12):

            result = fighter_service.roll_skill_check(
                character_id='fighter-3',
                skill='Insight',  # Wisdom skill - not covered
                ability_modifier=1,
                proficiency_bonus=2,
                proficient=False
            )

            assert result['remarkable_athlete_applied'] is False
            assert result['advantage_state'] == 'normal'

    def test_remarkable_athlete_availability_level_3(self, fighter_service):
        """Test Remarkable Athlete is available at Champion level 3."""
        # Level 3 Champion should have it
        has_feature = fighter_service.has_remarkable_athlete('fighter-3')
        assert has_feature is True

        # Level 1 Fighter should not
        has_feature = fighter_service.has_remarkable_athlete('fighter-1')
        assert has_feature is False


class TestChampionHeroicWarrior:
    """Test Champion's Heroic Warrior feature (level 10)."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def fighter_service(self, fighter_db):
        """Create FighterAbilitiesService with test database."""
        return FighterAbilitiesService(fighter_db)

    def test_heroic_warrior_grants_inspiration(self, fighter_service):
        """Test Heroic Warrior grants inspiration at start of turn."""
        result = fighter_service.process_champion_turn_start('fighter-10')

        heroic_info = result['heroic_warrior']
        assert heroic_info['available'] is True
        assert heroic_info['triggered'] is True
        assert heroic_info['current'] == 1
        assert heroic_info['max'] == 1

    def test_heroic_warrior_no_duplicate_inspiration(self, fighter_service, fighter_db):
        """Test Heroic Warrior doesn't grant inspiration if already at max."""
        # Set character to already have inspiration
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters
            SET inspiration_uses_current = 1, inspiration_uses_max = 1
            WHERE id = ?
        """, ('fighter-10',))

        conn.commit()
        conn.close()

        result = fighter_service.process_champion_turn_start('fighter-10')

        heroic_info = result['heroic_warrior']
        assert heroic_info['triggered'] is False  # Should not trigger

    def test_heroic_warrior_level_requirement(self, fighter_service):
        """Test Heroic Warrior requires Champion level 10."""
        # Level 3 Champion should not have it
        result = fighter_service.process_champion_turn_start('fighter-3')

        assert 'heroic_warrior' not in result or result['heroic_warrior']['available'] is False


class TestChampionStudiedAttacks:
    """Test Champion's Studied Attacks feature (level 7)."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def weapon_service(self, fighter_db):
        """Create WeaponAttackService with test database."""
        return WeaponAttackService(fighter_db)

    @pytest.fixture
    def fighter_service(self, fighter_db):
        """Create FighterAbilitiesService with test database."""
        return FighterAbilitiesService(fighter_db)

    def test_studied_attacks_advantage_after_miss(self, weapon_service, fighter_service, fighter_db):
        """Test Studied Attacks grants advantage after missing same target."""
        # Create level 7+ Champion
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters SET level = 7 WHERE id = 'fighter-10'
        """)

        conn.commit()
        conn.close()

        # First attack misses
        with patch('random.randint', return_value=5):  # Miss
            attack1 = weapon_service.calculate_attack(
                character_id='fighter-10',
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=15,
                target_id='orc-1'
            )

            assert attack1['hit'] is False

        # Record the miss for Studied Attacks
        fighter_service.record_attack_miss('fighter-10', 'orc-1')

        # Second attack against same target should have advantage
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [12, 16]  # Advantage rolls

            attack2 = weapon_service.calculate_attack(
                character_id='fighter-10',
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=15,
                target_id='orc-1'
            )

            assert attack2['studied_attacks_advantage'] is True
            assert attack2['advantage_state'] == 'advantage'

    def test_studied_attacks_target_specific(self, fighter_service):
        """Test Studied Attacks advantage is specific to each target."""
        # Miss against target 1
        fighter_service.record_attack_miss('fighter-10', 'orc-1')

        # Should have advantage against orc-1
        has_advantage = fighter_service.has_studied_attacks_advantage('fighter-10', 'orc-1')
        assert has_advantage is True

        # Should NOT have advantage against different target
        has_advantage = fighter_service.has_studied_attacks_advantage('fighter-10', 'goblin-1')
        assert has_advantage is False

    def test_studied_attacks_resets_on_hit(self, fighter_service):
        """Test Studied Attacks advantage resets after hitting."""
        # Miss, then hit same target
        fighter_service.record_attack_miss('fighter-10', 'orc-1')
        fighter_service.record_attack_hit('fighter-10', 'orc-1')

        # Should no longer have advantage
        has_advantage = fighter_service.has_studied_attacks_advantage('fighter-10', 'orc-1')
        assert has_advantage is False


class TestChampionSurvivor:
    """Test Champion's Survivor feature (level 18)."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def fighter_service(self, fighter_db):
        """Create FighterAbilitiesService with test database."""
        return FighterAbilitiesService(fighter_db)

    def test_survivor_healing_when_bloodied(self, fighter_service):
        """Test Survivor heals when starting turn at half HP or less."""
        # Fighter-15 is set up as bloodied (80/160 HP)
        result = fighter_service.process_champion_turn_start('fighter-15')

        survivor_info = result['survivor']
        assert survivor_info['available'] is True
        assert survivor_info['healing_triggered'] is True
        assert survivor_info['healing'] == 5 + 4  # 5 + CON mod (+4 for CON 18)
        assert survivor_info['new_hp'] == 80 + 9  # Current + healing

    def test_survivor_no_healing_when_healthy(self, fighter_service, fighter_db):
        """Test Survivor doesn't heal when above half HP."""
        # Set character to above half HP
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters
            SET hit_points_current = 100
            WHERE id = 'fighter-15'
        """)

        conn.commit()
        conn.close()

        result = fighter_service.process_champion_turn_start('fighter-15')

        survivor_info = result['survivor']
        assert survivor_info['healing_triggered'] is False
        assert survivor_info['healing'] == 0

    def test_survivor_defy_death_at_zero_hp(self, fighter_service, fighter_db):
        """Test Survivor prevents death at 0 HP."""
        # Set character to 0 HP
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters
            SET hit_points_current = 0
            WHERE id = 'fighter-15'
        """)

        conn.commit()
        conn.close()

        result = fighter_service.process_champion_turn_start('fighter-15')

        survivor_info = result['survivor']
        assert survivor_info['defy_death_active'] is True

    def test_survivor_level_requirement(self, fighter_service):
        """Test Survivor requires Champion level 18."""
        # Level 10 Champion should not have Survivor
        result = fighter_service.process_champion_turn_start('fighter-10')

        assert 'survivor' not in result or result['survivor']['available'] is False


class TestChampionFeatureIntegration:
    """Test integration between Champion features."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def combat_manager(self, fighter_db):
        """Create CombatManager with test database."""
        return CombatManager(fighter_db)

    def test_champion_features_in_full_combat(self, combat_manager, fighter_db):
        """Test Champion features work together in complete combat scenario."""
        fighter_service = FighterAbilitiesService(fighter_db)
        weapon_service = WeaponAttackService(fighter_db)

        # Set up combat with high-level Champion
        combat_manager.add_player_combatant({
            'id': 'fighter-15',
            'name': 'Legendary Champion',
            'ac': 19,
            'hp': 80,  # Bloodied for Survivor
            'max_hp': 160,
            'class_id': 'fighter',
            'level': 15
        })

        combat_manager.add_enemy_combatant({
            'id': 'dragon-1',
            'name': 'Young Dragon',
            'ac': 18,
            'hp': 200,
            'max_hp': 200
        })

        combat_manager.start_combat()

        # Turn start: Survivor should heal, Heroic Warrior should grant inspiration
        turn_result = fighter_service.process_champion_turn_start('fighter-15')

        # Should get healing from Survivor
        assert turn_result['survivor']['healing_triggered'] is True

        # Make attack with improved critical range
        with patch('random.randint', return_value=18):  # Should crit with Superior Critical
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-15',
                weapon_name='+1 Greatsword',
                attack_type='melee',
                target_ac=18
            )

            assert attack_data['critical_hit'] is True  # 18 should crit at level 15

    def test_remarkable_athlete_with_champion_combat(self, fighter_db):
        """Test Remarkable Athlete enhances Champion's versatility."""
        fighter_service = FighterAbilitiesService(fighter_db)

        # Test initiative advantage
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [8, 15]

            init_result = fighter_service.roll_initiative('fighter-3', 2)

            assert init_result['remarkable_athlete_applied'] is True
            assert init_result['total'] == 17  # 15 + 2 DEX

        # Test Athletics for grappling
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [10, 18]

            athletics_result = fighter_service.roll_skill_check(
                'fighter-3', 'Athletics', 3, 2, True
            )

            assert athletics_result['remarkable_athlete_applied'] is True
            assert athletics_result['total'] == 23  # 18 + 3 + 2


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])