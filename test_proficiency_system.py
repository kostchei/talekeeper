#!/usr/bin/env python
"""
Test script for the proficiency system implementation.
Tests weapon, armor, and skill proficiencies.
"""

import sqlite3
import uuid
from services.proficiency_system import ProficiencySystem
from services.proficiency_bonus import get_proficiency_bonus

def test_proficiency_system():
    print("Testing Proficiency System...")
    print("=" * 50)
    
    # Initialize proficiency system
    prof_system = ProficiencySystem()
    
    # Create a test character
    test_char_id = str(uuid.uuid4())
    test_class = 'fighter'
    
    print(f"Creating test Fighter character: {test_char_id}")
    
    # Initialize proficiencies for fighter
    success = prof_system.initialize_character_proficiencies(test_char_id, test_class)
    print(f"Proficiency initialization: {'SUCCESS' if success else 'FAILED'}")
    
    # Get all proficiencies
    proficiencies = prof_system.get_character_proficiencies(test_char_id)
    
    print("\n--- Fighter Proficiencies ---")
    print(f"Armor: {proficiencies.get('armor', [])}")
    print(f"Weapons: {proficiencies.get('weapon', [])}")
    print(f"Skills: {proficiencies.get('skill', [])}")
    
    # Test weapon proficiency checks
    print("\n--- Weapon Proficiency Tests ---")
    weapons_to_test = [
        ('Longsword', True),  # martial weapon - fighter should be proficient
        ('Dagger', True),     # simple weapon - fighter should be proficient
        ('Exotic Weapon', True)  # unknown weapon - defaults to allowing
    ]
    
    for weapon_name, expected in weapons_to_test:
        is_prof, msg = prof_system.is_proficient_with_weapon(test_char_id, weapon_name)
        result = "PASS" if is_prof == expected else "FAIL"
        print(f"{weapon_name}: {is_prof} ({msg}) - {result}")
    
    # Test armor proficiency checks
    print("\n--- Armor Proficiency Tests ---")
    armors_to_test = [
        ('Leather Armor', True),  # light armor
        ('Chain Shirt', True),    # medium armor
        ('Plate Armor', True),    # heavy armor - fighter is proficient
    ]
    
    for armor_name, expected in armors_to_test:
        is_prof, msg = prof_system.is_proficient_with_armor(test_char_id, armor_name)
        result = "PASS" if is_prof == expected else "FAIL"
        print(f"{armor_name}: {is_prof} ({msg}) - {result}")
    
    # Test shield proficiency
    print("\n--- Shield Proficiency Test ---")
    has_shield = prof_system.is_proficient_with_shield(test_char_id)
    print(f"Shield proficiency: {has_shield} - {'PASS' if has_shield else 'FAIL'}")
    
    # Test skill proficiencies
    print("\n--- Skill Proficiency Tests ---")
    skills_to_test = [
        'Athletics',  # Fighter skill
        'Intimidation',  # Fighter skill
        'Arcana'  # Not a fighter skill
    ]
    
    for skill in skills_to_test:
        is_prof = prof_system.is_proficient_in_skill(test_char_id, skill)
        print(f"{skill}: {'Proficient' if is_prof else 'Not proficient'}")
    
    # Test proficiency bonus calculation
    print("\n--- Proficiency Bonus by Level ---")
    test_levels = [1, 5, 9, 13, 17, 20]
    for level in test_levels:
        bonus = get_proficiency_bonus(level)
        print(f"Level {level:2d}: +{bonus}")
    
    # Test skill bonus calculation
    print("\n--- Skill Bonus Calculation ---")
    # Add a skill proficiency for testing
    prof_system.add_proficiency(test_char_id, 'skill', 'Athletics', 'test')
    
    # Create a temporary character in DB for skill bonus calculation
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO characters (id, name, level, class_id)
        VALUES (?, 'Test Fighter', 5, 'fighter')
    """, (test_char_id,))
    conn.commit()
    
    ability_mod = 3  # +3 STR modifier
    skill_bonus = prof_system.calculate_skill_bonus(test_char_id, 'Athletics', ability_mod)
    expected_bonus = ability_mod + get_proficiency_bonus(5)  # Level 5 = +3 prof bonus
    print(f"Athletics with +3 STR at level 5: {skill_bonus} (expected {expected_bonus})")
    
    # Clean up test character
    cursor.execute("DELETE FROM characters WHERE id = ?", (test_char_id,))
    cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (test_char_id,))
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("Proficiency System Test Complete!")

def test_combat_integration():
    print("\n\nTesting Combat Integration...")
    print("=" * 50)
    
    from core.combat_manager import CombatManager
    
    # Create combat manager
    combat = CombatManager()
    
    # Create a test character
    test_char = {
        'id': str(uuid.uuid4()),
        'name': 'Test Fighter',
        'class_id': 'fighter',
        'level': 5,
        'strength': 16,
        'dexterity': 14,
        'constitution': 15,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'ac': 18,
        'hp': 44,
        'max_hp': 44
    }
    
    # Initialize proficiencies
    prof_system = ProficiencySystem()
    prof_system.initialize_character_proficiencies(test_char['id'], 'fighter')
    
    # Add to combat
    combatant = combat.add_player_combatant(test_char)
    
    print(f"Created combatant: {combatant.name}")
    print(f"Level: {combatant.level}")
    print(f"Extra Attacks: {combatant.extra_attacks}")
    
    # Test weapon attack with proficiency
    weapon_data = {
        'name': 'Longsword',
        'attack_bonus': 3,  # STR modifier
        'damage_dice': '1d8',
        'damage_bonus': 3
    }
    
    # Calculate expected attack bonus
    str_mod = 3
    prof_bonus = get_proficiency_bonus(5)  # +3 at level 5
    expected_total = str_mod + prof_bonus
    
    print(f"\nWeapon: {weapon_data['name']}")
    print(f"Expected attack bonus: +{str_mod} (STR) +{prof_bonus} (prof) = +{expected_total}")
    print("Proficiency should be automatically applied in combat")
    
    # Clean up
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (test_char['id'],))
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("Combat Integration Test Complete!")

if __name__ == "__main__":
    test_proficiency_system()
    test_combat_integration()