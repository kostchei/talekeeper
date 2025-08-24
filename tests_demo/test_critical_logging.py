"""
Test critical hits and detailed damage logging.
"""

import sys
import os
# Add parent directory to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import from current directory
from combat_demo import MockCharacter, MockMonster
from services.combat import CombatService, AttackResult


def test_critical_and_miss_logging():
    """Test critical hits, misses, and detailed damage logging."""
    print("=== Testing Critical Hits and Detailed Logging ===\n")
    
    # Create test combatants
    character = MockCharacter()
    monster = MockMonster()
    
    combat = CombatService()
    combat.initialize_combat([character], [monster])
    
    # Get combatants
    char_combatant = combat._get_combatant_by_id("player_1")
    monster_combatant = combat._get_combatant_by_id("monster_0")
    
    if not char_combatant or not monster_combatant:
        print("Error: Could not get combatants")
        return
    
    print("=== Test 1: Normal Hit with Longsword (1d8+3) ===")
    weapon_longsword = {
        "name": "Longsword",
        "attack_bonus": 5,
        "damage_dice": "1d8+3",
        "damage_type": "slashing"
    }
    
    # Reset monster HP
    monster_combatant.current_hp = monster_combatant.max_hp
    monster_combatant.is_alive = True
    
    result = combat.attack(char_combatant.id, monster_combatant.id, weapon_longsword)
    print(f"Result: {result}")
    print()
    
    print("=== Test 2: Unarmed Strike (simple damage) ===")
    weapon_unarmed = {
        "name": "Unarmed Strike",
        "attack_bonus": 5,
        "damage_dice": "1",
        "damage_type": "bludgeoning"
    }
    
    # Reset monster HP
    monster_combatant.current_hp = monster_combatant.max_hp
    monster_combatant.is_alive = True
    
    result = combat.attack(char_combatant.id, monster_combatant.id, weapon_unarmed)
    print(f"Result: {result}")
    print()
    
    print("=== Test 3: Two-Handed Longsword (1d10+3) ===")
    weapon_2h = {
        "name": "Longsword (Two-Handed)",
        "attack_bonus": 5,
        "damage_dice": "1d10+3",
        "damage_type": "slashing"
    }
    
    # Reset monster HP
    monster_combatant.current_hp = monster_combatant.max_hp
    monster_combatant.is_alive = True
    
    result = combat.attack(char_combatant.id, monster_combatant.id, weapon_2h)
    print(f"Result: {result}")
    print()
    
    print("=== Test 4: Monster Default Attack ===")
    # Reset character HP
    char_combatant.current_hp = char_combatant.max_hp
    char_combatant.is_alive = True
    
    result = combat.attack(monster_combatant.id, char_combatant.id)
    print(f"Result: {result}")
    print()
    
    print("=== Combat Log Sample ===")
    summary = combat.get_combat_summary()
    for entry in summary['log'][-8:]:  # Last 8 entries
        print(f"  {entry}")


if __name__ == "__main__":
    test_critical_and_miss_logging()