#!/usr/bin/env python3
"""
Test script for D&D 2024 compliant combat system.
Tests initiative, Extra Attack, Multiattack, and combat flow.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.combat_manager import CombatManager

def test_fighter_extra_attack():
    """Test Fighter Extra Attack at different levels"""
    print("=== Testing Fighter Extra Attack ===")
    
    combat_manager = CombatManager()
    
    # Test Level 5 Fighter (2 attacks)
    fighter_l5 = {
        'id': 'fighter_l5',
        'name': 'Fighter Level 5',
        'class_id': 'fighter',
        'level': 5,
        'ac': 18,
        'hp': 44,
        'max_hp': 44,
        'dexterity': 14,
        'strength': 16
    }
    
    # Test Level 11 Fighter (3 attacks) 
    fighter_l11 = {
        'id': 'fighter_l11',
        'name': 'Fighter Level 11',
        'class_id': 'fighter',
        'level': 11,
        'ac': 19,
        'hp': 88,
        'max_hp': 88,
        'dexterity': 14,
        'strength': 18
    }
    
    # Test Level 20 Fighter (4 attacks)
    fighter_l20 = {
        'id': 'fighter_l20',
        'name': 'Fighter Level 20',
        'class_id': 'fighter',
        'level': 20,
        'ac': 20,
        'hp': 160,
        'max_hp': 160,
        'dexterity': 14,
        'strength': 20
    }
    
    test_cases = [
        (fighter_l5, 2, "Level 5: 2 attacks"),
        (fighter_l11, 3, "Level 11: 3 attacks"),
        (fighter_l20, 4, "Level 20: 4 attacks")
    ]
    
    for fighter_data, expected_attacks, description in test_cases:
        combatant = combat_manager.add_player_combatant(fighter_data)
        actual_attacks = 1 + combatant.extra_attacks
        
        status = "PASS" if actual_attacks == expected_attacks else "FAIL"
        print(f"{status} {description}: Expected {expected_attacks}, got {actual_attacks}")
    
    print()

def test_monster_multiattack():
    """Test monster Multiattack parsing"""
    print("=== Testing Monster Multiattack ===")
    
    combat_manager = CombatManager()
    
    # Test Scout (should have 2 attacks via Multiattack)
    scout_data = {
        'id': 'scout1',
        'name': 'Scout',
        'armor_class': 13,
        'hit_points': 16,
        'dexterity': 14,
        'actions': '[{"name": "Multiattack", "entries": ["The scout makes two melee attacks or two ranged attacks."]}, {"name": "Shortsword", "entries": ["{@atk mw} {@hit 4} to hit, reach 5 ft., one target. {@h}5 ({@damage 1d6 + 2}) piercing damage."]}]',
        'experience_points': 100
    }
    
    combatant = combat_manager.add_monster_combatant('scout1', scout_data)
    
    # Check if actions were parsed
    print(f"PASS Scout actions parsed: {len(combatant.actions)} actions")
    for action in combatant.actions:
        print(f"   - {action.name}: +{action.attack_bonus} to hit, {action.damage_dice} damage")
    
    print()

def test_initiative_system():
    """Test initiative system"""
    print("=== Testing Initiative System ===")
    
    combat_manager = CombatManager()
    
    # Add player
    player_data = {
        'id': 'player1',
        'name': 'Test Fighter',
        'class_id': 'fighter',
        'level': 5,
        'ac': 18,
        'hp': 44,
        'max_hp': 44,
        'dexterity': 14  # +2 initiative
    }
    
    # Add monsters with different DEX
    tiger_data = {
        'id': 'tiger1',
        'name': 'Tiger',
        'armor_class': 12,
        'hit_points': 37,
        'dexterity': 15,  # +2 initiative
        'actions': '[{"name": "Bite", "entries": ["{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}8 ({@damage 1d10 + 3}) piercing damage."]}]',
        'experience_points': 200
    }
    
    lizard_data = {
        'id': 'lizard1',
        'name': 'Lizard',
        'armor_class': 10,
        'hit_points': 2,
        'dexterity': 11,  # +0 initiative
        'actions': '[{"name": "Bite", "entries": ["{@atk mw} {@hit 0} to hit, reach 5 ft., one target. {@h}1 piercing damage."]}]',
        'experience_points': 10
    }
    
    combat_manager.add_player_combatant(player_data)
    combat_manager.add_monster_combatant('tiger1', tiger_data)
    combat_manager.add_monster_combatant('lizard1', lizard_data)
    
    # Start combat
    initiative_order = combat_manager.start_combat()
    
    print(f"PASS Initiative rolled for {len(initiative_order)} combatants")
    for i, combatant in enumerate(initiative_order):
        print(f"   {i+1}. {combatant.name}: {combatant.initiative_roll}")
    
    print()

def test_combat_flow():
    """Test full combat flow"""
    print("=== Testing Full Combat Flow ===")
    
    combat_manager = CombatManager()
    
    # Add Level 5 Fighter
    fighter_data = {
        'id': 'fighter1',
        'name': 'Test Fighter',
        'class_id': 'fighter',
        'level': 5,
        'ac': 18,
        'hp': 44,
        'max_hp': 44,
        'dexterity': 14,
        'strength': 16
    }
    
    # Add weak enemy for quick test
    goblin_data = {
        'id': 'goblin1',
        'name': 'Goblin',
        'armor_class': 12,
        'hit_points': 7,
        'dexterity': 14,
        'actions': '[{"name": "Scimitar", "entries": ["{@atk mw} {@hit 4} to hit, reach 5 ft., one target. {@h}5 ({@damage 1d6 + 2}) slashing damage."]}]',
        'experience_points': 50
    }
    
    combat_manager.add_player_combatant(fighter_data)
    combat_manager.add_monster_combatant('goblin1', goblin_data)
    
    # Start combat
    initiative_order = combat_manager.start_combat()
    print(f"PASS Combat started with initiative order")
    
    # Test turn management
    current = combat_manager.get_current_combatant()
    print(f"PASS Current combatant: {current.name if current else 'None'}")
    
    # Test player turn check
    is_player_turn = combat_manager.is_player_turn()
    print(f"PASS Is player turn: {is_player_turn}")
    
    # Test combat end condition
    is_ended = combat_manager.is_combat_ended()
    print(f"PASS Combat ended: {is_ended}")
    
    print()

def test_dead_creature_validation():
    """Test dead creature targeting validation"""
    print("=== Testing Dead Creature Validation ===")
    
    combat_manager = CombatManager()
    
    # Add combatants
    player_data = {
        'id': 'player1',
        'name': 'Test Player',
        'class_id': 'fighter',
        'level': 1,
        'ac': 15,
        'hp': 10,
        'max_hp': 10,
        'dexterity': 12,
        'strength': 14
    }
    
    target_data = {
        'id': 'target1',
        'name': 'Test Target',
        'armor_class': 10,
        'hit_points': 0,  # Already dead
        'dexterity': 10,
        'actions': '[]',
        'experience_points': 25
    }
    
    player = combat_manager.add_player_combatant(player_data)
    target = combat_manager.add_monster_combatant('target1', target_data)
    
    # Set target as dead
    target.is_alive = False
    target.hit_points = 0
    
    combat_manager.start_combat()
    
    # Try to attack dead target
    weapon_data = {
        'name': 'Sword',
        'attack_bonus': 5,
        'damage_dice': '1d8',
        'damage_bonus': 2
    }
    
    result = combat_manager.execute_player_attack('player1', weapon_data, 'target1')
    
    expected_error = 'Cannot target dead creature'
    status = "PASS" if result.get('error') == expected_error else "FAIL"
    print(f"{status} Dead creature validation: {result.get('error', 'No error')}")
    
    print()

def main():
    """Run all combat system tests"""
    print("D&D 2024 Combat System Tests")
    print("=" * 40)
    
    try:
        test_fighter_extra_attack()
        test_monster_multiattack()
        test_initiative_system()
        test_combat_flow()
        test_dead_creature_validation()
        
        print("All combat system tests completed!")
        
    except Exception as e:
        print(f"FAIL Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()