"""
Combat demo using actual saved characters from the database.
This demonstrates the combat system with real character data and abilities.

Run with: cd tests_demo && python actual_character_combat.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.combat import CombatService, CombatState
from core.database import DatabaseSession, init_database
from models.character import Character
from models.monsters import Monster
from models.items import Item


def get_database_character():
    """Load the first available character from the database."""
    
    # First check with direct SQLite access
    import sqlite3
    try:
        conn = sqlite3.connect("../talekeeper.db")  # Try parent directory
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM characters")
        char_count = cursor.fetchone()[0]
        print(f"Found {char_count} characters in database")
        if char_count > 0:
            cursor.execute("SELECT id, name, level, strength, dexterity, constitution, armor_class, current_hit_points, max_hit_points FROM characters LIMIT 1")
            char_data = cursor.fetchone()
            print(f"Character data: {char_data}")
        conn.close()
    except Exception as e:
        print(f"SQLite check failed: {e}")
    
    # Try with SQLAlchemy
    with DatabaseSession() as db:
        character = db.query(Character).first()
        if not character:
            print("No characters found in SQLAlchemy session!")
            print("Create a character using the main app first.")
            return None
        
        print(f"Loaded character: {character.name}")
        print(f"  Race: {character.race.name if character.race else 'Unknown'}")
        print(f"  Class: {character.character_class.name if character.character_class else 'Unknown'}")
        print(f"  Level: {character.level}")
        print(f"  HP: {character.current_hit_points}/{character.max_hit_points}")
        print(f"  AC: {character.armor_class}")
        print(f"  STR: {character.strength} (+{character.strength_modifier})")
        print(f"  DEX: {character.dexterity} (+{character.dexterity_modifier})")
        print(f"  CON: {character.constitution} (+{character.constitution_modifier})")
        
        # Equip them with a weapon if they don't have one
        if not character.equipment_main_hand:
            print(f"  No weapon equipped - assigning a shortsword")
            # Find a shortsword in the database
            shortsword = db.query(Item).filter_by(name='Shortsword').first()
            if shortsword:
                character.equipment_main_hand = shortsword.id
                db.commit()
                print(f"  Equipped: {shortsword.name}")
        else:
            weapon = db.query(Item).filter_by(id=character.equipment_main_hand).first()
            if weapon:
                print(f"  Equipped: {weapon.name} ({weapon.damage_dice} {weapon.damage_type})")
        
        return character


def get_database_monster():
    """Create a monster for testing."""
    with DatabaseSession() as db:
        monster = db.query(Monster).first()
        if not monster:
            # Create a simple test monster if none exist
            print("No monsters in database, creating test monster...")
            monster = Monster()
            monster.name = "Test Goblin"
            monster.hit_points = 7
            monster.armor_class = 15
            monster.strength = 8
            monster.dexterity = 14
            monster.constitution = 10
            monster.intelligence = 10
            monster.wisdom = 8
            monster.charisma = 8
            monster.actions = [
                {
                    "name": "Scimitar",
                    "damage_dice": "1d6+2",
                    "damage_type": "slashing"
                }
            ]
            db.add(monster)
            db.commit()
        
        print(f"Monster: {monster.name}")
        print(f"  HP: {monster.hit_points}, AC: {monster.armor_class}")
        print(f"  STR: {monster.strength} (+{monster.strength_modifier})")
        print(f"  DEX: {monster.dexterity} (+{monster.dexterity_modifier})")
        
        return monster


def demonstrate_actual_character_combat():
    """Run combat with actual database characters."""
    print("=== Actual Character Combat Demo ===\n")
    
    # Initialize database
    try:
        init_database()
    except:
        pass  # May already be initialized
    
    # Load actual character from database
    character = get_database_character()
    if not character:
        return
        
    print()
    
    # Get a monster
    monster = get_database_monster()
    print()
    
    # Initialize combat with real character
    combat = CombatService()
    combat.initialize_combat([character], [monster])
    
    print("=== Combat Initialized ===")
    print("Initiative Results:")
    for combatant in combat.combatants:
        print(f"  - {combatant.name}: {combatant.initiative}")
    print()
    
    # Show available weapons for the real character
    current = combat.get_current_combatant()
    if current and current.type == "character":
        weapons = combat.get_available_weapons(current.id)
        print(f"{current.name}'s available weapons:")
        for i, weapon in enumerate(weapons, 1):
            print(f"  {i}. {weapon['name']} - {weapon['damage_dice']} {weapon['damage_type']}")
            print(f"     Attack bonus: +{weapon['attack_bonus']} | {weapon['description']}")
        print()
    
    # Run a few test attacks
    print("=== Test Combat Actions ===")
    
    # Test attack with first available weapon
    if current and current.type == "character":
        targets = combat.get_alive_enemies("character")
        if targets and weapons:
            print(f"{current.name} attacks {targets[0].name} with {weapons[0]['name']}:")
            result = combat.attack(current.id, targets[0].id, weapons[0])
            print(f"  Result: {result}")
            print()
    
    # Monster's turn
    combat.next_turn()
    current = combat.get_current_combatant()
    if current and current.type == "monster":
        targets = combat.get_alive_enemies("monster")
        if targets:
            print(f"{current.name} attacks {targets[0].name}:")
            result = combat.attack(current.id, targets[0].id)
            print(f"  Result: {result}")
            print()
    
    # Show combat summary
    print("=== Combat Summary ===")
    summary = combat.get_combat_summary()
    print(f"State: {summary['state']}")
    print(f"Round: {summary['round']}")
    
    print("\nCombatant Status:")
    for combatant_info in summary['combatants']:
        status = "ALIVE" if combatant_info['alive'] else "DEFEATED"
        print(f"  - {combatant_info['name']}: {combatant_info['hp']} HP - {status}")
    
    print("\nRecent Combat Log:")
    for entry in summary['log'][-5:]:
        print(f"  {entry}")


if __name__ == "__main__":
    demonstrate_actual_character_combat()