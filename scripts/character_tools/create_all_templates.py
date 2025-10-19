# redundant
#utility
# redundant
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / 'src'))

from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator

def main():
    templates_dir = repo_root / 'templates'

    if not templates_dir.exists():
        print(f"Error: Templates directory not found at {templates_dir}")
        return

    template_files = sorted(templates_dir.glob('*.json'))

    if not template_files:
        print(f"No JSON templates found in {templates_dir}")
        return

    print("="*60)
    print(f"BATCH CHARACTER CREATION - {len(template_files)} templates")
    print("="*60)
    print()

    creator = ProgrammaticCharacterCreator('talekeeper.db')
    created_characters = []

    for template_path in template_files:
        print(f"\n[Processing] {template_path.name}")
        print("-" * 60)

        try:
            character = creator.create_from_template(str(template_path))
            created_characters.append({
                'template': template_path.name,
                'name': character['name'],
                'class': character['class_name'],
                'species': character['race_name'],
                'level': character['level'],
                'hp': f"{character['hit_points_current']}/{character['hit_points_max']}",
                'ac': character['armor_class'],
                'slot': character.get('save_slot', 'Unknown')
            })
            print(f"[SUCCESS] Created {character['name']}")

        except Exception as e:
            print(f"[ERROR] Failed to create character from {template_path.name}")
            print(f"  Error: {str(e)}")
            created_characters.append({
                'template': template_path.name,
                'error': str(e)
            })

    print("\n" + "="*60)
    print("BATCH CREATION SUMMARY")
    print("="*60)
    print(f"Total templates processed: {len(template_files)}")
    print(f"Successfully created: {len([c for c in created_characters if 'error' not in c])}")
    print(f"Failed: {len([c for c in created_characters if 'error' in c])}")
    print()

    print("Characters Created:")
    print("-" * 60)
    for char in created_characters:
        if 'error' in char:
            print(f"  [FAILED] {char['template']}: {char['error']}")
        else:
            print(f"  Slot {char['slot']}: {char['name']} - L{char['level']} {char['species']} {char['class']}")
            print(f"            HP: {char['hp']}, AC: {char['ac']}")

    print("="*60)

if __name__ == '__main__':
    main()
