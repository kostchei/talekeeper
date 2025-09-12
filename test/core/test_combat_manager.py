import pytest
from unittest.mock import MagicMock
from core.combat_manager import CombatManager, CombatantType

@pytest.fixture
def mock_services(mocker):
    """Mocks all external services for CombatManager."""
    mocker.patch('core.combat_manager.EquipmentService')
    mocker.patch('core.combat_manager.ProficiencySystem')
    mocker.patch('core.combat_manager.FightingStyleEffects')
    mocker.patch('core.combat_manager.get_proficiency_bonus', return_value=2)

class TestTwoWeaponFighting:

    def test_two_weapon_fighting_light_weapons_no_style(self, mocker, mock_services):
        """
        Tests that a character with two light weapons can make a bonus action attack,
        and that the damage does NOT include the ability modifier.
        """
        # --- Setup ---
        cm = CombatManager(db_path=':memory:')

        # Mock services
        cm.fighting_style_service.should_add_ability_mod_to_offhand.return_value = False
        cm.fighting_style_service.get_attack_bonus.return_value = 0
        cm.fighting_style_service.get_damage_bonus.return_value = 0
        cm.proficiency_system.is_proficient_with_weapon.return_value = (True, 'weapon')

        scimitar = {
            'name': 'Scimitar', 'item_type': 'weapon', 'damage_dice': '1d6',
            'weapon_properties': ['Light', 'Finesse'], 'damage_bonus': 0, 'attack_bonus': 0
        }
        cm.equipment_service.get_equipped_weapons.return_value = [
            {**scimitar, 'slot': 'main_hand'},
            {**scimitar, 'slot': 'off_hand'}
        ]
        cm.equipment_service.get_equipped_items.return_value = cm.equipment_service.get_equipped_weapons.return_value

        # Setup combatants
        character_data = {
            'id': 'chad', 'name': 'Chad', 'hp': 10, 'max_hp': 10, 'ac': 14,
            'strength': 16, 'dexterity': 14, 'level': 1, 'class_id': 'fighter'
        }
        monster_data = {'id': 'goblin', 'name': 'Goblin', 'hp': 7, 'max_hp': 7, 'ac': 15}

        player = cm.add_player_combatant(character_data)
        monster = cm.add_monster_combatant(monster_data['id'], monster_data)
        cm.start_combat()

        # Ensure it's player's turn
        while not cm.is_player_turn():
            cm.advance_turn()

        # --- Mock Rolls ---
        def mock_randint(low, high):
            if high == 20:  # d20 roll for attack
                return 18
            if high == 6:  # d6 roll for damage
                return 5
            return 1 # Default for other rolls like initiative

        mocker.patch('random.randint', side_effect=mock_randint)

        # --- Main Attack ---
        attack_results = cm.execute_player_attack('chad', scimitar, 'goblin')
        assert len(attack_results['attacks']) == 1
        main_attack = attack_results['attacks'][0]
        assert main_attack['hit']
        # Damage should be 1d6 + STR_MOD(3) = 5 + 3 = 8
        assert main_attack['damage'] == 8

        # --- Bonus Action Attack ---
        offhand_results = cm.execute_offhand_attack('chad', 'goblin')
        assert 'error' not in offhand_results
        assert len(offhand_results['attacks']) == 1
        offhand_attack = offhand_results['attacks'][0]
        assert offhand_attack['hit']
        # Damage should be 1d6 = 5 (no ability modifier)
        assert offhand_attack['damage'] == 5

        # --- Verify Action Economy ---
        assert player.has_taken_action
        assert player.has_taken_bonus_action
        assert player.light_property_attack_used_this_turn

        # Try to attack with bonus action again
        double_dip_results = cm.execute_offhand_attack('chad', 'goblin')
        assert 'error' in double_dip_results
        assert double_dip_results['error'] == 'Bonus action already taken'

    def test_two_weapon_fighting_with_style(self, mocker, mock_services):
        """
        Tests that a character with the Two-Weapon Fighting style adds their
        ability modifier to the off-hand attack damage.
        """
        # --- Setup ---
        cm = CombatManager(db_path=':memory:')
        cm.fighting_style_service.should_add_ability_mod_to_offhand.return_value = True
        cm.fighting_style_service.get_attack_bonus.return_value = 0
        cm.fighting_style_service.get_damage_bonus.return_value = 0
        cm.proficiency_system.is_proficient_with_weapon.return_value = (True, 'weapon')

        scimitar = {'name': 'Scimitar', 'item_type': 'weapon', 'damage_dice': '1d6', 'weapon_properties': ['Light', 'Finesse'], 'damage_bonus': 0, 'attack_bonus': 0}
        cm.equipment_service.get_equipped_weapons.return_value = [{'slot': 'main_hand', **scimitar}, {'slot': 'off_hand', **scimitar}]
        cm.equipment_service.get_equipped_items.return_value = cm.equipment_service.get_equipped_weapons.return_value

        character_data = {'id': 'chad', 'name': 'Chad', 'hp': 10, 'max_hp': 10, 'ac': 14, 'strength': 16, 'dexterity': 14, 'level': 1, 'class_id': 'fighter'}
        monster_data = {'id': 'goblin', 'name': 'Goblin', 'hit_points': 20, 'max_hit_points': 20, 'ac': 15}

        player = cm.add_player_combatant(character_data)
        cm.add_monster_combatant(monster_data['id'], monster_data)
        cm.start_combat()

        # Ensure it's player's turn
        while not cm.is_player_turn():
            cm.advance_turn()

        # --- Mock Rolls ---
        def mock_randint(low, high):
            if high == 20: return 18
            if high == 6: return 5
            return 1
        mocker.patch('random.randint', side_effect=mock_randint)

        # --- Main Attack ---
        cm.execute_player_attack('chad', scimitar, 'goblin')

        # --- Bonus Action Attack ---
        offhand_results = cm.execute_offhand_attack('chad', 'goblin')
        assert 'error' not in offhand_results
        offhand_attack = offhand_results['attacks'][0]
        assert offhand_attack['hit']
        # Damage should be 1d6 + STR_MOD(3) = 5 + 3 = 8
        assert offhand_attack['damage'] == 8

    def test_two_weapon_fighting_with_nick(self, mocker, mock_services):
        """
        Tests that a character with a Nick weapon gets an extra attack as part of the
        Attack Action and cannot use their bonus action for another attack.
        """
        # --- Setup ---
        cm = CombatManager(db_path=':memory:')
        cm.fighting_style_service.should_add_ability_mod_to_offhand.return_value = False
        cm.fighting_style_service.get_attack_bonus.return_value = 0
        cm.fighting_style_service.get_damage_bonus.return_value = 0
        cm.proficiency_system.is_proficient_with_weapon.return_value = (True, 'weapon')

        scimitar_nick = {'name': 'Scimitar of Nicking', 'item_type': 'weapon', 'damage_dice': '1d6', 'weapon_properties': ['Light', 'Finesse', 'Nick'], 'damage_bonus': 0, 'attack_bonus': 0}
        cm.equipment_service.get_equipped_weapons.return_value = [{'slot': 'main_hand', **scimitar_nick}, {'slot': 'off_hand', **scimitar_nick}]
        cm.equipment_service.get_equipped_items.return_value = cm.equipment_service.get_equipped_weapons.return_value

        character_data = {'id': 'chad', 'name': 'Chad', 'hp': 10, 'max_hp': 10, 'ac': 14, 'strength': 16, 'dexterity': 14, 'level': 1, 'class_id': 'fighter'}
        monster_data = {'id': 'goblin', 'name': 'Goblin', 'hit_points': 20, 'max_hit_points': 20, 'ac': 15}

        player = cm.add_player_combatant(character_data)
        cm.add_monster_combatant(monster_data['id'], monster_data)
        cm.start_combat()

        # Ensure it's player's turn
        while not cm.is_player_turn():
            cm.advance_turn()

        # --- Mock Rolls ---
        def mock_randint(low, high):
            if high == 20: return 18
            if high == 6: return 5
            return 1
        mocker.patch('random.randint', side_effect=mock_randint)

        # --- Main Attack with Nick ---
        attack_results = cm.execute_player_attack('chad', scimitar_nick, 'goblin')

        # Should get 2 attacks: 1 base + 1 from Nick
        assert len(attack_results['attacks']) == 2

        main_attack = attack_results['attacks'][0]
        nick_attack = attack_results['attacks'][1]

        assert main_attack['hit']
        assert main_attack['damage'] == 8 # 1d6(5) + STR(3)

        assert nick_attack['hit']
        assert nick_attack['damage'] == 5 # 1d6(5), no STR mod

        # --- Verify Action Economy ---
        assert player.has_taken_action
        assert not player.has_taken_bonus_action # Nick does not use a bonus action
        assert player.light_property_attack_used_this_turn

        # --- Bonus Action Attack should fail ---
        offhand_results = cm.execute_offhand_attack('chad', 'goblin')
        assert 'error' in offhand_results
        assert offhand_results['error'] == 'Light property attack already used this turn'

    def test_dual_wielder_feat_with_non_light_weapons(self, mocker, mock_services):
        """
        Tests that the Dual Wielder feat allows two-weapon fighting with non-Light
        one-handed weapons and grants a +1 AC bonus.
        """
        # --- Setup ---
        cm = CombatManager(db_path=':memory:')
        cm.fighting_style_service.should_add_ability_mod_to_offhand.return_value = False
        cm.fighting_style_service.get_attack_bonus.return_value = 0
        cm.fighting_style_service.get_damage_bonus.return_value = 0
        cm.proficiency_system.is_proficient_with_weapon.return_value = (True, 'weapon')
        # Mock the feat check
        mocker.patch.object(cm, '_get_character_feats', return_value=['Dual Wielder'])

        longsword = {'name': 'Longsword', 'item_type': 'weapon', 'damage_dice': '1d8', 'weapon_properties': ['Versatile (1d10)'], 'damage_bonus': 0, 'attack_bonus': 0}
        cm.equipment_service.get_equipped_weapons.return_value = [{'slot': 'main_hand', **longsword}, {'slot': 'off_hand', **longsword}]
        cm.equipment_service.get_equipped_items.return_value = cm.equipment_service.get_equipped_weapons.return_value

        character_data = {'id': 'chad', 'name': 'Chad', 'hp': 10, 'max_hp': 10, 'ac': 14, 'strength': 16, 'dexterity': 14, 'level': 1, 'class_id': 'fighter'}
        monster_data = {'id': 'goblin', 'name': 'Goblin', 'hit_points': 20, 'max_hit_points': 20, 'ac': 15}

        player = cm.add_player_combatant(character_data)
        cm.add_monster_combatant(monster_data['id'], monster_data)
        cm.start_combat()

        # --- Assert AC Bonus ---
        assert player.armor_class == 15 # 14 base + 1 from Dual Wielder

        # Ensure it's player's turn
        while not cm.is_player_turn():
            cm.advance_turn()

        # --- Mock Rolls ---
        def mock_randint(low, high):
            if high == 20: return 18
            if high == 8: return 6 # d8 for longsword
            return 1
        mocker.patch('random.randint', side_effect=mock_randint)

        # --- Main Attack ---
        cm.execute_player_attack('chad', longsword, 'goblin')

        # --- Bonus Action Attack should succeed ---
        offhand_results = cm.execute_offhand_attack('chad', 'goblin')
        assert 'error' not in offhand_results
        offhand_attack = offhand_results['attacks'][0]
        assert offhand_attack['hit']
        # Damage should be 1d8 = 6 (no ability modifier)
        assert offhand_attack['damage'] == 6
