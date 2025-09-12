#!/usr/bin/env python3
"""
Simple test for two-weapon fighting implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.combat_manager import CombatManager, CombatantType

def test_two_weapon_fighting():
    """Test basic two-weapon fighting functionality"""
    cm = CombatManager(db_path="talekeeper.db")
    
    # Create a test player character with dual-wielding capability
    player_data = {
        'id': 'test_player',
        'name': 'Test Fighter',
        'class_id': 'fighter',
        'level': 3,
        'ac': 16,
        'hp': 25,
        'max_hp': 25,
        'strength': 16,
        'dexterity': 14
    }
    
    # Create a test monster
    monster_data = {
        'name': 'Goblin',
        'armor_class': 12,
        'hit_points': 10,
        'strength': 8,
        'dexterity': 14,
        'actions': '[]'
    }
    
    # Add combatants
    player = cm.add_player_combatant(player_data)
    monster = cm.add_monster_combatant('goblin_1', monster_data)
    
    print(f"Player created: {player.name} (STR:{player.strength}, DEX:{player.dexterity})")
    print(f"Monster created: {monster.name} (AC:{monster.armor_class}, HP:{monster.hit_points})")
    
    # Start combat
    initiative_order = cm.start_combat()
    print(f"\nCombat started with initiative order:")
    for i, combatant in enumerate(initiative_order):
        print(f"  {i+1}. {combatant.name} (Initiative: {combatant.initiative_roll})")
    
    # Test off-hand attack capability
    print(f"\nCan make off-hand attack: {cm.can_make_offhand_attack('test_player')}")
    
    # Create mock weapons for testing
    light_weapon_main = {
        'name': 'Scimitar',
        'item_type': 'weapon',
        'damage_dice': '1d6',
        'weapon_properties': ['Light', 'Finesse'],
        'attack_bonus': 0,
        'damage_bonus': 0
    }
    
    light_weapon_off = {
        'name': 'Shortsword',
        'item_type': 'weapon', 
        'damage_dice': '1d6',
        'weapon_properties': ['Light', 'Finesse'],
        'attack_bonus': 0,
        'damage_bonus': 0
    }
    
    if cm.is_player_turn():
        print(f"\n{player.name}'s turn!")
        
        # Test main-hand attack
        print("\nExecuting main-hand attack:")
        attack_result = cm.execute_player_attack('test_player', light_weapon_main, 'goblin_1')
        print(f"Attack result: {attack_result}")
        
        # Test off-hand attack (should work if both weapons are light)
        if cm.can_make_offhand_attack('test_player'):
            print("\nExecuting off-hand attack:")
            offhand_result = cm.execute_offhand_attack('test_player', 'goblin_1')
            print(f"Off-hand result: {offhand_result}")
        else:
            print("\nCannot make off-hand attack (no dual weapons equipped)")
    
    print(f"\nFinal monster HP: {monster.hit_points}/{monster.max_hit_points}")
    print(f"Combat log entries: {len(cm.combat_log)}")
    
    return True

if __name__ == "__main__":
    print("Testing Two-Weapon Fighting Implementation")
    print("=" * 50)
    try:
        test_two_weapon_fighting()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()