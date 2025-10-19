#test
"""
Comprehensive tests for Fighter combat flow and fighting styles.

Tests complete attack sequences with all fighting styles, damage calculations,
modifier applications, and integration with weapon mastery effects.
"""

import pytest
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.fixtures.fighter_test_database import FighterTestDatabase
from services.weapon_attack_service import WeaponAttackService
from core.combat_manager import CombatManager


class TestFightingStyleEffects:
    """Test all Fighter fighting style mechanics."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def weapon_service(self, fighter_db):
        """Create WeaponAttackService with test database."""
        return WeaponAttackService(fighter_db)

    def test_defense_fighting_style_ac_bonus(self, weapon_service, fighter_db):
        """Test Defense fighting style adds +1 AC when wearing armor."""
        # Fighter-1 has Defense style and Chain Mail
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT armor_class FROM characters WHERE id = ?
        """, ('fighter-1',))
        ac = cursor.fetchone()[0]
        conn.close()

        # Should have base Chain Mail (16) + Defense (+1) = 17 AC
        assert ac >= 17, f"Defense fighting style should provide +1 AC, got {ac}"

    def test_dueling_fighting_style_damage_bonus(self, weapon_service):
        """Test Dueling adds +2 damage to one-handed weapon attacks."""
        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [15, 6]  # Attack roll, damage roll

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3',  # Has Dueling style
                weapon_name='Rapier',
                attack_type='melee',
                target_ac=12
            )

            assert attack_data['hit'] is True

            # Base damage (6) + DEX mod (2) + Dueling (+2) = 10
            total_damage = attack_data['damage']['total']
            assert total_damage >= 10, f"Dueling should add +2 damage, got {total_damage}"

            # Verify Dueling bonus is specifically listed
            damage_breakdown = attack_data['damage']['breakdown']
            assert any('Dueling' in component['source'] for component in damage_breakdown)

    def test_dueling_no_bonus_with_shield_and_two_handed(self, weapon_service, fighter_db):
        """Test Dueling doesn't apply with two-handed weapons."""
        # Add a two-handed weapon to Dueling Fighter
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('fighter-3', 'Greatsword', 1, 1))

        conn.commit()
        conn.close()

        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [15, 8, 4]  # Attack, 2d6 damage

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3',
                weapon_name='Greatsword',
                attack_type='melee',
                target_ac=12
            )

            # Should not get Dueling bonus with two-handed weapon
            damage_breakdown = attack_data['damage']['breakdown']
            assert not any('Dueling' in component['source'] for component in damage_breakdown)

    def test_great_weapon_fighting_treats_low_rolls_as_three(self, weapon_service):
        """Test Great Weapon Fighting treats 1s and 2s as 3s per D&D 2024."""
        with patch('random.randint') as mock_roll:
            # Attack hits, damage rolls are 1, 2 (should become 3, 3)
            mock_roll.side_effect = [16, 1, 2]

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-9',  # Has Great Weapon Fighting
                weapon_name='Greatsword',
                attack_type='melee',
                target_ac=12
            )

            # 2d6 with 1,2 becomes 3,3 = 6 + STR mod (4) = 10
            base_damage = 6  # 3 + 3 from treated rolls
            str_mod = 4     # STR 18 = +4
            expected_min = base_damage + str_mod

            total_damage = attack_data['damage']['total']
            assert total_damage >= expected_min, f"GWF should treat 1s,2s as 3s, got {total_damage}"

    def test_great_weapon_fighting_no_effect_on_normal_rolls(self, weapon_service):
        """Test Great Weapon Fighting doesn't affect rolls of 3 or higher."""
        with patch('random.randint') as mock_roll:
            # Attack hits, damage rolls are 4, 5 (should stay 4, 5)
            mock_roll.side_effect = [16, 4, 5]

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-9',
                weapon_name='Greatsword',
                attack_type='melee',
                target_ac=12
            )

            # Should be 4 + 5 + STR mod (4) = 13
            expected_damage = 4 + 5 + 4
            total_damage = attack_data['damage']['total']
            assert total_damage == expected_damage

    def test_archery_fighting_style_attack_bonus(self, weapon_service):
        """Test Archery adds +2 to ranged weapon attack rolls."""
        with patch('random.randint', return_value=10):  # Base roll of 10

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-5',  # Has Archery style
                weapon_name='Longbow',
                attack_type='ranged',
                target_ac=14
            )

            # Base roll (10) + DEX mod (2) + Prof (3) + Archery (+2) = 17
            attack_bonus = attack_data['attack_roll']['total_bonus']
            assert attack_bonus >= 7, f"Archery should provide +2 attack bonus, got {attack_bonus}"

            assert attack_data['hit'] is True  # Should hit AC 14 with bonuses

    def test_archery_no_bonus_for_melee(self, weapon_service):
        """Test Archery doesn't apply to melee attacks."""
        with patch('random.randint', return_value=12):

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-5',  # Has Archery style
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=12
            )

            # Should not get Archery bonus for melee
            attack_breakdown = attack_data['attack_roll']['breakdown']
            assert not any('Archery' in component['source'] for component in attack_breakdown)

    def test_two_weapon_fighting_offhand_modifier(self, weapon_service, fighter_db):
        """Test Two-Weapon Fighting adds ability modifier to off-hand damage."""
        # Set up Fighter with TWF and light weapons
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE character_features SET feature_name = 'Two-Weapon Fighting'
            WHERE character_id = 'fighter-10' AND feature_type = 'fighting_style'
        """)

        # Add light weapons for TWF
        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('fighter-10', 'Scimitar', 2, 1))

        conn.commit()
        conn.close()

        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [15, 4, 13, 3]  # Main attack, damage, off-hand attack, damage

            # Main hand attack
            main_attack = weapon_service.calculate_attack(
                character_id='fighter-10',
                weapon_name='Scimitar',
                attack_type='melee',
                target_ac=12
            )

            # Off-hand attack (with TWF should get ability modifier)
            offhand_attack = weapon_service.calculate_offhand_attack(
                character_id='fighter-10',
                weapon_name='Scimitar',
                target_ac=12
            )

            # Off-hand should include ability modifier with TWF
            offhand_damage = offhand_attack['damage']['total']
            assert offhand_damage >= 3 + 2, "TWF should add ability mod to off-hand damage"

    def test_protection_fighting_style_reaction(self, weapon_service, fighter_db):
        """Test Protection fighting style allows imposing disadvantage as reaction."""
        # Fighter-2 has Protection style
        protection_available = weapon_service.check_protection_available('fighter-2')

        assert protection_available['available'] is True
        assert protection_available['requires_shield'] is True
        assert protection_available['range'] == 5  # 5 feet


class TestCombatSequenceIntegration:
    """Test complete combat sequences with all Fighter features."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def combat_manager(self, fighter_db):
        """Create CombatManager with test database."""
        return CombatManager(fighter_db)

    @pytest.fixture
    def weapon_service(self, fighter_db):
        """Create WeaponAttackService with test database."""
        return WeaponAttackService(fighter_db)

    def test_full_attack_sequence_with_extra_attack(self, combat_manager, weapon_service):
        """Test complete attack sequence with Extra Attack."""
        # Set up combat with level 5 Fighter (has Extra Attack)
        combat_manager.add_player_combatant({
            'id': 'fighter-5',
            'name': 'Seasoned Fighter',
            'ac': 17,
            'hp': 45,
            'max_hp': 45,
            'class_id': 'fighter',
            'level': 5
        })

        combat_manager.add_enemy_combatant({
            'id': 'orc-1',
            'name': 'Orc',
            'ac': 13,
            'hp': 15,
            'max_hp': 15
        })

        combat_manager.start_combat()

        with patch('random.randint') as mock_roll:
            # Two attacks: both hit, deal damage
            mock_roll.side_effect = [15, 6, 14, 5]  # Attack1, dmg1, attack2, dmg2

            # Perform full attack action
            attacks = weapon_service.perform_full_attack_action(
                character_id='fighter-5',
                weapon_name='Longsword',
                target_ac=13
            )

            assert len(attacks) == 2  # Should get 2 attacks from Extra Attack
            assert all(attack['hit'] for attack in attacks)

            total_damage = sum(attack['damage']['total'] for attack in attacks)
            assert total_damage > 10  # Should deal significant damage

    def test_action_surge_doubles_attacks(self, combat_manager, weapon_service, fighter_db):
        """Test Action Surge allows doubling attack actions."""
        from services.fighter_abilities import FighterAbilitiesService

        fighter_service = FighterAbilitiesService(fighter_db)

        # Set up combat
        combat_manager.add_player_combatant({
            'id': 'fighter-5',
            'name': 'Fighter',
            'ac': 17,
            'hp': 45,
            'max_hp': 45,
            'class_id': 'fighter',
            'level': 5
        })

        combat_manager.start_combat()

        # Use Action Surge
        fighter_service.use_action_surge('fighter-5')

        with patch('random.randint') as mock_roll:
            # 4 attacks total (2 from each Attack action)
            mock_roll.side_effect = [15, 6, 14, 5, 16, 7, 13, 4]

            # First Attack action
            attacks1 = weapon_service.perform_full_attack_action(
                character_id='fighter-5',
                weapon_name='Longsword',
                target_ac=13
            )

            # Second Attack action (from Action Surge)
            attacks2 = weapon_service.perform_full_attack_action(
                character_id='fighter-5',
                weapon_name='Longsword',
                target_ac=13
            )

            total_attacks = len(attacks1) + len(attacks2)
            assert total_attacks == 4  # Should get 4 total attacks

    def test_critical_hit_damage_doubling(self, weapon_service):
        """Test critical hits double damage dice correctly."""
        with patch('random.randint') as mock_roll:
            # Critical hit (20), then damage rolls
            mock_roll.side_effect = [20, 6, 4]  # Crit, base damage, extra damage

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3',
                weapon_name='Rapier',
                attack_type='melee',
                target_ac=12
            )

            assert attack_data['critical_hit'] is True

            # Critical should double dice, not total damage
            # Rapier: 1d8 + DEX, crit = 2d8 + DEX
            damage = attack_data['damage']['total']
            assert damage >= 10  # Should be substantial critical damage

    def test_fighting_style_and_mastery_combination(self, weapon_service):
        """Test fighting style effects combine with weapon mastery."""
        with patch('random.randint', return_value=16):  # Hit

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-3',  # Dueling style
                weapon_name='Rapier',     # Vex mastery
                attack_type='melee',
                target_ac=12
            )

            assert attack_data['hit'] is True

            # Should have both Dueling damage bonus and Vex mastery effect
            damage_breakdown = attack_data['damage']['breakdown']
            dueling_applied = any('Dueling' in comp['source'] for comp in damage_breakdown)

            mastery_effects = attack_data['mastery_effects']
            vex_applied = mastery_effects['mastery_name'] == 'Vex'

            assert dueling_applied, "Dueling fighting style should apply"
            assert vex_applied, "Vex weapon mastery should apply"

    def test_damage_resistance_interaction(self, weapon_service, fighter_db):
        """Test Fighter damage vs resistant creatures."""
        # Add resistant enemy to database
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO creatures (
                id, name, ac, hp, max_hp, damage_resistances
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('skeleton-1', 'Skeleton', 13, 13, 13, 'slashing'))

        conn.commit()
        conn.close()

        with patch('random.randint') as mock_roll:
            mock_roll.side_effect = [15, 8]  # Hit, damage

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Longsword',  # Slashing damage
                attack_type='melee',
                target_ac=13,
                target_resistances=['slashing']
            )

            # Damage should be halved due to resistance
            base_damage = 8 + 3  # Roll + STR mod
            expected_damage = base_damage // 2

            actual_damage = attack_data['damage']['effective']
            assert actual_damage == expected_damage


class TestCombatFlowEdgeCases:
    """Test edge cases and error conditions in combat flow."""

    @pytest.fixture
    def fighter_db(self):
        """Create Fighter test database."""
        with FighterTestDatabase() as db_path:
            yield db_path

    @pytest.fixture
    def weapon_service(self, fighter_db):
        """Create WeaponAttackService with test database."""
        return WeaponAttackService(fighter_db)

    def test_attack_with_missing_weapon(self, weapon_service):
        """Test attack calculation with weapon not in inventory."""
        with pytest.raises(ValueError, match="Weapon .* not found"):
            weapon_service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Nonexistent Sword',
                attack_type='melee',
                target_ac=12
            )

    def test_attack_with_unequipped_weapon(self, weapon_service, fighter_db):
        """Test attack with weapon in inventory but not equipped."""
        # Add unequipped weapon
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO character_inventory (character_id, item_name, quantity, equipped)
            VALUES (?, ?, ?, ?)
        """, ('fighter-1', 'Dagger', 1, 0))  # Not equipped

        conn.commit()
        conn.close()

        # Should still be able to attack (can draw as part of attack)
        with patch('random.randint', return_value=15):
            attack_data = weapon_service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Dagger',
                attack_type='melee',
                target_ac=12
            )

            assert attack_data is not None
            # Might have drawing warning or penalty

    def test_unconscious_character_cannot_attack(self, weapon_service, fighter_db):
        """Test unconscious characters cannot make attacks."""
        # Set character to 0 HP
        conn = sqlite3.connect(fighter_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE characters SET hit_points_current = 0 WHERE id = ?
        """, ('fighter-1',))

        conn.commit()
        conn.close()

        with pytest.raises(ValueError, match="unconscious|cannot attack"):
            weapon_service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=12
            )

    def test_attack_roll_natural_1_always_misses(self, weapon_service):
        """Test natural 1 always misses regardless of bonuses."""
        with patch('random.randint', return_value=1):  # Natural 1

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=5  # Very low AC
            )

            assert attack_data['hit'] is False
            assert attack_data['attack_roll']['natural_roll'] == 1
            assert attack_data['attack_roll']['automatic_miss'] is True

    def test_attack_roll_natural_20_always_hits(self, weapon_service):
        """Test natural 20 always hits and crits regardless of AC."""
        with patch('random.randint', return_value=20):  # Natural 20

            attack_data = weapon_service.calculate_attack(
                character_id='fighter-1',
                weapon_name='Longsword',
                attack_type='melee',
                target_ac=25  # Very high AC
            )

            assert attack_data['hit'] is True
            assert attack_data['critical_hit'] is True
            assert attack_data['attack_roll']['natural_roll'] == 20
            assert attack_data['attack_roll']['automatic_hit'] is True


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])