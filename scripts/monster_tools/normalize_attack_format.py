"""
Normalize monster attack format from 'Attack Roll: +X' to '{@hit X}' format.

This ensures consistency in the monster data and allows the parser to work
with a single pattern instead of multiple fallbacks.
"""

import json
import re
from pathlib import Path


def normalize_attack_descriptions(monster_data):
    """Normalize attack descriptions to use {@hit X} format."""
    changes_made = 0

    for monster in monster_data:
        if 'actions' not in monster:
            continue

        for action in monster['actions']:
            if 'description' not in action:
                continue

            original = action['description']

            # Pattern: "Melee Attack Roll: +X" or "Ranged Attack Roll: +X"
            pattern = r'(Melee|Ranged) Attack Roll:\s*\+(\d+)'

            def replacement(match):
                attack_type = match.group(1)
                bonus = match.group(2)
                return f'{attack_type} {{@hit {bonus}}}'

            normalized = re.sub(pattern, replacement, original)

            if normalized != original:
                action['description'] = normalized
                changes_made += 1

    return changes_made


def main():
    # Load monster data
    monster_file = Path('d:/Code/TaleKeeper/data/monsters/monsters_extracted.json')

    if not monster_file.exists():
        print(f"Monster file not found: {monster_file}")
        return

    print(f"Loading monster data from {monster_file}...")
    with open(monster_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)

    print(f"Loaded {len(monsters)} monsters")

    # Create backup
    backup_file = monster_file.with_suffix('.json.backup')
    print(f"Creating backup at {backup_file}...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, indent=2)

    # Normalize
    print("Normalizing attack formats...")
    changes = normalize_attack_descriptions(monsters)

    print(f"Made {changes} changes")

    # Save normalized data
    if changes > 0:
        print(f"Writing normalized data to {monster_file}...")
        with open(monster_file, 'w', encoding='utf-8') as f:
            json.dump(monsters, f, indent=2)
        print("Done!")
    else:
        print("No changes needed")


if __name__ == '__main__':
    main()
