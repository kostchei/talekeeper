"""
Combat demo using actual saved character data.
Creates a character object from the database data to use in combat.

Run with: cd tests_demo && python real_character_combat.py
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
        self.equipment_main_hand = "shortsword"  # Will be handled by combat system
    
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


def load_character_from_database():
    """Load character data from the actual database."""
    try:
        conn = sqlite3.connect("../talekeeper.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, level, strength, dexterity, constitution, armor_class, current_hit_points, max_hit_points FROM characters LIMIT 1")
        char_data = cursor.fetchone()
        conn.close()
        
        if char_data:
            return DatabaseCharacter(char_data)
        else:
            print("No characters found in database!")
            return None
            
    except Exception as e:
        print(f"Failed to load character: {e}")
        return None


def demonstrate_real_character_combat():
    """Run combat with actual database character."""
    print("=== Real Character Combat Demo ===\n")
    
    # Load actual character from database
    character = load_character_from_database()
    if not character:
        print("Could not load character from database.")
        return
    
    print(f"Loaded Character: {character.name}")
    print(f"  Level: {character.level}")
    print(f"  HP: {character.current_hit_points}/{character.max_hit_points}")
    print(f"  AC: {character.armor_class}")
    print(f"  STR: {character.strength} (+{character.strength_modifier})")
    print(f"  DEX: {character.dexterity} (+{character.dexterity_modifier})")
    print(f"  CON: {character.constitution} (+{character.constitution_modifier})")
    print(f"  Proficiency: +{character.proficiency_bonus}")
    print()
    
    # Create a monster
    monster = SimpleMonster()
    print(f"Opponent: {monster.name}")
    print(f"  HP: {monster.hit_points}, AC: {monster.armor_class}")
    print(f"  STR: {monster.strength} (+{monster.strength_modifier})")
    print(f"  DEX: {monster.dexterity} (+{monster.dexterity_modifier})")
    print()
    
    # Initialize combat
    combat = CombatService()
    combat.initialize_combat([character], [monster])
    
    print("=== Combat Started ===")
    print("Initiative Results:")
    for combatant in combat.combatants:
        print(f"  - {combatant.name}: {combatant.initiative}")
    print()
    
    # Show character's weapon options
    current = combat.get_current_combatant()
    if current and current.type == "character":
        weapons = combat.get_available_weapons(current.id)
        print(f"{current.name}'s Available Weapons:")
        for i, weapon in enumerate(weapons, 1):
            print(f"  {i}. {weapon['name']}")
            print(f"     Attack: +{weapon['attack_bonus']}, Damage: {weapon['damage_dice']} {weapon['damage_type']}")
            print(f"     {weapon['description']}")
        print()
        
        # Test attack with best weapon
        if weapons and len(weapons) > 1:
            best_weapon = weapons[1]  # Skip unarmed, use first real weapon
        else:
            best_weapon = weapons[0]
            
        targets = combat.get_alive_enemies("character")
        if targets:
            print(f"=== {current.name} attacks {targets[0].name} with {best_weapon['name']} ===")
            result = combat.attack(current.id, targets[0].id, best_weapon)
            print(f"Result: {result}")
            print()
    
    # Monster's turn
    combat.next_turn()
    current = combat.get_current_combatant()
    if current and current.type == "monster":
        targets = combat.get_alive_enemies("monster")
        if targets:
            print(f"=== {current.name} attacks {targets[0].name} ===")
            result = combat.attack(current.id, targets[0].id)
            print(f"Result: {result}")
            print()
    
    # Show final status
    print("=== Combat Status ===")
    summary = combat.get_combat_summary()
    print(f"State: {summary['state']}")
    print(f"Round: {summary['round']}")
    
    print("\nCombatants:")
    for combatant_info in summary['combatants']:
        status = "ALIVE" if combatant_info['alive'] else "DEFEATED"
        print(f"  - {combatant_info['name']}: {combatant_info['hp']} HP - {status}")
    
    print(f"\nThis demonstrates that the combat system can use real character data!")
    print(f"Character '{character.name}' with actual stats from the database fought in combat.")


if __name__ == "__main__":
    demonstrate_real_character_combat()