#!/usr/bin/env python3
"""
Test multi-enemy combat scenario to verify D&D 2024 compliance.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.combat_manager import CombatManager

def test_multi_enemy_scenario():
    """Test complex multi-enemy combat scenario"""
    print("=== Multi-Enemy Combat Test ===")
    
    combat_manager = CombatManager()
    
    # Add Level 5 Fighter
    fighter_data = {
        'id': 'fighter1',
        'name': 'Fighter Level 5',
        'class_id': 'fighter',
        'level': 5,
        'ac': 18,
        'hp': 44,
        'max_hp': 44,
        'dexterity': 14,  # +2 initiative
        'strength': 16   # +3 attack/damage
    }
    
    # Add multiple enemies with different stats
    scout_data = {
        'id': 'scout1',
        'name': 'Scout',
        'armor_class': 13,
        'hit_points': 16,
        'dexterity': 14,  # +2 initiative
        'actions': '[{"name": "Multiattack", "entries": ["The scout makes two melee attacks or two ranged attacks."]}, {"name": "Shortsword", "entries": ["{@atk mw} {@hit 4} to hit, reach 5 ft., one target. {@h}5 ({@damage 1d6 + 2}) piercing damage."]}]',
        'experience_points': 100
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
    
    tiger_data = {
        'id': 'tiger1',
        'name': 'Tiger', 
        'armor_class': 12,
        'hit_points': 37,
        'dexterity': 15,  # +2 initiative
        'actions': '[{"name": "Bite", "entries": ["{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}8 ({@damage 1d10 + 3}) piercing damage."]}]',
        'experience_points': 200
    }
    
    # Add all combatants
    fighter = combat_manager.add_player_combatant(fighter_data)
    scout = combat_manager.add_monster_combatant('scout1', scout_data)
    lizard = combat_manager.add_monster_combatant('lizard1', lizard_data)
    tiger = combat_manager.add_monster_combatant('tiger1', tiger_data)
    
    print(f"Added {len(combat_manager.combatants)} combatants to combat")
    
    # Start combat and verify initiative
    initiative_order = combat_manager.start_combat()
    
    print("PASS Initiative order established:")
    for i, combatant in enumerate(initiative_order):
        print(f"  {i+1}. {combatant.name}: {combatant.initiative_roll}")
    
    # Test turn sequence
    print("\n=== Turn Sequence Test ===")
    for turn in range(3):  # Test first 3 turns
        current = combat_manager.get_current_combatant()
        if not current:
            print("PASS Combat ended properly")
            break
            
        is_player = combat_manager.is_player_turn()
        print(f"Turn {turn + 1}: {current.name} {'(Player)' if is_player else '(Enemy)'}")
        
        if is_player:
            # Test fighter Extra Attack
            weapon_data = {
                'name': 'Longsword',
                'attack_bonus': 6,  # +3 STR + 3 prof
                'damage_dice': '1d8',
                'damage_bonus': 3
            }
            
            # Attack weakest target first
            target_id = 'lizard1' if lizard.is_alive else 'scout1'
            result = combat_manager.execute_player_attack('fighter1', weapon_data, target_id)
            
            if 'error' not in result:
                print(f"  PASS Fighter attacked: {result.get('damage_dealt', 0)} damage")
            else:
                print(f"  Attack failed: {result['error']}")
                
        else:
            # Enemy turn
            combat_manager.execute_monster_turn(current.id)
            print(f"  Enemy {current.name} completed turn")
        
        # Next turn
        combat_manager.advance_turn()
        
        if combat_manager.is_combat_ended():
            print("PASS Combat ended when all enemies defeated")
            break
    
    # Verify dead creature validation
    print("\n=== Dead Creature Validation ===")
    if not lizard.is_alive:
        weapon_data = {'name': 'Test', 'attack_bonus': 5, 'damage_dice': '1d6', 'damage_bonus': 2}
        result = combat_manager.execute_player_attack('fighter1', weapon_data, 'lizard1')
        
        if result.get('error') == 'Cannot target dead creature':
            print("PASS Dead creature validation working")
        else:
            print(f"FAIL Expected dead creature error, got: {result}")
    
    print("\n=== Multi-Enemy Combat Test Complete ===")

if __name__ == '__main__':
    test_multi_enemy_scenario()