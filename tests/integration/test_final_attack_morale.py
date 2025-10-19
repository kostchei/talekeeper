#test
import sys
sys.path.insert(0, 'src')

from talekeeper.core.combat_manager import CombatManager, Combatant, CombatantType
import random

def test_final_attack_hit_and_miss():
    """Test that final attack can hit or miss, with proper XP/loot distribution"""
    print("\n=== Testing Final Attack: Hit vs Miss ===")

    for test_num in range(5):
        print(f"\n--- Test Run {test_num + 1} ---")

        cm = CombatManager()

        player_data = {
            'id': 'test_player',
            'name': 'Test Fighter',
            'class_id': 'fighter',
            'level': 5,
            'ac': 18,
            'hp': 50,
            'max_hp': 50,
            'dexterity': 14
        }

        wolf_data = {
            'name': 'Wolf',
            'armor_class': 13,
            'hit_points': 20,
            'dexterity': 15,
            'wisdom': 12,
            'actions': '[{"name":"Bite","attack_type":"melee","attack_bonus":4,"damage":"2d4+2","damage_type":"piercing"}]'
        }

        cm.add_player_combatant(player_data)
        cm.add_monster_combatant('wolf', wolf_data)

        cm.start_combat()

        weapon_data = {
            'name': 'Longsword',
            'attack_bonus': 7,
            'damage_dice': '1d8',
            'damage_bonus': 5
        }

        total_xp = 0
        total_loot = []

        round_num = 1
        while not cm.is_combat_ended() and round_num < 10:
            current = cm.get_current_combatant()
            if not current:
                break

            if current.type == CombatantType.PLAYER:
                living_monsters = [c for c in cm.combatants.values()
                                 if c.type == CombatantType.MONSTER and c.is_alive and not c.has_fled]
                if living_monsters:
                    target = living_monsters[0]
                    result = cm.execute_player_attack('test_player', weapon_data, target.id)

                    if 'xp_gained' in result:
                        total_xp += result['xp_gained']

                    if 'loot' in result:
                        total_loot.extend(result['loot'])

                    if result.get('morale_event'):
                        morale = result['morale_event']
                        final = morale.get('final_attack_result', {})

                        if final.get('killed'):
                            print(f"  FINAL ATTACK: HIT - Wolf killed, dropped loot")
                        else:
                            print(f"  FINAL ATTACK: MISS - Wolf escaped")

            cm.advance_turn()
            round_num += 1

        summary = cm.end_combat()

        fled_count = summary.get('fled_monsters', 0)
        print(f"  Combat ended: {summary['result']}")
        print(f"  Fled enemies: {fled_count}")
        print(f"  Total XP: {total_xp}")
        print(f"  Total loot: {len(total_loot)} items")

        if fled_count > 0:
            assert total_xp > 0, "Should get XP even if enemy fled!"
            print("  [OK] XP granted for fled enemy")
        if total_loot:
            print(f"  [OK] Loot: {total_loot[0]['quantity']}x {total_loot[0]['name']}")

    print("\n=== Final Attack Test Complete ===")


def test_group_morale_with_final_attack():
    """Test morale with multiple enemies - some may be killed in final attack"""
    print("\n=== Testing Group Morale + Final Attack ===")

    cm = CombatManager()

    player_data = {
        'id': 'test_player',
        'name': 'Test Barbarian',
        'class_id': 'barbarian',
        'level': 5,
        'ac': 16,
        'hp': 60,
        'max_hp': 60,
        'dexterity': 14
    }

    goblin_data = {
        'name': 'Goblin',
        'armor_class': 15,
        'hit_points': 3,
        'dexterity': 14,
        'wisdom': 10,
        'actions': '[{"name":"Scimitar","attack_type":"melee","attack_bonus":4,"damage":"1d6+2","damage_type":"slashing"}]'
    }

    cm.add_player_combatant(player_data)

    for i in range(4):
        cm.add_monster_combatant(f'goblin_{i}', goblin_data)

    cm.start_combat()

    weapon_data = {
        'name': 'Greataxe',
        'attack_bonus': 8,
        'damage_dice': '1d12',
        'damage_bonus': 4
    }

    round_num = 1
    morale_triggered = False

    while not cm.is_combat_ended() and round_num < 20:
        current = cm.get_current_combatant()
        if not current:
            break

        if current.type == CombatantType.PLAYER:
            living_monsters = [c for c in cm.combatants.values()
                             if c.type == CombatantType.MONSTER and c.is_alive and not c.has_fled]
            if living_monsters:
                target = living_monsters[0]
                result = cm.execute_player_attack('test_player', weapon_data, target.id)

                if result.get('morale_event'):
                    morale_triggered = True
                    print(f"\nMORALE TRIGGERED!")
                    print(f"  Fleeing: {len(result['morale_event'].get('fleeing_combatants', []))} goblins")
                    print(f"  XP from morale: {result.get('xp_gained', 0)}")

                    final = result['morale_event'].get('final_attack_result', {})
                    if final.get('killed'):
                        print(f"  Final attack killed: {len(final['killed'])} goblin(s)")
                    else:
                        print(f"  Final attack missed")

        cm.advance_turn()
        round_num += 1

    summary = cm.end_combat()
    print(f"\nCombat Summary:")
    print(f"  Result: {summary['result']}")
    print(f"  Enemies fled: {summary.get('fled_monsters', 0)}")
    print(f"  Morale triggered: {morale_triggered}")

    print("\n=== Group Morale Test Complete ===")


if __name__ == "__main__":
    random.seed(None)

    test_final_attack_hit_and_miss()
    test_group_morale_with_final_attack()

    print("\n[OK] ALL FINAL ATTACK TESTS COMPLETE")
