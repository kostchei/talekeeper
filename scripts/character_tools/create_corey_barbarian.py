# core
#utility
# core
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / 'src'))

from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator

def main():
    template_path = repo_root / 'templates' / 'barbarian_corey.json'

    print("Creating Corey Barbarian from template...")
    print(f"Template: {template_path}")
    print()

    creator = ProgrammaticCharacterCreator('talekeeper.db')
    character = creator.create_from_template(str(template_path))

    print("\n" + "="*60)
    print("COREY BARBARIAN CHARACTER CREATED")
    print("="*60)
    print(f"Name: {character['name']}")
    print(f"Species: {character['race_name']}")
    print(f"Class: {character['class_name']} Level {character['level']}")
    print(f"Background: Soldier")
    print(f"HP: {character['hit_points_current']}/{character['hit_points_max']}")
    print(f"AC: {character['armor_class']}")
    print(f"Save Slot: {character.get('save_slot', 'Unknown')}")
    print()
    print("Ability Scores:")
    print(f"  STR: {character['strength']} DEX: {character['dexterity']} CON: {character['constitution']}")
    print(f"  INT: {character['intelligence']} WIS: {character['wisdom']} CHA: {character['charisma']}")
    print()
    print("Features:")
    print("  - Rage (2 uses, +2 damage)")
    print("  - Unarmored Defense")
    print("  - Savage Attacker (Origin Feat)")
    print("  - Greatsword Mastery (Graze)")
    print()
    print("Skills: Stealth, Survival, Intimidation, Perception")
    print()
    print("Equipment:")
    print("  - Scale Mail (armor)")
    print("  - Greatsword (main hand)")
    print("  - Handaxe (backup weapon)")
    print()
    print("Starting Inventory:")
    print("  - 1x Potion of Healing")
    print("  - 1x Blanket")
    print("  - 10x Rations")
    print("="*60)

if __name__ == '__main__':
    main()
