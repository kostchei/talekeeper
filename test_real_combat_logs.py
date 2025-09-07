#!/usr/bin/env python3
"""
Test actual TaleKeeper combat with comprehensive logging to demonstrate D&D 2024 compliance.
This will create a real combat scenario and show all the logs.
"""

import sys
import os
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.combat_manager import CombatManager

def test_comprehensive_combat_scenario():
    """Test a comprehensive combat scenario showing all logs"""
    print("=" * 60)
    print("TALEKEEPER D&D 2024 COMBAT SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    combat_manager = CombatManager()
    
    # Create Level 5 Fighter (same as from combat logs)
    print("\n>>> SETTING UP COMBAT PARTICIPANTS <<<")
    fighter_data = {
        'id': 'fighter_5',
        'name': 'Fighter_5',
        'class_id': 'fighter',
        'level': 5,
        'ac': 18,
        'hp': 44,
        'max_hp': 44,
        'dexterity': 14,  # +2 initiative
        'strength': 16   # +3 attack/damage
    }
    
    # Add the exact same enemies from the original combat log
    lizard_data = {
        'id': 'lizard1',
        'name': 'Lizard',
        'armor_class': 10,
        'hit_points': 2,
        'dexterity': 11,  # +0 initiative
        'actions': '[{"name": "Bite", "entries": ["{@atk mw} {@hit 0} to hit, reach 5 ft., one target. {@h}1 piercing damage."]}]',
        'experience_points': 10
    }
    
    swarm_data = {
        'id': 'swarm1',
        'name': 'Swarm of Insects',
        'armor_class': 12,
        'hit_points': 22,
        'dexterity': 13,  # +1 initiative
        'actions': '[{"name": "Bites", "entries": ["{@atk mw} {@hit 3} to hit, reach 0 ft., one target in the swarm\'s space. {@h}10 ({@damage 4d4}) piercing damage, or 5 ({@damage 2d4}) piercing damage if the swarm has half of its hit points or fewer."]}]',
        'experience_points': 100
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
    
    scout_data = {
        'id': 'scout1',
        'name': 'Scout',
        'armor_class': 13,
        'hit_points': 16,
        'dexterity': 14,  # +2 initiative
        'actions': '[{"name": "Multiattack", "entries": ["The scout makes two melee attacks or two ranged attacks."]}, {"name": "Shortsword", "entries": ["{@atk mw} {@hit 4} to hit, reach 5 ft., one target. {@h}5 ({@damage 1d6 + 2}) piercing damage."]}]',
        'experience_points': 100
    }
    
    # Add all combatants
    fighter = combat_manager.add_player_combatant(fighter_data)
    lizard = combat_manager.add_monster_combatant('lizard1', lizard_data)
    swarm = combat_manager.add_monster_combatant('swarm1', swarm_data)
    tiger = combat_manager.add_monster_combatant('tiger1', tiger_data)
    scout = combat_manager.add_monster_combatant('scout1', scout_data)
    
    print(f"Fighter_5: AC {fighter.armor_class}, HP {fighter.hit_points}/{fighter.max_hit_points}, Level {fighter.level}")
    print(f"Lizard: AC {lizard.armor_class}, HP {lizard.hit_points}")
    print(f"Swarm: AC {swarm.armor_class}, HP {swarm.hit_points}")
    print(f"Tiger: AC {tiger.armor_class}, HP {tiger.hit_points}")
    print(f"Scout: AC {scout.armor_class}, HP {scout.hit_points}")
    
    print(f"\nAdded {len(combat_manager.combatants)} combatants to combat")
    
    # Start combat - this will show initiative rolls
    print("\n>>> COMBAT START - INITIATIVE PHASE <<<")
    initiative_order = combat_manager.start_combat()
    
    print(f"\nFinal Initiative Order:")
    for i, combatant in enumerate(initiative_order):
        print(f"  {i+1}. {combatant.name}: {combatant.initiative_roll}")
    
    # Run several rounds of combat to show the system working
    print("\n>>> ROUND 1 BEGINS <<<")
    
    round_num = 1
    turn_count = 0
    max_turns = 20  # Prevent infinite loops
    
    while not combat_manager.is_combat_ended() and turn_count < max_turns:
        current = combat_manager.get_current_combatant()
        if not current:
            print("No current combatant - combat ended")
            break
            
        turn_count += 1
        is_player = combat_manager.is_player_turn()
        
        print(f"\n--- Turn {turn_count} (Round {round_num}) ---")
        print(f"Current: {current.name} {'(PLAYER)' if is_player else '(ENEMY)'}")
        print(f"HP Status: {current.hit_points}/{current.max_hit_points if hasattr(current, 'max_hit_points') else current.hit_points}")
        
        if is_player:
            # Fighter's turn - test Extra Attack
            print(f"\n>>> FIGHTER'S TURN - TESTING EXTRA ATTACK <<<")
            
            # Create weapon data for longsword
            weapon_data = {
                'name': 'Longsword',
                'attack_bonus': 6,  # +3 STR + 3 proficiency
                'damage_dice': '1d8',
                'damage_bonus': 3
            }
            
            # Choose target - prioritize weakest enemy
            target_id = None
            if lizard.is_alive:
                target_id = 'lizard1'
            elif swarm.is_alive:
                target_id = 'swarm1'
            elif scout.is_alive:
                target_id = 'scout1' 
            elif tiger.is_alive:
                target_id = 'tiger1'
            
            if target_id:
                print(f"Fighter attacking: {target_id}")
                result = combat_manager.execute_player_attack('fighter_5', weapon_data, target_id)
                
                if 'error' not in result:
                    print(f"Attack result: {result.get('damage_dealt', 0)} total damage dealt")
                    print(f"Target status: {result.get('target_status', 'unknown')}")
                else:
                    print(f"Attack error: {result['error']}")
            else:
                print("No valid targets for Fighter")
                
        else:
            # Enemy turn
            print(f"\n>>> {current.name.upper()}'S TURN <<<")
            
            if current.is_alive:
                result = combat_manager.execute_monster_turn(current.id)
                print(f"Monster turn result: {result.get('action', 'unknown action')}")
                
                if result.get('hit'):
                    damage = result.get('damage', 0)
                    print(f"Fighter takes {damage} damage!")
                    print(f"Fighter HP: {fighter.hit_points}/{fighter.max_hit_points}")
            else:
                print(f"{current.name} is defeated, skipping turn")
        
        # Advance to next combatant
        combat_manager.advance_turn()
        
        # Check if we've completed a round (back to highest initiative)
        next_combatant = combat_manager.get_current_combatant()
        if next_combatant and next_combatant.initiative_roll >= current.initiative_roll:
            round_num += 1
            if round_num > 1:
                print(f"\n>>> ROUND {round_num} BEGINS <<<")
        
        # Show current HP status of all combatants
        print(f"\nCurrent HP Status:")
        print(f"  Fighter_5: {fighter.hit_points}/{fighter.max_hit_points} {'(ALIVE)' if fighter.is_alive else '(DEFEATED)'}")
        print(f"  Lizard: {lizard.hit_points}/2 {'(ALIVE)' if lizard.is_alive else '(DEFEATED)'}")
        print(f"  Swarm: {swarm.hit_points}/22 {'(ALIVE)' if swarm.is_alive else '(DEFEATED)'}")
        print(f"  Tiger: {tiger.hit_points}/37 {'(ALIVE)' if tiger.is_alive else '(DEFEATED)'}")
        print(f"  Scout: {scout.hit_points}/16 {'(ALIVE)' if scout.is_alive else '(DEFEATED)'}")
        
        time.sleep(0.5)  # Brief pause for readability
    
    print(f"\n>>> COMBAT COMPLETE <<<")
    print(f"Total turns: {turn_count}")
    print(f"Rounds completed: {round_num}")
    
    # Final status
    if fighter.is_alive:
        enemies_alive = sum(1 for c in [lizard, swarm, tiger, scout] if c.is_alive)
        if enemies_alive == 0:
            print("RESULT: Fighter VICTORY! All enemies defeated")
        else:
            print(f"RESULT: Combat ongoing - {enemies_alive} enemies remaining")
    else:
        print("RESULT: Fighter DEFEATED")
    
    # Show all combat log messages
    print(f"\n>>> COMPLETE COMBAT LOG ({len(combat_manager.get_combat_log())} messages) <<<")
    for i, message in enumerate(combat_manager.get_combat_log(), 1):
        print(f"{i:3d}: {message}")
    
    print("\n" + "=" * 60)
    print("COMBAT TEST COMPLETE")
    print("=" * 60)

def test_dead_creature_validation():
    """Specific test for dead creature targeting"""
    print("\n" + "=" * 60)
    print("DEAD CREATURE TARGETING VALIDATION TEST")
    print("=" * 60)
    
    combat_manager = CombatManager()
    
    # Add fighter
    fighter_data = {
        'id': 'test_fighter',
        'name': 'Test Fighter',
        'class_id': 'fighter',
        'level': 5,
        'ac': 18,
        'hp': 44,
        'max_hp': 44,
        'dexterity': 14,
        'strength': 16
    }
    
    # Add already-dead enemy
    dead_enemy_data = {
        'id': 'dead_enemy',
        'name': 'Dead Enemy',
        'armor_class': 10,
        'hit_points': 0,  # Already dead
        'dexterity': 10,
        'actions': '[{"name": "Attack", "entries": ["Test attack"]}]',
        'experience_points': 50
    }
    
    fighter = combat_manager.add_player_combatant(fighter_data)
    enemy = combat_manager.add_monster_combatant('dead_enemy', dead_enemy_data)
    
    # Manually set enemy as dead
    enemy.is_alive = False
    enemy.hit_points = 0
    
    combat_manager.start_combat()
    
    print(f"Fighter: {fighter.hit_points} HP, Alive: {fighter.is_alive}")
    print(f"Enemy: {enemy.hit_points} HP, Alive: {enemy.is_alive}")
    
    # Try to attack dead enemy
    weapon_data = {
        'name': 'Test Sword',
        'attack_bonus': 5,
        'damage_dice': '1d6',
        'damage_bonus': 2
    }
    
    print(f"\nAttempting to attack dead enemy...")
    result = combat_manager.execute_player_attack('test_fighter', weapon_data, 'dead_enemy')
    
    print(f"Result: {result}")
    
    if result.get('error') == 'Cannot target dead creature':
        print("PASS: Dead creature validation working correctly")
    else:
        print(f"FAIL: Expected 'Cannot target dead creature' error")
    
    print("=" * 60)

if __name__ == '__main__':
    test_comprehensive_combat_scenario()
    test_dead_creature_validation()