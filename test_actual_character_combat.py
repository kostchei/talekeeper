"""
Test the combat-demo-actual-character branch.
This branch enhances the combat system to use actual database characters and weapons.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.combat import CombatService
from core.database import DatabaseSession
from models.character import Character
from models.monsters import Monster
from models.items import Item


def test_database_weapon_integration():
    """Test that the combat system properly queries database for weapons."""
    print("=== Testing Database Weapon Integration ===\n")
    
    combat = CombatService()
    
    # Test the get_available_weapons method with a mock character that has equipment
    class TestCharacter:
        def __init__(self):
            self.id = "test_char_1"
            self.name = "Test Hero"
            self.proficiency_bonus = 2
            self.strength_modifier = 3
            self.equipment_main_hand = "longsword_item_id"  # Simulate equipped weapon
    
    class TestCombatant:
        def __init__(self):
            self.id = "test_char_1" 
            self.type = "character"
            self.entity = TestCharacter()
    
    # Add test combatant to combat service
    combat.combatants = [TestCombatant()]
    
    # Try to get weapons (this should query the database)
    try:
        weapons = combat.get_available_weapons("test_char_1")
        print("Available weapons for test character:")
        for i, weapon in enumerate(weapons, 1):
            print(f"  {i}. {weapon['name']}")
            print(f"     Attack bonus: +{weapon['attack_bonus']}")  
            print(f"     Damage: {weapon['damage_dice']} {weapon['damage_type']}")
            print(f"     Description: {weapon['description']}")
            print()
            
        if len(weapons) > 1:
            print("✅ SUCCESS: Combat system is querying database for weapons!")
            print(f"Found {len(weapons)} weapons (more than just unarmed strike)")
        else:
            print("⚠️  Only found unarmed strike - database weapon query may not be working")
            
    except Exception as e:
        print(f"❌ ERROR testing database weapon integration: {e}")


def check_database_contents():
    """Check what's actually in the database."""
    print("=== Checking Database Contents ===\n")
    
    try:
        with DatabaseSession() as db:
            # Check items/weapons
            weapons = db.query(Item).filter_by(item_type='weapon').all()
            print(f"Weapons in database: {len(weapons)}")
            for weapon in weapons[:3]:  # Show first 3
                print(f"  - {weapon.name}: {weapon.damage_dice} {weapon.damage_type}")
            print()
            
            # Check if there are any characters
            characters = db.query(Character).all()  
            print(f"Characters in database: {len(characters)}")
            for char in characters[:2]:  # Show first 2
                print(f"  - {char.name} (Level {char.level})")
                if char.equipment_main_hand:
                    print(f"    Equipped: {char.equipment_main_hand}")
            print()
            
    except Exception as e:
        print(f"Database query error: {e}")
        print("This may be expected if database isn't fully initialized")


if __name__ == "__main__":
    print("Testing combat-demo-actual-character branch improvements\n")
    check_database_contents()
    test_database_weapon_integration()