"""
Combat System Demonstration

This script demonstrates the turn-based combat system with:
1. Initiative rolling and turn order
2. Round-by-round combat flow  
3. Attack rolls, damage calculation, and HP tracking
4. Win/loss conditions

Run with: cd tests_demo && python combat_demo.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.combat import CombatService, CombatState


class MockCharacter:
    """Mock character for testing without SQLAlchemy dependencies."""
    def __init__(self):
        self.id = "player_1"
        self.name = "Sir Reginald"
        self.level = 1
        
        # Ability scores
        self.strength = 16  # +3 modifier
        self.dexterity = 14  # +2 modifier  
        self.constitution = 15  # +2 modifier
        self.intelligence = 12  # +1 modifier
        self.wisdom = 13  # +1 modifier
        self.charisma = 10  # +0 modifier
        
        # Combat stats
        self.armor_class = 16  # Chain mail
        self.max_hit_points = 10  # 8 + 2 (con modifier)
        self.current_hit_points = 10
        
        # Sample equipment for demo
        self.equipment_main_hand = "longsword"
        
    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2
    
    @property
    def constitution_modifier(self) -> int:
        return (self.constitution - 10) // 2
    
    @property
    def intelligence_modifier(self) -> int:
        return (self.intelligence - 10) // 2
    
    @property
    def wisdom_modifier(self) -> int:
        return (self.wisdom - 10) // 2
    
    @property
    def charisma_modifier(self) -> int:
        return (self.charisma - 10) // 2
        
    @property
    def proficiency_bonus(self) -> int:
        return (self.level - 1) // 4 + 2


class MockMonster:
    """Mock monster for testing without SQLAlchemy dependencies."""
    def __init__(self):
        self.id = 1
        self.name = "Goblin"
        self.challenge_rating = 0.25
        
        # Ability scores
        self.strength = 8   # -1 modifier
        self.dexterity = 14  # +2 modifier
        self.constitution = 10  # +0 modifier
        self.intelligence = 10  # +0 modifier
        self.wisdom = 8   # -1 modifier
        self.charisma = 8   # -1 modifier
        
        # Combat stats
        self.armor_class = 15  # Leather armor + shield
        self.hit_points = 7   # 2d6
        
        # Attacks
        self.actions = [
            {
                "name": "Scimitar",
                "attack_bonus": 4,  # +2 dex, +2 proficiency
                "damage_dice": "1d6+2",
                "damage_type": "slashing"
            }
        ]
        
    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2
    
    @property
    def constitution_modifier(self) -> int:
        return (self.constitution - 10) // 2
    
    @property
    def intelligence_modifier(self) -> int:
        return (self.intelligence - 10) // 2
    
    @property
    def wisdom_modifier(self) -> int:
        return (self.wisdom - 10) // 2
    
    @property
    def charisma_modifier(self) -> int:
        return (self.charisma - 10) // 2
        
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on CR."""
        if not self.challenge_rating:
            return 2
        cr = float(self.challenge_rating)
        if cr <= 4:
            return 2
        elif cr <= 8:
            return 3
        elif cr <= 12:
            return 4
        elif cr <= 16:
            return 5
        else:
            return 6


def create_sample_character() -> MockCharacter:
    """Create a sample character for testing."""
    return MockCharacter()


def create_sample_monster() -> MockMonster:
    """Create a sample monster for testing."""
    return MockMonster()


def simulate_combat():
    """Run a complete combat simulation."""
    print("=== D&D Turn-Based Combat Demo ===\n")
    
    # Create participants
    character = create_sample_character()
    monster = create_sample_monster()
    
    print(f"Player Character: {character.name}")
    print(f"  - HP: {character.current_hit_points}/{character.max_hit_points}")
    print(f"  - AC: {character.armor_class}")
    print(f"  - STR: {character.strength} (+{character.strength_modifier}), DEX: {character.dexterity} (+{character.dexterity_modifier})\n")
    
    print(f"Monster: {monster.name}")
    print(f"  - HP: {monster.hit_points}")
    print(f"  - AC: {monster.armor_class}")
    print(f"  - STR: {monster.strength} (+{monster.strength_modifier}), DEX: {monster.dexterity} (+{monster.dexterity_modifier})\n")
    
    # Initialize combat
    combat = CombatService()
    combat.initialize_combat([character], [monster])
    
    print("Initiative Results:")
    for combatant in combat.combatants:
        print(f"  - {combatant.name}: {combatant.initiative}")
    print()
    
    # Interactive combat rounds
    turn_count = 0
    max_turns = 50  # Prevent infinite loops
    
    while combat.state == CombatState.IN_PROGRESS and turn_count < max_turns:
        current = combat.get_current_combatant()
        if not current:
            break
            
        turn_count += 1
        print(f"\n--- Turn {turn_count}: {current.name}'s turn ---")
        
        # Get available targets
        if current.type == "character":
            targets = combat.get_alive_enemies("character")
        else:
            targets = combat.get_alive_enemies("monster")
        
        if not targets:
            print("  No targets available!")
            combat.next_turn()
            continue
            
        # Show current HP status
        print("Current Status:")
        for combatant in combat.combatants:
            if combatant.is_alive:
                print(f"  {combatant.name}: {combatant.current_hp}/{combatant.max_hp} HP")
        print()
        
        # Handle player vs monster turns differently
        if current.type == "character":
            # PLAYER TURN - Interactive weapon selection
            print(f"{current.name} - Choose your weapon:")
            
            weapons = combat.get_available_weapons(current.id)
            for i, weapon in enumerate(weapons, 1):
                print(f"  {i}. {weapon['name']} - {weapon['damage_dice']} {weapon['damage_type']} damage")
                print(f"     Attack bonus: +{weapon['attack_bonus']} | {weapon['description']}")
            
            # Get player choice
            while True:
                try:
                    choice = input(f"\nEnter weapon choice (1-{len(weapons)}): ").strip()
                    weapon_index = int(choice) - 1
                    if 0 <= weapon_index < len(weapons):
                        chosen_weapon = weapons[weapon_index]
                        break
                    else:
                        print(f"Invalid choice. Enter 1-{len(weapons)}")
                except (ValueError, KeyboardInterrupt):
                    print(f"Invalid input. Enter 1-{len(weapons)}")
            
            # Choose target
            print(f"\nChoose target:")
            for i, target in enumerate(targets, 1):
                print(f"  {i}. {target.name} (AC {target.armor_class}, {target.current_hp}/{target.max_hp} HP)")
            
            while True:
                try:
                    choice = input(f"\nEnter target (1-{len(targets)}): ").strip()
                    target_index = int(choice) - 1
                    if 0 <= target_index < len(targets):
                        chosen_target = targets[target_index]
                        break
                    else:
                        print(f"Invalid choice. Enter 1-{len(targets)}")
                except (ValueError, KeyboardInterrupt):
                    print(f"Invalid input. Enter 1-{len(targets)}")
            
            print(f"\n{current.name} attacks {chosen_target.name} with {chosen_weapon['name']}!")
            result = combat.attack(current.id, chosen_target.id, chosen_weapon)
            
        else:
            # MONSTER TURN - Automatic
            target = targets[0]  # Attack first available target
            print(f"{current.name} attacks {target.name}!")
            result = combat.attack(current.id, target.id)
        
        # Show attack result
        print(f">>> {result}")
        if result.hit:
            for combatant in combat.combatants:
                if combatant.name in result.target_name:
                    print(f">>> {combatant.name} HP: {combatant.current_hp}/{combatant.max_hp}")
                    break
        
        # Next turn
        combat.next_turn()
        
        # Pause between turns for readability
        if combat.state == CombatState.IN_PROGRESS:
            input("\nPress Enter to continue...")
    
    # Combat results
    print("=== Combat Results ===")
    summary = combat.get_combat_summary()
    
    print(f"Final State: {summary['state'].replace('_', ' ').title()}")
    print(f"Rounds: {summary['round']}")
    print(f"Total Turns: {turn_count}")
    
    print("\nFinal HP:")
    for combatant_info in summary['combatants']:
        status = "ALIVE" if combatant_info['alive'] else "DEFEATED"
        print(f"  - {combatant_info['name']}: {combatant_info['hp']} HP - {status}")
    
    print("\nCombat Log (last 10 entries):")
    for log_entry in summary['log']:
        print(f"  {log_entry}")


if __name__ == "__main__":
    simulate_combat()