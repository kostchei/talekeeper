"""
Comprehensive tests for Fighter weapon mastery mechanics.

Tests weapon mastery effects, reordering during rests, Tactical Master
substitution at level 9+, and interaction with the UI system.
"""

import pytest
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.fixtures.fighter_test_database import FighterTestDatabase
from services.weapon_attack_service import WeaponAttackService
from services.fighter_abilities import FighterAbilitiesService
from core.game_engine_sqlite import GameEngineSQLite


class TestWeaponMasteryBasics:
    """Test basic weapon mastery mechanics for Fighters."""

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

    def test_fighter_weapon_mastery_availability(self, weapon_service):
        """Test Fighters get weapon mastery from level 1."""
        # Level 1 Fighter should have weapon mastery
        attack_data = weapon_service.calculate_attack(
            character_id='fighter-1',
            weapon_name='Longsword',
            attack_type='melee',
            target_ac=12
        )

        assert 'mastery_effects' in attack_data
        assert attack_data['mastery_effects']['available'] is True
        assert attack_data['mastery_effects']['mastery_name'] == 'Sap'

    def test_sap_mastery_effect(self, weapon_service):
        """Test Sap mastery effect reduces target's next attack roll."""
        with patch('random.randint', return_value=15):  # Hit
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=12
            )

            mastery = attack_data['mastery_effects']
            assert mastery['mastery_name'] == 'Sap'
            assert mastery['triggered'] is True
            assert 'next attack roll' in mastery['effect_description'].lower()
            assert mastery['target_penalty'] == -1  # -1 to next attack

    def test_vex_mastery_effect(self, weapon_service):
        """Test Vex mastery grants advantage on next attack against same target."""
        with patch('random.randint', return_value=16):  # Hit
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3',  # Has Rapier with Vex
                weapon_name='Rapier',
                attack_type='melee',
                target_ac=12
            )

            mastery = attack_data['mastery_effects']
            assert mastery['mastery_name'] == 'Vex'
            assert mastery['triggered'] is True
            assert 'advantage' in mastery['effect_description'].lower()

    def test_graze_mastery_effect(self, weapon_service):
        """Test Graze mastery deals damage on miss."""
        with patch('random.randint', return_value=8):  # Miss (8 + mods < 13 AC)
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-9',  # Has Greatsword with Graze
                weapon_name='Greatsword',
                attack_type='melee',
                target_ac=16  # High AC to ensure miss
            )

            assert attack_data['hit'] is False
            mastery = attack_data['mastery_effects']
            assert mastery['mastery_name'] == 'Graze'
            assert mastery['triggered'] is True
            assert mastery['graze_damage'] > 0  # Should deal some damage on miss

    def test_topple_mastery_effect(self, weapon_service):
        """Test Topple mastery can knock target prone."""
        with patch('random.randint', return_value=18):  # Hit
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-2',  # Has Battleaxe with Topple
                weapon_name='Battleaxe',
                attack_type='melee',
                target_ac=12
            )

            mastery = attack_data['mastery_effects']
            assert mastery['mastery_name'] == 'Topple'
            assert mastery['triggered'] is True
            assert 'prone' in mastery['effect_description'].lower()

    def test_slow_mastery_effect(self, weapon_service):
        """Test Slow mastery reduces target movement."""
        with patch('random.randint', return_value=14):  # Hit
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-5',  # Has Longbow with Slow
                weapon_name='Longbow',
                attack_type='ranged',
                target_ac=12
            )

            mastery = attack_data['mastery_effects']
            assert mastery['mastery_name'] == 'Slow'
            assert mastery['triggered'] is True
            assert 'movement' in mastery['effect_description'].lower()

    def test_non_mastery_class_no_effects(self, weapon_service, fighter_db):
        """Test non-mastery classes don't get mastery effects."""
        # Create a Wizard character
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, strength, dexterity
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('wizard-1', 'Test Wizard', 'wizard', 1, 10, 14))

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('wizard-1', 'Dagger', 1, 1))

        conn.commit()
        conn.close()

        with patch('random.randint', return_value=15):
            attack_data = weapon_service.calculate_attack(
                character_id='wizard-1',
                weapon_name='Dagger',
                attack_type='melee',
                target_ac=12
            )

            # Should not have mastery effects
            assert attack_data['mastery_effects']['available'] is False


class TestTacticalMasterSubstitution:
    """Test Tactical Master feature at level 9+."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def fighter_service(self, fighter_db):
        """Create FighterAbilitiesService with test database."""
        return FighterAbilitiesService(fighter_db)

    def test_tactical_master_push_substitution(self, fighter_service, fighter_db):
        """Test level 9+ Fighters can substitute Push mastery."""
        # Add weapon with Push mastery to level 9 Fighter
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('fighter-9', 'Pike', 1, 1))

        # Pike has Push mastery, but Fighter can substitute
        cursor.execute("""
            INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_name, substituted)
            VALUES (?, ?, ?, ?)
        """, ('fighter-9', 'Pike', 'Sap', 1))  # Substituted Push with Sap

        conn.commit()
        conn.close()

        result = fighter_service.get_weapon_mastery_for_weapon('fighter-9', 'Pike')
        assert result['mastery_name'] == 'Sap'  # Should be substituted
        assert result['substituted'] is True
        assert result['original_mastery'] == 'Push'

    def test_tactical_master_sap_substitution(self, fighter_service, fighter_db):
        """Test level 9+ Fighters can substitute Sap mastery."""
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        # Fighter-9 already has Greatsword with Graze, add one with Sap to substitute
        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('fighter-9', 'Maul', 1, 0))

        # Substitute Sap with Topple
        cursor.execute("""
            INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_name, substituted)
            VALUES (?, ?, ?, ?)
        """, ('fighter-9', 'Maul', 'Topple', 1))

        conn.commit()
        conn.close()

        result = fighter_service.get_weapon_mastery_for_weapon('fighter-9', 'Maul')
        assert result['mastery_name'] == 'Topple'
        assert result['substituted'] is True

    def test_tactical_master_slow_substitution(self, fighter_service, fighter_db):
        """Test level 9+ Fighters can substitute Slow mastery."""
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        # Add weapon with Slow mastery
        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('fighter-9', 'Heavy Crossbow', 1, 0))

        # Substitute Slow with Vex
        cursor.execute("""
            INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_name, substituted)
            VALUES (?, ?, ?, ?)
        """, ('fighter-9', 'Heavy Crossbow', 'Vex', 1))

        conn.commit()
        conn.close()

        result = fighter_service.get_weapon_mastery_for_weapon('fighter-9', 'Heavy Crossbow')
        assert result['mastery_name'] == 'Vex'
        assert result['substituted'] is True

    def test_tactical_master_level_requirement(self, fighter_service):
        """Test Tactical Master only available at level 9+."""
        # Level 5 Fighter cannot substitute masteries
        can_substitute = fighter_service.can_use_tactical_master('fighter-5')
        assert can_substitute is False

        # Level 9 Fighter can substitute
        can_substitute = fighter_service.can_use_tactical_master('fighter-9')
        assert can_substitute is True

    def test_tactical_master_only_specific_masteries(self, fighter_service):
        """Test Tactical Master only allows substituting Push, Sap, and Slow."""
        substitutable = fighter_service.get_substitutable_masteries('fighter-9')

        assert 'Push' in substitutable
        assert 'Sap' in substitutable
        assert 'Slow' in substitutable

        # Should not be able to substitute these
        assert 'Vex' not in substitutable
        assert 'Graze' not in substitutable
        assert 'Topple' not in substitutable
        assert 'Cleave' not in substitutable

    def test_tactical_master_ui_interaction(self, fighter_service, fighter_db):
        """Test UI shows substitution options for Tactical Master."""
        # This would test that the UI properly displays mastery substitution options
        # and allows the player to select alternatives during rest periods

        available_options = fighter_service.get_mastery_substitution_options('fighter-9')

        assert len(available_options) > 0
        assert all('original' in option for option in available_options)
        assert all('substitutes' in option for option in available_options)


class TestWeaponMasteryReordering:
    """Test weapon mastery reordering during rests."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def game_engine(self, fighter_db):
        """Create GameEngine with test database."""
        return GameEngineSQLite(fighter_db)

    @pytest.fixture
    def fighter_service(self, fighter_db):
        """Create FighterAbilitiesService with test database."""
        return FighterAbilitiesService(fighter_db)

    def test_mastery_reordering_during_long_rest(self, game_engine, fighter_service):
        """Test Fighters can reorder weapon masteries during long rest."""
        # Get current mastery order
        original_order = fighter_service.get_weapon_mastery_order('fighter-5')

        # Simulate reordering
        new_order = ['Longbow', 'Longsword']  # Swap order
        fighter_service.reorder_weapon_masteries('fighter-5', new_order)

        # Take long rest
        game_engine.take_long_rest('fighter-5')

        # Verify order changed
        current_order = fighter_service.get_weapon_mastery_order('fighter-5')
        assert current_order == new_order

    def test_mastery_persistence_across_rests(self, game_engine, fighter_service):
        """Test Fighter retains all weapon masteries after rest."""
        # Fighters should keep access to all weapon masteries they've learned
        original_masteries = fighter_service.get_all_weapon_masteries('fighter-9')

        # Take long rest
        game_engine.take_long_rest('fighter-9')

        # Should still have all masteries
        current_masteries = fighter_service.get_all_weapon_masteries('fighter-9')
        assert len(current_masteries) == len(original_masteries)

        for mastery in original_masteries:
            assert mastery in current_masteries

    def test_no_mastery_slot_tracking(self, fighter_service):
        """Test Fighters don't have limited mastery slots (per documentation)."""
        # Fighters should have access to all weapon masteries without slot restrictions
        masteries = fighter_service.get_available_masteries('fighter-9')

        # Should not have a 'slots_used' or 'max_slots' limitation
        assert 'slots_used' not in masteries
        assert 'max_slots' not in masteries
        assert masteries['unlimited_access'] is True

    def test_mastery_reordering_preserves_substitutions(self, fighter_service):
        """Test reordering preserves Tactical Master substitutions."""
        # Set up substitution
        fighter_service.substitute_weapon_mastery('fighter-9', 'Greatsword', 'Push', 'Sap')

        # Reorder weapons
        new_order = ['Greatsword', '+1 Greataxe']
        fighter_service.reorder_weapon_masteries('fighter-9', new_order)

        # Substitution should be preserved
        mastery_info = fighter_service.get_weapon_mastery_for_weapon('fighter-9', 'Greatsword')
        assert mastery_info['substituted'] is True
        assert mastery_info['mastery_name'] == 'Sap'


class TestWeaponMasteryUIIntegration:
    """Test weapon mastery UI display and interaction."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    def test_mastery_tooltip_display(self, fighter_db):
        """Test weapon tooltips show correct mastery information."""
        from services.weapon_attack_service import WeaponAttackService

        service = WeaponAttackService(fighter_db)

        # Get weapon info with mastery
        weapon_info = service.get_weapon_display_info('fighter-3', 'Rapier')

        assert 'mastery' in weapon_info
        assert weapon_info['mastery']['name'] == 'Vex'
        assert 'tooltip' in weapon_info['mastery']
        assert 'advantage' in weapon_info['mastery']['tooltip'].lower()

    def test_mastery_substitution_ui_indication(self, fighter_db):
        """Test UI indicates when masteries are substituted."""
        from services.fighter_abilities import FighterAbilitiesService

        service = FighterAbilitiesService(fighter_db)

        # Set up substitution for testing
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE character_weapon_masteries
            SET mastery_name = 'Topple', substituted = 1, original_mastery = 'Graze'
            WHERE character_id = 'fighter-9' AND weapon_name = 'Greatsword'
        """)

        conn.commit()
        conn.close()

        display_info = service.get_weapon_mastery_display('fighter-9', 'Greatsword')

        assert display_info['substituted'] is True
        assert display_info['display_text'].startswith('Topple*')  # Asterisk indicates substitution
        assert 'originally Graze' in display_info['tooltip']

    def test_mastery_reordering_ui_feedback(self, fighter_db):
        """Test UI provides feedback during mastery reordering."""
        from services.fighter_abilities import FighterAbilitiesService

        service = FighterAbilitiesService(fighter_db)

        # Test reordering validation
        current_weapons = ['Greatsword', '+1 Greataxe']
        new_order = ['+1 Greataxe', 'Greatsword']

        validation = service.validate_mastery_reorder('fighter-9', new_order)

        assert validation['valid'] is True
        assert 'message' in validation
        assert len(validation['preview']) == len(new_order)


class TestWeaponMasteryEdgeCases:
    """Test edge cases and error conditions for weapon mastery."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    def test_mastery_with_magical_weapons(self, fighter_db):
        """Test weapon mastery works with magical weapon variants."""
        from services.weapon_attack_service import WeaponAttackService

        service = WeaponAttackService(fighter_db)

        # +1 Greataxe should have same mastery as base Greataxe (Cleave)
        with patch('random.randint', return_value=15):
            attack_data = service.calculate_attack(
                character_id='fighter-9',
                weapon_name='+1 Greataxe',
                attack_type='melee',
                target_ac=12
            )

        assert attack_data['mastery_effects']['mastery_name'] == 'Cleave'

    def test_mastery_with_improvised_weapons(self, fighter_db):
        """Test mastery behavior with improvised weapons."""
        from services.weapon_attack_service import WeaponAttackService

        service = WeaponAttackService(fighter_db)

        # Improvised weapons should not have mastery
        with patch('random.randint', return_value=12):
            attack_data = service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Improvised Weapon',
                attack_type='melee',
                target_ac=10
            )

        assert attack_data['mastery_effects']['available'] is False

    def test_mastery_multiclass_interaction(self, fighter_db):
        """Test weapon mastery for multiclass characters."""
        # Create Fighter/Rogue multiclass
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, strength, dexterity
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('fighter-rogue', 'Fighter/Rogue', 'fighter', 6, 16, 16))

        # Add both Fighter and Rogue class levels
        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
            VALUES (?, ?, ?, ?)
        """, ('fighter-rogue', 'fighter', None, 3))

        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
            VALUES (?, ?, ?, ?)
        """, ('fighter-rogue', 'rogue', None, 3))

        conn.commit()
        conn.close()

        from services.fighter_abilities import FighterAbilitiesService
        service = FighterAbilitiesService(fighter_db)

        # Should have mastery from both Fighter and Rogue
        can_use_mastery = service.character_has_weapon_mastery('fighter-rogue')
        assert can_use_mastery is True


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])