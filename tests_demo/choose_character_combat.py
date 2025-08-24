"""
Combat demo with character selection.
Player can choose which saved character to use in combat.

Run with: cd tests_demo && python choose_character_combat.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.combat import CombatService, CombatState
import sqlite3


class DatabaseCharacter:
    """Character loaded from database data."""
    def __init__(self, char_data):
        # Unpack database row: id, name, level, strength, dex, con, ac, current_hp, max_hp
        self.id = char_data[0]
        self.name = char_data[1]
        self.level = char_data[2]
        self.strength = char_data[3]
        self.dexterity = char_data[4]
        self.constitution = char_data[5]
        self.armor_class = char_data[6]
        self.current_hit_points = char_data[7]
        self.max_hit_points = char_data[8]
        
        # For demo, give them a weapon
        self.equipment_main_hand = "shortsword"
    
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
    def proficiency_bonus(self) -> int:
        return (self.level - 1) // 4 + 2


class SimpleMonster:
    """Simple monster for testing."""
    def __init__(self):
        self.id = "monster_1"
        self.name = "Goblin Warrior"
        self.armor_class = 15
        self.hit_points = 7
        self.strength = 8
        self.dexterity = 14
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 8
        self.charisma = 8
        
        self.actions = [
            {
                "name": "Scimitar",
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
    def proficiency_bonus(self) -> int:
        return 2


def get_all_characters():
    """Get all characters from database."""
    try:
        conn = sqlite3.connect("../talekeeper.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, level, strength, dexterity, constitution, armor_class, current_hit_points, max_hit_points FROM characters")
        char_data = cursor.fetchall()
        conn.close()
        
        characters = []
        for data in char_data:
            characters.append(DatabaseCharacter(data))
        
        return characters
        
    except Exception as e:
        print(f"Failed to load characters: {e}")
        return []


def choose_character():
    """Let player choose which character to use."""
    characters = get_all_characters()
    
    if not characters:
        print("No characters found in database!")
        print("Create a character using the main app first.")
        return None
    
    print("Available Characters:")
    for i, char in enumerate(characters, 1):
        print(f"  {i}. {char.name} (Level {char.level})")
        print(f"     HP: {char.current_hit_points}/{char.max_hit_points}, AC: {char.armor_class}")
        print(f"     STR: {char.strength} (+{char.strength_modifier}), DEX: {char.dexterity} (+{char.dexterity_modifier})")
        print()
    
    while True:
        try:
            choice = input(f"Choose character (1-{len(characters)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(characters):
                return characters[index]
            else:
                print(f"Invalid choice. Enter 1-{len(characters)}")
        except (ValueError, KeyboardInterrupt):
            print(f"Invalid input. Enter 1-{len(characters)}")


def run_combat_encounter(character):
    """Run a combat encounter with the chosen character."""
    print(f"\n=== Combat with {character.name} ===")
    
    # Create opponent
    monster = SimpleMonster()
    
    # Initialize combat
    combat = CombatService()
    combat.initialize_combat([character], [monster])
    
    print(f"\nInitiative Results:")
    for combatant in combat.combatants:
        print(f"  - {combatant.name}: {combatant.initiative}")
    print()
    
    # Run interactive combat
    turn_count = 0
    max_turns = 20
    
    while combat.state == CombatState.IN_PROGRESS and turn_count < max_turns:
        current = combat.get_current_combatant()
        if not current:
            break
            
        turn_count += 1
        print(f"--- Turn {turn_count}: {current.name}'s turn ---")
        
        # Show current HP status
        print("Current Status:")
        for combatant in combat.combatants:
            if combatant.is_alive:
                print(f"  {combatant.name}: {combatant.current_hp}/{combatant.max_hp} HP")
        print()
        
        if current.type == "character":
            # Player turn - show weapon options
            weapons = combat.get_available_weapons(current.id)
            print(f"{current.name} - Choose your weapon:")
            
            for i, weapon in enumerate(weapons, 1):
                print(f"  {i}. {weapon['name']} - {weapon['damage_dice']} {weapon['damage_type']}")
                print(f"     Attack bonus: +{weapon['attack_bonus']} | {weapon['description']}")
            
            # Get weapon choice
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
            targets = combat.get_alive_enemies("character")
            target = targets[0]  # Only one enemy in this demo
            
            print(f"\n{current.name} attacks {target.name} with {chosen_weapon['name']}!")
            result = combat.attack(current.id, target.id, chosen_weapon)
            
        else:
            # Monster turn - automatic
            targets = combat.get_alive_enemies("monster")
            target = targets[0]
            print(f"{current.name} attacks {target.name}!")
            result = combat.attack(current.id, target.id)
        
        # Show attack result
        print(f">>> {result}")
        if result.hit:
            for combatant in combat.combatants:
                if combatant.name == result.target_name:
                    print(f">>> {combatant.name} HP: {combatant.current_hp}/{combatant.max_hp}")
                    break
        
        # Next turn
        combat.next_turn()
        
        # Pause between turns
        if combat.state == CombatState.IN_PROGRESS:
            input("\nPress Enter to continue...")
        
        print()
    
    # Combat results
    print("=== Combat Results ===")
    summary = combat.get_combat_summary()
    
    print(f"Final State: {summary['state'].replace('_', ' ').title()}")
    print(f"Rounds: {summary['round']}")
    print(f"Total Turns: {turn_count}")
    
    print("\nFinal Status:")
    for combatant_info in summary['combatants']:
        status = "ALIVE" if combatant_info['alive'] else "DEFEATED"
        print(f"  - {combatant_info['name']}: {combatant_info['hp']} HP - {status}")


def main():
    """Main demo function."""
    print("=== Character Selection Combat Demo ===\n")
    
    # Let player choose character
    character = choose_character()
    if not character:
        return
    
    print(f"\nSelected: {character.name}")
    print(f"Level: {character.level}")
    print(f"HP: {character.current_hit_points}/{character.max_hit_points}")
    print(f"AC: {character.armor_class}")
    print(f"STR: {character.strength} (+{character.strength_modifier})")
    print(f"DEX: {character.dexterity} (+{character.dexterity_modifier})")
    print(f"CON: {character.constitution} (+{character.constitution_modifier})")
    
    # Ask if ready for combat
    ready = input(f"\nReady to enter combat with {character.name}? (y/n): ").strip().lower()
    if ready in ['y', 'yes']:
        run_combat_encounter(character)
    else:
        print("Combat cancelled.")


if __name__ == "__main__":
    main()