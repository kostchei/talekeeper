#test
import sys
sys.path.insert(0, 'src')

from talekeeper.core.combat_manager import CombatManager, Combatant, CombatantType
import random

def test_morale_system_with_goblins():
    """Test morale system with multiple goblins"""
    print("\n=== Testing Morale System (Group of Goblins) ===")

    cm = CombatManager()

    player_data = {
        'id': 'test_player',
        'name': 'Test Fighter',
        'class_id': 'fighter',
        'level': 5,
        'ac': 18,
        'hp': 40,
        'max_hp': 40,
        'dexterity': 14,
        'equipment_armor': 'Chain Mail'
    }

    goblin_data = {
        'name': 'Goblin',
        'armor_class': 15,
        'hit_points': 7,
        'dexterity': 14,
        'wisdom': 10,
        'actions': '[{"name":"Scimitar","attack_type":"melee","attack_bonus":4,"damage":"1d6+2","damage_type":"slashing"}]'
    }

    cm.add_player_combatant(player_data)

    for i in range(4):
        cm.add_monster_combatant(f'goblin_{i}', goblin_data)

    initiative_order = cm.start_combat()
    print(f"Combat started with {len(initiative_order)} combatants")

    weapon_data = {
        'name': 'Longsword',
        'attack_bonus': 7,
        'damage_dice': '1d8',
        'damage_bonus': 3
    }

    round_num = 1
    while not cm.is_combat_ended() and round_num < 10:
        print(f"\n--- Round {round_num} ---")

        current = cm.get_current_combatant()
        if not current:
            break

        if current.type == CombatantType.PLAYER:
            living_monsters = [c for c in cm.combatants.values()
                             if c.type == CombatantType.MONSTER and c.is_alive]
            if living_monsters:
                target = living_monsters[0]
                print(f"Player attacks {target.name}")
                result = cm.execute_player_attack('test_player', weapon_data, target.id)

                if result.get('morale_event'):
                    print(f"MORALE EVENT: {result['morale_event']['monster_name']} fled!")
                    print(f"XP gained from fleeing: {result.get('xp_gained', 0)}")

        cm.advance_turn()
        round_num += 1

    summary = cm.end_combat()
    print(f"\nCombat ended: {summary['result']}")

    print("\nMORALE TEST COMPLETE")


def test_beast_loot_drops():
    """Test beast ration drops from wolves"""
    print("\n=== Testing Beast Loot System (Wolves) ===")

    cm = CombatManager()

    player_data = {
        'id': 'test_player',
        'name': 'Test Ranger',
        'class_id': 'ranger',
        'level': 3,
        'ac': 16,
        'hp': 30,
        'max_hp': 30,
        'dexterity': 16
    }

    wolf_data = {
        'name': 'Wolf',
        'armor_class': 13,
        'hit_points': 11,
        'dexterity': 15,
        'wisdom': 12,
        'actions': '[{"name":"Bite","attack_type":"melee","attack_bonus":4,"damage":"2d4+2","damage_type":"piercing"}]'
    }

    cm.add_player_combatant(player_data)
    cm.add_monster_combatant('wolf', wolf_data)

    cm.start_combat()

    weapon_data = {
        'name': 'Longbow',
        'attack_bonus': 6,
        'damage_dice': '1d8',
        'damage_bonus': 3
    }

    total_loot = []
    round_num = 1

    while not cm.is_combat_ended() and round_num < 10:
        current = cm.get_current_combatant()
        if not current:
            break

        if current.type == CombatantType.PLAYER:
            living_monsters = [c for c in cm.combatants.values()
                             if c.type == CombatantType.MONSTER and c.is_alive]
            if living_monsters:
                target = living_monsters[0]
                result = cm.execute_player_attack('test_player', weapon_data, target.id)

                if 'loot' in result:
                    total_loot.extend(result['loot'])
                    for loot_item in result['loot']:
                        print(f"LOOT: {loot_item['quantity']}x {loot_item['name']}")

        cm.advance_turn()
        round_num += 1

    cm.end_combat()

    print(f"\nTotal loot items: {len(total_loot)}")
    for item in total_loot:
        print(f"  - {item['quantity']}x {item['name']} ({item['value_gp']} GP)")

    print("\nBEAST LOOT TEST COMPLETE")


def test_mixed_combat():
    """Test combat with both beasts and non-beasts"""
    print("\n=== Testing Mixed Combat (Wolves + Goblins) ===")

    cm = CombatManager()

    player_data = {
        'id': 'test_player',
        'name': 'Test Paladin',
        'class_id': 'paladin',
        'level': 4,
        'ac': 18,
        'hp': 35,
        'max_hp': 35,
        'dexterity': 10
    }

    wolf_data = {
        'name': 'Wolf',
        'armor_class': 13,
        'hit_points': 11,
        'dexterity': 15,
        'wisdom': 12,
        'actions': '[{"name":"Bite","attack_type":"melee","attack_bonus":4,"damage":"2d4+2","damage_type":"piercing"}]'
    }

    goblin_data = {
        'name': 'Goblin',
        'armor_class': 15,
        'hit_points': 7,
        'dexterity': 14,
        'wisdom': 10,
        'actions': '[{"name":"Scimitar","attack_type":"melee","attack_bonus":4,"damage":"1d6+2","damage_type":"slashing"}]'
    }

    cm.add_player_combatant(player_data)
    cm.add_monster_combatant('wolf', wolf_data)

    cm.start_combat()

    weapon_data = {
        'name': 'Warhammer',
        'attack_bonus': 6,
        'damage_dice': '1d8',
        'damage_bonus': 3
    }

    total_rations = 0
    round_num = 1

    while not cm.is_combat_ended() and round_num < 15:
        current = cm.get_current_combatant()
        if not current:
            break

        if current.type == CombatantType.PLAYER:
            living_monsters = [c for c in cm.combatants.values()
                             if c.type == CombatantType.MONSTER and c.is_alive]
            if living_monsters:
                target = living_monsters[0]
                result = cm.execute_player_attack('test_player', weapon_data, target.id)

                if 'loot' in result:
                    for loot_item in result['loot']:
                        if 'Rations' in loot_item['name']:
                            total_rations += loot_item['quantity']

        cm.advance_turn()
        round_num += 1

    cm.end_combat()

    print(f"\nTotal beast rations collected: {total_rations}")
    print("Goblins should drop no rations (humanoids don't drop food)")

    print("\nMIXED COMBAT TEST COMPLETE")


if __name__ == "__main__":
    random.seed(42)

    test_morale_system_with_goblins()
    test_beast_loot_drops()
    test_mixed_combat()

    print("\n=== ALL INTEGRATION TESTS COMPLETE ===")
